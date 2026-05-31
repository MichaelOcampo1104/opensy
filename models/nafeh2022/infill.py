"""
Masonry infill strut model for infilled RC frames (Nafeh, 2020).

Port of the Tcl infill procedure from:
    https://github.com/gerardjoreilly/Infilled-RC-Building-Database

Implements four infill typologies (single, double, triple, truss) as
equivalent diagonal struts with Pinching4 material models. Failure
modes: compression centre, compression corner, shear sliding, diagonal
tension. Drift limits from Sassun et al. (2015).

Ref:
    Nafeh, A. M. B. (2020). Infilled-RC-Building-Database. IUSS Pavia.
    Hak et al. (2012).
    Sassun et al. (2015).

Units: N, mm, MPa  (= N/mm^2)
"""

import math
import openseespy.opensees as ops
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *

# ── Infill property sets (from infill_prop.tcl, Hak et al. 2012) ──────────
# Properties: Ewh, Ewv, Gw, fwv, fwu, fws, tw  (all MPa or mm)
INFILL_PROPS = {
    "weak": {
        "Ewh": 991.0, "Ewv": 1873.0, "Gw": 1089.0,
        "fwv": 2.02,  "fwu": 0.44,   "fws": 0.55,
        "tw": 80.0,
    },
    "medium": {
        "Ewh": 991.0, "Ewv": 1873.0, "Gw": 1089.0,
        "fwv": 1.50,  "fwu": 0.25,   "fws": 0.31,
        "tw": 240.0,
    },
    "strong": {
        "Ewh": 1050.0, "Ewv": 3240.0, "Gw": 1296.0,
        "fwv": 3.51,  "fwu": 0.30,    "fws": 0.36,
        "tw": 300.0,
    },
}


def _pinching4_from_backbone(
    tag: int,
    p_stress: list,
    n_stress: list,
    p_strain: list,
    n_strain: list,
    rDisp: list,
    rForce: list,
    uForce: list,
    gammaK: list,
    gammaD: list,
    gammaF: list,
    gammaE: float,
    damage: str,
) -> None:
    """Create a Pinching4 uniaxial material from backbone parameters."""
    ops.uniaxialMaterial(
        "Pinching4", tag,
        p_stress[0], p_strain[0], p_stress[1], p_strain[1],
        p_stress[2], p_strain[2], p_stress[3], p_strain[3],
        n_stress[0], n_strain[0], n_stress[1], n_strain[1],
        n_stress[2], n_strain[2], n_stress[3], n_strain[3],
        rDisp[0], rForce[0], uForce[0],
        rDisp[1], rForce[1], uForce[1],
        gammaK[0], gammaK[1], gammaK[2], gammaK[3], gammaK[4],
        gammaD[0], gammaD[1], gammaD[2], gammaD[3], gammaD[4],
        gammaF[0], gammaF[1], gammaF[2], gammaF[3], gammaF[4],
        gammaE, damage,
    )


def create_infill(
    ele_tag: int,
    typ: str,
    nds: list,
    B: float,
    H: float,
    hb: float,
    hc: float,
    bc: float,
    tw: float,
    Ec: float,
    Ewh: float,
    Ewv: float,
    Gw: float,
    v: float,
    fwv: float,
    fwu: float,
    fws: float,
    sig_v: float = 0.0,
    GT_inf: int = None,
    pflag: int = 0,
) -> None:
    """Create a masonry infill panel as equivalent diagonal strut(s).

    Args:
        ele_tag: Tag for this infill panel.
        typ: Infill typology ("single", "double", "triple", "truss").
        nds: List of 4 corner node tags [TL, TR, BR, BL]
             (always start from top-left corner).
        B: Bay width centre-to-centre in mm.
        H: Storey height centre-to-centre in mm.
        hb: Beam section depth in mm.
        hc: Column section depth in mm.
        bc: Column section width in mm.
        tw: Infill wall thickness in mm.
        Ec: Concrete elastic modulus in MPa.
        Ewh: Masonry horizontal secant modulus in MPa.
        Ewv: Masonry vertical secant modulus in MPa.
        Gw: Masonry shear modulus in MPa.
        v: Masonry Poisson ratio.
        fwv: Vertical compressive strength in MPa.
        fwu: Sliding shear resistance of mortar joints in MPa.
        fws: Shear resistance under diagonal compression in MPa.
        sig_v: Vertical compression from gravity loading in MPa.
        GT_inf: Geometric transformation tag for rigid links (truss type only).
        pflag: Print flag (0 = silent, 1+ = verbose).
    """
    pi = math.pi

    # ── Geometry ──────────────────────────────────────────────────────────
    Ic = bc * hc**3 / 12.0              # mm^4
    Bw = B - hc                          # mm
    Hw = H - hb                          # mm
    theta = math.atan(Hw / Bw)           # rad
    dw = math.sqrt(Bw * Bw + Hw * Hw)    # mm

    # Directional modulus (Hankinson-type formula)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    Ewtheta = 1.0 / (
        cos_t**4 / Ewh
        + sin_t**4 / Ewv
        + cos_t**2 * sin_t**2 * (1.0 / Gw - 2.0 * v / Ewv)
    )

    # Contact length
    lambdaH = H * (Ewtheta * tw * math.sin(2.0 * theta) / (4.0 * Ec * Ic * Hw)) ** 0.25
    z = pi / (2.0 * lambdaH) * H          # mm
    s = z / 3.0                            # mm

    # ── Strut width (Stafford-Smith & Carter, 1969) ────────────────────────
    if lambdaH < 3.14:
        K1, K2 = 1.300, -0.178
    elif lambdaH <= 7.85:
        K1, K2 = 0.707, 0.010
    else:
        K1, K2 = 0.470, 0.040

    bw = dw * (K1 / lambdaH + K2)          # mm
    Aw = bw * tw                            # mm^2  (N-mm-MPa: mm^2, not m^2)

    # ── Critical stress (four failure modes) ──────────────────────────────
    sigw1 = 1.16 * fwv * math.tan(theta) / (K1 + K2 * lambdaH)
    sigw2 = (1.12 * fwv * sin_t * cos_t
             / (K1 * lambdaH**-0.12 + K2 * lambdaH**0.88))
    sigw3 = ((fwu * (1.2 * sin_t + 0.45 * cos_t) + 0.3 * sig_v)
             * dw / bw)
    sigw4 = (0.6 * fws + 0.3 * sig_v) * dw / bw

    sigw = sigw1
    if sigw2 < sigw: sigw = sigw2
    if sigw3 < sigw: sigw = sigw3
    if sigw4 < sigw: sigw = sigw4

    # ── Hysteretic parameters ─────────────────────────────────────────────
    sigDS2 = sigw                     # peak stress (already MPa)
    sigDS1 = 0.80 * sigDS2            # cracking
    sigDS4 = 0.10 * sigDS2            # residual

    # Drift limits from Sassun et al. (2015)
    thetaDS1 = 0.0018
    thetaDS2 = 0.0046
    thetaDS3 = 0.0105
    thetaDS4 = 0.0188

    # eps-to-theta transformation
    B_over_H = B / H
    epsDS1 = 1.0 - math.sqrt((1.0 + (B_over_H - thetaDS1)**2) / (1.0 + B_over_H**2))
    epsDS2 = 1.0 - math.sqrt((1.0 + (B_over_H - thetaDS2)**2) / (1.0 + B_over_H**2))
    epsDS3 = 1.0 - math.sqrt((1.0 + (B_over_H - thetaDS3)**2) / (1.0 + B_over_H**2))
    epsDS4 = 1.0 - math.sqrt((1.0 + (B_over_H - thetaDS4)**2) / (1.0 + B_over_H**2))

    # ── Create Pinching4 material ─────────────────────────────────────────
    if typ == "truss":
        deltaDS1 = thetaDS1 * H / 2.0
        deltaDS2 = thetaDS2 * H / 2.0
        deltaDS4 = thetaDS4 * H / 2.0

        forceDS1 = sigDS1 * Aw
        forceDS2 = sigDS2 * Aw
        forceDS4 = sigDS4 * Aw

        pF = [forceDS1, forceDS2, forceDS4, forceDS4]
        nF = [-forceDS1, -forceDS2, -forceDS4, -forceDS4]
        pD = [deltaDS1, deltaDS2, deltaDS4, deltaDS4]
        nD = [-deltaDS1, -deltaDS2, -deltaDS4, -deltaDS4]

        mat_tag = 9000 + ele_tag
    else:
        pF = [0.001, 0.002, 0.001, 0.001]  # pos stress (compression ≈ 0)
        nF = [-sigDS1, -sigDS2, -sigDS4, -sigDS4]   # neg stress (tension)
        pD = [epsDS1, epsDS2, epsDS4, epsDS4]        # pos strain (extension)
        nD = [-epsDS1, -epsDS2, -epsDS4, -epsDS4]    # neg strain (compression)

        mat_tag = 8000 + ele_tag

    rDisp = [0.8, 0.8]
    rForce = [0.1, 0.1]
    uForce = [0.0, 0.0]
    gammaK = [0.0, 0.0, 0.0, 0.0, 0.0]
    gammaD = [0.0, 0.0, 0.0, 0.0, 0.0]
    gammaF = [0.0, 0.0, 0.0, 0.0, 0.0]
    gammaE = 0.0
    dam = "energy"

    _pinching4_from_backbone(mat_tag, pF, nF, pD, nD,
                             rDisp, rForce, uForce,
                             gammaK, gammaD, gammaF, gammaE, dam)

    # ── Create elements ───────────────────────────────────────────────────
    if typ == "single":
        nI = nds[0]  # TL
        nJ = nds[1]  # TR
        nK = nds[2]  # BR
        nL = nds[3]  # BL

        ops.element("truss", int(f"{ele_tag}1"), nI, nK, Aw, mat_tag,
                    "-doRayleigh", 1)
        ops.element("truss", int(f"{ele_tag}2"), nL, nJ, Aw, mat_tag,
                    "-doRayleigh", 1)

    elif typ == "double":
        nI1, nI2 = nds[0], nds[1]
        nJ1, nJ2 = nds[2], nds[3]
        nK1, nK2 = nds[4], nds[5]
        nL1, nL2 = nds[6], nds[7]

        Aw_half = 0.5 * Aw
        ops.element("truss", int(f"{ele_tag}1"), nI1, nK2, Aw_half, mat_tag,
                    "-doRayleigh", 1)
        ops.element("truss", int(f"{ele_tag}2"), nI2, nK1, Aw_half, mat_tag,
                    "-doRayleigh", 1)
        ops.element("truss", int(f"{ele_tag}3"), nL1, nJ2, Aw_half, mat_tag,
                    "-doRayleigh", 1)
        ops.element("truss", int(f"{ele_tag}4"), nL2, nJ1, Aw_half, mat_tag,
                    "-doRayleigh", 1)

    elif typ == "triple":
        nI1, nI2, nI3 = nds[0], nds[1], nds[2]
        nJ1, nJ2, nJ3 = nds[3], nds[4], nds[5]
        nK1, nK2, nK3 = nds[6], nds[7], nds[8]
        nL1, nL2, nL3 = nds[9], nds[10], nds[11]

        Aw_025 = 0.25 * bw * tw   # outer struts
        Aw_050 = 0.50 * bw * tw   # centre strut

        ops.element("truss", int(f"{ele_tag}1"), nI1, nK3, Aw_025, mat_tag,
                    "-doRayleigh", 1)
        ops.element("truss", int(f"{ele_tag}2"), nI2, nK2, Aw_050, mat_tag,
                    "-doRayleigh", 1)
        ops.element("truss", int(f"{ele_tag}3"), nI3, nK1, Aw_025, mat_tag,
                    "-doRayleigh", 1)
        ops.element("truss", int(f"{ele_tag}4"), nL1, nJ3, Aw_025, mat_tag,
                    "-doRayleigh", 1)
        ops.element("truss", int(f"{ele_tag}5"), nL2, nJ2, Aw_050, mat_tag,
                    "-doRayleigh", 1)
        ops.element("truss", int(f"{ele_tag}6"), nL3, nJ1, Aw_025, mat_tag,
                    "-doRayleigh", 1)

    elif typ == "truss":
        if GT_inf is None:
            raise ValueError("GT_inf (geometric transform tag) is required for truss typology.")

        nI = nds[0]  # TL
        nJ = nds[1]  # TR
        nK = nds[2]  # BR
        nL = nds[3]  # BL

        # Centre nodes
        cNodeU = 30000 + ele_tag
        cNodeL = 40000 + ele_tag

        nIX = ops.nodeCoord(nI, 1)
        nIY = ops.nodeCoord(nI, 2)
        nIZ = ops.nodeCoord(nI, 3)

        # Assumes infill is in X-direction (direction 1)
        ops.node(cNodeU, nIX + 0.5 * B, nIY, nIZ - 0.5 * H,
                 "-mass", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        ops.node(cNodeL, nIX + 0.5 * B, nIY, nIZ - 0.5 * H,
                 "-mass", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        # Rigid link properties (very stiff elastic)
        Ar = 0.5        # mm^2 (stiff but tiny)
        Ir = 0.1        # mm^4
        Er = 1e10       # MPa
        Gr = 1e10       # MPa
        Jr = 0.1        # mm^4

        # Rigid links to centre nodes
        ops.element("elasticBeamColumn", int(f"{ele_tag}1"), nI, cNodeU,
                    Ar, Er, Gr, Jr, Ir, Ir, GT_inf)
        ops.element("elasticBeamColumn", int(f"{ele_tag}2"), nJ, cNodeU,
                    Ar, Er, Gr, Jr, Ir, Ir, GT_inf)
        ops.element("elasticBeamColumn", int(f"{ele_tag}3"), nK, cNodeL,
                    Ar, Er, Gr, Jr, Ir, Ir, GT_inf)
        ops.element("elasticBeamColumn", int(f"{ele_tag}4"), nL, cNodeL,
                    Ar, Er, Gr, Jr, Ir, Ir, GT_inf)

        # Zero-length masonry spring between centre nodes
        ops.element("zeroLength", int(f"{ele_tag}0"), cNodeU, cNodeL,
                    "-mat", mat_tag, "-dir", 1)

    # ── Print output ──────────────────────────────────────────────────────
    if pflag > 0:
        if typ == "single":
            pass  # original Tcl doesn't print for single
        elif typ == "double":
            print(f"Created Double-Strut Infill Wall {ele_tag} between: "
                  f"{nds[0]}-{nds[5]}/{nds[1]}-{nds[4]} and "
                  f"{nds[6]}-{nds[3]}/{nds[7]}-{nds[2]}")
        elif typ == "triple":
            print(f"Created Triple-Strut Infill Wall {ele_tag} between: "
                  f"{nds[0]}-{nds[8]}/{nds[1]}-{nds[7]}/{nds[2]}-{nds[6]} and "
                  f"{nds[9]}-{nds[5]}/{nds[10]}-{nds[4]}/{nds[11]}-{nds[3]}")
        elif typ == "truss":
            print(f"Created Truss Infill Wall {ele_tag} between: "
                  f"{nds[0]}-{nds[2]} and {nds[3]}-{nds[1]}")

    if pflag > 1:
        print(f"bw: {bw:.1f}mm dw: {dw:.1f}mm tw: {tw:.1f}mm "
              f"z:{z:.1f}mm s:{s:.1f}mm theta:{theta:.4f}rad")
        print(f"sigw: {sigw:.2f}MPa Ewtheta:{Ewtheta:.2f}MPa Aw:{Aw:.1f}mm2")

    if pflag > 2:
        print(f"sigDS1: {sigDS1:.2f} sigDS2: {sigDS2:.2f} sigDS4: {sigDS4:.2f} (MPa)")

    if pflag > 3:
        print("Mechanism Parameters:")
        print(f"Compression in centre: {sigw1:.3f} MPa")
        print(f"Compression at corners: {sigw2:.3f} MPa")
        print(f"Shear sliding: {sigw3:.3f} MPa")
        print(f"Diagonal tension: {sigw4:.3f} MPa")
