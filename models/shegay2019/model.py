# ──0. FILE HEADER ============================================================
"""
Model    : 8-Story RC Core Wall Building -- Dynamic Time History
UniqueID : shegay2019
Author   : Converted from Shegay (2019) Tcl model (NZ.tcl)
Date     : 2026-06-14
Purpose  : Nonlinear dynamic time-history analysis of an 8-story RC core wall
           under ground motion WELL1p0_1_10_1, with fiber-section dispBeamColumn
           elements and PDelta leaning column.
Ref      : Shegay et al. (2019) -- RC core wall seismic performance
Units    : N, mm, MPa  (see standards/units.py)
"""

# ──1. IMPORTS ================================================================
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ──2. TAG REGISTRY ===========================================================
# Tcl uses a 3-range scheme for sequential tags to avoid colliding with reserved
# ranges (e.g. 300xxx, 400xxx).  Helper below replicates that scheme exactly.

def _tag3(prefix: int, idx: int, group_offset: int = 0) -> int:
    """Tcl 3-range tag: prefix + (group_offset+idx)*10000 + 1, with digit shift
    when the group number crosses 9 or 99 to keep tags non-colliding."""
    group = group_offset + idx
    if group < 10:
        return prefix * 100_000 + group * 10_000 + 1
    elif group < 100:
        return prefix * 1_000_000 + group * 10_000 + 1
    else:
        return prefix * 10_000_000 + group * 10_000 + 1

# Geometric transformation
TRANS_PDELTA = 1

# Material tags
MAT_RIGID           = 400001   # super-stiff elastic (zeroLength non-rot DOFs)
MAT_PDELTA_ELASTIC  = 400002   # elastic for PDelta columns
MAT_TRUSS_RIGID     = 1113601  # rigid diaphragm truss elastic

# Wall material groups (15 materials each, 160 groups = 1 per element)
# Element e uses group g=e: MAT_GROUP_BASE + g*15 + 0..14
MAT_GROUP_BASE      = 110001

# Section tags (1 aggregator per element, wraps 1 fiber section)
SEC_BASE            = 300001

# Beam integration tags (1 per element, Lobatto with N_INTEG IPs)
INTEG_BASE          = 600001

# Element bases (tags generated via _tag3 matching Tcl scheme)
ELE_BEAM_PREFIX     = 5
ELE_ZL_PREFIX       = 9
MAT_SPRING_PREFIX   = 2

# elasticBeamColumn PDelta + truss + reaction (outside _tag3 range)
ELE_PDELTA_BASE     = 910002
ELE_TRUSS_BASE      = 910005
ELE_REACT_LEFT      = 910003
ELE_REACT_RIGHT     = 910004

# Load patterns
PATTERN_GRAVITY     = 100
PATTERN_DYNAMIC     = 400
TS_DYNAMIC          = 1
TS_GRAVITY          = 999

# ODB
ODB_TAG             = 1
ODB_EVERY_N         = 10     # throttle fetch_response_step for transient (>500 steps)

# Counts
N_STORIES           = 8
N_ELE_PER_STORY     = 20    # 19 wall segments + 1 floor transition
N_WALL_NODES        = 19    # wall edge nodes per story
N_ELEMENTS          = 160   # total dispBeamColumn
N_SPRINGS           = 160   # total rotational zeroLength springs
N_INTEG             = 5     # Lobatto integration points per element
N_MODES             = 7
N_MAT_GROUPS        = 160   # one material group per element

# ──3. PARAMETERS =============================================================
# --- Building geometry ---
H_GROUND   = 4000.0           # mm (ground story height, was 157.48 in)
H_TYPICAL  = 3600.0           # mm (typical story height, was 141.73 in)
W_BUILDING = 400.0 * inch     # mm (10,160 mm)
DZ         = 200.0            # mm (vertical wall discretization, was 7.874 in)

# Wall cross-section (mm, converted from inches)
W_WALL     = 275.59055 * inch  # 7000 mm overall width
T_WALL     = 19.68504 * inch   # 500 mm overall thickness
# Confined boundary zone dimensions
W_CONF     = 41.33858 * inch   # ~1050 mm (width of each boundary zone)
D_CONF     = 13.68504 * inch   # ~347.6 mm (depth of confined zone)
# Cover thickness
T_COVER    = 3.0 * inch        # ~76.2 mm

# --- Concrete: unconfined (fc=-5.80 ksi) ---
FC_UC      = -5.801558 * ksi   # MPa
EPSC0_UC   = -0.002673
FCU_UC     = -0.058016 * ksi   # MPa
EPSCU_UC   = -0.016475
FT_RATIO   = 0.100000
FT_UC      = 0.304672 * ksi    # MPa (tension strength)
ETS_UC     = 217.078678 * ksi  # MPa (tension softening stiffness)

# --- Concrete: confined (fc=-8.13 ksi) ---
FC_C       = -8.132419 * ksi   # MPa
EPSC0_C    = -0.008041
FCU_C      = -1.626484 * ksi   # MPa
EPSCU_C    = -0.028152

# --- Steel: Steel02 + MinMax ---
FY         = 84.825 * ksi      # MPa (yield strength)
E_STEEL    = 29000.0 * ksi     # MPa (elastic modulus)
B_MAIN     = 0.006             # strain-hardening ratio (main bars)
B_SPALL    = 0.00784           # strain-hardening ratio (spalling bars)
R0         = 20.0
CR1        = 0.925
CR2        = 0.15
MINMAX_MIN_MAIN  = -0.028152  # MinMax min (confined epscu)
MINMAX_MIN_SPALL = -0.016475  # MinMax min (unconfined epscu)
MINMAX_MAX       = 0.203153   # MinMax max

# --- Steel bar areas (in^2 -> mm^2) ---
A_MAIN_BAR = 0.760856 * inch**2   # 490.9 mm^2 (~25 mm dia bar)
A_WEB_BAR  = 0.486948 * inch**2   # 314.2 mm^2 (~20 mm dia bar)

# --- Shear spring (G in MPa) ---
G_SHEAR    = 853372.597834 * psi

# --- Rotational spring stiffness ---
K_SPRING_S1  = 108378.319925 * kip * inch   # N.mm/rad (story 1)
K_SPRING_S28 = 120420.355472 * kip * inch   # N.mm/rad (stories 2-8)

# --- PDelta leaning column ---
A_PDELTA       = 806400.0 * inch**2      # mm^2
E_PDELTA       = 1732.554420 * ksi       # MPa (matches Tcl)
I_PDELTA       = 0.276480 * inch**4      # mm^4 (matches Tcl)

# --- Rigid diaphragm truss ---
A_TRUSS        = 100000000.0 * inch**2   # mm^2 (matches Tcl 1e8 in^2)
E_TRUSS        = 100000000.0 * ksi       # MPa (matches Tcl 1e8 ksi)

# --- Nodal masses (kip.s^2/in -> consistent N-mm-s mass units) ---
MASS_FLOOR_1_7 = 2.059222 * kip / inch  # floors 1-7
MASS_ROOF      = 1.388570 * kip / inch  # roof (lighter)

# --- Rayleigh damping ---
ZETA       = 0.02              # 2% damping
DAMP_MODE_I = 1
DAMP_MODE_J = 3

# --- Dynamic analysis ---
DT_GM      = 0.005             # sec
N_STEPS_GM = 8000              # 40 sec duration
SCALE_GM   = inch              # convert in/s^2 to mm/s^2

# ──4. INIT MODEL ============================================================
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ──5. DEFINE MATERIALS ======================================================
def _define_wall_material_group(g: int) -> None:
    """Define 15 materials for integration-point group g (0-indexed, 0..799).
    Tags: MAT_GROUP_BASE + g*15 + offset (offset 0..14).
    """
    b = MAT_GROUP_BASE + g * 15

    # +0: Unconfined Concrete02
    ops.uniaxialMaterial("Concrete02", b + 0, FC_UC, EPSC0_UC, FCU_UC, EPSCU_UC,
                         FT_RATIO, FT_UC, ETS_UC)
    # +1: Soft elastic tension stub
    ops.uniaxialMaterial("Elastic", b + 1, 0.01)
    # +2: Parallel (unconfined + tension)
    ops.uniaxialMaterial("Parallel", b + 2, b + 0, b + 1)

    # +3: Confined Concrete02
    ops.uniaxialMaterial("Concrete02", b + 3, FC_C, EPSC0_C, FCU_C, EPSCU_C,
                         FT_RATIO, FT_UC, ETS_UC)
    # +4: Soft elastic tension stub
    ops.uniaxialMaterial("Elastic", b + 4, 0.01)
    # +5: Parallel (confined + tension)
    ops.uniaxialMaterial("Parallel", b + 5, b + 3, b + 4)

    # +6: Main steel (Steel02)
    ops.uniaxialMaterial("Steel02", b + 6, FY, E_STEEL, B_MAIN, R0, CR1, CR2)
    # +7: MinMax on main steel
    ops.uniaxialMaterial("MinMax", b + 7, b + 6,
                         "-min", MINMAX_MIN_MAIN, "-max", MINMAX_MAX)
    # +8: Soft elastic
    ops.uniaxialMaterial("Elastic", b + 8, 0.01)
    # +9: Parallel (main steel + tension)
    ops.uniaxialMaterial("Parallel", b + 9, b + 7, b + 8)

    # +10: Spalling steel (Steel02, different b)
    ops.uniaxialMaterial("Steel02", b + 10, FY, E_STEEL, B_SPALL, R0, CR1, CR2)
    # +11: MinMax on spalling steel
    ops.uniaxialMaterial("MinMax", b + 11, b + 10,
                         "-min", MINMAX_MIN_SPALL, "-max", MINMAX_MAX)
    # +12: Soft elastic
    ops.uniaxialMaterial("Elastic", b + 12, 0.01)
    # +13: Parallel (spalling steel + tension)
    ops.uniaxialMaterial("Parallel", b + 13, b + 11, b + 12)

    # +14: Elastic shear spring (Vy)
    ops.uniaxialMaterial("Elastic", b + 14, G_SHEAR)


def _define_rotational_spring_materials() -> None:
    """Elastic rotational springs for 160 zeroLength elements.
    Story 1 (first 20 springs): K_SPRING_S1.
    Stories 2-8 (remaining 140): K_SPRING_S28.
    """
    for e in range(N_SPRINGS):
        tag = _tag3(MAT_SPRING_PREFIX, e, 0)
        K = K_SPRING_S1 if e < 20 else K_SPRING_S28
        ops.uniaxialMaterial("Elastic", tag, K)


def define_materials() -> None:
    """Define shared/base materials."""
    ops.uniaxialMaterial("Elastic", MAT_RIGID, 1e16)
    ops.uniaxialMaterial("Elastic", MAT_PDELTA_ELASTIC, E_PDELTA)
    ops.uniaxialMaterial("Elastic", MAT_TRUSS_RIGID, E_TRUSS)
    _define_rotational_spring_materials()


# ──6. DEFINE SECTIONS ========================================================
def define_sections() -> None:
    """160 fiber + aggregator sections (1 per element).
    Cross-section: 7000 x 500 mm wall with confined boundary zones.
    Matches Tcl fiber layout from NZ.tcl lines 462-492.
    All 5 Lobatto IPs share the same section (beamIntegration limitation).
    """
    hw = W_WALL / 2.0
    hd = T_WALL / 2.0
    hdc = D_CONF / 2.0

    y_web_neg = -90.456693 * inch
    y_web_pos =  90.456693 * inch
    y_conf_neg_L = -134.795276 * inch
    y_conf_pos_R =  134.795276 * inch
    y_ext_neg = -137.795276 * inch
    y_ext_pos =  137.795276 * inch
    y_cover_inner_L = -93.456693 * inch
    y_cover_inner_R =  93.456693 * inch

    z_bot = -9.842520 * inch
    z_top =  9.842520 * inch
    z_conf_bot = -6.842520 * inch
    z_conf_top =  6.842520 * inch

    left_bar_positions = [
        -134.795276, -128.889764, -122.984252, -117.078740,
        -111.173228, -105.267717, -99.362205, -93.456693,
    ]
    left_bar_counts = [3, 2, 2, 2, 2, 2, 2, 3]

    y_web_bar_start = -87.456693 * inch
    y_web_bar_end   =  87.456693 * inch

    for e in range(N_ELEMENTS):
        g = e
        _define_wall_material_group(g)
        mb = MAT_GROUP_BASE + g * 15

        fib_tag = SEC_BASE + e * 2
        aggr_tag = fib_tag + 1

        ops.section("Fiber", fib_tag)

        # Unconfined concrete web
        ops.patch("rect", mb + 2, 31, 1, y_web_neg, z_bot, y_web_pos, z_top)

        # Confined concrete, left zone
        ops.patch("rect", mb + 5, 8, 1, y_conf_neg_L, z_conf_bot, y_web_neg, z_conf_top)
        # Confined concrete, right zone
        ops.patch("rect", mb + 5, 8, 1, y_web_pos, z_conf_bot, y_conf_pos_R, z_conf_top)

        # Cover concrete strips
        ops.patch("rect", mb + 2, 8, 1, y_ext_neg, z_bot, y_web_neg, z_conf_bot)
        ops.patch("rect", mb + 2, 8, 1, y_ext_neg, z_conf_top, y_web_neg, z_top)
        ops.patch("rect", mb + 2, 1, 1, y_ext_neg, z_conf_bot, y_conf_neg_L, z_conf_top)
        ops.patch("rect", mb + 2, 1, 1, y_cover_inner_L, z_conf_bot, y_web_neg, z_conf_top)
        ops.patch("rect", mb + 2, 8, 1, y_web_pos, z_bot, y_ext_pos, z_conf_bot)
        ops.patch("rect", mb + 2, 8, 1, y_web_pos, z_conf_top, y_ext_pos, z_top)
        ops.patch("rect", mb + 2, 1, 1, y_web_pos, z_conf_bot, y_cover_inner_R, z_conf_top)
        ops.patch("rect", mb + 2, 1, 1, y_conf_pos_R, z_conf_bot, y_ext_pos, z_conf_top)

        # Longitudinal steel bars
        for n_bars, y_pos_in in zip(left_bar_counts, left_bar_positions):
            y_mm = y_pos_in * inch
            ops.layer("straight", mb + 9, n_bars, A_MAIN_BAR,
                      y_mm, z_conf_bot, y_mm, z_conf_top)
            ops.layer("straight", mb + 9, n_bars, A_MAIN_BAR,
                      -y_mm, z_conf_bot, -y_mm, z_conf_top)

        # Web distributed steel
        ops.layer("straight", mb + 13, 15, A_WEB_BAR,
                  y_web_bar_start, z_conf_bot, y_web_bar_end, z_conf_bot)
        ops.layer("straight", mb + 13, 15, A_WEB_BAR,
                  y_web_bar_start, z_conf_top, y_web_bar_end, z_conf_top)

        # Aggregator
        ops.section("Aggregator", aggr_tag, mb + 14, "Vy", "-section", fib_tag)

        # Beam integration: Lobatto with N_INTEG IPs, all sharing this section
        ops.beamIntegration("Lobatto", INTEG_BASE + e, aggr_tag, N_INTEG)


# ──7. DEFINE NODES ===========================================================
def _story_bottom_y(story_0idx: int) -> float:
    """Bottom y (mm) of story `story_0idx` (0-indexed, 0..7)."""
    if story_0idx == 0:
        return 0.0
    return H_GROUND + (story_0idx - 1) * H_TYPICAL


def _dz_for_story(story_0idx: int) -> float:
    """DZ per segment for this story (mm). 20 segments per story."""
    h = H_GROUND if story_0idx == 0 else H_TYPICAL
    return h / N_ELE_PER_STORY


def define_nodes() -> None:
    """Nodes with Tcl-compatible tags.
    Master:  1 + (s+1)*10 + NNN  e.g. 110001, 120001 (left), 110002, 120002 (right)
    Wall:    2 + (s+1)*10 + NNN  e.g. 210001..210019 (story 1), 220001..220019 (story 2)
    CL:      310001..310160 (continuous, 1 per element)
    """
    # Base / reaction extraction nodes
    ops.node(100001, 0.0, 0.0)
    ops.node(100002, W_BUILDING, 0.0)
    ops.node(200001, 0.0, 0.0)
    ops.node(200002, W_BUILDING, 0.0)

    # Master floor nodes: at top of each story
    master_left = []
    master_right = []
    for s in range(N_STORIES):
        y = _story_bottom_y(s) + (H_GROUND if s == 0 else H_TYPICAL)
        n_left  = 100000 + (s + 1) * 10000 + 1
        n_right = 100000 + (s + 1) * 10000 + 2
        ops.node(n_left,  0.0, y)
        ops.node(n_right, W_BUILDING, y)
        master_left.append(n_left)
        master_right.append(n_right)

    # Wall edge nodes + centerline nodes
    cl_nodes = []
    wall_nodes = []
    for e in range(N_ELEMENTS):
        s = e // N_ELE_PER_STORY
        seg = e % N_ELE_PER_STORY
        dz = _dz_for_story(s)

        cl_y = _story_bottom_y(s) + seg * dz
        cl_tag = 310001 + e
        ops.node(cl_tag, 0.0, cl_y)
        cl_nodes.append(cl_tag)

        # Target node for beam: wall node at top of segment, or master at transition
        if seg == N_ELE_PER_STORY - 1:
            target_tag = master_left[s]
            target_y = _story_bottom_y(s) + (H_GROUND if s == 0 else H_TYPICAL)
        else:
            target_tag = 200000 + (s + 1) * 10000 + (seg + 1)
            target_y = cl_y + dz
            ops.node(target_tag, 0.0, target_y)
        wall_nodes.append((target_tag, target_y))

    define_nodes._master_left = master_left
    define_nodes._master_right = master_right
    define_nodes._cl_nodes = cl_nodes
    define_nodes._wall_nodes = wall_nodes


# ──8. DEFINE BOUNDARY CONDITIONS ============================================
def define_boundary_conditions() -> None:
    """Fixity and rigid diaphragm constraints."""
    ops.fix(200001, 1, 1, 1)   # full fixity (left base)
    ops.fix(200002, 1, 1, 0)   # pinned (right base, rotation free)

    ml = define_nodes._master_left
    mr = define_nodes._master_right
    for s in range(N_STORIES):
        ops.equalDOF(ml[s], mr[s], 1)  # DOF 1 (UX) = rigid diaphragm


# ──9. DEFINE ELEMENTS ========================================================
def _geom_transforms() -> None:
    ops.geomTransf("PDelta", TRANS_PDELTA)


def _define_wall_elements() -> None:
    """160 dispBeamColumn + 160 zeroLength rotational springs.
    Connectivity matches Tcl: beam[e] CL[e]→target[e], zl[e] prev→CL[e]
    where prev = 100001 for e=0, otherwise target[e-1].
    """

    cl = define_nodes._cl_nodes
    wnodes = define_nodes._wall_nodes

    for e in range(N_ELEMENTS):
        s = e // N_ELE_PER_STORY
        seg = e % N_ELE_PER_STORY

        cl_node = cl[e]               # 310001..310160
        target, _ = wnodes[e]          # wall or master node

        prev = 100001 if e == 0 else wnodes[e - 1][0]

        beam_tag = _tag3(ELE_BEAM_PREFIX, e, 1)
        integ_tag = INTEG_BASE + e
        ops.element("dispBeamColumn", beam_tag,
                    cl_node, target,
                    TRANS_PDELTA, integ_tag)

        # ZeroLength rotational spring
        zl_tag = _tag3(ELE_ZL_PREFIX, e, 1)
        spring_mat = _tag3(MAT_SPRING_PREFIX, e, 0)
        ops.element("zeroLength", zl_tag,
                    prev, cl_node,
                    "-mat", spring_mat, MAT_RIGID, MAT_RIGID,
                    "-dir", 1, 2, 3)


def _define_pdelta_column() -> None:
    """8 elasticBeamColumn elements -- P-Delta leaning column (right side).
    Tcl: 910002(100002→110002), 920002(110002→120002), ... 980002(170002→180002).
    """
    for s in range(N_STORIES):
        bot = 100002 if s == 0 else (100000 + s * 10000 + 2)
        top = 100000 + (s + 1) * 10000 + 2
        tag = ELE_PDELTA_BASE + s * 10000
        ops.element("elasticBeamColumn", tag,
                    bot, top, A_PDELTA, MAT_PDELTA_ELASTIC, I_PDELTA,
                    TRANS_PDELTA)

    # Base anchor: connect 200002 to 100002 via rigid zeroLength
    ops.element("zeroLength", ELE_REACT_RIGHT,
                200002, 100002,
                "-mat", MAT_RIGID, MAT_RIGID, MAT_RIGID,
                "-dir", 1, 2, 3)


def _define_diaphragm_trusses() -> None:
    """8 rigid truss elements linking left/right master nodes at each floor."""
    ml = define_nodes._master_left
    mr = define_nodes._master_right
    for s in range(N_STORIES):
        tag = ELE_TRUSS_BASE + s * 10000
        ops.element("truss", tag, ml[s], mr[s], A_TRUSS, MAT_TRUSS_RIGID)


def _define_reaction_elements() -> None:
    """ZeroLength element for reaction extraction at base (left side)."""
    ops.element("zeroLength", ELE_REACT_LEFT,
                200001, 100001,
                "-mat", MAT_RIGID, MAT_RIGID, MAT_RIGID,
                "-dir", 1, 2, 3)


def define_elements() -> None:
    _geom_transforms()
    _define_wall_elements()
    _define_pdelta_column()
    _define_diaphragm_trusses()
    _define_reaction_elements()


# ── 10. CREATE ODB ============================================================
def create_odb(output_dir: Path, node_tags: list | None = None) -> "opst.post.CreateODB":
    opst.post.set_odb_path(str(output_dir))
    if node_tags:
        odb = opst.post.CreateODB(
            odb_tag=ODB_TAG,
            node_tags=node_tags,
        )
    else:
        odb = opst.post.CreateODB(odb_tag=ODB_TAG)
    odb.save_model_data()
    return odb


# ──11. LOADING ==============================================================
def define_nodal_masses() -> None:
    """Lumped translational masses at left master nodes only (Tcl convention).
    Right side is connected via rigid diaphragm (equalDOF) and PDelta column.
    """
    ml = define_nodes._master_left
    for s in range(N_STORIES):
        m = MASS_ROOF if s == N_STORIES - 1 else MASS_FLOOR_1_7
        ops.mass(ml[s], m, 1e-9, 1e-9)


def define_gravity_loads() -> None:
    """No explicit gravity loads -- self-weight equilibration only."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PATTERN_GRAVITY, TS_GRAVITY)


# ──12. ANALYSIS =============================================================
def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10) -> None:
    """Static gravity analysis (LoadControl)."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", 1.0e-6, 1000, 2)
    ops.algorithm("KrylovNewton")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.analysis("Static")
    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()
    print("Gravity analysis complete.")


def run_eigen() -> list:
    """Eigenvalue analysis -- 7 modes. Returns list of circular frequencies."""
    eigenvalues = ops.eigen(N_MODES)
    omegas = [float(np.sqrt(max(lam, 0.0))) for lam in eigenvalues]
    periods = [2.0 * np.pi / w if w > 0 else float("inf") for w in omegas]
    for i, (T, w) in enumerate(zip(periods, omegas), 1):
        print(f"  T{i} = {T:.4f} s,  omega{i} = {w:.4f} rad/s")
    return omegas


def _define_rayleigh_damping(omegas: list) -> None:
    """Rayleigh damping: 2% targeted on modes 1 and 3."""
    w1 = omegas[DAMP_MODE_I - 1]
    w3 = omegas[DAMP_MODE_J - 1]
    aM = ZETA * 2.0 * w1 * w3 / (w1 + w3)
    bK = ZETA * 2.0 / (w1 + w3)
    ops.rayleigh(aM, 0.0, 0.0, bK)
    print(f"Rayleigh damping: aM={aM:.6f}, bK={bK:.6f} "
          f"(zeta={ZETA:.1%} on modes {DAMP_MODE_I},{DAMP_MODE_J})")


def run_dynamic(
    odb: "opst.post.CreateODB",
    gm_file: Path,
    dt: float = DT_GM,
    n_steps: int = N_STEPS_GM,
) -> None:
    """Transient time-history analysis using SmartAnalyze."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.integrator("Newmark", 0.5, 0.25)

    ops.timeSeries("Path", TS_DYNAMIC, "-dt", dt,
                   "-filePath", str(gm_file), "-factor", SCALE_GM)
    ops.pattern("UniformExcitation", PATTERN_DYNAMIC, 1, "-accel", TS_DYNAMIC)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50, 60],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )
    segs = analysis.transient_split(n_steps)
    completed = 0
    print(f"Dynamic analysis: {n_steps} steps, dt={dt}s")
    for i, _ in enumerate(segs):
        ok = analysis.TransientAnalyze(dt)
        if ok < 0:
            print(f"  Dynamic analysis failed at step {i}/{n_steps}")
            break
        if i % ODB_EVERY_N == 0:
            odb.fetch_response_step()
        completed = i + 1
    analysis.close()
    print(f"Dynamic analysis complete ({completed}/{n_steps} steps).")


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    # Build model
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)           # V1
    define_elements()
    vis_model(output_dir)           # V2

    # Track only key nodes in ODB (master + reaction) to avoid I/O bottleneck
    tracked_nodes = (
        define_nodes._master_left
        + define_nodes._master_right
        + [200001, 200002, 100001, 100002]
    )
    odb = create_odb(output_dir, node_tags=tracked_nodes)
    define_nodal_masses()
    define_gravity_loads()
    vis_loads(output_dir)           # V3
    vis_pre_analysis(output_dir)    # V4

    # Gravity
    run_gravity(odb)

    # Eigen
    omegas = run_eigen()

    # Rayleigh damping
    _define_rayleigh_damping(omegas)

    # Dynamic (skip if EIGEN_ONLY=1)
    if os.environ.get("EIGEN_ONLY") != "1":
        gm_file = Path(__file__).parent / "ground_motions" / "WELL1p0_1_10_1.txt"
        run_dynamic(odb, gm_file)

    return odb


# ── 13. POST-PROCESSING =======================================================
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    odb.save_response()
    if not _headless():
        try:
            fig = opst.vis.plotly.plot_nodal_responses(
                odb_tag=ODB_TAG, resp_type="disp", resp_dof="UX",
            )
            fig.write_html(str(output_dir / "vis_05_deformed.html"))
        except Exception:
            pass
        try:
            n_frames = N_STEPS_GM // ODB_EVERY_N
            anim = opst.vis.plotly.plot_nodal_responses_animation(
                odb_tag=ODB_TAG,
                framerate=n_frames // 20,
                defo_scale=True,
                resp_type="disp",
                resp_dof="UX",
            )
            anim.write_html(str(output_dir / "vis_06_animation.html"))
        except Exception:
            pass


# ──14. MAIN ==================================================================
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    ops.wipe()
