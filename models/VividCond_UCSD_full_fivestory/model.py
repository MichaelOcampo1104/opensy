# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 5-Story RC Frame-Wall Building — Dual Perimeter Frames + Walls
UniqueID : VividCond_UCSD_full_fivestory
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-10
Purpose  : 3D nonlinear seismic time-history analysis of a 5-story reinforced-
           concrete building with two 2-bay perimeter moment frames (south &
           north), two planar RC shear walls, diagonal corotTruss braces, and
           rigid floor diaphragms. Gravity → Rayleigh damping → seismic time-
           history under a horizontal ground motion.
Ref      : Kuanshi Zhong (Stanford / UCSD) frame-wall building framework.
           Source: models/VividCond_UCSD_full_fivestory/tcl_ref/ (9 Tcl files:
           UCSDFrameWall, RunTests, SolverNewmark, CreateConcreteMaterial,
           BuildRCrectSection3D, CreateRCWallSection, GetGaussLobattoIP,
           RecorderAnalysis). Source runs 13 triaxial base_motions/ (not in
           repo); NR94cnp.txt (Northridge-1994, X-direction, dt=0.01s, ~2495
           pts, g-units, reused from VividConcrete/elkady2019) used for
           validation. run_dynamic() is generic so real records drop in.
Units    : N, mm, MPa  (converted from source imperial: in, kip, ksi)

NOTE     : Source is imperial (in, kip, ksi); converted to N-mm-MPa via the
           standards/units.py constants (inch, kip, ksi). All confined concrete
           properties (rectangular ke1*ke2*ke3/(1-rou_cc) confinement, fpc,
           epsc0, epsU), the Hysteretic shear backbone, the Steel02 post-yield
           tangent, the DuctileFracture CPM coefficients, and the Bond_SP01
           slip are derived mirroring the source Tcl expr chains
           (CreateConcreteMaterial.tcl, UCSDFrameWall.tcl), then unit-converted
           at material-definition time.

SOLVER NOTE: Source gravity uses Transformation + BandGeneral + LoadControl;
             dynamic uses Transformation + SparseGEN + Newmark with an adaptive
             dt/tol/algorithm recovery loop. Reproduced as: gravity via manual
             LoadControl loop (allowed SmartAnalyze exception); dynamic via
             opst.anlys.SmartAnalyze (Transient) with the repo-convention retry
             settings (§12am). SparseGEN is not compiled in this OpenSeesPy
             build, so BandGeneral is used (per §12af).

GM:       NR94cnp.txt loaded as a single UniformExcitation in direction 1 (X).
          GM defined AFTER loadConst (§12i) so gravity is frozen correctly.
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import math
import sys
from pathlib import Path

import openseespy.opensees as ops
import opstool as opst

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import inch, kip, ksi, MPa, N, mm, ft
from vis_utils import (vis_nodes, vis_model, vis_loads, vis_pre_analysis,
                       vis_defo, vis_slider, _headless)


# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Node-id scheme (source UCSDFrameWall.tcl):  floor*1000 + group*100 + col*10
#   group 100 = south frame cols, 200 = north frame cols,
#   300 = rigid-diaphragm master, 500 = walls.
NUM_STORIES = 5
FT = 12.0 * inch                       # one source-foot in mm


def _nd(floor, group, col=0):
    """Floor/group/col -> source node tag (floor*1000 + group + col*10)."""
    return floor * 1000 + group + col * 10


# diaphragm master nodes (one per floor 1..5)
CTRL_NODES = [_nd(s, 300) for s in range(1, NUM_STORIES + 1)]

# Geometric transformations: per-story, per-element (source: 100000+/200000+/300000+ blocks)
#   1xxxxx = south frame, 2xxxxx = north frame, 3xxxxx = walls + Y-beams.

# Time series & load patterns
TS_GRAVITY = 1
PAT_GRAVITY = 1
TS_GM = 100                            # ground-motion accel time series
PAT_GM = 100                           # UniformExcitation tag

ODB_TAG = 1

# Brace material
MAT_BRACE = 999

# Element tag scheme mirrors source (floor*1000 + group + col*10):
#   south cols 100+, south beams 200+, north cols 300+, north beams 400+,
#   Y-beam 900, walls 500+, braces 9000+.

# Gauss-Lobatto N=6 (port of GetGaussLobattolLIP.tcl)
_GAUSS_LOBATTO_6 = {
    "xi": [-1.0, -0.7650553239, -0.2852315164, 0.2852315164, 0.7650553239, 1.0],
    "wt": [0.06666666667, 0.3784749562, 0.5548583770,
           0.5548583770, 0.3784749562, 0.06666666667],
}


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# All source values imperial (in, kip, ksi); converted to N, mm, MPa at use.

# Geometry (UCSDFrameWall.tcl §geometry)
NUM_BAYS_X = 2
NUM_BAYS_Y = 1
NUM_WALLS = 2
H_STORY = 12.0 * ft                          # story height (144 in)
BAY_X = 17.0 * ft                            # x-bay width (204 in)
BAY_Y = 20.0 * ft                            # y-bay width (240 in)
WALL_LENGTH = 9.0 * ft                       # wall length (108 in)
WALL_THICKNESS = 7.5 * inch
WALL_CTR_X = [25.5 * inch, 138.6 * inch]     # wall centre x
WALL_CTR_Y = [180.0 * inch, 180.0 * inch]    # wall centre y
# south frame at y=0, north frame at y=120 ft, floor centre (17ft,10ft)
SOUTH_Y = 0.0
NORTH_Y = 120.0 * ft
FLR_CTR_X = 17.0 * ft
FLR_CTR_Y = 10.0 * ft
COL_START_X = 18.0 * ft                      # first column x (216 in)

# Section fibre discretisation
NF_CORE_Y = 10
NF_CORE_Z = 10
NF_COVER_Y = 2
NF_COVER_Z = 2
NF_WEB_Y = 5 * NF_CORE_Y                     # wall web fibres
C_CONCRETE = 1.375 * inch                    # cover to rebar centroid

# Slab (effective tributary slab for the slab-act-as-beam first bay)
SLAB_THICKNESS = 8.0 * inch
SLAB_WIDTH_EFF = 90.0 * inch
SLAB_DB_1 = 0.625 * inch
SLAB_DB_2 = 0.5 * inch
SLAB_N1 = round(SLAB_WIDTH_EFF / inch / 8.0)
SLAB_N2 = round(SLAB_WIDTH_EFF / inch / 16.0)
SLAB_C = 1.0 * inch

# Per-story section sizes (lists, index = story 0..4) --- in inches source
H_BEAM = [28.0, 28.0, 28.0, 28.0, 28.0]
B_BEAM = [12.0, 12.0, 12.0, 12.0, 12.0]
H_COL = [26.0, 26.0, 26.0, 26.0, 26.0]
B_COL = [18.0, 18.0, 18.0, 18.0, 18.0]

# Beam reinforcement
RT_BEAM = [0.008, 0.008, 0.008, 0.008, 0.016]
S_BEAM = [4.0, 4.0, 4.0, 4.0, 4.0]
DB_BEAM = [0.875, 0.875, 0.875, 0.875, 0.875]
NL_BEAM = [4, 4, 4, 4, 8]
FYL_BEAM = [130.0, 130.0, 125.0, 125.0, 73.5]
FUL_BEAM = [160.0, 160.0, 160.0, 160.0, 97.0]
ESU_BEAM = [0.05, 0.05, 0.05, 0.05, 0.15]
FYT_BEAM = [69.0, 69.0, 69.0, 69.0, 69.0]

# Column reinforcement (two bar sizes per column)
RT_COL = [0.008, 0.008, 0.008, 0.008, 0.008]
S_COL = [4.0, 4.0, 4.0, 4.0, 4.0]
DB_COL_1 = [1.128, 1.128, 1.128, 1.128, 1.128]
NL_COL_1 = [4, 4, 4, 4, 4]
FYL_COL_1 = [79.5, 79.5, 79.5, 79.5, 79.5]
FUL_COL_1 = [119.3, 119.3, 119.3, 119.3, 119.3]
ESU_COL_1 = [0.12, 0.12, 0.12, 0.12, 0.12]
DB_COL_2 = [0.75, 0.75, 0.75, 0.75, 0.75]
NL_COL_2 = [6, 6, 6, 6, 6]
FYL_COL_2 = [84.5, 84.5, 84.5, 84.5, 84.5]
FUL_COL_2 = [118.8, 118.8, 118.8, 118.8, 118.8]
ESU_COL_2 = [0.12, 0.12, 0.12, 0.12, 0.12]
FYT_COL = [80.0, 80.0, 80.0, 80.0, 80.0]

# Wall reinforcement
RT_WALL = [0.0025, 0.0025, 0.0025, 0.0025, 0.0025]
S_WALL = [6.0, 6.0, 6.0, 6.0, 6.0]
DB_WALL_1 = [1.128, 1.128, 1.128, 1.128, 1.128]   # boundary-element bars
NL_WALL_1 = [4, 4, 4, 4, 4]
FYL_WALL_1 = [79.5, 79.5, 79.5, 79.5, 79.5]
FUL_WALL_1 = [119.3, 119.3, 119.3, 119.3, 119.3]
ESU_WALL_1 = [0.12, 0.12, 0.12, 0.12, 0.12]
DB_WALL_2 = [0.375, 0.375, 0.375, 0.375, 0.375]   # web bars
NL_WALL_2 = [15, 15, 15, 15, 15]
FYL_WALL_2 = [80.0, 80.0, 80.0, 80.0, 80.0]
FUL_WALL_2 = [106.0, 106.0, 106.0, 106.0, 106.0]
ESU_WALL_2 = [0.12, 0.12, 0.12, 0.12, 0.12]
FYT_WALL = [80.0, 80.0, 80.0, 80.0, 80.0]
ALPHA_C_WALL = 2.0                              # wall shear alpha_c

# Concrete strengths (ksi source)
FC0_COL_WALL = -8.3                             # ksi, column/wall
FC0_BEAM = -7.5                                 # ksi, beam/slab

# Steel + fracture flags
ES_STEEL = 29000.0                              # ksi, all steel Young's modulus
FRAC_TAG = 1                                    # 1 = use DuctileFracture, 0 = plain Steel02
PHI_COL = 0.01                                  # buckling length coeff (column)
PHI_BEAM = 0.25                                 # buckling length coeff (beam)
PHI_WALL = 0.01                                 # buckling length coeff (wall)

# Mass and gravity
G_INCH = 386.4                                  # in/s^2 (source g)
W_STORY = [166.1, 168.2, 228.4, 226.3, 134.8]   # kip, story weights
# tributary gravity-load fractions per node group (source pr_1..pr_5)
PR = [0.18, 0.12, 0.12, 0.12, 0.12]
MASS_SMALL = 1.0e-6                             # regularization mass (N s^2/mm)
MASS_SMALL_2 = 1.0e-3                           # rotational regularization mass

# Integration
NUM_IP = 6

# Damping
XDAMP = 0.02

# Ground motion (validation substitute; real records drop in via these params)
GM_FILE = "NR94cnp.txt"
GM_DT = 0.01
GM_NPTS = 2495
GM_FACTOR = G_INCH * inch                       # g (in/s^2) -> mm/s^2
GM_DIR = 1                                      # X

# Throttle ODB writes during the transient run
ODB_EVERY_N = 10


# ── 4. DERIVED PROPERTY HELPERS (source ksi/kip/in domain) ────────────────────
def _unconfined_concrete02(fc_k, LIP_in):
    """Port of DefineRegularizedUnconfinedConcreteMaterial 'Concrete02' branch.

    Pugh et al. (2015) fracture-energy regularization. Returns stress/strain in
    source domain (ksi, dimensionless). fc_k in ksi, LIP_in in inches.
    """
    mm_in = 25.4
    mpa_ksi = 6.895
    fpc = fc_k
    epsc0 = -0.002
    fpcu = 0.2 * fpc
    Gfc = 2.0 * (-fc_k) * mpa_ksi
    Ec_temp = 57.0 * math.sqrt(-fc_k * 1000.0) * mpa_ksi
    epsU = -(Gfc / 0.6 / (-fc_k) / (LIP_in * mm_in)
             - 0.8 * (-fc_k) / Ec_temp + (-epsc0))
    lam = 0.1
    ft = 0.004 * math.sqrt(-fc_k * 1000.0)              # ksi (note: 0.004 here)
    Ec = 57.0 * math.sqrt(-fc_k * 1000.0)
    Ets = Ec * 0.05                                      # ksi
    return dict(fpc=fpc, epsc0=epsc0, fpcu=fpcu, epsU=epsU,
                lam=lam, ft=ft, ets=Ets)


def _confined_concrete02(fc_k, nl, s_in, b_in, d_in, db_in, rou, fyt_k, LIP_in):
    """Port of DefineRegularizedConfinedConcreteMaterial 'Concrete02' branch.

    Rectangular confinement factor ke = ke1*ke2*ke3/(1-rou_cc). Returns
    stress/strain in source domain. fc_k,fyt_k in ksi; s,b,d,db,LIP in inches.
    """
    mm_in = 25.4
    mpa_ksi = 6.895
    n = nl / 2.0
    wi = (b_in - n * db_in) / (n - 1.0)
    ke1 = 1.0 - n * wi ** 2 / 6.0 / b_in / d_in
    ke2 = 1.0 - 0.5 * s_in / b_in
    ke3 = 1.0 - 0.5 * s_in / d_in
    rou_cc = n * 0.25 * 3.14 * db_in ** 2 / b_in / d_in
    ke = ke1 * ke2 * ke3 / (1.0 - rou_cc)

    fl = ke * rou * fyt_k
    Kfc = (-1.254 + 2.254 * math.sqrt(1.0 + 7.94 * fl / (-fc_k))
           - 2.0 * fl / (-fc_k))
    fpc = Kfc * fc_k
    Keps = 1.0 + 5.0 * (Kfc - 1.0)
    epsc0 = Keps * (-0.002)
    fpcu = 0.2 * fpc
    Gfc = 1.7 * 2.0 * (-fc_k) * mpa_ksi
    Ec_temp = 57.0 * math.sqrt(-fc_k * 1000.0) * mpa_ksi
    epsU = -(Gfc / 0.6 / (-fpc) / (LIP_in * mm_in)
             - 0.8 * (-fpc) / Ec_temp + (-epsc0))
    lam = 0.1
    ft = 0.004 * math.sqrt(-fc_k * 1000.0)              # ksi
    Ec = 57.0 * math.sqrt(-fc_k * 1000.0)
    Ets = Ec * 0.05                                      # ksi
    return dict(fpc=fpc, epsc0=epsc0, fpcu=fpcu, epsU=epsU,
                lam=lam, ft=ft, ets=Ets)


def _shear_hysteretic(fc_k, alpha_c, rou_t, fyt_k, lw_in, bw_in):
    """Port of CreatePlanarWallSection §shear / BuildRCrectSection §GA.

    Returns s1..s3 (kip) and e1..e3 (dimensionless). fc_k,fyt_k in ksi;
    lw,bw in inches.
    """
    Ec = 57.0 * math.sqrt(-fc_k * 1000.0)
    Gc = Ec / 2.0 / (1.0 + 0.2)
    vn = alpha_c * math.sqrt(-fc_k * 1000.0) / 1000.0 + rou_t * fyt_k
    vn_cap = 8.0 * math.sqrt(-fc_k * 1000.0) / 1000.0
    if vn > vn_cap:
        vn = vn_cap
    s1p = 0.002 * math.sqrt(-fc_k * 1000.0) * lw_in * bw_in
    e1p = s1p / Gc / (lw_in * bw_in)
    s2p = 0.6 * vn * lw_in * bw_in
    e2p = e1p + (s2p - s1p) / 0.4 / Gc / (lw_in * bw_in)
    s3p = vn * lw_in * bw_in
    e3p = e2p + 0.4 * vn / 0.1 / Gc
    return dict(s1p=s1p, e1p=e1p, s2p=s2p, e2p=e2p, s3p=s3p, e3p=e3p)


def _steel02_b(fyl_k, ful_k, esu, es_k=ES_STEEL):
    """Steel02 post-yield tangent b = (ful-fyl)/((esu-fyl/Es)*Es)."""
    return (ful_k - fyl_k) / (esu - fyl_k / es_k) / es_k


def _df_params(esu, fyl_k, ful_k, db_in, phi, s_in):
    """DuctileFracture CPM coefficients (UCSDFrameWall.tcl §steel fracture)."""
    c_mono = math.exp(-3.96 - 1.85 * math.log(esu) + 0.2 * math.log(db_in / 8.0))
    c_cycl = math.exp(5.90 + 1.53 * math.log(fyl_k / 60.0)
                      + 2.32 * math.log(esu) + 1.11 * math.log(db_in / 8.0))
    c_symm = 1.05
    k1 = math.exp(2.21 - 0.32 * math.log(ful_k / fyl_k)
                  - 0.66 * math.log(db_in / 8.0))
    k2 = math.exp(1.29 + 0.64 * math.log(fyl_k / 60.0)
                  - 0.46 * math.log(db_in / 8.0))
    b1 = math.exp(-2.53 - 1.90 * math.log(ful_k / fyl_k)
                  - 1.36 * math.log(db_in / 8.0))
    b2 = math.exp(-3.29 - 0.49 * math.log(esu)
                  - 0.7 * math.log(phi * s_in / db_in))
    return dict(c_mono=c_mono, c_cycl=c_cycl, c_symm=c_symm,
                k1=k1, k2=k2, b1=b1, b2=b2)


def _bond_sp01_sy(db_in, fyl_k, fc_k, LIP_in):
    """Bond_SP01 yield slip Sy = (0.013+0.1*(db/4000*fyl/sqrt(|fc|*1000)*(2*0.4+1))^2.5)/LIP."""
    inner = db_in / 4000.0 * fyl_k / math.sqrt(abs(fc_k * 1000.0)) * (2.0 * 0.4 + 1.0)
    return (0.013 + 0.1 * inner ** 2.5) / LIP_in


def _gauss_lobatto_ip():
    """Return (LIP, LIPR, XIP) lists for col/wall (h_story) and beam (bay_x)."""
    LIP_cw, LIPR_cw, XIP_cw = [], [], []
    for i in range(NUM_IP):
        wt = _GAUSS_LOBATTO_6["wt"][i]
        xi = _GAUSS_LOBATTO_6["xi"][i]
        LIPR_cw.append(0.5 * wt)
        LIP_cw.append(0.5 * wt * (H_STORY / inch))
        XIP_cw.append(0.5 * xi + 0.5)
    LIP_b, LIPR_b, XIP_b = [], [], []
    for i in range(NUM_IP):
        wt = _GAUSS_LOBATTO_6["wt"][i]
        xi = _GAUSS_LOBATTO_6["xi"][i]
        LIPR_b.append(0.5 * wt)
        LIP_b.append(0.5 * wt * (BAY_X / inch))
        XIP_b.append(0.5 * xi + 0.5)
    return (LIP_cw, LIPR_cw, XIP_cw), (LIP_b, LIPR_b, XIP_b)


# ── 5. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and create a 3D BasicBuilder (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 6. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Per-story, per-IP concrete (cover+core for col/wall and beam) + per-story
    Steel02, DuctileFracture, Bond_SP01, and the brace ElasticPPGap.

    Tag scheme mirrors the source exactly:
      concrete : story*1000 + ip*10 + {1 col/wall cover, 2 beam cover,
                                       4 col/wall core,  5 beam core}
      Steel02  : story*1000 + {101 beam, 102 col#1, 103 col#2, 104 wall#1, 105 wall#2}
      DuctileFracture : story*1000 + {201..205} wrapping the matching Steel02
      Bond_SP01: story*1000 + {301..305}
    """
    (LIP_cw, _, _), (LIP_b, _, _) = _gauss_lobatto_ip()

    for s in range(NUM_STORIES):
        # cur_* are source-domain scalars (in, ksi, dimensionless)
        nl_col = NL_COL_1[s] + NL_COL_2[s]
        # ---- concrete: per IP ----
        for ip in range(NUM_IP):
            base = s * 1000 + ip * 10
            cov_cw = _unconfined_concrete02(FC0_COL_WALL, LIP_cw[ip])
            cov_b = _unconfined_concrete02(FC0_BEAM, LIP_b[ip])
            core_cw = _confined_concrete02(FC0_COL_WALL, nl_col, S_COL[s],
                                           B_COL[s], 0.9 * H_COL[s],
                                           DB_COL_1[s], RT_COL[s], FYT_COL[s],
                                           LIP_cw[ip])
            core_b = _confined_concrete02(FC0_BEAM, NL_BEAM[s], S_BEAM[s],
                                          B_BEAM[s], 0.9 * H_BEAM[s],
                                          DB_BEAM[s], RT_BEAM[s], FYT_BEAM[s],
                                          LIP_b[ip])
            _concrete02(base + 1, cov_cw)      # col/wall cover
            _concrete02(base + 2, cov_b)       # beam cover
            _concrete02(base + 4, core_cw)     # col/wall core
            _concrete02(base + 5, core_b)      # beam core

        # ---- Steel02 (story-level) ----
        b_beam = _steel02_b(FYL_BEAM[s], FUL_BEAM[s], ESU_BEAM[s])
        b_c1 = _steel02_b(FYL_COL_1[s], FUL_COL_1[s], ESU_COL_1[s])
        b_c2 = _steel02_b(FYL_COL_2[s], FUL_COL_2[s], ESU_COL_2[s])
        b_w1 = _steel02_b(FYL_WALL_1[s], FUL_WALL_1[s], ESU_WALL_1[s])
        b_w2 = _steel02_b(FYL_WALL_2[s], FUL_WALL_2[s], ESU_WALL_2[s])
        ops.uniaxialMaterial("Steel02", s * 1000 + 101, FYL_BEAM[s] * ksi,
                             ES_STEEL * ksi, b_beam, 18, 0.925, 0.15)
        ops.uniaxialMaterial("Steel02", s * 1000 + 102, FYL_COL_1[s] * ksi,
                             ES_STEEL * ksi, b_c1, 18, 0.925, 0.15)
        ops.uniaxialMaterial("Steel02", s * 1000 + 103, FYL_COL_2[s] * ksi,
                             ES_STEEL * ksi, b_c2, 18, 0.925, 0.15)
        ops.uniaxialMaterial("Steel02", s * 1000 + 104, FYL_WALL_1[s] * ksi,
                             ES_STEEL * ksi, b_w1, 18, 0.925, 0.15)
        ops.uniaxialMaterial("Steel02", s * 1000 + 105, FYL_WALL_2[s] * ksi,
                             ES_STEEL * ksi, b_w2, 18, 0.925, 0.15)

        # ---- DuctileFracture wrapping each Steel02 ----
        if FRAC_TAG == 1:
            _df(s * 1000 + 201, s * 1000 + 101, ESU_BEAM[s], FYL_BEAM[s], FUL_BEAM[s],
                DB_BEAM[s], PHI_BEAM, S_BEAM[s])
            _df(s * 1000 + 202, s * 1000 + 102, ESU_COL_1[s], FYL_COL_1[s], FUL_COL_1[s],
                DB_COL_1[s], PHI_COL, S_COL[s])
            _df(s * 1000 + 203, s * 1000 + 103, ESU_COL_2[s], FYL_COL_2[s], FUL_COL_2[s],
                DB_COL_2[s], PHI_COL, S_COL[s])
            _df(s * 1000 + 204, s * 1000 + 104, ESU_WALL_1[s], FYL_WALL_1[s], FUL_WALL_1[s],
                DB_WALL_1[s], PHI_WALL, S_WALL[s])
            _df(s * 1000 + 205, s * 1000 + 105, ESU_WALL_2[s], FYL_WALL_2[s], FUL_WALL_2[s],
                DB_WALL_2[s], PHI_BEAM, S_WALL[s])

        # ---- Bond_SP01 (barslip_tag=0 in source → not used for end IPs, but
        # define them anyway so the tag scheme is intact for future use) ----
        sy_b = _bond_sp01_sy(DB_BEAM[s], FYL_BEAM[s], FC0_BEAM, LIP_b[0])
        su_b = 40.0 * sy_b
        ops.uniaxialMaterial("Bond_SP01", s * 1000 + 301, FYL_BEAM[s] * ksi,
                             sy_b * inch, FUL_BEAM[s] * ksi, su_b * inch, 0.3, 0.5)
        sy_c1 = _bond_sp01_sy(DB_COL_1[s], FYL_COL_1[s], FC0_COL_WALL, LIP_cw[0])
        su_c1 = 40.0 * sy_c1
        ops.uniaxialMaterial("Bond_SP01", s * 1000 + 302, FYL_COL_1[s] * ksi,
                             sy_c1 * inch, FUL_COL_1[s] * ksi, su_c1 * inch, 0.3, 1.0)
        sy_c2 = _bond_sp01_sy(DB_COL_2[s], FYL_COL_2[s], FC0_COL_WALL, LIP_cw[0])
        su_c2 = 40.0 * sy_c2
        ops.uniaxialMaterial("Bond_SP01", s * 1000 + 303, FYL_COL_2[s] * ksi,
                             sy_c2 * inch, FUL_COL_2[s] * ksi, su_c2 * inch, 0.3, 1.0)
        sy_w1 = _bond_sp01_sy(DB_WALL_1[s], FYL_WALL_1[s], FC0_COL_WALL, LIP_cw[0])
        su_w1 = 40.0 * sy_w1
        ops.uniaxialMaterial("Bond_SP01", s * 1000 + 304, FYL_WALL_1[s] * ksi,
                             sy_w1 * inch, FUL_WALL_1[s] * ksi, su_w1 * inch, 0.3, 1.0)
        sy_w2 = _bond_sp01_sy(DB_WALL_2[s], FYL_WALL_2[s], FC0_COL_WALL, LIP_cw[0])
        su_w2 = 40.0 * sy_w2
        ops.uniaxialMaterial("Bond_SP01", s * 1000 + 305, FYL_WALL_2[s] * ksi,
                             sy_w2 * inch, FUL_WALL_2[s] * ksi, su_w2 * inch, 0.3, 1.0)

    # diagonal brace (ElasticPPGap) — source uses 68 ksi yield
    ops.uniaxialMaterial("ElasticPPGap", MAT_BRACE, ES_STEEL * ksi, 68.0 * ksi,
                         0.0, 0.005)


def _concrete02(tag, d):
    """Define a Concrete02 from a derived-property dict (source-domain values)."""
    ops.uniaxialMaterial("Concrete02", tag,
                         d["fpc"] * ksi, d["epsc0"], d["fpcu"] * ksi, d["epsU"],
                         d["lam"], d["ft"] * ksi, d["ets"] * ksi)


def _df(tag, steel_tag, esu, fyl_k, ful_k, db_in, phi, s_in):
    p = _df_params(esu, fyl_k, ful_k, db_in, phi, s_in)
    ops.uniaxialMaterial("DuctileFracture", tag, steel_tag,
                         "-c_mono", p["c_mono"], "-c_cycl", p["c_cycl"],
                         "-c_symm", p["c_symm"],
                         "-E_s", ES_STEEL * ksi, "-esu", esu,
                         "-k1", p["k1"], "-k2", p["k2"],
                         "-db", db_in * inch,
                         "-b1", p["b1"], "-b2", p["b2"])


# ── 7. SECTIONS ──────────────────────────────────────────────────────────────
def _build_rc_rect_section(id_tag, h_in, b_in, cover_h_in, cover_b_in,
                           core_mat, cover_mat, steel_mat,
                           n_top, a_top, n_bot, a_bot, n_int_tot, a_int,
                           GJ, GA):
    """Port of BuildRCrectSection3D.tcl.

    Rectangular fiber section (tag = id*1000+1) with confined core, four cover
    patches, top/bot/intermediate rebar layers; then an Elastic shear material
    (id*1000+1, reused as a uniaxial tag) aggregated onto Vy/Vz producing the
    aggregator section (tag = id).
    """
    h = h_in * inch
    b = b_in * inch
    ch = cover_h_in * inch
    cb = cover_b_in * inch
    coverY = h / 2.0
    coverZ = b / 2.0
    coreY = coverY - ch
    coreZ = coverZ - cb
    ncoreY = -coreY
    ncoreZ = -coreZ
    ncoverY = -coverY
    ncoverZ = -coverZ
    n_int = n_int_tot // 2

    fiber_tag = id_tag * 1000 + 1
    ops.section("Fiber", fiber_tag, "-GJ", GJ)
    # core
    ops.patch("quadr", core_mat, NF_CORE_Z, NF_CORE_Y,
              ncoreY, coreZ, ncoreY, ncoreZ, coreY, ncoreZ, coreY, coreZ)
    # four covers
    ops.patch("quadr", cover_mat, 2, NF_COVER_Y,
              ncoverY, coverZ, ncoreY, coreZ, coreY, coreZ, coverY, coverZ)
    ops.patch("quadr", cover_mat, 2, NF_COVER_Y,
              ncoreY, ncoreZ, ncoverY, ncoverZ, coverY, ncoverZ, coreY, ncoreZ)
    ops.patch("quadr", cover_mat, NF_COVER_Z, 2,
              ncoverY, coverZ, ncoverY, ncoverZ, ncoreY, ncoreZ, ncoreY, coreZ)
    ops.patch("quadr", cover_mat, NF_COVER_Z, 2,
              coreY, coreZ, coreY, ncoreZ, coverY, ncoverZ, coverY, coverZ)
    # rebar
    if n_int > 0:
        ops.layer("straight", steel_mat, n_int, a_int * inch ** 2,
                  ncoreY, coreZ, coreY, coreZ)
        ops.layer("straight", steel_mat, n_int, a_int * inch ** 2,
                  ncoreY, ncoreZ, coreY, ncoreZ)
    ops.layer("straight", steel_mat, n_top, a_top * inch ** 2,
              coreY, coreZ, coreY, ncoreZ)
    ops.layer("straight", steel_mat, n_bot, a_bot * inch ** 2,
              ncoreY, coreZ, ncoreY, ncoreZ)

    # shear: Elastic (source uses an Elastic shear in BuildRCrectSection via GA)
    ops.uniaxialMaterial("Elastic", fiber_tag, GA)
    ops.section("Aggregator", id_tag, fiber_tag, "Vy", fiber_tag, "Vz",
                "-section", fiber_tag)


def _create_planar_wall_section(id_tag, steel_w1, steel_w2, steel_w3,
                                core1, core2, core3, cover_mat,
                                shear_mat):
    """Port of CreatePlanarWallSection (boundary elements + web + shear).

    Fiber section tag = id+10000; aggregator section tag = id. Shear material
    (Hysteretic) tag = id+10000 (same int, separate uniaxial namespace) — passed
    in pre-built.
    """
    lw = WALL_LENGTH
    bw = WALL_THICKNESS
    cover = C_CONCRETE
    lbe1 = 18.0 * inch
    lbe2 = 18.0 * inch
    db1 = DB_WALL_1[0] * inch
    db2 = DB_WALL_1[0] * inch
    db3 = DB_WALL_2[0] * inch
    a1 = 0.25 * 3.14 * DB_WALL_1[0] ** 2 * inch ** 2
    a3 = 0.25 * 3.14 * DB_WALL_2[0] ** 2 * inch ** 2
    num_be = NL_WALL_1[0] // 2          # top/bot bars in each boundary element
    num_web = NL_WALL_2[0]

    coverY = lw / 2.0
    coverZ = bw / 2.0
    webY = lw / 2.0 - cover - lbe1
    nwebY = -lw / 2.0 + cover + lbe2
    ncoverY = -coverY
    ncoverZ = -coverZ
    coreY = coverY - cover
    coreZ = coverZ - cover
    ncoreY = -coreY
    ncoreZ = -coreZ

    fiber_tag = id_tag + 10000
    GJ = 1.0e9 * kip * inch ** 2
    ops.section("Fiber", fiber_tag, "-GJ", GJ)
    # upper boundary-element core
    ops.patch("quadr", core1, NF_CORE_Y, NF_CORE_Z,
              webY, coreZ, webY, ncoreZ, coreY, ncoreZ, coreY, coreZ)
    # lower boundary-element core
    ops.patch("quadr", core2, NF_CORE_Y, NF_CORE_Z,
              ncoreY, coreZ, ncoreY, ncoreZ, nwebY, ncoreZ, nwebY, coreZ)
    # side covers
    ops.patch("quadr", cover_mat, NF_CORE_Y, NF_COVER_Z,
              webY, coverZ, webY, coreZ, coreY, coreZ, coverY, coverZ)
    ops.patch("quadr", cover_mat, NF_CORE_Y, NF_COVER_Z,
              webY, ncoreZ, webY, ncoverZ, coverY, ncoverZ, coreY, ncoreZ)
    ops.patch("quadr", cover_mat, NF_CORE_Y, NF_COVER_Z,
              ncoverY, coverZ, ncoreY, coreZ, nwebY, coreZ, nwebY, coverZ)
    ops.patch("quadr", cover_mat, NF_CORE_Y, NF_COVER_Z,
              ncoreY, ncoreZ, ncoverY, ncoverZ, nwebY, ncoverZ, nwebY, ncoreZ)
    # top & bottom covers
    ops.patch("quadr", cover_mat, NF_COVER_Y, NF_CORE_Z,
              ncoverY, coverZ, ncoverY, ncoverZ, ncoreY, ncoreZ, ncoreY, coreZ)
    ops.patch("quadr", cover_mat, NF_COVER_Y, NF_CORE_Z,
              coreY, coreZ, coreY, ncoreZ, coverY, ncoverZ, coverY, coverZ)
    # web concrete
    if NF_WEB_Y > 0:
        ops.patch("quadr", core3, NF_WEB_Y, NF_COVER_Z,
                  nwebY, coverZ, nwebY, coreZ, webY, coreZ, webY, coverZ)
        ops.patch("quadr", core3, NF_WEB_Y, NF_COVER_Z,
                  nwebY, coreZ, nwebY, ncoreZ, webY, ncoreZ, webY, coreZ)
        ops.patch("quadr", core3, NF_WEB_Y, NF_COVER_Z,
                  nwebY, ncoreZ, nwebY, ncoverZ, webY, ncoverZ, webY, ncoreZ)

    # boundary-element steel: top + bottom layers (1 bar each end per source call:
    # numBotBars1=numTopBars1=1, numInterLayers1=1)
    ops.layer("straight", steel_w1, 1, a1,
              coreY - 0.5 * db1, coreZ - 0.5 * db1,
              coreY - 0.5 * db1, ncoreZ + 0.5 * db1)
    ops.layer("straight", steel_w1, 1, a1,
              webY + 0.5 * db1, coreZ - 0.5 * db1,
              webY + 0.5 * db1, ncoreZ + 0.5 * db1)
    # one intermediate layer in upper BE
    inter_sp1 = (lbe1 - 2 * db1) / (1 + 1)
    ld1 = coreY - 0.5 * db1 - inter_sp1
    ops.layer("straight", steel_w1, 2, a1, ld1, coreZ - 0.5 * db1,
              ld1, ncoreZ + 0.5 * db1)
    # lower BE
    ops.layer("straight", steel_w2, 1, a1,
              ncoreY + 0.5 * db2, coreZ - 0.5 * db2,
              ncoreY + 0.5 * db2, ncoreZ + 0.5 * db2)
    ops.layer("straight", steel_w2, 1, a1,
              nwebY - 0.5 * db2, coreZ - 0.5 * db2,
              nwebY - 0.5 * db2, ncoreZ + 0.5 * db2)
    inter_sp2 = (lbe2 - 2 * db2) / (1 + 1)
    ld2 = ncoreY + 0.5 * db2 + inter_sp2
    ops.layer("straight", steel_w2, 2, a1, ld2, coreZ - 0.5 * db2,
              ld2, ncoreZ + 0.5 * db2)
    # web steel layers
    if num_web > 0:
        inter_sp3 = (webY - nwebY) / (num_web + 1)
        ld3 = nwebY + inter_sp3
        for _ in range(num_web):
            ops.layer("straight", steel_w3, 2, a3, ld3, coreZ - 0.5 * db3,
                      ld3, ncoreZ + 0.5 * db3)
            ld3 += inter_sp3

    # aggregate shear (Vy, Vz) onto the fiber section
    ops.section("Aggregator", id_tag, shear_mat, "Vy", shear_mat, "Vz",
                "-section", fiber_tag)


def _wall_shear_material(id_tag):
    """Hysteretic shear material for a wall section (source CreatePlanarWallSection)."""
    sh = _shear_hysteretic(FC0_COL_WALL, ALPHA_C_WALL, RT_WALL[0], FYT_WALL[0],
                           WALL_LENGTH / inch, WALL_THICKNESS / inch)
    _define_hysteretic_shear(id_tag, sh)


def _define_hysteretic_shear(mat_tag, sh):
    s1p, e1p, s2p, e2p, s3p, e3p = (sh["s1p"], sh["e1p"], sh["s2p"],
                                    sh["e2p"], sh["s3p"], sh["e3p"])
    ops.uniaxialMaterial("Hysteretic", mat_tag,
                         s1p * kip, e1p, s2p * kip, e2p, s3p * kip, e3p,
                         -s1p * kip, -e1p, -s2p * kip, -e2p, -s3p * kip, -e3p,
                         1.0, 1.0, 0.0, 0.0, 0.0)


def define_sections() -> None:
    """Build per-story, per-IP beam/column/wall/slab sections.

    Section tags (source):
      beam   story*1000 + 100 + ip     (BuildRCrectSection)
      column story*1000 + 200 + ip     (BuildRCrectSection)
      wall   story*1000 + 300 + ip     (CreatePlanarWallSection)
      slab   story*1000 + 400 + ip     (BuildRCrectSection, slab-as-beam)
    Steel tag at end IPs uses DuctileFracture (201..205) if frac_tag=1 else Steel02.
    """
    for s in range(NUM_STORIES):
        # steel tags (end IPs use DF; interior IPs always use DF when frac_tag=1)
        s_be = s * 1000 + (101 + FRAC_TAG * 100)
        s_c1 = s * 1000 + (102 + FRAC_TAG * 100)
        s_c2 = s * 1000 + (103 + FRAC_TAG * 100)
        s_w1 = s * 1000 + (104 + FRAC_TAG * 100)
        s_w2 = s * 1000 + (105 + FRAC_TAG * 100)

        for ip in range(NUM_IP):
            base = s * 1000 + ip * 10
            # ---- beam section ----
            h_b = H_BEAM[s]; b_b = B_BEAM[s]
            GJ_b = (57.0 * math.sqrt(abs(FC0_BEAM * 1000)) / 2.0 / (1 + 0.3)
                    * h_b * b_b * (h_b ** 2 + b_b ** 2) / 12.0)
            GA_b = (57.0 * math.sqrt(abs(FC0_BEAM * 1000)) / 2.0 / (1 + 0.3)
                    * h_b * b_b)
            a_beam = 0.25 * 3.14 * DB_BEAM[s] ** 2
            _build_rc_rect_section(s * 1000 + 100 + ip, h_b, b_b,
                                   C_CONCRETE / inch, C_CONCRETE / inch,
                                   base + 5, base + 2, s_be,
                                   NL_BEAM[s] // 2, a_beam,
                                   NL_BEAM[s] // 2, a_beam,
                                   0, 0.0, GJ_b * kip * inch ** 2,
                                   GA_b * kip)
            # ---- column section ----
            h_c = H_COL[s]; b_c = B_COL[s]
            GJ_c = (57.0 * math.sqrt(abs(FC0_COL_WALL * 1000)) / 2.0 / (1 + 0.3)
                    * h_c * b_c * (h_c ** 2 + b_c ** 2) / 12.0)
            GA_c = (57.0 * math.sqrt(abs(FC0_COL_WALL * 1000)) / 2.0 / (1 + 0.3)
                    * h_c * b_c)
            a_c1 = 0.25 * 3.14 * DB_COL_1[s] ** 2
            a_c2 = 0.25 * 3.14 * DB_COL_2[s] ** 2
            a_int_c = (a_c1 * 2 + a_c2) / 3.0
            _build_rc_rect_section(s * 1000 + 200 + ip, h_c, b_c,
                                   C_CONCRETE / inch, C_CONCRETE / inch,
                                   base + 4, base + 1, s_c1,
                                   3, a_int_c, 3, a_int_c,
                                   2, a_c2, GJ_c * kip * inch ** 2,
                                   GA_c * kip)
            # ---- wall section ----
            wall_sec = s * 1000 + 300 + ip
            # wall core/cover concrete: source reuses col/wall cover (base+1)
            # for all 4 wall concrete tags; cores use base+1 too (source quirk)
            _wall_shear_material(wall_sec + 10000)
            _create_planar_wall_section(wall_sec, s_w1, s_w1, s_w2,
                                        base + 1, base + 1, base + 1, base + 1,
                                        wall_sec + 10000)
            # ---- slab section (first-bay slab-as-beam) ----
            GJ_sl = (57.0 * math.sqrt(abs(FC0_BEAM * 1000)) / 2.0 / (1 + 0.3)
                     * SLAB_THICKNESS / inch * SLAB_WIDTH_EFF / inch
                     * ((SLAB_THICKNESS / inch) ** 2
                        + (SLAB_WIDTH_EFF / inch) ** 2) / 12.0)
            GA_sl = (57.0 * math.sqrt(abs(FC0_BEAM * 1000)) / 2.0 / (1 + 0.3)
                     * SLAB_THICKNESS / inch * SLAB_WIDTH_EFF / inch)
            _build_rc_rect_section(s * 1000 + 400 + ip,
                                   SLAB_THICKNESS / inch, SLAB_WIDTH_EFF / inch,
                                   SLAB_C / inch, SLAB_C / inch,
                                   base + 2, base + 2, s_c1,
                                   SLAB_N2, 0.25 * 3.14 * (SLAB_DB_2 / inch) ** 2,
                                   SLAB_N1, 0.25 * 3.14 * (SLAB_DB_1 / inch) ** 2,
                                   0, 0.0, GJ_sl * kip * inch ** 2,
                                   GA_sl * kip)


# ── 8. NODES ─────────────────────────────────────────────────────────────────
def _story_mass(story_idx):
    """Story translational mass = W[kip] / g[mm/s^2]  (N s^2/mm). §12al."""
    return W_STORY[story_idx] * kip / (G_INCH * inch)


def define_nodes() -> None:
    """Nodes for floors 0..5 (source §nodes).

    Per floor: 3 south-frame nodes (group 100), 3 north-frame nodes (group 200),
    2 wall nodes (group 500), 1 rigid-diaphragm master (group 300). Frame/wall
    nodes carry mass_small regularization; the diaphragm master carries the full
    story translational mass.
    """
    for f in range(NUM_STORIES + 1):
        z = f * H_STORY
        # south frame (y=0)
        for c in range(NUM_BAYS_X + 1):
            x = COL_START_X + c * BAY_X
            ops.node(_nd(f, 100, c), x, SOUTH_Y, z,
                     "-mass", MASS_SMALL, MASS_SMALL, MASS_SMALL,
                     MASS_SMALL_2, MASS_SMALL_2, MASS_SMALL_2)
        # north frame (y=120 ft)
        for c in range(NUM_BAYS_X + 1):
            x = COL_START_X + c * BAY_X
            ops.node(_nd(f, 200, c), x, NORTH_Y, z,
                     "-mass", MASS_SMALL, MASS_SMALL, MASS_SMALL,
                     MASS_SMALL_2, MASS_SMALL_2, MASS_SMALL_2)
        # walls
        for w in range(NUM_WALLS):
            ops.node(_nd(f, 500, w), WALL_CTR_X[w], WALL_CTR_Y[w], z,
                     "-mass", MASS_SMALL, MASS_SMALL, MASS_SMALL,
                     MASS_SMALL_2, MASS_SMALL_2, MASS_SMALL_2)
        # rigid-diaphragm master
        if f > 0:
            m = _story_mass(f - 1)
            ops.node(_nd(f, 300), FLR_CTR_X, FLR_CTR_Y, z,
                     "-mass", m, m, m,
                     MASS_SMALL_2, MASS_SMALL_2, MASS_SMALL_2)
        else:
            ops.node(_nd(f, 300), FLR_CTR_X, FLR_CTR_Y, z)


# ── 9. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix all floor-0 nodes fully; constrain diaphragm masters: UZ, RX, RY fixed,
    UX/UY/RZ free (source: fix 0 0 1 1 1 0)."""
    for c in range(NUM_BAYS_X + 1):
        ops.fix(_nd(0, 100, c), 1, 1, 1, 1, 1, 1)
        ops.fix(_nd(0, 200, c), 1, 1, 1, 1, 1, 1)
    for w in range(NUM_WALLS):
        ops.fix(_nd(0, 500, w), 1, 1, 1, 1, 1, 1)
    ops.fix(_nd(0, 300), 1, 1, 1, 1, 1, 1)
    for f in range(1, NUM_STORIES + 1):
        ops.fix(_nd(f, 300), 0, 0, 1, 1, 1, 0)


def define_rigid_diaphragms() -> None:
    """Tie each floor's frame/wall nodes to the diaphragm master in DOF 3 (UZ is
    held by the master constraint; rigidDiaphragm 3 = the horizontal plane)."""
    for f in range(1, NUM_STORIES + 1):
        master = _nd(f, 300)
        slaves = []
        for c in range(NUM_BAYS_X + 1):
            slaves += [_nd(f, 100, c), _nd(f, 200, c)]
        for w in range(NUM_WALLS):
            slaves += [_nd(f, 500, w)]
        ops.rigidDiaphragm(3, master, *slaves)


# ── 10. ELEMENTS ─────────────────────────────────────────────────────────────
def _col_transf(story, frame_block, idx):
    """PDelta column transform with the source's -jntOffset (frame_block=100000
    south / 200000 north). vecx = (0,-1,0)."""
    dXi = dYi = 0.0
    dZi = 0.0 if story == 0 else 0.5 * H_BEAM[story - 1] * inch
    dXj = dYj = 0.0
    dZj = -0.5 * H_BEAM[story] * inch
    tag = frame_block + story * 100 + idx
    ops.geomTransf("PDelta", tag, 0.0, -1.0, 0.0,
                   "-jntOffset", dXi, dYi, dZi, dXj, dYj, dZj)
    return tag


def _beam_transf(story, frame_block, idx):
    """PDelta beam transform (vecx=(0,-1,0)) with ±0.5*h_col jntOffset."""
    dXi = 0.5 * H_COL[story] * inch
    dXj = -0.5 * H_COL[story] * inch
    tag = frame_block + story * 100 + idx * 10 + 9
    ops.geomTransf("PDelta", tag, 0.0, -1.0, 0.0,
                   "-jntOffset", dXi, 0.0, 0.0, dXj, 0.0, 0.0)
    return tag


def _user_defined_integration(integ_tag, story, sec_base, kind="col"):
    """UserDefined beamIntegration with 6 per-IP sections. kind 'col' uses the
    col/wall XIP/LIPR; 'beam' uses the beam XIP/LIPR."""
    (_, LIPR_cw, XIP_cw), (_, LIPR_b, XIP_b) = _gauss_lobatto_ip()
    sec_tags = [story * 1000 + sec_base + ip for ip in range(NUM_IP)]
    xips = XIP_cw if kind == "col" else XIP_b
    liprs = LIPR_cw if kind == "col" else LIPR_b
    ops.beamIntegration("UserDefined", integ_tag, NUM_IP,
                        *sec_tags, *xips, *liprs)


def define_elements() -> None:
    """Lateral-system elements: south/north frame columns + beams, Y-direction
    tie beams (stories 4 & 5), walls, and diagonal corotTruss braces."""
    integ_counter = 1
    for s in range(NUM_STORIES):
        # ---- south frame columns (group 100) ----
        for c in range(NUM_BAYS_X + 1):
            n1 = _nd(s, 100, c); n2 = _nd(s + 1, 100, c)
            transf = _col_transf(s, 100000, c)
            _user_defined_integration(integ_counter, s, 200, "col")
            ops.element("forceBeamColumn", s * 1000 + 100 + c * 10,
                        n1, n2, transf, integ_counter)
            integ_counter += 1
        # ---- south frame beams (group 200) ----
        for b in range(NUM_BAYS_X):
            n1 = _nd(s + 1, 100, b); n2 = _nd(s + 1, 100, b + 1)
            transf = _beam_transf(s, 100000, b)
            sec_base = 100 if b > 0 else 400   # first bay = slab section
            _user_defined_integration(integ_counter, s, sec_base, "beam")
            ops.element("forceBeamColumn", s * 1000 + 200 + b * 10,
                        n1, n2, transf, integ_counter)
            integ_counter += 1
        # ---- north frame columns (group 300) ----
        for c in range(NUM_BAYS_X + 1):
            n1 = _nd(s, 200, c); n2 = _nd(s + 1, 200, c)
            transf = _col_transf(s, 200000, c)
            _user_defined_integration(integ_counter, s, 200, "col")
            ops.element("forceBeamColumn", s * 1000 + 300 + c * 10,
                        n1, n2, transf, integ_counter)
            integ_counter += 1
        # ---- north frame beams (group 400) ----
        for b in range(NUM_BAYS_X):
            n1 = _nd(s + 1, 200, b); n2 = _nd(s + 1, 200, b + 1)
            transf = _beam_transf(s, 200000, b)
            sec_base = 100 if b > 0 else 400
            _user_defined_integration(integ_counter, s, sec_base, "beam")
            ops.element("forceBeamColumn", s * 1000 + 400 + b * 10,
                        n1, n2, transf, integ_counter)
            integ_counter += 1
        # ---- Y-direction tie beams (stories 4 & 5; story_id > 2) ----
        if s > 2:
            n1 = _nd(s + 1, 100, NUM_BAYS_X); n2 = _nd(s + 1, 200, NUM_BAYS_X)
            tag = 300000 + s * 100 + 9
            ops.geomTransf("PDelta", tag, 1.0, 0.0, 0.0)
            _user_defined_integration(integ_counter, s, 100, "beam")
            ops.element("forceBeamColumn", s * 1000 + 900,
                        n1, n2, tag, integ_counter)
            integ_counter += 1
        # ---- walls (group 500) ----
        for w in range(NUM_WALLS):
            n1 = _nd(s, 500, w); n2 = _nd(s + 1, 500, w)
            tag = 300000 + s * 100 + w
            ops.geomTransf("PDelta", tag, 1.0, 0.0, 0.0)
            _user_defined_integration(integ_counter, s, 300, "col")
            ops.element("forceBeamColumn", s * 1000 + 500 + w * 10,
                        n1, n2, tag, integ_counter)
            integ_counter += 1

    # ---- diagonal braces (corotTruss) south<->north corners ----
    a_brace = 0.25 * 3.14 * 1.25 ** 2 * inch ** 2
    for s in range(NUM_STORIES):
        # brace 1: south-top-of-story -> north-bottom-of-next
        ops.element("corotTruss", 9000 + s * 100 + 1,
                    _nd(s, 100, NUM_BAYS_X), _nd(s + 1, 200, NUM_BAYS_X),
                    a_brace, MAT_BRACE)
        # brace 2: north-top -> south-bottom (crossing)
        ops.element("corotTruss", 9000 + s * 100 + 2,
                    _nd(s, 200, NUM_BAYS_X), _nd(s + 1, 100, NUM_BAYS_X),
                    a_brace, MAT_BRACE)


# ── 11. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB. set_odb_path MUST precede CreateODB (§12ac).

    save_frame_resp=False: forceBeamColumn fiber sections + corotTruss braces
    are not collected frame-by-frame (§12ai — corotTruss in frame_tags crashes
    the basic-force extractor). Nodal responses suffice for the deformed-shape
    plots and roof drift.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        save_nodal_resp=True,
        save_frame_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 12. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    """Gravity pattern 1 (Constant): per-node vertical point loads (DOF3) by
    tributary fraction of W_story. Source maps node groups -> pr_i fractions."""
    ops.timeSeries("Constant", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    # node-group -> gravity-fraction index into PR (source §gravity loads)
    #   p1=0.18, p2=0.12, p3=0.12, p4=0.12, p5=0.12
    node_frac = [
        (100, 1), (110, 3), (120, 4),    # south frame: p2,p4,p5
        (200, 4), (210, 1), (220, 0),    # north frame: p5,p2,p1
        (500, 4), (510, 2),              # walls: p5,p3
    ]
    for f in range(1, NUM_STORIES + 1):
        w = W_STORY[f - 1]
        for grp, pi in node_frac:
            load = w * PR[pi] * kip
            ops.load(_nd(f, grp), 0.0, 0.0, -load, 0.0, 0.0, 0.0)


def define_recorders(output_dir: Path) -> None:
    """Plain recorders for story drift (ctrl nodes DOF1) and roof X-disp."""
    dyn = output_dir / "DynamicOutput"
    dyn.mkdir(parents=True, exist_ok=True)
    # roof / story X-displacement of diaphragm masters
    nodes = " ".join(str(n) for n in CTRL_NODES)
    ops.recorder("Node", "-file", str(dyn / "story_disp.out"),
                 "-time", "-node", *CTRL_NODES, "-dof", 1, "disp")


# ── 13. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(odb) -> bool:
    """Gravity: LoadControl 10 steps (source), Transformation constraints for
    the rigidDiaphragm MP constraints, BandGeneral, Newton. Then loadConst.
    """
    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-6, 25, 3)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.1)
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


def run_eigen(n_modes: int = 6) -> list:
    """Eigen analysis; print periods and set up Rayleigh damping (modes 1&3)."""
    eigs = ops.eigen(n_modes)
    periods = [2.0 * math.pi / math.sqrt(l) for l in eigs]
    for i, t in enumerate(periods, 1):
        print(f"  T{i} = {t:.4f} s")
    w1 = math.sqrt(eigs[0])
    w3 = math.sqrt(eigs[2])
    alphaM = XDAMP * (2.0 * w1 * w3) / (w1 + w3)
    betaK = 2.0 * XDAMP / (w1 + w3)
    ops.rayleigh(alphaM, 0.0, betaK, 0.0)
    print(f"  Rayleigh damping set: alphaM={alphaM:.3e}, betaK={betaK:.3e}")
    return periods


def run_dynamic(odb, output_dir: Path, odb_every_n: int = ODB_EVERY_N) -> bool:
    """Transient time-history under the X-direction ground motion.

    GM is defined here (after loadConst, §12i) via UniformExcitation dir 1.
    Source uses Transformation + SparseGEN + Newmark with adaptive dt/tol
    recovery; reproduced as Transformation + BandGeneral + Newmark via
    opst.anlys.SmartAnalyze (Transient) with the repo-convention retry settings.
    """
    gm_path = Path(__file__).parent / "ground_motions" / GM_FILE
    ops.timeSeries("Path", TS_GM, "-dt", GM_DT, "-filePath", str(gm_path),
                   "-factor", GM_FACTOR)
    ops.pattern("UniformExcitation", PAT_GM, GM_DIR, "-accel", TS_GM)

    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("Newmark", 0.5, 0.25)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )
    segs = analysis.transient_split(GM_NPTS)
    t_current = 0.0
    step_count = 0
    for i, _ in enumerate(segs):
        ok = analysis.TransientAnalyze(GM_DT)
        if ok < 0:
            print(f"  Dynamic: failed at t = {t_current:.3f} s (step {i})")
            break
        t_current += GM_DT
        step_count += 1
        if i % odb_every_n == 0:
            odb.fetch_response_step()
        if (i + 1) % 500 == 0:
            rx = ops.nodeDisp(CTRL_NODES[-1], 1)
            print(f"  dynamic step {i + 1}/{GM_NPTS}  t={t_current:.2f}s "
                  f"roof_X={rx:.2f} mm")
    if step_count % odb_every_n != 0:
        odb.fetch_response_step()
    analysis.close()
    print(f"  Dynamic: {step_count}/{GM_NPTS} steps completed "
          f"(t_final = {t_current:.3f} s).")
    return step_count == GM_NPTS


# ── 14. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb, output_dir: Path) -> None:
    """Flush ODB, render deformed-shape HTML, and note the drift output."""
    odb.save_response()
    print("  ODB saved.")

    try:
        vis_defo(output_dir, filename="vis_05_peak_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UX", resp_type="disp", scale=50.0)
        print("  -> vis_05_peak_deformed.html")
    except Exception as e:
        print(f"  Skipped peak plot: {e}")
    try:
        # step slider — scrub through the collected ODB frames
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UX", resp_type="disp", scale=50.0)
        print("  -> vis_06_slider.html")
    except Exception as e:
        print(f"  Skipped slider plot: {e}")

    dyn = output_dir / "DynamicOutput"
    print(f"  Story drift data: {dyn / 'story_disp.out'} (ctrl nodes, DOF1).")


# ── 15. MAIN ─────────────────────────────────────────────────────────────────
def run_analysis(output_dir: Path):
    """Build the model, run gravity + eigen + dynamic. Returns odb."""
    output_dir.mkdir(parents=True, exist_ok=True)

    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    define_rigid_diaphragms()
    vis_nodes(output_dir)                       # V1
    define_elements()
    vis_model(output_dir)                       # V2
    odb = create_odb(output_dir)
    define_gravity_loads()
    vis_loads(output_dir)                       # V3
    vis_pre_analysis(output_dir)                # V4

    print("=== Gravity ===")
    if not run_gravity(odb):
        print("Gravity failed — aborting.")
        return odb

    print("=== Eigen ===")
    run_eigen(6)

    print("=== Dynamic ===")
    define_recorders(output_dir)
    run_dynamic(odb, output_dir)
    return odb


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print("\n=== Complete ===")
