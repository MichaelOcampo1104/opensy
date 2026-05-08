from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Iterable, Optional
import opstool as opst
import os
import builtins

import openseespy.opensees as ops
import numpy as np
import matplotlib.pyplot as plt
    
# Storage for created nodes and elements
created_nodes = []
created_elements = []
block_registry = {}

###########################################################
#                                                         #
# CREATING THE CORNER NODES WITH 3 DOF                    #
#                                                         #
###########################################################
def create_corner_nodes_3dof(start_x, start_y, length, height, num_x, num_y, node_offset=1):
    dx = length / num_x
    dy = height / num_y

    corner_nodes = {}
    nid = node_offset

    for j in range(num_y + 1):
        for i in range(num_x + 1):
            x = start_x + i * dx
            y = start_y + j * dy
            ops.node(nid, x, y)
            created_nodes.append((nid, x, y, 3))
            corner_nodes[(i, j)] = nid
            nid += 1

    return corner_nodes, nid
# CREATING THE CORNER NODES WITH 3 DOF


###########################################################
#                                                         #
# CREATING THE MID AND CENTRE NODE WITH 2 DOF             #
#                                                         #
###########################################################
def create_mid_and_center_nodes_2dof(start_x, start_y, length, height,
                                     num_x, num_y, corner_nodes, node_offset):
    dx = length / num_x
    dy = height / num_y

    mid_center_nodes = {}
    element_nodes = {}   # <-- full 9-node connectivity for each element
    nid = node_offset

    horizontal_mids = {}
    vertical_mids   = {}

    for j in range(num_y):
        for i in range(num_x):
            n1 = corner_nodes[(i, j)]
            n2 = corner_nodes[(i+1, j)]
            n3 = corner_nodes[(i+1, j+1)]
            n4 = corner_nodes[(i, j+1)]

            x1, y1, _ = created_nodes[n1-1][1:]
            x2, y2, _ = created_nodes[n2-1][1:]
            x3, y3, _ = created_nodes[n3-1][1:]
            x4, y4, _ = created_nodes[n4-1][1:]

            elem_nodes = {}

            key = (i, j, "H")
            if key not in horizontal_mids:
                x, y = (x1+x2)/2, (y1+y2)/2
                ops.node(nid, x, y)
                created_nodes.append((nid, x, y, 2))
                horizontal_mids[key] = nid
                nid += 1
            elem_nodes["n5"] = horizontal_mids[key]

            key = (i+1, j, "V")
            if key not in vertical_mids:
                x, y = (x2+x3)/2, (y2+y3)/2
                ops.node(nid, x, y)
                created_nodes.append((nid, x, y, 2))
                vertical_mids[key] = nid
                nid += 1
            elem_nodes["n6"] = vertical_mids[key]

            key = (i, j+1, "H")
            if key not in horizontal_mids:
                x, y = (x3+x4)/2, (y3+y4)/2
                ops.node(nid, x, y)
                created_nodes.append((nid, x, y, 2))
                horizontal_mids[key] = nid
                nid += 1
            elem_nodes["n7"] = horizontal_mids[key]

            key = (i, j, "V")
            if key not in vertical_mids:
                x, y = (x4+x1)/2, (y4+y1)/2
                ops.node(nid, x, y)
                created_nodes.append((nid, x, y, 2))
                vertical_mids[key] = nid
                nid += 1
            elem_nodes["n8"] = vertical_mids[key]

            x, y = (x1+x2+x3+x4)/4, (y1+y2+y3+y4)/4
            ops.node(nid, x, y)
            created_nodes.append((nid, x, y, 2))
            elem_nodes["n9"] = nid
            nid += 1

            mid_center_nodes[(i,j)] = elem_nodes

            # full connectivity list for this element
            element_nodes[(i,j)] = [
                n1, n2, n3, n4,
                elem_nodes["n5"], elem_nodes["n6"],
                elem_nodes["n7"], elem_nodes["n8"],
                elem_nodes["n9"]
            ]

    return mid_center_nodes, element_nodes, nid
# CREATING THE MID AND CENTRE NODE WITH 2 DOF


###########################################################
#                                                         #
# CREATING THE 4_9 QUAD UP ELEMENT                        #
#                                                         #
###########################################################
def create_quadUP_elements(
    element_nodes, elem_offset,
    thickness, mat_tag, bulk, fmass, hPerm, vPerm,
    b1=0.0, b2=0.0
):
    """
    Create 9_4_QuadUP elements using pre-built element_nodes.
    Tracks both element IDs and element groups (by row, col, full mesh).
    """
    elements = {}       # (i,j) -> eid
    groups = {          # track sets of elements
        "all": [],
        "rows": {},     # row j -> [eids]
        "cols": {},     # col i -> [eids]
    }

    eid = elem_offset

    for (i, j), nodes in element_nodes.items():
        # create element in OpenSees
        ops.element(
            "9_4_QuadUP", eid,
            *nodes,
            thickness, mat_tag, bulk, fmass, hPerm, vPerm, b1, b2
        )

        # store mapping
        elements[(i, j)] = eid
        groups["all"].append(eid)

        # track row group
        if j not in groups["rows"]:
            groups["rows"][j] = []
        groups["rows"][j].append(eid)

        # track col group
        if i not in groups["cols"]:
            groups["cols"][i] = []
        groups["cols"][i].append(eid)

        eid += 1

    return elements, groups, eid
# CREATING THE 4_9 QUAD UP ELEMENT


###########################################################
#                                                         #
# CREATING THE 4_9 QUAD UP ELEMENT WITH THE LIST OF NODES #
#                                                         #
###########################################################
def create_quadUP_from_list(
    nodes_list, elem_offset,
    thickness, mat_tag, bulk, fmass, hPerm, vPerm,
    b1=0.0, b2=0.0
):
    """
    Create 9_4_QuadUP elements directly from a list of node IDs.

    Parameters
    ----------
    nodes_list : list[list[int]]
        List of node connectivity (each element must have 9 nodes).
    elem_offset : int
        Starting element ID.
    thickness, mat_tag, bulk, fmass, hPerm, vPerm : float
        Element properties.
    b1, b2 : float
        Optional body forces.

    Returns
    -------
    elements : dict
        Mapping element index -> element ID
    next_eid : int
        Next available element ID
    """
    elements = {}
    eid = elem_offset

    for idx, nodes in enumerate(nodes_list):
        if len(nodes) != 9:
            raise ValueError(f"Element {idx} must have 9 nodes, got {len(nodes)}")

        ops.element(
            "9_4_QuadUP", eid,
            *nodes,
            thickness, mat_tag, bulk, fmass, hPerm, vPerm, b1, b2
        )

        elements[idx] = eid
        eid += 1

    return elements, eid
# CREATING THE 4_9 QUAD UP ELEMENT WITH THE LIST OF NODES


###########################################################
#                                                         #
# CREATING THE 4_9 QUAD UP ELEMENT WITH PAIRS OF NODES    #
#                                                         #
###########################################################
def create_row_quadUP(
    bot_corner_node,
    top_corner_node,
    mid_bot_node,
    mid_top_node,
    mid_mid_node,
    center_node, 
    elem_offset,
    thickness,
    mat_tag,
    bulk,
    fmass,
    hPerm,
    vPerm,
    b1=0.0,
    b2=0.0,
):
    """
    Create a horizontal row of 9_4_QuadUP elements using provided node IDs.

    Node order matches OpenSees 9_4_QuadUP convention:
    n1--n5--n2
    |   |   |
    n8--n9--n6
    |   |   |
    n4--n7--n3

    Where: n5=bottom mid, n6=right mid, n7=top mid, n8=left mid.

    Parameters
    ----------
    bot_corner_node : list[int]   # length = num_elem+1
    top_corner_node : list[int]   # length = num_elem+1
    mid_bot_node    : list[int]   # length = num_elem
    mid_top_node    : list[int]   # length = num_elem
    mid_mid_node    : list[int]   # length = num_elem+1 (vertical mids along the row)
    center_node     : list[int]   # length = num_elem

    Returns
    -------
    elements : list[int]
    next_eid : int
    connectivities : list[tuple[int, list[int]]]
        Per-element node list in creation order (for verification/reporting).

    Notes
    -----
    - Validates lengths to avoid mis-alignment.
    - Uses counter-clockwise corner ordering.
    - Swaps n6/n7 compared to previous draft so n6 is the RIGHT mid and n7 is the TOP mid.
    """
    num_elem = len(center_node)
    assert len(bot_corner_node) == num_elem + 1, "bot_corner_node length must be num_elem+1"
    assert len(top_corner_node) == num_elem + 1, "top_corner_node length must be num_elem+1"
    assert len(mid_bot_node) == num_elem, "mid_bot_node length must be num_elem"
    assert len(mid_top_node) == num_elem, "mid_top_node length must be num_elem"
    assert len(mid_mid_node) == num_elem + 1, "mid_mid_node length must be num_elem+1"

    elements = []
    conns = []
    eid = elem_offset

    for i in range(num_elem):
        # corners (counter-clockwise)
        n1 = bot_corner_node[i]
        n2 = bot_corner_node[i + 1]
        n3 = top_corner_node[i + 1]
        n4 = top_corner_node[i]

        # mids + center (per OpenSees numbering)
        n5 = mid_bot_node[i]      # bottom edge mid
        n6 = mid_mid_node[i + 1]  # RIGHT edge vertical mid  (fix)
        n7 = mid_top_node[i]      # TOP edge mid             (fix)
        n8 = mid_mid_node[i]      # LEFT edge vertical mid
        n9 = center_node[i]       # center

        # create element
        ops.element(
            "9_4_QuadUP",
            eid,
            n1, n2, n3, n4,
            n5, n6, n7, n8, n9,
            thickness, mat_tag, bulk, fmass, hPerm, vPerm, b1, b2,
        )
        elements.append(eid)
        conns.append((eid, [n1, n2, n3, n4, n5, n6, n7, n8, n9]))
        eid += 1

    return elements, eid, conns
# CREATING THE 4_9 QUAD UP ELEMENT WITH PAIRS OF NODES



###########################################################
#                                                         #
# FIXING NODES BY RANGE                                   #
#                                                         #
###########################################################


def add_nodes_from_coordinates(coord_list: list[tuple[float, ...]], start_id: int, block_name: str):
    """
    Add 2D or 3D nodes to the OpenSees model from coordinate tuples.

    Args:
        coord_list (list[tuple[float, ...]]): List of (x, y) or (x, y, z) coordinates.
        start_id (int): Starting node ID.
        block_name (str): Block name for registry tracking.

    Returns:
        list[int]: List of created node IDs.
    """
    if not coord_list:
        raise ValueError("coord_list cannot be empty")

    # Detect dimensionality from the first coordinate
    dim = len(coord_list[0])
    if dim not in (2, 3):
        raise ValueError("Each coordinate must be (x, y) for 2D or (x, y, z) for 3D")

    node_ids = []

    for i, coord in enumerate(coord_list):
        nid = start_id + i
        if len(coord) != dim:
            raise ValueError("All coordinates must have the same dimension (2D or 3D)")

        # Create node based on dimensionality
        if dim == 2:
            x, y = coord
            ops.node(nid, x, y)
            created_nodes.append((nid, x, y))
        else:
            x, y, z = coord
            ops.node(nid, x, y, z)
            created_nodes.append((nid, x, y, z))

        node_ids.append(nid)

    # Record in block registry
    block_registry[block_name] = {
        "nodes": node_ids,
        "elements": []
    }

    return node_ids


###########################################################
#                                                         #
# FIXING NODES BY RANGE                                   #
#                                                         #
###########################################################

  
def fix_nodes_by_range(start_id, end_id, step, fixity, block_name="fixed_nodes"):
    node_ids = list(range(start_id, end_id + 1, step))
    for nid in node_ids:
        ops.fix(nid, *fixity)
    block_registry[block_name] = {
        "nodes": node_ids,
        "elements": []
    }
    return node_ids

###########################################################
#                                                         #
# FIXING NODES BY LIST                                    #
#                                                         #
###########################################################

def fix_nodes_by_list(node_ids, fixity, block_name="fixed_nodes"):
    for nid in node_ids:
        ops.fix(nid, *fixity)

    block_registry[block_name] = {
        "nodes": node_ids,
        "elements": []
    }

    return node_ids

###########################################################
#                                                         #
# APPLYING EQUAL DOF FROM PAIRS FOR CONSTRAINTS AND SLAVE #
# NODES                                                   #
#                                                         #
###########################################################
  
def apply_equal_dof_by_range(
    primary_start, primary_end, primary_step,
    secondary_start, secondary_end, secondary_step,
    dofs=[1, 2, 3], block_name="equal_dof_constraints"):

    primary_nodes = list(range(primary_start, primary_end + 1, primary_step))
    secondary_nodes = list(range(secondary_start, secondary_end + 1, secondary_step))

    constraint_pairs = []
    for r, c in zip(primary_nodes, secondary_nodes):
        ops.equalDOF(r, c, *dofs)
        constraint_pairs.append((r, c))

    block_registry[block_name] = {
        "nodes": primary_nodes + secondary_nodes,
        "constraints": constraint_pairs
    }

    return constraint_pairs

###########################################################
#                                                         #
# APPLYING EQUAL DOF FROM PAIRS FOR CONSTRAINTS AND SLAVE #
# NODES                                                   #
#                                                         #
###########################################################

def apply_equal_dof_pairs(r_nodes, c_nodes, dofs=[1, 2, 3], block_name="equal_dof_pairs"):
    assert len(r_nodes) == len(c_nodes), "Node lists must be the same length."

    constraint_pairs = []
    for r, c in zip(r_nodes, c_nodes):
        ops.equalDOF(r, c, *dofs)
        constraint_pairs.append((r, c))

    block_registry[block_name] = {
        "nodes": r_nodes + c_nodes,
        "constraints": constraint_pairs
    }

    return constraint_pairs

###########################################################
#                                                         #
# GETTING THE NEXT NODE ID                                #
#                                                         #
###########################################################

def get_next_node_id(start_from=None):
    existing_tags = ops.getNodeTags()
    next_id = max(existing_tags) + 1 if existing_tags else 1
    return max(next_id, start_from) if start_from is not None else next_id

###########################################################
#                                                         #
# GETTING THE NEXT ELEMENT ID                             #
#                                                         #
###########################################################


def get_next_elem_id(start_from=None):
    existing_tags = ops.getEleTags()
    next_id = max(existing_tags) + 1 if existing_tags else 1
    return max(next_id, start_from) if start_from is not None else next_id


###########################################################
#                                                         #
# CREATE A SET OF LAGRANGE NODES                          #
#                                                         #
###########################################################


def create_lagrange_nodes(start_id, x_coord, y_coord, count, block_name="lagrange_nodes"):
    lagrange_node_ids = []
    for i in range(count):
        nid = start_id + i
        ops.node(nid, x_coord, y_coord)
        created_nodes.append((nid, x_coord, y_coord))
        lagrange_node_ids.append(nid)

    block_registry[block_name] = {
        "nodes": lagrange_node_ids,
        "elements": []
    }

    return lagrange_node_ids

###########################################################
#                                                         #
# CREATE DISMPLACEMENT BEAM COLUMN CHAINS                 #
#                                                         #
###########################################################

def create_disp_beam_column_chain(beam_nodes, beam_start_id,
                                   transFTag, intTag,
                                   block_name="beam_chain"):

    beam_elem_ids = []
    for i in range(len(beam_nodes) - 1):
        sN = beam_nodes[i]
        eN = beam_nodes[i + 1]
        eid = beam_start_id + i
        ops.element("dispBeamColumn", eid, sN, eN, transFTag, intTag)
        created_elements.append((eid, sN, eN))
        beam_elem_ids.append(eid)

    block_registry[block_name] = {
        "nodes": beam_nodes,
        "elements": beam_elem_ids
    }

    return beam_elem_ids

###########################################################
#                                                         #
# CREATE DISMPLACEMENT BEAM COLUMN CHAINS                 #
#                                                         #
###########################################################

def create_force_beam_column_chain(beam_nodes, beam_start_id,
                                   transFTag, intTag,
                                   block_name="beam_chain"):

    beam_elem_ids = []
    for i in range(len(beam_nodes) - 1):
        sN = beam_nodes[i]
        eN = beam_nodes[i + 1]
        eid = beam_start_id + i
        ops.element("forceBeamColumn", eid, sN, eN, transFTag, intTag)
        created_elements.append((eid, sN, eN))
        beam_elem_ids.append(eid)

    block_registry[block_name] = {
        "nodes": beam_nodes,
        "elements": beam_elem_ids
    }

    return beam_elem_ids


###########################################################
#                                                         #
# CREATE ELASTIC BEAM COLUMN CHAINS 2D                    #
#                                                         #
###########################################################

def create_elastic_beam_column_chain2d(
    beam_nodes: list[int],
    beam_start_id: int,
    A: float,
    E: float,
    Iz: float,
    transf_tag: int,
    mass: float | None = None,
    cMass: bool = False,
    release: str | None = None,
    block_name: str = "elastic_beam_chain"
) -> list[int]:
    """
    Create a chain of elasticBeamColumn elements between consecutive beam nodes.

    Args:
        beam_nodes (list[int]): Ordered list of beam node IDs.
        beam_start_id (int): Starting element tag.
        A (float): Cross-sectional area.
        E (float): Elastic modulus.
        Iz (float): Moment of inertia.
        transf_tag (int): Geometric transformation tag.
        mass (float, optional): Element mass per unit length (for '-mass').
        cMass (bool, optional): Use consistent mass formulation (adds '-cMass' flag).
        release (str, optional): Release code string for '-release'.
        block_name (str, optional): Name for block registry.

    Returns:
        list[int]: List of created element IDs.
    """
    if len(beam_nodes) < 2:
        raise ValueError("At least two nodes are required to create a beam chain.")

    elem_ids = []

    for i in range(len(beam_nodes) - 1):
        iNode = beam_nodes[i]
        jNode = beam_nodes[i + 1]
        eid = beam_start_id + i

        cmd = [
            "elasticBeamColumn",
            eid,
            iNode,
            jNode,
            A,
            E,
            Iz,
            transf_tag
        ]

        # Optional flags
        if mass is not None:
            cmd += ["-mass", mass]

        if cMass:
            cmd.append("-cMass")

        if release is not None:
            cmd += ["-release", release]

        # Create element
        ops.element(*cmd)
        created_elements.append((eid, iNode, jNode))
        elem_ids.append(eid)

    # Record in block registry
    block_registry[block_name] = {
        "nodes": beam_nodes,
        "elements": elem_ids
    }

    return elem_ids

###########################################################
#                                                         #
# CREATE ELASTIC BEAM COLUMN CHAINS 3D                    #
#                                                         #
###########################################################

def create_elastic_beam_column_chain_3d(
    beam_nodes: list[int],
    beam_start_id: int,
    A: float,
    E: float,
    G: float,
    Jx: float,
    Iy: float,
    Iz: float,
    transf_tag: int,
    mass: float | None = None,
    cMass: bool = False,
    block_name: str = "elastic_beam_chain_3d"
) -> list[int]:
    """
    Create a chain of 3D elasticBeamColumn elements between consecutive beam nodes.

    Args:
        beam_nodes (list[int]): Ordered list of beam node IDs.
        beam_start_id (int): Starting element tag.
        A (float): Cross-sectional area.
        E (float): Elastic modulus.
        G (float): Shear modulus.
        Jx (float): Torsional constant.
        Iy (float): Moment of inertia about the local y-axis.
        Iz (float): Moment of inertia about the local z-axis.
        transf_tag (int): Geometric transformation tag.
        mass (float, optional): Mass per unit length (adds '-mass' flag).
        cMass (bool, optional): Use consistent mass matrix (adds '-cMass' flag).
        block_name (str): Name for tracking in the registry.

    Returns:
        list[int]: List of created element IDs.
    """
    if len(beam_nodes) < 2:
        raise ValueError("At least two nodes are required to create a beam chain.")

    elem_ids = []

    for i in range(len(beam_nodes) - 1):
        iNode = beam_nodes[i]
        jNode = beam_nodes[i + 1]
        eid = beam_start_id + i

        cmd = [
            "elasticBeamColumn",
            eid,
            iNode,
            jNode,
            A,
            E,
            G,
            Jx,
            Iy,
            Iz,
            transf_tag
        ]

        if mass is not None:
            cmd += ["-mass", mass]

        if cMass:
            cmd.append("-cMass")

        ops.element(*cmd)
        created_elements.append((eid, iNode, jNode))
        elem_ids.append(eid)

    # Record created elements and nodes for reference
    block_registry[block_name] = {
        "nodes": beam_nodes,
        "elements": elem_ids
    }

    return elem_ids


###########################################################
#                                                         #
# CREATE BEAM CONTACT 2D CHAINS                           #
#                                                         #
###########################################################


def create_beam_contact_chain(master_nodes, slave_nodes, lagrange_nodes,
                               contact_mat, beam_start_id,
                               width=0.5, tol1=1e-10, tol2=1e-10,
                               block_name="contact_beams"):

    contact_elem_ids = []
    for i in range(len(slave_nodes)):
        tag = beam_start_id + i
        iN = master_nodes[i]
        jN = master_nodes[i + 1]
        sN = slave_nodes[i]
        IN = lagrange_nodes[i]

        ops.element("BeamContact2D", tag, iN, jN, sN, IN, contact_mat, width, tol1, tol2)
        created_elements.append((tag, iN, jN, sN, IN))
        contact_elem_ids.append(tag)

    block_registry[block_name] = {
        "nodes": master_nodes + slave_nodes + lagrange_nodes,
        "elements": contact_elem_ids
    }

    return contact_elem_ids

###########################################################
#                                                         #
# CREATE ZERO LENGTH ELEMENTS FROM NODE PAIRS             #
#                                                         #
###########################################################

def create_zero_length_chain(
    i_nodes: list[int],
    j_nodes: list[int],
    mat_tag: int,
    dirs: list[int],
    start_id: int,
    rFlag: int | None = None,
    orient_x: tuple[float, float, float] | None = None,
    orient_yp: tuple[float, float, float] | None = None,
    block_name: str = "zero_length_chain"
) -> list[int]:
    """
    Create a chain of zeroLength elements start nodes and end nodes.

    Args:
        i_nodes (list[int]): start node IDs.
        j_nodes (list[int]): end node IDs.
        mat_tag (int): Material tag to assign.
        dirs (list[int]): Direction(s) for the zeroLength element.
        start_id (int): Starting element ID.
        rFlag (int, optional): Rayleigh damping flag (0 or 1).
        orient_x (tuple[float, float, float], optional): x-axis orientation vector.
        orient_yp (tuple[float, float, float], optional): yp-axis orientation vector.
        block_name (str): Optional name for block registry.

    Returns:
        list[int]: Created element IDs.
    """
    if len(i_nodes) != len(j_nodes):
        raise ValueError("i_nodes and j_nodes must have the same length")

    elem_ids = []

    for i in range(len(i_nodes)):
        tag = start_id + i
        iNode = i_nodes[i]
        jNode = j_nodes[i]

        # Build element command
        cmd = [
            "zeroLength",
            tag,
            iNode,
            jNode,
            "-mat", mat_tag,
            "-dir", *dirs
        ]

        if rFlag is not None:
            cmd += ["-doRayleigh", rFlag]

        if orient_x is not None and orient_yp is not None:
            cmd += ["-orient", *orient_x, *orient_yp]

        # Create element in OpenSees
        ops.element(*cmd)
        elem_ids.append(tag)

    # Optional registry (for tracking groups)
    block_registry[block_name] = {
        "nodes": i_nodes + j_nodes,
        "elements": elem_ids
    }

    return elem_ids


###########################################################
#                                                         #
# CREATE ZERO LENGTH CONTACT CHAINS                       #
#                                                         #
########################################################### 

def create_zero_length_contact2d_chain(master_node: list[int], slave_node: list[int],
                                       Kn:float, Kt:float, fs: float,
                                       start_id: int,
                                       normal: tuple[float, float, float],
                                       block_name: str = "zero_length_contacts") -> list[int]:
    """
    Create a chain of ZeroLengthContact2D elements from pairs of nodes.
    """
    if len(master_node) != len(slave_node):
        raise ValueError("node_list_1 and node_list_2 must have the same length")

    contact_elem_ids = []
    Nx, Ny, Nz = normal

    for i, (n1, n2) in enumerate(zip(master_node, slave_node)):
        tag = start_id + i
        ops.element("zeroLengthContactASDimplex", tag, n1, n2, Kn, Kt, fs, '-orient', Nx, Ny, Nz) #zeroLengthContact2D #SimpleContact2D #zeroLengthContactASDimplex
        contact_elem_ids.append(tag)

    block_registry[block_name] = {
        "nodes": master_node + slave_node,
        "elements": contact_elem_ids
    }

    return contact_elem_ids


###########################################################
#                                                         #
# CREATE ZERO LENGTH INTERFACE CONTACT CHAINS             #
#                                                         #
########################################################### 


def create_zero_length_interface2d(
    tag: int,
    slave_nodes: list[int],
    master_nodes: list[int],
    Kn: float,
    Kt: float,
    phi: float,
    sdof: int,
    mdof: int
) -> int:
    """
    Create a zeroLengthInterface2D element in OpenSees.

    Args:
        tag (int): Element tag.
        slave_nodes (list[int]): IDs of slave (constrained) nodes.
        master_nodes (list[int]): IDs of master (retained) nodes.
        Kn (float): Normal stiffness.
        Kt (float): Tangential stiffness.
        phi (float): Friction angle (degrees).
        sdof (int): DOF for constrained node.
        mdof (int): DOF for retained node.

    Returns:
        int: Created element tag.
    """
    sNdNum = len(slave_nodes)
    mNdNum = len(master_nodes)

    ops.element(
        "zeroLengthInterface2D",
        tag,
        "-sNdNum", sNdNum,
        "-mNdNum", mNdNum,
        "-dof", sdof, mdof,
        "-Nodes", *slave_nodes, *master_nodes,
        Kn, Kt, phi
    )
    return tag


###########################################################
#                                                         #
# CREATE W STEEL SECTION                                  #
#                                                         #
###########################################################

def W_section(section, sec_tag, mat_tag, nf_dw, nf_tw, nf_bf, nf_tf):
    """
    Creates a W-Section based on nominal dimensions and generates
    fibers over it.
    """
    d, bf = section['d'], section['bf']
    tf, tw = section['tf'], section['tw']

    dw = d - 2 * tf
    y1, y2, y3, y4 = -d / 2, -dw / 2, dw / 2, d / 2
    z1, z2, z3, z4 = -bf / 2, -tw / 2, tw / 2, bf / 2

    ops.section('Fiber', sec_tag)
    ops.patch('quad', mat_tag, nf_bf, nf_tf, y1, z4, y1, z1, y2, z1, y2, z4)  # Top flange
    ops.patch('quad', mat_tag, nf_tw, nf_dw, y2, z3, y2, z2, y3, z2, y3, z3)  # Web
    ops.patch('quad', mat_tag, nf_bf, nf_tf, y3, z4, y3, z1, y4, z1, y4, z4)  # Bottom flange

    return [['section', 'Fiber', sec_tag],
            ['patch', 'quad', mat_tag, nf_bf, nf_tf, y1, z4, y1, z1, y2, z1, y2, z4],
            ['patch', 'quad', mat_tag, nf_tw, nf_dw, y2, z3, y2, z2, y3, z2, y3, z3],
            ['patch', 'quad', mat_tag, nf_bf, nf_tf, y3, z4, y3, z1, y4, z1, y4, z4]]


###########################################################
#                                                         #
# PREPARE OUTPUT DIRECTORY                                #
#                                                         #
###########################################################

def prepare_output_directories(
    output_dir_name: str,
    analysis_name: str,
    data_dir: str = "Data",
    base_output_root: str = "outputs",
    verbose: bool = True
) -> str:
    """
    Prepare directory structure for analysis outputs and recorder data.

    Args:
        output_dir_name (str): Name of the output folder (e.g. 'r_nine_one_seven').
        analysis_name (str): Name of the analysis case (e.g. 'examp').
        data_dir (str, optional): Folder for storing input or raw data. Defaults to 'Data'.
        base_output_root (str, optional): Root folder for all output results. Defaults to 'outputs'.
        verbose (bool, optional): Print the generated path if True.

    Returns:
        str: Full base path for recorder/output files (e.g., 'outputs/r_nine_one_seven/examp').
    """
    # Ensure data directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Prepare main output directory
    base_dir = os.path.join(base_output_root, output_dir_name)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Build full output file base path
    base_name = os.path.join(base_dir, analysis_name)

    if verbose:
        print(f"📁 Recorder output path prepared: {base_name}")

    return base_name

###########################################################
#                                                         #
# FACTORED STRENGTH PARAMETERS                            #
#                                                         #
###########################################################


def factored_strength_params(c, phi, fs):
    """Return factored strength parameters, c and phi"""
    c = c / fs
    phi = np.degrees(np.arctan(np.tan(np.radians(phi)) / fs))

    return c, phi


###########################################################
#                                                         #
# CONVERSION OF MOHR-COULOMB TO DRUCKER-PRAGER            #
#                                                         #
###########################################################

def mc2dp(cohesion, friction_angle):
    """Convert Mohr-Coulomb cohesion, friction angle to Drucker-Prager sigma_y and rho"""

    # convert Mohr-Coulomb phi and c to Drucker-Prager
    sigma_y = (6 * cohesion * np.cos(np.radians(friction_angle))) / (
        np.sqrt(3) * (3 - np.sin(np.radians(friction_angle)))
    )

    rho = (2 * np.sqrt(2) * np.sin(np.radians(friction_angle))) / (
        np.sqrt(3) * (3 - np.sin(np.radians(friction_angle)))
    )

    return sigma_y, rho



##########################################################
#                                                         #
# Procedure to compute ultimate lateral resistance, p_u,  #
#  and displacement at 50% of lateral capacity, y50, for  #
#  p-y springs representing cohesionless soil.            #
#   Converted to openseespy by: Pavan Chigullapally       #
#                               University of Auckland    # 
#                                                         #
#   Created by:   Hyung-suk Shin                          #
#                 University of Washington                #
#   Modified by:  Chris McGann                            #
#                 Pedro Arduino                           #
#                 Peter Mackenzie-Helnwein                #
#                 University of Washington                #
#                                                         #
###########################################################

# references
#  American Petroleum Institute (API) (1987). Recommended Practice for Planning, Designing and
#   Constructing Fixed Offshore Platforms. API Recommended Practice 2A(RP-2A), Washington D.C,
#   17th edition.
#
# Brinch Hansen, J. (1961). "The ultimate resistance of rigid piles against transversal forces."
#  Bulletin No. 12, Geoteknisk Institute, Copenhagen, 59.
#
#  Boulanger, R. W., Kutter, B. L., Brandenberg, S. J., Singh, P., and Chang, D. (2003). Pile 
#   Foundations in liquefied and laterally spreading ground during earthquakes: Centrifuge experiments
#   and analyses. Center for Geotechnical Modeling, University of California at Davis, Davis, CA.
#   Rep. UCD/CGM-03/01.
#
#  Reese, L.C. and Van Impe, W.F. (2001), Single Piles and Pile Groups Under Lateral Loading.
#    A.A. Balkema, Rotterdam, Netherlands.

import math

def get_pyParam ( pyDepth, gamma, phiDegree, b, pEleLength, puSwitch, kSwitch, gwtSwitch):
    
    #----------------------------------------------------------
    #  define ultimate lateral resistance, pult 
    #----------------------------------------------------------
    
    # pult is defined per API recommendations (Reese and Van Impe, 2001 or API, 1987) for puSwitch = 1
    #  OR per the method of Brinch Hansen (1961) for puSwitch = 2
    
    pi = 3.14159265358979
    phi = phiDegree * (pi/180)
    zbRatio = pyDepth / b
    
    #-------API recommended method-------
    
    if puSwitch == 1:
    
      # obtain loading-type coefficient A for given depth-to-diameter ratio zb
      #  ---> values are obtained from a figure and are therefore approximate
        zb = []
        dataNum = 41
        for i in range(dataNum):
            b1 = i * 0.125
            zb.append(b1)
        As = [2.8460, 2.7105, 2.6242, 2.5257, 2.4271, 2.3409, 2.2546, 2.1437, 2.0575, 1.9589, 1.8973, 1.8111, 1.7372, 1.6632, 1.5893, 1.5277, 1.4415, 1.3799, 1.3368, 1.2690, 1.2074, 1.1581, 
            1.1211, 1.0780, 1.0349, 1.0164, 0.9979, 0.9733, 0.9610, 0.9487, 0.9363, 0.9117, 0.8994, 0.8994, 0.8871, 0.8871, 0.8809, 0.8809, 0.8809, 0.8809, 0.8809] 
      
      # linear interpolation to define A for intermediate values of depth:diameter ratio
        for i in range(dataNum):
            if zbRatio >= 5.0:
                A = 0.88
            elif zb[i] <= zbRatio and zbRatio <= zb[i+1]:
                A = (As[i+1] - As[i])/(zb[i+1] - zb[i]) * (zbRatio-zb[i]) + As[i]
                
      # define common terms
        alpha = phi / 2
        beta = pi / 4 + phi / 2
        K0 = 0.4
        
        tan_1 = math.tan(pi / 4 - phi / 2)        
        Ka = math.pow(tan_1 , 2) 
    
      # terms for Equation (3.44), Reese and Van Impe (2001)
        tan_2 = math.tan(phi)
        tan_3 = math.tan(beta - phi)
        sin_1 = math.sin(beta)
        cos_1 = math.cos(alpha)
        c1 = K0 * tan_2 * sin_1 / (tan_3*cos_1)
        
        tan_4 = math.tan(beta)
        tan_5 = math.tan(alpha)
        c2 = (tan_4/tan_3)*tan_4 * tan_5
        
        c3 = K0 * tan_4 * (tan_2 * sin_1 - tan_5)
        
        c4 = tan_4 / tan_3 - Ka
    
        # terms for Equation (3.45), Reese and Van Impe (2001)
        pow_1 = math.pow(tan_4,8)
        pow_2 = math.pow(tan_4,4)
        c5 = Ka * (pow_1-1)
        c6 = K0 * tan_2 * pow_2
    
      # Equation (3.44), Reese and Van Impe (2001)
        pst = gamma * pyDepth * (pyDepth * (c1 + c2 + c3) + b * c4)
    
      # Equation (3.45), Reese and Van Impe (2001)
        psd = b * gamma * pyDepth * (c5 + c6)
    
      # pult is the lesser of pst and psd. At surface, an arbitrary value is defined
        if pst <=psd:
            if pyDepth == 0:
                pu = 0.01
              
            else:
                pu = A * pst
              
        else:
            pu = A * psd
          
      # PySimple1 material formulated with pult as a force, not force/length, multiply by trib. length
        pult = pu * pEleLength
    
    #-------Brinch Hansen method-------
    elif puSwitch == 2:
      # pressure at ground surface
        cos_2 = math.cos(phi)
        
        tan_6 = math.tan(pi/4+phi/2) 
        
        sin_2 = math.sin(phi)
        sin_3 = math.sin(pi/4 + phi/2)
        
        exp_1 = math.exp((pi/2+phi)*tan_2)
        exp_2 = math.exp(-(pi/2-phi) * tan_2)
        
        Kqo = exp_1 * cos_2 * tan_6 - exp_2 * cos_2 * tan_1
        Kco = (1/tan_2) * (exp_1 * cos_2 * tan_6 - 1)
    
      # pressure at great depth
        exp_3 = math.exp(pi * tan_2)
        pow_3 = math.pow(tan_2,4)
        pow_4 = math.pow(tan_6,2)
        dcinf = 1.58 + 4.09 * (pow_3)
        Nc = (1/tan_2)*(exp_3)*(pow_4 - 1)
        Ko = 1 - sin_2
        Kcinf = Nc * dcinf
        Kqinf = Kcinf * Ko * tan_2
    
      # pressure at an arbitrary depth
        aq = (Kqo/(Kqinf - Kqo))*(Ko*sin_2/sin_3)
        KqD = (Kqo + Kqinf * aq * zbRatio)/(1 + aq * zbRatio)
    
      # ultimate lateral resistance
        if pyDepth == 0:
            pu = 0.01
        else:
            pu = gamma * pyDepth * KqD * b
               
      # PySimple1 material formulated with pult as a force, not force/length, multiply by trib. length
        pult  = pu * pEleLength
        
    #----------------------------------------------------------
    #  define displacement at 50% lateral capacity, y50
    #----------------------------------------------------------
    
    # values of y50 depend of the coefficent of subgrade reaction, k, which can be defined in several ways.
    #  for gwtSwitch = 1, k reflects soil above the groundwater table
    #  for gwtSwitch = 2, k reflects soil below the groundwater table
    #  a linear variation of k with depth is defined for kSwitch = 1 after API (1987)
    #  a parabolic variation of k with depth is defined for kSwitch = 2 after Boulanger et al. (2003)
    
    # API (1987) recommended subgrade modulus for given friction angle, values obtained from figure (approximate)
    
    ph = [28.8, 29.5, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0]    
   
    # subgrade modulus above the water table
    if gwtSwitch == 1:
        k = [10, 23, 45, 61, 80, 100, 120, 140, 160, 182, 215, 250, 275]
        
    else:
        k = [10, 20, 33, 42, 50, 60, 70, 85, 95, 107, 122, 141, 155]
    
    dataNum = 13  
    for i in range(dataNum):
        if ph[i] <= phiDegree and phiDegree <= ph[i+1]:
            khat = (k[i+1]-k[i])/(ph[i+1]-ph[i])*(phiDegree - ph[i]) + k[i]            
            
    # change units from (lb/in^3) to (kN/m^3)
    k_SIunits = khat * 271.45
    
    # define parabolic distribution of k with depth if desired (i.e. lin_par switch == 2)
    sigV = pyDepth * gamma
    
    if sigV == 0:
         sigV = 0.01
         
    if kSwitch == 2:
       # Equation (5-16), Boulanger et al. (2003)
        cSigma = math.pow(50 / sigV , 0.5)
       # Equation (5-15), Boulanger et al. (2003)
        k_SIunits = cSigma * k_SIunits
    
    # define y50 based on pult and subgrade modulus k
    
    # based on API (1987) recommendations, p-y curves are described using tanh functions.
    #  tcl does not have the atanh function, so must define this specifically
    
    #  i.e.  atanh(x) = 1/2*ln((1+x)/(1-x)), |x| < 1
    
    # when half of full resistance has been mobilized, p(y50)/pult = 0.5
    x = 0.5
    log_1 = math.log((1+x)/(1-x))
    atanh_value = 0.5 * log_1
    
    # need to be careful at ground surface (don't want to divide by zero)
    if pyDepth == 0.0:
        pyDepth = 0.01

    y50 = 0.5 * (pu/ A)/(k_SIunits * pyDepth) * atanh_value
    # return pult and y50 parameters
    outResult = []
    outResult.append(pult)
    outResult.append(y50)
    
    return outResult

#########################################################################################################################################################################

#########################################################################################################################################################################

###########################################################
#                                                         #
# Procedure to compute ultimate tip resistance, qult, and #
#  displacement at 50% mobilization of qult, z50, for     #
#  use in q-z curves for cohesionless soil.               #
#   Converted to openseespy by: Pavan Chigullapally       #  
#                               University of Auckland    #
#   Created by:  Chris McGann                             #
#                Pedro Arduino                            #
#                University of Washington                 #
#                                                         #
###########################################################

    # references
    #  Meyerhof G.G. (1976). "Bearing capacity and settlement of pile foundations." 
    #   J. Geotech. Eng. Div., ASCE, 102(3), 195-228.
    #
    #  Vijayvergiya, V.N. (1977). "Load-movement characteristics of piles."
    #   Proc., Ports 77 Conf., ASCE, New York.
    #
    #  Kulhawy, F.H. ad Mayne, P.W. (1990). Manual on Estimating Soil Properties for 
    #   Foundation Design. Electrical Power Research Institute. EPRI EL-6800, 
    #   Project 1493-6 Final Report.

def get_qzParam (phiDegree, b, sigV, G):
    
    # define required constants; pi, atmospheric pressure (kPa), pa, and coeff. of lat earth pressure, Ko
    pi = 3.14159265358979
    pa = 101
    sin_4 = math.sin(phiDegree * (pi/180))
    Ko = 1 - sin_4

  # ultimate tip pressure can be computed by qult = Nq*sigV after Meyerhof (1976)
  #  where Nq is a bearing capacity factor, phi is friction angle, and sigV is eff. overburden
  #  stress at the pile tip.
    phi = phiDegree * (pi/180)

  # rigidity index
    tan_7 = math.tan(phi)
    Ir = G/(sigV * tan_7)
  # bearing capacity factor
    tan_8 = math.tan(pi/4+phi/2)
    sin_5 = math.sin(phi)
    pow_4 = math.pow(tan_8,2)
    pow_5 = math.pow(Ir,(4*sin_5)/(3*(1+sin_5)))
    exp_4 = math.exp(pi/2-phi)
    
    Nq = (1+2*Ko)*(1/(3-sin_5))*exp_4*(pow_4)*(pow_5)  
  # tip resistance
    qu = Nq * sigV
  # QzSimple1 material formulated with qult as force, not stress, multiply by area of pile tip
    pow_6 = math.pow(b, 2)  
    qult = qu * pi*pow_6/4

  # the q-z curve of Vijayvergiya (1977) has the form, q(z) = qult*(z/zc)^(1/3)
  #  where zc is critical tip deflection given as ranging from 3-9% of the
  #  pile diameter at the tip.  

  # assume zc is 5% of pile diameter
    zc = 0.05 * b

  # based on Vijayvergiya (1977) curve, z50 = 0.125*zc
    z50 = 0.125 * zc

  # return values of qult and z50 for use in q-z material
    outResult = []
    outResult.append(qult)
    outResult.append(z50)
    
    return outResult

#########################################################################################################################################################################

#########################################################################################################################################################################
##########################################################
#                                                         #
# Procedure to compute ultimate resistance, tult, and     #
#  displacement at 50% mobilization of tult, z50, for     #
#  use in t-z curves for cohesionless soil.               #
#   Converted to openseespy by: Pavan Chigullapally       #
#                               University of Auckland    #
#   Created by:  Chris McGann                             #
#                University of Washington                 #
#                                                         #
###########################################################

def get_tzParam ( phi, b, sigV, pEleLength):

    # references
    #  Mosher, R.L. (1984). "Load transfer criteria for numerical analysis of
    #   axial loaded piles in sand." U.S. Army Engineering and Waterways
    #   Experimental Station, Automatic Data Processing Center, Vicksburg, Miss.
    #
    #  Kulhawy, F.H. (1991). "Drilled shaft foundations." Foundation engineering
    #   handbook, 2nd Ed., Chap 14, H.-Y. Fang ed., Van Nostrand Reinhold, New York

    pi = 3.14159265358979
    
  # Compute tult based on tult = Ko*sigV*pi*dia*tan(delta), where
  #   Ko    is coeff. of lateral earth pressure at rest, 
  #         taken as Ko = 0.4
  #   delta is interface friction between soil and pile,
  #         taken as delta = 0.8*phi to be representative of a 
  #         smooth precast concrete pile after Kulhawy (1991)
  
    delta = 0.8 * phi * pi/180

  # if z = 0 (ground surface) need to specify a small non-zero value of sigV
  
    if sigV == 0.0:
        sigV = 0.01
    
    tan_9 = math.tan(delta)
    tu = 0.4 * sigV * pi * b * tan_9
    
  # TzSimple1 material formulated with tult as force, not stress, multiply by tributary length of pile
    tult = tu * pEleLength

  # Mosher (1984) provides recommended initial tangents based on friction angle
	# values are in units of psf/in
    kf = [6000, 10000, 10000, 14000, 14000, 18000]
    fric = [28, 31, 32, 34, 35, 38]

    dataNum = len(fric)
    
    
	# determine kf for input value of phi, linear interpolation for intermediate values
    if phi < fric[0]:
        k = kf[0]
    elif phi > fric[5]:
        k = kf[5]
    else:
        for i in range(dataNum):
            if fric[i] <= phi and phi <= fric[i+1]:
                k = ((kf[i+1] - kf[i])/(fric[i+1] - fric[i])) * (phi - fric[i]) + kf[i]
        

  # need to convert kf to units of kN/m^3
    kSIunits =  k * 1.885

  # based on a t-z curve of the shape recommended by Mosher (1984), z50 = tult/kf
    z50 = tult / kSIunits

  # return values of tult and z50 for use in t-z material
    outResult = []
    outResult.append(tult)
    outResult.append(z50)

    return outResult



###########################################################
#                                                         #
# CALCULATE ALPHA FOR SSPQUADUP ELEMENT                   #
#                                                         #
###########################################################


def compute_alpha(h: float, density: float, youngs_modulus: float) -> float:
    """
    Compute stabilization parameter alpha for SSPquadUP element.

    Parameters
    ----------
    h : float
        Characteristic element size (m).
    density : float
        Mass density of solid phase (kg/m^3). For soils, use saturated density.
    youngs_modulus : float
        Young's modulus of the solid skeleton (Pa).
    poisson : float
        Poisson's ratio of the solid skeleton (dimensionless).

    Returns
    -------
    alpha : float
        Stabilization parameter for SSPquadUP.

    Example :
    h = 1.0          # m
    rho = 2000.0     # kg/m^3
    E = 30e6         # Pa
    nu = 0.3         # -

    alpha = compute_alpha(h, rho, E, nu)
    print("alpha =", alpha)
    """
    poisson = 0.3
    # shear modulus
    G = youngs_modulus / (2.0 * (1.0 + poisson))
    # bulk modulus
    K = youngs_modulus / (3.0 * (1.0 - 2.0 * poisson))

    # P-wave speed in solid skeleton
    c = np.sqrt((K + 4.0/3.0 * G) / density)

    # alpha parameter
    alpha = 0.25 * (h ** 2) / (density * c ** 2)

    return alpha



###########################################################
#                                                         #
# penseespy_dc_qsa_framework                              #
#                                                         #
###########################################################

# -----------------------------------------------------------------------------
# Analysis components
# -----------------------------------------------------------------------------


def setup_variable_transient_analysis(
    tol=1e-9,
    max_iter=30,
    print_flag=1,
    line_search_eta=0.8,
    gamma=0.5,
    beta=0.25
):
    """
    Helper to configure VariableTransient analysis in OpenSeesPy.

    Parameters
    ----------
    tol : float
        Convergence tolerance for test (default=1e-6).
    max_iter : int
        Maximum number of iterations per step (default=30).
    print_flag : int
        Print flag for test (0=no print, 1=print on failure).
    line_search_eta : float
        NewtonLineSearch eta parameter (default=0.8).
    gamma : float
        Newmark gamma (default=0.5).
    beta : float
        Newmark beta (default=0.25).
    """

    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", tol, max_iter, print_flag)
    ops.algorithm("NewtonLineSearch", line_search_eta)
    #ops.integrator("Newmark", gamma, beta)
    ops.integrator('TRBDF2 ')
    ops.analysis("VariableTransient") #VariableTransient #Transient

# analysis_setup.py

def setup_analysis(
    analysis_type: str = "Static",
    constraints_type: str = "Transformation",
    numberer_type: str = "RCM",
    system_type: str = "UmfPack",
    algorithm_type: str | None = "Newton",
    test_type: str | None = None,
    test_tolerance: float = 1e-6,
    test_iterations: int = 10,
    test_flag: int = 0,
    integrator_type: str | None = "LoadControl",
    dt: float | None = None,
    gamma: float = 0.5,
    beta: float = 0.25,
    analyze_steps: int | None = None,
    disp_ctrl_args: tuple | None = None,
    run_analysis: bool = True,
    out: bool = True
):
    """
    Configure and optionally run an OpenSees analysis with flexible control
    for both static and dynamic problems.

    Parameters
    ----------
    analysis_type : str, default="Static"
        "Static" or "Transient" (dynamic).
    constraints_type : str, default="Transformation"
        Constraint handler.
    numberer_type : str, default="RCM"
        Numbering scheme.
    system_type : str, default="UmfPack"
        Linear equation solver.
    algorithm_type : str or None, default="Newton"
        Nonlinear solution algorithm. If None, user must define outside.
    test_type : str or None, optional
        Convergence test type (e.g. "NormDispIncr").
    test_tolerance : float, default=1e-6
        Convergence test tolerance.
    test_iterations : int, default=10
        Max iterations for test.
    test_flag : int, default=0
        Print flag for test (0 = silent, 2 = verbose).
    integrator_type : str or None, default="LoadControl"
        Integration method (e.g. "LoadControl", "DisplacementControl", "Newmark", "HHT").
    dt : float or None, optional
        Step size or time increment for load/time control.
    gamma, beta : float, optional
        Newmark parameters (used if integrator_type="Newmark").
    analyze_steps : int or None, optional
        Number of steps to analyze. If None, analysis is only set up.
    disp_ctrl_args : tuple or None, optional
        Arguments for "DisplacementControl" integrator:
        (nodeTag, dof, incr, numIter, minIncr, maxIncr)
    run_analysis : bool, default=True
        Whether to run the analysis immediately after setup.
    out : bool, default=True
        Print setup summary.
    """

    # --- Base configuration ---
    ops.constraints(constraints_type)
    ops.numberer(numberer_type)
    ops.system(system_type)

    # --- Optional algorithm setup ---
    if algorithm_type is not None:
        ops.algorithm(algorithm_type)

    # --- Optional convergence test setup ---
    if test_type is not None:
        ops.test(test_type, test_tolerance, test_iterations, test_flag)

    # --- Integrator setup ---
    if integrator_type is not None:
        int_type = integrator_type.lower()

        if int_type == "loadcontrol":
            ops.integrator("LoadControl", dt if dt is not None else 1.0)

        elif int_type == "displacementcontrol":
            if disp_ctrl_args is not None:
                ops.integrator("DisplacementControl", *disp_ctrl_args)
            else:
                ops.integrator("DisplacementControl", 1, 1, dt if dt is not None else 1.0)

        elif int_type == "newmark":
            ops.integrator("Newmark", gamma, beta)

        elif int_type == "hht":
            ops.integrator("HHT", gamma)  # reuse gamma as α

        else:
            if dt is not None:
                ops.integrator(integrator_type, dt)
            else:
                ops.integrator(integrator_type)

    # --- Analysis type setup ---
    if analysis_type.lower() == "static":
        ops.analysis("Static")
    elif analysis_type.lower() in ("transient", "dynamic"):
        ops.analysis("Transient")
    else:
        raise ValueError(f"Unknown analysis_type: {analysis_type}")

    # --- Optionally run analysis ---
    if run_analysis and analyze_steps is not None:
        if analysis_type.lower() == "transient" and dt is not None:
            ops.analyze(int(analyze_steps), dt)
        else:
            ops.analyze(int(analyze_steps))

    # --- Optional summary ---
    if out:
        print(f"""
        🔧 OpenSees Analysis Setup
        --------------------------
        Analysis Type : {analysis_type}
        Constraints   : {constraints_type}
        Numberer      : {numberer_type}
        System        : {system_type}
        Algorithm     : {algorithm_type or 'External'}
        Test          : {test_type or 'External/None'}
        Integrator    : {integrator_type or 'External'}
        Steps         : {analyze_steps if analyze_steps is not None else 'N/A'}
        dt            : {dt if dt is not None else 'N/A'}
        γ, β          : ({gamma}, {beta})
        DisplCtrlArgs : {disp_ctrl_args if disp_ctrl_args else 'N/A'}
        """)

    return True


def setup_smart_analysis(
    analysis_type: str = "Static",
    test_type: str = "NormDispIncr",
    test_tol: float = 1.0e-10,
    test_iter: int = 30,
    test_print: int = 0,
    norm_tol: float = 1000,
    relax: float = 0.5,
    min_step: float = 1.0e-6,
    algo_types: list[int] | None = None,
    debug: bool = False,
    print_per: int = 20,
    show_status: bool = True,
    **kwargs
):
    """
    Wrapper for opst.anlys.SmartAnalyze with informative print output.

    Args:
        analysis_type (str): "Static" or "Transient".
        test_type (str): Convergence test type.
        test_tol (float): Convergence tolerance.
        test_iter (int): Max iterations.
        test_print (int): Print flag for test.
        norm_tol (float): Norm tolerance for smart relaxation.
        relax (float): Relaxation factor.
        min_step (float): Minimum step size.
        algo_types (list[int] | None): Algorithm fallback sequence.
        debug (bool): Enable debug output from SmartAnalyze.
        print_per (int): Print frequency for progress.
        show_status (bool): Print configuration summary.
        **kwargs: Additional SmartAnalyze keyword args.

    Returns:
        opst.anlys.SmartAnalyze: Configured SmartAnalyze object.
    """

    # Normalize case
    analysis_type = analysis_type.capitalize()

    # Default algorithm types (fallback sequence)
    if algo_types is None:
        algo_types = [40, 10, 20, 30, 31, 50, 60, 70, 90]

    # Initialize SmartAnalyze
    analysis = opst.anlys.SmartAnalyze(
        analysis_type,
        testType=test_type,
        testTol=test_tol,
        testIterTimes=test_iter,
        testPrintFlag=test_print,
        tryAddTestTimes=True,
        normTol=norm_tol,
        testIterTimesMore=[50],
        tryLooseTestTol=True,
        looseTestTolTo=1e-3,
        tryAlterAlgoTypes=True,
        algoTypes=algo_types,
        UserAlgoArgs=None,
        initialStep=None,
        relaxation=relax,
        minStep=min_step,
        debugMode=debug,
        printPer=print_per,
        **kwargs
    )

    # Optional print summary
    if show_status:
        print(f"""
        ⚙️ SmartAnalyze Setup Summary
        -------------------------------------
        Analysis Type   : {analysis_type}
        Test Type       : {test_type}
        Test Tolerance  : {test_tol}
        Max Iterations  : {test_iter}
        Test Print Flag : {test_print}
        Norm Tolerance  : {norm_tol}
        Relaxation      : {relax}
        Min Step        : {min_step}
        Print Frequency : {print_per}
        Algo Fallbacks  : {algo_types}
        Debug Mode      : {debug}
        Extra Args      : {kwargs if kwargs else 'None'}
        -------------------------------------
        ✅ SmartAnalyze instance created successfully.
        """)

    return analysis



@dataclass
class DcqsaResult:
    """Container for DC-QSA results."""
    def __init__(self, step: int, time: float, hist: Dict[str, List[float]]):
        self.step = step
        self.time = time
        self.hist = hist

    def __repr__(self) -> str:
        return f"DcqsaResult(step={self.step}, time={self.time:.3f}s, steps_logged={len(self.hist['time'])})"


def dc_qsa_alt(
    *,
    monitor_nodes: Iterable[int],
    dt0: float,
    disp_tol: float,           # m
    pwp_tol: float,            # kPa
    stg_time: float,           # s
    monitor_pwp: bool = True,
    dt_min: float = 0.01,
    dt_max: float = 3600.0,
    growth: float = 1.5,
    max_steps: int = 5000,
    min_stage_frac_before_pwp: float = 0.10,
    verbose: bool = True,
    analysis: Optional[object] = None,   # SmartAnalyze
    ODB: Optional[object] = None,        # optional odb
    p_source: str = "vel",               # "vel" or "disp"
) -> DcqsaResult:

    nds = list(monitor_nodes)
    if not nds:
        raise ValueError("monitor_nodes is empty.")

    missing_nodes_warned = set()

    # --- pore pressure reader (maps to flowchart: "Read node disp (DOF 1-2) & pressure (DOF 3)")
    def _get_p(nd: int) -> float:
        if not monitor_pwp:
            return 0.0
        try:
            if p_source.lower().startswith("v"):
                return float(ops.nodeVel(nd, 3))   # kPa in your setup
            else:
                return float(ops.nodeDisp(nd, 3))  # pore pressure DOF
        except Exception:
            return 0.0

    def _read_nodes(node_tags: List[int]) -> Tuple[List[float], List[float], List[float]]:
        ux, uy, p = [], [], []
        for nd in node_tags:
            try:
                ux.append(float(ops.nodeDisp(nd, 1)))
                uy.append(float(ops.nodeDisp(nd, 2)))
                p.append(_get_p(nd))
            except Exception:
                if nd not in missing_nodes_warned:
                    if verbose:
                        print(f"[dc_qsa] warning: node {nd} not readable (removed?). Using zeros.")
                    missing_nodes_warned.add(nd)
                ux.append(0.0); uy.append(0.0); p.append(0.0)
        return ux, uy, p

    # --- Initialize analysis (flowchart: "Initialize analysis Analyze 1 Δt0")
    dt = max(min(dt0, dt_max), dt_min)
    t_acc = 0.0
    
    # Initial state at @stage i
    ux0, uy0, p0 = _read_nodes(nds)
    
    hist: Dict[str, List[float]] = {
        "time": [], "dt": [], "dUmax": [], "dPmax": [], "ePmax": [],
        "disp_check": [], "pwp_check": [], "decision": []
    }

    if verbose:
        print("\n--- DC-QSA Stage Start ---")
        print(f"dt0={dt0:.3g}s  disp_tol={disp_tol:.3g} m  pwp_tol={pwp_tol:.3g} kPa  "
              f"stg_time={stg_time:.3g} s")
        print(f"min_stage_frac_before_pwp={min_stage_frac_before_pwp:.2f}")
        print("step |   t_acc(s) |    dt(s) |  dUmax(m) | dPmax(kPa) | ePmax(kPa) | disp_check | pwp_check | decision")

    # Perform initial quasi-static analysis (flowchart: "Analyze 1 Δt0")
    if verbose:
        print(f"\n[Initial QS Analysis] Analyzing with dt0={dt0:.3g}s...")
    
    if analysis is not None:
        ok = analysis.TransientAnalyze(dt) #TransientAnalyze
    else:
        ok = ops.analyze(1, dt)
    
    if ok != 0:
        raise RuntimeError(f"Initial quasi-static analysis failed with dt0={dt0}")
    
    # Update accumulated time and read new state
    t_acc += dt
    ux_prev, uy_prev, p_prev = _read_nodes(nds)
    
    # Optional ODB logging
    if ODB is not None:
        try:
            ODB.fetch_response_step()
        except Exception as _e:
            if verbose:
                print(f"[dc_qsa] ODB.fetch_response_step() raised: {_e!r} (continuing)")
    
    # --- Main DC-QSA loop (flowchart: "Run DC-QSA for step i")
    for step in range(1, max_steps + 1):
        
        # Ensure we don't exceed stgTime (flowchart: exit check "aTime > stgTime?")
        if t_acc + dt > stg_time:
            dt = max(stg_time - t_acc, dt_min)
            if dt <= 0:
                break  # Stage time reached
        
        # Run analysis step
        if analysis is not None:
            if getattr(analysis, "debugMode", False) and verbose:
                print(f"  [SmartAnalyze] step {step}, dt={dt:.3g} → entering TransientAnalyze...")
            ok = analysis.TransientAnalyze(dt)
        else:
            ok = ops.analyze(1, dt)
        
        # --- Convergence diamond (flowchart: "Convergence?")
        if ok != 0:
            # No → retry with reduced Δt
            dt_new = max(dt * 0.5, dt_min)
            if verbose:
                print(f"{step:4d} | {t_acc:10.3f} | {dt:8.4g} |     -     |     -     |     -     |    -    |    -    | failed, retry dt={dt_new:.4g}")
            
            if dt_new <= dt_min:
                raise RuntimeError(
                    f"DC-QSA: analysis failed at step {step}; dt reached dt_min={dt_min}."
                )
            dt = dt_new
            continue  # Retry this step
        
        # Yes → accumulate time and read responses
        t_acc += dt
        ux, uy, p = _read_nodes(nds)
        
        # ODB hook
        if ODB is not None:
            try:
                ODB.fetch_response_step()
            except Exception as _e:
                if verbose:
                    print(f"[dc_qsa] ODB.fetch_response_step() raised: {_e!r} (continuing)")
        
        # --- Compute δdisp and ePwp (flowchart: "Compute δdisp, ePwp")
        d_umax = max(
            max(abs(a - b) for a, b in zip(ux, ux_prev)),
            max(abs(a - b) for a, b in zip(uy, uy_prev))
        )
        
        if monitor_pwp:
            d_pmax = max(abs(a - b) for a, b in zip(p, p_prev))  # incremental PWP
            e_pmax = max(abs(pi - p0i) for pi, p0i in zip(p, p0))  # from initial
        else:
            d_pmax = 0.0
            e_pmax = 0.0
        
        ux_prev, uy_prev, p_prev = ux[:], uy[:], p[:]
        
        # --- Decision diamond (flowchart: "δdisp < dispTol?")
        if d_umax < disp_tol:
            # Yes → increase Δt
            dt_new = min(dt * growth, dt_max)
            decision = "increase dt"
        else:
            # No → hold Δt
            dt_new = dt
            decision = "hold dt"
        
        disp_check = f"{d_umax:.3e} < {disp_tol:.3e}" if d_umax < disp_tol else f"{d_umax:.3e} >= {disp_tol:.3e}"
        pwp_check = f"{e_pmax:.3e} < {pwp_tol:.3e}" if e_pmax < pwp_tol else f"{e_pmax:.3e} >= {pwp_tol:.3e}"
        
        # Save to history
        hist["time"].append(t_acc)
        hist["dt"].append(dt)
        hist["dUmax"].append(d_umax)
        hist["dPmax"].append(d_pmax)
        hist["ePmax"].append(e_pmax)
        hist["disp_check"].append(disp_check)
        hist["pwp_check"].append(pwp_check)
        hist["decision"].append(decision)
        
        if verbose:
            print(f"{step:4d} | {t_acc:10.3f} | {dt:8.4g} | {d_umax:9.6g} | {d_pmax:10.6g} | {e_pmax:10.6g} | "
                  f"{disp_check:>15} | {pwp_check:>15} | {decision}")
        
        # --- Exit condition diamond (flowchart: "ePwp < pwpTol or aTime > stgTime?")
        if monitor_pwp:
            if t_acc >= min_stage_frac_before_pwp * stg_time:
                if e_pmax < pwp_tol:
                    if verbose:
                        print(f"\nDC-QSA completed at step {step}, t={t_acc:.3f}s — PWP tolerance reached (ePwp={e_pmax:.3e} < {pwp_tol:.3e})")
                    return DcqsaResult(step, t_acc, hist)
        
        if t_acc >= stg_time:
            if verbose:
                print(f"\nDC-QSA completed at step {step}, t={t_acc:.3f}s — Stage time reached")
            return DcqsaResult(step, t_acc, hist)
        
        # Update Δt for next iteration (maps to flowchart: "Increase Δti" or "Hold Δti")
        dt = dt_new
    
    # --- Safety exit (not explicitly in flowchart, added for robustness)
    if verbose:
        print(f"\nDC-QSA reached max_steps={max_steps} without meeting exit criteria.")
    return DcqsaResult(max_steps, t_acc, hist)


def dc_qsa_enhanced(
    *,
    monitor_nodes: Iterable[int],
    dt0: float,
    disp_tol: float,           # m
    pwp_tol: float,            # kPa
    stg_time: float,           # days or seconds
    monitor_pwp: bool = True,
    dt_min: float = 0.01,      # s
    dt_max: float = 3600.0,    # s
    growth: float = 1.5,
    shrink: float = 0.5,
    max_steps: int = 5000,
    min_stage_frac_before_pwp: float = 0.10,
    verbose: bool = True,
    analysis: Optional[object] = None,
    ODB: Optional[object] = None,
    verify_initial_state: bool = True,
) -> DcqsaResult:
    """
    Enhanced DC-QSA algorithm following the paper with proper unit handling.
    """

    nds = list(monitor_nodes)
    if not nds:
        raise ValueError("monitor_nodes is empty.")

    # --- Stage time conversion
    if stg_time <= 0:
        raise ValueError("stg_time must be positive.")
    if stg_time <= 10000:
        stg_time_sec = float(stg_time) * 86400.0
        stg_time_note = f"{stg_time} days -> {stg_time_sec:.3f} s"
    else:
        stg_time_sec = float(stg_time)
        stg_time_note = f"{stg_time_sec:.3f} s (assumed seconds)"

    missing_nodes_warned = set()

    def _get_pwp(nd: int) -> float:
        if not monitor_pwp:
            return 0.0
        try:
            return float(ops.nodeVel(nd, 3))  # kPa if using kN-m-s #nodeDisp
        except Exception:
            if nd not in missing_nodes_warned and verbose:
                print(f"[dc_qsa] warning: pore pressure for node {nd} not readable.")
                missing_nodes_warned.add(nd)
            return 0.0

    def _read_nodes(node_tags: List[int]) -> Tuple[List[float], List[float], List[float]]:
        ux, uy, p = [], [], []
        for nd in node_tags:
            try:
                ux.append(float(ops.nodeDisp(nd, 1)))
                uy.append(float(ops.nodeDisp(nd, 2)))
                p.append(_get_pwp(nd))
            except Exception:
                if nd not in missing_nodes_warned and verbose:
                    print(f"[dc_qsa] warning: node {nd} not readable. Using zeros.")
                    missing_nodes_warned.add(nd)
                ux.append(0.0); uy.append(0.0); p.append(0.0)
        return ux, uy, p

    # --- Init
    dt = max(min(dt0, dt_max), dt_min)
    t_acc = 0.0
    ux0, uy0, p0 = _read_nodes(nds)

    hist: Dict[str, List[float]] = {
        "time": [], "dt": [],
        "dUmax_m": [], "dPmax_kPa": [], "ePmax_kPa": [],
        "disp_check": [], "pwp_check": [],
        "decision": [], "convergence": []
    }

    if verbose:
        print("\n--- Enhanced DC-QSA Stage Start ---")
        print(f"stg_time interpretation: {stg_time_note}")
        print(f"dt0={dt0:.6g} s  disp_tol={disp_tol:.6g} m ({disp_tol*1e3:.3f} mm)  pwp_tol={pwp_tol:.6g} kPa")
        print(f"dt_min={dt_min}s  dt_max={dt_max}s")
        print("step |   t_acc(s) |    dt(s) |  dU(mm) | dP(kPa) | eP(kPa) | dispChk | pwpChk | decision")
        print("-" * 105)

    # --- First step
    if analysis is not None:
        ok = analysis.TransientAnalyze(dt)
    else:
        ok = ops.analyze(1, dt)
    if ok != 0:
        raise RuntimeError(f"Initial analysis failed with dt0={dt0}")

    t_acc += dt
    ux_prev, uy_prev, p_prev = _read_nodes(nds)

    if ODB is not None:
        try: ODB.fetch_response_step()
        except Exception: pass

    consecutive_small_disp = 0

    # --- Loop
    for step in range(1, max_steps + 1):

        if t_acc >= stg_time_sec:
            if verbose: print(f"\nStage time reached: {t_acc:.3f}s >= {stg_time_sec:.3f}s")
            break

        if t_acc + dt > stg_time_sec:
            dt = max(stg_time_sec - t_acc, dt_min)

        if analysis is not None:
            ok = analysis.TransientAnalyze(dt)
        else:
            ok = ops.analyze(1, dt)

        if ok != 0:
            dt_new = max(dt * shrink, dt_min)
            if dt_new <= dt_min + 1e-12:
                raise RuntimeError(f"Analysis failed at step {step}, cannot reduce dt further")
            dt = dt_new
            consecutive_small_disp = 0
            continue

        # Update state
        t_acc += dt
        ux, uy, p = _read_nodes(nds)

        if ODB is not None:
            try: ODB.fetch_response_step()
            except Exception: pass

        d_umax = max(
            max((abs(a - b) for a, b in zip(ux, ux_prev)), default=0.0),
            max((abs(a - b) for a, b in zip(uy, uy_prev)), default=0.0)
        )
        d_umax_mm = d_umax * 1e3
        d_pmax = max((abs(a - b) for a, b in zip(p, p_prev)), default=0.0)
        e_pmax = max((abs(pi - p0i) for pi, p0i in zip(p, p0)), default=0.0)

        ux_prev, uy_prev, p_prev = ux[:], uy[:], p[:]

        # --- Flowchart checks
        disp_check = (d_umax < disp_tol)
        pwp_check = (e_pmax < pwp_tol) or (t_acc > stg_time_sec)

        if disp_check:
            consecutive_small_disp += 1
            if consecutive_small_disp >= 3:
                dt_new = min(dt * growth, dt_max)
                decision = "increase"
            else:
                dt_new = dt
                decision = "hold"
        else:
            consecutive_small_disp = 0
            dt_new = dt
            decision = "hold"

        if pwp_check:
            decision = "completed"

        # Log
        hist["time"].append(t_acc)
        hist["dt"].append(dt)
        hist["dUmax_m"].append(d_umax)
        hist["dPmax_kPa"].append(d_pmax)
        hist["ePmax_kPa"].append(e_pmax)
        hist["disp_check"].append(disp_check)
        hist["pwp_check"].append(pwp_check)
        hist["convergence"].append(ok == 0)
        hist["decision"].append(decision)

        # Print
        if verbose and (step <= 10 or step % 10 == 0 or disp_check or pwp_check):
            print(f"{step:4d} | {t_acc:10.3f} | {dt:8.4g} | {d_umax_mm:7.4f} | "
                  f"{d_pmax:7.3f} | {e_pmax:7.3f} | "
                  f"{'PASS' if disp_check else 'FAIL':^7} | "
                  f"{'PASS' if pwp_check else 'FAIL':^7} | "
                  f"{decision:^9}")

        if decision == "completed":
            if verbose:
                print(f"\n✓ Analysis completed at t={t_acc:.3f}s ({t_acc/86400:.3f} days)")
            return DcqsaResult(step, t_acc, hist)

        dt = dt_new

    if verbose:
        if t_acc >= stg_time_sec:
            print(f"\n✓ Stage time completed: {t_acc:.3f}s")
        else:
            print(f"\n⚠ Maximum steps ({max_steps}) reached without full convergence")

    return DcqsaResult(step, t_acc, hist)


###########################################################
#                                                         #
# OTHER QUAD ELEMENTS CREATION                            #
#                                                         #
###########################################################


def generate_block(start_x, start_y, length, height, node_offset, elem_offset, etype, mat_tag, thickness, box_width, box_height, block_name="block"):
    num_x = int(length / box_width)
    num_y = int(height / box_height)

    def block_node_id(i, j):
        return node_offset + j * (num_x + 1) + i + 1

    block_nodes = []
    block_elements = []

    # Create nodes
    for j in range(num_y + 1):
        for i in range(num_x + 1):
            nid = block_node_id(i, j)
            x = start_x + i * box_width
            y = start_y + j * box_height
            ops.node(nid, x, y)
            created_nodes.append((nid, x, y))
            block_nodes.append(nid)

    # Create elements
    eid = elem_offset
    for j in range(num_y):
        for i in range(num_x):
            n1 = block_node_id(i, j)
            n2 = block_node_id(i + 1, j)
            n3 = block_node_id(i + 1, j + 1)
            n4 = block_node_id(i, j + 1)
            # element quadUP $eleTag $iNode $jNode $kNode $lNode $thick $matTag $bulk $fmass $hPerm $vPerm <$b1=0 $b2=0 $t=0>
            ops.element("enhancedQuad", eid, n1, n2, n3, n4, thickness, etype, mat_tag) #enhancedQuad , quadWithSensitivity
            created_elements.append((eid, n1, n2, n3, n4))
            block_elements.append(eid)
            eid += 1

    # Register block
    block_registry[block_name] = {
        "nodes": block_nodes,
        "elements": block_elements,
    }

    return (node_offset + (num_x + 1) * (num_y + 1), elem_offset + num_x * num_y)

def generate_bbar_quadup_block(
    start_x, start_y, length, height, node_offset, elem_offset, 
    thickness, material_tag, bulk,
    fluid_mass_density, horizontal_perm, vertical_perm, b1, b2, 
    box_width, box_height, block_name="block"
):
    num_x = int(length / box_width)
    num_y = int(height / box_height)

    if num_x <= 0 or num_y <= 0:
        raise ValueError("Box width/height too large for given length/height. Must result in at least one element.")

    def get_node_id(i, j):
        return node_offset + j * (num_x + 1) + i + 1

    block_nodes = []
    block_elements = []

    # Create nodes
    for j in range(num_y + 1):
        for i in range(num_x + 1):
            node_id = get_node_id(i, j)
            x_coord = start_x + i * box_width
            y_coord = start_y + j * box_height
            ops.node(node_id, x_coord, y_coord)
            created_nodes.append((node_id, x_coord, y_coord))
            block_nodes.append(node_id)

    # Create elements
    element_id = elem_offset
    for j in range(num_y):
        for i in range(num_x):
            n1 = get_node_id(i, j)
            n2 = get_node_id(i + 1, j)
            n3 = get_node_id(i + 1, j + 1)
            n4 = get_node_id(i, j + 1)
            ops.element(
                "bbarQuadUP", element_id, n1, n2, n3, n4, #quadUP , bbarQuadUP
                thickness, material_tag, bulk,
                fluid_mass_density, horizontal_perm, vertical_perm, b1, b2,
            )
            created_elements.append((element_id, n1, n2, n3, n4))
            block_elements.append(element_id)
            element_id += 1

    # Register block
    block_registry[block_name] = {
        "nodes": block_nodes,
        "elements": block_elements,
    }

    next_node_id = node_offset + (num_x + 1) * (num_y + 1)
    next_elem_id = element_id

    return next_node_id, next_elem_id


def generate_ssp_quadup_block(
    start_x, start_y, length, height, node_offset, elem_offset, 
    material_tag, thickness, fluid_bulk,
    fluid_mass_density, horizontal_perm, vertical_perm, void, alpha, b1, b2,
    box_width, box_height, block_name="block"
):
    num_x = int(length / box_width)
    num_y = int(height / box_height)

    if num_x <= 0 or num_y <= 0:
        raise ValueError("Box width/height too large for given length/height. Must result in at least one element.")

    def get_node_id(i, j):
        return node_offset + j * (num_x + 1) + i + 1

    block_nodes = []
    block_elements = []

    # Create nodes
    for j in range(num_y + 1):
        for i in range(num_x + 1):
            node_id = get_node_id(i, j)
            x_coord = start_x + i * box_width
            y_coord = start_y + j * box_height
            ops.node(node_id, x_coord, y_coord)
            created_nodes.append((node_id, x_coord, y_coord))  # <-- fixed (was x, y)
            block_nodes.append(node_id)

    # Create elements
    element_id = elem_offset
    for j in range(num_y):
        for i in range(num_x):
            n1 = get_node_id(i, j)
            n2 = get_node_id(i + 1, j)
            n3 = get_node_id(i + 1, j + 1)
            n4 = get_node_id(i, j + 1)
            ops.element(
                "SSPquadUP", element_id, n1, n2, n3, n4, 
                int(material_tag), thickness, fluid_bulk,
                fluid_mass_density, horizontal_perm, vertical_perm, void, alpha, b1, b2
            )
            created_elements.append((element_id, n1, n2, n3, n4))
            block_elements.append(element_id)
            element_id += 1

    # Register block
    block_registry[block_name] = {
        "nodes": block_nodes,
        "elements": block_elements,
    }

    next_node_id = node_offset + (num_x + 1) * (num_y + 1)
    next_elem_id = element_id

    return next_node_id, next_elem_id


def create_ring_quads(set_a_coords, set_b_coords, start_node_id, start_elem_id,
                      thickness, etype, mat_tag, block_name="ring_quads"):
    assert len(set_a_coords) == len(set_b_coords), "Mismatch in point count."

    num = len(set_a_coords)
    node_ids_a = []
    node_ids_b = []

    # Create nodes for set_a
    for i, (x, y) in enumerate(set_a_coords):
        nid = start_node_id + i
        ops.node(nid, x, y)
        created_nodes.append((nid, x, y))
        node_ids_a.append(nid)

    # Create nodes for set_b
    for i, (x, y) in enumerate(set_b_coords):
        nid = start_node_id + num + i
        ops.node(nid, x, y)
        created_nodes.append((nid, x, y))
        node_ids_b.append(nid)

    # Create quad elements
    quad_ids = []
    for i in range(num):
        n1 = node_ids_a[i]
        n2 = node_ids_a[(i + 1) % num]
        n3 = node_ids_b[(i + 1) % num]
        n4 = node_ids_b[i]
        eid = start_elem_id + i
        ops.element("quadWithSensitivity", eid, n1, n2, n3, n4, thickness, etype, mat_tag)
        created_elements.append((eid, n1, n2, n3, n4))
        quad_ids.append(eid)

    block_registry[block_name] = {
        "nodes": node_ids_a + node_ids_b,
        "elements": quad_ids
    }

    return node_ids_a + node_ids_b, quad_ids

def create_bbar_quadup_ring_quads(
    bottom_nodes, top_nodes, start_node_id, start_element_id,
    thickness, material_tag, bulk,
    fluid_mass_density, horizontal_perm, vertical_perm, b1, b2, block_name="ring_quads"
):
    """
    Create a ring of bbarQuadUP elements from two sets of coordinates.
    """
    num = len(bottom_nodes)
    assert num == len(top_nodes), "Mismatch in point count."

    node_ids_a = []
    node_ids_b = []
    for i, (x, y) in enumerate(bottom_nodes):
        node_id = start_node_id + i
        ops.node(node_id, x, y)
        created_nodes.append((node_id, x, y))
        node_ids_a.append(node_id)

    for i, (x, y) in enumerate(top_nodes):
        node_id = start_node_id + num + i
        ops.node(node_id, x, y)
        created_nodes.append((node_id, x, y))
        node_ids_b.append(node_id)

    element_ids = []
    for i in range(num):
        n1 = node_ids_a[i]
        n2 = node_ids_a[(i + 1) % num]
        n3 = node_ids_b[(i + 1) % num]
        n4 = node_ids_b[i]
        element_id = start_element_id + i
        ops.element(
            "bbarQuadUP", element_id, n1, n2, n3, n4, thickness, material_tag, bulk,
            fluid_mass_density, horizontal_perm, vertical_perm, b1, b2
        )
        created_elements.append((element_id, n1, n2, n3, n4))
        element_ids.append(element_id)

    block_registry[block_name] = {
        "nodes": node_ids_a + node_ids_b,
        "elements": element_ids
    }

    return node_ids_a + node_ids_b, element_ids


def create_ring_triangles(bottom_nodes, top_nodes, start_elem_id, etype, mat_tag, thickness, block_name="ring_triangles"):
    expected_top = 2 * (len(bottom_nodes) - 1) + 1
    assert len(top_nodes) >= expected_top, f"Top node count must be at least 2*(bottom-1)+1. Got {len(top_nodes)}."

    created_elements = []
    quad_ids = []
    eid = start_elem_id

    for i in range(len(bottom_nodes) - 1):
        b0 = bottom_nodes[i]
        b1 = bottom_nodes[i + 1]
        t0 = top_nodes[2 * i]
        t1 = top_nodes[2 * i + 1]
        t2 = top_nodes[2 * i + 2]

        # Triangle 1 (bottom to top left)
        ops.element("quadWithSensitivity", eid, b0, b0, t1, t0, thickness, etype, mat_tag)
        created_elements.append((eid, b0, b0, t1, t0))
        quad_ids.append(eid)
        eid += 1

        # Triangle 2 (bottom span)
        ops.element("quadWithSensitivity", eid, b0, b0, b1, t1, thickness, etype, mat_tag)
        created_elements.append((eid, b0, b0, b1, t1))
        quad_ids.append(eid)
        eid += 1

        # Triangle 3 (bottom to top right)
        ops.element("quadWithSensitivity", eid, b1, b1, t2, t1, thickness, etype, mat_tag)
        created_elements.append((eid, b1, b1, t2, t1))
        quad_ids.append(eid)
        eid += 1

    block_registry[block_name] = {
        "elements": quad_ids
    }

    return quad_ids


def create_bbar_quadup_ring_triangles(
    bottom_nodes, top_nodes, start_element_id, thickness, material_tag,
    bulk, fluid_mass_density, horizontal_perm, vertical_perm,
    block_name="ring_triangles"):
    """
    Create a ring of bbarQuadUP elements from two sets of coordinates.
    """
    assert len(top_nodes) >= 2 * (len(bottom_nodes) - 1) + 1, (
        f"Top node count must be at least 2*(bottom-1)+1. Got {len(top_nodes)}."
    )

    created_elements = []
    element_ids = []
    element_id = start_element_id

    for i in range(len(bottom_nodes) - 1):
        bottom_node_1 = bottom_nodes[i]
        bottom_node_2 = bottom_nodes[i + 1]
        top_node_1 = top_nodes[2 * i]
        top_node_2 = top_nodes[2 * i + 1]
        top_node_3 = top_nodes[2 * i + 2]

        # Triangle 1 (bottom to top left)
        ops.element(
            "bbarQuadUP", element_id, bottom_node_1, bottom_node_1,
            top_node_2, top_node_1, thickness, material_tag, bulk,
            fluid_mass_density, horizontal_perm, vertical_perm
        )
        created_elements.append((element_id, bottom_node_1, bottom_node_1, top_node_2, top_node_1))
        element_ids.append(element_id)
        element_id += 1

        # Triangle 2 (bottom span)
        ops.element(
            "bbarQuadUP", element_id, bottom_node_1, bottom_node_1,
            bottom_node_2, top_node_2, thickness, material_tag, bulk,
            fluid_mass_density, horizontal_perm, vertical_perm
        )
        created_elements.append((element_id, bottom_node_1, bottom_node_1, bottom_node_2, top_node_2))
        element_ids.append(element_id)
        element_id += 1

        # Triangle 3 (bottom to top right)
        ops.element(
            "bbarQuadUP", element_id, bottom_node_2, bottom_node_2,
            top_node_3, top_node_2, thickness, material_tag, bulk,
            fluid_mass_density, horizontal_perm, vertical_perm
        )
        created_elements.append((element_id, bottom_node_2, bottom_node_2, top_node_3, top_node_2))
        element_ids.append(element_id)
        element_id += 1

    block_registry[block_name] = {
        "nodes": bottom_nodes + top_nodes,
        "elements": element_ids
    }

    return element_ids


def create_quad_strip_from_nodes(edge1_nodes, edge2_nodes, start_elem_id, thickness, etype, mat_tag, block_name="quad_strip"):
    assert len(edge1_nodes) == len(edge2_nodes), "Node lists must be equal length"
    quad_ids = []

    for i in range(len(edge1_nodes) - 1):
        n1 = edge1_nodes[i]
        n2 = edge1_nodes[i + 1]
        n3 = edge2_nodes[i + 1]
        n4 = edge2_nodes[i]

        eid = start_elem_id + i
        ops.element("quadWithSensitivity", eid, n1, n2, n3, n4, thickness, etype, mat_tag)
        created_elements.append((eid, n1, n2, n3, n4))
        quad_ids.append(eid)

    block_registry[block_name] = {
        "nodes": edge1_nodes + edge2_nodes,
        "elements": quad_ids
    }

    return quad_ids


def create_bbar_quadup_strip_from_nodes(
    edge1_nodes, edge2_nodes, start_element_id, thickness, material_id, bulk,
    fluid_mass_density, horizontal_perm, vertical_perm, block_name="quad_strip"
):
    """Create a strip of bbarQuadUP elements from two node lists."""
    assert len(edge1_nodes) == len(edge2_nodes), "Node lists must be equal length"

    element_ids = []
    for i in range(len(edge1_nodes) - 1):
        node1 = edge1_nodes[i]
        node2 = edge1_nodes[i + 1]
        node3 = edge2_nodes[i + 1]
        node4 = edge2_nodes[i]

        element_id = start_element_id + i
        ops.element(
            "bbarQuadUP", element_id, node1, node2, node3, node4, thickness, material_id, bulk,
            fluid_mass_density, horizontal_perm, vertical_perm
        )
        created_elements.append((element_id, node1, node2, node3, node4))
        element_ids.append(element_id)

    block_registry[block_name] = {
        "nodes": edge1_nodes + edge2_nodes,
        "elements": element_ids
    }

    return element_ids


def add_paired_quads_by_range(
    bottom_start, bottom_end, bottom_step,
    top_start, top_end, top_step,
    thickness, etype, mat_tag,
    block_name="paired_quads"):
    
    last_eid = max(ops.getEleTags()) if ops.getEleTags() else 0
    bottom_nodes = list(range(bottom_start, bottom_end + 1, bottom_step))
    top_nodes = list(range(top_start, top_end + 1, top_step))

    pair_count = min(len(bottom_nodes), len(top_nodes)) - 1
    start_elem_id = last_eid + 1

    paired_quad_ids = []
    for i in range(pair_count):
        n1 = bottom_nodes[i]
        n2 = bottom_nodes[i + 1]
        n3 = top_nodes[i + 1]
        n4 = top_nodes[i]
        eid = start_elem_id + i
        ops.element("quadWithSensitivity", eid, n1, n2, n3, n4, thickness, etype, mat_tag)
        created_elements.append((eid, n1, n2, n3, n4))
        paired_quad_ids.append(eid)

    block_registry[block_name] = {
        "nodes": bottom_nodes + top_nodes,
        "elements": paired_quad_ids
    }

def add_paired_bbar_quadup_by_range(
    bottom_node_start, bottom_node_end, bottom_node_step,
    top_node_start, top_node_end, top_node_step,
    thickness, material_tag, bulk,
    fluid_mass_density, horizontal_perm, vertical_perm,
    block_name="paired_bbar_quadup"
):
    """
    Create a strip of bbarQuadUP elements from two node lists.
    """
    last_element_id = max(ops.getEleTags()) if ops.getEleTags() else 0
    bottom_nodes = list(
        range(bottom_node_start, bottom_node_end + 1, bottom_node_step)
    )
    top_nodes = list(
        range(top_node_start, top_node_end + 1, top_node_step)
    )

    pair_count = min(len(bottom_nodes), len(top_nodes)) - 1
    start_element_id = last_element_id + 1

    paired_element_ids = []
    for i in range(pair_count):
        node1 = bottom_nodes[i]
        node2 = bottom_nodes[i + 1]
        node3 = top_nodes[i + 1]
        node4 = top_nodes[i]
        element_id = start_element_id + i
        ops.element(
            "bbarQuadUP", element_id, node1, node2, node3, node4, thickness,
            material_tag, bulk, fluid_mass_density, horizontal_perm, vertical_perm
        )
        created_elements.append((element_id, node1, node2, node3, node4))
        paired_element_ids.append(element_id)

    block_registry[block_name] = {
        "nodes": bottom_nodes + top_nodes,
        "elements": paired_element_ids
    }

def remove_block(ops, start_elem: int, elem_count: int, node_start: int, node_base: int) -> None:
    """
    Remove a block of elements and associated nodes.

    Args:
        ops: The OpenSees (or similar) ops object with remove().
        start_elem (int): First element to remove.
        elem_count (int): Number of consecutive elements to remove.
        node_start (int): First node in the consecutive node block.
        node_base (int): Base node ID. Function will also handle node_base+1 and node_base-1.
    """
    # Remove elements
    for ele in range(start_elem, start_elem + elem_count):
        ops.remove("element", ele)

    # Remove consecutive nodes
    for node in range(node_start, node_start + elem_count - 1):
        ops.remove("node", node)

    # Node bases: base, base+1, base-1
    for i in range(elem_count):
        ops.remove("node", node_base + i * 3)       # main base
        ops.remove("node", (node_base + 1) + i * 3) # base+1
    for i in range(elem_count - 1):
        ops.remove("node", (node_base - 1) + i * 3) # base-1

def remove_simple_block(ops, start_elem: int, elem_count: int, start_node: int) -> None:
    """
    Remove a simple block of consecutive elements and nodes.

    Args:
        ops: The OpenSees (or similar) ops object with remove().
        start_elem (int): First element ID to remove.
        elem_count (int): Number of consecutive elements to remove.
        start_node (int): First node ID to remove (removes elem_count - 1 nodes).
    """
    # Remove elements
    for ele in range(start_elem, start_elem + elem_count):
        ops.remove("element", ele)

    # Remove consecutive nodes
    for node in range(start_node, start_node + (elem_count - 1)):
        ops.remove("node", node)

def remove_custom_block(
    ops,
    start_elem: int,
    elem_count: int,
    elem_step: int,
    start_node: int,
    node_count: int,
    node_step: int
) -> None:
    """
    Remove a block of elements and nodes with custom stepping.

    Args:
        ops: The OpenSees (or similar) ops object with remove().
        start_elem (int): First element ID to remove.
        elem_count (int): Number of elements to remove.
        elem_step (int): Step size between element IDs.
        start_node (int): First node ID to remove.
        node_count (int): Number of nodes to remove.
        node_step (int): Step size between node IDs.
    """
    # Remove elements
    for i in range(elem_count):
        ele = start_elem + i * elem_step
        ops.remove("element", ele)

    # Remove nodes
    for i in range(node_count):
        node = start_node + i * node_step
        ops.remove("node", node)


def convert_trimsh_to_quadmsh(input_file: str, output_file: str) -> None:
    with open(input_file, "r") as f:
        lines = f.readlines()

    in_elements = False
    updated_lines = []

    for line in lines:
        if line.strip() == "$Elements":
            in_elements = True
            updated_lines.append(line)
            continue
        if line.strip() == "$EndElements":
            in_elements = False
            updated_lines.append(line)
            continue

        if in_elements and line.strip():
            parts = line.strip().split()
            # Element index + nodes
            if len(parts) == 4:  # 1 element ID + 3 nodes
                element_id, n1, n2, n3 = parts
                updated_lines.append(f"{element_id} {n1} {n1} {n2} {n3}\n")
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    with open(output_file, "w") as f:
        f.writelines(updated_lines)