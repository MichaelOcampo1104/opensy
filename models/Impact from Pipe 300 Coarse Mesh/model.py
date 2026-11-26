# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Impact from Pipe 300 Coarse Mesh — 75 kPa surcharge on a cut section beside a 300 mm pipe
UniqueID : Impact from Pipe 300 Coarse Mesh
Author   : Michael Ocampo
Date     : 2026-11-26
Purpose  : Coarse-mesh variant of the Impact from Pipe 300 model, for quick runs. Same geometry, box, interface and placeholder soil and pipe data; about a quarter of the soil nodes.
Ref      : No published source. Geometry from "Impact to 300mm Pipe.dxf" in the folder "Impact from Pipe 300" (see that folder's README.md).
Units    : N, mm, MPa

Documented exception to the SmartAnalyze mandate (AGENT.md §3c, §10):
  - The gravity state and the surcharge ramp run in manual ops.analyze() loops with
    odb.fetch_response_step() after each converged step. SmartAnalyze forces DisplacementControl on
    static steps, so it cannot run a load-controlled ramp (AGENT.md §3c, §12z).
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import json
import math
import sys
import time
from pathlib import Path

import gmsh
import matplotlib

matplotlib.use("Agg")
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import animation  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
import openseespy.opensees as ops  # noqa: E402
import opstool as opst  # noqa: E402

# Add standards/ to path if running standalone
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *  # noqa: F401,F403  — N, mm, MPa, m, kN, kPa
from vis_utils import _headless, vis_defo, vis_loads, vis_model, vis_nodes, vis_pre_analysis  # noqa: E402

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Soil quads and soil nodes use the gmsh mesh tags. The bases below keep the other families apart.
MAT_SOIL = 1                 # ElasticIsotropic, plane strain (placeholder soil)
TRANSF_RING = 1              # geomTransf for the pipe ring
TS_CONST = 1                 # constant factor 1.0: pipe self-weight, applied in full
TS_ZERO = 2                  # constant factor 0.0: surcharge pattern before the ramp
TS_RAMP = 3                  # linear time series: load factor of the surcharge
PAT_WEIGHT = 1               # pipe self-weight pattern
PAT_SURCHARGE = 2            # 75 kPa surcharge pattern
ODB_TAG = 1                  # CreateODB tag
GMSH_QUAD4 = 3               # gmsh element type code for 4-node quadrangles
NODE_BEAM_BASE = 1000000     # pipe ring nodes (3 DOF): NODE_BEAM_BASE + k
NODE_AUX_BASE = 2000000      # interface nodes on the pipe outer surface (2 DOF): NODE_AUX_BASE + k
ELE_BEAM_BASE = 3000000      # pipe ring beam elements: ELE_BEAM_BASE + k
ELE_SPRING_BASE = 4000000    # interface springs (zeroLength): ELE_SPRING_BASE + k
MAT_IF_N_BASE = 1000000      # normal interface materials (ENT, compression only): MAT_IF_N_BASE + k
MAT_IF_T_BASE = 2000000      # tangential interface materials (ElasticPP): MAT_IF_T_BASE + k

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# PLACEHOLDER SOIL AND PIPE VALUES — replace with site data before using any result (see README.md).
# Geometry is read from the DXF (metres) and converted here to mm.

# Soil box. Chosen from the box convergence study in README.md: the pipe-moment increments converge
# at x = -60 m to 85 m and a base 100 m below ground (within 2% of the larger boxes tested).
x_left = -60.0 * m
x_right = 85.0 * m
y_base = -90.0 * m
y_ground = 10.0 * m

# Pipe: DXF circle centre (14.45, 8.59) m. The 0.15 m radius is taken as the outer radius.
pipe_centre_x = 14.45227796261315 * m
pipe_centre_y = 8.594546467914369 * m
pipe_od = 300.0 * mm
pipe_wall = 12.0 * mm                       # PLACEHOLDER
pipe_e = 3000.0 * MPa                       # PLACEHOLDER
pipe_nu = 0.38                              # PLACEHOLDER
pipe_unit_weight = 14.0 * kN / m**3         # PLACEHOLDER
pipe_radius_out = pipe_od / 2.0
pipe_radius_in = pipe_radius_out - pipe_wall
pipe_radius_mid = pipe_radius_out - pipe_wall / 2.0
pipe_area_wall = math.pi * (pipe_radius_out**2 - pipe_radius_in**2)   # mm² of wall section

# Soil: linear elastic placeholder
e_soil = 30.0 * MPa                         # PLACEHOLDER
nu_soil = 0.30                              # PLACEHOLDER
gamma_soil = 18.0 * kN / m**3               # PLACEHOLDER

# Pipe-soil interface placeholder. Normal stiffness per unit area over an assumed 25 mm thickness.
# Shear: constant capacity (adhesion type, alpha * c_u with alpha = 0.5 and c_u = 60 kPa) reached at
# a relative slip of 2 mm, so self-weight does not push the springs past yield.
interface_thickness = 25.0 * mm             # PLACEHOLDER
k_interface = e_soil / interface_thickness  # N/mm³ per unit area (normal)
tau_interface = 30.0 * kPa                  # PLACEHOLDER
interface_yield_disp = 2.0 * mm             # PLACEHOLDER: slip at which the shear capacity is reached
k_tangent = tau_interface / interface_yield_disp   # N/mm³ per unit area (shear)

# Open cut: DXF Boundary polyline, 45-degree sides, floor at y = 8.257 m. The soil is already cut,
# so the cut is the initial geometry; no excavation stage is simulated.
trench_floor_y = 8.257244422105941 * m
trench_x_min = 2.500019919969417 * m
trench_x_max = 10.40336536539507 * m
trench_outline = [
    (2.500019919969417 * m, y_ground),
    (4.246883620608059 * m, trench_floor_y),
    (8.652339545982613 * m, trench_floor_y),
    (10.40336536539507 * m, y_ground),
]

# Surcharge pad on the ground (DXF Pad_load line)
pad_left = 16.83036756027832 * m
pad_right = 21.74491451144058 * m
surcharge = 75.0 * kPa

# Mesh sizes and the out-of-plane thickness of the plane-strain model. Coarse variant (candidate K1 in
# the fine model's README): 25 mm at the pipe, 400 mm in the cut, 1 m under the pad, 4 m in the far field.
# Against the fine mesh its pipe-moment increments differ by up to 4%, and its settlements by about 1%.
h_pipe = 25.0 * mm
h_trench = 400.0 * mm
h_pad = 1000.0 * mm
h_far = 4000.0 * mm
coord_tol = 1.0e-3 * mm
unit_length = 1.0 * mm

# Analysis controls
n_surcharge_steps = 20
odb_every_n_steps = 20       # response database at the final step only: per-step collection is too slow
                             # on the full mesh; the animation uses its own frame file (AGENT.md §3d)
tol_disp = 1.0e-6 * mm
max_iter = 60

# Animation (display only): magnification of the ground and of the pipe shape
anim_fps = 4
anim_scale_ground = 50.0
anim_scale_pipe = 100.0


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Reset OpenSees and start a 2D model with 2 DOF per node (soil and interface nodes).

    The pipe ring uses 3-DOF nodes; they are created in define_nodes().
    """
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 2)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials(mesh: dict) -> None:
    """Define the soil and one normal and one tangential material per interface spring.

    Args:
        mesh: Mesh dictionary from build_mesh(). Its 'iface_length' list sets the spring count.
    """
    ops.nDMaterial("ElasticIsotropic", MAT_SOIL, e_soil, nu_soil)
    for k, length in enumerate(mesh["iface_length"]):
        spring_n = k_interface * length * unit_length          # N/mm for this tributary length
        spring_t = k_tangent * length * unit_length
        ops.uniaxialMaterial("ENT", MAT_IF_N_BASE + k, spring_n)
        # ElasticPP yields at a displacement, so the yield force is spring_t * interface_yield_disp
        ops.uniaxialMaterial("ElasticPP", MAT_IF_T_BASE + k, spring_t, interface_yield_disp)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> dict:
    """Return the pipe ring section per 1 mm of pipe length, in plane strain.

    Returns:
        Dictionary with 'area' (mm²), 'inertia' (mm⁴) and 'e_plane' (MPa).
    """
    return {
        "area": pipe_wall * unit_length,
        "inertia": unit_length * pipe_wall**3 / 12.0,
        "e_plane": pipe_e / (1.0 - pipe_nu**2),
    }


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def _quad_area(nodes: dict, conn: tuple) -> float:
    """Shoelace area of a quad in mm²; positive when the node order is counter-clockwise."""
    area = 0.0
    for i in range(4):
        x0, y0 = nodes[conn[i]]
        x1, y1 = nodes[conn[(i + 1) % 4]]
        area += x0 * y1 - x1 * y0
    return 0.5 * area


def _within(bb: tuple, box: tuple) -> bool:
    """True when the bounding box bb = (x0, y0, z0, x1, y1, z1) lies inside box = (x0, y0, x1, y1)."""
    return (bb[0] >= box[0] - coord_tol and bb[1] >= box[1] - coord_tol
            and bb[3] <= box[2] + coord_tol and bb[4] <= box[3] + coord_tol)


def build_mesh() -> dict:
    """Mesh the soil box with gmsh, with the open cut and the pipe hole as boundaries.

    The cut region is meshed so the boundary and the mesh match the analysed version, but its quads,
    and the nodes that belong only to them, are left out of the model: the soil is already cut.

    Returns:
        Dictionary with node coordinates (mm), the soil quads, the soil node tags, the interface nodes
        with their angles and tributary lengths (mm), boundary node lists, ground-load tributaries (mm)
        and the node use counts.

    Raises:
        RuntimeError: If the mesh has a non-quad element or the pad loads do not add up.
    """
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add("impact_from_pipe_300")
        occ = gmsh.model.occ
        rect = occ.addRectangle(x_left, y_base, 0.0, x_right - x_left, y_ground - y_base)
        hole = occ.addDisk(pipe_centre_x, pipe_centre_y, 0.0, pipe_radius_out, pipe_radius_out)
        soil_dimtags, _ = occ.cut([(2, rect)], [(2, hole)])
        cut_pts = [occ.addPoint(x, y, 0.0) for x, y in trench_outline]
        cut_lines = [occ.addLine(cut_pts[i], cut_pts[(i + 1) % len(cut_pts)]) for i in range(len(cut_pts))]
        cut_surface = occ.addPlaneSurface([occ.addCurveLoop(cut_lines)])
        pad_pts = [occ.addPoint(pad_left, y_ground, 0.0), occ.addPoint(pad_right, y_ground, 0.0)]
        occ.fragment(soil_dimtags, [(2, cut_surface)] + [(0, p) for p in pad_pts])
        occ.synchronize()

        cut_tags, soil_tags = [], []
        for _, tag in gmsh.model.getEntities(2):
            cx, cy, _ = occ.getCenterOfMass(2, tag)
            inside_cut = trench_x_min < cx < trench_x_max and trench_floor_y < cy < y_ground
            (cut_tags if inside_cut else soil_tags).append(tag)

        hole_box = (pipe_centre_x - pipe_radius_out, pipe_centre_y - pipe_radius_out,
                    pipe_centre_x + pipe_radius_out, pipe_centre_y + pipe_radius_out)
        cut_box = (trench_x_min, trench_floor_y, trench_x_max, y_ground)
        pipe_curves, cut_curves, pad_curves = [], [], []
        for _, tag in gmsh.model.getEntities(1):
            bb = gmsh.model.getBoundingBox(1, tag)
            if _within(bb, hole_box):
                pipe_curves.append(tag)
            if _within(bb, cut_box):
                cut_curves.append(tag)
            if (abs(bb[1] - y_ground) <= coord_tol and abs(bb[4] - y_ground) <= coord_tol
                    and bb[0] >= pad_left - coord_tol and bb[3] <= pad_right + coord_tol):
                pad_curves.append(tag)

        field = gmsh.model.mesh.field

        def _size_threshold(curves: list, size_min: float, dist_min: float, dist_max: float) -> int:
            dist_field = field.add("Distance")
            field.setNumbers(dist_field, "CurvesList", curves)
            field.setNumber(dist_field, "Sampling", 200)
            thr_field = field.add("Threshold")
            field.setNumber(thr_field, "InField", dist_field)
            field.setNumber(thr_field, "SizeMin", size_min)
            field.setNumber(thr_field, "SizeMax", h_far)
            field.setNumber(thr_field, "DistMin", dist_min)
            field.setNumber(thr_field, "DistMax", dist_max)
            return thr_field

        f_pipe = _size_threshold(pipe_curves, h_pipe, 300.0 * mm, 6000.0 * mm)
        f_cut = _size_threshold(cut_curves, h_trench, 500.0 * mm, 4000.0 * mm)
        f_pad = _size_threshold(pad_curves, h_pad, 1000.0 * mm, 6000.0 * mm)
        f_min = field.add("Min")
        field.setNumbers(f_min, "FieldsList", [f_pipe, f_cut, f_pad])
        field.setAsBackgroundMesh(f_min)

        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh.option.setNumber("Mesh.Algorithm", 8)
        gmsh.option.setNumber("Mesh.RecombineAll", 1)
        gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
        gmsh.model.mesh.generate(2)

        raw_tags, raw_xyz, _ = gmsh.model.mesh.getNodes()
        nodes = {int(t): (float(raw_xyz[3 * i]), float(raw_xyz[3 * i + 1])) for i, t in enumerate(raw_tags)}

        quads_all = []
        for tag in cut_tags + soil_tags:
            elem_types, elem_tags, elem_nodes = gmsh.model.mesh.getElements(2, tag)
            for elem_type, tags_list, node_list in zip(elem_types, elem_tags, elem_nodes):
                if elem_type != GMSH_QUAD4:
                    raise RuntimeError(f"surface {tag} has element type {elem_type}; only quads are supported")
                for e in range(len(tags_list)):
                    conn = [int(v) for v in node_list[4 * e:4 * e + 4]]
                    if _quad_area(nodes, tuple(conn)) < 0.0:
                        conn = [conn[0], conn[3], conn[2], conn[1]]
                    quads_all.append({"tag": int(tags_list[e]), "nodes": tuple(conn), "cut": tag in cut_tags})

        # The cut is already excavated: its quads are not part of the model.
        quads = [q for q in quads_all if not q["cut"]]
        node_use: dict = {}
        for q in quads:
            for n in q["nodes"]:
                node_use[n] = node_use.get(n, 0) + 1
        soil_nodes = sorted(node_use)

        iface = sorted(
            ((t, math.atan2(y - pipe_centre_y, x - pipe_centre_x)) for t, (x, y) in nodes.items()
             if abs(math.hypot(x - pipe_centre_x, y - pipe_centre_y) - pipe_radius_out) <= coord_tol),
            key=lambda item: item[1],
        )
        count = len(iface)
        iface_length = []
        for k in range(count):
            p_prev = nodes[iface[k - 1][0]]
            p_k = nodes[iface[k][0]]
            p_next = nodes[iface[(k + 1) % count][0]]
            iface_length.append(0.5 * (math.dist(p_prev, p_k) + math.dist(p_k, p_next)))

        ground = sorted((t for t, (x, y) in nodes.items() if abs(y - y_ground) <= coord_tol),
                        key=lambda t: nodes[t][0])
        base = [t for t, (x, y) in nodes.items() if abs(y - y_base) <= coord_tol]
        left = [t for t, (x, y) in nodes.items() if abs(x - x_left) <= coord_tol]
        right = [t for t, (x, y) in nodes.items() if abs(x - x_right) <= coord_tol]

        ground_loads = []
        for i, tag in enumerate(ground):
            x = nodes[tag][0]
            if not (pad_left - coord_tol <= x <= pad_right + coord_tol):
                continue
            x_prev = nodes[ground[i - 1]][0] if i > 0 else x
            x_next = nodes[ground[i + 1]][0] if i < len(ground) - 1 else x
            lo = max(0.5 * (x + x_prev), pad_left)
            hi = min(0.5 * (x + x_next), pad_right)
            if hi > lo:
                ground_loads.append((tag, hi - lo))
        if abs(sum(length for _, length in ground_loads) - (pad_right - pad_left)) > coord_tol:
            raise RuntimeError("pad tributary lengths do not add up to the pad width")

        print(f"mesh: {len(soil_nodes)} soil nodes, {len(quads)} quads (open cut excluded), "
              f"{count} interface nodes", flush=True)
        return {
            "nodes": nodes,
            "quads": quads,
            "soil_nodes": soil_nodes,
            "iface": iface,
            "iface_length": iface_length,
            "ground": ground,
            "ground_loads": ground_loads,
            "base": base,
            "left": left,
            "right": right,
            "node_use": node_use,
        }
    finally:
        gmsh.finalize()


def define_nodes(mesh: dict) -> None:
    """Create the pipe ring nodes (3 DOF), then the soil nodes and the interface nodes (2 DOF).

    Args:
        mesh: Mesh dictionary from build_mesh().
    """
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    for k, (_, theta) in enumerate(mesh["iface"]):
        ops.node(NODE_BEAM_BASE + k,
                 pipe_centre_x + pipe_radius_mid * math.cos(theta),
                 pipe_centre_y + pipe_radius_mid * math.sin(theta))
    ops.model("basic", "-ndm", 2, "-ndf", 2)
    for tag in mesh["soil_nodes"]:
        x, y = mesh["nodes"][tag]
        ops.node(tag, x, y)
    for k, (tag, _) in enumerate(mesh["iface"]):
        x, y = mesh["nodes"][tag]
        ops.node(NODE_AUX_BASE + k, x, y)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions(mesh: dict) -> None:
    """Rollers on both sides, pinned base, and an equalDOF tie from each interface node to its ring node.

    Args:
        mesh: Mesh dictionary from build_mesh().
    """
    for tag in mesh["left"] + mesh["right"]:
        ops.fix(tag, 1, 0)
    for tag in mesh["base"]:
        ops.fix(tag, 0, 1)
    for k in range(len(mesh["iface"])):
        ops.equalDOF(NODE_AUX_BASE + k, NODE_BEAM_BASE + k, 1, 2)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(mesh: dict, section: dict) -> None:
    """Create the soil quads (self-weight as body force), the pipe ring beams and the interface springs.

    Args:
        mesh: Mesh dictionary from build_mesh().
        section: Pipe ring section from define_sections().
    """
    count = len(mesh["iface"])
    ops.model("basic", "-ndm", 2, "-ndf", 3)          # frame elements need 3 DOF per node
    ops.geomTransf("Linear", TRANSF_RING)
    for k in range(count):
        ops.element("elasticBeamColumn", ELE_BEAM_BASE + k,
                    NODE_BEAM_BASE + k, NODE_BEAM_BASE + (k + 1) % count,
                    section["area"], section["e_plane"], section["inertia"], TRANSF_RING)
    ops.model("basic", "-ndm", 2, "-ndf", 2)          # soil quads and springs need 2 DOF per node
    for q in mesh["quads"]:
        ops.element("quad", q["tag"], *q["nodes"], unit_length, "PlaneStrain", MAT_SOIL,
                    0.0, 0.0, 0.0, -gamma_soil)
    for k, (tag, theta) in enumerate(mesh["iface"]):
        c, s = math.cos(theta), math.sin(theta)
        # local x = radial outward (normal), local y = tangential; node I is the pipe side
        ops.element("zeroLength", ELE_SPRING_BASE + k, NODE_AUX_BASE + k, tag,
                    "-mat", MAT_IF_N_BASE + k, MAT_IF_T_BASE + k, "-dir", 1, 2,
                    "-orient", c, s, 0.0, -s, c, 0.0)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Create the response database for all nodes and the pipe ring beams.

    Args:
        output_dir: Folder for the ODB files.

    Returns:
        The CreateODB instance; fetch_response_step() is called after every converged step.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=ODB_TAG, save_nodal_resp=True, save_frame_resp=True)
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads(mesh: dict) -> None:
    """Apply the pipe self-weight as constant nodal loads. Soil self-weight is in the quads.

    Args:
        mesh: Mesh dictionary from build_mesh().
    """
    ops.timeSeries("Constant", TS_CONST)
    ops.pattern("Plain", PAT_WEIGHT, TS_CONST)
    weight_per_length = pipe_unit_weight * pipe_area_wall          # N per mm of pipe length
    for k, length in enumerate(mesh["iface_length"]):
        ops.load(NODE_BEAM_BASE + k, 0.0, -weight_per_length * length, 0.0)


def _surcharge_pattern(mesh: dict, ts_tag: int) -> None:
    """Create the surcharge pattern on the ground nodes of the pad with the given time series.

    Args:
        mesh: Mesh dictionary from build_mesh().
        ts_tag: Time series tag (TS_ZERO before the ramp, TS_RAMP for the surcharge).
    """
    ops.pattern("Plain", PAT_SURCHARGE, ts_tag)
    for tag, length in mesh["ground_loads"]:
        ops.load(tag, 0.0, -surcharge * length * unit_length)


def define_surcharge_loads(mesh: dict) -> None:
    """Define the surcharge with a zero factor so the checkpoints show it; it is switched on later.

    Args:
        mesh: Mesh dictionary from build_mesh().
    """
    ops.timeSeries("Constant", TS_ZERO, "-factor", 0.0)
    _surcharge_pattern(mesh, TS_ZERO)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def _set_solver() -> None:
    """Solver set-up shared by the manual static loops.

    wipeAnalysis() first, so the handlers can be set again for every stage (AGENT.md §12h-3).
    """
    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", tol_disp, max_iter)
    ops.analysis("Static")


def _advance(label: str) -> None:
    """Take one static step, retrying with other Newton variants if the first try does not converge.

    Args:
        label: Name of the step, used in the log and the error message.

    Raises:
        RuntimeError: If no algorithm converges.
    """
    started = time.perf_counter()
    for algorithm in ("Newton", "NewtonLineSearch", "KrylovNewton"):
        ops.algorithm(algorithm)
        if ops.analyze(1) == 0:
            print(f"  {label}: converged with {algorithm} in {time.perf_counter() - started:.1f} s", flush=True)
            return
    raise RuntimeError(f"step '{label}' did not converge with Newton, NewtonLineSearch or KrylovNewton")


def _nearest(values: list, target: float) -> int:
    """Index of the angle in values closest to target (radians, wrapped)."""
    best, best_gap = 0, math.inf
    for i, v in enumerate(values):
        gap = abs(math.atan2(math.sin(v - target), math.cos(v - target)))
        if gap < best_gap:
            best, best_gap = i, gap
    return best


def _nearest_ground(mesh: dict, x: float) -> int:
    """Tag of the ground node closest to x that belongs to the model."""
    alive = [t for t in mesh["ground"] if mesh["node_use"].get(t, 0) > 0]
    return min(alive, key=lambda t: abs(mesh["nodes"][t][0] - x))


def _snapshot(mesh: dict) -> dict:
    """Displacements of the soil and ring nodes, and the ring moments at the i-end of each element.

    Args:
        mesh: Mesh dictionary from build_mesh().

    Returns:
        Dictionary of arrays (mm, and N·mm/mm for the moments) at the current state.
    """
    n_ring = len(mesh["iface"])
    return {
        "soil_ux": np.array([ops.nodeDisp(t, 1) for t in mesh["soil_nodes"]]),
        "soil_uy": np.array([ops.nodeDisp(t, 2) for t in mesh["soil_nodes"]]),
        "ring_ux": np.array([ops.nodeDisp(NODE_BEAM_BASE + k, 1) for k in range(n_ring)]),
        "ring_uy": np.array([ops.nodeDisp(NODE_BEAM_BASE + k, 2) for k in range(n_ring)]),
        "ring_m": np.array([ops.eleResponse(ELE_BEAM_BASE + k, "localForce")[2] for k in range(n_ring)]),
    }


def collect_state(mesh: dict, load_factor: float = 0.0) -> dict:
    """Read the current pipe, interface, ground and equilibrium quantities.

    Args:
        mesh: Mesh dictionary from build_mesh().
        load_factor: Surcharge load factor applied at this state (0 before the surcharge).

    Returns:
        Dictionary of floats in N, mm and MPa (per 1 mm of pipe length for forces and moments).
    """
    ops.reactions()
    base_ry = sum(ops.nodeReaction(tag)[1] for tag in mesh["base"])
    soil_weight = sum(_quad_area(mesh["nodes"], q["nodes"]) for q in mesh["quads"]) * gamma_soil * unit_length
    pipe_weight = pipe_unit_weight * pipe_area_wall * sum(mesh["iface_length"])
    surcharge_total = surcharge * (pad_right - pad_left) * unit_length * load_factor

    angles = [theta for _, theta in mesh["iface"]]
    n = len(angles)
    ux = [ops.nodeDisp(NODE_BEAM_BASE + k, 1) for k in range(n)]
    uy = [ops.nodeDisp(NODE_BEAM_BASE + k, 2) for k in range(n)]
    i_top = _nearest(angles, math.pi / 2.0)
    i_bot = _nearest(angles, -math.pi / 2.0)
    i_right = _nearest(angles, 0.0)
    i_left = _nearest(angles, math.pi)

    m_max, m_angle = 0.0, 0.0
    for k in range(n):
        forces = ops.eleResponse(ELE_BEAM_BASE + k, "localForce")
        for moment in (forces[2], forces[5]):
            if abs(moment) > abs(m_max):
                m_max, m_angle = moment, angles[k]
    moment_at_deg = {}
    for label, target in (("0", 0.0), ("90", math.pi / 2.0), ("180", math.pi), ("270", -math.pi / 2.0)):
        i = _nearest(angles, target)
        moment_at_deg[label] = ops.eleResponse(ELE_BEAM_BASE + i, "localForce")[2]

    fn_max, ft_max, in_contact = 0.0, 0.0, 0
    for k in range(n):
        forces = ops.eleResponse(ELE_SPRING_BASE + k, "localForce")
        fn_max = max(fn_max, abs(forces[0]))
        ft_max = max(ft_max, abs(forces[1]))
        if abs(forces[0]) > 1.0e-9 * N:
            in_contact += 1

    ground_uy = {}
    for label, x in (("x_0m", 0.0), ("x_pipe", pipe_centre_x),
                     ("x_pad_centre", 0.5 * (pad_left + pad_right)), ("x_40m", 40.0 * m)):
        ground_uy[label] = ops.nodeDisp(_nearest_ground(mesh, x), 2)

    return {
        "load_factor": load_factor,
        "base_sum_ry_N": base_ry,
        "soil_weight_N": soil_weight,
        "pipe_weight_N": pipe_weight,
        "surcharge_N": surcharge_total,
        "pipe_mean_uy_mm": sum(uy) / n,
        "pipe_dD_vertical_mm": uy[i_top] - uy[i_bot],
        "pipe_dD_horizontal_mm": ux[i_right] - ux[i_left],
        "pipe_moment_max_N_mm_per_mm": m_max,
        "pipe_moment_angle_deg": math.degrees(m_angle),
        "pipe_moment_at_deg_N_mm_per_mm": moment_at_deg,
        "interface_normal_max_N_per_mm": fn_max,
        "interface_tangential_max_N_per_mm": ft_max,
        "interface_springs_loaded": in_contact,
        "ground_uy_mm": ground_uy,
    }


def run_gravity(odb, mesh: dict, results: dict) -> None:
    """Gravity on the cut section: soil self-weight (quads) and pipe self-weight, in one full step.

    The soil is already cut, so the gravity state is computed on the cut geometry. Element body forces
    are not scaled by the load factor in OpenSeesPy (checked), so the full soil weight acts in the first
    step. loadConst() then freezes the gravity state.

    Args:
        odb: Active CreateODB instance.
        mesh: Mesh dictionary from build_mesh().
        results: Results dictionary, updated in place.
    """
    _set_solver()
    ops.integrator("LoadControl", 1.0)
    _advance("gravity")
    ops.loadConst("-time", 0.0)
    results["gravity"] = collect_state(mesh)


def _frame(now: dict, reference: dict, lam: float) -> dict:
    """Change from the gravity state at load factor lam."""
    frame = {key: now[key] - reference[key] for key in reference}
    frame["lam"] = lam
    return frame


def _stack_frames(frames: list) -> dict:
    """Stack the per-step frames into arrays with the step as the first index."""
    stacked = {"lam": np.array([f["lam"] for f in frames])}
    for key in ("soil_ux", "soil_uy", "ring_ux", "ring_uy", "ring_m"):
        stacked[key] = np.stack([f[key] for f in frames])
    return stacked


def run_surcharge(odb, mesh: dict, results: dict) -> dict:
    """Surcharge ramp on the cut section, with a displacement and moment frame at every step.

    Args:
        odb: Active CreateODB instance.
        mesh: Mesh dictionary from build_mesh().
        results: Results dictionary, updated in place.

    Returns:
        Frames relative to the gravity state, stacked over the steps (frame 0 is the gravity state).
    """
    reference = _snapshot(mesh)
    ops.remove("loadPattern", PAT_SURCHARGE)
    ops.timeSeries("Linear", TS_RAMP)
    _surcharge_pattern(mesh, TS_RAMP)
    _set_solver()
    ops.integrator("LoadControl", 1.0 / n_surcharge_steps)
    history = []
    frames = [_frame(reference, reference, 0.0)]
    for step in range(1, n_surcharge_steps + 1):
        _advance(f"surcharge step {step}")
        if step % odb_every_n_steps == 0:            # throttled ODB collection (AGENT.md §3d)
            odb.fetch_response_step()
        lam = step / n_surcharge_steps
        history.append(collect_state(mesh, load_factor=lam))
        frames.append(_frame(_snapshot(mesh), reference, lam))
    results["surcharge_history"] = history
    results["surcharge_final"] = history[-1]
    return _stack_frames(frames)


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def save_frames(output_dir: Path, mesh: dict, frames: dict) -> None:
    """Write the geometry and the surcharge frames used by the animation to surcharge_frames.npz.

    Args:
        output_dir: Folder for the file.
        mesh: Mesh dictionary from build_mesh().
        frames: Frames returned by run_surcharge().
    """
    index = {tag: i for i, tag in enumerate(mesh["soil_nodes"])}
    node_xy = np.array([mesh["nodes"][t] for t in mesh["soil_nodes"]])
    quads = np.array([[index[n] for n in q["nodes"]] for q in mesh["quads"]])
    np.savez(
        output_dir / "surcharge_frames.npz",
        node_xy=node_xy,
        quads=quads,
        ring_angle=np.array([theta for _, theta in mesh["iface"]]),
        pipe_centre=np.array([pipe_centre_x, pipe_centre_y]),
        pipe_radius_out=pipe_radius_out,
        pipe_radius_mid=pipe_radius_mid,
        pad=np.array([pad_left, pad_right]),
        y_ground=y_ground,
        lam=frames["lam"],
        soil_ux=frames["soil_ux"],
        soil_uy=frames["soil_uy"],
        ring_ux=frames["ring_ux"],
        ring_uy=frames["ring_uy"],
        ring_m=frames["ring_m"],
    )


def _edges(points: np.ndarray) -> np.ndarray:
    """Edges of closed polygons: points (K, n, 2) -> segments (K·n, 2, 2)."""
    return np.stack([points, np.roll(points, -1, axis=1)], axis=2).reshape(-1, 2, 2)


def _ring_segments(points: np.ndarray) -> np.ndarray:
    """Segments of a closed ring of points (R, 2) -> (R, 2, 2)."""
    return np.stack([points, np.roll(points, -1, axis=0)], axis=1)


def write_surcharge_animation(output_dir: Path) -> None:
    """Animate the ground and pipe response as the surcharge ramps from 0 to 75 kPa.

    The frames come from surcharge_frames.npz. Displacements are increments from the gravity state.
    The ground is magnified by anim_scale_ground and the pipe shape, relative to its mean, by
    anim_scale_pipe; both scales are printed on the figure. Writes a GIF, a self-contained HTML player
    and the final frame as PNG.

    Args:
        output_dir: Folder that holds surcharge_frames.npz; the outputs are written there.
    """
    data = np.load(output_dir / "surcharge_frames.npz")
    node_xy = data["node_xy"]
    quads = data["quads"]
    ring_angle = data["ring_angle"]
    cx, cy = (float(v) for v in data["pipe_centre"])
    r_out = float(data["pipe_radius_out"])
    r_mid = float(data["pipe_radius_mid"])
    pad0, pad1 = (float(v) for v in data["pad"])
    y_gl = float(data["y_ground"])
    lam = data["lam"]
    soil_ux, soil_uy = data["soil_ux"], data["soil_uy"]
    ring_ux, ring_uy, ring_m = data["ring_ux"], data["ring_uy"], data["ring_m"]
    q_kpa = lam * (surcharge / kPa)
    ring_xy = np.stack([cx + r_mid * np.cos(ring_angle), cy + r_mid * np.sin(ring_angle)], axis=1)

    angles = list(ring_angle)
    top = _nearest(angles, math.pi / 2.0)
    bottom = _nearest(angles, -math.pi / 2.0)
    left = _nearest(angles, math.pi)
    right = _nearest(angles, 0.0)
    pad_node = int(np.argmin((node_xy[:, 0] - 0.5 * (pad0 + pad1)) ** 2 + (node_xy[:, 1] - y_gl) ** 2))
    settle_pad = -soil_uy[:, pad_node]
    settle_pipe = -ring_uy.mean(axis=1)
    dd_v = ring_uy[:, top] - ring_uy[:, bottom]
    dd_h = ring_ux[:, right] - ring_ux[:, left]
    crown_m = ring_m[:, top]

    x_lo, x_hi, y_lo, y_hi = -4000.0, 34000.0, -8000.0, 12500.0
    centroid = node_xy[quads].mean(axis=1)
    in_sec = ((centroid[:, 0] > x_lo - 2000.0) & (centroid[:, 0] < x_hi + 2000.0)
              & (centroid[:, 1] > y_lo - 2000.0) & (centroid[:, 1] < y_hi + 2000.0))
    quads_sec = quads[in_sec]
    in_pipe = (np.abs(centroid[:, 0] - cx) < 1500.0) & (np.abs(centroid[:, 1] - cy) < 1500.0)
    quads_pipe = quads[in_pipe]
    ground_idx = np.where((np.abs(node_xy[:, 1] - y_gl) < 1.0)
                          & (node_xy[:, 0] > x_lo) & (node_xy[:, 0] < x_hi))[0]
    ground_idx = ground_idx[np.argsort(node_xy[ground_idx, 0])]
    gaps = np.where(np.diff(node_xy[ground_idx, 0]) > 1000.0)[0] + 1
    ground_groups = np.split(ground_idx, gaps)

    fig = plt.figure(figsize=(14.0, 8.5))
    grid = fig.add_gridspec(2, 3, width_ratios=[2.3, 1.0, 1.0], height_ratios=[1.0, 1.0], bottom=0.14)
    ax_sec = fig.add_subplot(grid[:, 0])
    ax_pipe = fig.add_subplot(grid[0, 1:])
    ax_set = fig.add_subplot(grid[1, 1])
    ax_def = fig.add_subplot(grid[1, 2])

    ax_sec.set_xlim(x_lo, x_hi)
    ax_sec.set_ylim(y_lo, y_hi)
    ax_sec.set_aspect("equal")
    ax_sec.set_xlabel("x (mm)")
    ax_sec.set_ylabel("y (mm)")
    ax_sec.set_title(f"Ground and pipe, displacements ×{anim_scale_ground:.0f}")
    ax_pipe.set_xlim(cx - 1200.0, cx + 1200.0)
    ax_pipe.set_ylim(cy - 1200.0, cy + 1200.0)
    ax_pipe.set_aspect("equal")
    ax_pipe.set_title(f"Pipe shape relative to its mean, ×{anim_scale_pipe:.0f}")
    ring_circle = np.linspace(0.0, 2.0 * math.pi, 181)
    ax_pipe.plot(cx + r_out * np.cos(ring_circle), cy + r_out * np.sin(ring_circle), "k--", lw=0.8)

    mesh_sec = LineCollection([], colors="0.45", linewidths=0.3)
    ax_sec.add_collection(mesh_sec)
    mesh_pipe = LineCollection([], colors="0.45", linewidths=0.4)
    ax_pipe.add_collection(mesh_pipe)
    moment_max = float(np.max(np.abs(ring_m))) or 1.0
    norm = plt.Normalize(-moment_max, moment_max)
    ring_sec = LineCollection([], cmap="RdBu_r", norm=norm, linewidths=3.0)
    ring_pipe = LineCollection([], cmap="RdBu_r", norm=norm, linewidths=4.0)
    ax_sec.add_collection(ring_sec)
    ax_pipe.add_collection(ring_pipe)
    ring_sec.set_array(np.zeros(len(ring_angle)))
    ring_pipe.set_array(np.zeros(len(ring_angle)))
    fig.colorbar(ring_pipe, ax=ax_pipe, shrink=0.85, label="pipe moment change (N·mm/mm)")

    ground_lines = [ax_sec.plot([], [], "k-", lw=1.5)[0] for _ in ground_groups]
    arrow_x = np.linspace(pad0, pad1, 6)
    arrow_h = 2200.0
    arrows = ax_sec.quiver(arrow_x, np.full(6, y_gl + arrow_h), np.zeros(6), np.zeros(6),
                           color="tab:red", angles="xy", scale_units="xy", scale=1.0, width=0.004)

    q_max = float(q_kpa[-1])
    ax_set.plot(q_kpa, settle_pad, color="tab:blue", label="ground at pad centre")
    ax_set.plot(q_kpa, settle_pipe, color="tab:green", label="pipe (mean)")
    ax_set.set_xlim(0.0, q_max * 1.02)
    ax_set.set_ylim(0.0, 1.15 * max(float(settle_pad.max()), float(settle_pipe.max()), 1.0e-6))
    ax_set.set_xlabel("surcharge (kPa)")
    ax_set.set_ylabel("settlement (mm)")
    ax_set.legend(fontsize=8, loc="upper left")
    marker_set = ax_set.axvline(0.0, color="k", lw=0.8)
    ax_def.plot(q_kpa, dd_v, color="tab:purple", label="ΔD vertical")
    ax_def.plot(q_kpa, dd_h, color="tab:orange", label="ΔD horizontal")
    span = 1.3 * max(float(np.abs(dd_v).max()), float(np.abs(dd_h).max()), 1.0e-6)
    ax_def.set_xlim(0.0, q_max * 1.02)
    ax_def.set_ylim(-span, span)
    ax_def.set_xlabel("surcharge (kPa)")
    ax_def.set_ylabel("pipe diameter change (mm)")
    ax_def.legend(fontsize=8, loc="upper left")
    marker_def = ax_def.axvline(0.0, color="k", lw=0.8)
    info = fig.text(0.02, 0.02, "", va="bottom", fontsize=10,
                    bbox=dict(boxstyle="round", facecolor="white", alpha=0.9))

    def update(k: int) -> list:
        """Draw frame k."""
        u_g = np.stack([soil_ux[k], soil_uy[k]], axis=1)
        ring_u = np.stack([ring_ux[k], ring_uy[k]], axis=1)
        ring_mean = ring_u.mean(axis=0)
        mesh_sec.set_segments(_edges(node_xy[quads_sec] + anim_scale_ground * u_g[quads_sec]))
        for line, idx in zip(ground_lines, ground_groups):
            gp = node_xy[idx] + anim_scale_ground * u_g[idx]
            line.set_data(gp[:, 0], gp[:, 1])
        ring_sec.set_segments(_ring_segments(ring_xy + anim_scale_ground * ring_u))
        ring_sec.set_array(ring_m[k])
        arrows.set_UVC(np.zeros(6), np.full(6, -arrow_h * lam[k]))
        mesh_pipe.set_segments(_edges(node_xy[quads_pipe] + anim_scale_pipe * (u_g[quads_pipe] - ring_mean)))
        ring_pipe.set_segments(_ring_segments(ring_xy + anim_scale_pipe * (ring_u - ring_mean)))
        ring_pipe.set_array(ring_m[k])
        marker_set.set_xdata([q_kpa[k], q_kpa[k]])
        marker_def.set_xdata([q_kpa[k], q_kpa[k]])
        info.set_text(
            f"surcharge q = {q_kpa[k]:5.1f} kPa  (load factor {lam[k]:.2f})\n"
            f"pad-centre settlement {settle_pad[k]:6.2f} mm\n"
            f"pipe mean settlement {settle_pipe[k]:6.2f} mm\n"
            f"pipe ΔD vertical {dd_v[k]:+.3f} mm, horizontal {dd_h[k]:+.3f} mm\n"
            f"crown moment change {crown_m[k]:+.2f} N·mm/mm"
        )
        return []

    anim = animation.FuncAnimation(fig, update, frames=len(lam), interval=1000.0 / anim_fps, blit=False)
    anim.save(str(output_dir / "vis_07_surcharge_animation.gif"), writer="pillow", fps=anim_fps, dpi=90)
    html = anim.to_jshtml(fps=anim_fps, default_mode="loop")
    (output_dir / "vis_07_surcharge_animation.html").write_text(html, encoding="utf-8")
    update(len(lam) - 1)
    fig.savefig(output_dir / "vis_07_surcharge_final.png", dpi=110)
    plt.close(fig)


def post_process(odb, output_dir: Path) -> None:
    """Write the response database, the deformed-shape checkpoint and the surcharge animation.

    Args:
        odb: CreateODB instance returned by run_analysis().
        output_dir: Folder for the ODB files, HTML checkpoints and animation.
    """
    odb.save_response()
    if not _headless():
        # True-scale total displacement: the wrapper default (scale 10) exaggerates the ~2 m gravity
        # settlement and makes the surface look sunk. The surcharge response is in the animation.
        vis_defo(output_dir, filename="vis_05_defo_surcharge.html", odb_tag=ODB_TAG, resp_dof="UY", scale=1.0)
        write_surcharge_animation(output_dir)


def _increment(state: dict, base: dict) -> dict:
    """Change in the pipe and ground quantities from the gravity state (the existing pipe).

    Args:
        state: Later stage from collect_state().
        base: Gravity stage from collect_state().

    Returns:
        Dictionary of differences in mm and N·mm/mm.
    """
    return {
        "pipe_dD_vertical_mm": state["pipe_dD_vertical_mm"] - base["pipe_dD_vertical_mm"],
        "pipe_dD_horizontal_mm": state["pipe_dD_horizontal_mm"] - base["pipe_dD_horizontal_mm"],
        "pipe_mean_uy_mm": state["pipe_mean_uy_mm"] - base["pipe_mean_uy_mm"],
        "pipe_moment_at_deg_N_mm_per_mm": {
            key: state["pipe_moment_at_deg_N_mm_per_mm"][key] - base["pipe_moment_at_deg_N_mm_per_mm"][key]
            for key in state["pipe_moment_at_deg_N_mm_per_mm"]
        },
        "ground_uy_mm": {key: state["ground_uy_mm"][key] - base["ground_uy_mm"][key]
                         for key in state["ground_uy_mm"]},
    }


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build the model on the cut section, run gravity and the surcharge, and write the outputs.

    Args:
        output_dir: Folder for the ODB files, HTML checkpoints, frames and results.json.

    Returns:
        The populated CreateODB instance (save_response() is called in post_process).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    mesh = build_mesh()
    section = define_sections()
    init_model()
    define_materials(mesh)
    define_nodes(mesh)
    define_boundary_conditions(mesh)
    vis_nodes(output_dir)
    define_elements(mesh, section)
    vis_model(output_dir)
    odb = create_odb(output_dir)
    define_gravity_loads(mesh)
    define_surcharge_loads(mesh)
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)
    results: dict = {}
    run_gravity(odb, mesh, results)
    frames = run_surcharge(odb, mesh, results)
    results["increment_surcharge_vs_gravity"] = _increment(results["surcharge_final"], results["gravity"])
    save_frames(output_dir, mesh, frames)
    (output_dir / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return odb


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
