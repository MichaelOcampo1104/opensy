#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import openseespy.opensees as ops
from pathlib import Path
from itertools import count, chain, repeat, product, dropwhile, takewhile, islice
import time

# Description: 2D slope stability analysis from Griffiths and Lane (1999) paper
# Example 1: Homogeneous slope with no foundation layer (D=1)
# ref: Griffiths, D. V. and Lande P. A. (1999). Slope stability analysis by Finite elements Geotechnique 49, No. 3, 387-403
# Units: kN, m, sec


def read_blocks(fpath, start_string, end_string):
    """Return blocks of lines between start_string and end_string in a file as list
    ref:https://stackoverflow.com/questions/18865058/extract-values-between-two-strings-in-a-text-file-using-python
    ref:https://stackoverflow.com/questions/27805919/how-to-only-read-lines-in-a-text-file-after-a-certain-string
    """
    with open(fpath) as f:
        while True:
            # it = dropwhile(lambda line: line.strip() != start_string, f)
            # it = takewhile(lambda line: line.strip() != end_string, it)
            it = dropwhile(lambda line: start_string not in line.strip(), f)
            it = takewhile(lambda line: end_string not in line.strip(), it)
            return list(it)[1:]


def read_nodes(fpath):
    """Read nodes tags and coordinates from file
    fpath: path to the nodes file
    Return: a dictionary {node_id: [x, y, x]} datatypes {int: [float, float, float]}"""
    datatypes = [int, float, float, float]
    data = {}
    with open(fpath, "r") as f:
        lines = f.readlines()
    lines = lines[2:]
    for line in lines:
        vals = line.strip(",\n").split(",")
        pvals = [datatype(val.strip()) for val, datatype in zip(vals, datatypes)]
        data.update({pvals[0]: pvals[1:]})
    return data


def read_elements(fpath, element_type="quad"):
    """Read nodes tags and coordinates from file, 4 node Quad elements
    fpath: path to the nodes file
    Return: a dictionary {node_id: [x, y, x]} datatypes {int: [float, float, float]}"""
    # datatypes = [int, int, int, int, int, str, str]
    # datatypes_dict = {"quad": [int for _ in range(0, 5)]}
    datatypes_dict = {"quad": [int] * 5}
    data = {}
    datatypes = datatypes_dict[element_type] + [str, str]
    with open(fpath, "r") as f:
        lines = f.readlines()
    lines = lines[2:]
    for line in lines:
        vals = line.strip(",\n").split(",")
        pvals = [datatype(val.strip()) for val, datatype in zip(vals, datatypes)]
        data.update(
            {
                pvals[0]: {
                    "nodes": pvals[1:5],
                    "element_type": pvals[5],
                    "physical_tag": pvals[6],
                }
            }
        )
    return data


def read_tagged_nodes(fpath, physical_tags):
    """Get nodes from the tag file
    fpath: path to the tag file, where the boundary conditions are written
    physical_tag: physical tag for nodes in Gmsh .geo file
    Return: list of nodes 
    """
    # start and end tags indicating the start of text block to be read
    tagged_nodes_dict = {}
    for physical_tag in physical_tags:
        start_string = "Start_tag:" + physical_tag
        end_string = "End_tag:" + physical_tag
        lines = read_blocks(fpath, start_string, end_string)
        fnodes = []
        for line in lines:
            vals = line.strip(",\n").split(",")
            fnodes += [int(val.strip()) for val in vals]
        tagged_nodes_dict[physical_tag] = fnodes

    return tagged_nodes_dict


def create_nodes(nodes, ndm=2):
    """Create nodes
    nodes: a dictionary of nodes {node_id: [x, y, x]} 
           datatypes {int: [float, float, float]}
    ndf: number of degree of dimensions
    """

    for node_id, xycrds in nodes.items():
        ops.node(node_id, *xycrds[:ndm])

    # the last node number created
    return ops.getNodeTags()[-1]


def fix_nodes(nodes, dofs):
    """Fix a list of nodes as per the list of dof
    nodes: a list of nodes [node1, node2 ...]
    dofs a list of dofs [ dof1, dof2 dof3.. ndodfs]
    Same dofs will be applied to all nodes"""
    for nd in nodes:
        ops.fix(nd, *dofs)
        print(f"Node: {nd}, fix: {dofs}")


def create_equaldofs(rnodetags, cnodetags, dofs):
    """Ensure that the cnodes have the same contraint as rnode for dofs
    rnodetags: list of node tags for reference node, if a single rnode then [rnode]
    cnodetags: list of node tags for which the dofs are to be constrained
    dofs: a list of lists of dofs e.g. [[1, 2], [1, 2,], ....] which is to be constrained in cnodes
    """

    # check to see if rnodetags and dofs are single element list then expand the list
    # to be equal to len(cnodetags)
    if len(rnodetags) == 1:
        rnodetags = rnodetags * len(cnodetags)

    if len([dofs]) == 1:
        dofs = [dofs] * len(cnodetags)

    # check if rnodetags/dofs and cnodetags are the same length
    if len(rnodetags) != len(cnodetags):
        raise ValueError(
            "create_equaldofs: List rnodetags and list cnodetags must be of same length"
        )

    if len(dofs) != len(cnodetags):
        raise ValueError(
            "create_equaldofs: List dofs and list cnodetags must be of same length"
        )
    # print(f"rnodetags: {rnodetags}, cnodetags: {cnodetags}, dofs: {dofs}")

    print("{0:>6}, {1:>6}, {2:10}".format("NodeR", "NodeC", "dofs"))
    for rnode, cnode, dof in zip(rnodetags, cnodetags, dofs):
        # print(f"rnode: {rnode}")
        # print(f"cnode: {cnode}")
        # print(f"dof: {dof}")
        ops.equalDOF(rnode, cnode, *dof)
        print(f"{rnode:6d}, {cnode:6d}, {dof}")


def sort_nodestags_coordinates(nodestags, nodes_dict):
    """Sort nodetags first based on x-coordinate and then based on y-coordinate.
    nodes_dict: a dictionary of node tags and list of associated coordinates
    {1: [x, y, z], 2: [x, y, z], ...}
    nodetags: a list of nodetags to sort
    Return: a list of sorted nodestags
    """

    return sorted(nodestags, key=lambda k: [nodes_dict[k][1], nodes_dict[k][0]])


def assign_boundary_condition(tagged_nodes_dict, nodes_dict):
    """Create boundary conditions
    tagged_nodes_dict: dictionary of node tags for different physical tags
                        {physical_tag: [list of nodetags]}
    Return
    """
    # fix bottom nodes in the y-direction
    basedofs = [0, 1]
    base_nodes = tagged_nodes_dict["Fix_010"]
    fix_nodes(base_nodes, basedofs)
    print(f"Done fixing boundary conditions for the base.")

    # enforce equal degree of freedom in the horizontal direction for all base nodes
    # in this case node 7 is the rnode and rest are cnodes
    print(f"EqualDOF for base nodes:")
    create_equaldofs([base_nodes[0]], base_nodes[1:], [1])

    # foundation: left boundary, equalDOF
    left_outer_found_nodes = tagged_nodes_dict["left_outer_foundation_boundary"]
    left_inner_found_nodes = tagged_nodes_dict["left_inner_foundation_boundary"]
    # remove the base nodes from the list of edge nodes
    rnodes = list(set(left_outer_found_nodes) - set(base_nodes))
    cnodes = list(set(left_inner_found_nodes) - set(base_nodes))
    # arrange the nodes in left to right and bottom to top order
    rnodes = sort_nodestags_coordinates(rnodes, nodes_dict)
    cnodes = sort_nodestags_coordinates(cnodes, nodes_dict)
    # for rnode, cnode in zip(rnodes, cnodes):
    #     print(rnode, cnode)
    create_equaldofs(rnodes, cnodes, [1, 2])
    print(f"Boundary condition: equalDOF for foundation left boundary created")

    # foundaiton: right boundary, equalDOF
    right_outer_found_nodes = tagged_nodes_dict["right_outer_foundation_boundary"]
    right_inner_found_nodes = tagged_nodes_dict["right_inner_foundation_boundary"]
    # remove the base nodes from the list of edge nodes
    rnodes = list(set(right_outer_found_nodes) - set(base_nodes))
    cnodes = list(set(right_inner_found_nodes) - set(base_nodes))
    # arrange the nodes in left to right and bottom to top order
    rnodes = sort_nodestags_coordinates(rnodes, nodes_dict)
    cnodes = sort_nodestags_coordinates(cnodes, nodes_dict)
    # for rnode, cnode in zip(rnodes, cnodes):
    #     print(rnode, cnode)
    create_equaldofs(rnodes, cnodes, [1, 2])
    print(f"Boundary condition: equalDOF for foundation right boundary created")

    # slope: left boundary, equalDOF
    left_outer_slope_nodes = tagged_nodes_dict["left_outer_slope_boundary"]
    left_inner_slope_nodes = tagged_nodes_dict["left_inner_slope_boundary"]
    # remove the base nodes from the list of edge nodes
    rnodes = list(set(left_outer_slope_nodes) - set(left_outer_found_nodes))
    cnodes = list(set(left_inner_slope_nodes) - set(left_inner_found_nodes))
    # arrange the nodes in left to right and bottom to top order
    rnodes = sort_nodestags_coordinates(rnodes, nodes_dict)
    cnodes = sort_nodestags_coordinates(cnodes, nodes_dict)
    # for rnode, cnode in zip(rnodes, cnodes):
    #     print(rnode, cnode)
    create_equaldofs(rnodes, cnodes, [1, 2])
    print(f"Boundary condition: equalDOF for slope left boundary created")


def create_zerolength_dashpot_nodes(nodetag, nodes_dict):
    """Create dashpot nodes
    nodetag: node to which the dashpot is to be attached
    nodes_dict: dictionary of note tags and nodal coordinates
                {nodetag: [x, y, z]}
    tagged_nodes_dict: dictionary of physical tags and list of nodetags beloging
                       to the physical tag {physical_tag: [nodetag, ..]} 
    
    """
    # get the xy coordinates of the node to which the dashpot is to be attached
    xycoord = nodes_dict[nodetag]

    # get the last node and element numbers used
    ntags = ops.getNodeTags()[-1]

    dp_node1 = ntags + 1
    dp_node2 = ntags + 2

    # create two nodes at the specified point for zerolength dashpot element
    ops.node(dp_node1, xycoord[0], xycoord[1])
    ops.node(dp_node2, xycoord[0], xycoord[1])

    # fix the dashpot
    ops.fix(dp_node1, 1, 1)
    ops.fix(dp_node2, 0, 1)

    # equal DOF for dashpot and application point
    ops.equalDOF(nodetag, dp_node2, *[1])

    print(f"Dashpot nodes created: Fixed node: {dp_node1}, equalDOF node: {dp_node2}")
    print(f"Dasthpot equalDOF nodes: rnode={nodetag}, cnode={dp_node2}, equalDOF: {1}")
    # the first one is fixed node and the second one is equalDOF
    return [dp_node1, dp_node2]


def read_nyieldsurf(fpath, nyldsurf, start_nsurftag, end_nsurftag):
    """Read Shear strain  and shear stress values from the material input file"""

    nyieldsurflines = read_blocks(fpath, start_nsurftag, end_nsurftag)
    # drop the first line of header
    nyieldsurflines = nyieldsurflines[1:]
    nyldsurf_data = []
    for line in nyieldsurflines:
        line = line.strip(",\n").split(",")
        line = [float(val) for val in line]
        nyldsurf_data += [line[0], line[1]]
        # check if correct number of lines were read
    if len(nyldsurf_data) != (2 * abs(nyldsurf)):
        print(
            "WARNING: The number of yield surface points returned is less than that specified"
        )
    return nyldsurf_data


def read_ndmaterial_pressureindependent(fpath):
    """Read material parameters for nDmaterial """
    start_matprop = "start_ndmaterial:"
    end_matprop = "end_ndmaterial:"
    datatypes = [str] * 2 + [int] * 2 + [float] * 8 + [int]
    dkeys = [
        "mattype",
        "mattag",
        "nd",
        "rho",
        "refshear",
        "refbulk",
        "cohesion",
        "peak_shear_strain",
        "friction_angle",
        "refpressure",
        "pressure_coeff",
        "nyieldsurf",
        "yieldsurf",
    ]
    # discard the first header line
    lines = read_blocks(fpath, start_matprop, end_matprop)[1:]

    matprop_dict = {}
    mattag_dict = {}
    nsurf_dict = {}
    for line in lines:
        vals = line.strip(",\n").split(",")
        # parse values with correct datatype
        pvals = [datatype(val) for val, datatype in zip(vals, datatypes)]
        physical_tag = pvals[0]
        mattag = pvals[2]
        mattag_dict.update({physical_tag: mattag})
        dkv = dict(zip(dkeys, pvals[1:]))
        matprop_dict.update({physical_tag: dkv})
        nyldsurf = pvals[-1]
        customsurf = []
        if nyldsurf < 0:
            start_nyldsurftag = "start_nyldsurf:" + physical_tag
            end_nyldsurftag = "end_nyldsurf:" + physical_tag
            nyldsurf_data = read_nyieldsurf(
                fpath, nyldsurf, start_nyldsurftag, end_nyldsurftag
            )
            nsurf_dict.update({physical_tag: nyldsurf_data})
        else:
            nsurf_dict.update({})
    print(f"Number of materials: {len(mattag_dict)}")
    return mattag_dict, matprop_dict, nsurf_dict


def create_ndmat(matprop_dict, nsurf_dict):
    """Create material for Pressure Independent MultiYield ndMaterial"""
    for phytag, matprop in matprop_dict.items():
        prop = list(matprop.values())
        # the ndyield surface points code is not yet tested
        if nsurf_dict and matprop["nyieldsurf"] < 0:
            nsurfpts = nsurf_dict[phytag]
            prop += nsurfpts
        ops.nDMaterial(*prop)
    print(f"Created materials: {len(matprop_dict)}")


def create_elements(elements, eleprop, mattag_dict):
    """Create elements from the 4 node quad elements"""
    for element_id, v in elements.items():
        # print(element_id, v["nodes"])
        if "Periodic" in v["physical_tag"]:
            # print(element_id, "Periodic")
            eleprop["thickness"] = 10000.0
        else:
            eleprop["thickness"] = 1.0

        if "Slope" in v["physical_tag"]:
            eleprop["material_tag"] = mattag_dict["Slope"]
        elif "Foundation" in v["physical_tag"]:
            eleprop["material_tag"] = mattag_dict["Foundation"]
        else:
            print(f"ERROR: Unknown material")
            eleprop["material_tag"] = "Unknown"

        ops.element(
            eleprop["element_type"],
            element_id,
            *v["nodes"],
            eleprop["thickness"],
            eleprop["analysis_type"],
            eleprop["material_tag"],
            eleprop["surface_pressure"],
            eleprop["density"],
            eleprop["b1"],
            eleprop["b2"],
        )
    print(f"Element created: {ops.getEleTags()[-1]}")
    # return the tag of the last element created
    return ops.getEleTags()[-1]


def lysmer_dashpot_element(dashpot_element_tag, dashpot_nodes, dashpot_matparam):
    """Create Lysmer dashpot
    dashpot_element_tag: tag for the dashpot element
    dashpot_nodes: node of the soil to which the dashpot is attached
    dashpot_matparam: dict of parameters for the dashpot material 
    """

    # material for the dashpot material
    ops.uniaxialMaterial(
        "Viscous",
        dashpot_matparam["mattag"],
        dashpot_matparam["dashpot_c"],
        dashpot_matparam["dashpot_alpha"],
    )

    # define dashpot material
    ops.element(
        "zeroLength",
        dashpot_element_tag,
        *dashpot_nodes,
        "-mat",
        dashpot_matparam["mattag"],
        "-dir",
        *[1],
    )

    print(f"Dashpot created:")
    print(
        f"Element number: {dashpot_element_tag}, dashpot node numbers: {dashpot_nodes}, dashpot material tag: {dashpot_matparam['mattag']}"
    )


# def get_tagged_nodes(fpath, physical_tag):
#     """Get nodes from the tag file
#     fpath: path to the tag file, where the boundary conditions are written
#     physical_tag: physical tag for nodes in Gmsh .geo file
#     Return: list of nodes
#     """
#     # start and end tags indicating the start of text block to be read
#     start_string = "Start_tag:" + physical_tag
#     end_string = "End_tag:" + physical_tag
#     lines = read_blocks(fpath, start_string, end_string)
#     fnodes = []
#     for line in lines:
#         vals = line.strip(",\n").split(",")
#         fnodes += [int(val.strip()) for val in vals]
#     return fnodes


def update_material_stage(mattags, stage=0):
    """Update material stage"""
    for mattag in mattags:
        ops.updateMaterialStage("-material", int(mattag), "-stage", stage)


def data_recorders(fpath, fname_prefix, node_range, element_range, dt):
    """Create recorders for displacements, velocity and accelerations at the nodes, and
    stress and strains at the Gauss points of the elements"""

    # fmt: off
    # recorders for nodal displacements, velocity and acceleration at each time step
    restypes = ["disp", "vel", "accel"]
    for restype in restypes:
        fname = fname_prefix + "_" + restype + ".out"
        print(f"Filename: {fname}")
        fout = str(fpath.joinpath(fname))
        ops.recorder(
        "Node",
        "-file", fout,
        "-time",
        "-dT", dt,
        "-nodeRange", node_range[0], node_range[1],
        "-dof", *[1, 2],
        restype,
    )

    # ref: http://opensees.berkeley.edu/wiki/index.php/PressureIndependMultiYield_Material
    # For 2D problems, the stress output follows this order: σxx, σyy, σzz, σxy, ηr, where ηr 
    # is the ratio between the shear (deviatoric) stress and peak shear strength at the current
    # confinement (0<=ηr<=1.0). The strain output follows this order: εxx, εyy, γxy.
    # stresses and strains at each Gauss point in the soil elements
    gausspoints = ["1", "2", "3", "4"]
    var = ["stress", "strain"]
    # tuples of combination of var and gausspoints
    combs = product(var, gausspoints)
    for comb in combs:
        fname = fname_prefix + "_" + comb[0] + comb[1] + ".out"
        print(f"Created recorder and filename: {fname}")
        fout = str(fpath.joinpath(fname))
        ops.recorder(
            "Element",
            "-file", fout,
            "-time",
            "-dT", dt,
            "-eleRange", element_range[0], element_range[1],
            # "material", gpt,
            "material", comb[1],
            "stress",
        )
    # fmt: on


# def create_model(fid_dict, eleprop):
#     """Create model with nodes and elements"""

#     # the number of nodes created
#     print(f"Number of nodes created: {len(ops.getNodeTags())}")
#     # number of nodes created
#     print(f"Number of nodes in the mesh: {len(nodes.keys())}")

#     tagged_boundary_nodes = {}
#     for physical_tag in physical_tags:
#         tagged_boundary_nodes.update(
#             {physical_tag: get_tagged_nodes(fid_dict["tags"], physical_tag)}
#         )
#     # for k, v in lateral_boundary_nodes.items():
#     #     print(k, v)
#     # check the order of nodes in the list to see if they are at the same location
#     # for this particular case has to order the nodes in left_outer_foundation_boundary
#     # in ascending order
#     tagged_boundary_nodes = nodetags_b2t_and_l2r(nodes, tagged_boundary_nodes)
#     # print(tagged_boundary_nodes)
#     # boundary conditions for the base nodes, 0 = do not fix, 1 = fix
#     # fix means displacement = 0
#     print(f"Fixing boundary conditions for the base:")
#     basedofs = [0, 1]
#     base_nodes = tagged_boundary_nodes["Fix_010"]
#     # print(f"Fix base nodes:")
#     fix_nodes_bound(base_nodes, basedofs)
#     print(f"Done fixing boundary conditions for the base.")

#     # enforce equal degree of freedom in the horizontal direction for all base nodes
#     # in this case node 7 is the rnode and rest are cnodes
#     print(f"EqualDOF for base nodes:")
#     create_equaldofs([base_nodes[0]], base_nodes[1:], [1])

#     # enforce equal degree of freedom in the horizontal and vertical direction
#     # for rest of the lateral periodic boundaries in the slope and foundation region
#     # slope left boundary
#     rnodes = tagged_boundary_nodes["left_outer_slope_boundary"]
#     cnodes = tagged_boundary_nodes["left_inner_slope_boundary"]
#     # print(f"rnodes: {rnodes}, cnodes: {cnodes}")
#     # print(f"Length rnodes: {len(rnodes)}, Length cnodes: {len(cnodes)} ")
#     print(f"EqualDOF for slope left boundary:")
#     create_equaldofs(rnodes, cnodes, [1, 2])

#     # foundation left boundary, chaging set to list reorders the numbers
#     # in ascending order, so rnodes must be reversed to matching nodes in cnodes
#     # sets ensure that boundary conditions are set for a node only once
#     rnodes = list(
#         set(tagged_boundary_nodes["left_outer_foundation_boundary"])
#         - set(tagged_boundary_nodes["left_outer_slope_boundary"])
#         - set(tagged_boundary_nodes["Fix_110"])
#     )[::-1]
#     cnodes = list(
#         set(tagged_boundary_nodes["left_inner_foundation_boundary"])
#         - set(tagged_boundary_nodes["left_inner_slope_boundary"])
#         - set(tagged_boundary_nodes["Fix_110"])
#     )
#     # print(tagged_boundary_nodes["left_outer_foundation_boundary"])
#     # print(tagged_boundary_nodes["left_inner_foundation_boundary"])
#     # print(rnodes)
#     # print(cnodes)
#     print(f"EqualDOF for foundation left boundary:")
#     create_equaldofs(rnodes, cnodes, [1, 2])

#     # foundation right boundary, chaging set to list reorders the numbers
#     # in ascending order, so rnodes must be reversed to matching nodes in cnodes
#     rnodes = list(
#         set(tagged_boundary_nodes["right_outer_foundation_boundary"])
#         - set(tagged_boundary_nodes["Fix_110"])
#     )
#     cnodes = list(
#         set(tagged_boundary_nodes["right_inner_foundation_boundary"])
#         - set(tagged_boundary_nodes["Fix_110"])
#     )
#     # print(tagged_boundary_nodes["left_outer_foundation_boundary"])
#     # print(tagged_boundary_nodes["left_inner_foundation_boundary"])
#     # print(rnodes)
#     # print(cnodes)
#     print(f"EqualDOF for foundation right boundary:")
#     create_equaldofs(rnodes, cnodes, [1, 2])

#     # read ndmaterial parameters from external file
#     print(f"Reading material parameters from {fid_dict['matfile']}")
#     mattag_dict, matprop_dict, nsurf_dict = read_ndmaterial_pressureindependent(
#         fid_dict["matfile"]
#     )
#     # print(mattag_dict, matprop_dict, nsurf_dict)

#     # create material
#     print(f"Creating materials:")
#     create_ndmat_pimy(matprop_dict, nsurf_dict)
#     for k, v in mattag_dict.items():
#         print(f"Material: {k}, Material tag: {v}")

#     # create elements
#     print(f"Creating elements:")
#     number_of_elements = create_elements(elements, eleprop, mattag_dict)

#     print(f"Creating dashpot:")
#     # create lysmer dashpot
#     # apply motion at node 7: (0, -20) Use the _nodes and _tags files
#     equaldof_node = 7
#     dp_xycoord = (0.0, -20.0)
#     # the thickness of boundary elements on the left and the right is 10000.0
#     # other element are PlainStrain elements with thickness 1.0
#     base_area = (10 - 0) * 10000 + (72 - 10) * 1.0 + (82 - 72) * 10000.0
#     # dashpot coefficient = rock density * rock shear wave velocity
#     dashpot_coef = 1750.0
#     dashpot_c = base_area * dashpot_coef
#     dashpot_alpha = 1.0
#     print(
#         f"Base area: {base_area:.1f}, dashpot coef: {dashpot_coef:.1f}, damping coeff: {dashpot_c:.2f}"
#     )
#     dashpot_matparm = {
#         "mattag": 3,
#         "dashpot_c": dashpot_c,
#         "dashpot_alpha": dashpot_alpha,
#     }

#     lysmer_dashpot(dp_xycoord, equaldof_node, dashpot_matparm)
#     return mattag_dict, number_of_nodes, number_of_elements, dashpot_c, dashpot_alpha


def gravity_analysis(soil_mattags, tol, maxiter, newmark_gamma, newmark_beta):
    """Perform elastic and plastic gravity loading
    mattag_dict: dictonary of material for """
    # gravity analysis
    # update materials to ensure elastic behavior, stage=0

    update_material_stage(soil_mattags, 0)

    start_time = time.perf_counter()
    # gravity loading
    ops.constraints("Penalty", 1.0e18, 1.0e18)
    ops.test("NormDispIncr", tol, maxiter, 2)
    ops.algorithm("Newton")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", newmark_gamma, newmark_beta)
    ops.analysis("Transient")
    ops.analyze(10, 500.0)
    # ops.analyze(10, 5.0e3)
    print(f"Elastic gravity analysis over")

    # update material stage to include plastic analysis
    update_material_stage(soil_mattags, 1)
    ops.analyze(40, 500.0)
    end_time = time.perf_counter()
    analysis_time = end_time - start_time
    print("Plastic gravity analysis over")
    return analysis_time


def dynamic_load_pattern(fvel, gm_dt, cfactor, ts_tag, ldpat_tag, nodeq_tag):
    """Create dynamic load to apply
    fvel: path object to the velocity time series file
    gm_dt: time step of the ground motion
    cfactor: scaling factor for the ground motion
    ts_tag: load timeseries tag
    ldpat_tag: loadpattern tag
    nodeq_tag: node at which the excitation is applied """
    load_dir = [1, 0]
    fvel = str(fvel)
    print(f"Ground motion file: {fvel}, dt: {gm_dt}, cfactor: {cfactor}")
    # define constant factor for applied velocity, find out how this comes about?
    # this is what I found, the link might not work the next time
    # http://www.bgu.ac.il/geol/hatzor/articles/Bao_Hatzor_Huang_2012.pdf
    ops.timeSeries("Path", ts_tag, "-dt", gm_dt, "-filePath", fvel, "-factor", cfactor)
    ops.pattern("Plain", ldpat_tag, ts_tag)
    ops.load(nodeq_tag, *load_dir)
    print(f"Load pattern: {ldpat_tag}, with time series: {ts_tag} from file: {fvel}")


def dynamic_analysis(
    gm_dt,
    gm_nsteps,
    tol,
    maxiter,
    vs_max,
    element_size,
    newmark_gamma,
    newmark_beta,
    alpham,
    betak,
    betakinit,
    betakcomm,
):
    # determine the analysis time  step using CFL condition
    # CFL stands for Courant-Friedrichs-Levy
    # ref: http://web.mit.edu/16.90/BackUp/www/pdfs/Chapter14.pdf
    # duration of groundmotion [s]
    duration = gm_dt * gm_nsteps

    # trial analysis for time step
    ktrial = element_size / np.sqrt(vs_max)
    if gm_dt > ktrial:
        nsteps = int(floor(duration / ktrial) + 1)
        dt = duration / nsteps
    else:
        nsteps = gm_nsteps
        dt = gm_dt
    print(f"Number of steps: {nsteps}, time step, dt: {dt}")

    start_time = time.perf_counter()
    # equake loading
    ops.constraints("Penalty", 1.0e20, 1.0e20)
    ops.test("NormDispIncr", tol, maxiter, 2)
    ops.algorithm("Newton")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", newmark_gamma, newmark_beta)
    ops.rayleigh(alpham, betak, betakinit, betakcomm)
    ops.analysis("Transient")
    res = ops.analyze(nsteps, dt)

    # reduce timestep if fail to converge
    # maximum number of times to reduce the timestep
    maxiter = 2
    while res < 0 and niter < maxiter:
        print(f"WARNING: Dynamic analysis did not converge, reducing timestep")
        current_time = ops.getTime()
        current_step = current_time / dt
        print(
            f"iter: {niter}, current time: {current_time}, current step: {current_step}"
        )
        # when reducing the dt increase nsteps by the same factor
        nsteps = int((nsteps - current_step) * 2)
        dt = dt / 2.0
        print(f"Revised nsteps: {revised_nsteps}, revised dt: {dt}")
        nsteps = revised
        res = ops.analyze(nsteps, dt)
    end_time = time.perf_counter()
    analysis_time = end_time - start_time
    return analysis_time


# def analysis(
#     fid_dict,
#     datafile_dict,
#     number_of_nodes,
#     number_of_elements,
#     dashpot_c,
#     dashpot_alpha,
#     mattag_dict,
# ):
#     """Analysis steps preceeding with elastic and plastic gravity loading"""

#     # Ground motion paramters
#     # time step in ground motion record [s]
#     gm_dt = 0.005
#     # number of steps in ground motion record, the data beyond 15 s is useless
#     gm_nsteps = 3000

#     # rayleigh damping parameters (read on this)
#     damping_ratio = 0.02
#     # lower frequency [Hz]
#     f_lower = 0.2
#     omega_lower = 2 * np.pi * f_lower
#     # upper frequency [Hz]
#     f_upper = 20.0
#     omega_upper = 2 * np.pi * f_upper
#     # rayleigh damping coefficients
#     alpham = 2 * damping_ratio * omega_lower * omega_upper / (omega_lower + omega_upper)
#     betak = 2 * damping_ratio / (omega_lower + omega_upper)
#     betakinit = 0.0
#     betakcomm = 0.0
#     print(f"Damping coefficients: alpham = {alpham:6.3f}, betak = {betak:6.5f}")

#     # Newmark parameters
#     newmark_gamma = 0.5
#     newmark_beta = 0.25

#     # determine stable analysis time step using CFL condition
#     # maximum shear wave velocity [m/s]
#     vs_max = 250.0
#     # biggest element size [m]
#     element_size = 1.0

#     print(f"Newmark: gamma: {newmark_gamma}, beta: {newmark_beta}")
#     print(
#         f"Rayleigh: alpham: {alpham}, betak: {betak}, betakinit: {betakinit}, betakcomm: {betakcomm}"
#     )

#     # gravity analysis
#     # update materials to ensure elastic behavior, stage=0
#     soil_mattags = list(mattag_dict.values())
#     update_material_stage(soil_mattags, 0)

#     start_time = time.perf_counter()
#     # gravity loading
#     ops.constraints("Penalty", 1.0e18, 1.0e18)
#     ops.test("NormDispIncr", 1e-3, 35, 2)
#     ops.algorithm("Newton")
#     ops.numberer("RCM")
#     ops.system("ProfileSPD")
#     ops.integrator("Newmark", newmark_gamma, newmark_beta)
#     ops.analysis("Transient")
#     ops.analyze(10, 500.0)
#     # ops.analyze(10, 5.0e3)
#     print(f"Elastic gravity analysis over")

#     # update material stage to include plastic analysis
#     update_material_stage(soil_mattags, 1)
#     ops.analyze(40, 500.0)
#     end_time = time.perf_counter()
#     analysis_time = end_time - start_time
#     print("Plastic gravity analysis over")

#     print(f"Create data recorders")
#     # specify the node and element at which the acceleration, velocity, displacement,
#     # stress and strain time histories are required, for surface node

#     print(f"Finished creating data recorders")

#     # destory previous analysis object and start consolidation
#     print(
#         f"Wiping gravity analysis, resetting time to 0.0, and starting dynamic analysis:"
#     )
#     ops.wipeAnalysis()
#     ops.setTime(0.0)

#     # define constant factor for applied velocity, find out how this comes about?
#     # this is what I found, the link might not work the next time
#     # http://www.bgu.ac.il/geol/hatzor/articles/Bao_Hatzor_Huang_2012.pdf
#     cfactor = dashpot_c

#     fvel = str(fid_dict["velocityfile"])
#     # load pattern and timeseries for applied force history
#     print(f"Ground motion file: {fvel}, dt: {gm_dt}, cfactor: {cfactor}")

#     # load timeseries tag
#     tstag_eq = 1
#     # load pattern tag
#     pattag_eq = 1
#     # node at which the excitation is applied
#     nodetag_eq = 1
#     loadvals = [1.0, 0.0]
#     ops.timeSeries(
#         "Path", tstag_eq, "-dt", gm_dt, "-filePath", fvel, "-factor", cfactor
#     )
#     ops.pattern("Plain", pattag_eq, tstag_eq)
#     ops.load(nodetag_eq, *loadvals)

#     # determine the analysis time  step using CFL condition
#     # CFL stands for Courant-Friedrichs-Levy
#     # ref: http://web.mit.edu/16.90/BackUp/www/pdfs/Chapter14.pdf
#     # duration of groundmotion [s]
#     duration = gm_dt * gm_nsteps

#     # trial analysis for time step
#     ktrial = element_size / np.sqrt(vs_max)
#     if gm_dt > ktrial:
#         nsteps = int(floor(duration / ktrial) + 1)
#         dt = duration / nsteps
#     else:
#         nsteps = gm_nsteps
#         dt = gm_dt

#     print(f"Number of steps: {nsteps}, time step, dt: {dt}")

#     start_time = time.perf_counter()
#     # equake loading
#     ops.constraints("Penalty", 1.0e20, 1.0e20)
#     ops.test("NormDispIncr", 1e-3, 35, 2)
#     ops.algorithm("Newton")
#     ops.numberer("RCM")
#     ops.system("ProfileSPD")
#     ops.integrator("Newmark", newmark_gamma, newmark_beta)
#     ops.rayleigh(alpham, betak, betakinit, betakcomm)
#     ops.analysis("Transient")
#     res = ops.analyze(nsteps, dt)

#     # reduce timestep if fail to converge
#     # maximum number of times to reduce the timestep
#     maxiter = 2
#     while res < 0 and niter < maxiter:
#         print(f"WARNING: Dynamic analysis did not converge, reducing timestep")
#         current_time = ops.getTime()
#         current_step = current_time / dt
#         print(
#             f"iter: {niter}, current time: {current_time}, current step: {current_step}"
#         )
#         # when reducing the dt increase nsteps by the same factor
#         nsteps = int((nsteps - current_step) * 2)
#         dt = dt / 2.0
#         print(f"Revised nsteps: {revised_nsteps}, revised dt: {dt}")
#         nsteps = revised
#         res = ops.analyze(nsteps, dt)
#     end_time = time.perf_counter()
#     analysis_time = end_time - start_time
#     print(
#         f"Time: gravity loading {gravity_time:.4f}, dynamic analysis: {dynamic_time: .4f}, total: {gravity_time + dynamic_time:.4f} s"
#     )


def main():
    # file path and filenames
    path_root = Path(r"../")
    path_data = path_root / "data"
    path_msh = path_root / "gmsh"
    path_pvd = path_root / "pvd"

    # name of the nodes file
    fname_nodes = "2d_dynamicslopeanalysis_ex1_gmsh_nodes.txt"
    fnodes = path_msh.joinpath(fname_nodes)
    # name of the elements file
    fname_elements = "2d_dynamicslopeanalysis_ex1_gmsh_elements.txt"
    felements = path_msh.joinpath(fname_elements)
    # name of the files with fixities written
    fname_tags = "2d_dynamicslopeanalysis_ex1_gmsh_tags.txt"
    ftags = path_msh.joinpath(fname_tags)
    # name of the material parameters file
    fname_matfile = "ndmat_multiyield_pressureindependent.csv"
    fmatfile = path_data.joinpath(fname_matfile)
    # velocity file
    fname_vel = "velocityHistory.out"
    fvel = path_data.joinpath(fname_vel)

    # dictionary of fids relating to various files that is either read or written
    fid_dict = {
        "nodes": fnodes,
        "elements": felements,
        "tags": ftags,
        "matfile": fmatfile,
        "velocityfile": fvel,
    }

    # the output data is written in ../data folder
    # a common name for all data files
    fname_prefix = "2ddex1"
    # data file dict with the path and the filename prefix
    datafile_dict = {"path": path_data, "prefix": fname_prefix}

    # tagged nodes for boundaries
    physical_tags = [
        "Fix_010",
        "left_outer_slope_boundary",
        "left_inner_slope_boundary",
        "left_outer_foundation_boundary",
        "left_inner_foundation_boundary",
        "right_outer_foundation_boundary",
        "right_inner_foundation_boundary",
    ]

    # acceleration due to gravity [m/s2]
    accg = 9.81
    # soil saturated density, or soil mass density  [Mg/m3] equivalent [1 Mg/m3 = 10 kN/m3]
    soil_density = 1.7
    # acceleration due to gravity in the x and y direction
    wgt_x = 0.0
    wgt_y = -accg * soil_density

    # Ground motion paramters
    # time step in ground motion record [s]
    gm_dt = 0.005
    # number of steps in ground motion record, the data beyond 15 s is useless
    gm_nsteps = 3000

    # rayleigh damping parameters (read on this)
    damping_ratio = 0.02
    # lower frequency [Hz]
    f_lower = 0.2
    omega_lower = 2 * np.pi * f_lower
    # upper frequency [Hz]
    f_upper = 20.0
    omega_upper = 2 * np.pi * f_upper
    # rayleigh damping coefficients
    alpham = 2 * damping_ratio * omega_lower * omega_upper / (omega_lower + omega_upper)
    betak = 2 * damping_ratio / (omega_lower + omega_upper)
    betakinit = 0.0
    betakcomm = 0.0
    print(f"Damping coefficients: alpham = {alpham:6.3f}, betak = {betak:6.5f}")

    # Newmark parameters
    newmark_gamma = 0.5
    newmark_beta = 0.25

    # determine stable analysis time step using CFL condition
    # maximum shear wave velocity [m/s]
    vs_max = 250.0
    # biggest element size [m]
    element_size = 1.0

    print(f"Newmark: gamma: {newmark_gamma}, beta: {newmark_beta}")
    print(
        f"Rayleigh: alpham: {alpham}, betak: {betak}, betakinit: {betakinit}, betakcomm: {betakcomm}"
    )

    # element property dictionary
    eleprop = {
        "element_type": "quad",
        "thickness": 1.0,
        # analysis type, "PlaneStrain" or "PlaneStress"
        "analysis_type": "PlaneStrain",
        "material_tag": 0,
        "bulk_modulus": 0,
        "surface_pressure": 0.0,
        "density": 0.0,
        "b1": wgt_x,
        "b2": wgt_y,
    }

    # the thickness of boundary elements on the left and the right is 10000.0
    # other element are PlainStrain elements with thickness 1.0
    base_area = (10 - 0) * 10000 + (72 - 10) * 1.0 + (82 - 72) * 10000.0
    # dashpot coefficient = rock density * rock shear wave velocity
    dashpot_coef = 1750.0
    dashpot_c = base_area * dashpot_coef
    dashpot_alpha = 1.0
    print(
        f"Base area: {base_area:.1f}, dashpot coef: {dashpot_coef:.1f}, damping coeff: {dashpot_c:.2f}"
    )

    # dashpot material parameters, soils and foundation have mattags 1 and 2
    dashpot_matparam = {
        "mattag": 3,
        "dashpot_c": dashpot_c,
        "dashpot_alpha": dashpot_alpha,
    }

    # dictionary of ground motion parameters
    # read the nodes file
    nodes_dict = read_nodes(fid_dict["nodes"])
    elements_dict = read_elements(fid_dict["elements"], element_type="quad")
    tagged_nodes_dict = read_tagged_nodes(fid_dict["tags"], physical_tags)

    # wipe previous analysis
    ops.wipe()
    # corner nodes are 2D with 2 DOF (displacements in x1 and x2)
    ops.model("basic", "-ndm", 2, "-ndf", 2)

    # create model, the nodes
    number_of_nodes = create_nodes(nodes_dict, ndm=2)

    # boundary conditions for the nodes
    # the base is fixed in the y-dir and the left and right nodes are equalDOF,
    # modify create_boundary function to address specific requirements
    assign_boundary_condition(tagged_nodes_dict, nodes_dict)

    # create nodes for zerolength dashpot
    attachdp = 7
    # the first node is fixed and the second is the equalDOF node
    dashpot_nodes = create_zerolength_dashpot_nodes(attachdp, nodes_dict)
    tagged_nodes_dict.update({"dashpot": dashpot_nodes})
    # for k, v in tagged_nodes_dict.items():
    #     print(k, v)

    # read material properties from file
    mattag_dict, matprop_dict, nsurf_dict = read_ndmaterial_pressureindependent(
        fid_dict["matfile"]
    )
    # print(mattag_dict, matprop_dict, nsurf_dict)

    # create material
    create_ndmat(matprop_dict, nsurf_dict)

    # create foundation and slope elements including periodic
    number_of_elements = create_elements(elements_dict, eleprop, mattag_dict)

    # create dashpot element
    dashpot_element_tag = number_of_elements + 1
    lysmer_dashpot_element(dashpot_element_tag, dashpot_nodes, dashpot_matparam)

    # gravity analysis
    soil_mattags = [1, 2]
    tol = 1e-3
    maxiter = 35
    time_gravity = gravity_analysis(
        soil_mattags, tol, maxiter, newmark_gamma, newmark_beta
    )
    print(f"Time taken for gravity analysis: {time_gravity:6.3f} s")

    print(f"Create data recorders")
    dt = 2.0 * gm_dt
    node_range = [ops.getNodeTags()[0], ops.getNodeTags()[-1]]
    element_range = [ops.getEleTags()[0], ops.getEleTags()[-1]]
    print(node_range, element_range)
    data_recorders(
        datafile_dict["path"], datafile_dict["prefix"], node_range, element_range, dt,
    )

    # Wipe gravity analysis and reset time
    ops.wipeAnalysis()
    ops.setTime(0.0)

    # create load pattern for the earthquake motion and apply at node 7
    tstag_eq = 1
    pattag_eq = 1
    nodeq_tag = attachdp
    dynamic_load_pattern(
        fid_dict["velocityfile"], gm_dt, dashpot_c, tstag_eq, pattag_eq, nodeq_tag
    )

    # for dynamic analysis
    tol = 1.0e-3
    maxiter = 35

    time_dynamic = dynamic_analysis(
        gm_dt,
        gm_nsteps,
        tol,
        maxiter,
        vs_max,
        element_size,
        newmark_gamma,
        newmark_beta,
        alpham,
        betak,
        betakinit,
        betakcomm,
    )
    print(
        f"Time: gravity loading {time_gravity:.4f}, dynamic analysis: {time_dynamic: .4f}, total: {time_gravity + time_dynamic:.4f} s"
    )

    ops.wipe()


if __name__ == "__main__":
    main()
