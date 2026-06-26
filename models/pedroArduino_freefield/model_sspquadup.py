# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Effective-Stress Site Response — Layered Soil Column (SSPquadUP)
UniqueID : pedroArduino_freefield
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-06-26
Purpose  : Faithful SSPquadUP port of freeFieldEffective.tcl — 1D effective-
           stress site response of a 3-layer soil profile on a 1% slope using
           stabilized single-point quad (SSPquadUP) coupled u-p elements with
           PressureDependMultiYield02 and Lysmer dashpot base.
Ref      : McGann, Shin, Arduino, Mackenzie-Helnwein — U. Washington
           tcl_ref/freeFieldEffective.tcl
Units    : kN, m, kPa, sec  (coupled u-p — retained per source)
NOTE     : SSPquadUP arg order: matTag, thick, bulk, fmass, hPerm, vPerm,
           e0, press, bx, by  (13 args after connectivity).
           Differs from quadUP in: (a) matTag BEFORE thick, (b) extra e0 and
           press parameters, (c) no fmass gap — fmass is present in both.
           Key fix vs model.py: correct element type + arg order + PostShake.
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import sys
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import math
from pathlib import Path

# Access standards/ helpers (vis_utils, units)
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Soil materials (PDMY02) — tag = layer number (1=bottom, 2=middle, 3=top)
MAT_SOIL_1 = 1
MAT_SOIL_2 = 2
MAT_SOIL_3 = 3
NUM_LAYERS = 3

# Dashpot material (Viscous)
MAT_DASHPOT = 4

# Load patterns
PAT_GRAVITY  = 1   # unused (gravity uses Transient, no load pattern)
PAT_DYNAMIC  = 10

# Time series
TS_VELOCITY  = 11

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Units: kN, m, kPa, s (source convention for coupled u-p)

# Soil geometry
LAYER_THICK = {3: 2.0, 2: 8.0, 1: 20.0}   # top-down (m)
WATER_TABLE = 2.0                           # m below surface
SOIL_THICK  = sum(LAYER_THICK.values())     # 30 m

# Mesh — matches Tcl: nElemX=1, nNodeX=2, sElemX=0.5
N_ELEM_X, N_NODE_X = 1, 2
S_ELEM_X = 0.5                               # m
N_ELEM_Y = {3: 4, 2: 16, 1: 40}             # vertical elements per layer
S_ELEM_Y = {k: LAYER_THICK[k] / N_ELEM_Y[k] for k in range(1, 4)}

# Slope — 1% grade (matches Tcl; notebook uses 2%)
GRADE = 1.0                                   # percent
SLOPE = math.atan(GRADE / 100.0)
GRAV  = -9.81                                 # m/s²
BODY_X = GRAV * math.sin(SLOPE)               # body force X
BODY_Y = GRAV * math.cos(SLOPE)               # body force Y

# Rock / dashpot
ROCK_VS, ROCK_DEN = 700.0, 2.5                # m/s, Mg/m³
COL_AREA   = S_ELEM_X * 1.0                   # tributary area (m²)
DASHPOT_C  = ROCK_VS * ROCK_DEN * COL_AREA    # 875 kN·s/m

# Ground motion
MOTION_DT, MOTION_STEPS = 0.005, 7990

# Rayleigh damping — 2% on 0.2–20 Hz
DAMP_RATIO = 0.02
OMEGA_1 = 2.0 * math.pi * 0.2
OMEGA_2 = 2.0 * math.pi * 20.0
A0 = 2.0 * DAMP_RATIO * OMEGA_1 * OMEGA_2 / (OMEGA_1 + OMEGA_2)
A1 = 2.0 * DAMP_RATIO / (OMEGA_1 + OMEGA_2)

# Reference pressure for SSPquadUP effective-stress calculation
PRESS = 1.5e-6                                # kPa (matches Tcl source)

# PDMY02 properties per layer (1=bottom dense sand, 2=middle, 3=top loose)
SOIL = {
    3: {"rho": 1.80, "Gr": 9.0e4, "Br": 2.2e5, "phi": 32.0,
        "d1": 0.067, "d2": 0.23, "d3": 0.06, "l1": 0.27, "e0": 0.77,
        "uBulk": 5.0e-6, "vPerm": 1.0e-8, "hPerm": 1.0e-8},
    2: {"rho": 2.24, "Gr": 9.0e4, "Br": 2.2e5, "phi": 32.0,
        "d1": 0.067, "d2": 0.23, "d3": 0.06, "l1": 0.27, "e0": 0.77,
        "uBulk": 5.06e6, "vPerm": 1.0e-8, "hPerm": 1.0e-8},
    1: {"rho": 2.45, "Gr": 1.3e5, "Br": 2.6e5, "phi": 39.0,
        "d1": 0.010, "d2": 0.0, "d3": 0.35, "l1": 0.0, "e0": 0.47,
        "uBulk": 6.88e6, "vPerm": 1.0e-8, "hPerm": 1.0e-8},
}


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """PDMY02 soil + Viscous dashpot.  Tags = layer number (1,2,3)."""
    for k in range(1, 4):
        s = SOIL[k]
        ops.nDMaterial("PressureDependMultiYield02", k, 2,
            s["rho"], s["Gr"], s["Br"], s["phi"],
            0.1, 101.0, 0.5, 26.0,
            s["d1"], s["d2"], s["d3"], s["l1"],
            20.0, 5.0, 3.0, 1.0,
            0.0, s["e0"], 0.9, 0.02, 0.7, 101.0)

    ops.uniaxialMaterial("Viscous", MAT_DASHPOT, DASHPOT_C, 1)


# ── 7. NODES + 8. BOUNDARY CONDITIONS ───────────────────────────────────────
def define_nodes_and_bcs() -> tuple:
    """Generate 1-column mesh (2 nodes wide). Returns (n_total, dry_nodes,
    n_elem, n_node_per_layer)."""
    n_node_per_layer = {}
    n_tot = 0
    for k in range(1, 4):
        n_node_per_layer[k] = N_NODE_X * (N_ELEM_Y[k] + (1 if k == 3 else 0))
        n_tot += n_node_per_layer[k]

    y = 0.0
    c = 0
    dry = []
    water_y = SOIL_THICK - WATER_TABLE

    for k in range(1, 4):
        for j in range(1, n_node_per_layer[k] + 1, N_NODE_X):
            for i in range(1, N_NODE_X + 1):
                tag = j + c + i - 1
                ops.node(tag, (i - 1) * S_ELEM_X, y)
                if y >= water_y:
                    dry.append(tag)
            y += S_ELEM_Y[k]
        c += n_node_per_layer[k]

    # Base BCs — UX free, UY fixed, PWP free
    for i in range(1, N_NODE_X + 1):
        ops.fix(i, 0, 1, 0)
        if i > 1:
            ops.equalDOF(1, i, 1)  # tie UX for periodic boundary

    # Periodic BCs — tie each horizontal row
    for j in range(N_NODE_X + 1, n_tot, N_NODE_X):
        for i in range(j, j + N_NODE_X - 1):
            ops.equalDOF(j, i + 1, 1, 2)

    # Free drainage above water table (PWP = 0)
    for tag in dry:
        ops.fix(tag, 0, 0, 1)

    n_elem = sum(N_ELEM_Y[k] * N_ELEM_X for k in range(1, 4))

    return n_tot, dry, n_elem, n_node_per_layer


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(n_node_per_layer: dict) -> int:
    """Create SSPquadUP elements with correct arg order:
    (matTag, thick, bulk, fmass, hPerm, vPerm, e0, press, bx, by).

    Permeabilities are initially 1.0 m/s — updated post-gravity.
    Returns total element count.
    """
    c_e = 0
    for k in range(1, 4):
        s = SOIL[k]
        for j in range(1, N_ELEM_Y[k] + 1):
            for i_el in range(1, N_ELEM_X + 1):
                tag = N_ELEM_X * (j + c_e - 1) + i_el
                nI = N_NODE_X * (j + c_e - 1) + i_el

                # SSPquadUP: matTag, thick, bulk, fmass, hPerm, vPerm,
                #             e0, press, bx, by
                ops.element("SSPquadUP", tag,
                    nI, nI + 1, nI + N_NODE_X + 1, nI + N_NODE_X,
                    k,                                  # matTag
                    1.0,                                # thick
                    s["uBulk"],                         # bulk
                    1.0,                                # fmass
                    1.0, 1.0,                           # hPerm, vPerm (temp)
                    s["e0"],                            # e0  ← WAS MISSING
                    PRESS,                              # press  ← WAS MISSING
                    BODY_X, BODY_Y)                     # body forces
        c_e += N_ELEM_Y[k]

    n_elem = sum(N_ELEM_Y[k] * N_ELEM_X for k in range(1, 4))

    # ── Dashpot (ndf=2 section) ─────────────────────────────────────────────
    n_tot = sum(n_node_per_layer.values())
    dash_fixed = n_tot + 1
    dash_free  = n_tot + 2

    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 2)
    ops.node(dash_fixed, 0.0, 0.0)
    ops.node(dash_free,  0.0, 0.0)
    ops.fix(dash_fixed, 1, 1)
    ops.fix(dash_free,  0, 1)
    ops.equalDOF(1, dash_free, 1)
    ops.element("zeroLength", n_elem + 1, dash_fixed, dash_free,
                "-mat", MAT_DASHPOT, "-dir", 1)

    # Switch back to ndf=3 for dynamic loading
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)

    return n_elem


# ── 10. OUTPUT DATABASE ──────────────────────────────────────────────────────
def create_odb(odb_tag: int, output_dir: Path, n_elem: int) -> "opst.post.CreateODB":
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_plane_resp=True,
        plane_tags=list(range(1, n_elem + 1)),
        compute_mechanical_measures=True,
        project_gauss_to_nodes="copy",
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_dynamic_loading(velocity_file: Path) -> None:
    """Dynamic: velocity applied as force at base node 1 (UX direction)."""
    ops.timeSeries("Path", TS_VELOCITY, "-dt", MOTION_DT,
                   "-filePath", str(velocity_file), "-factor", DASHPOT_C)
    ops.pattern("Plain", PAT_DYNAMIC, TS_VELOCITY)
    ops.load(1, 1.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(n_elem: int) -> bool:
    """Gravity: elastic → plastic consolidation with Newmark Transient.

    Matches Tcl source: (1) elastic stage (stage=0) at dt=500s,
    (2) plastic stage (stage=1) at dt=1s. Base node 1 gets extra UX fixity
    during gravity for numerical stability.
    """
    # Extra base UX fixity during gravity (tcl: `fix 1 1 1 0`).
    # OpenSeesPy's fix() errors on already-constrained DOF, so release UY first.
    ops.remove("sp", 1, 2)
    ops.fix(1, 1, 1, 0)

    # Elastic stage
    for k in range(1, 4):
        ops.updateMaterialStage("-material", k, "-stage", 0)

    ops.constraints("Penalty", 1.0e14, 1.0e14)
    ops.test("NormDispIncr", 1.0e-4, 35, 1)
    ops.algorithm("Newton")
    ops.numberer("Plain")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", 5.0 / 6.0, 4.0 / 9.0)
    ops.analysis("Transient")

    ok = ops.analyze(100, 500.0)
    print(f"  Elastic gravity: ok={ok}")
    if ok != 0:
        return False

    # Plastic stage
    for k in range(1, 4):
        ops.updateMaterialStage("-material", k, "-stage", 1)

    ok = ops.analyze(100, 1.0)
    print(f"  Plastic gravity: ok={ok}")
    if ok != 0:
        return False

    # Release gravity-only base UX fixity (tcl: `remove sp 1 1`)
    ops.remove("sp", 1, 1)
    return True


def update_permeability(n_elem: int) -> None:
    """Set actual permeability values post-gravity using setParameter.

    Matches Tcl: setParameter -value $vPerm -eleRange ... vPerm
    OpenSeesPy uses -val flag (not -value).
    """
    ctr = 0
    for k in range(1, 4):
        start = ctr + 1
        end = ctr + N_ELEM_Y[k] * N_ELEM_X
        for ele in range(start, end + 1):
            ops.setParameter("-val", SOIL[k]["vPerm"], "-ele", ele, "vPerm")
            ops.setParameter("-val", SOIL[k]["hPerm"], "-ele", ele, "hPerm")
        ctr += N_ELEM_Y[k] * N_ELEM_X


def activate_postshake(n_elem: int) -> None:
    """Activate PostShake consolidation mode in PDMY02.

    Tcl: setParameter -value 0 -eleRange 1 3125 PostShake 1
    This was MISSING from model.py — critical for pore pressure dissipation
    during the post-shake consolidation phase.
    """
    for ele in range(1, n_elem + 1):
        ops.setParameter("-val", 1, "-ele", ele, "PostShake")


def _create_synthetic_velocity(filepath: Path) -> None:
    """Fallback: Ricker wavelet velocity (dt=0.005s, 7990 pts, peak 0.15 m/s).

    The Tcl source expects an external velocityHistory.in file. This generates
    a synthetic equivalent when the file is not provided.
    """
    npts, dt = MOTION_STEPS, MOTION_DT
    f_peak, t0, A = 1.5, 5.0, 0.15
    vals = []
    for i in range(npts):
        t = i * dt
        tau = t - t0
        arg = math.pi * f_peak * tau
        v = A * (1.0 - 2.0 * arg**2) * math.exp(-arg**2)
        vals.append(f"{v:.8e}")
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(" ".join(vals))


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    init_model()

    # Build
    define_materials()
    n_total, dry_nodes, n_elem, n_node_per_layer = define_nodes_and_bcs()
    print(f"Mesh: {n_elem} SSPquadUP elements, {n_total} nodes, "
          f"{len(dry_nodes)} dry")

    # V1 — Nodes + boundary conditions
    vis_nodes(output_dir)

    define_elements(n_node_per_layer)

    # V2 — Full undeformed model geometry
    vis_model(output_dir)

    # ODB
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=1,
        model_update=False,
        save_nodal_resp=True,
        save_plane_resp=True,
        plane_tags=list(range(1, n_elem + 1)),
        compute_mechanical_measures=True,
        project_gauss_to_nodes="copy",
    )
    odb.save_model_data()

    # ── Gravity ────────────────────────────────────────────────────────────
    print("\n=== Gravity ===")
    if not run_gravity(n_elem):
        print("Gravity failed.")
        exit(1)

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()

    # ── Post-gravity permeability update ───────────────────────────────────
    print("\n=== Permeability Update ===")
    update_permeability(n_elem)

    # ── Dynamic ────────────────────────────────────────────────────────────
    print("\n=== Dynamic ===")
    vel_file = output_dir.parent / "ground_motions" / "velocityHistory.in"
    if not vel_file.exists():
        print("  Generating synthetic velocity (Ricker wavelet)")
        _create_synthetic_velocity(vel_file)
    else:
        print(f"  Using existing: {vel_file}")
    define_dynamic_loading(vel_file)

    # V3 — Load vectors (dynamic base excitation)
    vis_loads(output_dir)

    # V4 — Full model + loads, final pre-analysis check
    vis_pre_analysis(output_dir)

    # CFL condition
    CFL_ok = min(S_ELEM_Y.values()) / math.sqrt(500.0)
    dT = min(MOTION_DT, CFL_ok)
    print(f"  dT={dT:.6f}s (CFL limit={CFL_ok:.6f}), {MOTION_STEPS} steps")

    ops.integrator("Newmark", 0.5, 0.25)
    ops.rayleigh(A0, A1, 0.0, 0.0)

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
    for i, _ in enumerate(segs):
        result = analysis.TransientAnalyze(dT)
        if result < 0:
            print(f"  Step {i + 1} failed")
            break
        if i % 10 == 0:
            odb.fetch_response_step()
        if (i + 1) % 1000 == 0:
            print(f"  Step {i + 1}/{MOTION_STEPS}")
    analysis.close()

    # ── Post-Shake Consolidation ───────────────────────────────────────────
    # Tcl: setParameter -value 0 -eleRange 1 3125 PostShake 1
    print("\n=== Post-Shake ===")
    activate_postshake(n_elem)

    ops.wipeAnalysis()
    damp_ps = 0.2                       # 20% damping for consolidation
    a0_ps = 2.0 * damp_ps * OMEGA_1 * OMEGA_2 / (OMEGA_1 + OMEGA_2)
    a1_ps = 2.0 * damp_ps / (OMEGA_1 + OMEGA_2)
    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", 5.0 / 6.0, 4.0 / 9.0)
    ops.rayleigh(a0_ps, a1_ps, 0.0, 0.0)
    ops.test("NormDispIncr", 1.0e-5, 35, 1)
    ops.algorithm("Newton")
    ops.analysis("Transient")

    dT_ps = 0.05
    n_ps = max(1, int((100.0 - ops.getTime()) / dT_ps))
    print(f"  {n_ps} steps @ dT={dT_ps}s")
    ops.analyze(n_ps, dT_ps)

    odb.save_response()
    print("\n=== Complete ===")

    # ── 15. POST-PROCESSING ──────────────────────────────────────────────────
    print("\n=== Post-Process ===")
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
