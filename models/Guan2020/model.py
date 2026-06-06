# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Single-story single-bay 2D steel SMF with leaning column (Building 10)
UniqueID : Guan2020
Author   : Xingquan Guan, Henry Burton, Mehrdad Shokrabadi (2020),
           ported by OpenSeesPy Standardisation Agent
Date     : 2026-06-06
Purpose  : Eigenvalue analysis and pushover of a 2D steel special moment frame
           with leaning column.  Part of a database of 621 SMF buildings.
Ref      : Guan, X., Burton, H., Shokrabadi, M. (2020). "A Database of Seismic
           Designs, Nonlinear Models, and Seismic Responses for Steel Moment
           Resisting Frame Buildings." DesignSafe-CI, DOI: 10.17603/ds2-8yc7-1285.
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo, vis_anim


# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────

# Geometric transformations
TRANS_PDELTA = 1   # PDelta for columns and leaning column
TRANS_LINEAR = 2   # Linear for beams

# Materials
MAT_TRUSS_RIGID = 60000     # Rigid truss material
MAT_STIFF       = 1200      # Very stiff elastic (rigid links)
MAT_SOFT        = 1300      # Very soft elastic (pin connections)

# Nodes
NODE_COL1_BASE  = 111       # Exterior column base (left)
NODE_COL2_BASE  = 211       # Interior column base (right)
NODE_COL1_ROOF  = 121       # Exterior column roof (left)
NODE_COL2_ROOF  = 221       # Interior column roof (right)
NODE_LEAN_BASE  = 31        # Leaning column base
NODE_LEAN_ROOF  = 32        # Leaning column roof
NODE_LEAN_MID   = 322       # Leaning column intermediate node (below roof)

# Elements
ELE_COL1        = 3111121   # Exterior column
ELE_COL2        = 3211221   # Interior column
ELE_BEAM         = 2121221  # Roof beam
ELE_LEAN_COL    = 331322    # Leaning column (elastic)
ELE_LEAN_SPRING = 32322     # Leaning column top spring
ELE_TRUSS       = 222132    # Truss connecting frame to leaning column

# Load patterns
PATTERN_DEAD    = 101       # Dead load
PATTERN_LIVE    = 102       # Live load
PATTERN_EQ      = 103       # Earthquake lateral load
PATTERN_GRAV_EQ = 104       # Gravity + Earthquake combined


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────

# --- Section property database (AISC, imperial → N-mm) ---
# Returns: (name, d, A, bf, tw, tf, Ix, Iy, Zx, Zy, ry, J)
# All values converted from inches/kips to N-mm
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

# AISC nominal properties (imperial) → converted via _wf()
SECTION_DB = {
    "W14X370": _wf(17.9, 109.0, 16.5, 1.66, 2.66, 5440, 831, 672, 260, 2.78, 99.2),
    "W14X455": _wf(19.1, 134.0, 17.0, 2.02, 3.21, 7190, 1100, 847, 329, 2.89, 158.0),
    "W36X160": _wf(36.0, 47.0,  12.0, 0.650, 1.02, 9760, 295, 596, 74.2, 2.50, 17.2),
}

def section_property(name: str) -> tuple:
    """Return section property tuple: (d, A, bf, tw, tf, Ix, Iy, Zx, Zy, ry, J)."""
    return SECTION_DB[name]

# --- Geometry (converted from inches) ---
bay_width    = 20.00 * ft     # 20 ft → 6096 mm
h_first      = 19.50 * ft     # 19.5 ft → 5943.6 mm
h_typical    = 13.00 * ft     # 13 ft → 3962.4 mm (not used, single-story)

# --- Steel material properties (converted from ksi) ---
Es = 29000.0 * ksi            # 29000 ksi → ~200,000 MPa
Gs = 11500.0 * ksi            # 11500 ksi → ~79,290 MPa

# Extract section properties
col_ext    = section_property("W14X370")   # Exterior column
col_int    = section_property("W14X455")   # Interior column (not used in this model)
beam_prop  = section_property("W36X160")   # Beam
# Unpack: indices: 0=d, 1=A, 2=bf, 3=tw, 4=tf, 5=Ix, 6=Iy, 7=Zx, 8=Zy, 9=ry, 10=J
col_ext_A  = col_ext[1]       # Area
col_ext_Ix = col_ext[5]       # Strong-axis I
beam_A     = beam_prop[1]     # Area
beam_Ix    = beam_prop[5]     # Strong-axis I

# --- Rigid link properties ---
A_rigid = 200000000.0 * inch**2   # Very large area
I_rigid = 9000000000.0 * inch**4  # Very large inertia
rigid_E = 1.0 * MPa               # Dummy E for rigid truss (not used, truss uses mat tag)

# --- Stiff/soft materials ---
large_stiff = 1.0e12 * ksi        # Very stiff
negligible_val = 1.0e-12 * ksi    # Very soft (≈ 0)

# --- Gravity (inch/s² → mm/s²) ---
g_accel_in = 386.09 * inch / sec**2   # 386.09 in/s² → 9806.7 mm/s²

# --- Masses and loads (converted from kips) ---
floor2_weight      = 1800.00 * kip           # 1800 kip total floor weight
tributary_mass_ratio = 0.5                    # Frame takes 50%
nodes_per_floor    = 3                        # 121, 221, 32
nodal_mass_floor2  = (floor2_weight * tributary_mass_ratio
                      / nodes_per_floor / g_accel_in)

# Uniform beam loads (kip/in → N/mm)
beam_dead_load = 0.066667 * (kip / inch)      # 0.066667 kip/in
beam_live_load = 0.041667 * (kip / inch)      # 0.041667 kip/in

# Leaning column point loads (kip → N)
lean_dead_load = 900.0 * kip                  # 900 kip
lean_live_load = 562.5 * kip                 # 562.5 kip

# Lateral earthquake load (kip → N)
lateral_eq_load = 159.952126 * kip            # 159.95 kip

# Load combination factors for pattern 104 (Gravity + EQ)
combo_dead_factor  = 1.2 + 0.2 * 1.50        # = 1.5
combo_live_factor  = 0.5

# --- Analysis ---
n_steps_gravity = 10
pushover_target_drift = 0.05                   # 5% drift
pushover_dmax = pushover_target_drift * h_first
pushover_max_step = pushover_dmax / 200.0
pushover_ref_load = lateral_eq_load            # Use EQ load pattern as reference

# --- Eigenvalue ---
n_eigen_modes = 3


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────

def init_model() -> None:
    """Wipe any existing model and create a 2D-3DOF BasicBuilder."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────

def define_materials() -> None:
    """Define stiff/soft elastic materials for rigid links and springs."""
    ops.uniaxialMaterial("Elastic", MAT_STIFF, large_stiff)
    ops.uniaxialMaterial("Elastic", MAT_SOFT, negligible_val)
    # Rigid truss material (E = 1.0, very small — truss stiffness comes from A_rigid)
    ops.uniaxialMaterial("Elastic", MAT_TRUSS_RIGID, 1.0)


# ── 6. GEOMETRIC TRANSFORMATIONS ────────────────────────────────────────────

def define_transformations() -> None:
    """Define PDelta (columns) and Linear (beams) transformations."""
    ops.geomTransf("PDelta", TRANS_PDELTA)
    ops.geomTransf("Linear", TRANS_LINEAR)


# ── 7. NODES ─────────────────────────────────────────────────────────────────

def define_nodes() -> None:
    """Create all frame and leaning column nodes.

    Node layout (2D, Y-up):
      (0, h_first) 121 ───beam─── 221 (bay_width, h_first)
                    │            │
                    │col1        │col2
                    │            │
      (0, 0)       111          211 (bay_width, 0)

      Leaning column:
        31 @ (2*bay_width, 0)           — base
       322 @ (2*bay_width, h_first)     — below roof
        32 @ (2*bay_width, h_first)     — roof level
    """
    # Frame corners
    ops.node(NODE_COL1_BASE, 0.0, 0.0)                          # 111
    ops.node(NODE_COL2_BASE, bay_width, 0.0)                     # 211
    ops.node(NODE_COL1_ROOF, 0.0, h_first)                       # 121
    ops.node(NODE_COL2_ROOF, bay_width, h_first)                  # 221

    # Leaning column
    ops.node(NODE_LEAN_BASE, 2.0 * bay_width, 0.0)               # 31
    ops.node(NODE_LEAN_ROOF, 2.0 * bay_width, h_first)            # 32
    ops.node(NODE_LEAN_MID,  2.0 * bay_width, h_first)            # 322 (coincident with 32)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────

def define_boundary_conditions() -> None:
    """Apply base fixity and floor diaphragm constraints."""
    # Column bases: fully fixed
    ops.fix(NODE_COL1_BASE, 1, 1, 1)
    ops.fix(NODE_COL2_BASE, 1, 1, 1)
    # Leaning column base: fixed in X, Y; free in RZ (pin)
    ops.fix(NODE_LEAN_BASE, 1, 1, 0)

    # Floor constraint: equal X displacement at roof level
    ops.equalDOF(NODE_COL1_ROOF, NODE_COL2_ROOF, 1)   # 121 ↔ 221
    ops.equalDOF(NODE_COL1_ROOF, NODE_LEAN_ROOF, 1)   # 121 ↔ 32


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────

def define_elements() -> None:
    """Define elastic beam-columns, truss, and leaning column spring.

    Elements:
      - Exterior column (3111121):  111 → 121  (W14×370)
      - Interior column (3211221):  211 → 221  (W14×370 — same as exterior in this model)
      - Beam (2121221):            121 → 221  (W36×160)
      - Leaning column (331322):    31 → 322  (rigid elastic)
      - Leaning spring (32322):    32 ↔ 322  (zeroLength: stiff UX/UY, soft RZ)
      - Truss (222132):           221 → 32   (rigid, transfers lateral disp.)
    """
    # Frame columns (both use exterior section per the original model)
    ops.element("elasticBeamColumn", ELE_COL1,
                NODE_COL1_BASE, NODE_COL1_ROOF,
                col_ext_A, Es, col_ext_Ix, TRANS_PDELTA)
    ops.element("elasticBeamColumn", ELE_COL2,
                NODE_COL2_BASE, NODE_COL2_ROOF,
                col_ext_A, Es, col_ext_Ix, TRANS_PDELTA)

    # Roof beam
    ops.element("elasticBeamColumn", ELE_BEAM,
                NODE_COL1_ROOF, NODE_COL2_ROOF,
                beam_A, Es, beam_Ix, TRANS_LINEAR)

    # Leaning column (rigid elastic element)
    ops.element("elasticBeamColumn", ELE_LEAN_COL,
                NODE_LEAN_BASE, NODE_LEAN_MID,
                A_rigid, Es, I_rigid, TRANS_PDELTA)

    # Leaning column top spring (zeroLength, 2D: DOF 1=UX, 2=UY, 3=RZ)
    # Stiff in UX and UY (transfers load), soft in RZ (pin behavior)
    ops.element("zeroLength", ELE_LEAN_SPRING,
                NODE_LEAN_ROOF, NODE_LEAN_MID,
                "-mat", MAT_STIFF, MAT_STIFF, MAT_SOFT,
                "-dir", 1, 2, 3)

    # Truss connecting frame to leaning column (transfers lateral displacement)
    ops.element("truss", ELE_TRUSS,
                NODE_COL2_ROOF, NODE_LEAN_ROOF,
                A_rigid, MAT_TRUSS_RIGID)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────

def create_odb(output_dir: Path, odb_tag: int = 1) -> "opst.post.CreateODB":
    """Initialise ODB and snapshot model geometry."""
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=odb_tag)
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────

def define_masses() -> None:
    """Apply nodal masses at roof level."""
    ops.mass(NODE_COL1_ROOF, nodal_mass_floor2, negligible_val, negligible_val)
    ops.mass(NODE_COL2_ROOF, nodal_mass_floor2, negligible_val, negligible_val)
    ops.mass(NODE_LEAN_ROOF, nodal_mass_floor2, negligible_val, negligible_val)


def define_dead_loads() -> None:
    """Pattern 101 — Dead load (Constant time series)."""
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", PATTERN_DEAD, 1)
    ops.eleLoad("-ele", ELE_BEAM, "-type", "-beamUniform", -beam_dead_load, 0.0)
    ops.load(NODE_LEAN_ROOF, 0.0, -lean_dead_load, 0.0)


def define_live_loads() -> None:
    """Pattern 102 — Live load (Constant time series)."""
    ops.timeSeries("Constant", 2)
    ops.pattern("Plain", PATTERN_LIVE, 2)
    ops.eleLoad("-ele", ELE_BEAM, "-type", "-beamUniform", -beam_live_load, 0.0)
    ops.load(NODE_LEAN_ROOF, 0.0, -lean_live_load, 0.0)


def define_eq_loads() -> None:
    """Pattern 103 — Earthquake lateral load (Linear time series)."""
    ops.timeSeries("Linear", 3)
    ops.pattern("Plain", PATTERN_EQ, 3)
    ops.load(NODE_COL1_ROOF, lateral_eq_load, 0.0, 0.0)


def define_gravity_eq_loads() -> None:
    """Pattern 104 — Gravity + Earthquake combined (Constant time series)."""
    ops.timeSeries("Constant", 4)
    ops.pattern("Plain", PATTERN_GRAV_EQ, 4)
    beam_comb = -(combo_dead_factor * beam_dead_load
                  + combo_live_factor * beam_live_load)
    lean_comb = -(combo_dead_factor * lean_dead_load
                  + combo_live_factor * lean_live_load)
    ops.eleLoad("-ele", ELE_BEAM, "-type", "-beamUniform", beam_comb, 0.0)
    ops.load(NODE_LEAN_ROOF, 0.0, lean_comb, 0.0)
    ops.load(NODE_COL1_ROOF, lateral_eq_load, 0.0, 0.0)


# ── 12. EIGENVALUE ANALYSIS ──────────────────────────────────────────────────

def run_eigenvalue(output_dir: Path) -> list:
    """Run eigenvalue analysis and write periods to file.

    Returns:
        List of modal periods [T1, T2, T3, ...].
    """
    eigenvalues = ops.eigen(n_eigen_modes)
    periods = [2.0 * np.pi / (lam**0.5) for lam in eigenvalues]

    eigen_dir = output_dir / "EigenAnalysisOutput"
    eigen_dir.mkdir(parents=True, exist_ok=True)

    # Write periods
    with open(eigen_dir / "Periods.out", "w") as f:
        for T in periods:
            f.write(f"{T:.6f}\n")

    print(f"Eigenvalue analysis complete. T1 = {periods[0]:.4f} s")
    return periods


# ── 13. ANALYSIS ─────────────────────────────────────────────────────────────

def run_gravity(odb: "opst.post.CreateODB", n_steps: int = n_steps_gravity) -> None:
    """Apply dead + live gravity loads incrementally (LoadControl).

    Uses the permitted SmartAnalyze exception for load-controlled static
    analysis (AGENT.md §3c).
    """
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


def run_pushover(
    odb: "opst.post.CreateODB",
    ctrl_node: int,
    ctrl_dof: int,
    target_disp: float,
    max_step: float,
) -> None:
    """Run displacement-controlled pushover using SmartAnalyze (Static)."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50, 60],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-4,
    )
    protocol = [target_disp]
    segs = analysis.static_split(protocol, maxStep=max_step)
    for seg in segs:
        analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
        odb.fetch_response_step()
    analysis.close()


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + eigenvalue + pushover, return ODB.

    Analysis sequence:
      1. Apply dead load (pattern 101) — LoadControl
      2. Freeze dead, apply live (pattern 102) — LoadControl
      3. Freeze all gravity, run eigenvalue
      4. Pushover with EQ load pattern as reference (pattern 103)

    Returns:
        Populated CreateODB instance for post-processing.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials()
    define_transformations()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)                        # V1: nodes + supports
    define_elements()
    vis_model(output_dir)                        # V2: full geometry
    odb = create_odb(output_dir, odb_tag=1)
    define_masses()

    # --- Gravity phase: dead + live ---
    define_dead_loads()
    vis_loads(output_dir, filename="vis_03a_dead_loads.html")
    run_gravity(odb, n_steps=n_steps_gravity)

    define_live_loads()
    vis_loads(output_dir, filename="vis_03b_live_loads.html")
    run_gravity(odb, n_steps=n_steps_gravity)

    # --- Eigenvalue ---
    periods = run_eigenvalue(output_dir)

    # --- Pushover phase ---
    define_eq_loads()
    vis_pre_analysis(output_dir)                 # V4: pre-analysis check
    run_pushover(
        odb,
        ctrl_node=NODE_COL1_ROOF,
        ctrl_dof=1,
        target_disp=pushover_dmax,
        max_step=pushover_max_step,
    )
    return odb


# ── 14. POST-PROCESSING ──────────────────────────────────────────────────────

def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk, render deformed shape and animation."""
    odb.save_response()
    vis_defo(output_dir, filename="vis_05_deformed.html")
    vis_anim(
        output_dir,
        filename="vis_06_pushover_animation.html",
        odb_tag=1,
        defo_scale=20.0,
        resp_type="disp",
        resp_dof=("UX", "UY"),
        show_undeformed=True,
    )


# ── 15. MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import numpy as np  # needed by eigenvalue calculation
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print(f"Guan2020 analysis complete. Output in {output_dir}")
