# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 3D Reinforced Concrete Column Static Pushover Analysis (Dino OpenSees3)
UniqueID : Dino_RC_Column_3D_Pushover
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-28
Purpose  : Static elastic-plastic pushover analysis of a 3D reinforced concrete column under gravity axial load and displacement control.
Ref      : Static Elastic-Plastic Analysis of Frame Structures (Dino TCL Ref opensees3)
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
MAT_STEEL       = 1
MAT_CONCRETE    = 2
MAT_TORSION     = 3

SEC_COLUMN      = 1

TRANSF_COLUMN   = 1

NODE_BASE       = 1
NODE_TOP        = 2

ELE_COL_1       = 1

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Geometry
h_col       = 3000.0 * mm        # column total height [mm] (3 m)
b_col       = 500.0 * mm         # column width [mm]
d_col       = 500.0 * mm         # column depth [mm]
n_ele       = 8                  # number of elements along column height

# Material properties
fy          = 335.0 * MPa        # steel yield strength [MPa = N/mm²]
Es          = 200000.0 * MPa     # steel elastic modulus [MPa]
b_steel     = 0.00001            # steel strain hardening ratio

fc          = 26.8 * MPa         # concrete compressive strength (peak) [MPa]
epsc0       = 0.002              # concrete strain at peak compressive strength
fcu         = 15.0 * MPa         # concrete ultimate compressive strength [MPa]
epscu       = 0.006              # concrete ultimate strain

Gj          = 1.999e5 * MPa      # torsional rigidity / modulus

# Loading
P_gravity   = 1.5e6 * N          # axial gravity load (1.5 MN = 1500 kN)
P_lateral   = 1000.0 * N         # reference lateral load vector (1 kN)
target_disp = 100.0 * mm         # target pushover displacement [mm]
n_steps_push = 100               # pushover analysis steps

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    # Steel01 material
    ops.uniaxialMaterial("Steel01", MAT_STEEL, fy, Es, b_steel)
    # Concrete01 material (compressive stress is negative)
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE, -fc, -epsc0, -fcu, -epscu)
    # Elastic material for torsion
    ops.uniaxialMaterial("Elastic", MAT_TORSION, Gj)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    # Define 500x500 mm fiber section with 64 concrete fibers and 16 steel rebar fibers
    # 3D Fiber section in OpenSeesPy requires torsional stiffness -GJ flag
    ops.section("Fiber", SEC_COLUMN, "-GJ", Gj)
    
    # 64 Concrete fibers (8x8 grid: y from -218.8 to 218.8, z from -218.8 to 218.8, area=3906.0 mm² each)
    y_c = [-218.8, -156.3, -93.75, -31.25, 31.25, 93.75, 156.3, 218.8]
    z_c = [-218.8, -156.3, -93.75, -31.25, 31.25, 93.75, 156.3, 218.8]
    area_c = 3906.0 * mm**2
    for y in y_c:
        for z in z_c:
            ops.fiber(y * mm, z * mm, area_c, MAT_CONCRETE)
            
    # 16 Steel rebar fibers (area=490.6 mm² each)
    rebar_coords = [
        (-215.0, -215.0), (-107.5, -215.0), (0.0, -215.0), (107.5, -215.0), (215.0, -215.0),
        (-215.0,  215.0), (-107.5,  215.0), (0.0,  215.0), (107.5,  215.0), (215.0,  215.0),
        (-215.0, -107.5), (-215.0,    0.0), (-215.0, 107.5),
        ( 215.0, -107.5), ( 215.0,    0.0), ( 215.0, 107.5)
    ]
    area_s = 490.6 * mm**2
    for y, z in rebar_coords:
        ops.fiber(y * mm, z * mm, area_s, MAT_STEEL)

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    # Base node 1 at (0, 0, 0)
    ops.node(NODE_BASE, 0.0, 0.0, 0.0)
    # Top node 2 at (0, 0, h_col)
    ops.node(NODE_TOP, 0.0, 0.0, h_col)
    
    # Intermediate nodes 3..(n_ele+1) if n_ele > 1
    if n_ele > 1:
        dz = h_col / n_ele
        for i in range(1, n_ele):
            node_tag = 2 + i  # node 3, 4, 5, ...
            ops.node(node_tag, 0.0, 0.0, i * dz)

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    # Fix base node 1 completely in all 6 DOFs
    ops.fix(NODE_BASE, 1, 1, 1, 1, 1, 1)
    
    # Fix top node 2 (and intermediate nodes) in DOF 2 (Y disp), DOF 4 (Y rot), DOF 6 (Z rot)
    # Free in DOF 1 (X disp), DOF 3 (Z disp), DOF 5 (X rot)
    ops.fix(NODE_TOP, 0, 1, 0, 1, 0, 1)
    if n_ele > 1:
        for i in range(1, n_ele):
            node_tag = 2 + i
            ops.fix(node_tag, 0, 1, 0, 1, 0, 1)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    # Geometric transformation for 3D column
    ops.geomTransf("Linear", TRANSF_COLUMN, 1.0, 0.0, 0.0)
    
    # Define nonlinear beam-column elements with 3 integration points
    n_ip = 3
    if n_ele == 1:
        ops.element("nonlinearBeamColumn", ELE_COL_1, NODE_BASE, NODE_TOP, n_ip, SEC_COLUMN, TRANSF_COLUMN)
    else:
        # Node sequence: NODE_BASE (1), node 3, node 4, ..., node (1+n_ele), NODE_TOP (2)
        node_seq = [NODE_BASE] + [2 + i for i in range(1, n_ele)] + [NODE_TOP]
        for e in range(n_ele):
            ele_tag = ELE_COL_1 + e
            i_node = node_seq[e]
            j_node = node_seq[e + 1]
            ops.element("nonlinearBeamColumn", ele_tag, i_node, j_node, n_ip, SEC_COLUMN, TRANSF_COLUMN)

# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: int = 1) -> "opst.post.CreateODB":
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
    # Dead load: compressive axial force P_gravity applied at top node 2 (negative Z)
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(NODE_TOP, 0.0, 0.0, -P_gravity, 0.0, 0.0, 0.0)

def define_lateral_loads() -> None:
    # Lateral pushover reference load applied at top node 2 (positive X)
    ops.timeSeries("Linear", 2)
    ops.pattern("Plain", 3, 2)
    ops.load(NODE_TOP, P_lateral, 0.0, 0.0, 0.0, 0.0, 0.0)

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10) -> None:
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
    max_step: float = 1.0 * mm,
) -> None:
    """Run static displacement-controlled pushover using SmartAnalyze."""
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

def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + pushover, return ODB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)
    
    odb = create_odb(output_dir, odb_tag=1)
    
    define_gravity_loads()
    run_gravity(odb, n_steps=10)
    
    define_lateral_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    
    run_pushover(odb, ctrl_node=NODE_TOP, ctrl_dof=1, target_disp=target_disp)
    return odb

# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and write visualisation plots."""
    odb.save_response()
    if not _headless():
        vis_defo(output_dir, filename="vis_05_deformed.html", odb_tag=1, resp_dof="UX")
        vis_slider(output_dir, filename="vis_06_slider.html", odb_tag=1, resp_dof="UX")

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
