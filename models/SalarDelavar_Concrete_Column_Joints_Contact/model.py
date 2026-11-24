# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D concrete column with axial, lateral and rotational springs at both ends (beam-column joint model).
           Three fibre nonlinearBeamColumn elements, 3 m long, 600 x 600 mm section with 16 bars of 25 mm.
UniqueID : SalarDelavar_Concrete_Column_Joints_Contact
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-24
Purpose  : Horizontal pushover of the top node (displacement control, 520 mm) and the response to two ground motions
           (X and Y) with modal Rayleigh damping (5 %).
Ref      : py_ref/CONCRETE_COLUMN_JOINTS_CONTACT.py (source), py_ref/README_SOURCE.md, py_ref/PLOT_2D.py (source plotting
           helper, not run), py_ref/OPENSEES_COLUMN_JOINT_SPRINGS_CONCRETE.jpg (reference figure). Source:
           https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_COLUMN_JOINTS_CONTACT
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
ODB_DYN = "dynamic"
NODE_GROUND_BASE = 100           # source ground node of the base springs (fixed)
NODE_GROUND_TOP = 400            # source ground node of the top springs (fixed)
ELE_COLUMN = (1, 2, 3)           # nonlinearBeamColumn elements, bottom to top (source)
MAT_CONC_CORE_END = 1            # Concrete02, confined core: bottom and top sections
MAT_CONC_COVER = 2               # Concrete02, unconfined cover
MAT_REBAR = 3                    # Hysteretic reinforcement
MAT_CONC_CORE_MID = 4            # Concrete02, confined core: middle section
MAT_SPRING_TRANS = 100           # Steel02: lateral (dir 1) and axial (dir 2) joint springs
MAT_SPRING_ROT = 200             # Steel02: rotational joint spring (dir 6)
SEC_END = 1                      # fibre section, bottom and top elements
SEC_MID = 2                      # fibre section, middle element
TRANSF = 1                       # corotational transformation
TS_PUSH = 1                      # reference load of the pushover
PAT_PUSH = 1
TS_GROUND_X = 100                # horizontal ground acceleration (source time series 100, pattern 1)
PAT_GROUND_X = 1
TS_GROUND_Y = 200                # vertical ground acceleration (source time series 200, pattern 2)
PAT_GROUND_Y = 2
N_INT_POINTS = 5                 # integration points per element (source)
N_FIB_Y = 120                    # fibres along y per patch (source nFibCoverY = nFibCoreY)
N_FIB_Z = 3                      # fibres along z per patch (source nFibCoverZ = nFibCoreZ)


def node_tag(i: int) -> int:
    """Tag of column node i (0-based): nodes 1 to 4 from the base to the top (source)."""
    return i + 1


CONTROL_NODE = node_tag(3)       # top node (source num_nodes = 4)

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
col_length = 3000.0 * mm                       # source COL
b_sec = 600.0 * mm                             # source Bcol01 = Bcol02 (width)
h_sec = 600.0 * mm                             # source Hcol01 = Hcol02 (depth)
cover = 50.0 * mm                              # source COVER
rebar_dia = 25.0 * mm                          # source REBAR_DIA
fc = -25.0 * MPa                               # source fc: nominal concrete strength (compression negative)
Ec = 4700.0 * np.sqrt(-fc / MPa) * MPa         # source Ec = 4700 sqrt(-fc)
Es = 210e4 * MPa                               # source E_steel = 210e4 N/mm^2 as written (see README)
fy_rebar = 4000.0 * MPa                        # source fy = 4000 N/mm^2 as written (see README)

# joint springs (source formulas, based on the section area B x H)
P_Y = 42000.0 * b_sec * h_sec                  # axial spring yield force (N)
P_Y_D = 12.0 * mm                              # axial spring yield displacement
P_K = P_Y / P_Y_D                              # axial spring stiffness (N/mm)
P_U = 1.21 * P_Y
P_ESH_D = 20.0 * mm
P_EULT_D = 50.0 * mm
P_ESH_STIFF = (P_U - P_Y) / (P_EULT_D - P_ESH_D)
Z_TRANS = P_ESH_STIFF / P_K                    # hardening ratio of the axial and lateral springs
M_Y = 57530.0 * b_sec * h_sec                  # rotational spring yield moment (N.mm)
M_Y_R = 0.0523                                 # rotational spring yield rotation (rad)
M_K = M_Y / M_Y_R                              # rotational spring stiffness (N.mm/rad)
M_U = 1.524 * M_Y
M_ESH_R = 0.095
M_EULT_R = 0.162
M_ESH_STIFF = (M_U - M_Y) / (M_EULT_R - M_ESH_R)
Z_ROT = M_ESH_STIFF / M_K                      # hardening ratio of the rotational spring

# masses at the top node, as written in the source (labelled [N] there, used as N.s^2/mm; see README)
mass_top_x = 20.0e5 * N * sec**2 / mm
mass_top_y = 20.0e5 * N * sec**2 / mm
mass_top_rot = 1.0e-9                          # rotational mass, as written

# pushover
push_load_x = 100.0 * N                        # source PX: reference horizontal load at the top node (scaled by lambda)
push_load_y = 0.0 * N                          # source PY
push_moment = 0.0 * N * mm                     # source MZ
max_disp = 520.0 * mm                          # source MAX_DISP (horizontal, top node)
disp_incr = 0.01 * mm                          # source DISP_INCR: 52000 steps
pushover_tol = 1.0e-10                         # source tolerance
pushover_iter = 5000                           # source MAX_ITERATIONS

# dynamic
damping_ratio = 0.05                           # source Damping_Ratio (modal Rayleigh damping)
dyn_dt = 0.01 * sec                            # source dt
duration = 10.0 * sec                          # source Duration
n_transient = int(round(duration / dyn_dt))    # 1000 steps
gm_factor = 9810.0 * mm / sec**2               # source GMfact: standard gravity in mm/s^2
ssf_x = 0.01                                   # source SSF_X
ssf_y = 0.01                                   # source SSF_Y
iv0 = 0.00005 * mm / sec                       # source iv0_X = iv0_Y
st_iv0 = 0.0 * sec                             # source st_iv0
dyn_tol = 1.0e-10                              # source tolerance (MAX_TOLERANCE in DYNAMIC_ANALYSIS)
dyn_iter = 10000                               # source MAX_ITERATIONS in DYNAMIC_ANALYSIS
newmark_gamma = 0.5                            # source NewmarkGamma
newmark_beta = 0.25                            # source NewmarkBeta

odb_every_pushover = 500                       # 104 ODB fetches over 52000 steps (AGENT.md §3d)
odb_every_transient = 10                       # 100 fetches over 1000 steps


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Start a fresh 2D model with three DOFs per node (ux, uy, rotation)."""
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)


# ── 5. NODES AND BOUNDARY CONDITIONS ─────────────────────────────────────────
def define_nodes() -> None:
    """Column nodes 1 to 4 (every 1 m), the two ground nodes of the springs, and the top-node masses."""
    for i in range(4):
        ops.node(node_tag(i), 0.0, col_length * i / 3.0)
    ops.node(NODE_GROUND_BASE, 0.0, 0.0)
    ops.node(NODE_GROUND_TOP, 0.0, col_length)
    ops.mass(CONTROL_NODE, mass_top_x, mass_top_y, mass_top_rot)


def define_boundary_conditions() -> None:
    """Base node: vertical DOF fixed, lateral and rotation free (source fix(1, 0, 1, 0)).
    The ground nodes of the springs are fixed in all DOFs.
    """
    ops.fix(node_tag(0), 0, 1, 0)
    ops.fix(NODE_GROUND_BASE, 1, 1, 1)
    ops.fix(NODE_GROUND_TOP, 1, 1, 1)


# ── 6. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Concrete02 (confined core and cover), Hysteretic reinforcement, and Steel02 joint springs, as written in the source."""
    Kfc = 1.2                                   # confined/unconfined strength ratio, bottom and top sections
    fc1C = Kfc * fc
    eps1C = 2 * fc1C / Ec
    fc2C = 0.2 * fc1C
    eps2C = 5 * eps1C
    Kfcm = 1.05                                 # confined/unconfined strength ratio, middle section
    fc1Cm = Kfcm * fc
    eps1Cm = 2 * fc1Cm / Ec
    fc2Cm = 0.2 * fc1Cm
    eps2Cm = 5 * eps1Cm
    ftCm = -0.55 * fc1Cm
    fc1U = fc
    eps1U = -0.0025
    fc2U = 0.2 * fc1U
    eps2U = -0.012
    Lam = 0.1
    ftC = -0.55 * fc1C
    ftU = -0.55 * fc1U
    Ets = ftU / 0.002
    ops.uniaxialMaterial("Concrete02", MAT_CONC_CORE_END, fc1C, eps1C, fc2C, eps2C, Lam, ftC, Ets)
    ops.uniaxialMaterial("Concrete02", MAT_CONC_CORE_MID, fc1Cm, eps1Cm, fc2Cm, eps2Cm, Lam, ftCm, Ets)
    ops.uniaxialMaterial("Concrete02", MAT_CONC_COVER, fc1U, eps1U, fc2U, eps2U, Lam, ftU, Ets)

    ey = fy_rebar / Es
    fu = 1.1818 * fy_rebar
    esu = ey * 75.2
    ops.uniaxialMaterial("Hysteretic", MAT_REBAR, fy_rebar, ey, fu, esu, 0.2 * fu, 1.1 * esu,
                         -fy_rebar, -ey, -fu, -0.5 * esu, -0.2 * fu, -1.1 * esu,
                         0.8, 0.5, 0.0, 0.0, 0.1)

    ops.uniaxialMaterial("Steel02", MAT_SPRING_TRANS, P_Y, P_K, Z_TRANS, 18.0, 0.925, 0.15)
    ops.uniaxialMaterial("Steel02", MAT_SPRING_ROT, M_Y, M_K, Z_ROT, 18.0, 0.925, 0.15)


# ── 7. SECTIONS ──────────────────────────────────────────────────────────────
def define_fiber_section(sec_tag: int, core_mat: int) -> None:
    """Rectangular fibre section with a confined core, four cover strips and the 16 reinforcing bars (source geometry)."""
    y1 = h_sec / 2.0
    z1 = b_sec / 2.0
    y2 = 0.5 * (h_sec - 2 * cover) / 2.0
    area_bar = np.pi * rebar_dia**2 / 4.0
    ops.section("Fiber", sec_tag, "-GJ", 1.0e6)
    ops.patch("rect", core_mat, N_FIB_Y, N_FIB_Z, cover - y1, cover - z1, y1 - cover, z1 - cover)
    ops.patch("rect", MAT_CONC_COVER, N_FIB_Y, N_FIB_Z, -y1, -z1, y1, cover - z1)
    ops.patch("rect", MAT_CONC_COVER, N_FIB_Y, N_FIB_Z, -y1, z1 - cover, y1, z1)
    ops.patch("rect", MAT_CONC_COVER, N_FIB_Y, N_FIB_Z, -y1, cover - z1, cover - y1, z1 - cover)
    ops.patch("rect", MAT_CONC_COVER, N_FIB_Y, N_FIB_Z, y1 - cover, cover - z1, y1, z1 - cover)
    ops.layer("straight", MAT_REBAR, 5, area_bar, y1 - cover, z1 - cover, y1 - cover, cover - z1)
    ops.layer("straight", MAT_REBAR, 2, area_bar, y2, z1 - cover, y2, cover - z1)
    ops.layer("straight", MAT_REBAR, 2, area_bar, 0.0, z1 - cover, 0.0, cover - z1)
    ops.layer("straight", MAT_REBAR, 2, area_bar, -y2, z1 - cover, -y2, cover - z1)
    ops.layer("straight", MAT_REBAR, 5, area_bar, cover - y1, z1 - cover, cover - y1, cover - z1)


def define_fiber_sections() -> None:
    """Bottom and top section (confined core MAT 1) and middle section (confined core MAT 4)."""
    define_fiber_section(SEC_END, MAT_CONC_CORE_END)
    define_fiber_section(SEC_MID, MAT_CONC_CORE_MID)


# ── 8. ELEMENTS AND JOINT SPRINGS ────────────────────────────────────────────
def define_elements() -> None:
    """Three corotational nonlinearBeamColumn elements; the bottom and top elements use the end section."""
    ops.geomTransf("Corotational", TRANSF)
    for i, ele in enumerate(ELE_COLUMN):
        sec = SEC_END if i in (0, 2) else SEC_MID
        ops.element("nonlinearBeamColumn", ele, node_tag(i), node_tag(i + 1), N_INT_POINTS, sec, TRANSF)


def define_springs() -> None:
    """Joint springs at both ends (source elements 4 to 9). The base vertical spring (element 5) acts on a fixed DOF,
    so it carries no force (as in the source)."""
    ops.element("zeroLength", 4, NODE_GROUND_BASE, node_tag(0), "-mat", MAT_SPRING_TRANS, "-dir", 1)
    ops.element("zeroLength", 5, NODE_GROUND_BASE, node_tag(0), "-mat", MAT_SPRING_TRANS, "-dir", 2)
    ops.element("zeroLength", 6, NODE_GROUND_BASE, node_tag(0), "-mat", MAT_SPRING_ROT, "-dir", 6)
    ops.element("zeroLength", 7, NODE_GROUND_TOP, CONTROL_NODE, "-mat", MAT_SPRING_TRANS, "-dir", 1)
    ops.element("zeroLength", 8, NODE_GROUND_TOP, CONTROL_NODE, "-mat", MAT_SPRING_TRANS, "-dir", 2)
    ops.element("zeroLength", 9, NODE_GROUND_TOP, CONTROL_NODE, "-mat", MAT_SPRING_ROT, "-dir", 6)


# ── 9. OUTPUT DATABASE (ODB) ─────────────────────────────────────────────────
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


def build_model(odb_tag, output_dir: Path = None):
    """Build the model and, when odb_tag is given, its ODB. The V1 and V2 stages are written when output_dir is given.

    Returns:
        The CreateODB instance, or None when odb_tag is None.
    """
    init_model()
    define_nodes()
    define_boundary_conditions()
    define_materials()
    define_fiber_sections()
    if output_dir is not None:
        vis_nodes(output_dir)                      # V1: nodes and supports
    define_elements()
    define_springs()
    if output_dir is not None:
        vis_model(output_dir)                      # V2: geometry
    return None if odb_tag is None else create_odb(odb_tag)


# ── 10. LOADING ──────────────────────────────────────────────────────────────
def define_static_load() -> None:
    """Reference horizontal load PX at the top node (source: load(num_nodes, PX, PY, MZ)); the displacement control sets lambda."""
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    ops.load(CONTROL_NODE, push_load_x, push_load_y, push_moment)


def define_ground_motions(gm_x: Path, gm_y: Path) -> None:
    """Both ground accelerations, as the source defines them: X in DOF 1 (pattern 1) and Y in DOF 2 (pattern 2)."""
    ops.timeSeries("Path", TS_GROUND_X, "-dt", dyn_dt, "-filePath", str(gm_x), "-factor", gm_factor,
                   "-startTime", st_iv0)
    ops.pattern("UniformExcitation", PAT_GROUND_X, 1, "-accel", TS_GROUND_X, "-vel0", iv0, "-fact", ssf_x)
    ops.timeSeries("Path", TS_GROUND_Y, "-dt", dyn_dt, "-filePath", str(gm_y), "-factor", gm_factor)
    ops.pattern("UniformExcitation", PAT_GROUND_Y, 2, "-accel", TS_GROUND_Y, "-vel0", iv0, "-fact", ssf_y)


def support_reactions() -> tuple:
    """Horizontal reactions at the two spring ground nodes (base and top) for the current state."""
    ops.reactions()
    return ops.nodeReaction(NODE_GROUND_BASE, 1), ops.nodeReaction(NODE_GROUND_TOP, 1)


# ── 11. ANALYSIS ─────────────────────────────────────────────────────────────
def run_pushover(output_dir: Path) -> tuple:
    """Horizontal displacement control at the top node, through SmartAnalyze (source PUSHOVER_ANALYSIS).

    Returns:
        (odb, history): the ODB and the per-step arrays. The base shear, axial and moment follow the source's sign
        convention for the pushover (minus the element-1 end forces).
    """
    odb = build_model(ODB_PUSH, output_dir)
    define_static_load()
    vis_loads(output_dir)                          # V3: load vectors
    vis_pre_analysis(output_dir)                   # V4: last check before the solver
    ops.constraints("Plain")
    ops.numberer("RCM")
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
    keys = ("lam", "ctrl_x", "ctrl_y", "rot", "drift", "base_shear", "base_axial", "base_moment", "rx_base", "rx_top")
    history = {key: [] for key in keys}
    for k, seg in enumerate(analysis.static_split([max_disp], maxStep=abs(disp_incr))):
        ok = analysis.StaticAnalyze(node=CONTROL_NODE, dof=1, seg=seg)
        if ok < 0:
            break
        if k % odb_every_pushover == 0:
            odb.fetch_response_step()
        ef = ops.eleResponse(ELE_COLUMN[0], "force")   # base end of element 1: [Fx, Fy, M] (global)
        rx_base, rx_top = support_reactions()
        history["lam"].append(ops.getTime())
        history["ctrl_x"].append(ops.nodeDisp(CONTROL_NODE, 1))
        history["ctrl_y"].append(ops.nodeDisp(CONTROL_NODE, 2))
        history["rot"].append(ops.nodeDisp(CONTROL_NODE, 3))
        history["drift"].append((ops.nodeDisp(CONTROL_NODE, 1) - ops.nodeDisp(node_tag(0), 1)) / col_length * 100.0)
        history["base_shear"].append(-ef[0])
        history["base_axial"].append(-ef[1])
        history["base_moment"].append(-ef[2])
        history["rx_base"].append(rx_base)
        history["rx_top"].append(rx_top)
    analysis.close()
    return odb, {key: np.array(value) for key, value in history.items()}


def modal_rayleigh(zeta: float) -> tuple:
    """Rayleigh coefficients from the first two eigenvalues of the model (source: modal, not assumed).

    Returns:
        (alpha_m, alpha_k, omega_lower, omega_higher). ops.rayleigh(alpha_m, alpha_k, 0, 0).
    """
    eig = ops.eigen("-fullGenLapack", 2)
    w_hi = np.power(max(eig), 0.5)
    w_lo = np.power(min(eig), 0.5)
    alpha_m = 2.0 * w_hi * w_lo * zeta / (w_hi + w_lo)
    alpha_k = 2.0 * zeta / (w_hi + w_lo)
    ops.rayleigh(alpha_m, alpha_k, 0.0, 0.0)
    return alpha_m, alpha_k, w_lo, w_hi


def run_dynamic(gm_x: Path, gm_y: Path) -> tuple:
    """Both ground motions through Newmark (0.5, 0.25) and SmartAnalyze, with modal Rayleigh damping (source DYNAMIC_ANALYSIS).

    The source's gravity step has no loads (its load lines are commented out), so it is not run here.

    Returns:
        (odb, history, rayleigh): rayleigh = (alpha_m, alpha_k, omega_lower, omega_higher).
    """
    odb = build_model(ODB_DYN)
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    rayleigh = modal_rayleigh(damping_ratio)
    define_ground_motions(gm_x, gm_y)
    ops.integrator("Newmark", newmark_gamma, newmark_beta)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="RelativeNormUnbalance",
        testTol=dyn_tol,
        testIterTimes=dyn_iter,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 40, 20, 30, 50],            # Newton first (the source's RaphsonNewton)
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6 * sec,
        printPer=0,
        testPrintFlag=0,
    )
    keys = ("time", "ctrl_x", "vel_x", "acc_x", "ctrl_y", "vel_y", "acc_y", "rot", "drift",
            "base_shear", "base_axial", "base_moment", "rx_base", "rx_top")
    rows = {key: [] for key in keys}
    for k in analysis.transient_split(n_transient):
        ok = analysis.TransientAnalyze(dyn_dt)
        if ok < 0:
            break
        if k % odb_every_transient == 0:
            odb.fetch_response_step()
        ef = ops.eleResponse(ELE_COLUMN[0], "force")   # as written in the source (no minus sign here)
        rx_base, rx_top = support_reactions()
        rows["time"].append(ops.getTime())
        rows["ctrl_x"].append(ops.nodeDisp(CONTROL_NODE, 1))
        rows["vel_x"].append(ops.nodeVel(CONTROL_NODE, 1))
        rows["acc_x"].append(ops.nodeAccel(CONTROL_NODE, 1))
        rows["ctrl_y"].append(ops.nodeDisp(CONTROL_NODE, 2))
        rows["vel_y"].append(ops.nodeVel(CONTROL_NODE, 2))
        rows["acc_y"].append(ops.nodeAccel(CONTROL_NODE, 2))
        rows["rot"].append(ops.nodeDisp(CONTROL_NODE, 3))
        rows["drift"].append((ops.nodeDisp(CONTROL_NODE, 1) - ops.nodeDisp(node_tag(0), 1)) / col_length * 100.0)
        rows["base_shear"].append(ef[0])
        rows["base_axial"].append(ef[1])
        rows["base_moment"].append(ef[2])
        rows["rx_base"].append(rx_base)
        rows["rx_top"].append(rx_top)
    analysis.close()
    return odb, {key: np.array(value, dtype=float) for key, value in rows.items()}, rayleigh


# ── 12. POST-PROCESSING ──────────────────────────────────────────────────────
def damping_ratio_logdec(signal) -> float:
    """Damping ratio in percent from the logarithmic decrement of the positive peaks (source EQUATION, closed form).

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


def plot_figures(output_dir: Path, push: dict, dyn: dict) -> None:
    """Two PNG figures: the pushover curve (base shear against top displacement) and the seismic response."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    ax.plot(push["ctrl_x"] / mm, push["base_shear"] / N, color=COLORS["primary"], lw=1.8)
    _style_ax(ax, "Horizontal displacement of top node (mm)", "Base shear (N), source definition",
              "Pushover: base shear vs top displacement")
    fig.tight_layout()
    fig.savefig(output_dir / "pushover_curve.png")
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), dpi=150)
    axes[0].plot(dyn["time"], dyn["ctrl_x"] / mm, color=COLORS["primary"], lw=1.0)
    _style_ax(axes[0], "Time (s)", "Top node x (mm)", "Seismic response, horizontal (ground motions X and Y)")
    axes[1].plot(dyn["time"], dyn["ctrl_y"] / mm, color=COLORS["secondary"], lw=1.0)
    _style_ax(axes[1], "Time (s)", "Top node y (mm)", "Seismic response, vertical")
    fig.tight_layout()
    fig.savefig(output_dir / "dynamic.png")
    plt.close(fig)


def post_process(output_dir: Path, odbs: dict, push: dict, dyn: dict, periods: np.ndarray) -> None:
    """Write the CSV files, figures, interactive views and flush the ODBs."""
    for odb in odbs.values():
        odb.save_response()
    save_csv(output_dir, "pushover_history.csv", {
        "load_factor": push["lam"], "ctrl_x_mm": push["ctrl_x"], "ctrl_y_mm": push["ctrl_y"],
        "rot_rad": push["rot"], "drift_pct": push["drift"], "base_shear_N": push["base_shear"],
        "base_axial_N": push["base_axial"], "base_moment_Nmm": push["base_moment"],
        "rx_base_N": push["rx_base"], "rx_top_N": push["rx_top"]})
    save_csv(output_dir, "dynamic_history.csv", {key: dyn[key] for key in dyn})
    np.savetxt(output_dir / "initial_periods.txt", periods,
               header="first two periods of the undeformed model (s): lower, higher")
    plot_figures(output_dir, push, dyn)
    vis_curves(output_dir, [
        {"x": push["ctrl_x"] / mm, "y": push["base_shear"] / N, "xlabel": "Top node x (mm)",
         "ylabel": "Base shear (N), source definition", "title": "Pushover"},
    ], filename="vis_08_pushover.html", title="Pushover: base shear vs top displacement")
    t = dyn["time"]
    vis_curves(output_dir, [
        {"x": t, "y": dyn["ctrl_x"] / mm, "xlabel": "Time (s)", "ylabel": "Top node x (mm)", "title": "Horizontal"},
        {"x": t, "y": dyn["ctrl_y"] / mm, "xlabel": "Time (s)", "ylabel": "Top node y (mm)", "title": "Vertical"},
    ], filename="vis_09_dynamic.html", title="Seismic response (ground motions X and Y)")
    if "pushover" in odbs:
        vis_defo(output_dir, filename="vis_05_deformed_pushover.html", odb_tag=ODB_PUSH,
                 resp_dof="UX", resp_type="disp", scale=1.0)


# ── 13. VALIDATION (independent numpy checks) ───────────────────────────────
def section_stiffness_from_fibres() -> tuple:
    """Initial axial stiffness EA and bending stiffness EI of the fibre section, summed over the fibre geometry.

    The initial tangents are E0 = 2 fc / eps0 for Concrete02 (the core, and the cover with eps0 = -0.0025) and Es for
    the reinforcement. This does not use OpenSees.
    """
    y1 = h_sec / 2.0
    z1 = b_sec / 2.0
    y2 = 0.5 * (h_sec - 2 * cover) / 2.0
    area_bar = np.pi * rebar_dia**2 / 4.0
    Ec_core = Ec                                                   # E0 = 2 fc1C / eps1C = Ec for the confined core
    E_cover = 2.0 * fc / -0.0025                                   # unconfined cover (eps0 = -0.0025)
    fibres = []

    def patch(E, yI, zI, yJ, zJ):
        dy = (yJ - yI) / N_FIB_Y
        dz = (zJ - zI) / N_FIB_Z
        for i in range(N_FIB_Y):
            yc = yI + (i + 0.5) * dy
            for _ in range(N_FIB_Z):
                fibres.append((E, dy * dz, yc))

    def layer(E, n, yS, zS, yE, zE):
        for k in range(n):
            t = k / (n - 1) if n > 1 else 0.0
            fibres.append((E, area_bar, yS + t * (yE - yS)))

    patch(Ec_core, cover - y1, cover - z1, y1 - cover, z1 - cover)
    patch(E_cover, -y1, -z1, y1, cover - z1)
    patch(E_cover, -y1, z1 - cover, y1, z1)
    patch(E_cover, -y1, cover - z1, cover - y1, z1 - cover)
    patch(E_cover, y1 - cover, cover - z1, y1, z1 - cover)
    layer(Es, 5, y1 - cover, z1 - cover, y1 - cover, cover - z1)
    layer(Es, 2, y2, z1 - cover, y2, cover - z1)
    layer(Es, 2, 0.0, z1 - cover, 0.0, cover - z1)
    layer(Es, 2, -y2, z1 - cover, -y2, cover - z1)
    layer(Es, 5, cover - y1, z1 - cover, cover - y1, cover - z1)
    EA = sum(E * A for E, A, _ in fibres)
    EI = sum(E * A * y * y for E, A, y in fibres)
    return EA, EI


def frame_matrices(EA: float, EI: float) -> tuple:
    """Linear 2D frame (column) stiffness, joint spring stiffness, lumped mass and free DOFs, in numpy."""
    ndof = 3 * 4

    def dof(node: int, d: int) -> int:
        return 3 * (node - 1) + d

    Kc = np.zeros((ndof, ndof))
    Ks = np.zeros((ndof, ndof))
    M = np.zeros((ndof, ndof))
    L = col_length / 3.0
    kl = np.array([
        [EA / L, 0, 0, -EA / L, 0, 0],
        [0, 12 * EI / L**3, 6 * EI / L**2, 0, -12 * EI / L**3, 6 * EI / L**2],
        [0, 6 * EI / L**2, 4 * EI / L, 0, -6 * EI / L**2, 2 * EI / L],
        [-EA / L, 0, 0, EA / L, 0, 0],
        [0, -12 * EI / L**3, -6 * EI / L**2, 0, 12 * EI / L**3, -6 * EI / L**2],
        [0, 6 * EI / L**2, 2 * EI / L, 0, -6 * EI / L**2, 4 * EI / L],
    ])
    c, s = 0.0, 1.0                                # every column element is vertical (along +y)
    T = np.array([
        [c, s, 0, 0, 0, 0],
        [-s, c, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, c, s, 0],
        [0, 0, 0, -s, c, 0],
        [0, 0, 0, 0, 0, 1],
    ])
    kg = T.T @ kl @ T
    for e in range(3):
        d = [dof(e + 1, k) for k in range(3)] + [dof(e + 2, k) for k in range(3)]
        for p in range(6):
            for q in range(6):
                Kc[d[p], d[q]] += kg[p, q]
    # joint springs (initial tangents: Steel02 E0 = P_K for lateral/axial, M_K for rotational)
    Ks[dof(1, 0), dof(1, 0)] += P_K                # base lateral (element 4)
    Ks[dof(1, 2), dof(1, 2)] += M_K                # base rotational (element 6)
    Ks[dof(4, 0), dof(4, 0)] += P_K                # top lateral (element 7)
    Ks[dof(4, 1), dof(4, 1)] += P_K                # top axial (element 8)
    Ks[dof(4, 2), dof(4, 2)] += M_K                # top rotational (element 9)
    M[dof(4, 0), dof(4, 0)] = mass_top_x
    M[dof(4, 1), dof(4, 1)] = mass_top_y
    M[dof(4, 2), dof(4, 2)] = mass_top_rot
    free = [d for d in range(ndof) if d != dof(1, 1)]   # base vertical DOF is fixed
    return Kc, Ks, M, free


def read_record(path: Path) -> np.ndarray:
    """Ground acceleration record (one value per line, at the record time step)."""
    return np.loadtxt(path)


def newmark_linear(M, C, K, F, dt, gamma, beta, v0) -> np.ndarray:
    """Linear Newmark integration of M u'' + C u' + K u = F(t) from u = 0 and u' = v0.

    The initial acceleration is taken as zero, as OpenSees starts a transient analysis without an initial-acceleration
    solve. Massless DOFs are handled by the constraint form of the Newmark update.
    """
    n_t, ndof = F.shape
    U = np.zeros((n_t, ndof))
    V = np.zeros_like(U)
    A = np.zeros_like(U)
    V[0] = v0
    Keff = M + gamma * dt * C + beta * dt * dt * K
    for k in range(n_t - 1):
        up = U[k] + dt * V[k] + dt * dt * (0.5 - beta) * A[k]
        vp = V[k] + dt * (1.0 - gamma) * A[k]
        a = np.linalg.solve(Keff, F[k + 1] - C @ vp - K @ up)
        U[k + 1] = up + beta * dt * dt * a
        V[k + 1] = vp + gamma * dt * a
        A[k + 1] = a
    return U


def validate(output_dir: Path, push: dict, dyn: dict, periods_os: np.ndarray, rayleigh: tuple,
             gm_x: Path, gm_y: Path) -> None:
    """Compare the OpenSees run with independent numpy calculations and write validation.txt.

    Checks: the first two periods (from the fibre section geometry and the spring stiffnesses); the first pushover step
    against a linear solve; the pushover equilibrium; the seismic response against a linear numpy Newmark run with the
    same modal Rayleigh coefficients (with the stiffness term on the column only, and on all elements); and the damping
    ratio from the logarithmic decrement.
    """
    import scipy.linalg as sla

    report = []
    EA0, EI0 = section_stiffness_from_fibres()
    report.append(f"section initial stiffness from the fibre geometry: EA = {EA0:.6e} N, EI = {EI0:.6e} N.mm^2")
    Kc, Ks, M, free = frame_matrices(EA0, EI0)
    K = Kc + Ks
    Kf = K[np.ix_(free, free)]
    Mf = M[np.ix_(free, free)]
    vals, vecs = sla.eig(Kf, Mf)
    order = np.argsort(np.real(vals))
    good = [i for i in order if np.isfinite(vals[i]) and np.real(vals[i]) > 1e-9]
    w_np = np.sqrt(np.real(vals[good[:2]]))
    t_np = 2.0 * np.pi / w_np
    report.append("periods (s), OpenSees: " + ", ".join(f"{t:.6f}" for t in periods_os))
    report.append("periods (s), numpy:    " + ", ".join(f"{t:.6f}" for t in t_np))

    ix = free.index(3 * (CONTROL_NODE - 1))         # top node, horizontal DOF
    iy = free.index(3 * (CONTROL_NODE - 1) + 1)     # top node, vertical DOF
    f = np.zeros(len(free))
    f[ix] = push_load_x / N
    u_unit = np.linalg.solve(Kf, f)
    lam_lin = (disp_incr / mm) / u_unit[ix]
    rel = abs(push["lam"][0] / lam_lin - 1.0)
    report.append(f"first pushover step: load factor OpenSees {push['lam'][0]:.6e}, linear numpy {lam_lin:.6e} "
                  f"(relative difference {rel:.2e})")

    load_total = push["lam"] * push_load_x / N
    residual = np.abs(push["rx_base"] + push["rx_top"] + load_total)
    report.append(f"pushover equilibrium over {len(push['lam'])} steps: max |Rx(base) + Rx(top) + lambda P| / max|lambda P| = "
                  f"{np.max(residual) / np.max(np.abs(load_total)):.2e}")

    rec_x = np.zeros(n_transient + 1)
    rec_y = np.zeros(n_transient + 1)
    rx_vals = read_record(gm_x)
    ry_vals = read_record(gm_y)
    rec_x[:min(len(rx_vals), n_transient + 1)] = rx_vals[:n_transient + 1]
    rec_y[:min(len(ry_vals), n_transient + 1)] = ry_vals[:n_transient + 1]
    ag_x = gm_factor * ssf_x * rec_x
    ag_y = gm_factor * ssf_y * rec_y
    F = np.zeros((n_transient + 1, len(free)))
    F[:, ix] = -mass_top_x * ag_x
    F[:, iy] = -mass_top_y * ag_y
    v0_free = np.array([float(iv0) if (d % 3) in (0, 1) else 0.0 for d in free])   # initial velocity iv0 in x and y
    alpha_m, alpha_k = rayleigh[0], rayleigh[1]
    K_col = Kc[np.ix_(free, free)]
    for label, Kd in (("stiffness term on the column only (as written: springs are zeroLength)", K_col),
                      ("stiffness term on all elements (springs included)", Kf)):
        C = alpha_m * Mf + alpha_k * Kd
        U = newmark_linear(Mf, C, Kf, F, dyn_dt / sec, newmark_gamma, newmark_beta, v0_free)
        err_x = np.max(np.abs(U[1:, ix] - dyn["ctrl_x"] / mm))
        err_y = np.max(np.abs(U[1:, iy] - dyn["ctrl_y"] / mm))
        amp = max(np.max(np.abs(dyn["ctrl_x"])) / mm, np.max(np.abs(dyn["ctrl_y"])) / mm)
        report.append(f"seismic response, linear numpy Newmark (OpenSees start: zero acceleration, velocity iv0), {label}: "
                      f"max |OpenSees - numpy| x = {err_x:.3e} mm, "
                      f"y = {err_y:.3e} mm (relative to the largest response {amp:.3e} mm: {max(err_x, err_y) / amp:.2e})")
        # modal damping ratios from the numpy modes (zeta_n = phi' C phi / (2 w_n phi' M phi))
        Cf_full = C
        zetas = []
        for i in good[:2]:
            phi = np.real(vecs[:, i])
            w = np.sqrt(np.real(vals[i]))
            zetas.append((phi @ Cf_full @ phi) / (2.0 * w * (phi @ Mf @ phi)))
        report.append(f"modal damping ratios from the numpy modes, {label} (%): "
                      + ", ".join(f"{100.0 * z:.3f}" for z in zetas))
    report.append(f"damping ratio from log decrement of the OpenSees top-node x response (%): "
                  f"{damping_ratio_logdec(dyn['ctrl_x']):.4f}")
    (output_dir / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report:
        print(line)


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))        # before any CreateODB (AGENT.md §12ac)
    gm_x = Path(__file__).parent / "ground_motions" / "Ground_Acceleration_X.txt"
    gm_y = Path(__file__).parent / "ground_motions" / "Ground_Acceleration_Y.txt"
    odb_push, push = run_pushover(output_dir)
    odb_dyn, dyn, rayleigh = run_dynamic(gm_x, gm_y)
    periods = np.array([2.0 * np.pi / rayleigh[2], 2.0 * np.pi / rayleigh[3]])
    post_process(output_dir, {"pushover": odb_push, "dynamic": odb_dyn}, push, dyn, periods)
    validate(output_dir, push, dyn, periods, rayleigh, gm_x, gm_y)
