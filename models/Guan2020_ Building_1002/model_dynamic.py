# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 9-story 3-bay 2D steel SMF — DYNAMIC time-history analysis
UniqueID : Guan2020_Building_1002
Author   : Xingquan Guan, Henry Burton, Mehrdad Shokrabadi (2020),
           ported by OpenSeesPy Standardisation Agent
Date     : 2026-06-06
Purpose  : Nonlinear dynamic time-history analysis under ground motion
           excitation with Rayleigh damping (2% on modes 1 & 3).
Ref      : Guan, X., Burton, H., Shokrabadi, M. (2020). DesignSafe-CI,
           DOI: 10.17603/ds2-8yc7-1285.
Units    : N, mm, MPa  (see standards/units.py)
"""

import openseespy.opensees as ops
import opstool as opst
import numpy as np
import sys, csv, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo, vis_anim, _headless


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION DATABASE
# ══════════════════════════════════════════════════════════════════════════════

def _load_section_db(csv_path):
    db = {}
    with open(csv_path, encoding="ISO-8859-1") as f:
        reader = csv.reader(f)
        next(reader); next(reader)
        for row in reader:
            if len(row) < 130: continue
            name = row[2].strip()
            if not name or name in db: continue
            try:
                db[name] = (
                    float(row[6])*inch, float(row[5])*inch**2,
                    float(row[11])*inch, float(row[16])*inch, float(row[19])*inch,
                    float(row[38])*inch**4, float(row[42])*inch**4,
                    float(row[39])*inch**3, float(row[43])*inch**3,
                    float(row[45])*inch, float(row[49])*inch**4)
            except (ValueError, IndexError): continue
    return db

_DB_PATH = (Path(__file__).parent / "ref" / "BaselineFiles"
            / "DynamicAnalysis" / "Database.csv")
SECTION_DB = _load_section_db(_DB_PATH)

# ══════════════════════════════════════════════════════════════════════════════
#  PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════

bay_width = 40.00*ft; h_first = 26.00*ft; h_typical = 13.00*ft
n_stories = 9; n_bays = 3; n_cols = n_bays + 1; n_floors = n_stories + 1

Es_val = 29000.0*ksi; Fy_val = 50.0*ksi; n_stiff = 10.0
large_stiff = 1.0e12*ksi; negligible = 1.0e-12*ksi
A_rigid = 1.0e8*inch**2; I_rigid = 1.0e8*inch**4
g_acc = 386.4*inch/sec**2

MAT_TRUSS = 600; MAT_STIFF = 1200
TRANS_PDELTA = 1; TRANS_LINEAR = 2

_y_level = [0.0]
for lvl in range(1, n_floors+1):
    if lvl == 1: _y_level.append(0.0)
    elif lvl == 2: _y_level.append(h_first)
    else: _y_level.append(_y_level[-1] + h_typical)

_beam_sec_names = {
    2:"W36X262",3:"W36X262",4:"W36X194",5:"W36X194",
    6:"W27X217",7:"W27X217",8:"W27X178",9:"W27X178",10:"W21X93"}
_col_ext_names = {
    1:"W14X730",2:"W14X730",3:"W14X665",4:"W14X550",
    5:"W14X455",6:"W14X370",7:"W14X283",8:"W14X211",9:"W14X145"}
_col_int_names = {
    1:"W14X730",2:"W14X730",3:"W14X665",4:"W14X550",
    5:"W14X500",6:"W14X398",7:"W14X342",8:"W14X257",9:"W14X193"}

# Dynamic parameters
DAMP_RATIO = 0.02       # 2% Rayleigh damping
GM_DT = 0.01             # time step (s)
GM_NPTS = 2000           # 20 s ground motion
GM_SCALE = 1.0           # scale factor
GM_DIR = 1               # X-direction excitation
ODB_EVERY_N = 5          # throttle ODB collection

n_steps_gravity = 10
n_eigen_modes = 3

# ══════════════════════════════════════════════════════════════════════════════
#  NODE TAGGING
# ══════════════════════════════════════════════════════════════════════════════

def _jt(c,l): return int(f"{c}{l}00")
def _jl(c,l): return int(f"{c}{l}01")
def _jr(c,l): return int(f"{c}{l}02")
def _jt_top(c,l): return int(f"{c}{l}03")
def _jb(c,l): return int(f"{c}{l}04")

def _col_sec_name(story,col):
    d = _col_ext_names if col in (1,n_cols) else _col_int_names
    idx = min(story, len(d))
    return d.get(idx, d.get(len(d),"W14X145"))

def _beam_sec_name(lvl):
    return _beam_sec_names.get(lvl, "W21X93")

# ══════════════════════════════════════════════════════════════════════════════
#  HINGE MATERIALS (Steel01 — IMK-calibrated)
# ══════════════════════════════════════════════════════════════════════════════

def create_hinge_material(mat_tag, K0, n_factor, a_men, My, Lambda,
                          theta_p, theta_pc, residual, theta_u):
    K_eff = K0 * n_factor
    b = a_men
    ops.uniaxialMaterial("Steel01", mat_tag, My, K_eff, b)

def beam_imk_params(sec, L_beam):
    d,A,bf,tw,tf,Ix,Iy,Zx,Zy,ry,J = sec
    K0 = 6.0*Es_val*Ix/L_beam; My = Zx*Fy_val
    h = d-2.0*tf; fy_mpa = Fy_val/MPa
    Lambda = (536.0*(h/tw)**(-1.26)*(bf/2.0/tf)**(-0.525)*
              (fy_mpa/355.0)**(-0.291)*(L_beam/ry)**(-0.130))
    theta_p = (0.318*(h/tw)**(-0.55)*(bf/2.0/tf)**(-0.345)*
               (fy_mpa/355.0)**(-0.130)*(d/mm/533.0)**(-0.330)*
               (L_beam/d)**(0.090)*(L_beam/ry)**(-0.0230))
    theta_pc = (7.50*(h/tw)**(-0.61)*(bf/2.0/tf)**(-0.71)*
                (fy_mpa/355.0)**(-0.320)*(d/mm/533.0)**(-0.161)*
                (L_beam/ry)**(-0.110))
    a_s = My*0.11/K0/theta_p; residual = 0.25
    theta_u = min(0.06, My/K0 + theta_p*theta_pc)
    return K0, n_stiff, a_s, My, Lambda, theta_p, theta_pc, residual, theta_u

def column_imk_params(sec, L_col):
    d,A,bf,tw,tf,Ix,Iy,Zx,Zy,ry,J = sec
    K0 = 6.0*Es_val*Ix/L_col; My = Zx*Fy_val
    h = d-2.0*tf; fy_mpa = Fy_val/MPa
    Lambda = (536.0*(h/tw)**(-1.26)*(bf/2.0/tf)**(-0.525)*
              (fy_mpa/355.0)**(-0.291)*(L_col/ry)**(-0.130))*0.8
    theta_p = (0.318*(h/tw)**(-0.55)*(bf/2.0/tf)**(-0.345)*
               (fy_mpa/355.0)**(-0.130)*(d/mm/533.0)**(-0.330)*
               (L_col/d)**(0.090)*(L_col/ry)**(-0.0230))*0.7
    theta_pc = (7.50*(h/tw)**(-0.61)*(bf/2.0/tf)**(-0.71)*
                (fy_mpa/355.0)**(-0.320)*(d/mm/533.0)**(-0.161)*
                (L_col/ry)**(-0.110))*1.5
    a_s = My*0.06/K0/theta_p; residual = 0.25
    theta_u = min(0.4, My/K0 + theta_p*theta_pc)
    return K0, n_stiff, a_s, My, Lambda, theta_p, theta_pc, residual, theta_u

# ══════════════════════════════════════════════════════════════════════════════
#  GROUND MOTION
# ══════════════════════════════════════════════════════════════════════════════

def generate_synthetic_gm(dt, npts):
    t = np.arange(npts)*dt
    t0 = 5.0; freq = 2.5
    a = (1.0 - 2.0*(np.pi*freq*(t-t0))**2)*np.exp(-(np.pi*freq*(t-t0))**2)
    n_taper = int(0.5/dt)
    w = np.ones(npts)
    w[:n_taper] = np.linspace(0,1,n_taper)
    w[-n_taper:] = np.linspace(1,0,n_taper)
    a *= w
    a *= (0.3*9810.0)/max(abs(a)) if max(abs(a))>1e-12 else 1.0
    out_dir = Path(__file__).parent / "ground_motions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "synthetic_gm.acc"
    np.savetxt(out_path, a, fmt="%.6e")
    print(f"  Synthetic GM: {out_path} ({npts}pts, dt={dt}s, peak={max(abs(a)):.0f} mm/s²)")
    return out_path

# ══════════════════════════════════════════════════════════════════════════════
#  MODEL BUILDING
# ══════════════════════════════════════════════════════════════════════════════

def init_model():
    ops.wipe(); ops.model("BasicBuilder","-ndm",2,"-ndf",3)

def define_materials():
    ops.uniaxialMaterial("Elastic", MAT_TRUSS, Es_val)
    ops.uniaxialMaterial("Elastic", MAT_STIFF, large_stiff)

def define_transformations():
    ops.geomTransf("PDelta", TRANS_PDELTA); ops.geomTransf("Linear", TRANS_LINEAR)

def define_all_nodes():
    for col in range(1, n_cols+1):
        x = (col-1)*bay_width
        for lvl in range(1, n_floors+1):
            y = _y_level[lvl]
            for tag in (_jt(col,lvl), _jl(col,lvl), _jr(col,lvl),
                        _jt_top(col,lvl), _jb(col,lvl)):
                ops.node(tag, x, y)
    for lvl in range(1, n_floors+1):
        ops.node(50+lvl, n_cols*bay_width, _y_level[lvl])
    print(f"  {n_floors*n_cols*5 + n_floors} nodes")

def define_fixities():
    for col in range(1, n_cols+1): ops.fix(_jt(col,1), 1,1,1)
    ops.fix(51, 1,1,0)

def define_joint_constraints():
    for col in range(1, n_cols+1):
        for lvl in range(1, n_floors+1):
            master = _jt(col,lvl)
            for slave in (_jl(col,lvl),_jr(col,lvl),_jt_top(col,lvl),_jb(col,lvl)):
                ops.equalDOF(master, slave, 1,2,3)
    for lvl in range(2, n_floors+1):
        master = _jt(1,lvl)
        for col in range(2, n_cols+1): ops.equalDOF(master, _jt(col,lvl), 1)
        ops.equalDOF(master, 50+lvl, 1)

def define_beam_hinge_materials():
    for lvl in range(2, n_floors+1):
        create_hinge_material(7000000+lvl*100, *beam_imk_params(SECTION_DB[_beam_sec_name(lvl)], bay_width))

def define_column_hinge_materials():
    for story in range(1, n_stories+1):
        L_col = h_first if story==1 else h_typical
        for col in range(1, n_cols+1):
            create_hinge_material(8000000+story*100+col, *column_imk_params(SECTION_DB[_col_sec_name(story,col)], L_col))

def define_beams():
    for lvl in range(2, n_floors+1):
        sec = SECTION_DB[_beam_sec_name(lvl)]
        A_beam, Ix_beam = sec[1], sec[5]
        I_eff = (n_stiff+1.0)/n_stiff*Ix_beam
        for col in range(1, n_cols):
            ops.element("elasticBeamColumn", int(f"{col}{lvl}{col+1}{lvl}1"),
                        _jr(col,lvl), _jl(col+1,lvl), A_beam, Es_val, I_eff, TRANS_LINEAR)
        ops.element("truss", int(f"{n_cols}{lvl}{50+lvl}"),
                    _jr(n_cols,lvl), 50+lvl, A_rigid, MAT_TRUSS)

def define_columns():
    for story in range(1, n_stories+1):
        lvl_below, lvl_above = story, story+1
        L_col = h_first if story==1 else h_typical
        for col in range(1, n_cols+1):
            sec = SECTION_DB[_col_sec_name(story,col)]
            A_col, Ix_col = sec[1], sec[5]
            I_eff = (n_stiff+1.0)/n_stiff*Ix_col
            ops.element("elasticBeamColumn", int(f"{col}{story}{col}{story+1}1"),
                        _jt_top(col,lvl_below), _jb(col,lvl_above),
                        A_col, Es_val, I_eff, TRANS_PDELTA)
    for lvl in range(1, n_floors):
        ops.element("elasticBeamColumn", int(f"99{lvl}{lvl+1}1"),
                    50+lvl, 50+lvl+1, A_rigid, Es_val, I_rigid, TRANS_PDELTA)

def define_beam_hinges():
    for lvl in range(2, n_floors+1):
        mat_tag = 7000000+lvl*100
        for col in range(1, n_cols+1):
            if col > 1:
                ops.element("zeroLength", int(f"{col}{lvl}{col-1}{lvl}7"),
                            _jt(col,lvl), _jl(col,lvl),
                            "-mat", MAT_STIFF, MAT_STIFF, mat_tag, "-dir",1,2,3)
            if col < n_cols:
                ops.element("zeroLength", int(f"{col}{lvl}{col+1}{lvl}7"),
                            _jt(col,lvl), _jr(col,lvl),
                            "-mat", MAT_STIFF, MAT_STIFF, mat_tag, "-dir",1,2,3)

def define_column_hinges():
    for story in range(1, n_stories+1):
        lvl_below = story
        for col in range(1, n_cols+1):
            mat_tag = 8000000+story*100+col
            ops.element("zeroLength", int(f"{col}{lvl_below}{col}{lvl_below}2"),
                        _jt(col,lvl_below), _jt_top(col,lvl_below),
                        "-mat", MAT_STIFF, MAT_STIFF, mat_tag, "-dir",1,2,3)

def define_masses():
    floor_weight = 1800.0*kip
    mass_per_node = floor_weight/(n_cols+1)/g_acc
    for lvl in range(2, n_floors+1):
        for col in range(1, n_cols+1):
            ops.mass(_jt(col,lvl), mass_per_node, negligible, negligible)
        ops.mass(50+lvl, mass_per_node, negligible, negligible)

def define_gravity_loads():
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 101, 1)
    beam_dead = 0.066667*(kip/inch)
    lean_dead = 900.0*kip/n_stories
    for lvl in range(2, n_floors+1):
        for col in range(1, n_cols):
            ops.eleLoad("-ele", int(f"{col}{lvl}{col+1}{lvl}1"),
                       "-type","-beamUniform", -beam_dead, 0.0)
        ops.load(50+lvl, 0.0, -lean_dead, 0.0)

# ══════════════════════════════════════════════════════════════════════════════
#  ODB
# ══════════════════════════════════════════════════════════════════════════════

def create_odb(output_dir, odb_tag=1):
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=odb_tag)
    odb.save_model_data()
    return odb

# ══════════════════════════════════════════════════════════════════════════════
#  ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def run_gravity(odb, n_steps=n_steps_gravity):
    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("BandGeneral")
    ops.test("NormDispIncr", 1e-6, 20, 2); ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0/n_steps); ops.analysis("Static")
    for _ in range(n_steps):
        ops.analyze(1); odb.fetch_response_step()
    ops.loadConst("-time", 0.0); ops.wipeAnalysis()

def run_eigenvalue():
    eigenvalues = ops.eigen(n_eigen_modes)
    periods = [2.0*np.pi/np.sqrt(lam) for lam in eigenvalues]
    omega = [2.0*np.pi/T for T in periods]
    for i,(T,w) in enumerate(zip(periods,omega),1):
        print(f"  Mode {i}: T={T:.4f}s, ω={w:.4f} rad/s")
    return periods, omega

def run_dynamic(odb, periods, omega, gm_file, dt, npts, scale=1.0):
    # Rayleigh damping: mass + stiffness proportional
    omega_i = omega[0]         # mode 1
    omega_j = omega[2]         # mode 3
    alpha_m = DAMP_RATIO*2.0*omega_i*omega_j/(omega_i+omega_j)
    alpha_k = DAMP_RATIO*2.0/(omega_i+omega_j)*(n_stiff+1.0)/n_stiff
    ops.rayleigh(alpha_m, 0.0, alpha_k, 0.0)
    print(f"  Rayleigh: α_M={alpha_m:.6f}, β_K={alpha_k:.6f} (ζ={DAMP_RATIO:.0%} on modes 1,3)")

    # Ground motion
    ops.timeSeries("Path", 10, "-dt", dt, "-filePath", str(gm_file), "-factor", scale)
    ops.pattern("UniformExcitation", 200, GM_DIR, "-accel", 10)

    # Transient analysis
    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("BandGeneral")
    ops.integrator("Newmark", 0.5, 0.25)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True, algoTypes=[40,10,20,30,50],
        tryAddTestTimes=True, testIterTimesMore=[50,100],
        relaxation=0.5, minStep=1.0e-6)
    segs = analysis.transient_split(npts)
    for i, _ in enumerate(segs):
        ok = analysis.TransientAnalyze(dt)
        if ok < 0: print(f"  Dynamic failed at step {i}"); break
        if i % ODB_EVERY_N == 0: odb.fetch_response_step()
    analysis.close()

# ══════════════════════════════════════════════════════════════════════════════
#  ORCHESTRATION
# ══════════════════════════════════════════════════════════════════════════════

def run_analysis(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    print("Building model...")
    init_model(); define_materials(); define_transformations()
    define_all_nodes(); define_fixities(); define_joint_constraints()
    if not _headless(): vis_nodes(output_dir)
    print("  Hinge materials...")
    define_beam_hinge_materials(); define_column_hinge_materials()
    print("  Elements...")
    define_beams(); define_columns()
    print("  Hinges...")
    define_beam_hinges(); define_column_hinges()
    print("  Masses...")
    define_masses()
    if not _headless(): vis_model(output_dir)
    odb = create_odb(output_dir)

    print("  Gravity...")
    define_gravity_loads()
    if not _headless(): vis_loads(output_dir)
    run_gravity(odb)

    print("  Eigenvalue...")
    periods, omega = run_eigenvalue()

    print("  Ground motion...")
    gm_file = generate_synthetic_gm(GM_DT, GM_NPTS)

    if not _headless(): vis_pre_analysis(output_dir)
    print("  Dynamic analysis...")
    run_dynamic(odb, periods, omega, gm_file, GM_DT, GM_NPTS, GM_SCALE)
    return odb

def post_process(odb, output_dir):
    odb.save_response()
    if not _headless():
        vis_defo(output_dir, filename="vis_05_deformed.html")
        vis_anim(output_dir, filename="vis_06_dynamic_animation.html",
                 odb_tag=1, defo_scale=10.0, resp_dof=("UX","UY"),
                 show_undeformed=True)

if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
    print(f"Building_1002 dynamic analysis complete. Output in {output_dir}")
