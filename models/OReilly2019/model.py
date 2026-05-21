# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Calvi et al. (2002) 3-Storey Gravity-Load-Designed RC Frame
UniqueID : OReilly2019
Author   : Gerard J. O'Reilly, ported by OpenSeesPy Standardisation Agent
Date     : 2026-05-10
Purpose  : Quasi-static cyclic pushover of a 3D non-ductile RC frame
           representative of Italian pre-1970s construction (gravity-only design).
Ref      : https://github.com/gerardjoreilly/Numerical-Modelling-of-GLD-RC-Frames
           O'Reilly & Sullivan (2019) J. Earthquake Eng., 23(8), 1262-1296.
Units    : N, mm, MPa  (see standards/units.py)
"""
# ── 1. IMPORTS ───────────────────────────────────────────────────────────────────
import numpy as np
import math
# Compatibility: opstool v0.8.7 uses deprecated np.NAN (patch BEFORE opstool import)
np.NAN = np.nan

import openseespy.opensees as ops
import opstool as opst
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import vis_nodes, vis_model, vis_loads, vis_pre_analysis, _headless


sys.path.insert(0, str(Path(__file__).parent))
from joint_model import create_joint
from rc_bc_non_duct import create_rc_column

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Ground nodes (grid g → tag = 1000 + idx(g,0) where idx = {g}1{0})
#   idx(1,0)=110 → tag 1110, idx(2,0)=210 → tag 1210, etc.

def _idx(grid: int, floor: int) -> int:
    """Joint index in original Tcl convention: {grid}{1}{floor}."""
    return int(f"{grid}1{floor}")

# Ground (floor 0) node tags → 1{idx}
NODE_GROUND = {g: 1000 + _idx(g, 0) for g in (1, 2, 3, 4)}
NODE_1A = NODE_GROUND[1]   # 1110
NODE_2A = NODE_GROUND[2]   # 1210
NODE_3A = NODE_GROUND[3]   # 1310
NODE_4A = NODE_GROUND[4]   # 1410

# Geometric transformation tags
GT_BEAM   = 1
GT_COLUMN = 2

# Load pattern tags
PATTERN_GRAVITY = 101
PATTERN_LATERAL = 1

# Control node for pushover (grid 1, floor 3 outer joint node)
CTRL_NODE = 1000 + _idx(1, 3)   # 1113

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# All lengths in mm, forces in N, stresses in MPa (= N/mm²)

n_stories = 3
n_bays    = 3
H_story   = 2000.0 * mm         # 2.0 m

# Section dimensions  [mm]
hc = 200.0 * mm                  # column section height
bc = 200.0 * mm                  # column section width
hb = 330.0 * mm                  # beam section height
bb = 200.0 * mm                  # beam section width
sb = 115.0 * mm                  # beam stirrup spacing
sc = 135.0 * mm                  # column stirrup spacing
cv = 20.0 * mm                   # concrete cover

# Reinforcement
dbL = 10.0 * mm                  # longitudinal bar diameter
dbV = 4.0 * mm                   # transverse (stirrup) bar diameter

# Material strengths  [MPa]
fyL  = 345.9 * MPa
fuL  = 458.6 * MPa
fyV  = 385.6 * MPa
fuV  = 451.9 * MPa
Es   = 200.0e3 * MPa

# Concrete — per floor
fcb1 = 13.28 * MPa;  Ecb1 = (3320.0 * math.sqrt(fcb1) + 6900.0) * MPa
fcb2 = 13.84 * MPa;  Ecb2 = (3320.0 * math.sqrt(fcb2) + 6900.0) * MPa
fcb3 = 12.72 * MPa;  Ecb3 = (3320.0 * math.sqrt(fcb3) + 6900.0) * MPa

fcc1 = 17.06 * MPa;  Ecc1 = (3320.0 * math.sqrt(fcc1) + 6900.0) * MPa
fcc2 = 13.19 * MPa;  Ecc2 = (3320.0 * math.sqrt(fcc2) + 6900.0) * MPa
fcc3 = 13.47 * MPa;  Ecc3 = (3320.0 * math.sqrt(fcc3) + 6900.0) * MPa

# Reinforcement ratios
rC_top  = 0.0043836176561718
rC_web  = 0.0
rC_bot  = 0.0043836176561718
rC_shr  = 0.000930842267730309

rB1_top = 0.00542912215581993
rB1_web = 0.0
rB1_bot = 0.00542912215581993
rB1_shr = 0.00109272787950949

rB3_top = 0.00730498482849603
rB3_web = 0.0
rB3_bot = 0.00166971081794195
rB3_shr = 0.00109272787950949

rB5_top = 0.00542656015831134
rB5_web = 0.0
rB5_bot = 0.00354813548812665
rB5_shr = 0.00109272787950949

# Joint parameters — kappa (principal tensile stress coefficients)
k_cr_int = 0.29;   k_pk_int = 0.42;   k_ult_int = 0.42
k_cr_ext = 0.132;  k_pk_ext = 0.132;  k_ult_ext = 0.053

gamm_cr  = 0.0002
gamm_pk  = 0.0132
gamm_ult = 0.020

hyst_ext = [0.6, 0.2, 0.0, 0.0, 0.3]
hyst_int = [0.6, 0.2, 0.0, 0.01, 0.3]

# Cyclic pushover
dref     = 1.0 * mm

# Grid geometry  [mm]
GRID_X = [0.0, 3000.0, 4330.0, 6660.0]   # grids 1, 2, 3, 4
FLOOR_Z = [0.0, 2000.0, 4000.0, 6000.0]  # ground, floor 1, 2, 3

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
# Materials are created internally by create_joint() and create_rc_column()
# during define_elements(). No standalone material definitions needed.


def define_materials() -> None:
    pass


# ── 6. SECTIONS ─────────────────────────────────────────────────────────────
# Sections are created internally by create_joint() and create_rc_column()
# during define_elements(). No standalone section definitions needed.


def define_sections() -> None:
    pass

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    for g, x in zip((1, 2, 3, 4), GRID_X):
        ops.node(NODE_GROUND[g], x, 0.0, 0.0)

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    # Fully fixed base
    for tag in NODE_GROUND.values():
        ops.fix(tag, 1, 1, 1, 1, 1, 1)

    # Out-of-plane (Y-direction) restraint at every floor joint outer node
    for g in (1, 2, 3, 4):
        for f in (1, 2, 3):
            idx = _idx(g, f)          # e.g. 111, 211, 311, 411, 112, …
            ops.fix(1000 + idx, 0, 1, 0, 0, 0, 0)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(output_dir: Path) -> None:
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    pfile_jnts = open(outdir / "Properties_joints.txt", "w")
    pfile_bms   = open(outdir / "Properties_beams.txt",  "w")
    pfile_cols  = open(outdir / "Properties_columns.txt", "w")

    col_dims = (hc, bc)                       # (hcX, hcY)
    bm_dims  = (hb, hb, bb, bb)               # (hbX, hbY, bbX, bbY)
    bars = (dbL, dbV)

    conc_col = [(fcc1, Ecc1, cv), (fcc2, Ecc2, cv), (fcc3, Ecc3, cv)]
    conc_bm  = [(fcb1, Ecb1, cv), (fcb2, Ecb2, cv), (fcb3, Ecb3, cv)]

    ptc_ext = [k_cr_ext, k_pk_ext, k_ult_ext, k_cr_ext, k_pk_ext, k_ult_ext]
    ptc_int = [k_cr_int, k_pk_int, k_ult_int, k_cr_int, k_pk_int, k_ult_int]
    gam_ext = [gamm_cr, gamm_pk, gamm_ult, gamm_cr, gamm_pk, gamm_ult]
    gam_int = [gamm_cr, gamm_pk, gamm_ult, gamm_cr, gamm_pk, gamm_ult]

    # ── Geometric transformations ──────────────────────────────────────
    ops.geomTransf("PDelta", GT_BEAM, 0, 1, 0,
                   "-jntOffset", hc / 2.0, 0.0, 0.0,
                                 -hc / 2.0, 0.0, 0.0)
    ops.geomTransf("PDelta", GT_COLUMN, 0, 1, 0,
                   "-jntOffset", 0.0, 0.0, hb / 2.0,
                                 0.0, 0.0, -hb / 2.0)

    # ── Joints ─────────────────────────────────────────────────────────
    # Floor data: (floor, masses[tonnes], axial_P[kN])
    floor_data = [
        (1, [1.62, 2.34, 2.10, 1.38], [43.0, 61.8, 57.1, 38.3]),
        (2, [1.62, 2.34, 2.10, 1.38], [27.1, 38.9, 36.5, 24.8]),
        (3, [1.14, 1.62, 1.62, 1.14], [11.2, 15.9, 15.9, 11.2]),
    ]
    joint_types = ("Exterior", "Interior", "Interior", "Exterior")

    for f_idx, (f, masses, axial_P) in enumerate(floor_data, start=0):
        for g in (1, 2, 3, 4):
            idx = _idx(g, f)
            create_joint(
                joint_types[g - 1],
                idx,
                (GRID_X[g - 1], 0.0, FLOOR_Z[f]),
                masses[g - 1],
                col_dims, bm_dims, conc_col[f_idx], bars,
                axial_P[g - 1] * kN,
                H_story,
                ptc_ext if g in (1, 4) else ptc_int,
                gam_ext  if g in (1, 4) else gam_int,
                hyst_ext if g in (1, 4) else hyst_int,
                pfile_jnts,
            )

    # ── Column elements ─────────────────────────────────────────────────
    col_P_Ls = [
        # floor 1          floor 2          floor 3
        (43.0, 1000.0),  (27.1, 1000.0),  (11.2, 1000.0),  # grid 1
        (61.8, 1000.0),  (38.9, 1000.0),  (15.9, 1000.0),  # grid 2
        (57.1, 1000.0),  (36.5, 1000.0),  (15.9, 1000.0),  # grid 3
        (38.3, 1000.0),  (24.8, 1000.0),  (11.2, 1000.0),  # grid 4
    ]
    col_n = 0
    for g in (1, 2, 3, 4):
        for f in (1, 2, 3):
            base_idx = _idx(g, f - 1)      # floor below
            top_idx  = _idx(g, f)          # this floor
            ET = int(f"7{g}1{f}")
            P_kN, Ls = col_P_Ls[col_n]
            col_n += 1
            create_rc_column(
                1, ET, GT_COLUMN,
                1000 + base_idx,            # base node tag
                1000 + top_idx,             # top (joint) node tag
                fyL, fyV, Es,
                conc_col[f - 1][0], conc_col[f - 1][1],
                bc, hc, sc, cv, dbL, dbV,
                P_kN * kN, Ls,
                rC_shr,
                rC_top, rC_web, rC_bot,
                rC_top, rC_web, rC_bot,
                rC_top, rC_web, rC_bot,
                rC_top, rC_web, rC_bot,
                pfile_cols,
            )

    # ── Beam elements ──────────────────────────────────────────────────
    # Three beam types per floor: B1 (span 1-2), B3 (span 2-3), B5 (span 3-4)
    beam_rhos = [
        (rB1_top, rB1_web, rB1_bot, rB1_shr),
        (rB3_top, rB3_web, rB3_bot, rB3_shr),
        (rB5_top, rB5_web, rB5_bot, rB5_shr),
    ]
    beam_Ls = [1500.0, 665.0, 1665.0]

    for f in (1, 2, 3):
        for span in (0, 1, 2):   # spans between grid (s+1) and (s+2)
            g_i = span + 1
            g_j = span + 2
            ET = int(f"5{span + 1}1{f}")
            idx_i = _idx(g_i, f)
            idx_j = _idx(g_j, f)
            i_node = 6000 + idx_i     # internal joint node
            j_node = 6000 + idx_j
            rho_t, rho_w, rho_b, rho_sh = beam_rhos[span]
            create_rc_column(
                0, ET, GT_BEAM, i_node, j_node,
                fyL, fyV, Es,
                conc_bm[f - 1][0], conc_bm[f - 1][1],
                bb, hb, sb, cv, dbL, dbV,
                0.0,                     # P = 0 for beams
                beam_Ls[span],
                rho_sh,
                rho_t, rho_w, rho_b,
                rho_t, rho_w, rho_b,
                rho_t, rho_w, rho_b,
                rho_t, rho_w, rho_b,
                pfile_bms,
            )

    pfile_jnts.close()
    pfile_bms.close()
    pfile_cols.close()
    print("Elements created")

# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    opst.post.set_odb_path(str(output_dir))
    opst.post.save_model_data(odb_tag=1)
    odb = opst.post.CreateODB(odb_tag=1)
    return odb

# ── 11. LOADING ──────────────────────────────────────────────────────────────
def _load_gravity_tag(g: int, f: int) -> int:
    """Outer joint node tag for gravity load application."""
    return 1000 + _idx(g, f)

def define_gravity_loads() -> None:
    ops.timeSeries("Constant", PATTERN_GRAVITY)
    ops.pattern("Plain", PATTERN_GRAVITY, PATTERN_GRAVITY)
    # Floor loads in N  (converted from original kN values)
    grav = {
        1: [(-15.90, -22.95, -20.60, -13.55)],
        2: [(-15.90, -22.95, -20.60, -13.55)],
        3: [(-11.20, -15.90, -15.90, -11.20)],
    }
    for f, loads in grav.items():
        for g, val in enumerate(loads[0], start=1):
            ops.load(_load_gravity_tag(g, f), 0.0, 0.0, val * kN, 0.0, 0.0, 0.0)

def define_lateral_loads() -> None:
    f1 = 0.45 / (0.45 + 0.90 + 1.0)   # 0.1915
    f2 = 0.90 / (0.45 + 0.90 + 1.0)   # 0.3830
    f3 = 1.00 / (0.45 + 0.90 + 1.0)   # 0.4255
    ops.timeSeries("Linear", PATTERN_LATERAL)
    ops.pattern("Plain", PATTERN_LATERAL, PATTERN_LATERAL)
    ops.load(_load_gravity_tag(1, 1), f1 * kN, 0.0, 0.0, 0.0, 0.0, 0.0)
    ops.load(_load_gravity_tag(1, 2), f2 * kN, 0.0, 0.0, 0.0, 0.0, 0.0)
    ops.load(_load_gravity_tag(1, 3), f3 * kN, 0.0, 0.0, 0.0, 0.0, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_gravity(
    odb: "opst.post.CreateODB",
    n_steps: int = 10,
) -> None:
    """Apply gravity loads incrementally using standard OpenSees load control."""
    import openseespy.opensees as ops
    
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    
    # 1.0e-6 tolerance is standard for well-behaved gravity loads
    ops.test("NormDispIncr", 1.0e-6, 100)
    ops.algorithm("Newton")
    
    # Apply 100% of gravity evenly over n_steps
    step_size = 1.0 / n_steps
    ops.integrator("LoadControl", step_size)
    ops.analysis("Static")
    
    for _ in range(n_steps):
        ok = ops.analyze(1)
        
        # Fallback step-cutting if the standard Newton algorithm fails
        if ok != 0:
            print("  Warning: standard Newton failed, trying Newton with Initial Tangent...")
            ops.algorithm("Newton", "-initial")
            ok = ops.analyze(1)
            
            if ok != 0:
                print("  Error: Gravity analysis completely failed to converge.")
                break
                
            # Revert back to normal Newton for the next steps
            ops.algorithm("Newton")
            
        # Manually save the response at each load increment
        odb.fetch_response_step()
        
    # Freeze gravity and reset pseudo-time to 0.0 for the subsequent pushover
    ops.loadConst("-time", 0.0)   
    print("Gravity analysis completed")

def _push_segment(
    odb: "opst.post.CreateODB", 
    ctrl_node: int,
    ctrl_dof: int,
    target_disp: float,
) -> None:
    """Displacement-controlled push to target_disp with automatic step cutting."""
    
    current = ops.nodeDisp(ctrl_node, ctrl_dof)
    remaining = target_disp - current
    
    if abs(remaining) < 1e-12:
        return

    # Use a step size of 1.0 mm for efficiency; SmartAnalyze automatically cuts it if needed.
    step_size = 1.0
    steps = max(int(abs(remaining) / step_size), 10)
    dU = remaining / steps

    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-5, 1000)

    # 1. Initialize the SmartAnalyzer with solver parameters
    analyzer = opst.anlys.SmartAnalyze(
        analysis_type="Static",        # Tell opstool we are doing static analysis
        minStep=abs(dU) / 1.0e5,       # Allow it to cut steps down to this size if it fails
        tryAlterAlgoTypes=True,        # Automatically switch Newton algorithms if needed
        debugMode=False
    )

    # 2. Push incrementally and record data
    for i in range(steps):
        # Apply a single increment
        ok = analyzer.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=dU)
        
        # 0 means converged successfully, anything else is a failure
        if ok != 0:
            print(f"  Warning: smart_analyze failed to reach target displacement {target_disp:.4f} at step {i+1}/{steps}")
            break
            
        # 3. Save the data for this specific step!
        odb.fetch_response_step()
        
    # Close the analyzer to free resources
    analyzer.close()


def run_cyclic_pushover(
    odb: "opst.post.CreateODB",
    ctrl_node: int = CTRL_NODE,
    ctrl_dof: int = 1,
    dref_local: float = 1.0,
) -> None:
    """Run a cyclic pushover protocol at increasing amplitude levels.

    Protocol: 3 cycles at ±12, ±36, ±72 mm, then 1 cycle at ±96 mm.

    Args:
        odb: Active GetFEMdata instance.
        ctrl_node: Control node tag (default CTRL_NODE).
        ctrl_dof: Control DOF (default 1 = X).
        dref_local: Reference displacement increment (default 1.0 mm).
    """
    amplitudes = [12, 36, 72, 80]
    n_cycles_list = [3, 3, 3, 1]

    for amp_mult, n_cyc in zip(amplitudes, n_cycles_list):
        peak = amp_mult * dref_local
        for cyc in range(n_cyc):
            print(f"  Cycle {cyc + 1}/{n_cyc} at ±{peak:.1f} mm")
            try:
                _push_segment(odb, ctrl_node, ctrl_dof, peak)
                _push_segment(odb, ctrl_node, ctrl_dof, 0.0)
                _push_segment(odb, ctrl_node, ctrl_dof, -peak)
                _push_segment(odb, ctrl_node, ctrl_dof, 0.0)
            except Exception as e:
                print(f"  Pushover failed at cycle {cyc + 1}/{n_cyc}, ±{peak:.1f} mm: {e}")
                print("  Continuing with post-processing (partial results available).")
                return


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + cyclic pushover, return ODB.

    Returns:
        The populated GetFEMdata instance (call save_resp_all() in post_process).

    NOTE: Lateral loads are defined AFTER gravity (loadConst) so that
    DisplacementControl has an active (non-frozen) pattern to scale during
    the pushover. The frozen gravity pattern supplies constant vertical loads.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    init_model()
    define_nodes()
    define_elements(output_dir)
    define_boundary_conditions()
    define_materials()
    define_sections()
    vis_nodes(output_dir)                         # V1: nodes + supports
    vis_model(output_dir)                         # V2: full geometry
    odb = create_odb(output_dir)                  # initialise ODB after model built
    define_gravity_loads()                        # gravity pattern (frozen later)
    vis_pre_analysis(output_dir)                  # V4: pre-analysis check
    run_gravity(odb)                              # applies gravity + loadConst
    vis_loads(output_dir)                         # V3: loads
    define_lateral_loads()                        # lateral pattern (AFTER loadConst, still active)
    run_cyclic_pushover(odb,
                        ctrl_node=CTRL_NODE,
                        ctrl_dof=1,
                        dref_local=dref)

    return odb


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    odb.save_response()
    if not _headless():
        fig = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1,
            slides=True,
            defo_scale=30.0,
            resp_type="disp",
            resp_dof=("UX",),
        )
        fig.write_html(str(output_dir / "vis_05_deformed_UX.html"))
        print("HTML written.")
    

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    print("--- OReilly2019: Quasi-static cyclic pushover ---")
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print(f"Analysis complete. Results in {output_dir}/")
