# ── 0. FILE HEADER ──────────────────────────────────────────────────────────────
"""
Model    : 2D Cantilever Column — Elastic Dynamic Analysis (Tabas EQ)
UniqueID : XMU_Chapter4_1
Author   : XMU (Xiamen University) — Chapter 4.1 Example
Date     : 2026-06-15
Purpose  : Textbook-example dynamic time-history analysis of a 2D elastic
           cantilever column (2 DOF system) under Tabas earthquake with
           Rayleigh damping (2% on mode 1).
Ref      : XMU Finite Element Analysis course, Chapter 4.1
Units    : N, mm, MPa  (see standards/units.py)
Notes    : Converted from model.tcl.
           Original units: N, m, kg, Pa (SI) — converted to N, mm, MPa.
           SI→N-mm: length ×1000, area ×1e6, inertia ×1e12.
           Pa in Tcl is NOT units.py Pa (which = N/mm² = MPa).
           30 GPa = 3.0e10 Pa(si) = 30000 N/mm². Mass ÷1000 (kg→tonne).
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────────
NODE_BASE = 1
NODE_MID  = 2
NODE_TOP  = 3

ELE_LOWER = 1
ELE_UPPER = 2

TRANS_LINEAR = 1

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────────
# --- Geometry (original: m) ---
h_story = 3.0 * m                                   # story height  [mm]
h_total = 6.0 * m                                   # total height  [mm]

# --- Section properties (original: m, m², m⁴) ---
A_col = 0.25 * m**2                                 # cross-section area  [mm²]
E_col = 30000.0 * MPa                               # 30 GPa = 3.0e10 Pa → 30000 MPa  [N/mm²]
I_col = 5.2e-3 * m**4                               # moment of inertia  [mm⁴]

# --- Mass (original: kg; converted to tonne = N·s²/mm) ---
mass_node = 10.0                                    # 10000 kg → 10 tonnes  [N·s²/mm]

# --- Gravity loads (original: N) ---
P_vertical = -1.0e5                                 # downward vertical load at each floor  [N]

# --- Damping ---
damp_ratio = 0.02                                   # Rayleigh damping ratio  [-]

# --- Ground motion ---
gm_dir     = Path(__file__).parent / "ground_motions"
gm_file_x  = "tabas.txt"
gm_dt      = 0.02                                   # time step  [s]
gm_npts    = 1000                                   # steps to run (first 1000 of 2501)

# --- Analysis ---
n_steps_gravity = 10
n_steps_free    = 0
odb_every_n     = 5

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────────
def init_model() -> None:
    """Initialise 2D model (ndm=2, ndf=3)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Elastic beam-column elements use E directly — no separate materials."""
    pass


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────────
def define_sections() -> None:
    """Elastic beam-column elements use A, E, I directly — no section objects."""
    pass


# ── 7. NODES ─────────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Create 3 nodes: fixed base + mid-height + top."""
    ops.node(NODE_BASE, 0.0, 0.0)
    ops.node(NODE_MID,  0.0, h_story)
    ops.node(NODE_TOP,  0.0, h_total)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix base node; assign lumped mass at mid and top nodes."""
    ops.fix(NODE_BASE, 1, 1, 1)
    ops.mass(NODE_MID, mass_node, 0.0, 0.0)
    ops.mass(NODE_TOP, mass_node, 0.0, 0.0)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Two elasticBeamColumn elements with Linear geometric transformation."""
    ops.geomTransf("Linear", TRANS_LINEAR)
    ops.element("elasticBeamColumn", ELE_LOWER,
                NODE_BASE, NODE_MID, A_col, E_col, I_col, TRANS_LINEAR)
    ops.element("elasticBeamColumn", ELE_UPPER,
                NODE_MID, NODE_TOP, A_col, E_col, I_col, TRANS_LINEAR)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise ODB after model is fully built."""
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=1)
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Apply vertical point loads at mid and top nodes."""
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(NODE_MID, 0.0, P_vertical, 0.0)
    ops.load(NODE_TOP, 0.0, P_vertical, 0.0)


def define_ground_motion() -> tuple:
    """Define UniformExcitation ground motion in X-direction (Tabas).

    Returns (dt, npts).
    """
    path_x = gm_dir / gm_file_x
    if not path_x.exists():
        raise FileNotFoundError(f"Ground motion file not found: {path_x}")
    accel_raw = np.loadtxt(path_x)
    npts = min(len(accel_raw), gm_npts)
    accel = accel_raw[:npts]

    # File values in g; convert to mm/s² via g_accel (=9810 mm/s²)
    ops.timeSeries("Path", 101, "-dt", gm_dt, "-values", *accel,
                   "-factor", g_accel)
    ops.pattern("UniformExcitation", 2, 1, "-accel", 101)

    return gm_dt, npts


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────────

_peak_drift_1 = 0.0
_peak_drift_2 = 0.0
_peak_disp_x  = 0.0
_peak_shear   = 0.0


def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10) -> None:
    """Apply vertical loads via load-controlled static analysis."""
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.test("NormDispIncr", 1.0e-8, 6)
    ops.algorithm("Newton")
    ops.analysis("Static")

    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def _track_edps() -> None:
    """Update peak drifts, top displacement, and base shear."""
    global _peak_drift_1, _peak_drift_2, _peak_disp_x, _peak_shear

    d_top = ops.nodeDisp(NODE_TOP, 1)
    d_mid = ops.nodeDisp(NODE_MID, 1)
    y_top = ops.nodeCoord(NODE_TOP, 2)
    y_mid = ops.nodeCoord(NODE_MID, 2)

    _peak_drift_1 = max(_peak_drift_1, abs(d_mid) / y_mid)
    _peak_drift_2 = max(_peak_drift_2, abs(d_top - d_mid) / (y_top - y_mid))
    _peak_disp_x  = max(_peak_disp_x,  abs(d_top))
    _peak_shear   = max(_peak_shear,   abs(ops.nodeReaction(NODE_BASE, 1)))


def run_dynamic(
    odb: "opst.post.CreateODB",
    dt: float,
    npts: int,
    odb_every_n: int = 5,
) -> None:
    """Run transient dynamic analysis with SmartAnalyze + Newmark.

    Rayleigh damping (2% on mode 1) computed from eigenvalue analysis.
    """
    # Eigen for Rayleigh damping
    eigenvalues = ops.eigen(1)
    omega1 = eigenvalues[0] ** 0.5
    T1 = 2.0 * np.pi / omega1
    f1 = 1.0 / T1
    print(f"  Mode 1: T1 = {T1:.4f} s,  f1 = {f1:.4f} Hz")

    # Rayleigh: a0=0 (mass-proportional), a1 = 2ξ/ω₁ (stiffness-proportional)
    a0 = 0.0
    a1 = 2.0 * damp_ratio / omega1
    ops.rayleigh(a0, 0.0, a1, 0.0)

    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.integrator("Newmark", 0.5, 0.25)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )

    total_steps = npts + n_steps_free
    segs = analysis.transient_split(total_steps)
    t_current = 0.0
    step_count = 0

    for i, seg in enumerate(segs):
        ok = analysis.TransientAnalyze(dt)
        if ok < 0:
            print(f"  Dynamic analysis failed at t = {t_current:.3f} s (step {i})")
            break
        t_current += dt
        step_count += 1

        if i % odb_every_n == 0:
            odb.fetch_response_step()
            _track_edps()

    analysis.close()
    print(f"  Completed {step_count} steps (t_final = {t_current:.3f} s)")


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + dynamic, return ODB for post-processing."""
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

    odb = create_odb(output_dir)

    define_gravity_loads()
    vis_loads(output_dir)

    print("Running static preload (gravity) ...")
    run_gravity(odb, n_steps=n_steps_gravity)

    # Ground motion MUST be defined after gravity (AGENT.md §12i)
    gm_dt, gm_npts = define_ground_motion()
    vis_pre_analysis(output_dir)

    print(f"Running dynamic analysis ({gm_npts} steps, dt={gm_dt:.3f} s) ...")
    run_dynamic(odb, gm_dt, gm_npts, odb_every_n=odb_every_n)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
) -> dict:
    """Flush ODB, write EDPs to JSON, and generate deformation visualizations."""
    odb.save_response()

    edp_values = {
        "1-PID-1-1": _peak_drift_1,
        "1-PID-2-1": _peak_drift_2,
        "1-PRD-1":   _peak_disp_x,
        "1-PFB-1":   _peak_shear,
        "collapse_status": 0,
    }

    import json
    edp_file = output_dir / "EDP.json"
    edp_list = [{"name": k, "value": v} for k, v in edp_values.items()]
    with open(edp_file, "w") as f:
        json.dump({"EDP": edp_list}, f, indent=2)
    print(f"EDP file written: {edp_file}")

    if not _headless():
        fig_defo = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, step="absMax", defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig_defo.write_html(str(output_dir / "vis_05_deformed_peak.html"))

        fig_slider = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, slides=True, defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig_slider.write_html(str(output_dir / "vis_06_deformed_slider.html"))

    return edp_values


# ── 14. MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    edps = post_process(odb, output_dir)
    print(f"\nExtracted {len(edps)} EDPs.")
