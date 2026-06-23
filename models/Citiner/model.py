# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Cantilever RC Column Pushover (AdaBoost PHL parameterisation)
UniqueID : Citiner
Author   : OpenSeesPy Standardisation Agent (from Tcl templates by Citiner group)
Date     : 2026-06-23
Purpose  : Monotonic or cyclic displacement-controlled pushover of a single RC
           cantilever column with a fiber-section beamWithHinges element.
           Column geometry, reinforcement, material strengths, and plastic-hinge
           length (PHL) are parameterised so they can be set from an external
           ML model (e.g. the companion AdaBoost notebook in ref/).
Ref      : ref/monotonicTemplate.tcl, ref/cyclicTemplate.tcl
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import sys
from pathlib import Path

import numpy as np

np.NAN = np.nan
np.NaN = np.nan

import openseespy.opensees as ops
import opstool as opst

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import vis_nodes, vis_model, vis_loads, vis_pre_analysis, _headless

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
MAT_STEEL       = 1
MAT_CONCRETE_C  = 2   # confined core
MAT_CONCRETE_U  = 3   # unconfined cover

SEC_COL         = 1

NODE_BASE       = 1
NODE_TOP        = 2

ELE_COL         = 1

GT_TAG          = 2

PAT_GRAVITY     = 10
PAT_LATERAL     = 20

CTRL_NODE       = NODE_TOP
CTRL_DOF        = 1      # X-direction

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# ── Loading type ─────────────────────────────────────────────────────────
CYCLIC = True      # False = monotonic pushover; True = cyclic (23-segment)

# ── Column geometry [mm] ──────────────────────────────────────────────────
B       = 150.0 * mm   # section width  (z-direction in fiber section)
H       = 140.0 * mm   # section height (y-direction in fiber section)
L       = 1500.0 * mm  # column clear length (base to load point)

# ── Reinforcement ─────────────────────────────────────────────────────────
db      = 10.0 * mm    # longitudinal bar diameter
nb      = 6            # number of longitudinal bars (3 per face for nb=6)
dbv     = 6.0 * mm     # stirrup / transverse bar diameter
ast     = 2.0 * dbv + db / 2.0   # cover to bar centreline

# ── Longitudinal steel ────────────────────────────────────────────────────
fy      = 557.0 * MPa  # yield strength
Es      = 200.0e3 * MPa  # elastic modulus
k       = 0.002          # strain-hardening ratio (Steel02 parameter b)
R0      = 18.0
cR1     = 0.925
cR2     = 0.15

# ── Concrete — confined core ──────────────────────────────────────────────
# (Concrete01 parameters for monotonic; Concrete02 parameters for cyclic use
#  the same strengths — the model constant SWITCH_CONCRETE selects which)
fpc_c   = -52.0 * MPa   # confined compressive strength
epsc0_c = -0.01          # strain at peak confined stress
fpcu_c  = -5.0 * MPa     # confined crushing strength
epscu_c = -0.1           # confined ultimate strain

# ── Concrete — unconfined cover ──────────────────────────────────────────
# Cover concrete has lower strength and less ductility
fpc_u   = -40.0 * MPa   # cover compressive strength  (≈ 0.77 × fpc_c)
epsc0_u = -0.003         # strain at peak cover stress
fpcu_u  = -0.0 * MPa     # cover crushing strength (zero residual)
epscu_u = -0.006         # cover ultimate strain

# ── Plastic hinge length [mm] (from AdaBoost ML model) ─────────────────────
PHL     = 99.82 * mm

# ── Computed section properties ────────────────────────────────────────────
pi_     = 3.141592653589793
As      = pi_ * db**2 / 4.0          # single bar area [mm^2]
Ag      = B * H                      # gross cross-section [mm^2]
Iz      = B * H**3 / 12.0            # strong-axis moment of inertia [mm^4]

# Equivalent concrete elastic modulus (weighted by area of concrete + steel)
Ecc     = 20000.0 * MPa              # concrete Young's modulus
Ec      = ((Ag - nb * As) * Ecc + nb * As * Es) / Ag   # [MPa]

# Cover dimensions for fiber section
bt1 = B - 2.0 * ast                  # core width  (z-direction)  [mm]
bt2 = H - 2.0 * ast                  # core height (y-direction)  [mm]

# ── Axial load ratio ───────────────────────────────────────────────────────
axial_ratio = 0.10                   # P / (Ag * fpc_c) — 0.10 or 0.32
P_axial     = axial_ratio * Ag * abs(fpc_c)   # [N]

# ── Pushover parameters ────────────────────────────────────────────────────
n_horizontal_steps = 100              # sub-steps per segment

# Monotonic: push to 72 mm
monotonic_target   = 72.0 * mm

# Cyclic protocol: sequence of displacement changes (Dmax per segment)
# from ref/cyclicTemplate.tcl  (→ cumulative path: 0 → -2.5 → +2.5 → -5.0 → ...)
cyclic_delta = np.array([
    -2.5,  5.0,  -7.5,  10.0, -12.5,  15.0, -17.5,  20.0,
    -25.0, 30.0, -40.0,  50.0, -60.0,  70.0, -85.0, 100.0,
    -118.0, 136.0, -153.0, 170.0, -193.0, 216.0, -158.0,
]) * mm


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    # Longitudinal steel — Steel02 (Giuffré-Menegotto-Pinto)
    ops.uniaxialMaterial("Steel02", MAT_STEEL, fy, Es, k, R0, cR1, cR2)

    if CYCLIC:
        # Confined core — Concrete02 (tension ft=0.1*|fpc|, Ets=9e3 MPa)
        ops.uniaxialMaterial("Concrete02", MAT_CONCRETE_C,
                             fpc_c, epsc0_c, fpcu_c, epscu_c,
                             0.1, 9.0e3, 10.0e3)
        # Cover — Concrete02 with minimal tension
        ops.uniaxialMaterial("Concrete02", MAT_CONCRETE_U,
                             fpc_u, epsc0_u, fpcu_u, epscu_u,
                             0.05, 9.0e3, 10.0e3)
    else:
        # Confined core — Concrete01 (no tension)
        ops.uniaxialMaterial("Concrete01", MAT_CONCRETE_C,
                             fpc_c, epsc0_c, fpcu_c, epscu_c)
        # Unconfined cover
        ops.uniaxialMaterial("Concrete01", MAT_CONCRETE_U,
                             fpc_u, epsc0_u, fpcu_u, epscu_u)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    ops.section("Fiber", SEC_COL)

    # Confined core patch
    #   patch rect matTag numSubdivY numSubdivZ  yMin zMin  yMax zMax
    ops.patch("rect", MAT_CONCRETE_C, 20, 20,
              -bt2 / 2.0, -bt1 / 2.0, bt2 / 2.0, bt1 / 2.0)

    # Cover patches (4 sides)
    # Left   (y-negative face)
    ops.patch("rect", MAT_CONCRETE_U, 1, 12,
              -H / 2.0, -B / 2.0, -bt2 / 2.0, B / 2.0)
    # Right  (y-positive face)
    ops.patch("rect", MAT_CONCRETE_U, 1, 12,
              H / 2.0, B / 2.0, bt2 / 2.0, -B / 2.0)
    # Bottom (z-negative face)
    ops.patch("rect", MAT_CONCRETE_U, 12, 1,
              -bt2 / 2.0, -B / 2.0, bt2 / 2.0, -bt1 / 2.0)
    # Top    (z-positive face)
    ops.patch("rect", MAT_CONCRETE_U, 12, 1,
              -bt2 / 2.0, bt1 / 2.0, bt2 / 2.0, B / 2.0)

    # Rebar fibers — 3 bars per face (left + right) at z = -bt1/2, 0, bt1/2
    ops.fiber(-bt2 / 2.0, -bt1 / 2.0, As, MAT_STEEL)
    ops.fiber(-bt2 / 2.0,  0.0,         As, MAT_STEEL)
    ops.fiber(-bt2 / 2.0,  bt1 / 2.0,   As, MAT_STEEL)
    ops.fiber( bt2 / 2.0, -bt1 / 2.0,   As, MAT_STEEL)
    ops.fiber( bt2 / 2.0,  0.0,         As, MAT_STEEL)
    ops.fiber( bt2 / 2.0,  bt1 / 2.0,   As, MAT_STEEL)

    if nb > 6:
        # Additional mid-height bars (as in cyclic template, nb=8)
        ops.fiber(0.0,  bt1 / 2.0, As, MAT_STEEL)
        ops.fiber(0.0, -bt1 / 2.0, As, MAT_STEEL)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    ops.node(NODE_BASE, 0.0, 0.0)
    ops.node(NODE_TOP,  0.0, L)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    ops.fix(NODE_BASE, 1, 1, 1)   # fully fixed base
    # Top node is free (UX, UY, RZ all unrestrained)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    # Geometric transformation
    if CYCLIC:
        ops.geomTransf("PDelta", GT_TAG)         # P-Delta for cyclic
    else:
        ops.geomTransf("Linear", GT_TAG)          # Linear for monotonic

    # beamWithHinges: eleTag iNode jNode secTag lpL secTag lpR Ec A Iz transfTag
    ops.element("beamWithHinges", ELE_COL,
                NODE_BASE, NODE_TOP,
                SEC_COL, PHL, SEC_COL, PHL,
                Ec, Ag, Iz, GT_TAG)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(odb_tag: int = 1) -> "opst.post.CreateODB":
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        save_frame_resp=False,   # beamWithHinges internal sections lack user-visible tags
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    ops.timeSeries("Constant", PAT_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, PAT_GRAVITY)
    ops.load(NODE_TOP, 0.0, P_axial, 0.0)    # -Y in global (axial compression)


def define_lateral_loads() -> None:
    ops.timeSeries("Linear", PAT_LATERAL)
    ops.pattern("Plain", PAT_LATERAL, PAT_LATERAL)
    ops.load(NODE_TOP, 1.0, 0.0, 0.0)    # +X unit load (scale follows disp-control)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(
    odb: "opst.post.CreateODB",
    n_steps: int = 10,
) -> None:
    """Load-controlled gravity — manual loop (SmartAnalyze exception)."""
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-2, 20)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.analysis("Static")
    ops.analyze(n_steps)
    ops.loadConst("-time", 0.0)
    print(f"  Gravity completed  (P = {P_axial / 1000.0:.1f} kN)")


def _push_segment(
    odb: "opst.post.CreateODB",
    target_disp: float,
    n_steps: int = 100,
    ctrl_node: int = CTRL_NODE,
    ctrl_dof: int = CTRL_DOF,
) -> None:
    """Displacement-controlled push to *target_disp* using SmartAnalyze.

    Pushes from the current deformed configuration to the absolute target
    displacement in *n_steps* equal increments. SmartAnalyze manages test
    tolerance and algorithm fallback internally.

    Args:
        odb: Active CreateODB instance.
        target_disp: Absolute target displacement (mm) from origin.
        n_steps: Number of sub-steps for the push.
    """
    current = ops.nodeDisp(ctrl_node, ctrl_dof)
    remaining = target_disp - current
    if abs(remaining) < 1e-12:
        return

    dU = remaining / n_steps

    ops.wipeAnalysis()
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

    for _ in range(n_steps):
        ok = analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=dU)
        if ok != 0:
            print(f"  Warning: push failed at target {target_disp:.3f} mm")
            break
        odb.fetch_response_step()
    analysis.close()


def run_pushover(odb: "opst.post.CreateODB") -> None:
    """Run monotonic or cyclic displacement-controlled pushover."""
    if CYCLIC:
        print("  Cyclic pushover (23 segments)")
        cum_disp = 0.0
        for i, delta in enumerate(cyclic_delta):
            cum_disp += delta
            print(f"    Segment {i + 1}: → {cum_disp:.2f} mm")
            _push_segment(odb, cum_disp, n_horizontal_steps)
    else:
        print(f"  Monotonic pushover: → {monotonic_target:.1f} mm")
        _push_segment(odb, monotonic_target, n_horizontal_steps)


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + pushover, return ODB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)                         # V1
    define_elements()
    vis_model(output_dir)                         # V2
    odb = create_odb(odb_tag=1)
    define_gravity_loads()
    define_lateral_loads()
    vis_loads(output_dir)                         # V3
    vis_pre_analysis(output_dir)                  # V4

    run_gravity(odb)
    run_pushover(odb)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    odb.save_response()
    if not _headless():
        fig = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1,
            slides=True,
            defo_scale=30.0,
            resp_type="disp",
            resp_dof=("UX",),
        )
        fig.write_html(str(output_dir / "vis_05_deformed_UX.html"))
        print("  HTML output written.")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    mode = "CYCLIC" if CYCLIC else "MONOTONIC"
    print(f"--- Citiner: {mode} RC column pushover ---")
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print(f"Analysis complete. Results in {output_dir}/")
