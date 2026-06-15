# ── 0. FILE HEADER ──────────────────────────────────────────────────────────────
"""
Model    : 2D Elastic Truss — Static Point Load + El Centro Dynamic Analysis
UniqueID : XMU_Chapter2
Author   : XMU (Xiamen University) — Chapter 2 Example
Date     : 2026-06-15
Purpose  : Textbook-example dynamic time-history analysis of a 2D elastic
           three-bar truss under static preload followed by El Centro ground
           motion (NS component, factor 3.0).
Ref      : XMU Finite Element Analysis course, Chapter 2
Units    : N, mm, MPa  (see standards/units.py)
Notes    : Converted from tcl_ref/model.tcl.
           Original units: kips, inches, ksi (imperial).
           ndf=2 model (no rotational DOFs) — truss-only.
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
MAT_ELASTIC = 1

NODE_1 = 1
NODE_2 = 2
NODE_3 = 3
NODE_4 = 4  # apex

ELE_TRUSS_1 = 1
ELE_TRUSS_2 = 2
ELE_TRUSS_3 = 3

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────────
# --- Geometry (original: inches) ---
x1, y1 = 0.0, 0.0
x2, y2 = 144.0 * inch, 0.0
x3, y3 = 168.0 * inch, 0.0
x4, y4 = 72.0 * inch, 96.0 * inch

# --- Material ---
E_elastic = 3000.0 * ksi                         # elastic modulus  [MPa]

# --- Truss areas (original: in²) ---
A_truss_1 = 10.0 * inch**2                       # left diagonal  [mm²]
A_truss_2 = 5.0 * inch**2                        # middle vertical  [mm²]
A_truss_3 = 5.0 * inch**2                        # right diagonal  [mm²]

# --- Point load at apex (original: kip) ---
Px_apex = 100.0 * kip                            # horizontal  [N]
Py_apex = -50.0 * kip                            # vertical (downward)  [N]

# --- Mass at apex (original: kip·s²/in) ---
mass_apex = 100.0 * kip / inch                   # mass in X and Y  [N·s²/mm]

# --- Ground motion ---
gm_dir     = Path(__file__).parent / "ground_motions"
gm_file_x  = "elcentro.txt"
gm_factor  = 3.0                                 # scale factor × g
gm_dt      = 0.01                                # time step  [s]
gm_npts    = 2000                                # steps to run

# --- Analysis ---
n_steps_gravity = 10
n_steps_free    = 0                              # no free-vibration tail
odb_every_n     = 5

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────────
def init_model() -> None:
    """Initialise 2D model (ndm=2, ndf=2 — no rotational DOFs)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 2)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Single elastic material for all truss elements."""
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC, E_elastic)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────────
def define_sections() -> None:
    """Truss elements use area directly — no section objects needed."""
    pass


# ── 7. NODES ─────────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Create 4 nodes: 3 fixed base nodes + 1 free apex node."""
    ops.node(NODE_1, x1, y1)
    ops.node(NODE_2, x2, y2)
    ops.node(NODE_3, x3, y3)
    ops.node(NODE_4, x4, y4)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix all three base nodes; lump mass at apex."""
    ops.fix(NODE_1, 1, 1)
    ops.fix(NODE_2, 1, 1)
    ops.fix(NODE_3, 1, 1)
    ops.mass(NODE_4, mass_apex, mass_apex)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Three elastic truss elements connecting base nodes to apex."""
    ops.element("Truss", ELE_TRUSS_1, NODE_1, NODE_4, A_truss_1, MAT_ELASTIC)
    ops.element("Truss", ELE_TRUSS_2, NODE_2, NODE_4, A_truss_2, MAT_ELASTIC)
    ops.element("Truss", ELE_TRUSS_3, NODE_3, NODE_4, A_truss_3, MAT_ELASTIC)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise ODB after model is fully built."""
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=1)
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Apply static point load at apex node (preload)."""
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(NODE_4, Px_apex, Py_apex)


def define_ground_motion() -> tuple:
    """Define UniformExcitation ground motion in X-direction.

    Returns (dt, npts) for use by the dynamic solver.
    """
    path_x = gm_dir / gm_file_x
    if not path_x.exists():
        raise FileNotFoundError(f"Ground motion file not found: {path_x}")
    accel_raw = np.loadtxt(path_x)
    npts = min(len(accel_raw), gm_npts)
    accel = accel_raw[:npts]

    # File values are in g; scale by gm_factor and convert to mm/s²
    factor = gm_factor * g_accel
    ops.timeSeries("Path", 101, "-dt", gm_dt, "-values", *accel,
                   "-factor", factor)
    ops.pattern("UniformExcitation", 2, 1, "-accel", 101)

    return gm_dt, npts


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────────

_peak_disp_x  = 0.0
_peak_disp_y  = 0.0
_peak_reac_1x = 0.0
_peak_reac_1y = 0.0
_peak_reac_2x = 0.0
_peak_reac_2y = 0.0
_peak_reac_3x = 0.0
_peak_reac_3y = 0.0
_collapse_status = "no_collapse"


def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10) -> None:
    """Apply static point load via load-controlled static analysis."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandSPD")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.test("NormDispIncr", 1.0e-6, 6)
    ops.algorithm("Newton")
    ops.analysis("Static")

    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def _track_edps() -> None:
    """Update peak displacements and reactions from current converged state."""
    global _peak_disp_x, _peak_disp_y
    global _peak_reac_1x, _peak_reac_1y
    global _peak_reac_2x, _peak_reac_2y
    global _peak_reac_3x, _peak_reac_3y

    _peak_disp_x = max(_peak_disp_x, abs(ops.nodeDisp(NODE_4, 1)))
    _peak_disp_y = max(_peak_disp_y, abs(ops.nodeDisp(NODE_4, 2)))

    _peak_reac_1x = max(_peak_reac_1x, abs(ops.nodeReaction(NODE_1, 1)))
    _peak_reac_1y = max(_peak_reac_1y, abs(ops.nodeReaction(NODE_1, 2)))
    _peak_reac_2x = max(_peak_reac_2x, abs(ops.nodeReaction(NODE_2, 1)))
    _peak_reac_2y = max(_peak_reac_2y, abs(ops.nodeReaction(NODE_2, 2)))
    _peak_reac_3x = max(_peak_reac_3x, abs(ops.nodeReaction(NODE_3, 1)))
    _peak_reac_3y = max(_peak_reac_3y, abs(ops.nodeReaction(NODE_3, 2)))


def run_dynamic(
    odb: "opst.post.CreateODB",
    dt: float,
    npts: int,
    odb_every_n: int = 5,
) -> None:
    """Run transient dynamic analysis with SmartAnalyze + Newmark."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandSPD")
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
    """Flush ODB, write EDPs to JSON, and generate deformation visualizations.

    Returns:
        dict mapping EDP name → value.
    """
    odb.save_response()

    edp_values = {
        "1-PID-4-1": _peak_disp_x,
        "1-PID-4-2": _peak_disp_y,
        "1-PFB-1-1": _peak_reac_1x,
        "1-PFB-1-2": _peak_reac_1y,
        "1-PFB-2-1": _peak_reac_2x,
        "1-PFB-2-2": _peak_reac_2y,
        "1-PFB-3-1": _peak_reac_3x,
        "1-PFB-3-2": _peak_reac_3y,
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
