"""
Joint model for non-ductile RC beam-column joints (O'Reilly, 2019).

Port of the Tcl jointModel procedure from:
    https://github.com/gerardjoreilly/Numerical-Modelling-of-GLD-RC-Frames

Creates a zero-length rotational spring element that captures shear
deformation and strength degradation of exterior/interior/roof joints
with smooth bars and end-hooks, typical of Italian pre-1970s construction.

Ref:
    O'Reilly, G. J., Sullivan, T. J. (2019) "Modeling Techniques for the
    Seismic Assessment of the Existing Italian RC Frame Structures,"
    Journal of Earthquake Engineering, 23(8), pp. 1262-1296.

Units: N, mm, MPa  (= N/mm^2)
"""

import math
import openseespy.opensees as ops
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *


def create_joint(
    jtype: str,
    index: int,
    xyz: tuple,
    mass: float,
    col: tuple,
    bm: tuple,
    conc: tuple,
    bars: tuple,
    P: float,
    H: float,
    ptc: list,
    gamm: list,
    hyst: list,
    pfile,
    pflag: int = 0,
) -> None:
    """Create a beam-column joint with rotational hinge (zero-length element).

    The joint is represented by a pair of coincident nodes connected by a
    zeroLength element with a Hysteretic material for moment-rotation
    response in both local bending directions.

    Args:
        jtype: Joint type ("Exterior", "Interior", "Roof", "Elastic").
        index: Index tag used to construct all internal tags
               (nodes 1{index}, 6{index}; element 9{index}; materials 1-6{index}).
        xyz: (X, Y, Z) coordinates of joint centre in mm.
        mass: Nodal mass (tonnes) — stored as mass in N*s^2/mm.
        col: (hcX, hcY) column section dimensions in mm.
        bm: (hbX, hbY, bbX, bbY) beam dimensions in mm.
        conc: (fc, Ec, cv) concrete compressive strength (MPa),
              elastic modulus (MPa), cover (mm).
        bars: (dbL, dbV) longitudinal and transverse bar diameters (mm).
        P: Axial force in N (compression positive).
        H: Interstorey height in mm.
        ptc: 6 kappa coefficients [pos_crack, pos_peak, pos_ult,
             neg_crack, neg_peak, neg_ult].
        gamm: 6 shear deformation parameters [pos_crack, pos_peak, pos_ult,
              neg_crack, neg_peak, neg_ult] in radians.
        hyst: 5 hysteretic parameters [pinchX, pinchY, damage1, damage2, beta].
        pfile: Open file handle for property output.
        pflag: Print flag (0 = silent, 1 = verbose).
    """
    X, Y, Z = xyz
    hcX, hcY = col
    hbX, hbY, bbX, bbY = bm
    fc, Ec, cv = conc
    dbL, dbV = bars

    # Column cross-section area  [mm^2]
    Ac = hcX * hcY

    # Beam height — pick the larger of the two orientations
    hb = hbY if hbX < hbY else hbX

    # ── Compute effective joint width bjX, bjY ──────────────────────────
    # X direction
    if hcY >= bbX:
        bjX = float(hcY)
    elif bbX + 0.5 * hcX < hcY:
        bjX = bbX + 0.5 * hcX
    if hcY < bbX:
        bjX = float(bbX)
    elif hcY + 0.5 * hcX < bbX:
        bjX = hcY + 0.5 * hcX

    # Y direction
    if hcX >= bbY:
        bjY = float(hcX)
    elif bbY + 0.5 * hcY < hcX:
        bjY = bbY + 0.5 * hcY
    if hcX < bbY:
        bjY = float(bbY)
    elif hcX + 0.5 * hcY < bbY:
        bjY = hcX + 0.5 * hcY

    # ── Axial spring stiffness ──────────────────────────────────────────
    Kspr = 2.0 * Ec * Ac / hb          # N/mm

    # ── Create nodes ────────────────────────────────────────────────────
    ops.node(1 * 1000 + index, X, Y, Z,
             "-mass", mass, mass, 0.0, 0.0, 0.0, 0.0)
    ops.node(6 * 1000 + index, X, Y, Z,
             "-mass", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    # ── Create materials ────────────────────────────────────────────────
    # Rigid (axial constraint)
    ops.uniaxialMaterial("Elastic", 1 * 1000 + index, 1.0e15)
    # Axial spring
    ops.uniaxialMaterial("Elastic", 2 * 1000 + index, Kspr)

    # ── Compute flexural backbone ───────────────────────────────────────
    # Internal lever arms  [mm]
    jX = 0.9 * (hbX - cv - dbV - dbL / 2.0)
    jY = 0.9 * (hbY - cv - dbV - dbL / 2.0)

    # Convert P from N to kN to match original calibration
    P_kN = P / 1000.0

    MjX = []
    MjY = []
    for ii in range(6):
        pt = ptc[ii] * math.sqrt(fc)       # principal tensile stress factor [MPa]
        if jtype == "Interior":
            term = (H * jX / (H - jX))
            Mx = pt * bjX * hcX * term * math.sqrt(
                1.0 + P_kN / (bjX * hcX * pt)
            )
            term = (H * jY / (H - jY))
            My = pt * bjY * hcY * term * math.sqrt(
                1.0 + P_kN / (bjY * hcY * pt)
            )
        elif jtype == "Exterior":
            term = (H * jX / (H - jX))
            ratio = hbX / (2.0 * hcX)
            Mx = pt * bjX * hcX * term * (
                ratio + math.sqrt(ratio**2 + 1.0 + P_kN / (bjX * hcX * pt))
            )
            term = (H * jY / (H - jY))
            ratio = hbY / (2.0 * hcY)
            My = pt * bjY * hcY * term * (
                ratio + math.sqrt(ratio**2 + 1.0 + P_kN / (bjY * hcY * pt))
            )
        elif jtype == "Roof":
            term = jX
            ratio = hbX / (2.0 * hcX)
            Mx = 2.0 * pt * bjX * hcX * term * (
                ratio + math.sqrt(ratio**2 + 1.0 + P_kN / (bjX * hcX * pt))
            )
            term = jY
            ratio = hbY / (2.0 * hcY)
            My = 2.0 * pt * bjY * hcY * term * (
                ratio + math.sqrt(ratio**2 + 1.0 + P_kN / (bjY * hcY * pt))
            )
        else:  # "Elastic"
            term = (H * jX / (H - jX))
            Mx = pt * bjX * hcX * term * math.sqrt(
                1.0 + P_kN / (bjX * hcX * pt)
            )
            term = (H * jY / (H - jY))
            My = pt * bjY * hcY * term * math.sqrt(
                1.0 + P_kN / (bjY * hcY * pt)
            )
        MjX.append(Mx)
        MjY.append(My)

    # ── Create rotational spring materials ──────────────────────────────
    gamm_max = 0.100   # rad — upper limit on joint rotation

    if jtype != "Elastic":
        # Positive and negative backbone from computed moments
        pos_rot = [gamm[0], gamm[1], gamm[2]]
        neg_rot = [gamm[3], gamm[4], gamm[5]]

        # X-direction rotation
        ops.uniaxialMaterial(
            "Hysteretic",
            3 * 1000 + index,
            1.0 * MjX[0], pos_rot[0],
            1.0 * MjX[1], pos_rot[1],
            1.0 * MjX[2], pos_rot[2],
            -1.0 * MjX[3], -neg_rot[0],
            -1.0 * MjX[4], -neg_rot[1],
            -1.0 * MjX[5], -neg_rot[2],
            hyst[0], hyst[1], hyst[2], hyst[3], hyst[4],
        )
        # Y-direction rotation
        ops.uniaxialMaterial(
            "Hysteretic",
            4 * 1000 + index,
            1.0 * MjY[0], pos_rot[0],
            1.0 * MjY[1], pos_rot[1],
            1.0 * MjY[2], pos_rot[2],
            -1.0 * MjY[3], -neg_rot[0],
            -1.0 * MjY[4], -neg_rot[1],
            -1.0 * MjY[5], -neg_rot[2],
            hyst[0], hyst[1], hyst[2], hyst[3], hyst[4],
        )
    else:
        # Elastic joint — linear elastic rotational spring
        ops.uniaxialMaterial("Elastic", 3 * 1000 + index,
                             MjX[0] / gamm[0])
        ops.uniaxialMaterial("Elastic", 4 * 1000 + index,
                             MjY[0] / gamm[0])

    # ── Apply MinMax rotation limits ────────────────────────────────────
    ops.uniaxialMaterial(
        "MinMax", 5 * 1000 + index, 3 * 1000 + index,
        "-min", -gamm_max, "-max", gamm_max,
    )
    ops.uniaxialMaterial(
        "MinMax", 6 * 1000 + index, 4 * 1000 + index,
        "-min", -gamm_max, "-max", gamm_max,
    )

    # ── Create zero-length element ──────────────────────────────────────
    ops.element(
        "zeroLength",
        9 * 1000 + index,
        1 * 1000 + index,
        6 * 1000 + index,
        "-mat",
        1 * 1000 + index,   # rigid (dir 1)
        1 * 1000 + index,   # rigid (dir 2)
        2 * 1000 + index,   # axial (dir 3)
        6 * 1000 + index,   # rotational-Y (dir 4) — MinMax wrapped
        5 * 1000 + index,   # rotational-X (dir 5) — MinMax wrapped
        1 * 1000 + index,   # rigid (dir 6)
        "-dir", 1, 2, 3, 4, 5, 6,
        "-doRayleigh", 1,
    )

    # ── Output ──────────────────────────────────────────────────────────
    if pflag:
        print(f"Created connection at grid (XYZ): {index}")
        print(f"  Coords: {X:.1f} {Y:.1f} {Z:.1f} mm")
        print(f"  Element: {9 * 1000 + index}")
        print(f"  Mass: {mass:.1f} tonne")
        print(f"  P: {P_kN:.1f} kN")
        print(f"  Concrete: fc={fc:.1f} MPa  Ec={Ec:.1f} MPa")
        print(f"  Joint: bjX={bjX:.1f} mm  bjY={bjY:.1f} mm")
        print(f"  Kspr: {Kspr:.1f} N/mm")

    pfile.write(
        f"Element {9 * 1000 + index} "
        f"MjX:{MjX[0]:.2f} {MjX[1]:.2f} {MjX[2]:.2f} "
        f"{MjX[3]:.2f} {MjX[4]:.2f} {MjX[5]:.2f} "
        f"MjY:{MjY[0]:.2f} {MjY[1]:.2f} {MjY[2]:.2f} "
        f"{MjY[3]:.2f} {MjY[4]:.2f} {MjY[5]:.2f} "
        f"gamma:{gamm[0]:.4f} {gamm[1]:.4f} {gamm[2]:.4f}\n"
    )
