#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import openseespy.opensees as ops
from pathlib import Path
from itertools import count, chain, repeat, product

# Example problem:
# Description: 1D Total Stress Site Response Analysis, Single soil layer
# Original authors of this example: Christopher McGann and Pedro Arduino, University of Washington
# ref: https://opensees.berkeley.edu/wiki/index.php/Site_Response_Analysis_of_a_Layered_Soil_Column_(Total_Stress_Analysis)
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


def create_nodes(cxs, cys, start_node_number, xycoords):
    """Define node number with rectangular gridlike xy coordinates
    cxs: list of x-coordinates
    cys: list of y-coordinates
    start_node_number: interger number for the starting node
    xycoords: a dictionary that is returned {node1: (xc1, yc1), node2: (xc2, yc2), ...}
    """
    print("{0:>5}, {1:>6}, {2:>6}".format("Node", "X", "Y"))
    # create a itertools generator count
    gen_node_number = count(start_node_number)
    for (yc, xc) in product(cys, cxs):
        node_number = next(gen_node_number)
        print("{0:5d}, {1:6.2f}, {2:6.2f}".format(node_number, xc, yc))
        ops.node(node_number, xc, yc)
        xycoords.update({node_number: (xc, yc)})

    return xycoords


def create_dashpot_nodes(cxs, cys, start_node_number, xycoords):
    """Define dashpot nodes"""
    # checks
    if len(cxs) != len(cys):
        raise ValueError("List cxs and list cys must be of same length")
    # print(f"Cxs: {cxs}")
    # print(f"Cys: {cys}")
    # create a itertools generator count
    gen_node_number = count(start_node_number)
    for (yc, xc) in zip(cys, cxs):
        node_number = next(gen_node_number)
        print(f"Node number: {node_number}, xc: {xc}, yc: {yc}")
        ops.node(node_number, xc, yc)
        xycoords.update({node_number: (xc, yc)})
        # node_number = next(gen_node_number)
        # ops.node(node_number, xc, yc)
        # xycoords.update({node_number: (xc, yc)})

    return xycoords


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


def create_elements(soil_elements, soil_nodes, nx, ny, eprop):
    """Create elements from the 4 node quad elements"""
    thick = eprop["thickness"]
    anlys_type = eprop["type"]
    mattag = eprop["material_tag"]
    pressure = eprop["pressure"]
    rho = eprop["rho"]
    b1 = eprop["b1"]
    b2 = eprop["b2"]
    gen_element_numbers = count(1)
    crnodes_list = list(soil_nodes.keys())

    # arrange the nodes horizontally
    hr_crnodes = list(chunks(crnodes_list, nx + 1))
    gen_element_numbers = count(1)

    # for (x1, y1), (x2, y2)
    rlist = [1] + [2] * (nx - 1) + [1]
    for bcrns, tcrns in zip(hr_crnodes[0:-1], hr_crnodes[1:]):
        bcrns = list(chunks(repeatlist(bcrns, rlist), 2))
        tcrns = list(chunks(repeatlist(tcrns, rlist), 2))
        for bcrn, tcrn in zip(bcrns, tcrns):
            elen = next(gen_element_numbers)
            # print(
            #     f"Element: {elen}, Nodei: {bcrn[0]}, Nodej: {bcrn[1]}, Nodek: {tcrn[1]}, Nodel: {tcrn[0]}"
            # )
            elnodes = [bcrn[0], bcrn[1], tcrn[1], tcrn[0]]
            ops.element(
                "quad", elen, *elnodes, thick, anlys_type, mattag, pressure, rho, b1, b2
            )
            soil_elements.update({elen: elnodes})

    return soil_elements


def data_recorders(fpath, fname_prefix, number_of_nodes, number_of_elements, motiondt):
    # this is a deviation from the original solution, since only ground
    # accelerations, velocity and displacements are considered, for now only ground
    # node values will be recorded

    # fmt: off
    # recorders for nodal displacements, velocity and acceleration at each time step
    restypes = ["disp", "vel", "accel"]
    for restype in restypes:
        fname = fname_prefix + restype + ".out"
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

    # # ref: http://opensees.berkeley.edu/wiki/index.php/PressureIndependMultiYield_Material
    # # For 2D problems, the stress output follows this order: σxx, σyy, σzz, σxy, ηr, where ηr 
    # # is the ratio between the shear (deviatoric) stress and peak shear strength at the current
    # # confinement (0<=ηr<=1.0). The strain output follows this order: εxx, εyy, γxy.
    # stresses and strains at each Gauss point in the soil elements
    gausspoints = ["1", "2", "3", "4"]
    for gpt in gausspoints:
        fname = fname_prefix + "_stress" + gpt + ".out"
        fout = str(fpath.joinpath(fname))
        ops.recorder(
            "Element",
            "-file", fout,
            "-time",
            "-dT", motiondt,
            "-eleRange", 1, number_of_elements,
            "material", gpt,
            "stress",
        )
        fname = fname_prefix + "_strain" + gpt + ".out"
        fout = str(fpath.joinpath(fname))
        ops.recorder(
            "Element",
            "-file", fout,
            "-time",
            "-dT", motiondt,
            "-eleRange", 1, number_of_elements,
            "material", gpt,
            "strain",
        )
    # fmt: on


def roundup(num):
    """Check if a float is a whole number if not round up"""
    return int(num) if num.is_integer() else int(np.ceil(num))


def main():
    # file path and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"

    # general filename for recorder outputs
    fname_prefix = "ex_g_02_siteresponse_totalstress_"

    # velocity time history file
    velfile = "velocityhistory.out"
    fvel = str(path_data.joinpath(velfile))
    print(f"Ground motion file path: {fvel}")
    fvel = "data/velocityhistory.out"

    # soil profile, thickness of the soil layer [m]
    depth_soillayer = 40.0

    # acceleration due to gravity [m/s2]
    accg = 9.81

    # material properties
    # # soil saturated density [Mg/m3], or soil mass density
    soil_satdensity = 1.7
    # soil shear wave velocity [m/s]
    soil_vs = 250.0
    # Poisson's ratio of the soil
    nu = 0.0
    # the undrained shear strength, c of Mohr-Coulomb failure envelop [kPa]
    cohesion = 95.0
    # soil friction angle, phi of Mohr-Coulomb failure envelop [deg]
    friction_angle = 0.0
    # peak shear strain
    peak_shear_strain = 0.05
    # reference pressure [kPa]
    reference_pressure = 80.0
    # pressure dependency coefficient
    pressure_dependence = 0.0
    # bedrock shear wave velocity [m/s]
    rock_vs = 760.0
    # bedrock mass density [Mg/m^3]
    rock_density = 2.4
    # soil shear modulus [kPa]
    modG = soil_satdensity * soil_vs ** 2
    # soil elastic modulus [kPa]
    modE = 2 * modG * (1 + nu)
    # soil bulk modulus [kPa]
    modK = modE / (3 * (1 - 2 * nu))
    # number of yield surfaces
    nsurf = 25

    print(f"Soil elastic properites:")
    print(f"G: {modG/1000:6.1f} MPa, E: {modE/1000:6.1f} MPa, K: {modK/1000:6.1f} MPa")

    # ground motion paramters
    # time step in ground motion record [s]
    gm_dt = 0.005
    # number of steps in ground motion record
    # this depends on the number of points in the ground motion file
    gm_nsteps = 7990
    # gm_nsteps = 300

    # wavelength parameters
    # highest frequency desired to be well resolved [Hz]
    fmax = 100.0
    # wavelength of the highest resolved frequency
    lamdamin = soil_vs / fmax
    # number of elements per one wavelength
    nele_wave = 10

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
    alpham = (
        2.0 * damping_ratio * omega_lower * omega_upper / (omega_lower + omega_upper)
    )
    betak = 2.0 * damping_ratio / (omega_lower + omega_upper)
    betakinit = 0.0
    betakcomm = 0.0
    print(f"Damping coefficients: alpham = {alpham:6.3f}, betak = {betak:6.5f}")

    # Newmark parameters
    newmark_gamma = 0.5
    newmark_beta = 0.25

    # acceleration due to gravity in the x and y direction
    accg_x = 0.0
    accg_y = -accg
    wgt_x = 0.0
    wgt_y = accg_y * soil_satdensity

    # define mesh geometry
    # center offset from the bottom left of the page (origin of the page, origin transformed)
    ox = 0.0
    oy = 0.0

    # number of element in x and y direction
    nx = 1
    # trial for vertical element size
    # initial element size
    h_trial = lamdamin / nele_wave
    # if the number of elements is not an integer round up
    ny = roundup(depth_soillayer / h_trial)
    print(f"Number of elements: nx = {nx}, ny = {ny}")

    # size of elements in x and y direction of the nodes
    ly = float(depth_soillayer / ny)
    lx = ly
    print(f"Element size: lx = {lx:6.3f} m, ly = {ly:6.3f} m")

    # soil element thickness
    thickness = 1.0
    # analysis type, "PlaneStrain" or "PlaneStress"
    analysis_type = "PlaneStrain"
    # surface pressure on elements
    surface_pressure = 0.0

    # start node number
    start_node_number = 1

    # ending node number for corner nodes
    # corner nodes, crnodes: the nodes at the corners of the elements
    last_node_number = (nx + 1) * (ny + 1)

    # total number of elements
    total_number_elements = nx * ny

    # dictionary for node numbers and corresponding coordinates
    # {node_number: (x, y)}
    soil_nodes = {}

    # dashpot nodes
    dashpot_nodes = {}

    # dictionary for elements and node numbers
    soil_elements = {}

    # wipe previous analyses
    ops.wipe()

    # corner nodes are 2D with 2 DOF (displacements in x1 and x2)
    ops.model("basic", "-ndm", 2, "-ndf", 2)

    # the corner coordinates are in increasing order of the nodes
    # with node number and (x, y) coordinates with origin at the bottom left
    # {1: (x1, y1), 2: (x2, y2), .....}
    # center for the corner nodes
    cxs = np.linspace(0, nx * lx, num=nx + 1) + ox
    cys = np.linspace(0, ny * ly, num=ny + 1) + oy
    # print(f"Length cxs: {len(cxs)}, length cys: {len(cys)}")
    soil_nodes = create_nodes(cxs, cys, start_node_number, soil_nodes)
    print(f"Finished creating soil nodes")
    print(f"Last soil node number: {last_node_number}")
    # print the corner nodes
    # for key, values in soil_nodes.items():
    #     print(f"Node: {key}, (x, y): {values}")

    # dashpot node numbers
    dp_start_node_number = 2000
    print(f"Dashpot nodes:")
    # location of dashpot nodes, the way create_nodes is written
    # the total nodes is the itertools.prodcut of dp_cxs and dp_cys
    dp_cxs = [0.0]
    dp_cys = [0.0, 0.0]
    dashpot_nodes = create_nodes(dp_cxs, dp_cys, dp_start_node_number, dashpot_nodes)
    print(f"Finished creating dashpot nodes")
    print(f"Last dashpot node number: {dp_start_node_number + 1}")

    # corner nodes horizontally arranged
    hr_crnodes = list(chunks(list(soil_nodes.keys()), nx + 1))
    base_crnodes = hr_crnodes[0]
    # print(f"Corner nodes horizontally arranged: {hr_crnodes}")
    # print(f"Base nodes: {base_crnodes}")

    # boundary conditions for the base nodes, 0 = do not fix, 1 = fix
    # fix means displacement = 0
    basedofs = [0, 1]
    print(f"Fix base nodes:")
    fix_nodes_same(base_crnodes, basedofs)

    # for key, values in dashpot_nodes.items():
    #     print(f"Node: {key}, (x, y): {values}")

    # fix dashpot nodes
    dashpot_ndnums = list(dashpot_nodes.keys())
    # print(f"Dashpot node numbers: {dashpot_ndnums}")
    dashdofs = [[1, 1], [0, 1]]
    print(f"Fix dashpot nodes:")
    fix_nodes(dashpot_ndnums, dashdofs)

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
    print(f"Soil equalDOF:")
    # do not apply equalDOF to the base nodes
    create_equaldofs(rnodetags[1:], cnodetags[1:], [sdofs])

    # equalDOF for the dashpot
    rnodetags = base_crnodes[0]
    cnodestags = [[2, 2001]]
    dpdofs = [[1]]
    print(f"Dashpot equalDOF:")
    create_equaldofs([rnodetags], cnodestags, dpdofs)

    print(f"Created all boundary conditions:")

    # define soil material
    soil_mattag = 1
    # nd = 2 for plane strain and 3 for 3-D
    nd = 2
    # number of dimensions (nd) 2 for plain-strain 3 for 3D
    ops.nDMaterial(
        "PressureIndependMultiYield",
        soil_mattag,
        nd,
        soil_satdensity,
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
        "type": analysis_type,
        "material_tag": soil_mattag,
        "bulk_modulus": modK,
        "pressure": surface_pressure,
        "rho": 0.0,
        "b1": wgt_x,
        "b2": wgt_y,
    }

    soil_elements = create_elements(soil_elements, soil_nodes, nx, ny, eleprop)
    print(f"Soil elements:")
    print(
        "{0:5s}, {1:6s}, {2:6s}, {3:6s}, {4:6s}".format(
            "Ele", "Node i", "Node j", "Node k", "Node l"
        )
    )
    for key, values in soil_elements.items():
        print("{0:5d}, {1:6d}, {2:6d}, {3:6d}, {4:6d}".format(key, *values))

    last_element_number = list(soil_elements.keys())[-1]
    print(f"Last element number: {last_element_number}")
    print(f"All soil elements created")

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
    ops.updateMaterialStage("-material", soil_mattag, "-stage", 0)
    print(f"Material updated for elastic behavior during gravity loading")

    # gravity loading
    # ops.constraints("Transformation")
    ops.constraints("Plain")
    ops.test("NormDispIncr", 1e-5, 30, 1)
    ops.algorithm("Newton")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.integrator("Newmark", newmark_gamma, newmark_beta)
    ops.analysis("Transient")
    ops.analyze(10, 500.0)
    print(f"Elastic gravity analysis over")

    # update material stage to include plastic analysis
    ops.updateMaterialStage("-material", soil_mattag, "-stage", 1)
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
    ops.wipeAnalysis()
    ops.setTime(0.0)

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
    ktrial = lx / np.sqrt(soil_vs)
    if gm_dt < ktrial:
        nsteps = gm_nsteps
        dt = gm_dt
    else:
        nsteps = int(floor(duration / ktrial) + 1)
        dt = duration / nsteps
    # dt = 0.005
    print(f"Number of steps: {nsteps}, time step, dt: {dt}")
    print(f"Newmark: gamma: {newmark_gamma}, beta: {newmark_beta}")
    print(
        f"Rayleigh: alpham: {alpham}, betak: {betak}, betakinit: {betakinit}, betakcomm: {betakcomm}"
    )
    # at present use KrylovNewton with Transformation and Plain with Newton
    # ops.constraints("Transformation")
    # ops.test("NormDispIncr", 1.0e-6, 50, 5)
    # ops.algorithm("KrylovNewton")
    ops.constraints("Plain")
    ops.test("NormDispIncr", 1.0e-5, 15, 5)
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

