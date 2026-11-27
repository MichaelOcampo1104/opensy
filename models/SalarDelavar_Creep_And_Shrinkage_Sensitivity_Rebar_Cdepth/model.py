# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D reinforced-concrete frame with time-dependent (creep and shrinkage) concrete, swept over the column rebar diameter
           and the column depth: six diameters (18 to 32 mm) by six depths (500 to 600 mm), 36 cases. Two 3 m columns (500 mm wide),
           a 7 m beam (500 mm wide, 300 mm deep) in two elements, and both column bases fixed. The beam's bars are 4 mm smaller
           than the column's. Fibre sections with TDConcrete core and cover (ACI 209R-92 creep and shrinkage), Hysteretic
           reinforcement, and corotational nonlinearBeamColumn elements with 5 integration points. The loads are applied at the
           creep age and their load factor follows the analysis time (Note 1).
UniqueID : SalarDelavar_Creep_And_Shrinkage_Sensitivity_Rebar_Cdepth
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-27
Purpose  : Sensitivity of the creep and shrinkage response of the frame to the column rebar diameter and the column depth. For each
           of the 36 cases: the largest value over the 73 load steps of the base reactions, the displacements, the rotation and the
           stiffnesses; the bilinear fit of the base shear against the node-3 displacement (ductility, over-strength factor, R and
           the stiffnesses); and the rebar ratios as the source computes them (Note 5). The source's surfaces are drawn on its own
           6 x 6 grid of cases (Note 6).
Ref      : py_ref/CONCRETE_FRAME_CREEP_AND_SHRINKAGE_SENSITIVITY_REBAR_Cdepth.py (source main), CONCRETE_SECTION_FUN.py (fibre
           section), CONCRETE_SECTION_CREEP_AND_SHRINKAGE_FUN.py (its creep section is not called by the main script; the material
           values are the main script's), ANALYSIS_FUNCTION.py (its fallback ladder is ported here, Note 3), BILINEAR_CURVE.py (fit),
           PLOT_2D.py (PLOT_2D_FRAME is not called; vis_defo gives the deformed shape), COVER.png.
           Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CREEP_AND_SHRINKAGE/CREEP_AND_SHRINKAGE_SENSITIVITY_ANALYSIS_REBAR_Cdepth
           Creep and shrinkage: https://openseespydoc.readthedocs.io/en/latest/src/TDConcrete.html
Units    : N, mm, MPa  (see standards/units.py); time in days (the TDConcrete material works in days)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import os
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops
import opstool as opst
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
ODB_TAG_FIRST_CASE = 1          # the ODB of case k (1 to 36) has tag ODB_TAG_FIRST_CASE + k - 1
NODE_BASE_L, NODE_BASE_R = 1, 2
NODE_TOP_L, NODE_TOP_R = 3, 4
NODE_MID_TOP = 5                # midspan of the beam (source node 5)
SEC_COL = 10                    # column fibre section (source secTagC)
SEC_BEAM = 20                   # beam fibre section (source secTagB)
TAG_CORE, TAG_COVER, TAG_STEEL = 1, 2, 3     # material tags (source coreTag, coverTag, steelTag)
TRANSF_COROT = 1
TS_LOAD = 1                     # Linear time series of the loads
PAT_LOAD = 1
ELE_COL_L, ELE_COL_R = 1, 2
ELE_BEAM_L, ELE_BEAM_R = 3, 4
STEEL_KIND_HYSTERETIC = 2       # the source's sensitivity loop calls its analysis with STEEL_KIND 2 only

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Lengths in mm, forces in N, stresses in MPa = N/mm². Time in days (the TDConcrete material works in days).
fc = -25.0 * MPa                 # concrete strength, negative in compression (source fc)
kfc = 1.2                        # confinement ratio of the core, for both sections (source global Kfc)
col_b = 500.0 * mm               # column section width in Z (source Bc)
col_cover = 50.0 * mm            # source coverC
beam_h = 300.0 * mm              # beam section depth in Y (source Hb)
beam_b = 500.0 * mm              # beam section width in Z (source Bb)
beam_cover = 50.0 * mm           # source coverB
beam_bar_offset = 4.0 * mm       # the beam's bars are this much smaller than the column's (source DIAb = DIAc - 4)
rebar_diameters = (18.0 * mm, 20.0 * mm, 22.0 * mm, 28.0 * mm, 30.0 * mm, 32.0 * mm)   # source DIAc
column_depths = (500.0 * mm, 510.0 * mm, 525.0 * mm, 550.0 * mm, 580.0 * mm, 600.0 * mm)  # source Hc
num_fibers = 20                  # fibres per patch along the section depth (source NUMFIBERS)
num_fibers_z = 5                 # fibres per patch across the section width (source)
bars_top = 3                     # bars in each outer layer (source)
bars_mid = 2                     # bars in the beam's middle layer (source)
num_int_points = 5               # integration points per element (source numIntgrPts)

len_col = 3000.0 * mm            # column height (source LENGTH_COL)
len_beam = 7000.0 * mm           # beam span (source LENGTH_BM)

px_top = 1.0 * N                 # horizontal load at each top node (source PX3, PX4)
py_top = -10000.0 * N            # vertical load at each top node (source PY3, PY4)
mz_top_left = -25.0e4 * N * mm   # moment at node 3 (source MZ3)
mz_top_right = 25.0e4 * N * mm   # moment at node 4 (source MZ4)

n_years = 5
tmax_days = 365.0 * n_years      # analysis time [day] (source TMAX)
tincr_days = 25.0                # time increment [day] (source TINCR)
max_iterations = 5000            # convergence iterations of the fallback tests (source MAX_ITERATIONS)
max_tolerance = 1.0e-10          # convergence tolerance of the fallback tests (source MAX_TOLERANCE)
slope_node = 10                  # index of the point at which the bilinear fit takes its slope (source SLOPE_NODE)

# TDConcrete (ACI 209R-92 creep and shrinkage; source values, shared by the core and the cover)
creep_age = 28.0                 # Tcr: creep age, and the analysis time at which the loads are first applied [day]
td_beta = 0.4                    # tension softening exponent (recommended)
td_drying_day = 14.0             # analysis time at the initiation of drying [day]
shrink_ultimate = 400.0e-6       # ultimate shrinkage strain (entered negative in the material)
shrink_psi = 64.174              # shrinkage time-evolution fitting parameter
creep_phi_ultimate = 3.0         # ultimate creep coefficient
creep_psi1 = 1.0                 # creep time-evolution fitting parameter (recommended)
creep_psi2 = 75.4218             # creep time-evolution fitting parameter (section dimensions)
casting_day = 2.0                # analysis time at casting [day] (minimum 2.0)
tension_ratio = 0.55             # tensile strength = 0.55 x compressive strength (source ftC, ftU)

# Reinforcement (source values; the Hysteretic steel)
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

RECORD_KEYS = ("time", "force_s", "force_a", "moment", "disp_x", "disp_y", "rot", "ks", "ka", "ki",
               "r1x", "r1y", "r1z", "r2x", "r2y", "r2z", "u3x", "u3y", "u4x", "u4y", "ok")


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Reset OpenSees and create a 2D model with 3 DOFs per node (source ops.model('basic', '-ndm', 2, '-ndf', 3))."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. NODES AND SUPPORTS ────────────────────────────────────────────────────
def define_nodes_and_supports() -> None:
    """Nodes of the frame (source ops.node) and the fixed column bases (source ops.fix)."""
    ops.node(NODE_BASE_L, 0.0 * mm, 0.0 * mm)
    ops.node(NODE_BASE_R, len_beam, 0.0 * mm)
    ops.node(NODE_TOP_L, 0.0 * mm, len_col)
    ops.node(NODE_TOP_R, len_beam, len_col)
    ops.node(NODE_MID_TOP, 0.5 * len_beam, len_col)
    ops.fix(NODE_BASE_L, 1, 1, 1)
    ops.fix(NODE_BASE_R, 1, 1, 1)


# ── 6. SECTIONS (MATERIALS AND FIBRES) ───────────────────────────────────────
def define_materials() -> None:
    """Materials of each case, as the source's CREEP_ANALYSIS defines them: TDConcrete for the core (confined, tag TAG_CORE)
    and the cover (unconfined, tag TAG_COVER), and the Hysteretic reinforcement (tag TAG_STEEL). The source's global values,
    with the confinement ratio kfc for the core, are used for both sections."""
    fc1_u = fc
    ec_u = 4700.0 * np.sqrt(-fc1_u) * MPa        # unconfined elastic modulus
    fc1_c = kfc * fc                             # confined compressive strength (negative)
    ec_c = 4700.0 * np.sqrt(-fc1_c) * MPa        # confined elastic modulus
    ft_c = -tension_ratio * fc1_c                # tensile strength (tension positive)
    ft_u = -tension_ratio * fc1_u
    ey = fy / es                                 # steel yield strain
    fu = fu_ratio * fy                           # steel ultimate strength
    esu = ey * esu_ratio                         # steel ultimate strain (source)
    ops.uniaxialMaterial("Hysteretic", TAG_STEEL, fy, ey, fu, esu,
                         hyst_stress_ratio * fu, hyst_strain_ratio * esu,
                         -fy, -ey, -fu, -esu,
                         -hyst_stress_ratio * fu, -hyst_strain_ratio * esu,
                         pinch_x, pinch_y, damage1, damage2, hyst_beta)
    ops.uniaxialMaterial("TDConcrete", TAG_CORE, fc1_c, ft_c, ec_c, td_beta, td_drying_day, -shrink_ultimate,
                         shrink_psi, creep_age, creep_phi_ultimate, creep_psi1, creep_psi2, casting_day)
    ops.uniaxialMaterial("TDConcrete", TAG_COVER, fc1_u, ft_u, ec_u, td_beta, td_drying_day, -shrink_ultimate,
                         shrink_psi, creep_age, creep_phi_ultimate, creep_psi1, creep_psi2, casting_day)


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
    """Corotational transformation and four nonlinearBeamColumn elements: two columns, and the beam in two halves through
    its midspan node (source ops.element('nonlinearBeamColumn', ...))."""
    ops.geomTransf("Corotational", TRANSF_COROT)
    ops.element("nonlinearBeamColumn", ELE_COL_L, NODE_BASE_L, NODE_TOP_L, num_int_points, SEC_COL, TRANSF_COROT)
    ops.element("nonlinearBeamColumn", ELE_COL_R, NODE_BASE_R, NODE_TOP_R, num_int_points, SEC_COL, TRANSF_COROT)
    ops.element("nonlinearBeamColumn", ELE_BEAM_L, NODE_TOP_L, NODE_MID_TOP, num_int_points, SEC_BEAM, TRANSF_COROT)
    ops.element("nonlinearBeamColumn", ELE_BEAM_R, NODE_MID_TOP, NODE_TOP_R, num_int_points, SEC_BEAM, TRANSF_COROT)


# ── 8. OUTPUT DATABASE (ODB) ─────────────────────────────────────────────────
def create_odb(odb_tag: int) -> "opst.post.CreateODB":
    """Nodal responses of one case, one step per load step (the source's sweep keeps its maxima only). The model data are
    saved here.

    Args:
        odb_tag: Tag of this case's ODB.

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
    """Horizontal, vertical and moment loads at the two top nodes on a Linear time series (source ops.load). The load
    factor of the Linear series is the analysis time, so the loads grow with time (Note 1)."""
    ops.timeSeries("Linear", TS_LOAD)
    ops.pattern("Plain", PAT_LOAD, TS_LOAD)
    ops.load(NODE_TOP_L, px_top, py_top, mz_top_left)
    ops.load(NODE_TOP_R, px_top, py_top, mz_top_right)


# ── 10. ANALYSIS ─────────────────────────────────────────────────────────────
def analyze_step(ok: int, increment: float, tolerance: float, max_iter: int) -> tuple:
    """Fallback ladder of the source (its ANALYSIS_FUNCTION.py). When a step does not converge, it is retried with each
    convergence test and each algorithm in turn until one converges. SmartAnalyze cannot run this load-controlled analysis
    (AGENT.md §3c), so the step loop is a manual ops.analyze loop (the exception in §3c and §10; Note 3).

    Args:
        ok: Return code of the first attempt (0 = converged).
        increment: Load-step size of each attempt.
        tolerance: Convergence tolerance of each test.
        max_iter: Maximum number of iterations of each test.

    Returns:
        (final return code, list of (test, algorithm, return code) for each attempt made; empty when ok was 0).
    """
    tests = {1: "NormDispIncr", 2: "RelativeEnergyIncr", 4: "RelativeNormUnbalance",
             5: "RelativeNormDispIncr", 6: "NormUnbalance"}
    algorithms = {1: "KrylovNewton", 2: "SecantNewton", 4: "RaphsonNewton", 5: "PeriodicNewton",
                  6: "BFGS", 7: "Broyden", 8: "NewtonLineSearch"}
    attempts = []
    for i in tests:
        for j in algorithms:
            if ok != 0:
                if j < 4:                # the first two algorithms are started with -initial (source)
                    ops.algorithm(algorithms[j], "-initial")
                else:
                    ops.algorithm(algorithms[j])
                ops.test(tests[i], tolerance, max_iter)
                ok = ops.analyze(increment)
                attempts.append((tests[i], algorithms[j], ok))
                if ok == 0:
                    break
    return ok, attempts


def bilinear_curve(cur: np.ndarray, mom: np.ndarray, node: int) -> dict:
    """Bilinear fit of a response curve (source BILINEAR_CURVE.py: equal-area, with the slope from point 'node').

    Args:
        cur: Abscissa (absolute values), e.g. the displacement.
        mom: Ordinate (absolute values), e.g. the base shear.
        node: Index of the point that gives the initial slope.

    Returns:
        Dict with the fit points X and Y, the elastic, plastic and tangent stiffnesses, the ductility and the over-strength.
    """
    size = len(mom)
    hh = np.zeros(size - 1)
    aa = np.zeros(size - 1)
    for i in range(size - 1):
        hh[i] = cur[i + 1] - cur[i]
        aa[i] = (mom[i] + mom[i + 1]) * 0.5 * hh[i]
    area = float(sum(aa))
    last = size - 1
    k0 = mom[node] / cur[node]
    fiy = (mom[last] * max(cur) * 0.5 - area) / (mom[last] * 0.5 - k0 * max(cur) * 0.5)
    my = k0 * fiy
    x = np.array([0.0, fiy, max(cur)])
    y = np.array([0.0, my, mom[last]])
    return {"x": x, "y": y, "elastic": y[1] / x[1], "plastic": y[2] / x[2],
            "tangent": (y[2] - y[1]) / (x[2] - x[1]), "ductility": x[2] / x[1], "over_strength": y[2] / y[1]}


def run_case(rebar_dia: float, col_depth: float, case_index: int, odb_tag: int, output_dir: Path | None = None) -> dict:
    """One case of the sweep: the frame with the column rebar diameter rebar_dia and the column depth col_depth, the loads
    applied at the creep age, creep switched on, and 73 load steps of 25 days (source CREEP_ANALYSIS). Each step: one
    analysis (with the fallback ladder if it does not converge), the base reactions and displacements, and one ODB step.
    The bilinear fit of the base shear is then made, as the source does.

    Args:
        rebar_dia: Column rebar diameter (mm); the beam's bars are beam_bar_offset smaller.
        col_depth: Column section depth (mm).
        case_index: Number of the case, from 1 (for the messages).
        odb_tag: Tag of this case's ODB.
        output_dir: Folder for the V1 to V4 figures, or None.

    Returns:
        Dict with the arrays of each step (keys in RECORD_KEYS), the rebar ratios RO_COL and RO_BE (as the source computes them,
        Note 5), the bilinear fit ('fit'), the ratio R (over-strength times ductility), the ODB, and the analysis messages.
    """
    as_col = np.pi * rebar_dia**2 / 4                       # bar area, column (source AsC)
    dia_beam = rebar_dia - beam_bar_offset
    as_beam = np.pi * dia_beam**2 / 4                       # bar area, beam (source AsB)
    ro_col = (8 * as_col) / (col_depth * col_b)             # source RO_COL: 8 bars for the column's 6 (Note 5)
    ro_be = (6 * as_beam) / (beam_h * beam_b)               # source RO_BE: 6 bars for the beam's 8 (Note 5)

    init_model()
    define_nodes_and_supports()
    if output_dir is not None:
        vis_nodes(output_dir)                                # V1: nodes and supports
    define_materials()
    define_fibre_section(SEC_COL, col_depth, col_b, col_cover, as_col, True)
    define_fibre_section(SEC_BEAM, beam_h, beam_b, beam_cover, as_beam, False)
    define_elements()
    if output_dir is not None:
        vis_model(output_dir)                                # V2: geometry
    define_loads()
    if output_dir is not None:
        vis_loads(output_dir)                                # V3: load vectors
    odb = create_odb(odb_tag)
    if output_dir is not None:
        vis_pre_analysis(output_dir)                         # V4: all definitions complete, before the solver
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.algorithm("Newton")
    ops.setTime(creep_age)
    ops.integrator("LoadControl", 0)
    ops.analysis("Static")
    # The loads at the creep age, creep still off (source). The source does not test this analysis: when it does not converge,
    # its load steps start from the unconverged state, with no fallback. The converted model does the same (Note 3), and records
    # the return code; the validation counts the cases concerned.
    initial_ok = ops.analyze(1)
    initial_ladder = []
    ops.setCreep(1)                                          # creep on (source)
    ops.integrator("LoadControl", tincr_days)

    steps = int(abs(tmax_days) / abs(tincr_days))
    rec = {key: [] for key in RECORD_KEYS}
    ladder = []
    for step in range(steps):
        ok = ops.analyze(1)
        ok, attempts = analyze_step(ok, 1, max_tolerance, max_iterations)
        if attempts:
            ladder.append((step + 1, attempts))
        ops.reactions()
        r1x, r1y, r1z = (ops.nodeReaction(NODE_BASE_L, dof) for dof in (1, 2, 3))
        r2x, r2y, r2z = (ops.nodeReaction(NODE_BASE_R, dof) for dof in (1, 2, 3))
        s_shear = r1x + r2x                                  # base shear (source S)
        a_axial = r1y + r2y                                  # base axial force (source A)
        m_moment = r1z + r2z                                 # base moment (source M)
        disp_x = ops.nodeDisp(NODE_TOP_L, 1)
        disp_y = ops.nodeDisp(NODE_MID_TOP, 2)
        rot = ops.nodeDisp(NODE_TOP_L, 3)
        values = {"time": ops.getTime(), "force_s": s_shear, "force_a": a_axial, "moment": m_moment,
                  "disp_x": disp_x, "disp_y": disp_y, "rot": rot,
                  "ks": abs(s_shear / disp_x), "ka": abs(a_axial / disp_y), "ki": abs(m_moment / rot),
                  "r1x": r1x, "r1y": r1y, "r1z": r1z, "r2x": r2x, "r2y": r2y, "r2z": r2z,
                  "u3x": ops.nodeDisp(NODE_TOP_L, 1), "u3y": ops.nodeDisp(NODE_TOP_L, 2),
                  "u4x": ops.nodeDisp(NODE_TOP_R, 1), "u4y": ops.nodeDisp(NODE_TOP_R, 2), "ok": ok}
        for key in RECORD_KEYS:
            rec[key].append(values[key])
        odb.fetch_response_step()

    out = {key: np.array(value) for key, value in rec.items()}
    fit = bilinear_curve(np.abs(out["disp_x"]), np.abs(out["force_s"]), slope_node)
    out.update({"odb": odb, "odb_tag": odb_tag, "index": case_index, "dia": rebar_dia, "hc": col_depth,
                "ro_col": ro_col, "ro_be": ro_be, "fit": fit, "R": fit["over_strength"] * fit["ductility"],
                "initial_ok": initial_ok, "initial_ladder": initial_ladder, "ladder": ladder})
    print(f"case {case_index:2d}: rebar {rebar_dia:.0f} mm, depth {col_depth:.0f} mm, ductility {fit['ductility']:.4f}, "
          f"over-strength {fit['over_strength']:.4f}, R {out['R']:.4f}, ladder steps {[s for s, _ in ladder]}", flush=True)
    return out


def run_sweep(output_dir: Path) -> list:
    """The 36 cases of the sweep, in the source's order: the rebar diameters outside, the column depths inside (source loops).
    The visualisation stages are written for the last case, whose curves are plotted. The model is left as the last case, so
    its printModel output is the last case's model (as in the source).

    Args:
        output_dir: Folder for the figures of the last case.

    Returns:
        List of the 36 case dicts returned by run_case().
    """
    cases = []
    index = 0
    for rebar_dia in rebar_diameters:
        for col_depth in column_depths:
            index += 1
            last = rebar_dia == rebar_diameters[-1] and col_depth == column_depths[-1]
            cases.append(run_case(rebar_dia, col_depth, index, ODB_TAG_FIRST_CASE + index - 1,
                                  output_dir if last else None))
    return cases


def run_analysis(output_dir: Path) -> list:
    """Run the 36 cases of the sweep and write the model of the last case to output/ (source printModel).

    Args:
        output_dir: Folder for the ODBs, figures and reports.

    Returns:
        The list of case dicts.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))            # direct all ODB files to output/, before any CreateODB
    cases = run_sweep(output_dir)
    ops.printModel("-JSON", "-file", str(output_dir / "CONCRETE_FRAME_CREEP_AND_SHRINKAGE_SENSITIVITY_REBAR_Cdepth.json"))
    return cases


# ── 11. POST-PROCESSING ──────────────────────────────────────────────────────
def case_table(cases: list) -> pd.DataFrame:
    """The sweep's results, one row per case, with the source's column names (its DATA_TOTAL). Each response is the largest
    absolute value over the 73 steps; the fit values are those of the case's own bilinear fit (Note 4)."""
    rows = {name: [] for name in ("DIAc", "Hc", "RO_COL", "RO_BE", "DISP_X", "DISP_Y", "ROTATION", "AXIAL_FORCE",
                                  "SHEAR_FORCE", "MOMENT_WO", "AXIAL_RIGIDITY", "ROTATIONAL_ST", "LATERAL_ST_Y",
                                  "LATERAL_ST_X", "R_MAX", "Elastic_ST_MAX", "Plastic_ST_MAX", "Tangent_ST_MAX",
                                  "Ductility_Rito_MAX", "Over_Strength_Factor_MAX", "Structural_Behavior_Coefficient_MAX")}
    for case in cases:
        rows["DIAc"].append(case["dia"] / mm)
        rows["Hc"].append(case["hc"] / mm)
        rows["RO_COL"].append(case["ro_col"])
        rows["RO_BE"].append(case["ro_be"])
        rows["DISP_X"].append(np.max(np.abs(case["disp_x"])))
        rows["DISP_Y"].append(np.max(np.abs(case["disp_y"])))
        rows["ROTATION"].append(np.max(np.abs(case["rot"])))
        rows["AXIAL_FORCE"].append(np.max(np.abs(case["force_a"])))
        rows["SHEAR_FORCE"].append(np.max(np.abs(case["force_s"])))
        rows["MOMENT_WO"].append(np.max(np.abs(case["moment"])))
        rows["AXIAL_RIGIDITY"].append(np.max(np.abs(case["force_a"])))
        rows["ROTATIONAL_ST"].append(np.max(np.abs(case["ki"])))
        rows["LATERAL_ST_Y"].append(np.max(np.abs(case["ka"])))
        rows["LATERAL_ST_X"].append(np.max(np.abs(case["ks"])))
        rows["R_MAX"].append(case["R"])
        rows["Elastic_ST_MAX"].append(case["fit"]["elastic"])
        rows["Plastic_ST_MAX"].append(case["fit"]["plastic"])
        rows["Tangent_ST_MAX"].append(case["fit"]["tangent"])
        rows["Ductility_Rito_MAX"].append(case["fit"]["ductility"])
        rows["Over_Strength_Factor_MAX"].append(case["fit"]["over_strength"])
        rows["Structural_Behavior_Coefficient_MAX"].append(case["R"])
    return pd.DataFrame(rows)


def plot_surfaces(output_dir: Path, table: pd.DataFrame) -> None:
    """The source's ten 3D contour figures of the sweep, as one HTML page with ten surfaces. The source interpolates the 36
    cases onto a 100 x 100 grid (scipy griddata, cubic); the converted surfaces are drawn on the cases' own 6 x 6 grid (Note 6).

    Args:
        output_dir: Folder where the HTML file is written.
        table: The table of case_table().
    """
    dias = [d / mm for d in rebar_diameters]
    depths = [h / mm for h in column_depths]
    quantities = [("SHEAR_FORCE", "Structure shear reaction in X [N]"),
                  ("AXIAL_FORCE", "Structure axial reaction in Y [N]"),
                  ("MOMENT_WO", "Structure moment reaction [N.mm]"),
                  ("DISP_X", "Structure displacement in X [mm]"),
                  ("DISP_Y", "Structure displacement in Y [mm]"),
                  ("Elastic_ST_MAX", "Structure elastic stiffness [N/mm]"),
                  ("Plastic_ST_MAX", "Structure plastic stiffness [N/mm]"),
                  ("Ductility_Rito_MAX", "Ductility ratio"),
                  ("Over_Strength_Factor_MAX", "Over-strength factor"),
                  ("R_MAX", "Structural behaviour coefficient R")]
    fig = make_subplots(rows=2, cols=5, specs=[[{"type": "surface"}] * 5, [{"type": "surface"}] * 5],
                        subplot_titles=[title for _, title in quantities], horizontal_spacing=0.02, vertical_spacing=0.06)
    for idx, (column, _) in enumerate(quantities):
        z = table[column].to_numpy().reshape(len(dias), len(depths))    # rows: rebar diameter, columns: depth
        row, col = divmod(idx, 5)
        fig.add_trace(go.Surface(x=depths, y=dias, z=z, colorscale="Viridis", showscale=False), row=row + 1, col=col + 1)
    fig.update_layout(height=900, width=1800, title_text="Sensitivity to the column rebar diameter (rows, mm) and the "
                                                        "column depth (columns, mm)")
    fig.write_html(str(output_dir / "vis_12_sensitivity_surfaces.html"))


def plot_correlation(output_dir: Path, table: pd.DataFrame) -> None:
    """Correlation matrix of the sweep's table, as an annotated HTML heatmap (the source's PLOT_HEATMAP)."""
    corr = table.corr()
    fig = go.Figure(go.Heatmap(z=corr.to_numpy(), x=list(corr.columns), y=list(corr.index), colorscale="Viridis",
                               text=np.round(corr.to_numpy(), 2), texttemplate="%{text}"))
    fig.update_layout(title="Correlation heatmap of the sweep", height=900, width=900, xaxis_tickangle=-90)
    fig.write_html(str(output_dir / "vis_13_correlation_heatmap.html"))


def plot_last_case(output_dir: Path, case: dict) -> None:
    """Curves and histories of the last case as HTML figures (the source's figures 1 to 12 for that case, drawn with vis_curves;
    its log axes are not reproduced)."""
    vis_curves(output_dir, panels=[
        {"x": case["moment"], "y": case["force_a"], "xlabel": "Bending moment [N.mm]", "ylabel": "Axial force [N]",
         "title": "P-M interaction"},
        {"x": case["disp_x"], "y": case["force_s"], "xlabel": "Displacement in X [mm]", "ylabel": "Shear force [N]",
         "title": "Shear force-displacement"},
        {"x": case["disp_y"], "y": case["force_a"], "xlabel": "Displacement in Y [mm]", "ylabel": "Axial force [N]",
         "title": "Axial force-displacement"},
        {"x": case["rot"], "y": case["moment"], "xlabel": "Rotation [rad]", "ylabel": "Moment [N.mm]",
         "title": "Moment-rotation"},
    ], filename="vis_08_curves_last_case.html", title="Last case: curves")
    time = case["time"]
    vis_curves(output_dir, panels=[
        {"x": time, "y": case["force_a"], "xlabel": "Time [day]", "ylabel": "Axial force [N]", "title": "Axial force"},
        {"x": time, "y": case["force_s"], "xlabel": "Time [day]", "ylabel": "Shear force [N]", "title": "Shear force"},
        {"x": time, "y": case["moment"], "xlabel": "Time [day]", "ylabel": "Moment [N.mm]", "title": "Moment"},
        {"x": time, "y": case["disp_x"], "xlabel": "Time [day]", "ylabel": "Displacement X [mm]", "title": "Displacement X"},
        {"x": time, "y": case["disp_y"], "xlabel": "Time [day]", "ylabel": "Displacement Y [mm]", "title": "Displacement Y"},
        {"x": time, "y": case["rot"], "xlabel": "Time [day]", "ylabel": "Rotation [rad]", "title": "Rotation"},
    ], filename="vis_09_history_last_case.html", title="Last case: histories")


def post_process(cases: list, table: pd.DataFrame, output_dir: Path) -> None:
    """Flush the ODBs, write the results table (CSV, in place of the source's Excel file, which needs openpyxl that the project
    environment does not have), the surfaces, the heatmap, the last case's figures and its deformed shape.

    Args:
        cases: The list of case dicts.
        table: The table of case_table().
        output_dir: Folder where the files are written.
    """
    for case in cases:
        case["odb"].save_response()                 # once per ODB, after its analysis
    table.to_csv(output_dir / "CONCRETE_FRAME_CREEP_AND_SHRINKAGE_SENSITIVITY_REBAR_Cdepth_RESULTS.csv", index=False)
    plot_surfaces(output_dir, table)
    plot_correlation(output_dir, table)
    plot_last_case(output_dir, cases[-1])
    vis_defo(output_dir, filename="vis_05_deformed_last_case.html", odb_tag=cases[-1]["odb_tag"], resp_dof="UX")


# ── 12. VALIDATION (independent checks) ─────────────────────────────────────
# The source's own run as written: its table of the 36 cases (the four corner cases are embedded here; the other 32 are
# compared outside the model, see the README), and its printed fits of the last case (the X fit, and the Y fit with its own R formula).
source_cases = {
    (18, 500): {
        "RO_COL": 0.008143008158104743,
        "RO_BE": 0.006157521601035994,
        "DISP_X": 2.1881870117444295,
        "DISP_Y": 34.65051438484942,
        "ROTATION": 0.006836265682924166,
        "AXIAL_FORCE": 37059999.99999905,
        "SHEAR_FORCE": 3706.000000002765,
        "MOMENT_WO": 26804943.615735114,
        "AXIAL_RIGIDITY": 37059999.99999905,
        "ROTATIONAL_ST": 3920992082.371714,
        "LATERAL_ST_Y": 1069536.7921061267,
        "LATERAL_ST_X": 1693.6395198910948,
        "R_MAX": 12.051139999510433,
        "Elastic_ST_MAX": 574.2657664877319,
        "Plastic_ST_MAX": 1693.6395198910948,
        "Tangent_ST_MAX": 2789.5217166315915,
        "Ductility_Rito_MAX": 2.0214362061293976,
        "Over_Strength_Factor_MAX": 5.961672182861361,
        "Structural_Behavior_Coefficient_MAX": 12.051139999510433,
    },
    (18, 600): {
        "RO_COL": 0.006785840131753953,
        "RO_BE": 0.006157521601035994,
        "DISP_X": 1.8361398270056504,
        "DISP_Y": 27.175611870059804,
        "ROTATION": 0.004360308879968024,
        "AXIAL_FORCE": 37060000.000000164,
        "SHEAR_FORCE": 3705.999999999418,
        "MOMENT_WO": 17617382.742111415,
        "AXIAL_RIGIDITY": 37060000.000000164,
        "ROTATIONAL_ST": 6418708866.251228,
        "LATERAL_ST_Y": 3795320.592838466,
        "LATERAL_ST_X": 14662.930256779095,
        "R_MAX": 8.682562354624798,
        "Elastic_ST_MAX": 585.3134812639535,
        "Plastic_ST_MAX": 2018.3648028827456,
        "Tangent_ST_MAX": 4460.568744370702,
        "Ductility_Rito_MAX": 1.5867860981117246,
        "Over_Strength_Factor_MAX": 5.471791292447701,
        "Structural_Behavior_Coefficient_MAX": 8.682562354624798,
    },
    (32, 500): {
        "RO_COL": 0.025735927018207587,
        "RO_BE": 0.024630086404143978,
        "DISP_X": 1.3118738856537329,
        "DISP_Y": 26.107178847470106,
        "ROTATION": 0.004597612306065795,
        "AXIAL_FORCE": 37059999.999998845,
        "SHEAR_FORCE": 3705.999999997497,
        "MOMENT_WO": 17376738.041689485,
        "AXIAL_RIGIDITY": 37059999.999998845,
        "ROTATIONAL_ST": 4362633938.235854,
        "LATERAL_ST_Y": 3258093.6637622877,
        "LATERAL_ST_X": 15569.943704084335,
        "R_MAX": 9.809814727879083,
        "Elastic_ST_MAX": 851.0863122347562,
        "Plastic_ST_MAX": 2824.9666683095256,
        "Tangent_ST_MAX": 5569.7562818063325,
        "Ductility_Rito_MAX": 1.7191372141488415,
        "Over_Strength_Factor_MAX": 5.7062430195462905,
        "Structural_Behavior_Coefficient_MAX": 9.809814727879083,
    },
    (32, 600): {
        "RO_COL": 0.02144660584850632,
        "RO_BE": 0.024630086404143978,
        "DISP_X": 1.1749420375494555,
        "DISP_Y": 21.27570248449844,
        "ROTATION": 0.0030106330991452666,
        "AXIAL_FORCE": 37060000.00000087,
        "SHEAR_FORCE": 3706.000000000058,
        "MOMENT_WO": 14311857.62547049,
        "AXIAL_RIGIDITY": 37060000.00000087,
        "ROTATIONAL_ST": 7514163882.154097,
        "LATERAL_ST_Y": 4202450.485995064,
        "LATERAL_ST_X": 17371.99815485323,
        "R_MAX": 8.216698803621494,
        "Elastic_ST_MAX": 868.2587837781489,
        "Plastic_ST_MAX": 3154.198148982363,
        "Tangent_ST_MAX": 7690.385760667944,
        "Ductility_Rito_MAX": 1.5039340434940238,
        "Over_Strength_Factor_MAX": 5.46347018286254,
        "Structural_Behavior_Coefficient_MAX": 8.216698803621494,
    },
}
source_last_fit_x = {"ductility": 1.5039340434940238, "over_strength": 5.46347018286254}      # the source table, last case
source_last_fit_y = {"ductility": 4.0093, "over_strength": 4.8786}      # the source printed Y fit (4 decimals)


def equilibrium_residuals(run: dict) -> tuple:
    """Force and moment residuals of the base reactions and the applied loads at every step (all must vanish). The loaded
    nodes are at their deformed positions, as the corotational analysis computes them (LESSON 118 of the creep model).

    Args:
        run: One of the case dicts returned by run_case().

    Returns:
        (residual in X, residual in Y, residual of the moments about the origin), arrays over the steps, in N and N.mm.
    """
    t = run["time"]
    fx = 2.0 * px_top * t
    fy = 2.0 * py_top * t
    res_x = run["force_s"] + fx
    res_y = run["force_a"] + fy
    applied_m = (run["u3x"] * (py_top * t) - (len_col + run["u3y"]) * (px_top * t) + mz_top_left * t
                 + (len_beam + run["u4x"]) * (py_top * t) - (len_col + run["u4y"]) * (px_top * t) + mz_top_right * t)
    reacted_m = run["r1z"] + run["r2z"] + len_beam * run["r2y"]
    res_m = reacted_m + applied_m
    return res_x, res_y, res_m


def check(report: list, name: str, value: float, reference: float, tol: float) -> bool:
    """Compare two values by relative difference and record the line in the report.

    Args:
        report: Report lines (appended to).
        name: Label of the check.
        value: Value from the model.
        reference: Reference value.
        tol: Relative tolerance.

    Returns:
        True when the check passes.
    """
    rel = abs(value - reference) / max(abs(reference), 1.0e-300)
    ok = rel <= tol
    report.append(f"{'PASS' if ok else 'FAIL'}  {name}: {value:.10e} vs {reference:.10e} (relative {rel:.1e}, tolerance {tol:.0e})")
    return ok


def validate(cases: list, table: pd.DataFrame, output_dir: Path) -> None:
    """Checks of the sweep: the time sequence and the equilibrium of every case at every step, the fallback-ladder use, the
    table's values for the embedded source cases, the last case's printed fits, and the internal consistency of the table
    (R = over-strength x ductility; the rebar ratios). Writes output/validation.txt and prints it.

    Args:
        cases: The list of case dicts.
        table: The table of case_table().
        output_dir: Folder where validation.txt is written.
    """
    report, oks = [], []
    report.append("RESULTS")
    n_ladder = sum(1 for c in cases if c["ladder"])
    n_initial = sum(1 for c in cases if c["initial_ok"] != 0)
    n_unconverged = int(sum(int(np.sum(c["ok"] != 0)) for c in cases))
    report.append(f"  {len(cases)} cases; cases needing the fallback ladder in a load step: {n_ladder}; cases whose analysis at "
                  f"the creep age did not converge (carried forward unchecked, as in the source): {n_initial}; steps not "
                  f"converged after the ladder, all cases: {n_unconverged}")
    last = table.iloc[-1]
    report.append(f"  last case (rebar {last['DIAc']:.0f} mm, depth {last['Hc']:.0f} mm): ductility "
                  f"{last['Ductility_Rito_MAX']:.4f}, over-strength {last['Over_Strength_Factor_MAX']:.4f}, R {last['R_MAX']:.4f}")
    report.append(f"  table: largest shear reaction {table['SHEAR_FORCE'].max():.6e} N, largest axial reaction "
                  f"{table['AXIAL_FORCE'].max():.6e} N, largest displacement in X {table['DISP_X'].max():.4f} mm")

    report.append("CHECKS")
    for case in cases:
        t = case["time"]
        expected = creep_age + tincr_days * np.arange(1, len(t) + 1)
        oks.append(abs(t[-1] - expected[-1]) <= 1.0e-12 and np.all(np.abs(t - expected) <= 1.0e-12))
    report.append(f"{'PASS' if all(oks[-len(cases):]) else 'FAIL'}  time sequence 28 + 25n, all {len(cases)} cases")
    worst = {"X force": 0.0, "Y force": 0.0, "moment": 0.0}
    for case in cases:
        t = case["time"]
        rx, ry, rm = equilibrium_residuals(case)
        worst["X force"] = max(worst["X force"], float(np.max(np.abs(rx) / np.maximum(np.abs(2.0 * px_top * t), 1.0))))
        worst["Y force"] = max(worst["Y force"], float(np.max(np.abs(ry) / np.abs(2.0 * py_top * t))))
        worst["moment"] = max(worst["moment"], float(np.max(np.abs(rm) / np.abs(len_beam * 2.0 * py_top * t))))
    for label, value in worst.items():
        ok = value <= 1.0e-9
        oks.append(ok)
        report.append(f"{'PASS' if ok else 'FAIL'}  equilibrium of the {label} at every step of every case, max relative "
                      f"residual {value:.1e} (tol 1e-09)")
    ok = n_unconverged == 0
    oks.append(ok)
    report.append(f"{'PASS' if ok else 'FAIL'}  every step converged, with or without the fallback ladder")
    finite = bool(np.all(np.isfinite(table.to_numpy(dtype=float))))
    oks.append(finite)
    report.append(f"{'PASS' if finite else 'FAIL'}  the table is finite for all cases")
    r_ok = bool(np.allclose(table["R_MAX"], table["Over_Strength_Factor_MAX"] * table["Ductility_Rito_MAX"], rtol=1e-12))
    oks.append(r_ok)
    report.append(f"{'PASS' if r_ok else 'FAIL'}  R = over-strength x ductility for all cases")
    ro_ok = True
    for case in cases:
        as_col = np.pi * case["dia"]**2 / 4
        ro_ok = ro_ok and abs(case["ro_col"] - 8 * as_col / (case["hc"] * col_b)) <= 1e-15
    oks.append(ro_ok)
    report.append(f"{'PASS' if ro_ok else 'FAIL'}  rebar ratio RO_COL = 8 A_bar / (Hc Bc) as the source writes it (Note 5)")

    for (dia, depth), reference in source_cases.items():
        row = table[(np.isclose(table["DIAc"], dia)) & (np.isclose(table["Hc"], depth))].iloc[0]
        for column, ref_value in reference.items():
            oks.append(check(report, f"source case rebar {dia:.0f} mm, depth {depth:.0f} mm: {column}",
                             row[column], ref_value, 1.0e-9))
    fit_x = cases[-1]["fit"]
    oks.append(check(report, "last case, X fit ductility = source (4 decimals)", fit_x["ductility"],
                     source_last_fit_x["ductility"], 1.0e-4))
    oks.append(check(report, "last case, X fit over-strength = source (4 decimals)", fit_x["over_strength"],
                     source_last_fit_x["over_strength"], 1.0e-4))
    fit_y = bilinear_curve(np.abs(cases[-1]["disp_y"]), np.abs(cases[-1]["force_a"]), slope_node)
    oks.append(check(report, "last case, Y fit ductility = source (4 decimals)", fit_y["ductility"],
                     source_last_fit_y["ductility"], 1.0e-4))
    oks.append(check(report, "last case, Y fit over-strength = source (4 decimals)", fit_y["over_strength"],
                     source_last_fit_y["over_strength"], 1.0e-4))
    report.append(f"INFO  the source's Y fit uses R = Omega x (2 mu - 1)^0.5 / mu^0.5 as its ductility coefficient; here R = "
                  f"Omega x mu for both fits (Note 2): the Y fit's R is {fit_y['over_strength'] * fit_y['ductility']:.4f} here and "
                  f"{fit_y['over_strength'] * (2 * fit_y['ductility'] - 1) ** 0.5 / fit_y['ductility'] ** 0.5:.4f} with the source's "
                  "formula")
    report.append("RESULT: " + ("ALL CHECKS PASS" if all(oks) else "SOME CHECKS FAILED"))
    (output_dir / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report:
        print(line, flush=True)


# ── 13. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(output_dir)                       # opstool's working files go to output/
    cases = run_analysis(output_dir)
    table = case_table(cases)
    post_process(cases, table, output_dir)
    validate(cases, table, output_dir)
