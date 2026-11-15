# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Elastoplastic Time History Analysis of Frame Structures (Dino Exam07)
UniqueID : Dino_FrameTH
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-08
Purpose  : Gravity + X-direction seismic transient of a 6-storey RC frame
           (63 nodes, 126 forceBeamColumn elements; Steel01 + Concrete02
           column/beam fibre sections in shear+torsion Aggregators).
           After beam-UDL gravity, 5%-damped Newmark transient (3000 x
           0.005 s) under GM1X (x0.6072); node-59 UX history validated
           against ref/OPENSEES/node59.out and base-column forces against
           shear.out (eles 106-114).
Ref      : Dino -- Elastoplastic Time History Analysis of Frame Structures
           (original EXAM7.s2k / ETABS EXAM7.EDB; ref/OPENSEES/EXAM7.tcl)
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import re
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

# This model nests under models/Dino/<analysis-name>/, one level deeper than
# the usual models/<UniqueID>/, so standards/ is parents[3] not parents[2]
# (see AGENT.md §12as-5).
_STANDARDS = Path(__file__).parents[3] / "standards"
if not _STANDARDS.exists():
    _STANDARDS = Path(__file__).parents[2] / "standards"   # fallback for relocation
sys.path.insert(0, str(_STANDARDS))
from units import *
from vis_utils import (
    _headless,
    vis_nodes,
    vis_model,
    vis_loads,
    vis_pre_analysis,
    vis_defo,
    vis_slider,
    vis_anim,
)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Steel01 rebar + Concrete02 + dead Elastic + rigid shear/torsion materials
# (source tags verbatim; one set of Vy/Vz/T per Aggregator).
MAT_S1        = 1      # Steel01 400/206000/0.01 (rebar, BOTH sections)
MAT_C2        = 2      # Concrete02 -26.8/-0.0015/-10/-0.0033/0.1/2.2/1100
MAT_E3        = 3      # Elastic 1.999e5 (dead -- no fiber references it)
MAT_VY_1      = 201    # Elastic shear-Vy for Aggregator 1001 (columns)
MAT_VZ_1      = 301    # Elastic shear-Vz for Aggregator 1001
MAT_T_1       = 401    # Elastic torsion-T for Aggregator 1001
MAT_VY_2      = 202    # Elastic shear-Vy for Aggregator 1002 (beams)
MAT_VZ_2      = 302    # Elastic shear-Vz for Aggregator 1002
MAT_T_2       = 402    # Elastic torsion-T for Aggregator 1002

# Fibre sections + Aggregator wrappers + shared Lobatto integrations.
SEC_FIBER_1   = 1      # NC400X400 column (25 conc + 20 steel fibres)
SEC_FIBER_2   = 2      # NB200X500 beam (25 conc + 10 steel fibres)
SEC_AGG_1     = 1001
SEC_AGG_2     = 1002
INTEG_1       = 1001   # beamIntegration Lobatto shared by all sec-1001 elements
INTEG_2       = 1002   # beamIntegration Lobatto shared by all sec-1002 elements

# Validation
NODE_MONITOR  = 59     # roof-corner UX validated against node59.out
SHEAR_ELES    = tuple(range(106, 115))  # base columns in shear.out (eleRange 106-114)

# Time series / patterns (tags match the source).
TS_GRAV       = 1
PAT_GRAV      = 1
TS_GM         = 1002   # inline Series tag (source IDloadTag 1001 -> incr 1002)
PAT_GM        = 1002

# ODB
ODB_TAG       = 1

# Source files
TCL_FILE      = Path(__file__).parent / "ref" / "OPENSEES" / "EXAM7.tcl"
REF_NODE      = Path(__file__).parent / "ref" / "OPENSEES" / "node59.out"
REF_SHEAR     = Path(__file__).parent / "ref" / "OPENSEES" / "shear.out"
GM_FILE       = Path(__file__).parent / "ground_motions" / "GM1X.txt"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E/fc in MPa, forces in N,
# GM in mm/s^2 scaled by GM_FACTOR).

# Steel01 rebar (source line, verbatim).
FY_STEEL = 400.0 * MPa
E_STEEL  = 206000.0 * MPa
B_STEEL  = 0.01               # strain-hardening ratio (dimensionless)

# Concrete02 (source line, verbatim: fpc epsc0 fpcu epsU lambda ft Ets).
FC   = -26.8 * MPa
EPSC0 = -0.0015              # (dimensionless)
FPCU = -10.0 * MPa
EPSU = -0.0033               # (dimensionless)
LAMBD = 0.1                  # (dimensionless)
FT   = 2.2 * MPa
ETS  = 1100.0 * MPa

# Rigid shear/torsion stiffnesses for the Aggregators (source, verbatim).
K_VY_1 = 1.056e10            # N (columns)
K_VZ_1 = 1.056e10            # N
K_T_1  = 2.857e14            # N*mm^2
K_VY_2 = 1.094e9             # N (beams)
K_VZ_2 = 1.094e9             # N
K_T_2  = 1.310e13            # N*mm^2

N_IP = 3                     # forceBeamColumn integration points (source)

# Gravity (source: LoadControl 0.1 x analyze 10 -> LF 1.0; UDL eleLoads).
GRAV_INCR    = 0.1           # load factor per step (dimensionless)
N_GRAV_STEPS = 10            # -> LF 1.0 total

# Rayleigh damping, 5% on modes 1-2 (source).
DAMP_RATIO = 0.05
N_EIGEN    = 2

# Ground motion GM1X (source: Series dt 0.02, factor 0.6072, dir 1).
DT_GM     = 0.02             # s (timeSeries Series -dt; units: seconds)
GM_FACTOR = 0.6072           # scale factor (dimensionless, "large" level)
GM_DIR    = 1                # excitation direction (UX)

# Transient (source: Newmark 0.5/0.25, analyze 3000 x 0.005 -> 15 s).
DT_ANALYSIS = 0.005          # s
N_STEPS     = 3000
N_TRIAL_STEPS: int | None = None   # trial runs: first N transient steps (None = full 3000)
# Convergence test tolerance for the transient (source: 1.0e-1; level-run
# drivers may override -- tight 1e-6 tracks true equilibrium at ~30x cost).
TEST_TOL = 1.0e-1

# ODB stride (§3d): 3000 steps x 63 nodes -> fetch every Nth step.
ODB_EVERY_N = 6              # ~500 fetches

N_TOTAL_STEPS = N_GRAV_STEPS + N_STEPS  # 3010


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Steel01 rebar + Concrete02 + rigid shear/torsion (source, verbatim).

    MAT_E3 (Elastic 1.999e5) is defined in the source but referenced by no
    fiber -- kept for tag fidelity (Dino §12ap-6).
    """
    ops.uniaxialMaterial("Steel01", MAT_S1, FY_STEEL, E_STEEL, B_STEEL)
    ops.uniaxialMaterial("Concrete02", MAT_C2, FC, EPSC0, FPCU, EPSU,
                         LAMBD, FT, ETS)
    ops.uniaxialMaterial("Elastic", MAT_E3, 1.999e5 * MPa)
    ops.uniaxialMaterial("Elastic", MAT_VY_1, K_VY_1)
    ops.uniaxialMaterial("Elastic", MAT_VZ_1, K_VZ_1)
    ops.uniaxialMaterial("Elastic", MAT_T_1, K_T_1)
    ops.uniaxialMaterial("Elastic", MAT_VY_2, K_VY_2)
    ops.uniaxialMaterial("Elastic", MAT_VZ_2, K_VZ_2)
    ops.uniaxialMaterial("Elastic", MAT_T_2, K_T_2)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def _parse_fiber_block(src: str, sec_tag: int) -> list[tuple[float, float, float, int]]:
    """Return [(y, z, area, matTag), ...] for one ``section Fiber N { ... }`` block."""
    m = re.search(rf"section\s+Fiber\s+{sec_tag}\s*\{{(.*?)\n\}}", src, re.S)
    if not m:
        return []
    body = m.group(1)
    fibers: list[tuple[float, float, float, int]] = []
    for fm in re.finditer(
        r"fiber\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+(\d+)", body
    ):
        fibers.append((float(fm.group(1)), float(fm.group(2)),
                       float(fm.group(3)), int(fm.group(4))))
    return fibers


def define_sections(src: str) -> None:
    """Rebuild both RC fibre sections + Aggregators (source, verbatim).

    VERBATIM FIBER REPLAY (§12aq): every ``fiber`` line of EXAM7.tcl --
    sec 1: 25 x 6400 mm² Concrete02 + 20 x 196 mm² Steel01;
    sec 2: 25 x 4000 mm² Concrete02 + 10 x 125.6 mm² Steel01 -- is
    re-emitted with ops.fiber(y, z, area, matTag) preserving exact
    centroid + area, each wrapped by its section Aggregator (1001/1002).

    -GJ (LESSONS item 11): the Tcl source omits -GJ on both sections, so
    the fiber sections carry NO torsion and the Aggregators' T codes
    govern alone.  OpenSeesPy REQUIRES -GJ, so negligible 1.0 is passed.
    """
    # NOTE sec 1 is ALL-Steel01 in the source (25 x 6400 mm² "concrete"
    # grid + 20 x 196 mm² rebar ALL carry mat tag 1); only sec 2 mixes
    # Concrete02 (25 x 4000 mm²) with Steel01 rebar (10 x 125.6 mm²).
    # Replayed verbatim -- the column-as-steel quirk is the author's.
    agg_of = {
        SEC_FIBER_1: (SEC_AGG_1, INTEG_1, MAT_VY_1, MAT_VZ_1, MAT_T_1,
                      {MAT_S1: 45}, 45),
        SEC_FIBER_2: (SEC_AGG_2, INTEG_2, MAT_VY_2, MAT_VZ_2, MAT_T_2,
                      {MAT_C2: 25, MAT_S1: 10}, 35),
    }
    for sec_tag, (agg, integ, mvy, mvz, mt, mix, n_exp) in agg_of.items():
        fibers = _parse_fiber_block(src, sec_tag)
        assert len(fibers) == n_exp, f"sec {sec_tag}: {len(fibers)} fibers, expected {n_exp}"
        counts: dict[int, int] = {}
        for (_, _, _, m) in fibers:
            counts[m] = counts.get(m, 0) + 1
        assert counts == mix, f"sec {sec_tag}: mat mix {counts}, expected {mix}"
        ops.section("Fiber", sec_tag, "-GJ", 1.0)
        for (y, z, area, mat) in fibers:
            # OpenSeesPy fiber signature: fiber(y, z, area, matTag)
            ops.fiber(y, z, area, mat)
        ops.section("Aggregator", agg,
                    mvy, "Vy", mvz, "Vz", mt, "T",
                    "-section", sec_tag)
        ops.beamIntegration("Lobatto", integ, agg, N_IP)


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 63 nodes + 3-component lumped mass, verbatim.

    Unlike the static Dino models, mass here has UX/UY/UZ components (active
    in the transient).  Values are already N-s^2/mm; no conversion applied.
    """
    n_node = 0
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))
        n_node += 1
    assert n_node == 63, f"expected 63 nodes, parsed {n_node}"
    n_mass = 0
    for m in re.finditer(
        r"^mass\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.mass(int(m.group(1)), float(m.group(2)), float(m.group(3)),
                 float(m.group(4)), 0.0, 0.0, 0.0)
        n_mass += 1
    assert n_mass == 63, f"expected 63 mass lines, parsed {n_mass}"


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Apply the nine fully-fixed base nodes 37-45 (tolerates trailing ';').

    The source prints "rigidDiaphragm" / "mass" / "node" labels but issues no
    MP-constraint commands, so Plain constraints are used for gravity.
    """
    n_fix = 0
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)
        n_fix += 1
    assert n_fix == 9, f"expected 9 fix lines, parsed {n_fix}"


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> int:
    """Create geomTransf + forceBeamColumn elements, verbatim.

    The source ``element nonlinearBeamColumn`` is the legacy force-based
    element = OpenSeesPy ``forceBeamColumn`` (NOT dispBeamColumn).
    ``tag i j nIP secTag transfTag`` → (tag, i, j, transfTag, integTag)
    with the shared Lobatto rule of the element's section (§12l).
    geomTransf Linear (126 transforms).  Returns element count.
    """
    n_transf = 0
    for m in re.finditer(
        r"^geomTransf\s+Linear\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)",
        src, re.M,
    ):
        ops.geomTransf("Linear", int(m.group(1)),
                       float(m.group(2)), float(m.group(3)), float(m.group(4)))
        n_transf += 1
    assert n_transf == 126, f"expected 126 geomTransf, parsed {n_transf}"

    integ_of = {SEC_AGG_1: INTEG_1, SEC_AGG_2: INTEG_2}
    n = 0
    for m in re.finditer(
        r"^element\s+nonlinearBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        src, re.M,
    ):
        tag = int(m.group(1))
        n1, n2 = int(m.group(2)), int(m.group(3))
        sec = int(m.group(5))
        transf = int(m.group(6))
        ops.element("forceBeamColumn", tag, n1, n2, transf, integ_of[sec])
        n += 1
    assert n == 126, f"expected 126 elements, parsed {n}"
    return n


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a static/transient RC frame model.

    ``save_frame_resp=False`` -- consistent with the other Dino
    fiber-section models (internal sections lack user-visible tags;
    §12v).  ``set_odb_path`` precedes ``CreateODB`` (§12ac).
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
        save_shell_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads(src: str) -> int:
    """DEAD pattern: replay EVERY beamUniform eleLoad line, verbatim.

    The source lists ~450 eleLoad lines (many duplicated element tags --
    duplicates ACCUMULATE in the pattern, as in Tcl).  Returns the count.
    """
    ops.timeSeries("Linear", TS_GRAV)
    ops.pattern("Plain", PAT_GRAV, TS_GRAV)
    n = 0
    for m in re.finditer(
        r"^eleLoad\s+-ele\s+(\d+)\s+-type\s+-beamUniform\s+"
        r"([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M,
    ):
        ops.eleLoad("-ele", int(m.group(1)), "-type", "-beamUniform",
                    float(m.group(2)), float(m.group(3)), float(m.group(4)))
        n += 1
    return n


def define_ground_motion(gm_dir: Path) -> None:
    """UniformExcitation dir-1 from ground_motions/GM1X.txt (source).

    GM1X.txt is byte-identical to ref/OPENSEES/GM1X.txt (2048 pts @ 0.02 s,
    factor 0.6072 -- the "large" level of result_all.xlsx).
    """
    ops.timeSeries("Series", TS_GM, "-dt", DT_GM,
                   "-filePath", str(gm_dir / "GM1X.txt"),
                   "-factor", GM_FACTOR)
    ops.pattern("UniformExcitation", PAT_GM, GM_DIR, "-accel", TS_GM)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB", history: list) -> bool:
    """Gravity: LoadControl 0.1 x 10 steps (source), manual loop + ODB.

    Permitted SmartAnalyze exception (AGENT §3c/§10): SmartAnalyze Static
    forces DisplacementControl, so true load-controlled gravity uses
    ``ops.analyze()`` directly with the source's Newton / EnergyIncr 1e-6.
    History rows 0-9 mirror node59.out rows 0-9 (time 0.1-1.0).
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", GRAV_INCR)
    ops.analysis("Static")
    ok = 0
    for _ in range(N_GRAV_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"  WARNING: gravity step {len(history)} failed (ok={ok})")
            break
        odb.fetch_response_step()
        ops.reactions()
        history.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_MONITOR, 1)),
        ))
    ops.loadConst("-time", 0.0)   # freeze gravity, reset pseudo-time
    ops.wipeAnalysis()  # clear Static objects so Newmark sets cleanly below
    return ok == 0


def apply_rayleigh_damping() -> None:
    """Rayleigh damping, 5% on modes 1-2 (source eigen-based computation)."""
    lam = ops.eigen(N_EIGEN)
    om_i = lam[0] ** 0.5
    om_j = lam[1] ** 0.5
    alpha_m = DAMP_RATIO * 2.0 * om_i * om_j / (om_i + om_j)
    beta_k = 2.0 * DAMP_RATIO / (om_i + om_j)
    ops.rayleigh(alpha_m, beta_k, 0.0, 0.0)


def run_transient(odb: "opst.post.CreateODB", history: list,
                  shear_hist: list, n_steps: int | None = None) -> bool:
    """X-direction seismic transient (Newmark 0.5/0.25) via SmartAnalyze.

    Mirrors the source (Transformation / Plain / UmfPack, NormDispIncr
    0.1 / 1000, Newmark, analyze 3000 x 0.005).  Plain Newton first
    (flag 10, LESSONS 14); fallbacks allowed for transient robustness.
    Per-step in-loop history (time, node-59 UX) plus base-column
    localForce for eles 106-114 (Tcl sign convention: flip sim Vz,
    idx 2/8, before diffing — orientation-dependent, see post_process).
    ODB fetch throttled to every ODB_EVERY_N steps (§3d large-model rule).
    """
    if n_steps is None:
        n_steps = N_STEPS
    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("UmfPack")
    ops.integrator("Newmark", 0.5, 0.25)   # set BEFORE SmartAnalyze
    # NOTE TEST_TOL default = source 0.1.  Tight 1e-6 tracks the same path
    # here (both agree step-for-step) at ~30x cost -- the Exam08 loose-tol
    # artifact does NOT occur in this transient (LESSONS 15 n/a); the
    # large-level divergence is formulation drift (see README).
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="NormDispIncr",
        testTol=TEST_TOL,
        testIterTimes=1000,
        tryAlterAlgoTypes=False,
        algoTypes=[10],
        tryAddTestTimes=False,
        printPer=0,
        testPrintFlag=0,
    )
    segs = analysis.transient_split(n_steps)
    ok = 0
    for i, _ in enumerate(segs):
        ok = analysis.TransientAnalyze(DT_ANALYSIS)
        if ok < 0:
            print(f"  WARNING: transient step {len(history)} failed (ok={ok})")
            break
        if i % ODB_EVERY_N == 0:
            odb.fetch_response_step()
        ops.reactions()
        history.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_MONITOR, 1)),
        ))
        shear_hist.append([
            float(ops.getTime()),
            [list(map(float, ops.eleResponse(e, "localForce")))
             for e in SHEAR_ELES],
        ])
    analysis.close()
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run gravity + transient, return ODB + results.

    Returns:
        (odb, results) with hist (2,N) [time, node59-UX], shear list,
        ref arrays from node59.out / shear.out.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    gm_dir = Path(__file__).parent / "ground_motions"
    src = TCL_FILE.read_text()

    init_model()
    define_materials()
    define_sections(src)
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_ele = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_ele} forceBeamColumn elements (expected 126).")

    odb = create_odb(output_dir)

    history: list[tuple[float, float]] = []
    shear_hist: list = []
    n_ld = define_gravity_loads(src)
    print(f"  Gravity eleLoads replayed: {n_ld} lines.")
    vis_loads(output_dir)
    print("Running gravity analysis...")
    run_gravity(odb, history)

    define_ground_motion(gm_dir)
    vis_pre_analysis(output_dir)
    apply_rayleigh_damping()
    n_tr = N_TRIAL_STEPS if N_TRIAL_STEPS else N_STEPS
    print(f"Running transient analysis ({n_tr} steps)...")
    run_transient(odb, history, shear_hist, n_steps=n_tr)

    hist = np.array(history, dtype=float).T  # (2, N)
    ref = np.loadtxt(str(REF_NODE)).T if REF_NODE.exists() else None
    ref_sh = np.loadtxt(str(REF_SHEAR)).T if REF_SHEAR.exists() else None
    results = {"hist": hist, "ref": ref, "ref_shear": ref_sh,
               "shear": shear_hist}
    sh_times = np.array([s[0] for s in shear_hist], dtype=float)
    sh_forces = np.array([s[1] for s in shear_hist], dtype=float)  # (M,9,12)
    np.savez(output_dir / "transient_history.npz", hist=hist,
             ref=ref if ref is not None else np.zeros((0, 0)),
             shear_t=sh_times, shear_f=sh_forces,
             ref_shear=results["ref_shear"] if results["ref_shear"] is not None
             else np.zeros((0, 0)))
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, verify node-59 + shear histories.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis.
    """
    odb.save_response()
    vis_defo(output_dir, filename="vis_05_deformed.html", odb_tag=ODB_TAG, resp_dof="UX")
    vis_slider(output_dir, filename="vis_06_slider.html", odb_tag=ODB_TAG, resp_dof="UX")

    hist, ref = results.get("hist"), results.get("ref")
    if hist is not None and hist.size and ref is not None:
        n = min(hist.shape[1], ref.shape[1])
        sim_t, sim_ux = hist[0, :n], hist[1, :n]
        ref_t, ref_ux = ref[0, :n], ref[1, :n]
        denom = np.maximum(np.abs(ref_ux), 1.0)
        ux_rel = np.abs(sim_ux - ref_ux) / denom
        print(f"  node59: {n} steps | UX max-rel-err {ux_rel.max():.5f} "
              f"(mean {ux_rel.mean():.6f}) | UXmax sim {np.abs(sim_ux).max():.2f} "
              f"vs ref {np.abs(ref_ux).max():.2f} mm")
        print(f"  time: sim [{sim_t[0]:.3f}, {sim_t[-1]:.3f}] vs "
              f"ref [{ref_t[0]:.3f}, {ref_t[-1]:.3f}]")

    # Base-column shear verification (shear.out eles 106-114).
    # Sign rule is ORIENTATION-dependent (refines LESSONS 1): for these
    # vertical columns (vecxz 0,0,1) the Py eleResponse Vz (idx 2,8) is the
    # negative of the Tcl localForce recorder; Vy/M/N agree.  Resolved from
    # the quasi-static first transient row, applied to all steps.
    if results.get("ref_shear") is not None and len(results.get("shear", [])):
        sh = results["shear"]
        m = len(sh)
        ref_sh = results["ref_shear"]
        FLIP = [2, 8]
        errs = {}
        for ei in range(9):
            r = ref_sh[1 + ei * 12:1 + (ei + 1) * 12, 10:10 + m].T
            s = np.stack([np.asarray(x[1][ei], dtype=float) for x in sh])
            s[:, FLIP] *= -1.0
            for c, nm in ((0, "N"), (2, "Vz"), (4, "My")):
                denom = max(float(np.abs(r[:, c]).max()), 1.0)
                e = np.abs(s[:, c] - r[:, c]) / denom
                errs.setdefault(nm, []).append((float(e.max()), float(e.mean())))
        for nm, v in errs.items():
            print(f"  shear {nm}: max-of-max {max(x[0] for x in v):.4f} "
                  f"mean-of-mean {sum(x[1] for x in v) / len(v):.5f}")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print(f"Dino_FrameTH transient complete. Output in {output_dir}")
