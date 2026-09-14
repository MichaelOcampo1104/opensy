# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Elastic-Plastic Pushover of a 3D RC Moment Frame — concentrated
           (beamWithHinges) vs distributed (nonlinearBeamColumn) plasticity
UniqueID : Dino_PlasticHinge
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-14
Purpose  : Compare two fibre-section plasticity formulations of the same RC
           space frame under a displacement-controlled lateral pushover,
           validating each against the original Tcl reference (node2.out).
Ref      : Dino -- Elastic-Plastic Analysis of Plastic Hinge Fiber Element
           (original tcl_ref/co.tcl = beamWithHinges, co2.tcl = nonlinearBeamColumn)
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
# Materials (match source co.tcl tags exactly).
# NOTE -- the source defines three materials: Steel01 1, Concrete02 2, Elastic 3.
# Material 3 (Elastic, E=1.999e5) is DEAD -- never bound to any section/element
# (co2.tcl's nonlinearBeamColumn references section 1/2, which only use mats 1
# and 2) -- so it is omitted here per §12ap-6 (dead materials dropped).
MAT_STEEL     = 1      # Steel01  fy=300 MPa, E=206000 MPa, b=0.01
MAT_CONCRETE  = 2      # Concrete02  fc=20 MPa core/cover

# Sections (fibre) -- HC500x500 columns (sec 1) and HB300x600 beams (sec 2).
SEC_COL = 1            # ##HC500X500  (500x500, 25 concrete fibres + 20 steel)
SEC_BEAM = 2           # ##HB300X600  (300x600)

# Geometric transformations (1..52, one per element in the source).  Columns
# (tag 1..6, 14..19, 27..32, 40..45) use vecxz=(1,0,0); beams (the rest) use
# (0,0,1).  Parsed verbatim.

# Time series / pattern
TS_LATERAL  = 1
PAT_LATERAL = 1

# ODB
ODB_TAG_HINGE  = 1     # beamWithHinges variant
ODB_TAG_FIBER  = 2     # nonlinearBeamColumn variant

# Source files
TCL_HINGE = Path(__file__).parent / "tcl_ref" / "co.tcl"     # beamWithHinges
TCL_FIBER = Path(__file__).parent / "tcl_ref" / "co2.tcl"    # nonlinearBeamColumn
REF_FILE  = Path(__file__).parent / "tcl_ref" / "node2.out"  # 100-step pushover

# Control node / DOF for displacement-controlled pushover
NODE_CTRL = 2          # node 2 (0,0,12000) -- roof corner on the X=0 plane
DOF_CTRL  = 1          # UX (lateral)
N_STEPS   = 100        # source: analyze 100
D_INCR    = 1.0 * mm   # source: DisplacementControl 2 1 1.000E+000 (1 mm/step)


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is already N-mm-MPa (coords in mm, E in MPa, forces in N).  No unit
# conversion needed -- the dimensional suffixes below are documentation only.

# Geometry -- 3D RC moment frame: 2 bays x 2 bays in plan (6 m bay), 4 stories
# (3 m story).  30 nodes parsed verbatim from co.tcl (lines 5-34).
BAY   = 6000.0 * mm
STORY = 3000.0 * mm

# Materials (source line 76-77)
FY_STEEL  = 300.0 * MPa
E_STEEL   = 206000.0 * MPa
B_STEEL   = 0.01              # Steel01 post-yield stiffness ratio
FC_CONC   = 20.0 * MPa        # Concrete02 compressive strength (negative sign
                              # applied at the material call)

# Hinge length (source element lines, e.g. "... 1 500 1 500 ...")
LP_COL = 500.0 * mm           # column hinge region (sec 1)
LP_BEAM = 600.0 * mm          # beam hinge region (sec 2)

# Elastic-interior section properties (source element lines, the 6 values
# between lpJ and transfTag).  These are the gross-section axial/bending/
# torsion stiffnesses of the elastic (non-hinge) middle of beamWithHinges.
# HC500x500 columns:
E_ELAST  = 2.000e4 * MPa              # E  (≈ concrete E, source)
A_COL    = 2.500e5 * mm**2            # A
IZ_COL   = 5.208e9 * mm**4            # Iz (strong axis)
IY_COL   = 5.208e9 * mm**4            # Iy
G_COL    = 8.333e3 * MPa              # G  (= E/2.4, ν≈0.2)
GJ_COL   = 8.802e9 * N * mm**2        # torsion  (rect-section J)
# HB300x600 beams:
A_BEAM   = 1.800e5 * mm**2
IZ_BEAM  = 1.350e9 * mm**4            # Iz (note: beam's weak axis for gravity)
IY_BEAM  = 5.400e9 * mm**4
GJ_BEAM  = 3.708e9 * N * mm**2

# 3D fibre-section torsion stiffness (§12au): the source Tcl omits -GJ from
# the section and only warns; OpenSeesPy ERRORS.  Use the same GJ as the
# elastic interior so the section is consistent.
GJ_SEC_COL  = GJ_COL
GJ_SEC_BEAM = GJ_BEAM

# nonlinearBeamColumn integration points (source: "... 3 1 1" -> nIP=3, sec, transf)
N_IP = 3

# Lateral load pattern -- inverted triangle on UX (source lines 290-297).
# Nodes 2,4 (roof edge), 1,3,13,14,19,20.  Recorder -time = load factor λ,
# so base shear = λ × ΣP.
LATERAL_LOADS = [
    (2,  4.0e5 * N),
    (4,  4.0e5 * N),
    (1,  3.0e5 * N),
    (3,  3.0e5 * N),
    (13, 2.0e5 * N),
    (14, 2.0e5 * N),
    (19, 1.0e5 * N),
    (20, 1.0e5 * N),
]
P_LATERAL_TOTAL = sum(p for _, p in LATERAL_LOADS)   # 2.2e6 N

# Element-type variants built by this script.  Each is a full build + pushover
# against the SAME reference curve, so the two plasticity formulations are
# directly comparable.
ELEMENT_TYPES = ["hinge", "fiber"]


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model (ndm=3, ndf=6)."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Steel01 rebar + Concrete02 concrete (source lines 76-77).

    Steel01 takes (tag, fy, E0, b) -- all positive; the sign is handled
    internally.  Concrete02 takes (tag, fpc, epsc0, fpcu, epsU, lambda, ft,
    Ets) with fpc NEGATIVE (compression convention).
    """
    ops.uniaxialMaterial("Steel01", MAT_STEEL, FY_STEEL, E_STEEL, B_STEEL)
    ops.uniaxialMaterial("Concrete02", MAT_CONCRETE,
                         -FC_CONC, -0.002, -5.0, -0.0033, 0.1, 2.2, 1100.0)


# ── 6. SECTIONS (fibre) ──────────────────────────────────────────────────────
def _build_fiber_section(sec_tag: int, gj: float) -> None:
    """Build a fibre section by VERBATIM REPLAY of the source's fibres.

    The source sections (##HC500X500 / ##HB300X600) list discrete fibres as
    "fiber y z A matTag" -- a hand-meshed core + corner rebar layout.  Re-
    meshing risks A/I drift (§12aq), so each fibre is emitted verbatim.  A
    3D fibre section REQUIRES -GJ in OpenSeesPy (§12au); the source Tcl omits
    it and only warns.
    """
    ops.section("Fiber", sec_tag, "-GJ", gj)
    src = TCL_HINGE.read_text()
    # find the "##" header for this section, then its "section Fiber <tag> { ... }"
    m = re.search(rf"section\s+Fiber\s+{sec_tag}\s*\{{(.*?)\}}", src, re.S)
    if m is None:
        raise RuntimeError(f"section Fiber {sec_tag} block not found in source")
    for fm in re.finditer(
        r"fiber\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+(\d+)", m.group(1)
    ):
        y, z, area, mat = (float(fm.group(1)), float(fm.group(2)),
                           float(fm.group(3)), int(fm.group(4)))
        ops.fiber(y, z, area, mat)


def define_sections() -> None:
    """HC500x500 column + HB300x600 beam fibre sections (verbatim fibres)."""
    _build_fiber_section(SEC_COL, GJ_SEC_COL)
    _build_fiber_section(SEC_BEAM, GJ_SEC_BEAM)


# ── 7. NODES / MASS ──────────────────────────────────────────────────────────
def define_nodes_mass(src: str) -> None:
    """Create the 30 nodes + lumped mass from co.tcl (lines 5-66), verbatim.

    Mass is applied on UX and UY only (zero on UZ/rotations) -- a lumped
    lateral-mass model.  Mass is irrelevant to this static pushover but is
    preserved for fidelity to the source.
    """
    for m in re.finditer(
        r"^node\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.node(int(m.group(1)),
                 float(m.group(2)), float(m.group(3)), float(m.group(4)))
    for m in re.finditer(
        r"^mass\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", src, re.M
    ):
        ops.mass(int(m.group(1)), float(m.group(2)), float(m.group(3)),
                 0.0, 0.0, 0.0, 0.0)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(src: str) -> None:
    """Fully fix the 6 base nodes (25-30) -- source lines 68-73, verbatim.

    NOTE -- ops.fix must be called with the UNPACK form ``ops.fix(tag, *vals)``:
    this openseespy build errors on the literal form ``ops.fix(tag, 1,1,1,1,1,1)``
    ("invalid # of constraint values") while accepting the unpacked list.  This
    is a pure arg-counting quirk of the wrapper, not a modelling issue.
    """
    for m in re.finditer(
        r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)", src, re.M
    ):
        vals = [int(m.group(i)) for i in range(2, 8)]
        ops.fix(int(m.group(1)), *vals)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_transformations(src: str) -> dict[int, tuple[float, float, float]]:
    """Parse the 52 geomTransf Linear commands (source lines 177-228).

    Returns a {tag: (vx, vy, vz)} map.  Columns use vecxz along X (1,0,0);
    beams along Z (0,0,1) -- the standard 3D-frame orientation.
    """
    transfs: dict[int, tuple[float, float, float]] = {}
    for m in re.finditer(
        r"^geomTransf\s+Linear\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)",
        src, re.M,
    ):
        tag = int(m.group(1))
        transfs[tag] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))
        ops.geomTransf("Linear", tag, *transfs[tag])
    return transfs


def define_elements_hinge(src: str) -> int:
    """Create the 52 beamWithHinges elements (source lines 230-281), verbatim.

    3D signature (confirmed empirically -- §12ay):
        element beamWithHinges eleTag iNode jNode secTagI lpI secTagJ lpJ
                                  E A Iz Iy G J transfTag
    The Tcl passes 6 elastic-interior values (E A Iz Iy G J); the Python
    wrapper accepts the SAME 6.  (The 2D form, as in Citiner, takes only
    E A Iz.)  Hinge length is sec-tag-specific: lp=500 for sec 1 columns,
    lp=600 for sec 2 beams.
    """
    n = 0
    for m in re.finditer(
        r"^element\s+beamWithHinges\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.eE+-]+)"
        r"\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)"
        r"\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+(\d+)", src, re.M,
    ):
        tag = int(m.group(1)); ni, nj = int(m.group(2)), int(m.group(3))
        secI, lpI, secJ, lpJ = (int(m.group(4)), float(m.group(5)),
                                int(m.group(6)), float(m.group(7)))
        E  = float(m.group(8));   A  = float(m.group(9))
        Iz = float(m.group(10));  Iy = float(m.group(11))
        G  = float(m.group(12));  J  = float(m.group(13))
        transf = int(m.group(14))
        ops.element("beamWithHinges", tag, ni, nj,
                    secI, lpI, secJ, lpJ, E, A, Iz, Iy, G, J, transf)
        n += 1
    return n


def define_elements_fiber(src: str) -> int:
    """Create the 52 nonlinearBeamColumn elements (co2.tcl lines 230-281).

    Signature (§12l -- nonlinearBeamColumn keeps the Tcl 6-arg form):
        element nonlinearBeamColumn eleTag iNode jNode nIP secTag transfTag
    """
    n = 0
    for m in re.finditer(
        r"^element\s+nonlinearBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
        r"\s+(\d+)\s+(\d+)", src, re.M,
    ):
        tag = int(m.group(1)); ni, nj = int(m.group(2)), int(m.group(3))
        n_ip, sec, transf = int(m.group(4)), int(m.group(5)), int(m.group(6))
        ops.element("nonlinearBeamColumn", tag, ni, nj, n_ip, sec, transf)
        n += 1
    return n


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: int) -> "opst.post.CreateODB":
    """Initialise the ODB for one element variant.

    save_frame_resp=False is MANDATORY for BOTH variants: beamWithHinges
    internal sections are accessed by auto-index not user tag (§12v-1), and
    nonlinearBeamColumn internal sections likewise lack user-visible tags
    (§12ap / Dino column precedent).  Nodal responses still track for the
    deformed-shape visualisations.  set_odb_path precedes CreateODB (§12ac).
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        save_nodal_resp=True,
        save_frame_resp=False,
        save_truss_resp=False,
        save_shell_resp=False,
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_lateral_loads() -> None:
    """Inverted-triangle lateral load on UX (source lines 289-298).

    A single Plain pattern with a Linear time series; the displacement-
    control integrator scales it via the load factor λ (pseudo-time).  There
    is NO gravity in this model -- the source applies only this lateral
    pattern before analyze.  (§12z lateral-after-loadConst ordering does NOT
    apply here because there is no gravity phase.)
    """
    ops.timeSeries("Linear", TS_LATERAL)
    ops.pattern("Plain", PAT_LATERAL, TS_LATERAL)
    for node, px in LATERAL_LOADS:
        ops.load(node, px, 0.0, 0.0, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_pushover(odb: "opst.post.CreateODB", odb_tag: int,
                 label: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Run the 100-step displacement-controlled pushover via SmartAnalyze.

    Source solver (lines 300-307): Plain constraints, Plain numberer,
    BandGeneral, EnergyIncr 1e-6/200, Newton, DisplacementControl node 2 DOF 1
    1.0 mm, 100 steps.  SmartAnalyze manages test/algorithm internally (§3c):
    we supply the pushover algorithm fallback list + relaxation (§12v-3) and
    Transformation constraints (converges better than Plain for PDelta-free
    fibre pushover, §12v-4).

    Returns (ux, uz, base_shear) -- 100-element arrays of the control-node UX
    (mm, the controlled DOF), node-2 UZ (mm, the free lateral-drift companion
    DOF validated against node2.out col 4), and base shear (kN = λ × ΣP).
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50, 60],   # Krylov→Newton→NewtonInit→ModNewton→LineSearch→BFGS
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-4,
    )
    # Per-increment cadence: one D_INCR target at a time, static_split into a
    # single segment (§12am) -- gives a 1:1 alignment with the 100-row ref.
    protocol = [D_INCR]
    ux_hist, uz_hist, shear_hist = [], [], []
    for step in range(N_STEPS):
        segs = analysis.static_split(protocol, maxStep=D_INCR)
        done = False
        for seg in segs:
            ok = analysis.StaticAnalyze(node=NODE_CTRL, dof=DOF_CTRL, seg=seg)
            odb.fetch_response_step()
            lam = ops.getTime()                      # load factor (pseudo-time)
            ux = float(ops.nodeDisp(NODE_CTRL, DOF_CTRL))
            uz = float(ops.nodeDisp(NODE_CTRL, 3))   # node 2 UZ
            ux_hist.append(ux)
            uz_hist.append(uz)
            shear_hist.append(lam * P_LATERAL_TOTAL / kN)   # kN
            done = True
        if not done:
            print(f"  [{label}] WARNING: step {step+1} produced no segment")
            break
    analysis.close()

    ux = np.array(ux_hist)
    uz = np.array(uz_hist)
    shear = np.array(shear_hist)
    lam_final = shear[-1] * kN / P_LATERAL_TOTAL if len(shear) else 0.0
    print(f"  [{label}] pushover: {len(ux)}/{N_STEPS} steps | "
          f"final UX={ux[-1]:.3f} mm, UZ={uz[-1]:.3f} mm, "
          f"base shear={shear[-1]:.2f} kN (λ={lam_final:.4f})")
    return ux, uz, shear


def run_analysis(output_dir: Path) -> dict:
    """Build + pushover BOTH element variants; return results dict.

    Each variant is a full wipe/rebuild so they share nothing but the parsed
    source.  The first variant (hinge) also renders the model/loads/pre-
    analysis visualisations (the geometry is identical for both, so rendering
    once is sufficient).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    src_hinge = TCL_HINGE.read_text()
    src_fiber = TCL_FIBER.read_text()
    ref = _read_reference()

    results = {"ref": ref, "variants": {}}

    for i, etype in enumerate(ELEMENT_TYPES):
        odb_tag = ODB_TAG_HINGE if etype == "hinge" else ODB_TAG_FIBER
        label = "beamWithHinges" if etype == "hinge" else "nonlinearBeamColumn"
        print(f"\n=== Building {label} variant (ODB tag {odb_tag}) ===")

        init_model()
        define_materials()
        define_sections()
        define_nodes_mass(src_hinge)               # nodes/mass identical in both TCLs
        define_boundary_conditions(src_hinge)
        if i == 0:
            vis_nodes(output_dir)
        define_transformations(src_hinge)          # transf commands identical
        if etype == "hinge":
            n_ele = define_elements_hinge(src_hinge)
        else:
            n_ele = define_elements_fiber(src_fiber)
        if i == 0:
            vis_model(output_dir)
        print(f"  Built model: {n_ele} {label} elements (expected 52).")

        odb = create_odb(output_dir, odb_tag)
        define_lateral_loads()
        if i == 0:
            vis_loads(output_dir)
            vis_pre_analysis(output_dir)

        print(f"Running {label} pushover...")
        ux, uz, shear = run_pushover(odb, odb_tag, label)
        results["variants"][etype] = {
            "label": label, "odb_tag": odb_tag, "ux": ux, "uz": uz,
            "shear": shear,
        }
        _finalise_odb_vis(odb, output_dir, odb_tag, label)

    return results


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def _read_reference() -> dict:
    """Parse node2.out -- 100 rows of [λ, node2.UX, node2.UY, node2.UZ].

    Returns dict with arrays: lam (load factor), ux, uy, uz.  The pushover is
    DisplacementControl on node-2 UX, so ref UX is exactly 1..100 mm (the
    controlled DOF); the quantities to validate are λ (col 0 -> base shear)
    and the free UZ (col 3).
    """
    lam, ux, uy, uz = [], [], [], []
    if not REF_FILE.exists():
        return {}
    with open(REF_FILE) as f:
        for line in f:
            p = line.split()
            if len(p) >= 4:
                lam.append(float(p[0])); ux.append(float(p[1]))
                uy.append(float(p[2])); uz.append(float(p[3]))
    return {"lam": np.array(lam), "ux": np.array(ux),
            "uy": np.array(uy), "uz": np.array(uz),
            "shear": np.array(lam) * P_LATERAL_TOTAL / kN}


def _finalise_odb_vis(odb: "opst.post.CreateODB", output_dir: Path,
                      odb_tag: int, label: str) -> None:
    """Flush the ODB and render deformed-shape visualisations for one variant."""
    odb.save_response()
    if _headless():
        return
    opst.post.set_odb_path(str(output_dir))
    suffix = "hinge" if label.startswith("beamWith") else "fiber"
    vis_defo(output_dir, filename=f"vis_05_deformed_{suffix}.html",
             odb_tag=odb_tag, resp_dof="UX", scale=50.0)
    vis_slider(output_dir, filename=f"vis_06_slider_{suffix}.html",
               odb_tag=odb_tag, resp_dof="UX", scale=50.0)
    vis_anim(output_dir, filename=f"vis_07_animation_{suffix}.html",
             odb_tag=odb_tag, defo_scale=50.0,
             resp_dof=("UX", "UY", "UZ"))


def _plot_compare(results: dict, output_dir: Path) -> None:
    """Three-way pushover comparison: hinge vs fiber vs reference.

    Two panels: (a) base shear vs node-2 UX (the capacity curve -- the
    controlled DOF), (b) node-2 UZ vs step (the free companion DOF most
    sensitive to the plasticity formulation).
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  (matplotlib unavailable -- skipping compare plot)")
        return

    ref = results["ref"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    styles = {"hinge": ("r", "--", "beamWithHinges"),
              "fiber": ("b", "-.", "nonlinearBeamColumn")}
    # (a) base shear vs UX
    if ref.get("ux") is not None and len(ref["ux"]):
        ax1.plot(ref["ux"], ref["shear"], "k-", linewidth=1.0, alpha=0.6,
                 label="Reference (node2.out)")
    for etype, (c, ls, lbl) in styles.items():
        v = results["variants"].get(etype)
        if v is not None and len(v["ux"]):
            ax1.plot(v["ux"], v["shear"], color=c, linestyle=ls,
                     linewidth=1.3, alpha=0.9, label=f"Sim: {lbl}")
    ax1.set_xlabel("Node 2 UX displacement (mm)")
    ax1.set_ylabel("Base shear (kN)")
    ax1.set_title("Pushover capacity curve")
    ax1.axhline(0.0, color="0.6", linewidth=0.5)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=8)

    # (b) UZ vs step
    steps = np.arange(1, N_STEPS + 1)
    if ref.get("uz") is not None and len(ref["uz"]):
        ax2.plot(steps, ref["uz"], "k-", linewidth=1.0, alpha=0.6,
                 label="Reference (node2.out)")
    for etype, (c, ls, lbl) in styles.items():
        v = results["variants"].get(etype)
        if v is not None and len(v["uz"]):
            ax2.plot(steps[:len(v["uz"])], v["uz"], color=c, linestyle=ls,
                     linewidth=1.3, alpha=0.9, label=f"Sim: {lbl}")
    ax2.set_xlabel("Pushover step (1 .. 100)")
    ax2.set_ylabel("Node 2 UZ displacement (mm)")
    ax2.set_title("Free lateral-drift companion DOF (UZ)")
    ax2.axhline(0.0, color="0.6", linewidth=0.5)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8)

    fig.suptitle("Dino_PlasticHinge -- concentrated vs distributed plasticity",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(str(output_dir / "pushover_compare.png"), dpi=150)
    plt.close(fig)


def _verify(results: dict) -> None:
    """Print step-count + peak/RMS comparison against node2.out for each variant."""
    ref = results["ref"]
    print("\n── Verification vs node2.out ─────────────────────────────────")
    if not ref:
        print("  (no reference file -- skipping)")
        return
    ref_uz = ref["uz"]
    ref_shear = ref["shear"]
    for etype in ELEMENT_TYPES:
        v = results["variants"].get(etype)
        if v is None:
            continue
        label = v["label"]
        uz, shear = v["uz"], v["shear"]
        print(f"\n  [{label}]")
        print(f"    steps: {len(uz)} / {N_STEPS}")
        if len(uz) == 0:
            continue
        n = min(len(uz), len(ref_uz))
        # peak + RMS on UZ (the formulation-sensitive DOF)
        print(f"    final UZ:   sim={uz[-1]:.4f} mm | ref={ref_uz[-1]:.4f} mm | "
              f"diff={100*abs(uz[-1]-ref_uz[-1])/max(abs(ref_uz[-1]),1e-9):.2f}%")
        if n > 0:
            rms = float(np.sqrt(np.mean((uz[:n] - ref_uz[:n]) ** 2)))
            print(f"    UZ per-point RMS over {n} steps: {rms:.5f} mm")
        # base shear at final step
        print(f"    final shear: sim={shear[-1]:.3f} kN | "
              f"ref={ref_shear[-1]:.3f} kN | "
              f"diff={100*abs(shear[-1]-ref_shear[-1])/max(abs(ref_shear[-1]),1e-9):.2f}%")


def post_process(results: dict, output_dir: Path) -> None:
    """Render the comparison plot, dump CSVs, and print verification."""
    # per-variant CSV: step, ux, uz, base_shear_kN
    ref = results["ref"]
    if ref.get("uz") is not None and len(ref["uz"]):
        curve = np.column_stack([np.arange(1, len(ref["uz"]) + 1),
                                 ref["ux"], ref["uz"], ref["shear"]])
        np.savetxt(str(output_dir / "pushover_ref.csv"), curve,
                   delimiter=",", header="step,ux_mm,uz_mm,shear_kN")
    for etype in ELEMENT_TYPES:
        v = results["variants"].get(etype)
        if v is None or len(v["ux"]) == 0:
            continue
        curve = np.column_stack([np.arange(1, len(v["ux"]) + 1),
                                 v["ux"], v["uz"], v["shear"]])
        np.savetxt(str(output_dir / f"pushover_{etype}.csv"), curve,
                   delimiter=",", header="step,ux_mm,uz_mm,shear_kN")
    _plot_compare(results, output_dir)
    _verify(results)


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    results = run_analysis(output_dir)
    post_process(results, output_dir)
    print("\nDino_PlasticHinge: analysis complete.")
