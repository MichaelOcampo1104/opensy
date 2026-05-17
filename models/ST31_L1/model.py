# ── 0. FILE HEADER ──────────────────────────────────────────────────────────────
"""
Model    : ST31_L1 — Underground Box-with_leg-Frame Structure (Cut-and-Cover)
UniqueID : ST31_L1
Author   : Michael Ocampo
Date     : 2026-05-13
Purpose  : 2D soil-structure interaction analysis of a cut-and-cover underground
           structure with diaphragm walls and base slab on Winkler spring supports.
Ref      : <paper / standard reference>
Units    : N, mm, MPa
"""
# ── 1. IMPORTS ───────────────────────────────────────────────────────────────────
import numpy as np

# Compatibility: opstool v0.8.7 uses deprecated np.NAN (patch BEFORE opstool import)
np.NAN = np.nan

import openseespy.opensees as ops
import opstool as opst
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import vis_nodes, vis_model, _headless

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────────
# ── Materials
MAT_CONCRETE = 1       # elastic section material 
MAT_SOIL_1   = 2       # ENT — layer 1  ( 0 m  to  -6 m)
MAT_SOIL_2   = 3       # ENT — layer 2  (-6 m  to -12 m)
MAT_SOIL_3   = 4       # ENT — layer 3  (-12 m to -18 m)
MAT_SOIL_4   = 5       # ENT — layer 4  (-18 m to -24 m)
MAT_SOIL_5   = 6       # ENT — layer 5  (-24 m to -32 m)
MAT_SOIL_SLAB = 7       # Vertical subgrade reaction for the slab

# ── Sections
SEC_DWALL    = 1
SEC_SLAB     = 2

# ── Beam integrations
INT_DWALL    = 1
INT_SLAB     = 2

# ── Geometric transformations
TRANSF_DWALL = 1
TRANSF_SLAB  = 2

# -- element partions
n_ele_wall  = 32
n_ele_slab  = 9 
n_node_slab = n_ele_slab + 1
n_node_wall = n_ele_wall + 1 #33

# ── Left wall nodes (1–33)
NODE_LWALL_TOP  = 1
NODE_LWALL_TOP_SLAB = 3   # y = -2 000 mm (1 + 2 = 3)
NODE_LWALL_SLAB = 11      # y = -10 000 mm
NODE_LWALL_BASE = 33      # y = -32 000 mm

# ── Right wall nodes (34–66)
NODE_RWALL_TOP  = 34
NODE_RWALL_TOP_SLAB = 36  # y = -2 000 mm (34 + 2 = 36)
NODE_RWALL_SLAB = 44      # y = -10 000 mm (34 + 10 = 44)
NODE_RWALL_BASE = 66      # y = -32 000 mm (34 + 32 = 66)

# ── Slab nodes (67-74)
NODE_SLAB_START = 67
NODE_SLAB_END   = NODE_SLAB_START + n_ele_slab - 2

# ── Top Slab nodes (75-82)
NODE_TOP_SLAB_START = 75
NODE_TOP_SLAB_END   = NODE_TOP_SLAB_START + n_ele_slab - 2

# ── Soil node ranges (101–133 left, 134–162 right)
NODE_SOIL_L_START = 101
NODE_SOIL_R_START = 101 + n_node_wall
NODE_SOIL_S_START = 300

# ── Spring element ranges (100–130 left, 200–230 right)
ELE_SPRING_L_START = 100
ELE_SPRING_R_START = 200
ELE_SPRING_S_START = 300 # Range for slab springs

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────────
h_dwall    = 32000.0 * mm
t_dwall    = 1000.0  * mm
t_slab     = 800.0   * mm
l_center   = 9000.0  * mm        # centre-to-centre wall spacing
depth_slab = 10000.0 * mm
depth_top_slab = 2000.0 * mm
elem_size  = 1000.0  * mm

# ── Concrete properties
fc = 40.0 * MPa
Ec = 4700.0 * (fc / MPa)**0.5 * MPa

# ── Cross-section properties (per 1 000 mm strip)
b_strip = 1000.0 * mm
A_dwall = b_strip * t_dwall
I_dwall = b_strip * t_dwall**3 / 12.0
A_slab  = b_strip * t_slab
I_slab  = b_strip * t_slab**3 / 12.0

# ── Soil spring stiffnesses (PLACEHOLDER — replace with k_h × tributary area)
#   k_spring = k_h · 1000 mm · 1000 mm
k_soil_1 =    10_000.0 * N / mm  # (≈ k_h = 0.01 MPa/mm)
k_soil_2 =    20_000.0 * N / mm
k_soil_3 =    30_000.0 * N / mm
k_soil_4 =    40_000.0 * N / mm
k_soil_5 =    50_000.0 * N / mm
k_v_slab =    40_000.0 * N / mm  # (Vertical subgrade modulus × tributary area)

# ── Physical constants
gamma_w  = 9.81e-6       # N/mm³  (unit weight of water)

# Helper: soil layer → material tag
def _soil_mat_for_node(i: int) -> int:
    """Return MAT_SOIL_X for a wall node at 0-based index *i* from top."""
    if i < 6:
        return MAT_SOIL_1
    elif i < 12:
        return MAT_SOIL_2
    elif i < 18:
        return MAT_SOIL_3
    elif i < 24:
        return MAT_SOIL_4
    else:
        return MAT_SOIL_5

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)

# ── 5. MATERIALS ──────────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Compression-only Winkler spring materials (ENT)."""
    ops.uniaxialMaterial("ENT", MAT_SOIL_1, k_soil_1)
    ops.uniaxialMaterial("ENT", MAT_SOIL_2, k_soil_2)
    ops.uniaxialMaterial("ENT", MAT_SOIL_3, k_soil_3)
    ops.uniaxialMaterial("ENT", MAT_SOIL_4, k_soil_4)
    ops.uniaxialMaterial("ENT", MAT_SOIL_5, k_soil_5)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────────
def define_sections() -> None:
    ops.section("Elastic", SEC_DWALL, Ec, A_dwall, I_dwall)
    ops.section("Elastic", SEC_SLAB,  Ec, A_slab,  I_slab)

    ops.beamIntegration("Lobatto", INT_DWALL, SEC_DWALL, 5)
    ops.beamIntegration("Lobatto", INT_SLAB,  SEC_SLAB,  5)

    ops.geomTransf("PDelta",  TRANSF_DWALL)
    ops.geomTransf("Linear",  TRANSF_SLAB)

# ── 7. NODES ─────────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    # ── Left wall (x = 0), nodes numbered from top (y = 0) to base (y = -32 000)
    nid = 1
    for i in range(n_node_wall):
        ops.node(nid, 0.0, -i * elem_size)
        nid += 1

    # ── Right wall (x = l_center), same y-levels
    for i in range(n_node_wall):
        ops.node(nid, l_center, -i * elem_size)
        nid += 1

    # ── Slab nodes between the walls at y = -depth_slab (x = 1 000 … 8 000 mm)
    for i in range(1, n_ele_slab):
        ops.node(nid, i * elem_size, -depth_slab)
        nid += 1

    # ── Top Slab nodes between the walls at y = -depth_top_slab (x = 1 000 … 8 000 mm)
    for i in range(1, n_ele_slab):
        ops.node(nid, i * elem_size, -depth_top_slab)
        nid += 1

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    # ── Wall base fixity
    ops.fix(NODE_LWALL_BASE, 1, 1, 1)
    ops.fix(NODE_RWALL_BASE, 1, 1, 1)

    # ── Winkler compression-only springs along both walls
    for i in range(n_node_wall):
        y = -i * elem_size

        # Left wall — soil is on the left (-x) side
        wall_node_l = NODE_LWALL_TOP + i
        soil_node_l = NODE_SOIL_L_START + i
        ele_l       = ELE_SPRING_L_START + i
        mat_l       = _soil_mat_for_node(i)

        ops.node(soil_node_l, 0.0, y)
        ops.fix(soil_node_l, 1, 1, 1)
        ops.element(
            "zeroLength", ele_l, wall_node_l, soil_node_l,
            "-mat", mat_l, "-dir", 1,
            "-orient", -1, 0, 0, 0, 1, 0
        )
        
        # Right wall - soils is on the right (+x) side
        wall_node_r = NODE_RWALL_TOP + i
        soil_node_r = NODE_SOIL_R_START + i
        ele_r       = ELE_SPRING_R_START + i
        mat_r       = _soil_mat_for_node(i)

        ops.node(soil_node_r, l_center, y)
        ops.fix(soil_node_r, 1, 1, 1)
        ops.element(
            "zeroLength", ele_r, wall_node_r, soil_node_r,
            "-mat", mat_r, "-dir", 1,
            "-orient", 1, 0, 0, 0, 1, 0
        )
    
    # ── Base slab Winkler springs
    n_interior_slab = n_ele_slab - 1
    slab_nodes = [NODE_LWALL_SLAB] + list(range(NODE_SLAB_START, NODE_SLAB_START + n_interior_slab)) + [NODE_RWALL_SLAB]
    ops.uniaxialMaterial("ENT", MAT_SOIL_SLAB, k_v_slab)
    
    for i, s_node in enumerate(slab_nodes):
        x_coord = ops.nodeCoord(s_node, 1)
        soil_node_s = NODE_SOIL_S_START + i  # Fixed: using defined constant
        ele_s = ELE_SPRING_S_START + i

        ops.node(soil_node_s, x_coord, -depth_slab)
        ops.fix(soil_node_s, 1, 1, 1)

        ops.element(
            "zeroLength", ele_s, s_node, soil_node_s,
            "-mat", MAT_SOIL_SLAB, "-dir", 1,
            "-orient", 0, -1, 0, 1, 0, 0
        )

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────────
def define_elements() -> None:
    # ── Left wall
    for i in range(n_ele_wall):
        n1 = NODE_LWALL_TOP + i
        n2 = n1 + 1
        ops.element("dispBeamColumn", i + 1, n1, n2, TRANSF_DWALL, INT_DWALL)

    # ── Right wall
    for i in range(n_ele_wall):
        n1 = NODE_RWALL_TOP + i
        n2 = n1 + 1
        ops.element("dispBeamColumn", n_ele_wall + i + 1, n1, n2, TRANSF_DWALL, INT_DWALL)

    # ── Base slab  (left wall  →  right wall at y = -10 000 mm, 9 elements)
    slab_nodes = (
        [NODE_LWALL_SLAB]
        + list(range(NODE_SLAB_START, NODE_SLAB_END + 1))
        + [NODE_RWALL_SLAB]
    )
    for i in range(n_ele_slab):
        n1 = slab_nodes[i]
        n2 = slab_nodes[i + 1]
        ops.element("dispBeamColumn", 2 * n_ele_wall + i + 1, n1, n2, TRANSF_SLAB, INT_SLAB)

    # ── Top slab (left wall → right wall at y = -2 000 mm, 9 elements)
    top_slab_nodes = (
        [NODE_LWALL_TOP_SLAB]
        + list(range(NODE_TOP_SLAB_START, NODE_TOP_SLAB_END + 1))
        + [NODE_RWALL_TOP_SLAB]
    )
    for i in range(n_ele_slab):
        n1 = top_slab_nodes[i]
        n2 = top_slab_nodes[i + 1]
        ops.element("dispBeamColumn", 2 * n_ele_wall + n_ele_slab + i + 1, n1, n2, TRANSF_SLAB, INT_SLAB)


# ── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from pathlib import Path

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    define_elements()

    vis_nodes(output_dir)
    vis_model(output_dir)
    print(f"Model built. Open output/vis_01_nodes.html to view nodes.")
