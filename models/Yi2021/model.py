# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Single-bay single-story steel moment frame with lumped plasticity
UniqueID : Yi2021
Author   : Xiaolei Xiong (Tongji Univ.) / Henry Burton (Stanford Univ.),
           ported by OpenSeesPy Standardisation Agent
Date     : 2026-06-06
Purpose  : Static pushover analysis of a 3D steel moment-resisting frame with
           Modified Ibarra-Krawinkler (Bilin) concentrated plastic hinges.
           Originally part of the WoodFrameBuildingTool suite.
Ref      : https://github.com/roveryi/WoodFrameBuildingTool
           Ibarra, L. F., and Krawinkler, H. (2005). "Global collapse of frame
           structures under seismic excitations," Technical Report 152, Stanford.
           Lignos, D. G., and Krawinkler, H. (2011). "Deterioration modeling of
           steel components in support of collapse prediction of steel moment
           frames under earthquake loading," ASCE, Journal of Structural
           Engineering, Vol. 137, No. 11, pp. 1291-1302.
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
from vis_utils import vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo, vis_anim


# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# All integer tags as NAMED CONSTANTS — no magic numbers anywhere else.

# --- Geometric transformations ---
TRANS_PDELTA    = 1   # PDelta transformation (columns)
TRANS_XBEAM     = 4   # Linear transformation for X-direction beam

# --- Materials ---
MAT_STIFF       = 1200       # Very stiff elastic (rigid links)
MAT_SOFT        = 1300       # Very soft (negligible stiffness)
MAT_BEAM_HINGE  = 700000001  # Bilin hinge material for beam
MAT_COL_HINGE   = 800000001  # Bilin hinge material for column

# --- Nodes ---
NODE_BASE_L_EXT  = 111017    # Base, left column, external (fixed node)
NODE_BASE_L_INT  = 111018    # Base, left column, internal (column base)
NODE_BASE_R_EXT  = 121017    # Base, right column, external (fixed node)
NODE_BASE_R_INT  = 121018    # Base, right column, internal (column base)

NODE_ROOF_L_BEAM = 211015    # Roof, left, beam end
NODE_ROOF_L_MID  = 211016    # Roof, left, mid (column top + hinge)
NODE_ROOF_L_MAIN = 211019    # Roof, left, main (diaphragm + loading)

NODE_ROOF_R_BEAM = 221015    # Roof, right, beam end
NODE_ROOF_R_MID  = 221016    # Roof, right, mid (column top + hinge)
NODE_ROOF_R_MAIN = 221019    # Roof, right, main (diaphragm + loading)

# --- Elements ---
ELE_BEAM        = 101   # Elastic beam
ELE_COL_L       = 201   # Elastic column, left
ELE_COL_R       = 202   # Elastic column, right
ELE_BEAM_HINGE_L = 21107  # Zero-length beam hinge, left end
ELE_BEAM_HINGE_R = 22107  # Zero-length beam hinge, right end
ELE_COL_HINGE_BL = 111012  # Zero-length column base hinge, left
ELE_COL_HINGE_BR = 121012  # Zero-length column base hinge, right
ELE_COL_HINGE_TL = 211011  # Zero-length column top hinge, left
ELE_COL_HINGE_TR = 221011  # Zero-length column top hinge, right

# --- Load patterns ---
PATTERN_GRAVITY = 101
PATTERN_PUSHOVER = 200


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────

# --- Geometry (converted from inches) ---
bay_width    = 180.0 * inch      # 15 ft bay width → 4572 mm
story_height = 111.0 * inch      # 9.25 ft story height → 2819.4 mm

# --- Steel material properties (converted from ksi) ---
E_steel  = 29000.0 * ksi    # 29000 ksi → ~200,000 MPa
G_steel  = 11500.0 * ksi    # 11500 ksi → ~79,290 MPa
fy_beam  = 36.0 * ksi       # Beam yield strength → ~248 MPa
fy_col   = 50.0 * ksi       # Column yield strength → ~345 MPa

# --- Stiffness factors (dimensionless) ---
stiff_factor_n = 20.0        # n factor for hinge stiffness modification

# --- Beam section: W10X33 (from Database.csv) ---
# Imperial source values shown in comments
beam_A  = 9.71  * inch**2    # → 6265 mm²
beam_Ix = 171.0 * inch**4    # → 7.118e7 mm⁴
beam_Iy = 36.6  * inch**4    # → 1.523e7 mm⁴
beam_Zx = 38.8  * inch**3    # → 635,800 mm³
beam_J  = 0.583 * inch**4    # → 242,700 mm⁴
beam_d  = 9.73  * inch       # depth → 247.1 mm
beam_bf = 7.96  * inch       # flange width → 202.2 mm
beam_tw = 0.290 * inch       # web thickness → 7.37 mm
beam_tf = 0.435 * inch       # flange thickness → 11.05 mm
beam_ry = 1.94  * inch       # radius of gyration → 49.3 mm

# --- Column section: Box (hardcoded in original PoModel.tcl) ---
# b=8.02 in, t=0.35 in
col_b   = 8.02 * inch        # box width → 203.7 mm
col_t   = 0.35 * inch        # wall thickness → 8.89 mm
col_A   = 17.0  * inch**2    # area → 10,968 mm²
col_Ix  = 475.0 * inch**4    # Ix → 1.977e8 mm⁴
col_Zx  = 86.4  * inch**3    # Zx → 1,415,845 mm³
col_ry  = 2.51  * inch       # ry → 63.8 mm
col_J   = 1.0e6 * inch**4    # J (intentionally large) → 4.162e11 mm⁴

# --- Very stiff / very soft materials (for rigid links) ---
large_stiff = 1.0e12 * ksi           # → 6.895e12 MPa
negligible   = 1.0e-12 * ksi         # → ~0 MPa

# --- Empirical coefficients for c2 (stress unit converter for Lignos equations) ---
# In the original Tcl: set c2 6.895 (converts MPa to ksi multiply factor)
# The Lignos equations use value/355 where 355 is fy in MPa
# We keep fy*c2 to get fy in MPa for the ratio fy/355
c2_mpa = 6.895   # ksi-to-MPa factor (used in empirical equations)

# --- Hinge geometry ---
beam_h   = beam_d - 2 * beam_tf              # clear depth between flanges
beam_L   = bay_width                          # beam length
col_L    = story_height                       # column height

# --- Beam hinge parameters (Lignos & Krawinkler empirical equations) ---
beam_K0 = 6.0 * E_steel * beam_Ix / beam_L   # initial rotational stiffness
beam_My = beam_Zx * fy_beam                   # yield moment
beam_theta_y = beam_My / beam_K0              # yield rotation

# Lambda: cyclic deterioration parameter (Lignos & Krawinkler 2011)
beam_Lambda = (536.0
               * (beam_h / beam_tw) ** (-1.26)
               * (beam_bf / 2.0 / beam_tf) ** (-0.525)
               * ((fy_beam / MPa) / 355.0) ** (-0.291)
               * (beam_L / beam_ry) ** (-0.130))

# theta_p: plastic rotation capacity
beam_theta_p = (0.318
                * (beam_h / beam_tw) ** (-0.55)
                * (beam_bf / 2.0 / beam_tf) ** (-0.345)
                * ((fy_beam / MPa) / 355.0) ** (-0.130)
                * (beam_d / mm / 533.0) ** (-0.330)
                * (beam_L / beam_d) ** (0.090)
                * (beam_L / beam_ry) ** (-0.0230))

# theta_pc: post-capping rotation capacity
beam_theta_pc = (7.50
                 * (beam_h / beam_tw) ** (-0.61)
                 * (beam_bf / 2.0 / beam_tf) ** (-0.71)
                 * ((fy_beam / MPa) / 355.0) ** (-0.320)
                 * (beam_d / mm / 533.0) ** (-0.161)
                 * (beam_L / beam_ry) ** (-0.110))

beam_as = beam_My * 0.11 / beam_K0 / beam_theta_p   # strain hardening ratio
beam_MrR = 0.25                                      # residual strength ratio
beam_theta_all = beam_theta_y + beam_theta_p * beam_theta_pc
beam_theta_u = min(0.06, beam_theta_all)             # ultimate rotation capacity

# --- Column hinge parameters ---
col_K0 = 6.0 * E_steel * col_Ix / col_L
col_My = 5750.0 * kip * inch           # 5750 kip-in → ~6.497e8 N·mm
col_theta_y = col_My / col_K0
col_Lambda = 1.659                     # hardcoded in PoModel.tcl
col_theta_p = 0.046                    # hardcoded in PoModel.tcl
col_theta_pc = 0.183                   # hardcoded in PoModel.tcl
col_as = col_My * 0.06 / col_K0 / col_theta_p  # strain hardening ratio
col_MrR = 0.25                         # residual strength ratio
col_theta_u = 0.4                      # ultimate rotation capacity

# --- Pushover parameters ---
pushover_target_drift = 0.10            # 10% drift
pushover_dmax = pushover_target_drift * story_height  # target displacement
pushover_max_step = 1.0 * mm            # initial step size → 1 mm
pushover_load_magnitude = 1000.0 * kip   # 1000 kip reference load → ~4.448 MN

# --- Gravity parameters ---
n_steps_gravity = 5


# ── 4. HELPER: Bilin Material Factory ──────────────────────────────────────

def create_bilin_material(
    mat_tag: int,
    K0: float,
    n_factor: float,
    as_val: float,
    My: float,
    Lambda: float,
    th_p: float,
    th_pc: float,
    Res: float,
    th_u: float,
) -> None:
    """Create a Bilin (Modified Ibarra-Krawinkler) uniaxial material.

    Implements the stiffness/strength modification per Ibarra & Krawinkler (2005)
    for use with concentrated plastic hinge elements.  The n_factor accounts for
    the difference between the elastic element stiffness and the hinge stiffness.

    Args:
        mat_tag: Material tag.
        K0: Initial rotational stiffness before n-factor modification.
        n_factor: Stiffness modification factor (≡ stiffFactor_n).
        as_val: Strain hardening ratio before n-factor modification.
        My: Positive yield moment (absolute value).
        Lambda: Reference cumulative deterioration parameter.
        th_p: Pre-capping plastic rotation capacity.
        th_pc: Post-capping rotation capacity.
        Res: Residual strength ratio.
        th_u: Ultimate rotation capacity (before n-factor modification).
    """
    K_mod = n_factor * K0
    asM = as_val * (n_factor + 1.0) / n_factor
    as_scaled = asM / (1.0 + n_factor * (1.0 - asM))

    LS = Lambda * n_factor
    LK = 0.0
    LA = 0.0
    LD = Lambda * n_factor
    th_u_scaled = th_u * n_factor

    ops.uniaxialMaterial(
        "IMKBilin",
        mat_tag,
        K_mod,
        as_scaled,                   # as_Plus
        as_scaled,                   # as_Neg
        My,                          # My_Plus
        -My,                         # My_Neg
        LS, LK, LA, LD,             # Lambda_S, Lambda_K, Lambda_A, Lambda_D
        1.0, 1.0, 1.0, 1.0,        # c_S, c_K, c_A, c_D
        th_p, th_p,                 # theta_p_Plus / Neg
        th_pc, th_pc,               # theta_pc_Plus / Neg
        Res, Res,                   # Res_Pos / Neg
        th_u_scaled, th_u_scaled,   # theta_u_Plus / Neg
        1.0, 1.0,                   # D_Plus / Neg
        0.0,                        # nFactor — no internal mod (we pre-modify)
    )


# ── 5. MODEL INITIALISATION ──────────────────────────────────────────────────

def init_model() -> None:
    """Wipe any existing model and create a 3D-6DOF BasicBuilder."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 6. MATERIALS ─────────────────────────────────────────────────────────────

def define_materials() -> None:
    """Define all uniaxial materials: stiff/soft elastic + Bilin hinges."""
    # Rigid / soft links
    ops.uniaxialMaterial("Elastic", MAT_STIFF, large_stiff)
    ops.uniaxialMaterial("Elastic", MAT_SOFT, negligible)

    # Beam rotational hinge (Bilin — Modified Ibarra-Krawinkler)
    create_bilin_material(
        mat_tag=MAT_BEAM_HINGE,
        K0=beam_K0,
        n_factor=stiff_factor_n,
        as_val=beam_as,
        My=beam_My,
        Lambda=beam_Lambda,
        th_p=beam_theta_p,
        th_pc=beam_theta_pc,
        Res=beam_MrR,
        th_u=beam_theta_u,
    )

    # Column rotational hinge (Bilin — Modified Ibarra-Krawinkler)
    create_bilin_material(
        mat_tag=MAT_COL_HINGE,
        K0=col_K0,
        n_factor=stiff_factor_n,
        as_val=col_as,
        My=col_My,
        Lambda=col_Lambda,
        th_p=col_theta_p,
        th_pc=col_theta_pc,
        Res=col_MrR,
        th_u=col_theta_u,
    )


# ── 7. GEOMETRIC TRANSFORMATIONS ────────────────────────────────────────────

def define_transformations() -> None:
    """Define geometric transformations for columns and beams."""
    ops.geomTransf("PDelta", TRANS_PDELTA, 0, 0, 1)       # columns
    ops.geomTransf("Linear", TRANS_XBEAM, 0, 0, 1)        # X-direction beam


# ── 8. NODES ─────────────────────────────────────────────────────────────────

def define_nodes() -> None:
    """Create all nodes.

    Node topology (each physical location has 2-3 coincident nodes for hinges):

      Base level (Y=0):
        [111017, 111018] @ (0, 0, 0)        — left column base
        [121017, 121018] @ (bay_width, 0, 0) — right column base

      Roof level (Y=story_height):
        [211015, 211016, 211019] @ (0,            story_height, 0) — left
        [221015, 221016, 221019] @ (bay_width,    story_height, 0) — right

    Node roles:
      - xx17: external / fixed boundary node
      - xx18: internal (column element end)
      - xx15: beam end node
      - xx16: mid node (column element end + hinge)
      - xx19: main node (diaphragm constraints + loads)
    """
    # Base level — left column
    ops.node(NODE_BASE_L_EXT, 0.0, 0.0, 0.0)
    ops.node(NODE_BASE_L_INT, 0.0, 0.0, 0.0)
    # Base level — right column
    ops.node(NODE_BASE_R_EXT, bay_width, 0.0, 0.0)
    ops.node(NODE_BASE_R_INT, bay_width, 0.0, 0.0)

    # Roof level — left
    ops.node(NODE_ROOF_L_BEAM, 0.0, story_height, 0.0)
    ops.node(NODE_ROOF_L_MID,  0.0, story_height, 0.0)
    ops.node(NODE_ROOF_L_MAIN, 0.0, story_height, 0.0)
    # Roof level — right
    ops.node(NODE_ROOF_R_BEAM, bay_width, story_height, 0.0)
    ops.node(NODE_ROOF_R_MID,  bay_width, story_height, 0.0)
    ops.node(NODE_ROOF_R_MAIN, bay_width, story_height, 0.0)


# ── 9. BOUNDARY CONDITIONS ───────────────────────────────────────────────────

def define_boundary_conditions() -> None:
    """Apply base fixity and rigid diaphragm constraint."""
    # Both base column external nodes fully fixed
    ops.fix(NODE_BASE_L_EXT, 1, 1, 1, 1, 1, 1)
    ops.fix(NODE_BASE_R_EXT, 1, 1, 1, 1, 1, 1)

    # Rigid diaphragm: constrain X, Z, RY between roof main nodes
    ops.equalDOF(NODE_ROOF_R_MAIN, NODE_ROOF_L_MAIN, 1, 3, 5)


# ── 10. ELEMENTS ─────────────────────────────────────────────────────────────

def define_elements() -> None:
    """Define elastic beam-columns and zero-length hinge springs.

    Element connectivity:

    Beam:
      elasticBeamColumn 101 : 211015 (L beam end) → 221015 (R beam end)
      zeroLength hinge 21107 : 211019 (main) ↔ 211015 (beam end)  — left end, RY
      zeroLength hinge 22107 : 221015 (beam end) ↔ 221019 (main)  — right end, RY

    Columns:
      elasticBeamColumn 201 : 111018 (base int) → 211016 (roof mid)
      elasticBeamColumn 202 : 121018 (base int) → 221016 (roof mid)

      zeroLength hinge 111012 : 111017 (fixed) ↔ 111018 (col base) — base left
      zeroLength hinge 121012 : 121017 (fixed) ↔ 121018 (col base) — base right
      zeroLength hinge 211011 : 211016 (col top) ↔ 211019 (main)   — top left
      zeroLength hinge 221011 : 221016 (col top) ↔ 221019 (main)   — top right
    """
    # --- Elastic beam ---
    ops.element(
        "elasticBeamColumn",
        ELE_BEAM,
        NODE_ROOF_L_BEAM, NODE_ROOF_R_BEAM,
        beam_A, E_steel, G_steel,
        beam_J, beam_Iy, beam_Ix,
        TRANS_XBEAM,
    )

    # --- Elastic columns ---
    for ele_tag, base_node, roof_node in [
        (ELE_COL_L, NODE_BASE_L_INT, NODE_ROOF_L_MID),
        (ELE_COL_R, NODE_BASE_R_INT, NODE_ROOF_R_MID),
    ]:
        ops.element(
            "elasticBeamColumn",
            ele_tag,
            base_node, roof_node,
            col_A, E_steel, G_steel,
            col_J, col_Ix, col_Ix,
            TRANS_PDELTA,
        )

    # --- Beam rotational hinges (zero-length, RY direction = DOF 6) ---
    # rotXBeamSpring3DModIKModel: all DOFs stiff except RY (DOF 6) which gets hinge
    for ele_tag, node_r, node_c in [
        (ELE_BEAM_HINGE_L, NODE_ROOF_L_MAIN, NODE_ROOF_L_BEAM),
        (ELE_BEAM_HINGE_R, NODE_ROOF_R_BEAM, NODE_ROOF_R_MAIN),
    ]:
        ops.element(
            "zeroLength",
            ele_tag,
            node_r, node_c,
            "-mat",
            MAT_STIFF, MAT_STIFF, MAT_STIFF,
            MAT_STIFF, MAT_STIFF, MAT_BEAM_HINGE,
            "-dir", 1, 2, 3, 4, 5, 6,
            "-orient", 1, 0, 0, 0, 1, 0,
        )

    # --- Column hinges (zero-length, default orientation) ---
    # rotColSpring3DModIKModel: DOF 1=axial(stiff), 2,3=shear(stiff),
    #   DOF 4=torsion(stiff), DOF 5,6=flexure(hinge)
    # Base hinges: between fixed external node and column internal node
    for ele_tag, ext_node, int_node in [
        (ELE_COL_HINGE_BL, NODE_BASE_L_EXT, NODE_BASE_L_INT),
        (ELE_COL_HINGE_BR, NODE_BASE_R_EXT, NODE_BASE_R_INT),
    ]:
        ops.element(
            "zeroLength",
            ele_tag,
            ext_node, int_node,
            "-mat",
            MAT_STIFF, MAT_STIFF, MAT_STIFF,
            MAT_COL_HINGE, MAT_STIFF, MAT_COL_HINGE,
            "-dir", 1, 2, 3, 4, 5, 6,
        )

    # Top hinges: between column internal node and main node
    for ele_tag, mid_node, main_node in [
        (ELE_COL_HINGE_TL, NODE_ROOF_L_MID, NODE_ROOF_L_MAIN),
        (ELE_COL_HINGE_TR, NODE_ROOF_R_MID, NODE_ROOF_R_MAIN),
    ]:
        ops.element(
            "zeroLength",
            ele_tag,
            mid_node, main_node,
            "-mat",
            MAT_STIFF, MAT_STIFF, MAT_STIFF,
            MAT_COL_HINGE, MAT_STIFF, MAT_COL_HINGE,
            "-dir", 1, 2, 3, 4, 5, 6,
        )


# ── 11. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────

def create_odb(output_dir: Path, odb_tag: int = 1) -> "opst.post.CreateODB":
    """Initialise the ODB and snapshot the model geometry.

    Args:
        output_dir: Directory where ODB (Zarr) files are written.
        odb_tag: ODB identifier tag.

    Returns:
        The active CreateODB instance ready for fetch_response_step() calls.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=odb_tag)
    odb.save_model_data()
    return odb


# ── 12. LOADING ──────────────────────────────────────────────────────────────

def define_gravity_loads() -> None:
    """Define gravity load pattern.

    Note: The original PoModel.tcl has gravity loads commented out for this
    single-bay single-story test case.  We define the pattern but with no
    applied loads — gravity self-weight is not applied in this simplified model.
    The load pattern is created for compatibility with the canonical layout.
    """
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", PATTERN_GRAVITY, 1, "-fact", 1.0)
    # No nodal/element loads — this is a simplified test case where gravity
    # self-weight is omitted (matching the original PoModel.tcl behaviour).
    # To add gravity self-weight, define nodal masses and/or eleLoad here.


def define_lateral_loads() -> None:
    """Define X-direction pushover reference load at the roof control node."""
    ops.timeSeries("Linear", 2)
    ops.pattern("Plain", PATTERN_PUSHOVER, 2, "-fact", 1.0)
    ops.load(NODE_ROOF_L_MAIN, pushover_load_magnitude, 0.0, 0.0, 0.0, 0.0, 0.0)


# ── 13. ANALYSIS ─────────────────────────────────────────────────────────────

# Gravity — load-controlled static (permitted exception to SmartAnalyze mandate)
def run_gravity(odb: "opst.post.CreateODB", n_steps: int = n_steps_gravity) -> None:
    """Apply gravity loads incrementally using LoadControl.

    SmartAnalyze.StaticAnalyze forcibly overrides the integrator to
    DisplacementControl, making LoadControl impossible.  This manual loop is
    the permitted exception documented in AGENT.md §3c and §10.

    Args:
        odb: Active CreateODB instance.
        n_steps: Number of load increments.
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("SparseSYM")
    ops.test("NormDispIncr", 1.0e-8, 20, 2)
    ops.algorithm("NewtonLineSearch", 0.75)
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.analysis("Static")

    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


# Pushover — displacement-controlled static (SmartAnalyze)
def run_pushover(
    odb: "opst.post.CreateODB",
    ctrl_node: int,
    ctrl_dof: int,
    target_disp: float,
    max_step: float,
) -> None:
    """Run a displacement-controlled pushover using SmartAnalyze (Static).

    Args:
        odb: Active CreateODB instance.
        ctrl_node: Tag of the control node (roof level).
        ctrl_dof: DOF direction (1 = X).
        target_disp: Target displacement in mm.
        max_step: Maximum step size in mm.
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("SparseSYM")
    # Do NOT set integrator — SmartAnalyze uses DisplacementControl internally

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


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + pushover, return ODB for post-processing.

    Args:
        output_dir: Directory for ODB files and HTML output.

    Returns:
        The populated CreateODB instance.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials()
    define_transformations()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)                     # V1: nodes + supports
    define_elements()
    vis_model(output_dir)                     # V2: full geometry
    odb = create_odb(output_dir, odb_tag=1)
    define_gravity_loads()
    vis_loads(output_dir)                     # V3: gravity load vectors
    run_gravity(odb)
    # ── define pushover loads AFTER gravity so loadConst doesn't freeze them ──
    define_lateral_loads()
    vis_pre_analysis(output_dir)              # V4: full model + all loads
    run_pushover(
        odb,
        ctrl_node=NODE_ROOF_L_MAIN,
        ctrl_dof=1,
        target_disp=pushover_dmax,
        max_step=pushover_max_step,
    )
    return odb


# ── 14. POST-PROCESSING ──────────────────────────────────────────────────────

def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk, render deformed shape and animation.

    Args:
        odb: Populated CreateODB returned by run_analysis().
        output_dir: Folder where ODB and HTML files are written.
    """
    odb.save_response()
    vis_defo(output_dir, filename="vis_05_deformed.html")
    vis_anim(
        output_dir,
        filename="vis_06_pushover_animation.html",
        odb_tag=1,
        defo_scale=20.0,
        resp_type="disp",
        resp_dof=("UX", "UY", "UZ"),
        show_undeformed=True,
    )


# ── 15. MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print(f"Yi2021 pushover complete. Output in {output_dir}")
