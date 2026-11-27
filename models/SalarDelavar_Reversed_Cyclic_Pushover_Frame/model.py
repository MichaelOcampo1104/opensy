# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D reinforced-concrete frame under a reversed cyclic displacement history (60 cycles, 500 samples each) applied by
           displacement control at the top right node. Two 3 m columns (500 x 500 mm) and a 7 m beam (500 mm wide, 300 mm deep),
           a single beam element, both column bases fixed. Fibre sections with Concrete01 core and cover, and Steel01 or
           Hysteretic reinforcement; corotational nonlinearBeamColumn elements with 5 integration points. The protocol is the
           source's, as written: its increments are the differences between consecutive cycles (Note 1).
UniqueID : SalarDelavar_Reversed_Cyclic_Pushover_Frame
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-27
Purpose  : Reversed cyclic pushover of the frame with the two reinforcement models: the base shear, the axial force, the moment,
           the displacements, the rotation and the stiffnesses at each of the 30,000 steps, and the moment-rotation, shear-drift
           and P-M relations of the source. The envelope of the imposed displacement is the source's, which Note 1 explains.
Ref      : py_ref/CONCRETE_FRAME_CYCLIC.py (source main), CONCRETE_SECTION_FUN.py (fibre section), ANALYSIS_FUNCTION.py (its fallback
           ladder is replaced by SmartAnalyze, AGENT.md §3c), PLOT_2D.py (PLOT_2D_FRAME is not called; vis_defo gives the deformed
           shape), CONCRETE_FRAME_CYCLIC.png (figure).
           Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CYCLIC_PUSHOVER
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import os
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops
import opstool as opst
import pandas as pd

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

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
ODB_TAG_STEEL01 = 1             # run with Steel01 reinforcement (source WITHOUT HARDENING AND ULTIMATE STRAIN)
ODB_TAG_HYSTERETIC = 2          # run with Hysteretic reinforcement (source WITH HARDENING AND ULTIMATE STRAIN)
NODE_BASE_L, NODE_BASE_R = 1, 2
NODE_TOP_L, NODE_TOP_R = 3, 4
NODE_CONTROL, DOF_CONTROL = NODE_TOP_R, 1      # the displacement control: node 4, X (the source's second integrator call)
SEC_COL = 10                    # column fibre section (source secTagC)
SEC_BEAM = 20                   # beam fibre section (source secTagB)
TAG_CORE, TAG_COVER, TAG_STEEL = 1, 2, 3       # material tags (source coreTag, coverTag, steelTag)
TRANSF_COROT = 1
TS_LOAD = 1                     # Linear time series of the reference load
PAT_LOAD = 1
ELE_COL_L, ELE_COL_R, ELE_BEAM = 1, 2, 3
STEEL_KIND_STEEL01 = 1          # source STEEL_KIND 1
STEEL_KIND_HYSTERETIC = 2       # source STEEL_KIND 2

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Lengths in mm, forces in N, stresses in MPa = N/mm²
# Concrete01: core (confined) and cover (unconfined), as the source gives them
fc_core = -27.6 * MPa            # compressive strength of the core (source fcC)
ec0_core = -0.0045               # strain at the strength (source ec0C)
fcu_core = -21.0 * MPa           # ultimate strength of the core (source fcUC)
ecu_core = -0.015                # ultimate strain of the core (source ecuC)
fc_cover = -18.0 * MPa           # compressive strength of the cover (source fcU)
ec0_cover = -0.0025              # strain at the strength (source ec0U)
fcu_cover = -2.0 * MPa           # ultimate strength of the cover (source fcUU)
ecu_cover = -0.008               # ultimate strain of the cover (source ecuU)

# Reinforcement (source values)
fy = 4000.0 * MPa                # steel yield strength
es = 2.0e5 * MPa                 # steel modulus of elasticity
fu_ratio = 1.1818                # ultimate strength / yield strength
esu_ratio = 75.2                 # ultimate strain / yield strain (source esu = ey * 75.2)
hyst_stress_ratio = 0.2          # Hysteretic: second point at 0.2 f_u
hyst_strain_ratio = 1.1          # Hysteretic: second point at 1.1 e_su
pinch_x = 0.8                    # Hysteretic pinching factor in X
pinch_y = 0.5                    # Hysteretic pinching factor in Y
damage1 = 0.0                    # Hysteretic damage due to ductility
damage2 = 0.0                    # Hysteretic damage due to energy
hyst_beta = 0.1                  # Hysteretic stiffness degradation parameter

# Sections (source Bc, Hc, coverC, DIAc; Bb, Hb, coverB, DIAb)
col_b = 500.0 * mm               # column width in Z
col_h = 500.0 * mm               # column depth in Y
col_cover = 50.0 * mm
col_bar_dia = 25.0 * mm
beam_b = 500.0 * mm              # beam width in Z
beam_h = 300.0 * mm              # beam depth in Y
beam_cover = 50.0 * mm
beam_bar_dia = 18.0 * mm
as_col_bar = np.pi * col_bar_dia**2 / 4        # bar area, column (source AsC)
as_beam_bar = np.pi * beam_bar_dia**2 / 4      # bar area, beam (source AsB)
bars_top = 3                     # bars in each outer layer (source)
bars_mid = 2                     # bars in the beam's middle layer (source)
num_fibers = 20                  # fibres per patch along the section depth (source NUMFIBERS)
num_fibers_z = 5                 # fibres per patch across the section width (source)
num_int_points = 5               # integration points per element (source numIntgrPts)

len_col = 3000.0 * mm            # column height (source LENGTH_COL)
len_beam = 7000.0 * mm           # beam span (source LENGTH_BM)

# Reference load of the pattern (the displacement control sets its factor): 1 N in X and -1 N in Y at nodes 3 and 4
px_ref = 1.0 * N
py_ref = -1.0 * N

# Cyclic displacement history (source CYCLIC_LOADING, polynomial amplitude growth, EXPO = True)
num_cycles = 60
samples_per_cycle = 500
max_value = 80.0 * mm           # maximum displacement amplitude intended by the source (see Note 1)
growth_exponent = 2

max_iterations = 5000            # convergence iterations of the tests (source MAX_ITERATIONS)
max_tolerance = 1.0e-6           # convergence tolerance of the tests (source MAX_TOLERANCE)
odb_every_n = 60                 # ODB step every 60 analysis steps (500 ODB steps per run, AGENT.md §3d)

RECORD_KEYS = ("step", "increment", "control", "force_s", "force_a", "moment", "disp_x", "disp_y", "rot", "drift",
               "ks", "ka", "ki", "r1x", "r1y", "r1z", "r2x", "r2y", "r2z", "u3x", "u3y", "u4x", "u4y", "ok")


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Reset OpenSees and create a 2D model with 3 DOFs per node (source ops.model('basic', '-ndm', 2, '-ndf', 3))."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. NODES AND SUPPORTS ────────────────────────────────────────────────────
def define_nodes_and_supports() -> None:
    """Corner nodes of the frame (source ops.node) and the fixed column bases (source ops.fix)."""
    ops.node(NODE_BASE_L, 0.0 * mm, 0.0 * mm)
    ops.node(NODE_BASE_R, len_beam, 0.0 * mm)
    ops.node(NODE_TOP_L, 0.0 * mm, len_col)
    ops.node(NODE_TOP_R, len_beam, len_col)
    ops.fix(NODE_BASE_L, 1, 1, 1)
    ops.fix(NODE_BASE_R, 1, 1, 1)


# ── 6. SECTIONS (MATERIALS AND FIBRES) ───────────────────────────────────────
def define_materials(steel_kind: int) -> None:
    """Materials of the frame (source CYCLIC_ANALYSIS): Concrete01 for the core and the cover, and Steel01 or Hysteretic for the
    reinforcement.

    Args:
        steel_kind: STEEL_KIND_STEEL01 or STEEL_KIND_HYSTERETIC.
    """
    ey = fy / es                                   # steel yield strain
    fu = fu_ratio * fy                             # steel ultimate strength
    esu = ey * esu_ratio                           # steel ultimate strain (source)
    if steel_kind == STEEL_KIND_STEEL01:
        ops.uniaxialMaterial("Steel01", TAG_STEEL, fy, es, 0.0)
    elif steel_kind == STEEL_KIND_HYSTERETIC:
        ops.uniaxialMaterial("Hysteretic", TAG_STEEL, fy, ey, fu, esu,
                             hyst_stress_ratio * fu, hyst_strain_ratio * esu,
                             -fy, -ey, -fu, -esu,
                             -hyst_stress_ratio * fu, -hyst_strain_ratio * esu,
                             pinch_x, pinch_y, damage1, damage2, hyst_beta)
    else:
        raise ValueError(f"unknown steel kind {steel_kind}")
    ops.uniaxialMaterial("Concrete01", TAG_CORE, fc_core, ec0_core, fcu_core, ecu_core)
    ops.uniaxialMaterial("Concrete01", TAG_COVER, fc_cover, ec0_cover, fcu_cover, ecu_cover)


def define_fibre_section(sec_tag: int, h: float, b: float, cover: float, bar_area: float, is_column: bool) -> None:
    """Fibre section (source CONFINED_CONCRETE_SECTION of CONCRETE_SECTION_FUN.py): the core and cover patches, and the rebar
    layers, three bars on each outer face and, in a beam, two bars in the middle.

    Args:
        sec_tag: Section tag.
        h: Section extent in Y, the depth that bends about Z (mm).
        b: Section extent in Z (mm).
        cover: Concrete cover (mm).
        bar_area: Area of one rebar (mm²).
        is_column: True for a column; False for the beam.
    """
    y1 = h / 2.0
    z1 = b / 2.0
    ops.section("Fiber", sec_tag)
    ops.patch("rect", TAG_CORE, num_fibers, num_fibers_z, cover - y1, cover - z1, y1 - cover, z1 - cover)
    ops.patch("rect", TAG_COVER, num_fibers, num_fibers_z, -y1, z1 - cover, y1, z1)
    ops.patch("rect", TAG_COVER, num_fibers, num_fibers_z, -y1, -z1, y1, cover - z1)
    ops.patch("rect", TAG_COVER, num_fibers, num_fibers_z, -y1, cover - z1, cover - y1, z1 - cover)
    ops.patch("rect", TAG_COVER, num_fibers, num_fibers_z, y1 - cover, cover - z1, y1, z1 - cover)
    ops.layer("straight", TAG_STEEL, bars_top, bar_area, y1 - cover, z1 - cover, y1 - cover, cover - z1)
    if not is_column:
        ops.layer("straight", TAG_STEEL, bars_mid, bar_area, 0.0, z1 - cover, 0.0, cover - z1)
    ops.layer("straight", TAG_STEEL, bars_top, bar_area, cover - y1, z1 - cover, cover - y1, cover - z1)


# ── 7. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Corotational transformation and three nonlinearBeamColumn elements: two columns, and the beam as one element between
    the two top nodes (source ops.element('nonlinearBeamColumn', ...))."""
    ops.geomTransf("Corotational", TRANSF_COROT)
    ops.element("nonlinearBeamColumn", ELE_COL_L, NODE_BASE_L, NODE_TOP_L, num_int_points, SEC_COL, TRANSF_COROT)
    ops.element("nonlinearBeamColumn", ELE_COL_R, NODE_BASE_R, NODE_TOP_R, num_int_points, SEC_COL, TRANSF_COROT)
    ops.element("nonlinearBeamColumn", ELE_BEAM, NODE_TOP_L, NODE_TOP_R, num_int_points, SEC_BEAM, TRANSF_COROT)


# ── 8. OUTPUT DATABASE (ODB) ─────────────────────────────────────────────────
def create_odb(odb_tag: int) -> "opst.post.CreateODB":
    """Nodal responses of one run, one ODB step every odb_every_n analysis steps. The model data are saved here.

    Args:
        odb_tag: Tag of this run's ODB.

    Returns:
        The CreateODB instance.
    """
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 9. LOADING ───────────────────────────────────────────────────────────────
def define_loads() -> None:
    """The reference load of the pattern: 1 N in X and -1 N in Y at both top nodes (source ops.load). Under displacement control
    its load factor is set by the response, so the reactions are the load factor times these loads."""
    ops.timeSeries("Linear", TS_LOAD)
    ops.pattern("Plain", PAT_LOAD, TS_LOAD)
    ops.load(NODE_TOP_L, px_ref, py_ref, 0.0)
    ops.load(NODE_TOP_R, px_ref, py_ref, 0.0)


# ── 10. ANALYSIS ─────────────────────────────────────────────────────────────
def cyclic_increments() -> np.ndarray:
    """Displacement increments of the source's cyclic history (its CYCLIC_LOADING with polynomial growth, EXPO = True).

    The source builds each cycle's amplitude i**2 * scale (scale = max_value / num_cycles**2) times sin(t), and then subtracts the
    previous cycle's whole array from it (signal - last_end) before concatenating the cycles. The result is the sequence of
    increments that DisplacementControl applies, so the displacement at a step is the sum of all the increments up to it. The
    peak displacement is therefore not max_value (Note 1).

    Returns:
        Array of the increments, one per analysis step (mm).
    """
    t_cycle = np.linspace(0, 2 * np.pi, samples_per_cycle)
    scale_factor = (max_value / mm) / (num_cycles ** growth_exponent)
    signals = []
    last_end = 0.0
    for i in range(1, num_cycles + 1):
        amplitude = (i ** growth_exponent) * scale_factor
        signal = amplitude * np.sin(t_cycle)
        signals.append(signal - last_end)
        last_end = signal
    return np.concatenate(signals) * mm


def build_model(steel_kind: int, output_dir: Path | None = None) -> None:
    """Build the frame, its materials and sections, its elements and its reference load. The visualisation stages V1 to V3 are
    written when output_dir is given.

    Args:
        steel_kind: STEEL_KIND_STEEL01 or STEEL_KIND_HYSTERETIC.
        output_dir: Folder for the V1 to V3 HTML files, or None to skip them.
    """
    init_model()
    define_nodes_and_supports()
    if output_dir is not None:
        vis_nodes(output_dir)                  # V1: nodes and supports
    define_materials(steel_kind)
    define_fibre_section(SEC_COL, col_h, col_b, col_cover, as_col_bar, True)
    define_fibre_section(SEC_BEAM, beam_h, beam_b, beam_cover, as_beam_bar, False)
    define_elements()
    if output_dir is not None:
        vis_model(output_dir)                  # V2: geometry
    define_loads()
    if output_dir is not None:
        vis_loads(output_dir)                  # V3: load vectors


def stiffness(force: float, disp: float) -> float:
    """|force| / |displacement|, computed as the source does with numpy (np.abs(S) / np.abs(disp_X)): NaN where both are zero (the
    first step, where the increment is zero) and inf where only the displacement is zero. Python floats would raise instead.

    Args:
        force: Force or moment (N or N.mm).
        disp: Displacement or rotation (mm or rad).

    Returns:
        The secant stiffness.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        return float(np.abs(force) / np.abs(disp))


def run_cyclic(steel_kind: int, odb_tag: int, increments: np.ndarray, output_dir: Path | None = None) -> dict:
    """One reversed cyclic analysis under displacement control at node 4. Each increment is one analysis step, passed unchanged to
    SmartAnalyze's StaticAnalyze (a zero increment is a step of its own, as in the source). The reactions, the displacements and
    the stiffnesses are recorded at each step; the ODB is written every odb_every_n steps.

    Args:
        steel_kind: STEEL_KIND_STEEL01 or STEEL_KIND_HYSTERETIC.
        odb_tag: Tag of this run's ODB.
        increments: The displacement increments (cyclic_increments()).
        output_dir: Folder for the V1 to V4 figures, or None.

    Returns:
        Dict of arrays over the steps (keys in RECORD_KEYS), with the ODB and the step return codes.
    """
    build_model(steel_kind, output_dir)
    odb = create_odb(odb_tag)
    if output_dir is not None:
        vis_pre_analysis(output_dir)           # V4: all definitions complete, before the solver
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.analysis("Static")
    # The test and the algorithm the source uses after its first step (ANALYSIS_FUNCTION.py, its ladder's first entry, with the source's
    # MAX_TOLERANCE and MAX_ITERATIONS). They persist for the rest of the source's run, so they are the first choice here.
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="NormDispIncr",
        testTol=max_tolerance,
        testIterTimes=max_iterations,
        tryAddTestTimes=False,
        tryAlterAlgoTypes=True,
        algoTypes=[100, 10, 20, 30, 50, 60],   # 100: the user algorithm below (KrylovNewton -initial, as in the source's ladder)
        UserAlgoArgs=["KrylovNewton", "-initial"],
        relaxation=0.5,
        minStep=1.0e-4,
    )
    rec = {key: [] for key in RECORD_KEYS}
    control = 0.0                              # the cumulative displacement target: the sum of the increments
    for step, inc in enumerate(increments):
        control = control + inc
        # The increment goes to the solver unchanged, as the source passes CYCL[step]. Passing the difference of two cumulative
        # targets (static_split) rounds it at about 1e-13 mm, which changed an iteration count at step 1502 (Note 4).
        ok = analysis.StaticAnalyze(node=NODE_CONTROL, dof=DOF_CONTROL, seg=float(inc))
        ops.reactions()
        r1x, r1y, r1z = (ops.nodeReaction(NODE_BASE_L, dof) for dof in (1, 2, 3))
        r2x, r2y, r2z = (ops.nodeReaction(NODE_BASE_R, dof) for dof in (1, 2, 3))
        s_shear = r1x + r2x                    # base shear (source S)
        a_axial = r1y + r2y                    # base axial force (source A)
        m_moment = r1z + r2z                   # base moment (source M)
        disp_x = ops.nodeDisp(NODE_TOP_L, 1)
        disp_y = ops.nodeDisp(NODE_TOP_L, 2)
        rot = ops.nodeDisp(NODE_TOP_L, 3)
        values = {"step": step + 1, "increment": inc, "control": control, "force_s": s_shear, "force_a": a_axial,
                  "moment": m_moment, "disp_x": disp_x, "disp_y": disp_y, "rot": rot,
                  "drift": 100.0 * disp_x / len_col,
                  "ks": stiffness(s_shear, disp_x), "ka": stiffness(a_axial, disp_y), "ki": stiffness(m_moment, rot),
                  "r1x": r1x, "r1y": r1y, "r1z": r1z, "r2x": r2x, "r2y": r2y, "r2z": r2z,
                  "u3x": disp_x, "u3y": disp_y, "u4x": ops.nodeDisp(NODE_TOP_R, 1), "u4y": ops.nodeDisp(NODE_TOP_R, 2),
                  "ok": ok}
        for key in RECORD_KEYS:
            rec[key].append(values[key])
        if (step + 1) % odb_every_n == 0 or step == len(increments) - 1:
            odb.fetch_response_step()
    out = {key: np.array(value) for key, value in rec.items()}
    out.update({"odb": odb, "odb_tag": odb_tag})
    return out


def run_analysis(output_dir: Path) -> dict:
    """Run the source's protocol with the two reinforcement models (Steel01, then Hysteretic).

    Args:
        output_dir: Folder for the ODBs, figures and reports.

    Returns:
        Dict with the runs under the keys "steel01" and "hysteretic", and the increments under "increments".
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))            # direct all ODB files to output/, before any CreateODB
    increments = cyclic_increments()
    steel01 = run_cyclic(STEEL_KIND_STEEL01, ODB_TAG_STEEL01, increments, output_dir)
    hysteretic = run_cyclic(STEEL_KIND_HYSTERETIC, ODB_TAG_HYSTERETIC, increments)
    return {"steel01": steel01, "hysteretic": hysteretic, "increments": increments}


# ── 11. POST-PROCESSING ──────────────────────────────────────────────────────
def results_table(results: dict) -> pd.DataFrame:
    """The results of the two runs with the source's column names (its DATA_TOTAL), one row per step, plus the step and the
    drift in percent (the source plots the drift but does not export it)."""
    s01, hy = results["steel01"], results["hysteretic"]
    return pd.DataFrame({
        "STEP": s01["step"],
        "DISP_X_WO": s01["disp_x"], "DISP_X_W": hy["disp_x"],
        "DISP_Y_WO": s01["disp_y"], "DISP_Y_W": hy["disp_y"],
        "ROTATION_WO": s01["rot"], "ROTATION_W": hy["rot"],
        "AXIAL_FORCE_WO": s01["force_a"], "AXIAL_FORCE_W": hy["force_a"],
        "SHEAR_FORCE_WO": s01["force_s"], "SHEAR_FORCE_W": hy["force_s"],
        "MOMENT_WO": s01["moment"], "MOMENT_W": hy["moment"],
        "AXIAL_RIGIDITY_WO": np.abs(s01["force_a"]), "AXIAL_RIGIDITY_W": np.abs(hy["force_a"]),
        "ROTATIONAL_ST_WO": s01["ki"], "ROTATIONAL_ST_W": hy["ki"],
        "LATERAL_ST_Y_WO": s01["ka"], "LATERAL_ST_Y_W": hy["ka"],
        "LATERAL_ST_X_WO": s01["ks"], "LATERAL_ST_X_W": hy["ks"],
        "DRIFT_PERCENT_WO": s01["drift"], "DRIFT_PERCENT_W": hy["drift"],
    })


def plot_run(output_dir: Path, run: dict, label: str, tag: str) -> None:
    """Curves and histories of one run as HTML figures (the source's figures 1 to 12, drawn with vis_curves; its log axes are not
    reproduced).

    Args:
        output_dir: Folder where the HTML files are written.
        run: One of the dicts returned by run_cyclic().
        label: Title prefix.
        tag: File name tag (steel01 or hysteretic).
    """
    vis_curves(output_dir, panels=[
        {"x": run["moment"], "y": run["force_a"], "xlabel": "Bending moment [N.mm]", "ylabel": "Axial force [N]",
         "title": "P-M interaction"},
        {"x": run["disp_x"], "y": run["force_s"], "xlabel": "Displacement in X [mm]", "ylabel": "Shear force [N]",
         "title": "Shear force-displacement"},
        {"x": run["disp_y"], "y": run["force_a"], "xlabel": "Displacement in Y [mm]", "ylabel": "Axial force [N]",
         "title": "Axial force-displacement"},
        {"x": run["rot"], "y": run["moment"], "xlabel": "Rotation [rad]", "ylabel": "Moment [N.mm]",
         "title": "Moment-rotation"},
    ], filename=f"vis_08_curves_{tag}.html", title=f"{label}: curves")
    vis_curves(output_dir, panels=[
        {"x": run["drift"], "y": run["force_s"], "xlabel": "Lateral story drift in X [%]", "ylabel": "Shear force [N]",
         "title": "Shear force-drift"},
        {"x": run["step"], "y": run["force_s"], "xlabel": "Steps", "ylabel": "Shear force [N]", "title": "Shear force"},
        {"x": run["step"], "y": run["force_a"], "xlabel": "Steps", "ylabel": "Axial force [N]", "title": "Axial force"},
        {"x": run["step"], "y": run["moment"], "xlabel": "Steps", "ylabel": "Moment [N.mm]", "title": "Moment"},
        {"x": run["step"], "y": run["disp_x"], "xlabel": "Steps", "ylabel": "Displacement X [mm]", "title": "Displacement X"},
        {"x": run["step"], "y": run["rot"], "xlabel": "Steps", "ylabel": "Rotation [rad]", "title": "Rotation"},
    ], filename=f"vis_09_history_{tag}.html", title=f"{label}: histories")


def post_process(results: dict, output_dir: Path) -> None:
    """Flush the two ODBs, write the results table (CSV, in place of the source's Excel file, which needs openpyxl that the project
    environment does not have), the deformed shape of the Steel01 run and the figures of both runs.

    Args:
        results: Output of run_analysis().
        output_dir: Folder where the files are written.
    """
    for key in ("steel01", "hysteretic"):
        results[key]["odb"].save_response()    # once per ODB, after its analysis
    results_table(results).to_csv(output_dir / "CONCRETE_FRAME_CYCLIC_RESULTS.csv", index=False)
    plot_run(output_dir, results["steel01"], "Steel01 (without hardening and ultimate strain)", "steel01")
    plot_run(output_dir, results["hysteretic"], "Hysteretic (with hardening and ultimate strain)", "hysteretic")
    vis_defo(output_dir, filename="vis_05_deformed_steel01.html", odb_tag=ODB_TAG_STEEL01, resp_dof="UX")


# ── 12. VALIDATION (independent checks) ─────────────────────────────────────
# The source's own run as written (its printed values at four steps of each run, and the envelope of each run's table).
source_steps = {
    ODB_TAG_STEEL01: {
        2: (0.000279804911076814, 0.00025887582113345815, -3.025789469432527),
        3: (0.0005595654604475228, 0.0007764955419531335, -9.08281230626514),
        15000: (-3.211296051097501e-16, 8.57981117626581e-11, 3.375608599095162e-08),
        30000: (-6.477020848823795e-16, -3.9179180191051586, 1162091.32362429),
    },
    ODB_TAG_HYSTERETIC: {
        2: (0.000279804911076814, 0.00025887582113345815, -3.025789469432527),
        3: (0.0005595654604475228, 0.0007764955419531335, -9.08281230626514),
        15000: (-3.211296051097501e-16, 8.52111872733634e-11, 3.2790920429435824e-08),
        30000: (-6.477020848823795e-16, -1.9362555656036846, 586899.157070867),
    },
}
source_envelope = {
    ODB_TAG_STEEL01: (410.67156461347287, 1764017.5609905513),
    ODB_TAG_HYSTERETIC: (410.66133593706365, 1775196.6415600034),
}


def check(report: list, name: str, value: float, reference: float, tol: float, absolute: bool = False) -> bool:
    """Compare two values and record the line in the report: by relative difference (tolerance scaled by max(1, |reference|)) or,
    when absolute is True, by absolute difference.

    Args:
        report: Report lines (appended to).
        name: Label of the check.
        value: Value from the model.
        reference: Reference value.
        tol: Tolerance.
        absolute: True for an absolute tolerance.

    Returns:
        True when the check passes.
    """
    if absolute:
        diff = abs(value - reference)
        ok = diff <= tol
        report.append(f"{'PASS' if ok else 'FAIL'}  {name}: {value:.10e} vs {reference:.10e} (absolute {diff:.1e}, tol {tol:.0e})")
        return ok
    rel = abs(value - reference) / max(abs(reference), 1.0)
    ok = rel <= tol
    report.append(f"{'PASS' if ok else 'FAIL'}  {name}: {value:.10e} vs {reference:.10e} (relative {rel:.1e}, tol {tol:.0e})")
    return ok


def validate(results: dict, output_dir: Path) -> None:
    """Checks of the two runs: the protocol, the reproduction of the source's printed steps and envelopes, the equilibrium of the
    base reactions with the reference load at every step (force and moment, with the deformed node positions), and the step
    return codes. Writes output/validation.txt and prints it.

    Args:
        results: Output of run_analysis().
        output_dir: Folder where validation.txt is written.
    """
    report, oks = [], []
    names = {ODB_TAG_STEEL01: "Steel01", ODB_TAG_HYSTERETIC: "Hysteretic"}
    inc = results["increments"]
    report.append("RESULTS")
    for key, tag in (("steel01", ODB_TAG_STEEL01), ("hysteretic", ODB_TAG_HYSTERETIC)):
        run = results[key]
        report.append(f"  {names[tag]}: {len(run['step'])} steps, peak |displacement X| {np.max(np.abs(run['disp_x'])):.4f} mm "
                      f"(step {int(np.argmax(np.abs(run['disp_x']))) + 1}), peak |shear| {np.max(np.abs(run['force_s'])):.6e} N, "
                      f"final displacement {run['disp_x'][-1]:.6f} mm, final shear {run['force_s'][-1]:.6e} N")
    report.append(f"  the imposed increments: sum over the run {np.sum(inc) / mm:.6e} mm; the displacement control reaches "
                  f"{results['steel01']['control'][-1]:.6f} mm at the last step")

    report.append("CHECKS")
    for key, tag in (("steel01", ODB_TAG_STEEL01), ("hysteretic", ODB_TAG_HYSTERETIC)):
        run = results[key]
        oks.append(len(run["step"]) == len(inc))
        report.append(f"{'PASS' if oks[-1] else 'FAIL'}  {names[tag]}: one analysis per increment ({len(inc)})")
        ok_codes = bool(np.all(run["ok"] == 0))
        oks.append(ok_codes)
        report.append(f"{'PASS' if ok_codes else 'FAIL'}  {names[tag]}: every step returned success "
                      f"({int(np.sum(run['ok'] != 0))} not successful)")
        s_abs = np.max(np.abs(run["force_s"]))
        # The solver's test (NormDispIncr with MAX_TOLERANCE) bounds the displacement increments, not the force unbalance, so the
        # balance holds to about that tolerance times the stiffness. The tolerance here is MAX_TOLERANCE (see the README).
        res_axial = np.max(np.abs(run["force_a"] + run["force_s"])) / s_abs
        oks.append(bool(res_axial <= max_tolerance))
        report.append(f"{'PASS' if oks[-1] else 'FAIL'}  {names[tag]}: axial and shear balance the reference load at every step "
                      f"(A + S = 0), max relative residual {res_axial:.1e} (tol {max_tolerance:.0e})")
        lam = -run["force_s"] / (2.0 * px_ref)      # load factor: the reference load is lam * (px_ref, py_ref) at each top node
        applied_m = lam * (py_ref * (run["u3x"] + run["u4x"] + len_beam)
                           - px_ref * (2.0 * len_col + run["u3y"] + run["u4y"]))
        reacted_m = run["r1z"] + run["r2z"] + len_beam * run["r2y"]
        res_m = np.max(np.abs(reacted_m + applied_m)) / (len_beam * s_abs)
        oks.append(bool(res_m <= max_tolerance))
        report.append(f"{'PASS' if oks[-1] else 'FAIL'}  {names[tag]}: moments about the origin balance at every step, with the "
                      f"loaded nodes at their deformed positions, max relative residual {res_m:.1e} (tol {max_tolerance:.0e})")
        undeformed_m = lam * (py_ref * len_beam - px_ref * 2.0 * len_col)
        report.append(f"  {names[tag]}: moment residual with the undeformed node positions (not used): "
                      f"{np.max(np.abs(reacted_m + undeformed_m)) / (len_beam * s_abs):.1e}")

    for tag, steps in source_steps.items():
        run = results["steel01"] if tag == ODB_TAG_STEEL01 else results["hysteretic"]
        for step, (inc_ref, disp_ref, shear_ref) in steps.items():
            i = step - 1
            oks.append(check(report, f"{names[tag]}, step {step}: increment = source", run["increment"][i], inc_ref, 1.0e-12,
                             absolute=True))
            oks.append(check(report, f"{names[tag]}, step {step}: node-3 X displacement = source", run["disp_x"][i], disp_ref,
                             1.0e-6, absolute=True))
            oks.append(check(report, f"{names[tag]}, step {step}: base shear = source", run["force_s"][i], shear_ref, 1.0e-6))
        env_disp, env_shear = source_envelope[tag]
        oks.append(check(report, f"{names[tag]}: peak |displacement X| = source", np.max(np.abs(run["disp_x"])), env_disp, 1.0e-6))
        oks.append(check(report, f"{names[tag]}: peak |base shear| = source", np.max(np.abs(run["force_s"])), env_shear, 1.0e-6))
    report.append("RESULT: " + ("ALL CHECKS PASS" if all(oks) else "SOME CHECKS FAILED"))
    (output_dir / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report:
        print(line, flush=True)


# ── 13. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(output_dir)                       # opstool's working files go to output/
    results = run_analysis(output_dir)
    post_process(results, output_dir)
    validate(results, output_dir)
