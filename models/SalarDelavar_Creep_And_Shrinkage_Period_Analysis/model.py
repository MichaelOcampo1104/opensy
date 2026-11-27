# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D reinforced-concrete frame with time-dependent (creep and shrinkage) concrete, and its structural periods. Two
           3 m columns (500 x 500 mm) and a 7 m beam (500 mm wide, 300 mm deep) in two elements, both column bases fixed. The top
           nodes carry lumped masses. Fibre sections with TDConcrete core and cover concrete (ACI 209R-92 creep and shrinkage) and
           rebar as Steel01 or Hysteretic; corotational nonlinearBeamColumn elements with 5 integration points and 20 fibres per
           patch. The loads are applied at the creep age and their load factor follows the analysis time (Note 1).
UniqueID : SalarDelavar_Creep_And_Shrinkage_Period_Analysis
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-26
Purpose  : Structural periods of the creep and shrinkage analysis: the first four periods at each of 73 load steps over 5 years of
           analysis time, for the two reinforcement models, with the base reactions and displacements of each step and the
           bilinear fits of the Steel01 run. The source's period figure is redrawn with each run's own displacements (Note 6).
Ref      : py_ref/CONCRETE_FRAME_CREEP_AND_SHRINKAGE_PERIOD.py (source main), CONCRETE_SECTION_CREEP_AND_SHRINKAGE_FUN.py (section),
           EIGENVALUE_ANALYSIS_FUN.py (periods, ported as eigen_periods), ANALYSIS_FUNCTION.py (its fallback ladder is ported here,
           Note 3), BILINEAR_CURVE.py (fit), PLOT_2D.py (PLOT_2D_FRAME is not called; vis_defo gives the deformed shape), COVER_CREEP.png.
           Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CREEP_AND_SHRINKAGE/CREEP_AND_SHRINKAGE_ANALYSIS_PERIOD
           Creep and shrinkage: https://openseespydoc.readthedocs.io/en/latest/src/TDConcrete.html
Units    : N, mm, MPa  (see standards/units.py); time in days (the TDConcrete material works in days); masses in N.s^2/mm (Note 4)
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
ODB_TAG_STEEL01 = 1             # main run, Steel01 reinforcement (source WITHOUT HARDENING AND ULTIMATE STRAIN)
ODB_TAG_HYSTERETIC = 2          # main run, Hysteretic reinforcement (source WITH HARDENING AND ULTIMATE STRAIN)
ODB_TAG_CHECK = 3               # check run: Steel01, the source's mass and the beam's Kfc of 1.2 (Note 2 and Note 4)
NODE_BASE_L, NODE_BASE_R = 1, 2
NODE_TOP_L, NODE_TOP_R = 3, 4
NODE_MID_TOP = 5                # midspan of the beam (source node 5)
SEC_COL = 10                    # column fibre section (source secTagC)
SEC_BEAM = 20                   # beam fibre section (source secTagB)
OFFSET_CORE, OFFSET_COVER, OFFSET_STEEL = 1, 2, 3    # material tags = section tag + offset (source)
TRANSF_COROT = 1
TS_LOAD = 1                     # Linear time series of the loads
PAT_LOAD = 1
ELE_COL_L, ELE_COL_R = 1, 2
ELE_BEAM_L, ELE_BEAM_R = 3, 4
STEEL_KIND_STEEL01 = 1          # source STEEL_KIND 1
STEEL_KIND_HYSTERETIC = 2       # source STEEL_KIND 2

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Lengths in mm, forces in N, stresses in MPa = N/mm². Time in days (the TDConcrete material works in days).
fc = -25.0 * MPa                 # concrete strength, negative in compression (source fc)
col_h = 500.0 * mm               # column section depth in Y (source Hc)
col_b = 500.0 * mm               # column section width in Z (source Bc)
col_cover = 50.0 * mm            # source coverC
col_bar_dia = 25.0 * mm          # source DIAc
beam_h = 300.0 * mm              # beam section depth in Y (source Hb)
beam_b = 500.0 * mm              # beam section width in Z (source Bb)
beam_cover = 50.0 * mm           # source coverB
beam_bar_dia = 18.0 * mm         # source DIAb
as_col_bar = np.pi * col_bar_dia**2 / 4        # bar area, column (source AsC)
as_beam_bar = np.pi * beam_bar_dia**2 / 4      # bar area, beam (source AsB)
bars_top = 3                     # bars in each outer layer (source)
bars_mid = 2                     # bars in the beam's middle layer (source)
num_fibers = 20                  # fibres per patch along the section depth (source NUMFIBERS)
num_fibers_z = 5                 # fibres per patch across the section width (source)
num_int_points = 5               # integration points per element (source numIntgrPts)
kfc_col = 1.2                    # column confinement ratio (source call)
kfc_beam = 1.1                   # beam confinement ratio (source call; the source's section function uses 1.2, Note 2)
kfc_beam_as_computed = 1.2       # the value the source's section function actually uses for the beam (check run)

# Nodal mass at nodes 3 and 4 (X and Y). The source writes MASS = 10000.0 with the label [kg]. In the N-mm-s system
# 1 N·s²/mm = 1000 kg, so 10000 kg = 10 N·s²/mm (AGENT.md §12j, as for the CQC model). The source's value is kept for the check.
mass_node_si = 10000.0 / 1000.0          # 10 N·s²/mm per node (converted)
mass_node_as_written = 10000.0           # the source's value taken as N·s²/mm (check run only)
num_eigen = 4                            # modes per eigenvalue analysis (source N_DOF)
hyst_esu = 0.12                          # Hysteretic: ultimate strain of the steel (source esu = .12)

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

# Reinforcement (source values)
fy = 4000.0 * MPa                # steel yield strength
es = 2.0e5 * MPa                 # steel modulus of elasticity
fu_ratio = 1.1818                # ultimate strength / yield strength
hyst_stress_ratio = 0.2          # Hysteretic: second point at 0.2 f_u
hyst_strain_ratio = 1.1          # Hysteretic: second point at 1.1 e_su
pinch_x = 0.8                    # Hysteretic pinching factor in X
pinch_y = 0.5                    # Hysteretic pinching factor in Y
damage1 = 0.0                    # Hysteretic damage due to ductility
damage2 = 0.0                    # Hysteretic damage due to energy
hyst_beta = 0.1                  # Hysteretic stiffness degradation parameter

# Elastic check frame (validate only): concrete modulus of the cover (4700 sqrt(fc)) on gross sections
check_modulus = 4700.0 * np.sqrt(-fc / MPa) * MPa

RECORD_KEYS = ("time", "force_s", "force_a", "moment", "disp_x", "disp_y", "rot", "ks", "ka", "ki",
               "period_min", "period_max",
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


def define_nodal_masses(mass: float) -> None:
    """Lumped masses at the two top nodes in X and Y, none in rotation (source ops.mass(3, MASS, MASS, 0.0) and node 4).

    Args:
        mass: Nodal mass in N·s²/mm (1 N·s²/mm = 1000 kg).
    """
    ops.mass(NODE_TOP_L, mass, mass, 0.0)
    ops.mass(NODE_TOP_R, mass, mass, 0.0)


# ── 6. SECTIONS (MATERIALS AND FIBRES) ───────────────────────────────────────
def define_section(sec_tag: int, h: float, b: float, cover: float, bar_area: float, steel_kind: int,
                   is_column: bool, kfc: float) -> float:
    """Fibre section of a reinforced-concrete member with TDConcrete core and cover concrete and steel rebar (source
    CONFINED_CONCRETE_CREEP_AND_SHRINKAGE_SECTION, with the same material values).

    Args:
        sec_tag: Section tag (the material tags are sec_tag + offset).
        h: Section extent in Y, the depth that bends about Z (mm).
        b: Section extent in Z (mm).
        cover: Concrete cover (mm).
        bar_area: Area of one rebar (mm²).
        steel_kind: STEEL_KIND_STEEL01 or STEEL_KIND_HYSTERETIC.
        is_column: True for a column (three bars per face); False for the beam (a middle layer of two bars as well).
        kfc: Ratio of the confined to the unconfined concrete strength (the source's section function uses 1.2 whatever
            is passed; see Note 2).

    Returns:
        The creep age of the section, in days (source Tcr).
    """
    fc1_u = fc                           # unconfined compressive strength (negative)
    ec_u = 4700.0 * np.sqrt(-fc1_u) * MPa        # unconfined elastic modulus
    fc1_c = kfc * fc                     # confined compressive strength (negative)
    ec_c = 4700.0 * np.sqrt(-fc1_c) * MPa        # confined elastic modulus
    ft_c = -tension_ratio * fc1_c        # tensile strength (tension positive)
    ft_u = -tension_ratio * fc1_u
    ey = fy / es                         # steel yield strain
    fu = fu_ratio * fy                   # steel ultimate strength
    esu = hyst_esu                       # steel ultimate strain (source esu)

    core_tag = sec_tag + OFFSET_CORE
    cover_tag = sec_tag + OFFSET_COVER
    steel_tag = sec_tag + OFFSET_STEEL
    if steel_kind == STEEL_KIND_STEEL01:
        ops.uniaxialMaterial("Steel01", steel_tag, fy, es, 0.0)
    elif steel_kind == STEEL_KIND_HYSTERETIC:
        ops.uniaxialMaterial("Hysteretic", steel_tag, fy, ey, fu, esu,
                             hyst_stress_ratio * fu, hyst_strain_ratio * esu,
                             -fy, -ey, -fu, -esu,
                             -hyst_stress_ratio * fu, -hyst_strain_ratio * esu,
                             pinch_x, pinch_y, damage1, damage2, hyst_beta)
    else:
        raise ValueError(f"unknown steel kind {steel_kind}")
    # Time-dependent concrete: core (confined) and cover (unconfined); shrinkage is entered negative
    ops.uniaxialMaterial("TDConcrete", core_tag, fc1_c, ft_c, ec_c, td_beta, td_drying_day, -shrink_ultimate,
                         shrink_psi, creep_age, creep_phi_ultimate, creep_psi1, creep_psi2, casting_day)
    ops.uniaxialMaterial("TDConcrete", cover_tag, fc1_u, ft_u, ec_u, td_beta, td_drying_day, -shrink_ultimate,
                         shrink_psi, creep_age, creep_phi_ultimate, creep_psi1, creep_psi2, casting_day)

    y1 = h / 2.0
    z1 = b / 2.0
    ops.section("Fiber", sec_tag)
    ops.patch("rect", core_tag, num_fibers, num_fibers_z, cover - y1, cover - z1, y1 - cover, z1 - cover)
    ops.patch("rect", cover_tag, num_fibers, num_fibers_z, -y1, z1 - cover, y1, z1)
    ops.patch("rect", cover_tag, num_fibers, num_fibers_z, -y1, -z1, y1, cover - z1)
    ops.patch("rect", cover_tag, num_fibers, num_fibers_z, -y1, cover - z1, cover - y1, z1 - cover)
    ops.patch("rect", cover_tag, num_fibers, num_fibers_z, y1 - cover, cover - z1, y1, z1 - cover)
    ops.layer("straight", steel_tag, bars_top, bar_area, y1 - cover, z1 - cover, y1 - cover, cover - z1)
    if not is_column:
        ops.layer("straight", steel_tag, bars_mid, bar_area, 0.0, z1 - cover, 0.0, cover - z1)
    ops.layer("straight", steel_tag, bars_top, bar_area, cover - y1, z1 - cover, cover - y1, cover - z1)
    return creep_age


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
    """Nodal and frame responses of one analysis, one step per load step. The model data are saved here.

    Args:
        odb_tag: Tag of this analysis (one ODB per analysis, because each analysis rebuilds the model).

    Returns:
        The CreateODB instance.
    """
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=True,
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


def eigen_periods(num: int) -> np.ndarray:
    """Periods of the first num modes of the current model, from the source's ops.eigen('-fullGenLapack', N_DOF) (its
    EIGENVALUE_ANALYSIS_FUN.py): period = 2 pi / sqrt(lambda). The eigenvalues are in ascending order, so the periods are
    in descending order (Note 5).

    Args:
        num: Number of modes.

    Returns:
        Array of the periods, in seconds.
    """
    lam = np.array(ops.eigen("-fullGenLapack", num))
    return 2.0 * np.pi / np.sqrt(lam)


def build_model(steel_kind: int, kfc_beam_value: float, mass: float, output_dir: Path | None = None) -> None:
    """Build the frame, its two fibre sections, its masses and its loads. The visualisation stages V1 to V3 are written when
    output_dir is given.

    Args:
        steel_kind: STEEL_KIND_STEEL01 or STEEL_KIND_HYSTERETIC.
        kfc_beam_value: Confinement ratio of the beam section.
        mass: Nodal mass at nodes 3 and 4, in N·s²/mm.
        output_dir: Folder for the V1 to V3 HTML files, or None to skip them.
    """
    init_model()
    define_nodes_and_supports()
    if output_dir is not None:
        vis_nodes(output_dir)                  # V1: nodes and supports
    define_section(SEC_COL, col_h, col_b, col_cover, as_col_bar, steel_kind, True, kfc_col)
    define_section(SEC_BEAM, beam_h, beam_b, beam_cover, as_beam_bar, steel_kind, False, kfc_beam_value)
    define_elements()
    if output_dir is not None:
        vis_model(output_dir)                  # V2: geometry
    define_nodal_masses(mass)
    define_loads()
    if output_dir is not None:
        vis_loads(output_dir)                  # V3: load vectors


def run_creep(steel_kind: int, kfc_beam_value: float, mass: float, odb_tag: int, output_dir: Path | None = None) -> dict:
    """Run the creep and shrinkage analysis: the loads applied at the creep age, creep switched on, then load steps of
    25 days up to 5 years (source CREEP_ANALYSIS). Each step: one analysis (with the fallback ladder if it does not
    converge), the base reactions, the displacements and rotation, the first periods of the structure at that state,
    and one ODB step.

    Args:
        steel_kind: STEEL_KIND_STEEL01 or STEEL_KIND_HYSTERETIC.
        kfc_beam_value: Confinement ratio of the beam section.
        mass: Nodal mass at nodes 3 and 4, in N·s²/mm.
        odb_tag: Tag of this analysis' ODB.
        output_dir: Folder for the V1 to V4 figures, or None for a check run.

    Returns:
        Dict of arrays per step (keys in RECORD_KEYS, with the source's names: force_s is the base shear in X, force_a the
        base axial force, moment the base moment, ks, ka and ki the stiffnesses, period_min and period_max the smallest and
        largest of the modal periods), plus 'periods' (the array of all the periods, one row per step), 'odb', 'initial_ok'
        and 'initial_ladder' (the return code and the fallback attempts of the analysis at the creep age) and 'ladder' (the
        steps that needed the fallback ladder).
    """
    build_model(steel_kind, kfc_beam_value, mass, output_dir)
    odb = create_odb(odb_tag)
    if output_dir is not None:
        vis_pre_analysis(output_dir)           # V4: all definitions complete, before the solver
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.algorithm("Newton")
    ops.setTime(creep_age)
    ops.integrator("LoadControl", 0)
    ops.analysis("Static")
    # the loads at the creep age, creep still off (source). The source does not test this analysis; here it gets the same
    # fallback ladder as the steps, so a failure is not carried forward unchecked (Note 3).
    initial_ok, initial_ladder = analyze_step(ops.analyze(1), 1, max_tolerance, max_iterations)
    ops.setCreep(1)                            # creep on (source)
    ops.integrator("LoadControl", tincr_days)

    steps = int(abs(tmax_days) / abs(tincr_days))
    rec = {key: [] for key in RECORD_KEYS}
    periods_all = []
    ladder = []
    for step in range(steps):
        ok = ops.analyze(1)
        ok, attempts = analyze_step(ok, 1, max_tolerance, max_iterations)
        if attempts:
            ladder.append((step + 1, attempts))
            print(f"step {step + 1}: fallback ladder, attempts {attempts}", flush=True)
        ops.reactions()
        r1x, r1y, r1z = (ops.nodeReaction(NODE_BASE_L, dof) for dof in (1, 2, 3))
        r2x, r2y, r2z = (ops.nodeReaction(NODE_BASE_R, dof) for dof in (1, 2, 3))
        s_shear = r1x + r2x                    # base shear (source S)
        a_axial = r1y + r2y                    # base axial force (source A)
        m_moment = r1z + r2z                   # base moment (source M)
        disp_x = ops.nodeDisp(NODE_TOP_L, 1)
        disp_y = ops.nodeDisp(NODE_MID_TOP, 2)
        rot = ops.nodeDisp(NODE_TOP_L, 3)
        periods = eigen_periods(num_eigen)     # source EIGENVALUE_ANALYSIS at this step (Note 5)
        periods_all.append(periods)
        values = {"time": ops.getTime(), "force_s": s_shear, "force_a": a_axial, "moment": m_moment,
                  "disp_x": disp_x, "disp_y": disp_y, "rot": rot,
                  "ks": abs(s_shear / disp_x), "ka": abs(a_axial / disp_y), "ki": abs(m_moment / rot),
                  "period_min": float(np.min(periods)), "period_max": float(np.max(periods)),
                  "r1x": r1x, "r1y": r1y, "r1z": r1z, "r2x": r2x, "r2y": r2y, "r2z": r2z,
                  "u3x": ops.nodeDisp(NODE_TOP_L, 1), "u3y": ops.nodeDisp(NODE_TOP_L, 2),
                  "u4x": ops.nodeDisp(NODE_TOP_R, 1), "u4y": ops.nodeDisp(NODE_TOP_R, 2), "ok": ok}
        for key in RECORD_KEYS:
            rec[key].append(values[key])
        odb.fetch_response_step()
        print(step + 1, disp_x, disp_y, s_shear, a_axial, flush=True)

    out = {key: np.array(value) for key, value in rec.items()}
    out.update({"odb": odb, "initial_ok": initial_ok, "initial_ladder": initial_ladder, "ladder": ladder,
                "periods": np.array(periods_all)})
    return out


def run_analysis(output_dir: Path) -> dict:
    """Run the two main analyses (Steel01 and Hysteretic reinforcement, as in the source) and the check run (Steel01 with the
    source's mass and the beam's Kfc of 1.2 that the source computes), then return them.

    Args:
        output_dir: Folder for the ODB, figures and reports.

    Returns:
        Dict with the runs under the keys "steel01", "hysteretic" and "check".
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))            # direct all ODB files to output/, before any CreateODB
    steel01 = run_creep(STEEL_KIND_STEEL01, kfc_beam, mass_node_si, ODB_TAG_STEEL01, output_dir)
    hysteretic = run_creep(STEEL_KIND_HYSTERETIC, kfc_beam, mass_node_si, ODB_TAG_HYSTERETIC)
    ops.printModel("-JSON", "-file", str(output_dir / "CONCRETE_FRAME_CREEP_AND_SHRINKAGE_PERIOD.json"))   # last main model
    check = run_creep(STEEL_KIND_STEEL01, kfc_beam_as_computed, mass_node_as_written, ODB_TAG_CHECK)
    return {"steel01": steel01, "hysteretic": hysteretic, "check": check}


# ── 11. POST-PROCESSING ──────────────────────────────────────────────────────
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


def fits_of(run: dict) -> tuple:
    """Bilinear fits of the Steel01 run in X (base shear against the node-3 displacement) and in Y (base axial force against
    the node-5 displacement), as the source plots them."""
    fit_x = bilinear_curve(np.abs(run["disp_x"]), np.abs(run["force_s"]), slope_node)
    fit_y = bilinear_curve(np.abs(run["disp_y"]), np.abs(run["force_a"]), slope_node)
    return fit_x, fit_y


def plot_run(output_dir: Path, run: dict, label: str, tag: str) -> None:
    """Curves, periods and histories of one run as HTML figures (the source's matplotlib figures; its log axes are not
    reproduced).

    Args:
        output_dir: Folder where the HTML files are written.
        run: One of the dicts returned by run_creep().
        label: Title prefix of the figures.
        tag: File name tag (e.g. steel01).
    """
    vis_curves(output_dir, panels=[
        {"x": run["moment"], "y": run["force_a"], "xlabel": "Bending moment [N.mm]", "ylabel": "Axial force [N]",
         "title": "P-M interaction"},
        {"x": run["disp_x"], "y": run["force_s"], "xlabel": "Displacement in X [mm], node 3", "ylabel": "Shear force [N]",
         "title": "Shear force-displacement"},
        {"x": run["disp_y"], "y": run["force_a"], "xlabel": "Displacement in Y [mm], node 5", "ylabel": "Axial force [N]",
         "title": "Axial force-displacement"},
        {"x": run["rot"], "y": run["moment"], "xlabel": "Rotation [rad]", "ylabel": "Moment [N.mm]",
         "title": "Moment-rotation"},
    ], filename=f"vis_08_curves_{tag}.html", title=f"{label}: curves")
    vis_curves(output_dir, panels=[
        {"x": run["disp_x"], "y": run["period_min"], "xlabel": "Displacement in X [mm], node 3",
         "ylabel": "Period [s]", "title": "Smallest of the four periods"},
        {"x": run["disp_x"], "y": run["period_max"], "xlabel": "Displacement in X [mm], node 3",
         "ylabel": "Period [s]", "title": "Largest of the four periods"},
        {"x": run["time"], "y": run["period_max"], "xlabel": "Time [day]", "ylabel": "Period [s]",
         "title": "Largest period against time"},
    ], filename=f"vis_10_period_{tag}.html", title=f"{label}: structural periods (each run against its own displacement)")
    time = run["time"]
    vis_curves(output_dir, panels=[
        {"x": time, "y": run["force_a"], "xlabel": "Time [day]", "ylabel": "Axial force [N]", "title": "Axial force"},
        {"x": time, "y": run["force_s"], "xlabel": "Time [day]", "ylabel": "Shear force [N]", "title": "Shear force"},
        {"x": time, "y": run["moment"], "xlabel": "Time [day]", "ylabel": "Moment [N.mm]", "title": "Moment"},
        {"x": time, "y": run["disp_x"], "xlabel": "Time [day]", "ylabel": "Displacement X [mm]", "title": "Displacement X"},
        {"x": time, "y": run["disp_y"], "xlabel": "Time [day]", "ylabel": "Displacement Y [mm]", "title": "Displacement Y"},
        {"x": time, "y": run["rot"], "xlabel": "Time [day]", "ylabel": "Rotation [rad]", "title": "Rotation"},
    ], filename=f"vis_09_history_{tag}.html", title=f"{label}: histories")


def post_process(results: dict, output_dir: Path) -> None:
    """Flush the three ODBs, write the results table (CSV, in place of the source's Excel file, which needs openpyxl that the
    project environment does not have), the deformed shape and the figures.

    Args:
        results: Output of run_analysis().
        output_dir: Folder where the ODB, CSV and HTML files are written.
    """
    for key in ("steel01", "hysteretic", "check"):
        results[key]["odb"].save_response()    # once per ODB, after its analysis
    s01, hy = results["steel01"], results["hysteretic"]
    table = {
        "TIME_DAY": s01["time"],
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
        "PERIOD_MIN_WO": s01["period_min"], "PERIOD_MIN_W": hy["period_min"],
        "PERIOD_MAX_WO": s01["period_max"], "PERIOD_MAX_W": hy["period_max"],
    }
    pd.DataFrame(table).to_csv(output_dir / "CONCRETE_FRAME_CREEP_AND_SHRINKAGE_PERIOD_RESULTS.csv", index=False)
    vis_defo(output_dir, filename="vis_05_deformed_steel01.html", odb_tag=ODB_TAG_STEEL01, resp_dof="UX")
    plot_run(output_dir, s01, "Steel01 (without hardening and ultimate strain)", "steel01")
    plot_run(output_dir, hy, "Hysteretic (with hardening and ultimate strain)", "hysteretic")


# ── 12. VALIDATION (independent checks) ─────────────────────────────────────
# The source's own run as written (its printed Steel01 values at steps 1, 2 and 73, its printed bilinear fits, and its printed
# periods, the four modes of each step, at steps 1, 2 and 73 of the Steel01 run; the printed values have four decimals).
source_steps = {
    1: (0.4798340808018714, -1.280262884452544, -105.99999999983947, 1059999.9999993038),
    2: (0.6053305620141646, -1.8197138927907728, -155.99999999983083, 1560000.0000002454),
    73: (1.841718526260877, -30.493871728525875, -3705.999999999942, 37060000.00000039),
}
source_periods = {
    1: (4.2107, 0.5752, 0.4166, 0.4165),
    2: (4.2181, 0.5753, 0.4166, 0.4165),
    73: (4.8876, 0.5783, 0.4166, 0.4165),
}
source_fit_x = {"ductility": 1.7728, "over_strength": 5.5951, "r": 9.9190}
source_fit_y = {"ductility": 3.8682, "over_strength": 4.4667, "r": 17.2781}


def equilibrium_residuals(run: dict) -> tuple:
    """Force and moment residuals of the base reactions and the applied loads at every step (all must vanish). The loaded
    nodes are at their deformed positions, as the corotational analysis computes them (LESSON 118 of the creep model).

    Args:
        run: One of the dicts returned by run_creep().

    Returns:
        (residual in X, residual in Y, residual of the moments about the origin), arrays over the steps, in N and N.mm.
    """
    t = run["time"]
    fx = 2.0 * px_top * t                          # applied X loads, both top nodes
    fy = 2.0 * py_top * t                          # applied Y loads, both top nodes
    res_x = run["force_s"] + fx
    res_y = run["force_a"] + fy
    applied_m = (run["u3x"] * (py_top * t) - (len_col + run["u3y"]) * (px_top * t) + mz_top_left * t
                 + (len_beam + run["u4x"]) * (py_top * t) - (len_col + run["u4y"]) * (px_top * t) + mz_top_right * t)
    reacted_m = run["r1z"] + run["r2z"] + len_beam * run["r2y"]
    res_m = reacted_m + applied_m
    return res_x, res_y, res_m


def gross_section_properties() -> tuple:
    """Gross area and second moment of area of the column and of the beam (mm², mm⁴), for the elastic check frame."""
    area_col = col_b * col_h
    inertia_col = col_b * col_h**3 / 12
    area_beam = beam_b * beam_h
    inertia_beam = beam_b * beam_h**3 / 12
    return area_col, inertia_col, area_beam, inertia_beam


def element_global_stiffness(node_i: tuple, node_j: tuple, ea: float, ei: float) -> tuple:
    """Global 6 x 6 stiffness of an elastic 2D beam-column (Euler-Bernoulli).

    Args:
        node_i: (x, y) of the first node.
        node_j: (x, y) of the second node.
        ea: Axial stiffness E A (N).
        ei: Flexural stiffness E I (N mm²).

    Returns:
        (global stiffness, local stiffness, transformation matrix).
    """
    dx = node_j[0] - node_i[0]
    dy = node_j[1] - node_i[1]
    length = float(np.hypot(dx, dy))
    c, s = dx / length, dy / length
    a = ea / length
    b = 12.0 * ei / length**3
    d = 6.0 * ei / length**2
    e = 4.0 * ei / length
    f = 2.0 * ei / length
    k_local = np.array([
        [a, 0.0, 0.0, -a, 0.0, 0.0],
        [0.0, b, d, 0.0, -b, d],
        [0.0, d, e, 0.0, -d, f],
        [-a, 0.0, 0.0, a, 0.0, 0.0],
        [0.0, -b, -d, 0.0, b, -d],
        [0.0, d, f, 0.0, -d, e],
    ])
    t = np.array([
        [c, s, 0.0, 0.0, 0.0, 0.0],
        [-s, c, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, c, s, 0.0],
        [0.0, 0.0, 0.0, -s, c, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    ])
    return t.T @ k_local @ t, k_local, t


def build_elastic_frame(mass: float) -> None:
    """Elastic check frame: the same nodes, supports, masses and member layout as the model, with elasticBeamColumn members on
    the gross sections and the cover modulus. It is used only in validate() to compare the eigenvalue analysis with numpy."""
    init_model()
    define_nodes_and_supports()
    area_col, inertia_col, area_beam, inertia_beam = gross_section_properties()
    ops.geomTransf("Linear", TRANSF_COROT)
    ops.element("elasticBeamColumn", ELE_COL_L, NODE_BASE_L, NODE_TOP_L, area_col, check_modulus, inertia_col, TRANSF_COROT)
    ops.element("elasticBeamColumn", ELE_COL_R, NODE_BASE_R, NODE_TOP_R, area_col, check_modulus, inertia_col, TRANSF_COROT)
    ops.element("elasticBeamColumn", ELE_BEAM_L, NODE_TOP_L, NODE_MID_TOP, area_beam, check_modulus, inertia_beam,
                TRANSF_COROT)
    ops.element("elasticBeamColumn", ELE_BEAM_R, NODE_MID_TOP, NODE_TOP_R, area_beam, check_modulus, inertia_beam,
                TRANSF_COROT)
    define_nodal_masses(mass)
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")


def numpy_elastic_eigen(mass: float, num: int) -> tuple:
    """Independent eigenvalues of the elastic check frame. The massless DOFs (the rotations, and the X and Y of the midspan
    node) are condensed out of K; the finite eigenvalues of K phi = lambda M phi are then those of the condensed matrix with the
    masses of nodes 3 and 4, which is exact.

    Args:
        mass: Nodal mass at nodes 3 and 4, in N·s²/mm.
        num: Number of eigenvalues (the smallest).

    Returns:
        (eigenvalues in ascending order, X and Y shares of each mode: the X-direction participation of the top nodes).
    """
    coords = {NODE_BASE_L: (0.0, 0.0), NODE_BASE_R: (len_beam, 0.0), NODE_TOP_L: (0.0, len_col),
              NODE_TOP_R: (len_beam, len_col), NODE_MID_TOP: (0.5 * len_beam, len_col)}
    area_col, inertia_col, area_beam, inertia_beam = gross_section_properties()
    members = [(NODE_BASE_L, NODE_TOP_L, area_col, inertia_col), (NODE_BASE_R, NODE_TOP_R, area_col, inertia_col),
               (NODE_TOP_L, NODE_MID_TOP, area_beam, inertia_beam), (NODE_MID_TOP, NODE_TOP_R, area_beam, inertia_beam)]
    k = np.zeros((15, 15))
    for node_i, node_j, area, inertia in members:
        k_g, _, _ = element_global_stiffness(coords[node_i], coords[node_j], check_modulus * area, check_modulus * inertia)
        dofs = [3 * (node_i - 1) + d for d in range(3)] + [3 * (node_j - 1) + d for d in range(3)]
        k[np.ix_(dofs, dofs)] += k_g
    free = list(range(6, 15))                       # nodes 3, 4 and 5 (nodes 1 and 2 are fixed)
    kf = k[np.ix_(free, free)]
    massed = [0, 1, 3, 4]                           # ux3, uy3, ux4, uy4
    other = [2, 5, 6, 7, 8]                         # theta3, theta4, ux5, uy5, theta5 (no mass)
    kaa = kf[np.ix_(massed, massed)]
    kab = kf[np.ix_(massed, other)]
    kbb = kf[np.ix_(other, other)]
    k_red = kaa - kab @ np.linalg.solve(kbb, kab.T)
    w, v = np.linalg.eigh(k_red / mass)             # equal masses: M^-1/2 K M^-1/2 = K / mass
    phi = v / np.sqrt(mass)                         # mass-normalised shapes of the massed DOFs
    x_share = np.abs(phi[0, :]) + np.abs(phi[2, :])
    y_share = np.abs(phi[1, :]) + np.abs(phi[3, :])
    return w[:num], x_share[:num], y_share[:num]


def check(report: list, name: str, value: float, reference: float, tol: float, absolute: bool = False) -> bool:
    """Compare two values and record the line in the report: by relative difference, or by absolute difference when
    absolute is True (the source's printed periods have four decimals).

    Args:
        report: Report lines (appended to).
        name: Label of the check.
        value: Value from the model.
        reference: Reference value.
        tol: Tolerance (relative, or absolute).
        absolute: True for an absolute tolerance.

    Returns:
        True when the check passes.
    """
    if absolute:
        diff = abs(value - reference)
        ok = diff <= tol
        report.append(f"{'PASS' if ok else 'FAIL'}  {name}: {value:.10e} vs {reference:.10e} "
                      f"(absolute {diff:.1e}, tolerance {tol:.0e})")
        return ok
    rel = abs(value - reference) / max(abs(reference), 1.0e-300)
    ok = rel <= tol
    report.append(f"{'PASS' if ok else 'FAIL'}  {name}: {value:.10e} vs {reference:.10e} (relative {rel:.1e}, tolerance {tol:.0e})")
    return ok


def validate(results: dict, output_dir: Path) -> None:
    """Checks of the runs: the time sequence, the equilibrium of the base reactions with the applied loads at every step, the
    fallback-ladder use, the source's printed values reproduced by the check run (displacements, base shear and axial force,
    the bilinear fits and the four periods of each printed step), the eigenvalue analysis against numpy on the elastic check
    frame, and the period results. Writes output/validation.txt and prints it.

    Args:
        results: Output of run_analysis().
        output_dir: Folder where validation.txt is written.
    """
    report, oks = [], []
    names = {"steel01": "Steel01 (main)", "hysteretic": "Hysteretic (main)", "check": "Steel01, source mass and Kfc 1.2 (check)"}
    report.append("RESULTS")
    for key in ("steel01", "hysteretic", "check"):
        run = results[key]
        rx, ry, rm = equilibrium_residuals(run)
        t = run["time"]
        scale_x = np.maximum(np.abs(2.0 * px_top * t), 1.0)
        scale_y = np.abs(2.0 * py_top * t)
        scale_m = np.abs(len_beam * 2.0 * py_top * t)
        report.append(f"  {names[key]}: steps {len(t)}, time {t[0]:.0f} to {t[-1]:.0f} day, final base shear "
                      f"{run['force_s'][-1]:.6e} N, axial {run['force_a'][-1]:.6e} N, moment {run['moment'][-1]:.6e} N.mm, "
                      f"node-3 X {run['disp_x'][-1]:.6f} mm, node-5 Y {run['disp_y'][-1]:.6f} mm")
        report.append(f"    analysis at the creep age: fallback attempts {run['initial_ladder']}, final return code "
                      f"{run['initial_ok']}")
        report.append(f"    fallback ladder used at steps {[s for s, _ in run['ladder']]}; steps not converged after the "
                      f"ladder: {int(np.sum(run['ok'] != 0))}")
        report.append(f"    max relative residual: X {np.max(np.abs(rx)) / np.max(scale_x):.1e}, "
                      f"Y {np.max(np.abs(ry)) / np.max(scale_y):.1e}, moments {np.max(np.abs(rm)) / np.max(scale_m):.1e}")
        report.append(f"    first period {run['periods'][0, 0]:.6f} s at day {t[0]:.0f}, {run['periods'][-1, 0]:.6f} s at day "
                      f"{t[-1]:.0f}; smallest of the four periods {run['period_min'][0]:.6f} s to {run['period_min'][-1]:.6f} s; "
                      f"all periods finite: {bool(np.all(np.isfinite(run['periods'])))}")
    fit_x, fit_y = fits_of(results["steel01"])
    report.append(f"  Steel01 fit X: elastic {fit_x['elastic']:.2f}, plastic {fit_x['plastic']:.2f}, tangent "
                  f"{fit_x['tangent']:.2f} N/mm; ductility {fit_x['ductility']:.4f}, over-strength {fit_x['over_strength']:.4f}, "
                  f"R {fit_x['ductility'] * fit_x['over_strength']:.4f}")
    report.append(f"  Steel01 fit Y: elastic {fit_y['elastic']:.2f}, plastic {fit_y['plastic']:.2f}, tangent "
                  f"{fit_y['tangent']:.2f} N/mm; ductility {fit_y['ductility']:.4f}, over-strength {fit_y['over_strength']:.4f}, "
                  f"R {fit_y['ductility'] * fit_y['over_strength']:.4f}")

    report.append("CHECKS")
    for key in ("steel01", "hysteretic", "check"):
        run = results[key]
        t = run["time"]
        expected_t = creep_age + tincr_days * np.arange(1, len(t) + 1)
        oks.append(check(report, f"{names[key]}: analysis time sequence (last step)", t[-1], expected_t[-1], 1.0e-12))
        rx, ry, rm = equilibrium_residuals(run)
        for label, res, scale in (("X force", rx, np.maximum(np.abs(2.0 * px_top * t), 1.0)),
                                  ("Y force", ry, np.abs(2.0 * py_top * t)),
                                  ("moment", rm, np.abs(len_beam * 2.0 * py_top * t))):
            worst = float(np.max(np.abs(res) / scale))
            ok = worst <= 1.0e-9
            oks.append(ok)
            report.append(f"{'PASS' if ok else 'FAIL'}  {names[key]}: equilibrium of the {label} at every step, "
                          f"max relative residual {worst:.1e} (tol 1e-09)")
        oks.append(bool(np.all(np.isfinite(run["periods"])) and np.all(run["periods"] > 0)))
        report.append(f"{'PASS' if oks[-1] else 'FAIL'}  {names[key]}: all periods finite and positive")
        oks.append(bool(np.all(run["period_max"] >= run["period_min"])))
        report.append(f"{'PASS' if oks[-1] else 'FAIL'}  {names[key]}: largest period is never below the smallest")

    chk = results["check"]
    for step, (ref_x, ref_y, ref_s, ref_a) in source_steps.items():
        i = step - 1
        oks.append(check(report, f"check run = source, step {step}: node-3 X displacement", chk["disp_x"][i], ref_x, 1.0e-9))
        oks.append(check(report, f"check run = source, step {step}: node-5 Y displacement", chk["disp_y"][i], ref_y, 1.0e-9))
        oks.append(check(report, f"check run = source, step {step}: base shear", chk["force_s"][i], ref_s, 1.0e-9))
        oks.append(check(report, f"check run = source, step {step}: base axial force", chk["force_a"][i], ref_a, 1.0e-9))
    for step, printed in source_periods.items():
        for mode, ref_t in enumerate(printed):
            oks.append(check(report, f"check run = source, step {step}: period {mode + 1} (printed value)",
                             chk["periods"][step - 1, mode], ref_t, 5.0e-5, absolute=True))
    ladder_ok = [s for s, _ in chk["ladder"]] == [7]
    oks.append(ladder_ok)
    report.append(f"{'PASS' if ladder_ok else 'FAIL'}  check run: fallback ladder at step 7 only (source: the step at load "
                  f"factor 203)")
    cx, cy = fits_of(chk)
    for label, fit, ref in (("X", cx, source_fit_x), ("Y", cy, source_fit_y)):
        oks.append(check(report, f"check run = source, fit {label} ductility", fit["ductility"], ref["ductility"], 1.0e-4))
        oks.append(check(report, f"check run = source, fit {label} over-strength", fit["over_strength"],
                         ref["over_strength"], 1.0e-4))
        oks.append(check(report, f"check run = source, fit {label} R", fit["ductility"] * fit["over_strength"], ref["r"],
                         1.0e-4))

    # Eigenvalue analysis against numpy, on the elastic check frame (the same eigenvalue call as the model)
    for mass_label, mass in (("SI mass", mass_node_si), ("source mass", mass_node_as_written)):
        build_elastic_frame(mass)
        lam_ops = np.array(ops.eigen("-fullGenLapack", num_eigen))
        lam_np, x_share, y_share = numpy_elastic_eigen(mass, num_eigen)
        worst = float(np.max(np.abs(lam_ops - lam_np) / np.abs(lam_np)))
        ok = worst <= 1.0e-9
        oks.append(ok)
        report.append(f"{'PASS' if ok else 'FAIL'}  elastic frame, {mass_label}: four eigenvalues, OpenSees against numpy "
                      f"(static condensation of the massless DOFs), max relative difference {worst:.1e} (tol 1e-09)")
        report.append(f"  elastic frame, {mass_label}: periods {np.round(2.0 * np.pi / np.sqrt(lam_np), 6).tolist()} s; "
                      f"X share of each mode {np.round(x_share, 3).tolist()}, Y share {np.round(y_share, 3).tolist()}")
    lam_si_np = numpy_elastic_eigen(mass_node_si, num_eigen)[0]
    lam_as_np = numpy_elastic_eigen(mass_node_as_written, num_eigen)[0]
    scale_err = float(np.max(np.abs(lam_si_np * mass_node_si - lam_as_np * mass_node_as_written)
                             / (lam_as_np * mass_node_as_written)))
    scale_ok = scale_err <= 1.0e-9
    oks.append(scale_ok)
    report.append(f"{'PASS' if scale_ok else 'FAIL'}  eigenvalues scale as 1 / mass (lambda x mass, SI against the source "
                  f"mass): max relative difference {scale_err:.1e} (tol 1e-09)")

    main = results["steel01"]
    report.append(f"INFO  periods of the Steel01 run (SI mass) against the source's mass as written, at day 53: largest "
                  f"{main['period_max'][0]:.6f} s against {chk['period_max'][0]:.6f} s; ratio "
                  f"{main['period_max'][0] / chk['period_max'][0]:.6f} (the stiffness differs by the beam's Kfc, the mass ratio "
                  f"alone would be {1.0 / np.sqrt(1000.0):.6f})")
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
