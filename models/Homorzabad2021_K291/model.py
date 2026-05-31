# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 6-Story CRSBF Building (Concentrically Braced Frame with Rocking)
UniqueID : Homorzabad2021_K291
Author   : S. Homorzabad, ported by OpenSeesPy Standardisation Agent
Date     : 2026-05-29
Purpose  : 3D nonlinear time-history analysis of a 6-story concentrically-braced
           steel frame with rocking, PT strands, and fuse assemblies.
Ref      : CRSBF-NDAP.py — optimization framework for CBFs with rocking
Units    : N, mm, MPa (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import numpy as np

# Compatibility: opstool v0.8.7 uses deprecated np.NAN / np.NaN (patch BEFORE opstool import)
np.NAN = np.nan
np.NaN = np.nan

import openseespy.opensees as ops

import sys
from pathlib import Path
import time
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from units import *



# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────

# Geometric transformations
TRANS_Y = 1  # PDelta — vector (1,0,0)
TRANS_X = 2  # PDelta — vector (0,-1,0)

# Materials
MAT_STRAND_PP1  = 201
MAT_STRAND_PP2  = 202
MAT_STRAND_PAR  = 203
MAT_BASE_SPRING = 301
MAT_FUSE_GAP    = 401
MAT_FUSE_STEEL  = 414

# Section data (1-indexed): (A, Iy, Iz, J)  — from Section_Mat.txt
# Values converted from m²→mm² (×1e6) and m⁴→mm⁴ (×1e12) for N-mm unit system
_SEC = [
    None,
    (10200.0,      1.257e8,    4.314e7,    2.094733e9),    # 1
    (12900.0,      1.638e8,    5.549e7,    4.303334e9),    # 2
    (16700.0,      2.215e8,    7.446e7,    9.515365e9),    # 3
    (21200.0,      3.002e8,    9.879e7,    1.8869649e10),  # 4
    (22800.0,      4.453e8,    1.438e8,    1.829304e10),   # 5
    (28800.0,      5.956e8,    1.893e8,    3.4536757e10),  # 6
    (32300.0,      6.84e8,     2.15e8,     4.6950566e10),  # 7
    (36000.0,      7.87e8,     2.45e8,     6.3722278e10),  # 8
    (40000.0,      1.10e9,     4.27e8,     6.0523082e10),  # 9
    (43400.0,      3.18e9,     2.71e8,     6.3075296e10),  # 10
    (49500.0,      5.44e9,     4.00e8,     6.7885701e10),  # 11
    (60300.0,      8.13e9,     5.37e8,     1.02952701e11), # 12
]

[VS1, VS2, VS3, VS4, VS5, VS6, VS7, VS8, VS9, VS10, VS11, VS12] = range(1, 13)

# Strut properties (converted from m²→mm², m⁴→mm⁴)
AC1 = 13376.0           # 0.013376 m²
IC1 = 1.15373416e8      # 1.15373416e-4 m⁴

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
B_X = 6.0 * m        # bay width X → 6000 mm
B_Y = 6.0 * m        # bay width Y → 6000 mm
H_S = 4.0 * m        # story height → 4000 mm

Es = 2.05e5 * MPa     # 205 GPa — converted from 2.05e11 Pa (SI → N/mm²)
Gs = 7.93e4 * MPa     # 79.3 GPa — converted from 7.93e10 Pa

M_n = 24.0 * kg         # 24000 kg in SI consistent mass

Strand_Area = 890.28e-6 * m**2

KvA   = 2.99151e5       # N/mm — converted from 2.99151e8 N/m
Kf1A  = KvA / 1000.0    # = 299.151 N/mm
Kf2A  = KvA * 1000.0    # = 2.99151e8 N/mm
Fuse_Yield = 450000.0 * N

n_stories = 6

XDAMP = 0.05
GM_DT = 0.02
GM_POINTS = 2500
EQ_FACTOR = 0.69

# ── Coordinate helpers ───────────────────────────────────────────────────────
def _x(gx: float) -> float: return gx * B_X
def _y(gy: float) -> float: return gy * B_Y
def _z(fl: int) -> float:   return fl * H_S

# ── Ground-floor (tag → gx, gy) for all grid points ─────────────────────────
_GROUND = [
    (1, 0, 0), (2, 1, 0), (4, 2, 0), (5, 3, 0), (7, 4, 0), (8, 5, 0),
    (11, 0, 0.5), (18, 5, 0.5),
    (21, 0, 1), (22, 1, 1), (23, 1.5, 1), (24, 2, 1), (25, 3, 1),
    (26, 3.5, 1), (27, 4, 1), (28, 5, 1),
    (31, 0, 2), (32, 1, 2), (34, 2, 2), (35, 3, 2), (37, 4, 2), (38, 5, 2),
    (41, 0, 3), (42, 1, 3), (43, 1.5, 3), (44, 2, 3), (45, 3, 3),
    (46, 3.5, 3), (47, 4, 3), (48, 5, 3),
    (51, 0, 3.5), (58, 5, 3.5),
    (61, 0, 4), (62, 1, 4), (64, 2, 4), (65, 3, 4), (67, 4, 4), (68, 5, 4),
]

def _sec(sec_id: int) -> tuple:
    return _SEC[sec_id]

def _e(eid: int, n1: int, n2: int, sec: int, tr: int) -> None:
    A, Iy, Iz, J = _sec(sec)
    ops.element("elasticBeamColumn", eid, n1, n2, A, Es, Gs, J, Iy, Iz, tr)

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    # Strand moduli converted from Pa to MPa (N/mm²)
    ops.uniaxialMaterial("ElasticPP",     MAT_STRAND_PP1, 8.7799e4, 0.0120, -0.0158, -0.0038)
    ops.uniaxialMaterial("ElasticPP",     MAT_STRAND_PP2, 9.0201e4, 0.0089, -0.0127, -0.0038)
    ops.uniaxialMaterial("Parallel",      MAT_STRAND_PAR, MAT_STRAND_PP1, MAT_STRAND_PP2)
    # Base spring stiffness converted from N/m to N/mm
    ops.uniaxialMaterial("ENT",           MAT_BASE_SPRING, 1.0e6)
    ops.uniaxialMaterial("SelfCentering", MAT_FUSE_GAP,
                          Kf1A, 0.0, Kf1A * 0.0005, 0.0, 0.0, 0.0005, 1.0e6)
    # Fuse steel E0 converted from Pa to MPa
    ops.uniaxialMaterial("Steel01",       MAT_FUSE_STEEL,
                          Fuse_Yield, 373038.0, 0.04, 0.06, 1.0, 0.0, 1.0)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    pass

# ── 7. NODES ─────────────────────────────────────────────────────────────────
# Column ground tags (nodes with columns on every floor)
_COL_GT = {1, 2, 4, 5, 7, 8, 21, 22, 24, 25, 27, 28,
           31, 32, 34, 35, 37, 38, 41, 42, 44, 45, 47, 48, 61, 62, 64, 65, 67, 68}

def _floor_nodes(fl: int) -> set:
    """Return the set of floor-node tags that exist on a given floor (1-indexed).
    Only nodes referenced by columns or beams are created."""
    nodes = {fl * 100 + gt for gt in _COL_GT}
    # X-beam nodes per floor (full rows A,E,I every floor; rows C,G: skip mid-side on even floors)
    for gt in [1, 2, 4, 5, 7, 8, 31, 32, 34, 35, 37, 38, 61, 62, 64, 65, 67, 68]:
        nodes.add(fl * 100 + gt)
    if fl in (1, 3, 5, 6):
        for gt in [23, 26, 43, 46]:
            nodes.add(fl * 100 + gt)
    # Y-beam nodes per floor (rows A,F: mid-side on odd floors only)
    for gt in [2, 22, 32, 42, 62, 4, 24, 34, 44, 64, 5, 25, 35, 45, 65, 7, 27, 37, 47, 67]:
        nodes.add(fl * 100 + gt)
    if fl in (1, 3, 5, 6):
        for gt in [11, 51, 18, 58]:
            nodes.add(fl * 100 + gt)
    return nodes


def define_nodes() -> None:
    # Lookup: ground tag → (x, y)
    _gt_to_xy = {tag: (_x(gx), _y(gy)) for tag, gx, gy in _GROUND}
    # Ground floor
    for tag, gx, gy in _GROUND:
        ops.node(tag, gx * B_X, gy * B_Y, _z(0))
    # Floors 1-6
    for fl in range(1, n_stories + 1):
        z = _z(fl)
        for tag in _floor_nodes(fl):
            gt = tag % 100
            x, y = _gt_to_xy[gt]
            ops.node(tag, x, y, z)
    # Fuse nodes at ground level
    for tag, gx, gy in [(1011, 0, 0.5), (1018, 5, 0.5),
                         (1023, 1.5, 1), (1026, 3.5, 1),
                         (1043, 1.5, 3), (1046, 3.5, 3),
                         (1051, 0, 3.5), (1058, 5, 3.5)]:
        ops.node(tag, _x(gx), _y(gy), _z(0))
    # Intermediate fuse nodes
    for tag, gx, gy in [(2011, 0, 0.5), (2018, 5, 0.5),
                         (2023, 1.5, 1), (2026, 3.5, 1),
                         (2043, 1.5, 3), (2046, 3.5, 3),
                         (2051, 0, 3.5), (2058, 5, 3.5)]:
        ops.node(tag, _x(gx), _y(gy), _z(0))
    # Column base nodes at rocking bays (z = -0.2 mm)
    for tag, gx, gy in [(1001, 0, 0), (1008, 5, 0),
                         (1021, 0, 1), (1022, 1, 1), (1024, 2, 1),
                         (1025, 3, 1), (1027, 4, 1), (1028, 5, 1),
                         (1041, 0, 3), (1042, 1, 3), (1044, 2, 3),
                         (1045, 3, 3), (1047, 4, 3), (1048, 5, 3),
                         (1061, 0, 4), (1068, 5, 4)]:
        ops.node(tag, _x(gx), _y(gy), -0.2)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    for n in [2, 4, 5, 7, 31, 32, 34, 35, 37, 38, 62, 64, 65, 67]:
        ops.fix(n, 1, 1, 1, 1, 1, 1)
    for n in [1001, 1008, 1021, 1022, 1024, 1025, 1027, 1028,
              1041, 1042, 1044, 1045, 1047, 1048, 1061, 1068]:
        ops.fix(n, 1, 1, 1, 1, 1, 1)
    for n in [1011, 1018, 1023, 1026, 1043, 1046, 1051, 1058]:
        ops.fix(n, 1, 1, 1, 1, 1, 1)
    for n in [2011, 2018, 2023, 2026, 2043, 2046, 2051, 2058]:
        ops.fix(n, 1, 1, 0, 1, 1, 1)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def _define_geom_transforms() -> None:
    ops.geomTransf("PDelta", TRANS_Y, 1.0, 0.0, 0.0)
    ops.geomTransf("PDelta", TRANS_X, 0.0, -1.0, 0.0)

# --- Columns ----------------------------------------------------------------
def _define_columns() -> None:
    # Story 1 (ground → fl1): eid = 1000 + ground_tag
    for gt, s in [(1,VS1),(2,VS1),(4,VS1),(5,VS1),(7,VS1),(8,VS1),
                  (21,VS1),(22,VS2),(24,VS2),(25,VS2),(27,VS2),(28,VS1),
                  (31,VS1),(32,VS2),(34,VS2),(35,VS2),(37,VS2),(38,VS1),
                  (41,VS1),(42,VS2),(44,VS2),(45,VS2),(47,VS2),(48,VS1),
                  (61,VS1),(62,VS1),(64,VS1),(65,VS1),(67,VS1),(68,VS1)]:
        _e(1000 + gt, gt, 100 + gt, s, TRANS_Y)

    # Story 2 (fl1→fl2): eid = 1000 + 100 + ground_tag
    for gt, s in [(1,VS1),(2,VS1),(4,VS1),(5,VS1),(7,VS1),(8,VS1),
                  (21,VS1),(22,VS2),(24,VS2),(25,VS2),(27,VS2),(28,VS1),
                  (31,VS1),(32,VS2),(34,VS2),(35,VS2),(37,VS2),(38,VS1),
                  (41,VS1),(42,VS2),(44,VS2),(45,VS2),(47,VS2),(48,VS1),
                  (61,VS1),(62,VS1),(64,VS1),(65,VS1),(67,VS1),(68,VS1)]:
        _e(1100 + gt, 100 + gt, 200 + gt, s, TRANS_Y)

    # Story 3 (fl2→fl3)
    for gt, s in [(1,VS3),(2,VS3),(4,VS3),(5,VS3),(7,VS3),(8,VS3),
                  (21,VS3),(22,VS4),(24,VS4),(25,VS4),(27,VS4),(28,VS3),
                  (31,VS3),(32,VS4),(34,VS4),(35,VS4),(37,VS4),(38,VS3),
                  (41,VS3),(42,VS4),(44,VS4),(45,VS4),(47,VS4),(48,VS3),
                  (61,VS3),(62,VS3),(64,VS3),(65,VS3),(67,VS3),(68,VS3)]:
        _e(1200 + gt, 200 + gt, 300 + gt, s, TRANS_Y)

    # Story 4 (fl3→fl4)
    for gt, s in [(1,VS3),(2,VS3),(4,VS3),(5,VS3),(7,VS3),(8,VS3),
                  (21,VS3),(22,VS4),(24,VS4),(25,VS4),(27,VS4),(28,VS3),
                  (31,VS3),(32,VS4),(34,VS4),(35,VS4),(37,VS4),(38,VS3),
                  (41,VS3),(42,VS4),(44,VS4),(45,VS4),(47,VS4),(48,VS3),
                  (61,VS3),(62,VS3),(64,VS3),(65,VS3),(67,VS3),(68,VS3)]:
        _e(1300 + gt, 300 + gt, 400 + gt, s, TRANS_Y)

    # Story 5 (fl4→fl5)
    for gt, s in [(1,VS5),(2,VS5),(4,VS5),(5,VS5),(7,VS5),(8,VS5),
                  (21,VS5),(22,VS6),(24,VS6),(25,VS6),(27,VS6),(28,VS5),
                  (31,VS5),(32,VS6),(34,VS6),(35,VS6),(37,VS6),(38,VS5),
                  (41,VS5),(42,VS6),(44,VS6),(45,VS6),(47,VS6),(48,VS5),
                  (61,VS5),(62,VS5),(64,VS5),(65,VS5),(67,VS5),(68,VS5)]:
        _e(1400 + gt, 400 + gt, 500 + gt, s, TRANS_Y)

    # Story 6 (fl5→fl6)
    for gt, s in [(1,VS5),(2,VS5),(4,VS5),(5,VS5),(7,VS5),(8,VS5),
                  (21,VS5),(22,VS6),(24,VS6),(25,VS6),(27,VS6),(28,VS5),
                  (31,VS5),(32,VS6),(34,VS6),(35,VS6),(37,VS6),(38,VS5),
                  (41,VS5),(42,VS6),(44,VS6),(45,VS6),(47,VS6),(48,VS5),
                  (61,VS5),(62,VS5),(64,VS5),(65,VS5),(67,VS5),(68,VS5)]:
        _e(1500 + gt, 500 + gt, 600 + gt, s, TRANS_Y)

# --- X-direction beams -------------------------------------------------------
# Per-floor span pairs for rows that have irregular mid-side nodes
_X_SPANS = {
    # Row C: mid-side gt=23,26 skipped on even floors
    "C": {f: [(21,22),(22,23),(23,24),(24,25),(25,26),(26,27),(27,28)]
          if f in (1,3,5,6) else [(21,22),(22,24),(24,25),(25,27),(27,28)]
          for f in range(1, 7)},
    # Row G: mid-side gt=43,46 skipped on even floors
    "G": {f: [(41,42),(42,43),(43,44),(44,45),(45,46),(46,47),(47,48)]
          if f in (1,3,5,6) else [(41,42),(42,44),(44,45),(45,47),(47,48)]
          for f in range(1, 7)},
}

def _define_beams_x() -> None:
    for fl in range(1, n_stories + 1):
        sec = VS7 if fl <= 2 else (VS8 if fl <= 4 else VS9)
        fl_base = (20 + fl) * 100
        off = fl * 100
        # Row A, E, I (regular: same spans every floor)
        for a, b in [(1,2),(2,4),(4,5),(5,7),(7,8)]:
            _e(fl_base + a, off + a, off + b, sec, TRANS_X)
        for a, b in [(31,32),(32,34),(34,35),(35,37),(37,38)]:
            _e(fl_base + a, off + a, off + b, sec, TRANS_X)
        for a, b in [(61,62),(62,64),(64,65),(65,67),(67,68)]:
            _e(fl_base + a, off + a, off + b, sec, TRANS_X)
        # Row C (irregular on even floors)
        for a, b in _X_SPANS["C"][fl]:
            _e(fl_base + a, off + a, off + b, sec, TRANS_X)
        # Row G (irregular on even floors)
        for a, b in _X_SPANS["G"][fl]:
            _e(fl_base + a, off + a, off + b, sec, TRANS_X)

# --- Y-direction beams -------------------------------------------------------
# Node sequences per row (ground tags, per-floor). Rows A and F skip mid-side
# nodes on even floors (2, 4) matching the original model.
_Y_LINES = {
    1: {1: [1, 11, 21, 31, 41, 51, 61], 2: [1, 21, 31, 41, 61],
        3: [1, 11, 21, 31, 41, 51, 61], 4: [1, 21, 31, 41, 61],
        5: [1, 11, 21, 31, 41, 51, 61], 6: [1, 11, 21, 31, 41, 51, 61]},
    2: {f: [2, 22, 32, 42, 62] for f in range(1, 7)},
    4: {f: [4, 24, 34, 44, 64] for f in range(1, 7)},
    5: {f: [5, 25, 35, 45, 65] for f in range(1, 7)},
    7: {f: [7, 27, 37, 47, 67] for f in range(1, 7)},
    8: {1: [8, 18, 28, 38, 48, 58, 68], 2: [8, 28, 38, 48, 68],
        3: [8, 18, 28, 38, 48, 58, 68], 4: [8, 28, 38, 48, 68],
        5: [8, 18, 28, 38, 48, 58, 68], 6: [8, 18, 28, 38, 48, 58, 68]},
}

def _define_beams_y() -> None:
    for fl in range(1, n_stories + 1):
        sec = VS7 if fl <= 2 else (VS8 if fl <= 4 else VS9)
        fl_base = (30 + fl) * 100
        off = fl * 100
        for row_base, seqs in _Y_LINES.items():
            gt_seq = seqs[fl]
            for i in range(len(gt_seq) - 1):
                tag = fl_base + row_base + i * 10
                _e(tag, off + gt_seq[i], off + gt_seq[i + 1], sec, TRANS_Y)

# --- Braces -------------------------------------------------------------------
_BRACE_SPECS = {
    # (section, transform): list of (eid, n1, n2)
    "S1": (VS10, TRANS_X, [
        (4022, 22, 123), (4024, 24, 123), (4025, 25, 126), (4027, 27, 126),
        (4042, 42, 143), (4044, 44, 143), (4045, 45, 146), (4047, 47, 146),
    ]),
    "S2": (VS10, TRANS_X, [
        (4122, 123, 222), (4124, 123, 224), (4125, 126, 225), (4127, 126, 227),
        (4142, 143, 242), (4144, 143, 244), (4145, 146, 245), (4147, 146, 247),
    ]),
    "S3": (VS11, TRANS_X, [
        (4222, 222, 323), (4224, 224, 323), (4225, 225, 326), (4227, 227, 326),
        (4242, 242, 343), (4244, 244, 343), (4245, 245, 346), (4247, 247, 346),
    ]),
    "S4": (VS11, TRANS_X, [
        (4322, 323, 422), (4324, 323, 424), (4325, 326, 425), (4327, 326, 427),
        (4342, 343, 442), (4344, 343, 444), (4345, 346, 445), (4347, 346, 447),
    ]),
    "S5": (VS12, TRANS_X, [
        (4422, 422, 523), (4424, 424, 523), (4425, 425, 526), (4427, 427, 526),
        (4442, 442, 543), (4444, 444, 543), (4445, 445, 546), (4447, 447, 546),
    ]),
    "S6": (VS12, TRANS_X, [
        (4522, 522, 623), (4524, 524, 623), (4525, 525, 626), (4527, 527, 626),
        (4542, 542, 643), (4544, 544, 643), (4545, 545, 646), (4547, 547, 646),
    ]),
    # Y-direction braces (exterior)
    "Y1": (VS10, TRANS_Y, [
        (5001, 1, 111), (5021, 21, 111), (5041, 41, 151), (5061, 61, 151),
        (5008, 8, 118), (5028, 28, 118), (5048, 48, 158), (5068, 68, 158),
    ]),
    "Y2": (VS10, TRANS_Y, [
        (5101, 111, 201), (5121, 111, 221), (5141, 151, 241), (5161, 151, 261),
        (5108, 118, 208), (5128, 118, 228), (5148, 158, 248), (5168, 158, 268),
    ]),
    "Y3": (VS11, TRANS_Y, [
        (5201, 201, 311), (5221, 221, 311), (5241, 241, 351), (5261, 261, 351),
        (5208, 208, 318), (5228, 228, 318), (5248, 248, 358), (5268, 268, 358),
    ]),
    "Y4": (VS11, TRANS_Y, [
        (5301, 311, 401), (5321, 311, 421), (5341, 351, 441), (5361, 351, 461),
        (5308, 318, 408), (5328, 318, 428), (5348, 358, 448), (5368, 358, 468),
    ]),
    "Y5": (VS12, TRANS_Y, [
        (5401, 401, 511), (5421, 421, 511), (5441, 441, 551), (5461, 461, 551),
        (5408, 408, 518), (5428, 428, 518), (5448, 448, 558), (5468, 468, 558),
    ]),
    "Y6": (VS12, TRANS_Y, [
        (5501, 501, 611), (5521, 521, 611), (5541, 541, 651), (5561, 561, 651),
        (5508, 508, 618), (5528, 528, 618), (5548, 548, 658), (5568, 568, 658),
    ]),
}

def _define_braces() -> None:
    for sec, tr, els in _BRACE_SPECS.values():
        for eid, n1, n2 in els:
            _e(eid, n1, n2, sec, tr)

# --- Struts -------------------------------------------------------------------
def _define_struts() -> None:
    for t, a, b in [(1011, 11, 111), (1018, 18, 118), (1023, 23, 123),
                     (1026, 26, 126), (1043, 43, 143), (1046, 46, 146),
                     (1051, 51, 151), (1058, 58, 158)]:
        ops.element("elasticBeamColumn", t, a, b, AC1, Es, Gs, 2 * IC1, IC1, IC1, TRANS_Y)

# --- PT strands ---------------------------------------------------------------
def _define_pt_strands() -> None:
    for t, a, b in [(6011, 1011, 611), (6018, 1018, 618), (6023, 1023, 623),
                     (6026, 1026, 626), (6043, 1043, 643), (6046, 1046, 646),
                     (6051, 1051, 651), (6058, 1058, 658)]:
        ops.element("truss", t, a, b, Strand_Area, MAT_STRAND_PAR)

# --- Base springs -------------------------------------------------------------
def _define_base_springs() -> None:
    for t, a, b in [(7001, 1001, 1), (7008, 1008, 8),
                     (7021, 1021, 21), (7022, 1022, 22), (7024, 1024, 24),
                     (7025, 1025, 25), (7027, 1027, 27), (7028, 1028, 28),
                     (7041, 1041, 41), (7042, 1042, 42), (7044, 1044, 44),
                     (7045, 1045, 45), (7047, 1047, 47), (7048, 1048, 48),
                     (7061, 1061, 61), (7068, 1068, 68)]:
        ops.element("twoNodeLink", t, a, b,
                    "-mat", MAT_BASE_SPRING, "-dir", 1,
                    "-orient", -1.0, 0.0, 0.0)

# --- Fuses --------------------------------------------------------------------
def _define_fuses() -> None:
    # Pin gap (SelfCentering, dir 3)
    for t, a, b in [(8011, 2011, 11), (8018, 2018, 18), (8023, 2023, 23),
                     (8026, 2026, 26), (8043, 2043, 43), (8046, 2046, 46),
                     (8051, 2051, 51), (8058, 2058, 58)]:
        ops.element("zeroLength", t, a, b, "-mat", MAT_FUSE_GAP, "-dir", 3)
    # Fuse steel (Steel01, dir 3)
    for t, a, b in [(9011, 1011, 2011), (9018, 1018, 2018), (9023, 1023, 2023),
                     (9026, 1026, 2026), (9043, 1043, 2043), (9046, 1046, 2046),
                     (9051, 1051, 2051), (9058, 1058, 2058)]:
        ops.element("zeroLength", t, a, b, "-mat", MAT_FUSE_STEEL, "-dir", 3)


def define_elements() -> None:
    _define_geom_transforms()
    _define_columns()
    _define_beams_x()
    _define_beams_y()
    _define_braces()
    _define_struts()
    _define_pt_strands()
    _define_base_springs()
    _define_fuses()


# ── 11. LOADING ──────────────────────────────────────────────────────────────
# All gravity-loaded nodes per floor
_GRAV_NODES = {
    1: [101, 102, 104, 105, 107, 108, 121, 122, 124, 125, 127, 128,
        131, 132, 134, 135, 137, 138, 141, 142, 144, 145, 147, 148,
        161, 162, 164, 165, 167, 168],
    2: [201, 202, 204, 205, 207, 208, 221, 222, 224, 225, 227, 228,
        231, 232, 234, 235, 237, 238, 241, 242, 244, 245, 247, 248,
        261, 262, 264, 265, 267, 268],
    3: [301, 302, 304, 305, 307, 308, 321, 322, 324, 325, 327, 328,
        331, 332, 334, 335, 337, 338, 341, 342, 344, 345, 347, 348,
        361, 362, 364, 365, 367, 368],
    4: [401, 402, 404, 405, 407, 408, 421, 422, 424, 425, 427, 428,
        431, 432, 434, 435, 437, 438, 441, 442, 444, 445, 447, 448,
        461, 462, 464, 465, 467, 468],
    5: [501, 502, 504, 505, 507, 508, 521, 522, 524, 525, 527, 528,
        531, 532, 534, 535, 537, 538, 541, 542, 544, 545, 547, 548,
        561, 562, 564, 565, 567, 568],
    6: [601, 602, 604, 605, 607, 608, 621, 622, 624, 625, 627, 628,
        631, 632, 634, 635, 637, 638, 641, 642, 644, 645, 647, 648,
        661, 662, 664, 665, 667, 668],
}


def define_nodal_masses() -> None:
    for nodes in _GRAV_NODES.values():
        for tag in nodes:
            ops.mass(tag, M_n, M_n, 0.0, 0.0, 0.0, 0.0)
    ops.constraints("Plain")


def define_gravity_loads() -> None:
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    f = -1.0 * M_n * g_accel
    for nodes in _GRAV_NODES.values():
        for tag in nodes:
            ops.load(tag, 0.0, 0.0, f, 0.0, 0.0, 0.0)

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def _run_eigen(n_modes: int = 3) -> list[float]:
    lam = ops.eigen("-genBandArpack", n_modes)
    periods = [2.0 * np.pi / np.sqrt(l) for l in lam]
    for i, t in enumerate(periods, 1):
        print(f"T{i} = {t:.3f} s")
    return periods


def _define_rayleigh_damping(w1: float, w3: float) -> None:
    aM = XDAMP * 2.0 * w1 * w3 / (w1 + w3)
    bK = 2.0 * XDAMP / (w1 + w3)
    ops.rayleigh(aM, 0.0, 0.0, bK)


def run_gravity(n_steps: int = 10,
                ctrl_node: int = 604, ctrl_dof: int = 3) -> None:
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.test('EnergyIncr', 1.0e-6, 100)
    ops.algorithm('Linear')
    ops.analysis("Static")
    for _ in range(n_steps):
        ops.analyze(1)
    ops.loadConst("-time", 0.0)
    print("Gravity Analysis Done.")


def run_dynamic(
    periods: list[float],
    gm_file: Path,
    max_run_time: float = 1800.0,
) -> None:
    """Run transient earthquake analysis using manual loop instead of SmartAnalyze."""
    w1 = 2.0 * np.pi / periods[0]
    w3 = 2.0 * np.pi / periods[2]
    _define_rayleigh_damping(w1, w3)

    ops.timeSeries("Path", 2, "-dt", GM_DT,
                   "-filePath", str(gm_file), "-factor", EQ_FACTOR * g_accel)
    ops.pattern("UniformExcitation", 2, 2, "-accel", 2)

    ops.wipeAnalysis()
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test('EnergyIncr', 1.0e-6, 100)
    ops.algorithm('Linear')
    ops.integrator("Newmark", 0.5, 0.25)
    ops.analysis('Transient')

    dt_anal = 0.5 * GM_DT            # half-step: 0.01 s, matches original

    for iAnal in range(GM_POINTS):
        ErrorState = ops.analyze(1, dt_anal)
        if ErrorState != 0:
            print('Error: The dynamic analysis failed!!')
            break

    print("Dynamic Analysis Done.")


def run_analysis(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    init_model()
    define_materials()
    define_nodes()
    define_boundary_conditions()

    define_elements()

    define_nodal_masses()
    define_gravity_loads()

    periods = _run_eigen(n_modes=3)
    with open(output_dir / "EigenPeriod.out", "w") as f:
        for t in periods:
            f.write(f"{t}\n")

    run_gravity(n_steps=10)

    gm_file = Path(__file__).parent / "kobe.txt"
    run_dynamic(periods=periods, gm_file=gm_file)

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    run_analysis(output_dir)
