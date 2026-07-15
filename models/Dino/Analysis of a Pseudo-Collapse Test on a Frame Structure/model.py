# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Pseudo-Collapse Test on a Frame Structure (OpenSees Example 2.9)
UniqueID : Dino_PseudoCollapse
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-15
Purpose  : Gravity + force-controlled pushdown of a 3D RC moment frame
           (3 bays x 3 bays x 4 storeys; 44 nodes, 83 nonlinearBeamColumn
           elements; two Steel01/Concrete02 fiber sections wrapped in rigid
           shear+torsion Aggregators).  Node 35 (a ground-level corner) is
           first pulled UP 300 kN under beam UDLs (gravity, 10 steps), then
           pushed DOWN 300 kN (pushdown, 100 steps) = 110 recorded steps.
           The two load signs do not cancel: phase 2 starts from the frozen
           gravity state, so UZ grows monotonically to ~-17 mm -- this is the
           "pseudo-collapse" displacement demand.  Node-35 history is
           validated against tcl_ref/node35.out.
Ref      : Dino -- Analysis of a Pseudo-Collapse Test on a Frame Structure
           (original co.tcl, a.k.a. EXAM29.tcl)
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
MAT_STEEL      = 1      # Steel01 rebar (fiber sections)
MAT_CONCRETE   = 2      # Concrete02 concrete (fiber sections)
# NOTE -- source also defines uniaxialMaterial Elastic 3 (1.999e5) which is
# never referenced by any fiber/element -> dead, omitted (§12ap-6).
# Rigid shear + torsion materials feeding the two Aggregators (kept verbatim):
MAT_VY_1   = 201
MAT_VZ_1   = 301
MAT_T_1    = 401
MAT_VY_2   = 202
MAT_VZ_2   = 302
MAT_T_2    = 402

# Fiber sections (NC500X500 column, NB300X600 beam) + their Aggregator wrappers.
SEC_FIBER_COL = 1       # section Fiber 1 -- NC500X500
SEC_FIBER_BM  = 2       # section Fiber 2 -- NB300X600
SEC_COL       = 1001    # section Aggregator wrapping fiber 1 (+Vy/Vz/T)
SEC_BM        = 1002    # section Aggregator wrapping fiber 2 (+Vy/Vz/T)

# Validation
NODE_MONITOR  = 35      # node-35 disp validated against node35.out
                            # (ground corner, coords (0,0,3000) mm)

# Time series / patterns
TS_GRAVITY    = 1
PAT_GRAVITY   = 1
TS_PUSH       = 2       # pushdown (force-controlled, after loadConst)
PAT_PUSH      = 2

# ODB
ODB_TAG       = 1

# Source files
TCL_FILE      = Path(__file__).parent / "tcl_ref" / "co.tcl"
REF_FILE      = Path(__file__).parent / "tcl_ref" / "node35.out"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N).

# Materials -- Steel01 (source line 107)
STEEL_FY = 300.0 * MPa          # N/mm^2
STEEL_E  = 206000.0 * MPa       # N/mm^2
STEEL_B  = 0.01                 # strain-hardening ratio

# Concrete02 (source line 108) -- 7-arg, verbatim
# fpc, epsc0, fpcu, epsU, lambda, ft, Ets
CONC_FPC    = -20.0 * MPa
CONC_EPSC0  = -0.002
CONC_FPCU   = -5.0 * MPa
CONC_EPSU   = -0.0033
CONC_LAMBDA = 0.1
CONC_FT     = 2.2 * MPa
CONC_ETS    = 1100.0            # Ets (slope of tension-softening, MPa units)

# Rigid shear/torsion stiffnesses for the Aggregators (source lines 112-117).
# In a section Aggregator the Vy/Vz codes bind a uniaxial material to the
# shear force-deformation and T to torsion; the source sets these to very
# large numbers (rigid) so all deformation is carried by the fiber section.
K_VY_1 = 2.170e9    # sec 1 Vy (mat 201)
K_VZ_1 = 2.170e9    # sec 1 Vz (mat 301)
K_T_1  = 9.169e13   # sec 1 T  (mat 401)
K_VY_2 = 1.562e9    # sec 2 Vy (mat 202)
K_VZ_2 = 1.562e9    # sec 2 Vz (mat 302)
K_T_2  = 3.862e13   # sec 2 T  (mat 402)

# Torsional stiffness GJ for the bare fiber sections (§12au).  The Tcl source
# omits -GJ (Tcl only warns); OpenSeesPy 3D ``section Fiber`` REQUIRES it.  The
# Aggregator's rigid T code (mat 401/402) dominates torsion regardless, so the
# fiber-section GJ is a fallback -- set from the steel G (concrete contribution
# negligible) as G*Sum(A*r^2), computed per-section from the parsed fibers in
# define_sections().  This value only seeds the constant; it is overwritten.
SEC_GJ = 1.0e10     # N*mm^2  (placeholder; recomputed in define_sections)

# Loading (source lines 376, 377-504, 519)
P_NODE_GRAV = 3.0e5 * N     # phase 1 node-35 UZ (up)
P_NODE_PUSH = -3.0e5 * N    # phase 2 node-35 UZ (down)
W_BEAM      = -6.375        # N/mm (beamUniform: Wy=0, Wz=-6.375, no axial)
# (the source writes every beam load twice over; the recorder's time column
#  therefore advances by 0.1 per gravity step and 0.01 per pushdown step.)

# Analysis -- both phases are LoadControl (source lines 512, 527)
N_IP          = 3            # nonlinearBeamColumn integration points
N_GRAV_STEPS  = 10
GRAV_LAMBDA   = 0.1          # LoadControl step (-> t = 1.0 after gravity)
N_PUSH_STEPS  = 100
PUSH_LAMBDA   = 0.01         # LoadControl step (-> t = 1.0 after pushdown)

# Total expected recorded steps = gravity + pushdown
N_TOTAL_STEPS = N_GRAV_STEPS + N_PUSH_STEPS    # 110


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Steel01 + Concrete02 + rigid Elastic shear/torsion (source lines 107-117).

    Steel01/Concrete02 feed the two fiber sections; the six Elastic materials
    are the rigid shear (Vy/Vz) and torsion (T) codes used by the two section
    Aggregators.  The dead ``Elastic 3`` (1.999e5, never referenced) is omitted
    (§12ap-6).
    """
    ops.uniaxialMaterial("Steel01", MAT_STEEL, STEEL_FY, STEEL_E, STEEL_B)
    ops.uniaxialMaterial("Concrete02", MAT_CONCRETE,
                         CONC_FPC, CONC_EPSC0, CONC_FPCU, CONC_EPSU,
                         CONC_LAMBDA, CONC_FT, CONC_ETS)

    ops.uniaxialMaterial("Elastic", MAT_VY_1, K_VY_1)
    ops.uniaxialMaterial("Elastic", MAT_VZ_1, K_VZ_1)
    ops.uniaxialMaterial("Elastic", MAT_T_1,  K_T_1)
    ops.uniaxialMaterial("Elastic", MAT_VY_2, K_VY_2)
    ops.uniaxialMaterial("Elastic", MAT_VZ_2, K_VZ_2)
    ops.uniaxialMaterial("Elastic", MAT_T_2,  K_T_2)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def _parse_fiber_block(src: str, sec_tag: int) -> list[tuple[float, float, float, int]]:
    """Return [(y, z, area, matTag), ...] for one ``section Fiber N { ... }`` block."""
    # capture from the opening brace to its matching close
    m = re.search(rf"section\s+Fiber\s+{sec_tag}\s*\{{(.*?)\n\}}", src, re.S)
    if not m:
        return []
    body = m.group(1)
    fibers: list[tuple[float, float, float, int]] = []
    for fm in re.finditer(
        r"fiber\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+(\d+)", body
    ):
        fibers.append((float(fm.group(1)), float(fm.group(2)),
                       float(fm.group(3)), int(fm.group(4))))
    return fibers


def define_sections(src: str) -> None:
    """Rebuild the two fiber sections + Aggregators (source lines 118-197).

    VERBATIM FIBER REPLAY (§12aq): the concrete + rebar fibers are parsed from
    co.tcl and re-emitted with ops.fiber(), preserving exact centroid + area
    (re-meshing risks A/I drift and breaks the displacement match).  Each fiber
    section is then wrapped by a section Aggregator adding rigid Vy/Vz/T codes,
    matching the source's 1001/1002 so nonlinearBeamColumn binds the same
    aggregated section.

    -GJ (§12au): OpenSeesPy 3D ``section Fiber`` REQUIRES -GJ (Tcl only warns);
    computed per-section as G_steel * Sum(A*r^2) from the parsed fibers.  The
    Aggregator's rigid T code (mat 401/402) dominates torsion regardless, so
    this GJ is only a fallback and has negligible effect on results.
    """
    g_steel = STEEL_E / (2.0 * (1.0 + 0.3))     # G = E/(2(1+nu)), nu~0.3

    for sec_tag, fiber_tag in ((SEC_FIBER_COL, SEC_FIBER_COL),
                               (SEC_FIBER_BM,  SEC_FIBER_BM)):
        fibers = _parse_fiber_block(src, sec_tag)
        gj = g_steel * sum(a * (y * y + z * z) for (y, z, a, _) in fibers)
        ops.section("Fiber", fiber_tag, "-GJ", gj)
        for (y, z, area, mat) in fibers:
            # OpenSeesPy fiber signature: fiber(y, z, area, matTag)
            ops.fiber(y, z, area, mat)

    # section Aggregator 1001 -- NC500X500 (fiber 1) + rigid Vy/Vz/T
    ops.section("Aggregator", SEC_COL,
                MAT_VY_1, "Vy", MAT_VZ_1, "Vz", MAT_T_1, "T",
                "-section", SEC_FIBER_COL)
    # section Aggregator 1002 -- NB300X600 (fiber 2) + rigid Vy/Vz/T
    ops.section("Aggregator", SEC_BM,
                MAT_VY_2, "Vy", MAT_VZ_2, "Vz", MAT_T_2, "T",
                "-section", SEC_FIBER_BM)


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 44 nodes + lumped mass from co.tcl (lines 5-94), verbatim.

    The frame is 3 bays x 3 bays in plan (6 m bay) x 4 storeys (3 m each).
    Mass is applied on UX and UY only (zero on UZ/rotations) at the upper
    nodes; the base nodes 37-44 get a small 0.9187 mass.
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
    """Pin the 8 base nodes 37-44 (translations fixed, rotations free).

    Source lines 96-103: ``fix 37..44 1 1 1 0 0 0``.  Only the initial-BC fix
    lines are matched -- there are no death-phase re-pins in this model, but
    the regex is anchored to 6 binary fields so only genuine fix commands hit.
    """
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> int:
    """Create the 83 geomTransf + nonlinearBeamColumn from co.tcl (lines 202-368).

    geomTransf Linear (source lines 202-284): 83 transforms, each with an
    orientation vector of either (1,0,0) or (0,0,1) -- the source uses
    alternating vectorxz to orient columns vs beams.  nonlinearBeamColumn
    (lines 286-368): ``(tag, i, j, nIP=3, secTag, transfTag)`` -- the native
    signature is retained (§12l: NOT converted to dispBeamColumn).  secTag is
    1001 (Aggregator/column) for the verticals and 1002 (Aggregator/beam) for
    the horizontals.  Returns the number of elements created.
    """
    for m in re.finditer(
        r"^geomTransf\s+Linear\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)",
        src, re.M,
    ):
        ops.geomTransf("Linear", int(m.group(1)),
                       float(m.group(2)), float(m.group(3)), float(m.group(4)))

    n = 0
    for m in re.finditer(
        r"^element\s+nonlinearBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        src, re.M,
    ):
        tag = int(m.group(1))
        n1, n2 = int(m.group(2)), int(m.group(3))
        nip = int(m.group(4))
        sec = int(m.group(5))
        transf = int(m.group(6))
        ops.element("nonlinearBeamColumn", tag, n1, n2, nip, sec, transf)
        n += 1
    return n


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a static nonlinear frame model.

    ``save_frame_resp=False`` (§12v) -- nonlinearBeamColumn uses internal
    sections with no user-visible tags; enabling frame response raises
    ``sectionForceDeformation(tag=0) not found``.  ``model_update=False`` --
    no elements are removed/added mid-analysis (unlike §12ax).  ``set_odb_path``
    precedes ``CreateODB`` (§12ac).
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
        save_shell_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads(src: str) -> None:
    """Phase-1 gravity pattern (source lines 375-505): BEFORE loadConst.

    Node 35 gets +3e5 N UZ (upward); each of the 128 eleLoad lines applies a
    beamUniform ``0 -6.375 0`` (Wy=0, Wz=-6.375 N/mm, no axial) -- the source
    writes most beams 2-4x, and every line is replayed verbatim so the total
    load (and hence the displacement match) is identical to the Tcl run.
    """
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)

    ops.load(NODE_MONITOR, 0.0, 0.0, P_NODE_GRAV, 0.0, 0.0, 0.0)

    for m in re.finditer(r"^eleLoad\s+-ele\s+(\d+)\s+-type\s+-beamUniform"
                         r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M):
        ele = int(m.group(1))
        wy, wz, wx = float(m.group(2)), float(m.group(3)), float(m.group(4))
        ops.eleLoad("-ele", ele, "-type", "-beamUniform", wy, wz, wx)


def define_pushdown_loads() -> None:
    """Phase-2 pushdown pattern (source lines 518-520): AFTER loadConst (§12z-1).

    A second Plain pattern on its own Linear time series applies -3e5 N UZ at
    node 35.  Defined after ``loadConst`` so the gravity load is frozen and
    only this new pattern advances during the pushdown phase.
    """
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    ops.load(NODE_MONITOR, 0.0, 0.0, P_NODE_PUSH, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def _configure_solver() -> None:
    """Source solver (lines 507-513 / 522-528), verbatim for both phases."""
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Newton")


def run_gravity(odb: "opst.post.CreateODB") -> bool:
    """Phase 1 -- gravity (source lines 506-514): LoadControl 0.1, 10 steps.

    Manual ``ops.analyze()`` loop is the §3c permitted exception for LoadControl
    (SmartAnalyze forces DisplacementControl).  Ends with ``loadConst`` +
    ``wipeAnalysis`` so phase 2 starts from a frozen, clean solver state.
    """
    _configure_solver()
    ops.integrator("LoadControl", GRAV_LAMBDA)
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


def run_pushdown(odb: "opst.post.CreateODB") -> bool:
    """Phase 2 -- pushdown (source lines 521-529): LoadControl 0.01, 100 steps.

    Force-controlled, so again a manual ``ops.analyze()`` loop (§3c exception).
    No ``loadConst`` here -- this is the final phase.
    """
    _configure_solver()
    ops.integrator("LoadControl", PUSH_LAMBDA)
    ops.analysis("Static")

    ok = 0
    for step in range(N_PUSH_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"  WARNING: pushdown step {step} failed (ok={ok})")
            break
        odb.fetch_response_step()

    print(f"  Pushdown converged to lambda={ops.getTime():.4f} (target 1.0)")
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run gravity + pushdown, return ODB + results.

    Returns:
        (odb, results) where results has keys: disp (3,N) sim node-35
        [UX,UY,UZ] history (mm), ref_disp (3,N) reference from node35.out.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    src = TCL_FILE.read_text()

    init_model()
    define_materials()
    define_sections(src)
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_ele = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_ele} nonlinearBeamColumn elements "
          f"(expected 83).")

    odb = create_odb(output_dir)

    # Phase 1: gravity (before loadConst)
    define_gravity_loads(src)
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running gravity analysis...")
    run_gravity(odb)

    # Phase 2: pushdown (after loadConst)
    define_pushdown_loads()
    print("Running pushdown analysis...")
    run_pushdown(odb)

    # Reference node-35 disp (node35.out: col0=time, col1=UX, col2=UY, col3=UZ)
    ref_disp = None
    if REF_FILE.exists():
        ref = np.loadtxt(str(REF_FILE))
        ref_disp = ref[:, 1:4].T      # (3, N) -> [UX, UY, UZ]

    results = {"disp": None, "ref_disp": ref_disp}
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def _read_node35_history_from_odb() -> np.ndarray:
    """Read node 35's [UX,UY,UZ] at every recorded step from the flushed ODB.

    Returns a (3, N) array; empty on failure.  The ODB stores N+1 frames (the
    t=0 pre-analysis zero state plus N recorded steps); the leading zero-frame
    is dropped to align 1:1 with the 110-row reference (§12am).
    """
    try:
        ds = opst.post.get_nodal_responses(
            odb_tag=ODB_TAG, resp_type="disp", print_info=False,
        )
        # ds: DataArray (time, nodeTags, DOFs); DOFs = UX,UY,UZ,RX,RY,RZ
        disp = (ds.sel(nodeTags=NODE_MONITOR)
                 .isel(DOFs=[0, 1, 2])      # UX, UY, UZ
                 .values.astype(float))     # (time, 3)
        return disp[1:].T                    # drop t=0 -> (3, N)
    except Exception:
        return np.empty((3, 0))


def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot node-35 history, verify.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis (``disp`` filled here from ODB).
    """
    odb.save_response()

    sim = _read_node35_history_from_odb()
    results["disp"] = sim
    ref = results["ref_disp"]

    # Dump the full node-35 history (gravity + pushdown) for the record.
    if sim.shape[1] > 0:
        step = np.arange(1, sim.shape[1] + 1)
        curve = np.column_stack([step, sim.T])     # (N, 4): step, UX, UY, UZ
        np.savetxt(str(output_dir / "node35_disp_history.csv"), curve,
                   delimiter=",", header="step,ux_mm,uy_mm,uz_mm")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))

        # V5 -- final deformed shape (pushdown is vertical -> UZ)
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UZ", scale=200.0)
        # V6 -- step slider
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UZ", scale=200.0)
        # V7 -- animation
        vis_anim(output_dir, filename="vis_07_animation.html",
                 odb_tag=ODB_TAG, defo_scale=200.0,
                 resp_dof=("UX", "UY", "UZ"))

    # Node-35 UZ-vs-step: simulation vs reference (matplotlib)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 1, figsize=(8, 5))
        if ref is not None and ref.shape[1] > 0:
            ax.plot(np.arange(1, ref.shape[1] + 1), ref[2], "k-",
                    linewidth=1.0, alpha=0.6, label="Reference (node35.out)")
        if sim.shape[1] > 0:
            ax.plot(np.arange(1, sim.shape[1] + 1), sim[2], "r--",
                    linewidth=1.2, alpha=0.85, label="Simulation")
        ax.axvline(N_GRAV_STEPS, color="0.5", linewidth=0.8, linestyle=":",
                   label=f"gravity end (step {N_GRAV_STEPS})")
        ax.set_xlabel("Recorded step (10 gravity + 100 pushdown)")
        ax.set_ylabel(f"Node {NODE_MONITOR} UZ displacement (mm)")
        ax.set_title("Dino_PseudoCollapse -- node 35 UZ, gravity + pushdown")
        ax.axhline(0.0, color="0.6", linewidth=0.5)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "pushdown_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable -- skipping UZ plot)")

    # Verification summary
    print(f"\n  Recorded steps: {sim.shape[1]} / {N_TOTAL_STEPS} expected")
    if sim.shape[1] > 0:
        grav_idx = min(N_GRAV_STEPS - 1, sim.shape[1] - 1)
        labels = ("UX", "UY", "UZ")
        for d in range(3):
            sim_final = float(sim[d, -1])
            print(f"  Sim node{NODE_MONITOR} {labels[d]}: "
                  f"post-gravity = {float(sim[d, grav_idx]):.5f} mm | "
                  f"final = {sim_final:.5f} mm")
        if ref is not None and ref.shape[1] > 0:
            n = min(sim.shape[1], ref.shape[1])
            for d in range(3):
                sv, rv = sim[d, :n], ref[d, :n]
                rms = float(np.sqrt(np.mean((sv - rv) ** 2)))
                denom = np.maximum(np.abs(rv), 1e-12)
                rel = float(np.mean(np.abs(sv - rv) / denom) * 100.0)
                print(f"    {labels[d]}: per-point RMS {rms:.5f} mm | "
                      f"mean rel error {rel:.4f}%")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_PseudoCollapse: analysis complete.")
