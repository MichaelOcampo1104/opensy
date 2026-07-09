# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Circular RC Bridge Column — Fiber + Bar-Slip, Seismic Time-History
UniqueID : VividConcrete
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-09
Purpose  : 3D nonlinear dynamic analysis of a circular RC bridge column with a
           fiber-section forceBeamColumn (6 Gauss-Lobatto IPs, each with its own
           confined/unconfined concrete + rebar section) and a zeroLengthSection
           bar-slip end spring (Bond_SP01). Gravity → Rayleigh damping → seismic
           time-history under a horizontal ground motion.
Ref      : Zhong, K. (2017). Fiber-section + bar-slip column modeling framework.
           Stanford University. Source: models/VividConcrete/tcl_ref/ (5 Tcl
           files: CreateModel, DesignPropertyC1, GetGaussLobattoIP, SolverNewmark,
           SquenceTestNew).
Units    : N, mm, MPa  (converted from source imperial: in, kip, ksi)

NOTE     : Source is imperial (in, kip, ksi); converted to N-mm-MPa via the
           standards/units.py constants (inch, kip, ksi). All Mander-confined
           concrete properties (fcc, ecc, flp, ke, rouS, vn) and the Hysteretic
           shear backbone are derived in _compute_derived() exactly mirroring the
           source Tcl expr chain (CreateModel.tcl §concrete/§shear), then unit-
           converted at material-definition time.

GM SUBSTITUTION: The source runs 6 sequential ground motions (Loma Prieta ×5 +
           Kobe, ./TableInput/EQ1GM.txt … EQ6GM.txt) which are NOT in the repo.
           For end-to-end validation the Northridge-1994 record NR94cnp.txt
           (dt=0.01 s, ~2490 pts, g-units, reused from models/elkady2019) is
           used. run_dynamic() is generic — the real GMs drop in by pointing
           GM_FILE / GM_DT / GM_NPTS at them.

SOLVER NOTE: Source uses SparseGEN; not compiled into this OpenSeesPy build, so
           BandGeneral is substituted (§12af). Source eigen uses -fullGenLapack;
           the default subspace solver is used instead (§12h-2, robustness).
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
                       vis_defo, _headless)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Nodes
NODE_BASE = 1            # fixed base (below the bar-slip spring)
NODE_SLIP = 2            # bar-slip interface (top of zeroLengthSection)
NODE_TOP = 3             # column top (mass + gravity load)

# Geometric transformation
TRANSF_COL = 1           # PDelta, vertical column

# Time series & load patterns
TS_GRAVITY = 1
TS_GM = 101              # source uses 101..106 for the 6 GMs; we use 101
PAT_GRAVITY = 1
PAT_GM = 101

ODB_TAG = 1

# Material tag schemes (source: per-IP, IPTag*10 + offset)
#   IPTag 1..6 → cover=11,21,..,61 ; core=12,22,..,62 ; steel=13,23,..,63
MAT_BOND_SLIP1 = 4       # Bond_SP01 (bar-slip steel)
MAT_BOND_SLIP2 = 5       # Concrete02 (bar-slip core, 4×fpcu, 10×ecc)
MAT_BOND_SLIP3 = 6       # Concrete02 (bar-slip cover)
MAT_SHEAR = 7            # Hysteretic shear (aggregated Vy/Vz)

# Section tag schemes
#   per-IP fiber section: IPTag*100+1 (e.g. 101..601)
#   per-IP aggregator:    IPTag*10+1  (e.g. 11..61)
SEC_BOND_FIBER = 3       # bar-slip fiber section (source sectag_barslip)
SEC_BOND_ZERO = 5        # bar-slip aggregator (source sectag_zerolength)

# Elements
ELE_BEAM = 1             # forceBeamColumn (nodes 2→3)
ELE_BOND = 101           # zeroLengthSection (nodes 1→2)

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# All source values imperial (in, kip, ksi); converted to N, mm, MPa at use.

# Geometry (DesignPropertyC1.tcl)
L_COL = 288.0 * inch          # column height (288 in → 7315 mm)
D_COL = 48.0 * inch           # column diameter (48 in → 1219 mm)
COVER = 2.0 * inch            # cover (2 in → 50.8 mm)

# Concrete
FC = -6.1 * ksi               # unconfined compressive strength (-6.1 ksi)
EC = 3320.0 * ksi             # Young's modulus (3320 ksi)
# ft = 7.4*sqrt(-fc*1000)/1000 ksi  (derived in _compute_derived)
# Et = ft/0.002 ksi

# Longitudinal reinforcement
NSL = 18                      # number of longitudinal bars
DBL = 1.41 * inch             # bar diameter (1.41 in)
ASL = 1.56 * inch**2          # bar area (1.56 in²)
FYL = 75.2 * ksi              # yield strength (75.2 ksi)
FUL = 102.4 * ksi             # ultimate strength (102.4 ksi)
ESY = 0.0026                  # yield strain
ESH = 0.0110                  # strain-hardening strain
ESU = 0.1220                  # ultimate strain
ESL_MOD = 28400.0 * ksi       # steel Young's modulus (28400 ksi)  [source: Esl]
# Esh (tangent) = b*2*Esl, b=(ful-fyl)/(esu-esy)/Esl  (derived)

# Lateral (transverse) reinforcement
DBT = 0.625 * inch            # tie/bar diameter
AST = 0.62 * inch**2          # tie area
FYT = 54.8 * ksi              # tie yield
S_TIE = 6.0 * inch            # tie spacing

# Loads / mass
P_GRAVITY = -522.0 * kip      # axial gravity load (−522 kip, downward)
G_INCH = 386.089              # g in in/s² (source); = 9806.65 mm/s²

# Fiber discretisation (CreateModel.tcl §sections)
NUM_CIRC = 20                 # circumferential divisions (patches)
NUM_RAD1 = 4                  # radial divisions, cover
NUM_RAD2 = 40                 # radial divisions, core

# Integration
NUM_IP = 6                    # Gauss-Lobatto integration points
NUM_GRAV_STEPS = 10

# Damping
ZETA = 0.03                   # Rayleigh damping ratio (modes 1 & 3)
N_EIGEN = 3

# Ground motion (Northridge-1994 validation substitute; source EQ1-6 missing)
GM_FILE = "NR94cnp.txt"       # in ground_motions/
GM_DT = 0.01                  # s
GM_NPTS = 2490                # ~498 lines × 5 vals
GM_FACTOR = G_INCH * inch     # g, source factor: $g*1.0 (in/s² → mm/s²)
ODB_EVERY_N = 25              # throttle ODB writes for the long GM


# Gauss-Lobatto integration points (port of GetGaussLobattoIP.tcl, N=6)
_GAUSS_LOBATTO_6 = {
    "xi": [-1.0, -0.7650553239, -0.2852315164, 0.2852315164, 0.7650553239, 1.0],
    "wt": [0.06666666667, 0.3784749562, 0.5548583770,
           0.5548583770, 0.3784749562, 0.06666666667],
}


def _compute_derived():
    """Reproduce the source Tcl derived-property chain (CreateModel.tcl §concrete/
    §shear) and return a dict of N-mm-MPa values, ready for material definition.

    Units note: the source mixes ksi and ksi-internal expressions (e.g. it
    computes fcc in ksi via the Mander formula using flp in ksi). To preserve
    the exact arithmetic, the Mander/shear derivations are evaluated in the
    SOURCE ksi domain (using fc, Ec, fyt … as ksi values), then the final
    stress/strain/modulus results are converted to MPa at return. Length-derived
    quantities (Ac, Ae, intRad, extRad, Sy/Su) are computed in inches then
    converted to mm.
    """
    # --- source ksi-domain scalars (for exact expr parity) ---
    fc_k = -6.1                 # ksi
    Ec_k = 3320.0               # ksi
    fyl_k = 75.2                # ksi
    fyt_k = 54.8                # ksi
    Esl_k = 28400.0             # ksi
    ft_k = 7.4 * math.sqrt(-fc_k * 1000.0) / 1000.0    # ksi
    Et_k = ft_k / 0.002                                 # ksi

    # cover concrete
    eco = 2.0 * fc_k / Ec_k                             # (strain, negative)

    # core concrete (Mander confinement)
    ds = 48.0 - 2.0 * 2.0 - 0.625                       # in (D-2c-dbt)
    Ac = 0.25 * math.pi * ds * ds                       # in²
    rouCC = 18 * 1.56 / Ac
    Acc = Ac * (1.0 - rouCC)
    Ae = 0.25 * math.pi * (ds - 0.5 * (6.0 - 0.625)) ** 2    # in²
    ke = Ae / Acc
    rouS = 4.0 * 0.62 / ds / 6.0
    fl = 0.5 * rouS * fyt_k                             # ksi
    flp = fl * ke                                       # ksi
    fcc = fc_k * (-1.254 + 2.254 * math.sqrt(1 + 7.94 * flp / abs(fc_k))
                  - 2.0 * flp / abs(fc_k))              # ksi (negative)
    ecc = eco * (1.0 + 5.0 * (fcc / fc_k - 1.0))        # strain (negative)
    fpcu = 0.2 * fcc                                    # ksi (negative)
    Gfc = 1.7 * 2.0 * (-fc_k) * 6.895                   # ksi-domain (×mpa_ksi)

    # per-IP ecu (ultimate core strain) — depends on IP weight LIP
    # source: ecu = -(Gfc/0.6/(-fcc*mpa_ksi)/(LIP*mm_in) - 0.8*(-fcc)/Ec + (-ecc))
    # LIP per IP = 0.5*wt*L/numEle ; numEle=1, L=288 in, mm_in=25.4
    LIPs = [0.5 * wt * 288.0 for wt in _GAUSS_LOBATTO_6["wt"]]    # in
    ecu_per_ip = []
    for LIP in LIPs:
        ecu = -(Gfc / 0.6 / (-fcc * 6.895) / (LIP * 25.4)
                - 0.8 * (-fcc) / Ec_k + (-ecc))
        ecu_per_ip.append(ecu)

    # steel Esh (tangent at strain hardening)
    b_hard = (102.4 - 75.2) / (0.1220 - 0.0026) / Esl_k
    Esh = b_hard * 2.0 * Esl_k                          # ksi

    # bar-slip (Bond_SP01)
    alpha = 0.4
    dbl_in = 1.41
    Sy = 0.1 * ((dbl_in / 4000.0 * fyl_k * 1000.0 / math.sqrt(-fc_k * 1000.0)
                 * (2.0 * alpha + 1.0)) ** (1.0 / alpha)) + 0.013    # in
    Su = 50.0 * Sy                                       # in

    # shear backbone (Hysteretic)
    Gc = Ec_k / 2.0 / (1.0 + 0.2)                        # ksi
    Ac_mm = Ac                                           # in² (use in shear-area)
    vn = 3.0 * math.sqrt(-fc_k * 1000.0) / 1000.0 + rouS * fyt_k   # ksi
    vn_cap = 8.0 * math.sqrt(-fc_k * 1000.0) / 1000.0
    if vn > vn_cap:
        vn = vn_cap
    s1p = 0.002 * math.sqrt(-fc_k * 1000.0) * Ac_mm     # kip
    e1p = s1p / Gc / Ac_mm                               # strain
    s2p = 0.6 * vn * Ac_mm                               # kip
    e2p = e1p + (s2p - s1p) / 0.4 / Gc / Ac_mm
    s3p = vn * Ac_mm                                     # kip
    e3p = e2p + 0.4 * vn / 0.1 / Gc

    # radii for fiber layout
    intRad_in = 0.5 * 48.0 - 2.0 - 0.625                 # in
    extRad_in = 0.5 * 48.0                               # in

    return dict(
        # stresses → MPa
        fc=fc_k * ksi, ft=ft_k * ksi, Ec=Ec_k * ksi, Et=Et_k * ksi,
        eco=eco, ecc=ecc, fcc=fcc * ksi, fpcu=fpcu * ksi,
        fyl=FYL, ful=FUL, Esl=ESL_MOD, Esh=Esh * ksi,
        fyt=FYT,
        ecu_per_ip=ecu_per_ip,                           # strains (dimensionless)
        # bar-slip
        Sy=Sy * inch, Su=Su * inch,
        # shear backbone → N + dimensionless strain
        s1p=s1p * kip, e1p=e1p, s2p=s2p * kip, e2p=e2p,
        s3p=s3p * kip, e3p=e3p,
        # geometry
        intRad=intRad_in * inch, extRad=extRad_in * inch,
    )


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and create a 3D BasicBuilder (ndm=3, ndf=6) + 1 PDelta transform.

    Source: ``geomTransf PDelta 1 0 -1 0`` — the column is along global Z, and
    the local-z vector (0,-1,0) orients bending about global X.
    """
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)
    ops.geomTransf("PDelta", TRANSF_COL, 0.0, -1.0, 0.0)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials(d: dict) -> None:
    """Define per-IP Concrete02 (cover+core) + ReinforcingSteel, the bar-slip
    materials (Bond_SP01 + 2 Concrete02), and the Hysteretic shear material.

    Tag scheme mirrors the source: per IP i (1..6), cover=i*10+1, core=i*10+2,
    steel=i*10+3. Concrete02 signature: fpc, epsc0, fpcu, epscu, ratio, ft, Ets.
    """
    # per-IP concrete + steel
    for i in range(1, NUM_IP + 1):
        cover_tag = i * 10 + 1
        core_tag = i * 10 + 2
        steel_tag = i * 10 + 3
        ecu = d["ecu_per_ip"][i - 1]
        # cover: fc, eco, 0.0, -0.008, 0.1, ft, 0.05*Ec
        ops.uniaxialMaterial("Concrete02", cover_tag,
                             d["fc"], d["eco"], 0.0, -0.008, 0.1,
                             d["ft"], 0.05 * d["Ec"])
        # core: fcc, ecc, fpcu, ecu, 0.1, ft, 0.05*Ec
        ops.uniaxialMaterial("Concrete02", core_tag,
                             d["fcc"], d["ecc"], d["fpcu"], ecu, 0.1,
                             d["ft"], 0.05 * d["Ec"])
        # steel: fyl, ful, Esl, Esh, esh, esu
        ops.uniaxialMaterial("ReinforcingSteel", steel_tag,
                             d["fyl"], d["ful"], d["Esl"], d["Esh"],
                             ESH, ESU)

    # bar-slip materials
    ops.uniaxialMaterial("Bond_SP01", MAT_BOND_SLIP1,
                         d["fyl"], d["Sy"], d["ful"], d["Su"], 0.3, 0.9)
    ops.uniaxialMaterial("Concrete02", MAT_BOND_SLIP2,
                         d["fcc"], d["ecc"], 4.0 * d["fpcu"], 10.0 * d["ecc"],
                         0.1, d["ft"], 0.05 * d["Ec"])
    ops.uniaxialMaterial("Concrete02", MAT_BOND_SLIP3,
                         d["fc"], d["eco"], 0.0, -0.008, 0.1,
                         d["ft"], 0.05 * d["Ec"])

    # shear (Hysteretic): s1p,e1p,...,s3n,e3n,pinchX,pinchY,damage1,damage2,beta
    s1p, e1p, s2p, e2p, s3p, e3p = d["s1p"], d["e1p"], d["s2p"], d["e2p"], d["s3p"], d["e3p"]
    ops.uniaxialMaterial("Hysteretic", MAT_SHEAR,
                         s1p, e1p, s2p, e2p, s3p, e3p,
                         -s1p, -e1p, -s2p, -e2p, -s3p, -e3p,
                         1.0, 1.0, 0.0, 0.0, 0.0)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections(d: dict) -> None:
    """Build 6 per-IP Aggregator-wrapped fiber sections + the bar-slip section.

    Each fiber section: ``section Fiber tag -GJ`` with a cover ``patch circ``,
    a core ``patch circ``, and NSL rebar ``fiber``s around the inner ring. The
    source uses ``patch circ mat nCirc nRad 0 0 rI rE 0 360`` (centre, inner r,
    outer r, start/end angles in degrees).
    """
    GJ = 10000000.0 * kip * inch**2          # source -GJ value (torsional)
    intR, extR = d["intRad"], d["extRad"]

    # per-IP flexure sections
    for i in range(1, NUM_IP + 1):
        fiber_tag = i * 100 + 1
        agg_tag = i * 10 + 1
        cover_mat = i * 10 + 1
        core_mat = i * 10 + 2
        steel_mat = i * 10 + 3
        ops.section("Fiber", fiber_tag, "-GJ", GJ)
        # cover (ring intR→extR)
        ops.patch("circ", cover_mat, NUM_CIRC, NUM_RAD1, 0.0, 0.0,
                  intR, extR, 0.0, 360.0)
        # core (disc 0→intR)
        ops.patch("circ", core_mat, NUM_CIRC, NUM_RAD2, 0.0, 0.0,
                  0.0, intR, 0.0, 360.0)
        # NSL rebar around the inner ring
        for b in range(NSL):
            ang = b * 2.0 * math.pi / NSL
            yLoc = intR * math.sin(ang)
            zLoc = intR * math.cos(ang)
            ops.fiber(yLoc, zLoc, ASL, steel_mat)
        # aggregator: add shear (Vy, Vz)
        ops.section("Aggregator", agg_tag,
                    MAT_SHEAR, "Vy", MAT_SHEAR, "Vz",
                    "-section", fiber_tag)

    # bar-slip fiber section (source sectag_barslip=3)
    ops.section("Fiber", SEC_BOND_FIBER, "-GJ", GJ)
    ops.patch("circ", MAT_BOND_SLIP3, NUM_CIRC, NUM_RAD1, 0.0, 0.0,
              intR, extR, 0.0, 360.0)
    ops.patch("circ", MAT_BOND_SLIP2, NUM_CIRC, NUM_RAD2, 0.0, 0.0,
              0.0, intR, 0.0, 360.0)
    for b in range(NSL):
        ang = b * 2.0 * math.pi / NSL
        yLoc = intR * math.cos(ang)     # source uses cos/sin swapped here
        zLoc = intR * math.sin(ang)
        ops.fiber(yLoc, zLoc, ASL, MAT_BOND_SLIP1)
    # bar-slip aggregator (source sectag_zerolength=5)
    ops.section("Aggregator", SEC_BOND_ZERO,
                MAT_SHEAR, "Vy", MAT_SHEAR, "Vz",
                "-section", SEC_BOND_FIBER)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Create 3 nodes along global Z. Node 3 carries the lateral mass (-P/g)
    and a small rotational inertia (source: -0.125*P*L²/g about Y).

    Mass conversion: source mass = -P[kip]/g[in/s²] in kip·s²/in. P_GRAVITY is
    already in Newtons and L_COL in mm, so dividing by g[mm/s²]=G_INCH*inch gives
    N·s²/mm directly — NO extra unit factor. (Earlier multiplied by kip/inch,
    which double-converted and gave a 4448× too-heavy mass → T1=56s.)
    """
    g_mm = G_INCH * inch                         # g in mm/s² (= 9806.65)
    mx = -P_GRAVITY / g_mm                       # lateral mass (N·s²/mm)
    myy = -0.125 * P_GRAVITY * (L_COL**2) / g_mm  # RY inertia (N·s²/mm·mm²)
    ops.node(NODE_BASE, 0.0, 0.0, 0.0)
    ops.node(NODE_SLIP, 0.0, 0.0, 0.0,
             "-mass", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    ops.node(NODE_TOP, 0.0, 0.0, L_COL,
             "-mass", mx, 0.0, 1e-2, 0.0, myy, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Node 1 fully fixed; node 2 free except RZ (source: fix 2 0 0 0 0 0 1)."""
    ops.fix(NODE_BASE, 1, 1, 1, 1, 1, 1)
    ops.fix(NODE_SLIP, 0, 0, 0, 0, 0, 1)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """forceBeamColumn (nodes 2→3) with UserDefined Gauss-Lobatto integration
    (6 IPs, per-IP sections), and a zeroLengthSection bar-slip spring (1→2).

    UserDefined beamIntegration signature (verified):
      beamIntegration("UserDefined", integTag, N, secTag1..N, xip1..N, lipr1..N)
    where xip is location (0..1) and lipr is the weight. Source: XIP = 0.5*xi+0.5,
    LIPR = 0.5*wt (the 0.5*L factor is folded into the weight).
    """
    sec_tags = [i * 10 + 1 for i in range(1, NUM_IP + 1)]
    xips = [0.5 * xi + 0.5 for xi in _GAUSS_LOBATTO_6["xi"]]
    liprs = [0.5 * wt for wt in _GAUSS_LOBATTO_6["wt"]]

    integ_tag = 1
    ops.beamIntegration("UserDefined", integ_tag, NUM_IP,
                        *sec_tags, *xips, *liprs)
    ops.element("forceBeamColumn", ELE_BEAM, NODE_SLIP, NODE_TOP,
                TRANSF_COL, integ_tag)

    # bar-slip zeroLengthSection: -orient vecx(0,0,1) vecy(-1,0,0)
    ops.element("zeroLengthSection", ELE_BOND, NODE_BASE, NODE_SLIP,
                SEC_BOND_ZERO, "-orient", 0, 0, 1, -1, 0, 0)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB. set_odb_path MUST precede CreateODB (§12ac).

    save_frame_resp=False: forceBeamColumn fiber sections expose internal
    section tags that opstool's beam-basic-force extractor mishandles (§12v);
    nodal responses suffice for the deformed-shape plots.
    """
    opst.post.set_odb_path(str(output_dir))      # §12ac
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        save_nodal_resp=True,
        save_frame_resp=False,     # §12v
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Gravity pattern 1 (Linear): axial point load P at node 3 (DOF3, -Z)."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    ops.load(NODE_TOP, 0.0, 0.0, P_GRAVITY, 0.0, 0.0, 0.0)


def define_ground_motion(motion_dir: Path) -> None:
    """UniformExcitation (X-dir) driven by a Path timeSeries.

    MUST be defined AFTER run_gravity (§12i): loadConst freezes all existing
    patterns at t=0; a Path GM frozen at its t≈0 value (≈0 accel) is permanently
    disabled. Defining the GM after loadConst keeps it live.
    """
    gm_path = motion_dir / GM_FILE
    ops.timeSeries("Path", TS_GM, "-dt", GM_DT,
                   "-filePath", str(gm_path), "-factor", GM_FACTOR)
    ops.pattern("UniformExcitation", PAT_GM, 1, "-accel", TS_GM)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb) -> bool:
    """Gravity: LoadControl, 10 steps. Manual ops.analyze(1) loop — documented
    SmartAnalyze exception (§3c): SmartAnalyze.StaticAnalyze forces
    DisplacementControl, incompatible with load-controlled gravity.

    Source: RelativeEnergyIncr 1e-6, BandGeneral, Newton.
    """
    ops.wipeAnalysis()
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("RelativeEnergyIncr", 1.0e-6, 500)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / NUM_GRAV_STEPS)
    ops.analysis("Static")

    ok = 0
    for _ in range(NUM_GRAV_STEPS):
        ok = ops.analyze(1)
        if ok != 0:
            break
        odb.fetch_response_step()

    lf = ops.getTime()
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()                       # §12h-3 — clear static obj
    if ok == 0:
        print(f"  Gravity: full (lf={lf:.2f}), loadConst applied.")
        return True
    print(f"  Gravity: incomplete (lf={lf:.2f}, ok={ok}).")
    return False


def _setup_rayleigh_damping() -> tuple:
    """Eigen + Rayleigh damping (ζ on modes 1 & 3, Chopra p.457).

    Uses -fullGenLapack (the source's choice). This deviates from §12h-2 (which
    prefers the default subspace solver for stiffness-contrast models) because
    the issue here is NOT stiffness contrast — the column has a rank-2 mass
    matrix (only node-3 UX + RY carry mass) that defeats the ARPACK subspace
    iteration ("Could not build an Arnoldi factorization"). fullGenLapack
    factorizes M⁻¹K directly and returns the modes reliably.
    """
    lam = ops.eigen("-fullGenLapack", N_EIGEN)
    omegas = [math.sqrt(l) for l in lam[:N_EIGEN]]
    periods = [2 * math.pi / w for w in omegas]
    wi, wj = omegas[0], omegas[2]            # modes 1 & 3
    a0 = ZETA * 2.0 * wi * wj / (wi + wj)
    a1 = ZETA * 2.0 / (wi + wj)
    ops.rayleigh(a0, 0.0, 0.0, a1)
    print(f"  Damping: T1={periods[0]:.3f}s T2={periods[1]:.3f}s "
          f"T3={periods[2]:.3f}s | a0={a0:.3e} a1={a1:.3e}")
    return tuple(periods)


def run_dynamic(odb) -> bool:
    """Seismic time-history under the UniformExcitation GM.

    Uses opst.anlys.SmartAnalyze (Transient) with the §12z fiber-softening recipe
    (NormDispIncr @ 1e-6, KrylovNewton-primary algoTypes, auto-relaxed tol +
    added iterations). Newmark(0.5,0.25), BandGeneral (SparseGEN unavailable,
    §12af). ODB collected every ODB_EVERY_Nth step.
    """
    n_steps = GM_NPTS
    dt = GM_DT

    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("Newmark", 0.5, 0.25)
    ops.analysis("Transient")

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="NormDispIncr",
        testTol=1.0e-6,
        testIterTimes=100,
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30],
        tryLooseTestTol=True,
        looseTestTolTo=1.0e-3,
        tryAddTestTimes=True,
        testIterTimesMore=[200, 400],
    )
    segs = analysis.transient_split(n_steps)
    ok_count = 0
    for i, _ in enumerate(segs):
        ok = analysis.TransientAnalyze(dt)
        if ok < 0:
            print(f"  Dynamic: SmartAnalyze failed at step {i} "
                  f"(t={ops.getTime():.2f}s) — stopping.")
            break
        if i % ODB_EVERY_N == 0:
            odb.fetch_response_step()
        ok_count += 1
        if (i + 1) % 500 == 0:
            print(f"  step {i + 1}/{n_steps}  t={ops.getTime():.2f}s "
                  f"dispUX={ops.nodeDisp(NODE_TOP, 1):.2f} mm")
    analysis.close()
    print(f"  Dynamic: {ok_count}/{n_steps} steps converged "
          f"(t_final={ops.getTime():.2f}s).")
    return ok_count == n_steps


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb, output_dir: Path) -> None:
    """Flush ODB, render deformed-shape HTML, write roof-disp summary."""
    odb.save_response()
    print("  ODB saved.")

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
    """Build the model, run gravity + dynamic. Returns odb."""
    output_dir.mkdir(parents=True, exist_ok=True)
    d = _compute_derived()

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

    # Ground motion MUST be defined after loadConst (§12i)
    motion_dir = Path(__file__).parent / "ground_motions"
    define_ground_motion(motion_dir)

    print("=== Rayleigh Damping ===")
    _setup_rayleigh_damping()

    print("=== Dynamic (seismic) ===")
    run_dynamic(odb)
    return odb


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print("\n=== Complete ===")
