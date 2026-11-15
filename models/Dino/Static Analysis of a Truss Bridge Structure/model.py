# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Static Analysis of a Truss Bridge Structure (Dino OpenSees tutorial, Example 01)
UniqueID : Dino_Truss_Bridge_Ex01
Purpose  : Linear-elastic static analysis of a 3D truss bridge (18 nodes, 46 truss
           elements, 24 m span, two 3 m wide chords) under four 100 kN nodal loads
           on the top chord, applied by LoadControl (0.01 x 100 steps).
Ref      : ref/Exam01.tcl (source); ref/node0.out (nodes 1-18), ref/node5.out
           (node 5), ref/ele0.out (axial force of elements 1-46)
Units    : N, mm, MPa  (see standards/units.py)
Solver   : manual LoadControl loop, the AGENT.md §3c exception. SmartAnalyze would
           switch the source's LoadControl to DisplacementControl.
Known discrepancy: the truss has a zero-energy mode (a common UY translation of nodes
           11-18), so the source and this model can differ by one constant there
           (0.097 mm at the final step). See README.md, "Verification".
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import sys
from pathlib import Path
import numpy as np
import openseespy.opensees as ops
import opstool as opst

# This model sits under models/Dino/<analysis-name>/, one level deeper than the
# usual models/<UniqueID>/, so standards/ is parents[3] (see AGENT.md §12as-5).
_STANDARDS = Path(__file__).parents[3] / "standards"
if not _STANDARDS.exists():
    _STANDARDS = Path(__file__).parents[2] / "standards"   # fallback for relocation
sys.path.insert(0, str(_STANDARDS))
from units import *
from vis_utils import (
    _headless,
    vis_nodes,
    vis_model,
    vis_loads,
    vis_pre_analysis,
    vis_defo,
    vis_slider,
)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
MAT_TRUSS    = 1          # Elastic steel, used by every truss element
NODE_MONITOR = 5          # node 5 history (node5.out)
N_STEPS      = 100        # Exam01.tcl: analyze 100
N_NODES      = 18
N_ELEMS      = 46

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Node coordinates [mm], verbatim from Exam01.tcl
NODE_XYZ = {
    1: (0.0, 0.0, 0.0),           2: (0.0, 3000.0, 0.0),
    3: (6000.0, 0.0, 0.0),        4: (6000.0, 3000.0, 0.0),
    5: (12000.0, 0.0, 0.0),       6: (12000.0, 3000.0, 0.0),
    7: (18000.0, 0.0, 0.0),       8: (18000.0, 3000.0, 0.0),
    9: (24000.0, 0.0, 0.0),       10: (24000.0, 3000.0, 0.0),
    11: (3000.0, 0.0, 4500.0),    12: (3000.0, 3000.0, 4500.0),
    13: (9000.0, 0.0, 4500.0),    14: (9000.0, 3000.0, 4500.0),
    15: (15000.0, 0.0, 4500.0),   16: (15000.0, 3000.0, 4500.0),
    17: (21000.0, 0.0, 4500.0),   18: (21000.0, 3000.0, 4500.0),
}
# Pinned supports (UX, UY, UZ fixed) at the four bottom-chord end nodes, verbatim
PINNED_NODES = (1, 2, 9, 10)
# Top-chord nodes: UY is free up to one common translation (zero-energy mode, see header)
TOP_CHORD_NODES = tuple(range(11, 19))

# Material: Elastic steel, E = 199900 MPa (Exam01.tcl material 1). Materials 2 and 3
# are defined in the source but never referenced by an element, so they are omitted.
E_STEEL = 1.999e5 * MPa

# (element tag, i-node, j-node, area [mm^2]), verbatim from Exam01.tcl
TRUSS_ELEMENTS = [
    (1, 11, 12, 13050.0), (2, 13, 14, 13050.0), (3, 15, 16, 13050.0), (4, 17, 18, 13050.0),
    (5, 11, 13, 21200.0), (6, 13, 15, 21200.0), (7, 15, 17, 21200.0), (8, 12, 14, 21200.0),
    (9, 14, 16, 21200.0), (10, 16, 18, 21200.0), (11, 1, 11, 13050.0), (12, 3, 11, 13050.0),
    (13, 3, 13, 13050.0), (14, 5, 13, 13050.0), (15, 5, 15, 13050.0), (16, 7, 15, 13050.0),
    (17, 7, 17, 13050.0), (18, 9, 17, 13050.0), (19, 2, 12, 13050.0), (20, 4, 12, 13050.0),
    (21, 4, 14, 13050.0), (22, 6, 14, 13050.0), (23, 6, 16, 13050.0), (24, 8, 16, 13050.0),
    (25, 8, 18, 13050.0), (26, 10, 18, 13050.0), (27, 12, 13, 13050.0), (28, 13, 16, 13050.0),
    (29, 16, 17, 13050.0), (30, 1, 2, 13050.0), (31, 3, 4, 13050.0), (32, 5, 6, 13050.0),
    (33, 7, 8, 13050.0), (34, 9, 10, 13050.0), (35, 1, 3, 21200.0), (36, 3, 5, 21200.0),
    (37, 5, 7, 21200.0), (38, 7, 9, 21200.0), (39, 2, 4, 21200.0), (40, 4, 6, 21200.0),
    (41, 6, 8, 21200.0), (42, 8, 10, 21200.0), (43, 2, 3, 13050.0), (44, 3, 6, 13050.0),
    (45, 6, 7, 13050.0), (46, 7, 10, 13050.0),
]
# Nodal loads (UZ, N) on the top chord, pattern 1 (four 100 kN loads), verbatim
LOAD_NODES = (13, 14, 15, 16)
LOAD_FZ    = -1.0e5 * N

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D translational model (ndm=3, ndf=3)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 3)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    ops.uniaxialMaterial("Elastic", MAT_TRUSS, E_STEEL)

# ── 6. NODES AND BOUNDARY CONDITIONS ─────────────────────────────────────────
def define_nodes() -> None:
    for tag, (x, y, z) in NODE_XYZ.items():
        ops.node(tag, x * mm, y * mm, z * mm)

def define_boundary_conditions() -> None:
    for tag in PINNED_NODES:
        ops.fix(tag, 1, 1, 1)

# ── 7. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    for ele_tag, i_node, j_node, area in TRUSS_ELEMENTS:
        ops.element("truss", ele_tag, i_node, j_node, area * mm**2, MAT_TRUSS)

# ── 8. OUTPUT DATABASE (ODB) ─────────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: str = "static") -> "opst.post.CreateODB":
    output_dir.mkdir(parents=True, exist_ok=True)
    abs_str = str(output_dir.resolve())
    if sys.platform == "win32" and not abs_str.startswith("\\\\?\\"):
        abs_str = "\\\\?\\" + abs_str
    opst.post.set_odb_path(abs_str)
    odb = opst.post.CreateODB(odb_tag=odb_tag)
    odb.save_model_data()
    return odb

# ── 9. LOADING ───────────────────────────────────────────────────────────────
def define_loads() -> None:
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    for node in LOAD_NODES:
        ops.load(node, 0.0, 0.0, LOAD_FZ)

# ── 10. ANALYSIS ─────────────────────────────────────────────────────────────
def run_static(odb: "opst.post.CreateODB", on_step) -> None:
    """Linear static analysis by LoadControl, one step per analyze call, as in Exam01.tcl.

    Manual loop under the AGENT.md §3c LoadControl exception (SmartAnalyze would replace
    the LoadControl integrator with DisplacementControl).
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.01)
    ops.analysis("Static")
    for _ in range(N_STEPS):
        if ops.analyze(1) != 0:
            print("  analysis failed; stopping")
            break
        odb.fetch_response_step()
        on_step()

def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build the truss, run the static analysis, and return the ODB and the histories."""
    output_dir.mkdir(parents=True, exist_ok=True)
    init_model()
    define_materials()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)

    odb = create_odb(output_dir, odb_tag="static")
    define_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    # Mirrors the source recorders: node0.out (all nodes, UX UY UZ), node5.out (node 5),
    # and ele0.out (localForce of elements 1-46 = axial force)
    nodes_hist, ele_hist = [], []

    def on_step() -> None:
        lf = ops.getTime()
        row = [lf]
        for n in range(1, N_NODES + 1):
            row += [ops.nodeDisp(n, 1), ops.nodeDisp(n, 2), ops.nodeDisp(n, 3)]
        nodes_hist.append(row)
        ele_hist.append([lf] + [float(ops.eleResponse(e, "axialForce")[0])
                                for e in range(1, N_ELEMS + 1)])

    run_static(odb, on_step)
    return odb, {"nodes": np.array(nodes_hist, dtype=float),
                 "elements": np.array(ele_hist, dtype=float)}

# ── 11. POST-PROCESSING ──────────────────────────────────────────────────────
def _rel_error(sim: np.ndarray, ref: np.ndarray) -> float:
    """Maximum absolute difference relative to the largest reference magnitude."""
    return float(np.max(np.abs(sim - ref)) / max(np.max(np.abs(ref)), 1e-30))

def post_process(odb: "opst.post.CreateODB", output_dir: Path, results: dict) -> None:
    """Flush the ODB, render visualisations, and compare with the three source outputs."""
    odb.save_response()
    nodes = results["nodes"]          # (100, 55): LF, nodes 1-18 x UX UY UZ
    elems = results["elements"]       # (100, 47): LF, axial force of elements 1-46
    ref_dir = Path(__file__).parent / "ref"
    ref_nodes = np.loadtxt(str(ref_dir / "node0.out"))    # (100, 55)
    ref_node5 = np.loadtxt(str(ref_dir / "node5.out"))    # (100, 4)
    ref_elems = np.loadtxt(str(ref_dir / "ele0.out"))     # (100, 47)
    np.savetxt(str(output_dir / "node0_history.csv"), nodes, delimiter=",")
    np.savetxt(str(output_dir / "ele0_history.csv"), elems, delimiter=",")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))
        vis_defo(output_dir, filename="vis_05_deformed.html", odb_tag="static", resp_dof="UZ", scale=50.0)
        vis_slider(output_dir, filename="vis_06_slider.html", odb_tag="static", resp_dof="UZ", scale=50.0)
        print("  Visualisation HTMLs rendered in output/")

    # Columns: 0 = load factor (excluded from every error below), then UX UY UZ per node
    # (node n at 3n-2, 3n-1, 3n). Node 5 is therefore columns 13, 14, 15.
    cols5 = [3 * NODE_MONITOR - 2, 3 * NODE_MONITOR - 1, 3 * NODE_MONITOR]
    sim5 = nodes[:, cols5]
    # The zero-energy mode leaves one common UY translation of nodes 11-18 undetermined,
    # so the comparison also reports the error with that translation removed.
    top_uy = [3 * n - 1 for n in TOP_CHORD_NODES]
    d_top = nodes[:, top_uy] - ref_nodes[:, top_uy]
    offset = d_top.mean(axis=1)
    corrected = nodes.copy()
    corrected[:, top_uy] -= offset[:, None]
    print("\nVerification against the source outputs:")
    print(f"  Recorded steps: {len(nodes)} / {N_STEPS}")
    print(f"  node0.out (nodes 1-18, UX UY UZ): max error {100 * _rel_error(nodes[:, 1:], ref_nodes[:, 1:]):.4f}% of max |value|")
    print(f"  node0.out, common top-chord UY translation removed: {100 * _rel_error(corrected[:, 1:], ref_nodes[:, 1:]):.6f}% of max |value|")
    print(f"  top-chord UY offset at final step: {offset[-1]:+.6f} mm (nodes 11-18 within {np.max(np.abs(d_top - offset[:, None])):.1e} mm of it)")
    print(f"  node5.out (node 5):               max error {100 * _rel_error(sim5, ref_node5[:, 1:]):.6f}% of max |value|")
    print(f"  ele0.out (axial forces 1-46):     max error {100 * _rel_error(elems[:, 1:], ref_elems[:, 1:]):.6f}% of max |value|")
    print(f"  Final node 5 UZ = {nodes[-1, cols5[2]]:.6f} mm; final element 5 force = {elems[-1, 5]:.3f} N")

# ── 12. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Static Analysis of a Truss Bridge Structure: analysis complete.")
