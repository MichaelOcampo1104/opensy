# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D cable suspension bridge (Presidente Ibáñez type). Cables and hangers are corotational
           truss elements; the deck is a corotational elastic beam (bending stiffness added, see README)
UniqueID : SalarDelavar_Cable_Suspension_Bridge_04
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-20
Purpose  : Vertical pushover of a deck node, free vibration after a static deck displacement
           (undamped and Rayleigh-damped), and the vertical response to ground motion Y.
Ref      : py_ref/OPENSEES_CABLE_SUSPENSION_BRIDGE_04.py (source) and its helpers in py_ref/
           (ANALYSIS_FUNCTION.py, DAMPING_RATIO_FUN.py, EIGENVALUE_ANALYSIS_FUN.py, RAYLEIGH_DAMPING_FUN.py,
           BILINEAR_CURVE.py, SALAR_MATH.py, PLOT_2D.py), py_ref/README.md and py_ref/OPENSEES_CABLE_SUSPENSION_BRIDGE_04.png
           (reference figure, a 51-node version). Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CABLE_SUSPENSION_BRIDGE/OPENSEES_CABLE_SUSPENSION_BRIDGE_04
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
from units import *  # noqa: E402,F403  (N, mm, sec, m, MPa)
from vis_utils import (  # noqa: E402
    vis_curves,
    vis_defo,
    vis_loads,
    vis_model,
    vis_nodes,
    vis_pre_analysis,
)
from plot_utils import COLORS, _style_ax  # noqa: E402

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Node and element tags follow the source numbering; they are built by the helpers in section 3.
ODB_PUSH = "pushover"
ODB_FREE_UNDAMPED = "free_undamped"
ODB_FREE_DAMPED = "free_damped"
ODB_DYNAMIC = "dynamic"
MAT_CABLE = 1           # Elastic, used by the cables and hangers
TRANSF_DECK = 1         # Corotational transformation for the deck beams
TS_STATIC = 1           # unit load: pushover and the initial deck displacement
PAT_STATIC = 1
TS_GROUND = 200         # ground acceleration Y (source tag 200)
PAT_GROUND = 200

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
n_cable_nodes = 22                       # nodes per cable (source num_nodes)
span = 210000.0 * mm                     # main span (source L)
tower_top = 25000.0 * mm                 # height of the top cable at the towers (source H1)
arc_depth = 20000.0 * mm                 # sag of the top cable (source arc_depth)
E_cable = 210e5 * MPa                    # 210e5 N/mm^2 as written in the source (100x structural steel; see README)
dia_deck = 145600.0 * mm                 # source "equivalent diameter" of the deck; used as a diameter, as in the source
dia_top = 300.0 * mm                     # top cable equivalent diameter (source Cable_Dia_02)
dia_hanger = 50.0 * mm                   # hanger equivalent diameter (source Cable_Dia_03)
A_deck = np.pi * dia_deck**2 / 4         # deck area, as in the source (1.67e10 mm^2)
A_top = np.pi * dia_top**2 / 4
A_hanger = np.pi * dia_hanger**2 / 4
I_deck = np.pi * dia_deck**4 / 64.0      # ADDED: bending inertia of the solid circle with the deck diameter (not in the source; see README)
total_mass = 5.0e7 * N * sec**2 / mm     # source TOTAL_MASS = 5e7, labelled kg but used as N.s^2/mm (see README)
mass_node = total_mass / n_cable_nodes   # lumped at each deck node, in x and y
max_disp = -2500.0 * mm                  # pushover target, downward (source MAX_DISP)
disp_incr = -0.01 * mm                   # pushover increment (source disp_incr): 250000 steps
pushover_tol = 1.0e-6                    # source MAX_TOLERANCE for the pushover
pushover_iter = 50000                    # source MAX_ITERATIONS for the pushover
u0 = 20.0 * mm                           # initial deck displacement, upward (source u0)
damping_ratio = 0.01                     # source damping_ratio (mode 1)
damping_ratio_2 = 0.6 * damping_ratio    # source: mode 2 uses 0.6 times damping_ratio
duration = 50.0 * sec                    # analysis length (source)
dt = 0.01 * sec                          # time step (source)
n_transient = int(round(duration / dt))  # 5000 steps
transient_tol = 1.0e-6                   # source MAX_TOLERANCE for the free and seismic runs
transient_iter = 10000                   # source MAX_ITERATIONS for the free and seismic runs
gm_factor = 9810.0 * mm / sec**2         # source GMfact: the record is in g
ssf_y = 1.0                              # source SSF_Y
iv0_y = 0.0005 * mm / sec                # source iv0_Y, initial ground velocity
odb_every_pushover = 2500                # 100 ODB fetches over 250000 steps (AGENT.md §3d)
odb_every_transient = 10                 # 500 fetches over 5000 steps

# Tag helpers (source numbering, n_cable_nodes = 22):
#   top cable nodes 1..22, deck nodes 23..44, top cable elements 1..21, deck beams 23..43, hangers 45..66.
def top_node(i: int) -> int:
    """Tag of top-cable node i (0-based)."""
    return i + 1


def deck_node(i: int) -> int:
    """Tag of deck node i (0-based)."""
    return n_cable_nodes + i + 1


def control_node() -> int:
    """Tag of the source's control node (mid_node = int(num_nodes + 0.5 * num_nodes)). It is not the midspan."""
    return int(n_cable_nodes + 0.5 * n_cable_nodes)


def support_nodes() -> list:
    """Tags of the four supports: both ends of the top cable and of the deck."""
    return [top_node(0), top_node(n_cable_nodes - 1), deck_node(0), deck_node(n_cable_nodes - 1)]


def top_element(i: int) -> int:
    """Tag of the top-cable element between top nodes i and i+1."""
    return i + 1


def deck_element(i: int) -> int:
    """Tag of the deck beam between deck nodes i and i+1."""
    return n_cable_nodes + i + 1


def hanger_element(i: int) -> int:
    """Tag of the hanger between top node i and deck node i."""
    return 2 * n_cable_nodes + i + 1


def cable_xy(i: int) -> tuple:
    """Coordinates of top-cable node i: x = i * dx, y = tower_top - arc_depth * sin(pi x / span)."""
    dx = span / (n_cable_nodes - 1)
    x = i * dx
    return x, tower_top - arc_depth * np.sin(np.pi * x / span)


def deck_xy(i: int) -> tuple:
    """Coordinates of deck node i, on the x axis below the cable node."""
    dx = span / (n_cable_nodes - 1)
    return i * dx, 0.0


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Start a fresh 2D model with three DOFs per node (ux, uy, rotation)."""
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """One elastic material for the cables, hangers and deck (source LINEAR = True branch)."""
    ops.uniaxialMaterial("Elastic", MAT_CABLE, E_cable)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    """No fibre sections: the deck beam uses the area and inertia passed to elasticBeamColumn."""
    pass


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Top-cable and deck nodes, with the lumped deck masses in x and y (no rotational mass, as in the source)."""
    for i in range(n_cable_nodes):
        ops.node(top_node(i), *cable_xy(i))
    for i in range(n_cable_nodes):
        ops.node(deck_node(i), *deck_xy(i))
        ops.mass(deck_node(i), mass_node, mass_node, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Supports pinned in x and y. Rotation is fixed at the top-cable nodes, which have no bending stiffness.

    The deck supports leave the rotation free. Without these fixes the top-cable rotations would have no stiffness.
    """
    ops.fix(top_node(0), 1, 1, 1)
    ops.fix(top_node(n_cable_nodes - 1), 1, 1, 1)
    for i in range(1, n_cable_nodes - 1):
        ops.fix(top_node(i), 0, 0, 1)
    ops.fix(deck_node(0), 1, 1, 0)
    ops.fix(deck_node(n_cable_nodes - 1), 1, 1, 0)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Top cable and hangers as corotTruss; deck as corotational elasticBeamColumn (the source uses corotTruss).

    The deck beam keeps the source's axial area and adds the bending inertia I_deck.
    """
    ops.geomTransf("Corotational", TRANSF_DECK)
    for i in range(n_cable_nodes - 1):
        ops.element("corotTruss", top_element(i), top_node(i), top_node(i + 1), A_top, MAT_CABLE)
    for i in range(n_cable_nodes - 1):
        ops.element("elasticBeamColumn", deck_element(i), deck_node(i), deck_node(i + 1),
                    A_deck, E_cable, I_deck, TRANSF_DECK)
    for i in range(n_cable_nodes):
        ops.element("corotTruss", hanger_element(i), top_node(i), deck_node(i), A_hanger, MAT_CABLE)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(odb_tag) -> "opst.post.CreateODB":
    """Nodal responses for one load case. The model is saved here, right after the elements are defined.

    Args:
        odb_tag: Tag of this load case (one ODB per analysis, because each analysis rebuilds the model).

    Returns:
        The CreateODB instance.
    """
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_static_load() -> None:
    """Unit load of -1 N at the control node (source: load(mid_node, 0, -1), a vertical load).

    The source comment says "horizontal", but the load is vertical and the control DOF is y.
    """
    ops.timeSeries("Linear", TS_STATIC)
    ops.pattern("Plain", PAT_STATIC, TS_STATIC)
    ops.load(control_node(), 0.0, -1.0 * N, 0.0)


def define_ground_motion(gm_file: Path) -> None:
    """Vertical ground acceleration (record Y, in g, scaled by gm_factor), applied in DOF 2 (source SEI = 'Y')."""
    ops.timeSeries("Path", TS_GROUND, "-dt", dt, "-filePath", str(gm_file), "-factor", gm_factor)
    ops.pattern("UniformExcitation", PAT_GROUND, 2, "-accel", TS_GROUND, "-vel0", iv0_y, "-fact", ssf_y)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def build_model(odb_tag, output_dir: Path = None):
    """Build the model and, when odb_tag is given, its ODB. The V1 and V2 stages are written when output_dir is given.

    Returns:
        The CreateODB instance, or None when odb_tag is None.
    """
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    if output_dir is not None:
        vis_nodes(output_dir)                      # V1: nodes and supports
    define_elements()
    if output_dir is not None:
        vis_model(output_dir)                      # V2: geometry
    return None if odb_tag is None else create_odb(odb_tag)


def support_reactions() -> tuple:
    """Sum of the x and y reactions at the four supports for the current state."""
    ops.reactions()
    rx = sum(ops.nodeReaction(n)[0] for n in support_nodes())
    ry = sum(ops.nodeReaction(n)[1] for n in support_nodes())
    return rx, ry


def run_pushover(output_dir: Path, target=max_disp, step=abs(disp_incr)) -> tuple:
    """Downward displacement control at the control node (source PUSHOVER_ANALYSIS), as a raw solver loop.

    This is the one exception to AGENT.md §3c for this model, approved by the user in chat on 2026-11-20.
    SmartAnalyze stopped this pushover at step 16,881 (LESSON 53), while a raw loop with the same test,
    algorithm and increment reaches the target. The source's fall-back ladder (ANALYSIS_FUNCTION.py) is not
    reproduced: it was not triggered in the 250,000 steps, and a failed step stops the loop and is reported.

    Returns:
        (odb, history): the ODB and the per-step arrays (load factor, control displacement, support reactions).
    """
    odb = build_model(ODB_PUSH, output_dir)
    define_static_load()
    vis_loads(output_dir)                          # V3: load vectors
    vis_pre_analysis(output_dir)                   # V4: last check before the solver
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", pushover_tol, pushover_iter)
    ops.algorithm("ModifiedNewton")                # set once, as in the source
    increment = float(np.sign(target)) * step      # signed increment (source disp_incr = -0.01 mm)
    n_steps = int(round(abs(target / step)))       # 250000 steps for the source protocol
    ops.integrator("DisplacementControl", control_node(), 2, increment)
    ops.analysis("Static")
    history = {"lam": [], "ctrl_x": [], "ctrl_y": [], "rx": [], "ry": []}
    for k in range(1, n_steps + 1):
        ok = ops.analyze(1)
        if ok < 0:
            print(f"pushover stopped: step {k} failed, control node y = {ops.nodeDisp(control_node(), 2):.3f} mm")
            break
        if k % odb_every_pushover == 0:
            odb.fetch_response_step()
        rx, ry = support_reactions()
        history["lam"].append(ops.getTime())
        history["ctrl_x"].append(ops.nodeDisp(control_node(), 1))
        history["ctrl_y"].append(ops.nodeDisp(control_node(), 2))
        history["rx"].append(rx)
        history["ry"].append(ry)
    return odb, {key: np.array(value) for key, value in history.items()}


def rayleigh_coefficients(zeta_i: float, zeta_j: float) -> tuple:
    """Rayleigh alpha (mass) and beta (committed stiffness) for modes 1 and 2 (source RAYLEIGH_DAMPING).

    Solves [1/w_i, w_i; 1/w_j, w_j] [alpha, beta] = [2 zeta_i, 2 zeta_j] and applies ops.rayleigh(alpha, 0, 0, beta).
    Requires the constraints, numberer and system to be set before the call.

    Returns:
        (alpha, beta, period_1, period_2) with the periods in s.
    """
    lam = ops.eigen("-genBandArpack", 2)
    w_i, w_j = np.sqrt(lam[0]), np.sqrt(lam[1])
    mat = np.array([[1.0 / w_i, w_i], [1.0 / w_j, w_j]])
    alpha, beta = np.linalg.solve(mat, np.array([2.0 * zeta_i, 2.0 * zeta_j]))
    ops.rayleigh(alpha, 0.0, 0.0, beta)
    return alpha, beta, 2.0 * np.pi / w_i, 2.0 * np.pi / w_j


def run_free_vibration(damped: bool, output_dir: Path, n_steps: int = n_transient) -> tuple:
    """Static deck displacement of u0, release, then Newmark free vibration (source FREE_VIBRATION_ANALYSIS).

    Returns:
        (odb, history, info): history holds the control-node response per step; info holds the Rayleigh data.
    """
    tag = ODB_FREE_DAMPED if damped else ODB_FREE_UNDAMPED
    odb = build_model(tag)
    define_static_load()
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    static = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="EnergyIncr",
        testTol=transient_tol,
        testIterTimes=transient_iter,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 40, 20, 30],
        printPer=0,
        testPrintFlag=0,
    )
    for seg in static.static_split([u0], maxStep=u0):
        ok = static.StaticAnalyze(node=control_node(), dof=2, seg=seg)
        if ok < 0:
            raise RuntimeError("initial deck displacement did not converge")
        odb.fetch_response_step()
    static.close()
    ops.setTime(0.0)
    ops.wipeAnalysis()
    ops.remove("loadPattern", PAT_STATIC)          # the deck is released
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("UmfPack")
    info = {"u_initial": ops.nodeDisp(control_node(), 2)}
    if damped:
        alpha, beta, t1, t2 = rayleigh_coefficients(damping_ratio, damping_ratio_2)
        info.update({"alpha": alpha, "beta": beta, "period_1": t1, "period_2": t2})
    ops.integrator("Newmark", 0.5, 0.25)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="EnergyIncr",
        testTol=transient_tol,
        testIterTimes=transient_iter,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 40, 20, 30, 50],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6 * sec,
        printPer=0,
        testPrintFlag=0,
    )
    rows = []
    for k in analysis.transient_split(n_steps):
        ok = analysis.TransientAnalyze(dt)
        if ok < 0:
            break
        if k % odb_every_transient == 0:
            odb.fetch_response_step()
        rx, ry = support_reactions()
        rows.append([ops.getTime(), ops.nodeDisp(control_node(), 1), ops.nodeDisp(control_node(), 2),
                     ops.nodeVel(control_node(), 2), ops.nodeAccel(control_node(), 2), rx, ry])
    analysis.close()
    table = np.array(rows, dtype=float)
    history = {"time": table[:, 0], "ctrl_x": table[:, 1], "ctrl_y": table[:, 2],
               "vel_y": table[:, 3], "acc_y": table[:, 4], "rx": table[:, 5], "ry": table[:, 6]}
    return odb, history, info


def run_dynamic(gm_file: Path, n_steps: int = n_transient) -> tuple:
    """Vertical ground motion through HHT (alpha = 1, i.e. Newmark 0.5, 0.25) and SmartAnalyze (source DYNAMIC_ANALYSIS).

    The source runs this twice: once with Rayleigh damping requested and once without. Rayleigh is applied
    only when periodTF is True, and the source sets it False in both runs, so the two runs are the same.
    The period of each step is taken from a default eigen solve, as the source does with fullGenLapack.

    Returns:
        (odb, history): per-step control-node response, support reactions and the first two periods.
    """
    odb = build_model(ODB_DYNAMIC)
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("UmfPack")
    alpha = 1.0
    gamma = 1.5 - alpha
    beta = (2.0 - alpha) ** 2 / 4.0               # source HHT parameters
    ops.integrator("HHT", alpha, gamma, beta)
    define_ground_motion(gm_file)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="EnergyIncr",
        testTol=transient_tol,
        testIterTimes=transient_iter,
        tryAlterAlgoTypes=True,
        algoTypes=[30, 10, 40, 20],               # ModifiedNewton first, as in the source
        printPer=0,
        testPrintFlag=0,
    )
    rows = []
    for k in analysis.transient_split(n_steps):
        ok = analysis.TransientAnalyze(dt)
        if ok < 0:
            break
        if k % odb_every_transient == 0:
            odb.fetch_response_step()
        rx, ry = support_reactions()
        lam = ops.eigen(2)
        periods = [2.0 * np.pi / np.sqrt(v) for v in lam]
        rows.append([ops.getTime(), ops.nodeDisp(control_node(), 1), ops.nodeDisp(control_node(), 2),
                     ops.nodeVel(control_node(), 2), ops.nodeAccel(control_node(), 2), rx, ry,
                     min(periods), max(periods)])
    analysis.close()
    table = np.array(rows, dtype=float)
    history = {"time": table[:, 0], "ctrl_x": table[:, 1], "ctrl_y": table[:, 2], "vel_y": table[:, 3],
               "acc_y": table[:, 4], "rx": table[:, 5], "ry": table[:, 6],
               "period_min": table[:, 7], "period_max": table[:, 8]}
    return odb, history


def run_initial_periods(output_dir: Path) -> np.ndarray:
    """First four periods of the undeformed model (default eigen solver). No ODB is created here."""
    build_model(None, output_dir)
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    lam = ops.eigen(4)
    return np.array([2.0 * np.pi / np.sqrt(v) for v in lam])


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def damping_ratio_logdec(signal) -> float:
    """Damping ratio in percent from the logarithmic decrement of the peaks (source DAMPING_RATIO).

    The source solves x^2 - 1 + (2 pi x / mean(delta))^2 = 0 with fsolve. The root is x = dbar / sqrt(dbar^2 + 4 pi^2),
    which is used here directly. Returns 0.0 when there are fewer than two peaks or any peak is not positive.
    """
    x = np.asarray(signal, dtype=float)
    peaks = np.array([x[i] for i in range(1, len(x) - 1) if x[i] > x[i - 1] and x[i] > x[i + 1]])
    if len(peaks) < 2 or np.any(peaks <= 0):
        return 0.0
    delta = np.log(peaks[:-1] / peaks[1:])
    delta = delta[np.isfinite(delta)]
    if len(delta) == 0:
        return 0.0
    dbar = np.mean(delta)
    return 100.0 * dbar / np.sqrt(dbar**2 + 4.0 * np.pi**2)


def save_csv(output_dir: Path, name: str, columns: dict) -> None:
    """Write named columns to CSV (N, mm, s)."""
    table = np.column_stack([columns[key] for key in columns])
    np.savetxt(output_dir / name, table, delimiter=",", header=",".join(columns), comments="")


def plot_figures(output_dir: Path, push: dict, free_u: dict, free_d: dict, dyn: dict) -> None:
    """Three PNG figures: the pushover curve and deformed shape data, the free vibration, and the seismic response."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    ax.plot(-push["ctrl_y"] / mm, -push["ry"] / kN, color=COLORS["primary"], lw=1.8)
    _style_ax(ax, "Downward displacement of control node (mm)", "Support reaction, vertical (kN)", "Pushover: reaction vs displacement")
    fig.tight_layout()
    fig.savefig(output_dir / "pushover_curve.png")
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), dpi=150)
    axes[0].plot(free_u["time"], free_u["ctrl_y"] / mm, color=COLORS["primary"], lw=1.2, label="undamped")
    axes[0].plot(free_d["time"], free_d["ctrl_y"] / mm, color=COLORS["secondary"], lw=1.2, label="Rayleigh (beam deck only)")
    _style_ax(axes[0], "Time (s)", "Control node y (mm)", "Free vibration")
    axes[0].legend()
    axes[1].plot(free_u["time"], free_u["ry"] / kN, color=COLORS["primary"], lw=1.2)
    axes[1].plot(free_d["time"], free_d["ry"] / kN, color=COLORS["secondary"], lw=1.2)
    _style_ax(axes[1], "Time (s)", "Support reaction, vertical (kN)", "Free vibration reactions")
    fig.tight_layout()
    fig.savefig(output_dir / "free_vibration.png")
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), dpi=150)
    axes[0].plot(dyn["time"], dyn["ctrl_y"] / mm, color=COLORS["primary"], lw=1.0)
    _style_ax(axes[0], "Time (s)", "Control node y (mm)", "Seismic response (ground motion Y)")
    axes[1].plot(dyn["time"], dyn["ry"] / kN, color=COLORS["primary"], lw=1.0)
    _style_ax(axes[1], "Time (s)", "Support reaction, vertical (kN)", "Seismic support reaction")
    fig.tight_layout()
    fig.savefig(output_dir / "dynamic.png")
    plt.close(fig)


def validate(output_dir: Path, push: dict, free_u: dict, free_d: dict, dyn: dict, info_u: dict, info_d: dict,
             periods_os: np.ndarray, gm_file: Path) -> None:
    """Compare the OpenSees run with independent numpy calculations and write validation.txt.

    Checks: first periods of the undeformed model; initial stiffness; pushover equilibrium (vertical and horizontal
    reactions); free vibration (undamped and damped) against a linear numpy Newmark run; seismic response against the
    same linear run; and the damping ratio estimates. No value is tuned to the source figure.
    """
    import scipy.linalg as sla

    report = []
    K, Kd, M, free = linear_matrices()
    # 1. periods (free DOFs with no mass give infinite eigenvalues, which are dropped)
    lam_np = np.sort(np.real(sla.eig(K[np.ix_(free, free)], M[np.ix_(free, free)])[0]))
    lam_np = lam_np[np.isfinite(lam_np) & (lam_np > 1e-12)]
    t_np = 2.0 * np.pi / np.sqrt(lam_np[:4])
    report.append("periods (s), OpenSees: " + ", ".join(f"{t:.6f}" for t in periods_os))
    report.append("periods (s), numpy:    " + ", ".join(f"{t:.6f}" for t in t_np))
    # 2. static stiffness: first pushover step against the linear solve
    f = np.zeros(K.shape[0])
    f[3 * (control_node() - 1) + 1] = -1.0
    u_unit = np.zeros(K.shape[0])
    u_unit[free] = np.linalg.solve(K[np.ix_(free, free)], f[free])
    lam_pred = push["ctrl_y"][0] / u_unit[3 * (control_node() - 1) + 1]
    report.append(f"first pushover step: load factor OpenSees {push['lam'][0]:.6e}, linear numpy {lam_pred:.6e} "
                  f"(relative difference {abs(push['lam'][0] / lam_pred - 1.0):.2e})")
    # 3. equilibrium of the pushover: vertical sum equals the load factor, horizontal sum is zero
    lam_all = push["lam"]
    rel_v = np.max(np.abs(push["ry"] - lam_all)) / np.max(np.abs(lam_all))
    rel_h = np.max(np.abs(push["rx"])) / np.max(np.abs(lam_all))
    report.append(f"pushover equilibrium over {len(lam_all)} steps: max |sum Ry - lambda| / max lambda = {rel_v:.2e}; "
                  f"max |sum Rx| / max lambda = {rel_h:.2e}")
    # 4. free vibration against a linear numpy Newmark run (zero start acceleration, as OpenSees).
    # The initial state is the linear static state with the control node at +u0.
    dofc = 3 * (control_node() - 1) + 1
    lam_u = u0 / u_unit[dofc]
    u_static = np.zeros(K.shape[0])
    u_static[free] = lam_u * u_unit[free]
    for label, res, info in (("undamped", free_u, info_u),
                             ("damped (Rayleigh; stiffness term acts on the deck beams only)", free_d, info_d)):
        if label == "undamped":
            C = np.zeros_like(M)
        else:
            C = info["alpha"] * M + info["beta"] * Kd
        ff = np.array(free)
        Mf, Cf, Kf = M[np.ix_(ff, ff)], C[np.ix_(ff, ff)], K[np.ix_(ff, ff)]
        u = u_static[ff].copy()
        v = np.zeros(len(ff))
        a = np.zeros(len(ff))
        g, b = 0.5, 0.25
        eff = Mf + g * dt * Cf + b * dt**2 * Kf
        mid_idx = list(ff).index(dofc)
        err = 0.0
        for k in range(len(res["time"])):
            up = u + dt * v + dt**2 * (0.5 - b) * a
            vp = v + dt * (1 - g) * a
            a = np.linalg.solve(eff, -(Cf @ vp + Kf @ up))
            u = up + b * dt**2 * a
            v = vp + g * dt * a
            err = max(err, abs(u[mid_idx] - res["ctrl_y"][k]))
        report.append(f"free vibration {label}: max |control-node y, OpenSees - numpy linear| = {err:.3e} mm "
                      f"(initial {u0 / mm:.1f} mm)")
    # 5. seismic response against a linear numpy run with the same ground motion
    rec = np.loadtxt(gm_file) * 9810.0
    rec = np.concatenate([rec, np.zeros(max(0, n_transient + 1 - len(rec)))])
    ff = np.array(free)
    Mf, Cf, Kf = M[np.ix_(ff, ff)], np.zeros((len(ff), len(ff))), K[np.ix_(ff, ff)]
    r = np.zeros(len(ff))
    for j, d in enumerate(ff):
        if d % 3 == 1:                       # DOF 2 of each node carries the excitation
            r[j] = 1.0
    u = np.zeros(len(ff))
    v = np.zeros(len(ff))
    a = np.zeros(len(ff))
    g, b = 0.5, 0.25
    eff = Mf + g * dt * Cf + b * dt**2 * Kf
    mid_idx = list(ff).index(dofc)
    err = 0.0
    scale = np.max(np.abs(dyn["ctrl_y"])) if np.max(np.abs(dyn["ctrl_y"])) > 0 else 1.0
    for k in range(len(dyn["time"])):
        ag_next = rec[k + 1] if k + 1 < len(rec) else 0.0
        F = -(Mf @ r) * ag_next
        up = u + dt * v + dt**2 * (0.5 - b) * a
        vp = v + dt * (1 - g) * a
        a = np.linalg.solve(eff, F - (Cf @ vp + Kf @ up))
        u = up + b * dt**2 * a
        v = vp + g * dt * a
        err = max(err, abs(u[mid_idx] - dyn["ctrl_y"][k]))
    report.append(f"seismic (ground motion Y): max |control-node y, OpenSees - numpy linear| = {err:.3e} mm "
                  f"(peak OpenSees {scale:.3e} mm)")
    # 6. damping estimates
    report.append(f"damping ratio from log decrement (%): undamped x = {damping_ratio_logdec(free_u['ctrl_x']):.4f}, "
                  f"damped x = {damping_ratio_logdec(free_d['ctrl_x']):.4f}, undamped y = {damping_ratio_logdec(free_u['ctrl_y']):.4f}")
    (output_dir / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report:
        print(line)


def linear_matrices() -> tuple:
    """Linear stiffness (all elements), deck-only stiffness, lumped mass and free-DOF list, rebuilt in numpy.

    Truss members give EA/L (c c^T) terms; deck beams give the standard 2D frame matrix (the deck is horizontal).
    """
    ndof = 3 * 2 * n_cable_nodes
    K = np.zeros((ndof, ndof))
    Kd = np.zeros((ndof, ndof))
    M = np.zeros((ndof, ndof))

    def dofs(node):
        return [3 * (node - 1), 3 * (node - 1) + 1, 3 * (node - 1) + 2]

    def truss(ni, nj, ea, target):
        xi, yi = nodes[ni]
        xj, yj = nodes[nj]
        ln = np.hypot(xj - xi, yj - yi)
        c = np.array([(xj - xi) / ln, (yj - yi) / ln])
        bvec = np.concatenate([-c, c])
        d = [3 * (ni - 1), 3 * (ni - 1) + 1, 3 * (nj - 1), 3 * (nj - 1) + 1]
        for p in range(4):
            for q in range(4):
                target[d[p], d[q]] += ea / ln * bvec[p] * bvec[q]

    def beam(ni, nj, ea, ei, target):
        ln = abs(nodes[nj][0] - nodes[ni][0])
        kl = np.array([
            [ea / ln, 0, 0, -ea / ln, 0, 0],
            [0, 12 * ei / ln**3, 6 * ei / ln**2, 0, -12 * ei / ln**3, 6 * ei / ln**2],
            [0, 6 * ei / ln**2, 4 * ei / ln, 0, -6 * ei / ln**2, 2 * ei / ln],
            [-ea / ln, 0, 0, ea / ln, 0, 0],
            [0, -12 * ei / ln**3, -6 * ei / ln**2, 0, 12 * ei / ln**3, -6 * ei / ln**2],
            [0, 6 * ei / ln**2, 2 * ei / ln, 0, -6 * ei / ln**2, 4 * ei / ln],
        ])
        d = dofs(ni) + dofs(nj)
        for p in range(6):
            for q in range(6):
                target[d[p], d[q]] += kl[p, q]

    nodes = {}
    for i in range(n_cable_nodes):
        nodes[top_node(i)] = cable_xy(i)
        nodes[deck_node(i)] = deck_xy(i)
    for i in range(n_cable_nodes - 1):
        truss(top_node(i), top_node(i + 1), E_cable * A_top, K)
        beam(deck_node(i), deck_node(i + 1), E_cable * A_deck, E_cable * I_deck, K)
        beam(deck_node(i), deck_node(i + 1), E_cable * A_deck, E_cable * I_deck, Kd)
    for i in range(n_cable_nodes):
        truss(top_node(i), deck_node(i), E_cable * A_hanger, K)
        M[3 * (deck_node(i) - 1), 3 * (deck_node(i) - 1)] = mass_node
        M[3 * (deck_node(i) - 1) + 1, 3 * (deck_node(i) - 1) + 1] = mass_node
    fixed = []
    fixed += dofs(top_node(0)) + dofs(top_node(n_cable_nodes - 1))
    for i in range(1, n_cable_nodes - 1):
        fixed += [3 * (top_node(i) - 1) + 2]
    fixed += [3 * (deck_node(0) - 1), 3 * (deck_node(0) - 1) + 1]
    fixed += [3 * (deck_node(n_cable_nodes - 1) - 1), 3 * (deck_node(n_cable_nodes - 1) - 1) + 1]
    free = [d for d in range(ndof) if d not in set(fixed)]
    return K, Kd, M, free


def post_process(output_dir: Path, odbs: dict, push, free_u, free_d, dyn, periods_os: np.ndarray) -> None:
    """Write the CSV files, figures, interactive views and validation, and flush the ODBs."""
    for odb in odbs.values():
        odb.save_response()
    save_csv(output_dir, "pushover_history.csv", {"load_factor": push["lam"], "ctrl_x_mm": push["ctrl_x"],
                                                  "ctrl_y_mm": push["ctrl_y"], "rx_N": push["rx"], "ry_N": push["ry"]})
    save_csv(output_dir, "free_undamped_history.csv", {k: free_u[k] for k in ("time", "ctrl_x", "ctrl_y", "vel_y", "acc_y", "rx", "ry")})
    save_csv(output_dir, "free_damped_history.csv", {k: free_d[k] for k in ("time", "ctrl_x", "ctrl_y", "vel_y", "acc_y", "rx", "ry")})
    save_csv(output_dir, "dynamic_history.csv", {k: dyn[k] for k in ("time", "ctrl_x", "ctrl_y", "vel_y", "acc_y", "rx", "ry", "period_min", "period_max")})
    np.savetxt(output_dir / "initial_periods.txt", periods_os, header="first four periods of the undeformed model (s)")
    plot_figures(output_dir, push, free_u, free_d, dyn)
    vis_curves(output_dir, [
        {"x": -push["ctrl_y"] / mm, "y": -push["ry"] / kN, "xlabel": "Downward displacement of control node (mm)",
         "ylabel": "Support reaction, vertical (kN)", "title": "Pushover"},
    ], filename="vis_08_pushover.html", title="Pushover: reaction vs displacement")
    t = dyn["time"]
    vis_curves(output_dir, [
        {"x": t, "y": dyn["ctrl_y"] / mm, "xlabel": "Time (s)", "ylabel": "Control node y (mm)", "title": "Displacement"},
        {"x": t, "y": dyn["vel_y"], "xlabel": "Time (s)", "ylabel": "Velocity (mm/s)", "title": "Velocity"},
        {"x": t, "y": dyn["acc_y"], "xlabel": "Time (s)", "ylabel": "Acceleration (mm/s^2)", "title": "Acceleration"},
        {"x": t, "y": dyn["ry"] / kN, "xlabel": "Time (s)", "ylabel": "Support reaction, vertical (kN)", "title": "Reaction"},
    ], filename="vis_09_dynamic.html", title="Seismic response (ground motion Y)")
    if "pushover" in odbs:
        vis_defo(output_dir, filename="vis_05_deformed_pushover.html", odb_tag=ODB_PUSH,
                 resp_dof="UY", resp_type="disp", scale=1.0)


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))        # before any CreateODB (AGENT.md §12ac)
    gm_file = Path(__file__).parent / "ground_motions" / "Ground_Acceleration_Y.txt"
    periods_os = run_initial_periods(output_dir)
    odb_push, push = run_pushover(output_dir)
    odb_fu, free_u, info_u = run_free_vibration(False, output_dir)
    odb_fd, free_d, info_d = run_free_vibration(True, output_dir)
    odb_dyn, dyn = run_dynamic(gm_file)
    post_process(output_dir, {"pushover": odb_push, "free_undamped": odb_fu, "free_damped": odb_fd, "dynamic": odb_dyn},
                 push, free_u, free_d, dyn, periods_os)
    validate(output_dir, push, free_u, free_d, dyn, info_u, info_d, periods_os, gm_file)
