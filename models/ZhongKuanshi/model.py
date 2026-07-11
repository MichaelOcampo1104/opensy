# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : RC Beam-Column Shear-Hinge Calibration (Naish 2015 test series)
UniqueID : ZhongKuanshi
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-11
Purpose  : Calibrate HystereticSM shear hinges against 7 cyclic beam-column
           joint tests (Naish 2015) using the Zhong (2016) calibration framework.
Ref      : Zhong, K. (2016). ShearHingeCalibration framework, Stanford University.
           Naish, D. (2015). RC beam-column joint test database.
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
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
# Materials
MAT_ELASTIC_BEAM = 1     # Elastic material for beam-column stiffness (Ec)
MAT_HINGE        = 2     # HystereticSM shear hinge

# Geometric transformation
TRANS_BEAM       = 1

# Elements
ELE_BEAM_LEFT    = 1     # elasticBeamColumn: fixed-end → hinge-left
ELE_BEAM_RIGHT   = 2     # elasticBeamColumn: hinge-right → loaded-end
ELE_HINGE        = 3     # zeroLength: shear hinge (DOF 2)

# Nodes
NODE_FIX_L       = 1     # left fixed support  (pin: UX, UY, RZ fixed)
NODE_HINGE_L     = 2     # hinge left node (master)
NODE_HINGE_R     = 3     # hinge right node (slave via equalDOF)
NODE_FIX_R       = 4     # right loaded end   (roller: UX, RZ free; UY loaded)

# Load patterns / time series
TS_LOAD          = 1     # Linear time series for lateral reference load
PAT_LOAD         = 1     # Plain pattern for lateral reference

# ODB / analysis
ODB_TAG          = 1


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source units: imperial (in, kip, ksi). All values converted to N-mm-MPa below.
# ---------------------------------------------------------------------------
# Case database — 7 specimens from the Naish (2015) RC beam-column joint series.
# Each tuple: (case_id, b_in, h_in, L_in, fc_ksi,
#              V1..V5 [kip], theta1..theta5 [-], px, py, beta, rnp, rpp)
# Backbone:  y_i = V_i * rpp,  x_i = theta_i * L   (positive envelope)
#            y_i = -V_i * rpp * rnp, x_i = -theta_i * L  (negative envelope)
# rpp = positive residual/proportional factor; rnp = negative ratio.
# ---------------------------------------------------------------------------
# Derived from hinge_calibration_examples.csv (source CSV, imperial units).
CASES = {
    "naish_cb24f": dict(
        b=12.0, h=15.0, L=36.0, fc=6.85,
        V=[23.27, 121.52, 141.0, 146.64, 45.12],
        th=[0.0006446, 0.0075, 0.012, 0.08, 0.11],
        px=0.5, py=0.6, beta=0.35, rnp=1.16, rpp=1.0,
    ),
    "naish_cb24d": dict(
        b=12.0, h=15.0, L=36.0, fc=6.85,
        V=[26.1, 142.6, 145.0, 159.21, 55.1],
        th=[0.0006706, 0.0081, 0.013, 0.08, 0.11],
        px=0.5, py=0.7, beta=0.35, rnp=0.97, rpp=1.0,
    ),
    "naish_cb24f-rc": dict(
        b=12.0, h=15.0, L=36.0, fc=7.31,
        V=[33.93, 135.72, 174.0, 191.4, 48.72],
        th=[0.0007143, 0.0071, 0.013, 0.08, 0.1207],
        px=0.5, py=0.6, beta=0.38, rnp=0.96, rpp=1.0,
    ),
    "naish_cb24f-pt": dict(
        b=12.0, h=15.0, L=36.0, fc=7.24,
        V=[33.66, 155.21, 187.0, 211.31, 46.75],
        th=[0.0009252, 0.0075, 0.0125, 0.08, 0.12],
        px=0.5, py=0.6, beta=0.3, rnp=0.98, rpp=1.0,
    ),
    "naish_cb24f-12-pt": dict(
        b=12.0, h=15.0, L=36.0, fc=6.99,
        V=[32.94, 150.06, 183.0, 188.49, 68.43],
        th=[0.0006583, 0.0078, 0.0127, 0.06, 0.09],
        px=0.5, py=0.5, beta=0.38, rnp=0.97, rpp=1.0,
    ),
    "naish_cb33f": dict(
        b=12.0, h=18.0, L=60.0, fc=6.85,
        V=[26.18, 105.91, 119.0, 123.76, 30.46],
        th=[0.00076055, 0.008, 0.0135, 0.06, 0.1],
        px=0.5, py=0.55, beta=0.36, rnp=0.9, rpp=1.0,
    ),
    "naish_cb33d": dict(
        b=12.0, h=18.0, L=60.0, fc=6.85,
        V=[23.65, 88.15, 107.5, 120.4, 43.75],
        th=[0.000606379, 0.0065, 0.013, 0.08, 0.1],
        px=0.5, py=0.6, beta=0.45, rnp=0.9, rpp=1.0,
    ),
}

# Default case (overridable via argv[1])
DEFAULT_CASE = "naish_cb24d"

# Analysis parameters
DINCR    = 0.0001          # incremental step (chord rotation rad — source value)
# EnergyIncr tolerance — source Tcl uses Tol=1e-4 in kip·in energy units.
# Converting to N·mm:  1e-4 kip·in × (4448.22 N/kip × 25.4 mm/in) ≈ 11.3 N·mm.
LBIN2NMM = kip * inch          # 1 kip·in → N·mm  (= 112,984.8)
TOL      = 1.0e-4 * LBIN2NMM   # → ~11.3 N·mm  (source tolerance, unit-converted)
NUM_ITER = 800             # max iterations per step


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 2D model (ndm=2, ndf=3)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials(case: dict) -> None:
    """Define the elastic beam material and the HystereticSM shear hinge.

    Args:
        case: Case dictionary with b, h, L, fc, V, th, px, py, beta, rnp, rpp.
    """
    # Concrete elastic modulus:  ACI 318  E = 57000*sqrt(fc')  [psi → ksi]
    #   fc is in ksi; fc*1000 → psi; sqrt → psi^0.5; ÷1000 → ksi
    Ec_ksi = (57000.0 * (case["fc"] * 1000.0) ** 0.5) / 1000.0
    Ec = Ec_ksi * ksi          # → MPa (N/mm²)

    # Elastic material for beam-column elements
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_BEAM, Ec)

    # ── HystereticSM shear-hinge backbone (force-deformation) ──
    # Source convention (imperial):
    #   y_i = V_i * rpp            [kip]    → convert to N
    #   x_i = theta_i * L          [in]     → convert to mm
    #   y_i_neg = -V_i * rpp * rnp [kip]    → convert to N
    #   x_i_neg = -theta_i * L     [in]     → convert to mm
    # The HystereticSM material defines a uniaxial force-deformation law; the
    # zeroLength element maps DOF 2 (transverse) so "force" = shear, "deformation"
    # = transverse displacement = chord-rotation × length.
    V  = case["V"]
    th = case["th"]
    L  = case["L"] * inch          # mm
    rnp = case["rnp"]
    rpp = case["rpp"]

    pos_y = [V[i] * rpp * kip for i in range(5)]           # N
    pos_x = [th[i] * L for i in range(5)]                  # mm
    neg_y = [-V[i] * rpp * rnp * kip for i in range(5)]    # N
    neg_x = [-th[i] * L for i in range(5)]                 # mm

    ops.uniaxialMaterial(
        "HystereticSM", MAT_HINGE,
        "-posEnv", pos_y[0], pos_x[0], pos_y[1], pos_x[1],
                   pos_y[2], pos_x[2], pos_y[3], pos_x[3],
                   pos_y[4], pos_x[4],
        "-negEnv", neg_y[0], neg_x[0], neg_y[1], neg_x[1],
                   neg_y[2], neg_x[2], neg_y[3], neg_x[3],
                   neg_y[4], neg_x[4],
        "-pinch", case["px"], case["py"],
        "-damage", 0.0, 0.0,
        "-beta", case["beta"],
    )

    # Geometric transformation (PDelta per source)
    ops.geomTransf("PDelta", TRANS_BEAM)

    # Store Ec-derived section properties for define_elements()
    case["_Ec"] = Ec
    case["_Ag"] = case["b"] * inch * case["h"] * inch          # mm²
    case["_Ig"] = case["b"] * inch * (case["h"] * inch) ** 3 / 12.0  # mm⁴


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    """No fiber sections — beams use elasticBeamColumn with A, E, I directly."""
    pass


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes(case: dict) -> None:
    """Define the 4-node shear-hinge subassembly.

    Topology (half-symmetry → doubled to full beam):
      Node 1 (fixed) ──E1── Node 2 ──zeroLength── Node 3 ──E2── Node 4 (loaded)
      |← L/2 →|← hinge →|← L/2 →|
    Nodes 2 & 3 are coincident at mid-span; the zeroLength carries the shear
    hinge on DOF 2; equalDOF ties DOFs 1 & 3 (axial + rotation).

    Args:
        case: Case dictionary (L used for node positions).
    """
    L = case["L"] * inch          # mm
    ops.node(NODE_FIX_L,   0.0 * L, 0.0)
    ops.node(NODE_HINGE_L, 0.5 * L, 0.0)
    ops.node(NODE_HINGE_R, 0.5 * L, 0.0)
    ops.node(NODE_FIX_R,   1.0 * L, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Apply fixities and the equalDOF constraint linking hinge nodes.

    Node 1: pin (UX, UY, RZ fixed).
    Node 4: roller (UY fixed, UX + RZ free) — lateral load applied in UY.
    Nodes 2→3: equalDOF on DOFs 1 (UX) and 3 (RZ); DOF 2 (UY) carries the hinge.
    """
    ops.fix(NODE_FIX_L, 1, 1, 1)     # pin
    ops.fix(NODE_FIX_R, 1, 0, 1)     # roller: UX fixed, UY free, RZ fixed
    ops.equalDOF(NODE_HINGE_L, NODE_HINGE_R, 1, 3)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(case: dict) -> None:
    """Create two elastic beam-column elements + the zeroLength shear hinge.

    Args:
        case: Case dictionary (uses _Ec, _Ag, _Ig from define_materials).
    """
    Ec = case["_Ec"]
    Ag = case["_Ag"]
    Ig = case["_Ig"]

    ops.element("elasticBeamColumn", ELE_BEAM_LEFT,
                NODE_FIX_L, NODE_HINGE_L, Ag, Ec, Ig, TRANS_BEAM)
    ops.element("elasticBeamColumn", ELE_BEAM_RIGHT,
                NODE_HINGE_R, NODE_FIX_R, Ag, Ec, Ig, TRANS_BEAM)

    # zeroLength shear hinge — material 2 on DOF 2 (transverse shear)
    # -orient 1 0 0 0 1 0  →  local-x = global-X, local-y = global-Y
    ops.element("zeroLength", ELE_HINGE,
                NODE_HINGE_L, NODE_HINGE_R,
                "-mat", MAT_HINGE, "-dir", 2,
                "-orient", 1, 0, 0, 0, 1, 0)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(odb_tag: int, output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB after the model is built.

    Args:
        odb_tag: ODB tag identifier.
        output_dir: Directory for ODB files.

    Returns:
        The initialised CreateODB instance.
    """
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,     # elasticBeamColumn — not needed
        save_link_resp=True,       # zeroLength hinge force
        link_tags=[ELE_HINGE],
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_lateral_loads() -> None:
    """Define a unit lateral reference load at the loaded node (DOF 2).

    The reference magnitude is 1 N (scaled to 1.0 kip in source).  Displacement-
    Control drives the protocol; the reference load vector sets the distribution.
    """
    ops.timeSeries("Linear", TS_LOAD)
    ops.pattern("Plain", PAT_LOAD, TS_LOAD)
    ops.load(NODE_FIX_R, 0.0, 1.0 * N, 0.0)


def _load_displacement_history(case_id: str, tcl_ref: Path) -> np.ndarray:
    """Parse a LoadingParameter tcl file into a displacement array (mm).

    The source files list chord-rotation-derived displacements in inches.  This
    reads the numeric lines and converts to mm.

    Args:
        case_id: Case identifier (e.g. "naish_cb24d").
        tcl_ref: Path to the tcl_ref directory.

    Returns:
        1-D numpy array of displacement targets in mm.
    """
    # Map case_id → loading-parameter file name (source naming, capitalised)
    name_map = {
        "naish_cb24d":       "LoadingParameterCB24D-S0.tcl",
        "naish_cb24f":       "LoadingParameterCB24F-S0.tcl",
        "naish_cb24f-pt":    "LoadingParameterCB24FPT-S0.tcl",
        "naish_cb24f-rc":    "LoadingParameterCB24FRC-S0.tcl",
        "naish_cb24f-12-pt": "LoadingParameterCB24_1_2_PT-S0.tcl",
        "naish_cb33d":       "LoadingParameterCB33D-S0.tcl",
        "naish_cb33f":       "LoadingParameterCB33F-S0.tcl",
    }
    fname = name_map.get(case_id)
    if fname is None:
        raise ValueError(f"Unknown case_id '{case_id}' — no loading history")

    path = tcl_ref / "LoadingHistory" / fname
    values = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            # skip 'set ... {' and '}' lines
            if not line or line.startswith("set") or line in ("{", "}"):
                continue
            try:
                values.append(float(line))
            except ValueError:
                continue
    return np.array(values) * inch   # in → mm


def _load_test_data(case_id: str, tcl_ref: Path) -> tuple[np.ndarray, np.ndarray]:
    """Parse a test-data file into (displacement [mm], shear [N]) arrays.

    Source format: col1 = displacement [in], col2 = shear [kip].

    Args:
        case_id: Case identifier.
        tcl_ref: Path to the tcl_ref directory.

    Returns:
        (disp_mm, shear_N) arrays.
    """
    path = tcl_ref / "TestData" / f"{case_id}.txt"
    data = np.loadtxt(path)
    disp_mm = data[:, 0] * inch      # in → mm
    shear_N = data[:, 1] * kip       # kip → N
    return disp_mm, shear_N


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_cyclic(
    odb: "opst.post.CreateODB",
    disp_history: np.ndarray,
) -> tuple[list[float], list[float]]:
    """Run displacement-controlled cyclic analysis following the protocol.

    Uses a manual ops.analyze(1) loop with DisplacementControl — the source's
    RunStaticLoading.tcl algorithm (Newton + 6-algorithm fallback ladder).  The
    fallback ladder is preserved faithfully because the HystereticSM hinge has a
    severe softening branch (V5 < V3) that can defeat a single algorithm.

    Per AGENT.md §3c / §10 this is a documented exception to the SmartAnalyze
    mandate: the source's custom recovery ladder with per-step integrator resets
    is not exposed by SmartAnalyze, and the hinge softening requires the
    multi-algorithm retry chain.

    Args:
        odb: Active CreateODB instance.
        disp_history: Displacement targets in mm (control node DOF 2).

    Returns:
        (shear_history, disp_history_converged) — base shear [N] and control-node
        displacement [mm] at each converged step.
    """
    ctrl_node = NODE_FIX_R
    ctrl_dof = 2

    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", TOL, NUM_ITER, 0)
    ops.algorithm("Newton")
    ops.analysis("Static")

    shear_hist: list[float] = []
    disp_hist: list[float] = []
    current_disp = 0.0
    converged = 0

    for i, target in enumerate(disp_history):
        incr = target - current_disp
        ops.integrator("DisplacementControl", ctrl_node, ctrl_dof, incr)

        ok = ops.analyze(1)

        # ── Fallback ladder (mirrors RunStaticLoading.tcl) ──
        if ok != 0:
            # Newton with initial tangent
            ops.test("EnergyIncr", TOL, 10 * NUM_ITER, 0)
            ops.algorithm("Newton", "-initial")
            ok = ops.analyze(1)
            ops.test("EnergyIncr", TOL, NUM_ITER, 0)
            ops.algorithm("Newton")

        if ok != 0:
            # ModifiedNewton
            ops.test("EnergyIncr", 10 * TOL, 10 * NUM_ITER, 0)
            ops.algorithm("ModifiedNewton")
            ok = ops.analyze(1)
            ops.test("EnergyIncr", TOL, NUM_ITER, 0)
            ops.algorithm("Newton")

        if ok != 0:
            # ModifiedNewton with initial tangent
            ops.test("EnergyIncr", 10 * TOL, 10 * NUM_ITER, 0)
            ops.algorithm("ModifiedNewton", "-initial")
            ok = ops.analyze(1)
            ops.test("EnergyIncr", TOL, NUM_ITER, 0)
            ops.algorithm("Newton")

        if ok != 0:
            # Broyden
            ops.test("EnergyIncr", 10 * TOL, 10 * NUM_ITER, 0)
            ops.algorithm("Broyden", 20)
            ok = ops.analyze(1)
            ops.test("EnergyIncr", TOL, NUM_ITER, 0)
            ops.algorithm("Newton")

        if ok != 0:
            # NewtonLineSearch
            ops.test("EnergyIncr", 10 * TOL, 10 * NUM_ITER, 0)
            ops.algorithm("NewtonLineSearch", 0.8, 100)
            ok = ops.analyze(1)
            ops.test("EnergyIncr", TOL, NUM_ITER, 0)
            ops.algorithm("Newton")

        if ok != 0:
            print(f"  Step {i + 1}/{len(disp_history)}: FAILED at "
                  f"target {target:+.4f} mm — stopping.")
            break

        current_disp = target
        odb.fetch_response_step()
        converged += 1

        # Base shear from the zeroLength hinge element force (DOF 2 component).
        # The source reads nodeReaction(node 1, DOF 2), but under OpenSeesPy's
        # equalDOF + Plain constraints the retained-node reaction includes the
        # MP-constraint force, giving spurious values past first yield.  The
        # zeroLength global-Y force IS the hinge shear.  Negated to match the
        # source's reaction sign convention (positive shear opposes positive
        # displacement at the loaded node).
        ele_forces = ops.eleResponse(ELE_HINGE, "forces")
        shear = -ele_forces[1] if len(ele_forces) > 1 else 0.0   # global Y comp
        shear_hist.append(shear)
        disp_hist.append(current_disp)

    print(f"  Converged {converged}/{len(disp_history)} steps.")
    return shear_hist, disp_hist


def run_analysis(
    output_dir: Path,
    case_id: str = DEFAULT_CASE,
    tcl_ref: Path | None = None,
) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run cyclic analysis, return ODB + results dict.

    Args:
        output_dir: Directory for ODB + HTML visualisations.
        case_id: Case identifier from the CASES registry.
        tcl_ref: Path to tcl_ref/ (for loading history + test data).

    Returns:
        (odb, results) where results has keys: shear, disp, test_disp, test_shear.
    """
    if case_id not in CASES:
        raise ValueError(f"Unknown case '{case_id}'. Available: {list(CASES)}")
    case = CASES[case_id]

    if tcl_ref is None:
        tcl_ref = Path(__file__).parent / "tcl_ref"

    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials(case)
    define_sections()
    define_nodes(case)
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements(case)
    vis_model(output_dir)

    odb = create_odb(ODB_TAG, output_dir)

    define_lateral_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    disp_history = _load_displacement_history(case_id, tcl_ref)
    print(f"[{case_id}] Cyclic protocol: {len(disp_history)} steps, "
          f"peak ±{np.max(np.abs(disp_history)):.2f} mm "
          f"(drift ±{np.max(np.abs(disp_history)) / (case['L'] * inch) * 100:.1f}%)")

    shear_hist, disp_hist = run_cyclic(odb, disp_history)

    # Load test data for comparison
    test_disp, test_shear = _load_test_data(case_id, tcl_ref)

    results = {
        "shear": np.array(shear_hist),
        "disp": np.array(disp_hist),
        "test_disp": test_disp,
        "test_shear": test_shear,
    }

    # Save hysteresis curve as CSV (shear [N], disp [mm])
    if len(shear_hist) > 0:
        curve = np.column_stack([results["shear"], results["disp"]])
        np.savetxt(str(output_dir / "hysteresis_curve.csv"), curve,
                   delimiter=",", header="shear_N,disp_mm")

    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
    case_id: str = DEFAULT_CASE,
) -> None:
    """Flush ODB, render deformed-shape visualisations, plot hysteresis.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis (shear, disp, test_disp, test_shear).
        case_id: Case identifier (for plot title).
    """
    odb.save_response()

    if not _headless():
        # Deformed shape — peak (absMax step)
        opst.post.set_odb_path(str(output_dir))
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UY", scale=50.0)

        # V6 — step slider: scrub through every converged step
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UY", scale=50.0)

        # V7 — animation: auto-play the deformation evolution
        vis_anim(output_dir, filename="vis_07_animation.html",
                 odb_tag=ODB_TAG, defo_scale=50.0,
                 resp_dof=("UX", "UY"))

        # Hysteresis curve: simulation vs test (matplotlib)
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(1, 1, figsize=(7, 5))
            if len(results["test_disp"]) > 0:
                ax.plot(results["test_disp"], results["test_shear"],
                        "k-", linewidth=1.0, alpha=0.7, label="Test")
            if len(results["disp"]) > 0:
                ax.plot(results["disp"], results["shear"],
                        "r--", linewidth=1.0, alpha=0.8, label="Simulation")
            ax.set_xlabel("Displacement (mm)")
            ax.set_ylabel("Shear (N)")
            ax.set_title(f"{case_id} — Shear hinge calibration")
            ax.legend()
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            fig.savefig(str(output_dir / "hysteresis_compare.png"), dpi=150)
            plt.close(fig)
        except ImportError:
            print("  (matplotlib unavailable — skipping hysteresis plot)")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Case selection: argv[1] overrides default
    case = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CASE

    if case == "all":
        # Run the full 7-case sweep
        tcl_ref = Path(__file__).parent / "tcl_ref"
        for cid in CASES:
            print(f"\n{'=' * 60}")
            print(f"  Running case: {cid}")
            print(f"{'=' * 60}")
            out = Path(__file__).parent / "output" / cid
            odb, res = run_analysis(out, cid, tcl_ref)
            post_process(odb, out, res, cid)
            print(f"[{cid}] complete → {out}")
    else:
        out = Path(__file__).parent / "output" / case
        odb, res = run_analysis(out, case)
        post_process(odb, out, res, case)
        print(f"[{case}] complete → {out}")
