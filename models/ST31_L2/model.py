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

# Compatibility: opstool v0.8.7 uses deprecated np.NAN
np.NAN = np.nan


def _headless() -> bool:
    """Return True in CI / headless environments (output from vis_utils)."""
    import os
    return os.getenv("OPENSEES_HEADLESS", "0") == "1"


# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────────
# ── Materials
MAT_CONCRETE = 1       # elastic section material (reference only)
MAT_SOIL_1   = 2       # ENT — layer 1  ( 0 m  to  -6 m)
MAT_SOIL_2   = 3       # ENT — layer 2  (-6 m  to -12 m)
MAT_SOIL_3   = 4       # ENT — layer 3  (-12 m to -18 m)
MAT_SOIL_4   = 5       # ENT — layer 4  (-18 m to -24 m)
MAT_SOIL_5   = 6       # ENT — layer 5  (-24 m to -30 m)

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


# ── Helper: soil layer → material tag ───────────────────────────────────────────
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


# ── Visualisation helper (opstool v0.8.7 compatible) ────────────────────────────
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
        # (soil, wall) → wall moving left (neg. x) compresses the spring
        ops.element("zeroLength", ele_l, soil_node_l, wall_node_l,
                    "-mat", mat_l, "-dir", 1,
                    "-orient", 1, 0, 0, 0, 1, 0)

        # Right wall — soil is on the right (+x) side
        wall_node_r = NODE_RWALL_TOP + i
        soil_node_r = NODE_SOIL_R_START + i
        ele_r       = ELE_SPRING_R_START + i
        mat_r       = _soil_mat_for_node(i)

        ops.node(soil_node_r, l_center, y)
        ops.fix(soil_node_r, 1, 1, 1)
        # (wall, soil) → wall moving right (pos. x) compresses the spring
        ops.element("zeroLength", ele_r, wall_node_r, soil_node_r,
                    "-mat", mat_r, "-dir", 1,
                    "-orient", 1, 0, 0, 0, 1, 0)


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
    """TODO: apply self-weight and any surcharge."""
    pass


def define_lateral_loads() -> None:
    """TODO: apply lateral earth / water / seismic loading."""
    pass


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
def run_analysis(output_dir: Path) -> None:
    """Build model with Winkler springs and render visualisation checkpoints.

    (Analysis stubs — replace with solver calls when loading is defined.)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)
    define_gravity_loads()
    define_lateral_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────────
def post_process(output_dir: Path) -> None:
    """TODO: render deformed shape after analysis."""
    pass


# ── 14. MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    run_analysis(output_dir)
    post_process(output_dir)
    print("ST31_L2 model built successfully. Open output/vis_02_model.html to view.")
