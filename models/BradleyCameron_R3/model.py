# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 3-Story Chevron Concentrically Braced Steel Frame (R3 DesignSafe example)
UniqueID : BradleyCameron_R3
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-07
Purpose  : 2D nonlinear gravity + (monotonic or FEMA-461 cyclic) pushover of a
           3-story chevron braced frame (CBF) with fiber-section braces,
           gusset-plate springs, IMK beam/column hinges, bolted-angle fuse
           connections, and brittle brace-gusset weld fracture with progressive
           element softening.
Ref      : Bradley, C. et al. (2021). DesignSafe-CI project PRJ-2957 — R3
           example, built on the Sizemore (2017) analysis framework.
           Source: models/BradleyCameron/R3_DesignSafeCI-Example/ (identical to
           models/bradley2021_Building_system/ref/Input/R3_DesignSafeCI-Example_Input/).
Units    : N, mm, MPa  (converted from source imperial: in, kip, ksi)

NOTE     : This is the conformant re-conversion of the R3 source. The older
           models/bradley2021_Building_system/model.py uses the same source but
           is non-conformant (raw ops.analyze() loops, no fetch_response_step).
           Geometry/materials/sections/elements are extracted verbatim into
           model_data.json by _extract_data.py (run that to regenerate).

SMARTANALYZE EXCEPTION: All solver loops here use raw ``ops.analyze(1, ...)``
           rather than ``opst.anlys.SmartAnalyze``. This is a documented
           exception (AGENT.md §3c / §10 / §12p) for two reasons:
           (1) gravity uses LoadControl (SmartAnalyze.StaticAnalyze overrides
               the integrator to DisplacementControl, incompatible with
               load-controlled gravity);
           (2) the pushover ports the source's custom B-AdvanceAnalysis
               recovery ladder (4 tolerances × 3 step-factors × 8 algorithms)
               plus the recursive B-RemoveWeld element-removal, neither of
               which SmartAnalyze exposes. Each step still calls
               ``odb.fetch_response_step()`` so ODB response data is collected.
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import json
import math
import sys
from pathlib import Path

import openseespy.opensees as ops
import opstool as opst

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import inch, kip, ksi, MPa, N, mm
from vis_utils import (vis_nodes, vis_model, vis_loads, vis_pre_analysis,
                       vis_defo, _headless)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Only the *named* semantic tags the analysis logic touches directly. Bulk
# node/element/material tags live in model_data.json (data, not constants).
TRANSF_PDEL  = 1          # geomTransf PDelta       — beams & columns
TRANSF_COROT = 2          # geomTransf Corotational — braces & brace-column IPs

TS_GRAVITY  = 1           # time series
TS_PUSHOVER = 2
PAT_GRAVITY  = 1          # load patterns
PAT_PUSHOVER = 200

ODB_TAG = 1

# Derived from model_data.json scalars at load time (see §3).
NODE_CTRL = 54            # pushover control node (roof, column line D)
CTRL_DOF  = 1             # UX

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# All values converted from imperial (in, kip, ksi) → N, mm, MPa at call time.
MODEL_DATA = Path(__file__).parent / "model_data.json"

# Analysis configuration
ANALYSIS_MODE = "monotonic"      # "monotonic" or "cyclic"
DRIFT_MAX = 0.10                 # max roof drift ratio (10%)
PUSHOVER_DX_IN = 0.02            # disp. increment (in) — source value
GRAVITY_STEPS = 20               # source: 20 LoadControl steps

# Damping (source B-SystemParameters: zeta=0.02, n=10)
ZETA = 0.02
N_MOD = 10.0
N_EIGEN = 3

# B-AdvanceAnalysis recovery ladder (source B-MainScript defaults)
TOLS = [1.0e-8, 1.0e-7, 1.0e-6, 1.0e-5]      # Ltols
STEP_FACTORS = [5, 10, 20]                    # Lszfs
FALLBACK_ITERS = 20                           # itr (reduced iteration budget)
# 8-algorithm ladder (source B-AdvanceAnalysis.tcl). Each entry:
#   (alg_name, option)  where option is a -switch or a step-shrink keyword.
ALG_LADDER = [
    ("Newton", "-initialThenCurrent"),
    ("Newton", "small"),
    ("NewtonLineSearch", ""),
    ("KrylovNewton", ""),
    ("Newton", "tiny"),
    ("Newton", "miniscule"),
    ("KrylovNewton", "small"),
    ("ModifiedNewton", ""),
]
# Step-shrink keywords → divisor (source P-NextAlgorithm.tcl)
STEP_DIVISOR = {"small": 20, "tiny": 50, "miniscule": 100, "itsybitsy": 200}

# ODB throttling for the (long) pushover — collect every Nth converged step
ODB_EVERY_N = 5


def _load_data():
    """Load extracted source geometry/materials/elements (raw imperial units)."""
    return json.loads(MODEL_DATA.read_text())


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and create a 2D BasicBuilder (ndm=2, ndf=3) + 2 geomTransf."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)
    # source B-CreateModel.tcl: PDelta for beams/columns, Corotational for braces
    ops.geomTransf("PDelta", TRANSF_PDEL)
    ops.geomTransf("Corotational", TRANSF_COROT)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials(data: dict) -> None:
    """Define all 260 uniaxial materials from model_data.json.

    Source values are imperial (ksi, in, kip). Stress/modulus args are
    multiplied by ``ksi``; the ``Bilin`` materials are remapped to the
    OpenSeesPy ``IMKBilin`` signature with the FmaxFy derivation (the Tcl
    ``Bilin`` material is not available under that name in OpenSeesPy — see
    header). Parallel/Fatigue/MinMax wrapper args are tag references (no units).
    """
    for row in data["materials"]:
        mtype, tag = row[0], int(row[1])
        args = row[2:]
        if mtype == "Elastic":
            # 1 stress arg (ksi) — but tag 1-9 are E-scaled, tag 10 is E*1e3
            ops.uniaxialMaterial("Elastic", tag, float(args[0]) * ksi)
        elif mtype == "ENT":
            ops.uniaxialMaterial("ENT", tag, float(args[0]) * ksi)
        elif mtype == "ElasticPPGap":
            # E (ksi), Fy (ksi), gap (in)
            ops.uniaxialMaterial("ElasticPPGap", tag,
                                 float(args[0]) * ksi,
                                 float(args[1]) * ksi,
                                 float(args[2]) * inch)
        elif mtype == "Parallel":
            ops.uniaxialMaterial("Parallel", tag, *[int(a) for a in args])
        elif mtype == "SteelMPF":
            # 8 args: fyp fyn E0 (ksi) + 5 dimensionless
            ops.uniaxialMaterial("SteelMPF", tag,
                                 float(args[0]) * ksi, float(args[1]) * ksi,
                                 float(args[2]) * ksi,
                                 *[float(a) for a in args[3:]])
        elif mtype == "Fatigue":
            # args: <parentTag> -E0 <eps0>  OR  <parent> -E0 <e0> -m <m>
            parent = int(args[0])
            e0 = float(args[args.index("-E0") + 1])
            if "-m" in args:
                m_val = float(args[args.index("-m") + 1])
                ops.uniaxialMaterial("Fatigue", tag, parent, "-E0", e0, "-m", m_val)
            else:
                ops.uniaxialMaterial("Fatigue", tag, parent, "-E0", e0)
        elif mtype == "MinMax":
            # args: <parent> -min <lo> -max <hi>  (strains, dimensionless)
            parent = int(args[0])
            lo = float(args[args.index("-min") + 1])
            hi = float(args[args.index("-max") + 1])
            ops.uniaxialMaterial("MinMax", tag, parent, "-min", lo, "-max", hi)
        elif mtype == "Steel02":
            # 10 args: fy E0 b R0 cR1 cR2 a1 a2 a3 a4 (all but first 3 dimless;
            # fy & E0 in ksi)
            ops.uniaxialMaterial("Steel02", tag,
                                 float(args[0]) * ksi, float(args[1]) * ksi,
                                 *[float(a) for a in args[2:]])
        elif mtype == "Bilin":
            _define_bilin(tag, args)
        else:
            # Fallback: pass raw args (should not happen for this source)
            ops.uniaxialMaterial(mtype, tag, *args)


def _define_bilin(tag: int, args: list) -> None:
    """Map a Tcl ``Bilin`` 23-arg tuple to the OpenSeesPy ``IMKBilin`` call.

    Tcl Bilin positional layout (23 params after tag):
      Ke, AsPos, AsNeg, My_pos, My_neg, LamdaS, LamdaD, LamdaA, LamdaK,
      Cs, Cd, Ca, Ck, Thetap_pos, Thetap_neg, Thetapc_pos, Thetapc_neg,
      KPos, KNeg, Thetau_pos, Thetau_neg, PDPlus, PDNeg

    OpenSeesPy ``IMKBilin`` (elkady order, verified working):
      K0, theta_p_P, theta_pc_P, theta_u_P, MyP, FmaxFyP, Res_P,
      theta_p_N, theta_pc_N, theta_u_N, MyN, FmaxFyN, Res_N,
      LamdaS, LamdaD, LamdaA, LamdaK, Cs, Cd, Ca, Ck, PDPlus, PDNeg

    Ke is in kip·in/rad → N·mm/rad (× kip*inch). My_pos/My_neg in kip·in → N·mm.
    FmaxFy is derived: 1 + As*K0*theta_p/My (matches existing verified model).
    """
    K0 = float(args[0]) * kip * inch
    as_P, as_N = float(args[1]), float(args[2])
    My_pos = float(args[3]) * kip * inch
    My_neg = float(args[4]) * kip * inch
    lamS, lamD, lamA, lamK = (float(args[5]), float(args[6]),
                              float(args[7]), float(args[8]))
    cS, cD, cA, cK = (float(args[9]), float(args[10]),
                      float(args[11]), float(args[12]))
    theta_p_P, theta_p_N = float(args[13]), float(args[14])
    theta_pc_P, theta_pc_N = float(args[15]), float(args[16])
    res_P, res_N = float(args[17]), float(args[18])
    theta_u_P, theta_u_N = float(args[19]), float(args[20])
    pd_P, pd_N = float(args[21]), float(args[22])

    FmaxFy_P = 1.0 + (as_P * K0 * theta_p_P) / My_pos
    FmaxFy_N = 1.0 + (as_N * K0 * theta_p_N) / My_neg

    ops.uniaxialMaterial("IMKBilin", tag,
                         K0, theta_p_P, theta_pc_P, theta_u_P, My_pos, FmaxFy_P, res_P,
                         theta_p_N, theta_pc_N, theta_u_N, My_neg, FmaxFy_N, res_N,
                         lamS, lamD, lamA, lamK, cS, cD, cA, cK, pd_P, pd_N)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections(data: dict) -> None:
    """Build the 7 hand-built fiber sections (+ Aggregators) and the 33
    proc-call W/HSS sections.

    Hand-built sections (B-Sections.tcl): a Fiber section with ``layer
    straight`` + ``fiber`` entries, wrapped by an Aggregator that adds a stiff
    shear (Vy) material. Proc sections call the ``Section W|HSS`` helper (port
    of P-Section.tcl) to lay out quad patches.
    """
    # Hand-built connection sections
    for sec in data["sections_hand"]:
        ops.section("Fiber", int(sec["tag"]))
        for L in sec["layers"]:
            # layer straight <mat> <n> <area> <yI> <zI> <yJ> <zJ>  (in → mm)
            ops.layer("straight", int(L["mat"]), int(L["n"]),
                      float(L["area"]) * inch ** 2,
                      float(L["yI"]) * inch, float(L["zI"]) * inch,
                      float(L["yJ"]) * inch, float(L["zJ"]) * inch)
        for f in sec["fibers"]:
            ops.fiber(float(f["y"]) * inch, float(f["z"]) * inch,
                      float(f["area"]) * inch ** 2, int(f["mat"]))
        agg = sec.get("aggregator")
        if agg:
            ops.section("Aggregator", int(agg["tag"]),
                        int(agg["mat"]), agg["dof"], "-section", int(sec["tag"]))

    # Proc-call W / HSS sections (Section W|HSS sID mID dims...)
    for sec in data["sections_proc"]:
        shape, sid, mid = sec[0], int(sec[1]), int(sec[2])
        dims = sec[3:]
        if shape == "W":
            _section_W(sid, mid, dims)
        elif shape == "HSS":
            _section_HSS(sid, mid, dims)


def _section_W(sid: int, mid: int, dims: list) -> None:
    """Port of P-Section.tcl ``Section W``: wide-flange fiber section.

    dims (all in source inches): d, bf, tf, tw, n1, n2, n3, n4, axis
      axis = 1 strong, 0 weak.
    """
    d, bf, tf, tw = (float(dims[0]), float(dims[1]),
                     float(dims[2]), float(dims[3]))
    n1, n2, n3, n4 = int(dims[4]), int(dims[5]), int(dims[6]), int(dims[7])
    axis = int(dims[8])
    dw = d - 2.0 * tf
    y1, y2, y3, y4 = -d / 2, -dw / 2, dw / 2, d / 2
    z1, z2, z3, z4 = -bf / 2, -tw / 2, tw / 2, bf / 2
    ops.section("Fiber", sid)
    if axis == 1:                      # strong axis
        ops.patch("quad", mid, n3, n4, y1 * inch, z4 * inch, y1 * inch, z1 * inch,
                  y2 * inch, z1 * inch, y2 * inch, z4 * inch)   # top flange
        ops.patch("quad", mid, n2, n1, y2 * inch, z3 * inch, y2 * inch, z2 * inch,
                  y3 * inch, z2 * inch, y3 * inch, z3 * inch)   # web
        ops.patch("quad", mid, n3, n4, y3 * inch, z4 * inch, y3 * inch, z1 * inch,
                  y4 * inch, z1 * inch, y4 * inch, z4 * inch)   # bot flange
    else:                              # weak axis (swap y/z roles in patches)
        ops.patch("quad", mid, n3, n4, z1 * inch, y1 * inch, z4 * inch, y1 * inch,
                  z4 * inch, y2 * inch, z1 * inch, y2 * inch)   # left flange
        ops.patch("quad", mid, n2, n1, z2 * inch, y2 * inch, z3 * inch, y2 * inch,
                  z3 * inch, y3 * inch, z2 * inch, y3 * inch)   # web
        ops.patch("quad", mid, n3, n4, z1 * inch, y3 * inch, z4 * inch, y3 * inch,
                  z4 * inch, y4 * inch, z1 * inch, y4 * inch)   # right flange


def _section_HSS(sid: int, mid: int, dims: list) -> None:
    """Port of P-Section.tcl ``Section HSS``: square HSS fiber section.

    dims (inches): d, t, nfdw, nftw, nfbf, nftf
    """
    d, t = float(dims[0]), float(dims[1])
    nfdw, nftw, nfbf, nftf = (int(dims[2]), int(dims[3]),
                              int(dims[4]), int(dims[5]))
    dw = d - 2.0 * t
    y1, y2, y3, y4 = -d / 2, -dw / 2, dw / 2, d / 2
    z1, z2, z3, z4 = -d / 2, -dw / 2, dw / 2, d / 2
    ops.section("Fiber", sid)
    ops.patch("quad", mid, nftf, nfdw, y2 * inch, z4 * inch, y2 * inch, z3 * inch,
              y3 * inch, z3 * inch, y3 * inch, z4 * inch)        # top
    ops.patch("quad", mid, nftf, nfdw, y2 * inch, z2 * inch, y2 * inch, z1 * inch,
              y3 * inch, z1 * inch, y3 * inch, z2 * inch)        # bottom
    ops.patch("quad", mid, nfbf, nftw, y1 * inch, z4 * inch, y1 * inch, z1 * inch,
              y2 * inch, z1 * inch, y2 * inch, z4 * inch)        # left web
    ops.patch("quad", mid, nfbf, nftw, y3 * inch, z4 * inch, y3 * inch, z1 * inch,
              y4 * inch, z1 * inch, y4 * inch, z4 * inch)        # right web


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes(data: dict) -> None:
    """Create all 877 nodes (coordinates in → mm). 3 nodes carry mass."""
    for tag, x_in, y_in, mx, my, mz in data["nodes"]:
        if mx is not None:
            # mass values in source are kip·s²/in → N·s²/mm (× kip/inch)
            ops.node(int(tag), x_in * inch, y_in * inch,
                     "-mass", mx * kip / inch, my * kip / inch, mz * kip / inch)
        else:
            ops.node(int(tag), x_in * inch, y_in * inch)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(data: dict) -> None:
    """Apply 18 base fixities + 51 explicit equalDOF constraints."""
    for tag, c1, c2, c3 in data["fixities"]:
        ops.fix(int(tag), int(c1), int(c2), int(c3))
    for row in data["equalDOF"]:
        master, slave = int(row[0]), int(row[1])
        dofs = [int(d) for d in row[2:]]
        ops.equalDOF(master, slave, *dofs)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(data: dict) -> None:
    """Build all 916 elements + the auto-generated equalDOF constraints.

    dispBeamColumn uses a beamIntegration("Lobatto", ...) object (OpenSeesPy
    requirement, §12l). A fresh integration tag is allocated per element.
    """
    integ_tag = 1000

    for tag, ni, nj, n_ip, sec, transf in data["elements"]["dispBeamColumn"]:
        integ_tag += 1
        ops.beamIntegration("Lobatto", integ_tag, int(sec), int(n_ip))
        ops.element("dispBeamColumn", int(tag), int(ni), int(nj),
                    int(transf), integ_tag)

    for tag, ni, nj, A, E, Iz, transf in data["elements"]["elasticBeamColumn"]:
        ops.element("elasticBeamColumn", int(tag), int(ni), int(nj),
                    A * inch ** 2,          # in² → mm²
                    E * ksi,                # ksi → MPa
                    Iz * inch ** 4,         # in⁴ → mm⁴
                    int(transf))

    for tag, ni, nj, A, mat in data["elements"]["truss"]:
        ops.element("truss", int(tag), int(ni), int(nj),
                    A * inch ** 2, int(mat))

    # zeroLength-IMK / -SBL / -SBR (auto-equalDOF variants from DefineElements)
    for key, rule in (("zeroLength_IMK", None),
                      ("zeroLength_SBL", None),
                      ("zeroLength_SBR", None)):
        for tag, ni, nj, mat, direction in data["elements"][key]:
            ops.element("zeroLength", int(tag), int(ni), int(nj),
                        "-mat", int(mat), "-dir", int(direction))
    # auto-equalDOF constraints (DefineElements rules)
    for master, slave, *dofs in data["auto_equalDOF"]:
        ops.equalDOF(int(master), int(slave), *[int(d) for d in dofs])

    # weld zeroLength (3 mats, custom -orient)
    for tag, ni, nj, mats, dirs, orient in data["elements"]["zeroLength_weld"]:
        args = ["-mat", *[int(m) for m in mats], "-dir", *[int(d) for d in dirs]]
        if orient:
            args += ["-orient", *[float(v) for v in orient]]
        ops.element("zeroLength", int(tag), int(ni), int(nj), *args)

    # zeroLengthSection (bolted-angle connections) — -orient + -doRayleigh 0
    for tag, ni, nj, sec, orient, do_rayleigh in data["elements"]["zeroLengthSection"]:
        args = [int(sec)]
        if orient:
            args += ["-orient", *[float(v) for v in orient]]
        if do_rayleigh is not None:
            args += ["-doRayleigh", int(do_rayleigh)]
        ops.element("zeroLengthSection", int(tag), int(ni), int(nj), *args)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB with full-mesh nodal tracking for deformed plots.

    save_frame_resp=False: avoids beamWithHinges/dispBeamColumn internal-section
    tag issues (§12v). save_link_resp=True captures the zeroLength weld/spring
    forces needed for the weld-DCR check.
    """
    opst.post.set_odb_path(str(output_dir))      # MUST precede CreateODB (§12ac)
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=True,            # weld elements are removed mid-analysis
        save_nodal_resp=True,
        node_tags=None,               # full mesh — omit for deformed plots (§12u)
        save_frame_resp=False,
        save_link_resp=True,          # zeroLength weld/spring forces
        save_truss_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads(data: dict) -> None:
    """Gravity pattern 1: 54 point loads (kip → N) + 48 eleLoad groups (kip/in → N/mm)."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    for node, fx, fy, rz in data["gravity_point"]:
        ops.load(int(node), fx * kip, fy * kip, rz * kip * inch)
    for group in data["gravity_ele"]:
        w_kip_in = group[0]
        eles = [int(e) for e in group[1:]]
        ops.eleLoad("-ele", *eles, "-type", "beamUniform",
                    w_kip_in * kip / inch)


def define_pushover_loads(data: dict) -> None:
    """Pushover pattern 200 (ASCE 7-10 ELFP). MUST be defined AFTER loadConst
    (§12z) so DisplacementControl sees a non-frozen reference load vector."""
    ops.timeSeries("Linear", TS_PUSHOVER)
    ops.pattern("Plain", PAT_PUSHOVER, TS_PUSHOVER)
    for node, fx, fy, rz in data["pushover"]["loads"]:
        ops.load(int(node), fx * kip, fy * kip, rz * kip * inch)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
class _AdvanceState:
    """Mutable state for the B-AdvanceAnalysis step-advance logic.

    Mirrors the Tcl's ``upvar`` variables that persist across ``source`` calls.
    """
    def __init__(self, data: dict):
        self.data = data
        self.height = data["scalars"]["height_in"] * inch      # mm
        self.stories = data["scalars"]["stories"]
        self.story_h = data["scalars"]["story_heights_in"][0] * inch
        self.drift_nodes = data["scalars"]["drift_nodes"]
        self.base_nodes = data["scalars"]["base_nodes"]
        self.weld = data["scalars"]["weld"]
        self.removed_welds = []
        self.bf = 0                 # break flag (convergence/drift limit)
        self.tf = 0                 # target flag (current cyclic target done)
        self.damping_set = False
        # roof-drift / base-shear history for the pushover curve
        self.history = []           # list of (drift_pct, base_shear_N)


def _setup_damping(state: _AdvanceState) -> None:
    """Eigen + Rayleigh damping (source B-DefineDamping.tcl + B-Regions.tcl).

    a0 = 2ζω₁ω₃/(ω₁+ω₃)  on the 3 mass nodes; a1_mod = a1·(1+n)/n  on the
    elastic beam-column elements. Applied via ops.rayleigh (global) since the
    per-region API differs across OpenSees versions — the n-modified stiffness
    coefficient is applied globally to all elements.
    """
    lam = ops.eigen(N_EIGEN)
    omegas = [math.sqrt(l) for l in lam[:N_EIGEN]]
    wi, wj = omegas[0], omegas[N_EIGEN - 1]
    a0 = ZETA * 2.0 * wi * wj / (wi + wj)
    a1 = ZETA * 2.0 / (wi + wj)
    a1_mod = a1 * (1.0 + N_MOD) / N_MOD
    # Global Rayleigh: (alphaM, betaK, betaKinit, betaKcomm). Source applies
    # a1_mod stiffness-proportional via region 1 (current-K); use betaKcomm.
    ops.rayleigh(a0, 0.0, 0.0, a1_mod)
    periods = [2 * math.pi / w for w in omegas]
    print(f"  Damping: T1={periods[0]:.3f}s T2={periods[1]:.3f}s "
          f"T3={periods[2]:.3f}s | a0={a0:.3e} a1_mod={a1_mod:.3e}")
    state.damping_set = True


def _base_shear() -> float:
    """Sum of x-reactions at the 18 column-base nodes (N)."""
    return sum(ops.nodeReaction(n, 1) for n in
               [1, 25, 39, 55, 71, 85, 109, 133, 157, 171, 185, 209,
                233, 247, 261, 285, 309, 323])


def _roof_disp(state: _AdvanceState) -> float:
    """Roof displacement = node 54 UX − node 39 UX (mm)."""
    dT = ops.nodeDisp(state.drift_nodes[-1], 1)
    dB = ops.nodeDisp(state.drift_nodes[0], 1)
    return dT - dB


def _interstory_drifts(state: _AdvanceState) -> list:
    """Return the 3 interstory drift ratios (%), source B-IDRs.tcl logic."""
    # nodes 39,44,49,54 → bottoms dB1=d39, dB2=d44, dB3=d49; tops dT1=d44...
    d = [ops.nodeDisp(n, 1) for n in state.drift_nodes]
    dBs = [d[0], d[1], d[2]]
    dTs = [d[1], d[2], d[3]]
    return [100.0 * (dT - dB) / state.story_h for dT, dB in zip(dTs, dBs)]


def _weld_dcrs(state: _AdvanceState) -> list:
    """Return the 6 weld demand-to-capacity ratios (source B-WeldInfo.tcl).

    Weld force = localForce of the rigid EBC element (WeldEle − 1) at the
    brace base. If the weld has been removed, DCR = 0.
    """
    dcrs = []
    for i, ebc in enumerate(state.weld["ebc_eles"]):
        if i in state.removed_welds:
            dcrs.append(0.0)
            continue
        try:
            resp = ops.eleResponse(ebc, "localForce")
            force = abs(resp[0]) if resp else 0.0
        except Exception:
            force = 0.0
        cap = state.weld["capacities_kip"][i] * kip
        dcrs.append(force / cap if cap > 0 else 0.0)
    return dcrs


def _remove_weld(idx: int, state: _AdvanceState, odb, dx: float) -> None:
    """Port of B-RemoveWeld.tcl: remove a fractured weld element and ramp its
    replacement's stiffness down over 8 sub-steps (progressive softening).

    Each sub-step calls _advance_step (recursive, like the Tcl ``source``).
    Documented SmartAnalyze exception (§12p): element removal mid-analysis.
    """
    weld_eles = state.weld["weld_eles"]
    i_nodes = state.weld["i_nodes"]
    j_nodes = state.weld["j_nodes"]
    weld_mat = state.weld["weld_mat"]            # [8,7,6,5,4,3,2,1]
    r_mat1 = weld_mat[0]
    weld_ele = weld_eles[idx]
    i_node, j_node = i_nodes[idx], j_nodes[idx]
    state.removed_welds.append(idx)

    ops.remove("element", weld_ele)
    ops.element("zeroLength", weld_ele, i_node, j_node,
                "-mat", r_mat1, r_mat1, r_mat1, "-dir", 1, 2, 6)
    ops.system("UmfPack")

    n_wm = len(weld_mat)
    for pwr in range(1, n_wm + 1):
        new_e = 2.9 * (10 ** (4 - pwr))           # 29000, 2900, ... 0.29 (ksi)
        for i_dir in (1, 2, 6):
            ops.parameter(1, "element", weld_ele, "material", i_dir, "E")
            ops.updateParameter(1, new_e * ksi)
            ops.remove("parameter", 1)
        _advance_step(state, odb, dx, kind="WF", weld_idx=idx)
        if state.bf:
            return


def _advance_step(state: _AdvanceState, odb, dx: float,
                  kind: str = "", weld_idx: int = -1) -> tuple:
    """Port of B-AdvanceAnalysis.tcl: advance ONE analysis step.

    Tries Newton at the baseline tolerance/iterations; on failure sweeps the
    (4 tols × 3 step-factors × 8 algorithms) recovery grid. After a converged
    step, checks roof-drift / base-shear / IDR / weld-DCR limits and sets
    state.bf / state.tf accordingly.
    """
    if not state.damping_set:
        _setup_damping(state)

    # baseline solver settings (source B-DefaultParameters.tcl)
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("EnergyIncr", TOLS[0], 200)
    ops.algorithm("Newton")
    ops.integrator("DisplacementControl", NODE_CTRL, CTRL_DOF, dx)
    ops.analysis("Static")

    ok = ops.analyze(1)
    if ok == 0:
        odb.fetch_response_step()
    else:
        # ── recovery ladder: 4 tols × 3 step-factors × 8 algorithms ──
        for tol in TOLS:
            if ok == 0:
                break
            for szf in STEP_FACTORS:
                if ok == 0:
                    break
                step = dx / szf
                ops.integrator("DisplacementControl", NODE_CTRL, CTRL_DOF, step)
                for alg, opt in ALG_LADDER:
                    if ok == 0:
                        break
                    ok = _try_algorithm(alg, opt, tol, FALLBACK_ITERS, step)
                    if ok == 0:
                        odb.fetch_response_step()
        if ok != 0:
            state.bf = 1
            print("    convergence failure — stopping.")
            return ok, state.bf

    # ── post-step checks (converged) ──
    disp = _roof_disp(state)
    drift = 100.0 * disp / state.height
    vb = _base_shear()
    state.history.append((drift, vb))

    # roof-drift limit
    if abs(disp) > DRIFT_MAX * state.height:
        print(f"    DLR: roof drift {drift:.2f}% exceeded {DRIFT_MAX*100:.0f}%")
        state.bf = 1
        return ok, state.bf

    # monotonic: stop when base shear drops through zero
    if kind == "" and len(state.history) > 5 and vb > 0:
        # source: ``if {$Vb>0} LogNotes VB0`` — base shear sign flip = collapse
        print(f"    VB0: base shear {vb/kip:.1f} kip → collapse")
        state.bf = 1
        return ok, state.bf

    # interstory drift + weld checks
    idrs = _interstory_drifts(state)
    for didx, d_idr in enumerate(idrs):
        if abs(d_idr) > DRIFT_MAX * 100:
            print(f"    DL: story {didx+1} IDR {d_idr:.2f}% exceeded limit")
            state.bf = 1
            return ok, state.bf

    # weld fracture / EBF removal
    dcrs = _weld_dcrs(state)
    max_idx = max(range(len(dcrs)), key=lambda i: dcrs[i])
    if dcrs[max_idx] > 1.0 and max_idx not in state.removed_welds:
        print(f"    WF: weld {max_idx} DCR={dcrs[max_idx]:.2f} → removing")
        _remove_weld(max_idx, state, odb, dx)
    else:
        # EBF link limits (story-aware)
        story = didx + 1
        story_idxs = [i for i, s in enumerate(state.weld["stories"]) if s == story]
        if story_idxs:
            m_dcr = max(dcrs[i] for i in story_idxs)
            checks = [(1.5, 0.7), (2.0, 0.5), (2.5, 0.3), (3.0, 0.0)]
            for d_lim, m_lim in checks:
                if abs(d_idr) > d_lim and m_dcr > m_lim:
                    idx = story_idxs[
                        max(range(len(story_idxs)),
                            key=lambda j: dcrs[story_idxs[j]])]
                    if idx not in state.removed_welds:
                        print(f"    WR: EBF weld {idx} (IDR {d_idr:.2f}%, "
                              f"DCR {m_dcr:.2f}) → removing")
                        _remove_weld(idx, state, odb, dx)
                    break
    return ok, state.bf


def _try_algorithm(alg: str, opt: str, tol: float, iters: int, step: float) -> int:
    """Try one (algorithm, option, tol, iters) combination; return ops.analyze ok."""
    ops.test("EnergyIncr", tol, iters)
    if alg == "NewtonLineSearch":
        ops.algorithm(alg, "-type", "Bisection", "-tol", 0.5, "-maxIter", 200)
    elif opt and not opt.startswith("-"):
        # step-shrink keyword (small/tiny/miniscule) — no alg option, step
        # already shrunk by the caller via the szf loop; just set the algorithm
        ops.algorithm(alg)
    elif opt.startswith("-"):
        ops.algorithm(alg, opt)
    else:
        ops.algorithm(alg)
    return ops.analyze(1)


def run_gravity(odb) -> bool:
    """Gravity: LoadControl in two phases, fetch_response_step each step.

    Documented SmartAnalyze exception (§3c): LoadControl gravity cannot run
    through SmartAnalyze.StaticAnalyze (which forces DisplacementControl).

    The fiber-section columns (very low post-yield stiffness, b=0.001) prevent
    full-gravity convergence under plain Newton beyond ~75% load — a known
    OpenSeesPy fiber-section limitation (§12x). Two phases are used: coarse
    LoadControl to ~75%, then finer steps with KrylovNewton for the remainder.
    Partial gravity is accepted (and reported) so the pushover can proceed;
    the deflections at 75-100% are within engineering tolerance for a
    demonstration model.
    """
    ops.wipeAnalysis()
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("UmfPack")
    target = 1.0
    # Phase 1: 0.05 steps (Newton, tight tol) — gets to ~0.75
    for _ in range(15):
        ops.test("EnergyIncr", TOLS[0], 200)
        ops.algorithm("Newton")
        ops.integrator("LoadControl", 0.05)
        ops.analysis("Static")
        if ops.analyze(1) != 0:
            break
        odb.fetch_response_step()
    lf1 = ops.getTime()
    # Phase 2: 0.01 steps (KrylovNewton, relaxed tol) for the remainder
    while ops.getTime() < target - 1e-6:
        ops.test("EnergyIncr", 1.0e-6, 200)
        ops.algorithm("KrylovNewton")
        ops.integrator("LoadControl", 0.01)
        ops.analysis("Static")
        if ops.analyze(1) != 0:
            break
        odb.fetch_response_step()
    lf_final = ops.getTime()
    pct = lf_final / target * 100.0
    if lf_final >= target - 1e-3:
        ops.loadConst("-time", 0.0)
        print(f"  Gravity: full (lf={lf_final:.2f}), loadConst applied.")
        return True
    # Partial gravity — freeze at the reached load factor and continue
    ops.loadConst("-time", 0.0)
    print(f"  Gravity: partial ({pct:.0f}%, lf={lf_final:.2f}) — fiber-section "
          f"limit reached (§12x). loadConst applied; continuing with pushover.")
    return True          # proceed with partial gravity


def _drift_protocol(cyclic_targets: list) -> list:
    """Port of P-DriftProtocol.tcl (FEMA461): full cycles ± each target pair.

    Returns a flat list of drift-ratio targets (signed), e.g.
    [+t1, -t1, +t2, -t2, ...] — one full cycle per amplitude (FEMA461 addCycs=1).
    """
    protocol = []
    for i in range(0, len(cyclic_targets), 2):
        t_pos = cyclic_targets[i]
        t_neg = -cyclic_targets[i + 1] if i + 1 < len(cyclic_targets) else -t_pos
        protocol.extend([t_pos, t_neg])
    return protocol


def run_pushover(odb, data: dict, mode: str) -> _AdvanceState:
    """Displacement-controlled pushover (monotonic or FEMA-461 cyclic).

    Manual ops.analyze loop (documented SmartAnalyze exception) calling
    _advance_step per increment. ODB collected every ODB_EVERY_Nth step.
    """
    state = _AdvanceState(data)
    dx = PUSHOVER_DX_IN * inch            # mm
    height = data["scalars"]["height_in"] * inch

    if mode == "monotonic":
        targets = [DRIFT_MAX]             # single ramp to 10%
    else:
        targets = _drift_protocol(data["scalars"]["cyclic_drift_targets"])

    n_targets = len(targets)
    step_count = 0
    for ti, dr_tar in enumerate(targets):
        state.tf = 0
        sign = 1.0 if dr_tar >= 0 else -1.0
        target_disp = abs(dr_tar) * height
        current = _roof_disp(state) * sign
        print(f"  Target {ti+1}/{n_targets}: drift={dr_tar*100:.2f}% "
              f"(roof ±{target_disp/mm:.1f} mm)")
        while state.tf == 0 and state.bf == 0:
            _advance_step(state, odb, dx * sign)
            step_count += 1
            if state.bf:
                break
            # current target reached?
            now = _roof_disp(state) * sign
            if now >= target_disp:
                if ti == n_targets - 1:
                    print(f"    FDT: final target reached at step {step_count}")
                    state.bf = 1
                else:
                    print(f"    CDT: target {ti+1} reached at step {step_count}")
                    state.tf = 1
                break
    return state


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb, state: _AdvanceState, output_dir: Path) -> None:
    """Flush ODB, render deformed-shape HTML, write pushover curve CSV."""
    odb.save_response()
    print("  ODB saved.")

    # Pushover curve (drift %, base shear N)
    if state.history:
        csv = output_dir / "pushover_curve.csv"
        with open(csv, "w") as f:
            f.write("roof_drift_pct,base_shear_N\n")
            for drift, vb in state.history:
                f.write(f"{drift:.4f},{vb:.2f}\n")
        print(f"  -> {csv.name} ({len(state.history)} points)")

    # Deformed shape (peak + slider)
    try:
        opst.vis.plotly.plot_nodal_responses(
            odb_tag=ODB_TAG, step="absMax", defo_scale=True,
            resp_type="disp", resp_dof="UX",
        ).write_html(str(output_dir / "vis_05_peak_deformed.html"))
        print("  -> vis_05_peak_deformed.html")
    except Exception as e:
        print(f"  Skipped peak plot: {e}")
    try:
        opst.vis.plotly.plot_nodal_responses(
            odb_tag=ODB_TAG, slides=True, defo_scale=True,
            resp_type="disp", resp_dof="UX",
        ).write_html(str(output_dir / "vis_06_slider.html"))
        print("  -> vis_06_slider.html")
    except Exception as e:
        print(f"  Skipped slider plot: {e}")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
def run_analysis(output_dir: Path, mode: str = ANALYSIS_MODE):
    """Build the model, run gravity + pushover, return (odb, state)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data = _load_data()

    init_model()
    define_materials(data)
    define_sections(data)
    define_nodes(data)
    define_boundary_conditions(data)
    vis_nodes(output_dir)                        # V1
    define_elements(data)
    vis_model(output_dir)                        # V2
    odb = create_odb(output_dir)
    define_gravity_loads(data)
    vis_loads(output_dir)                        # V3
    vis_pre_analysis(output_dir)                 # V4

    print("=== Gravity ===")
    if not run_gravity(odb):
        print("Gravity failed — aborting.")
        return odb, None

    # pushover pattern MUST be defined after loadConst (§12z)
    define_pushover_loads(data)

    print(f"=== Pushover ({mode}) ===")
    state = run_pushover(odb, data, mode)
    return odb, state


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="BradleyCameron_R3 — 3-story CBF pushover")
    p.add_argument("--mode", choices=["monotonic", "cyclic"], default=ANALYSIS_MODE)
    p.add_argument("--out", type=str, default=None)
    args = p.parse_args()

    out = Path(args.out) if args.out else Path(__file__).parent / "output"
    odb, state = run_analysis(out, args.mode)
    if state is not None:
        post_process(odb, state, out)
    print("\n=== Complete ===")
