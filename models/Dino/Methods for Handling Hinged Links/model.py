# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Methods for Handling Hinged Links (Dino Exam12)
UniqueID : Dino_HingedLinks
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-07
Purpose  : Linear-static gravity check (-10 kN x 10 roof nodes) of a 3D
           one-storey steel frame validating the ETABS rigid-link + moment
           release detail against the OpenSees zeroLength + equalDOF hinge
           method. Nodal displacements validated against
           ref/OPENSEES/node0.out, element local forces against ele0.out.
Ref      : Dino -- Methods for Handling Hinged Links (EXAM12.tcl + EXAM12.e2k)
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
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
# Materials (source tags preserved).
MAT_HINGE   = 1    # uniaxial Elastic k=1.0 -> near-zero rotational spring (hinge)
MAT_UNUSED  = 2    # uniaxial Elastic 25500 (C20, dead code -- never referenced)
MAT_STEEL   = 3    # uniaxial Elastic E=206000 MPa (fiber parent)

# Fiber sections (source tags preserved).
SEC_BEAM    = 1    # DH200X500  (beams along Y/X + ground beams)
SEC_COL     = 2    # DH200X200  (columns)

# Beam integration tags (OpenSeesPy requires beamIntegration objects;
# Tcl dispBeamColumn took numIntPts inline -- §12l Lobatto mapping).
INTEG_BEAM  = 1
INTEG_COL   = 2

# Load pattern / time series (source pattern Plain 1 Linear).
TS_GRAV     = 1
PAT_GRAV    = 1

# Control node/DOF for SmartAnalyze-style monitoring (roof node, UZ).
NODE_CTRL   = 8
CTRL_DOF    = 3

# ODB
ODB_TAG     = 1

# Source / reference files.
TCL_FILE    = Path(__file__).parent / "ref" / "OPENSEES" / "exam12.tcl"
REF_NODE    = Path(__file__).parent / "ref" / "OPENSEES" / "node0.out"
REF_ELE     = Path(__file__).parent / "ref" / "OPENSEES" / "ele0.out"
REF_NODE8   = Path(__file__).parent / "ref" / "OPENSEES" / "node8.out"

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N, masses in
# N-s^2/mm = tonne). Values below carry * mm / * N / * MPa multipliers.

# Geometry -- 4 m X-bay, 4 x 4 m Y-bays, 3 m storey.
X_BAY   = 4000.0 * mm
Y_BAY   = 4000.0 * mm
H_STORY = 3000.0 * mm

# Gravity -- 10 kN point load at each of the 10 roof nodes.
P_GRAV = -10000.0 * N
LOAD_NODES = (1, 3, 5, 8, 10, 21, 23, 25, 28, 30)

# Roof mass (source: 1.02 on UX/UY) = 10 kN / g. Mass unit IS N-s^2/mm
# (= 1 tonne), so the literal is kept without a tonne multiplier (AGENT.md
# mass rule -- multiplying again would be 1000x too large).
M_ROOF = 1.02  # N-s^2/mm on UX + UY, zero elsewhere

# Materials.
E_HINGE  = 1.0          # N-mm/rad rotational spring (effectively released)
E_CONC   = 25500.0 * MPa  # dead code in source (kept for fidelity)
E_STEEL  = 206000.0 * MPa

# Fiber-section torsional stiffness (OpenSeesPy requires -GJ; Tcl Fiber
# section ran without one). Open-section J = sum(b*t^3)/3, G = E/2.6.
#   DH200X500: J = (2*200*20^3 + 460*20^3)/3 = 2.293e6 mm4 -> GJ = 1.817e11
#   DH200X200: J = (2*200*12^3 + 176*12^3)/3 = 3.318e5 mm4 -> GJ = 2.629e10
GJ_BEAM = 1.817e11  # N-mm^2
GJ_COL  = 2.629e10  # N-mm^2

# dispBeamColumn integration points (source: 3 for every frame element).
N_IP = 3

# Node table (tag, x, y, z) verbatim from exam12.tcl, in mm.
# Nodes 1..10 = structural (roof + bases on grid A x=0 and grid B x=4000);
# 11..20 / 31..40 = hinge-end duplicates; 2/4/6/7/9 + 22/24/26/27/29 = bases.
NODE_DATA = [
    (1, 0.0, 0.0, 3000.0), (2, 0.0, 0.0, 0.0),
    (3, 0.0, 4000.0, 3000.0), (4, 0.0, 8000.0, 0.0),
    (5, 0.0, 12000.0, 3000.0), (6, 0.0, 16000.0, 0.0),
    (7, 0.0, 4000.0, 0.0), (8, 0.0, 8000.0, 3000.0),
    (9, 0.0, 12000.0, 0.0), (10, 0.0, 16000.0, 3000.0),
    (11, 0.0, 0.0, 0.0), (12, 0.0, 0.0, 3000.0),
    (13, 0.0, 4000.0, 0.0), (14, 0.0, 4000.0, 3000.0),
    (15, 0.0, 8000.0, 0.0), (16, 0.0, 8000.0, 3000.0),
    (17, 0.0, 12000.0, 0.0), (18, 0.0, 12000.0, 3000.0),
    (19, 0.0, 16000.0, 0.0), (20, 0.0, 16000.0, 3000.0),
    (21, 4000.0, 0.0, 3000.0), (22, 4000.0, 0.0, 0.0),
    (23, 4000.0, 4000.0, 3000.0), (24, 4000.0, 8000.0, 0.0),
    (25, 4000.0, 12000.0, 3000.0), (26, 4000.0, 16000.0, 0.0),
    (27, 4000.0, 4000.0, 0.0), (28, 4000.0, 8000.0, 3000.0),
    (29, 4000.0, 12000.0, 0.0), (30, 4000.0, 16000.0, 3000.0),
    (31, 4000.0, 0.0, 0.0), (32, 4000.0, 0.0, 3000.0),
    (33, 4000.0, 4000.0, 0.0), (34, 4000.0, 4000.0, 3000.0),
    (35, 4000.0, 8000.0, 0.0), (36, 4000.0, 8000.0, 3000.0),
    (37, 4000.0, 12000.0, 0.0), (38, 4000.0, 12000.0, 3000.0),
    (39, 4000.0, 16000.0, 0.0), (40, 4000.0, 16000.0, 3000.0),
]
MASS_NODES = (1, 3, 5, 8, 10, 21, 23, 25, 28, 30)
FIX_NODES = (2, 6, 22, 26)

# equalDOF pairs (rNode, cNode) tying hinge duplicates translationally (1 2 3).
EQUALDOF_PAIRS = [
    (2, 11), (1, 12), (7, 13), (3, 14), (4, 15),
    (8, 16), (9, 17), (5, 18), (6, 19), (10, 20),
    (22, 31), (21, 32), (27, 33), (23, 34), (24, 35),
    (28, 36), (29, 37), (25, 38), (26, 39), (30, 40),
]

# Geometric transforms: vertical columns use vecxz (1,0,0), all horizontal
# beams use (0,0,1). transfTag == eleTag for every dispBeamColumn (source).
COL_ELES = (6, 9, 12, 15, 18, 25, 28, 31, 34, 37)  # vecxz (1,0,0)
BEAM_ELES = (1, 2, 3, 4, 20, 21, 22, 23, 39, 40, 41, 42, 43,
             44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56)  # (0,0,1)

# Frame elements (eleTag, iNode, jNode, secTag): 36 dispBeamColumns.
# Sec 1 = DH200X500 (Y-roof + X-roof + ground beams), Sec 2 = DH200X200
# (columns + X transverse beams). Layout verbatim from exam12.tcl.
FRAME_ELES = [
    (1, 10, 5, SEC_BEAM), (2, 5, 8, SEC_BEAM),
    (3, 8, 3, SEC_BEAM), (4, 3, 1, SEC_BEAM),
    (6, 11, 12, SEC_COL), (9, 13, 14, SEC_COL),
    (12, 15, 16, SEC_COL), (15, 17, 18, SEC_COL),
    (18, 19, 20, SEC_COL), (20, 30, 25, SEC_BEAM),
    (21, 25, 28, SEC_BEAM), (22, 28, 23, SEC_BEAM),
    (23, 23, 21, SEC_BEAM), (25, 31, 32, SEC_COL),
    (28, 33, 34, SEC_COL), (31, 35, 36, SEC_COL),
    (34, 37, 38, SEC_COL), (37, 39, 40, SEC_COL),
    (39, 10, 30, SEC_COL), (40, 5, 25, SEC_COL),
    (41, 8, 28, SEC_COL), (42, 3, 23, SEC_COL),
    (43, 1, 21, SEC_COL), (44, 6, 9, SEC_BEAM),
    (45, 9, 4, SEC_BEAM), (46, 4, 7, SEC_BEAM),
    (47, 7, 2, SEC_BEAM), (48, 26, 29, SEC_BEAM),
    (49, 29, 24, SEC_BEAM), (50, 24, 27, SEC_BEAM),
    (51, 27, 22, SEC_BEAM), (52, 6, 26, SEC_COL),
    (53, 9, 29, SEC_COL), (54, 4, 24, SEC_COL),
    (55, 7, 27, SEC_COL), (56, 2, 22, SEC_COL),
]

# zeroLength hinges (eleTag, iNode, jNode): 20 rotational releases (dirs 4 5 6).
# Each column gets one hinge at each end; translations are carried by the
# paired equalDOF above -- the OpenSees analogue of the ETABS
# RIGID-segment + RELEASE M2/M3 detail (EXAM12.e2k C*-1 / C*-9 lines).
ZEROLENGTH_ELES = [
    (5, 2, 11), (7, 12, 1), (8, 7, 13), (10, 14, 3),
    (11, 4, 15), (13, 16, 8), (14, 9, 17), (16, 18, 5),
    (17, 6, 19), (19, 20, 10), (24, 22, 31), (26, 32, 21),
    (27, 27, 33), (29, 34, 23), (30, 24, 35), (32, 36, 28),
    (33, 29, 37), (35, 38, 25), (36, 26, 39), (38, 40, 30),
]


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Three uniaxial Elastic materials verbatim from exam12.tcl.

    MAT_HINGE (k=1.0) feeds the 20 zeroLength rotational springs; MAT_STEEL
    (E=206000 MPa) is the fiber parent. MAT_UNUSED (25500 MPa, C20) is dead
    code in the source -- kept for fidelity, never referenced.
    """
    ops.uniaxialMaterial("Elastic", MAT_HINGE, E_HINGE)
    ops.uniaxialMaterial("Elastic", MAT_UNUSED, E_CONC)
    ops.uniaxialMaterial("Elastic", MAT_STEEL, E_STEEL)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    """Two elastic fiber sections verbatim from exam12.tcl (+ -GJ for Py).

    DH200X500 (SEC_BEAM): flanges 200x20 as 2x5x800 mm2 at z=+-240 mm,
      web 460x20 as 5x1840 mm2 at y=0. DH200X200 (SEC_COL): flanges
      200x12 as 2x5x480 mm2 at z=+-94 mm, web 176x12 as 5x422.4 mm2.
    OpenSeesPy requires -GJ on 3D Fiber sections (Tcl defaulted it);
    GJ values are open-section estimates, torsion is inactive here
    (pure vertical loading). Each section gets a Lobatto beamIntegration
    object (OpenSeesPy dispBeamColumn takes transfTag + integTag, not the
    Tcl inline numIntPts -- PrestressedBeam precedent).
    """
    ops.section("Fiber", SEC_BEAM, "-GJ", GJ_BEAM)
    for y in (-80.0, -40.0, 0.0, 40.0, 80.0):
        ops.fiber(y * mm, -240.0 * mm, 800.0 * mm * mm, MAT_STEEL)
    for y in (-80.0, -40.0, 0.0, 40.0, 80.0):
        ops.fiber(y * mm, 240.0 * mm, 800.0 * mm * mm, MAT_STEEL)
    for z in (-184.0, -92.0, 0.0, 92.0, 184.0):
        ops.fiber(0.0 * mm, z * mm, 1840.0 * mm * mm, MAT_STEEL)

    ops.section("Fiber", SEC_COL, "-GJ", GJ_COL)
    for y in (-80.0, -40.0, 0.0, 40.0, 80.0):
        ops.fiber(y * mm, -94.0 * mm, 480.0 * mm * mm, MAT_STEEL)
    for y in (-80.0, -40.0, 0.0, 40.0, 80.0):
        ops.fiber(y * mm, 94.0 * mm, 480.0 * mm * mm, MAT_STEEL)
    for z in (-70.4, -35.2, 0.0, 35.2, 70.4):
        ops.fiber(0.0 * mm, z * mm, 422.4 * mm * mm, MAT_STEEL)
    ops.beamIntegration("Lobatto", INTEG_BEAM, SEC_BEAM, N_IP)
    ops.beamIntegration("Lobatto", INTEG_COL, SEC_COL, N_IP)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Create the 40 nodes + 10 roof masses (source lines, verbatim coords)."""
    assert len(NODE_DATA) == 40, f"NODE_DATA has {len(NODE_DATA)} rows, expected 40"
    for tag, x, y, z in NODE_DATA:
        ops.node(tag, x * mm, y * mm, z * mm)
    for tag in MASS_NODES:
        ops.mass(tag, M_ROOF, M_ROOF, 0.0, 0.0, 0.0, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix 4 corner bases + 20 translational equalDOF hinge pairs."""
    for tag in FIX_NODES:
        ops.fix(tag, 1, 1, 1, 1, 1, 1)
    for r, c in EQUALDOF_PAIRS:
        ops.equalDOF(r, c, 1, 2, 3)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """36 dispBeamColumns + 20 zeroLength rotational hinges (source verbatim).

    Transforms are 1:1 with frame eleTags: columns vecxz (1,0,0), beams
    (0,0,1). zeroLength elements carry MAT_HINGE on dirs 4/5/6 (rotations
    released, translations via equalDOF) -- the hinge-link method.
    OpenSeesPy dispBeamColumn signature is (tag, i, j, transfTag, integTag).
    """
    for tag in COL_ELES:
        ops.geomTransf("Linear", tag, 1.0, 0.0, 0.0)
    for tag in BEAM_ELES:
        ops.geomTransf("Linear", tag, 0.0, 0.0, 1.0)
    integ_of = {SEC_BEAM: INTEG_BEAM, SEC_COL: INTEG_COL}
    for tag, i, j, sec in FRAME_ELES:
        ops.element("dispBeamColumn", tag, i, j, tag, integ_of[sec])
    for tag, i, j in ZEROLENGTH_ELES:
        ops.element("zeroLength", tag, i, j,
                    "-mat", MAT_HINGE, MAT_HINGE, MAT_HINGE,
                    "-dir", 4, 5, 6)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB (nodal + frame + link responses).

    ``save_link_resp=True`` collects the 20 zeroLength hinge forces;
    ``set_odb_path`` precedes ``CreateODB``. ``model_update=False`` -- no
    elements change mid-analysis.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=True,
        save_truss_resp=False,
        save_link_resp=True,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Single Plain pattern: 10 x -10 kN UZ at the roof nodes (DEAD case)."""
    ops.timeSeries("Linear", TS_GRAV)
    ops.pattern("Plain", PAT_GRAV, TS_GRAV)
    for nd in LOAD_NODES:
        ops.load(nd, 0.0, 0.0, P_GRAV, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB") -> int:
    """Load-controlled gravity in one Linear step (documented exception).

    Permitted ``ops.analyze()`` use per AGENT.md 3c/10: the model is linear
    elastic (algorithm Linear) under LoadControl, which SmartAnalyze cannot
    reproduce (it forces DisplacementControl and would mis-scale a
    single-step gravity case). One step, ODB fetch, then ``loadConst``.
    Returns the OpenSees return code (0 = success).
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0)
    ops.test("EnergyIncr", 1.0e-6, 200)
    ops.algorithm("Linear")
    ops.analysis("Static")
    ok = ops.analyze(1)
    odb.fetch_response_step()
    ops.loadConst("-time", 0.0)
    return ok


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run gravity, return ODB + sim-vs-ref results.

    Returns:
        (odb, results) with sim/ref nodal UZ + element-force arrays and
        error metrics against node0.out / ele0.out (single static step).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)
    print(f"  Built model: {len(FRAME_ELES)} dispBeamColumn + "
          f"{len(ZEROLENGTH_ELES)} zeroLength (expected 36 + 20).")

    odb = create_odb(output_dir)

    define_gravity_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running linear-static gravity analysis...")
    ok = run_gravity(odb)
    print(f"  Gravity analysis return code: {ok}")

    # In-loop simulation vectors (authoritative, not ODB-derived).
    n_nodes = 40
    sim_disp = np.array([[float(ops.nodeDisp(t, d)) for d in (1, 2, 3)]
                         for t in range(1, n_nodes + 1)])  # (40, 3)
    sim_ele = []
    for tag in range(1, 57):
        try:
            sim_ele.append([float(v) for v in ops.eleResponse(tag, "localForce")])
        except Exception:
            sim_ele.append([np.nan] * 12)

    # Reference files: first column is pseudo-time (=1.0); drop it.
    ref_disp = ref_ele = None
    if REF_NODE.exists():
        ref_disp = np.loadtxt(str(REF_NODE)).reshape(-1)
        ref_disp = ref_disp[1:].reshape(40, 3)  # (40, 3) UZ-heavy
    if REF_ELE.exists():
        raw = np.loadtxt(str(REF_ELE)).reshape(-1)[1:]
        # Per-element localForce lengths: 12 for dispBeamColumn, 3 for
        # zeroLength (rotational triplet) -- 36*12 + 20*3 = 492 values.
        ele_lens = {t: 12 for (t, _, _, _) in FRAME_ELES}
        ele_lens.update({t: 3 for (t, _, _) in ZEROLENGTH_ELES})
        ref_ele, pos = {}, 0
        for tag in range(1, 57):
            n = ele_lens.get(tag, 0)
            ref_ele[tag] = raw[pos:pos + n]
            pos += n

    results = {"ok": ok, "sim_disp": sim_disp, "ref_disp": ref_disp,
               "sim_ele": sim_ele, "ref_ele": ref_ele}
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, verify against ele0/node0.out.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis.
    """
    odb.save_response()

    sim_disp = results["sim_disp"]
    ref_disp = results["ref_disp"]
    np.savetxt(str(output_dir / "node_disp_sim.csv"), sim_disp, delimiter=",",
               header="ux,uy,uz (mm), rows = nodes 1..40")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UZ", scale=10.0)
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UZ", scale=10.0)

    # Nodal verification (UZ dominates; UX/UY ~ 1e-14 are numerical noise
    # and excluded from the relative metric -- absolute RMS is authoritative).
    print(f"\n  Steps recorded: 1 / 1 expected (ok={results['ok']})")
    if ref_disp is not None:
        diff = sim_disp - ref_disp
        rms = float(np.sqrt(np.mean(diff ** 2)))
        big = np.abs(ref_disp) > 1e-9  # mm; UX/UY noise floor excluded
        if np.any(big):
            rel_big = float(np.mean(
                np.abs(diff[big]) / np.abs(ref_disp[big])) * 100.0)
        else:
            rel_big = 0.0
        uz_sim, uz_ref = sim_disp[:, 2], ref_disp[:, 2]
        uz_rms = float(np.sqrt(np.mean((uz_sim - uz_ref) ** 2)))
        print(f"  Node disp (40x3): RMS {rms:.3e} mm | (|ref|>1e-9 mm "
              f"mean rel {rel_big:.4f}%)")
        print(f"  UZ column: sim range [{float(np.min(uz_sim)):.5f}, "
              f"{float(np.max(uz_sim)):.5f}] vs ref "
              f"[{float(np.min(uz_ref)):.5f}, {float(np.max(uz_ref)):.5f}] "
              f"| UZ RMS {uz_rms:.3e} mm")
        # Node 8 (dedicated recorder) spot-check.
        print(f"  Node 8: sim UZ {float(sim_disp[7, 2]):.5f} mm vs ref "
              f"{float(ref_disp[7, 2]):.5f} mm")

    # Element verification per-element (12 for beams, 3 for zeroLength hinges).
    sim_ele = results["sim_ele"]
    ref_ele = results.get("ref_ele")
    n_match = sum(1 for v in sim_ele if len(v) in (3, 12))
    print(f"  Elements with localForce response: {n_match} / 56")
    finite = [v for v in sim_ele if len(v) in (3, 12)]
    if finite:
        big = max(abs(x) for v in finite for x in v)
        print(f"  Max |localForce| across elements: {big:.5f} N / N-mm")
    if ref_ele is not None:
        sq, n_big, rel_acc = 0.0, 0, 0.0
        n_tot = 0
        for tag in range(1, 57):
            sv = np.array(sim_ele[tag - 1], dtype=float)
            rv = np.array(ref_ele.get(tag, []), dtype=float)
            if sv.shape != rv.shape or sv.size == 0:
                continue
            # Shear sign convention: the Tcl `recorder ... localForce`
            # reports Vy/Vz with opposite sign to OpenSeesPy
            # `eleResponse(..., "localForce")` for dispBeamColumn
            # (axial, torsion and both bending moments agree at +1.000,
            # shears at -1.000; displacements agree to 1e-6 -- structure
            # is identical, only the shear output sign differs).
            # Flip sim shears (idx 1,2,7,8 of each 12-vector) before diff.
            if sv.size == 12:
                sv = sv.copy()
                sv[[1, 2, 7, 8]] *= -1.0
            d = sv - rv
            sq += float(np.sum(d ** 2))
            n_tot += d.size
            m = np.abs(rv) > 1.0  # N / N-mm; near-zero hinge terms excluded
            if np.any(m):
                rel_acc += float(np.sum(np.abs(d[m]) / np.abs(rv[m])))
                n_big += int(np.sum(m))
        e_rms = float(np.sqrt(sq / max(n_tot, 1)))
        e_rel = float(rel_acc / max(n_big, 1) * 100.0)
        print(f"  Ele localForce (56 eles, shear sign-adjusted): RMS "
              f"{e_rms:.3e} | (|ref|>1 mean rel {e_rel:.4f}%, n={n_big}/{n_tot})")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_HingedLinks: analysis complete.")
