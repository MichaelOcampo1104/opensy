# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 4-Story Steel Special Moment Frame (SMF4B)
UniqueID : elkady2019
Author   : Dr. Ahmed Elkady (original Tcl); converted to Python by OpenSeesPy Standardisation Agent
Date     : 2026-05-24
Purpose  : Nonlinear dynamic (EQ) and pushover (PO) analysis of a 4-story 3-bay steel
           special moment frame (SMF) with panel zones, IMK springs, and an elastic gravity
           frame, used to study seismic collapse capacity of steel MRFs.
Ref      : Elkady, A. and Lignos, D.G. (2014). Earthquake Engineering & Structural Dynamics 43(13).
           Lignos, D.G. and Krawinkler, H. (2011). Journal of Structural Engineering 137(11).
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

# Add standards/ to path if running standalone
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo, _headless

# Add model folder to path for helper modules
sys.path.insert(0, str(Path(__file__).parent))
from constructpanel_rectangle import construct_panel_rectangle
from spring_pz import spring_pz
from spring_imk import spring_imk
from spring_rigid import spring_rigid
from spring_zero import spring_zero
from dynamicanalysiscollapsesolverx import dynamic_analysis_collapse_solver

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Geometric transformation tags
TRANS_LINEAR  = 1
TRANS_PDELTA  = 2
TRANS_COROT   = 3

# Basic material tags
MAT_FLEXIBLE  = 9    # very low stiffness (near-zero)
MAT_RIGID     = 99   # very high stiffness
MAT_UVC       = 666  # Voce-Chaboche (UVCuniaxial) steel

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# --- Structural configuration ---
N_STORY = 4
N_BAY   = 3

# --- Material ---
E   = 29_000.0 * ksi    # Young's modulus         [N/mm²]  originally 29000 ksi
MU  = 0.30               # Poisson's ratio          [-]
FY  = 55.0 * ksi         # Expected yield stress   [N/mm²]  originally 55.0 ksi

# --- Analysis flags (set to 1 to run) ---
RUN_EQ  = 1   # Dynamic earthquake analysis
RUN_PO  = 0   # Pushover analysis
RUN_ELF = 0   # Equivalent lateral force (not implemented)

# --- Composite beam factor ---
COMPOSITE    = 0
COMP_I       = 1.400   # composite stiffness amplifier
COMP_I_GC    = 1.400

# --- Fiber element / integration ---
N_SEGMENTS   = 8
INITIAL_GI   = 0.001
N_INTEG      = 5

# --- Stiff elements ---
A_STIFF = 1_000.0 * inch**2       # originally 1000 in²
I_STIFF = 100_000.0 * inch**4     # originally 100000 in⁴

# --- Uncertainty (log-std = 1e-9 → deterministic) ---
SIGMA_IMK_COL  = [1e-9] * 9
SIGMA_IMK_BEAM = [1e-9] * 9
SIGMA_PZ       = [1e-9] * 4
SIGMA_FY       = 1e-9
SIGMA_ZETA     = 1e-9

# --- Rayleigh damping ---
ZETA       = 0.020   # target critical damping ratio
DAMP_MODE_I = 1
DAMP_MODE_J = 3

# --- Stiffness modifiers (modified elastic beam, Gupta & Krawinkler 1999) ---
_n    = 10.0
K44_2 = 6.0 * (1.0 + _n) / (2.0 + 3.0 * _n)
K11_2 = (1.0 + 2.0 * _n) * K44_2 / (1.0 + _n)
K33_2 = (1.0 + 2.0 * _n) * K44_2 / (1.0 + _n)
K44_1 = 6.0 * _n / (1.0 + 3.0 * _n)
K11_1 = (1.0 + 2.0 * _n) * K44_1 / (1.0 + _n)
K33_1 = 2.0 * K44_1

# ── 3a. GRID COORDINATES (all in mm, originally in inches) ──────────────────
# Floor elevations
FLOOR1 = 0.0       * inch              # originally 0.0 in
FLOOR2 = 180.00    * inch              # originally 180.00 in
FLOOR3 = 336.00    * inch              # originally 336.00 in
FLOOR4 = 492.00    * inch              # originally 492.00 in
FLOOR5 = 648.00    * inch              # originally 648.00 in  (roof)

# Column grid lines
AXIS1  = 0.0       * inch              # originally 0.0 in
AXIS2  = 240.00    * inch              # originally 240.00 in
AXIS3  = 480.00    * inch              # originally 480.00 in
AXIS4  = 720.00    * inch              # originally 720.00 in
AXIS5  = 960.00    * inch              # originally 960.00 in  (EGF)
AXIS6  = 1_200.00  * inch              # originally 1200.00 in (EGF)

H_BUILDING = 648.00 * inch            # total building height [mm]
W_FRAME    = 720.00 * inch            # total frame width     [mm]

# --- Story heights (for collapse drift check) ---
H1_STORY   = 180.00 * inch            # first story height  [mm]
H_TYP      = 156.00 * inch            # typical story height [mm]

# ── 3b. SECTION DIMENSIONS (mm, originally inches) ──────────────────────────
# Roof / Floor 5 columns  W14×68 : d=23.70 in → mm
D_COL_5  = 23.70 * inch
# Floor 4–5 columns  W14×68
D_COL_4  = 23.70 * inch
# Floor 2–4 columns  W14×132 : d=24.50 in → mm
D_COL_3  = 24.50 * inch
D_COL_2  = 24.50 * inch

# Beam depths
D_BEAM_5 = 21.10 * inch   # roof beam W21×68
D_BEAM_4 = 21.10 * inch   # floor 4 beam W21×68
D_BEAM_3 = 21.20 * inch   # floor 3 beam W21×73
D_BEAM_2 = 21.20 * inch   # floor 2 beam W21×73

# --- RBS cut distances from column face ---
L_RBS5 = 0.625 * (6.56 * inch) + 0.750 * (21.10 * inch) / 2.0
L_RBS4 = 0.625 * (6.56 * inch) + 0.750 * (21.10 * inch) / 2.0
L_RBS3 = 0.625 * (8.30 * inch) + 0.750 * (21.20 * inch) / 2.0
L_RBS2 = 0.625 * (8.30 * inch) + 0.750 * (21.20 * inch) / 2.0

# --- Gravity (for mass computation) ---
G_ACCEL = 386.10 * inch              # gravitational acceleration [mm/s²]  originally 386.10 in/s²

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe the model and initialise a 2D / 3-DOF-per-node model.

    Args:
        None
    """
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Define basic uniaxial materials.

    Three materials are always required:
    - MAT_FLEXIBLE (9): near-zero stiffness (gravity column rotation release)
    - MAT_RIGID (99): very high stiffness (rigid links / splice springs)
    - MAT_UVC (666): Voce-Chaboche cyclic steel (UVCuniaxial)

    All stress values converted from ksi → MPa.
    """
    ops.uniaxialMaterial("Elastic", MAT_FLEXIBLE, 1.0e-9)
    ops.uniaxialMaterial("Elastic", MAT_RIGID,    1_000_000_000.0)  # rigid

    # Voce-Chaboche (UVCuniaxial)
    # Originally: 29000 ksi, 55 ksi, with hardening params unchanged (dimensionless ratios)
    ops.uniaxialMaterial(
        "UVCuniaxial", MAT_UVC,
        E,          # Young's modulus [MPa]
        FY,         # Initial yield stress [MPa]
        18.0,       # isotropic hardening coefficient C_K (dimensionless)
        10.0,       # isotropic hardening coefficient gamma_K (dimensionless)
        0.0,        # isotropic saturation Qinf
        1.0,        # isotropic growth b
        2,          # number of backstress terms
        3_500.0,  # C1  originally 3500 ksi → MPa
        180.0,          # gamma1 (dimensionless)
        345.0,   # C2  originally 345 ksi → MPa
        10.0,           # gamma2 (dimensionless)
    )


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    """No explicit fiber sections for this elastic-spring model.

    All nonlinearity is lumped in zero-length IMK springs and PZ springs.
    Cross-section properties are passed directly to ModElasticBeam2d /
    elasticBeamColumn commands via parameters.
    """
    pass


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Define all nodes for the 4-story SMF + EGF.

    Node numbering convention (matches original Tcl):
    - Ground support nodes: 110, 120, … 160
    - EGF grid nodes: floor × 100 + axis (e.g. 550, 560, 450, …)
    - MF column nodes: floor × 100 + axis × 10 + offset (e.g. 511, 413 …)
    - Panel zone beam/column nodes: created by construct_panel_rectangle
    - Beam spring nodes: floor × 1000 + axis × 100 + offset
    - Column splice nodes: 103172, 103171, …
    """
    # ── Support / ground-level nodes ────────────────────────────────────────
    ops.node(110, AXIS1, FLOOR1)
    ops.node(120, AXIS2, FLOOR1)
    ops.node(130, AXIS3, FLOOR1)
    ops.node(140, AXIS4, FLOOR1)
    ops.node(150, AXIS5, FLOOR1)
    ops.node(160, AXIS6, FLOOR1)

    # ── EGF column grid nodes (shared with truss floor links) ────────────────
    for floor_tag, y_floor in [(5, FLOOR5), (4, FLOOR4), (3, FLOOR3), (2, FLOOR2)]:
        ops.node(floor_tag * 100 + 50, AXIS5, y_floor)
        ops.node(floor_tag * 100 + 60, AXIS6, y_floor)

    # ── EGF column upper/lower nodes ─────────────────────────────────────────
    ops.node(551, AXIS5, FLOOR5);  ops.node(561, AXIS6, FLOOR5)
    ops.node(453, AXIS5, FLOOR4);  ops.node(463, AXIS6, FLOOR4)
    ops.node(451, AXIS5, FLOOR4);  ops.node(461, AXIS6, FLOOR4)
    ops.node(353, AXIS5, FLOOR3);  ops.node(363, AXIS6, FLOOR3)
    ops.node(351, AXIS5, FLOOR3);  ops.node(361, AXIS6, FLOOR3)
    ops.node(253, AXIS5, FLOOR2);  ops.node(263, AXIS6, FLOOR2)
    ops.node(251, AXIS5, FLOOR2);  ops.node(261, AXIS6, FLOOR2)
    ops.node(153, AXIS5, FLOOR1);  ops.node(163, AXIS6, FLOOR1)

    # ── EGF beam end-nodes ───────────────────────────────────────────────────
    ops.node(554, AXIS5, FLOOR5);  ops.node(562, AXIS6, FLOOR5)
    ops.node(454, AXIS5, FLOOR4);  ops.node(462, AXIS6, FLOOR4)
    ops.node(354, AXIS5, FLOOR3);  ops.node(362, AXIS6, FLOOR3)
    ops.node(254, AXIS5, FLOOR2);  ops.node(262, AXIS6, FLOOR2)

    # ── MF column nodes: above (+3) and below (+1) panel zones ───────────────
    # Floor 5 (below panel = ..11)
    for ax, x in [(1, AXIS1), (2, AXIS2), (3, AXIS3), (4, AXIS4)]:
        ops.node(500 + ax * 10 + 1, x, FLOOR5 - D_BEAM_5 / 2.0)
    # Floor 4 above (+13) and below (+11)
    for ax, x in [(1, AXIS1), (2, AXIS2), (3, AXIS3), (4, AXIS4)]:
        ops.node(400 + ax * 10 + 3, x, FLOOR4 + D_BEAM_5 / 2.0)
        ops.node(400 + ax * 10 + 1, x, FLOOR4 - D_BEAM_5 / 2.0)
    # Floor 3 above (+13) and below (+11)
    for ax, x in [(1, AXIS1), (2, AXIS2), (3, AXIS3), (4, AXIS4)]:
        ops.node(300 + ax * 10 + 3, x, FLOOR3 + D_BEAM_3 / 2.0)
        ops.node(300 + ax * 10 + 1, x, FLOOR3 - D_BEAM_3 / 2.0)
    # Floor 2 above (+13) and below (+11)
    for ax, x in [(1, AXIS1), (2, AXIS2), (3, AXIS3), (4, AXIS4)]:
        ops.node(200 + ax * 10 + 3, x, FLOOR2 + D_BEAM_3 / 2.0)
        ops.node(200 + ax * 10 + 1, x, FLOOR2 - D_BEAM_3 / 2.0)
    # Ground-level column base nodes
    for ax, x in [(1, AXIS1), (2, AXIS2), (3, AXIS3), (4, AXIS4)]:
        ops.node(100 + ax * 10 + 3, x, FLOOR1)

    # ── MF beam RBS nodes (panel zone faces — left/right of each column) ─────
    # Floor 5  d_col = D_COL_5 = 23.70 in
    ops.node(514,  AXIS1 + L_RBS5 + D_COL_5 / 2.0, FLOOR5)
    ops.node(522,  AXIS2 - L_RBS5 - D_COL_5 / 2.0, FLOOR5)
    ops.node(524,  AXIS2 + L_RBS5 + D_COL_5 / 2.0, FLOOR5)
    ops.node(532,  AXIS3 - L_RBS5 - D_COL_5 / 2.0, FLOOR5)
    ops.node(534,  AXIS3 + L_RBS5 + D_COL_5 / 2.0, FLOOR5)
    ops.node(542,  AXIS4 - L_RBS5 - D_COL_5 / 2.0, FLOOR5)
    # Floor 4  d_col = D_COL_4 = 24.50 in
    ops.node(414,  AXIS1 + L_RBS4 + 24.50 * inch / 2.0, FLOOR4)
    ops.node(422,  AXIS2 - L_RBS4 - 24.50 * inch / 2.0, FLOOR4)
    ops.node(424,  AXIS2 + L_RBS4 + 24.50 * inch / 2.0, FLOOR4)
    ops.node(432,  AXIS3 - L_RBS4 - 24.50 * inch / 2.0, FLOOR4)
    ops.node(434,  AXIS3 + L_RBS4 + 24.50 * inch / 2.0, FLOOR4)
    ops.node(442,  AXIS4 - L_RBS4 - 24.50 * inch / 2.0, FLOOR4)
    # Floor 3  d_col = D_COL_3 = 24.50 in
    ops.node(314,  AXIS1 + L_RBS3 + 24.50 * inch / 2.0, FLOOR3)
    ops.node(322,  AXIS2 - L_RBS3 - 24.50 * inch / 2.0, FLOOR3)
    ops.node(324,  AXIS2 + L_RBS3 + 24.50 * inch / 2.0, FLOOR3)
    ops.node(332,  AXIS3 - L_RBS3 - 24.50 * inch / 2.0, FLOOR3)
    ops.node(334,  AXIS3 + L_RBS3 + 24.50 * inch / 2.0, FLOOR3)
    ops.node(342,  AXIS4 - L_RBS3 - 24.50 * inch / 2.0, FLOOR3)
    # Floor 2  d_col = D_COL_2 = 24.50 in
    ops.node(214,  AXIS1 + L_RBS2 + 24.50 * inch / 2.0, FLOOR2)
    ops.node(222,  AXIS2 - L_RBS2 - 24.50 * inch / 2.0, FLOOR2)
    ops.node(224,  AXIS2 + L_RBS2 + 24.50 * inch / 2.0, FLOOR2)
    ops.node(232,  AXIS3 - L_RBS2 - 24.50 * inch / 2.0, FLOOR2)
    ops.node(234,  AXIS3 + L_RBS2 + 24.50 * inch / 2.0, FLOOR2)
    ops.node(242,  AXIS4 - L_RBS2 - 24.50 * inch / 2.0, FLOOR2)

    # ── Beam spring (zero-length IMK) nodes — co-located with RBS nodes ──────
    # Floor 5
    ops.node(5140, AXIS1 + L_RBS5 + D_COL_5 / 2.0, FLOOR5)
    ops.node(5220, AXIS2 - L_RBS5 - D_COL_5 / 2.0, FLOOR5)
    ops.node(5240, AXIS2 + L_RBS5 + D_COL_5 / 2.0, FLOOR5)
    ops.node(5320, AXIS3 - L_RBS5 - D_COL_5 / 2.0, FLOOR5)
    ops.node(5340, AXIS3 + L_RBS5 + D_COL_5 / 2.0, FLOOR5)
    ops.node(5420, AXIS4 - L_RBS5 - D_COL_5 / 2.0, FLOOR5)
    # Floor 4
    ops.node(4140, AXIS1 + L_RBS4 + 24.50 * inch / 2.0, FLOOR4)
    ops.node(4220, AXIS2 - L_RBS4 - 24.50 * inch / 2.0, FLOOR4)
    ops.node(4240, AXIS2 + L_RBS4 + 24.50 * inch / 2.0, FLOOR4)
    ops.node(4320, AXIS3 - L_RBS4 - 24.50 * inch / 2.0, FLOOR4)
    ops.node(4340, AXIS3 + L_RBS4 + 24.50 * inch / 2.0, FLOOR4)
    ops.node(4420, AXIS4 - L_RBS4 - 24.50 * inch / 2.0, FLOOR4)
    # Floor 3
    ops.node(3140, AXIS1 + L_RBS3 + 24.50 * inch / 2.0, FLOOR3)
    ops.node(3220, AXIS2 - L_RBS3 - 24.50 * inch / 2.0, FLOOR3)
    ops.node(3240, AXIS2 + L_RBS3 + 24.50 * inch / 2.0, FLOOR3)
    ops.node(3320, AXIS3 - L_RBS3 - 24.50 * inch / 2.0, FLOOR3)
    ops.node(3340, AXIS3 + L_RBS3 + 24.50 * inch / 2.0, FLOOR3)
    ops.node(3420, AXIS4 - L_RBS3 - 24.50 * inch / 2.0, FLOOR3)
    # Floor 2
    ops.node(2140, AXIS1 + L_RBS2 + 24.50 * inch / 2.0, FLOOR2)
    ops.node(2220, AXIS2 - L_RBS2 - 24.50 * inch / 2.0, FLOOR2)
    ops.node(2240, AXIS2 + L_RBS2 + 24.50 * inch / 2.0, FLOOR2)
    ops.node(2320, AXIS3 - L_RBS2 - 24.50 * inch / 2.0, FLOOR2)
    ops.node(2340, AXIS3 + L_RBS2 + 24.50 * inch / 2.0, FLOOR2)
    ops.node(2420, AXIS4 - L_RBS2 - 24.50 * inch / 2.0, FLOOR2)

    # ── Column splice nodes (mid-height of story 3–4, both MF and EGF) ───────
    splice_y = FLOOR3 + 0.50 * 156.0 * inch    # originally Floor3 + 0.5*156 in
    for ax, x in [
        (1, AXIS1), (2, AXIS2), (3, AXIS3), (4, AXIS4),
        (5, AXIS5), (6, AXIS6),
    ]:
        ops.node(103000 + ax * 100 + 72, x, splice_y)   # upper
        ops.node(103000 + ax * 100 + 71, x, splice_y)   # lower


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Apply pinned and roller supports; enforce rigid diaphragm DOF coupling.

    MF column bases: fully fixed (1 1 1).
    EGF column bases: pin in X+Y, free rotation (1 1 0).
    equalDOF: lateral (DOF 1) tied across all panel-zone centroid nodes on each floor.
    """
    # MF supports – fixed
    for n in [110, 120, 130, 140]:
        ops.fix(n, 1, 1, 1)
    # EGF supports – pinned (rotation free)
    for n in [150, 160]:
        ops.fix(n, 1, 1, 0)

    # MF floor-level diaphragm DOF 1 coupling (node 4 = panel centroid)
    # Reference node for each floor is axis-1 panel centroid (405104, 404104, 403104, 402104)
    for floor_code in [5, 4, 3, 2]:
        ref_node = 400_000 + floor_code * 1_000 + 1 * 100 + 4  # e.g., 405104 for floor 5, axis 1
        for ax in [2, 3, 4]:
            target_node = 400_000 + floor_code * 1_000 + ax * 100 + 4  # e.g., 405204 for floor 5, axis 2
            ops.equalDOF(ref_node, target_node, 1)# EGF floor-level diaphragm DOF 1 coupling
    # EGF floor-level diaphragm
    for floor_code in [5, 4, 3, 2]:
        n_axis5 = floor_code * 100 + 50
        n_axis6 = floor_code * 100 + 60
        ops.equalDOF(n_axis5, n_axis6, 1)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def _define_geom_transforms() -> None:
    """Define geometric transformation tags (Linear, PDelta, Corotational)."""
    ops.geomTransf("Linear",      TRANS_LINEAR)
    ops.geomTransf("PDelta",      TRANS_PDELTA)
    ops.geomTransf("Corotational", TRANS_COROT)


def _define_panel_zones() -> None:
    """Construct panel zone nodes + elastic frame elements for all 16 joints."""
    trans = TRANS_PDELTA   # matches Tcl trans_selected = 2

    # Floor 5 — d_col=23.70in, d_beam=21.10in
    for ax, x in [(1, AXIS1), (2, AXIS2), (3, AXIS3), (4, AXIS4)]:
        construct_panel_rectangle(ax, 5, x, FLOOR5, E, A_STIFF, I_STIFF,
                                  23.70 * inch, 21.10 * inch, trans)
    # Floor 4 — d_col=24.50in, d_beam=21.10in
    for ax, x in [(1, AXIS1), (2, AXIS2), (3, AXIS3), (4, AXIS4)]:
        construct_panel_rectangle(ax, 4, x, FLOOR4, E, A_STIFF, I_STIFF,
                                  24.50 * inch, 21.10 * inch, trans)
    # Floor 3 — d_col=24.50in, d_beam=21.20in
    for ax, x in [(1, AXIS1), (2, AXIS2), (3, AXIS3), (4, AXIS4)]:
        construct_panel_rectangle(ax, 3, x, FLOOR3, E, A_STIFF, I_STIFF,
                                  24.50 * inch, 21.20 * inch, trans)
    # Floor 2 — d_col=24.50in, d_beam=21.20in
    for ax, x in [(1, AXIS1), (2, AXIS2), (3, AXIS3), (4, AXIS4)]:
        construct_panel_rectangle(ax, 2, x, FLOOR2, E, A_STIFF, I_STIFF,
                                  24.50 * inch, 21.20 * inch, trans)


def _define_panel_zone_springs() -> None:
    """Attach Skiadopoulos–Elkady–Lignos panel zone springs at all 16 joints.

    Response_ID = 2 for bare steel (COMPOSITE=0).
    """
    ri = 2    # bare steel
    tr = TRANS_LINEAR

    # Floor 5  tw=0.43in  tdp=0  d_col=23.70in d_beam=21.10in tf=0.59in bf=7.04in Ic=1560in⁴ trib=3.5in ts=4in
    for eid, ni, nj, tdp in [
        (905100, 405109, 405110, 0.00 * inch),
        (905200, 405209, 405210, 0.31 * inch),
        (905300, 405309, 405310, 0.31 * inch),
        (905400, 405409, 405410, 0.00 * inch),
    ]:
        spring_pz(eid, ni, nj, E, MU, FY, 0.43 * inch, tdp,
                  23.70 * inch, 21.10 * inch, 0.59 * inch, 7.04 * inch,
                  1_560.0 * inch**4, 3.500 * inch, 4.000 * inch, ri, tr)

    # Floor 4  same column section
    for eid, ni, nj, tdp in [
        (904100, 404109, 404110, 0.00 * inch),
        (904200, 404209, 404210, 0.31 * inch),
        (904300, 404309, 404310, 0.31 * inch),
        (904400, 404409, 404410, 0.00 * inch),
    ]:
        spring_pz(eid, ni, nj, E, MU, FY, 0.43 * inch, tdp,
                  23.70 * inch, 21.10 * inch, 0.59 * inch, 7.04 * inch,
                  1_560.0 * inch**4, 3.500 * inch, 4.000 * inch, ri, tr)

    # Floor 3  W14×132: tw=0.55in tf=0.98in bf=9.0in Ic=3000in⁴
    for eid, ni, nj, tdp in [
        (903100, 403109, 403110, 0.00 * inch),
        (903200, 403209, 403210, 0.31 * inch),
        (903300, 403309, 403310, 0.31 * inch),
        (903400, 403409, 403410, 0.00 * inch),
    ]:
        spring_pz(eid, ni, nj, E, MU, FY, 0.55 * inch, tdp,
                  24.50 * inch, 21.20 * inch, 0.98 * inch, 9.00 * inch,
                  3_000.0 * inch**4, 3.500 * inch, 4.000 * inch, ri, tr)

    # Floor 2  same as floor 3
    for eid, ni, nj, tdp in [
        (902100, 402109, 402110, 0.00 * inch),
        (902200, 402209, 402210, 0.31 * inch),
        (902300, 402309, 402310, 0.31 * inch),
        (902400, 402409, 402410, 0.00 * inch),
    ]:
        spring_pz(eid, ni, nj, E, MU, FY, 0.55 * inch, tdp,
                  24.50 * inch, 21.20 * inch, 0.98 * inch, 9.00 * inch,
                  3_000.0 * inch**4, 3.500 * inch, 4.000 * inch, ri, tr)


def _define_mf_elastic_columns() -> None:
    """ModElasticBeam2d column elements for the 4-story MF.

    Cross-sections (A in², I in⁴ — converted to mm² and mm⁴):
      Stories 3–5  W14×68 : A=18.3in², I=1560in⁴
      Stories 1–2  W14×132: A=30.3in², I=3000in⁴
    """
    trans = TRANS_PDELTA
    # Story 4 (Floor4→Floor5)
    for eid, ni, nj in [
        (604100, 413, 511), (604200, 423, 521),
        (604300, 433, 531), (604400, 443, 541),
    ]:
        ops.element("ModElasticBeam2d", eid, ni, nj,
                    18.3 * inch**2, E,
                    (_n + 1) / _n * 1_560.0 * inch**4,
                    K11_2, K33_2, K44_2, trans)

    # Story 3 upper half (splice → floor4-bottom)
    for eid, ni, nj in [
        (603102, 103172, 411), (603202, 103272, 421),
        (603302, 103372, 431), (603402, 103472, 441),
    ]:
        ops.element("ModElasticBeam2d", eid, ni, nj,
                    18.3 * inch**2, E,
                    (_n + 1) / _n * 1_560.0 * inch**4,
                    K33_1, K11_1, K44_1, trans)

    # Story 3 lower half (floor3-top → splice)
    for eid, ni, nj in [
        (603101, 313, 103171), (603201, 323, 103271),
        (603301, 333, 103371), (603401, 343, 103471),
    ]:
        ops.element("ModElasticBeam2d", eid, ni, nj,
                    30.3 * inch**2, E,
                    (_n + 1) / _n * 3_000.0 * inch**4,
                    K33_1, K11_1, K44_1, trans)

    # Story 2
    for eid, ni, nj in [
        (602100, 213, 311), (602200, 223, 321),
        (602300, 233, 331), (602400, 243, 341),
    ]:
        ops.element("ModElasticBeam2d", eid, ni, nj,
                    30.3 * inch**2, E,
                    (_n + 1) / _n * 3_000.0 * inch**4,
                    K11_2, K33_2, K44_2, trans)

    # Story 1
    for eid, ni, nj in [
        (601100, 113, 211), (601200, 123, 221),
        (601300, 133, 231), (601400, 143, 241),
    ]:
        ops.element("ModElasticBeam2d", eid, ni, nj,
                    30.3 * inch**2, E,
                    (_n + 1) / _n * 3_000.0 * inch**4,
                    K11_2, K33_2, K44_2, trans)


def _define_mf_elastic_beams() -> None:
    """ModElasticBeam2d beam elements between RBS spring nodes.

    Floor 5: W21×68 A=16.7in² I=1170in⁴
    Floor 4: W21×68 A=16.7in² I=1170in⁴
    Floor 3: W21×73 A=21.5in² I=1600in⁴
    Floor 2: W21×73 A=21.5in² I=1600in⁴
    """
    trans = TRANS_PDELTA
    # Floor 5
    for eid, ni, nj in [
        (505100, 514, 522), (505200, 524, 532), (505300, 534, 542),
    ]:
        ops.element("ModElasticBeam2d", eid, ni, nj,
                    16.7 * inch**2, E,
                    (_n + 1) / _n * 0.90 * COMP_I * 1_170.0 * inch**4,
                    K11_2, K33_2, K44_2, trans)
    # Floor 4
    for eid, ni, nj in [
        (504100, 414, 422), (504200, 424, 432), (504300, 434, 442),
    ]:
        ops.element("ModElasticBeam2d", eid, ni, nj,
                    16.7 * inch**2, E,
                    (_n + 1) / _n * 0.90 * COMP_I * 1_170.0 * inch**4,
                    K11_2, K33_2, K44_2, trans)
    # Floor 3
    for eid, ni, nj in [
        (503100, 314, 322), (503200, 324, 332), (503300, 334, 342),
    ]:
        ops.element("ModElasticBeam2d", eid, ni, nj,
                    21.5 * inch**2, E,
                    (_n + 1) / _n * 0.90 * COMP_I * 1_600.0 * inch**4,
                    K11_2, K33_2, K44_2, trans)
    # Floor 2
    for eid, ni, nj in [
        (502100, 214, 222), (502200, 224, 232), (502300, 234, 242),
    ]:
        ops.element("ModElasticBeam2d", eid, ni, nj,
                    21.5 * inch**2, E,
                    (_n + 1) / _n * 0.90 * COMP_I * 1_600.0 * inch**4,
                    K11_2, K33_2, K44_2, trans)


def _define_rbs_elements() -> None:
    """ElasticBeamColumn RBS stub elements (panel-face → RBS spring node).

    These short elastic stubs represent the reduced beam section geometry.
    Floor 5/4: A=14.568in² I_rbs=947.023in⁴
    Floor 3/2: A=18.429in² I_rbs=1278.471in⁴
    """
    # Floor 5
    for eid, ni, nj in [
        (505104, 405104, 5140), (505202, 405202, 5220),
        (505204, 405204, 5240), (505302, 405302, 5320),
        (505304, 405304, 5340), (505402, 405402, 5420),
    ]:
        ops.element("elasticBeamColumn", eid, ni, nj,
                    14.568 * inch**2, E, COMP_I * 947.023 * inch**4, TRANS_LINEAR)
    # Floor 4
    for eid, ni, nj in [
        (504104, 404104, 4140), (504202, 404202, 4220),
        (504204, 404204, 4240), (504302, 404302, 4320),
        (504304, 404304, 4340), (504402, 404402, 4420),
    ]:
        ops.element("elasticBeamColumn", eid, ni, nj,
                    14.568 * inch**2, E, COMP_I * 947.023 * inch**4, TRANS_LINEAR)
    # Floor 3
    for eid, ni, nj in [
        (503104, 403104, 3140), (503202, 403202, 3220),
        (503204, 403204, 3240), (503302, 403302, 3320),
        (503304, 403304, 3340), (503402, 403402, 3420),
    ]:
        ops.element("elasticBeamColumn", eid, ni, nj,
                    18.429 * inch**2, E, COMP_I * 1_278.471 * inch**4, TRANS_LINEAR)
    # Floor 2
    for eid, ni, nj in [
        (502104, 402104, 2140), (502202, 402202, 2220),
        (502204, 402204, 2240), (502302, 402302, 2320),
        (502304, 402304, 2340), (502402, 402402, 2420),
    ]:
        ops.element("elasticBeamColumn", eid, ni, nj,
                    18.429 * inch**2, E, COMP_I * 1_278.471 * inch**4, TRANS_LINEAR)


def _define_mf_beam_springs() -> None:
    """IMK beam-end springs at all RBS cut locations (connection_type=0, RBS).

    Units passed to spring_imk: mm and MPa (N/mm² system).
    """
    comp = COMPOSITE

    # Floor 5  W21×68: d=21.1in htw=46.3 bftf=5.04 ry=1.35in L=192.275in Ls=96.138in Lb=108.15in My=5039.254kip·in
    _bsp5 = dict(
        E=E, Fy=FY,
        Ix=COMP_I * 724.046 * inch**4,
        d=21.100 * inch, htw=46.300, bftf=5.040, ry=1.350 * inch,
        L=192.275 * inch, Ls=96.138 * inch, Lb=108.150 * inch,
        My=5_039.254 * kip * inch,    # originally 5039.254 kip·in
        PgPye=0.0, composite_flag=comp, connection_type=0,
    )
    spring_imk(905104, 514, 5140, **_bsp5)
    spring_imk(905202, 5220, 522, **_bsp5)
    spring_imk(905204, 524, 5240, **_bsp5)
    spring_imk(905302, 5320, 532, **_bsp5)
    spring_imk(905304, 534, 5340, **_bsp5)
    spring_imk(905402, 5420, 542, **_bsp5)

    # Floor 4 — same section
    spring_imk(904104, 414, 4140, **_bsp5)
    spring_imk(904202, 4220, 422, **_bsp5)
    spring_imk(904204, 424, 4240, **_bsp5)
    spring_imk(904302, 4320, 432, **_bsp5)
    spring_imk(904304, 434, 4340, **_bsp5)
    spring_imk(904402, 4420, 442, **_bsp5)

    # Floor 3  W21×73: d=21.2in htw=41.2 bftf=5.6 ry=1.81in L=189.225in Ls=94.612in Lb=107.75in My=6477.588kip·in
    _bsp3 = dict(
        E=E, Fy=FY,
        Ix=COMP_I * 956.942 * inch**4,
        d=21.200 * inch, htw=41.200, bftf=5.600, ry=1.810 * inch,
        L=189.225 * inch, Ls=94.612 * inch, Lb=107.750 * inch,
        My=6_477.588 * kip * inch,    # originally 6477.588 kip·in
        PgPye=0.0, composite_flag=comp, connection_type=0,
    )
    spring_imk(903104, 314, 3140, **_bsp3)
    spring_imk(903202, 3220, 322, **_bsp3)
    spring_imk(903204, 324, 3240, **_bsp3)
    spring_imk(903302, 3320, 332, **_bsp3)
    spring_imk(903304, 334, 3340, **_bsp3)
    spring_imk(903402, 3420, 342, **_bsp3)

    # Floor 2 — same section as floor 3
    spring_imk(902104, 214, 2140, **_bsp3)
    spring_imk(902202, 2220, 222, **_bsp3)
    spring_imk(902204, 224, 2240, **_bsp3)
    spring_imk(902302, 2320, 232, **_bsp3)
    spring_imk(902304, 234, 2340, **_bsp3)
    spring_imk(902402, 2420, 242, **_bsp3)


def _define_mf_column_springs() -> None:
    """IMK column springs at panel-zone faces (connection_type=2, column).

    Gravity-load ratios (PgPye) vary by location and are taken from Tcl.
    """
    # W14×68: d=23.7in htw=49.7 bftf=5.97 ry=1.37in Ic=1560in⁴ L=Ls=Lb=134.9in My=9317kip·in
    _col68 = dict(
        E=E, Fy=FY, Ix=1_560.0 * inch**4,
        d=23.7 * inch, htw=49.7, bftf=5.97, ry=1.37 * inch,
        L=134.9 * inch, Ls=67.45 * inch, Lb=134.9 * inch,
        My=9_317.0 * kip * inch, composite_flag=0, connection_type=2,
    )
    # W14×132: d=24.5in htw=39.2 bftf=4.59 ry=1.99in Ic=3000in⁴
    _col132_134 = dict(
        E=E, Fy=FY, Ix=3_000.0 * inch**4,
        d=24.5 * inch, htw=39.2, bftf=4.59, ry=1.99 * inch,
        L=134.85 * inch, Ls=67.425 * inch, Lb=134.85 * inch,
        My=16_940.0 * kip * inch, composite_flag=0, connection_type=2,
    )
    _col132_134b = dict(
        E=E, Fy=FY, Ix=3_000.0 * inch**4,
        d=24.5 * inch, htw=39.2, bftf=4.59, ry=1.99 * inch,
        L=134.8 * inch, Ls=67.4 * inch, Lb=134.8 * inch,
        My=16_940.0 * kip * inch, composite_flag=0, connection_type=2,
    )
    _col132_169 = dict(
        E=E, Fy=FY, Ix=3_000.0 * inch**4,
        d=24.5 * inch, htw=39.2, bftf=4.59, ry=1.99 * inch,
        L=169.4 * inch, Ls=84.7 * inch, Lb=169.4 * inch,
        My=16_940.0 * kip * inch, composite_flag=0, connection_type=2,
    )

    # Story 4 top springs (panel→column-above): W14×68
    for eid, ni, nj, pgpye in [
        (905101, 405101, 511, 0.0232), (905201, 405201, 521, 0.0347),
        (905301, 405301, 531, 0.0347), (905401, 405401, 541, 0.0232),
    ]:
        spring_imk(eid, ni, nj, PgPye=pgpye, **_col68)

    # Story 4 bottom (panel→column-below): W14×68
    for eid, ni, nj, pgpye in [
        (904103, 404103, 413, 0.0232), (904203, 404203, 423, 0.0347),
        (904303, 404303, 433, 0.0347), (904403, 404403, 443, 0.0232),
    ]:
        spring_imk(eid, ni, nj, PgPye=pgpye, **_col68)

    for eid, ni, nj, pgpye in [
        (904101, 404101, 411, 0.0512), (904201, 404201, 421, 0.0768),
        (904301, 404301, 431, 0.0768), (904401, 404401, 441, 0.0512),
    ]:
        spring_imk(eid, ni, nj, PgPye=pgpye, **_col68)

    # Story 3 top: W14×132 L=134.85
    for eid, ni, nj, pgpye in [
        (903103, 403103, 313, 0.0309), (903203, 403203, 323, 0.0464),
        (903303, 403303, 333, 0.0464), (903403, 403403, 343, 0.0309),
    ]:
        spring_imk(eid, ni, nj, PgPye=pgpye, **_col132_134)

    for eid, ni, nj, pgpye in [
        (903101, 403101, 311, 0.0479), (903201, 403201, 321, 0.0718),
        (903301, 403301, 331, 0.0718), (903401, 403401, 341, 0.0479),
    ]:
        spring_imk(eid, ni, nj, PgPye=pgpye, **_col132_134b)

    # Story 2 top: W14×132 L=134.8
    for eid, ni, nj, pgpye in [
        (902103, 402103, 213, 0.0479), (902203, 402203, 223, 0.0718),
        (902303, 402303, 233, 0.0718), (902403, 402403, 243, 0.0479),
    ]:
        spring_imk(eid, ni, nj, PgPye=pgpye, **_col132_134b)

    # Story 1 bottom (panel→base): W14×132 L=169.4
    for eid, ni, nj, pgpye in [
        (902101, 402101, 211, 0.0651), (902201, 402201, 221, 0.0977),
        (902301, 402301, 231, 0.0977), (902401, 402401, 241, 0.0651),
    ]:
        spring_imk(eid, ni, nj, PgPye=pgpye, **_col132_169)

    # Ground-level (support → base node): W14×132 L=169.4
    for eid, ni, nj, pgpye in [
        (901103, 110, 113, 0.0651), (901203, 120, 123, 0.0977),
        (901303, 130, 133, 0.0977), (901403, 140, 143, 0.0651),
    ]:
        spring_imk(eid, ni, nj, PgPye=pgpye, **_col132_169)


def _define_column_splice_springs() -> None:
    """Rigid springs at column splice locations (mid-height story 3–4)."""
    for eid, ni, nj in [
        (903107, 103171, 103172), (903207, 103271, 103272),
        (903307, 103371, 103372), (903407, 103471, 103472),
        (903507, 103571, 103572), (903607, 103671, 103672),
    ]:
        spring_rigid(eid, ni, nj)


def _define_floor_link_trusses() -> None:
    """Rigid truss elements linking MF panel node to EGF node on each floor."""
    for eid, ni, nj in [
        (1005, 405404, 550),
        (1004, 404404, 450),
        (1003, 403404, 350),
        (1002, 402404, 250),
    ]:
        ops.element("truss", eid, ni, nj, A_STIFF, MAT_RIGID)


def _define_egf_columns() -> None:
    """Elastic leaning-column elements for the gravity frame (PDelta columns)."""
    # Very large A and I to represent rigid leaning column behaviour
    a_gc = 100_000.0 * inch**2
    i_gc = 100_000_000.0 * inch**4
    trans = TRANS_PDELTA

    for eid, ni, nj in [
        (604500, 453, 551), (604600, 463, 561),
        (603502, 103572, 451), (603602, 103672, 461),
        (603501, 353, 103571), (603601, 363, 103671),
        (602500, 253, 351), (602600, 263, 361),
        (601500, 153, 251), (601600, 163, 261),
    ]:
        ops.element("elasticBeamColumn", eid, ni, nj, a_gc, E, i_gc, trans)


def _define_egf_beams() -> None:
    """Elastic gravity frame beams (rigid links between EGF nodes)."""
    a_gb = 100_000.0 * inch**2
    i_gb = 100_000_000.0 * inch**4
    trans = TRANS_PDELTA

    for eid, ni, nj in [
        (505400, 554, 562),
        (504400, 454, 462),
        (503400, 354, 362),
        (502400, 254, 262),
    ]:
        ops.element("elasticBeamColumn", eid, ni, nj, a_gb, E, i_gb, trans)


def _define_egf_springs() -> None:
    """Zero-stiffness gravity column springs + rigid gravity beam springs."""
    # EGF gravity column zero-length (rotation-release)
    egf_col_zero = [
        (905501, 550, 551), (905601, 560, 561),
        (904503, 450, 453), (904603, 460, 463),
        (904501, 450, 451), (904601, 460, 461),
        (903503, 350, 353), (903603, 360, 363),
        (903501, 350, 351), (903601, 360, 361),
        (902503, 250, 253), (902603, 260, 263),
        (902501, 250, 251), (902601, 260, 261),
        (901503, 150, 153), (901603, 160, 163),
    ]
    for eid, ni, nj in egf_col_zero:
        spring_zero(eid, ni, nj)

    # EGF gravity beam rigid springs
    egf_beam_rigid = [
        (905504, 550, 554), (905602, 560, 562),
        (904504, 450, 454), (904602, 460, 462),
        (903504, 350, 354), (903602, 360, 362),
        (902504, 250, 254), (902602, 260, 262),
    ]
    for eid, ni, nj in egf_beam_rigid:
        spring_rigid(eid, ni, nj)


def define_elements() -> None:
    """Build all frame elements: panel zones, elastic columns/beams, springs.

    Call order matters — panel nodes must exist before springs are attached.
    """
    _define_geom_transforms()
    _define_panel_zones()
    _define_panel_zone_springs()
    _define_mf_elastic_columns()
    _define_mf_elastic_beams()
    _define_rbs_elements()
    _define_mf_beam_springs()
    _define_mf_column_springs()
    _define_column_splice_springs()
    _define_floor_link_trusses()
    _define_egf_columns()
    _define_egf_beams()
    _define_egf_springs()


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(odb_tag: int = 1, output_dir: Path = Path("output")) -> "opst.post.CreateODB":
    """Initialise the opstool ODB after model geometry is fully built.

    Args:
        odb_tag: Integer tag for this ODB instance.
        output_dir: Folder where .nc / .h5 files are written.

    Returns:
        Populated CreateODB object (call odb.save_response() in post_process).
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=odb_tag, model_update=False)
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Apply dead + live gravity loads as a plain linear pattern (tag=100).

    All loads in N (originally in kips; multiplied by kip).
    MF column loads applied at top-of-column panel nodes (xx103 tags).
    EGF loads applied directly to grid nodes.
    """
    ops.timeSeries("Linear", 100)
    ops.pattern("Plain", 100, 100)

    # MF column loads — originally in kips
    # Floor 5
    ops.load(405103, 0.0, -23.313 * kip, 0.0)
    ops.load(405203, 0.0, -34.969 * kip, 0.0)
    ops.load(405303, 0.0, -34.969 * kip, 0.0)
    ops.load(405403, 0.0, -23.313 * kip, 0.0)
    # Floor 4
    ops.load(404103, 0.0, -28.225 * kip, 0.0)
    ops.load(404203, 0.0, -42.338 * kip, 0.0)
    ops.load(404303, 0.0, -42.338 * kip, 0.0)
    ops.load(404403, 0.0, -28.225 * kip, 0.0)
    # Floor 3
    ops.load(403103, 0.0, -28.225 * kip, 0.0)
    ops.load(403203, 0.0, -42.338 * kip, 0.0)
    ops.load(403303, 0.0, -42.338 * kip, 0.0)
    ops.load(403403, 0.0, -28.225 * kip, 0.0)
    # Floor 2
    ops.load(402103, 0.0, -28.750 * kip, 0.0)
    ops.load(402203, 0.0, -43.125 * kip, 0.0)
    ops.load(402303, 0.0, -43.125 * kip, 0.0)
    ops.load(402403, 0.0, -28.750 * kip, 0.0)

    # EGF column loads — originally in kips
    ops.load(550, 0.0, -310.443750 * kip, 0.0)
    ops.load(560, 0.0, -310.443750 * kip, 0.0)
    ops.load(450, 0.0, -344.887500 * kip, 0.0)
    ops.load(460, 0.0, -344.887500 * kip, 0.0)
    ops.load(350, 0.0, -344.887500 * kip, 0.0)
    ops.load(360, 0.0, -344.887500 * kip, 0.0)
    ops.load(250, 0.0, -346.725000 * kip, 0.0)
    ops.load(260, 0.0, -346.725000 * kip, 0.0)


def define_nodal_masses() -> None:
    """Assign nodal masses (converted from kip·s²/in to kg).

    Original Tcl uses units of kip·s²/in which equals 175.127 kg.
    Here we convert: mass_kg = mass_kip_s2_in × kip / (inch × 1e-3) but
    OpenSeesPy `mass` command in N–mm system expects mass in kg.
    Conversion: 1 kip·s²/in = 4448.22 N·s²/25.4mm = 175.127 kg.

    Rotational mass set to 1e-9 kg·mm² (negligible, matches Tcl).
    """
    _c = kip / (G_ACCEL)   # kip·s²/in → kg  (= 175.127 kg per unit)

    # Floor 5
    ops.mass(405104, 0.1476 * _c, 1e-9, 1e-9)
    ops.mass(405204, 0.1709 * _c, 1e-9, 1e-9)
    ops.mass(405304, 0.1709 * _c, 1e-9, 1e-9)
    ops.mass(405404, 0.1709 * _c, 1e-9, 1e-9)
    ops.mass(550,    0.5361 * _c, 1e-9, 1e-9)
    ops.mass(560,    0.5361 * _c, 1e-9, 1e-9)
    # Floor 4
    ops.mass(404104, 0.2486 * _c, 1e-9, 1e-9)
    ops.mass(404204, 0.2720 * _c, 1e-9, 1e-9)
    ops.mass(404304, 0.2720 * _c, 1e-9, 1e-9)
    ops.mass(404404, 0.2720 * _c, 1e-9, 1e-9)
    ops.mass(450,    0.3846 * _c, 1e-9, 1e-9)
    ops.mass(460,    0.3846 * _c, 1e-9, 1e-9)
    # Floor 3
    ops.mass(403104, 0.2486 * _c, 1e-9, 1e-9)
    ops.mass(403204, 0.2720 * _c, 1e-9, 1e-9)
    ops.mass(403304, 0.2720 * _c, 1e-9, 1e-9)
    ops.mass(403404, 0.2720 * _c, 1e-9, 1e-9)
    ops.mass(350,    0.3846 * _c, 1e-9, 1e-9)
    ops.mass(360,    0.3846 * _c, 1e-9, 1e-9)
    # Floor 2
    ops.mass(402104, 0.2797 * _c, 1e-9, 1e-9)
    ops.mass(402204, 0.3030 * _c, 1e-9, 1e-9)
    ops.mass(402304, 0.3030 * _c, 1e-9, 1e-9)
    ops.mass(402404, 0.3030 * _c, 1e-9, 1e-9)
    ops.mass(250,    0.3380 * _c, 1e-9, 1e-9)
    ops.mass(260,    0.3380 * _c, 1e-9, 1e-9)

    ops.constraints("Plain")


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def _run_eigen(n_modes: int = 4) -> list[float]:
    """Run eigen analysis and return natural periods (seconds).

    Args:
        n_modes: Number of modes to extract.

    Returns:
        List of natural periods T1…Tn in seconds.
    """
    lam = ops.eigen(n_modes)
    periods = [2.0 * np.pi / np.sqrt(l) for l in lam]
    for i, t in enumerate(periods, 1):
        print(f"T{i} = {t:.3f} s")
    return periods


def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10) -> None:
    """Apply gravity loads incrementally using SmartAnalyze (Static).

    Args:
        odb: Active CreateODB instance; fetch_response_step() called each step.
        n_steps: Number of equal load increments (default 10).
    """
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / n_steps)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30],
    )
    protocol = [1.0]
    segs = analysis.static_split(protocol, maxStep=1.0 / n_steps)
    for seg in segs:
        analysis.StaticAnalyze(node=405104, dof=1, seg=seg)
        odb.fetch_response_step()
    analysis.close()
    ops.loadConst("-time", 0.0)


def run_pushover(
    odb: "opst.post.CreateODB",
    ctrl_node: int,
    ctrl_dof: int,
    target_disp: float,
    output_dir: Path,
    max_step: float | None = None,
) -> None:
    """Run a displacement-controlled pushover using SmartAnalyze.

    A lateral load pattern (tag=222) must be defined before calling this.

    Args:
        odb: Active CreateODB instance.
        ctrl_node: Control node tag (usually roof panel centroid = 405104).
        ctrl_dof: DOF (1 = X).
        target_disp: Target displacement in mm.
        output_dir: Path to write deformed shape visualisation.
        max_step: Max step size in mm. Defaults to target_disp / 100.
    """
    if max_step is None:
        max_step = target_disp / 200.0
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("DisplacementControl", ctrl_node, ctrl_dof, max_step)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50, 60],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-4,
    )
    protocol = [target_disp]
    segs = analysis.static_split(protocol, maxStep=max_step)
    for seg in segs:
        analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
        odb.fetch_response_step()
    analysis.close()


def _define_rayleigh_damping(w1: float, w3: float) -> None:
    """Assign Rayleigh damping to regions.

    Stiffness-proportional a1 is split between frame elements (a1_mod) and
    spring elements (a1_mod/10) following the Tcl model convention.

    Args:
        w1: First mode circular frequency (rad/s).
        w3: Third mode circular frequency (rad/s).
    """
    a0 = ZETA * 2.0 * w1 * w3 / (w1 + w3)
    a1 = ZETA * 2.0 / (w1 + w3)
    a1_mod = a1 * (1.0 + _n) / _n

    # Frame elements (MF columns, beams)
    frame_eles = [
        604100, 604200, 604300, 604400,
        603102, 603202, 603302, 603402,
        603101, 603201, 603301, 603401,
        602100, 602200, 602300, 602400,
        601100, 601200, 601300, 601400,
        505100, 505200, 505300,
        504100, 504200, 504300,
        503100, 503200, 503300,
        502100, 502200, 502300,
    ]
    ops.region(1, "-ele", *frame_eles, "-rayleigh", 0.0, 0.0, a1_mod, 0.0)

    # Mass nodes
    mass_nodes = [
        402104, 402204, 402304, 402404, 250, 260,
        403104, 403204, 403304, 403404, 350, 360,
        404104, 404204, 404304, 404404, 450, 460,
        405104, 405204, 405304, 405404, 550, 560,
    ]
    ops.region(2, "-node", *mass_nodes, "-rayleigh", a0, 0.0, 0.0, 0.0)

    # Spring elements (eleRange 900000–999999) — 1/10 stiffness damping
    ops.region(3, "-eleRange", 900000, 999999, "-rayleigh", 0.0, 0.0, a1_mod / 10.0, 0.0)


def run_dynamic(
    odb: "opst.post.CreateODB",
    periods: list[float],
    gm_file: Path,
    gm_dt: float = 0.01,
    gm_points: int = 2495,
    eq_sf: float = 1.0,
    fv_duration: float = 10.0,
    max_run_time: float = 600.0,
    output_dir: Path = Path("output"),
) -> None:
    """Run transient earthquake analysis using DynamicAnalysisCollapseSolverX.

    Args:
        odb: Active CreateODB instance.
        periods: List of modal periods [T1, T2, T3, T4] from eigen analysis.
        gm_file: Path to ground motion acceleration file (.txt, values in g).
        gm_dt: Timestep of the ground motion record (seconds).
        gm_points: Number of data points in the record.
        eq_sf: Ground motion scale factor.
        fv_duration: Free-vibration duration after GM ends (seconds).
        max_run_time: Maximum wall-clock run time in seconds.
        output_dir: Output directory for visualisation.
    """
    w1 = 2.0 * np.pi / periods[0]
    w3 = 2.0 * np.pi / periods[2]
    _define_rayleigh_damping(w1, w3)

    gm_duration = gm_dt * gm_points
    tot_time    = gm_dt * round((gm_duration + fv_duration) / gm_dt)
    dt_anal     = 0.5 * gm_dt

    ops.timeSeries("Path", 1, "-dt", gm_dt, "-filePath", str(gm_file), "-factor", eq_sf * G_ACCEL)
    ops.pattern("UniformExcitation", 200, 1, "-accel", 1)

    mf_nodes  = [402104, 403104, 404104, 405104]
    egf_nodes = [250, 350, 450, 550]

    dynamic_analysis_collapse_solver(
        dt=gm_dt,
        dt_anal_step=dt_anal,
        gm_time=tot_time,
        num_stories=N_STORY,
        drift_limit=0.15,
        mf_floor_nodes=mf_nodes,
        egf_floor_nodes=egf_nodes,
        h1=H1_STORY,
        htyp=H_TYP,
        trace_gf_drift=True,
        max_run_time=max_run_time,
        odb=odb,
        output_dir=output_dir,
    )


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, apply gravity, run pushover or dynamic analysis, return ODB.

    Args:
        output_dir: Directory where ODB and HTML visualisation files are saved.

    Returns:
        Populated CreateODB instance. Call post_process(odb, output_dir) next.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    # ── Build model ──────────────────────────────────────────────────────────
    init_model()
    define_materials()
    define_sections()
    define_nodes()

    define_elements()
    define_boundary_conditions()

    vis_nodes(output_dir)                       # V1: nodes + supports

    vis_model(output_dir)                       # V2: full geometry

    define_gravity_loads()
    define_nodal_masses()

    vis_loads(output_dir)                       # V3: gravity load vectors
    vis_pre_analysis(output_dir)                # V4: pre-analysis check

    odb = create_odb(odb_tag=1, output_dir=output_dir)
    # ── Gravity analysis ─────────────────────────────────────────────────────
    run_gravity(odb)

    # ── Eigen analysis (needed for damping and period reporting) ─────────────
    periods = _run_eigen(n_modes=4)

    # ── Dynamic earthquake analysis ───────────────────────────────────────────
    if RUN_EQ:
        gm_file = Path(__file__).parent / "ground_motions" / "NR94cnp.txt"
        run_dynamic(
            odb,
            periods=periods,
            gm_file=gm_file,
            gm_dt=0.01,
            gm_points=2495,
            eq_sf=1.0,
            fv_duration=10.0,
            max_run_time=600.0,
            output_dir=output_dir,
        )

    # ── Pushover analysis ─────────────────────────────────────────────────────
    if RUN_PO:
        # Inverted triangular lateral load pattern (tag=222)
        ops.timeSeries("Linear", 222)
        ops.pattern("Plain", 222, 222)
        ops.load(405103, -0.52567 * kip, 0.0, 0.0)   # originally kip, converted
        ops.load(404103, -0.42889 * kip, 0.0, 0.0)
        ops.load(403103, -0.28636 * kip, 0.0, 0.0)
        ops.load(402103, -0.13418 * kip, 0.0, 0.0)

        target_disp = 0.10 * FLOOR5            # 10% of building height [mm]
        run_pushover(odb, ctrl_node=405104, ctrl_dof=1,
                     target_disp=target_disp, output_dir=output_dir)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and render deformed-shape visualisations.

    Args:
        odb: Populated CreateODB returned by run_analysis().
        output_dir: Folder where ODB and HTML files are written.
    """
    odb.save_response()

    if not _headless():
        vis_defo(output_dir, "vis_05_defo_dynamic.html", odb_tag=1, resp_dof="UX")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    ops.wipe()
