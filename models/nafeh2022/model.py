"""
Model    : 5-Storey Infilled RC Frame (Archetype 1, GLD)
UniqueID : nafeh2022
Author   : Al Mouayed Bellah Nafeh (IUSS Pavia, 2020), ported by OpenSeesPy Standardisation Agent
Date     : 2026-05-31
Purpose  : 3D nonlinear gravity + eigen analysis of a 5-storey infilled RC
           frame with masonry infill struts, representative of Italian
           pre-1970s construction.
Ref      : https://github.com/gerardjoreilly/Infilled-RC-Building-Database
           Nafeh, A. M. B. (2020). Infilled-RC-Building-Database. IUSS Pavia.
           O'Reilly, G. J., Sullivan, T. J. (2019) J. Earthquake Eng., 23(8), 1262–1296.
Units    : N, mm, MPa  (see standards/units.py)
"""

# ────────────────────────────────────────────────────────────────────────── #
# §1  Imports
# ────────────────────────────────────────────────────────────────────────── #

import math
import sys
from pathlib import Path

import openseespy.opensees as ops
import opstool as opst

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
g = g_accel   # shorthand for gravity acceleration (mm/s²)
from vis_utils import vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo

# Local helper modules (ported from OReilly2019 + new infill)
from joint_model import create_joint
from rc_bc_non_duct import create_rc_column
from infill import create_infill, INFILL_PROPS

# ────────────────────────────────────────────────────────────────────────── #
# §2  Tag Registry
# ────────────────────────────────────────────────────────────────────────── #
# Tags follow the Tcl convention with computed integer ranges.  Helper
# modules (joint_model, rc_bc_non_duct, infill) allocate material and
# section tags internally from their own offset bases.
#
#   Node ranges:
#     Base nodes:     1X10          (X = column 1..8, ri 1..4)
#     Joint master:   1XXY          (XX = col 1..8, Y = floor 1..5)
#     Joint slave:    6XXY          (constrained node for zeroLength)
#     Rigid diaphragm: 14(3)(fl)     (master = column 4, row 3)
#
#   Element ranges:
#     Geom transfs:   1, 2, 5, 6    (col C1, col C2, beam X, beam Y)
#     Beam X:         5XXY          (Tcl original)
#     Beam Y:         60000+XXY     (shifted to avoid material-tag collision)
#     Column:         80000+XXY     (shifted to avoid material-tag collision)
#     Joint springs:  9XXY          (zeroLength)
#     Infill:         2XXY          (truss pair: {tag}1, {tag}2)
#     Infill material: 8000+eleTag  (single/double/triple) or 9000+eleTag (truss)
#
#   Load tags:
#     Time series:    1
#     Load pattern:   101
#
#   rc_bc_non_duct material tags (per element, ST=0):  101000..119000+ET
#   joint_model material tags (per joint):              1..6 * 1000 + index

# ────────────────────────────────────────────────────────────────────────── #
# §3  Parameters
# ────────────────────────────────────────────────────────────────────────── #
# Ported from arch_1_inputParam_GLD.tcl.  Original Tcl uses kN-m units;
# all values below have been converted to N-mm-MPa.

# ── Unit aliases ─────────────────────────────────────────────────────────
mm_ = mm     # 1.0
m_  = m      # 1000.0
MPa_ = MPa   # 1.0

# ── Story count ──────────────────────────────────────────────────────────
N_STORIES = 5

# ── Section dimensions ───────────────────────────────────────────────────
hc1 = 300.0 * mm_;   bc1 = 300.0 * mm_   # Column #1 (300×300)
hc2 = 200.0 * mm_;   bc2 = 200.0 * mm_   # Column #2 (200×200)
hb1 = 500.0 * mm_;   bb1 = 300.0 * mm_   # Beam (500×300)

sb = 200.0 * mm_     # Beam stirrup spacing
sc = 150.0 * mm_     # Column stirrup spacing
cv = 20.0 * mm_      # Cover

H_STORY = 3.00 * m_  # Floor height

# Bar diameters
dbL1 = 12.0 * mm_;   dbL2 = 14.0 * mm_
dbL3 = 16.0 * mm_;   dbL4 = 20.0 * mm_
dbV  = 6.0  * mm_

# ── Material properties ──────────────────────────────────────────────────
fcb1  = 15.0  * MPa_
Ecb1  = 3320.0 * math.sqrt(fcb1) + 6900.0  # ≈ 19760 MPa
fcc1  = 15.0  * MPa_
Ecc1  = 3320.0 * math.sqrt(fcc1) + 6900.0
fyL   = 280.0 * MPa_
fuL   = 290.0 * MPa_
fyV   = 280.0 * MPa_
fuV   = 290.0 * MPa_
Es    = 200e3 * MPa_

# ── Reinforcement ratios ─────────────────────────────────────────────────
# Columns
rC1_top, rC1_web, rC1_bot, rC1_shr = 0.004470, 0.0, 0.004470, 0.00093  # 300×300
rC2_top, rC2_web, rC2_bot, rC2_shr = 0.004925, 0.0, 0.004925, 0.00093  # 200×200
# Beams (external / internal)
rB1_top, rB1_web, rB1_bot, rB1_shr = 0.00308, 0.0, 0.00205, 0.00109
rB2_top, rB2_web, rB2_bot, rB2_shr = 0.00308, 0.0, 0.00308, 0.00109

# ── Joint properties ─────────────────────────────────────────────────────
k_cr_int, k_pk_int, k_ult_int = 0.29, 0.42, 0.42
k_cr_ext, k_pk_ext, k_ult_ext = 0.132, 0.132, 0.053
gamm_cr, gamm_pk, gamm_ult = 0.0002, 0.0132, 0.020

ptc_int  = [k_cr_int, k_pk_int, k_ult_int, k_cr_int, k_pk_int, k_ult_int]
ptc_ext  = [k_cr_ext, k_pk_ext, k_ult_ext, k_cr_ext, k_pk_ext, k_ult_ext]
gamm_ext = [gamm_cr, gamm_pk, gamm_ult, gamm_cr, gamm_pk, gamm_ult]
gamm_int = [gamm_cr, gamm_pk, gamm_ult, gamm_cr, gamm_pk, gamm_ult]
hyst_ext = [0.6, 0.2, 0.0, 0.0, 0.3]
hyst_int = [0.6, 0.2, 0.0, 0.010, 0.3]
hyst_rof = [0.6, 0.2, 0.0, 0.0, 0.3]

# ── Concrete and reinforcement lists ─────────────────────────────────────
c_c1 = [fcc1, Ecc1, cv]
brs1 = [dbL1, dbV]
brs2 = [dbL2, dbV]
brs3 = [dbL3, dbV]
col1 = [hc1, bc1]
col2 = [hc2, bc2]
bm1  = [hb1, hb1, bb1, bb1]

# ── Grid bay widths ──────────────────────────────────────────────────────
BX1 = 3.50 * m_;    BX2 = 5.50 * m_;    BX3 = 8.65 * m_
BX4 = 11.35 * m_;   BX5 = 14.50 * m_;   BX6 = 16.50 * m_
BX7 = 20.00 * m_

BY1 = 3.0 * m_;     BY2 = 5.0 * m_;     BY3 = 9.0 * m_

# Grid line X coordinates (centreline)
BX = [0.0, BX1, BX2, BX3, BX4, BX5, BX6, BX7]
# Grid line Y coordinates
BY = [0.0, BY1, BY2, BY3]

# ── Floor loading ─────────────────────────────────────────────────────────
FloorL = 12.0e-3  * MPa_    # 12 kPa → N/mm²
RoofL  = 11.5e-3  * MPa_    # 11.5 kPa

# ── Column masses per floor ───────────────────────────────────────────────
total_area = BX7 * BY3  # mm²
FloorL_totalN = FloorL * total_area  # N
RoofL_totalN  = RoofL  * total_area  # N

mass_frac_1 = 0.0875; mass_frac_2 = 0.1375
mass_frac_3 = 0.12875; mass_frac_4 = 0.14625

tribs = [0.167, 0.277, 0.333, 0.222]  # per Y-row
mfracs = [mass_frac_1, mass_frac_2, mass_frac_3, mass_frac_4,
          mass_frac_4, mass_frac_3, mass_frac_2, mass_frac_1]  # per X-col

def _mass(frac, trib, loadN):
    return frac * trib * loadN / g   # N / (mm/s²) = tonne

# Floor masses [row][col] in tonnes
M_floor = {}
M_roof = {}
for ri, trib in enumerate(tribs, 1):    # 1..4
    for ci, frac in enumerate(mfracs, 1):  # 1..8
        key = f"{ci}{ri}"
        M_floor[key] = _mass(frac, trib, FloorL_totalN)
        M_roof[key]  = _mass(frac, trib, RoofL_totalN)

# Total floor mass for PDelta
massT  = FloorL_totalN / g   # tonne
massTr = RoofL_totalN  / g   # tonne
bdg_w  = (massTr + (N_STORIES - 1) * massT) * g  # N

# ── Model options ────────────────────────────────────────────────────────
STb         = 0     # No beam shear hinge
STc         = 0     # No column shear hinge
stairsOPT   = 0     # No stairs
infillsOPT  = 1     # Add infills
pilotisOPT  = 0     # Don't remove ground floor infills

INFILL_POISSON = 0.2  # Masonry Poisson ratio (Hak et al. 2012)

# Infill bay definitions: (row, col_start, col_end, prop_set)
INFILL_DEFS = [
    # Y=1 (row 1): all bays infilled with medium
    (1, 1, 2, "medium"), (1, 2, 3, "medium"), (1, 3, 4, "medium"),
    (1, 4, 5, "medium"), (1, 5, 6, "medium"), (1, 6, 7, "medium"),
    (1, 7, 8, "medium"),
    # Y=2 (row 2): only outer bays infilled with weak
    (2, 2, 3, "weak"), (2, 6, 7, "weak"),
    # Y=3 (row 3): only outer bays infilled with weak
    (3, 2, 3, "weak"), (3, 6, 7, "weak"),
    # Y=4 (row 4): all bays infilled with medium
    (4, 1, 2, "medium"), (4, 2, 3, "medium"), (4, 3, 4, "medium"),
    (4, 4, 5, "medium"), (4, 5, 6, "medium"), (4, 6, 7, "medium"),
    (4, 7, 8, "medium"),
]

# ── Analysis parameters ──────────────────────────────────────────────────
GRAVITY_STEPS     = 100
GRAVITY_TOL       = 1.0e-6
GRAVITY_MAX_ITER  = 500
NUM_EIGEN_MODES   = N_STORIES


def _col_type(ci: int) -> bool:
    """True = C1 (300×300), False = C2 (200×200)."""
    return ci in (1, 2, 7, 8)


def _beam_type(ri: int) -> str:
    """rB1 for Y=1,4 (external); rB2 for Y=2,3 (internal)."""
    return "ext" if ri in (1, 4) else "int"


# ────────────────────────────────────────────────────────────────────────── #
# §4  Model Initialisation
# ────────────────────────────────────────────────────────────────────────── #

def init_model() -> None:
    """Wipe any existing model and create a new 3D-6DOF domain."""
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)


# ────────────────────────────────────────────────────────────────────────── #
# §5  Materials  (created inside joint / rc_bc_non_duct / infill helpers)
# ────────────────────────────────────────────────────────────────────────── #

# ────────────────────────────────────────────────────────────────────────── #
# §6  Sections   (created inside rc_bc_non_duct)
# ────────────────────────────────────────────────────────────────────────── #

# ────────────────────────────────────────────────────────────────────────── #
# §7  Geometry — Nodes, BCs, Elements
# ────────────────────────────────────────────────────────────────────────── #

def define_geometry(output_dir: Path) -> dict:
    """Build nodes, boundary conditions, geometric transforms, and elements.

    Returns:
        base_nodes: dict mapping (ci, ri) → base node tag, used by infills
            and columns connecting to ground.
    """
    # ── 7a. Base nodes (Z=0) — 8 columns × 4 rows ────────────────────────
    base_nodes = {}
    n_cols, n_rows = 8, 4
    for ri in range(1, n_rows + 1):
        for ci in range(1, n_cols + 1):
            tag = 1000 * ci + 100 * ri + 10
            x = BX[ci - 1]
            y = BY[ri - 1]
            ops.node(tag, x, y, 0.0,
                     "-mass", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            base_nodes[(ci, ri)] = tag

    # ── 7b. Boundary conditions ─────────────────────────────────────────
    for ri in range(1, n_rows + 1):
        for ci in range(1, n_cols + 1):
            ops.fix(base_nodes[(ci, ri)], 1, 1, 1, 1, 1, 1)

    # ── 7c. Geometric transformations ───────────────────────────────────
    ops.geomTransf("PDelta", 1, 0, 1, 0,
                   "-jntOffset", 0.0, 0.0, hc1 / 2.0, 0.0, 0.0, -hc1 / 2.0)
    ops.geomTransf("PDelta", 2, 0, 1, 0,
                   "-jntOffset", 0.0, 0.0, hc2 / 2.0, 0.0, 0.0, -hc2 / 2.0)
    ops.geomTransf("PDelta", 5, 0, 1, 0,
                   "-jntOffset", hb1 / 2.0, 0.0, 0.0, -hb1 / 2.0, 0.0, 0.0)
    ops.geomTransf("PDelta", 6, -1, 0, 0,
                   "-jntOffset", 0.0, hb1 / 2.0, 0.0, 0.0, -hb1 / 2.0, 0.0)
    GTc1, GTc2 = 1, 2
    GTbX1, GTbY1 = 5, 6

    # ── 7d. Element construction ────────────────────────────────────────
    # Build without stairs (stairsOPT = 0)

    pfile_jnts = open(output_dir / "Properties_joints.txt", "w")
    pfile_bms  = open(output_dir / "Properties_beams.txt", "w")
    pfile_cols = open(output_dir / "Properties_columns.txt", "w")

    # ── 7d-i. Joints ─────────────────────────────────────────────────
    for fl in range(1, N_STORIES + 1):
        floors_above = N_STORIES - fl
        for ri in range(1, n_rows + 1):
            for ci in range(1, n_cols + 1):
                key = f"{ci}{ri}"
                m = M_roof[key] if fl == N_STORIES else M_floor[key]
                P_val = (floors_above * M_floor[key] + M_roof[key]) * g

                is_interior = (ci > 1 and ci < n_cols) and (ri > 1 and ri < n_rows)
                if is_interior:
                    jtype = "Interior"
                    ptc, gamm, hyst = ptc_int, gamm_int, hyst_int
                else:
                    jtype = "Exterior"
                    ptc, gamm, hyst = ptc_ext, gamm_ext, hyst_ext

                if fl <= 2:
                    col = col1; bars = brs3
                else:
                    col = col2; bars = brs2

                index = 100 * ci + 10 * ri + fl
                x = BX[ci - 1]
                y = BY[ri - 1]
                z = fl * H_STORY

                create_joint(jtype, index, (x, y, z), m, col, bm1,
                             c_c1, bars, P_val, H_STORY, ptc, gamm, hyst,
                             pfile_jnts)

    print("Joints created...")

    # ── 7d-ii. Beams — X-direction ────────────────────────────────────
    for fl in range(1, N_STORIES + 1):
        for ri in range(1, n_rows + 1):
            beam_type = _beam_type(ri)
            if beam_type == "ext":
                rb_top, rb_web, rb_bot, rb_shr = rB1_top, rB1_web, rB1_bot, rB1_shr
            else:
                rb_top, rb_web, rb_bot, rb_shr = rB2_top, rB2_web, rB2_bot, rB2_shr

            for ci in range(1, n_cols):
                ET = int(f"5{ci}{ri}{fl}")
                iNode = int(f"6{ci}{ri}{fl}")
                jNode = int(f"6{ci+1}{ri}{fl}")
                Ls = BX[ci] - BX[ci - 1]

                create_rc_column(
                    STb, ET, GTbX1, iNode, jNode,
                    fyL, fyV, Es, fcb1, Ecb1,
                    bb1, hb1, sb, cv, dbL2, dbV,
                    0.0, Ls,
                    rb_shr,
                    rb_top, rb_web, rb_bot,
                    rb_top, rb_web, rb_bot,
                    rb_top, rb_web, rb_bot,
                    rb_top, rb_web, rb_bot,
                    pfile_bms,
                )

    # ── 7d-iii. Beams — Y-direction ───────────────────────────────────
    for fl in range(1, N_STORIES + 1):
        for ci in (1, n_cols):
            for ri in range(1, n_rows):
                ET = 60000 + 100 * ci + 10 * ri + fl
                iNode = int(f"6{ci}{ri}{fl}")
                jNode = int(f"6{ci}{ri+1}{fl}")
                Ls = BY[ri] - BY[ri - 1]

                create_rc_column(
                    STb, ET, GTbY1, iNode, jNode,
                    fyL, fyV, Es, fcb1, Ecb1,
                    bb1, hb1, sb, cv, dbL2, dbV,
                    0.0, Ls,
                    rB1_shr,
                    rB1_top, rB1_web, rB1_bot,
                    rB1_top, rB1_web, rB1_bot,
                    rB1_top, rB1_web, rB1_bot,
                    rB1_top, rB1_web, rB1_bot,
                    pfile_bms,
                )

    print("Beams created...")

    # ── 7d-iv. Columns ────────────────────────────────────────────────
    for fl in range(1, N_STORIES + 1):
        floors_above = N_STORIES - fl
        for ri in range(1, n_rows + 1):
            for ci in range(1, n_cols + 1):
                key = f"{ci}{ri}"
                P_val = (floors_above * M_floor[key] + M_roof[key]) * g

                base_node = base_nodes[(ci, ri)]
                joint_node = int(f"1{ci}{ri}{fl}")
                ET = 80000 + 100 * ci + 10 * ri + fl

                if _col_type(ci):
                    col = col1; GTc = GTc1
                    rc_top, rc_bot, rc_shr = rC1_top, rC1_bot, rC1_shr
                else:
                    col = col2; GTc = GTc2
                    rc_top, rc_bot, rc_shr = rC2_top, rC2_bot, rC2_shr

                hc_col, bc_col = col

                create_rc_column(
                    STc, ET, GTc, base_node, joint_node,
                    fyL, fyV, Es, fcc1, Ecc1,
                    bc_col, hc_col, sc, cv, dbL3, dbV,
                    P_val, H_STORY / 2.0,
                    rc_shr,
                    rc_top, 0.0, rc_bot,
                    rc_top, 0.0, rc_bot,
                    rc_top, 0.0, rc_bot,
                    rc_top, 0.0, rc_bot,
                    pfile_cols,
                )

    print("Columns created...")

    # ── 7d-v. Infills ─────────────────────────────────────────────────
    if infillsOPT and not pilotisOPT:
        for fl in range(1, N_STORIES + 1):
            if fl <= 2:
                hc_col, bc_col = hc1, bc1
            else:
                hc_col, bc_col = hc2, bc2

            for _ri, ci_start, ci_end, prop_name in INFILL_DEFS:
                ri = _ri
                for ci in range(ci_start, ci_end):
                    props = INFILL_PROPS[prop_name]

                    nTL = int(f"1{ci}{ri}{fl}")
                    nTR = int(f"1{ci+1}{ri}{fl}")
                    if fl > 1:
                        nBL = int(f"1{ci}{ri}{fl-1}")
                        nBR = int(f"1{ci+1}{ri}{fl-1}")
                    else:
                        nBL = base_nodes[(ci, ri)]
                        nBR = base_nodes[(ci+1, ri)]

                    nds = [nTL, nTR, nBR, nBL]
                    B_bay = BX[ci] - BX[ci - 1]
                    ele_tag = int(f"2{ci}{ri}{fl}")

                    create_infill(
                        ele_tag, "single", nds,
                        B_bay, H_STORY,
                        hb1, hc_col, bc_col,
                        props["tw"],
                        Ecc1,
                        props["Ewh"], props["Ewv"], props["Gw"],
                        INFILL_POISSON,
                        props["fwv"], props["fwu"], props["fws"],
                        sig_v=0.0,
                    )

        print("Infills created...")

    pfile_jnts.close()
    pfile_bms.close()
    pfile_cols.close()

    # ── 7e. Rigid diaphragms ──────────────────────────────────────────
    for fl in range(1, N_STORIES + 1):
        master_tag = int(f"14{3}{fl}")
        slaves = []
        for ri in range(1, n_rows + 1):
            for ci in range(1, n_cols):  # exclude column 8
                tag = int(f"1{ci}{ri}{fl}")
                if tag != master_tag:
                    slaves.append(tag)
        ops.rigidDiaphragm(3, master_tag, *slaves)

    return base_nodes


# ────────────────────────────────────────────────────────────────────────── #
# §8  Loading
# ────────────────────────────────────────────────────────────────────────── #

def define_loads() -> None:
    """Apply gravity loads as nodal forces on all joint nodes."""
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 101, 1)

    for fl in range(1, N_STORIES + 1):
        for ri in range(1, 5):
            for ci in range(1, 9):
                key = f"{ci}{ri}"
                m = M_roof[key] if fl == N_STORIES else M_floor[key]
                node_tag = int(f"1{ci}{ri}{fl}")
                ops.load(node_tag, 0.0, 0.0, -m * g, 0.0, 0.0, 0.0)


# ────────────────────────────────────────────────────────────────────────── #
# §9  ODB Recorder
# ────────────────────────────────────────────────────────────────────────── #

def create_odb() -> "opst.post.CreateODB":
    """Initialise opstool ODB and snapshot model geometry."""
    odb = opst.post.CreateODB(odb_tag=1)
    odb.save_model_data()
    return odb


# ────────────────────────────────────────────────────────────────────────── #
# §10  Analysis
# ────────────────────────────────────────────────────────────────────────── #

def run_gravity(odb: "opst.post.CreateODB") -> int:
    """Load-controlled gravity analysis (manual LoadControl loop).

    Per AGENT.md §3c exception: SmartAnalyze Static forces DisplacementControl
    internally, so load-controlled gravity requires manual ops.analyze().

    Returns:
        Number of converged gravity steps.
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", GRAVITY_TOL, GRAVITY_MAX_ITER)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / GRAVITY_STEPS)
    ops.analysis("Static")

    ok = 0
    for i in range(GRAVITY_STEPS):
        ok = ops.analyze(1)
        if ok < 0:
            print(f"Gravity step {i} failed: {ok}")
            break
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()

    print(f"Gravity analysis completed (steps: {i + 1})")
    return i + 1


def run_eigen(odb: "opst.post.CreateODB") -> tuple:
    """Eigenvalue analysis — compute periods and mode shapes.

    Returns:
        (periods, eigenvalues) — each a list of length NUM_EIGEN_MODES.
    """
    eigenvalues = ops.eigen(NUM_EIGEN_MODES)

    periods = []
    for val in eigenvalues:
        if val > 1e-12:
            T = 2.0 * math.pi / math.sqrt(val)
            periods.append(T)
        else:
            periods.append(float('inf'))

    print("\nEigenvalue Analysis Results:")
    print(f"{'Mode':<8} {'Period (s)':<15} {'Frequency (Hz)':<15} {'Eigenvalue':<15}")
    print("-" * 55)
    for i, (val, T) in enumerate(zip(eigenvalues, periods)):
        freq = 1.0 / T if T > 0 and T < float('inf') else 0.0
        print(f"{i + 1:<8} {T:<15.4f} {freq:<15.4f} {val:<15.4f}")

    return periods, eigenvalues


# ────────────────────────────────────────────────────────────────────────── #
# §11  Post-Processing
# ────────────────────────────────────────────────────────────────────────── #

def post_process(odb: "opst.post.CreateODB") -> None:
    """Flush response data to disk and save eigen results."""
    odb.save_response()
    odb.save_eigen_data(mode_tag=1, solver="-genBandArpack")


# ────────────────────────────────────────────────────────────────────────── #
# §12  Visualization
# ────────────────────────────────────────────────────────────────────────── #

def run_visualization(output_dir: Path) -> None:
    """Generate four opstool visualization checkpoints (V1–V4)."""
    vis_nodes(output_dir)
    vis_model(output_dir)
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)


# ────────────────────────────────────────────────────────────────────────── #
# §13  Main
# ────────────────────────────────────────────────────────────────────────── #

def run_analysis(output_dir: Path):
    """Build model, run gravity + eigen, and return ODB instance.

    Args:
        output_dir: Directory for HDF5 data, property files, and HTML vis.

    Returns:
        (odb, periods, eigenvalues)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_geometry(output_dir)
    define_loads()

    # ── ODB initialisation (after model built) ───────────────────────────
    odb = create_odb()

    # ── Visualisation checkpoints (V1–V4) ───────────────────────────────
    run_visualization(output_dir)

    # ── Analysis ────────────────────────────────────────────────────────
    n_grav_steps = run_gravity(odb)
    periods, eigenvalues = run_eigen(odb)

    # ── Post-processing ─────────────────────────────────────────────────
    post_process(odb)

    # ── Deformed shape (V5) ─────────────────────────────────────────────
    vis_defo(output_dir)

    return odb, periods, eigenvalues


if __name__ == "__main__":
    import time
    t0 = time.time()

    output_dir = Path(__file__).parent / "output"

    print("Building model: nafeh2022 — 5-storey infilled RC frame (Archetype 1, GLD)")
    print("Units: N · mm · MPa · tonne · s")
    print(f"Output directory: {output_dir}")

    odb, periods, eigenvalues = run_analysis(output_dir)

    elapsed = time.time() - t0
    print(f"\nTotal runtime: {elapsed:.1f} s")
