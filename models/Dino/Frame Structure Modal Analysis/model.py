# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Frame Structure Modal Analysis (Dino OpenSees tutorial, Example 05)
UniqueID : Dino_Frame_Modal_Ex05
Purpose  : Pure eigen (modal) analysis of the Example 04 four-storey 3D frame
           (2 x 1 bays, 28 nodes, 47 elasticBeamColumn elements with elastic
           sections, 22 lumped translational masses). The model runs `eigen 12`
           and writes the 12 eigenvalues (lambda = omega^2) to Periods.txt in the
           source format. They are validated against the source's Periods.txt.
Ref      : ref/co.tcl (source), ref/Periods.txt (reference eigenvalues),
           ref/EXAM05.s2k and ref/EXAM05.EDB (ETABS model)
Units    : N, mm, MPa, tonne (N.s^2/mm)  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import sys
from pathlib import Path
import numpy as np
import openseespy.opensees as ops
import opstool as opst

# This model sits under models/Dino/<analysis-name>/, one level deeper than the
# usual models/<UniqueID>/, so standards/ is parents[3] (see AGENT.md §12as-5).
_STANDARDS = Path(__file__).parents[3] / "standards"
if not _STANDARDS.exists():
    _STANDARDS = Path(__file__).parents[2] / "standards"   # fallback for relocation
sys.path.insert(0, str(_STANDARDS))
from units import *
from vis_utils import _headless, vis_nodes, vis_model

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Node, element, and transform tags match the source exactly.
NUM_MODES = 12          # source: set numModes 12
ODB_TAG   = 1
REF_PERIODS = Path(__file__).parent / "ref" / "Periods.txt"   # source eigenvalues

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Node coordinates [mm], verbatim from co.tcl (x: 0 / 4500 / 9000, y: 0 / 5000,
# z: base 0, floors 4500 / 7500 / 10500 / 13500)
NODE_XYZ = {
    1: (4500.0, 5000.0, 10500.0),   2: (4500.0, 5000.0, 13500.0),
    3: (4500.0, 0.0, 10500.0),      4: (4500.0, 0.0, 13500.0),
    5: (0.0, 0.0, 10500.0),         6: (0.0, 0.0, 13500.0),
    7: (0.0, 5000.0, 10500.0),      8: (0.0, 5000.0, 13500.0),
    9: (4500.0, 0.0, 7500.0),       10: (4500.0, 5000.0, 7500.0),
    11: (0.0, 0.0, 7500.0),         12: (0.0, 5000.0, 7500.0),
    13: (9000.0, 0.0, 7500.0),      14: (9000.0, 0.0, 10500.0),
    15: (9000.0, 5000.0, 7500.0),   16: (9000.0, 5000.0, 10500.0),
    17: (4500.0, 0.0, 4500.0),      18: (4500.0, 5000.0, 4500.0),
    19: (0.0, 0.0, 4500.0),         20: (0.0, 5000.0, 4500.0),
    21: (9000.0, 0.0, 4500.0),      22: (9000.0, 5000.0, 4500.0),
    23: (4500.0, 0.0, 0.0),         24: (4500.0, 5000.0, 0.0),
    25: (0.0, 0.0, 0.0),            26: (0.0, 5000.0, 0.0),
    27: (9000.0, 0.0, 0.0),         28: (9000.0, 5000.0, 0.0),
}
# Restrained nodes (all six DOFs fixed), verbatim from co.tcl
RESTRAINED_NODES = (23, 24, 25, 26, 27, 28)
# Lumped translational mass per node (UX = UY = UZ, rotations zero), verbatim from co.tcl.
# Units N.s^2/mm (= tonne), so the source values are used as they are.
MASS = {
    1: 8.604, 2: 4.302, 3: 8.604, 4: 4.302, 5: 4.302, 6: 4.302, 7: 4.302, 8: 4.302,
    9: 8.604, 10: 8.604, 11: 4.302, 12: 4.302, 13: 4.302, 14: 4.302, 15: 4.302,
    16: 4.302, 17: 8.604, 18: 8.604, 19: 4.302, 20: 4.302, 21: 4.302, 22: 4.302,
}

# elasticBeamColumn section properties (A, E, G, J, Iy, Iz), verbatim from co.tcl
PROPS = {
    "P1": (1.6e5, 2.68e4, 1.117e4, 3.605e9, 2.133e9, 2.133e9),
    "P2": (1.8e5, 2.68e4, 1.117e4, 3.708e9, 5.4e9, 1.35e9),
    "P3": (1.5e5, 2.68e4, 1.117e4, 2.817e9, 3.125e9, 1.125e9),
    "P4": (2.4e5, 2.68e4, 1.117e4, 7.512e9, 7.2e9, 3.2e9),
}
# (element tag, i-node, j-node, property key); the transform tag equals the element tag
ELEMENTS = [
    (1, 1, 2, "P1"), (2, 3, 4, "P1"), (3, 5, 6, "P1"), (4, 7, 8, "P1"),
    (5, 6, 8, "P2"), (6, 4, 2, "P2"), (7, 8, 2, "P3"), (8, 6, 4, "P3"),
    (9, 9, 3, "P1"), (10, 10, 1, "P1"), (11, 11, 5, "P4"), (12, 12, 7, "P4"),
    (13, 13, 14, "P4"), (14, 15, 16, "P4"), (15, 7, 1, "P3"), (16, 1, 16, "P3"),
    (17, 3, 14, "P3"), (18, 5, 3, "P3"), (19, 3, 1, "P2"), (20, 14, 16, "P2"),
    (21, 5, 7, "P2"), (22, 17, 9, "P1"), (23, 18, 10, "P1"), (24, 19, 11, "P4"),
    (25, 20, 12, "P4"), (26, 21, 13, "P4"), (27, 22, 15, "P4"), (28, 12, 10, "P3"),
    (29, 10, 15, "P3"), (30, 9, 13, "P3"), (31, 11, 9, "P3"), (32, 9, 10, "P2"),
    (33, 13, 15, "P2"), (34, 11, 12, "P2"), (35, 23, 17, "P1"), (36, 24, 18, "P1"),
    (37, 25, 19, "P4"), (38, 26, 20, "P4"), (39, 27, 21, "P4"), (40, 28, 22, "P4"),
    (41, 20, 18, "P3"), (42, 18, 22, "P3"), (43, 17, 21, "P3"), (44, 19, 17, "P3"),
    (45, 17, 18, "P2"), (46, 21, 22, "P2"), (47, 19, 20, "P2"),
]
# geomTransf vecxz per transform tag 1..47, verbatim from co.tcl (x-axis vectors for
# tags 1-4, 9-14, 22-27, 35-40; z-axis vectors for the rest)
TRANSF_VECXZ = (
    [(1.0, 0.0, 0.0)] * 4 + [(0.0, 0.0, 1.0)] * 4 + [(1.0, 0.0, 0.0)] * 6
    + [(0.0, 0.0, 1.0)] * 7 + [(1.0, 0.0, 0.0)] * 6 + [(0.0, 0.0, 1.0)] * 7
    + [(1.0, 0.0, 0.0)] * 6 + [(0.0, 0.0, 1.0)] * 7
)

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
# Not used: elasticBeamColumn takes E and G as numbers, not material tags. The
# source's three `uniaxialMaterial Elastic` lines (tags 1, 2, 3) are never referenced
# by any element, so they are omitted (AGENT.md §12ap-6).

# ── 6. GEOMETRIC TRANSFORMATIONS ─────────────────────────────────────────────
def define_geom_transf() -> None:
    for tag, vecxz in enumerate(TRANSF_VECXZ, start=1):
        ops.geomTransf("Linear", tag, *vecxz)

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    for tag, (x, y, z) in NODE_XYZ.items():
        ops.node(tag, x * mm, y * mm, z * mm)

# ── 8. BOUNDARY CONDITIONS AND MASS ──────────────────────────────────────────
def define_boundary_conditions() -> None:
    for tag in RESTRAINED_NODES:
        ops.fix(tag, 1, 1, 1, 1, 1, 1)
    for tag, m in MASS.items():
        ops.mass(tag, m, m, m, 0.0, 0.0, 0.0)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    for ele_tag, i_node, j_node, key in ELEMENTS:
        A, E, G, J, Iy, Iz = PROPS[key]
        ops.element("elasticBeamColumn", ele_tag, i_node, j_node,
                    A, E, G, J, Iy, Iz, ele_tag)     # transform tag = element tag

# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """ODB for the eigen results. Mode shapes are saved in run_eigen via save_eigen_data.
    No nodal responses are collected (there is no static or transient analysis).
    set_odb_path must come before CreateODB (AGENT.md §12ac).
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=False,
        save_frame_resp=False,
    )
    odb.save_model_data()
    return odb

# ── 11. LOADING ──────────────────────────────────────────────────────────────
# Not used: pure modal analysis has no load patterns, gravity, or time history.
# Example 05 lists no lateral loads (AGENT.md §12ar: inapplicable sections are omitted).

# ── 12. ANALYSIS (eigen) ─────────────────────────────────────────────────────
def load_reference_lambdas() -> np.ndarray:
    """Eigenvalues written by the source's `puts $Periods $lambda` (ref/Periods.txt)."""
    return np.array([float(v) for v in REF_PERIODS.read_text().split()])

def run_eigen(odb: "opst.post.CreateODB", output_dir: Path) -> dict:
    """Run `eigen 12`, save the mode shapes to the ODB, write Periods.txt, and compare
    the eigenvalues with the source's reference (ref/Periods.txt)."""
    lams = np.array(ops.eigen(NUM_MODES), dtype=float)
    for mode in range(1, NUM_MODES + 1):
        odb.save_eigen_data(mode_tag=mode, solver="-genBandArpack")

    with open(output_dir / "Periods.txt", "w") as f:
        f.write(" " + " ".join(f"{v:.6e}" for v in lams) + "\n")

    lams_ref = load_reference_lambdas()
    periods = 2.0 * np.pi / np.sqrt(lams)
    periods_ref = 2.0 * np.pi / np.sqrt(lams_ref)
    diff = np.abs(lams - lams_ref) / np.abs(lams_ref) * 100.0

    print("  Mode |  lambda sim |  lambda ref | diff (%) |  T_sim (s) |  T_ref (s)")
    for j in range(NUM_MODES):
        print(f"   {j + 1:2d}  |  {lams[j]:10.4f} |  {lams_ref[j]:10.4f} | {diff[j]:8.5f} |"
              f"  {periods[j]:.4f}   |  {periods_ref[j]:.4f}")
    print(f"  Max diff vs source eigenvalues: {diff.max():.6f}%")
    return {"lams": lams, "lams_ref": lams_ref, "periods": periods,
            "periods_ref": periods_ref, "diff": diff}

def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build the frame, run the eigen analysis, and return the ODB and results."""
    output_dir.mkdir(parents=True, exist_ok=True)
    init_model()
    define_geom_transf()
    define_nodes()
    vis_nodes(output_dir)
    define_boundary_conditions()
    define_elements()
    vis_model(output_dir)

    odb = create_odb(output_dir)
    print("Running eigen analysis...")
    results = run_eigen(odb, output_dir)
    return odb, results

# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def _plot_periods(output_dir: Path, results: dict) -> None:
    """Simulated vs source periods (matplotlib)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  (matplotlib unavailable -- skipping periods plot)")
        return
    modes = np.arange(1, NUM_MODES + 1)
    width = 0.38
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    ax.bar(modes - width / 2, results["periods_ref"], width, color="0.6", label="Source (Periods.txt)")
    ax.bar(modes + width / 2, results["periods"], width, color="#5170d7", label="Simulation")
    ax.set_xlabel("Mode")
    ax.set_ylabel("Period (s)")
    ax.set_title("Dino_Frame_Modal_Ex05 -- periods vs source")
    ax.set_xticks(modes)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(str(output_dir / "periods_compare.png"), dpi=150)
    plt.close(fig)

def post_process(odb: "opst.post.CreateODB", output_dir: Path, results: dict) -> None:
    """Flush the ODB, render the eigen visualisations, and print the verification."""
    odb.save_response()

    if not _headless():
        opst.post.set_odb_path(str(output_dir))
        try:
            fig_t = opst.vis.plotly.plot_eigen_table(
                mode_tags=list(range(1, NUM_MODES + 1)), odb_tag=ODB_TAG)
            fig_t.write_html(str(output_dir / "vis_05_eigen_table.html"))
        except Exception as exc:
            print(f"  (plot_eigen_table failed: {exc})")
        try:
            fig_m = opst.vis.plotly.plot_eigen(
                mode_tags=list(range(1, 5)), odb_tag=ODB_TAG,
                subplots=True, scale=50.0, show_origin=True)
            fig_m.write_html(str(output_dir / "vis_06_eigen_modes.html"))
        except Exception as exc:
            print(f"  (plot_eigen failed: {exc})")
        try:
            fig_a = opst.vis.plotly.plot_eigen_animation(
                mode_tag=1, odb_tag=ODB_TAG, n_cycle=3, framerate=10,
                scale=50.0, show_origin=True)
            fig_a.write_html(str(output_dir / "vis_07_mode1_animation.html"))
        except Exception as exc:
            print(f"  (plot_eigen_animation failed: {exc})")

    _plot_periods(output_dir, results)

    diff = results["diff"]
    print(f"\n  Eigen: {NUM_MODES} modes | T1 = {results['periods'][0]:.4f} s | "
          f"T{NUM_MODES} = {results['periods'][-1]:.4f} s")
    print(f"  Max diff vs source eigenvalues: {float(np.max(diff)):.6f}%  "
          f"({'PASS' if float(np.max(diff)) < 0.1 else 'CHECK'})")

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_Frame_Modal_Ex05: analysis complete.")
