# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Modeling of a Simplified Lateral Multi-Degree-of-Freedom (MDOF) Model
UniqueID : Dino_MDOF_eigen
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-12
Purpose  : Pure eigen / modal analysis of a 12-story uniform lumped-mass shear
           building.  ElasticTimoshenkoBeam elements with rigid axial/bending
           (A=J=Iy=Iz=1e20) and finite shear (Avy=Avz=3000) realise the
           shear-building idealisation; only UX mass is retained, so the
           structure has 12 lateral DOFs.  The model runs `eigen 10` and writes
           the periods + 10 mode shapes, validated against the closed-form
           uniform N-DOF shear-building frequency.
Ref      : Dino -- Modeling of a simplified lateral multi-degree-of-freedom
           model (original co.tcl)
Units    : N, mm, MPa, tonne  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import math
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

# This model nests under models/Dino/<analysis-name>/, one level deeper than
# the usual models/<UniqueID>/, so standards/ is parents[3] not parents[2]
# (see AGENT.md §12as-5).
_STANDARDS = Path(__file__).parents[3] / "standards"
if not _STANDARDS.exists():
    _STANDARDS = Path(__file__).parents[2] / "standards"   # fallback for relocation
sys.path.insert(0, str(_STANDARDS))
from units import *
from vis_utils import _headless, vis_nodes, vis_model

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Nodes / elements / transforms match the source tags exactly.
#   node 1   = top   (z = 36000)
#   node 13  = base  (z = 0)
NODE_TOP  = 1
NODE_BASE = 13
N_NODES   = 13
N_ELEMS   = 12

ODB_TAG = 1

# Source reference: Periods.txt (lambda values), no .out mode-shape files ship
# in tcl_ref/ -- the closed-form shear-building formula is the validation anchor.
REF_PERIODS = Path(__file__).parent / "tcl_ref" / "Periods.txt"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is N-mm-MPa-tonne (coords in mm, E in MPa, mass in N.s^2/mm = tonne).

# Geometry -- 13 nodes at x=y=0, z = 36000, 33000, ..., 3000, 0
#   (node 1 = top, node 13 = base; uniform 3 m storeys, 36 m total)
STORY_H = 3000.0 * mm
H_TOTAL = 36000.0 * mm
Z_COORDS = [H_TOTAL - STORY_H * k for k in range(N_NODES)]   # [36000, ..., 0]
N_STORIES = N_ELEMS                                         # 12 active UX DOFs

# Mass -- 100 (N.s^2/mm) of UX mass per node.  NOTE: in this N-mm system the
# mass unit IS N.s^2/mm (= 1 tonne), so the source's literal `mass 1 1.00E+002`
# is already in model units -- do NOT multiply by `tonne` (that double-converts,
# making the mass 1000x too large -> T 1000x too long).  AGENT.md §12al/§12b.
M_FLOOR = 100.0           # N.s^2/mm  (== 100 tonne)

# ElasticTimoshenkoBeam properties (source lines 67-78).
# E = G = 1e5 MPa; A = Jx = Iy = Iz = 1e20 (rigid axial/bending/torsion);
# Avy = Avz = 3000 mm^2 (the ONLY finite flexibility -> shear).
E_MOD  = 1.0e5 * MPa
G_MOD  = 1.0e5 * MPa
AREA   = 1.0e20            # mm^2  (rigid axial)
JX     = 1.0e20            # mm^4  (rigid torsion)
IY     = 1.0e20            # mm^4  (rigid bending, major)
IZ     = 1.0e20            # mm^4  (rigid bending, minor)
AVY    = 3000.0 * mm ** 2  # shear area y -> finite story shear stiffness
AVZ    = 3000.0 * mm ** 2  # shear area z

# Derived story shear stiffness:  k_story = G * Av / L
K_STORY = G_MOD * AVY / STORY_H     # = 1e5 MPa * 3000 mm^2 / 3000 mm = 1e5 N/mm

# Eigen analysis
NUM_MODES = 10                       # source: set numModes 10


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
# Not used -- ElasticTimoshenkoBeam takes E, G as numeric literals, NOT material
# tags.  The source's three `uniaxialMaterial Elastic` (tags 1, 2, 3) are dead
# code (never referenced by any element/section); omitted per AGENT.md §12ap-6.


# ── 6. GEOMETRIC TRANSFORMATIONS ─────────────────────────────────────────────
def define_geom_transf() -> None:
    """Define 12 Linear transforms with vector (1, 0, 0) (source lines 53-64)."""
    for k in range(1, N_ELEMS + 1):
        ops.geomTransf("Linear", k, 1.0, 0.0, 0.0)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Create the 13 column nodes along z at x=y=0 (source lines 5-17).

    Node 1 = top (z = 36000 mm); node 13 = base (z = 0).
    """
    for tag, z in enumerate(Z_COORDS, start=1):
        ops.node(tag, 0.0, 0.0, z)


# ── 8. BOUNDARY CONDITIONS + MASS ────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix nodes 1-12 in UY/UZ + all rotations (UX free); fix node 13 fully.

    Lumped mass = 100 tonne on UX (DOF 1) at every node (source lines 20-32,
    34-46).  Node 13's UX mass sits on a fixed DOF and contributes nothing to
    the dynamics, leaving 12 active lateral DOFs.
    """
    for tag in range(1, N_NODES):                 # nodes 1..12: UX free
        ops.fix(tag, 0, 1, 1, 1, 1, 1)
    ops.fix(NODE_BASE, 1, 1, 1, 1, 1, 1)          # node 13 fully fixed

    for tag in range(1, N_NODES + 1):             # mass on all 13 (source)
        ops.mass(tag, M_FLOOR, 0.0, 0.0, 0.0, 0.0, 0.0)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Create 12 ElasticTimoshenkoBeam elements (source lines 67-78).

    OpenSeesPy's 3D ElasticTimoshenkoBeam REQUIRES the 11-arg form with explicit
    shear areas:  (tag, iNode, jNode, E, G, A, Jx, Iy, Iz, Avy, Avz, transfTag).
    The 9-arg form (without Avy/Avz) errors (AGENT.md §12av).  Element k connects
    node k+1 (lower) to node k (upper); A=J=Iy=Iz=1e20 makes axial/bending/
    torsion rigid, leaving shear (Avy=Avz=3000) as the only finite flexibility.
    """
    for k in range(1, N_ELEMS + 1):
        ops.element(
            "ElasticTimoshenkoBeam",
            k,        # eleTag
            k + 1,    # iNode (lower)
            k,        # jNode (upper)
            E_MOD, G_MOD,
            AREA, JX, IY, IZ,
            AVY, AVZ,
            k,        # transfTag (1:1 with element)
        )


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB.  Eigen data is saved separately per mode in
    ``run_eigen`` via ``save_eigen_data`` (Guan2020 precedent).  No nodal
    responses are collected (there is no static/transient analysis).
    ``set_odb_path`` MUST precede ``CreateODB`` (§12ac).
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
# Not used -- pure eigen / modal analysis: no load patterns, gravity, or
# static/transient analysis step.  Precedent: AGENT.md §12ar omits inapplicable
# sections with an explanatory comment rather than stubbing them.


# ── 12. ANALYSIS (eigen) ─────────────────────────────────────────────────────
def _theoretical_periods(n_stories: int, k_story: float, m_floor: float,
                         n_modes: int) -> list[float]:
    """Closed-form periods of a uniform N-DOF shear building.

    omega_j = 2*sqrt(k/m)*sin((2j-1)*pi/(4N+2)),  T_j = 2*pi/omega_j.
    Used as the validation anchor (no external reference file ships in tcl_ref).
    """
    omegas = [
        2.0 * math.sqrt(k_story / m_floor) *
        math.sin((2 * j - 1) * math.pi / (4 * n_stories + 2))
        for j in range(1, n_modes + 1)
    ]
    return [2.0 * math.pi / w for w in omegas]


def run_eigen(odb: "opst.post.CreateODB", output_dir: Path) -> dict:
    """Run the eigen analysis and write periods + eigen data to the ODB.

    Uses the default subspace (ARPACK) solver -- the model has uniform stiffness
    and full-rank mass, so neither the stiffness-contrast rule (§12h-2) nor the
    rank-deficient-mass rule (§12al) applies.  Saves each mode's shape to the
    ODB via ``save_eigen_data`` (Guan2020 precedent) and writes the lambda
    values to ``Periods.txt`` matching the source's ``puts $Periods`` format.

    Returns a results dict: lams, periods (sim), periods_theo, diffs (%).
    """
    lams = ops.eigen(NUM_MODES)
    periods = [2.0 * math.pi / math.sqrt(l) for l in lams]

    # Save eigen mode shapes to the ODB (for plot_eigen* in post_process)
    for mode in range(1, NUM_MODES + 1):
        odb.save_eigen_data(mode_tag=mode, solver="-genBandArpack")

    # Write Periods.txt matching the source convention (a single line of lambdas)
    with open(output_dir / "Periods.txt", "w") as f:
        f.write(" " + " ".join(f"{l:.6e}" for l in lams) + "\n")

    # Theoretical anchor
    periods_theo = _theoretical_periods(N_STORIES, K_STORY, M_FLOOR, NUM_MODES)
    diffs = [abs(p - pt) / pt * 100.0 for p, pt in zip(periods, periods_theo)]

    print("  Mode |  T_sim (s) | T_theo (s) |  diff %")
    for j, (p, pt, d) in enumerate(zip(periods, periods_theo, diffs), start=1):
        print(f"   {j:2d}  |  {p:.4f}   |  {pt:.4f}   | {d:6.3f}")
    print(f"  Max diff: {max(diffs):.4f}%  (validation vs shear-building theory)")

    return {
        "lams": np.array(lams),
        "periods": np.array(periods),
        "periods_theo": np.array(periods_theo),
        "diffs": np.array(diffs),
    }


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build the MDOF model, run the eigen analysis, return ODB + results."""
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
    """Sim vs theoretical periods (matplotlib, plot_utils style)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  (matplotlib unavailable -- skipping periods plot)")
        return

    modes = np.arange(1, len(results["periods"]) + 1)
    width = 0.38
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    ax.bar(modes - width / 2, results["periods_theo"], width,
           color="0.6", label="Theory (shear building)")
    ax.bar(modes + width / 2, results["periods"], width,
           color="#5170d7", label="Simulation")
    ax.set_xlabel("Mode")
    ax.set_ylabel("Period (s)")
    ax.set_title("Dino_MDOF_eigen -- periods vs shear-building theory")
    ax.set_xticks(modes)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(str(output_dir / "periods_compare.png"), dpi=150)
    plt.close(fig)


def _plot_mode_shapes(output_dir: Path, n_plot: int = 4) -> None:
    """First few UX mode shapes vs height (matplotlib, plot_utils style).

    Reads the eigenvectors via ``ops.nodeEigenvector(node, mode)``; OpenSees
    mass-normalises so phi^T M phi = 1.  We normalise each shape to unit
    top-node amplitude for plotting (sign + scale arbitrary for mode shapes).
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  (matplotlib unavailable -- skipping mode-shape plot)")
        return

    heights = np.array(Z_COORDS) / 1.0e3            # m
    colors = ["#5170d7", "#d76151", "#51a357", "#d7a051"]
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    for m in range(1, n_plot + 1):
        shape = np.array([ops.nodeEigenvector(tag, m)[0]   # [0] = UX
                          for tag in range(1, N_NODES + 1)])
        top = abs(shape[NODE_TOP - 1])
        if top > 0:
            shape = shape / shape[NODE_TOP - 1]           # normalise to top = 1
        ax.plot(shape, heights, "-o", color=colors[m - 1],
                linewidth=1.3, markersize=4, label=f"Mode {m}")
    ax.axvline(0.0, color="0.6", linewidth=0.5)
    ax.set_xlabel("Normalised UX amplitude (top = 1)")
    ax.set_ylabel("Height (m)")
    ax.set_title("Dino_MDOF_eigen -- mode shapes")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(output_dir / "mode_shapes.png"), dpi=150)
    plt.close(fig)


def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render eigen visualisations + period/mode-shape plots.

    Args:
        odb: Populated CreateODB instance (model + eigen data saved).
        output_dir: Directory for output files.
        results: Results dict from ``run_eigen``.
    """
    odb.save_response()

    if not _headless():
        opst.post.set_odb_path(str(output_dir))

        # Eigen table (all modes)
        try:
            fig_t = opst.vis.plotly.plot_eigen_table(
                mode_tags=list(range(1, NUM_MODES + 1)), odb_tag=ODB_TAG)
            fig_t.write_html(str(output_dir / "vis_05_eigen_table.html"))
        except Exception as exc:
            print(f"  (plot_eigen_table failed: {exc})")

        # Mode-shape subplots (first 4 modes)
        try:
            fig_m = opst.vis.plotly.plot_eigen(
                mode_tags=list(range(1, 5)), odb_tag=ODB_TAG,
                subplots=True, scale=50.0, show_origin=True)
            fig_m.write_html(str(output_dir / "vis_06_eigen_modes.html"))
        except Exception as exc:
            print(f"  (plot_eigen failed: {exc})")

        # Mode-1 animation
        try:
            fig_a = opst.vis.plotly.plot_eigen_animation(
                mode_tag=1, odb_tag=ODB_TAG, n_cycle=3, framerate=10,
                scale=50.0, show_origin=True)
            fig_a.write_html(str(output_dir / "vis_07_mode1_animation.html"))
        except Exception as exc:
            print(f"  (plot_eigen_animation failed: {exc})")

    # Matplotlib plots
    _plot_periods(output_dir, results)
    _plot_mode_shapes(output_dir, n_plot=4)

    # Verification summary
    diffs = results["diffs"]
    print(f"\n  Eigen: {len(results['periods'])} modes | "
          f"T1 = {results['periods'][0]:.4f} s | "
          f"T10 = {results['periods'][-1]:.4f} s")
    print(f"  Max diff vs shear-building theory: {float(np.max(diffs)):.4f}%  "
          f"({'PASS' if float(np.max(diffs)) < 0.1 else 'CHECK'})")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_MDOF_eigen: analysis complete.")
