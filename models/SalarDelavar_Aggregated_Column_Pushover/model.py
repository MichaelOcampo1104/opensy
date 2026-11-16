# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D cantilever column with an aggregated axial-flexural section
           (uncoupled axial and moment-curvature behaviour), top-node pushover
UniqueID : SalarDelavar_Aggregated_Column_Pushover
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR)
Date     : 2026-11-16
Purpose  : One nonlinearBeamColumn (5 integration points) whose section is a
           section Aggregator: elastic axial EA plus a Hysteretic moment-curvature
           law. Gravity is applied by LoadControl, then the top node is pushed
           sideways in 5 mm steps to 1750 mm.
Ref      : py_ref/COLUMN_PUSHOVER_P-M_INTERACTION.py (source), py_ref/SECTION_ANALYSIS_FUN.py,
           py_ref/ANALYSIS_FUNCTION.py, py_ref/RESULTS_COLUMN_PUSHOVER_P-M_INTERACTION.png
           (reference figure). OpenSees example:
           https://opensees.berkeley.edu/OpenSees/manuals/ExamplesManual/HTML/3600.htm
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops
import opstool as opst

# models/<UniqueID>/model.py -> repository root is parents[2]
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *  # noqa: E402,F403  (mm, m, sec, N, MPa)
from vis_utils import (  # noqa: E402
    _headless,
    vis_defo,
    vis_loads,
    vis_model,
    vis_nodes,
    vis_pre_analysis,
)
from plot_utils import COLORS, _style_ax  # noqa: E402

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
ODB_TAG = 1
NODE_BASE = 1       # fixed base, (0, 0)
NODE_TOP = 2        # top node, pushed in x, (0, L)
ELE_COL = 1         # nonlinearBeamColumn
SEC_COL = 1         # section Aggregator: P from MAT_AXIAL, Mz from MAT_FLEX
TRANSF_COL = 1      # geomTransf Linear
MAT_FLEX = 2        # Hysteretic moment-curvature
MAT_AXIAL = 3       # Elastic axial stiffness
TS_GRAV = 1         # gravity time series and pattern
PAT_GRAV = 1
TS_PUSH = 100       # pushover reference pattern, created after loadConst (AGENT.md §12z)
PAT_PUSH = 100

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Section rectangles [x_centroid, y_centroid, width, height], in mm (source SECTION_ANALYSIS_FUN.py).
RECTS = np.array([
    [-55.0, 250.0, 10.0, 580.0],   # side plate, labelled "Right Web Plate" in the source
    [250.0, 520.0, 500.0, 20.0],   # top plate
    [250.0, 500.0, 600.0, 20.0],   # top flange
    [450.0, 250.0, 20.0, 480.0],   # right web
    [50.0, 250.0, 20.0, 480.0],    # left web
    [250.0, 0.0, 600.0, 20.0],     # bottom flange
    [250.0, -20.0, 500.0, 20.0],   # bottom plate
    [555.0, 250.0, 10.0, 580.0],   # side plate on the right
]) * mm

E_S = 21e4 * MPa                   # steel modulus (originally 21e4 N/mm^2)
L_COL = 5000.0 * mm                # column length (originally 5000 mm)
WEIGHT = 200000.0 * N              # top weight (source comment says kg; the source uses it as N, i.e. 200 kN)
G_ACC = 9.81 * m / sec**2          # 9810 mm/s^2 (source g)
MASS = WEIGHT / G_ACC              # nodal mass, N.s^2/mm (tonne)
D_MAX = 0.35 * L_COL               # ultimate top displacement (1750 mm)
D_INCR = 0.001 * L_COL             # displacement increment (5 mm), giving 350 steps
MAX_ITER = 1000                    # convergence iterations (source)
MAX_TOL = 1.0e-6                   # convergence tolerance (source, mm units)
N_GRAV = 10                        # gravity load steps (source NstepGravity)
PUSH_REF = (1.0 * N, -1.0 * N, 0.0 * N)   # pushover reference load: the -1 N vertical part is kept from the source
FI_Y = 1.474e-6 / mm               # yield curvature (1/mm)
FI_SU = 5.41e-4 / mm               # ultimate curvature (1/mm)
PINCH_X = 0.4
PINCH_Y = 0.2
DAMAGE1 = 0.0
DAMAGE2 = 0.0
BETA = 0.1
NIP = 5                            # integration points of the nonlinearBeamColumn

def section_geometry(rects: np.ndarray) -> tuple:
    """Area, centroid and Ix of the composite section (same arithmetic as SECTION_ANALYSIS_FUN.py).

    Args:
        rects: rows of [x_centroid, y_centroid, width, height].

    Returns:
        (A_total, Ix_total, x_c, y_c) in mm^2 and mm^4.
    """
    areas = rects[:, 2] * rects[:, 3]
    x_c = float(np.sum(areas * rects[:, 0]) / np.sum(areas))
    y_c = float(np.sum(areas * rects[:, 1]) / np.sum(areas))
    ix_total = 0.0
    for _, y, b, h in rects:
        ix_total += b * h**3 / 12.0 + b * h * (y - y_c) ** 2
    return float(np.sum(areas)), ix_total, x_c, y_c

A_TOTAL, IX_TOTAL, X_C, Y_C = section_geometry(RECTS)
EI_COL = E_S * IX_TOTAL            # flexural rigidity (N.mm^2)
EA_COL = E_S * A_TOTAL             # axial rigidity (N)
MY_COL = EI_COL * FI_Y             # yield moment (N.mm)
MU_COL = 1.36 * MY_COL             # ultimate moment (N.mm)

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Start a fresh 2D model with three DOFs per node (ux, uy, rz)."""
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Hysteretic moment-curvature law (pinching and degradation) and the elastic axial law."""
    ops.uniaxialMaterial(
        "Hysteretic", MAT_FLEX,
        MY_COL, FI_Y, MU_COL, FI_SU, 0.23 * MU_COL, 1.13 * FI_SU,
        -MY_COL, -FI_Y, -MU_COL, -FI_SU, -0.23 * MU_COL, -1.07 * FI_SU,
        PINCH_X, PINCH_Y, DAMAGE1, DAMAGE2, BETA,
    )
    ops.uniaxialMaterial("Elastic", MAT_AXIAL, EA_COL)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    """Aggregated section: axial force from MAT_AXIAL (P), moment from MAT_FLEX (Mz)."""
    ops.section("Aggregator", SEC_COL, MAT_AXIAL, "P", MAT_FLEX, "Mz")

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Base at the origin and top node at the column height, with the top lumped mass."""
    ops.node(NODE_BASE, 0.0, 0.0)
    ops.node(NODE_TOP, 0.0, L_COL)
    ops.mass(NODE_TOP, MASS, MASS, 0.0)

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix the base in x, y and rotation.

    The source comment says "free theta", but its call fix(1, 1, 1, 1) fixes all three DOFs,
    and the code is kept as written.
    """
    ops.fix(NODE_BASE, *[1, 1, 1])

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Linear geometric transformation and one nonlinearBeamColumn."""
    ops.geomTransf("Linear", TRANSF_COL)
    ops.element("nonlinearBeamColumn", ELE_COL, NODE_BASE, NODE_TOP, NIP, SEC_COL, TRANSF_COL)

# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb() -> "opst.post.CreateODB":
    """Nodal responses only. Frame section responses are off (AGENT.md §12v); element forces are read per step."""
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
    )
    odb.save_model_data()
    return odb

# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Gravity on the top node (source: pattern Plain 1 Linear, load (0, -Weight, 0))."""
    ops.timeSeries("Linear", TS_GRAV)
    ops.pattern("Plain", PAT_GRAV, TS_GRAV)
    ops.load(NODE_TOP, 0.0, -WEIGHT, 0.0)

def define_pushover_loads() -> None:
    """Pushover reference pattern, defined after loadConst so that it is not frozen (AGENT.md §12z)."""
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    ops.load(NODE_TOP, *PUSH_REF)

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity() -> None:
    """Gravity by a manual LoadControl loop (the AGENT.md §3c exception), then freeze the load."""
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", MAX_TOL, MAX_ITER)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / N_GRAV)
    ops.analysis("Static")
    for _ in range(N_GRAV):
        ops.analyze(1)
    ops.loadConst("-time", 0.0)

def run_pushover(odb: "opst.post.CreateODB") -> dict:
    """Top-node pushover in x, 5 mm per step, through SmartAnalyze (AGENT.md §3c).

    The source's EnergyIncr test (1e-6, 1000 iterations) and Newton start are kept.
    The fall-back algorithms are SmartAnalyze's. The source's own fall-back ladder is not
    reproduced: it contains the algorithm name 'RaphsonNewton', which OpenSees does not define.
    """
    ops.constraints("Plain")                     # handlers set after wipeAnalysis, before SmartAnalyze
    ops.numberer("Plain")
    ops.system("BandGeneral")
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="EnergyIncr",
        testTol=MAX_TOL,
        testIterTimes=MAX_ITER,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 40, 20, 30, 50, 60],
        printPer=0,
        testPrintFlag=0,
    )
    history = {key: [] for key in ("lateral", "axial_disp", "rotation", "axial", "shear", "moment")}
    segs = analysis.static_split([D_MAX], maxStep=D_INCR)
    for seg in segs:
        ok = analysis.StaticAnalyze(node=NODE_TOP, dof=1, seg=seg)
        if ok < 0:
            break
        odb.fetch_response_step()
        ef = ops.eleResponse(ELE_COL, "force")      # global end forces at the base node (Fx, Fy, Mz, ...)
        history["lateral"].append(ops.nodeDisp(NODE_TOP, 1))
        history["axial_disp"].append(ops.nodeDisp(NODE_TOP, 2))
        history["rotation"].append(ops.nodeDisp(NODE_TOP, 3))
        history["axial"].append(-ef[1])             # compressive axial force
        history["shear"].append(-ef[0])
        history["moment"].append(-ef[2])
    analysis.close()
    return {key: np.array(value) for key, value in history.items()}

def run_analysis(output_dir: Path):
    """Build the model, apply gravity, run the pushover, and return the ODB and the histories."""
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))         # must precede CreateODB (AGENT.md §12ac)
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)                           # V1
    define_elements()
    vis_model(output_dir)                           # V2
    odb = create_odb()
    define_gravity_loads()
    vis_loads(output_dir)                           # V3
    vis_pre_analysis(output_dir)                    # V4
    run_gravity()
    gravity_axial = -ops.eleResponse(ELE_COL, "force")[1]
    ops.wipeAnalysis()
    define_pushover_loads()
    history = run_pushover(odb)
    return odb, history, gravity_axial

# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def save_history(history: dict, output_dir: Path) -> None:
    """Write the per-step pushover history to CSV (SI-like N, mm, rad)."""
    table = np.column_stack([
        history["lateral"], history["axial_disp"], history["rotation"],
        history["axial"], history["shear"], history["moment"],
    ])
    np.savetxt(
        output_dir / "pushover_history.csv", table, delimiter=",",
        header="lateral_mm,axial_disp_mm,rotation_rad,axial_N,shear_N,moment_Nmm", comments="",
    )

def plot_curves(history: dict, output_dir: Path) -> None:
    """The three source curves (axial, shear, moment), drawn with the plot_utils style."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), dpi=150)
    # Magnitudes are plotted as in the source (np.abs on force and rotation).
    panels = [
        (axes[0], history["axial_disp"], np.abs(history["axial"]),
         "Axial displacement at top (mm)", "Axial compressive force (N)", "Axial force-displacement"),
        (axes[1], history["lateral"], np.abs(history["shear"]),
         "Lateral displacement at top (mm)", "Shear force (N)", "Shear force-displacement"),
        (axes[2], np.abs(history["rotation"]), np.abs(history["moment"]),
         "Rotation at top (rad)", "Moment at base (N.mm)", "Moment-rotation"),
    ]
    for ax, x, y, xlabel, ylabel, title in panels:
        ax.plot(x, y, color=COLORS["primary"], lw=2.0)
        _style_ax(ax, xlabel, ylabel, title)
    fig.tight_layout()
    fig.savefig(output_dir / "pushover_curves.png")
    plt.close(fig)

def post_process(odb: "opst.post.CreateODB", output_dir: Path, history: dict) -> None:
    """Flush the ODB, write the history and curves, and draw the deformed shape."""
    odb.save_response()
    save_history(history, output_dir)
    plot_curves(history, output_dir)
    if not _headless():
        vis_defo(output_dir, filename="vis_05_deformed.html", odb_tag=ODB_TAG,
                 resp_dof="UX", resp_type="disp", scale=1.0)

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    print(f"section: A = {A_TOTAL:.1f} mm^2, Ix = {IX_TOTAL:.4e} mm^4, centroid = ({X_C:.1f}, {Y_C:.1f}) mm")
    print(f"EA = {EA_COL:.4e} N, EI = {EI_COL:.4e} N.mm^2, My = {MY_COL:.4e} N.mm, Mu = {MU_COL:.4e} N.mm")
    odb, history, gravity_axial = run_analysis(output_dir)
    print(f"gravity axial force = {gravity_axial:.1f} N; steps completed = {len(history['lateral'])}")
    post_process(odb, output_dir, history)
