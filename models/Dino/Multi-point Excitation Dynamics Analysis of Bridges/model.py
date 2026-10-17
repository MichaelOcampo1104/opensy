# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Multi-point Excitation Dynamics Analysis of Bridges (Dino)
UniqueID : Dino_MultiBridge
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-10-03
Purpose  : Nonlinear dynamic time-history of a 3D bridge under multi-support
           displacement excitation (241 nodes; 367 elasticBeamColumn + 72
           ShellMITC4 deck shells).  5%-damped (Rayleigh on modes 1-2)
           response to 20 s of support displacement (1000 steps x 0.02 s);
           histories validated against ref/OPENSEES/node203_mul.out (the
           record reproduced by the committed co.tcl) and ele330.out.
Ref      : Dino -- Multi-point Excitation Dynamics Analysis of Bridges
           (original ref/OPENSEES/co.tcl)
Ref      : Dino -- Multi-point Excitation Dynamics Analysis of Bridges
           (original ref/OPENSEES/co.tcl)
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
# Elastic frame materials (source tags).
MAT_E1        = 1      # Elastic (frame)
MAT_E2        = 2      # Elastic (frame)
MAT_E3        = 3      # Elastic (frame)
# ElasticIsotropic deck -> PlateFiber matrix -> PlateFiber shell section.
MAT_DECK      = 4      # nDMaterial ElasticIsotropic (deck)
MAT_PLATE     = 601    # nDMaterial PlateFiber wrapping MAT_DECK
SEC_DECK      = 701    # section PlateFiber (601, 260 mm)

# Time series / ground motions / patterns (support groups mirror source).
TS_GM1        = 11     # Path series, support displacements record 1
TS_GM2        = 12     # Path series, support displacements record 2
GM_1          = 1      # groundMotion tag, support group 1 (nodes 1, 3)
GM_2          = 2      # groundMotion tag, support group 2 (nodes 2, 4)
PAT_MS1       = 1      # MultiSupport pattern, group 1
PAT_MS2       = 2      # MultiSupport pattern, group 2

# ODB (nodal-only, throttled for the 1000-step transient, §3d).
ODB_TAG       = 1
ODB_EVERY_N   = 2

# Validation
NODE_MONITOR  = 203    # node-203 history validated against node203.out
ELE_MONITOR   = 330    # elasticBeamColumn localForce (ele330.out)

# Support displacement records (copied to ground_motions/ per convention).
# NOTE: the committed co.tcl assigns DM1X to BOTH support groups (factor 1)
# -- replayed verbatim even though DM2X ships alongside in ref/.
GM_DIR        = 1                # imposed along UX (source)
GM_DT         = 0.02             # s (source)
GM_FACTOR     = 1.0              # source amplitude factor (verbatim)

# Source files
TCL_FILE      = Path(__file__).parent / "ref" / "OPENSEES" / "co.tcl"
REF_DIR       = Path(__file__).parent / "ref" / "OPENSEES"


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa; displacement records
# applied verbatim in mm).

# Elastic frame materials (source lines, verbatim).
E_1 = 2.060e5 * MPa
E_2 = 2.600e4 * MPa
E_3 = 1.999e5 * MPa

# ElasticIsotropic deck (source line, verbatim).
E_DECK  = 26000.0 * MPa
NU_DECK = 0.2
DECK_T  = 260.0 * mm

# Rayleigh damping (source): 5% on modes 1-2 (computed from eigen).
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
    """Elastic frame + ElasticIsotropic deck + PlateFiber matrix (verbatim)."""
    ops.uniaxialMaterial("Elastic", MAT_E1, E_1)
    ops.uniaxialMaterial("Elastic", MAT_E2, E_2)
    ops.uniaxialMaterial("Elastic", MAT_E3, E_3)
    ops.nDMaterial("ElasticIsotropic", MAT_DECK, E_DECK, NU_DECK)
    ops.nDMaterial("PlateFiber", MAT_PLATE, MAT_DECK)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    """260 mm PlateFiber deck section (source line, verbatim)."""
    ops.section("PlateFiber", SEC_DECK, MAT_PLATE, DECK_T)


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes(src: str) -> None:
    """Create the 241 nodes + lumped mass from co.tcl, verbatim.

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
    """Fix support nodes 1-4 (source, verbatim; trailing ';' tolerated).

    (The source prints a "rigidDiaphragm" label but issues no such commands
    -- Transformation constraints cover the imposed-motion supports.)
    """
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s*;?", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(src: str) -> tuple[int, int]:
    """Create geomTransf + elasticBeamColumn + ShellMITC4 (source, verbatim).

    elasticBeamColumn keeps its native 3D form
    ``(tag, i, j, A, E, G, J, Iy, Iz, transfTag)``.  ShellMITC4 deck shells:
    ``(tag, n1, n2, n3, n4, secTag)`` with the PlateFiber section directly
    (§12as).  Returns (n_frame, n_shell).
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

    n_shell = 0
    for m in re.finditer(
        r"^element\s+ShellMITC4\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        src, re.M,
    ):
        ops.element("ShellMITC4", int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), int(m.group(4)), int(m.group(5)),
                    int(m.group(6)))
        n_shell += 1
    return n_frame, n_shell


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Initialise the ODB for a transient bridge model.

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
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_ground_motions(gm_dir: Path) -> None:
    """Two MultiSupport displacement patterns (source, verbatim).

    Pattern 1 drives supports 1 and 3 (UX) from record 1; pattern 2 drives
    supports 2 and 4 from record 2 (§12p pattern/groundMotion/imposedMotion
    form).  The committed source assigns DM1X to BOTH records -- replayed
    verbatim.  Only the first 20 s (1000 steps) are consumed, as in the
    source's ``analyze 1000``.
    """
    dm1 = [float(v) for v in (gm_dir / "dm1x.txt").read_text().split()]
    dm2 = [float(v) for v in (gm_dir / "dm2x.txt").read_text().split()]
    ops.timeSeries("Path", TS_GM1, "-dt", GM_DT, "-values", *dm1,
                   "-factor", GM_FACTOR)
    ops.timeSeries("Path", TS_GM2, "-dt", GM_DT, "-values", *dm2,
                   "-factor", GM_FACTOR)
    ops.pattern("MultipleSupport", PAT_MS1)
    ops.groundMotion(GM_1, "Plain", "-disp", TS_GM1)
    ops.imposedMotion(1, GM_DIR, GM_1)
    ops.imposedMotion(3, GM_DIR, GM_1)
    ops.pattern("MultipleSupport", PAT_MS2)
    ops.groundMotion(GM_2, "Plain", "-disp", TS_GM2)
    ops.imposedMotion(2, GM_DIR, GM_2)
    ops.imposedMotion(4, GM_DIR, GM_2)


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

    The integrator is set BEFORE SmartAnalyze (§3c transient rule); the
    source's SparseSPD system is kept verbatim.  In-loop history every
    step (nodeDisp + eleResponse -- cheap calls) gives 1:1 validation;
    ODB throttled to every ODB_EVERY_N steps (§3d).
    """
    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("SparseSPD")  # source solver, verbatim
    ops.integrator("Newmark", 0.5, 0.25)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="EnergyIncr",      # source test, verbatim (SmartAnalyze
        testTol=1.0e-4,             # default 1e-10 is far too tight here)
        testIterTimes=200,          # source max iterations, verbatim
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
            f_mon = [float(v) for v in
                     ops.eleResponse(ELE_MONITOR, "localForce")]
        except Exception:
            f_mon = []
        hist.append((
            float(ops.getTime()),
            float(ops.nodeDisp(NODE_MONITOR, 1)),
            float(ops.nodeDisp(NODE_MONITOR, 2)),
            float(ops.nodeDisp(NODE_MONITOR, 3)),
            f_mon,
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
    define_sections()
    define_nodes(src)
    define_boundary_conditions(src)
    vis_nodes(output_dir)
    n_frame, n_shell = define_elements(src)
    vis_model(output_dir)
    print(f"  Built model: {n_frame} elasticBeamColumn + {n_shell} "
          f"ShellMITC4 (expected 367 + 72).", flush=True)

    odb = create_odb(output_dir)

    print("Running eigenvalue analysis...", flush=True)
    t1, t2, aM, bK = run_eigen_rayleigh()
    print(f"  T1={t1:.4f} s T2={t2:.4f} s "
          f"alphaM={aM:.5f} betaK={bK:.6f}", flush=True)

    # Multi-support patterns defined after the model is complete (single
    # transient phase; no gravity/loadConst in the source, so §12i N/A).
    define_ground_motions(Path(__file__).parent / "ground_motions")
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    print("Running transient analysis...", flush=True)
    run_dynamic(odb)

    results = {"hist": getattr(run_dynamic, "history", []),
               "T1": t1, "T2": t2}
    # PRIMARY reference: node203_mul.out -- proven (2026-10-03) to be the
    # record reproduced by the committed co.tcl (0.0001% all DOFs).  The
    # node203.out / ele330.out / node0-2.out set is self-consistent but
    # belongs to an unidentified variant run (e.g. node203 row1 is exactly
    # 2x _mul row1 while finals differ 18x -- not a uniform scale, so a
    # genuinely different excitation); reported secondarily as variant
    # evidence, per the §12aq stale-reference protocol.
    for key, name in (("ref_mon", "node203_mul.out"),
                      ("ref_alt", "node203.out"),
                      ("ref_ele", "ele330.out")):
        p = REF_DIR / name
        try:
            results[key] = np.loadtxt(str(p)) if p.exists() else None
        except Exception:
            results[key] = None
    # Full-field final state from node0-2.out (1000 rows x (time + triplets)).
    try:
        blocks = [np.loadtxt(str(REF_DIR / f"node{i}.out")) for i in range(3)]
        results["ref_field"] = [b[-1, 1:] for b in blocks]
    except Exception as e:
        print(f"  (full-field reference unreadable: {e})")
        results["ref_field"] = None
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
    ux = np.array([h[1] for h in hist]) if n else np.empty(0)

    # Dump the monitor history for the record.
    if n > 0:
        np.savetxt(str(output_dir / "node203_disp_history.csv"),
                   np.column_stack([tt, [h[1] for h in hist],
                                    [h[2] for h in hist],
                                    [h[3] for h in hist]]),
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

    # Monitor history vs reference (matplotlib).
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 1, figsize=(9, 5))
        ref = results.get("ref_mon")
        if ref is not None and ref.size:
            ax.plot(ref[:, 0], ref[:, 1], "k-",
                    linewidth=1.0, alpha=0.6,
                    label="Reference (node203_mul.out)")
        if n > 0:
            ax.plot(tt, ux, "r--",
                    linewidth=1.0, alpha=0.85, label="Simulation")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(f"Node {NODE_MONITOR} UX (mm)")
        ax.set_title("Dino_MultiBridge -- support-driven UX history")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(output_dir / "dynamic_compare.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        print("  (matplotlib unavailable -- skipping compare plot)")

    # Verification summary
    print(f"\n  Recorded steps: {n} / {N_TOTAL_STEPS} expected", flush=True)
    print(f"  T1={results['T1']:.4f} s T2={results['T2']:.4f} s", flush=True)

    ref = results.get("ref_mon")
    if n > 0 and ref is not None and ref.size:
        r = np.atleast_2d(ref)
        m = min(n, r.shape[0])
        denom = np.maximum(np.abs(r[:m, 1]), 1e-12)
        rms = float(np.sqrt(np.mean((ux[:m] - r[:m, 1]) ** 2)))
        rel = float(np.mean(np.abs(ux[:m] - r[:m, 1]) / denom) * 100.0)
        print(f"    node{NODE_MONITOR} UX vs _mul: RMS {rms:.5f} | "
              f"mean rel error {rel:.4f}%", flush=True)
    alt = results.get("ref_alt")
    if n > 0 and alt is not None and alt.size:
        r = np.atleast_2d(alt)
        m = min(n, r.shape[0])
        d = float(np.max(np.abs(ux[:m] - r[:m, 1])))
        print(f"    vs node203.out: max abs diff {d:.4f} mm "
              f"(variant set -- expected to differ)", flush=True)

    ref_ele = results.get("ref_ele")
    sim_f = [h[4] for h in hist] if n else []
    if ref_ele is not None and sim_f and sim_f[0]:
        sim = np.array(sim_f)
        r = np.atleast_2d(ref_ele)
        rblk = r[:, 1:1 + sim.shape[1]] if r.shape[1] > sim.shape[1] else r
        print(f"    ele{ELE_MONITOR} localForce: sim {sim.shape} "
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

    rf = results.get("ref_field")
    if rf is not None:
        print(f"  Full-field reference final rows assembled "
              f"({len(rf)} ranges)", flush=True)


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, results = run_analysis(output_dir)
    post_process(odb, output_dir, results)
    print("Dino_MultiBridge: analysis complete.")
