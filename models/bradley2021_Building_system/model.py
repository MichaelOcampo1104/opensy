# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 3-Story Chevron-Braced Steel Frame (SID-1, R3)
UniqueID : bradley2021_Building_system
Author   : Bradley et al. (2021) — converted from Tcl
Date     : 2026-06-07
Purpose  : 2D nonlinear model of a 3-story chevron-braced steel frame (CBF)
           for pushover and dynamic analysis.
Ref      : Bradley, C. et al. (2021). DesignSafe-CI PRJ-2957.
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────

# ── Materials: Elastic (stiffness-scaled for numerical stability) ──
MAT_ELASTIC_E8 = 1
MAT_ELASTIC_E7 = 2
MAT_ELASTIC_E6 = 3
MAT_ELASTIC_E5 = 4
MAT_ELASTIC_E4 = 5
MAT_ELASTIC_E3 = 6
MAT_ELASTIC_E2 = 7
MAT_ELASTIC_E1 = 8
MAT_ELASTIC_E0 = 9
MAT_ELASTIC_Ep3 = 10
MAT_ENT = 11
MAT_B2C_GAP = 12
MAT_G2C_GAP = 13
MAT_B2C_CONTACT = 14
MAT_G2C_CONTACT = 15

# ── Materials: Tension-Coupon SteelMPF composites (19 angle sizes) ──
# Each TC has: SteelMPF → Fatigue → MinMax → Parallel(+Elastic+ENT)
MAT_TC1_SF  = 16; MAT_TC1_F = 17; MAT_TC1_M = 18; MAT_TC1_P = 19
MAT_TC2_SF  = 20; MAT_TC2_F = 21; MAT_TC2_M = 22; MAT_TC2_P = 23
MAT_TC3_SF  = 24; MAT_TC3_F = 25; MAT_TC3_M = 26; MAT_TC3_P = 27
MAT_TC4_SF  = 28; MAT_TC4_F = 29; MAT_TC4_M = 30; MAT_TC4_P = 31
MAT_TC5_SF  = 32; MAT_TC5_F = 33; MAT_TC5_M = 34; MAT_TC5_P = 35
MAT_TC6_SF  = 36; MAT_TC6_F = 37; MAT_TC6_M = 38; MAT_TC6_P = 39
MAT_TC7_SF  = 40; MAT_TC7_F = 41; MAT_TC7_M = 42; MAT_TC7_P = 43
MAT_TC8_SF  = 44; MAT_TC8_F = 45; MAT_TC8_M = 46; MAT_TC8_P = 47
MAT_TC9_SF  = 48; MAT_TC9_F = 49; MAT_TC9_M = 50; MAT_TC9_P = 51
MAT_TC10_SF = 52; MAT_TC10_F = 53; MAT_TC10_M = 54; MAT_TC10_P = 55
MAT_TC11_SF = 56; MAT_TC11_F = 57; MAT_TC11_M = 58; MAT_TC11_P = 59
MAT_TC12_SF = 60; MAT_TC12_F = 61; MAT_TC12_M = 62; MAT_TC12_P = 63
MAT_TC13_SF = 64; MAT_TC13_F = 65; MAT_TC13_M = 66; MAT_TC13_P = 67
MAT_TC14_SF = 68; MAT_TC14_F = 69; MAT_TC14_M = 70; MAT_TC14_P = 71
MAT_TC15_SF = 72; MAT_TC15_F = 73; MAT_TC15_M = 74; MAT_TC15_P = 75
MAT_TC16_SF = 76; MAT_TC16_F = 77; MAT_TC16_M = 78; MAT_TC16_P = 79
MAT_TC17_SF = 80; MAT_TC17_F = 81; MAT_TC17_M = 82; MAT_TC17_P = 83
MAT_TC18_SF = 84; MAT_TC18_F = 85; MAT_TC18_M = 86; MAT_TC18_P = 87
MAT_TC19_SF = 88; MAT_TC19_F = 89; MAT_TC19_M = 90; MAT_TC19_P = 91

# ── Materials: Gusset plate Steel02 ──
MAT_GUSSET_S1_L = 96; MAT_GUSSET_S1_R = 97
MAT_GUSSET_S2_L = 92; MAT_GUSSET_S2_R = 93
MAT_GUSSET_S3_L = 94; MAT_GUSSET_S3_R = 95

# ── Materials: W12X40 Web composites (repeated for each beam line) ──
MAT_W12X40_E1_SF = 98;  MAT_W12X40_E1_F = 99;  MAT_W12X40_E1_EL = 100; MAT_W12X40_E1_P = 101
MAT_W12X40_E2_SF = 102; MAT_W12X40_E2_F = 103; MAT_W12X40_E2_EL = 104; MAT_W12X40_E2_P = 105
MAT_W12X40_E3_SF = 106; MAT_W12X40_E3_F = 107; MAT_W12X40_E3_EL = 108; MAT_W12X40_E3_P = 109
MAT_W12X40_D1_SF = 116; MAT_W12X40_D1_F = 117; MAT_W12X40_D1_EL = 118; MAT_W12X40_D1_P = 119
MAT_W12X40_D2_SF = 120; MAT_W12X40_D2_F = 121; MAT_W12X40_D2_EL = 122; MAT_W12X40_D2_P = 123
MAT_W12X40_D3_SF = 124; MAT_W12X40_D3_F = 125; MAT_W12X40_D3_EL = 126; MAT_W12X40_D3_P = 127
MAT_W12X40_F1_SF = 128; MAT_W12X40_F1_F = 129; MAT_W12X40_F1_EL = 130; MAT_W12X40_F1_P = 131
MAT_W12X40_F2_SF = 132; MAT_W12X40_F2_F = 133; MAT_W12X40_F2_EL = 134; MAT_W12X40_F2_P = 135
MAT_W12X40_F3_SF = 136; MAT_W12X40_F3_F = 137; MAT_W12X40_F3_EL = 138; MAT_W12X40_F3_P = 139

# ── Materials: W12X50 Web composites ──
MAT_W12X50_C1_SF = 140; MAT_W12X50_C1_F = 141; MAT_W12X50_C1_EL = 142; MAT_W12X50_C1_P = 143
MAT_W12X50_C2_SF = 144; MAT_W12X50_C2_F = 145; MAT_W12X50_C2_EL = 146; MAT_W12X50_C2_P = 147
MAT_W12X50_C3_SF = 148; MAT_W12X50_C3_F = 149; MAT_W12X50_C3_EL = 150; MAT_W12X50_C3_P = 151
MAT_W12X50_D4_SF = 152; MAT_W12X50_D4_F = 153; MAT_W12X50_D4_EL = 154; MAT_W12X50_D4_P = 155
MAT_W12X50_D5_SF = 156; MAT_W12X50_D5_F = 157; MAT_W12X50_D5_EL = 158; MAT_W12X50_D5_P = 159
MAT_W12X50_D6_SF = 160; MAT_W12X50_D6_F = 161; MAT_W12X50_D6_EL = 162; MAT_W12X50_D6_P = 163

# ── Materials: W12X40 Web composites (C/F lines, continued) ──
MAT_W12X40_C4_SF = 164; MAT_W12X40_C4_F = 165; MAT_W12X40_C4_EL = 166; MAT_W12X40_C4_P = 167
MAT_W12X40_C5_SF = 168; MAT_W12X40_C5_F = 169; MAT_W12X40_C5_EL = 170; MAT_W12X40_C5_P = 171
MAT_W12X40_C6_SF = 172; MAT_W12X40_C6_F = 173; MAT_W12X40_C6_EL = 174; MAT_W12X40_C6_P = 175

# ── Materials: W12X35 Web composites ──
MAT_W12X35_FS1_SF = 182; MAT_W12X35_FS1_F = 183; MAT_W12X35_FS1_EL = 184; MAT_W12X35_FS1_P = 185
MAT_W12X35_FS2_SF = 186; MAT_W12X35_FS2_F = 187; MAT_W12X35_FS2_EL = 188; MAT_W12X35_FS2_P = 189
MAT_W12X35_FS3_SF = 190; MAT_W12X35_FS3_F = 191; MAT_W12X35_FS3_EL = 192; MAT_W12X35_FS3_P = 193
MAT_W12X35_CS1_SF = 194; MAT_W12X35_CS1_F = 195; MAT_W12X35_CS1_EL = 196; MAT_W12X35_CS1_P = 197
MAT_W12X35_CS2_SF = 198; MAT_W12X35_CS2_F = 199; MAT_W12X35_CS2_EL = 200; MAT_W12X35_CS2_P = 201
MAT_W12X35_CS3_SF = 202; MAT_W12X35_CS3_F = 203; MAT_W12X35_CS3_EL = 204; MAT_W12X35_CS3_P = 205

# ── Materials: W12X35 Web composites (F lines) ──
MAT_W12X35_F4_SF = 206; MAT_W12X35_F4_F = 207; MAT_W12X35_F4_EL = 208; MAT_W12X35_F4_P = 209
MAT_W12X35_F5_SF = 210; MAT_W12X35_F5_F = 211; MAT_W12X35_F5_EL = 212; MAT_W12X35_F5_P = 213
MAT_W12X35_F6_SF = 214; MAT_W12X35_F6_F = 215; MAT_W12X35_F6_EL = 216; MAT_W12X35_F6_P = 217

# ── Materials: IMK Bilin springs ──
MAT_IMK_W12X50_S = [110, 111, 112, 113, 114, 115]
MAT_IMK_W12X35_S = [176, 177, 178]
MAT_IMK_W12X40_S = [179, 180, 181]
MAT_IMK_W16X57_S = [218, 220, 222, 224]
MAT_IMK_W16X26_S = [219, 221, 223, 225]
MAT_IMK_W16X40_S = [226, 227]
MAT_IMK_W12X26_S = [228]
MAT_IMK_W18X60_S = [229, 231, 233, 235]
MAT_IMK_W18X35_S = [230, 232, 234, 236]

# ── Materials: Brace Steel02 composites (BR1-BR6) ──
MAT_BR1_SF = 237; MAT_BR1_F = 238; MAT_BR1_EL = 239; MAT_BR1_P = 240
MAT_BR2_SF = 241; MAT_BR2_F = 242; MAT_BR2_EL = 243; MAT_BR2_P = 244
MAT_BR3_SF = 245; MAT_BR3_F = 246; MAT_BR3_EL = 247; MAT_BR3_P = 248
MAT_BR4_SF = 249; MAT_BR4_F = 250; MAT_BR4_EL = 251; MAT_BR4_P = 252
MAT_BR5_SF = 253; MAT_BR5_F = 254; MAT_BR5_EL = 255; MAT_BR5_P = 256
MAT_BR6_SF = 257; MAT_BR6_F = 258; MAT_BR6_EL = 259; MAT_BR6_P = 260

# ── Sections: Fiber + Aggregator for bolted angle connections ──
SEC_FIBER_B1L_W16X57 = 1
SEC_AGG_B1L = 2
SEC_FIBER_B3L_W16X26 = 3
SEC_AGG_B3L = 4
SEC_FIBER_B19L_W16X40_BR1 = 5
SEC_AGG_B19L = 6
SEC_FIBER_B20L_W16X40_BR1 = 7
SEC_AGG_B20L = 8
SEC_FIBER_B21L_W12X26 = 9
SEC_AGG_B21L = 10
SEC_FIBER_B31L_W18X60 = 11
SEC_AGG_B31L = 12
SEC_FIBER_B33L_W18X35 = 13
SEC_AGG_B33L = 14

# ── Sections: W-shape fiber sections (weak-axis) ──
SEC_W12X40_E1  = 15; SEC_W12X40_E2  = 16; SEC_W12X40_E3  = 17
SEC_W12X40_E6  = 18; SEC_W12X40_E6b = 19; SEC_W12X40_E6c = 20
SEC_W12X40_D1  = 21; SEC_W12X40_D1b = 22; SEC_W12X40_D1c = 23
SEC_W12X50_D2  = 24; SEC_W12X50_D2b = 25; SEC_W12X50_D2c = 26
SEC_W12X50_D5  = 27; SEC_W12X50_D5b = 28; SEC_W12X50_D5c = 29
SEC_W12X40_D6  = 30; SEC_W12X40_D6b = 31; SEC_W12X40_D6c = 32
SEC_W12X40_F3  = 33; SEC_W12X40_F3b = 34; SEC_W12X40_F3c = 35
SEC_W12X40_F4  = 36; SEC_W12X40_F4b = 37; SEC_W12X40_F4c = 38
SEC_W12X35_F6  = 39; SEC_W12X35_F6b = 40; SEC_W12X35_F6c = 41

# ── Sections: HSS brace fiber sections ──
SEC_HSS9X9_BR1 = 42; SEC_HSS8X8_BR2 = 43; SEC_HSS7X7_BR3 = 44
SEC_HSS9X9_BR4 = 45; SEC_HSS8X8_BR5 = 46; SEC_HSS7X7_BR6 = 47

# ── GeomTransf tags ──
GEOM_PDELTA = 1
GEOM_COROT = 2

# ── Key Node Tags ──
# Grid C (left braced frame): columns at 0, 420, 840, 1260, 1680, 2100 in X
# Grid D (interior frame): columns at 2160, 2580, 3000, 3420, 3840, 4260 in X
# Grid E (right braced frame): columns at 4320, 4740, 5160, 5580, 6000, 6420 in X
# Grid F (pinned leaner): columns at 0, 420, 840, 1260, 1680, 2100 in X

# Braced frame lines: C (left, nodes 1-24, 261-346), D (nodes 25-84), E (right, nodes 85-232)
# Pinned leaner: F (nodes 233-346)

# Roof node for pushover control
NODE_ROOF_CTRL = 54

# Base nodes (all columns fixed at base)
NODE_BASE = [1, 25, 39, 55, 71, 85, 109, 133, 157, 171, 185, 209, 233, 247, 261, 285, 309, 323]

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# All values converted from imperial (in, kip, ksi) to N, mm, MPa
n_stories = 3
h_story = 180.0 * inch          # 180 in → 4572 mm (15 ft)
height = 540.0 * inch           # 540 in → 13716 mm (45 ft)
zeta = 0.02                     # critical damping ratio
config = "Chevron"              # bracing configuration
n_mod = 10.0                    # n-modification factor for stiff damping

# Steel material properties (base)
E0 = 29000.0 * ksi              # 199948 MPa
Fy = 55.0 * ksi                 # ~379 MPa (W12X40 web yield)
b = 0.01                        # strain-hardening ratio for Steel02

# ── 4. HELPER FUNCTIONS ──────────────────────────────────────────────────────

def _section_W(sec_tag, mat_tag, d, bf, tf, tw, n_fw_d, n_fw_t, n_ff_w, n_ff_t, axis):
    """Fiber-discretise a W-shape section (strong or weak axis bending).

    Port of the Tcl ``Section W`` procedure from P-Section.tcl.
    Axis: 1 = strong (major), 0 = weak (minor).
    """
    dw = d - 2.0 * tf
    y1 = -d / 2.0;  y2 = -dw / 2.0;  y3 = dw / 2.0;  y4 = d / 2.0
    z1 = -bf / 2.0; z2 = -tw / 2.0;  z3 = tw / 2.0;  z4 = bf / 2.0

    if axis == 1:  # strong axis
        ops.section("Fiber", sec_tag)
        ops.patch("quad", mat_tag, n_ff_w, n_ff_t, y1, z4, y1, z1, y2, z1, y2, z4)
        ops.patch("quad", mat_tag, n_fw_d, n_fw_t, y2, z3, y2, z2, y3, z2, y3, z3)
        ops.patch("quad", mat_tag, n_ff_w, n_ff_t, y3, z4, y3, z1, y4, z1, y4, z4)
    else:  # weak axis
        ops.section("Fiber", sec_tag)
        ops.patch("quad", mat_tag, n_ff_w, n_ff_t, z1, y1, z4, y1, z4, y2, z1, y2)
        ops.patch("quad", mat_tag, n_fw_d, n_fw_t, z2, y2, z3, y2, z3, y3, z2, y3)
        ops.patch("quad", mat_tag, n_ff_w, n_ff_t, z1, y3, z4, y3, z4, y4, z1, y4)


def _section_HSS(sec_tag, mat_tag, d, t, n_fw_d, n_fw_t, n_ff_w, n_ff_t):
    """Fiber-discretise a square HSS section.

    Port of the Tcl ``Section HSS`` procedure from P-Section.tcl.
    """
    dw = d - 2.0 * t
    y1 = -d / 2.0;  y2 = -dw / 2.0;  y3 = dw / 2.0;  y4 = d / 2.0
    z1 = -d / 2.0;  z2 = -dw / 2.0;  z3 = dw / 2.0;  z4 = d / 2.0

    ops.section("Fiber", sec_tag)
    ops.patch("quad", mat_tag, n_ff_w, n_fw_d, y2, z4, y2, z3, y3, z3, y3, z4)   # top flange
    ops.patch("quad", mat_tag, n_ff_w, n_fw_d, y2, z2, y2, z1, y3, z1, y3, z2)   # bottom flange
    ops.patch("quad", mat_tag, n_ff_t, n_fw_t, y1, z4, y1, z1, y2, z1, y2, z4)   # left web
    ops.patch("quad", mat_tag, n_ff_t, n_fw_t, y3, z4, y3, z1, y4, z1, y4, z4)   # right web


def _define_elements_batch(elem_type, e_tags, i_nodes, j_nodes, *args):
    """Batch-create OpenSees elements, port of Tcl ``DefineElements``.

    The ``*args`` can contain lists (one value per element) or scalars.
    ``zeroLength-IMK`` and ``zeroLength-SBL/SBR`` add automatic equalDOFs.
    ``dispBeamColumn`` is translated from Tcl order (nIP, secTag, geomTag)
    to OpenSeesPy order (geomTag, beamIntegration).
    """
    is_imk = (elem_type == "zeroLength-IMK")
    is_sbl = (elem_type == "zeroLength-SBL")
    is_sbr = (elem_type == "zeroLength-SBR")
    is_disp_bm = (elem_type == "dispBeamColumn")

    if is_imk or is_sbl or is_sbr:
        elem_type = "zeroLength"
    elif is_disp_bm:
        # Tcl: (nIP, secTag, geomTag) → OpenSeesPy: (geomTag, beamIntegration)
        return _define_disp_beam_batch(e_tags, i_nodes, j_nodes, *args)

    n_ele = len(e_tags)
    for idx in range(n_ele):
        etag = e_tags[idx]
        inode = i_nodes[idx]
        jnode = j_nodes[idx]
        resolved = []
        for a in args:
            if isinstance(a, (list, tuple)):
                resolved.append(a[idx])
            else:
                resolved.append(a)
        getattr(ops, "element")(elem_type, etag, inode, jnode, *resolved)

        if is_imk:
            ops.equalDOF(inode, jnode, 1, 2)
        if is_sbl:
            ops.equalDOF(inode, jnode - 1, 2, 3)
        if is_sbr:
            ops.equalDOF(inode + 1, jnode, 2, 3)


def _define_disp_beam_batch(e_tags, i_nodes, j_nodes, n_ip, sec_tags, geom_tag):
    """Create dispBeamColumn elements with OpenSeesPy beamIntegration convention.

    Tcl convention:  element dispBeamColumn tag iNd jNd nIP secTag transfTag
    OpenSeesPy:      element('dispBeamColumn', tag, iNd, jNd, transfTag, integTag)
    """
    n_ele = len(e_tags)
    for idx in range(n_ele):
        etag = e_tags[idx]
        inode = i_nodes[idx]
        jnode = j_nodes[idx]
        # Resolve per-element args
        _nip = n_ip[idx] if isinstance(n_ip, (list, tuple)) else n_ip
        _sec = sec_tags[idx] if isinstance(sec_tags, (list, tuple)) else sec_tags
        _gtag = geom_tag[idx] if isinstance(geom_tag, (list, tuple)) else geom_tag
        integ_tag = _beam_integ(_sec, _nip)
        ops.element("dispBeamColumn", etag, inode, jnode, _gtag, integ_tag)


# ── Beam-integration cache (section → integ tag) for dispBeamColumn ──
_INTEG_CACHE = {}
_INTEG_NEXT = 1000  # start high to avoid collisions with other tags


def _beam_integ(sec_tag, n_ip=5):
    """Return a beamIntegration tag for (sec_tag, n_ip), creating one if needed."""
    key = (sec_tag, n_ip)
    if key not in _INTEG_CACHE:
        global _INTEG_NEXT
        tid = _INTEG_NEXT
        _INTEG_NEXT += 1
        ops.beamIntegration("Lobatto", tid, sec_tag, n_ip)
        _INTEG_CACHE[key] = tid
    return _INTEG_CACHE[key]


# ── 5. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model():
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)
    ops.geomTransf("PDelta", GEOM_PDELTA)
    ops.geomTransf("Corotational", GEOM_COROT)


# ── 6. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials():
    # ── Elastic (stiffness-scaled for numerical stability; E in MPa) ──
    _E = 199948.0  # E0 = 29000 ksi
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_E8,  1e-8 * _E)   # E*10^-8
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_E7,  1e-7 * _E)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_E6,  1e-6 * _E)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_E5,  1e-5 * _E)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_E4,  1e-4 * _E)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_E3,  1e-3 * _E)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_E2,  1e-2 * _E)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_E1,  1e-1 * _E)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_E0,  1.0 * _E)
    ops.uniaxialMaterial("Elastic", MAT_ELASTIC_Ep3, 1e3 * _E)

    # ── ENT (bolt bearing elastic, 29000 ksi = 199948 MPa) ──
    ops.uniaxialMaterial("ENT", MAT_ENT, 199948.0)

    # ── ElasticPPGap: brace-to-column / gusset-to-column contact ──
    ops.uniaxialMaterial("ElasticPPGap", MAT_B2C_GAP, 1999.48, -55.0 * ksi, -0.5)
    ops.uniaxialMaterial("ElasticPPGap", MAT_G2C_GAP, 1999.48, -46.8 * ksi, -0.5)
    ops.uniaxialMaterial("Parallel", MAT_B2C_CONTACT, MAT_B2C_GAP, MAT_ELASTIC_E3)
    ops.uniaxialMaterial("Parallel", MAT_G2C_CONTACT, MAT_G2C_GAP, MAT_ELASTIC_E3)

    # ── Tension-coupon SteelMPF composites (19 angle sizes from Beland et al. 2019) ──
    _tc = [  # (tag_steelmpf, tag_fatigue, tag_minmax, tag_parallel, fyp, fyn, E0, bp, bn, R1, R2, R3, eps_fatigue, eps_max)
        # TC1: L6X4X3/8
        (MAT_TC1_SF, MAT_TC1_F, MAT_TC1_M, MAT_TC1_P,
         21.638461, 21.638461, 1987.230, 0.0129, 0.0129, 1.118, -0.944, 0.2283465, 1.785, 1.0),
        # TC2: L6X6X3/8
        (MAT_TC2_SF, MAT_TC2_F, MAT_TC2_M, MAT_TC2_P,
         17.823831, 17.823831, 1770.234, 0.0155, 0.0155, 1.114, -1.306, 0.1771654, 1.98, 1.318898),
        # TC3: L8X4X1/2
        (MAT_TC3_SF, MAT_TC3_F, MAT_TC3_M, MAT_TC3_P,
         44.120141, 44.120141, 5156.520, 0.017, 0.017, 1.803, -0.633, 0.1023622, 1.2, 0.7047244),
        # TC4: L8X6X1/2
        (MAT_TC4_SF, MAT_TC4_F, MAT_TC4_M, MAT_TC4_P,
         41.142401, 41.142401, 3117.896, 0.0137, 0.0137, 1.451, -0.733, 0.2007874, 1.785, 1.543307),
        # TC5: L8X6X5/8
        (MAT_TC5_SF, MAT_TC5_F, MAT_TC5_M, MAT_TC5_P,
         60.271851, 60.271851, 12454.45, 0.0046, 0.0046, 1.625, -1.03, 0.1574803, 1.955, 1.374016),
        # TC6: L8X6X3/4
        (MAT_TC6_SF, MAT_TC6_F, MAT_TC6_M, MAT_TC6_P,
         84.903351, 84.903351, 11346.63, 0.0041, 0.0041, 1.311, -0.932, 0.1417323, 1.565, 1.086614),
        # TC7: L6X6X3/8
        (MAT_TC7_SF, MAT_TC7_F, MAT_TC7_M, MAT_TC7_P,
         16.867691, 16.867691, 822.3022, 0.0241, 0.0241, 1.314, -1.14, 0.2559055, 2.19, 1.370079),
        # TC8: L6X6X3/8
        (MAT_TC8_SF, MAT_TC8_F, MAT_TC8_M, MAT_TC8_P,
         15.874231, 15.874231, 793.7500, 0.0158, 0.0158, 0.939, -1.323, 0.2283465, 2.612, 1.452756),
        # TC9: L8X6X1/2
        (MAT_TC9_SF, MAT_TC9_F, MAT_TC9_M, MAT_TC9_P,
         34.749981, 34.749981, 2158.543, 0.0133, 0.0133, 1.687, -0.518, 0.2165354, 2.185, 1.799213),
        # TC10: L8X6X1/2
        (MAT_TC10_SF, MAT_TC10_F, MAT_TC10_M, MAT_TC10_P,
         26.148961, 26.148961, 2272.752, 0.0125, 0.0125, 1.751, -0.639, 0.2322835, 2.39, 1.559055),
        # TC11: L8X6X5/8
        (MAT_TC11_SF, MAT_TC11_F, MAT_TC11_M, MAT_TC11_P,
         49.478561, 49.478561, 5127.968, 0.0105, 0.0105, 1.211, -0.935, 0.2125984, 1.84, 0.6062992),
        # TC12: L8X6X5/8
        (MAT_TC12_SF, MAT_TC12_F, MAT_TC12_M, MAT_TC12_P,
         42.154431, 42.154431, 5476.304, 0.0078, 0.0078, 1.218, -0.861, 0.2165354, 1.96, 1.405512),
        # TC13: L8X6X3/4
        (MAT_TC13_SF, MAT_TC13_F, MAT_TC13_M, MAT_TC13_P,
         69.400742, 69.400742, 9679.182, 0.0077, 0.0077, 0.895, -1.162, 0.1653543, 1.96, 1.003937),
        # TC14: L8X6X3/4
        (MAT_TC14_SF, MAT_TC14_F, MAT_TC14_M, MAT_TC14_P,
         57.115898, 57.115898, 7149.460, 0.01, 0.01, 1.079, -1.088, 0.2165354, 1.84, 0.8700787),
        # TC15: L6X6X3/8
        (MAT_TC15_SF, MAT_TC15_F, MAT_TC15_M, MAT_TC15_P,
         11.168101, 11.168101, 405.4406, 0.0263, 0.0263, 1.179, -1.369, 0.2716535, 2.39, 1.905512),
        # TC16: L8X6X1/2
        (MAT_TC16_SF, MAT_TC16_F, MAT_TC16_M, MAT_TC16_P,
         23.691750, 23.691750, 2095.728, 0.0116, 0.0116, 1.218, -0.876, 0.2874016, 1.785, 1.5),
        # TC17: L8X6X5/8
        (MAT_TC17_SF, MAT_TC17_F, MAT_TC17_M, MAT_TC17_P,
         35.420650, 35.420650, 4277.113, 0.0065, 0.0065, 1.492, -0.677, 0.1929134, 2.61, 1.96063),
        # TC18: L8X6X3/4
        (MAT_TC18_SF, MAT_TC18_F, MAT_TC18_M, MAT_TC18_P,
         46.783939, 46.783939, 5653.327, 0.0055, 0.0055, 1.526, -0.274, 0.1889764, 2.61, 1.712598),
        # TC19: L4X4X5/16
        (MAT_TC19_SF, MAT_TC19_F, MAT_TC19_M, MAT_TC19_P,
         14.816120, 14.816120, 1479.002, 0.0115, 0.0115, 1.433, -1.194, 0.1889764, 1.785, 1.251969),
    ]
    for (m_sf, m_f, m_m, m_p, fyp, fyn, e0, bp, bn, r1, r2, r3, efat, emax) in _tc:
        # SteelMPF: Fy_pos, Fy_neg, E0, b_pos, b_neg, R1, R2, R3 (all ksi→MPa for stress)
        ops.uniaxialMaterial("SteelMPF", m_sf,
                             fyp * ksi, fyn * ksi, e0 * ksi,
                             bp, bn, r1, r2, r3)
        ops.uniaxialMaterial("Fatigue",  m_f,  m_sf, "-E0", efat)
        ops.uniaxialMaterial("MinMax",   m_m,  m_f,  "-min", -1e9, "-max", emax)
        ops.uniaxialMaterial("Parallel", m_p,  MAT_ELASTIC_E3, MAT_ENT, m_m)

    # ── Gusset plate Steel02 ──
    _gusset = [
        (MAT_GUSSET_S1_L, 91.125, 3387.296),  # Left gusset, S1
        (MAT_GUSSET_S1_R, 91.125, 3387.296),  # Right gusset, S1
        (MAT_GUSSET_S2_L, 64.45751, 4572.328),  # Left gusset, S2
        (MAT_GUSSET_S2_R, 64.45751, 4572.328),  # Right gusset, S2
        (MAT_GUSSET_S3_L, 59.71754, 3887.270),  # Left gusset, S3
        (MAT_GUSSET_S3_R, 59.71754, 3887.270),  # Right gusset, S3
    ]
    for (mtag, fy_val, e_val) in _gusset:
        ops.uniaxialMaterial("Steel02", mtag,
                             fy_val * ksi, e_val * ksi, 0.01,
                             20.0, 0.925, 0.15, 0.0005, 0.01, 0.0005, 0.01)

    # ── Steel02 web composites: (Steel02 tag, Fatigue tag, Elastic tag, Parallel tag, eps_fatigue) ──
    _web_sets = [
        (MAT_W12X40_E1_SF, MAT_W12X40_E1_F, MAT_W12X40_E1_EL, MAT_W12X40_E1_P, 0.08733237),
        (MAT_W12X40_E2_SF, MAT_W12X40_E2_F, MAT_W12X40_E2_EL, MAT_W12X40_E2_P, 0.08833755),
        (MAT_W12X40_E3_SF, MAT_W12X40_E3_F, MAT_W12X40_E3_EL, MAT_W12X40_E3_P, 0.08829339),
        (MAT_W12X40_D1_SF, MAT_W12X40_D1_F, MAT_W12X40_D1_EL, MAT_W12X40_D1_P, 0.08733237),
        (MAT_W12X40_D2_SF, MAT_W12X40_D2_F, MAT_W12X40_D2_EL, MAT_W12X40_D2_P, 0.08833755),
        (MAT_W12X40_D3_SF, MAT_W12X40_D3_F, MAT_W12X40_D3_EL, MAT_W12X40_D3_P, 0.08829339),
        (MAT_W12X40_F1_SF, MAT_W12X40_F1_F, MAT_W12X40_F1_EL, MAT_W12X40_F1_P, 0.08733237),
        (MAT_W12X40_F2_SF, MAT_W12X40_F2_F, MAT_W12X40_F2_EL, MAT_W12X40_F2_P, 0.08833755),
        (MAT_W12X40_F3_SF, MAT_W12X40_F3_F, MAT_W12X40_F3_EL, MAT_W12X40_F3_P, 0.08829339),
        (MAT_W12X50_C1_SF, MAT_W12X50_C1_F, MAT_W12X50_C1_EL, MAT_W12X50_C1_P, 0.09198028),
        (MAT_W12X50_C2_SF, MAT_W12X50_C2_F, MAT_W12X50_C2_EL, MAT_W12X50_C2_P, 0.09303896),
        (MAT_W12X50_C3_SF, MAT_W12X50_C3_F, MAT_W12X50_C3_EL, MAT_W12X50_C3_P, 0.09299244),
        (MAT_W12X50_D4_SF, MAT_W12X50_D4_F, MAT_W12X50_D4_EL, MAT_W12X50_D4_P, 0.09198028),
        (MAT_W12X50_D5_SF, MAT_W12X50_D5_F, MAT_W12X50_D5_EL, MAT_W12X50_D5_P, 0.09303896),
        (MAT_W12X50_D6_SF, MAT_W12X50_D6_F, MAT_W12X50_D6_EL, MAT_W12X50_D6_P, 0.09299244),
        (MAT_W12X40_C4_SF, MAT_W12X40_C4_F, MAT_W12X40_C4_EL, MAT_W12X40_C4_P, 0.08733237),
        (MAT_W12X40_C5_SF, MAT_W12X40_C5_F, MAT_W12X40_C5_EL, MAT_W12X40_C5_P, 0.08833755),
        (MAT_W12X40_C6_SF, MAT_W12X40_C6_F, MAT_W12X40_C6_EL, MAT_W12X40_C6_P, 0.08829339),
        (MAT_W12X35_FS1_SF, MAT_W12X35_FS1_F, MAT_W12X35_FS1_EL, MAT_W12X35_FS1_P, 0.08743977),
        (MAT_W12X35_FS2_SF, MAT_W12X35_FS2_F, MAT_W12X35_FS2_EL, MAT_W12X35_FS2_P, 0.08856654),
        (MAT_W12X35_FS3_SF, MAT_W12X35_FS3_F, MAT_W12X35_FS3_EL, MAT_W12X35_FS3_P, 0.08853455),
        (MAT_W12X35_CS1_SF, MAT_W12X35_CS1_F, MAT_W12X35_CS1_EL, MAT_W12X35_CS1_P, 0.08743977),
        (MAT_W12X35_CS2_SF, MAT_W12X35_CS2_F, MAT_W12X35_CS2_EL, MAT_W12X35_CS2_P, 0.08856654),
        (MAT_W12X35_CS3_SF, MAT_W12X35_CS3_F, MAT_W12X35_CS3_EL, MAT_W12X35_CS3_P, 0.08853455),
        (MAT_W12X35_F4_SF,  MAT_W12X35_F4_F,  MAT_W12X35_F4_EL,  MAT_W12X35_F4_P,  0.09060927),
        (MAT_W12X35_F5_SF,  MAT_W12X35_F5_F,  MAT_W12X35_F5_EL,  MAT_W12X35_F5_P,  0.09177688),
        (MAT_W12X35_F6_SF,  MAT_W12X35_F6_F,  MAT_W12X35_F6_EL,  MAT_W12X35_F6_P,  0.09174373),
    ]
    for (ms, mf, mel, mp, eps_f) in _web_sets:
        ops.uniaxialMaterial("Steel02", ms,
                             55.0 * ksi, E0, 0.001, 20.0, 0.925, 0.25,
                             0.01, 1.0, 0.02, 1.0)
        ops.uniaxialMaterial("Fatigue",  mf,  ms,  "-E0", eps_f, "-m", -0.3)
        ops.uniaxialMaterial("Elastic",  mel, 0.029 * ksi)
        ops.uniaxialMaterial("Parallel", mp,  mf, mel)

    # ── IMK Bilin springs (K0 in N-mm/rad, My in N-mm) ──
    _kipin_Nmm = 4448.22 * 25.4  # 1 kip-in = 112985 N-mm
    _bilin = [
        # (tag, K0, asP, asN, MyP, MyN, LamS, LamC, LamA, LamK,
        #  cS, cC, cA, cK, th_pP, th_pN, th_pcP, th_pcN, ResP, ResN, th_uP, th_uN, DP, DN)
        # W12X50(S) — 6 variants for different connection locations
        (110, 2.178038e6, 0.001471526, 0.001471526, 2260.601, -2260.601,
         21.43095, 21.43095, 21.43095, 21.43095,
         1.0, 1.0, 1.0, 1.0, 0.07157060, 0.07157060, 0.2246953, 0.2246953,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (111, 4.574413e6, 0.001330887, 0.001330887, 3341.163, -3341.163,
         21.43095, 21.43095, 21.43095, 21.43095,
         1.0, 1.0, 1.0, 1.0, 0.05561128, 0.05561128, 0.2246953, 0.2246953,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (112, 4.564648e6, 0.001656802, 0.001656802, 4140.186, -4140.186,
         21.43095, 21.43095, 21.43095, 21.43095,
         1.0, 1.0, 1.0, 1.0, 0.05565171, 0.05565171, 0.2246953, 0.2246953,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (113, 5.080611e6, 0.0004025521, 0.0004025521, 1093.097, -1093.097,
         21.43095, 21.43095, 21.43095, 21.43095,
         1.0, 1.0, 1.0, 1.0, 0.05366184, 0.05366184, 0.2246953, 0.2246953,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (114, 5.046352e6, 0.001115163, 0.001115163, 2993.396, -2993.396,
         21.43095, 21.43095, 21.43095, 21.43095,
         1.0, 1.0, 1.0, 1.0, 0.05378542, 0.05378542, 0.2246953, 0.2246953,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (115, 5.000829e6, 0.001558444, 0.001558444, 4140.186, -4140.186,
         21.43095, 21.43095, 21.43095, 21.43095,
         1.0, 1.0, 1.0, 1.0, 0.05395140, 0.05395140, 0.2246953, 0.2246953,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        # W12X35(S) — 3 variants
        (176, 1.595933e6, 0.001773463, 0.001773463, 1735.475, -1735.475,
         14.33851, 14.33851, 14.33851, 14.33851,
         1.0, 1.0, 1.0, 1.0, 0.06240454, 0.06240454, 0.1884644, 0.1884644,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (177, 3.371384e6, 0.001515207, 0.001515207, 2435.205, -2435.205,
         14.33851, 14.33851, 14.33851, 14.33851,
         1.0, 1.0, 1.0, 1.0, 0.04839343, 0.04839343, 0.1884644, 0.1884644,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (178, 3.366183e6, 0.001833096, 0.001833096, 2933.920, -2933.920,
         14.33851, 14.33851, 14.33851, 14.33851,
         1.0, 1.0, 1.0, 1.0, 0.04841884, 0.04841884, 0.1884644, 0.1884644,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        # W12X40(S) — 3 variants
        (179, 1.719128e6, 0.001824842, 0.001824842, 2025.263, -2025.263,
         14.08769, 14.08769, 14.08769, 14.08769,
         1.0, 1.0, 1.0, 1.0, 0.06573573, 0.06573573, 0.1690638, 0.1690638,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (180, 3.631632e6, 0.001513149, 0.001513149, 2759.516, -2759.516,
         14.08769, 14.08769, 14.08769, 14.08769,
         1.0, 1.0, 1.0, 1.0, 0.05097670, 0.05097670, 0.1690638, 0.1690638,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (181, 3.626029e6, 0.001807009, 0.001807009, 3282.567, -3282.567,
         14.08769, 14.08769, 14.08769, 14.08769,
         1.0, 1.0, 1.0, 1.0, 0.05100346, 0.05100346, 0.1690638, 0.1690638,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        # W16X57(S) — 4 variants
        (218, 3.524233e6, 0.003498436, 0.003498436, 6352.500, -6352.500,
         18.73781, 18.73781, 18.73781, 18.73781,
         1.0, 1.0, 1.0, 1.0, 0.05332612, 0.05332612, 0.2226478, 0.2226478,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (220, 3.575939e6, 0.003463808, 0.003463808, 6352.500, -6352.500,
         18.73781, 18.73781, 18.73781, 18.73781,
         1.0, 1.0, 1.0, 1.0, 0.05306269, 0.05306269, 0.2226478, 0.2226478,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (222, 3.628844e6, 0.003429249, 0.003429249, 6352.500, -6352.500,
         18.73781, 18.73781, 18.73781, 18.73781,
         1.0, 1.0, 1.0, 1.0, 0.05279839, 0.05279839, 0.2226478, 0.2226478,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (224, 3.575608e6, 0.003464026, 0.003464026, 6352.500, -6352.500,
         18.73781, 18.73781, 18.73781, 18.73781,
         1.0, 1.0, 1.0, 1.0, 0.05306436, 0.05306436, 0.2226478, 0.2226478,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        # W16X26(S) — 4 variants
        (219, 1.399464e6, 0.004667470, 0.004667470, 2674.100, -2674.100,
         6.817471, 6.817471, 6.817471, 6.817471,
         1.0, 1.0, 1.0, 1.0, 0.04284952, 0.04284952, 0.1136469, 0.1136469,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (221, 1.419997e6, 0.004620753, 0.004620753, 2674.100, -2674.100,
         6.817471, 6.817471, 6.817471, 6.817471,
         1.0, 1.0, 1.0, 1.0, 0.04263785, 0.04263785, 0.1136469, 0.1136469,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (223, 1.441006e6, 0.004574142, 0.004574142, 2674.100, -2674.100,
         6.817471, 6.817471, 6.817471, 6.817471,
         1.0, 1.0, 1.0, 1.0, 0.04242547, 0.04242547, 0.1136469, 0.1136469,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (225, 1.419866e6, 0.004621048, 0.004621048, 2674.100, -2674.100,
         6.817471, 6.817471, 6.817471, 6.817471,
         1.0, 1.0, 1.0, 1.0, 0.04263919, 0.04263919, 0.1136469, 0.1136469,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        # W16X40(S) — 2 variants
        (226, 6.298933e6, 0.001139212, 0.001139212, 2357.544, -2357.544,
         9.689555, 9.689555, 9.689555, 9.689555,
         1.0, 1.0, 1.0, 1.0, 0.03322828, 0.03322828, 0.1415743, 0.1415743,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (227, 6.200450e6, 0.001374114, 0.001374114, 2807.720, -2807.720,
         9.689555, 9.689555, 9.689555, 9.689555,
         1.0, 1.0, 1.0, 1.0, 0.03340679, 0.03340679, 0.1415743, 0.1415743,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        # W12X26(S) — 1 variant
        (228, 2.188655e6, 0.001758797, 0.001758797, 1690.354, -1690.354,
         8.407581, 8.407581, 8.407581, 8.407581,
         1.0, 1.0, 1.0, 1.0, 0.04468449, 0.04468449, 0.1282892, 0.1282892,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        # W18X60(S) — 4 variants
        (229, 4.710795e6, 0.003716595, 0.003716595, 7441.500, -7441.500,
         14.39241, 14.39241, 14.39241, 14.39241,
         1.0, 1.0, 1.0, 1.0, 0.04408281, 0.04408281, 0.1843210, 0.1843210,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (231, 4.639971e6, 0.003755342, 0.003755342, 7441.500, -7441.500,
         14.39241, 14.39241, 14.39241, 14.39241,
         1.0, 1.0, 1.0, 1.0, 0.04431045, 0.04431045, 0.1843210, 0.1843210,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (233, 4.574576e6, 0.003792028, 0.003792028, 7441.500, -7441.500,
         14.39241, 14.39241, 14.39241, 14.39241,
         1.0, 1.0, 1.0, 1.0, 0.04452481, 0.04452481, 0.1843210, 0.1843210,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (235, 4.640000e6, 0.003755326, 0.003755326, 7441.500, -7441.500,
         14.39241, 14.39241, 14.39241, 14.39241,
         1.0, 1.0, 1.0, 1.0, 0.04431035, 0.04431035, 0.1843210, 0.1843210,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        # W18X35(S) — 4 variants
        (230, 2.441571e6, 0.004429667, 0.004429667, 4023.250, -4023.250,
         7.947889, 7.947889, 7.947889, 7.947889,
         1.0, 1.0, 1.0, 1.0, 0.03884727, 0.03884727, 0.1253297, 0.1253297,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (232, 2.404863e6, 0.004476170, 0.004476170, 4023.250, -4023.250,
         7.947889, 7.947889, 7.947889, 7.947889,
         1.0, 1.0, 1.0, 1.0, 0.03904787, 0.03904787, 0.1253297, 0.1253297,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (234, 2.370970e6, 0.004520205, 0.004520205, 4023.250, -4023.250,
         7.947889, 7.947889, 7.947889, 7.947889,
         1.0, 1.0, 1.0, 1.0, 0.03923677, 0.03923677, 0.1253297, 0.1253297,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
        (236, 2.404878e6, 0.004476151, 0.004476151, 4023.250, -4023.250,
         7.947889, 7.947889, 7.947889, 7.947889,
         1.0, 1.0, 1.0, 1.0, 0.03904778, 0.03904778, 0.1253297, 0.1253297,
         0.40, 0.40, 0.12, 0.12, 1.0, 1.0),
    ]
    for bt in _bilin:
        tag = bt[0]
        K0 = bt[1] * _kipin_Nmm
        MyP = bt[4] * _kipin_Nmm
        MyN = bt[5] * _kipin_Nmm
        ops.uniaxialMaterial("IMKBilin", tag,
                             K0, bt[2], bt[3], MyP, MyN,
                             bt[6], bt[7], bt[8], bt[9],
                             bt[10], bt[11], bt[12], bt[13],
                             bt[14], bt[15], bt[16], bt[17],
                             bt[18], bt[19], bt[20], bt[21],
                             bt[22], bt[23])

    # ── Brace Steel02 composites (BR1-BR6) ──
    _brace_sets = [
        (MAT_BR1_SF, MAT_BR1_F, MAT_BR1_EL, MAT_BR1_P, 0.02259786),
        (MAT_BR2_SF, MAT_BR2_F, MAT_BR2_EL, MAT_BR2_P, 0.02297707),
        (MAT_BR3_SF, MAT_BR3_F, MAT_BR3_EL, MAT_BR3_P, 0.01799337),
        (MAT_BR4_SF, MAT_BR4_F, MAT_BR4_EL, MAT_BR4_P, 0.02259786),
        (MAT_BR5_SF, MAT_BR5_F, MAT_BR5_EL, MAT_BR5_P, 0.02297707),
        (MAT_BR6_SF, MAT_BR6_F, MAT_BR6_EL, MAT_BR6_P, 0.01799337),
    ]
    for (ms, mf, mel, mp, eps_f) in _brace_sets:
        ops.uniaxialMaterial("Steel02", ms,
                             64.4 * ksi, E0, 0.001, 22.0, 0.925, 0.25,
                             0.03, 1.0, 0.02, 1.0)
        ops.uniaxialMaterial("Fatigue",  mf,  ms,  "-E0", eps_f, "-m", -0.3)
        ops.uniaxialMaterial("Elastic",  mel, 0.029 * ksi)
        ops.uniaxialMaterial("Parallel", mp,  mf, mel)


# ── 7. SECTIONS ────────────────────────────────────────────────────────────────
def define_sections():
    """Define all fiber sections, aggregator sections, W-shapes, and HSS sections."""
    _in2_mm2 = inch * inch  # in² → mm²

    # ── Manual fiber sections for bolted angle connections ──
    # Section 1: W16X57 GRAV B1L
    ops.section("Fiber", SEC_FIBER_B1L_W16X57)
    ops.layer("straight", MAT_TC19_P, 3, 0.708333 * _in2_mm2,
              -3.0 * inch, 0.0, 3.0 * inch, 0.0)  # B2C-TC19
    ops.fiber(-8.2 * inch, 0.0, 0.89 * _in2_mm2, MAT_B2C_CONTACT)   # B2C-BFC
    ops.fiber(8.2 * inch, 0.0, 0.89 * _in2_mm2, MAT_B2C_CONTACT)    # B2C-TFC
    ops.section("Aggregator", SEC_AGG_B1L, MAT_ELASTIC_E3, "Vy", "-section", SEC_FIBER_B1L_W16X57)

    # Section 3: W16X26 GRAV B3L
    ops.section("Fiber", SEC_FIBER_B3L_W16X26)
    ops.layer("straight", MAT_TC19_P, 3, 0.708333 * _in2_mm2,
              -3.0 * inch, 0.0, 3.0 * inch, 0.0)
    ops.fiber(-7.85 * inch, 0.0, 0.6875 * _in2_mm2, MAT_B2C_CONTACT)
    ops.fiber(7.85 * inch, 0.0, 0.6875 * _in2_mm2, MAT_B2C_CONTACT)
    ops.section("Aggregator", SEC_AGG_B3L, MAT_ELASTIC_E3, "Vy", "-section", SEC_FIBER_B3L_W16X26)

    # Section 5: W16X40 BR1 B19L
    ops.section("Fiber", SEC_FIBER_B19L_W16X40_BR1)
    ops.layer("straight", MAT_TC3_P, 2, 0.6875 * _in2_mm2,
              12.375 * inch, 0.0, 15.375 * inch, 0.0)  # G2C-TC3
    ops.layer("straight", MAT_TC3_P, 3, 0.708333 * _in2_mm2,
              -1.0 * inch, 0.0, 5.0 * inch, 0.0)       # B2C-TC3
    ops.fiber(-8.0 * inch, 0.0, 0.875 * _in2_mm2, MAT_B2C_CONTACT)
    ops.fiber(23.5 * inch, 0.0, 0.09375 * _in2_mm2, MAT_G2C_CONTACT)
    ops.section("Aggregator", SEC_AGG_B19L, MAT_ELASTIC_E3, "Vy", "-section", SEC_FIBER_B19L_W16X40_BR1)

    # Section 7: W16X40 BR1 B20L
    ops.section("Fiber", SEC_FIBER_B20L_W16X40_BR1)
    ops.layer("straight", MAT_TC3_P, 2, 0.6875 * _in2_mm2,
              11.875 * inch, 0.0, 14.875 * inch, 0.0)  # G2C-TC3
    ops.layer("straight", MAT_TC3_P, 3, 0.708333 * _in2_mm2,
              -1.0 * inch, 0.0, 5.0 * inch, 0.0)       # B2C-TC3
    ops.fiber(-8.0 * inch, 0.0, 0.875 * _in2_mm2, MAT_B2C_CONTACT)
    ops.fiber(22.5 * inch, 0.0, 0.09375 * _in2_mm2, MAT_G2C_CONTACT)
    ops.section("Aggregator", SEC_AGG_B20L, MAT_ELASTIC_E3, "Vy", "-section", SEC_FIBER_B20L_W16X40_BR1)

    # Section 9: W12X26 BR1 B21L
    ops.section("Fiber", SEC_FIBER_B21L_W12X26)
    ops.layer("straight", MAT_TC3_P, 3, 0.708333 * _in2_mm2,
              -3.0 * inch, 0.0, 3.0 * inch, 0.0)  # B2C-TC3
    ops.fiber(-6.1 * inch, 0.0, 0.81125 * _in2_mm2, MAT_B2C_CONTACT)
    ops.fiber(6.1 * inch, 0.0, 0.81125 * _in2_mm2, MAT_B2C_CONTACT)
    ops.section("Aggregator", SEC_AGG_B21L, MAT_ELASTIC_E3, "Vy", "-section", SEC_FIBER_B21L_W12X26)

    # Section 11: W18X60 GRAV B31L
    ops.section("Fiber", SEC_FIBER_B31L_W18X60)
    ops.layer("straight", MAT_TC19_P, 3, 0.708333 * _in2_mm2,
              -3.0 * inch, 0.0, 3.0 * inch, 0.0)  # B2C-TC19
    ops.fiber(-9.1 * inch, 0.0, 0.82 * _in2_mm2, MAT_B2C_CONTACT)
    ops.fiber(9.1 * inch, 0.0, 0.82 * _in2_mm2, MAT_B2C_CONTACT)
    ops.section("Aggregator", SEC_AGG_B31L, MAT_ELASTIC_E3, "Vy", "-section", SEC_FIBER_B31L_W18X60)

    # Section 13: W18X35 GRAV B33L
    ops.section("Fiber", SEC_FIBER_B33L_W18X35)
    ops.layer("straight", MAT_TC19_P, 3, 0.708333 * _in2_mm2,
              -3.0 * inch, 0.0, 3.0 * inch, 0.0)  # B2C-TC19
    ops.fiber(-8.85 * inch, 0.0, 0.75 * _in2_mm2, MAT_B2C_CONTACT)
    ops.fiber(8.85 * inch, 0.0, 0.75 * _in2_mm2, MAT_B2C_CONTACT)
    ops.section("Aggregator", SEC_AGG_B33L, MAT_ELASTIC_E3, "Vy", "-section", SEC_FIBER_B33L_W18X35)

    # ── W-shape fiber sections (weak-axis columns) ──
    # W12X40 (d=11.9, bf=8.01, tf=0.515, tw=0.295 in)
    _w12x40 = (11.9 * inch, 8.01 * inch, 0.515 * inch, 0.295 * inch, 6, 2, 6, 2, 0)
    _section_W(SEC_W12X40_E1,  MAT_W12X40_E1_P, *_w12x40)
    _section_W(SEC_W12X40_E2,  MAT_W12X40_E2_P, *_w12x40)
    _section_W(SEC_W12X40_E3,  MAT_W12X40_E3_P, *_w12x40)
    _section_W(SEC_W12X40_E6,  MAT_W12X40_D1_P, *_w12x40)
    _section_W(SEC_W12X40_E6b, MAT_W12X40_D2_P, *_w12x40)
    _section_W(SEC_W12X40_E6c, MAT_W12X40_D3_P, *_w12x40)
    _section_W(SEC_W12X40_D1,  MAT_W12X40_F1_P, *_w12x40)
    _section_W(SEC_W12X40_D1b, MAT_W12X40_F2_P, *_w12x40)
    _section_W(SEC_W12X40_D1c, MAT_W12X40_F3_P, *_w12x40)
    # W12X50 (d=12.2, bf=8.08, tf=0.64, tw=0.37 in)
    _w12x50 = (12.2 * inch, 8.08 * inch, 0.64 * inch, 0.37 * inch, 6, 2, 6, 2, 0)
    _section_W(SEC_W12X50_D2,  MAT_W12X50_C1_P, *_w12x50)
    _section_W(SEC_W12X50_D2b, MAT_W12X50_C2_P, *_w12x50)
    _section_W(SEC_W12X50_D2c, MAT_W12X50_C3_P, *_w12x50)
    _section_W(SEC_W12X50_D5,  MAT_W12X50_D4_P, *_w12x50)
    _section_W(SEC_W12X50_D5b, MAT_W12X50_D5_P, *_w12x50)
    _section_W(SEC_W12X50_D5c, MAT_W12X50_D6_P, *_w12x50)
    # W12X40 continued (C/F lines)
    _section_W(SEC_W12X40_D6,  MAT_W12X40_C4_P, *_w12x40)
    _section_W(SEC_W12X40_D6b, MAT_W12X40_C5_P, *_w12x40)
    _section_W(SEC_W12X40_D6c, MAT_W12X40_C6_P, *_w12x40)
    _section_W(SEC_W12X40_F3,  MAT_W12X35_FS1_P, *_w12x40)
    _section_W(SEC_W12X40_F3b, MAT_W12X35_FS2_P, *_w12x40)
    _section_W(SEC_W12X40_F3c, MAT_W12X35_FS3_P, *_w12x40)
    # W12X40 continued
    _section_W(SEC_W12X40_F4,  MAT_W12X35_CS1_P, *_w12x40)
    _section_W(SEC_W12X40_F4b, MAT_W12X35_CS2_P, *_w12x40)
    _section_W(SEC_W12X40_F4c, MAT_W12X35_CS3_P, *_w12x40)
    # W12X35 (d=12.5, bf=6.56, tf=0.52, tw=0.30 in)
    _w12x35 = (12.5 * inch, 6.56 * inch, 0.52 * inch, 0.30 * inch, 6, 2, 6, 2, 0)
    _section_W(SEC_W12X35_F6,  MAT_W12X35_F4_P,  *_w12x35)
    _section_W(SEC_W12X35_F6b, MAT_W12X35_F5_P,  *_w12x35)
    _section_W(SEC_W12X35_F6c, MAT_W12X35_F6_P,  *_w12x35)

    # ── HSS brace fiber sections ──
    _section_HSS(SEC_HSS9X9_BR1, MAT_BR1_P, 9.0 * inch, 0.174 * inch, 10, 4, 10, 4)
    _section_HSS(SEC_HSS8X8_BR2, MAT_BR2_P, 8.0 * inch, 0.174 * inch, 10, 4, 10, 4)
    _section_HSS(SEC_HSS7X7_BR3, MAT_BR3_P, 7.0 * inch, 0.116 * inch, 10, 4, 10, 4)
    _section_HSS(SEC_HSS9X9_BR4, MAT_BR4_P, 9.0 * inch, 0.174 * inch, 10, 4, 10, 4)
    _section_HSS(SEC_HSS8X8_BR5, MAT_BR5_P, 8.0 * inch, 0.174 * inch, 10, 4, 10, 4)
    _section_HSS(SEC_HSS7X7_BR6, MAT_BR6_P, 7.0 * inch, 0.116 * inch, 10, 4, 10, 4)


# ── 8. NODES ───────────────────────────────────────────────────────────────────
def define_nodes():
    """Define all 877 nodes with coordinates converted from inches to mm."""
    nodes = []

    # Grid C — left braced frame columns (nodes 1-24)
    x0 = 2160.0
    for i, y in enumerate([0.0, 28.63333, 57.26667, 85.9, 114.5333, 143.1667,
                           171.8, 180.0, 188.2, 215.4667, 242.7333, 270.0,
                           297.2667, 324.5333, 351.8, 360.0, 368.2, 395.525,
                           422.85, 450.175, 477.5, 504.825, 532.15, 540.0]):
        nodes.append((1 + i, x0, y))
    # Grid D interior columns (nodes 25-84)
    x0 = 2580.0
    for i, (x, y) in enumerate([
        (0.0, 0.0), (0.0, 171.8), (0.0, 171.8), (0.0, 180.0), (0.0, 188.2),
        (0.0, 188.2), (0.0, 351.8), (0.0, 351.8), (0.0, 360.0), (0.0, 368.2),
        (0.0, 368.2), (0.0, 532.15), (0.0, 532.15), (0.0, 540.0),
    ]):
        nodes.append((25 + i, x0 + x, y))
    x0 = 3000.0
    for i, (x, y) in enumerate([
        (0.0, 0.0), (0.0, 24.5), (0.0, 24.5), (0.0, 171.8), (0.0, 171.8),
        (0.0, 180.0), (0.0, 203.5), (0.0, 203.5), (0.0, 351.8), (0.0, 351.8),
        (0.0, 360.0), (0.0, 382.5), (0.0, 382.5), (0.0, 532.15),
        (0.0, 532.15), (0.0, 540.0),
    ]):
        nodes.append((39 + i, x0 + x, y))
    x0 = 3420.0
    for i, (x, y) in enumerate([
        (0.0, 0.0), (0.0, 24.5), (0.0, 24.5), (0.0, 171.8), (0.0, 171.8),
        (0.0, 180.0), (0.0, 203.5), (0.0, 203.5), (0.0, 351.8), (0.0, 351.8),
        (0.0, 360.0), (0.0, 382.5), (0.0, 382.5), (0.0, 532.15),
        (0.0, 532.15), (0.0, 540.0),
    ]):
        nodes.append((55 + i, x0 + x, y))
    x0 = 3840.0
    for i, (x, y) in enumerate([
        (0.0, 0.0), (0.0, 171.8), (0.0, 171.8), (0.0, 180.0), (0.0, 188.2),
        (0.0, 188.2), (0.0, 351.8), (0.0, 351.8), (0.0, 360.0), (0.0, 368.2),
        (0.0, 368.2), (0.0, 532.15), (0.0, 532.15), (0.0, 540.0),
    ]):
        nodes.append((71 + i, x0 + x, y))

    # Grid E — right braced frame (nodes 85-232)
    _e_col_y = [0.0, 28.63333, 57.26667, 85.9, 114.5333, 143.1667,
                171.8, 180.0, 188.2, 215.4667, 242.7333, 270.0,
                297.2667, 324.5333, 351.8, 360.0, 368.2, 395.525,
                422.85, 450.175, 477.5, 504.825, 532.15, 540.0]
    # Braced-frame columns: 24 nodes each
    _e_brace_cols = [(4260.0, 85), (4320.0, 109), (4740.0, 133),
                     (6000.0, 185), (6420.0, 209)]
    for cx, base_tag in _e_brace_cols:
        for i, y in enumerate(_e_col_y):
            nodes.append((base_tag + i, cx, y))
    # Interior columns at x=5160 (nodes 157-170) and x=5580 (nodes 171-184): 14 nodes
    _e_int_y = [0.0, 171.8, 171.8, 180.0, 188.2, 188.2,
                351.8, 351.8, 360.0, 368.2, 368.2, 532.15, 532.15, 540.0]
    for cx, base_tag in [(5160.0, 157), (5580.0, 171)]:
        for i, y in enumerate(_e_int_y):
            nodes.append((base_tag + i, cx, y))

    # Grid F — pinned leaner (nodes 233-346)
    # Columns at x=840, x=1260, x=2100 use 24-node braced pattern
    _f_col_y_brace = [0.0, 28.48333, 56.96667, 85.45, 113.9333, 142.4167,
                      170.9, 180.0, 189.1, 216.0667, 243.0333, 270.0,
                      296.9667, 323.9333, 350.9, 360.0, 369.1, 396.1083,
                      423.1167, 450.125, 477.1333, 504.1417, 531.15, 540.0]
    _f_brace_cols = [(840.0, 261), (1260.0, 285), (2100.0, 323)]
    for cx, base_tag in _f_brace_cols:
        for i, y in enumerate(_f_col_y_brace):
            nodes.append((base_tag + i, cx, y))
    # Columns at x=0, x=420, x=1680 use 14-node leaner pattern
    _f_col_y_leaner = [0.0, 170.9, 170.9, 180.0, 189.1, 189.1,
                       350.9, 350.9, 360.0, 369.1, 369.1, 531.15, 531.15, 540.0]
    for cx, base_tag in [(0.0, 233), (420.0, 247), (1680.0, 309)]:
        for i, y in enumerate(_f_col_y_leaner):
            nodes.append((base_tag + i, cx, y))

    # Braced-frame left-side connection slave nodes (nodes 347-376)
    _conn_left = [
        (4320.148, 180.0, 347), (4320.148, 180.0, 348), (4320.148, 180.0, 349),
        (4324.148, 180.0, 350), (4324.148, 180.0, 351),
        (4735.815, 180.0, 352), (4735.815, 180.0, 353),
        (4739.815, 180.0, 354), (4739.815, 180.0, 355), (4739.815, 180.0, 356),
        (4320.148, 360.0, 357), (4320.148, 360.0, 358), (4320.148, 360.0, 359),
        (4324.148, 360.0, 360), (4324.148, 360.0, 361),
        (4735.815, 360.0, 362), (4735.815, 360.0, 363),
        (4739.815, 360.0, 364), (4739.815, 360.0, 365), (4739.815, 360.0, 366),
        (4320.148, 540.0, 367), (4320.148, 540.0, 368), (4320.148, 540.0, 369),
        (4324.148, 540.0, 370), (4324.148, 540.0, 371),
        (4735.815, 540.0, 372), (4735.815, 540.0, 373),
        (4739.815, 540.0, 374), (4739.815, 540.0, 375), (4739.815, 540.0, 376),
    ]
    for x, y, t in _conn_left:
        nodes.append((t, x, y))

    # E-grid right-side connection slave nodes (nodes 377-406)
    _conn_right_E = [
        (4740.185, 180.0, 377), (4740.185, 180.0, 378), (4740.185, 180.0, 379),
        (4744.185, 180.0, 380), (4744.185, 180.0, 381),
        (5149.9, 180.0, 382), (5149.9, 180.0, 383),
        (5153.9, 180.0, 384), (5153.9, 180.0, 385), (5153.9, 180.0, 386),
        (4740.185, 360.0, 387), (4740.185, 360.0, 388), (4740.185, 360.0, 389),
        (4744.185, 360.0, 390), (4744.185, 360.0, 391),
        (5149.9, 360.0, 392), (5149.9, 360.0, 393),
        (5153.9, 360.0, 394), (5153.9, 360.0, 395), (5153.9, 360.0, 396),
        (4740.185, 540.0, 397), (4740.185, 540.0, 398), (4740.185, 540.0, 399),
        (4744.185, 540.0, 400), (4744.185, 540.0, 401),
        (5149.9, 540.0, 402), (5149.9, 540.0, 403),
        (5153.9, 540.0, 404), (5153.9, 540.0, 405), (5153.9, 540.0, 406),
    ]
    for x, y, t in _conn_right_E:
        nodes.append((t, x, y))

    # S3-level and S4-level connections (nodes 407-496)
    _conn_mid = [
        (5166.1, 180.0, 407), (5166.1, 180.0, 408), (5166.1, 180.0, 409),
        (5170.1, 180.0, 410), (5170.1, 180.0, 411),
        (5569.9, 180.0, 412), (5569.9, 180.0, 413),
        (5573.9, 180.0, 414), (5573.9, 180.0, 415), (5573.9, 180.0, 416),
        (5166.1, 360.0, 417), (5166.1, 360.0, 418), (5166.1, 360.0, 419),
        (5170.1, 360.0, 420), (5170.1, 360.0, 421),
        (5569.9, 360.0, 422), (5569.9, 360.0, 423),
        (5573.9, 360.0, 424), (5573.9, 360.0, 425), (5573.9, 360.0, 426),
        (5166.1, 540.0, 427), (5166.1, 540.0, 428), (5166.1, 540.0, 429),
        (5170.1, 540.0, 430), (5170.1, 540.0, 431),
        (5569.9, 540.0, 432), (5569.9, 540.0, 433),
        (5573.9, 540.0, 434), (5573.9, 540.0, 435), (5573.9, 540.0, 436),
        (5586.1, 180.0, 437), (5586.1, 180.0, 438), (5586.1, 180.0, 439),
        (5590.1, 180.0, 440), (5590.1, 180.0, 441),
        (5995.815, 180.0, 442), (5995.815, 180.0, 443),
        (5999.815, 180.0, 444), (5999.815, 180.0, 445), (5999.815, 180.0, 446),
        (5586.1, 360.0, 447), (5586.1, 360.0, 448), (5586.1, 360.0, 449),
        (5590.1, 360.0, 450), (5590.1, 360.0, 451),
        (5995.815, 360.0, 452), (5995.815, 360.0, 453),
        (5999.815, 360.0, 454), (5999.815, 360.0, 455), (5999.815, 360.0, 456),
        (5586.1, 540.0, 457), (5586.1, 540.0, 458), (5586.1, 540.0, 459),
        (5590.1, 540.0, 460), (5590.1, 540.0, 461),
        (5995.815, 540.0, 462), (5995.815, 540.0, 463),
        (5999.815, 540.0, 464), (5999.815, 540.0, 465), (5999.815, 540.0, 466),
        (6000.185, 180.0, 467), (6000.185, 180.0, 468), (6000.185, 180.0, 469),
        (6004.185, 180.0, 470), (6004.185, 180.0, 471),
        (6415.852, 180.0, 472), (6415.852, 180.0, 473),
        (6419.852, 180.0, 474), (6419.852, 180.0, 475), (6419.852, 180.0, 476),
        (6000.185, 360.0, 477), (6000.185, 360.0, 478), (6000.185, 360.0, 479),
        (6004.185, 360.0, 480), (6004.185, 360.0, 481),
        (6415.852, 360.0, 482), (6415.852, 360.0, 483),
        (6419.852, 360.0, 484), (6419.852, 360.0, 485), (6419.852, 360.0, 486),
        (6000.185, 540.0, 487), (6000.185, 540.0, 488), (6000.185, 540.0, 489),
        (6004.185, 540.0, 490), (6004.185, 540.0, 491),
        (6415.852, 540.0, 492), (6415.852, 540.0, 493),
        (6419.852, 540.0, 494), (6419.852, 540.0, 495), (6419.852, 540.0, 496),
    ]
    for x, y, t in _conn_mid:
        nodes.append((t, x, y))

    # C-grid left-side connection slave nodes (nodes 497-526)
    _conn_C = [
        (2160.148, 180.0, 497), (2160.148, 180.0, 498), (2160.148, 180.0, 499),
        (2164.148, 180.0, 500), (2164.148, 180.0, 501),
        (2569.9, 180.0, 502), (2569.9, 180.0, 503),
        (2573.9, 180.0, 504), (2573.9, 180.0, 505), (2573.9, 180.0, 506),
        (2160.148, 360.0, 507), (2160.148, 360.0, 508), (2160.148, 360.0, 509),
        (2164.148, 360.0, 510), (2164.148, 360.0, 511),
        (2569.9, 360.0, 512), (2569.9, 360.0, 513),
        (2573.9, 360.0, 514), (2573.9, 360.0, 515), (2573.9, 360.0, 516),
        (2160.148, 540.0, 517), (2160.148, 540.0, 518), (2160.148, 540.0, 519),
        (2164.148, 540.0, 520), (2164.148, 540.0, 521),
        (2569.9, 540.0, 522), (2569.9, 540.0, 523),
        (2573.9, 540.0, 524), (2573.9, 540.0, 525), (2573.9, 540.0, 526),
    ]
    for x, y, t in _conn_C:
        nodes.append((t, x, y))

    # D-grid connection slave nodes (nodes 527-571)
    _conn_D = [
        (3006.1, 180.0, 527), (3006.1, 180.0, 528), (3006.1, 180.0, 529),
        (3025.6, 180.0, 530), (3025.6, 180.0, 531),
        (3183.0, 180.0, 532), (3183.0, 180.0, 533),
        (3210.0, 180.0, 534), (3237.0, 180.0, 535), (3237.0, 180.0, 536),
        (3394.4, 180.0, 537), (3394.4, 180.0, 538),
        (3413.9, 180.0, 539), (3413.9, 180.0, 540), (3413.9, 180.0, 541),
        (3006.1, 360.0, 542), (3006.1, 360.0, 543), (3006.1, 360.0, 544),
        (3024.6, 360.0, 545), (3024.6, 360.0, 546),
        (3184.5, 360.0, 547), (3184.5, 360.0, 548),
        (3210.0, 360.0, 549), (3235.5, 360.0, 550), (3235.5, 360.0, 551),
        (3395.4, 360.0, 552), (3395.4, 360.0, 553),
        (3413.9, 360.0, 554), (3413.9, 360.0, 555), (3413.9, 360.0, 556),
        (3006.1, 540.0, 557), (3006.1, 540.0, 558), (3006.1, 540.0, 559),
        (3010.1, 540.0, 560), (3010.1, 540.0, 561),
        (3188.5, 540.0, 562), (3188.5, 540.0, 563),
        (3210.0, 540.0, 564), (3231.5, 540.0, 565), (3231.5, 540.0, 566),
        (3409.9, 540.0, 567), (3409.9, 540.0, 568),
        (3413.9, 540.0, 569), (3413.9, 540.0, 570), (3413.9, 540.0, 571),
    ]
    for x, y, t in _conn_D:
        nodes.append((t, x, y))

    # D-grid additional connection slave nodes (nodes 572-661)
    _conn_D2 = [
        (2586.1, 180.0, 572), (2586.1, 180.0, 573), (2586.1, 180.0, 574),
        (2590.1, 180.0, 575), (2590.1, 180.0, 576),
        (2989.9, 180.0, 577), (2989.9, 180.0, 578),
        (2993.9, 180.0, 579), (2993.9, 180.0, 580), (2993.9, 180.0, 581),
        (2586.1, 360.0, 582), (2586.1, 360.0, 583), (2586.1, 360.0, 584),
        (2590.1, 360.0, 585), (2590.1, 360.0, 586),
        (2989.9, 360.0, 587), (2989.9, 360.0, 588),
        (2993.9, 360.0, 589), (2993.9, 360.0, 590), (2993.9, 360.0, 591),
        (2586.1, 540.0, 592), (2586.1, 540.0, 593), (2586.1, 540.0, 594),
        (2590.1, 540.0, 595), (2590.1, 540.0, 596),
        (2989.9, 540.0, 597), (2989.9, 540.0, 598),
        (2993.9, 540.0, 599), (2993.9, 540.0, 600), (2993.9, 540.0, 601),
        (3426.1, 180.0, 602), (3426.1, 180.0, 603), (3426.1, 180.0, 604),
        (3430.1, 180.0, 605), (3430.1, 180.0, 606),
        (3829.9, 180.0, 607), (3829.9, 180.0, 608),
        (3833.9, 180.0, 609), (3833.9, 180.0, 610), (3833.9, 180.0, 611),
        (3426.1, 360.0, 612), (3426.1, 360.0, 613), (3426.1, 360.0, 614),
        (3430.1, 360.0, 615), (3430.1, 360.0, 616),
        (3829.9, 360.0, 617), (3829.9, 360.0, 618),
        (3833.9, 360.0, 619), (3833.9, 360.0, 620), (3833.9, 360.0, 621),
        (3426.1, 540.0, 622), (3426.1, 540.0, 623), (3426.1, 540.0, 624),
        (3430.1, 540.0, 625), (3430.1, 540.0, 626),
        (3829.9, 540.0, 627), (3829.9, 540.0, 628),
        (3833.9, 540.0, 629), (3833.9, 540.0, 630), (3833.9, 540.0, 631),
        (3846.1, 180.0, 632), (3846.1, 180.0, 633), (3846.1, 180.0, 634),
        (3850.1, 180.0, 635), (3850.1, 180.0, 636),
        (4255.852, 180.0, 637), (4255.852, 180.0, 638),
        (4259.852, 180.0, 639), (4259.852, 180.0, 640), (4259.852, 180.0, 641),
        (3846.1, 360.0, 642), (3846.1, 360.0, 643), (3846.1, 360.0, 644),
        (3850.1, 360.0, 645), (3850.1, 360.0, 646),
        (4255.852, 360.0, 647), (4255.852, 360.0, 648),
        (4259.852, 360.0, 649), (4259.852, 360.0, 650), (4259.852, 360.0, 651),
        (3846.1, 540.0, 652), (3846.1, 540.0, 653), (3846.1, 540.0, 654),
        (3850.1, 540.0, 655), (3850.1, 540.0, 656),
        (4255.852, 540.0, 657), (4255.852, 540.0, 658),
        (4259.852, 540.0, 659), (4259.852, 540.0, 660), (4259.852, 540.0, 661),
    ]
    for x, y, t in _conn_D2:
        nodes.append((t, x, y))

    # F-grid connection slave nodes (nodes 662-811)
    _conn_F = [
        (6.25, 180.0, 662), (6.25, 180.0, 663), (6.25, 180.0, 664),
        (10.25, 180.0, 665), (10.25, 180.0, 666),
        (410.05, 180.0, 667), (410.05, 180.0, 668),
        (414.05, 180.0, 669), (414.05, 180.0, 670), (414.05, 180.0, 671),
        (6.25, 360.0, 672), (6.25, 360.0, 673), (6.25, 360.0, 674),
        (10.25, 360.0, 675), (10.25, 360.0, 676),
        (410.05, 360.0, 677), (410.05, 360.0, 678),
        (414.05, 360.0, 679), (414.05, 360.0, 680), (414.05, 360.0, 681),
        (6.25, 540.0, 682), (6.25, 540.0, 683), (6.25, 540.0, 684),
        (10.25, 540.0, 685), (10.25, 540.0, 686),
        (410.05, 540.0, 687), (410.05, 540.0, 688),
        (414.05, 540.0, 689), (414.05, 540.0, 690), (414.05, 540.0, 691),
        (425.95, 180.0, 692), (425.95, 180.0, 693), (425.95, 180.0, 694),
        (429.95, 180.0, 695), (429.95, 180.0, 696),
        (835.8525, 180.0, 697), (835.8525, 180.0, 698),
        (839.8525, 180.0, 699), (839.8525, 180.0, 700), (839.8525, 180.0, 701),
        (425.95, 360.0, 702), (425.95, 360.0, 703), (425.95, 360.0, 704),
        (429.95, 360.0, 705), (429.95, 360.0, 706),
        (835.8525, 360.0, 707), (835.8525, 360.0, 708),
        (839.8525, 360.0, 709), (839.8525, 360.0, 710), (839.8525, 360.0, 711),
        (425.95, 540.0, 712), (425.95, 540.0, 713), (425.95, 540.0, 714),
        (429.95, 540.0, 715), (429.95, 540.0, 716),
        (835.8525, 540.0, 717), (835.8525, 540.0, 718),
        (839.8525, 540.0, 719), (839.8525, 540.0, 720), (839.8525, 540.0, 721),
        (840.1475, 180.0, 722), (840.1475, 180.0, 723), (840.1475, 180.0, 724),
        (844.1475, 180.0, 725), (844.1475, 180.0, 726),
        (1255.852, 180.0, 727), (1255.852, 180.0, 728),
        (1259.852, 180.0, 729), (1259.852, 180.0, 730), (1259.852, 180.0, 731),
        (840.1475, 360.0, 732), (840.1475, 360.0, 733), (840.1475, 360.0, 734),
        (844.1475, 360.0, 735), (844.1475, 360.0, 736),
        (1255.852, 360.0, 737), (1255.852, 360.0, 738),
        (1259.852, 360.0, 739), (1259.852, 360.0, 740), (1259.852, 360.0, 741),
        (840.1475, 540.0, 742), (840.1475, 540.0, 743), (840.1475, 540.0, 744),
        (844.1475, 540.0, 745), (844.1475, 540.0, 746),
        (1255.852, 540.0, 747), (1255.852, 540.0, 748),
        (1259.852, 540.0, 749), (1259.852, 540.0, 750), (1259.852, 540.0, 751),
        (1260.148, 180.0, 752), (1260.148, 180.0, 753), (1260.148, 180.0, 754),
        (1264.148, 180.0, 755), (1264.148, 180.0, 756),
        (1670.05, 180.0, 757), (1670.05, 180.0, 758),
        (1674.05, 180.0, 759), (1674.05, 180.0, 760), (1674.05, 180.0, 761),
        (1260.148, 360.0, 762), (1260.148, 360.0, 763), (1260.148, 360.0, 764),
        (1264.148, 360.0, 765), (1264.148, 360.0, 766),
        (1670.05, 360.0, 767), (1670.05, 360.0, 768),
        (1674.05, 360.0, 769), (1674.05, 360.0, 770), (1674.05, 360.0, 771),
        (1260.148, 540.0, 772), (1260.148, 540.0, 773), (1260.148, 540.0, 774),
        (1264.148, 540.0, 775), (1264.148, 540.0, 776),
        (1670.05, 540.0, 777), (1670.05, 540.0, 778),
        (1674.05, 540.0, 779), (1674.05, 540.0, 780), (1674.05, 540.0, 781),
        (1685.95, 180.0, 782), (1685.95, 180.0, 783), (1685.95, 180.0, 784),
        (1689.95, 180.0, 785), (1689.95, 180.0, 786),
        (2095.85, 180.0, 787), (2095.85, 180.0, 788),
        (2099.85, 180.0, 789), (2099.85, 180.0, 790), (2099.85, 180.0, 791),
        (1685.95, 360.0, 792), (1685.95, 360.0, 793), (1685.95, 360.0, 794),
        (1689.95, 360.0, 795), (1689.95, 360.0, 796),
        (2095.85, 360.0, 797), (2095.85, 360.0, 798),
        (2099.85, 360.0, 799), (2099.85, 360.0, 800), (2099.85, 360.0, 801),
        (1685.95, 540.0, 802), (1685.95, 540.0, 803), (1685.95, 540.0, 804),
        (1689.95, 540.0, 805), (1689.95, 540.0, 806),
        (2095.85, 540.0, 807), (2095.85, 540.0, 808),
        (2099.85, 540.0, 809), (2099.85, 540.0, 810), (2099.85, 540.0, 811),
    ]
    for x, y, t in _conn_F:
        nodes.append((t, x, y))

    # Brace fiber discretization points — BR1-BR3 (nodes 812-844, left side)
    _brace_pts_L = [
        (3015.537, 13.31704, 812), (3015.537, 13.31704, 813),
        (3037.829, 32.54376, 814), (3060.131, 51.76005, 815),
        (3082.449, 70.95710, 816), (3104.789, 90.12900, 817),
        (3127.152, 109.2737, 818), (3149.536, 128.3932, 819),
        (3171.937, 147.4935, 820), (3194.347, 166.5833, 821),
        (3194.347, 166.5833, 822),
        (3015.621, 193.3896, 823), (3015.621, 193.3896, 824),
        (3037.959, 212.6548, 825), (3060.305, 231.9096, 826),
        (3082.668, 251.1451, 827), (3105.052, 270.3555, 828),
        (3127.460, 289.5385, 829), (3149.889, 308.6963, 830),
        (3172.335, 327.8349, 831), (3194.790, 346.9630, 832),
        (3194.790, 346.9630, 833),
        (3015.706, 373.4622, 834), (3015.706, 373.4622, 835),
        (3038.364, 393.0043, 836), (3061.032, 412.5358, 837),
        (3083.716, 432.0477, 838), (3106.422, 451.5341, 839),
        (3129.152, 470.9928, 840), (3151.904, 490.4260, 841),
        (3174.672, 509.8396, 842), (3197.450, 529.2426, 843),
        (3197.450, 529.2426, 844),
    ]
    for x, y, t in _brace_pts_L:
        nodes.append((t, x, y))

    # BR4-BR6 (nodes 845-877, right side)
    _brace_pts_R = [
        (3404.463, 13.31704, 845), (3404.463, 13.31704, 846),
        (3382.171, 32.54376, 847), (3359.869, 51.76005, 848),
        (3337.551, 70.95710, 849), (3315.211, 90.12900, 850),
        (3292.848, 109.2737, 851), (3270.464, 128.3932, 852),
        (3248.063, 147.4935, 853), (3225.653, 166.5833, 854),
        (3225.653, 166.5833, 855),
        (3404.379, 193.3896, 856), (3404.379, 193.3896, 857),
        (3382.041, 212.6548, 858), (3359.695, 231.9096, 859),
        (3337.332, 251.1451, 860), (3314.948, 270.3555, 861),
        (3292.540, 289.5385, 862), (3270.111, 308.6963, 863),
        (3247.665, 327.8349, 864), (3225.210, 346.9630, 865),
        (3225.210, 346.9630, 866),
        (3404.294, 373.4622, 867), (3404.294, 373.4622, 868),
        (3381.636, 393.0043, 869), (3358.968, 412.5358, 870),
        (3336.284, 432.0477, 871), (3313.578, 451.5341, 872),
        (3290.848, 470.9928, 873), (3268.096, 490.4260, 874),
        (3245.328, 509.8396, 875), (3222.550, 529.2426, 876),
        (3222.550, 529.2426, 877),
    ]
    for x, y, t in _brace_pts_R:
        nodes.append((t, x, y))

    # Create all nodes with unit conversion (in → mm)
    _mass_nodes = {534: 3.211686, 549: 3.211686, 564: 1.499650}  # kip·s²/in
    _kip_s2_in_to_Mg = 4448.22 / (25.4 * 1000.0)  # ≈ 0.1751
    for tag, x_in, y_in in nodes:
        x_mm = x_in * inch
        y_mm = y_in * inch
        if tag in _mass_nodes:
            mass_Mg = _mass_nodes[tag] * _kip_s2_in_to_Mg
            ops.node(tag, x_mm, y_mm, "-mass", mass_Mg, 1e-9, 1e-9)
        else:
            ops.node(tag, x_mm, y_mm)


# ── 9. BOUNDARY CONDITIONS ─────────────────────────────────────────────────────
def define_boundary_conditions():
    """Define equalDOF constraints and fixity at column bases."""
    # ── Brace rigid links (equalDOF: master = last fiber pt, slave = second-to-last) ──
    ops.equalDOF(822, 821, 1, 2)  # BR1
    ops.equalDOF(833, 832, 1, 2)  # BR2
    ops.equalDOF(844, 843, 1, 2)  # BR3
    ops.equalDOF(855, 854, 1, 2)  # BR4
    ops.equalDOF(866, 865, 1, 2)  # BR5
    ops.equalDOF(877, 876, 1, 2)  # BR6

    # ── Floor diaphragm constraints (X-direction) ──
    _diaphragm_s1 = [
        (116, 140), (116, 160), (116, 174), (116, 192), (116, 216),
        (8, 28), (8, 44), (8, 60), (8, 74), (8, 92),
        (236, 250), (236, 268), (236, 292), (236, 312), (236, 330),
    ]
    for m, s in _diaphragm_s1:
        ops.equalDOF(m, s, 1)
    _diaphragm_s2 = [
        (124, 148), (124, 165), (124, 179), (124, 200), (124, 224),
        (16, 33), (16, 49), (16, 65), (16, 79), (16, 100),
        (241, 255), (241, 276), (241, 300), (241, 317), (241, 338),
    ]
    for m, s in _diaphragm_s2:
        ops.equalDOF(m, s, 1)
    _diaphragm_s3 = [
        (132, 156), (132, 170), (132, 184), (132, 208), (132, 232),
        (24, 38), (24, 54), (24, 70), (24, 84), (24, 108),
        (246, 260), (246, 284), (246, 308), (246, 322), (246, 346),
    ]
    for m, s in _diaphragm_s3:
        ops.equalDOF(m, s, 1)

    # ── Column base fixity ──
    _fix_11 = [1, 25, 71, 85, 109, 133, 157, 171, 185, 209, 233, 247, 261, 285, 309, 323]
    for n in _fix_11:
        ops.fix(n, 1, 1, 0)
    ops.fix(39, 1, 1, 1)
    ops.fix(55, 1, 1, 1)


# ── 10. ELEMENTS ───────────────────────────────────────────────────────────────
def define_elements():
    """Define all elements: dispBeamColumn, elasticBeamColumn, truss, zeroLength variants."""
    _A_in2_mm2 = inch * inch
    _I_in4_mm4 = inch ** 4
    _E_MPa = 29000.0 * ksi  # 199948 MPa

    # ── Fiber brace elements (dispBeamColumn) ──
    # BR1 (left) — elements 847-854
    _br1_et = list(range(847, 855))
    _br1_in = [813, 814, 815, 816, 817, 818, 819, 820]
    _br1_jn = [814, 815, 816, 817, 818, 819, 820, 821]
    _br1_st = [SEC_HSS9X9_BR1] * 8
    _define_elements_batch("dispBeamColumn", _br1_et, _br1_in, _br1_jn, 5, _br1_st, GEOM_COROT)

    # BR2 (left) — elements 859-866
    _br2_et = list(range(859, 867))
    _br2_in = [824, 825, 826, 827, 828, 829, 830, 831]
    _br2_jn = [825, 826, 827, 828, 829, 830, 831, 832]
    _br2_st = [SEC_HSS8X8_BR2] * 8
    _define_elements_batch("dispBeamColumn", _br2_et, _br2_in, _br2_jn, 5, _br2_st, GEOM_COROT)

    # BR3 (left) — elements 871-878
    _br3_et = list(range(871, 879))
    _br3_in = [835, 836, 837, 838, 839, 840, 841, 842]
    _br3_jn = [836, 837, 838, 839, 840, 841, 842, 843]
    _br3_st = [SEC_HSS7X7_BR3] * 8
    _define_elements_batch("dispBeamColumn", _br3_et, _br3_in, _br3_jn, 5, _br3_st, GEOM_COROT)

    # BR4 (right) — elements 883-890
    _br4_et = list(range(883, 891))
    _br4_in = [846, 847, 848, 849, 850, 851, 852, 853]
    _br4_jn = [847, 848, 849, 850, 851, 852, 853, 854]
    _br4_st = [SEC_HSS9X9_BR4] * 8
    _define_elements_batch("dispBeamColumn", _br4_et, _br4_in, _br4_jn, 5, _br4_st, GEOM_COROT)

    # BR5 (right) — elements 895-902
    _br5_et = list(range(895, 903))
    _br5_in = [857, 858, 859, 860, 861, 862, 863, 864]
    _br5_jn = [858, 859, 860, 861, 862, 863, 864, 865]
    _br5_st = [SEC_HSS8X8_BR5] * 8
    _define_elements_batch("dispBeamColumn", _br5_et, _br5_in, _br5_jn, 5, _br5_st, GEOM_COROT)

    # BR6 (right) — elements 907-914
    _br6_et = list(range(907, 915))
    _br6_in = [868, 869, 870, 871, 872, 873, 874, 875]
    _br6_jn = [869, 870, 871, 872, 873, 874, 875, 876]
    _br6_st = [SEC_HSS7X7_BR6] * 8
    _define_elements_batch("dispBeamColumn", _br6_et, _br6_in, _br6_jn, 5, _br6_st, GEOM_COROT)

    # ── Fiber weak-axis column elements (dispBeamColumn) ──
    # C1: elements 1-6
    _wc1_et = list(range(1, 7)); _wc1_in = list(range(1, 7)); _wc1_jn = list(range(2, 8))
    _wc1_st = [SEC_W12X40_E1] * 6
    _define_elements_batch("dispBeamColumn", _wc1_et, _wc1_in, _wc1_jn, 5, _wc1_st, GEOM_COROT)
    # C2: elements 9-14
    _wc2_et = list(range(9, 15)); _wc2_in = list(range(9, 15)); _wc2_jn = list(range(10, 16))
    _wc2_st = [SEC_W12X40_E2] * 6
    _define_elements_batch("dispBeamColumn", _wc2_et, _wc2_in, _wc2_jn, 5, _wc2_st, GEOM_COROT)
    # C3: elements 17-22
    _wc3_et = list(range(17, 23)); _wc3_in = list(range(17, 23)); _wc3_jn = list(range(18, 24))
    _wc3_st = [SEC_W12X40_E3] * 6
    _define_elements_batch("dispBeamColumn", _wc3_et, _wc3_in, _wc3_jn, 5, _wc3_st, GEOM_COROT)
    # C16: elements 80-85
    _c16_et = list(range(80, 86)); _c16_in = list(range(85, 91)); _c16_jn = list(range(86, 92))
    _c16_st = [SEC_W12X40_E6] * 6
    _define_elements_batch("dispBeamColumn", _c16_et, _c16_in, _c16_jn, 5, _c16_st, GEOM_COROT)
    # C17: elements 88-93
    _c17_et = list(range(88, 94)); _c17_in = list(range(93, 99)); _c17_jn = list(range(94, 100))
    _c17_st = [SEC_W12X40_E6b] * 6
    _define_elements_batch("dispBeamColumn", _c17_et, _c17_in, _c17_jn, 5, _c17_st, GEOM_COROT)
    # C18: elements 96-101
    _c18_et = list(range(96, 102)); _c18_in = list(range(101, 107)); _c18_jn = list(range(102, 108))
    _c18_st = [SEC_W12X40_E6c] * 6
    _define_elements_batch("dispBeamColumn", _c18_et, _c18_in, _c18_jn, 5, _c18_st, GEOM_COROT)
    # C19: elements 103-108
    _c19_et = list(range(103, 109)); _c19_in = list(range(109, 115)); _c19_jn = list(range(110, 116))
    _c19_st = [SEC_W12X40_D1] * 6
    _define_elements_batch("dispBeamColumn", _c19_et, _c19_in, _c19_jn, 5, _c19_st, GEOM_COROT)
    # C20: elements 111-116
    _c20_et = list(range(111, 117)); _c20_in = list(range(117, 123)); _c20_jn = list(range(118, 124))
    _c20_st = [SEC_W12X40_D1b] * 6
    _define_elements_batch("dispBeamColumn", _c20_et, _c20_in, _c20_jn, 5, _c20_st, GEOM_COROT)
    # C21: elements 119-124
    _c21_et = list(range(119, 125)); _c21_in = list(range(125, 131)); _c21_jn = list(range(126, 132))
    _c21_st = [SEC_W12X40_D1c] * 6
    _define_elements_batch("dispBeamColumn", _c21_et, _c21_in, _c21_jn, 5, _c21_st, GEOM_COROT)
    # C22: elements 126-131
    _c22_et = list(range(126, 132)); _c22_in = list(range(133, 139)); _c22_jn = list(range(134, 140))
    _c22_st = [SEC_W12X50_D2] * 6
    _define_elements_batch("dispBeamColumn", _c22_et, _c22_in, _c22_jn, 5, _c22_st, GEOM_COROT)
    # C23: elements 134-139
    _c23_et = list(range(134, 140)); _c23_in = list(range(141, 147)); _c23_jn = list(range(142, 148))
    _c23_st = [SEC_W12X50_D2b] * 6
    _define_elements_batch("dispBeamColumn", _c23_et, _c23_in, _c23_jn, 5, _c23_st, GEOM_COROT)
    # C24: elements 142-147
    _c24_et = list(range(142, 148)); _c24_in = list(range(149, 155)); _c24_jn = list(range(150, 156))
    _c24_st = [SEC_W12X50_D2c] * 6
    _define_elements_batch("dispBeamColumn", _c24_et, _c24_in, _c24_jn, 5, _c24_st, GEOM_COROT)

    # C31-C48: W12X40/W12X50/W12X35 weak-axis columns on F/C grids
    _wc_batches = [
        # C31: el 175-180, in 185-190, jn 186-191, sec 27
        (list(range(175, 181)), list(range(185, 191)), list(range(186, 192)), [SEC_W12X50_D5] * 6),
        (list(range(183, 189)), list(range(193, 199)), list(range(194, 200)), [SEC_W12X50_D5b] * 6),
        (list(range(191, 197)), list(range(201, 207)), list(range(202, 208)), [SEC_W12X50_D5c] * 6),
        # C34: el 198-203, in 209-214, jn 210-215, sec 30
        (list(range(198, 204)), list(range(209, 215)), list(range(210, 216)), [SEC_W12X40_D6] * 6),
        (list(range(206, 212)), list(range(217, 223)), list(range(218, 224)), [SEC_W12X40_D6b] * 6),
        (list(range(214, 220)), list(range(225, 231)), list(range(226, 232)), [SEC_W12X40_D6c] * 6),
        # C43: el 247-252, in 261-266, jn 262-267, sec 33
        (list(range(247, 253)), list(range(261, 267)), list(range(262, 268)), [SEC_W12X40_F3] * 6),
        (list(range(255, 261)), list(range(269, 275)), list(range(270, 276)), [SEC_W12X40_F3b] * 6),
        (list(range(263, 269)), list(range(277, 283)), list(range(278, 284)), [SEC_W12X40_F3c] * 6),
        # C46: el 270-275, in 285-290, jn 286-291, sec 36
        (list(range(270, 276)), list(range(285, 291)), list(range(286, 292)), [SEC_W12X40_F4] * 6),
        (list(range(278, 284)), list(range(293, 299)), list(range(294, 300)), [SEC_W12X40_F4b] * 6),
        (list(range(286, 292)), list(range(301, 307)), list(range(302, 308)), [SEC_W12X40_F4c] * 6),
        # C52: el 306-311, C53: 314-319, C54: 322-327
        (list(range(306, 312)), list(range(323, 329)), list(range(324, 330)), [SEC_W12X35_F6] * 6),
        (list(range(314, 320)), list(range(331, 337)), list(range(332, 338)), [SEC_W12X35_F6b] * 6),
        (list(range(322, 328)), list(range(339, 345)), list(range(340, 346)), [SEC_W12X35_F6c] * 6),
    ]
    for et, inn, jn, st in _wc_batches:
        _define_elements_batch("dispBeamColumn", et, inn, jn, 5, st, GEOM_COROT)

    # ── elasticBeamColumn elements ──
    # Helper for elasticBeamColumn with imperial-to-metric conversion
    def _ebc_batch(et, inn, jn, A_in2, E_ksi, I_in4, gtag):
        A_mm2 = A_in2 * _A_in2_mm2
        E_MPa = E_ksi * ksi
        I_mm4 = I_in4 * _I_in4_mm4
        _define_elements_batch("elasticBeamColumn", et, inn, jn, A_mm2, E_MPa, I_mm4, gtag)

    # W18X35(S) beams B33,B36,B39,B42,B45: A=10.3, E=29000, I=561
    _ebc_batch([701, 734, 767, 800, 833],
               [686, 716, 746, 776, 806],
               [687, 717, 747, 777, 807],
               10.3, 29000, 561, GEOM_PDELTA)
    # W12X35(WR) C52,C53,C54 leaner columns: A=103, E=29000, I=269.5
    _ebc_batch([312, 313, 320, 321, 328],
               [329, 330, 337, 338, 345],
               [330, 331, 338, 339, 346],
               103, 29000, 269.5, GEOM_COROT)
    # W12X35(SR) C37,C38,C39: A=103, E=29000, I=3135
    _ebc_batch([223, 224, 228, 229, 233],
               [235, 236, 240, 241, 245],
               [236, 237, 241, 242, 246],
               103, 29000, 3135, GEOM_PDELTA)
    # W18X35(SR) stiff girder extensions: A=103, E=29000, I=5610
    _ebc_batch([696, 699, 703, 706, 729, 732, 736, 739, 762, 765, 769, 772,
                795, 798, 802, 805, 828, 831, 835, 838],
               [246, 684, 688, 691, 260, 714, 718, 721, 284, 744, 748, 751,
                308, 774, 778, 781, 322, 804, 808, 811],
               [682, 685, 689, 260, 712, 715, 719, 284, 742, 745, 749, 308,
                772, 775, 779, 322, 802, 805, 809, 346],
               103, 29000, 5610, GEOM_PDELTA)
    # W12X40(S) C40,C41,C42,C49,C50,C51: A=11.7, E=29000, I=337.7
    _ebc_batch([234, 239, 244, 293, 298, 303],
               [247, 252, 257, 309, 314, 319],
               [248, 253, 258, 310, 315, 320],
               11.7, 29000, 337.7, GEOM_PDELTA)
    # W12X40(SR) rigid extensions: A=117, E=29000, I=3377
    _ebc_batch([236, 237, 241, 242, 246, 295, 296, 300, 301, 305],
               [249, 250, 254, 255, 259, 311, 312, 316, 317, 321],
               [250, 251, 255, 256, 260, 312, 313, 317, 318, 322],
               117, 29000, 3377, GEOM_PDELTA)
    # W12X40(WR) weak-axis elastic columns: A=117, E=29000, I=485.1
    _ebc_batch([7, 8, 15, 16, 23, 86, 87, 94, 95, 102, 109, 110, 117, 118, 125,
                204, 205, 212, 213, 220, 253, 254, 261, 262],
               [7, 8, 15, 16, 23, 91, 92, 99, 100, 107, 115, 116, 123, 124, 131,
                215, 216, 223, 224, 231, 267, 268, 275, 276],
               [8, 9, 16, 17, 24, 92, 93, 100, 101, 108, 116, 117, 124, 125, 132,
                216, 217, 224, 225, 232, 268, 269, 276, 277],
               117, 29000, 485.1, GEOM_COROT)
    _ebc_batch([269, 276, 277, 284, 285, 292],
               [283, 291, 292, 299, 300, 307],
               [284, 292, 293, 300, 301, 308],
               117, 29000, 485.1, GEOM_COROT)
    # W16X40(SR) B19/B20: A=118, E=29000, I=5698
    _ebc_batch([527, 530, 534, 535, 539, 542, 543, 546, 550, 551, 555, 558],
               [44, 529, 533, 534, 538, 541, 49, 544, 548, 549, 553, 556],
               [527, 530, 534, 535, 539, 60, 542, 545, 549, 550, 554, 65],
               118, 29000, 5698, GEOM_PDELTA)
    # W12X50(S) columns: A=14.6, E=29000, I=430.1
    _ebc_batch([24, 29, 34, 39, 44, 49, 54, 59, 64, 67, 72, 77, 149, 154, 159, 162, 167, 172],
               [25, 30, 35, 41, 46, 51, 57, 62, 67, 71, 76, 81, 157, 162, 167, 171, 176, 181],
               [26, 31, 36, 42, 47, 52, 58, 63, 68, 72, 77, 82, 158, 163, 168, 172, 177, 182],
               14.6, 29000, 430.1, GEOM_PDELTA)
    # W12X50(SR) rigid extensions: A=146, E=29000, I=4301
    _ebc_batch([26, 27, 31, 32, 36, 37, 41, 42, 46, 47, 51, 52, 56, 57, 61, 62, 66, 69, 70, 74, 75, 79,
                151, 152, 156, 157, 161, 164, 165, 169, 170, 174],
               [27, 28, 32, 33, 37, 39, 43, 44, 48, 49, 53, 55, 59, 60, 64, 65, 69, 73, 74, 78, 79, 83,
                159, 160, 164, 165, 169, 173, 174, 178, 179, 183],
               [28, 29, 33, 34, 38, 40, 44, 45, 49, 50, 54, 56, 60, 61, 65, 66, 70, 74, 75, 79, 80, 84,
                160, 161, 165, 166, 170, 174, 175, 179, 180, 184],
               146, 29000, 4301, GEOM_PDELTA)
    # W12X50(WR) C22-C24,C31-C33: A=146, E=29000, I=619.3
    _ebc_batch([132, 133, 140, 141, 148, 181, 182, 189, 190, 197],
               [139, 140, 147, 148, 155, 191, 192, 199, 200, 207],
               [140, 141, 148, 149, 156, 192, 193, 200, 201, 208],
               146, 29000, 619.3, GEOM_COROT)
    # W16X57(S) beams B1-B29: A=16.8, E=29000, I=833.8
    _ebc_batch([334, 345, 367, 378, 400, 411, 433, 444, 466, 477, 499, 510, 580, 591, 613, 624, 646, 657],
               [351, 361, 381, 391, 411, 421, 441, 451, 471, 481, 501, 511, 576, 586, 606, 616, 636, 646],
               [352, 362, 382, 392, 412, 422, 442, 452, 472, 482, 502, 512, 577, 587, 607, 617, 637, 647],
               16.8, 29000, 833.8, GEOM_PDELTA)
    # W16X57(SR) rigid extensions: A=168, E=29000, I=8338
    _w16x57_sr_e = [329, 332, 336, 339, 340, 343, 347, 350, 362, 365, 369, 372, 373, 376, 380, 383,
                    395, 398, 402, 405, 406, 409, 413, 416]
    _w16x57_sr_i = [116, 349, 353, 356, 124, 359, 363, 366, 140, 379, 383, 386, 148, 389, 393, 396,
                    160, 409, 413, 416, 165, 419, 423, 426]
    _w16x57_sr_j = [347, 350, 354, 140, 357, 360, 364, 148, 377, 380, 384, 160, 387, 390, 394, 165,
                    407, 410, 414, 174, 417, 420, 424, 179]
    _ebc_batch(_w16x57_sr_e, _w16x57_sr_i, _w16x57_sr_j, 168, 29000, 8338, GEOM_PDELTA)
    _ebc_batch([428, 431, 435, 438, 439, 442, 446, 449, 461, 464, 468, 471, 472, 475, 479, 482,
                494, 497, 501, 504, 505, 508, 512, 515],
               [174, 439, 443, 446, 179, 449, 453, 456, 192, 469, 473, 476, 200, 479, 483, 486,
                8, 499, 503, 506, 16, 509, 513, 516],
               [437, 440, 444, 192, 447, 450, 454, 200, 467, 470, 474, 216, 477, 480, 484, 224,
                497, 500, 504, 28, 507, 510, 514, 33],
               168, 29000, 8338, GEOM_PDELTA)
    _ebc_batch([575, 578, 582, 585, 586, 589, 593, 596, 608, 611, 615, 618, 619, 622, 626, 629,
                641, 644, 648, 651, 652, 655, 659, 662],
               [28, 574, 578, 581, 33, 584, 588, 591, 60, 604, 608, 611, 65, 614, 618, 621,
                74, 634, 638, 641, 79, 644, 648, 651],
               [572, 575, 579, 44, 582, 585, 589, 49, 602, 605, 609, 74, 612, 615, 619, 79,
                632, 635, 639, 92, 642, 645, 649, 100],
               168, 29000, 8338, GEOM_PDELTA)
    # W18X60(S) beams B31-B44: A=17.6, E=29000, I=1082.4
    _ebc_batch([679, 690, 712, 723, 745, 756, 778, 789, 811, 822],
               [666, 676, 696, 706, 726, 736, 756, 766, 786, 796],
               [667, 677, 697, 707, 727, 737, 757, 767, 787, 797],
               17.6, 29000, 1082.4, GEOM_PDELTA)
    # W18X60(SR) rigid extensions: A=176, E=29000, I=10824
    _w18x60_sr_batches = [
        ([674, 677, 681, 684, 685, 688, 692, 695, 707, 710, 714, 717, 718, 721, 725, 728,
          740, 743, 747, 750, 751, 754, 758, 761],
         [236, 664, 668, 671, 241, 674, 678, 681, 250, 694, 698, 701, 255, 704, 708, 711,
          268, 724, 728, 731, 276, 734, 738, 741],
         [662, 665, 669, 250, 672, 675, 679, 255, 692, 695, 699, 268, 702, 705, 709, 276,
          722, 725, 729, 292, 732, 735, 739, 300]),
        ([773, 776, 780, 783, 784, 787, 791, 794, 806, 809, 813, 816, 817, 820, 824, 827],
         [292, 754, 758, 761, 300, 764, 768, 771, 312, 784, 788, 791, 317, 794, 798, 801],
         [752, 755, 759, 312, 762, 765, 769, 317, 782, 785, 789, 330, 792, 795, 799, 338]),
    ]
    for et, inn, jn in _w18x60_sr_batches:
        _ebc_batch(et, inn, jn, 176, 29000, 10824, GEOM_PDELTA)
    # W12X26(SR) B21: A=76.5, E=29000, I=2244
    _ebc_batch([559, 562, 566, 567, 571, 574],
               [54, 559, 563, 564, 568, 571],
               [557, 560, 564, 565, 569, 70],
               76.5, 29000, 2244, GEOM_PDELTA)
    # W16X26(S) beams: A=7.68, E=29000, I=331.1
    _ebc_batch([356, 389, 422, 455, 488, 521, 602, 635, 668],
               [371, 401, 431, 461, 491, 521, 596, 626, 656],
               [372, 402, 432, 462, 492, 522, 597, 627, 657],
               7.68, 29000, 331.1, GEOM_PDELTA)
    # W16X26(SR) rigid extensions: A=76.8, E=29000, I=3311
    _w16x26_sr_batches = [
        ([351, 354, 358, 361, 384, 387, 391, 394, 417, 420, 424, 427, 450, 453, 457, 460,
          483, 486, 490, 493, 516, 519, 523, 526],
         [132, 369, 373, 376, 156, 399, 403, 406, 170, 429, 433, 436, 184, 459, 463, 466,
          208, 489, 493, 496, 24, 519, 523, 526],
         [367, 370, 374, 156, 397, 400, 404, 170, 427, 430, 434, 184, 457, 460, 464, 208,
          487, 490, 494, 232, 517, 520, 524, 38]),
        ([597, 600, 604, 607, 630, 633, 637, 640, 663, 666, 670, 673],
         [38, 594, 598, 601, 70, 624, 628, 631, 84, 654, 658, 661],
         [592, 595, 599, 54, 622, 625, 629, 84, 652, 655, 659, 108]),
    ]
    for et, inn, jn in _w16x26_sr_batches:
        _ebc_batch(et, inn, jn, 76.8, 29000, 3311, GEOM_PDELTA)

    # Individual elasticBeamColumn (B19/B20/B21 individual + brace SR)
    _ind_ebc = [
        (532, 531, 532, 11.8, 29000, 569.8, GEOM_PDELTA),   # B19 W16X40(S)
        (537, 536, 537, 11.8, 29000, 569.8, GEOM_PDELTA),   # B19
        (548, 546, 547, 11.8, 29000, 569.8, GEOM_PDELTA),   # B20
        (553, 551, 552, 11.8, 29000, 569.8, GEOM_PDELTA),   # B20
        (564, 561, 562, 7.65, 29000, 224.4, GEOM_PDELTA),   # B21 W12X26(S)
        (569, 566, 567, 7.65, 29000, 224.4, GEOM_PDELTA),   # B21
        (845, 39, 812, 60.6, 29000, 860.2, GEOM_COROT),     # BR1 SR
        (856, 822, 534, 60.6, 29000, 860.2, GEOM_COROT),    # BR1 SR
        (857, 44, 823, 53.7, 29000, 598.4, GEOM_COROT),     # BR2 SR
        (868, 833, 549, 53.7, 29000, 598.4, GEOM_COROT),    # BR2 SR
        (869, 49, 834, 31.6, 29000, 272.8, GEOM_COROT),     # BR3 SR
        (880, 844, 564, 31.6, 29000, 272.8, GEOM_COROT),    # BR3 SR
        (881, 55, 845, 60.6, 29000, 860.2, GEOM_COROT),     # BR4 SR
        (892, 855, 534, 60.6, 29000, 860.2, GEOM_COROT),    # BR4 SR
        (893, 60, 856, 53.7, 29000, 598.4, GEOM_COROT),     # BR5 SR
        (904, 866, 549, 53.7, 29000, 598.4, GEOM_COROT),    # BR5 SR
        (905, 65, 867, 31.6, 29000, 272.8, GEOM_COROT),     # BR6 SR
        (916, 877, 564, 31.6, 29000, 272.8, GEOM_COROT),    # BR6 SR
        (221, 233, 234, 10.3, 29000, 313.5, GEOM_PDELTA),   # C37 W12X35(S)
        (226, 238, 239, 10.3, 29000, 313.5, GEOM_PDELTA),   # C38
        (231, 243, 244, 10.3, 29000, 313.5, GEOM_PDELTA),   # C39
    ]
    for et, inn, jn, a_i, e_k, i_i, gt in _ind_ebc:
        ops.element("elasticBeamColumn", et, inn, jn,
                    a_i * _A_in2_mm2, e_k * ksi, i_i * _I_in4_mm4, gt)

    # ── Truss rigid ties (RL1-RL6) ──
    _truss_et = [839, 840, 841, 842, 843, 844]
    _truss_in = [330, 338, 346, 92, 100, 108]
    _truss_jn = [8, 16, 24, 116, 124, 132]
    _define_elements_batch("truss", _truss_et, _truss_in, _truss_jn,
                           1000.0 * _A_in2_mm2, MAT_ELASTIC_E0)

    # ── IMK rotational springs ──
    _imk = [
        # B1-B18
        ([333, 335, 344, 346, 355, 357, 366, 368, 377, 379, 388, 390,
          399, 401, 410, 412, 421, 423, 432, 434, 443, 445, 454, 456],
         [350, 352, 360, 362, 370, 372, 380, 382, 390, 392, 400, 402,
          410, 412, 420, 422, 430, 432, 440, 442, 450, 452, 460, 462],
         [351, 353, 361, 363, 371, 373, 381, 383, 391, 393, 401, 403,
          411, 413, 421, 423, 431, 433, 441, 443, 451, 453, 461, 463],
         [218, 218, 218, 218, 219, 219, 220, 220, 220, 220, 221, 221,
          222, 222, 222, 222, 223, 223, 220, 220, 220, 220, 221, 221]),
        # B13-B21
        ([465, 467, 476, 478, 487, 489, 498, 500, 509, 511, 520, 522,
          531, 533, 536, 538, 547, 549, 552, 554, 563, 565, 568, 570],
         [470, 472, 480, 482, 490, 492, 500, 502, 510, 512, 520, 522,
          530, 532, 535, 537, 545, 547, 550, 552, 560, 562, 565, 567],
         [471, 473, 481, 483, 491, 493, 501, 503, 511, 513, 521, 523,
          531, 533, 536, 538, 546, 548, 551, 553, 561, 563, 566, 568],
         [218, 218, 218, 218, 219, 219, 224, 224, 224, 224, 225, 225,
          226, 226, 226, 226, 227, 227, 227, 227, 228, 228, 228, 228]),
        # B22-B33
        ([579, 581, 590, 592, 601, 603, 612, 614, 623, 625, 634, 636,
          645, 647, 656, 658, 667, 669, 678, 680, 689, 691, 700, 702],
         [575, 577, 585, 587, 595, 597, 605, 607, 615, 617, 625, 627,
          635, 637, 645, 647, 655, 657, 665, 667, 675, 677, 685, 687],
         [576, 578, 586, 588, 596, 598, 606, 608, 616, 618, 626, 628,
          636, 638, 646, 648, 656, 658, 666, 668, 676, 678, 686, 688],
         [222, 222, 222, 222, 223, 223, 222, 222, 222, 222, 223, 223,
          224, 224, 224, 224, 225, 225, 229, 229, 229, 229, 230, 230]),
        # B34-B45
        ([711, 713, 722, 724, 733, 735, 744, 746, 755, 757, 766, 768,
          777, 779, 788, 790, 799, 801, 810, 812, 821, 823, 832, 834],
         [695, 697, 705, 707, 715, 717, 725, 727, 735, 737, 745, 747,
          755, 757, 765, 767, 775, 777, 785, 787, 795, 797, 805, 807],
         [696, 698, 706, 708, 716, 718, 726, 728, 736, 738, 746, 748,
          756, 758, 766, 768, 776, 778, 786, 788, 796, 798, 806, 808],
         [231, 231, 231, 231, 232, 232, 233, 233, 233, 233, 234, 234,
          231, 231, 231, 231, 232, 232, 235, 235, 235, 235, 236, 236]),
        # C4-C15, C25-C30: column IMKs
        ([25, 28, 30, 33, 35, 38, 40, 43, 45, 48, 50, 53, 55, 58, 60, 63, 65, 68,
          71, 73, 76, 78, 150, 153],
         [26, 29, 31, 34, 36, 40, 42, 45, 47, 50, 52, 56, 58, 61, 63, 66, 68, 72,
          75, 77, 80, 82, 158, 161],
         [27, 30, 32, 35, 37, 41, 43, 46, 48, 51, 53, 57, 59, 62, 64, 67, 69, 73,
          76, 78, 81, 83, 159, 162],
         [110, 111, 111, 112, 112, 113, 113, 114, 114, 115, 115, 113, 113, 114, 114, 115, 115, 110,
          111, 111, 112, 112, 110, 111]),
        # C26-C51
        ([155, 158, 160, 163, 166, 168, 171, 173, 222, 225, 227, 230, 232,
          235, 238, 240, 243, 245, 294, 297, 299, 302, 304],
         [163, 166, 168, 172, 175, 177, 180, 182, 234, 237, 239, 242, 244,
          248, 251, 253, 256, 258, 310, 313, 315, 318, 320],
         [164, 167, 169, 173, 176, 178, 181, 183, 235, 238, 240, 243, 245,
          249, 252, 254, 257, 259, 311, 314, 316, 319, 321],
         [111, 112, 112, 110, 111, 111, 112, 112, 176, 177, 177, 178, 178,
          179, 180, 180, 181, 181, 179, 180, 180, 181, 181]),
    ]
    for et, inn, jn, mt in _imk:
        _define_elements_batch("zeroLength-IMK", et, inn, jn, "-mat", mt, "-dir", 6)

    # ── zeroLength-SBL (bridge left) ──
    _sbl_batches = [
        (list(range(330, 529, 11)),  # 330,341,...,528 → 19 elements
         [347, 357, 367, 377, 387, 397, 407, 417, 427, 437, 447, 457,
          467, 477, 487, 497, 507, 517, 527],
         [349, 359, 369, 379, 389, 399, 409, 419, 429, 439, 449, 459,
          469, 479, 489, 499, 509, 519, 529]),
        ([542, 544],  # B20 SBL
         [542], [544]),
        ([557, 559], [557], [559]),  # B21 SBL (wait, checking the Tcl...)
    ]
    # Actually, the SBL/SBR elements are best handled directly from Tcl mapping.
    # Using the exact element tags from Tcl:
    _sbl_et = [330, 341, 352, 363, 374, 385, 396, 407, 418, 429, 440, 451, 462, 473, 484, 495, 506, 517,
               528, 544, 560, 576, 587, 598, 609, 620, 631, 642, 653, 664, 675, 686, 697, 708, 719, 730,
               741, 752, 763, 774, 785, 796, 807, 818, 829]
    _sbl_in = [347, 357, 367, 377, 387, 397, 407, 417, 427, 437, 447, 457, 467, 477, 487, 497, 507, 517,
               527, 542, 557, 572, 582, 592, 602, 612, 622, 632, 642, 652, 662, 672, 682, 692, 702, 712,
               722, 732, 742, 752, 762, 772, 782, 792, 802]
    _sbl_jn = [349, 359, 369, 379, 389, 399, 409, 419, 429, 439, 449, 459, 469, 479, 489, 499, 509, 519,
               529, 544, 559, 574, 584, 594, 604, 614, 624, 634, 644, 654, 664, 674, 684, 694, 704, 714,
               724, 734, 744, 754, 764, 774, 784, 794, 804]
    _sbl_mat = [MAT_ELASTIC_Ep3] * len(_sbl_et)
    _define_elements_batch("zeroLength-SBL", _sbl_et, _sbl_in, _sbl_jn, "-mat", _sbl_mat, "-dir", 1)

    _sbr_et = [338, 349, 360, 371, 382, 393, 404, 415, 426, 437, 448, 459, 470, 481, 492, 503, 514, 525,
               541, 557, 573, 584, 595, 606, 617, 628, 639, 650, 661, 672, 683, 694, 705, 716, 727, 738,
               749, 760, 771, 782, 793, 804, 815, 826, 837]
    _sbr_in = [354, 364, 374, 384, 394, 404, 414, 424, 434, 444, 454, 464, 474, 484, 494, 504, 514, 524,
               539, 554, 569, 579, 589, 599, 609, 619, 629, 639, 649, 659, 669, 679, 689, 699, 709, 719,
               729, 739, 749, 759, 769, 779, 789, 799, 809]
    _sbr_jn = [356, 366, 376, 386, 396, 406, 416, 426, 436, 446, 456, 466, 476, 486, 496, 506, 516, 526,
               541, 556, 571, 581, 591, 601, 611, 621, 631, 641, 651, 661, 671, 681, 691, 701, 711, 721,
               731, 741, 751, 761, 771, 781, 791, 801, 811]
    _sbr_mat = [MAT_ELASTIC_Ep3] * len(_sbr_et)
    _define_elements_batch("zeroLength-SBR", _sbr_et, _sbr_in, _sbr_jn, "-mat", _sbr_mat, "-dir", 1)

    # ── Brace-gusset weld zeroLength elements ──
    _cos = 0.7592566; _sin = 0.6507914  # brace angle direction cosines
    # BR1-BR3 (left braces — positive orientation)
    _weld_L = [
        (846, 812, 813, [MAT_ELASTIC_E0, MAT_ELASTIC_E0, MAT_GUSSET_S1_L], [1, 2, 6],
         [_cos, _sin, 0.0, -_sin, _cos, 0.0]),
        (855, 821, 822, [MAT_GUSSET_S1_L], [6],
         [_cos, _sin, 0.0, -_sin, _cos, 0.0]),
        (858, 823, 824, [MAT_ELASTIC_E0, MAT_ELASTIC_E0, MAT_GUSSET_S2_L], [1, 2, 6],
         [_cos, _sin, 0.0, -_sin, _cos, 0.0]),
        (867, 832, 833, [MAT_GUSSET_S2_L], [6],
         [_cos, _sin, 0.0, -_sin, _cos, 0.0]),
        (870, 834, 835, [MAT_ELASTIC_E0, MAT_ELASTIC_E0, MAT_GUSSET_S3_L], [1, 2, 6],
         [_cos, _sin, 0.0, -_sin, _cos, 0.0]),
        (879, 843, 844, [MAT_GUSSET_S3_L], [6],
         [_cos, _sin, 0.0, -_sin, _cos, 0.0]),
    ]
    # BR4-BR6 (right braces — negative x-orientation)
    _weld_R = [
        (882, 845, 846, [MAT_ELASTIC_E0, MAT_ELASTIC_E0, MAT_GUSSET_S1_R], [1, 2, 6],
         [-_cos, _sin, 0.0, -_sin, -_cos, 0.0]),
        (891, 854, 855, [MAT_GUSSET_S1_R], [6],
         [-_cos, _sin, 0.0, -_sin, -_cos, 0.0]),
        (894, 856, 857, [MAT_ELASTIC_E0, MAT_ELASTIC_E0, MAT_GUSSET_S2_R], [1, 2, 6],
         [-_cos, _sin, 0.0, -_sin, -_cos, 0.0]),
        (903, 865, 866, [MAT_GUSSET_S2_R], [6],
         [-_cos, _sin, 0.0, -_sin, -_cos, 0.0]),
        (906, 867, 868, [MAT_ELASTIC_E0, MAT_ELASTIC_E0, MAT_GUSSET_S3_R], [1, 2, 6],
         [-_cos, _sin, 0.0, -_sin, -_cos, 0.0]),
        (915, 876, 877, [MAT_GUSSET_S3_R], [6],
         [-_cos, _sin, 0.0, -_sin, -_cos, 0.0]),
    ]
    for et, inn, jn, mats, dirs, orient in _weld_L + _weld_R:
        ops.element("zeroLength", et, inn, jn, "-mat", *mats, "-dir", *dirs, "-orient", *orient)

    # ── zeroLengthSection bolted angle connections ──
    # B31-B32, B34-B35, B37-B38, B40-B41, B43-B44: sec 12 (Aggregator W18X60)
    _zls_12_et = [676, 682, 687, 693, 709, 715, 720, 726, 742, 748, 753, 759,
                  775, 781, 786, 792, 808, 814, 819, 825]
    _zls_12_in = [663, 669, 673, 679, 693, 699, 703, 709, 723, 729, 733, 739,
                  753, 759, 763, 769, 783, 789, 793, 799]
    _zls_12_jn = [664, 670, 674, 680, 694, 700, 704, 710, 724, 730, 734, 740,
                  754, 760, 764, 770, 784, 790, 794, 800]
    _define_elements_batch("zeroLengthSection", _zls_12_et, _zls_12_in, _zls_12_jn,
                           SEC_AGG_B31L, "-orient", 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, "-doRayleigh", 0)

    # B33,B36,B39,B42,B45: sec 14 (Aggregator W18X35)
    _zls_14_et = [698, 704, 731, 737, 764, 770, 797, 803, 830, 836]
    _zls_14_in = [683, 689, 713, 719, 743, 749, 773, 779, 803, 809]
    _zls_14_jn = [684, 690, 714, 720, 744, 750, 774, 780, 804, 810]
    _define_elements_batch("zeroLengthSection", _zls_14_et, _zls_14_in, _zls_14_jn,
                           SEC_AGG_B33L, "-orient", 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, "-doRayleigh", 0)

    # B1-B17, B22-B29: sec 2 (Aggregator W16X57)
    _zls_2_et = [331, 337, 342, 348, 364, 370, 375, 381, 397, 403, 408, 414,
                 430, 436, 441, 447, 463, 469, 474, 480, 496, 502, 507, 513,
                 577, 583, 588, 594, 610, 616, 621, 627, 643, 649, 654, 660]
    _zls_2_in = [348, 354, 358, 364, 378, 384, 388, 394, 408, 414, 418, 424,
                 438, 444, 448, 454, 468, 474, 478, 484, 498, 504, 508, 514,
                 573, 579, 583, 589, 603, 609, 613, 619, 633, 639, 643, 649]
    _zls_2_jn = [349, 355, 359, 365, 379, 385, 389, 395, 409, 415, 419, 425,
                 439, 445, 449, 455, 469, 475, 479, 485, 499, 505, 509, 515,
                 574, 580, 584, 590, 604, 610, 614, 620, 634, 640, 644, 650]
    _define_elements_batch("zeroLengthSection", _zls_2_et, _zls_2_in, _zls_2_jn,
                           SEC_AGG_B1L, "-orient", 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, "-doRayleigh", 0)

    # B3,B6,B9,B12,B15,B18,B24,B27,B30: sec 4 (Aggregator W16X26)
    _zls_4_et = [353, 359, 386, 392, 419, 425, 452, 458, 485, 491, 518, 524,
                 599, 605, 632, 638, 665, 671]
    _zls_4_in = [368, 374, 398, 404, 428, 434, 458, 464, 488, 494, 518, 524,
                 593, 599, 623, 629, 653, 659]
    _zls_4_jn = [369, 375, 399, 405, 429, 435, 459, 465, 489, 495, 519, 525,
                 594, 600, 624, 630, 654, 660]
    _define_elements_batch("zeroLengthSection", _zls_4_et, _zls_4_in, _zls_4_jn,
                           SEC_AGG_B3L, "-orient", 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, "-doRayleigh", 0)

    # Individual zeroLengthSection B19: sec 6, B20: sec 8, B21: sec 10
    _zls_ind = [
        (529, 528, 529, SEC_AGG_B19L),
        (540, 539, 540, SEC_AGG_B19L),
        (545, 543, 544, SEC_AGG_B20L),
        (556, 554, 555, SEC_AGG_B20L),
        (561, 558, 559, SEC_AGG_B21L),
        (572, 569, 570, SEC_AGG_B21L),
    ]
    for et, inn, jn, st in _zls_ind:
        ops.element("zeroLengthSection", et, inn, jn, st,
                    "-orient", 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, "-doRayleigh", 0)


# ── 11. ODB ────────────────────────────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: int = 1) -> "opst.post.CreateODB":
    """Initialise opstool ODB for all model output.

    Args:
        output_dir: Directory where ODB files are written.
        odb_tag: ODB identifier tag.

    Returns:
        The active CreateODB instance.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=odb_tag)
    odb.save_model_data()
    return odb


# ── 12. LOADS ──────────────────────────────────────────────────────────────────
def define_gravity_loads():
    """Gravity load pattern: column point loads + beam uniform loads."""
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    # Concentrated column loads (kip → N)
    _col_grav = [
        (8, -42.79), (16, -42.79), (24, -22.305), (28, -58.10), (33, -58.10),
        (38, -25.20), (44, -58.10), (49, -58.10), (54, -25.20), (60, -58.10),
        (65, -58.10), (70, -25.20), (74, -58.10), (79, -58.10), (84, -25.20),
        (92, -42.79), (100, -42.79), (108, -22.305), (116, -42.79), (124, -42.79),
        (132, -22.305), (140, -58.10), (148, -58.10), (156, -25.20),
        (160, -58.10), (165, -58.10), (170, -25.20), (174, -58.10), (179, -58.10),
        (184, -25.20), (192, -58.10), (200, -58.10), (208, -25.20),
        (216, -42.79), (224, -42.79), (232, -22.305),
        (236, -21.853), (241, -21.853), (246, -11.476),
        (250, -29.05), (255, -29.05), (260, -12.60),
        (268, -29.05), (276, -29.05), (284, -12.60),
        (292, -29.05), (300, -29.05), (308, -12.60),
        (312, -29.05), (317, -29.05), (322, -12.60),
        (330, -21.853), (338, -21.853), (346, -11.476),
    ]
    for node, fy_kip in _col_grav:
        ops.load(node, 0.0, fy_kip * kip, 0.0)

    # Uniform beam loads (kip/in → N/mm)
    _w069167 = -0.06916667 * kip / inch   # B1-2, B4-5, B7-8, etc.
    _w030 = -0.030 * kip / inch           # B3, B6, B9, ...
    _w07275 = -0.07275 * kip / inch       # B31-32, B34-35, ...
    _w041958 = -0.04195833 * kip / inch   # B33, B36, B39, ...

    _beam_batches = [
        (_w069167, [329, 332, 334, 336, 339, 340, 343, 345, 347, 350]),
        (_w030, [351, 354, 356, 358, 361]),
        (_w069167, [362, 365, 367, 369, 372, 373, 376, 378, 380, 383]),
        (_w030, [384, 387, 389, 391, 394]),
        (_w069167, [395, 398, 400, 402, 405, 406, 409, 411, 413, 416]),
        (_w030, [417, 420, 422, 424, 427]),
        (_w069167, [428, 431, 433, 435, 438, 439, 442, 444, 446, 449]),
        (_w030, [450, 453, 455, 457, 460]),
        (_w069167, [461, 464, 466, 468, 471, 472, 475, 477, 479, 482]),
        (_w030, [483, 486, 488, 490, 493]),
        (_w069167, [494, 497, 499, 501, 504, 505, 508, 510, 512, 515]),
        (_w030, [516, 519, 521, 523, 526]),
        (_w069167, [527, 530, 532, 534, 535, 537, 539, 542]),
        (_w069167, [543, 546, 548, 550, 551, 553, 555, 558]),
        (_w030, [559, 562, 564, 566, 567, 569, 571, 574]),
        (_w069167, [575, 578, 580, 582, 585, 586, 589, 591, 593, 596]),
        (_w030, [597, 600, 602, 604, 607]),
        (_w069167, [608, 611, 613, 615, 618, 619, 622, 624, 626, 629]),
        (_w030, [630, 633, 635, 637, 640]),
        (_w069167, [641, 644, 646, 648, 651, 652, 655, 657, 659, 662]),
        (_w030, [663, 666, 668, 670, 673]),
        (_w07275, [674, 677, 679, 681, 684, 685, 688, 690, 692, 695]),
        (_w041958, [696, 699, 701, 703, 706]),
        (_w07275, [707, 710, 712, 714, 717, 718, 721, 723, 725, 728]),
        (_w041958, [729, 732, 734, 736, 739]),
        (_w07275, [740, 743, 745, 747, 750, 751, 754, 756, 758, 761]),
        (_w041958, [762, 765, 767, 769, 772]),
        (_w07275, [773, 776, 778, 780, 783, 784, 787, 789, 791, 794]),
        (_w041958, [795, 798, 800, 802, 805]),
        (_w07275, [806, 809, 811, 813, 816, 817, 820, 822, 824, 827]),
        (_w041958, [828, 831, 833, 835, 838]),
    ]
    for w, elems in _beam_batches:
        for e in elems:
            ops.eleLoad("-ele", e, "-type", "-beamUniform", w)


def define_lateral_loads():
    """Pushover load pattern: ELFP lateral forces at floor levels."""
    ops.timeSeries("Linear", 200)
    ops.pattern("Plain", 200, 200)
    lat1 = 21.37474 * kip
    lat2 = 43.58698 * kip
    lat3 = 33.06335 * kip
    ops.load(44, lat1, 0.0, 0.0)
    ops.load(49, lat2, 0.0, 0.0)
    ops.load(54, lat3, 0.0, 0.0)
    ops.load(60, lat1, 0.0, 0.0)
    ops.load(65, lat2, 0.0, 0.0)
    ops.load(70, lat3, 0.0, 0.0)


# ── 13. ANALYSIS ───────────────────────────────────────────────────────────────
def define_damping():
    """Rayleigh damping regions: stiffness-proportional on elastic beams, mass-proportional on floor masses."""
    # Compute Rayleigh coefficients (stiffness-proportional with n_mod factor)
    # a0 = zeta * (2*w_i*w_j)/(w_i+w_j), a1 = zeta * 2/(w_i+w_j)
    # With n_mod=10: w_j = 10*w_i → stiff-proportional approx
    # a1_mod = a1 * n = 2*zeta/(w_i*(1+n)) * n ... simplified from Tcl
    w_i = 2.0 * np.pi * 0.5  # approximate first mode frequency ~0.5 Hz (T≈2s for 3-story CBF)
    a1_mod = 2.0 * zeta / (w_i * (1.0 + n_mod)) * n_mod
    a0 = 2.0 * zeta / (w_i * (1.0 + n_mod))

    # Region 1: Stiffness-proportional damping on elastic beam-column elements
    _region1_ele = [
        7, 8, 15, 16, 23, 24, 26, 27, 29, 31, 32, 34, 36, 37, 39, 41, 42, 44, 46, 47, 49, 51, 52,
        54, 56, 57, 59, 61, 62, 64, 66, 67, 69, 70, 72, 74, 75, 77, 79, 86, 87, 94, 95, 102, 109,
        110, 117, 118, 125, 132, 133, 140, 141, 148, 149, 151, 152, 154, 156, 157, 159, 161, 162,
        164, 165, 167, 169, 170, 172, 174, 181, 182, 189, 190, 197, 204, 205, 212, 213, 220, 221,
        223, 224, 226, 228, 229, 231, 233, 234, 236, 237, 239, 241, 242, 244, 246, 253, 254, 261,
        262, 269, 276, 277, 284, 285, 292, 293, 295, 296, 298, 300, 301, 303, 305, 312, 313, 320,
        321, 328, 329, 332, 334, 336, 339, 340, 343, 345, 347, 350, 351, 354, 356, 358, 361, 362,
        365, 367, 369, 372, 373, 376, 378, 380, 383, 384, 387, 389, 391, 394, 395, 398, 400, 402,
        405, 406, 409, 411, 413, 416, 417, 420, 422, 424, 427, 428, 431, 433, 435, 438, 439, 442,
        444, 446, 449, 450, 453, 455, 457, 460, 461, 464, 466, 468, 471, 472, 475, 477, 479, 482,
        483, 486, 488, 490, 493, 494, 497, 499, 501, 504, 505, 508, 510, 512, 515, 516, 519, 521,
        523, 526, 527, 530, 532, 534, 535, 537, 539, 542, 543, 546, 548, 550, 551, 553, 555, 558,
        559, 562, 564, 566, 567, 569, 571, 574, 575, 578, 580, 582, 585, 586, 589, 591, 593, 596,
        597, 600, 602, 604, 607, 608, 611, 613, 615, 618, 619, 622, 624, 626, 629, 630, 633, 635,
        637, 640, 641, 644, 646, 648, 651, 652, 655, 657, 659, 662, 663, 666, 668, 670, 673, 674,
        677, 679, 681, 684, 685, 688, 690, 692, 695, 696, 699, 701, 703, 706, 707, 710, 712, 714,
        717, 718, 721, 723, 725, 728, 729, 732, 734, 736, 739, 740, 743, 745, 747, 750, 751, 754,
        756, 758, 761, 762, 765, 767, 769, 772, 773, 776, 778, 780, 783, 784, 787, 789, 791, 794,
        795, 798, 800, 802, 805, 806, 809, 811, 813, 816, 817, 820, 822, 824, 827, 828, 831, 833,
        835, 838, 845, 856, 857, 868, 869, 880, 881, 892, 893, 904, 905, 916,
    ]
    ops.region(1, "-ele", *_region1_ele, "-rayleigh", 0.0, 0.0, a1_mod, 0.0)

    # Region 2: Mass-proportional damping on nodes with mass
    ops.region(2, "-node", 534, 549, 564, "-rayleigh", a0, 0.0, 0.0, 0.0)


def run_gravity():
    """Gravity analysis with LoadControl, 20 steps."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-6, 20)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.05)
    ops.analysis("Static")
    for _ in range(20):
        ok = ops.analyze(1)
        if ok != 0:
            break
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def run_pushover(dU_max_mm=457.2, dU_incr_mm=2.0):
    """Pushover analysis using DisplacementControl at roof node."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-4, 20)
    ops.algorithm("Newton")
    ops.integrator("DisplacementControl", NODE_ROOF_CTRL, 1, dU_incr_mm)
    ops.analysis("Static")
    n_steps = int(dU_max_mm / dU_incr_mm)
    for _ in range(n_steps):
        ok = ops.analyze(1)
        if ok != 0:
            break
    ops.wipeAnalysis()


# ── 14. ORCHESTRATOR ──────────────────────────────────────────────────────────
def run_analysis(output_dir: Path):
    """Build model and run gravity + pushover analyses with vis checkpoints."""
    output_dir.mkdir(parents=True, exist_ok=True)
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)
    odb = create_odb(output_dir)
    define_damping()
    define_gravity_loads()
    vis_loads(output_dir)
    run_gravity()
    define_lateral_loads()
    vis_pre_analysis(output_dir)
    run_pushover()
    return odb


# ── 15. POST-PROCESS ──────────────────────────────────────────────────────────
def post_process(odb, output_dir: Path):
    """Save ODB and generate deformed shape visualization."""
    odb.save_response()
    vis_defo(output_dir)


# ── 16. MAIN ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
