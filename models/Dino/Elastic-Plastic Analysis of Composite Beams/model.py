# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Elastic-Plastic Analysis of Composite Beams (Dino Exam21)
UniqueID : Dino_CompositeBeam
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-03
Purpose  : Displacement-controlled UZ pushover (-1.5 mm x 100 steps) of a 3D
           composite-beam frame (28 nodes, 39 dispBeamColumn elements;
           three fiber sections wrapped in rigid shear+torsion
           Aggregators).  Node 8 is pushed down 150 mm under a -1e5 N
           reference load; the load-factor history is validated against
           tcl_ref/node8.out.  Default PLASTIC = True activates the
           source's commented Steel01 lines (mats 1 + 4) -- the
           elasto-plastic run that generated the reference; PLASTIC = False
           reproduces the committed all-Elastic exam21.tcl (linear).
Ref      : Dino -- Elastic-Plastic Analysis of Composite Beams
           (original exam21.tcl)
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
# Elastic fiber materials (match source exam21.tcl tags exactly; the Steel01
# lines in the source are commented out -- the active model is all-elastic).
MAT_E1        = 1      # Elastic 2.05e5  (fiber section 1)
MAT_E2        = 2      # Elastic 2.482e4 (fiber section 2)
MAT_E3        = 3      # Elastic 1.999e5 (dead -- no fiber references it)
MAT_E4        = 4      # Elastic 2.05e6  (fiber section 3, circular tube)
# Rigid shear + torsion materials feeding the three Aggregators (verbatim):
MAT_VY_1      = 201
MAT_VZ_1      = 301
MAT_T_1       = 401
MAT_VY_2      = 202
MAT_VZ_2      = 302
MAT_T_2       = 402
MAT_VY_3      = 203
MAT_VZ_3      = 303
MAT_T_3       = 403

# Fiber sections + Aggregator wrappers + shared Lobatto integrations.
SEC_FIBER_1   = 1
SEC_FIBER_2   = 2
SEC_FIBER_3   = 3
SEC_AGG_1     = 1001
SEC_AGG_2     = 1002
SEC_AGG_3     = 1003
INTEG_1       = 1001   # beamIntegration Lobatto shared by all sec-1001 elements
INTEG_2       = 1002
INTEG_3       = 1003

# Validation
NODE_MONITOR  = 8      # node-8 disp validated against node8.out

# Time series / patterns
TS_PUSH       = 1
PAT_PUSH      = 1

# ODB
ODB_TAG       = 1

# Source files
TCL_FILE      = Path(__file__).parent / "tcl_ref" / "exam21.tcl"
REF_FILE      = Path(__file__).parent / "tcl_ref" / "node8.out"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N).

# Elastic fiber materials (source lines, verbatim values in MPa).
E_1 = 2.05e5 * MPa
E_2 = 2.482e4 * MPa
E_4 = 2.05e6 * MPa

# Rigid shear/torsion stiffnesses for the Aggregators (source, verbatim).
K_VY_1 = 1.154e9
K_VZ_1 = 1.538e9
K_T_1  = 9.690e11
K_VY_2 = 3.447e9
K_VZ_2 = 3.447e9
K_T_2  = 5.168e13
K_VY_3 = 2.725e10
K_VZ_3 = 2.725e10
K_T_3  = 8.310e13

# Torsional stiffness GJ for the bare fiber sections (§12au).  The Tcl source
# omits -GJ (Tcl only warns); OpenSeesPy 3D ``section Fiber`` REQUIRES it.  The
# Aggregator's rigid T code dominates torsion regardless, so the fiber-section
# GJ is a fallback -- set from G*Sum(A*r^2), computed per-section from the
# parsed fibers in define_sections().  This value only seeds the constant.
SEC_GJ = 1.0e10     # N*mm^2  (placeholder; recomputed in define_sections)

# Loading (source: pattern Plain 1 + DisplacementControl 8 3 -1.5 x 100).
P_REF       = -1.0e5 * N      # reference UZ load at node 8 (single pattern)
CTRL_DOF    = 3               # UZ displacement control at node 8
PUSH_INCR   = -1.5 * mm       # displacement increment per step (signed)
N_PUSH_STEPS = 100            # total recorded steps
N_IP        = 3               # dispBeamColumn integration points (source)

# Elasto-plastic variant switch.  The committed exam21.tcl runs all-Elastic
# (the Steel01 lines are commented out), but tcl_ref/node8.out yields past
# ~step 30 -- it was generated with the Steel01 lines active (the folder's
# namesake "Elastic-Plastic" run).  PLASTIC = False reproduces the committed
# Tcl exactly; PLASTIC = True activates Steel01 for mats 1 and 4 with the
# source's commented parameters (mat-4 fy chosen by PLASTIC_FY4).
PLASTIC     = True
# Verified 2026-10-03: PLASTIC mat-1-only reproduces node8.out to 0.01%
# (LF RMS 0.005, UY RMS 0.0005).  PLASTIC_MAT4 = True (fy 1000) undershoots
# badly (LF 20.4 vs 25.3, UY 3.1 vs 8.3); all-Elastic matches only steps
# 1-30 then overshoots (LF 46.9 vs 25.3).  So the reference was generated
# with ONLY the Steel01-mat-1 line uncommented; mat 4 stays Elastic.
PLASTIC_MAT4 = False     # True: Steel01 for mat 4 as well (fy = PLASTIC_FY4)
PLASTIC_FY4 = 1000.0 * MPa    # candidate: 1000 (alt: 500 -- see commented lines)
STEEL1_FY   = 450.0 * MPa     # Steel01 mat 1 (commented source line)
STEEL1_E    = 2.05e5 * MPa
STEEL1_B    = 0.0001
STEEL4_E    = 2.05e6 * MPa
STEEL4_B    = 0.00001

N_TOTAL_STEPS = N_PUSH_STEPS  # 100


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Elastic fiber + rigid shear/torsion materials (source, verbatim).

    MAT_E3 (Elastic 1.999e5) is defined in the source but referenced by no
    fiber -- kept for tag fidelity (it is a live source tag, unlike the
    commented-out Steel01 lines which are not defined at all).

    With PLASTIC = True (default), mats 1 and 4 use the source's commented
    Steel01 lines -- this reproduces the elasto-plastic run that generated
    tcl_ref/node8.out.  With PLASTIC = False, all-Elastic reproduces the
    committed exam21.tcl exactly (linear to 100 steps).
    """
    if PLASTIC:
        ops.uniaxialMaterial("Steel01", MAT_E1, STEEL1_FY, STEEL1_E, STEEL1_B)
    else:
        ops.uniaxialMaterial("Elastic", MAT_E1, E_1)
    ops.uniaxialMaterial("Elastic", MAT_E2, E_2)
    ops.uniaxialMaterial("Elastic", MAT_E3, 1.999e5 * MPa)
    if PLASTIC and PLASTIC_MAT4:
        ops.uniaxialMaterial("Steel01", MAT_E4, PLASTIC_FY4, STEEL4_E, STEEL4_B)
    else:
        ops.uniaxialMaterial("Elastic", MAT_E4, E_4)

    ops.uniaxialMaterial("Elastic", MAT_VY_1, K_VY_1)
    ops.uniaxialMaterial("Elastic", MAT_VZ_1, K_VZ_1)
    ops.uniaxialMaterial("Elastic", MAT_T_1, K_T_1)
    ops.uniaxialMaterial("Elastic", MAT_VY_2, K_VY_2)
    ops.uniaxialMaterial("Elastic", MAT_VZ_2, K_VZ_2)
    ops.uniaxialMaterial("Elastic", MAT_T_2, K_T_2)
    ops.uniaxialMaterial("Elastic", MAT_VY_3, K_VY_3)
    ops.uniaxialMaterial("Elastic", MAT_VZ_3, K_VZ_3)
    ops.uniaxialMaterial("Elastic", MAT_T_3, K_T_3)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def _parse_fiber_block(src: str, sec_tag: int) -> list[tuple[float, float, float, int]]:
    """Return [(y, z, area, matTag), ...] for one ``section Fiber N { ... }`` block."""
    m = re.search(rf"section\s+Fiber\s+{sec_tag}\s*\{{(.*?)\n\}}", src, re.S)
    if not m:
        return []
    body = m.group(1)
    fibers: list[tuple[float, float, float, int]] = []
    for fm in re.finditer(
        r"fiber\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+(\d+)", body
    ):
        fibers.append((float(fm.group(1)), float(fm.group(2)),
                       float(fm.group(3)), int(fm.group(4))))
    return fibers


def define_sections(src: str) -> None:
    """Rebuild the three fiber sections + Aggregators (source, verbatim).

    VERBATIM FIBER REPLAY (§12aq): every ``fiber`` line of exam21.tcl --
    including the ten zero-area fibers of section 2 -- is re-emitted with
    ops.fiber(y, z, area, matTag) preserving exact centroid + area.
    Each fiber section is wrapped by a section Aggregator adding rigid
    Vy/Vz/T codes, matching the source's 1001/1002/1003.

    -GJ (§12au): OpenSeesPy 3D ``section Fiber`` REQUIRES -GJ (Tcl only
    warns); computed per-section as G*Sum(A*r^2) from the parsed fibers
    (G from the section's own E).  The Aggregator's rigid T code dominates
    torsion regardless.
    """
    e_of = {SEC_FIBER_1: E_1, SEC_FIBER_2: E_2, SEC_FIBER_3: E_4}
    agg_of = {
        SEC_FIBER_1: (SEC_AGG_1, MAT_VY_1, MAT_VZ_1, MAT_T_1),
        SEC_FIBER_2: (SEC_AGG_2, MAT_VY_2, MAT_VZ_2, MAT_T_2),
        SEC_FIBER_3: (SEC_AGG_3, MAT_VY_3, MAT_VZ_3, MAT_T_3),
    }
    for sec_tag in (SEC_FIBER_1, SEC_FIBER_2, SEC_FIBER_3):
        fibers = _parse_fiber_block(src, sec_tag)
        g_mod = e_of[sec_tag] / (2.0 * (1.0 + 0.3))   # G = E/2(1+nu), nu~0.3
        gj = g_mod * sum(a * (y * y + z * z) for (y, z, a, _) in fibers)
        ops.section("Fiber", sec_tag, "-GJ", gj)
        for (y, z, area, mat) in fibers:
            # OpenSeesPy fiber signature: fiber(y, z, area, matTag)
            ops.fiber(y, z, area, mat)
        agg, mvy, mvz, mt = agg_of[sec_tag]
        ops.section("Aggregator", agg,
                    mvy, "Vy", mvz, "Vz", mt, "T",
                    "-section", sec_tag)

    # dispBeamColumn needs beamIntegration objects (§12l); one shared Lobatto
    # rule per Aggregator section (all source elements use nIP = 3).
    ops.beamIntegration("Lobatto", INTEG_1, SEC_AGG_1, N_IP)
    ops.beamIntegration("Lobatto", INTEG_2, SEC_AGG_2, N_IP)
    ops.beamIntegration("Lobatto", INTEG_3, SEC_AGG_3, N_IP)


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 28 nodes + lumped mass from exam21.tcl, verbatim.

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
    """Apply the two fix lines from exam21.tcl (tolerates trailing ';').

    fix 1: UX/UZ free-ish (0 0 1 0 0 0); fix 2: translations fixed (1 1 1).
    (The source prints "rigidDiaphragm" / "Equal DOF" labels but issues no
    MP-constraint commands, so Plain constraints are used throughout.)
    """
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> int:
    """Create geomTransf + dispBeamColumn elements from exam21.tcl, verbatim.

    geomTransf Linear (39 transforms with (1,0,0) or (0,0,1) orientation).
    dispBeamColumn (39 elements: ``tag i j nIP secTag transfTag``) -- the
    OpenSeesPy form takes (tag, i, j, transfTag, integTag) with a shared
    Lobatto beamIntegration per section (§12l), reusing the source nIP=3.
    Returns the number of elements created.
    """
    for m in re.finditer(
        r"^geomTransf\s+Linear\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)",
        src, re.M,
    ):
        ops.geomTransf("Linear", int(m.group(1)),
                       float(m.group(2)), float(m.group(3)), float(m.group(4)))

    integ_of = {SEC_AGG_1: INTEG_1, SEC_AGG_2: INTEG_2, SEC_AGG_3: INTEG_3}
    n = 0
    for m in re.finditer(
        r"^element\s+dispBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        src, re.M,
    ):
        tag = int(m.group(1))
        n1, n2 = int(m.group(2)), int(m.group(3))
        sec = int(m.group(5))
        transf = int(m.group(6))
        ops.element("dispBeamColumn", tag, n1, n2, transf, integ_of[sec])
        n += 1
    return n


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a static elastic frame model.

    ``save_frame_resp=False`` -- consistent with the other Dino
    fiber-section models (internal sections lack user-visible tags;
    §12v).  ``model_update=False`` -- no elements are removed/added
    mid-analysis.  ``set_odb_path`` precedes ``CreateODB`` (§12ac).
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
        save_shell_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_pushdown_loads(src: str) -> None:
    """Single Plain pattern (source): reference UZ load at node 8.

    The ``load 8 0 0 -1e5 0 0 0`` line inside the source's
    ``pattern Plain 1 Linear {...}`` block is replayed verbatim.
    DisplacementControl scales this reference vector to reach each
    target displacement.
    """
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    m = re.search(
        r"^load\s+8\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)"
        r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    )
    if m:
        ops.load(NODE_MONITOR, *(float(m.group(i)) for i in range(1, 7)))
    else:  # fallback to the documented reference load
        ops.load(NODE_MONITOR, 0.0, 0.0, P_REF, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_pushover(odb: "opst.post.CreateODB") -> bool:
    """UZ pushover: DisplacementControl node 8 DOF 3, -1.5 mm x 100 steps.

    One increment per reference step via static_split([incr],
    maxStep=|incr|) so the recorder stays 1:1 with the 100-row node8.out
    (§12am per-increment cadence).  In-loop history (load factor via
    getTime, node-8 UX/UY/UZ) is tracked for verification.
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
    analysis.close()
    run_pushover.history = history  # type: ignore[attr-defined]
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run UZ pushover, return ODB + results.

    Returns:
        (odb, results) where results has keys: hist (4,N) sim
        [LF,UX,UY,UZ] history, ref (4,N) reference from node8.out.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    src = TCL_FILE.read_text()

    init_model()
    define_materials()
    define_sections(src)
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_ele = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_ele} dispBeamColumn elements (expected 39).")

    odb = create_odb(output_dir)

    define_pushdown_loads(src)
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running UZ pushover analysis...")
    run_pushover(odb)

    # Reference node-8 history (node8.out: col0=lambda, col1=UX, col2=UY, col3=UZ)
    ref = None
    if REF_FILE.exists():
        ref = np.loadtxt(str(REF_FILE)).T  # (4, N) -> [LF, UX, UY, UZ]

    hist = np.array(getattr(run_pushover, "history", []), dtype=float).T
    results = {"hist": hist, "ref": ref}
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot node-8 history, verify.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis (hist/ref arrays).
    """
    odb.save_response()

    hist = results["hist"]
    ref = results["ref"]

    # Dump the full node-8 history for the record.
    if hist is not None and hist.shape[1] > 0:
        step = np.arange(1, hist.shape[1] + 1)
        curve = np.column_stack([step, hist.T])  # (N,5): step, LF, UX, UY, UZ
        np.savetxt(str(output_dir / "node8_disp_history.csv"), curve,
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

    # Node-8 UZ-vs-load-factor: simulation vs reference (matplotlib)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        if ref is not None and ref.shape[1] > 0:
            ax1.plot(ref[3], ref[0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node8.out)")
        if hist is not None and hist.shape[1] > 0:
            ax1.plot(hist[3], hist[0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax1.set_xlabel(f"Node {NODE_MONITOR} UZ displacement (mm)")
        ax1.set_ylabel("Load factor")
        ax1.set_title("Dino_CompositeBeam -- capacity (UZ vs LF)")
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        if ref is not None and ref.shape[1] > 0:
            ax2.plot(np.arange(1, ref.shape[1] + 1), ref[0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node8.out)")
        if hist is not None and hist.shape[1] > 0:
            ax2.plot(np.arange(1, hist.shape[1] + 1), hist[0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax2.set_xlabel("Recorded step (100 UZ increments)")
        ax2.set_ylabel("Load factor")
        ax2.set_title("Dino_CompositeBeam -- load factor history")
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


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_CompositeBeam: analysis complete.")
