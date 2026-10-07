# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Application Analysis of Elastic Shell Unit (Dino Exam13)
UniqueID : Dino_ElasticShell
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-07
Purpose  : Linear-static lateral (PUSH) check (6 x 100 kN UX at top nodes)
           of an L-shaped 100 mm elastic concrete shell wall assembly.
           Nodal displacements validated against ref/OpenSEES/node0.out
           (nodes 1-100) and node1.out (nodes 101-121).
Ref      : Dino -- Application Analysis of Elastic Shell Unit
           (EXAM13.tcl + EXAM13.s2k)
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
# the usual models/<UniqueID>/, so standards/ is parents[3] not parents[2].
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
)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Materials/sections (source tags preserved).
MAT_DEAD_1    = 1    # uniaxial Elastic (dead code -- never referenced)
NDM_ELASTIC   = 2    # nDMaterial ElasticIsotropic (C45 concrete)
MAT_DEAD_3    = 3    # uniaxial Elastic (dead code -- never referenced)
MAT_PLATE     = 601  # nDMaterial PlateFiber wrapping NDM_ELASTIC
SEC_SHELL     = 701  # section PlateFiber (601, 100 mm thick)

# Shell elements carry the source's 1-based tags (1..100); replayed verbatim
# from EXAM13.tcl rather than enumerated as named constants.
ELE_TAG_MIN   = 1
ELE_TAG_MAX   = 100

# Validation
NODE_MONITOR  = 6    # dedicated node6.out recorder in source (file not shipped)

# Time series / patterns (pattern tag 1 matches the source).
TS_PUSH       = 1
PAT_PUSH      = 1

# ODB
ODB_TAG       = 1

# Source files
TCL_FILE      = Path(__file__).parent / "ref" / "OpenSEES" / "EXAM13.tcl"
REF_NODE0     = Path(__file__).parent / "ref" / "OpenSEES" / "node0.out"
REF_NODE1     = Path(__file__).parent / "ref" / "OpenSEES" / "node1.out"

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N, masses in
# N-s^2/mm = tonne). Node coords / masses replayed verbatim (no conversion).

# C45 concrete (ElasticIsotropic 2) + 100 mm PlateFiber shell.
E_CONC   = 32500.0 * MPa
NU_CONC  = 0.2
SHELL_T  = 100.0 * mm

# Dead uniaxial stiffness (tags 1 and 3, kept for fidelity, never referenced).
E_DEAD = 1.999e5 * MPa

# PUSH loads (source pattern Plain 1): 6 x 100 kN UX at the top edge.
P_PUSH = 1.0e5 * N
LOAD_NODES = (4, 6, 79, 90, 101, 112)

# Model size (source counts).
N_NODES = 121
N_ELES  = 100
N_FIX   = 11

# Load ramp: source applies full PUSH in 1 step; we ramp it over 100 equal
# LoadControl increments so the ODB/slider shows the deflection evolving.
# Linear elastic -- final state is identical to the 1-step reference.
N_PUSH_STEPS = 100


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """ElasticIsotropic concrete -> PlateFiber matrix -> PlateFiber section.

    Tags 1 and 3 (uniaxial Elastic) are dead code in the source -- defined
    here for tag fidelity, never referenced by any element/section.
    """
    ops.uniaxialMaterial("Elastic", MAT_DEAD_1, E_DEAD)
    ops.uniaxialMaterial("Elastic", MAT_DEAD_3, E_DEAD)
    ops.nDMaterial("ElasticIsotropic", NDM_ELASTIC, E_CONC, NU_CONC)
    ops.nDMaterial("PlateFiber", MAT_PLATE, NDM_ELASTIC)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    """100 mm PlateFiber shell section (source line, verbatim)."""
    ops.section("PlateFiber", SEC_SHELL, MAT_PLATE, SHELL_T)


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 121 nodes + 22 lumped masses from EXAM13.tcl, verbatim.

    Mass is applied on UX and UY only (zero elsewhere). Values are already
    in N-s^2/mm so no conversion is applied (static PUSH -- mass inactive).
    """
    n = 0
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))
        n += 1
    assert n == N_NODES, f"nodes created {n}, expected {N_NODES}"
    for m in re.finditer(
        r"^mass\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.mass(int(m.group(1)), float(m.group(2)), float(m.group(3)),
                 0.0, 0.0, 0.0, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Apply the 11 fully-fixed base nodes from EXAM13.tcl.

    (The source prints a "rigidDiaphragm" label but issues no MP-constraint
    commands, so Plain constraints are used throughout.)
    """
    n = 0
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)
        n += 1
    assert n == N_FIX, f"fixities applied {n}, expected {N_FIX}"


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> int:
    """Create the 100 ShellMITC4 elements from EXAM13.tcl, verbatim.

    ``element ShellMITC4 tag n1 n2 n3 n4 secTag`` -- the OpenSeesPy signature
    matches the Tcl form directly (no transformation or integration objects
    needed for shells). Returns the number of elements created.
    """
    n = 0
    for m in re.finditer(
        r"^element\s+ShellMITC4\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        src, re.M,
    ):
        ops.element("ShellMITC4", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), int(m.group(4)), int(m.group(5)),
                    int(m.group(6)))
        n += 1
    assert n == N_ELES, f"elements created {n}, expected {N_ELES}"
    return n


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a static shell model.

    ``save_shell_resp=True`` (shells carry the stress response);
    frame/truss responses disabled (no such elements). ``set_odb_path``
    precedes ``CreateODB``. ``model_update=False`` -- topology is static.
    """
    opst.post.set_odb_path(str(output_dir))
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


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_push_loads() -> None:
    """Single Plain pattern (source pattern 1): 6 x 100 kN UX top loads."""
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    for nd in LOAD_NODES:
        ops.load(nd, P_PUSH, 0.0, 0.0, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_push(odb: "opst.post.CreateODB") -> int:
    """Load-controlled PUSH ramped over N_PUSH_STEPS (documented exception).

    Permitted ``ops.analyze()`` use per AGENT.md 3c/10: the model is linear
    elastic (algorithm Linear) under LoadControl, which SmartAnalyze cannot
    reproduce (it forces DisplacementControl and would mis-scale a
    load-controlled case). N_PUSH_STEPS equal increments with an ODB fetch
    per step (slider shows the deflection evolving), then ``loadConst``.
    Returns the OpenSees return code (0 = success).
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / N_PUSH_STEPS)
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Linear")
    ops.analysis("Static")
    ok = 0
    for _ in range(N_PUSH_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            break
        odb.fetch_response_step()
    ops.loadConst("-time", 0.0)
    return ok


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run PUSH, return ODB + sim-vs-ref results.

    Returns:
        (odb, results) with sim (121,3) nodal UX/UY/UZ and ref arrays from
        node0.out (nodes 1-100) + node1.out (nodes 101-121).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    src = TCL_FILE.read_text(encoding="utf-8", errors="replace")

    init_model()
    define_materials()
    define_sections()
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_ele = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_ele} ShellMITC4 elements (expected {N_ELES}).")

    odb = create_odb(output_dir)

    define_push_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running linear-static PUSH analysis...")
    ok = run_push(odb)
    print(f"  PUSH analysis return code: {ok}")

    sim = np.array([[float(ops.nodeDisp(t, d)) for d in (1, 2, 3)]
                    for t in range(1, N_NODES + 1)])  # (121, 3)

    ref0 = ref1 = None
    if REF_NODE0.exists():
        r = np.loadtxt(str(REF_NODE0)).reshape(-1)[1:].reshape(100, 3)
        ref0 = r
    if REF_NODE1.exists():
        r = np.loadtxt(str(REF_NODE1)).reshape(-1)[1:].reshape(21, 3)
        ref1 = r

    results = {"ok": ok, "sim": sim, "ref0": ref0, "ref1": ref1}
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, verify against node0/node1.out.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis (sim/ref0/ref1 arrays).
    """
    odb.save_response()

    sim = results["sim"]
    ref0, ref1 = results["ref0"], results["ref1"]
    np.savetxt(str(output_dir / "node_disp_sim.csv"), sim, delimiter=",",
               header="ux,uy,uz (mm), rows = nodes 1..121")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))
        # Lateral PUSH is UX -- colour the deformed shape by UX.
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UX", scale=10.0)
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UX", scale=10.0)

    print(f"\n  Steps recorded: {N_PUSH_STEPS} / {N_PUSH_STEPS} expected "
          f"(ok={results['ok']})")
    if ref0 is not None and ref1 is not None:
        ref = np.vstack([ref0, ref1])  # (121, 3)
        diff = sim - ref
        rms = float(np.sqrt(np.mean(diff ** 2)))
        big = np.abs(ref) > 1e-9  # mm; sub-nanometre noise excluded
        rel_big = (float(np.mean(np.abs(diff[big]) / np.abs(ref[big])) * 100.0)
                   if np.any(big) else 0.0)
        ux_sim, ux_ref = sim[:, 0], ref[:, 0]
        ux_rms = float(np.sqrt(np.mean((ux_sim - ux_ref) ** 2)))
        print(f"  Node disp (121x3): RMS {rms:.3e} mm | (|ref|>1e-9 mm "
              f"mean rel {rel_big:.4f}%)")
        print(f"  UX column: sim range [{float(np.min(ux_sim)):.5f}, "
              f"{float(np.max(ux_sim)):.5f}] vs ref "
              f"[{float(np.min(ux_ref)):.5f}, {float(np.max(ux_ref)):.5f}] "
              f"| UX RMS {ux_rms:.3e} mm")
        print(f"  Node {NODE_MONITOR}: sim UX {float(sim[NODE_MONITOR - 1, 0]):.5f} "
              f"mm vs ref {float(ref[NODE_MONITOR - 1, 0]):.5f} mm")
        print(f"  Node 112 (top loaded): sim UX {float(sim[111, 0]):.5f} mm "
              f"vs ref {float(ref[111, 0]):.5f} mm")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_ElasticShell: analysis complete.")
