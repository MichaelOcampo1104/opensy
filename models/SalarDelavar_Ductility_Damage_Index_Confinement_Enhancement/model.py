# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D reinforced-concrete frame, the same as CONFINEMENT_NONCONSTANT_ELASTIC_OR_INELASTIC_FRAME: two 3 m columns
           (500 x 500 mm) and a 7 m beam (500 x 300 mm), both bases fixed, fibre sections whose confinement enhancement ratio
           differs between the elements (Kc = 1.25 for elements 1, 3, 4 and 6; Kc - 0.15 for 2 and 5; Kc - 0.1 for 7 and 9;
           Kc - 0.2 for 8). Corotational nonlinearBeamColumn elements with 10 integration points (inelastic only, as in the
           source).
UniqueID : SalarDelavar_Ductility_Damage_Index_Confinement_Enhancement
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-25
Purpose  : Structural ductility damage index of the frame: the monotonic pushover to 675 mm (base-shear bilinear fit with the
           over-strength factor, displacement ductility and R) and the index DI = (Dd - Dy) / (Du - Dy), where Dd is the peak
           node-3 displacement of a time history under the X record scaled by 0.01 g (the source's SSF_X), with the source's
           ramp load, Rayleigh damping, the period history and the logarithmic-decrement damping estimate.
Ref      : py_ref/CONCRETE_FRAME_DUCTILITY_DAMAGE_INDEX_CONFINEMENT_ENHANCEMENT_RATIO.py (source main), CONCRETE_SECTION_FUN_TWO.py
           (section), ANALYSIS_FUNCTION.py (its fallback ladder is replaced by SmartAnalyze), BILINEAR_CURVE.py,
           DAMPING_RATIO_FUN.py (this sub-model's version), RAYLEIGH_DAMPING_FUN.py, EIGENVALUE_ANALYSIS_FUN.py,
           PLOT_2D.py (not run), SALAR_MATH.py (not imported by the source's main), COVER.png (reference figure).
           Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO/DUCTILITY_DAMAGE_INDEX_CONFINEMENT_ENHANCEMENT_RATIO
Units    : N, mm, MPa  (see standards/units.py); time in s
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops
import opstool as opst

# models/<UniqueID>/model.py -> repository root is parents[2]
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *  # noqa: E402,F403  (N, mm, sec, MPa)
from vis_utils import (  # noqa: E402
    vis_curves,
    vis_defo,
    vis_loads,
    vis_model,
    vis_nodes,
    vis_pre_analysis,
)
from plot_utils import COLORS, _style_ax  # noqa: E402

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
ODB_PUSH_I = "pushover_inelastic"
ODB_DYN_I = "dynamic_inelastic"
NODE_BASE_L, NODE_BASE_R = 1, 2
NODE_TOP_L, NODE_TOP_R = 3, 4                  # NODE_TOP_R is the pushover control node (DOF 1)
NODE_COL_L_1, NODE_COL_L_2 = 5, 6              # left column, intermediate nodes (source)
NODE_COL_R_1, NODE_COL_R_2 = 7, 8              # right column, intermediate nodes (source)
NODE_BEAM_1, NODE_BEAM_2 = 9, 10               # beam, intermediate nodes (source)
SEC_C01, SEC_C02 = 10, 20                      # column fibre sections (source secTagC01, secTagC02)
SEC_B01, SEC_B02 = 30, 40                      # beam fibre sections (source secTagB01, secTagB02)
MAT_OFFSET_CORE, MAT_OFFSET_COVER, MAT_OFFSET_STEEL = 100, 200, 300   # source: sec + 100, + 200, + 300
TRANSF = 1                                     # corotational transformation (source)
TS_LINEAR, PAT_LINEAR = 1, 1                   # Linear time series and pattern (pushover load and the ramp of the dynamic run)
TS_GROUND_X, PAT_GROUND_X = 100, 100           # ground motion in X (source tags 100)
NUM_INT_POINTS = 10                            # integration points per inelastic element (source numIntgrPts)
NUM_FIBERS = 40                                # fibres along the depth of each patch (source NUMFIBERS)
NUM_FIBERS_Z = 5                               # fibres across the width of each patch

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Concrete and reinforcing steel (source CONFINED_CONCRETE_SECTION; steel values of the source's STEEL_KIND 2)
fc = 25.0 * MPa                 # unconfined concrete compressive strength (source fc)
KC = 1.25                       # confinement enhancement ratio of elements 1, 3, 4 and 6 (source Kc)
FY_STEEL = 4000.0 * MPa         # yield stress (source fy), as written
ES_STEEL = 2.0e5 * MPa          # modulus (source Es)
EY_STEEL = FY_STEEL / ES_STEEL  # yield strain (source ey)
FU_STEEL = 1.1818 * FY_STEEL    # ultimate stress (source fu)
ESU_STEEL = EY_STEEL * 75.2     # ultimate strain (source esu)
PINCH_X, PINCH_Y = 0.8, 0.5     # Hysteretic pinching factors (source)
DAMAGE_1, DAMAGE_2 = 0.0, 0.0   # Hysteretic damage factors (source)
BETA_HYS = 0.1                  # Hysteretic stiffness degradation (source beta)

# Column section (source Bc, Hc, coverC, DIAc): both sides 500 mm
B_COL = 500.0 * mm
H_COL = 500.0 * mm
COVER_COL = 50.0 * mm
DIA_COL = 25.0 * mm
A_BAR_COL = np.pi * DIA_COL**2 / 4.0
# Beam section (source Bb, Hb, coverB, DIAb): width Bb = 500 mm and depth Hb = 300 mm
B_BEAM = 500.0 * mm
H_BEAM = 300.0 * mm
COVER_BEAM = 50.0 * mm
DIA_BEAM = 18.0 * mm
A_BAR_BEAM = np.pi * DIA_BEAM**2 / 4.0
LENGTH_COL = 3000.0 * mm        # source LENGTH_COL
LENGTH_BEAM = 7000.0 * mm       # source LENGTH_BM
# Element masses per unit length, as written in the source (Bc*Hc*0.000025 and Bb*Hb*0.000025); see Note 5
MASS_PER_LENGTH_COL = B_COL * H_COL * 0.000025
MASS_PER_LENGTH_BEAM = B_BEAM * H_BEAM * 0.000025
# Nodal masses at nodes 3 and 4 (source MASS, labelled [kg]); used as written in N.s^2/mm (see Note 5)
MASS_NODE = 12000.0

# Dynamic analysis (source)
GM_FACT = 9810.0 * mm / sec**2  # standard acceleration of gravity in mm/s^2 (source GMfact)
SSF_X = 0.01                    # ground-motion scale factor, X (source SSF_X): 0.01 g, not 10 g as in the first sub-model
IV0_X = 0.0005 * mm / sec       # initial velocity, X (source iv0_X)
ST_IV0 = 0.0 * sec              # start time of the ground motion (source st_iv0)
DR = 0.05                       # damping ratio of mode 1; mode 2 takes 0.6 DR (source DR and 0.6*DR)
DURATION = 50.0 * sec           # total duration (source duration); the record itself is 10 s
DT = 0.01 * sec                 # time step (source dt)
NEWMARK_GAMMA, NEWMARK_BETA = 0.5, 0.25

# Pushover (source)
DMAX = 675.0 * mm               # maximum displacement (source DMAX)
DINCR = 0.05 * mm               # displacement increment (source DINCR): 13500 steps

# Analysis properties (source)
MAX_ITERATIONS = 5000           # convergence iterations (source MAX_ITERATIONS)
MAX_TOLERANCE = 1.0e-6          # convergence tolerance (source MAX_TOLERANCE)
ODB_EVERY_PUSHOVER = 20         # ODB fetch every 20 pushover steps (AGENT.md §3d)
ODB_EVERY_DYNAMIC = 10          # ODB fetch every 10 transient steps (AGENT.md §3d)


def concrete_parameters(kc: float) -> dict:
    """Concrete01 parameters of the source's CONFINED_CONCRETE_SECTION for the confinement ratio kc. The cover is the
    unconfined concrete (fc); the core takes the ratio kc."""
    fc_u = -fc                                     # unconfined peak stress (negative in compression)
    ec0_u = -0.002 * (abs(fc_u) / 30.0) ** 0.25    # strain at the peak (semi-empirical, source)
    fcu_u = 0.1 * fc_u                             # ultimate stress
    ecu_u = ec0_u * 3.5                            # ultimate strain
    fc_c = fc_u * kc                               # confined peak stress
    ec0_c = ec0_u * 1.8                            # confined strain at the peak
    fcu_c = 0.95 * fc_c                            # confined ultimate stress
    ecu_c = 1.475 * ecu_u * kc                     # confined ultimate strain
    return {"fc_u": fc_u, "ec0_u": ec0_u, "fcu_u": fcu_u, "ecu_u": ecu_u,
            "fc_c": fc_c, "ec0_c": ec0_c, "fcu_c": fcu_c, "ecu_c": ecu_c}


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Start a fresh 2D model with three DOFs per node (ux, uy, rotation)."""
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)


# ── 5. NODES AND SUPPORTS ────────────────────────────────────────────────────
def node_positions() -> dict:
    """Source node coordinates (mm): corners 1 to 4, column nodes at thirds of the column height, beam nodes at 1/7 and
    6/7 of the span."""
    return {
        NODE_BASE_L: (0.0, 0.0),
        NODE_BASE_R: (LENGTH_BEAM, 0.0),
        NODE_TOP_L: (0.0, LENGTH_COL),
        NODE_TOP_R: (LENGTH_BEAM, LENGTH_COL),
        NODE_COL_L_1: (0.0, LENGTH_COL / 3.0),
        NODE_COL_L_2: (0.0, 2.0 * LENGTH_COL / 3.0),
        NODE_COL_R_1: (LENGTH_BEAM, LENGTH_COL / 3.0),
        NODE_COL_R_2: (LENGTH_BEAM, 2.0 * LENGTH_COL / 3.0),
        NODE_BEAM_1: (LENGTH_BEAM / 7.0, LENGTH_COL),
        NODE_BEAM_2: (6.0 * LENGTH_BEAM / 7.0, LENGTH_COL),
    }


def define_nodes_and_supports() -> None:
    """Ten nodes and the fixed bases (source ops.fix(1, 1, 1, 1) and ops.fix(2, 1, 1, 1))."""
    for tag, (x, y) in node_positions().items():
        ops.node(tag, x, y)
    ops.fix(NODE_BASE_L, 1, 1, 1)
    ops.fix(NODE_BASE_R, 1, 1, 1)


# ── 6. SECTIONS (MATERIALS AND FIBRES) ───────────────────────────────────────
# tag: (depth h, width b, cover, bar area, confinement ratio kc, column flag), as the source calls
# CONFINED_CONCRETE_SECTION for each section.
SECTION_SPEC = {
    SEC_C01: (H_COL, B_COL, COVER_COL, A_BAR_COL, KC, True),
    SEC_C02: (H_COL, B_COL, COVER_COL, A_BAR_COL, KC - 0.15, True),
    SEC_B01: (H_BEAM, B_BEAM, COVER_BEAM, A_BAR_BEAM, KC - 0.1, False),
    SEC_B02: (H_BEAM, B_BEAM, COVER_BEAM, A_BAR_BEAM, KC - 0.2, False),
}


def define_fiber_section(sec_tag: int, h: float, b: float, cover: float, area_bar: float, kc: float, col: bool) -> None:
    """Confined fibre section of the source (CONFINED_CONCRETE_SECTION). Each section has its own materials, as in the
    source: core (sec + 100, Concrete01 with kc), cover (sec + 200, Concrete01, unconfined) and steel (sec + 300,
    Hysteretic). Column: three bars on each face. Beam (col = False): plus a middle layer of two bars.
    """
    p = concrete_parameters(kc)
    tag_core = sec_tag + MAT_OFFSET_CORE
    tag_cover = sec_tag + MAT_OFFSET_COVER
    tag_steel = sec_tag + MAT_OFFSET_STEEL
    ops.uniaxialMaterial("Hysteretic", tag_steel, FY_STEEL, EY_STEEL, FU_STEEL, ESU_STEEL,
                         0.2 * FU_STEEL, 1.1 * ESU_STEEL, -FY_STEEL, -EY_STEEL, -FU_STEEL, -ESU_STEEL,
                         -0.2 * FU_STEEL, -1.1 * ESU_STEEL, PINCH_X, PINCH_Y, DAMAGE_1, DAMAGE_2, BETA_HYS)
    ops.uniaxialMaterial("Concrete01", tag_core, p["fc_c"], p["ec0_c"], p["fcu_c"], p["ecu_c"])
    ops.uniaxialMaterial("Concrete01", tag_cover, p["fc_u"], p["ec0_u"], p["fcu_u"], p["ecu_u"])
    y1 = h / 2.0
    z1 = b / 2.0
    ops.section("Fiber", sec_tag)
    ops.patch("rect", tag_core, NUM_FIBERS, NUM_FIBERS_Z, cover - y1, cover - z1, y1 - cover, z1 - cover)
    ops.patch("rect", tag_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, z1 - cover, y1, z1)
    ops.patch("rect", tag_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, -z1, y1, cover - z1)
    ops.patch("rect", tag_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, cover - z1, cover - y1, z1 - cover)
    ops.patch("rect", tag_cover, NUM_FIBERS, NUM_FIBERS_Z, y1 - cover, cover - z1, y1, z1 - cover)
    ops.layer("straight", tag_steel, 3, area_bar, y1 - cover, z1 - cover, y1 - cover, cover - z1)
    if not col:
        ops.layer("straight", tag_steel, 2, area_bar, 0.0, z1 - cover, 0.0, cover - z1)
    ops.layer("straight", tag_steel, 3, area_bar, cover - y1, z1 - cover, cover - y1, cover - z1)


def define_sections() -> None:
    """The four fibre sections of the source, with the confinement ratios of their elements."""
    for sec_tag, (h, b, cover, area_bar, kc, col) in SECTION_SPEC.items():
        define_fiber_section(sec_tag, h, b, cover, area_bar, kc, col)


# ── 7. ELEMENTS ──────────────────────────────────────────────────────────────
# (tag, start node, end node, section, mass per unit length), as in the source's element list
ELEMENTS = (
    (1, NODE_BASE_L, NODE_COL_L_1, SEC_C01, MASS_PER_LENGTH_COL),
    (2, NODE_COL_L_1, NODE_COL_L_2, SEC_C02, MASS_PER_LENGTH_COL),
    (3, NODE_COL_L_2, NODE_TOP_L, SEC_C01, MASS_PER_LENGTH_COL),
    (4, NODE_BASE_R, NODE_COL_R_1, SEC_C01, MASS_PER_LENGTH_COL),
    (5, NODE_COL_R_1, NODE_COL_R_2, SEC_C02, MASS_PER_LENGTH_COL),
    (6, NODE_COL_R_2, NODE_TOP_R, SEC_C01, MASS_PER_LENGTH_COL),
    (7, NODE_TOP_L, NODE_BEAM_1, SEC_B01, MASS_PER_LENGTH_BEAM),
    (8, NODE_BEAM_1, NODE_BEAM_2, SEC_B02, MASS_PER_LENGTH_BEAM),
    (9, NODE_BEAM_2, NODE_TOP_R, SEC_B01, MASS_PER_LENGTH_BEAM),
)


def define_elements() -> None:
    """The nine elements of the source: corotational nonlinearBeamColumn with 10 integration points. The source has no
    elastic branch in this sub-model."""
    ops.geomTransf("Corotational", TRANSF)
    for tag, ni, nj, sec, mass in ELEMENTS:
        ops.element("nonlinearBeamColumn", tag, ni, nj, NUM_INT_POINTS, sec, TRANSF, "-mass", mass)


# ── 8. OUTPUT DATABASE (ODB) ─────────────────────────────────────────────────
def create_odb(odb_tag) -> "opst.post.CreateODB":
    """Nodal responses for one analysis. The model data are saved here, after the elements are defined.

    Args:
        odb_tag: Tag of this analysis (one ODB per analysis, because each analysis rebuilds the model).

    Returns:
        The CreateODB instance.
    """
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
    )
    odb.save_model_data()
    return odb


def define_nodal_masses() -> None:
    """Nodal masses at the top nodes in X and Y (source ops.mass(3, MASS, MASS, 0.0) and ops.mass(4, ...)). Dynamic runs."""
    ops.mass(NODE_TOP_L, MASS_NODE, MASS_NODE, 0.0)
    ops.mass(NODE_TOP_R, MASS_NODE, MASS_NODE, 0.0)


def build_model(odb_tag, output_dir: Path = None, dynamic: bool = False):
    """Build the frame for one analysis. The V1 and V2 stages are written when output_dir is given. The nodal masses are
    defined for the dynamic run only, as in the source.

    Returns:
        The CreateODB instance.
    """
    init_model()
    define_nodes_and_supports()
    define_sections()
    if output_dir is not None:
        vis_nodes(output_dir)                      # V1: nodes and supports
    define_elements()
    if dynamic:
        define_nodal_masses()
    if output_dir is not None:
        vis_model(output_dir)                      # V2: geometry
    return create_odb(odb_tag)


# ── 9. LOADING ───────────────────────────────────────────────────────────────
def define_push_load() -> None:
    """Reference load of the pushover (source: 1 N horizontal and -1 N vertical at nodes 3 and 4). The displacement
    control sets the load factor."""
    ops.timeSeries("Linear", TS_LINEAR)
    ops.pattern("Plain", PAT_LINEAR, TS_LINEAR)
    ops.load(NODE_TOP_L, 1.0 * N, -1.0 * N, 0.0)
    ops.load(NODE_TOP_R, 1.0 * N, -1.0 * N, 0.0)


def define_ramp_load() -> None:
    """Horizontal load of the source's dynamic run (SEI = 'X'): 1 N at nodes 3 and 4 in a Linear pattern. A Linear time
    series grows with time, so this load is t N at time t (Note 6)."""
    ops.timeSeries("Linear", TS_LINEAR)
    ops.pattern("Plain", PAT_LINEAR, TS_LINEAR)
    ops.load(NODE_TOP_L, 1.0 * N, 0.0, 0.0)
    ops.load(NODE_TOP_R, 1.0 * N, 0.0, 0.0)


def define_ground_motion_x(gm_x: Path) -> None:
    """Ground acceleration X as the source defines it: a Path series scaled by GM_FACT, and a UniformExcitation pattern in
    DOF 1 with the initial velocity IV0_X and the scale factor SSF_X (0.01 in this sub-model)."""
    ops.timeSeries("Path", TS_GROUND_X, "-dt", DT, "-filePath", str(gm_x), "-factor", GM_FACT, "-startTime", ST_IV0)
    ops.pattern("UniformExcitation", PAT_GROUND_X, 1, "-accel", TS_GROUND_X, "-vel0", IV0_X, "-fact", SSF_X)


# ── 10. ANALYSIS ─────────────────────────────────────────────────────────────
def source_rayleigh(n_modes: int, zeta_i: float, zeta_j: float, mode_i: int, mode_j: int) -> tuple:
    """Rayleigh damping of the source (RAYLEIGH_DAMPING_FUN): alpha_M and beta_K from two modes of the current state and
    their damping ratios. The source passes beta_K as the fourth argument of ops.rayleigh, which is the committed-stiffness
    coefficient, not the current-stiffness one (Note 7). This is kept as written.

    Returns:
        (alpha_m, beta_k, period_i, period_j), the periods of the two modes in s.
    """
    lam = ops.eigen("-fullGenLapack", n_modes)
    omega_i = np.sqrt(lam[mode_i])
    omega_j = np.sqrt(lam[mode_j])
    coef = np.array([[1.0 / omega_i, omega_i], [1.0 / omega_j, omega_j]])
    alpha_m, beta_k = np.linalg.solve(coef, np.array([2.0 * zeta_i, 2.0 * zeta_j]))
    ops.rayleigh(alpha_m, 0.0, 0.0, beta_k)
    return float(alpha_m), float(beta_k), float(2.0 * np.pi / omega_i), float(2.0 * np.pi / omega_j)


def period_bounds() -> tuple:
    """Shortest and longest of the first four periods of the current state (source EIGENVALUE_ANALYSIS, no printing)."""
    lam = np.asarray(ops.eigen("-fullGenLapack", 4), dtype=float)
    periods = 2.0 * np.pi / np.sqrt(lam)
    return float(np.min(periods)), float(np.max(periods))


def run_pushover(odb_tag: str, output_dir: Path = None) -> tuple:
    """Horizontal displacement control of node 4 (DOF 1) to DMAX through SmartAnalyze (source PD_ANALYSIS, PUSHOVER).

    Returns:
        (odb, history): the ODB and the per-step arrays. The base reactions keep the source's sign (no minus).
    """
    odb = build_model(odb_tag, output_dir)
    define_push_load()
    if output_dir is not None:
        vis_loads(output_dir)                      # V3: load vectors
        vis_pre_analysis(output_dir)               # V4: last check before the solver
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="NormDispIncr",
        testTol=MAX_TOLERANCE,
        testIterTimes=MAX_ITERATIONS,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 41, 40, 20, 50, 60],        # Newton first, then the fallback ladder of the source's solver
        printPer=0,
        testPrintFlag=0,
    )
    keys = ("lam", "disp_x", "disp_y", "rot", "shear", "axial", "moment", "ks", "ka", "ki", "drift_x", "drift_y")
    history = {key: [] for key in keys}
    for k, seg in enumerate(analysis.static_split([DMAX], maxStep=DINCR)):
        ok = analysis.StaticAnalyze(node=NODE_TOP_R, dof=1, seg=seg)
        if ok < 0:
            break
        if k % ODB_EVERY_PUSHOVER == 0:
            odb.fetch_response_step()
        ops.reactions()
        shear = ops.nodeReaction(NODE_BASE_L, 1) + ops.nodeReaction(NODE_BASE_R, 1)
        axial = ops.nodeReaction(NODE_BASE_L, 2) + ops.nodeReaction(NODE_BASE_R, 2)
        moment = ops.nodeReaction(NODE_BASE_L, 3) + ops.nodeReaction(NODE_BASE_R, 3)
        dx = ops.nodeDisp(NODE_TOP_L, 1)
        dy = ops.nodeDisp(NODE_TOP_L, 2)
        rot = ops.nodeDisp(NODE_TOP_L, 3)
        with np.errstate(divide="ignore", invalid="ignore"):
            history["ks"].append(float(np.abs(np.float64(shear) / np.float64(dx))))
            history["ka"].append(float(np.abs(np.float64(axial) / np.float64(dy))))
            history["ki"].append(float(np.abs(np.float64(moment) / np.float64(rot))))
        history["lam"].append(ops.getTime())
        history["disp_x"].append(dx)
        history["disp_y"].append(dy)
        history["rot"].append(rot)
        history["shear"].append(shear)
        history["axial"].append(axial)
        history["moment"].append(moment)
        history["drift_x"].append(100.0 * dx / LENGTH_COL)
        history["drift_y"].append(100.0 * dy / LENGTH_BEAM)
    analysis.close()
    return odb, {key: np.array(value) for key, value in history.items()}


def run_dynamic(odb_tag: str, gm_x: Path) -> tuple:
    """Ramp load and the X ground motion (scaled by SSF_X) through Newmark (0.5, 0.25) and SmartAnalyze, with the source's
    Rayleigh damping (source PD_ANALYSIS, DYNAMIC). The transient runs for DURATION, as in the source.

    Returns:
        (odb, history, rayleigh): rayleigh = (alpha_m, beta_k, period_i, period_j).
    """
    odb = build_model(odb_tag, dynamic=True)
    define_ramp_load()
    define_ground_motion_x(gm_x)
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    rayleigh = source_rayleigh(2, DR, 0.6 * DR, 0, 1)
    ops.integrator("Newmark", NEWMARK_GAMMA, NEWMARK_BETA)     # set before SmartAnalyze (AGENT.md §3c)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="NormDispIncr",
        testTol=MAX_TOLERANCE,
        testIterTimes=MAX_ITERATIONS,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 41, 40, 20, 50],            # Newton first, as in the source
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6 * sec,
        printPer=0,
        testPrintFlag=0,
    )
    keys = ("time", "disp_x", "disp_y", "rot", "vel_x", "acc_x", "shear", "axial", "moment", "ks", "ka", "ki",
            "drift_x", "drift_y", "period_min", "period_max")
    history = {key: [] for key in keys}
    n_steps = int(round(DURATION / DT))
    for k in analysis.transient_split(n_steps):
        ok = analysis.TransientAnalyze(DT)
        if ok < 0:
            break
        if k % ODB_EVERY_DYNAMIC == 0:
            odb.fetch_response_step()
        ops.reactions()
        shear = ops.nodeReaction(NODE_BASE_L, 1) + ops.nodeReaction(NODE_BASE_R, 1)
        axial = ops.nodeReaction(NODE_BASE_L, 2) + ops.nodeReaction(NODE_BASE_R, 2)
        moment = ops.nodeReaction(NODE_BASE_L, 3) + ops.nodeReaction(NODE_BASE_R, 3)
        dx = ops.nodeDisp(NODE_TOP_L, 1)
        dy = ops.nodeDisp(NODE_TOP_L, 2)
        rot = ops.nodeDisp(NODE_TOP_L, 3)
        with np.errstate(divide="ignore", invalid="ignore"):
            history["ks"].append(float(np.abs(np.float64(shear) / np.float64(dx))))
            history["ka"].append(float(np.abs(np.float64(axial) / np.float64(dy))))
            history["ki"].append(float(np.abs(np.float64(moment) / np.float64(rot))))
        period_min, period_max = period_bounds()
        history["time"].append(ops.getTime())
        history["disp_x"].append(dx)
        history["disp_y"].append(dy)
        history["rot"].append(rot)
        history["vel_x"].append(ops.nodeVel(NODE_TOP_L, 1))
        history["acc_x"].append(ops.nodeAccel(NODE_TOP_L, 1))
        history["shear"].append(shear)
        history["axial"].append(axial)
        history["moment"].append(moment)
        history["drift_x"].append(100.0 * dx / LENGTH_COL)
        history["drift_y"].append(100.0 * dy / LENGTH_BEAM)
        history["period_min"].append(period_min)
        history["period_max"].append(period_max)
    analysis.close()
    return odb, {key: np.array(value, dtype=float) for key, value in history.items()}, rayleigh


# ── 11. POST-PROCESSING ──────────────────────────────────────────────────────
def bilinear_fit(disp: np.ndarray, shear: np.ndarray, slope_node: int = 10) -> tuple:
    """Equal-area bilinear fit of a base-shear curve (port of the source's BILNEAR_CURVE, same formulas).

    Returns:
        (X, Y, elastic stiffness, plastic stiffness, tangent stiffness, ductility ratio, over-strength factor).
    """
    size = len(shear)
    hh = np.zeros(size - 1)
    aa = np.zeros(size - 1)
    for i in range(size - 1):
        hh[i] = disp[i + 1] - disp[i]
        aa[i] = (shear[i] + shear[i + 1]) * 0.5 * hh[i]
    area = float(np.sum(aa))
    k0 = shear[slope_node] / disp[slope_node]
    last = size - 1
    fiy = (shear[last] * max(disp) * 0.5 - area) / (shear[last] * 0.5 - k0 * max(disp) * 0.5)
    my = k0 * fiy
    X = np.array([0.0, fiy, max(disp)])
    Y = np.array([0.0, my, shear[last]])
    return (X, Y, Y[1] / X[1], Y[2] / X[2], (Y[2] - Y[1]) / (X[2] - X[1]), X[2] / X[1], Y[2] / Y[1])


def damping_ratio_source(signal) -> float:
    """Damping ratio in percent from the logarithmic decrement of the local maxima of the signal (source DAMPING_RATIO_FUN,
    this sub-model's version). The source solves x^2 - 1 + (2 pi x / mean(delta))^2 = 0 with fsolve from x0 = 1. Its
    positive root is x = |dbar| / sqrt(dbar^2 + 4 pi^2), used here directly (fsolve agrees to its tolerance). Unlike the
    first sub-model's helper, the source has no check of the number of peaks or of their sign: with fewer than two peaks,
    or a non-positive peak, the source returns NaN, and so does this port (Note 10). The record is forced, so this is only
    the source's estimate (LESSON 62)."""
    x = np.asarray(signal, dtype=float)
    peaks = np.array([x[i] for i in range(1, len(x) - 1) if x[i] > x[i - 1] and x[i] > x[i + 1]])
    if len(peaks) < 2:
        return float("nan")
    with np.errstate(divide="ignore", invalid="ignore"):
        delta = np.log(peaks[:-1] / peaks[1:])
        dbar = float(np.mean(delta))
        return 100.0 * abs(dbar) / np.sqrt(dbar**2 + 4.0 * np.pi**2)


def save_csv(output_dir: Path, name: str, columns: dict) -> None:
    """Write named columns to CSV (N, mm, s, rad)."""
    table = np.column_stack([columns[key] for key in columns])
    np.savetxt(output_dir / name, table, delimiter=",", header=",".join(columns), comments="")


def pushover_columns(push: dict) -> dict:
    """Pushover columns, named as in the first sub-model's results (the source does not export its pushover)."""
    return {"load_factor": push["lam"], "DISP_X": push["disp_x"], "DISP_Y": push["disp_y"],
            "ROTATION": push["rot"], "AXIAL_FORCE": push["axial"], "SHEAR_FORCE": push["shear"],
            "MOMENT": push["moment"], "LATERAL_ST_X": push["ks"], "LATERAL_ST_Y": push["ka"],
            "ROTATIONAL_ST": push["ki"], "DRIFT_X": push["drift_x"], "DRIFT_Y": push["drift_y"]}


def dynamic_columns(dyn: dict) -> dict:
    """Transient columns named as in the source's Excel export (its *_WO names, which the source writes without a time
    column); TIME, PERIOD_MIN and PERIOD_MAX are added here."""
    return {"TIME": dyn["time"], "DISP_X_WO": dyn["disp_x"], "DISP_Y_WO": dyn["disp_y"],
            "ROTATION_WO": dyn["rot"], "VELO_WO": dyn["vel_x"], "ACCEL_WO": dyn["acc_x"],
            "AXIAL_FORCE_WO": dyn["axial"], "SHEAR_FORCE_WO": dyn["shear"], "MOMENT_WO": dyn["moment"],
            "AXIAL_RIGIDITY_WO": np.abs(dyn["axial"]), "ROTATIONAL_ST_WO": dyn["ki"],
            "LATERAL_ST_Y_WO": dyn["ka"], "LATERAL_ST_X_WO": dyn["ks"],
            "PERIOD_MIN": dyn["period_min"], "PERIOD_MAX": dyn["period_max"]}


def write_results(output_dir: Path, push_i: dict, dyn_i: dict, ray_i: tuple, fit_i: tuple, fit_axial_i: tuple) -> None:
    """Text summaries: the pushover fit and the behaviour coefficients, the damage indices (source formulas), and the
    transient results (source printouts)."""
    X, Y, k_el, k_pl, k_tan, mu, omega = fit_i
    Dd_x = float(np.max(np.abs(dyn_i["disp_x"])))
    dix = (Dd_x - X[1]) / (X[2] - X[1])
    Xa, Ya, _, _, _, mu_a, omega_a = fit_axial_i
    Dd_y = float(np.max(np.abs(dyn_i["disp_y"])))
    diy = (Dd_y - Xa[1]) / (Xa[2] - Xa[1])
    lines = [
        f"inelastic pushover: steps {len(push_i['lam'])} of {round(DMAX / DINCR)}; last node-3 displacement X "
        f"{push_i['disp_x'][-1]:.6f} mm at load factor {push_i['lam'][-1]:.6e}",
        f"inelastic pushover: largest base shear {np.max(np.abs(push_i['shear'])):.6e} N",
        f"bilinear fit (X): X = {X[1]:.4f} mm, {X[2]:.4f} mm; Y = {Y[1]:.4f} N, {Y[2]:.4f} N",
        f"bilinear fit (X): elastic stiffness {k_el:.4f} N/mm; plastic {k_pl:.4f} N/mm; tangent {k_tan:.4f} N/mm",
        f"over-strength factor (Omega_0) = {omega:.4f}; displacement ductility (mu) = {mu:.4f}; "
        f"R = Omega_0 mu = {omega * mu:.4f}",
        f"structural ductility damage index in X: DI = (Dd - Dy) / (Du - Dy), Dd = {Dd_x:.4f} mm (peak node-3 displacement "
        f"X of the time history), Dy = {X[1]:.4f} mm, Du = {X[2]:.4f} mm: DI = {dix:.4f}",
        f"bilinear fit (Y, axial): Omega_0 = {omega_a:.4f}; mu = {mu_a:.4f}",
        f"structural ductility damage index in Y: Dd = {Dd_y:.4f} mm, Dy = {Xa[1]:.4f} mm, Du = {Xa[2]:.4f} mm: DI = {diy:.4f}",
    ]
    (output_dir / "pushover_results.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    alpha_m, beta_k, t1, t2 = ray_i
    dyn_lines = [
        f"inelastic: Rayleigh alpha_M = {alpha_m:.6e} 1/s, beta_K = {beta_k:.6e} s (committed stiffness, Note 7); periods "
        f"of the two targeted modes {t1:.6f} s and {t2:.6f} s",
        f"inelastic: period range over the run (finite values): shortest {np.nanmin(dyn_i['period_min']):.6f} s, longest "
        f"{np.nanmax(dyn_i['period_max']):.6f} s; steps with a NaN period (a negative eigenvalue of the tangent stiffness; "
        f"Note 13): {int(np.sum(np.isnan(dyn_i['period_min']) | np.isnan(dyn_i['period_max'])))} of {len(dyn_i['time'])}; "
        f"first step {dyn_i['period_min'][0]:.6f} s to {dyn_i['period_max'][0]:.6f} s; last step "
        f"{dyn_i['period_min'][-1]:.6f} s to {dyn_i['period_max'][-1]:.6f} s",
        f"inelastic: peak node-3 displacement X {Dd_x:.6f} mm, Y {Dd_y:.6f} mm; peak base shear "
        f"{np.max(np.abs(dyn_i['shear'])):.6e} N; peak base axial {np.max(np.abs(dyn_i['axial'])):.6e} N",
        f"inelastic: damping ratio from the logarithmic decrement of X (the source's estimate, not a modal ratio; "
        f"LESSON 62): {damping_ratio_source(dyn_i['disp_x']):.6f} %",
    ]
    (output_dir / "dynamic_results.txt").write_text("\n".join(dyn_lines) + "\n", encoding="utf-8")


def plot_figures(output_dir: Path, push_i: dict, dyn_i: dict, fit_i: tuple) -> None:
    """Two PNG figures: the pushover curve with the bilinear fit, and the transient displacement, base shear and periods."""
    import matplotlib.pyplot as plt

    X, Y = fit_i[0], fit_i[1]
    fig, ax = plt.subplots(figsize=(10, 7), dpi=150)
    ax.plot(np.abs(push_i["disp_x"]) / mm, np.abs(push_i["shear"]) / N, color=COLORS["secondary"], lw=1.8,
            label="inelastic")
    ax.plot(X / mm, Y / N, color="black", lw=1.0, ls=":", label="bilinear (inelastic)")
    _style_ax(ax, "Displacement in X (mm), node 3", "Base shear (N)", "Pushover: base shear vs displacement")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "pushover_curve.png")
    plt.close(fig)

    fig, axes = plt.subplots(3, 1, figsize=(10, 11), dpi=150, sharex=True)
    axes[0].plot(dyn_i["time"] / sec, dyn_i["disp_x"] / mm, color=COLORS["secondary"], lw=1.0)
    _style_ax(axes[0], "Time (s)", "Displacement X (mm)", "Node 3, X")
    axes[1].plot(dyn_i["time"] / sec, dyn_i["shear"] / N, color=COLORS["secondary"], lw=1.0)
    _style_ax(axes[1], "Time (s)", "Base shear (N)", "Base shear, sum of both bases (source sign)")
    axes[2].plot(dyn_i["time"] / sec, dyn_i["period_max"] / sec, color=COLORS["secondary"], lw=1.0, label="longest")
    axes[2].plot(dyn_i["time"] / sec, dyn_i["period_min"] / sec, color=COLORS["primary"], lw=1.0, ls="--",
                 label="shortest")
    _style_ax(axes[2], "Time (s)", "Period (s)", "Periods of the first four modes during the run")
    axes[2].legend()
    fig.tight_layout()
    fig.savefig(output_dir / "dynamic_response.png")
    plt.close(fig)


def post_process(output_dir: Path, odbs: dict, push_i: dict, dyn_i: dict, ray_i: tuple, fit_i: tuple,
                 fit_axial_i: tuple) -> None:
    """Write the CSV files, the results, the figures and the interactive views; flush the ODBs."""
    for odb in odbs.values():
        odb.save_response()
    save_csv(output_dir, "pushover_inelastic.csv", pushover_columns(push_i))
    save_csv(output_dir, "dynamic_inelastic.csv", dynamic_columns(dyn_i))
    write_results(output_dir, push_i, dyn_i, ray_i, fit_i, fit_axial_i)
    plot_figures(output_dir, push_i, dyn_i, fit_i)

    vis_curves(output_dir, [
        {"x": np.abs(push_i["disp_x"]) / mm, "y": np.abs(push_i["shear"]) / N,
         "xlabel": "Displacement in X (mm), node 3", "ylabel": "Base shear (N)", "title": "Inelastic"},
    ], filename="vis_08_pushover.html", title="Base shear vs displacement (source pushover)")
    vis_curves(output_dir, [
        {"x": dyn_i["time"] / sec, "y": dyn_i["disp_x"] / mm, "xlabel": "Time (s)",
         "ylabel": "Displacement X (mm)", "title": "Inelastic"},
    ], filename="vis_09_dynamic.html", title="Node 3 displacement under the X record (source transient)")
    vis_defo(output_dir, filename="vis_05_deformed_inelastic_pushover.html", odb_tag=ODB_PUSH_I,
             resp_dof="UX", resp_type="disp", scale=1.0)


# ── 12. VALIDATION (independent numpy calculations) ─────────────────────────
def lobatto_rule(n: int) -> tuple:
    """n-point Lobatto rule on [0, 1] as (positions, weights): the endpoints and the roots of P'_(n-1) on [-1, 1]. This is
    the rule of OpenSees' Lobatto integration of nonlinearBeamColumn."""
    coef = np.zeros(n)
    coef[n - 1] = 1.0                                       # Legendre polynomial P_(n-1)
    interior = np.polynomial.legendre.legroots(np.polynomial.legendre.legder(coef))
    x = np.concatenate(([-1.0], np.sort(interior), [1.0]))
    weight = 2.0 / (n * (n - 1) * np.polynomial.legendre.legval(x, coef) ** 2)
    return (x + 1.0) / 2.0, weight / 2.0


LOBATTO_RULE = lobatto_rule(NUM_INT_POINTS)
NDOF = 3 * len(node_positions())                            # ten nodes, three DOFs each


def frame_dof(node: int, k: int) -> int:
    """Global DOF index of DOF k (0 ux, 1 uy, 2 rotation) of a node."""
    return 3 * (node - 1) + k


def section_fibres(sec_tag: int) -> tuple:
    """Fibre list (is_concrete, E0, A, y) of a section, from the geometry of define_fiber_section and the initial tangents
    (Concrete01 E0 = 2 f'c / eps0; Hysteretic E0 = f_y / eps_y). Independent of OpenSees."""
    h, b, cover, area_bar, kc, col = SECTION_SPEC[sec_tag]
    p = concrete_parameters(kc)
    E_core = 2.0 * p["fc_c"] / p["ec0_c"]
    E_cover = 2.0 * p["fc_u"] / p["ec0_u"]
    E_steel = FY_STEEL / EY_STEEL
    y1 = h / 2.0
    z1 = b / 2.0
    rows = []

    def patch(is_conc, E, n_y, n_z, y_i, z_i, y_j, z_j):
        dy = (y_j - y_i) / n_y
        dz = (z_j - z_i) / n_z
        for i in range(n_y):
            rows.extend([(is_conc, E, dy * dz, y_i + (i + 0.5) * dy)] * n_z)

    def bars(n, y_bar):
        rows.extend([(False, E_steel, area_bar, y_bar)] * n)

    patch(True, E_core, NUM_FIBERS, NUM_FIBERS_Z, cover - y1, cover - z1, y1 - cover, z1 - cover)
    patch(True, E_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, z1 - cover, y1, z1)
    patch(True, E_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, -z1, y1, cover - z1)
    patch(True, E_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, cover - z1, cover - y1, z1 - cover)
    patch(True, E_cover, NUM_FIBERS, NUM_FIBERS_Z, y1 - cover, cover - z1, y1, z1 - cover)
    bars(3, y1 - cover)
    if not col:
        bars(2, 0.0)
    bars(3, cover - y1)
    arr = np.array(rows, dtype=float)
    return arr[:, 0] > 0.5, arr[:, 1], arr[:, 2], arr[:, 3]


def section_state(sec: tuple, N_sec: float, M_sec: float) -> tuple:
    """Strain state (eps0, kappa), with eps(y) = eps0 + kappa * y, that gives the section forces N_sec and M_sec, and the
    tangent D = [[EA, EB], [EB, EI]] at that state. Concrete fibres in tension carry no stress and no stiffness
    (Concrete01 has no tensile strength). Newton iteration on the piecewise-linear section response."""
    is_conc, E, A, y = sec
    EA = E * A
    x = np.linalg.solve(np.array([[EA.sum(), (EA * y).sum()], [(EA * y).sum(), (EA * y * y).sum()]]),
                        np.array([N_sec, M_sec]))
    for _ in range(200):
        eps = x[0] + x[1] * y
        Ea = EA * ((~is_conc) | (eps <= 0.0))
        res = np.array([(Ea * eps).sum(), (Ea * eps * y).sum()]) - np.array([N_sec, M_sec])
        jac = np.array([[Ea.sum(), (Ea * y).sum()], [(Ea * y).sum(), (Ea * y * y).sum()]])
        dx = np.linalg.solve(jac, -res)
        x = x + dx
        if np.max(np.abs(dx)) <= 1e-14 * max(1.0, np.max(np.abs(x))):
            break
    else:
        raise RuntimeError("section state did not converge")
    eps = x[0] + x[1] * y
    Ea = EA * ((~is_conc) | (eps <= 0.0))
    D = np.array([[Ea.sum(), (Ea * y).sum()], [(Ea * y).sum(), (Ea * y * y).sum()]])
    return x, D


def element_geometry(pos: dict, ni: int, nj: int) -> tuple:
    """Length and direction cosines (c, s) of an element from its start to its end node."""
    (xi, yi), (xj, yj) = pos[ni], pos[nj]
    L = float(np.hypot(xj - xi, yj - yi))
    return L, (xj - xi) / L, (yj - yi) / L


def transform(c: float, s: float) -> np.ndarray:
    """6 x 6 rotation from global to local end displacements (ux, uy, rotation at each end)."""
    R = np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]])
    Tg = np.zeros((6, 6))
    Tg[:3, :3] = R
    Tg[3:, 3:] = R
    return Tg


def classic_element(EA: float, EI: float, L: float) -> np.ndarray:
    """Textbook 6 x 6 Euler-Bernoulli frame element in local coordinates (used by the element check)."""
    a, b1, b2, c1, c2 = EA / L, 12 * EI / L**3, 6 * EI / L**2, 4 * EI / L, 2 * EI / L
    return np.array([[a, 0, 0, -a, 0, 0],
                     [0, b1, b2, 0, -b1, b2],
                     [0, b2, c1, 0, -b2, c2],
                     [-a, 0, 0, a, 0, 0],
                     [0, -b1, -b2, 0, b1, -b2],
                     [0, b2, c2, 0, -b2, c1]])


def compatibility(L: float) -> np.ndarray:
    """Basic deformations (elongation; rotation of each end relative to the chord) from the local end displacements."""
    return np.array([[-1.0, 0.0, 0.0, 1.0, 0.0, 0.0],
                     [0.0, 1.0 / L, 1.0, 0.0, -1.0 / L, 0.0],
                     [0.0, -1.0 / L, 0.0, 0.0, 1.0 / L, -1.0]])


def element_basic_stiffness(sec: tuple, L: float, q: np.ndarray, gross: bool, rule: tuple) -> np.ndarray:
    """Basic stiffness (3 x 3) of a force-based element. The basic forces are q = [N, M_i, M_j]: N is constant and M(x) is
    linear between the end moments (no distributed loads). The section flexibility at each integration point is the
    inverse of the section tangent at the state of that point's section forces; gross=True uses the uncracked section."""
    is_conc, E, A, y = sec
    EA = E * A
    flexibility = np.zeros((3, 3))
    for xi, w in zip(*rule):
        if gross:
            D = np.array([[EA.sum(), (EA * y).sum()], [(EA * y).sum(), (EA * y * y).sum()]])
        else:
            _, D = section_state(sec, q[0], q[1] * (1.0 - xi) + q[2] * xi)
        b = np.array([[1.0, 0.0, 0.0], [0.0, 1.0 - xi, xi]])
        flexibility += L * w * b.T @ np.linalg.inv(D) @ b
    return np.linalg.inv(flexibility)


def first_step_frame(gross: bool, rule: tuple) -> tuple:
    """First displacement-control step of the frame in numpy, for the pushover load (1 N horizontal and -1 N vertical at
    the top nodes). Each element is a force-based element whose section flexibilities follow the section states of the
    current solution, iterated to convergence; gross=True keeps the uncracked sections.

    Returns:
        (load factor, displacements per unit load, number of iterations).
    """
    pos = node_positions()
    elements = []
    for tag, ni, nj, sec, _ in ELEMENTS:
        L, c, s = element_geometry(pos, ni, nj)
        dofs = [frame_dof(ni, k) for k in range(3)] + [frame_dof(nj, k) for k in range(3)]
        elements.append({"sec": section_fibres(sec), "L": L, "T": transform(c, s), "dofs": dofs, "q": np.zeros(3)})
    force = np.zeros(NDOF)
    for n in (NODE_TOP_L, NODE_TOP_R):
        force[frame_dof(n, 0)] = 1.0 * N
        force[frame_dof(n, 1)] = -1.0 * N
    fixed = {frame_dof(n, k) for n in (NODE_BASE_L, NODE_BASE_R) for k in range(3)}
    free = [d for d in range(NDOF) if d not in fixed]
    u_prev = None
    for iteration in range(1, 101):
        K = np.zeros((NDOF, NDOF))
        parts = []
        for e in elements:
            kb = element_basic_stiffness(e["sec"], e["L"], e["q"], gross, rule)
            Bc = compatibility(e["L"])
            K[np.ix_(e["dofs"], e["dofs"])] += e["T"].T @ (Bc.T @ kb @ Bc) @ e["T"]
            parts.append((kb, Bc))
        u = np.zeros(NDOF)
        u[free] = np.linalg.solve(K[np.ix_(free, free)], force[free])
        for e, (kb, Bc) in zip(elements, parts):
            e["q"] = kb @ (Bc @ (e["T"] @ u[e["dofs"]]))
        if u_prev is not None and np.max(np.abs(u - u_prev)) <= 1e-12 * np.max(np.abs(u)):
            return (DINCR / mm) / u[frame_dof(NODE_TOP_R, 0)], u, iteration
        u_prev = u
    raise RuntimeError("the first-step iteration did not converge")


def assemble_linear() -> tuple:
    """Linear stiffness (gross sections, initial tangents) and lumped mass of the frame, all DOFs (no nodal masses). The
    element mass is lumped as OpenSees does for the -mass option: m L / 2 at each end in X and Y, and no rotational inertia
    (LESSON 69). The lumped matrix is diagonal, so the rotational DOFs of the frame carry no mass."""
    pos = node_positions()
    K = np.zeros((NDOF, NDOF))
    M = np.zeros((NDOF, NDOF))
    for tag, ni, nj, sec, mass in ELEMENTS:
        is_conc, E, A, y = section_fibres(sec)
        EA = float(np.sum(E * A))
        EI = float(np.sum(E * A * y * y))
        L, c, s = element_geometry(pos, ni, nj)
        Tg = transform(c, s)
        dofs = [frame_dof(ni, k) for k in range(3)] + [frame_dof(nj, k) for k in range(3)]
        K[np.ix_(dofs, dofs)] += Tg.T @ classic_element(EA, EI, L) @ Tg
        for node in (ni, nj):
            for k in (0, 1):
                M[frame_dof(node, k), frame_dof(node, k)] += mass * L / 2.0
    return K, M


def add_nodal_masses(M: np.ndarray) -> np.ndarray:
    """Adds the nodal masses of the dynamic run to the lumped element masses (top nodes, X and Y)."""
    M = M.copy()
    for n in (NODE_TOP_L, NODE_TOP_R):
        M[frame_dof(n, 0), frame_dof(n, 0)] += MASS_NODE
        M[frame_dof(n, 1), frame_dof(n, 1)] += MASS_NODE
    return M


def free_dofs() -> list:
    """Free DOFs of the frame (all but the two fixed bases)."""
    fixed = {frame_dof(n, k) for n in (NODE_BASE_L, NODE_BASE_R) for k in range(3)}
    return [d for d in range(NDOF) if d not in fixed]


def finite_eigenvalues(K: np.ndarray, M: np.ndarray, count: int) -> np.ndarray:
    """Lowest `count` finite eigenvalues (rad^2/s^2) of K phi = lambda M phi on the free DOFs. M is diagonal; its zero rows
    (the rotational DOFs of the lumped mass) are condensed out, which gives the finite eigenvalues OpenSees returns."""
    free = free_dofs()
    Kf = K[np.ix_(free, free)]
    d = np.diag(M)[free]
    t = np.where(d > 0.0)[0]
    r = np.where(d == 0.0)[0]
    K_cond = Kf[np.ix_(t, t)] - Kf[np.ix_(t, r)] @ np.linalg.solve(Kf[np.ix_(r, r)], Kf[np.ix_(r, t)])
    lam = np.sort(np.linalg.eigvals(np.linalg.solve(np.diag(d[t]), K_cond)).real)
    return lam[:count]


def validate(output_dir: Path, push_i: dict, dyn_i: dict, ray_i: tuple) -> None:
    """Compare the OpenSees runs with independent numpy calculations and write validation.txt.

    Checks: (1) the force-based element with gross sections against the textbook frame element; (2) the first pushover
    step of the inelastic run (section states of the first step, 10 Lobatto points) and the equilibrium of the base
    reactions at every step of the pushover; (3) the periods and the Rayleigh coefficients of the lumped-mass frame against
    OpenSees (the dynamic run starts from the initial tangents, as the frame does here). The time history under the ramp
    and the scaled ground motion is not replicated: the frame is cracked, so its transient is nonlinear, and only its
    start is compared (its first periods). The bilinear fits, the damage indices and the behaviour coefficients are
    outputs of the source's formulas, ported, and are reported, not validated.
    """
    report = []
    sec_c = section_fibres(SEC_C01)
    _, E_c, A_c, y_c = sec_c
    EA_c = float(np.sum(E_c * A_c))
    EI_c = float(np.sum(E_c * A_c * y_c * y_c))
    L_col = element_geometry(node_positions(), NODE_BASE_L, NODE_COL_L_1)[0]
    Bc = compatibility(L_col)
    k_fibre = Bc.T @ element_basic_stiffness(sec_c, L_col, np.zeros(3), True, LOBATTO_RULE) @ Bc
    k_text = classic_element(EA_c, EI_c, L_col)
    report.append(f"element check (gross section, column element 1): force-based element vs textbook frame element, "
                  f"max relative difference {np.max(np.abs(k_fibre - k_text)) / np.max(np.abs(k_text)):.1e}")
    for label, sec_tag in (("column", SEC_C01), ("beam", SEC_B01)):
        _, E0, A0, y0 = section_fibres(sec_tag)
        report.append(f"section {label} (tag {sec_tag}): EA = {np.sum(E0 * A0):.6e} N, EI = {np.sum(E0 * A0 * y0 * y0):.6e} "
                      f"N.mm^2 (numpy, gross, initial tangents)")

    lam_e, _, _ = first_step_frame(True, LOBATTO_RULE)
    lam_i, u_i, n_it = first_step_frame(False, LOBATTO_RULE)
    report.append(f"inelastic pushover, first step: load factor OpenSees {push_i['lam'][0]:.6e}, section-state numpy "
                  f"{lam_i:.6e} (iterations {n_it}; relative difference {abs(push_i['lam'][0] / lam_i - 1.0):.2e}); "
                  f"node-3 displacement X: OpenSees {push_i['disp_x'][0]:.6e} mm, numpy "
                  f"{lam_i * u_i[frame_dof(NODE_TOP_L, 0)]:.6e} mm")
    report.append(f"inelastic pushover, first step, reference only: the uncracked frame gives {lam_e:.6e}")
    lam = push_i["lam"]
    res_shear = np.abs(push_i["shear"] + 2.0 * lam)
    res_axial = np.abs(push_i["axial"] - 2.0 * lam)
    report.append(f"inelastic pushover equilibrium over {len(lam)} steps: max |shear + 2 lambda| / max(2 lambda) = "
                  f"{np.max(res_shear) / np.max(2.0 * lam):.2e}; max |axial - 2 lambda| / max(2 lambda) = "
                  f"{np.max(res_axial) / np.max(2.0 * lam):.2e}")

    K0, M0 = assemble_linear()
    M_dyn = add_nodal_masses(M0)
    lam_np = finite_eigenvalues(K0, M_dyn, 4)
    periods_np = 2.0 * np.pi / np.sqrt(lam_np)
    report.append(f"periods of the four lowest modes, gross frame with lumped masses (numpy): "
                  f"{periods_np[0]:.6f} s, {periods_np[1]:.6f} s, {periods_np[2]:.6f} s, {periods_np[3]:.6f} s")
    report.append(f"periods of the four lowest modes at the first step (OpenSees, inelastic run): shortest "
                  f"{dyn_i['period_min'][0]:.6f} s, longest {dyn_i['period_max'][0]:.6f} s")
    omega_1, omega_2 = np.sqrt(lam_np[0]), np.sqrt(lam_np[1])
    coef = np.array([[1.0 / omega_1, omega_1], [1.0 / omega_2, omega_2]])
    alpha_np, beta_np = np.linalg.solve(coef, np.array([2.0 * DR, 2.0 * 0.6 * DR]))
    report.append(f"Rayleigh coefficients (numpy, gross frame): alpha_M = {alpha_np:.6e} 1/s, beta_K = {beta_np:.6e} s; "
                  f"OpenSees inelastic run: alpha_M = {ray_i[0]:.6e} 1/s, beta_K = {ray_i[1]:.6e} s")
    report.append("inelastic transient under the ramp and the scaled ground motion: not replicated (cracked frame, "
                  "nonlinear); its first periods above are the check of its start")
    zeta_1 = alpha_np / (2.0 * omega_1) + beta_np * omega_1 / 2.0
    zeta_2 = alpha_np / (2.0 * omega_2) + beta_np * omega_2 / 2.0
    report.append(f"modal damping ratios from the coefficients (gross stiffness): mode 1 {100 * zeta_1:.4f} %, "
                  f"mode 2 {100 * zeta_2:.4f} % (design 5 % and 3 %)")
    (output_dir / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report:
        print(line)


# ── 13. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))        # before any CreateODB (AGENT.md §12ac)
    gm_x = Path(__file__).parent / "ground_motions" / "Ground_Acceleration_X.txt"
    odb_pi, push_i = run_pushover(ODB_PUSH_I, output_dir)
    odb_di, dyn_i, ray_i = run_dynamic(ODB_DYN_I, gm_x)
    ops.printModel("-JSON", "-file", str(output_dir / "model_info.json"))   # model of the last analysis
    fit_i = bilinear_fit(np.abs(push_i["disp_x"]), np.abs(push_i["shear"]))
    fit_axial_i = bilinear_fit(np.abs(push_i["disp_y"]), np.abs(push_i["axial"]))
    post_process(output_dir, {ODB_PUSH_I: odb_pi, ODB_DYN_I: odb_di}, push_i, dyn_i, ray_i, fit_i, fit_axial_i)
    validate(output_dir, push_i, dyn_i, ray_i)
