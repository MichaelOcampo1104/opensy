# ── 0. FILE HEADER ──────────────────────────────────────────────────────────────
"""
Model    : ST31_L3 — Underground Box-with-Leg-Frame Structure (Cut-and-Cover)
           Steel strut variant — RC top slab replaced by axial-only steel strut.
UniqueID : ST31_L3
Author   : Michael Ocampo
Date     : 2026-05-13
Purpose  : 2D soil-structure interaction analysis of a cut-and-cover underground
           structure with diaphragm walls and base slab on Winkler spring supports.
           The top slab is modelled as an axial-only steel strut (corotTruss) with
           an equivalent axial stiffness of 1.36e6 kN/m (= 1 360 N/mm per 1 m strip).
Ref      : <paper / standard reference>
Units    : N, mm, MPa

Key difference from ST31_L1
───────────────────────────
  L1 : RC top slab  → dispBeamColumn (SEC_SLAB, bending + axial)
  L3 : Steel strut  → corotTruss     (axial only, k = EA/L = 1 360 N/mm)
       No top-slab gravity load (strut carries no transverse load).
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
from vis_utils import vis_nodes, vis_model, vis_loads, vis_pre_analysis, _headless

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────────
# ── Materials
MAT_CONCRETE  = 1       # elastic section material
MAT_SOIL_1    = 2       # ENT — layer 1  ( 0 m  to  -6 m)
MAT_SOIL_2    = 3       # ENT — layer 2  (-6 m  to -12 m)
MAT_SOIL_3    = 4       # ENT — layer 3  (-12 m to -18 m)
MAT_SOIL_4    = 5       # ENT — layer 4  (-18 m to -24 m)
MAT_SOIL_5    = 6       # ENT — layer 5  (-24 m to -32 m)
MAT_SOIL_SLAB = 7       # Vertical subgrade reaction for the base slab
MAT_STRUT     = 8       # Elastic uniaxial — steel top strut (axial only)

# ── Sections  (top slab removed; strut uses uniaxialMaterial directly)
SEC_DWALL     = 1
SEC_SLAB      = 2       # base slab only

# ── Beam integrations
INT_DWALL     = 1
INT_SLAB      = 2       # base slab only

# ── Geometric transformations
TRANSF_DWALL  = 1
TRANSF_SLAB   = 2       # base slab only

# ── Element partition counts
n_ele_wall   = 32
n_ele_slab   = 9
n_node_slab  = n_ele_slab + 1
n_node_wall  = n_ele_wall + 1   # 33

# ── Left wall nodes (1–33)
NODE_LWALL_TOP       = 1
NODE_LWALL_TOP_SLAB  = 3    # y = -2 000 mm  (strut connection)
NODE_LWALL_SLAB      = 11   # y = -10 000 mm (base slab connection)
NODE_LWALL_BASE      = 33   # y = -32 000 mm

# ── Right wall nodes (34–66)
NODE_RWALL_TOP       = 34
NODE_RWALL_TOP_SLAB  = 36   # y = -2 000 mm  (strut connection)
NODE_RWALL_SLAB      = 44   # y = -10 000 mm (base slab connection)
NODE_RWALL_BASE      = 66   # y = -32 000 mm

# ── Base slab interior nodes (67–74)
NODE_SLAB_START      = 67
NODE_SLAB_END        = NODE_SLAB_START + n_ele_slab - 2   # 74

# NOTE: No interior top-slab nodes in L3.
#       The strut is a SINGLE corotTruss element connecting
#       NODE_LWALL_TOP_SLAB (3) directly to NODE_RWALL_TOP_SLAB (36).

# ── Soil node ranges (101–133 left, 134–166 right)
NODE_SOIL_L_START    = 101
NODE_SOIL_R_START    = 101 + n_node_wall   # 134
NODE_SOIL_S_START    = 300

# ── Spring element ranges
ELE_SPRING_L_START   = 100
ELE_SPRING_R_START   = 200
ELE_SPRING_S_START   = 300

# ── Strut element tag
ELE_STRUT            = 400

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────────
h_dwall        = 32_000.0 * mm
t_dwall        =  1_000.0 * mm
t_slab         =    800.0 * mm
l_center       =  9_000.0 * mm       # centre-to-centre wall spacing
depth_slab     = 10_000.0 * mm
depth_top_slab =  2_000.0 * mm
elem_size      =  1_000.0 * mm

# ── Concrete properties
fc = 40.0 * MPa
Ec = 4700.0 * (fc / MPa) ** 0.5 * MPa

# ── Cross-section properties (per 1 000 mm strip)
b_strip = 1_000.0 * mm
A_dwall = b_strip * t_dwall
I_dwall = b_strip * t_dwall ** 3 / 12.0
A_slab  = b_strip * t_slab
I_slab  = b_strip * t_slab ** 3 / 12.0

# ── Steel strut — axial stiffness
#   k_strut = EA / L = 1.36e6 kN/m = 1 360 N/mm
#   The corotTruss element needs EA directly; L = l_center = 9 000 mm
#   → EA = k_strut × L = 1 360 N/mm × 9 000 mm = 12 240 000 N  (= 12 240 kN)
k_strut = 1_360.0         # N/mm  (1.36e6 kN/m converted to N/mm)
EA_strut = k_strut * l_center   # N  (EA for the corotTruss element)

# ── Soil spring stiffnesses (k_h × tributary area, 1 000 mm strip)
k_soil_1  =  10_000.0 * N / mm
k_soil_2  =  20_000.0 * N / mm
k_soil_3  =  30_000.0 * N / mm
k_soil_4  =  40_000.0 * N / mm
k_soil_5  =  50_000.0 * N / mm
k_v_slab  =  40_000.0 * N / mm

# ── Physical constants
gamma_w = 9.81e-6   # N/mm³


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


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Compression-only Winkler spring materials (ENT) + elastic strut material."""
    ops.uniaxialMaterial("ENT",     MAT_SOIL_1, k_soil_1)
    ops.uniaxialMaterial("ENT",     MAT_SOIL_2, k_soil_2)
    ops.uniaxialMaterial("ENT",     MAT_SOIL_3, k_soil_3)
    ops.uniaxialMaterial("ENT",     MAT_SOIL_4, k_soil_4)
    ops.uniaxialMaterial("ENT",     MAT_SOIL_5, k_soil_5)
    # Steel strut: elastic (tension + compression), stiffness = EA (corotTruss uses EA)
    ops.uniaxialMaterial("Elastic", MAT_STRUT,  EA_strut)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────────
def define_sections() -> None:
    """Define diaphragm wall and base slab sections only (no top slab section)."""
    ops.section("Elastic", SEC_DWALL, Ec, A_dwall, I_dwall)
    ops.section("Elastic", SEC_SLAB,  Ec, A_slab,  I_slab)

    ops.beamIntegration("Lobatto", INT_DWALL, SEC_DWALL, 5)
    ops.beamIntegration("Lobatto", INT_SLAB,  SEC_SLAB,  5)

    ops.geomTransf("PDelta",  TRANSF_DWALL)
    ops.geomTransf("Linear",  TRANSF_SLAB)


# ── 7. NODES ─────────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Create wall nodes, base slab interior nodes.

    L3 difference: NO interior top-slab nodes are created.
    The strut connects existing wall nodes 3 and 36 directly.
    """
    nid = 1
    # Left wall (x = 0), top → base
    for i in range(n_node_wall):
        ops.node(nid, 0.0, -i * elem_size)
        nid += 1

    # Right wall (x = l_center), top → base
    for i in range(n_node_wall):
        ops.node(nid, l_center, -i * elem_size)
        nid += 1

    # Base slab interior nodes (y = -depth_slab, x = 1 000 … 8 000 mm)
    for i in range(1, n_ele_slab):
        ops.node(nid, i * elem_size, -depth_slab)
        nid += 1

    # ── No top-slab interior nodes in L3 ──


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    # ── Wall base fixity
    ops.fix(NODE_LWALL_BASE, 1, 1, 1)
    ops.fix(NODE_RWALL_BASE, 1, 1, 1)

    # ── Winkler compression-only springs along both walls
    for i in range(n_node_wall):
        y = -i * elem_size

        # Left wall — soil on the left (−x) side
        wall_node_l = NODE_LWALL_TOP + i
        soil_node_l = NODE_SOIL_L_START + i
        ele_l       = ELE_SPRING_L_START + i
        mat_l       = _soil_mat_for_node(i)

        ops.node(soil_node_l, 0.0, y)
        ops.fix(soil_node_l, 1, 1, 1)
        ops.element(
            "zeroLength", ele_l, wall_node_l, soil_node_l,
            "-mat", mat_l, "-dir", 1,
            "-orient", -1, 0, 0, 0, 1, 0,
        )

        # Right wall — soil on the right (+x) side
        wall_node_r = NODE_RWALL_TOP + i
        soil_node_r = NODE_SOIL_R_START + i
        ele_r       = ELE_SPRING_R_START + i
        mat_r       = _soil_mat_for_node(i)

        ops.node(soil_node_r, l_center, y)
        ops.fix(soil_node_r, 1, 1, 1)
        ops.element(
            "zeroLength", ele_r, wall_node_r, soil_node_r,
            "-mat", mat_r, "-dir", 1,
            "-orient", 1, 0, 0, 0, 1, 0,
        )

    # ── Base slab Winkler springs (vertical)
    n_interior_slab = n_ele_slab - 1
    slab_nodes = (
        [NODE_LWALL_SLAB]
        + list(range(NODE_SLAB_START, NODE_SLAB_START + n_interior_slab))
        + [NODE_RWALL_SLAB]
    )
    ops.uniaxialMaterial("ENT", MAT_SOIL_SLAB, k_v_slab)

    for i, s_node in enumerate(slab_nodes):
        x_coord    = ops.nodeCoord(s_node, 1)
        soil_node_s = NODE_SOIL_S_START + i
        ele_s       = ELE_SPRING_S_START + i

        ops.node(soil_node_s, x_coord, -depth_slab)
        ops.fix(soil_node_s, 1, 1, 1)
        ops.element(
            "zeroLength", ele_s, s_node, soil_node_s,
            "-mat", MAT_SOIL_SLAB, "-dir", 1,
            "-orient", 0, -1, 0, 1, 0, 0,
        )


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────────
def define_elements() -> None:
    # ── Left wall (elements 1–32)
    for i in range(n_ele_wall):
        n1 = NODE_LWALL_TOP + i
        n2 = n1 + 1
        ops.element("dispBeamColumn", i + 1, n1, n2, TRANSF_DWALL, INT_DWALL)

    # ── Right wall (elements 33–64)
    for i in range(n_ele_wall):
        n1 = NODE_RWALL_TOP + i
        n2 = n1 + 1
        ops.element("dispBeamColumn", n_ele_wall + i + 1, n1, n2, TRANSF_DWALL, INT_DWALL)

    # ── Base slab (elements 65–73)
    slab_nodes = (
        [NODE_LWALL_SLAB]
        + list(range(NODE_SLAB_START, NODE_SLAB_END + 1))
        + [NODE_RWALL_SLAB]
    )
    for i in range(n_ele_slab):
        n1 = slab_nodes[i]
        n2 = slab_nodes[i + 1]
        ops.element("dispBeamColumn", 2 * n_ele_wall + i + 1, n1, n2, TRANSF_SLAB, INT_SLAB)

    # ── Steel strut (element 400) — axial only, corotTruss
    #   Connects left wall @ y = -2 000 mm  →  right wall @ y = -2 000 mm
    #   corotTruss syntax: element("corotTruss", tag, iNode, jNode, A, matTag)
    #   Here A is set to 1.0 because EA_strut already encodes the full EA.
    #   Alternatively pass A=l_center and E=k_strut — either is equivalent.
    ops.element(
        "corotTruss", ELE_STRUT,
        NODE_LWALL_TOP_SLAB, NODE_RWALL_TOP_SLAB,
        1.0, MAT_STRUT,          # A = 1 mm², E-material encodes full EA
    )


# ── 10. LOADING ──────────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Apply 10 kPa uniform gravity load on base slab only.

    L3 difference: NO gravity load on top strut — a corotTruss element
    carries axial force only and cannot accept transverse distributed loads.
    """
    # 10 kPa = 0.010 N/mm²; for 1 000 mm strip → 10 N/mm
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)

    for i in range(n_ele_slab):
        ele_tag = 2 * n_ele_wall + i + 1
        ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform", -10.0)


def define_lateral_loads() -> None:
    """Load Case 1 — uniform earth pressure 15 kPa on both diaphragm walls."""
    # 15 kPa = 0.015 N/mm²; for 1 000 mm strip → 15 N/mm
    ops.timeSeries("Linear", 2)
    ops.pattern("Plain", 2, 2)

    for i in range(n_ele_wall):
        ops.eleLoad("-ele", i + 1,              "-type", "-beamUniform",  15.0)
    for i in range(n_ele_wall):
        ops.eleLoad("-ele", n_ele_wall + i + 1, "-type", "-beamUniform", -15.0)


def define_water_pressure() -> None:
    """Load Case 2 — triangular hydrostatic pressure (water table at surface)."""
    ops.timeSeries("Linear", 3)
    ops.pattern("Plain", 3, 3)

    for i in range(n_ele_wall):
        d_mid = (i + 0.5) * elem_size
        w = gamma_w * d_mid * b_strip   # N/mm

        ops.eleLoad("-ele", i + 1,              "-type", "-beamUniform",  w)
        ops.eleLoad("-ele", n_ele_wall + i + 1, "-type", "-beamUniform", -w)


# ── 11. OUTPUT DATABASE (ODB) ───────────────────────────────────────────────────
def create_odb(odb_tag: int = 1) -> "opst.post.CreateODB":
    odb = opst.post.CreateODB(odb_tag=odb_tag, model_update=False)
    odb.save_model_data()
    return odb


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────────
def run_gravity(
    odb: "opst.post.CreateODB",
    n_steps: int = 10,
    ctrl_node: int = NODE_SLAB_START,
    ctrl_dof: int = 2,
) -> None:
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
    ops.loadConst("-time", 0.0)


def run_lateral_case(
    odb: "opst.post.CreateODB",
    pattern_tag: int,
    n_steps: int = 10,
    ctrl_node: int = NODE_LWALL_SLAB,
    ctrl_dof: int = 1,
) -> None:
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
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)
    odb = create_odb(odb_tag=1)

    # Phase 1: Gravity
    define_gravity_loads()
    run_gravity(odb)

    # Phase 2: Lateral (defined after loadConst)
    if lateral_case == 1:
        define_lateral_loads()
    else:
        define_water_pressure()

    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    run_lateral_case(odb, pattern_tag=lateral_case + 1)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and render deformed-shape HTML (UX and UY)."""
    odb.save_response()
    if not _headless():
        fig_ux = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, resp_type="disp", resp_dof="UX",
        )
        fig_ux.write_html(str(output_dir / "vis_05_deformed_UX.html"))

        fig_uy = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, resp_type="disp", resp_dof="UY",
        )
        fig_uy.write_html(str(output_dir / "vis_06_deformed_UY.html"))


# ── 14. MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ST31_L3 — Underground H-Frame (Steel Strut)")
    parser.add_argument(
        "--case", type=int, choices=[1, 2], default=1,
        help="Lateral load case: 1 = earth pressure, 2 = water pressure (default 1)",
    )
    args = parser.parse_args()

    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir, lateral_case=args.case)
    post_process(odb, output_dir)
    print(
        f"ST31_L3 case {args.case} analysis complete. "
        f"Open output/vis_05_deformed_UX.html / vis_06_deformed_UY.html to view results."
    )
