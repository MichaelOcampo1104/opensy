# -- 0. FILE HEADER ----------------------------------------------------------------
"""
Model    : 2D Soil-Structure Interaction -- RC Frame + MultiYieldSurfaceClay
           Soil Deposit under El Centro Earthquake
UniqueID : XMU_Chapter6
Author   : XMU (Xiamen University) -- Chapter 6 Example
Date     : 2026-06-16
Purpose  : Dynamic time-history analysis of a 2-story 3-bay RC frame founded
           on a 5-layer soil deposit. Fiber-section columns/beams (Concrete01
           cover + core, Hardening rebar) with MultiYieldSurfaceClay quad
           elements represent the soil domain. Sequential model building:
           frame (ndf=3) -> soil (ndf=2) -> equalDOF ties.
Ref      : XMU Finite Element Analysis course, Chapter 6
Units    : N, mm, MPa  (see standards/units.py)
Notes    : Converted from model.tcl.
           Original units: m, ton, sec, kN, kPa -- converted to N, mm, MPa.
           kN->N (x1000), m->mm (x1000), kPa->MPa (/1000).
           Mass (ton) -> tonne (x1, same).
           Hardening material for rebar (not Steel01/Steel02).
           MultiYieldSurfaceClay for soil layers (4 soil + 1 structural).
           quadWithSensitivity elements with PlaneStrain condition.
           Soil body force: kN/m^3 -> N/mm^3 (/10^6).
           Ground motion: elcentro.txt (m/s^2) * factor 3 * 1000 -> mm/s^2.
"""

# -- 1. IMPORTS -------------------------------------------------------------------
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# -- 2. TAG REGISTRY --------------------------------------------------------------
# Frame materials (ndf=3 phase)
MAT_COVER_UPPER  = 1   # Concrete01 -- unconfined cover (upper structure)
MAT_CORE_UPPER   = 2   # Concrete01 -- confined core   (upper structure)
MAT_REBAR_UPPER  = 3   # Hardening  -- rebar           (upper structure)
MAT_COVER_LOWER  = 4   # Concrete01 -- unconfined cover (underground)
MAT_CORE_LOWER   = 5   # Concrete01 -- confined core   (underground)
MAT_REBAR_LOWER  = 6   # Hardening  -- rebar           (underground)

# Frame sections
SEC_COL_UPPER_BIG   = 1   # 600x500 mm (center column, upper)
SEC_COL_UPPER_SIDE  = 2   # 500x500 mm (side columns, upper)
SEC_BEAM            = 3   # 500x400 mm (beams)
SEC_COL_LOWER_BIG   = 4   # 600x500 mm (center column, underground)
SEC_COL_LOWER_SIDE  = 5   # 500x500 mm (side columns, underground)

# Soil materials (ndf=2 phase)
MAT_SOIL_STRUCTURAL = 100  # MultiYieldSurfaceClay -- structural concrete surrogate
MAT_SOIL_LAYER1     = 101  # MultiYieldSurfaceClay -- top layer (weakest)
MAT_SOIL_LAYER2     = 102  # MultiYieldSurfaceClay
MAT_SOIL_LAYER3     = 103  # MultiYieldSurfaceClay
MAT_SOIL_LAYER4     = 104  # MultiYieldSurfaceClay -- bottom layer (strongest)

# Node ranges
FRAME_FIRST = 1
FRAME_LAST  = 15
SOIL_FIRST  = 16
SOIL_LAST   = 110

# Element ranges
ELE_FRAME_FIRST = 1
ELE_FRAME_LAST  = 16
ELE_SOIL_FIRST  = 17
ELE_SOIL_LAST   = 88

# Integrations & transforms (one per section type)
INTEG_SEC1 = 1   # 600x500 upper center column
INTEG_SEC2 = 2   # 500x500 upper side column
INTEG_SEC3 = 3   # 500x400 beam
INTEG_SEC4 = 4   # 600x500 underground center column
INTEG_SEC5 = 5   # 500x500 underground side column
TRANS_TAG  = 1

# -- 3. PARAMETERS ----------------------------------------------------------------
# --- Geometry (m -> mm) ---
bay_width    = 7.0 * m      # 7000 mm
story_h1     = 3.6 * m      # 3600 mm
story_h2     = 3.6 * m      # 3600 mm
ug_level1    = -1.2 * m     # -1200 mm
ug_level2    = -2.4 * m     # -2400 mm
n_ip         = 4             # Legendre integration points

frame_x_left   = 0.0 * m
frame_x_center = 7.0 * m
frame_x_right  = 14.0 * m

# --- Section 1: Upper center column 600x500 ---
sec1_z1, sec1_y1 = -0.30*m,  0.25*m   # top-left
sec1_z2, sec1_y2 = -0.30*m, -0.25*m   # bottom-left
sec1_z3, sec1_y3 =  0.30*m, -0.25*m   # bottom-right
sec1_z4, sec1_y4 =  0.30*m,  0.25*m   # top-right
sec1_core_y_top  =  0.20*m
sec1_core_y_bot  = -0.20*m
sec1_core_z_left  = -0.25*m
sec1_core_z_right =  0.25*m
n_bars_sec1 = 3
As_sec1 = 0.000645 * m**2      # 645 mm^2

# --- Section 2: Upper side column 500x500 ---
sec2_z1, sec2_y1 = -0.25*m,  0.25*m
sec2_z2, sec2_y2 = -0.25*m, -0.25*m
sec2_z3, sec2_y3 =  0.25*m, -0.25*m
sec2_z4, sec2_y4 =  0.25*m,  0.25*m
sec2_core_y_top  =  0.20*m
sec2_core_y_bot  = -0.20*m
sec2_core_z_left  = -0.20*m
sec2_core_z_right =  0.20*m
n_bars_sec2 = 3
As_sec2 = 0.000510 * m**2      # 510 mm^2

# --- Section 3: Beam 500x400 ---
sec3_z1, sec3_y1 = -0.25*m,  0.20*m
sec3_z2, sec3_y2 = -0.25*m, -0.20*m
sec3_z3, sec3_y3 =  0.25*m, -0.20*m
sec3_z4, sec3_y4 =  0.25*m,  0.20*m
n_bars_beam = 2
As_beam = 0.000645 * m**2      # 645 mm^2

# --- Concrete01 cover (upper, tags 1 & 4) ---
fc_cover    = -27588.5 * kPa   # -27.6 MPa
epsc0_cover = -0.002
fcu_cover   = 0.0
epsu_cover  = -0.008

# --- Concrete01 core (upper, tags 2 & 5) ---
fc_core     = -34485.6 * kPa   # -34.5 MPa
epsc0_core  = -0.004
fcu_core    = -20691.4 * kPa   # -20.7 MPa
epsu_core   = -0.014

# --- Hardening rebar (tags 3 & 6) ---
# E=200 GPa, sigmaY=248.2 MPa, H_iso=0, H_kin=1613 MPa, b=H_kin/(E+H_kin)=0.008
E_rebar     = 2.0e8 * kPa      # 200000 MPa
sigmaY_rebar = 248200.0 * kPa  # 248.2 MPa
H_iso_rebar  = 0.0
H_kin_rebar  = 1.6129e6 * kPa  # 1612.9 MPa

# --- Soil material parameters (kPa -> MPa) ---
soil_rho = 0.0  # no dynamic mass in soil (static gravity only via body force)

# Material 100: Structural concrete surrogate (very stiff)
soil100_Gr       = 2.0e7 * kPa      # 20000 MPa
soil100_Br       = 1.0e6 * kPa      # 1000 MPa
soil100_cohesion = 21000.0 * kPa    # 21 MPa
soil100_peak     = 50.0
soil100_phi      = 0
soil100_refPress = 100.0 * kPa      # 0.1 MPa
soil100_pressDep = 0
soil100_nSurf    = 2

# Materials 101-104: Actual soil layers (increasing stiffness with depth)
soil101_Gr       = 54450.0 * kPa    # 54.45 MPa
soil101_Br       = 1.6e5 * kPa      # 160 MPa
soil101_cohesion = 33.0 * kPa       # 0.033 MPa
soil101_peak     = 0.1

soil102_Gr       = 33800.0 * kPa    # 33.8 MPa
soil102_Br       = 1.0e5 * kPa      # 100 MPa
soil102_cohesion = 26.0 * kPa       # 0.026 MPa
soil102_peak     = 0.1

soil103_Gr       = 61250.0 * kPa    # 61.25 MPa
soil103_Br       = 1.8e5 * kPa      # 180 MPa
soil103_cohesion = 35.0 * kPa       # 0.035 MPa
soil103_peak     = 0.1

soil104_Gr       = 96800.0 * kPa    # 96.8 MPa
soil104_Br       = 2.9e5 * kPa      # 290 MPa
soil104_cohesion = 44.0 * kPa       # 0.044 MPa
soil104_peak     = 0.1

# --- Quad element properties ---
quad_thickness     = 0.60 * m        # 600 mm
quad_density       = 2.0             # tonne/m^3 (preserved for dynamic)
quad_body_force_y  = -19.6 * 1e-6   # kN/m^3 -> N/mm^3: 19.6 / 10^6 = 1.96e-5

# --- Soil mesh geometry ---
soil_x_array = np.array([
    -9.2, -7.2, -5.2, -3.2, -1.2, 0.0, 1.2, 3.5, 5.8,
    7.0, 8.2, 10.5, 12.8, 14.0, 15.2, 17.2, 19.2, 21.2, 23.2
]) * m  # 19 x-positions in mm

soil_y_array = np.array([-7.2, -4.8, -2.4, -1.2, 0.0]) * m  # 5 y-positions in mm
n_soil_x = len(soil_x_array)  # 19
n_soil_y = len(soil_y_array)  # 5

# --- Masses (tonne, same as Tcl ton) ---
framemass1 = 15.0     # side column nodes
framemass2 = 30.0     # center column nodes
framemass3 = 4.0      # underground nodes

# --- Nodal gravity loads (kN -> N) ---
# In Tcl: mass * 10 m/s^2 = load in kN
# In N-mm: mass * 10000 mm/s^2 = load in N (same as mass * 10 * 1000)
upperload1 = -framemass1 * 10.0 * kN   # -150000 N
upperload2 = -framemass2 * 10.0 * kN   # -300000 N
download3  = -framemass3 * 10.0 * kN   # -40000 N

# --- Ground motion ---
gm_dir    = Path(__file__).parent / "ground_motions"
gm_file   = "elcentro.txt"
gm_dt     = 0.01          # time step of ground motion file [s]
gm_factor = 3.0           # amplification factor from Tcl
gm_npts   = 2400          # total analysis steps (2400 * 0.005 = 12s)

# --- Analysis ---
n_steps_gravity = 10
analysis_dt     = 0.005   # analysis time step (sub-stepping from gm_dt=0.01)
newmark_gamma   = 0.55
newmark_beta    = 0.275625
odb_every_n     = 10

# -- 4. MODEL BUILD ---------------------------------------------------------------

def _soil_node_index(col: int, row: int) -> int:
    """Return global node tag for soil node at (col, row).

    col: 0..18 (x-position index), row: 0..4 (y-position index, 0=bottom)
    """
    return SOIL_FIRST + row * n_soil_x + col


def _soil_ele_tag(row: int, col: int) -> int:
    """Return element tag for quad in element row `row` (0..3) and column `col` (0..17)."""
    return ELE_SOIL_FIRST + row * (n_soil_x - 1) + col


def _soil_mat_for_position(ele_row: int, col: int) -> int:
    """Return MultiYieldSurfaceClay material tag for a quad element position.

    ele_row: 0=bottom (y=-7.2 to -4.8), 3=top (y=-1.2 to 0)
    col: 0..17 (element column index)

    Structural concrete (material 100) under each frame column (x=0, 7, 14 m)
    occupies 2 elements wide in the upper two element rows.
    """
    layer_soil_mat = {
        0: MAT_SOIL_LAYER4,   # bottom: strongest soil
        1: MAT_SOIL_LAYER3,
        2: MAT_SOIL_LAYER2,
        3: MAT_SOIL_LAYER1,   # surface: weakest soil
    }

    # Structural elements in upper two rows under each frame column position
    # Left (x=0): cols 4,5. Center (x=7): cols 8,9. Right (x=14): cols 12,13
    structural_cols = {4, 5, 8, 9, 12, 13}

    if ele_row >= 2 and col in structural_cols:
        return MAT_SOIL_STRUCTURAL

    return layer_soil_mat[ele_row]


def build_model() -> None:
    """Build full SSI model in three phases."""

    # --- Phase 1: Frame model (ndf=3) ---
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    _define_frame_materials()
    _define_frame_sections()
    _create_frame_nodes()
    _apply_frame_bcs()
    _create_frame_elements()
    print("Frame model built (ndf=3): 15 nodes, 16 elements.")

    # --- Phase 2: Soil model (ndf=2) ---
    ops.model("basic", "-ndm", 2, "-ndf", 2)
    _define_soil_materials()
    _create_soil_nodes()
    _apply_soil_bcs()
    _create_soil_elements()
    print("Soil model built (ndf=2): 95 nodes, 72 quad elements.")

    # --- Phase 3: Tie models ---
    _tie_frame_to_soil()
    print("Models tied: 5 lateral periodicity + 9 frame-to-soil equalDOF pairs.")


# -- 5. FRAME MATERIALS ------------------------------------------------------------

def _define_frame_materials() -> None:
    """Concrete01 (cover + core) and Hardening rebar for upper and lower sections."""
    # Upper structure
    ops.uniaxialMaterial("Concrete01", MAT_COVER_UPPER,
                         fc_cover, epsc0_cover, fcu_cover, epsu_cover)
    ops.uniaxialMaterial("Concrete01", MAT_CORE_UPPER,
                         fc_core, epsc0_core, fcu_core, epsu_core)
    ops.uniaxialMaterial("Hardening", MAT_REBAR_UPPER,
                         E_rebar, sigmaY_rebar, H_iso_rebar, H_kin_rebar)

    # Underground (same properties, separate tags)
    ops.uniaxialMaterial("Concrete01", MAT_COVER_LOWER,
                         fc_cover, epsc0_cover, fcu_cover, epsu_cover)
    ops.uniaxialMaterial("Concrete01", MAT_CORE_LOWER,
                         fc_core, epsc0_core, fcu_core, epsu_core)
    ops.uniaxialMaterial("Hardening", MAT_REBAR_LOWER,
                         E_rebar, sigmaY_rebar, H_iso_rebar, H_kin_rebar)


# -- 6. FRAME SECTIONS -------------------------------------------------------------

def _define_frame_sections() -> None:
    """Build 5 fiber sections for columns and beams."""

    # --- Section 1: Upper center column 600x500 mm ---
    ops.section("Fiber", SEC_COL_UPPER_BIG)
    # Confined core: 500x400 mm (z from -250 to 250, y from -200 to 200)
    ops.patch("quad", MAT_CORE_UPPER, 12, 1,
              sec1_core_z_left,  sec1_core_y_top,
              sec1_core_z_left,  sec1_core_y_bot,
              sec1_core_z_right, sec1_core_y_bot,
              sec1_core_z_right, sec1_core_y_top)
    # Bottom cover
    ops.patch("quad", MAT_COVER_UPPER, 14, 1,
              sec1_z1, sec1_core_y_bot,
              sec1_z2, sec1_y2,
              sec1_z3, sec1_y3,
              sec1_z4, sec1_core_y_bot)
    # Top cover
    ops.patch("quad", MAT_COVER_UPPER, 14, 1,
              sec1_z1, sec1_y1,
              sec1_z2, sec1_core_y_top,
              sec1_z3, sec1_core_y_top,
              sec1_z4, sec1_y4)
    # Left cover
    ops.patch("quad", MAT_COVER_UPPER, 2, 1,
              sec1_z1, sec1_y1,
              sec1_z2, sec1_y2,
              sec1_core_z_left, sec1_core_y_bot,
              sec1_core_z_left, sec1_core_y_top)
    # Right cover
    ops.patch("quad", MAT_COVER_UPPER, 2, 1,
              sec1_core_z_right, sec1_core_y_top,
              sec1_core_z_right, sec1_core_y_bot,
              sec1_z3, sec1_y3,
              sec1_z4, sec1_y4)
    # Top rebar layer: 3 bars, y=0.20, z=-0.20 to 0.20
    ops.layer("straight", MAT_REBAR_UPPER, n_bars_sec1, As_sec1,
              sec1_core_y_top, sec1_core_z_left,
              sec1_core_y_top, sec1_core_z_right)
    # Bottom rebar layer: 3 bars, y=-0.20, z=-0.20 to 0.20
    ops.layer("straight", MAT_REBAR_UPPER, n_bars_sec1, As_sec1,
              sec1_core_y_bot, sec1_core_z_left,
              sec1_core_y_bot, sec1_core_z_right)

    # --- Section 2: Upper side column 500x500 mm ---
    ops.section("Fiber", SEC_COL_UPPER_SIDE)
    ops.patch("quad", MAT_CORE_UPPER, 10, 1,
              sec2_core_z_left,  sec2_core_y_top,
              sec2_core_z_left,  sec2_core_y_bot,
              sec2_core_z_right, sec2_core_y_bot,
              sec2_core_z_right, sec2_core_y_top)
    ops.patch("quad", MAT_COVER_UPPER, 12, 1,
              sec2_z1, sec2_core_y_bot,
              sec2_z2, sec2_y2,
              sec2_z3, sec2_y3,
              sec2_z4, sec2_core_y_bot)
    ops.patch("quad", MAT_COVER_UPPER, 12, 1,
              sec2_z1, sec2_y1,
              sec2_z2, sec2_core_y_top,
              sec2_z3, sec2_core_y_top,
              sec2_z4, sec2_y4)
    ops.patch("quad", MAT_COVER_UPPER, 2, 1,
              sec2_z1, sec2_y1,
              sec2_z2, sec2_y2,
              sec2_core_z_left, sec2_core_y_bot,
              sec2_core_z_left, sec2_core_y_top)
    ops.patch("quad", MAT_COVER_UPPER, 2, 1,
              sec2_core_z_right, sec2_core_y_top,
              sec2_core_z_right, sec2_core_y_bot,
              sec2_z3, sec2_y3,
              sec2_z4, sec2_y4)
    ops.layer("straight", MAT_REBAR_UPPER, n_bars_sec2, As_sec2,
              sec2_core_y_top, sec2_core_z_left,
              sec2_core_y_top, sec2_core_z_right)
    ops.layer("straight", MAT_REBAR_UPPER, n_bars_sec2, As_sec2,
              sec2_core_y_bot, sec2_core_z_left,
              sec2_core_y_bot, sec2_core_z_right)

    # --- Section 3: Beam 500x400 mm ---
    ops.section("Fiber", SEC_BEAM)
    ops.patch("quad", MAT_COVER_UPPER, 12, 1,
              sec3_z1, sec3_y1,
              sec3_z2, sec3_y2,
              sec3_z3, sec3_y3,
              sec3_z4, sec3_y4)
    ops.layer("straight", MAT_REBAR_UPPER, n_bars_beam, As_beam,
              sec3_y1, sec3_z2,
              sec3_y1, sec3_z3)
    ops.layer("straight", MAT_REBAR_UPPER, n_bars_beam, As_beam,
              sec3_y2, sec3_z2,
              sec3_y2, sec3_z3)

    # --- Section 4: Underground center column 600x500 (copy of Sec1 with lower mats) ---
    ops.section("Fiber", SEC_COL_LOWER_BIG)
    ops.patch("quad", MAT_CORE_LOWER, 12, 1,
              sec1_core_z_left,  sec1_core_y_top,
              sec1_core_z_left,  sec1_core_y_bot,
              sec1_core_z_right, sec1_core_y_bot,
              sec1_core_z_right, sec1_core_y_top)
    ops.patch("quad", MAT_COVER_LOWER, 14, 1,
              sec1_z1, sec1_core_y_bot,
              sec1_z2, sec1_y2,
              sec1_z3, sec1_y3,
              sec1_z4, sec1_core_y_bot)
    ops.patch("quad", MAT_COVER_LOWER, 14, 1,
              sec1_z1, sec1_y1,
              sec1_z2, sec1_core_y_top,
              sec1_z3, sec1_core_y_top,
              sec1_z4, sec1_y4)
    ops.patch("quad", MAT_COVER_LOWER, 2, 1,
              sec1_z1, sec1_y1,
              sec1_z2, sec1_y2,
              sec1_core_z_left, sec1_core_y_bot,
              sec1_core_z_left, sec1_core_y_top)
    ops.patch("quad", MAT_COVER_LOWER, 2, 1,
              sec1_core_z_right, sec1_core_y_top,
              sec1_core_z_right, sec1_core_y_bot,
              sec1_z3, sec1_y3,
              sec1_z4, sec1_y4)
    ops.layer("straight", MAT_REBAR_LOWER, n_bars_sec1, As_sec1,
              sec1_core_y_top, sec1_core_z_left,
              sec1_core_y_top, sec1_core_z_right)
    ops.layer("straight", MAT_REBAR_LOWER, n_bars_sec1, As_sec1,
              sec1_core_y_bot, sec1_core_z_left,
              sec1_core_y_bot, sec1_core_z_right)

    # --- Section 5: Underground side column 500x500 (copy of Sec2 with lower mats) ---
    ops.section("Fiber", SEC_COL_LOWER_SIDE)
    ops.patch("quad", MAT_CORE_LOWER, 10, 1,
              sec2_core_z_left,  sec2_core_y_top,
              sec2_core_z_left,  sec2_core_y_bot,
              sec2_core_z_right, sec2_core_y_bot,
              sec2_core_z_right, sec2_core_y_top)
    ops.patch("quad", MAT_COVER_LOWER, 12, 1,
              sec2_z1, sec2_core_y_bot,
              sec2_z2, sec2_y2,
              sec2_z3, sec2_y3,
              sec2_z4, sec2_core_y_bot)
    ops.patch("quad", MAT_COVER_LOWER, 12, 1,
              sec2_z1, sec2_y1,
              sec2_z2, sec2_core_y_top,
              sec2_z3, sec2_core_y_top,
              sec2_z4, sec2_y4)
    ops.patch("quad", MAT_COVER_LOWER, 2, 1,
              sec2_z1, sec2_y1,
              sec2_z2, sec2_y2,
              sec2_core_z_left, sec2_core_y_bot,
              sec2_core_z_left, sec2_core_y_top)
    ops.patch("quad", MAT_COVER_LOWER, 2, 1,
              sec2_core_z_right, sec2_core_y_top,
              sec2_core_z_right, sec2_core_y_bot,
              sec2_z3, sec2_y3,
              sec2_z4, sec2_y4)
    ops.layer("straight", MAT_REBAR_LOWER, n_bars_sec2, As_sec2,
              sec2_core_y_top, sec2_core_z_left,
              sec2_core_y_top, sec2_core_z_right)
    ops.layer("straight", MAT_REBAR_LOWER, n_bars_sec2, As_sec2,
              sec2_core_y_bot, sec2_core_z_left,
              sec2_core_y_bot, sec2_core_z_right)


# -- 7. FRAME NODES ----------------------------------------------------------------

def _create_frame_nodes() -> None:
    """Create 15 frame nodes (ndf=3) with lumped masses."""
    # Above ground: columns at x=0, 7, 14 m; stories at y=0, 3.6, 7.2 m
    ops.node(1,  frame_x_left,   0.0)
    ops.node(2,  frame_x_left,   story_h1)
    ops.node(3,  frame_x_left,   story_h1 + story_h2)
    ops.node(4,  frame_x_center, 0.0)
    ops.node(5,  frame_x_center, story_h1)
    ops.node(6,  frame_x_center, story_h1 + story_h2)
    ops.node(7,  frame_x_right,  0.0)
    ops.node(8,  frame_x_right,  story_h1)
    ops.node(9,  frame_x_right,  story_h1 + story_h2)

    # Underground: columns at x=0, 7, 14 m; y=-2.4, -1.2 m
    ops.node(10, frame_x_left,   ug_level2)  # y=-2.4
    ops.node(11, frame_x_left,   ug_level1)  # y=-1.2
    ops.node(12, frame_x_center, ug_level2)
    ops.node(13, frame_x_center, ug_level1)
    ops.node(14, frame_x_right,  ug_level2)
    ops.node(15, frame_x_right,  ug_level1)


# -- 8. FRAME BOUNDARY CONDITIONS --------------------------------------------------

def _apply_frame_bcs() -> None:
    """Lumped masses at frame nodes. No fixity (support via soil equalDOF)."""
    # Above-ground masses
    ops.mass(1, framemass1, framemass1, 0.0)
    ops.mass(2, framemass1, framemass1, 0.0)
    ops.mass(3, framemass1, framemass1, 0.0)
    ops.mass(4, framemass2, framemass2, 0.0)
    ops.mass(5, framemass2, framemass2, 0.0)
    ops.mass(6, framemass2, framemass2, 0.0)
    ops.mass(7, framemass1, framemass1, 0.0)
    ops.mass(8, framemass1, framemass1, 0.0)
    ops.mass(9, framemass1, framemass1, 0.0)

    # Underground masses
    ops.mass(10, framemass3, framemass3, 0.0)
    ops.mass(11, framemass3, framemass3, 0.0)
    ops.mass(12, framemass3, framemass3, 0.0)
    ops.mass(13, framemass3, framemass3, 0.0)
    ops.mass(14, framemass3, framemass3, 0.0)
    ops.mass(15, framemass3, framemass3, 0.0)


# -- 9. FRAME ELEMENTS -------------------------------------------------------------

def _create_frame_elements() -> None:
    """16 dispBeamColumn elements with Legendre integration.

    Column sections: center=1 (600x500), sides=2 (500x500)
    Beam section: 3 (500x400)
    Underground columns: center=4 (600x500), sides=5 (500x500)
    """
    ops.geomTransf("Linear", TRANS_TAG)

    # Create beam integrations for each section type
    ops.beamIntegration("Legendre", INTEG_SEC1, SEC_COL_UPPER_BIG,   n_ip)
    ops.beamIntegration("Legendre", INTEG_SEC2, SEC_COL_UPPER_SIDE,  n_ip)
    ops.beamIntegration("Legendre", INTEG_SEC3, SEC_BEAM,            n_ip)
    ops.beamIntegration("Legendre", INTEG_SEC4, SEC_COL_LOWER_BIG,   n_ip)
    ops.beamIntegration("Legendre", INTEG_SEC5, SEC_COL_LOWER_SIDE,  n_ip)

    # Left column (section 2): 1->2, 2->3
    ops.element("dispBeamColumn", 1, 1, 2, TRANS_TAG, INTEG_SEC2)
    ops.element("dispBeamColumn", 2, 2, 3, TRANS_TAG, INTEG_SEC2)

    # Center column (section 1): 4->5, 5->6
    ops.element("dispBeamColumn", 3, 4, 5, TRANS_TAG, INTEG_SEC1)
    ops.element("dispBeamColumn", 4, 5, 6, TRANS_TAG, INTEG_SEC1)

    # Right column (section 2): 7->8, 8->9
    ops.element("dispBeamColumn", 5, 7, 8, TRANS_TAG, INTEG_SEC2)
    ops.element("dispBeamColumn", 6, 8, 9, TRANS_TAG, INTEG_SEC2)

    # Floor 1 beams (section 3): 2->5, 5->8
    ops.element("dispBeamColumn", 7, 2, 5, TRANS_TAG, INTEG_SEC3)
    ops.element("dispBeamColumn", 8, 5, 8, TRANS_TAG, INTEG_SEC3)

    # Floor 2 beams (section 3): 3->6, 6->9
    ops.element("dispBeamColumn", 9, 3, 6, TRANS_TAG, INTEG_SEC3)
    ops.element("dispBeamColumn", 10, 6, 9, TRANS_TAG, INTEG_SEC3)

    # Underground left (section 4): 10->11, 11->1
    ops.element("dispBeamColumn", 11, 10, 11, TRANS_TAG, INTEG_SEC4)
    ops.element("dispBeamColumn", 12, 11, 1, TRANS_TAG, INTEG_SEC4)

    # Underground center (section 5): 12->13, 13->4
    ops.element("dispBeamColumn", 13, 12, 13, TRANS_TAG, INTEG_SEC5)
    ops.element("dispBeamColumn", 14, 13, 4, TRANS_TAG, INTEG_SEC5)

    # Underground right (section 4): 14->15, 15->7
    ops.element("dispBeamColumn", 15, 14, 15, TRANS_TAG, INTEG_SEC4)
    ops.element("dispBeamColumn", 16, 15, 7, TRANS_TAG, INTEG_SEC4)


# -- 10. SOIL MATERIALS ------------------------------------------------------------

def _define_soil_materials() -> None:
    """MultiYieldSurfaceClay nDMaterials for soil layers and structural concrete."""
    # Structural concrete surrogate
    ops.nDMaterial("MultiYieldSurfaceClay", MAT_SOIL_STRUCTURAL, 2,
                   soil_rho, soil100_Gr, soil100_Br, soil100_cohesion,
                   soil100_peak, soil100_phi, soil100_refPress,
                   soil100_pressDep, soil100_nSurf)

    # Soil layers 1-4 (weakest at top, strongest at bottom)
    soil_layers = [
        (MAT_SOIL_LAYER1, soil101_Gr, soil101_Br, soil101_cohesion, soil101_peak),
        (MAT_SOIL_LAYER2, soil102_Gr, soil102_Br, soil102_cohesion, soil102_peak),
        (MAT_SOIL_LAYER3, soil103_Gr, soil103_Br, soil103_cohesion, soil103_peak),
        (MAT_SOIL_LAYER4, soil104_Gr, soil104_Br, soil104_cohesion, soil104_peak),
    ]
    for tag, Gr, Br, cohesion, peak in soil_layers:
        ops.nDMaterial("MultiYieldSurfaceClay", tag, 2,
                       soil_rho, Gr, Br, cohesion, peak)


# -- 11. SOIL NODES ----------------------------------------------------------------

def _create_soil_nodes() -> None:
    """Create 95 soil nodes (ndf=2) in a 19x5 grid."""
    for row in range(n_soil_y):
        for col in range(n_soil_x):
            tag = _soil_node_index(col, row)
            ops.node(tag, soil_x_array[col], soil_y_array[row])


# -- 12. SOIL BOUNDARY CONDITIONS --------------------------------------------------

def _apply_soil_bcs() -> None:
    """Fix base of soil mesh (row 0, y=-7.2 m)."""
    for col in range(n_soil_x):
        tag = _soil_node_index(col, 0)
        ops.fix(tag, 1, 1)


# -- 13. SOIL ELEMENTS -------------------------------------------------------------

def _create_soil_elements() -> None:
    """72 quadWithSensitivity elements (4 rows x 18 cols), PlaneStrain.

    Each quad connects nodes: bottom-left, bottom-right, top-right, top-left.
    """
    for ele_row in range(n_soil_y - 1):   # 0..3
        node_row_bot = ele_row
        node_row_top = ele_row + 1
        for col in range(n_soil_x - 1):   # 0..17
            ele_tag = _soil_ele_tag(ele_row, col)
            mat_tag = _soil_mat_for_position(ele_row, col)

            n_bl = _soil_node_index(col,     node_row_bot)
            n_br = _soil_node_index(col + 1, node_row_bot)
            n_tr = _soil_node_index(col + 1, node_row_top)
            n_tl = _soil_node_index(col,     node_row_top)

            ops.element("quadWithSensitivity", ele_tag,
                        n_bl, n_br, n_tr, n_tl,
                        quad_thickness, "PlaneStrain", mat_tag,
                        0.0, quad_density, 0.0, quad_body_force_y)


# -- 14. TIE MODELS ----------------------------------------------------------------

def _tie_frame_to_soil() -> None:
    """equalDOF ties: soil lateral periodicity + frame-to-soil connections."""
    # Lateral periodicity ties (5 pairs of soil boundary nodes)
    lateral_pairs = [
        (16, 34),    # bottom row
        (35, 53),    # row 2
        (54, 72),    # row 3
        (73, 91),    # row 4
        (92, 110),   # surface row
    ]
    for left, right in lateral_pairs:
        ops.equalDOF(left, right, 1, 2)

    # Frame-to-soil ties
    # Frame node -> soil node at same (x,y) location
    frame_to_soil = [
        (1,  97),   # left column base (x=0, y=0)
        (11, 78),   # left column mid (x=0, y=-1.2)
        (10, 59),   # left column base (x=0, y=-2.4)
        (4,  101),  # center column base (x=7, y=0)
        (13, 82),   # center column mid (x=7, y=-1.2)
        (12, 63),   # center column base (x=7, y=-2.4)
        (7,  105),  # right column base (x=14, y=0)
        (15, 86),   # right column mid (x=14, y=-1.2)
        (14, 67),   # right column base (x=14, y=-2.4)
    ]
    for frame_node, soil_node in frame_to_soil:
        ops.equalDOF(frame_node, soil_node, 1, 2)


# -- 15. OUTPUT DATABASE (ODB) -----------------------------------------------------

def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise ODB after model is fully built."""
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=1)
    odb.save_model_data()
    return odb


# -- 16. RECORDERS ----------------------------------------------------------------

def setup_recorders(output_dir: Path) -> None:
    """Direct file recorders matching Tcl outputs."""
    out = output_dir

    # Node displacement recorders
    ops.recorder("Node", "-file", str(out / "disp6.out"),
                 "-time", "-node", 6, "-dof", 1, 2, "disp")
    ops.recorder("Node", "-file", str(out / "disp5.out"),
                 "-time", "-node", 5, "-dof", 1, 2, "disp")
    ops.recorder("Node", "-file", str(out / "disp4.out"),
                 "-time", "-node", 4, "-dof", 1, 2, "disp")

    # Soil surface node recorders
    soil_surface_nodes = [6, 5, 4, 13, 12, 99, 80, 61, 42, 23]
    for tag in soil_surface_nodes:
        ops.recorder("Node", "-file", str(out / f"node{tag}.out"),
                     "-time", "-node", tag, "-dof", 1, 2, "disp")

    # Section force/deformation recorders
    ops.recorder("Element", "-ele", 1, 2, "-file", str(out / "Deformation12.out"),
                 "-time", "section", 2, "deformations")
    ops.recorder("Element", "-ele", 1, 2, "-file", str(out / "Force12.out"),
                 "-time", "section", 2, "force")
    ops.recorder("Element", "-ele", 3, 4, "-file", str(out / "Deformation34.out"),
                 "-time", "section", 2, "deformations")
    ops.recorder("Element", "-ele", 3, 4, "-file", str(out / "Force34.out"),
                 "-time", "section", 2, "force")
    ops.recorder("Element", "-ele", 7, 9, "-file", str(out / "Deformation79.out"),
                 "-time", "section", 3, "deformations")
    ops.recorder("Element", "-ele", 7, 9, "-file", str(out / "Force79.out"),
                 "-time", "section", 3, "force")

    # Fiber stress/strain recorders (beam element 7, section 3)
    ops.recorder("Element", "-ele", 7, "-time",
                 "-file", str(out / "steelstress7.out"),
                 "section", 3, "fiber", -0.2286*m, 0.2286*m, "stress")
    ops.recorder("Element", "-ele", 7, "-time",
                 "-file", str(out / "steelstrain7.out"),
                 "section", 3, "fiber", -0.2286*m, 0.2286*m, "strain")
    ops.recorder("Element", "-ele", 7, "-time",
                 "-file", str(out / "concretestress7.out"),
                 "section", 3, "fiber", 0.0, 0.0, "stress")
    ops.recorder("Element", "-ele", 7, "-time",
                 "-file", str(out / "concretestrain7.out"),
                 "section", 3, "fiber", 0.0, 0.0, "strain")

    # Soil element stress/strain recorders (material 2 = second integration point)
    soil_stress_elements = [23, 41, 59, 77]
    for ele in soil_stress_elements:
        ops.recorder("Element", "-ele", ele, "-time",
                     "-file", str(out / f"stress{ele}.out"),
                     "material", 2, "stress")
    ops.recorder("Element", "-ele", 37, "-time",
                 "-file", str(out / "stress37.out"),
                 "material", 2, "stress")
    ops.recorder("Element", "-ele", 37, "-time",
                 "-file", str(out / "strain37.out"),
                 "material", 2, "strain")


# -- 17. LOADING -------------------------------------------------------------------

def define_gravity_loads() -> None:
    """Apply vertical gravity loads to frame nodes (self-weight)."""
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 2, 1)

    # Above-ground column loads
    for node in range(1, 10):
        if node in (4, 5, 6):
            ops.load(node, 0.0, upperload2, 0.0)     # center columns: 300 kN
        else:
            ops.load(node, 0.0, upperload1, 0.0)     # side columns: 150 kN

    # Underground column loads
    for node in range(10, 16):
        ops.load(node, 0.0, download3, 0.0)          # 40 kN


def define_ground_motion() -> tuple:
    """Define El Centro ground motion in X-direction.

    File values in m/s^2; convert to mm/s^2 (x1000) and apply factor 3.
    Returns (dt, npts).
    """
    path_gm = gm_dir / gm_file
    if not path_gm.exists():
        raise FileNotFoundError(f"Ground motion file not found: {path_gm}")
    accel_raw = np.loadtxt(path_gm)

    # File: m/s^2. Conversion: x1000 (m->mm) x gm_factor = x3000
    gm_scale = gm_factor * 1000.0

    ops.timeSeries("Path", 101, "-dt", gm_dt, "-values", *accel_raw,
                   "-factor", gm_scale)
    ops.pattern("UniformExcitation", 1, 1, "-accel", 101)

    return gm_dt, gm_npts


# -- 18. ANALYSIS ------------------------------------------------------------------

_peak_disp_x = 0.0
_peak_disp_y = 0.0


def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10) -> None:
    """Apply gravity loads (frame self-weight + soil body forces)."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.test("NormDispIncr", 1.0e-6, 25, 2)
    ops.algorithm("Newton")
    ops.analysis("Static")

    for i in range(n_steps):
        ok = ops.analyze(1)
        if ok < 0:
            print(f"  Gravity step {i+1} failed to converge.")
            break
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()
    print("Gravity analysis complete.")


def run_dynamic(
    odb: "opst.post.CreateODB",
    dt: float,
    n_steps: int,
    odb_every_n: int = 10,
) -> None:
    """Run transient dynamic analysis with Newmark integration.

    Uses opstool SmartAnalyze for robust convergence.
    """
    global _peak_disp_x, _peak_disp_y

    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("Newmark", newmark_gamma, newmark_beta)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )

    segs = analysis.transient_split(n_steps)
    t_current = 0.0
    step_count = 0

    for i, seg in enumerate(segs):
        try:
            ok = analysis.TransientAnalyze(dt)
        except UnicodeEncodeError:
            ok = 0
        if ok < 0:
            print(f"  Dynamic analysis failed at t = {t_current:.3f} s (step {i})")
            break
        t_current += dt
        step_count += 1

        if i % odb_every_n == 0:
            try:
                odb.fetch_response_step()
            except Exception:
                pass
            # Track peak roof displacement (node 6 = center top)
            _peak_disp_x = max(_peak_disp_x, abs(ops.nodeDisp(6, 1)))
            _peak_disp_y = max(_peak_disp_y, abs(ops.nodeDisp(6, 2)))

    try:
        analysis.close()
    except UnicodeEncodeError:
        pass

    print(f"  Completed {step_count} steps (t_final = {t_current:.3f} s)")


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + dynamic, return ODB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    ops.wipe()
    build_model()
    setup_recorders(output_dir)

    vis_nodes(output_dir)
    vis_model(output_dir)

    odb = create_odb(output_dir)

    define_gravity_loads()
    vis_loads(output_dir)

    print("Running static preload (gravity) ...")
    run_gravity(odb, n_steps=n_steps_gravity)

    gm_dt_actual, gm_nsteps = define_ground_motion()
    vis_pre_analysis(output_dir)

    print(f"Running dynamic analysis ({gm_nsteps} steps, dt={analysis_dt:.3f} s) ...")
    run_dynamic(odb, analysis_dt, gm_nsteps, odb_every_n=odb_every_n)

    return odb


# -- 19. POST-PROCESSING -----------------------------------------------------------

def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> dict:
    """Flush ODB, write EDPs, generate visualizations."""
    odb.save_response()

    total_height = story_h1 + story_h2
    edp_values = {
        "1-PRD-1":    _peak_disp_x,
        "1-PRD-2":    _peak_disp_y,
        "1-PID-1-1":  _peak_disp_x / total_height,
        "1-PID-1-2":  _peak_disp_y / total_height,
        "collapse_status": 0,
    }

    import json
    edp_file = output_dir / "EDP.json"
    edp_list = [{"name": k, "value": v} for k, v in edp_values.items()]
    with open(edp_file, "w") as f:
        json.dump({"EDP": edp_list}, f, indent=2)
    print(f"EDP file written: {edp_file}")

    if not _headless():
        try:
            fig_defo = opst.vis.plotly.plot_nodal_responses(
                odb_tag=1, step="absMax", defo_scale=True,
                resp_type="disp", resp_dof="UX",
            )
            fig_defo.write_html(str(output_dir / "vis_05_deformed_peak.html"))
            print("  -> vis_05_deformed_peak.html")

            fig_slider = opst.vis.plotly.plot_nodal_responses(
                odb_tag=1, slides=True, defo_scale=True,
                resp_type="disp", resp_dof="UX",
            )
            fig_slider.write_html(str(output_dir / "vis_06_deformed_slider.html"))
            print("  -> vis_06_deformed_slider.html")
        except Exception as e:
            print(f"  Visualization skipped: {e}")

    return edp_values


# -- 20. MAIN ----------------------------------------------------------------------

if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    edps = post_process(odb, output_dir)
    print(f"\nExtracted {len(edps)} EDPs.")
    print(f"  Peak roof X disp: {_peak_disp_x:.1f} mm")
    print(f"  Peak roof Y disp: {_peak_disp_y:.1f} mm")
