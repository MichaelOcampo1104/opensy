# ── 0. FILE HEADER ──────────────────────────────────────────────────────────────
"""
Model    : 2D RC Portal Frame — Fiber-Section Columns + Elastic Beam (Tabas EQ)
UniqueID : XMU_Chapter4_3
Author   : XMU (Xiamen University) — Chapter 4.3 Example
Date     : 2026-06-15
Purpose  : Textbook-example dynamic time-history analysis of a single-story
           single-bay RC portal frame with fiber-section columns (Concrete01
           cover + confined core, Steel01 rebar) and elastic beam under Tabas
           earthquake (Rayleigh damping 2% on mode 1).
Ref      : XMU Finite Element Analysis course, Chapter 4.3
Units    : N, mm, MPa  (see standards/units.py)
Notes    : Converted from model.tcl.
           Original units: kN, m, kPa — converted to N, mm, MPa.
           kN→N (×1000), m→mm (×1000), kPa→MPa (÷1000).
           Fiber section: 500×500 mm column with 440×440 mm confined core,
           30 mm cover, 6×Φ25 rebar (3 top + 3 bottom).
           dispBeamColumn elements (5 IPs each) — preserved from source.
           RC fiber sections use stress-strain materials (standard ÷1000
           kPa→MPa conversion applies, unlike Aggregator force-deformation).
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────────
# Materials
MAT_CONCRETE_U  = 1   # Concrete01 — unconfined cover
MAT_CONCRETE_C  = 2   # Concrete01 — confined core
MAT_STEEL_REBAR = 3   # Steel01    — longitudinal rebar

# Sections
SEC_COL  = 1   # Fiber section for columns
SEC_BEAM = 2   # Elastic section for beam

# Nodes
NODE_L_BASE = 1
NODE_R_BASE = 2
NODE_L_TOP  = 3
NODE_R_TOP  = 4

# Elements
ELE_COL_L = 1
ELE_COL_R = 2
ELE_BEAM  = 3

# Beam integration (dispBeamColumn requires beamIntegration in OpenSeesPy)
INTEG_COL  = 1
INTEG_BEAM = 2

# Geometric transformations
TRANS_COL  = 1
TRANS_BEAM = 2

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────────
# --- Geometry (original: m) ---
frame_width  = 6.0 * m                             # bay width  [mm]
frame_height = 3.0 * m                             # column height  [mm]
n_ip         = 5                                   # integration points

# --- Column fiber-section geometry (original: m, m²) ---
col_depth  = 0.50 * m          # total section depth  [mm]  (0.50 m)
col_width  = 0.50 * m          # total section width   [mm]
core_depth = 0.44 * m          # confined core depth   [mm]  (0.44 m)
core_width = 0.44 * m          # confined core width   [mm]
cover_thk  = 0.03 * m          # cover thickness       [mm]
bar_area   = 4.91e-4 * m**2    # single bar area       [mm²] (Φ25 ≈ 491 mm²)
n_bars_top = 3
n_bars_bot = 3
bar_y_top  =  0.22 * m         # rebar y-coordinate (top)     [mm]
bar_y_bot  = -0.22 * m         # rebar y-coordinate (bottom)  [mm]
bar_z_min  = -0.22 * m         # rebar z-coordinate (left)    [mm]
bar_z_max  =  0.22 * m         # rebar z-coordinate (right)   [mm]

# --- Column materials (original: kPa — fiber stress-strain, NOT force-deformation) ---
fc_cover   = -34473.8 * kPa    # unconfined cover peak stress  [MPa]  (≈ -34.5 MPa)
epsc_cover = -0.005            # unconfined strain at peak
fcu_cover  = -24131.66 * kPa   # unconfined crushing stress    [MPa]  (≈ -24.1 MPa)
epsu_cover = -0.02             # unconfined ultimate strain

fc_core    = 27579.04 * kPa    # confined core peak stress     [MPa]  (≈ +27.6 MPa)
epsc_core  = -0.002            # confined strain at peak
fcu_core   = 0.0               # confined crushing stress
epsu_core  = -0.006            # confined ultimate strain

Fy_steel   = 248200.0 * kPa    # rebar yield strength  [MPa]  (≈ 248 MPa)
Es_steel   = 2.1e8 * kPa       # rebar elastic modulus [MPa]  (≈ 210 GPa)
steel_b    = 0.02              # strain hardening ratio

# --- Beam elastic section (original: kPa, m², m⁴) ---
E_beam = 3.0e7 * kPa           # 30000 MPa  (30 GPa)
A_beam = 0.15 * m**2           # 150000 mm²
I_beam = 4.5e-3 * m**4         # 4.5e9 mm⁴

# --- Mass (original: kN·s²/m; ×1 → N·s²/mm) ---
mass_top = 20.0                # 20 N·s²/mm = 20 tonnes per node

# --- Beam uniform load (original: kN/m; ×1 → N/mm) ---
w_beam = -65.33                # downward uniform load  [N/mm]

# --- Damping ---
damp_ratio = 0.02

# --- Ground motion ---
gm_dir    = Path(__file__).parent / "ground_motions"
gm_file_x = "tabas.txt"
gm_dt     = 0.02
gm_npts   = 1000

# --- Analysis ---
n_steps_gravity = 10
n_steps_free    = 0
odb_every_n     = 5

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────────
def init_model() -> None:
    """Initialise 2D model (ndm=2, ndf=3)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Concrete01 (cover + core) and Steel01 rebar for column fiber sections."""
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE_U,
                         fc_cover, epsc_cover, fcu_cover, epsu_cover)
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE_C,
                         fc_core, epsc_core, fcu_core, epsu_core)
    ops.uniaxialMaterial("Steel01", MAT_STEEL_REBAR,
                         Fy_steel, Es_steel, steel_b)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────────
def define_sections() -> None:
    """Fiber section for columns; Elastic section for beam."""
    # Column fiber section — 500×500 mm with 440×440 confined core
    ops.section("Fiber", SEC_COL)
    # Confined concrete core: 440×440 mm, 8×8 mesh
    ops.patch("rect", MAT_CONCRETE_C, 8, 8,
              -0.22*m, -0.22*m, 0.22*m, 0.22*m)
    # Top cover: unconfined, 500 wide × 30 thick
    ops.patch("rect", MAT_CONCRETE_U, 10, 1,
              -0.25*m, 0.22*m, 0.25*m, 0.25*m)
    # Bottom cover: unconfined
    ops.patch("rect", MAT_CONCRETE_U, 10, 1,
              -0.25*m, -0.25*m, 0.25*m, -0.22*m)
    # Left cover: unconfined, 30 wide × 440 tall
    ops.patch("rect", MAT_CONCRETE_U, 2, 1,
              -0.25*m, -0.22*m, -0.22*m, 0.22*m)
    # Right cover: unconfined
    ops.patch("rect", MAT_CONCRETE_U, 2, 1,
              0.22*m, -0.22*m, 0.25*m, 0.22*m)
    # Top rebar layer: 3 × Φ25
    ops.layer("straight", MAT_STEEL_REBAR, n_bars_top, bar_area,
              bar_y_top, bar_z_min, bar_y_top, bar_z_max)
    # Bottom rebar layer: 3 × Φ25
    ops.layer("straight", MAT_STEEL_REBAR, n_bars_bot, bar_area,
              bar_y_bot, bar_z_min, bar_y_bot, bar_z_max)

    # Beam elastic section
    ops.section("Elastic", SEC_BEAM, E_beam, A_beam, I_beam)


# ── 7. NODES ─────────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Create 4 nodes: left base, right base, left top, right top."""
    ops.node(NODE_L_BASE, 0.0, 0.0)
    ops.node(NODE_R_BASE, frame_width, 0.0)
    ops.node(NODE_L_TOP,  0.0, frame_height)
    ops.node(NODE_R_TOP,  frame_width, frame_height)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix both base nodes; lumped mass at top nodes (X direction only)."""
    ops.fix(NODE_L_BASE, 1, 1, 1)
    ops.fix(NODE_R_BASE, 1, 1, 1)
    ops.mass(NODE_L_TOP, mass_top, 0.0, 0.0)
    ops.mass(NODE_R_TOP, mass_top, 0.0, 0.0)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Two dispBeamColumn columns + one dispBeamColumn beam (Legendre, 5 IPs).

    dispBeamColumn in OpenSeesPy requires beamIntegration (unlike
    nonlinearBeamColumn which takes section + nIP directly).
    """
    ops.geomTransf("Linear", TRANS_COL)
    ops.geomTransf("Linear", TRANS_BEAM)

    ops.beamIntegration("Legendre", INTEG_COL, SEC_COL, n_ip)
    ops.beamIntegration("Legendre", INTEG_BEAM, SEC_BEAM, n_ip)

    ops.element("dispBeamColumn", ELE_COL_L,
                NODE_L_BASE, NODE_L_TOP, TRANS_COL, INTEG_COL)
    ops.element("dispBeamColumn", ELE_COL_R,
                NODE_R_BASE, NODE_R_TOP, TRANS_COL, INTEG_COL)
    ops.element("dispBeamColumn", ELE_BEAM,
                NODE_L_TOP, NODE_R_TOP, TRANS_BEAM, INTEG_BEAM)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise ODB after model is fully built."""
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=1)
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Apply uniform downward load on beam element."""
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    ops.eleLoad("-ele", ELE_BEAM, "-type", "-beamUniform", w_beam)


def define_ground_motion() -> tuple:
    """Define UniformExcitation ground motion in X-direction (Tabas).

    Returns (dt, npts).
    """
    path_x = gm_dir / gm_file_x
    if not path_x.exists():
        raise FileNotFoundError(f"Ground motion file not found: {path_x}")
    accel_raw = np.loadtxt(path_x)
    npts = min(len(accel_raw), gm_npts)
    accel = accel_raw[:npts]

    # File values in g; convert to mm/s² via g_accel
    ops.timeSeries("Path", 101, "-dt", gm_dt, "-values", *accel,
                   "-factor", g_accel)
    ops.pattern("UniformExcitation", 2, 1, "-accel", 101)

    return gm_dt, npts


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────────

_peak_disp_x  = 0.0
_peak_shear   = 0.0
_peak_uplift  = 0.0


def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10) -> None:
    """Apply gravity loads via load-controlled static analysis."""
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.test("NormDispIncr", 1.0e-8, 6)
    ops.algorithm("Newton")
    ops.analysis("Static")

    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def _track_edps() -> None:
    """Update peak lateral displacement, base shear, and column uplift."""
    global _peak_disp_x, _peak_shear, _peak_uplift

    _peak_disp_x = max(_peak_disp_x, abs(ops.nodeDisp(NODE_L_TOP, 1)))
    _peak_shear  = max(_peak_shear, abs(ops.nodeReaction(NODE_L_BASE, 1))
                       + abs(ops.nodeReaction(NODE_R_BASE, 1)))
    _peak_uplift = max(_peak_uplift,
                       abs(ops.nodeReaction(NODE_L_BASE, 2)),
                       abs(ops.nodeReaction(NODE_R_BASE, 2)))


def run_dynamic(
    odb: "opst.post.CreateODB",
    dt: float,
    npts: int,
    odb_every_n: int = 5,
) -> None:
    """Run transient dynamic analysis with SmartAnalyze + Newmark.

    Rayleigh damping (2% on mode 1) computed from eigenvalue analysis.
    """
    eigenvalues = ops.eigen(1)
    omega1 = eigenvalues[0] ** 0.5
    T1 = 2.0 * np.pi / omega1
    f1 = 1.0 / T1
    print(f"  Mode 1: T1 = {T1:.4f} s,  f1 = {f1:.4f} Hz")

    a0 = 0.0
    a1 = 2.0 * damp_ratio / omega1
    ops.rayleigh(a0, 0.0, a1, 0.0)

    ops.constraints("Plain")
    ops.numberer("Plain")
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

    total_steps = npts + n_steps_free
    segs = analysis.transient_split(total_steps)
    t_current = 0.0
    step_count = 0

    for i, seg in enumerate(segs):
        try:
            ok = analysis.TransientAnalyze(dt)
        except UnicodeEncodeError:
            # Rich progress bar emoji on Windows cp1252 consoles
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

    odb = create_odb(output_dir)

    define_gravity_loads()
    vis_loads(output_dir)

    print("Running static preload (gravity) ...")
    run_gravity(odb, n_steps=n_steps_gravity)

    # Ground motion MUST be defined after gravity (AGENT.md §12i)
    gm_dt, gm_npts = define_ground_motion()
    vis_pre_analysis(output_dir)

    print(f"Running dynamic analysis ({gm_npts} steps, dt={gm_dt:.3f} s) ...")
    run_dynamic(odb, gm_dt, gm_npts, odb_every_n=odb_every_n)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
) -> dict:
    """Flush ODB, write EDPs to JSON, and generate deformation visualizations."""
    odb.save_response()

    edp_values = {
        "1-PID-1-1":  _peak_disp_x / frame_height,
        "1-PRD-1":    _peak_disp_x,
        "1-PFB-1":    _peak_shear,
        "1-PFB-2":    _peak_uplift,
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


# ── 14. MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    edps = post_process(odb, output_dir)
    print(f"\nExtracted {len(edps)} EDPs.")
