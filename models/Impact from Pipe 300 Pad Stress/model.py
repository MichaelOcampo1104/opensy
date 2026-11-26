# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Impact from Pipe 300 Pad Stress — soil stress under a 75 kPa surcharge carried by a pad foundation
UniqueID : Impact from Pipe 300 Pad Stress
Author   : Michael Ocampo
Date     : 2026-11-26
Purpose  : Vertical and horizontal soil stress increase (kPa) from a 75 kPa surcharge, for a flexible load on the ground and for a bonded pad foundation of different thickness and modulus, beside a 300 mm pipe. Placeholder soil, pad and pipe data.
Ref      : No published source. Geometry from "Impact to 300mm Pipe.dxf" in the folder "Impact from Pipe 300".
Units    : N, mm, MPa

Documented exception to the SmartAnalyze mandate (AGENT.md §3c, §10): gravity and the surcharge ramp run
in manual ops.analyze() loops with a load-controlled ramp (AGENT.md §12z). Only the base case writes the
opstool checkpoints and the response database; the pad cases write the stress outputs only.
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
from matplotlib.collections import PolyCollection  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402
import openseespy.opensees as ops  # noqa: E402
import opstool as opst  # noqa: E402

# Add standards/ to path if running standalone
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *  # noqa: F401,F403  — N, mm, MPa, GPa, m, kN, kPa
from vis_utils import _headless, vis_defo, vis_loads, vis_model, vis_nodes, vis_pre_analysis  # noqa: E402

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# Soil quads and soil nodes use the gmsh mesh tags. The bases below keep the other families apart.
MAT_SOIL = 1                 # ElasticIsotropic, plane strain (placeholder soil)
MAT_PAD = 2                  # ElasticIsotropic, plane strain (pad foundation)
TRANSF_RING = 1              # geomTransf for the pipe ring
TS_CONST = 1                 # constant factor 1.0: pipe self-weight, applied in full
TS_ZERO = 2                  # constant factor 0.0: surcharge pattern before the ramp
TS_RAMP = 3                  # linear time series: load factor of the surcharge
PAT_WEIGHT = 1               # pipe self-weight pattern
PAT_SURCHARGE = 2            # surcharge pattern
NODE_PADCOPY_BASE = 4000000  # pad base nodes separated from the soil in the interface models: + k
ELE_PADIF_BASE = 5000000     # pad interface springs (zeroLength): ELE_PADIF_BASE + k
MAT_PADIF_N_BASE = 3000000   # pad interface normal materials (ENT): MAT_PADIF_N_BASE + k
MAT_PADIF_T_BASE = 6000000   # pad interface shear materials (ElasticPP, friction model): MAT_PADIF_T_BASE + k
ODB_TAG = 1                  # CreateODB tag
GMSH_QUAD4 = 3               # gmsh element type code for 4-node quadrangles
NODE_BEAM_BASE = 1000000     # pipe ring nodes (3 DOF): NODE_BEAM_BASE + k
NODE_AUX_BASE = 2000000      # interface nodes on the pipe outer surface (2 DOF): NODE_AUX_BASE + k
ELE_BEAM_BASE = 3000000      # pipe ring beam elements: ELE_BEAM_BASE + k
ELE_SPRING_BASE = 4000000    # interface springs (zeroLength): ELE_SPRING_BASE + k
MAT_IF_N_BASE = 1000000      # normal interface materials (ENT, compression only): MAT_IF_N_BASE + k
MAT_IF_T_BASE = 2000000      # tangential interface materials (ElasticPP): MAT_IF_T_BASE + k

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# PLACEHOLDER SOIL, PAD AND PIPE VALUES — replace with site data before using any result (see README.md).
# Geometry is read from the DXF (metres) and converted here to mm.

# Soil box: the converged box of Impact from Pipe 300 (see its README.md).
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

# Pipe-soil interface placeholder (as in Impact from Pipe 300)
interface_thickness = 25.0 * mm             # PLACEHOLDER
k_interface = e_soil / interface_thickness  # N/mm³ per unit area (normal)
tau_interface = 30.0 * kPa                  # PLACEHOLDER
interface_yield_disp = 2.0 * mm             # PLACEHOLDER
k_tangent = tau_interface / interface_yield_disp

# Open cut: DXF Boundary polyline, 45-degree sides, floor at y = 8.257 m. The soil is already cut.
trench_floor_y = 8.257244422105941 * m
trench_x_min = 2.500019919969417 * m
trench_x_max = 10.40336536539507 * m
trench_outline = [
    (2.500019919969417 * m, y_ground),
    (4.246883620608059 * m, trench_floor_y),
    (8.652339545982613 * m, trench_floor_y),
    (10.40336536539507 * m, y_ground),
]

# Surcharge pad (DXF Pad_load line) and the surcharge itself
pad_left = 16.83036756027832 * m
pad_right = 21.74491451144058 * m
pad_width = pad_right - pad_left
surcharge = 75.0 * kPa
nu_pad = 0.20                               # PLACEHOLDER
gamma_pad = 24.0 * kN / m**3                # PLACEHOLDER: concrete self-weight

# Cases. Thickness None = the surcharge is applied straight on the ground (flexible load).
# The pad is bonded to the ground and carries the surcharge on its top face.
pad_cases = [
    {"name": "flexible_no_pad", "thickness": None, "e_pad": None},
    {"name": "pad_t0p3_E30", "thickness": 0.3 * m, "e_pad": 30.0 * GPa},
    {"name": "pad_t0p6_E30", "thickness": 0.6 * m, "e_pad": 30.0 * GPa},
    {"name": "pad_t1p2_E30", "thickness": 1.2 * m, "e_pad": 30.0 * GPa},
    {"name": "pad_t0p6_E3", "thickness": 0.6 * m, "e_pad": 3.0 * GPa},
]

# Mesh sizes below are gmsh targets. gmsh halves them when it makes quads, so the element sizes are about half.
# Pipe and cut settings of Impact from Pipe 300 Coarse Mesh, with refined zones under and beside the pad. The
# 4 m far-field target is too coarse for a 4.9 m load at depth, so the zones reach 12 m below ground.
h_pipe = 25.0 * mm
h_trench = 400.0 * mm
h_far = 4000.0 * mm
h_pad_max = 500.0 * mm                      # largest target under the pad, and in the zone under the flexible load
h_mid = 1000.0 * mm                         # target in the wider zone beside the pad
pad_size_divisor = 4                        # target size in the pad = thickness / 4 (about 8 elements through it)
zone_fine_margin = 1.5 * m                  # h_pad_max zone reaches this far beyond each pad edge
zone_mid_margin = 6.0 * m                   # h_mid zone reaches this far beyond each pad edge
zone_depth = 12.0 * m                       # both zones reach this depth below the ground
zone_above = 1.0 * m                        # zones rise this far above the ground (pad cases)
pad_transition = 0.5 * m                    # soil beside and below the pad grades to h_pad_max over this distance
box_thickness = 3.0 * m                     # transition from the zones to the far field
coord_tol = 1.0e-3 * mm
unit_length = 1.0 * mm

# Pad-soil interface: used by the frictionless and friction models only (the default is a bonded pad)
pad_interface_thickness = 1.0 * mm          # PLACEHOLDER: normal and shear stiffness per area = E_soil / this
pad_friction_coefficient = 0.4              # PLACEHOLDER: Coulomb coefficient of the friction model

# Analysis controls
n_surcharge_steps = 20
tol_disp = 1.0e-6 * mm
max_iter = 60


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Reset OpenSees and start a 2D model with 2 DOF per node (soil, pad and interface nodes).

    The pipe ring uses 3-DOF nodes; they are created in define_nodes().
    """
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 2)


def pad_mesh_size(case: dict) -> float:
    """Target mesh size in the pad: thickness / pad_size_divisor, at most h_pad_max. The flexible case uses h_pad_max.

    Args:
        case: One entry of pad_cases.

    Returns:
        Target gmsh size in mm.
    """
    if case["thickness"] is None:
        return h_pad_max
    return min(case["thickness"] / pad_size_divisor, h_pad_max)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials(mesh: dict, case: dict) -> None:
    """Define the soil, the pad (if any) and one normal and one tangential material per interface spring.

    Args:
        mesh: Mesh dictionary from build_mesh(). Its 'iface_length' list sets the spring count.
        case: The case being run; its e_pad sets the pad modulus.
    """
    ops.nDMaterial("ElasticIsotropic", MAT_SOIL, e_soil, nu_soil)
    if case["thickness"] is not None:
        ops.nDMaterial("ElasticIsotropic", MAT_PAD, case["e_pad"], nu_pad)
    for k, length in enumerate(mesh["iface_length"]):
        spring_n = k_interface * length * unit_length          # N/mm for this tributary length
        spring_t = k_tangent * length * unit_length
        ops.uniaxialMaterial("ENT", MAT_IF_N_BASE + k, spring_n)
        # ElasticPP yields at a displacement, so the yield force is spring_t * interface_yield_disp
        ops.uniaxialMaterial("ElasticPP", MAT_IF_T_BASE + k, spring_t, interface_yield_disp)
    if mesh.get("interface", "bonded") != "bonded" and case["thickness"] is not None:
        k_area = e_soil / pad_interface_thickness
        for k, (_, length) in enumerate(mesh["ground_tribs"]):
            k_node = k_area * length * unit_length                 # N/mm for this pad base node
            ops.uniaxialMaterial("ENT", MAT_PADIF_N_BASE + k, k_node)
            if mesh["interface"] == "friction":
                guess = mesh.get("normal_guess")
                n_est = guess[k] if guess is not None else (surcharge + gamma_pad * case["thickness"]) * length * unit_length   # N, sets the friction limit
                ops.uniaxialMaterial("ElasticPP", MAT_PADIF_T_BASE + k, k_node,
                                     pad_friction_coefficient * n_est / k_node)


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


def _tributaries(nodes: dict, ordered: list) -> list:
    """Tributary length (mm) of each node on the pad, for a line load of pad_width (N/mm² x mm per node).

    Args:
        nodes: Node coordinates (mm).
        ordered: Node tags on one horizontal line, sorted by x.

    Returns:
        List of (node tag, tributary length in mm) for the nodes under the pad.

    Raises:
        RuntimeError: If the tributary lengths do not add up to the pad width.
    """
    tribs = []
    for i, tag in enumerate(ordered):
        x = nodes[tag][0]
        if not (pad_left - coord_tol <= x <= pad_right + coord_tol):
            continue
        x_prev = nodes[ordered[i - 1]][0] if i > 0 else x
        x_next = nodes[ordered[i + 1]][0] if i < len(ordered) - 1 else x
        lo = max(0.5 * (x + x_prev), pad_left)
        hi = min(0.5 * (x + x_next), pad_right)
        if hi > lo:
            tribs.append((tag, hi - lo))
    if abs(sum(length for _, length in tribs) - pad_width) > coord_tol:
        raise RuntimeError("pad tributary lengths do not add up to the pad width")
    return tribs


def build_mesh(case: dict) -> dict:
    """Mesh the soil box (and the pad, if any) with gmsh.

    The open cut is meshed so the boundary matches the other models, but its quads are left out of the
    model: the soil is already cut. The pad is a rectangle on the ground, conforming to the soil mesh.

    Args:
        case: One entry of pad_cases.

    Returns:
        Dictionary with node coordinates (mm), the soil and pad quads (with a 'pad' flag), the node tags in
        the model, the interface nodes with their angles and tributary lengths, boundary node lists, the
        surcharge tributaries and the node use counts.

    Raises:
        RuntimeError: If the mesh has a non-quad element or the surcharge does not add up.
    """
    t = case["thickness"] or 0.0
    h_box = pad_mesh_size(case)
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add("impact_from_pipe_300_pad")
        occ = gmsh.model.occ
        rect = occ.addRectangle(x_left, y_base, 0.0, x_right - x_left, y_ground - y_base)
        hole = occ.addDisk(pipe_centre_x, pipe_centre_y, 0.0, pipe_radius_out, pipe_radius_out)
        soil_dimtags, _ = occ.cut([(2, rect)], [(2, hole)])
        cut_pts = [occ.addPoint(x, y, 0.0) for x, y in trench_outline]
        cut_lines = [occ.addLine(cut_pts[i], cut_pts[(i + 1) % len(cut_pts)]) for i in range(len(cut_pts))]
        cut_surface = occ.addPlaneSurface([occ.addCurveLoop(cut_lines)])
        tools = [(2, cut_surface)]
        if t > 0.0:
            pad_rect = occ.addRectangle(pad_left, y_ground, 0.0, pad_width, t)
            tools.append((2, pad_rect))
        pad_pts = [occ.addPoint(pad_left, y_ground, 0.0), occ.addPoint(pad_right, y_ground, 0.0)]
        occ.fragment(soil_dimtags, tools + [(0, p) for p in pad_pts])
        occ.synchronize()

        cut_tags, pad_tags, soil_tags = [], [], []
        for _, tag in gmsh.model.getEntities(2):
            cx, cy, _ = occ.getCenterOfMass(2, tag)
            if trench_x_min < cx < trench_x_max and trench_floor_y < cy < y_ground:
                cut_tags.append(tag)
            elif t > 0.0 and pad_left < cx < pad_right and y_ground < cy < y_ground + t:
                pad_tags.append(tag)
            else:
                soil_tags.append(tag)

        hole_box = (pipe_centre_x - pipe_radius_out, pipe_centre_y - pipe_radius_out,
                    pipe_centre_x + pipe_radius_out, pipe_centre_y + pipe_radius_out)
        cut_box = (trench_x_min, trench_floor_y, trench_x_max, y_ground)
        pipe_curves, cut_curves = [], []
        for _, tag in gmsh.model.getEntities(1):
            bb = gmsh.model.getBoundingBox(1, tag)
            if _within(bb, hole_box):
                pipe_curves.append(tag)
            if _within(bb, cut_box):
                cut_curves.append(tag)

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

        def _box(x0: float, x1: float, y0: float, y1: float, v_in: float, v_out: float, thick: float) -> int:
            box = field.add("Box")
            field.setNumber(box, "VIn", v_in)
            field.setNumber(box, "VOut", v_out)
            field.setNumber(box, "XMin", x0)
            field.setNumber(box, "XMax", x1)
            field.setNumber(box, "YMin", y0)
            field.setNumber(box, "YMax", y1)
            field.setNumber(box, "Thickness", thick)
            return box

        f_pipe = _size_threshold(pipe_curves, h_pipe, 300.0 * mm, 6000.0 * mm)
        f_cut = _size_threshold(cut_curves, h_trench, 500.0 * mm, 4000.0 * mm)
        zone_bottom = y_ground - zone_depth
        zone_top = y_ground + t + zone_above
        f_fine = _box(pad_left - zone_fine_margin, pad_right + zone_fine_margin, zone_bottom, zone_top,
                      h_pad_max, h_far, box_thickness)
        f_mid = _box(pad_left - zone_mid_margin, pad_right + zone_mid_margin, zone_bottom, zone_top,
                     h_mid, h_far, box_thickness)
        fields = [f_pipe, f_cut, f_fine, f_mid]
        if t > 0.0:
            # The pad interior takes the pad size. Soil beside and below the pad grades from the pad size to
            # h_pad_max over pad_transition; StopAtDistMax leaves the field unconstrained beyond that, so it does
            # not cap the far field.
            pad_box = (pad_left - 1.0 * m, y_ground - 1.0 * m, pad_right + 1.0 * m, y_ground + t + 1.0 * m)
            pad_curves = [tag for _, tag in gmsh.model.getEntities(1)
                          if _within(gmsh.model.getBoundingBox(1, tag), pad_box)]
            if not pad_curves:
                raise RuntimeError("no pad outline curves found for the mesh size field")
            dist_pad = field.add("Distance")
            field.setNumbers(dist_pad, "CurvesList", pad_curves)
            field.setNumber(dist_pad, "Sampling", 1000)
            thr_pad = field.add("Threshold")
            field.setNumber(thr_pad, "InField", dist_pad)
            field.setNumber(thr_pad, "SizeMin", h_box)
            field.setNumber(thr_pad, "SizeMax", h_pad_max)
            field.setNumber(thr_pad, "DistMin", 0.0)
            field.setNumber(thr_pad, "DistMax", pad_transition)
            field.setNumber(thr_pad, "StopAtDistMax", 1)
            f_pad_in = _box(pad_left, pad_right, y_ground, y_ground + t, h_box, 1.0e6 * mm, 0.0)
            fields += [thr_pad, f_pad_in]
        f_min = field.add("Min")
        field.setNumbers(f_min, "FieldsList", fields)
        field.setAsBackgroundMesh(f_min)

        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh.option.setNumber("Mesh.Algorithm", 8)
        gmsh.option.setNumber("Mesh.RecombineAll", 1)
        gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
        gmsh.model.mesh.generate(2)

        raw_tags, raw_xyz, _ = gmsh.model.mesh.getNodes()
        nodes = {int(t_): (float(raw_xyz[3 * i]), float(raw_xyz[3 * i + 1])) for i, t_ in enumerate(raw_tags)}

        quads_all = []
        for tag in cut_tags + pad_tags + soil_tags:
            elem_types, elem_tags, elem_nodes = gmsh.model.mesh.getElements(2, tag)
            for elem_type, tags_list, node_list in zip(elem_types, elem_tags, elem_nodes):
                if elem_type != GMSH_QUAD4:
                    raise RuntimeError(f"surface {tag} has element type {elem_type}; only quads are supported")
                for e in range(len(tags_list)):
                    conn = [int(v) for v in node_list[4 * e:4 * e + 4]]
                    if _quad_area(nodes, tuple(conn)) < 0.0:
                        conn = [conn[0], conn[3], conn[2], conn[1]]
                    quads_all.append({"tag": int(tags_list[e]), "nodes": tuple(conn),
                                      "cut": tag in cut_tags, "pad": tag in pad_tags})

        # The cut is already excavated: its quads are not part of the model.
        quads = [q for q in quads_all if not q["cut"]]
        node_use: dict = {}
        for q in quads:
            for n in q["nodes"]:
                node_use[n] = node_use.get(n, 0) + 1
        soil_nodes = sorted(node_use)

        iface = sorted(
            ((t_, math.atan2(y - pipe_centre_y, x - pipe_centre_x)) for t_, (x, y) in nodes.items()
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

        base = [t_ for t_, (x, y) in nodes.items() if abs(y - y_base) <= coord_tol and node_use.get(t_, 0) > 0]
        left = [t_ for t_, (x, y) in nodes.items() if abs(x - x_left) <= coord_tol and node_use.get(t_, 0) > 0]
        right = [t_ for t_, (x, y) in nodes.items() if abs(x - x_right) <= coord_tol and node_use.get(t_, 0) > 0]
        ground = sorted((t_ for t_, (x, y) in nodes.items()
                         if abs(y - y_ground) <= coord_tol and node_use.get(t_, 0) > 0),
                        key=lambda t_: nodes[t_][0])
        if t > 0.0:
            top = sorted((t_ for t_, (x, y) in nodes.items()
                          if abs(y - (y_ground + t)) <= coord_tol and node_use.get(t_, 0) > 0),
                         key=lambda t_: nodes[t_][0])
        else:
            top = ground
        load_tribs = _tributaries(nodes, top)

        print(f"mesh [{case['name']}]: {len(soil_nodes)} nodes, {len(quads)} quads "
              f"({sum(q['pad'] for q in quads)} in the pad), {count} interface nodes, element size {h_box:.0f} mm",
              flush=True)
        return {
            "nodes": nodes,
            "quads": quads,
            "soil_nodes": soil_nodes,
            "iface": iface,
            "iface_length": iface_length,
            "ground": ground,
            "load_tribs": load_tribs,
            "ground_tribs": _tributaries(nodes, ground),
            "base": base,
            "left": left,
            "right": right,
            "node_use": node_use,
            "pad_thickness": t,
        }
    finally:
        gmsh.finalize()


def define_nodes(mesh: dict) -> None:
    """Create the pipe ring nodes (3 DOF), then the soil and pad nodes and the interface nodes (2 DOF).

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
    if mesh.get("interface", "bonded") != "bonded" and mesh.get("pad_thickness", 0.0) > 0.0:
        mesh["pad_copy"] = {}
        for k, (tag, _) in enumerate(mesh["ground_tribs"]):
            x, y = mesh["nodes"][tag]
            ops.node(NODE_PADCOPY_BASE + k, x, y)
            mesh["pad_copy"][tag] = NODE_PADCOPY_BASE + k
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
    if mesh.get("pad_copy"):
        x_c = 0.5 * (pad_left + pad_right)
        centre = min(mesh["ground_tribs"], key=lambda item: abs(mesh["nodes"][item[0]][0] - x_c))[0]
        ops.fix(mesh["pad_copy"][centre], 1, 0)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements(mesh: dict, section: dict, case: dict) -> None:
    """Create the soil and pad quads (self-weight as body force), the pipe ring beams and the springs.

    Args:
        mesh: Mesh dictionary from build_mesh().
        section: Pipe ring section from define_sections().
        case: The case being run.
    """
    count = len(mesh["iface"])
    ops.model("basic", "-ndm", 2, "-ndf", 3)          # frame elements need 3 DOF per node
    ops.geomTransf("Linear", TRANSF_RING)
    for k in range(count):
        ops.element("elasticBeamColumn", ELE_BEAM_BASE + k,
                    NODE_BEAM_BASE + k, NODE_BEAM_BASE + (k + 1) % count,
                    section["area"], section["e_plane"], section["inertia"], TRANSF_RING)
    ops.model("basic", "-ndm", 2, "-ndf", 2)          # soil and pad quads and springs need 2 DOF per node
    for q in mesh["quads"]:
        if q["pad"]:
            pad_nodes = tuple(mesh.get("pad_copy", {}).get(n, n) for n in q["nodes"])
            ops.element("quad", q["tag"], *pad_nodes, unit_length, "PlaneStrain", MAT_PAD,
                        0.0, 0.0, 0.0, -gamma_pad)
        else:
            ops.element("quad", q["tag"], *q["nodes"], unit_length, "PlaneStrain", MAT_SOIL,
                        0.0, 0.0, 0.0, -gamma_soil)
    for k, (tag, theta) in enumerate(mesh["iface"]):
        c, s = math.cos(theta), math.sin(theta)
        # local x = radial outward (normal), local y = tangential; node I is the pipe side
        ops.element("zeroLength", ELE_SPRING_BASE + k, NODE_AUX_BASE + k, tag,
                    "-mat", MAT_IF_N_BASE + k, MAT_IF_T_BASE + k, "-dir", 1, 2,
                    "-orient", c, s, 0.0, -s, c, 0.0)
    if mesh.get("pad_copy"):
        for k, (tag, _) in enumerate(mesh["ground_tribs"]):
            if mesh["interface"] == "friction":
                mats, dirs = [MAT_PADIF_T_BASE + k, MAT_PADIF_N_BASE + k], [1, 2]
            else:
                mats, dirs = [MAT_PADIF_N_BASE + k], [2]
            ops.element("zeroLength", ELE_PADIF_BASE + k, tag, mesh["pad_copy"][tag],
                        "-mat", *mats, "-dir", *dirs)


# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(output_dir: Path) -> "opst.post.CreateODB":
    """Create the response database for the base case (used by the deformed-shape checkpoint).

    Args:
        output_dir: Folder for the ODB files.

    Returns:
        The CreateODB instance.
    """
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=ODB_TAG, save_nodal_resp=True, save_frame_resp=True)
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads(mesh: dict) -> None:
    """Apply the pipe self-weight as constant nodal loads. Soil and pad self-weight are in the quads.

    Args:
        mesh: Mesh dictionary from build_mesh().
    """
    ops.timeSeries("Constant", TS_CONST)
    ops.pattern("Plain", PAT_WEIGHT, TS_CONST)
    weight_per_length = pipe_unit_weight * pipe_area_wall          # N per mm of pipe length
    for k, length in enumerate(mesh["iface_length"]):
        ops.load(NODE_BEAM_BASE + k, 0.0, -weight_per_length * length, 0.0)


def _surcharge_pattern(mesh: dict, ts_tag: int) -> None:
    """Create the surcharge pattern on the loaded nodes (the pad top, or the ground when there is no pad).

    Args:
        mesh: Mesh dictionary from build_mesh().
        ts_tag: Time series tag (TS_ZERO before the ramp, TS_RAMP for the surcharge).
    """
    ops.pattern("Plain", PAT_SURCHARGE, ts_tag)
    for tag, length in mesh["load_tribs"]:
        ops.load(tag, 0.0, -surcharge * length * unit_length)


def define_surcharge_loads(mesh: dict) -> None:
    """Define the surcharge with a zero factor so the checkpoints show it; it is switched on later.

    Args:
        mesh: Mesh dictionary from build_mesh().
    """
    ops.timeSeries("Constant", TS_ZERO, "-factor", 0.0)
    _surcharge_pattern(mesh, TS_ZERO)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
class _NoODB:
    """Stand-in for CreateODB in the pad cases, which write no response database."""

    def fetch_response_step(self):
        return None

    def save_response(self):
        return None


def _set_solver() -> None:
    """Solver set-up shared by the manual static loops (wipeAnalysis first, AGENT.md §12h-3)."""
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


def collect_state(mesh: dict, load_factor: float = 0.0) -> dict:
    """Read the pipe, interface, ground and equilibrium quantities.

    Args:
        mesh: Mesh dictionary from build_mesh().
        load_factor: Surcharge load factor applied at this state.

    Returns:
        Dictionary of floats in N, mm and MPa (per 1 mm of pipe length for forces and moments).
    """
    ops.reactions()
    base_ry = sum(ops.nodeReaction(tag)[1] for tag in mesh["base"])
    soil_weight = 0.0
    pad_weight = 0.0
    for q in mesh["quads"]:
        area = _quad_area(mesh["nodes"], q["nodes"])
        if q["pad"]:
            pad_weight += area * gamma_pad * unit_length
        else:
            soil_weight += area * gamma_soil * unit_length
    pipe_weight = pipe_unit_weight * pipe_area_wall * sum(mesh["iface_length"])
    surcharge_total = surcharge * pad_width * unit_length * load_factor

    angles = [theta for _, theta in mesh["iface"]]
    n = len(angles)
    uy = [ops.nodeDisp(NODE_BEAM_BASE + k, 2) for k in range(n)]
    ux = [ops.nodeDisp(NODE_BEAM_BASE + k, 1) for k in range(n)]
    i_top = _nearest(angles, math.pi / 2.0)
    i_bot = _nearest(angles, -math.pi / 2.0)
    i_right = _nearest(angles, 0.0)
    i_left = _nearest(angles, math.pi)
    moment_at_deg = {}
    for label, target in (("0", 0.0), ("90", math.pi / 2.0), ("180", math.pi), ("270", -math.pi / 2.0)):
        i = _nearest(angles, target)
        moment_at_deg[label] = ops.eleResponse(ELE_BEAM_BASE + i, "localForce")[2]
    ground_uy = {}
    for label, x in (("x_pipe", pipe_centre_x), ("x_pad_centre", 0.5 * (pad_left + pad_right))):
        ground_uy[label] = ops.nodeDisp(_nearest_ground(mesh, x), 2)

    return {
        "load_factor": load_factor,
        "base_sum_ry_N": base_ry,
        "soil_weight_N": soil_weight,
        "pad_weight_N": pad_weight,
        "pipe_weight_N": pipe_weight,
        "surcharge_N": surcharge_total,
        "pipe_mean_uy_mm": sum(uy) / n,
        "pipe_dD_vertical_mm": uy[i_top] - uy[i_bot],
        "pipe_dD_horizontal_mm": ux[i_right] - ux[i_left],
        "pipe_moment_at_deg_N_mm_per_mm": moment_at_deg,
        "ground_uy_mm": ground_uy,
    }


def _stresses(mesh: dict) -> np.ndarray:
    """Stress of every model quad at its Gauss-point average: sxx, syy, sxy in MPa (compression negative)."""
    out = np.empty((len(mesh["quads"]), 3))
    for i, q in enumerate(mesh["quads"]):
        s = ops.eleResponse(q["tag"], "stress")
        out[i, 0], out[i, 1], out[i, 2] = s[0], s[1], s[2]
    return out


_GAUSS_2X2 = [(xi, eta) for xi in (-1.0 / math.sqrt(3.0), 1.0 / math.sqrt(3.0))
              for eta in (-1.0 / math.sqrt(3.0), 1.0 / math.sqrt(3.0))]
_QUAD_CORNERS = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]     # natural coordinates of quad nodes 1 to 4


def _quad_stiffness(xs: list, ys: list, e_mod: float, nu: float) -> np.ndarray:
    """8 x 8 stiffness of one plane-strain quad: the same bilinear element and 2 x 2 Gauss rule that OpenSees uses.

    Args:
        xs: Four x coordinates (mm), nodes 1 to 4 in counter-clockwise order.
        ys: Four y coordinates (mm).
        e_mod: Young's modulus (MPa).
        nu: Poisson's ratio.

    Returns:
        Stiffness (N/mm) with DOF order (u1, v1, u2, v2, u3, v3, u4, v4), thickness unit_length.
    """
    c = e_mod / ((1.0 + nu) * (1.0 - 2.0 * nu))
    d_mat = c * np.array([[1.0 - nu, nu, 0.0], [nu, 1.0 - nu, 0.0], [0.0, 0.0, 0.5 * (1.0 - 2.0 * nu)]])
    k = np.zeros((8, 8))
    for xi, eta in _GAUSS_2X2:
        d_xi = [0.25 * cxi * (1.0 + ceta * eta) for cxi, ceta in _QUAD_CORNERS]
        d_eta = [0.25 * ceta * (1.0 + cxi * xi) for cxi, ceta in _QUAD_CORNERS]
        g11 = sum(x * d for x, d in zip(xs, d_xi))         # dx/dxi
        g12 = sum(y * d for y, d in zip(ys, d_xi))         # dy/dxi
        g21 = sum(x * d for x, d in zip(xs, d_eta))        # dx/deta
        g22 = sum(y * d for y, d in zip(ys, d_eta))        # dy/deta
        det = g11 * g22 - g12 * g21
        b = np.zeros((3, 8))
        for i in range(4):
            dn_dx = (g22 * d_xi[i] - g12 * d_eta[i]) / det
            dn_dy = (-g21 * d_xi[i] + g11 * d_eta[i]) / det
            b[0, 2 * i] = dn_dx
            b[1, 2 * i + 1] = dn_dy
            b[2, 2 * i] = dn_dy
            b[2, 2 * i + 1] = dn_dx
        k += b.T @ d_mat @ b * abs(det) * unit_length
    return k


def _soil_displacements(mesh: dict) -> dict:
    """Horizontal and vertical displacement (mm) of every soil node, as node tag -> (ux, uy)."""
    return {n: (ops.nodeDisp(n, 1), ops.nodeDisp(n, 2)) for n in mesh["soil_nodes"]}


def _soil_force_change(mesh: dict, u_ref: dict, u_fin: dict) -> dict:
    """Change in the vertical force that each soil quad applies to its nodes, from the surcharge.

    The soil is linear elastic, so the change in internal force is exactly K (u_fin - u_ref) for each element. Pad
    quads are left out: the change at the ground nodes under the pad is the load the pad transmits to the soil.

    Args:
        mesh: Mesh dictionary from build_mesh().
        u_ref: Node displacements after gravity, from _soil_displacements().
        u_fin: Node displacements after the surcharge.

    Returns:
        Dictionary of node tag -> change in the vertical internal force (N per 1 mm slice), summed over soil quads.
    """
    forces: dict = {}
    for q in mesh["quads"]:
        if q["pad"]:
            continue
        xs = [mesh["nodes"][n][0] for n in q["nodes"]]
        ys = [mesh["nodes"][n][1] for n in q["nodes"]]
        k = _quad_stiffness(xs, ys, e_soil, nu_soil)
        du = np.concatenate([np.subtract(u_fin[n], u_ref[n]) for n in q["nodes"]])
        df = k @ du
        for i, n in enumerate(q["nodes"]):
            forces[n] = forces.get(n, 0.0) + float(df[2 * i + 1])
    return forces


def run_gravity(odb, mesh: dict, results: dict) -> None:
    """Gravity on the cut section: soil, pad and pipe self-weight in one full step (body forces are not
    scaled by the load factor in OpenSeesPy, checked in Impact from Pipe 300).

    Args:
        odb: CreateODB or _NoODB.
        mesh: Mesh dictionary from build_mesh().
        results: Results dictionary, updated in place.
    """
    _set_solver()
    ops.integrator("LoadControl", 1.0)
    _advance("gravity")
    odb.fetch_response_step()
    ops.loadConst("-time", 0.0)
    results["gravity"] = collect_state(mesh)


def run_surcharge(odb, mesh: dict, results: dict, per_step_odb: bool = False) -> list:
    """Surcharge ramp on the pad (or the ground), in n_surcharge_steps steps.

    Args:
        odb: CreateODB or _NoODB.
        mesh: Mesh dictionary from build_mesh().
        results: Results dictionary, updated in place.
        per_step_odb: Write the database after every load step (for the stress sliders), not only at the end.

    Returns:
        Element stresses (MPa, see _stresses()) after each load step, for the stress animations.
    """
    ops.remove("loadPattern", PAT_SURCHARGE)
    ops.timeSeries("Linear", TS_RAMP)
    _surcharge_pattern(mesh, TS_RAMP)
    _set_solver()
    ops.integrator("LoadControl", 1.0 / n_surcharge_steps)
    steps = []
    for step in range(1, n_surcharge_steps + 1):
        _advance(f"surcharge step {step}")
        if per_step_odb:
            odb.fetch_response_step()
        steps.append(_stresses(mesh))
    if not per_step_odb:
        odb.fetch_response_step()
    results["surcharge_final"] = collect_state(mesh, load_factor=1.0)
    return steps


# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def summarise_case(case: dict, mesh: dict, results: dict, ref: np.ndarray, fin: np.ndarray,
                   d_if: dict) -> dict:
    """Stress increase (kPa) from the surcharge: depth profile under the pad centre, contact stress under the pad,
    and the stress at the pipe level.

    Args:
        case: The case being run.
        mesh: Mesh dictionary from build_mesh().
        results: Gravity and final surcharge states from collect_state().
        ref: Stresses after gravity (MPa).
        fin: Stresses after the surcharge (MPa).
        d_if: Change in the soil-side nodal vertical forces from the surcharge (N per 1 mm slice), from
            _soil_force_change().

    Returns:
        Dictionary with 'summary' (numbers for the JSON file) and 'data' (arrays for the figures).
    """
    kpa = 1000.0                                                 # MPa -> kPa
    dsig = -(fin - ref) * kpa                                    # kPa, compression positive
    cent = np.array([[sum(mesh["nodes"][n][0] for n in q["nodes"]) / 4.0,
                      sum(mesh["nodes"][n][1] for n in q["nodes"]) / 4.0] for q in mesh["quads"]])
    cx, cy = cent[:, 0], cent[:, 1]
    is_pad = np.array([q["pad"] for q in mesh["quads"]])
    x_c = 0.5 * (pad_left + pad_right)
    dsig_yy = dsig[:, 1]
    areas = np.array([abs(_quad_area(mesh["nodes"], q["nodes"])) for q in mesh["quads"]])

    # Depth profile: area-weighted mean vertical stress increase in 0.5 m depth bins, over a 2 m wide band
    # centred under the pad.
    band = (~is_pad) & (np.abs(cx - x_c) <= 1000.0)
    depth_all = (y_ground - cy[band]) / m
    val_all = dsig_yy[band]
    w_all = areas[band]
    edges = np.arange(0.0, 12.5, 0.5)
    centres, means = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = (depth_all >= lo) & (depth_all < hi)
        if sel.any():
            centres.append(0.5 * (lo + hi))
            means.append(float(np.sum(w_all[sel] * val_all[sel]) / np.sum(w_all[sel])))
    depth_m = np.array(centres)
    depth_vals = np.array(means)
    at_depth = {d: float(np.interp(d, depth_m, depth_vals)) for d in (1.0, 3.0, 5.0, 10.0)}

    # Contact stress from the soil side: minus the change in the soil elements' nodal vertical force at each ground
    # node under the pad (negative under load), per tributary length, so compression is positive as in dsig. The
    # total must equal the applied surcharge. Nodes at the pad edges carry mesh-dependent peaks, so the distribution
    # is also reported as 0.5 m bin averages across the pad.
    x_nodes = np.array([mesh["nodes"][tag][0] for tag, _ in mesh["ground_tribs"]])
    trib = np.array([length for _, length in mesh["ground_tribs"]])
    f_nodes = np.array([-d_if.get(tag, 0.0) for tag, _ in mesh["ground_tribs"]])
    contact_total_N = float(f_nodes.sum())
    contact_x_m = x_nodes / m
    contact_kpa = f_nodes / (trib * unit_length) * kpa
    n_bins = int(math.ceil(pad_width / (0.5 * m)))
    bin_of = np.minimum(np.floor((x_nodes - pad_left) / (0.5 * m)).astype(int), n_bins - 1)
    bin_x_m, bin_kpa = [], []
    for b in range(n_bins):
        sel = bin_of == b
        if sel.any():
            lo = pad_left + b * 0.5 * m
            hi = min(lo + 0.5 * m, pad_right)
            bin_x_m.append(0.5 * (lo + hi) / m)
            bin_kpa.append(float(f_nodes[sel].sum() / (trib[sel].sum() * unit_length) * kpa))
    bin_x_m = np.array(bin_x_m)
    bin_kpa = np.array(bin_kpa)

    near_pipe = (~is_pad) & (np.abs(cx - pipe_centre_x) < 250.0) & (np.abs(cy - pipe_centre_y) < 250.0)
    pipe_level = float(dsig_yy[near_pipe].mean()) if near_pipe.any() else float("nan")

    if case["thickness"] is None:
        kr = 0.0
        pad_weight_kpa = 0.0
    else:
        t = case["thickness"]
        kr = case["e_pad"] * t**3 / (12.0 * (1.0 - nu_pad**2)) / (e_soil * pad_width**3)
        pad_weight_kpa = gamma_pad * t * kpa

    settle = -(results["surcharge_final"]["ground_uy_mm"]["x_pad_centre"]
               - results["gravity"]["ground_uy_mm"]["x_pad_centre"])
    summary = {
        "name": case["name"],
        "pad_thickness_m": None if case["thickness"] is None else case["thickness"] / m,
        "pad_modulus_GPa": None if case["e_pad"] is None else case["e_pad"] / GPa,
        "relative_stiffness_K": kr,
        "pad_self_weight_kPa": pad_weight_kpa,
        "contact_nodal_max_kPa": float(contact_kpa.max()),
        "contact_nodal_min_kPa": float(contact_kpa.min()),
        "contact_bins_kPa": [round(float(v), 3) for v in bin_kpa],
        "contact_total_N": float(contact_total_N),
        "surcharge_N": float(results["surcharge_final"]["surcharge_N"]),
        "settlement_pad_centre_mm": float(settle),
        "dsig_yy_depth_1m_kPa": at_depth[1.0],
        "dsig_yy_depth_3m_kPa": at_depth[3.0],
        "dsig_yy_depth_5m_kPa": at_depth[5.0],
        "dsig_yy_depth_10m_kPa": at_depth[10.0],
        "dsig_yy_pipe_level_kPa": pipe_level,
        "soil_nodes": len(mesh["soil_nodes"]),
        "quads": len(mesh["quads"]),
        "pad_quads": int(is_pad.sum()),
    }
    # Stress maps show soil only; the pad is drawn as an outline.
    window = (~is_pad) & (cx >= 0.0) & (cx <= 36000.0) & (cy >= -15000.0) & (cy <= 12500.0)
    polys = np.array([[mesh["nodes"][n] for n in q["nodes"]] for q, w in zip(mesh["quads"], window) if w]) / m
    data = {
        "win_polys": polys,
        "win_vals": dsig_yy[window],
        "depth_m": depth_m,
        "depth_kPa": depth_vals,
        "contact_x_m": contact_x_m,
        "contact_kPa": contact_kpa,
        "contact_bin_x_m": bin_x_m,
        "contact_bin_kPa": bin_kpa,
        "cx": cx, "cy": cy, "is_pad": is_pad,
        "dsig_xx": dsig[:, 0], "dsig_yy": dsig_yy, "dsig_xy": dsig[:, 2],
    }
    return {"summary": summary, "data": data}


def run_case(output_dir: Path, case: dict, interface: str = "bonded", normal_guess=None) -> dict:
    """Run one case: build, gravity, surcharge, stress extraction. The base case also writes the checkpoints.

    Args:
        output_dir: Folder for the outputs.
        case: One entry of pad_cases.

    Returns:
        The dictionary from summarise_case().
    """
    full = case["thickness"] is None
    mesh = build_mesh(case)
    mesh["interface"] = interface
    mesh["normal_guess"] = normal_guess
    section = define_sections()
    init_model()
    define_materials(mesh, case)
    define_nodes(mesh)
    define_boundary_conditions(mesh)
    if full:
        vis_nodes(output_dir)
    define_elements(mesh, section, case)
    if full:
        vis_model(output_dir)
    odb = create_odb(output_dir) if full else _NoODB()
    define_gravity_loads(mesh)
    define_surcharge_loads(mesh)
    if full:
        vis_loads(output_dir)
        vis_pre_analysis(output_dir)
    results: dict = {}
    run_gravity(odb, mesh, results)
    ref = _stresses(mesh)
    u_ref = _soil_displacements(mesh)
    pad_ref = _pad_base_uy(mesh)
    steps = run_surcharge(odb, mesh, results)
    fin = _stresses(mesh)
    u_fin = _soil_displacements(mesh)
    pad_fin = _pad_base_uy(mesh)
    d_if = _soil_force_change(mesh, u_ref, u_fin)
    if full:
        odb.save_response()
        if not _headless():
            vis_defo(output_dir, filename="vis_05_defo_surcharge.html", odb_tag=ODB_TAG,
                     resp_dof="UY", scale=1.0)
    out = summarise_case(case, mesh, results, ref, fin, d_if)
    out["summary"]["interface"] = mesh.get("interface", "bonded")
    if mesh.get("pad_copy"):
        out["summary"]["pad_base_settlement_centre_mm"] = float(-(pad_fin - pad_ref))
        out["summary"].update(_interface_checks(mesh))
        out["data"]["interface_normal_N"] = _interface_normal(mesh)
    s = out["summary"]
    print(f"  {case['name']}: contact total {s['contact_total_N']:.3f} N, applied {s['surcharge_N']:.3f} N", flush=True)
    cases_dir = output_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    frames = np.stack([ref] + steps)                                 # (steps + 1, quads, 3), MPa
    dsig_frames = -(frames - ref[None]) * 1000.0                     # kPa, compression positive
    load = np.arange(n_surcharge_steps + 1) / n_surcharge_steps
    scale_err = float(np.max(np.abs(dsig_frames[:, :, 1] - load[:, None] * dsig_frames[-1, :, 1][None, :])))
    quad_xy = np.array([[mesh["nodes"][n] for n in q["nodes"]] for q in mesh["quads"]], dtype=np.float32)
    np.savez(cases_dir / f"{case['name']}_frames.npz",
             load_factor=load, dsig_yy=dsig_frames[:, :, 1].astype(np.float32), quad_xy=quad_xy,
             cx=out["data"]["cx"], cy=out["data"]["cy"], is_pad=out["data"]["is_pad"])
    print(f"  {case['name']}: {len(load)} stress frames saved; linear-scaling deviation {scale_err:.2e} kPa",
          flush=True)
    np.savez(cases_dir / f"{case['name']}_stress.npz",
             cx=out["data"]["cx"], cy=out["data"]["cy"], is_pad=out["data"]["is_pad"],
             dsig_xx=out["data"]["dsig_xx"], dsig_yy=out["data"]["dsig_yy"], dsig_xy=out["data"]["dsig_xy"])
    (cases_dir / f"{case['name']}_results.json").write_text(
        json.dumps({"gravity": results["gravity"], "surcharge_final": results["surcharge_final"],
                    "summary": out["summary"]}, indent=2), encoding="utf-8")
    print(f"case {case['name']} done", flush=True)
    return out


def _pad_base_uy(mesh: dict):
    """Vertical displacement (mm) of the pad base node under the pad centre, in the interface models; None if bonded.

    Args:
        mesh: Mesh dictionary from build_mesh(), with the pad base copies from define_nodes().

    Returns:
        Displacement in mm, or None.
    """
    if not mesh.get("pad_copy"):
        return None
    x_c = 0.5 * (pad_left + pad_right)
    centre = min(mesh["ground_tribs"], key=lambda item: abs(mesh["nodes"][item[0]][0] - x_c))[0]
    return ops.nodeDisp(mesh["pad_copy"][centre], 2)


def _interface_normal(mesh: dict) -> np.ndarray:
    """Normal force (N per 1 mm slice) in each pad interface spring after the surcharge, per pad base node."""
    return np.array([abs(ops.eleResponse(ELE_PADIF_BASE + k, "localForce")[-1])
                     for k in range(len(mesh["ground_tribs"]))])


def _interface_checks(mesh: dict) -> dict:
    """Pad interface after the surcharge. The normal forces are compared with the estimate that sets the friction
    limit. For the friction model the shear is compared with the Coulomb limit, mu times the actual normal force.

    Args:
        mesh: Mesh dictionary from build_mesh(), with the interface springs from define_elements().

    Returns:
        Dictionary of numbers for the summary file.
    """
    friction = mesh["interface"] == "friction"
    normal, shear = [], []
    for k in range(len(mesh["ground_tribs"])):
        f = ops.eleResponse(ELE_PADIF_BASE + k, "localForce")
        if friction:
            shear.append(abs(f[0]))
            normal.append(abs(f[1]))
        else:
            normal.append(abs(f[0]))
    normal = np.array(normal)
    est = np.array([(surcharge + gamma_pad * mesh["pad_thickness"]) * length * unit_length
                    for _, length in mesh["ground_tribs"]])
    out = {
        "interface_total_normal_N": float(normal.sum()),
        "interface_normal_over_estimate_min": float((normal / est).min()),
        "interface_normal_over_estimate_max": float((normal / est).max()),
    }
    if friction:
        shear = np.array(shear)
        ratio = shear / np.maximum(pad_friction_coefficient * normal, 1e-12)
        out["interface_shear_over_limit_max"] = float(ratio.max())
        out["interface_fraction_at_friction_limit"] = float((ratio >= 0.99).mean())
    return out


def make_interface_figure(output_dir: Path, rows: dict) -> None:
    """Contact stress under the pad (0.5 m bins) for the bonded, frictionless and friction interfaces; one panel per case.

    Args:
        output_dir: Folder for the figure (interface/ is created).
        rows: Dictionary of case name -> {'bonded', 'frictionless', 'friction'} summaries.
    """
    n_bins = int(math.ceil(pad_width / (0.5 * m)))
    centres = []
    for b in range(n_bins):
        lo = pad_left + b * 0.5 * m
        hi = min(lo + 0.5 * m, pad_right)
        centres.append(0.5 * (lo + hi) / m)
    labels = {"bonded": "bonded", "frictionless": "frictionless",
              "friction": f"friction, mu = {pad_friction_coefficient:g}"}
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True, sharey=True)
    for ax, (name, variants) in zip(axes.ravel(), rows.items()):
        case = next(c for c in pad_cases if c["name"] == name)
        for key in ("bonded", "frictionless", "friction"):
            ax.plot(centres, variants[key]["contact_bins_kPa"], marker="o", lw=1.6, label=labels[key])
        ax.axhline(surcharge / kPa, color="k", ls="--", lw=1.0)
        ax.set_title(_case_label(case), fontsize=9)
        ax.set_xlabel("x (m)")
        ax.set_ylabel("contact stress (kPa)")
    axes.ravel()[0].legend(fontsize=8)
    fig.suptitle("Pad contact stress from the 75 kPa surcharge: bonded, frictionless and friction interfaces")
    fig.tight_layout()
    (output_dir / "interface").mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "interface" / "pad_interface_comparison.png", dpi=110)
    plt.close(fig)


def run_interface_study(output_dir: Path) -> None:
    """Frictionless and friction pad-soil interfaces for each pad case, compared with the bonded results.

    Writes output/interface/<mode>/cases, output/interface/interface_summary.json and a comparison figure.

    Args:
        output_dir: Folder with the bonded results in cases/.
    """
    runs = {}
    for mode in ("frictionless", "friction"):
        for case in pad_cases:
            if case["thickness"] is None:
                continue
            if mode == "frictionless":
                runs[(mode, case["name"])] = run_case(output_dir / "interface" / mode, case, interface=mode)["summary"]
                continue
            guess = None
            change = float("nan")
            for _ in range(3):                       # friction limit from the normal force of the previous pass
                res = run_case(output_dir / "interface" / mode, case, interface=mode, normal_guess=guess)
                normal = res["data"]["interface_normal_N"]
                if guess is not None:
                    change = float(np.max(np.abs(normal - guess) / np.maximum(normal, 1e-9)))
                guess = normal
            res["summary"]["friction_passes"] = 3
            res["summary"]["friction_normal_change_last_pass"] = change
            runs[(mode, case["name"])] = res["summary"]
    rows = {}
    for case in pad_cases:
        if case["thickness"] is None:
            continue
        with open(output_dir / "cases" / f"{case['name']}_results.json", encoding="utf-8") as fh:
            bonded = json.load(fh)["summary"]
        rows[case["name"]] = {"bonded": bonded,
                              "frictionless": runs[("frictionless", case["name"])],
                              "friction": runs[("friction", case["name"])]}
    (output_dir / "interface").mkdir(parents=True, exist_ok=True)
    (output_dir / "interface" / "interface_summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    make_interface_figure(output_dir, rows)
    for name, variants in rows.items():
        for key in ("bonded", "frictionless", "friction"):
            s = variants[key]
            bins = s["contact_bins_kPa"]
            print(f"  {name} [{key}]: depth 1/3/5/10 m {s['dsig_yy_depth_1m_kPa']:.1f} / {s['dsig_yy_depth_3m_kPa']:.1f}"
                  f" / {s['dsig_yy_depth_5m_kPa']:.1f} / {s['dsig_yy_depth_10m_kPa']:.1f} kPa | contact edge"
                  f" {bins[0]:.1f} / middle {bins[len(bins) // 2]:.1f} / edge {bins[-1]:.1f} kPa | pad settlement"
                  f" {s.get('pad_base_settlement_centre_mm', s['settlement_pad_centre_mm']):.2f} mm", flush=True)
    print("interface study complete", flush=True)


def compare_coarse(fine_dir: Path, coarse_dir: Path) -> None:
    """Key results of the coarser pad zones against the current study: a table per case and a contact comparison.

    Args:
        fine_dir: Folder with the current pad_study_summary.json.
        coarse_dir: Folder with the coarser-zone pad_study_summary.json; the comparison is written here.
    """
    fine = json.loads((fine_dir / "pad_study_summary.json").read_text(encoding="utf-8"))
    coarse = json.loads((coarse_dir / "pad_study_summary.json").read_text(encoding="utf-8"))
    depth_keys = ("dsig_yy_depth_1m_kPa", "dsig_yy_depth_3m_kPa", "dsig_yy_depth_5m_kPa", "dsig_yy_depth_10m_kPa")
    rows = {}
    for name in fine:
        f, c = fine[name], coarse[name]
        rows[name] = {
            "soil_nodes": {"fine": f["soil_nodes"], "coarse": c["soil_nodes"]},
            "depth_kPa": {key: {"fine": f[key], "coarse": c[key]} for key in depth_keys},
            "pipe_level_kPa": {"fine": f["dsig_yy_pipe_level_kPa"], "coarse": c["dsig_yy_pipe_level_kPa"]},
            "settlement_mm": {"fine": f["settlement_pad_centre_mm"], "coarse": c["settlement_pad_centre_mm"]},
            "contact_bins_kPa": {"fine": f["contact_bins_kPa"], "coarse": c["contact_bins_kPa"]},
            "contact_total_N": {"fine": f["contact_total_N"], "coarse": c["contact_total_N"]},
        }
    (coarse_dir / "coarse_vs_fine.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    for name, r in rows.items():
        depth_change = max(abs(r["depth_kPa"][k]["coarse"] - r["depth_kPa"][k]["fine"]) / r["depth_kPa"][k]["fine"]
                           for k in depth_keys)
        bins_f, bins_c = r["contact_bins_kPa"]["fine"], r["contact_bins_kPa"]["coarse"]
        bin_change = max(abs(b - a) / a for a, b in zip(bins_f, bins_c))
        print(f"  {name}: soil nodes {r['soil_nodes']['fine']} -> {r['soil_nodes']['coarse']} | depth change up to "
              f"{100 * depth_change:.1f} % | contact bins change up to {100 * bin_change:.1f} % | pipe level "
              f"{r['pipe_level_kPa']['fine']:.2f} -> {r['pipe_level_kPa']['coarse']:.2f} kPa", flush=True)
    n_bins = int(math.ceil(pad_width / (0.5 * m)))
    centres = []
    for b in range(n_bins):
        lo = pad_left + b * 0.5 * m
        hi = min(lo + 0.5 * m, pad_right)
        centres.append(0.5 * (lo + hi) / m)
    pad_rows = {name: r for name, r in rows.items() if name != "flexible_no_pad"}
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True, sharey=True)
    for ax, (name, r) in zip(axes.ravel(), pad_rows.items()):
        case = next(c for c in pad_cases if c["name"] == name)
        ax.plot(centres, r["contact_bins_kPa"]["fine"], marker="o", lw=1.6, label="current zones")
        ax.plot(centres, r["contact_bins_kPa"]["coarse"], marker="s", lw=1.6, ls="--", label="coarser zones")
        ax.axhline(surcharge / kPa, color="k", ls=":", lw=1.0)
        ax.set_title(_case_label(case), fontsize=9)
        ax.set_xlabel("x (m)")
        ax.set_ylabel("contact stress (kPa)")
    axes.ravel()[0].legend(fontsize=8)
    fig.suptitle("Pad contact stress: current and coarser zones (0.5 m bins)")
    fig.tight_layout()
    fig.savefig(coarse_dir / "coarse_vs_fine_contact.png", dpi=110)
    plt.close(fig)


def make_study_figures(output_dir: Path, runs: list) -> None:
    """Stress maps (kPa), depth profiles under the pad centre and contact pressure under the pad.

    Args:
        output_dir: Folder for the PNG files.
        runs: List of dictionaries from run_case(), each with 'summary' and 'data'.
    """
    vmax = 100.0                                 # kPa; colour cap (cells at the pad corners saturate above it)

    fig, axes = plt.subplots(2, 3, figsize=(16, 9.5), sharex=True, sharey=True)
    axes = axes.ravel()
    last = None
    for ax, run in zip(axes, runs):
        d, s = run["data"], run["summary"]
        pc = PolyCollection(d["win_polys"], array=d["win_vals"], cmap="inferno", edgecolors="face", linewidths=0.15)
        pc.set_clim(0.0, vmax)
        ax.add_collection(pc)
        last = pc
        if s["pad_thickness_m"] is None:
            ax.plot([pad_left / m, pad_right / m], [y_ground / m, y_ground / m], color="cyan", lw=3)
            label = "no pad (surcharge on the ground)"
        else:
            ax.add_patch(Rectangle((pad_left / m, y_ground / m), pad_width / m, s["pad_thickness_m"],
                                   fill=False, edgecolor="cyan", lw=1.5))
            label = f"pad {s['pad_thickness_m']:.1f} m, E {s['pad_modulus_GPa']:.0f} GPa"
        ax.add_patch(Circle((pipe_centre_x / m, pipe_centre_y / m), pipe_radius_out / m,
                            fill=False, edgecolor="white", lw=0.8))
        ax.set_xlim(0.0, 36.0)
        ax.set_ylim(-15.0, 12.5)
        ax.set_aspect("equal")
        ax.set_title(f"{label}\nK = {s['relative_stiffness_K']:.2f}", fontsize=10)
    for ax in axes[len(runs):]:
        ax.axis("off")
    for ax in axes[::3]:
        ax.set_ylabel("y (m)")
    for ax in axes[3:]:
        ax.set_xlabel("x (m)")
    fig.colorbar(last, ax=axes.tolist(), label="vertical soil stress increase (kPa)", shrink=0.8)
    fig.suptitle("Soil stress increase from the 75 kPa surcharge: pad thickness and stiffness (colour scale capped at 100 kPa)",
                 fontsize=12)
    fig.savefig(output_dir / "pad_stress_maps_kPa.png", dpi=110)
    plt.close(fig)

    fig2, ax2 = plt.subplots(figsize=(7.5, 8.5))
    for run in runs:
        d, s = run["data"], run["summary"]
        ax2.plot(d["depth_kPa"], d["depth_m"], lw=1.8, label=f"{s['name']} (K = {s['relative_stiffness_K']:.2f})")
    depth = np.linspace(0.05, 12.0, 240)
    half = 0.5 * pad_width / m
    theta = np.arctan(half / depth)
    reference = surcharge / kPa / math.pi * (2.0 * theta + np.sin(2.0 * theta))
    ax2.plot(reference, depth, "k--", lw=1.2, label="closed form, flexible strip (2D half-space)")
    ax2.invert_yaxis()
    ax2.set_xlabel("vertical stress increase (kPa)")
    ax2.set_ylabel("depth below ground (m), band under the pad centre")
    ax2.set_xlim(0.0, vmax)
    ax2.set_ylim(12.0, 0.0)
    ax2.legend(fontsize=8)
    ax2.set_title("How the surcharge spreads with depth")
    fig2.tight_layout()
    fig2.savefig(output_dir / "pad_stress_depth_profile_kPa.png", dpi=110)
    plt.close(fig2)

    fig3, ax3 = plt.subplots(figsize=(9, 5))
    for run in runs:
        d, s = run["data"], run["summary"]
        ax3.plot(d["contact_bin_x_m"], d["contact_bin_kPa"], marker="o", lw=1.8, label=s["name"])
    ax3.axhline(surcharge / kPa, color="k", ls="--", lw=1.0, label="75 kPa applied")
    ax3.set_xlim(pad_left / m - 0.5, pad_right / m + 0.5)
    ax3.set_xlabel("x (m)")
    ax3.set_ylabel("contact stress under the pad (kPa)")
    ax3.legend(fontsize=8)
    ax3.set_title("Contact stress under the pad, 0.5 m bin averages (bins sum to the applied load)")
    fig3.tight_layout()
    fig3.savefig(output_dir / "pad_contact_pressure_kPa.png", dpi=110)
    plt.close(fig3)


def _case_label(case: dict) -> str:
    """Short label for a case: the pad size and modulus with its relative stiffness K, or the no-pad case."""
    if case["thickness"] is None:
        return "no pad (surcharge on the ground)"
    k_rel = case["e_pad"] * case["thickness"] ** 3 / (12.0 * (1.0 - nu_pad ** 2)) / (e_soil * pad_width ** 3)
    return f"pad {case['thickness'] / m:.1f} m, E {case['e_pad'] / GPa:.0f} GPa, K = {k_rel:.2f}"


def _draw_stress_panel(ax, panel: dict) -> PolyCollection:
    """Soil stress map (first frame) with the pad outline and the pipe. Returns the PolyCollection to update."""
    pc = PolyCollection(panel["polys"], array=panel["frames"][0], cmap="inferno", edgecolors="face", linewidths=0.15)
    pc.set_clim(0.0, 100.0)
    ax.add_collection(pc)
    case = panel["case"]
    if case["thickness"] is None:
        ax.plot([pad_left / m, pad_right / m], [y_ground / m, y_ground / m], color="cyan", lw=3)
    else:
        ax.add_patch(Rectangle((pad_left / m, y_ground / m), pad_width / m, case["thickness"] / m,
                               fill=False, edgecolor="cyan", lw=1.5))
    ax.add_patch(Circle((pipe_centre_x / m, pipe_centre_y / m), pipe_radius_out / m,
                        fill=False, edgecolor="white", lw=0.8))
    ax.set_xlim(0.0, 36.0)
    ax.set_ylim(-15.0, 12.5)
    ax.set_aspect("equal")
    ax.set_title(panel["label"], fontsize=9)
    return pc


def _animate_one(panel: dict, path: Path) -> None:
    """GIF for one case: the applied surcharge bar above the soil stress map, both updated at each load step.

    Args:
        panel: Dictionary with 'case', 'label', 'polys', 'frames' (kPa per frame) and 'load_kpa' (per frame).
        path: Output GIF file.
    """
    from matplotlib.animation import FuncAnimation, PillowWriter

    fig = plt.figure(figsize=(7.0, 6.6), dpi=80)
    grid = fig.add_gridspec(2, 1, height_ratios=[1, 5], hspace=0.5)
    bar_ax = fig.add_subplot(grid[0])
    ax = fig.add_subplot(grid[1])
    load = panel["load_kpa"]
    bar = bar_ax.barh([0], [load[0]], color="tab:blue", height=0.6)[0]
    bar_ax.set_xlim(0.0, float(load[-1]))
    bar_ax.set_ylim(-0.5, 0.5)
    bar_ax.set_yticks([])
    bar_ax.set_xlabel("surcharge applied (kPa)")
    pc = _draw_stress_panel(ax, panel)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    fig.colorbar(pc, ax=ax, label="vertical soil stress increase (kPa)", shrink=0.9)
    title = fig.suptitle("")
    n_last = len(load) - 1

    def update(k: int) -> list:
        pc.set_array(panel["frames"][k])
        bar.set_width(float(load[k]))
        title.set_text(f"{panel['label']}: load {load[k]:.1f} kPa (step {k} of {n_last})")
        return []

    anim = FuncAnimation(fig, update, frames=len(load), interval=250, blit=False)
    anim.save(path, writer=PillowWriter(fps=4))
    plt.close(fig)


def _animate_all(panels: list, path: Path) -> None:
    """GIF with all cases side by side, each updated at the same load step.

    Args:
        panels: Panel dictionaries from make_stress_animations().
        path: Output GIF file.
    """
    from matplotlib.animation import FuncAnimation, PillowWriter

    fig, axes = plt.subplots(2, 3, figsize=(15.0, 9.8), dpi=70, sharex=True, sharey=True)
    axes = axes.ravel()
    pcs = [_draw_stress_panel(ax, panel) for ax, panel in zip(axes, panels)]
    for ax in axes[len(panels):]:
        ax.axis("off")
    for ax in axes[::3]:
        ax.set_ylabel("y (m)")
    for ax in axes[3:]:
        ax.set_xlabel("x (m)")
    fig.colorbar(pcs[0], ax=axes.tolist(), label="vertical soil stress increase (kPa)", shrink=0.8)
    load = panels[0]["load_kpa"]
    n_last = len(load) - 1
    title = fig.suptitle("")

    def update(k: int) -> list:
        for pc, panel in zip(pcs, panels):
            pc.set_array(panel["frames"][k])
        title.set_text(f"Surcharge applied: {load[k]:.1f} kPa (step {k} of {n_last})")
        return []

    anim = FuncAnimation(fig, update, frames=len(load), interval=250, blit=False)
    anim.save(path, writer=PillowWriter(fps=4))
    plt.close(fig)


def make_stress_animations(output_dir: Path, case_names: list) -> None:
    """Soil stress increase (kPa) while the surcharge is applied: one GIF per case, and one GIF with all cases side
    by side. Each frame is one load step. The model is linear elastic and the ramp is linear, so each frame is the
    final stress scaled by the load factor: the animation shows the stress building up, not a change of shape.

    Args:
        output_dir: Folder holding cases/{name}_frames.npz from run_case().
        case_names: Case names, in pad_cases order.
    """
    anim_dir = output_dir / "animations"
    anim_dir.mkdir(parents=True, exist_ok=True)
    panels = []
    for name in case_names:
        case = next(c for c in pad_cases if c["name"] == name)
        with np.load(output_dir / "cases" / f"{name}_frames.npz") as z:
            cx, cy, is_pad = z["cx"], z["cy"], z["is_pad"]
            window = (~is_pad) & (cx >= 0.0) & (cx <= 36000.0) & (cy >= -15000.0) & (cy <= 12500.0)
            panels.append({
                "case": case,
                "label": _case_label(case),
                "polys": z["quad_xy"][window] / m,
                "frames": z["dsig_yy"][:, window],
                "load_kpa": z["load_factor"] * surcharge / kPa,
            })
    for panel in panels:
        _animate_one(panel, anim_dir / f"stress_{panel['case']['name']}.gif")
        print(f"  animation written: stress_{panel['case']['name']}.gif", flush=True)
    _animate_all(panels, anim_dir / "stress_all_cases.gif")
    print("  animation written: stress_all_cases.gif", flush=True)


def create_plane_odb(output_dir: Path):
    """Response database with plane-element stresses written at every load step, for the opstool stress sliders.

    Nodal projection is off, so the stresses are stored per element. That halves the write time per step.

    Args:
        output_dir: Folder for the database files.

    Returns:
        The CreateODB instance.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=ODB_TAG, save_plane_resp=True, project_gauss_to_nodes=False)
    odb.save_model_data()
    return odb


def run_stress_odb(output_dir: Path, case: dict) -> Path:
    """Full model (self-weight, then the surcharge) with the plane stresses written at every step.

    The gravity state is the first stored step, so the slider can show each step minus the gravity state, which is
    the surcharge increment.

    Args:
        output_dir: Folder with the outputs; the database goes in animations/odb/<case name>.
        case: One entry of pad_cases.

    Returns:
        Folder holding the database.
    """
    odb_dir = output_dir / "animations" / "odb" / case["name"]
    mesh = build_mesh(case)
    section = define_sections()
    init_model()
    define_materials(mesh, case)
    define_nodes(mesh)
    define_boundary_conditions(mesh)
    define_elements(mesh, section, case)
    define_gravity_loads(mesh)
    define_surcharge_loads(mesh)
    odb = create_plane_odb(odb_dir)
    results: dict = {}
    run_gravity(odb, mesh, results)
    run_surcharge(odb, mesh, results, per_step_odb=True)
    odb.save_response()
    print(f"  {case['name']}: stress database written to {odb_dir}", flush=True)
    return odb_dir


def make_stress_sliders(output_dir: Path, case_names: list) -> None:
    """Interactive stress slider per case, built with opstool: the soil stress increase (kPa) at each load step.

    The figure is opstool's animation of the stored plane stresses: the mesh is stored once and each frame carries only
    its colours, which keeps the HTML small. The colours are the surcharge increments behind the static maps (the saved
    element stresses), so the slider and the maps agree. The page has Play, Pause and a slider.

    Args:
        output_dir: Folder with animations/odb/<case> from run_stress_odb().
        case_names: Case names, in pad_cases order.
    """
    import plotly.graph_objects as go

    slider_dir = output_dir / "animations" / "opstool"
    slider_dir.mkdir(parents=True, exist_ok=True)
    for name in case_names:
        case = next(c for c in pad_cases if c["name"] == name)
        opst.post.set_odb_path(str(output_dir / "animations" / "odb" / name))
        fig = opst.vis.plotly.plot_unstruct_responses_animation(
            odb_tag=ODB_TAG, ele_type="Plane", resp_type="Stresses", resp_dof="sigma22",
            show_defo=False, show_model=False, unit_factor=-1000.0, unit_symbol="kPa")
        mesh_idx = next(i for i, tr in enumerate(fig.frames[0].data) if type(tr).__name__ == "Mesh3d")
        # Keep only the filled mesh. opstool's element edges, vertex markers and support symbols cover the colours.
        fig.data = tuple(tr for tr in fig.data if type(tr).__name__ == "Mesh3d")
        base_idx = next(i for i, tr in enumerate(fig.data) if type(tr).__name__ == "Mesh3d")
        # Element values: the saved stresses behind the static maps, placed on opstool's elements by centroid. opstool's
        # own values are Gauss-point means, which differ from these at re-entrant corners, so the slider uses the maps'.
        geo = fig.frames[0].data[mesh_idx]
        xs = np.asarray(geo.x, dtype=float).reshape(-1, 4)
        ys = np.asarray(geo.y, dtype=float).reshape(-1, 4)
        cen_plot = np.column_stack([xs.mean(axis=1), ys.mean(axis=1)])
        with np.load(output_dir / "cases" / f"{name}_frames.npz") as z:
            cen_saved = np.column_stack([z["cx"], z["cy"]])
            saved = z["dsig_yy"].astype(float)          # saved[0] = gravity state; saved[k] = after load step k
        match = np.empty(len(cen_plot), dtype=int)
        for s in range(0, len(cen_plot), 300):
            d2 = ((cen_plot[s:s + 300, None, :] - cen_saved[None, :, :]) ** 2).sum(axis=2)
            match[s:s + 300] = d2.argmin(axis=1)
        n_steps = len(saved) - 1
        increments = [np.repeat(saved[k][match] - saved[0][match], 4) for k in range(len(saved))]
        loads = [surcharge / kPa * k / n_steps for k in range(len(saved))]
        frames = [go.Frame(data=[go.Mesh3d(intensity=inc)], traces=[base_idx], name=f"s{k:02d}")
                  for k, inc in enumerate(increments)]
        mesh_trace = fig.data[base_idx]
        mesh_trace.intensity = increments[-1]          # shown at the final load until the slider is moved
        mesh_trace.update(cmin=0.0, cmax=100.0, lighting=dict(ambient=1.0, diffuse=0.0, specular=0.0, fresnel=0.0),
                          colorbar=dict(title=dict(text="vertical soil stress increase (kPa)")))
        fig.frames = frames
        fig.update_layout(
            title=dict(text=f"Soil stress increase from the 75 kPa surcharge: {_case_label(case)}"),
            coloraxis=dict(cmin=0.0, cmax=100.0, colorbar=dict(title=dict(text="vertical soil stress increase (kPa)"))),
            scene=dict(
                xaxis=dict(title="x (mm)", range=[0.0, 36000.0]),
                yaxis=dict(title="y (mm)", range=[-15000.0, 12500.0]),
                zaxis=dict(visible=False),
                aspectmode="manual", aspectratio=dict(x=1.0, y=0.76, z=0.01),
                camera=dict(eye=dict(x=0.0, y=0.0, z=1.3), up=dict(x=0.0, y=1.0, z=0.0),
                            projection=dict(type="orthographic"))),
            updatemenus=[dict(
                type="buttons", showactive=False, x=0.0, y=0.0, xanchor="left", yanchor="top", pad=dict(t=0, r=10),
                buttons=[
                    dict(label="Play", method="animate",
                         args=[None, dict(frame=dict(duration=250, redraw=True), fromcurrent=True,
                                          transition=dict(duration=0))]),
                    dict(label="Pause", method="animate",
                         args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate",
                                            transition=dict(duration=0))]),
                ])],
            sliders=[dict(
                active=len(frames) - 1, x=0.12, y=0.0, len=0.85, pad=dict(t=30),
                currentvalue=dict(prefix="Surcharge applied: ", suffix=" kPa", visible=True),
                steps=[dict(method="animate", label=f"{load:.2f}",
                            args=[[fr.name], dict(mode="immediate", frame=dict(duration=0, redraw=True),
                                                  transition=dict(duration=0))])
                       for load, fr in zip(loads, frames)])])
        html = slider_dir / f"stress_slider_{name}.html"
        fig.write_html(str(html), include_plotlyjs=True, full_html=True)
        fig.write_image(str(slider_dir / f"stress_slider_{name}_final.png"), width=900, height=640)
        print(f"  {name}: slider written, {len(frames)} frames, "
              f"{html.stat().st_size / 1e6:.1f} MB", flush=True)


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    if "--coarse" in sys.argv:
        # Coarser zones around the pad: the coarse pad target of the Impact from Pipe 300 Coarse Mesh model (1000 mm),
        # a 2000 mm wider zone and pad elements of thickness / 2. The pipe, cut and far-field sizes are unchanged.
        h_pad_max = 1000.0 * mm
        h_mid = 2000.0 * mm
        pad_size_divisor = 2
        coarse_dir = output_dir / "coarse_zone"
        coarse_dir.mkdir(parents=True, exist_ok=True)
        runs = [run_case(coarse_dir, case) for case in pad_cases]
        summary = {r["summary"]["name"]: r["summary"] for r in runs}
        (coarse_dir / "pad_study_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        compare_coarse(output_dir, coarse_dir)
        print("coarse zone study complete", flush=True)
        raise SystemExit(0)
    if "--interface" in sys.argv:
        run_interface_study(output_dir)
        raise SystemExit(0)
    if "--sliders-only" in sys.argv:
        make_stress_sliders(output_dir, [case["name"] for case in pad_cases])
        raise SystemExit(0)
    if "--sliders" in sys.argv:
        for case in pad_cases:
            run_stress_odb(output_dir, case)
        make_stress_sliders(output_dir, [case["name"] for case in pad_cases])
        raise SystemExit(0)
    if "--animations-only" in sys.argv:
        make_stress_animations(output_dir, [case["name"] for case in pad_cases])
        print("animations complete", flush=True)
        raise SystemExit(0)
    runs = [run_case(output_dir, case) for case in pad_cases]
    summary = {r["summary"]["name"]: r["summary"] for r in runs}
    (output_dir / "pad_study_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    make_study_figures(output_dir, runs)
    make_stress_animations(output_dir, [case["name"] for case in pad_cases])
    print("study complete", flush=True)
