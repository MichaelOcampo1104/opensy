"""
2D Frame — OpenSeesPy Template
================================
Description:
    Nonlinear 2D RC portal frame with gravity + pushover analysis.
    Replace parameters and section definitions for your specific frame.

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

# Local utilities (from templates/ directory)
# Adjust the import path if you move this file elsewhere
from units import m, mm, kN, MPa, GPa, g_accel
from analysis_utils import setup_static_analysis, run_gravity, run_pushover
from plot_utils import plot_pushover_curve

# Optional: model visualization
try:
    import opstool as opst
    HAS_OPSTOOL = True
except ImportError:
    HAS_OPSTOOL = False


# ══════════════════════════════════════════════════════════════════════════════
# 2. TAG REGISTRY
# ══════════════════════════════════════════════════════════════════════════════
# Define ALL tags as named constants here — never use magic numbers in the model.

# -- Material tags --
MAT_CONCRETE_CORE    = 1     # confined concrete
MAT_CONCRETE_COVER   = 2     # unconfined concrete
MAT_STEEL_REBAR      = 3     # reinforcing steel

# -- Section tags --
SEC_COLUMN           = 1
SEC_BEAM             = 2

# -- Integration tags --
INT_COLUMN           = 1
INT_BEAM             = 2

# -- Geometric transformation tags --
TRANSF_COLUMN        = 1     # PDelta for columns
TRANSF_BEAM          = 2     # Linear for beams

# -- Load pattern tags --
PAT_GRAVITY          = 1
PAT_LATERAL          = 2

# -- Time series tags --
TS_GRAVITY           = 1
TS_LATERAL           = 2


# ══════════════════════════════════════════════════════════════════════════════
# 3. PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════

# -- Geometry --
n_bays    = 1                # number of bays
n_stories = 1                # number of stories
bay_width = 6.0 * m         # center-to-center bay width
story_height = 3.5 * m      # floor-to-floor height

# -- Column section --
col_width = 400 * mm         # column width (b)
col_depth = 400 * mm         # column depth (h)
col_cover = 40 * mm          # concrete cover

# -- Beam section --
beam_width = 300 * mm
beam_depth = 500 * mm

# -- Rebar --
rebar_area = 314 * mm**2     # area of one bar (e.g., Ø20 = 314 mm²)
n_bars_top = 3               # bars in top layer
n_bars_bot = 3               # bars in bottom layer

# -- Material properties --
fc_core   = -30.0 * MPa     # confined concrete f'c (negative in compression)
ec0_core  = -0.004           # strain at f'c
fcu_core  = -25.0 * MPa     # residual strength
ecu_core  = -0.014           # ultimate strain

fc_cover  = -25.0 * MPa     # unconfined concrete f'c
ec0_cover = -0.002
fcu_cover = 0.0
ecu_cover = -0.006

fy_steel  = 500.0 * MPa     # steel yield stress
Es_steel  = 200.0 * GPa     # steel elastic modulus
b_steel   = 0.01             # strain hardening ratio

# -- Loading --
P_gravity = -200.0 * kN     # gravity load per beam-column joint (negative = down)
F_lateral = 1.0 * kN        # reference lateral load (scaled in pushover)

# -- Pushover --
control_node_tag = None      # set after nodes are created
control_dof = 1              # X-direction
target_drift_ratio = 0.04    # 4% drift
n_integration_pts = 5        # Gauss-Lobatto points per element


# ══════════════════════════════════════════════════════════════════════════════
# 4. MODEL BUILDER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════


def init_model():
    """Wipe and initialize 2D model with 3 DOFs per node (Ux, Uy, Rz)."""
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    print("── Model initialized (2D, 3-DOF) ──")


# ── 4a. Materials ─────────────────────────────────────────────────────────────

def define_materials():
    """Define concrete and steel uniaxial materials."""
    # Confined concrete (core)
    ops.uniaxialMaterial(
        "Concrete01", MAT_CONCRETE_CORE,
        fc_core, ec0_core, fcu_core, ecu_core,
    )

    # Unconfined concrete (cover)
    ops.uniaxialMaterial(
        "Concrete01", MAT_CONCRETE_COVER,
        fc_cover, ec0_cover, fcu_cover, ecu_cover,
    )

    # Reinforcing steel
    ops.uniaxialMaterial(
        "Steel01", MAT_STEEL_REBAR,
        fy_steel, Es_steel, b_steel,
    )

    print("  ✓ Materials defined (core concrete, cover concrete, steel)")


# ── 4b. Sections ──────────────────────────────────────────────────────────────

def define_sections():
    """Define fiber sections for columns and beams."""
    # -- Column fiber section --
    _build_rc_rect_section(
        sec_tag=SEC_COLUMN,
        width=col_width, depth=col_depth, cover=col_cover,
        core_mat=MAT_CONCRETE_CORE, cover_mat=MAT_CONCRETE_COVER,
        steel_mat=MAT_STEEL_REBAR,
        n_bars_top=n_bars_top, n_bars_bot=n_bars_bot, bar_area=rebar_area,
        n_fiber_core=10, n_fiber_cover=2,
    )

    # -- Beam fiber section --
    _build_rc_rect_section(
        sec_tag=SEC_BEAM,
        width=beam_width, depth=beam_depth, cover=col_cover,
        core_mat=MAT_CONCRETE_CORE, cover_mat=MAT_CONCRETE_COVER,
        steel_mat=MAT_STEEL_REBAR,
        n_bars_top=n_bars_top, n_bars_bot=n_bars_bot, bar_area=rebar_area,
        n_fiber_core=10, n_fiber_cover=2,
    )

    print("  ✓ Sections defined (column, beam — fiber)")


def _build_rc_rect_section(
    sec_tag, width, depth, cover,
    core_mat, cover_mat, steel_mat,
    n_bars_top, n_bars_bot, bar_area,
    n_fiber_core=10, n_fiber_cover=2,
):
    """
    Build a rectangular RC fiber section.

    Local axes: y along depth, z along width.
    Origin at centroid.
    """
    y1 = depth / 2.0
    z1 = width / 2.0

    ops.section("Fiber", sec_tag)

    # Core concrete (inside cover)
    ops.patch(
        "rect", core_mat, n_fiber_core, 1,
        cover - y1, cover - z1,
        y1 - cover, z1 - cover,
    )

    # Cover concrete — four sides
    ops.patch("rect", cover_mat, n_fiber_cover, 1, -y1, z1 - cover, y1, z1)        # top
    ops.patch("rect", cover_mat, n_fiber_cover, 1, -y1, -z1, y1, cover - z1)       # bottom
    ops.patch("rect", cover_mat, n_fiber_cover, 1, -y1, cover - z1, cover - y1, z1 - cover)  # left
    ops.patch("rect", cover_mat, n_fiber_cover, 1, y1 - cover, cover - z1, y1, z1 - cover)   # right

    # Reinforcement layers
    ops.layer("straight", steel_mat, n_bars_top, bar_area,
              y1 - cover, z1 - cover, y1 - cover, cover - z1)       # top bars
    ops.layer("straight", steel_mat, n_bars_bot, bar_area,
              cover - y1, z1 - cover, cover - y1, cover - z1)       # bottom bars


# ── 4c. Nodes ─────────────────────────────────────────────────────────────────

def define_nodes() -> dict:
    """
    Create nodes for a regular n_bays × n_stories frame.

    Returns:
        Node map: {(bay_idx, story_idx): node_tag}
        bay_idx   = 0 .. n_bays
        story_idx = 0 (base) .. n_stories
    """
    node_map = {}
    tag = 1

    for story in range(n_stories + 1):
        y = story * story_height
        for bay in range(n_bays + 1):
            x = bay * bay_width
            ops.node(tag, x, y)
            node_map[(bay, story)] = tag
            tag += 1

    print(f"  ✓ Nodes created ({tag - 1} nodes)")
    return node_map


# ── 4d. Boundary Conditions ──────────────────────────────────────────────────

def define_fixities(node_map: dict):
    """Fix all base nodes (story = 0) in all DOFs."""
    for bay in range(n_bays + 1):
        base_tag = node_map[(bay, 0)]
        ops.fix(base_tag, 1, 1, 1)

    print(f"  ✓ Base nodes fixed ({n_bays + 1} supports)")


# ── 4e. Elements ──────────────────────────────────────────────────────────────

def define_elements(node_map: dict) -> dict:
    """
    Create beam-column elements for columns and beams.

    Returns:
        Element map: {'columns': [tags], 'beams': [tags]}
    """
    # Geometric transformations
    ops.geomTransf("PDelta", TRANSF_COLUMN)
    ops.geomTransf("Linear", TRANSF_BEAM)

    # Beam integrations (Gauss-Lobatto)
    ops.beamIntegration("Lobatto", INT_COLUMN, SEC_COLUMN, n_integration_pts)
    ops.beamIntegration("Lobatto", INT_BEAM, SEC_BEAM, n_integration_pts)

    elem_tag = 1
    col_tags = []
    beam_tags = []

    # Columns (vertical: story i → story i+1)
    for story in range(n_stories):
        for bay in range(n_bays + 1):
            i_node = node_map[(bay, story)]
            j_node = node_map[(bay, story + 1)]
            ops.element(
                "forceBeamColumn", elem_tag,
                i_node, j_node,
                TRANSF_COLUMN, INT_COLUMN,
            )
            col_tags.append(elem_tag)
            elem_tag += 1

    # Beams (horizontal: bay i → bay i+1)
    for story in range(1, n_stories + 1):
        for bay in range(n_bays):
            i_node = node_map[(bay, story)]
            j_node = node_map[(bay + 1, story)]
            ops.element(
                "forceBeamColumn", elem_tag,
                i_node, j_node,
                TRANSF_BEAM, INT_BEAM,
            )
            beam_tags.append(elem_tag)
            elem_tag += 1

    print(f"  ✓ Elements created ({len(col_tags)} columns, {len(beam_tags)} beams)")
    return {"columns": col_tags, "beams": beam_tags}


# ── 4f. Loading ───────────────────────────────────────────────────────────────

def define_gravity_loads(node_map: dict):
    """Apply gravity loads at all beam-column joints (story ≥ 1)."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)

    for story in range(1, n_stories + 1):
        for bay in range(n_bays + 1):
            tag = node_map[(bay, story)]
            ops.load(tag, 0.0, P_gravity, 0.0)

    n_loaded = n_stories * (n_bays + 1)
    print(f"  ✓ Gravity loads applied ({n_loaded} nodes, P = {P_gravity} kN each)")


def define_lateral_loads(node_map: dict):
    """
    Apply lateral load pattern for pushover (inverted-triangular distribution).
    """
    ops.timeSeries("Linear", TS_LATERAL)
    ops.pattern("Plain", PAT_LATERAL, TS_LATERAL)

    for story in range(1, n_stories + 1):
        # Inverted-triangular: force proportional to height
        height_ratio = story / n_stories
        F = F_lateral * height_ratio

        # Apply to all nodes at this story level
        for bay in range(n_bays + 1):
            tag = node_map[(bay, story)]
            ops.load(tag, F, 0.0, 0.0)

    print(f"  ✓ Lateral loads applied (inverted-triangular, F_ref = {F_lateral} kN)")


# ══════════════════════════════════════════════════════════════════════════════
# 5. VISUALIZATION (optional)
# ══════════════════════════════════════════════════════════════════════════════

def visualize_model(filename: str = "model_view.html"):
    """Generate an interactive 3D model view (requires opstool)."""
    if not HAS_OPSTOOL:
        print("  ⚠ opstool not installed — skipping visualization")
        return

    fig = opst.vis.plotly.plot_model(show_node_numbering=True)
    fig.write_html(filename)
    print(f"  📐 Model visualization saved → {filename}")


# ══════════════════════════════════════════════════════════════════════════════
# 6. MAIN — ASSEMBLE & RUN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  2D RC Frame — Gravity + Pushover Analysis")
    print("=" * 60)

    # ── Build model ───────────────────────────────────────────────────────────
    init_model()
    define_materials()
    define_sections()
    node_map = define_nodes()
    define_fixities(node_map)
    elem_map = define_elements(node_map)

    # ── Visualize (optional) ──────────────────────────────────────────────────
    visualize_model("outputs/frame_model.html")

    # ── Gravity analysis ──────────────────────────────────────────────────────
    print("\n── Phase 1: Gravity ──")
    define_gravity_loads(node_map)
    setup_static_analysis()
    ok = run_gravity(n_steps=10)
    if ok != 0:
        print("FATAL: Gravity analysis did not converge.")
        sys.exit(1)

    # ── Pushover analysis ─────────────────────────────────────────────────────
    print("\n── Phase 2: Pushover ──")
    ops.wipeAnalysis()
    define_lateral_loads(node_map)
    setup_static_analysis()

    # Control node = top-left
    ctrl_node = node_map[(0, n_stories)]
    target_disp = target_drift_ratio * (n_stories * story_height)

    results = run_pushover(
        control_node=ctrl_node,
        control_dof=control_dof,
        target_disp=target_disp,
        incr=0.001 * m,
    )

    # ── Post-processing ───────────────────────────────────────────────────────
    print("\n── Post-processing ──")
    plot_pushover_curve(
        disp=results["disp"],
        base_shear=results["base_shear"],
        title=f"Pushover — {n_bays}-Bay {n_stories}-Story RC Frame",
        save_path="outputs/pushover_curve.png",
    )

    # Print summary
    print("\n── Summary ──")
    print(f"  Peak displacement : {results['disp'][-1]:.4f} m")
    print(f"  Peak base shear   : {abs(results['base_shear']).max():.1f} kN")
    print(f"  Target drift      : {target_drift_ratio * 100:.1f}%")

    ops.wipe()
    print("\n  ✓ All analyses complete.\n")


if __name__ == "__main__":
    main()
