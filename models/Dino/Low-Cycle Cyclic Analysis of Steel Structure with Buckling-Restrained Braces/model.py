# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Low-Cycle Cyclic Analysis of Steel Structure with Buckling-Restrained Braces
UniqueID : Low-Cycle Cyclic Analysis of Steel Structure with Buckling-Restrained Braces
Author   : Antigravity OpenSeesPy Agent
Date     : 2026-07-15
Purpose  : Low-cycle cyclic lateral displacement analysis of a steel frame structure with buckling-restrained braces.
Ref      : Original Dino model co.tcl
Units    : N, mm, MPa (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

# Add standards/ to path if running standalone
_STANDARDS = Path(__file__).parents[3] / "standards"
if not _STANDARDS.exists():
    _STANDARDS = Path(__file__).parents[2] / "standards"  # fallback
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
# Materials
MAT_ELASTIC_1 = 1
MAT_ELASTIC_2 = 2
MAT_STEEL_3 = 3

MAT_ELASTIC_201 = 201
MAT_ELASTIC_301 = 301
MAT_ELASTIC_401 = 401
MAT_ELASTIC_202 = 202
MAT_ELASTIC_302 = 302
MAT_ELASTIC_402 = 402
MAT_ELASTIC_203 = 203
MAT_ELASTIC_303 = 303
MAT_ELASTIC_403 = 403

# Sections
SEC_FIBER_1 = 1
SEC_FIBER_2 = 2
SEC_FIBER_3 = 3
SEC_AGG_1001 = 1001
SEC_AGG_1002 = 1002
SEC_AGG_1003 = 1003

# Integration tags (for dispBeamColumn)
INTEG_1001 = 1001
INTEG_1002 = 1002
INTEG_1003 = 1003

# Key Nodes
NODE_CTRL = 25
NODES_BASE = [1, 7, 12, 17, 21, 27, 32, 37]

# Key Elements
ELE_RECORD = 85

# Time Series & Patterns
TS_GRAVITY = 1
PAT_GRAVITY = 1
TS_CYCLIC = 3
PAT_CYCLIC = 3

# ODB Tag
ODB_TAG = 1

# Source Reference Files
TCL_FILE = Path(__file__).parent / "tcl_ref" / "co.tcl"
REF_FILE = Path(__file__).parent / "tcl_ref" / "node25.out"

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Steel Material 3 Properties
fy_steel = 295.0 * MPa
E_steel = 206000.0 * MPa
b_steel = 0.05

# Elastic Materials Properties
E_elastic_1 = 1.999E+005 * MPa
E_elastic_2 = 2.482E+004 * MPa

# Aggregator Stiffnesses
# Section 1001
k_shear_y_1001 = 4.614E+008 * N
k_shear_z_1001 = 1.794E+009 * N
k_torsion_1001 = 9.058E+011 * N * mm

# Section 1002
k_shear_y_1002 = 1.122E+009 * N
k_shear_z_1002 = 2.243E+009 * N
k_torsion_1002 = 1.649E+012 * N * mm

# Section 1003
k_shear_y_1003 = 5.127E+008 * N
k_shear_z_1003 = 1.025E+009 * N
k_torsion_1003 = 2.461E+011 * N * mm

# Gravity Loads
w_gravity = -4.0 * N / mm  # distributed beam load

# Lateral Cyclic Reference Loads
p_ref_top = 4.000E+005 * N       # Nodes 5, 25
p_ref_floor3 = 3.000E+005 * N    # Nodes 4, 24
p_ref_floor2 = 2.000E+005 * N    # Nodes 3, 23
p_ref_floor1 = 1.000E+005 * N    # Nodes 2, 22

# Analysis Steps
N_GRAV_STEPS = 10
GRAV_LAMBDA = 0.1

# Cyclic Protocol Segments: (n_steps, displacement_increment_per_step)
# 1) Push to +200mm (50 steps of 4mm)
# 2) Pull to -200mm (50 steps of -8mm)
# 3) Push to +400mm (50 steps of 12mm)
# 4) Pull to -400mm (50 steps of -16mm)
CYCLIC_SEGMENTS = [
    (50, 4.0 * mm),
    (50, -8.0 * mm),
    (50, 12.0 * mm),
    (50, -16.0 * mm),
]
N_TOTAL_CYCLIC_STEPS = 200
N_TOTAL_RECORDED_STEPS = N_GRAV_STEPS + N_TOTAL_CYCLIC_STEPS  # 210 steps total

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Initialize a 3D model with 6 DOFs per node."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Define steel and elastic properties."""
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_1, E_elastic_1)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_2, E_elastic_2)
    ops.uniaxialMaterial("Steel01", MAT_STEEL_3, fy_steel, E_steel, b_steel)
    
    # Aggregator 1001 Materials
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_201, k_shear_y_1001)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_301, k_shear_z_1001)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_401, k_torsion_1001)
    
    # Aggregator 1002 Materials
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_202, k_shear_y_1002)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_302, k_shear_z_1002)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_402, k_torsion_1002)
    
    # Aggregator 1003 Materials
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_203, k_shear_y_1003)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_303, k_shear_z_1003)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_403, k_torsion_1003)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    """Define fiber cross-sections and section aggregators."""
    def compute_gj(fibers, G):
        sum_area_r2 = sum(area * (y**2 + z**2) for y, z, area, mat in fibers)
        return G * sum_area_r2

    G_elastic = E_elastic_1 / 2.6
    G_steel = E_steel / 2.6

    # 1. Section 1 (DH300X300X35X12)
    fibers_1 = [
        (-120.0 * mm, -132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (-60.0 * mm,  -132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (0.0 * mm,    -132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (60.0 * mm,   -132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (120.0 * mm,  -132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (-120.0 * mm,  132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (-60.0 * mm,   132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (0.0 * mm,     132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (60.0 * mm,    132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (120.0 * mm,   132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (0.0 * mm,    -92.0 * mm,  552.0 * mm**2,  MAT_ELASTIC_1),
        (0.0 * mm,    -46.0 * mm,  552.0 * mm**2,  MAT_ELASTIC_1),
        (0.0 * mm,      0.0 * mm,  552.0 * mm**2,  MAT_ELASTIC_1),
        (0.0 * mm,     46.0 * mm,  552.0 * mm**2,  MAT_ELASTIC_1),
        (0.0 * mm,     92.0 * mm,  552.0 * mm**2,  MAT_ELASTIC_1),
    ]
    gj_1 = compute_gj(fibers_1, G_elastic)
    ops.section("Fiber", SEC_FIBER_1, "-GJ", gj_1)
    for y, z, area, mat in fibers_1:
        ops.fiber(y, z, area, mat)

    # 2. Section 2 (DH300X300X35X35)
    fibers_2 = [
        (-120.0 * mm, -132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (-60.0 * mm,  -132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (0.0 * mm,    -132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (60.0 * mm,   -132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (120.0 * mm,  -132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (-120.0 * mm,  132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (-60.0 * mm,   132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (0.0 * mm,     132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (60.0 * mm,    132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (120.0 * mm,   132.5 * mm, 2100.0 * mm**2, MAT_ELASTIC_1),
        (0.0 * mm,    -92.0 * mm,  1610.0 * mm**2, MAT_ELASTIC_1),
        (0.0 * mm,    -46.0 * mm,  1610.0 * mm**2, MAT_ELASTIC_1),
        (0.0 * mm,      0.0 * mm,  1610.0 * mm**2, MAT_ELASTIC_1),
        (0.0 * mm,     46.0 * mm,  1610.0 * mm**2, MAT_ELASTIC_1),
        (0.0 * mm,     92.0 * mm,  1610.0 * mm**2, MAT_ELASTIC_1),
    ]
    gj_2 = compute_gj(fibers_2, G_elastic)
    ops.section("Fiber", SEC_FIBER_2, "-GJ", gj_2)
    for y, z, area, mat in fibers_2:
        ops.fiber(y, z, area, mat)

    # 3. Section 3 (DB400X400X20)
    fibers_3 = [
        (-160.0 * mm, -190.0 * mm, 1600.0 * mm**2, MAT_STEEL_3),
        (-80.0 * mm,  -190.0 * mm, 1600.0 * mm**2, MAT_STEEL_3),
        (0.0 * mm,    -190.0 * mm, 1600.0 * mm**2, MAT_STEEL_3),
        (80.0 * mm,   -190.0 * mm, 1600.0 * mm**2, MAT_STEEL_3),
        (160.0 * mm,  -190.0 * mm, 1600.0 * mm**2, MAT_STEEL_3),
        (-160.0 * mm,  190.0 * mm, 1600.0 * mm**2, MAT_STEEL_3),
        (-80.0 * mm,   190.0 * mm, 1600.0 * mm**2, MAT_STEEL_3),
        (0.0 * mm,     190.0 * mm, 1600.0 * mm**2, MAT_STEEL_3),
        (80.0 * mm,    190.0 * mm, 1600.0 * mm**2, MAT_STEEL_3),
        (160.0 * mm,   190.0 * mm, 1600.0 * mm**2, MAT_STEEL_3),
        (0.0 * mm,    -144.0 * mm, 1440.0 * mm**2, MAT_STEEL_3),
        (0.0 * mm,    -72.0 * mm,  1440.0 * mm**2, MAT_STEEL_3),
        (0.0 * mm,      0.0 * mm,  1440.0 * mm**2, MAT_STEEL_3),
        (0.0 * mm,     72.0 * mm,  1440.0 * mm**2, MAT_STEEL_3),
        (0.0 * mm,     144.0 * mm,  1440.0 * mm**2, MAT_STEEL_3),
    ]
    gj_3 = compute_gj(fibers_3, G_steel)
    ops.section("Fiber", SEC_FIBER_3, "-GJ", gj_3)
    for y, z, area, mat in fibers_3:
        ops.fiber(y, z, area, mat)

    # 4. Section Aggregators (Vy, Vz, T)
    ops.section("Aggregator", SEC_AGG_1001, MAT_ELASTIC_201, "Vy", MAT_ELASTIC_301, "Vz", MAT_ELASTIC_401, "T", "-section", SEC_FIBER_1)
    ops.section("Aggregator", SEC_AGG_1002, MAT_ELASTIC_202, "Vy", MAT_ELASTIC_302, "Vz", MAT_ELASTIC_402, "T", "-section", SEC_FIBER_2)
    ops.section("Aggregator", SEC_AGG_1003, MAT_ELASTIC_203, "Vy", MAT_ELASTIC_303, "Vz", MAT_ELASTIC_403, "T", "-section", SEC_FIBER_3)

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Define all model nodes, coordinates, and mass distributions."""
    nodes_coords = [
        (1, 0.0, 0.0, 0.0), (2, 0.0, 0.0, 3000.0), (3, 0.0, 0.0, 6000.0),
        (4, 0.0, 0.0, 9000.0), (5, 0.0, 0.0, 12000.0), (6, 6000.0, 0.0, 12000.0),
        (7, 6000.0, 0.0, 0.0), (8, 6000.0, 0.0, 3000.0), (9, 6000.0, 0.0, 6000.0),
        (10, 6000.0, 0.0, 9000.0), (11, 12000.0, 0.0, 12000.0), (12, 12000.0, 0.0, 0.0),
        (13, 12000.0, 0.0, 3000.0), (14, 12000.0, 0.0, 6000.0), (15, 12000.0, 0.0, 9000.0),
        (16, 18000.0, 0.0, 12000.0), (17, 18000.0, 0.0, 0.0), (18, 18000.0, 0.0, 3000.0),
        (19, 18000.0, 0.0, 6000.0), (20, 18000.0, 0.0, 9000.0), (21, 0.0, 6000.0, 0.0),
        (22, 0.0, 6000.0, 3000.0), (23, 0.0, 6000.0, 6000.0), (24, 0.0, 6000.0, 9000.0),
        (25, 0.0, 6000.0, 12000.0), (26, 6000.0, 6000.0, 12000.0), (27, 6000.0, 6000.0, 0.0),
        (28, 6000.0, 6000.0, 3000.0), (29, 6000.0, 6000.0, 6000.0), (30, 6000.0, 6000.0, 9000.0),
        (31, 12000.0, 6000.0, 12000.0), (32, 12000.0, 6000.0, 0.0), (33, 12000.0, 6000.0, 3000.0),
        (34, 12000.0, 6000.0, 6000.0), (35, 12000.0, 6000.0, 9000.0), (36, 18000.0, 6000.0, 12000.0),
        (37, 18000.0, 6000.0, 0.0), (38, 18000.0, 6000.0, 3000.0), (39, 18000.0, 6000.0, 6000.0),
        (40, 18000.0, 6000.0, 9000.0),
        # Brace nodes at y=6000
        (41, 7000.0, 6000.0, 9500.0), (42, 8000.0, 6000.0, 10000.0),
        (43, 9000.0, 6000.0, 10500.0), (44, 10000.0, 6000.0, 11000.0),
        (45, 11000.0, 6000.0, 11500.0), (46, 7000.0, 6000.0, 6500.0),
        (47, 8000.0, 6000.0, 7000.0), (48, 9000.0, 6000.0, 7500.0),
        (49, 10000.0, 6000.0, 8000.0), (50, 11000.0, 6000.0, 8500.0),
        (51, 7000.0, 6000.0, 3500.0), (52, 8000.0, 6000.0, 4000.0),
        (53, 9000.0, 6000.0, 4500.0), (54, 10000.0, 6000.0, 5000.0),
        (55, 11000.0, 6000.0, 5500.0), (56, 7000.0, 6000.0, 500.0),
        (57, 8000.0, 6000.0, 1000.0), (58, 9000.0, 6000.0, 1500.0),
        (59, 10000.0, 6000.0, 2000.0), (60, 11000.0, 6000.0, 2500.0),
        # Brace nodes at y=0
        (61, 7000.0, 0.0, 9500.0), (62, 8000.0, 0.0, 10000.0),
        (63, 9000.0, 0.0, 10500.0), (64, 10000.0, 0.0, 11000.0),
        (65, 11000.0, 0.0, 11500.0), (66, 7000.0, 0.0, 6500.0),
        (67, 8000.0, 0.0, 7000.0), (68, 9000.0, 0.0, 7500.0),
        (69, 10000.0, 0.0, 8000.0), (70, 11000.0, 0.0, 8500.0),
        (71, 7000.0, 0.0, 3500.0), (72, 8000.0, 0.0, 4000.0),
        (73, 9000.0, 0.0, 4500.0), (74, 10000.0, 0.0, 5000.0),
        (75, 11000.0, 0.0, 5500.0), (76, 7000.0, 0.0, 500.0),
        (77, 8000.0, 0.0, 1000.0), (78, 9000.0, 0.0, 1500.0),
        (79, 10000.0, 0.0, 2000.0), (80, 11000.0, 0.0, 2500.0),
    ]

    for tag, x, y, z in nodes_coords:
        ops.node(tag, x * mm, y * mm, z * mm)

    # Nodal mass definition (consistent N*s^2/mm, no multiplier)
    nodes_masses = {
        1: 0.5876, 2: 2.654, 3: 2.654, 4: 2.654, 5: 2.067,
        6: 2.806, 7: 0.6891, 8: 3.495, 9: 3.495, 10: 3.495,
        11: 2.908, 12: 0.5876, 13: 3.495, 14: 3.495, 15: 3.495,
        16: 2.067, 17: 0.5876, 18: 2.654, 19: 2.654, 20: 2.654,
        21: 0.5876, 22: 2.654, 23: 2.654, 24: 2.654, 25: 2.067,
        26: 2.806, 27: 0.6891, 28: 3.495, 29: 3.495, 30: 3.495,
        31: 2.908, 32: 0.5876, 33: 3.495, 34: 3.495, 35: 3.495,
        36: 2.067, 37: 0.5876, 38: 2.654, 39: 2.654, 40: 2.654
    }
    # Brace nodes 41 to 80
    for tag in range(41, 81):
        nodes_masses[tag] = 0.2030

    for tag, m_val in nodes_masses.items():
        ops.mass(tag, m_val, m_val, 0.0, 0.0, 0.0, 0.0)

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Define boundary constraints (supports)."""
    for tag in NODES_BASE:
        ops.fix(tag, 1, 1, 1, 1, 1, 1)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Define coordinate transformations, integration schemes, and elements."""
    # Coordinate Transformations
    geom_transfs = [
        (1, 'Linear', [1.0, 0.0, 0.0]), (2, 'Linear', [1.0, 0.0, 0.0]),
        (3, 'Linear', [1.0, 0.0, 0.0]), (4, 'Linear', [1.0, 0.0, 0.0]),
        (5, 'Linear', [1.0, 0.0, 0.0]), (6, 'Linear', [1.0, 0.0, 0.0]),
        (7, 'Linear', [0.0, 0.0, 1.0]), (8, 'Linear', [0.0, 0.0, 1.0]),
        (9, 'Linear', [0.0, 0.0, 1.0]), (10, 'Linear', [0.0, 0.0, 1.0]),
        (11, 'Linear', [0.0, 0.0, 1.0]), (12, 'Linear', [0.0, 0.0, 1.0]),
        (13, 'Linear', [0.0, 0.0, 1.0]), (14, 'Linear', [-0.447, 0.0, 0.894]),
        (15, 'Linear', [-0.447, 0.0, 0.894]), (16, 'Linear', [-0.447, 0.0, 0.894]),
        (17, 'Linear', [-0.447, 0.0, 0.894]), (18, 'Linear', [-0.447, 0.0, 0.894]),
        (19, 'Linear', [-0.447, 0.0, 0.894]), (20, 'Linear', [1.0, 0.0, 0.0]),
        (21, 'Linear', [1.0, 0.0, 0.0]), (22, 'Linear', [0.0, 0.0, 1.0]),
        (23, 'Linear', [0.0, 0.0, 1.0]), (24, 'Linear', [0.0, 0.0, 1.0]),
        (25, 'Linear', [-0.447, 0.0, 0.894]), (26, 'Linear', [-0.447, 0.0, 0.894]),
        (27, 'Linear', [-0.447, 0.0, 0.894]), (28, 'Linear', [-0.447, 0.0, 0.894]),
        (29, 'Linear', [-0.447, 0.0, 0.894]), (30, 'Linear', [-0.447, 0.0, 0.894]),
        (31, 'Linear', [1.0, 0.0, 0.0]), (32, 'Linear', [1.0, 0.0, 0.0]),
        (33, 'Linear', [1.0, 0.0, 0.0]), (34, 'Linear', [1.0, 0.0, 0.0]),
        (35, 'Linear', [1.0, 0.0, 0.0]), (36, 'Linear', [1.0, 0.0, 0.0]),
        (37, 'Linear', [0.0, 0.0, 1.0]), (38, 'Linear', [0.0, 0.0, 1.0]),
        (39, 'Linear', [0.0, 0.0, 1.0]), (40, 'Linear', [0.0, 0.0, 1.0]),
        (41, 'Linear', [0.0, 0.0, 1.0]), (42, 'Linear', [0.0, 0.0, 1.0]),
        (43, 'Linear', [0.0, 0.0, 1.0]), (44, 'Linear', [-0.447, 0.0, 0.894]),
        (45, 'Linear', [-0.447, 0.0, 0.894]), (46, 'Linear', [-0.447, 0.0, 0.894]),
        (47, 'Linear', [-0.447, 0.0, 0.894]), (48, 'Linear', [-0.447, 0.0, 0.894]),
        (49, 'Linear', [-0.447, 0.0, 0.894]), (50, 'Linear', [1.0, 0.0, 0.0]),
        (51, 'Linear', [1.0, 0.0, 0.0]), (52, 'Linear', [0.0, 0.0, 1.0]),
        (53, 'Linear', [0.0, 0.0, 1.0]), (54, 'Linear', [0.0, 0.0, 1.0]),
        (55, 'Linear', [-0.447, 0.0, 0.894]), (56, 'Linear', [-0.447, 0.0, 0.894]),
        (57, 'Linear', [-0.447, 0.0, 0.894]), (58, 'Linear', [-0.447, 0.0, 0.894]),
        (59, 'Linear', [-0.447, 0.0, 0.894]), (60, 'Linear', [-0.447, 0.0, 0.894]),
        (61, 'Linear', [1.0, 0.0, 0.0]), (62, 'Linear', [1.0, 0.0, 0.0]),
        (63, 'Linear', [1.0, 0.0, 0.0]), (64, 'Linear', [1.0, 0.0, 0.0]),
        (65, 'Linear', [1.0, 0.0, 0.0]), (66, 'Linear', [1.0, 0.0, 0.0]),
        (67, 'Linear', [0.0, 0.0, 1.0]), (68, 'Linear', [0.0, 0.0, 1.0]),
        (69, 'Linear', [0.0, 0.0, 1.0]), (70, 'Linear', [0.0, 0.0, 1.0]),
        (71, 'Linear', [0.0, 0.0, 1.0]), (72, 'Linear', [0.0, 0.0, 1.0]),
        (73, 'Linear', [0.0, 0.0, 1.0]), (74, 'Linear', [-0.447, 0.0, 0.894]),
        (75, 'Linear', [-0.447, 0.0, 0.894]), (76, 'Linear', [-0.447, 0.0, 0.894]),
        (77, 'Linear', [-0.447, 0.0, 0.894]), (78, 'Linear', [-0.447, 0.0, 0.894]),
        (79, 'Linear', [-0.447, 0.0, 0.894]), (80, 'Linear', [1.0, 0.0, 0.0]),
        (81, 'Linear', [1.0, 0.0, 0.0]), (82, 'Linear', [0.0, 0.0, 1.0]),
        (83, 'Linear', [0.0, 0.0, 1.0]), (84, 'Linear', [0.0, 0.0, 1.0]),
        (85, 'Linear', [-0.447, 0.0, 0.894]), (86, 'Linear', [-0.447, 0.0, 0.894]),
        (87, 'Linear', [-0.447, 0.0, 0.894]), (88, 'Linear', [-0.447, 0.0, 0.894]),
        (89, 'Linear', [-0.447, 0.0, 0.894]), (90, 'Linear', [-0.447, 0.0, 0.894]),
        (91, 'Linear', [1.0, 0.0, 0.0]), (92, 'Linear', [1.0, 0.0, 0.0]),
        (93, 'Linear', [1.0, 0.0, 0.0]), (94, 'Linear', [1.0, 0.0, 0.0]),
        (95, 'Linear', [1.0, 0.0, 0.0]), (96, 'Linear', [1.0, 0.0, 0.0]),
        (97, 'Linear', [1.0, 0.0, 0.0]), (98, 'Linear', [1.0, 0.0, 0.0]),
        (99, 'Linear', [0.0, 0.0, 1.0]), (100, 'Linear', [0.0, 0.0, 1.0]),
        (101, 'Linear', [0.0, 0.0, 1.0]), (102, 'Linear', [0.0, 0.0, 1.0]),
        (103, 'Linear', [0.0, 0.0, 1.0]), (104, 'Linear', [0.0, 0.0, 1.0]),
        (105, 'Linear', [0.0, 0.0, 1.0]), (106, 'Linear', [-0.447, 0.0, 0.894]),
        (107, 'Linear', [-0.447, 0.0, 0.894]), (108, 'Linear', [-0.447, 0.0, 0.894]),
        (109, 'Linear', [-0.447, 0.0, 0.894]), (110, 'Linear', [-0.447, 0.0, 0.894]),
        (111, 'Linear', [-0.447, 0.0, 0.894]), (112, 'Linear', [0.0, 0.0, 1.0]),
        (113, 'Linear', [0.0, 0.0, 1.0]), (114, 'Linear', [0.0, 0.0, 1.0]),
        (115, 'Linear', [-0.447, 0.0, 0.894]), (116, 'Linear', [-0.447, 0.0, 0.894]),
        (117, 'Linear', [-0.447, 0.0, 0.894]), (118, 'Linear', [-0.447, 0.0, 0.894]),
        (119, 'Linear', [-0.447, 0.0, 0.894]), (120, 'Linear', [-0.447, 0.0, 0.894]),
    ]
    for tag, ttype, vec in geom_transfs:
        ops.geomTransf(ttype, tag, *vec)

    # beamIntegration (Lobatto 3 IP for the aggregated sections)
    ops.beamIntegration("Lobatto", INTEG_1001, SEC_AGG_1001, 3)
    ops.beamIntegration("Lobatto", INTEG_1002, SEC_AGG_1002, 3)
    ops.beamIntegration("Lobatto", INTEG_1003, SEC_AGG_1003, 3)

    # Define Elements
    elements_data = [
        (1, [4, 5], 1002, 1), (2, [10, 6], 1002, 2), (3, [15, 11], 1002, 3),
        (4, [20, 16], 1002, 4), (5, [24, 25], 1002, 5), (6, [40, 36], 1002, 6),
        (7, [5, 25], 1001, 7), (8, [6, 26], 1001, 8), (9, [11, 31], 1001, 9),
        (10, [16, 36], 1001, 10), (11, [25, 26], 1001, 11), (12, [26, 31], 1001, 12),
        (13, [31, 36], 1001, 13), (14, [30, 41], 1003, 14), (15, [41, 42], 1003, 15),
        (16, [42, 43], 1003, 16), (17, [43, 44], 1003, 17), (18, [44, 45], 1003, 18),
        (19, [45, 31], 1003, 19), (20, [35, 31], 1002, 20), (21, [30, 26], 1002, 21),
        (22, [5, 6], 1001, 22), (23, [6, 11], 1001, 23), (24, [11, 16], 1001, 24),
        (25, [10, 61], 1003, 25), (26, [61, 62], 1003, 26), (27, [62, 63], 1003, 27),
        (28, [63, 64], 1003, 28), (29, [64, 65], 1003, 29), (30, [65, 11], 1003, 30),
        (31, [3, 4], 1002, 31), (32, [9, 10], 1002, 32), (33, [14, 15], 1002, 33),
        (34, [19, 20], 1002, 34), (35, [23, 24], 1002, 35), (36, [39, 40], 1002, 36),
        (37, [4, 24], 1001, 37), (38, [10, 30], 1001, 38), (39, [15, 35], 1001, 39),
        (40, [20, 40], 1001, 40), (41, [24, 30], 1001, 41), (42, [30, 35], 1001, 42),
        (43, [35, 40], 1001, 43), (44, [29, 46], 1003, 44), (45, [46, 47], 1003, 45),
        (46, [47, 48], 1003, 46), (47, [48, 49], 1003, 47), (48, [49, 50], 1003, 48),
        (49, [50, 35], 1003, 49), (50, [34, 35], 1002, 50), (51, [29, 30], 1002, 51),
        (52, [4, 10], 1001, 52), (53, [10, 15], 1001, 53), (54, [15, 20], 1001, 54),
        (55, [9, 66], 1003, 55), (56, [66, 67], 1003, 56), (57, [67, 68], 1003, 57),
        (58, [68, 69], 1003, 58), (59, [69, 70], 1003, 59), (60, [70, 15], 1003, 60),
        (61, [2, 3], 1002, 61), (62, [8, 9], 1002, 62), (63, [13, 14], 1002, 63),
        (64, [18, 19], 1002, 64), (65, [22, 23], 1002, 65), (66, [38, 39], 1002, 66),
        (67, [3, 23], 1001, 67), (68, [9, 29], 1001, 68), (69, [14, 34], 1001, 69),
        (70, [19, 39], 1001, 70), (71, [23, 29], 1001, 71), (72, [29, 34], 1001, 72),
        (73, [34, 39], 1001, 73), (74, [28, 51], 1003, 74), (75, [51, 52], 1003, 75),
        (76, [52, 53], 1003, 76), (77, [53, 54], 1003, 77), (78, [54, 55], 1003, 78),
        (79, [55, 34], 1003, 79), (80, [33, 34], 1002, 80), (81, [28, 29], 1002, 81),
        (82, [3, 9], 1001, 82), (83, [9, 14], 1001, 83), (84, [14, 19], 1001, 84),
        (85, [8, 71], 1003, 85), (86, [71, 72], 1003, 86), (87, [72, 73], 1003, 87),
        (88, [73, 74], 1003, 88), (89, [74, 75], 1003, 89), (90, [75, 14], 1003, 90),
        (91, [1, 2], 1002, 91), (92, [7, 8], 1002, 92), (93, [12, 13], 1002, 93),
        (94, [17, 18], 1002, 94), (95, [21, 22], 1002, 95), (96, [27, 28], 1002, 96),
        (97, [32, 33], 1002, 97), (98, [37, 38], 1002, 98), (99, [2, 22], 1001, 99),
        (100, [8, 28], 1001, 100), (101, [13, 33], 1001, 101), (102, [18, 38], 1001, 102),
        (103, [22, 28], 1001, 103), (104, [28, 33], 1001, 104), (105, [33, 38], 1001, 105),
        (106, [27, 56], 1003, 106), (107, [56, 57], 1003, 107), (108, [57, 58], 1003, 108),
        (109, [58, 59], 1003, 109), (110, [59, 60], 1003, 110), (111, [60, 33], 1003, 111),
        (112, [2, 8], 1001, 112), (113, [8, 13], 1001, 113), (114, [13, 18], 1001, 114),
        (115, [7, 76], 1003, 115), (116, [76, 77], 1003, 116), (117, [77, 78], 1003, 117),
        (118, [78, 79], 1003, 118), (119, [79, 80], 1003, 119), (120, [80, 13], 1003, 120),
    ]

    for tag, nodes_list, sec_tag, transf_tag in elements_data:
        i, j = nodes_list
        ops.element("dispBeamColumn", tag, i, j, transf_tag, sec_tag)

# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialize the ODB object to store response data."""
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
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
    """Define distributed gravity loads on the beams (before gravity analysis)."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    
    # 120 eleLoad lines from co.tcl, replayed verbatim
    ele_loads_data = [
        (7, '-beamUniform', [0.0, -4.0, 0.0]), (7, '-beamUniform', [0.0, -4.0, 0.0]),
        (7, '-beamUniform', [0.0, -4.0, 0.0]), (8, '-beamUniform', [0.0, -4.0, 0.0]),
        (8, '-beamUniform', [0.0, -4.0, 0.0]), (8, '-beamUniform', [0.0, -4.0, 0.0]),
        (9, '-beamUniform', [0.0, -4.0, 0.0]), (9, '-beamUniform', [0.0, -4.0, 0.0]),
        (9, '-beamUniform', [0.0, -4.0, 0.0]), (10, '-beamUniform', [0.0, -4.0, 0.0]),
        (10, '-beamUniform', [0.0, -4.0, 0.0]), (10, '-beamUniform', [0.0, -4.0, 0.0]),
        (37, '-beamUniform', [0.0, -4.0, 0.0]), (37, '-beamUniform', [0.0, -4.0, 0.0]),
        (37, '-beamUniform', [0.0, -4.0, 0.0]), (38, '-beamUniform', [0.0, -4.0, 0.0]),
        (38, '-beamUniform', [0.0, -4.0, 0.0]), (38, '-beamUniform', [0.0, -4.0, 0.0]),
        (39, '-beamUniform', [0.0, -4.0, 0.0]), (39, '-beamUniform', [0.0, -4.0, 0.0]),
        (39, '-beamUniform', [0.0, -4.0, 0.0]), (40, '-beamUniform', [0.0, -4.0, 0.0]),
        (40, '-beamUniform', [0.0, -4.0, 0.0]), (40, '-beamUniform', [0.0, -4.0, 0.0]),
        (67, '-beamUniform', [0.0, -4.0, 0.0]), (67, '-beamUniform', [0.0, -4.0, 0.0]),
        (67, '-beamUniform', [0.0, -4.0, 0.0]), (68, '-beamUniform', [0.0, -4.0, 0.0]),
        (68, '-beamUniform', [0.0, -4.0, 0.0]), (68, '-beamUniform', [0.0, -4.0, 0.0]),
        (69, '-beamUniform', [0.0, -4.0, 0.0]), (69, '-beamUniform', [0.0, -4.0, 0.0]),
        (69, '-beamUniform', [0.0, -4.0, 0.0]), (70, '-beamUniform', [0.0, -4.0, 0.0]),
        (70, '-beamUniform', [0.0, -4.0, 0.0]), (70, '-beamUniform', [0.0, -4.0, 0.0]),
        (99, '-beamUniform', [0.0, -4.0, 0.0]), (99, '-beamUniform', [0.0, -4.0, 0.0]),
        (99, '-beamUniform', [0.0, -4.0, 0.0]), (100, '-beamUniform', [0.0, -4.0, 0.0]),
        (100, '-beamUniform', [0.0, -4.0, 0.0]), (100, '-beamUniform', [0.0, -4.0, 0.0]),
        (101, '-beamUniform', [0.0, -4.0, 0.0]), (101, '-beamUniform', [0.0, -4.0, 0.0]),
        (101, '-beamUniform', [0.0, -4.0, 0.0]), (102, '-beamUniform', [0.0, -4.0, 0.0]),
        (102, '-beamUniform', [0.0, -4.0, 0.0]), (102, '-beamUniform', [0.0, -4.0, 0.0]),
        (11, '-beamUniform', [0.0, -4.0, 0.0]), (11, '-beamUniform', [0.0, -4.0, 0.0]),
        (11, '-beamUniform', [0.0, -4.0, 0.0]), (12, '-beamUniform', [0.0, -4.0, 0.0]),
        (12, '-beamUniform', [0.0, -4.0, 0.0]), (12, '-beamUniform', [0.0, -4.0, 0.0]),
        (13, '-beamUniform', [0.0, -4.0, 0.0]), (13, '-beamUniform', [0.0, -4.0, 0.0]),
        (13, '-beamUniform', [0.0, -4.0, 0.0]), (103, '-beamUniform', [0.0, -4.0, 0.0]),
        (103, '-beamUniform', [0.0, -4.0, 0.0]), (103, '-beamUniform', [0.0, -4.0, 0.0]),
        (104, '-beamUniform', [0.0, -4.0, 0.0]), (104, '-beamUniform', [0.0, -4.0, 0.0]),
        (104, '-beamUniform', [0.0, -4.0, 0.0]), (105, '-beamUniform', [0.0, -4.0, 0.0]),
        (105, '-beamUniform', [0.0, -4.0, 0.0]), (105, '-beamUniform', [0.0, -4.0, 0.0]),
        (71, '-beamUniform', [0.0, -4.0, 0.0]), (71, '-beamUniform', [0.0, -4.0, 0.0]),
        (71, '-beamUniform', [0.0, -4.0, 0.0]), (72, '-beamUniform', [0.0, -4.0, 0.0]),
        (72, '-beamUniform', [0.0, -4.0, 0.0]), (72, '-beamUniform', [0.0, -4.0, 0.0]),
        (73, '-beamUniform', [0.0, -4.0, 0.0]), (73, '-beamUniform', [0.0, -4.0, 0.0]),
        (73, '-beamUniform', [0.0, -4.0, 0.0]), (41, '-beamUniform', [0.0, -4.0, 0.0]),
        (41, '-beamUniform', [0.0, -4.0, 0.0]), (41, '-beamUniform', [0.0, -4.0, 0.0]),
        (42, '-beamUniform', [0.0, -4.0, 0.0]), (42, '-beamUniform', [0.0, -4.0, 0.0]),
        (42, '-beamUniform', [0.0, -4.0, 0.0]), (43, '-beamUniform', [0.0, -4.0, 0.0]),
        (43, '-beamUniform', [0.0, -4.0, 0.0]), (43, '-beamUniform', [0.0, -4.0, 0.0]),
        (22, '-beamUniform', [0.0, -4.0, 0.0]), (22, '-beamUniform', [0.0, -4.0, 0.0]),
        (22, '-beamUniform', [0.0, -4.0, 0.0]), (23, '-beamUniform', [0.0, -4.0, 0.0]),
        (23, '-beamUniform', [0.0, -4.0, 0.0]), (23, '-beamUniform', [0.0, -4.0, 0.0]),
        (24, '-beamUniform', [0.0, -4.0, 0.0]), (24, '-beamUniform', [0.0, -4.0, 0.0]),
        (24, '-beamUniform', [0.0, -4.0, 0.0]), (112, '-beamUniform', [0.0, -4.0, 0.0]),
        (112, '-beamUniform', [0.0, -4.0, 0.0]), (112, '-beamUniform', [0.0, -4.0, 0.0]),
        (113, '-beamUniform', [0.0, -4.0, 0.0]), (113, '-beamUniform', [0.0, -4.0, 0.0]),
        (113, '-beamUniform', [0.0, -4.0, 0.0]), (114, '-beamUniform', [0.0, -4.0, 0.0]),
        (114, '-beamUniform', [0.0, -4.0, 0.0]), (114, '-beamUniform', [0.0, -4.0, 0.0]),
        (82, '-beamUniform', [0.0, -4.0, 0.0]), (82, '-beamUniform', [0.0, -4.0, 0.0]),
        (82, '-beamUniform', [0.0, -4.0, 0.0]), (83, '-beamUniform', [0.0, -4.0, 0.0]),
        (83, '-beamUniform', [0.0, -4.0, 0.0]), (83, '-beamUniform', [0.0, -4.0, 0.0]),
        (84, '-beamUniform', [0.0, -4.0, 0.0]), (84, '-beamUniform', [0.0, -4.0, 0.0]),
        (84, '-beamUniform', [0.0, -4.0, 0.0]), (52, '-beamUniform', [0.0, -4.0, 0.0]),
        (52, '-beamUniform', [0.0, -4.0, 0.0]), (52, '-beamUniform', [0.0, -4.0, 0.0]),
        (53, '-beamUniform', [0.0, -4.0, 0.0]), (53, '-beamUniform', [0.0, -4.0, 0.0]),
        (53, '-beamUniform', [0.0, -4.0, 0.0]), (54, '-beamUniform', [0.0, -4.0, 0.0]),
        (54, '-beamUniform', [0.0, -4.0, 0.0]), (54, '-beamUniform', [0.0, -4.0, 0.0]),
    ]
    for ele_tag, ltype, lvals in ele_loads_data:
        ops.eleLoad("-ele", ele_tag, "-type", ltype, lvals[0], lvals[1], lvals[2])

def define_lateral_loads() -> None:
    """Define lateral cyclic loads (MUST be called AFTER loadConst — §12z-1)."""
    ops.timeSeries("Linear", TS_CYCLIC)
    ops.pattern("Plain", PAT_CYCLIC, TS_CYCLIC)
    
    # Nodal reference forces
    nodal_loads = [
        (5, [p_ref_top, 0.0, 0.0, 0.0, 0.0, 0.0]),
        (25, [p_ref_top, 0.0, 0.0, 0.0, 0.0, 0.0]),
        (4, [p_ref_floor3, 0.0, 0.0, 0.0, 0.0, 0.0]),
        (24, [p_ref_floor3, 0.0, 0.0, 0.0, 0.0, 0.0]),
        (3, [p_ref_floor2, 0.0, 0.0, 0.0, 0.0, 0.0]),
        (23, [p_ref_floor2, 0.0, 0.0, 0.0, 0.0, 0.0]),
        (2, [p_ref_floor1, 0.0, 0.0, 0.0, 0.0, 0.0]),
        (22, [p_ref_floor1, 0.0, 0.0, 0.0, 0.0, 0.0]),
    ]
    for tag, vals in nodal_loads:
        ops.load(tag, *vals)

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB") -> bool:
    """Run gravity load analysis using manual step loop (LoadControl exception, §3c)."""
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", GRAV_LAMBDA)
    ops.analysis("Static")
    
    ok = 0
    for step in range(N_GRAV_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"  WARNING: gravity step {step} failed (ok={ok})")
            break
        odb.fetch_response_step()
        
    print(f"  Gravity converged to lambda={ops.getTime():.4f} (target 1.0)")
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()
    return ok == 0

def run_pushover(odb: "opst.post.CreateODB") -> bool:
    """Run cyclic displacement-controlled pushover using SmartAnalyze static solver."""
    ops.constraints("Transformation")  # Better convergence for cyclic
    ops.numberer("RCM")
    ops.system("BandGeneral")
    
    # Configure SmartAnalyze with falling back algorithm chain
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="EnergyIncr",
        testTol=1.0e-6,
        testIterTimes=200,
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50, 60],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-4,
    )
    
    ok = 0
    for seg_idx, (n_steps, dU) in enumerate(CYCLIC_SEGMENTS):
        print(f"  Running cyclic segment {seg_idx + 1}: {n_steps} steps of {dU:.2f} mm...")
        for step in range(n_steps):
            ok = analysis.StaticAnalyze(node=NODE_CTRL, dof=1, seg=dU)
            if ok < 0:
                print(f"    WARNING: static analysis failed at segment {seg_idx+1}, step {step} (ok={ok})")
                break
            odb.fetch_response_step()
        if ok < 0:
            break
            
    analysis.close()
    return ok >= 0

def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Execute model generation, gravity analysis, and cyclic lateral pushover."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    
    # Visualization stage V1: Nodes
    vis_nodes(output_dir)
    
    define_elements()
    
    # Visualization stage V2: Full Model
    vis_model(output_dir)
    
    odb = create_odb(output_dir)
    
    # Phase 1: Gravity Analysis
    define_gravity_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running gravity phase...")
    run_gravity(odb)
    
    # Phase 2: Cyclic Pushover (Define lateral pattern AFTER gravity loadConst!)
    define_lateral_loads()
    print("Running cyclic pushover phase...")
    run_pushover(odb)
    
    # Load reference displacement data for verification
    ref_disp = None
    if REF_FILE.exists():
        ref = np.loadtxt(str(REF_FILE))
        ref_disp = ref[:, 1]  # UX column
        
    results = {"disp": None, "ref_disp": ref_disp}
    return odb, results

# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def _read_node25_history_from_odb() -> np.ndarray:
    """Read node 25's UX displacement at every recorded cyclic step from flushed ODB."""
    try:
        ds = opst.post.get_nodal_responses(
            odb_tag=ODB_TAG, resp_type="disp", print_info=False,
        )
        # N_GRAV_STEPS = 10, plus t=0 initial state -> gravity steps occupy indices 0 to 10
        # Cyclic steps occupy indices 11 onwards (total of 200 steps)
        disp = (ds.sel(nodeTags=NODE_CTRL)
                 .isel(DOFs=[0])  # UX only
                 .values.astype(float))
        # drop t=0 state + 10 gravity steps to extract cyclic phase only
        return disp[N_GRAV_STEPS + 1:].flatten()
    except Exception as e:
        print(f"Error reading ODB: {e}")
        return np.empty(0)

def post_process(odb: "opst.post.CreateODB", output_dir: Path, results: dict) -> None:
    """Flush ODB, render visualisations, compare results to reference, and plot."""
    odb.save_response()
    
    sim = _read_node25_history_from_odb()
    results["disp"] = sim
    ref = results["ref_disp"]
    
    # Save the simulated cyclic history to a CSV file for archiving
    if len(sim) > 0:
        step = np.arange(1, len(sim) + 1)
        curve = np.column_stack([step, sim])
        np.savetxt(str(output_dir / "node25_disp_history.csv"), curve,
                   delimiter=",", header="step,ux_mm")
                   
    # Plot comparison against reference node25.out
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(8, 5))
        if ref is not None and len(ref) > 0:
            ax.plot(np.arange(1, len(ref) + 1), ref, "k-", linewidth=1.0, alpha=0.6, label="Reference (node25.out)")
        if len(sim) > 0:
            ax.plot(np.arange(1, len(sim) + 1), sim, "r--", linewidth=1.2, alpha=0.85, label="Simulation")
            
        ax.set_xlabel("Recorded cyclic step")
        ax.set_ylabel("Node 25 UX displacement (mm)")
        ax.set_title("Low-Cycle Cyclic Analysis -- Node 25 UX Comparison")
        ax.axhline(0.0, color="0.6", linewidth=0.5)
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "cyclic_compare.png"), dpi=150)
        plt.close(fig)
        print("  Comparison plot saved to output/cyclic_compare.png")
    except ImportError:
        print("  Matplotlib unavailable — skipping plot creation.")
        
    # Render opstool html plots
    if not _headless():
        opst.post.set_odb_path(str(output_dir))
        
        # Deformed shape (scale up displacement to see cyclic deformation)
        vis_defo(output_dir, filename="vis_05_deformed.html", odb_tag=ODB_TAG, resp_dof="UX", scale=50.0)
        # Step slider
        vis_slider(output_dir, filename="vis_06_slider.html", odb_tag=ODB_TAG, resp_dof="UX", scale=50.0)
        # Animation
        vis_anim(output_dir, filename="vis_07_animation.html", defo_scale=50.0, resp_dof=("UX", "UY", "UZ"))
        print("  Visualisation HTMLs rendered in output/")

    # Print validation errors
    if len(sim) > 0 and ref is not None and len(ref) > 0:
        n = min(len(sim), len(ref))
        rms = float(np.sqrt(np.mean((sim[:n] - ref[:n])**2)))
        denom = np.maximum(np.abs(ref[:n]), 1e-12)
        rel_err = float(np.mean(np.abs(sim[:n] - ref[:n]) / denom) * 100.0)
        print(f"\nVerification against reference (node25.out):")
        print(f"  Recorded cyclic steps: {len(sim)} / {N_TOTAL_CYCLIC_STEPS}")
        print(f"  Final Node 25 UX: Sim = {sim[-1]:.4f} mm | Ref = {ref[-1]:.4f} mm")
        print(f"  Per-point RMS error: {rms:.5f} mm")
        print(f"  Mean relative error: {rel_err:.4f}%")

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Low-Cycle Cyclic Analysis of Steel Structure: Analysis complete.")
