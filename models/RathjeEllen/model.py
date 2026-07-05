# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : PM4Sand Effective-Stress Site Response — Parametric Liquefaction Sweep
UniqueID : RathjeEllen
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-05
Purpose  : 2D coupled u-p effective-stress site response analysis of a
           layered soil profile (loose-sand crust over dense-sand base) with
           PM4Sand liquefaction constitutive model and Lysmer dashpot base,
           parametric in liquefiable-layer thickness and crust thickness.
Ref      : McGann, C. & Arduino, P. — University of Washington, GiD UWquad2D
           problem type (2010); Ellen Rathje liquefaction-sweep study.
Units    : kN, m, kPa, sec  (coupled u-p — retained per AGENT.md §3a/§12j and
           the pedroArduino_freefield / XMU_Ch8 precedent; converting PM4Sand
           empirical constants and fluid bulk/permeability to N-mm would
           destroy numerical conditioning and is non-physical).

NOTE     : This is a parametric driver. Select the case via CLI:
               python model.py 2_HA_2_H          # default if omitted
           Cases live in cases/<case>/ (mesh .dat + case_meta.json).
           The 18 cases in the `loose` set differ only in mesh geometry —
           materials, motion, and analysis logic are identical (verified).
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import json
import sys
import math
from pathlib import Path

import sys
from pathlib import Path

import openseespy.opensees as ops
import opstool as opst

# standards/ helpers (vis_utils does NOT pull units.py — safe for kN-m models)
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from vis_utils import vis_nodes, vis_model, vis_loads, vis_pre_analysis, _headless

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# PM4Sand materials (4 — main column + free-field duplicate of each)
MAT_PM4SAND_DENSE     = 1   # dense sand, main column  (Dr = 0.85)
MAT_PM4SAND_DENSE_FF  = 2   # dense sand, free-field column (thick = 10000)
MAT_PM4SAND_LOOSE     = 3   # loose sand, main column  (Dr = 0.55)
MAT_PM4SAND_LOOSE_FF  = 4   # loose sand, free-field column

# Dashpot
MAT_DASHPOT = 5

# Load pattern + time series
PAT_DYNAMIC = 10
TS_VELOCITY = 11

# Defaults
DEFAULT_CASE = "2_HA_2_H"

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Units: kN, m, kPa, s  (coupled u-p SI set — retained per precedent; see header)

# --- PM4Sand constitutive parameters (from tcl_ref/loose/*/final_model.tcl) ---
# PM4Sand minimal 6-arg form: tag, Dr, G0, kDr, mDr, P_atm
PM4SAND_DENSE = dict(Dr=0.85, G0=1481.0, kDr=3.0, mDr=2.1)   # mats 1, 2
PM4SAND_LOOSE = dict(Dr=0.55, G0=642.0,  kDr=0.1, mDr=1.8)   # mats 3, 4
P_ATM = 101.1   # kPa reference pressure

# --- SSPquadUP element parameters (per-material, read at element-build time) ---
# thick: 1.0 for main column, 10000 for free-field column
# uBulk (fluid): 2.2e6 kPa; hPerm = vPerm = 1e-4 m/s; mAlpha (Biot) = 1e-5
ELE_PARAMS = {
    MAT_PM4SAND_DENSE:     dict(thick=1.0,    uBulk=2.2e6, hPerm=1.0e-4, vPerm=1.0e-4,
                                mVoid=0.51, mAlpha=1.0e-5),
    MAT_PM4SAND_DENSE_FF:  dict(thick=10000.0, uBulk=2.2e6, hPerm=1.0e-4, vPerm=1.0e-4,
                                mVoid=0.51, mAlpha=1.0e-5),
    MAT_PM4SAND_LOOSE:     dict(thick=1.0,    uBulk=2.2e6, hPerm=1.0e-4, vPerm=1.0e-4,
                                mVoid=0.77, mAlpha=1.0e-5),
    MAT_PM4SAND_LOOSE_FF:  dict(thick=10000.0, uBulk=2.2e6, hPerm=1.0e-4, vPerm=1.0e-4,
                                mVoid=0.77, mAlpha=1.0e-5),
}

# --- Body forces (gravity) ---
BODY_X = 0.0       # horizontal body force (kN/m³ → element scales by density)
BODY_Y = -9.81     # vertical body force (m/s²; SSPquadUP scales internally by rho)

# --- Rayleigh damping (2% on 0.2–20 Hz) ---
DAMP_RATIO = 0.02
OMEGA_1 = 2.0 * math.pi * 0.2
OMEGA_2 = 2.0 * math.pi * 20.0
A0 = 2.0 * DAMP_RATIO * OMEGA_1 * OMEGA_2 / (OMEGA_1 + OMEGA_2)
A1 = 2.0 * DAMP_RATIO / (OMEGA_1 + OMEGA_2)

# --- Newmark integrator parameters ---
GAMMA_GRAV = 5.0 / 6.0      # gravity consolidation (Newmark, tcl)
BETA_GRAV  = 4.0 / 9.0
GAMMA_DYN  = 0.5            # dynamic (Newmark, tcl)
BETA_DYN   = 0.25

# --- Analysis control ---
ANALYSIS_DT = 0.001         # s — dynamic analysis step (tcl: AnalysisdT)
                           # Near the CFL limit (dt_CFL ≈ 0.0011s for dense sand
                           # at h_min=0.333m, Vs≈300 m/s) — do NOT increase.
ODB_EVERY_N = 200           # throttle ODB for large transient runs (AGENT §3d/§12d)
                           # 16505/200 ≈ 82 ODB samples — well under the ≤500
                           # target; gives a smooth deformation envelope.
DYN_TEST_TOL = 1.0e-2       # NormDispIncr tol — matches Tcl source exactly.
                           # Tighter (1e-3) wastes Newton iterations with no
                           # physics benefit for a liquefying sand.
DYN_TEST_ITER = 8           # max Newton iters/step. Tcl uses 35, but a
                           # well-conditioned step converges in 2-4; capping
                           # at 8 fails fast on the rare bad step (sub-stepping
                           # then handles it) instead of grinding 35 iters.
DYN_PRINT_EVERY = 2000      # per-step print frequency

# --- Solver mode (AGENT §12ag lesson 4 — toggleable flag) ---
USE_SMARTANALYZE = False    # True → SmartAnalyze (dev/iter); False → manual Newton
                           # loop at fixed dt (faster + more robust for production).
                           # §12ag table: manual loop 100% step coverage vs
                           # SmartAnalyze's 54% on stiffness-contrast models.


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and create a 2D BasicBuilder with 3 DOF/node (u, v, pore-pressure)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials(dashpot_coeff_total: float) -> None:
    """Define the 4 PM4Sand materials and the Lysmer dashpot.

    Args:
        dashpot_coeff_total: Viscous dashpot coefficient C = baseArea × dashpotCoeff
                             (kN·s/m), already multiplied per case_meta.
    """
    for tag, params in ((MAT_PM4SAND_DENSE, PM4SAND_DENSE),
                        (MAT_PM4SAND_DENSE_FF, PM4SAND_DENSE),
                        (MAT_PM4SAND_LOOSE, PM4SAND_LOOSE),
                        (MAT_PM4SAND_LOOSE_FF, PM4SAND_LOOSE)):
        ops.nDMaterial("PM4Sand", tag,
                       params["Dr"], params["G0"], params["kDr"], params["mDr"], P_ATM)

    # Lysmer dashpot — viscous damper at the base (X direction only)
    ops.uniaxialMaterial("Viscous", MAT_DASHPOT, dashpot_coeff_total, 1)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def _read_node_info(case_dir: Path) -> dict:
    """Parse nodeInfo.dat → {tag: (x, y)}."""
    nodes = {}
    with open(case_dir / "nodeInfo.dat") as f:
        for line in f:
            p = line.split()
            if len(p) >= 3:
                nodes[int(p[0])] = (float(p[1]), float(p[2]))
    return nodes


def define_nodes(nodes: dict) -> None:
    """Create all soil (ndf=3) nodes from nodeInfo.dat."""
    for tag, (x, y) in nodes.items():
        ops.node(tag, x, y)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(case_dir: Path, nodes: dict) -> tuple:
    """Apply fixities, equalDOF constraints, and build the dashpot (ndf=2 sub-builder).

    Reads nodeFixitiesInfo.dat and nodeEqualDOFInfo.dat from the case folder.

    Args:
        case_dir: Folder containing the .dat mesh files.
        nodes: {tag: (x, y)} from _read_node_info (used for dashpot node coords).

    Returns:
        (base_master_node, dashpot_node_free) — needed for the dynamic load.
    """
    # --- Soil node fixities (3 DOF: ux, uy, pore-pressure) ---
    with open(case_dir / "nodeFixitiesInfo.dat") as f:
        for line in f:
            p = line.split()
            if len(p) >= 4:
                ops.fix(int(p[0]), int(p[1]), int(p[2]), int(p[3]))

    # --- equalDOF (free-field column tying + base tying) ---
    # 4-column rows: "master slave 1 2" → tie ux and uy
    # 3-column rows: "master slave 1"   → tie ux only (base lateral tie)
    with open(case_dir / "nodeEqualDOFInfo.dat") as f:
        for line in f:
            p = line.split()
            if len(p) == 4:
                ops.equalDOF(int(p[0]), int(p[1]), 1, 2)
            elif len(p) == 3:
                ops.equalDOF(int(p[0]), int(p[1]), 1)

    return nodes  # placeholder; dashpot handled in define_elements for ordering


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(case_dir: Path, nodes: dict, meta: dict) -> int:
    """Build SSPquadUP soil elements + Lysmer dashpot zeroLength.

    SSPquadUP arg order (matching the Tcl source exactly):
        eleTag, n1, n2, n3, n4, matTag, thick, bulk, fmass, hPerm, vPerm,
        e0(=mVoid), alpha(=mAlpha), bx, by

    Permeabilities are 1.0 m/s for gravity (updated via update_permeability after).

    Args:
        case_dir: Folder with elementInfo.dat and firstCall.dat.
        nodes: {tag: (x, y)} for dashpot node placement.
        meta: case_meta dict (dashpot element/node tags).

    Returns:
        Number of soil elements created.
    """
    n_elem = 0
    with open(case_dir / "elementInfo.dat") as f:
        for line in f:
            p = line.split()
            if len(p) < 6:
                continue
            tag = int(p[0])
            n1, n2, n3, n4 = int(p[1]), int(p[2]), int(p[3]), int(p[4])
            mat_tag = int(p[5])
            ep = ELE_PARAMS[mat_tag]
            # SSPquadUP: ..., matTag, thick, bulk, fmass, hPerm, vPerm, e0, alpha, bx, by
            ops.element("SSPquadUP", tag, n1, n2, n3, n4,
                        mat_tag,
                        ep["thick"], ep["uBulk"],
                        1.0,                # fmass (fluid mass — tcl uses 1.0)
                        1.0, 1.0,           # hPerm, vPerm (placeholder 1.0 m/s for gravity)
                        ep["mVoid"],        # e0 (void ratio)
                        ep["mAlpha"],       # alpha (Biot coefficient)
                        BODY_X, BODY_Y)
            n_elem += 1

    # --- Lysmer dashpot (ndf=2 sub-builder, mirrors tcl §4) ---
    dash_elem  = meta["dashpot_element"]
    dash_fixed = meta["dashpot_node_fixed"]
    dash_free  = meta["dashpot_node_free"]
    base_node  = meta["base_master_node"]

    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 2)
    bx, by = nodes[base_node]
    ops.node(dash_fixed, bx, by)
    ops.node(dash_free,  bx, by)
    ops.fix(dash_fixed, 1, 1)
    ops.fix(dash_free,  0, 1)
    ops.equalDOF(base_node, dash_free, 1)
    ops.element("zeroLength", dash_elem, dash_fixed, dash_free,
                "-mat", MAT_DASHPOT, "-dir", 1)

    # Switch back to ndf=3 for the dynamic load definition
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)
    return n_elem


def update_permeability(case_dir: Path) -> None:
    """Restore true permeabilities after gravity consolidation.

    Reads each element's material from elementInfo.dat and sets hPerm/vPerm
    from ELE_PARAMS. Mirrors tcl §9 (permeabilities are 1.0 during gravity,
    real values after). Uses -val (OpenSeesPy form per AGENT §12).
    """
    with open(case_dir / "elementInfo.dat") as f:
        for line in f:
            p = line.split()
            if len(p) < 6:
                continue
            tag = int(p[0])
            mat_tag = int(p[5])
            ep = ELE_PARAMS[mat_tag]
            ops.setParameter("-val", ep["hPerm"], "-ele", tag, "hPerm")
            ops.setParameter("-val", ep["vPerm"], "-ele", tag, "vPerm")


def apply_first_call(case_dir: Path) -> None:
    """Parse firstCall.dat and apply each setParameter(FirstCall=0).

    firstCall.dat line format (tokens, 0-indexed):
        0:setParameter  1:-value  2:0  3:-ele  4:<eleTag>  5:FirstCall  6:<matTag>

    For PM4Sand, FirstCall is MANDATORY at the elastic→plastic transition: it
    triggers the material's internal initialization, which reads the gravity
    stress state and populates the stress-dependent secondary parameters
    (Ado, z_max, h0, c_dr, c_kaf, ...). Without it, those parameters stay at
    their sentinels and the first plastic computation divides by zero
    (Vector::operator/(double fact) - divide-by-zero error → NaN residuals).

    OpenSeesPy requires the trailing <matTag> AS A STRING (per the official
    PM4Sand cyclic-simple-shear example, line 191):
        ops.setParameter('-val', 0, '-ele', ele, 'FirstCall', '<matTag>')
    Passing it as an int raises "Invalid String Input!" (openseespy stringifies
    trailing positional args but cannot stringify a bare int into the parameter
    name slot). Dropping it entirely skips initialization entirely.
    The §12ab PostShake lesson (drop the trailing tag) does NOT generalize to
    PM4Sand's FirstCall — PostShake is a different parameter on a different
    material (PDMY02). Commented (#) and blank lines are skipped.
    """
    with open(case_dir / "firstCall.dat") as f:
        for line in f:
            p = line.split()
            # need: setParameter -value 0 -ele <eleTag> FirstCall <matTag>
            if len(p) < 7 or p[0] != "setParameter":
                continue
            ele_tag = int(p[4])
            mat_tag_str = p[6]   # pass as string — OpenSees expects a token here
            ops.setParameter("-val", 0, "-ele", ele_tag, "FirstCall", mat_tag_str)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def _ensure_minimum_mass(soil_node_tags, min_mass: float = 1.0e-9) -> None:
    """Assign a tiny fictitious mass to every free soil DOF that has zero mass.

    Regularises K_eff = 1/(β·Δt²)·M + γ/(β·Δt)·C + K at the small Δt sizes
    hit during sub-stepping, where the mass term would otherwise vanish on
    zero-mass DOFs and leave K_eff near-singular. (AGENT §12ag lesson 2.)

    Only patches the soil nodes (ndf=3) — the dashpot nodes (10402/10403) are
    ndf=2 (built in the ndf=2 sub-builder for the Lysmer dashpot) and have
    their own fixities; calling ops.mass() with 3 args on them raises
    "incompatible matrices".

    Args:
        soil_node_tags: Iterable of the ndf=3 soil node tags (from nodeInfo.dat).
        min_mass: Floor mass per DOF (1e-9 — far below any physical soil mass,
                  negligible for dynamics, decisive for solver stability).
    """
    for tag in soil_node_tags:
        masses = []
        for dof in range(1, 4):                # ndf=3 soil nodes only
            try:
                masses.append(ops.nodeMass(tag, dof))
            except Exception:
                masses.append(0.0)
        if any(m < min_mass for m in masses):
            ops.mass(tag, *[max(m, min_mass) for m in masses])


def create_odb(odb_tag: int, output_dir: Path, n_elem: int) -> "opst.post.CreateODB":
    """Initialise the ODB after the model is built.

    PERFORMANCE: only nodal responses are saved. Saving plane (element
    stress/strain) responses was the dominant cost on a 10000+ element mesh
    (every fetch_response_step queried all 10050 elements) — AND the results
    were silently all-zeros anyway, because opstool's Gauss→node projection
    does not support SSPquadUP's single-Gauss-point topology (AGENT §12ad).
    Element stresses can be recovered later via a separate recorder if needed.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_plane_resp=False,        # §12ad: all-zeros for SSPquadUP; pure overhead
        compute_mechanical_measures=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_dynamic_loading(meta: dict, motion_dir: Path) -> None:
    """Define the dynamic base excitation as a force = velocity × C at the base.

    Mirrors tcl §11: Path timeSeries from motion1.time + motion1.vel, scaled by
    cFactor = baseArea × dashpotCoeff, applied as a UX point load at the base
    master node via a Plain pattern.
    """
    c_factor = meta["base_area"] * meta["dashpot_coeff"]
    ops.timeSeries("Path", TS_VELOCITY,
                   "-dt", meta["motion_dt"],
                   "-filePath", str(motion_dir / "motion1.vel"),
                   "-factor", c_factor)
    ops.pattern("Plain", PAT_DYNAMIC, TS_VELOCITY)
    ops.load(meta["load_node"], 1.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB", meta: dict, case_dir: Path) -> bool:
    """Two-phase gravity consolidation (tcl §8): elastic then plastic.

    Elastic stage: Newmark-Transient, Newton, dt=500s (matches Tcl). The large
    dt is the standard consolidation trick for coupled u-p soils.

    Plastic stage: KrylovNewton + tighter tol + dt=1s. PM4Sand's tangent near
    the yield surface defeats plain Newton-Raphson at the elastic→plastic
    transition — Newton cycles above tol (or, in this model, hits a
    divide-by-zero producing NaN residuals). KrylovNewton's secant acceleration
    escapes the cycle. This mirrors the §12ae recipe for the 9_4_QuadUP /
    PDMY02 sibling (the same physics applies to PM4Sand in SSPquadUP).

    Args:
        odb: Active CreateODB.
        meta: case_meta dict (gravity step/dt values).
        case_dir: Folder with firstCall.dat (applied between elastic & plastic).

    Returns:
        True if both phases converge, False otherwise.
    """
    # Elastic stage — materials forced elastic
    for k in (MAT_PM4SAND_DENSE, MAT_PM4SAND_DENSE_FF,
              MAT_PM4SAND_LOOSE, MAT_PM4SAND_LOOSE_FF):
        ops.updateMaterialStage("-material", k, "-stage", 0)

    ops.constraints("Penalty", 1.0e15, 1.0e15)
    ops.test("NormDispIncr", 1.0e-2, 35, 0)
    ops.algorithm("Newton")
    ops.numberer("RCM")
    ops.system("ProfileSPD")   # tcl uses Mumps — unavailable in openseespy; ProfileSPD is the standard substitute
    ops.integrator("Newmark", GAMMA_GRAV, BETA_GRAV)
    ops.analysis("Transient")

    ok = ops.analyze(meta["gravity_steps_elastic"], meta["gravity_dt_elastic"])
    print(f"  Elastic gravity ({meta['gravity_steps_elastic']}×"
          f"{meta['gravity_dt_elastic']}s): ok={ok}")
    if ok != 0:
        return False

    # Plastic stage — materials switched to plastic, FirstCall fired.
    # KrylovNewton + 1e-4 + dt=1s (§12ae lesson 2): plain Newton cycles or
    # NaNs at the elastic→plastic transition in PM4Sand.
    for k in (MAT_PM4SAND_DENSE, MAT_PM4SAND_DENSE_FF,
              MAT_PM4SAND_LOOSE, MAT_PM4SAND_LOOSE_FF):
        ops.updateMaterialStage("-material", k, "-stage", 1)
    apply_first_call(case_dir)

    ops.wipeAnalysis()
    ops.constraints("Penalty", 1.0e15, 1.0e15)
    ops.test("NormDispIncr", 1.0e-4, 50, 1)
    ops.algorithm("KrylovNewton")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", GAMMA_GRAV, BETA_GRAV)
    ops.analysis("Transient")

    ok = ops.analyze(meta["gravity_steps_plastic"], meta["gravity_dt_plastic"])
    print(f"  Plastic gravity ({meta['gravity_steps_plastic']}×"
          f"{meta['gravity_dt_plastic']}s): ok={ok}")
    return ok == 0


def run_dynamic(odb: "opst.post.CreateODB", meta: dict) -> bool:
    """Run the transient dynamic analysis.

    Two solver paths (toggleable via USE_SMARTANALYZE, AGENT §12ag lesson 4):

    * Manual Newton loop (default, USE_SMARTANALYZE = False): faster and more
      robust for production. A fixed-dt loop avoids SmartAnalyze's per-step
      dispatch overhead and its tendency to shrink dt to singular values on
      stiffness-contrast models. §12ag table: manual loop achieves 100% step
      coverage vs SmartAnalyze's 54% on a bridge model; the same pattern
      applies here. Sub-stepping is implemented inline (halve dt on failure,
      up to 8 levels) so the analysis still recovers from local nonlinearity.

    * SmartAnalyze (USE_SMARTANALYZE = True): use during model development for
      its auto-algorithm-switching and detailed logging.

    ODB collection is throttled to every ODB_EVERY_N-th step (these are
    10000+ element / 16500+ step models). With the slimmed-down ODB
    (nodal-only, no plane responses) each fetch is ~100× cheaper.

    Returns:
        True if analysis completes all steps, False on failure.
    """
    duration = meta["motion_npts"] * meta["motion_dt"]
    n_steps = int(math.floor(duration / ANALYSIS_DT) + 1)
    dt = ANALYSIS_DT
    print(f"  Dynamic: {n_steps} steps @ dt={dt}s (motion {meta['motion_npts']}pts"
          f"@{meta['motion_dt']:.4f}s, duration {duration:.2f}s)")

    ops.constraints("Penalty", 1.0e15, 1.0e15)
    ops.test("NormDispIncr", DYN_TEST_TOL, DYN_TEST_ITER, 0)
    ops.algorithm("Newton")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", GAMMA_DYN, BETA_DYN)
    ops.analysis("Transient")               # required after wipeAnalysis()
    ops.rayleigh(A0, A1, 0.0, 0.0)

    if USE_SMARTANALYZE:
        return _run_dynamic_smart(odb, meta, n_steps, dt)
    return _run_dynamic_manual(odb, meta, n_steps, dt)


def _run_dynamic_manual(odb, meta, n_steps, dt) -> bool:
    """Manual fixed-dt Newton loop with inline sub-stepping on failure.

    Each step: try ops.analyze(1, dt). On failure, halve dt and retry; if the
    sub-step converges, advance and try to grow dt back. Capped at 8 halvings
    (dt → dt/256); beyond that, give up on the step. ODB sampled every
    ODB_EVERY_N-th *converged* step.
    """
    failed = 0
    for i in range(n_steps):
        # try the full step; sub-step on failure
        ok = ops.analyze(1, dt)
        sub = 0
        while ok != 0 and sub < 8:
            sub_dt = dt / (2 ** sub)
            ok = ops.analyze(1, sub_dt)
            sub += 1
        if ok != 0:
            print(f"  Step {i + 1}/{n_steps} failed after {sub} sub-steps "
                  f"(ok={ok}); aborting.")
            return False
        if sub > 0:
            failed += 1
        if i % ODB_EVERY_N == 0:
            odb.fetch_response_step()
        if (i + 1) % DYN_PRINT_EVERY == 0:
            print(f"  Step {i + 1}/{n_steps}  (sub-stepped: {failed})")
    print(f"  Done: {n_steps} steps, {failed} required sub-stepping.")
    return True


def _run_dynamic_smart(odb, meta, n_steps, dt) -> bool:
    """SmartAnalyze path (development). Slower but auto-switches algorithms."""
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="NormDispIncr",
        testTol=DYN_TEST_TOL,
        testIterTimes=DYN_TEST_ITER,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 20, 30],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )
    segs = analysis.transient_split(n_steps)
    for i, _ in enumerate(segs):
        ok = analysis.TransientAnalyze(dt)
        if ok < 0:
            print(f"  Step {i + 1}/{n_steps} failed (ok={ok}); aborting.")
            analysis.close()
            return False
        if i % ODB_EVERY_N == 0:
            odb.fetch_response_step()
        if (i + 1) % DYN_PRINT_EVERY == 0:
            print(f"  Step {i + 1}/{n_steps}")
    analysis.close()
    return True


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB and render deformed-shape HTML plots (peak + slider)."""
    odb.save_response()
    print("  ODB saved.")
    try:
        opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, step="absMax", defo_scale=True,
            resp_type="disp", resp_dof="UX",
        ).write_html(str(output_dir / "vis_05_peak_deformed.html"))
        print("  -> vis_05_peak_deformed.html")
    except Exception as e:
        print(f"  Skipped peak plot: {e}")
    try:
        opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, slides=True, defo_scale=True,
            resp_type="disp", resp_dof="UX",
        ).write_html(str(output_dir / "vis_06_slider.html"))
        print("  -> vis_06_slider.html")
    except Exception as e:
        print(f"  Skipped slider plot: {e}")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
def run_analysis(case: str, root: Path) -> "opst.post.CreateODB":
    """Build the model for one case, run gravity + dynamic, return the ODB.

    Args:
        case: Case folder name (e.g. "2_HA_2_H").
        root: Project root (models/RathjeEllen).
    """
    case_dir    = root / "cases" / case
    motion_dir  = root / "ground_motions"
    output_dir  = root / "output" / case
    output_dir.mkdir(parents=True, exist_ok=True)
    meta = json.loads((case_dir / "case_meta.json").read_text())

    print(f"\n=== RathjeEllen / {case} ===")
    print(f"  {meta['motion_npts']} motion pts, "
          f"load_node={meta['load_node']}, dash={meta['dashpot_element']}")

    init_model()
    define_materials(meta["base_area"] * meta["dashpot_coeff"])

    nodes = _read_node_info(case_dir)
    define_nodes(nodes)
    define_boundary_conditions(case_dir, nodes)
    vis_nodes(output_dir)                                  # V1: nodes + supports
    n_elem = define_elements(case_dir, nodes, meta)
    print(f"  Mesh: {n_elem} SSPquadUP elements, {len(nodes)} soil nodes")
    vis_model(output_dir)                                  # V2: full geometry

    # Regularise K_eff for the small dt's hit during sub-stepping (AGENT §12ag).
    # Must run before create_odb() — save_model_data() snapshots the mass.
    # Soil nodes only — the ndf=2 dashpot nodes are skipped (see fn docstring).
    _ensure_minimum_mass(nodes.keys())

    odb = create_odb(odb_tag=1, output_dir=output_dir, n_elem=n_elem)

    # Gravity
    print("=== Gravity ===")
    if not run_gravity(odb, meta, case_dir):
        print("Gravity failed.")
        return odb

    # Reset for dynamic
    ops.setTime(0.0)
    ops.wipeAnalysis()

    # Real permeabilities + dynamic loading (load defined AFTER loadConst-safe reset)
    print("=== Permeability Update ===")
    update_permeability(case_dir)

    define_dynamic_loading(meta, motion_dir)
    vis_loads(output_dir)                                  # V3: load vectors
    vis_pre_analysis(output_dir)                           # V4: pre-analysis sanity

    # Dynamic
    print("=== Dynamic ===")
    run_dynamic(odb, meta)

    return odb


if __name__ == "__main__":
    case = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CASE
    root = Path(__file__).parent
    odb = run_analysis(case, root)
    post_process(odb, root / "output" / case)
    print(f"\n=== Complete: {case} ===")
