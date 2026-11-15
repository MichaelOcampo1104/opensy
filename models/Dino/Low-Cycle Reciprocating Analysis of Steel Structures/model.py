# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Low-Cycle Reciprocating Analysis of Steel Structures (Dino Exam08)
UniqueID : Dino_LowCycleSteel
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-08
Purpose  : Gravity + 4-phase low-cycle UX reciprocation of a 2-storey steel
           frame (112 nodes, 128 dispBeamColumn elements; Steel01
           DH300X400X25X25 columns + DH200X200X20X12 beams/braces in
           shear+torsion Aggregators).  After -1e5 N gravity at top nodes
           2/4/6/8, node 4 is cycled +100 / -200 / +225 / -250 mm under a
           250 N reference load; the load-factor history is validated
           against ref/OPENSEES/result.xls (right block, cols F-I).
Ref      : Dino -- Low-Cycle Reciprocating Analysis of Steel Structures
           (original EXAM08.s2k / ETABS EXAM08.EDB; ref/OPENSEES/Exam08.tcl)
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
# Steel01 fiber material + dead Elastic mats + rigid shear/torsion materials
# (source tags verbatim; one set of Vy/Vz/T per Aggregator).
MAT_S1        = 1      # Steel01 295/206000/0.001 (ALL fibers, both sections)
MAT_E2        = 2      # Elastic 2.482e4 (dead -- no fiber references it)
MAT_E3        = 3      # Elastic 1.999e5 (dead -- no fiber references it)
MAT_VY_1      = 201    # Elastic shear-Vy for Aggregator 1001 (columns)
MAT_VZ_1      = 301    # Elastic shear-Vz for Aggregator 1001
MAT_T_1       = 401    # Elastic torsion-T for Aggregator 1001
MAT_VY_2      = 202    # Elastic shear-Vy for Aggregator 1002 (beams/braces)
MAT_VZ_2      = 302    # Elastic shear-Vz for Aggregator 1002
MAT_T_2       = 402    # Elastic torsion-T for Aggregator 1002

# Fiber sections + Aggregator wrappers + shared Lobatto integrations.
SEC_FIBER_1   = 1      # DH300X400X25X25 (columns)
SEC_FIBER_2   = 2      # DH200X200X20X12 (beams/braces)
SEC_AGG_1     = 1001
SEC_AGG_2     = 1002
INTEG_1       = 1001   # beamIntegration Lobatto shared by all sec-1001 elements
INTEG_2       = 1002   # beamIntegration Lobatto shared by all sec-1002 elements

# Validation
NODE_MONITOR  = 4      # cyclic control + recorder node (result.xls anchor)

# Time series / patterns (tags match the source).
TS_GRAV       = 1
PAT_GRAV      = 1
TS_PUSH       = 3
PAT_PUSH      = 3

# ODB
ODB_TAG       = 1

# Source files
TCL_FILE      = Path(__file__).parent / "ref" / "OPENSEES" / "Exam08.tcl"
REF_FILE      = Path(__file__).parent / "ref" / "OPENSEES" / "result.xls"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E/fy in MPa, forces in N).

# Steel01 fiber material (source line, verbatim).
FY_STEEL = 295.0 * MPa
E_STEEL  = 206000.0 * MPa
B_STEEL  = 0.001              # strain-hardening ratio (dimensionless)

# Rigid shear/torsion stiffnesses for the Aggregators (source, verbatim).
K_VY_1 = 6.409e8             # N (columns)
K_VZ_1 = 9.613e8             # N
K_T_1  = 4.005e11            # N*mm^2
K_VY_2 = 1.538e8             # N (beams/braces)
K_VZ_2 = 5.127e8             # N
K_T_2  = 9.089e10            # N*mm^2

# Column section DH300X400X25X25: 24 flange x 625 mm^2 + 12 web x 729.2 mm^2.
# Beam/brace section DH200X200X20X12: 24 flange x 333.3 mm^2 + 12 web x 160 mm^2.
N_IP = 3                     # dispBeamColumn integration points (source)

# Gravity (source: LoadControl 0.5 x analyze 10 -> LF 5.0).
P_GRAV       = -1.0e5 * N    # UZ at each of nodes 2/4/6/8 (total -4e5 N ref)
GRAV_INCR    = 0.5           # load factor per step (dimensionless)
N_GRAV_STEPS = 10            # -> LF 5.0 total

# Low-cycle reciprocation (source: DisplacementControl node 4 DOF 1).
P_PUSH     = 250.0 * N       # UX reference at each of nodes 2/4/6/8
CTRL_DOF   = 1               # UX displacement control at node 4
# (signed increment [mm], n-steps): +100 / -200 / +225 / -250 mm.
CYC_PHASES = [
    (+0.100 * mm, 1000),
    (-0.200 * mm, 1000),
    (+0.225 * mm, 1000),
    (-0.250 * mm, 1000),
]
RUN_PHASES = 4               # full run: gravity + all 4 cyclic phases (4010 steps)

# ODB stride (§3d): 4000+ steps x 112 nodes -> fetch every Nth step.
ODB_EVERY_N = 20             # ~200 cyclic fetches + 10 gravity

N_TOTAL_STEPS = N_GRAV_STEPS + sum(n for (_, n) in CYC_PHASES)  # 4010


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Steel01 fiber + rigid shear/torsion materials (source, verbatim).

    MAT_E2 / MAT_E3 are defined in the source but referenced by no fiber
    -- kept for tag fidelity (same rule as Dino §12ap-6).  The commented
    ``Elastic 1`` line in the source is NOT defined (Steel01 tag 1 active).
    """
    ops.uniaxialMaterial("Steel01", MAT_S1, FY_STEEL, E_STEEL, B_STEEL)
    ops.uniaxialMaterial("Elastic", MAT_E2, 2.482e4 * MPa)
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
    """Rebuild both fiber sections + Aggregators (source, verbatim).

    VERBATIM FIBER REPLAY (§12aq): every ``fiber`` line of Exam08.tcl
    (36 + 36 fibres, all on Steel01 mat 1) is re-emitted with
    ops.fiber(y, z, area, matTag) preserving exact centroid + area, each
    wrapped by its section Aggregator (1001/1002) adding rigid Vy/Vz/T.

    -GJ (LESSONS item 11): the Tcl source omits -GJ on both sections, so the
    fiber sections carry NO torsion and the Aggregators' T codes govern
    alone.  OpenSeesPy REQUIRES -GJ, so negligible 1.0 is passed.  The polar
    G·Σ(A·r²) recipe (≈144x / 83x the Aggregator T here) is WRONG for this
    configuration (cf. Dino_ReticulatedShell, 184x, +6.5% post-buckling).
    """
    agg_of = {
        SEC_FIBER_1: (SEC_AGG_1, INTEG_1, MAT_VY_1, MAT_VZ_1, MAT_T_1),
        SEC_FIBER_2: (SEC_AGG_2, INTEG_2, MAT_VY_2, MAT_VZ_2, MAT_T_2),
    }
    for sec_tag, (agg, integ, mvy, mvz, mt) in agg_of.items():
        fibers = _parse_fiber_block(src, sec_tag)
        assert len(fibers) == 36, f"sec {sec_tag}: parsed {len(fibers)} fibers, expected 36"
        assert all(m == MAT_S1 for (_, _, _, m) in fibers), f"sec {sec_tag}: non-Steel01 fiber"
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
    """Create the 112 nodes + lumped mass from Exam08.tcl, verbatim.

    Mass is applied on UX and UY only (zero on UZ/rotations); only nodes
    1-12, 29-44 and 61-76 carry mass in the source.  Values are already in
    N-s^2/mm so no conversion is applied.  (Static analysis: mass inactive.)
    """
    n_node = 0
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))
        n_node += 1
    assert n_node == 112, f"expected 112 nodes, parsed {n_node}"
    for m in re.finditer(
        r"^mass\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.mass(int(m.group(1)), float(m.group(2)), float(m.group(3)),
                 0.0, 0.0, 0.0, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Apply the four fully-fixed base nodes 9-12 (tolerates trailing ';').

    The source prints "rigidDiaphragm" / "mass" / "node" labels but issues no
    MP-constraint commands, so Plain constraints are used throughout.
    """
    n_fix = 0
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)
        n_fix += 1
    assert n_fix == 4, f"expected 4 fix lines, parsed {n_fix}"


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> int:
    """Create geomTransf + dispBeamColumn elements from Exam08.tcl, verbatim.

    geomTransf Linear (128 transforms: (1,0,0) beams/columns, (0,0,1)
    verticals, (±0.8,0,0.6) braces).  dispBeamColumn (128 elements:
    ``tag i j nIP secTag transfTag``) -- OpenSeesPy form takes
    (tag, i, j, transfTag, integTag) with the shared Lobatto rule of the
    element's section (§12l).  Returns the number of elements created.
    """
    n_transf = 0
    for m in re.finditer(
        r"^geomTransf\s+Linear\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)",
        src, re.M,
    ):
        ops.geomTransf("Linear", int(m.group(1)),
                       float(m.group(2)), float(m.group(3)), float(m.group(4)))
        n_transf += 1
    assert n_transf == 128, f"expected 128 geomTransf, parsed {n_transf}"

    integ_of = {SEC_AGG_1: INTEG_1, SEC_AGG_2: INTEG_2}
    n = 0
    for m in re.finditer(
        r"^element\s+dispBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        src, re.M,
    ):
        tag = int(m.group(1))
        n1, n2 = int(m.group(2)), int(m.group(3))
        sec = int(m.group(5))
        transf = int(m.group(6))
        ops.element("dispBeamColumn", tag, n1, n2, transf, integ_of[sec])
        n += 1
    assert n == 128, f"expected 128 elements, parsed {n}"
    return n


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a static steel frame model.

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
GRAV_NODES = (2, 4, 6, 8)    # -1e5 N UZ each (DEAD pattern)
PUSH_NODES = (2, 4, 6, 8)    # +250 N UX each (PUSH pattern)


def define_gravity_loads() -> None:
    """DEAD pattern (source): -1e5 N UZ at each top node 2/4/6/8."""
    ops.timeSeries("Linear", TS_GRAV)
    ops.pattern("Plain", PAT_GRAV, TS_GRAV)
    for nd in GRAV_NODES:
        ops.load(nd, 0.0, 0.0, P_GRAV, 0.0, 0.0, 0.0)


def define_push_loads() -> None:
    """PUSH pattern (source): +250 N UX at each top node 2/4/6/8."""
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    for nd in PUSH_NODES:
        ops.load(nd, P_PUSH, 0.0, 0.0, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def _record(odb: "opst.post.CreateODB", history: list) -> None:
    """Fetch ODB + append (load factor, node-4 UX/UY/UZ) to history."""
    odb.fetch_response_step()
    ops.reactions()
    history.append((
        float(ops.getTime()),
        float(ops.nodeDisp(NODE_MONITOR, 1)),
        float(ops.nodeDisp(NODE_MONITOR, 2)),
        float(ops.nodeDisp(NODE_MONITOR, 3)),
    ))


def run_gravity(odb: "opst.post.CreateODB", history: list) -> bool:
    """Gravity: LoadControl 0.5 x 10 steps (source), manual loop + ODB.

    Permitted SmartAnalyze exception (AGENT §3c/§10): SmartAnalyze Static
    forces DisplacementControl, so true load-controlled gravity uses
    ``ops.analyze()`` directly with the source's Newton / EnergyIncr 1e-6.
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
        _record(odb, history)
    ops.loadConst("-time", 0.0)   # freeze gravity, reset pseudo-time
    return ok == 0


def run_cyclic(odb: "opst.post.CreateODB", history: list) -> bool:
    """4-phase UX reciprocation: DisplacementControl node 4 DOF 1.

    One increment per reference step via static_split([incr],
    maxStep=|incr|) so the recorder stays 1:1 with the 4000-row reference
    (§12am per-increment cadence).  ODB fetch throttled to every
    ODB_EVERY_N steps (§3d); the in-loop history stays per-step.
    Plain Newton (flag 10) + NormDispIncr 1e-6 / 200 iter; see the
    testTol NOTE above for why 1e-6 replaces the source 0.1.
    """
    ops.constraints("Plain")
    ops.numberer("RCM")
    # UmfPack mirrors the source (BandGeneral roundoff differs at knife-edge
    # capacity steps and breaks Newton convergence there).
    ops.system("UmfPack")

    # No algo/test fallback (both False).  SmartAnalyze is retained as the
    # DisplacementControl driver.  NOTE flag 10 = plain Newton: the opensy
    # default first-flag 40 is KrylovNewton, which diverges where Newton
    # passes; 10 mirrors the source solver.
    # NOTE testTol 1e-6, NOT the source 0.1: the source's loose
    # NormDispIncr 0.1 accepts non-equilibrium points near the virgin
    # capacity (UX~50), producing a spurious softening branch (xls block A:
    # 6637 -> 6253 in phase 1, degrading to 5900 by phase 4) and killing
    # the 2012-Newton path under current OpenSeesPy at reversals.  Tight
    # 1e-6 recovers the TRUE hardening curve = xls block B (bit-exact,
    # mean rel err 1e-6 over phase 1).  Block A is retained only as the
    # documented loose-tolerance artifact; the anchor is block B.
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="NormDispIncr",
        testTol=1.0e-6,
        testIterTimes=200,
        tryAlterAlgoTypes=False,
        algoTypes=[10],
        tryAddTestTimes=False,
        printPer=0,
        testPrintFlag=0,
    )

    ok = 0
    step = 0
    for phase, (incr, n_steps) in enumerate(CYC_PHASES[:RUN_PHASES]):
        segs = analysis.static_split([n_steps * incr], maxStep=abs(incr))
        assert len(segs) == n_steps, f"phase {phase}: {len(segs)} segs, expected {n_steps}"
        for seg in segs:
            ok = analysis.StaticAnalyze(
                node=NODE_MONITOR, dof=CTRL_DOF, seg=seg)
            if ok < 0:
                print(f"  WARNING: cyclic step {len(history)} failed (ok={ok})")
                break
            step += 1
            if step % ODB_EVERY_N == 0:
                odb.fetch_response_step()
            ops.reactions()
            history.append((
                float(ops.getTime()),
                float(ops.nodeDisp(NODE_MONITOR, 1)),
                float(ops.nodeDisp(NODE_MONITOR, 2)),
                float(ops.nodeDisp(NODE_MONITOR, 3)),
            ))
        if ok < 0:
            break
        print(f"  Phase {phase + 1} complete ({n_steps} steps).")
    analysis.close()
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run gravity + cyclic, return ODB + results.

    Returns:
        (odb, results) where results has keys: hist (4,N) sim
        [LF,UX,UY,UZ] history, refA (4,N) left xls block, refB (4,N) right.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    src = TCL_FILE.read_text()

    init_model()
    define_materials()
    define_sections(src)
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_ele = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_ele} dispBeamColumn elements (expected 128).")

    odb = create_odb(output_dir)

    history: list[tuple[float, float, float, float]] = []
    define_gravity_loads()
    vis_loads(output_dir)
    print("Running gravity analysis...")
    run_gravity(odb, history)

    define_push_loads()
    vis_pre_analysis(output_dir)
    print("Running cyclic analysis...")
    run_cyclic(odb, history)

    hist = np.array(history, dtype=float).T  # (4, N)
    results = {"hist": hist, "refA": None, "refB": None}
    if REF_FILE.exists():
        import xlrd
        wb = xlrd.open_workbook(str(REF_FILE))
        sh = wb.sheet_by_name("Sheet1")
        n = sh.nrows
        refA = np.array([[(sh.cell_value(r, c) or 0.0) for r in range(n)]
                         for c in range(4)], dtype=float)
        refB = np.array([[(sh.cell_value(r, c + 5) or 0.0) for r in range(n)]
                         for c in range(4)], dtype=float)
        results["refA"] = refA
        results["refB"] = refB
    np.savez(output_dir / "cyclic_history.npz", hist=hist,
             refA=results["refA"] if results["refA"] is not None else np.zeros((0, 0)),
             refB=results["refB"] if results["refB"] is not None else np.zeros((0, 0)))
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, report history vs both xls blocks.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis (hist/refA/refB arrays).
    """
    odb.save_response()
    vis_defo(output_dir, filename="vis_05_deformed.html", odb_tag=ODB_TAG, resp_dof="UX")
    vis_slider(output_dir, filename="vis_06_slider.html", odb_tag=ODB_TAG, resp_dof="UX")

    hist = results.get("hist")
    for tag, key in (("left-A", "refA"), ("right-B", "refB")):
        ref = results.get(key)
        if hist is None or not hist.size or ref is None:
            continue
        n = min(hist.shape[1], ref.shape[1])
        sim_lf, sim_ux = hist[0, :n], hist[1, :n]
        ref_lf, ref_ux = ref[0, :n], ref[1, :n]
        denom = np.maximum(np.abs(ref_lf), 1.0)
        lf_rel = np.abs(sim_lf - ref_lf) / denom
        print(f"  vs block {tag}: {n} steps | LF max-rel-err {lf_rel.max():.5f} "
              f"(mean {lf_rel.mean():.6f}) | UX max-abs-err "
              f"{np.abs(sim_ux - ref_ux).max():.3e} mm")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print(f"Dino_LowCycleSteel cyclic complete. Output in {output_dir}")
