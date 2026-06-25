# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 1-DOF Building with Tuned Mass Damper (Hybrid Simulation Specimen)
UniqueID : mosqueda
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-06-25
Purpose  : Transient dynamic analysis of a 3D SDOF building with a
           TripleFrictionPendulum TMD isolator under multi-support
           excitation. Numerical-only version of the original OpenFresco
           hybrid simulation model (expElmFact=0).
Ref      : Schellenberg, A. — NEEShybrid / mosqueda specimen
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
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Materials
MAT_KX          = 1   # building stiffness — X direction
MAT_KY          = 2   # building stiffness — Y direction
MAT_KZ         = 3   # building stiffness — Z direction
MAT_KVC        = 10  # TMD isolator vertical compression stiffness
MAT_KVT        = 11  # TMD isolator vertical tension stiffness

# Friction models
FRN_LOW        = 1   # low-velocity friction (mu=0.055)
FRN_MED        = 2   # medium-velocity friction (mu=0.13)
FRN_HIGH       = 3   # high-velocity friction (mu=0.13)

# Nodes
NODE_BASE      = 1   # fixed base (ground motion applied here)
NODE_BLDG      = 2   # building mass (SDOF)
NODE_TMD       = 3   # TMD mass

# Elements
ELE_BLDG       = 1   # twoNodeLink — building stiffness
ELE_TMD        = 2   # TripleFrictionPendulum — TMD isolator

# Load patterns
PAT_GRAVITY    = 1
PAT_GM         = 2

# Time series
TS_GRAV        = 1
TS_DISP        = 11
TS_VEL         = 12
TS_ACCEL       = 13

# Ground motion
GM_X           = 1

# Analysis
ODB_TAG        = 1
N_GRAV_STEPS   = 10

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# All converted from kip·in → N·mm. Base units: N, mm, s.

# Physical constants
g_accel = 9810.0                # mm/s²

# Building parameters (from Schellenberg Building1DOFwithTMD.tcl)
fx_bldg    = 4.0                # Hz — building X frequency
fy_bldg    = 1.25 * fx_bldg     # Hz — building Y frequency (5.0)
fz_bldg    = 11.0               # Hz — building Z frequency
m_ratio    = 0.88585            # —   effective mass ratio
h_ratio    = 0.64721            # —   effective height ratio

# Weight/mass (kip → N × 4448.22)
w_tmd      = 56.0   * 4448.22  # N   — TMD weight (249,100 N)
w_ratio_tmd = 56.0 / 450.0     # —   — TMD/building weight ratio (0.12444)
w_bldg     = w_tmd / w_ratio_tmd  # N — building weight (2,001,700 N)

m_bldg     = m_ratio * w_bldg / g_accel   # N·s²/mm — building mass (180.7)
m_tmd      = w_tmd / g_accel               # N·s²/mm — TMD mass (25.4)

# Building height (in → mm × 25.4)
h_tmd      = 6.0 * 25.4         # mm  — TMD height (152.4 mm)
h_bldg_raw = h_ratio * 5.0 * 144.0 / 3.0  # in — building height (155.33 in)
h_bldg     = h_bldg_raw * 25.4  # mm  — building height (3945 mm)

# Building stiffness (N/mm)
kx_bldg    = m_bldg * (2.0 * np.pi * fx_bldg)**2   # N/mm (114,140)
ky_bldg    = m_bldg * (2.0 * np.pi * fy_bldg)**2   # N/mm (178,400)
kz_bldg    = m_bldg * (2.0 * np.pi * fz_bldg)**2   # N/mm (863,000)

# Damping
zeta        = 0.05               # —    damping ratio (5%)

# Experimental element factor (0 = pure numerical)
exp_elm_fact = 0.0

# Isolator type: "FPSB" or "LPRB"
iso_type    = "FPSB"

# FPSB isolator parameters (in → mm × 25.4, kip → N × 4448.22)
# Friction coefficients (dimensionless)
mu1         = 0.055
mu2         = 0.13
mu3         = 0.13

# Pendulum radii
L1          = (3.0 - 1.65 / 2.0) * 25.4       # mm  (55.2 mm)
L2          = (18.64 - 2.94 / 2.0) * 25.4     # mm  (436.1 mm)
L3          = (18.64 - 2.94 / 2.0) * 25.4     # mm  (436.1 mm)

# Displacement limits
d1          = (2.60 - 1.75) / 2.0 * 25.4      # mm  (10.8 mm)
d2          = (9.0 - 3.0) / 2.0 * 25.4        # mm  (76.2 mm)
d3          = (9.0 - 3.0) / 2.0 * 25.4        # mm  (76.2 mm)

# Isolator vertical stiffnesses
w_iso       = (1.0 - exp_elm_fact) * w_tmd    # N   (249,100 N)
uy_iso      = 0.0047 * 25.4                    # mm  (0.119 mm)
kvc_iso     = (1.0 - exp_elm_fact) * 5.0e3 * 4448.22 / 25.4  # N/mm (875,650)
kvt_iso     = (1.0 - exp_elm_fact) * 0.001 * 4448.22 / 25.4  # N/mm (0.175)
min_fv      = 1.0e-6 * 4448.22                # N   (0.00445 N)
tol_iso     = 1.0e-6                           # —   convergence tolerance

# Ground motion — Sine excitation (0.5 Hz, 1.5x amplitude)
gm_freq     = 0.5                # Hz
gm_omega    = 2.0 * np.pi * gm_freq  # rad/s
gm_amp      = 1.5 * 25.4        # mm — displacement amplitude (38.1 mm)
gm_start    = 0.0                # s
gm_finish   = 30.0               # s
gm_period   = 1.0 / gm_freq     # s  (2.0 s)

# Transient analysis
N_PTS       = 8192
DT_GM       = 10.0 / 2048.0     # s — ≈ 0.00488 s

# Length scaling (physical specimen scale)
length_scale = 3.0
time_scale   = np.sqrt(length_scale)  # ≈ 1.732

# Gravity
g = g_accel


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    # Building stiffness — elastic springs (N/mm converted from kip/in)
    # kx = 114,140 N/mm, ky = 178,400 N/mm, kz = 863,000 N/mm
    ops.uniaxialMaterial("Elastic", MAT_KX, kx_bldg)
    ops.uniaxialMaterial("Elastic", MAT_KY, ky_bldg)
    ops.uniaxialMaterial("Elastic", MAT_KZ, kz_bldg)

    # Isolator vertical materials (N/mm)
    ops.uniaxialMaterial("Elastic", MAT_KVC, kvc_iso)   # compression stiffness
    ops.uniaxialMaterial("Elastic", MAT_KVT, kvt_iso)   # tension stiffness

    # Friction models (dimensionless coefficients)
    ops.frictionModel("Coulomb", FRN_LOW,  mu1)
    ops.frictionModel("Coulomb", FRN_MED,  mu2)
    ops.frictionModel("Coulomb", FRN_HIGH, mu3)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    pass  # No fiber sections — using spring elements


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    ops.node(NODE_BASE, 0.0, 0.0, 0.0)
    ops.node(NODE_BLDG, 0.0, 0.0, h_bldg, "-mass",
             m_bldg, m_bldg, m_bldg, 0.0, 0.0, 0.0)
    ops.node(NODE_TMD,  0.0, 0.0, h_bldg + h_tmd, "-mass",
             m_tmd, m_tmd, m_tmd, 0.0, 0.0, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    # Base — fixed in all DOFs (ground motion applied via MultipleSupport)
    ops.fix(NODE_BASE, 1, 1, 1, 1, 1, 1)

    # Building — free in X, fixed Y, free Z, fixed rotations (1-DOF X + vertical)
    # RX, RY, RZ fixed
    ops.fix(NODE_BLDG, 0, 1, 0, 1, 1, 1)

    # TMD — same as building (follows building horizontally + vertical isolation)
    ops.fix(NODE_TMD,  0, 1, 0, 1, 1, 1)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    # Building: twoNodeLink with elastic springs in X, Y, Z
    # DOF mapping for 1-DOF case (numCtrlDOF=1): mat 1 → dir 2 (X shear),
    # mat 3 → dir 1 (Z axial). Orient local-x = global-X.
    # Note: dirs map as: dir 2 = local X shear, dir 1 = local Z axial
    ops.element("twoNodeLink", ELE_BLDG, NODE_BASE, NODE_BLDG,
                "-mat", MAT_KX, MAT_KZ,
                "-dir", 2, 1,
                "-orient", 1, 0, 0,
                "-doRayleigh")

    # TMD isolator: TripleFrictionPendulum bearing
    # Wraps friction models 1/2/3 with vertical materials 10/11
    ops.element("TripleFrictionPendulum", ELE_TMD,
                NODE_BLDG, NODE_TMD,
                FRN_LOW, FRN_MED, FRN_HIGH,
                MAT_KVC, MAT_KVT, MAT_KVT, MAT_KVT,
                L1, L2, L3, d1, d2, d3, w_iso, uy_iso, kvt_iso, min_fv, tol_iso)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(odb_tag: int, output_dir: Path) -> "opst.post.CreateODB":
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_link_resp=True,       # twoNodeLink + TFP bearing
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Gravity: building self-weight + TMD self-weight."""
    ops.timeSeries("Linear", TS_GRAV)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAV)

    # Building weight (node 2): includes any experimental element contribution
    load_bldg_z = -(w_bldg + exp_elm_fact * w_tmd)
    ops.load(NODE_BLDG, 0.0, 0.0, load_bldg_z, 0.0, 0.0, 0.0)

    # TMD weight (node 3)
    load_tmd_z = -(1.0 - exp_elm_fact) * w_tmd
    ops.load(NODE_TMD, 0.0, 0.0, load_tmd_z, 0.0, 0.0, 0.0)


def define_ground_motion() -> None:
    """Multi-support excitation with Sine time series (0.5 Hz).

    Displacement, velocity, and acceleration Sine series for X-direction
    base excitation. No external files needed.
    """
    # Displacement: u(t) = amp * sin(ωt)
    ops.timeSeries("Sine", TS_DISP, gm_start, gm_finish, gm_period,
                   "-factor", gm_amp)
    # Velocity: v(t) = amp * ω * cos(ωt) = amp * ω * sin(ωt + π/2)
    ops.timeSeries("Sine", TS_VEL, gm_start, gm_finish, gm_period,
                   "-factor", gm_amp * gm_omega,
                   "-shift", np.pi / 2.0)
    # Acceleration: a(t) = -amp * ω² * sin(ωt)
    ops.timeSeries("Sine", TS_ACCEL, gm_start, gm_finish, gm_period,
                   "-factor", -gm_amp * gm_omega**2)

    # MultipleSupport pattern
    ops.pattern("MultipleSupport", PAT_GM)
    ops.groundMotion(GM_X, "Plain", "-disp", TS_DISP,
                     "-vel", TS_VEL, "-accel", TS_ACCEL)
    ops.imposedMotion(NODE_BASE, 1, GM_X)  # X-direction at base


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB") -> bool:
    """Apply gravity — LoadControl with Newton (elastic ⇒ 1 iteration/step)."""
    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-12, 25)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / N_GRAV_STEPS)
    ops.analysis("Static")

    for step in range(N_GRAV_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"WARNING: Gravity step {step + 1} failed (ok={ok})")
            return False
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()
    return True


def run_eigen() -> None:
    """Eigenvalue analysis — compute first 2 modes."""
    omega2 = ops.eigen("-fullGenLapack", 2)
    print("\nEigenvalues at start of transient:")
    print("|   lambda   |  omega   |  period | frequency |")
    for lam in omega2:
        omega = np.sqrt(lam)
        period = 2.0 * np.pi / omega
        freq = 1.0 / period if period > 0 else float("inf")
        print(f"| {lam:8.3e} | {omega:8.4f} | {period:7.4f} | {freq:9.4f} |")
    ops.wipeAnalysis()


def run_transient(odb: "opst.post.CreateODB") -> bool:
    """Run transient analysis with SmartAnalyze Transient.

    Integrator (Newmark) MUST be set before SmartAnalyze per AGENT.md §3c.
    The building is linear-elastic + TMD friction — KrylovNewton handles this.
    """
    ops.integrator("Newmark", 0.5, 0.25)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="NormDispIncr",
        testTol=1.0e-8,
        testIterTimes=50,
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
    )

    segs = analysis.transient_split(N_PTS)
    ok = True
    for i, _ in enumerate(segs):
        result = analysis.TransientAnalyze(DT_GM)
        if result < 0:
            print(f"WARNING: Transient step {i + 1}/{N_PTS} failed (ok={result})")
            ok = False
            break
        # Throttle ODB collection — 8192 steps × 3 nodes is manageable
        if i % 5 == 0:
            odb.fetch_response_step()

    analysis.close()
    return ok


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + eigen + transient, return ODB."""
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

    # Phase 1: Gravity
    define_gravity_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    print("Running gravity analysis...")
    if not run_gravity(odb):
        print("ERROR: Gravity analysis failed — aborting.")
        return odb

    # Phase 2: Eigen
    print("\nEigenvalue analysis...")
    run_eigen()

    # Phase 3: Transient (ground motion AFTER loadConst per §12z-1)
    define_ground_motion()

    print(f"\nRunning transient analysis ({N_PTS} steps, dt = {DT_GM:.6f} s)...")
    run_transient(odb)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and render visualizations."""
    odb.save_response()

    if not _headless():
        opst.post.set_odb_path(str(output_dir))
        fig_slider = opst.vis.plotly.plot_nodal_responses(
            odb_tag=ODB_TAG, slides=True, defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig_slider.write_html(str(output_dir / "vis_05_slider.html"))


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print("mosqueda: analysis complete.")
