# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Sensitivity analysis of a 2D truss (XMU Chapter 11)
UniqueID : XMU_Chapter11
Author   : XMU Finite Element Analysis course
Date     : 2026-06-22
Purpose  : Textbook-example sensitivity analysis of a 2D truss under static
           lateral load followed by El Centro ground motion using DDM.
Ref      : XMU Finite Element Analysis course, Chapter 11.
Units    : N, mm, MPa
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
MAT_STEEL = 1

ELE_TRUSS_1 = 1
ELE_TRUSS_2 = 2

NODE_FIXED = 1
NODE_MID   = 2
NODE_LOAD  = 3

PARAM_STIFF = 1

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
L1     = 10.0 * m         # 10 m
L2     = 10.0 * m         # 10 m
A_truss = 0.1 * m**2      # 0.1 m^2
Fy     = 248200.0 * kPa   # 248200 kPa -> 248.2 MPa
E_mod  = 2.0e8 * kPa      # 2.0e8 kPa -> 200000 MPa
b_hard = 0.05

P_lateral = 2.0e4 * N     # 20000 N
mass_node = 100.0 / 1000.0  # 100 kg -> 0.1 N . s^2 / mm

GM_FILE   = Path(__file__).parent / "ground_motions" / "el.txt"
GM_DT     = 0.01
GM_FACTOR = 300.0

n_steps_static  = 10
n_steps_dynamic = 100
dt_dynamic      = 0.01
TOL_TEST  = 1.0e-12
MAX_ITER  = 25

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 2)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    ops.uniaxialMaterial("Steel01", MAT_STEEL, Fy, E_mod, b_hard)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
# Not used — truss elements carry area directly

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    ops.node(NODE_FIXED, 0.0,      0.0)
    ops.node(NODE_MID,   L1,       0.0)
    ops.node(NODE_LOAD,  L1 + L2,  0.0)

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    ops.fix(NODE_FIXED, 1, 1)
    ops.fix(NODE_MID,   0, 1)
    ops.fix(NODE_LOAD,  0, 1)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    ops.element("truss", ELE_TRUSS_1, NODE_FIXED, NODE_MID,   A_truss, MAT_STEEL)
    ops.element("truss", ELE_TRUSS_2, NODE_MID,   NODE_LOAD,  A_truss, MAT_STEEL)

# ── 10. SENSITIVITY PARAMETERS ───────────────────────────────────────────────
def define_sensitivity_params() -> None:
    ops.parameter(PARAM_STIFF, "element", ELE_TRUSS_1, "material", "E")
    ops.addToParameter(PARAM_STIFF, "element", ELE_TRUSS_2, "material", "E")

# ── 11. OUTPUT DATABASE (ODB) ───────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: int = 1) -> "opst.post.CreateODB":
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        save_nodal_resp=True,
        save_truss_resp=True,
        node_tags=[NODE_FIXED, NODE_MID, NODE_LOAD],
        truss_tags=[ELE_TRUSS_1, ELE_TRUSS_2],
    )
    odb.save_model_data()
    return odb

# ── 12. LOADING ──────────────────────────────────────────────────────────────
def define_static_load() -> None:
    """Define static lateral load at node 3 (ramp time series)."""
    ops.timeSeries(
        "Path", 1, "-time", 0, 0.5, 1.0, 10000.0,
        "-values", 0, 0.5, 1.0, 1.0,
    )
    ops.pattern("Plain", 1, 1)
    ops.load(NODE_LOAD, P_lateral, 0.0)

def define_ground_motion() -> None:
    """Define UniformExcitation ground motion from el.txt."""
    ops.timeSeries(
        "Path", 2, "-dt", GM_DT, "-filePath", str(GM_FILE),
        "-factor", GM_FACTOR,
    )
    ops.pattern("UniformExcitation", 2, 1, "-accel", 2)

# ── 13. ANALYSIS ─────────────────────────────────────────────────────────────
def run_static_sensitivity(output_dir: Path, odb: "opst.post.CreateODB") -> None:
    """Load-controlled static analysis with DDM sensitivity.

    NOTE: Uses manual ops.analyze() loop instead of SmartAnalyze because
    SmartAnalyze does not support sensitivity computation (DDM).
    This is a documented exception per AGENT.md Section 10.
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", TOL_TEST, MAX_ITER, 2)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / n_steps_static)
    ops.analysis("Static")
    ops.sensitivityAlgorithm("-computeAtEachStep")

    for _ in range(n_steps_static):
        ops.analyze(1)
        odb.fetch_response_step()
    ops.loadConst("-time", 0.0)

def run_dynamic_sensitivity(output_dir: Path, odb: "opst.post.CreateODB") -> None:
    """Transient analysis with DDM sensitivity.

    NOTE: Uses manual ops.analyze() loop instead of SmartAnalyze because
    SmartAnalyze does not support sensitivity computation (DDM).
    """
    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", TOL_TEST, MAX_ITER, 2)
    ops.algorithm("Newton")
    ops.integrator("Newmark", 0.5, 0.25)
    ops.analysis("Transient")
    ops.sensitivityAlgorithm("-computeAtEachStep")

    for _ in range(n_steps_dynamic):
        ops.analyze(1, dt_dynamic)
        odb.fetch_response_step()

def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run static + dynamic analysis with sensitivity, return ODB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))
    init_model()
    define_materials()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)
    define_sensitivity_params()
    odb = create_odb(output_dir=output_dir, odb_tag=1)
    ops.recorder(
        "Node", "-file", str(output_dir / "ddm2E.out"),
        "-time", "-precision", 16, "-node", NODE_MID, "-dof", 1,
        f"sensitivity {PARAM_STIFF}",
    )
    define_static_load()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    run_static_sensitivity(output_dir, odb)
    ops.mass(NODE_FIXED, mass_node, 0.0)
    ops.mass(NODE_MID,   mass_node, 0.0)
    ops.mass(NODE_LOAD,  mass_node, 0.0)
    define_ground_motion()
    run_dynamic_sensitivity(output_dir, odb)
    return odb

# ── 14. POST-PROCESSING ─────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    odb.save_response()
    if not _headless():
        fig_defo = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, resp_type="disp", resp_dof="UX",
        )
        fig_defo.write_html(str(output_dir / "vis_05_deformed.html"))

# ── 15. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
