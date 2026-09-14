# ── 0. FILE HEADER ─────────────────────────────────────────────────────────────
"""
Model    : P103 movable platform — PFC outrigger + SHS100x4, NO ballast, LL 0.525
UniqueID : P103_MovablePlatform
Author   : Muse Spark (OpenCode session)
Date     : 2026-09-14
Purpose  : Stability check of the ballast-scheme sections (PFC 100x50x10
            outriggers, SHS 100x100x4 elsewhere) with NO counterweight and a
            reduced cantilever live load of 0.525 kN/m (was 0.81): report the
            overturning FoS and any wheel uplift on the COMB 301 pattern case.

Section scheme (as model_ballast.py, user direction 2026-09-13):
    outriggers  members 7, 17               -> PFC 100x50x10  (CH100X50X10)
    all others  members 1-6,11-16,21-29     -> SHS 100x100x4  (TUB1001004.0)

Two criteria (as model_ballast.py):
    (1) overturning FoS >= 1.50 on the COMB 301 pattern case (moment method)
    (2) no wheel uplift under the FE solution
Units    : N, mm, MPa  (see standards/units.py)
Notes    : Live load reduced 0.81 -> 0.525 kN/m on members 23, 24, 25 only
            (originally 0.81 kN/m). All other loads as model_ballast.py.
            No counterweight applied.
"""
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1] / "standards"))

import model as base               # noqa: E402  (shared geometry, untouched)
from units import kN_m             # noqa: E402  (distributed-load unit)

# A mm2, I_strong mm4, I_weak mm4, J mm4 (as model_ballast.py)
SEC_SHS = (1520.0, 2.320e6, 2.320e6, 3.539e6)     # TUB1001004.0
SEC_PFC = (1300.0, 2.080e6, 3.230e5, 2.259e4)     # CH100X50X10  (J ~ open sect)

OUTRIGGERS = (7, 17)
GAM = 7.68e-5          # N/mm3
RHO_M = 0.785          # kg per (cm2 . m)
TS, PAT, N_STEPS = 1, 2, 10

# Cantilever live load, COMB 301 (originally 0.81 kN/m)
W_LL = 0.525 * kN_m    # [N/mm]


def sec(mid):
    return SEC_PFC if mid in OUTRIGGERS else SEC_SHS


def member_udl(mid):
    """Factored global downward UDL [N/mm], COMB 301 (1.0 DL + 1.0 LL)."""
    w_dl = sec(mid)[0] * GAM
    if mid in (21, 22, 23, 24):
        w_dl += 0.15
    if mid in (5, 7, 17, 21, 23, 24, 25):
        w_dl += 0.03
    w_ll = W_LL if mid in (23, 24, 25) else 0.0
    return 1.0 * w_dl + 1.0 * w_ll


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


def solve():
    ops.timeSeries("Linear", TS)
    ops.pattern("Plain", PAT, TS)
    for mid, (j1, j2) in base.MEMBERS.items():
        w = member_udl(mid)
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


def fos():
    """Restoring / overturning about the Frame B tipping axis."""
    rest = over = 0.0
    for mid, (j1, j2) in base.MEMBERS.items():
        a, b = np.array(base.JOINTS_M[j1]), np.array(base.JOINTS_M[j2])
        L = float(np.linalg.norm(b - a))
        w = member_udl(mid)
        arm = (a[2] + b[2]) / 2.0 - base.Z_AXIS / base.m
        if arm < 0:
            rest += w * L * abs(arm)
        else:
            over += w * L * arm
    return rest / over


def mass_kg():
    m = 0.0
    for mid, (j1, j2) in base.MEMBERS.items():
        a, b = np.array(base.JOINTS_M[j1]), np.array(base.JOINTS_M[j2])
        L = float(np.linalg.norm(b - a))
        m += (sec(mid)[0] / 100.0) * RHO_M * L
    return m


def evaluate():
    build()
    solve()
    ops.reactions()
    wheels = {n: float(ops.nodeReaction(n, 2)) for n in base.SUPPORT_NODES}
    return dict(fos=fos(), min_wheel=min(wheels.values()),
                uplift=[n for n, v in wheels.items() if v < 0.0],
                wheels=wheels)


if __name__ == "__main__":
    print(f"steel mass = {mass_kg():.1f} kg (no ballast, LL 0.525 kN/m)")
    r = evaluate()
    ok_fos = r["fos"] >= 1.50
    ok_up = not r["uplift"]
    print(f"FoS             : {r['fos']:.3f}  "
          f"({'PASS >= 1.50' if ok_fos else 'FAIL < 1.50'})")
    print(f"min wheel       : {r['min_wheel']:+.1f} N  "
          f"({'no uplift' if ok_up else 'UPLIFT at ' + str(r['uplift'])})")
    print("wheels N: " + " ".join(f"{n}:{v:+.1f}"
                                  for n, v in r["wheels"].items()))
    print(f"verdict: {'PASS' if (ok_fos and ok_up) else 'FAIL'}")
