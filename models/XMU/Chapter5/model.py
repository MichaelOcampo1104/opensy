# -- 0. FILE HEADER --------------------------------------------------------------
"""
Model    : 2D RC Shear Wall RW2-2 -- Cyclic Pushover
UniqueID : XMU_Chapter5
Author   : XMU (Xiamen University) -- Chapter 5 Example
Date     : 2026-06-16
Purpose  : Textbook-example cyclic pushover analysis of a slender RC structural
           wall (RW2-2 specimen, Thomsen & Wallace 2004) with fiber-section
           boundary columns (Concrete02 core+cover, Steel02 rebar), elastic
           spider-beam top, and quad wall elements with SmearedCompositePlaneStress
           nDMaterial. Sequential model building: frame (ndf=3) -> quad (ndf=2)
           -> equalDOF ties. Gravity (378 kN) then displacement-controlled cyclic
           pushover with 8 peak amplitudes (Full cycle type).
Ref      : XMU Finite Element Analysis course, Chapter 5
Units    : N, mm, MPa  (see standards/units.py)
Notes    : Converted from RW2_2.tcl + GeneratePeaks.tcl.
           Original uses N-mm-MPa -- NO unit conversion needed, values preserved.
           SmearedCompositePlaneStress and SmearedConcrete are RESEARCH-FORK
           materials NOT in standard OpenSeesPy. Requires custom build.
           Boundary columns: 153x102 mm, 19 mm cover, 4x#3 rebar per layer.
           Wall panel: 1032x3660x102 mm, SmearedCompositePlaneStress quad mesh.
           Cyclic protocol: 8 peaks (3.79->71.28 mm), Full cycle, 0.02 mm incr.
"""

# -- 1. IMPORTS -------------------------------------------------------------------
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# -- 2. TAG REGISTRY --------------------------------------------------------------
# Frame materials (ndf=3 phase)
MAT_CONCRETE_CORE  = 1   # Concrete02 -- confined core
MAT_CONCRETE_COVER = 2   # Concrete02 -- cover
MAT_STEEL_REBAR    = 3   # Steel02    -- longitudinal rebar

# Frame sections
SEC_COL_FIBER  = 1   # Fiber section for boundary columns
SEC_BEAM_ELAST = 2   # Elastic section for top beam (rigid links)

# Frame element tags
# Nodes: 1-11 left col, 12-22 right col, 23-27 top beam, 28 control, 29-105 quad grid

# Wall materials (ndf=2 phase)
MAT_STEEL_SMEAR_X = 11  # Steel02 -- smeared reinforcement X
MAT_STEEL_SMEAR_Y = 12  # Steel02 -- smeared reinforcement Y
MAT_CONC_W1       = 13  # SmearedConcrete -- zone 1 (fc=42.8)
MAT_CONC_W2       = 14  # SmearedConcrete -- zone 2 (fc=45.7)
MAT_CONC_W3       = 15  # SmearedConcrete -- zone 3 (fc=40.8)
MAT_CONC_W4       = 16  # SmearedConcrete -- zone 4 (fc=41.3)

# nDMaterials
MAT_ND_W1 = 111  # SmearedCompositePlaneStress -- zone 1
MAT_ND_W2 = 112  # SmearedCompositePlaneStress -- zone 2
MAT_ND_W3 = 113  # SmearedCompositePlaneStress -- zone 3
MAT_ND_W4 = 114  # SmearedCompositePlaneStress -- zone 4

# Quad elements: 5001-5060 (nL*nH = 60 quads)
# Quad nodes: 29-105 (77 nodes in (nH+1)x(nL+1) grid)

# Beam integration (dispBeamColumn requires beamIntegration in OpenSeesPy)
INTEG_COL  = 1
INTEG_BEAM = 2

# Geometric transformations
TRANS_COL  = 1
TRANS_BEAM = 2

# -- 3. PARAMETERS ----------------------------------------------------------------
# --- Geometry ---
L_wall = 1032.0              # wall width [mm]
H_wall = 3660.0              # wall height [mm]
t_wall = 102.0               # wall thickness [mm]
nL = 6                       # horizontal divisions
nH = 10                      # vertical divisions
deltL = L_wall / nL          # horizontal mesh size [mm]
deltH = H_wall / nH          # vertical mesh size [mm]
n_ip = 5                     # integration points

# --- Column section geometry ---
col_width = 153.0            # section width (Z) [mm]
col_depth = 102.0            # section depth (Y) [mm]
col_cover = 19.0             # cover thickness [mm]
As_bar = 71.2                # single bar area [mm^2] (#3 US rebar, 9.5 mm dia)
nf_y = 10                    # core fiber count in Y
nf_z = 20                    # core fiber count in Z
n_bars = 4                   # bars per layer

# Column local coords
cy1 = col_depth / 2.0        # = 51.0  -- half-depth
cz1 = col_width / 2.0        # = 76.5  -- half-width

# --- Concrete02 -- confined core (tag 1) ---
fc_core    = -47.6           # peak compressive stress [MPa]
epsc0_core = -0.0032         # strain at peak stress
fcu_core   = -33.0           # crushing stress [MPa]
epscu_core = -0.015          # strain at crushing
con_lambda = 0.1             # ratio between unloading slope and initial slope
ft_core    = 2.6             # tensile strength [MPa]
Ets_core   = 3000.0          # tension softening stiffness [MPa]

# --- Concrete02 -- cover (tag 2) ---
fc_cover    = -42.8
epsc0_cover = -0.0021
fcu_cover   = -8.56
epscu_cover = -0.02
ft_cover    = 2.1
Ets_cover   = 3000.0

# --- Steel02 -- longitudinal rebar (tag 3) ---
Fy_rebar  = 395.2            # yield stress [MPa]
E_rebar   = 200000.0         # elastic modulus [MPa]
b_rebar   = 0.0185           # strain hardening ratio
R0_rebar  = 18.0             # transition parameter
cR1_rebar = 0.925            # transition parameter
cR2_rebar = 0.15             # transition parameter

# --- Elastic beam section (tag 2) -- essentially rigid spider links ---
E_beam  = 1e10               # [MPa]
A_beam  = 100                # [mm^2]
I_beam  = 1e10               # [mm^4]

# --- Wall reinforcement steel (tags 11, 12) ---
wfy    = 336.0               # yield stress [MPa]
wE     = 200000.0            # elastic modulus [MPa]
w_b    = 0.035               # strain hardening ratio (for smeared steel)
w_R0   = 18.0
w_cR1  = 0.925
w_cR2  = 0.15
wrou1  = 0.0024              # reinforcement ratio
wrou2  = 0.0024

# --- Wall concrete zones -- SmearedConcrete (tags 13-16) ---
wfc_arr = [42.8, 45.7, 40.8, 41.3]  # fc for zones 1-4 [MPa]
wepsc0  = -0.0021                    # strain at peak stress

# --- SmearedCompositePlaneStress parameters ---
scps_rho    = 0.0            # density
scps_theta1 = 0.0            # reinforcement angle 1 [rad]
scps_theta2 = 0.5 * np.pi    # reinforcement angle 2 [rad] (orthogonal)
scps_eps0   = 0.002          # reference strain
scps_k1     = 0.25           # crack parameter
scps_k2     = 1500.0         # crack parameter

# --- Loading ---
N_gravity = 378000.0         # axial load at control node [N] (= 378 kN)
P_ref     = 1000.0           # reference lateral load [N]

# --- Cyclic pushover ---
peak_displacements = [3.788, 9.986, 16.41, 24.22, 38.91, 54.52, 71.05, 71.28]  # [mm]
Dincr_static = 0.02          # displacement increment [mm]
cycle_type = "Full"          # 0 -> +peak -> 0 -> -peak -> 0

# --- Control node position ---
control_x = L_wall / 2.0           # = 516.0
control_y = H_wall + 305.0 / 2.0   # = 3812.5


# -- 4. HELPER FUNCTIONS ----------------------------------------------------------

def _generate_peaks(Dmax: float, Dincr: float, cycle_type: str) -> list[float]:
    """Generate displacement target list for cyclic pushover.

    Ported from GeneratePeaks.tcl (Silvia Mazzoni, 2006).

    Args:
        Dmax: Peak displacement (positive or negative).
        Dincr: Displacement increment.
        cycle_type: "Full" (0->+->0->-->0), "HalfCycle" (0->+->0), "Push" (0->+).

    Returns:
        List of absolute displacement targets.
    """
    dx = -Dincr if Dmax < 0 else Dincr
    n_steps_peak = int(abs(Dmax) / Dincr)

    targets = []
    disp = 0.0

    # 0 -> +peak
    for _ in range(n_steps_peak):
        disp += dx
        targets.append(disp)

    if cycle_type != "Push":
        # +peak -> 0
        for _ in range(n_steps_peak):
            disp -= dx
            targets.append(disp)

        if cycle_type != "HalfCycle":
            # 0 -> -peak
            for _ in range(n_steps_peak):
                disp -= dx
                targets.append(disp)

            # -peak -> 0
            for _ in range(n_steps_peak):
                disp += dx
                targets.append(disp)

    return targets


def _build_rc_section() -> None:
    """Build column fiber section: core + 4 cover patches + 2 rebar layers.

    Uses opstool's decorated section/patch/layer wrappers so that
    plot_fiber_sec_cmds() can read back the geometry later.
    """
    from opstool.pre.section import section as _sec, patch as _pch, layer as _lyr

    _sec("Fiber", SEC_COL_FIBER)

    # Confined core: rect [cover-cy1, cover-cz1] to [cy1-cover, cz1-cover]
    _pch("rect", MAT_CONCRETE_CORE, nf_z, nf_y,
         col_cover - cy1, col_cover - cz1,
         cy1 - col_cover, cz1 - col_cover)

    # Cover: 4 rectangular patches (top, bottom, left, right)
    _pch("rect", MAT_CONCRETE_COVER, nf_z, 1,
         -cy1, cz1 - col_cover, cy1, cz1)
    _pch("rect", MAT_CONCRETE_COVER, nf_z, 1,
         -cy1, -cz1, cy1, col_cover - cz1)
    _pch("rect", MAT_CONCRETE_COVER, 1, nf_y,
         -cy1, col_cover - cz1, col_cover - cy1, cz1 - col_cover)
    _pch("rect", MAT_CONCRETE_COVER, 1, nf_y,
         cy1 - col_cover, col_cover - cz1, cy1, cz1 - col_cover)

    # Rebar layers: top and bottom (4 bars each)
    _lyr("straight", MAT_STEEL_REBAR, n_bars, As_bar,
         col_cover - cy1, cz1 - col_cover,
         cy1 - col_cover, cz1 - col_cover)
    _lyr("straight", MAT_STEEL_REBAR, n_bars, As_bar,
         col_cover - cy1, col_cover - cz1,
         cy1 - col_cover, col_cover - cz1)


def _vis_fiber_section(output_dir: Path) -> None:
    """Plot and save the column fiber section mesh."""
    if _headless():
        return
    print("Plotting fiber section mesh ...")
    import matplotlib
    _prev = matplotlib.get_backend()
    matplotlib.use("Agg")
    import warnings
    import matplotlib.pyplot as plt
    from opstool.pre.section import plot_fiber_sec_cmds

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*non-interactive.*")
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        plot_fiber_sec_cmds(
            SEC_COL_FIBER,
            title=f"Chapter5 -- Column Fiber Section\n"
                  f"{col_width}x{col_depth} mm, {nf_z}x{nf_y} core mesh, "
                  f"{n_bars} bars/layer (#3, As={As_bar} mm^2)",
            title_size=12,
        )
    plt.savefig(
        str(output_dir / "vis_01_fiber_section.png"),
        dpi=150, bbox_inches="tight",
    )
    plt.close()
    matplotlib.use(_prev)


# -- 5. BUILD FRAME MODEL (ndf=3) -------------------------------------------------

# Node index variables (matching Tcl numbering)
_L_side_first = 0   # will be set to 1
_R_side_first = 0
_Top_beam_first = 0
_ControlNode = 0


def _build_frame_model() -> None:
    """Phase 1: Build frame model with ndf=3 (UX, UY, RZ).

    Creates:
    - Left column nodes: 1-11 (x=0, y=0..H_wall)
    - Right column nodes: 12-22 (x=L_wall, y=0..H_wall)
    - Top beam nodes: 23-27 (y=H_wall, interior x positions)
    - Control node: 28 (x=L_wall/2, y=H_wall+152.5)
    - dispBeamColumn elements for columns and spider-beams
    """
    global _L_side_first, _R_side_first, _Top_beam_first, _ControlNode

    ops.model("basic", "-ndm", 2, "-ndf", 3)

    # --- Materials ---
    ops.uniaxialMaterial("Concrete02", MAT_CONCRETE_CORE,
                         fc_core, epsc0_core, fcu_core, epscu_core,
                         con_lambda, ft_core, Ets_core)
    ops.uniaxialMaterial("Concrete02", MAT_CONCRETE_COVER,
                         fc_cover, epsc0_cover, fcu_cover, epscu_cover,
                         con_lambda, ft_cover, Ets_cover)
    ops.uniaxialMaterial("Steel02", MAT_STEEL_REBAR,
                         Fy_rebar, E_rebar, b_rebar, R0_rebar, cR1_rebar, cR2_rebar)

    # --- Sections ---
    _build_rc_section()
    ops.section("Elastic", SEC_BEAM_ELAST, E_beam, A_beam, I_beam)

    # --- Geometric transformations ---
    ops.geomTransf("Linear", TRANS_COL)
    ops.geomTransf("Linear", TRANS_BEAM)

    # --- Beam integration (required for dispBeamColumn in OpenSeesPy) ---
    ops.beamIntegration("Legendre", INTEG_COL, SEC_COL_FIBER, n_ip)
    ops.beamIntegration("Legendre", INTEG_BEAM, SEC_BEAM_ELAST, n_ip)

    # --- Left column nodes (index 0..nH -> tags 1..11) ---
    nodeID = 0
    _L_side_first = nodeID + 1   # = 1
    for i in range(nH + 1):
        nodeID += 1
        ops.node(nodeID, 0.0, i * deltH)

    # --- Right column nodes (tags 12..22) ---
    _R_side_first = nodeID + 1   # = 12
    for i in range(nH + 1):
        nodeID += 1
        ops.node(nodeID, L_wall, i * deltH)

    # --- Top beam interior nodes (tags 23-27) ---
    _Top_beam_first = nodeID + 1  # = 23
    for j in range(1, nL):  # j = 1..5
        nodeID += 1
        ops.node(nodeID, j * deltL, H_wall)

    # --- Base fixity ---
    ops.fixY(0.0, 1, 1, 1)  # all nodes at y=0 fixed in DOFs 1,2,3

    # --- Control node (tag 28) ---
    _ControlNode = nodeID + 1  # = 28
    nodeID += 1
    ops.node(_ControlNode, control_x, control_y)

    # --- Column elements ---
    for i in range(1, nH + 1):
        # Left column: elements 1001-1010
        ops.element("dispBeamColumn", 1000 + i,
                    _L_side_first + i - 1, _L_side_first + i,
                    TRANS_COL, INTEG_COL)
        # Right column: elements 2001-2010
        ops.element("dispBeamColumn", 2000 + i,
                    _R_side_first + i - 1, _R_side_first + i,
                    TRANS_COL, INTEG_COL)

    # --- Top beam spider elements ---
    # ControlNode -> left column top
    ops.element("dispBeamColumn", 3000,
                _ControlNode, _L_side_first + nH,
                TRANS_BEAM, INTEG_BEAM)
    # ControlNode -> top beam interior nodes (j=1..5)
    for j in range(1, nL):
        ops.element("dispBeamColumn", 3000 + j,
                    _ControlNode, _Top_beam_first + j - 1,
                    TRANS_BEAM, INTEG_BEAM)
    # ControlNode -> right column top
    ops.element("dispBeamColumn", 3000 + nL,
                _ControlNode, _R_side_first + nH,
                TRANS_BEAM, INTEG_BEAM)

    print("Frame model built (ndf=3).")


# -- 6. BUILD QUAD MODEL (ndf=2) --------------------------------------------------

_quad_first = 0   # first quad node tag


def _build_quad_model() -> None:
    """Phase 2: Build quad wall model with ndf=2 (UX, UY).

    Creates:
    - Quad grid nodes: tags 29-105 ((nH+1)*(nL+1) = 77 nodes)
    - Quad elements: tags 5001..5060 (nL*nH = 60 elements)
    - SmearedCompositePlaneStress nDMaterials
    """
    global _quad_first

    # Switch model builder to ndf=2 for new nodes
    ops.model("basic", "-ndm", 2, "-ndf", 2)

    # --- Wall materials ---
    # Smeared reinforcement steel (standard Steel02 -- always available)
    ops.uniaxialMaterial("Steel02", MAT_STEEL_SMEAR_X,
                         wfy, wE, w_b, w_R0, w_cR1, w_cR2)
    ops.uniaxialMaterial("Steel02", MAT_STEEL_SMEAR_Y,
                         wfy, wE, w_b, w_R0, w_cR1, w_cR2)

    # SmearedConcrete + SmearedCompositePlaneStress are RESEARCH-FORK materials.
    # Check availability with a clear message if not compiled into OpenSeesPy.
    _MISSING_MSG = (
        "\n  ERROR: This model requires a custom OpenSeesPy build with\n"
        "  'SmearedConcrete' (uniaxialMaterial) and 'SmearedCompositePlaneStress'\n"
        "  (nDMaterial). These are research-fork materials from the Thomsen &\n"
        "  Wallace (2004) RC wall modeling framework and are NOT included in\n"
        "  standard OpenSeesPy from PyPI.\n"
        "\n  The frame model (ndf=3, fiber-section columns) was built successfully.\n"
        "  To run the full model, use your custom OpenSees build that includes\n"
        "  these materials (same build used for the original RW2_2.tcl).\n"
    )

    # SmearedConcrete for 4 wall zones
    for tag, fc in zip([MAT_CONC_W1, MAT_CONC_W2, MAT_CONC_W3, MAT_CONC_W4],
                       wfc_arr):
        try:
            ops.uniaxialMaterial("SmearedConcrete", tag, -fc, wepsc0)
        except Exception:
            print(_MISSING_MSG)
            raise

    # SmearedCompositePlaneStress nDMaterials
    # Signature: matTag, rho, s1, s2, c1, c2, c3, c4, theta1, theta2,
    #             rou1, rou2, fc, fy, Es, eps0, k1, k2
    for nd_tag, conc_tag, fc in zip(
        [MAT_ND_W1, MAT_ND_W2, MAT_ND_W3, MAT_ND_W4],
        [MAT_CONC_W1, MAT_CONC_W2, MAT_CONC_W3, MAT_CONC_W4],
        wfc_arr,
    ):
        try:
            ops.nDMaterial("SmearedCompositePlaneStress", nd_tag,
                           scps_rho,
                           MAT_STEEL_SMEAR_X, MAT_STEEL_SMEAR_Y,
                           conc_tag, conc_tag, conc_tag, conc_tag,
                           scps_theta1, scps_theta2,
                           wrou1, wrou2,
                           fc, wfy, wE,
                           scps_eps0, scps_k1, scps_k2)
        except Exception:
            print(_MISSING_MSG)
            raise

    # --- Quad nodes ---
    _quad_first = 29  # quadNodeID = nodeID + 1 after frame (28+1)
    nodeID = _quad_first - 1
    for i in range(nH + 1):       # 0..10
        for j in range(nL + 1):   # 0..6
            nodeID += 1
            ops.node(nodeID, j * deltL, i * deltH)

    # Base fixity for quad nodes
    ops.fixY(0.0, 1, 1)

    # --- Quad elements ---
    for i in range(1, nH + 1):
        for j in range(1, nL + 1):
            ele_tag = 5000 + (i - 1) * nL + j
            # Nodes: bottom-left, bottom-right, top-right, top-left
            n_bl = _quad_first + (i - 1) * (nL + 1) + j - 1
            n_br = _quad_first + (i - 1) * (nL + 1) + j
            n_tr = _quad_first + i * (nL + 1) + j
            n_tl = _quad_first + i * (nL + 1) + j - 1
            ops.element("quad", ele_tag, n_bl, n_br, n_tr, n_tl,
                        t_wall, "PlaneStress", MAT_ND_W1)

    print("Quad model built (ndf=2).")


# -- 7. TIE MODELS ----------------------------------------------------------------

def _tie_models() -> None:
    """Phase 3: Tie frame nodes to coincident quad nodes via equalDOF (DOFs 1,2).

    Left column, right column, and top beam frame nodes (ndf=3) are tied
    to the corresponding quad mesh nodes (ndf=2) in translational DOFs.
    """
    # Left column: equalDOF (L_side_first+i) -> (quad_first+(nL+1)*i)  DOFs 1,2
    for i in range(1, nH + 1):
        ops.equalDOF(_L_side_first + i,
                     _quad_first + (nL + 1) * i,
                     1, 2)

    # Right column: equalDOF (R_side_first+i) -> (quad_first+(nL+1)*i+nL)  DOFs 1,2
    for i in range(1, nH + 1):
        ops.equalDOF(_R_side_first + i,
                     _quad_first + (nL + 1) * i + nL,
                     1, 2)

    # Top beam interior: equalDOF (Top_beam_first+j-1) -> (quad_first+(nL+1)*nH+j)
    for j in range(1, nL):
        ops.equalDOF(_Top_beam_first + j - 1,
                     _quad_first + (nL + 1) * nH + j,
                     1, 2)

    print("Models tied via equalDOF.")


# -- 8. RECORDERS -----------------------------------------------------------------

def _setup_recorders(output_dir: Path) -> None:
    """Set up ODB-compatible recorders (displacement + reaction + element strains).

    Recorder tags match the original Tcl recorders for traceability.
    """
    # Control node displacement
    ops.recorder("Node", "-file", str(output_dir / "disp.out"),
                 "-time", "-node", _ControlNode, "-dof", 1, "disp")

    # Region: quad base nodes + left/right column base
    quad_last_base = _quad_first + nL  # last base quad node
    ops.region(1, "-nodeRange", _quad_first, quad_last_base,
               "-node", _L_side_first, _R_side_first)
    ops.recorder("Node", "-file", str(output_dir / "force.out"),
                 "-time", "-region", 1, "-dof", 1, "reaction")

    # Displacement profile along left column
    ops.recorder("Node", "-file", str(output_dir / "disprofile.out"),
                 "-time",
                 "-node", *[_L_side_first + d for d in [2, 4, 6, 8]],
                 "-dof", 1, "disp")

    # Quad element strain recorders (material gauges 1-4)
    quad_first_ele = 5001
    quad_last_ele = 5000 + nL * nH
    for p in range(1, 5):
        ops.recorder("Element", "-file",
                     str(output_dir / f"quadStrainP{p}.out"),
                     "-time", "-eleRange", quad_first_ele, quad_last_ele,
                     "material", str(p), "strain")

    # Left column fiber strain recorders at extreme fiber (-cy1, cz1)
    col_first_ele = 1001
    col_last_ele = 1000 + nH
    for s in range(1, 6):
        ops.recorder("Element", "-file",
                     str(output_dir / f"LColS{s}P1.out"),
                     "-time", "-eleRange", col_first_ele, col_last_ele,
                     "section", str(s), "fiber",
                     -cy1, cz1, "strain")
        ops.recorder("Element", "-file",
                     str(output_dir / f"LColS{s}P2.out"),
                     "-time", "-eleRange", col_first_ele, col_last_ele,
                     "section", str(s), "fiber",
                     cy1, cz1, "strain")

    # Right column fiber strain recorders
    rcol_first_ele = 2001
    rcol_last_ele = 2000 + nH
    for s in range(1, 6):
        ops.recorder("Element", "-file",
                     str(output_dir / f"RColS{s}P1.out"),
                     "-time", "-eleRange", rcol_first_ele, rcol_last_ele,
                     "section", str(s), "fiber",
                     -cy1, cz1, "strain")
        ops.recorder("Element", "-file",
                     str(output_dir / f"RColS{s}P2.out"),
                     "-time", "-eleRange", rcol_first_ele, rcol_last_ele,
                     "section", str(s), "fiber",
                     cy1, cz1, "strain")


# -- 9. OUTPUT DATABASE -----------------------------------------------------------

def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise ODB after model is fully built."""
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=1)
    odb.save_model_data()
    return odb


# -- 10. ANALYSIS -----------------------------------------------------------------

# Global EDP trackers
_peak_disp = 0.0
_peak_shear = 0.0
_disp_history: list[tuple[float, float]] = []  # (disp, force) pairs
_collapse = False


def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10) -> None:
    """Apply gravity (378 kN) via load-controlled static analysis.

    Uses KrylovNewton (matching Tcl), then loadConst to freeze gravity.
    """
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(_ControlNode, 0.0, -N_gravity, 0.0)

    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-3, 100)
    ops.algorithm("KrylovNewton")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.analysis("Static")

    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()
    print("Gravity applied and frozen.")


def _solve_one_step(d_incr: float) -> bool:
    """Attempt one displacement-controlled step with 5-tier algorithm fallback.

    Returns True if converged, False otherwise.
    """
    ops.integrator("DisplacementControl", _ControlNode, 1, d_incr)
    ops.analysis("Static")

    fallback_chain = [
        ("Newton -initial", "Newton", "-initial", 50),
        ("Broyden 8", "Broyden", 8, 200),
        ("NewtonLineSearch 0.8", "NewtonLineSearch", 0.8, 200),
        ("KrylovNewton", "KrylovNewton", None, 200),
    ]

    # Tier 1: default Newton
    ok = ops.analyze(1)
    if ok == 0:
        return True

    # Tiers 2-5: fallback chain
    for name, algo, arg, max_iter in fallback_chain:
        print(f"  Trying {name} ...")
        ops.test("NormDispIncr", 1.0e-3, max_iter)
        if arg is not None:
            ops.algorithm(algo, arg)
        else:
            ops.algorithm(algo)
        ok = ops.analyze(1)
        # Reset algorithm and test for next attempt/step
        ops.algorithm("Newton")
        ops.test("NormDispIncr", 1.0e-3, 200)
        if ok == 0:
            return True

    return False


def run_cyclic_pushover(odb: "opst.post.CreateODB") -> None:
    """Execute cyclic displacement-controlled pushover.

    For each peak amplitude, generates Full-cycle displacement targets
    and solves step-by-step with algorithm fallback.
    """
    global _peak_disp, _peak_shear, _disp_history, _collapse

    # Reference lateral load for DisplacementControl integrator
    ops.timeSeries("Linear", 2)
    ops.pattern("Plain", 2, 2)
    ops.load(_ControlNode, P_ref, 0.0, 0.0)

    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-3, 200)
    ops.algorithm("Newton")

    step_count = 0

    for peak_idx, Dmax in enumerate(peak_displacements):
        print(f"\nPeak {peak_idx + 1}/{len(peak_displacements)}: "
              f"Dmax = {Dmax:.3f} mm")

        targets = _generate_peaks(Dmax, Dincr_static, cycle_type)
        d0 = 0.0

        for d1 in targets:
            d_incr = d1 - d0
            ok = _solve_one_step(d_incr)
            if not ok:
                print(f"  FAILED to converge at disp = {d1:.4f} mm")
                _collapse = True
                break

            step_count += 1
            if step_count % 500 == 0:
                odb.fetch_response_step()

            # Track EDPs
            current_disp = ops.nodeDisp(_ControlNode, 1)
            current_force = ops.nodeReaction(_ControlNode, 1)
            _peak_disp = max(_peak_disp, abs(current_disp))
            _peak_shear = max(_peak_shear, abs(current_force))
            _disp_history.append((current_disp, current_force))

            d0 = d1

        if _collapse:
            break

    # Final ODB fetch
    odb.fetch_response_step()
    print(f"\nCyclic pushover complete. {step_count} steps, "
          f"collapse={_collapse}")


# -- 11. POST-PROCESSING ----------------------------------------------------------

def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> dict:
    """Flush ODB, write EDPs to JSON, generate visualizations."""
    odb.save_response()

    drift_ratio = _peak_disp / H_wall

    edp_values = {
        "1-PRD-1":    _peak_disp,
        "1-PID-1":    drift_ratio,
        "1-PFB-1":    _peak_shear,
        "collapse_status": 1 if _collapse else 0,
    }

    import json
    edp_file = output_dir / "EDP.json"
    edp_list = [{"name": k, "value": v} for k, v in edp_values.items()]
    with open(edp_file, "w") as f:
        json.dump({"EDP": edp_list}, f, indent=2)
    print(f"EDP file written: {edp_file}")

    # Force-displacement hysteresis
    if _disp_history and not _headless():
        import matplotlib
        _prev = matplotlib.get_backend()
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        disps, forces = zip(*_disp_history)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(disps, [f / 1000.0 for f in forces],
                linewidth=0.5, color="steelblue")
        ax.set_xlabel("Lateral Displacement [mm]")
        ax.set_ylabel("Lateral Force [kN]")
        ax.set_title("Chapter5 -- RW2-2 Cyclic Pushover\n"
                     f"Peak drift: {drift_ratio * 100:.2f}%")
        ax.axhline(y=0, color="gray", linewidth=0.5)
        ax.axvline(x=0, color="gray", linewidth=0.5)
        ax.grid(True, alpha=0.3)
        fig.savefig(str(output_dir / "vis_07_force_disp.png"),
                    dpi=150, bbox_inches="tight")
        plt.close()
        matplotlib.use(_prev)
        print("Force-displacement plot saved.")

    # Deformation visualizations (opstool)
    if not _headless():
        try:
            fig_defo = opst.vis.plotly.plot_nodal_responses(
                odb_tag=1, step="absMax", defo_scale=True,
                resp_type="disp", resp_dof="UX",
            )
            fig_defo.write_html(str(output_dir / "vis_05_deformed_peak.html"))
        except Exception:
            print("Peak deformation view skipped (no valid response steps).")

        try:
            fig_slider = opst.vis.plotly.plot_nodal_responses(
                odb_tag=1, slides=True, defo_scale=True,
                resp_type="disp", resp_dof="UX",
            )
            fig_slider.write_html(str(output_dir / "vis_06_deformed_slider.html"))
        except Exception:
            print("Slider view skipped (not enough response steps).")

    return edp_values


# -- 12. MAIN ---------------------------------------------------------------------

def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Full model build -> gravity -> cyclic pushover -> return ODB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    ops.wipe()

    # Phases 1-3: Build
    _build_frame_model()
    _build_quad_model()
    _tie_models()

    _setup_recorders(output_dir)

    # Pre-analysis visuals
    vis_nodes(output_dir)
    vis_model(output_dir)

    # Fiber section visualization (after frame section is built)
    _vis_fiber_section(output_dir)

    odb = create_odb(output_dir)

    vis_loads(output_dir)

    # Phase 4: Gravity
    print("\nRunning gravity analysis ...")
    run_gravity(odb)

    vis_pre_analysis(output_dir)

    # Phase 5: Cyclic pushover
    print("\nRunning cyclic pushover analysis ...")
    run_cyclic_pushover(odb)

    return odb


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    edps = post_process(odb, output_dir)
    print(f"\nExtracted {len(edps)} EDPs.")
    for k, v in edps.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
