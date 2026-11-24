# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D single-cable suspension foot bridge chain (sub-model 03, span 18 m, sag 0.5 m). The source's 50 truss members
           are converted to corotational elastic beams with bending stiffness added, so that the chain is stable (see README).
UniqueID : SalarDelavar_Cable_Suspension_Foot_Bridge_03
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-24
Purpose  : Vertical pushover of the midspan node, free vibration after a static midspan displacement (undamped and
           Rayleigh-damped), and the response to two ground motions (X and Y).
Ref      : py_ref/OPENSEES_CABLE_SUSPENSION_BRIDGE_03.py (source), py_ref/README_FOOT_BRIDGE.md, and py_ref/PLOT_2D_TRUSS.py
           (source plotting helper, not used). Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CABLE_SUSPENSION_FOOT_BRIDGE/CABLE_STRUCTURE_03
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
ODB_PUSH = "pushover"
ODB_FREE_UNDAMPED = "free_undamped"
ODB_FREE_DAMPED = "free_damped"
ODB_DYN_UNDAMPED = "dynamic_undamped"
ODB_DYN_DAMPED = "dynamic_damped"
TRANSF_BEAM = 1         # corotational transformation for the chain members
TS_STATIC = 1           # unit load: pushover and the initial midspan displacement
PAT_STATIC = 1
TS_GROUND_X = 1         # horizontal ground acceleration (source time series and pattern 1)
PAT_GROUND_X = 1
TS_GROUND_Y = 2         # vertical ground acceleration (source time series and pattern 2)
PAT_GROUND_Y = 2

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
n_nodes = 51                                       # source num_nodes
span = 18000.0 * mm                                # source L
top_height = 500.0 * mm                            # source H1: height of the chain ends
arc_depth = 500.0 * mm                             # source arc_depth: the midspan node is at H1 - arc_depth = 0
E_cable = 210e5 * MPa                              # 210e5 N/mm^2 as written in the source (100x structural steel)
dia_cable = 32.0 * mm                              # source Cable_Dia_01: diameter of one cable
n_cables = 10                                      # source N_cable: the source's element area is ten cables
A_section = n_cables * np.pi * dia_cable**2 / 4    # source element area, N_cable * A_cable_01 (8042.5 mm^2)
D_section = np.sqrt(4.0 * A_section / np.pi)       # diameter of the solid circle with the same area (ADDED; see README)
I_section = np.pi * D_section**4 / 64.0            # ADDED bending inertia (not in the source; see README)
total_mass = 5.0e4 * N * sec**2 / mm               # source TOTAL_MASS = 50000, labelled kg but used as N.s^2/mm (see README)
mass_node = total_mass / n_nodes                   # lumped at each node, in x and y (source MASS)
max_disp = -50.0 * mm                              # pushover target, downward (source MAX_DISP)
disp_incr = -0.01 * mm                             # pushover increment (source disp_incr): 5000 steps
pushover_tol = 1.0e-10                             # source MAX_TOLERANCE for the pushover
pushover_iter = 50000                              # source MAX_ITERATIONS for the pushover
u0 = 0.1 * mm                                      # initial midspan displacement, upward (source u0)
damping_ratio = 0.05                               # source damping_ratio
rayleigh_reference_free = 1.0 * N / mm             # source KE = 1 in the free-vibration run (an assumed stiffness)
rayleigh_reference_dyn = 1000.0 * N / mm           # source KE = 1000 in the dynamic run (an assumed stiffness)
duration = 50.0 * sec                              # analysis length (source)
dt = 0.01 * sec                                    # time step (source)
n_transient = int(round(duration / dt))            # 5000 steps
free_tol = 1.0e-10                                 # source MAX_TOLERANCE for the free-vibration run
free_iter = 10000                                  # source MAX_ITERATIONS for the free-vibration run
dyn_tol = 1.0e-6                                   # source MAX_TOLERANCE for the dynamic run (differs from the free run)
dyn_iter = 10000                                   # source MAX_ITERATIONS for the dynamic run
hht_alpha = 0.9                                    # source ops.integrator('HHT', 0.9), single argument as written
gm_factor = 1.0 * mm / sec**2                      # source GMfact = 1: the records are used as they are (mm/s^2)
ssf = 1.0                                          # source scale factor of the excitation patterns
iv0 = 0.0 * mm / sec                               # source iv0 = 0.0 (initial velocity)
st_iv0 = 0.0 * sec                                 # source st_iv0 = 0.0 (start time of the X record)
odb_every_pushover = 50                            # 100 ODB fetches over 5000 steps (AGENT.md §3d)
odb_every_transient = 10                           # 500 fetches over 5000 steps


# Tag helpers (source numbering, 1-based): nodes 1..51 along the chain, members 1..50.
def node_tag(i: int) -> int:
    """Tag of chain node i (0-based)."""
    return i + 1


def element_tag(i: int) -> int:
    """Tag of the member between chain nodes i and i+1 (0-based)."""
    return i + 1


def control_node() -> int:
    """Source mid_node = num_nodes // 2 + 1 = 26: the midspan node (x = 9 m, y = 0)."""
    return n_nodes // 2 + 1


def support_nodes() -> list:
    """Tags of the two supports: the chain ends, pinned in x and y."""
    return [node_tag(0), node_tag(n_nodes - 1)]


def chain_xy(i: int) -> tuple:
    """Coordinates of chain node i: x = i * dx, y = H1 - arc_depth * sin(pi x / L) (source Y1)."""
    dx = span / (n_nodes - 1)
    x = i * dx
    return x, top_height - arc_depth * np.sin(np.pi * x / span)


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Start a fresh 2D model with three DOFs per node (ux, uy, rotation): the chain members are beams."""
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)


# ── 5. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Chain nodes with the lumped mass in x and y at every node (no rotational mass, as in the source)."""
    for i in range(n_nodes):
        ops.node(node_tag(i), *chain_xy(i))
        ops.mass(node_tag(i), mass_node, mass_node, 0.0)


# ── 6. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Both ends pinned in x and y (source ops.fix(1, 1, 1) and ops.fix(num_nodes, 1, 1) with two DOFs).

    The end rotations are left free, as for a pin. The source truss has no rotation DOF to fix.
    """
    ops.fix(node_tag(0), 1, 1, 0)
    ops.fix(node_tag(n_nodes - 1), 1, 1, 0)


# ── 7. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Chain members as corotational elasticBeamColumn (the source uses corotTruss).

    The member keeps the source's element area (ten cables) and adds the bending inertia I_section (see README).
    """
    ops.geomTransf("Corotational", TRANSF_BEAM)
    for i in range(n_nodes - 1):
        ops.element("elasticBeamColumn", element_tag(i), node_tag(i), node_tag(i + 1),
                    A_section, E_cable, I_section, TRANSF_BEAM)


# ── 8. OUTPUT DATABASE (ODB) ─────────────────────────────────────────────────
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


# ── 9. LOADING ───────────────────────────────────────────────────────────────
def define_static_load() -> None:
    """Unit load of -1 N at the control node (source: load(mid_node, 0, -1), a vertical load)."""
    ops.timeSeries("Linear", TS_STATIC)
    ops.pattern("Plain", PAT_STATIC, TS_STATIC)
    ops.load(control_node(), 0.0, -1.0 * N, 0.0)


def define_ground_motions(gm_x: Path, gm_y: Path) -> None:
    """Both ground accelerations, as the source defines them: X in DOF 1 (pattern 1) and Y in DOF 2 (pattern 2)."""
    ops.timeSeries("Path", TS_GROUND_X, "-dt", dt, "-filePath", str(gm_x), "-factor", gm_factor, "-startTime", st_iv0)
    ops.pattern("UniformExcitation", PAT_GROUND_X, 1, "-accel", TS_GROUND_X, "-vel0", iv0, "-fact", ssf)
    ops.timeSeries("Path", TS_GROUND_Y, "-dt", dt, "-filePath", str(gm_y), "-factor", gm_factor)
    ops.pattern("UniformExcitation", PAT_GROUND_Y, 2, "-accel", TS_GROUND_Y, "-vel0", iv0, "-fact", ssf)


# ── 10. ANALYSIS ─────────────────────────────────────────────────────────────
def build_model(odb_tag, output_dir: Path = None):
    """Build the model and, when odb_tag is given, its ODB. The V1 and V2 stages are written when output_dir is given.

    Returns:
        The CreateODB instance, or None when odb_tag is None.
    """
    init_model()
    define_nodes()
    define_boundary_conditions()
    if output_dir is not None:
        vis_nodes(output_dir)                      # V1: nodes and supports
    define_elements()
    if output_dir is not None:
        vis_model(output_dir)                      # V2: geometry
    return None if odb_tag is None else create_odb(odb_tag)


def support_reactions() -> tuple:
    """Sum of the x and y reactions at the two supports for the current state."""
    ops.reactions()
    rx = sum(ops.nodeReaction(n)[0] for n in support_nodes())
    ry = sum(ops.nodeReaction(n)[1] for n in support_nodes())
    return rx, ry


def run_pushover(output_dir: Path, target=max_disp, step=abs(disp_incr)) -> tuple:
    """Downward displacement control at the midspan node, through SmartAnalyze (source PUSHOVER_ANALYSIS).

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
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="EnergyIncr",
        testTol=pushover_tol,
        testIterTimes=pushover_iter,
        tryAlterAlgoTypes=True,
        algoTypes=[30, 10, 40, 20],                # ModifiedNewton first, as in the source
        printPer=0,
        testPrintFlag=0,
    )
    history = {"lam": [], "ctrl_x": [], "ctrl_y": [], "rx": [], "ry": []}
    segs = analysis.static_split([target], maxStep=step)
    for k, seg in enumerate(segs):
        ok = analysis.StaticAnalyze(node=control_node(), dof=2, seg=seg)
        if ok < 0:
            break
        if k % odb_every_pushover == 0:
            odb.fetch_response_step()
        rx, ry = support_reactions()
        history["lam"].append(ops.getTime())
        history["ctrl_x"].append(ops.nodeDisp(control_node(), 1))
        history["ctrl_y"].append(ops.nodeDisp(control_node(), 2))
        history["rx"].append(rx)
        history["ry"].append(ry)
    analysis.close()
    return odb, {key: np.array(value) for key, value in history.items()}


def rayleigh_assumed(zeta: float, reference_stiffness: float, total_mass: float) -> tuple:
    """Rayleigh coefficients from the source's assumed frequency, not from the modes.

    The source sets omega1 = sqrt(K_ref / total_mass) and omega2 = 2 omega1, then
    alpha = zeta * 2 w1 w2 / (w1 + w2) and beta = 2 zeta / (w1 + w2). ops.rayleigh(alpha, beta, 0, 0).

    Returns:
        (alpha, beta, omega1, omega2).
    """
    w1 = np.sqrt(reference_stiffness / total_mass)
    w2 = 2.0 * w1
    alpha = zeta * 2.0 * w1 * w2 / (w1 + w2)
    beta = 2.0 * zeta / (w1 + w2)
    return alpha, beta, w1, w2


def run_free_vibration(damped: bool, output_dir: Path, n_steps: int = n_transient) -> tuple:
    """Static midspan displacement of u0, release, then Newmark free vibration (source FREE_VIBRATION_ANALYSIS).

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
        testTol=free_tol,
        testIterTimes=free_iter,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 40, 20, 30],
        printPer=0,
        testPrintFlag=0,
    )
    for seg in static.static_split([u0], maxStep=u0):
        ok = static.StaticAnalyze(node=control_node(), dof=2, seg=seg)
        if ok < 0:
            raise RuntimeError("initial midspan displacement did not converge")
        odb.fetch_response_step()
    static.close()
    ops.setTime(0.0)
    ops.wipeAnalysis()
    ops.remove("loadPattern", PAT_STATIC)          # the chain is released
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("UmfPack")
    info = {"u_initial": ops.nodeDisp(control_node(), 2)}
    if damped:
        alpha, beta, w1, w2 = rayleigh_assumed(damping_ratio, rayleigh_reference_free, total_mass)
        ops.rayleigh(alpha, beta, 0.0, 0.0)
        info.update({"alpha": alpha, "beta": beta, "omega1": w1, "omega2": w2})
    ops.integrator("Newmark", 0.5, 0.25)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="EnergyIncr",
        testTol=free_tol,
        testIterTimes=free_iter,
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


def run_dynamic(damped: bool, gm_x: Path, gm_y: Path, n_steps: int = n_transient) -> tuple:
    """Both ground motions through HHT (single argument alpha = 0.9, as in the source) and SmartAnalyze.

    The damped run adds the source's assumed Rayleigh damping with K_ref = 1000 N/mm (the source's dynamic KE).

    Returns:
        (odb, history, info).
    """
    tag = ODB_DYN_DAMPED if damped else ODB_DYN_UNDAMPED
    odb = build_model(tag)
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("UmfPack")
    info = {}
    if damped:
        alpha, beta, w1, w2 = rayleigh_assumed(damping_ratio, rayleigh_reference_dyn, total_mass)
        ops.rayleigh(alpha, beta, 0.0, 0.0)
        info.update({"alpha": alpha, "beta": beta, "omega1": w1, "omega2": w2})
    ops.integrator("HHT", hht_alpha)
    define_ground_motions(gm_x, gm_y)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="EnergyIncr",
        testTol=dyn_tol,
        testIterTimes=dyn_iter,
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
        rows.append([ops.getTime(), ops.nodeDisp(control_node(), 1), ops.nodeDisp(control_node(), 2),
                     ops.nodeVel(control_node(), 2), ops.nodeAccel(control_node(), 2), rx, ry])
    analysis.close()
    table = np.array(rows, dtype=float)
    history = {"time": table[:, 0], "ctrl_x": table[:, 1], "ctrl_y": table[:, 2],
               "vel_y": table[:, 3], "acc_y": table[:, 4], "rx": table[:, 5], "ry": table[:, 6]}
    return odb, history, info


def run_initial_periods(output_dir: Path) -> np.ndarray:
    """First four periods of the undeformed model (default eigen solver). No ODB is created here."""
    build_model(None, output_dir)
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    lam = ops.eigen(4)
    return np.array([2.0 * np.pi / np.sqrt(v) for v in lam])


# ── 11. POST-PROCESSING ──────────────────────────────────────────────────────
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


def plot_figures(output_dir: Path, push: dict, free_u: dict, free_d: dict, dyn_u: dict, dyn_d: dict) -> None:
    """Three PNG figures: the pushover curve, the free vibration, and the seismic response (undamped and damped)."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    ax.plot(-push["ctrl_y"] / mm, -push["ry"] / N, color=COLORS["primary"], lw=1.8)
    _style_ax(ax, "Downward displacement of midspan node (mm)", "Support reaction, vertical (N)", "Pushover: reaction vs displacement")
    fig.tight_layout()
    fig.savefig(output_dir / "pushover_curve.png")
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), dpi=150)
    axes[0].plot(free_u["time"], free_u["ctrl_y"] / mm, color=COLORS["primary"], lw=1.2, label="undamped")
    axes[0].plot(free_d["time"], free_d["ctrl_y"] / mm, color=COLORS["secondary"], lw=1.2, label="Rayleigh (assumed)")
    _style_ax(axes[0], "Time (s)", "Midspan y (mm)", "Free vibration")
    axes[0].legend()
    axes[1].plot(free_u["time"], free_u["ry"] / N, color=COLORS["primary"], lw=1.2)
    axes[1].plot(free_d["time"], free_d["ry"] / N, color=COLORS["secondary"], lw=1.2)
    _style_ax(axes[1], "Time (s)", "Support reaction, vertical (N)", "Free vibration reactions")
    fig.tight_layout()
    fig.savefig(output_dir / "free_vibration.png")
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), dpi=150)
    axes[0].plot(dyn_u["time"], dyn_u["ctrl_y"] / mm, color=COLORS["primary"], lw=1.0, label="undamped")
    axes[0].plot(dyn_d["time"], dyn_d["ctrl_y"] / mm, color=COLORS["secondary"], lw=1.0, label="Rayleigh (assumed)")
    _style_ax(axes[0], "Time (s)", "Midspan y (mm)", "Seismic response (ground motions X and Y)")
    axes[0].legend()
    axes[1].plot(dyn_u["time"], dyn_u["ctrl_x"] / mm, color=COLORS["primary"], lw=1.0, label="undamped")
    axes[1].plot(dyn_d["time"], dyn_d["ctrl_x"] / mm, color=COLORS["secondary"], lw=1.0, label="Rayleigh (assumed)")
    _style_ax(axes[1], "Time (s)", "Midspan x (mm)", "Seismic response, horizontal")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(output_dir / "dynamic.png")
    plt.close(fig)


def linear_matrices() -> tuple:
    """Linear stiffness K (all members), the stiffness used by the damping term Kd (here equal to K, because every
    member is a beam), the lumped mass M and the free-DOF list, rebuilt in numpy.

    Every member is a 2D beam at its initial orientation, so the general 6x6 transformation is used.
    """
    ndof = 3 * n_nodes
    K = np.zeros((ndof, ndof))
    M = np.zeros((ndof, ndof))

    def dofs(node):
        return [3 * (node - 1), 3 * (node - 1) + 1, 3 * (node - 1) + 2]

    def beam(ni, nj, ea, ei, target):
        xi, yi = nodes[ni]
        xj, yj = nodes[nj]
        ln = np.hypot(xj - xi, yj - yi)
        c, s = (xj - xi) / ln, (yj - yi) / ln
        kl = np.array([
            [ea / ln, 0, 0, -ea / ln, 0, 0],
            [0, 12 * ei / ln**3, 6 * ei / ln**2, 0, -12 * ei / ln**3, 6 * ei / ln**2],
            [0, 6 * ei / ln**2, 4 * ei / ln, 0, -6 * ei / ln**2, 2 * ei / ln],
            [-ea / ln, 0, 0, ea / ln, 0, 0],
            [0, -12 * ei / ln**3, -6 * ei / ln**2, 0, 12 * ei / ln**3, -6 * ei / ln**2],
            [0, 6 * ei / ln**2, 2 * ei / ln, 0, -6 * ei / ln**2, 4 * ei / ln],
        ])
        T = np.array([
            [c, s, 0, 0, 0, 0],
            [-s, c, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, c, s, 0],
            [0, 0, 0, -s, c, 0],
            [0, 0, 0, 0, 0, 1],
        ])
        kg = T.T @ kl @ T                     # global stiffness of a member at any orientation
        d = dofs(ni) + dofs(nj)
        for p in range(6):
            for q in range(6):
                target[d[p], d[q]] += kg[p, q]

    nodes = {node_tag(i): chain_xy(i) for i in range(n_nodes)}
    for i in range(n_nodes - 1):
        beam(node_tag(i), node_tag(i + 1), E_cable * A_section, E_cable * I_section, K)
    for i in range(n_nodes):
        M[3 * (node_tag(i) - 1), 3 * (node_tag(i) - 1)] = mass_node
        M[3 * (node_tag(i) - 1) + 1, 3 * (node_tag(i) - 1) + 1] = mass_node
    fixed = []
    for node in support_nodes():
        fixed += dofs(node)[:2]                # ux and uy; the end rotations are free (pin)
    free = [d for d in range(ndof) if d not in set(fixed)]
    Kd = K.copy()                              # every member carries the Rayleigh stiffness term in this model
    return K, Kd, M, free


def validate(output_dir: Path, push: dict, free_u: dict, free_d: dict, info_u: dict, info_d: dict,
             periods_os: np.ndarray) -> None:
    """Compare the OpenSees run with independent numpy calculations and write validation.txt.

    Checks: first periods of the undeformed model; the first pushover step against a linear solve; the pushover
    equilibrium; the free vibration (undamped and damped, with the same assumed Rayleigh coefficients) against a
    linear numpy Newmark run; and the modal damping ratios implied by the assumed coefficients.
    The dynamic runs use HHT with alpha = 0.9, which is not checked by this numpy run.
    """
    import scipy.linalg as sla

    report = []
    K, Kd, M, free = linear_matrices()
    lam_np = np.sort(np.real(sla.eig(K[np.ix_(free, free)], M[np.ix_(free, free)])[0]))
    lam_np = lam_np[np.isfinite(lam_np) & (lam_np > 1e-12)]
    t_np = 2.0 * np.pi / np.sqrt(lam_np[:4])
    report.append("periods (s), OpenSees: " + ", ".join(f"{t:.6f}" for t in periods_os))
    report.append("periods (s), numpy:    " + ", ".join(f"{t:.6f}" for t in t_np))
    f = np.zeros(K.shape[0])
    dofc = 3 * (control_node() - 1) + 1
    f[dofc] = -1.0
    u_unit = np.zeros(K.shape[0])
    u_unit[free] = np.linalg.solve(K[np.ix_(free, free)], f[free])
    lam_pred = push["ctrl_y"][0] / u_unit[dofc]
    report.append(f"first pushover step: load factor OpenSees {push['lam'][0]:.6e}, linear numpy {lam_pred:.6e} "
                  f"(relative difference {abs(push['lam'][0] / lam_pred - 1.0):.2e})")
    lam_all = push["lam"]
    rel_v = np.max(np.abs(push["ry"] - lam_all)) / np.max(np.abs(lam_all))
    rel_h = np.max(np.abs(push["rx"])) / np.max(np.abs(lam_all))
    report.append(f"pushover equilibrium over {len(lam_all)} steps: max |sum Ry - lambda| / max lambda = {rel_v:.2e}; "
                  f"max |sum Rx| / max lambda = {rel_h:.2e}")
    lam_u = u0 / u_unit[dofc]
    u_static = np.zeros(K.shape[0])
    u_static[free] = lam_u * u_unit[free]
    ff = np.array(free)
    mid_idx = list(ff).index(dofc)
    for label, res, info, damped in (("undamped", free_u, info_u, False),
                                     ("damped (assumed Rayleigh; stiffness term on all members)", free_d, info_d, True)):
        C = (info["alpha"] * M + info["beta"] * Kd) if damped else np.zeros_like(M)
        Mf, Cf, Kf = M[np.ix_(ff, ff)], C[np.ix_(ff, ff)], K[np.ix_(ff, ff)]
        u = u_static[ff].copy()
        v = np.zeros(len(ff))
        a = np.zeros(len(ff))
        g, b = 0.5, 0.25
        eff = Mf + g * dt * Cf + b * dt**2 * Kf
        err = 0.0
        for k in range(len(res["time"])):
            up = u + dt * v + dt**2 * (0.5 - b) * a
            vp = v + dt * (1 - g) * a
            a = np.linalg.solve(eff, -(Cf @ vp + Kf @ up))
            u = up + b * dt**2 * a
            v = vp + g * dt * a
            err = max(err, abs(u[mid_idx] - res["ctrl_y"][k]))
        report.append(f"free vibration {label}: max |midspan y, OpenSees - numpy linear| = {err:.3e} mm "
                      f"(initial {u0 / mm:.1f} mm)")
    # Modal damping implied by the assumed coefficients (proportional damping: zeta_n = alpha/(2 w_n) + beta w_n/2).
    w = np.sqrt(lam_np[:4])
    for label, ref in (("free run", rayleigh_reference_free), ("dynamic run", rayleigh_reference_dyn)):
        alpha, beta, _, _ = rayleigh_assumed(damping_ratio, ref, total_mass)
        zeta_full = alpha / (2.0 * w) + beta * w / 2.0
        zeta_mass = alpha / (2.0 * w)
        report.append(f"modal damping ratios, {label}, modes 1-4, all members carry the stiffness term (%): "
                      + ", ".join(f"{100.0 * z:.3f}" for z in zeta_full))
        report.append(f"modal damping ratios, {label}, modes 1-4, mass term only, as in the source's truss model (%): "
                      + ", ".join(f"{100.0 * z:.4f}" for z in zeta_mass))
    report.append(f"damping ratio from log decrement (%): undamped y = {damping_ratio_logdec(free_u['ctrl_y']):.4f}, "
                  f"damped y = {damping_ratio_logdec(free_d['ctrl_y']):.4f}")
    (output_dir / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report:
        print(line)


def post_process(output_dir: Path, odbs: dict, push, free_u, free_d, dyn_u, dyn_d, periods_os: np.ndarray) -> None:
    """Write the CSV files, figures, interactive views and flush the ODBs."""
    for odb in odbs.values():
        odb.save_response()
    save_csv(output_dir, "pushover_history.csv", {"load_factor": push["lam"], "ctrl_x_mm": push["ctrl_x"],
                                                  "ctrl_y_mm": push["ctrl_y"], "rx_N": push["rx"], "ry_N": push["ry"]})
    keys = ("time", "ctrl_x", "ctrl_y", "vel_y", "acc_y", "rx", "ry")
    save_csv(output_dir, "free_undamped_history.csv", {k: free_u[k] for k in keys})
    save_csv(output_dir, "free_damped_history.csv", {k: free_d[k] for k in keys})
    save_csv(output_dir, "dynamic_undamped_history.csv", {k: dyn_u[k] for k in keys})
    save_csv(output_dir, "dynamic_damped_history.csv", {k: dyn_d[k] for k in keys})
    np.savetxt(output_dir / "initial_periods.txt", periods_os, header="first four periods of the undeformed model (s)")
    plot_figures(output_dir, push, free_u, free_d, dyn_u, dyn_d)
    vis_curves(output_dir, [
        {"x": -push["ctrl_y"] / mm, "y": -push["ry"] / N, "xlabel": "Downward displacement of midspan node (mm)",
         "ylabel": "Support reaction, vertical (N)", "title": "Pushover"},
    ], filename="vis_08_pushover.html", title="Pushover: reaction vs displacement")
    t = dyn_d["time"]
    vis_curves(output_dir, [
        {"x": t, "y": dyn_u["ctrl_y"] / mm, "xlabel": "Time (s)", "ylabel": "Midspan y (mm)", "title": "Vertical, undamped"},
        {"x": t, "y": dyn_d["ctrl_y"] / mm, "xlabel": "Time (s)", "ylabel": "Midspan y (mm)", "title": "Vertical, damped"},
        {"x": t, "y": dyn_u["ctrl_x"] / mm, "xlabel": "Time (s)", "ylabel": "Midspan x (mm)", "title": "Horizontal, undamped"},
        {"x": t, "y": dyn_d["ctrl_x"] / mm, "xlabel": "Time (s)", "ylabel": "Midspan x (mm)", "title": "Horizontal, damped"},
    ], filename="vis_09_dynamic.html", title="Seismic response (ground motions X and Y)")
    if "pushover" in odbs:
        vis_defo(output_dir, filename="vis_05_deformed_pushover.html", odb_tag=ODB_PUSH,
                 resp_dof="UY", resp_type="disp", scale=1.0)


# ── 12. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))        # before any CreateODB (AGENT.md §12ac)
    gm_x = Path(__file__).parent / "ground_motions" / "OPENSEES_SPRING_SEISMIC_01.txt"
    gm_y = Path(__file__).parent / "ground_motions" / "OPENSEES_SPRING_SEISMIC_02.txt"
    periods_os = run_initial_periods(output_dir)
    odb_push, push = run_pushover(output_dir)
    odb_fu, free_u, info_u = run_free_vibration(False, output_dir)
    odb_fd, free_d, info_d = run_free_vibration(True, output_dir)
    odb_du, dyn_u, _ = run_dynamic(False, gm_x, gm_y)
    odb_dd, dyn_d, _ = run_dynamic(True, gm_x, gm_y)
    post_process(output_dir, {"pushover": odb_push, "free_undamped": odb_fu, "free_damped": odb_fd,
                              "dynamic_undamped": odb_du, "dynamic_damped": odb_dd},
                 push, free_u, free_d, dyn_u, dyn_d, periods_os)
    validate(output_dir, push, free_u, free_d, info_u, info_d, periods_os)
