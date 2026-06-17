# ── 0. FILE HEADER ──────────────────────────────────────────────────────────────
"""
Model    : Steel01 Parameter Optimization — Truss under Tabas Earthquake
UniqueID : XMU_Chapter9
Author   : XMU (Xiamen University) — Chapter 9
Date     : 2026-06-17
Purpose  : Demonstrate material parameter optimization with scipy.optimize.
           A 3-element truss is subjected to the Tabas earthquake, and 6 Steel01
           parameters (E1, fy1, b1, E2, fy2, b2) are calibrated to match experimental
           node 4 displacement data via sum-of-squared-errors minimization.
Ref      : XMU Finite Element Analysis course, Chapter 9
Units    : N, mm, MPa, s  (see standards/units.py)
Notes    : Converted from main.tcl + tclFileToRun.tcl + F.tcl.
           * SNOPT replaced with scipy.optimize.minimize (L-BFGS-B).
           * SI (N, m, kg, Pa) → N-mm-MPa.
           * AGENT.md v1.15.0: SmartAnalyze + ODB + opstool vis (June 2026).
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────────
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")  # Windows: rich emoji in SmartAnalyze

import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────────
MAT_1 = 1
MAT_2 = 2

NODE_1 = 1
NODE_2 = 2
NODE_3 = 3
NODE_4 = 4

ELE_1 = 1
ELE_2 = 2
ELE_3 = 3

GM_SERIES   = 1
PATTERN_TAG = 1

ODB_TAG = 1

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
GM_DIR     = SCRIPT_DIR / "ground_motions"
TABAS_PATH = GM_DIR / "tabas.txt"
EXP_PATH   = SCRIPT_DIR / "node4_exp.txt"
OUTPUT_DIR = SCRIPT_DIR / "output"

# --- Geometry (SI m → N-mm) ---
COORDS = {
    NODE_1: (0.0,        0.0),
    NODE_2: (10.0 * m,   0.0),
    NODE_3: (20.0 * m,   0.0),
    NODE_4: (30.0 * m,   0.0),
}

# --- Element cross-sectional areas (SI m² → mm²) ---
AREA_1 = 0.01 * m**2   # 10 000 mm²
AREA_2 = 0.02 * m**2   # 20 000 mm²
AREA_3 = 0.02 * m**2

# --- Nodal masses (SI kg → N·s²/mm, ÷1000) ---
MASS_2 = 3174.1 / 1000     # 3.1741 N·s²/mm
MASS_3 = 4174.1 / 1000     # 4.1741 N·s²/mm
MASS_4 = 5174.1 / 1000     # 5.1741 N·s²/mm

# --- Ground motion (Tabas) ---
GM_DT     = 0.02            # time step  [s]
GM_FACTOR = 9.8 * m         # g → mm/s²  (9.8 m/s² × 1000 mm/m = 9800 mm/s²)

# --- Transient analysis ---
N_STEPS        = 2000
DT             = 0.01        # [s]
NEWMARK_GAMMA  = 0.55
NEWMARK_BETA   = 0.275625

# --- ODB throttling (2000 steps / 5 = 400 fetch calls, within §3d limit) ---
ODB_EVERY_N = 5

# --- Optimization bounds (converted from SI Pa → N-mm-MPa) ---
BOUNDS = [
    (1.0e2, 1.0e14),     # E1   [MPa]
    (1.0e-1, 1.0e14),    # fy1  [MPa]
    (0.0,    1.0),        # b1   [-]
    (1.0e2, 1.0e14),     # E2   [MPa]
    (1.0e-1, 1.0e14),    # fy2  [MPa]
    (0.0,    1.0),        # b2   [-]
]

# Starting point (SI Pa → MPa, divide by 1e6)
X0 = [
    1.8e2,    # E1  = 1.8e8 Pa(SI) → 180 MPa
    2.7e-1,   # fy1 = 2.7e5 Pa(SI) → 0.27 MPa
    0.016,    # b1  (dimensionless)
    1.8e2,    # E2  → 180 MPa
    2.7e-1,   # fy2 → 0.27 MPa
    0.016,    # b2
]

# Experimental data — loaded once in main(), cached here for objective()
_exp_disp = None


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 2)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────────
def define_materials(E1: float, fy1: float, b1: float,
                     E2: float, fy2: float, b2: float) -> None:
    ops.uniaxialMaterial("Steel01", MAT_1, fy1, E1, b1)
    ops.uniaxialMaterial("Steel01", MAT_2, fy2, E2, b2)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────────
# (ndf=2 truss — not applicable; area given on element command)


# ── 7. NODES ─────────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    ops.node(NODE_1, *COORDS[NODE_1])
    ops.node(NODE_2, *COORDS[NODE_2], "-mass", MASS_2, 0.0)
    ops.node(NODE_3, *COORDS[NODE_3], "-mass", MASS_3, 0.0)
    ops.node(NODE_4, *COORDS[NODE_4], "-mass", MASS_4, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    ops.fix(NODE_1, 1, 1)   # fixed base
    ops.fix(NODE_2, 0, 1)   # roller (Y restrained)
    ops.fix(NODE_3, 0, 1)
    ops.fix(NODE_4, 0, 1)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────────
def define_elements() -> None:
    ops.element("truss", ELE_1, NODE_1, NODE_2, AREA_1, MAT_1)
    ops.element("truss", ELE_2, NODE_2, NODE_3, AREA_2, MAT_2)
    ops.element("truss", ELE_3, NODE_3, NODE_4, AREA_3, MAT_1)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        node_tags=[NODE_1, NODE_2, NODE_3, NODE_4],
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────────
def define_loading() -> None:
    ops.timeSeries("Path", GM_SERIES, "-filePath", str(TABAS_PATH),
                   "-dt", GM_DT, "-factor", GM_FACTOR)
    ops.pattern("UniformExcitation", PATTERN_TAG, 1, "-accel", GM_SERIES)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────────
def build_model(E1: float, fy1: float, b1: float,
                E2: float, fy2: float, b2: float) -> None:
    """Shared construction for both optimization and visualization paths."""
    init_model()
    define_nodes()
    define_boundary_conditions()
    define_materials(E1, fy1, b1, E2, fy2, b2)
    define_elements()


def run_obj_fem(E1: float, fy1: float, b1: float,
                E2: float, fy2: float, b2: float) -> np.ndarray:
    """Build model, run SmartAnalyze Transient, return node-4 UX [mm].

    Lean path for scipy optimization — no ODB, no file I/O.
    Tracks displacement in-memory via ops.nodeDisp() each step.
    Raises RuntimeError on non-convergence (caught by objective → penalty).
    """
    build_model(E1, fy1, b1, E2, fy2, b2)
    define_loading()

    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandSPD")
    ops.integrator("Newmark", NEWMARK_GAMMA, NEWMARK_BETA)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )

    segs = analysis.transient_split(N_STEPS)
    ux_history = np.empty(N_STEPS)

    for i, _ in enumerate(segs):
        ok = analysis.TransientAnalyze(DT)
        if ok < 0:
            analysis.close()
            raise RuntimeError(f"Transient analysis failed at step {i}")
        ux_history[i] = ops.nodeDisp(NODE_4, 1)

    analysis.close()
    return ux_history


def run_fem_full(odb: "opst.post.CreateODB",
                 E1: float, fy1: float, b1: float,
                 E2: float, fy2: float, b2: float,
                 output_dir: Path | None = None) -> None:
    """Run SmartAnalyze Transient with throttled ODB collection.

    odb is populated in-place (fetch_response_step every ODB_EVERY_N steps).
    Full-resolution UX saved to node4_optimised.out for post_process.py.
    """
    define_loading()

    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandSPD")
    ops.integrator("Newmark", NEWMARK_GAMMA, NEWMARK_BETA)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )

    segs = analysis.transient_split(N_STEPS)
    t_current = 0.0
    step_count = 0
    ux_full = []

    for i, _ in enumerate(segs):
        ok = analysis.TransientAnalyze(DT)
        if ok < 0:
            print(f"  Dynamic analysis failed at t = {t_current:.3f} s (step {i})")
            break
        t_current += DT
        step_count += 1

        ux_full.append(ops.nodeDisp(NODE_4, 1))

        if i % ODB_EVERY_N == 0:
            odb.fetch_response_step()

    analysis.close()

    if output_dir is not None and step_count > 0:
        times = np.arange(DT, (step_count + 1) * DT, DT)
        np.savetxt(output_dir / "node4_optimised.out",
                   np.column_stack([times[:step_count], ux_full]),
                   header="time ux_fem", comments="")
        print(f"  Full-resolution UX saved to {output_dir / 'node4_optimised.out'}")

    print(f"  Completed {step_count} steps (t_final = {t_current:.3f} s)")


def run_analysis(output_dir: Path,
                 E1: float, fy1: float, b1: float,
                 E2: float, fy2: float, b2: float) -> "opst.post.CreateODB":
    """AGENT.md-compliant entry point: build + ODB + vis + transient.

    Returns the populated ODB for post_process().
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    build_model(E1, fy1, b1, E2, fy2, b2)

    vis_nodes(output_dir)                        # V1 — after BCs
    vis_model(output_dir)                        # V2 — after elements

    odb = create_odb(output_dir)

    define_loading()
    vis_loads(output_dir)                        # V3 — after loading
    vis_pre_analysis(output_dir)                 # V4 — before solver

    run_fem_full(odb, E1, fy1, b1, E2, fy2, b2, output_dir=output_dir)

    return odb


def objective(x: np.ndarray) -> float:
    """Sum of squared errors between experimental and FEM node-4 UX displacement."""
    E1, fy1, b1, E2, fy2, b2 = x
    try:
        u_fem = run_obj_fem(E1, fy1, b1, E2, fy2, b2)
    except Exception:
        return 1e20  # penalty for non-convergent parameters

    n = min(len(u_fem), len(_exp_disp))
    return float(np.sum((_exp_disp[:n] - u_fem[:n]) ** 2))


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and render deformed-shape HTML."""
    odb.save_response()
    print("  ODB responses saved.")

    if _headless():
        print("  OPENSEES_HEADLESS=1 — skipping visualization.")
        return

    try:
        fig_peak = opst.vis.plotly.plot_nodal_responses(
            odb_tag=ODB_TAG, step="absMax", defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig_peak.write_html(str(output_dir / "vis_05_deformed_peak.html"))
        print("  -> vis_05_deformed_peak.html")
    except Exception as e:
        print(f"  Peak deformed view skipped: {e}")

    try:
        fig_slider = opst.vis.plotly.plot_nodal_responses(
            odb_tag=ODB_TAG, slides=True, defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig_slider.write_html(str(output_dir / "vis_06_deformed_slider.html"))
        print("  -> vis_06_deformed_slider.html")
    except Exception as e:
        print(f"  Slider view skipped: {e}")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from scipy.optimize import minimize

    print("=" * 64)
    print("XMU Chapter 9 — Steel01 Parameter Optimization")
    print("=" * 64)

    # Load experimental displacement data once
    exp_data = np.loadtxt(EXP_PATH)
    _exp_disp = exp_data[:, 1]  # UX column (second column)
    print(f"Loaded {len(_exp_disp)} experimental data points from {EXP_PATH.name}")

    # --- Optimization ---
    print(f"\nStarting optimization (L-BFGS-B, max 50 iterations)...")
    print(f"  Initial x0: E1={X0[0]:.1f}, fy1={X0[1]:.4f}, b1={X0[2]:.4f}, "
          f"E2={X0[3]:.1f}, fy2={X0[4]:.4f}, b2={X0[5]:.4f}")
    print(f"  Initial F   = {objective(np.array(X0)):.6e}")
    print()

    result = minimize(
        objective,
        np.array(X0),
        method="L-BFGS-B",
        bounds=BOUNDS,
        options={"maxiter": 50, "disp": True, "ftol": 1e-12, "gtol": 1e-8},
    )

    print(f"\nOptimization finished: {result.message}")
    print(f"  Iterations : {result.nit}")
    print(f"  Final F    : {result.fun:.6e}")

    # --- Save results ---
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    E1_opt, fy1_opt, b1_opt, E2_opt, fy2_opt, b2_opt = result.x
    opt_results = {
        "E1_MPa":  float(E1_opt),
        "fy1_MPa": float(fy1_opt),
        "b1":      float(b1_opt),
        "E2_MPa":  float(E2_opt),
        "fy2_MPa": float(fy2_opt),
        "b2":      float(b2_opt),
        "F_final": float(result.fun),
        "nit":     int(result.nit),
        "message": str(result.message),
    }
    with open(OUTPUT_DIR / "opt_results.json", "w") as f:
        json.dump(opt_results, f, indent=2)
    print(f"  Results saved to {OUTPUT_DIR / 'opt_results.json'}")

    # --- Final AGENT.md-compliant run with optimised parameters ---
    print("\nRunning final analysis with optimised parameters (full ODB + vis)...")
    odb = run_analysis(OUTPUT_DIR,
                       E1_opt, fy1_opt, b1_opt,
                       E2_opt, fy2_opt, b2_opt)

    print()
    post_process(odb, OUTPUT_DIR)

    # Quick summary
    print(f"\nOptimised parameters (N-mm-MPa):")
    print(f"  E1  = {E1_opt:.2f} MPa")
    print(f"  fy1 = {fy1_opt:.6f} MPa")
    print(f"  b1  = {b1_opt:.6f}")
    print(f"  E2  = {E2_opt:.2f} MPa")
    print(f"  fy2 = {fy2_opt:.6f} MPa")
    print(f"  b2  = {b2_opt:.6f}")
    print(f"\n  Final objective F = {result.fun:.6e}")
    print(f"\nOutput files written to: {OUTPUT_DIR}")
    print("Done.")
