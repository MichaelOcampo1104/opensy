# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Elastic-Plastic Analysis of Prestressed Beams (Dino)
UniqueID : Dino_PrestressedBeam
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-03
Purpose  : Displacement-controlled UZ pushdown (-1.0 mm x 360 steps) of a
           3D prestressed beam (24 nodes; 23 dispBeamColumn fiber elements
           + 12 rigid elasticBeamColumn links).  Node 19 is pushed down
           360 mm under a -1e3 N reference load; the load-factor history is
           validated against ref/OpenSEES/node19.out.
Ref      : Dino -- Elastic-Plastic Analysis of Prestressed Beams
           (original ref/OpenSEES/co.tcl)
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
# Fiber materials (match source co.tcl tags exactly; the commented Steel02
# line is superseded by the active Steel01 strand line and is NOT defined).
MAT_STEEL     = 1      # Steel01 mild steel (fy=200 MPa)
MAT_E2        = 2      # Elastic filler
MAT_E3        = 3      # Elastic (dead -- referenced by no fiber)
MAT_CONCRETE  = 4      # Concrete02 concrete
MAT_STRAND    = 5      # Steel01 prestressing strand (fy=1600 MPa)

# Fiber sections + shared Lobatto integrations (no Aggregators in source).
SEC_GIRDER    = 1      # section Fiber 1 (concrete grid)
SEC_STRAND    = 3      # section Fiber 3 (concrete + strand ring)
INTEG_1       = 101
INTEG_3       = 103

# Validation
NODE_MONITOR  = 19     # node-19 history validated against node19.out

# Time series / patterns (tags match the source).
TS_GRAVITY    = 1
PAT_GRAVITY   = 1
TS_PUSH       = 2
PAT_PUSH      = 2

# ODB
ODB_TAG       = 1

# Source files
TCL_FILE      = Path(__file__).parent / "ref" / "OpenSEES" / "co.tcl"
REF_FILE      = Path(__file__).parent / "ref" / "OpenSEES" / "node19.out"
REF_FIELD     = Path(__file__).parent / "ref" / "OpenSEES" / "node0.out"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N).

# Steel01 mild steel + strand (source lines, verbatim).
STEEL_FY = 200.0 * MPa
STEEL_E  = 200000.0 * MPa
STEEL_B  = 0.02
STRAND_FY = 1600.0 * MPa
STRAND_E  = 206000.0 * MPa
STRAND_B  = 0.02

# Concrete02 (source line, verbatim): fpc, epsc0, fpcu, epsU, lambda, ft, Ets.
CONC_FPC    = -26.8 * MPa
CONC_EPSC0  = -0.002
CONC_FPCU   = -10.0 * MPa
CONC_EPSU   = -0.005
CONC_LAMBDA = 0.1
CONC_FT     = 2.68 * MPa
CONC_ETS    = 1000.0

# Elastic filler (source lines, verbatim).
E_2 = 2.482e4 * MPa
E_3 = 1.999e5 * MPa

# Torsional stiffness GJ for the bare fiber sections (§12au).  There are NO
# Aggregators in this model, so the fiber GJ is the real torsional stiffness
# (no parallel-add issue, cf. §12ba): G_steel*Sum(A*r^2) per section.
SEC_GJ_SEED = 1.0e10  # N*mm^2 (placeholder; recomputed in define_sections)

# Loading.
P_NODE_PUSH = -1.0e3 * N     # phase-2 reference UZ load at node 19
CTRL_DOF    = 3              # UZ displacement control at node 19
PUSH_INCR   = -1.0 * mm      # displacement increment per step (signed)
N_PUSH_STEPS = 360            # phase-2 recorded steps
N_IP        = 3              # dispBeamColumn integration points (source)

# Total recorded steps = 1 gravity + 360 pushdown (the Tcl recorder writes
# one row per analyze step with no initial zero row: 361 = ref rows).
N_TOTAL_STEPS = 1 + N_PUSH_STEPS  # 361


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Steel01 (mild + strand) + Concrete02 + Elastic (source, verbatim).

    MAT_E3 (Elastic 1.999e5) is defined in the source but referenced by no
    fiber -- kept for tag fidelity.  The commented Steel02 strand line is
    superseded by the active Steel01 strand line (only one may carry tag 5).
    """
    ops.uniaxialMaterial("Steel01", MAT_STEEL, STEEL_FY, STEEL_E, STEEL_B)
    ops.uniaxialMaterial("Elastic", MAT_E2, E_2)
    ops.uniaxialMaterial("Elastic", MAT_E3, E_3)
    ops.uniaxialMaterial("Concrete02", MAT_CONCRETE,
                         CONC_FPC, CONC_EPSC0, CONC_FPCU, CONC_EPSU,
                         CONC_LAMBDA, CONC_FT, CONC_ETS)
    ops.uniaxialMaterial("Steel01", MAT_STRAND,
                         STRAND_FY, STRAND_E, STRAND_B)


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
    """Rebuild the two fiber sections (source, verbatim fiber replay, §12aq).

    Section 1: concrete grid (mat 4).  Section 3: concrete + prestressing
    strand ring (mat 5, 20 fibers on r=50 mm).  Each fiber re-emitted with
    ops.fiber(y, z, area, matTag) preserving exact centroid + area.

    -GJ (§12au, physical variant): no Aggregators wrap these sections, so
    the fiber GJ is the true torsional stiffness -- G_steel*Sum(A*r^2).
    """
    g_steel = STRAND_E / (2.0 * (1.0 + 0.3))  # G = E/(2(1+nu)), nu~0.3
    for sec_tag, integ_tag in ((SEC_GIRDER, INTEG_1),
                               (SEC_STRAND, INTEG_3)):
        fibers = _parse_fiber_block(src, sec_tag)
        gj = g_steel * sum(a * (y * y + z * z) for (y, z, a, _) in fibers)
        ops.section("Fiber", sec_tag, "-GJ", gj)
        for (y, z, area, mat) in fibers:
            # OpenSeesPy fiber signature: fiber(y, z, area, matTag)
            ops.fiber(y, z, area, mat)
        ops.beamIntegration("Lobatto", integ_tag, sec_tag, N_IP)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 24 nodes from co.tcl, verbatim (no masses in source)."""
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Apply fixities from co.tcl (trailing ';' tolerated).

    Node 1 is near-fully fixed (1 1 1 1 0 1); nodes 2-24 are guided
    rollers (0 1 0 1 0 1: UY/RY/RZ held, UX/UZ/RX free).  Six values on
    ndf=6 -- no arity issue (§12ba).  (The source prints a
    "rigidDiaphragm" label but issues no MP-constraint commands.)
    """
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> tuple[int, int]:
    """Create geomTransf + dispBeamColumn + elasticBeamColumn (verbatim).

    dispBeamColumn ``(tag, i, j, nIP, secTag, transfTag)`` maps to
    OpenSeesPy ``(tag, i, j, transfTag, integTag)`` via the shared Lobatto
    beamIntegration per section (§12l).  elasticBeamColumn keeps its native
    3D form ``(tag, i, j, A, E, G, J, Iy, Iz, transfTag)`` -- the 12 links
    use rigid-scale properties (E ~ 2e8 MPa) verbatim.  Returns
    (n_disp, n_elastic).
    """
    for m in re.finditer(
        r"^geomTransf\s+Linear\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)",
        src, re.M,
    ):
        ops.geomTransf("Linear", int(m.group(1)),
                       float(m.group(2)), float(m.group(3)), float(m.group(4)))

    integ_of = {SEC_GIRDER: INTEG_1, SEC_STRAND: INTEG_3}
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
    """Initialise the ODB for a static beam model.

    ``save_frame_resp=False`` (dispBeamColumn internal-section convention
    shared with the other Dino fiber models).  ``set_odb_path`` precedes
    ``CreateODB`` (§12ac).  ``model_update=False`` -- topology is static.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=1,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
        save_shell_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Phase-1 pattern (source pattern 1): a single ZERO load at node 3.

    ``load 3 0 0 0 0 0 0`` -- structurally a no-op that establishes the
    initial analysis state; replayed verbatim.
    """
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    ops.load(3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


def define_pushdown_loads() -> None:
    """Phase-2 pattern (source pattern 2, after phase 1): -1e3 N UZ at 19.

    No loadConst exists in the source; phase 1 carries zero load anyway.
    """
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    ops.load(NODE_MONITOR, 0.0, 0.0, P_NODE_PUSH, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB") -> bool:
    """Phase 1 -- single LoadControl step on the zero-load pattern (§3c).

    Manual ``ops.analyze(1)`` loop (SmartAnalyze forces DisplacementControl).
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0)
    ops.analysis("Static")

    history: list[tuple[float, float, float, float]] = []
    ok = ops.analyze(1)
    if ok == 0:
        odb.fetch_response_step()
        ops.reactions()
        history.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_MONITOR, 1)),
            float(ops.nodeDisp(NODE_MONITOR, 2)),
            float(ops.nodeDisp(NODE_MONITOR, 3)),
        ))
    else:
        print(f"  WARNING: gravity step failed (ok={ok})")
    ops.wipeAnalysis()
    run_gravity.history = history  # type: ignore[attr-defined]
    return ok == 0


def run_pushdown(odb: "opst.post.CreateODB") -> bool:
    """Phase 2 -- UZ pushdown: DisplacementControl 19/3, -1.0 mm x 360.

    SmartAnalyze static with one increment per reference step
    (static_split([incr], maxStep=|incr]), §12am cadence).  In-loop
    history (load factor via getTime, node-19 UX/UY/UZ) every step.
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
                node=NODE_MONITOR, dof=CTRL_DOF, seg=seg)
            if ok < 0:
                step_ok = False
                break
            odb.fetch_response_step()
        if not step_ok:
            print(f"  WARNING: pushdown step {i} failed (ok={ok})")
            break
        ops.reactions()
        history.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_MONITOR, 1)),
            float(ops.nodeDisp(NODE_MONITOR, 2)),
            float(ops.nodeDisp(NODE_MONITOR, 3)),
        ))
        if (i + 1) % 120 == 0:
            print(f"  ... pushdown step {i + 1}/{N_PUSH_STEPS}, "
                  f"UZ={history[-1][3]:.1f} mm", flush=True)
    analysis.close()
    run_pushdown.history = history  # type: ignore[attr-defined]
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run zero-load gravity + pushdown, return ODB + results.

    Returns:
        (odb, results) where results has keys: hist (4,N) sim
        [LF,UX,UY,UZ] history (1 gravity + 360 pushdown = 361, matching the
        reference layout of one row per analyze step), ref (4,M)
        reference from node19.out.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    # The source carries Chinese banner comments in GBK bytes -- decode
    # tolerantly (only ASCII numerics are parsed, so replacement is safe).
    src = TCL_FILE.read_text(encoding="gbk", errors="replace")

    init_model()
    define_materials()
    define_sections(src)
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_disp, n_elastic = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_disp} dispBeamColumn + {n_elastic} "
          f"elasticBeamColumn (expected 23 + 12).", flush=True)

    odb = create_odb(output_dir)

    # Phase 1: zero-load gravity.
    define_gravity_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running gravity analysis...", flush=True)
    run_gravity(odb)

    # Phase 2: pushdown (no loadConst in source; phase 1 is load-free).
    define_pushdown_loads()
    print("Running pushdown analysis...", flush=True)
    run_pushdown(odb)

    # Reference node-19 history (col0=lambda, col1=UX, col2=UY, col3=UZ).
    ref = None
    if REF_FILE.exists():
        ref = np.loadtxt(str(REF_FILE)).T  # (4, M) -> [LF, UX, UY, UZ]

    ghist = np.array(getattr(run_gravity, "history", []),
                     dtype=float).T  # (4,<=1)
    phist = np.array(getattr(run_pushdown, "history", []),
                     dtype=float).T  # (4,<=360)
    parts = []
    if ghist.size:
        parts.append(ghist)
    if phist.size:
        parts.append(phist)
    hist = np.concatenate(parts, axis=1)
    results = {"hist": hist, "ref": ref}
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot node-19 history, verify.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis (hist/ref arrays).
    """
    odb.save_response()

    hist = results["hist"]
    ref = results["ref"]

    # Dump the full node-19 history for the record.
    if hist is not None and hist.shape[1] > 0:
        step = np.arange(hist.shape[1])
        curve = np.column_stack([step, hist.T])  # (N,5): idx, LF, UX, UY, UZ
        np.savetxt(str(output_dir / "node19_disp_history.csv"), curve,
                   delimiter=",", header="idx,lf,ux_mm,uy_mm,uz_mm")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))

        # V5 -- final deformed shape (pushdown is vertical -> UZ)
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=1, resp_dof="UZ", scale=10.0)
        # V6 -- step slider
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=1, resp_dof="UZ", scale=10.0)
        # V7 -- animation
        vis_anim(output_dir, filename="vis_07_animation.html",
                 odb_tag=1, defo_scale=10.0,
                 resp_dof=("UX", "UY", "UZ"))

    # Node-19 UZ-vs-load-factor: simulation vs reference (matplotlib)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        if ref is not None and ref.shape[1] > 0:
            ax1.plot(ref[3], ref[0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node19.out)")
        if hist is not None and hist.shape[1] > 0:
            ax1.plot(hist[3], hist[0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax1.set_xlabel(f"Node {NODE_MONITOR} UZ displacement (mm)")
        ax1.set_ylabel("Load factor")
        ax1.set_title("Dino_PrestressedBeam -- capacity (UZ vs LF)")
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        if ref is not None and ref.shape[1] > 0:
            ax2.plot(np.arange(ref.shape[1]), ref[0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node19.out)")
        if hist is not None and hist.shape[1] > 0:
            ax2.plot(np.arange(hist.shape[1]), hist[0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax2.set_xlabel("Recorded step (1 + 1 + 360)")
        ax2.set_ylabel("Load factor")
        ax2.set_title("Dino_PrestressedBeam -- load factor history")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "pushdown_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable -- skipping compare plot)")

    # Verification summary
    n_sim = hist.shape[1] if hist is not None else 0
    n_ref = ref.shape[1] if ref is not None else 0
    print(f"\n  Recorded steps: {n_sim} / {n_ref} expected", flush=True)
    if hist is not None and n_sim > 0:
        labels = ("LF", "UX", "UY", "UZ")
        for d in range(4):
            print(f"  Sim node{NODE_MONITOR} {labels[d]} final = "
                  f"{float(hist[d, -1]):.5f}", flush=True)
        if ref is not None and n_ref > 0:
            n = min(n_sim, n_ref)
            for d in range(4):
                sv, rv = hist[d, :n], ref[d, :n]
                rms = float(np.sqrt(np.mean((sv - rv) ** 2)))
                denom = np.maximum(np.abs(rv), 1e-12)
                rel = float(np.mean(np.abs(sv - rv) / denom) * 100.0)
                print(f"    {labels[d]}: per-point RMS {rms:.5f} | "
                      f"mean rel error {rel:.4f}%", flush=True)


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_PrestressedBeam: analysis complete.")
