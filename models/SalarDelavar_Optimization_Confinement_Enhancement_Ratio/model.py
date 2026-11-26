# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D reinforced-concrete frame, the frame of CONFINEMENT_NONCONSTANT_ELASTIC_OR_INELASTIC_FRAME: two 3 m columns
           (500 x 500 mm) and a 7 m beam (500 x 300 mm), both bases fixed. The confinement enhancement ratio of the column
           sections, Kc, is the unknown of the source's optimisation; the other sections keep the source's offsets (the middle
           column Kc - 0.15, the beam Kc - 0.1 and the middle beam Kc - 0.2). Corotational nonlinearBeamColumn elements with
           10 integration points (inelastic only, as in the source).
UniqueID : SalarDelavar_Optimization_Confinement_Enhancement_Ratio
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-25
Purpose  : Find the column confinement enhancement ratio whose pushover to 675 mm gives a structural ductility ratio of 5.5
           (source TARGET_DUCT), by the source's Newton iteration on F(X) = mu(X) - 5.5 with a finite-difference derivative
           (ESP = 1e-5, tolerance 1e-6, start X = 1.40). Then the pushover at the optimum is run and written out, with its
           bilinear fit (over-strength factor, displacement ductility and R).
Ref      : py_ref/CONCRETE_FRAME_OPTIMIZATION_CONFINEMENT_ENHANCEMENT_RATIO.py (source main), CONCRETE_SECTION_FUN_TWO.py
           (section), ANALYSIS_FUNCTION.py (its fallback ladder is replaced by SmartAnalyze), BILINEAR_CURVE.py, PLOT_2D.py
           (not run), SALAR_MATH.py (not imported by the source's main), COVER.png (reference figure).
           Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO/OPTIMIZATION_CONFINEMENT_ENHANCEMENT_RATIO
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import multiprocessing
import os
import shutil
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops
import opstool as opst

# models/<UniqueID>/model.py -> repository root is parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "standards"))
from units import *  # noqa: E402,F403  (N, mm, sec, MPa)
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
ODB_OPTIMUM = "optimum_pushover"
NODE_BASE_L, NODE_BASE_R = 1, 2
NODE_TOP_L, NODE_TOP_R = 3, 4                  # NODE_TOP_R is the pushover control node (DOF 1)
NODE_COL_L_1, NODE_COL_L_2 = 5, 6              # left column, intermediate nodes (source)
NODE_COL_R_1, NODE_COL_R_2 = 7, 8              # right column, intermediate nodes (source)
NODE_BEAM_1, NODE_BEAM_2 = 9, 10               # beam, intermediate nodes (source)
SEC_C01, SEC_C02 = 10, 20                      # column fibre sections (source secTagC01, secTagC02)
SEC_B01, SEC_B02 = 30, 40                      # beam fibre sections (source secTagB01, secTagB02)
MAT_OFFSET_CORE, MAT_OFFSET_COVER, MAT_OFFSET_STEEL = 100, 200, 300   # source: sec + 100, + 200, + 300
TRANSF = 1                                     # corotational transformation (source)
TS_LINEAR, PAT_LINEAR = 1, 1                   # Linear time series and pattern (pushover load, source tag 1)
NUM_INT_POINTS = 10                            # integration points per inelastic element (source numIntgrPts)
NUM_FIBERS = 40                                # fibres along the depth of each patch (source NUMFIBERS)
NUM_FIBERS_Z = 1                               # fibres across the width of each patch (1: the in-plane response does not depend on it, Note 2)


def odb_tag_for(iteration: int, which: str) -> str:
    """ODB tag of one pushover of the search: 'x' (at X), 'min' (at X - ESP) or 'max' (at X + ESP), in iteration
    `iteration` (counted from 1)."""
    return f"opt{iteration:02d}_{which}"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Concrete and reinforcing steel (source CONFINED_CONCRETE_SECTION; steel values of the source's STEEL_KIND 2)
fc = 25.0 * MPa                 # unconfined concrete compressive strength (source fc)
FY_STEEL = 4000.0 * MPa         # yield stress (source fy), as written
ES_STEEL = 2.0e5 * MPa          # modulus (source Es)
EY_STEEL = FY_STEEL / ES_STEEL  # yield strain (source ey)
FU_STEEL = 1.1818 * FY_STEEL    # ultimate stress (source fu)
ESU_STEEL = EY_STEEL * 75.2     # ultimate strain (source esu)
PINCH_X, PINCH_Y = 0.8, 0.5     # Hysteretic pinching factors (source)
DAMAGE_1, DAMAGE_2 = 0.0, 0.0   # Hysteretic damage factors (source)
BETA_HYS = 0.1                  # Hysteretic stiffness degradation (source beta)

# Column section (source Bc, Hc, coverC, DIAc): both sides 500 mm
B_COL = 500.0 * mm
H_COL = 500.0 * mm
COVER_COL = 50.0 * mm
DIA_COL = 25.0 * mm
A_BAR_COL = np.pi * DIA_COL**2 / 4.0
# Beam section (source Bb, Hb, coverB, DIAb): width Bb = 500 mm and depth Hb = 300 mm
B_BEAM = 500.0 * mm
H_BEAM = 300.0 * mm
COVER_BEAM = 50.0 * mm
DIA_BEAM = 18.0 * mm
A_BAR_BEAM = np.pi * DIA_BEAM**2 / 4.0
LENGTH_COL = 3000.0 * mm        # source LENGTH_COL
LENGTH_BEAM = 7000.0 * mm       # source LENGTH_BM
# Element masses per unit length, as written in the source (no effect on a static pushover)
MASS_PER_LENGTH_COL = B_COL * H_COL * 0.000025
MASS_PER_LENGTH_BEAM = B_BEAM * H_BEAM * 0.000025

# Pushover (source)
DMAX = 675.0 * mm               # maximum displacement (source DMAX)
DINCR = 0.05 * mm               # displacement increment (source DINCR): 13500 steps
MAX_ITERATIONS = 5000           # convergence iterations (source MAX_ITERATIONS)
MAX_TOLERANCE = 1.0e-6          # convergence tolerance (source MAX_TOLERANCE)
ODB_EVERY_PUSHOVER = 20         # ODB fetch every 20 pushover steps (AGENT.md §3d)

# Optimisation (source, FIND THE BEST CONCRETE COLUMN CONFINEMENT ENHANCEMENT RATIO)
KC_START = 1.40                 # initial guess of the column confinement ratio (source X = Kc)
TARGET_DUCT = 5.5               # target structural ductility ratio (source TARGET_DUCT)
ESP = 1.0e-5                    # finite-difference step of the derivative (source ESP)
TOLERANCE = 1.0e-6              # convergence tolerance on the Newton step (source TOLERANCE)
ITMAX = 100000                  # maximum number of iterations (source ITMAX)
SEARCH_WORKERS = 3              # the three pushovers of one iteration run in separate processes (Note 3)


def concrete_parameters(kc: float) -> dict:
    """Concrete01 parameters of the source's CONFINED_CONCRETE_SECTION for the confinement ratio kc. The cover is the
    unconfined concrete (fc); the core takes the ratio kc."""
    fc_u = -fc                                     # unconfined peak stress (negative in compression)
    ec0_u = -0.002 * (abs(fc_u) / 30.0) ** 0.25    # strain at the peak (semi-empirical, source)
    fcu_u = 0.1 * fc_u                             # ultimate stress
    ecu_u = ec0_u * 3.5                            # ultimate strain
    fc_c = fc_u * kc                               # confined peak stress
    ec0_c = ec0_u * 1.8                            # confined strain at the peak
    fcu_c = 0.95 * fc_c                            # confined ultimate stress
    ecu_c = 1.475 * ecu_u * kc                     # confined ultimate strain
    return {"fc_u": fc_u, "ec0_u": ec0_u, "fcu_u": fcu_u, "ecu_u": ecu_u,
            "fc_c": fc_c, "ec0_c": ec0_c, "fcu_c": fcu_c, "ecu_c": ecu_c}


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Start a fresh 2D model with three DOFs per node (ux, uy, rotation)."""
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)


# ── 5. NODES AND SUPPORTS ────────────────────────────────────────────────────
def node_positions() -> dict:
    """Source node coordinates (mm): corners 1 to 4, column nodes at thirds of the column height, beam nodes at 1/7 and
    6/7 of the span."""
    return {
        NODE_BASE_L: (0.0, 0.0),
        NODE_BASE_R: (LENGTH_BEAM, 0.0),
        NODE_TOP_L: (0.0, LENGTH_COL),
        NODE_TOP_R: (LENGTH_BEAM, LENGTH_COL),
        NODE_COL_L_1: (0.0, LENGTH_COL / 3.0),
        NODE_COL_L_2: (0.0, 2.0 * LENGTH_COL / 3.0),
        NODE_COL_R_1: (LENGTH_BEAM, LENGTH_COL / 3.0),
        NODE_COL_R_2: (LENGTH_BEAM, 2.0 * LENGTH_COL / 3.0),
        NODE_BEAM_1: (LENGTH_BEAM / 7.0, LENGTH_COL),
        NODE_BEAM_2: (6.0 * LENGTH_BEAM / 7.0, LENGTH_COL),
    }


def define_nodes_and_supports() -> None:
    """Ten nodes and the fixed bases (source ops.fix(1, 1, 1, 1) and ops.fix(2, 1, 1, 1))."""
    for tag, (x, y) in node_positions().items():
        ops.node(tag, x, y)
    ops.fix(NODE_BASE_L, 1, 1, 1)
    ops.fix(NODE_BASE_R, 1, 1, 1)


# ── 6. SECTIONS (MATERIALS AND FIBRES) ───────────────────────────────────────
def section_spec(kc: float) -> dict:
    """Confined fibre sections of the source for the column ratio kc, as its CONFINED_CONCRETE_SECTION calls give them:
    tag -> (depth h, width b, cover, bar area, confinement ratio, column flag). The columns take kc and kc - 0.15, the beams
    kc - 0.1 and kc - 0.2."""
    return {
        SEC_C01: (H_COL, B_COL, COVER_COL, A_BAR_COL, kc, True),
        SEC_C02: (H_COL, B_COL, COVER_COL, A_BAR_COL, kc - 0.15, True),
        SEC_B01: (H_BEAM, B_BEAM, COVER_BEAM, A_BAR_BEAM, kc - 0.1, False),
        SEC_B02: (H_BEAM, B_BEAM, COVER_BEAM, A_BAR_BEAM, kc - 0.2, False),
    }


def define_fiber_section(sec_tag: int, h: float, b: float, cover: float, area_bar: float, kc: float, col: bool) -> None:
    """Confined fibre section of the source (CONFINED_CONCRETE_SECTION). Each section has its own materials, as in the
    source: core (sec + 100, Concrete01 with kc), cover (sec + 200, Concrete01, unconfined) and steel (sec + 300,
    Hysteretic). Column: three bars on each face. Beam (col = False): plus a middle layer of two bars.
    """
    p = concrete_parameters(kc)
    tag_core = sec_tag + MAT_OFFSET_CORE
    tag_cover = sec_tag + MAT_OFFSET_COVER
    tag_steel = sec_tag + MAT_OFFSET_STEEL
    ops.uniaxialMaterial("Hysteretic", tag_steel, FY_STEEL, EY_STEEL, FU_STEEL, ESU_STEEL,
                         0.2 * FU_STEEL, 1.1 * ESU_STEEL, -FY_STEEL, -EY_STEEL, -FU_STEEL, -ESU_STEEL,
                         -0.2 * FU_STEEL, -1.1 * ESU_STEEL, PINCH_X, PINCH_Y, DAMAGE_1, DAMAGE_2, BETA_HYS)
    ops.uniaxialMaterial("Concrete01", tag_core, p["fc_c"], p["ec0_c"], p["fcu_c"], p["ecu_c"])
    ops.uniaxialMaterial("Concrete01", tag_cover, p["fc_u"], p["ec0_u"], p["fcu_u"], p["ecu_u"])
    y1 = h / 2.0
    z1 = b / 2.0
    ops.section("Fiber", sec_tag)
    ops.patch("rect", tag_core, NUM_FIBERS, NUM_FIBERS_Z, cover - y1, cover - z1, y1 - cover, z1 - cover)
    ops.patch("rect", tag_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, z1 - cover, y1, z1)
    ops.patch("rect", tag_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, -z1, y1, cover - z1)
    ops.patch("rect", tag_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, cover - z1, cover - y1, z1 - cover)
    ops.patch("rect", tag_cover, NUM_FIBERS, NUM_FIBERS_Z, y1 - cover, cover - z1, y1, z1 - cover)
    ops.layer("straight", tag_steel, 3, area_bar, y1 - cover, z1 - cover, y1 - cover, cover - z1)
    if not col:
        ops.layer("straight", tag_steel, 2, area_bar, 0.0, z1 - cover, 0.0, cover - z1)
    ops.layer("straight", tag_steel, 3, area_bar, cover - y1, z1 - cover, cover - y1, cover - z1)


def define_sections(kc: float) -> None:
    """The four fibre sections of the source for the column ratio kc."""
    for sec_tag, (h, b, cover, area_bar, kc_sec, col) in section_spec(kc).items():
        define_fiber_section(sec_tag, h, b, cover, area_bar, kc_sec, col)


# ── 7. ELEMENTS ──────────────────────────────────────────────────────────────
# (tag, start node, end node, section, mass per unit length), as in the source's element list
ELEMENTS = (
    (1, NODE_BASE_L, NODE_COL_L_1, SEC_C01, MASS_PER_LENGTH_COL),
    (2, NODE_COL_L_1, NODE_COL_L_2, SEC_C02, MASS_PER_LENGTH_COL),
    (3, NODE_COL_L_2, NODE_TOP_L, SEC_C01, MASS_PER_LENGTH_COL),
    (4, NODE_BASE_R, NODE_COL_R_1, SEC_C01, MASS_PER_LENGTH_COL),
    (5, NODE_COL_R_1, NODE_COL_R_2, SEC_C02, MASS_PER_LENGTH_COL),
    (6, NODE_COL_R_2, NODE_TOP_R, SEC_C01, MASS_PER_LENGTH_COL),
    (7, NODE_TOP_L, NODE_BEAM_1, SEC_B01, MASS_PER_LENGTH_BEAM),
    (8, NODE_BEAM_1, NODE_BEAM_2, SEC_B02, MASS_PER_LENGTH_BEAM),
    (9, NODE_BEAM_2, NODE_TOP_R, SEC_B01, MASS_PER_LENGTH_BEAM),
)


def define_elements() -> None:
    """The nine elements of the source: corotational nonlinearBeamColumn with 10 integration points."""
    ops.geomTransf("Corotational", TRANSF)
    for tag, ni, nj, sec, mass in ELEMENTS:
        ops.element("nonlinearBeamColumn", tag, ni, nj, NUM_INT_POINTS, sec, TRANSF, "-mass", mass)


# ── 8. OUTPUT DATABASE (ODB) ─────────────────────────────────────────────────
def create_odb(odb_tag) -> "opst.post.CreateODB":
    """Nodal responses for one analysis. The model data are saved here, after the elements are defined.

    Args:
        odb_tag: Tag of this analysis (one ODB per analysis, because each analysis rebuilds the model).

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


def build_model(kc: float, odb_tag, output_dir: Path = None):
    """Build the frame for one analysis at the column ratio kc. The V1 and V2 stages are written when output_dir is given.

    Returns:
        The CreateODB instance.
    """
    init_model()
    define_nodes_and_supports()
    define_sections(kc)
    if output_dir is not None:
        vis_nodes(output_dir)                      # V1: nodes and supports
    define_elements()
    if output_dir is not None:
        vis_model(output_dir)                      # V2: geometry
    return create_odb(odb_tag)


# ── 9. LOADING ───────────────────────────────────────────────────────────────
def define_push_load() -> None:
    """Reference load of the pushover (source: 1 N horizontal and -1 N vertical at nodes 3 and 4). The displacement
    control sets the load factor."""
    ops.timeSeries("Linear", TS_LINEAR)
    ops.pattern("Plain", PAT_LINEAR, TS_LINEAR)
    ops.load(NODE_TOP_L, 1.0 * N, -1.0 * N, 0.0)
    ops.load(NODE_TOP_R, 1.0 * N, -1.0 * N, 0.0)


# ── 10. ANALYSIS ─────────────────────────────────────────────────────────────
def run_pushover(kc: float, odb_tag: str, output_dir: Path = None) -> tuple:
    """Horizontal displacement control of node 4 (DOF 1) to DMAX through SmartAnalyze (source PD_ANALYSIS, PUSHOVER) for
    the column ratio kc.

    Returns:
        (odb, history): the ODB and the per-step arrays. The base reactions keep the source's sign (no minus).
    """
    odb = build_model(kc, odb_tag, output_dir)
    define_push_load()
    if output_dir is not None:
        vis_loads(output_dir)                      # V3: load vectors
        vis_pre_analysis(output_dir)               # V4: last check before the solver
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="NormDispIncr",
        testTol=MAX_TOLERANCE,
        testIterTimes=MAX_ITERATIONS,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 41, 40, 20, 50, 60],        # Newton first, then the fallback ladder of the source's solver
        printPer=0,
        testPrintFlag=0,
    )
    keys = ("lam", "disp_x", "disp_y", "rot", "shear", "axial", "moment", "ks", "ka", "ki", "drift_x", "drift_y")
    history = {key: [] for key in keys}
    for k, seg in enumerate(analysis.static_split([DMAX], maxStep=DINCR)):
        ok = analysis.StaticAnalyze(node=NODE_TOP_R, dof=1, seg=seg)
        if ok < 0:
            break
        if k % ODB_EVERY_PUSHOVER == 0:
            odb.fetch_response_step()
        ops.reactions()
        shear = ops.nodeReaction(NODE_BASE_L, 1) + ops.nodeReaction(NODE_BASE_R, 1)
        axial = ops.nodeReaction(NODE_BASE_L, 2) + ops.nodeReaction(NODE_BASE_R, 2)
        moment = ops.nodeReaction(NODE_BASE_L, 3) + ops.nodeReaction(NODE_BASE_R, 3)
        dx = ops.nodeDisp(NODE_TOP_L, 1)
        dy = ops.nodeDisp(NODE_TOP_L, 2)
        rot = ops.nodeDisp(NODE_TOP_L, 3)
        with np.errstate(divide="ignore", invalid="ignore"):
            history["ks"].append(float(np.abs(np.float64(shear) / np.float64(dx))))
            history["ka"].append(float(np.abs(np.float64(axial) / np.float64(dy))))
            history["ki"].append(float(np.abs(np.float64(moment) / np.float64(rot))))
        history["lam"].append(ops.getTime())
        history["disp_x"].append(dx)
        history["disp_y"].append(dy)
        history["rot"].append(rot)
        history["shear"].append(shear)
        history["axial"].append(axial)
        history["moment"].append(moment)
        history["drift_x"].append(100.0 * dx / LENGTH_COL)
        history["drift_y"].append(100.0 * dy / LENGTH_BEAM)
    analysis.close()
    return odb, {key: np.array(value) for key, value in history.items()}


def search_worker(job: tuple, result_file: str) -> None:
    """One pushover of the search, run in its own process (see run_search_jobs). job = (kc, odb_tag, output_dir). The ODB
    is written and saved here, after the analysis (not inside its step loop). The ductility ratio of the bilinear fit (source
    formula), the over-strength factor and the step arrays are saved to result_file."""
    kc, odb_tag, output_dir = job
    opst.post.set_odb_path(output_dir)            # before any CreateODB (AGENT.md §12ac), in this process
    odb, history = run_pushover(kc, odb_tag, None)
    odb.save_response()
    if len(history["lam"]) != round(DMAX / DINCR):
        raise RuntimeError(f"pushover {odb_tag} stopped after {len(history['lam'])} of {round(DMAX / DINCR)} steps")
    fit = bilinear_fit(np.abs(history["disp_x"]), np.abs(history["shear"]))
    np.savez(result_file, mu=fit[5], omega=fit[6], **history)


def run_search_jobs(jobs: list, output_dir: Path) -> list:
    """Run the pushovers of one search iteration in separate processes, one per job. opstool's set_odb_path removes the
    '.opstool.output' folder of the process's working folder, and that folder is fixed when opstool is imported, so
    processes that share a working folder fail with PermissionError (LESSON 85). Each process is therefore started from its
    own working folder under output/.work. Returns one dict per job, in order."""
    ctx = multiprocessing.get_context("spawn")
    work_root = output_dir / ".work"
    original = os.getcwd()
    procs, results_files = [], []
    try:
        for kc, odb_tag, out in jobs:
            work = work_root / odb_tag
            work.mkdir(parents=True, exist_ok=True)
            result_file = work_root / f"{odb_tag}.npz"
            os.chdir(work)                         # the new process inherits this working folder when it starts
            proc = ctx.Process(target=search_worker, args=((kc, odb_tag, out), str(result_file)))
            proc.start()
            procs.append(proc)
            results_files.append(result_file)
            os.chdir(original)
        for proc in procs:
            proc.join()
    finally:
        os.chdir(original)
    results = []
    for (kc, odb_tag, _), proc, result_file in zip(jobs, procs, results_files):
        if proc.exitcode != 0:
            raise RuntimeError(f"pushover {odb_tag} failed in its process (exit code {proc.exitcode})")
        with np.load(result_file) as data:
            history = {key: data[key] for key in ("lam", "disp_x", "disp_y", "rot", "shear", "axial", "moment",
                                                  "ks", "ka", "ki", "drift_x", "drift_y")}
            results.append({"kc": kc, "tag": odb_tag, "mu": float(data["mu"]), "omega": float(data["omega"]),
                            "history": history})
    shutil.rmtree(work_root, ignore_errors=True)
    return results


def load_search_history(output_dir: Path) -> list:
    """The Newton iterations already completed by an earlier, interrupted run (the rows of search_history.csv), so that the
    search continues from the last one. Returns [] when there is no history."""
    path = output_dir / "search_history.csv"
    if not path.exists() or path.stat().st_size == 0:
        return []
    table = np.genfromtxt(path, delimiter=",", names=True, ndmin=1)
    keys = ("iteration", "X", "mu", "F", "F_min", "F_max", "DF", "DX", "residual", "X_new")
    return [{key: float(table[key][i]) for key in keys} for i in range(len(table))]


def clear_incomplete_iteration(output_dir: Path, iteration: int) -> None:
    """Remove the ODB files of an iteration that an interrupted run started but did not complete."""
    for path in output_dir.glob(f"*opt{iteration:02d}_*"):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def find_optimum(output_dir: Path) -> tuple:
    """The source's Newton iteration: F(X) = mu(X) - TARGET_DUCT, with the derivative from the pushovers at X - ESP and
    X + ESP. The three pushovers of an iteration run in separate processes (run_search_jobs). The source's update is kept:
    DX = F / DF, X = X - DX, RESIDUAL = |DX|. Every completed iteration is written to search_history.csv at once, and an
    interrupted run continues from its last completed iteration.

    Returns:
        (X*, rows): the converged column ratio and one row per iteration.
    """
    rows = load_search_history(output_dir)
    if rows:
        x, residual, it = rows[-1]["X_new"], rows[-1]["residual"], len(rows)
        clear_incomplete_iteration(output_dir, it + 1)
    else:
        x, residual, it = KC_START, 100.0, 0          # source RESIDUAL = 100
    while residual > TOLERANCE:
        k = it + 1
        jobs = [(x, odb_tag_for(k, "x"), str(output_dir)),
                (x - ESP, odb_tag_for(k, "min"), str(output_dir)),
                (x + ESP, odb_tag_for(k, "max"), str(output_dir))]
        res_x, res_min, res_max = run_search_jobs(jobs, output_dir)
        f = res_x["mu"] - TARGET_DUCT
        f_min = res_min["mu"] - TARGET_DUCT
        f_max = res_max["mu"] - TARGET_DUCT
        df = (f_max - f_min) / (2.0 * ESP)
        dx = f / df
        residual = abs(dx)
        x_old = x
        x = x - dx
        it += 1
        rows.append({"iteration": it, "X": x_old, "mu": res_x["mu"], "F": f, "F_min": f_min, "F_max": f_max,
                     "DF": df, "DX": dx, "residual": residual, "X_new": x})
        save_csv(output_dir, "search_history.csv", search_columns(rows))
        if it == ITMAX:
            raise RuntimeError("the search reached the maximum number of iterations (ITMAX) without converging")
    return x, rows


# ── 11. POST-PROCESSING ──────────────────────────────────────────────────────
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


def save_csv(output_dir: Path, name: str, columns: dict) -> None:
    """Write named columns to CSV (N, mm, s, rad)."""
    table = np.column_stack([columns[key] for key in columns])
    np.savetxt(output_dir / name, table, delimiter=",", header=",".join(columns), comments="")


def pushover_columns(push: dict) -> dict:
    """Pushover columns, named as in the first sub-model's results (the source does not export its pushover)."""
    return {"load_factor": push["lam"], "DISP_X": push["disp_x"], "DISP_Y": push["disp_y"],
            "ROTATION": push["rot"], "AXIAL_FORCE": push["axial"], "SHEAR_FORCE": push["shear"],
            "MOMENT": push["moment"], "LATERAL_ST_X": push["ks"], "LATERAL_ST_Y": push["ka"],
            "ROTATIONAL_ST": push["ki"], "DRIFT_X": push["drift_x"], "DRIFT_Y": push["drift_y"]}


def search_columns(rows: list) -> dict:
    """The iteration table of the search, one row per Newton iteration."""
    keys = ("iteration", "X", "mu", "F", "F_min", "F_max", "DF", "DX", "residual", "X_new")
    return {key: np.array([row[key] for row in rows], dtype=float) for key in keys}


def write_results(output_dir: Path, kc_star: float, fit: tuple, rows: list) -> None:
    """Text summary of the optimum: the column ratios, the iteration count and the ductility at the optimum, and the
    behaviour coefficients of its bilinear fit (source formulas)."""
    X, Y, k_el, k_pl, k_tan, mu, omega = fit
    lines = [
        f"optimum column confinement enhancement ratio X* = {kc_star:.6f} (source Kc, the optimisation variable)",
        f"optimum middle column ratio X* - 0.15 = {kc_star - 0.15:.6f}; beam ratio X* - 0.1 = {kc_star - 0.1:.6f}; "
        f"middle beam ratio X* - 0.2 = {kc_star - 0.2:.6f}",
        f"iterations: {len(rows)}; last Newton step |DX| = {rows[-1]['residual']:.3e} (tolerance {TOLERANCE:.0e}); "
        f"start X = {KC_START:.2f}; target ductility ratio {TARGET_DUCT}",
        f"ductility ratio at X* (bilinear fit, source formula) mu = {mu:.6f}; mu - target = {mu - TARGET_DUCT:.3e}",
        f"over-strength factor (Omega_0) = {omega:.4f}; displacement ductility (mu) = {mu:.4f}; "
        f"R = Omega_0 mu = {omega * mu:.4f}",
        f"bilinear fit (X): X = {X[1]:.4f} mm, {X[2]:.4f} mm; Y = {Y[1]:.4f} N, {Y[2]:.4f} N; elastic stiffness "
        f"{k_el:.4f} N/mm; plastic {k_pl:.4f} N/mm; tangent {k_tan:.4f} N/mm",
    ]
    (output_dir / "optimisation_results.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_figures(output_dir: Path, push: dict, fit: tuple, rows: list) -> None:
    """Two PNG figures: the pushover at the optimum with its bilinear fit, and the Newton residuals of the search."""
    import matplotlib.pyplot as plt

    X, Y = fit[0], fit[1]
    fig, ax = plt.subplots(figsize=(10, 7), dpi=150)
    ax.plot(np.abs(push["disp_x"]) / mm, np.abs(push["shear"]) / N, color=COLORS["secondary"], lw=1.8, label="optimum")
    ax.plot(X / mm, Y / N, color="black", lw=1.0, ls=":", label="bilinear (optimum)")
    _style_ax(ax, "Displacement in X (mm), node 3", "Base shear (N)", "Pushover at the optimum column ratio")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "pushover_curve.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    its = [row["iteration"] for row in rows]
    ax.semilogy(its, [max(row["residual"], 1e-16) for row in rows], marker="o", color=COLORS["primary"])
    _style_ax(ax, "Newton iteration", "|DX| (confinement ratio)", "Newton step of the optimum search")
    fig.tight_layout()
    fig.savefig(output_dir / "search_residual.png")
    plt.close(fig)


def post_process(output_dir: Path, odb, push: dict, kc_star: float, fit: tuple, rows: list) -> None:
    """Write the CSV files, the results, the figures and the interactive views; flush the ODB."""
    odb.save_response()
    save_csv(output_dir, "pushover_optimum.csv", pushover_columns(push))
    save_csv(output_dir, "search_history.csv", search_columns(rows))
    write_results(output_dir, kc_star, fit, rows)
    plot_figures(output_dir, push, fit, rows)
    vis_curves(output_dir, [
        {"x": np.abs(push["disp_x"]) / mm, "y": np.abs(push["shear"]) / N,
         "xlabel": "Displacement in X (mm), node 3", "ylabel": "Base shear (N)", "title": "Optimum"},
    ], filename="vis_08_pushover.html", title="Base shear vs displacement at the optimum column ratio")
    vis_defo(output_dir, filename="vis_05_deformed_optimum.html", odb_tag=ODB_OPTIMUM,
             resp_dof="UX", resp_type="disp", scale=1.0)


# ── 12. VALIDATION (independent numpy calculations) ─────────────────────────
def lobatto_rule(n: int) -> tuple:
    """n-point Lobatto rule on [0, 1] as (positions, weights): the endpoints and the roots of P'_(n-1) on [-1, 1]. This is
    the rule of OpenSees' Lobatto integration of nonlinearBeamColumn."""
    coef = np.zeros(n)
    coef[n - 1] = 1.0                                       # Legendre polynomial P_(n-1)
    interior = np.polynomial.legendre.legroots(np.polynomial.legendre.legder(coef))
    x = np.concatenate(([-1.0], np.sort(interior), [1.0]))
    weight = 2.0 / (n * (n - 1) * np.polynomial.legendre.legval(x, coef) ** 2)
    return (x + 1.0) / 2.0, weight / 2.0


LOBATTO_RULE = lobatto_rule(NUM_INT_POINTS)
NDOF = 3 * len(node_positions())                            # ten nodes, three DOFs each


def frame_dof(node: int, k: int) -> int:
    """Global DOF index of DOF k (0 ux, 1 uy, 2 rotation) of a node."""
    return 3 * (node - 1) + k


def section_fibres(sec_tag: int, kc: float) -> tuple:
    """Fibre list (is_concrete, E0, A, y) of a section for the column ratio kc, from the geometry of define_fiber_section and
    the initial tangents (Concrete01 E0 = 2 f'c / eps0; Hysteretic E0 = f_y / eps_y). Independent of OpenSees."""
    h, b, cover, area_bar, kc_sec, col = section_spec(kc)[sec_tag]
    p = concrete_parameters(kc_sec)
    E_core = 2.0 * p["fc_c"] / p["ec0_c"]
    E_cover = 2.0 * p["fc_u"] / p["ec0_u"]
    E_steel = FY_STEEL / EY_STEEL
    y1 = h / 2.0
    z1 = b / 2.0
    rows = []

    def patch(is_conc, E, n_y, n_z, y_i, z_i, y_j, z_j):
        dy = (y_j - y_i) / n_y
        dz = (z_j - z_i) / n_z
        for i in range(n_y):
            rows.extend([(is_conc, E, dy * dz, y_i + (i + 0.5) * dy)] * n_z)

    def bars(n, y_bar):
        rows.extend([(False, E_steel, area_bar, y_bar)] * n)

    patch(True, E_core, NUM_FIBERS, NUM_FIBERS_Z, cover - y1, cover - z1, y1 - cover, z1 - cover)
    patch(True, E_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, z1 - cover, y1, z1)
    patch(True, E_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, -z1, y1, cover - z1)
    patch(True, E_cover, NUM_FIBERS, NUM_FIBERS_Z, -y1, cover - z1, cover - y1, z1 - cover)
    patch(True, E_cover, NUM_FIBERS, NUM_FIBERS_Z, y1 - cover, cover - z1, y1, z1 - cover)
    bars(3, y1 - cover)
    if not col:
        bars(2, 0.0)
    bars(3, cover - y1)
    arr = np.array(rows, dtype=float)
    return arr[:, 0] > 0.5, arr[:, 1], arr[:, 2], arr[:, 3]


def section_state(sec: tuple, N_sec: float, M_sec: float) -> tuple:
    """Strain state (eps0, kappa), with eps(y) = eps0 + kappa * y, that gives the section forces N_sec and M_sec, and the
    tangent D = [[EA, EB], [EB, EI]] at that state. Concrete fibres in tension carry no stress and no stiffness
    (Concrete01 has no tensile strength). Newton iteration on the piecewise-linear section response."""
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


def element_geometry(pos: dict, ni: int, nj: int) -> tuple:
    """Length and direction cosines (c, s) of an element from its start to its end node."""
    (xi, yi), (xj, yj) = pos[ni], pos[nj]
    L = float(np.hypot(xj - xi, yj - yi))
    return L, (xj - xi) / L, (yj - yi) / L


def transform(c: float, s: float) -> np.ndarray:
    """6 x 6 rotation from global to local end displacements (ux, uy, rotation at each end)."""
    R = np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]])
    Tg = np.zeros((6, 6))
    Tg[:3, :3] = R
    Tg[3:, 3:] = R
    return Tg


def classic_element(EA: float, EI: float, L: float) -> np.ndarray:
    """Textbook 6 x 6 Euler-Bernoulli frame element in local coordinates (used by the element check)."""
    a, b1, b2, c1, c2 = EA / L, 12 * EI / L**3, 6 * EI / L**2, 4 * EI / L, 2 * EI / L
    return np.array([[a, 0, 0, -a, 0, 0],
                     [0, b1, b2, 0, -b1, b2],
                     [0, b2, c1, 0, -b2, c2],
                     [-a, 0, 0, a, 0, 0],
                     [0, -b1, -b2, 0, b1, -b2],
                     [0, b2, c2, 0, -b2, c1]])


def compatibility(L: float) -> np.ndarray:
    """Basic deformations (elongation; rotation of each end relative to the chord) from the local end displacements."""
    return np.array([[-1.0, 0.0, 0.0, 1.0, 0.0, 0.0],
                     [0.0, 1.0 / L, 1.0, 0.0, -1.0 / L, 0.0],
                     [0.0, -1.0 / L, 0.0, 0.0, 1.0 / L, -1.0]])


def element_basic_stiffness(sec: tuple, L: float, q: np.ndarray, gross: bool, rule: tuple) -> np.ndarray:
    """Basic stiffness (3 x 3) of a force-based element. The basic forces are q = [N, M_i, M_j]: N is constant and M(x) is
    linear between the end moments (no distributed loads). The section flexibility at each integration point is the
    inverse of the section tangent at the state of that point's section forces; gross=True uses the uncracked section."""
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


def first_step_frame(kc: float, gross: bool, rule: tuple) -> tuple:
    """First displacement-control step of the frame in numpy for the column ratio kc, for the pushover load (1 N horizontal
    and -1 N vertical at the top nodes). Each element is a force-based element whose section flexibilities follow the
    section states of the current solution, iterated to convergence; gross=True keeps the uncracked sections. The restrained
    DOFs are those of the two fixed bases.

    Returns:
        (load factor, displacements per unit load, number of iterations).
    """
    pos = node_positions()
    elements = []
    for tag, ni, nj, sec, _ in ELEMENTS:
        L, c, s = element_geometry(pos, ni, nj)
        dofs = [frame_dof(ni, k) for k in range(3)] + [frame_dof(nj, k) for k in range(3)]
        elements.append({"sec": section_fibres(sec, kc), "L": L, "T": transform(c, s), "dofs": dofs, "q": np.zeros(3)})
    force = np.zeros(NDOF)
    for n in (NODE_TOP_L, NODE_TOP_R):
        force[frame_dof(n, 0)] = 1.0 * N
        force[frame_dof(n, 1)] = -1.0 * N
    fixed = {frame_dof(n, k) for n in (NODE_BASE_L, NODE_BASE_R) for k in range(3)}
    free = [d for d in range(NDOF) if d not in fixed]
    u_prev = None
    for iteration in range(1, 101):
        K = np.zeros((NDOF, NDOF))
        parts = []
        for e in elements:
            kb = element_basic_stiffness(e["sec"], e["L"], e["q"], gross, rule)
            Bc = compatibility(e["L"])
            K[np.ix_(e["dofs"], e["dofs"])] += e["T"].T @ (Bc.T @ kb @ Bc) @ e["T"]
            parts.append((kb, Bc))
        u = np.zeros(NDOF)
        u[free] = np.linalg.solve(K[np.ix_(free, free)], force[free])
        for e, (kb, Bc) in zip(elements, parts):
            e["q"] = kb @ (Bc @ (e["T"] @ u[e["dofs"]]))
        if u_prev is not None and np.max(np.abs(u - u_prev)) <= 1e-12 * np.max(np.abs(u)):
            return (DINCR / mm) / u[frame_dof(NODE_TOP_R, 0)], u, iteration
        u_prev = u
    raise RuntimeError("the first-step iteration did not converge")


def validate(output_dir: Path, kc_star: float, push: dict, fit: tuple, rows: list) -> None:
    """Compare the OpenSees pushover at the optimum with independent numpy calculations and check the search; write
    validation.txt.

    Checks: (1) the force-based element of the column section at X* against the textbook frame element; (2) the first
    pushover step at X* (section states, 10 Lobatto points) and the equilibrium of the base reactions at every step; (3) the
    ductility at X* against the target, and the last Newton step of the search. The bilinear fit and the behaviour
    coefficients are the source's formulas, ported, and are reported, not validated.
    """
    report = []
    sec_c = section_fibres(SEC_C01, kc_star)
    _, E_c, A_c, y_c = sec_c
    EA_c = float(np.sum(E_c * A_c))
    EI_c = float(np.sum(E_c * A_c * y_c * y_c))
    L_col = element_geometry(node_positions(), NODE_BASE_L, NODE_COL_L_1)[0]
    Bc = compatibility(L_col)
    k_fibre = Bc.T @ element_basic_stiffness(sec_c, L_col, np.zeros(3), True, LOBATTO_RULE) @ Bc
    k_text = classic_element(EA_c, EI_c, L_col)
    report.append(f"element check (gross section, column element 1 at X*): force-based element vs textbook frame element, "
                  f"max relative difference {np.max(np.abs(k_fibre - k_text)) / np.max(np.abs(k_text)):.1e}")
    for label, sec_tag in (("column", SEC_C01), ("beam", SEC_B01)):
        _, E0, A0, y0 = section_fibres(sec_tag, kc_star)
        report.append(f"section {label} at X* (tag {sec_tag}): EA = {np.sum(E0 * A0):.6e} N, EI = "
                      f"{np.sum(E0 * A0 * y0 * y0):.6e} N.mm^2 (numpy, gross, initial tangents)")

    lam_i, u_i, n_it = first_step_frame(kc_star, False, LOBATTO_RULE)
    report.append(f"inelastic pushover at X*, first step: load factor OpenSees {push['lam'][0]:.6e}, section-state numpy "
                  f"{lam_i:.6e} (iterations {n_it}; relative difference {abs(push['lam'][0] / lam_i - 1.0):.2e}); "
                  f"node-3 displacement X: OpenSees {push['disp_x'][0]:.6e} mm, numpy "
                  f"{lam_i * u_i[frame_dof(NODE_TOP_L, 0)]:.6e} mm")
    lam = push["lam"]
    res_shear = np.abs(push["shear"] + 2.0 * lam)
    res_axial = np.abs(push["axial"] - 2.0 * lam)
    report.append(f"pushover at X* equilibrium over {len(lam)} steps: max |shear + 2 lambda| / max(2 lambda) = "
                  f"{np.max(res_shear) / np.max(2.0 * lam):.2e}; max |axial - 2 lambda| / max(2 lambda) = "
                  f"{np.max(res_axial) / np.max(2.0 * lam):.2e}")
    mu_star = fit[5]
    report.append(f"search: {len(rows)} iterations; last Newton step |DX| = {rows[-1]['residual']:.3e} (tolerance {TOLERANCE:.0e}); "
                  f"ductility at X* = {mu_star:.8f}, target {TARGET_DUCT}, difference {mu_star - TARGET_DUCT:.3e}")
    (output_dir / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report:
        print(line)


# ── 13. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))        # before any CreateODB (AGENT.md §12ac)
    kc_star, rows = find_optimum(output_dir)
    odb_opt, push_opt = run_pushover(kc_star, ODB_OPTIMUM, output_dir)
    ops.printModel("-JSON", "-file", str(output_dir / "model_info.json"))   # model at the optimum
    fit_opt = bilinear_fit(np.abs(push_opt["disp_x"]), np.abs(push_opt["shear"]))
    post_process(output_dir, odb_opt, push_opt, kc_star, fit_opt, rows)
    validate(output_dir, kc_star, push_opt, fit_opt, rows)
