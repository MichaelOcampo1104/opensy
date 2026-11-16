# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Elastic site-response test of one plane-strain quad with a
           PressureIndependMultiYield material (OpenSees geotechnical Example 1)
UniqueID : Geo_example_1
Author   : Zhaohui Yang (UCSD), OpenSees example; OpenSeesPy conversion 2026-11-16
Date     : 2026-11-16
Purpose  : One 1 m x 1 m plane-strain quad, kept in the elastic stage of
           PressureIndependMultiYield, carrying its buoyant unit weight and a
           1 Hz sinusoidal base acceleration of 9.81 m/s^2 amplitude.
Ref      : tcl_ref/example_1.tcl (source), tcl_ref/*.out (source responses)
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import math
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops
import opstool as opst

# models/<UniqueID>/model.py -> repository root is parents[2]
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *  # noqa: E402,F403  (mm, m, sec, MPa, kPa, N)
from vis_utils import (  # noqa: E402
    _headless,
    vis_defo,
    vis_loads,
    vis_model,
    vis_nodes,
    vis_pre_analysis,
)
from plot_utils import COLORS, _style_ax  # noqa: E402

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
ODB_TAG = 1
MAT_SOIL = 2        # PressureIndependMultiYield (source tag 1, FluidSolidPorous, is unused and omitted)
ELE_SOIL = 1        # quad element
NODE_1 = 1          # base, left    (0, 0)
NODE_2 = 2          # base, right   (1 m, 0)
NODE_3 = 3          # top, right    (1 m, 1 m)
NODE_4 = 4          # top, left     (0, 1 m)
TS_BASE_ACC = 10    # Sine base acceleration (tags >= 10: created after wipeAnalysis, AGENT.md §12t)
PAT_BASE_ACC = 10   # UniformExcitation pattern
GP_A = 1            # Gauss point 1 (the source's `recorder ... material 1` is a Gauss-point index)
GP_B = 3            # Gauss point 3 (the source's `recorder ... material 3`)

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source units are SI (m, kN, t, s). Conversions used here:
#   length m -> mm (x1000);  stress kPa -> MPa (x0.001);
#   density t/m^3 -> N.s^2/mm^4 (x1e-9, because 1 t = 1 N.s^2/mm);
#   g = 9.81 m/s^2 -> 9810 mm/s^2.
# units.py `kg` and `tonne` are deliberately not used for mass (see LESSONS.md).
L_ELEM = 1.0 * m                       # element width and height (originally 1.0 m)
THICKNESS = 1.0 * m                    # out-of-plane thickness (originally 1.0 m)
E_MODULUS = 90000.0 * kPa              # originally 90000 kPa
POISSON = 0.40
G_SHEAR = E_MODULUS / (2.0 * (1.0 + POISSON))           # originally G = E/(2(1+nu))
B_BULK = E_MODULUS / (3.0 * (1.0 - 2.0 * POISSON))      # originally B = E/(3(1-2nu))
COHESION = 30.0 * kPa                  # originally 30 kPa
PEAK_SHEAR_STRAIN = 0.1                # dimensionless
# Required by the current OpenSees PressureIndependMultiYield (not in the source).
# 0 / 100 kPa / 0 are the recommended values and do not change the elastic stage.
FRICTION_ANG = 0.0                     # degrees
REF_PRESS = 100.0 * kPa                # reference pressure
PRESS_DEPEND = 0.0                     # pressure-dependence coefficient
N_YIELD_SURF = 20                      # number of yield surfaces (must be > 0; 20 is the usual value)
MASS_DEN = 2.0 * (N * sec**2 / mm) / m**3                      # solid density: 2.000 t/m^3 -> N.s^2/mm^4
FLUID_DEN = 1.0 * (N * sec**2 / mm) / m**3                     # fluid density: 1.000 t/m^3 -> N.s^2/mm^4
G_ACC = 9.81 * m / sec**2              # 9.81 m/s^2 -> 9810 mm/s^2
INCLINATION_DEG = 0.0
UNIT_WEIGHT_X = (MASS_DEN - FLUID_DEN) * G_ACC * math.sin(math.radians(INCLINATION_DEG))
UNIT_WEIGHT_Y = -(MASS_DEN - FLUID_DEN) * G_ACC * math.cos(math.radians(INCLINATION_DEG))
PRESS = 0.0 * MPa                      # isotropic consolidation pressure (originally 0)
RHO_ELEM = 0.0                         # quad density argument (originally 0.0)
PERIOD = 1.0 * sec                          # s, sinusoidal base acceleration period (originally 1)
SINE_T_END = 10.0 * sec                     # s, end of the Sine series (originally 10)
DT = 0.01 * sec                             # s, analysis step and recorder interval (originally 0.01)
N_STEPS = 2000                         # originally 2000
GAMMA = 0.5                            # Newmark gamma
BETA = (GAMMA + 0.5) ** 2 / 4.0        # Newmark beta, as in the source
MASS_PROP_DAMP = 0.0                   # Rayleigh alphaM (originally 0.0)
STIFF_PROP_DAMP = 0.001 * sec               # Rayleigh betaKinit (originally 0.001, third argument)
PENALTY = 1.0e18                       # penalty constraint stiffness (originally 1e18)
N_GRAV_STEPS = 2                       # gravity analyze count (source: analyze 2)
TEST_TOL_DISP = 1.0e-12 * m            # NormDispIncr tolerance: 1e-12 m, scaled to mm
TEST_ITERS = 25                        # originally 25

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Start a fresh 2D model with two DOFs per node."""
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 2)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Define PressureIndependMultiYield and hold it in its elastic stage (source: stage 0)."""
    ops.nDMaterial(
        "PressureIndependMultiYield", MAT_SOIL, 2, MASS_DEN,
        G_SHEAR, B_BULK, COHESION, PEAK_SHEAR_STRAIN,
        FRICTION_ANG, REF_PRESS, PRESS_DEPEND, N_YIELD_SURF,
    )
    ops.updateMaterialStage("-material", MAT_SOIL, "-stage", 0)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
# Not used: the quad element takes the nDMaterial directly, so there is no section.

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Create the four corners of a 1 m x 1 m square (coordinates in mm)."""
    ops.node(NODE_1, 0.0, 0.0)
    ops.node(NODE_2, L_ELEM, 0.0)
    ops.node(NODE_3, L_ELEM, L_ELEM)
    ops.node(NODE_4, 0.0, L_ELEM)

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
FIX_XY = [1, 1]                        # both translations fixed (source: fix 1 1 1; fix 2 1 1)

def define_boundary_conditions() -> None:
    """Fix the base nodes in x and y."""
    ops.fix(NODE_1, *FIX_XY)
    ops.fix(NODE_2, *FIX_XY)

def define_top_tie() -> None:
    """Tie the top nodes in x and y. Called after gravity, as in the source."""
    ops.equalDOF(NODE_3, NODE_4, 1, 2)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """One plane-strain quad. Gravity enters as its body force (unit weight)."""
    ops.element(
        "quad", ELE_SOIL, NODE_1, NODE_2, NODE_3, NODE_4,
        THICKNESS, "PlaneStrain", MAT_SOIL, PRESS, RHO_ELEM,
        UNIT_WEIGHT_X, UNIT_WEIGHT_Y,
    )

# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb() -> "opst.post.CreateODB":
    """Create the ODB after the element exists and before the first analysis.

    Nodal responses are saved for all four nodes; Gauss-point stresses and
    strains are read per Gauss point (AGENT.md §12ad).
    """
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_plane_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
    )
    odb.save_model_data()
    return odb

# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """No load pattern: gravity is the element body force set in define_elements()."""
    return None

def define_base_excitation() -> None:
    """Sinusoidal base acceleration, defined after gravity (source: UniformExcitation -accel Sine)."""
    ops.timeSeries("Sine", TS_BASE_ACC, 0.0, SINE_T_END, PERIOD, "-factor", G_ACC)
    ops.pattern("UniformExcitation", PAT_BASE_ACC, 1, "-accel", TS_BASE_ACC)

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity() -> None:
    """Gravity phase.

    A manual LoadControl loop, the permitted exception in AGENT.md §3c, because
    SmartAnalyze forces DisplacementControl for static analysis.
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.test("NormDispIncr", TEST_TOL_DISP, TEST_ITERS, 0)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0, 1, 1.0, 1.0)     # source: LoadControl 1 1 1 1
    ops.analysis("Static")
    for _ in range(N_GRAV_STEPS):                        # source: analyze 2
        ops.analyze(1)
    ops.setTime(0.0)
    ops.wipeAnalysis()

def run_dynamic(odb: "opst.post.CreateODB") -> None:
    """Transient phase with SmartAnalyze (AGENT.md §3c).

    The source's VariableTransient is replaced by a fixed step of DT. The
    model stays elastic, so no step is subdivided and the recorder grid is the same.
    """
    ops.constraints("Penalty", PENALTY, PENALTY)
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.rayleigh(MASS_PROP_DAMP, 0.0, STIFF_PROP_DAMP, 0.0)
    ops.integrator("Newmark", GAMMA, BETA)               # must be set before SmartAnalyze
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="NormDispIncr",
        testTol=TEST_TOL_DISP,
        testIterTimes=TEST_ITERS,
        tryAlterAlgoTypes=False,
        algoTypes=[10],                                  # Newton, as in the source
        tryAddTestTimes=False,
        printPer=0,
        testPrintFlag=0,
    )
    segs = analysis.transient_split(N_STEPS)
    for _ in segs:
        ok = analysis.TransientAnalyze(DT)
        if ok < 0:
            break
        odb.fetch_response_step()
    analysis.close()

def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build the model, run gravity then the base excitation, and return the ODB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))              # must precede CreateODB (AGENT.md §12ac)
    init_model()
    define_materials()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)                                # V1
    define_elements()
    vis_model(output_dir)                                # V2
    odb = create_odb()
    define_gravity_loads()
    vis_loads(output_dir)                                # V3 (body force only; no nodal loads)
    vis_pre_analysis(output_dir)                         # V4
    run_gravity()
    define_top_tie()
    define_base_excitation()
    run_dynamic(odb)
    return odb

# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
REF_DIR = Path(__file__).parent / "tcl_ref"         # source outputs (SI units)
REF_SIG_ORDER = ["sigma11", "sigma22", "sigma33", "sigma12", "para#1"]   # source column order
REF_EPS_ORDER = ["eps11", "eps22", "eps12"]
PASS_TOL = 1.0e-3                                   # largest error, as a fraction of the reference peak

def compare_with_reference(output_dir: Path) -> dict:
    """Compare ODB responses with the source outputs, both in N-mm-MPa.

    Displacement m -> mm, acceleration m/s^2 -> mm/s^2, stress kPa -> MPa.
    The t = 0 frame is dropped so the rows line up with the recorder rows.
    Stress and strain columns are matched by name, because the source writes
    stress as (sigma11, sigma22, sigma33, sigma12, para) while opstool stores
    (sigma11, sigma22, sigma12, sigma33, para#1).

    Args:
        output_dir: Folder for validation.txt and response_compare.png.

    Returns:
        Metric name -> largest absolute error divided by the reference peak.
    """
    import matplotlib.pyplot as plt

    nod = opst.post.get_nodal_responses(odb_tag=ODB_TAG)
    pl = opst.post.get_element_responses(odb_tag=ODB_TAG, ele_type="Plane")
    t_sim = nod["time"].values[1:]
    n_steps = len(t_sim)
    disp_sim = nod["disp"].sel(DOFs=["UX", "UY"]).values[1:].reshape(n_steps, -1)
    acc_sim = nod["accel"].sel(DOFs=["UX", "UY"]).values[1:].reshape(n_steps, -1)
    sig_names = [str(s) for s in pl["stressDOFs"].values]
    eps_names = [str(s) for s in pl["strainDOFs"].values]
    sig_cols = [sig_names.index(n) for n in REF_SIG_ORDER]
    eps_cols = [eps_names.index(n) for n in REF_EPS_ORDER]
    sig_sim = pl["Stresses"].values[1:]                 # (step, element, GP, component)
    eps_sim = pl["Strains"].values[1:]

    disp_file = np.loadtxt(REF_DIR / "disp.out")
    acc_file = np.loadtxt(REF_DIR / "acce.out")
    t_ref = disp_file[:, 0]
    s_ref = {gp: np.loadtxt(REF_DIR / f"stress{gp}.out")[:, 1:] * kPa for gp in (GP_A, GP_B)}
    e_ref = {gp: np.loadtxt(REF_DIR / f"strain{gp}.out")[:, 1:] for gp in (GP_A, GP_B)}

    pairs = {
        "disp_mm": (disp_sim, disp_file[:, 1:] * m),
        "accel_mm_s2": (acc_sim, acc_file[:, 1:] * (m / sec**2)),
        "stress_gp1_MPa": (sig_sim[:, 0, GP_A - 1, sig_cols], s_ref[GP_A]),
        "stress_gp3_MPa": (sig_sim[:, 0, GP_B - 1, sig_cols], s_ref[GP_B]),
        "strain_gp1": (eps_sim[:, 0, GP_A - 1, eps_cols], e_ref[GP_A]),
        "strain_gp3": (eps_sim[:, 0, GP_B - 1, eps_cols], e_ref[GP_B]),
    }
    results = {}
    for name, (sim, ref) in pairs.items():
        peak = float(np.max(np.abs(ref)))
        results[name] = float(np.max(np.abs(sim - ref)) / peak) if peak > 0.0 else 0.0
    time_ok = bool(np.allclose(t_sim, t_ref, atol=1.0e-4))

    # Units sanity gate (AGENT.md §12aq-3): simulated and reference peaks must agree within 10x.
    for name in ("disp_mm", "accel_mm_s2"):
        sim_peak = float(np.max(np.abs(pairs[name][0])))
        ref_peak = float(np.max(np.abs(pairs[name][1])))
        assert 0.1 < sim_peak / ref_peak < 10.0, f"units check failed for {name}"

    lines = [f"time grid matches the recorder rows: {time_ok}"]
    for name, err in results.items():
        status = "PASS" if err < PASS_TOL else "FAIL"
        lines.append(f"{name:<16s} normalised max error {err:.2e}  {status}")
    text = "\n".join(lines) + "\n"
    (output_dir / "validation.txt").write_text(text, encoding="utf-8")
    print(text)

    fig, axes = plt.subplots(2, 2, figsize=(10, 7), dpi=150)
    panels = [
        (axes[0, 0], disp_sim[:, 4], pairs["disp_mm"][1][:, 4], "Node 3, UX", "displacement (mm)"),
        (axes[0, 1], acc_sim[:, 4], pairs["accel_mm_s2"][1][:, 4], "Node 3, UX",
         "acceleration (mm/s$^2$)"),
        (axes[1, 0], sig_sim[:, 0, GP_A - 1, sig_cols[3]], s_ref[GP_A][:, 3],
         f"Gauss point {GP_A}, shear", "sigma12 (MPa)"),
        (axes[1, 1], sig_sim[:, 0, GP_B - 1, sig_cols[3]], s_ref[GP_B][:, 3],
         f"Gauss point {GP_B}, shear", "sigma12 (MPa)"),
    ]
    for ax, sim, ref, title, ylabel in panels:
        ax.plot(t_sim, sim, color=COLORS["primary"], lw=1.2, label="OpenSeesPy (N-mm-MPa)")
        ax.plot(t_ref, ref, color=COLORS["secondary"], lw=1.0, ls="--", label="source output")
        _style_ax(ax, "time (s)", ylabel, title)
        ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "response_compare.png")
    plt.close(fig)
    return results

def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush the ODB, write the deformed-shape view, and compare with the source outputs."""
    odb.save_response()
    if not _headless():
        vis_defo(output_dir, filename="vis_05_deformed.html", odb_tag=ODB_TAG,
                 resp_dof="UX", resp_type="disp", scale=1.0)
    compare_with_reference(output_dir)

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
