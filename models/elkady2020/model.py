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
SEC_COL_L3 = 101
SEC_COL_L2 = 103
SEC_COL_L1 = 105

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

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    # Circular HSS Sections
    # FiberCHSS secID matID d t nfdy nfty
    fiber_chss(SEC_BRACE_L1, MAT_BRACE_FAT_L1, 9.6300 * inch, 0.5000 * inch, 12, 4)
    fiber_chss(SEC_BRACE_L2, MAT_BRACE_FAT_L2, 8.6300 * inch, 0.5000 * inch, 12, 4)
    fiber_chss(SEC_BRACE_L3, MAT_BRACE_FAT_L3, 8.6300 * inch, 0.3220 * inch, 12, 4)

    # Wide-Flange Sections for Columns (all identical geometry in this model)
    # fiber_wf(secID, matID, d, bf, tf, tw, nfdw, nftw, nfbf, nftf)
    fiber_wf(101, MAT_VOCE_CHABOCHE, 13.1000 * inch, 12.3000 * inch, 1.1100 * inch, 0.7100 * inch, 6, 2, 6, 2)
    fiber_wf(102, MAT_VOCE_CHABOCHE, 13.1000 * inch, 12.3000 * inch, 1.1100 * inch, 0.7100 * inch, 6, 2, 6, 2)
    fiber_wf(103, MAT_VOCE_CHABOCHE, 13.1000 * inch, 12.3000 * inch, 1.1100 * inch, 0.7100 * inch, 6, 2, 6, 2)
    fiber_wf(104, MAT_VOCE_CHABOCHE, 13.1000 * inch, 12.3000 * inch, 1.1100 * inch, 0.7100 * inch, 6, 2, 6, 2)
    fiber_wf(105, MAT_VOCE_CHABOCHE, 13.1000 * inch, 12.3000 * inch, 1.1100 * inch, 0.7100 * inch, 6, 2, 6, 2)
    fiber_wf(106, MAT_VOCE_CHABOCHE, 13.1000 * inch, 12.3000 * inch, 1.1100 * inch, 0.7100 * inch, 6, 2, 6, 2)

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
def define_elements() -> None:
    # --- Geometric Transformations ---
    ops.geomTransf("Linear", TRANS_LINEAR)
    ops.geomTransf("PDelta", TRANS_PDELTA)
    ops.geomTransf("Corotational", TRANS_COROT)

    # --- Panel Zone Nodes and Elastic Elements ---
    # construct_panel_rectangle(axis, floor, x_axis, y_floor, E, A_panel, I_panel, d_col, d_beam, transf_tag)
    construct_panel_rectangle(1, 4, axis_1, floor_4, E, A_stiff, I_stiff, 13.10 * inch, 30.40 * inch, TRANS_SELECTED)
    construct_panel_rectangle(2, 4, axis_2, floor_4, E, A_stiff, I_stiff, 13.10 * inch, 30.40 * inch, TRANS_SELECTED)
    construct_panel_rectangle(1, 3, axis_1, floor_3, E, A_stiff, I_stiff, 13.10 * inch, 21.50 * inch, TRANS_SELECTED)
    construct_panel_rectangle(2, 3, axis_2, floor_3, E, A_stiff, I_stiff, 13.10 * inch, 21.50 * inch, TRANS_SELECTED)
    construct_panel_rectangle(1, 2, axis_1, floor_2, E, A_stiff, I_stiff, 13.10 * inch, 18.40 * inch, TRANS_SELECTED)
    construct_panel_rectangle(2, 2, axis_2, floor_2, E, A_stiff, I_stiff, 13.10 * inch, 18.40 * inch, TRANS_SELECTED)

    # --- Panel Zone Springs ---
    # spring_pz(p_elm, node_i, node_j, E, mu, fy, tw_col, tdp, d_col, d_beam, tf_col, bf_col, ix_col, trib, ts, response_id, transf_tag, sigma_pz)
    spring_pz(904100, 404109, 404110, E, mu, fy * 1.0, 0.71 * inch, 0.00 * inch, 13.10 * inch, 30.40 * inch, 1.11 * inch, 12.30 * inch, 1070.00 * inch**4, 3.500 * inch, 4.000 * inch, 2, TRANS_LINEAR)
    spring_pz(904200, 404209, 404210, E, mu, fy * 1.0, 0.71 * inch, 0.00 * inch, 13.10 * inch, 30.40 * inch, 1.11 * inch, 12.30 * inch, 1070.00 * inch**4, 3.500 * inch, 4.000 * inch, 2, TRANS_LINEAR)
    spring_pz(903100, 403109, 403110, E, mu, fy * 1.0, 0.71 * inch, 0.00 * inch, 13.10 * inch, 21.50 * inch, 1.11 * inch, 12.30 * inch, 1070.00 * inch**4, 3.500 * inch, 4.000 * inch, 2, TRANS_LINEAR)
    spring_pz(903200, 403209, 403210, E, mu, fy * 1.0, 0.71 * inch, 0.00 * inch, 13.10 * inch, 21.50 * inch, 1.11 * inch, 12.30 * inch, 1070.00 * inch**4, 3.500 * inch, 4.000 * inch, 2, TRANS_LINEAR)
    spring_pz(902100, 402109, 402110, E, mu, fy * 1.0, 0.71 * inch, 0.00 * inch, 13.10 * inch, 18.40 * inch, 1.11 * inch, 12.30 * inch, 1070.00 * inch**4, 3.500 * inch, 4.000 * inch, 2, TRANS_LINEAR)
    spring_pz(902200, 402209, 402210, E, mu, fy * 1.0, 0.71 * inch, 0.00 * inch, 13.10 * inch, 18.40 * inch, 1.11 * inch, 12.30 * inch, 1070.00 * inch**4, 3.500 * inch, 4.000 * inch, 2, TRANS_LINEAR)

    # --- Middle Rigid Links ---
    ops.element("elasticBeamColumn", 704122, 204101, 204102, A_stiff, E, I_stiff, TRANS_SELECTED)
    ops.element("elasticBeamColumn", 704133, 204101, 204103, A_stiff, E, I_stiff, TRANS_COROT)
    ops.element("elasticBeamColumn", 704144, 204101, 204104, A_stiff, E, I_stiff, TRANS_COROT)
    ops.element("elasticBeamColumn", 704155, 204101, 204105, A_stiff, E, I_stiff, TRANS_SELECTED)

    ops.element("elasticBeamColumn", 702122, 202101, 202102, A_stiff, E, I_stiff, TRANS_SELECTED)
    ops.element("elasticBeamColumn", 702133, 202101, 202103, A_stiff, E, I_stiff, TRANS_COROT)
    ops.element("elasticBeamColumn", 702144, 202101, 202104, A_stiff, E, I_stiff, TRANS_COROT)
    ops.element("elasticBeamColumn", 702155, 202101, 202105, A_stiff, E, I_stiff, TRANS_SELECTED)
    ops.element("elasticBeamColumn", 702166, 202101, 202106, A_stiff, E, I_stiff, TRANS_COROT)
    ops.element("elasticBeamColumn", 702177, 202101, 202107, A_stiff, E, I_stiff, TRANS_COROT)

    # --- Corner Rigid Links ---
    ops.element("elasticBeamColumn", 703111, 403110, 103140, A_stiff, E, I_stiff, TRANS_COROT)
    ops.element("elasticBeamColumn", 703199, 403199, 103150, A_stiff, E, I_stiff, TRANS_COROT)
    ops.element("elasticBeamColumn", 703211, 403208, 103240, A_stiff, E, I_stiff, TRANS_COROT)
    ops.element("elasticBeamColumn", 703299, 403206, 103250, A_stiff, E, I_stiff, TRANS_COROT)

    ops.element("elasticBeamColumn", 701111, 110, 101140, A_stiff, E, I_stiff, TRANS_COROT)
    ops.element("elasticBeamColumn", 701211, 120, 101240, A_stiff, E, I_stiff, TRANS_COROT)

    # --- Beam Mid-Span Gusset Plate Springs ---
    # spring_gusset(SpringID, NodeI, NodeJ, E, fy, Lb, tp, Lc, d_Brace, matTag)
    spring_gusset(904133, 204113, 204103, E, fy_g, 9.1220 * inch, 0.5000 * inch, 14.0000 * inch, 8.6300 * inch, MAT_GUSSET_L3_LEFT)
    spring_gusset(904144, 204114, 204104, E, fy_g, 9.1220 * inch, 0.5000 * inch, 14.0000 * inch, 8.6300 * inch, MAT_GUSSET_L3_RIGHT)

    spring_gusset(902133, 202113, 202103, E, fy_g, 9.0551 * inch, 0.5000 * inch, 24.0000 * inch, 9.6300 * inch, MAT_GUSSET_L2_LEFT)
    spring_gusset(902144, 202114, 202104, E, fy_g, 9.0551 * inch, 0.5000 * inch, 24.0000 * inch, 9.6300 * inch, MAT_GUSSET_L2_RIGHT)
    spring_gusset(902166, 202116, 202106, E, fy_g, 8.9712 * inch, 0.5000 * inch, 24.4375 * inch, 8.6300 * inch, MAT_GUSSET_L2_MID_L)
    spring_gusset(902177, 202117, 202107, E, fy_g, 8.9712 * inch, 0.5000 * inch, 24.4375 * inch, 8.6300 * inch, MAT_GUSSET_L2_MID_R)

    # --- Corner Gusset Plate Springs ---
    spring_gusset(903111, 103140, 103141, E, fy_g, 7.3731 * inch, 0.5000 * inch, 14.0000 * inch, 8.6300 * inch, MAT_GUSSET_L3_COR_L)
    spring_gusset(903199, 103150, 103151, E, fy_g, 7.9925 * inch, 0.5000 * inch, 21.0000 * inch, 8.6300 * inch, MAT_GUSSET_L3_COR_R)
    spring_gusset(903211, 103240, 103241, E, fy_g, 7.3731 * inch, 0.5000 * inch, 14.0000 * inch, 8.6300 * inch, MAT_GUSSET_L3_COR_L2)
    spring_gusset(903299, 103250, 103251, E, fy_g, 7.9925 * inch, 0.5000 * inch, 21.0000 * inch, 8.6300 * inch, MAT_GUSSET_L3_COR_R2)

    spring_gusset(901111, 101140, 101141, E, fy_g, 10.2084 * inch, 0.5000 * inch, 24.0000 * inch, 9.6300 * inch, MAT_GUSSET_L1_COR_L)
    spring_gusset(901211, 101240, 101241, E, fy_g, 10.2084 * inch, 0.5000 * inch, 24.0000 * inch, 9.6300 * inch, MAT_GUSSET_L1_COR_R)

    # --- Fatigue Materials ---
    # fatigue_mat(matID, SecType, fy, E, L, ry, wt, ht, bt)
    fatigue_mat(MAT_BRACE_BASE_L1, 2, fy_b, E, 202.3709 * inch, 3.2400 * inch, 20.7000, 0.0 * inch, 0.0 * inch)
    fatigue_mat(MAT_BRACE_BASE_L2, 2, fy_b, E, 200.3084 * inch, 2.8900 * inch, 18.5000, 0.0 * inch, 0.0 * inch)
    fatigue_mat(MAT_BRACE_BASE_L3, 2, fy_b, E, 195.5584 * inch, 2.9500 * inch, 28.8000, 0.0 * inch, 0.0 * inch)

    # --- Brace Members ---
    # construct_brace(eleID, NodeI, NodeJ, secID, numSeg, Initial_GI, nInt, Trans_tag, Sigma_GI=0.0)
    construct_brace(8101100, 101141, 202113, SEC_BRACE_L1, n_segments, initial_gi, n_integration, TRANS_COROT, Sigma_GI=1.e-9)
    construct_brace(8201100, 101241, 202114, SEC_BRACE_L1, n_segments, initial_gi, n_integration, TRANS_COROT, Sigma_GI=1.e-9)

    construct_brace(8102100, 103151, 202117, SEC_BRACE_L2, n_segments, initial_gi, n_integration, TRANS_COROT, Sigma_GI=1.e-9)
    construct_brace(8202100, 103251, 202116, SEC_BRACE_L2, n_segments, initial_gi, n_integration, TRANS_COROT, Sigma_GI=1.e-9)

    construct_brace(8103100, 103141, 204113, SEC_BRACE_L3, n_segments, initial_gi, n_integration, TRANS_COROT, Sigma_GI=1.e-9)
    construct_brace(8203100, 103241, 204114, SEC_BRACE_L3, n_segments, initial_gi, n_integration, TRANS_COROT, Sigma_GI=1.e-9)

    # --- Ghost Braces ---
    ops.uniaxialMaterial("Elastic", MAT_GHOST_BRACE, 100.0 * ksi)
    ops.element("corotTruss", 4101100, 101141, 202113, 0.05 * inch**2, MAT_GHOST_BRACE)
    ops.element("corotTruss", 4201100, 101241, 202114, 0.05 * inch**2, MAT_GHOST_BRACE)
    ops.element("corotTruss", 4102100, 103151, 202117, 0.05 * inch**2, MAT_GHOST_BRACE)
    ops.element("corotTruss", 4202100, 103251, 202116, 0.05 * inch**2, MAT_GHOST_BRACE)
    ops.element("corotTruss", 4103100, 103141, 204113, 0.05 * inch**2, MAT_GHOST_BRACE)
    ops.element("corotTruss", 4203100, 103241, 204114, 0.05 * inch**2, MAT_GHOST_BRACE)

    # --- Columns (Fiber Sections + Construction) ---
    # Columns L3
    construct_fiber_column(603100, 313, 411, SEC_COL_L3, 5, 0.0010, 5, TRANS_SELECTED, 0)
    construct_fiber_column(603200, 323, 421, 102, 5, 0.0010, 5, TRANS_SELECTED, 0)
    # Columns L2
    construct_fiber_column(602100, 213, 311, SEC_COL_L2, 5, 0.0010, 5, TRANS_SELECTED, 0)
    construct_fiber_column(602200, 223, 321, 104, 5, 0.0010, 5, TRANS_SELECTED, 0)
    # Columns L1
    construct_fiber_column(601100, 113, 211, SEC_COL_L1, 5, 0.0010, 5, TRANS_SELECTED, 0)
    construct_fiber_column(601200, 123, 221, 106, 5, 0.0010, 5, TRANS_SELECTED, 0)

    # --- Beams (ModElasticBeam2d) ---
    ops.element("ModElasticBeam2d", 504101, 414, 204112, 51.0000 * inch**2, E, ((n_stiff_mod + 1.0) / n_stiff_mod) * 0.90 * comp_i * 8230.00 * inch**4, k11_2, k33_2, k44_2, TRANS_SELECTED)
    ops.element("ModElasticBeam2d", 504102, 422, 204115, 51.0000 * inch**2, E, ((n_stiff_mod + 1.0) / n_stiff_mod) * 0.90 * comp_i * 8230.00 * inch**4, k11_2, k33_2, k44_2, TRANS_SELECTED)
    ops.element("ModElasticBeam2d", 503100, 314, 322, 32.7000 * inch**2, E, ((n_stiff_mod + 1.0) / n_stiff_mod) * 0.90 * comp_i * 2670.00 * inch**4, k11_2, k33_2, k44_2, TRANS_SELECTED)
    ops.element("ModElasticBeam2d", 502101, 214, 202112, 19.1000 * inch**2, E, ((n_stiff_mod + 1.0) / n_stiff_mod) * 0.90 * comp_i * 1070.00 * inch**4, k11_2, k33_2, k44_2, TRANS_SELECTED)
    ops.element("ModElasticBeam2d", 502102, 222, 202115, 19.1000 * inch**2, E, ((n_stiff_mod + 1.0) / n_stiff_mod) * 0.90 * comp_i * 1070.00 * inch**4, k11_2, k33_2, k44_2, TRANS_SELECTED)

    # --- MF Beam Springs (Spring_IMK) ---
    # spring_imk(spring_id, node_i, node_j, E, Fy, Ix, d, htw, bftf, ry, L, Ls, Lb, My, PgPye, composite_flag, connection_type)
    spring_imk(904104, 404104, 414, E, fy, comp_i * 8230.00 * inch**4, 30.4000 * inch, 40.8000, 7.0400, 3.4200 * inch, 137.3875 * inch, 68.6937 * inch, 68.6937 * inch, 36723.5000 * kip * inch, 0, composite, 0)
    spring_imk(904202, 422, 404202, E, fy, comp_i * 8230.00 * inch**4, 30.4000 * inch, 40.8000, 7.0400, 3.4200 * inch, 137.3875 * inch, 68.6937 * inch, 68.6937 * inch, 36723.5000 * kip * inch, 0, composite, 0)
    spring_imk(904122, 204102, 204112, E, fy, comp_i * 8230.00 * inch**4, 30.4000 * inch, 40.8000, 7.0400, 3.4200 * inch, 137.3875 * inch, 68.6937 * inch, 68.6937 * inch, 36723.5000 * kip * inch, 0, composite, 0)
    spring_imk(904155, 204105, 204115, E, fy, comp_i * 8230.00 * inch**4, 30.4000 * inch, 40.8000, 7.0400, 3.4200 * inch, 137.3875 * inch, 68.6937 * inch, 68.6937 * inch, 36723.5000 * kip * inch, 0, composite, 0)
    
    spring_imk(902104, 402104, 214, E, fy, comp_i * 1070.00 * inch**4, 18.4000 * inch, 35.7000, 5.0600, 1.6900 * inch, 135.7000 * inch, 67.8500 * inch, 67.8500 * inch, 8046.5000 * kip * inch, 0, composite, 0)
    spring_imk(902202, 222, 402202, E, fy, comp_i * 1070.00 * inch**4, 18.4000 * inch, 35.7000, 5.0600, 1.6900 * inch, 135.7000 * inch, 67.8500 * inch, 67.8500 * inch, 8046.5000 * kip * inch, 0, composite, 0)
    spring_imk(902122, 202102, 202112, E, fy, comp_i * 1070.00 * inch**4, 18.4000 * inch, 35.7000, 5.0600, 1.6900 * inch, 135.7000 * inch, 67.8500 * inch, 67.8500 * inch, 8046.5000 * kip * inch, 0, composite, 0)
    spring_imk(902155, 202105, 202115, E, fy, comp_i * 1070.00 * inch**4, 18.4000 * inch, 35.7000, 5.0600, 1.6900 * inch, 135.7000 * inch, 67.8500 * inch, 67.8500 * inch, 8046.5000 * kip * inch, 0, composite, 0)

    # --- conventional shear tab springs (Spring_Pinching) ---
    # spring_pinching(spring_id, node_i, node_j, M_p, gap, response_id)
    spring_pinching(903104, 403104, 314, 16879.5000 * kip * inch, gap, composite)
    spring_pinching(903202, 322, 403202, 16879.5000 * kip * inch, gap, composite)

    # --- MF Column Springs (Spring_Rigid) ---
    spring_rigid(904101, 404101, 411)
    spring_rigid(904201, 404201, 421)
    spring_rigid(903103, 403103, 313)
    spring_rigid(903203, 403203, 323)
    spring_rigid(903101, 403101, 311)
    spring_rigid(903201, 403201, 321)
    spring_rigid(902103, 402103, 213)
    spring_rigid(902203, 402203, 223)
    spring_rigid(902101, 402101, 211)
    spring_rigid(902201, 402201, 221)
    spring_rigid(901103, 110, 113)
    spring_rigid(901203, 120, 123)

    # --- Floor Links ---
    ops.element("truss", 1004, 404204, 430, A_stiff, MAT_RIGID)
    ops.element("truss", 1003, 403204, 330, A_stiff, MAT_RIGID)
    ops.element("truss", 1002, 402204, 230, A_stiff, MAT_RIGID)

    # --- EGF Columns ---
    ops.element("elasticBeamColumn", 603300, 333, 431, 100000.0000 * inch**2, E, 100000000.0000 * inch**4, TRANS_PDELTA)
    ops.element("elasticBeamColumn", 603400, 343, 441, 100000.0000 * inch**2, E, 100000000.0000 * inch**4, TRANS_PDELTA)
    ops.element("elasticBeamColumn", 602300, 233, 331, 100000.0000 * inch**2, E, 100000000.0000 * inch**4, TRANS_PDELTA)
    ops.element("elasticBeamColumn", 602400, 243, 341, 100000.0000 * inch**2, E, 100000000.0000 * inch**4, TRANS_PDELTA)
    ops.element("elasticBeamColumn", 601300, 133, 231, 100000.0000 * inch**2, E, 100000000.0000 * inch**4, TRANS_PDELTA)
    ops.element("elasticBeamColumn", 601400, 143, 241, 100000.0000 * inch**2, E, 100000000.0000 * inch**4, TRANS_PDELTA)

    # --- EGF Beams ---
    ops.element("elasticBeamColumn", 504200, 434, 442, 100000.0000 * inch**2, E, 100000000.0000 * inch**4, TRANS_PDELTA)
    ops.element("elasticBeamColumn", 503200, 334, 342, 100000.0000 * inch**2, E, 100000000.0000 * inch**4, TRANS_PDELTA)
    ops.element("elasticBeamColumn", 502200, 234, 242, 100000.0000 * inch**2, E, 100000000.0000 * inch**4, TRANS_PDELTA)

    # --- EGF Columns Springs (Spring_Zero) ---
    spring_zero(904301, 430, 431)
    spring_zero(904401, 440, 441)
    spring_zero(903303, 330, 333)
    spring_zero(903403, 340, 343)
    spring_zero(903301, 330, 331)
    spring_zero(903401, 340, 341)
    spring_zero(902303, 230, 233)
    spring_zero(902403, 240, 243)
    spring_zero(902301, 230, 231)
    spring_zero(902401, 240, 241)
    spring_zero(901303, 130, 133)
    spring_zero(901403, 140, 143)

    # --- EGF Beams Springs (Spring_Rigid) ---
    spring_rigid(904304, 430, 434)
    spring_rigid(904402, 440, 442)
    spring_rigid(903304, 330, 334)
    spring_rigid(903402, 340, 342)
    spring_rigid(902304, 230, 234)
    spring_rigid(902402, 240, 242)

# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(odb_tag: int = 1) -> "opst.post.CreateODB":
    """Initialize ODB database and snapshot geometry topology."""
    odb = opst.post.CreateODB(odb_tag=odb_tag)
    odb.save_model_data()
    return odb

# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_masses() -> None:
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

def define_lateral_loads() -> None:
    # Ground motion loading (UniformExcitation)
    # File path is set to relative 'ground_motions' subfolder per standards
    ops.timeSeries(
        "Path", 200,
        "-dt", 0.01 * sec,
        "-filePath", str(Path(__file__).parent / "ground_motions" / "NR94cnp.txt"),
        "-factor", 1.0 * g_const
    )
    ops.pattern("UniformExcitation", 200, 1, "-accel", 200)

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10, ctrl_node: int = 404104, ctrl_dof: int = 2) -> None:
    """Apply gravity loads using SmartAnalyze (Static) and collect responses."""
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-5, 60)
    ops.algorithm("Newton")
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

def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + transient dynamic analysis, return ODB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))
    
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    
    # Visualisation Stage V1 (Nodes + supports)
    vis_nodes(output_dir)
    
    define_elements()
    
    # Visualisation Stage V2 (Full geometry)
    vis_model(output_dir)
    
    # Create ODB
    odb = opst.post.CreateODB(odb_tag=1)
    odb.save_model_data()
    
    define_masses()
    define_gravity_loads()
    
    # Visualisation Stage V3 (Loads)
    vis_loads(output_dir)
    
    # Visualisation Stage V4 (Pre-analysis)
    vis_pre_analysis(output_dir)
    
    # Eigenvalue analysis before gravity
    n_eigen = 3
    lambda_n = ops.eigen(n_eigen)
    w1 = lambda_n[0]**0.5
    w3 = lambda_n[2]**0.5
    T1 = round(2.0 * np.pi / w1 * 1000.0) / 1000.0
    T3 = round(2.0 * np.pi / w3 * 1000.0) / 1000.0
    print(f"T1 = {T1} s")
    print(f"T3 = {T3} s")
    
    # Save periods
    with open(output_dir / "EigenPeriod.out", "w") as f:
        f.write(f"{T1}\n{T3}\n")
    
    # 1. Run Gravity Analysis
    run_gravity(odb, n_steps=10)
    print("Gravity Analysis Done.")
    
    # 2. Run Rayleigh Damping and Dynamic Analysis
    # Rayleigh Damping coefficients based on first and third modes
    zeta_val = 0.020
    a0 = zeta_val * 2.0 * w1 * w3 / (w1 + w3)
    a1 = zeta_val * 2.0 / (w1 + w3)
    a1_mod = a1 * (1.0 + n_stiff_mod) / n_stiff_mod
    
    # Define Rayleigh damping region elements/nodes
    # region 1: main frames elms
    region1_eles = [603100, 603200, 602100, 602200, 601100, 601200, 504101, 504102, 503100, 502101, 502102]
    # region 2: main floor nodes
    region2_nodes = [402104, 402204, 230, 240, 403104, 403204, 330, 340, 404104, 404204, 430, 440]
    
    ops.region(1, "-ele", *region1_eles, "-rayleigh", 0.0, 0.0, a1_mod, 0.0)
    ops.region(2, "-node", *region2_nodes, "-rayleigh", a0, 0.0, 0.0, 0.0)
    ops.region(3, "-eleRange", 900000, 999999, "-rayleigh", 0.0, 0.0, a1_mod / 10.0, 0.0)
    
    # Define Dynamic Loading
    define_lateral_loads()
    
    # Solver execution
    gm_dt = 0.01 * sec
    dt_analysis = 0.5 * gm_dt
    gm_points = 2495
    fv_duration = 10.0 * sec
    gm_time = gm_dt * gm_points
    tot_time = gm_time + fv_duration
    max_run_time = 10.0 * 60.0 * sec  # 10 minutes
    
    mf_floor_nodes = [402104, 403104, 404104]
    egf_floor_nodes = [230, 330, 430]
    
    dynamic_analysis_collapse_solver(
        dt=gm_dt,
        dt_anal_step=dt_analysis,
        gm_time=tot_time,
        num_stories=n_stories,
        drift_limit=0.15,
        mf_floor_nodes=mf_floor_nodes,
        egf_floor_nodes=egf_floor_nodes,
        h1=h1_story,
        htyp=h_typ,
        trace_gf_drift=True,
        max_run_time=max_run_time,
        odb=odb,
        output_dir=output_dir
    )
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
