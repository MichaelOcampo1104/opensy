# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Low-cycle reciprocating analysis of shear wall components (Dino)
UniqueID : Dino_ShearWallCyclic
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-03
Purpose  : Low-cycle reciprocating (cyclic) displacement analysis of a 3D
           shear-wall component (31 nodes; 12 dispBeamColumn fiber elements
           + 24 elasticBeamColumn).  After gravity, node 26 is cycled in UY
           through 9 DisplacementControl segments (+-0.2 .. +-1.4 mm x 100
           steps each); the load-factor history is validated against
           OPENSEES/node26.out (glitch-aware -- see Notes).
Ref      : Dino -- Low-cycle reciprocating analysis of shear wall
           components (original OPENSEES/co1.tcl)
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
# Fiber materials (match source co1.tcl tags exactly; commented lines are
# superseded and NOT defined).
MAT_STEEL     = 1      # Steel01 rebar (fy=395 MPa)
MAT_E2        = 2      # Elastic filler
MAT_E3        = 3      # Elastic
MAT_CONCRETE  = 4      # Concrete01 concrete
MAT_E5        = 5      # Elastic
# Rigid shear/torsion materials feeding Aggregators 1001-1002 (verbatim).
MAT_VY_1      = 201
MAT_VZ_1      = 301
MAT_T_1       = 401
MAT_VY_2      = 202
MAT_VZ_2      = 302
MAT_T_2       = 402

# Fiber sections + Aggregator wrappers + shared Lobatto integrations.
SEC_FIBER_1   = 1
SEC_FIBER_2   = 2
SEC_AGG_1     = 1001
SEC_AGG_2     = 1002
INTEG_1       = 1001
INTEG_2       = 1002

# Validation
NODE_MONITOR  = 26     # node-26 history validated against node26.out

# Time series / patterns (tags match the source).
TS_GRAVITY    = 1
PAT_GRAVITY   = 1
TS_CYCLIC     = 2
PAT_CYCLIC    = 2

# ODB
ODB_TAG       = 1

# Source files
TCL_FILE      = Path(__file__).parent / "OPENSEES" / "co1.tcl"
REF_FILE      = Path(__file__).parent / "OPENSEES" / "node26.out"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N).

# Steel01 (source line, verbatim).
STEEL_FY = 395.0 * MPa
STEEL_E  = 200000.0 * MPa
STEEL_B  = 0.0185

# Concrete01 (source line, verbatim).
CONC_FPC    = -30.0 * MPa
CONC_EPSC0  = -0.0028
CONC_FPCU   = -15.0 * MPa
CONC_EPSU   = -0.015

# Elastic fillers (source lines, verbatim).
E_2 = 2.550e4 * MPa
E_3 = 3.000e4 * MPa
E_5 = 2.060e5 * MPa

# Rigid shear/torsion stiffnesses for the Aggregators (source, verbatim).
K_VY_1, K_VZ_1, K_T_1 = 6.225e8, 6.225e8, 2.292e12
K_VY_2, K_VZ_2, K_T_2 = 1.360e9, 1.360e9, 5.361e12

# Torsional stiffness GJ for the bare fiber sections: negligible 1.0.
# The Aggregators' rigid T codes supply torsion and ADD the fiber GJ in
# parallel -- a physical GJ would corrupt torsional response (§12ba, proven
# on Dino_FrameWall: +31% torsional modes; GJ=1.0 exact).
SEC_GJ = 1.0      # N*mm^2 -- negligible by design

# Loading (source pattern 1: gravity UZ at nodes 29-31).
P_GRAV = -2.433e5 * N
GRAV_NODES = (29, 30, 31)

# Cyclic protocol (source pattern 2): reference UY load at node 26; segments
# parsed verbatim from the integrator/analyze pairs below (§12am: one target
# increment at a time via static_split for 1:1 recorder alignment).
CTRL_DOF = 2               # UY displacement control at node 26
P_CYCLIC = 1000.0 * N      # reference lateral load (1 kN)
N_IP     = 3               # dispBeamColumn integration points (source)

# Expected clean steps = 1 gravity + 9 x 100 cyclic.
N_GRAV_STEPS = 1
N_CYC_STEPS  = 900
N_TOTAL_STEPS = N_GRAV_STEPS + N_CYC_STEPS  # 901


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Steel01 + Concrete01 + Elastic fillers + rigid shear/torsion (verbatim).

    Commented Elastic 1 / Elastic 4 lines are superseded by the active
    Steel01 1 / Concrete01 4 lines (only one material may carry a tag).
    """
    ops.uniaxialMaterial("Steel01", MAT_STEEL, STEEL_FY, STEEL_E, STEEL_B)
    ops.uniaxialMaterial("Elastic", MAT_E2, E_2)
    ops.uniaxialMaterial("Elastic", MAT_E3, E_3)
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE,
                         CONC_FPC, CONC_EPSC0, CONC_FPCU, CONC_EPSU)
    ops.uniaxialMaterial("Elastic", MAT_E5, E_5)
    ops.uniaxialMaterial("Elastic", MAT_VY_1, K_VY_1)
    ops.uniaxialMaterial("Elastic", MAT_VZ_1, K_VZ_1)
    ops.uniaxialMaterial("Elastic", MAT_T_1, K_T_1)
    ops.uniaxialMaterial("Elastic", MAT_VY_2, K_VY_2)
    ops.uniaxialMaterial("Elastic", MAT_VZ_2, K_VZ_2)
    ops.uniaxialMaterial("Elastic", MAT_T_2, K_T_2)


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
    """Rebuild the two fiber sections + Aggregators (source, verbatim).

    VERBATIM FIBER REPLAY (§12aq): every ``fiber`` line re-emitted with
    ops.fiber(y, z, area, matTag) (§12ay area-is-THIRD).  Each wrapped by
    a section Aggregator (rigid Vy/Vz/T) + shared Lobatto beamIntegration
    for dispBeamColumn (§12l).
    """
    for sec_tag, agg_tag, integ_tag, mats in (
            (SEC_FIBER_1, SEC_AGG_1, INTEG_1, (MAT_VY_1, MAT_VZ_1, MAT_T_1)),
            (SEC_FIBER_2, SEC_AGG_2, INTEG_2, (MAT_VY_2, MAT_VZ_2, MAT_T_2))):
        fibers = _parse_fiber_block(src, sec_tag)
        ops.section("Fiber", sec_tag, "-GJ", SEC_GJ)
        for (y, z, area, mat) in fibers:
            ops.fiber(y, z, area, mat)
        mvy, mvz, mt = mats
        ops.section("Aggregator", agg_tag,
                    mvy, "Vy", mvz, "Vz", mt, "T",
                    "-section", sec_tag)
        ops.beamIntegration("Lobatto", integ_tag, agg_tag, N_IP)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 31 nodes from co1.tcl, verbatim (no masses in source)."""
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Apply the 3 fully-fixed nodes (8, 9, 10) from co1.tcl.

    (The source prints a "rigidDiaphragm" label but issues no MP-constraint
    commands.)
    """
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> tuple[int, int]:
    """Create geomTransf + dispBeamColumn + elasticBeamColumn (verbatim).

    dispBeamColumn ``(tag, i, j, nIP, secTag, transfTag)`` maps to
    OpenSeesPy ``(tag, i, j, transfTag, integTag)`` via the shared Lobatto
    beamIntegration per Aggregator section (§12l).  elasticBeamColumn keeps
    its native 3D form ``(tag, i, j, A, E, G, J, Iy, Iz, transfTag)``.
    Returns (n_disp, n_elastic).
    """
    for m in re.finditer(
        r"^geomTransf\s+Linear\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)",
        src, re.M,
    ):
        ops.geomTransf("Linear", int(m.group(1)),
                       float(m.group(2)), float(m.group(3)), float(m.group(4)))

    integ_of = {SEC_AGG_1: INTEG_1, SEC_AGG_2: INTEG_2}
    n_disp = 0
    for m in re.finditer(
        r"^element\s+dispBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        src, re.M,
    ):
        ops.element("dispBeamColumn", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), int(m.group(6)),
                    integ_of[int(m.group(5))])
        n_disp += 1

    n_elastic = 0
    for m in re.finditer(
        r"^element\s+elasticBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)"
        r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)"
        r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+(\d+)", src, re.M,
    ):
        ops.element("elasticBeamColumn", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), float(m.group(4)), float(m.group(5)),
                    float(m.group(6)), float(m.group(7)), float(m.group(8)),
                    float(m.group(9)), int(m.group(10)))
        n_elastic += 1
    return n_disp, n_elastic


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a cyclic wall model.

    ``save_frame_resp=False`` (dispBeamColumn internal-section convention
    shared with the other Dino fiber models).  ``set_odb_path`` precedes
    ``CreateODB`` (§12ac).  ``model_update=False`` -- topology is static.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=1,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
        save_shell_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Gravity pattern (source pattern 1): 3 x -2.433e5 N UZ."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    for nd in GRAV_NODES:
        ops.load(nd, 0.0, 0.0, P_GRAV, 0.0, 0.0, 0.0)


def define_cyclic_loads() -> None:
    """Cyclic pattern (source pattern 2, after loadConst): 1 kN UY at 26."""
    ops.timeSeries("Linear", TS_CYCLIC)
    ops.pattern("Plain", PAT_CYCLIC, TS_CYCLIC)
    ops.load(NODE_MONITOR, 0.0, P_CYCLIC, 0.0, 0.0, 0.0, 0.0)


def parse_cyclic_protocol(src: str) -> list[tuple[float, int]]:
    """Parse ``integrator DisplacementControl 26 2 <incr>`` / ``analyze <n>``
    pairs after ``pattern Plain 2`` into [(incr_mm, n_steps), ...]."""
    segs: list[tuple[float, int]] = []
    lines = src.splitlines()
    i = 0
    started = False
    pending_incr: float | None = None
    for line in lines:
        s = line.strip()
        if s.startswith("pattern Plain 2"):
            started = True
            continue
        if not started:
            continue
        m = re.match(r"integrator\s+DisplacementControl\s+26\s+2\s+"
                     r"([\d.eE+-]+)", s)
        if m:
            pending_incr = float(m.group(1))
            continue
        m = re.match(r"analyze\s+(\d+)", s)
        if m and pending_incr is not None:
            segs.append((pending_incr, int(m.group(1))))
            pending_incr = None
    return segs


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB") -> bool:
    """Gravity phase (source: LoadControl 1, 1 step).

    Manual ``ops.analyze(1)`` loop is the §3c permitted exception for
    LoadControl (SmartAnalyze forces DisplacementControl).  Ends with
    ``loadConst`` + ``wipeAnalysis`` exactly as the source.
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0)
    ops.analysis("Static")

    history: list[tuple[float, float, float, float]] = []
    ok = ops.analyze(1)
    if ok == 0:
        odb.fetch_response_step()
        ops.reactions()
        history.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_MONITOR, 1)),
            float(ops.nodeDisp(NODE_MONITOR, 2)),
            float(ops.nodeDisp(NODE_MONITOR, 3)),
        ))
    else:
        print(f"  WARNING: gravity step failed (ok={ok})")
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()
    run_gravity.history = history  # type: ignore[attr-defined]
    return ok == 0


def run_cyclic(odb: "opst.post.CreateODB",
               protocol: list[tuple[float, int]]) -> bool:
    """Cyclic phase: 9 DisplacementControl segments via SmartAnalyze.

    Each ``(incr, n)`` pair is fed as one target (static_split with
    maxStep=|incr|) so the recorder stays 1:1 with the reference (§12am
    per-increment cadence).  Full SmartAnalyze fallback (relaxation +
    minStep) for fiber-section softening at load reversals.
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="NormDispIncr",
        testTol=1.0e-5,
        testIterTimes=200,
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50, 60],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-4,
        printPer=0,
        testPrintFlag=0,
    )

    history: list[tuple[float, float, float, float]] = []  # (lf, ux, uy, uz)
    ok = 0
    for si, (incr, n) in enumerate(protocol):
        target = incr * n
        segs = analysis.static_split([target], maxStep=abs(incr))
        step_ok = True
        for seg in segs:
            ok = analysis.StaticAnalyze(
                node=NODE_MONITOR, dof=CTRL_DOF, seg=seg)
            if ok < 0:
                step_ok = False
                break
            odb.fetch_response_step()
            ops.reactions()
            # One history row per converged sub-step: with no subdivision
            # this is exactly n rows per segment (1:1 with the reference).
            history.append((
                float(ops.getTime()),
                float(ops.nodeDisp(NODE_MONITOR, 1)),
                float(ops.nodeDisp(NODE_MONITOR, 2)),
                float(ops.nodeDisp(NODE_MONITOR, 3)),
            ))
        if not step_ok:
            print(f"  WARNING: cyclic segment {si} failed (ok={ok})")
            break
        print(f"  ... segment {si + 1}/{len(protocol)}: incr={incr} mm "
              f"x {n} -> UY={history[-1][2]:.2f} mm", flush=True)
    analysis.close()
    run_cyclic.history = history  # type: ignore[attr-defined]
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run gravity + cyclic, return ODB + results.

    NOTE on history cadence: the reference recorder writes one row per
    converged analyze step (901 clean rows expected).  SmartAnalyze may
    subdivide troubled increments, so per-sub-step history rows are
    recorded and compared on the UY-imposed axis (see post_process).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    src = TCL_FILE.read_text(encoding="gbk", errors="replace")

    init_model()
    define_materials()
    define_sections(src)
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_disp, n_elastic = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_disp} dispBeamColumn + {n_elastic} "
          f"elasticBeamColumn (expected 12 + 24).", flush=True)

    protocol = parse_cyclic_protocol(src)
    print(f"  Parsed protocol: {len(protocol)} segments, "
          f"{sum(n for _, n in protocol)} steps.", flush=True)

    odb = create_odb(output_dir)

    # Gravity (before loadConst).
    define_gravity_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running gravity analysis...", flush=True)
    run_gravity(odb)

    # Cyclic (after loadConst, §12z-1).
    define_cyclic_loads()
    print("Running cyclic analysis...", flush=True)
    run_cyclic(odb, protocol)

    # Reference node-26 history, robust to the file's artifacts (one
    # 5-column glitch row + restart overlap rows): keep valid 4-col rows.
    ref_rows: list[list[float]] = []
    if REF_FILE.exists():
        for line in REF_FILE.read_text().splitlines():
            p = line.split()
            if len(p) == 4:
                try:
                    ref_rows.append([float(x) for x in p])
                except ValueError:
                    pass
    ref = np.array(ref_rows, dtype=float).T if ref_rows else None  # (4, M)

    ghist = np.array(getattr(run_gravity, "history", []),
                     dtype=float).T  # (4,<=1)
    phist = np.array(getattr(run_cyclic, "history", []),
                     dtype=float).T  # (4,<=segs)
    parts = []
    if ghist.size:
        parts.append(ghist)
    if phist.size:
        parts.append(phist)
    hist = np.concatenate(parts, axis=1) if parts else None
    results = {"hist": hist, "ref": ref, "protocol": protocol}
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot hysteresis, verify.

    The reference file carries a mid-protocol divergence glitch plus
    restart-overlap rows (917 valid rows vs 901 clean steps), so validation
    is glitch-aware: clean-prefix comparison (first 856 rows, before the
    glitch) + final-state comparison + envelope check.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis.
    """
    odb.save_response()

    hist = results["hist"]
    ref = results["ref"]

    # Dump the simulation history for the record.
    if hist is not None and hist.shape[1] > 0:
        step = np.arange(hist.shape[1])
        curve = np.column_stack([step, hist.T])  # (N,5): idx, LF, UX, UY, UZ
        np.savetxt(str(output_dir / "node26_disp_history.csv"), curve,
                   delimiter=",", header="idx,lf,ux_mm,uy_mm,uz_mm")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))

        # V5 -- peak deformed shape (cyclic is lateral -> UY)
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=1, resp_dof="UY", scale=10.0)
        # V6 -- step slider
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=1, resp_dof="UY", scale=10.0)
        # V7 -- animation
        vis_anim(output_dir, filename="vis_07_animation.html",
                 odb_tag=1, defo_scale=10.0,
                 resp_dof=("UX", "UY", "UZ"))

    # Hysteresis (LF vs UY): simulation vs reference (matplotlib).
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        if ref is not None and ref.shape[1] > 0:
            ax1.plot(ref[2], ref[0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node26.out)")
        if hist is not None and hist.shape[1] > 0:
            ax1.plot(hist[2], hist[0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax1.set_xlabel(f"Node {NODE_MONITOR} UY displacement (mm)")
        ax1.set_ylabel("Load factor")
        ax1.set_title("Dino_ShearWallCyclic -- hysteresis (UY vs LF)")
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        if ref is not None and ref.shape[1] > 0:
            ax2.plot(np.arange(ref.shape[1]), ref[0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node26.out)")
        if hist is not None and hist.shape[1] > 0:
            ax2.plot(np.arange(hist.shape[1]), hist[0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax2.set_xlabel("Recorded step")
        ax2.set_ylabel("Load factor")
        ax2.set_title("Dino_ShearWallCyclic -- load factor history")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "cyclic_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable -- skipping compare plot)")

    # Verification summary (glitch-aware segment alignment).
    n_sim = hist.shape[1] if hist is not None else 0
    n_ref = ref.shape[1] if ref is not None else 0
    print(f"\n  Recorded steps: sim {n_sim} / ref {n_ref} valid rows",
          flush=True)
    if hist is not None and n_sim > 0:
        labels = ("LF", "UX", "UY", "UZ")
        for d in range(4):
            print(f"  Sim node{NODE_MONITOR} {labels[d]} final = "
                  f"{float(hist[d, -1]):.5f}", flush=True)
        if ref is not None and n_ref > 0:
            # The pre-glitch reference is exactly 100 rows per segment
            # (rows 1-800 = segments 1-8 after the gravity row 0); the
            # segment-9 region (rows 801+) carries the divergence glitch +
            # restart overlap, so it is compared by peak only.  Index
            # alignment is exact pre-glitch (no extras there).
            print("  Per-segment peak |LF|:", flush=True)
            peak_errs = []
            for k in range(9):
                c, e = 1 + 100 * k, 1 + 100 * (k + 1)
                sv = hist[0, c:e] if e <= n_sim else hist[0, c:]
                if k < 8:
                    rv = ref[0, c:e] if e <= n_ref else ref[0, c:]
                else:
                    rv = ref[0, c:]  # seg-9 region incl. glitch + overlap
                sp = float(np.max(np.abs(sv))) if sv.size else float("nan")
                rp = float(np.max(np.abs(rv))) if rv.size else float("nan")
                pe = abs(sp - rp) / max(abs(rp), 1e-12) * 100.0
                peak_errs.append(pe)
                print(f"    seg{k + 1}: sim peak {sp:.3f} vs "
                      f"ref peak {rp:.3f} ({pe:.2f}%)", flush=True)
            print(f"    mean segment-peak error: "
                  f"{float(np.nanmean(peak_errs)):.3f}%", flush=True)
            # Pointwise check on the clean prefix (rows 0-800, exact).
            # NOTE: plain mean-rel-error is meaningless here (it explodes at
            # load reversals where LF crosses zero); RMS normalized by the
            # reference peak scale is the robust figure.
            n_pre = min(n_sim, n_ref, 801)
            sv, rv = hist[0, :n_pre], ref[0, :n_pre]
            rms = float(np.sqrt(np.mean((sv - rv) ** 2)))
            scale = float(np.max(np.abs(rv)))
            print(f"    LF clean-prefix ({n_pre} rows): RMS {rms:.5f} "
                  f"(= {rms / scale * 100.0:.3f}% of ref peak {scale:.2f})",
                  flush=True)
            print(f"    LF final: sim={float(hist[0, -1]):.4f} "
                  f"ref={float(ref[0, -1]):.4f}", flush=True)
            print(f"    UY final: sim={float(hist[2, -1]):.4f} "
                  f"ref={float(ref[2, -1]):.4f}", flush=True)


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_ShearWallCyclic: analysis complete.")
