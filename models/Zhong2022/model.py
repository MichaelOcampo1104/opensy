# ── 0. FILE HEADER ──────────────────────────────────────────────────────────────
"""
Model    : 12-Story MDOF Shear Building with Bilinear Story Springs
UniqueID : Zhong2022
Author   : Kuanshi Zhong, Stanford University (2022)
Date     : 2026-06-15
Purpose  : Nonlinear dynamic time-history analysis of a 12-story MDOF
           shear-building model with bilinear hysteretic story springs
           for seismic UQ studies via SimCenter EE-UQ.
Ref      : Zhong, K. (2022). SimCenter EE-UQ MDOF building model.
Units    : N, mm, MPa  (see standards/units.py)
Notes    : Converted from SimCenter EE-UQ MDOF_BuildingModel Tcl reference
           files (tcl_ref/newmark_solver.tcl, MyRecorder.tcl, MyPostprocess.tcl).
           Original units: kips, inches, seconds.
           EDPs: PID (peak inter-story drift ratio) and PFA (peak floor
           acceleration) for all 12 stories in both horizontal directions.
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────────
# Materials
MAT_SHEAR_X_BASE   = 1   # story 1 X-shear (stories offset from this)
MAT_SHEAR_Y_BASE   = 101  # story 1 Y-shear
MAT_RIGID_AXIAL    = 200  # rigid vertical spring
MAT_RIGID_ROT      = 201  # rigid rotational spring

# Nodes (base = 1, floors 1..12 = nodes 2..13)
NODE_BASE          = 1
NODE_ROOF          = 13

# Elements (twoNodeLink per story)
ELE_SHEAR_BASE     = 1    # story 1 link (stories offset from this)

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────────
# --- Geometry (original: 144 in/story, 1728 in total) ---
n_stories   = 12
h_story     = 144.0 * inch          # story height  [mm]

# --- Mass / weight (original: 50 kip/floor nominal) ---
w_floor     = 50.0 * kip            # seismic weight per floor  [N]

# --- Story stiffness (original: 500 kip/in nominal) ---
kx_story    = 500.0 * kip / inch    # X-direction story stiffness  [N/mm]
ky_story    = 500.0 * kip / inch    # Y-direction story stiffness  [N/mm]

# --- Story yield strength (original: 300 kip nominal) ---
Fyx_story   = 300.0 * kip           # X-direction yield force  [N]
Fyy_story   = 300.0 * kip           # Y-direction yield force  [N]

# --- Hysteretic hardening ratio ---
HRx         = 0.3                   # post-yield stiffness / initial stiffness  [-]
HRy         = 0.3

# --- Rigid link stiffnesses ---
K_rigid_axial = 1.0e12              # vertical spring  [N/mm]
K_rigid_rot   = 1.0e15              # rotational spring  [N·mm/rad]

# --- Damping ---
damp_ratio  = 0.02                  # Rayleigh damping ratio  [-]
mode_i      = 1                     # first mode for Rayleigh
mode_j      = 3                     # second mode for Rayleigh

# --- Ground motion ---
gm_dir      = Path(__file__).parent / "ground_motions"
gm_file_x   = ""                    # set to filename in ground_motions/ for X-dir
gm_file_y   = ""                    # set to filename in ground_motions/ for Y-dir
gm_factor   = 1.0                   # scale factor applied to record
gm_dt       = 0.01                  # time step  [s]
gm_npts     = 2000                  # number of points (synthetic default)

# --- Analysis ---
n_steps_gravity = 10

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────────
def init_model() -> None:
    """Initialise 2D model (ndm=2, ndf=3)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Bilinear Steel01 materials for story shear; Elastic for rigid links."""

    # --- Story shear springs (X direction) ---
    for i in range(1, n_stories + 1):
        ops.uniaxialMaterial("Steel01", MAT_SHEAR_X_BASE + i - 1,
                             Fyx_story, kx_story, HRx)

    # --- Story shear springs (Y direction) ---
    for i in range(1, n_stories + 1):
        ops.uniaxialMaterial("Steel01", MAT_SHEAR_Y_BASE + i - 1,
                             Fyy_story, ky_story, HRy)

    # --- Rigid springs (axial + rotational) ---
    ops.uniaxialMaterial("Elastic", MAT_RIGID_AXIAL, K_rigid_axial)
    ops.uniaxialMaterial("Elastic", MAT_RIGID_ROT,   K_rigid_rot)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────────
def define_sections() -> None:
    """No fiber sections needed — MDOF stick model uses link elements."""
    pass


# ── 7. NODES ─────────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Base node at (0,0); 12 floor nodes stacked vertically at h_story spacing."""
    # Base
    ops.node(NODE_BASE, 0.0, 0.0)

    # Floors 1–12
    for i in range(1, n_stories + 1):
        ops.node(NODE_BASE + i, 0.0, i * h_story)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix base in all DOFs. Assign lumped mass at each floor."""
    ops.fix(NODE_BASE, 1, 1, 1)

    mass_per_floor = w_floor / g_accel   # in consistent N-mm mass units

    for i in range(1, n_stories + 1):
        ops.mass(NODE_BASE + i, mass_per_floor, mass_per_floor, 0.0)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────────
def define_elements() -> None:
    """TwoNodeLink elements for each story with shear + rigid axial/rot springs.

    -orient  1 0 0  0 1 0  ensures local-x = global-X (horizontal shear),
    local-y = global-Y (vertical).
    """
    for i in range(1, n_stories + 1):
        node_below = NODE_BASE + i - 1
        node_above = NODE_BASE + i
        ele_tag    = ELE_SHEAR_BASE + i - 1

        ops.element("twoNodeLink", ele_tag, node_below, node_above,
                    "-mat", MAT_SHEAR_X_BASE + i - 1,
                            MAT_RIGID_AXIAL,
                            MAT_RIGID_ROT,
                    "-dir", 1, 2, 3,
                    "-orient", 1.0, 0.0, 0.0, 0.0, 1.0, 0.0)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise ODB after model is fully built."""
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=1)
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Apply floor weights as vertical nodal loads."""
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    for i in range(1, n_stories + 1):
        ops.load(NODE_BASE + i, 0.0, -w_floor, 0.0)


def _generate_synthetic_gm(dt: float, npts: int) -> np.ndarray:
    """Generate a synthetic Ricker-wavelet ground motion for testing.

    Returns acceleration in **g** units (compatible with PEER AT2 convention).
    """
    t = np.arange(npts) * dt
    freq = 2.0          # dominant frequency  [Hz]
    t0 = npts * dt / 3.0
    tau = np.pi * freq * (t - t0)
    accel_g = (1.0 - 2.0 * tau**2) * np.exp(-tau**2)
    # Scale to ~0.3g peak
    accel_g *= 0.3 / np.max(np.abs(accel_g))
    return accel_g


def define_ground_motion() -> tuple:
    """Define UniformExcitation ground motion patterns.

    Returns (dt, npts) for use by the dynamic solver.  If real .AT2 files
    are provided in ground_motions/ they are used; otherwise a synthetic
    Ricker wavelet is generated for testing.
    """
    def _load_peer_at2(filepath: Path) -> tuple:
        """Parse a PEER NGA .AT2 file, return (dt, npts, accel_g_values)."""
        with open(filepath) as f:
            lines = f.readlines()
        # Header: first line has npts and dt (space-delimited, last two tokens)
        header = lines[0].strip().split()
        npts = int(header[-2])
        dt   = float(header[-1])
        # Acceleration values follow (space-delimited across remaining lines)
        accel = []
        for line in lines[1:]:
            accel.extend([float(v) for v in line.strip().split()])
        accel = np.array(accel[:npts])
        return dt, npts, accel

    # --- X direction ---
    if gm_file_x:
        path_x = gm_dir / gm_file_x
        if path_x.exists():
            dt, npts, accel_x = _load_peer_at2(path_x)
        else:
            raise FileNotFoundError(f"Ground motion file not found: {path_x}")
    else:
        dt = gm_dt
        npts = gm_npts
        accel_x = _generate_synthetic_gm(dt, npts)

    # --- Y direction ---
    if gm_file_y:
        path_y = gm_dir / gm_file_y
        if path_y.exists():
            dt_y, npts_y, accel_y = _load_peer_at2(path_y)
            dt = min(dt, dt_y)
            npts = max(npts, npts_y)
        else:
            raise FileNotFoundError(f"Ground motion file not found: {path_y}")
    else:
        accel_y = _generate_synthetic_gm(dt, npts)

    # Acceleration in g → convert to mm/s² for UniformExcitation
    factor = gm_factor * g_accel

    ops.timeSeries("Path", 101, "-dt", dt, "-values", *accel_x,
                   "-factor", factor)
    ops.pattern("UniformExcitation", 2, 1, "-accel", 101)

    ops.timeSeries("Path", 102, "-dt", dt, "-values", *accel_y,
                   "-factor", factor)
    ops.pattern("UniformExcitation", 3, 2, "-accel", 102)

    return dt, npts


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────────

# EDP tracking — populated during dynamic analysis
_edp_peak_drift = {}       # key: "story-dof" → peak drift ratio
_edp_peak_accel = {}       # key: "floor-dof" → peak accel  [mm/s²]


def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10) -> None:
    """Apply gravity loads via load-controlled static analysis.

    Uses the documented AGENT.md §3c exception: manual LoadControl loop
    with odb.fetch_response_step(), because SmartAnalyze Static forcibly
    overrides the integrator to DisplacementControl.
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.test("EnergyIncr", 1.0e-6, 100)
    ops.algorithm("Linear")
    ops.analysis("Static")

    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def _track_edps() -> None:
    """Update peak EDP values from current converged state.

    Called after each odb.fetch_response_step() in the dynamic loop.
    """
    for story in range(1, n_stories + 1):
        node_above = NODE_BASE + story
        node_below = NODE_BASE + story - 1

        for dof in [1, 2]:
            # Inter-story drift ratio
            d_above = ops.nodeDisp(node_above, dof)
            d_below = ops.nodeDisp(node_below, dof)
            drift = abs(d_above - d_below) / h_story
            key = f"{story}-{dof}"
            _edp_peak_drift[key] = max(_edp_peak_drift.get(key, 0.0), drift)

            # Floor acceleration (at floor node, i.e. node_above)
            a_floor = abs(ops.nodeAccel(node_above, dof))
            key_a = f"{story}-{dof}"
            _edp_peak_accel[key_a] = max(_edp_peak_accel.get(key_a, 0.0), a_floor)


def run_dynamic(
    odb: "opst.post.CreateODB",
    dt: float,
    npts: int,
    odb_every_n: int = 5,
) -> None:
    """Run transient dynamic analysis with SmartAnalyze + Newmark integration.

    Rayleigh damping is computed from eigenvalues of modes {mode_i, mode_j}.
    EDP peak values are tracked during the loop via _track_edps().

    Args:
        odb: Active CreateODB instance.
        dt: Time step size [s].
        npts: Number of time steps.
        odb_every_n: Throttle ODB collection to every Nth step.
    """
    # --- Eigen analysis for Rayleigh damping ---
    # Use default solver (subspace iteration) — fullGenLapack is unstable
    # with the very stiff vertical/rotational springs in twoNodeLink elements.
    eigenvalues = ops.eigen(mode_j)
    omega_i = eigenvalues[mode_i - 1] ** 0.5
    omega_j = eigenvalues[mode_j - 1] ** 0.5

    T1 = 2.0 * np.pi / omega_i
    Tj = 2.0 * np.pi / omega_j
    print(f"  T{mode_i} = {T1:.4f} s,  T{mode_j} = {Tj:.4f} s")

    alpha_m = 2.0 * omega_i * omega_j / (omega_i + omega_j) * damp_ratio
    beta_k  = 2.0 / (omega_i + omega_j) * damp_ratio
    ops.rayleigh(alpha_m, 0.0, beta_k, 0.0)

    # --- SmartAnalyze Transient ---
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
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
    t_current = 0.0
    for i, seg in enumerate(segs):
        ok = analysis.TransientAnalyze(dt)
        if ok < 0:
            print(f"  Dynamic analysis failed at t = {t_current:.3f} s (step {i})")
            break
        t_current += dt
        if i % odb_every_n == 0:
            odb.fetch_response_step()
            _track_edps()

    analysis.close()
    print(f"  Completed {i + 1} steps (t_final = {t_current:.3f} s)")


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + dynamic, return ODB for post-processing."""
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

    odb = create_odb(output_dir)

    define_gravity_loads()
    gm_dt, gm_npts = define_ground_motion()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    print("Running gravity analysis ...")
    run_gravity(odb, n_steps=n_steps_gravity)

    print(f"Running dynamic analysis ({gm_npts} steps, dt={gm_dt:.4f} s) ...")
    run_dynamic(odb, gm_dt, gm_npts, odb_every_n=5)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
) -> dict:
    """Flush ODB, write EDPs to JSON, and generate deformation visualizations.

    EDPs are tracked during the dynamic analysis loop (_track_edps) and
    assembled here.  Format matches SimCenter EE-UQ EDP.json convention:
      - PID (Peak Inter-story Drift ratio) for stories 1–12, dof 1 and 2
      - PFA (Peak Floor Acceleration)     for floors  1–12, dof 1 and 2

    Returns:
        dict mapping EDP name → value.
    """
    odb.save_response()

    # --- Assemble EDPs from tracked peak values ---
    edp_values = {}

    for story in range(1, n_stories + 1):
        for dof in [1, 2]:
            drift_val = _edp_peak_drift.get(f"{story}-{dof}", 0.0)
            accel_val = _edp_peak_accel.get(f"{story}-{dof}", 0.0)
            edp_values[f"1-PID-{story}-{dof}"] = drift_val
            edp_values[f"1-PFA-{story}-{dof}"] = accel_val

    # --- Write EDPs to JSON (SimCenter-compatible) ---
    import json
    edp_file = output_dir / "EDP.json"
    edp_list = [{"name": k, "value": v} for k, v in edp_values.items()]
    with open(edp_file, "w") as f:
        json.dump({"EDP": edp_list}, f, indent=2)
    print(f"EDP file written: {edp_file}")

    # --- Visualisation ---
    if not _headless():
        fig_defo = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, step="absMax", defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig_defo.write_html(str(output_dir / "vis_05_deformed_peak.html"))

        fig_slider = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, slides=True, defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig_slider.write_html(str(output_dir / "vis_06_deformed_slider.html"))

    return edp_values


# ── 14. MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    edps = post_process(odb, output_dir)
    print(f"\nExtracted {len(edps)} EDPs.")
