# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Rectangular RC Column Subassembly — Fiber + Bar-Slip, Cyclic Test
UniqueID : VividConcrete_RCconc_full_subassembly
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-09
Purpose  : 3D nonlinear static cyclic analysis of a square (18×18 in) RC column
            subassembly with a fiber-section forceBeamColumn (6 Gauss-Lobatto IPs,
            each with its own confined/unconfined concrete + ReinforcingSteel/
            DuctileFracture section) and two zeroLengthSection bar-slip end springs
            (Bond_SP01) at the column-foundation / column-beam interfaces. Gravity
            axial load → monotonic/cyclic lateral displacement control at the top
            control node.
Ref      : Kuanshi Zhong (Stanford) column cyclic test framework. Source:
            models/VividConcrete_RCconc_full_subassembly/tcl_ref/ (7 Tcl files:
            ColumnCyclicTestVR, DesignVariableVR, CreateConcreteMaterial,
            CreateRCColumnSection, GetGaussLobattoIP, LoadingAlgorithmVR,
            LoadingParameterVR). SetupBarSlip.tcl (T-wall bar-slip) is NOT sourced
            by ColumnCyclicTestVR.tcl and is out of scope for this column model.
Units    : N, mm, MPa  (converted from source imperial: in, kip, ksi)

NOTE     : Source is imperial (in, kip, ksi); converted to N-mm-MPa via the
            standards/units.py constants (inch, kip, ksi). All Mander-confined
            concrete properties (fcc, ecc, flp, ke, …), the Hysteretic shear
            backbone, and the Bond_SP01 bar-slip slips are derived exactly mirroring
            the source Tcl expr chains (CreateConcreteMaterial.tcl §confined/
            §unconfined, CreateRCColumnSection.tcl §shear, ColumnCyclicTestVR.tcl
            §bar-slip), then unit-converted at material-definition time.

CYCLIC PROTOCOL: LoadingParameterVR.tcl carries a 22 455-point displacement
            target history (inches) in its ``LoadHistory`` block. That vector is
            extracted 1:1 into ./load_history.txt (one float per line, source
            inches) and read at run time — keeping model.py readable while
            preserving the exact experimental protocol. Max amplitude ≈ 5.94 in.

SOLVER NOTE: Source uses BandGeneral / Newton(+fallbacks) and EnergyIncr test
            for the cyclic stepping; reproduced exactly. A manual fallback chain
            (Newton→ModifiedNewton→Broyden→NewtonLineSearch) is used per step,
            mirroring RunStaticLoading.tcl. SparseGEN is not available in this
            OpenSeesPy build, so BandGeneral is used (as in the source).
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import math
import sys
from pathlib import Path

import openseespy.opensees as ops
import opstool as opst

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import inch, kip, ksi, MPa, N, mm
from vis_utils import (vis_nodes, vis_model, vis_loads, vis_pre_analysis,
                       vis_defo, vis_slider, _headless)


# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Nodes
NODE_FIX_BASE = 10001   # fixed foundation support (z = 0)
NODE_BOT = 1            # column bottom (above base bar-slip spring)
NODE_TOP = 2            # column top (above top bar-slip spring)
NODE_CTRL = 10002       # top control node (axial load + cyclic displacement)

# Geometric transformation
TRANSF_COL = 1          # PDelta, column along global Z, vecx = (1,0,0)

# Time series & load patterns
TS_GRAVITY = 1
PAT_GRAVITY = 1
TS_CYCLIC = 200
PAT_CYCLIC = 200

ODB_TAG = 1

# Per-IP material tag scheme (source: cover=IP*10+1, core=IP*10+2, steel=IP*10+3)
#   per-IP fiber section  : 10+IP   (+1000 = internal fiber section tag)
#   per-IP aggregator sec : 10+IP
# Bar-slip material tags
MAT_BS_STEEL = 10001     # Bond_SP01 (bar-slip steel)
MAT_BS_COVER = 10002     # Concrete02 (bar-slip cover)
MAT_BS_CORE = 10003      # Concrete02 (bar-slip core)

# Elements
ELE_COL = 1             # forceBeamColumn (nodes 1→2)
ELE_BS_BASE = 10001     # zeroLengthSection bar-slip (nodes 10001→1)
ELE_BS_TOP = 10002      # zeroLengthSection bar-slip (nodes 2→10002)


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# All source values imperial (in, kip, ksi); converted to N, mm, MPa at use.

# Geometry (DesignVariableVR.tcl) — square section b × h
B_SEC = 18.0 * inch      # section width  (z dir)
H_SEC = 18.0 * inch      # section height (y dir)
COVER = 1.0 * inch       # cover
L_COL = 108.0 * inch     # column height
DB = 0.7480315 * inch    # longitudinal bar diameter

# Concrete
FC = -4.57 * ksi         # unconfined compressive strength
# (Ec = 57*sqrt(-fc*1000) ksi, derived in helpers)

# Longitudinal reinforcement
FYL = 64.4 * ksi         # yield strength
TY = 1.45                # fu/fy ratio
FUL = TY * FYL           # ultimate strength
ES = 26200.0 * ksi       # steel Young's modulus
ESH = 0.0400 * ES        # post-yield tangent (Epyr*Es)
ESH_STRAIN = 0.0160      # strain-hardening strain (esh)
EULT = 0.1180            # ultimate strain (esu)
NLT = 3                  # top bars
NLB = 3                  # bottom bars
NLM = 1                  # intermediate layers
NL = NLT + NLB + 2 * NLM # = 8 longitudinal bars (restrained by hoops)
ASLI = 0.44 * inch**2    # longitudinal bar area

# Transverse (hoop) reinforcement
FYT = 68.5 * ksi         # hoop yield
NT = 3
S_TIE = 4.5 * inch       # hoop spacing
ASHI = 0.20 * inch**2
ASH = NT * ASHI          # total hoop area per dir
ROU = ASH / (B_SEC / inch) / (S_TIE / inch)   # Ash/(b*s) [dimensionless]

# Bar-slip (Bond_SP01) — source Sy/Su in inches, b/R scalars
SY = 0.0219 * inch
SU = 0.9876 * inch
BS = 0.3
BR = 1.0

# DuctileFracture flags
C_MONO = 0.9811
C_CYCL = 2.1369
C_SYMM = 1.0200
K1 = 10.0906
K2 = 4.5957
B1 = 0.0475
B2 = 0.0326

# Menegotto-Pinto (ReinforcingSteel -MPCurveParams)
MPR1 = 3.0
MPR2 = 31.708
MPR3 = 7.014

# Axial load (LoadingParameterVR.tcl)
P_AXIAL = -232.0 * kip   # compression (downward, DOF3 at control node)

# Integration
NUM_IP = 6

# Fiber discretisation (ColumnCyclicTestVR.tcl)
NF_CORE_Y = 1
NF_CORE_Z = 100
NF_COVER_Y = 1
NF_COVER_Z = 2

# Damping — none (static cyclic, no dynamics)

# Cyclic stepping (RunStaticLoading.tcl)
NUM_ITER = 800
CYCLIC_TOL = 1.0e-6

# Throttle ODB writes during the long cyclic protocol
ODB_EVERY_N = 50

# Gauss-Lobatto integration points (port of GetGaussLobattolLIP.tcl, N=6)
_GAUSS_LOBATTO_6 = {
    "xi": [-1.0, -0.7650553239, -0.2852315164, 0.2852315164, 0.7650553239, 1.0],
    "wt": [0.06666666667, 0.3784749562, 0.5548583770,
           0.5548583770, 0.3784749562, 0.06666666667],
}


# ── 4. DERIVED PROPERTY HELPERS (source ksi/kip/in domain) ────────────────────
def _unconfined_concrete02(fc_k):
    """Port of DefineRegularizedUnconfinedConcreteMaterial 'Concrete02' branch.

    Returns stress/strain in source domain (ksi, dimensionless). fc_k in ksi.
    """
    Ec_k = 57.0 * math.sqrt(-fc_k * 1000.0)          # ksi
    fpc = fc_k
    epsc0 = 2.0 * fc_k / Ec_k
    fpcu = 0.2 * fpc
    epsU = -0.008
    lam = 0.1
    ft = 0.0074 * math.sqrt(-fc_k * 1000.0)          # ksi
    ets = Ec_k * 0.05                                # ksi
    return dict(fpc=fpc, epsc0=epsc0, fpcu=fpcu, epsU=epsU,
                lam=lam, ft=ft, ets=ets, Ec=Ec_k)


def _confined_concrete02(fc_k, nl, s_in, b_col_in, rou, fyt_k, LIP_in):
    """Port of DefineRegularizedConfinedConcreteMaterial 'Concrete02' branch.

    fc_k in ksi; s_in, b_col_in, LIP_in in inches; fyt_k in ksi; rou dimensionless.
    Returns stress/strain in source domain.
    """
    mm_in = 25.4
    mpa_ksi = 6.895
    Ec_k = 57.0 * math.sqrt(-fc_k * 1000.0)          # ksi
    ke = (nl - 2.0) / nl * (1.0 - s_in / b_col_in)
    fl = ke * rou * fyt_k                            # ksi
    Kfc = (-1.254 + 2.254 * math.sqrt(1.0 + 7.94 * fl / (-fc_k))
           - 2.0 * fl / (-fc_k))
    fpc = Kfc * fc_k
    Keps = 1.0 + 5.0 * (Kfc - 1.0)
    epsc0 = 2.0 * fc_k / Ec_k
    epsc0 = Keps * epsc0
    fpcu = 0.2 * fpc
    Gfc = 1.7 * 2.0 * (-fc_k) * mpa_ksi
    if LIP_in > 0:
        fpcu = 0.2 * fpc
        epsU = -(Gfc / 0.6 / (-fpc * mpa_ksi) / (LIP_in * mm_in)
                 - 0.8 * (-fpc) / Ec_k + (-epsc0))
    else:
        # bar-slip branch: LIP folded to 1.0
        fpcu = 0.8 * fpc
        epsU = -(Gfc / 0.6 / (-fpc * mpa_ksi) / (1.0 * mm_in)
                 - 0.8 * (-fpc) / Ec_k + (-epsc0))
    lam = 0.1
    ft = 0.0074 * math.sqrt(-fc_k * 1000.0)          # ksi
    ets = Ec_k * 0.05                                # ksi
    return dict(fpc=fpc, epsc0=epsc0, fpcu=fpcu, epsU=epsU,
                lam=lam, ft=ft, ets=ets)


def _shear_hysteretic(fc_k, rou, fyt_k, h_in, b_in):
    """Port of CreateColumnSection.tcl §shear (ShearTag == 'NonLinear').

    Returns s1..s3 (kip→N) and e1..e3 (dimensionless). Source h,b in inches.
    """
    Ec_k = 57.0 * math.sqrt(-fc_k * 1000.0)          # ksi
    Gc = Ec_k / 2.0 / (1.0 + 0.2)                    # ksi
    alpha_c = 3.0
    vn = alpha_c * math.sqrt(-fc_k * 1000.0) / 1000.0 + rou * fyt_k   # ksi
    vn_cap = 8.0 * math.sqrt(-fc_k * 1000.0) / 1000.0
    if vn > vn_cap:
        vn = vn_cap
    s1p = 0.002 * math.sqrt(-fc_k * 1000.0) * h_in * b_in       # kip
    e1p = s1p / Gc / (h_in * b_in)
    s2p = 0.6 * vn * h_in * b_in
    e2p = e1p + (s2p - s1p) / 0.4 / Gc / (h_in * b_in)
    s3p = vn * h_in * b_in
    e3p = e2p + 0.4 * vn / 0.1 / Gc
    return dict(s1p=s1p, e1p=e1p, s2p=s2p, e2p=e2p,
                s3p=s3p, e3p=e3p)


def _compute_per_ip():
    """Build per-IP and bar-slip derived property table (MPa / N / strain)."""
    fc_k = -4.57
    fyt_k = FYT / ksi
    rou = ROU
    b_col_in = (B_SEC / inch) - 2.0 * (COVER / inch) - 2.0 * (DB / inch)

    # per-IP LIP (in) = 0.5*wt*Lcol
    LIPs = [0.5 * wt * (L_COL / inch) for wt in _GAUSS_LOBATTO_6["wt"]]

    per_ip = []
    for i in range(NUM_IP):
        LIP = LIPs[i]
        cov = _unconfined_concrete02(fc_k)
        core = _confined_concrete02(fc_k, NL, S_TIE / inch, b_col_in,
                                    rou, fyt_k, LIP)
        per_ip.append((cov, core))

    # bar-slip concrete (LIP = -1)
    bs_cov = _unconfined_concrete02(fc_k)
    bs_core = _confined_concrete02(fc_k, NL, S_TIE / inch, B_SEC / inch,
                                   rou, fyt_k, -1.0)

    # shear backbone (shared shape; per-section material carries its own copy)
    sh = _shear_hysteretic(fc_k, rou, fyt_k, H_SEC / inch, B_SEC / inch)

    return dict(
        per_ip=per_ip,
        bs_cov=bs_cov, bs_core=bs_core,
        shear=sh,
        LIPs=LIPs,
    )


# ── 5. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and create a 3D BasicBuilder (ndm=3, ndf=6) + 1 PDelta transform.

    Source: ``geomTransf PDelta 1 1 0 0`` — column along global Z, local-x
    reference vector (1,0,0) so lateral bending occurs about global Y.
    """
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)
    ops.geomTransf("PDelta", TRANSF_COL, 1.0, 0.0, 0.0)


# ── 6. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials(d: dict) -> None:
    """Define per-IP Concrete02 (cover+core) + ReinforcingSteel/DuctileFracture,
    the bar-slip materials (Bond_SP01 + 2 Concrete02), and the per-section
    Hysteretic shear materials.

    Tag scheme mirrors the source: per IP i (1..6), cover=i*10+1, core=i*10+2,
    steel=i*10+3 (DuctileFracture), ReinforcingSteel=i*10+3+10000. Concrete02
    signature: fpc, epsc0, fpcu, epscu, lambda, ft, Ets.
    """
    fc_k = -4.57
    fyt_k = FYT / ksi

    # per-IP concrete + steel (1-based IPTag, like the source: tags 11..61)
    for i in range(NUM_IP):
        ip = i + 1
        cov, core = d["per_ip"][i]
        cover_tag = ip * 10 + 1
        core_tag = ip * 10 + 2
        steel_tag = ip * 10 + 3         # DuctileFracture
        rs_tag = steel_tag + 10000      # ReinforcingSteel (wrapped)
        # cover: fpc, epsc0, fpcu, epsU, lambda, ft, Ets
        ops.uniaxialMaterial("Concrete02", cover_tag,
                              cov["fpc"] * ksi, cov["epsc0"], cov["fpcu"] * ksi,
                              cov["epsU"], cov["lam"], cov["ft"] * ksi,
                              cov["ets"] * ksi)
        # core
        ops.uniaxialMaterial("Concrete02", core_tag,
                              core["fpc"] * ksi, core["epsc0"], core["fpcu"] * ksi,
                              core["epsU"], core["lam"], core["ft"] * ksi,
                              core["ets"] * ksi)
        # ReinforcingSteel (B = Esh, a1 = esh, a2 = esu_temp = eult)
        ops.uniaxialMaterial("ReinforcingSteel", rs_tag,
                              FYL, FUL, ES, ESH, ESH_STRAIN, EULT,
                              "-MPCurveParams", 1.0 / MPR1, MPR2, MPR3)
        # DuctileFracture wrapping the ReinforcingSteel
        ops.uniaxialMaterial("DuctileFracture", steel_tag, rs_tag,
                              "-c_mono", C_MONO, "-c_cycl", C_CYCL, "-c_symm", C_SYMM,
                              "-E_s", ES, "-esu", EULT,
                              "-k1", K1, "-k2", K2, "-db", DB / inch,
                              "-b1", B1, "-b2", B2)

    # bar-slip materials
    ops.uniaxialMaterial("Bond_SP01", MAT_BS_STEEL,
                          FYL, SY, FUL, SU, BS, BR)
    ops.uniaxialMaterial("Concrete02", MAT_BS_COVER,
                          d["bs_cov"]["fpc"] * ksi, d["bs_cov"]["epsc0"],
                          d["bs_cov"]["fpcu"] * ksi, d["bs_cov"]["epsU"],
                          d["bs_cov"]["lam"], d["bs_cov"]["ft"] * ksi,
                          d["bs_cov"]["ets"] * ksi)
    ops.uniaxialMaterial("Concrete02", MAT_BS_CORE,
                          d["bs_core"]["fpc"] * ksi, d["bs_core"]["epsc0"],
                          d["bs_core"]["fpcu"] * ksi, d["bs_core"]["epsU"],
                          d["bs_core"]["lam"], d["bs_core"]["ft"] * ksi,
                          d["bs_core"]["ets"] * ksi)

    # per-section Hysteretic shear materials
    sh = d["shear"]
    for i in range(NUM_IP):
        sec_id = 10 + (i + 1)
        mat_tag = sec_id + 1000
        _define_shear_material(mat_tag, sh)
    # bar-slip shear material
    _define_shear_material(MAT_BS_STEEL + 1000, sh)


def _define_shear_material(mat_tag, sh):
    s1p, e1p, s2p, e2p, s3p, e3p = (sh["s1p"], sh["e1p"], sh["s2p"],
                                     sh["e2p"], sh["s3p"], sh["e3p"])
    ops.uniaxialMaterial("Hysteretic", mat_tag,
                          s1p * kip, e1p, s2p * kip, e2p, s3p * kip, e3p,
                          -s1p * kip, -e1p, -s2p * kip, -e2p, -s3p * kip, -e3p,
                          0.9, 0.1, 0.0, 0.0, 0.0)


# ── 7. SECTIONS ──────────────────────────────────────────────────────────────
def create_column_section(id_tag, core_mat, cover_mat, steel_mat, shear_mat):
    """Port of CreateColumnSection.tcl (ShearTag == 'NonLinear').

    Builds a rectangular fiber section (tag = id_tag + 1000) with a core
    ``patch quadr``, four cover ``patch quadr``s, top/bottom ``layer straight``
    bars, and one intermediate layer (2 bars). Then aggregates the Hysteretic
    shear material (tag = id_tag + 1000, same int, material namespace) onto Vy
    and Vz of the fiber section, producing aggregator section tag = id_tag.
    """
    GJ = 1000000.0 * kip * inch**2     # source -GJ value (torsional)
    h = H_SEC / inch
    b = B_SEC / inch
    c = COVER / inch
    db = DB / inch

    coverY = h / 2.0
    coverZ = b / 2.0
    ncoverY = -coverY
    ncoverZ = -coverZ
    coreY = coverY - c
    coreZ = coverZ - c
    ncoreY = -coreY
    ncoreZ = -coreZ

    fiber_tag = id_tag + 1000

    ops.section("Fiber", fiber_tag, "-GJ", GJ)
    # core patch
    ops.patch("quadr", core_mat, NF_CORE_Y, NF_CORE_Z,
               ncoreY, coreZ, ncoreY, ncoreZ, coreY, ncoreZ, coreY, coreZ)
    # side covers
    ops.patch("quadr", cover_mat, NF_CORE_Y, NF_COVER_Z,
               ncoverY, coverZ, ncoreY, coreZ, coreY, coreZ, coverY, coverZ)
    ops.patch("quadr", cover_mat, NF_CORE_Y, NF_COVER_Z,
               ncoreY, ncoreZ, ncoverY, ncoverZ, coverY, ncoverZ, coreY, ncoreZ)
    # top & bottom covers
    ops.patch("quadr", cover_mat, NF_COVER_Y, NF_CORE_Z,
               ncoverY, coverZ, ncoverY, ncoreZ, ncoreY, ncoreZ, ncoreY, coreZ)
    ops.patch("quadr", cover_mat, NF_COVER_Y, NF_CORE_Z,
               coreY, coreZ, coreY, ncoreZ, coverY, ncoreZ, coverY, coverZ)

    # top layer
    ops.layer("straight", steel_mat, NLT, ASLI,
               coreY - 0.5 * db, ncoreZ + 0.5 * db,
               coreY - 0.5 * db, coreZ - 0.5 * db)
    # bottom layer
    ops.layer("straight", steel_mat, NLB, ASLI,
               ncoreY + 0.5 * db, ncoreZ + 0.5 * db,
               ncoreY + 0.5 * db, coreZ - 0.5 * db)

    # intermediate layers (2 bars each)
    if NLM > 0:
        interSpacing = (h - 2.0 * c - db) / (NLM + 1.0)
        layerDepth = coreY - 0.5 * db - interSpacing
        for _ in range(NLM):
            ops.layer("straight", steel_mat, 2, ASLI,
                       layerDepth, coreZ, layerDepth, ncoreZ)
            layerDepth -= interSpacing

    # aggregate shear (Vy, Vz) onto the fiber section
    ops.section("Aggregator", id_tag, shear_mat, "Vy", shear_mat, "Vz",
                "-section", fiber_tag)


def define_sections(d: dict) -> None:
    """Build 6 per-IP aggregator sections + the bar-slip aggregator section."""
    for i in range(NUM_IP):
        ip = i + 1
        id_tag = 10 + ip
        core_mat = ip * 10 + 2
        cover_mat = ip * 10 + 1
        steel_mat = ip * 10 + 3
        shear_mat = id_tag + 1000
        create_column_section(id_tag, core_mat, cover_mat, steel_mat, shear_mat)
    # bar-slip section
    create_column_section(MAT_BS_STEEL, MAT_BS_CORE, MAT_BS_COVER,
                          MAT_BS_STEEL, MAT_BS_STEEL + 1000)


# ── 8. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Four nodes along global Z (source ColumnCyclicTestVR.tcl §nodes).

    Node 10001 fixed base; node 10002 is the top control node carrying the axial
    gravity load (DOF3) and the cyclic displacement (DOF2).
    """
    ops.node(NODE_FIX_BASE, 0.0, 0.0, 0.0)
    ops.node(NODE_BOT, 0.0, 0.0, 0.0)
    ops.node(NODE_TOP, 0.0, 0.0, L_COL)
    ops.node(NODE_CTRL, 0.0, 0.0, L_COL)


# ── 9. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Source: fix 10001 all; fix 1 x/Ry/Rz; fix 2 x/Ry/Rz;
    fix 10002 x/Rx/Ry/Rz (free Y and Z at the control node)."""
    ops.fix(NODE_FIX_BASE, 1, 1, 1, 1, 1, 1)
    ops.fix(NODE_BOT, 1, 0, 0, 0, 1, 1)
    ops.fix(NODE_TOP, 1, 0, 0, 0, 1, 1)
    ops.fix(NODE_CTRL, 1, 0, 0, 1, 1, 1)


# ── 10. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """forceBeamColumn (nodes 1→2) with UserDefined Gauss-Lobatto integration
    (6 IPs, per-IP aggregator sections), and two zeroLengthSection bar-slip
    springs (10001→1 and 2→10002).

    UserDefined beamIntegration signature (verified):
      beamIntegration("UserDefined", integTag, N, secTag1..N, xip1..N, lipr1..N)
    where xip = 0.5*xi+0.5, lipr = 0.5*wt.
    """
    sec_tags = [10 + (i + 1) for i in range(NUM_IP)]
    xips = [0.5 * xi + 0.5 for xi in _GAUSS_LOBATTO_6["xi"]]
    liprs = [0.5 * wt for wt in _GAUSS_LOBATTO_6["wt"]]

    integ_tag = 1
    ops.beamIntegration("UserDefined", integ_tag, NUM_IP,
                        *sec_tags, *xips, *liprs)
    ops.element("forceBeamColumn", ELE_COL, NODE_BOT, NODE_TOP,
                TRANSF_COL, integ_tag)

    # bar-slip zeroLengthSections: -orient vecx(0,0,1) vecy(0,-1,0)
    ops.element("zeroLengthSection", ELE_BS_BASE, NODE_FIX_BASE, NODE_BOT,
                MAT_BS_STEEL, "-orient", 0, 0, 1, 0, -1, 0)
    ops.element("zeroLengthSection", ELE_BS_TOP, NODE_TOP, NODE_CTRL,
                MAT_BS_STEEL, "-orient", 0, 0, 1, 0, -1, 0)


# ── 11. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB. set_odb_path MUST precede CreateODB (§12ac).

    save_frame_resp=False: forceBeamColumn fiber sections expose internal
    section tags that opstool's beam-basic-force extractor mishandles; nodal
    responses suffice for the deformed-shape plots. Per-step cyclic data is also
    captured by plain recorders (disp.out / force.out) for the hysteresis loop.
    """
    opst.post.set_odb_path(str(output_dir))      # §12ac
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        save_nodal_resp=True,
        save_frame_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 12. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Gravity pattern 1 (Linear): axial point load P at control node (DOF3)."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    ops.load(NODE_CTRL, 0.0, 0.0, P_AXIAL, 0.0, 0.0, 0.0)


def define_recorders(output_dir: Path) -> None:
    """Plain recorders mirroring the source CyclicOutputVR/*.out files, for the
    hysteresis loop (top lateral disp vs base-shear reaction)."""
    cyc = output_dir / "CyclicOutput"
    cyc.mkdir(parents=True, exist_ok=True)
    ops.recorder("Node", "-file", str(cyc / "disp.out"),
                 "-time", "-node", NODE_TOP, "-dof", 2, "disp")
    ops.recorder("Node", "-file", str(cyc / "force.out"),
                 "-time", "-node", NODE_FIX_BASE, "-dof", 2, "reaction")


# ── 13. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb) -> bool:
    """Gravity: LoadControl, 10 steps. Source: RelativeEnergyIncr 1e-8,
    BandGeneral, Newton. Then loadConst freezes the axial load for the cyclic
    stage.
    """
    ops.wipeAnalysis()
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("RelativeEnergyIncr", 1.0e-8, 500)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / 10.0)
    ops.analysis("Static")

    ok = 0
    for _ in range(10):
        ok = ops.analyze(1)
        if ok != 0:
            break
        odb.fetch_response_step()

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()
    if ok == 0:
        print("  Gravity: full, loadConst applied.")
        return True
    print(f"  Gravity: failed (ok={ok}).")
    return False


def _read_load_history() -> list:
    """Read the extracted cyclic displacement targets (source inches)."""
    hist_file = Path(__file__).parent / "load_history.txt"
    vals = []
    with open(hist_file, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                vals.append(float(line) * inch)     # inches → mm
    return vals


def run_cyclic(odb) -> bool:
    """Cyclic displacement-controlled loading (port of RunStaticLoading.tcl,
    LoadType == 'CyclicStep'). Unit reference lateral load at NODE_CTRL DOF2,
    DisplacementControl on the same.

    The source's manual Newton→ModifiedNewton→Broyden→NewtonLineSearch fallback
    chain (a per-step, fixed-increment retry) stalls mid-protocol on hard
    unloading steps where the full increment cannot converge in one shot. The
    repo convention (elkady2019, padgett_jamie) is opstool's SmartAnalyze, which
    adds adaptive sub-stepping (relaxation + minStep) on top of the alternate-
    algorithm retries. Each target increment is handed to SmartAnalyze via
    static_split, so the recorder still gets one row per experimental target
    (disp.out/force.out align 1:1 with the 22 455-pt protocol) while gaining
    sub-stepping where a single full increment would otherwise diverge.
    """
    load_history = _read_load_history()
    n_steps = len(load_history)

    ops.wipeAnalysis()
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", CYCLIC_TOL, NUM_ITER, 0)
    ops.algorithm("Newton")
    ops.analysis("Static")

    # unit reference load at control node DOF2
    ops.timeSeries("Linear", TS_CYCLIC)
    ops.pattern("Plain", PAT_CYCLIC, TS_CYCLIC)
    ops.load(NODE_CTRL, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0)

    # algoTypes: 40 Newton, 10 Newton -initial, 20 Newton -initialThenCurrent,
    # 30 Newton -Secant, 50 NewtonLineSearch, 60 NewtonLineSearch -type Bisection.
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50, 60],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-3,
    )

    current_disp = 0.0
    completed = 0
    failed_at = None
    for i, target in enumerate(load_history):
        incr = target - current_disp
        # hand this single increment to SmartAnalyze; it sub-divides as needed
        segs = analysis.static_split([incr], maxStep=abs(incr))
        step_ok = True
        for seg in segs:
            rc = analysis.StaticAnalyze(node=NODE_CTRL, dof=2, seg=seg)
            if rc < 0:
                step_ok = False
                break
        if not step_ok:
            failed_at = i
            print(f"  Cyclic: convergence failed at step {i + 1} "
                  f"(target={target / mm:.2f} mm) — stopping.")
            break
        current_disp = target
        completed = i + 1
        if i % ODB_EVERY_N == 0:
            odb.fetch_response_step()
        if (i + 1) % 2000 == 0:
            print(f"  cyclic step {i + 1}/{n_steps}  "
                  f"drift={ops.nodeDisp(NODE_TOP, 2):.2f} mm")
    analysis.close()
    odb.fetch_response_step()
    if failed_at is None:
        print(f"  Cyclic: {completed}/{n_steps} steps completed.")
    else:
        print(f"  Cyclic: {completed}/{n_steps} steps completed "
              f"(failed at {failed_at + 1}).")
    return failed_at is None


# ── 14. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb, output_dir: Path) -> None:
    """Flush ODB, render deformed-shape HTML, and note the hysteresis outputs."""
    odb.save_response()
    print("  ODB saved.")

    try:
        # peak-step (absMax) deformed shape via the repo vis_defo helper, which
        # uses a numeric defo scale and the absMax step by default.
        vis_defo(output_dir, filename="vis_05_peak_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UY", resp_type="disp", scale=10.0)
        print("  -> vis_05_peak_deformed.html")
    except Exception as e:
        print(f"  Skipped peak plot: {e}")
    try:
        # step slider — scrub through the collected ODB frames
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UY", resp_type="disp", scale=10.0)
        print("  -> vis_06_slider.html")
    except Exception as e:
        print(f"  Skipped slider plot: {e}")

    cyc = output_dir / "CyclicOutput"
    print(f"  Hysteresis data: {cyc / 'disp.out'} (top drift) / "
          f"{cyc / 'force.out'} (base shear).")


# ── 15. MAIN ─────────────────────────────────────────────────────────────────
def run_analysis(output_dir: Path):
    """Build the model, run gravity + cyclic. Returns odb."""
    output_dir.mkdir(parents=True, exist_ok=True)
    d = _compute_per_ip()

    init_model()
    define_materials(d)
    define_sections(d)
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)                        # V1
    define_elements()
    vis_model(output_dir)                        # V2
    odb = create_odb(output_dir)
    define_gravity_loads()
    vis_loads(output_dir)                        # V3
    vis_pre_analysis(output_dir)                 # V4

    print("=== Gravity ===")
    if not run_gravity(odb):
        print("Gravity failed — aborting.")
        return odb

    print("=== Cyclic ===")
    define_recorders(output_dir)
    run_cyclic(odb)
    return odb


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print("\n=== Complete ===")
