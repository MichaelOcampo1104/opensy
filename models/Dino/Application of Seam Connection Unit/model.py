# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Application of Seam Connection Unit (Dino Exam10)
UniqueID : Dino_SeamConnection
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-07
Purpose  : Displacement-controlled UX pushover (3 mm x 100 steps = 300 mm
           at node 1) of a main-tower + podium assembly linked by 4
           ElasticPPGap trusses across a 200 mm seismic seam. Nodal
           histories validated against ref/OPENSEES/node0.out (nodes 1-32)
           plus node1/node12/node13.out spot recorders.
Ref      : Dino -- Application of Seam Connection Unit
           (EXAM10.tcl + EXAM10.s2k)
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
# the usual models/<UniqueID>/, so standards/ is parents[3] not parents[2].
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
)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Materials (source tags preserved).
MAT_GAP     = 1    # uniaxial ElasticPPGap (seam trusses)
MAT_UNUSED2 = 2    # uniaxial Elastic (dead code -- never referenced)
MAT_UNUSED3 = 3    # uniaxial Elastic (dead code -- never referenced)
MAT_TRUSS   = 1    # truss parent material (= MAT_GAP)

# Truss cross-section (source, both diagonals).
TRUSS_A = 4265.0  # mm^2 -- carried via mm2 multiplier in Parameters

# Control node/DOF for the DisplacementControl pushover (source verbatim).
NODE_CTRL   = 1
CTRL_DOF    = 1              # UX

# Time series / patterns (pattern tag 1 matches the source).
TS_PUSH       = 1
PAT_PUSH      = 1

# ODB
ODB_TAG       = 1

# Seam-link trusses across the 200 mm gap (validation spot: ele 33).
ELE_SEAM_1  = 33
ELE_SEAM_2  = 34

# Source files
TCL_FILE    = Path(__file__).parent / "ref" / "OPENSEES" / "EXAM10.tcl"
REF_NODE0   = Path(__file__).parent / "ref" / "OPENSEES" / "node0.out"
REF_NODE1   = Path(__file__).parent / "ref" / "OPENSEES" / "node1.out"
REF_NODE12  = Path(__file__).parent / "ref" / "OPENSEES" / "node12.out"
REF_NODE13  = Path(__file__).parent / "ref" / "OPENSEES" / "node13.out"

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, A in mm^2, J/I in mm^4,
# forces in N). Frame/truss/node values replayed verbatim via regex (no
# conversion); named loads below carry * N / * mm multipliers.

# Gap material (source line verbatim): E, gap, damage flag.
E_GAP    = 200000.0 * MPa
GAP_OPEN = -2.0e10 * mm
GAP_DMG  = -1

# Dead uniaxial stiffnesses (tags 2/3, kept for fidelity, never referenced).
E_DEAD2 = 2.482e4 * MPa
E_DEAD3 = 1.999e5 * MPa

# Truss area.
A_TRUSS = 4265.0 * mm * mm

# PUSH reference loads (source pattern Plain 1): 8 x 1 kN UX.
P_PUSH = 1000.0 * N
LOAD_NODES = (1, 2, 5, 6, 9, 10, 17, 18)

# Pushover (source: DisplacementControl 1 1 3.0, analyze 100).
PUSH_INCR    = 3.0 * mm       # UX increment per step at node 1
N_PUSH_STEPS = 100            # total recorded steps
TARGET_DISP  = 300.0 * mm    # 3 mm x 100

# Model size (source counts).
N_NODES = 32
N_BEAMS = 48
N_TRUSS = 4
N_FIX   = 8


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """ElasticPPGap seam material + two dead Elastic materials (source).

    MAT_GAP (tag 1) parents the 4 seam trusses. Tags 2/3 are dead code in
    the source (elasticBeamColumn takes E/G as numeric literals) -- kept
    for tag fidelity, never referenced.
    """
    ops.uniaxialMaterial("ElasticPPGap", MAT_GAP, E_GAP, GAP_OPEN, GAP_DMG)
    ops.uniaxialMaterial("Elastic", MAT_UNUSED2, E_DEAD2)
    ops.uniaxialMaterial("Elastic", MAT_UNUSED3, E_DEAD3)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
# Not used -- elasticBeamColumn takes A/E/G/J/Iy/Iz as numeric literals, NOT
# section tags (MDOF precedent: material-tag-free elements omit this section).


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 32 nodes + 32 lumped masses from EXAM10.tcl, verbatim.

    Mass is applied on UX and UY only (zero elsewhere). Values are already
    in N-s^2/mm so no conversion is applied (pushover -- mass is inactive).
    """
    n = 0
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))
        n += 1
    assert n == N_NODES, f"nodes created {n}, expected {N_NODES}"
    for m in re.finditer(
        r"^mass\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.mass(int(m.group(1)), float(m.group(2)), float(m.group(3)),
                 0.0, 0.0, 0.0, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Apply the 8 partial base fixities (1 1 1 0 0 0) from EXAM10.tcl.

    (The source prints a "rigidDiaphragm" label but issues no MP-constraint
    commands, so Plain constraints are used throughout.)
    """
    n = 0
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)
        n += 1
    assert n == N_FIX, f"fixities applied {n}, expected {N_FIX}"


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> tuple[int, int]:
    """Create geomTransf + 48 elasticBeamColumns + 4 trusses, verbatim.

    ``element elasticBeamColumn tag i j A E G J Iy Iz transfTag`` maps
    directly to the OpenSeesPy signature (native 3D form). transfTag == eleTag
    for every beam (source). Trusses take ``(tag, i, j, A, matTag)``.
    Returns (n_beams, n_trusses).
    """
    for m in re.finditer(
        r"^geomTransf\s+Linear\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)",
        src, re.M,
    ):
        ops.geomTransf("Linear", int(m.group(1)),
                       float(m.group(2)), float(m.group(3)), float(m.group(4)))

    n_beam = 0
    for m in re.finditer(
        r"^element\s+elasticBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)"
        r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)"
        r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+(\d+)", src, re.M,
    ):
        ops.element("elasticBeamColumn", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), float(m.group(4)), float(m.group(5)),
                    float(m.group(6)), float(m.group(7)), float(m.group(8)),
                    float(m.group(9)), int(m.group(10)))
        n_beam += 1

    n_truss = 0
    for m in re.finditer(
        r"^element\s+truss\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.eE+-]+)\s+(\d+)",
        src, re.M,
    ):
        ops.element("truss", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), float(m.group(4)), int(m.group(5)))
        n_truss += 1

    assert n_beam == N_BEAMS, f"beams created {n_beam}, expected {N_BEAMS}"
    assert n_truss == N_TRUSS, f"trusses created {n_truss}, expected {N_TRUSS}"
    return n_beam, n_truss


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB (nodal + frame + truss responses).

    ``set_odb_path`` precedes ``CreateODB``. ``model_update=False`` -- no
    elements change mid-analysis.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=True,
        save_truss_resp=True,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_push_loads() -> None:
    """Single Plain pattern (source pattern 1): 8 x 1 kN UX reference loads.

    DisplacementControl scales this reference vector to reach each target
    displacement at node 1.
    """
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    for nd in LOAD_NODES:
        ops.load(nd, P_PUSH, 0.0, 0.0, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_pushover(odb: "opst.post.CreateODB") -> bool:
    """UX pushover: DisplacementControl node 1 DOF 1, 3 mm x 100 steps.

    SmartAnalyze Static (native DisplacementControl mode) with one segment
    per reference step via static_split([incr], maxStep=|incr|) so the
    recorder stays 1:1 with the 100-row node0.out. In-loop history
    (pseudo-time, node-1 UX/UY/UZ, ele-33 axialForce) is tracked for
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

    history: list[tuple[float, float, float, float]] = []  # (t, ux, uy, uz)
    axial: list[float] = []
    ok = 0
    for _ in range(N_PUSH_STEPS):
        segs = analysis.static_split([PUSH_INCR], maxStep=abs(PUSH_INCR))
        step_ok = True
        for seg in segs:
            ok = analysis.StaticAnalyze(
                node=NODE_CTRL, dof=CTRL_DOF, seg=seg)
            if ok < 0:
                step_ok = False
                break
            odb.fetch_response_step()
        if not step_ok:
            print(f"  WARNING: pushover step {len(history)} failed (ok={ok})")
            break
        history.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_CTRL, 1)),
            float(ops.nodeDisp(NODE_CTRL, 2)),
            float(ops.nodeDisp(NODE_CTRL, 3)),
        ))
        try:
            axial.append(float(ops.eleResponse(ELE_SEAM_1, "axialForce")[0]))
        except Exception:
            axial.append(float("nan"))
    analysis.close()
    run_pushover.history = history  # type: ignore[attr-defined]
    run_pushover.axial = axial  # type: ignore[attr-defined]
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run UX pushover, return ODB + results.

    Returns:
        (odb, results) with sim (100,4) [time,UX,UY,UZ] node-1 history,
        ref (100,4) from node1.out, full-field sim/ref blocks from node0.out,
        and the ele-33 axialForce history (sim only -- see Notes).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    src = TCL_FILE.read_text(encoding="utf-8", errors="replace")

    init_model()
    define_materials()
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_beam, n_truss = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_beam} elasticBeamColumn + {n_truss} truss "
          f"(expected {N_BEAMS} + {N_TRUSS}).")

    odb = create_odb(output_dir)

    define_push_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running UX pushover analysis...")
    converged = run_pushover(odb)
    print(f"  Pushover converged: {converged}")

    hist = np.array(getattr(run_pushover, "history", []), dtype=float)
    axial = np.array(getattr(run_pushover, "axial", []), dtype=float)

    ref1 = None
    if REF_NODE1.exists():
        ref1 = np.loadtxt(str(REF_NODE1))  # (100, 4): [time, UX, UY, UZ]

    # Full-field final-step vectors: current nodal state is the final step;
    # ref final row drops its time column for the disp-vs-disp compare.
    ref_final = None
    if REF_NODE0.exists():
        ref_final = np.loadtxt(str(REF_NODE0))[-1, 1:]  # (96,)
    sim_final = np.array([[float(ops.nodeDisp(t, d)) for d in (1, 2, 3)]
                          for t in range(1, N_NODES + 1)]).reshape(-1)  # (96,)

    results = {"hist": hist, "axial": axial, "ref1": ref1,
               "sim_final": sim_final, "ref_final": ref_final}
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot capacity, verify.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis.
    """
    odb.save_response()

    hist = results["hist"]
    ref1 = results["ref1"]
    axial = results["axial"]

    if hist is not None and hist.shape[0] > 0:
        np.savetxt(str(output_dir / "node1_ux_history.csv"), hist,
                   delimiter=",", header="time,ux,uy,uz (node 1)")
    if axial is not None and axial.size > 0:
        np.savetxt(str(output_dir / "ele33_axial_history.csv"), axial,
                   delimiter=",", header="ele33 axialForce per step (N)")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UX", scale=1.0)
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UX", scale=1.0)

    # Capacity plot: node-1 UX vs pseudo-time, sim vs node1.out.
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        if ref1 is not None and ref1.shape[0] > 0:
            ax1.plot(ref1[:, 1], ref1[:, 0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node1.out)")
        if hist is not None and hist.shape[0] > 0:
            ax1.plot(hist[:, 1], hist[:, 0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax1.set_xlabel("Node 1 UX displacement (mm)")
        ax1.set_ylabel("Pseudo-time (load factor)")
        ax1.set_title("Dino_SeamConnection -- capacity (UX vs time)")
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        steps = np.arange(1, (hist.shape[0] if hist is not None else 0) + 1)
        if axial is not None and axial.size > 0:
            ax2.plot(steps, axial, "b-", linewidth=1.2, label="Ele 33 axialForce")
        ax2.set_xlabel("Recorded step (100 UX increments)")
        ax2.set_ylabel("Axial force (N)")
        ax2.set_title("Dino_SeamConnection -- seam truss force history")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "pushover_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable -- skipping compare plot)")

    # Verification summary
    n_sim = hist.shape[0] if hist is not None else 0
    print(f"\n  Recorded steps: {n_sim} / {N_PUSH_STEPS} expected")
    if hist is not None and n_sim > 0:
        labels = ("time", "UX", "UY", "UZ")
        for d in range(4):
            print(f"  Sim node1 {labels[d]} final = {float(hist[-1, d]):.5f}")
        if ref1 is not None and ref1.shape[0] > 0:
            n = min(n_sim, ref1.shape[0])
            for d in range(4):
                sv, rv = hist[:n, d], ref1[:n, d]
                rms = float(np.sqrt(np.mean((sv - rv) ** 2)))
                big = np.abs(rv) > 1e-9
                rel = (float(np.mean(np.abs(sv[big] - rv[big]) / np.abs(rv[big])) * 100.0)
                       if np.any(big) else 0.0)
                print(f"    {labels[d]}: per-point RMS {rms:.5f} | "
                      f"mean rel error {rel:.4f}% (|ref|>1e-9)")
    sim_final = results.get("sim_final")
    ref_final = results.get("ref_final")
    if sim_final is not None and ref_final is not None:
        d = sim_final - ref_final
        f_rms = float(np.sqrt(np.mean(d ** 2)))
        big = np.abs(ref_final) > 1e-9
        f_rel = (float(np.mean(np.abs(d[big]) / np.abs(ref_final[big])) * 100.0)
                if np.any(big) else 0.0)
        print(f"  Final-step full-field (32x3): RMS {f_rms:.3e} mm | "
              f"(|ref|>1e-9 mean rel {f_rel:.4f}%)")
    if axial is not None and axial.size > 0:
        print(f"  Ele 33 axialForce final = {float(axial[-1]):.5f} N "
              f"(ref file duplicates time column -- sim only, see Notes)")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_SeamConnection: analysis complete.")
