# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Peridynamics fracture model (XMU Chapter 12.2)
UniqueID : XMU_Chapter12_2
Author   : XMU Finite Element Analysis course
Date     : 2026-06-22
Purpose  : Textbook-example 2D peridynamic bond-based fracture simulation under
           transient base excitation with explicit CentralDifference integration.
Ref      : XMU Finite Element Analysis course, Chapter 12.2.
Units    : N, mm, MPa
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import math
import openseespy.opensees as ops
import opstool as opst
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
MAT_ELASTIC = 1

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
nx      = 40
dx      = 1000.0 * mm       # 1.0 m -> 1000 mm
horizon = 1500.0 * mm       # 1.5 m -> 1500 mm

E_mod         = 200000.0 * MPa   # 2.0e11 Pa -> 200000 MPa
mass_per_node = 1e-5             # 0.01 kg -> 1e-5 N.s^2/mm
A_bond        = 1.0 * m**2       # 1.0 m^2 -> 1e6 mm^2

timestep = 2.5e-8
n_steps  = 4000

ksi     = 0.02
TOL_TEST = 1.0e-8
MAX_ITER = 6

GM_FILE  = Path(__file__).parent / "ground_motions" / "gm_disp.txt"
GM_DT    = 1.0e-5
GM_FACTOR = 1.0

# Module-level state populated during build
nodenum: int = 0
elenum: int = 0
bond: list = []
active: list = []

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 2)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC, E_mod)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
# Not used — truss bonds carry area directly

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def build_nodes() -> int:
    global nodenum
    nodenum = 0
    for i in range(1, nx + 1):
        for j in range(1, nx + 1):
            nodenum += 1
            ops.node(nodenum, (i - 1) * dx, (j - 1) * dx)
            ops.mass(nodenum, mass_per_node, mass_per_node)
    return nodenum

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    ops.fixX(0.0, 1, 1)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def build_elements() -> tuple:
    global elenum, bond, active
    bond = [(0, 0)]
    active = [False]
    elenum = 0
    max_offset = nx + int(horizon / dx) + 1
    for i in range(1, nodenum):
        maxnode = min(i + max_offset, nodenum)
        for j in range(i + 1, maxnode + 1):
            if 761 <= i <= 781 and 801 <= j <= 821:
                continue
            xi, yi = ops.nodeCoord(i)
            xj, yj = ops.nodeCoord(j)
            length = math.sqrt((xj - xi)**2 + (yj - yi)**2)
            if length <= horizon + 1.0:
                elenum += 1
                ops.element("truss", elenum, i, j, A_bond, MAT_ELASTIC)
                bond.append((i, j))
                active.append(True)
    return bond, active, elenum

# ── 10. OUTPUT DATABASE (ODB) ───────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: int = 1) -> "opst.post.CreateODB":
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        save_nodal_resp=True,
        save_truss_resp=True,
        node_tags=list(range(1, nodenum + 1)),
        truss_tags=list(range(1, elenum + 1)),
    )
    odb.save_model_data()
    return odb

# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_ground_motion() -> None:
    ops.timeSeries("Path", 22, "-dt", GM_DT, "-filePath", str(GM_FILE),
                   "-factor", GM_FACTOR)
    ops.pattern("MultipleSupport", 1)
    ops.groundMotion(11, "Plain", "-disp", 22)
    for i in range(nodenum - nx + 1, nodenum + 1):
        ops.imposedMotion(i, 1, 11)

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_analysis(output_dir: Path) -> None:
    """Build model, eigen, Rayleigh damping, explicit CentralDifference
    with bond-breaking damage model.

    NOTE: SmartAnalyze does not support explicit dynamics (CentralDifference)
    or element removal. Manual ops.analyze() loop required — documented
    exception per AGENT.md §10.
    """
    global nodenum
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))
    init_model()
    define_materials()
    nodenum = build_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    build_elements()
    vis_model(output_dir)
    odb = create_odb(output_dir=output_dir, odb_tag=1)
    define_ground_motion()
    vis_loads(output_dir)

    w1s = ops.eigen(1)[0]
    w1 = math.sqrt(w1s)
    a1 = 2.0 * ksi / w1
    ops.rayleigh(0.0, 0.0, a1, 0.0)

    vis_pre_analysis(output_dir)

    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", TOL_TEST, MAX_ITER, 2)
    ops.algorithm("Linear")
    ops.integrator("CentralDifference")
    ops.analysis("Transient")

    # NOTE: Recorders instead of ODB fetch_response_step —
    # 4000 steps x 1600 nodes makes ODB collection impractical
    # (documented exception per AGENT.md §3d/§10).
    ops.recorder("Node", "-file", str(output_dir / "Dispx.out"),
                 "-nodeRange", 1, nodenum, "-dof", 1, "disp")
    ops.recorder("Node", "-file", str(output_dir / "Dispy.out"),
                 "-nodeRange", 1, nodenum, "-dof", 2, "disp")
    ops.recorder("Element", "-file", str(output_dir / "force.out"),
                 "-ele", 4641, "globalForce")

    for t_step in range(1, n_steps + 1):
        ops.analyze(1, timestep)
        for ele in range(2984, min(3080, elenum) + 1):
            if active[ele]:
                n1, n2 = bond[ele]
                cAx = ops.nodeCoord(n1)[0] + ops.nodeDisp(n1)[0]
                cAy = ops.nodeCoord(n1)[1] + ops.nodeDisp(n1)[1]
                cBx = ops.nodeCoord(n2)[0] + ops.nodeDisp(n2)[0]
                cBy = ops.nodeCoord(n2)[1] + ops.nodeDisp(n2)[1]
                length = math.sqrt((cBx - cAx)**2 + (cBy - cAy)**2)
                if length > 1500.0:
                    print(f"remove ele {ele}")
                    ops.remove("element", ele)
                    active[ele] = False

    odb.save_response()

# ── 13. POST-PROCESSING ─────────────────────────────────────────────────────
def post_process(output_dir: Path) -> None:
    pass

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    run_analysis(output_dir)
    post_process(output_dir)
