# ── 0. FILE HEADER ──────────────────────────────────────────────────────────────
"""
Model    : Single quadUP Soil Element — Consolidation + Cyclic Horizontal Load
UniqueID : XMU_Chapter8_1
Author   : XMU (Xiamen University) — Chapter 8.1 Example
Date     : 2026-06-16
Purpose  : Demonstrate coupled u-p (solid-fluid) analysis of a 1×1 m saturated
           soil element using PressureDependMultiYield under consolidation
           followed by cyclic horizontal loading.
Ref      : XMU Finite Element Analysis course, Chapter 8.1
Units    : kN, m, sec, kPa  (coupled u-p — fluid properties are physical SI constants)
Notes    : Converted from model.tcl.
           * Source uses XMU-custom BoundingSurfaceSand — substituted with standard
             PressureDependMultiYield (PDMY). Parameter mapping: rad→deg, MPa→kPa.
           * First model in catalogue to retain source units — converting densities to
             N-mm (~10⁻⁹) would risk numerical conditioning in the u-p formulation.
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_pre_analysis

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────────
MAT_PDMY = 1
ELE_QUAD = 1

NODE_1 = 1  # bottom-left
NODE_2 = 2  # bottom-right
NODE_3 = 3  # top-left
NODE_4 = 4  # top-right

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────────
# --- Geometry (kN-m-kPa — coupled u-p retains source units) ---
x1, y1 = 0.0, 0.0
x2, y2 = 1.0, 0.0
x3, y3 = 0.0, 1.0
x4, y4 = 1.0, 1.0
quad_thickness = 1.0                        # element thickness  [m]

# --- Soil: PressureDependMultiYield (mapped from BoundingSurfaceSand) ---
pdmy_rho                = 1.90              # mass density  [Mg/m³]
pdmy_refShearModul      = 506.6             # Gr (0.5066 MPa → kPa)  [kPa]
pdmy_refBulkModul       = 200000.0          # Br (200 MPa → kPa)  [kPa]
pdmy_frictionAng        = 47.0              # φ (0.818 rad → degrees)  [°]
pdmy_peakShearStra      = 0.05              # peak shear strain
pdmy_refPress           = 101.325           # reference pressure  [kPa]
pdmy_pressDependCoe     = 1.01537           # pressure dependency coefficient
pdmy_phaseTransformAng  = 31.0              # PT angle (0.5423 rad → degrees)  [°]
pdmy_contractionParam1  = 0.75              # contraction parameter 1
pdmy_dilationParam1     = 0.0               # dilation parameter 1
pdmy_dilationParam2     = 1.0               # dilation parameter 2
pdmy_liquefactionParam1 = 1.9               # liquefaction parameter 1
pdmy_liquefactionParam2 = 0.1811            # liquefaction parameter 2
pdmy_liquefactionParam4 = 0.0               # liquefaction parameter 4
pdmy_numYieldSurf       = 20                # number of yield surfaces
pdmy_e                  = 0.6               # void ratio parameter
pdmy_volLimit1          = 0.9               # volume limit 1
pdmy_volLimit2          = 0.02              # volume limit 2
pdmy_volLimit3          = 0.7               # volume limit 3
pdmy_cohesi             = 0.0               # cohesion  [kPa]

# --- Fluid properties (kN-m-kPa) ---
water_bulk  = 2.2e6                          # water bulk modulus  [kPa]
water_rho   = 1.0                            # water density  [Mg/m³]
perm_x      = 5.09e-8                        # horizontal permeability  [m/s]
perm_y      = 5.09e-8                        # vertical permeability  [m/s]
body_force_x = 0.0                           # horizontal body force  [kN/m³]
body_force_y = -480.0                        # vertical body force (downward)  [kN/m³]
additional_press = 0                         # additional pore pressure

# --- Consolidation ---
consol_dt     = 5000.0                       # initial time step  [s]
consol_dt_min = 50.0                         # minimum time step  [s]
consol_dt_max = 5000.0                       # maximum time step  [s]
consol_Jd     = 20                           # sub-steps
consol_n1     = 5                            # steps phase 1
consol_n2     = 3                            # steps phase 2

# --- Cyclic loading ---
P_max       = 20.0                           # peak horizontal load  [kN]
cycle_dt    = 0.01                           # dynamic time step  [s]
cycle_n     = 4000                           # number of steps

# --- Rayleigh damping (dynamic phase only) ---
rayleigh_alpha = 0.0
rayleigh_beta  = 0.02

# --- ODB ---
ODB_TAG    = 1
out_dir    = Path(__file__).parent / "output"

# ── 4. MODEL BUILD ───────────────────────────────────────────────────────────────
def build_model() -> None:
    """Create 4-node, 1-element quadUP model (ndm=2, ndf=3: UX, UY, PWP)."""
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)

    # ── §5  Materials ──
    _define_materials()

    # ── §7  Nodes ──
    _create_nodes()

    # ── §8  Boundary Conditions ──
    _apply_bcs()

    # ── §9  Elements ──
    _create_elements()

    # ── §10 Recorders ──
    _setup_recorders()

    print("  Model build complete: 4 nodes, 1 quadUP element")


def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialize ODB after model is fully built."""
    opst.post.set_odb_path(str(output_dir))
    node_tags = [NODE_1, NODE_2, NODE_3, NODE_4]
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        node_tags=node_tags,
    )
    odb.save_model_data()
    return odb

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────────
def _define_materials() -> None:
    """PressureDependMultiYield — substituted from source BoundingSurfaceSand."""
    ops.nDMaterial(
        "PressureDependMultiYield", MAT_PDMY, 2,
        pdmy_rho,
        pdmy_refShearModul,
        pdmy_refBulkModul,
        pdmy_frictionAng,
        pdmy_peakShearStra,
        pdmy_refPress,
        pdmy_pressDependCoe,
        pdmy_phaseTransformAng,
        pdmy_contractionParam1,
        pdmy_dilationParam1,
        pdmy_dilationParam2,
        pdmy_liquefactionParam1,
        pdmy_liquefactionParam2,
        pdmy_liquefactionParam4,
        pdmy_numYieldSurf,
        pdmy_e,
        pdmy_volLimit1,
        pdmy_volLimit2,
        pdmy_volLimit3,
        pdmy_cohesi,
    )

# ── 7. NODES ─────────────────────────────────────────────────────────────────────
def _create_nodes() -> None:
    """Create 4 corner nodes of the 1×1 m soil element."""
    ops.node(NODE_1, x1, y1)
    ops.node(NODE_2, x2, y2)
    ops.node(NODE_3, x3, y3)
    ops.node(NODE_4, x4, y4)

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────────
def _apply_bcs() -> None:
    """Fix base in UX,UY; fix top in PWP (free-draining surface); periodic tie."""
    # Base: fixed in UX, UY (free in PWP)
    ops.fix(NODE_1, 1, 1, 0)
    ops.fix(NODE_2, 1, 1, 0)
    # Top: fixed in PWP only (free-draining surface)
    ops.fix(NODE_3, 0, 0, 1)
    ops.fix(NODE_4, 0, 0, 1)
    # Lateral periodicity: tie top nodes in UX, UY
    ops.equalDOF(NODE_3, NODE_4, 1, 2)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────────
def _create_elements() -> None:
    """Single quadUP element: coupled solid-fluid (u-p) formulation."""
    ops.element(
        "quadUP",
        ELE_QUAD,
        NODE_1, NODE_2, NODE_4, NODE_3,          # counter-clockwise
        quad_thickness,
        MAT_PDMY,
        water_bulk,
        water_rho,
        perm_x,
        perm_y,
        body_force_x,
        body_force_y,
        additional_press,
    )

# ── 10. RECORDERS ────────────────────────────────────────────────────────────────
def _setup_recorders() -> None:
    """Element stress/strain recorders matching Tcl source + ODB."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # Direct file recorders (matching Tcl)
    ops.recorder(
        "Element", "-ele", ELE_QUAD, "-time", "-file",
        str(out_dir / "stress.out"), "material", 1, "stress",
    )
    ops.recorder(
        "Element", "-ele", ELE_QUAD, "-time", "-file",
        str(out_dir / "strain.out"), "material", 1, "strain",
    )

    pass  # ODB initialized separately via create_odb() after model is built

# ── 11. LOADING ──────────────────────────────────────────────────────────────────
def _define_loading() -> None:
    """Define cyclic horizontal loading — applied in dynamic phase after consolidation."""
    # Loading is defined in run_dynamic() since it requires domain time context
    # after consolidation. Body force (gravity) is embedded in quadUP element.
    pass

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────────
def run_consolidation() -> None:
    """Phase 1: Consolidation with VariableTransient analysis."""
    print("--- Consolidation Phase ---")

    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.test("NormDispIncr", 1.0e-8, 50, 1)
    ops.algorithm("KrylovNewton")
    ops.constraints("Transformation")
    ops.integrator("Newmark", 1.5, 1.0)
    ops.analysis("VariableTransient")

    t0 = ops.getTime()
    print(f"  Phase 1a: {consol_n1} steps at dt={consol_dt}...")
    ops.analyze(consol_n1, consol_dt, consol_dt_min, consol_dt_max, consol_Jd)
    print(f"    Time: {t0:.0f} -> {ops.getTime():.0f} s")

    # Switch material to plastic stage
    ops.updateMaterialStage("-material", MAT_PDMY, "-stage", 1)

    print(f"  Phase 1b: {consol_n2} more steps...")
    ops.analyze(consol_n2, consol_dt, consol_dt_min, consol_dt_max, consol_Jd)
    print(f"    Time: {ops.getTime():.0f} s")
    print("  Consolidation complete.")


def run_dynamic(odb: "opst.post.CreateODB") -> None:
    """Phase 2: Cyclic horizontal loading via Transient analysis."""
    print("--- Dynamic Phase ---")

    ops.wipeAnalysis()  # preserves domain state + time

    # Build cyclic loading pattern (Series time series)
    # Domain time ≈ 40000s after consolidation; Series times align with this clock
    t_start = int(ops.getTime())
    cycle_times = [float(t_start + i) for i in range(42)]

    cycle_vals = [0.0]
    for i in range(20):
        cycle_vals.extend([-1.0, 1.0])
    cycle_vals.append(-1.0)  # 0, -1, 1, -1, ..., -1 (41 values)
    if len(cycle_vals) < len(cycle_times):
        cycle_vals.append(-1.0)

    # Match lengths
    n_pts = min(len(cycle_times), len(cycle_vals))
    cycle_times = cycle_times[:n_pts]
    cycle_vals = cycle_vals[:n_pts]

    # Plain load pattern: horizontal at top nodes
    ops.timeSeries("Series", 2, "-values", *cycle_vals, "-time", *cycle_times)
    ops.pattern("Plain", 2, 2)
    ops.load(NODE_3, P_max, 0.0, 0.0)
    ops.load(NODE_4, P_max, 0.0, 0.0)

    # Analysis setup
    ops.constraints("Transformation")
    ops.test("NormDispIncr", 1.0e-8, 50, 0)
    ops.numberer("RCM")
    ops.algorithm("Newton")
    ops.system("BandGeneral")
    ops.rayleigh(rayleigh_alpha, 0.0, rayleigh_beta, 0.0)

    beta_int = pow(0.6 + 0.5, 2) / 4  # = 0.3025
    ops.integrator("Newmark", 0.6, beta_int)
    ops.analysis("Transient")

    print(f"  Running {cycle_n} steps at dt={cycle_dt}...")
    print(f"  Domain time: {ops.getTime():.0f} -> {ops.getTime() + cycle_n * cycle_dt:.0f} s")

    for i in range(cycle_n):
        ok = ops.analyze(1, cycle_dt)
        if ok != 0:
            print(f"  Dynamic FAILED at step {i + 1}")
            break
        odb.fetch_response_step()
    else:
        print(f"  Dynamic complete. Final time: {ops.getTime():.2f} s")


# ── 13. POST-PROCESS ─────────────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB") -> None:
    """Save ODB responses and generate visualizations."""
    odb.save_response()
    print("  ODB responses saved.")

    if _headless():
        print("  OPENSEES_HEADLESS=1 — skipping visualization.")
        return

    print("  Peak deformation view ...")
    opst.vis.plotly.plot_nodal_responses(
        odb_tag=ODB_TAG, step="absMax", defo_scale=True,
        resp_type="disp", resp_dof="UX",
    ).write_html(str(out_dir / "vis_05_deformed_peak.html"))
    print("    -> vis_05_deformed_peak.html")

    print("  Step-by-step slider view ...")
    opst.vis.plotly.plot_nodal_responses(
        odb_tag=ODB_TAG, slides=True, defo_scale=True,
        resp_type="disp", resp_dof="UX",
    ).write_html(str(out_dir / "vis_06_deformed_slider.html"))
    print("    -> vis_06_deformed_slider.html")

    print("Done.")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────────
def main() -> None:
    """Run full model: build → consolidation → dynamic → post-process."""
    print("=" * 70)
    print("XMU Chapter 8.1 — Single quadUP Soil Element")
    print("Coupled u-p analysis: Consolidation + Cyclic Horizontal Loading")
    print("=" * 70)

    out_dir.mkdir(parents=True, exist_ok=True)

    build_model()
    odb = create_odb(out_dir)

    print("\n--- Pre-analysis Visualization ---")
    try:
        vis_pre_analysis(output_dir=out_dir)
    except Exception as e:
        print(f"  Skipped: {e}")

    print()
    run_consolidation()

    print()
    run_dynamic(odb)

    print()
    post_process(odb)

    print(f"\nOutput files written to: {out_dir}")
    print("Done.")


if __name__ == "__main__":
    main()
