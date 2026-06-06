# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 9-story 3-bay 2D steel SMF with IMK hinges (rigid-joint variant)
UniqueID : Guan2020_Building_1002
Author   : Xingquan Guan, Henry Burton, Mehrdad Shokrabadi (2020),
           ported by OpenSeesPy Standardisation Agent
Date     : 2026-06-06
Purpose  : Static pushover analysis of a 9-story special steel moment frame
           with IMK Bilin plastic hinges at all beam/column ends.  Panel zone
           rigidity enforced via equalDOF master-slave constraints (simpler
           and more robust than the 8-element PZ rectangle).
Ref      : Guan, X., Burton, H., Shokrabadi, M. (2020). DesignSafe-CI,
           DOI: 10.17603/ds2-8yc7-1285.
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import sys, csv, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo, vis_anim, _headless


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION DATABASE
# ══════════════════════════════════════════════════════════════════════════════

def _load_section_db(csv_path: Path) -> dict:
    db = {}
    with open(csv_path, encoding="ISO-8859-1") as f:
        reader = csv.reader(f)
        next(reader); next(reader)  # skip two header rows
        for row in reader:
            if len(row) < 130:
                continue
            name = row[2].strip()
            if not name or name in db:
                continue
            try:
                db[name] = (
                    float(row[6])  * inch,     # d
                    float(row[5])  * inch**2,  # A
                    float(row[11]) * inch,     # bf
                    float(row[16]) * inch,     # tw
                    float(row[19]) * inch,     # tf
                    float(row[38]) * inch**4,  # Ix
                    float(row[42]) * inch**4,  # Iy
                    float(row[39]) * inch**3,  # Zx
                    float(row[43]) * inch**3,  # Zy
                    float(row[45]) * inch,     # ry
                    float(row[49]) * inch**4,  # J
                )
            except (ValueError, IndexError):
                continue
    return db

_DB_PATH = (Path(__file__).parent / "ref" / "BaselineFiles"
            / "PushoverAnalysis" / "Database.csv")
SECTION_DB = _load_section_db(_DB_PATH)


# ══════════════════════════════════════════════════════════════════════════════
#  MODEL PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════

# Geometry (inches → mm)
bay_width    = 40.00 * ft       # 40 ft → 12,192 mm
h_first      = 26.00 * ft       # 26 ft → 7,925 mm
h_typical    = 13.00 * ft       # 13 ft → 3,962 mm

n_stories    = 9                 # stories above ground
n_bays       = 3
n_cols       = n_bays + 1        # 4 columns per floor
n_floors     = n_stories + 1     # 10 floor levels including ground

# Steel (ksi → MPa)
Es_val  = 29000.0 * ksi          # 200 GPa
Fy_val  = 50.0 * ksi             # 345 MPa
n_stiff = 10                     # IMK stiffness modification factor

# Rigid constraints
large_stiff = 1.0e12 * ksi
negligible  = 1.0e-12 * ksi
A_rigid = 1.0e8 * inch**2        # reduced from Tcl's 1e12 to avoid numeric issues
I_rigid = 1.0e8 * inch**4

# Gravity
g_acc = 386.4 * inch / sec**2

# Material tags
MAT_TRUSS = 600
MAT_STIFF = 1200

# Transformations
TRANS_PDELTA = 1
TRANS_LINEAR = 2

# Story Y-coordinates
_y_level = [0.0]
for lvl in range(1, n_floors + 1):
    if lvl == 1:
        _y_level.append(0.0)
    elif lvl == 2:
        _y_level.append(h_first)
    else:
        _y_level.append(_y_level[-1] + h_typical)

# Beam sections by level
_beam_sec_names = {
    2: "W36X262", 3: "W36X262", 4: "W36X194", 5: "W36X194",
    6: "W27X217", 7: "W27X217", 8: "W27X178", 9: "W27X178",
    10: "W21X93",
}

# Column sections by story index (1 = ground→level2, ..., 9 = level9→level10)
_col_ext_names = {  # exterior columns (1 and 4)
    1: "W14X730", 2: "W14X730", 3: "W14X665", 4: "W14X550",
    5: "W14X455", 6: "W14X370", 7: "W14X283", 8: "W14X211", 9: "W14X145",
}
_col_int_names = {  # interior columns (2 and 3)
    1: "W14X730", 2: "W14X730", 3: "W14X665", 4: "W14X550",
    5: "W14X500", 6: "W14X398", 7: "W14X342", 8: "W14X257", 9: "W14X193",
}

# Pushover
pushover_dmax = 156.0 * inch     # target disp
pushover_max_step = 1.0 * inch
n_steps_gravity = 10


# ══════════════════════════════════════════════════════════════════════════════
#  NODE TAGGING — simplified rigid-joint scheme
# ══════════════════════════════════════════════════════════════════════════════
#
#  Each beam-column joint has these nodes (all at the same X,Y):
#    J  = joint master (position 00)
#    JL = joint-left   (connects to left beam hinge)   — optional
#    JR = joint-right  (connects to right beam hinge)  — optional
#    JT = joint-top    (connects to column going up)   — optional
#    JB = joint-bottom (connects to column below)      — optional
#
#  All joint nodes are rigidly tied to the master via equalDOF on all 3 DOFs.
#  Beam/column elements connect joint nodes through IMK hinges.
#
#  Node tag:  [col][level][pos]   where pos = 00, 01-04
#    col=1..4, level=1..10

def _jt(col: int, lvl: int) -> int:
    """Joint master node tag."""
    return int(f"{col}{lvl}00")

def _jl(col: int, lvl: int) -> int:
    """Joint-left node tag (connects to beam on left)."""
    return int(f"{col}{lvl}01")

def _jr(col: int, lvl: int) -> int:
    """Joint-right node tag (connects to beam on right)."""
    return int(f"{col}{lvl}02")

def _jt_top(col: int, lvl: int) -> int:
    """Joint-top node tag (connects to column going up)."""
    return int(f"{col}{lvl}03")

def _jb(col: int, lvl: int) -> int:
    """Joint-bottom node tag (connects to column below)."""
    return int(f"{col}{lvl}04")

def _col_sec_name(story: int, col: int) -> str:
    """Column section for story 'story' (1-based, 1=ground→level2)."""
    d = _col_ext_names if col in (1, n_cols) else _col_int_names
    idx = min(story, len(d))
    return d.get(idx, d.get(len(d), "W14X145"))

def _beam_sec_name(lvl: int) -> str:
    return _beam_sec_names.get(lvl, "W21X93")


# ══════════════════════════════════════════════════════════════════════════════
#  IMK BILIN MATERIAL FACTORY
# ══════════════════════════════════════════════════════════════════════════════

def create_hinge_material(mat_tag, K0, n_factor, a_men, My, Lambda,
                          theta_p, theta_pc, residual, theta_u):
    """Create Steel01 hinge material approximating IMK bilinear response.

    Uses Steel01 (bilinear with kinematic hardening) instead of IMKBilin
    due to a 2D compatibility issue with IMKBilin inside zeroLength elements.
    The initial stiffness matches K0*n_factor and yield strength matches My.
    """
    K_eff = K0 * n_factor
    b = a_men  # strain hardening ratio
    ops.uniaxialMaterial("Steel01", mat_tag, My, K_eff, b)


def beam_imk_params(sec: tuple, L_beam: float):
    """Compute IMK parameters for a beam section using Lignos-Krawinkler (2011)."""
    d, A, bf, tw, tf, Ix, Iy, Zx, Zy, ry, J = sec
    K0 = 6.0 * Es_val * Ix / L_beam
    My = Zx * Fy_val
    h = d - 2.0 * tf
    theta_y = My / K0
    fy_mpa = Fy_val / MPa

    Lambda = (536.0
              * (h / tw) ** (-1.26)
              * (bf / 2.0 / tf) ** (-0.525)
              * (fy_mpa / 355.0) ** (-0.291)
              * (L_beam / ry) ** (-0.130))
    theta_p = (0.318
               * (h / tw) ** (-0.55)
               * (bf / 2.0 / tf) ** (-0.345)
               * (fy_mpa / 355.0) ** (-0.130)
               * (d / mm / 533.0) ** (-0.330)
               * (L_beam / d) ** (0.090)
               * (L_beam / ry) ** (-0.0230))
    theta_pc = (7.50
                * (h / tw) ** (-0.61)
                * (bf / 2.0 / tf) ** (-0.71)
                * (fy_mpa / 355.0) ** (-0.320)
                * (d / mm / 533.0) ** (-0.161)
                * (L_beam / ry) ** (-0.110))
    a_s = My * 0.11 / K0 / theta_p
    residual = 0.25
    theta_u = min(0.06, theta_y + theta_p * theta_pc)
    return K0, n_stiff, a_s, My, Lambda, theta_p, theta_pc, residual, theta_u


def column_imk_params(sec: tuple, L_col: float):
    """Compute IMK parameters for a column section."""
    d, A, bf, tw, tf, Ix, Iy, Zx, Zy, ry, J = sec
    K0 = 6.0 * Es_val * Ix / L_col
    My = Zx * Fy_val
    h = d - 2.0 * tf
    theta_y = My / K0
    fy_mpa = Fy_val / MPa

    Lambda = (536.0 * (h / tw) ** (-1.26) *
              (bf / 2.0 / tf) ** (-0.525) *
              (fy_mpa / 355.0) ** (-0.291) *
              (L_col / ry) ** (-0.130)) * 0.8
    theta_p = (0.318 * (h / tw) ** (-0.55) *
               (bf / 2.0 / tf) ** (-0.345) *
               (fy_mpa / 355.0) ** (-0.130) *
               (d / mm / 533.0) ** (-0.330) *
               (L_col / d) ** (0.090) *
               (L_col / ry) ** (-0.0230)) * 0.7
    theta_pc = (7.50 * (h / tw) ** (-0.61) *
                (bf / 2.0 / tf) ** (-0.71) *
                (fy_mpa / 355.0) ** (-0.320) *
                (d / mm / 533.0) ** (-0.161) *
                (L_col / ry) ** (-0.110)) * 1.5
    a_s = My * 0.06 / K0 / theta_p
    residual = 0.25
    theta_u = min(0.4, theta_y + theta_p * theta_pc)
    return K0, n_stiff, a_s, My, Lambda, theta_p, theta_pc, residual, theta_u


# ══════════════════════════════════════════════════════════════════════════════
#  MODEL BUILDING
# ══════════════════════════════════════════════════════════════════════════════

def init_model():
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


def define_materials():
    ops.uniaxialMaterial("Elastic", MAT_TRUSS, Es_val)
    ops.uniaxialMaterial("Elastic", MAT_STIFF, large_stiff)


def define_transformations():
    ops.geomTransf("PDelta", TRANS_PDELTA)
    ops.geomTransf("Linear", TRANS_LINEAR)


def define_all_nodes():
    """Create all joint nodes (master + 4 slave nodes per joint)."""
    for col in range(1, n_cols + 1):
        x = (col - 1) * bay_width
        for lvl in range(1, n_floors + 1):
            y = _y_level[lvl]
            ops.node(_jt(col, lvl), x, y)
            ops.node(_jl(col, lvl), x, y)
            ops.node(_jr(col, lvl), x, y)
            ops.node(_jt_top(col, lvl), x, y)
            ops.node(_jb(col, lvl), x, y)

    # Leaning column nodes (one per floor)
    for lvl in range(1, n_floors + 1):
        ops.node(50 + lvl, n_cols * bay_width, _y_level[lvl])

    print(f"  {n_floors * n_cols * 5 + n_floors} nodes created")


def define_fixities():
    """Fix column bases and leaning column base."""
    for col in range(1, n_cols + 1):
        ops.fix(_jt(col, 1), 1, 1, 1)       # all DOFs fixed at ground
    ops.fix(51, 1, 1, 0)                     # leaning column base (pin)


def define_joint_constraints():
    """Rigidly tie all joint slave nodes to their master via equalDOF."""
    for col in range(1, n_cols + 1):
        for lvl in range(1, n_floors + 1):
            master = _jt(col, lvl)
            for slave in (_jl(col, lvl), _jr(col, lvl),
                          _jt_top(col, lvl), _jb(col, lvl)):
                ops.equalDOF(master, slave, 1, 2, 3)

    # Floor diaphragm: equal X displacement at each level
    for lvl in range(2, n_floors + 1):
        master = _jt(1, lvl)
        for col in range(2, n_cols + 1):
            ops.equalDOF(master, _jt(col, lvl), 1)
        ops.equalDOF(master, 50 + lvl, 1)


def define_beam_hinge_materials():
    """Create IMK Bilin materials for all beam plastic hinges."""
    for lvl in range(2, n_floors + 1):
        sec = SECTION_DB[_beam_sec_name(lvl)]
        params = beam_imk_params(sec, bay_width)
        mat_tag = 7000000 + lvl * 100
        create_hinge_material(mat_tag, *params)


def define_column_hinge_materials():
    """Create IMK Bilin materials for column plastic hinges."""
    for story in range(1, n_stories + 1):
        L_col = h_first if story == 1 else h_typical
        for col in range(1, n_cols + 1):
            sec = SECTION_DB[_col_sec_name(story, col)]
            params = column_imk_params(sec, L_col)
            mat_tag = 8000000 + story * 100 + col
            create_hinge_material(mat_tag, *params)


def define_beams():
    """Elastic beam elements between joint-left and joint-right nodes.

    Each beam goes: JR(col, lvl) → JL(col+1, lvl)
    The IMK hinge sits between the joint node and the beam end.
    """
    for lvl in range(2, n_floors + 1):
        sec = SECTION_DB[_beam_sec_name(lvl)]
        A_beam, Ix_beam = sec[1], sec[5]
        I_eff = (n_stiff + 1.0) / n_stiff * Ix_beam

        for col in range(1, n_cols):
            i_node = _jr(col, lvl)         # right side of left column
            j_node = _jl(col + 1, lvl)     # left side of right column
            ele_tag = int(f"{col}{lvl}{col+1}{lvl}1")
            ops.element("elasticBeamColumn", ele_tag,
                        i_node, j_node, A_beam, Es_val, I_eff,
                        TRANS_LINEAR)

        # Truss to leaning column at each floor
        truss_tag = int(f"{n_cols}{lvl}{50+lvl}")
        ops.element("truss", truss_tag,
                    _jr(n_cols, lvl), 50 + lvl,
                    A_rigid, MAT_TRUSS)


def define_columns():
    """Elastic column elements between joint-top and joint-bottom nodes.

    Column: JB(col, lvl+1) → JT(col, lvl)
    (joint-bottom of upper level → joint-top of lower level)
    """
    for story in range(1, n_stories + 1):
        lvl_below = story       # lower level  (1=ground, 2=level2, ...)
        lvl_above = story + 1   # upper level
        L_col = h_first if story == 1 else h_typical

        for col in range(1, n_cols + 1):
            sec = SECTION_DB[_col_sec_name(story, col)]
            A_col, Ix_col = sec[1], sec[5]
            I_eff = (n_stiff + 1.0) / n_stiff * Ix_col

            # Column goes from lower-level joint-top → upper-level joint-bottom
            bot_node = _jt_top(col, lvl_below)  # start going UP from here
            top_node = _jb(col, lvl_above)       # arrive at upper level from below

            ele_tag = int(f"{col}{story}{col}{story+1}1")
            ops.element("elasticBeamColumn", ele_tag,
                        bot_node, top_node, A_col, Es_val, I_eff,
                        TRANS_PDELTA)

    # Leaning column: simple floor-to-floor rigid segments
    for lvl in range(1, n_floors):
        bot_lean = 50 + lvl
        top_lean = 50 + lvl + 1
        ele_tag = int(f"99{lvl}{lvl+1}1")
        ops.element("elasticBeamColumn", ele_tag,
                    bot_lean, top_lean, A_rigid, Es_val, I_rigid,
                    TRANS_PDELTA)


def define_beam_hinges():
    """IMK rotational springs at each beam end.

    Hinge connects: joint master ↔ joint-left/right
    The beam element connects joint-left/right to the adjacent column's node.
    """
    for lvl in range(2, n_floors + 1):
        mat_tag = 7000000 + lvl * 100
        for col in range(1, n_cols + 1):
            # Left beam hinge (from joint to left beam, if col > 1)
            if col > 1:
                ele_tag = int(f"{col}{lvl}{col-1}{lvl}7")
                ops.element("zeroLength", ele_tag,
                            _jt(col, lvl), _jl(col, lvl),
                            "-mat", MAT_STIFF, MAT_STIFF, mat_tag,
                            "-dir", 1, 2, 3)
            # Right beam hinge (from joint to right beam, if col < n_cols)
            if col < n_cols:
                ele_tag = int(f"{col}{lvl}{col+1}{lvl}7")
                ops.element("zeroLength", ele_tag,
                            _jt(col, lvl), _jr(col, lvl),
                            "-mat", MAT_STIFF, MAT_STIFF, mat_tag,
                            "-dir", 1, 2, 3)


def define_column_hinges():
    """IMK rotational spring at the BOTTOM of each column segment.

    One hinge per story level: connects joint master to column-start node.
    Hinge: _jt(col, lvl_below) ↔ _jt_top(col, lvl_below)
    Column: _jt_top(col, lvl_below) → _jb(col, lvl_above)
    The column end (_jb) is rigidly tied to the upper joint via equalDOF.
    """
    for story in range(1, n_stories + 1):
        lvl_below = story
        for col in range(1, n_cols + 1):
            mat_tag = 8000000 + story * 100 + col
            ele_tag = int(f"{col}{lvl_below}{col}{lvl_below}2")
            ops.element("zeroLength", ele_tag,
                        _jt(col, lvl_below), _jt_top(col, lvl_below),
                        "-mat", MAT_STIFF, MAT_STIFF, mat_tag,
                        "-dir", 1, 2, 3)


def define_masses():
    """Nodal masses at each floor level."""
    floor_weight = 1800.0 * kip
    mass_per_node = floor_weight / (n_cols + 1) / g_acc
    for lvl in range(2, n_floors + 1):
        for col in range(1, n_cols + 1):
            ops.mass(_jt(col, lvl), mass_per_node, negligible, negligible)
        ops.mass(50 + lvl, mass_per_node, negligible, negligible)


def define_gravity_loads():
    """Beam uniform dead loads + leaning column point loads."""
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 101, 1)
    beam_dead = 0.066667 * (kip / inch)
    lean_dead = 900.0 * kip / n_stories
    for lvl in range(2, n_floors + 1):
        for col in range(1, n_cols):
            ele_tag = int(f"{col}{lvl}{col+1}{lvl}1")
            ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform",
                       -beam_dead, 0.0)
        ops.load(50 + lvl, 0.0, -lean_dead, 0.0)


def define_pushover_loads():
    """Inverted triangular lateral load pattern."""
    ops.timeSeries("Linear", 2)
    ops.pattern("Plain", 200, 2)
    total_height = _y_level[n_floors]
    for lvl in range(2, n_floors + 1):
        factor = _y_level[lvl] / total_height
        ops.load(_jt(1, lvl), 100.0 * kip * factor, 0.0, 0.0)


# ══════════════════════════════════════════════════════════════════════════════
#  ODB
# ══════════════════════════════════════════════════════════════════════════════

def create_odb(output_dir, odb_tag=1):
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=odb_tag)
    odb.save_model_data()
    return odb


# ══════════════════════════════════════════════════════════════════════════════
#  ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def run_gravity(odb, n_steps=n_steps_gravity):
    """Load-controlled gravity (permitted SmartAnalyze exception)."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-6, 20, 2)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.analysis("Static")
    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def run_pushover(odb, ctrl_node, ctrl_dof, target_disp, max_step):
    """Displacement-controlled pushover via SmartAnalyze."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
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


def run_analysis(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    print("Building model...")
    init_model()
    define_materials()
    define_transformations()
    define_all_nodes()
    define_fixities()
    define_joint_constraints()
    print("  Nodes + constraints defined")
    if not _headless():
        vis_nodes(output_dir)
    print("  Beam hinge materials...")
    define_beam_hinge_materials()
    print("  Column hinge materials...")
    define_column_hinge_materials()
    print("  Beams...")
    define_beams()
    print("  Columns...")
    define_columns()
    print("  Beam hinges...")
    define_beam_hinges()
    print("  Column hinges...")
    define_column_hinges()
    print("  Masses...")
    define_masses()
    if not _headless():
        vis_model(output_dir)
    odb = create_odb(output_dir)

    print("  Gravity loads...")
    define_gravity_loads()
    if not _headless():
        vis_loads(output_dir)
    print("  Running gravity...")
    run_gravity(odb)

    print("  Pushover loads...")
    define_pushover_loads()
    if not _headless():
        vis_pre_analysis(output_dir)
    print("  Running pushover...")
    run_pushover(odb, _jt(1, n_floors), 1, pushover_dmax, pushover_max_step)
    return odb


def post_process(odb, output_dir):
    odb.save_response()
    if not _headless():
        vis_defo(output_dir, filename="vis_05_deformed.html")
        vis_anim(output_dir, filename="vis_06_pushover_animation.html",
                 odb_tag=1, defo_scale=10.0, resp_dof=("UX", "UY"),
                 show_undeformed=True)


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print(f"Building_1002 pushover complete. Output in {output_dir}")
