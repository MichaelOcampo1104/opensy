# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 3D wheelset-rigid-track interaction (XMU Chapter 13.2)
UniqueID : XMU_Chapter13_2
Author   : XMU Finite Element Analysis course
Date     : 2026-06-23
Purpose  : 3D single-wheelset model on rigid track with SP-based wheel-rail
           contact, lateral excitation, and transient dynamics.
Ref      : XMU Finite Element Analysis course, Chapter 13.2.
Units    : m, kg, N, Pa, sec (SI)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import time
import openseespy.opensees as ops
import opstool as opst
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
TRANSF_RAIL       = 2
TRANSF_WHEELSET   = 1

NODE_RAIL_LEFT    = 10000
NODE_RAIL_RIGHT   = 50000
NODE_WHEEL_LEFT   = 1
NODE_WHEEL_RIGHT  = 1001
NODE_WHEEL_L_EXT  = 51
NODE_WHEEL_R_EXT  = 1051
NODE_WHEEL_CENTER = 2001

TS_GRAVITY        = 2
PAT_GRAVITY       = 2
TS_LATERAL        = 3
PAT_LATERAL       = 3
TS_WHEEL          = 10
PAT_WHEEL         = 10

NODE_UY_SPRING    = 30000
MAT_UY_SPRING     = 5
ELE_UY_SPRING     = 30001

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Time integration
dT    = 0.001               # s (time step)
pVel  = 20.0                # m/s (train speed)
nL    = 100                 # static load steps
N_TRANSIENT = 6000

# Train geometry
R0     = 0.43               # m (wheel radius)

# Rail geometry
N_NODE_RAIL = 200
zr    = 0.15                # m (rail vertical offset)
wb    = 1.505               # m (rail gauge / spacing)
Lele  = 0.6                 # m (element length)

# Rail material (UIC50 profile)
Er_rail  = 2.06e11          # Pa
miuRail  = 0.296
Ar_rail  = 7.745e-3         # m^2
Gr_rail  = Er_rail / (1.0 + miuRail) / 2.0   # Pa
Jr_rail  = 2.104e-6         # m^4 (torsion constant)
Irz_rail = 5.24e-6          # m^4 (weak axis)
Iry_rail = 3.217e-5         # m^4 (strong axis)
mrail    = 60.64            # kg/m (rail mass per unit length)

# Wheelset masses / inertias
Mw  = 933.0     # wheelset mass (kg)
Iwx = 461.4     # wheelset moment of inertia X
Iwy = 61.6      # wheelset moment of inertia Y
Iwz = 461.4     # wheelset moment of inertia Z

# Rigid beam properties
ARigid  = 1.0e3             # m^2
ERigid  = 2.0e11            # Pa
GRigid  = 7.9e10            # Pa
IxRigid = 0.1               # m^4
IyRigid = 0.1               # m^4
IzRigid = 0.1               # m^4

# Wheelset geometry
y0 = 0.7523                 # m (half-gauge to wheel contact)
y1 = 0.90                   # m (half-gauge to extension)

g = 9.801                   # m/s^2

# Excitation time series
LAT_TIMES  = [0.0, 0.01, 0.02, 0.200001, 800.0]
LAT_VALUES = [0.0, 0.0, 2.48e-4, 0.0, 0.0]

GRAV_RAMP_TIMES  = [0.0, 0.01, 10000.0]
GRAV_RAMP_VALUES = [0.0, 1.0, 1.0]

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    pass

def define_geom_transf() -> None:
    ops.geomTransf("Linear", TRANSF_WHEELSET, 0, 0, 1)
    ops.geomTransf("Linear", TRANSF_RAIL, 0, 0, 1)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    pass

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def build_nodes() -> None:
    # Rail left: nodes 10001-10200
    for i in range(1, N_NODE_RAIL + 1):
        ops.node(i + NODE_RAIL_LEFT, (i - 1) * Lele, -wb / 2, -zr)
    # Rail right: nodes 50001-50200
    for i in range(1, N_NODE_RAIL + 1):
        ops.node(i + NODE_RAIL_RIGHT, (i - 1) * Lele, wb / 2, -zr)

def build_wheelset_nodes() -> None:
    # Wheelset nodes
    ops.node(NODE_WHEEL_LEFT,   0, -y0, R0)
    ops.node(NODE_WHEEL_RIGHT,  0,  y0, R0)
    ops.node(NODE_WHEEL_L_EXT,  0, -y1, R0)
    ops.node(NODE_WHEEL_R_EXT,  0,  y1, R0)
    ops.node(NODE_WHEEL_CENTER, 0,  0,  R0)
    # Auxiliary node for soft UY spring (eliminates rigid body mode)
    ops.node(NODE_UY_SPRING, 0, 0, R0)

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    # All rail nodes fully fixed (rigid track)
    for i in range(1, N_NODE_RAIL + 1):
        ops.fix(i + NODE_RAIL_LEFT, 1, 1, 1, 1, 1, 1)
        ops.fix(i + NODE_RAIL_RIGHT, 1, 1, 1, 1, 1, 1)
    # Wheelset center: fix UX (static only), UZ (rail contact), RY (pitch)
    ops.fix(NODE_WHEEL_CENTER, 1, 0, 1, 0, 1, 0)
    # Auxiliary fix for UY spring
    ops.fix(NODE_UY_SPRING, 1, 1, 1, 1, 1, 1)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def build_rail_elements() -> None:
    for i in range(1, N_NODE_RAIL):
        # Left rail beams
        ops.element("elasticBeamColumn", i + NODE_RAIL_LEFT,
                    i + NODE_RAIL_LEFT, i + NODE_RAIL_LEFT + 1,
                    Ar_rail, Er_rail, Gr_rail, Jr_rail, Iry_rail, Irz_rail,
                    TRANSF_RAIL, "-mass", mrail)
        # Right rail beams
        ops.element("elasticBeamColumn", i + NODE_RAIL_RIGHT,
                    i + NODE_RAIL_RIGHT, i + NODE_RAIL_RIGHT + 1,
                    Ar_rail, Er_rail, Gr_rail, Jr_rail, Iry_rail, Irz_rail,
                    TRANSF_RAIL, "-mass", mrail)

def build_wheelset_elements() -> None:
    # Rigid beams connecting wheelset components
    ops.element("elasticBeamColumn", 2001,
                NODE_WHEEL_LEFT, NODE_WHEEL_CENTER,
                ARigid, ERigid, GRigid, IxRigid, IyRigid, IzRigid, TRANSF_WHEELSET)
    ops.element("elasticBeamColumn", 2101,
                NODE_WHEEL_CENTER, NODE_WHEEL_RIGHT,
                ARigid, ERigid, GRigid, IxRigid, IyRigid, IzRigid, TRANSF_WHEELSET)
    ops.element("elasticBeamColumn", 2051,
                NODE_WHEEL_LEFT, NODE_WHEEL_L_EXT,
                ARigid, ERigid, GRigid, IxRigid, IyRigid, IzRigid, TRANSF_WHEELSET)
    ops.element("elasticBeamColumn", 2151,
                NODE_WHEEL_RIGHT, NODE_WHEEL_R_EXT,
                ARigid, ERigid, GRigid, IxRigid, IyRigid, IzRigid, TRANSF_WHEELSET)

def add_uy_spring() -> None:
    """Very soft spring (1 N/m) in UY to eliminate rigid body mode for static."""
    ops.uniaxialMaterial("Elastic", MAT_UY_SPRING, 1.0)
    ops.element("zeroLength", ELE_UY_SPRING, NODE_WHEEL_CENTER, NODE_UY_SPRING,
                "-mat", MAT_UY_SPRING, "-dir", 2)

def setup_wheel_sp() -> None:
    """Create SP for wheel longitudinal motion with Constant time series.

    The SP is initially UX = 0 (for the static gravity phase).  During the
    transient loop, `update_wheel_sp(t)` is called each step to advance the
    imposed displacement to UX = pVel * t.
    """
    ops.timeSeries("Constant", TS_WHEEL)
    ops.pattern("Plain", PAT_WHEEL, TS_WHEEL)
    ops.sp(NODE_WHEEL_CENTER, 1, 0.0)

def update_wheel_sp(t: float) -> None:
    """Update the wheel longitudinal SP to UX = pVel * t.
    Removes the old SP first to avoid conflicting constraints.
    """
    ops.remove("sp", PAT_WHEEL, NODE_WHEEL_CENTER, 1)
    ops.sp(NODE_WHEEL_CENTER, 1, pVel * t, PAT_WHEEL)

# ── 10. OUTPUT DATABASE (ODB) ───────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: int = 1) -> "opst.post.CreateODB":
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
    )
    odb.save_model_data()
    return odb

# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity() -> None:
    """Gravity load on wheelset with ramp-up."""
    ops.timeSeries("Series", TS_GRAVITY, "-time", *GRAV_RAMP_TIMES,
                   "-values", *GRAV_RAMP_VALUES)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    ops.load(NODE_WHEEL_CENTER, 0.0, 0.0, -Mw * g, 0.0, 0.0, 0.0)

def define_lateral_excitation() -> None:
    """Lateral excitation on wheelset."""
    ops.timeSeries("Series", TS_LATERAL, "-time", *LAT_TIMES,
                   "-values", *LAT_VALUES)
    ops.pattern("Plain", PAT_LATERAL, TS_LATERAL)
    ops.load(NODE_WHEEL_CENTER, 0.0, Mw * g, 0.0, 0.0, 0.0, 0.0)

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials()
    define_geom_transf()
    build_nodes()
    build_wheelset_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    build_rail_elements()
    build_wheelset_elements()
    add_uy_spring()
    vis_model(output_dir)

    odb = create_odb(output_dir=output_dir, odb_tag=1)

    # Train masses on center node
    ops.mass(NODE_WHEEL_CENTER, Mw, Mw, Mw, Iwx, Iwy, Iwz)

    define_gravity()
    define_lateral_excitation()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    # ── Phase 1: Static gravity ──
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormUnbalance", 1.0e-1, 20, 1)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / nL)
    ops.analysis("Static")

    for step in range(1, nL + 1):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"WARNING: static analysis failed at step {step}")
            break
    print("Static gravity finished!")

    # Freeze loads, reset analysis
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()

    # Create wheel SP pattern after loadConst (so it's NOT frozen)
    setup_wheel_sp()

    # ── Phase 2: Transient dynamics (SmartAnalyze) ──
    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.integrator("Newmark", 0.5, 0.25)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )
    segs = analysis.transient_split(N_TRANSIENT)

    start_t = time.time()
    for i, _ in enumerate(segs):
        update_wheel_sp(i * dT)
        ok = analysis.TransientAnalyze(dT)
        if ok < 0:
            print(f"WARNING: transient analysis failed at step {i + 1}")
            break
        if (i + 1) % 500 == 0:
            print(f"  transient step {i + 1}/{N_TRANSIENT}")
        odb.fetch_response_step()
    analysis.close()
    elapsed = time.time() - start_t
    print(f"Over! ({elapsed:.2f}s, {i + 1} steps)")

    odb.save_response()
    return odb

# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    if not _headless():
        opst.vis.plotly.plot_nodal_responses(
            odb_tag=1,
            resp_type="disp", resp_dof="UZ", defo_scale=10.0,
        ).write_html(str(output_dir / "vis_05_defo_transient.html"))
        opst.vis.plotly.plot_nodal_responses(
            odb_tag=1,
            slides=True, defo_scale=10.0,
            resp_type="disp", resp_dof="UZ",
        ).write_html(str(output_dir / "vis_06_slider.html"))

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
