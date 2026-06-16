# ---- 0. FILE HEADER ----------------------------------------------------------------------------------------------------------------------------
"""
Model    : 3D RC Frame -- 3-Story 1-Bay with Aggregator Columns + Elastic Beams
UniqueID : XMU_Chapter4_4
Author   : XMU (Xiamen University) -- Chapter 4.4 Example
Date     : 2026-06-16
Purpose  : Textbook-example dynamic time-history analysis of a 3-story 1-bay
           3D RC frame with fiber-section columns (Concrete01 confined core +
           unconfined cover, Steel01 rebar, Aggregator torsion), elastic beams,
           rigid diaphragms, and bi-directional Tabas earthquake (FN + FP).
Ref      : XMU Finite Element Analysis course, Chapter 4.4
Units    : N, mm, MPa  (see standards/units.py)
Notes    : Converted from model.tcl + RCsection.tcl.
           Original units: kN, m, kPa -- converted to N, mm, MPa.
           kN->N (x1000), m->mm (x1000), kPa->MPa (/1000).
           Column fiber section: 457.2x457.2 mm with 377.2x377.2 mm confined
           core, 40 mm cover, 3 bars per side (Phi25.5, area=510 mm^2).
           Aggregator wraps fiber section with elastic torsion material (GJ).
           Beam elastic section uses E, A, Iz, Iy, G=GJ, J=1.0 trick.
           dispBeamColumn elements (4 IPs columns, 3 IPs beams).
           RC fiber sections use stress-strain materials (standard /1000
           kPa->MPa conversion applies, unlike Aggregator force-deformation).
"""

# ---- 1. IMPORTS --------------------------------------------------------------------------------------------------------------------------------------
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ---- 2. TAG REGISTRY ----------------------------------------------------------------------------------------------------------------------------
# Materials
MAT_CONCRETE_CORE  = 1   # Concrete01 -- confined core (higher strength, more ductile)
MAT_CONCRETE_COVER = 2   # Concrete01 -- unconfined cover
MAT_STEEL_REBAR    = 3   # Steel01    -- longitudinal rebar
MAT_TORSION        = 10  # Elastic    -- torsion material for Aggregator

# Sections
SEC_COL_FIBER = 1   # Fiber section (RC -- core + cover + rebar)
SEC_COL_AGG   = 2   # Aggregator -- fiber + torsion
SEC_BEAM      = 3   # Elastic 3D beam section

# Beam integration (dispBeamColumn requires beamIntegration in OpenSeesPy)
INTEG_COL  = 1
INTEG_BEAM = 2

# Geometric transformations
TRANS_COL  = 1
TRANS_BEAM = 2

# ---- 3. PARAMETERS --------------------------------------------------------------------------------------------------------------------------------
# --- Geometry (original: m) ---
story_h = 3.6576 * m                         # story height  [mm]
bay_x   = 6.096 * m                          # bay width X   [mm]
bay_y   = 6.096 * m                          # bay width Y   [mm]

# --- Column fiber-section geometry (original: m, m^2) ---
col_dim     = 0.4572 * m                     # column side  [mm]
cover_thk   = 0.04 * m                       # cover thickness  [mm]
core_dim    = col_dim - 2.0 * cover_thk      # confined core side  [mm]
n_bars      = 3                              # bars per side
bar_area    = 0.00051 * m**2                 # single bar area  [mm^2]  (Phi25.5 ~ 510 mm^2)
nf_core_y   = 8                              # core mesh subdivisions Y
nf_core_z   = 8                              # core mesh subdivisions Z
nf_cover_y  = 10                             # cover mesh subdivisions Y
nf_cover_z  = 10                             # cover mesh subdivisions Z

# --- Column materials (original: kPa -- fiber stress-strain /1000) ---
fc_core     = -34473.8 * kPa                 # confined core peak stress  [MPa]
epsc_core   = -0.005                         # confined strain at peak
fcu_core    = -24131.66 * kPa                # confined crushing stress  [MPa]
epsu_core   = -0.02                          # confined ultimate strain

fc_cover    = -27579.04 * kPa                # unconfined cover peak stress  [MPa]
epsc_cover  = -0.002                         # unconfined strain at peak
fcu_cover   = 0.0 * kPa                      # unconfined crushing stress
epsu_cover  = -0.006                         # unconfined ultimate strain

Fy_steel    = 248200.0 * kPa                 # rebar yield strength  [MPa]
Es_steel    = 2.1e8 * kPa                    # rebar elastic modulus  [MPa]
steel_b     = 0.02                           # strain hardening ratio

# --- Torsion material (original: kPa.m^4) ---
GJ = 68947600000000 * kPa * m**4            # torsional rigidity  [N.mm^2]

# --- Beam elastic section (original: kPa, m^2, m^4) ---
E_beam  = 24855585.89304 * kPa               # elastic modulus  [MPa]
A_beam  = 0.278709 * m**2                    # cross-section area  [mm^2]
Iz_beam = 0.004315 * m**4                    # moment of inertia about local z  [mm^4]
Iy_beam = 0.002427 * m**4                    # moment of inertia about local y  [mm^4]
# Note: G=GJ, J=1.0 in section Elastic (Tcl trick: GxJ = GJ where J=1.0)

# --- Mass (original: kN.s^2/m -> N.s^2/mm, both are tonne-equivalent) ---
mass_floor = 30.0                            # translational mass per floor
mass_rot   = mass_floor * (bay_x**2 + bay_y**2) / 12.0  # rotational mass

# --- Column gravity load (original: kN, downward on Z) ---
p_col = -74.0 * kN                           # vertical load per column node  [N]

# --- Ground motion ---
gm_dir    = Path(__file__).parent / "ground_motions"
gm_file_x = "tabasfn.txt"                    # Tabas fault-normal
gm_file_y = "tabasfp.txt"                    # Tabas fault-parallel
gm_dt     = 0.02                             # time step  [s]
gm_npts   = 2500                             # number of points (50 s)

# --- Damping ---
damp_ratio = 0.02                            # 2% on mode 1

# --- Analysis ---
n_steps_gravity = 3
n_steps_free    = 0
odb_every_n     = 5


# ---- 4. MODEL INITIALISATION ------------------------------------------------------------------------------------------------------------
def init_model() -> None:
    """Initialise 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ---- 5. MATERIALS ----------------------------------------------------------------------------------------------------------------------------------
def define_materials() -> None:
    """Concrete01 (core + cover), Steel01 rebar, Elastic torsion."""
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE_CORE,
                         fc_core, epsc_core, fcu_core, epsu_core)
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE_COVER,
                         fc_cover, epsc_cover, fcu_cover, epsu_cover)
    ops.uniaxialMaterial("Steel01", MAT_STEEL_REBAR,
                         Fy_steel, Es_steel, steel_b)
    ops.uniaxialMaterial("Elastic", MAT_TORSION, GJ)


# ---- 6. SECTIONS ------------------------------------------------------------------------------------------------------------------------------------
def _build_rc_section(
    sec_tag: int,
    h: float, b: float, cover: float,
    core_mat: int, cover_mat: int, steel_mat: int,
    num_bars: int, bar_area: float,
    nf_core_y: int, nf_core_z: int,
    nf_cover_y: int, nf_cover_z: int,
) -> None:
    """Build RC fiber section replicating RCsection.tcl procedure.

    Patch layout (Y=vertical in section plane, Z=horizontal):
      - Confined core: quadr patch, nfCoreZ x nfCoreY mesh
      - Cover: 4 quadr patches (top, bottom, left, right)
      - Rebar: 4 straight layers (top, bottom, left, right)
        Side layers skip corner bars (numBars-2 each) to avoid double-counting.
    """
    cover_y  =  h / 2.0
    cover_z  =  b / 2.0
    ncover_y = -cover_y
    ncover_z = -cover_z

    core_y  = cover_y - cover
    core_z  = cover_z - cover
    ncore_y = -core_y
    ncore_z = -core_z

    from opstool.pre.section import section as _sec, patch as _pch, layer as _lyr

    _sec("Fiber", sec_tag, "-GJ", 0.0)

    # Confined core (quadr: I->J->K->L counter-clockwise in Y-Z plane)
    _pch("quadr", core_mat, nf_core_z, nf_core_y,
         ncore_y, core_z,    # I  (bottom-right?  Y=-core, Z=+core)
         ncore_y, ncore_z,   # J  (bottom-left)
         core_y,  ncore_z,   # K  (top-left)
         core_y,  core_z)    # L  (top-right)

    # Cover -- top (Z+ side)
    _pch("quadr", cover_mat, 1, nf_cover_y,
         ncover_y, cover_z, ncore_y, core_z, core_y, core_z, cover_y, cover_z)
    # Cover -- bottom (Z- side)
    _pch("quadr", cover_mat, 1, nf_cover_y,
         ncore_y, ncore_z, ncover_y, ncover_z, cover_y, ncover_z, core_y, ncore_z)
    # Cover -- left (Y- side)
    _pch("quadr", cover_mat, nf_cover_z, 1,
         ncover_y, cover_z, ncover_y, ncover_z, ncore_y, ncore_z, ncore_y, core_z)
    # Cover -- right (Y+ side)
    _pch("quadr", cover_mat, nf_cover_z, 1,
         core_y, core_z, core_y, ncore_z, cover_y, ncover_z, cover_y, cover_z)

    # Rebar -- top layer (at Y=core_y, along Z)
    _lyr("straight", steel_mat, num_bars, bar_area,
         core_y, core_z, core_y, ncore_z)
    # Rebar -- bottom layer (at Y=ncore_y, along Z)
    _lyr("straight", steel_mat, num_bars, bar_area,
         ncore_y, core_z, ncore_y, ncore_z)

    # Rebar -- side layers (skip corner bars: num_bars - 2)
    num_bars_side = num_bars - 2
    spacing_y = (core_y - ncore_y) / (num_bars - 1)
    # Left side (at Z=core_z, along Y, excluding corners)
    _lyr("straight", steel_mat, num_bars_side, bar_area,
         core_y - spacing_y, core_z, ncore_y + spacing_y, core_z)
    # Right side (at Z=ncore_z, along Y, excluding corners)
    _lyr("straight", steel_mat, num_bars_side, bar_area,
         core_y - spacing_y, ncore_z, ncore_y + spacing_y, ncore_z)


def define_sections() -> None:
    """RC fiber section + Aggregator for columns; Elastic section for beams."""
    _build_rc_section(
        sec_tag=SEC_COL_FIBER,
        h=col_dim, b=col_dim, cover=cover_thk,
        core_mat=MAT_CONCRETE_CORE,
        cover_mat=MAT_CONCRETE_COVER,
        steel_mat=MAT_STEEL_REBAR,
        num_bars=n_bars,
        bar_area=bar_area,
        nf_core_y=nf_core_y, nf_core_z=nf_core_z,
        nf_cover_y=nf_cover_y, nf_cover_z=nf_cover_z,
    )

    # Aggregator: fiber section + torsional stiffness
    ops.section("Aggregator", SEC_COL_AGG, MAT_TORSION, "T",
                "-section", SEC_COL_FIBER)

    # Beam elastic 3D section -- G=GJ, J=1.0 trick from source Tcl
    ops.section("Elastic", SEC_BEAM, E_beam, A_beam,
                Iz_beam, Iy_beam, GJ, 1.0)


# ---- 7. NODES ------------------------------------------------------------------------------------------------------------------------------------------
def define_nodes() -> None:
    """Create 19 nodes: 4 base, 4x3 column nodes, 3 master nodes."""
    bx2 = bay_x / 2.0
    by2 = bay_y / 2.0
    z_vals = [0.0, story_h, 2 * story_h, 3 * story_h]

    # Base (Z=0)
    ops.node(1,  -bx2,  by2, z_vals[0])
    ops.node(2,   bx2,  by2, z_vals[0])
    ops.node(3,   bx2, -by2, z_vals[0])
    ops.node(4,  -bx2, -by2, z_vals[0])

    # Floor 1 (Z=h)
    ops.node(5,  -bx2,  by2, z_vals[1])
    ops.node(6,   bx2,  by2, z_vals[1])
    ops.node(7,   bx2, -by2, z_vals[1])
    ops.node(8,  -bx2, -by2, z_vals[1])
    ops.node(9,   0.0,  0.0, z_vals[1])   # master

    # Floor 2 (Z=2h)
    ops.node(10, -bx2,  by2, z_vals[2])
    ops.node(11,  bx2,  by2, z_vals[2])
    ops.node(12,  bx2, -by2, z_vals[2])
    ops.node(13, -bx2, -by2, z_vals[2])
    ops.node(14,  0.0,  0.0, z_vals[2])   # master

    # Floor 3 (Z=3h)
    ops.node(15, -bx2,  by2, z_vals[3])
    ops.node(16,  bx2,  by2, z_vals[3])
    ops.node(17,  bx2, -by2, z_vals[3])
    ops.node(18, -bx2, -by2, z_vals[3])
    ops.node(19,  0.0,  0.0, z_vals[3])   # master


# ---- 8. BOUNDARY CONDITIONS --------------------------------------------------------------------------------------------------------------
def define_boundary_conditions() -> None:
    """Fix bases; rigid diaphragms; lumped mass at master nodes."""
    # Fixed column bases (all 6 DOFs)
    for node in range(1, 5):
        ops.fix(node, 1, 1, 1, 1, 1, 1)

    # Rigid diaphragms -- constrain DOF 3 (Rz) of slaves to master
    ops.rigidDiaphragm(3,  9,  5,  6,  7,  8)
    ops.rigidDiaphragm(3, 14, 10, 11, 12, 13)
    ops.rigidDiaphragm(3, 19, 15, 16, 17, 18)

    # Fix master nodes: free X, Y, Rz; fixed Z, Rx, Ry
    # (rigidDiaphragm constrains slave Rz->master, so master Rz stays free)
    for master in [9, 14, 19]:
        ops.fix(master, 0, 0, 1, 1, 1, 0)

    # Lumped mass at each floor master node (X, Y transl + Rz rotation)
    for master in [9, 14, 19]:
        ops.mass(master, mass_floor, mass_floor, 0.0, 0.0, 0.0, mass_rot)


# ---- 9. ELEMENTS ------------------------------------------------------------------------------------------------------------------------------------
def define_elements() -> None:
    """dispBeamColumn columns (4 IPs) and beams (3 IPs).

    dispBeamColumn requires beamIntegration in OpenSeesPy (unlike
    nonlinearBeamColumn which takes section + nIP directly).
    """
    # Local axes: vecxz = (1, 0, 0) for columns, (1, 1, 0) for beams
    ops.geomTransf("Linear", TRANS_COL, 1, 0, 0)
    ops.geomTransf("Linear", TRANS_BEAM, 1, 1, 0)

    ops.beamIntegration("Legendre", INTEG_COL, SEC_COL_AGG, 4)
    ops.beamIntegration("Legendre", INTEG_BEAM, SEC_BEAM, 3)

    # Columns -- 12 elements (4 columns x 3 stories)
    col_runs = [
        ( 1,  1,  5), ( 2,  2,  6), ( 3,  3,  7), ( 4,  4,  8),
        ( 5,  5, 10), ( 6,  6, 11), ( 7,  7, 12), ( 8,  8, 13),
        ( 9, 10, 15), (10, 11, 16), (11, 12, 17), (12, 13, 18),
    ]
    for ele_tag, i_node, j_node in col_runs:
        ops.element("dispBeamColumn", ele_tag, i_node, j_node,
                    TRANS_COL, INTEG_COL)

    # Beams -- 12 elements (4 beams x 3 floors, perimeter only)
    beam_runs = [
        # Floor 1
        (13,  5,  6), (14,  6,  7), (15,  7,  8), (16,  8,  5),
        # Floor 2
        (17, 10, 11), (18, 11, 12), (19, 12, 13), (20, 13, 10),
        # Floor 3
        (21, 15, 16), (22, 16, 17), (23, 17, 18), (24, 18, 15),
    ]
    for ele_tag, i_node, j_node in beam_runs:
        ops.element("dispBeamColumn", ele_tag, i_node, j_node,
                    TRANS_BEAM, INTEG_BEAM)


# ---- 10. FIBER SECTION VISUALIZATION ----------------------------------------------------------------------------------
def _vis_fiber_section(output_dir: Path) -> None:
    """Plot and save the column fiber section mesh (patch-based view)."""
    if _headless():
        return
    print("Plotting fiber section mesh ...")
    import matplotlib
    _prev = matplotlib.get_backend()
    matplotlib.use("Agg")
    import warnings
    import matplotlib.pyplot as plt
    from opstool.pre.section import plot_fiber_sec_cmds

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*non-interactive.*")
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        plot_fiber_sec_cmds(
            SEC_COL_FIBER,
            title=f"Chapter4.4 -- Column Fiber Section\n"
                  f"457.2x457.2 mm, {nf_core_y}x{nf_core_z} core mesh, "
                  f"{n_bars} bars/side (Phi25.5)",
            title_size=12,
        )
    plt.savefig(
        str(output_dir / "vis_01_fiber_section.png"),
        dpi=150, bbox_inches="tight",
    )
    plt.close()
    matplotlib.use(_prev)


# ---- 11. OUTPUT DATABASE (ODB) --------------------------------------------------------------------------------------------------------
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise ODB after model is fully built."""
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=1)
    odb.save_model_data()
    return odb


# ---- 12. LOADING ------------------------------------------------------------------------------------------------------------------------------------
def define_gravity_loads() -> None:
    """Apply vertical loads on all column nodes (Series ramp 0->2s)."""
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    column_nodes = [5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18]
    for node in column_nodes:
        ops.load(node, 0.0, 0.0, p_col, 0.0, 0.0, 0.0)


def define_ground_motion() -> tuple:
    """Define bi-directional UniformExcitation (Tabas FN in X, FP in Y).

    Returns (dt, npts).
    """
    path_x = gm_dir / gm_file_x
    path_y = gm_dir / gm_file_y
    if not path_x.exists():
        raise FileNotFoundError(f"Ground motion file not found: {path_x}")
    if not path_y.exists():
        raise FileNotFoundError(f"Ground motion file not found: {path_y}")

    accel_raw_x = np.loadtxt(path_x)
    accel_raw_y = np.loadtxt(path_y)
    npts = min(len(accel_raw_x), len(accel_raw_y), gm_npts)
    accel_x = accel_raw_x[:npts]
    accel_y = accel_raw_y[:npts]

    # Tabas FN -- X-direction
    ops.timeSeries("Path", 101, "-dt", gm_dt, "-values", *accel_x,
                   "-factor", g_accel)
    ops.pattern("UniformExcitation", 2, 1, "-accel", 101)

    # Tabas FP -- Y-direction
    ops.timeSeries("Path", 102, "-dt", gm_dt, "-values", *accel_y,
                   "-factor", g_accel)
    ops.pattern("UniformExcitation", 3, 2, "-accel", 102)

    return gm_dt, npts


# ---- 13. ANALYSIS ----------------------------------------------------------------------------------------------------------------------------------

_peak_disp_x  = 0.0
_peak_disp_y  = 0.0
_peak_shear_x = 0.0
_peak_shear_y = 0.0
_peak_uplift  = 0.0


def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 3) -> None:
    """Apply gravity loads via load-controlled static analysis."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-16, 20, 2)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.analysis("Static")

    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def _track_edps() -> None:
    """Update peak lateral displacement, base shear, and column uplift."""
    global _peak_disp_x, _peak_disp_y, _peak_shear_x, _peak_shear_y, _peak_uplift

    _peak_disp_x = max(_peak_disp_x, abs(ops.nodeDisp(19, 1)))
    _peak_disp_y = max(_peak_disp_y, abs(ops.nodeDisp(19, 2)))

    sx = sum(abs(ops.nodeReaction(n, 1)) for n in range(1, 5))
    sy = sum(abs(ops.nodeReaction(n, 2)) for n in range(1, 5))
    _peak_shear_x = max(_peak_shear_x, sx)
    _peak_shear_y = max(_peak_shear_y, sy)

    for n in range(1, 5):
        _peak_uplift = max(_peak_uplift, abs(ops.nodeReaction(n, 3)))


def run_dynamic(
    odb: "opst.post.CreateODB",
    dt: float,
    npts: int,
    odb_every_n: int = 5,
) -> None:
    """Run transient dynamic analysis with SmartAnalyze + Newmark.

    Rayleigh damping (2% on mode 1) computed from eigenvalue analysis.
    Uses gamma=0.55, beta=0.275625 (slightly damped Newmark, same as source Tcl).
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    eigenvalues = ops.eigen("-fullGenLapack", 1)
    omega1 = eigenvalues[0] ** 0.5
    T1 = 2.0 * np.pi / omega1
    f1 = 1.0 / T1
    print(f"  Mode 1: T1 = {T1:.4f} s,  f1 = {f1:.4f} Hz")

    a0 = 0.0
    a1 = 2.0 * damp_ratio / omega1
    ops.rayleigh(a0, 0.0, a1, 0.0)

    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-16, 20, 2)
    ops.algorithm("Newton")
    ops.integrator("Newmark", 0.55, 0.275625)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )

    total_steps = npts + n_steps_free
    segs = analysis.transient_split(total_steps)
    t_current = 0.0
    step_count = 0

    for i, seg in enumerate(segs):
        try:
            ok = analysis.TransientAnalyze(dt)
        except UnicodeEncodeError:
            ok = 0
        if ok < 0:
            print(f"  Dynamic analysis failed at t = {t_current:.3f} s (step {i})")
            break
        t_current += dt
        step_count += 1

        if i % odb_every_n == 0:
            odb.fetch_response_step()
            _track_edps()

    try:
        analysis.close()
    except UnicodeEncodeError:
        pass
    print(f"  Completed {step_count} steps (t_final = {t_current:.3f} s)")


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
    _vis_fiber_section(output_dir)

    odb = create_odb(output_dir)

    define_gravity_loads()
    vis_loads(output_dir)

    print("Running static preload (gravity) ...")
    run_gravity(odb, n_steps=n_steps_gravity)

    # Ground motion MUST be defined after gravity (AGENT.md S12i)
    gm_dt, gm_npts = define_ground_motion()
    vis_pre_analysis(output_dir)

    print(f"Running dynamic analysis ({gm_npts} steps, dt={gm_dt:.3f} s) ...")
    run_dynamic(odb, gm_dt, gm_npts, odb_every_n=odb_every_n)

    return odb


# ---- 14. POST-PROCESSING --------------------------------------------------------------------------------------------------------------------
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
) -> dict:
    """Flush ODB, write EDPs to JSON, and generate deformation visualizations."""
    odb.save_response()

    building_height = 3.0 * story_h

    edp_values = {
        "1-PID-1-1":  _peak_disp_x / building_height,
        "1-PID-1-2":  _peak_disp_y / building_height,
        "1-PRD-1":    _peak_disp_x,
        "1-PRD-2":    _peak_disp_y,
        "1-PFB-1":    _peak_shear_x,
        "1-PFB-2":    _peak_shear_y,
        "1-PFB-3":    _peak_uplift,
        "collapse_status": 0,
    }

    import json
    edp_file = output_dir / "EDP.json"
    edp_list = [{"name": k, "value": v} for k, v in edp_values.items()]
    with open(edp_file, "w") as f:
        json.dump({"EDP": edp_list}, f, indent=2)
    print(f"EDP file written: {edp_file}")

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


# ---- 15. MAIN ------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    edps = post_process(odb, output_dir)
    print(f"\nExtracted {len(edps)} EDPs.")
