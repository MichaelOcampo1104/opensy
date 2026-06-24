# ── 0. FILE HEADER ──────────────────────────────────────────
"""
Model: F12-D100
UniqueID: CookDustin_F12-D100
Author: auto-converted from F12-D100_ref/model.tcl
Date:   2026-06-23
Purpose:
    2D 4-bay × 12-story RC SMF with concentrated plasticity
    hinges (IMKPeakOriented) at beam and column ends.
    ElasticBeamColumn + PDelta, leaning column.
    Gravity then displacement-controlled pushover.

Ref:  Cook Dustin FEMA P695 archetype "m112v5"
      (12-story drift 10 %). NHERI SimCenter pipeline.
Units: N, mm, MPa  (converted from original lb, in, psi)
"""

# ── 1. IMPORTS ──────────────────────────────────────────────
import sys
import csv
import re
from pathlib import Path
import openseespy.opensees as ops
import opstool as opst
import numpy as np

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from units import *
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo

# ── 2. TAG REGISTRY ─────────────────────────────────────────
# Fixed tags (everything else is derived from Tcl)
TS_GRAVITY = 1
PAT_GRAVITY = 1
TS_LATERAL = 2
PAT_LATERAL = 2

# ── 3. PARAMETERS ───────────────────────────────────────────
REF_DIR = Path(__file__).parent.parent / "F12-D100_ref"
TCL_PATH = REF_DIR / "model.tcl"

# Conversion factors:  lb·in → N·mm
LB2N = 4.4482216152605
IN2MM = 25.4
PSI2MPA = 0.006894757293168   # 1 psi = 0.00689476 MPa
LBIN2NMM = LB2N * IN2MM       # moment/stiffness
IN22MM2 = IN2MM * IN2MM
IN42MM4 = IN2MM ** 4
LBIN2_to_NMM2 = LB2N / IN2MM  # distributed load lb/in → N/mm
MASS_CONV = LB2N / IN2MM      # lb·s²/in → N·s²/mm (consistent mass unit)

# Analysis control
N_GRAV_STEPS = 10
MAX_DRIFT_RATIO = 0.10
N_PUSH_STEPS = 200

# Global dims (for drift computation)
STORY_HTS = [180.0 * IN2MM] + [156.0 * IN2MM] * 11  # mm
TOTAL_H = sum(STORY_HTS)


# ── TCL PARSER HELPERS ──────────────────────────────────────
def _parse_tcl(filepath):
    """Parse model.tcl into structured data blocks."""
    text = Path(filepath).read_text()
    lines = text.splitlines()

    data = {
        "nodes": [],
        "fix": [],
        "mass": [],
        "geom_transf": [],
        "elastic_beam": [],
        "zero_length": [],
        "uniaxial_mat": [],
    }

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("puts"):
            continue
        parts = line.split()
        if not parts:
            continue

        cmd = parts[0]
        if cmd == "node":
            tag, x, y = int(parts[1]), float(parts[2]), float(parts[3])
            data["nodes"].append((tag, x, y))
        elif cmd == "fix":
            tag = int(parts[1])
            bc = tuple(int(parts[i]) for i in range(2, min(5, len(parts))))
            data["fix"].append((tag, *bc))
        elif cmd == "mass":
            tag = int(parts[1])
            m = float(parts[2])
            data["mass"].append((tag, m))
        elif cmd == "geomTransf":
            # geomTransf PDelta 1
            ttype = parts[1]
            tag = int(parts[2])
            data["geom_transf"].append((tag, ttype))
        elif cmd == "element":
            etype = parts[1]
            if etype == "elasticBeamColumn":
                tag = int(parts[2])
                iNode, jNode = int(parts[3]), int(parts[4])
                A, E, Iz = float(parts[5]), float(parts[6]), float(parts[7])
                trans = int(parts[8])
                data["elastic_beam"].append((tag, iNode, jNode, A, E, Iz, trans))
            elif etype == "zeroLength":
                tag = int(parts[2])
                iNode, jNode = int(parts[3]), int(parts[4])
                # parse -mat and -dir flags
                mat_args = []
                dirs = []
                in_mat = False
                in_dir = False
                i = 5
                while i < len(parts):
                    p = parts[i]
                    if p == "-mat":
                        in_mat = True
                        i += 1
                        # collect mat tags until next flag
                        while i < len(parts) and not parts[i].startswith("-"):
                            mat_args.append(int(parts[i]))
                            i += 1
                        in_mat = False
                    elif p == "-dir":
                        in_dir = True
                        i += 1
                        while i < len(parts) and not parts[i].startswith("-"):
                            dirs.append(int(parts[i]))
                            i += 1
                        in_dir = False
                    else:
                        i += 1
                data["zero_length"].append((tag, iNode, jNode, mat_args, dirs))
        elif cmd == "uniaxialMaterial":
            mtype = parts[1]
            tag = int(parts[2])
            vals = [float(p) for p in parts[3:]]
            data["uniaxial_mat"].append((tag, mtype, vals))

    return data


# ── 4. MODEL INITIALISATION ─────────────────────────────────
def init_model():
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ────────────────────────────────────────────
def define_materials(tcl_data):
    for tag, mtype, vals in tcl_data["uniaxial_mat"]:
        cvals = list(vals)
        if mtype == "IMKPeakOriented":
            # Convert moment/stiffness parameters (K0, Mp) from lb·in → N·mm
            # K0: index 0 (rotational stiffness, lb·in/rad → N·mm/rad)
            if len(cvals) >= 1:
                cvals[0] *= LBIN2NMM
            # Mp values: indices 4 and 10 (positive/negative plastic moment)
            if len(cvals) >= 5:
                cvals[4] *= LBIN2NMM
            if len(cvals) >= 11:
                cvals[10] *= LBIN2NMM
        # For Elastic materials — no conversion needed (stiffness ratios already large)
        ops.uniaxialMaterial(mtype, tag, *cvals)


# ── 6. GEOMETRIC TRANSFORMATIONS ────────────────────────────
def define_geom_transf(tcl_data):
    for tag, ttype in tcl_data["geom_transf"]:
        ops.geomTransf(ttype, tag)


# ── 7. NODES ────────────────────────────────────────────────
def build_nodes(tcl_data):
    for tag, x, y in tcl_data["nodes"]:
        ops.node(tag, x * IN2MM, y * IN2MM)


# ── 8. BOUNDARY CONDITIONS ──────────────────────────────────
def define_boundary_conditions(tcl_data):
    for entry in tcl_data["fix"]:
        tag = entry[0]
        bc = entry[1:]
        while len(bc) < 3:
            bc = bc + (0,)
        ops.fix(tag, *bc[:3])


# ── 9. ELEMENTS ─────────────────────────────────────────────
def build_elements(tcl_data):
    # --- elasticBeamColumn ---
    for tag, iNode, jNode, A, E, Iz, trans in tcl_data["elastic_beam"]:
        A_mm = A * IN22MM2
        E_mpa = E * PSI2MPA
        Iz_mm4 = Iz * IN42MM4
        ops.element("elasticBeamColumn", tag, iNode, jNode, A_mm, E_mpa, Iz_mm4, trans)

    # --- zeroLength ---
    for tag, iNode, jNode, mat_args, dirs in tcl_data["zero_length"]:
        ops.element("zeroLength", tag, iNode, jNode,
                    "-mat", *mat_args, "-dir", *dirs)


# ── 10. OUTPUT DATABASE ─────────────────────────────────────
def create_odb(output_dir, tcl_data):
    opst.post.set_odb_path(str(output_dir))
    node_tags = [n[0] for n in tcl_data["nodes"]]
    odb = opst.post.CreateODB("F12-D100",
                              save_nodal_resp=True,
                              node_tags=node_tags,
                              save_frame_resp=True,
                              save_link_resp=True)
    return odb


# ── 11. LOADS ────────────────────────────────────────────────
def build_masses(tcl_data):
    for tag, m in tcl_data["mass"]:
        m_conv = m * MASS_CONV
        ops.mass(tag, m_conv, m_conv, 0.0)


# ── 12. ANALYSIS ────────────────────────────────────────────
def run_analysis(output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    tcl_data = _parse_tcl(TCL_PATH)

    init_model()
    define_materials(tcl_data)
    define_geom_transf(tcl_data)
    build_nodes(tcl_data)
    define_boundary_conditions(tcl_data)
    vis_nodes(output_dir)

    build_elements(tcl_data)
    vis_model(output_dir)

    odb = create_odb(output_dir, tcl_data)
    odb.save_model_data()

    build_masses(tcl_data)

    # ── Gravity load ──
    # Distribute story total (D + 0.25L) proportionally to nodal masses
    node_csv = _read_csv(REF_DIR / "node.csv")
    node_story = {}
    node_mass_val = {}
    for r in node_csv:
        nid = int(r["id"])
        s = r.get("story", "0")
        if s.isdigit():
            node_story[nid] = int(s)
        m = float(r.get("mass", "0"))
        if m > 0:
            node_mass_val[nid] = m

    ops.timeSeries("Constant", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)

    story_csv = _read_csv(REF_DIR / "story.csv")
    for s in story_csv:
        sid = int(s["id"])
        dl = float(s["story_dead_load"]) * LB2N
        ll = float(s["story_live_load"]) * LB2N
        total_s = dl + 0.25 * ll
        # Nodes at this story with mass > 0
        snodes = [nid for nid, st in node_story.items() if st == sid and nid in node_mass_val]
        if not snodes:
            continue
        total_m = sum(node_mass_val[nid] for nid in snodes)
        for nid in snodes:
            frac = node_mass_val[nid] / total_m if total_m > 0 else 1.0 / len(snodes)
            ops.load(nid, 0.0, -total_s * frac, 0.0)

    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    # ── Gravity analysis ──
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("EnergyIncr", 1.0e-8, 200)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1.0 / N_GRAV_STEPS)
    ops.analysis("Static")
    for _ in range(N_GRAV_STEPS):
        ops.analyze(1)
    ops.loadConst("-time", 0.0)

    # ── Pushover ──
    # Roof node for displacement control
    roof_tag = 6048  # left roof node
    roof_nodes_all = [n[0] for n in tcl_data["nodes"] if 6048 <= n[0] <= 6051]
    if roof_nodes_all:
        roof_tag = roof_nodes_all[0]

    # Inverted triangular lateral pattern
    ops.timeSeries("Linear", TS_LATERAL)
    ops.pattern("Plain", PAT_LATERAL, TS_LATERAL)

    # Compute weights per node
    node_weights = {}
    for tag, m in tcl_data["mass"]:
        y_mm = 0.0
        for nt, x, y in tcl_data["nodes"]:
            if nt == tag:
                y_mm = y * IN2MM
                break
        node_weights[tag] = (m * MASS_CONV, y_mm)

    total_wh = sum(w * y for w, y in node_weights.values())
    for tag, (w, y) in node_weights.items():
        f = w * y / total_wh if total_wh > 0 else 0.0
        ops.load(tag, f, 0.0, 0.0)

    # Displacement-controlled pushover via SmartAnalyze
    # NOTE: SmartAnalyze sets constraints/numberer/system internally — do NOT
    # call them manually here (they are frozen after the gravity analysis object).
    d_target = MAX_DRIFT_RATIO * TOTAL_H
    d_inc = d_target / N_PUSH_STEPS
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30],
    )
    protocol = [d_target]
    segs = analysis.static_split(protocol, maxStep=d_inc)
    n_ok = 0
    for seg in segs:
        ok = analysis.StaticAnalyze(node=roof_tag, dof=1, seg=seg)
        if ok < 0:
            print(f"Pushover diverged at step {n_ok + 1}")
            break
        n_ok += 1
        odb.fetch_response_step()
    analysis.close()
    print(f"Pushover loop ended, {n_ok} steps converged, saving responses...")
    odb.save_response()
    drift_pct = (n_ok * d_inc) / TOTAL_H * 100
    print(f"Pushover: {n_ok}/{N_PUSH_STEPS} steps, roof drift = {drift_pct:.2f} %")
    return odb


def _read_csv(path):
    """Read a CSV and return list of dicts."""
    with open(str(path), newline="") as f:
        return list(csv.DictReader(f))


# ── 13. POST-PROCESSING ─────────────────────────────────────
def post_process(odb, output_dir):
    if _headless():
        return
    opst.post.set_odb_path(str(output_dir))
    vis_defo(output_dir, odb_tag="F12-D100", resp_dof="UX")
    fig_slider = opst.vis.plotly.plot_nodal_responses(
        odb_tag="F12-D100", slides=True, defo_scale=True,
        resp_type="disp", resp_dof="UX",
    )
    fig_slider.write_html(str(output_dir / "vis_06_slider.html"))


# ── 14. MAIN ────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
