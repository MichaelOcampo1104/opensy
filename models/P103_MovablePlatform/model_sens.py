# ── 0. FILE HEADER ─────────────────────────────────────────────────────────────
"""
Model    : P103 movable platform — section sensitivity / stability-constrained design
UniqueID : P103_MovablePlatform
Author   : Claude Code session
Date     : 2026-09-13
Purpose  : Sweep standard British (BS EN 10219) SHS/RHS member sets and a rear
           counterweight, and report for each combination the overturning factor
           of safety, support reactions and peak deflection — the data needed to
           choose the LIGHTEST set that still satisfies FoS >= 1.50.

WHY THIS EXISTS
  The as-modelled members are custom PRIS sections (SHS 100x100x12.0 and
  RHS 100x50x18.7) which STAAD refuses to design ("DESIGN NOT PERFORMED WITH
  PRISMATIC PROPERTIES"). Both are heavier than the heaviest standard section in
  that size. Replacing them with standard sections moves the governing check from
  STRENGTH (max utilisation 4.1%) to STABILITY: the platform stays upright partly
  because its own members are heavy on the restoring side, so shrinking members
  LOWERS the overturning FoS. A strength-only optimisation (STAAD SELECT) drives
  every member to a 20x20x2 tube and the platform tips.

Ref      : STAAD 3D_Movable_bcad-model.std and 3D_Movable_sens.std.
           Section properties taken from the STAAD British catalogue
           (BS-SHS / BS-RHS tables) — Ix there is the STRONG axis and maps to the
           model's IZ; Iy maps to IY. Verified against the modelled RHS 100x50x18.7
           (Ix = 3.909e6, Iy = 1.031e6 mm4, both reproduced exactly).
Units    : N, mm, N.mm ; kN, m for the stability sums (declared per function)

Geometry is imported from model.py (the verified COMB 301 harness), which is left
untouched. Only the member sections and the added counterweight differ.
"""

# ── 1. IMPORTS ─────────────────────────────────────────────────────────────────
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import openseespy.opensees as ops

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1] / "standards"))

import model as base               # noqa: E402  (shared geometry)

# ── 2. SECTION REGISTRY ────────────────────────────────────────────────────────
# BS EN 10219 hot-finished hollow sections, from the STAAD British catalogue.
# IZ = strong axis (DB "Ix"), IY = weak axis (DB "Iy"), J = thin-walled closed
# tube torsion  J = 2t(h-t)^2(b-t)^2 / ((h-t)+(b-t)).  Units mm / mm2 / mm4.
SECTIONS = {
    # SHS 100x100 -- catalogue stops at 10.0 mm (the model uses a non-standard 12.0)
    "SHS100X10":   dict(A=3490.0, IZ=4.620e6, IY=4.620e6, J=7.290e6, mass=27.4),
    "SHS100X8":    dict(A=2880.0, IZ=4.000e6, IY=4.000e6, J=6.230e6, mass=22.6),
    "SHS100X6.3":  dict(A=2320.0, IZ=3.360e6, IY=3.360e6, J=5.183e6, mass=18.2),
    "SHS100X5":    dict(A=1870.0, IZ=2.790e6, IY=2.790e6, J=4.140e6, mass=14.7),
    "SHS80X5":     dict(A=1470.0, IZ=1.370e6, IY=1.370e6, J=2.109e6, mass=11.6),
    "SHS80X4":     dict(A=1200.0, IZ=1.140e6, IY=1.140e6, J=1.756e6, mass=9.41),
    # RHS 100x50 -- catalogue stops at 8.0 mm (the model uses a non-standard 18.7)
    "RHS100X50X8":   dict(A=2080.0, IZ=2.300e6, IY=7.170e5, J=1.783e6, mass=16.3),
    "RHS100X50X6.3": dict(A=1690.0, IZ=1.970e6, IY=6.300e5, J=1.538e6, mass=13.3),
    "RHS100X50X5":   dict(A=1370.0, IZ=1.670e6, IY=5.430e5, J=1.305e6, mass=10.8),
    "RHS100X50X4":   dict(A=1120.0, IZ=1.400e6, IY=4.620e5, J=1.099e6, mass=8.78),
}

# The as-modelled custom sections, for reference/baseline runs
SECTIONS["SHS100X100X12_asmodelled"] = dict(A=4224.0, IZ=5.553e6, IY=5.553e6,
                                            J=8.177e6, mass=33.2)
SECTIONS["RHS100X50X18.7_asmodelled"] = dict(A=4211.0, IZ=3.909e6, IY=1.031e6,
                                             J=2.151e6, mass=33.1)

RHS_MEMBERS = (7, 17)                     # the two outriggers

# Candidate design sets to sweep.  None = keep the as-modelled custom section.
SENS_SETS = {
    "baseline":   dict(shs="SHS100X100X12_asmodelled", rhs="RHS100X50X18.7_asmodelled",
                       ballast_kg=0.0),
    "std_max":    dict(shs="SHS100X10", rhs="RHS100X50X8", ballast_kg=16.7),
    "mid":        dict(shs="SHS100X6.3", rhs="RHS100X50X6.3", ballast_kg=49.4),
    "light":      dict(shs="SHS80X4", rhs="RHS100X50X4", ballast_kg=84.1),
}

# ── 3. PARAMETERS ──────────────────────────────────────────────────────────────
TS_GRAVITY = 1
PAT_CASE = 2
N_STEPS = 10
G = 9.81e-3                               # kN per kg

# Load cases, transcribed from the STAAD .std (kN/m == N/mm)
CASES = {
    "301": dict(f_dl=1.0, f_ll=1.0, ll_source="cantilever"),   # stability, service
    "202": dict(f_dl=1.4, f_ll=1.6, ll_source="full"),         # ULS strength
}
DL_GRATING = (21, 22, 23, 24)
DL_ANGLE = (5, 7, 17, 21, 23, 24, 25)
W_GRATING = 0.15
W_ANGLE = 0.03
LL_FULL = dict(platform=(21, 22, 23, 24), w_platform=0.75,
               outrigger=(7, 17), w_outrigger=0.85)
LL_CANT = dict(members=(23, 24, 25), w=0.81)

TIP_NODE = 24                             # cantilever tip - deflection monitor


# ── 4. BUILD ───────────────────────────────────────────────────────────────────
def build(model_set: dict) -> None:
    """Create nodes/supports/elements with the sections named in `model_set`."""
    shs = SECTIONS[model_set["shs"]]
    rhs = SECTIONS[model_set["rhs"]]
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)
    for tag, (x, y, z) in base.JOINTS_M.items():
        ops.node(tag, x * base.m, y * base.m, z * base.m)
    ops.geomTransf("Linear", 1, 0.0, 0.0, 1.0)
    ops.geomTransf("Linear", 2, 1.0, 0.0, 0.0)
    for s in base.SUPPORT_NODES:
        ops.fix(s, 1, 1, 1, 0, 0, 0)
    for mid, (j1, j2) in base.MEMBERS.items():
        sec = rhs if mid in RHS_MEMBERS else shs
        ops.element("elasticBeamColumn", mid, j1, j2, sec["A"], base.E_STEEL_MOD,
                    base.G_STEEL_MOD, sec["J"], sec["IY"], sec["IZ"],
                    base.ELE_TRANS[mid])


def member_udl(mid: int, case: str, model_set: dict) -> float:
    """Factored global downward UDL on one member [N/mm]."""
    spec = CASES[case]
    sec = SECTIONS[model_set["rhs"]] if mid in RHS_MEMBERS else SECTIONS[model_set["shs"]]
    w_dl = sec["A"] * base.GAMMA_STEEL
    if mid in DL_GRATING:
        w_dl += W_GRATING
    if mid in DL_ANGLE:
        w_dl += W_ANGLE
    if spec["ll_source"] == "full":
        w_ll = (LL_FULL["w_platform"] if mid in LL_FULL["platform"]
                else LL_FULL["w_outrigger"] if mid in LL_FULL["outrigger"] else 0.0)
    else:
        w_ll = LL_CANT["w"] if mid in LL_CANT["members"] else 0.0
    return spec["f_dl"] * w_dl + spec["f_ll"] * w_ll


def apply_loads(case: str, model_set: dict) -> float:
    """Apply the member UDLs plus the rear counterweight. Returns total [N]."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_CASE, TS_GRAVITY)
    total = 0.0
    for mid, (j1, j2) in base.MEMBERS.items():
        w = member_udl(mid, case, model_set)
        wx, wy, wz = base._member_udl_local(mid, w)
        ops.eleLoad("-ele", mid, "-type", "-beamUniform", wy, wz, wx)
        a = np.array(base.JOINTS_M[j1]) * base.m
        b = np.array(base.JOINTS_M[j2]) * base.m
        total += w * float(np.linalg.norm(b - a))
    # counterweight: split equally between the two ends of member 6 (both at
    # z = 0, so the restoring arm about the tipping axis is identical)
    kg = model_set.get("ballast_kg", 0.0)
    if kg:
        p = kg * G / 2.0                       # kN, then to N
        ops.load(2, 0.0, -p * 1000.0, 0.0, 0.0, 0.0, 0.0)
        ops.load(5, 0.0, -p * 1000.0, 0.0, 0.0, 0.0, 0.0)
        total += kg * G * 1000.0
    return total


def run() -> None:
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / N_STEPS)
    ops.test("EnergyIncr", 1.0e-8, 100)
    ops.algorithm("Linear")
    ops.analysis("Static")
    for _ in range(N_STEPS):
        if ops.analyze(1) != 0:
            raise RuntimeError("gravity step failed")


# ── 5. RESULTS ─────────────────────────────────────────────────────────────────
def overturning_fos(model_set: dict, case: str = "301") -> dict:
    """Restoring/overturning moment about Frame B (Z = 0.70 m) [kN.m].

    Load-based sum (the method validated against the endorsed check: reproduces
    FoS 1.723 for the as-modelled sections). Self-weight follows the section in
    use, so a lighter set directly lowers the restoring term.
    """
    spec = CASES[case]
    rest = over = 0.0
    for mid, (j1, j2) in base.MEMBERS.items():
        a = np.array(base.JOINTS_M[j1])           # m
        b = np.array(base.JOINTS_M[j2])
        L = float(np.linalg.norm(b - a))
        # member_udl returns N/mm, which is numerically identical to kN/m, so
        # w * L is already in kN (L is in m). Do NOT rescale -- doing so would
        # leave the ballast term (added in kNm below) on a different scale.
        w = member_udl(mid, case, model_set)
        arm = ((a[2] + b[2]) / 2.0) - base.Z_AXIS / base.m
        if arm < 0:
            rest += w * L * abs(arm)
        else:
            over += w * L * arm
    kg = model_set.get("ballast_kg", 0.0)
    if kg:
        rest += kg * G * abs(0.0 - base.Z_AXIS / base.m)
    return dict(restoring_kNm=rest, overturning_kNm=over,
                fos=(rest / over if over else float("inf")))


def system_mass_kg(model_set: dict) -> float:
    """Total steel mass (from catalogue mass/m x length) plus the counterweight."""
    m = 0.0
    for mid, (j1, j2) in base.MEMBERS.items():
        a = np.array(base.JOINTS_M[j1])
        b = np.array(base.JOINTS_M[j2])
        L = float(np.linalg.norm(b - a))
        sec = SECTIONS[model_set["rhs"]] if mid in RHS_MEMBERS else SECTIONS[model_set["shs"]]
        m += sec["mass"] * L
    return m + model_set.get("ballast_kg", 0.0)


def extract(model_set: dict, case: str) -> dict:
    """Reactions, deflection and member actions for one case."""
    ops.reactions()
    joints = {n: float(ops.nodeReaction(n, 2)) for n in base.SUPPORT_NODES}
    line_a = sum(joints[n] for n in base.LINE_A_NODES)
    line_b = sum(joints[n] for n in base.LINE_B_NODES)
    disp = {n: [float(v) for v in ops.nodeDisp(n)] for n in base.JOINTS_M}
    max_uz = max(abs(d[2]) for d in disp.values())
    tip = disp[TIP_NODE]
    return dict(
        case=case,
        line_A_N=line_a, line_B_N=line_b, total_N=line_a + line_b,
        uplift=[n for n in base.SUPPORT_NODES if joints[n] < 0.0],
        max_abs_uz_mm=max_uz,
        tip_uy_mm=tip[1], tip_uz_mm=tip[2],
    )


def run_set(name: str, model_set: dict) -> dict:
    """Build, solve and report one candidate set for both load cases."""
    out = {"set": name, "shs": model_set["shs"], "rhs": model_set["rhs"],
           "ballast_kg": model_set.get("ballast_kg", 0.0),
           "mass_kg": system_mass_kg(model_set)}
    out.update(overturning_fos(model_set, "301"))
    for case in ("301", "202"):
        build(model_set)
        applied = apply_loads(case, model_set)
        run()
        r = extract(model_set, case)
        r["applied_N"] = applied
        r["fy_residual_N"] = applied - r["total_N"]
        out[f"case{case}"] = r
    return out


# ── 6. MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    which = sys.argv[1:] or list(SENS_SETS)
    print(f"{'set':<10}{'SHS':<22}{'RHS':<18}{'ballast':>8}{'mass kg':>9}"
          f"{'FoS':>7}{'lineA N':>9}{'lineB N':>9}{'uplift':>8}{'maxUz mm':>10}")
    for name in which:
        r = run_set(name, SENS_SETS[name])
        c = r["case301"]
        print(f"{name:<10}{r['shs']:<22}{r['rhs']:<18}{r['ballast_kg']:>8.1f}"
              f"{r['mass_kg']:>9.1f}{r['fos']:>7.3f}{c['line_A_N']:>9.1f}"
              f"{c['line_B_N']:>9.1f}{('none' if not c['uplift'] else str(c['uplift'])):>8}"
              f"{r['case301']['max_abs_uz_mm']:>10.3f}")
