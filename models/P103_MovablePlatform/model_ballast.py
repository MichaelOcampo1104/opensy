# ── 0. FILE HEADER ─────────────────────────────────────────────────────────────
"""
Model    : P103 movable platform — PFC outrigger + SHS100x4, ballast sizing
UniqueID : P103_MovablePlatform
Author   : Claude Code session
Date     : 2026-09-13
Purpose  : Find the MINIMUM counterweight needed so the platform does not tip.

Section scheme (user direction 2026-09-13):
    outriggers  members 7, 17               -> PFC 100x50x10  (CH100X50X10)
    all others  members 1-6,11-16,21-29     -> SHS 100x100x4  (TUB1001004.0)

Two criteria must BOTH hold:
    (1) overturning FoS >= 1.50 on the COMB 301 pattern case (moment method)
    (2) no wheel uplift under the FE solution (the moment method cannot see
        local uplift, and a design can pass (1) while lifting a wheel)

The counterweight is applied at joints 2 and 5 (the ends of member 6, z = 0), so
it works at the full 0.70 m lever from the Frame B tipping axis and adds nothing
on the overturning side.

Units : N, mm, N.mm ; kN, m for the stability sums
Writes nothing.
"""
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1] / "standards"))

import model as base               # noqa: E402  (shared geometry, untouched)

# A mm2, I_strong mm4, I_weak mm4, J mm4
# SHS from the BS-SHS catalogue; the PFC properties are STAAD's own reported
# values (z-z = strong, y-y = weak) since the catalogue gives geometry only.
SEC_SHS = (1520.0, 2.320e6, 2.320e6, 3.539e6)     # TUB1001004.0
SEC_PFC = (1300.0, 2.080e6, 3.230e5, 2.259e4)     # CH100X50X10  (J ~ open sect)

OUTRIGGERS = (7, 17)
BALLAST_JOINTS = (2, 5)
GAM = 7.68e-5          # N/mm3
RHO_M = 0.785          # kg per (cm2 . m)
TS, PAT, N_STEPS = 1, 2, 10


def sec(mid):
    return SEC_PFC if mid in OUTRIGGERS else SEC_SHS


def member_udl(mid, case):
    """Factored global downward UDL [N/mm]. Only self-weight + imposed loads -
    the counterweight is applied separately as nodal loads."""
    w_dl = sec(mid)[0] * GAM
    if mid in (21, 22, 23, 24):
        w_dl += 0.15
    if mid in (5, 7, 17, 21, 23, 24, 25):
        w_dl += 0.03
    if case == "301":
        w_ll = 0.81 if mid in (23, 24, 25) else 0.0
        return 1.0 * w_dl + 1.0 * w_ll
    w_ll = (0.75 if mid in (21, 22, 23, 24) else 0.85 if mid in (7, 17) else 0.0)
    return 1.4 * w_dl + 1.6 * w_ll


def build():
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)
    for tag, (x, y, z) in base.JOINTS_M.items():
        ops.node(tag, x * base.m, y * base.m, z * base.m)
    ops.geomTransf("Linear", 1, 0.0, 0.0, 1.0)
    ops.geomTransf("Linear", 2, 1.0, 0.0, 0.0)
    for s in base.SUPPORT_NODES:
        ops.fix(s, 1, 1, 1, 0, 0, 0)
    for mid, (j1, j2) in base.MEMBERS.items():
        A, Is, Iw, J = sec(mid)
        ops.element("elasticBeamColumn", mid, j1, j2, A, base.E_STEEL_MOD,
                    base.G_STEEL_MOD, J, Iw, Is, base.ELE_TRANS[mid])


def solve(case, ballast_kg):
    ops.timeSeries("Linear", TS)
    ops.pattern("Plain", PAT, TS)
    for mid, (j1, j2) in base.MEMBERS.items():
        w = member_udl(mid, case)
        wx, wy, wz = base._member_udl_local(mid, w)
        ops.eleLoad("-ele", mid, "-type", "-beamUniform", wy, wz, wx)
    if ballast_kg > 0.0:
        per = ballast_kg * 9.81 / len(BALLAST_JOINTS)      # N, unfactored ->
        # COMB 301 has f_dl = 1.0 so no further scaling is needed there
        for j in BALLAST_JOINTS:
            ops.load(j, 0.0, -per, 0.0, 0.0, 0.0, 0.0)
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / N_STEPS)
    ops.test("EnergyIncr", 1.0e-8, 100)
    ops.algorithm("Linear")
    ops.analysis("Static")
    for _ in range(N_STEPS):
        if ops.analyze(1) != 0:
            raise RuntimeError("solve failed")


def fos(ballast_kg, case="301"):
    """Restoring / overturning about the Frame B tipping axis (f_dl = 1 here)."""
    rest = over = 0.0
    for mid, (j1, j2) in base.MEMBERS.items():
        a, b = np.array(base.JOINTS_M[j1]), np.array(base.JOINTS_M[j2])
        L = float(np.linalg.norm(b - a))
        w = member_udl(mid, case)
        arm = (a[2] + b[2]) / 2.0 - base.Z_AXIS / base.m
        if arm < 0:
            rest += w * L * abs(arm)
        else:
            over += w * L * arm
    if ballast_kg > 0.0:
        w_b = ballast_kg * 9.81e-3                          # kN
        for j in BALLAST_JOINTS:
            arm = base.JOINTS_M[j][2] - base.Z_AXIS / base.m
            rest += w_b / len(BALLAST_JOINTS) * abs(arm)
    return rest / over


def mass_kg():
    m = 0.0
    for mid, (j1, j2) in base.MEMBERS.items():
        a, b = np.array(base.JOINTS_M[j1]), np.array(base.JOINTS_M[j2])
        L = float(np.linalg.norm(b - a))
        m += (sec(mid)[0] / 100.0) * RHO_M * L
    return m


def evaluate(ballast_kg):
    build()
    solve("301", ballast_kg)
    ops.reactions()
    wheels = {n: float(ops.nodeReaction(n, 2)) for n in base.SUPPORT_NODES}
    return dict(ballast=ballast_kg, fos=fos(ballast_kg),
                min_wheel=min(wheels.values()),
                uplift=[n for n, v in wheels.items() if v < 0.0],
                wheels=wheels)


if __name__ == "__main__":
    steel = mass_kg()
    print(f"steel mass (no ballast) = {steel:.1f} kg")
    print(f"\n{'ballast kg':>11}{'FoS':>8}{'min wheel N':>13}  uplift        criteria")
    first_both = None
    for b in [70, 72, 73, 74, 75, 76, 78, 80]:
        r = evaluate(b)
        ok_fos = r["fos"] >= 1.50
        ok_up = not r["uplift"]
        both = ok_fos and ok_up
        if both and first_both is None:
            first_both = r
        flag = ("FoS+uplift OK" if both
                else "FoS ok, UPLIFT" if ok_fos else
                "no uplift, FoS low" if ok_up else "neither")
        print(f"{b:>11.1f}{r['fos']:>8.3f}{r['min_wheel']:>13.1f}  "
              f"{'none' if not r['uplift'] else str(r['uplift']):<13}  {flag}")
    if first_both:
        b = first_both["ballast"]
        print(f"\nMINIMUM BALLAST MEETING BOTH: {b:.1f} kg  "
              f"(FoS {first_both['fos']:.3f}, min wheel {first_both['min_wheel']:+.1f} N)")
        print(f"  + steel {steel:.1f} kg  =  total {steel + b:.1f} kg")
