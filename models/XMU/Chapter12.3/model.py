# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 3D peridynamic concrete bond pushdown (XMU Chapter 12.3)
UniqueID : XMU_Chapter12_3
Author   : XMU Finite Element Analysis course
Date     : 2026-06-22
Purpose  : 3D peridynamic bond-based concrete damage simulation under
           static DisplacementControl pushdown.
Ref      : XMU Finite Element Analysis course, Chapter 12.3.
Units    : N, mm, MPa
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import math
import time
import openseespy.opensees as ops
import opstool as opst
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# No fixed materials — each bond gets a unique Concrete02 material tag = bond number
TS_LOAD  = 1
PAT_LOAD = 2

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
x_len = 0.15 * m        # 150 mm
y_len = 0.30 * m        # 300 mm
z_len = 0.15 * m        # 150 mm
dx    = 0.015 * m       # 15 mm

ndivx = int(x_len / dx)   # 10
ndivy = int(y_len / dx)   # 20
ndivz = int(z_len / dx)   # 10

# Node indexing stride
NODE_STRIDE_Y = ndivz + 1        # 11
NODE_STRIDE_X = (ndivy + 1) * (ndivz + 1)  # 231

horizonrate   = 2.015
horizonratem  = 3.0
horizon       = horizonrate * dx          # 30.225 mm
radij         = 0.5 * dx                  # 7.5 mm

A_bond = dx * dx / 4.0 * math.pi         # ~176.7 mm^2

# Concrete02 parameters (Tcl SI values converted)
cfpc   = -8.2 * MPa     # -8.2 MPa
cepsc0 = -0.003         # strain (dimensionless)
cfpcu  = -1.0 * MPa     # -1.0 MPa
cepsU  = -0.035         # strain
clambda = 0.1           # unitless
cft    = 2.0 * MPa      # 2.0 MPa
cEts   = 100.0 * MPa    # 100 MPa

TOP_LOAD = -2.0e6       # N per top node
DISP_INCR = -0.005      # mm per step (Tcl: -0.000005 m)

TOL_TEST = 2.0e-5
MAX_ITER = 10
PRINT_FLAG = 1

# Module-level state
nodenum: int = 0
elenum: int = 0
bond: list = []
_CTRL_NODE: int = 0


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
# Materials are created per-bond in build_elements()

def define_materials() -> None:
    pass


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
# Not used — truss bonds carry area directly


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def node_id(i: int, j: int, k: int) -> int:
    return 1 + i * NODE_STRIDE_X + j * NODE_STRIDE_Y + k


def build_nodes() -> int:
    global nodenum
    nodenum = 0
    for i in range(ndivx + 1):
        for j in range(ndivy + 1):
            for k in range(ndivz + 1):
                nid = node_id(i, j, k)
                nodenum = nid
                ops.node(nid, i * dx, j * dx, k * dx)
    return nodenum


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    ctrl_node = node_id(ndivx // 2, ndivy, ndivz // 2)
    # Base (j=0): fully fixed
    for i in range(ndivx + 1):
        for k in range(ndivz + 1):
            ops.fix(node_id(i, 0, k), 1, 1, 1)
    # Constrain all top nodes to ctrl_node in UY (DOF 2)
    for i in range(ndivx + 1):
        for k in range(ndivz + 1):
            nid = node_id(i, ndivy, k)
            if nid != ctrl_node:
                ops.equalDOF(ctrl_node, nid, 2)
    # Fix top nodes UX and UZ (allow UY for pushdown)
    for i in range(ndivx + 1):
        for k in range(ndivz + 1):
            ops.fix(node_id(i, ndivy, k), 1, 0, 1)

    global _CTRL_NODE
    _CTRL_NODE = ctrl_node


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def build_elements() -> tuple:
    global elenum, bond
    bond = [(0, 0)]
    elenum = 0
    visited: set = set()

    for i in range(ndivx + 1):
        imin = max(0, i - int(horizonratem))
        imax = min(ndivx, i + int(horizonratem))
        for j in range(ndivy + 1):
            jmin = max(0, j - int(horizonratem))
            jmax = min(ndivy, j + int(horizonratem))
            for k in range(ndivz + 1):
                n1 = node_id(i, j, k)
                x1, y1, z1 = ops.nodeCoord(n1)
                kmn = max(0, k - int(horizonratem))
                kmx = min(ndivz, k + int(horizonratem))
                for l in range(imin, imax + 1):
                    for m in range(jmin, jmax + 1):
                        for n in range(kmn, kmx + 1):
                            n2 = node_id(l, m, n)
                            if n1 == n2:
                                continue
                            key = (min(n1, n2), max(n1, n2))
                            if key in visited:
                                continue
                            x2, y2, z2 = ops.nodeCoord(n2)
                            dist = math.sqrt(
                                (x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2
                            )
                            if dist <= 0.0:
                                continue
                            if dist <= horizon - radij:
                                elenum += 1
                                ops.uniaxialMaterial(
                                    "Concrete02", elenum,
                                    cfpc, cepsc0, cfpcu, cepsU, clambda, cft, cEts,
                                )
                                ops.element("truss", elenum, n1, n2, A_bond, elenum)
                                bond.append((n1, n2))
                                visited.add(key)
                            elif dist < horizon + radij:
                                fac = (horizon + radij - dist) / (2.0 * radij)
                                elenum += 1
                                ops.uniaxialMaterial(
                                    "Concrete02", elenum,
                                    cfpc * fac, cepsc0, cfpcu * fac, cepsU,
                                    clambda, cft * fac, cEts * fac,
                                )
                                ops.element("truss", elenum, n1, n2, A_bond, elenum)
                                bond.append((n1, n2))
                                visited.add(key)
    return bond, elenum


# ── 10. OUTPUT DATABASE (ODB) ───────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: int = 1) -> "opst.post.CreateODB":
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        save_nodal_resp=True,
        save_truss_resp=False,
        node_tags=list(range(1, nodenum + 1)),
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_loads() -> None:
    ops.timeSeries("Linear", TS_LOAD)
    ops.pattern("Plain", PAT_LOAD, TS_LOAD)
    for i in range(ndivx + 1):
        for k in range(ndivz + 1):
            ops.load(node_id(i, ndivy, k), 0.0, TOP_LOAD, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    global nodenum, _CTRL_NODE
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials()
    nodenum = build_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    build_elements()
    vis_model(output_dir)
    define_loads()
    vis_loads(output_dir)
    odb = create_odb(output_dir=output_dir, odb_tag=1)
    vis_pre_analysis(output_dir)

    # Recorders for targeted output (permitted exception per AGENT.md §10)
    base_nodes = [
        node_id(i, 0, k)
        for i in range(ndivx + 1)
        for k in range(ndivz + 1)
    ]
    ops.recorder("Node", "-file", str(output_dir / "reaction.out"),
                 "-node", *base_nodes, "-dof", 2, "reaction")
    ops.recorder("Node", "-file", str(output_dir / "disp.out"),
                 "-node", _CTRL_NODE, "-dof", 2, "disp")

    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", TOL_TEST, MAX_ITER, PRINT_FLAG)
    ops.algorithm("Newton")
    ops.integrator("DisplacementControl", _CTRL_NODE, 2, DISP_INCR)
    ops.analysis("Static")

    start_t = time.time()
    step: int = 0
    for step in range(1, 401):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"WARNING: analysis failed at step {step}")
            break
        odb.fetch_response_step()
    elapsed = time.time() - start_t
    print(f"Over time: {elapsed:.2f} seconds ({step} steps).")
    return odb


# ── 13. POST-PROCESSING ─────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and render deformed-shape HTML."""
    if nodenum == 0:
        return
    odb.save_response()
    if not _headless():
        vis_defo(output_dir, filename="vis_05_defo_lateral.html")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
