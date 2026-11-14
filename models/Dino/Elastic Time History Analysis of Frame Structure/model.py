# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 3D RC Moment Frame Static Pushover Analysis (Dino OpenSees Tutorial Ex04)
UniqueID : Dino_FramePushover
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-11-14
Purpose  : Static elastoplastic pushover analysis of a 4-story, 2-bay x 1-bay 3D RC frame
           with fiber-section beam-column elements under gravity beam loads and an inverted
           triangular lateral pushover to 300 mm roof displacement.
Ref      : Dino OpenSees Tutorial - 实例4_框架结构推覆分析 (EXAM04.s2k / co.tcl)
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import sys
from pathlib import Path
import numpy as np
import openseespy.opensees as ops
import opstool as opst

# Dynamic standards/ path resolution (supports 3-level deep directory nesting)
for p in Path(__file__).resolve().parents:
    if (p / "standards").exists():
        sys.path.insert(0, str(p / "standards"))
        break

from units import *
from vis_utils import (
    _headless,
    vis_nodes,
    vis_model,
    vis_loads,
    vis_pre_analysis,
    vis_defo,
    vis_slider,
)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Materials
MAT_STEEL_REBAR    = 1    # Steel01 for longitudinal reinforcement (HRB335)
MAT_CONCRETE       = 2    # Concrete01 unconfined concrete (C30)
MAT_ELASTIC_T      = 3    # Generic elastic material

# Aggregator shear (Vy, Vz) and torsional (T) elastic materials
MAT_VY_SEC1        = 201
MAT_VZ_SEC1        = 301
MAT_T_SEC1         = 401

MAT_VY_SEC2        = 202
MAT_VZ_SEC2        = 302
MAT_T_SEC2         = 402

MAT_VY_SEC3        = 203
MAT_VZ_SEC3        = 303
MAT_T_SEC3         = 403

MAT_VY_SEC4        = 204
MAT_VZ_SEC4        = 304
MAT_T_SEC4         = 404

# Fiber sections (inner)
SEC_FIBER_COL_400X400   = 1    # NC400X400 column
SEC_FIBER_COL_400X600   = 2    # NC400X600 column
SEC_FIBER_BEAM_300X600  = 3    # NB300X600 beam
SEC_FIBER_BEAM_300X500  = 4    # NB300X500 beam

# Aggregator sections (composite: Fiber + Vy + Vz + T)
SEC_AGG_COL_400X400     = 1001
SEC_AGG_COL_400X600     = 1002
SEC_AGG_BEAM_300X600    = 1003
SEC_AGG_BEAM_300X500    = 1004

# Geometric transformations
TRANSF_COL_PDELTA       = 1    # Columns: PDelta, local x along global X [1, 0, 0]
TRANSF_BEAM_LINEAR      = 2    # Beams: Linear, local x along global Z [0, 0, 1]

# Load patterns & TimeSeries
TS_LINEAR               = 1
PAT_DEAD                = 1
PAT_PUSH                = 2

# Output Database
ODB_TAG                 = 1

# Node Tags (28 nodes total)
BASE_NODES = [23, 24, 25, 26, 27, 28]

# Control Node for Pushover
CTRL_NODE               = 8
CTRL_DOF                = 1    # Global X

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Steel01 Material Properties (HRB335 rebar)
fy_steel        = 335.0 * MPa
Es_steel        = 200000.0 * MPa
b_steel         = 1.0e-5

# Concrete01 Material Properties (C30 concrete, unconfined)
fpc_conc        = -26.8 * MPa
epsc0_conc      = -0.002
fpcu_conc       = -10.0 * MPa
epsu_conc       = -0.0033

# Aggregator Section Stiffnesses
# Section 1 (NC400X400)
ky_sec1         = 1.489e9 * N
kz_sec1         = 1.489e9 * N
gj_sec1         = 4.026e13 * N * mm**2

# Section 2 (NC400X600)
ky_sec2         = 2.233e9 * N
kz_sec2         = 2.233e9 * N
gj_sec2         = 8.389e13 * N * mm**2

# Section 3 (NB300X600)
ky_sec3         = 1.675e9 * N
kz_sec3         = 1.675e9 * N
gj_sec3         = 4.140e13 * N * mm**2

# Section 4 (NB300X500)
ky_sec4         = 1.396e9 * N
kz_sec4         = 1.396e9 * N
gj_sec4         = 3.146e13 * N * mm**2

# Integration points along nonlinear beam-columns
N_INT_PTS       = 4

# Analysis Parameters
N_GRAV_STEPS    = 10
GRAV_STEP_SIZE  = 1.0 / N_GRAV_STEPS

N_PUSH_STEPS    = 100
PUSH_STEP_SIZE  = 3.0 * mm
TARGET_DISP     = N_PUSH_STEPS * PUSH_STEP_SIZE    # 300.0 mm

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Initialise OpenSees model with 3 dimensions and 6 DOFs per node."""
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Define constitutive materials for steel rebar, concrete, and shear/torsion."""
    # 1. Longitudinal reinforcement (HRB335)
    ops.uniaxialMaterial("Steel01", MAT_STEEL_REBAR, fy_steel, Es_steel, b_steel)

    # 2. Unconfined concrete (C30)
    ops.uniaxialMaterial(
        "Concrete01", MAT_CONCRETE, fpc_conc, epsc0_conc, fpcu_conc, epsu_conc
    )

    # 3. Generic elastic reference
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_T, 1.999e5 * MPa)

    # 4. Aggregator shear (Vy, Vz) and torsional (T) elastic materials
    # Section 1 (NC400X400)
    ops.uniaxialMaterial("Elastic", MAT_VY_SEC1, ky_sec1)
    ops.uniaxialMaterial("Elastic", MAT_VZ_SEC1, kz_sec1)
    ops.uniaxialMaterial("Elastic", MAT_T_SEC1, gj_sec1)

    # Section 2 (NC400X600)
    ops.uniaxialMaterial("Elastic", MAT_VY_SEC2, ky_sec2)
    ops.uniaxialMaterial("Elastic", MAT_VZ_SEC2, kz_sec2)
    ops.uniaxialMaterial("Elastic", MAT_T_SEC2, gj_sec2)

    # Section 3 (NB300X600)
    ops.uniaxialMaterial("Elastic", MAT_VY_SEC3, ky_sec3)
    ops.uniaxialMaterial("Elastic", MAT_VZ_SEC3, kz_sec3)
    ops.uniaxialMaterial("Elastic", MAT_T_SEC3, gj_sec3)

    # Section 4 (NB300X500)
    ops.uniaxialMaterial("Elastic", MAT_VY_SEC4, ky_sec4)
    ops.uniaxialMaterial("Elastic", MAT_VZ_SEC4, kz_sec4)
    ops.uniaxialMaterial("Elastic", MAT_T_SEC4, gj_sec4)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
# Fiber data definitions: (y_mm, z_mm, area_mm2, mat_tag)
# NC400X400 (44 fibers: 36 concrete + 8 steel rebar)
FIBERS_SEC1 = [
    (-166.7, -166.7, 4444.0, 2), (-100.0, -166.7, 4444.0, 2), (-33.33, -166.7, 4444.0, 2),
    (33.33, -166.7, 4444.0, 2), (100.0, -166.7, 4444.0, 2), (166.7, -166.7, 4444.0, 2),
    (-166.7, -100.0, 4444.0, 2), (-100.0, -100.0, 4444.0, 2), (-33.33, -100.0, 4444.0, 2),
    (33.33, -100.0, 4444.0, 2), (100.0, -100.0, 4444.0, 2), (166.7, -100.0, 4444.0, 2),
    (-166.7, -33.33, 4444.0, 2), (-100.0, -33.33, 4444.0, 2), (-33.33, -33.33, 4444.0, 2),
    (33.33, -33.33, 4444.0, 2), (100.0, -33.33, 4444.0, 2), (166.7, -33.33, 4444.0, 2),
    (-166.7, 33.33, 4444.0, 2), (-100.0, 33.33, 4444.0, 2), (-33.33, 33.33, 4444.0, 2),
    (33.33, 33.33, 4444.0, 2), (100.0, 33.33, 4444.0, 2), (166.7, 33.33, 4444.0, 2),
    (-166.7, 100.0, 4444.0, 2), (-100.0, 100.0, 4444.0, 2), (-33.33, 100.0, 4444.0, 2),
    (33.33, 100.0, 4444.0, 2), (100.0, 100.0, 4444.0, 2), (166.7, 100.0, 4444.0, 2),
    (-166.7, 166.7, 4444.0, 2), (-100.0, 166.7, 4444.0, 2), (-33.33, 166.7, 4444.0, 2),
    (33.33, 166.7, 4444.0, 2), (100.0, 166.7, 4444.0, 2), (166.7, 166.7, 4444.0, 2),
    (-165.0, -165.0, 490.0, 1), (0.0, -165.0, 490.0, 1), (165.0, -165.0, 490.0, 1),
    (-165.0, 165.0, 490.0, 1), (0.0, 165.0, 490.0, 1), (165.0, 165.0, 490.0, 1),
    (-165.0, 0.0, 490.0, 1), (165.0, 0.0, 490.0, 1)
]

# NC400X600 (46 fibers: 36 concrete + 10 steel rebar)
FIBERS_SEC2 = [
    (-166.7, -250.0, 6667.0, 2), (-100.0, -250.0, 6667.0, 2), (-33.33, -250.0, 6667.0, 2),
    (33.33, -250.0, 6667.0, 2), (100.0, -250.0, 6667.0, 2), (166.7, -250.0, 6667.0, 2),
    (-166.7, -150.0, 6667.0, 2), (-100.0, -150.0, 6667.0, 2), (-33.33, -150.0, 6667.0, 2),
    (33.33, -150.0, 6667.0, 2), (100.0, -150.0, 6667.0, 2), (166.7, -150.0, 6667.0, 2),
    (-166.7, -50.0, 6667.0, 2), (-100.0, -50.0, 6667.0, 2), (-33.33, -50.0, 6667.0, 2),
    (33.33, -50.0, 6667.0, 2), (100.0, -50.0, 6667.0, 2), (166.7, -50.0, 6667.0, 2),
    (-166.7, 50.0, 6667.0, 2), (-100.0, 50.0, 6667.0, 2), (-33.33, 50.0, 6667.0, 2),
    (33.33, 50.0, 6667.0, 2), (100.0, 50.0, 6667.0, 2), (166.7, 50.0, 6667.0, 2),
    (-166.7, 150.0, 6667.0, 2), (-100.0, 150.0, 6667.0, 2), (-33.33, 150.0, 6667.0, 2),
    (33.33, 150.0, 6667.0, 2), (100.0, 150.0, 6667.0, 2), (166.7, 150.0, 6667.0, 2),
    (-166.7, 250.0, 6667.0, 2), (-100.0, 250.0, 6667.0, 2), (-33.33, 250.0, 6667.0, 2),
    (33.33, 250.0, 6667.0, 2), (100.0, 250.0, 6667.0, 2), (166.7, 250.0, 6667.0, 2),
    (-165.0, -265.0, 490.0, 1), (0.0, -265.0, 490.0, 1), (165.0, -265.0, 490.0, 1),
    (-165.0, 265.0, 490.0, 1), (0.0, 265.0, 490.0, 1), (165.0, 265.0, 490.0, 1),
    (-165.0, -88.33, 490.0, 1), (-165.0, 88.33, 490.0, 1),
    (165.0, -88.33, 490.0, 1), (165.0, 88.33, 490.0, 1)
]

# NB300X600 (47 fibers: 40 concrete + 7 steel rebar)
FIBERS_SEC3 = [
    (-112.5, -270.0, 4500.0, 2), (-37.5, -270.0, 4500.0, 2), (37.5, -270.0, 4500.0, 2), (112.5, -270.0, 4500.0, 2),
    (-112.5, -210.0, 4500.0, 2), (-37.5, -210.0, 4500.0, 2), (37.5, -210.0, 4500.0, 2), (112.5, -210.0, 4500.0, 2),
    (-112.5, -150.0, 4500.0, 2), (-37.5, -150.0, 4500.0, 2), (37.5, -150.0, 4500.0, 2), (112.5, -150.0, 4500.0, 2),
    (-112.5, -90.0, 4500.0, 2), (-37.5, -90.0, 4500.0, 2), (37.5, -90.0, 4500.0, 2), (112.5, -90.0, 4500.0, 2),
    (-112.5, -30.0, 4500.0, 2), (-37.5, -30.0, 4500.0, 2), (37.5, -30.0, 4500.0, 2), (112.5, -30.0, 4500.0, 2),
    (-112.5, 30.0, 4500.0, 2), (-37.5, 30.0, 4500.0, 2), (37.5, 30.0, 4500.0, 2), (112.5, 30.0, 4500.0, 2),
    (-112.5, 90.0, 4500.0, 2), (-37.5, 90.0, 4500.0, 2), (37.5, 90.0, 4500.0, 2), (112.5, 90.0, 4500.0, 2),
    (-112.5, 150.0, 4500.0, 2), (-37.5, 150.0, 4500.0, 2), (37.5, 150.0, 4500.0, 2), (112.5, 150.0, 4500.0, 2),
    (-112.5, 210.0, 4500.0, 2), (-37.5, 210.0, 4500.0, 2), (37.5, 210.0, 4500.0, 2), (112.5, 210.0, 4500.0, 2),
    (-112.5, 270.0, 4500.0, 2), (-37.5, 270.0, 4500.0, 2), (37.5, 270.0, 4500.0, 2), (112.5, 270.0, 4500.0, 2),
    (-115.0, 265.0, 490.0, 1), (0.0, 265.0, 490.0, 1), (115.0, 265.0, 490.0, 1),
    (-115.0, -265.0, 490.0, 1), (-38.33, -265.0, 490.0, 1), (38.33, -265.0, 490.0, 1), (115.0, -265.0, 490.0, 1)
]

# NB300X500 (45 fibers: 40 concrete + 5 steel rebar)
FIBERS_SEC4 = [
    (-112.5, -225.0, 3750.0, 2), (-37.5, -225.0, 3750.0, 2), (37.5, -225.0, 3750.0, 2), (112.5, -225.0, 3750.0, 2),
    (-112.5, -175.0, 3750.0, 2), (-37.5, -175.0, 3750.0, 2), (37.5, -175.0, 3750.0, 2), (112.5, -175.0, 3750.0, 2),
    (-112.5, -125.0, 3750.0, 2), (-37.5, -125.0, 3750.0, 2), (37.5, -125.0, 3750.0, 2), (112.5, -125.0, 3750.0, 2),
    (-112.5, -75.0, 3750.0, 2), (-37.5, -75.0, 3750.0, 2), (37.5, -75.0, 3750.0, 2), (112.5, -75.0, 3750.0, 2),
    (-112.5, -25.0, 3750.0, 2), (-37.5, -25.0, 3750.0, 2), (37.5, -25.0, 3750.0, 2), (112.5, -25.0, 3750.0, 2),
    (-112.5, 25.0, 3750.0, 2), (-37.5, 25.0, 3750.0, 2), (37.5, 25.0, 3750.0, 2), (112.5, 25.0, 3750.0, 2),
    (-112.5, 75.0, 3750.0, 2), (-37.5, 75.0, 3750.0, 2), (37.5, 75.0, 3750.0, 2), (112.5, 75.0, 3750.0, 2),
    (-112.5, 125.0, 3750.0, 2), (-37.5, 125.0, 3750.0, 2), (37.5, 125.0, 3750.0, 2), (112.5, 125.0, 3750.0, 2),
    (-112.5, 175.0, 3750.0, 2), (-37.5, 175.0, 3750.0, 2), (37.5, 175.0, 3750.0, 2), (112.5, 175.0, 3750.0, 2),
    (-112.5, 225.0, 3750.0, 2), (-37.5, 225.0, 3750.0, 2), (37.5, 225.0, 3750.0, 2), (112.5, 225.0, 3750.0, 2),
    (-115.0, 215.0, 490.0, 1), (115.0, 215.0, 490.0, 1),
    (-115.0, -215.0, 490.0, 1), (0.0, -215.0, 490.0, 1), (115.0, -215.0, 490.0, 1)
]


def define_sections() -> None:
    """Define fiber sections and composite Aggregator sections."""
    fiber_sections = [
        (SEC_FIBER_COL_400X400, FIBERS_SEC1),
        (SEC_FIBER_COL_400X600, FIBERS_SEC2),
        (SEC_FIBER_BEAM_300X600, FIBERS_SEC3),
        (SEC_FIBER_BEAM_300X500, FIBERS_SEC4),
    ]

    for sec_tag, fibers in fiber_sections:
        # -GJ 1.0 required by OpenSeesPy for 3D fiber sections; Aggregator supplies actual T
        ops.section("Fiber", sec_tag, "-GJ", 1.0)
        for y, z, a, m in fibers:
            ops.fiber(y, z, a, m)

    # Aggregator sections: combines Fiber (P, Mz, My) with elastic Vy, Vz, and T
    ops.section("Aggregator", SEC_AGG_COL_400X400, MAT_VY_SEC1, "Vy", MAT_VZ_SEC1, "Vz", MAT_T_SEC1, "T", "-section", SEC_FIBER_COL_400X400)
    ops.section("Aggregator", SEC_AGG_COL_400X600, MAT_VY_SEC2, "Vy", MAT_VZ_SEC2, "Vz", MAT_T_SEC2, "T", "-section", SEC_FIBER_COL_400X600)
    ops.section("Aggregator", SEC_AGG_BEAM_300X600, MAT_VY_SEC3, "Vy", MAT_VZ_SEC3, "Vz", MAT_T_SEC3, "T", "-section", SEC_FIBER_BEAM_300X600)
    ops.section("Aggregator", SEC_AGG_BEAM_300X500, MAT_VY_SEC4, "Vy", MAT_VZ_SEC4, "Vz", MAT_T_SEC4, "T", "-section", SEC_FIBER_BEAM_300X500)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
# (tag, x_mm, y_mm, z_mm)
NODE_COORDS = [
    (1,  4500.0 * mm, 5000.0 * mm, 10500.0 * mm),
    (2,  4500.0 * mm, 5000.0 * mm, 13500.0 * mm),
    (3,  4500.0 * mm,    0.0 * mm, 10500.0 * mm),
    (4,  4500.0 * mm,    0.0 * mm, 13500.0 * mm),
    (5,     0.0 * mm,    0.0 * mm, 10500.0 * mm),
    (6,     0.0 * mm,    0.0 * mm, 13500.0 * mm),
    (7,     0.0 * mm, 5000.0 * mm, 10500.0 * mm),
    (8,     0.0 * mm, 5000.0 * mm, 13500.0 * mm),
    (9,  4500.0 * mm,    0.0 * mm,  7500.0 * mm),
    (10, 4500.0 * mm, 5000.0 * mm,  7500.0 * mm),
    (11,    0.0 * mm,    0.0 * mm,  7500.0 * mm),
    (12,    0.0 * mm, 5000.0 * mm,  7500.0 * mm),
    (13, 9000.0 * mm,    0.0 * mm,  7500.0 * mm),
    (14, 9000.0 * mm,    0.0 * mm, 10500.0 * mm),
    (15, 9000.0 * mm, 5000.0 * mm,  7500.0 * mm),
    (16, 9000.0 * mm, 5000.0 * mm, 10500.0 * mm),
    (17, 4500.0 * mm,    0.0 * mm,  4500.0 * mm),
    (18, 4500.0 * mm, 5000.0 * mm,  4500.0 * mm),
    (19,    0.0 * mm,    0.0 * mm,  4500.0 * mm),
    (20,    0.0 * mm, 5000.0 * mm,  4500.0 * mm),
    (21, 9000.0 * mm,    0.0 * mm,  4500.0 * mm),
    (22, 9000.0 * mm, 5000.0 * mm,  4500.0 * mm),
    (23, 4500.0 * mm,    0.0 * mm,     0.0 * mm),
    (24, 4500.0 * mm, 5000.0 * mm,     0.0 * mm),
    (25,    0.0 * mm,    0.0 * mm,     0.0 * mm),
    (26,    0.0 * mm, 5000.0 * mm,     0.0 * mm),
    (27, 9000.0 * mm,    0.0 * mm,     0.0 * mm),
    (28, 9000.0 * mm, 5000.0 * mm,     0.0 * mm),
]


def define_nodes() -> None:
    """Instantiate all 28 frame nodes."""
    for tag, x, y, z in NODE_COORDS:
        ops.node(tag, x, y, z)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix all 6 DOFs for base column nodes at ground level (Z = 0)."""
    for node in BASE_NODES:
        ops.fix(node, 1, 1, 1, 1, 1, 1)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
# Element connectivity: (ele_tag, node_i, node_j, sec_tag, is_column)
ELEMENTS_DATA = [
    # 4th Story Columns (NC400X400)
    (1,   1,  2, SEC_AGG_COL_400X400,  True),
    (2,   3,  4, SEC_AGG_COL_400X400,  True),
    (3,   5,  6, SEC_AGG_COL_400X400,  True),
    (4,   7,  8, SEC_AGG_COL_400X400,  True),
    # 4th Story Beams (NB300X600 and NB300X500)
    (5,   6,  8, SEC_AGG_BEAM_300X600, False),
    (6,   4,  2, SEC_AGG_BEAM_300X600, False),
    (7,   8,  2, SEC_AGG_BEAM_300X500, False),
    (8,   6,  4, SEC_AGG_BEAM_300X500, False),
    # 3rd Story Columns
    (9,   9,  3, SEC_AGG_COL_400X400,  True),
    (10, 10,  1, SEC_AGG_COL_400X400,  True),
    (11, 11,  5, SEC_AGG_COL_400X600,  True),
    (12, 12,  7, SEC_AGG_COL_400X600,  True),
    (13, 13, 14, SEC_AGG_COL_400X600,  True),
    (14, 15, 16, SEC_AGG_COL_400X600,  True),
    # 3rd Story Beams
    (15,  7,  1, SEC_AGG_BEAM_300X500, False),
    (16,  1, 16, SEC_AGG_BEAM_300X500, False),
    (17,  3, 14, SEC_AGG_BEAM_300X500, False),
    (18,  5,  3, SEC_AGG_BEAM_300X500, False),
    (19,  3,  1, SEC_AGG_BEAM_300X600, False),
    (20, 14, 16, SEC_AGG_BEAM_300X600, False),
    (21,  5,  7, SEC_AGG_BEAM_300X600, False),
    # 2nd Story Columns
    (22, 17,  9, SEC_AGG_COL_400X400,  True),
    (23, 18, 10, SEC_AGG_COL_400X400,  True),
    (24, 19, 11, SEC_AGG_COL_400X600,  True),
    (25, 20, 12, SEC_AGG_COL_400X600,  True),
    (26, 21, 13, SEC_AGG_COL_400X600,  True),
    (27, 22, 15, SEC_AGG_COL_400X600,  True),
    # 2nd Story Beams
    (28, 12, 10, SEC_AGG_BEAM_300X500, False),
    (29, 10, 15, SEC_AGG_BEAM_300X500, False),
    (30,  9, 13, SEC_AGG_BEAM_300X500, False),
    (31, 11,  9, SEC_AGG_BEAM_300X500, False),
    (32,  9, 10, SEC_AGG_BEAM_300X600, False),
    (33, 13, 15, SEC_AGG_BEAM_300X600, False),
    (34, 11, 12, SEC_AGG_BEAM_300X600, False),
    # 1st Story Columns (Base to Floor 1)
    (35, 23, 17, SEC_AGG_COL_400X400,  True),
    (36, 24, 18, SEC_AGG_COL_400X400,  True),
    (37, 25, 19, SEC_AGG_COL_400X600,  True),
    (38, 26, 20, SEC_AGG_COL_400X600,  True),
    (39, 27, 21, SEC_AGG_COL_400X600,  True),
    (40, 28, 22, SEC_AGG_COL_400X600,  True),
    # 1st Story Beams
    (41, 20, 18, SEC_AGG_BEAM_300X500, False),
    (42, 18, 22, SEC_AGG_BEAM_300X500, False),
    (43, 17, 21, SEC_AGG_BEAM_300X500, False),
    (44, 19, 17, SEC_AGG_BEAM_300X500, False),
    (45, 17, 18, SEC_AGG_BEAM_300X600, False),
    (46, 21, 22, SEC_AGG_BEAM_300X600, False),
    (47, 19, 20, SEC_AGG_BEAM_300X600, False),
]


def define_elements() -> None:
    """Define geometric transformations and 47 nonlinear beam-column elements."""
    # Column transform: PDelta with local x oriented along global X
    ops.geomTransf("PDelta", TRANSF_COL_PDELTA, 1.0, 0.0, 0.0)
    # Beam transform: Linear with local x oriented along global Z
    ops.geomTransf("Linear", TRANSF_BEAM_LINEAR, 0.0, 0.0, 1.0)

    for ele_tag, ni, nj, sec_tag, is_column in ELEMENTS_DATA:
        transf_tag = TRANSF_COL_PDELTA if is_column else TRANSF_BEAM_LINEAR
        ops.element(
            "nonlinearBeamColumn", ele_tag, ni, nj, N_INT_PTS, sec_tag, transf_tag
        )


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: int = ODB_TAG) -> "opst.post.CreateODB":
    """Initialise opstool CreateODB output database for response collection.

    Args:
        output_dir: Directory where the ODB file will be written.
        odb_tag: Identifier tag for this database.

    Returns:
        Initialised CreateODB instance with model topology saved.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
# Distributed gravity beam loads: (ele_tag, wz_N_per_mm)
GRAVITY_ELE_LOADS = [
    # 4th Story Beams
    (5, -3.797 * N / mm), (5, -1.688 * N / mm), (5, -3.797 * N / mm),
    (8, -4.219 * N / mm), (8, -4.219 * N / mm),
    (6, -3.797 * N / mm), (6, -1.688 * N / mm), (6, -3.797 * N / mm),
    (7, -4.219 * N / mm), (7, -4.219 * N / mm),
    # 3rd Story Beams
    (15, -4.219 * N / mm), (15, -4.219 * N / mm),
    (21, -3.797 * N / mm), (21, -1.688 * N / mm), (21, -3.797 * N / mm),
    (18, -4.219 * N / mm), (18, -4.219 * N / mm),
    (19, -3.797 * N / mm), (19, -1.688 * N / mm), (19, -3.797 * N / mm),
    (16, -4.219 * N / mm), (16, -4.219 * N / mm),
    (19, -3.797 * N / mm), (19, -1.688 * N / mm), (19, -3.797 * N / mm),
    (17, -4.219 * N / mm), (17, -4.219 * N / mm),
    (20, -3.797 * N / mm), (20, -1.688 * N / mm), (20, -3.797 * N / mm),
    # 2nd Story Beams
    (28, -4.219 * N / mm), (28, -4.219 * N / mm),
    (34, -3.797 * N / mm), (34, -1.688 * N / mm), (34, -3.797 * N / mm),
    (31, -4.219 * N / mm), (31, -4.219 * N / mm),
    (32, -3.797 * N / mm), (32, -1.688 * N / mm), (32, -3.797 * N / mm),
    (29, -4.219 * N / mm), (29, -4.219 * N / mm),
    (32, -3.797 * N / mm), (32, -1.688 * N / mm), (32, -3.797 * N / mm),
    (30, -4.219 * N / mm), (30, -4.219 * N / mm),
    (33, -3.797 * N / mm), (33, -1.688 * N / mm), (33, -3.797 * N / mm),
    # 1st Story Beams
    (41, -4.219 * N / mm), (41, -4.219 * N / mm),
    (47, -3.797 * N / mm), (47, -1.688 * N / mm), (47, -3.797 * N / mm),
    (44, -4.219 * N / mm), (44, -4.219 * N / mm),
    (45, -3.797 * N / mm), (45, -1.688 * N / mm), (45, -3.797 * N / mm),
    (42, -4.219 * N / mm), (42, -4.219 * N / mm),
    (45, -3.797 * N / mm), (45, -1.688 * N / mm), (45, -3.797 * N / mm),
    (43, -4.219 * N / mm), (43, -4.219 * N / mm),
    (46, -3.797 * N / mm), (46, -1.688 * N / mm), (46, -3.797 * N / mm),
]

# Lateral pushover nodal loads (inverted triangular distribution): (node_tag, fx_N)
LATERAL_NODAL_LOADS = [
    # Story 4 (Roof, Z = 13500 mm)
    (6, 13500.0 * N), (8, 13500.0 * N),
    # Story 3 (Z = 10500 mm)
    (5, 10500.0 * N), (7, 10500.0 * N),
    # Story 2 (Z = 7500 mm)
    (11, 7500.0 * N), (12, 7500.0 * N),
    # Story 1 (Z = 4500 mm)
    (19, 4500.0 * N), (20, 4500.0 * N),
]


def define_gravity_loads() -> None:
    """Apply uniform beam loads under gravity dead load pattern."""
    ops.timeSeries("Linear", TS_LINEAR)
    ops.pattern("Plain", PAT_DEAD, TS_LINEAR)
    for ele_tag, wz in GRAVITY_ELE_LOADS:
        ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform", 0.0, wz, 0.0)


def define_lateral_loads() -> None:
    """Apply inverted-triangular reference lateral point loads in global +X direction."""
    ops.timeSeries("Linear", 2)
    ops.pattern("Plain", PAT_PUSH, 2)
    for node, fx in LATERAL_NODAL_LOADS:
        ops.load(node, fx, 0.0, 0.0, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB", n_steps: int = N_GRAV_STEPS) -> None:
    """Run load-controlled static gravity analysis with ODB response collection.

    Permitted exception per AGENT.md §3c / §10: SmartAnalyze.StaticAnalyze forcibly
    imposes DisplacementControl, so a manual LoadControl loop with odb.fetch_response_step()
    is used to accurately apply incremental gravity loads.
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.analysis("Static")

    for _ in range(n_steps):
        ok = ops.analyze(1)
        if ok != 0:
            raise RuntimeError("Gravity analysis failed to converge.")
        odb.fetch_response_step()

    # Freeze gravity loads and clear static analysis object
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def run_pushover(
    odb: "opst.post.CreateODB",
    ctrl_node: int = CTRL_NODE,
    ctrl_dof: int = CTRL_DOF,
    target_disp: float = TARGET_DISP,
    max_step: float = PUSH_STEP_SIZE,
) -> None:
    """Run displacement-controlled pushover using SmartAnalyze."""
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="EnergyIncr",
        testTol=1.0e-3,
        testIterTimes=1000,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 40, 20, 30],
    )

    protocol = [target_disp]
    segs = analysis.static_split(protocol, maxStep=max_step)
    for seg in segs:
        analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
        odb.fetch_response_step()
    analysis.close()


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity and pushover analyses, and return populated ODB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)                           # V1: Nodes & supports

    define_elements()
    vis_model(output_dir)                           # V2: Full mesh geometry

    odb = create_odb(output_dir)
    define_gravity_loads()
    vis_loads(output_dir)                           # V3: Load vectors
    vis_pre_analysis(output_dir)                    # V4: Pre-analysis check

    run_gravity(odb)
    define_lateral_loads()                          # Defined AFTER loadConst per §12z-1
    run_pushover(odb)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and render interactive HTML visualizations.

    Args:
        odb: Populated CreateODB instance returned by run_analysis().
        output_dir: Directory where ODB and HTML outputs are saved.
    """
    odb.save_response()
    opst.post.set_odb_path(str(output_dir))

    if not _headless():
        vis_defo(
            output_dir,
            filename="vis_05_deformed.html",
            odb_tag=ODB_TAG,
            resp_dof="UX",
            scale=5.0,
        )
        vis_slider(
            output_dir,
            filename="vis_06_slider.html",
            odb_tag=ODB_TAG,
            resp_dof="UX",
            scale=5.0,
        )


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
