# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D reinforced-concrete portal frame: two 3 m columns (500 x 500 mm) and a 7 m beam (500 x 300 mm), both bases
           fixed. Corotational nonlinearBeamColumn elements with 10 integration points, and fibre sections (Concrete01 for the
           core and the cover, Hysteretic reinforcement). The column rebar diameter (20, 22, 28, 30 and 32 mm; the beam bars
           are 4 mm smaller) and the confinement enhancement ratio (1.15 to 1.35) are varied over a 5 x 5 grid, and each case
           is pushed over to 675 mm (inelastic only, as in the source).
UniqueID : SalarDelavar_Sensitivity_Confinement_Enhancement_Ratio_Rebar
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-26
Purpose  : Sensitivity of the pushover response of the frame to the column rebar diameter and the confinement enhancement
           ratio. For each of the 25 cases: the ductility ratio, the over-strength factor, the behaviour coefficient R, the
           stiffnesses of the bilinear fit of the base shear, and the peak responses. Then the source's post-processing of its
           last case (the one its plots and exports use).
Ref      : py_ref/SENSITIVITY_CONFINEMENT_ENHANCEMENT_RATIO_&_REBAR.py (source main), CONCRETE_SECTION_FUN_TWO.py (section),
           ANALYSIS_FUNCTION.py (its fallback ladder is replaced by SmartAnalyze), BILINEAR_CURVE.py, PLOT_2D.py (PLOT_2D_FRAME
           not run; vis_defo gives the deformed shape), SALAR_MATH.py (not imported by the source's main), COVER.png (figure).
           ground_motions/ holds the source's records; the converted pushover does not use them, as the source's dynamic
           branch is never called.
           Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO/SENSITIVITY_CONFINEMENT_ENHANCEMENT_RATIO_%26_REBAR
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import multiprocessing
import os
import shutil
import sys
from multiprocessing.connection import wait
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
ODB_LAST_CASE = "last_case"                    # ODB of the last case, run again in the main process (LESSON 86)
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
NUM_FIBERS_Z = 1                               # fibres across the width of each patch (source 5; Note 2)
HISTORY_KEYS = ("lam", "disp_x", "disp_y", "rot", "shear", "axial", "moment", "ks", "ka", "ki", "drift_x", "drift_y")
SUMMARY_KEYS = ("dia_col", "kfc", "ro_col", "ro_be", "peak_disp_x", "peak_disp_y", "peak_rot", "peak_axial",
                "peak_shear", "peak_moment", "peak_ks", "peak_ka", "peak_ki", "elastic", "plastic", "tangent",
                "ductility", "omega", "R")


def case_tag(dia_col: float, kfc: float) -> str:
    """Tag of one pushover of the grid: 'd' and the column rebar diameter in mm, '_k' and the ratio times 100 (d20_k115 for
    20 mm and 1.15). The tag names the ODB files and the case result. It is kept short for the 260-character path limit
    on Windows."""
    return f"d{round(dia_col / mm):02d}_k{round(kfc * 100):03d}"


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

# Column section (source Bc, Hc, coverC): both sides 500 mm
B_COL = 500.0 * mm
H_COL = 500.0 * mm
COVER_COL = 50.0 * mm
# Beam section (source Bb, Hb, coverB): width 500 mm and depth 300 mm
B_BEAM = 500.0 * mm
H_BEAM = 300.0 * mm
COVER_BEAM = 50.0 * mm
LENGTH_COL = 3000.0 * mm        # source LENGTH_COL
LENGTH_BEAM = 7000.0 * mm       # source LENGTH_BM
# Element masses per unit length, as written in the source (no effect on a static pushover)
MASS_PER_LENGTH_COL = B_COL * H_COL * 0.000025
MASS_PER_LENGTH_BEAM = B_BEAM * H_BEAM * 0.000025

# The grid (source DIAc and Kfc; the source loops over DIAc outside and Kfc inside)
DIA_COL_VALUES = (20.0 * mm, 22.0 * mm, 28.0 * mm, 30.0 * mm, 32.0 * mm)   # source DIAc: column rebar diameter
KFC_VALUES = (1.15, 1.20, 1.25, 1.30, 1.35)                                # source Kfc: confinement enhancement ratio
DIA_BEAM_REDUCTION = 4.0 * mm   # source DIAb = DIAc - 4: beam rebar diameter
# Confinement offsets of the other sections (source Kfc - 0.05, Kfc - 0.10 and Kfc - 0.15)
KFC_OFFSET_COL_MID = 0.05       # secTagC02, the middle column (source)
KFC_OFFSET_BEAM = 0.10          # secTagB01, the beam (source)
KFC_OFFSET_BEAM_MID = 0.15      # secTagB02, the middle beam (source)
CASES = tuple((dia, kfc) for dia in DIA_COL_VALUES for kfc in KFC_VALUES)   # 25 cases, source loop order
LAST_CASE = CASES[-1]           # the source's last call: its plots and exports use it (LESSON 86)

# Pushover (source)
DMAX = 675.0 * mm               # maximum displacement (source DMAX)
DINCR = 0.05 * mm               # displacement increment (source DINCR): 13500 steps
MAX_ITERATIONS = 5000           # convergence iterations (source MAX_ITERATIONS)
MAX_TOLERANCE = 1.0e-6          # convergence tolerance (source MAX_TOLERANCE)
ODB_EVERY_PUSHOVER = 20         # ODB fetch every 20 pushover steps (AGENT.md §3d)
GRID_WORKERS = 3                # pushovers of the grid run in separate processes, three at a time (Note 3)


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


def bar_area(dia: float) -> float:
    """Area of one reinforcing bar (source AsC and AsB = pi D^2 / 4)."""
    return np.pi * dia**2 / 4.0


def rebar_ratios(dia_col: float) -> tuple:
    """Column and beam reinforcement ratios as the source writes them: RO_COL = 8 A_bar,col / (Hc Bc) and
    RO_BE = 6 A_bar,beam / (Hb Bb). The column section has six bars and the beam eight (Note 6).

    Returns:
        (RO_COL, RO_BE) for the column rebar diameter dia_col.
    """
    ro_col = 8.0 * bar_area(dia_col) / (H_COL * B_COL)
    ro_be = 6.0 * bar_area(dia_col - DIA_BEAM_REDUCTION) / (H_BEAM * B_BEAM)
    return ro_col, ro_be


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
def section_spec(kfc: float, dia_col: float) -> dict:
    """Confined fibre sections of the source for the ratio kfc and the column rebar diameter dia_col, as its
    CONFINED_CONCRETE_SECTION calls give them: tag -> (depth h, width b, cover, bar area, confinement ratio, column flag).
    The columns take kfc and kfc - 0.05, the beams kfc - 0.10 and kfc - 0.15. The beam bars are dia_col - 4 mm (source DIAb).
    """
    a_col = bar_area(dia_col)
    a_beam = bar_area(dia_col - DIA_BEAM_REDUCTION)
    return {
        SEC_C01: (H_COL, B_COL, COVER_COL, a_col, kfc, True),
        SEC_C02: (H_COL, B_COL, COVER_COL, a_col, kfc - KFC_OFFSET_COL_MID, True),
        SEC_B01: (H_BEAM, B_BEAM, COVER_BEAM, a_beam, kfc - KFC_OFFSET_BEAM, False),
        SEC_B02: (H_BEAM, B_BEAM, COVER_BEAM, a_beam, kfc - KFC_OFFSET_BEAM_MID, False),
    }


def define_fiber_section(sec_tag: int, h: float, b: float, cover: float, area_bar: float, kc: float, col: bool) -> None:
    """Confined fibre section of the source (CONFINED_CONCRETE_SECTION). Each section has its own materials, as in the
    source: core (sec + 100, Concrete01 with kc), cover (sec + 200, Concrete01, unconfined) and steel (sec + 300,
    Hysteretic). Column (col = True): three bars on each face, six in all. Beam (col = False): a middle layer of two bars
    as well, eight in all.
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


def define_sections(kfc: float, dia_col: float) -> None:
    """The four fibre sections of the source for the ratio kfc and the column rebar diameter dia_col."""
    for sec_tag, (h, b, cover, area_bar, kc_sec, col) in section_spec(kfc, dia_col).items():
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


def build_model(dia_col: float, kfc: float, odb_tag, output_dir: Path = None):
    """Build the frame for one analysis of the grid. The V1 and V2 stages are written when output_dir is given.

    Returns:
        The CreateODB instance.
    """
    init_model()
    define_nodes_and_supports()
    define_sections(kfc, dia_col)
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
def run_pushover(dia_col: float, kfc: float, odb_tag: str, output_dir: Path = None) -> tuple:
    """Horizontal displacement control of node 4 (DOF 1) to DMAX through SmartAnalyze (source PD_ANALYSIS, PUSHOVER) for
    the column rebar diameter dia_col and the confinement ratio kfc.

    Returns:
        (odb, history): the ODB and the per-step arrays. The base reactions keep the source's sign (no minus).
    """
    odb = build_model(dia_col, kfc, odb_tag, output_dir)
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
        algoTypes=[10, 41, 40, 20, 50, 60],        # Newton first, then the fallback ladder (Note 4)
        printPer=0,
        testPrintFlag=0,
    )
    history = {key: [] for key in HISTORY_KEYS}
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


def case_result_path(output_dir: Path, tag: str) -> Path:
    """File that holds the saved result of one case of the grid."""
    return output_dir / "cases" / f"{tag}.npz"


def peak(values: np.ndarray) -> float:
    """Largest absolute value of a response array, ignoring non-finite entries (the source's np.max(np.abs(...)))."""
    values = np.abs(np.asarray(values, dtype=float))
    finite = values[np.isfinite(values)]
    return float(finite.max()) if finite.size else float("nan")


def case_summary(dia_col: float, kfc: float, history: dict) -> dict:
    """The source's results of one case: the reinforcement ratios (its formulas), the largest absolute value of each
    response over the pushover (its MAX lists) and the bilinear fit of the base shear with R = Omega_0 mu (its PD_ANALYSIS).
    """
    fit = bilinear_fit(np.abs(history["disp_x"]), np.abs(history["shear"]))
    ro_col, ro_be = rebar_ratios(dia_col)
    return {
        "dia_col": dia_col / mm, "kfc": kfc, "ro_col": ro_col, "ro_be": ro_be,
        "peak_disp_x": peak(history["disp_x"]), "peak_disp_y": peak(history["disp_y"]),
        "peak_rot": peak(history["rot"]), "peak_axial": peak(history["axial"]),
        "peak_shear": peak(history["shear"]), "peak_moment": peak(history["moment"]),
        "peak_ks": peak(history["ks"]), "peak_ka": peak(history["ka"]), "peak_ki": peak(history["ki"]),
        "elastic": fit[2], "plastic": fit[3], "tangent": fit[4], "ductility": fit[5], "omega": fit[6],
        "R": fit[6] * fit[5],
    }


def case_worker(job: tuple) -> None:
    """One pushover of the grid, run in its own process (see run_grid). job = (dia_col, kfc, odb_tag, output_dir). The ODB
    is saved after the analysis, not inside its step loop. The case summary and the step arrays are saved to
    output/cases/<odb_tag>.npz only when the pushover has completed all its steps."""
    dia_col, kfc, odb_tag, output_dir = job
    opst.post.set_odb_path(output_dir)            # before any CreateODB (AGENT.md §12ac), in this process
    odb, history = run_pushover(dia_col, kfc, odb_tag, None)
    odb.save_response()
    steps = round(DMAX / DINCR)
    if len(history["lam"]) != steps:
        raise RuntimeError(f"pushover {odb_tag} stopped after {len(history['lam'])} of {steps} steps")
    np.savez(case_result_path(Path(output_dir), odb_tag), **case_summary(dia_col, kfc, history), **history)


def clear_case_outputs(output_dir: Path, tag: str) -> None:
    """Remove the ODB files of a case that an interrupted run started but did not complete (LESSON 88)."""
    for path in output_dir.glob(f"*{tag}*"):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def run_grid(output_dir: Path) -> None:
    """Run the pushovers of the grid that have no saved result yet, GRID_WORKERS at a time, each in its own process
    (LESSON 85): each process starts from its own working folder under output/.work, because opstool's set_odb_path
    removes the '.opstool.output' folder of the working folder. Each completed case is saved to output/cases at once, so
    an interrupted run continues with the cases that are missing (LESSON 88).

    Raises:
        RuntimeError: if a pushover did not complete in its process.
    """
    (output_dir / "cases").mkdir(parents=True, exist_ok=True)
    queue = []
    for dia_col, kfc in CASES:
        tag = case_tag(dia_col, kfc)
        if case_result_path(output_dir, tag).exists():
            continue
        clear_case_outputs(output_dir, tag)
        queue.append((dia_col, kfc, tag, str(output_dir)))
    ctx = multiprocessing.get_context("spawn")
    work_root = output_dir / ".work"
    original = os.getcwd()
    running, failed = {}, []
    try:
        while queue or running:
            while queue and len(running) < GRID_WORKERS:
                dia_col, kfc, tag, out = queue.pop(0)
                work = work_root / tag
                work.mkdir(parents=True, exist_ok=True)
                os.chdir(work)                    # the new process inherits this working folder when it starts
                proc = ctx.Process(target=case_worker, args=((dia_col, kfc, tag, out),))
                proc.start()
                os.chdir(original)
                running[proc.sentinel] = (tag, proc)
                print(f"  started {tag}", flush=True)
            for sentinel in wait(list(running)):
                tag, proc = running.pop(sentinel)
                proc.join()
                print(f"  finished {tag} (exit code {proc.exitcode})", flush=True)
                if proc.exitcode != 0:
                    failed.append(tag)
    finally:
        os.chdir(original)
        shutil.rmtree(work_root, ignore_errors=True)
    if failed:
        raise RuntimeError(f"pushovers {', '.join(failed)} failed in their processes (see the messages above)")


def load_case_rows(output_dir: Path) -> list:
    """The saved result of every case of the grid, in the source's loop order (DIAc outer, Kfc inner). Each row holds the
    summary (SUMMARY_KEYS) and the step arrays under 'history'."""
    rows = []
    for dia_col, kfc in CASES:
        with np.load(case_result_path(output_dir, case_tag(dia_col, kfc))) as data:
            row = {key: float(data[key]) for key in SUMMARY_KEYS}
            row["history"] = {key: np.array(data[key]) for key in HISTORY_KEYS}
        rows.append(row)
    return rows


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
    """Pushover columns of the last case, named as in the first sub-model's results (the source does not export its
    pushover)."""
    return {"load_factor": push["lam"], "DISP_X": push["disp_x"], "DISP_Y": push["disp_y"],
            "ROTATION": push["rot"], "AXIAL_FORCE": push["axial"], "SHEAR_FORCE": push["shear"],
            "MOMENT": push["moment"], "LATERAL_ST_X": push["ks"], "LATERAL_ST_Y": push["ka"],
            "ROTATIONAL_ST": push["ki"], "DRIFT_X": push["drift_x"], "DRIFT_Y": push["drift_y"]}


# The source's DATA_TOTAL table: (column name in the source, key of the case summary)
TABLE_COLUMNS = (
    ("DIAc", "dia_col"), ("Kfc", "kfc"), ("RO_COL", "ro_col"), ("RO_BE", "ro_be"),
    ("DISP_X", "peak_disp_x"), ("DISP_Y", "peak_disp_y"), ("ROTATION", "peak_rot"),
    ("AXIAL_FORCE", "peak_axial"), ("SHEAR_FORCE", "peak_shear"), ("MOMENT_WO", "peak_moment"),
    ("AXIAL_RIGIDITY", "peak_axial"),                 # the source's |max axial force|, the same as AXIAL_FORCE (Note 9)
    ("ROTATIONAL_ST", "peak_ki"), ("LATERAL_ST_Y", "peak_ka"), ("LATERAL_ST_X", "peak_ks"),
    ("Elastic_ST_MAX", "elastic"), ("Plastic_ST_MAX", "plastic"), ("Tangent_ST_MAX", "tangent"),
    ("Ductility_Rito_MAX", "ductility"), ("Over_Strength_Factor_MAX", "omega"),
    ("Structural_Behavior_Coefficient_MAX", "R"),
)


def grid_table(rows: list) -> dict:
    """The source's results table over the grid (its DATA_TOTAL), one entry per column, in the source's order."""
    return {name: np.array([row[key] for row in rows], dtype=float) for name, key in TABLE_COLUMNS}


def write_results(output_dir: Path, rows: list, fit_x: tuple, fit_y: tuple) -> None:
    """Text summary: the bilinear fits of the last case (the source's formulas, in X and in Y) and the ranges of the grid."""
    X, Y, k_el, k_pl, k_tan, mu, omega = fit_x
    mu_y, omega_y = fit_y[5], fit_y[6]
    r_y = omega_y * (2.0 * mu_y - 1.0) ** 0.5 / mu_y ** 0.5          # the source's Y-direction R (its R_mu)
    ductility = [row["ductility"] for row in rows]
    behaviour = [row["R"] for row in rows]
    elastic = [row["elastic"] for row in rows]
    lines = [
        f"cases: {len(rows)} = {len(DIA_COL_VALUES)} column rebar diameters x {len(KFC_VALUES)} confinement ratios; "
        f"each pushover to {DMAX / mm:.0f} mm in {round(DMAX / DINCR)} steps (SmartAnalyze)",
        f"last case (the source's last call, LESSON 86): column rebar {LAST_CASE[0] / mm:.0f} mm, confinement ratio "
        f"{LAST_CASE[1]:.2f}; its ODB is {ODB_LAST_CASE}",
        f"last case, base shear in X: ductility mu = {mu:.6f}; over-strength Omega_0 = {omega:.4f}; "
        f"R = Omega_0 mu = {omega * mu:.4f}",
        f"  bilinear fit in X: X = {X[1]:.4f} mm, {X[2]:.4f} mm; Y = {Y[1]:.4f} N, {Y[2]:.4f} N; elastic stiffness "
        f"{k_el:.4f} N/mm; plastic {k_pl:.4f} N/mm; tangent {k_tan:.4f} N/mm",
        f"last case, base axial force in Y (the source's Y formulas): mu = {mu_y:.6f}; Omega_0 = {omega_y:.4f}; "
        f"R = {r_y:.4f}",
        f"grid: ductility mu from {min(ductility):.4f} to {max(ductility):.4f}; R from {min(behaviour):.4f} to "
        f"{max(behaviour):.4f}; elastic stiffness from {min(elastic):.1f} to {max(elastic):.1f} N/mm",
    ]
    (output_dir / "sensitivity_results.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_last_case(output_dir: Path, push: dict, fit_x: tuple, fit_y: tuple) -> None:
    """The source's line and scatter plots of its last case (PLOT_LINE, PLOT_SCATTER and BC.PLOT_2D), saved as PNG files
    in place of the source's plt.show() calls."""
    import matplotlib.pyplot as plt

    colour = COLORS["primary"]
    fig, axes = plt.subplots(2, 2, figsize=(14, 11), dpi=150)
    panels = (
        (push["moment"], push["axial"], "P-M Interaction", "Bending Moment [N.mm]", "Axial Force [N]"),
        (push["disp_x"], push["shear"], "Shear Force-Displacement Diagram", "Displacement in X [mm]", "Shear Force [N]"),
        (push["disp_y"], push["axial"], "Axial Force-Displacement Diagram", "Displacement in Y [mm]", "Axial Force [N]"),
        (push["rot"], push["moment"], "Moment-Rotation Diagram", "Rotation [rad]", "Moment [N.mm]"),
    )
    for ax, (x, y, title, xlabel, ylabel) in zip(axes.ravel(), panels):
        ax.plot(x, y, color=colour, lw=1.6)
        _style_ax(ax, xlabel, ylabel, title)
    fig.tight_layout()
    fig.savefig(output_dir / "last_case_curves.png")
    plt.close(fig)

    step = np.arange(len(push["lam"]))
    fig, axes = plt.subplots(2, 3, figsize=(18, 10), dpi=150)
    series = (("Axial Force [N]", push["axial"]), ("Shear Force [N]", push["shear"]),
              ("Moment [N.mm]", push["moment"]), ("Displacement - X [mm]", push["disp_x"]),
              ("Displacement - Y [mm]", push["disp_y"]), ("Rotation [rad]", push["rot"]))
    for ax, (ylabel, y) in zip(axes.ravel(), series):
        ax.plot(step, y, color=colour, lw=1.2)
        _style_ax(ax, "Step", ylabel, f"{ylabel} during the analysis")
    fig.tight_layout()
    fig.savefig(output_dir / "last_case_steps.png")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), dpi=150)
    for ax, (lateral, label) in zip(axes, ((push["ks"], "X"), (push["ka"], "Y"))):
        ax.scatter(push["ki"], lateral, s=4, color="black")
        _style_ax(ax, "Rotational Stiffness [N.mm/rad]", f"Lateral Stiffness in {label} Dir. [N/mm]",
                  f"Rotational - lateral stiffness ({label} Dir)")
        ax.set_xscale("log")
        ax.set_yscale("log")
    fig.tight_layout()
    fig.savefig(output_dir / "last_case_stiffness.png")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), dpi=150)
    panels = (
        (fit_x, push["disp_x"], push["shear"], "Last case: base shear - X", "Displacement in X [mm]", "Base shear [N]"),
        (fit_y, push["disp_y"], push["axial"], "Last case: base axial force - Y", "Displacement in Y [mm]",
         "Base axial force [N]"),
    )
    for ax, (fit, x, y, title, xlabel, ylabel) in zip(axes, panels):
        ax.plot(np.abs(x) / mm, np.abs(y) / N, color=colour, lw=1.6, label="curve")
        ax.plot(fit[0] / mm, fit[1] / N, color="black", lw=1.0, ls=":", label="bilinear fit")
        _style_ax(ax, xlabel, ylabel, title)
        ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "last_case_bilinear.png")
    plt.close(fig)


SURFACES = (                                      # (summary key, z-axis label), the source's PLOT_3D figures 1 to 10
    ("peak_shear", "Structure Shear Reaction in X Dir. [N]"),
    ("peak_axial", "Structure Axial Reaction in Y Dir. [N]"),
    ("peak_moment", "Structure Moment Reaction [N.mm]"),
    ("peak_disp_x", "Structure Displacement in X Dir. [mm]"),
    ("peak_disp_y", "Structure Displacement in Y Dir. [mm]"),
    ("elastic", "Structure Elastic Stiffness [N/mm]"),
    ("plastic", "Structure Plastic Stiffness [N/mm]"),
    ("ductility", "Ductility Ratio [mm/mm]"),
    ("omega", "Over Strength Factor [N/N]"),
    ("R", "Structural Behavior Coefficient"),
)


def plot_surface(output_dir: Path, key: str, zlabel: str, rows: list) -> None:
    """3D contour surface of one quantity over the grid (source PLOT_3D: cubic interpolation of the 25 cases onto a
    100 x 100 grid), saved as a PNG file."""
    import matplotlib.pyplot as plt
    from scipy.interpolate import griddata

    X = np.array([row["dia_col"] for row in rows])
    Y = np.array([row["kfc"] for row in rows])
    Z = np.array([row[key] for row in rows])
    xi = np.linspace(X.min(), X.max(), 100)
    yi = np.linspace(Y.min(), Y.max(), 100)
    xi, yi = np.meshgrid(xi, yi)
    zi = griddata((X, Y), Z, (xi, yi), method="cubic")
    fig = plt.figure(figsize=(10, 7), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    surface = ax.plot_surface(xi, yi, zi, cmap="viridis", edgecolor="none")
    ax.set_xlabel("Rebar Diameter (column) [mm]")
    ax.set_ylabel("Confinement Enhancement Ratio")
    ax.set_zlabel(zlabel)
    fig.colorbar(surface, ax=ax, shrink=0.5, aspect=5)
    ax.set_title(f"3D Contour Plot of {zlabel}")
    fig.tight_layout()
    fig.savefig(output_dir / f"surface_{key}.png")
    plt.close(fig)


def plot_heatmap(output_dir: Path, table: dict) -> None:
    """Correlation heatmap of the grid table (source PLOT_HEATMAP), saved as a PNG file."""
    import matplotlib.pyplot as plt
    import pandas as pd

    corr = pd.DataFrame(table).corr()
    fig, ax = plt.subplots(figsize=(12, 12), dpi=150)
    image = ax.matshow(corr.values, cmap="viridis")
    fig.colorbar(image, ax=ax, shrink=0.8)
    ax.set_xticks(np.arange(len(corr.columns)))
    ax.set_yticks(np.arange(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=90)
    ax.set_yticklabels(corr.index)
    for i in range(len(corr.index)):
        for j in range(len(corr.columns)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", color="white", fontsize=7)
    ax.set_title("Correlation Heatmap", pad=20)
    fig.tight_layout()
    fig.savefig(output_dir / "correlation_heatmap.png")
    plt.close(fig)


def post_process(output_dir: Path, odb, push: dict, rows: list, fit_x: tuple, fit_y: tuple) -> None:
    """Write the CSV files, the summary, the figures and the interactive views; flush the ODB of the last case."""
    odb.save_response()
    save_csv(output_dir, "pushover_last_case.csv", pushover_columns(push))
    save_csv(output_dir, "sensitivity_results.csv", grid_table(rows))
    write_results(output_dir, rows, fit_x, fit_y)
    plot_last_case(output_dir, push, fit_x, fit_y)
    for key, zlabel in SURFACES:
        plot_surface(output_dir, key, zlabel, rows)
    plot_heatmap(output_dir, grid_table(rows))
    vis_curves(output_dir, [
        {"x": np.abs(push["disp_x"]) / mm, "y": np.abs(push["shear"]) / N,
         "xlabel": "Displacement in X (mm), node 3", "ylabel": "Base shear (N)", "title": "Last case of the grid"},
    ], filename="vis_08_pushover_last_case.html", title="Base shear vs displacement, last case of the grid")
    vis_defo(output_dir, filename="vis_05_deformed_last_case.html", odb_tag=ODB_LAST_CASE, resp_dof="UX",
             resp_type="disp", scale=1.0)


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


def section_fibres(sec_tag: int, kfc: float, dia_col: float) -> tuple:
    """Fibre list (is_concrete, E0, A, y) of a section for the ratio kfc and the column rebar diameter dia_col, from the
    geometry of define_fiber_section and the initial tangents (Concrete01 E0 = 2 f'c / eps0; Hysteretic E0 = f_y / eps_y).
    Independent of OpenSees."""
    h, b, cover, area_bar, kc_sec, col = section_spec(kfc, dia_col)[sec_tag]
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


def first_step_frame(dia_col: float, kfc: float, gross: bool, rule: tuple) -> tuple:
    """First displacement-control step of the frame in numpy for the column rebar diameter dia_col and the ratio kfc, for
    the pushover load (1 N horizontal and -1 N vertical at the top nodes). Each element is a force-based element whose
    section flexibilities follow the section states of the current solution, iterated to convergence; gross=True keeps the
    uncracked sections. The restrained DOFs are those of the two fixed bases.

    Returns:
        (load factor, displacements per unit load, number of iterations).
    """
    pos = node_positions()
    elements = []
    for _, ni, nj, sec, _ in ELEMENTS:
        L, c, s = element_geometry(pos, ni, nj)
        dofs = [frame_dof(ni, k) for k in range(3)] + [frame_dof(nj, k) for k in range(3)]
        elements.append({"sec": section_fibres(sec, kfc, dia_col), "L": L, "T": transform(c, s), "dofs": dofs,
                         "q": np.zeros(3)})
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
            Bmat = compatibility(e["L"])
            K[np.ix_(e["dofs"], e["dofs"])] += e["T"].T @ (Bmat.T @ kb @ Bmat) @ e["T"]
            parts.append((kb, Bmat))
        u = np.zeros(NDOF)
        u[free] = np.linalg.solve(K[np.ix_(free, free)], force[free])
        for e, (kb, Bmat) in zip(elements, parts):
            e["q"] = kb @ (Bmat @ (e["T"] @ u[e["dofs"]]))
        if u_prev is not None and np.max(np.abs(u - u_prev)) <= 1e-12 * np.max(np.abs(u)):
            return (DINCR / mm) / u[frame_dof(NODE_TOP_R, 0)], u, iteration
        u_prev = u
    raise RuntimeError("the first-step iteration did not converge")


def element_check(dia_col: float, kfc: float) -> float:
    """Largest relative difference between the gross force-based element of column element 1 and the textbook frame element
    (EA and EI from the initial tangents of its fibres), for this case."""
    sec_c = section_fibres(SEC_C01, kfc, dia_col)
    _, E_c, A_c, y_c = sec_c
    EA_c = float(np.sum(E_c * A_c))
    EI_c = float(np.sum(E_c * A_c * y_c * y_c))
    L_col = element_geometry(node_positions(), NODE_BASE_L, NODE_COL_L_1)[0]
    Bmat = compatibility(L_col)
    k_fibre = Bmat.T @ element_basic_stiffness(sec_c, L_col, np.zeros(3), True, LOBATTO_RULE) @ Bmat
    k_text = classic_element(EA_c, EI_c, L_col)
    return float(np.max(np.abs(k_fibre - k_text)) / np.max(np.abs(k_text)))


def validate(output_dir: Path, rows: list, push_last: dict) -> None:
    """Compare the grid with independent numpy calculations and check its bookkeeping; write validation.txt.

    For every case: (1) the force-based element of its column section against the textbook frame element (gross sections);
    (2) the first pushover step (section states, 10 Lobatto points) against OpenSees; (3) the equilibrium of the base
    reactions at every step (shear = -2 lambda, axial = +2 lambda); (4) that the case completed all its steps. The last case,
    run again in this process, is compared with its grid run. The bilinear fits and the behaviour coefficients are the
    source's formulas, ported, and are reported, not validated.
    """
    report = []
    worst = {"element": 0.0, "first": 0.0, "equilibrium": 0.0}
    nonfinite = 0
    for row in rows:
        dia_col, kfc = row["dia_col"] * mm, row["kfc"]
        hist = row["history"]
        lam = hist["lam"]
        elem = element_check(dia_col, kfc)
        lam_i, _, n_it = first_step_frame(dia_col, kfc, False, LOBATTO_RULE)
        first = abs(lam[0] / lam_i - 1.0)
        scale = np.max(2.0 * lam)
        eq = max(np.max(np.abs(hist["shear"] + 2.0 * lam)), np.max(np.abs(hist["axial"] - 2.0 * lam))) / scale
        nonfinite += sum(int(np.sum(~np.isfinite(hist[key]))) for key in ("ks", "ka", "ki"))
        worst["element"] = max(worst["element"], elem)
        worst["first"] = max(worst["first"], first)
        worst["equilibrium"] = max(worst["equilibrium"], eq)
        report.append(
            f"{case_tag(dia_col, kfc)}: element check {elem:.1e}; first step lambda OpenSees {lam[0]:.6e}, numpy "
            f"{lam_i:.6e} (relative difference {first:.1e}, {n_it} iterations); equilibrium {eq:.1e}; steps {len(lam)}; "
            f"ductility {row['ductility']:.6f}; R {row['R']:.4f}"
        )
    rerun = np.max(np.abs(push_last["shear"] - rows[-1]["history"]["shear"])) / np.max(np.abs(rows[-1]["history"]["shear"]))
    steps = sorted({len(row["history"]["lam"]) for row in rows})
    report += [
        "",
        f"cases completed: {len(rows)} of {len(CASES)}; steps per case: {steps} (expected {round(DMAX / DINCR)})",
        f"largest element-check difference {worst['element']:.1e}; largest first-step relative difference "
        f"{worst['first']:.1e}; largest equilibrium residual {worst['equilibrium']:.1e}",
        f"non-finite stiffness values in the case histories (KS, KA, KI): {nonfinite}",
        f"last case run again in this process vs its grid run: largest difference of the base shear {rerun:.1e} (relative)",
        "The bilinear fits and the behaviour coefficients are the source's formulas, ported; they are reported, not validated.",
    ]
    (output_dir / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report:
        print(line)


# ── 13. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(output_dir)                           # opstool's analysis log goes to the working folder: keep it in output/
    opst.post.set_odb_path(str(output_dir))        # before any CreateODB (AGENT.md §12ac)
    run_grid(output_dir)
    rows = load_case_rows(output_dir)
    odb_last, push_last = run_pushover(LAST_CASE[0], LAST_CASE[1], ODB_LAST_CASE, output_dir)
    ops.printModel("-JSON", "-file", str(output_dir / "model_info.json"))   # model at the last case
    fit_x = bilinear_fit(np.abs(push_last["disp_x"]), np.abs(push_last["shear"]))
    fit_y = bilinear_fit(np.abs(push_last["disp_y"]), np.abs(push_last["axial"]))
    post_process(output_dir, odb_last, push_last, rows, fit_x, fit_y)
    validate(output_dir, rows, push_last)
