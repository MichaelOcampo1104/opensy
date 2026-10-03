# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Modeling and Application of Solid Elements (Dino Exam24)
UniqueID : Dino_SolidBrick
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-03
Purpose  : Static gravity analysis of a 3D solid-element assembly (480
           nodes, 248 stdBrick brick elements; ElasticIsotropic steel).
           Three -1e5 N UZ loads are ramped 0.01 x 100 steps (LoadControl);
           the node-102 history is validated against ref/node102.out and the
           full 480-node field against node0-4.out.
Ref      : Dino -- Modeling and Application of Solid Elements
           (original exam24.tcl)
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import re
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
# ElasticIsotropic solid material (source tag).
MAT_SOLID     = 100    # nDMaterial ElasticIsotropic steel

# Brick elements carry the source's 1-based tags (1..248); replayed verbatim
# from exam24.tcl rather than enumerated as named constants.
ELE_TAG_MIN   = 1
ELE_TAG_MAX   = 248

# Validation
NODE_MONITOR  = 102    # node-102 history validated against node102.out

# Time series / patterns (pattern tag 1 matches the source).
TS_GRAVITY    = 1
PAT_GRAVITY   = 1

# ODB
ODB_TAG       = 1

# Source files
TCL_FILE      = Path(__file__).parent / "ref" / "exam24.tcl"
REF_RAMP      = Path(__file__).parent / "ref" / "node102.out"
REF_SINGLE    = Path(__file__).parent / "ref" / "snode102.out"
REF_FIELDS    = [Path(__file__).parent / "ref" / f"node{i}.out" for i in range(5)]


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N).

# ElasticIsotropic steel (source line, verbatim).
E_SOLID  = 206000.0 * MPa
NU_SOLID = 0.3

# Reference loads (source pattern Plain 1): 3 x -1e5 N UZ.
P_REF = -1.0e5 * N
LOAD_NODES = (100, 101, 102)

# Load ramp: the source runs a single LoadControl(1.0) step, but ref/
# also ships node102.out -- the same final state reached via a 0.01 x 100
# ramp.  The ramp is used (100 x LoadControl 0.01 manual loop, §3c
# exception) so every intermediate state validates 1:1 against node102.out;
# the final state additionally matches snode102.out and node0-4.out.
N_RAMP_STEPS = 100
RAMP_LAMBDA  = 0.01

N_TOTAL_STEPS = N_RAMP_STEPS  # 100


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D solid model (ndm=3, ndf=3)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """ElasticIsotropic steel (source line, verbatim)."""
    ops.nDMaterial("ElasticIsotropic", MAT_SOLID, E_SOLID, NU_SOLID)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
# Not used -- stdBrick elements take the nDMaterial tag directly; there are
# no fiber/plate sections in this model.


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 480 nodes from exam24.tcl, verbatim (no masses in source)."""
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Apply the 27 fully-fixed nodes from exam24.tcl.

    The source writes six constraint values (``fix 1 1 1 1 1 1 1;``) on an
    ndf=3 model; only the first three take effect (all ones -- fully fixed
    either way), so the replay keeps the leading triple.  Trailing ';'
    tolerated.  (The source prints "rigidDiaphragm" / "Equal DOF" labels
    but issues no MP-constraint commands.)
    """
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)", src, re.M
    ):
        ops.fix(int(m.group(1)),
                int(m.group(2)), int(m.group(3)), int(m.group(4)))


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> int:
    """Create the 248 stdBrick elements from exam24.tcl, verbatim.

    ``element stdBrick tag n1..n8 matTag`` -- the OpenSeesPy signature
    matches the Tcl form directly (no transformation or section objects
    needed for bricks).  Returns the number of elements created.
    """
    n = 0
    for m in re.finditer(
        r"^element\s+stdBrick\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
        r"\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", src, re.M,
    ):
        ops.element("stdBrick", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), int(m.group(4)), int(m.group(5)),
                    int(m.group(6)), int(m.group(7)), int(m.group(8)),
                    int(m.group(9)), int(m.group(10)))
        n += 1
    return n


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a static brick model.

    Nodal responses carry the displacement validation; brick Gauss-point
    responses are disabled (no stress reference exists).  ``set_odb_path``
    precedes ``CreateODB`` (§12ac).  ``model_update=False`` -- no elements
    are removed/added mid-analysis.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
        save_shell_resp=False,
        save_brick_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Single Plain pattern (source pattern 1): 3 x -1e5 N UZ loads.

    ndf=3 nodes take exactly 3 load values -- the source writes six
    (``load 100 0 0 -1e5 0 0 0``) but ``Node::addunbalLoad`` rejects size 6
    ("load to add of incorrect size 6 should be 3", warning only, load
    silently dropped); only the leading UX/UY/UZ triple is applied.
    """
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    for nd in LOAD_NODES:
        ops.load(nd, 0.0, 0.0, P_REF)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity_ramp(odb: "opst.post.CreateODB") -> bool:
    """Load-factor ramp: 100 x LoadControl(0.01) manual loop (§3c exception).

    SmartAnalyze forces DisplacementControl, so the source's LoadControl
    static analysis uses a manual ``ops.analyze(1)`` loop (the permitted
    §3c/§10 exception).  In-loop history (load factor via getTime,
    node-102 UX/UY/UZ) is tracked for 1:1 validation against node102.out.
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", RAMP_LAMBDA)
    ops.analysis("Static")

    history: list[tuple[float, float, float, float]] = []  # (lf, ux, uy, uz)
    ok = 0
    for step in range(N_RAMP_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"  WARNING: ramp step {step} failed (ok={ok})")
            break
        odb.fetch_response_step()
        ops.reactions()
        history.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_MONITOR, 1)),
            float(ops.nodeDisp(NODE_MONITOR, 2)),
            float(ops.nodeDisp(NODE_MONITOR, 3)),
        ))
    run_gravity_ramp.history = history  # type: ignore[attr-defined]
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run load ramp, return ODB + results.

    Returns:
        (odb, results) where results has keys: hist (4,N) sim
        [LF,UX,UY,UZ] history, ref (4,N) node102.out ramp reference,
        ref_single (4,) snode102.out final state, ref_field (480,3)
        full-field final displacements from node0-4.out.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    src = TCL_FILE.read_text()

    init_model()
    define_materials()
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_ele = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_ele} stdBrick elements (expected 248).")

    odb = create_odb(output_dir)

    define_gravity_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running gravity load ramp...")
    run_gravity_ramp(odb)

    # Reference node-102 ramp (node102.out: col0=lambda, cols 1-3=UX/UY/UZ).
    ref = np.loadtxt(str(REF_RAMP)).T if REF_RAMP.exists() else None
    ref_single = (np.loadtxt(str(REF_SINGLE))
                  if REF_SINGLE.exists() else None)
    # Full-field final state from node0.out..node4.out.  Each file holds ONE
    # long row: pseudo-time followed by (UX, UY, UZ) triplets for every node
    # in its range -- drop col 0 and reshape to (n, 3).
    ref_field = None
    try:
        mats = []
        for f in REF_FIELDS:
            b = np.loadtxt(str(f))
            b = np.atleast_2d(b)
            mats.append(b[0, 1:].reshape(-1, 3))
        ref_field = np.vstack(mats)
    except Exception as e:
        print(f"  (full-field reference unreadable: {e})")

    hist = np.array(getattr(run_gravity_ramp, "history", []), dtype=float).T
    results = {"hist": hist, "ref": ref,
               "ref_single": ref_single, "ref_field": ref_field}
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot histories, verify.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis.
    """
    odb.save_response()

    hist = results["hist"]
    ref = results["ref"]

    # Dump the full node-102 history for the record.
    if hist is not None and hist.shape[1] > 0:
        step = np.arange(1, hist.shape[1] + 1)
        curve = np.column_stack([step, hist.T])  # (N,5): step, LF, UX, UY, UZ
        np.savetxt(str(output_dir / "node102_disp_history.csv"), curve,
                   delimiter=",", header="step,lf,ux_mm,uy_mm,uz_mm")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))

        # V5 -- final deformed shape (gravity is vertical -> UZ).
        # Peak UZ is only ~0.28 mm on a ~12 m structure, so a large
        # magnification is needed for the deflection to be visible.
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UZ", scale=2000.0)
        # V6 -- step slider
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UZ", scale=2000.0)
        # V7 -- animation
        vis_anim(output_dir, filename="vis_07_animation.html",
                 odb_tag=ODB_TAG, defo_scale=2000.0,
                 resp_dof=("UX", "UY", "UZ"))

    # Node-102 load-displacement: simulation vs reference (matplotlib)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        if ref is not None and ref.shape[1] > 0:
            ax1.plot(ref[3], ref[0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node102.out)")
        if hist is not None and hist.shape[1] > 0:
            ax1.plot(hist[3], hist[0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax1.set_xlabel(f"Node {NODE_MONITOR} UZ displacement (mm)")
        ax1.set_ylabel("Load factor")
        ax1.set_title("Dino_SolidBrick -- capacity (UZ vs LF)")
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        if ref is not None and ref.shape[1] > 0:
            ax2.plot(np.arange(1, ref.shape[1] + 1), ref[0], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node102.out)")
        if hist is not None and hist.shape[1] > 0:
            ax2.plot(np.arange(1, hist.shape[1] + 1), hist[0], "r--",
                     linewidth=1.2, alpha=0.85, label="Simulation")
        ax2.set_xlabel("Recorded step (100 x 0.01 ramp)")
        ax2.set_ylabel("Load factor")
        ax2.set_title("Dino_SolidBrick -- load factor history")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "loadramp_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable -- skipping compare plot)")

    # Verification summary
    n_sim = hist.shape[1] if hist is not None else 0
    print(f"\n  Recorded steps: {n_sim} / {N_TOTAL_STEPS} expected")
    if hist is not None and n_sim > 0:
        labels = ("LF", "UX", "UY", "UZ")
        for d in range(4):
            print(f"  Sim node{NODE_MONITOR} {labels[d]} final = "
                  f"{float(hist[d, -1]):.6f}")
        if ref is not None and ref.shape[1] > 0:
            n = min(n_sim, ref.shape[1])
            for d in range(4):
                sv, rv = hist[d, :n], ref[d, :n]
                rms = float(np.sqrt(np.mean((sv - rv) ** 2)))
                denom = np.maximum(np.abs(rv), 1e-12)
                rel = float(np.mean(np.abs(sv - rv) / denom) * 100.0)
                print(f"    ramp {labels[d]}: per-point RMS {rms:.6f} | "
                      f"mean rel error {rel:.4f}%")
        rs = results.get("ref_single")
        if rs is not None:
            print(f"  snode102.out final: LF={rs[0]:.6f} UX={rs[1]:.6f} "
                  f"UY={rs[2]:.6f} UZ={rs[3]:.6f}")
        rf = results.get("ref_field")
        if rf is not None:
            print(f"  Full-field reference: {rf.shape[0]} nodes assembled "
                  f"from node0-4.out")
            try:
                opst.post.set_odb_path(str(output_dir))
                ds = opst.post.get_nodal_responses(
                    odb_tag=ODB_TAG, resp_type="disp", print_info=False)
                tags = sorted(int(t) for t in ds.nodeTags.values)
                simf = np.array([ds.sel(nodeTags=t).isel(
                    DOFs=[0, 1, 2]).values.astype(float)[-1] for t in tags])
                n = min(simf.shape[0], rf.shape[0])
                f_rms = float(np.sqrt(np.mean((simf[:n] - rf[:n]) ** 2)))
                f_denom = np.maximum(np.abs(rf[:n]), 1e-12)
                f_rel = float(np.mean(np.abs(simf[:n] - rf[:n])
                                      / f_denom) * 100.0)
                print(f"    full-field ({n} nodes): RMS {f_rms:.6f} mm | "
                      f"mean rel error {f_rel:.4f}%")
            except Exception as e:
                print(f"    (full-field sim read failed: {e})")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_SolidBrick: analysis complete.")
