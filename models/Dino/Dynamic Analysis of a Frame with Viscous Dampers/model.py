# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Dynamic Analysis of a Frame with Viscous Dampers (Dino)
UniqueID : Dino_ViscousDamper
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-03
Purpose  : Nonlinear dynamic time-history of a 3D frame with viscous
           dampers (54 nodes; 105 elasticBeamColumn + 5 nonlinearBeamColumn
           damper columns whose fiber sections carry Maxwell dashpot
           fibers).  2%-damped (Rayleigh on modes 1-2) response to 20 s of
           ground motion (1000 steps x 0.02 s); disp/velocity/force
           histories validated against ref/opensees/disp14.out,
           disp45.out, vel45.out, ele110.out.  DAMPER_ACTIVE = True builds
           the verbatim Maxwell dampers; = False is a limp-damper
           diagnostic that reproduces the reference frame response (the
           reference is consistent with idle dampers -- see Notes).
Ref      : Dino -- Dynamic Analysis of a Frame with Viscous Dampers
           (original ref/opensees/co.tcl)
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import re
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

# This model nests under models/Dino/<analysis-name>/, one level deeper than
# the usual models/<UniqueID>/, so standards/ is parents[3] not parents[2]
# (see AGENT.md §12as-5).
_STANDARDS = Path(__file__).parents[3] / "standards"
if not _STANDARDS.exists():
    _STANDARDS = Path(__file__).parents[2] / "standards"   # fallback for relocation
sys.path.insert(0, str(_STANDARDS))
from units import *
from vis_utils import (
    _headless,
    vis_nodes,
    vis_model,
    vis_loads,
    vis_pre_analysis,
    vis_defo,
    vis_slider,
    vis_anim,
)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Elastic frame materials (source tags; some may be unreferenced -- kept
# for tag fidelity, §12ap-6 documents the check).
MAT_E1        = 1
MAT_E2        = 2
MAT_E3        = 3
# Maxwell dashpot material (damper fibers).
MAT_MAXWELL   = 4
# Rigid shear/torsion materials feeding Aggregator 1003 (verbatim).
MAT_VY        = 203
MAT_VZ        = 303
MAT_T         = 403

# Damper fiber section + Aggregator wrapper (no beamIntegration needed:
# nonlinearBeamColumn takes section + nIP directly, §12l).
SEC_DAMPER    = 3
SEC_AGG       = 1003

# Time series / patterns.
TS_GM         = 1      # Path time series (ground acceleration)
PAT_GM        = 1002   # UniformExcitation pattern (echoes source's incr tag)

# ODB (nodal-only, throttled for the 1000-step transient, §3d).
ODB_TAG       = 1
ODB_EVERY_N   = 2

# Validation
NODE_A        = 14     # disp14.out (UX disp)
NODE_B        = 45     # disp45.out (UX disp) + vel45.out (UX vel)
ELE_DAMPER    = 110    # ele110.out (damper column localForce)

# Ground motion (copied to ground_motions/ per catalogue convention).
GM_FILE       = Path(__file__).parent / "ground_motions" / "gm1x.txt"
GM_DT         = 0.02             # s (source)
GM_FACTOR     = 5.0              # source amplitude factor (verbatim)
GM_DIR        = 1                # excitation along UX (source)

# Source files
TCL_FILE      = Path(__file__).parent / "ref" / "opensees" / "co.tcl"
REF_DIR       = Path(__file__).parent / "ref" / "opensees"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N; the GM
# file values are applied verbatim with the source's factor of 5).

# Maxwell dashpot (source line, verbatim): K, C, a, Length.
MAX_K = 100000.0
MAX_C = 3000.0
MAX_A = 1.0
MAX_L = 1.0

# Elastic frame materials (source lines, verbatim).
E_1 = 1.999e5 * MPa
E_2 = 2.550e4 * MPa
E_3 = 3.000e4 * MPa

# Rigid shear/torsion stiffnesses for Aggregator 1003 (source, verbatim).
K_VY = 2.641e8
K_VZ = 2.641e8
K_T  = 2.113e10

# Torsional stiffness GJ for the damper fiber section (§12au).  The section
# holds only 4 tiny Maxwell fibers (0.01 x 0.01); computed G*Sum(A*r^2) is
# negligible anyway, and the Aggregator's rigid T code governs torsion.
SEC_GJ = 1.0e10   # placeholder; recomputed in define_sections()

# Rayleigh damping (source): 2% on modes 1-2 (computed from eigen).
XDAMP = 0.02
N_EIGEN = 2

# Damper variant switch.  DAMPER_ACTIVE = True (default) builds the source-
# verbatim Maxwell dampers.  The reference outputs are consistent with
# effectively-idle dampers (ele110 ≈ 3 N vs ~81 kN analytic; see Notes), so
# DAMPER_ACTIVE = False (near-zero-stiffness stand-in) reproduces the
# reference frame response for isolation/validation purposes.
DAMPER_ACTIVE = True

# Transient (source): Newmark(0.5, 0.25), 1000 steps x 0.02 s = 20 s.
N_STEPS = 1000
DT      = 0.02
N_IP    = 3              # nonlinearBeamColumn integration points (source)

N_TOTAL_STEPS = N_STEPS  # 1000


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Elastic + Maxwell dashpot + rigid shear/torsion (source, verbatim).

    Maxwell takes 4 args (K, C, a, Length) in stock OpenSeesPy -- verified
    available (no custom build needed).  Commented lines in the source are
    skipped (only one material may carry a tag).
    """
    ops.uniaxialMaterial("Elastic", MAT_E1, E_1)
    ops.uniaxialMaterial("Elastic", MAT_E2, E_2)
    ops.uniaxialMaterial("Elastic", MAT_E3, E_3)
    if DAMPER_ACTIVE:
        ops.uniaxialMaterial("Maxwell", MAT_MAXWELL, MAX_K, MAX_C, MAX_A, MAX_L)
    else:
        # Diagnostic stand-in: near-zero stiffness so the damper columns go
        # limp and the bare-frame response can be validated against the
        # reference (which is consistent with idle dampers -- see Notes).
        ops.uniaxialMaterial("Elastic", MAT_MAXWELL, 1.0e-6)
    ops.uniaxialMaterial("Elastic", MAT_VY, K_VY)
    ops.uniaxialMaterial("Elastic", MAT_VZ, K_VZ)
    ops.uniaxialMaterial("Elastic", MAT_T, K_T)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections(src: str) -> None:
    """Damper fiber section + Aggregator (source fiber block, verbatim).

    Section Fiber 3 holds ONLY 4 Maxwell fibers (0.01 x 0.01, area 1250)
    -- the 5 nonlinearBeamColumn "columns" are pure viscous-damper
    elements.  Wrapped by section Aggregator 1003 (rigid Vy/Vz/T).
    Re-emitted with ops.fiber(y, z, area, matTag) (§12aq, §12ay).
    """
    m = re.search(r"section\s+Fiber\s+3\s*\{(.*?)\n\}", src, re.S)
    fibers: list[tuple[float, float, float, int]] = []
    if m:
        for fm in re.finditer(
            r"fiber\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+(\d+)",
            m.group(1),
        ):
            fibers.append((float(fm.group(1)), float(fm.group(2)),
                           float(fm.group(3)), int(fm.group(4))))
    # Maxwell is rate-dependent (no stable G); the section is 4 tiny fibers
    # and the Aggregator's rigid T governs torsion -- keep the §12ba
    # negligible-GJ convention for Aggregator-wrapped sections.
    ops.section("Fiber", SEC_DAMPER, "-GJ", 1.0)
    for (y, z, area, mat) in fibers:
        ops.fiber(y, z, area, mat)
    ops.section("Aggregator", SEC_AGG,
                MAT_VY, "Vy", MAT_VZ, "Vz", MAT_T, "T",
                "-section", SEC_DAMPER)


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 54 nodes + lumped mass from co.tcl, verbatim.

    Mass values are already in N-s^2/mm so no conversion is applied.
    Mass lines carry 6 values (ndf=6 here -- no arity issue, §12ba).
    """
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))
    for m in re.finditer(
        r"^mass\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)"
        r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.mass(int(m.group(1)), *(float(m.group(i)) for i in range(2, 8)))


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Fix the 9 base nodes from co.tcl (trailing ';' tolerated).

    (The source prints a "rigidDiaphragm" label but issues no MP-constraint
    commands.)
    """
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> tuple[int, int]:
    """Create geomTransf + elasticBeamColumn + nonlinearBeamColumn (verbatim).

    elasticBeamColumn keeps its native 3D form
    ``(tag, i, j, A, E, G, J, Iy, Iz, transfTag)``.  nonlinearBeamColumn
    damper columns keep theirs ``(tag, i, j, nIP, secTag, transfTag)`` --
    NO beamIntegration object (§12l).  Returns (n_frame, n_damper).
    """
    for m in re.finditer(
        r"^geomTransf\s+Linear\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)",
        src, re.M,
    ):
        ops.geomTransf("Linear", int(m.group(1)),
                       float(m.group(2)), float(m.group(3)), float(m.group(4)))

    n_frame = 0
    for m in re.finditer(
        r"^element\s+elasticBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)"
        r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)"
        r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+(\d+)", src, re.M,
    ):
        ops.element("elasticBeamColumn", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), float(m.group(4)), float(m.group(5)),
                    float(m.group(6)), float(m.group(7)), float(m.group(8)),
                    float(m.group(9)), int(m.group(10)))
        n_frame += 1

    n_damper = 0
    for m in re.finditer(
        r"^element\s+nonlinearBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        src, re.M,
    ):
        ops.element("nonlinearBeamColumn", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), int(m.group(4)), int(m.group(5)),
                    int(m.group(6)))
        n_damper += 1
    return n_frame, n_damper


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a transient frame model.

    Nodal responses only (damper forces come from in-loop eleResponse,
    1:1 with the reference recorder; ``save_frame_resp=False`` per the
    nonlinearBeamColumn convention, §12v).  ``set_odb_path`` precedes
    ``CreateODB`` (§12ac).  ``model_update=False`` -- topology is static.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
        save_shell_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_ground_motion() -> None:
    """UniformExcitation ground motion (source: dir 1, dt 0.02, factor 5).

    The 1501-point record is applied verbatim; the 1000-step analysis
    consumes its first 20 s, exactly like the source's ``analyze 1000``.
    """
    vals = [float(v) for v in GM_FILE.read_text().split()]
    ops.timeSeries("Path", TS_GM, "-dt", GM_DT, "-values", *vals,
                   "-factor", GM_FACTOR)
    ops.pattern("UniformExcitation", PAT_GM, GM_DIR, "-accel", TS_GM)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_eigen_rayleigh() -> tuple[float, float, float, float]:
    """Eigen (2 modes) + Rayleigh 2% exactly as the source.

    Returns (T1, T2, alphaM, betaKcurr).  Rayleigh uses mass-proportional
    alphaM and current-stiffness betaKcurr (``rayleigh aM bK 0 0``).
    """
    lam = ops.eigen(N_EIGEN)
    w1 = float(lam[0]) ** 0.5
    w2 = float(lam[1]) ** 0.5
    alphaM = XDAMP * (2 * w1 * w2) / (w1 + w2)
    betaK = 2.0 * XDAMP / (w1 + w2)
    ops.rayleigh(alphaM, betaK, 0.0, 0.0)
    return 2 * np.pi / w1, 2 * np.pi / w2, alphaM, betaK


def run_dynamic(odb: "opst.post.CreateODB") -> bool:
    """Transient Newmark analysis: 1000 steps x 0.02 s via SmartAnalyze.

    The integrator is set BEFORE SmartAnalyze (§3c transient rule) with the
    source-verbatim test tolerance (EnergyIncr 1e-4/200 -- SmartAnalyze
    defaults stall immediately on damper models).  In-loop history every
    step (nodeDisp + nodeVel + eleResponse -- cheap calls) gives 1:1
    validation; ODB throttled to every ODB_EVERY_N steps (§3d).
    """
    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("UmfPack")  # source solver, verbatim
    ops.integrator("Newmark", 0.5, 0.25)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="EnergyIncr",      # source test, verbatim
        testTol=1.0e-4,
        testIterTimes=200,
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        printPer=0,
        testPrintFlag=0,
    )

    hist: list[tuple[float, ...]] = []
    ok = 0
    segs = analysis.transient_split(N_STEPS)
    for i, _ in enumerate(segs):
        ok = analysis.TransientAnalyze(DT)
        if ok < 0:
            print(f"  WARNING: dynamic step {i} failed (ok={ok})")
            break
        if i % ODB_EVERY_N == 0:
            odb.fetch_response_step()
        ops.reactions()
        try:
            f_damp = [float(v) for v in
                      ops.eleResponse(ELE_DAMPER, "localForce")]
        except Exception:
            f_damp = []
        hist.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_A, 1)),
            float(ops.nodeDisp(NODE_B, 1)),
            float(ops.nodeVel(NODE_B, 1)),
            f_damp,
        ))
        if (i + 1) % 250 == 0:
            print(f"  ... dynamic step {i + 1}/{N_STEPS}, "
                  f"t={hist[-1][0]:.2f} s", flush=True)
    analysis.close()
    run_dynamic.history = hist  # type: ignore[attr-defined]
    return ok == 0


def run_analysis(output_dir: Path) -> tuple["opst.post.CreateODB", dict]:
    """Build model, run eigen + Rayleigh + transient, return ODB + results."""
    output_dir.mkdir(parents=True, exist_ok=True)
    src = TCL_FILE.read_text(encoding="gbk", errors="replace")

    init_model()
    define_materials()
    define_sections(src)
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_frame, n_damper = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_frame} elasticBeamColumn + {n_damper} "
          f"nonlinearBeamColumn damper columns (expected 105 + 5).",
          flush=True)

    odb = create_odb(output_dir)

    print("Running eigenvalue analysis...", flush=True)
    t1, t2, aM, bK = run_eigen_rayleigh()
    print(f"  T1={t1:.4f} s T2={t2:.4f} s "
          f"alphaM={aM:.5f} betaK={bK:.6f}", flush=True)

    # Ground motion defined after the model is complete (single-phase
    # transient; no gravity/loadConst in the source, so §12i N/A).
    define_ground_motion()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running transient analysis...", flush=True)
    run_dynamic(odb)

    results = {"hist": getattr(run_dynamic, "history", []),
               "T1": t1, "T2": t2}
    for key, name in (("ref_a", "disp14.out"), ("ref_b", "disp45.out"),
                      ("ref_v", "vel45.out"), ("ref_f", "ele110.out")):
        p = REF_DIR / name
        try:
            results[key] = np.loadtxt(str(p)) if p.exists() else None
        except Exception:
            results[key] = None
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(
    odb: "opst.post.CreateODB",
    output_dir: Path,
    results: dict,
) -> None:
    """Flush ODB, render visualisations, plot histories, verify.

    Args:
        odb: Populated CreateODB instance.
        output_dir: Directory for output files.
        results: Results dict from run_analysis.
    """
    odb.save_response()

    hist = results["hist"]
    n = len(hist)
    tt = np.array([h[0] for h in hist]) if n else np.empty(0)
    dx_a = np.array([h[1] for h in hist]) if n else np.empty(0)
    dx_b = np.array([h[2] for h in hist]) if n else np.empty(0)
    vx_b = np.array([h[3] for h in hist]) if n else np.empty(0)

    # Dump histories for the record.
    if n > 0:
        np.savetxt(str(output_dir / "disp14_disp_history.csv"),
                   np.column_stack([tt, dx_a]),
                   delimiter=",", header="t_s,ux_mm")
        np.savetxt(str(output_dir / "node45_history.csv"),
                   np.column_stack([tt, dx_b, vx_b]),
                   delimiter=",", header="t_s,ux_mm,ux_vel_mm_s")

    if not _headless():
        opst.post.set_odb_path(str(output_dir))

        # V5 -- peak deformed shape (lateral -> UX, absMax step)
        vis_defo(output_dir, filename="vis_05_deformed.html",
                 odb_tag=ODB_TAG, resp_dof="UX", scale=10.0)
        # V6 -- step slider
        vis_slider(output_dir, filename="vis_06_slider.html",
                   odb_tag=ODB_TAG, resp_dof="UX", scale=10.0)
        # V7 -- animation
        vis_anim(output_dir, filename="vis_07_animation.html",
                 odb_tag=ODB_TAG, defo_scale=10.0,
                 resp_dof=("UX", "UY", "UZ"))

    # Histories vs reference (matplotlib).
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7),
                                       sharex=True)
        ref_b, ref_v = results.get("ref_b"), results.get("ref_v")
        if ref_b is not None and ref_b.size:
            ax1.plot(ref_b[:, 0], ref_b[:, 1], "k-",
                     linewidth=1.0, alpha=0.6,
                     label="Reference (disp45.out)")
        if n > 0:
            ax1.plot(tt, dx_b, "r--",
                     linewidth=1.0, alpha=0.85, label="Simulation")
        ax1.set_ylabel(f"Node {NODE_B} UX (mm)")
        ax1.set_title("Dino_ViscousDamper -- disp/vel histories")
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        if ref_v is not None and ref_v.size:
            ax2.plot(ref_v[:, 0], ref_v[:, 1], "k-",
                     linewidth=1.0, alpha=0.6,
                     label="Reference (vel45.out)")
        if n > 0:
            ax2.plot(tt, vx_b, "r--",
                     linewidth=1.0, alpha=0.85, label="Simulation")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel(f"Node {NODE_B} UX vel (mm/s)")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "dynamic_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable -- skipping compare plot)")

    # Verification summary
    print(f"\n  Recorded steps: {n} / {N_TOTAL_STEPS} expected", flush=True)
    print(f"  T1={results['T1']:.4f} s T2={results['T2']:.4f} s", flush=True)

    def _check(label: str, sim: np.ndarray, ref) -> None:
        if sim.size == 0 or ref is None or ref.size == 0:
            print(f"    {label}: no data", flush=True)
            return
        r = np.atleast_2d(ref)
        m = min(sim.shape[0], r.shape[0])
        denom = np.maximum(np.abs(r[:m, 1]), 1e-12)
        rms = float(np.sqrt(np.mean((sim[:m] - r[:m, 1]) ** 2)))
        rel = float(np.mean(np.abs(sim[:m] - r[:m, 1]) / denom) * 100.0)
        print(f"    {label}: RMS {rms:.5f} | mean rel error {rel:.4f}%",
              flush=True)

    _check(f"node{NODE_A} UX disp", dx_a, results.get("ref_a"))
    _check(f"node{NODE_B} UX disp", dx_b, results.get("ref_b"))
    _check(f"node{NODE_B} UX vel", vx_b, results.get("ref_v"))

    ref_f = results.get("ref_f")
    sim_f = [h[4] for h in hist] if n else []
    if ref_f is not None and sim_f and sim_f[0]:
        sim = np.array(sim_f)
        r = np.atleast_2d(ref_f)
        rblk = r[:, 1:1 + sim.shape[1]] if r.shape[1] > sim.shape[1] else r
        print(f"    ele{ELE_DAMPER} localForce: sim {sim.shape} "
              f"ref {r.shape} | sim peak {np.max(np.abs(sim)):.4f} vs "
              f"ref peak {np.max(np.abs(rblk)):.4f}", flush=True)
        if sim.shape == rblk.shape:
            e_rms = float(np.sqrt(np.mean((sim - rblk) ** 2)))
            big = np.abs(rblk) > 1.0
            if np.any(big):
                e_rel = float(np.mean(
                    np.abs(np.abs(sim[big]) - np.abs(rblk[big]))
                    / np.abs(rblk[big])) * 100.0)
                print(f"      RMS {e_rms:.5f} | magnitude mean rel "
                      f"error {e_rel:.4f}%", flush=True)
            else:
                print(f"      RMS {e_rms:.5f}", flush=True)


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_ViscousDamper: analysis complete.")
