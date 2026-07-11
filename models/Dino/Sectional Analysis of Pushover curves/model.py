# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : RC Column Sectional Pushover (fiber-section cantilever)
UniqueID : Dino
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-11
Purpose  : Gravity + displacement-controlled pushover of a 3D RC cantilever
           column with a fiber section (Concrete01 concrete + Steel01 rebar).
Ref      : Dino — Sectional Analysis of Pushover curves (original column_sec.py)
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
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
# Materials
MAT_CONCRETE = 1     # Concrete01 (unconfined)
MAT_STEEL    = 5     # Steel01 (rebar)

# Section
SEC_FIBER    = 1     # Fiber section (concrete + rebar)

# Geometric transformation
TRANS_COL    = 1     # Linear geomTransf, vecxZ = (1, 0, 0)

# Nodes
NODE_BASE    = 1     # fixed base
NODE_TOP     = 2     # loaded top (free UX)

# Elements
ELE_COL      = 1     # nonlinearBeamColumn

# Load patterns / time series
TS_GRAVITY   = 1
TS_LATERAL   = 2
PAT_GRAVITY  = 1
PAT_LATERAL  = 2

# ODB
ODB_TAG      = 1

# Analysis
N_GRAV_STEPS = 10


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# All values already in N-mm-MPa (source is SI-consistent).
# Geometry
COL_LEN   = 1000.0          # mm — column length
B_SEC     = 1200.0           # mm — section width  (local y)
H_SEC     = 800.0            # mm — section height (local z)
COVER     = 50.0             # mm — clear cover to rebar centroid

# Rebar layout
NX_BAR    = 8                # bars along the top/bottom rows (local y dir)
NY_BAR    = 6                # bars along the side rows (local z dir)
DX_BAR    = 40.0             # mm — bar diameter (top/bottom rows)
DY_BAR    = 40.0             # mm — bar diameter (side rows)

# Material (Concrete01: fcu, eps0, fcu, epsU — all negative for compression)
CONC_FCU   = -26.8            # MPa — concrete compressive strength
CONC_EPS0  = -0.00214         # —    — strain at peak
CONC_FCUU  = -26.8            # MPa — crushing stress
CONC_EPSU  = -0.01            # —    — crushing strain
STEEL_FY   = 435.0            # MPa — steel yield
STEEL_E    = 205000.0         # MPa — steel elastic modulus
STEEL_B    = 0.0001           # —    — strain-hardening ratio

# Fiber-section discretisation (replaces source pygmsh triangle mesh)
N_PATCH_Y  = 20               # concrete patch divisions along local y (width)
N_PATCH_Z  = 20               # concrete patch divisions along local z (height)
SEC_GJ     = 200.0            # N·mm² — torsional stiffness (source value)

# nonlinearBeamColumn integration
N_IP       = 2                # integration points

# Loading
P_GRAVITY  = -15000e3         # N — axial compression at top node (DOF 3, UZ)
P_LATERAL  = 1000.0           # N — lateral reference load at top node (DOF 1, UX)

# Pushover analysis
DISP_MAX   = 8.0              # mm — target top displacement
N_PUSH_STEPS = 100            # displacement-controlled steps
MAX_STEP   = DISP_MAX / N_PUSH_STEPS   # mm — max increment


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Define Concrete01 and Steel01 uniaxial materials + geometric transform.

    Values are ported verbatim from the source (already N-mm-MPa).  The source's
    dead ``Elastic`` material tag 200 (1e12 stiffness, never referenced) is
    omitted — it served no structural purpose.
    """
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE,
                         CONC_FCU, CONC_EPS0, CONC_FCUU, CONC_EPSU)
    ops.uniaxialMaterial("Steel01", MAT_STEEL,
                         STEEL_FY, STEEL_E, STEEL_B)

    # Geometric transformation (Linear, local-z = global-Z)
    ops.geomTransf("Linear", TRANS_COL, 1.0, 0.0, 0.0)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    """Build the fiber section (rectangular concrete patch + rebar layers).

    The source used pygmsh to triangulate the 1200×800 concrete area into 244
    triangle fibers.  pygmsh is not available in the opensy env; the standard
    repo approach uses ``ops.patch("rect", ...)`` with a 20×20 grid (400 fibers
    — comparable resolution).  Rebar layers (``ops.layer("straight")``) are
    preserved exactly: same bar counts (8+8+6+6), diameter (40 mm), and
    perimeter layout.
    """
    ops.section("Fiber", SEC_FIBER, "-GJ", SEC_GJ)

    # Concrete patch: full rectangle centred at origin
    #   y ∈ [-B/2, B/2], z ∈ [-H/2, H/2]
    ops.patch("rect", MAT_CONCRETE, N_PATCH_Y, N_PATCH_Z,
              -B_SEC / 2.0, -H_SEC / 2.0, B_SEC / 2.0, H_SEC / 2.0)

    # Rebar layers — area per bar
    asx = np.pi * DX_BAR ** 2 / 4.0      # top/bottom row bar area
    asy = np.pi * DY_BAR ** 2 / 4.0      # side row bar area
    yc = H_SEC / 2.0 - COVER             # ±350 mm (rebar y-coordinate)
    zc = B_SEC / 2.0 - COVER             # ±550 mm (rebar z-coordinate)
    divy = (B_SEC - 2.0 * COVER) / (NY_BAR + 1)
    zs = zc - divy                       # ±392.86 mm (side row inner z)

    # Top row (z = +zc, 8 bars along y)
    ops.layer("straight", MAT_STEEL, NX_BAR, asx, -yc,  zc,  yc,  zc)
    # Bottom row (z = -zc, 8 bars along y)
    ops.layer("straight", MAT_STEEL, NX_BAR, asx, -yc, -zc,  yc, -zc)
    # Right side (y = +yc, 6 bars along z)
    ops.layer("straight", MAT_STEEL, NY_BAR, asy,  yc, -zs,  yc,  zs)
    # Left side (y = -yc, 6 bars along z)
    ops.layer("straight", MAT_STEEL, NY_BAR, asy, -yc, -zs, -yc,  zs)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Define base (fixed) and top (loaded) nodes along the Z axis."""
    ops.node(NODE_BASE, 0.0, 0.0, 0.0)
    ops.node(NODE_TOP,  0.0, 0.0, COL_LEN)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix the base fully; free UX/UZ and rotations at top except UY/RX/RZ.

    Source fixities (column_sec.py:127-128):
      Node 1: fix 1 1 1 1 1 1  (fully fixed)
      Node 2: fix 0 1 0 1 0 1  (UX free, UY fixed, UZ free, RX fixed, RY free, RZ fixed)
    This allows pushover in UX + axial in UZ while restraining out-of-plane.
    """
    ops.fix(NODE_BASE, 1, 1, 1, 1, 1, 1)
    ops.fix(NODE_TOP,  0, 1, 0, 1, 0, 1)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Create the nonlinearBeamColumn (flexibility-based, 2 IPs)."""
    ops.element("nonlinearBeamColumn", ELE_COL,
                NODE_BASE, NODE_TOP, N_IP, SEC_FIBER, TRANS_COL)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(odb_tag: int, output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB after the model is built.

    ``save_frame_resp=False`` — nonlinearBeamColumn (like forceBeamColumn) uses
    internal sections without user-visible tags; enabling frame response saving
    raises ``sectionForceDeformation(tag=0) not found`` (§12v).

    Args:
        odb_tag: ODB tag identifier.
        output_dir: Directory for ODB files.

    Returns:
        The initialised CreateODB instance.
    """
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Apply axial compression at the top node (UZ direction)."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    ops.load(NODE_TOP, 0.0, 0.0, P_GRAVITY, 0.0, 0.0, 0.0)


def define_lateral_loads() -> None:
    """Apply unit lateral reference load at top node (UX direction).

    Called AFTER ``run_gravity`` so the pattern is not frozen by
    ``loadConst`` (§12z).
    """
    ops.timeSeries("Linear", TS_LATERAL)
    ops.pattern("Plain", PAT_LATERAL, TS_LATERAL)
    ops.load(NODE_TOP, P_LATERAL, 0.0, 0.0, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB") -> None:
    """Apply gravity axial load via manual LoadControl loop.

    Per AGENT.md §3c / §10, manual ``ops.analyze()`` is the permitted exception
    for LoadControl gravity (SmartAnalyze forces DisplacementControl).
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / N_GRAV_STEPS)
    ops.analysis("Static")

    for step in range(N_GRAV_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"  WARNING: gravity step {step + 1} failed (ok={ok})")
            break
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def run_pushover(
    odb: "opst.post.CreateODB",
    ctrl_node: int = NODE_TOP,
    ctrl_dof: int = 1,
    target_disp: float = DISP_MAX,
    max_step: float = MAX_STEP,
) -> tuple[list[float], list[float]]:
    """Run displacement-controlled pushover using SmartAnalyze.

    SmartAnalyze manages constraints / numberer / system / test / algorithm
    internally.  Test tolerance relaxed to NormDispIncr @ 1e-5 with KrylovNewton
    primary (§12z settings for fiber-section RC).

    Args:
        odb: Active CreateODB instance.
        ctrl_node: Control node tag.
        ctrl_dof: Control DOF (1 = UX).
        target_disp: Target displacement in mm.
        max_step: Maximum displacement increment in mm.

    Returns:
        (base_shear [N], disp [mm]) lists at each converged step.  Base shear =
        lateral-pattern load factor × P_LATERAL.
    """
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
    )

    protocol = [target_disp]
    segs = analysis.static_split(protocol, maxStep=max_step)

    shear_hist: list[float] = []
    disp_hist: list[float] = []

    for seg in segs:
        rc = analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
        odb.fetch_response_step()
        if rc < 0:
            print(f"  WARNING: pushover segment failed (rc={rc})")
            break
        # Base shear = lateral load-factor × reference load.
        # For a Plain pattern with Linear TS, λ = pseudo-time t.  The load
        # factor scales the reference load P_LATERAL, so base shear = t × P_LATERAL.
        t = ops.getTime()
        shear_hist.append(t * P_LATERAL)
        disp_hist.append(ops.nodeDisp(ctrl_node, ctrl_dof))

    analysis.close()
    print(f"  Converged {len(shear_hist)}/{len(segs)} pushover steps.")
    return shear_hist, disp_hist


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run gravity + pushover, return ODB + results dict.

    Args:
        output_dir: Directory for ODB + HTML visualisations.

    Returns:
        (odb, results) where results has keys: shear, disp, ref_shear, ref_disp.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)

    odb = create_odb(ODB_TAG, output_dir)

    # Phase 1: Gravity (before loadConst)
    define_gravity_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    print("Running gravity analysis...")
    run_gravity(odb)

    # Phase 2: Lateral pushover (AFTER loadConst — §12z)
    define_lateral_loads()

    print("Running pushover...")
    shear_hist, disp_hist = run_pushover(odb)

    # Load reference pushover curve
    ref_path = Path(__file__).parent / "Sectional Analysis of Pushover curves" \
        / "py_ref" / "node_disp.out"
    if ref_path.exists():
        ref = np.loadtxt(str(ref_path))
        # node_disp.out was recorded with `recorder Node -time -dof 1 disp`, so
        # col 0 is the pseudo-time λ (= lateral load factor for the Plain pattern),
        # NOT base shear.  The source used a 1000 N reference load, so base shear
        # in N = λ × 1000.  Col 1 is the top UX displacement in mm.
        ref_shear = ref[:, 0] * P_LATERAL     # N  (λ × 1000 N reference load)
        ref_disp = ref[:, 1]                  # mm
    else:
        ref_shear = np.array([])
        ref_disp = np.array([])

    results = {
        "shear": np.array(shear_hist),
        "disp": np.array(disp_hist),
        "ref_shear": ref_shear,
        "ref_disp": ref_disp,
    }

    # Save pushover curve
    if len(shear_hist) > 0:
        curve = np.column_stack([results["shear"], results["disp"]])
        np.savetxt(str(output_dir / "pushover_curve.csv"), curve,
                   delimiter=",", header="base_shear_N,disp_mm")

    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render deformed-shape visualisations, plot pushover curve.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis.
    """
    odb.save_response()

    if not _headless():
        opst.post.set_odb_path(str(output_dir))

        # V5 — peak deformed shape (absMax step)
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UX", scale=50.0)

        # V6 — step slider
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UX", scale=50.0)

        # V7 — animation
        vis_anim(output_dir, filename="vis_07_animation.html",
                 odb_tag=ODB_TAG, defo_scale=50.0,
                 resp_dof=("UX", "UY", "UZ"))

        # Pushover curve: simulation vs reference (matplotlib)
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(1, 1, figsize=(7, 5))
            if len(results["ref_disp"]) > 0:
                ax.plot(results["ref_disp"], results["ref_shear"] / 1e3,
                        "k-", linewidth=1.2, alpha=0.7, label="Reference")
            if len(results["disp"]) > 0:
                ax.plot(results["disp"], results["shear"] / 1e3,
                        "r--", linewidth=1.2, alpha=0.8, label="Simulation")
            ax.set_xlabel("Top displacement (mm)")
            ax.set_ylabel("Base shear (kN)")
            ax.set_title("Dino — RC column pushover")
            ax.legend()
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            fig.savefig(str(output_dir / "pushover_compare.png"), dpi=150)
            plt.close(fig)
        except ImportError:
            print("  (matplotlib unavailable — skipping pushover plot)")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino: analysis complete.")
