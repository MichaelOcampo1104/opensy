# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 3-story CBF Building
UniqueID : elkady2020
Author   : Dr. Ahmed Elkady (amaelkady)
Date     : 2026-05-28
Purpose  : Converted 3-story special concentrically-braced frame (SCBF) model from Tcl (SCBF3B.tcl).
Ref      : https://github.com/amaelkady/OpenSEES_Models_CBF
Units    : N, mm, MPa (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst          # visualisation — use opst.vis.plotly.*
import numpy as np
import sys
from pathlib import Path

# Add standards/ to path if running standalone
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo

# Add local directory for sourcing helper functions
sys.path.insert(0, str(Path(__file__).parent))
from spring_pz import spring_pz
from spring_imk import spring_imk
from spring_zero import spring_zero
from spring_rigid import spring_rigid
from spring_pinching import spring_pinching
from constructpanel_rectangle import construct_panel_rectangle
from constructbrace import construct_brace
from spring_gusset import spring_gusset
from fatigue_mat import fatigue_mat
from construct_fiber_column import construct_fiber_column
from fiberchss import fiber_chss
from fiberwf import fiber_wf
from dynamicanalysiscollapsesolverx import dynamic_analysis_collapse_solver

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Geometric Transformations
TRANS_LINEAR      = 1
TRANS_PDELTA      = 2
TRANS_COROT       = 3
TRANS_SELECTED    = TRANS_PDELTA

# Basic Materials
MAT_FLEXIBLE       = 9
MAT_RIGID          = 99
MAT_VOCE_CHABOCHE  = 666
MAT_GHOST_BRACE    = 1000

# Gusset Plate Spring Materials
MAT_GUSSET_L3_LEFT   = 4000
MAT_GUSSET_L3_RIGHT  = 4001
MAT_GUSSET_L2_LEFT   = 4002
MAT_GUSSET_L2_RIGHT  = 4003
MAT_GUSSET_L2_MID_L  = 4004
MAT_GUSSET_L2_MID_R  = 4005
MAT_GUSSET_L3_COR_L  = 4006
MAT_GUSSET_L3_COR_R  = 4007
MAT_GUSSET_L3_COR_L2 = 4008
MAT_GUSSET_L3_COR_R2 = 4009
MAT_GUSSET_L1_COR_L  = 4010
MAT_GUSSET_L1_COR_R  = 4011

# Fatigue & Brace Steel Materials
MAT_BRACE_BASE_L1 = 100  # Steel02
MAT_BRACE_FAT_L1  = 101  # Fatigue wrapped
MAT_BRACE_BASE_L2 = 102  # Steel02
MAT_BRACE_FAT_L2  = 103  # Fatigue wrapped
MAT_BRACE_BASE_L3 = 104  # Steel02
MAT_BRACE_FAT_L3  = 105  # Fatigue wrapped

# Column Sections/Materials (Wide Flange)
SEC_COL_L3 = 201
SEC_COL_L2 = 203
SEC_COL_L1 = 205
SEC_COL_R202  = 202
SEC_COL_R204  = 204
SEC_COL_R206  = 206

# Brace Section Types
SEC_BRACE_L1 = 1
SEC_BRACE_L2 = 2
SEC_BRACE_L3 = 3

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Seconds constant
sec = 1.0

# Frame centerline geometry
n_stories = 3
n_bays    = 1

# Floor levels
floor_1 = 0.0 * inch
floor_2 = 180.0 * inch
floor_3 = 360.0 * inch
floor_4 = 540.0 * inch

# Frame grid lines (Axes)
axis_1 = 0.0 * inch
axis_2 = 360.0 * inch
axis_3 = 720.0 * inch
axis_4 = 1080.0 * inch

h_building = 540.0 * inch
w_frame    = 360.0 * inch

# Material properties
E   = 29000.0 * ksi
mu  = 0.3
fy  = 55.0 * ksi
fy_b = 45.0 * ksi
fy_g = 55.0 * ksi

# Stiff elements properties
A_stiff = 1000.0 * inch**2
I_stiff = 100000.0 * inch**4

# Composite beam factor
composite = 0
comp_i    = 1.400
comp_i_gc = 1.400

# Fiber element properties
n_segments    = 8
initial_gi    = 0.00100
n_integration = 5

# Geometry of Corner Gusset Plate
x_cgp1 = 21.3016 * inch
y_cgp1 = 21.3016 * inch
x_cgp2 = 22.7600 * inch
y_cgp2 = 22.7600 * inch
x_cgp3 = 20.4177 * inch
y_cgp3 = 20.4177 * inch

# Geometry of Mid-Span Gusset Plate
x_mgp1 = 15.6005 * inch
y_mgp1 = 15.6005 * inch
x_mgp2 = 15.6005 * inch
y_mgp2 = 15.6005 * inch
x_mgp3 = 21.3016 * inch
y_mgp3 = 21.3016 * inch

# Stiffness modifiers parameters
n_stiff_mod = 10.0
k44_2 = 6.0 * (1.0 + n_stiff_mod) / (2.0 + 3.0 * n_stiff_mod)
k11_2 = (1.0 + 2.0 * n_stiff_mod) * k44_2 / (1.0 + n_stiff_mod)
k33_2 = (1.0 + 2.0 * n_stiff_mod) * k44_2 / (1.0 + n_stiff_mod)
k44_1 = 6.0 * n_stiff_mod / (1.0 + 3.0 * n_stiff_mod)
k11_1 = (1.0 + 2.0 * n_stiff_mod) * k44_1 / (1.0 + n_stiff_mod)
k33_1 = 2.0 * k44_1

# Gravity
g_const = 386.10 * inch / sec**2  # will evaluate to ~9810 mm/s2

# Gap distance between beam end and column flange (for shear tab connections)
gap = 0.08

# Story heights (for collapse drift check)
h1_story = 180.0 * inch
h_typ    = 180.0 * inch

# Rayleigh damping ratio
ZETA = 0.020

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    # Flexible Material
    ops.uniaxialMaterial("Elastic", MAT_FLEXIBLE, 1.e-9 * ksi)
    # Rigid Material
    ops.uniaxialMaterial("Elastic", MAT_RIGID, 1.e9 * ksi)
    # Voce-Chaboche Material
    ops.uniaxialMaterial(
        "UVCuniaxial", MAT_VOCE_CHABOCHE,
        29000.0 * ksi, 55.0 * ksi, 18.0, 10.0, 0.0, 1.0, 2,
        3500.0 * ksi, 180.0, 345.0 * ksi, 10.0
    )
    # Fatigue-wrapped brace materials (Steel02 base + Fatigue wrapper).
    # Must be defined here — before define_sections() references them.
    fatigue_mat(MAT_BRACE_BASE_L1, 2, fy_b, E, 202.3709 * inch, 3.2400 * inch, 20.7000, 0.0 * inch, 0.0 * inch)
    fatigue_mat(MAT_BRACE_BASE_L2, 2, fy_b, E, 200.3084 * inch, 2.8900 * inch, 18.5000, 0.0 * inch, 0.0 * inch)
    fatigue_mat(MAT_BRACE_BASE_L3, 2, fy_b, E, 195.5584 * inch, 2.9500 * inch, 28.8000, 0.0 * inch, 0.0 * inch)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    # Circular HSS Sections
    # FiberCHSS secID matID d t nfdy nfty
    fiber_chss(SEC_BRACE_L1, MAT_BRACE_FAT_L1, 9.6300 * inch, 0.5000 * inch, 12, 4)
    fiber_chss(SEC_BRACE_L2, MAT_BRACE_FAT_L2, 8.6300 * inch, 0.5000 * inch, 12, 4)
    fiber_chss(SEC_BRACE_L3, MAT_BRACE_FAT_L3, 8.6300 * inch, 0.3220 * inch, 12, 4)

    # Wide-Flange Sections for Columns (all identical geometry in this model)
    # fiber_wf(secID, matID, d, bf, tf, tw, nfdw, nftw, nfbf, nftf)
    fiber_wf(SEC_COL_L3, MAT_VOCE_CHABOCHE, 13.1000 * inch, 12.3000 * inch, 1.1100 * inch, 0.7100 * inch, 6, 2, 6, 2)
    fiber_wf(SEC_COL_R202, MAT_VOCE_CHABOCHE, 13.1000 * inch, 12.3000 * inch, 1.1100 * inch, 0.7100 * inch, 6, 2, 6, 2)
    fiber_wf(SEC_COL_L2, MAT_VOCE_CHABOCHE, 13.1000 * inch, 12.3000 * inch, 1.1100 * inch, 0.7100 * inch, 6, 2, 6, 2)
    fiber_wf(SEC_COL_R204, MAT_VOCE_CHABOCHE, 13.1000 * inch, 12.3000 * inch, 1.1100 * inch, 0.7100 * inch, 6, 2, 6, 2)
    fiber_wf(SEC_COL_L1, MAT_VOCE_CHABOCHE, 13.1000 * inch, 12.3000 * inch, 1.1100 * inch, 0.7100 * inch, 6, 2, 6, 2)
    fiber_wf(SEC_COL_R206, MAT_VOCE_CHABOCHE, 13.1000 * inch, 12.3000 * inch, 1.1100 * inch, 0.7100 * inch, 6, 2, 6, 2)

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    # SUPPORT NODES
    ops.node(110, axis_1, floor_1)
    ops.node(120, axis_2, floor_1)
    ops.node(130, axis_3, floor_1)
    ops.node(140, axis_4, floor_1)

    # EGF COLUMN GRID NODES
    ops.node(430, axis_3, floor_4)
    ops.node(440, axis_4, floor_4)
    ops.node(330, axis_3, floor_3)
    ops.node(340, axis_4, floor_3)
    ops.node(230, axis_3, floor_2)
    ops.node(240, axis_4, floor_2)

    # EGF COLUMN NODES
    ops.node(431, axis_3, floor_4)
    ops.node(441, axis_4, floor_4)
    ops.node(333, axis_3, floor_3)
    ops.node(343, axis_4, floor_3)
    ops.node(331, axis_3, floor_3)
    ops.node(341, axis_4, floor_3)
    ops.node(233, axis_3, floor_2)
    ops.node(243, axis_4, floor_2)
    ops.node(231, axis_3, floor_2)
    ops.node(241, axis_4, floor_2)
    ops.node(133, axis_3, floor_1)
    ops.node(143, axis_4, floor_1)

    # EGF BEAM NODES
    ops.node(434, axis_3, floor_4)
    ops.node(442, axis_4, floor_4)
    ops.node(334, axis_3, floor_3)
    ops.node(342, axis_4, floor_3)
    ops.node(234, axis_3, floor_2)
    ops.node(242, axis_4, floor_2)

    # MF COLUMN NODES
    ops.node(411, axis_1, floor_4 - 30.40 * inch / 2.0)
    ops.node(421, axis_2, floor_4 - 30.40 * inch / 2.0)
    ops.node(313, axis_1, floor_3 + 21.50 * inch / 2.0)
    ops.node(323, axis_2, floor_3 + 21.50 * inch / 2.0)
    ops.node(311, axis_1, floor_3 - 21.50 * inch / 2.0)
    ops.node(321, axis_2, floor_3 - 21.50 * inch / 2.0)
    ops.node(213, axis_1, floor_2 + 18.40 * inch / 2.0)
    ops.node(223, axis_2, floor_2 + 18.40 * inch / 2.0)
    ops.node(211, axis_1, floor_2 - 18.40 * inch / 2.0)
    ops.node(221, axis_2, floor_2 - 18.40 * inch / 2.0)
    ops.node(113, axis_1, floor_1)
    ops.node(123, axis_2, floor_1)

    # MF BEAM NODES
    ops.node(414, axis_1 + 13.10 * inch / 2.0, floor_4)
    ops.node(422, axis_2 - 13.10 * inch / 2.0, floor_4)
    ops.node(314, axis_1 + 13.10 * inch / 2.0, floor_3)
    ops.node(322, axis_2 - 13.10 * inch / 2.0, floor_3)
    ops.node(214, axis_1 + 13.10 * inch / 2.0, floor_2)
    ops.node(222, axis_2 - 13.10 * inch / 2.0, floor_2)

    # MID-SPAN GUSSET PLATE RIGID OFFSET NODES
    ops.node(204101, (axis_1 + axis_2) / 2.0, floor_4)
    ops.node(204102, (axis_1 + axis_2) / 2.0 - 72.1250 * inch / 2.0, floor_4)
    ops.node(204112, (axis_1 + axis_2) / 2.0 - 72.1250 * inch / 2.0, floor_4)
    ops.node(204105, (axis_1 + axis_2) / 2.0 + 72.1250 * inch / 2.0, floor_4)
    ops.node(204115, (axis_1 + axis_2) / 2.0 + 72.1250 * inch / 2.0, floor_4)
    ops.node(204104, (axis_1 + axis_2) / 2.0 + x_mgp3, floor_4 - y_mgp3)
    ops.node(204114, (axis_1 + axis_2) / 2.0 + x_mgp3, floor_4 - y_mgp3)
    ops.node(204103, (axis_1 + axis_2) / 2.0 - x_mgp3, floor_4 - y_mgp3)
    ops.node(204113, (axis_1 + axis_2) / 2.0 - x_mgp3, floor_4 - y_mgp3)
    
    ops.node(202101, (axis_1 + axis_2) / 2.0, floor_2)
    ops.node(202102, (axis_1 + axis_2) / 2.0 - 75.5000 * inch / 2.0, floor_2)
    ops.node(202112, (axis_1 + axis_2) / 2.0 - 75.5000 * inch / 2.0, floor_2)
    ops.node(202105, (axis_1 + axis_2) / 2.0 + 75.5000 * inch / 2.0, floor_2)
    ops.node(202115, (axis_1 + axis_2) / 2.0 + 75.5000 * inch / 2.0, floor_2)
    ops.node(202104, (axis_1 + axis_2) / 2.0 + x_mgp1, floor_2 - y_mgp1)
    ops.node(202114, (axis_1 + axis_2) / 2.0 + x_mgp1, floor_2 - y_mgp1)
    ops.node(202103, (axis_1 + axis_2) / 2.0 - x_mgp1, floor_2 - y_mgp1)
    ops.node(202113, (axis_1 + axis_2) / 2.0 - x_mgp1, floor_2 - y_mgp1)
    ops.node(202106, (axis_1 + axis_2) / 2.0 + x_mgp2, floor_2 + y_mgp2)
    ops.node(202116, (axis_1 + axis_2) / 2.0 + x_mgp2, floor_2 + y_mgp2)
    ops.node(202107, (axis_1 + axis_2) / 2.0 - x_mgp2, floor_2 + y_mgp2)
    ops.node(202117, (axis_1 + axis_2) / 2.0 - x_mgp2, floor_2 + y_mgp2)

    # CORNER X-BRACING RIGID OFFSET NODES
    ops.node(103140, axis_1 + x_cgp3, floor_3 + y_cgp3)
    ops.node(103141, axis_1 + x_cgp3, floor_3 + y_cgp3)
    ops.node(103150, axis_1 + x_cgp2, floor_3 - y_cgp2)
    ops.node(103151, axis_1 + x_cgp2, floor_3 - y_cgp2)
    ops.node(103240, axis_2 - x_cgp3, floor_3 + y_cgp3)
    ops.node(103241, axis_2 - x_cgp3, floor_3 + y_cgp3)
    ops.node(103250, axis_2 - x_cgp2, floor_3 - y_cgp2)
    ops.node(103251, axis_2 - x_cgp2, floor_3 - y_cgp2)
    ops.node(101140, axis_1 + x_cgp1, floor_1 + y_cgp1)
    ops.node(101141, axis_1 + x_cgp1, floor_1 + y_cgp1)
    ops.node(101240, axis_2 - x_cgp1, floor_1 + y_cgp1)
    ops.node(101241, axis_2 - x_cgp1, floor_1 + y_cgp1)

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    # MF SUPPORTS
    ops.fix(110, 1, 1, 0)
    ops.fix(120, 1, 1, 0)

    # EGF SUPPORTS
    ops.fix(130, 1, 1, 0)
    ops.fix(140, 1, 1, 0)

    # MF FLOOR MOVEMENT
    ops.equalDOF(404104, 404204, 1)
    ops.equalDOF(403104, 403204, 1)
    ops.equalDOF(402104, 402204, 1)

    # BEAM MID-SPAN HORIZONTAL MOVEMENT CONSTRAINT
    ops.equalDOF(404104, 204101, 1)
    ops.equalDOF(402104, 202101, 1)

    # EGF FLOOR MOVEMENT
    ops.equalDOF(430, 440, 1)
    ops.equalDOF(330, 340, 1)
    ops.equalDOF(230, 240, 1)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def _define_geom_transforms() -> None:
    """Define geometric transformation tags (Linear, PDelta, Corotational)."""
    ops.geomTransf("Linear", TRANS_LINEAR)
    ops.geomTransf("PDelta", TRANS_PDELTA)
    ops.geomTransf("Corotational", TRANS_COROT)


def _define_panel_zones() -> None:
    """Construct panel zone nodes + elastic frame elements."""
    _y = {4: floor_4, 3: floor_3, 2: floor_2}
    for (a, x, fl, d_c, d_b) in [
        (1, axis_1, 4, 13.10 * inch, 30.40 * inch),
        (2, axis_2, 4, 13.10 * inch, 30.40 * inch),
        (1, axis_1, 3, 13.10 * inch, 21.50 * inch),
        (2, axis_2, 3, 13.10 * inch, 21.50 * inch),
        (1, axis_1, 2, 13.10 * inch, 18.40 * inch),
        (2, axis_2, 2, 13.10 * inch, 18.40 * inch),
    ]:
        construct_panel_rectangle(a, fl, x, _y[fl], E, A_stiff, I_stiff, d_c, d_b, TRANS_SELECTED)


def _define_panel_zone_springs() -> None:
    """Attach panel zone springs at all joints (response_id=2 bare steel)."""
    for eid, ni, nj, d_col, d_beam in [
        (904100, 404109, 404110, 13.10 * inch, 30.40 * inch),
        (904200, 404209, 404210, 13.10 * inch, 30.40 * inch),
        (903100, 403109, 403110, 13.10 * inch, 21.50 * inch),
        (903200, 403209, 403210, 13.10 * inch, 21.50 * inch),
        (902100, 402109, 402110, 13.10 * inch, 18.40 * inch),
        (902200, 402209, 402210, 13.10 * inch, 18.40 * inch),
    ]:
        spring_pz(eid, ni, nj, E, mu, fy, 0.71 * inch, 0.00 * inch,
                  d_col, d_beam, 1.11 * inch, 12.30 * inch,
                  1070.00 * inch**4, 3.500 * inch, 4.000 * inch, 2, TRANS_LINEAR)


def _define_rigid_brace_links() -> None:
    """Rigid elastic beam column links around gusset plates."""
    # Mid-span rigid links
    for eid, ni, nj, tr in [
        (704122, 204101, 204102, TRANS_SELECTED),
        (704133, 204101, 204103, TRANS_COROT),
        (704144, 204101, 204104, TRANS_COROT),
        (704155, 204101, 204105, TRANS_SELECTED),
        (702122, 202101, 202102, TRANS_SELECTED),
        (702133, 202101, 202103, TRANS_COROT),
        (702144, 202101, 202104, TRANS_COROT),
        (702155, 202101, 202105, TRANS_SELECTED),
        (702166, 202101, 202106, TRANS_COROT),
        (702177, 202101, 202107, TRANS_COROT),
    ]:
        ops.element("elasticBeamColumn", eid, ni, nj, A_stiff, E, I_stiff, tr)

    # Corner rigid links
    for eid, ni, nj in [
        (703111, 403110, 103140), (703199, 403199, 103150),
        (703211, 403208, 103240), (703299, 403206, 103250),
        (701111, 110, 101140), (701211, 120, 101240),
    ]:
        ops.element("elasticBeamColumn", eid, ni, nj, A_stiff, E, I_stiff, TRANS_COROT)


def _define_gusset_springs() -> None:
    """Gusset plate rotational springs (mid-span and corner)."""
    for sid, ni, nj, lb, lc, d_br, mt in [
        (904133, 204113, 204103, 9.1220 * inch, 14.0000 * inch, 8.6300 * inch, MAT_GUSSET_L3_LEFT),
        (904144, 204114, 204104, 9.1220 * inch, 14.0000 * inch, 8.6300 * inch, MAT_GUSSET_L3_RIGHT),
        (902133, 202113, 202103, 9.0551 * inch, 24.0000 * inch, 9.6300 * inch, MAT_GUSSET_L2_LEFT),
        (902144, 202114, 202104, 9.0551 * inch, 24.0000 * inch, 9.6300 * inch, MAT_GUSSET_L2_RIGHT),
        (902166, 202116, 202106, 8.9712 * inch, 24.4375 * inch, 8.6300 * inch, MAT_GUSSET_L2_MID_L),
        (902177, 202117, 202107, 8.9712 * inch, 24.4375 * inch, 8.6300 * inch, MAT_GUSSET_L2_MID_R),
        (903111, 103140, 103141, 7.3731 * inch, 14.0000 * inch, 8.6300 * inch, MAT_GUSSET_L3_COR_L),
        (903199, 103150, 103151, 7.9925 * inch, 21.0000 * inch, 8.6300 * inch, MAT_GUSSET_L3_COR_R),
        (903211, 103240, 103241, 7.3731 * inch, 14.0000 * inch, 8.6300 * inch, MAT_GUSSET_L3_COR_L2),
        (903299, 103250, 103251, 7.9925 * inch, 21.0000 * inch, 8.6300 * inch, MAT_GUSSET_L3_COR_R2),
        (901111, 101140, 101141, 10.2084 * inch, 24.0000 * inch, 9.6300 * inch, MAT_GUSSET_L1_COR_L),
        (901211, 101240, 101241, 10.2084 * inch, 24.0000 * inch, 9.6300 * inch, MAT_GUSSET_L1_COR_R),
    ]:
        spring_gusset(sid, ni, nj, E, fy_g, lb, 0.5000 * inch, lc, d_br, mt)


def _define_brace_members() -> None:
    """Brace elements and ghost braces (fatigue materials already defined in define_materials)."""
    # Brace members
    for bid, ni, nj, sec in [
        (8101100, 101141, 202113, SEC_BRACE_L1),
        (8201100, 101241, 202114, SEC_BRACE_L1),
        (8102100, 103151, 202117, SEC_BRACE_L2),
        (8202100, 103251, 202116, SEC_BRACE_L2),
        (8103100, 103141, 204113, SEC_BRACE_L3),
        (8203100, 103241, 204114, SEC_BRACE_L3),
    ]:
        construct_brace(bid, ni, nj, sec, n_segments, initial_gi, n_integration, TRANS_COROT, Sigma_GI=1.e-9)

    # Ghost braces
    ops.uniaxialMaterial("Elastic", MAT_GHOST_BRACE, 100.0 * ksi)
    for eid, ni, nj in [
        (4101100, 101141, 202113), (4201100, 101241, 202114),
        (4102100, 103151, 202117), (4202100, 103251, 202116),
        (4103100, 103141, 204113), (4203100, 103241, 204114),
    ]:
        ops.element("corotTruss", eid, ni, nj, 0.05 * inch**2, MAT_GHOST_BRACE)


def _define_mf_columns() -> None:
    """Fiber-section columns for the moment frame."""
    for eid, ni, nj, sec in [
        (603100, 313, 411, SEC_COL_L3), (603200, 323, 421, SEC_COL_R202),
        (602100, 213, 311, SEC_COL_L2), (602200, 223, 321, SEC_COL_R204),
        (601100, 113, 211, SEC_COL_L1), (601200, 123, 221, SEC_COL_R206),
    ]:
        construct_fiber_column(eid, ni, nj, sec, 5, 0.0010, 5, TRANS_SELECTED, 0)


def _define_mf_beams() -> None:
    """ModElasticBeam2d beam elements."""
    _ix = lambda i: ((n_stiff_mod + 1.0) / n_stiff_mod) * 0.90 * comp_i * i
    for eid, ni, nj, a, i in [
        (504101, 414, 204112, 51.0000 * inch**2, _ix(8230.00 * inch**4)),
        (504102, 422, 204115, 51.0000 * inch**2, _ix(8230.00 * inch**4)),
        (503100, 314, 322, 32.7000 * inch**2, _ix(2670.00 * inch**4)),
        (502101, 214, 202112, 19.1000 * inch**2, _ix(1070.00 * inch**4)),
        (502102, 222, 202115, 19.1000 * inch**2, _ix(1070.00 * inch**4)),
    ]:
        ops.element("ModElasticBeam2d", eid, ni, nj, a, E, i, k11_2, k33_2, k44_2, TRANS_SELECTED)


def _define_mf_beam_springs() -> None:
    """IMK beam-end springs + pinching shear-tab springs."""
    # IMK springs (beam-end rotation)
    for sid, ni, nj, d, htw, bftf, ry, L, Ls, Lb, My, ix in [
        (904104, 404104, 414, 30.4000, 40.8000, 7.0400, 3.4200, 137.3875, 68.6937, 68.6937, 36723.5000, 8230.00),
        (904202, 422, 404202, 30.4000, 40.8000, 7.0400, 3.4200, 137.3875, 68.6937, 68.6937, 36723.5000, 8230.00),
        (904122, 204102, 204112, 30.4000, 40.8000, 7.0400, 3.4200, 137.3875, 68.6937, 68.6937, 36723.5000, 8230.00),
        (904155, 204105, 204115, 30.4000, 40.8000, 7.0400, 3.4200, 137.3875, 68.6937, 68.6937, 36723.5000, 8230.00),
        (902104, 402104, 214, 18.4000, 35.7000, 5.0600, 1.6900, 135.7000, 67.8500, 67.8500, 8046.5000, 1070.00),
        (902202, 222, 402202, 18.4000, 35.7000, 5.0600, 1.6900, 135.7000, 67.8500, 67.8500, 8046.5000, 1070.00),
        (902122, 202102, 202112, 18.4000, 35.7000, 5.0600, 1.6900, 135.7000, 67.8500, 67.8500, 8046.5000, 1070.00),
        (902155, 202105, 202115, 18.4000, 35.7000, 5.0600, 1.6900, 135.7000, 67.8500, 67.8500, 8046.5000, 1070.00),
    ]:
        spring_imk(sid, ni, nj, E, fy, comp_i * ix * inch**4,
                   d * inch, htw, bftf, ry * inch,
                   L * inch, Ls * inch, Lb * inch,
                   My * kip * inch, 0, composite, 0)

    # Pinching springs (shear tab connections)
    for sid, ni, nj in [(903104, 403104, 314), (903202, 322, 403202)]:
        spring_pinching(sid, ni, nj, 16879.5000 * kip * inch, gap, composite)


def _define_mf_column_springs() -> None:
    """Rigid zero-length springs at column ends."""
    for sid, ni, nj in [
        (904101, 404101, 411), (904201, 404201, 421),
        (903103, 403103, 313), (903203, 403203, 323),
        (903101, 403101, 311), (903201, 403201, 321),
        (902103, 402103, 213), (902203, 402203, 223),
        (902101, 402101, 211), (902201, 402201, 221),
        (901103, 110, 113), (901203, 120, 123),
    ]:
        spring_rigid(sid, ni, nj)


def _define_floor_links() -> None:
    """Rigid truss links between MF and EGF on each floor."""
    for eid, ni, nj in [
        (1004, 404204, 430), (1003, 403204, 330), (1002, 402204, 230),
    ]:
        ops.element("truss", eid, ni, nj, A_stiff, MAT_RIGID)


def _define_egf_columns() -> None:
    """Elastic leaning-column elements for the gravity frame."""
    a_gc = 100000.0000 * inch**2
    i_gc = 100000000.0000 * inch**4
    for eid, ni, nj in [
        (603300, 333, 431), (603400, 343, 441),
        (602300, 233, 331), (602400, 243, 341),
        (601300, 133, 231), (601400, 143, 241),
    ]:
        ops.element("elasticBeamColumn", eid, ni, nj, a_gc, E, i_gc, TRANS_PDELTA)


def _define_egf_beams() -> None:
    """Elastic gravity frame beams."""
    a_gb = 100000.0000 * inch**2
    i_gb = 100000000.0000 * inch**4
    for eid, ni, nj in [
        (504200, 434, 442), (503200, 334, 342), (502200, 234, 242),
    ]:
        ops.element("elasticBeamColumn", eid, ni, nj, a_gb, E, i_gb, TRANS_PDELTA)


def _define_egf_springs() -> None:
    """Zero-stiffness column springs + rigid beam springs for gravity frame."""
    # Column springs (rotation release)
    for sid, ni, nj in [
        (904301, 430, 431), (904401, 440, 441),
        (903303, 330, 333), (903403, 340, 343),
        (903301, 330, 331), (903401, 340, 341),
        (902303, 230, 233), (902403, 240, 243),
        (902301, 230, 231), (902401, 240, 241),
        (901303, 130, 133), (901403, 140, 143),
    ]:
        spring_zero(sid, ni, nj)

    # Beam springs (rigid)
    for sid, ni, nj in [
        (904304, 430, 434), (904402, 440, 442),
        (903304, 330, 334), (903402, 340, 342),
        (902304, 230, 234), (902402, 240, 242),
    ]:
        spring_rigid(sid, ni, nj)


def define_elements() -> None:
    """Build all frame elements in the correct dependency order."""
    _define_geom_transforms()
    _define_panel_zones()
    _define_panel_zone_springs()
    _define_rigid_brace_links()
    _define_gusset_springs()
    _define_brace_members()
    _define_mf_columns()
    _define_mf_beams()
    _define_mf_beam_springs()
    _define_mf_column_springs()
    _define_floor_links()
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
def define_nodal_masses() -> None:
    # Nodal mass definition
    # mass NodeID mx my mz (input in kip * sec**2 / inch converted to consistent mass system)
    mass_factor = kip * sec**2 / inch
    ops.mass(404104, 0.2506 * mass_factor, 1.e-9 * mass_factor, 1.e-9 * mass_factor)
    ops.mass(404204, 0.2506 * mass_factor, 1.e-9 * mass_factor, 1.e-9 * mass_factor)
    ops.mass(430,    1.0810 * mass_factor, 1.e-9 * mass_factor, 1.e-9 * mass_factor)
    ops.mass(440,    1.0810 * mass_factor, 1.e-9 * mass_factor, 1.e-9 * mass_factor)

    ops.mass(403104, 0.3963 * mass_factor, 1.e-9 * mass_factor, 1.e-9 * mass_factor)
    ops.mass(403204, 0.3963 * mass_factor, 1.e-9 * mass_factor, 1.e-9 * mass_factor)
    ops.mass(330,    1.0082 * mass_factor, 1.e-9 * mass_factor, 1.e-9 * mass_factor)
    ops.mass(340,    1.0082 * mass_factor, 1.e-9 * mass_factor, 1.e-9 * mass_factor)

    ops.mass(402104, 0.3963 * mass_factor, 1.e-9 * mass_factor, 1.e-9 * mass_factor)
    ops.mass(402204, 0.3963 * mass_factor, 1.e-9 * mass_factor, 1.e-9 * mass_factor)
    ops.mass(230,    1.0082 * mass_factor, 1.e-9 * mass_factor, 1.e-9 * mass_factor)
    ops.mass(240,    1.0082 * mass_factor, 1.e-9 * mass_factor, 1.e-9 * mass_factor)

    ops.constraints("Plain")


def define_gravity_loads() -> None:
    ops.timeSeries("Linear", 100)
    ops.pattern("Plain", 100, 100)

    # MF COLUMNS LOADS (kips -> N)
    ops.load(404103, 0.0, -50.681 * kip, 0.0)
    ops.load(404203, 0.0, -50.681 * kip, 0.0)
    ops.load(403103, 0.0, -59.963 * kip, 0.0)
    ops.load(403203, 0.0, -59.963 * kip, 0.0)
    ops.load(402103, 0.0, -59.963 * kip, 0.0)
    ops.load(402203, 0.0, -59.963 * kip, 0.0)

    # EGF COLUMN LOADS (kips -> N)
    ops.load(430, 0.0, -516.150000 * kip, 0.0)
    ops.load(440, 0.0, -516.150000 * kip, 0.0)
    ops.load(330, 0.0, -576.900000 * kip, 0.0)
    ops.load(340, 0.0, -576.900000 * kip, 0.0)
    ops.load(230, 0.0, -576.900000 * kip, 0.0)
    ops.load(240, 0.0, -576.900000 * kip, 0.0)

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def _run_eigen(n_modes: int = 3) -> list[float]:
    """Run eigen analysis and return natural periods (seconds)."""
    lam = ops.eigen(n_modes)
    periods = [2.0 * np.pi / np.sqrt(l) for l in lam]
    for i, t in enumerate(periods, 1):
        print(f"T{i} = {t:.3f} s")
    return periods


def _define_rayleigh_damping(w1: float, w3: float) -> None:
    """Assign Rayleigh damping to frame elements, mass nodes, and springs."""
    a0 = ZETA * 2.0 * w1 * w3 / (w1 + w3)
    a1 = ZETA * 2.0 / (w1 + w3)
    a1_mod = a1 * (1.0 + n_stiff_mod) / n_stiff_mod

    frame_eles = [603100, 603200, 602100, 602200, 601100, 601200,
                  504101, 504102, 503100, 502101, 502102]
    mass_nodes = [402104, 402204, 230, 240,
                  403104, 403204, 330, 340,
                  404104, 404204, 430, 440]

    ops.region(1, "-ele", *frame_eles, "-rayleigh", 0.0, 0.0, a1_mod, 0.0)
    ops.region(2, "-node", *mass_nodes, "-rayleigh", a0, 0.0, 0.0, 0.0)
    ops.region(3, "-eleRange", 900000, 999999, "-rayleigh", 0.0, 0.0, a1_mod / 10.0, 0.0)


def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10, ctrl_node: int = 404104, ctrl_dof: int = 2) -> None:
    """Apply gravity loads using SmartAnalyze (Static) and collect responses."""
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
        analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
        odb.fetch_response_step()
    analysis.close()
    ops.loadConst("-time", 0.0)


def run_dynamic(odb: "opst.post.CreateODB", periods: list[float],
                gm_file: Path, output_dir: Path,
                gm_dt: float = 0.01, gm_points: int = 2495,
                eq_sf: float = 1.0, fv_duration: float = 10.0,
                max_run_time: float = 600.0) -> None:
    """Run transient earthquake analysis using DynamicAnalysisCollapseSolverX."""
    w1 = 2.0 * np.pi / periods[0]
    w3 = 2.0 * np.pi / periods[2]
    _define_rayleigh_damping(w1, w3)

    gm_duration = gm_dt * gm_points
    tot_time = gm_dt * round((gm_duration + fv_duration) / gm_dt)
    dt_anal = 0.5 * gm_dt

    ops.timeSeries("Path", 200, "-dt", gm_dt, "-filePath", str(gm_file), "-factor", eq_sf * g_const)
    ops.pattern("UniformExcitation", 200, 1, "-accel", 200)

    mf_nodes = [402104, 403104, 404104]
    egf_nodes = [230, 330, 430]

    dynamic_analysis_collapse_solver(
        dt=gm_dt, dt_anal_step=dt_anal, gm_time=tot_time,
        num_stories=n_stories, drift_limit=0.15,
        mf_floor_nodes=mf_nodes, egf_floor_nodes=egf_nodes,
        h1=h1_story, htyp=h_typ, trace_gf_drift=True,
        max_run_time=max_run_time, odb=odb, output_dir=output_dir
    )


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, apply gravity, run dynamic analysis, return ODB."""
    output_dir.mkdir(parents=True, exist_ok=True)

    init_model()
    define_materials()
    define_sections()
    define_nodes()

    define_elements()
    define_boundary_conditions()

    vis_nodes(output_dir)

    vis_model(output_dir)

    odb = create_odb(odb_tag=1, output_dir=output_dir)

    define_nodal_masses()
    define_gravity_loads()

    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    # Eigen analysis (before gravity — needed for damping)
    periods = _run_eigen(n_modes=3)

    # Save periods
    with open(output_dir / "EigenPeriod.out", "w") as f:
        for t in periods:
            f.write(f"{t}\n")

    # Gravity analysis
    run_gravity(odb, n_steps=10)
    print("Gravity Analysis Done.")

    # Dynamic earthquake analysis
    gm_file = Path(__file__).parent / "ground_motions" / "NR94cnp.txt"
    run_dynamic(odb, periods=periods, gm_file=gm_file, output_dir=output_dir,
                max_run_time=10.0 * 60.0)

    print("Dynamic Analysis Done.")

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and render deformed-shape visualisation."""
    odb.save_response()

    if not _headless():
        vis_defo(output_dir, "vis_05_defo_dynamic.html", odb_tag=1, resp_dof="UX")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    ops.wipe()
