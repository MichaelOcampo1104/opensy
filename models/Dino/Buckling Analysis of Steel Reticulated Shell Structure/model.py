# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Buckling Analysis of Steel Reticulated Shell Structure (Dino Exam09)
UniqueID : Dino_ReticulatedShell
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-08
Purpose  : Displacement-controlled UZ snap-through buckling (-5 mm x 200
           steps) of a 3D single-layer steel reticulated shell (67 nodes,
           72 dispBeamColumn elements; elastic DH200X200X12X12 fiber
           section wrapped in a shear+torsion Aggregator).  Crown node 7
           is pushed down 1000 mm under a -1000 N reference load; the
           load-factor history is validated against ref/OPENSEES/node7.out
           (peak ~1967 at -175 mm, valley ~426 at -640 mm, ~4967 at
           -1000 mm).
Ref      : Dino -- Buckling Analysis of Steel Reticulated Shell Structure
           (original EXAM09.s2k / ETABS EXAM09.EDB; ref/OPENSEES/co.tcl)
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
# Elastic fiber material + rigid shear/torsion materials (source tags verbatim).
MAT_E1        = 1      # Elastic 2.06e5 MPa (the only fiber material)
MAT_E2        = 2      # Elastic 2.482e4 MPa (dead -- no fiber references it)
MAT_E3        = 3      # Elastic 1.999e5 MPa (dead -- no fiber references it)
MAT_VY        = 201    # Elastic shear-Vy for the Aggregator
MAT_VZ        = 301    # Elastic shear-Vz for the Aggregator
MAT_T         = 401    # Elastic torsion-T for the Aggregator

# Fiber section + Aggregator wrapper + shared Lobatto integration.
SEC_FIBER     = 1
SEC_AGG       = 1001
INTEG_AGG     = 1001   # beamIntegration Lobatto shared by all 72 elements

# Validation
NODE_MONITOR  = 7      # crown node validated against node7.out

# Time series / patterns (pattern tag 1 matches the source).
TS_PUSH       = 1
PAT_PUSH      = 1

# ODB
ODB_TAG       = 1

# Source files
TCL_FILE      = Path(__file__).parent / "ref" / "OPENSEES" / "co.tcl"
REF_FILE      = Path(__file__).parent / "ref" / "OPENSEES" / "node7.out"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N).

# Elastic fiber material (source line, verbatim value in MPa).
E_STEEL = 2.06e5 * MPa

# Rigid shear/torsion stiffnesses for the Aggregator (source, verbatim).
K_VY = 1.585e8         # N (shear stiffness Vy)
K_VZ = 3.169e8         # N (shear stiffness Vz)
K_T  = 2.738e10        # N*mm^2 (torsional stiffness)

# DH200X200X12X12 wide-flange section (ETABS FRAMESECTION, s2k SH=I).
# Flanges: 12 fibres x 200 mm^2 (16.667 x 12 mm); web: 12 fibres x 176 mm^2
# (12 x 14.667 mm).  Total A = 24x200 + 12x176 = 6912 mm^2.
SEC_D = 200.0 * mm
SEC_B = 200.0 * mm
SEC_TF = 12.0 * mm
SEC_TW = 12.0 * mm

# Loading (source: pattern Plain 1 + DisplacementControl 7 3 -5.0 x 200).
P_REF        = -1000.0 * N    # reference UZ load at crown node 7
CTRL_DOF     = 3              # UZ displacement control at node 7
PUSH_INCR    = -5.0 * mm      # displacement increment per step (signed)
N_PUSH_STEPS = 200            # total recorded steps -> -1000 mm target
N_IP         = 3              # dispBeamColumn integration points (source)

N_TOTAL_STEPS = N_PUSH_STEPS  # 200


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Elastic fiber + rigid shear/torsion materials (source, verbatim).

    MAT_E2 / MAT_E3 are defined in the source but referenced by no fiber
    -- kept for tag fidelity (same cleanup rule as Dino §12ap-6 keeps live
    dead tags but drops commented-out lines; here nothing is commented).
    """
    ops.uniaxialMaterial("Elastic", MAT_E1, E_STEEL)
    ops.uniaxialMaterial("Elastic", MAT_E2, 2.482e4 * MPa)
    ops.uniaxialMaterial("Elastic", MAT_E3, 1.999e5 * MPa)
    ops.uniaxialMaterial("Elastic", MAT_VY, K_VY)
    ops.uniaxialMaterial("Elastic", MAT_VZ, K_VZ)
    ops.uniaxialMaterial("Elastic", MAT_T, K_T)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def _parse_fiber_block(src: str, sec_tag: int) -> list[tuple[float, float, float, int]]:
    """Return [(y, z, area, matTag), ...] for one ``section Fiber N { ... }`` block."""
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
    """Rebuild the DH200X200X12X12 fiber section + Aggregator (source, verbatim).

    VERBATIM FIBER REPLAY (§12aq): every ``fiber`` line of co.tcl (36 fibres:
    24 flange x 200 mm^2 + 12 web x 176 mm^2) is re-emitted with
    ops.fiber(y, z, area, matTag) preserving exact centroid + area.
    The fiber section is wrapped by section Aggregator 1001 adding rigid
    Vy/Vz/T codes, matching the source.

    -GJ (§12au): OpenSeesPy 3D ``section Fiber`` REQUIRES -GJ (Tcl only
    warns); computed as G*Sum(A*r^2) from the parsed fibers (G from E with
    nu = 0.3).  The Aggregator's rigid T code dominates torsion regardless.
    """
    fibers = _parse_fiber_block(src, SEC_FIBER)
    assert len(fibers) == 36, f"expected 36 fibers, parsed {len(fibers)}"
    # -GJ: the Tcl source omits -GJ (``section Fiber 1 {...}``), so the fiber
    # section contributes NO torsional stiffness and the Aggregator's rigid T
    # code (2.738e10 N-mm^2) governs torsion alone.  OpenSeesPy REQUIRES -GJ,
    # so a negligible 1.0 is passed for Tcl fidelity.  NOTE: do NOT use the
    # §12au G*Sum(A*r^2) recipe here -- it gives 5.05e12 N-mm^2 (184x the
    # Aggregator T) and over-stiffens the post-buckling branch by ~6.5%
    # (valley 453 vs 425, final 5287 vs 4967).
    ops.section("Fiber", SEC_FIBER, "-GJ", 1.0)
    for (y, z, area, mat) in fibers:
        # OpenSeesPy fiber signature: fiber(y, z, area, matTag)
        ops.fiber(y, z, area, mat)
    ops.section("Aggregator", SEC_AGG,
                MAT_VY, "Vy", MAT_VZ, "Vz", MAT_T, "T",
                "-section", SEC_FIBER)

    # dispBeamColumn needs a beamIntegration object (§12l); one shared Lobatto
    # rule (all 72 source elements use nIP = 3).
    ops.beamIntegration("Lobatto", INTEG_AGG, SEC_AGG, N_IP)


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 67 nodes + lumped mass from co.tcl, verbatim.

    Mass is applied on UX and UY only (zero on UZ/rotations).  Values are
    already in N-s^2/mm so no conversion is applied.
    """
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))
    for m in re.finditer(
        r"^mass\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.mass(int(m.group(1)), float(m.group(2)), float(m.group(3)),
                 0.0, 0.0, 0.0, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Apply the six pinned supports from co.tcl (tolerates trailing ';').

    fix 1..6: UX/UY/UZ fixed, rotations free (1 1 1 0 0 0).  The source
    prints "rigidDiaphragm" / "mass" / "node" labels but issues no
    MP-constraint commands, so Plain constraints are used throughout.
    """
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> int:
    """Create geomTransf + dispBeamColumn elements from co.tcl, verbatim.

    geomTransf Corotational (72 transforms; inclined shell members carry
    the source vecxz ~ (+-0.052, -+0.09, 0.995), ring beams use (0, 0, 1)).
    dispBeamColumn (72 elements: ``tag i j nIP secTag transfTag``) -- the
    OpenSeesPy form takes (tag, i, j, transfTag, integTag) with the shared
    Lobatto beamIntegration (source nIP = 3).  Returns element count.
    """
    n_transf = 0
    for m in re.finditer(
        r"^geomTransf\s+Corotational\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)",
        src, re.M,
    ):
        ops.geomTransf("Corotational", int(m.group(1)),
                       float(m.group(2)), float(m.group(3)), float(m.group(4)))
        n_transf += 1
    assert n_transf == 72, f"expected 72 geomTransf, parsed {n_transf}"

    n = 0
    for m in re.finditer(
        r"^element\s+dispBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        src, re.M,
    ):
        tag = int(m.group(1))
        n1, n2 = int(m.group(2)), int(m.group(3))
        transf = int(m.group(6))
        ops.element("dispBeamColumn", tag, n1, n2, transf, INTEG_AGG)
        n += 1
    assert n == 72, f"expected 72 elements, parsed {n}"
    return n


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a static elastic frame model.

    ``save_frame_resp=False`` -- consistent with the other Dino
    fiber-section models (internal sections lack user-visible tags;
    §12v).  ``model_update=False`` -- no elements are removed/added
    mid-analysis.  ``set_odb_path`` precedes ``CreateODB`` (§12ac).
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
def define_buckling_loads(src: str) -> None:
    """Single Plain pattern (source): reference UZ load at crown node 7.

    The ``load 7 0 0 -1000 0 0 0`` line inside the source's
    ``pattern Plain 1 Linear {...}`` block is replayed verbatim.
    DisplacementControl scales this reference vector to reach each
    target displacement (snap-through: peak / valley / re-stiffening).
    """
    ops.timeSeries("Linear", TS_PUSH)
    ops.pattern("Plain", PAT_PUSH, TS_PUSH)
    m = re.search(
        r"^load\s+7\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)"
        r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    )
    if m:
        ops.load(NODE_MONITOR, *(float(m.group(i)) for i in range(1, 7)))
    else:  # fallback to the documented reference load
        ops.load(NODE_MONITOR, 0.0, 0.0, P_REF, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_buckling(odb: "opst.post.CreateODB") -> bool:
    """Crown pushdown: DisplacementControl node 7 DOF 3, -5 mm x 200 steps.

    One increment per reference step via static_split([incr],
    maxStep=|incr|) so the recorder stays 1:1 with the 200-row node7.out
    (§12am per-increment cadence).  In-loop history (load factor via
    getTime, crown UX/UY/UZ) is tracked for verification.
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="EnergyIncr",
        testTol=1.0e-6,
        testIterTimes=200,
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50, 60],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        printPer=0,
        testPrintFlag=0,
    )

    history: list[tuple[float, float, float, float]] = []  # (lf, ux, uy, uz)
    ok = 0
    for _ in range(N_PUSH_STEPS):
        segs = analysis.static_split([PUSH_INCR], maxStep=abs(PUSH_INCR))
        step_ok = True
        for seg in segs:
            ok = analysis.StaticAnalyze(
                node=NODE_MONITOR, dof=CTRL_DOF, seg=seg)
            if ok < 0:
                step_ok = False
                break
            odb.fetch_response_step()
        if not step_ok:
            print(f"  WARNING: buckling step {len(history)} failed (ok={ok})")
            break
        ops.reactions()
        history.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_MONITOR, 1)),
            float(ops.nodeDisp(NODE_MONITOR, 2)),
            float(ops.nodeDisp(NODE_MONITOR, 3)),
        ))
    analysis.close()
    run_buckling.history = history  # type: ignore[attr-defined]
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run crown pushdown, return ODB + results.

    Returns:
        (odb, results) where results has keys: hist (4,N) sim
        [LF,UX,UY,UZ] history, ref (4,N) reference from node7.out.
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
    print(f"  Built model: {n_ele} dispBeamColumn elements (expected 72).")

    odb = create_odb(output_dir)

    define_buckling_loads(src)
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running crown pushdown buckling analysis...")
    run_buckling(odb)

    # Reference crown history (node7.out: col0=lambda, col1=UX, col2=UY, col3=UZ)
    ref = None
    if REF_FILE.exists():
        ref = np.loadtxt(str(REF_FILE)).T  # (4, N) -> [LF, UX, UY, UZ]

    hist = np.array(getattr(run_buckling, "history", []), dtype=float).T
    results = {"hist": hist, "ref": ref}
    if hist.size:
        np.savez(output_dir / "crown_history.npz", hist=hist,
                 ref=ref if ref is not None else np.zeros((0, 0)))
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot crown history, verify.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis (hist/ref arrays).
    """
    odb.save_response()
    vis_defo(output_dir, filename="vis_05_deformed.html", odb_tag=ODB_TAG, resp_dof="UX")
    vis_slider(output_dir, filename="vis_06_slider.html", odb_tag=ODB_TAG, resp_dof="UX")

    hist = results.get("hist")
    ref = results.get("ref")
    if hist is not None and hist.size and ref is not None:
        n = min(hist.shape[1], ref.shape[1])
        sim_lf, sim_uz = hist[0, :n], hist[3, :n]
        ref_lf, ref_uz = ref[0, :n], ref[3, :n]
        # Load-factor error (relative, guarded at snap-through zero crossings).
        denom = np.maximum(np.abs(ref_lf), 1.0)
        lf_rel = np.abs(sim_lf - ref_lf) / denom
        uz_err = np.abs(sim_uz - ref_uz)
        print(f"  Crown history: {n} steps | LF max-rel-err {lf_rel.max():.4f} "
              f"(mean {lf_rel.mean():.5f}) | UZ max-abs-err {uz_err.max():.3e} mm")
        i_peak = int(np.argmax(ref_lf[:60]))
        i_val = i_peak + int(np.argmin(ref_lf[i_peak:]))  # post-buckling minimum
        print(f"  Peak: sim LF {sim_lf[i_peak]:.2f} vs ref {ref_lf[i_peak]:.2f} "
              f"@ UZ {sim_uz[i_peak]:.1f} mm (ref {ref_uz[i_peak]:.1f})")
        print(f"  Post-buckling valley: sim LF {sim_lf[i_val]:.2f} vs ref "
              f"{ref_lf[i_val]:.2f} @ UZ {sim_uz[i_val]:.1f} mm (ref {ref_uz[i_val]:.1f})")
        print(f"  Final: sim LF {sim_lf[-1]:.2f} vs ref {ref_lf[-1]:.2f} "
              f"@ UZ {sim_uz[-1]:.1f} mm (ref {ref_uz[-1]:.1f})")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print(f"Dino_ReticulatedShell buckling complete. Output in {output_dir}")
