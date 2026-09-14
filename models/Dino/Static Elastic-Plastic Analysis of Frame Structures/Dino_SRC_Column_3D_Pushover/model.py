# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 3D Steel Reinforced Concrete Column Static Pushover Analysis (Dino OpenSees3 Ex27)
UniqueID : Dino_SRC_Column_3D_Pushover
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-31
Purpose  : Static elastic-plastic pushover analysis of a 3D steel reinforced concrete column under gravity axial load and displacement control.
Ref      : http://dinochen.com/article.asp?id=267
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import sys
from pathlib import Path
import numpy as np
import openseespy.opensees as ops
import opstool as opst

# Add standards/ to path dynamically
for p in Path(__file__).parents:
    if (p / "standards").exists():
        sys.path.insert(0, str(p / "standards"))
        break
from units import *
from vis_utils import (
    _headless,
    vis_nodes,
    vis_model,
    vis_loads,
    vis_pre_analysis,
    vis_defo,
    vis_slider,
    vis_anim,
)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
MAT_CONCRETE_CORE   = 2
MAT_CONCRETE_COVER  = 1
MAT_REBAR           = 4
MAT_STEEL_SHAPE     = 5

SEC_COLUMN          = 1

TRANSF_COLUMN       = 1

NODE_BASE           = 1
NODE_TOP            = 2

ELE_COL             = 1

# Number of steps and constants
N_GRAV_STEPS        = 10
N_PUSH_STEPS        = 100

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Geometry
h_col       = 3000.0 * mm        # column total height [mm] (3 m)

# Material properties
# Concrete
fc          = 27.5 * MPa         # concrete peak strength [MPa]
ec1         = -0.002             # concrete strain at peak
fcu         = 10.0 * MPa         # concrete ultimate strength [MPa]
ec2         = -0.0035            # concrete ultimate strain

# Steel Rebars
fy_rebar    = 400.0 * MPa        # rebar yield strength [MPa]
Es_rebar    = 205000.0 * MPa     # rebar elastic modulus [MPa]
b_rebar     = 0.001              # strain hardening ratio

# Steel embedded shape
fy_shape    = 360.0 * MPa        # steel shape yield strength [MPa]
Es_shape    = 205000.0 * MPa     # steel shape elastic modulus [MPa]
b_shape     = 0.001              # strain hardening ratio

# Torsional rigidity
Gj          = 1.0e12 * N * mm**2 # Torsional stiffness

# Loading
P_gravity   = 1.0e7 * N          # gravity load (10000 kN = 10 MN)
P_lateral   = 1000.0 * N         # reference lateral load (1 kN)
target_disp = 40.0 * mm          # target lateral displacement [mm] (100 * 0.4 mm)
push_incr   = 0.4 * mm           # displacement increment per step

# Verbatim fiber coordinates from co.tcl
FIBERS_LIST = [
    # confined concrete (mat 2)
    (-324.0, -324.0, 5184.0, MAT_CONCRETE_CORE),
    (-324.0, -252.0, 5184.0, MAT_CONCRETE_CORE),
    (-324.0, -180.0, 5184.0, MAT_CONCRETE_CORE),
    (-324.0, -108.0, 5184.0, MAT_CONCRETE_CORE),
    (-324.0, -36.0, 5184.0, MAT_CONCRETE_CORE),
    (-324.0, 36.0, 5184.0, MAT_CONCRETE_CORE),
    (-324.0, 108.0, 5184.0, MAT_CONCRETE_CORE),
    (-324.0, 180.0, 5184.0, MAT_CONCRETE_CORE),
    (-324.0, 252.0, 5184.0, MAT_CONCRETE_CORE),
    (-324.0, 324.0, 5184.0, MAT_CONCRETE_CORE),
    (-252.0, -324.0, 5184.0, MAT_CONCRETE_CORE),
    (-252.0, -252.0, 5184.0, MAT_CONCRETE_CORE),
    (-252.0, -180.0, 5184.0, MAT_CONCRETE_CORE),
    (-252.0, -108.0, 5184.0, MAT_CONCRETE_CORE),
    (-252.0, -36.0, 5184.0, MAT_CONCRETE_CORE),
    (-252.0, 36.0, 5184.0, MAT_CONCRETE_CORE),
    (-252.0, 108.0, 5184.0, MAT_CONCRETE_CORE),
    (-252.0, 180.0, 5184.0, MAT_CONCRETE_CORE),
    (-252.0, 252.0, 5184.0, MAT_CONCRETE_CORE),
    (-252.0, 324.0, 5184.0, MAT_CONCRETE_CORE),
    (-180.0, -324.0, 5184.0, MAT_CONCRETE_CORE),
    (-180.0, -252.0, 5184.0, MAT_CONCRETE_CORE),
    (-180.0, -180.0, 5184.0, MAT_CONCRETE_CORE),
    (-180.0, -108.0, 5184.0, MAT_CONCRETE_CORE),
    (-180.0, -36.0, 5184.0, MAT_CONCRETE_CORE),
    (-180.0, 36.0, 5184.0, MAT_CONCRETE_CORE),
    (-180.0, 108.0, 5184.0, MAT_CONCRETE_CORE),
    (-180.0, 180.0, 5184.0, MAT_CONCRETE_CORE),
    (-180.0, 252.0, 5184.0, MAT_CONCRETE_CORE),
    (-180.0, 324.0, 5184.0, MAT_CONCRETE_CORE),
    (-108.0, -324.0, 5184.0, MAT_CONCRETE_CORE),
    (-108.0, -252.0, 5184.0, MAT_CONCRETE_CORE),
    (-108.0, -180.0, 5184.0, MAT_CONCRETE_CORE),
    (-108.0, -108.0, 5184.0, MAT_CONCRETE_CORE),
    (-108.0, -36.0, 5184.0, MAT_CONCRETE_CORE),
    (-108.0, 36.0, 5184.0, MAT_CONCRETE_CORE),
    (-108.0, 108.0, 5184.0, MAT_CONCRETE_CORE),
    (-108.0, 180.0, 5184.0, MAT_CONCRETE_CORE),
    (-108.0, 252.0, 5184.0, MAT_CONCRETE_CORE),
    (-108.0, 324.0, 5184.0, MAT_CONCRETE_CORE),
    (-36.0, -324.0, 5184.0, MAT_CONCRETE_CORE),
    (-36.0, -252.0, 5184.0, MAT_CONCRETE_CORE),
    (-36.0, -180.0, 5184.0, MAT_CONCRETE_CORE),
    (-36.0, -108.0, 5184.0, MAT_CONCRETE_CORE),
    (-36.0, -36.0, 5184.0, MAT_CONCRETE_CORE),
    (-36.0, 36.0, 5184.0, MAT_CONCRETE_CORE),
    (-36.0, 108.0, 5184.0, MAT_CONCRETE_CORE),
    (-36.0, 180.0, 5184.0, MAT_CONCRETE_CORE),
    (-36.0, 252.0, 5184.0, MAT_CONCRETE_CORE),
    (-36.0, 324.0, 5184.0, MAT_CONCRETE_CORE),
    (36.0, -324.0, 5184.0, MAT_CONCRETE_CORE),
    (36.0, -252.0, 5184.0, MAT_CONCRETE_CORE),
    (36.0, -180.0, 5184.0, MAT_CONCRETE_CORE),
    (36.0, -108.0, 5184.0, MAT_CONCRETE_CORE),
    (36.0, -36.0, 5184.0, MAT_CONCRETE_CORE),
    (36.0, 36.0, 5184.0, MAT_CONCRETE_CORE),
    (36.0, 108.0, 5184.0, MAT_CONCRETE_CORE),
    (36.0, 180.0, 5184.0, MAT_CONCRETE_CORE),
    (36.0, 252.0, 5184.0, MAT_CONCRETE_CORE),
    (36.0, 324.0, 5184.0, MAT_CONCRETE_CORE),
    (108.0, -324.0, 5184.0, MAT_CONCRETE_CORE),
    (108.0, -252.0, 5184.0, MAT_CONCRETE_CORE),
    (108.0, -180.0, 5184.0, MAT_CONCRETE_CORE),
    (108.0, -108.0, 5184.0, MAT_CONCRETE_CORE),
    (108.0, -36.0, 5184.0, MAT_CONCRETE_CORE),
    (108.0, 36.0, 5184.0, MAT_CONCRETE_CORE),
    (108.0, 108.0, 5184.0, MAT_CONCRETE_CORE),
    (108.0, 180.0, 5184.0, MAT_CONCRETE_CORE),
    (108.0, 252.0, 5184.0, MAT_CONCRETE_CORE),
    (108.0, 324.0, 5184.0, MAT_CONCRETE_CORE),
    (180.0, -324.0, 5184.0, MAT_CONCRETE_CORE),
    (180.0, -252.0, 5184.0, MAT_CONCRETE_CORE),
    (180.0, -180.0, 5184.0, MAT_CONCRETE_CORE),
    (180.0, -108.0, 5184.0, MAT_CONCRETE_CORE),
    (180.0, -36.0, 5184.0, MAT_CONCRETE_CORE),
    (180.0, 36.0, 5184.0, MAT_CONCRETE_CORE),
    (180.0, 108.0, 5184.0, MAT_CONCRETE_CORE),
    (180.0, 180.0, 5184.0, MAT_CONCRETE_CORE),
    (180.0, 252.0, 5184.0, MAT_CONCRETE_CORE),
    (180.0, 324.0, 5184.0, MAT_CONCRETE_CORE),
    (252.0, -324.0, 5184.0, MAT_CONCRETE_CORE),
    (252.0, -252.0, 5184.0, MAT_CONCRETE_CORE),
    (252.0, -180.0, 5184.0, MAT_CONCRETE_CORE),
    (252.0, -108.0, 5184.0, MAT_CONCRETE_CORE),
    (252.0, -36.0, 5184.0, MAT_CONCRETE_CORE),
    (252.0, 36.0, 5184.0, MAT_CONCRETE_CORE),
    (252.0, 108.0, 5184.0, MAT_CONCRETE_CORE),
    (252.0, 180.0, 5184.0, MAT_CONCRETE_CORE),
    (252.0, 252.0, 5184.0, MAT_CONCRETE_CORE),
    (252.0, 324.0, 5184.0, MAT_CONCRETE_CORE),
    (324.0, -324.0, 5184.0, MAT_CONCRETE_CORE),
    (324.0, -252.0, 5184.0, MAT_CONCRETE_CORE),
    (324.0, -180.0, 5184.0, MAT_CONCRETE_CORE),
    (324.0, -108.0, 5184.0, MAT_CONCRETE_CORE),
    (324.0, -36.0, 5184.0, MAT_CONCRETE_CORE),
    (324.0, 36.0, 5184.0, MAT_CONCRETE_CORE),
    (324.0, 108.0, 5184.0, MAT_CONCRETE_CORE),
    (324.0, 180.0, 5184.0, MAT_CONCRETE_CORE),
    (324.0, 252.0, 5184.0, MAT_CONCRETE_CORE),
    (324.0, 324.0, 5184.0, MAT_CONCRETE_CORE),
    # unconfined concrete (mat 1)
    (-366.67, -380.0, 2666.7, MAT_CONCRETE_COVER),
    (-366.67, 380.0, 2666.7, MAT_CONCRETE_COVER),
    (-300.0, -380.0, 2666.7, MAT_CONCRETE_COVER),
    (-300.0, 380.0, 2666.7, MAT_CONCRETE_COVER),
    (-233.33, -380.0, 2666.7, MAT_CONCRETE_COVER),
    (-233.33, 380.0, 2666.7, MAT_CONCRETE_COVER),
    (-166.67, -380.0, 2666.7, MAT_CONCRETE_COVER),
    (-166.67, 380.0, 2666.7, MAT_CONCRETE_COVER),
    (-100.0, -380.0, 2666.7, MAT_CONCRETE_COVER),
    (-100.0, 380.0, 2666.7, MAT_CONCRETE_COVER),
    (-33.333, -380.0, 2666.7, MAT_CONCRETE_COVER),
    (-33.333, 380.0, 2666.7, MAT_CONCRETE_COVER),
    (33.333, -380.0, 2666.7, MAT_CONCRETE_COVER),
    (33.333, 380.0, 2666.7, MAT_CONCRETE_COVER),
    (100.0, -380.0, 2666.7, MAT_CONCRETE_COVER),
    (100.0, 380.0, 2666.7, MAT_CONCRETE_COVER),
    (166.67, -380.0, 2666.7, MAT_CONCRETE_COVER),
    (166.67, 380.0, 2666.7, MAT_CONCRETE_COVER),
    (233.33, -380.0, 2666.7, MAT_CONCRETE_COVER),
    (233.33, 380.0, 2666.7, MAT_CONCRETE_COVER),
    (300.0, -380.0, 2666.7, MAT_CONCRETE_COVER),
    (300.0, 380.0, 2666.7, MAT_CONCRETE_COVER),
    (366.67, -380.0, 2666.7, MAT_CONCRETE_COVER),
    (366.67, 380.0, 2666.7, MAT_CONCRETE_COVER),
    (-380.0, -330.0, 2400.0, MAT_CONCRETE_COVER),
    (380.0, -330.0, 2400.0, MAT_CONCRETE_COVER),
    (-380.0, -270.0, 2400.0, MAT_CONCRETE_COVER),
    (380.0, -270.0, 2400.0, MAT_CONCRETE_COVER),
    (-380.0, -210.0, 2400.0, MAT_CONCRETE_COVER),
    (380.0, -210.0, 2400.0, MAT_CONCRETE_COVER),
    (-380.0, -150.0, 2400.0, MAT_CONCRETE_COVER),
    (380.0, -150.0, 2400.0, MAT_CONCRETE_COVER),
    (-380.0, -90.0, 2400.0, MAT_CONCRETE_COVER),
    (380.0, -90.0, 2400.0, MAT_CONCRETE_COVER),
    (-380.0, -30.0, 2400.0, MAT_CONCRETE_COVER),
    (380.0, -30.0, 2400.0, MAT_CONCRETE_COVER),
    (-380.0, 30.0, 2400.0, MAT_CONCRETE_COVER),
    (380.0, 30.0, 2400.0, MAT_CONCRETE_COVER),
    (-380.0, 90.0, 2400.0, MAT_CONCRETE_COVER),
    (380.0, 90.0, 2400.0, MAT_CONCRETE_COVER),
    (-380.0, 150.0, 2400.0, MAT_CONCRETE_COVER),
    (380.0, 150.0, 2400.0, MAT_CONCRETE_COVER),
    (-380.0, 210.0, 2400.0, MAT_CONCRETE_COVER),
    (380.0, 210.0, 2400.0, MAT_CONCRETE_COVER),
    (-380.0, 270.0, 2400.0, MAT_CONCRETE_COVER),
    (380.0, 270.0, 2400.0, MAT_CONCRETE_COVER),
    (-380.0, 330.0, 2400.0, MAT_CONCRETE_COVER),
    (380.0, 330.0, 2400.0, MAT_CONCRETE_COVER),
    # rebars (mat 4)
    (-120.0, -360.0, 490.63, MAT_REBAR),
    (-120.0, 360.0, 490.63, MAT_REBAR),
    (120.0, -360.0, 490.63, MAT_REBAR),
    (120.0, 360.0, 490.63, MAT_REBAR),
    (-360.0, 0.0, 490.63, MAT_REBAR),
    (360.0, 0.0, 490.63, MAT_REBAR),
    (-360.0, -360.0, 490.63, MAT_REBAR),
    (360.0, -360.0, 490.63, MAT_REBAR),
    (360.0, 360.0, 490.63, MAT_REBAR),
    (-360.0, 360.0, 490.63, MAT_REBAR),
    # steel shape (mat 5)
    (-183.33, -185.0, 1000.0, MAT_STEEL_SHAPE),
    (-150.0, -185.0, 1000.0, MAT_STEEL_SHAPE),
    (-116.67, -185.0, 1000.0, MAT_STEEL_SHAPE),
    (-83.333, -185.0, 1000.0, MAT_STEEL_SHAPE),
    (-50.0, -185.0, 1000.0, MAT_STEEL_SHAPE),
    (-16.667, -185.0, 1000.0, MAT_STEEL_SHAPE),
    (16.667, -185.0, 1000.0, MAT_STEEL_SHAPE),
    (50.0, -185.0, 1000.0, MAT_STEEL_SHAPE),
    (83.333, -185.0, 1000.0, MAT_STEEL_SHAPE),
    (116.67, -185.0, 1000.0, MAT_STEEL_SHAPE),
    (150.0, -185.0, 1000.0, MAT_STEEL_SHAPE),
    (183.33, -185.0, 1000.0, MAT_STEEL_SHAPE),
    (-183.33, 185.0, 1000.0, MAT_STEEL_SHAPE),
    (-150.0, 185.0, 1000.0, MAT_STEEL_SHAPE),
    (-116.67, 185.0, 1000.0, MAT_STEEL_SHAPE),
    (-83.333, 185.0, 1000.0, MAT_STEEL_SHAPE),
    (-50.0, 185.0, 1000.0, MAT_STEEL_SHAPE),
    (-16.667, 185.0, 1000.0, MAT_STEEL_SHAPE),
    (16.667, 185.0, 1000.0, MAT_STEEL_SHAPE),
    (50.0, 185.0, 1000.0, MAT_STEEL_SHAPE),
    (83.333, 185.0, 1000.0, MAT_STEEL_SHAPE),
    (116.67, 185.0, 1000.0, MAT_STEEL_SHAPE),
    (150.0, 185.0, 1000.0, MAT_STEEL_SHAPE),
    (183.33, 185.0, 1000.0, MAT_STEEL_SHAPE),
    (0.0, -141.67, 1700.0, MAT_STEEL_SHAPE),
    (0.0, -85.0, 1700.0, MAT_STEEL_SHAPE),
    (0.0, -28.333, 1700.0, MAT_STEEL_SHAPE),
    (0.0, 28.333, 1700.0, MAT_STEEL_SHAPE),
    (0.0, 85.0, 1700.0, MAT_STEEL_SHAPE),
    (0.0, 141.67, 1700.0, MAT_STEEL_SHAPE),
]

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    # Concrete cover (material 1)
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE_COVER, -fc, ec1, -fcu, ec2)
    # Concrete core (material 2)
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE_CORE, -fc, ec1, -fcu, ec2)
    # Rebar steel (material 4)
    ops.uniaxialMaterial("Steel01", MAT_REBAR, fy_rebar, Es_rebar, b_rebar)
    # Steel shape (material 5)
    ops.uniaxialMaterial("Steel01", MAT_STEEL_SHAPE, fy_shape, Es_shape, b_shape)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    # Define fiber section with required -GJ flag
    ops.section("Fiber", SEC_COLUMN, "-GJ", Gj)
    # Add fibers
    for y, z, area, mat in FIBERS_LIST:
        ops.fiber(y * mm, z * mm, area * mm**2, mat)

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    # Base node 1 at (0.0, 18000.0, 0.0)
    ops.node(NODE_BASE, 0.0, 18000.0, 0.0)
    # Top node 2 at (0.0, 18000.0, h_col)
    ops.node(NODE_TOP, 0.0, 18000.0, h_col)

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    # Fixed base node 1
    ops.fix(NODE_BASE, 1, 1, 1, 1, 1, 1)
    # Fixed UY, RX, RZ at node 2
    ops.fix(NODE_TOP, 0, 1, 0, 1, 0, 1)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    # Geometric transformation for 3D column
    ops.geomTransf("Linear", TRANSF_COLUMN, 1.0, 0.0, 0.0)
    # Define single nonlinear beam-column element with 4 integration points
    n_ip = 4
    ops.element("nonlinearBeamColumn", ELE_COL, NODE_BASE, NODE_TOP, n_ip, SEC_COLUMN, TRANSF_COLUMN)

# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: str = "pushover") -> "opst.post.CreateODB":
    output_dir.mkdir(parents=True, exist_ok=True)
    abs_str = str(output_dir.resolve())
    if sys.platform == "win32" and not abs_str.startswith("\\\\?\\"):
        abs_str = "\\\\?\\" + abs_str
    opst.post.set_odb_path(abs_str)
    odb = opst.post.CreateODB(odb_tag=odb_tag)
    odb.save_model_data()
    return odb

# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    # Constant gravity axial compression load (compressive is negative Z direction)
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(NODE_TOP, 0.0, 0.0, -P_gravity, 0.0, 0.0, 0.0)

def define_lateral_loads() -> None:
    # Reference lateral load at node 2 (positive X direction)
    ops.timeSeries("Linear", 2)
    ops.pattern("Plain", 3, 2)
    ops.load(NODE_TOP, P_lateral, 0.0, 0.0, 0.0, 0.0, 0.0)

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB", n_steps: int = N_GRAV_STEPS) -> None:
    """Run gravity load-controlled static analysis (Permitted Exception §3c)."""
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.analysis("Static")
    
    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()
        
    ops.loadConst("-time", 0.0)

def run_pushover(
    odb: "opst.post.CreateODB",
    ctrl_node: int = NODE_TOP,
    ctrl_dof: int = 1,
    target_disp: float = target_disp,
    max_step: float = push_incr,
) -> None:
    """Run static displacement-controlled lateral pushover using SmartAnalyze."""
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50, 60],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-4,
        printPer=0,
        testPrintFlag=0,
    )
    
    protocol = [target_disp]
    segs = analysis.static_split(protocol, maxStep=max_step)
    for seg in segs:
        analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
        odb.fetch_response_step()
        
    analysis.close()

def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run gravity + pushover, return ODB and reference comparisons."""
    output_dir.mkdir(parents=True, exist_ok=True)
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)
    
    odb = create_odb(output_dir, odb_tag="pushover")
    
    define_gravity_loads()
    run_gravity(odb, n_steps=N_GRAV_STEPS)
    
    define_lateral_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    
    run_pushover(odb, ctrl_node=NODE_TOP, ctrl_dof=1, target_disp=target_disp)
    
    # Load reference node2.out file
    ref_path = Path(__file__).parent / "ref" / "node2.out"
    ref_data = None
    if ref_path.exists():
        ref_data = np.loadtxt(str(ref_path))
        
    return odb, {"ref_data": ref_data}

# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def _read_top_node_history_from_odb(output_dir: Path) -> np.ndarray:
    """Extract Node 2 displacements and load factors from the generated ODB."""
    try:
        # Load ODB data
        ds = opst.post.get_nodal_responses(
            odb_tag="pushover", resp_type="disp", print_info=False
        )
        # N_GRAV_STEPS = 10, plus t=0 initial state -> gravity steps occupy indices 0 to 10
        # Pushover steps occupy indices 11 onwards (total of 100 steps)
        ux = (ds.sel(nodeTags=NODE_TOP)
                .isel(DOFs=[0])  # UX only
                .values.astype(float))
        uz = (ds.sel(nodeTags=NODE_TOP)
                .isel(DOFs=[2])  # UZ only
                .values.astype(float))
        
        # Get load factors
        # The time variable in get_nodal_responses holds the getTime() of each step.
        # For the pushover phase, getTime() represents the load factor.
        lfs = ds.time.values.astype(float)
        
        # We slice from step 11 onwards to extract the pushover phase
        sim_data = []
        for i in range(N_GRAV_STEPS + 1, len(ux)):
            sim_data.append([lfs[i], ux[i][0], uz[i][0]])
        return np.array(sim_data)
    except Exception as e:
        print(f"Error reading ODB: {e}")
        return np.empty((0, 3))

def post_process(odb: "opst.post.CreateODB", output_dir: Path, results: dict) -> None:
    """Flush ODB, render visualisations, compare results to reference, and plot."""
    odb.save_response()
    
    sim = _read_top_node_history_from_odb(output_dir)
    ref = results["ref_data"]
    
    # Save simulated pushover history
    if len(sim) > 0:
        np.savetxt(str(output_dir / "node2_disp_history.csv"), sim,
                   delimiter=",", header="load_factor,ux_mm,uz_mm")
                   
    # Plot comparison against reference
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot 1: Load-displacement (UX vs Load Factor)
        if ref is not None and len(ref) > 0:
            # ref_data: col 0 = time/load factor, col 1 = UX, col 3 = UZ
            # Gravity: first 10 steps, Pushover: next 100 steps
            ref_push = ref[N_GRAV_STEPS:]
            ax1.plot(ref_push[:, 1], ref_push[:, 0], "k-", linewidth=1.5, alpha=0.6, label="Reference (co.tcl)")
        if len(sim) > 0:
            ax1.plot(sim[:, 1], sim[:, 0], "r--", linewidth=1.5, alpha=0.85, label="Simulation")
        ax1.set_xlabel("Top displacement UX (mm)")
        ax1.set_ylabel("Lateral Load Factor (kN)")
        ax1.set_title("Load-Displacement Curve")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Axial displacement (UX vs UZ)
        if ref is not None and len(ref) > 0:
            ax2.plot(ref_push[:, 1], ref_push[:, 3], "k-", linewidth=1.5, alpha=0.6, label="Reference (co.tcl)")
        if len(sim) > 0:
            ax2.plot(sim[:, 1], sim[:, 2], "r--", linewidth=1.5, alpha=0.85, label="Simulation")
        ax2.set_xlabel("Top displacement UX (mm)")
        ax2.set_ylabel("Top displacement UZ (mm)")
        ax2.set_title("Axial-Shear Displacement Interaction")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        fig.tight_layout()
        fig.savefig(str(output_dir / "pushover_compare.png"), dpi=150)
        plt.close(fig)
        print("  Comparison plot saved to output/pushover_compare.png")
    except Exception as e:
        print(f"  Matplotlib plotting skipped: {e}")
        
    # Render opstool html plots
    if not _headless():
        opst.post.set_odb_path(str(output_dir))
        
        # Deformed shape
        vis_defo(output_dir, filename="vis_05_deformed.html", odb_tag="pushover", resp_dof="UX", scale=10.0)
        # Step slider
        vis_slider(output_dir, filename="vis_06_slider.html", odb_tag="pushover", resp_dof="UX", scale=10.0)
        # Animation
        vis_anim(output_dir, filename="vis_07_animation.html", odb_tag="pushover", defo_scale=10.0, resp_dof=("UX", "UY", "UZ"))
        print("  Visualisation HTMLs rendered in output/")
        
    # Print validation errors
    if len(sim) > 0 and ref is not None and len(ref) > 0:
        ref_push = ref[N_GRAV_STEPS:]
        n = min(len(sim), len(ref_push))
        
        # Compare final displacement UX, UZ, and final Load Factor
        sim_lf_final = sim[n-1, 0]
        ref_lf_final = ref_push[n-1, 0]
        sim_uz_final = sim[n-1, 2]
        ref_uz_final = ref_push[n-1, 3]
        
        rms_lf = float(np.sqrt(np.mean((sim[:n, 0] - ref_push[:n, 0])**2)))
        rel_err_lf = float(np.mean(np.abs(sim[:n, 0] - ref_push[:n, 0]) / np.maximum(np.abs(ref_push[:n, 0]), 1e-12)) * 100.0)
        
        rms_uz = float(np.sqrt(np.mean((sim[:n, 2] - ref_push[:n, 3])**2)))
        rel_err_uz = float(np.mean(np.abs(sim[:n, 2] - ref_push[:n, 3]) / np.maximum(np.abs(ref_push[:n, 3]), 1e-12)) * 100.0)
        
        print(f"\nVerification against reference (node2.out):")
        print(f"  Recorded pushover steps: {len(sim)} / {N_PUSH_STEPS}")
        print(f"  Final Load Factor: Sim = {sim_lf_final:.4f} | Ref = {ref_lf_final:.4f} (Error = {abs(sim_lf_final-ref_lf_final):.4f} or {abs(sim_lf_final-ref_lf_final)/ref_lf_final*100.0:.4f}%)")
        print(f"  Final Node 2 UZ: Sim = {sim_uz_final:.4f} mm | Ref = {ref_uz_final:.4f} mm (Error = {abs(sim_uz_final-ref_uz_final):.4f} mm)")
        print(f"  Load Factor RMS error: {rms_lf:.4f} kN, Mean relative error: {rel_err_lf:.4f}%")
        print(f"  UZ displacement RMS error: {rms_uz:.5f} mm, Mean relative error: {rel_err_uz:.4f}%")

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Static Pushover Analysis of SRC Column: Analysis complete.")
