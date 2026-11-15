# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 3D simply supported RC beam, displacement-controlled pushdown (Dino OpenSees tutorial, Example 03)
UniqueID : Dino_Beam_Exam03_Pushdown
Purpose  : Vertical uniform load of 10 N/mm on a 3 m simply supported beam with a
           300x600 mm fiber section, pushed down at midspan (node 5, UZ) by 0.1 mm
           per step for 100 steps (10 mm).
Ref      : ref/Exam03.tcl (source). ref/node0.out is copied for completeness but
           records zeros only; no other reference output exists for this source.
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
MAT_STEEL_BAR = 1       # Steel01 bars
MAT_CONCRETE  = 2       # Concrete01 (compression only)
SEC_BEAM      = 1
MID_NODE      = 5       # midspan node (x = 1500 mm): pushdown control and history
MID_DOF       = 3       # UZ (vertical)

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Node coordinates [mm], verbatim from Exam03.tcl (beam along X)
NODE_XYZ = {
    1: (0.0, 0.0, 0.0),
    2: (3000.0, 0.0, 0.0),
    3: (500.0, 0.0, 0.0),
    4: (1000.0, 0.0, 0.0),
    5: (1500.0, 0.0, 0.0),
    6: (2000.0, 0.0, 0.0),
    7: (2500.0, 0.0, 0.0),
}
# (element tag, i-node, j-node, geomTransf tag), verbatim from Exam03.tcl
ELEMENTS = [(1, 1, 3, 1), (2, 3, 4, 2), (3, 4, 5, 3), (4, 5, 6, 4), (5, 6, 7, 5), (6, 7, 2, 6)]
N_IP = 3                  # integration points per element, as in Exam03.tcl
# Restraint flags per node (UX, UY, UZ, RX, RY, RZ; 1 = fixed), verbatim from Exam03.tcl
RESTRAINTS = {
    1: (1, 1, 1, 1, 0, 1),   # pin
    2: (0, 1, 1, 1, 0, 1),   # roller (UX free)
    3: (0, 1, 0, 1, 0, 1),
    4: (0, 1, 0, 1, 0, 1),
    5: (0, 1, 0, 1, 0, 1),
    6: (0, 1, 0, 1, 0, 1),
    7: (0, 1, 0, 1, 0, 1),
}

# Materials, verbatim from Exam03.tcl
FY_BAR  = 335.0 * MPa        # Steel01 yield strength
ES_BAR  = 200000.0 * MPa     # Steel01 elastic modulus
B_BAR   = 0.00001            # Steel01 hardening ratio
FPC     = 26.8 * MPa         # Concrete01 peak compressive stress (passed negative)
EPS_C0  = -0.002             # Concrete01 strain at peak stress
FPCU    = 10.0 * MPa         # Concrete01 ultimate compressive stress (passed negative)
EPS_CU  = -0.0033            # Concrete01 ultimate strain

# Section (Exam03.tcl "section Fiber 1"): 6x6 concrete fibers of 5000 mm^2 (300x600 mm),
# plus 5 bars (2 of 390 mm^2 on the top side, 3 of 490 mm^2 on the bottom side)
CONC_Y    = (-125.0, -75.0, -25.0, 25.0, 75.0, 125.0)     # [mm]
CONC_Z    = (-250.0, -150.0, -50.0, 50.0, 150.0, 250.0)   # [mm]
CONC_AREA = 5000.0                                          # [mm^2]
BARS = [                                                    # (y, z, area) [mm, mm, mm^2]
    (-115.0, 265.0, 390.0), (115.0, 265.0, 390.0),
    (-115.0, -265.0, 490.0), (0.0, -265.0, 490.0), (115.0, -265.0, 490.0),
]
# Torsional stiffness [N mm^2]. Exam03.tcl assigns none; 1e8 N*mm is the default noted
# in AGENT.md. Torsion is fixed at the supports, so the response is unaffected.
GJ = 1.0e8 * N * mm**2

# Load: uniform 10 N/mm in local z (vertical), on every element (beamUniform 0 -10 0)
W_UDL       = -10.0          # [N/mm]
PUSH_TARGET = -10.0 * mm     # midspan UZ target after the pushdown
PUSH_STEP   = 0.1 * mm       # magnitude of each displacement step
N_PUSH_STEPS = 100           # Exam03.tcl: analyze 100

# ── 4. MODEL INITIALISATION ─────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)

# ── 5. MATERIALS ────────────────────────────────────────────────────────────
def define_materials() -> None:
    ops.uniaxialMaterial("Steel01", MAT_STEEL_BAR, FY_BAR, ES_BAR, B_BAR)
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE, -FPC, EPS_C0, -FPCU, EPS_CU)

# ── 6. SECTIONS ─────────────────────────────────────────────────────────────
def define_sections() -> None:
    # 3D fiber sections need an explicit torsional stiffness in OpenSeesPy
    ops.section("Fiber", SEC_BEAM, "-GJ", GJ)
    for z in CONC_Z:
        for y in CONC_Y:
            ops.fiber(y * mm, z * mm, CONC_AREA * mm**2, MAT_CONCRETE)
    for y, z, area in BARS:
        ops.fiber(y * mm, z * mm, area * mm**2, MAT_STEEL_BAR)

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
    for _, _, _, transf in ELEMENTS:
        ops.geomTransf("Linear", transf, 0.0, 0.0, 1.0)     # local z = global Z
    for ele_tag, i_node, j_node, transf in ELEMENTS:
        ops.element("nonlinearBeamColumn", ele_tag, i_node, j_node, N_IP, SEC_BEAM, transf)

# ── 10. OUTPUT DATABASE (ODB) ───────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: str = "pushdown") -> "opst.post.CreateODB":
    output_dir.mkdir(parents=True, exist_ok=True)
    abs_str = str(output_dir.resolve())
    if sys.platform == "win32" and not abs_str.startswith("\\\\?\\"):
        abs_str = "\\\\?\\" + abs_str
    opst.post.set_odb_path(abs_str)
    odb = opst.post.CreateODB(odb_tag=odb_tag)
    odb.save_model_data()
    return odb

# ── 11. LOADING ─────────────────────────────────────────────────────────────
def define_loads() -> None:
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    for ele_tag, _, _, _ in ELEMENTS:
        ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform", 0.0, W_UDL, 0.0)

# ── 12. ANALYSIS ────────────────────────────────────────────────────────────
def run_pushdown(odb: "opst.post.CreateODB", on_step) -> None:
    """Midspan UZ control via SmartAnalyze: Newton first, EnergyIncr 1e-6 as in Exam03.tcl."""
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
    for seg in analysis.static_split([PUSH_TARGET], maxStep=PUSH_STEP):
        analysis.StaticAnalyze(node=MID_NODE, dof=MID_DOF, seg=seg)
        odb.fetch_response_step()
        on_step()
    analysis.close()

def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build the model, run the pushdown, and return the ODB and the midspan history."""
    output_dir.mkdir(parents=True, exist_ok=True)
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)

    odb = create_odb(output_dir, odb_tag="pushdown")
    define_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    # Midspan history: load factor (pseudo-time), UX, UY, UZ of node 5
    history = []

    def on_step() -> None:
        history.append([ops.getTime(), ops.nodeDisp(MID_NODE, 1),
                        ops.nodeDisp(MID_NODE, 2), ops.nodeDisp(MID_NODE, 3)])

    run_pushdown(odb, on_step)
    return odb, {"history": np.array(history, dtype=float)}

# ── 13. POST-PROCESSING ─────────────────────────────────────────────────────
def cracked_flexural_stiffness() -> float:
    """EI about the local y axis with Concrete01 (no tension) and initial tangents, no axial load."""
    E_c = 2.0 * FPC / abs(EPS_C0)
    fibers = [(z, CONC_AREA, E_c) for z in CONC_Z for _ in CONC_Y]
    fibers += [(z, a, ES_BAR) for _, z, a in BARS]

    def active(c):
        # sagging (downward load): compression is above the neutral axis, so concrete
        # below it (z < c) is in tension and carries no stress
        return [(z, a, E) for z, a, E in fibers if not (E == E_c and z - c < 0)]

    def net_force(c):
        return sum(E * a * (z - c) for z, a, E in active(c))

    lo, hi = -250.0, 250.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if net_force(lo) * net_force(mid) <= 0.0:
            hi = mid
        else:
            lo = mid
    c = 0.5 * (lo + hi)
    return sum(E * a * (z - c) ** 2 for z, a, E in active(c))

def post_process(odb: "opst.post.CreateODB", output_dir: Path, results: dict) -> None:
    """Flush ODB, render visualisations, and check the first steps against elastic beam theory."""
    odb.save_response()
    sim = results["history"]                       # (100, 4): load factor, UX, UY, UZ of node 5
    np.savetxt(str(output_dir / "midspan_history.csv"), sim, delimiter=",")

    # Load-displacement plot (no reference curve exists for this source)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.plot(-sim[:, 3], sim[:, 0], "r-", linewidth=1.5, label="Simulation")
        ax.set_xlabel("Midspan deflection |UZ| (mm)")
        ax.set_ylabel("Load factor (x 10 N/mm UDL)")
        ax.set_title("Pushdown at midspan (node 5)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "pushdown_curve.png"), dpi=150)
        plt.close(fig)
        print("  Pushdown plot saved to output/pushdown_curve.png")
    except Exception as e:
        print(f"  Matplotlib plotting skipped: {e}")

    # opstool HTML renders
    if not _headless():
        opst.post.set_odb_path(str(output_dir))
        vis_defo(output_dir, filename="vis_05_deformed.html", odb_tag="pushdown", resp_dof="UZ", scale=10.0)
        vis_slider(output_dir, filename="vis_06_slider.html", odb_tag="pushdown", resp_dof="UZ", scale=10.0)
        vis_anim(output_dir, filename="vis_07_animation.html", odb_tag="pushdown", defo_scale=10.0,
                 resp_dof=("UX", "UY", "UZ"))
        print("  Visualisation HTMLs rendered in output/")

    # Elastic check: the first steps are linear, so midspan deflection = load factor / C
    L = 3000.0
    EI = cracked_flexural_stiffness()
    C = 5.0 * abs(W_UDL) * L**4 / (384.0 * EI)      # mm per unit load factor
    print("\nElastic check (cracked section, initial tangents, simply supported UDL):")
    print(f"  EI_cracked = {EI:.4e} N mm^2 ; deflection per unit load factor C = {C:.5f} mm")
    for i in range(3):
        lam, dz = sim[i, 0], sim[i, 3]
        print(f"  step {i + 1}: UZ = {dz:.4f} mm, load factor sim = {lam:.4f}, "
              f"theory = {abs(dz) / C:.4f}, ratio = {lam / (abs(dz) / C):.5f}")
    lam_end, dz_end = sim[-1, 0], sim[-1, 3]
    print("\nPushdown result (no usable reference output):")
    print(f"  Recorded steps: {len(sim)} / {N_PUSH_STEPS}")
    print(f"  Final midspan UZ = {dz_end:.4f} mm, final load factor = {lam_end:.4f} "
          f"(UDL {abs(lam_end) * abs(W_UDL):.2f} N/mm)")
    print("  Reference status: ref/node0.out records zeros only; node5.out and element outputs are absent.")

# ── 14. MAIN ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Pushdown analysis of the Exam03 simply supported beam: analysis complete.")
