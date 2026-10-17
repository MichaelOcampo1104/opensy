# ── 0. FILE HEADER ─────────────────────────────────────────────────────────────
"""
Model    : L-bar walkway 2 m — STAAD equivalent, ULS static
UniqueID : LbarWalkway2m
Author   : Muse Spark (OpenCode session)
Date     : 2026-09-23
Purpose  : Equivalent OpenSeesPy model of the STAAD "Lbar walkway.std"
           2 m walkway (2 x 1 m L-bar spans + diagonal brace), run at
           ULS 1.35 DL + 1.5 LL for member forces and reactions.
Ref      : models/2m L bars Walk way/Lbar walkway.std (STAAD SPACE,
           UNIT METER KN; joints 1-4, members 1-3, L75756 angles,
           SELFWEIGHT + 2.25 kN/m UDL on members 1-2, COMB 3 ULS)
Units    : N, mm, MPa  (see standards/units.py)
Notes    : All source values in m / kN / kN/m converted with unit
           multipliers (no bare numbers). Two deliberate deviations
           from the .std, both user-confirmed 2026-09-23: (a) member 3
           carries the same EA 75x75x6 (the .std assigns no property
           to member 3); (b) joint 4 is pinned (the .std defines no
           support there, which leaves joint 4 free - a mechanism).
           OpenSees beamUniform acts in element LOCAL axes while STAAD
           UNI GY acts in global Y, so every UDL is transformed
           global->local via the member direction + vecxz (see
           _member_udl_local, same CrdTransf convention as
           P103_MovablePlatform). ops.reactions() is called before any
           ops.nodeReaction read (else 0.0 is returned).
"""

# ── 1. IMPORTS ─────────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import (_headless, vis_nodes, vis_model, vis_loads,
                       vis_pre_analysis, vis_defo)

# ── 2. TAG REGISTRY ────────────────────────────────────────────────────────────
# Node tags reuse STAAD joint numbers; element tags reuse STAAD member
# numbers (diffed 1:1 against the .std JOINT COORDINATES / MEMBER
# INCIDENCES blocks).
TS_ULS = 1
PAT_ULS = 1

TRANS_XY = 1   # vecxz (0,0,1): all members lie in / parallel to X-Y plane

NODE_FIXED = 1   # STAAD SUPPORTS: 1 FIXED
NODE_PINNED = 4  # user-confirmed deviation: pinned (was free in .std)

# ── 3. PARAMETERS ──────────────────────────────────────────────────────────────
# --- Geometry: STAAD JOINT COORDINATES block (originally m) ---
JOINTS_M = {
    1: (0.0, 0.0, 0.0),
    2: (1.0, 0.0, 0.0),
    3: (2.0, 0.0, 0.0),
    4: (0.0, -0.6, 0.0),
}

# --- Topology: STAAD MEMBER INCIDENCES block: member -> (joint_i, joint_j) ---
MEMBERS = {
    1: (1, 2),
    2: (2, 3),
    3: (4, 2),
}

# --- Section: EA 75x75x6 per user confirmation (originally cm2 / cm4) ---
# Nominal equal-angle values: A = 8.73 cm2, Iy = Iz = 45.5 cm4 about
# geometric axes; J = (2b-t) t^3 / 3 = (150-6)*216/3 = 10368 mm4.
A_ANGLE = 8.73 * cm**2       # [mm2] -> 873
IY_ANGLE = 45.5 * cm**4      # [mm4] -> 455000
IZ_ANGLE = 45.5 * cm**4      # [mm4] -> 455000
J_ANGLE = 10368.0 * mm**4    # [mm4]

# --- Material: S275 per user confirmation ---
E_STEEL = 200000.0 * MPa     # [N/mm2]
NU_STEEL = 0.3               # [-]
G_STEEL = E_STEEL / (2.0 * (1.0 + NU_STEEL))  # [N/mm2]

# --- Unit weight: STAAD DEFINE MATERIAL density line (originally kN/m3) ---
GAMMA_STEEL = 76.8195 * kN / m**3  # [N/mm3] -> 7.682e-5

# --- Applied loads (originally kN/m) ---
W_LL = 2.25 * kN / m         # LOAD 2 UNI Y on members 1-2  [N/mm]
LL_MEMBERS = (1, 2)

# --- ULS factors: STAAD LOAD COMB 3 (1 1.35  2 1.5) ---
F_DL = 1.35
F_LL = 1.50

# --- Analysis ---
N_STEPS_ULS = 10


def _member_udl_local(mid: int, w_global_down: float) -> tuple:
    """Resolve a global downward UDL (N/mm, positive) on member mid into
    element-local (Wx axial, Wy, Wz transverse) components for beamUniform.

    Uses the OpenSees CrdTransf convention: x = (j-i)/L,
    z = vecxz - (vecxz.x)x normalised, y = z cross x.
    """
    j1, j2 = MEMBERS[mid]
    p1 = np.array(JOINTS_M[j1], dtype=float)
    p2 = np.array(JOINTS_M[j2], dtype=float)
    x = p2 - p1
    x = x / np.linalg.norm(x)
    vec = np.array([0.0, 0.0, 1.0])
    z = vec - float(np.dot(vec, x)) * x
    z = z / np.linalg.norm(z)
    y = np.cross(z, x)
    g = np.array([0.0, -w_global_down, 0.0])
    return float(np.dot(g, x)), float(np.dot(g, y)), float(np.dot(g, z))


# ── 4. MODEL INITIALISATION ────────────────────────────────────────────────────
def init_model() -> None:
    """Initialise 3D model (ndm=3, ndf=6) per STAAD SPACE."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ───────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Elastic beam-column elements take E/G directly - no materials."""
    pass


# ── 6. SECTIONS ────────────────────────────────────────────────────────────────
def define_sections() -> None:
    """Elastic beam-column elements take A/J/I directly - no sections."""
    pass


# ── 7. NODES ───────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Create one node per STAAD joint (tags = joint numbers), coords in mm."""
    for tag, (x, y, z) in JOINTS_M.items():
        ops.node(tag, x * m, y * m, z * m)  # originally m


# ── 8. BOUNDARY CONDITIONS ─────────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Joint 1 fixed (STAAD SUPPORTS); joint 4 pinned (user-confirmed)."""
    ops.fix(NODE_FIXED, 1, 1, 1, 1, 1, 1)
    ops.fix(NODE_PINNED, 1, 1, 1, 0, 0, 0)


# ── 9. ELEMENTS ────────────────────────────────────────────────────────────────
def define_elements() -> None:
    """elasticBeamColumn members, single Linear transf (all in X-Y plane)."""
    ops.geomTransf("Linear", TRANS_XY, 0.0, 0.0, 1.0)
    for mid, (j1, j2) in MEMBERS.items():
        ops.element("elasticBeamColumn", mid, j1, j2, A_ANGLE, E_STEEL,
                    G_STEEL, J_ANGLE, IY_ANGLE, IZ_ANGLE, TRANS_XY)


# ── 10. OUTPUT DATABASE (ODB) ──────────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag=1) -> "opst.post.CreateODB":
    """Initialise ODB after model is fully built (all nodes + frames)."""
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        save_nodal_resp=True,
        node_tags=list(JOINTS_M),
        save_frame_resp=True,
        frame_tags=list(MEMBERS),
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ────────────────────────────────────────────────────────────────
def _add_member_udl(mid: int, w_down: float) -> None:
    """Apply a global downward UDL (N/mm) on one member via beamUniform."""
    wx, wy, wz = _member_udl_local(mid, w_down)
    ops.eleLoad("-ele", mid, "-type", "-beamUniform", wy, wz, wx)


def define_uls_loads(f_dl: float = F_DL, f_ll: float = F_LL) -> float:
    """Apply factored loads = f_dl x (selfweight) + f_ll x (2.25 kN/m on 1-2).

    Defaults reproduce ULS COMB 3 (1.35 / 1.5); pass (1.0, 1.0) for SLS.

    Returns total applied vertical load [N].
    """
    ops.timeSeries("Linear", TS_ULS)
    ops.pattern("Plain", PAT_ULS, TS_ULS)
    w_sw = A_ANGLE * GAMMA_STEEL  # unfactored selfweight [N/mm]
    total = 0.0
    for mid, (j1, j2) in MEMBERS.items():
        p1 = np.array(JOINTS_M[j1]) * m
        p2 = np.array(JOINTS_M[j2]) * m
        le = float(np.linalg.norm(p2 - p1))
        w = f_dl * w_sw
        if mid in LL_MEMBERS:
            w += f_ll * W_LL
        _add_member_udl(mid, w)
        total += w * le
    return total


def member_w_values(f_dl: float, f_ll: float) -> dict:
    """Factored UDL intensity per member (global -Y, N/mm) for given factors."""
    w_sw = A_ANGLE * GAMMA_STEEL
    return {mid: f_dl * w_sw + (f_ll * W_LL if mid in LL_MEMBERS else 0.0)
            for mid in MEMBERS}


# ── 12. ANALYSIS ───────────────────────────────────────────────────────────────
def run_uls(odb: "opst.post.CreateODB",
            n_steps: int = N_STEPS_ULS) -> None:
    """Load-controlled ULS static via the AGENT.md 3c permitted exception:
    manual LoadControl/Linear loop (SmartAnalyze cannot do load control)."""
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / n_steps)
    ops.test("EnergyIncr", 1.0e-6, 100)
    ops.algorithm("Linear")
    ops.analysis("Static")
    for _ in range(n_steps):
        ok = ops.analyze(1)
        if ok != 0:
            raise RuntimeError(f"ULS step failed (ok={ok})")
        odb.fetch_response_step()
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def run_analysis(output_dir: Path, f_dl: float = F_DL, f_ll: float = F_LL,
                 odb_tag=1, case_label: str = "ULS 1.35DL+1.5LL") -> tuple:
    """Build model, run factored static, return (odb, applied_total_N)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)
    odb = create_odb(output_dir, odb_tag)
    applied_total = define_uls_loads(f_dl, f_ll)
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print(f"Running {case_label} (load-controlled, {N_STEPS_ULS} steps) ...")
    run_uls(odb)
    return odb, applied_total


# ── 13. POST-PROCESSING ────────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path,
                 applied_total: float,
                 case_label: str = "ULS 1.35DL+1.5LL",
                 stem: str = "uls", odb_tag=1) -> dict:
    """Flush ODB, deformed shape, equilibrium + member-force verdict table."""
    odb.save_response()
    ops.reactions()  # mandatory: nodeReaction reads 0.0 without this call
    joints = (NODE_FIXED, NODE_PINNED)
    rx = {n: float(ops.nodeReaction(n, 1)) for n in joints}
    ry = {n: float(ops.nodeReaction(n, 2)) for n in joints}
    rz = {n: float(ops.nodeReaction(n, 3)) for n in joints}
    dfy = applied_total - (ry[NODE_FIXED] + ry[NODE_PINNED])
    dfx = -(rx[NODE_FIXED] + rx[NODE_PINNED])
    dfz = -(rz[NODE_FIXED] + rz[NODE_PINNED])

    # NOTE (verified 2026-09-23 by inclined-cantilever probe): in this
    # openseespy build, eleResponse('forces') on a 3D elasticBeamColumn
    # returns node-on-element actions in GLOBAL axes, not element-local
    # forces (probe: N readout 0.0 / V readout = global vertical
    # resultant while reactions prove the axial UDL share was applied;
    # full-model nodal closure exact under the global reading, and the
    # 54.3 N axial-UDL share reappears exactly after projection).
    # Project onto the member frame for true local forces. The opstool
    # sectionForces diagrams are unaffected (built from local sections;
    # ODB axial spans +11.73 / -13.40 kN as expected).
    forces_raw, forces = {}, {}
    for mid, (j1, j2) in MEMBERS.items():
        f = [float(v) for v in ops.eleResponse(mid, "forces")]
        forces_raw[mid] = f
        p1 = np.array(JOINTS_M[j1], dtype=float)
        p2 = np.array(JOINTS_M[j2], dtype=float)
        xh = (p2 - p1) / np.linalg.norm(p2 - p1)
        yh = np.cross(np.array([0.0, 0.0, 1.0]), xh)
        ri = np.array([f[0], f[1], f[2]])    # node-on-element, i, global
        rj = np.array([f[6], f[7], f[8]])    # node-on-element, j, global
        # on-member: negate (element action); raw order is
        # [N, Vy, Vz, T, My, Mz] per end (element moment equilibrium:
        # Mi_z + Mj_z = wL.500 - Vj.1000 closes exactly on idx 5/11).
        forces[mid] = [
            float(-ri @ xh), float(-ri @ yh), float(-f[2]),
            float(-f[3]), float(-f[4]), float(-f[5]),
            float(rj @ xh), float(rj @ yh), float(-f[8]),
            float(-f[9]), float(-f[10]), float(-f[11]),
        ]

    results = {
        "applied_total_N": applied_total,
        "reactions_N": {str(n): {"FX": rx[n], "FY": ry[n], "FZ": rz[n]}
                        for n in joints},
        "equilibrium_dFx_N": dfx,
        "equilibrium_dFy_N": dfy,
        "equilibrium_dFz_N": dfz,
        "member_forces_local": {str(m): v for m, v in forces.items()},
        "member_forces_raw_global": {str(m): v
                                     for m, v in forces_raw.items()},
    }

    import json
    with open(output_dir / f"{stem}_summary.json", "w",
              encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    print(f"{case_label} summary written: {output_dir / f'{stem}_summary.json'}")

    print("")
    print("===============================================================")
    print(f"VERIFICATION REPORT - LbarWalkway2m - {case_label}")
    print("Source STAAD: 2m L bars Walk way/Lbar walkway.std (COMB 3)")
    print("---------------------------------------------------------------")
    print(f"Applied total (N)        : {applied_total:12.1f}")
    print(f"Reaction J1 FY (N)       : {ry[NODE_FIXED]:12.1f}   (fixed)")
    print(f"Reaction J4 FY (N)       : {ry[NODE_PINNED]:12.1f}   (pinned)")
    print(f"Equilibrium dFy (N)      : {dfy:+12.3f}")
    print(f"Equilibrium dFx/dFz (N)  : {dfx:+12.3f} / {dfz:+12.3f}")
    print("---------------------------------------------------------------")
    for mid, v in forces.items():
        print(f"Member {mid} local forces : " + " ".join(f"{x:+.1f}" for x in v))
    print("  (local on-member order: [Ni, Vyi, Vzi, Ti, Myi, Mzi, Nj, ...];")
    print("   N, Nmm; +N = tensile. Projected from global readouts.)")
    print("---------------------------------------------------------------")
    ok = abs(dfy) < 1.0 and abs(dfx) < 1.0 and abs(dfz) < 1.0
    print(f"OVERALL VERDICT: {'PASS - equilibrium within 1 N' if ok else 'FAIL'}")
    print("NOTE: counter-check vs STAAD .anl output pending - run")
    print("      STAAD ANALYSE and compare reactions/member forces (<=3%).")
    print("===============================================================")
    results["verdict"] = "PASS" if ok else "FAIL"

    if not _headless():
        vis_defo(output_dir, filename=f"vis_05_deformed_{stem}.html",
                 odb_tag=odb_tag, resp_dof="UY")
    return results


# ── 14. MAIN ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    _ap = argparse.ArgumentParser()
    _ap.add_argument("--case", choices=("uls", "sls"), default="uls")
    _args = _ap.parse_args()
    output_dir = Path(__file__).parent / "output"
    if _args.case == "sls":
        odb, applied_total = run_analysis(
            output_dir, 1.0, 1.0, "sls", "SLS 1.0DL+1.0LL")
        post_process(odb, output_dir, applied_total, "SLS 1.0DL+1.0LL", "sls")
    else:
        odb, applied_total = run_analysis(output_dir)
        post_process(odb, output_dir, applied_total)
