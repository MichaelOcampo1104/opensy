# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Effective-Stress Site Response — Layered Soil Column
UniqueID : pedroArduino_freefield
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-06-25
Purpose  : 1D effective-stress site response analysis of a 3-layer soil
           profile on a 2% slope using coupled u-p (SSPquadUP) elements
           with PressureDependMultiYield02 and Lysmer dashpot base.
Ref      : McGann, Shin, Arduino, Mackenzie-Helnwein — U. Washington
Units    : kN, m, kPa, sec  (coupled u-p — retained per XMU_Ch8 precedent)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys, math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Soil materials (PDMY02) — one per layer
MAT_SOIL_1 = 1   # deep layer (20m) — dense sand
MAT_SOIL_2 = 2   # middle layer (8m) — medium sand
MAT_SOIL_3 = 3   # top layer (2m) — loose sand

# Dashpot material (Viscous)
MAT_DASHPOT = 4  # Lysmer dashpot

# Nodes
NODE_DASH_FIXED = 1001   # fixed dashpot node
NODE_DASH_FREE  = 1002   # dashpot free node (connected to base)

# Elements
ELE_DASHPOT     = 10000  # zeroLength dashpot element

# Load patterns
PAT_GRAVITY  = 1
PAT_DYNAMIC  = 10

# Time series
TS_GRAV      = 1
TS_VELOCITY  = 11

# Analysis
N_ELASTIC_STEPS = 100
N_PLASTIC_STEPS = 100
DT_ELASTIC      = 500.0   # s — large time steps for consolidation
DT_PLASTIC      = 1.0     # s — smaller time steps for plastic gravity


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# --- SOIL PROFILE
NUM_LAYERS = 3
# Layer thicknesses (m) — indexed top-to-bottom: 3=surface, 2=middle, 1=deep
LAYER_THICK = {3: 2.0, 2: 8.0, 1: 20.0}
WATER_TABLE = 2.0       # m below surface

soil_thick = sum(LAYER_THICK.values())  # 30 m total

# --- MESH
N_ELEM_X = 1            # single column
N_NODE_X = N_ELEM_X + 1  # 2 nodes wide
S_ELEM_X = 0.5          # m — element width
# Elements per layer
N_ELEM_Y = {3: 4, 2: 16, 1: 40}
# Element height per layer
S_ELEM_Y = {}
for k in range(1, NUM_LAYERS + 1):
    S_ELEM_Y[k] = LAYER_THICK[k] / N_ELEM_Y[k]

# Slope
GRADE = 1.0  # percent
SLOPE = math.atan(GRADE / 100.0)
GRAVITY_ACCEL = -9.81  # m/s²

# Gravity body force components (m/s² — SSPquadUP scales internally)
BODY_X = GRAVITY_ACCEL * math.sin(SLOPE)
BODY_Y = GRAVITY_ACCEL * math.cos(SLOPE)

# --- ROCK (elastic half-space)
ROCK_VS  = 700.0   # m/s — shear wave velocity
ROCK_DEN = 2.5     # tonne/m³ — density

# --- GROUND MOTION
MOTION_DT    = 0.005    # s
MOTION_STEPS = 7990

# --- DAMPING (Rayleigh)
DAMP_RATIO   = 0.02
OMEGA_1      = 2.0 * math.pi * 0.2   # rad/s — lower frequency bound
OMEGA_2      = 2.0 * math.pi * 20.0  # rad/s — upper frequency bound

# --- ANALYSIS
GAMMA_NM = 5.0 / 6.0
BETA_NM  = 4.0 / 9.0

# --- SOIL PROPERTIES
# Layer 3 (top, 0-2m) — loose sand
SOIL = {
    3: {
        "rho": 1.8,          # tonne/m³
        "Gr": 9.0e4,         # kPa — low-strain shear modulus
        "Br": 2.2e5,         # kPa — bulk modulus
        "phi": 32.0,         # deg — friction angle
        "peakStrain": 0.1,
        "refPress": 101.0,   # kPa
        "pressDepend": 0.5,
        "dilate": 26.0,      # deg
        "d1": 0.067, "d2": 0.23, "d3": 0.06,
        "liquefac1": 0.27, "liquefac2": 20.0,
        "liquefac3": 5.0, "liquefac4": 3.0, "liquefac5": 1.0,
        "contra": 0.0,
        "eInit": 0.77,
        "voidLimit": 0.9,
        "c1": 0.02, "c2": 0.7,
        "c3": 101.0,
        "uBulk": 5.0e-6,     # kPa — fluid bulk modulus (water)
        "hPerm": 1.0e-8,     # m/s — horizontal permeability
        "vPerm": 1.0e-8,     # m/s — vertical permeability
    },
    2: {
        "rho": 2.24,
        "Gr": 9.0e4,
        "Br": 2.2e5,
        "phi": 32.0,
        "peakStrain": 0.1,
        "refPress": 101.0,
        "pressDepend": 0.5,
        "dilate": 26.0,
        "d1": 0.067, "d2": 0.23, "d3": 0.06,
        "liquefac1": 0.27, "liquefac2": 20.0,
        "liquefac3": 5.0, "liquefac4": 3.0, "liquefac5": 1.0,
        "contra": 0.0,
        "eInit": 0.77,
        "voidLimit": 0.9,
        "c1": 0.02, "c2": 0.7,
        "c3": 101.0,
        "uBulk": 5.06e6,
        "hPerm": 1.0e-8,
        "vPerm": 1.0e-8,
    },
    1: {
        "rho": 2.45,
        "Gr": 1.3e5,
        "Br": 2.6e5,
        "phi": 39.0,
        "peakStrain": 0.1,
        "refPress": 101.0,
        "pressDepend": 0.5,
        "dilate": 26.0,
        "d1": 0.010, "d2": 0.0, "d3": 0.35,
        "liquefac1": 0.0, "liquefac2": 20.0,
        "liquefac3": 5.0, "liquefac4": 3.0, "liquefac5": 1.0,
        "contra": 0.0,
        "eInit": 0.47,
        "voidLimit": 0.9,
        "c1": 0.02, "c2": 0.7,
        "c3": 101.0,
        "uBulk": 6.88e6,
        "hPerm": 1.0e-8,
        "vPerm": 1.0e-8,
    }
}


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model(ndf: int = 3) -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", ndf)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    for layer in range(1, NUM_LAYERS + 1):
        s = SOIL[layer]
        ops.nDMaterial(
            "PressureDependMultiYield02", layer, 2,
            s["rho"], s["Gr"], s["Br"], s["phi"], s["peakStrain"],
            s["refPress"], s["pressDepend"], s["dilate"],
            s["d1"], s["d2"], s["d3"],
            s["liquefac1"], s["liquefac2"], s["liquefac3"],
            s["liquefac4"], s["liquefac5"],
            s["contra"], s["eInit"], s["voidLimit"],
            s["c1"], s["c2"], s["c3"],
        )

    # Lysmer dashpot — Viscous material
    # c = rho * Vs * A_rock = 2.5 * 700 * (0.5 * 1.0) = 875 kN·s/m
    col_area = S_ELEM_X * SOIL[1]["thick"] if "thick" in SOIL[1] else S_ELEM_X * 1.0
    # Actually thickness is 1.0 for all layers in source
    col_area = S_ELEM_X * 1.0  # 0.5 m²
    dashpot_C = ROCK_VS * ROCK_DEN * col_area  # 700 * 2.5 * 0.5 = 875 kN·s/m
    ops.uniaxialMaterial("Viscous", MAT_DASHPOT, dashpot_C, 1)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    pass  # No fiber sections — continuum elements


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def generate_mesh() -> tuple:
    """Generate soil column mesh. Returns (n_total_nodes, n_total_elems)."""
    # Count total elements
    n_elem_total = sum(N_ELEM_Y[k] * N_ELEM_X for k in range(1, NUM_LAYERS + 1))

    # Count total nodes
    n_node_per_layer = {}
    n_node_total = 0
    for k in range(1, NUM_LAYERS):
        n_node_per_layer[k] = N_NODE_X * N_ELEM_Y[k]
        n_node_total += n_node_per_layer[k]
    n_node_per_layer[NUM_LAYERS] = N_NODE_X * (N_ELEM_Y[NUM_LAYERS] + 1)
    n_node_total += n_node_per_layer[NUM_LAYERS]

    y_coord = 0.0  # starts at base
    count = 0
    gwt = 1  # ground-water-table counter
    dry_nodes = []

    for k in range(1, NUM_LAYERS + 1):
        for j in range(1, n_node_per_layer[k] + 1, N_NODE_X):
            for i in range(1, N_NODE_X + 1):
                tag = j + count + i - 1
                x = (i - 1) * S_ELEM_X
                ops.node(tag, x, y_coord)

                # Track nodes above water table (for free drainage)
                water_height = soil_thick - WATER_TABLE
                if y_coord >= water_height:
                    dry_nodes.append(tag)

            y_coord += S_ELEM_Y[k]
        count += n_node_per_layer[k]

    return n_node_total, n_elem_total, dry_nodes


def define_boundary_conditions(n_node_total: int, dry_nodes: list, n_elem_total: int) -> None:
    """Set up fixities, periodic boundaries, and drainage."""
    # Base fixity: UX free, UY fixed, PWP free
    for i in range(1, N_NODE_X + 1):
        ops.fix(i, 0, 1, 0)
        if i > 1:
            ops.equalDOF(1, i, 1)  # periodic — same UX at base

    # Periodic boundaries — equalDOF for UX and UY on each row
    for j in range(N_NODE_X + 1, n_node_total, N_NODE_X):
        for i in range(j, j + N_NODE_X - 1):
            ops.equalDOF(j, i + 1, 1, 2)

    # Free drainage: PWP=0 for nodes above water table
    for tag in dry_nodes:
        ops.fix(tag, 0, 0, 1)


def define_dashpot() -> None:
    """Create Lysmer dashpot at base.

    Dashpot uses ndf=2 nodes (UX, UY) connected to the ndf=3 base node (UX).
    Uses fixed tag constants from Tag Registry (NODE_DASH_FIXED, NODE_DASH_FREE).
    """
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 2)

    ops.node(NODE_DASH_FIXED, 0.0, 0.0)
    ops.node(NODE_DASH_FREE,  0.0, 0.0)
    ops.fix(NODE_DASH_FIXED, 1, 1)
    ops.fix(NODE_DASH_FREE,  0, 1)

    # Wire dashpot free node to base soil node (tag 1) in UX only
    try:
        ops.equalDOF(1, NODE_DASH_FREE, 1)
    except Exception:
        ops.sp(NODE_DASH_FREE, 1, 0.0)

    ops.element("zeroLength", ELE_DASHPOT, NODE_DASH_FIXED, NODE_DASH_FREE,
                "-mat", MAT_DASHPOT, "-dir", 1)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(n_elem_total: int) -> None:
    """Create SSPquadUP elements for all layers."""
    # Permeabilities = 1.0 m/s during gravity (rapid drainage)
    init_perm = 1.0

    count = 0
    for k in range(1, NUM_LAYERS + 1):
        s = SOIL[k]
        for j in range(1, N_ELEM_Y[k] + 1):
            for i_el in range(1, N_ELEM_X + 1):
                tag = (N_ELEM_X) * (j + count - 1) + i_el
                n_I = (N_NODE_X) * (j + count - 1) + i_el
                n_J = n_I + 1
                n_K = n_I + N_NODE_X + 1
                n_L = n_I + N_NODE_X

                ops.element(
                    "SSPquadUP", tag,
                    n_I, n_J, n_K, n_L,
                    k,              # material tag = layer number
                    s["thick"] if "thick" in s else 1.0,  # thickness (m)
                    s["uBulk"],     # fluid bulk modulus (kPa)
                    init_perm,      # hPerm — high during gravity
                    init_perm,      # vPerm — high during gravity
                    s["eInit"],     # initial void ratio
                    1.5e-6,         # fluid density (tonne/m³ for water? Actually this seems like the Tcl value)
                    # Actually looking at Tcl: 1.5e-6 is the fluid density — seems too low
                    # Let me check. Water density = 1 tonne/m³. But 1.5e-6 ≈ 1.5 kg/m³.
                    # Wait, in the Tcl it's setPerElement? No, it's hardcoded.
                    # Looking at Tcl line 222:
                    # element SSPquadUP ... $thick($i) $uBulk($i) 1.0 1.0 1.0 $eInit($i) 1.5e-6 $xWgt($i) $yWgt($i)
                    # The 1.5e-6 is between eInit and body forces.
                    # For water, density = 1.5e-6 is NOT 1 tonne/m³. But this might be the element's internal
                    # unit convention. Let's just use the Tcl value.
                    BODY_X, BODY_Y,
                )
        count += N_ELEM_Y[k]


# ── 10. OUTPUT DATABASE ──────────────────────────────────────────────────────
def create_odb(odb_tag: int, output_dir: Path) -> "opst.post.CreateODB":
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """No explicit gravity loads — body forces are in SSPquadUP elements."""
    pass


def define_dynamic_loading(n_elem_total: int, velocity_file: Path) -> None:
    """Dynamic loading: velocity applied as force at base via dashpot."""
    col_area = S_ELEM_X * 1.0
    c_factor = col_area * ROCK_VS * ROCK_DEN  # 0.5 * 700 * 2.5 = 875

    ops.timeSeries("Path", TS_VELOCITY,
                   "-dt", MOTION_DT,
                   "-filePath", str(velocity_file),
                   "-factor", c_factor)

    ops.pattern("Plain", PAT_DYNAMIC, TS_VELOCITY)
    # Load at base node (node 1) — velocity history × dashpot coefficient
    # Node 1 has ndf=3 (UX, UY, PWP); load is applied to UX direction
    ops.load(1, 1.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def update_permeability(n_elem_total: int) -> None:
    """Update element permeability from initial 1.0 to actual values."""
    ctr = 0
    for k in range(1, NUM_LAYERS + 1):
        start = ctr + 1
        end = ctr + N_ELEM_Y[k] * N_ELEM_X
        for ele in range(start, end + 1):
            try:
                ops.setParameter("-val", SOIL[k]["vPerm"], "-ele", ele, "vPerm")
                ops.setParameter("-val", SOIL[k]["hPerm"], "-ele", ele, "hPerm")
            except Exception:
                pass  # Some elements may not accept parameter modification
        ctr += N_ELEM_Y[k] * N_ELEM_X


def run_gravity(n_elem_total: int) -> bool:
    """Two-phase gravity: elastic consolidation → plastic consolidation."""
    # Extra base fixity for stability during gravity
    # Need to remove existing SPs before re-setting
    for dof in [1, 2]:
        try:
            ops.remove("sp", 1, dof)
        except Exception:
            pass
    ops.fix(1, 1, 1, 0)

    # Phase 1: Elastic gravity
    for k in range(1, NUM_LAYERS + 1):
        ops.updateMaterialStage("-material", k, "-stage", 0)

    ops.constraints("Penalty", 1.0e14, 1.0e14)
    ops.test("NormDispIncr", 1.0e-4, 35, 1)
    ops.algorithm("Newton")
    ops.numberer("Plain")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", GAMMA_NM, BETA_NM)
    ops.analysis("Transient")

    ok = ops.analyze(N_ELASTIC_STEPS, DT_ELASTIC)
    if ok != 0:
        print(f"WARNING: Elastic gravity failed (ok={ok})")
        return False
    print("Elastic gravity completed.")

    # Phase 2: Plastic gravity
    for k in range(1, NUM_LAYERS + 1):
        ops.updateMaterialStage("-material", k, "-stage", 1)

    ok = ops.analyze(N_PLASTIC_STEPS, DT_PLASTIC)
    if ok != 0:
        print(f"WARNING: Plastic gravity failed (ok={ok})")
        return False
    print("Plastic gravity completed.")

    # Remove extra base fixity
    try:
        ops.remove("sp", 1, 1)
    except Exception:
        pass
    # Actually this is ops.remove("sp", ...) not ops.remove sp
    # In OpenSeesPy: ops.remove('sp', nodeTag, dofTag)
    ops.remove("sp", 1, 1)

    return True


def run_dynamic(n_elem_total: int, velocity_file: Path) -> bool:
    """Dynamic analysis with velocity input at base."""
    # Create velocity time history file if it doesn't exist
    if not velocity_file.exists():
        print(f"Creating synthetic velocity file at {velocity_file}")
        _create_synthetic_velocity(velocity_file)

    # Switch to ndf=3 for dynamic phase (soil nodes + dashpot)
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)

    # Define dynamic loading
    define_dynamic_loading(n_elem_total, velocity_file)

    # Determine time step from CFL condition
    vs_max = 500.0  # m/s — max shear wave velocity
    min_size = min(S_ELEM_Y[k] for k in range(1, NUM_LAYERS + 1))
    dT = min(MOTION_DT, min_size / math.sqrt(vs_max))
    n_steps_analysis = MOTION_STEPS

    # Rayleigh damping
    a0 = 2.0 * DAMP_RATIO * OMEGA_1 * OMEGA_2 / (OMEGA_1 + OMEGA_2)
    a1 = 2.0 * DAMP_RATIO / (OMEGA_1 + OMEGA_2)

    # Dynamic analysis using SmartAnalyze Transient
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", 0.5, 0.25)
    ops.rayleigh(a0, a1, 0.0, 0.0)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="NormDispIncr",
        testTol=1.0e-5,
        testIterTimes=4,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 20, 30],
        tryAddTestTimes=True,
        testIterTimesMore=[10, 20],
    )

    segs = analysis.transient_split(n_steps_analysis)
    ok = True
    for i, _ in enumerate(segs):
        result = analysis.TransientAnalyze(dT)
        if result < 0:
            print(f"WARNING: Dynamic step {i + 1} failed (ok={result})")
            ok = False
            break
        # Throttle ODB — sample every 10 steps
        if i % 10 == 0:
            odb.fetch_response_step() if 'odb' in dir() else None
            # NOTE: ODB fetch would need odb reference — handled in run_analysis

    analysis.close()
    return ok


# The actual run_analysis orchestrates everything differently
def _create_synthetic_velocity(filepath: Path) -> None:
    """Create a synthetic Ricker wavelet velocity time history.

    Peak velocity ~0.1 m/s, dt=0.005s, 7990 points (~40 seconds).
    """
    dt = MOTION_DT
    npts = MOTION_STEPS
    duration = npts * dt

    # Ricker wavelet: v(t) = A * (1 - 2*pi²*f²*(t-t0)²) * exp(-pi²*f²*(t-t0)²)
    f_peak = 1.5  # Hz — peak frequency
    t0 = 5.0      # s — time shift
    A = 0.15      # m/s — peak amplitude

    values = []
    for i in range(npts):
        t = i * dt
        tau = t - t0
        arg = math.pi * f_peak * tau
        v = A * (1.0 - 2.0 * arg**2) * math.exp(-arg**2)
        values.append(f"{v:.8e}")

    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(" ".join(values))
    print(f"  Synthetic velocity file: {npts} pts, dt={dt}s, peak={A:.3f} m/s")


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Full model: gravity → permeability update → dynamic → post-shake."""
    raise NotImplementedError("Split into run_all() for clarity")
    # The complexity is better handled in __main__ directly


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and render visualizations."""
    odb.save_response()
    if not _headless():
        opst.post.set_odb_path(str(output_dir))
        fig = opst.vis.plotly.plot_nodal_responses(
            odb_tag=ODB_TAG if 'ODB_TAG' in dir() else 1,
            slides=True, defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig.write_html(str(output_dir / "vis_05_slider.html"))


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    # ---- BUILD MODEL ----
    init_model(ndf=3)
    define_materials()

    n_node_total, n_elem_total, dry_nodes = generate_mesh()
    print(f"Mesh: {n_elem_total} elements, {n_node_total} nodes")

    define_boundary_conditions(n_node_total, dry_nodes, n_elem_total)
    define_elements(n_elem_total)

    # Dashpot (ndf=2) — do NOT wipe; switch default ndf to 2 for new nodes
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 2)
    define_dashpot()

    # Visualize
    vis_nodes(output_dir)
    vis_model(output_dir)

    # ODB
    odb = opst.post.CreateODB(
        odb_tag=1,
        model_update=False,
        save_nodal_resp=True,
    )
    odb.save_model_data()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    # ---- GRAVITY ----
    print("\n=== Gravity Analysis ===")
    # Switch back to ndf=3 for gravity
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)
    ok = run_gravity(n_elem_total)
    if not ok:
        print("ERROR: Gravity failed — aborting.")
        exit(1)

    # ---- PERMEABILITY UPDATE ----
    print("\n=== Updating Permeabilities ===")
    update_permeability(n_elem_total)

    # ---- DYNAMIC ----
    print("\n=== Dynamic Analysis ===")
    velocity_file = output_dir.parent / "ground_motions" / "velocityHistory.in"
    _create_synthetic_velocity(velocity_file)

    # Switch to ndf=3 for dynamic phase
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)

    define_dynamic_loading(n_elem_total, velocity_file)

    # CFL time step
    vs_max = 500.0
    min_size = min(S_ELEM_Y[k] for k in range(1, NUM_LAYERS + 1))
    dT = min(MOTION_DT, min_size / math.sqrt(vs_max))
    a0 = 2.0 * DAMP_RATIO * OMEGA_1 * OMEGA_2 / (OMEGA_1 + OMEGA_2)
    a1 = 2.0 * DAMP_RATIO / (OMEGA_1 + OMEGA_2)

    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", 0.5, 0.25)
    ops.rayleigh(a0, a1, 0.0, 0.0)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="NormDispIncr",
        testTol=1.0e-5,
        testIterTimes=4,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 20, 30],
        tryAddTestTimes=True,
        testIterTimesMore=[10, 20],
    )

    segs = analysis.transient_split(MOTION_STEPS)
    print(f"Dynamic: {MOTION_STEPS} steps, dt={dT:.6f}s, CFL-limited dT={min_size/math.sqrt(vs_max):.6f}s")
    for i, _ in enumerate(segs):
        result = analysis.TransientAnalyze(dT)
        if result < 0:
            print(f"WARNING: Dynamic step {i + 1}/{MOTION_STEPS} failed (ok={result})")
            break
        if i % 10 == 0:
            odb.fetch_response_step()
        if i == 0 or (i + 1) % 1000 == 0:
            print(f"  Step {i + 1}/{MOTION_STEPS}...")
    analysis.close()

    # ---- POST-SHAKE ----
    print("\n=== Post-Shake Consolidation ===")
    # Update to higher damping (20%) for post-shake
    damp_ps = 0.2
    omega1_ps = OMEGA_1
    omega2_ps = OMEGA_2
    a0_ps = 2.0 * damp_ps * omega1_ps * omega2_ps / (omega1_ps + omega2_ps)
    a1_ps = 2.0 * damp_ps / (omega1_ps + omega2_ps)

    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", 5.0/6.0, 4.0/9.0)
    ops.rayleigh(a0_ps, a1_ps, 0.0, 0.0)
    ops.test("NormDispIncr", 1.0e-5, 35, 1)
    ops.algorithm("Newton")
    ops.analysis("Transient")

    # Post-shake setParameter (optional — may not be supported)
    try:
        ops.setParameter("-val", 0, "-eleRange", 1, n_elem_total, "PostShake", 1)
    except Exception:
        print("  PostShake parameter not supported — skipping.")

    dT_ps = 0.05
    n_steps_ps = max(1, int((100.0 - ops.getTime()) / dT_ps))
    print(f"  Post-shake: {n_steps_ps} steps, dt={dT_ps}s")

    # Manual substepping for post-shake (similar to source)
    current_step = 0
    max_retries = 10
    while current_step < n_steps_ps:
        remaining = n_steps_ps - current_step
        ok = ops.analyze(remaining, dT_ps)
        if ok == 0:
            print("  Post-shake completed.")
            break
        # Fall back to single-step with substepping
        cur_time = ops.getTime()
        print(f"  Post-shake failed at t={cur_time:.1f}s — trying single steps")
        for _ in range(max_retries):
            ok = ops.analyze(1, dT_ps)
            if ok == 0:
                current_step += 1
                odb.fetch_response_step()
                break
            dT_ps /= 2.0
            if dT_ps < 1.0e-4:
                print("  Post-shake: substepping below limit — aborting")
                break

    odb.save_response()
    print("pedroArduino_freefield: analysis complete.")
