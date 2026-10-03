# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Stress Analysis of Three-Dimensional Steel Structure Joints
           (Dino Exam25)
UniqueID : Dino_SteelJoint
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-03
Purpose  : Displacement-controlled UZ pushover (-1.0 mm x 10 steps) of a 3D
           steel joint assembly (580 nodes, 542 ShellMITC4 shell elements;
           J2Plasticity steel wrapped in a 20 mm PlateFiber section).
           Node 286 is pushed down 10 mm under 5 x -4e5 N reference loads;
           the load-factor history is validated against
           ref/OpenSees/node286.out (stresses spot-checked against
           Stress366.out).
Ref      : Dino -- Stress Analysis of Three-Dimensional Steel Structure
           Joints (original EXAM25.tcl)
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import re
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

# This model nests under models/Dino/<analysis-name>/, one level deeper than
# the usual models/<UniqueID>/, so standards/ is parents[3] not parents[2]
# (see AGENT.md §12as-5).
_STANDARDS = Path(__file__).parents[3] / "standards"
if not _STANDARDS.exists():
    _STANDARDS = Path(__file__).parents[2] / "standards"   # fallback for relocation
sys.path.insert(0, str(_STANDARDS))
from units import *
from vis_utils import (
    _headless,
    vis_nodes,
    vis_model,
    vis_loads,
    vis_pre_analysis,
    vis_defo,
    vis_slider,
    vis_anim,
)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# J2 plasticity steel -> PlateFiber matrix -> PlateFiber section (source tags).
MAT_J2        = 16     # nDMaterial J2Plasticity steel
MAT_PLATE     = 601    # nDMaterial PlateFiber wrapping MAT_J2
SEC_SHELL     = 701    # section PlateFiber (601, 20 mm thick)

# Shell elements carry the source's 0-based tags (0..541); they are replayed
# verbatim from EXAM25.tcl rather than enumerated as named constants.
ELE_TAG_MIN   = 0
ELE_TAG_MAX   = 541
ELE_STRESS    = 366    # shell element tracked in Stress366.out

# Validation
NODE_MONITOR  = 286    # node-286 disp validated against node286.out

# Time series / patterns (pattern tag 3 matches the source).
TS_PUSH       = 1
PAT_PUSH      = 3

# ODB
ODB_TAG       = 1

# Source files
TCL_FILE      = Path(__file__).parent / "ref" / "OpenSees" / "EXAM25.tcl"
REF_FILE      = Path(__file__).parent / "ref" / "OpenSees" / "node286.out"
REF_STRESS    = Path(__file__).parent / "ref" / "OpenSees" / "Stress366.out"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, K/G/sig in MPa, forces in N).

# J2Plasticity steel (source line, verbatim): K, G, sig0, sigInf, delta1, delta2.
J2_K     = 171666.0 * MPa
J2_G     = 79231.0 * MPa
J2_SIG0  = 200.0 * MPa
J2_SIGINF = 300.0 * MPa
J2_D1    = 1.0
J2_D2    = 1.0

# PlateFiber section thickness.
SHELL_T = 20.0 * mm

# Reference loads (source pattern Plain 3): 5 x -4e5 N UZ.
P_REF = -4.0e5 * N
LOAD_NODES = (272, 273, 286, 293, 300)

# Pushover (source: DisplacementControl 286 3 -1.0, analyze 10).
CTRL_DOF     = 3              # UZ displacement control at node 286
PUSH_INCR    = -1.0 * mm      # displacement increment per step (signed)
N_PUSH_STEPS = 10             # total recorded steps

N_TOTAL_STEPS = N_PUSH_STEPS  # 10


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """J2Plasticity steel -> PlateFiber matrix (source lines, verbatim).

    The commented ``ElasticIsotropic 16`` line is superseded by the active
    ``J2Plasticity 16`` line and is NOT defined (only one material may
    carry tag 16).
    """
    ops.nDMaterial("J2Plasticity", MAT_J2,
                   J2_K, J2_G, J2_SIG0, J2_SIGINF, J2_D1, J2_D2)
    ops.nDMaterial("PlateFiber", MAT_PLATE, MAT_J2)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    """20 mm PlateFiber shell section (source line, verbatim)."""
    ops.section("PlateFiber", SEC_SHELL, MAT_PLATE, SHELL_T)


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 580 nodes + lumped mass from EXAM25.tcl, verbatim.

    Mass is applied on UX and UY only (zero on UZ/rotations).  Values are
    already in N-s^2/mm so no conversion is applied.
    """
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))
    for m in re.finditer(
        r"^mass\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.mass(int(m.group(1)), float(m.group(2)), float(m.group(3)),
                 0.0, 0.0, 0.0, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Apply the 28 fully-fixed nodes from EXAM25.tcl (trailing ';' tolerated).

    (The source prints a "rigidDiaphragm" label but issues no MP-constraint
    commands, so Plain constraints are used throughout.)
    """
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> int:
    """Create the 542 ShellMITC4 elements from EXAM25.tcl, verbatim.

    ``element ShellMITC4 tag n1 n2 n3 n4 secTag`` -- the OpenSeesPy signature
    matches the Tcl form directly (no transformation or integration objects
    needed for shells).  Source tags are 0-based (0..541) and preserved.
    Returns the number of elements created.
    """
    n = 0
    for m in re.finditer(
        r"^element\s+ShellMITC4\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        src, re.M,
    ):
        ops.element("ShellMITC4", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), int(m.group(4)), int(m.group(5)),
                    int(m.group(6)))
        n += 1
    return n


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a static shell model.

    ``save_shell_resp=True`` (shells carry the stress response; §12as);
    frame/truss responses disabled (no such elements).  ``set_odb_path``
    precedes ``CreateODB`` (§12ac).  ``model_update=False`` -- no elements
    are removed/added mid-analysis.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
        save_shell_resp=True,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_pushdown_loads() -> None:
    """Single Plain pattern (source pattern 3): 5 x -4e5 N UZ reference loads.

    DisplacementControl scales this reference vector to reach each target
    displacement at node 286.
    """
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    for nd in LOAD_NODES:
        ops.load(nd, 0.0, 0.0, P_REF, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_pushover(odb: "opst.post.CreateODB") -> bool:
    """UZ pushover: DisplacementControl node 286 DOF 3, -1.0 mm x 10 steps.

    One increment per reference step via static_split([incr],
    maxStep=|incr|) so the recorder stays 1:1 with the 10-row node286.out
    (§12am per-increment cadence).  In-loop history (load factor via
    getTime, node-286 UX/UY/UZ, ele-366 stresses) is tracked for
    verification.
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="NormDispIncr",
        testTol=1.0e-8,
        testIterTimes=100,
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        printPer=0,
        testPrintFlag=0,
    )

    history: list[tuple[float, float, float, float]] = []  # (lf, ux, uy, uz)
    stresses: list[list[float]] = []
    ok = 0
    for _ in range(N_PUSH_STEPS):
        segs = analysis.static_split([PUSH_INCR], maxStep=abs(PUSH_INCR))
        step_ok = True
        for seg in segs:
            ok = analysis.StaticAnalyze(
                node=NODE_MONITOR, dof=CTRL_DOF, seg=seg)
            if ok < 0:
                step_ok = False
                break
            odb.fetch_response_step()
        if not step_ok:
            print(f"  WARNING: pushover step {len(history)} failed (ok={ok})")
            break
        ops.reactions()
        history.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_MONITOR, 1)),
            float(ops.nodeDisp(NODE_MONITOR, 2)),
            float(ops.nodeDisp(NODE_MONITOR, 3)),
        ))
        try:
            stresses.append([float(v) for v in
                             ops.eleResponse(ELE_STRESS, "stresses")])
        except Exception:
            pass
    analysis.close()
    run_pushover.history = history  # type: ignore[attr-defined]
    run_pushover.stresses = stresses  # type: ignore[attr-defined]
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run UZ pushover, return ODB + results.

    Returns:
        (odb, results) where results has keys: hist (4,N) sim
        [LF,UX,UY,UZ] history, ref (4,N) reference from node286.out,
        sim_stress / ref_stress (stress spot-check arrays).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    src = TCL_FILE.read_text()

    init_model()
    define_materials()
    define_sections()
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_ele = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_ele} ShellMITC4 elements (expected 542).")

    odb = create_odb(output_dir)

    define_pushdown_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running UZ pushover analysis...")
    run_pushover(odb)

    # Reference node-286 history (col0=lambda, col1=UX, col2=UY, col3=UZ)
    ref = None
    if REF_FILE.exists():
        ref = np.loadtxt(str(REF_FILE)).T  # (4, N) -> [LF, UX, UY, UZ]
    ref_stress = None
    if REF_STRESS.exists():
        try:
            ref_stress = np.loadtxt(str(REF_STRESS))
        except Exception:
            ref_stress = None

    hist = np.array(getattr(run_pushover, "history", []), dtype=float).T
    sim_stress_raw = getattr(run_pushover, "stresses", [])
    sim_stress = (np.array(sim_stress_raw, dtype=float)
                  if len(sim_stress_raw) > 0 else None)
    results = {"hist": hist, "ref": ref,
               "sim_stress": sim_stress, "ref_stress": ref_stress}
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot node-286 history, verify.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis (hist/ref/stress arrays).
    """
    odb.save_response()

    hist = results["hist"]
    ref = results["ref"]

    # Dump the full node-286 history for the record.
    if hist is not None and hist.shape[1] > 0:
        step = np.arange(1, hist.shape[1] + 1)
        curve = np.column_stack([step, hist.T])  # (N,5): step, LF, UX, UY, UZ
        np.savetxt(str(output_dir / "node286_disp_history.csv"), curve,
                   delimiter=",", header="step,lf,ux_mm,uy_mm,uz_mm")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))

        # V5 -- final deformed shape (pushdown is vertical -> UZ)
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UZ", scale=10.0)
        # V6 -- step slider
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UZ", scale=10.0)
        # V7 -- animation
        vis_anim(output_dir, filename="vis_07_animation.html",
                 odb_tag=ODB_TAG, defo_scale=10.0,
                 resp_dof=("UX", "UY", "UZ"))

    # Node-286 UZ-vs-load-factor: simulation vs reference (matplotlib)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        if ref is not None and ref.shape[1] > 0:
            ax1.plot(ref[3], ref[0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node286.out)")
        if hist is not None and hist.shape[1] > 0:
            ax1.plot(hist[3], hist[0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax1.set_xlabel(f"Node {NODE_MONITOR} UZ displacement (mm)")
        ax1.set_ylabel("Load factor")
        ax1.set_title("Dino_SteelJoint -- capacity (UZ vs LF)")
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        if ref is not None and ref.shape[1] > 0:
            ax2.plot(np.arange(1, ref.shape[1] + 1), ref[0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node286.out)")
        if hist is not None and hist.shape[1] > 0:
            ax2.plot(np.arange(1, hist.shape[1] + 1), hist[0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax2.set_xlabel("Recorded step (10 UZ increments)")
        ax2.set_ylabel("Load factor")
        ax2.set_title("Dino_SteelJoint -- load factor history")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "pushover_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable -- skipping compare plot)")

    # Verification summary
    n_sim = hist.shape[1] if hist is not None else 0
    print(f"\n  Recorded steps: {n_sim} / {N_TOTAL_STEPS} expected")
    if hist is not None and n_sim > 0:
        labels = ("LF", "UX", "UY", "UZ")
        for d in range(4):
            print(f"  Sim node{NODE_MONITOR} {labels[d]} final = "
                  f"{float(hist[d, -1]):.5f}")
        if ref is not None and ref.shape[1] > 0:
            n = min(n_sim, ref.shape[1])
            for d in range(4):
                sv, rv = hist[d, :n], ref[d, :n]
                rms = float(np.sqrt(np.mean((sv - rv) ** 2)))
                denom = np.maximum(np.abs(rv), 1e-12)
                rel = float(np.mean(np.abs(sv - rv) / denom) * 100.0)
                print(f"    {labels[d]}: per-point RMS {rms:.5f} | "
                      f"mean rel error {rel:.4f}%")

    # Stress spot-check (ele 366, values in MPa = N/mm^2).
    # Reference file layout: col 0 = pseudo-time, cols 1.. = stresses,
    # so the comparable block is ref_stress[:, 1:].
    sim_stress = results.get("sim_stress")
    ref_stress = results.get("ref_stress")
    if sim_stress is not None and sim_stress.shape[0] > 0:
        np.savetxt(str(output_dir / "ele366_stress_history.csv"), sim_stress,
                   delimiter=",", header="ele366 stresses per step (MPa)")
    if sim_stress is not None and ref_stress is not None:
        print(f"\n  Stress ele {ELE_STRESS}: sim shape {sim_stress.shape}, "
              f"ref shape {ref_stress.shape}")
        ref_block = (ref_stress[:, 1:1 + sim_stress.shape[1]]
                     if ref_stress.shape[1] > sim_stress.shape[1]
                     else ref_stress)
        if sim_stress.shape == ref_block.shape:
            s_rms = float(np.sqrt(np.mean((sim_stress - ref_block) ** 2)))
            big = np.abs(ref_block) > 1.0  # MPa; near-zero shears excluded
            if np.any(big):
                s_rel_big = float(np.mean(
                    np.abs(sim_stress[big] - ref_block[big])
                    / np.abs(ref_block[big])) * 100.0)
                print(f"    stress RMS {s_rms:.5f} MPa | (|ref|>1 MPa "
                      f"mean rel error {s_rel_big:.4f}%; near-zero shear "
                      f"terms excluded -- max abs diff there "
                      f"{float(np.max(np.abs(sim_stress[~big] - ref_block[~big]))):.2e} MPa)")
            else:
                print(f"    stress RMS {s_rms:.5f} MPa")
        else:
            print("    shapes differ -- disp validation above is authoritative")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_SteelJoint: analysis complete.")
