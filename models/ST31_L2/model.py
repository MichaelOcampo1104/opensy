# ── 0. FILE HEADER ──────────────────────────────────────────────────────────────
"""
Model    : ST31_L2 — Underground H-Frame Structure (Cut-and-Cover)
UniqueID : ST31_L2
Author   : <your name>
Date     : 2026-05-12
Purpose  : 2D soil-structure interaction analysis of a cut-and-cover underground
           structure with diaphragm walls and base slab on Winkler spring supports.
Ref      : <paper / standard reference>
Units    : N, mm, MPa
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import _headless

# Compatibility: opstool v0.8.7 uses deprecated np.NAN
np.NAN = np.nan

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────────
# ── Materials
MAT_CONCRETE = 1       # elastic section material (reference only)
MAT_SOIL_1   = 2       # ENT — layer 1  ( 0 m  to  -6 m)
MAT_SOIL_2   = 3       # ENT — layer 2  (-6 m  to -12 m)
MAT_SOIL_3   = 4       # ENT — layer 3  (-12 m to -18 m)
MAT_SOIL_4   = 5       # ENT — layer 4  (-18 m to -24 m)
MAT_SOIL_5   = 6       # ENT — layer 5  (-24 m to -30 m)
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

# ── Left wall nodes (1–31)
NODE_LWALL_TOP  = 1
NODE_LWALL_SLAB = 11      # y = -10 000 mm
NODE_LWALL_BASE = 31      # y = -30 000 mm

# ── Right wall nodes (32–62)
NODE_RWALL_TOP  = 32
NODE_RWALL_SLAB = 42      # y = -10 000 mm
NODE_RWALL_BASE = 62      # y = -30 000 mm

# ── Slab nodes (63–70)
NODE_SLAB_START = 63
NODE_SLAB_END   = 70

# ── Soil node ranges (101–131 left, 132–162 right)
NODE_SOIL_L_START = 101
NODE_SOIL_R_START = 132

# ── Spring element ranges (100–130 left, 200–230 right)
ELE_SPRING_L_START = 100
ELE_SPRING_R_START = 200
ELE_SPRING_S_START = 300 # Range for slab springs

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────────
h_dwall    = 30000.0 * mm
t_dwall    = 1000.0  * mm
t_slab     = 800.0   * mm
l_center   = 9000.0  * mm        # centre-to-centre wall spacing
depth_slab = 10000.0 * mm
elem_size  = 1000.0  * mm

n_ele_wall  = 30
n_ele_slab  = 9 
n_node_wall = n_ele_wall + 1

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
k_soil_1 =    10_000.0   # N/mm   (≈ k_h = 0.01 MPa/mm)
k_soil_2 =    20_000.0   # N/mm
k_soil_3 =    30_000.0   # N/mm
k_soil_4 =    40_000.0   # N/mm
k_soil_5 =    50_000.0   # N/mm
k_v_slab =    40_000.0   # N/mm   (Vertical subgrade modulus × tributary area)

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


# Visualisation helper (opstool v0.8.7 compatible)
def _snapshot_and_render(output_dir: Path, filename: str, **kwargs) -> None:
    """Render model geometry via opstool.vis.plotly.plot_model (v1.0+).

    Returns a plotly Figure; we save it as a self-contained HTML file.
    Keyword args are forwarded to plot_model (e.g. show_node_numbering=True).
    """
    if _headless():
        return

    from opstool.vis.plotly import plot_model

    fig = plot_model(**kwargs)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_dir / filename))
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
    # ── Left wall (x = 0), nodes numbered from top (y = 0) to base (y = -30 000)
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
        # LEFT WALL — soil located on negative global X side
        # Local spring axis points outward toward soil (-X).
        # Wall displacement toward soil activates ENT compression spring.
        ops.element(
            "zeroLength",
            ele_l,
            wall_node_l,
            soil_node_l,
            "-mat", mat_l,
            "-dir", 1,
            "-orient",
            -1, 0, 0,
            0, 1, 0
        )
        wall_node_r = NODE_RWALL_TOP + i
        soil_node_r = NODE_SOIL_R_START + i
        ele_r       = ELE_SPRING_R_START + i
        mat_r       = _soil_mat_for_node(i)

        ops.node(soil_node_r, l_center, y)
        ops.fix(soil_node_r, 1, 1, 1)
        # RIGHT WALL — soil located on positive global X side
        # Local spring axis points outward toward soil (+X).
        # Wall displacement toward soil activates ENT compression spring.
        ops.element(
            "zeroLength",
            ele_r,
            wall_node_r,
            soil_node_r,
            "-mat", mat_r,
            "-dir", 1,
            "-orient",
            1, 0, 0,
            0, 1, 0
        )
    slab_nodes = [NODE_LWALL_SLAB] + list(range(NODE_SLAB_START, NODE_SLAB_END + 1)) + [NODE_RWALL_SLAB]
    ops.uniaxialMaterial("ENT", MAT_SOIL_SLAB, k_v_slab)
    for i, s_node in enumerate(slab_nodes):
            x_coord = ops.nodeCoord(s_node, 1)
            soil_node_s = 200 + i # Unique ID for slab soil nodes
            ele_s       = ELE_SPRING_S_START + i

            # Create fixed soil node below the slab
            ops.node(soil_node_s, x_coord, -depth_slab)
            ops.fix(soil_node_s, 1, 1, 1)

            # Vertical Spring: soil is on negative global Y side
            ops.element(
                "zeroLength",
                ele_s,
                s_node,
                soil_node_s,
                "-mat", MAT_SOIL_SLAB,
                "-dir", 2, # Direction 2 is UY (Vertical)
                "-orient", 0, -1, 0, 1, 0, 0 #
        )

# ── 7V. VISUALISE — NODES ────────────────────────────────────────────────────────
def vis_nodes(output_dir: Path) -> None:
    _snapshot_and_render(output_dir, "vis_01_nodes.html",
                         show_node_numbering=True, show_ele_numbering=False)


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


# ── 9V. VISUALISE — MODEL ────────────────────────────────────────────────────────
def vis_model(output_dir: Path) -> None:
    """V2 — Full undeformed model geometry (nodes + members + fixities)."""
    _snapshot_and_render(output_dir, "vis_02_model.html",
                         show_node_numbering=False, show_ele_numbering=True)


# ── 11. LOADING ──────────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Apply 10 kPa uniform gravity load on base slab (downward)."""
    # 10 kPa = 0.01 N/mm²; for 1 000 mm strip → 10 N/mm
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)

    # Slab elements: tags 61 … 69  (= 2 × n_ele_wall + 1 … 2 × n_ele_wall + n_ele_slab)
    for i in range(n_ele_slab):
        ele_tag = 2 * n_ele_wall + i + 1
        ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform", -10.0)


# Load-case 1: 15 kPa earth pressure (both walls)
def define_lateral_loads() -> None:
    """Define lateral earth pressure on both diaphragm walls.

    Load Case 1 — Earth pressure: 15 kPa uniform full height.
    (Load Case 2 — Water pressure: to be added.)
    """
    # ── Load Case 1: Earth pressure ──
    # 15 kPa = 0.015 N/mm²; for 1 000 mm strip → 15 N/mm
    ops.timeSeries("Linear", 2)
    ops.pattern("Plain", 2, 2)

    # Left wall (elements 1 … 30): soil outside pushes right → +local y
    for i in range(n_ele_wall):
        ops.eleLoad("-ele", i + 1, "-type", "-beamUniform", 15.0)

    # Right wall (elements 31 … 60): soil outside pushes left → −local y
    for i in range(n_ele_wall):
        ops.eleLoad("-ele", n_ele_wall + i + 1, "-type", "-beamUniform", -15.0)


def define_water_pressure() -> None:
    """Apply hydrostatic water pressure on both diaphragm walls.

    Assumes water table at ground surface (y = 0).  Triangular distribution
    with depth, acting inward on each wall.

    Load Case 2 — uses pattern tag 3.
    """
    ops.timeSeries("Linear", 3)
    ops.pattern("Plain", 3, 3)

    for i in range(n_ele_wall):
        d_mid = (i + 0.5) * elem_size        # mm — mid-height of this element
        w = gamma_w * d_mid * b_strip        # N/mm — line load for 1 m strip

        # Left wall: water pushes right → +local y
        ops.eleLoad("-ele", i + 1, "-type", "-beamUniform", w)
        # Right wall: water pushes left → −local y
        ops.eleLoad("-ele", n_ele_wall + i + 1, "-type", "-beamUniform", -w)


# ── 10. OUTPUT DATABASE (ODB) ───────────────────────────────────────────────────
def create_odb(odb_tag: int = 1) -> "opst.post.CreateODB":
    """Initialise an opstool ODB and save model data snapshot.

    Call this after all nodes and elements are defined and before the first
    analysis step.

    Args:
        odb_tag: Integer tag identifying this load-case ODB (default 1).

    Returns:
        Configured CreateODB instance ready to collect responses.
    """
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
    )
    odb.save_model_data()
    return odb


# ── 11V. VISUALISE — LOADS ───────────────────────────────────────────────────────
def vis_loads(output_dir: Path) -> None:
    """V3 — Applied load vectors (placeholder until loads are defined)."""
    _snapshot_and_render(output_dir, "vis_03_loads.html",
                         show_ele_loads=True, show_node_numbering=False, show_ele_numbering=False)


# ── 11C. PRE-ANALYSIS CHECK ──────────────────────────────────────────────────────
def vis_pre_analysis(output_dir: Path) -> None:
    """V4 — Full model + loads — final sanity check before solver."""
    _snapshot_and_render(output_dir, "vis_04_pre_analysis.html",
                         show_ele_loads=True, show_node_numbering=True, show_ele_numbering=True)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────────
# Gravity — load-controlled static
def run_gravity(
    odb: "opst.post.CreateODB",
    n_steps: int = 10,
    ctrl_node: int = NODE_SLAB_START,
    ctrl_dof: int = 2,
) -> None:
    """Apply gravity loads incrementally using SmartAnalyze (Static).

    Args:
        odb: Active CreateODB instance; fetch_response_step() called each step.
        n_steps: Number of equal load increments (default 10).
        ctrl_node: Tag of the control node used by SmartAnalyze (default slab start).
        ctrl_dof: DOF direction for convergence monitoring (default 2 = UY).
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / n_steps)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30],
        minStep=1e-12,
    )
    protocol = [1.0]
    segs = analysis.static_split(protocol, maxStep=1.0 / n_steps)
    for seg in segs:
        analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
        odb.fetch_response_step()
    analysis.close()
    ops.loadConst("-time", 0.0)   # freeze gravity, reset pseudo-time


# Lateral — load-controlled static (pattern defined after loadConst)
def run_lateral_case(
    odb: "opst.post.CreateODB",
    pattern_tag: int,
    n_steps: int = 10,
    ctrl_node: int = NODE_LWALL_SLAB,
    ctrl_dof: int = 1,
) -> None:
    """Apply a lateral load case (pattern defined after loadConst).

    The lateral pattern (2 = earth, 3 = water) must already be defined in the
    model.  Because it was created after ops.loadConst(), its Linear time series
    responds to pseudo-time while the frozen gravity loads stay constant.

    Args:
        odb: Active CreateODB instance; fetch_response_step() called each step.
        pattern_tag: Tag of the lateral load pattern (2 or 3).
        n_steps: Number of load increments (default 10).
        ctrl_node: Convergence-monitoring node (default NODE_LWALL_SLAB).
        ctrl_dof: Convergence-monitoring DOF (1 = UX, default).
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
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


def run_analysis(
    output_dir: Path,
    lateral_case: int = 1,
) -> "opst.post.CreateODB":
    """Build model, run gravity + lateral case, return populated ODB.

    Two-phase approach:
      1. Gravity loads (pattern 1) — load-controlled, then frozen.
      2. Lateral pattern defined AFTER freeze so it alone scales with pseudo-time.

    Args:
        output_dir: Folder for output files.
        lateral_case: 1 = earth pressure (pattern 2), 2 = water pressure (pattern 3).

    Returns:
        CreateODB with all response steps collected.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    # ── Build ──
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)                           # V1
    define_elements()
    vis_model(output_dir)                           # V2
    odb = create_odb(odb_tag=1)                     # ODB after full model definition

    # ── Phase 1: Gravity ──
    define_gravity_loads()                          # pattern 1
    run_gravity(odb)                                # gravity → 100 %, then frozen

    # ── Phase 2: Lateral (defined AFTER loadConst so TS responds to time) ──
    if lateral_case == 1:
        define_lateral_loads()                      # earth pressure → pattern 2
    else:
        define_water_pressure()                     # water pressure → pattern 3

    vis_loads(output_dir)                           # V3 — all loads shown
    vis_pre_analysis(output_dir)                    # V4 — final sanity check

    run_lateral_case(odb, pattern_tag=lateral_case + 1)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and render deformed-shape HTML.

    Args:
        odb: Populated CreateODB returned by run_analysis().
        output_dir: Folder where ODB and HTML files are written.
    """
    odb.save_response()   # write all accumulated responses to output/ as .nc / .h5
    if not _headless():
        fig_defo = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, resp_type="disp", resp_dof="UX",
        )
        fig_defo.write_html(str(output_dir / "vis_05_deformed.html"))


# ── 14. MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ST31_L2 — Underground H-Frame")
    parser.add_argument(
        "--case", type=int, choices=[1, 2], default=1,
        help="Lateral load case: 1 = earth pressure, 2 = water pressure (default 1)",
    )
    args = parser.parse_args()

    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir, lateral_case=args.case)
    post_process(odb, output_dir)
    print(
        f"ST31_L2 case {args.case} analysis complete. "
        f"Open output/vis_05_deformed.html to view results."
    )
