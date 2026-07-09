# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : RC1 Fixed-Base Structure — Monotonic Pushover (JP3 Parametric Study)
UniqueID : Bessette
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-09
Purpose  : 3D monotonic displacement-controlled pushover of the RC1 structure
           (a 4 m-tall, 2-column braced-frame-like stick) on a fixed base, with
           elasticBeamColumn members and concentrated IMKPeakOriented rotational
           hinges (RZ) at the column bases and floor levels via zeroLength
           springs. Gravity (axial) then pushover to 10% roof drift.
Ref      : Bessette, C. (2024). JP3 Parametric Study — Phase 1, Structure
           Fixed-Base Analyses, Static Pushover. University of Colorado Boulder.
           Source: models/Bessette/tcl_ref/idCf=48_mainStructPushover.tcl
           (one self-contained file of the larger SSI study; the full 3D
           soil-structure-interaction build lives in idCf=48_idgm=225_MP_main*.tcl
           and is out of scope for this conversion — see Notes).
Units    : N, mm, MPa  (converted from source SI: m, tonne, kN, Pa, s)

NOTE     : Source is SI (m-tonne-kN-Pa). Converted to N-mm-MPa per AGENT.md
           §12j/§12k — Pa is ÷1e6→MPa (NOT the units.py ``Pa`` alias, which is
           1.0=MPa), lengths ×1000 (m→mm), moments/stiffness ×1e6 (kN·m→N·mm),
           masses ×1000 (tonne→N·s²/mm). Rotation/ratio IMK params are
           dimensionless and pass through unchanged.

SSI EXCLUSION: The source distribution contains the full 3D SSI model
           (2080 20_8_BrickUP soil elements + PDMY02 liquefiable layers +
           foundation + 4-stage analysis: elastic/plastic gravity, seismic,
           post-shake diffusion) driven under OpenSeesMP across 3 processors
           with the Mumps solver. That model is NOT converted here: 20_8_BrickUP
           OpenSeesPy signature, OpenSeesMP partition merging, and Mumps
           substitution are unverified for this project and the compute is
           hours-long. Only the fixed-base structure pushover is converted.
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import sys
from pathlib import Path

import openseespy.opensees as ops
import opstool as opst

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import (N, mm, kN, m, MPa, tonne, m2, m4)
from vis_utils import (vis_nodes, vis_model, vis_loads, vis_pre_analysis,
                       vis_defo, _headless)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Materials
MAT_STIFF = 6            # Elastic, very stiff (1e9 Pa → 1000 MPa) — zeroLength DOFs 1-5
MAT_IMK   = 501          # IMKPeakOriented rotational hinge — zeroLength DOF 6 (RZ)

# Geometric transformations (3D needs an explicit local-z vector)
TRANSF_COL = 1           # PDelta,  columns (vertical, along Z)
TRANSF_BM  = 2           # Linear,  beams    (horizontal, along X)

# Time series & load patterns
TS_GRAVITY  = 1
TS_PUSHOVER = 2
PAT_GRAVITY  = 2          # source pattern tag (Plain 2, Constant)
PAT_PUSHOVER = 200        # source pattern tag (Plain 200, Linear)

ODB_TAG = 1

# Control node / DOF for the pushover (source: node 3000003, dof 1 = UX)
NODE_CTRL = 3000003
CTRL_DOF  = 1

# Base nodes (fully fixed) — for base-shear sum & reference
NODE_BASE_L = 5000001
NODE_BASE_R = 5000002

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Geometry (source: m → mm)
X_COL     = 2.5 * m          # column line offset from centreline (±2.5 m)
H_TOTAL   = 4.0 * m          # total structure height (4 m)
H_STORY   = 1.0 * m          # inter-segment height (4 segments of 1 m)

# Section properties (source: m², m⁴, Pa → mm², mm⁴, MPa) — identical for all
# 13 elasticBeamColumn members in the source.
SEC_A   = 0.64 * m2                  # cross-section area (0.64 m² → 640000 mm²)
SEC_E   = 2.9e9 / 1e6 * MPa          # Young's modulus (2.9e9 Pa → 29000 MPa)
SEC_G   = 9.666666666e8 / 1e6 * MPa  # shear modulus (9.6667e8 Pa → 966.67 MPa)
SEC_J   = 0.0682667 * m4             # torsional constant (m⁴ → mm⁴)
SEC_IY  = 0.0341333 * m4             # Iy (m⁴ → mm⁴)  — source uses 0.0341333
SEC_IZ  = 0.0341333 * m4             # Iz (m⁴ → mm⁴)

# Gravity loads (source: kN → N) — applied at DOF3 (vertical, -Z)
P_GRAVITY = 67.6195 * kN             # per node, downward (source: -67.6195)

# Lateral (pushover) loads (source: kN → N) — applied at DOF1 (X), equal split
LAT1 = 1.0 * kN                      # source lat1=1.0 kN per roof node (unit ref load)

# Nodal mass (source: 3.446 tonne → N·s²/mm). tonne = 1000 kg = 1 N·s²/mm·×1000.
# Per §12j: in N-mm-s the consistent mass unit is N·s²/mm; 1 tonne = 1000 kg and
# ``tonne`` constant = 1000, so 3.446 tonne → 3446 N·s²/mm.
MASS_NODE = 3.446 * tonne            # = 3446.0 N·s²/mm

# Pushover target (source: Dmax = 0.1*4.0 m = 0.4 m → 400 mm; Dincr = 0.001 m → 1 mm)
DRIFT_MAX   = 0.10                   # 10% roof drift ratio
D_TARGET    = DRIFT_MAX * H_TOTAL    # 400 mm
D_INCREMENT = 0.001 * m              # 1.0 mm per step (source)

# Gravity analysis
N_GRAV_STEPS = 10                    # source: 10 LoadControl steps


def _load_source():
    """Return the hardcoded source data (small model — no JSON extraction needed).

    All values are in SOURCE SI units (m, tonne, kN, Pa); the define_* functions
    apply the §12j/§12k conversions at call time.
    """
    # Nodes: (tag, x_m, y_m, z_m, mass_tonne_or_None)
    nodes = [
        (3000001, -2.5, 0, 0,    None),
        (3000002,  2.5, 0, 0,    None),
        (3000003, -2.5, 0, 4.0,  3.446),
        (3000004, -2.5, 0, 4.0,  3.446),   # coincident w/ 3000003 (equalDOF target)
        (3000005,  2.5, 0, 4.0,  3.446),
        (3000006,  2.5, 0, 4.0,  3.446),   # coincident w/ 3000005
        (3000007, -2.5, 0, 1.0,  None),
        (3000008,  2.5, 0, 1.0,  None),
        (3000009, -2.5, 0, 2.0,  None),
        (3000010,  2.5, 0, 2.0,  None),
        (3000011, -2.5, 0, 3.0,  None),
        (3000012,  2.5, 0, 3.0,  None),
        (3000013, -1.5, 0, 4.0,  None),
        (3000014, -0.5, 0, 4.0,  None),
        (3000015,  0.5, 0, 4.0,  None),
        (3000016,  1.5, 0, 4.0,  None),
        (NODE_BASE_L, -2.5, 0, 0, None),
        (NODE_BASE_R,  2.5, 0, 0, None),
    ]
    # Boundary conditions: (tag, c1,c2,c3,c4,c5,c6) — source fixes UY, RX, RZ
    fixities = [(n[0], 0, 1, 0, 1, 0, 1) for n in nodes if n[0] < 5000000]
    fixities += [(NODE_BASE_L, 1, 1, 1, 1, 1, 1),
                 (NODE_BASE_R, 1, 1, 1, 1, 1, 1)]
    # zeroLength equalDOF: (master, slave, *dofs) — couples UX,UY,UZ between the
    # coincident pairs so the spring carries only RZ (DOF6) rotation.
    equal_dof = [
        (NODE_BASE_L, 3000001, 1, 2, 3),
        (NODE_BASE_R, 3000002, 1, 2, 3),
        (3000003, 3000004, 1, 2, 3),
        (3000005, 3000006, 1, 2, 3),
    ]
    return nodes, fixities, equal_dof


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and create a 3D BasicBuilder (ndm=3, ndf=6) + 2 geomTransf.

    Columns run vertically (along Z); beams run horizontally (along X). In 3D
    geomTransf the third argument group is the local-z orientation vector, which
    must be chosen so the member's bending plane is consistent. For columns the
    local-x is along the member (global Z), so local-z = global X (1,0,0) puts
    bending about global Y. For beams local-x is global X, so local-z = global Z
    (0,0,1).
    """
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)
    ops.geomTransf("PDelta",  TRANSF_COL, 1.0, 0.0, 0.0)   # columns
    ops.geomTransf("Linear",  TRANSF_BM,  0.0, 0.0, 1.0)   # beams


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Define the stiff elastic (MAT_STIFF) and IMK rotational hinge (MAT_IMK).

    MAT_STIFF: source Elastic 1e9 Pa → 1000 MPa (used on zeroLength DOFs 1-5 to
    make them rigid; only DOF 6/RZ carries the IMK hinge).

    MAT_IMK: source ``IMKPeakOriented 501`` with 23 params. Only K0 (idx 0) and
    My (idx 4, 10) carry moment/stiffness units (kN·m, kN·m/rad → N·mm,
    N·mm/rad); rotations and ratios are dimensionless (unchanged). Layout:
      K0, θpP, θpcP, θuP, MyP, FmaxFyP, ResP,
      θpN, θpcN, θuN, MyN, FmaxFyN, ResN,
      nLamS, nLamC, nLamA, nLamK, cS, cC, cA, cK, Dpos, Dneg
    """
    ops.uniaxialMaterial("Elastic", MAT_STIFF, 1.0e9 / 1e6 * MPa)   # 1000 MPa

    # Source values (SI), in IMKPeakOriented positional order:
    Ke, asP, asN = 6526.99, 0.0279347, 0.0279347      # K0 (kN·m/rad), strain-hardening
    MyP, MyN = 27.1256, 27.1256                        # kN·m
    nLS, nLC, nLA, nLK = 282.618, 79926.5, 9941.97, 785.198
    cS, cC, cA, cK = 1.0, 1.0, 1.0, 1.0                # source overwrites all c_* to 1.0
    thpP, thpN = 0.0625298, 0.0625298
    thpcP, thpcN = 0.153246, 0.153246
    thuP, thuN = 0.242617, 0.242617
    ResP, ResN = 0.5, 0.5
    Dpos, Dneg = 0.292898, 0.292898
    FmaxFyP, FmaxFyN = 1.41539, 1.41539

    # Convert moment/stiffness: kN·m → N·mm (× kN*m = ×1e6)
    Ke_Nmm   = Ke   * kN * m
    MyP_Nmm  = MyP  * kN * m
    MyN_Nmm  = MyN  * kN * m

    ops.uniaxialMaterial(
        "IMKPeakOriented", MAT_IMK,
        Ke_Nmm, thpP, thpcP, thuP, MyP_Nmm, FmaxFyP, ResP,
        thpN, thpcN, thuN, MyN_Nmm, FmaxFyN, ResN,
        nLS, nLC, nLA, nLK, cS, cC, cA, cK, Dpos, Dneg,
    )


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Create the 18 nodes (coords m → mm) and apply nodal masses."""
    nodes, _, _ = _load_source()
    for tag, xm, ym, zm, mass_t in nodes:
        if mass_t is not None:
            # mass tonne → N·s²/mm (× tonne = ×1000); only DOF1 (UX) populated
            ops.node(int(tag), xm * m, ym * m, zm * m,
                     "-mass", mass_t * tonne, 0.0, 0.0, 0.0, 0.0, 0.0)
        else:
            ops.node(int(tag), xm * m, ym * m, zm * m)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Apply 16 structure fixities (UY/RX/RZ) + 2 full base fixities, plus the
    4 equalDOF constraints that couple UX/UY/UZ of the coincident spring pairs
    (so each zeroLength carries only RZ rotation → the IMK hinge)."""
    _, fixities, equal_dof = _load_source()
    for tag, c1, c2, c3, c4, c5, c6 in fixities:
        ops.fix(int(tag), int(c1), int(c2), int(c3), int(c4), int(c5), int(c6))
    for master, slave, *dofs in equal_dof:
        ops.equalDOF(int(master), int(slave), *[int(d) for d in dofs])


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Build the 13 elasticBeamColumn members + 4 zeroLength IMK springs.

    elasticBeamColumn 3D signature (10 args after tag):
      eleTag, Ni, Nj, A, E, G, J, Iy, Iz, transfTag
    All section props converted m²/m⁴/Pa → mm²/mm⁴/MPa here.

    zeroLength: 6 mats on 6 dirs; MAT_STIFF on DOFs 1-5 (rigid), MAT_IMK on
    DOF 6 (RZ hinge). Mirrors the source ``-mat 6 6 6 6 501 6 -dir 1 2 3 4 5 6``.
    """
    # Column segments (vertical, PDelta): 4 per column line × 2 lines = 8
    #   left line:  3000001→7→9→11→3   right line: 3000002→8→10→12→5
    cols = [
        (4000001, 3000001, 3000007), (4000002, 3000007, 3000009),
        (4000003, 3000009, 3000011), (4000004, 3000011, 3000003),
        (4000005, 3000002, 3000008), (4000006, 3000008, 3000010),
        (4000007, 3000010, 3000012), (4000008, 3000012, 3000005),
    ]
    for tag, ni, nj in cols:
        _elastic_beam(tag, ni, nj, TRANSF_COL)

    # Beam segments (horizontal at z=4m, Linear): 3000004→13→14→15→16→3000006
    beams = [
        (4000009,  3000004, 3000013), (4000010, 3000013, 3000014),
        (4000011, 3000014, 3000015), (4000012, 3000015, 3000016),
        (4000013, 3000016, 3000006),
    ]
    for tag, ni, nj in beams:
        _elastic_beam(tag, ni, nj, TRANSF_BM)

    # zeroLength IMK springs: base (2) + floor levels (2)
    #   600001: 5000001—3000001, 600002: 5000002—3000002 (column bases)
    #   600003: 3000003—3000004, 600004: 3000005—3000006 (roof beam-column joints)
    springs = [
        (600001, NODE_BASE_L, 3000001), (600002, NODE_BASE_R, 3000002),
        (600003, 3000003, 3000004),     (600004, 3000005, 3000006),
    ]
    for tag, ni, nj in springs:
        ops.element("zeroLength", tag, ni, nj,
                    "-mat", MAT_STIFF, MAT_STIFF, MAT_STIFF,
                    MAT_STIFF, MAT_IMK, MAT_STIFF,
                    "-dir", 1, 2, 3, 4, 5, 6)


def _elastic_beam(tag: int, ni: int, nj: int, transf: int) -> None:
    """One 3D elasticBeamColumn with the shared section properties."""
    ops.element("elasticBeamColumn", tag, ni, nj,
                SEC_A, SEC_E, SEC_G, SEC_J, SEC_IY, SEC_IZ, transf)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB. set_odb_path MUST precede CreateODB (§12ac).

    save_frame_resp=False: the zeroLength springs don't expose section tags that
    opstool's beam-basic-force extractor expects (§12v); link responses (the IMK
    spring forces) are captured via save_link_resp=True.
    """
    opst.post.set_odb_path(str(output_dir))      # §12ac — before CreateODB
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        save_nodal_resp=True,
        save_frame_resp=False,     # §12v — zeroLength-safe
        save_link_resp=True,       # IMK spring forces
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Gravity pattern 2 (Constant): 2 vertical point loads (kN → N) at DOF3."""
    ops.timeSeries("Constant", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    # source: load 3000004 / 3000006  0 0 -67.6195  (downward, -Z)
    ops.load(3000004, 0.0, 0.0, -P_GRAVITY, 0.0, 0.0, 0.0)
    ops.load(3000006, 0.0, 0.0, -P_GRAVITY, 0.0, 0.0, 0.0)


def define_pushover_loads() -> None:
    """Pushover pattern 200 (Linear): unit lateral loads (kN → N) at DOF1.

    MUST be defined AFTER run_gravity (§12z-1): loadConst freezes all existing
    patterns at t=0; a Linear TS frozen at λ=0 gives DisplacementControl a zero
    reference vector → infinite load factor. Defining the lateral pattern after
    loadConst keeps it live.
    """
    ops.timeSeries("Linear", TS_PUSHOVER)
    ops.pattern("Plain", PAT_PUSHOVER, TS_PUSHOVER)
    ops.load(3000004, LAT1, 0.0, 0.0, 0.0, 0.0, 0.0)
    ops.load(3000006, LAT1, 0.0, 0.0, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def _base_shear() -> float:
    """Sum of x-reactions at the column-base nodes (N).

    The base shear does NOT appear at the fully-fixed nodes 5000001/5000002:
    those are coupled to the column-base nodes 3000001/3000002 via equalDOF on
    UX/UY/UZ, and the zeroLength between them carries only RZ (the IMK hinge
    moment). So the translational reaction — i.e. the shear — is recorded at the
    column-base nodes (3000001, 3000002), where the column axial/shear force is
    in equilibrium with the base. Verified: nodeReaction(5000001,1) ≈ 0 while
    nodeReaction(3000001,1) carries the full column shear.
    """
    return (ops.nodeReaction(3000001, 1)
            + ops.nodeReaction(3000002, 1))


def _roof_disp() -> float:
    """Control-node UX displacement (mm)."""
    return ops.nodeDisp(NODE_CTRL, CTRL_DOF)


def run_gravity(odb) -> bool:
    """Gravity: LoadControl, 10 steps. Manual ops.analyze(1) loop — documented
    SmartAnalyze exception (§3c): SmartAnalyze.StaticAnalyze forces
    DisplacementControl, incompatible with load-controlled gravity.

    Source used Penalty(1e15) + KrylovNewton + NormDispIncr + Newmark(0.5,0.25).
    A static LoadControl analysis does not need Newmark, but we keep KrylovNewton
    + NormDispIncr (robust for the stiff zeroLength/elastic-beam contrast).
    """
    ops.wipeAnalysis()
    ops.constraints("Penalty", 1.0e15, 1.0e15)
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-5, 200)
    ops.algorithm("KrylovNewton", "-iterate", "current")
    ops.integrator("LoadControl", 1.0 / N_GRAV_STEPS)
    ops.analysis("Static")

    ok = 0
    for _ in range(N_GRAV_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            # fallback: ModifiedNewton + relaxed tolerance (§12z-6 style)
            ops.test("NormDispIncr", 1.0e-4, 500)
            ops.algorithm("ModifiedNewton")
            ok = ops.analyze(1)
            ops.test("NormDispIncr", 1.0e-5, 200)
            ops.algorithm("KrylovNewton", "-iterate", "current")
            if ok != 0:
                break
        odb.fetch_response_step()

    lf = ops.getTime()
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()                       # §12h-3 — clear static obj before pushover
    if ok == 0 and abs(lf - 1.0) < 1.0e-3:
        print(f"  Gravity: full (lf={lf:.2f}), loadConst applied.")
        return True
    print(f"  Gravity: incomplete (lf={lf:.2f}, ok={ok}) — continuing with pushover.")
    return True      # proceed even if partial (elastic model should reach lf=1.0)


def run_pushover(odb, history: list) -> bool:
    """Monotonic DisplacementControl pushover to D_TARGET (400 mm = 10% drift).

    Uses opst.anlys.SmartAnalyze (Static) with the §12z-3 RC/fiber-hinge recipe
    (NormDispIncr @ 1e-5, KrylovNewton-primary algoTypes, auto-relaxed tol).
    Each converged segment calls odb.fetch_response_step(); roof drift + base
    shear are recorded into ``history`` for the pushover curve.

    constraints("Penalty"): reused from gravity (Penalty converged the full 400-
    step run; Transformation stalled at 1.69% drift under the equalDOF +
    zeroLength architecture). Penalty constraint forces at the *fully-fixed*
    base nodes 5000001/5000002 return ~0 (the penalty springs absorb them), so
    the base shear is read from the column-base nodes 3000001/3000002 instead —
    see ``_base_shear``. SmartAnalyze does not manage the constraint handler,
    so we set it here before constructing the analysis object.
    """
    ops.constraints("Penalty", 1.0e15, 1.0e15)
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("DisplacementControl", NODE_CTRL, CTRL_DOF, D_INCREMENT)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="NormDispIncr",
        testTol=1.0e-5,
        testIterTimes=200,
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30],
        tryLooseTestTol=True,
        looseTestTolTo=1.0e-4,
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
    )
    segs = analysis.static_split([D_TARGET], maxStep=D_INCREMENT)
    n_steps = 0
    for seg in segs:
        ok = analysis.StaticAnalyze(node=NODE_CTRL, dof=CTRL_DOF, seg=seg)
        if ok < 0:
            print(f"  Pushover: SmartAnalyze failed at step {n_steps} "
                  f"(roof={_roof_disp():.1f} mm) — stopping.")
            break
        odb.fetch_response_step()
        n_steps += 1
        ops.reactions()                 # populate nodeReaction before reading
        disp = _roof_disp()
        drift = 100.0 * disp / H_TOTAL
        history.append((drift, _base_shear()))
        if n_steps % 25 == 0:
            print(f"  step {n_steps}: drift={drift:.2f}%  "
                  f"Vb={history[-1][1]/kN:.1f} kN")
    analysis.close()
    print(f"  Pushover: {n_steps} steps converged, "
          f"final drift={100.0*_roof_disp()/H_TOTAL:.2f}%.")
    return n_steps > 0


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb, history: list, output_dir: Path) -> None:
    """Flush ODB, render deformed-shape HTML, write pushover curve CSV."""
    odb.save_response()
    print("  ODB saved.")

    if history:
        csv = output_dir / "pushover_curve.csv"
        with open(csv, "w") as f:
            f.write("roof_drift_pct,base_shear_N\n")
            for drift, vb in history:
                f.write(f"{drift:.4f},{vb:.2f}\n")
        print(f"  -> {csv.name} ({len(history)} points)")

    # Peak deformed shape
    try:
        opst.vis.plotly.plot_nodal_responses(
            odb_tag=ODB_TAG, step="absMax", defo_scale=True,
            resp_type="disp", resp_dof="UX",
        ).write_html(str(output_dir / "vis_05_peak_deformed.html"))
        print("  -> vis_05_peak_deformed.html")
    except Exception as e:
        print(f"  Skipped peak plot: {e}")
    # Step slider
    try:
        opst.vis.plotly.plot_nodal_responses(
            odb_tag=ODB_TAG, slides=True, defo_scale=True,
            resp_type="disp", resp_dof="UX",
        ).write_html(str(output_dir / "vis_06_slider.html"))
        print("  -> vis_06_slider.html")
    except Exception as e:
        print(f"  Skipped slider plot: {e}")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
def run_analysis(output_dir: Path):
    """Build the model, run gravity + pushover. Returns (odb, history)."""
    output_dir.mkdir(parents=True, exist_ok=True)

    init_model()
    define_materials()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)                        # V1
    define_elements()
    vis_model(output_dir)                        # V2
    odb = create_odb(output_dir)
    define_gravity_loads()
    vis_loads(output_dir)                        # V3 (gravity)
    vis_pre_analysis(output_dir)                 # V4

    history = []
    print("=== Gravity ===")
    run_gravity(odb)

    # Pushover pattern MUST be defined after loadConst (§12z-1)
    define_pushover_loads()
    vis_loads(output_dir)                        # V3 (gravity + lateral)

    print("=== Pushover (monotonic) ===")
    run_pushover(odb, history)
    return odb, history


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, history = run_analysis(output_dir)
    post_process(odb, history, output_dir)
    print("\n=== Complete ===")
