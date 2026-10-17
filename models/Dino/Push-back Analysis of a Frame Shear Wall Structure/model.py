# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Push-back Analysis of a Frame Shear Wall Structure (Dino)
UniqueID : Dino_FrameWall
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-03
Purpose  : Eigen (39 modes) + gravity + displacement-controlled pushback
           (1 mm x 900 steps) of a 3D frame shear-wall structure (956
           nodes; 936 dispBeamColumn fiber elements + 364 elasticBeamColumn).
           Node 40 is pushed 900 mm in UX; eigenvalues validate against
           ref/Periods.txt, the mode-1 shape against eigen1_node.out, and
           the node-40 history against node40.out.
Ref      : Dino -- Push-back Analysis of a Frame Shear Wall Structure
           (original co.tcl)
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
# Fiber materials (match source co.tcl tags exactly).
MAT_STEEL     = 1      # Steel01 rebar
MAT_ELASTIC   = 2      # Elastic (fiber section filler)
MAT_CONCRETE  = 3      # Concrete01 concrete
# Rigid shear/torsion materials feeding Aggregators 1001-1004 (verbatim).
MAT_RIGID     = (201, 301, 401, 202, 302, 402, 203, 303, 403,
                 204, 304, 404, 205, 305, 405, 206, 306, 406)

# Fiber sections + Aggregator wrappers + shared Lobatto integrations.
SEC_FIBER     = (1, 2, 3, 4)
SEC_AGG       = (1001, 1002, 1003, 1004)
INTEG         = (1001, 1002, 1003, 1004)

# Elements carry source tags verbatim (dispBeamColumn + elasticBeamColumn).
# Time series / patterns (tags match the source).
TS_GRAVITY    = 1
PAT_GRAVITY   = 1
TS_PUSH       = 2
PAT_PUSH      = 2

# Validation
NODE_MONITOR  = 40     # node-40 history validated against node40.out
N_MODES       = 39     # eigen modes (source: set numModes 39)

# ODB (nodal-only; throttled for the 900-step pushover, §3d).
ODB_TAG       = 1
ODB_EVERY_N   = 10

# Source files
TCL_FILE      = Path(__file__).parent / "ref" / "co.tcl"
REF_HIST      = Path(__file__).parent / "ref" / "node40.out"
REF_PERIODS   = Path(__file__).parent / "ref" / "Periods.txt"
REF_MODE1     = Path(__file__).parent / "ref" / "eigen1_node.out"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N).

# Fiber materials (source lines, verbatim).
STEEL_FY = 400.0 * MPa
STEEL_E  = 200000.0 * MPa
STEEL_B  = 0.01
E_FILL   = 2.550e4 * MPa
CONC_FPC    = -23.4 * MPa
CONC_EPSC0  = -0.0015
CONC_FPCU   = -10.0 * MPa
CONC_EPSU   = -0.006

# Torsional stiffness GJ for the bare fiber sections (§12au).  The Tcl source
# omits -GJ (Tcl only warns); OpenSeesPy 3D ``section Fiber`` REQUIRES it.
# CRITICAL: use a NEGLIGIBLE value (1.0), NOT G*Sum(A*r^2).  The Aggregator's
# rigid T material already supplies the section torsion, and the Aggregator
# ADDS the fiber section's own GJ in parallel -- a physical GJ on these
# large sections stiffens torsion-sensitive modes by 10-30% (verified
# 2026-10-03: computed GJ gave +31% on mode 2; GJ=1.0 matches all 39
# eigenvalues to 0.0000%).  Tcl's missing torsion behaves as ~zero.
SEC_GJ = 1.0      # N*mm^2 -- negligible by design (see above)

# Analysis.
N_GRAV_STEPS = 10
GRAV_LAMBDA  = 0.1          # LoadControl step (-> t = 1.0 after gravity)
N_PUSH_STEPS = 900           # DisplacementControl 1 mm x 900
PUSH_INCR    = 1.0 * mm      # signed +1 mm UX per reference step
N_IP         = 3             # dispBeamColumn integration points (source)

# Total recorded steps = initial zero row + gravity + pushover.
N_TOTAL_STEPS = 1 + N_GRAV_STEPS + N_PUSH_STEPS  # 911


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials(src: str) -> None:
    """Steel01 + Elastic filler + Concrete01 + rigid Elastic (source, verbatim).

    Rigid shear/torsion stiffnesses are parsed from the source's
    ``uniaxialMaterial Elastic <tag> <E>`` lines so the 18 values stay
    byte-faithful without hand-copying.
    """
    ops.uniaxialMaterial("Steel01", MAT_STEEL, STEEL_FY, STEEL_E, STEEL_B)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC, E_FILL)
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE,
                         CONC_FPC, CONC_EPSC0, CONC_FPCU, CONC_EPSU)
    for m in re.finditer(
        r"^uniaxialMaterial\s+Elastic\s+(\d+)\s+([\d.eE+-]+)", src, re.M
    ):
        tag = int(m.group(1))
        if tag >= 200:  # rigid shear/torsion mats only (1/2/3 handled above)
            ops.uniaxialMaterial("Elastic", tag, float(m.group(2)))


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
    """Rebuild the four fiber sections + Aggregators (source, verbatim).

    VERBATIM FIBER REPLAY (§12aq): every ``fiber`` line of co.tcl is
    re-emitted with ops.fiber(y, z, area, matTag).  Each fiber section is
    wrapped by a section Aggregator adding rigid Vy/Vz/T codes.

    -GJ (§12au, tiny-value variant): OpenSeesPy 3D ``section Fiber``
    REQUIRES -GJ (Tcl only warns); pass SEC_GJ = 1.0 (negligible).  The
    Aggregator's rigid T code supplies the torsion and ADDS the fiber GJ
    in parallel, so a physical GJ would corrupt torsion-sensitive modes
    (verified: G*Sum(A*r^2) gave +31% on mode 2; GJ=1.0 matches all 39
    eigenvalues to 0.0000%).
    """
    rigid_of = {1001: (201, 301, 401), 1002: (202, 302, 402),
                1003: (203, 303, 403), 1004: (204, 304, 404)}
    for sec_tag, agg_tag, integ_tag in zip(SEC_FIBER, SEC_AGG, INTEG):
        fibers = _parse_fiber_block(src, sec_tag)
        ops.section("Fiber", sec_tag, "-GJ", SEC_GJ)
        for (y, z, area, mat) in fibers:
            # OpenSeesPy fiber signature: fiber(y, z, area, matTag)
            ops.fiber(y, z, area, mat)
        mvy, mvz, mt = rigid_of[agg_tag]
        ops.section("Aggregator", agg_tag,
                    mvy, "Vy", mvz, "Vz", mt, "T",
                    "-section", sec_tag)
        ops.beamIntegration("Lobatto", integ_tag, agg_tag, N_IP)


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 956 nodes + lumped mass from co.tcl, verbatim.

    Mass is applied on UX and UY only (zero on UZ/rotations) at 436 nodes.
    Values are already in N-s^2/mm so no conversion is applied.
    """
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))
    for m in re.finditer(
        r"^mass\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.mass(int(m.group(1)), float(m.group(2)), float(m.group(3)),
                 0.0, 0.0, 0.0, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Apply the 20 fully-fixed nodes from co.tcl (trailing ';' tolerated).

    (The source prints a "rigidDiaphragm" label but issues no MP-constraint
    commands, so Plain constraints are used throughout.)
    """
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> tuple[int, int]:
    """Create geomTransf + dispBeamColumn + elasticBeamColumn (source, verbatim).

    dispBeamColumn ``(tag, i, j, nIP, secTag, transfTag)`` maps to
    OpenSeesPy ``(tag, i, j, transfTag, integTag)`` via the shared Lobatto
    beamIntegration per Aggregator section (§12l).  elasticBeamColumn keeps
    its native 3D form ``(tag, i, j, A, E, G, J, Iy, Iz, transfTag)``.
    Returns (n_disp, n_elastic).
    """
    for m in re.finditer(
        r"^geomTransf\s+Linear\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)",
        src, re.M,
    ):
        ops.geomTransf("Linear", int(m.group(1)),
                       float(m.group(2)), float(m.group(3)), float(m.group(4)))

    integ_of = dict(zip(SEC_AGG, INTEG))
    n_disp = 0
    for m in re.finditer(
        r"^element\s+dispBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        src, re.M,
    ):
        ops.element("dispBeamColumn", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), int(m.group(6)),
                    integ_of[int(m.group(5))])
        n_disp += 1

    n_elastic = 0
    for m in re.finditer(
        r"^element\s+elasticBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)"
        r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)"
        r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+(\d+)", src, re.M,
    ):
        ops.element("elasticBeamColumn", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), float(m.group(4)), float(m.group(5)),
                    float(m.group(6)), float(m.group(7)), float(m.group(8)),
                    float(m.group(9)), int(m.group(10)))
        n_elastic += 1
    return n_disp, n_elastic


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a large frame-wall model.

    Nodal responses only (``save_frame_resp=False`` -- 936 dispBeamColumn
    x 910 steps of frame data is pure overhead for a disp validation;
    §3d/§12u).  ``set_odb_path`` precedes ``CreateODB`` (§12ac).
    ``model_update=False`` -- no elements are removed/added mid-analysis.
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
def define_gravity_loads(src: str) -> None:
    """Gravity pattern (source pattern 1): 2912 eleLoad beamUniform lines.

    Every line is replayed verbatim -- including the many duplicates, which
    are additive -- so the total gravity load matches the Tcl run exactly.
    """
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    for m in re.finditer(r"^eleLoad\s+-ele\s+(\d+)\s+-type\s+-beamUniform"
                         r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M):
        ops.eleLoad("-ele", int(m.group(1)), "-type", "-beamUniform",
                    float(m.group(2)), float(m.group(3)), float(m.group(4)))


def define_pushback_loads(src: str) -> None:
    """Pushback reference pattern (source pattern 2, defined after gravity).

    52 UX nodal loads in a triangular-ish distribution (1.17e5 at the
    monitored floor down to 4.17e3 at the roof).  No loadConst exists in
    the source, so the gravity pattern stays live and scales with lambda
    alongside this pattern during the pushback -- replayed faithfully.
    """
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    in_push = False
    for line in src.splitlines():
        s = line.strip()
        if s.startswith("pattern Plain 2"):
            in_push = True
            continue
        if in_push:
            if s.startswith("}"):
                break
            m = re.match(r"load\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+"
                         r"([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+"
                         r"([\d.eE+-]+)", s)
            if m:
                ops.load(int(m.group(1)), *(float(m.group(i))
                                             for i in range(2, 8)))


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_eigen(odb: "opst.post.CreateODB") -> np.ndarray:
    """Eigenvalue analysis (source: set lambda [eigen 39], before any loads).

    Mass is rank-deficient (UX/UY only on 436 of 956 nodes), which defeats
    the ARPACK subspace solver (§12al) -- fall back to -fullGenLapack.
    Returns the 39 eigenvalues (omega^2).
    """
    try:
        lam = ops.eigen(N_MODES)
    except Exception:
        print("  (default eigen solver failed -- trying -fullGenLapack)")
        lam = ops.eigen("-fullGenLapack", N_MODES)
    lam = np.array([float(v) for v in lam])
    try:
        for m in range(1, N_MODES + 1):
            odb.save_eigen_data(mode_tag=m)
    except Exception as e:
        print(f"  (save_eigen_data skipped: {e})")
    return lam


def run_gravity(odb: "opst.post.CreateODB") -> bool:
    """Gravity phase (source: LoadControl 0.1, 10 steps).

    Manual ``ops.analyze()`` loop is the §3c permitted exception for
    LoadControl (SmartAnalyze forces DisplacementControl).  NO loadConst
    afterwards -- the source has none, so gravity stays live into the
    pushback.  ODB collected every step (10 steps, cheap).
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", GRAV_LAMBDA)
    ops.analysis("Static")

    history: list[tuple[float, float, float, float]] = []
    ok = 0
    for step in range(N_GRAV_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"  WARNING: gravity step {step} failed (ok={ok})")
            break
        odb.fetch_response_step()
        ops.reactions()
        history.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_MONITOR, 1)),
            float(ops.nodeDisp(NODE_MONITOR, 2)),
            float(ops.nodeDisp(NODE_MONITOR, 3)),
        ))
    ops.wipeAnalysis()
    run_gravity.history = history  # type: ignore[attr-defined]
    return ok == 0


def run_pushback(odb: "opst.post.CreateODB") -> bool:
    """Pushback phase (source: DisplacementControl 40 1 1.0, 900 steps).

    SmartAnalyze static with one increment per reference step
    (static_split([1 mm], maxStep=1 mm), §12am cadence).  In-loop history
    every step (cheap nodeDisp reads); ODB throttled to every ODB_EVERY_N
    steps for the 900-step phase (§3d: <= ~100 fetches total).
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="NormDispIncr",
        testTol=1.0e-5,
        testIterTimes=200,
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30],
        tryLooseTestTol=True,
        looseTestTolTo=1.0e-4,
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        printPer=0,
        testPrintFlag=0,
    )

    history: list[tuple[float, float, float, float]] = []  # (lf, ux, uy, uz)
    ok = 0
    for i in range(N_PUSH_STEPS):
        segs = analysis.static_split([PUSH_INCR], maxStep=abs(PUSH_INCR))
        step_ok = True
        for seg in segs:
            ok = analysis.StaticAnalyze(
                node=NODE_MONITOR, dof=1, seg=seg)
            if ok < 0:
                step_ok = False
                break
            if i % ODB_EVERY_N == 0:
                odb.fetch_response_step()
        if not step_ok:
            print(f"  WARNING: pushback step {i} failed (ok={ok})")
            break
        ops.reactions()
        history.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_MONITOR, 1)),
            float(ops.nodeDisp(NODE_MONITOR, 2)),
            float(ops.nodeDisp(NODE_MONITOR, 3)),
        ))
        if (i + 1) % 100 == 0:
            print(f"  ... pushback step {i + 1}/{N_PUSH_STEPS}, "
                  f"UX={history[-1][1]:.1f} mm")
    analysis.close()
    run_pushback.history = history  # type: ignore[attr-defined]
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run eigen + gravity + pushback, return ODB + results.

    Returns:
        (odb, results) with eigen (39 eigenvalues), mode1 (956,) mode-1
        UX shape, hist (4,N) sim [LF,UX,UY,UZ] history incl the initial
        zero row, ref (4,911) reference from node40.out.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    src = TCL_FILE.read_text()

    init_model()
    define_materials(src)
    define_sections(src)
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_disp, n_elastic = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_disp} dispBeamColumn + {n_elastic} "
          f"elasticBeamColumn (expected 936 + 364).", flush=True)

    odb = create_odb(output_dir)

    print("Running eigenvalue analysis...", flush=True)
    eigen = run_eigen(odb)
    print(f"  lambda1..3 = {eigen[0]:.4f}, {eigen[1]:.4f}, {eigen[2]:.4f}",
          flush=True)

    # Mode-1 UX shape over all nodes (validates eigen1_node.out).
    try:
        tags = ops.getNodeTags()
        mode1 = np.array([float(ops.nodeEigenvector(int(t), 1, 1))
                          for t in tags])
    except Exception as e:
        print(f"  (mode-1 read failed: {e})")
        mode1, tags = None, None

    # Gravity (before loadConst -- there is none in the source).
    define_gravity_loads(src)
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running gravity analysis...", flush=True)
    run_gravity(odb)

    # Pushback (pattern 2 defined after gravity; gravity stays live).
    define_pushback_loads(src)
    print("Running pushback analysis...", flush=True)
    run_pushback(odb)

    # Reference node-40 history (col0=lambda, col1=UX, col2=UY, col3=UZ;
    # 911 rows = initial zero row + 10 gravity + 900 pushback).
    ref = None
    if REF_HIST.exists():
        ref = np.loadtxt(str(REF_HIST)).T  # (4, 911)
    ref_mode1 = None
    if REF_MODE1.exists():
        try:
            row = np.loadtxt(str(REF_MODE1))
            ref_mode1 = np.atleast_2d(row)[0, 1:]  # drop time col
        except Exception:
            ref_mode1 = None

    ghist = np.array(getattr(run_gravity, "history", []),
                     dtype=float).T  # (4,<=10)
    phist = np.array(getattr(run_pushback, "history", []),
                     dtype=float).T  # (4,<=900)
    zero = np.zeros((4, 1))
    parts = [zero]
    if ghist.size:
        parts.append(ghist)
    if phist.size:
        parts.append(phist)
    hist = np.concatenate(parts, axis=1)
    results = {"hist": hist, "ref": ref, "eigen": eigen,
               "mode1": mode1, "mode_tags": tags, "ref_mode1": ref_mode1}
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot node-40 history, verify.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis.
    """
    odb.save_response()

    hist = results["hist"]
    ref = results["ref"]

    # Dump the full node-40 history for the record.
    if hist is not None and hist.shape[1] > 0:
        step = np.arange(hist.shape[1])
        curve = np.column_stack([step, hist.T])  # (N,5): idx, LF, UX, UY, UZ
        np.savetxt(str(output_dir / "node40_disp_history.csv"), curve,
                   delimiter=",", header="idx,lf,ux_mm,uy_mm,uz_mm")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))

        # V5 -- final deformed shape (pushback is lateral -> UX)
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UX", scale=2.0)
        # V6 -- step slider
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UX", scale=2.0)
        # V7 -- animation
        vis_anim(output_dir, filename="vis_07_animation.html",
                 odb_tag=ODB_TAG, defo_scale=2.0,
                 resp_dof=("UX", "UY", "UZ"))

    # Node-40 UX-vs-load-factor: simulation vs reference (matplotlib)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        if ref is not None and ref.shape[1] > 0:
            ax1.plot(ref[1], ref[0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node40.out)")
        if hist is not None and hist.shape[1] > 0:
            ax1.plot(hist[1], hist[0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax1.set_xlabel(f"Node {NODE_MONITOR} UX displacement (mm)")
        ax1.set_ylabel("Load factor")
        ax1.set_title("Dino_FrameWall -- capacity (UX vs LF)")
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        if ref is not None and ref.shape[1] > 0:
            ax2.plot(np.arange(ref.shape[1]), ref[0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node40.out)")
        if hist is not None and hist.shape[1] > 0:
            ax2.plot(np.arange(hist.shape[1]), hist[0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax2.set_xlabel("Recorded step (1 + 10 gravity + 900 pushback)")
        ax2.set_ylabel("Load factor")
        ax2.set_title("Dino_FrameWall -- load factor history")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "pushback_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable -- skipping compare plot)")

    # Verification summary
    n_sim = hist.shape[1] if hist is not None else 0
    print(f"\n  Recorded steps: {n_sim} / {N_TOTAL_STEPS} expected", flush=True)
    if hist is not None and n_sim > 0:
        labels = ("LF", "UX", "UY", "UZ")
        for d in range(4):
            print(f"  Sim node{NODE_MONITOR} {labels[d]} final = "
                  f"{float(hist[d, -1]):.5f}", flush=True)
        if ref is not None and ref.shape[1] > 0:
            n = min(n_sim, ref.shape[1])
            for d in range(4):
                sv, rv = hist[d, :n], ref[d, :n]
                rms = float(np.sqrt(np.mean((sv - rv) ** 2)))
                denom = np.maximum(np.abs(rv), 1e-12)
                rel = float(np.mean(np.abs(sv - rv) / denom) * 100.0)
                print(f"    {labels[d]}: per-point RMS {rms:.5f} | "
                      f"mean rel error {rel:.4f}%", flush=True)
    eigen = results.get("eigen")
    if eigen is not None and REF_PERIODS.exists():
        ref_lam = np.loadtxt(str(REF_PERIODS))
        n = min(len(eigen), len(ref_lam))
        e_rms = float(np.sqrt(np.mean((eigen[:n] - ref_lam[:n]) ** 2)))
        e_rel = float(np.mean(np.abs(eigen[:n] - ref_lam[:n])
                              / np.maximum(np.abs(ref_lam[:n]), 1e-12)) * 100.0)
        print(f"  Eigen ({n} modes): RMS {e_rms:.5f} | "
              f"mean rel error {e_rel:.4f}%", flush=True)
        print(f"  lambda1: sim={eigen[0]:.5f} ref={ref_lam[0]:.5f}",
              flush=True)
    mode1, ref_mode1 = results.get("mode1"), results.get("ref_mode1")
    if mode1 is not None and ref_mode1 is not None:
        n = min(len(mode1), len(ref_mode1))
        a, b = mode1[:n], ref_mode1[:n]
        # Eigenvectors carry an arbitrary sign -- align before comparing.
        if float(np.dot(a, b)) < 0:
            b = -b
        m_rms = float(np.sqrt(np.mean((a - b) ** 2)))
        m_scale = np.sqrt(np.mean(b ** 2))
        print(f"  Mode-1 shape ({n} nodes): RMS {m_rms:.6f} "
              f"(rel {m_rms / max(m_scale, 1e-12) * 100.0:.4f}%)", flush=True)


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_FrameWall: analysis complete.")
