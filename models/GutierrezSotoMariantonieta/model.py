# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Self-Centering Post-Tensioned Steel Braced Frame with Controlled Rocking
UniqueID : GutierrezSotoMariantonieta
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-05
Purpose  : 3D non-linear dynamic analysis of a 6-story self-centering steel
           braced frame with post-tensioned (PT) rocking bays and replaceable
           fuse assemblies, subjected to scaled Kobe ground motion.
Ref      : Gutierrez-Soto, M. et al. — DREAM Structures Lab (sotostructures.com).
           Source: 13-file STKO build sequence (tcl_ref/01..13-*.py).
Units    : N, mm, MPa  (converted from source SI: m, kg, Pa — see §12j)

NOTE     : The source was the body of a parameter-sweep; the driver defining
           Section_Mat (12 cross-sections), Strand_Area, and Fuse_Yield was
           not provided. Representative AISC W-section values are used as
           placeholders — see the ASSUMED PARAMETERS block in §3. Replace
           with source data when available.
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import json
import math
import sys
from pathlib import Path

import openseespy.opensees as ops
import opstool as opst

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import m, mm, N, kN, MPa, GPa, kg, tonne
from vis_utils import (vis_nodes, vis_model, vis_loads, vis_pre_analysis, _headless)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Materials (matching source tags 201/202/203, 301, 401/414)
MAT_PT_STRAIN_1 = 201   # ElasticPP — outer PT strand
MAT_PT_STRAIN_2 = 202   # ElasticPP — inner PT strand
MAT_PT_PARALLEL = 203   # Parallel of 201 + 202
MAT_BASE_CONN   = 301   # ENT vertical-reaction spring at column base
MAT_FUSE_SC     = 401   # SelfCentering gap element (bolt connection)
MAT_FUSE_STEEL  = 414   # Steel01 fuse (Fuse A)

# Geometric transformations (source tags)
TRANSF_COL_Y = 1        # PDelta, x-axis-up — columns & braces in Y-direction
TRANSF_BM_X  = 2        # PDelta, -y-axis-up — beams & braces in X-direction

# Load patterns + time series
PAT_GRAVITY = 1
TS_GRAVITY  = 1
TS_KOBE     = 2
PAT_DYNAMIC = 2

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# All dimensional values converted SI → N-mm-MPa per AGENT.md §12j.
# Critical: never use `* Pa` or `* kg` from units.py for SI conversions
# (Pa = 1 N/mm² = 1 MPa, NOT 1 SI-Pascal; kg = 1 N·s²/mm = 1 tonne, NOT 1 kg).

# ── ASSUMED PARAMETERS (replace with source data when available) ─────────────
# Source 01-SetParameters.py referenced these but the driver defining them was
# not included in tcl_ref/. Values below are representative AISC W-section
# properties for a 6-story self-centering steel braced frame; clearly marked
# so the source data can be dropped in without touching model logic.
# ---------------------------------------------------------------------------

# Steel (from source 01-SetParameters: Esf=2.05e11 Pa, Gsf=7.93e10 Pa)
E_STEEL = 2.05e11 / 1e6 * MPa              # 205000 MPa = 205 GPa  (originally 2.05e11 Pa)
G_STEEL = 7.93e10 / 1e6 * MPa              #  79300 MPa = 79.3 GPa (originally 7.93e10 Pa)

# Geometry (from source: bw_x=bw_y=6.0 m, sh=4.0 m)
BAY_WIDTH_X = 6.0 * m                      # 6000 mm  (originally 6.0 m)
BAY_WIDTH_Y = 6.0 * m                      # 6000 mm
STORY_HEIGHT = 4.0 * m                     # 4000 mm
N_STORIES = 6

# Nodal mass (from source: M_n=24000 kg). In N-mm system, mass unit is
# N·s²/mm = tonne; 1 tonne = 1000 kg → divide by 1000 (§12j).
M_NODE = 24000.0 / 1000.0                  # 24 tonne  (originally 24000 kg)

# Gravity (9.81 m/s² → 9810 mm/s²)
G_ACCEL = 9.81 * m / 1.0                   # 9810 mm/s²  (= 9.81 m/s²)
# Gravity load per node = M_n * g  (source: ops.load(tag, 0, 0, -M_n*9.81, ...))
# In N: 24000 kg × 9.81 m/s² = 235440 N (force unit unchanged in N-mm system)
GRAV_LOAD_PER_NODE = 24000.0 * 9.81        # 235440 N  (originally M_n*9.81 in SI)

# ── ASSUMED Section properties (12 sections VS1..VS12) ───────────────────────
# Source used Section_Mat[VSn-1, j] with j ∈ {1=A, 2=Iy, 5=Iz, 9=J} in SI.
# Below: representative AISC W-sections, converted to N-mm (m²→mm², m⁴→mm⁴).
# Format: {section_id: (A_mm2, Iy_mm4, Iz_mm4, J_mm4)}
# Columns (VS1-6): W14 shapes; beams/braces (VS7-12): W24 beams, W12 braces.
SECTION = {
    # name:    (A in mm²,        Iy in mm⁴,        Iz in mm⁴,        J in mm⁴)
    "VS1":  (22800.0,    1.510e9,         5.53e8,          2.36e7),    # W14x120 col base
    "VS2":  (15100.0,    8.83e8,          3.71e8,          1.43e7),    # W14x80 col upper
    "VS3":  (22800.0,    1.510e9,         5.53e8,          2.36e7),    # W14x120 col-Y base
    "VS4":  (15100.0,    8.83e8,          3.71e8,          1.43e7),    # W14x80 col-Y upper
    "VS5":  (22800.0,    1.510e9,         5.53e8,          2.36e7),    # W14x120 col story 3
    "VS6":  (15100.0,    8.83e8,          3.71e8,          1.43e7),    # W14x80 col story 4-6
    "VS7":  (10500.0,    1.41e8,          6.24e9,          1.72e7),    # W24x55 beam floor 1
    "VS8":  (10500.0,    1.41e8,          6.24e9,          1.72e7),    # W24x55 beam floor 2
    "VS9":  (10500.0,    1.41e8,          6.24e9,          1.72e7),    # W24x55 beam floor 3-6
    "VS10": (7600.0,     7.65e7,          3.18e9,          1.23e7),    # W12x40 brace-Y
    "VS11": (7600.0,     7.65e7,          3.18e9,          1.23e7),    # W12x40 brace-Y
    "VS12": (7600.0,     7.65e7,          3.18e9,          1.23e7),    # W12x40 brace-Y
}

# Strut section (from source 01-SetParameters: AC1=0.013376 m², IC1=1.15373416e-4 m⁴)
AC1_MM2 = 0.013376 * m**2                  # 13376 mm²  (originally 0.013376 m²)
IC1_MM4 = 1.15373416e-4 * m**4             # 1.15373416e8 mm⁴

# Post-tensioning strand area (ASSUMED — 2.0e-3 m² ≈ 12 #15-mm strands)
STRAND_AREA = 2.0e-3 * m**2                # 2000 mm²  (originally 2.0e-3 m²)

# Fuse yield force (ASSUMED — 250 kN mid-range replaceable fuse)
FUSE_YIELD = 250.0e3 * N                   # 250000 N  (originally 250.0e3 N)

# Fuse stiffnesses (from source 01-SetParameters: KvA=2.99151e8 N/m)
KVA = 2.99151e8                            # N/m (kept in SI — fuse spring)
KF1A = KVA / 1000.0                        # N/m
KF2A = KVA * 1000.0                        # N/m

# Rayleigh damping (5% on modes 1 & 3)
DAMP_RATIO = 0.05
N_EIGEN_I = 1
N_EIGEN_J = 3

# Dynamic analysis
KOBE_DT = 0.02                             # s — source motion time step
KOBE_FACTOR = 0.69 * 9.81                  # source: 0.69*g (in m/s²)
ANALYSIS_DT = 0.01                         # s — source dynamic step
N_DYN_STEPS = 2500                         # source: 2500 steps
ODB_EVERY_N = 50                           # throttle ODB (§3d/§12d)

# Path to extracted source geometry (nodes, elements, BCs, masses, loads)
MODEL_DATA = Path(__file__).parent / "model_data.json"


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and create a 3D BasicBuilder with 6 DOF/node."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Define PT strand, base connection, and fuse materials.

    Source 05-Materials.py:
      201 = ElasticPP outer PT strand (E=8.78e10 Pa, epsY=0.012)
      202 = ElasticPP inner PT strand (E=9.02e10 Pa, epsY=0.0089)
      203 = Parallel(201, 202) — combined PT
      301 = ENT — stiff vertical reaction at rocking base
      401 = SelfCentering — fuse gap (bolt connection)
      414 = Steel01 — fuse yielding (Fuse A)
    """
    # PT strands — E converted Pa→MPa; strains are dimensionless (unchanged)
    ops.uniaxialMaterial("ElasticPP", MAT_PT_STRAIN_1,
                         8.7799e10 / 1e6, 0.0120, -0.0158, -0.0038)
    ops.uniaxialMaterial("ElasticPP", MAT_PT_STRAIN_2,
                         9.0201e10 / 1e6, 0.0089, -0.0127, -0.0038)
    ops.uniaxialMaterial("Parallel", MAT_PT_PARALLEL,
                         MAT_PT_STRAIN_1, MAT_PT_STRAIN_2)

    # Base connection — ENT (elastic-no-tension) for vertical reaction
    # source: ENT(301, 1.0e9) — kept dimensionless as source
    ops.uniaxialMaterial("ENT", MAT_BASE_CONN, 1.0e9)

    # Fuse: SelfCentering gap + Steel01 yielding
    # source: SelfCentering(401, Kf1A, 0, Kf1A*0.0005, 0, 0, 0.0005, 1e6)
    ops.uniaxialMaterial("SelfCentering", MAT_FUSE_SC,
                         KF1A, 0.0, KF1A * 0.0005, 0.0, 0.0, 0.0005, 1.0e6)
    # source: Steel01(414, Fuse_Yield, 373038000.0 Pa, 0.04, 0.06, 1, 0, 1)
    ops.uniaxialMaterial("Steel01", MAT_FUSE_STEEL,
                         FUSE_YIELD, 373038000.0 / 1e6, 0.04, 0.06, 1.0, 0.0, 1.0)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def _load_model_data() -> dict:
    """Load the extracted source geometry (nodes, elements, BCs, masses, loads)."""
    return json.loads(MODEL_DATA.read_text())


def define_nodes(data: dict) -> None:
    """Create all 282 nodes from extracted source coordinates (m → mm)."""
    for tag, x_m, y_m, z_m in data["nodes"]:
        ops.node(tag, x_m * m, y_m * m, z_m * m)   # m → mm


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(data: dict) -> None:
    """Apply all 46 fixities from source 03-Constraints.py.

    Three groups: full 6-DOF fixes at base/fuse/ground nodes (c1..c6 all 1),
    and rotation-only constraints (UX=1, UY=1, ROTZ=0, RX=1, RY=1, RZ=1) at
    intermediate fuse nodes.
    """
    for row in data["constraints"]:
        tag, c1, c2, c3, c4, c5, c6 = row
        ops.fix(tag, c1, c2, c3, c4, c5, c6)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_geom_transf() -> None:
    """Define the 2 PDelta transforms (source 04-GeomTrans.py).

    trans 1 = PDelta, x-up — for columns & braces in Y-direction
    trans 2 = PDelta, -y-up — for beams & braces in X-direction
    """
    ops.geomTransf("PDelta", TRANSF_COL_Y, 1.0, 0.0, 0.0)
    ops.geomTransf("PDelta", TRANSF_BM_X,  0.0, -1.0, 0.0)


def define_elements(data: dict) -> int:
    """Build all 650 elements: elasticBeamColumn + truss + twoNodeLink + zeroLength.

    Returns total element count.
    """
    n = 0
    # elasticBeamColumn (source stored raw SI values; convert here)
    # JSON tuple: (tag, ni, nj, A_m2, E_Pa, G_Pa, J_m4, Iy_m4, Iz_m4, trans)
    for tag, ni, nj, A_m2, E_Pa, G_Pa, J_m4, Iy_m4, Iz_m4, trans in (
        data["elements"]["elasticBeamColumn"]):
        ops.element("elasticBeamColumn", tag, ni, nj,
                    A_m2 * m**2,        # m² → mm²
                    E_Pa / 1e6 * MPa,   # Pa → MPa  (§12j: divide, never * Pa)
                    G_Pa / 1e6 * MPa,
                    J_m4 * m**4,        # m⁴ → mm⁴
                    Iy_m4 * m**4,
                    Iz_m4 * m**4,
                    trans)
        n += 1

    # truss (PT strands): (tag, ni, nj, A_m2, matTag=203)
    for tag, ni, nj, A_m2, mat_tag in data["elements"]["truss"]:
        ops.element("truss", tag, ni, nj, A_m2 * m**2, mat_tag)
        n += 1

    # twoNodeLink (base connection): (tag, ni, nj, mat, dir, orient[3])
    for tag, ni, nj, mat_tag, direction, orient in data["elements"]["twoNodeLink"]:
        ops.element("twoNodeLink", tag, ni, nj,
                    "-mat", mat_tag, "-dir", direction,
                    "-orient", *orient)
        n += 1

    # zeroLength (fuse pins): (tag, ni, nj, mat, dir)
    for tag, ni, nj, mat_tag, direction in data["elements"]["zeroLength"]:
        ops.element("zeroLength", tag, ni, nj, "-mat", mat_tag, "-dir", direction)
        n += 1

    return n


def define_masses(data: dict) -> None:
    """Apply nodal masses (source: M_n kg in 3 translational DOFs only).

    Convert kg → tonne (N·s²/mm) per §12j (÷1000).
    """
    for tag, mx_kg, my_kg, mz_kg in data["masses"]:
        ops.mass(tag,
                 mx_kg / 1000.0,
                 my_kg / 1000.0,
                 mz_kg / 1000.0,
                 0.0, 0.0, 0.0)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(odb_tag: int, output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB. Targeted node/frame tracking per §3d/§12d.

    Tracked nodes/elements match the source 12-Recorders.py: roof node 604,
    fuse nodes 2011/2051, PT strands 6011/6051, and the ~18 column/beam
    elements originally recorded for localForce time histories.
    """
    opst.post.set_odb_path(str(output_dir))
    # Originally-recorded nodes & elements (source 12-Recorders.py)
    key_nodes = [604, 2011, 2051]
    key_frames = [6011, 6051,                # PT strands
                  1001, 1002, 1004, 1021, 1022, 1024,    # columns
                  1201, 1202, 1204, 1221, 1222, 1224,
                  1401, 1402, 1404, 1421, 1422, 1424,
                  3101, 3102, 3104]          # beams
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=True,
        node_tags=key_nodes,
        frame_tags=key_frames,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads(data: dict) -> None:
    """Gravity: -M_n·g vertical load at every floor node (source 10-Gravity).

    Force unit is unchanged (N) in the N-mm system; only the length/time
    dimensions change. Source fz = -M_n*9.81 N stays in N.
    """
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    for tag, fx, fy, fz_N in data["gravity_loads"]:
        ops.load(tag, fx, fy, fz_N, 0.0, 0.0, 0.0)


def define_ground_motion(motion_dir: Path) -> None:
    """Define the Kobe UniformExcitation.

    Per AGENT.md §12i, ground motion MUST be defined AFTER run_gravity() so
    ops.loadConst doesn't freeze it at t≈0.

    Source 13-DynamicAnalysis.py:
      Path(2, dt=0.02, file=kobe.txt, factor=0.69*g)
      UniformExcitation(2, dir=2, -accel 2)   # dir 2 = Y in 3D? source used 2
    """
    ops.timeSeries("Path", TS_KOBE,
                   "-dt", KOBE_DT,
                   "-filePath", str(motion_dir / "kobe.txt"),
                   "-factor", KOBE_FACTOR)
    ops.pattern("UniformExcitation", PAT_DYNAMIC, 2, "-accel", TS_KOBE)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB") -> bool:
    """One-step elastic gravity (source 11-GravityAnalysis.py).

    Source uses LoadControl + Linear + 1 step. Per §3c, SmartAnalyze's
    StaticAnalyze overrides to DisplacementControl — incompatible with the
    Linear algorithm. Use the permitted LoadControl manual-loop exception.
    """
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0)
    ops.test("EnergyIncr", 1.0e-6, 100)
    ops.algorithm("Linear")
    ops.analysis("Static")
    ok = ops.analyze(1)
    odb.fetch_response_step()
    ops.loadConst("-time", 0.0)
    print(f"  Gravity (1 step, LoadControl+Linear): ok={ok}")
    return ok == 0


def _setup_rayleigh_damping() -> None:
    """Eigen-based Rayleigh damping (source 08-Rayleigh.py).

    5% on modes 1 & 3, current-K beta (KcommSwitch=1 in source).
    """
    lam = ops.eigen("-fullGenLapack", N_EIGEN_J)
    omega_i = lam[N_EIGEN_I - 1] ** 0.5
    omega_j = lam[N_EIGEN_J - 1] ** 0.5
    alpha_m = DAMP_RATIO * (2 * omega_i * omega_j) / (omega_i + omega_j)
    beta_kcomm = 2.0 * DAMP_RATIO / (omega_i + omega_j)
    ops.rayleigh(alpha_m, 0.0, 0.0, beta_kcomm)
    print(f"  Rayleigh: alphaM={alpha_m:.4e}, betaKcomm={beta_kcomm:.4e} "
          f"(T1={2*math.pi/omega_i:.3f}s, T3={2*math.pi/omega_j:.3f}s)")


def run_dynamic(odb: "opst.post.CreateODB") -> bool:
    """Transient dynamic analysis (source 13-DynamicAnalysis.py).

    Source: 2500 steps × dt=0.01, Linear algorithm, Newmark 0.5/0.25.
    Replaced raw ops.analyze() loop with SmartAnalyze (Transient).
    """
    _setup_rayleigh_damping()
    ops.wipeAnalysis()
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("Newmark", 0.5, 0.25)
    ops.analysis("Transient")
    ops.test("EnergyIncr", 1.0e-6, 100)
    ops.algorithm("Linear")

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="EnergyIncr",
        testTol=1.0e-6,
        testIterTimes=100,
        tryAlterAlgoTypes=False,    # Linear is sufficient (elastic elements)
    )
    segs = analysis.transient_split(N_DYN_STEPS)
    print(f"  Dynamic: {N_DYN_STEPS} steps @ dt={ANALYSIS_DT}s")
    for i, _ in enumerate(segs):
        ok = analysis.TransientAnalyze(ANALYSIS_DT)
        if ok < 0:
            print(f"  Step {i + 1}/{N_DYN_STEPS} failed (ok={ok}); aborting.")
            analysis.close()
            return False
        if i % ODB_EVERY_N == 0:
            odb.fetch_response_step()
        if (i + 1) % 500 == 0:
            print(f"  Step {i + 1}/{N_DYN_STEPS}")
    analysis.close()
    return True


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB and render deformed-shape HTML (peak + slider)."""
    odb.save_response()
    print("  ODB saved.")
    try:
        opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, step="absMax", defo_scale=True,
            resp_type="disp", resp_dof="UX",
        ).write_html(str(output_dir / "vis_05_peak_deformed.html"))
        print("  -> vis_05_peak_deformed.html")
    except Exception as e:
        print(f"  Skipped peak plot: {e}")
    try:
        opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, slides=True, defo_scale=True,
            resp_type="disp", resp_dof="UX",
        ).write_html(str(output_dir / "vis_06_slider.html"))
        print("  -> vis_06_slider.html")
    except Exception as e:
        print(f"  Skipped slider plot: {e}")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build the model, run gravity + dynamic, return the ODB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data = _load_model_data()

    init_model()
    define_materials()
    define_nodes(data)
    define_boundary_conditions(data)
    vis_nodes(output_dir)                                 # V1: nodes + supports
    define_geom_transf()
    n_elem = define_elements(data)
    print(f"  Mesh: {n_elem} elements, {len(data['nodes'])} nodes")
    define_masses(data)
    vis_model(output_dir)                                 # V2: full geometry

    odb = create_odb(odb_tag=1, output_dir=output_dir)

    # Gravity
    print("=== Gravity ===")
    define_gravity_loads(data)
    vis_loads(output_dir)                                 # V3: load vectors
    vis_pre_analysis(output_dir)                          # V4: pre-analysis sanity
    if not run_gravity(odb):
        print("Gravity failed.")
        return odb

    # Ground motion (defined AFTER loadConst per §12i)
    motion_dir = Path(__file__).parent / "ground_motions"
    define_ground_motion(motion_dir)

    # Dynamic
    print("=== Dynamic ===")
    run_dynamic(odb)
    return odb


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print("\n=== Complete ===")
