# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Single-story single-bay 2D steel SMF — DYNAMIC time-history analysis
UniqueID : Guan2020
Author   : Xingquan Guan, Henry Burton, Mehrdad Shokrabadi (2020),
           ported by OpenSeesPy Standardisation Agent
Date     : 2026-06-06
Purpose  : Nonlinear dynamic time-history analysis of a 2D steel special moment
           frame with leaning column under ground motion excitation.  Part of
           the Guan et al. (2020) database of 621 steel SMF buildings.
Ref      : Guan, X., Burton, H., Shokrabadi, M. (2020). "A Database of Seismic
           Designs, Nonlinear Models, and Seismic Responses for Steel Moment
           Resisting Frame Buildings." DesignSafe-CI, DOI: 10.17603/ds2-8yc7-1285.
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
from vis_utils import vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo, vis_anim


# ══════════════════════════════════════════════════════════════════════════════
#  SHARED MODEL DEFINITION  (same as model.py)
# ══════════════════════════════════════════════════════════════════════════════

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────

TRANS_PDELTA = 1
TRANS_LINEAR = 2

MAT_TRUSS_RIGID = 60000
MAT_STIFF       = 1200
MAT_SOFT        = 1300

NODE_COL1_BASE  = 111
NODE_COL2_BASE  = 211
NODE_COL1_ROOF  = 121
NODE_COL2_ROOF  = 221
NODE_LEAN_BASE  = 31
NODE_LEAN_ROOF  = 32
NODE_LEAN_MID   = 322

ELE_COL1        = 3111121
ELE_COL2        = 3211221
ELE_BEAM         = 2121221
ELE_LEAN_COL    = 331322
ELE_LEAN_SPRING = 32322
ELE_TRUSS       = 222132

PATTERN_DEAD    = 101
PATTERN_LIVE    = 102
PATTERN_EQ      = 103


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────

def _wf(d_in, A_in2, bf_in, tw_in, tf_in, Ix_in4, Iy_in4,
        Zx_in3, Zy_in3, ry_in, J_in4):
    """Build a WF section tuple with N-mm conversion."""
    return (
        d_in * inch,
        A_in2 * inch**2,
        bf_in * inch,
        tw_in * inch,
        tf_in * inch,
        Ix_in4 * inch**4,
        Iy_in4 * inch**4,
        Zx_in3 * inch**3,
        Zy_in3 * inch**3,
        ry_in * inch,
        J_in4 * inch**4,
    )

SECTION_DB = {
    "W14X370": _wf(17.9, 109.0, 16.5, 1.66, 2.66, 5440, 831, 672, 260, 2.78, 99.2),
    "W14X455": _wf(19.1, 134.0, 17.0, 2.02, 3.21, 7190, 1100, 847, 329, 2.89, 158.0),
    "W36X160": _wf(36.0, 47.0,  12.0, 0.650, 1.02, 9760, 295, 596, 74.2, 2.50, 17.2),
}

def section_property(name: str) -> tuple:
    return SECTION_DB[name]

bay_width    = 20.00 * ft
h_first      = 19.50 * ft
h_typical    = 13.00 * ft      # unused, single-story

Es = 29000.0 * ksi
Gs = 11500.0 * ksi

col_ext    = section_property("W14X370")
beam_prop  = section_property("W36X160")
col_ext_A  = col_ext[1]
col_ext_Ix = col_ext[5]
beam_A     = beam_prop[1]
beam_Ix    = beam_prop[5]

A_rigid = 200000000.0 * inch**2
I_rigid = 9000000000.0 * inch**4

large_stiff    = 1.0e12 * ksi
negligible_val = 1.0e-12 * ksi

g_accel_in = 386.09 * inch / sec**2

floor2_weight        = 1800.00 * kip
tributary_mass_ratio = 0.5
nodes_per_floor      = 3
nodal_mass_floor2    = (floor2_weight * tributary_mass_ratio
                        / nodes_per_floor / g_accel_in)

beam_dead_load = 0.066667 * (kip / inch)
beam_live_load = 0.041667 * (kip / inch)
lean_dead_load = 900.0 * kip
lean_live_load = 562.5 * kip

n_steps_gravity = 10

n_eigen_modes = 3


# ══════════════════════════════════════════════════════════════════════════════
#  DYNAMIC ANALYSIS PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════

# Rayleigh damping: 2% on modes 1 and 2 (standard for steel SMF)
damp_ratio = 0.02
damp_mode_i = 1         # Mode i for Rayleigh stiffness-proportional damping
damp_mode_j = 2         # Mode j

# Ground motion — synthetic pulse for testing; replace with real record
# When using a real .txt/.acc file, set GM_FILE to the file path and
# GM_DT / GM_NPTS accordingly.
GM_FILE = None           # set to pathlib Path for real ground motion
GM_DT   = 0.01           # time step (s)
GM_NPTS = 2000           # number of points (20 s at 0.01 s)
GM_SCALE = 1.0           # ground motion scale factor
GM_DIR  = 1              # direction of excitation (1 = X)

# ODB throttle for transient analysis (collect every Nth step)
ODB_EVERY_N = 5


# ── 4. GROUND MOTION GENERATOR ───────────────────────────────────────────────

def generate_synthetic_gm(dt: float, npts: int, gm_dir: int = 1) -> Path:
    """Generate a synthetic ground-motion file (Ricker-like pulse + noise).

    Writes ``ground_motions/synthetic_gm.acc`` and returns its path.
    Overwrite this file or set GM_FILE to use a real record.

    Args:
        dt: Time step in seconds.
        npts: Number of points.
        gm_dir: Direction tag for the excitation.

    Returns:
        Path to the generated acceleration file.
    """
    t = np.arange(npts) * dt
    # Ricker wavelet centred at t0 = 5 s
    t0 = 5.0
    freq = 2.5  # Hz
    a = (1.0 - 2.0 * (np.pi * freq * (t - t0)) ** 2) * \
        np.exp(-(np.pi * freq * (t - t0)) ** 2)
    # Taper ends
    window = np.ones(npts)
    n_taper = int(0.5 / dt)          # 0.5 s taper
    window[:n_taper] = np.linspace(0, 1, n_taper)
    window[-n_taper:] = np.linspace(1, 0, n_taper)
    a *= window
    # Scale to ~0.3g peak (9810 * 0.3 mm/s²)
    a *= (0.3 * 9810.0) / max(abs(a)) if max(abs(a)) > 1e-12 else 1.0

    out_dir = Path(__file__).parent / "ground_motions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "synthetic_gm.acc"
    np.savetxt(out_path, a, fmt="%.6e")
    print(f"Synthetic ground motion written to {out_path} "
          f"({npts} pts, dt={dt}s, peak={max(abs(a)):.1f} mm/s²)")
    return out_path


# ══════════════════════════════════════════════════════════════════════════════
#  MODEL BUILDING  (shared with model.py)
# ══════════════════════════════════════════════════════════════════════════════

# ── 5. MODEL INITIALISATION ──────────────────────────────────────────────────

def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 6. MATERIALS ─────────────────────────────────────────────────────────────

def define_materials() -> None:
    ops.uniaxialMaterial("Elastic", MAT_STIFF, large_stiff)
    ops.uniaxialMaterial("Elastic", MAT_SOFT, negligible_val)
    ops.uniaxialMaterial("Elastic", MAT_TRUSS_RIGID, 1.0)


# ── 7. GEOMETRIC TRANSFORMATIONS ────────────────────────────────────────────

def define_transformations() -> None:
    ops.geomTransf("PDelta", TRANS_PDELTA)
    ops.geomTransf("Linear", TRANS_LINEAR)


# ── 8. NODES ─────────────────────────────────────────────────────────────────

def define_nodes() -> None:
    ops.node(NODE_COL1_BASE, 0.0, 0.0)
    ops.node(NODE_COL2_BASE, bay_width, 0.0)
    ops.node(NODE_COL1_ROOF, 0.0, h_first)
    ops.node(NODE_COL2_ROOF, bay_width, h_first)
    ops.node(NODE_LEAN_BASE, 2.0 * bay_width, 0.0)
    ops.node(NODE_LEAN_ROOF, 2.0 * bay_width, h_first)
    ops.node(NODE_LEAN_MID,  2.0 * bay_width, h_first)


# ── 9. BOUNDARY CONDITIONS ───────────────────────────────────────────────────

def define_boundary_conditions() -> None:
    ops.fix(NODE_COL1_BASE, 1, 1, 1)
    ops.fix(NODE_COL2_BASE, 1, 1, 1)
    ops.fix(NODE_LEAN_BASE, 1, 1, 0)
    ops.equalDOF(NODE_COL1_ROOF, NODE_COL2_ROOF, 1)
    ops.equalDOF(NODE_COL1_ROOF, NODE_LEAN_ROOF, 1)


# ── 10. ELEMENTS ─────────────────────────────────────────────────────────────

def define_elements() -> None:
    ops.element("elasticBeamColumn", ELE_COL1,
                NODE_COL1_BASE, NODE_COL1_ROOF,
                col_ext_A, Es, col_ext_Ix, TRANS_PDELTA)
    ops.element("elasticBeamColumn", ELE_COL2,
                NODE_COL2_BASE, NODE_COL2_ROOF,
                col_ext_A, Es, col_ext_Ix, TRANS_PDELTA)
    ops.element("elasticBeamColumn", ELE_BEAM,
                NODE_COL1_ROOF, NODE_COL2_ROOF,
                beam_A, Es, beam_Ix, TRANS_LINEAR)
    ops.element("elasticBeamColumn", ELE_LEAN_COL,
                NODE_LEAN_BASE, NODE_LEAN_MID,
                A_rigid, Es, I_rigid, TRANS_PDELTA)
    ops.element("zeroLength", ELE_LEAN_SPRING,
                NODE_LEAN_ROOF, NODE_LEAN_MID,
                "-mat", MAT_STIFF, MAT_STIFF, MAT_SOFT,
                "-dir", 1, 2, 3)
    ops.element("truss", ELE_TRUSS,
                NODE_COL2_ROOF, NODE_LEAN_ROOF,
                A_rigid, MAT_TRUSS_RIGID)


# ── 11. ODB ──────────────────────────────────────────────────────────────────

def create_odb(output_dir: Path, odb_tag: int = 1) -> "opst.post.CreateODB":
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=odb_tag)
    odb.save_model_data()
    return odb


# ── 12. LOADING ──────────────────────────────────────────────────────────────

def define_masses() -> None:
    ops.mass(NODE_COL1_ROOF, nodal_mass_floor2, negligible_val, negligible_val)
    ops.mass(NODE_COL2_ROOF, nodal_mass_floor2, negligible_val, negligible_val)
    ops.mass(NODE_LEAN_ROOF, nodal_mass_floor2, negligible_val, negligible_val)


def define_dead_loads() -> None:
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", PATTERN_DEAD, 1)
    ops.eleLoad("-ele", ELE_BEAM, "-type", "-beamUniform", -beam_dead_load, 0.0)
    ops.load(NODE_LEAN_ROOF, 0.0, -lean_dead_load, 0.0)


def define_live_loads() -> None:
    ops.timeSeries("Constant", 2)
    ops.pattern("Plain", PATTERN_LIVE, 2)
    ops.eleLoad("-ele", ELE_BEAM, "-type", "-beamUniform", -beam_live_load, 0.0)
    ops.load(NODE_LEAN_ROOF, 0.0, -lean_live_load, 0.0)


# ── 13. EIGENVALUE ───────────────────────────────────────────────────────────

def run_eigenvalue(output_dir: Path) -> list:
    eigenvalues = ops.eigen(n_eigen_modes)
    periods = [2.0 * np.pi / (lam**0.5) for lam in eigenvalues]
    omega = [(2.0 * np.pi / T) for T in periods]

    eigen_dir = output_dir / "EigenAnalysisOutput"
    eigen_dir.mkdir(parents=True, exist_ok=True)
    with open(eigen_dir / "Periods.out", "w") as f:
        for i, T in enumerate(periods, 1):
            f.write(f"Mode {i}: T = {T:.6f} s, omega = {omega[i-1]:.4f} rad/s\n")

    print(f"Eigenvalue: T1={periods[0]:.4f}s, T2={periods[1]:.4f}s, "
          f"T3={periods[2]:.4f}s")
    return periods, omega


# ══════════════════════════════════════════════════════════════════════════════
#  ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

# ── 14. GRAVITY ──────────────────────────────────────────────────────────────

def run_gravity(odb: "opst.post.CreateODB", n_steps: int = n_steps_gravity) -> None:
    """Apply gravity loads incrementally using LoadControl (permitted exception)."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-6, 20, 2)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.analysis("Static")
    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


# ── 15. DYNAMIC ANALYSIS ─────────────────────────────────────────────────────

def run_dynamic(
    odb: "opst.post.CreateODB",
    periods: list,
    omega: list,
    gm_file: Path,
    dt: float,
    npts: int,
    gm_scale: float = 1.0,
    gm_dir: int = 1,
) -> None:
    """Run transient time-history analysis under uniform ground excitation.

    Uses SmartAnalyze (Transient) with Newmark integration and Rayleigh damping
    calibrated from eigenvalue results.

    Args:
        odb: Active CreateODB instance.
        periods: Modal periods [T1, T2, ...].
        omega: Modal circular frequencies [ω1, ω2, ...].
        gm_file: Path to ground motion acceleration file (one value per line).
        dt: Time step in seconds.
        npts: Number of acceleration points.
        gm_scale: Ground motion scale factor.
        gm_dir: Direction of uniform excitation (1 = X).
    """
    # --- Rayleigh damping ---
    # Mass and stiffness proportional coefficients from two modes
    omega_i = omega[damp_mode_i - 1]
    omega_j = omega[damp_mode_j - 1]
    alpha_m = damp_ratio * (2.0 * omega_i * omega_j) / (omega_i + omega_j)
    beta_k = damp_ratio * 2.0 / (omega_i + omega_j)
    ops.rayleigh(alpha_m, 0.0, beta_k, 0.0)
    print(f"Rayleigh damping: α_M={alpha_m:.6f}, β_K={beta_k:.6f} "
          f"(ζ={damp_ratio:.1%} on modes {damp_mode_i},{damp_mode_j})")

    # --- Ground motion input ---
    ops.timeSeries("Path", 10, "-dt", dt, "-filePath", str(gm_file),
                   "-factor", gm_scale)
    ops.pattern("UniformExcitation", PATTERN_EQ, gm_dir, "-accel", 10)

    # --- Transient analysis (SmartAnalyze) ---
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("Newmark", 0.5, 0.25)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )
    segs = analysis.transient_split(npts)
    n_segs = len(segs)
    for i, _ in enumerate(segs):
        ok = analysis.TransientAnalyze(dt)
        if ok < 0:
            print(f"Dynamic analysis failed at step {i}/{n_segs}")
            break
        if i % ODB_EVERY_N == 0:
            odb.fetch_response_step()
    analysis.close()


# ── 16. ORCHESTRATION ────────────────────────────────────────────────────────

def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity → eigenvalue → dynamic time-history.

    Sequence:
      1. Dead load gravity (LoadControl) + loadConst
      2. Live load gravity (LoadControl) + loadConst
      3. Eigenvalue analysis → periods + Rayleigh calibration
      4. Generate (or load) ground motion
      5. Dynamic transient analysis (SmartAnalyze)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    # --- Build ---
    init_model()
    define_materials()
    define_transformations()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)
    odb = create_odb(output_dir, odb_tag=1)
    define_masses()

    # --- Gravity ---
    define_dead_loads()
    vis_loads(output_dir, filename="vis_03a_dead_loads.html")
    run_gravity(odb)
    define_live_loads()
    vis_loads(output_dir, filename="vis_03b_live_loads.html")
    run_gravity(odb)

    # --- Eigenvalue ---
    periods, omega = run_eigenvalue(output_dir)

    # --- Ground motion ---
    if GM_FILE is not None:
        gm_file = Path(GM_FILE)
    else:
        gm_file = generate_synthetic_gm(GM_DT, GM_NPTS, GM_DIR)

    # --- Dynamic ---
    vis_pre_analysis(output_dir)
    run_dynamic(
        odb,
        periods=periods,
        omega=omega,
        gm_file=gm_file,
        dt=GM_DT,
        npts=GM_NPTS if GM_FILE is None else _count_gm_points(gm_file),
        gm_scale=GM_SCALE,
        gm_dir=GM_DIR,
    )
    return odb


def _count_gm_points(gm_file: Path) -> int:
    """Count lines in a ground motion file."""
    with open(gm_file) as f:
        return sum(1 for _ in f)


# ── 17. POST-PROCESSING ──────────────────────────────────────────────────────

def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB and render deformed shape + dynamic animation."""
    odb.save_response()
    vis_defo(output_dir, filename="vis_05_deformed.html")
    vis_anim(
        output_dir,
        filename="vis_06_dynamic_animation.html",
        odb_tag=1,
        defo_scale=10.0,
        resp_type="disp",
        resp_dof=("UX", "UY"),
        show_undeformed=True,
    )


# ── 18. MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print(f"Guan2020 dynamic analysis complete. Output in {output_dir}")
