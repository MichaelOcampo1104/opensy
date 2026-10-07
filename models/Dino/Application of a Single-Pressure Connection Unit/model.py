# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Application of a Single-Pressure Connection Unit (Dino Exam10)
UniqueID : Dino_SinglePressure
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-07
Purpose  : Two-phase DisplacementControl pushover of a beam-on-hangers
           assembly with compression-only (ENT) truss links: phase 1 pushes
           the mast top down 1 mm (UZ -0.01 x 100), phase 2 pushes it +X
           50 mm (UX 0.5 x 100). Node-24 history validated against
           ref/OPENSEES/node24.out, full-field final state against
           node0.out, hanger axial histories against ele23.out (200 rows).
Ref      : Dino -- Application of a Single-Pressure Connection Unit
           (co.tcl + EXAM10.s2k)
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
MAT_ENT     = 1    # uniaxial ENT (compression-only hanger parent)
MAT_UNUSED2 = 2    # uniaxial Elastic (dead code -- never referenced)
MAT_UNUSED3 = 3    # uniaxial Elastic (dead code -- never referenced)

# Control node/DOFs (source verbatim).
NODE_CTRL   = 24
DOF_DOWN    = 3              # UZ pushdown, phase 1
DOF_PUSH    = 1              # UX push, phase 2

# Time series / patterns (tags 1/2 match the source).
TS_1        = 1
PAT_1       = 1              # phase-1 gravity pattern (UZ at node 24)
TS_2        = 2
PAT_2       = 2              # phase-2 lateral pattern (UX at node 24)

# ODB
ODB_TAG       = 1

# Hanger trusses (source tags 13..23, 11 links).
TRUSS_TAGS = tuple(range(13, 24))

# Source files
TCL_FILE    = Path(__file__).parent / "ref" / "OPENSEES" / "co.tcl"
REF_NODE0   = Path(__file__).parent / "ref" / "OPENSEES" / "node0.out"
REF_NODE24  = Path(__file__).parent / "ref" / "OPENSEES" / "node24.out"
REF_ELE23   = Path(__file__).parent / "ref" / "OPENSEES" / "ele23.out"

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, A in mm^2, J/I in mm^4,
# forces in N). Frame/truss/node values replayed verbatim via regex (no
# conversion); named loads below carry * N / * mm multipliers.

# ENT compression-only hanger material (source line verbatim: E only).
E_ENT = 1.999e5 * MPa

# Dead uniaxial stiffnesses (tags 2/3, kept for fidelity, never referenced --
# elasticBeamColumn takes E/G as numeric literals).
E_DEAD2 = 2.482e4 * MPa
E_DEAD3 = 1.999e5 * MPa

# Phase-1 reference load (source pattern Plain 1): +1000 N UZ at mast top.
# (DisplacementControl drives UZ down regardless of the load sign.)
P_DOWN = 1000.0 * N
# Phase-2 reference load (source pattern Plain 2): 1 N UX at mast top.
P_PUSH = 1.0 * N

# Pushovers (source verbatim).
DOWN_INCR    = -0.01 * mm     # UZ increment per step at node 24, phase 1
N_DOWN_STEPS = 100            # -> -1 mm total pushdown
PUSH_INCR    = 0.5 * mm       # UX increment per step at node 24, phase 2
N_PUSH_STEPS = 100            # -> +50 mm total push
N_TOTAL_STEPS = N_DOWN_STEPS + N_PUSH_STEPS  # 200

# Model size (source counts).
N_NODES = 24
N_BEAMS = 12
N_TRUSS = 11
N_FIX   = 12


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """ENT compression-only hanger material + two dead Elastic materials.

    MAT_ENT (tag 1) parents the 11 hanger trusses (tensionless -- the
    "single-pressure" connection). Tags 2/3 are dead code in the source
    (elasticBeamColumn takes E/G as numeric literals) -- kept for tag
    fidelity, never referenced.
    """
    ops.uniaxialMaterial("ENT", MAT_ENT, E_ENT)
    ops.uniaxialMaterial("Elastic", MAT_UNUSED2, E_DEAD2)
    ops.uniaxialMaterial("Elastic", MAT_UNUSED3, E_DEAD3)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
# Not used -- elasticBeamColumn takes A/E/G/J/Iy/Iz as numeric literals, NOT
# section tags; trusses take A + matTag directly.


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 24 nodes + 22 lumped masses from co.tcl, verbatim.

    Mass is applied on UX and UY only (zero elsewhere; none on nodes 18 and
    24). Values are already in N-s^2/mm so no conversion is applied
    (pushover -- mass is inactive).
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
    """Apply fixities from co.tcl (trailing ';' tolerated).

    Node 3 slides (1 0 0 0 0 0: UX held); the 10 base nodes are fully fixed.
    (The source prints a "rigidDiaphragm" label but issues no MP-constraint
    commands.)
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
    """Create geomTransf + 12 elasticBeamColumns + 11 trusses, verbatim.

    ``element elasticBeamColumn tag i j A E G J Iy Iz transfTag`` maps
    directly to the OpenSeesPy signature (native 3D form). transfTag == eleTag
    for the 12 beams (source; trusses need none). Trusses take
    ``(tag, i, j, A, matTag)`` with the ENT parent. Returns (n_beams, n_truss).
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
    elements change mid-analysis (ENT slackening is material-level).
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
def define_down_loads() -> None:
    """Phase-1 pattern (source pattern 1): +1000 N UZ at node 24."""
    ops.timeSeries("Linear", TS_1)
    ops.pattern("Plain", PAT_1, TS_1)
    ops.load(NODE_CTRL, 0.0, 0.0, P_DOWN, 0.0, 0.0, 0.0)


def define_push_loads() -> None:
    """Phase-2 pattern (source pattern 2): 1 N UX at node 24."""
    ops.timeSeries("Linear", TS_2)
    ops.pattern("Plain", PAT_2, TS_2)
    ops.load(NODE_CTRL, P_PUSH, 0.0, 0.0, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def _new_pushover_analysis() -> "opst.anlys.SmartAnalyze":
    """Fresh SmartAnalyze Static instance (one per phase)."""
    return opst.anlys.SmartAnalyze(
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


def _run_phase(odb: "opst.post.CreateODB", history: list, axial: list,
               n_steps: int, incr: float, dof: int, phase: str) -> bool:
    """Run one DisplacementControl phase with per-increment ODB cadence.

    One segment per reference step via static_split([incr], maxStep=|incr|)
    so the recorder stays 1:1 with the 100-row-per-phase reference.
    Appends (time, node24 UX/UY/UZ) to history and the 11 hanger axialForces
    to axial. Returns True if all steps converged.
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")

    analysis = _new_pushover_analysis()
    ok = 0
    for _ in range(n_steps):
        segs = analysis.static_split([incr], maxStep=abs(incr))
        step_ok = True
        for seg in segs:
            ok = analysis.StaticAnalyze(node=NODE_CTRL, dof=dof, seg=seg)
            if ok < 0:
                step_ok = False
                break
            odb.fetch_response_step()
        if not step_ok:
            print(f"  WARNING: {phase} step {len(history)} failed (ok={ok})")
            analysis.close()
            return False
        history.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_CTRL, 1)),
            float(ops.nodeDisp(NODE_CTRL, 2)),
            float(ops.nodeDisp(NODE_CTRL, 3)),
        ))
        row = []
        for tag in TRUSS_TAGS:
            try:
                row.append(float(ops.eleResponse(tag, "axialForce")[0]))
            except Exception:
                row.append(float("nan"))
        axial.append(row)
    analysis.close()
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run pushdown + push phases, return ODB + results.

    Returns:
        (odb, results) with hist (200,4) [time,UX,UY,UZ] node-24 history,
        axial (200,11) hanger forces, ref24 (200,4) from node24.out,
        ref_ele (200,11) from ele23.out (time col dropped), and final-step
        full-field vectors sim_final/ref_final (24x3) from node0.out.
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

    history: list[tuple[float, float, float, float]] = []
    axial: list[list[float]] = []

    define_down_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running phase-1 pushdown (UZ -0.01 x 100)...")
    ok1 = _run_phase(odb, history, axial, N_DOWN_STEPS, DOWN_INCR,
                     DOF_DOWN, "pushdown")
    ops.loadConst("-time", 0.0)  # freeze phase-1 loads (source: loadConst 0)

    define_push_loads()
    print("Running phase-2 lateral push (UX 0.5 x 100)...")
    ok2 = _run_phase(odb, history, axial, N_PUSH_STEPS, PUSH_INCR,
                     DOF_PUSH, "push")
    print(f"  Phases converged: pushdown={ok1}, push={ok2}")

    hist = np.array(history, dtype=float)          # (200, 4)
    ax = np.array(axial, dtype=float)              # (200, 11)

    ref24 = ref_ele = ref_final = None
    if REF_NODE24.exists():
        ref24 = np.loadtxt(str(REF_NODE24))        # (200, 4)
    if REF_ELE23.exists():
        ref_ele = np.loadtxt(str(REF_ELE23))[:, 1:]  # drop time -> (200, 11)
    if REF_NODE0.exists():
        ref_final = np.loadtxt(str(REF_NODE0))[-1, 1:]  # (72,)
    sim_final = np.array([[float(ops.nodeDisp(t, d)) for d in (1, 2, 3)]
                          for t in range(1, N_NODES + 1)]).reshape(-1)  # (72,)

    results = {"hist": hist, "axial": ax, "ref24": ref24,
               "ref_ele": ref_ele, "sim_final": sim_final,
               "ref_final": ref_final, "ok": (ok1 and ok2)}
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot histories, verify.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis.
    """
    odb.save_response()

    hist, ax = results["hist"], results["axial"]
    ref24, ref_ele = results["ref24"], results["ref_ele"]

    if hist is not None and hist.shape[0] > 0:
        np.savetxt(str(output_dir / "node24_history.csv"), hist,
                   delimiter=",", header="time,ux,uy,uz (node 24, 200 steps)")
    if ax is not None and ax.size > 0:
        np.savetxt(str(output_dir / "hanger_axial_history.csv"), ax,
                   delimiter=",", header="hanger axialForce per step (N), eles 13..23")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UX", scale=1.0)
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UX", scale=1.0)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        if ref24 is not None and ref24.shape[0] > 0:
            ax1.plot(ref24[:, 1], ref24[:, 3], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node24.out)")
        if hist is not None and hist.shape[0] > 0:
            ax1.plot(hist[:, 1], hist[:, 3], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax1.set_xlabel("Node 24 UX displacement (mm)")
        ax1.set_ylabel("Node 24 UZ displacement (mm)")
        ax1.set_title("Dino_SinglePressure -- trajectory (UX vs UZ)")
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        steps = np.arange(1, (ax.shape[0] if ax is not None else 0) + 1)
        if ax is not None and ax.size > 0:
            for j in range(ax.shape[1]):
                alpha = 0.9 if j == 0 else 0.35
                ax2.plot(steps, ax[:, j], linewidth=1.1, alpha=alpha,
                         label=f"Ele {13 + j}" if j == 0 else None)
        if ref_ele is not None and ref_ele.size > 0:
            ax2.plot(steps, ref_ele[:, 0], "k--",
                     linewidth=1.0, alpha=0.6, label="Ref ele 13")
        ax2.set_xlabel("Recorded step (100 down + 100 push)")
        ax2.set_ylabel("Axial force (N)")
        ax2.set_title("Dino_SinglePressure -- hanger force histories")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "pushover_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable -- skipping compare plot)")

    # Verification summary
    n_sim = hist.shape[0] if hist is not None else 0
    print(f"\n  Recorded steps: {n_sim} / {N_TOTAL_STEPS} expected "
          f"(ok={results['ok']})")
    if hist is not None and n_sim > 0:
        labels = ("time", "UX", "UY", "UZ")
        for d in range(4):
            print(f"  Sim node24 {labels[d]} final = {float(hist[-1, d]):.5f}")
        if ref24 is not None and ref24.shape[0] > 0:
            n = min(n_sim, ref24.shape[0])
            # Pseudo-time is solver bookkeeping, not physics: phase 1 matches
            # exactly, but phase 2 diverges by construction (source's bare
            # `loadConst 0` vs standard `loadConst -time 0.0` -- see Notes).
            # Report it split by phase; pass/fail rests on UX/UY/UZ below.
            for a, b, nm in [(slice(0, 100), slice(0, 100), "phase-1"),
                             (slice(100, 200), slice(100, 200), "phase-2")]:
                sv, rv = hist[a, 0], ref24[b, 0]
                nn = min(sv.size, rv.size)
                if nn > 0:
                    rms_t = float(np.sqrt(np.mean((sv[:nn] - rv[:nn]) ** 2)))
                    print(f"    time ({nm}): per-point RMS {rms_t:.5f} "
                          f"(bookkeeping only -- see Notes)")
            for d in range(1, 4):
                sv, rv = hist[:n, d], ref24[:n, d]
                rms = float(np.sqrt(np.mean((sv - rv) ** 2)))
                big = np.abs(rv) > 1e-9
                rel = (float(np.mean(np.abs(sv[big] - rv[big])
                                     / np.abs(rv[big])) * 100.0)
                       if np.any(big) else 0.0)
                print(f"    {labels[d]}: per-point RMS {rms:.5f} | "
                      f"mean rel error {rel:.4f}% (|ref|>1e-9)")
    if ax is not None and ref_ele is not None and ax.size > 0:
        d = ax - ref_ele
        e_rms = float(np.sqrt(np.mean(d ** 2)))
        big = np.abs(ref_ele) > 1.0  # N; slack (zero-force) tail excluded
        e_rel = (float(np.mean(np.abs(d[big]) / np.abs(ref_ele[big])) * 100.0)
                 if np.any(big) else 0.0)
        print(f"  Hanger axial (11 links x 200 steps): RMS {e_rms:.3e} N | "
              f"(|ref|>1 mean rel {e_rel:.4f}%)")
    sim_final = results.get("sim_final")
    ref_final = results.get("ref_final")
    if sim_final is not None and ref_final is not None:
        dd = sim_final - ref_final
        f_rms = float(np.sqrt(np.mean(dd ** 2)))
        big = np.abs(ref_final) > 1e-9
        f_rel = (float(np.mean(np.abs(dd[big]) / np.abs(ref_final[big])) * 100.0)
                 if np.any(big) else 0.0)
        print(f"  Final-step full-field (24x3): RMS {f_rms:.3e} mm | "
              f"(|ref|>1e-9 mean rel {f_rel:.4f}%)")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_SinglePressure: analysis complete.")
