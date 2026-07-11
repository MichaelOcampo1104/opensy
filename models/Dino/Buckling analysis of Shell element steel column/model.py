# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Buckling Analysis of a Shell-Element Steel I-Section Column
UniqueID : Dino_Buckling
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-11
Purpose  : Axial-compression buckling of a thin-walled steel I-section column
           built from ShellNLDKGQ elements, with a lateral imperfection preload
           followed by displacement-controlled axial shortening.
Ref      : Dino — Buckling analysis of Shell element steel column (original co.tcl)
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

# This model nests under models/Dino/<analysis-name>/, one level deeper than the
# usual models/<UniqueID>/, so standards/ is parents[3] not parents[2].
_STANDARDS = Path(__file__).parents[3] / "standards"
if not _STANDARDS.exists():
    _STANDARDS = Path(__file__).parents[2] / "standards"   # fallback for relocation
sys.path.insert(0, str(_STANDARDS))
from units import *
from vis_utils import (
    _headless,
    vis_nodes,
    vis_model,
    vis_loads,
    vis_pre_analysis,
    vis_defo,
    vis_slider,
    vis_anim,
)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Materials
MAT_STEEL_ND   = 1     # ElasticIsotropic steel (nDMaterial)
MAT_PLATEFIBER = 601   # PlateFiber wrapper (references MAT_STEEL_ND)
# (source also defines dead uniaxialMaterial tags 2, 3 — never referenced; omitted)

# Section
SEC_PLATE      = 701   # PlateFiber section (20 mm thick)

# Nodes — generated; the following are named for clarity
#   base ring     : first 25 nodes (z = 0)
#   top ring      : the 25 nodes at z = H_COL (loaded)
NODE_CTRL_TOP  = 70    # DisplacementControl node (top, web-centre)
#  ^ matches the source tag at (100, 200, 5000)

# Elements — ShellNLDKGQ quads, tagged sequentially from 1

# Load patterns / time series
TS_PUSH        = 1
TS_DEAD        = 2
PAT_PUSH       = 3     # lateral imperfection (matches source pattern tag 3)
PAT_DEAD       = 1     # axial compression   (matches source pattern tag 1)

# ODB
ODB_TAG        = 1

# Analysis
N_PUSH_STEPS   = 1     # imperfection applied in a single LoadControl step


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coordinates in mm, E in MPa, forces in N).

# Geometry — I-section (wide-flange), 3 flat shell walls
H_COL     = 5000.0 * mm        # 5000 mm column height
B_FLANGE  = 200.0 * mm         # 200 mm flange width  (x: 0 -> 200)
D_SECT    = 200.0 * mm         # 200 mm section depth (y: 100 -> 300)
T_PLATE   = 20.0 * mm          # 20 mm plate (wall) thickness
# Flange y-planes
Y_TOP     = 300.0 * mm         # top flange at y = 300
Y_BOT     = 100.0 * mm         # bottom flange at y = 100
X_WEB     = 100.0 * mm         # web at x = 100 (mid-flange)

# Mesh discretisation (matches source)
N_SEG_FLANGE = 8               # 8 segments along each flange width (9 nodes)
N_SEG_WEB    = 8               # 8 segments along the web depth (7 interior + 2 shared)
N_SEG_H      = 50              # 50 segments along the height (51 z-levels)
#  -> 3 walls x 400 = 1200 elements; 25 nodes per ring x 51 = 1275 nodes

# Material — ElasticIsotropic steel
E_STEEL   = 205000.0 * MPa     # 205000 MPa elastic modulus
NU_STEEL  = 0.3                # Poisson's ratio

# Loading — imperfection (PUSH) then axial buckling (DEAD)
P_PUSH_PER_NODE = 1000.0 * N   # 1000 N lateral (UX) at each top node
P_DEAD_PER_NODE = -10000.0 * N # -10000 N axial (UZ) at each top node
N_TOP_NODES     = 25           # 25 top-ring nodes loaded
#  -> total lateral imperfection = 25 kN; total axial reference = -250 kN

# Buckling analysis (DisplacementControl on NODE_CTRL_TOP, DOF 3 = UZ)
DISP_MAX   = 50.0 * mm         # 50 mm imposed axial shortening (target)
N_PUSH_BUCKLE = 100            # displacement-controlled steps
MAX_STEP   = DISP_MAX / N_PUSH_BUCKLE   # 0.5 mm/step (matches source)


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Define ElasticIsotropic steel + PlateFiber wrapper + PlateFiber section.

    The chain is: ElasticIsotropic (nDMaterial) -> PlateFiber (nDMaterial,
    wraps the 3D material into a plane-stress plate form) -> PlateFiber section
    (20 mm thick shell section).  This is the standard openseespy shell-section
    recipe.  The source's dead ``uniaxialMaterial Elastic`` tags 2 and 3 are
    omitted (never referenced by any section/element — same cleanup as Dino §12ap-6).
    """
    ops.nDMaterial("ElasticIsotropic", MAT_STEEL_ND, E_STEEL, NU_STEEL)
    ops.nDMaterial("PlateFiber", MAT_PLATEFIBER, MAT_STEEL_ND)
    ops.section("PlateFiber", SEC_PLATE, MAT_PLATEFIBER, T_PLATE)


# ── 6. NODES ─────────────────────────────────────────────────────────────────
def _wall_node_coords() -> list[list[tuple[float, float]]]:
    """Return the 3 walls' node-coordinate sequences (9 nodes each, corners shared).

    Each wall is a list of 9 (x, y) points ordered along the wall.  The web's
    endpoints (100, Y_TOP) and (100, Y_BOT) are the SAME coordinate objects as
    the flange mid-nodes, so when ``define_nodes`` keys nodes by coordinate the
    walls genuinely share those corner nodes (a T-junction I-section, not three
    disconnected plates).  This is the critical connectivity detail — if the
    walls don't share corners the column cannot buckle as a composite section.
    """
    # Top flange: x = 0, 25, ..., 200  at y = Y_TOP  (9 nodes)
    top = [((B_FLANGE / N_SEG_FLANGE) * i, Y_TOP) for i in range(N_SEG_FLANGE + 1)]
    # Web: y = Y_TOP, Y_TOP-25, ..., Y_BOT  at x = X_WEB  (9 nodes; endpoints
    # shared with the flange mid-nodes by coordinate value)
    web = [(X_WEB, Y_TOP - (D_SECT / N_SEG_WEB) * j) for j in range(N_SEG_WEB + 1)]
    # Bottom flange: x = 200, 175, ..., 0  at y = Y_BOT  (9 nodes)
    bot = [(B_FLANGE - (B_FLANGE / N_SEG_FLANGE) * i, Y_BOT)
           for i in range(N_SEG_FLANGE + 1)]
    return [top, web, bot]


def define_nodes() -> tuple[dict, list[list[tuple[float, float]]]]:
    """Generate the 25 x 51 = 1275 nodes, keyed by (x, y, z) so walls share corners.

    Returns:
        rings: dict mapping z-level index -> dict {(x, y): node_tag} for that ring.
        walls: the 3 walls' coordinate sequences (from ``_wall_node_coords``).
    """
    walls = _wall_node_coords()
    rings: dict[int, dict[tuple[float, float], int]] = {}
    tag = 0
    for kz in range(N_SEG_H + 1):
        z = (H_COL / N_SEG_H) * kz
        ring: dict[tuple[float, float], int] = {}
        for wall in walls:
            for (x, y) in wall:
                key = (round(x, 6), round(y, 6))
                if key not in ring:
                    tag += 1
                    ops.node(tag, x, y, z)
                    ring[key] = tag
        rings[kz] = ring
    return rings, walls


# ── 7. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(rings: dict) -> list[int]:
    """Fully fix the 25 base-ring nodes (z = 0); return the top-ring node tags.

    Args:
        rings: Ring map from ``define_nodes``.

    Returns:
        List of the 25 top-ring node tags (loaded by PUSH and DEAD patterns).
    """
    for tag in rings[0].values():
        ops.fix(tag, 1, 1, 1, 1, 1, 1)
    return list(rings[N_SEG_H].values())


# ── 8. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(rings: dict, walls: list[list[tuple[float, float]]]) -> int:
    """Create the ShellNLDKGQ quad elements connecting consecutive rings.

    For each wall, each segment i (0..N_SEG-1) connects ring-node [i] and [i+1]
    on the lower ring and the same indices on the upper ring, forming a quad.
    Because ``define_nodes`` keys by coordinate, a web endpoint and the flange
    mid-node at the same (x, y) resolve to ONE tag — so the walls are rigidly
    joined at the T-junctions.  3 walls × 8 segments × 50 heights = 1200 elements.

    Returns the control-node tag at the top web-centre (100, Y_MID, H_COL),
    matching the source's node 70.
    """
    tag = 0
    for kz in range(N_SEG_H):
        lower = rings[kz]
        upper = rings[kz + 1]
        for wall in walls:
            for i in range(len(wall) - 1):
                k1 = (round(wall[i][0], 6), round(wall[i][1], 6))
                k2 = (round(wall[i + 1][0], 6), round(wall[i + 1][1], 6))
                n1 = lower[k1]
                n2 = lower[k2]
                n3 = upper[k2]
                n4 = upper[k1]
                tag += 1
                ops.element("ShellNLDKGQ", tag, n1, n2, n3, n4, SEC_PLATE)
    # Control node = top ring, web-centre coordinate (X_WEB, Y_MID)
    y_mid = (Y_TOP + Y_BOT) / 2.0
    return rings[N_SEG_H][(round(X_WEB, 6), round(y_mid, 6))]


# ── 9. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a shell model.

    ``save_shell_resp=True`` collects shell element responses; ``save_frame_resp``
    /``save_truss_resp`` disabled (no such elements — avoids silent memory growth,
    §12u-2).  ``node_tags`` omitted so the full mesh deforms in the visualisation
    (§12u — node_tags breaks ``plot_nodal_responses``).
    """
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
        save_shell_resp=True,
    )
    odb.save_model_data()
    return odb


# ── 10. LOADING ──────────────────────────────────────────────────────────────
def define_push_loads(top_nodes: list[int]) -> None:
    """Apply the lateral imperfection (UX) at each top-ring node.

    This is the small preload that gives the column a one-sided lean so the
    axial buckling has a preferred direction (an eigen buckling analysis would
    otherwise bifurcate symmetrically).  Run BEFORE ``loadConst``.
    """
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    for n in top_nodes:
        ops.load(n, P_PUSH_PER_NODE, 0.0, 0.0, 0.0, 0.0, 0.0)


def define_dead_loads(top_nodes: list[int]) -> None:
    """Apply the axial compression (UZ) reference load at each top-ring node.

    MUST be called AFTER ``loadConst`` (§12z-1) — a DisplacementControl pattern
    frozen at λ=0 yields an infinite load factor at step 0.
    """
    ops.timeSeries("Linear", TS_DEAD)
    ops.pattern("Plain", PAT_DEAD, TS_DEAD)
    for n in top_nodes:
        ops.load(n, 0.0, 0.0, P_DEAD_PER_NODE, 0.0, 0.0, 0.0)


# ── 11. ANALYSIS ─────────────────────────────────────────────────────────────
def run_push_imperfection(odb: "opst.post.CreateODB") -> None:
    """Apply the lateral imperfection via a manual LoadControl step.

    Per AGENT.md §3c / §10, a manual ``ops.analyze()`` loop is the permitted
    exception for LoadControl (SmartAnalyze forces DisplacementControl).
    Source: ``integrator LoadControl 0.07; analyze 1`` (one step to λ=0.07).
    """
    ops.constraints("Penalty", 1e20, 1e20)
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", 1.0e-4, 1000, 2)
    ops.algorithm("Linear")
    ops.integrator("LoadControl", 0.07)
    ops.analysis("Static")

    ok = ops.analyze(1)
    if ok != 0:
        print(f"  WARNING: PUSH imperfection step failed (ok={ok})")
    else:
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def run_axial_buckling(
    odb: "opst.post.CreateODB",
    ctrl_node: int = NODE_CTRL_TOP,
    ctrl_dof: int = 3,
    target_disp: float = -DISP_MAX,
    max_step: float = MAX_STEP,
) -> tuple[list[float], list[float]]:
    """Run the displacement-controlled axial buckling via SmartAnalyze.

    SmartAnalyze manages constraints / numberer / system / test / algorithm
    internally.  Settings follow §12z (NormDispIncr @ 1e-4, KrylovNewton primary,
    algorithm fallback ladder) for the post-buckling softening regime.

    Args:
        odb: Active CreateODB instance.
        ctrl_node: Control node tag (top web-centre, UZ).
        ctrl_dof: Control DOF (3 = UZ).
        target_disp: Target axial shortening (negative = compression) in mm.
        max_step: Maximum displacement increment in mm.

    Returns:
        (axial_load [kN], shortening [mm]) lists at each converged step.  Axial
        load = DEAD load-factor × total reference (250 kN); derived from the
        reaction sum would also work but λ × P_ref is the source convention.
    """
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="NormDispIncr",
        testTol=1.0e-4,
        testIterTimes=1000,
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30],
        tryLooseTestTol=True,
        looseTestTolTo=1.0e-3,
        tryAddTestTimes=True,
        testIterTimesMore=[500, 1000],
        relaxation=0.5,
        minStep=1.0e-2,
    )

    protocol = [target_disp]
    segs = analysis.static_split(protocol, maxStep=max_step)

    load_hist: list[float] = []
    disp_hist: list[float] = []
    p_ref_total = N_TOP_NODES * abs(P_DEAD_PER_NODE)   # 250 kN reference

    for seg in segs:
        rc = analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
        odb.fetch_response_step()
        if rc < 0:
            print(f"  WARNING: buckling segment failed (rc={rc})")
            break
        t = ops.getTime()
        load_hist.append(t * p_ref_total / 1e3)        # kN
        disp_hist.append(ops.nodeDisp(ctrl_node, ctrl_dof))

    analysis.close()
    print(f"  Converged {len(load_hist)}/{len(segs)} buckling steps.")
    return load_hist, disp_hist


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run imperfection + axial buckling, return ODB + results.

    Args:
        output_dir: Directory for ODB + HTML visualisations.

    Returns:
        (odb, results) where results has keys: load, disp, ref1, ref2, ref3.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials()
    rings, walls = define_nodes()
    top_nodes = define_boundary_conditions(rings)
    vis_nodes(output_dir)
    ctrl_node = define_elements(rings, walls)
    vis_model(output_dir)

    odb = create_odb(output_dir)

    # Phase 1: lateral imperfection (before loadConst)
    define_push_loads(top_nodes)
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    print("Running PUSH imperfection...")
    run_push_imperfection(odb)

    # Phase 2: axial buckling (DEAD pattern MUST be after loadConst — §12z-1)
    define_dead_loads(top_nodes)

    print("Running axial buckling...")
    load_hist, disp_hist = run_axial_buckling(odb, ctrl_node=ctrl_node)

    # Load the three reference buckling curves
    ref_csv = Path(__file__).parent / "py_ref" / "reference_curves.csv"
    ref1 = ref2 = ref3 = None
    if ref_csv.exists():
        raw = np.loadtxt(str(ref_csv), delimiter=",", skiprows=1)
        # columns: d1,L1,d2,L2,d3,L3  (disp mm, load kN)
        def clean(col_d, col_l):
            d = raw[:, col_d]; l = raw[:, col_l]
            m = ~np.isnan(d)
            return d[m], l[m]
        ref1 = clean(0, 1)
        ref2 = clean(2, 3)
        ref3 = clean(4, 5)

    results = {
        "load": np.array(load_hist),
        "disp": np.array(disp_hist),
        "ref1": ref1, "ref2": ref2, "ref3": ref3,
    }

    if len(load_hist) > 0:
        curve = np.column_stack([results["load"], results["disp"]])
        np.savetxt(str(output_dir / "buckling_curve.csv"), curve,
                   delimiter=",", header="axial_load_kN,shortening_mm")

    return odb, results


# ── 12. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render deformed-shape visualisations, plot buckling curves.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis.
    """
    odb.save_response()

    if not _headless():
        opst.post.set_odb_path(str(output_dir))

        # V5 — peak deformed shape (absMax step)
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UX", scale=5.0)

        # V6 — step slider
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UX", scale=5.0)

        # V7 — animation
        vis_anim(output_dir, filename="vis_07_animation.html",
                 odb_tag=ODB_TAG, defo_scale=5.0,
                 resp_dof=("UX", "UY", "UZ"))

    # Buckling curve: simulation vs three references (matplotlib)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 1, figsize=(7, 5))
        if results["ref1"] is not None:
            ax.plot(results["ref1"][0], results["ref1"][1], "k-",
                    linewidth=1.0, alpha=0.5, label="Ref d=1/264")
        if results["ref2"] is not None:
            ax.plot(results["ref2"][0], results["ref2"][1], "g-",
                    linewidth=1.0, alpha=0.5, label="Ref d=1/132")
        if results["ref3"] is not None:
            ax.plot(results["ref3"][0], results["ref3"][1], "b-",
                    linewidth=1.0, alpha=0.5, label="Ref d=1/377")
        if len(results["disp"]) > 0:
            ax.plot(results["disp"], results["load"], "r--",
                    linewidth=1.5, alpha=0.9, label="Simulation")
        ax.set_xlabel("Axial shortening (mm)")
        ax.set_ylabel("Axial load (kN)")
        ax.set_title("Dino_Buckling — steel I-column buckling")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "buckling_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable — skipping buckling plot)")

    # Verification summary
    if len(results["load"]) > 0:
        sim_peak = float(np.max(results["load"]))
        print(f"\n  Sim peak axial load: {sim_peak:.1f} kN"
              f"  (reference peak ~630 kN)")


# ── 13. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_Buckling: analysis complete.")
