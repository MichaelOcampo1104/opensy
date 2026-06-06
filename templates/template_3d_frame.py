"""
3D Frame — OpenSeesPy Template
================================
Description:
    3D elastic frame with gravity loading.
    Extend with nonlinear sections and dynamic analysis as needed.

Reference:
    - OpenSeesPy documentation: https://openseespydoc.readthedocs.io
    - TODO: Add your design code / paper reference here

Author:   TODO: Your name
Date:     TODO: Date
Units:    kN, m, sec (SI)
"""

# ══════════════════════════════════════════════════════════════════════════════
# 1. IMPORTS
# ══════════════════════════════════════════════════════════════════════════════

import sys
import numpy as np
import openseespy.opensees as ops

from units import m, mm, kN, MPa, GPa, g_accel
from analysis_utils import setup_static_analysis, run_gravity

try:
    import opstool as opst
    HAS_OPSTOOL = True
except ImportError:
    HAS_OPSTOOL = False


# ══════════════════════════════════════════════════════════════════════════════
# 2. TAG REGISTRY
# ══════════════════════════════════════════════════════════════════════════════

# -- Geometric transformations --
TRANSF_COL_Z         = 1     # columns along Z-axis
TRANSF_BEAM_X        = 2     # beams along X-axis
TRANSF_BEAM_Y        = 3     # beams along Y-axis

# -- Load patterns --
PAT_GRAVITY           = 1
TS_GRAVITY            = 1


# ══════════════════════════════════════════════════════════════════════════════
# 3. PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════

# -- Grid layout --
n_bays_x  = 2                 # bays in X direction
n_bays_y  = 2                 # bays in Y direction
n_stories = 3                 # number of stories

bay_width_x  = 6.0 * m
bay_width_y  = 6.0 * m
story_height = 3.5 * m

# -- Column properties (elastic) --
col_A   = 0.16               # area (m²)  — e.g., 400×400 mm
col_E   = 25 * GPa           # concrete E
col_G   = 10.4 * GPa         # shear modulus
col_Iz  = 2.133e-3           # strong-axis I (m⁴)
col_Iy  = 2.133e-3           # weak-axis I (m⁴)
col_J   = 3.6e-3             # torsional constant (m⁴)

# -- Beam properties (elastic) --
beam_A  = 0.15               # area (m²) — e.g., 300×500 mm
beam_E  = 25 * GPa
beam_G  = 10.4 * GPa
beam_Iz = 3.125e-3           # strong-axis I (m⁴)
beam_Iy = 1.125e-3           # weak-axis I (m⁴)
beam_J  = 2.5e-3             # torsional constant (m⁴)

# -- Loading --
P_gravity = -50.0 * kN       # gravity per node


# ══════════════════════════════════════════════════════════════════════════════
# 4. MODEL BUILDER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════


def init_model():
    """Wipe and initialize 3D model with 6 DOFs per node."""
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    print("── Model initialized (3D, 6-DOF) ──")


def define_nodes() -> dict:
    """
    Create nodes on a regular 3D grid.

    Returns:
        Node map: {(ix, iy, story): node_tag}
    """
    node_map = {}
    tag = 1

    for story in range(n_stories + 1):
        z = story * story_height
        for iy in range(n_bays_y + 1):
            y = iy * bay_width_y
            for ix in range(n_bays_x + 1):
                x = ix * bay_width_x
                ops.node(tag, x, y, z)
                node_map[(ix, iy, story)] = tag
                tag += 1

    print(f"  ✓ Nodes created: {tag - 1}")
    return node_map


def define_fixities(node_map: dict):
    """Fix all base nodes in all 6 DOFs."""
    count = 0
    for iy in range(n_bays_y + 1):
        for ix in range(n_bays_x + 1):
            tag = node_map[(ix, iy, 0)]
            ops.fix(tag, 1, 1, 1, 1, 1, 1)
            count += 1

    print(f"  ✓ Fixed supports: {count}")


def define_elements(node_map: dict) -> dict:
    """
    Create elastic beam-column elements for columns and beams.

    Returns:
        {'columns': [tags], 'beams_x': [tags], 'beams_y': [tags]}
    """
    # Geometric transformations (vecxz defines local z-axis orientation)
    ops.geomTransf("PDelta", TRANSF_COL_Z, 1, 0, 0)    # columns: local-z → global-X
    ops.geomTransf("Linear", TRANSF_BEAM_X, 0, 0, 1)    # X-beams: local-z → global-Z
    ops.geomTransf("Linear", TRANSF_BEAM_Y, 0, 0, 1)    # Y-beams: local-z → global-Z

    elem_tag = 1
    col_tags = []
    beam_x_tags = []
    beam_y_tags = []

    # ── Columns (vertical, along Z) ──────────────────────────────────────────
    for story in range(n_stories):
        for iy in range(n_bays_y + 1):
            for ix in range(n_bays_x + 1):
                i_node = node_map[(ix, iy, story)]
                j_node = node_map[(ix, iy, story + 1)]
                ops.element(
                    "elasticBeamColumn", elem_tag,
                    i_node, j_node,
                    col_A, col_E, col_G, col_J, col_Iy, col_Iz,
                    TRANSF_COL_Z,
                )
                col_tags.append(elem_tag)
                elem_tag += 1

    # ── Beams in X-direction ──────────────────────────────────────────────────
    for story in range(1, n_stories + 1):
        for iy in range(n_bays_y + 1):
            for ix in range(n_bays_x):
                i_node = node_map[(ix, iy, story)]
                j_node = node_map[(ix + 1, iy, story)]
                ops.element(
                    "elasticBeamColumn", elem_tag,
                    i_node, j_node,
                    beam_A, beam_E, beam_G, beam_J, beam_Iy, beam_Iz,
                    TRANSF_BEAM_X,
                )
                beam_x_tags.append(elem_tag)
                elem_tag += 1

    # ── Beams in Y-direction ──────────────────────────────────────────────────
    for story in range(1, n_stories + 1):
        for iy in range(n_bays_y):
            for ix in range(n_bays_x + 1):
                i_node = node_map[(ix, iy, story)]
                j_node = node_map[(ix, iy + 1, story)]
                ops.element(
                    "elasticBeamColumn", elem_tag,
                    i_node, j_node,
                    beam_A, beam_E, beam_G, beam_J, beam_Iy, beam_Iz,
                    TRANSF_BEAM_Y,
                )
                beam_y_tags.append(elem_tag)
                elem_tag += 1

    print(f"  ✓ Columns: {len(col_tags)}, "
          f"Beams-X: {len(beam_x_tags)}, "
          f"Beams-Y: {len(beam_y_tags)}")

    return {"columns": col_tags, "beams_x": beam_x_tags, "beams_y": beam_y_tags}


def define_gravity_loads(node_map: dict):
    """Apply gravity loads to all nodes above the base."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)

    count = 0
    for story in range(1, n_stories + 1):
        for iy in range(n_bays_y + 1):
            for ix in range(n_bays_x + 1):
                tag = node_map[(ix, iy, story)]
                ops.load(tag, 0.0, 0.0, P_gravity, 0.0, 0.0, 0.0)
                count += 1

    print(f"  ✓ Gravity loads: {count} nodes × {P_gravity} kN")


def visualize_model(filename: str = "model_3d.html"):
    """Interactive 3D visualization."""
    if not HAS_OPSTOOL:
        print("  ⚠ opstool not installed — skipping visualization")
        return
    fig = opst.vis.plotly.plot_model(show_node_numbering=True)
    fig.write_html(filename)
    print(f"  📐 Visualization → {filename}")


# ══════════════════════════════════════════════════════════════════════════════
# 5. MAIN
# ══════════════════════════════════════════════════════════════════════════════


def main():
    print("=" * 60)
    print("  3D Frame — Gravity Analysis")
    print("=" * 60)

    # Build
    init_model()
    node_map = define_nodes()
    define_fixities(node_map)
    elem_map = define_elements(node_map)
    visualize_model("outputs/frame_3d_model.html")

    # Load & analyse
    print("\n── Gravity analysis ──")
    define_gravity_loads(node_map)
    setup_static_analysis()
    ok = run_gravity(n_steps=10)

    if ok != 0:
        print("FATAL: Gravity analysis did not converge.")
        sys.exit(1)

    # Extract sample results
    print("\n── Results ──")
    top_node = node_map[(0, 0, n_stories)]
    disp = ops.nodeDisp(top_node)
    print(f"  Top corner displacement: "
          f"Ux={disp[0]*1000:.3f} mm, "
          f"Uy={disp[1]*1000:.3f} mm, "
          f"Uz={disp[2]*1000:.3f} mm")

    # Eigen analysis
    n_modes = min(6, len(ops.getNodeTags()) * 3)
    try:
        eigenvalues = ops.eigen(n_modes)
        print(f"\n  Natural periods (first {n_modes} modes):")
        for i, ev in enumerate(eigenvalues):
            T = 2 * np.pi / ev**0.5
            print(f"    Mode {i+1}: T = {T:.4f} s  (f = {1/T:.2f} Hz)")
    except Exception as e:
        print(f"  ⚠ Eigen analysis failed: {e}")

    ops.wipe()
    print("\n  ✓ All complete.\n")


if __name__ == "__main__":
    main()
