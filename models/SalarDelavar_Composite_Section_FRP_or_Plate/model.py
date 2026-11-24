# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D composite concrete-steel portal frame: two 3 m columns (500 x 500 mm) and a 7 m beam (500 x 300 mm).
           Fibre sections with confined and unconfined concrete, reinforcing bars and a steel plate jacket (10 mm).
           Corotational nonlinearBeamColumn elements; both bases fixed.
UniqueID : SalarDelavar_Composite_Section_FRP_or_Plate
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-24
Purpose  : Monotonic horizontal pushover of the frame without and with the steel plate (the two runs of the source),
           with the bilinear fit, the over-strength factor, the displacement ductility ratio and the behaviour
           coefficient R.
Ref      : py_ref/COMPOSITE_SECTION_FRAME_PUSHOVER.py (source), py_ref/CONFINED_CONCRETE_WITH_PLATE_SECTION_FUN.py,
           py_ref/BILINEAR_CURVE.py, py_ref/ANALYSIS_FUNCTION.py and py_ref/CONCRETE_SECTION_FUN.py (not used by the
           conversion), py_ref/PLOT_2D.py (not run), py_ref/COMPOSITE_SECTION_FRAME_PUSHOVER.png (reference figure).
           Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/COMPOSITE_SECTION%20(FRP%20or%20PLATE)
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
ODB_NO_PLATE = "pushover_without_plate"
ODB_PLATE = "pushover_with_plate"
NODE_BASE_L, NODE_BASE_R = 1, 2          # source nodes at the bases
NODE_TOP_L, NODE_TOP_R = 3, 4            # source nodes at the top (control node: NODE_TOP_R, DOF 1)
ELE_COL_L, ELE_COL_R, ELE_BEAM = 1, 2, 3 # source element numbering
SEC_COL, SEC_BEAM = 10, 20               # fibre sections, column and beam (source)
MAT_CORE, MAT_COVER = 1, 2               # Concrete01: confined core and unconfined cover (source)
MAT_REBAR, MAT_PLATE = 3, 4              # Hysteretic reinforcing steel and steel plate (source STEEL_KIND = 2)
TRANSF = 1                               # corotational transformation (source)
TS_PUSH, PAT_PUSH = 1, 1                 # reference load pattern (source)
NUM_FIBERS = 20                          # fibres along the depth of each patch (source NUMFIBERS)
NUM_FIBERS_Z = 5                         # fibres across the width of each patch (source)
NUM_INT_POINTS = 5                       # integration points per element (source numIntgrPts)

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Concrete01 (source): core (confined) and cover (unconfined)
fc_core = -27.6 * MPa                    # f'c core
ec0_core = -0.0045                       # strain at f'c core
fcu_core = -21.0 * MPa                   # ultimate stress core
ecu_core = -0.015                        # ultimate strain core
fc_cover = -18.0 * MPa                   # f'c cover
ec0_cover = -0.0025                      # strain at f'c cover
fcu_cover = -2.0 * MPa                   # ultimate stress cover
ecu_cover = -0.008                       # ultimate strain cover

# Reinforcing steel, Hysteretic (source STEEL_KIND 2; values as written)
fy_rebar = 4000.0 * MPa                  # yield stress (as written; high for reinforcement)
Es_rebar = 2.0e5 * MPa                   # Young's modulus
ey_rebar = fy_rebar / Es_rebar           # yield strain
fu_rebar = 1.1818 * fy_rebar             # ultimate stress
esu_rebar = ey_rebar * 75.2              # ultimate strain

# Steel plate, Hysteretic. The source takes the plate's yield strain, ultimate stress and ultimate strain from the rebar
# values (eyP = fy/Es, fuP = 1.1818 fy, esuP = ey 75.2), while its yield stress is 240 MPa. Kept as written (see README).
fy_plate = 240.0 * MPa                   # plate yield stress
ey_plate = fy_rebar / Es_rebar           # source eyP = fy/Es
fu_plate = 1.1818 * fy_rebar             # source fuP = 1.1818 fy
esu_plate = ey_rebar * 75.2              # source esuP = ey 75.2
pinch_x, pinch_y = 0.8, 0.5              # pinching factors (source)
damage1, damage2 = 0.0, 0.0              # damage factors (source)
beta_hys = 0.1                           # stiffness degradation (source)

# Sections (source)
b_col = 500.0 * mm                       # column width
h_col = 500.0 * mm                       # column depth
cover_col = 50.0 * mm
dia_col = 25.0 * mm                      # rebar diameter, column
b_beam = 500.0 * mm                      # beam width
h_beam = 300.0 * mm                      # beam depth
cover_beam = 50.0 * mm
dia_beam = 18.0 * mm                     # rebar diameter, beam
t_plate = 10.0 * mm                      # plate (or FRP) thickness (source T)
A_bar_col = np.pi * dia_col**2 / 4.0
A_bar_beam = np.pi * dia_beam**2 / 4.0

# Geometry and pushover (source)
len_col = 3000.0 * mm                    # column length
len_beam = 7000.0 * mm                   # beam length (distance between the two bases)
dmax = 175.0 * mm                        # maximum displacement (source DMAX)
dincr = 0.05 * mm                        # displacement increment (source DINCR): 3500 steps
max_iterations = 5000                    # source MAX_ITERATIONS
max_tolerance = 1.0e-6                   # source MAX_TOLERANCE
odb_every = 10                           # 350 ODB fetches per run (AGENT.md §3d)


def node_positions() -> dict:
    """Source node coordinates: bases at y = 0, tops at y = LENGTH_COL, the right column at x = LENGTH_BM."""
    return {1: (0.0, 0.0), 2: (len_beam, 0.0), 3: (0.0, len_col), 4: (len_beam, len_col)}


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Start a fresh 2D model with three DOFs per node (ux, uy, rotation)."""
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)


# ── 5. NODES AND SUPPORTS ────────────────────────────────────────────────────
def define_nodes_and_supports() -> None:
    """Four frame nodes and fixed bases (source ops.fix(1, 1, 1, 1) and ops.fix(2, 1, 1, 1))."""
    for tag, (x, y) in node_positions().items():
        ops.node(tag, x, y)
    ops.fix(NODE_BASE_L, 1, 1, 1)
    ops.fix(NODE_BASE_R, 1, 1, 1)


# ── 6. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Concrete01 for core and cover, and Hysteretic for the reinforcing bars and the steel plate (source values)."""
    ops.uniaxialMaterial("Concrete01", MAT_CORE, fc_core, ec0_core, fcu_core, ecu_core)
    ops.uniaxialMaterial("Concrete01", MAT_COVER, fc_cover, ec0_cover, fcu_cover, ecu_cover)
    ops.uniaxialMaterial("Hysteretic", MAT_REBAR, fy_rebar, ey_rebar, fu_rebar, esu_rebar,
                         0.2 * fu_rebar, 1.1 * esu_rebar, -fy_rebar, -ey_rebar, -fu_rebar, -esu_rebar,
                         -0.2 * fu_rebar, -1.1 * esu_rebar, pinch_x, pinch_y, damage1, damage2, beta_hys)
    ops.uniaxialMaterial("Hysteretic", MAT_PLATE, fy_plate, ey_plate, fu_plate, esu_plate,
                         0.2 * fu_plate, 1.1 * esu_plate, -fy_plate, -ey_plate, -fu_plate, -esu_plate,
                         -0.2 * fu_plate, -1.1 * esu_plate, pinch_x, pinch_y, damage1, damage2, beta_hys)


# ── 7. SECTIONS ──────────────────────────────────────────────────────────────
def define_fiber_section(sec_tag: int, h: float, b: float, cover: float, area_bar: float,
                         plate: bool, col: bool) -> None:
    """Fibre section of the source (CONFINED_CONCRETE_WITH_PLATE_SECTION_FUN): confined core, four cover patches,
    reinforcing bars (three on each face, plus a middle layer for the beam) and, if requested, the steel plate jacket.
    The column is jacketed on four faces. The beam gets one plate patch on its -z (width) face, spanning the full depth,
    as the source writes it (the source comment says "bottom"; see the README).
    """
    y1 = h / 2.0
    z1 = b / 2.0
    ops.section("Fiber", sec_tag)
    ops.patch("rect", MAT_CORE, NUM_FIBERS, NUM_FIBERS_Z, cover - y1, cover - z1, y1 - cover, z1 - cover)
    ops.patch("rect", MAT_COVER, NUM_FIBERS, NUM_FIBERS_Z, -y1, z1 - cover, y1, z1)
    ops.patch("rect", MAT_COVER, NUM_FIBERS, NUM_FIBERS_Z, -y1, -z1, y1, cover - z1)
    ops.patch("rect", MAT_COVER, NUM_FIBERS, NUM_FIBERS_Z, -y1, cover - z1, cover - y1, z1 - cover)
    ops.patch("rect", MAT_COVER, NUM_FIBERS, NUM_FIBERS_Z, y1 - cover, cover - z1, y1, z1 - cover)
    ops.layer("straight", MAT_REBAR, 3, area_bar, y1 - cover, z1 - cover, y1 - cover, cover - z1)
    if not col:
        ops.layer("straight", MAT_REBAR, 2, area_bar, 0.0, z1 - cover, 0.0, cover - z1)
    ops.layer("straight", MAT_REBAR, 3, area_bar, cover - y1, z1 - cover, cover - y1, cover - z1)
    if plate:
        if col:
            # Source order: +z face, -z face, -y face, +y face (the source comments say top, bottom, left, right).
            ops.patch("rect", MAT_PLATE, NUM_FIBERS, 2, -(y1 + t_plate), z1, y1 + t_plate, z1 + t_plate)
            ops.patch("rect", MAT_PLATE, NUM_FIBERS, 2, -(y1 + t_plate), -z1 - t_plate, y1 + t_plate, -z1)
            ops.patch("rect", MAT_PLATE, 2, NUM_FIBERS, -(y1 + t_plate), -z1, -y1, z1)
            ops.patch("rect", MAT_PLATE, 2, NUM_FIBERS, y1, -z1, y1 + t_plate, z1)
        else:
            # Source: one patch on the -z (width) face over the full depth; the source comment says "bottom".
            ops.patch("rect", MAT_PLATE, NUM_FIBERS, 2, -(y1 + t_plate), -z1 - t_plate, y1 + t_plate, -z1)


def define_fiber_sections(plate: bool) -> None:
    """Column section (SEC_COL) and beam section (SEC_BEAM) of the source."""
    define_fiber_section(SEC_COL, h_col, b_col, cover_col, A_bar_col, plate, col=True)
    define_fiber_section(SEC_BEAM, h_beam, b_beam, cover_beam, A_bar_beam, plate, col=False)


# ── 8. ELEMENTS AND LOADS ────────────────────────────────────────────────────
def define_elements() -> None:
    """Two columns and one beam, corotational nonlinearBeamColumn elements (source)."""
    ops.geomTransf("Corotational", TRANSF)
    ops.element("nonlinearBeamColumn", ELE_COL_L, NODE_BASE_L, NODE_TOP_L, NUM_INT_POINTS, SEC_COL, TRANSF)
    ops.element("nonlinearBeamColumn", ELE_COL_R, NODE_BASE_R, NODE_TOP_R, NUM_INT_POINTS, SEC_COL, TRANSF)
    ops.element("nonlinearBeamColumn", ELE_BEAM, NODE_TOP_L, NODE_TOP_R, NUM_INT_POINTS, SEC_BEAM, TRANSF)


def define_load() -> None:
    """Reference load of the source: 1 N horizontal and -1 N vertical at each top node. The load factor scales it."""
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    ops.load(NODE_TOP_L, 1.0 * N, -1.0 * N, 0.0)
    ops.load(NODE_TOP_R, 1.0 * N, -1.0 * N, 0.0)


# ── 9. OUTPUT DATABASE (ODB) ─────────────────────────────────────────────────
def create_odb(odb_tag) -> "opst.post.CreateODB":
    """Nodal responses for one load case, created after the elements are defined.

    Args:
        odb_tag: Tag of this load case (one ODB per run).

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


def build_model(plate: bool, odb_tag: str, output_dir: Path = None):
    """Build the frame for one run (with or without the steel plate). The V1 and V2 stages are written when
    output_dir is given.

    Returns:
        The CreateODB instance.
    """
    init_model()
    define_nodes_and_supports()
    define_materials()
    define_fiber_sections(plate)
    if output_dir is not None:
        vis_nodes(output_dir)                      # V1: nodes and supports
    define_elements()
    define_load()
    if output_dir is not None:
        vis_model(output_dir)                      # V2: geometry
    return create_odb(odb_tag)


# ── 10. ANALYSIS ─────────────────────────────────────────────────────────────
def run_pushover(plate: bool, odb_tag: str, output_dir: Path = None) -> tuple:
    """Horizontal displacement control of the right top node (source PUSHOVER_ANALYSIS).

    The source's displacement control is set by its second integrator call (node 4, DOF 1), which overrides the first
    (node 3). Its convergence ladder sets NormDispIncr with KrylovNewton (initial stiffness), which is SmartAnalyze's
    code 41 here. The source records node 3 displacements and the summed base reactions.

    Returns:
        (odb, record): the ODB and the per-step arrays. The base reactions follow the source's sign convention.
    """
    odb = build_model(plate, odb_tag, output_dir)
    if output_dir is not None:
        vis_loads(output_dir)                      # V3: load vectors
        vis_pre_analysis(output_dir)               # V4: last check before the solver
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="NormDispIncr",
        testTol=max_tolerance,
        testIterTimes=max_iterations,
        tryAlterAlgoTypes=True,
        algoTypes=[41, 10, 40, 20, 50, 60],        # KrylovNewton (initial stiffness) first, as in the source ladder
        printPer=0,
        testPrintFlag=0,
    )
    keys = ("lam", "disp_x", "disp_y", "rot", "shear", "axial", "moment", "ks", "ka", "ki")
    record = {key: [] for key in keys}
    for k, seg in enumerate(analysis.static_split([dmax], maxStep=dincr)):
        ok = analysis.StaticAnalyze(node=NODE_TOP_R, dof=1, seg=seg)
        if ok < 0:
            break
        if k % odb_every == 0:
            odb.fetch_response_step()
        ops.reactions()
        shear = ops.nodeReaction(NODE_BASE_L, 1) + ops.nodeReaction(NODE_BASE_R, 1)
        axial = ops.nodeReaction(NODE_BASE_L, 2) + ops.nodeReaction(NODE_BASE_R, 2)
        moment = ops.nodeReaction(NODE_BASE_L, 3) + ops.nodeReaction(NODE_BASE_R, 3)
        dx = ops.nodeDisp(NODE_TOP_L, 1)
        dy = ops.nodeDisp(NODE_TOP_L, 2)
        rot = ops.nodeDisp(NODE_TOP_L, 3)
        with np.errstate(divide="ignore", invalid="ignore"):
            record["ks"].append(float(np.abs(np.float64(shear) / np.float64(dx))))
            record["ka"].append(float(np.abs(np.float64(axial) / np.float64(dy))))
            record["ki"].append(float(np.abs(np.float64(moment) / np.float64(rot))))
        record["lam"].append(ops.getTime())
        record["disp_x"].append(dx)
        record["disp_y"].append(dy)
        record["rot"].append(rot)
        record["shear"].append(shear)
        record["axial"].append(axial)
        record["moment"].append(moment)
    analysis.close()
    return odb, {key: np.array(value) for key, value in record.items()}


def bilinear_fit(disp: np.ndarray, shear: np.ndarray, slope_node: int = 10) -> tuple:
    """Equal-area bilinear fit of a base-shear curve (port of the source's BILNEAR_CURVE, same formulas).

    Returns:
        (X, Y, elastic stiffness, plastic stiffness, tangent stiffness, ductility ratio, over-strength factor).
    """
    size = len(shear)
    hh = np.zeros(size - 1)
    aa = np.zeros(size - 1)
    for i in range(size - 1):
        hh[i] = disp[i + 1] - disp[i]
        aa[i] = (shear[i] + shear[i + 1]) * 0.5 * hh[i]
    area = float(np.sum(aa))
    k0 = shear[slope_node] / disp[slope_node]
    last = size - 1
    fiy = (shear[last] * max(disp) * 0.5 - area) / (shear[last] * 0.5 - k0 * max(disp) * 0.5)
    my = k0 * fiy
    X = np.array([0.0, fiy, max(disp)])
    Y = np.array([0.0, my, shear[last]])
    return (X, Y, Y[1] / X[1], Y[2] / X[2], (Y[2] - Y[1]) / (X[2] - X[1]), X[2] / X[1], Y[2] / Y[1])


# ── 11. POST-PROCESSING ──────────────────────────────────────────────────────
def save_csv(output_dir: Path, name: str, columns: dict) -> None:
    """Write named columns to CSV (N, mm, N.mm, rad)."""
    table = np.column_stack([columns[key] for key in columns])
    np.savetxt(output_dir / name, table, delimiter=",", header=",".join(columns), comments="")


def run_columns(record: dict) -> dict:
    """Columns of one run, named as in the source's results export."""
    return {
        "load_factor": record["lam"],
        "DISP_X": record["disp_x"],
        "DISP_Y": record["disp_y"],
        "ROTATION": record["rot"],
        "AXIAL_FORCE": record["axial"],
        "SHEAR_FORCE": record["shear"],
        "MOMENT": record["moment"],
        "LATERAL_ST_X": record["ks"],
        "LATERAL_ST_Y": record["ka"],
        "ROTATIONAL_ST": record["ki"],
    }


def post_process(output_dir: Path, odbs: dict, wo: dict, w: dict, fit_wo: tuple, fit_w: tuple) -> None:
    """Write the CSV files and the bilinear results, the figures and the interactive views; flush the ODBs."""
    for odb in odbs.values():
        odb.save_response()
    save_csv(output_dir, "pushover_without_plate.csv", run_columns(wo))
    save_csv(output_dir, "pushover_with_plate.csv", run_columns(w))

    lines = []
    for label, record, fit in (("without plate", wo, fit_wo), ("with plate", w, fit_w)):
        X, Y, k_el, k_pl, k_tan, mu, omega = fit
        lines.append(f"{label}: bilinear fit X = {X[1]:.4f} mm, {X[2]:.4f} mm; Y = {Y[1]:.4f} N, {Y[2]:.4f} N")
        lines.append(f"{label}: elastic stiffness {k_el:.4f} N/mm; plastic stiffness {k_pl:.4f} N/mm; "
                     f"tangent stiffness {k_tan:.4f} N/mm")
        lines.append(f"{label}: over-strength factor (omega_0) = {omega:.4f}; displacement ductility (mu) = {mu:.4f}; "
                     f"R_mu = mu = {mu:.4f}; R = omega_0 R_mu = {omega * mu:.4f}")
        lines.append(f"{label}: largest base shear {np.max(np.abs(record['shear'])):.6e} N at "
                     f"{np.abs(record['disp_x'][np.argmax(np.abs(record['shear']))]):.4f} mm")
    (output_dir / "pushover_results.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    vis_curves(output_dir, [
        {"x": np.abs(wo["disp_x"]) / mm, "y": np.abs(wo["shear"]) / N, "xlabel": "Displacement in X (mm), node 3",
         "ylabel": "Base shear (N)", "title": "Without plate"},
        {"x": np.abs(w["disp_x"]) / mm, "y": np.abs(w["shear"]) / N, "xlabel": "Displacement in X (mm), node 3",
         "ylabel": "Base shear (N)", "title": "With plate"},
    ], filename="vis_08_pushover.html", title="Base shear vs displacement (source pushover)")

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 7), dpi=150)
    ax.plot(np.abs(wo["disp_x"]) / mm, np.abs(wo["shear"]) / N, color=COLORS["primary"], lw=1.8, label="without plate")
    ax.plot(np.abs(w["disp_x"]) / mm, np.abs(w["shear"]) / N, color=COLORS["secondary"], lw=1.8, ls="--", label="with plate")
    ax.plot(fit_wo[0], fit_wo[1], color="black", lw=1.0, ls=":", label="bilinear (without plate)")
    ax.plot(fit_w[0], fit_w[1], color="grey", lw=1.0, ls=":", label="bilinear (with plate)")
    _style_ax(ax, "Displacement in X (mm), node 3", "Base shear (N)", "Pushover: base shear vs displacement")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "pushover_curve.png")
    plt.close(fig)

    if ODB_PLATE in odbs:
        vis_defo(output_dir, filename="vis_05_deformed_pushover_with_plate.html", odb_tag=ODB_PLATE,
                 resp_dof="UX", resp_type="disp", scale=1.0)


# ── 12. VALIDATION (independent numpy checks) ───────────────────────────────
# 5-point Lobatto rule on [0, 1] as (positions, weights). This is the rule that matches OpenSees' force-based element.
LOBATTO = (np.array([0.0, (1 - np.sqrt(3 / 7)) / 2, 0.5, (1 + np.sqrt(3 / 7)) / 2, 1.0]),
           np.array([1 / 20, 49 / 180, 16 / 45, 49 / 180, 1 / 20]))
# 5-point Gauss-Legendre rule on [0, 1], for the sensitivity line in validation.txt.
GAUSS = (0.5 + 0.5 * np.array([-0.9061798459, -0.5384693101, 0.0, 0.5384693101, 0.9061798459]),
         0.5 * np.array([0.2369268851, 0.4786286705, 0.5688888889, 0.4786286705, 0.2369268851]))


def fibres(h: float, b: float, cover: float, area_bar: float, plate: bool, col: bool) -> tuple:
    """Fibre list of one section as (is_concrete, E0, A, y) arrays; y is the depth coordinate, in the plane of the frame.

    The geometry is that of define_fiber_section(). The initial tangents are the ones OpenSees uses at zero strain:
    Concrete01 E0 = 2 f'c / eps0 and Hysteretic E0 = f_y / eps_y (the plate's E0 = 240 / 0.02 = 12000 MPa, as written).
    """
    E0_core = 2.0 * fc_core / ec0_core
    E0_cover = 2.0 * fc_cover / ec0_cover
    E0_rebar = fy_rebar / ey_rebar
    E0_plate = fy_plate / ey_plate
    y1 = h / 2.0
    z1 = b / 2.0
    rows = []

    def patch(is_conc, E, n_y, n_z, y_i, z_i, y_j, z_j):
        dy = (y_j - y_i) / n_y
        dz = (z_j - z_i) / n_z
        for i in range(n_y):
            rows.extend([(is_conc, E, dy * dz, y_i + (i + 0.5) * dy)] * n_z)

    def bars(n, y_bar):
        rows.extend([(False, E0_rebar, area_bar, y_bar)] * n)

    patch(True, E0_core, NUM_FIBERS, NUM_FIBERS_Z, cover - y1, cover - z1, y1 - cover, z1 - cover)
    patch(True, E0_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, z1 - cover, y1, z1)
    patch(True, E0_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, -z1, y1, cover - z1)
    patch(True, E0_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, cover - z1, cover - y1, z1 - cover)
    patch(True, E0_cover, NUM_FIBERS, NUM_FIBERS_Z, y1 - cover, cover - z1, y1, z1 - cover)
    bars(3, y1 - cover)
    if not col:
        bars(2, 0.0)
    bars(3, cover - y1)
    t = t_plate
    if plate and col:
        patch(False, E0_plate, NUM_FIBERS, 2, -(y1 + t), z1, y1 + t, z1 + t)
        patch(False, E0_plate, NUM_FIBERS, 2, -(y1 + t), -z1 - t, y1 + t, -z1)
        patch(False, E0_plate, 2, NUM_FIBERS, -(y1 + t), -z1, -y1, z1)
        patch(False, E0_plate, 2, NUM_FIBERS, y1, -z1, y1 + t, z1)
    elif plate:
        patch(False, E0_plate, NUM_FIBERS, 2, -(y1 + t), -z1 - t, y1 + t, -z1)
    arr = np.array(rows, dtype=float)
    return arr[:, 0] > 0.5, arr[:, 1], arr[:, 2], arr[:, 3]


def section_state(sec: tuple, N_sec: float, M_sec: float) -> tuple:
    """Strain state (eps0, kappa), with eps(y) = eps0 + kappa * y, that gives the section forces N_sec and M_sec, and the
    section tangent D = [[EA, EB], [EB, EI]] at that state.

    Concrete fibres in tension carry no stress and no stiffness (Concrete01 has no tensile strength). The steel is elastic
    at the first step. Newton iteration on the piecewise-linear section response.
    """
    is_conc, E, A, y = sec
    EA = E * A
    x = np.linalg.solve(np.array([[EA.sum(), (EA * y).sum()], [(EA * y).sum(), (EA * y * y).sum()]]),
                        np.array([N_sec, M_sec]))
    for _ in range(200):
        eps = x[0] + x[1] * y
        Ea = EA * ((~is_conc) | (eps <= 0.0))
        res = np.array([(Ea * eps).sum(), (Ea * eps * y).sum()]) - np.array([N_sec, M_sec])
        jac = np.array([[Ea.sum(), (Ea * y).sum()], [(Ea * y).sum(), (Ea * y * y).sum()]])
        dx = np.linalg.solve(jac, -res)
        x = x + dx
        if np.max(np.abs(dx)) <= 1e-14 * max(1.0, np.max(np.abs(x))):
            break
    else:
        raise RuntimeError("section state did not converge")
    eps = x[0] + x[1] * y
    Ea = EA * ((~is_conc) | (eps <= 0.0))
    D = np.array([[Ea.sum(), (Ea * y).sum()], [(Ea * y).sum(), (Ea * y * y).sum()]])
    return x, D


def element_basic_stiffness(sec: tuple, L: float, q: np.ndarray, gross: bool, rule: tuple = LOBATTO) -> np.ndarray:
    """Basic stiffness (3 x 3) of a force-based element. The basic forces are q = [N, M_i, M_j]: N is constant and M(x) is
    linear between the end moments (no distributed loads). The section flexibility at each integration point is the inverse
    of the section tangent at the state of that point's section forces; gross=True uses the uncracked sections instead.
    """
    is_conc, E, A, y = sec
    EA = E * A
    flexibility = np.zeros((3, 3))
    for xi, w in zip(*rule):
        if gross:
            D = np.array([[EA.sum(), (EA * y).sum()], [(EA * y).sum(), (EA * y * y).sum()]])
        else:
            _, D = section_state(sec, q[0], q[1] * (1.0 - xi) + q[2] * xi)
        b = np.array([[1.0, 0.0, 0.0], [0.0, 1.0 - xi, xi]])
        flexibility += L * w * b.T @ np.linalg.inv(D) @ b
    return np.linalg.inv(flexibility)


def compatibility(L: float) -> np.ndarray:
    """Basic deformations (elongation; rotation of each end relative to the chord) from the local end displacements
    (u_i, v_i, theta_i, u_j, v_j, theta_j)."""
    return np.array([[-1.0, 0.0, 0.0, 1.0, 0.0, 0.0],
                     [0.0, 1.0 / L, 1.0, 0.0, -1.0 / L, 0.0],
                     [0.0, -1.0 / L, 0.0, 0.0, 1.0 / L, -1.0]])


def classic_element(EA: float, EI: float, L: float) -> np.ndarray:
    """Textbook 6 x 6 Euler-Bernoulli frame element in local coordinates (used by the element check)."""
    a, b1, b2, c1, c2 = EA / L, 12 * EI / L**3, 6 * EI / L**2, 4 * EI / L, 2 * EI / L
    return np.array([[a, 0, 0, -a, 0, 0],
                     [0, b1, b2, 0, -b1, b2],
                     [0, b2, c1, 0, -b2, c2],
                     [-a, 0, 0, a, 0, 0],
                     [0, -b1, -b2, 0, b1, -b2],
                     [0, b2, c2, 0, -b2, c1]])


def first_step_frame(plate: bool, gross: bool = False, rule: tuple = LOBATTO) -> tuple:
    """First displacement-control step of the frame in numpy, for the load pattern of define_load() (1 N per node).

    Each element is a force-based element whose section flexibilities follow the section states of the current solution;
    the states are updated until the displacements converge. gross=True keeps the uncracked sections (reference only).

    Returns:
        (load factor, displacements per unit load (N), number of iterations).
    """
    sec_col = fibres(h_col, b_col, cover_col, A_bar_col, plate, col=True)
    sec_beam = fibres(h_beam, b_beam, cover_beam, A_bar_beam, plate, col=False)
    pos = node_positions()
    elements = []
    for n_i, n_j, sec in ((NODE_BASE_L, NODE_TOP_L, sec_col), (NODE_BASE_R, NODE_TOP_R, sec_col),
                          (NODE_TOP_L, NODE_TOP_R, sec_beam)):
        xi, yi = pos[n_i]
        xj, yj = pos[n_j]
        L = float(np.hypot(xj - xi, yj - yi))
        c, s = (xj - xi) / L, (yj - yi) / L
        R = np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]])
        Tg = np.block([[R, np.zeros((3, 3))], [np.zeros((3, 3)), R]])
        dofs = [3 * (n_i - 1) + k for k in range(3)] + [3 * (n_j - 1) + k for k in range(3)]
        elements.append({"sec": sec, "L": L, "Tg": Tg, "dofs": dofs, "q": np.zeros(3)})
    force = np.zeros(12)
    for n in (NODE_TOP_L, NODE_TOP_R):
        force[3 * (n - 1)] = 1.0 * N
        force[3 * (n - 1) + 1] = -1.0 * N
    fixed = {3 * (n - 1) + k for n in (NODE_BASE_L, NODE_BASE_R) for k in range(3)}
    free = [d for d in range(12) if d not in fixed]
    u_prev = None
    for iteration in range(1, 101):
        K = np.zeros((12, 12))
        parts = []
        for e in elements:
            kb = element_basic_stiffness(e["sec"], e["L"], e["q"], gross, rule)
            Bc = compatibility(e["L"])
            K[np.ix_(e["dofs"], e["dofs"])] += e["Tg"].T @ (Bc.T @ kb @ Bc) @ e["Tg"]
            parts.append((kb, Bc))
        u = np.zeros(12)
        u[free] = np.linalg.solve(K[np.ix_(free, free)], force[free])
        for e, (kb, Bc) in zip(elements, parts):
            e["q"] = kb @ (Bc @ (e["Tg"] @ u[e["dofs"]]))
        if u_prev is not None and np.max(np.abs(u - u_prev)) <= 1e-12 * np.max(np.abs(u)):
            return dincr / mm / u[3 * (NODE_TOP_R - 1)], u, iteration
        u_prev = u
    raise RuntimeError("the first-step iteration did not converge")


def validate(output_dir: Path, wo: dict, w: dict) -> None:
    """Compare the OpenSees pushover runs with independent numpy calculations and write validation.txt.

    Checks: (1) the force-based element assembly, with uncracked sections, against the textbook frame element; (2) the
    first load factor and the first node-3 displacement of each run against the numpy frame with the cracked section
    states of the first step (the uncracked frame and a Gauss-Legendre variant are reported for reference); (3) the
    equilibrium of the base reactions with the applied loads at every step. The bilinear fits and the behaviour
    coefficients are outputs of the source's post-processing; they are reported, not validated.
    """
    report = []
    sec_col = fibres(h_col, b_col, cover_col, A_bar_col, False, col=True)
    EA_k = float(np.sum(sec_col[1] * sec_col[2]))
    EI_k = float(np.sum(sec_col[1] * sec_col[2] * sec_col[3] ** 2))
    Bc = compatibility(len_col)
    k_fibre = Bc.T @ element_basic_stiffness(sec_col, len_col, np.zeros(3), gross=True) @ Bc
    k_text = classic_element(EA_k, EI_k, len_col)
    report.append(f"element check: force-based element with uncracked sections vs textbook frame element, max relative "
                  f"difference {np.max(np.abs(k_fibre - k_text)) / np.max(np.abs(k_text)):.1e}")
    for label, plate, record in (("without plate", False, wo), ("with plate", True, w)):
        sec_c = fibres(h_col, b_col, cover_col, A_bar_col, plate, col=True)
        sec_b = fibres(h_beam, b_beam, cover_beam, A_bar_beam, plate, col=False)
        EA_c, EI_c = float(np.sum(sec_c[1] * sec_c[2])), float(np.sum(sec_c[1] * sec_c[2] * sec_c[3] ** 2))
        EA_b, EI_b = float(np.sum(sec_b[1] * sec_b[2])), float(np.sum(sec_b[1] * sec_b[2] * sec_b[3] ** 2))
        report.append(f"{label}: column EA = {EA_c:.6e} N, EI = {EI_c:.6e} N.mm^2; beam EA = {EA_b:.6e} N, "
                      f"EI = {EI_b:.6e} N.mm^2 (numpy, uncracked, initial tangents)")
        lam_c, u, n_it = first_step_frame(plate)
        lam_gl, _, _ = first_step_frame(plate, rule=GAUSS)
        lam_u, _, _ = first_step_frame(plate, gross=True)
        rel = abs(record["lam"][0] / lam_c - 1.0)
        report.append(f"{label}: first pushover step, load factor: OpenSees {record['lam'][0]:.6e}, cracked numpy "
                      f"{lam_c:.6e} (iterations {n_it}; relative difference {rel:.2e})")
        report.append(f"{label}: first step, reference only: Gauss-Legendre 5 points {lam_gl:.6e} (relative difference "
                      f"{abs(record['lam'][0] / lam_gl - 1.0):.2e}); uncracked numpy {lam_u:.6e}")
        disp = lam_c * u[3 * (NODE_TOP_L - 1)]
        report.append(f"{label}: first step, node 3 displacement X: OpenSees {record['disp_x'][0]:.6e} mm, cracked numpy "
                      f"{disp:.6e} mm (relative difference {abs(record['disp_x'][0] / disp - 1.0):.2e})")
        lam = record["lam"]
        res_shear = np.abs(record["shear"] + 2.0 * lam)
        res_axial = np.abs(record["axial"] - 2.0 * lam)
        report.append(f"{label}: equilibrium over {len(lam)} steps: max |shear + 2 lambda| / max(2 lambda) = "
                      f"{np.max(res_shear) / np.max(2.0 * lam):.2e}; max |axial - 2 lambda| / max(2 lambda) = "
                      f"{np.max(res_axial) / np.max(2.0 * lam):.2e}")
    (output_dir / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report:
        print(line)


# ── 13. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))        # before any CreateODB (AGENT.md §12ac)
    odb_wo, wo = run_pushover(False, ODB_NO_PLATE, output_dir)
    odb_w, w = run_pushover(True, ODB_PLATE, None)
    fit_wo = bilinear_fit(np.abs(wo["disp_x"]), np.abs(wo["shear"]))
    fit_w = bilinear_fit(np.abs(w["disp_x"]), np.abs(w["shear"]))
    post_process(output_dir, {ODB_NO_PLATE: odb_wo, ODB_PLATE: odb_w}, wo, w, fit_wo, fit_w)
    validate(output_dir, wo, w)
