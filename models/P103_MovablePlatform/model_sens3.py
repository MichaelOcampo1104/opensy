# ── 0. FILE HEADER ─────────────────────────────────────────────────────────────
"""
Model    : P103 movable platform — 3-group section scheme, FoS + wheel uplift
UniqueID : P103_MovablePlatform
Author   : Claude Code session
Date     : 2026-09-13
Purpose  : Sweep a THREE-GROUP section scheme (columns / outriggers / rest) with
           NO counterweight and report, for each combination:
             - overturning FoS about the Frame B tipping axis (moment method)
             - the MINIMUM wheel reaction from the FE (uplift check)
             - total steel mass
           The moment method cannot see local wheel uplift, so both criteria are
           needed: a design with FoS > 1.50 can still lift a wheel.

Section scheme (user direction 2026-09-13):
    columns     members 1,2,3,4,11,12,13,14   -> SHS
    outriggers  members 7, 17                 -> CHANNEL
    rest        all others (13 members)       -> RHS

WAIT
  Run this with the repo's `model.py` on sys.path for the shared geometry. It is
  standalone and writes nothing.
Units : N, mm, N.mm ; kN, m for the stability sums
"""
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1] / "standards"))

import model as base               # noqa: E402  (shared geometry, untouched)

# ── 2. SECTION REGISTRY (BS EN 10219 / BS4) ────────────────────────────────────
# (A mm2, I_strong mm4, I_weak mm4). For the CHANNEL these come from STAAD's own
# reported properties (z-z = strong, y-y = weak); the SHS/RHS come from the
# BS-SHS / BS-RHS catalogue tables.
SHS = {   # A mm2, I_strong mm4, I_weak mm4, J mm4
    "SHS80X4":   (1200.0, 1.140e6, 1.140e6, 1.7563e6),
    "SHS100X5":  (1870.0, 2.790e6, 2.790e6, 4.287e6),
    "SHS100X6.3": (2320.0, 3.360e6, 3.360e6, 5.183e6),
    "SHS100X8":  (2880.0, 4.000e6, 4.000e6, 6.228e6),
    "SHS100X10": (3490.0, 4.620e6, 4.620e6, 7.290e6),
    "SHS120X6.3": (2820.0, 6.030e6, 6.030e6, 9.261e6),
    "SHS120X8":  (3520.0, 7.260e6, 7.260e6, 1.1239e7),
    "SHS140X8":  (4160.0, 1.034e7, 1.034e7, 1.8397e7),
}
CH = {   # A, Iz(strong), Iy(weak) from STAAD; J = open thin-walled (H*S^3+2*(B-S)*T^3)/3
    "CH150X75X18": (2280.0, 0.861e7, 0.131e7, 5.47e4),
    "CH180X90X26": (3320.0, 1.817e7, 0.277e7, 1.252e5),
    "CH200X90X30": (3790.0, 2.523e7, 0.314e7, 1.747e5),
    "CH230X90X32": (4100.0, 3.518e7, 0.334e7, 1.833e5),
    "CH260X90X35": (4440.0, 4.728e7, 0.353e7, 1.944e5),
    "CH300X90X41": (5270.0, 7.218e7, 0.404e7, 2.740e5),
}
RHS = {
    "RHS100X50X5":   (1370.0, 1.670e6, 5.430e5, 1.3054e6),
    "RHS100X50X6.3": (1690.0, 1.970e6, 6.300e5, 1.5375e6),
    "RHS100X50X8":   (2080.0, 2.300e6, 7.170e5, 1.7828e6),
    "RHS120X60X6.3": (2070.0, 3.580e6, 1.160e6, 2.806e6),
    "RHS120X60X8":   (2560.0, 4.250e6, 1.350e6, 3.309e6),
}

COLUMNS = (1, 2, 3, 4, 11, 12, 13, 14)
OUTRIGGERS = (7, 17)

GAM = 7.68e-5          # N/mm3
RHO_M = 0.785          # kg per (cm2 . m)
TS, PAT, N_STEPS = 1, 2, 10


def J_tube(h, b, t):
    """Thin-walled closed tube torsion constant (SHS/RHS)."""
    a1, a2 = h - t, b - t
    return 2 * t * a1 * a1 * a2 * a2 / (a1 + a2)


def J_open(H, B, S, T, wall_h, wall_b):
    """Open thin-walled torsion approximation for a channel, from STAAD geometry."""
    return (H * S ** 3 + 2 * (B - wall_b) * T ** 3) / 3


def sections_for(shs, ch, rhs):
    """Member -> (A, IZ_strong, IY_weak, J) in mm units, from the registries."""
    out = {}
    for mid in base.MEMBERS:
        if mid in COLUMNS:
            out[mid] = SHS[shs]
        elif mid in OUTRIGGERS:
            out[mid] = CH[ch]
        else:
            out[mid] = RHS[rhs]
    return out


def member_udl(mid, case, sec):
    """Factored global downward UDL [N/mm]. case 301 = stability pattern."""
    A = sec[mid][0]
    w_dl = A * GAM
    if mid in (21, 22, 23, 24):
        w_dl += 0.15
    if mid in (5, 7, 17, 21, 23, 24, 25):
        w_dl += 0.03
    if case == "301":
        w_ll = 0.81 if mid in (23, 24, 25) else 0.0
        return 1.0 * w_dl + 1.0 * w_ll
    w_ll = (0.75 if mid in (21, 22, 23, 24)
            else 0.85 if mid in (7, 17) else 0.0)
    return 1.4 * w_dl + 1.6 * w_ll


def build(sec):
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)
    for tag, (x, y, z) in base.JOINTS_M.items():
        ops.node(tag, x * base.m, y * base.m, z * base.m)
    ops.geomTransf("Linear", 1, 0.0, 0.0, 1.0)
    ops.geomTransf("Linear", 2, 1.0, 0.0, 0.0)
    for s in base.SUPPORT_NODES:
        ops.fix(s, 1, 1, 1, 0, 0, 0)
    for mid, (j1, j2) in base.MEMBERS.items():
        A, Is, Iw, J = sec[mid]
        # model IZ = STRONG axis (resists local x-y plane bending = the vertical
        # load path for the outrigger), IY = weak
        ops.element("elasticBeamColumn", mid, j1, j2, A, base.E_STEEL_MOD,
                    base.G_STEEL_MOD, J, Iw, Is, base.ELE_TRANS[mid])


def run_case(case, sec):
    ops.timeSeries("Linear", TS)
    ops.pattern("Plain", PAT, TS)
    for mid, (j1, j2) in base.MEMBERS.items():
        w = member_udl(mid, case, sec)
        wx, wy, wz = base._member_udl_local(mid, w)
        ops.eleLoad("-ele", mid, "-type", "-beamUniform", wy, wz, wx)
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


def fos(sec, case="301"):
    rest = over = 0.0
    for mid, (j1, j2) in base.MEMBERS.items():
        a, b = np.array(base.JOINTS_M[j1]), np.array(base.JOINTS_M[j2])
        L = float(np.linalg.norm(b - a))
        w = member_udl(mid, case, sec)
        arm = (a[2] + b[2]) / 2.0 - base.Z_AXIS / base.m
        if arm < 0:
            rest += w * L * abs(arm)
        else:
            over += w * L * arm
    return rest / over


def mass_kg(sec):
    m = 0.0
    for mid, (j1, j2) in base.MEMBERS.items():
        a, b = np.array(base.JOINTS_M[j1]), np.array(base.JOINTS_M[j2])
        L = float(np.linalg.norm(b - a))
        m += (sec[mid][0] / 100.0) * RHO_M * L
    return m


def evaluate(shs, ch, rhs):
    sec = sections_for(shs, ch, rhs)
    build(sec)
    run_case("301", sec)
    ops.reactions()
    wheels = {n: float(ops.nodeReaction(n, 2)) for n in base.SUPPORT_NODES}
    return dict(shs=shs, ch=ch, rhs=rhs, fos=fos(sec), mass=mass_kg(sec),
                min_wheel_N=min(wheels.values()),
                uplift=[n for n, v in wheels.items() if v < 0.0])


if __name__ == "__main__":
    ok = []
    for a in SHS:
        for b in CH:
            for c in RHS:
                r = evaluate(a, b, c)
                if not r["uplift"]:
                    ok.append(r)
    ok.sort(key=lambda r: r["mass"])
    print("BOTH criteria met  (FoS >= 1.50  AND  no wheel uplift, COMB 301):")
    print(f"{'SHS cols':<12}{'CH outrig':<14}{'RHS rest':<15}{'mass kg':>9}"
          f"{'FoS':>7}{'min wheel N':>13}")
    both = [r for r in ok if r["fos"] >= 1.50]
    for r in both[:8]:
        print(f"{r['shs']:<12}{r['ch']:<14}{r['rhs']:<15}{r['mass']:>9.1f}"
              f"{r['fos']:>7.3f}{r['min_wheel_N']:>13.1f}")
    print(f"\nno-uplift only          : {len(ok)} of {len(SHS)*len(CH)*len(RHS)}")
    print(f"FoS>=1.50 AND no-uplift : {len(both)}")
    if both:
        b = both[0]
        print(f"\nLIGHTEST MEETING BOTH: {b['shs']} / {b['ch']} / {b['rhs']}  "
              f"-> {b['mass']:.1f} kg, FoS {b['fos']:.3f}, "
              f"min wheel {b['min_wheel_N']:+.1f} N")
    if ok:
        b = ok[0]
        print(f"lightest no-uplift (fails FoS): {b['shs']} / {b['ch']} / "
              f"{b['rhs']}  {b['mass']:.1f} kg, FoS {b['fos']:.3f}")
