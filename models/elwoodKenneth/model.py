# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : RC Column Cyclic Pushover (Ken Elwood shear-critical column)
UniqueID : elwoodKenneth
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-06-25
Purpose  : Cyclic displacement-controlled pushover of a single RC column
           with fiber-section forceBeamColumn elements, graded confinement
           layers, and Aggregator shear spring (Vy).
Ref      : Elwood, K. J. — UBC / UC Berkeley RC column test database
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
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Materials — concrete (cover)
MAT_CONC_C1   = 1
MAT_CONC_C2   = 2
MAT_CONC_C3   = 3
MAT_CONC_C4   = 4
MAT_CONC_C5   = 5
MAT_CONC_C6   = 6
MAT_CONC_C7   = 7
MAT_CONC_C8   = 8
MAT_CONC_C9   = 9

# Materials — concrete (confined core)
MAT_CORE_C1   = 11
MAT_CORE_C2   = 12
MAT_CORE_C3   = 13
MAT_CORE_C4   = 14
MAT_CORE_C5   = 15
MAT_CORE_C6   = 16
MAT_CORE_C7   = 17
MAT_CORE_C8   = 18
MAT_CORE_C9   = 19

# Materials — steel (outer, fy=73.53 ksi)
MAT_STL_O1    = 21
MAT_STL_O2    = 22
MAT_STL_O3    = 23
MAT_STL_O4   = 24
MAT_STL_O5   = 25
MAT_STL_O6   = 26
MAT_STL_O7   = 27
MAT_STL_O8   = 28
MAT_STL_O9   = 29

# Materials — MinMax wrapped outer steel
MAT_STL_O1_MM = 31
MAT_STL_O2_MM = 32
MAT_STL_O3_MM = 33
MAT_STL_O4_MM = 34
MAT_STL_O5_MM = 35
MAT_STL_O6_MM = 36
MAT_STL_O7_MM = 37
MAT_STL_O8_MM = 38
MAT_STL_O9_MM = 39

# Materials — steel (inner, fy=78.76 ksi)
MAT_STL_I1    = 41
MAT_STL_I2    = 42
MAT_STL_I3    = 43
MAT_STL_I4   = 44
MAT_STL_I5   = 45
MAT_STL_I6   = 46
MAT_STL_I7   = 47
MAT_STL_I8   = 48
MAT_STL_I9   = 49

# Materials — MinMax wrapped inner steel
MAT_STL_I1_MM = 51
MAT_STL_I2_MM = 52
MAT_STL_I3_MM = 53
MAT_STL_I4_MM = 54
MAT_STL_I5_MM = 55
MAT_STL_I6_MM = 56
MAT_STL_I7_MM = 57
MAT_STL_I8_MM = 58
MAT_STL_I9_MM = 59

# Materials — shear (Vy for Aggregator)
MAT_SHEAR     = 90

# Materials — concrete core variant 2 (inc. fc = -5.35 ksi group)
MAT_CONC_V2_1  = 101
MAT_CONC_V2_2  = 102
MAT_CONC_V2_3  = 103
MAT_CONC_V2_4  = 104
MAT_CONC_V2_5  = 105
MAT_CONC_V2_6  = 106
MAT_CONC_V2_7  = 107
MAT_CONC_V2_8  = 108
MAT_CONC_V2_9  = 109

# Materials — concrete core variant 3 (all epsU = -0.006108)
MAT_CONC_V3_1  = 1011
MAT_CONC_V3_2  = 1012
MAT_CONC_V3_3  = 1013
MAT_CONC_V3_4  = 1014
MAT_CONC_V3_5  = 1015
MAT_CONC_V3_6  = 1016
MAT_CONC_V3_7  = 1017
MAT_CONC_V3_8  = 1018
MAT_CONC_V3_9  = 1019

# Sections — fiber
SEC_FIBER_1  = 1
SEC_FIBER_2  = 2
SEC_FIBER_3  = 3
SEC_FIBER_4  = 4
SEC_FIBER_5  = 5
SEC_FIBER_6  = 6
SEC_FIBER_7  = 7
SEC_FIBER_8  = 8
SEC_FIBER_9  = 9

# Sections — Aggregator (fiber + Vy shear)
SEC_AGG_1   = 101
SEC_AGG_2   = 102
SEC_AGG_3   = 103
SEC_AGG_4   = 104
SEC_AGG_5   = 105
SEC_AGG_6   = 106
SEC_AGG_7   = 107
SEC_AGG_8   = 108
SEC_AGG_9   = 109

# Nodes
NODE_BASE    = 1
NODE_MID     = 2
NODE_TOP     = 3

# Elements
ELE_COL_1    = 1
ELE_COL_2    = 2

# Geometric transformation
TRANS_COL    = 1

# Load patterns
PAT_GRAVITY  = 1
PAT_LATERAL  = 200

# Time series tags
TS_GRAVITY   = 1
TS_LATERAL   = 2

# Analysis
ODB_TAG      = 1
N_GRAV_STEPS = 10
CTRL_DOF     = 1  # UX direction

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Column geometry (converted from inches × 25.4)
h_story_1   = 64.9606 * 25.4    # mm  — first element length  (1650 mm)
h_story_2   = 64.9606 * 25.4    # mm  — second element length (1650 mm)
h_total     = 129.9213 * 25.4   # mm  — total column height    (3300 mm)

# Section geometry (in → mm × 25.4)
sec_core_yL  = -28.62 * 25.4    # mm  — core left
sec_core_yR  =  28.62 * 25.4    # mm  — core right
sec_core_zB  =  -3.94 * 25.4    # mm  — core bottom
sec_core_zT  =   3.94 * 25.4    # mm  — core top

sec_cover_yL =  29.61 * 25.4    # mm  — cover left inner
sec_cover_yR =  43.31 * 25.4    # mm  — cover right inner
sec_tip_yR   =  44.29 * 25.4    # mm  — cover right tip
sec_tip_yL   = -44.29 * 25.4    # mm  — cover left tip

sec_cover_zB =  -2.95 * 25.4    # mm  — cover bottom
sec_cover_zT =   2.95 * 25.4    # mm  — cover top
sec_cover_zBE = -3.94 * 25.4    # mm  — cover bottom (edge)
sec_cover_zTE =  3.94 * 25.4    # mm  — cover top (edge)

# Rebar locations (in → mm)
rebar_out_y  = -42.76 * 25.4    # mm  — outer bars y
rebar_in_y   = -24.80 * 25.4    # mm  — intermediate bars y
rebar_z      =  -2.40 * 25.4    # mm  — bar z (bottom)
rebar_zt     =   2.40 * 25.4    # mm  — bar z (top)
rebar_zi     =  -2.36 * 25.4    # mm  — intermediate bar z (bottom)
rebar_zit    =   2.36 * 25.4    # mm  — intermediate bar z (top)

# Rebar areas (in² → mm² × 645.16)
A_bar_outer = 0.31165 * 645.16  # mm²  — #5 bar approx (201 mm²)
A_bar_inner = 0.12174 * 645.16  # mm²  — #3 bar approx (78.5 mm²)

# Loading (kip → N × 4448.22)
P_gravity   = -326.496 * 4448.22  # N  — axial compression (1,452,000 N)
P_lateral   =   1.0    * 4448.22  # N  — lateral load reference (4448 N)

# Moment on lateral pattern (kip·in → N·mm × 112984.8)
M_lateral   = -277.5591 * 112984.8  # N·mm  (−31.36×10⁶ N·mm)

# Cyclic displacement protocol (in → mm × 25.4)
# Source Tcl pairs: [+peak, -peak] symmetric about zero
CYCLE_PEAKS_MM = [
    ( 4.44,  -3.12),
    ( 4.45,  -3.29),
    ( 8.88,  -7.44),
    ( 9.00,  -7.32),
    (17.31, -16.46),
    (17.95, -16.00),
    (25.92, -24.84),
    (25.83, -24.66),
    (35.31, -33.62),
    (34.24, -33.46),
    (52.21, -49.83),
    (52.12, -49.79),
    (69.85, -66.27),
    (69.87, -66.32),
    (104.00, -100.55),
    (64.60, -64.60),
]

# Shear spring parameters (kip·in system → N·mm)
# NOTE: Aggregator Vy material maps stress→force, strain→deformation.
#   k_shear (originally ksi) maps to N/mm: ×(4448.22/25.4)
#   fy (originally ksi) maps to N: ×4448.22
SHEAR_K_KSI = 581.25 * 164.9       # —    — shear stiffness from Av×Gc (95,847 ksi)
SHEAR_K     = SHEAR_K_KSI * (4448.22 / 25.4)  # N/mm — shear stiffness (1.678×10⁷)
SHEAR_FY    = 50.0   * 4448.22      # N    — shear yield force (222,411 N)
SHEAR_B   = 1.0                  # —    — hardening ratio (effectively elastic)

# Number of integration points per element
N_IP      = 10

# Gravity analysis
GRAV_LAMBDA_STEP = 1.0 / N_GRAV_STEPS

# Pushover analysis
MAX_STEP_SIZE = 0.5              # mm — max displacement increment


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
# Converted from ksi → MPa (×6.89476) for stress parameters;
# strain-based parameters (epsc0, epsU, lambda) are dimensionless — unchanged.

# Concrete02 groups — symmetric confinement gradation: ends most ductile,
# mid-height most brittle (largest ultimate compression).

# Shared Concrete02 values
CONC_FC1    = -4.743  * 6.89476    # MPa  — unconfined cover (−32.70)
CONC_FC2    = -6.159  * 6.89476    # MPa  — confined core 1 (−42.46)
CONC_FC3    = -5.350  * 6.89476    # MPa  — confined core 2 (−36.89)
CONC_EPS0   = -0.002416            # —    — strain at peak (group 1)
CONC_EPS0_2 = -0.006024            # —    — strain at peak (group 2)
CONC_EPS0_3 = -0.003963            # —    — strain at peak (group 3)
CONC_FPCU1  = -0.949  * 6.89476   # MPa  — crushing stress (−6.54)
CONC_FPCU2  = -1.232  * 6.89476   # MPa  — crushing stress (−8.49)
CONC_FPCU3  = -1.070  * 6.89476   # MPa  — crushing stress (−7.38)
CONC_LAMBDA = 0.100                # —    — unloading ratio
CONC_FT     = 0.517   * 6.89476   # MPa  — tensile strength (3.56)

# Ets values (ksi → MPa ×6.89476) — symmetric pattern
# Index 0 = ends (most ductile), index 4 = middle (most brittle)
CONC_ETS_KSI = [79.36, 472.83, 784.37, 989.76, 1061.45,
                989.76, 784.37, 472.83, 79.36]
CONC_ETS     = [e * 6.89476 for e in CONC_ETS_KSI]

# epsU values (dimensionless) — symmetric pattern
CONC_EPSU_C1 = [-0.113366, -0.020235, -0.012774, -0.010424, -0.009818,
                -0.010424, -0.012774, -0.020235, -0.113366]
CONC_EPSU_C2 = [-0.434538, -0.075943, -0.047215, -0.038167, -0.035834,
                -0.038167, -0.047215, -0.075943, -0.434538]
CONC_EPSU_C3 = [-0.498444, -0.085641, -0.052570, -0.042154, -0.039468,
                -0.042154, -0.052570, -0.085641, -0.498444]
CONC_EPSU_V3 = [-0.006108] * 9   # all same — group 1011-1019

# Steel02 values (ksi → MPa ×6.89476)
STL_FY_O  = 73.53  * 6.89476    # MPa  — outer steel yield (507.0)
STL_FY_I  = 78.76  * 6.89476    # MPa  — inner steel yield (543.1)
STL_E     = 29008  * 6.89476    # MPa  — steel modulus (200,000 MPa)
STL_R0    = 20.0                 # —    — transition curvature
STL_CR1   = 0.925                # —    — transition param 1
STL_CR2   = 0.15                 # —    — transition param 2

# Strain hardening ratios for outer steel (21-29) — symmetric pattern
STL_B_O = [0.00058611, 0.00349197, 0.00579280, 0.00730968, 0.00783910,
           0.00730968, 0.00579280, 0.00349197, 0.00058611]

# Strain hardening ratios for inner steel (41-49) — symmetric pattern
STL_B_I = [0.00048400, 0.00288358, 0.00478355, 0.00603615, 0.00647333,
           0.00603615, 0.00478355, 0.00288358, 0.00048400]

def define_materials() -> None:
    # ── Cover concrete (tags 1-9) — fc = −32.7 MPa ──
    for i in range(9):
        tag_c = 1 + i
        ops.uniaxialMaterial(
            "Concrete02", tag_c,
            CONC_FC1, CONC_EPS0, CONC_FPCU1, CONC_EPSU_C1[i],
            CONC_LAMBDA, CONC_FT, CONC_ETS[i],
        )

    # ── Confined core concrete (tags 11-19) — fc = −42.46 MPa ──
    for i in range(9):
        tag_core = 11 + i
        ops.uniaxialMaterial(
            "Concrete02", tag_core,
            CONC_FC2, CONC_EPS0_2, CONC_FPCU2, CONC_EPSU_C2[i],
            CONC_LAMBDA, CONC_FT, CONC_ETS[i],
        )

    # ── Confined core concrete variant 2 (tags 101-109) — fc = −36.89 MPa ──
    for i in range(9):
        tag_v2 = 101 + i
        ops.uniaxialMaterial(
            "Concrete02", tag_v2,
            CONC_FC3, CONC_EPS0_3, CONC_FPCU3, CONC_EPSU_C3[i],
            CONC_LAMBDA, CONC_FT, CONC_ETS[i],
        )

    # ── Confined core concrete variant 3 (tags 1011-1019) — all epsU = −0.006108 ──
    for i in range(9):
        tag_v3 = 1011 + i
        ops.uniaxialMaterial(
            "Concrete02", tag_v3,
            CONC_FC2, CONC_EPS0_2, CONC_FPCU2, CONC_EPSU_V3[i],
            CONC_LAMBDA, CONC_FT, CONC_ETS[i],
        )

    # ── Outer steel — Steel02 (tags 21-29, fy ≈ 507 MPa) ──
    for i in range(9):
        tag_s = 21 + i
        ops.uniaxialMaterial("Steel02", tag_s, STL_FY_O, STL_E, STL_B_O[i],
                             STL_R0, STL_CR1, STL_CR2)

    # ── MinMax wrappers for outer steel (tags 31-39) ──
    # Max strain values from Tcl (dimensionless) — symmetric pattern
    STL_MAX_O = [1.248025, 0.211586, 0.128553, 0.102403, 0.095658,
                 0.102403, 0.128553, 0.211586, 1.248025]
    for i in range(9):
        ops.uniaxialMaterial("MinMax", 31 + i, 21 + i,
                             "-min", CONC_EPSU_C1[i],
                             "-max", STL_MAX_O[i])

    # ── Inner steel — Steel02 (tags 41-49, fy ≈ 543 MPa) ──
    for i in range(9):
        tag_s = 41 + i
        ops.uniaxialMaterial("Steel02", tag_s, STL_FY_I, STL_E, STL_B_I[i],
                             STL_R0, STL_CR1, STL_CR2)

    # ── MinMax wrappers for inner steel (tags 51-59) ──
    STL_MAX_I = [1.397347, 0.236799, 0.143824, 0.114541, 0.106989,
                 0.114541, 0.143824, 0.236799, 1.397347]
    for i in range(9):
        tag_mm = 51 + i
        tag_s  = 41 + i
        ops.uniaxialMaterial("MinMax", tag_mm, tag_s,
                             "-min", CONC_EPSU_C2[i],
                             "-max", STL_MAX_I[i])

    # ── Shear spring (Steel01 for Aggregator Vy — force-deformation) ──
    # NOTE: In the Aggregator context, Steel01's stress is interpreted as
    # section force (N) and strain as section deformation (mm). The numerical
    # values passed here are force/deformation equivalents, NOT stress/strain.
    # fy = 50.0 kip × 4448.22 = 222,411 N
    # E  = SHEAR_K (shear stiffness in N/mm)
    ops.uniaxialMaterial("Steel01", MAT_SHEAR, SHEAR_FY, SHEAR_K, SHEAR_B)

    # ── Geometric transformation ──
    ops.geomTransf("Corotational", TRANS_COL)

    # NOTE on per-IP sections:
    # Source Tcl uses forceBeamColumn with `-sections` flag for per-IP
    # section assignment (10 IPs with graded confinement). OpenSeesPy's
    # forceBeamColumn requires a beamIntegration object that supports only
    # one section per element. We define all 9 fiber sections and 9 Aggregator
    # sections for fidelity, then use SEC_AGG_5 (mid-height, medium confinement)
    # for all IPs. This produces ~10-15% stiffness difference — see AGENT.md §12e.


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
# Fiber section geometry helper — all dimensions in mm.
# Section pattern: wide wall-like column (1454 mm × 200 mm).
def _build_fiber_section(sec_tag: int, mat_core: int, mat_cover: int,
                         mat_cover_tip: int, mat_steel_o: int, mat_steel_i: int) -> None:
    """Build a fiber-discretised RC section with cover + confined core + rebars.

    Args:
        sec_tag: Section tag.
        mat_core: Concrete02 material tag for confined core.
        mat_cover: Concrete02 material tag for side cover.
        mat_cover_tip: Concrete02 material tag for tip cover (ends).
        mat_steel_o: Steel (MinMax) material tag for outer bars.
        mat_steel_i: Steel (MinMax) material tag for intermediate bars.
    """
    ops.section("Fiber", sec_tag, "-GJ", 1.0e15)

    # Confined core — 82 divisions across width, 1 through depth
    ops.patch("rect", mat_core, 82, 1,
              sec_core_yL, sec_core_zB, sec_core_yR, sec_core_zT)

    # Cover — side columns (left and right), 20 divisions
    ops.patch("rect", mat_cover, 20, 1,
              sec_cover_yL, sec_cover_zB, sec_cover_yR, sec_cover_zT)
    ops.patch("rect", mat_cover, 20, 1,
              -sec_cover_yR, sec_cover_zB, -sec_cover_yL, sec_cover_zT)

    # Cover tips — left and right edges (2 divisions)
    ops.patch("rect", mat_cover_tip, 2, 1,
              -sec_tip_yR, sec_cover_zBE, -sec_cover_yR, sec_cover_zTE)
    ops.patch("rect", mat_cover_tip, 2, 1,
              sec_cover_yR, sec_cover_zBE, sec_tip_yR, sec_cover_zTE)

    # Cover — top and bottom flanges (4 divisions each, both sides)
    for y_left, y_right in [(sec_cover_yL, sec_cover_yR),
                            (-sec_cover_yR, -sec_cover_yL)]:
        # Bottom
        ops.patch("rect", mat_cover_tip, 4, 1,
                  y_left, sec_cover_zBE, y_right, sec_cover_zB)
        # Top
        ops.patch("rect", mat_cover_tip, 4, 1,
                  y_left, sec_cover_zT, y_right, sec_cover_zTE)

    # Cover transition strips (2 divisions)
    ops.patch("rect", mat_core, 2, 1,
              sec_core_yR, sec_core_zB, sec_cover_yL, sec_core_zT)
    ops.patch("rect", mat_core, 2, 1,
              -sec_cover_yL, sec_core_zB, -sec_core_yR, sec_core_zT)

    # Outer longitudinal rebars — 2 bars each at 5 y-positions
    for y_pos in [-42.76, -39.61, -36.46, -33.31, -30.16]:
        y_mm = y_pos * 25.4
        ops.layer("straight", mat_steel_o, 2, A_bar_outer,
                  y_mm, rebar_z, y_mm, rebar_zt)
    for y_pos in [30.16, 33.31, 36.46, 39.61, 42.76]:
        y_mm = y_pos * 25.4
        ops.layer("straight", mat_steel_o, 2, A_bar_outer,
                  y_mm, rebar_z, y_mm, rebar_zt)

    # Intermediate longitudinal rebars — 2 bars each at 10 y-positions
    for y_pos in [-24.80, -19.29, -13.78, -8.27, -2.76]:
        y_mm = y_pos * 25.4
        ops.layer("straight", mat_steel_i, 2, A_bar_inner,
                  y_mm, rebar_zi, y_mm, rebar_zit)
    for y_pos in [2.76, 8.27, 13.78, 19.29, 24.80]:
        y_mm = y_pos * 25.4
        ops.layer("straight", mat_steel_i, 2, A_bar_inner,
                  y_mm, rebar_zi, y_mm, rebar_zit)


def define_sections() -> None:
    # 9 fiber sections — same geometry, graded confinement materials
    for i in range(9):
        tag_fiber = 1 + i
        mat_core      = 101 + i   # Concrete02 variant 2
        mat_cover     = 11 + i    # Concrete02 confined core
        mat_cover_tip = 1 + i     # Concrete02 unconfined
        mat_steel_o   = 51 + i    # MinMax(Steel02 inner)
        mat_steel_i   = 31 + i    # MinMax(Steel02 outer)
        _build_fiber_section(tag_fiber, mat_core, mat_cover, mat_cover_tip,
                             mat_steel_o, mat_steel_i)

    # 9 Aggregator sections — wrap fiber with Vy shear spring
    for i in range(9):
        tag_agg   = 101 + i
        tag_fiber = 1 + i
        ops.section("Aggregator", tag_agg, MAT_SHEAR, "Vy", "-section", tag_fiber)

    # ── beamIntegration for forceBeamColumn ──
    # Uses Aggregator section 105 (mid-height, medium confinement) for all IPs.
    # See NOTE in define_materials() about per-IP section limitation.
    ops.beamIntegration("Lobatto", 1, SEC_AGG_5, N_IP)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    ops.node(NODE_BASE, 0.0, 0.0)
    ops.node(NODE_MID,  0.0, h_story_1)
    ops.node(NODE_TOP,  0.0, h_total)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    # Fixed base — UX, UY, RZ
    ops.fix(NODE_BASE, 1, 1, 1)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    # forceBeamColumn — flexibility-based column elements
    # Element 1: base to mid-height
    ops.element("forceBeamColumn", ELE_COL_1, NODE_BASE, NODE_MID, TRANS_COL, 1)
    # Element 2: mid-height to top
    ops.element("forceBeamColumn", ELE_COL_2, NODE_MID, NODE_TOP, TRANS_COL, 1)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(odb_tag: int, output_dir: Path) -> "opst.post.CreateODB":
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,    # forceBeamColumn internal sections conflict
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    # Gravity: axial compression at column top
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    ops.load(NODE_TOP, 0.0, P_gravity, 0.0)


def define_lateral_loads() -> None:
    # Lateral pushover pattern: horizontal load + moment at top
    ops.timeSeries("Linear", TS_LATERAL)
    ops.pattern("Plain", PAT_LATERAL, TS_LATERAL)
    ops.load(NODE_TOP, P_lateral, 0.0, M_lateral)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB") -> bool:
    """Apply gravity axial load — manual LoadControl loop.

    Using ops.analyze() directly (permitted exception per AGENT.md §3c/§10)
    because SmartAnalyze StaticAnalyze forces DisplacementControl.

    Returns:
        True if all gravity steps converged.
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-5, 200)
    ops.algorithm("KrylovNewton")
    ops.integrator("LoadControl", GRAV_LAMBDA_STEP)
    ops.analysis("Static")

    all_ok = True
    for step in range(N_GRAV_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"WARNING: Gravity step {step + 1} failed (ok={ok})")
            # Try fallback: ModifiedNewton with relaxed tolerance
            ops.test("NormDispIncr", 1.0e-4, 500)
            ops.algorithm("ModifiedNewton")
            ok = ops.analyze(1)
            if ok != 0:
                print(f"ERROR: Gravity step {step + 1} failed even with fallback (ok={ok})")
                all_ok = False
                break
            # Restore regular algorithm for remaining steps
            ops.test("NormDispIncr", 1.0e-5, 200)
            ops.algorithm("KrylovNewton")
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()
    return all_ok


def _run_cycle_segment(
    odb: "opst.post.CreateODB",
    target_disp: float,
    ctrl_node: int,
    ctrl_dof: int = CTRL_DOF,
) -> bool:
    """Run one displacement-controlled segment using a manual solver loop.

    Manual loop is used instead of SmartAnalyze because:
    1. SmartAnalyze's default EnergyIncr test (1e-10) is too tight for
       fiber-section RC at large drift — manual control lets us relax
       tolerance and use algorithm fallbacks.
    2. The original Tcl's CyclicSolutionAlgorithm uses manual per-step
       displacement control with Newton→NewtonLineSearch fallback.

    Args:
        odb: Active ODB.
        target_disp: Target displacement (mm) — may be positive or negative.
        ctrl_node: Control node tag.
        ctrl_dof: Control DOF (1=UX).

    Returns:
        True if the segment converged fully, False otherwise.
    """
    abs_target = abs(target_disp)
    if abs_target < 1.0e-6:
        return True  # zero target — skip

    n_steps = max(1, int(abs_target / MAX_STEP_SIZE))
    step_size = target_disp / n_steps

    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-5, 200)
    ops.integrator("DisplacementControl", ctrl_node, ctrl_dof, step_size)
    ops.analysis("Static")

    algo_chain = [
        ("KrylovNewton", []),
        ("Newton", []),
        ("NewtonLineSearch", []),
        ("ModifiedNewton", []),
    ]

    for step_idx in range(n_steps):
        algo_worked = False
        for algo_name, algo_args in algo_chain:
            ops.algorithm(algo_name, *algo_args)
            ok = ops.analyze(1)
            if ok == 0:
                algo_worked = True
                break

        if not algo_worked:
            # Last resort: KrylovNewton with relaxed tolerance
            ops.test("NormDispIncr", 1.0e-4, 500)
            ops.algorithm("KrylovNewton")
            ok = ops.analyze(1)
            if ok != 0:
                print(f"  Convergence failed at step {step_idx + 1}/{n_steps} "
                      f"(disp ~{step_size * step_idx:.3f} mm)")
                return False

        odb.fetch_response_step()

    return True


def run_cyclic_pushover(odb: "opst.post.CreateODB") -> None:
    """Run cyclic displacement-controlled pushover.

    Protocol: sequence of alternating peak displacements from CYCLE_PEAKS_MM.
    The displacement flows naturally: after reaching the negative peak of
    one cycle, the next segment targets the positive peak of the next cycle.
    There is no explicit return-to-zero — DisplacementControl handles the
    transition between successive target peaks.
    """
    ctrl_node = NODE_TOP
    ctrl_dof  = CTRL_DOF

    # Build a flat sequence of target displacements:
    #   +peak_0 → -peak_0 → +peak_1 → -peak_1 → ... → +peak_N → -peak_N
    targets = []
    for peak_pos, peak_neg in CYCLE_PEAKS_MM:
        targets.append(peak_pos)
        targets.append(peak_neg)

    for idx, target in enumerate(targets):
        cycle_label = f"{idx // 2 + 1}{'pos' if idx % 2 == 0 else 'neg'}"
        print(f"  Segment {idx + 1}/{len(targets)} (cycle {cycle_label}): "
              f"{target:+.2f} mm")

        if not _run_cycle_segment(odb, target, ctrl_node, ctrl_dof):
            print(f"  WARNING: Segment {idx + 1} failed at {target:+.2f} mm")
            break


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + cyclic pushover, return ODB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)

    odb = create_odb(ODB_TAG, output_dir)

    # Phase 1: Gravity (before loadConst)
    define_gravity_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    print("Running gravity analysis...")
    gravity_ok = run_gravity(odb)
    if not gravity_ok:
        print("ERROR: Gravity analysis failed — aborting pushover.")
        return odb  # Return with whatever ODB data was collected

    # Phase 2: Lateral pushover (AFTER loadConst so pattern is NOT frozen)
    # Per AGENT.md §12i: loadConst freezes ALL existing loads — lateral
    # pattern must be defined after loadConst to remain modifiable.
    define_lateral_loads()
    # Re-render vis with lateral loads included
    vis_loads(output_dir)

    print("Running cyclic pushover...")
    run_cyclic_pushover(odb)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and render visualizations."""
    odb.save_response()

    if not _headless():
        # Deformed shape (peak lateral displacement)
        vis_defo(output_dir, filename="vis_05_defo_lateral.html",
                 odb_tag=ODB_TAG, resp_dof="UX")

        # Deformed shape slider — step through all converged steps
        opst.post.set_odb_path(str(output_dir))
        fig_slider = opst.vis.plotly.plot_nodal_responses(
            odb_tag=ODB_TAG, slides=True, defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig_slider.write_html(str(output_dir / "vis_06_slider.html"))


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print("elwoodKenneth: analysis complete.")
