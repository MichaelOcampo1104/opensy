# ── 0. FILE HEADER ─────────────────────────────────────────────────────────────
"""
Model    : P103 movable platform — 3D steel frame, COMB 301 counter-check
UniqueID : P103_MovablePlatform
Author   : Muse Spark (OpenCode session)
Date     : 2026-09-13
Purpose  : Independent OpenSeesPy counter-check of the STAAD 3D movable
           platform model under COMB 301 (1.0 DL + cantilever LL): verify
           support reactions and the no-uplift (no-overturning) verdict.
Ref      : STAAD 3D model 3D_Movable_bcad-model.std (FINAL 12:41 run:
           SELFWEIGHT Y -1, no counterweight, LOAD 3 on 23-25) and the
           equivalent-beam check overturning_check.py (FoS 1.72, RA +1.20 kN).
Units    : N, mm, MPa  (see standards/units.py)
Notes    : All source values in m / kN / kN-m converted with unit
           multipliers (no Pa / kg use, per AGENT.md 12j).
           OpenSees beamUniform acts in element LOCAL axes while STAAD UNI
           GY acts in global Y, so every UDL is transformed global->local
           via the member direction + vecxz (see _local_udl). Verified by
           construction probes: transverse-only and axial-only cantilevers
           recover wL4/8EI and wL2/2AE exactly, and ops.reactions() must be
           called before ops.nodeReaction (else 0.0 is returned).
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
# numbers (diffed 1:1 against the .std MEMBER INCIDENCES block).
TS_GRAVITY = 1
PAT_COMB301 = 2

TRANS_XZ = 1   # vecxz (0,0,1): members in / parallel to the X-Y plane
TRANS_YZ = 2   # vecxz (1,0,0): verticals, Z-runners, Y-Z diagonals

# Supports: STAAD PINNED joints (translations restrained, rotations free)
SUPPORT_NODES = (1, 6, 7, 11, 16, 17)
LINE_A_NODES = (1, 6, 7)        # Frame A, Z = 0
LINE_B_NODES = (11, 16, 17)     # Frame B, Z = 0.7 (tipping axis)

# ── 3. PARAMETERS ──────────────────────────────────────────────────────────────
# --- Geometry: STAAD JOINT COORDINATES block (originally m) ---
JOINTS_M = {
    1: (0.0, 0.000, 0.00), 2: (0.0, 0.879, 0.00),
    3: (0.0, 1.758, 0.00), 4: (0.5, 1.758, 0.00),
    5: (0.5, 0.879, 0.00), 6: (0.5, 0.000, 0.00),
    7: (2.0, 0.000, 0.00),
    11: (0.0, 0.000, 0.70), 12: (0.0, 0.879, 0.70),
    13: (0.0, 1.758, 0.70), 14: (0.5, 1.758, 0.70),
    15: (0.5, 0.879, 0.70), 16: (0.5, 0.000, 0.70),
    17: (2.0, 0.000, 0.70),
    23: (0.0, 1.758, 1.35), 24: (0.5, 1.758, 1.35),
}

# --- Topology: STAAD MEMBER INCIDENCES block: member -> (joint_i, joint_j) ---
MEMBERS = {
    1: (1, 2), 2: (2, 3), 3: (6, 5), 4: (5, 4), 5: (3, 4), 6: (2, 5),
    7: (7, 4),
    11: (11, 12), 12: (12, 13), 13: (16, 15), 14: (15, 14), 15: (13, 14),
    16: (12, 15), 17: (17, 14),
    21: (3, 13), 22: (4, 14), 23: (13, 23), 24: (14, 24), 25: (23, 24),
    26: (2, 12), 27: (5, 15), 28: (23, 12), 29: (24, 15),
}

# --- Sections: STAAD MEMBER PROPERTY block (originally m2 / m4) ---
# SHS 100x100x12.0 for 1-6, 11-16, 21-29; "100x50x18.7" RHS for 7, 17.
RHS_MEMBERS = (7, 17)
AX_SHS = 0.004224 * m**2      # [mm2]
IX_SHS = 8.177e-06 * m**4     # [mm4] torsion constant
IY_SHS = 5.553e-06 * m**4     # [mm4]
IZ_SHS = 5.553e-06 * m**4     # [mm4]
AX_RHS = 0.004211 * m**2      # [mm2]
IX_RHS = 2.151e-06 * m**4     # [mm4]
IY_RHS = 1.031e-06 * m**4     # [mm4]
IZ_RHS = 3.909e-06 * m**4     # [mm4]

# --- Material: STAAD DEFINE MATERIAL (E originally kN/m2) ---
E_STEEL_MOD = 2.0e8 * kN / m**2   # 200000 N/mm2  [N/mm2]
NU_STEEL = 0.3                    # [-]
G_STEEL_MOD = E_STEEL_MOD / (2.0 * (1.0 + NU_STEEL))  # [N/mm2]

# --- Unit weight: STAAD DENSITY (originally kN/m3) ---
GAMMA_STEEL = 76.8 * kN / m**3    # 7.68e-5 N/mm3  [N/mm3]

# --- Applied UDLs, COMB 301 = LOAD 1 + LOAD 3 (originally kN/m) ---
W_GRATING = 0.15 * kN / m         # LOAD 1 on members 21-24  [N/mm]
W_ANGLE = 0.03 * kN / m           # LOAD 1 on 5,7,17,21,23,24,25  [N/mm]
W_LL = 0.81 * kN / m              # LOAD 3 on 23,24,25  [N/mm]
GRATING_MEMBERS = (21, 22, 23, 24)
ANGLE_MEMBERS = (5, 7, 17, 21, 23, 24, 25)
LL_MEMBERS = (23, 24, 25)
# FINAL model carries no counterweight (both CON lines commented out).

# --- Reference reactions for the counter-check verdict ---
# STAAD headless 12:41 run, COMB 301 line sums (FY, up +); Python beam check.
STAAD_LINE_A_N = 1.21 * kN        # joints 1+6+7  [N]
STAAD_LINE_B_N = 7.51 * kN        # joints 11+16+17  [N]
PYTHON_RA_N = 1.203 * kN          # [N]
PYTHON_RB_N = 7.515 * kN          # [N]

# --- Tipping axis (Frame B support line, originally m) ---
Z_AXIS = 0.7 * m                  # [mm]

# --- Analysis ---
N_STEPS_GRAVITY = 10

# Transformation assignment: vecxz must not parallel the member axis.
ELE_TRANS = {}
for _m in (5, 6, 7, 15, 16, 17, 25):
    ELE_TRANS[_m] = TRANS_XZ
for _m in (1, 2, 3, 4, 11, 12, 13, 14, 21, 22, 23, 24, 26, 27, 28, 29):
    ELE_TRANS[_m] = TRANS_YZ


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
    vec = np.array([0.0, 0.0, 1.0]) if ELE_TRANS[mid] == TRANS_XZ \
        else np.array([1.0, 0.0, 0.0])
    z = vec - float(np.dot(vec, x)) * x
    z = z / np.linalg.norm(z)
    y = np.cross(z, x)
    g = np.array([0.0, -w_global_down, 0.0])
    return float(np.dot(g, x)), float(np.dot(g, y)), float(np.dot(g, z))


# ── 4. MODEL INITIALISATION ────────────────────────────────────────────────────
def init_model() -> None:
    """Initialise 3D model (ndm=3, ndf=6)."""
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
        ops.node(tag, x * m, y * m, z * m)


# ── 8. BOUNDARY CONDITIONS ─────────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Pin supports: restrain UX/UY/UZ, leave RX/RY/RZ free (STAAD PINNED)."""
    for tag in SUPPORT_NODES:
        ops.fix(tag, 1, 1, 1, 0, 0, 0)


# ── 9. ELEMENTS ────────────────────────────────────────────────────────────────
def define_elements() -> None:
    """elasticBeamColumn members with per-orientation Linear transf."""
    ops.geomTransf("Linear", TRANS_XZ, 0.0, 0.0, 1.0)
    ops.geomTransf("Linear", TRANS_YZ, 1.0, 0.0, 0.0)
    for mid, (j1, j2) in MEMBERS.items():
        if mid in RHS_MEMBERS:
            a, jx, iy, iz = AX_RHS, IX_RHS, IY_RHS, IZ_RHS
        else:
            a, jx, iy, iz = AX_SHS, IX_SHS, IY_SHS, IZ_SHS
        ops.element("elasticBeamColumn", mid, j1, j2, a, E_STEEL_MOD,
                    G_STEEL_MOD, jx, iy, iz, ELE_TRANS[mid])


# ── 10. OUTPUT DATABASE (ODB) ──────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise ODB after model is fully built (all nodes + frames)."""
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=1,
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


def define_comb301_loads() -> tuple:
    """Apply COMB 301 (LOAD 1 + LOAD 3) member UDLs.

    Returns (total vertical load [N], applied moment about Frame B [Nmm]).
    """
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_COMB301, TS_GRAVITY)
    total = 0.0
    moment_b = 0.0
    z_axis = Z_AXIS
    for mid, (j1, j2) in MEMBERS.items():
        a = AX_RHS if mid in RHS_MEMBERS else AX_SHS
        p1 = np.array(JOINTS_M[j1]) * m
        p2 = np.array(JOINTS_M[j2]) * m
        le = float(np.linalg.norm(p2 - p1))
        w = a * GAMMA_STEEL
        if mid in GRATING_MEMBERS:
            w += W_GRATING
        if mid in ANGLE_MEMBERS:
            w += W_ANGLE
        if mid in LL_MEMBERS:
            w += W_LL
        _add_member_udl(mid, w)
        zc = float((p1[2] + p2[2]) / 2.0)
        total += w * le
        # downward force is -w: M_B = (-w) * le * (zc - z_axis)
        moment_b += -w * le * (zc - z_axis)
    return total, moment_b


# ── 12. ANALYSIS ───────────────────────────────────────────────────────────────
def run_gravity(odb: "opst.post.CreateODB",
                n_steps: int = N_STEPS_GRAVITY) -> None:
    """Load-controlled gravity via the AGENT.md 3c permitted exception:
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
            raise RuntimeError(f"gravity step failed (ok={ok})")
        odb.fetch_response_step()
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()


def run_analysis(output_dir: Path) -> tuple:
    """Build model, run COMB 301 gravity, return (odb, applied_total_N)."""
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
    odb = create_odb(output_dir)
    applied_total, applied_moment_b = define_comb301_loads()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running COMB 301 gravity (load-controlled, "
          f"{N_STEPS_GRAVITY} steps) ...")
    run_gravity(odb)
    return odb, applied_total, applied_moment_b


# ── 13. POST-PROCESSING ────────────────────────────────────────────────────────
def _line_sum(nodes: tuple) -> float:
    """Sum of vertical (FY) support reactions over a node line [N]."""
    return sum(float(ops.nodeReaction(n, 2)) for n in nodes)


def post_process(odb: "opst.post.CreateODB", output_dir: Path,
                 applied_total: float, applied_moment_b: float) -> dict:
    """Flush ODB, deformed shape, reactions vs STAAD/Python verdict table."""
    odb.save_response()
    ops.reactions()  # mandatory: nodeReaction reads 0.0 without this call
    line_a = _line_sum(LINE_A_NODES)
    line_b = _line_sum(LINE_B_NODES)
    joints = {n: float(ops.nodeReaction(n, 2)) for n in SUPPORT_NODES}

    fy_res = applied_total - (line_a + line_b)
    arms = {n: (JOINTS_M[n][2] * m - Z_AXIS) for n in SUPPORT_NODES}
    mb_res = applied_moment_b + sum(joints[n] * arms[n]
                                    for n in SUPPORT_NODES)

    results = {
        "applied_total_N": applied_total,
        "opensees_line_A_N": line_a,
        "opensees_line_B_N": line_b,
        "opensees_joints_N": joints,
        "staad_line_A_N": STAAD_LINE_A_N,
        "staad_line_B_N": STAAD_LINE_B_N,
        "python_ra_N": PYTHON_RA_N,
        "python_rb_N": PYTHON_RB_N,
        "fy_residual_N": fy_res,
        "mb_residual_Nmm": mb_res,
        "uplift": [n for n in SUPPORT_NODES if joints[n] < 0.0],
    }

    import json
    with open(output_dir / "reaction_summary.json", "w",
              encoding="utf-8") as fh:
        json.dump({k: (v if not isinstance(v, dict)
                       else {str(kk): vv for kk, vv in v.items()})
                   for k, v in results.items()}, fh, indent=2)
    print(f"reaction summary written: {output_dir / 'reaction_summary.json'}")

    print("\nCounter-check: OpenSees vs STAAD vs Python beam (COMB 301, N):")
    print(f"  applied total      : {applied_total:12.1f}")
    print(f"  OpenSees line A    : {line_a:12.1f}   "
          f"STAAD {STAAD_LINE_A_N:8.1f}   Python {PYTHON_RA_N:8.1f}")
    print(f"  OpenSees line B    : {line_b:12.1f}   "
          f"STAAD {STAAD_LINE_B_N:8.1f}   Python {PYTHON_RB_N:8.1f}")
    print(f"  joints " + " ".join(f"{n}:{joints[n]:+.1f}"
                                  for n in SUPPORT_NODES))
    print(f"  equilibrium dFy    : {fy_res:+.3f} N,  dM_B : {mb_res:+.1f} Nmm")
    da = abs(line_a - STAAD_LINE_A_N)
    db = abs(line_b - STAAD_LINE_B_N)
    verdict = (not results["uplift"] and da < 20.0 and db < 20.0
               and abs(fy_res) < 1.0)
    print(f"  verdict: {'PASS - no uplift, lines match STAAD within 20 N' if verdict else 'FAIL'}")
    results["verdict"] = "PASS" if verdict else "FAIL"

    if not _headless():
        vis_defo(output_dir, filename="vis_05_defo_gravity.html", odb_tag=1,
                 resp_dof="UY")
    return results


# ── 14. MAIN ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, applied_total, applied_moment_b = run_analysis(output_dir)
    post_process(odb, output_dir, applied_total, applied_moment_b)
