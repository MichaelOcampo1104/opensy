# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D reinforced-concrete portal frame: two 3 m columns and a 7 m beam (500 x 300 mm), both bases fixed. The column
           depth Hc (350, 400, 450, 500, 550 and 600 mm), the column rebar diameter (28, 30 and 32 mm; the beam bars are 4 mm
           smaller) and the confinement enhancement ratio (1.25) are the source's sensitivity cases: 18 cases. Corotational
           nonlinearBeamColumn elements with 10 integration points, and fibre sections (Concrete01 for the core and the cover,
           Hysteretic reinforcement). Each case has two analyses, as in the source: a monotonic pushover to 675 mm, and a free
           vibration of node 3 from an initial displacement, velocity and acceleration under a ramp load, with Rayleigh damping
           (inelastic, as in the source).
UniqueID : SalarDelavar_Sensitivity_Cdepth_Confinement_Free_Vibration
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-26
Purpose  : Sensitivity of the pushover and free-vibration responses of the frame to the column depth, the column rebar diameter
           and the confinement ratio. For each of the 18 cases: the ductility ratio, over-strength factor, R and the stiffnesses
           of the bilinear fit of the pushover; the peak responses of the free vibration; its first two periods, its Rayleigh
           coefficients and the logarithmic-decrement damping. Then the source's post-processing of its last pushover (the one
           its plots use).
Ref      : py_ref/SENSITIVITY_CONFINEMENT_ENHANCEMENT_RATIO_&_REBAR_&_Cdepth_FREE_VIBRATION.py (source main), CONCRETE_SECTION_FUN_TWO.py
           (section), ANALYSIS_FUNCTION.py (its fallback ladder is replaced by SmartAnalyze), BILINEAR_CURVE.py, DAMPING_RATIO_FUN.py
           (logarithmic decrement), RAYLEIGH_DAMPING_FUN.py (Rayleigh coefficients), PLOT_2D.py (PLOT_2D_FRAME not run; vis_defo
           gives the deformed shape), COVER.png (figure). The source folder's PARALLEL_COMPUTING variant is not converted.
           Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO/SENSITIVITY_CONFINEMENT_ENHANCEMENT_RATIO_%26_REBAR_%26_Cdepth_FREE_VIBRATION
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import multiprocessing
import os
import shutil
import sys
from multiprocessing.connection import wait
from pathlib import Path

import numpy as np
import openseespy.opensees as ops
import opstool as opst

# models/<UniqueID>/model.py -> repository root is parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "standards"))
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
ODB_LAST_CASE = "last_case"                    # ODB of the last case's pushover, run again in the main process (LESSON 86)
NODE_BASE_L, NODE_BASE_R = 1, 2
NODE_TOP_L, NODE_TOP_R = 3, 4                  # NODE_TOP_R controls the pushover (DOF 1); NODE_TOP_L is the free-vibration node
NODE_COL_L_1, NODE_COL_L_2 = 5, 6              # left column, intermediate nodes (source)
NODE_COL_R_1, NODE_COL_R_2 = 7, 8              # right column, intermediate nodes (source)
NODE_BEAM_1, NODE_BEAM_2 = 9, 10               # beam, intermediate nodes (source)
SEC_C01, SEC_C02 = 10, 20                      # column fibre sections (source secTagC01, secTagC02)
SEC_B01, SEC_B02 = 30, 40                      # beam fibre sections (source secTagB01, secTagB02)
MAT_OFFSET_CORE, MAT_OFFSET_COVER, MAT_OFFSET_STEEL = 100, 200, 300   # source: sec + 100, + 200, + 300
TRANSF = 1                                     # corotational transformation (source)
TS_LINEAR, PAT_LINEAR = 1, 1                   # Linear time series and pattern (source tags 1)
NUM_INT_POINTS = 10                            # integration points per inelastic element (source numIntgrPts)
NUM_FIBERS = 40                                # fibres along the depth of each patch (source NUMFIBERS)
NUM_FIBERS_Z = 1                               # fibres across the width of each patch (source 5; Note 2)
PUSH_KEYS = ("lam", "disp_x", "disp_y", "rot", "shear", "axial", "moment", "ks", "ka", "ki", "drift_x", "drift_y")
DYN_KEYS = ("time", "disp_x", "disp_y", "rot", "vel_x", "vel_y", "acc_x", "acc_y", "shear", "axial", "moment",
            "ks", "ka", "ki", "drift_x")
SUMMARY_KEYS = ("hc", "dia", "kfc", "ro_col", "ro_be",
                "p_shear", "p_axial", "p_moment", "p_disp_x", "p_disp_y", "p_rot", "p_ka", "p_ks", "p_ki", "p_drift",
                "p_elastic", "p_plastic", "p_tangent", "p_ductility", "p_omega", "p_R",
                "d_shear", "d_axial", "d_moment", "d_disp_x", "d_disp_y", "d_rot", "d_vel_x", "d_vel_y", "d_acc_x",
                "d_acc_y", "d_ka", "d_ks", "d_ki", "d_drift", "d_period_1", "d_period_2", "d_alpha", "d_beta", "d_damping")


def case_tag(hc: float, dia_col: float, kfc: float) -> str:
    """Tag of one case of the grid, e.g. h350_d28_k125 for a column depth of 350 mm, 28 mm column rebar and Kfc 1.25. The
    tag names the case result file and the two ODBs (push_ and dyn_ prefixes). It is kept short for the 260-character path
    limit on Windows."""
    return f"h{round(hc / mm):03d}_d{round(dia_col / mm):02d}_k{round(kfc * 100):03d}"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Concrete and reinforcing steel (source CONFINED_CONCRETE_SECTION; steel values of the source's STEEL_KIND 2)
fc = 25.0 * MPa                 # unconfined concrete compressive strength (source fc)
FY_STEEL = 4000.0 * MPa         # yield stress (source fy), as written
ES_STEEL = 2.0e5 * MPa          # modulus (source Es)
EY_STEEL = FY_STEEL / ES_STEEL  # yield strain (source ey)
FU_STEEL = 1.1818 * FY_STEEL    # ultimate stress (source fu)
ESU_STEEL = EY_STEEL * 75.2     # ultimate strain (source esu)
PINCH_X, PINCH_Y = 0.8, 0.5     # Hysteretic pinching factors (source)
DAMAGE_1, DAMAGE_2 = 0.0, 0.0   # Hysteretic damage factors (source)
BETA_HYS = 0.1                  # Hysteretic stiffness degradation (source beta)

# Column section (source Bc, coverC; the depth Hc is the sensitivity variable): width 500 mm
B_COL = 500.0 * mm
COVER_COL = 50.0 * mm
# Beam section (source Bb, Hb, coverB): width 500 mm and depth 300 mm
B_BEAM = 500.0 * mm
H_BEAM = 300.0 * mm
COVER_BEAM = 50.0 * mm
LENGTH_COL = 3000.0 * mm        # source LENGTH_COL
LENGTH_BEAM = 7000.0 * mm       # source LENGTH_BM

# Masses. The source's MASS = 12000 is labelled [kg] and the element masses are Bc*Hc*0.000025 and Bb*Hb*0.000025. They are used
# as written (N.s^2/mm for the nodes, and per unit area for the elements), as in the earlier sub-models of this folder (LESSON 71).
# The other reading (kg as N.s^2/mm = 1000 kg, and the density of concrete) is reported in validation.txt.
MASS_NODE = 12000.0 * N * sec**2 / mm               # source MASS, nodes 3 and 4 in X and Y (as written)
MASS_PER_AREA_AS_WRITTEN = 0.000025 * N * sec**2 / mm**4   # source B*H*0.000025: element mass per unit length = B*H times this
RHO_CONCRETE = 2.5e-9 * N * sec**2 / mm**4          # 2500 kg/m^3, for the other reading only

# The grid (source HCC, DIAc and Kfc; the source loops over HCC outside, then DIAc, then Kfc)
HCC_VALUES = (350.0 * mm, 400.0 * mm, 450.0 * mm, 500.0 * mm, 550.0 * mm, 600.0 * mm)   # source HCC: column depth
DIA_COL_VALUES = (28.0 * mm, 30.0 * mm, 32.0 * mm)                                     # source DIAc: column rebar diameter
KFC_VALUES = (1.25,)                                                                    # source Kfc: confinement ratio
DIA_BEAM_REDUCTION = 4.0 * mm   # source DIAb = DIAc - 4: beam rebar diameter
# Confinement offsets of the other sections (source Kfc - 0.05, Kfc - 0.10 and Kfc - 0.15)
KFC_OFFSET_COL_MID = 0.05       # secTagC02, the middle column (source)
KFC_OFFSET_BEAM = 0.10          # secTagB01, the beam (source)
KFC_OFFSET_BEAM_MID = 0.15      # secTagB02, the middle beam (source)
CASES = tuple((hc, dia, kfc) for hc in HCC_VALUES for dia in DIA_COL_VALUES for kfc in KFC_VALUES)   # source loop order
LAST_CASE = CASES[-1]           # the source's last call: its plots use its pushover (LESSON 86)

# Free vibration (source DYNAMIC branch, FV = 'X', IU = IV = IA = True)
U0 = 0.031 * mm                 # initial displacement of node 3 (source u0)
V0 = 0.00015 * mm / sec         # initial velocity (source v0)
A0 = 0.000065 * mm / sec**2     # initial acceleration (source a0)
DR = 0.05                       # damping ratio of mode 1; mode 2 takes 0.6 DR (source DR and 0.6*DR)
DURATION = 20.0 * sec           # total duration of the free vibration (source duration)
DT = 0.001 * sec                # time step (source dt)
NEWMARK_GAMMA, NEWMARK_BETA = 0.5, 0.25                                   # Newmark (source)
ODB_EVERY_DYNAMIC = 40          # ODB fetch every 40 transient steps (about 500 fetches, AGENT.md §3d)

# Pushover (source)
DMAX = 675.0 * mm               # maximum displacement (source DMAX)
DINCR = 0.05 * mm               # displacement increment (source DINCR): 13500 steps
MAX_ITERATIONS = 5000           # convergence iterations (source MAX_ITERATIONS)
MAX_TOLERANCE = 1.0e-6          # convergence tolerance (source MAX_TOLERANCE)
ODB_EVERY_PUSHOVER = 20         # ODB fetch every 20 pushover steps (AGENT.md §3d)
GRID_WORKERS = 3                # the cases of the grid run in separate processes, three at a time (Note 3)


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


def bar_area(dia: float) -> float:
    """Area of one reinforcing bar (source AsC and AsB = pi D^2 / 4)."""
    return np.pi * dia**2 / 4.0


def rebar_ratios(hc: float, dia_col: float) -> tuple:
    """Column and beam reinforcement ratios in percent, as the source writes them: RO_COL = 100 * 8 A_bar,col / (Hc Bc) and
    RO_BE = 100 * 6 A_bar,beam / (Hb Bb). The column section has six bars and the beam eight (Note 6).

    Returns:
        (RO_COL, RO_BE) in percent for the column depth hc and the column rebar diameter dia_col.
    """
    ro_col = 100.0 * 8.0 * bar_area(dia_col) / (hc * B_COL)
    ro_be = 100.0 * 6.0 * bar_area(dia_col - DIA_BEAM_REDUCTION) / (H_BEAM * B_BEAM)
    return ro_col, ro_be


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
def section_spec(hc: float, dia_col: float, kfc: float) -> dict:
    """Confined fibre sections of the source for the column depth hc, the column rebar diameter dia_col and the ratio kfc,
    as its CONFINED_CONCRETE_SECTION calls give them: tag -> (depth h, width b, cover, bar area, confinement ratio, column
    flag). The columns take kfc and kfc - 0.05, the beams kfc - 0.10 and kfc - 0.15. The beam bars are dia_col - 4 mm."""
    a_col = bar_area(dia_col)
    a_beam = bar_area(dia_col - DIA_BEAM_REDUCTION)
    return {
        SEC_C01: (hc, B_COL, COVER_COL, a_col, kfc, True),
        SEC_C02: (hc, B_COL, COVER_COL, a_col, kfc - KFC_OFFSET_COL_MID, True),
        SEC_B01: (H_BEAM, B_BEAM, COVER_BEAM, a_beam, kfc - KFC_OFFSET_BEAM, False),
        SEC_B02: (H_BEAM, B_BEAM, COVER_BEAM, a_beam, kfc - KFC_OFFSET_BEAM_MID, False),
    }


def define_fiber_section(sec_tag: int, h: float, b: float, cover: float, area_bar: float, kc: float, col: bool) -> None:
    """Confined fibre section of the source (CONFINED_CONCRETE_SECTION). Each section has its own materials, as in the
    source: core (sec + 100, Concrete01 with kc), cover (sec + 200, Concrete01, unconfined) and steel (sec + 300,
    Hysteretic). Column (col = True): three bars on each face, six in all. Beam (col = False): a middle layer of two bars
    as well, eight in all.
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


def define_sections(hc: float, dia_col: float, kfc: float) -> None:
    """The four fibre sections of the source for the column depth hc, the column rebar diameter and the ratio kfc."""
    for sec_tag, (h, b, cover, area_bar, kc_sec, col) in section_spec(hc, dia_col, kfc).items():
        define_fiber_section(sec_tag, h, b, cover, area_bar, kc_sec, col)


# ── 7. ELEMENTS ──────────────────────────────────────────────────────────────
# (tag, start node, end node, section, member), as in the source's element list; the mass follows the member
ELEMENT_TOPOLOGY = (
    (1, NODE_BASE_L, NODE_COL_L_1, SEC_C01, "col"),
    (2, NODE_COL_L_1, NODE_COL_L_2, SEC_C02, "col"),
    (3, NODE_COL_L_2, NODE_TOP_L, SEC_C01, "col"),
    (4, NODE_BASE_R, NODE_COL_R_1, SEC_C01, "col"),
    (5, NODE_COL_R_1, NODE_COL_R_2, SEC_C02, "col"),
    (6, NODE_COL_R_2, NODE_TOP_R, SEC_C01, "col"),
    (7, NODE_TOP_L, NODE_BEAM_1, SEC_B01, "beam"),
    (8, NODE_BEAM_1, NODE_BEAM_2, SEC_B02, "beam"),
    (9, NODE_BEAM_2, NODE_TOP_R, SEC_B01, "beam"),
)


def element_masses(hc: float, reading: str = "as_written") -> tuple:
    """Element mass per unit length of a column of depth hc and of the beam, in N.s^2/mm^2.

    Args:
        hc: Column depth.
        reading: 'as_written' is the source's B*H*0.000025 (LESSON 71). 'si' is the density of concrete (2500 kg/m^3)
            times B*H, for the other reading only.

    Returns:
        (column, beam) mass per unit length.
    """
    if reading == "as_written":
        return B_COL * hc * MASS_PER_AREA_AS_WRITTEN, B_BEAM * H_BEAM * MASS_PER_AREA_AS_WRITTEN
    return B_COL * hc * RHO_CONCRETE, B_BEAM * H_BEAM * RHO_CONCRETE


def nodal_mass(reading: str = "as_written") -> float:
    """Nodal mass at nodes 3 and 4 in X and Y: the source's MASS as written, or the same value read as kg (divided by 1000,
    AGENT.md §12j), for the other reading only."""
    if reading == "as_written":
        return MASS_NODE
    return MASS_NODE / 1000.0


def define_elements(hc: float) -> None:
    """The nine elements of the source: corotational nonlinearBeamColumn with 10 integration points, with the element
    masses of the source for the column depth hc."""
    ops.geomTransf("Corotational", TRANSF)
    mass_col, mass_beam = element_masses(hc)
    for tag, ni, nj, sec, member in ELEMENT_TOPOLOGY:
        mass = mass_col if member == "col" else mass_beam
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


def define_nodal_masses(reading: str = "as_written") -> None:
    """Nodal masses at nodes 3 and 4 in X and Y (source ops.mass(3, MASS, MASS, 0.0) and ops.mass(4, MASS, MASS, 0.0)).
    Free-vibration runs only, as in the source."""
    mass = nodal_mass(reading)
    ops.mass(NODE_TOP_L, mass, mass, 0.0)
    ops.mass(NODE_TOP_R, mass, mass, 0.0)


def build_model(hc: float, dia_col: float, kfc: float, odb_tag, output_dir: Path = None, dynamic: bool = False):
    """Build the frame for one analysis. The V1 and V2 stages are written when output_dir is given. The nodal masses are
    defined for the free-vibration run only.

    Returns:
        The CreateODB instance.
    """
    init_model()
    define_nodes_and_supports()
    define_sections(hc, dia_col, kfc)
    if output_dir is not None:
        vis_nodes(output_dir)                      # V1: nodes and supports
    define_elements(hc)
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
    """Horizontal load of the source's free-vibration run (FV = 'X'): 1 N at nodes 3 and 4 in a Linear pattern. A Linear time
    series grows with time, so this load is t N at time t, as in the source."""
    ops.timeSeries("Linear", TS_LINEAR)
    ops.pattern("Plain", PAT_LINEAR, TS_LINEAR)
    ops.load(NODE_TOP_L, 1.0 * N, 0.0, 0.0)
    ops.load(NODE_TOP_R, 1.0 * N, 0.0, 0.0)


def define_initial_conditions() -> None:
    """Initial displacement, velocity and acceleration of node 3 in X (source setNodeDisp, setNodeVel and setNodeAccel, with
    IU = IV = IA = True and the committed state)."""
    ops.setNodeDisp(NODE_TOP_L, 1, U0, "-commit")
    ops.setNodeVel(NODE_TOP_L, 1, V0, "-commit")
    ops.setNodeAccel(NODE_TOP_L, 1, A0, "-commit")


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


def run_pushover(hc: float, dia_col: float, kfc: float, odb_tag: str, output_dir: Path = None) -> tuple:
    """Horizontal displacement control of node 4 (DOF 1) to DMAX through SmartAnalyze (source PD_ANALYSIS, PUSHOVER).

    Returns:
        (odb, history): the ODB and the per-step arrays. The base reactions keep the source's sign (no minus).
    """
    odb = build_model(hc, dia_col, kfc, odb_tag, output_dir)
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
        algoTypes=[10, 41, 40, 20, 50, 60],        # Newton first, then the fallback ladder of the source's solver (Note 4)
        printPer=0,
        testPrintFlag=0,
    )
    history = {key: [] for key in PUSH_KEYS}
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


def run_dynamic(hc: float, dia_col: float, kfc: float, odb_tag: str, output_dir: Path = None) -> tuple:
    """Free vibration of the source (PD_ANALYSIS, DYNAMIC): the ramp load and the initial displacement, velocity and
    acceleration of node 3 in X, with Rayleigh damping from the two lowest modes, through Newmark (0.5, 0.25) and SmartAnalyze,
    for DURATION in steps of DT.

    Returns:
        (odb, history, rayleigh): rayleigh = (alpha_m, beta_k, period_1, period_2) from the frame at its initial state.
    """
    odb = build_model(hc, dia_col, kfc, odb_tag, output_dir, dynamic=True)
    define_ramp_load()
    define_initial_conditions()
    if output_dir is not None:
        vis_loads(output_dir)                      # V3: load vectors
        vis_pre_analysis(output_dir)               # V4: last check before the solver
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
    history = {key: [] for key in DYN_KEYS}
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
        history["time"].append(ops.getTime())
        history["disp_x"].append(dx)
        history["disp_y"].append(dy)
        history["rot"].append(rot)
        history["vel_x"].append(ops.nodeVel(NODE_TOP_L, 1))
        history["vel_y"].append(ops.nodeVel(NODE_TOP_L, 2))
        history["acc_x"].append(ops.nodeAccel(NODE_TOP_L, 1))
        history["acc_y"].append(ops.nodeAccel(NODE_TOP_L, 2))
        history["shear"].append(shear)
        history["axial"].append(axial)
        history["moment"].append(moment)
        history["drift_x"].append(100.0 * dx / LENGTH_COL)
    analysis.close()
    return odb, {key: np.array(value, dtype=float) for key, value in history.items()}, rayleigh


def case_result_path(output_dir: Path, tag: str) -> Path:
    """File that holds the saved result of one case of the grid."""
    return output_dir / "cases" / f"{tag}.npz"


def peak(values: np.ndarray) -> float:
    """Largest absolute value of a response array, ignoring non-finite entries (the source's np.max(np.abs(...)))."""
    values = np.abs(np.asarray(values, dtype=float))
    finite = values[np.isfinite(values)]
    return float(finite.max()) if finite.size else float("nan")


def damping_ratio_source(signal) -> float:
    """Damping ratio in percent from the logarithmic decrement of the local maxima of the signal (source DAMPING_RATIO_FUN).
    The source solves x^2 - 1 + (2 pi x / mean(delta))^2 = 0 with fsolve from x0 = 1. Its positive root is
    x = |dbar| / sqrt(dbar^2 + 4 pi^2), used here directly. The source has no check of the number of peaks or of their sign:
    with fewer than two peaks, or a non-positive peak, the port returns NaN (Note 10). For a free decay this is the source's
    estimate of the damping; it is not a modal ratio by itself (the Rayleigh ratios are checked in validation.txt)."""
    x = np.asarray(signal, dtype=float)
    peaks = np.array([x[i] for i in range(1, len(x) - 1) if x[i] > x[i - 1] and x[i] > x[i + 1]])
    if len(peaks) < 2:
        return float("nan")
    with np.errstate(divide="ignore", invalid="ignore"):
        delta = np.log(peaks[:-1] / peaks[1:])
        dbar = float(np.mean(delta))
        return 100.0 * abs(dbar) / np.sqrt(dbar**2 + 4.0 * np.pi**2)


def case_summary(hc: float, dia_col: float, kfc: float, push: dict, dyn: dict, rayleigh: tuple, damping: float) -> dict:
    """The source's results of one case: the reinforcement ratios (its formulas, in percent), the pushover's largest absolute
    values (its MAX lists) and the bilinear fit of the base shear with R = Omega_0 mu, and the free vibration's largest
    absolute values, its periods, Rayleigh coefficients and logarithmic-decrement damping (source PD_ANALYSIS)."""
    fit = bilinear_fit(np.abs(push["disp_x"]), np.abs(push["shear"]))
    ro_col, ro_be = rebar_ratios(hc, dia_col)
    alpha_m, beta_k, period_1, period_2 = rayleigh
    return {
        "hc": hc / mm, "dia": dia_col / mm, "kfc": kfc, "ro_col": ro_col, "ro_be": ro_be,
        "p_shear": peak(push["shear"]), "p_axial": peak(push["axial"]), "p_moment": peak(push["moment"]),
        "p_disp_x": peak(push["disp_x"]), "p_disp_y": peak(push["disp_y"]), "p_rot": peak(push["rot"]),
        "p_ka": peak(push["ka"]), "p_ks": peak(push["ks"]), "p_ki": peak(push["ki"]), "p_drift": peak(push["drift_x"]),
        "p_elastic": fit[2], "p_plastic": fit[3], "p_tangent": fit[4], "p_ductility": fit[5], "p_omega": fit[6],
        "p_R": fit[6] * fit[5],
        "d_shear": peak(dyn["shear"]), "d_axial": peak(dyn["axial"]), "d_moment": peak(dyn["moment"]),
        "d_disp_x": peak(dyn["disp_x"]), "d_disp_y": peak(dyn["disp_y"]), "d_rot": peak(dyn["rot"]),
        "d_vel_x": peak(dyn["vel_x"]), "d_vel_y": peak(dyn["vel_y"]),
        "d_acc_x": peak(dyn["acc_x"]), "d_acc_y": peak(dyn["acc_y"]),
        "d_ka": peak(dyn["ka"]), "d_ks": peak(dyn["ks"]), "d_ki": peak(dyn["ki"]), "d_drift": peak(dyn["drift_x"]),
        "d_period_1": period_1, "d_period_2": period_2, "d_alpha": alpha_m, "d_beta": beta_k, "d_damping": damping,
    }


def case_worker(job: tuple) -> None:
    """One case of the grid (pushover, then free vibration), run in its own process (see run_grid). job = (hc, dia_col, kfc,
    tag, output_dir). Each ODB is saved after its analysis, not inside its step loop. The case summary and the step arrays
    are saved to output/cases/<tag>.npz only when both analyses have completed all their steps."""
    hc, dia_col, kfc, tag, output_dir = job
    output_dir = Path(output_dir)
    opst.post.set_odb_path(str(output_dir))        # before any CreateODB (AGENT.md §12ac), in this process
    odb_p, push = run_pushover(hc, dia_col, kfc, "push_" + tag, None)
    odb_p.save_response()
    steps_push = round(DMAX / DINCR)
    if len(push["lam"]) != steps_push:
        raise RuntimeError(f"pushover {tag} stopped after {len(push['lam'])} of {steps_push} steps")
    odb_d, dyn, rayleigh = run_dynamic(hc, dia_col, kfc, "dyn_" + tag, None)
    odb_d.save_response()
    steps_dyn = round(DURATION / DT)
    if len(dyn["time"]) != steps_dyn:
        raise RuntimeError(f"free vibration {tag} stopped after {len(dyn['time'])} of {steps_dyn} steps")
    damping = damping_ratio_source(dyn["disp_x"])
    summary = case_summary(hc, dia_col, kfc, push, dyn, rayleigh, damping)
    arrays = {"push_" + key: value for key, value in push.items()}
    arrays.update({"dyn_" + key: value for key, value in dyn.items()})
    np.savez(case_result_path(output_dir, tag), **summary, **arrays)


def clear_case_outputs(output_dir: Path, tag: str) -> None:
    """Remove the ODB files of a case that an interrupted run started but did not complete (LESSON 88)."""
    for path in output_dir.glob(f"*{tag}*"):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def run_grid(output_dir: Path) -> None:
    """Run the cases of the grid that have no saved result yet, GRID_WORKERS at a time, each case in its own process
    (LESSON 85): each process starts from its own working folder under output/.work, because opstool's set_odb_path removes
    the '.opstool.output' folder of the working folder. Each completed case is saved to output/cases at once, so an
    interrupted run continues with the cases that are missing (LESSON 88).

    Raises:
        RuntimeError: if a case did not complete in its process.
    """
    (output_dir / "cases").mkdir(parents=True, exist_ok=True)
    queue = []
    for hc, dia_col, kfc in CASES:
        tag = case_tag(hc, dia_col, kfc)
        if case_result_path(output_dir, tag).exists():
            continue
        clear_case_outputs(output_dir, tag)
        queue.append((hc, dia_col, kfc, tag, str(output_dir)))
    ctx = multiprocessing.get_context("spawn")
    work_root = output_dir / ".work"
    original = os.getcwd()
    running, failed = {}, []
    try:
        while queue or running:
            while queue and len(running) < GRID_WORKERS:
                hc, dia_col, kfc, tag, out = queue.pop(0)
                work = work_root / tag
                work.mkdir(parents=True, exist_ok=True)
                os.chdir(work)                    # the new process inherits this working folder when it starts
                proc = ctx.Process(target=case_worker, args=((hc, dia_col, kfc, tag, out),))
                proc.start()
                os.chdir(original)
                running[proc.sentinel] = (tag, proc)
                print(f"  started {tag}", flush=True)
            for sentinel in wait(list(running)):
                tag, proc = running.pop(sentinel)
                proc.join()
                print(f"  finished {tag} (exit code {proc.exitcode})", flush=True)
                if proc.exitcode != 0:
                    failed.append(tag)
    finally:
        os.chdir(original)
        shutil.rmtree(work_root, ignore_errors=True)
    if failed:
        raise RuntimeError(f"cases {', '.join(failed)} failed in their processes (see the messages above)")


def load_case_rows(output_dir: Path) -> list:
    """The saved result of every case of the grid, in the source's loop order. Each row holds the summary (SUMMARY_KEYS),
    the pushover arrays under 'push' and the free-vibration arrays under 'dyn'."""
    rows = []
    for hc, dia_col, kfc in CASES:
        with np.load(case_result_path(output_dir, case_tag(hc, dia_col, kfc))) as data:
            row = {key: float(data[key]) for key in SUMMARY_KEYS}
            row["push"] = {key: np.array(data["push_" + key]) for key in PUSH_KEYS}
            row["dyn"] = {key: np.array(data["dyn_" + key]) for key in DYN_KEYS}
        rows.append(row)
    return rows


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


def save_csv(output_dir: Path, name: str, columns: dict) -> None:
    """Write named columns to CSV (N, mm, s, rad)."""
    table = np.column_stack([columns[key] for key in columns])
    np.savetxt(output_dir / name, table, delimiter=",", header=",".join(columns), comments="")


def pushover_columns(push: dict) -> dict:
    """Pushover columns of the last case, named as in the first sub-model's results (the source does not export its
    pushover)."""
    return {"load_factor": push["lam"], "DISP_X": push["disp_x"], "DISP_Y": push["disp_y"],
            "ROTATION": push["rot"], "AXIAL_FORCE": push["axial"], "SHEAR_FORCE": push["shear"],
            "MOMENT": push["moment"], "LATERAL_ST_X": push["ks"], "LATERAL_ST_Y": push["ka"],
            "ROTATIONAL_ST": push["ki"], "DRIFT_X": push["drift_x"], "DRIFT_Y": push["drift_y"]}


def dynamic_columns(dyn: dict) -> dict:
    """Free-vibration columns of the last case (node 3, source names where the source has them)."""
    return {"TIME": dyn["time"], "DISP_X": dyn["disp_x"], "DISP_Y": dyn["disp_y"], "ROTATION": dyn["rot"],
            "VELOCITY_X": dyn["vel_x"], "VELOCITY_Y": dyn["vel_y"], "ACCELERATION_X": dyn["acc_x"],
            "ACCELERATION_Y": dyn["acc_y"], "SHEAR_FORCE": dyn["shear"], "AXIAL_FORCE": dyn["axial"],
            "MOMENT": dyn["moment"], "LATERAL_ST_X": dyn["ks"], "LATERAL_ST_Y": dyn["ka"],
            "ROTATIONAL_ST": dyn["ki"], "DRIFT_X": dyn["drift_x"]}


# The source's DATA_TOTAL table of the pushover (its Excel export), with the column depth Hc added (the source's table omits it):
# (column name, summary key)
PUSH_TABLE = (
    ("Hc", "hc"), ("DIAc", "dia"), ("Kfc", "kfc"), ("RO_COL", "ro_col"), ("RO_BE", "ro_be"),
    ("DISP_X", "p_disp_x"), ("DISP_Y", "p_disp_y"), ("ROTATION", "p_rot"), ("AXIAL_FORCE", "p_axial"),
    ("SHEAR_FORCE", "p_shear"), ("MOMENT_WO", "p_moment"),
    ("AXIAL_RIGIDITY", "p_axial"),                 # the source's |max axial force|, the same as AXIAL_FORCE (Note 9)
    ("ROTATIONAL_ST", "p_ki"), ("LATERAL_ST_Y", "p_ka"), ("LATERAL_ST_X", "p_ks"),
    ("Elastic_ST_MAX", "p_elastic"), ("Plastic_ST_MAX", "p_plastic"), ("Tangent_ST_MAX", "p_tangent"),
    ("Ductility_Rito_MAX", "p_ductility"), ("Over_Strength_Factor_MAX", "p_omega"),
    ("Structural_Behavior_Coefficient_MAX", "p_R"),
)

# The free-vibration maxima of the source (its *_MAX_d lists), periods, Rayleigh coefficients and damping, which the source
# plots but does not export: (column name, summary key)
DYN_TABLE = (
    ("Hc", "hc"), ("DIAc", "dia"), ("Kfc", "kfc"), ("RO_COL", "ro_col"), ("RO_BE", "ro_be"),
    ("SHEAR_FORCE", "d_shear"), ("AXIAL_FORCE", "d_axial"), ("MOMENT_WO", "d_moment"),
    ("DISP_X", "d_disp_x"), ("DISP_Y", "d_disp_y"), ("ROTATION", "d_rot"),
    ("VELOCITY_X", "d_vel_x"), ("VELOCITY_Y", "d_vel_y"), ("ACCELERATION_X", "d_acc_x"), ("ACCELERATION_Y", "d_acc_y"),
    ("ROTATIONAL_ST", "d_ki"), ("LATERAL_ST_Y", "d_ka"), ("LATERAL_ST_X", "d_ks"), ("DRIFT", "d_drift"),
    ("PERIOD_01", "d_period_1"), ("PERIOD_02", "d_period_2"), ("DAMPING_RATIO_PCT", "d_damping"),
)


def grid_table(rows: list, table: tuple) -> dict:
    """One column per (name, key) of the table, over the cases in the source's order."""
    return {name: np.array([row[key] for row in rows], dtype=float) for name, key in table}


def write_results(output_dir: Path, rows: list, fit_x: tuple, fit_y: tuple) -> None:
    """Text summary: the bilinear fits of the last pushover (the source's formulas, in X and in Y), the ranges of the grid and
    the free-vibration periods and damping."""
    X, Y, k_el, k_pl, k_tan, mu, omega = fit_x
    mu_y, omega_y = fit_y[5], fit_y[6]
    r_y = omega_y * (2.0 * mu_y - 1.0) ** 0.5 / mu_y ** 0.5          # the source's Y-direction R (its R_mu)
    ductility = [row["p_ductility"] for row in rows]
    behaviour = [row["p_R"] for row in rows]
    period_1 = [row["d_period_1"] for row in rows]
    damping = [row["d_damping"] for row in rows]
    last = rows[-1]
    lines = [
        f"cases: {len(rows)} = {len(HCC_VALUES)} column depths x {len(DIA_COL_VALUES)} column rebar diameters x "
        f"{len(KFC_VALUES)} confinement ratio; each pushover to {DMAX / mm:.0f} mm in {round(DMAX / DINCR)} steps (SmartAnalyze); "
        f"each free vibration for {DURATION / sec:.0f} s in {round(DURATION / DT)} steps of {DT / sec:.3f} s",
        f"last case (the source's last call, LESSON 86): column depth {LAST_CASE[0] / mm:.0f} mm, column rebar "
        f"{LAST_CASE[1] / mm:.0f} mm, confinement ratio {LAST_CASE[2]:.2f}; its ODB is {ODB_LAST_CASE}",
        f"last case, base shear in X: ductility mu = {mu:.6f}; over-strength Omega_0 = {omega:.4f}; R = Omega_0 mu = {omega * mu:.4f}",
        f"  bilinear fit in X: X = {X[1]:.4f} mm, {X[2]:.4f} mm; Y = {Y[1]:.4f} N, {Y[2]:.4f} N; elastic stiffness "
        f"{k_el:.4f} N/mm; plastic {k_pl:.4f} N/mm; tangent {k_tan:.4f} N/mm",
        f"last case, base axial force in Y (the source's Y formulas): mu = {mu_y:.6f}; Omega_0 = {omega_y:.4f}; R = {r_y:.4f}",
        f"grid: ductility mu from {min(ductility):.4f} to {max(ductility):.4f}; R from {min(behaviour):.4f} to {max(behaviour):.4f}",
        f"free vibration, first period from {min(period_1):.4f} s to {max(period_1):.4f} s (as-written masses, gross "
        f"sections at t = 0); log-decrement damping from {np.nanmin(damping):.3f} % to {np.nanmax(damping):.3f} %",
        f"last case free vibration: first period {last['d_period_1']:.4f} s, second {last['d_period_2']:.4f} s, "
        f"log-decrement damping {last['d_damping']:.4f} %, peak node-3 displacement X {last['d_disp_x']:.4f} mm",
    ]
    (output_dir / "sensitivity_results.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_last_case(output_dir: Path, push: dict, fit_x: tuple, fit_y: tuple) -> None:
    """The source's line and scatter plots of its last pushover (PLOT_LINE, PLOT_SCATTER and BC.PLOT_2D), saved as PNG files
    in place of the source's plt.show() calls."""
    import matplotlib.pyplot as plt

    colour = COLORS["primary"]
    fig, axes = plt.subplots(2, 2, figsize=(14, 11), dpi=150)
    panels = (
        (push["moment"], push["axial"], "P-M Interaction", "Bending Moment [N.mm]", "Axial Force [N]"),
        (push["disp_x"], push["shear"], "Shear Force-Displacement Diagram", "Displacement in X [mm]", "Shear Force [N]"),
        (push["disp_y"], push["axial"], "Axial Force-Displacement Diagram", "Displacement in Y [mm]", "Axial Force [N]"),
        (push["rot"], push["moment"], "Moment-Rotation Diagram", "Rotation [rad]", "Moment [N.mm]"),
    )
    for ax, (x, y, title, xlabel, ylabel) in zip(axes.ravel(), panels):
        ax.plot(x, y, color=colour, lw=1.6)
        _style_ax(ax, xlabel, ylabel, title)
    fig.tight_layout()
    fig.savefig(output_dir / "last_case_curves.png")
    plt.close(fig)

    step = np.arange(len(push["lam"]))
    fig, axes = plt.subplots(2, 3, figsize=(18, 10), dpi=150)
    series = (("Axial Force [N]", push["axial"]), ("Shear Force [N]", push["shear"]),
              ("Moment [N.mm]", push["moment"]), ("Displacement - X [mm]", push["disp_x"]),
              ("Displacement - Y [mm]", push["disp_y"]), ("Rotation [rad]", push["rot"]))
    for ax, (ylabel, y) in zip(axes.ravel(), series):
        ax.plot(step, y, color=colour, lw=1.2)
        _style_ax(ax, "Step", ylabel, f"{ylabel} during the analysis")
    fig.tight_layout()
    fig.savefig(output_dir / "last_case_steps.png")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), dpi=150)
    for ax, (lateral, label) in zip(axes, ((push["ks"], "X"), (push["ka"], "Y"))):
        ax.scatter(push["ki"], lateral, s=4, color="black")
        _style_ax(ax, "Rotational Stiffness [N.mm/rad]", f"Lateral Stiffness in {label} Dir. [N/mm]",
                  f"Rotational - lateral stiffness ({label} Dir)")
        ax.set_xscale("log")
        ax.set_yscale("log")
    fig.tight_layout()
    fig.savefig(output_dir / "last_case_stiffness.png")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), dpi=150)
    panels = (
        (fit_x, push["disp_x"], push["shear"], "Last case: base shear - X", "Displacement in X [mm]", "Base shear [N]"),
        (fit_y, push["disp_y"], push["axial"], "Last case: base axial force - Y", "Displacement in Y [mm]",
         "Base axial force [N]"),
    )
    for ax, (fit, x, y, title, xlabel, ylabel) in zip(axes, panels):
        ax.plot(np.abs(x) / mm, np.abs(y) / N, color=colour, lw=1.6, label="curve")
        ax.plot(fit[0] / mm, fit[1] / N, color="black", lw=1.0, ls=":", label="bilinear fit")
        _style_ax(ax, xlabel, ylabel, title)
        ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "last_case_bilinear.png")
    plt.close(fig)


def plot_dynamic_last_case(output_dir: Path, dyn: dict) -> None:
    """Node-3 displacement and base shear of the last case's free vibration against time (a figure the source does not draw;
    it shows the decay that the damping estimate uses)."""
    import matplotlib.pyplot as plt

    colour = COLORS["primary"]
    fig, axes = plt.subplots(2, 1, figsize=(14, 9), dpi=150, sharex=True)
    _style_ax(axes[0], "Time [s]", "Displacement - X [mm]", "Free vibration of the last case: node 3")
    axes[0].plot(dyn["time"], dyn["disp_x"], color=colour, lw=1.0)
    _style_ax(axes[1], "Time [s]", "Base shear [N]", "Free vibration of the last case: base shear")
    axes[1].plot(dyn["time"], dyn["shear"], color=COLORS["secondary"], lw=1.0)
    fig.tight_layout()
    fig.savefig(output_dir / "dynamic_last_case.png")
    plt.close(fig)


# The source's PLOT_3D figures 0 to 36 (their Z data): a key of the case summary, or 'ratio:a/b' for a ratio of two keys
SURFACES = (
    ("kfc", "Confinement Enhancement Ratio"),
    ("p_shear", "Structure Shear Reaction in X Dir. [N] from Pushover Analysis"),
    ("d_shear", "Structure Shear Reaction in X Dir. [N] from Dynamic Analysis"),
    ("ratio:d_shear/p_shear", "Structure Shear Reaction Ratio in X Dir."),
    ("p_axial", "Structure Axial Reaction in Y Dir. [N] from Pushover Analysis"),
    ("d_axial", "Structure Axial Reaction in Y Dir. [N] from Dynamic Analysis"),
    ("ratio:d_axial/p_axial", "Structure Axial Reaction Ratio in Y Dir."),
    ("p_moment", "Structure Moment Reaction in Y Dir. [N.mm] from Pushover Analysis"),
    ("d_moment", "Structure Moment Reaction in Y Dir. [N.mm] from Dynamic Analysis"),
    ("ratio:d_moment/p_moment", "Structure Moment Reaction Ratio in Y Dir."),
    ("p_disp_x", "Structure Displacement in X Dir. [mm] from Pushover Analysis"),
    ("d_disp_x", "Structure Displacement in X Dir. [mm] from Dynamic Analysis"),
    ("ratio:d_disp_x/p_disp_x", "Structure Displacement Ratio in X Dir."),
    ("p_disp_y", "Structure Displacement in Y Dir. [mm] from Pushover Analysis"),
    ("d_disp_y", "Structure Displacement in Y Dir. [mm] from Dynamic Analysis"),
    ("ratio:d_disp_y/p_disp_y", "Structure Displacement Ratio in Y Dir."),
    ("p_ks", "Lateral Stiffness in X Dir. [N/mm] from Pushover Analysis"),
    ("d_ks", "Lateral Stiffness in X Dir. [N/mm] from Dynamic Analysis"),
    ("ratio:d_ks/p_ks", "Lateral Stiffness Ratio in X Dir."),
    ("p_ka", "Lateral Stiffness in Y Dir. [N/mm] from Pushover Analysis"),
    ("d_ka", "Lateral Stiffness in Y Dir. [N/mm] from Dynamic Analysis"),
    ("ratio:d_ka/p_ka", "Lateral Stiffness Ratio in Y Dir."),
    ("p_elastic", "Structure Elastic Stiffness [N/mm]"),
    ("p_plastic", "Structure Plastic Stiffness [N/mm]"),
    ("p_ductility", "Ductility Ratio [mm/mm]"),
    ("p_omega", "Over Strength Factor [N/N]"),
    ("p_R", "Structural Behavior Coefficient"),
    ("d_period_1", "Structural Period 01 [s]"),
    ("d_period_2", "Structural Period 02 [s]"),
    ("d_damping", "Structural Damping Ratio [%]"),
    ("d_vel_x", "Velocity in X Dir. [mm/s]"),
    ("d_vel_y", "Velocity in Y Dir. [mm/s]"),
    ("d_acc_x", "Acceleration in X Dir. [mm/s^2]"),
    ("d_acc_y", "Acceleration in Y Dir. [mm/s^2]"),
    ("p_drift", "Structural Lateral Drift [%] from Pushover Analysis"),
    ("d_drift", "Structural Lateral Drift [%] from Dynamic Analysis"),
    ("ratio:d_drift/p_drift", "Structural Lateral Drift [%] Ratio in X Dir."),
)


def surface_values(rows: list, spec: str) -> np.ndarray:
    """Z values of one surface: a summary key, or the ratio of two keys for a 'ratio:a/b' spec."""
    if spec.startswith("ratio:"):
        numerator, denominator = spec[len("ratio:"):].split("/")
        return np.array([row[numerator] for row in rows]) / np.array([row[denominator] for row in rows])
    return np.array([row[spec] for row in rows], dtype=float)


def plot_surface(output_dir: Path, index: int, z: np.ndarray, zlabel: str, rows: list) -> None:
    """3D contour surface of one quantity over the grid against the column and beam steel ratios (source PLOT_3D: cubic
    interpolation of the cases onto a 100 x 100 grid), saved as a PNG file."""
    import matplotlib.pyplot as plt
    from scipy.interpolate import griddata

    X = np.array([row["ro_col"] for row in rows])
    Y = np.array([row["ro_be"] for row in rows])
    xi = np.linspace(X.min(), X.max(), 100)
    yi = np.linspace(Y.min(), Y.max(), 100)
    xi, yi = np.meshgrid(xi, yi)
    zi = griddata((X, Y), z, (xi, yi), method="cubic")
    fig = plt.figure(figsize=(10, 7), dpi=120)
    ax = fig.add_subplot(111, projection="3d")
    surface = ax.plot_surface(xi, yi, zi, cmap="viridis", edgecolor="none")
    ax.set_xlabel("Column Steel Reinforcement Ratio [%]")
    ax.set_ylabel("Beam Steel Reinforcement Ratio [%]")
    ax.set_zlabel(zlabel)
    fig.colorbar(surface, ax=ax, shrink=0.5, aspect=5)
    ax.set_title(f"3D Contour Plot of {zlabel}")
    fig.tight_layout()
    (output_dir / "surfaces").mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "surfaces" / f"surface_{index:02d}.png")
    plt.close(fig)


def plot_heatmap(output_dir: Path, table: dict) -> None:
    """Correlation heatmap of the pushover table (source PLOT_HEATMAP), saved as a PNG file."""
    import matplotlib.pyplot as plt
    import pandas as pd

    corr = pd.DataFrame(table).corr()
    fig, ax = plt.subplots(figsize=(12, 12), dpi=150)
    image = ax.matshow(corr.values, cmap="viridis")
    fig.colorbar(image, ax=ax, shrink=0.8)
    ax.set_xticks(np.arange(len(corr.columns)))
    ax.set_yticks(np.arange(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=90)
    ax.set_yticklabels(corr.index)
    for i in range(len(corr.index)):
        for j in range(len(corr.columns)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", color="white", fontsize=7)
    ax.set_title("Correlation Heatmap", pad=20)
    fig.tight_layout()
    fig.savefig(output_dir / "correlation_heatmap.png")
    plt.close(fig)


def post_process(output_dir: Path, odb, push: dict, rows: list, fit_x: tuple, fit_y: tuple) -> None:
    """Write the CSV files, the summary, the figures and the interactive views; flush the ODB of the last pushover."""
    odb.save_response()
    save_csv(output_dir, "pushover_last_case.csv", pushover_columns(push))
    save_csv(output_dir, "pushover_results.csv", grid_table(rows, PUSH_TABLE))
    save_csv(output_dir, "free_vibration_results.csv", grid_table(rows, DYN_TABLE))
    save_csv(output_dir, "free_vibration_last_case.csv", dynamic_columns(rows[-1]["dyn"]))
    write_results(output_dir, rows, fit_x, fit_y)
    plot_last_case(output_dir, push, fit_x, fit_y)
    plot_dynamic_last_case(output_dir, rows[-1]["dyn"])
    for index, (spec, zlabel) in enumerate(SURFACES):
        plot_surface(output_dir, index, surface_values(rows, spec), zlabel, rows)
    plot_heatmap(output_dir, grid_table(rows, PUSH_TABLE))
    vis_curves(output_dir, [
        {"x": np.abs(push["disp_x"]) / mm, "y": np.abs(push["shear"]) / N,
         "xlabel": "Displacement in X (mm), node 3", "ylabel": "Base shear (N)", "title": "Last case of the grid"},
    ], filename="vis_08_pushover_last_case.html", title="Base shear vs displacement, last pushover of the grid")
    vis_defo(output_dir, filename="vis_05_deformed_last_case.html", odb_tag=ODB_LAST_CASE, resp_dof="UX",
             resp_type="disp", scale=1.0)


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


def section_fibres(sec_tag: int, hc: float, dia_col: float, kfc: float) -> tuple:
    """Fibre list (is_concrete, E0, A, y) of a section for the column depth hc, the rebar diameter and the ratio kfc, from the
    geometry of define_fiber_section and the initial tangents (Concrete01 E0 = 2 f'c / eps0; Hysteretic E0 = f_y / eps_y).
    Independent of OpenSees."""
    h, b, cover, area_bar, kc_sec, col = section_spec(hc, dia_col, kfc)[sec_tag]
    p = concrete_parameters(kc_sec)
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


def first_step_frame(hc: float, dia_col: float, kfc: float, gross: bool, rule: tuple) -> tuple:
    """First displacement-control step of the frame in numpy for the column depth hc, the rebar diameter and the ratio kfc,
    for the pushover load (1 N horizontal and -1 N vertical at the top nodes). Each element is a force-based element whose
    section flexibilities follow the section states of the current solution, iterated to convergence; gross=True keeps the
    uncracked sections. The restrained DOFs are those of the two fixed bases.

    Returns:
        (load factor, displacements per unit load, number of iterations).
    """
    pos = node_positions()
    elements = []
    for _, ni, nj, sec, _ in ELEMENT_TOPOLOGY:
        L, c, s = element_geometry(pos, ni, nj)
        dofs = [frame_dof(ni, k) for k in range(3)] + [frame_dof(nj, k) for k in range(3)]
        elements.append({"sec": section_fibres(sec, hc, dia_col, kfc), "L": L, "T": transform(c, s), "dofs": dofs,
                         "q": np.zeros(3)})
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
            Bmat = compatibility(e["L"])
            K[np.ix_(e["dofs"], e["dofs"])] += e["T"].T @ (Bmat.T @ kb @ Bmat) @ e["T"]
            parts.append((kb, Bmat))
        u = np.zeros(NDOF)
        u[free] = np.linalg.solve(K[np.ix_(free, free)], force[free])
        for e, (kb, Bmat) in zip(elements, parts):
            e["q"] = kb @ (Bmat @ (e["T"] @ u[e["dofs"]]))
        if u_prev is not None and np.max(np.abs(u - u_prev)) <= 1e-12 * np.max(np.abs(u)):
            return (DINCR / mm) / u[frame_dof(NODE_TOP_R, 0)], u, iteration
        u_prev = u
    raise RuntimeError("the first-step iteration did not converge")


def element_check(hc: float, dia_col: float, kfc: float) -> float:
    """Largest relative difference between the gross force-based element of column element 1 and the textbook frame element
    (EA and EI from the initial tangents of its fibres), for this case."""
    sec_c = section_fibres(SEC_C01, hc, dia_col, kfc)
    _, E_c, A_c, y_c = sec_c
    EA_c = float(np.sum(E_c * A_c))
    EI_c = float(np.sum(E_c * A_c * y_c * y_c))
    L_col = element_geometry(node_positions(), NODE_BASE_L, NODE_COL_L_1)[0]
    Bmat = compatibility(L_col)
    k_fibre = Bmat.T @ element_basic_stiffness(sec_c, L_col, np.zeros(3), True, LOBATTO_RULE) @ Bmat
    k_text = classic_element(EA_c, EI_c, L_col)
    return float(np.max(np.abs(k_fibre - k_text)) / np.max(np.abs(k_text)))


def assemble_linear(hc: float, dia_col: float, kfc: float, reading: str) -> tuple:
    """Linear stiffness (gross sections, initial tangents) and lumped mass of the frame, all DOFs, for the mass reading asked
    for. The element mass is lumped as OpenSees does for the -mass option: m L / 2 at each end in X and Y, and no rotational
    inertia (LESSON 69). The nodal masses are added by add_nodal_masses."""
    pos = node_positions()
    K = np.zeros((NDOF, NDOF))
    M = np.zeros((NDOF, NDOF))
    mass_col, mass_beam = element_masses(hc, reading)
    for _, ni, nj, sec, member in ELEMENT_TOPOLOGY:
        is_conc, E, A, y = section_fibres(sec, hc, dia_col, kfc)
        EA = float(np.sum(E * A))
        EI = float(np.sum(E * A * y * y))
        L, c, s = element_geometry(pos, ni, nj)
        Tg = transform(c, s)
        dofs = [frame_dof(ni, k) for k in range(3)] + [frame_dof(nj, k) for k in range(3)]
        K[np.ix_(dofs, dofs)] += Tg.T @ classic_element(EA, EI, L) @ Tg
        mass = mass_col if member == "col" else mass_beam
        for node in (ni, nj):
            for k in (0, 1):
                M[frame_dof(node, k), frame_dof(node, k)] += mass * L / 2.0
    return K, M


def add_nodal_masses(M: np.ndarray, reading: str) -> np.ndarray:
    """Adds the nodal masses of the free-vibration run (nodes 3 and 4, X and Y) to the lumped element masses."""
    M = M.copy()
    mass = nodal_mass(reading)
    for n in (NODE_TOP_L, NODE_TOP_R):
        M[frame_dof(n, 0), frame_dof(n, 0)] += mass
        M[frame_dof(n, 1), frame_dof(n, 1)] += mass
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


def count_peaks(signal: np.ndarray) -> int:
    """Number of local maxima of a signal (the peaks the logarithmic decrement uses)."""
    x = np.asarray(signal, dtype=float)
    return int(sum(1 for i in range(1, len(x) - 1) if x[i] > x[i - 1] and x[i] > x[i + 1]))


def validate(output_dir: Path, rows: list, push_last: dict) -> None:
    """Compare the grid with independent numpy calculations and check its bookkeeping; write validation.txt.

    For every case: (1) the force-based column element against the textbook frame element (gross sections); (2) the first
    pushover step against OpenSees (section states, 10 Lobatto points) and the equilibrium of the base reactions at every
    pushover step; (3) the first two periods at the initial state against the numpy gross frame with the lumped masses (the
    masses as written), and the Rayleigh damping ratios at those periods; (4) the shortest period against the time step
    (LESSON 71); (5) the same periods with the other reading of the masses (kg as N.s^2/mm = 1000 kg, and the density of
    concrete); (6) that both analyses completed all their steps. The last pushover, run again in this process, is compared
    with its grid run. The bilinear fits, the behaviour coefficients and the logarithmic-decrement damping are the source's
    formulas, ported, and are reported, not validated.
    """
    report = []
    worst = {"element": 0.0, "first": 0.0, "equilibrium": 0.0, "period": 0.0, "rayleigh": 0.0}
    nonfinite = 0
    for row in rows:
        hc, dia_col, kfc = row["hc"] * mm, row["dia"] * mm, row["kfc"]
        tag = case_tag(hc, dia_col, kfc)
        push, dyn = row["push"], row["dyn"]
        lam = push["lam"]
        elem = element_check(hc, dia_col, kfc)
        lam_i, _, n_it = first_step_frame(hc, dia_col, kfc, False, LOBATTO_RULE)
        first = abs(lam[0] / lam_i - 1.0)
        scale = np.max(2.0 * lam)
        eq = max(np.max(np.abs(push["shear"] + 2.0 * lam)), np.max(np.abs(push["axial"] - 2.0 * lam))) / scale
        nonfinite += sum(int(np.sum(~np.isfinite(push[key]))) for key in ("ks", "ka", "ki"))
        nonfinite += sum(int(np.sum(~np.isfinite(dyn[key]))) for key in ("ks", "ka", "ki"))
        K, M = assemble_linear(hc, dia_col, kfc, "as_written")
        M_a = add_nodal_masses(M, "as_written")
        w_a = finite_eigenvalues(K, M_a, NDOF)
        T_a = 2.0 * np.pi / np.sqrt(w_a[:2])
        per_err = max(abs(T_a[0] / row["d_period_1"] - 1.0), abs(T_a[1] / row["d_period_2"] - 1.0))
        T_a_min = 2.0 * np.pi / np.sqrt(w_a[-1])
        w1, w2 = 2.0 * np.pi / row["d_period_1"], 2.0 * np.pi / row["d_period_2"]
        xi1 = row["d_alpha"] / (2.0 * w1) + row["d_beta"] * w1 / 2.0
        xi2 = row["d_alpha"] / (2.0 * w2) + row["d_beta"] * w2 / 2.0
        ray = max(abs(xi1 - DR), abs(xi2 - 0.6 * DR))
        K, M = assemble_linear(hc, dia_col, kfc, "si")
        M_b = add_nodal_masses(M, "si")
        w_b = finite_eigenvalues(K, M_b, NDOF)
        T_b = 2.0 * np.pi / np.sqrt(w_b[:2])
        T_b_min = 2.0 * np.pi / np.sqrt(w_b[-1])
        worst["element"] = max(worst["element"], elem)
        worst["first"] = max(worst["first"], first)
        worst["equilibrium"] = max(worst["equilibrium"], eq)
        worst["period"] = max(worst["period"], per_err)
        worst["rayleigh"] = max(worst["rayleigh"], ray)
        report.append(
            f"{tag}: element check {elem:.1e}; first step lambda OpenSees {lam[0]:.6e}, numpy {lam_i:.6e} (relative "
            f"difference {first:.1e}, {n_it} iterations); equilibrium {eq:.1e}; steps {len(lam)} pushover, {len(dyn['time'])} "
            f"free vibration"
        )
        report.append(
            f"    periods at t = 0 (as written): OpenSees {row['d_period_1']:.6f} s and {row['d_period_2']:.6f} s, numpy "
            f"{T_a[0]:.6f} s and {T_a[1]:.6f} s (relative {per_err:.1e}); Rayleigh ratios at those periods "
            f"{100.0 * xi1:.4f} % and {100.0 * xi2:.4f} % (targets {100.0 * DR:.2f} % and {100.0 * 0.6 * DR:.2f} %)"
        )
        report.append(
            f"    shortest period (as written) {T_a_min:.4e} s, time step {DT / sec:.3e} s (ratio {T_a_min / (DT / sec):.1f}); "
            f"other reading (kg as N.s^2/mm, concrete density): first {T_b[0]:.6f} s, second {T_b[1]:.6f} s, shortest "
            f"{T_b_min:.4e} s (ratio {T_b_min / (DT / sec):.1f})"
        )
        report.append(
            f"    free vibration: log-decrement damping {row['d_damping']:.4f} % from {count_peaks(dyn['disp_x'])} peaks "
            f"of node-3 X; pushover ductility {row['p_ductility']:.6f}, R {row['p_R']:.4f}"
        )
    grid_last = rows[-1]["push"]
    rerun = np.max(np.abs(push_last["shear"] - grid_last["shear"])) / np.max(np.abs(grid_last["shear"]))
    steps_push = sorted({len(row["push"]["lam"]) for row in rows})
    steps_dyn = sorted({len(row["dyn"]["time"]) for row in rows})
    report += [
        "",
        f"cases completed: {len(rows)} of {len(CASES)}; pushover steps per case {steps_push} (expected {round(DMAX / DINCR)}); "
        f"free-vibration steps per case {steps_dyn} (expected {round(DURATION / DT)})",
        f"largest element-check difference {worst['element']:.1e}; largest first-step relative difference "
        f"{worst['first']:.1e}; largest equilibrium residual {worst['equilibrium']:.1e}",
        f"largest relative difference of the periods (as written) {worst['period']:.1e}; largest Rayleigh ratio error "
        f"{worst['rayleigh']:.1e}",
        f"non-finite stiffness values in the case histories (KS, KA, KI): {nonfinite}",
        f"last pushover run again in this process vs its grid run: largest difference of the base shear {rerun:.1e} (relative)",
        "The bilinear fits, the behaviour coefficients and the logarithmic-decrement damping are the source's formulas, ported; "
        "they are reported, not validated.",
    ]
    (output_dir / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report:
        print(line)


# ── 13. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(output_dir)                           # opstool's analysis log goes to the working folder: keep it in output/
    opst.post.set_odb_path(str(output_dir))        # before any CreateODB (AGENT.md §12ac)
    run_grid(output_dir)
    rows = load_case_rows(output_dir)
    odb_last, push_last = run_pushover(LAST_CASE[0], LAST_CASE[1], LAST_CASE[2], ODB_LAST_CASE, output_dir)
    ops.printModel("-JSON", "-file", str(output_dir / "model_info.json"))   # model at the last pushover
    fit_x = bilinear_fit(np.abs(push_last["disp_x"]), np.abs(push_last["shear"]))
    fit_y = bilinear_fit(np.abs(push_last["disp_y"]), np.abs(push_last["axial"]))
    post_process(output_dir, odb_last, push_last, rows, fit_x, fit_y)
    validate(output_dir, rows, push_last)
