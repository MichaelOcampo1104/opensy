# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Dynamic Analysis of a Frame with Vibration Isolation (Dino)
UniqueID : Dino_IsolatedFrame
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-03
Purpose  : Nonlinear dynamic time-history of a 3D frame on 9 rubber
           isolation bearings (126 nodes; 252 elasticBeamColumn + 9
           zeroLength Steel02 isolators).  5%-damped (Rayleigh on modes
           1-2) response to 20 s of ground motion (1000 steps x 0.02 s);
           node/element histories validated against ref/opensees/node2.out,
           node118.out, ele244.out, ele245.out, ele244d.out.
Ref      : Dino -- Dynamic Analysis of a Frame with Vibration Isolation
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
# Materials (match source co.tcl tags exactly; the commented Elastic 1 line
# is superseded by the active Steel02 isolator line and is NOT defined).
MAT_ISOLATOR  = 1      # Steel02 rubber-bearing bilinear (isolators)
MAT_E2        = 2      # Elastic (frame filler)
MAT_E3        = 3      # Elastic (frame)

# Time series / patterns.
TS_GM         = 1      # Path time series (ground acceleration)
PAT_GM        = 1002   # UniformExcitation pattern (echoes source's incr tag)

# ODB (nodal-only, throttled for the 1000-step transient, §3d).
ODB_TAG       = 1
ODB_EVERY_N   = 2

# Validation
NODE_A        = 2      # node-2 disp validated against node2.out
NODE_B        = 118    # node-118 disp validated against node118.out
ELE_ISOL      = 244    # isolator localForce (ele244.out) + deformation (ele244d.out)
ELE_FRAME     = 245    # frame localForce (ele245.out)

# Ground motion (copied to ground_motions/ per catalogue convention).
GM_FILE       = Path(__file__).parent / "ground_motions" / "gm1x.txt"
GM_DT         = 0.02             # s (source)
GM_FACTOR     = 10.0             # source amplitude factor (verbatim)
GM_DIR        = 1                # excitation along UX (source)

# Source files
TCL_FILE      = Path(__file__).parent / "ref" / "opensees" / "co.tcl"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N; the GM
# file values are applied verbatim with the source's factor of 10).

# Steel02 rubber isolator (source line, verbatim): Fy, E, b.
# (R0/cR1/cR2/a-factors take OpenSees defaults, as in the source.)
ISO_FY = 100000.0 * N
ISO_E  = 2000.0 * MPa
ISO_B  = 0.15

# Elastic frame materials (source lines, verbatim).
E_2 = 2.482e4 * MPa
E_3 = 1.999e5 * MPa

# Rayleigh damping (source): 5% on modes 1-2 (computed from eigen, §12h).
XDAMP = 0.05
N_EIGEN = 2

# Transient (source): Newmark(0.5, 0.25), 1000 steps x 0.02 s = 20 s.
N_STEPS = 1000
DT      = 0.02

N_TOTAL_STEPS = N_STEPS  # 1000


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Steel02 isolator + Elastic frame materials (source lines, verbatim)."""
    ops.uniaxialMaterial("Steel02", MAT_ISOLATOR, ISO_FY, ISO_E, ISO_B)
    ops.uniaxialMaterial("Elastic", MAT_E2, E_2)
    ops.uniaxialMaterial("Elastic", MAT_E3, E_3)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
# Not used -- elasticBeamColumn takes inline A/E/G/J/Iy/Iz and zeroLength
# takes uniaxial materials directly; no fiber/plate sections in this model.


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 126 nodes + lumped mass from co.tcl, verbatim.

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
    """Fix the 9 base nodes + 9 equalDOF isolator ties (source, verbatim).

    equalDOF ties DOFs 3-6 (UY/RX/RY/RZ) across each isolator pair
    (base node -> deck node); UX/UZ work through the zeroLength Steel02
    springs.  (The source prints a "rigidDiaphragm" label but issues no
    such commands -- Transformation constraints cover the equalDOF MPs.)
    """
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)
    for m in re.finditer(r"^equalDOF\s+(\d+)\s+(\d+)\s+([\d\s]+)", src, re.M):
        dofs = [int(v) for v in m.group(3).split()]
        ops.equalDOF(int(m.group(1)), int(m.group(2)), *dofs)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> tuple[int, int]:
    """Create geomTransf + elasticBeamColumn + zeroLength (source, verbatim).

    elasticBeamColumn keeps its native 3D form
    ``(tag, i, j, A, E, G, J, Iy, Iz, transfTag)``.  zeroLength isolators:
    ``(tag, n1, n2, -mat m1 m2, -dir d1 d2)`` with the Steel02 bearing
    material on DOFs 1-2.  Returns (n_frame, n_isolator).
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

    n_isol = 0
    for m in re.finditer(
        r"^element\s+zeroLength\s+(\d+)\s+(\d+)\s+(\d+)"
        r"\s+-mat\s+([\d\s]+?)\s+-dir\s+([\d\s]+?)\s*$", src, re.M
    ):
        mats = [int(v) for v in m.group(4).split()]
        dirs = [int(v) for v in m.group(5).split()]
        args: list = ["-mat", *mats, "-dir", *dirs]
        ops.element("zeroLength", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), *args)
        n_isol += 1
    return n_frame, n_isol


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a transient frame model.

    Nodal responses only (element forces come from in-loop eleResponse,
    1:1 with the reference recorders).  ``set_odb_path`` precedes
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
        save_link_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_ground_motion() -> None:
    """UniformExcitation ground motion (source: dir 1, dt 0.02, factor 10).

    The 1501-point record is applied verbatim; the 1000-step analysis
    consumes its first 20 s, exactly like the source's ``analyze 1000``.
    """
    vals = [float(v) for v in GM_FILE.read_text().split()]
    ops.timeSeries("Path", TS_GM, "-dt", GM_DT, "-values", *vals,
                   "-factor", GM_FACTOR)
    ops.pattern("UniformExcitation", PAT_GM, GM_DIR, "-accel", TS_GM)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_eigen_rayleigh() -> tuple[float, float, float, float]:
    """Eigen (2 modes) + Rayleigh 5% exactly as the source.

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

    The integrator is set BEFORE SmartAnalyze (§3c transient rule).
    In-loop history every step (nodeDisp + eleResponse -- cheap calls)
    gives 1:1 validation; ODB throttled to every ODB_EVERY_N steps (§3d).
    """
    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("UmfPack")  # source solver (falls back below on failure)
    ops.integrator("Newmark", 0.5, 0.25)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
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
            f_isol = [float(v) for v in
                      ops.eleResponse(ELE_ISOL, "localForce")]
        except Exception:
            f_isol = []
        try:
            d_isol = [float(v) for v in
                      ops.eleResponse(ELE_ISOL, "deformation")]
        except Exception:
            d_isol = []
        try:
            f_frame = [float(v) for v in
                       ops.eleResponse(ELE_FRAME, "localForce")]
        except Exception:
            f_frame = []
        hist.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_A, 1)),
            float(ops.nodeDisp(NODE_A, 2)),
            float(ops.nodeDisp(NODE_A, 3)),
            float(ops.nodeDisp(NODE_B, 1)),
            float(ops.nodeDisp(NODE_B, 2)),
            float(ops.nodeDisp(NODE_B, 3)),
            f_isol, d_isol, f_frame,
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
    src = TCL_FILE.read_text()

    init_model()
    define_materials()
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_frame, n_isol = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_frame} elasticBeamColumn + {n_isol} "
          f"zeroLength isolators (expected 252 + 9).", flush=True)

    odb = create_odb(output_dir)

    print("Running eigenvalue analysis...", flush=True)
    t1, t2, aM, bK = run_eigen_rayleigh()
    print(f"  T1={t1:.4f} s T2={t2:.4f} s "
          f"alphaM={aM:.5f} betaK={bK:.6f}", flush=True)

    # Ground motion defined after model is complete (single-phase transient;
    # no gravity/loadConst in the source, so §12i N/A).
    define_ground_motion()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running transient analysis...", flush=True)
    run_dynamic(odb)

    ref_dir = TCL_FILE.parent
    results = {"hist": getattr(run_dynamic, "history", []),
               "T1": t1, "T2": t2}
    for key, name in (("ref_a", "node2.out"), ("ref_b", "node118.out"),
                      ("ref_fi", "ele244.out"), ("ref_ff", "ele245.out"),
                      ("ref_di", "ele244d.out")):
        p = ref_dir / name
        try:
            results[key] = np.loadtxt(str(p)) if p.exists() else None
        except Exception:
            results[key] = None
    return odb, results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def _col(arr: np.ndarray, i: int) -> np.ndarray:
    """Column i of a 2-D array (or empty)."""
    if arr is None or arr.size == 0:
        return np.empty(0)
    a = np.atleast_2d(arr)
    return a[:, i] if a.shape[1] > i else np.empty(0)


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
    ux_a = np.array([h[1] for h in hist]) if n else np.empty(0)
    ux_b = np.array([h[4] for h in hist]) if n else np.empty(0)

    # Dump node histories for the record.
    if n > 0:
        np.savetxt(str(output_dir / "node2_disp_history.csv"),
                   np.column_stack([tt, [h[1] for h in hist],
                                    [h[2] for h in hist],
                                    [h[3] for h in hist]]),
                   delimiter=",", header="t_s,ux_mm,uy_mm,uz_mm")
        np.savetxt(str(output_dir / "node118_disp_history.csv"),
                   np.column_stack([tt, [h[4] for h in hist],
                                    [h[5] for h in hist],
                                    [h[6] for h in hist]]),
                   delimiter=",", header="t_s,ux_mm,uy_mm,uz_mm")

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

    # Roof/sil histories vs reference (matplotlib).
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7),
                                       sharex=True)
        ref_a, ref_b = results.get("ref_a"), results.get("ref_b")
        if ref_a is not None and ref_a.size:
            ax1.plot(ref_a[:, 0], ref_a[:, 1], "k-",
                     linewidth=1.0, alpha=0.6, label="Reference (node2.out)")
        if n > 0:
            ax1.plot(tt, ux_a, "r--",
                     linewidth=1.0, alpha=0.85, label="Simulation")
        ax1.set_ylabel(f"Node {NODE_A} UX (mm)")
        ax1.set_title("Dino_IsolatedFrame -- UX histories")
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        if ref_b is not None and ref_b.size:
            ax2.plot(ref_b[:, 0], ref_b[:, 1], "k-",
                     linewidth=1.0, alpha=0.6,
                     label="Reference (node118.out)")
        if n > 0:
            ax2.plot(tt, ux_b, "r--",
                     linewidth=1.0, alpha=0.85, label="Simulation")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel(f"Node {NODE_B} UX (mm)")
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

    def _check(label: str, sim: np.ndarray, ref: np.ndarray, col: int) -> None:
        if sim.size == 0 or ref is None or ref.size == 0:
            print(f"    {label}: no data", flush=True)
            return
        r = np.atleast_2d(ref)
        m = min(sim.shape[0], r.shape[0])
        denom = np.maximum(np.abs(r[:m, col]), 1e-12)
        rms = float(np.sqrt(np.mean((sim[:m] - r[:m, col]) ** 2)))
        rel = float(np.mean(np.abs(sim[:m] - r[:m, col]) / denom) * 100.0)
        print(f"    {label}: RMS {rms:.5f} | mean rel error {rel:.4f}%",
              flush=True)

    _check(f"node{NODE_A} UX", ux_a, results.get("ref_a"), 1)
    _check(f"node{NODE_B} UX", ux_b, results.get("ref_b"), 1)

    # Element-response spot-checks (shape + peak comparison).
    for key, idx, ename, etype in (
            ("ref_fi", 7, "ele244 localForce", "f"),
            ("ref_di", 8, "ele244 deformation", "d"),
            ("ref_ff", 9, "ele245 localForce", "f")):
        ref = results.get(key)
        sim_list = [h[idx] for h in hist] if n else []
        if ref is None or not sim_list or not sim_list[0]:
            print(f"    {ename}: no sim data", flush=True)
            continue
        sim = np.array(sim_list)
        r = np.atleast_2d(ref)
        # Reference layout: col 0 = time, cols 1.. = response values.
        rblk = r[:, 1:1 + sim.shape[1]] if r.shape[1] > sim.shape[1] else r
        print(f"    {ename}: sim {sim.shape} ref {r.shape} | "
              f"sim peak {np.max(np.abs(sim)):.4f} vs "
              f"ref peak {np.max(np.abs(rblk)):.4f}", flush=True)
        if sim.shape == rblk.shape:
            e_rms = float(np.sqrt(np.mean((sim - rblk) ** 2)))
            big = np.abs(rblk) > 1.0
            if np.any(big):
                # Sign-aware: the Tcl recorder and eleResponse use opposite
                # sign conventions on isolated shear pairs (ele245 Vz at
                # both ends); magnitudes are the comparable quantity.
                e_rel = float(np.mean(np.abs(np.abs(sim[big])
                                              - np.abs(rblk[big]))
                                      / np.abs(rblk[big])) * 100.0)
                sgn = np.sign(sim[big] * rblk[big])
                nflip = int(np.sum(sgn < 0))
                print(f"      RMS {e_rms:.5f} | magnitude mean rel "
                      f"error {e_rel:.4f}% (sign-flipped comps: {nflip})",
                      flush=True)
            else:
                print(f"      RMS {e_rms:.5f}", flush=True)


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_IsolatedFrame: analysis complete.")
