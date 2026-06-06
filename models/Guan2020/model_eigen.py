# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Single-story single-bay 2D steel SMF — EIGENVALUE analysis
UniqueID : Guan2020
Author   : Xingquan Guan, Henry Burton, Mehrdad Shokrabadi (2020),
           ported by OpenSeesPy Standardisation Agent
Date     : 2026-06-06
Purpose  : Eigenvalue / modal analysis of a 2D steel special moment frame with
           leaning column.  Computes natural periods, mode shapes, and generates
           eigen visualisations.  Part of the Guan et al. (2020) database of
           621 steel SMF buildings (Building 10).
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
from vis_utils import vis_nodes, vis_model, vis_loads


# ══════════════════════════════════════════════════════════════════════════════
#  SHARED MODEL DEFINITION
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


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────

def _wf(d_in, A_in2, bf_in, tw_in, tf_in, Ix_in4, Iy_in4,
        Zx_in3, Zy_in3, ry_in, J_in4):
    return (
        d_in * inch,        A_in2 * inch**2,
        bf_in * inch,       tw_in * inch,       tf_in * inch,
        Ix_in4 * inch**4,   Iy_in4 * inch**4,
        Zx_in3 * inch**3,   Zy_in3 * inch**3,
        ry_in * inch,       J_in4 * inch**4,
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
n_eigen_modes   = 3


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────

def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────

def define_materials() -> None:
    ops.uniaxialMaterial("Elastic", MAT_STIFF, large_stiff)
    ops.uniaxialMaterial("Elastic", MAT_SOFT, negligible_val)
    ops.uniaxialMaterial("Elastic", MAT_TRUSS_RIGID, 1.0)


# ── 6. GEOMETRIC TRANSFORMATIONS ────────────────────────────────────────────

def define_transformations() -> None:
    ops.geomTransf("PDelta", TRANS_PDELTA)
    ops.geomTransf("Linear", TRANS_LINEAR)


# ── 7. NODES ─────────────────────────────────────────────────────────────────

def define_nodes() -> None:
    ops.node(NODE_COL1_BASE, 0.0, 0.0)
    ops.node(NODE_COL2_BASE, bay_width, 0.0)
    ops.node(NODE_COL1_ROOF, 0.0, h_first)
    ops.node(NODE_COL2_ROOF, bay_width, h_first)
    ops.node(NODE_LEAN_BASE, 2.0 * bay_width, 0.0)
    ops.node(NODE_LEAN_ROOF, 2.0 * bay_width, h_first)
    ops.node(NODE_LEAN_MID,  2.0 * bay_width, h_first)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────

def define_boundary_conditions() -> None:
    ops.fix(NODE_COL1_BASE, 1, 1, 1)
    ops.fix(NODE_COL2_BASE, 1, 1, 1)
    ops.fix(NODE_LEAN_BASE, 1, 1, 0)
    ops.equalDOF(NODE_COL1_ROOF, NODE_COL2_ROOF, 1)
    ops.equalDOF(NODE_COL1_ROOF, NODE_LEAN_ROOF, 1)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────

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


# ── 10. MASSES ───────────────────────────────────────────────────────────────

def define_masses() -> None:
    ops.mass(NODE_COL1_ROOF, nodal_mass_floor2, negligible_val, negligible_val)
    ops.mass(NODE_COL2_ROOF, nodal_mass_floor2, negligible_val, negligible_val)
    ops.mass(NODE_LEAN_ROOF, nodal_mass_floor2, negligible_val, negligible_val)


# ── 11. LOADING ──────────────────────────────────────────────────────────────

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


# ══════════════════════════════════════════════════════════════════════════════
#  GRAVITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def run_gravity(n_steps: int = n_steps_gravity) -> None:
    """Apply dead + live gravity via LoadControl (permitted exception)."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-6, 20, 2)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.analysis("Static")
    for _ in range(n_steps):
        ops.analyze(1)
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


# ══════════════════════════════════════════════════════════════════════════════
#  EIGENVALUE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def run_eigenvalue(output_dir: Path) -> None:
    """Compute eigenvalues, save eigen data to ODB, and generate visualisations.

    Produces:
      - Periods.out — modal periods (text)
      - vis_05_eigen_table.html — period / frequency table
      - vis_06_eigen_mode1.html … modeN.html — individual mode shapes
    """
    # --- Compute eigenvalues ---
    eigenvalues = ops.eigen(n_eigen_modes)
    periods = [2.0 * np.pi / np.sqrt(lam) for lam in eigenvalues]

    eigen_dir = output_dir / "EigenAnalysisOutput"
    eigen_dir.mkdir(parents=True, exist_ok=True)

    # Print summary
    print("\n── Eigenvalue Results ──")
    for i, (lam, T) in enumerate(zip(eigenvalues, periods), 1):
        f = 1.0 / T if T > 1e-12 else float("inf")
        print(f"  Mode {i}: λ={lam:.6e}  T={T:.4f} s  f={f:.4f} Hz")

    # Write periods
    with open(eigen_dir / "Periods.out", "w") as f:
        for i, T in enumerate(periods, 1):
            f.write(f"{T:.6f}\n")
    print(f"\nPeriods written to {eigen_dir / 'Periods.out'}")

    # --- Save eigen data to ODB (required for visualisation) ---
    odb = opst.post.CreateODB(odb_tag=2)   # ODB tag 2 for eigen data
    odb.save_model_data()
    for mode in range(1, n_eigen_modes + 1):
        odb.save_eigen_data(mode_tag=mode, solver="-genBandArpack")
    # Finalise (writes eigen data to disk immediately)
    odb.save_response()

    # --- Eigen visualisations ---
    if not _headless():
        # Period / frequency table
        fig_table = opst.vis.plotly.plot_eigen_table(
            mode_tags=list(range(1, n_eigen_modes + 1)),
            odb_tag=2,
        )
        fig_table.write_html(str(output_dir / "vis_05_eigen_table.html"))

        # Mode shapes (all modes in one multi-panel figure)
        fig_modes = opst.vis.plotly.plot_eigen(
            mode_tags=list(range(1, n_eigen_modes + 1)),
            odb_tag=2,
            subplots=True,
            scale=50.0,
            show_origin=True,
        )
        fig_modes.write_html(str(output_dir / "vis_06_eigen_modes.html"))

        # Animated first mode
        fig_anim = opst.vis.plotly.plot_eigen_animation(
            mode_tag=1,
            odb_tag=2,
            n_cycle=3,
            framerate=10,
            scale=50.0,
            show_origin=True,
        )
        fig_anim.write_html(str(output_dir / "vis_07_eigen_mode1_animation.html"))

        print("Eigen visualisations written to output/")
    else:
        print("Headless mode — skipping eigen visualisation")


def _headless() -> bool:
    import os
    return os.getenv("OPENSEES_HEADLESS", "0") == "1"


# ══════════════════════════════════════════════════════════════════════════════
#  ORCHESTRATION
# ══════════════════════════════════════════════════════════════════════════════

def run_analysis(output_dir: Path) -> None:
    """Build model, run gravity (dead+live), then eigenvalue analysis.

    Sequence:
      1. Build model
      2. Dead load gravity → loadConst
      3. Live load gravity → loadConst
      4. Eigenvalue analysis with ODB-based visualisation
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials()
    define_transformations()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)
    define_masses()

    # Gravity
    define_dead_loads()
    vis_loads(output_dir, filename="vis_03a_dead_loads.html")
    run_gravity()
    define_live_loads()
    vis_loads(output_dir, filename="vis_03b_live_loads.html")
    run_gravity()

    # Eigenvalue
    run_eigenvalue(output_dir)


# ── 15. MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    run_analysis(output_dir)
    print(f"\nGuan2020 eigenvalue analysis complete. Output in {output_dir}")
