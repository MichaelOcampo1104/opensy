from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple
import logging

import openseespy.opensees as ops
import numpy as np
import matplotlib.pyplot as plt

from blueprints.codes.eurocode.nen_en_1992_1_1_c2_2011 import NEN_EN_1992_1_1_C2_2011
from blueprints.codes.formula import Formula
from blueprints.codes.latex_formula import LatexFormula #latex_replace_symbols
from blueprints.type_alias import MM, MM2, MM4, MPA, DIMENSIONLESS
from blueprints.validations import raise_if_negative


def _validate_positive_values(**kwargs):
    """
    Validates that all provided keyword arguments are greater than zero.

    Parameters
    ----------
    **kwargs :
        A dictionary of parameter_name=value pairs to validate.
    """
    for param_name, value in kwargs.items():
        if value <= 0:
            raise ValueError(f"Parameter '{param_name}' must be greater than zero, but got {value}.")


class FormRectangularInertia(Formula):
    r"""Moment of inertia (second moment of area) for a rectangular section."""

    label = "I = bh^3 / 12"
    source_document = NEN_EN_1992_1_1_C2_2011

    def __init__(self, b: MM, h: MM) -> None:
        r"""Moment of Inertia of a rectangle.

        Parameters
        ----------
        b : MM
            Base width of the rectangle [mm].
        h : MM
            Height of the rectangle [mm].
        """
        super().__init__()
        self.b = b
        self.h = h

    @staticmethod
    def _evaluate(b: MM, h: MM) -> MM4:
        raise_if_negative(b=b, h=h)
        return (b * h ** 3) / 12

    def latex(self) -> LatexFormula:
        _equation = r"\frac{b \cdot h^3}{12}"
        _numeric_equation = latex_replace_symbols(
            _equation,
            {
                r"b": f"{self.b:.3f}",
                r"h": f"{self.h:.3f}",
            },
            False,
        )
        return LatexFormula(
            return_symbol=r"I",
            result=f"{self:.3f}",
            equation=_equation,
            numeric_equation=_numeric_equation,
            comparison_operator_label="=",
            unit="mm^4",
        )
    
class FormShearModulus(Formula):
    r"""Class representing the formula for the shear modulus G."""

    label = "G"
    source_document = NEN_EN_1992_1_1_C2_2011

    def __init__(
        self,
        E: MPA,
        poisson_ratio: DIMENSIONLESS,
    ) -> None:
        r"""[$$G$$] Shear modulus in the elastic range.

        Parameters
        ----------
        E : MPA
            [$$E$$] Young's modulus of elasticity [$$MPa$$].
        poisson_ratio : DIMENSIONLESS
            [$$\nu$$] Poisson's ratio [-].
        """
        super().__init__()
        self.E = E
        self.poisson_ratio = poisson_ratio

    @staticmethod
    def _evaluate(
        E: MPA,
        poisson_ratio: DIMENSIONLESS,
    ) -> MPA:
        """Evaluates the formula for the shear modulus, for more information see the __init__ method."""
        _validate_positive_values(E=E)
        raise_if_negative(poisson_ratio=poisson_ratio)

        return E / (2 * (1 + poisson_ratio))

    def latex(self) -> LatexFormula:
        """Returns LatexFormula object for the shear modulus formula."""
        _equation: str = r"\frac{E}{2 \cdot (1 + \nu)}"
        _numeric_equation: str = latex_replace_symbols(
            _equation,
            {
                r"E": f"{self.E:.3f}",
                r"\nu": f"{self.poisson_ratio:.3f}",
            },
            False,
        )
        return LatexFormula(
            return_symbol=r"G",
            result=f"{self:.3f}",
            equation=_equation,
            numeric_equation=_numeric_equation,
            comparison_operator_label="=",
            unit="MPa",
        )

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


def add_nodes_from_coordinates(coord_list, start_id, block_name):
    node_ids = []
    for i, (x, y) in enumerate(coord_list):
        nid = start_id + i
        ops.node(nid, x, y)
        created_nodes.append((nid, x, y))
        node_ids.append(nid)

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
# CREATE ZERO LENGTH CONTACT CHAINS                       #
#                                                         #
########################################################### 

def create_zero_length_contact2d_chain(node_list_1: list[int], node_list_2: list[int],
                                       Kn: float, Kt: float, fs: float,
                                       start_id: int,
                                       normal: tuple[float, float],
                                       block_name: str = "zero_length_contacts") -> list[int]:
    """
    Create a chain of ZeroLengthContact2D elements from pairs of nodes.
    """
    if len(node_list_1) != len(node_list_2):
        raise ValueError("node_list_1 and node_list_2 must have the same length")

    contact_elem_ids = []
    Nx, Ny = normal

    for i, (n1, n2) in enumerate(zip(node_list_1, node_list_2)):
        tag = start_id + i
        ops.element("zeroLengthContact2D", tag, n1, n2, Kn, Kt, fs, "-normal", Nx, Ny)
        contact_elem_ids.append(tag)

    block_registry[block_name] = {
        "nodes": node_list_1 + node_list_2,
        "elements": contact_elem_ids
    }

    return contact_elem_ids


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


"""
File: openseespy_dc_qsa_framework.py

Purpose
-------
A compact, readable OpenSeesPy (ops) staging + DC-QSA controller you can drop
into your excavation model. It focuses on the analysis framework:
  • analysis component setup (constraints/numberer/system/algorithm/integrator/test)
  • displacement-controlled quasi-static (DC-QSA) loop with time-step adaptation
  • construction stage helpers (activate/deactivate element sets, add bracing, etc.)
  • plotting helper to visualize Δu, Δp, and Δt versus time

How to use
----------
1) Build your mesh & materials (e.g., PDMY/PDMY02 with quadUP/SSPquadUP) and
   your wall/interface/bracing elements in a separate script.
2) Import this module and call `setup_analysis()` once.
3) For each construction stage, call `dc_qsa()` with the stage parameters from
your framework (Δt0, dispTol, pwpTol, stgTime), optionally removing/adding
clusters/elements between stages via the helpers.
4) After each stage, use `plot_stage_history(result)` to visualize history.

Notes
-----
* The controller checks solid DOFs 1–2 (ux, uy) with `ops.nodeDisp` and DOF 3
  (pore pressure) with `ops.nodeVel`. If your nodes are not u-p type, keep
  `monitor_pwp=False`.
* Time units are seconds; displacement tolerance in model length units; pressure
  tolerance in model pressure units. Keep them consistent with your unit system.
"""

# -----------------------------------------------------------------------------
# Analysis components
# -----------------------------------------------------------------------------

def setup_analysis(*,
                   constraints: str = 'Penalty',
                   numberer: str = 'RCM',
                   system: str = 'BandGeneral',
                   algorithm: str = 'Newton',
                   integrator: Tuple[str, Tuple[float, float]] = ('Newmark', (0.5, 0.25)),
                   test: Tuple[str, Tuple[float, int, int]] = ('NormUnbalance', (1e-6, 50, 0)),
                   rayleigh: Tuple[float, float, float, float] | None = None) -> None:
    """Configure standard components for fully-coupled u-p quasi-static runs."""
    ops.constraints(constraints)
    ops.numberer(numberer)
    ops.system(system)
    ops.test(test[0], *test[1])
    ops.algorithm(algorithm)

    if integrator[0].lower() == 'newmark':
        gamma, beta = integrator[1]
        ops.integrator('Newmark', gamma, beta)
    elif integrator[0].lower() in {'generalizedalpha', 'genalpha'}:
        ops.integrator('GeneralizedAlpha', *integrator[1])
    elif integrator[0].lower() in {'backwardeuler', 'be'}:
        ops.integrator('BackwardEuler')
    elif integrator[0].lower() in {'trbdf2'}:
        if integrator[1]:
            gamma = integrator[1][0]
            ops.integrator('TRBDF2', gamma)
        else:
            ops.integrator('TRBDF2', 0.5)
    else:
        raise ValueError(f"Unsupported integrator: {integrator[0]}")

    ops.analysis('Transient')

    if rayleigh:
        a0, a1, a2, a3 = rayleigh
        ops.rayleigh(a0, a1, a2, a3)



# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def _node_vals(node_tags: Sequence[int]) -> Tuple[List[float], List[float], List[float]]:
    """Return ux, uy, p lists (p=0.0 if node doesn't have DOF 3).

    ux, uy are from ops.nodeDisp; p is from ops.nodeVel for DOF3.
    """
    ux, uy, p = [], [], []
    for nd in node_tags:
        ux.append(ops.nodeDisp(nd, 1))
        uy.append(ops.nodeDisp(nd, 2))
        try:
            p.append(ops.nodeVel(nd, 3))  # DOF3 is pressure for u-p nodes
        except Exception:
            p.append(0.0)
    return ux, uy, p


def _max_abs_delta(a: Sequence[float], b: Sequence[float]) -> float:
    return max((abs(x - y) for x, y in zip(a, b)), default=0.0)


@dataclass
class DcqsaResult:
    steps: int
    t_accum: float
    history: Dict[str, List[float]]  # keys: 'time', 'dt', 'dUmax', 'dPmax'


# -----------------------------------------------------------------------------
# DC-QSA controller
# -----------------------------------------------------------------------------

def dc_qsa(*,
           monitor_nodes: Sequence[int],
           dt0: float,
           disp_tol: float,
           pwp_tol: float,
           stg_time: float,
           monitor_pwp: bool = True,
           dt_min: float = 0.01,
           dt_max: float = 3600.0,
           growth: float = 1.5,
           max_steps: int = 5000) -> DcqsaResult:
    """Run displacement-controlled quasi-static analysis for the current stage.

    Control parameters (per stage): Δt0, dispTol, pwpTol, stgTime.
    """
    if dt0 <= 0:
        raise ValueError("dt0 must be > 0")

    nds = list(monitor_nodes)
    u_prev = _node_vals(nds)

    dt = max(dt0, dt_min)
    t_acc = 0.0

    hist = {"time": [], "dt": [], "dUmax": [], "dPmax": []}

    for step in range(1, max_steps + 1):
        ok = ops.analyze(1, dt)
        if ok != 0:
            dt *= 0.5
            if dt < dt_min:
                raise RuntimeError(f"Analyze failed at step {step} with dt below dt_min.")
            continue

        ux, uy, p = _node_vals(nds)
        d_umax = max(_max_abs_delta(ux, u_prev[0]), _max_abs_delta(uy, u_prev[1]))
        d_pmax = _max_abs_delta(p, u_prev[2]) if monitor_pwp else 0.0
        u_prev = (ux, uy, p)

        t_acc += dt
        hist["time"].append(t_acc)
        hist["dt"].append(dt)
        hist["dUmax"].append(d_umax)
        hist["dPmax"].append(d_pmax)

        if d_umax <= disp_tol:
            dt = min(dt * growth, dt_max)
        else:
            dt = max(dt, dt_min)

        # Exit criteria
        if monitor_pwp:
            if (d_pmax <= pwp_tol and t_acc >= 0.1 * stg_time) or t_acc >= stg_time:
                return DcqsaResult(steps=step, t_accum=t_acc, history=hist)
        else:
            if t_acc >= stg_time:
                return DcqsaResult(steps=step, t_accum=t_acc, history=hist)

    return DcqsaResult(steps=max_steps, t_accum=t_acc, history=hist)


# -----------------------------------------------------------------------------
# Plotting helper
# -----------------------------------------------------------------------------

def plot_stage_history(result: DcqsaResult, stage_name: str = "Stage") -> None:
    """Plot dUmax, dPmax, and dt versus time for a stage result."""
    t = result.history["time"]
    dU = result.history["dUmax"]
    dP = result.history["dPmax"]
    dt = result.history["dt"]

    fig, axs = plt.subplots(3, 1, figsize=(6, 8), sharex=True)

    axs[0].plot(t, dU, label="Δu max")
    axs[0].set_ylabel("Δu")
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(t, dP, color="tab:red", label="Δp max")
    axs[1].set_ylabel("Δp")
    axs[1].legend()
    axs[1].grid(True)

    axs[2].plot(t, dt, color="tab:green", label="Δt")
    axs[2].set_ylabel("Δt [s]")
    axs[2].set_xlabel("Time [s]")
    axs[2].legend()
    axs[2].grid(True)

    fig.suptitle(f"DC-QSA History: {stage_name}")
    plt.tight_layout()
    plt.show()
