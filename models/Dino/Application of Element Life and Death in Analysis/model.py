# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Element Birth/Death — Progressive Shell Removal (elastic)
UniqueID : Dino_LifeDeath_shell
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-12
Purpose  : Demonstrate the "element life and death" technique: a gravity-loaded
           elastic flat shell (6 m x 3 m, 100 ShellMITC4 elements) has an 8-
           element rectangular "hole" removed group-by-group mid-analysis,
           driving load redistribution under the frozen gravity field.  Orphan
           nodes left dangling by each removal are re-pinned to keep the
           stiffness matrix non-singular.
Ref      : Dino -- Application of Element Life and Death in Analysis
           (original co.tcl)
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
# Materials (match source co.tcl tags exactly)
# NOTE -- the source defines three materials (Elastic 1, ElasticIsotropic 2,
# Elastic 3) but only nDMaterial 2 is referenced (by the PlateFiber wrapper).
# The two uniaxial Elastic materials (1, 3) are dead -- never bound to any
# element/section -- so they are omitted here per §12ap-6 / §12av-5 (dead
# materials dropped, not stub-defined).
MAT_ELASTIC_3D = 2      # ElasticIsotropic (the only live material)
MAT_PLATEFIBER = 601    # PlateFiber nDMaterial wrapping mat 2

# Section
SEC_WALL = 701          # PlateFiber section, 300 mm thick (source: "##W300")
# SEC_SLAB = 702        # source also defines a 250 mm "##SLAB1" section that is
                        # never used by any element -- dead section, omitted.

# Nodes / elements (121 nodes, 100 ShellMITC4) -- parsed verbatim from co.tcl
NODE_MONITOR = 88       # validation node (top of slab, x=3.0 m, z=3.0 m)

# Time series / patterns
TS_GRAVITY  = 1
PAT_GRAVITY = 1
TS_DEATH    = 2          # empty pattern 2 (no new load; frozen gravity drives)
PAT_DEATH   = 2

# ODB
ODB_TAG = 1

# Source files
TCL_FILE = Path(__file__).parent / "tcl_ref" / "co.tcl"
REF_FILE = Path(__file__).parent / "tcl_ref" / "node88.out"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N).

# Geometry -- flat shell in the x-z plane (y=0), 6 m wide x 3 m tall, refined
# into 100 ShellMITC4 quads over a 121-node mesh.
W_SLAB = 6000.0 * mm
H_SLAB = 3000.0 * mm

# Material -- ElasticIsotropic (source line 275)
E_SHELL = 2.482e4 * MPa       # N/mm^2 (concrete-ish, low E)
NU_SHELL = 0.2                # Poisson's ratio

# Section -- PlateFiber, 300 mm thick (source line 280: "##W300")
T_WALL = 300.0 * mm

# Loading -- 9 loaded nodes, -1e6 N UZ each (source lines 395-403) = -9 MN total
P_GRAVITY = -1.0e6 * N
LOADED_NODES = [14, 20, 26, 32, 56, 72, 88, 104, 120]

# Gravity analysis (source lines 406-413)
N_GRAV_STEPS    = 10
GRAV_LAMBDA_STEP = 1.0 / N_GRAV_STEPS    # LoadControl 0.1

# Element-death sequence (source lines 432-450): 8 elements removed one group
# at a time, each followed by analyze(4).  Order matters -- later removals
# depend on earlier ones having already shed load.  Three nodes become
# orphaned (all 4 connected elements gone) and MUST be re-pinned at the noted
# stage or the global K goes singular:
#   node 67 orphaned after e32,e50,e31,e49  -> pin at the e49 stage
#   node 81 orphaned after e49,e50,e51,e52  -> pin at the e51 stage
#   node 83 orphaned after e51,e52,e69,e70  -> pin at the e69 stage
# Each tuple: (element to remove, optional orphan node to pin, label).
DEATH_SEQUENCE = [
    (32, None, "e32"),
    (50, None, "e50"),
    (52, None, "e52"),
    (70, None, "e70"),
    (31, None, "e31"),
    (49, 67,   "e49 (+pin 67)"),
    (51, 81,   "e51 (+pin 81)"),
    (69, 83,   "e69 (+pin 83)"),
]
N_DEATH_STEPS_PER_STAGE = 4
N_DEATH_STAGES = len(DEATH_SEQUENCE)            # 8
N_DEATH_STEPS = N_DEATH_STAGES * N_DEATH_STEPS_PER_STAGE   # 32

# Total expected recorded steps = gravity + death
N_TOTAL_STEPS = N_GRAV_STEPS + N_DEATH_STEPS    # 42


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Elastic shell material chain (source lines 275, 279-280).

    ElasticIsotropic (3D) -> PlateFiber nDMaterial (flattens the 3D law to a
    2D plane-stress plate through the thickness).  The two dead uniaxial
    Elastic materials in the source (mat 1, mat 3) are omitted (§12ap-6).
    """
    ops.nDMaterial("ElasticIsotropic", MAT_ELASTIC_3D, E_SHELL, NU_SHELL)
    ops.nDMaterial("PlateFiber", MAT_PLATEFIBER, MAT_ELASTIC_3D)


# ── 6. SECTION (PlateFiber) ──────────────────────────────────────────────────
def define_section() -> None:
    """PlateFiber section, 300 mm thick (source line 280).

    The source also defines a 250 mm "##SLAB1" section (702) that no element
    references; it is omitted here as a dead section.
    """
    ops.section("PlateFiber", SEC_WALL, MAT_PLATEFIBER, T_WALL)


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def _parse_tcl(path: Path) -> str:
    return path.read_text()


def define_nodes(src: str) -> None:
    """Create the 121 nodes + lumped mass from co.tcl (lines 5-149), verbatim.

    The shell lies in the x-z plane (y=0).  Mass is applied on UX and UY at
    a subset of nodes (zero on UZ/rotations).
    """
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))
    # masses: "mass <tag> <mx> <my> 0 0 0 0"
    for m in re.finditer(
        r"^mass\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.mass(int(m.group(1)), float(m.group(2)), float(m.group(3)),
                 0.0, 0.0, 0.0, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Apply the INITIAL fixities from co.tcl (lines 151-271), verbatim.

    Five "support-line" nodes (1, 2, 5, 15, 21, 27, 37, 58, 74, 90, 106 -- the
    x=0/600/1200/.../5400 mm, z=0 base nodes) are fully fixed; all other
    nodes are fixed only in the three rotations (translations free), the
    standard out-of-plane/drilling-restraint pattern for a flat shell.

    NOTE -- the source ALSO contains three later ``fix 67/81/83 1 1 1 1 1 1``
    lines (lines 443/446/449) that re-pin orphaned nodes mid-death-phase.
    Those MUST be excluded from this initial parse or OpenSees errors with
    "cannot add SP -- node already constrained" when the death-phase re-pin
    tries to add a duplicate SP.  We isolate the initial-BC block by slicing
    ``src`` at the ``puts "material"`` marker (the section that follows BCs).
    """
    bc_block = src.split('puts "material"')[0]
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)", bc_block, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> int:
    """Create the 100 ShellMITC4 quads from co.tcl (lines 287-386), verbatim.

    ShellMITC4 (MITC4 mixed-interpolation 4-node shell) takes the PlateFiber
    section tag directly as its last arg.  Returns the number of elements
    created (for a sanity check).
    """
    n = 0
    for m in re.finditer(
        r"^element\s+ShellMITC4\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+701",
        src, re.M,
    ):
        tag = int(m.group(1))
        n1, n2, n3, n4 = (int(m.group(i)) for i in range(2, 6))
        ops.element("ShellMITC4", tag, n1, n2, n3, n4, SEC_WALL)
        n += 1
    return n


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for an element-birth/death shell model.

    ``model_update=True`` is MANDATORY here (§12ax): elements are removed
    mid-analysis, so the ODB must re-query the live element set each step.
    With ``model_update=False`` the removed tags persist and the per-step
    response arrays misalign; with ``True`` opstool stores each step's data
    as a standalone dataset and concatenates with ``xr.concat(join="outer")``,
    so removed elements simply drop out of later steps.  Tag filters
    (``node_tags``/``shell_tags``) MUST be omitted (let the ODB track all
    live tags).  ``save_shell_resp=True``; ``save_frame_resp=False`` (no beam
    elements).  ``set_odb_path`` precedes ``CreateODB`` (§12ac).
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=True,        # §12ax: required for element death
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
        save_shell_resp=True,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Axial (UZ) gravity at the 9 loaded nodes (pattern 1).  BEFORE loadConst."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    for n in LOADED_NODES:
        ops.load(n, 0.0, 0.0, P_GRAVITY, 0.0, 0.0, 0.0)


def define_death_pattern() -> None:
    """Empty lateral pattern 2 (source line 419-421: ``pattern Plain 2 Linear {}``).

    No load is added in the death phase -- the frozen gravity (from
    ``loadConst``) provides the internal forces, and each ``analyze(4)``
    simply re-equilibrates the model under the reduced stiffness as an
    element is removed.  The empty pattern exists only so the LoadControl
    integrator has a time series to advance against, matching the source's
    pseudo-time progression (t = 2,3,4,5 after the first removal, etc.).
    """
    ops.timeSeries("Linear", TS_DEATH)
    ops.pattern("Plain", PAT_DEATH, TS_DEATH)   # no loads -- intentionally empty


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB") -> bool:
    """Apply gravity via a manual LoadControl loop (§3c permitted exception).

    Source settings (lines 406-413): Plain constraints, Plain numberer,
    BandGeneral SOE, EnergyIncr 1e-6/200, Newton, LoadControl 0.1, 10 steps.
    Ends with ``loadConst`` + ``wipeAnalysis``.
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", GRAV_LAMBDA_STEP)
    ops.analysis("Static")

    ok = 0
    for step in range(N_GRAV_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"  WARNING: gravity step {step} failed (ok={ok})")
            break
        odb.fetch_response_step()

    print(f"  Gravity converged to lambda={ops.getTime():.4f} (target 1.0)")
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()
    return ok == 0


def run_element_death(odb: "opst.post.CreateODB") -> list[float]:
    """Drive the progressive element-removal sequence (source lines 423-450).

    SmartAnalyze has no element-death hooks (§12ax-4), so this is a manual
    ``ops.analyze()`` loop.  For each stage: remove the element, pin any node
    that just became orphaned, then ``analyze(4)`` under the frozen gravity.
    The solver is reconfigured verbatim from the source (Transformation
    constraints, RCM, SparseGeneral, NormDispIncr 1e-4/60/1, KrylovNewton,
    LoadControl 1).

    Returns the node-88 UZ history (mm) at every recorded step (42 values:
    10 gravity + 32 death), for validation against ``node88.out``.
    """
    # Solver for the death phase (source lines 423-429) -- verbatim.
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("SparseGeneral")
    ops.test("NormDispIncr", 1.0e-4, 60, 1)
    ops.algorithm("KrylovNewton")
    ops.integrator("LoadControl", 1)
    ops.analysis("Static")

    uz_hist: list[float] = []
    stage_labels: list[str] = []

    for (etag, orphan, label) in DEATH_SEQUENCE:
        # 1. remove the element (ops.remove('ele', ...) -- §12ax-2)
        ops.remove("ele", etag)
        # 2. pin the orphan node if this removal isolates it (§12ax-1).
        # Pin only the 3 TRANSLATIONS -- the rotations were already fixed in
        # the initial BC (every non-support node starts as 0 0 0 1 1 1), and
        # OpenSeesPy errors on a duplicate SP where Tcl's ``fix ... 1 1 1 1 1 1``
        # silently no-ops the already-constrained rotational DOFs (§12ax-3).
        if orphan is not None:
            ops.fix(orphan, 1, 1, 1, 0, 0, 0)
        # 3. re-equilibrate under frozen gravity over 4 steps
        ok = ops.analyze(N_DEATH_STEPS_PER_STAGE)
        if ok != 0:
            print(f"  WARNING: death stage '{label}' failed (ok={ok})")
        for _ in range(N_DEATH_STEPS_PER_STAGE):
            odb.fetch_response_step()
            uz_hist.append(float(ops.nodeDisp(NODE_MONITOR, 3)))   # UZ (mm)
            stage_labels.append(label)

    print(f"  Element death: removed {N_DEATH_STAGES} elements across "
          f"{N_DEATH_STEPS} steps; final node{NODE_MONITOR} UZ = "
          f"{uz_hist[-1]:.5f} mm")
    return uz_hist


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run gravity + element-death, return ODB + results.

    Returns:
        (odb, results) where results has keys: uz (mm, sim node-88 history),
        ref_uz (mm, reference node-88 history), stage_labels.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    src = _parse_tcl(TCL_FILE)

    init_model()
    define_materials()
    define_section()
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_ele = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_ele} ShellMITC4 elements "
          f"(expected 100, section {SEC_WALL}).")

    odb = create_odb(output_dir)

    # Phase 1: gravity (before loadConst)
    define_gravity_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running gravity analysis...")
    run_gravity(odb)

    # Phase 2: empty pattern 2 + element death (after loadConst)
    define_death_pattern()
    print("Running element-death sequence...")
    death_uz = run_element_death(odb)

    # The death-phase UZ is collected in-memory (for the early progress print);
    # the FULL 42-step node-88 UZ history (gravity + death) is read back from
    # the flushed ODB in post_process, which is cleaner than reconstructing the
    # gravity branch here.  results["uz"] starts as the death-only history and
    # is overwritten with the full history once the ODB is flushed.
    uz_hist = death_uz

    # Reference node-88 UZ (node88.out: col0=time, col1=UX, col2=UY, col3=UZ)
    ref_uz = None
    if REF_FILE.exists():
        ref_uz = []
        with open(REF_FILE) as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 4:
                    ref_uz.append(float(parts[3]))

    results = {
        "uz": np.array(uz_hist),
        "ref_uz": np.array(ref_uz) if ref_uz else None,
    }

    if len(uz_hist) > 0 and len(uz_hist) == len(ref_uz) if ref_uz is not None else False:
        curve = np.column_stack([np.arange(1, len(uz_hist) + 1), uz_hist])
        np.savetxt(str(output_dir / "node88_uz_history.csv"), curve,
                   delimiter=",", header="step,uz_mm")

    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot node-88 UZ history, verify.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from ``run_analysis`` (may have an incomplete
                 ``uz``; the full 42-step history is read back from the
                 flushed ODB here).
    """
    odb.save_response()

    # Read the full node-88 UZ history (all 42 steps) from the flushed ODB.
    full_uz = _read_node88_history_from_odb()
    if len(full_uz) > 0:
        results["uz"] = np.array(full_uz)
        curve = np.column_stack([np.arange(1, len(full_uz) + 1),
                                 np.array(full_uz)])
        np.savetxt(str(output_dir / "node88_uz_history.csv"), curve,
                   delimiter=",", header="step,uz_mm")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))

        # V5 -- final deformed shape (last step, UZ).  model_update=True means
        # the hole left by the removed elements is visible in the mesh.
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UZ", scale=200.0)

        # V6 -- step slider (scrub through gravity + 8 removal stages)
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UZ", scale=200.0)

        # V7 -- animation (the hole grows stage by stage)
        vis_anim(output_dir, filename="vis_07_animation.html",
                 odb_tag=ODB_TAG, defo_scale=200.0,
                 resp_dof=("UX", "UY", "UZ"))

    # Node-88 UZ-vs-step: simulation vs reference (matplotlib)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        sim = results["uz"]
        ref = results["ref_uz"]
        fig, ax = plt.subplots(1, 1, figsize=(8, 5))
        if ref is not None and len(ref) > 0:
            ax.plot(np.arange(1, len(ref) + 1), ref, "k-",
                    linewidth=1.0, alpha=0.6, label="Reference (node88.out)")
        if len(sim) > 0:
            ax.plot(np.arange(1, len(sim) + 1), sim, "r--",
                    linewidth=1.2, alpha=0.85, label="Simulation")
        # mark the gravity/death boundary and each removal stage
        ax.axvline(N_GRAV_STEPS, color="0.5", linewidth=0.8, linestyle=":",
                   label=f"gravity end (step {N_GRAV_STEPS})")
        for i, (_, _, label) in enumerate(DEATH_SEQUENCE):
            xpos = N_GRAV_STEPS + i * N_DEATH_STEPS_PER_STAGE + 1
            ax.axvline(xpos, color="0.85", linewidth=0.5)
        ax.set_xlabel("Recorded step (10 gravity + 8 stages x 4)")
        ax.set_ylabel(f"Node {NODE_MONITOR} UZ displacement (mm)")
        ax.set_title("Dino_LifeDeath_shell -- node 88 UZ, element birth/death")
        ax.axhline(0.0, color="0.6", linewidth=0.5)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "node88_uz_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable -- skipping UZ plot)")

    # Verification summary
    sim = results["uz"]
    ref = results["ref_uz"]
    print(f"\n  Recorded steps: {len(sim)} / {N_TOTAL_STEPS} expected")
    if len(sim) > 0:
        # post-gravity UZ = step 10 (index 9); final = last
        grav_idx = min(N_GRAV_STEPS - 1, len(sim) - 1)
        sim_grav = float(sim[grav_idx])
        sim_final = float(sim[-1])
        print(f"  Sim: post-gravity UZ = {sim_grav:.5f} mm | "
              f"final UZ = {sim_final:.5f} mm")
        if ref is not None and len(ref) > 0:
            ref_grav = float(ref[grav_idx])
            ref_final = float(ref[-1])
            print(f"  Ref: post-gravity UZ = {ref_grav:.5f} mm | "
                  f"final UZ = {ref_final:.5f} mm")
            for name, sv, rv in (("post-gravity", sim_grav, ref_grav),
                                 ("final",       sim_final, ref_final)):
                denom = abs(rv) if rv != 0 else 1.0
                print(f"    {name:14s} diff: {100.0*abs(sv-rv)/denom:.3f}%")
            # per-point RMS over the common range
            n = min(len(sim), len(ref))
            if n > 0:
                rms = float(np.sqrt(np.mean((sim[:n] - ref[:n]) ** 2)))
                print(f"  Per-point RMS over {n} steps: {rms:.5f} mm")


def _read_node88_history_from_odb() -> list[float]:
    """Read node 88's UZ at every recorded step from the flushed ODB.

    With ``model_update=True`` the ``node_tags`` filter is unreliable (it can
    return the wrong node -- a §12ax quirk), so we read ALL nodes and select
    node 88 by coordinate.  The ODB stores 43 frames: the t=0.0 pre-analysis
    zero state plus 42 recorded steps (10 gravity + 32 death); the leading
    zero-frame is dropped to align 1:1 with the 42-row reference (§12am).

    Returns an empty list if the read fails (caller falls back to in-memory).
    """
    try:
        ds = opst.post.get_nodal_responses(
            odb_tag=ODB_TAG, resp_type="disp", print_info=False,
        )
        # ds: DataArray (time, nodeTags, DOFs); DOFs = UX,UY,UZ,RX,RY,RZ
        uz = (ds.sel(nodeTags=NODE_MONITOR)
               .isel(DOFs=2)        # UZ
               .values.astype(float))
        return uz[1:].tolist()      # drop the t=0.0 zero frame -> 42 steps
    except Exception:
        return []


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_LifeDeath_shell: analysis complete.")
