# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 3D RC Column Static Pushover, four-element fiber model (Dino OpenSees tutorial, video 03/04)
UniqueID : Dino_RC_Column_4Elem_3D_Pushover
Purpose  : Gravity (1500 kN) followed by a 100 mm displacement-controlled
           pushover of a 3 m reinforced-concrete column built from four
           nonlinearBeamColumn elements that share one 500x500 mm fiber section.
Ref      : ref/co.tcl (source), ref/node0.out (nodes 1-5), ref/node1.out (node 1)
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
MAT_STEEL_BAR    = 1      # Steel01 longitudinal bars
MAT_CONCRETE     = 2      # Concrete01 core
MAT_ELASTIC_DEAD = 3      # uniaxial Elastic: defined in co.tcl, used by no fiber
SEC_COLUMN       = 1
NODE_TOP         = 1
MONITOR_NODES    = (1, 2, 3, 4, 5)   # node0.out records nodes 1-5 in tag order

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Node coordinates [mm], verbatim from co.tcl (column along Z, X offset 6000 mm)
NODE_XYZ = {
    1: (6000.0, 0.0, 3000.0),   # top
    2: (6000.0, 0.0, 0.0),      # base
    3: (6000.0, 0.0, 750.0),
    4: (6000.0, 0.0, 1500.0),
    5: (6000.0, 0.0, 2250.0),
}
# (element tag, i-node, j-node, geomTransf tag), verbatim from co.tcl
ELEMENTS = [(1, 2, 3, 1), (2, 3, 4, 2), (3, 4, 5, 3), (4, 5, 1, 4)]
N_IP = 3                  # integration points per element, as in co.tcl
# Restraint flags per node (UX, UY, UZ, RX, RY, RZ; 1 = fixed), verbatim from co.tcl
RESTRAINTS = {
    1: (0, 1, 0, 1, 0, 1),
    2: (1, 1, 1, 1, 1, 1),
    3: (0, 1, 0, 1, 0, 1),
    4: (0, 1, 0, 1, 0, 1),
    5: (0, 1, 0, 1, 0, 1),
}

# Materials, verbatim from co.tcl
FY_BAR  = 335.0 * MPa        # Steel01 yield strength
ES_BAR  = 200000.0 * MPa     # Steel01 elastic modulus
B_BAR   = 0.00001            # Steel01 hardening ratio
FPC     = 26.8 * MPa        # Concrete01 peak compressive stress (passed negative)
EPS_C0  = -0.002             # Concrete01 strain at peak stress
FPCU    = 15.0 * MPa         # Concrete01 ultimate compressive stress (passed negative)
EPS_CU  = -0.006             # Concrete01 ultimate strain
E_DEAD  = 1.999e5 * MPa      # Elastic material 3 (not used by any fiber)

# Section (co.tcl "section Fiber 1"): 5x5 concrete fibers of 100x100 mm and
# 20 longitudinal bars of 200 mm^2 on the perimeter
CONC_GRID = (-200.0, -100.0, 0.0, 100.0, 200.0)   # fiber centres [mm]
CONC_AREA = 1.0e4                                   # [mm^2]
BAR_AREA  = 200.0                                   # [mm^2]
BAR_POS = [
    (-215.0, -215.0), (-107.5, -215.0), (0.0, -215.0), (107.5, -215.0), (215.0, -215.0),
    (-215.0, 215.0), (-107.5, 215.0), (0.0, 215.0), (107.5, 215.0), (215.0, 215.0),
    (-215.0, -143.3), (-215.0, -71.67), (-215.0, 0.0), (-215.0, 71.67), (-215.0, 143.3),
    (215.0, -143.3), (215.0, -71.67), (215.0, 0.0), (215.0, 71.67), (215.0, 143.3),
]
# Torsional stiffness [N mm^2]. co.tcl assigns none; 1e8 N*mm is the default noted
# in AGENT.md. Torsion is fixed at both ends, so the response is unaffected.
GJ = 1.0e8 * N * mm**2

# Loads [N, N mm, ...], both at the top node
GRAVITY_LOAD     = (0.0, 0.0, -1.5e6, 0.0, 0.0, 0.0)   # pattern 1 (1500 kN downward)
LATERAL_REF_LOAD = (1000.0, 0.0, 0.0, 0.0, 0.0, 0.0)   # pattern 3 (1 kN reference, UX)
N_GRAV_STEPS = 100        # LoadControl 0.01 x 100 -> load factor 1.0
GRAV_INCR    = 0.01
PUSH_TARGET  = 100.0 * mm # 100 steps of 1 mm
PUSH_INCR    = 1.0 * mm
N_PUSH_STEPS = 100        # co.tcl: analyze 100

# ── 4. MODEL INITIALISATION ─────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)

# ── 5. MATERIALS ────────────────────────────────────────────────────────────
def define_materials() -> None:
    ops.uniaxialMaterial("Steel01", MAT_STEEL_BAR, FY_BAR, ES_BAR, B_BAR)
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE, -FPC, EPS_C0, -FPCU, EPS_CU)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_DEAD, E_DEAD)

# ── 6. SECTIONS ─────────────────────────────────────────────────────────────
def define_sections() -> None:
    # 3D fiber sections need an explicit torsional stiffness in OpenSeesPy
    ops.section("Fiber", SEC_COLUMN, "-GJ", GJ)
    for z in CONC_GRID:
        for y in CONC_GRID:
            ops.fiber(y * mm, z * mm, CONC_AREA * mm**2, MAT_CONCRETE)
    for y, z in BAR_POS:
        ops.fiber(y * mm, z * mm, BAR_AREA * mm**2, MAT_STEEL_BAR)

# ── 7. NODES ────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    for tag, (x, y, z) in NODE_XYZ.items():
        ops.node(tag, x * mm, y * mm, z * mm)

# ── 8. BOUNDARY CONDITIONS ──────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    for tag, flags in RESTRAINTS.items():
        ops.fix(tag, *flags)

# ── 9. ELEMENTS ─────────────────────────────────────────────────────────────
def define_elements() -> None:
    for tag in (1, 2, 3, 4):
        ops.geomTransf("Linear", tag, 1.0, 0.0, 0.0)
    for ele_tag, i_node, j_node, transf in ELEMENTS:
        ops.element("nonlinearBeamColumn", ele_tag, i_node, j_node, N_IP, SEC_COLUMN, transf)

# ── 10. OUTPUT DATABASE (ODB) ───────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: str = "pushover") -> "opst.post.CreateODB":
    output_dir.mkdir(parents=True, exist_ok=True)
    abs_str = str(output_dir.resolve())
    if sys.platform == "win32" and not abs_str.startswith("\\\\?\\"):
        abs_str = "\\\\?\\" + abs_str
    opst.post.set_odb_path(abs_str)
    odb = opst.post.CreateODB(odb_tag=odb_tag)
    odb.save_model_data()
    return odb

# ── 11. LOADING ─────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(NODE_TOP, *GRAVITY_LOAD)

def define_lateral_loads() -> None:
    ops.timeSeries("Linear", 2)
    ops.pattern("Plain", 3, 2)
    ops.load(NODE_TOP, *LATERAL_REF_LOAD)

# ── 12. ANALYSIS ────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB", n_steps: int = N_GRAV_STEPS) -> None:
    """Gravity by LoadControl, one step per analyze call (AGENT.md §3c exception)."""
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", GRAV_INCR)
    ops.analysis("Static")
    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()
    ops.loadConst("-time", 0.0)

def run_pushover(odb: "opst.post.CreateODB", on_step) -> None:
    """Top-node displacement control via SmartAnalyze: Newton first, EnergyIncr 1e-6 as in co.tcl."""
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="EnergyIncr",
        testTol=1.0e-6,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 40, 20, 30, 50, 60],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-4,
        printPer=0,
        testPrintFlag=0,
    )
    for seg in analysis.static_split([PUSH_TARGET], maxStep=PUSH_INCR):
        analysis.StaticAnalyze(node=NODE_TOP, dof=1, seg=seg)
        odb.fetch_response_step()
        on_step()
    analysis.close()

def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build the model, run gravity and pushover, and return the ODB and the recorded history."""
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
    run_gravity(odb)
    define_lateral_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    # Mirrors co.tcl's recorders (created after gravity): time + UX, UY, UZ of nodes 1-5
    history = []

    def on_step() -> None:
        row = [ops.getTime()]
        for n in MONITOR_NODES:
            row += [ops.nodeDisp(n, 1), ops.nodeDisp(n, 2), ops.nodeDisp(n, 3)]
        history.append(row)

    run_pushover(odb, on_step)
    return odb, {"history": np.array(history, dtype=float)}

# ── 13. POST-PROCESSING ─────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path, results: dict) -> None:
    """Flush ODB, render visualisations, and compare with the co.tcl recorder outputs."""
    odb.save_response()
    sim = results["history"]                         # (100, 16): time, nodes 1-5 x UX, UY, UZ
    ref_dir = Path(__file__).parent / "ref"
    ref0 = np.loadtxt(str(ref_dir / "node0.out"))    # (100, 16), same layout as sim
    ref1 = np.loadtxt(str(ref_dir / "node1.out"))    # (100, 4): time, UX, UY, UZ of node 1
    np.savetxt(str(output_dir / "node0_history.csv"), sim, delimiter=",")

    # Load-displacement comparison at node 1
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.plot(ref1[:, 1], ref1[:, 0], "k-", linewidth=1.5, alpha=0.6, label="Reference (co.tcl)")
        ax.plot(sim[:, 1], sim[:, 0], "r--", linewidth=1.5, alpha=0.85, label="Simulation")
        ax.set_xlabel("Top displacement UX (mm)")
        ax.set_ylabel("Lateral load factor (kN)")
        ax.set_title("Pushover at node 1")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "pushover_compare.png"), dpi=150)
        plt.close(fig)
        print("  Comparison plot saved to output/pushover_compare.png")
    except Exception as e:
        print(f"  Matplotlib plotting skipped: {e}")

    # opstool HTML renders
    if not _headless():
        opst.post.set_odb_path(str(output_dir))
        vis_defo(output_dir, filename="vis_05_deformed.html", odb_tag="pushover", resp_dof="UX", scale=10.0)
        vis_slider(output_dir, filename="vis_06_slider.html", odb_tag="pushover", resp_dof="UX", scale=10.0)
        vis_anim(output_dir, filename="vis_07_animation.html", odb_tag="pushover", defo_scale=10.0,
                 resp_dof=("UX", "UY", "UZ"))
        print("  Visualisation HTMLs rendered in output/")

    # Verification against the co.tcl recorders
    n = min(len(sim), len(ref0), len(ref1))
    lf_s, lf_r = sim[:n, 0], ref1[:n, 0]
    rel = np.abs(lf_s - lf_r) / np.maximum(np.abs(lf_r), 1e-12)
    print("\nVerification against co.tcl recorders (node0.out, node1.out):")
    print(f"  Recorded pushover steps: {len(sim)} / {N_PUSH_STEPS}")
    print(f"  Load factor (kN), node 1: mean relative error {100 * rel.mean():.4f}%, "
          f"max {100 * rel.max():.4f}% (step {int(rel.argmax()) + 1}), "
          f"max abs error {np.abs(lf_s - lf_r).max():.3f} kN")
    print(f"  Node 1 UX max abs error {np.abs(sim[:n, 1] - ref1[:n, 1]).max():.3e} mm, "
          f"UZ max abs error {np.abs(sim[:n, 3] - ref1[:n, 3]).max():.3e} mm")
    for k, node in enumerate(MONITOR_NODES):
        cols = slice(1 + 3 * k, 4 + 3 * k)
        err = np.abs(sim[:n, cols] - ref0[:n, cols]).max(axis=0)
        print(f"  node {node}: max abs error UX {err[0]:.3e} mm, UY {err[1]:.3e} mm, UZ {err[2]:.3e} mm")

# ── 14. MAIN ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Static Pushover Analysis of 4-element RC column: Analysis complete.")
