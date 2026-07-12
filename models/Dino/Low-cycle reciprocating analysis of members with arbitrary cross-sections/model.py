# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Low-Cycle Reciprocating (Cyclic) Analysis of a Member with an
           Arbitrary (Irregular) Reinforced-Concrete Cross-Section
UniqueID : Dino_LowCycle
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-12
Purpose  : Cyclic lateral loading of a 3 m cantilever RC column whose section
           is an irregular (re-entrant) polygon meshed with 894 concrete +
           17 rebar fibers.  A gravity axial load is applied first, then a
           10-cycle DisplacementControl protocol drives the top node UX to
           +/- 5, 10, ..., 25 mm, producing the base-shear-vs-drift hysteresis.
Ref      : Dino -- Low-cycle reciprocating analysis of members with arbitrary
           cross-sections (original co.tcl + section_fiber.tcl)
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
# Materials (match source co.tcl tags exactly)
MAT_CONCRETE = 1     # Concrete01 (core + cover concrete)
MAT_STEEL    = 3     # Steel01   (longitudinal rebar)
MAT_DEAD2    = 2     # Elastic 1.999e5  (defined in source, unused -- kept verbatim)
MAT_VY       = 201   # Elastic 2.155e15 -> Aggregator Vy
MAT_VZ       = 301   # Elastic 2.155e15 -> Aggregator Vz
MAT_T        = 401   # Elastic 9.103e15 -> Aggregator T

# Sections
SEC_FIBER    = 1     # Fiber section (894 concrete + 17 rebar fibers)
SEC_AGG      = 1001  # Aggregator wrapping SEC_FIBER (+ rigid Vy/Vz/T)
BEAM_INT_TAG = 1001  # beamIntegration tag (reuses the aggregator section tag space)

# Nodes (match source tags)
NODE_BASE = 1        # fully fixed base
NODE_TOP  = 100      # loaded top node (control node, DOF 1 = UX)
NODE_LIST = [1, 2, 3, 4, 5, 100]
# element connectivity: (eleTag, iNode, jNode, transfTag)
ELEM_CONN = [(1, 1, 2, 1), (2, 2, 3, 2), (3, 3, 4, 3), (4, 4, 5, 4), (5, 5, 100, 5)]

# Time series / patterns
TS_GRAVITY   = 1
TS_LATERAL   = 2
PAT_GRAVITY  = 1
PAT_LATERAL  = 2

# ODB
ODB_TAG = 1

# Reference fibre file (verbatim replay source)
FIBER_FILE = Path(__file__).parent / "tcl_ref" / "section_fiber.tcl"
REF_FILE   = Path(__file__).parent / "tcl_ref" / "node2.out"
XLSX_FILE  = Path(__file__).parent / "tcl_ref" / "section_analysis.xlsx"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N).

# Geometry -- 6 nodes at x=y=6000, z = 0,600,1200,1800,2400,3000
X_NODE = 6000.0 * mm
Y_NODE = 6000.0 * mm
Z_COORDS = [0.0, 600.0, 1200.0, 1800.0, 2400.0, 3000.0]   # nodes 1..5,100
H_COL    = 3000.0 * mm                                    # column height
N_IP     = 3                                              # Lobatto integration pts (source)

# Materials (source co.tcl lines 17-24)
FC      = -26.8   * MPa    # Concrete01 peak compressive strength
EPSC0   = -0.002           # Concrete01 strain at peak
FCU     = -15.0   * MPa    # Concrete01 crushing strength
EPSCU   = -0.008           # Concrete01 crushing strain
FY      = 400.0   * MPa    # Steel01 yield strength
ES      = 200000.0 * MPa   # Steel01 elastic modulus
B_HARD  = 0.001            # Steel01 strain-hardening ratio

# Aggregator shear/torsion stiffness (effectively rigid in shear + torsion)
K_VY = 2.155e15   # N  (force-deformation, Vy)
K_VZ = 2.155e15   # N  (force-deformation, Vz)
K_T  = 9.103e15   # N.mm/rad (T)

# Loading
P_GRAVITY     = -19125000.0 * N   # axial compression at top node (DOF 3 = UZ)
P_LATERAL_REF = 1.0e5 * N         # unit reference lateral load at top node (DOF 1 = UX)

# Gravity analysis
N_GRAV_STEPS    = 10              # source: integrator LoadControl 0.1; analyze 10
GRAV_LAMBDA_STEP = 1.0 / N_GRAV_STEPS

# Cyclic protocol -- source co.tcl lines 82-99.
# Each cycle i imposes `kdisps[i] * 0.5` mm per step, for 100 steps.
# kdisps = {0.1,-0.2,...,1.0}  =>  step increments (mm):
CYCLE_INCR = [0.05, -0.10, 0.15, -0.20, 0.25, -0.30, 0.35, -0.40, 0.45, -0.50]
N_STEPS_PER_CYCLE = 100
N_CYCLES   = len(CYCLE_INCR)                            # 10 cycles
N_TOTAL    = N_CYCLES * N_STEPS_PER_CYCLE               # 1000 steps (matches node2.out)

# SmartAnalyze sub-step cap (largest single fixed increment in the protocol)
MAX_STEP = max(abs(c) for c in CYCLE_INCR)              # 0.5 mm

# Drift reference (for reporting)
DRIFT_REF = H_COL                                       # top drift / H_COL


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Define the source's uniaxialMaterials verbatim.

    Concrete01 (1) + Steel01 (3) form the fibre-section stress-strain laws.
    Elastic materials 201/301/401 supply the (rigid) shear-Vy / shear-Vz /
    torsion-T DOFs to the section Aggregator; tag 2 is defined in the source
    but never referenced (kept here for 1:1 fidelity; it is harmless).
    """
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE, FC, EPSC0, FCU, EPSCU)
    ops.uniaxialMaterial("Steel01", MAT_STEEL, FY, ES, B_HARD)
    ops.uniaxialMaterial("Elastic", MAT_DEAD2, 1.999e5)
    ops.uniaxialMaterial("Elastic", MAT_VY, K_VY)
    ops.uniaxialMaterial("Elastic", MAT_VZ, K_VZ)
    ops.uniaxialMaterial("Elastic", MAT_T, K_T)


# ── 6. SECTION (verbatim fibre replay) ───────────────────────────────────────
def _parse_fiber_file(path: Path) -> list[tuple[float, float, float, int]]:
    """Parse the source ``section_fiber.tcl`` into a list of fibre tuples.

    Each fibre line is ``fiber  <y>  <z>  <area>  <matTag>`` (Tcl OpenSees
    section-local convention: first coord = section y, second = section z).
    Returns ``[(y, z, area, matTag), ...]`` -- 894 concrete (mat 1) + 17
    rebar (mat 3) = 911 fibres for the reference file.
    """
    pat = re.compile(
        r"^\s*fiber\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+(\d+)\s*$"
    )
    fibers: list[tuple[float, float, float, int]] = []
    with open(path) as f:
        for line in f:
            m = pat.match(line)
            if m:
                fibers.append(
                    (float(m.group(1)), float(m.group(2)),
                     float(m.group(3)), int(m.group(4)))
                )
    return fibers


def _section_torsional_stiffness(fibers: list[tuple[float, float, float, int]]) -> float:
    """Estimate a GJ for the inner Fiber section.

    The source Tcl omits ``-GJ`` (Tcl only warns; OpenSeesPy *requires* it for
    a 3D Fiber section -- AGENT.md §12au).  The Aggregator's mat-401 torsion
    dominates the section response regardless, so the inner GJ is a
    formality; we compute a principled value from the concrete Young's
    modulus (|fc|/eps0 ~ Ec) and the fibre polar second moment of area so the
    value is physically defensible rather than an arbitrary placeholder.
    """
    # Concrete Young's modulus (secant to peak): Ec = |fc| / |eps0|
    Ec = abs(FC / EPSC0)                       # ~13400 MPa
    nu = 0.2                                   # concrete Poisson's ratio
    G = Ec / (2.0 * (1.0 + nu))                # shear modulus
    # Polar second moment of area about the section centroid (fibres are
    # centroided at 0,0 by the source mesher).
    J = 0.0
    for (y, z, area, _mat) in fibers:
        J += area * (y * y + z * z)
    return G * J


def define_section(fiber_file: Path = FIBER_FILE) -> None:
    """Build the fibre section by verbatim replay of the source fibre file.

    Re-meshing an irregular (re-entrant) section risks both A/I drift
    (AGENT.md §12aq) and getting the outline geometry wrong; replaying the
    source's 911 fibres guarantees identical section properties.  A 3D Fiber
    section in OpenSeesPy requires an explicit ``-GJ`` (Tcl only warns); we
    supply a principled value (the Aggregator's mat-401 dominates torsion
    anyway).
    """
    fibers = _parse_fiber_file(fiber_file)
    if not fibers:
        raise RuntimeError(f"No fibres parsed from {fiber_file}")

    n_conc = sum(1 for f in fibers if f[3] == MAT_CONCRETE)
    n_rebar = sum(1 for f in fibers if f[3] == MAT_STEEL)
    a_conc = sum(f[2] for f in fibers if f[3] == MAT_CONCRETE)
    print(f"  Fibre section: {n_conc} concrete + {n_rebar} rebar fibres "
          f"(A_conc = {a_conc:.0f} mm^2)")

    GJ = _section_torsional_stiffness(fibers)
    ops.section("Fiber", SEC_FIBER, "-GJ", GJ)
    for (y, z, area, mat) in fibers:
        ops.fiber(y, z, area, mat)

    # Aggregator adds the rigid shear (Vy, Vz) and torsion (T) DOFs.
    ops.section("Aggregator", SEC_AGG,
                MAT_VY, "Vy", MAT_VZ, "Vz", MAT_T, "T",
                "-section", SEC_FIBER)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Create the 6 column nodes along z at x=y=6000 (source co.tcl lines 5-10)."""
    for tag, z in zip(NODE_LIST, Z_COORDS):
        ops.node(tag, X_NODE, Y_NODE, z)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix the base node fully; the top node keeps only UY fixed (source lines 13-14)."""
    ops.fix(NODE_BASE, 1, 1, 1, 1, 1, 1)   # node 1 fully fixed
    ops.fix(NODE_TOP, 0, 1, 0, 0, 0, 0)    # node 100: UY fixed only


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Create 5 dispBeamColumn elements via beamIntegration (source lines 34-44).

    OpenSeesPy ``dispBeamColumn`` takes a ``beamIntegration`` object, NOT the
    Tcl-style ``(tag, i, j, nIP, secTag, transfTag)`` 6-arg form (AGENT.md
    §12l).  Lobatto with 3 IP and the aggregator section matches the source.
    """
    for (tag, _i, _j, transf) in ELEM_CONN:
        ops.geomTransf("Linear", transf, 1.0, 0.0, 0.0)
    ops.beamIntegration("Lobatto", BEAM_INT_TAG, SEC_AGG, N_IP)
    for (tag, iN, jN, transf) in ELEM_CONN:
        ops.element("dispBeamColumn", tag, iN, jN, transf, BEAM_INT_TAG)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a fibre-section beam-column model.

    ``save_frame_resp=False`` -- fibre-section dispBeamColumn internal
    sections lack user-visible tags, which conflicts with opstool's beam-force
    extractor (AGENT.md §12v-1).  ``set_odb_path`` MUST precede ``CreateODB``
    (§12ac).
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Axial compression at the top node (pattern 1).  Run BEFORE loadConst."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    ops.load(NODE_TOP, 0.0, 0.0, P_GRAVITY, 0.0, 0.0, 0.0)


def define_lateral_loads() -> None:
    """Unit reference lateral load at the top node (pattern 2).

    MUST be called AFTER ``loadConst`` (AGENT.md §12z-1) -- a DisplacementControl
    pattern frozen at lambda=0 yields an infinite load factor at step 0.
    """
    ops.timeSeries("Linear", TS_LATERAL)
    ops.pattern("Plain", PAT_LATERAL, TS_LATERAL)
    ops.load(NODE_TOP, P_LATERAL_REF, 0.0, 0.0, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB") -> bool:
    """Apply gravity via a manual LoadControl loop (§3c permitted exception).

    SmartAnalyze forces a DisplacementControl integrator, so LoadControl
    gravity is run as a manual ``ops.analyze(1)`` loop.  KrylovNewton +
    BandGeneral + Transformation constraints + NormDispIncr 1e-5; 10 steps to
    lambda=1.0, then ``loadConst`` + ``wipeAnalysis``.
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-5, 200)
    ops.algorithm("KrylovNewton")
    ops.integrator("LoadControl", GRAV_LAMBDA_STEP)
    ops.analysis("Static")

    ok = 0
    for step in range(N_GRAV_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            # Fallback: ModifiedNewton + relaxed tolerance (§12x-style ladder)
            ops.test("NormDispIncr", 1.0e-4, 200)
            ops.algorithm("ModifiedNewton")
            ok = ops.analyze(1)
            ops.test("NormDispIncr", 1.0e-5, 200)
            ops.algorithm("KrylovNewton")
            if ok != 0:
                print(f"  WARNING: gravity step {step} failed (ok={ok})")
                break
        odb.fetch_response_step()

    lf = ops.getTime()
    print(f"  Gravity converged to lambda={lf:.4f} (target 1.0)")
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()
    return ok == 0


def run_cyclic(odb: "opst.post.CreateODB") -> tuple[list[float], list[float]]:
    """Run the 10-cycle DisplacementControl protocol via SmartAnalyze.

    Per AGENT.md §12am, a faithful 1:1 port of a fixed-increment cyclic
    protocol stalls mid-protocol; SmartAnalyze with adaptive sub-stepping +
    relaxation tracks the softening/unloading branches.  To keep the recorder
    aligned 1:1 with the 1000-point reference, each cycle's full displacement
    is fed as ONE target to ``static_split`` with ``maxStep`` equal to that
    cycle's fixed increment -- so the step count matches the source (100 per
    cycle, 1000 total) while still allowing SmartAnalyze to sub-step within
    each fixed increment on convergence trouble.

    Returns:
        (shear_kN, disp_mm) lists at every converged sub-step.  Base shear =
        lateral load-factor lambda x P_LATERAL_REF (source recorder convention:
        ``recorder -time`` col 0 is the lateral pattern lambda, NOT force).
    """
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="NormDispIncr",
        testTol=1.0e-5,
        testIterTimes=200,
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30],      # KrylovNewton, Newton, ModifiedNewton, NewtonLineSearch
        tryLooseTestTol=True,
        looseTestTolTo=1.0e-4,
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100, 500],
        relaxation=0.5,
        minStep=1.0e-3,
    )

    shear_hist: list[float] = []
    disp_hist: list[float] = []
    n_done = 0

    for icycle, incr in enumerate(CYCLE_INCR):
        # Displacement CHANGE this cycle = incr x N_STEPS_PER_CYCLE (e.g. cycle 2
        # goes from +5 mm back to -5 mm, a delta of -10 mm).  static_split takes
        # this as the increment from the CURRENT position (NOT the cumulative
        # absolute destination); with maxStep = |incr| it yields exactly 100
        # segments per cycle, keeping the recorder 1:1 with the 1000-row source.
        cycle_delta = incr * N_STEPS_PER_CYCLE
        segs = analysis.static_split([cycle_delta], maxStep=abs(incr))
        for seg in segs:
            rc = analysis.StaticAnalyze(node=NODE_TOP, dof=1, seg=seg)
            if rc < 0:
                print(f"  WARNING: cycle {icycle + 1} failed mid-segment at "
                      f"incr={incr} (rc={rc})")
                break
            odb.fetch_response_step()
            lam = ops.getTime()                       # lateral pattern load-factor
            ux = ops.nodeDisp(NODE_TOP, 1)            # imposed top UX (mm)
            shear_hist.append(lam * P_LATERAL_REF / 1.0e3)   # kN
            disp_hist.append(ux)
            n_done += 1

    analysis.close()
    print(f"  Cyclic: converged {n_done}/{N_TOTAL} steps "
          f"(peak disp {max(abs(d) for d in disp_hist) if disp_hist else 0:.2f} mm).")
    return shear_hist, disp_hist


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build the model, run gravity + cyclic, return ODB + results.

    Args:
        output_dir: Directory for ODB + visualisations.

    Returns:
        (odb, results) where results has keys: shear (kN), disp (mm),
        ref_shear (kN), ref_disp (mm).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    init_model()
    define_materials()
    define_section(FIBER_FILE)
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)

    odb = create_odb(output_dir)

    # Phase 1: gravity (before loadConst)
    define_gravity_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running gravity analysis...")
    run_gravity(odb)

    # Phase 2: lateral pattern AFTER loadConst (§12z-1), then cyclic push.
    define_lateral_loads()
    print("Running cyclic protocol...")
    shear_hist, disp_hist = run_cyclic(odb)

    # Reference hysteresis (node2.out: col0=lambda, col1=UX disp mm)
    ref_shear = ref_disp = None
    if REF_FILE.exists():
        raw = np.loadtxt(str(REF_FILE))
        ref_shear = raw[:, 0] * P_LATERAL_REF / 1.0e3     # kN (lambda x 100 kN)
        ref_disp = raw[:, 1]                               # mm

    results = {
        "shear": np.array(shear_hist),
        "disp": np.array(disp_hist),
        "ref_shear": ref_shear,
        "ref_disp": ref_disp,
    }

    # Persist the simulation curve
    if len(shear_hist) > 0:
        curve = np.column_stack([results["shear"], results["disp"]])
        np.savetxt(str(output_dir / "hysteresis_curve.csv"), curve,
                   delimiter=",", header="shear_kN,disp_mm")

    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def _load_pmm(xlsx_path: Path):
    """Load the P-M interaction surface from the xlsx 'PMM' sheet.

    Reads the .xlsx (a zip of XML) with the stdlib alone -- ``openpyxl`` /
    ``pandas.read_excel`` are not available in the opensy env and adding a
    dependency for a secondary section-capacity plot is unwarranted.  The PMM
    sheet is columns B (P) and C (M), 62 numeric rows, already in **kN** and
    **kN.m** respectively (verified: P ranges -3336..32941 kN, M ranges
    -4764..4861 kN.m -- consistent with the 1.1e6 mm^2 section and its 19 125 kN
    gravity demand, which sits inside the surface).

    Returns (P_kN, M_kNm) arrays, or (None, None) if unavailable.
    """
    if not xlsx_path.exists():
        return None, None
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        z = zipfile.ZipFile(str(xlsx_path))
        tree = ET.fromstring(z.read("xl/worksheets/sheet2.xml"))
        P_list, M_list = [], []
        for row in tree.iter(f"{ns}row"):
            cells = {}
            for c in row.iter(f"{ns}c"):
                ref = c.get("r", "")
                col = re.match(r"([A-Z]+)", ref)
                v = c.find(f"{ns}v")
                if col is not None and v is not None and v.text is not None:
                    cells[col.group(1)] = float(v.text)
            if "B" in cells and "C" in cells:
                P_list.append(cells["B"])     # already kN
                M_list.append(cells["C"])     # already kN.m
        if not P_list:
            return None, None
        return np.array(P_list), np.array(M_list)
    except Exception as exc:
        print(f"  (could not read PMM sheet: {exc})")
        return None, None


def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot hysteresis + PMM surface.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from ``run_analysis``.
    """
    odb.save_response()

    if not _headless():
        opst.post.set_odb_path(str(output_dir))

        # V5 -- peak deformed shape (absMax step, UX)
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UX", scale=10.0)

        # V6 -- step slider
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UX", scale=10.0)

        # V7 -- animation
        vis_anim(output_dir, filename="vis_07_animation.html",
                 odb_tag=ODB_TAG, defo_scale=10.0,
                 resp_dof=("UX", "UY", "UZ"))

    # Hysteresis: simulation vs reference (matplotlib, plot_utils style)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 1, figsize=(7, 5))
        if results["ref_shear"] is not None:
            ax.plot(results["ref_disp"], results["ref_shear"], "k-",
                    linewidth=1.0, alpha=0.6, label="Reference (node2.out)")
        if len(results["disp"]) > 0:
            ax.plot(results["disp"], results["shear"], "r--",
                    linewidth=1.2, alpha=0.85, label="Simulation")
        ax.set_xlabel("Top UX displacement (mm)")
        ax.set_ylabel("Base shear (kN)")
        ax.set_title("Dino_LowCycle -- cyclic hysteresis "
                     "(arbitrary RC cross-section)")
        ax.axhline(0.0, color="0.6", linewidth=0.5)
        ax.axvline(0.0, color="0.6", linewidth=0.5)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "hysteresis_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable -- skipping hysteresis plot)")

    # PMM interaction surface (secondary, section-capacity context)
    P, M = _load_pmm(XLSX_FILE)
    if P is not None:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(1, 1, figsize=(6, 5))
            ax.plot(P, M, "b-", linewidth=1.2, label="P-M surface")
            # Gravity demand point (axial only, M~0 at zero lateral)
            ax.plot([P_GRAVITY / 1.0e3], [0.0], "rx",
                    markersize=8, label=f"Gravity demand "
                    f"({P_GRAVITY / 1.0e3:.0f} kN)")
            ax.set_xlabel("Axial force P (kN)")
            ax.set_ylabel("Moment M (kN.m)")
            ax.set_title("Dino_LowCycle -- section P-M interaction "
                         "(from section_analysis.xlsx)")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            fig.savefig(str(output_dir / "pmm_surface.png"), dpi=150)
            plt.close(fig)
        except ImportError:
            print("  (matplotlib unavailable -- skipping PMM plot)")

    # Verification summary
    sim_shear = results["shear"]
    ref_shear = results["ref_shear"] if results["ref_shear"] is not None else None
    if len(sim_shear) > 0:
        sim_peak_pos = float(np.max(sim_shear))
        sim_peak_neg = float(np.min(sim_shear))
        print(f"\n  Sim: peak shear +{sim_peak_pos:.1f} / {sim_peak_neg:.1f} kN "
              f"| peak disp {float(np.max(np.abs(results['disp']))):.2f} mm "
              f"| steps {len(sim_shear)}/{N_TOTAL}")
        if ref_shear is not None and len(ref_shear) > 0:
            ref_peak_pos = float(np.max(ref_shear))
            ref_peak_neg = float(np.min(ref_shear))
            print(f"  Ref: peak shear +{ref_peak_pos:.1f} / {ref_peak_neg:.1f} kN")
            denom = max(abs(ref_peak_pos), abs(ref_peak_neg))
            if denom > 0:
                dpos = 100.0 * abs(sim_peak_pos - ref_peak_pos) / denom
                dneg = 100.0 * abs(sim_peak_neg - ref_peak_neg) / denom
                print(f"  Peak-shear diff: +{dpos:.1f}% / {dneg:.1f}%")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_LowCycle: analysis complete.")
