# ── 0. FILE HEADER ──────────────────────────────────────────────────────────────
"""
Model    : 3-Story 4-Bay Steel Moment-Resisting Frame (SAC/FEMA Phase II)
UniqueID : NEES2014
Author   : Pedram Khajehhesameddin, Purdue University (June 2014)
Date     : 2026-06-15
Purpose  : Nonlinear dynamic time-history analysis of a pre-Northridge
           steel MRF with fiber-section beam-column elements for seismic
           collapse assessment.
Ref      : FEMA-355-C, Appendix B / FEMA-440 Appendix F
Units    : N, mm, MPa  (see standards/units.py)
Notes    : Converted from NEES project Model-93 Tcl reference files.
           Original units: kips, inches, seconds.
           EDPs: PID (peak inter-story drift ratio), PFA (peak floor
           acceleration), peak roof displacement, base shear, collapse status.
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
MAT_STEEL_BEAM = 301  # Steel02 for beams   (Fy = 36 ksi)
MAT_STEEL_COL  = 501  # Steel02 for columns (Fy = 54 ksi)

# Sections (named after W-shape designation)
SEC_W14x257 = 14257   # exterior columns, 1st/4th bay
SEC_W14x311 = 14311   # interior columns, 2nd/3rd bay
SEC_W33x118 = 33118   # floor-2 beams
SEC_W30x116 = 30116   # floor-3 beams
SEC_W24x68  = 2468    # roof beams

# Geometric transformations
TRANS_PDELTA = 2

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────────
# --- Geometry (original: inches) ---
n_stories   = 3
n_bays      = 4
h_story     = 156.0 * inch                  # story height  [mm]
w_bay       = 360.0 * inch                  # bay width  [mm]

# --- W-section geometry database (only sections used by this model) ---
# Values: d, bf, tf, tw  [in] (converted to mm at point of use)
W_SECTIONS = {
    "W14x257": dict(d=16.4, bf=16.0, tf=1.89, tw=1.18),
    "W14x311": dict(d=17.1, bf=16.2, tf=2.26, tw=1.41),
    "W33x118": dict(d=32.9, bf=11.5, tf=0.74, tw=0.55),
    "W30x116": dict(d=30.0, bf=10.5, tf=0.85, tw=0.565),
    "W24x68":  dict(d=23.7, bf=8.97, tf=0.585, tw=0.415),
}

# --- Fiber discretisation ---
nfdw = 6   # fibres along web depth
nftw = 2   # fibres along web thickness
nfbf = 4   # fibres along flange width
nftf = 2   # fibres along flange thickness

# --- Material properties ---
E_steel  = 29000.0 * ksi                   # Young's modulus  [MPa]
Fy_beam  = 36.0 * ksi                      # beam yield stress  [MPa]
Fy_col   = 54.0 * ksi                      # column yield stress  [MPa]
# Steel02 hardening & cyclic params (dimensionless)
steel_b  = 3.0e-3                           # strain hardening ratio
steel_R0 = 18.0
steel_cR1 = 0.925
steel_cR2 = 0.15

# --- Mass (original: kip·s²/in per node) ---
mass_floor_node = 0.683 * kip / inch       # floors 1-2 node mass  [N·s²/mm]
mass_roof_node  = 0.740 * kip / inch       # roof node mass  [N·s²/mm]
small_mass      = 1.0e-5 * kip / inch      # small rotational mass  [N·s²/mm]

# --- Gravity loads (original: kip per node) ---
gravity_floor_cols = [13.6, 27.2, 27.2, 13.6]    # floor 1-2  [kip]
gravity_roof_cols  = [12.1, 24.2, 24.2, 12.1]    # roof  [kip]

# --- Damping ---
damp_ratio  = 0.05                         # Rayleigh damping ratio  [-]
mode_i      = 1                            # first mode for Rayleigh
mode_j      = 3                            # second mode for Rayleigh

# --- Ground motion ---
gm_dir      = Path(__file__).parent / "ground_motions"
gm_file_x   = ""                           # set to filename in ground_motions/
gm_factor   = 1.0                          # scale factor applied to record
gm_dt       = 0.01                         # time step  [s]
gm_npts     = 2000                         # number of points (synthetic default)

# --- Analysis ---
n_steps_gravity = 10
n_steps_free    = 4000                     # extra steps for free vibration tail
odb_every_n     = 5                        # throttle ODB to every Nth step
allowable_drift = 0.8                      # collapse drift ratio threshold

# --- Column / beam layout ---
# Exterior bays (1st, 4th): W14x257; interior bays (2nd, 3rd): W14x311
col_sections = [SEC_W14x257, SEC_W14x311, SEC_W14x311, SEC_W14x257]
# Beam sections per floor: floor-2 → W33x118, floor-3 → W30x116, roof(floor-4) → W24x68
beam_sections = [SEC_W33x118, SEC_W30x116, SEC_W24x68]

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────────
def init_model() -> None:
    """Initialise 2D model (ndm=2, ndf=3)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Steel02 for beams (Fy=36 ksi) and columns (Fy=54 ksi)."""
    ops.uniaxialMaterial("Steel02", MAT_STEEL_BEAM,
                         Fy_beam, E_steel, steel_b,
                         steel_R0, steel_cR1, steel_cR2)
    ops.uniaxialMaterial("Steel02", MAT_STEEL_COL,
                         Fy_col, E_steel, steel_b,
                         steel_R0, steel_cR1, steel_cR2)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────────
def _w_section_fibers(sec_tag: int, mat_tag: int, w_name: str) -> None:
    """Define a fibre-discretised W-section.

    Replicates the Wsection_S Tcl procedure: three quad patches
    (bottom flange, web, top flange) in the local y-z plane.
    """
    w = W_SECTIONS[w_name]
    d  = w["d"]  * inch
    bf = w["bf"] * inch
    tf = w["tf"] * inch
    tw = w["tw"] * inch

    dw = d - 2.0 * tf
    y1 = -d / 2.0
    y2 = -dw / 2.0
    y3 =  dw / 2.0
    y4 =  d / 2.0
    z1 = -bf / 2.0
    z2 = -tw / 2.0
    z3 =  tw / 2.0
    z4 =  bf / 2.0

    ops.section("Fiber", sec_tag)
    # bottom flange
    ops.patch("quad", mat_tag, nfbf, nftf, y1, z4, y1, z1, y2, z1, y2, z4)
    # web
    ops.patch("quad", mat_tag, nftw, nfdw, y2, z3, y2, z2, y3, z2, y3, z3)
    # top flange
    ops.patch("quad", mat_tag, nfbf, nftf, y3, z4, y3, z1, y4, z1, y4, z4)


def define_sections() -> None:
    """Define all fibre sections used in the model."""
    _w_section_fibers(SEC_W14x257, MAT_STEEL_COL,  "W14x257")
    _w_section_fibers(SEC_W14x311, MAT_STEEL_COL,  "W14x311")
    _w_section_fibers(SEC_W33x118, MAT_STEEL_BEAM, "W33x118")
    _w_section_fibers(SEC_W30x116, MAT_STEEL_BEAM, "W30x116")
    _w_section_fibers(SEC_W24x68,  MAT_STEEL_BEAM, "W24x68")


# ── 7. NODES ─────────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Create the grid of 16 nodes (4 base + 12 floor nodes, 4 bays × 4 levels).

    Node numbering: ij where i = floor (1=base, 2=floor-2, 3=floor-3, 4=roof)
    and j = bay (1-4).  Base nodes fixed in all DOFs; floors constrained by
    equalDOF in X (rigid diaphragm).
    """
    for bay in range(1, n_bays + 1):
        x_coord = (bay - 1) * w_bay
        for floor in range(1, n_stories + 2):
            y_coord = (floor - 1) * h_story
            node_tag = 10 * floor + bay
            ops.node(node_tag, x_coord, y_coord)

    # Rigid diaphragm: all nodes on the same floor share lateral displacement
    for floor in range(2, n_stories + 2):
        master = 10 * floor + 1
        for bay in range(2, n_bays + 1):
            ops.equalDOF(master, 10 * floor + bay, 1)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix all base nodes; assign lumped mass at floor nodes."""
    for bay in range(1, n_bays + 1):
        ops.fix(10 + bay, 1, 1, 1)   # base nodes: all DOFs fixed

    for floor in range(2, n_stories + 2):
        m_node = mass_roof_node if floor == n_stories + 1 else mass_floor_node
        for bay in range(1, n_bays + 1):
            ops.mass(10 * floor + bay, m_node, small_mass, small_mass)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────────
def define_elements() -> None:
    """nonlinearBeamColumn elements with 3 integration points and PDelta.

    Columns: 12 elements (3 stories × 4 bays), tag = 50xy
             where x = story (1-3), y = bay (1-4).
    Beams:   9 elements (3 floors × 3 bays), tag = 30xy
             where x = floor (2-4), y = bay (1-3).
    """
    ops.geomTransf("PDelta", TRANS_PDELTA)
    n_ip = 3

    # --- Columns ---
    for story in range(1, n_stories + 1):
        for bay in range(1, n_bays + 1):
            node_below = 10 * story + bay
            node_above = 10 * (story + 1) + bay
            ele_tag = 5000 + 10 * story + bay
            sec_tag = col_sections[bay - 1]
            ops.element("nonlinearBeamColumn", ele_tag, node_below, node_above,
                        n_ip, sec_tag, TRANS_PDELTA)

    # --- Beams ---
    for floor in range(2, n_stories + 2):
        for bay in range(1, n_bays):
            node_left  = 10 * floor + bay
            node_right = 10 * floor + bay + 1
            ele_tag = 3000 + 10 * floor + bay
            sec_tag = beam_sections[floor - 2]
            ops.element("nonlinearBeamColumn", ele_tag, node_left, node_right,
                        n_ip, sec_tag, TRANS_PDELTA)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise ODB after model is fully built."""
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=1)
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Apply floor weights as vertical nodal loads on each column."""
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)

    for floor in range(2, n_stories + 2):
        loads = gravity_roof_cols if floor == n_stories + 1 else gravity_floor_cols
        for bay in range(1, n_bays + 1):
            w = loads[bay - 1] * kip
            ops.load(10 * floor + bay, 0.0, -w, 0.0)


def _generate_synthetic_gm(dt: float, npts: int) -> np.ndarray:
    """Generate a synthetic Ricker-wavelet ground motion for testing.

    Returns acceleration in **g** units.
    """
    t = np.arange(npts) * dt
    freq = 2.0
    t0 = npts * dt / 3.0
    tau = np.pi * freq * (t - t0)
    accel_g = (1.0 - 2.0 * tau**2) * np.exp(-tau**2)
    accel_g *= 0.3 / np.max(np.abs(accel_g))
    return accel_g


def define_ground_motion() -> tuple:
    """Define UniformExcitation ground motion in X-direction.

    Returns (dt, npts) for use by the dynamic solver.
    """
    if gm_file_x:
        path_x = gm_dir / gm_file_x
        if not path_x.exists():
            raise FileNotFoundError(f"Ground motion file not found: {path_x}")
        accel = np.loadtxt(path_x)
        npts = len(accel)
        # infer dt from file (assume constant; original uses inf.txt metadata)
        dt = gm_dt
    else:
        dt = gm_dt
        npts = gm_npts
        accel = _generate_synthetic_gm(dt, npts)

    # Acceleration in g → mm/s²
    factor = gm_factor * g_accel
    ops.timeSeries("Path", 101, "-dt", dt, "-values", *accel,
                   "-factor", factor)
    ops.pattern("UniformExcitation", 2, 1, "-accel", 101)

    return dt, npts


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────────

# EDP tracking — populated during dynamic analysis
_edp_peak_drift  = {}    # key: "story-dof" → peak drift ratio
_edp_peak_accel  = {}    # key: "story-dof" → peak accel  [mm/s²]
_edp_base_shear  = {}    # key: step → total base shear (from last fetch)
_edp_roof_disp   = {}    # key: step → roof displacement
_collapse_status = "no_collapse"


def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10) -> None:
    """Apply gravity loads via load-controlled static analysis.

    Manual LoadControl loop per AGENT.md §3c exception — SmartAnalyze
    Static forcibly overrides the integrator to DisplacementControl.
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.test("NormDispIncr", 1.0e-9, 100)
    ops.algorithm("KrylovNewton")
    ops.analysis("Static")

    for _ in range(n_steps):
        ops.analyze(1)
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def _track_edps() -> None:
    """Update peak EDP values from current converged state."""
    global _collapse_status

    # --- Inter-story drift & floor acceleration ---
    for story in range(1, n_stories + 1):
        node_above = 10 * (story + 1) + 1   # bay-1 node at floor above
        node_below = 10 * story + 1         # bay-1 node at floor below

        # Drift (X-direction, DOF 1)
        d_above = ops.nodeDisp(node_above, 1)
        d_below = ops.nodeDisp(node_below, 1)
        y_above = ops.nodeCoord(node_above, 2)
        y_below = ops.nodeCoord(node_below, 2)
        drift = abs(d_above - d_below) / (y_above - y_below)
        key = f"{story}-1"
        _edp_peak_drift[key] = max(_edp_peak_drift.get(key, 0.0), drift)

        # Collapse check
        if drift >= allowable_drift:
            _collapse_status = "collapsed"

        # Acceleration at floor above (DOF 1)
        a_floor = abs(ops.nodeAccel(node_above, 1))
        _edp_peak_accel[key] = max(_edp_peak_accel.get(key, 0.0), a_floor)

    # --- Base shear ---
    shear = 0.0
    for bay in range(1, n_bays + 1):
        shear += abs(ops.nodeReaction(10 + bay, 1))
    step_key = len(_edp_base_shear)
    _edp_base_shear[step_key] = shear

    # --- Roof displacement ---
    roof_node = 10 * (n_stories + 1) + 1
    _edp_roof_disp[step_key] = abs(ops.nodeDisp(roof_node, 1))


def run_dynamic(
    odb: "opst.post.CreateODB",
    dt: float,
    npts: int,
    odb_every_n: int = 5,
) -> None:
    """Run transient dynamic analysis with SmartAnalyze + Newmark integration.

    Rayleigh damping is computed from eigenvalues of modes {mode_i, mode_j}.
    Collapse is checked at each ODB fetch point; analysis stops early if
    drift exceeds the allowable threshold.
    """
    global _collapse_status

    # --- Eigen analysis for Rayleigh damping ---
    eigenvalues = ops.eigen(mode_j)
    omega_i = eigenvalues[mode_i - 1] ** 0.5
    omega_j = eigenvalues[mode_j - 1] ** 0.5
    T1 = 2.0 * np.pi / omega_i
    Tj = 2.0 * np.pi / omega_j
    print(f"  T{mode_i} = {T1:.4f} s,  T{mode_j} = {Tj:.4f} s")

    alpha_m = 2.0 * omega_i * omega_j / (omega_i + omega_j) * damp_ratio
    beta_k  = 2.0 / (omega_i + omega_j) * damp_ratio
    # M-prop + Kinit-prop Rayleigh damping (matches original)
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

    total_steps = npts + n_steps_free
    segs = analysis.transient_split(total_steps)
    t_current = 0.0
    step_count = 0

    for i, seg in enumerate(segs):
        ok = analysis.TransientAnalyze(dt)
        if ok < 0:
            print(f"  Dynamic analysis failed at t = {t_current:.3f} s (step {i})")
            _collapse_status = "not_converged"
            break
        t_current += dt
        step_count += 1

        if i % odb_every_n == 0:
            odb.fetch_response_step()
            _track_edps()

        if _collapse_status == "collapsed":
            print(f"  COLLAPSED at t = {t_current:.3f} s (step {step_count})")
            break

    analysis.close()
    print(f"  Completed {step_count} steps (t_final = {t_current:.3f} s)")
    print(f"  Status: {_collapse_status}")


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

    print("Running gravity analysis ...")
    run_gravity(odb, n_steps=n_steps_gravity)

    # Ground motion MUST be defined after gravity because loadConst
    # kills UniformExcitation if it was defined before.
    gm_dt, gm_npts = define_ground_motion()
    vis_pre_analysis(output_dir)

    print(f"Running dynamic analysis ({gm_npts} steps, dt={gm_dt:.4f} s) ...")
    run_dynamic(odb, gm_dt, gm_npts, odb_every_n=odb_every_n)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
) -> dict:
    """Flush ODB, write EDPs to JSON, and generate deformation visualizations.

    EDPs follow SimCenter EE-UQ EDP.json convention:
      - PID (Peak Inter-story Drift ratio) for stories 1–3, DOF 1
      - PFA (Peak Floor Acceleration)     for stories 1–3, DOF 1
      - Peak Base Shear (total X-reaction at base)
      - Peak Roof Displacement (X-direction)
      - Collapse status

    Returns:
        dict mapping EDP name → value.
    """
    odb.save_response()

    # --- Assemble EDPs from tracked peak values ---
    edp_values = {}

    for story in range(1, n_stories + 1):
        drift_val = _edp_peak_drift.get(f"{story}-1", 0.0)
        accel_val = _edp_peak_accel.get(f"{story}-1", 0.0)
        edp_values[f"1-PID-{story}-1"] = drift_val
        edp_values[f"1-PFA-{story}-1"] = accel_val

    # Peak base shear
    peak_shear = max(_edp_base_shear.values()) if _edp_base_shear else 0.0
    edp_values["1-PFB-1"] = peak_shear          # Peak Force Base

    # Peak roof displacement
    peak_roof = max(_edp_roof_disp.values()) if _edp_roof_disp else 0.0
    edp_values["1-PRD-1"] = peak_roof           # Peak Roof Displacement

    # Collapse status (0 = no collapse, 1 = collapsed, -1 = not converged)
    status_map = {"no_collapse": 0, "collapsed": 1, "not_converged": -1}
    edp_values["collapse_status"] = status_map.get(_collapse_status, -1)

    # --- Write EDPs to JSON ---
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
    if _collapse_status == "collapsed":
        print("Model COLLAPSED during analysis.")
