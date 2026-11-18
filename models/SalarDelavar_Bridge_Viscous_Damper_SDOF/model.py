# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Bridge substructure with viscous dampers: free vibration of two lumped
           masses (substructure Ms and deck Mb) after a static deck displacement
UniqueID : SalarDelavar_Bridge_Viscous_Damper_SDOF
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-18
Purpose  : Ground-fixed chain of zeroLength springs and linear viscous dampers. The deck is
           displaced 0.3 mm by a static step and released; the free decay over 10 s
           (dt = 0.01 s) is integrated with Newmark average acceleration through SmartAnalyze.
Ref      : py_ref/BRIDGE_VISCOUS_DAMPER_SDOF.py (source), py_ref/ANALYSIS_FUNCTION.py (source retry
           ladder, replaced by SmartAnalyze), py_ref/BRIDGE_VISCOUS_DAMPER_SDOF.png (reference
           figure), py_ref/README.md. Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/BRIDGE_VISCOUS_DAMPER_SDOF
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops
import opstool as opst

# models/<UniqueID>/model.py -> repository root is parents[2]
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *  # noqa: E402,F403  (N, mm, sec, m)
from vis_utils import (  # noqa: E402
    vis_curves,
    vis_loads,
    vis_model,
    vis_nodes,
    vis_pre_analysis,
)
from plot_utils import COLORS, _style_ax  # noqa: E402

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
ODB_TAG = 1
NODE_GROUND = 1      # fixed end of ks and Cs (display x = 0 mm)
NODE_MS = 2          # substructure mass Ms (display x = 1000 mm)
NODE_MB = 3          # deck mass Mb (display x = 2000 mm); initial displacement and output node
ELE_KS = 1           # zeroLength: ground - Ms, spring ks
ELE_CS = 2           # zeroLength: ground - Ms, viscous damper Cs
ELE_KB = 3           # zeroLength: Ms - Mb, bearing spring kb
ELE_CB = 4           # zeroLength: Ms - Mb, bearing viscous damper Cb
ELE_CD = 5           # zeroLength: Ms - Mb, viscous damper Cd
MAT_KS = 1
MAT_CS = 2
MAT_KB = 3
MAT_CB = 4
MAT_CD = 5
TS_INIT = 1          # unit load at Mb that drives the static DisplacementControl step
PAT_INIT = 1

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# The source labels the masses in kg, but its numbers reach OpenSees as N.s^2/mm
# (1 N.s^2/mm = 1000 kg). The values are kept as written (README, LESSONS 41).
mass_unit = N * sec**2 / mm          # 1 N.s^2/mm
mass_ms = 1000.0 * mass_unit         # source Ms = 1000 (labelled kg)
mass_mb = 500.0 * mass_unit          # source Mb = 500 (labelled kg)
k_s = 1.0e6 * N / mm                 # substructure spring ks (source 1e6, N/mm)
c_s = 1.0e4 * N * sec / mm           # damper Cs (source 1e4, N.s/mm)
k_b = 5.0e5 * N / mm                 # bearing spring kb (source comment says N/m; the value is used as N/mm)
c_b = 5.0e3 * N * sec / mm           # bearing damper Cb (source 5e3, N.s/mm)
c_d = 15.0e3 * N * sec / mm          # viscous damper Cd (source 15e3, N.s/mm)
viscous_alpha = 1.0                  # velocity exponent of the Viscous dampers (linear)
dr = 0.02                            # Rayleigh damping ratio (source DR)
link_rayleigh = False                # False = as written. True adds -doRayleigh to the two springs (not in the source; LESSONS 43)
u0 = 0.3 * mm                        # initial deck displacement (source u0)
duration = 10.0 * sec                # analysis length (source)
dt = 0.01 * sec                      # time step (source)
n_steps = int(round(duration / dt))  # 1000 transient steps
max_iter = 1000000                   # convergence iterations (source)
max_tol = 1.0e-10                    # convergence tolerance, NormDispIncr (source)
newmark_gamma = 0.5                  # average acceleration (source Newmark 0.5, 0.25)
newmark_beta = 0.25
odb_every_n = 10                     # ODB throttle for > 500 transient steps (AGENT.md §3d)
node_x = {NODE_GROUND: 0.0 * mm, NODE_MS: 1000.0 * mm, NODE_MB: 2000.0 * mm}   # display only, see define_nodes
# Peaks printed in the source figure (reference only; the model is not tuned to them).
figure_peaks = {
    "u_mb_mm": 0.09861536219210028 * mm,
    "v_mb_mm_s": 1.385535274477327 * mm / sec,
    "a_mb_mm_s2": 55.385512315988926 * mm / sec**2,
    "base_N": 7280.9519022762515 * N,
}

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Start a fresh 2D model with two DOFs per node. The y DOF is restrained everywhere, so the motion is along x.

    The model is 2D only because opstool cannot draw one-component nodal loads (ndm = 1 raises
    IndexError in its load extraction, LESSONS 44). The restrained y DOF leaves the equations unchanged.
    """
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 2)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Linear springs (ks, kb) and linear viscous dampers (Cs, Cb, Cd)."""
    ops.uniaxialMaterial("Elastic", MAT_KS, k_s)
    ops.uniaxialMaterial("Elastic", MAT_KB, k_b)
    ops.uniaxialMaterial("Viscous", MAT_CS, c_s, viscous_alpha)
    ops.uniaxialMaterial("Viscous", MAT_CB, c_b, viscous_alpha)
    ops.uniaxialMaterial("Viscous", MAT_CD, c_d, viscous_alpha)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    """No sections: every element is a zeroLength spring or damper."""
    pass

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    """Three nodes on the x axis (y = 0) with lumped masses in x.

    The source puts all three nodes at x = 0. Here they are spread along x so that the plots show
    the chain. Each zeroLength element then has a nonzero length, and OpenSees prints one warning per
    element. The response is the same as the source's, which the validation in post-processing checks.
    """
    for tag, x in node_x.items():
        ops.node(tag, x, 0.0)
    ops.mass(NODE_MS, mass_ms, 0.0)
    ops.mass(NODE_MB, mass_mb, 0.0)

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    """Ground node fixed in x and y; the two mass nodes restrained in y only."""
    ops.fix(NODE_GROUND, 1, 1)
    ops.fix(NODE_MS, 0, 1)
    ops.fix(NODE_MB, 0, 1)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Five zeroLength elements: ks and Cs from ground to Ms; kb, Cb and Cd from Ms to Mb.

    OpenSees applies the Rayleigh stiffness term (betaK) to a zeroLength element only with
    -doRayleigh. The source does not pass it, so its a1 has no effect (LESSONS 43). With
    link_rayleigh = True the flag is added to the two springs, which carry all the stiffness.
    """
    spring_opts = ["-doRayleigh"] if link_rayleigh else []
    ops.element("zeroLength", ELE_KS, NODE_GROUND, NODE_MS, "-mat", MAT_KS, "-dir", 1, *spring_opts)
    ops.element("zeroLength", ELE_CS, NODE_GROUND, NODE_MS, "-mat", MAT_CS, "-dir", 1)
    ops.element("zeroLength", ELE_KB, NODE_MS, NODE_MB, "-mat", MAT_KB, "-dir", 1, *spring_opts)
    ops.element("zeroLength", ELE_CB, NODE_MS, NODE_MB, "-mat", MAT_CB, "-dir", 1)
    ops.element("zeroLength", ELE_CD, NODE_MS, NODE_MB, "-mat", MAT_CD, "-dir", 1)

# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb() -> "opst.post.CreateODB":
    """Nodal and zeroLength (link) responses. The per-step time histories are also read in run_free_vibration.

    Returns:
        The CreateODB instance; save_model_data() has been called.
    """
    odb = opst.post.CreateODB(
        odb_tag=ODB_TAG,
        model_update=False,
        save_nodal_resp=True,
        save_link_resp=True,
        link_tags=[ELE_KS, ELE_CS, ELE_KB, ELE_CB, ELE_CD],
    )
    odb.save_model_data()
    return odb

# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_initial_load() -> None:
    """Unit load at Mb (1 N). Under DisplacementControl its factor follows from u0; the pattern is removed after the static step."""
    ops.timeSeries("Linear", TS_INIT)
    ops.pattern("Plain", PAT_INIT, TS_INIT)
    ops.load(NODE_MB, 1.0 * N, 0.0)

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_initial_displacement(odb: "opst.post.CreateODB") -> dict:
    """Static DisplacementControl step that moves the deck to u0 (source: one analyze(1) step of 0.3 mm).

    Args:
        odb: Active CreateODB instance; fetch_response_step() is called after each converged step.

    Returns:
        Node displacements after the step: keys u_ms and u_mb (mm).
    """
    ops.constraints("Plain")                     # handlers set before SmartAnalyze (AGENT.md §12w)
    ops.numberer("Plain")
    ops.system("BandGeneral")
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        testType="NormDispIncr",
        testTol=max_tol,
        testIterTimes=max_iter,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 40, 20, 30],              # Newton first, as in the source
        printPer=0,
        testPrintFlag=0,
    )
    segs = analysis.static_split([u0], maxStep=u0)   # one segment of u0
    for seg in segs:
        ok = analysis.StaticAnalyze(node=NODE_MB, dof=1, seg=seg)
        if ok < 0:
            break
        odb.fetch_response_step()
    analysis.close()
    static = {"u_ms": ops.nodeDisp(NODE_MS, 1), "u_mb": ops.nodeDisp(NODE_MB, 1)}
    ops.setTime(0.0)
    ops.wipeAnalysis()
    ops.remove("loadPattern", PAT_INIT)          # release the deck: free vibration from here
    return static

def run_free_vibration(odb: "opst.post.CreateODB") -> tuple:
    """Rayleigh damping from the first eigenvalue, then Newmark average acceleration through SmartAnalyze.

    Args:
        odb: Active CreateODB instance; fetch_response_step() is called every odb_every_n steps.

    Returns:
        (history, info). history holds one value per step (time, u_ms, v_ms, u_mb, v_mb, a_mb,
        spring_force, base_reaction). info holds omega_1 and the Rayleigh coefficients.
    """
    ops.constraints("Plain")                     # handlers re-set after wipeAnalysis (AGENT.md §12w, LESSON 40)
    ops.numberer("Plain")
    ops.system("BandGeneral")
    lam = ops.eigen("-fullGenLapack", 1)         # mode-1 eigenvalue of the undamped system
    omega_1 = float(np.sqrt(max(lam)))
    # Source formulas, kept as written. The omega_1 factors cancel in a0, so a0 = 2*dr (LESSON 42).
    a0 = (2.0 * omega_1 * dr) / omega_1          # mass-proportional coefficient
    a1 = (dr * 2.0) / omega_1                    # stiffness-proportional coefficient
    ops.rayleigh(a0, a1, 0.0, 0.0)
    ops.integrator("Newmark", newmark_gamma, newmark_beta)   # set before SmartAnalyze
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        testType="NormDispIncr",
        testTol=max_tol,
        testIterTimes=max_iter,
        tryAlterAlgoTypes=True,
        algoTypes=[10, 40, 20, 30, 50],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6 * sec,
        printPer=0,
        testPrintFlag=0,
    )
    rows = []
    segs = analysis.transient_split(n_steps)
    for step in segs:
        ok = analysis.TransientAnalyze(dt)
        if ok < 0:
            break
        if step % odb_every_n == 0:
            odb.fetch_response_step()
        rows.append([
            ops.getTime(),
            ops.nodeDisp(NODE_MS, 1), ops.nodeVel(NODE_MS, 1),
            ops.nodeDisp(NODE_MB, 1), ops.nodeVel(NODE_MB, 1), ops.nodeAccel(NODE_MB, 1),
            -ops.eleResponse(ELE_KS, "force")[0],    # spring force (source base_reactionW)
            -ops.eleResponse(ELE_CS, "force")[0],    # base reaction (source base_reaction)
        ])
    analysis.close()
    table = np.array(rows, dtype=float)
    history = {
        "time": table[:, 0],
        "u_ms": table[:, 1], "v_ms": table[:, 2],
        "u_mb": table[:, 3], "v_mb": table[:, 4], "a_mb": table[:, 5],
        "spring_force": table[:, 6], "base_reaction": table[:, 7],
    }
    info = {"omega_1": omega_1, "a0": a0, "a1": a1}
    return history, info

def run_analysis(output_dir: Path) -> tuple:
    """Build the model, run the static deck displacement and the free vibration.

    Returns:
        (odb, history, info): the populated CreateODB, the per-step histories and the run summary.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))         # must precede CreateODB (AGENT.md §12ac)
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)                           # V1
    define_elements()
    vis_model(output_dir)                           # V2
    odb = create_odb()
    define_initial_load()
    vis_loads(output_dir)                           # V3
    vis_pre_analysis(output_dir)                    # V4
    static = run_initial_displacement(odb)
    history, info = run_free_vibration(odb)
    info.update(static)
    return odb, history, info

# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def reference_matrices(a0: float, a1: float) -> tuple:
    """Mass, stiffness and total damping matrices of the chain, rebuilt in numpy (valid for viscous_alpha = 1).

    The damping is the dashpots plus a0*M. The a1*K term is added only when link_rayleigh is True,
    because OpenSees ignores it on zeroLength elements otherwise (LESSONS 43).

    Args:
        a0: Rayleigh mass-proportional coefficient used in the run.
        a1: Rayleigh stiffness-proportional coefficient used in the run.

    Returns:
        (mass, stiff, damp) for the DOFs (u_ms, u_mb), in N, mm, s units.
    """
    mass = np.diag([mass_ms, mass_mb])
    stiff = np.array([[k_s + k_b, -k_b], [-k_b, k_b]])
    dashpots = np.array([[c_s + c_b + c_d, -(c_b + c_d)], [-(c_b + c_d), c_b + c_d]])
    damp = dashpots + a0 * mass
    if link_rayleigh:
        damp = damp + a1 * stiff
    return mass, stiff, damp

def newmark_replica(mass, stiff, damp, u_start, a_start, dt_s, steps, gamma, beta) -> np.ndarray:
    """Average-acceleration Newmark for free vibration, written out in numpy.

    The motion starts at rest. a_start=None gives zero initial acceleration, as OpenSees does after
    the static step.

    Returns:
        Rows of [u_ms, u_mb, v_ms, v_mb, a_ms, a_mb], one per step.
    """
    u = np.asarray(u_start, dtype=float)
    v = np.zeros(2)
    a = np.zeros(2) if a_start is None else np.asarray(a_start, dtype=float)
    eff = mass + gamma * dt_s * damp + beta * dt_s**2 * stiff
    out = np.empty((steps, 6))
    for k in range(steps):
        u_pred = u + dt_s * v + dt_s**2 * (0.5 - beta) * a
        v_pred = v + dt_s * (1.0 - gamma) * a
        a = np.linalg.solve(eff, -(damp @ v_pred + stiff @ u_pred))
        u = u_pred + beta * dt_s**2 * a
        v = v_pred + gamma * dt_s * a
        out[k] = [u[0], u[1], v[0], v[1], a[0], a[1]]
    return out

def exact_free_response(mass, stiff, damp, u_start, times) -> np.ndarray:
    """Continuous free vibration from rest, from the eigen-decomposition of the first-order system.

    Returns:
        Rows of [u_ms, u_mb, v_ms, v_mb], one per time in ``times``.
    """
    minv = np.linalg.inv(mass)
    state = np.block([[np.zeros((2, 2)), np.eye(2)], [-minv @ stiff, -minv @ damp]])
    x0 = np.concatenate([np.asarray(u_start, dtype=float), np.zeros(2)]).astype(complex)
    lam, vec = np.linalg.eig(state)
    coef = np.linalg.solve(vec, x0)
    return np.array([np.real(vec @ (coef * np.exp(lam * t))) for t in times])

def save_history(history: dict, output_dir: Path) -> None:
    """Write the per-step time history to CSV (N, mm, s)."""
    columns = ["time", "u_ms", "v_ms", "u_mb", "v_mb", "a_mb", "spring_force", "base_reaction"]
    table = np.column_stack([history[name] for name in columns])
    np.savetxt(
        output_dir / "time_history.csv", table, delimiter=",",
        header="time_s,u_ms_mm,v_ms_mm_s,u_mb_mm,v_mb_mm_s,a_mb_mm_s2,spring_force_N,base_reaction_N",
        comments="",
    )

def plot_time_history(history: dict, output_dir: Path) -> None:
    """Four time-history panels in the source's style: response (blue) and running max |value| (red)."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), dpi=150)
    panels = [
        ("u_mb", "Displacement of Mb (mm)", "Time vs displacement"),
        ("v_mb", "Velocity of Mb (mm/s)", "Time vs velocity"),
        ("a_mb", "Acceleration of Mb (mm/s^2)", "Time vs acceleration"),
        ("base_reaction", "Base reaction (N)", "Time vs base reaction"),
    ]
    for ax, (key, ylabel, title) in zip(axes.ravel(), panels):
        y = history[key]
        ax.plot(history["time"], y, color=COLORS["primary"], lw=1.6)
        ax.plot(history["time"], np.maximum.accumulate(np.abs(y)), color=COLORS["secondary"], lw=1.6)
        _style_ax(ax, "Time (s)", ylabel, f"{title} (max |.| = {np.max(np.abs(y)):.4g})")
    fig.tight_layout()
    fig.savefig(output_dir / "time_history.png")
    plt.close(fig)

def plot_hysteresis(history: dict, output_dir: Path) -> None:
    """Base reaction against the deck displacement (the source's spiral plot)."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 5.5), dpi=150)
    ax.plot(history["u_mb"], history["base_reaction"], color=COLORS["primary"], lw=1.8)
    _style_ax(ax, "Displacement of Mb (mm)", "Base reaction (N)", "Base reaction vs displacement")
    fig.tight_layout()
    fig.savefig(output_dir / "hysteresis.png")
    plt.close(fig)

def validate(history: dict, info: dict, output_dir: Path) -> None:
    """Compare the OpenSees run with independent numpy calculations and write validation.txt.

    The source figure's peaks are printed beside the model's peaks. They are not matched; the
    model is not tuned to the figure.
    """
    mass, stiff, damp = reference_matrices(info["a0"], info["a1"])
    u_start = np.array([info["u_ms"], info["u_mb"]])
    omega = np.sqrt(np.sort(np.linalg.eigvals(np.linalg.solve(mass, stiff)).real))
    times = dt * np.arange(1, n_steps + 1)
    report = []

    report.append(f"omega_1: OpenSees {info['omega_1']:.6f}, analytic {omega[0]:.6f} rad/s")
    report.append(f"T_1 = 2*pi/omega_1 = {2 * np.pi / omega[0]:.5f} s; source PERIOD = pi/omega_1 = {np.pi / omega[0]:.5f} s (half of T_1)")
    xi_mass = [info["a0"] / (2 * w) for w in omega]
    xi_stiff = [info["a1"] * w / 2 for w in omega]
    report.append(f"link_rayleigh = {link_rayleigh}")
    report.append(f"Rayleigh mass term a0*M (active): modal xi_1 = {xi_mass[0]:.5f}, xi_2 = {xi_mass[1]:.5f}")
    report.append("Rayleigh stiffness term a1*K ("
                  + ("active" if link_rayleigh else "inactive: zeroLength ignores it without -doRayleigh")
                  + f"): modal xi_1 = {xi_stiff[0]:.5f}, xi_2 = {xi_stiff[1]:.5f}")
    minv = np.linalg.inv(mass)
    state = np.block([[np.zeros((2, 2)), np.eye(2)], [-minv @ stiff, -minv @ damp]])
    for i, s in enumerate(sorted([e for e in np.linalg.eigvals(state) if e.imag > 0], key=abs), 1):
        report.append(f"full system mode {i}: omega = {abs(s):.4f} rad/s, damped omega_d = {s.imag:.4f} rad/s, xi = {-s.real / abs(s):.5f}")

    u_ms_an = u0 * k_b / (k_s + k_b)
    report.append(f"static: u_ms OpenSees {info['u_ms']:.6f}, analytic {u_ms_an:.6f} mm; "
                  f"u_mb OpenSees {info['u_mb']:.6f}, analytic {u0:.6f} mm")

    rep = newmark_replica(mass, stiff, damp, u_start, None, dt, n_steps, newmark_gamma, newmark_beta)
    report.append(
        "Newmark replica (zero start) vs OpenSees, max abs difference: "
        f"u_mb {np.max(np.abs(rep[:, 1] - history['u_mb'])):.2e} mm, "
        f"v_mb {np.max(np.abs(rep[:, 3] - history['v_mb'])):.2e} mm/s, "
        f"a_mb {np.max(np.abs(rep[:, 5] - history['a_mb'])):.2e} mm/s^2"
    )

    exact = exact_free_response(mass, stiff, damp, u_start, times)
    diff = np.abs(exact[:, 1] - history["u_mb"])
    k_max = int(np.argmax(diff))
    a_consistent = -np.linalg.solve(mass, stiff @ u_start)
    rep_c = newmark_replica(mass, stiff, damp, u_start, a_consistent, dt, n_steps, newmark_gamma, newmark_beta)
    report.append(f"exact continuous solution vs OpenSees: max |u_mb difference| {diff[k_max]:.4f} mm at t = {times[k_max]:.2f} s")
    report.append("Newmark with a consistent start acceleration vs exact: "
                  f"max |u_mb difference| {np.max(np.abs(rep_c[:, 1] - exact[:, 1])):.4f} mm")

    cs_force = c_s * history["v_ms"]
    report.append("base reaction vs +Cs*v_ms: max |difference| "
                  f"{np.max(np.abs(history['base_reaction'] - cs_force)):.3e} N "
                  f"(vs -Cs*v_ms: {np.max(np.abs(history['base_reaction'] + cs_force)):.3e} N)")
    spring_ref = k_s * history["u_ms"]
    report.append("spring force vs +ks*u_ms: max |difference| "
                  f"{np.max(np.abs(history['spring_force'] - spring_ref)):.3e} N")

    model_peaks = {
        "u_mb_mm": np.max(np.abs(history["u_mb"])),
        "v_mb_mm_s": np.max(np.abs(history["v_mb"])),
        "a_mb_mm_s2": np.max(np.abs(history["a_mb"])),
        "base_N": np.max(np.abs(history["base_reaction"])),
    }
    u_alt = [0.1 * mm * k_b / (k_s + k_b), 0.1 * mm]
    alt = newmark_replica(mass, stiff, damp, u_alt, None, dt, n_steps, newmark_gamma, newmark_beta)
    alt_peaks = {"u_mb_mm": np.max(np.abs(alt[:, 1])), "v_mb_mm_s": np.max(np.abs(alt[:, 3])),
                 "a_mb_mm_s2": np.max(np.abs(alt[:, 5])), "base_N": np.max(np.abs(c_s * alt[:, 2]))}
    for key in model_peaks:
        report.append(f"peak {key}: figure {figure_peaks[key]:.6g} | model (u0 = 0.3 mm) {model_peaks[key]:.6g} "
                      f"| replica u0 = 0.1 mm {alt_peaks[key]:.6g}")

    (output_dir / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report:
        print(line)

def post_process(odb: "opst.post.CreateODB", output_dir: Path, history: dict, info: dict) -> None:
    """Flush the ODB, write the history and plots, run the checks, and write the interactive views."""
    odb.save_response()
    save_history(history, output_dir)
    plot_time_history(history, output_dir)
    plot_hysteresis(history, output_dir)
    validate(history, info, output_dir)
    t = history["time"]
    vis_curves(output_dir, [
        {"x": t, "y": history["u_mb"], "xlabel": "Time (s)", "ylabel": "Displacement of Mb (mm)", "title": "Displacement"},
        {"x": t, "y": history["v_mb"], "xlabel": "Time (s)", "ylabel": "Velocity of Mb (mm/s)", "title": "Velocity"},
        {"x": t, "y": history["a_mb"], "xlabel": "Time (s)", "ylabel": "Acceleration of Mb (mm/s^2)", "title": "Acceleration"},
        {"x": t, "y": history["base_reaction"], "xlabel": "Time (s)", "ylabel": "Base reaction (N)", "title": "Base reaction"},
    ], filename="vis_08_time_history.html", title="Free vibration: time histories")
    vis_curves(output_dir, [
        {"x": history["u_mb"], "y": history["base_reaction"], "xlabel": "Displacement of Mb (mm)",
         "ylabel": "Base reaction (N)", "title": "Base reaction vs displacement"},
    ], filename="vis_09_hysteresis.html", title="Base reaction vs displacement")

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb, history, info = run_analysis(output_dir)
    print(f"omega_1 = {info['omega_1']:.4f} rad/s, T_1 = {2 * np.pi / info['omega_1']:.4f} s")
    print(f"static: u_ms = {info['u_ms']:.4f} mm, u_mb = {info['u_mb']:.4f} mm")
    print(f"transient steps = {len(history['time'])}, end time = {history['time'][-1]:.2f} s")
    post_process(odb, output_dir, history, info)
