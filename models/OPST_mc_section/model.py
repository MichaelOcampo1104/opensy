# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Moment-Curvature Section Analysis (opstool FiberSecMesh)
UniqueID : OPST_mc_section
Author   : OpenSeesPy Standardisation Agent
Date     : 2026-07-11
Purpose  : Moment-curvature analysis of a 2x2 m hollow RC box section via
           opstool's FiberSecMesh + MomentCurvature (no structural mesh).
Ref      : https://opstool.readthedocs.io/en/stable/src/analysis/mc_analysis.html
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import _headless   # CI headless guard

import matplotlib
matplotlib.use("Agg")            # non-interactive — safe for scripts (plot_utils.py)
import matplotlib.pyplot as plt

# Plot style constants — mirrored from standards/plot_utils.py
COLORS = {
    "primary":   "#185FA5",   # M-phi curve
    "secondary": "#de0f17",   # bilinearised backbone / limit points
    "tertiary":  "#3B6D11",   # reference markers
    "grid":      "#cccccc",
    "text":      "#333333",
    "bg":        "#f8f8f6",
}


# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Materials (3 — source defines cover, core, and steel)
MAT_CONC_COVER = 1     # Concrete04 — unconfined cover
MAT_CONC_CORE  = 2     # Concrete04 — confined core
MAT_STEEL      = 3     # Steel01 — rebar

# Section
SEC_BOX        = 1     # Fiber section (hollow box: cover ring + core ring + rebar)


# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Source is kN-m; converted to N-mm-MPa here.  Conversion factors at top so each
# value reads as <source_value> * <factor> (AGENT.md §3a rule).
#   stress:   1 kN/m² = 1e-3 MPa
#   length:   1 m     = 1000 mm
#   moment:   1 kN·m  = 1e6 N·mm
#   force:    1 kN    = 1000 N
#   curvature:1 /m    = 1e-3 /mm   (curvature is 1/length)

# Geometry — square hollow box, 2 m side, 50 mm cover, 1x1 m core hole (mm)
B_OUT      = 2.0 * m            # 2000 mm outer side
COVER      = 0.05 * m           # 50 mm clear cover
HOLE_HALF  = 0.5 * m            # 500 mm — half of the 1x1 m central hole
D_BAR      = 0.02 * m           # 20 mm rebar diameter
COVER_OFF  = COVER + D_BAR / 2  # rebar centroid offset from outer edge
REBAR_GAP  = 0.1 * m            # 100 mm rebar spacing along the perimeter
MESH_SIZE  = 0.1 * m            # 100 mm triangle mesh size (cover + core)

# Material — Concrete04 (cover): fc, ec, ecu, Ec, ft, et
FC_COVER   = 32.4 * MPa         # |fc| = 32.4 MPa  (source -32.4e3 kN/m²)
EC_COVER   = -2000.0e-6         # strain at peak (dimensionless — unchanged)
ECU_COVER  = 2.1 * EC_COVER     # -0.0042 ultimate strain
EC_MOD    = 3.55e7 * kPa        # 35500 MPa concrete elastic modulus
FT_COVER   = 2.64 * MPa         # 2.64 MPa tensile strength
ET_COVER   = 107.0e-6           # tensile strain at ft

# Material — Concrete04 (core, confined): higher fc, larger ecu
FC_CORE    = 40.6 * MPa         # 40.6 MPa confined strength
EC_CORE    = -4079.0e-6         # -0.004079
ECU_CORE   = -0.0144            # -0.0144 ultimate strain

# Material — Steel01 rebar
FYS        = 300.0 * MPa        # 300 MPa yield
ES_STEEL   = 2.0e8 * kPa        # 200000 MPa elastic modulus
B_STEEL    = 0.01               # strain-hardening ratio

# Section torsional stiffness
SEC_GJ     = 100000.0 * kN * m**2   # source 100000 kN·m² -> N·mm²

# Moment-curvature analysis
AXIAL_FORCE = -20000.0 * kN     # -20 MN compression (source -20000 kN)
AXIS        = "y"               # bend about local y
# Curvature unit trap (§12ar): incr_phi/max_phi are in 1/length.
#   Source uses incr_phi=1e-5 [1/m]; in N-mm that becomes 1e-5 * (1 m / 1 mm)
#   = 1e-5 * 1e-3 = 1e-8 [1/mm].  max_phi default 0.5 [1/m] -> 5e-4 [1/mm].
INCR_PHI    = 1.0e-5 * 1.0e-3   # 1e-8 /mm
MAX_PHI     = 0.5 * 1.0e-3      # 5e-4 /mm
LIMIT_PEAK_RATIO = 0.8          # stop when moment drops to 80% of peak

# Limit-state thresholds (strains — dimensionless, unchanged by unit conversion)
THRESH_STEEL_YIELD = 2.0e-3     # steel yield strain -> (phiy, My)
THRESH_CORE_CRUSH  = ECU_CORE   # core concrete crushing -> (phiu, Mu)

# Reference values from the docs page (converted to N-mm / 1/mm for comparison)
REF_PHIY = 1.6e-3 * 1.0e-3      # 1.6e-6 /mm
REF_MY   = 20552.69 * kN * m    # 2.0553e10 N·mm
REF_PHIU = 4.34e-2 * 1.0e-3     # 4.34e-5 /mm
REF_MU   = 23749.61 * kN * m    # 2.3750e10 N·mm


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Wipe and initialise a 3D model.

    MomentCurvature builds its own zeroLength element internally, but it needs
    an active ``ops.model`` for material/section registration.
    """
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    """Define Concrete04 (cover + core) and Steel01 rebar materials.

    Source values converted from kN/m² to MPa via ``× kPa`` (1 kN/m² = 1 kPa =
    1e-3 MPa).  Strains are dimensionless — unchanged.
    """
    ops.uniaxialMaterial("Concrete04", MAT_CONC_COVER,
                         -FC_COVER, EC_COVER, ECU_COVER, EC_MOD, FT_COVER, ET_COVER)
    ops.uniaxialMaterial("Concrete04", MAT_CONC_CORE,
                         -FC_CORE, EC_CORE, ECU_CORE, EC_MOD, FT_COVER, ET_COVER)
    ops.uniaxialMaterial("Steel01", MAT_STEEL,
                         FYS, ES_STEEL, B_STEEL)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_section() -> "opst.pre.section.FiberSecMesh":
    """Build the hollow-box fiber section via opstool's FiberSecMesh.

    The section is a square ring (cover) + inner ring (core, around a 1x1 m
    central hole) + a rebar line around the perimeter.  opstool's
    ``FiberSecMesh`` triangulates the polygons (sectionproperties backend) and
    emits native OpenSees ``fiber`` commands via ``to_opspy_cmds``.

    Note: this uses opstool's polygon-patch mesher (supports the cover outline
    and central hole), NOT the raw ``ops.patch("rect")`` of §12ap/§12e — those
    are for simple rectangles without holes.

    Returns:
        The FiberSecMesh instance (for geometry visualisation).
    """
    # Outer square outline (mm)
    outlines = [[0.0, 0.0], [B_OUT, 0.0], [B_OUT, B_OUT], [0.0, B_OUT]]
    # Cover ring: outer square minus an inset square.  opst.pre.section.offset
    # shrinks inward for d>0 (despite the docstring saying the opposite).
    coverlines = opst.pre.section.offset(outlines, d=COVER)
    cover = opst.pre.section.create_polygon_patch(outlines, holes=[coverlines])
    # Core ring: inset square minus the central hole
    holelines = [[HOLE_HALF, HOLE_HALF],
                 [B_OUT - HOLE_HALF, HOLE_HALF],
                 [B_OUT - HOLE_HALF, B_OUT - HOLE_HALF],
                 [HOLE_HALF, B_OUT - HOLE_HALF]]
    core = opst.pre.section.create_polygon_patch(coverlines, holes=[holelines])

    SEC = opst.pre.section.FiberSecMesh()
    SEC.add_patch_group(dict(cover=cover, core=core))
    SEC.set_mesh_size(dict(cover=MESH_SIZE, core=MESH_SIZE))
    SEC.set_mesh_color(dict(cover="gray", core="green"))
    SEC.set_ops_mat_tag(dict(cover=MAT_CONC_COVER, core=MAT_CONC_CORE))
    SEC.mesh()

    # Rebar line around the perimeter at the cover-centroid offset (inward)
    rebar_lines = opst.pre.section.offset(outlines, d=COVER_OFF)
    SEC.add_rebar_line(points=rebar_lines, dia=D_BAR, gap=REBAR_GAP,
                       color="red", ops_mat_tag=MAT_STEEL)

    SEC.get_frame_props(display_results=False)
    SEC.centring()                          # re-centre on centroid
    SEC.to_opspy_cmds(secTag=SEC_BOX, GJ=SEC_GJ)
    return SEC


# ── 7. NODES ─────────────────────────────────────────────────────────────────
# Not used — MomentCurvature builds its own zeroLength element internally.
# (Section-level analysis: no structural nodes. Precedent: §12p/§12q.)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
# Not used — see §7.


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
# Not used — see §7.


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
# Not used — a section analysis produces no nodal/element ODB responses.  The
# M-phi curve and fiber data are returned in-memory by MomentCurvature.


# ── 11. LOADING ──────────────────────────────────────────────────────────────
# Not a load pattern — the constant axial compression (AXIAL_FORCE) is passed
# directly to the MomentCurvature constructor; curvature is the imposed
# deformation.


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_moment_curvature(output_dir: Path) -> tuple[dict, "opst.anlys.MomentCurvature"]:
    """Build the section and run the moment-curvature analysis.

    Args:
        output_dir: Directory for output files (created if absent).

    Returns:
        (results, MC) where results is a dict with keys:
          phi, M          — curvature [1/mm] and moment [N·mm] arrays;
          phiy, My        — yield point (steel reaches 2e-3 strain);
          phiu, Mu        — ultimate point (core concrete crushing);
          phi_eq, M_eq    — bilinearised equivalent (phi_eq, M_eq);
          and the REF_* constants for comparison.
        MC is the MomentCurvature instance (for fiber-response plotting).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    init_model()
    define_materials()
    define_section()

    MC = opst.anlys.MomentCurvature(sec_tag=SEC_BOX, axial_force=AXIAL_FORCE)
    MC.analyze(axis=AXIS, max_phi=MAX_PHI, incr_phi=INCR_PHI,
               limit_peak_ratio=LIMIT_PEAK_RATIO, smart_analyze=True)

    # Limit states (curvature, moment) — steel yield + core crush
    phiy, My = MC.get_limit_state(matTag=MAT_STEEL, threshold=THRESH_STEEL_YIELD)
    phiu, Mu = MC.get_limit_state(matTag=MAT_CONC_CORE, threshold=THRESH_CORE_CRUSH,
                                  peak_drop=False)
    # Bilinearised equivalent (equal-energy up to phiu)
    phi_eq, M_eq = MC.bilinearize(phiy, My, phiu)

    print(f"  phiy = {phiy*1e3:.4e} /m   My  = {My/(kN*m):.2f} kN·m")
    print(f"  phiu = {phiu*1e3:.4e} /m   Mu  = {Mu/(kN*m):.2f} kN·m")
    print(f"  phi_eq = {phi_eq*1e3:.4e} /m  M_eq = {M_eq/(kN*m):.2f} kN·m")

    results = {
        "phi": np.array(MC.phi), "M": np.array(MC.M),
        "phiy": phiy, "My": My,
        "phiu": phiu, "Mu": Mu,
        "phi_eq": phi_eq, "M_eq": M_eq,
        "ref_phiy": REF_PHIY, "ref_My": REF_MY,
        "ref_phiu": REF_PHIU, "ref_Mu": REF_MU,
    }
    return results, MC


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def _style_ax(ax, xlabel: str, ylabel: str, title: str):
    """Apply consistent styling (mirrors standards/plot_utils.py)."""
    ax.set_facecolor(COLORS["bg"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(COLORS["grid"])
    ax.tick_params(colors="#555555", labelsize=9)
    ax.set_xlabel(xlabel, fontsize=9, color="#555555")
    ax.set_ylabel(ylabel, fontsize=9, color="#555555")
    ax.set_title(title, fontsize=10, fontweight="bold",
                 color=COLORS["text"], pad=6)
    ax.grid(True, linestyle="dotted", alpha=0.5)


def _pct(sim: float, ref: float) -> str:
    """Percentage difference string (sim vs ref)."""
    if ref == 0:
        return "NA"
    return f"{(sim - ref) / abs(ref) * 100:+.2f}%"


def post_process(results: dict, MC: "opst.anlys.MomentCurvature",
                 output_dir: Path) -> None:
    """Render the M-phi curve, bilinearised backbone, and fiber responses.

    Axes are plotted in kN·m and 1/m (the source's native engineering units)
    for readability — converted from the model's N-mm / 1/mm on the plot.

    Args:
        results: Results dict from run_moment_curvature.
        MC: The MomentCurvature instance (for fiber-response plotting).
        output_dir: Directory for output files.
    """
    KN_M = kN * m   # 1e6 N·mm
    phi_perm = 1.0e3    # /mm -> /m for display
    M_perm = 1.0 / KN_M  # N·mm -> kN·m for display

    # ── M-phi curve with limit states + bilinearised backbone + reference ──
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor(COLORS["bg"])
    phi = results["phi"] * phi_perm
    M = results["M"] * M_perm
    ax.plot(phi, M, color=COLORS["primary"], linewidth=1.5, label="M-φ (sim)")

    # Bilinearised backbone (0 -> (phiy,My) -> (phi_eq,M_eq) -> (phiu,M_eq))
    phi_bl = [0, results["phiy"], results["phi_eq"], results["phiu"]]
    M_bl = [0, results["My"], results["M_eq"], results["M_eq"]]
    ax.plot([p * phi_perm for p in phi_bl],
            [m * M_perm for m in M_bl],
            color=COLORS["secondary"], linewidth=1.3, linestyle="--",
            label="Bilinearised")

    # Limit-state points
    ax.plot(results["phiy"] * phi_perm, results["My"] * M_perm, "o",
            ms=8, mec="black", mfc=COLORS["secondary"], label=f"Yield ({results['My']/KN_M:.0f} kN·m)")
    ax.plot(results["phiu"] * phi_perm, results["Mu"] * M_perm, "s",
            ms=8, mec="black", mfc=COLORS["secondary"], label=f"Ultimate ({results['Mu']/KN_M:.0f} kN·m)")

    # Reference markers
    ax.plot(results["ref_phiy"] * phi_perm, results["ref_My"] * M_perm, "x",
            ms=10, mew=2, color=COLORS["tertiary"], label="Reference (docs)")
    ax.plot(results["ref_phiu"] * phi_perm, results["ref_Mu"] * M_perm, "x",
            ms=10, mew=2, color=COLORS["tertiary"])

    _style_ax(ax, "Curvature φ (1/m)", "Moment M (kN·m)",
              "OPST_mc_section — Moment-Curvature")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(str(output_dir / "mphi_curve.png"), dpi=150,
                facecolor=COLORS["bg"])
    plt.close(fig)
    print(f"  📊 mphi_curve.png saved")

    # ── Fiber stress-strain responses (opstool's own plot) ──
    try:
        axs = MC.plot_fiber_responses(return_ax=True)
        fig2 = axs[0].figure if hasattr(axs, "__len__") else axs.figure
        fig2.savefig(str(output_dir / "fiber_stress_strain.png"), dpi=150,
                     bbox_inches="tight")
        plt.close(fig2)
        print("  📊 fiber_stress_strain.png saved")
    except Exception as e:
        print(f"  (fiber-response plot skipped: {e})")

    # ── Verification table ──
    print("\n  ── Verification (sim vs docs reference) ──")
    print(f"  phiy: sim {results['phiy']*phi_perm:.4e} /m"
          f"  ref {results['ref_phiy']*phi_perm:.4e} /m"
          f"  {_pct(results['phiy'], results['ref_phiy'])}")
    print(f"  My :  sim {results['My']/KN_M:.2f} kN·m"
          f"     ref {results['ref_My']/KN_M:.2f} kN·m"
          f"     {_pct(results['My'], results['ref_My'])}")
    print(f"  phiu: sim {results['phiu']*phi_perm:.4e} /m"
          f"  ref {results['ref_phiu']*phi_perm:.4e} /m"
          f"  {_pct(results['phiu'], results['ref_phiu'])}")
    print(f"  Mu :  sim {results['Mu']/KN_M:.2f} kN·m"
          f"     ref {results['ref_Mu']/KN_M:.2f} kN·m"
          f"     {_pct(results['Mu'], results['ref_Mu'])}")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    results, MC = run_moment_curvature(output_dir)
    post_process(results, MC, output_dir)
    print("OPST_mc_section: analysis complete.")
