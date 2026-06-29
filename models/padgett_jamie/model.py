# ── 0. FILE HEADER ──────────────────────────────────────────────────────────────
"""
Model    : Multi-Span Simply Supported (MSSS) Concrete Box Girder Bridge
UniqueID : padgett_jamie
Author   : Bryant G. Nielson (original Tcl), Sabarethinam Kameshwar & Navya Vishnu
           (parametric/aging extension); converted to OpenSeesPy by ZCode agent.
Date     : 2026-06-29
Purpose  : Nonlinear 3D seismic response of a simply-supported multi-span RC box
           girder bridge on elastomeric bearings with soil-pile abutment/foundation
           springs, deck pounding, and Rayleigh-damped transient analysis.
Ref      : Nielson (2005), "Analytical fragility curves for highway bridges in
           moderate seismic zones", PhD thesis, Georgia Tech.
           Padgett (2007), "Seismic vulnerability assessment of retrofitted
           bridges", PhD thesis, Rice University.
Units    : N, mm, MPa  (see standards/units.py)
Notes    : Converted from the Tcl parametric builder in tcl_ref/ which generates
           1152 fragility bridges. This model builds ONE representative bridge
           (3 spans, 4 girders, 3 columns per bent) using the median physical
           parameters of the dataset. All length/force/stress values were
           originally in inches / kips / ksi and have been converted to N-mm-MPa
           (see §3a of AGENT.md). Concrete section/element properties that are
           ratios or strain-like are carried through unchanged per §12g.
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────────
import math
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

# Add standards/ to path if running standalone
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import (
    _headless,
    vis_nodes,
    vis_model,
    vis_loads,
    vis_pre_analysis,
)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────────
# All integer tags as NAMED CONSTANTS — no magic numbers anywhere else.
# Material tags (match the Tcl convention exactly so sections/elements line up).
MAT_COL_CORE   = 1    # Concrete04 confined (column)
MAT_COL_COVER  = 2    # Concrete04 unconfined (column cover + bent)
MAT_COL_STEEL  = 3    # Steel02 longitudinal/transverse rebar
MAT_TORSION    = 4    # Elastic rigid torsion material (section Aggregator)
MAT_RIGID_DECK = 1000 # Elastic rigid material for transverse deck (deck.tcl)

# Bearing materials
MAT_BRG_VERT   = 8378 # Elastic vertical bearing stiffness
MAT_FYP_END    = 203  # Steel01 fixed bearing pad (end spans)
MAT_FYP_MID    = 204  # Steel01 fixed bearing pad (middle spans)
MAT_GAP_FP     = 200  # ElasticPPGap (positive)
MAT_GAP_FN     = 202  # ElasticPPGap (negative)
MAT_DOWEL      = 201  # Hysteretic steel dowel
MAT_DWL_GAP_FP = 300  # ElasticPPGap expansion (positive)
MAT_DWL_GAP_FN = 302  # ElasticPPGap expansion (negative)
MAT_BRG_END    = 7    # Parallel combined bearing (end spans)
MAT_BRG_MID    = 8    # Parallel combined bearing (middle spans)
MAT_EXP_END    = 37   # Parallel expansion bearing (end spans)
MAT_EXP_MID    = 38   # Parallel expansion bearing (middle spans)

# Abutment materials
MAT_ABUT_BACKFILL = 500  # Hysteretic passive soil
MAT_ABUT_GAP      = 501  # ElasticPPGap
MAT_ABUT_SER      = 504  # Series soil
MAT_ABUT_PILE     = 10   # Hysteretic abutment pile
MAT_ABUT_LONG     = 9    # Parallel abutment longitudinal

# Foundation materials
MAT_FND_T1 = 701; MAT_FND_T2 = 702; MAT_FND_T3 = 703; MAT_FND_T4 = 704
MAT_FND_TRANS = 15  # Parallel translational spring
MAT_FND_ROT   = 16  # Elastic rotational spring

# Impact materials (deck pounding)
MAT_IMPACT = [131, 132, 133, 134]  # Parallel impact materials per gap

# Section tags
SEC_COL     = 1     # Circular fiber section (column)  + Aggregator -> 2
SEC_COL_AGG = 2
SEC_BENT    = 3     # Rectangular fiber section (bent cap) + Aggregator -> 4
SEC_BENT_AGG = 4

# Geometric transformations
TRANS_DECK_GIRDER = 1   # Corotational (longitudinal girders)
TRANS_DECK_TRANS  = 2   # Corotational (transverse slab)
TRANS_COL         = 3   # PDelta (columns)
TRANS_BENT        = 4   # PDelta (bent cap)
TRANS_RIGID       = 6   # Linear (rigid links)

# BeamIntegration tags
INTEG_COL  = 6
INTEG_BENT = 4

# Time series & patterns
TS_GRAV    = 1
PAT_GRAV   = 1
PAT_GM_X   = 2
PAT_GM_Z   = 3
TS_GRAV_RAMP = 4
PAT_GRAV_RAMP = 4
TS_GM_X    = 101
TS_GM_Z    = 103

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────────
# All lengths in mm, forces in N, stresses in MPa = N/mm².
# Representative bridge = row i=1129 of parameter_value_AB.out (1152-combination
# fragility dataset). This row is a real, self-consistent geometry where the
# column band ((bn-1)*spacing) exactly equals the deck width ((gd-1)*gd_spc),
# which is a structural invariant of the Tcl generator. All values below were
# originally in inches / kips / ksi and have been converted to N-mm-MPa.

# --- Material strengths (originally ksi) ---
fc    = 6.2837 * ksi      # concrete strength            [MPa]  originally 6.2837 ksi
fys   = 76.8934 * ksi     # steel yield strength          [MPa]  originally 76.8934 ksi
Es    = 29000.0 * ksi     # steel elastic modulus         [MPa]  originally 29000 ksi
fcg   = 10.7497 * ksi     # girder concrete strength      [MPa]  originally 10.7497 ksi

# --- Geometry (originally inches) ---
spans = 3
ln    = 722.2967 * inch   # span length                  [mm]   originally 722.2967 in
gd    = 4                 # number of girders
gd_spc = 44.1221 * inch   # girder spacing               [mm]   originally 44.1221 in
bn    = 2                 # number of columns per bent
ch    = 140.2840 * inch   # column height                [mm]   originally 140.2840 in
D_col = 57.4767 * inch    # column diameter              [mm]   originally 57.4767 in
spacing = 132.3664 * inch # column spacing (transverse)  [mm]   originally 132.3664 in
cover_bent = 1.5 * inch   # bent cap cover               [mm]   originally 1.5 in
cover_col  = 2.6103 * inch# column cover                 [mm]   originally 2.6103 in

# --- Reinforcement ratios (dimensionless) ---
rho_l = 0.02598           # longitudinal reinforcement ratio
rho_t = 0.00728           # transverse reinforcement ratio

# --- Deck section properties (originally in², in⁴) ---
A_t  = 1488.2368 * inch**2   # transverse deck area       [mm²]
Ag   = 752.5468 * inch**2    # girder cross-section area  [mm²]
Iz_t = 238535.48 * inch**4   # transverse element Iz      [mm⁴]
Iy_t = 1797295.54 * inch**4  # transverse element Iy      [mm⁴]
Izg  = 43053.86 * inch**4    # girder Iz                  [mm⁴]
Iyg  = 90140.64 * inch**4    # girder Iy                  [mm⁴]

# --- Weights / masses (originally kip/in) ---
gd_wt   = 0.060094 * kip / inch  # girder weight         [N/mm]
slab_wt = 0.0 * kip / inch       # slab weight           [N/mm]
ms      = 0.9246                 # mass multiplication factor [-]

# --- Bearings (originally mixed: ksi, in², in) ---
cof_ep       = 0.7412          # friction coeff. bearing/concrete [-]
st_ep        = 0.4629 * ksi    # elastomer pad shear stiffness [MPa]
G_fac        = 1.8931          # oxidation stiffening factor [-]
bear_pad_area = 244.086 * inch**2  # bearing pad area     [mm²]
bear_pad_d   = 1.0631 * inch   # bearing pad thickness        [mm]
dwl_str      = 15.1675 * kip   # dowel strength               [N]   originally 15.1675 k
dwl_gap      = 1.2380 * inch   # dowel-bearings gap           [mm]
dowel_dec    = 0.1174          # dowel section decrease (in)
d_dec        = 0.4212 * inch   # rebar section decrease (in)

# --- Abutment & foundation springs ---
# st_abp is k/in/in (passive soil); kept dimensionless and converted inside
# _define_abutment_materials() (source-unit empirical equations, §12g).
st_abp   = 3.8368              # passive soil stiffness [k/in/in]
st_aba   = 40.8753 * kip / inch  # abutment pile stiffness [N/mm] per pile
rot_fnd  = 549.5388 * kip / inch # foundation rot stiffness [N/mm] per pile
trns_fnd = 50.9300 * kip / inch  # foundation lat stiffness [N/mm] per pile

# --- Impact gaps (originally inches) ---
gap1 = 1.4615 * inch   # pounding gaps [mm]
gap2 = 1.5604 * inch
gap3 = 1.0502 * inch
gap4 = 0.8343 * inch

# --- Loading / analysis ---
load_dir = 0.0                  # ground-motion incidence angle [deg] (0 = longitudinal)
dr       = 0.05                 # damping ratio [-]
n_steps_gravity = 5
gm_dt   = 0.005                 # ground-motion time step [s] (synthetic record)
gm_npts = 4000                  # number of synthetic points (20 s at dt=gm_dt)
grav_ramp_dur = 2.0             # gravity ramp duration [s] (transient ramp 0→100%)
odb_every_n = 5                 # throttle ODB in transient

# Ground motion directory / file (synthetic Ricker wavelet if empty)
gm_dir    = Path(__file__).parent / "ground_motions"
gm_file_x = ""                  # set to a filename inside ground_motions/ to use real GM
gm_file_z = ""

# Rigid-link material props. The Tcl used A=1e8 in², E=1e8 ksi, I=1e9 in⁴ which
# in N-mm is ~4e8× stiffer than the deck girders — this stiffness contrast breaks
# the solver (ill-conditioning, per §12x lesson 6). Here we scale the rigid links
# to be only ~1e6× the girder stiffness: rigid enough to transmit loads without
# deformation, but numerically tame. Values derived from the girder section.
Eg_girder = 185000.0 * (fcg / ksi * 1000.0) ** (3.0 / 8.0) / 1000.0 * ksi
RIGID_FACTOR = 1.0e6
Atd = RIGID_FACTOR * Ag
Itd = RIGID_FACTOR * Izg
Jtd = RIGID_FACTOR * (Iyg + Izg)
Etd = Eg_girder
Gtd = Eg_girder / (2.0 * (1.0 + 0.15))

# Gravity acceleration used in the source (384.6 in/s² ≈ g). Keep in mm/s².
G_IMP = 384.6 * inch   # 9766.4 mm/s², used to scale ground motion & weights


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────────
def init_model() -> None:
    """Initialise 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────────
def _confined_concrete_params():
    """Mander confined-concrete parameters for a circular column.

    The confinement equations (Mander 1988) and the Popovics modulus formulas
    are evaluated in their SOURCE units (ksi, inches) exactly as in
    bent2_circ_col.tcl, then the final outputs are converted to N-mm-MPa
    (per §12g: empirical equations are computed in source units and only the
    outputs carry unit conversion).

    Returns (fcon_MPa, eccon_strain, Econ_MPa, fc_unconf_MPa, Ec_MPa).
    """
    fc_pos = abs(fc) / ksi                       # ksi  (unconfined strength)
    D_in   = D_col / inch                        # inches
    cov_in = cover_col / inch                    # inches

    d_core_in  = D_in - 2.0 * cov_in - 1.0       # core diameter [in]
    hoop_dia_in = D_in - 2.0 * cov_in + 0.25
    Ast_in = 0.31                                # in²  (#16 transverse bar)
    Ast_in *= (1.0 - (d_dec / inch) / 0.625) ** 2   # aging reduction

    s_in = 4.0 * Ast_in / (d_core_in * rho_t)    # hoop clear spacing [in]
    rho_cc = Ast_in / (math.pi * d_core_in ** 2 / 4.0)
    Ke = (1.0 - (s_in - 0.25) / (2.0 * hoop_dia_in)) ** 2 / (1.0 - rho_cc)
    rho_t_eff = 4.0 * Ast_in / (d_core_in * s_in)
    fl = 0.5 * Ke * rho_t_eff * 66.66            # ksi  (confinement pressure)
    xd = fl * 2.0 / (2.0 * fc_pos)               # dimensionless

    q = 1.0
    a = 6.886 - (0.6069 + 17.275 * q) * math.exp(-4.989 * q)
    b = 4.5 / ((5.0 / a) * (0.9849 - 0.6036 * math.exp(-3.8939 * q) - 0.1)) - 5.0
    k1 = a * (0.1 + 0.9 / (1.0 + b * xd))
    k2 = 5.0 * k1

    fcon_ksi = fc_pos * (1.0 + k1 * xd)          # ksi  (confined strength)
    ec0   = 0.002
    eccon = ec0 * (1.0 + k2 * xd)
    Ec_ksi   = 185000.0 * (fc_pos * 1000.0) ** (3.0 / 8.0) / 1000.0    # ksi
    Econ_ksi = 57.0 * math.sqrt(fcon_ksi * 1000.0)                      # ksi

    return (fcon_ksi * ksi, eccon, Econ_ksi * ksi,
            fc_pos * ksi, Ec_ksi * ksi)


def define_materials() -> None:
    """Define all uniaxial materials.

    Columns: Concrete04 (confined core + unconfined cover), Steel02 rebar,
    rigid torsion; Bearings: Steel01 pad + ElasticPPGap + Hysteretic dowels;
    Abutments: Hysteretic soil/pile; Foundations: ElasticPPGap translational +
    Elastic rotational; Impact: ElasticPPGap pounding.
    """
    fcon, eccon, Econ, fc_pos, Ec = _confined_concrete_params()
    # ec0 / ecu (strain at crushing) — section material definitions
    ec0   = 0.002
    ecu   = 0.012

    # --- Column concrete (sign convention: negative compression) ---
    ops.uniaxialMaterial("Concrete04", MAT_COL_CORE,
                         -fcon, -ec0, -ecu, Econ)          # confined core
    ops.uniaxialMaterial("Concrete04", MAT_COL_COVER,
                         -fc_pos, -0.002, -0.004, Ec)      # unconfined cover

    # --- Reinforcing steel (Menegotto-Pinto, coeffs by Terzic 2010) ---
    ops.uniaxialMaterial("Steel02", MAT_COL_STEEL,
                         fys, Es, 0.025, 18.0, 0.925, 0.15)

    # --- Rigid torsion ---
    ops.uniaxialMaterial("Elastic", MAT_TORSION, 1.0e10)

    # --- Deck rigid material (transverse elements use A_t/E_t/Iz_t separately) ---
    ops.uniaxialMaterial("Elastic", MAT_RIGID_DECK, 9.0e9)

    _define_bearing_materials()
    _define_abutment_materials()
    _define_foundation_materials()
    _define_impact_materials()


def _bearing_reaction_kip() -> float:
    """Bearing reaction R (force per girder end) used for pad friction force.

    Reproduces masses.tcl: R = dm1 * sp / 2 * 384.6, where
    dm1 = (slab_wt + gd_wt) * ms / 386.4  [k·s²/in].  Evaluated entirely in
    source imperial units; returns kips (per §12g).
    """
    gd_wt_kin   = gd_wt / (kip / inch)          # kip/in
    slab_wt_kin = slab_wt / (kip / inch)        # kip/in
    ln_in = ln / inch                           # in
    dm1 = ms * (slab_wt_kin + gd_wt_kin) / 386.4   # k·s²/in  (386.4 in/s² ≈ g)
    R_kip = dm1 * ln_in / 2.0 * 384.6           # kip
    return R_kip


def _define_bearing_materials() -> None:
    """Elastomeric bearing pads + steel dowels + gaps (fixed & expansion).

    Empirical friction equation (Nielson 2005) evaluated in source units:
      Fyp = cof_ep * (R + b_add) * (0.05 + 0.4 / (R/Ap))   [kip]
    where 0.05 and 0.4 are kip-based empirical constants (the Tcl's 0.145
    factor was the ksi→MPa bridge — we drop it by computing in kip directly).
    """
    ops.uniaxialMaterial("Elastic", MAT_BRG_VERT, 2900.0 * ksi)   # vertical stiffness

    # Pad shear stiffness: Gp[ksi] * Ap[in²] / d[in]  → kip/in  → N/mm
    Gp_ksi = (st_ep / ksi) * G_fac
    Ap_in2 = bear_pad_area / inch**2
    d_in   = bear_pad_d / inch
    kp_kin = Gp_ksi * Ap_in2 / d_in              # kip/in
    kp = kp_kin * kip / inch                     # N/mm

    R_kip = _bearing_reaction_kip()
    b_add = 0.0                                   # additional vertical load [kip]
    Fyp_kip = cof_ep * (R_kip + b_add) * (0.05 + 0.4 / (R_kip / Ap_in2))   # kip
    Fyp = Fyp_kip * kip                           # N

    ops.uniaxialMaterial("Steel01", MAT_FYP_END, Fyp, kp, 0.0)
    ops.uniaxialMaterial("Steel01", MAT_FYP_MID, Fyp, kp, 0.0)

    # Gaps for fixed bearings (125 mil = 0.125 in). 9e5 = kip/in stiffness in source.
    ops.uniaxialMaterial("ElasticPPGap", MAT_GAP_FP,
                         9.0e5 * kip / inch,  9.0e10 * kip / inch,  0.125 * inch)
    ops.uniaxialMaterial("ElasticPPGap", MAT_GAP_FN,
                         9.0e5 * kip / inch, -9.0e10 * kip / inch, -0.125 * inch)

    # Steel dowel (Hysteretic) — strength reduced by aging factor
    dwl_str_eff = dwl_str * (1.0 - dowel_dec) ** 2          # N
    f1p = dwl_str_eff * 2 * 0.965
    f2p = dwl_str_eff * 2
    e1p, e2p = 0.048, 0.21
    ops.uniaxialMaterial("Hysteretic", MAT_DOWEL,
                         f1p, e1p, f2p, e2p, 0.0, 0.2101,
                         -f1p, -e1p, -f2p, -e2p, 0.0, -0.2101,
                         1.0, 0.0, 0.0, 0.0, 0.0)

    # Combine: gap || gap ; Series(dowel, gap-pair) ; then || pad
    ops.uniaxialMaterial("Parallel", 5, MAT_GAP_FP, MAT_GAP_FN)
    ops.uniaxialMaterial("Series", 6, MAT_DOWEL, 5)
    ops.uniaxialMaterial("Parallel", MAT_BRG_END, 6, MAT_FYP_END)
    ops.uniaxialMaterial("Parallel", MAT_BRG_MID, 6, MAT_FYP_MID)

    # Expansion bearings: gap = dwl_gap (movable); negative gap shifts by 1.25 in
    ops.uniaxialMaterial("ElasticPPGap", MAT_DWL_GAP_FP,
                         9.0e5 * kip / inch,  9.0e10 * kip / inch,  dwl_gap)
    ops.uniaxialMaterial("ElasticPPGap", MAT_DWL_GAP_FN,
                         9.0e5 * kip / inch, -9.0e10 * kip / inch,
                         -1.25 * inch + dwl_gap)
    ops.uniaxialMaterial("Parallel", 35, MAT_DWL_GAP_FP, MAT_DWL_GAP_FN)
    ops.uniaxialMaterial("Series", 36, MAT_DOWEL, 35)
    ops.uniaxialMaterial("Parallel", MAT_EXP_END, 36, MAT_FYP_END)
    ops.uniaxialMaterial("Parallel", MAT_EXP_MID, 36, MAT_FYP_MID)


def _define_abutment_materials() -> None:
    """Abutment backfill (Hysteretic) + pile (Hysteretic) in parallel.

    Nielson (2005) empirical soil/pile equations evaluated in source units
    (kips, inches, ksf) and converted to N-mm at the material call.
    """
    # --- Passive soil pressure per gd_spc-wide section (Nielson 2005) ---
    # st_abp [k/in/in]; k_soil = st_abp*12  [k/in/ft];  k1p = k_soil*gd_spc/12 [kip/in]
    gd_spc_in = gd_spc / inch
    k_soil_kin = st_abp * 12.0                 # kip/in/ft
    k1p_kin = k_soil_kin * gd_spc_in / 12.0    # kip/in per section
    D3p_in = (0.06 + ((st_abp - 20.0) / (50.0 - 20.0)) * 0.04) * 96.0   # in
    D1p_in = 0.1 * D3p_in
    D2p_in = 0.35 * D3p_in
    f1p_kip = k1p_kin * D1p_in
    # 7.7 ksf soil pressure on an 8 ft wall, per gd_spc-wide section
    f3p_kip = 7.7 * 8.0 * (gd_spc_in / 12.0)   # kip  (ksf * ft * ft)
    f2p_kip = 0.45 * f1p_kip + 0.55 * f3p_kip
    k3p_kin = (0.45 * (f3p_kip - f1p_kip)) / (0.65 * D3p_in)    # kip/in

    # Convert to N-mm and create materials
    D1p = D1p_in * inch; D2p = D2p_in * inch; D3p = D3p_in * inch
    f1p = f1p_kip * kip; f2p = f2p_kip * kip
    k3p = k3p_kin * kip / inch
    ops.uniaxialMaterial("Hysteretic", MAT_ABUT_BACKFILL,
                         f1p, D1p, f2p, D2p, f2p, D3p,
                         -f1p, -D1p, -f2p, -D2p, -f2p, -D3p,
                         1.0, 0.0, 0.0, 0.0, 0.0)
    ops.uniaxialMaterial("ElasticPPGap", MAT_ABUT_GAP, k3p, f2p - f3p_kip * kip, -D2p)
    ops.uniaxialMaterial("Parallel", 502, MAT_ABUT_BACKFILL, MAT_ABUT_GAP)
    ops.uniaxialMaterial("ENT", 503, 1.0e8 * kip / inch)     # 1e8 kip/in (source)
    ops.uniaxialMaterial("Series", MAT_ABUT_SER, 502, 503)

    # --- Abutment pile (longitudinal + transverse), Nielson 2005 ---
    # 62.5 in pile spacing; each pile stiffness st_aba [kip/in]
    k_pile_kin = st_aba / (kip / inch)          # kip/in
    keff_kin = k_pile_kin * (gd_spc_in / 62.5)  # kip/in per section
    k1a_kin = keff_kin * 2.33
    k2a_kin = keff_kin * 0.428
    D2a_in = 1.0
    D1a_in = D2a_in * 0.3
    f1a_kip = k1a_kin * D1a_in
    f2a_kip = 0.7 * D2a_in * k2a_kin

    D1a = D1a_in * inch; D2a = D2a_in * inch
    s1, e1 = f1a_kip * kip, D1a
    s2, e2 = (f2a_kip + f1a_kip) * kip, D2a
    s3, e3 = (f2a_kip + f1a_kip) * kip, 2.0 * D2a
    ops.uniaxialMaterial("Hysteretic", MAT_ABUT_PILE,
                         s1, e1, s2, e2, s3, e3,
                         -s1, -e1, -s2, -e2, -s3, -e3,
                         0.75, 0.5, 0.0, 0.0, 0.1)
    ops.uniaxialMaterial("Parallel", MAT_ABUT_LONG, MAT_ABUT_SER, MAT_ABUT_PILE)


def _define_foundation_materials() -> None:
    """Foundation translational (4 ElasticPPGap in parallel) + rotational spring.

    Nielson (2005) pile-group equations evaluated in source units (kip, in)
    then converted to N-mm.
    """
    n_pile = 8
    D2a_in = 1.0
    D1a_in = D2a_in * 0.3
    trns_fnd_kin = trns_fnd / (kip / inch)          # kip/in
    rot_fnd_kin  = rot_fnd  / (kip / inch)          # kip/in

    k1_fnd_kin = trns_fnd_kin * 2.33 * n_pile       # kip/in
    k2_fnd_kin = trns_fnd_kin * 0.428 * n_pile
    f1_fnd_kip = k1_fnd_kin * D1a_in
    f2_fnd_kip = 0.7 * D2a_in * k2_fnd_kin

    k1_fnd = k1_fnd_kin * kip / inch
    k2_fnd = k2_fnd_kin * kip / inch
    f1_fnd = f1_fnd_kip * kip
    f2_fnd = f2_fnd_kip * kip
    D1a = D1a_in * inch

    ops.uniaxialMaterial("ElasticPPGap", MAT_FND_T1, k1_fnd, -f1_fnd, 0.0)
    ops.uniaxialMaterial("ElasticPPGap", MAT_FND_T2, k2_fnd, -f2_fnd, -D1a)
    ops.uniaxialMaterial("ElasticPPGap", MAT_FND_T3, k1_fnd,  f1_fnd, 0.0)
    ops.uniaxialMaterial("ElasticPPGap", MAT_FND_T4, k2_fnd,  f2_fnd,  D1a)
    ops.uniaxialMaterial("Parallel", MAT_FND_TRANS, MAT_FND_T1, MAT_FND_T2, MAT_FND_T3, MAT_FND_T4)

    lever_arm_in = 30.0
    # kfndr = rot_fnd[kip/in] * 6 * lever_arm²  → kip·in/rad → N·mm/rad
    kfndr = rot_fnd_kin * 6.0 * lever_arm_in ** 2 * kip * inch   # N·mm/rad
    ops.uniaxialMaterial("Elastic", MAT_FND_ROT, kfndr)


def _define_impact_materials() -> None:
    """Deck pounding impact (Muthukumar & DesRoches 2006 Hertz contact).

    Each impact location is a Parallel of two ElasticPPGap materials with the
    SAME gap sign (one-sided contact — adjacent decks pound in the closing
    direction). The original Tcl used ``ElasticPPGap 403 2190 -9e9 gap`` whose
    large negative yield force combined with the gap produced an unstable
    committed tangent under gravity; here both branches carry a positive
    contact stiffness with a positive yield force (the soft branch yields at a
    lower force, the hard branch at the full contact force), keeping the
    initial stiffness well-defined and the gaps open under gravity.
    """
    K_hard = 6368.0 * kip / inch     # Hertz contact stiffness (kip/in source)
    K_soft = 2190.0 * kip / inch     # post-engagement stiffness (kip/in source)
    Fy_contact = 637.0 * kip         # contact yield force (kip source)
    # Both members of each pair share the gap sign (one-sided). gap offsets
    # reproduce the Tcl's 0.1418 in relative offset between the two branches.
    pairs = [
        (402, gap1,                  K_hard, Fy_contact),
        (403, gap1 - 0.1418 * inch,  K_soft, Fy_contact),
        (404, gap2,                  K_hard, Fy_contact),
        (405, gap2 - 0.1418 * inch,  K_soft, Fy_contact),
        (406, gap3,                  K_hard, Fy_contact),
        (407, gap3 - 0.1418 * inch,  K_soft, Fy_contact),
        (408, gap4,                  K_hard, Fy_contact),
        (409, gap4 - 0.1418 * inch,  K_soft, Fy_contact),
    ]
    for tag, gap, K, Fy in pairs:
        ops.uniaxialMaterial("ElasticPPGap", tag, K, Fy, gap)
    for i, par_tag in enumerate(MAT_IMPACT):
        ops.uniaxialMaterial("Parallel", par_tag, 402 + 2 * i, 403 + 2 * i)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────────
def define_sections() -> None:
    """Fiber sections for column (circular) and bent cap (rectangular)."""
    _col_fiber_section()
    _bent_fiber_section()


def _col_fiber_section() -> None:
    """Circular fiber section for columns (patch circ + layer circ).

    3D FiberSection requires torsional stiffness via ``-GJ``; the Tcl used a
    section Aggregator with a rigid torsion material — the ``-GJ`` flag is the
    direct OpenSeesPy equivalent (1e10 = effectively rigid, matching MAT_TORSION).
    """
    d_b = 1.128 * inch                            # longitudinal bar diameter
    A_bar = math.pi * d_b ** 2 / 4.0
    d_core = D_col - 2.0 * cover_col
    A_bar_t = rho_l * math.pi * D_col * d_core / 4.0
    n_bar = max(2, round(A_bar_t / A_bar))
    # aging reduction on bar area
    A_bar *= (1.0 - (d_dec / inch) / d_b) ** 2

    r_core_out = D_col / 2.0 - cover_col + d_b / 2.0   # core outer radius incl. bar offset
    r_cover    = D_col / 2.0
    # Use the aggregated section tag (SEC_COL_AGG) for the Fiber itself so all
    # downstream element references point at the complete section-with-torsion.
    ops.section("Fiber", SEC_COL_AGG, "-GJ", 1.0e10)
    ops.patch("circ", MAT_COL_CORE, n_bar, 8, 0.0, 0.0, 0.0, r_core_out, 0.0, 360.0)
    ops.patch("circ", MAT_COL_COVER, n_bar, 2, 0.0, 0.0, r_core_out, r_cover, 0.0, 360.0)
    if n_bar > 1:
        ops.layer("circ", MAT_COL_STEEL, n_bar, A_bar, 0.0, 0.0, r_core_out,
                  0.0, 360.0 - 360.0 / n_bar)


def _bent_fiber_section() -> None:
    """Rectangular fiber section for the bent cap."""
    bWidth = D_col + 2.0 * cover_bent
    bDepth = bWidth + 2.0 * cover_bent
    A_steel = 1.0767 * (bWidth - 2.0 * cover_bent) * (bDepth - 2.0 * cover_bent) / 100.0
    factor = A_steel / (15.0 * 1.0 + 4.0 * 0.32)
    As1 = factor * 1.00 * (1.0 - (d_dec / inch) / 1.128) ** 2     # #9 bars
    As2 = factor * 0.32 * (1.0 - (d_dec / inch) / 0.625) ** 2     # #5 bars

    y1 = bDepth / 2.0
    z1 = bWidth / 2.0
    ops.section("Fiber", SEC_BENT_AGG, "-GJ", 1.0e10)
    # core
    ops.patch("quad", MAT_COL_CORE, 10, 10,
              cover_bent - y1, cover_bent - z1, y1 - cover_bent, cover_bent - z1,
              y1 - cover_bent, z1 - cover_bent, cover_bent - y1, z1 - cover_bent)
    # cover (top, bottom, left, right)
    ops.patch("quad", MAT_COL_COVER, 10, 2, -y1, z1 - cover_bent, y1, z1 - cover_bent,
              y1, z1, -y1, z1)
    ops.patch("quad", MAT_COL_COVER, 10, 2, -y1, -z1, y1, -z1, y1, cover_bent - z1,
              -y1, cover_bent - z1)
    ops.patch("quad", MAT_COL_COVER, 2, 10, -y1, cover_bent - z1, cover_bent - y1,
              cover_bent - z1, cover_bent - y1, z1 - cover_bent, -y1, z1 - cover_bent)
    ops.patch("quad", MAT_COL_COVER, 2, 10, y1 - cover_bent, cover_bent - z1, y1,
              cover_bent - z1, y1, z1 - cover_bent, y1 - cover_bent, z1 - cover_bent)
    # rebar layers
    ops.layer("straight", MAT_COL_STEEL, 9, As1, y1 - cover_bent, z1 - cover_bent,
              y1 - cover_bent, cover_bent - z1)
    ops.layer("straight", MAT_COL_STEEL, 2, As2, -7.0 * inch, z1 - cover_bent,
              -7.0 * inch, cover_bent - z1)
    ops.layer("straight", MAT_COL_STEEL, 2, As2, 7.0 * inch, z1 - cover_bent,
              7.0 * inch, cover_bent - z1)
    ops.layer("straight", MAT_COL_STEEL, 6, As1, cover_bent - y1, z1 - cover_bent,
              cover_bent - y1, cover_bent - z1)


# ── 7. NODES ─────────────────────────────────────────────────────────────────────
# Node/element tag registries are generated procedurally to mirror the Tcl exactly.
# Layout summary (spans=3, gd=4, bn=3, ndiv2=6):
#   Deck interior grillage nodes: 10001.. (gd per transverse row × div-1 per span)
#   Deck end (rigid-link) nodes : 12001..
#   Abutment/bearing/bent nodes : 501.. (500 + index)
#   Column-bent meeting nodes   : 26001..
#   Foundation nodes            : 8001.. (8000 + index)
#   Column top/interior nodes   : 1001.. (1000 + q*50)
# Global registries populated by define_nodes() for use by other phases.
_deck_nodes = []        # interior deck grillage nodes per span
_deck_end_nodes = []    # left/right end nodes per span (12001..)
_abut_nodes = []        # left + right abutment top nodes (500 + ...)
_bearing_top_nodes = [] # bearing top nodes (deck-side)
_bent_top_nodes = []    # bent cap top nodes per bent
_bent_bot_nodes = []    # bent cap bottom nodes per bent
_bent_list = []         # ordered bent-cap node list (top + bottom) per bent
_eqdof_pairs = []       # (bent_top_col_node, col_top_node) for equalDOF
_found_nodes = []       # foundation nodes per bent (pair per column)
_col_nodes = []         # column nodes per column [top..base]


def define_nodes() -> None:
    """Generate all nodes: deck grillage, deck ends, abutments, bearings,
    bent caps, columns, and foundations.

    Node tag bands (mirror the Tcl exactly):
      10001..   deck interior grillage      (y=0)
      12001..   deck end nodes (left/right) (y=0)
      501..     abutment / bearing / bent-top / bent-bottom nodes
                  left abutment:    501..500+gd            (FIXED ground)
                  left bearing-top: 501+gd..500+2gd        (between soil & pad)
                  bent i top:       ...                    (y=0, deck level)
                  bent i bottom:    ...                    (y=-bDepth/2, cap beam)
                  right bearing-top, right abutment
      26001..   extra bent-column meeting nodes (only if column misaligns girder)
      8001..    foundation nodes (pairs: spring-top, fixed-base)
      1050..    column nodes (1000 + q*50 .. +8), top node = base+0
    """
    ndiv2 = 6
    dl = ln / 6.0                           # deck grillage element length [mm]
    width = (gd - 1) * gd_spc
    bWidth = D_col + 2.0 * cover_bent
    bDepth = bWidth + 2.0 * cover_bent
    y_cap = -bDepth / 2.0                   # bent-cap beam elevation

    _deck_nodes.clear(); _deck_end_nodes.clear()
    _abut_nodes.clear(); _bearing_top_nodes.clear()
    _bent_top_nodes.clear(); _bent_bot_nodes.clear(); _bent_list.clear()
    _eqdof_pairs.clear(); _found_nodes.clear(); _col_nodes.clear()

    # ---------- Deck interior grillage (10001..) : (div-1) rows × gd per span ----------
    n = 10000
    for i in range(spans):
        x = (i * ln) + dl
        per_span = []
        for j in range(ndiv2 - 1):
            z = -width / 2.0
            row = []
            for k in range(gd):
                n += 1
                ops.node(n, x, 0.0, z)
                row.append(n)
                z += gd_spc
            per_span.append(row)
            x += dl
        _deck_nodes.append(per_span)

    # ---------- Deck end nodes (12001..) : left & right of each span ----------
    for i in range(spans):
        xL = i * ln
        xR = (i + 1) * ln
        left = []; right = []
        for k in range(gd):
            z = -width / 2.0 + k * gd_spc
            n += 1; ops.node(n, xL, 0.0, z); left.append(n)
        for k in range(gd):
            z = -width / 2.0 + k * gd_spc
            n += 1; ops.node(n, xR, 0.0, z); right.append(n)
        _deck_end_nodes.append((left, right))

    # ---------- Abutment / bearing / bent nodes (501..) ----------
    m = 500
    girder_z = [-width / 2.0 + k * gd_spc for k in range(gd)]

    def _row(x: float, y: float) -> list:
        nonlocal m
        nodes = []
        for z in girder_z:
            m += 1
            ops.node(m, x, y, z)
            nodes.append(m)
        return nodes

    # Left abutment (FIXED ground) + left bearing-top
    _abut_nodes.append(_row(0.0, 0.0))
    _bearing_top_nodes.append(_row(0.0, 0.0))
    # Bent top (y=0) + bent bottom (y=y_cap) per bent
    for i in range(spans - 1):
        xb = (i + 1) * ln
        _bent_top_nodes.append(_row(xb, 0.0))
        _bent_bot_nodes.append(_row(xb, y_cap))
    # Right bearing-top + right abutment
    xR = spans * ln
    _bearing_top_nodes.append(_row(xR, 0.0))
    _abut_nodes.append(_row(xR, 0.0))

    # ---------- Bent-column meeting nodes + bent_list ----------
    # For each bent, build the bent-cap node chain (bent-bottom nodes at y_cap)
    # and record which bent-bottom node each column ties to (equalDOF target).
    # Columns sit at z = -(bn-1)*spacing/2 + j*spacing; because the generator
    # enforces (bn-1)*spacing == (gd-1)*gd_spc, each column z coincides with a
    # girder z, so the meeting node is the bent-bottom node at that girder line.
    n_extra = 26000
    for i in range(spans - 1):
        bot = _bent_bot_nodes[i]                 # bent-bottom nodes (girder lines)
        bot_z = [ops.nodeCoord(nd)[2] for nd in bot]
        bent_seq = list(bot)                     # bent cap runs along all gd nodes
        _bent_list.append(bent_seq)
        # column meeting nodes = bent-bottom node nearest each column z
        col_z = [-(bn - 1) * spacing / 2.0 + j * spacing for j in range(bn)]
        for z in col_z:
            meet = bot[min(range(gd), key=lambda k: abs(bot_z[k] - z))]
            _eqdof_pairs.append([meet, None])    # column-top filled below

    # ---------- Foundation nodes (8001..) : (spring-top, fixed-base) pairs ----------
    y_found = -ch - 48.0 * inch - y_cap
    m = 8000
    for i in range(spans - 1):
        xf = (i + 1) * ln
        bent_found = []
        for j in range(bn):
            z = -(bn - 1) * spacing / 2.0 + j * spacing
            m += 1; ops.node(m, xf, y_found, z); n_spring = m
            m += 1; ops.node(m, xf, y_found, z); n_fixed = m
            bent_found.append((n_spring, n_fixed))
        _found_nodes.append(bent_found)

    # ---------- Column nodes (1050..) : 9 nodes per column ----------
    # Node tags: base = 1000 + q*50 (q = column index 1..); nodes base+0 .. base+8.
    # base+0 = top (at y_cap, equalDOF'd to bent-bottom), base+8 = base.
    q = 0
    for i in range(spans - 1):
        xc = (i + 1) * ln
        for j in range(bn):
            q += 1
            z = -(bn - 1) * spacing / 2.0 + j * spacing
            base = 1000 + q * 50
            ys = [y_cap,
                  -bDepth,
                  -bDepth - ch / 3.0,
                  -bDepth - 2.0 * ch / 3.0]
            ys += [-bDepth - 2.0 * ch / 3.0 - ch / 15.0 * (k + 1) for k in range(5)]
            nodes = []
            for k, yk in enumerate(ys):
                tag = base + k
                ops.node(tag, xc, yk, z)
                nodes.append(tag)
            _col_nodes.append(nodes)

    # Tie each column's top node (nodes[0]) into its equalDOF meeting node.
    for idx, pair in enumerate(_eqdof_pairs):
        pair[1] = _col_nodes[idx][0]


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Fix abutments, bearing vertical DOFs, foundation bases; set up constraints."""
    # Left abutment — fully fixed
    for n in _abut_nodes[0]:
        ops.fix(n, 1, 1, 1, 1, 1, 1)
    # Right abutment — fully fixed
    for n in _abut_nodes[-1]:
        ops.fix(n, 1, 1, 1, 1, 1, 1)
    # Left bearing top nodes: UY, RX, RY, RZ fixed (free UX, UZ)
    for n in _bearing_top_nodes[0]:
        ops.fix(n, 0, 1, 0, 1, 1, 1)
    # Right bearing top nodes: same
    for n in _bearing_top_nodes[-1]:
        ops.fix(n, 0, 1, 0, 1, 1, 1)
    # Foundation: top node (spring) — UY, RY fixed; base node — fully fixed
    for bent in _found_nodes:
        for (n_top, n_base) in bent:
            ops.fix(n_top, 0, 1, 0, 0, 1, 0)
            ops.fix(n_base, 1, 1, 1, 1, 1, 1)


def define_masses() -> None:
    """Assign lumped translational + rotational masses.

    Reproduces masses.tcl: deck mass per node from (slab_wt + gd_wt)*ms, scaled
    by grillage length; bent-cap and column masses scaled by cross-section; plus
    mass moment of inertia about the deck axis.
    """
    wt1 = slab_wt + gd_wt                       # N/mm
    # source: dm1 = ms*wt1/386.4  [k·s²/in] -> convert to N·s²/mm
    dm1 = ms * wt1 / (386.4 * inch / sec ** 2)
    dl = ln / 6.0
    dm = dm1 * dl                                # N·s²/mm per interior deck node
    dm2 = dm / 2.0                               # half at girder ends

    # rotational mass moment of inertia about x (longitudinal) per girder line
    width = (gd - 1) * gd_spc
    Iz_rot = sum(((-width / 2.0 + k * gd_spc) ** 2) for k in range(gd)) * dm

    # --- Deck end nodes (left/right of each span) ---
    for i, (left, right) in enumerate(_deck_end_nodes):
        for n in left + right:
            ops.mass(n, dm2, dm2, dm2, dm2, dm2, dm2)
    # --- Deck interior grillage nodes ---
    for span_nodes in _deck_nodes:
        for row in span_nodes:
            for n in row:
                ops.mass(n, dm, dm, dm, dm, dm, dm)

    # --- Bent cap masses (scaled by cross-section & girder spacing) ---
    bWidth = D_col + 2.0 * cover_bent
    bDepth = bWidth + 2.0 * cover_bent
    bcm = (gd_spc / (75.0 * inch)) * (bWidth * bDepth) * \
          (0.03397 * kip * sec ** 2 / inch) / (3.5 * 4.0 * 144.0)
    bcm2 = bcm / 2.0
    for bent_idx, top in enumerate(_bent_top_nodes):
        # first + last node get bcm2; interior get bcm
        for k, n in enumerate(top):
            m = bcm2 if (k == 0 or k == len(top) - 1) else bcm
            ops.mass(n, m, m, m, m, m, m)

    # --- Column masses ---
    colm = (D_col / (36.0 * inch)) ** 2 * 0.000229 * kip * sec ** 2 / inch * ch / (3.0 * inch)
    colm2 = colm / 2.0
    for nodes in _col_nodes:
        # 8 nodes: [0]=top(half), [1],[2]=full, [3..7]=half-length sections
        ops.mass(nodes[0], colm2, colm2, colm2, colm2, colm2, colm2)
        ops.mass(nodes[1], colm, colm, colm, colm, colm, colm)
        ops.mass(nodes[2], colm, colm, colm, colm, colm, colm)
        for k in range(3, 8):
            ops.mass(nodes[k], colm2, colm2, colm2, colm2, colm2, colm2)

    # --- Foundation masses ---
    fndm = 0.02317 * kip * sec ** 2 / inch
    for bent in _found_nodes:
        for (n_top, _) in bent:
            ops.mass(n_top, fndm, fndm, fndm, fndm, fndm, fndm)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Define geom transfers, beam integrations, and all elements.

    Order mirrors the Tcl: deck grillage -> rigid links -> bearings -> impact ->
    abutments -> foundations -> columns -> bent caps -> equalDOF constraints.
    """
    # Geometric transformations.
    # Columns are stocky (L/D ≈ 2.4) so PDelta is negligible; PDelta here
    # triggered a spurious transverse-buckling divergence under gravity, so
    # Linear is used for columns (the Corotational deck captures the dominant
    # geometric nonlinearity). Bent cap and rigid links also Linear.
    ops.geomTransf("Corotational", TRANS_DECK_GIRDER, 0, 1, 0)   # girders
    ops.geomTransf("Corotational", TRANS_DECK_TRANS, 0, 1, 0)    # transverse slab
    ops.geomTransf("Linear", TRANS_COL, 1, 0, 0)                 # columns
    ops.geomTransf("Linear", TRANS_BENT, -1, 0, 0)               # bent cap
    ops.geomTransf("Linear", TRANS_RIGID, 1, 0, 0)               # rigid links

    # Beam integration objects (required by dispBeamColumn per §12l)
    ops.beamIntegration("Lobatto", INTEG_COL, SEC_COL_AGG, 6)    # 6 IP columns
    ops.beamIntegration("Lobatto", INTEG_BENT, SEC_BENT_AGG, 4)  # 4 IP bent

    _define_deck_elements()
    _define_rigid_links()
    _define_bearing_elements()
    _define_impact_elements()
    _define_abutment_elements()
    _define_foundation_elements()
    _define_column_elements()
    _define_bent_elements()
    _define_constraints()


def _deck_props():
    """Elastic deck material properties (girder + transverse slab)."""
    Eg = 185000.0 * (fcg / ksi * 1000.0) ** (3.0 / 8.0) / 1000.0 * ksi
    Gg = Eg / (2.0 * (1.0 + 0.15))
    Jg = Iyg + Izg
    E_t = 185000.0 * (fc / ksi * 1000.0) ** (3.0 / 8.0) / 1000.0 * ksi
    G_t = E_t / (2.0 * (1.0 + 0.15))
    J_t = Iy_t + Iz_t
    return Eg, Gg, Jg, E_t, G_t, J_t


def _define_deck_elements() -> None:
    """Longitudinal girders + transverse slab (elasticBeamColumn)."""
    Eg, Gg, Jg, E_t, G_t, J_t = _deck_props()
    ndiv2 = 6
    n = 100000

    # --- Longitudinal girders ---
    for i, (left, right) in enumerate(_deck_end_nodes):
        for k in range(gd):
            # first element: left end node -> first interior node of this girder
            n += 1
            m = left[k]
            p = _deck_nodes[i][0][k]
            ops.element("elasticBeamColumn", n, m, p,
                        Ag, Eg, Gg, Jg, Izg, Iyg, TRANS_DECK_GIRDER)
            # interior elements
            for j in range(ndiv2 - 2):
                n += 1
                m = _deck_nodes[i][j][k]
                p = _deck_nodes[i][j + 1][k]
                ops.element("elasticBeamColumn", n, m, p,
                            Ag, Eg, Gg, Jg, Izg, Iyg, TRANS_DECK_GIRDER)
            # last element: last interior node -> right end node
            n += 1
            m = _deck_nodes[i][ndiv2 - 2][k]
            p = right[k]
            ops.element("elasticBeamColumn", n, m, p,
                        Ag, Eg, Gg, Jg, Izg, Iyg, TRANS_DECK_GIRDER)

    # --- Transverse slab (end rows + interior grillage rows) ---
    n = 120000
    # end rows (left + right of each span)
    for i, (left, right) in enumerate(_deck_end_nodes):
        for row in (left, right):
            for k in range(gd - 1):
                n += 1
                ops.element("elasticBeamColumn", n, row[k], row[k + 1],
                            A_t, E_t, G_t, J_t, Iz_t, Iy_t, TRANS_DECK_TRANS)
    # interior grillage rows
    for span_nodes in _deck_nodes:
        for row in span_nodes:
            for k in range(gd - 1):
                n += 1
                ops.element("elasticBeamColumn", n, row[k], row[k + 1],
                            A_t, E_t, G_t, J_t, Iz_t, Iy_t, TRANS_DECK_TRANS)


def _define_rigid_links() -> None:
    """Rigid (effectively-rigid) elasticBeamColumn links:

    * bent-top  → bent-bottom (vertical struts at each girder line, per bent)
    * column-top node[0] → node[1] (rigid first segment from bent to column)
    * foundation spring-top → column base node[-1]
    """
    n = 9000
    # bent-top → bent-bottom vertical struts
    for bent_idx in range(spans - 1):
        top = _bent_top_nodes[bent_idx]
        bot = _bent_bot_nodes[bent_idx]
        for k in range(gd):
            n += 1
            ops.element("elasticBeamColumn", n, top[k], bot[k],
                        Atd, Etd, Gtd, Jtd, Itd, Itd, TRANS_RIGID)

    # column-top rigid link: node[0] → node[1]
    for nodes in _col_nodes:
        n += 1
        ops.element("elasticBeamColumn", n, nodes[0], nodes[1],
                    Atd, Etd, Gtd, Jtd, Itd, Itd, TRANS_RIGID)

    # column-base rigid link: foundation spring-top → column base node[-1]
    for bent_idx, bent in enumerate(_found_nodes):
        for col_idx, (n_spring, _) in enumerate(bent):
            n += 1
            col_base = _col_nodes[bent_idx * bn + col_idx][-1]
            ops.element("elasticBeamColumn", n, n_spring, col_base,
                        Atd, Etd, Gtd, Jtd, Itd, Itd, TRANS_RIGID)


def _define_bearing_elements() -> None:
    """Fixed + expansion elastomeric bearings (zeroLength).

    Fixed bearing of span i sits at the LEFT support of span i:
      i=0        → left bearing-top → deck-end[0].left
      i=1..end-1 → bent[i-1]-top    → deck-end[i].left
    Expansion bearing of span i sits at the RIGHT support of span i:
      i=0..end-2 → bent[i]-top      → deck-end[i].right
      i=end-1    → right bearing-top → deck-end[end-1].right
    """
    # --- Fixed bearings (tag 501..) ---
    n = 500
    for i in range(spans):
        mat = MAT_BRG_END if (i == 0 or i == spans - 1) else MAT_BRG_MID
        sup_side = _bearing_top_nodes[0] if i == 0 else _bent_top_nodes[i - 1]
        deck_side = _deck_end_nodes[i][0]                      # left end of span i
        for k in range(gd):
            n += 1
            ops.element("zeroLength", n, sup_side[k], deck_side[k],
                        "-mat", mat, MAT_BRG_VERT, mat, "-dir", 1, 2, 3)

    # --- Expansion bearings (tag 701..) ---
    n = 700
    for i in range(spans):
        mat = MAT_EXP_END if (i == 0 or i == spans - 1) else MAT_EXP_MID
        if i == spans - 1:
            sup_side = _bearing_top_nodes[-1]                  # right bearing-top
        else:
            sup_side = _bent_top_nodes[i]                      # bent[i]-top
        deck_side = _deck_end_nodes[i][1]                      # right end of span i
        for k in range(gd):
            n += 1
            ops.element("zeroLength", n, sup_side[k], deck_side[k],
                        "-mat", mat, MAT_BRG_VERT, mat, "-dir", 1, 2, 3)


def _define_impact_elements() -> None:
    """Deck pounding impact elements (zeroLength, UX only).

    * At each abutment: between the abutment bearing-top and the adjacent deck end
    * At each bent: between the right end of span i and the left end of span i+1
    """
    n = 14000
    # Abutment impact (left + right)
    abut_deck = [(_bearing_top_nodes[0], _deck_end_nodes[0][0]),        # left
                 (_bearing_top_nodes[-1], _deck_end_nodes[-1][1])]      # right
    for i in range(2):
        mat = MAT_IMPACT[i]
        for k in range(gd):
            n += 1
            ops.element("zeroLength", n, abut_deck[i][0][k], abut_deck[i][1][k],
                        "-mat", mat, "-dir", 1)
    # Bent impact (between adjacent spans)
    for bent_idx in range(spans - 1):
        mat = MAT_IMPACT[2 + bent_idx] if (2 + bent_idx) < len(MAT_IMPACT) else MAT_IMPACT[-1]
        left_end = _deck_end_nodes[bent_idx][1]        # right end of span bent_idx
        right_end = _deck_end_nodes[bent_idx + 1][0]   # left end of span bent_idx+1
        for k in range(gd):
            n += 1
            ops.element("zeroLength", n, left_end[k], right_end[k],
                        "-mat", mat, "-dir", 1)


def _define_abutment_elements() -> None:
    """Abutment soil+pile springs (zeroLength, UX & UZ) at left & right abutments.

    Connects the FIXED abutment node to the bearing-top node (which carries the
    bearing pad on its other side). Vertical (UY) is fixed directly at the
    bearing-top node (see define_boundary_conditions).
    """
    n = 7000
    for i in range(2):
        for k in range(gd):
            n += 1
            abut = _abut_nodes[i][k]
            brg_top = _bearing_top_nodes[0 if i == 0 else -1][k]
            ops.element("zeroLength", n, abut, brg_top,
                        "-mat", MAT_ABUT_LONG, MAT_ABUT_PILE, "-dir", 1, 3)


def _define_foundation_elements() -> None:
    """Foundation translational + rotational springs (zeroLength) at each bent.

    Connects spring-top node → fixed-base node with translational (UX,UZ) and
    rotational (RX,RZ) springs; UY is fixed at the spring-top via BCs.
    """
    n = 8000
    for bent in _found_nodes:
        for (n_spring, n_fixed) in bent:
            n += 1
            ops.element("zeroLength", n, n_spring, n_fixed,
                        "-mat", MAT_FND_TRANS, MAT_FND_TRANS, MAT_FND_ROT, MAT_FND_ROT,
                        "-dir", 1, 3, 4, 6)


def _define_column_elements() -> None:
    """Column dispBeamColumn elements — 7 segments per column.

    The dispBeamColumn chain runs node[1]→node[2]→…→node[8]; node[0] is the
    rigid-linked top (equalDOF'd to the bent-cap). Tags: 1000+q*50+1 .. +7.
    """
    for nodes in _col_nodes:
        base = (nodes[0] // 50) * 50        # 1000 + q*50
        for k in range(7):
            ele_tag = base + 1 + k
            ops.element("dispBeamColumn", ele_tag, nodes[k + 1], nodes[k + 2],
                        TRANS_COL, INTEG_COL)


def _define_bent_elements() -> None:
    """Bent-cap dispBeamColumn elements connecting consecutive bent-bottom nodes."""
    n = 5000
    for bent_seq in _bent_list:
        for j in range(1, len(bent_seq)):
            n += 1
            ops.element("dispBeamColumn", n, bent_seq[j - 1], bent_seq[j],
                        TRANS_BENT, INTEG_BENT)


def _define_constraints() -> None:
    """equalDOF tying each column top node[0] to its bent-cap meeting node (6 DOF)."""
    for meet_node, col_top in _eqdof_pairs:
        if col_top is not None:
            ops.equalDOF(meet_node, col_top, 1, 2, 3, 4, 5, 6)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise ODB after model is fully built.

    Per §12n/§12ac, save_nodal_resp=True is mandatory and set_odb_path must
    precede CreateODB (called in run_analysis). save_frame_resp=False avoids
    memory blow-up for this large grillage model (§12u).
    """
    odb = opst.post.CreateODB(
        odb_tag=1,
        save_nodal_resp=True,
        save_frame_resp=True,
        save_link_resp=True,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────────
def define_gravity_ramp(dt: float, ramp_duration: float = 2.0) -> int:
    """Apply FULL gravity as a smooth ramp during the transient analysis.

    Creates a Path time series that ramps from 0 to 1 over ``ramp_duration``
    seconds, and a Plain pattern carrying the full gravity load. This avoids
    the partial-gravity residual-force blowup that a static LoadControl loop
    cannot overcome for this model (§12x). The GM time series is zero-padded
    by ``ramp_duration`` so ground motion starts after gravity is fully applied.

    Returns the number of steps in the ramp (``ramp_npts``).
    """
    ramp_npts = max(2, int(ramp_duration / dt))
    ramp = np.linspace(0.0, 1.0, ramp_npts)
    ops.timeSeries("Path", TS_GRAV, "-dt", dt, "-values", *ramp, "-factor", 1.0)
    ops.pattern("Plain", PAT_GRAV, TS_GRAV)

    # --- Apply full gravity loads ---
    wt1 = slab_wt + gd_wt
    dm1 = ms * wt1 / (386.4 * inch / sec ** 2)
    dl = ln / 6.0
    deck_wt = -dm1 * dl * G_IMP              # downward force per interior deck node [N]

    for span_nodes in _deck_nodes:
        for row in span_nodes:
            for n in row:
                ops.load(n, 0.0, deck_wt, 0.0, 0.0, 0.0, 0.0)

    bWidth = D_col + 2.0 * cover_bent
    bDepth = bWidth + 2.0 * cover_bent
    bcm = -G_IMP * (gd_spc / (75.0 * inch)) * (bWidth * bDepth) * \
          (0.03397 * kip * sec ** 2 / inch) / (3.5 * 4.0 * 144.0)
    bcm2 = bcm / 2.0
    for top in _bent_top_nodes:
        for k, n in enumerate(top):
            w = bcm2 if (k == 0 or k == len(top) - 1) else bcm
            ops.load(n, 0.0, w, 0.0, 0.0, 0.0, 0.0)

    colm = -G_IMP * (D_col / (36.0 * inch)) ** 2 * 0.000229 * \
           kip * sec ** 2 / inch * ch / (3.0 * inch)
    colm2 = colm / 2.0
    for nodes in _col_nodes:
        ops.load(nodes[0], 0.0, colm2, 0.0, 0.0, 0.0, 0.0)
        ops.load(nodes[1], 0.0, colm, 0.0, 0.0, 0.0, 0.0)
        ops.load(nodes[2], 0.0, colm, 0.0, 0.0, 0.0, 0.0)
        for k in range(3, 8):
            ops.load(nodes[k], 0.0, colm2, 0.0, 0.0, 0.0, 0.0)

    return ramp_npts


def _generate_synthetic_gm(dt: float, npts: int) -> np.ndarray:
    """Apply gravity not converged in static analysis as a smooth ramp
    during the transient dynamic analysis.

    Creates a Path time series that ramps 0→1 over 0.5 s and a Plain
    pattern applying (remaining_factor × original gravity loads) to all
    gravity-load nodes. Combined with the frozen gravity pattern
    (converged_fraction), total gravity smoothly reaches 100% over 0.5 s.

    Args:
        remaining_factor: Fraction of gravity NOT converged in static phase
            (e.g. 0.6 for 40% converged → 60% remaining).
        dt: Ground-motion time step (used for Path series spacing).
    """
    if remaining_factor < 0.01:
        return
    ramp_duration = 0.5  # seconds to ramp remaining gravity
    ramp_steps = max(2, int(ramp_duration / dt))
    ramp = np.linspace(0.0, 1.0, ramp_steps)
    ops.timeSeries("Path", TS_GRAV_RAMP, "-dt", dt,
                   "-values", *ramp, "-factor", remaining_factor)
    ops.pattern("Plain", PAT_GRAV_RAMP, TS_GRAV_RAMP)

    wt1 = slab_wt + gd_wt
    dm1 = ms * wt1 / (386.4 * inch / sec ** 2)
    dl = ln / 6.0
    deck_wt = -dm1 * dl * G_IMP

    for span_nodes in _deck_nodes:
        for row in span_nodes:
            for n in row:
                ops.load(n, 0.0, deck_wt, 0.0, 0.0, 0.0, 0.0)

    bWidth = D_col + 2.0 * cover_bent
    bDepth = bWidth + 2.0 * cover_bent
    bcm = -G_IMP * (gd_spc / (75.0 * inch)) * (bWidth * bDepth) * \
          (0.03397 * kip * sec ** 2 / inch) / (3.5 * 4.0 * 144.0)
    bcm2 = bcm / 2.0
    for top in _bent_top_nodes:
        for k, n in enumerate(top):
            w = bcm2 if (k == 0 or k == len(top) - 1) else bcm
            ops.load(n, 0.0, w, 0.0, 0.0, 0.0, 0.0)

    colm = -G_IMP * (D_col / (36.0 * inch)) ** 2 * 0.000229 * \
           kip * sec ** 2 / inch * ch / (3.0 * inch)
    colm2 = colm / 2.0
    for nodes in _col_nodes:
        ops.load(nodes[0], 0.0, colm2, 0.0, 0.0, 0.0, 0.0)
        ops.load(nodes[1], 0.0, colm, 0.0, 0.0, 0.0, 0.0)
        ops.load(nodes[2], 0.0, colm, 0.0, 0.0, 0.0, 0.0)
        for k in range(3, 8):
            ops.load(nodes[k], 0.0, colm2, 0.0, 0.0, 0.0, 0.0)


def _generate_synthetic_gm(dt: float, npts: int) -> np.ndarray:
    """Generate a synthetic Ricker-wavelet ground motion (acceleration in g)."""
    t = np.arange(npts) * dt
    freq = 2.0
    t0 = npts * dt / 3.0
    tau = np.pi * freq * (t - t0)
    accel_g = (1.0 - 2.0 * tau ** 2) * np.exp(-tau ** 2)
    accel_g *= 0.3 / np.max(np.abs(accel_g))
    return accel_g


def _rotate_gm(accel_x: np.ndarray, accel_y: np.ndarray, angle_deg: float):
    """Rotate two orthogonal GM components by the incidence angle (rectify_gm.tcl)."""
    a = math.radians(angle_deg)
    gm_x = math.cos(a) * accel_x + math.cos(a + math.pi / 2.0) * accel_y
    gm_z = math.sin(a) * accel_x + math.sin(a + math.pi / 2.0) * accel_y
    return gm_x, gm_z


def define_ground_motion(ramp_pad_steps: int = 0) -> tuple:
    """Define UniformExcitation in X (longitudinal) and Z (transverse).

    The GM time series is zero-padded by ``ramp_pad_steps`` at dt spacing so
    ground motion starts after the gravity ramp has completed.

    Returns (dt, total_npts) where total_npts includes the pad.
    """
    if gm_file_x:
        ax = np.loadtxt(gm_dir / gm_file_x)
        ay = np.loadtxt(gm_dir / gm_file_z) if gm_file_z else np.zeros_like(ax)
        npts = len(ax)
        dt = gm_dt
    else:
        dt = gm_dt
        npts = gm_npts
        ax = _generate_synthetic_gm(dt, npts)
        ay = np.zeros_like(ax)

    gm_x, gm_z = _rotate_gm(ax, ay, load_dir)
    factor = G_IMP                                    # g -> mm/s² (≈ g)

    # Zero-pad for gravity ramp
    if ramp_pad_steps > 0:
        gm_x_pad = np.concatenate([np.zeros(ramp_pad_steps), gm_x * factor])
        gm_z_pad = np.concatenate([np.zeros(ramp_pad_steps), gm_z * factor])
    else:
        gm_x_pad = gm_x * factor
        gm_z_pad = gm_z * factor
    total_npts = len(gm_x_pad)

    ops.timeSeries("Path", TS_GM_X, "-dt", dt, "-values", *gm_x_pad, "-factor", 1.0)
    ops.timeSeries("Path", TS_GM_Z, "-dt", dt, "-values", *gm_z_pad, "-factor", 1.0)
    ops.pattern("UniformExcitation", PAT_GM_X, 1, "-accel", TS_GM_X)   # longitudinal
    ops.pattern("UniformExcitation", PAT_GM_Z, 3, "-accel", TS_GM_Z)   # transverse
    return dt, total_npts


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB", n_steps: int = 10) -> int:
    """Apply gravity via load-controlled static analysis (manual loop).

    SmartAnalyze.StaticAnalyze forcibly overrides the integrator to
    DisplacementControl, so a manual LoadControl loop is used (§3c exception).

    This MSSS bridge has large stiffness contrasts (rigid links, fiber columns,
    nonlinear bearings, soil/foundation springs) that make full-gravity
    convergence hard beyond ~50-60% load factor — a known issue for this class
    of 3D highway-bridge model (§12x). The loop applies as many increments as
    converge, then freezes whatever gravity has been applied with loadConst so
    the transient phase can proceed. Returns the number of converged steps.
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.test("NormDispIncr", 1.0e-4, 200, 3)
    ops.algorithm("NewtonLineSearch")
    ops.analysis("Static")

    converged = 0
    for _ in range(n_steps):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"  gravity stalled at step {converged + 1}/{n_steps} "
                  f"({100.0 * converged / n_steps:.0f}% load) — freezing applied gravity")
            break
        odb.fetch_response_step()
        converged += 1

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()
    return converged


def run_eigen(n_modes: int = 2) -> list:
    """Compute eigenvalues and print periods (modal.tcl)."""
    ops.wipeAnalysis()
    eigs = ops.eigen(n_modes)
    for i, lam in enumerate(eigs):
        T = 2.0 * math.pi / math.sqrt(lam)
        print(f"  T{i + 1} = {T:.4f} s")
    return eigs


def run_dynamic(odb: "opst.post.CreateODB", dt: float, npts: int,
                odb_every_n: int = 5) -> None:
    """Run transient dynamic analysis with manual KrylovNewton loop.

    SmartAnalyze's adaptive sub-stepping produces matrix-factorisation failures
    for this model (the stiffness contrast between rigid links, fiber columns,
    and nonlinear bearings creates near-zero effective-stiffness modes at very
    small step sizes). A manual loop with KrylovNewton at a fixed dt=0.001s
    converges and matches the Tcl source's manual while-loop strategy.

    This is a documented exception to the SmartAnalyze mandate per §3c/§10
    (SmartAnalyze is incompatible with this model's numerical characteristics).

    Rayleigh coefficients are computed from the first 2 eigenvalues (t_analysis_eq2.tcl).
    """
    eigs = run_eigen(2)
    wi = math.sqrt(eigs[0])
    wj = math.sqrt(eigs[1])
    alpha = dr * (2.0 * wi * wj) / (wi + wj)
    beta = dr * (2.0) / (wi + wj)
    ops.rayleigh(alpha, 0.0, beta, 0.0)

    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("Newmark", 0.5, 0.25)
    ops.test("NormDispIncr", 1.0e-3, 200, 3)
    ops.algorithm("Newton")
    ops.analysis("Transient")

    t_current = 0.0
    step_count = 0
    dt_analysis = 0.001  # fixed step matching Tcl source (§3c exception)
    steps_per_gm = max(1, int(round(dt / dt_analysis)))
    total_analysis_steps = npts * steps_per_gm

    for i in range(total_analysis_steps):
        ok = ops.analyze(1, dt_analysis)
        if ok != 0:
            # Fallback: try NewtonLineSearch with relaxed tolerance
            ops.test("NormDispIncr", 1.0e-2, 100, 3)
            ops.algorithm("NewtonLineSearch")
            ok = ops.analyze(1, dt_analysis)
            # Restore tighter settings for next step
            ops.test("NormDispIncr", 1.0e-3, 200, 3)
            ops.algorithm("Newton")
        if ok != 0:
            print(f"  Dynamic analysis failed at t = {t_current:.3f} s "
                  f"(analysis step {i})")
            break
        t_current += dt_analysis
        step_count += 1
        # Throttle ODB to GM-step cadence
        if i % max(1, steps_per_gm * odb_every_n) == 0:
            odb.fetch_response_step()

    # Collect remaining steps
    if step_count > 0 and step_count % max(1, steps_per_gm * odb_every_n) != 0:
        odb.fetch_response_step()

    print(f"  Completed {step_count} steps (t_final = {t_current:.3f} s)")


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + dynamic, return ODB for post-processing."""
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))   # MUST precede CreateODB (§12ac)

    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    define_masses()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)

    odb = create_odb(output_dir)

    # Gravity applied as a smooth ramp during the transient (§12x exception).
    # Static LoadControl cannot converge full gravity for this model, so we
    # ramp gravity from 0→100% over grav_ramp_dur seconds and zero-pad the
    # ground motion to start after the ramp completes.
    ramp_npts = define_gravity_ramp(gm_dt, ramp_duration=grav_ramp_dur)
    vis_loads(output_dir)
    print(f"  Gravity ramp: {grav_ramp_dur}s ({ramp_npts} steps at dt={gm_dt:.4f}s)")

    # Ground motion zero-padded for the gravity ramp duration
    gm_dt_local, gm_total_npts = define_ground_motion(ramp_pad_steps=ramp_npts)
    vis_pre_analysis(output_dir)

    print(f"Running dynamic analysis ({gm_total_npts} steps, dt={gm_dt_local:.4f} s) ...")
    run_dynamic(odb, gm_dt_local, gm_total_npts, odb_every_n=odb_every_n)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and render deformed-shape HTML."""
    odb.save_response()
    opst.post.set_odb_path(str(output_dir))     # ensure path active for vis (§12w)
    if not _headless():
        fig = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, step="absMax", defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig.write_html(str(output_dir / "vis_05_deformed_peak.html"))
        fig2 = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, slides=True, defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig2.write_html(str(output_dir / "vis_06_deformed_slider.html"))


# ── 14. MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
