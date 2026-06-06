# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Single bolted-bolted angle force-deformation (19 test cases)
UniqueID : bradley2021
Author   : Converted from Bradley (2021) Tcl model
Date     : 2026-06-07
Purpose  : Cyclic tension force-deformation analysis of 19 bolted-bolted steel
           angles using a zeroLengthSection fiber model with experimentally
           calibrated SteelMPF materials per Beland et al. (2019).
Ref      : Beland et al. (2019) — experimental calibration of bolted angle
           connection behavior
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Base materials (shared across all TCs)
MAT_ELASTIC_SOFT  = 3     # very soft elastic for Parallel numerical stability
MAT_ENT_BOLT      = 11    # ENT bolt bearing (very stiff)

# Section & element tags
SEC_FIBER         = 1
SEC_AGGR          = 2
ELE_ZLS           = 1

# Node tags
NODE_FIXED        = 1
NODE_LOADED       = 2

# Analysis
ODB_TAG           = 1
CTRL_DOF          = 1     # UX
N_STEPS_PER_CYCLE = 100   # substeps within each half-cycle

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# --- Drift targets (inches) ---
# 44 displacement targets from AISC 341 Section K2.4b
_DRIFT_TARGETS_IN = [
    0.01268, 0.02254, 0.04347, 0.07084, 0.1256, 0.1932, 0.3188, 0.4637,
    0.6118, 0.7535, 0.8903, 1.030, 1.159, 1.304, 1.435, 1.584, 1.716,
    1.848, 2.053, 2.190, 2.326, 2.463, 2.600, 2.737, 2.874, 3.011,
    3.148, 3.284, 3.421, 3.558, 3.695, 3.832, 3.969, 4.106, 4.242,
    4.379, 4.516, 4.653, 4.790, 4.927, 5.063, 5.200, 5.337, 5.474,
]

# FEMA 350 cycle counts: first 4 targets → 6,6,6,4 cycles; all subsequent → 2
_FEMA350_CYCLES = [6, 6, 6, 4]
_FEMA350_ADD    = 2

# --- SteelMPF parameters per TC ---
# [fyp, fyn, E0, bp, bn, R0, cR1, cR2]
# fyp/fyn/E0 in ksi; bp/bn/R0/cR1/cR2 dimensionless
_STEELMPF_KSI = {
    1:  (21.85252,  21.85252,  1987.230,  0.0129, 0.0129, 1.118, -0.944,   0.2283465),
    2:  (17.76079,  17.76079,  1770.234,  0.0155, 0.0155, 1.114, -1.306,   0.1771654),
    3:  (42.42356,  42.42356,  5156.520,  0.0170, 0.0170, 1.803, -0.633,   0.1023622),
    4:  (37.79227,  37.79227,  3117.896,  0.0137, 0.0137, 1.451, -0.733,   0.2007874),
    5:  (57.30665,  57.30665,  12454.45,  0.0046, 0.0046, 1.625, -1.030,   0.1574803),
    6:  (84.37500,  84.37500,  11346.63,  0.0041, 0.0041, 1.311, -0.932,   0.1417323),
    7:  (17.94065,  17.94065,  822.3022,  0.0241, 0.0241, 1.314, -1.140,   0.2559055),
    8:  (16.88399,  16.88399,  793.7500,  0.0158, 0.0158, 0.939, -1.323,   0.2283465),
    9:  (33.88040,  33.88040,  2158.543,  0.0133, 0.0133, 1.687, -0.518,   0.2165354),
    10: (25.49460,  25.49460,  2272.752,  0.0125, 0.0125, 1.751, -0.639,   0.2322835),
    11: (47.84173,  47.84173,  5127.968,  0.0105, 0.0105, 1.211, -0.935,   0.2125984),
    12: (40.75989,  40.75989,  5476.304,  0.0078, 0.0078, 1.218, -0.861,   0.2165354),
    13: (63.37680,  63.37680,  9679.182,  0.0077, 0.0077, 0.895, -1.162,   0.1653543),
    14: (52.15827,  52.15827,  7149.460,  0.0100, 0.0100, 1.079, -1.088,   0.2165354),
    15: (11.12860,  11.12860,  405.4406,  0.0263, 0.0263, 1.179, -1.369,   0.2716535),
    16: (21.76259,  21.76259,  2095.728,  0.0116, 0.0116, 1.218, -0.876,   0.2874016),
    17: (33.67806,  33.67806,  4277.113,  0.0065, 0.0065, 1.492, -0.677,   0.1929134),
    18: (46.49281,  46.49281,  5653.327,  0.0055, 0.0055, 1.526, -0.274,   0.1889764),
    19: (26.04541,  26.04541,  1479.002,  0.0115, 0.0115, 1.433, -1.194,   0.1889764),
}

# Fatigue eps0 per TC [inches]
_FATIGUE_EPS0_IN = {
    1: 1.785, 2: 1.980, 3: 1.200, 4: 1.785, 5: 1.955,
    6: 1.565, 7: 2.190, 8: 2.612, 9: 2.185, 10: 2.390,
    11: 1.840, 12: 1.960, 13: 1.960, 14: 1.840, 15: 2.390,
    16: 1.785, 17: 2.610, 18: 2.610, 19: 1.785,
}

# MinMax max per TC [inches]
_MINMAX_MAX_IN = {
    1: 1.000000, 2: 1.318898, 3: 0.7047244, 4: 1.543307, 5: 1.374016,
    6: 1.086614, 7: 1.370079, 8: 1.452756, 9: 1.799213, 10: 1.559055,
    11: 0.6062992, 12: 1.405512, 13: 1.003937, 14: 0.8700787, 15: 1.905512,
    16: 1.500000, 17: 1.960630, 18: 1.712598, 19: 1.251969,
}

# Angle labels for each TC
_ANGLE_LABELS = {
    1: "L6X4X3/8", 2: "L6X6X3/8", 3: "L8X4X1/2", 4: "L8X6X1/2",
    5: "L8X6X5/8", 6: "L8X6X3/4", 7: "L6X6X3/8", 8: "L6X6X3/8",
    9: "L8X6X1/2", 10: "L8X6X1/2", 11: "L8X6X5/8", 12: "L8X6X5/8",
    13: "L8X6X3/4", 14: "L8X6X3/4", 15: "L6X6X3/8", 16: "L8X6X1/2",
    17: "L8X6X5/8", 18: "L8X6X3/4", 19: "L4X4X5/16",
}

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def _define_base_materials() -> None:
    """Shared base materials (tags 1-11) plus gap/contact materials (12-15).

    Material tags 12-15 (ElasticPPGap / Parallel for B2C and G2C contact)
    are defined for fidelity to the reference Tcl but are not used in the
    fiber section. Only MAT_ELASTIC_SOFT (3) and MAT_ENT_BOLT (11) feed
    into the Parallel angle material.
    """
    E_STEEL = 29000.0 * ksi       # 29 000 ksi = ~200 000 MPa

    # Elastic materials at various scales (tags 1-9): 10^-8 … 10^0
    for k in range(1, 10):
        scale = 10.0 ** (k - 9)
        ops.uniaxialMaterial("Elastic", k, E_STEEL * scale)
    # Material 10: Elastic with E scaled 10^3 (very stiff, tag 10)
    ops.uniaxialMaterial("Elastic", 10, E_STEEL * 1e3)

    # ENT bolt bearing (tag 11) — very stiff
    ops.uniaxialMaterial("ENT", MAT_ENT_BOLT, E_STEEL * 1e3)

    # ElasticPPGap: B2C Gap (tag 12), G2C Gap (tag 13)
    ops.uniaxialMaterial("ElasticPPGap", 12,
                         290.0 * ksi,     # E  [ksi → MPa]
                         -55.0 * ksi,     # Fy [ksi → MPa] — compressive yield
                         -0.5 * inch)     # gap [in → mm]
    ops.uniaxialMaterial("ElasticPPGap", 13,
                         290.0 * ksi,
                         -46.8 * ksi,
                         -0.5 * inch)

    # Parallel contacts: B2C (tag 14), G2C (tag 15) — combine gap + soft elastic
    ops.uniaxialMaterial("Parallel", 14, 12, MAT_ELASTIC_SOFT)
    ops.uniaxialMaterial("Parallel", 15, 13, MAT_ELASTIC_SOFT)


def _define_tc_materials(tc: int) -> int:
    """Define TC-specific SteelMPF→Fatigue→MinMax→Parallel chain.

    Returns the AngleMat tag (Parallel composite) used in the fiber section.
    """
    fyp, fyn, E0, bp, bn, R0, cR1, cR2 = _STEELMPF_KSI[tc]
    eps0_in = _FATIGUE_EPS0_IN[tc]
    mmax_in = _MINMAX_MAX_IN[tc]

    tag_smpf   = tc * 4 + 12   # SteelMPF
    tag_fat    = tc * 4 + 13   # Fatigue
    tag_mm     = tc * 4 + 14   # MinMax
    tag_par    = tc * 4 + 15   # Parallel  → AngleMat

    ops.uniaxialMaterial("SteelMPF", tag_smpf,
                         fyp * ksi, fyn * ksi, E0 * ksi,
                         bp, bn, R0, cR1, cR2)
    ops.uniaxialMaterial("Fatigue", tag_fat, tag_smpf,
                         -E0 * ksi,           # -E0: use parent E0, negative
                         eps0_in * inch)      # eps0 [in → mm]
    ops.uniaxialMaterial("MinMax", tag_mm, tag_fat,
                         "-min", -1.0e9,
                         "-max", mmax_in * inch)  # max [in → mm]
    ops.uniaxialMaterial("Parallel", tag_par,
                         MAT_ELASTIC_SOFT, MAT_ENT_BOLT, tag_mm)
    return tag_par


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections(angle_mat: int) -> None:
    """Build fiber section with the angle material + numerical stability layer."""
    ops.section("Fiber", SEC_FIBER)
    # Single fiber at origin — represents the angle's axial behavior
    ops.fiber(0.0, 0.0, 1.0 * inch, angle_mat)      # A=1 in² → 25.4 mm² (ZLS)
    # Straight layer for numerical stability (2 fibers, mat 2, tiny area)
    ops.layer("straight", 2, 2, 1e-9 * inch,         # A=1e-9 in² → 2.54e-8 mm²
              -1.0 * inch, 0.0, 1.0 * inch, 0.0)     # y=±1 in → ±25.4 mm

    # Aggregator: stiff shear so only axial DOF is active
    ops.section("Aggregator", SEC_AGGR, 1, "Vy",
                "-section", SEC_FIBER)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    ops.node(NODE_FIXED,  0.0, 0.0)
    ops.node(NODE_LOADED, 0.0, 0.0)

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    ops.fix(NODE_FIXED,  1, 1, 1)   # all DOFs fixed
    ops.fix(NODE_LOADED, 0, 1, 0)   # only DY fixed; UX and RZ free

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    ops.element("zeroLengthSection", ELE_ZLS,
                NODE_FIXED, NODE_LOADED, SEC_AGGR,
                "-orient", 1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
                "-doRayleigh", 0)

# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(tc: int, output_dir: Path) -> "opst.post.CreateODB":
    tc_dir = output_dir / f"TC{tc}"
    tc_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(tc_dir))
    odb = opst.post.CreateODB(odb_tag=ODB_TAG)
    odb.save_model_data()
    return odb

# ── 11. LOADING ──────────────────────────────────────────────────────────────
def _build_drift_protocol() -> list:
    """Return the list of per-cycle displacement increments (mm).

    Each entry is the DisplacementControl increment for one half-cycle.
    Positive → away from zero; negative → back to zero.
    Follows FEMA 350 cycle counts with half-cycle alternation.
    """
    n_cyc_groups = len(_DRIFT_TARGETS_IN) // 2   # 22
    protocol = []
    for i in range(1, n_cyc_groups + 1):
        j = i - 1                                # half-cycle: use each target singly
        nc = (_FEMA350_CYCLES[i - 1]
              if i - 1 < len(_FEMA350_CYCLES)
              else _FEMA350_ADD)
        d_inc = _DRIFT_TARGETS_IN[j] / N_STEPS_PER_CYCLE  # in inches
        for _ in range(nc):
            protocol.append(d_inc * inch)        # positive increment [mm]
            protocol.append(-d_inc * inch)       # negative increment (back to zero)
    return protocol


def define_loading() -> None:
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(NODE_LOADED, 1.0, 0.0, 0.0)   # unit reference load in UX

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_cyclic_analysis(
    odb: "opst.post.CreateODB",
    drift_increments: list,
) -> None:
    """Run cyclic displacement-controlled analysis using SmartAnalyze.

    Each half-cycle is one SmartAnalyze run with DisplacementControl.
    Total disp change per cycle = increment × N_STEPS_PER_CYCLE.
    """
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-7, 400)

    for inc in drift_increments:
        total_disp = inc * N_STEPS_PER_CYCLE
        ops.integrator("DisplacementControl", NODE_LOADED, CTRL_DOF, inc)
        analysis = opst.anlys.SmartAnalyze(
            analysis_type="Static",
            tryAlterAlgoTypes=True,
            algoTypes=[40, 10, 20, 30, 50, 60],
            tryAddTestTimes=True,
            testIterTimesMore=[50, 100],
            relaxation=0.5,
            minStep=1.0e-4,
        )
        segs = analysis.static_split([total_disp], maxStep=abs(inc))
        for seg in segs:
            analysis.StaticAnalyze(node=NODE_LOADED, dof=CTRL_DOF, seg=seg)
            odb.fetch_response_step()
        analysis.close()


def run_analysis(tc: int, output_dir: Path) -> "opst.post.CreateODB":
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    _define_base_materials()
    angle_mat = _define_tc_materials(tc)
    define_sections(angle_mat)
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)
    define_elements()
    vis_model(output_dir)
    odb = create_odb(tc, output_dir)
    define_loading()
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    drift_inc = _build_drift_protocol()
    run_cyclic_analysis(odb, drift_inc)
    return odb

# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", tc: int, output_dir: Path) -> None:
    odb.save_response()
    tc_dir = output_dir / f"TC{tc}"
    if not _headless():
        try:
            fig = opst.vis.plotly.plot_nodal_responses(
                odb_tag=ODB_TAG, resp_type="disp", resp_dof="UX",
            )
            fig.write_html(str(tc_dir / "vis_05_deformed.html"))
        except Exception:
            pass   # skip post viz if ODB data is incomplete (e.g. convergence failure)

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Bradley2021 — single bolted-bolted angle force-deformation")
    parser.add_argument("--tc", type=int, default=0,
                        help="Test case to run (1-19, default 0 = all)")
    parser.add_argument("--out", type=str, default=None,
                        help="Output directory override")
    args = parser.parse_args()

    output_dir = Path(args.out) if args.out else Path(__file__).parent / "output"

    tcs = [args.tc] if args.tc else range(1, 20)
    for tc in tcs:
        label = _ANGLE_LABELS.get(tc, "?")
        print(f"\n── TC{tc} ({label}) ──")
        try:
            odb = run_analysis(tc, output_dir)
            post_process(odb, tc, output_dir)
            print(f"  TC{tc}: OK")
        except Exception as e:
            print(f"  TC{tc}: FAILED — {e}")

if __name__ == "__main__":
    main()
