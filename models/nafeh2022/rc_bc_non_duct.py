"""
Non-ductile RC beam-column element with lumped plasticity (O'Reilly, 2019).

Port of the Tcl rcBC_nonDuct and MomentCurvature procedures from:
    https://github.com/gerardjoreilly/Numerical-Modelling-of-GLD-RC-Frames

Creates a force-based beam-column element with Pinching4 flexural hinges
at both ends, aggregated with an uncoupled shear hinge (optional).

Units: N, mm, MPa  (= N/mm^2)

Refs:
    O'Reilly, G. J., Sullivan, T. J. (2019) J. Earthquake Eng., 23(8), 1262-1296.
    Zimos, D. K., Mergos, P. E., Kappos, A. J. (2015) COMPDYN 2015.
    Scott, M. H., Fenves, G. L. (2006) J. Struct. Eng., 132(2), 244-252.
"""

import math
import openseespy.opensees as ops
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *


def _moment_curvature(
    index: str,
    h: float,
    b: float,
    cv: float,
    dbL: float,
    dbV: float,
    fc: float,
    Ec: float,
    P: float,
    fyL: float,
    Es: float,
    rho1: float,
    rho2: float,
    rho3: float,
    pflag: int = 0,
) -> tuple:
    """Moment-curvature analysis to compute yield moment and neutral axis depth.

    Performs an iterative section analysis to determine the moment capacity
    at first yield, for both positive and negative bending.

    Args:
        index: Suffix string for upvar return values (e.g. "1zz").
        h: Section height in mm.
        b: Section width in mm.
        cv: Concrete cover in mm.
        dbL: Longitudinal bar diameter in mm.
        dbV: Transverse bar diameter in mm.
        fc: Concrete compressive strength in MPa.
        Ec: Concrete elastic modulus in MPa.
        P: Axial force in N (compression positive).
        fyL: Steel yield strength in MPa.
        Es: Steel elastic modulus in MPa.
        rho1: Top reinforcement ratio.
        rho2: Mid reinforcement ratio.
        rho3: Bottom reinforcement ratio.
        pflag: Print flag.

    Returns:
        dict with keys: Myp, Myn, cp, cn (yield moments in N-mm, NA depths in mm).
    """
    n_c = 0.8 + fc / 18.0
    e_c = 1.0 * fc / Ec * (n_c / (n_c - 1.0))
    e_s = fyL / Es

    phiY = 2.1 * fyL / Es / h      # yield curvature [1/mm]

    d1 = cv + dbV + dbL / 2.0      # depth to top bars [mm]
    d2 = h / 2.0                    # depth to middle bars [mm]
    d3 = h - cv - dbV - dbL / 2.0   # depth to bottom bars [mm]

    def _solve_bending(positive: bool) -> tuple:
        """Iterate to find neutral axis depth and yield moment."""
        c = h / 2.0               # initial trial NA depth [mm]
        count = 0
        err = 0.5

        while err > 0.001 and count < 1000:
            if positive:
                e_s1 = (c - d1) * phiY
                e_s2 = (d2 - c) * phiY
                e_s3 = (d3 - c) * phiY
            else:
                e_s1 = (c - d1) * phiY
                e_s2 = (d2 - c) * phiY
                e_s3 = (d3 - c) * phiY

            e_top = c * phiY

            # Steel stress
            f_s1 = e_s1 * Es if abs(e_s1) < e_s else fyL * (1.0 if e_s1 >= 0 else -1.0)
            f_s2 = e_s2 * Es if abs(e_s2) < e_s else fyL * (1.0 if e_s2 >= 0 else -1.0)
            f_s3 = e_s3 * Es if abs(e_s3) < e_s else fyL * (1.0 if e_s3 >= 0 else -1.0)

            # Steel forces  [N]
            if positive:
                Fs1 = f_s1 * rho1 * b * d3 if f_s1 >= 0 else f_s1 * rho1 * b * d3
                Fs3 = f_s3 * rho3 * b * d3
            else:
                Fs1 = f_s1 * rho3 * b * d3
                Fs3 = f_s3 * rho1 * b * d3
            Fs2 = f_s2 * rho2 * b * d3

            # Concrete stress block
            ec_ratio = e_top / e_c
            a1b1 = ec_ratio - ec_ratio ** 2 / 3.0
            b1 = (4.0 - ec_ratio) / (6.0 - 2.0 * ec_ratio)
            Fc = a1b1 * c * fc * b          # concrete compression force [N]

            # Section force balance
            Psec = P + Fs2 + Fs3 - Fc - Fs1

            # Adjust NA depth
            if Psec < 0:
                c -= 0.001
            else:
                c += 0.001

            err = abs(Psec)
            if err < 5.0:
                break
            count += 1

        if positive:
            Mp = (P * (0.5 * h - c)
                  + Fs1 * (c - d1)
                  + Fs3 * (d3 - c)
                  + Fs2 * (d2 - c)
                  + Fc * c * (1.0 - b1 / 2.0))
        else:
            Mp = (P * (0.5 * h - c)
                  + Fs1 * (c - d1)
                  + Fs3 * (d3 - c)
                  + Fs2 * (d2 - c)
                  + Fc * c * (1.0 - b1 / 2.0))

        return Mp, c

    Myp, cp = _solve_bending(positive=True)
    Myn, cn = _solve_bending(positive=False)

    result = {f"Myp{index}": Myp, f"Myn{index}": Myn,
              f"cp{index}": cp, f"cn{index}": cn}

    if pflag >= 1:
        print(f"Myp{index}: {Myp:.1f} N-mm")
        print(f"Myn{index}: {Myn:.1f} N-mm")

    return result


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


def create_rc_column(
    ST: int,
    ET: int,
    GT: int,
    iNode: int,
    jNode: int,
    fyL: float,
    fyV: float,
    Es: float,
    fc: float,
    Ec: float,
    b: float,
    h: float,
    s: float,
    cv: float,
    dbL: float,
    dbV: float,
    P: float,
    Ls: float,
    rho_shr: float,
    rho_top1zz: float,
    rho_mid1zz: float,
    rho_bot1zz: float,
    rho_top2zz: float,
    rho_mid2zz: float,
    rho_bot2zz: float,
    rho_top1yy: float,
    rho_mid1yy: float,
    rho_bot1yy: float,
    rho_top2yy: float,
    rho_mid2yy: float,
    rho_bot2yy: float,
    pfile,
    pflag: int = 0,
) -> None:
    """Create a force-based beam-column element with lumped plasticity hinges.

    Args:
        ST: Shear hinge flag (0 = no shear hinge, 1 = include shear hinge).
        ET: Element tag.
        GT: Geometric transformation tag.
        iNode, jNode: End node tags.
        fyL: Longitudinal steel yield strength [MPa].
        fyV: Transverse steel yield strength [MPa].
        Es: Steel elastic modulus [MPa].
        fc: Concrete compressive strength [MPa].
        Ec: Concrete elastic modulus [MPa].
        b: Section width [mm].
        h: Section height [mm].
        s: Stirrup spacing [mm].
        cv: Concrete cover [mm].
        dbL: Longitudinal bar diameter [mm].
        dbV: Transverse bar diameter [mm].
        P: Axial force [N] (compression positive).
        Ls: Shear span [mm].
        rho_shr: Shear reinforcement ratio (Ash / b / s).
        rho_top1zz, rho_mid1zz, rho_bot1zz: Reinf. ratios at end 1 about zz.
        rho_top2zz, rho_mid2zz, rho_bot2zz: Reinf. ratios at end 2 about zz.
        rho_top1yy, rho_mid1yy, rho_bot1yy: Reinf. ratios at end 1 about yy.
        rho_top2yy, rho_mid2yy, rho_bot2yy: Reinf. ratios at end 2 about yy.
        pfile: Open file handle for property output.
        pflag: Print flag.
    """
    # ── Section properties ──────────────────────────────────────────────
    nu = P / (b * h * fc)              # normalised axial load ratio
    dyy = h - dbV - cv - dbL / 2.0     # depth to bottom bars, zz axis
    dzz = b - dbV - cv - dbL / 2.0     # depth to bottom bars, yy axis

    Ag = b * h                                          # [mm^2]
    Izz = b * h ** 3 / 12.0                             # [mm^4]
    Iyy = h * b ** 3 / 12.0                             # [mm^4]
    EIzz_val = Ec * Izz                                 # [N*mm^2]
    EIyy_val = Ec * Iyy                                 # [N*mm^2]
    EA = Ec * Ag                                        # [N]
    Gc_val = 0.4 * Ec                                   # shear modulus [MPa]
    Kshear = Gc_val * Ag                                # [N]

    n_c = 0.8 + fc / 18.0
    e_c = 1.0 * fc / Ec * (n_c / (n_c - 1.0))
    e_s = fyL / Es

    # Torsional constant  [mm^4]
    if h >= b:
        J = h * b ** 3 * (0.333 - 0.21 * (h / b) * (1.0 - (b / h) ** 4 / 12.0))
    else:
        J = b * h ** 3 * (0.333 - 0.21 * (b / h) * (1.0 - (h / b) ** 4 / 12.0))

    # ── Member length from node coordinates ────────────────────────────
    x1 = ops.nodeCoord(iNode, 1)
    y1 = ops.nodeCoord(iNode, 2)
    z1 = ops.nodeCoord(iNode, 3)
    x2 = ops.nodeCoord(jNode, 1)
    y2 = ops.nodeCoord(jNode, 2)
    z2 = ops.nodeCoord(jNode, 3)
    L = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

    # ── Yield curvature ────────────────────────────────────────────────
    phiYzz = 2.1 * fyL / Es / h      # [1/mm]
    phiYyy = 2.1 * fyL / Es / b      # [1/mm]

    # ── Moment-curvature analysis ──────────────────────────────────────
    mc1zz = _moment_curvature("1zz", h, b, cv, dbL, dbV,
                              fc, Ec, P, fyL, Es,
                              rho_top1zz, rho_mid1zz, rho_bot1zz, pflag)
    mc2zz = _moment_curvature("2zz", h, b, cv, dbL, dbV,
                              fc, Ec, P, fyL, Es,
                              rho_top2zz, rho_mid2zz, rho_bot2zz, pflag)
    mc1yy = _moment_curvature("1yy", b, h, cv, dbL, dbV,
                              fc, Ec, P, fyL, Es,
                              rho_top1yy, rho_mid1yy, rho_bot1yy, pflag)
    mc2yy = _moment_curvature("2yy", b, h, cv, dbL, dbV,
                              fc, Ec, P, fyL, Es,
                              rho_top2yy, rho_mid2yy, rho_bot2yy, pflag)

    Myp1zz = mc1zz["Myp1zz"]
    Myn1zz = mc1zz["Myn1zz"]
    Myp2zz = mc2zz["Myp2zz"]
    Myn2zz = mc2zz["Myn2zz"]
    Myp1yy = mc1yy["Myp1yy"]
    Myn1yy = mc1yy["Myn1yy"]
    Myp2yy = mc2yy["Myp2yy"]
    Myn2yy = mc2yy["Myn2yy"]

    cp1zz = mc1zz["cp1zz"]
    cn1zz = mc1zz["cn1zz"]
    cp2zz = mc2zz["cp2zz"]
    cn2zz = mc2zz["cn2zz"]
    cp1yy = mc1yy["cp1yy"]
    cn1yy = mc1yy["cn1yy"]
    cp2yy = mc2yy["cp2yy"]
    cn2yy = mc2yy["cn2yy"]

    # ── Initial cracked stiffness ──────────────────────────────────────
    Kizz = Myp1zz / phiYzz      # initial cracked stiffness about zz [N*mm²]
    Kiyy = Myp1yy / phiYyy      # initial cracked stiffness about yy [N*mm²]
    EIrzz = Kizz / EIzz_val     # ratio gross-to-cracked EI
    EIryy = Kiyy / EIyy_val
    EIzze = EIrzz * EIzz_val    # cracked EI about zz [N*mm²]
    EIyye = EIryy * EIyy_val    # cracked EI about yy [N*mm²]
    Izze = EIrzz * Izz          # cracked I about zz [mm⁴]
    Iyye = EIryy * Iyy          # cracked I about yy [mm⁴]

    # ── Capping moment (1.077 * My) ─────────────────────────────────────
    Mcp1zz = 1.077 * Myp1zz
    Mcn1zz = 1.077 * Myn1zz
    Mcp2zz = 1.077 * Myp2zz
    Mcn2zz = 1.077 * Myn2zz
    Mcp1yy = 1.077 * Myp1yy
    Mcn1yy = 1.077 * Myn1yy
    Mcp2yy = 1.077 * Myp2yy
    Mcn2yy = 1.077 * Myn2yy

    # ── Ultimate moment (0.8 * Mc) ──────────────────────────────────────
    Mup1zz = 0.8 * Mcp1zz
    Mun1zz = 0.8 * Mcn1zz
    Mup2zz = 0.8 * Mcp2zz
    Mun2zz = 0.8 * Mcn2zz
    Mup1yy = 0.8 * Mcp1yy
    Mun1yy = 0.8 * Mcn1yy
    Mup2yy = 0.8 * Mcp2yy
    Mun2yy = 0.8 * Mcn2yy

    # ── Plastic hinge length (Priestley + Park, 1992) ──────────────────
    Lp = 0.08 * Ls + 0.022 * fyL * dbL     # [mm]

    # ── Ultimate curvature ─────────────────────────────────────────────
    mu_phi = 22.651 - 47.348 * nu
    # Check limits
    if nu < 0.1:
        mu_phi = 22.651 - 47.348 * 0.1
    if nu > 0.25:
        mu_phi = 22.651 - 47.348 * 0.25
    if nu > 0.999:
        print(f"WARNING: Element {ET} has axial load ratio > 1.0!")

    phiUzz = phiYzz * mu_phi       # [1/mm]
    phiUyy = phiYyy * mu_phi       # [1/mm]

    # ── Capping curvature ──────────────────────────────────────────────
    app = -0.1437 * nu - 0.0034
    if nu < 0.1:
        app = -0.1437 * 0.1 - 0.0034
    phiCzz = phiUzz + (0.2 * 1.077 * phiYzz) / app
    phiCyy = phiUyy + (0.2 * 1.077 * phiYyy) / app

    # ── Exhaustion curvature (rebar fracture at ε = 0.08) ──────────────
    phi0zz = 0.08 / (dzz - cp1zz) if (dzz - cp1zz) > 0 else 1.0
    phi0yy = 0.08 / (dyy - cp1yy) if (dyy - cp1yy) > 0 else 1.0

    # ── Maximum (residual) capacity ─────────────────────────────────────
    Mmp1zz = 0.1 * Mcp1zz
    Mmp2zz = 0.1 * Mcp2zz
    Mmp1yy = 0.1 * Mcp1yy
    Mmp2yy = 0.1 * Mcp2yy
    Mmn1zz = 0.1 * Mcn1zz
    Mmn2zz = 0.1 * Mcn2zz
    Mmn1yy = 0.1 * Mcn1yy
    Mmn2yy = 0.1 * Mcn2yy

    phiMp1zz = phiCzz + (Mmp1zz - Mcp1zz) * phiYzz / (app * Myp1zz)
    phiMp2zz = phiCzz + (Mmp2zz - Mcp2zz) * phiYzz / (app * Myp2zz)
    phiMp1yy = phiCyy + (Mmp1yy - Mcp1yy) * phiYyy / (app * Myp1yy)
    phiMp2yy = phiCyy + (Mmp2yy - Mcp2yy) * phiYyy / (app * Myp2yy)

    phiMn1zz = phiCzz + (Mmn1zz - Mcn1zz) * phiYzz / (app * Myn1zz)
    phiMn2zz = phiCzz + (Mmn2zz - Mcn2zz) * phiYzz / (app * Myn2zz)
    phiMn1yy = phiCyy + (Mmn1yy - Mcn1yy) * phiYyy / (app * Myn1yy)
    phiMn2yy = phiCyy + (Mmn2yy - Mcn2yy) * phiYyy / (app * Myn2yy)

    # ── Shear backbone (if ST > 0) ─────────────────────────────────────
    if ST > 0:
        ft = math.sqrt(fc) / 3.0           # tensile strength [MPa]

        V_cryy = ft * h / Ls * math.sqrt(1.0 + P / (ft * b * h)) * 0.8 * b * h
        V_crzz = ft * b / Ls * math.sqrt(1.0 + P / (ft * h * b)) * 0.8 * h * b

        gamm_cryy = V_cryy / Kshear
        gamm_crzz = V_crzz / Kshear

        # Shear capacity (Priestley et al., 1993)
        V_cyy = (0.29 * math.sqrt(fc) * 0.8 * b * h
                 + P * math.tan(h / 2.0 / Ls)
                 + rho_shr * b * fyV * (dyy - cv - dbV - dbL / 2.0))
        V_czz = (0.29 * math.sqrt(fc) * 0.8 * h * b
                 + P * math.tan(b / 2.0 / Ls)
                 + rho_shr * h * fyV * (dzz - cv - dbV - dbL / 2.0))

        GA1yy = (Es * b * (dyy - cv - dbV - dbL / 2.0) * rho_shr
                 / (1.0 + 4.0 * Es / Ec * rho_shr))
        GA1zz = (Es * h * (dzz - cv - dbV - dbL / 2.0) * rho_shr
                 / (1.0 + 4.0 * Es / Ec * rho_shr))

        paramV1yy = Ls / h if (Ls / h) <= 2.5 else 2.5
        paramV1zz = Ls / b if (Ls / b) <= 2.5 else 2.5

        gamm_pkyy = ((gamm_cryy + (V_cyy - V_cryy) / GA1yy)
                     * (1.0 - 1.07 * nu) * (5.37 - 1.59 * paramV1yy))
        gamm_pkzz = ((gamm_crzz + (V_czz - V_crzz) / GA1zz)
                     * (1.0 - 1.07 * nu) * (5.37 - 1.59 * paramV1zz))

        # Failure
        paramV2 = nu if nu < 0.4 else 0.4
        omega_k = rho_shr * fyV / fc
        paramV3 = omega_k if omega_k <= 0.08 else 0.08

        gamm_u1yy = ((1.0 - 2.5 * paramV2) * paramV1yy ** 2
                     * (0.31 + 17.8 * paramV3) * gamm_pkyy)
        gamm_u1zz = ((1.0 - 2.5 * paramV2) * paramV1zz ** 2
                     * (0.31 + 17.8 * paramV3) * gamm_pkzz)

        V_ccyy = V_cyy * 0.9      # residual (OpenSees cannot handle 0)
        V_cczz = V_czz * 0.9

        if gamm_u1yy <= gamm_pkyy:
            gamm_uyy = gamm_pkyy
            V_ccyy = V_cyy
        else:
            gamm_uyy = gamm_u1yy

        if gamm_u1zz <= gamm_pkzz:
            gamm_uzz = gamm_pkzz
            V_cczz = V_czz
        else:
            gamm_uzz = gamm_u1zz

        # Descending branch
        nu_lyy = (P / ((rho_top1zz + rho_bot1zz) * fyL * b * dyy)) if (rho_top1zz + rho_bot1zz) > 0 else 1e6
        nu_lzz = (P / ((rho_top1yy + rho_bot1yy) * fyL * h * dzz)) if (rho_top1yy + rho_bot1yy) > 0 else 1e6

        tau_aveyy = V_cyy / b / dyy
        tau_avezz = V_czz / h / dzz

        A_confpcyy = ((dyy - cv - dbV - dbL / 2.0) * (b - 2.0 * (cv + dbV + dbL))
                      / b / h)
        A_confpczz = ((dzz - cv - dbV - dbL / 2.0) * (h - 2.0 * (cv + dbV + dbL))
                      / h / b)

        if (A_confpcyy > 0 and tau_aveyy > 0 and nu_lyy > 0
                and rho_shr > 0 and s > 0):
            gamm_tppyy = (0.65 * ((rho_top1zz + rho_bot1zz) / A_confpcyy) ** 1.2
                          * math.sqrt(rho_shr * fyV / nu_lyy / (s / dyy)
                                      / (tau_aveyy / math.sqrt(fc))))
        else:
            gamm_tppyy = 0.0

        if (A_confpczz > 0 and tau_avezz > 0 and nu_lzz > 0
                and rho_shr > 0 and s > 0):
            gamm_tppzz = (0.65 * ((rho_top1yy + rho_bot1yy) / A_confpczz) ** 1.2
                          * math.sqrt(rho_shr * fyV / nu_lzz / (s / dzz)
                                      / (tau_avezz / math.sqrt(fc))))
        else:
            gamm_tppzz = 0.0

        gamm_myy = gamm_uyy + gamm_tppyy
        gamm_mzz = gamm_uzz + gamm_tppzz

        V_resyy = V_cyy * (1.0 - (1.0 / gamm_tppyy if gamm_tppyy > 0 else 0) * gamm_tppyy
                           if gamm_tppyy > 0 else V_cyy)
        # Hmm, the original formula is: V_res = V_c * (1 - Spp * gamm_tpp)
        # where Spp was computed but I skipped it in the conversion.
        # Let me compute Spp:
        Sppyy = (7.36 + 0.28 * math.sqrt(nu + 0.02) / (rho_shr + 0.0011)
                 / ((rho_top1zz + rho_bot1zz) * fyL * dbL / A_confpcyy / dyy + 0.06)) if A_confpcyy > 0 else 0
        Sppzz = (7.36 + 0.28 * math.sqrt(nu + 0.02) / (rho_shr + 0.0011)
                 / ((rho_top1yy + rho_bot1yy) * fyL * dbL / A_confpczz / dzz + 0.06)) if A_confpczz > 0 else 0

        V_resyy = V_cyy * (1.0 - Sppyy * gamm_tppyy)
        V_reszz = V_czz * (1.0 - Sppzz * gamm_tppzz)

        if V_resyy <= 0:
            V_resyy = 0.1 * V_cyy
            gamm_myy = gamm_uyy + 1.0 / Sppyy if Sppyy > 0 else gamm_uyy
        if V_reszz <= 0:
            V_reszz = 0.1 * V_czz
            gamm_mzz = gamm_uzz + 1.0 / Sppzz if Sppzz > 0 else gamm_uzz

    # ── Print output ───────────────────────────────────────────────────
    if pflag:
        print(f"Element {ET} between nodes {iNode} and {jNode}")
        _p = lambda name, v1, v2, v3, v4: print(
            f"  {name}: {v1:.1f} {v2:.1f} {v3:.1f} {v4:.1f}")
        _p("Myp1zz Myp2zz Myp1yy Myp2yy", Myp1zz, Myp2zz, Myp1yy, Myp2yy)
        _p("Myn1zz Myn2zz Myn1yy Myn2yy", Myn1zz, Myn2zz, Myn1yy, Myn2yy)
        _p("Mcp1zz Mcp2zz Mcp1yy Mcp2yy", Mcp1zz, Mcp2zz, Mcp1yy, Mcp2yy)
        _p("Mcn1zz Mcn2zz Mcn1yy Mcn2yy", Mcn1zz, Mcn2zz, Mcn1yy, Mcn2yy)
        print(f"  Lp: {Lp:.1f} mm  nu: {nu:.3f}  L: {L:.1f} mm")

    pfile.write(
        f"Element {ET} between nodes {iNode} and {jNode} "
        f"Myp1zz: {Myp1zz:.1f} Myp2zz: {Myp2zz:.1f} "
        f"Myp1yy: {Myp1yy:.1f} Myp2yy: {Myp2yy:.1f} "
        f"Myn1zz: {Myn1zz:.1f} Myn2zz: {Myn2zz:.1f} "
        f"phiYzz: {phiYzz:.6f} phiYyy: {phiYyy:.6f} ...\n"
    )

    # ── Create flexural Pinching4 materials ─────────────────────────────
    pMom1zz = [Myp1zz, Mcp1zz, Mup1zz, Mmp1zz]
    pMom2zz = [Myp2zz, Mcp2zz, Mup2zz, Mmp2zz]
    nMom1zz = [-Myn1zz, -Mcn1zz, -Mun1zz, -Mmn1zz]
    nMom2zz = [-Myn2zz, -Mcn2zz, -Mun2zz, -Mmn2zz]
    pMom1yy = [Myp1yy, Mcp1yy, Mup1yy, Mmp1yy]
    pMom2yy = [Myp2yy, Mcp2yy, Mup2yy, Mmp2yy]
    nMom1yy = [-Myn1yy, -Mcn1yy, -Mun1yy, -Mmn1yy]
    nMom2yy = [-Myn2yy, -Mcn2yy, -Mun2yy, -Mmn2yy]

    pCurv1zz = [phiYzz, phiCzz, phiUzz, phiMp1zz]
    pCurv2zz = [phiYzz, phiCzz, phiUzz, phiMp2zz]
    nCurv1zz = [-phiYzz, -phiCzz, -phiUzz, -phiMn1zz]
    nCurv2zz = [-phiYzz, -phiCzz, -phiUzz, -phiMn2zz]
    pCurv1yy = [phiYyy, phiCyy, phiUyy, phiMp1yy]
    pCurv2yy = [phiYyy, phiCyy, phiUyy, phiMp2yy]
    nCurv1yy = [-phiYyy, -phiCyy, -phiUyy, -phiMn1yy]
    nCurv2yy = [-phiYyy, -phiCyy, -phiUyy, -phiMn2yy]

    rDispM = [0.1, 0.1]
    rForceM = [0.3, 0.3]
    uForceM = [-0.8, -0.8]
    gammaKM = [0.0, 0.0, 0.0, 0.0, 0.0]
    gammaDM = [0.0, 0.0, 0.0, 0.0, 0.0]
    gammaFM = [0.0, 0.0, 0.0, 0.0, 0.0]
    gammaEM = 0.0
    damM = "energy"

    st_offset = 100000 if ST > 0 else 0

    ohingeMTag1zz = 101000 + st_offset + ET
    ohingeMTag2zz = 102000 + st_offset + ET
    ohingeMTag1yy = 103000 + st_offset + ET
    ohingeMTag2yy = 104000 + st_offset + ET

    _pinching4_from_backbone(ohingeMTag1zz,
                             pMom1zz, nMom1zz, pCurv1zz, nCurv1zz,
                             rDispM, rForceM, uForceM,
                             gammaKM, gammaDM, gammaFM, gammaEM, damM)
    _pinching4_from_backbone(ohingeMTag2zz,
                             pMom2zz, nMom2zz, pCurv2zz, nCurv2zz,
                             rDispM, rForceM, uForceM,
                             gammaKM, gammaDM, gammaFM, gammaEM, damM)
    _pinching4_from_backbone(ohingeMTag1yy,
                             pMom1yy, nMom1yy, pCurv1yy, nCurv1yy,
                             rDispM, rForceM, uForceM,
                             gammaKM, gammaDM, gammaFM, gammaEM, damM)
    _pinching4_from_backbone(ohingeMTag2yy,
                             pMom2yy, nMom2yy, pCurv2yy, nCurv2yy,
                             rDispM, rForceM, uForceM,
                             gammaKM, gammaDM, gammaFM, gammaEM, damM)

    # Apply MinMax limits
    hingeMTag1zz = 105000 + st_offset + ET
    hingeMTag2zz = 106000 + st_offset + ET
    hingeMTag1yy = 107000 + st_offset + ET
    hingeMTag2yy = 108000 + st_offset + ET

    ops.uniaxialMaterial("MinMax", hingeMTag1zz, ohingeMTag1zz,
                         "-min", -phi0zz, "-max", phi0zz)
    ops.uniaxialMaterial("MinMax", hingeMTag2zz, ohingeMTag2zz,
                         "-min", -phi0zz, "-max", phi0zz)
    ops.uniaxialMaterial("MinMax", hingeMTag1yy, ohingeMTag1yy,
                         "-min", -phi0yy, "-max", phi0yy)
    ops.uniaxialMaterial("MinMax", hingeMTag2yy, ohingeMTag2yy,
                         "-min", -phi0yy, "-max", phi0yy)

    # ── Create shear materials (if requested) ──────────────────────────
    if ST > 0:
        pV1yy = [V_cryy, V_ccyy, V_cyy, V_resyy]
        pV1zz = [V_crzz, V_cczz, V_czz, V_reszz]
        nV1yy = [-V_cryy, -V_ccyy, -V_cyy, -V_resyy]
        nV1zz = [-V_crzz, -V_cczz, -V_czz, -V_reszz]

        pShr1yy = [gamm_cryy, gamm_pkyy, gamm_uyy, gamm_myy]
        pShr1zz = [gamm_crzz, gamm_pkzz, gamm_uzz, gamm_mzz]
        nShr1yy = [-gamm_cryy, -gamm_pkyy, -gamm_uyy, -gamm_myy]
        nShr1zz = [-gamm_crzz, -gamm_pkzz, -gamm_uzz, -gamm_mzz]

        rDispV = [0.4, 0.4]
        rForceV = [0.2, 0.2]
        uForceV = [0.0, 0.0]
        gammaKV = [0.0, 0.0, 0.0, 0.0, 0.0]
        gammaDV = [0.0, 0.0, 0.0, 0.0, 0.0]
        gammaFV = [0.0, 0.0, 0.0, 0.0, 0.0]
        gammaEV = 0.0
        damV = "energy"

        ohingeShTagyy = 109000 + st_offset + ET
        ohingeShTagzz = 110000 + st_offset + ET

        _pinching4_from_backbone(ohingeShTagyy,
                                 pV1yy, nV1yy, pShr1yy, nShr1yy,
                                 rDispV, rForceV, uForceV,
                                 gammaKV, gammaDV, gammaFV, gammaEV, damV)
        _pinching4_from_backbone(ohingeShTagzz,
                                 pV1zz, nV1zz, pShr1zz, nShr1zz,
                                 rDispV, rForceV, uForceV,
                                 gammaKV, gammaDV, gammaFV, gammaEV, damV)

        hingeShTagyy = 111000 + st_offset + ET
        hingeShTagzz = 112000 + st_offset + ET

        ops.uniaxialMaterial("MinMax", hingeShTagyy, ohingeShTagyy,
                             "-min", -gamm_myy, "-max", gamm_myy)
        ops.uniaxialMaterial("MinMax", hingeShTagzz, ohingeShTagzz,
                             "-min", -gamm_mzz, "-max", gamm_mzz)

    # ── Create element ──────────────────────────────────────────────────
    intTag = 112000 + st_offset + ET          # internal elastic section tag
    fTag1zz = 113000 + st_offset + ET         # section tag Mz, end 1
    fTag2zz = 114000 + st_offset + ET         # section tag Mz, end 2
    fTag1yy = 115000 + st_offset + ET         # section tag My, end 1
    fTag2yy = 116000 + st_offset + ET         # section tag My, end 2
    phTag1 = 117000 + st_offset + ET          # aggregated section, end 1
    phTag2 = 118000 + st_offset + ET          # aggregated section, end 2

    # Internal elastic section with cracked properties
    ops.section("Elastic", intTag, Ec, Ag, Izze, Iyye, Gc_val, J)

    # Plastic hinge sections
    ops.section("Uniaxial", fTag1zz, hingeMTag1zz, "Mz")
    ops.section("Uniaxial", fTag2zz, hingeMTag2zz, "Mz")

    # Aggregate My to Mz behaviour
    ops.section("Aggregator", phTag1, hingeMTag1yy, "My", "-section", fTag1zz)
    ops.section("Aggregator", phTag2, hingeMTag2yy, "My", "-section", fTag2zz)

    # Integration scheme (Scott & Fenves, 2006)
    intTagBeam = 119000 + st_offset + ET
    ops.beamIntegration("HingeEndpoint", intTagBeam, phTag1, Lp, phTag2, Lp, intTag)

    if ST < 1:
        ops.element("forceBeamColumn", ET, iNode, jNode, GT,
                    intTagBeam, "-iter", 100, 1.0e-12)
    else:
        # Insert shear springs via dummy nodes
        iNodeX = ops.nodeCoord(iNode, 1)
        iNodeY = ops.nodeCoord(iNode, 2)
        iNodeZ = ops.nodeCoord(iNode, 3)
        jNodeX = ops.nodeCoord(jNode, 1)
        jNodeY = ops.nodeCoord(jNode, 2)
        jNodeZ = ops.nodeCoord(jNode, 3)

        ops.node(11000 + iNode, iNodeX, iNodeY, iNodeZ,
                 "-mass", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        ops.node(12000 + jNode, jNodeX, jNodeY, jNodeZ,
                 "-mass", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        rigM = 120000 + st_offset + ET
        ops.uniaxialMaterial("Elastic", rigM, 1.0e10)

        ops.element("zeroLength", 21000 + ET,
                    11000 + iNode, iNode,
                    "-mat", hingeShTagzz, hingeShTagyy, rigM, rigM, rigM, rigM,
                    "-dir", 1, 2, 3, 4, 5, 6,
                    "-doRayleigh", 1)
        ops.element("zeroLength", 22000 + ET,
                    12000 + jNode, jNode,
                    "-mat", hingeShTagzz, hingeShTagyy, rigM, rigM, rigM, rigM,
                    "-dir", 1, 2, 3, 4, 5, 6,
                    "-doRayleigh", 1)

        ops.element("forceBeamColumn", ET, 11000 + iNode, 12000 + jNode,
                    GT, intTagBeam, "-iter", 100, 1.0e-12)
