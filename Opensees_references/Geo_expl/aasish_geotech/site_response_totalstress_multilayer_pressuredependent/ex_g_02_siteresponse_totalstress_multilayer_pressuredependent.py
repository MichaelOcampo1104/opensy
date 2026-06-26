#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import pandas as pd
import openseespy.opensees as ops
from pathlib import Path
from itertools import count, chain, repeat, product

# Example problem:
# Description: 1D total stress site reponse analysis of multilayer pressure dependent multiyield soil
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


def roundup(num):
    """Check if a float is a whole number if not round up"""
    return int(num) if num.is_integer() else int(np.ceil(num))


def vrows_per_layer(lamda_min, fmax, layer_thickness, vs, nele_wave):
    """Determine the number of vertical elements in each layer"""
    htrial = lamda_min / nele_wave
    return roundup(layer_thickness / htrial)


def read_autogen_multiyield_pressure_dependent_properites_Vs(fpath, skiprows=2):
    """Read layer properties from a input ".csv" file. The elastic moduli are computed
    from Vs and nu. The multiple yield surface points are automatically generated based
    on the supplied number of multiyield surfaces values. This needs modification if
    additional parameters are required"""

    # fmt: off
    colnames = [ 
        "layer_num",
        "thickness",
        "vs", "nu", "density",
        "phi", "peakshearstrain",
        "refpressure", "pressurecoeff",
        "phasetrans_angle",
        "contraction_coeff",
        "dilation_param1", "dilation_param2",
        "liquefaction_param1", "liquefaction_param2", "liquefaction_param3",
        "nyieldsurfaces",
        "e0", "cs1", "cs2", "cs3", "pa",
        "c"
    ]
    # fmt: on
    print(f"Length of the column names: {len(colnames)}")
    # enforce these data types for each variable
    Float = lambda x: float(x)
    Integer = lambda x: int(x)
    converts = [
        Integer,
        Float,
        Float,
        Float,
        Float,
        Float,
        Float,
        Float,
        Float,
        Float,
        Float,
        Float,
        Float,
        Float,
        Float,
        Float,
        Integer,
        Float,
        Float,
        Float,
        Float,
        Float,
        Float,
    ]

    conversions = dict(zip(colnames, converts))
    # print(f"Conversions: {conversions}")
    # read the file using padas
    df = pd.read_csv(
        fpath,
        delimiter=",",
        names=colnames,
        skiprows=2,
        converters=conversions,
        engine="python",
    )
    print(f"Shape of the data: {df.values.shape}")

    df.loc[:, "modG"] = df.loc[:, "density"] * df.loc[:, "vs"] ** 2
    df.loc[:, "modE"] = 2 * df.loc[:, "modG"] * (1 + df.loc[:, "nu"])
    df.loc[:, "modK"] = df.loc[:, "modE"] / (3 * (1 - 2 * df.loc[:, "nu"]))
    column_headers = list(df.columns)
    data = df.to_records(index=False)
    layers = [dict(zip(column_headers, d)) for d in data][::-1]
    return layers


def number_of_layer_subdivisions(layers, fmax, nele_wave):
    """Compute element height and consequently the number of elements in each layer
    based on the smallest wavelength that needs to be resolved into a specified
    number of points."""

    # an array of shear wave velocities of different layers
    vs = np.array([layer["vs"] for layer in layers])

    # shear wave desired to be well resolved
    vs_min = np.min(vs)

    # wavelength of the highest resolved frequency [m]
    lamda_min = vs_min / fmax
    print(f"Shortest wave length: {lamda_min}, corresponding to {vs_min}")

    # determine and number of subdivisions (vertical elements) within each layer to layer properties
    for layer in layers:
        layer_thickness = layer["thickness"]
        eley_number = vrows_per_layer(
            lamda_min, fmax, layer_thickness, layer["vs"], nele_wave
        )
        eley_size = layer_thickness / eley_number
        # global coordinate offset from rock
        roffset = (layer["layer_num"] - 1) * (eley_number * eley_size)
        layer.update(
            [("nely", eley_number), ("szely", eley_size), ("rock_offset", roffset)]
        )
        print(f'Layer: {layer["layer_num"]}, Layer thickness: {layer["thickness"]}, Number of elements: {layer["nely"]}, Element size: {layer["szely"]}')

    # element size in the x-direction is the smallest vertical element size
    szelys = np.array([layer["szely"] for layer in layers])
    lx = np.min(szelys)
    print(f"The horizontal element size: {lx}")

    # sum all the subdivision within a layer (vertical elements) for total number of vertical elements
    nelys = np.array([layer["nely"] for layer in layers])
    total_number_vrows = np.sum(nelys)
    print(f"Total number of elements: {total_number_vrows}")

    return layers, lx, total_number_vrows


def create_nodes(cxs, cys, start_node_number, xycoords):
    """Define node number with xy coordinates"""
    # print(f"Cxs: {cxs}")
    # print(f"Cys: {cys}")
    # create a itertools generator count
    gen_node_number = count(start_node_number)
    for (yc, xc) in product(cys, cxs):
        node_number = next(gen_node_number)
        xc = round(xc, 3)
        yc = round(yc, 3)
        # print(f"Node number: {node_number}, xc: {xc}, yc: {yc}")
        ops.node(node_number, xc, yc)
        xycoords.update({node_number: (xc, yc)})

    return xycoords


def layered_soil_nodes(layers, xyorigin, lx, start_node_number):
    """Create nodes for site response analysis with layers"""

    # empty dictionary for node numbers and their coordinates
    # the corner coordinates are in increasing order of the nodes
    # with node number and (x, y) coordinates with origin at the bottom left
    # {1: (x1, y1), 2: (x2, y2), .....}
    xycoords = {}

    # number of element in x and y direction
    nx = 1
    ox, oy = xyorigin
    # the base nodes and all the nodes except the topmost layer of nodes
    for layer in layers:
        ny = layer["nely"]
        ly = layer["szely"]
        oy = layer["rock_offset"]
        cxs = np.linspace(0, nx * lx, num=nx + 1) + ox
        # do no account for the top most row of nodes as they
        # will be created as part of the next layer
        cys = np.linspace(0, (ny - 1) * ly, num=ny) + oy
        xycoords = create_nodes(cxs, cys, start_node_number, xycoords)
        start_node_number = list(xycoords.keys())[-1] + 1

    # the topmost layer of nodes
    layer = layers[-1]
    ny = layer["nely"]
    ly = layer["szely"]
    oy = layer["rock_offset"]
    cys = np.array([oy + ny * ly])
    xycoords = create_nodes(cxs, cys, start_node_number, xycoords)

    return xycoords


def zerolength_dashpot_nodes(xycrd, start_node_number):
    """Define zero length dashpot nodes
    Create two nodes at the same location
    xy: location of the dashpot nodes
    start_node_number: starting node number for dashpot nodes
    Return: a dictionary of node number and xy coordinates"""

    # dictionary for node  numbers and xy coordinates
    xycoords = {}
    x, y = xycrd
    cxs = [x]
    cys = [y] * 2

    return create_nodes(cxs, cys, start_node_number, xycoords)


def fix_nodes(nodes, dofs):
    """Fix a list of nodes as per the list of dofs
    nodes: list of nodes [node1, node2, ...]
    dofs: list of list of dofs = [[dof1, dof2], [dof1, dof2], ... ]
    where there is one-to-one correspondence between node numbrers in nodes and list
    of dofs"""

    for nd, dfs in zip(nodes, dofs):
        ops.fix(nd, *dfs)
        print(f"Node: {nd}, fix: {dfs}")


def fix_nodes_same(nodes, dofs):
    """Fix a list of nodes as per the list of dof
    nodes: a list of nodes [node1, node2 ...]
    dofs a list of dofs [ dof1, dof2 dof3.. ndodfs]
    Same list of dofs will be applied to all nodes"""
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

    if len(dofs) == 1:
        dofs = dofs * len(cnodetags)

    # check if rnodetags/dofs and cnodetags are the same length
    if len(rnodetags) != len(cnodetags):
        raise ValueError(
            "create_equaldofs: List rnodetags and list cnodetags must be of same length"
        )

    if len(dofs) != len(cnodetags):
        raise ValueError(
            "create_equaldofs: List dofs and list cnodetags must be of same length"
        )

    print("{0:>6}, {1:>6}, {2:>10}".format("NodeR", "NodeC", "dofs"))
    for rnodetag, cnodes, dfs in zip(rnodetags, cnodetags, dofs):
        for (rnode, cnode) in product([rnodetag], cnodes):
            # print(f"rnode: {rnode}")
            # print(f"cnode: {cnode}")
            ops.equalDOF(rnode, cnode, *dfs)
            print(f"{rnode:6d}, {cnode:6d}, {dfs}")


def layered_soil_assign_material(layers, analysis_type):
    """Assign material to different layers, material tags for each layer is the layer number"""
    for layer in layers:
        ops.nDMaterial(
            "PressureDependMultiYield",
            int(layer["layer_num"]),
            analysis_type,
            layer["density"],
            layer["modG"],
            layer["modK"],
            layer["phi"],
            layer["peakshearstrain"],
            layer["refpressure"],
            layer["pressurecoeff"],
            layer["phasetrans_angle"],
            layer["contraction_coeff"],
            *[layer["dilation_param1"], layer["dilation_param2"]],
            *[layer["liquefaction_param1"], layer["liquefaction_param2"], layer["liquefaction_param3"]],
            int(layer["nyieldsurfaces"]),
            layer["e0"],
            *[layer["cs1"], layer["cs2"], layer["cs3"], layer["pa"]],
            layer["c"],
        )
    print(f"Assigned materials to layers")


def layered_soil_elements(layers, soilnodes, start_element_number, nx, accg):
    """Create soil elements"""
    # dictionary for soil elements and nodes
    soil_elements = {}
    # arrange nodes as a list of lists grouped by rows of nodes
    # e.g [[1, 2], [3, 4], ...]
    # where [1, 2] are nodes in the first row at the rock level
    # [3, 4] are next row of nodes above [1, 2]
    # note layer 1 is the bottom most layer

    # some element paramters, these might need to be adjusted for different analysis
    thickness = 1.0
    analysis_type = "PlaneStrain"
    surface_pressure = 0.0
    rho = 0.0
    b1 = 0.0

    for layer in layers:
        b2 = -accg * layer["density"]
        eleprop = {
            "thickness": thickness,
            "type": analysis_type,
            "material_tag": int(layer["layer_num"]),
            "bulk_modulus": layer["modK"],
            "pressure": surface_pressure,
            "rho": rho,
            "b1": b1,
            "b2": b2,
        }
        ny = layer["nely"]
        layer_num = layer["layer_num"]

        start_idx = (layer_num - 1) * ny
        end_idx = layer_num * ny + 1
        soil_nodes = soilnodes[start_idx:end_idx]

        soil_elements = create_elements(
            soil_elements, soil_nodes, nx, ny, start_element_number, eleprop
        )
        start_element_number = list(soil_elements.keys())[-1] + 1

    return soil_elements


def create_elements(soil_elements, hr_nodes_list, nx, ny, start_element_number, eprop):
    """Create 4 node quad elements"""
    thick = eprop["thickness"]
    anlys_type = eprop["type"]
    mattag = eprop["material_tag"]
    pressure = eprop["pressure"]
    rho = eprop["rho"]
    b1 = eprop["b1"]
    b2 = eprop["b2"]

    # start the counter
    gen_element_numbers = count(start_element_number)

    # for (x1, y1), (x2, y2)
    rlist = [1] + [2] * (nx - 1) + [1]
    for bcrns, tcrns in zip(hr_nodes_list[0:-1], hr_nodes_list[1:]):
        bcrns = list(chunks(repeatlist(bcrns, rlist), 2))
        tcrns = list(chunks(repeatlist(tcrns, rlist), 2))
        for bcrn, tcrn in zip(bcrns, tcrns):
            elen = next(gen_element_numbers)
            # print(
            #     f"Element: {elen}, Nodei: {bcrn[0]}, Nodej: {bcrn[1]}, Nodek: {tcrn[1]}, Nodel: {tcrn[0]}, mattag: {mattag}"
            # )
            elnodes = [bcrn[0], bcrn[1], tcrn[1], tcrn[0]]
            ops.element(
                "quad", elen, *elnodes, thick, anlys_type, mattag, pressure, rho, b1, b2
            )
            soil_elements.update({elen: elnodes + [mattag]})

    return soil_elements


def update_material_stage(mattags, stage=0):
    """Update material stage"""
    for mattag in mattags:
        ops.updateMaterialStage("-material", int(mattag), "-stage", stage)


def data_recorders(fpath, fname_prefix, number_of_nodes, number_of_elements, motiondt):
    # this is a deviation from the original solution, since only ground
    # accelerations, velocity and displacements are considered, for now only ground
    # node values will be recorded

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
        "-dT", motiondt,
        "-nodeRange", 1, number_of_nodes,
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
            "-dT", motiondt,
            "-eleRange", 1, int(number_of_elements),
            # "material", gpt,
            "material", comb[1],
            "stress",
        )
    # fmt: on


def main():
    # file path and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"

    # layer info file
    fname_layerinfo = "ndmat_autogen_multiyield_pressuredependent_layers.csv"
    f_layerinfo = path_data.joinpath(fname_layerinfo)

    # general filename for recorder outputs
    fname_prefix = "ex_g_02_siteresponse_multiyield_dependent_totalstress"

    # velocity time history file
    velfile = "velocityhistory.out"
    fvel = str(path_data.joinpath(velfile))
    print(f"Ground motion file path: {fvel}")

    # bedrock shear wave velocity [m/s]
    rock_vs = 762.0
    # bedrock mass density [Mg/m^3]
    rock_density = 2.396
    # acceleration due to gravity [m/s2]
    accg = 9.81

    # ground motion paramters
    # time step in ground motion record [s]
    gm_dt = 0.005
    # number of steps in ground motion record
    # this depends on the number of points in the ground motion file
    gm_nsteps = 7990
    # gm_nsteps = 300

    # rayleigh damping parameters (read on this)
    # damping ratio
    damping_ratio = 0.02
    # lower frequency [Hz]
    f_lower = 0.2
    omega_lower = 2 * np.pi * f_lower
    # upper frequency [Hz]
    f_upper = 20
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


    # number of elements in the horizontal direction, ny will be determined based on
    # soil layer information
    nx = 1

    # define mesh geometry
    # center offset from the bottom left of the page (origin of the page, origin transformed)
    ox = 0.0
    oy = 0.0

    # wavelength parameters
    # highest frequency desired to be well resolved [Hz]
    fmax = 100.0
    # minimum number of elements per wavelength
    nele_wave = 8

    skiprows = 2
    layers = read_autogen_multiyield_pressure_dependent_properites_Vs(
        f_layerinfo, skiprows=skiprows
    )

    # compute the number of subdivisions required for each layer and 
    # add to the layer information
    layers, lx, total_number_vrows = number_of_layer_subdivisions(
        layers, fmax, nele_wave
    )

    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 2)

    # the origin of the model
    xyorigin = (0.0, 0.0)

    # the corner coordinates are in increasing order of the nodes
    # with node number and (x, y) coordinates with origin at the bottom left
    # {1: (x1, y1), 2: (x2, y2), .....}
    start_node_number = 1
    soil_nodes = layered_soil_nodes(layers, xyorigin, lx, start_node_number)
    last_node_number = list(soil_nodes.keys())[-1]

    # print the soil nodes
    for key, values in soil_nodes.items():
        print(f"Node: {key}, (x, y): {values}")

    print(f"Finished creating soil nodes")
    print(f"Last soil node number: {last_node_number}")

    print(f"Dashpot nodes:")
    # dashpot node numbers
    dp_start_node_number = 2000
    # dashpot location
    dashpot_xy = (0.0, 0.0)
    dashpot_nodes = zerolength_dashpot_nodes(dashpot_xy, dp_start_node_number)
    dp_last_node_number = list(dashpot_nodes.keys())[-1]

    # print the dashpot nodes
    for key, values in dashpot_nodes.items():
        print(f"Node: {key}, (x, y): {values}")

    print(f"Finished creating dashpot nodes")
    print(f"Last dashpot node number: {dp_last_node_number}")

    # boundary conditions
    print(f"Boundary conditions:")

    # fix based nodes against vertical displacement
    print(f"Fix base nodes:")
    # corner nodes horizontally arranged
    hr_crnodes = list(chunks(list(soil_nodes.keys()), nx + 1))
    base_crnodes = hr_crnodes[0]
    # print(f"Corner nodes horizontally arranged: {hr_crnodes}")
    print(f"Base nodes: {base_crnodes}")
    # boundary conditions for the base nodes, 0 = do not fix, 1 = fix
    # fix means displacement = 0
    basedofs = [0, 1]
    fix_nodes_same(base_crnodes, basedofs)

    print(f"Fix dahspot nodes:")
    # fix dashpot nodes
    dashpot_ndnums = list(dashpot_nodes.keys())
    # print(f"Dashpot node numbers: {dashpot_ndnums}")
    dashdofs = [[1, 1], [0, 1]]
    fix_nodes(dashpot_ndnums, dashdofs)

    print(f"Soil equalDOF:")
    # equalDOF for all soil elements (simple shear deformation)
    # the left edge nodes are the rnodes and rest of the nodes in the same
    # ordinates are the cnodes for e.g. if [1, 2, 3] are nodes at y = 0 then
    # rnode = 1 and cnodes are 2 and 3
    rnodetags = [x[0] for x in hr_crnodes]
    # print(f"Left edge nodes: {rnodetags}")
    # the interior and the right edge nodes
    cnodetags = [x[1:] for x in hr_crnodes]
    # print(f"Interior and right edge nodes: {cnodetags}")
    # the dof direction for equalDOF, 1 is the x-direction, 2 is the y-direction
    # make the 1 and 2 dofs of cnode same as that of the rnode
    sdofs = [1, 2]
    # do not apply equalDOF to the base nodes
    create_equaldofs(rnodetags[1:], cnodetags[1:], [sdofs])

    print(f"Dashpot equalDOF:")
    # equalDOF for the dashpot
    rnodetags = base_crnodes[0]
    cnodestags = [[2, 2001]]
    dpdofs = [[1]]
    create_equaldofs([rnodetags], cnodestags, dpdofs)

    print(f"Created all boundary conditions:")

    print(f"Soil materials")
    # define soil material
    # multi yield pressure dependent material properites with plane strain nd=2 analysis

    # type of analysis, 2: plane-strain, 3: 3D analysis
    anlytype = 2
    layered_soil_assign_material(layers, anlytype)
    print(f"Finished creating all soil materials")

    # define soil elements, some of the variables need to be changed in the function
    # not a good way to do things but it is what it is
    # todo: start from here, make this layer dependent too if soil density is different in different layers

    start_element_number = 1
    soil_elements = layered_soil_elements(
        layers, hr_crnodes, start_element_number, nx, accg
    )

    # print(
    #     "{0:5s}, {1:6s}, {2:6s}, {3:6s}, {4:6s}, {5:6s}".format(
    #         "Ele", "Node i", "Node j", "Node k", "Node l", "mattag"
    #     )
    # )
    # for key, values in soil_elements.items():
    #     print("{0:5d}, {1:6d}, {2:6d}, {3:6d}, {4:6d}, {5:6d}".format(key, *values))

    last_element_number = np.array(list(soil_elements.keys()))[-1]
    soil_mattags = np.unique(np.array(list(soil_elements.values()))[:, -1])
    print(
        f"Finished creating soil elements, number of elements: {last_element_number}, number of materials: {len(soil_mattags)}"
    )

    # material and elements for viscous damping
    # dashpot coefficients, again figure out how this coefficient comes about
    dashpot_c = lx * rock_density * rock_vs
    # for linear damping, power factor = 1
    dashpot_alpha = 1.0
    # dashpot material
    dashpot_mattag = 4000
    ops.uniaxialMaterial("Viscous", dashpot_mattag, dashpot_c, dashpot_alpha)
    # element, connecting two dashpot nodes
    dashpot_elenum = 5000

    # print(f"Dashpot element number: {dashpot_elenum}")
    # print(f"Dashpot node numbers: {dashpot_ndnums}")
    ops.element(
        "zeroLength",
        dashpot_elenum,
        *dashpot_ndnums,
        "-mat",
        dashpot_mattag,
        "-dir",
        *[1],
    )
    print(f"Dashpot element created:")
    print(
        f"Element number: {dashpot_elenum}, dashpot node numbers: {dashpot_ndnums}, dashpot material tag: {dashpot_mattag}"
    )

    print(f"Gravity analysis:")
    # update material stage to 0 for elastic behavior
    update_material_stage(soil_mattags, 0)
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
    update_material_stage(soil_mattags, 1)
    ops.analyze(40, 500.0)
    print(f"Plastic gravity analysis over")

    print(f"Create data recorders")
    # specify the node and element at which the acceleration, velocity, displacement,
    # stress and strain time histories are required, for surface node
    data_recorders(
        path_data, fname_prefix, last_node_number, last_element_number, gm_dt
    )
    print(f"Finished creating data recorders")

    # destory previous analysis object and start consolidation
    print(
        f"Wiping gravity analysis, resetting time to 0.0, and starting dynamic analysis:"
    )
    ops.setTime(0.0)
    ops.wipeAnalysis()
    

    # define constant factor for applied velocity, find out how this comes about?
    # this is what I found, the link might not work the next time
    # http://www.bgu.ac.il/geol/hatzor/articles/Bao_Hatzor_Huang_2012.pdf
    cfactor = dashpot_c

    # load pattern and timeseries for applied force history
    print(f"Ground motion file: {fvel}, dt: {gm_dt}, cfactor: {cfactor}")

    # load timeseries tag
    tstag_eq = 1
    # load pattern tag
    pattag_eq = 1
    # node at which the excitation is applied
    nodetag_eq = 1
    loadvals = [1.0, 0.0]
    ops.timeSeries(
        "Path", tstag_eq, "-dt", gm_dt, "-filePath", fvel, "-factor", cfactor
    )

    ops.pattern("Plain", pattag_eq, tstag_eq)
    ops.load(nodetag_eq, *loadvals)

    # determine the analysis time  step using CFL condition
    # CFL stands for Courant-Friedrichs-Levy
    # ref: http://web.mit.edu/16.90/BackUp/www/pdfs/Chapter14.pdf
    # duration of groundmotion [s]
    duration = gm_dt * gm_nsteps

    # trial analysis step, I do not know how this came about
    ktrial = lx / np.sqrt(rock_vs)
    if gm_dt < ktrial:
        nsteps = gm_nsteps
        dt = gm_dt
    else:
        nsteps = int(floor(duration / ktrial) + 1)
        dt = duration / nsteps

    print(f"Number of steps: {nsteps}, time step, dt: {dt}")
    print(f"Newmark: gamma: {newmark_gamma}, beta: {newmark_beta}")
    print(
        f"Rayleigh: alpham: {alpham}, betak: {betak}, betakinit: {betakinit}, betakcomm: {betakcomm}"
    )

    # ops.constraints("Transformation")
    # ops.test("NormDispIncr", 1.0e-6, 50, 5)
    # ops.algorithm("KrylovNewton")
    ops.constraints("Plain")
    ops.test("NormDispIncr", 1e-3, 15, 5)
    ops.algorithm("Newton")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", newmark_gamma, newmark_beta)
    ops.rayleigh(alpham, betak, betakinit, betakcomm)
    ops.analysis("Transient")
    ops.analyze(nsteps, dt)

    print(f"Dynamic analysis over")

    ops.wipe()


if __name__ == "__main__":
    main()

