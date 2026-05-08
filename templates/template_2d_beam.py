"""
2D Beam on Elastic Foundation — OpenSeesPy Template
=====================================================
Description:
    Beam on Winkler springs (soil-structure interaction).
    Uses elasticBeamColumn for the beam and zeroLength springs for soil.

Reference:
    - Vesic (1961) — Coefficient of subgrade reaction
    - TODO: Add your design code / paper reference here

Author:   TODO: Your name
Date:     TODO: Date
Units:    kN, m, sec (SI)
"""

# ══════════════════════════════════════════════════════════════════════════════
# 1. IMPORTS
# ══════════════════════════════════════════════════════════════════════════════

import math
import numpy as np
import openseespy.opensees as ops

from units import m, mm, kN, kPa, MPa, GPa
from analysis_utils import setup_static_analysis
from plot_utils import plot_beam_results

try:
    import opstool as opst
    HAS_OPSTOOL = True
except ImportError:
    HAS_OPSTOOL = False


# ══════════════════════════════════════════════════════════════════════════════
# 2. TAG REGISTRY
# ══════════════════════════════════════════════════════════════════════════════

# -- Geometric transformation --
TRANSF_BEAM          = 1

# -- Material tag ranges --
MAT_SPRING_START     = 100    # spring materials: 100, 101, 102, ...

# -- Element tag ranges --
ELEM_BEAM_START      = 1      # beam elements: 1, 2, 3, ...
ELEM_SPRING_START    = 1000   # spring elements: 1000, 1001, ...

# -- Node tag ranges --
NODE_BEAM_START      = 1      # beam nodes: 1, 2, 3, ...
NODE_GROUND_START    = 1000   # ground nodes: 1001, 1002, ...

# -- Load pattern --
PAT_LOAD             = 1
TS_LINEAR            = 1


# ══════════════════════════════════════════════════════════════════════════════
# 3. PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════

# -- Beam geometry --
L         = 8.0 * m           # total beam length
B_width   = 1.2 * m           # foundation / beam width
h_depth   = 0.6 * m           # beam depth
n_elem    = 40                 # number of beam elements

# -- Beam material --
E_beam    = 25 * GPa           # Young's modulus (concrete)

# -- Soil properties (for Vesic subgrade reaction) --
Es_soil   = 30_000 * kPa      # soil elastic modulus
nu_soil   = 0.30               # Poisson's ratio

# -- Loading --
# Point loads: list of (position_m, magnitude_kN). Negative = downward.
point_loads: list[tuple[float, float]] = [
    (L / 2, -300.0 * kN),     # 300 kN at midspan
]
udl = 0.0 * kN / m            # uniform distributed load (kN/m)


# ══════════════════════════════════════════════════════════════════════════════
# 4. HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════


def rect_inertia(b: float, h: float) -> float:
    """Moment of inertia for a rectangular section [m⁴]."""
    return (b * h**3) / 12.0


def vesic_ks(Es: float, B: float, nu: float, E_b: float, I: float) -> float:
    """
    Vesic (1961) coefficient of subgrade reaction [kN/m³].

    Args:
        Es:  Soil elastic modulus (kPa).
        B:   Foundation width (m).
        nu:  Soil Poisson's ratio.
        E_b: Beam elastic modulus (kPa).
        I:   Beam moment of inertia (m⁴).
    """
    flex_ratio = (Es * B**4) / (E_b * I)
    return (0.65 * Es) / (B * (1 - nu**2)) * flex_ratio ** (1 / 12)


def tributary_spring_k(ks: float, B: float, dx: float, is_end: bool) -> float:
    """Spring stiffness [kN/m] based on tributary length."""
    trib = dx / 2 if is_end else dx
    return ks * B * trib


# ══════════════════════════════════════════════════════════════════════════════
# 5. MODEL BUILDER
# ══════════════════════════════════════════════════════════════════════════════


def build_model() -> dict:
    """
    Build the complete Winkler beam model.

    Returns:
        Dict with derived properties: x_coords, ks, I, A, dx, n_nodes.
    """
    # ── Derived properties ────────────────────────────────────────────────────
    I = rect_inertia(B_width, h_depth)
    A = B_width * h_depth
    ks = vesic_ks(Es_soil, B_width, nu_soil, E_beam, I)
    dx = L / n_elem
    n_nodes = n_elem + 1

    print(f"  ks (Vesic) = {ks:,.0f} kN/m³")
    print(f"  I = {I:.6e} m⁴,  A = {A:.4f} m²")

    # ── 5a. Initialize ────────────────────────────────────────────────────────
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)

    # ── 5b. Nodes ─────────────────────────────────────────────────────────────
    x_coords = np.linspace(0, L, n_nodes)

    for i, x in enumerate(x_coords):
        beam_tag = NODE_BEAM_START + i
        ground_tag = NODE_GROUND_START + i + 1

        ops.node(beam_tag, x, 0.0)       # beam node (free)
        ops.node(ground_tag, x, 0.0)     # ground node (fixed)
        ops.fix(ground_tag, 1, 1, 1)

    print(f"  ✓ Nodes: {n_nodes} beam + {n_nodes} ground")

    # ── 5c. Beam elements ─────────────────────────────────────────────────────
    ops.geomTransf("Linear", TRANSF_BEAM)

    for i in range(n_elem):
        elem_tag = ELEM_BEAM_START + i
        i_node = NODE_BEAM_START + i
        j_node = NODE_BEAM_START + i + 1

        ops.element(
            "elasticBeamColumn", elem_tag,
            i_node, j_node,
            A, E_beam, I, TRANSF_BEAM,
        )

    print(f"  ✓ Beam elements: {n_elem}")

    # ── 5d. Soil springs ──────────────────────────────────────────────────────
    for i in range(n_nodes):
        mat_tag = MAT_SPRING_START + i
        elem_tag = ELEM_SPRING_START + i
        is_end = (i == 0) or (i == n_nodes - 1)
        k_i = tributary_spring_k(ks, B_width, dx, is_end)

        ops.uniaxialMaterial("Elastic", mat_tag, k_i)
        ops.element(
            "zeroLength", elem_tag,
            NODE_BEAM_START + i,          # beam node
            NODE_GROUND_START + i + 1,    # ground node
            "-mat", mat_tag, "-dir", 2,   # vertical direction
        )

    print(f"  ✓ Soil springs: {n_nodes}")

    # ── 5e. Horizontal fixity for stability ───────────────────────────────────
    ops.fix(NODE_BEAM_START, 1, 0, 0)             # left end
    ops.fix(NODE_BEAM_START + n_nodes - 1, 1, 0, 0)  # right end

    return {
        "x_coords": x_coords,
        "ks": ks, "I": I, "A": A, "dx": dx, "n_nodes": n_nodes,
    }


# ══════════════════════════════════════════════════════════════════════════════
# 6. LOADING
# ══════════════════════════════════════════════════════════════════════════════


def apply_loads(n_nodes: int, dx: float):
    """Apply point loads and/or UDL."""
    ops.timeSeries("Linear", TS_LINEAR)
    ops.pattern("Plain", PAT_LOAD, TS_LINEAR)

    # Point loads → nearest node
    for pos, P in point_loads:
        idx = int(round(pos / dx))
        idx = max(0, min(n_nodes - 1, idx))
        node_tag = NODE_BEAM_START + idx
        ops.load(node_tag, 0.0, P, 0.0)
        print(f"  ✓ Point load: {P:.1f} kN at x = {pos:.2f} m (node {node_tag})")

    # UDL → equivalent nodal loads
    if udl != 0.0:
        for i in range(n_nodes):
            is_end = (i == 0) or (i == n_nodes - 1)
            trib = dx / 2 if is_end else dx
            fy = udl * trib
            ops.load(NODE_BEAM_START + i, 0.0, fy, 0.0)
        print(f"  ✓ UDL applied: {udl:.1f} kN/m")


# ══════════════════════════════════════════════════════════════════════════════
# 7. ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════


def run_analysis():
    """Configure and run static analysis (single step, linear)."""
    ops.system("BandGeneral")
    ops.numberer("RCM")
    ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")
    ops.analyze(1)
    print("  ✓ Static analysis complete")


# ══════════════════════════════════════════════════════════════════════════════
# 8. POST-PROCESSING
# ══════════════════════════════════════════════════════════════════════════════


def extract_results(model_props: dict) -> dict:
    """Extract displacement, moment, shear, and contact pressure."""
    n_nodes = model_props["n_nodes"]
    dx = model_props["dx"]
    ks = model_props["ks"]
    x = model_props["x_coords"]

    # Displacements
    disp = np.array([
        ops.nodeDisp(NODE_BEAM_START + i, 2) for i in range(n_nodes)
    ])

    # Spring reactions & contact pressure
    reactions = np.zeros(n_nodes)
    contact_p = np.zeros(n_nodes)
    for i in range(n_nodes):
        is_end = (i == 0) or (i == n_nodes - 1)
        k_i = tributary_spring_k(ks, B_width, dx, is_end)
        trib = dx / 2 if is_end else dx

        reactions[i] = k_i * (-disp[i])
        contact_p[i] = reactions[i] / (B_width * trib)

    # Element forces
    moments = []
    shears = []
    for i in range(n_nodes - 1):
        f = ops.eleForce(ELEM_BEAM_START + i)
        # f = [Nx_i, Vy_i, Mz_i, Nx_j, Vy_j, Mz_j]
        shears.append(f[1])
        moments.append(-f[2])

    # Extend to n_nodes length
    shears.append(shears[-1])
    moments.append(moments[-1])

    results = {
        "x": x,
        "disp_mm": disp * 1000,           # m → mm
        "moment": np.array(moments),       # kN·m
        "shear": np.array(shears),         # kN
        "contact_p": contact_p,            # kPa
        "reaction": reactions,             # kN
    }

    # Print key results
    print(f"  Peak deflection   : {disp.min() * 1000:.3f} mm")
    print(f"  Peak moment       : {np.array(moments).max():.2f} kN·m")
    print(f"  Peak shear        : {np.abs(shears).max():.2f} kN")
    print(f"  Peak contact pres : {contact_p.max():.2f} kPa")

    return results


# ══════════════════════════════════════════════════════════════════════════════
# 9. VISUALIZATION
# ══════════════════════════════════════════════════════════════════════════════


def visualize_model(filename: str = "model_view.html"):
    """Generate interactive model view (requires opstool)."""
    if not HAS_OPSTOOL:
        print("  ⚠ opstool not installed — skipping visualization")
        return
    fig = opst.vis.plotly.plot_model(show_node_numbering=True)
    fig.write_html(filename)
    print(f"  📐 Model visualization → {filename}")


# ══════════════════════════════════════════════════════════════════════════════
# 10. MAIN — ASSEMBLE & RUN
# ══════════════════════════════════════════════════════════════════════════════


def main():
    print("=" * 60)
    print("  Beam on Elastic Foundation (Winkler) Analysis")
    print("=" * 60)

    # Build
    print("\n── Building model ──")
    props = build_model()

    # Visualize
    visualize_model("outputs/winkler_model.html")

    # Load
    print("\n── Applying loads ──")
    apply_loads(props["n_nodes"], props["dx"])

    # Analyse
    print("\n── Running analysis ──")
    run_analysis()

    # Results
    print("\n── Extracting results ──")
    results = extract_results(props)

    # Plot
    info = (
        f"L={L}m  B={B_width}m  h={h_depth}m  |  "
        f"Es={Es_soil/kPa:,.0f} kPa  ν={nu_soil}  |  "
        f"ks={props['ks']:,.0f} kN/m³"
    )
    plot_beam_results(
        x=results["x"],
        deflection_mm=results["disp_mm"],
        moment_kNm=results["moment"],
        shear_kN=results["shear"],
        reaction_kPa=results["contact_p"],
        title="Beam on Elastic Foundation — FEM Results",
        info_text=info,
        save_path="outputs/winkler_results.png",
    )

    ops.wipe()
    print("\n  ✓ All complete.\n")


if __name__ == "__main__":
    main()
