#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import openseespy.opensees as ops
from pathlib import Path
from itertools import count, chain, repeat

# Example problem:
# Description: 1D consolidation
# Original solution by: Christopher McGann and Pedro Arduino, University of Washington
# ref: https://opensees.berkeley.edu/wiki/index.php/One-dimensional_Consolidation
# Units: kN, m, sec


def chunks(L, n):
    """Yield successive n-sized chunks from L.
    chunks("abcdefghi", 3) -> ['abc', 'def', 'ghi']
    chunks([1,2,3,4,5,6,7,8,9], 3) -> [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    for list output: list(chunks(L, n))
    ref: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    author: Ned Batchelder
    """
    for i in range(0, len(L), n):
        yield L[i : i + n]


def slicedict(dict, start, stop):
    """Slice dictionary from start to stop
    ref: https://stackoverflow.com/questions/29216889/slicing-a-dictionary
    author: kindall
    """
    if start > stop:
        raise ValueError("stop > start")
    keys = range(start, stop)
    return {k: dict[k] for k in keys}


def repeatlist(a, b):
    """Repeat each item in list a, number of times specified in another list b
    ref: https://stackoverflow.com/questions/33382474/repeat-each-item-in-a-list-a-number-of-times-specified-in-another-list
    authors: thefourtheye and ShadowRanger
    example: a = [2, 3, 4], b = [1, 2, 3]
    repeatlist(a, b) -> [2, 3, 3, 4, 4, 4]"""
    return list(chain.from_iterable(map(repeat, a, b)))


def fix_nodes(nodes, dofs):
    """Fix a list of nodes as per the list of dof
    fixed nodes dof = 1, displacements and pore pressures are fixed to 0
    dof = 0 not fixed, displacements and pore pressures can vary during simulation"""
    for nd in nodes:
        ops.fix(nd, *dofs)
        print(f"Node: {nd}, fix {dofs}")


# def gen_node_numbers():
#     start = 0
#     yield start + 1


def create_nodes(cxs, cys, start_node_number, xycoords):
    # print(f"Cxs: {cxs}")
    # print(f"Cys: {cys}")
    # create a itertools generator count
    gen_node_number = count(start_node_number)
    xv, yv = np.meshgrid(cxs, cys, indexing="ij")
    coord_grid = np.array([xv, yv])
    gshape = coord_grid.shape

    for y in range(gshape[2]):
        for x in range(gshape[1]):
            xc, yc = coord_grid[:, x, y]
            node_number = next(gen_node_number)
            print(f"Node number: {node_number}, xc: {xc}, yc: {yc}")
            ops.node(node_number, xc, yc)
            xycoords.update({node_number: (xc, yc)})
    return xycoords


def create_equaldofs(rnodetag, cnodetags, dofs):
    """Ensure that the cnodes have the same contraint as rnode for dofs"""
    print(f"EqualDOF fixity")
    for cnodetag in cnodetags:
        ops.equalDOF(rnodetag, cnodetag, *dofs)
        print(f"R node: {rnodetag}, cnode: {cnodetag}, dof: {dofs}")


def create_elements(
    soil_elements, hr_crnodes, hr_tbnodes, hr_lrnodes, hr_cnnodes, eprop
):
    thick = eprop["thickness"]
    mattag = eprop["material_tag"]
    modK = eprop["bulk_modulus"]
    waterdensity = eprop["water_density"]
    k_hor = eprop["horizontal_permeability"]
    k_ver = eprop["vertical_permeability"]
    accg_x = eprop["g_xdir"]
    accg_y = eprop["g_ydir"]
    nx = len(hr_cnnodes[0])
    gen_element_numbers = count(1)

    rlist = [1] + [2] * (nx - 1) + [1]
    for bcrns, tcrns, btbns, ttbns, lrns, cnns in zip(
        hr_crnodes[0:-1],
        hr_crnodes[1:],
        hr_tbnodes[0:-1],
        hr_tbnodes[1:],
        hr_lrnodes,
        hr_cnnodes,
    ):
        bcrns = list(chunks(repeatlist(bcrns, rlist), 2))
        tcrns = list(chunks(repeatlist(tcrns, rlist), 2))
        lrns = list(chunks(repeatlist(lrns, rlist), 2))

        for bcrn, tcrn, btbn, ttbn, lrn, cnn in zip(
            bcrns, tcrns, btbns, ttbns, lrns, cnns
        ):
            elen = next(gen_element_numbers)
            # print(bcrn, tcrn, btbn, ttbn, lrn, cnn)
            elnodes = [
                bcrn[0],
                bcrn[1],
                tcrn[1],
                tcrn[0],
                btbn,
                lrn[1],
                ttbn,
                lrn[0],
                cnn,
            ]
            soil_elements.update({elen: elnodes})

            ops.element(
                "9_4_QuadUP",
                elen,
                *elnodes,
                thick,
                mattag,
                modK,
                waterdensity,
                k_hor,
                k_ver,
                accg_x,
                accg_y,
            )

    return soil_elements


def data_recorders(fnames, total_number_nodes, total_number_elements):
    # fmt: off
    fdisp = fnames["fdisp"]
    fpp = fnames["fpp"]
    fstress = fnames["fstress"]
    fstrain = fnames["fstrain"]
    
    # recorders for nodal displacements, porewater pressure and acceleration
    ops.recorder(
        "Node",
        "-file", fdisp,
        "-time",
        "-node", 33,
        "-dof", *[1, 2],
        "disp",
    )

    ops.recorder(
        "Node",
        "-file", fpp, 
        "-time", 
        "-nodeRange", 1, total_number_nodes,
        "-dof", 3,
        "vel")
    
    # ref: http://opensees.berkeley.edu/wiki/index.php/PressureIndependMultiYield_Material
    # For 2D problems, the stress output follows this order: σxx, σyy, σzz, σxy, ηr, where ηr 
    # is the ratio between the shear (deviatoric) stress and peak shear strength at the current
    # confinement (0<=ηr<=1.0). The strain output follows this order: εxx, εyy, γxy.
    ops.recorder(
        "Element",
        "-file", fstress,
        "-time",
        "-eleRange", 1, total_number_elements,
        "material", "9", "stress",
    )
    
    ops.recorder(
        "Element",
        "-file", fstrain,
        "-time",
        "-eleRange", 1, total_number_elements,
        "material", "9", "strain",
    )
    # fmt: on


def main():
    # file path and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"

    # drainage condition: "single" or "double"
    drainage = "single"

    fname_disp = "1dcon_disp_" + drainage + "drainage.txt"
    fname_pp = "1dcon_porepressure_" + drainage + "drainage.txt"
    fname_stress = "1dcon_stress_" + drainage + "drainage.txt"
    fname_strain = "1dcon_strain_" + drainage + "drainage.txt"

    fdisp = str(path_data.joinpath(fname_disp))
    fpp = str(path_data.joinpath(fname_pp))
    fstrain = str(path_data.joinpath(fname_strain))
    fstress = str(path_data.joinpath(fname_stress))
    fpaths = {"fdisp": fdisp, "fpp": fpp, "fstress": fstress, "fstrain": fstrain}

    # center offset from the bottom left of the page (origin of the page, origin transformed)
    ox = 0.0
    oy = 0.0

    # size of elements in x and y direction of the nodes
    lx = 1.0
    ly = 1.0

    # number of element in x and y direction
    nx = 1
    ny = 10

    # acceleration due to gravity [m/s2]
    accg = 9.81

    # density of water [Mg/m3]
    waterdensity = 1.0

    # material properties
    # soil saturated density [Mg/m3]
    satdensity = 2.3
    # shear, bulk and undrained bulk modulii [kPa]
    modG = 2.5e4
    modK = 6.2e5
    modKu = 2.2e5
    # vertical and horizontal permeability [m/s]
    kh = 5e-5
    kv = 5e-5
    # permeability used in the material model
    k_hor = kh / (accg * waterdensity)
    k_ver = kv / (accg * waterdensity)
    # Mohr-Column material properties c-intercept [kPa] and friction angle (deg)
    cohesion = 45.0
    friction_angle = 0.0
    # peak shear strain
    peak_shear_strain = 0.10
    # reference pressure
    reference_pressure = 80.0
    # pressure dependency coefficient
    pressure_dependence = 0.0
    # number of yield surface
    nsurf = 22

    # soil element thickness
    thickness = 1.0
    # acceleration due to gravity in the x and y direction
    accg_x = 0.0
    accg_y = -accg

    # Newmark parameters
    newmark_gamma = 0.5
    newmark_beta = 0.25

    # rayleigh damping
    alpham = 0.5
    betak = 0.2
    betakinit = 0.0
    betakcomm = 0.0

    # overburden stress one the surface [kN/m2]
    overburden = -1000.0

    # start node number
    start_node_number = 1

    # ending node numbers for different node "types"
    # the node types are:
    # corner nodes, crnodes: the nodes at the corners of the elements
    # top bottom nodes, tbnodes: the nodes that are in between the corner nodes
    #                          at the top and bottom (horizontal) of the elements
    # left right nodes, lrnodes: the nodes that are in between the corner nodes
    #                          at the left and right (vertical) of the elements
    # center nodes, cnnodes: nodes that are at the centers of elements
    cr_last_node_number = (nx + 1) * (ny + 1)
    tb_last_node_number = cr_last_node_number + nx * (ny + 1)
    lr_last_node_number = tb_last_node_number + (nx + 1) * ny
    total_number_nodes = lr_last_node_number + nx * ny

    # total number of elements
    total_number_elements = nx * ny

    # dictionary for node numbers and corresponding coordinates
    # {node_number: (x, y)}
    xycoords = {}

    # dictionary for elements and node numbers
    soil_elements = {}

    # wipe previous analyses
    ops.wipe()

    # corner nodes are 2D with 3 DOF
    ops.model("basic", "-ndm", 2, "-ndf", 3)

    # the corner coordinates are in increasing order of the nodes
    # with node number and (x, y) coordinates with origin at the bottom left
    # {1: (x1, y1), 2: (x2, y2), .....}
    # center for the corner nodes
    cxs = np.linspace(0, nx * lx, num=nx + 1) + ox
    cys = np.linspace(0, ny * ly, num=ny + 1) + oy
    xycoords = create_nodes(cxs, cys, start_node_number, xycoords)
    last_node_number = (nx + 1) * (ny + 1)
    print(f"Corner nodes: 1 - {last_node_number}")
    # print the corner nodes
    # for key, values in xycoords.items():
    #     print(f"Node: {key}, (x, y): {values}")

    # corner nodes horizontally arranged
    hr_crnodes = list(chunks(list(xycoords.keys()), nx + 1))
    base_crnodes = hr_crnodes[0]
    # print(f"Base nodes: {base_crnodes}")
    vr_crnodes = list(zip(*hr_crnodes))
    # print(f"Corner nodes vertically arranges: {vr_crnodes}")
    # boundary conditions for the base nodes, depends on the drainage condition
    # if single drainage fix only the displacements (DOFs 1 and 2) and not the pore pressure DOF 3
    # if double drainage fix all the 3 DOFs
    if drainage == "single":
        dofs = [1, 1, 0]
    elif drainage == "double":
        dofs = [1, 1, 1]
    else:
        raise ValueError("Wrong drainge condition")

    fix_nodes(base_crnodes, dofs)

    # boundary conditions for the top nodes, fix horizontal displacement and porepressure
    surface_crnodes = hr_crnodes[-1]
    # print(f"Top nodes: {surface_crnodes}")
    fix_nodes(surface_crnodes, [1, 0, 1])

    # fix all remaining nodes in the horizontal direction dofs = [1, 0, 0]
    interior_nodes = chain.from_iterable(hr_crnodes[1:-1])
    # print(f"Interior nodes: {interior_nodes}")
    fix_nodes(interior_nodes, [1, 0, 0])

    # create the top, bottom, left, right and center nodes 2D with 2 DOFs
    ops.model("basic", "-ndm", 2, "-ndf", 2)

    # centers for nodes along the top and bottom edges of the element
    cxs = np.cumsum([lx / 2] + [lx] * (nx - 1)) + ox
    cys = np.cumsum([0] + [ly] * ny) + oy
    xycoords = create_nodes(cxs, cys, cr_last_node_number + 1, xycoords)
    print(
        f"Top and bottom edges nodes: {cr_last_node_number + 1} - {tb_last_node_number}"
    )
    tbnodes_dict = slicedict(xycoords, cr_last_node_number + 1, tb_last_node_number + 1)
    # print(f"Top and bottom edges nodes: {tbnodes_dict}")
    hr_tbnodes = list(chunks(list(tbnodes_dict.keys()), nx))
    # print(f"Top and bottom edges nodes: {hr_tbnodes}")
    base_tbnodes = hr_tbnodes[0]
    surface_tbnodes = hr_tbnodes[-1]
    # print(f"Base nodes: top and bottom edges nodes: {base_tbnodes}")
    # print(f"Surface nodes: top and bottom edges nodes: {surface_tbnodes}")

    # centers for nodes along the vertical edges of the elements
    cxs = np.cumsum([0] + [lx] * nx) + ox
    cys = np.cumsum([ly / 2] + [ly] * (ny - 1)) + oy
    xycoords = create_nodes(cxs, cys, tb_last_node_number + 1, xycoords)
    print(
        f"Left and right vertical edges nodes: {tb_last_node_number + 1} - {lr_last_node_number}"
    )
    # arrange the edges nodes in horizontal groups and then in vertical groups
    lrnodes_dict = slicedict(xycoords, tb_last_node_number + 1, lr_last_node_number + 1)
    # print(f"Vertial edges nodes dict: {lrnodes_dict}")
    hr_lrnodes = list(chunks(list(lrnodes_dict.keys()), nx + 1))
    # print(f"Vertical edges nodes horizontal groups: {hr_lrnodes}")
    vr_lrnodes = list(zip(*hr_lrnodes))
    # print(f"Vertical edges nodes column: {vr_lrnodes}")

    # centers for center nodes
    cxs = np.cumsum([lx / 2] + [lx] * (nx - 1)) + ox
    cys = np.cumsum([ly / 2] + [ly] * (ny - 1)) + oy
    xycoords = create_nodes(cxs, cys, lr_last_node_number + 1, xycoords)
    cnnodes_dict = slicedict(xycoords, lr_last_node_number + 1, total_number_nodes + 1)
    hr_cnnodes = list(chunks(list(cnnodes_dict.keys()), nx))
    print(f"Center nodes: {lr_last_node_number + 1} - {total_number_nodes}")
    print(f"Finished creating all soil nodes:")

    # boundary conditions:
    # fix the base nodes in the vertical and horizontal directions
    fix_nodes(base_tbnodes, [1, 1])
    # fix horizontal displacements of the nodes along the edges of the soil profile
    soil_profile_edges = vr_lrnodes[0] + vr_lrnodes[-1]
    # print(f"Soil profile edges nodes: {soil_profile_edges}")
    fix_nodes(soil_profile_edges, [1, 0])

    # equalDOF for surface nodes for horizontal and vertical displacements dofs = [1, 2]
    # one of the interior unfixed surface nodes must be the rnode
    create_equaldofs(surface_tbnodes[0], surface_tbnodes[1:] + surface_crnodes, [1, 2])

    print(f"Created all boundary conditions:")

    # define soil material
    mattag = 1
    # number of dimensions (nd) 2 for plain-strain 3 for 3D
    ops.nDMaterial(
        "PressureIndependMultiYield",
        mattag,
        2,
        satdensity,
        modG,
        modK,
        cohesion,
        peak_shear_strain,
        friction_angle,
        reference_pressure,
        pressure_dependence,
        nsurf,
    )
    print(f"Soil material created")

    eleprop = {
        "thickness": thickness,
        "material_tag": mattag,
        "bulk_modulus": modK,
        "water_density": waterdensity,
        "horizontal_permeability": k_hor,
        "vertical_permeability": k_ver,
        "g_xdir": accg_x,
        "g_ydir": accg_y,
    }
    soil_elements = create_elements(
        soil_elements, hr_crnodes, hr_tbnodes, hr_lrnodes, hr_cnnodes, eleprop
    )
    print(f"Soil elements:")
    print(
        "{0:5s}, {1:6s}, {2:6s}, {3:6s}, {4:6s}, {5:6s}, {6:6s}, {7:6s}, {8:6s}, {9:6s}".format(
            "Ele",
            "Node 1",
            "Node 2",
            "Node 3",
            "Node 4",
            "Node 5",
            "Node 6",
            "Node 7",
            "Node 8",
            "Node 9",
        )
    )
    for key, values in soil_elements.items():
        print(
            "{0:5d}, {1:6d}, {2:6d}, {3:6d}, {4:6d}, {5:6d}, {6:6d}, {7:6d}, {8:6d}, {9:6d}".format(
                key, *values
            )
        )

    print(f"All soil elements created")

    print(f"Gravity analysis:")
    # update material stage to 0 for elastic behavior
    ops.updateMaterialStage("-material", mattag, "-stage", 0)
    print(f"Material updated for elastic behavior during gravity loading")

    # gravity loading
    ops.constraints("Transformation")
    ops.test("NormDispIncr", 1e-5, 30, 5)
    ops.algorithm("Newton")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", newmark_gamma, newmark_beta)
    ops.analysis("Transient")
    ops.analyze(10, 500.0)
    print(f"Elastic gravity analysis over")

    # update material stage to include plastic analysis
    ops.updateMaterialStage("-material", mattag, "-stage", 1)
    ops.analyze(40, 500.0)
    print(f"Plastic gravity analysis over")

    print(f"Create data recorders")
    data_recorders(fpaths, total_number_nodes, total_number_elements)
    print(f"Finished creating data recorders")

    # define load for consolidation, permanent overburden on the surface interior node
    ldnode = surface_tbnodes[0]
    tstag = 1
    pattag = 1
    ops.timeSeries("Constant", tstag)
    ops.pattern("Plain", pattag, tstag)
    ops.load(ldnode, *[0.0, overburden])
    print(f"Surface overburden created")

    # destory previous analysis object and start consolidation
    print(
        f"Wiping gravity analysis, resetting time to 0.0, and starting consolidation:"
    )
    ops.wipeAnalysis()
    ops.setTime(0.0)
    ops.constraints("Penalty", 1.0e16, 1.0e16)
    ops.test("NormDispIncr", 1.0e-4, 30, 5)
    ops.algorithm("Newton")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", newmark_gamma, newmark_beta)
    ops.rayleigh(alpham, betak, betakinit, betakcomm)
    ops.analysis("Transient")
    ops.analyze(800, 0.25)
    print(f"Consolidation analysis over")

    ops.wipe()


if __name__ == "__main__":

    # basic_shapes("basic_shapes.svg")
    main()

