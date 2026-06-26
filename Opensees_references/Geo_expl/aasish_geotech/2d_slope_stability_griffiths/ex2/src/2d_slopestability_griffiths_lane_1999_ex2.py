<<<<<<< HEAD
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


def fix_nodes_dashpot(nodes, dofs):
    """Fix a list of nodes as per the list of dofs
    nodes: list of nodes [node1, node2, ...]
    dofs: list of list of dofs = [[dof1, dof2], [dof1, dof2], ... ]
    where there is one-to-one correspondence between node numbrers in nodes and list
    of dofs"""

    for nd, dfs in zip(nodes, dofs):
        ops.fix(nd, *dfs)
        # print(f"Node: {nd}, fix: {dfs}")


def fix_nodes_bound(nodes, dofs):
    """Fix a list of nodes as per the list of dof
    nodes: a list of nodes [node1, node2 ...]
    dofs a list of dofs [ dof1, dof2 dof3.. ndodfs]
    Same dofs will be applied to all nodes"""
    for nd in nodes:
        ops.fix(nd, *dofs)
        # print(f"Node: {nd}, fix: {dofs}")


def get_tagged_nodes(fpath, start_string, end_string):
    """Get nodes from the tag file
    fpath: path to the tag file, where the boundary conditions are written
    start_tag: string indicating the start of text block to be read
    end_tag: string indicating the end of text block to be read
    Return: 
    """
    lines = read_blocks(fpath, start_string, end_string)
    fnodes = []
    for line in lines:
        vals = line.strip(",\n").split(",")
        fnodes += [int(val.strip()) for val in vals]
    return fnodes


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


def read_quadelements(fpath):
    """Read nodes tags and coordinates from file, 4 node Quad elements
    fpath: path to the nodes file
    Return: a dictionary {node_id: [x, y, x]} datatypes {int: [float, float, float]}"""
    datatypes = [int, int, int, int, int, str, str]
    data = {}
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


def create_elements(elements, elprop):
    """Create elements from the 4 node quad elements"""
    for element_id, v in elements.items():
        # print(element_id, v["nodes"])
        ops.element(
            elprop["element_type"],
            element_id,
            *v["nodes"],
            elprop["thickness"],
            elprop["analysis_type"],
            elprop["material_tag"],
            elprop["surface_pressure"],
            elprop["density"],
            elprop["b1"],
            elprop["b2"],
        )


def factored_strength_params(c, phi, fs):
    """Return factored strength parameters, c and phi"""
    c = c / fs
    phi = np.degrees(np.arctan(np.tan(np.radians(phi)) / fs))

    return c, phi


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


def data_recorders(
    fpath, fname_prefix, nodes_range, elements_range,
):
    # this is a deviation from the original solution, since only ground
    # accelerations, velocity and displacements are considered, for now only ground
    # node values will be recorded

    # fmt: off
    # recorders for nodal displacements, velocity and acceleration at each time step
    restypes = ["disp"]
    for restype in restypes:
        fname = fname_prefix + restype + ".out"
        print(f"Filename: {fname}")
        fout = str(fpath.joinpath(fname))
        ops.recorder(
        "Node",
        "-file", fout,
        "-time",
        "-nodeRange", *nodes_range,
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
            "-eleRange", *elements_range,
            "material", gpt,
            "stress",
        )
        fname = fname_prefix + "_strain" + gpt + ".out"
        fout = str(fpath.joinpath(fname))
        ops.recorder(
            "Element",
            "-file", fout,
            "-time",
            "-eleRange", *elements_range,
            "material", gpt,
            "strain",
        )
    # fmt: on


def slope_stability_analysis(fid_dict, fpath_rec, matprop, eleprop):
    # wipe previous analyses
    ops.wipe()

    # read the nodes file
    nodes = read_nodes(fid_dict["nodes"])
    elements = read_quadelements(fid_dict["elements"])

    # corner nodes are 2D with 2 DOF (displacements in x1 and x2)
    ops.model("basic", "-ndm", 2, "-ndf", 2)
    # print(f"Data recorders: ")

    # PVD recorder
    # ops.recorder("PVD", str(fpath_rec), "disp")

    # node and element recorders
    data_recorders(
        fpath_rec,
        fpath_rec.name,
        [min([*nodes.keys()]), max([*nodes.keys()])],
        [min([*elements.keys()]), max([*elements.keys()])],
    )

    # create the nodes
    for node_id, xycrds in nodes.items():
        ops.node(node_id, *xycrds[:2])
    # the number of nodes created
    # print(f"Number of nodes created: {len(ops.getNodeTags())}")
    # number of nodes created
    # print(f"Number of nodes in the mesh: {len(nodes.keys())}")

    # boundary conditions for the base nodes, 0 = do not fix, 1 = fix
    # fix means displacement = 0
    basedofs = [1, 1]
    base_nodes = get_tagged_nodes(
        fid_dict["tags"], "Start_tag:Fix_110", "End_tag:Fix_110"
    )

    # print(f"Fix base nodes:")
    fix_nodes_bound(base_nodes, basedofs)

    # fix the left boundary in x-direction dofs = [1, 0]
    left_bound_dofs = [1, 0]
    left_boundary_nodes = get_tagged_nodes(
        fid_dict["tags"], "Start_tag:Fix_100", "End_tag:Fix_100"
    )
    # there could be overlapping nodes among the boundary conditions
    # check the tags file carefully and remove nodes that have already
    # been assigned boundary condition, for example in this particular case
    # Node 1, has to be removed from the left boundary as it is part of the base
    # this can be done manually or programatically
    left_boundary_nodes = list(set(left_boundary_nodes) - set(base_nodes))
    # print(f"Fix left boundary nodes:")
    fix_nodes_bound(left_boundary_nodes, left_bound_dofs)
    # print(f"Created all boundary conditions:")

    # print(f"Define Drucker-Prager material:")

    # number of dimensions (nd) 2 for plain-strain 3 for 3D
    ops.nDMaterial(
        matprop["material_type"],
        matprop["material_tag"],
        matprop["bulk_modulus"],
        matprop["shear_modulus"],
        matprop["sigmay"],
        matprop["rho"],
        matprop["rhobar"],
        matprop["kinf"],
        matprop["ko"],
        matprop["delta1"],
        matprop["delta2"],
        matprop["hard"],
        matprop["theta"],
        matprop["density"],
    )
    # print(f"Soil material created")

    create_elements(elements, eleprop)
    # print(f"All soil elements created")

    # save the initial state
    ops.record()
    # data_recorders(
    #     fpath,
    #     fname_prefix,
    #
    # )

    # setup analysis
    # ops.constraints("Penalty", 1.0e20, 1.0e20)
    ops.constraints("Plain")
    ops.test("NormDispIncr", 1e-3, 50, 2)
    ops.algorithm("KrylovNewton")
    # ops.algorithm("Newton")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.integrator("LoadControl", 1)
    ops.analysis("Static")

    # not sure about this,
    two_stage_gravity = False
    if two_stage_gravity:
        # print(f"Gravity analysis:")
        # update material stage to 0 for elastic behavior,
        ops.updateMaterialStage("-material", eleprop["material_tag"], "-stage", 0)
        # print(f"Material updated for elastic behavior during gravity loading")
        # gravity loading
        analysis_res = ops.analyze(1)
        # print(f"Elastic gravity analysis over")
        # update material stage to include plastic analysis
        ops.updateMaterialStage("-material", eleprop["material_tag"], "-stage", 1)

    analysis_res = ops.analyze(1)
    # if analysis_res < 0:
    #     print("Regular Newton failed.. try initial stiffness for this step")
    #     ops.test("NormDispIncr", 1.0e-12, 1000)
    #     ops.algorithm("ModifiedNewton", "-initial")
    #     analysis_res = ops.analyze(1)
    # if analysis_res == 0:
    #     print("Modified Newton worked, now back to regular Newton")
    #     ops.test("NormDispIncr", 1.0e-12, 1000)
    #     ops.algorithm("Newton")
    # print(f"Plastic gravity analysis over\n")
    niter = ops.numIter()
    ops.wipe()

    return analysis_res, niter


def main():
    # file path and filenames
    path_root = Path(r"../")
    path_data = path_root / "data"
    path_msh = path_root / "gmsh"
    path_pvd = path_root / "pvd"

    # name of the nodes file
    fname_nodes = "griffiths_and_lane_1999_ex2_nodes.txt"
    fnodes = path_msh.joinpath(fname_nodes)
    # name of the elements file
    fname_elements = "griffiths_and_lane_1999_ex2_elements.txt"
    felements = path_msh.joinpath(fname_elements)
    # name of the files with fixities written
    fname_tags = "griffiths_and_lane_1999_ex2_tags.txt"
    ftags = path_msh.joinpath(fname_tags)

    # dictionary of fids relating to various files that is either read or written
    fid_dict = {"nodes": fnodes, "elements": felements, "tags": ftags}

    # acceleration due to gravity [m/s2]
    accg = 9.81
    # acceleration due to gravity in the x and y direction
    wgt_x = 0.0
    wgt_y = -accg

    # material properties
    # Young's modulus (kPa)
    modE = 1e5
    # Poisson's ratio of the soil
    nu = 0.3
    # soil shear modulus from Young's modulus [kPa]
    modG = modE / (2 * (1 + nu))
    # soil bulk modulus [kPa]
    modK = modE / (3 * (1 - 2 * nu))
    # soil saturated density, or soil mass density  [Mg/m3] equivalent [1 Mg/m3 = 10 kN/m3]
    soil_density = 2.0
    # soil friction angle, phi of Mohr-Coulomb failure envelop [deg]
    friction_angle = 20.0
    # the undrained shear strength, c of Mohr-Coulomb failure envelop [kPa]
    cohesion = 10.0
    # related to dilation? controls evolution of plastic volume change, 0 ≤ $rhoBar ≤ $rho
    rhobar = 0.0
    # nonlinear isotropic strain hardening parameter, $Kinf ≥ 0
    kinf = 0.0
    # nonlinear isotropic strain hardening parameter, $Ko ≥ 0
    ko = 0.0
    # nonlinear isotropic strain hardening parameter, $delta1 ≥ 0
    delta1 = 0.0
    # tension softening parameter, $delta2 ≥ 0
    delta2 = 0.0
    # linear strain hardening parameter, $H ≥ 0
    hard = 0.0
    # controls relative proportions of isotropic and kinematic hardening, 0 ≤ $theta ≤ 1
    theta = 0.0
    # print(f"Soil elastic properites:")
    # print(f"G: {modG/1000:6.1f} MPa, E: {modE/1000:6.1f} MPa, K: {modK/1000:6.1f} MPa")

    # material type and tag for soil
    soil_mattype = "DruckerPrager"
    soil_mattag = 1
    # material prop dictionary
    matprop = {
        "material_type": soil_mattype,
        "material_tag": soil_mattag,
        "bulk_modulus": modK,
        "shear_modulus": modG,
        "sigmay": 0.0,
        "rho": 0.0,
        "rhobar": rhobar,
        "kinf": kinf,
        "ko": ko,
        "delta1": delta1,
        "delta2": delta2,
        "hard": hard,
        "theta": theta,
        "density": soil_density,
    }

    # soil element thickness
    thickness = 1.0
    # analysis type, "PlaneStrain" or "PlaneStress"
    analysis_type = "PlaneStrain"
    # surface pressure on elements
    surface_pressure = 0.0
    # element type, 4 node quadrilateral
    eletype = "quad"
    # element property dictionary
    eleprop = {
        "element_type": eletype,
        "thickness": thickness,
        "analysis_type": analysis_type,
        "material_tag": soil_mattag,
        "bulk_modulus": modK,
        "surface_pressure": surface_pressure,
        "density": 0.0,
        "b1": wgt_x,
        "b2": wgt_y,
    }

    # filename prefix to store pvd data
    fnameprefix = "fs_"
    fss = np.linspace(1, 2.0, 11)
    # print(fss)
    fss = [0.8] + list(fss)
    # fss = [str(fs).replace(".", "").ljust(5, "0") for fs in fss]
    fnames_fs = [
        fnameprefix + str(round(fs, 5)).replace(".", "").ljust(5, "0") for fs in fss
    ]

    # factored parameters
    cs, phis = factored_strength_params(cohesion, friction_angle, np.array(fss))

    # convert to MC, c, phi to DP sigmay and rho
    sigmays, rhos = mc2dp(cs, phis)

    # file to save some iteration parameters
    fname_log = fnameprefix + "log.txt"
    fflog = path_data.joinpath(fname_log)
    fidlog = open(fflog, "w")
    print(
        f"{'FS':6s}, {'C':6s}, {'phi':6s}, {'num_iter':10s}, {'analysis':10s}",
        file=fidlog,
    )
    for fs, fname_fs, sigma_y, rho, c, phi in zip(
        fss, fnames_fs, sigmays, rhos, cs, phis
    ):
        path_fs = path_data / fname_fs
        path_fs.mkdir(parents=True, exist_ok=True)
        matprop["sigmay"] = sigma_y
        matprop["rho"] = rho
        fpath_rec = path_fs
        analysis_result, niter = slope_stability_analysis(
            fid_dict, fpath_rec, matprop, eleprop
        )
        print(
            f"{fs:6.3f}, {c:6.2f}, {phi:6.2f}, {niter:10d}, {analysis_result:10d}",
            file=fidlog,
        )
        if analysis_result < 0:
            break
        # time.sleep(2)
    fidlog.close()


if __name__ == "__main__":
    main()
=======
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


def fix_nodes_dashpot(nodes, dofs):
    """Fix a list of nodes as per the list of dofs
    nodes: list of nodes [node1, node2, ...]
    dofs: list of list of dofs = [[dof1, dof2], [dof1, dof2], ... ]
    where there is one-to-one correspondence between node numbrers in nodes and list
    of dofs"""

    for nd, dfs in zip(nodes, dofs):
        ops.fix(nd, *dfs)
        # print(f"Node: {nd}, fix: {dfs}")


def fix_nodes_bound(nodes, dofs):
    """Fix a list of nodes as per the list of dof
    nodes: a list of nodes [node1, node2 ...]
    dofs a list of dofs [ dof1, dof2 dof3.. ndodfs]
    Same dofs will be applied to all nodes"""
    for nd in nodes:
        ops.fix(nd, *dofs)
        # print(f"Node: {nd}, fix: {dofs}")


def get_tagged_nodes(fpath, start_string, end_string):
    """Get nodes from the tag file
    fpath: path to the tag file, where the boundary conditions are written
    start_tag: string indicating the start of text block to be read
    end_tag: string indicating the end of text block to be read
    Return: 
    """
    lines = read_blocks(fpath, start_string, end_string)
    fnodes = []
    for line in lines:
        vals = line.strip(",\n").split(",")
        fnodes += [int(val.strip()) for val in vals]
    return fnodes


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


def read_quadelements(fpath):
    """Read nodes tags and coordinates from file, 4 node Quad elements
    fpath: path to the nodes file
    Return: a dictionary {node_id: [x, y, x]} datatypes {int: [float, float, float]}"""
    datatypes = [int, int, int, int, int, str, str]
    data = {}
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


def create_elements(elements, elprop):
    """Create elements from the 4 node quad elements"""
    for element_id, v in elements.items():
        # print(element_id, v["nodes"])
        ops.element(
            elprop["element_type"],
            element_id,
            *v["nodes"],
            elprop["thickness"],
            elprop["analysis_type"],
            elprop["material_tag"],
            elprop["surface_pressure"],
            elprop["density"],
            elprop["b1"],
            elprop["b2"],
        )


def factored_strength_params(c, phi, fs):
    """Return factored strength parameters, c and phi"""
    c = c / fs
    phi = np.degrees(np.arctan(np.tan(np.radians(phi)) / fs))

    return c, phi


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


def data_recorders(
    fpath, fname_prefix, nodes_range, elements_range,
):
    # this is a deviation from the original solution, since only ground
    # accelerations, velocity and displacements are considered, for now only ground
    # node values will be recorded

    # fmt: off
    # recorders for nodal displacements, velocity and acceleration at each time step
    restypes = ["disp"]
    for restype in restypes:
        fname = fname_prefix + restype + ".out"
        print(f"Filename: {fname}")
        fout = str(fpath.joinpath(fname))
        ops.recorder(
        "Node",
        "-file", fout,
        "-time",
        "-nodeRange", *nodes_range,
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
            "-eleRange", *elements_range,
            "material", gpt,
            "stress",
        )
        fname = fname_prefix + "_strain" + gpt + ".out"
        fout = str(fpath.joinpath(fname))
        ops.recorder(
            "Element",
            "-file", fout,
            "-time",
            "-eleRange", *elements_range,
            "material", gpt,
            "strain",
        )
    # fmt: on


def slope_stability_analysis(fid_dict, fpath_rec, matprop, eleprop):
    # wipe previous analyses
    ops.wipe()

    # read the nodes file
    nodes = read_nodes(fid_dict["nodes"])
    elements = read_quadelements(fid_dict["elements"])

    # corner nodes are 2D with 2 DOF (displacements in x1 and x2)
    ops.model("basic", "-ndm", 2, "-ndf", 2)
    # print(f"Data recorders: ")

    # PVD recorder
    # ops.recorder("PVD", str(fpath_rec), "disp")

    # node and element recorders
    data_recorders(
        fpath_rec,
        fpath_rec.name,
        [min([*nodes.keys()]), max([*nodes.keys()])],
        [min([*elements.keys()]), max([*elements.keys()])],
    )

    # create the nodes
    for node_id, xycrds in nodes.items():
        ops.node(node_id, *xycrds[:2])
    # the number of nodes created
    # print(f"Number of nodes created: {len(ops.getNodeTags())}")
    # number of nodes created
    # print(f"Number of nodes in the mesh: {len(nodes.keys())}")

    # boundary conditions for the base nodes, 0 = do not fix, 1 = fix
    # fix means displacement = 0
    basedofs = [1, 1]
    base_nodes = get_tagged_nodes(
        fid_dict["tags"], "Start_tag:Fix_110", "End_tag:Fix_110"
    )

    # print(f"Fix base nodes:")
    fix_nodes_bound(base_nodes, basedofs)

    # fix the left boundary in x-direction dofs = [1, 0]
    left_bound_dofs = [1, 0]
    left_boundary_nodes = get_tagged_nodes(
        fid_dict["tags"], "Start_tag:Fix_100", "End_tag:Fix_100"
    )
    # there could be overlapping nodes among the boundary conditions
    # check the tags file carefully and remove nodes that have already
    # been assigned boundary condition, for example in this particular case
    # Node 1, has to be removed from the left boundary as it is part of the base
    # this can be done manually or programatically
    left_boundary_nodes = list(set(left_boundary_nodes) - set(base_nodes))
    # print(f"Fix left boundary nodes:")
    fix_nodes_bound(left_boundary_nodes, left_bound_dofs)
    # print(f"Created all boundary conditions:")

    # print(f"Define Drucker-Prager material:")

    # number of dimensions (nd) 2 for plain-strain 3 for 3D
    ops.nDMaterial(
        matprop["material_type"],
        matprop["material_tag"],
        matprop["bulk_modulus"],
        matprop["shear_modulus"],
        matprop["sigmay"],
        matprop["rho"],
        matprop["rhobar"],
        matprop["kinf"],
        matprop["ko"],
        matprop["delta1"],
        matprop["delta2"],
        matprop["hard"],
        matprop["theta"],
        matprop["density"],
    )
    # print(f"Soil material created")

    create_elements(elements, eleprop)
    # print(f"All soil elements created")

    # save the initial state
    ops.record()
    # data_recorders(
    #     fpath,
    #     fname_prefix,
    #
    # )

    # setup analysis
    # ops.constraints("Penalty", 1.0e20, 1.0e20)
    ops.constraints("Plain")
    ops.test("NormDispIncr", 1e-4, 100, 2)
    ops.algorithm("KrylovNewton")
    # ops.algorithm("Newton")
    ops.numberer("RCM")
    ops.system("ProfileSPD")
    ops.integrator("LoadControl", 1)
    ops.analysis("Static")

    # not sure about this,
    two_stage_gravity = False
    if two_stage_gravity:
        # print(f"Gravity analysis:")
        # update material stage to 0 for elastic behavior,
        ops.updateMaterialStage("-material", eleprop["material_tag"], "-stage", 0)
        # print(f"Material updated for elastic behavior during gravity loading")
        # gravity loading
        analysis_res = ops.analyze(1)
        # print(f"Elastic gravity analysis over")
        # update material stage to include plastic analysis
        ops.updateMaterialStage("-material", eleprop["material_tag"], "-stage", 1)

    analysis_res = ops.analyze(1)
    # if analysis_res < 0:
    #     print("Regular Newton failed.. try initial stiffness for this step")
    #     ops.test("NormDispIncr", 1.0e-12, 1000)
    #     ops.algorithm("ModifiedNewton", "-initial")
    #     analysis_res = ops.analyze(1)
    # if analysis_res == 0:
    #     print("Modified Newton worked, now back to regular Newton")
    #     ops.test("NormDispIncr", 1.0e-12, 1000)
    #     ops.algorithm("Newton")
    # print(f"Plastic gravity analysis over\n")
    niter = ops.numIter()
    ops.wipe()

    return analysis_res, niter


def main():
    # file path and filenames
    path_root = Path(r"../")
    path_data = path_root / "data"
    path_msh = path_root / "gmsh"
    path_pvd = path_root / "pvd"

    # name of the nodes file
    fname_nodes = "griffiths_and_lane_1999_ex2_nodes.txt"
    fnodes = path_msh.joinpath(fname_nodes)
    # name of the elements file
    fname_elements = "griffiths_and_lane_1999_ex2_elements.txt"
    felements = path_msh.joinpath(fname_elements)
    # name of the files with fixities written
    fname_tags = "griffiths_and_lane_1999_ex2_tags.txt"
    ftags = path_msh.joinpath(fname_tags)

    # dictionary of fids relating to various files that is either read or written
    fid_dict = {"nodes": fnodes, "elements": felements, "tags": ftags}

    # acceleration due to gravity [m/s2]
    accg = 9.81
    # acceleration due to gravity in the x and y direction
    wgt_x = 0.0
    wgt_y = -accg

    # material properties
    # Young's modulus (kPa)
    modE = 1e5
    # Poisson's ratio of the soil
    nu = 0.3
    # soil shear modulus from Young's modulus [kPa]
    modG = modE / (2 * (1 + nu))
    # soil bulk modulus [kPa]
    modK = modE / (3 * (1 - 2 * nu))
    # soil saturated density, or soil mass density  [Mg/m3] equivalent [1 Mg/m3 = 10 kN/m3]
    soil_density = 2.0
    # soil friction angle, phi of Mohr-Coulomb failure envelop [deg]
    friction_angle = 20.0
    # the undrained shear strength, c of Mohr-Coulomb failure envelop [kPa]
    cohesion = 10.0
    # related to dilation? controls evolution of plastic volume change, 0 ≤ $rhoBar ≤ $rho
    rhobar = 0.0
    # nonlinear isotropic strain hardening parameter, $Kinf ≥ 0
    kinf = 0.0
    # nonlinear isotropic strain hardening parameter, $Ko ≥ 0
    ko = 0.0
    # nonlinear isotropic strain hardening parameter, $delta1 ≥ 0
    delta1 = 0.0
    # tension softening parameter, $delta2 ≥ 0
    delta2 = 0.0
    # linear strain hardening parameter, $H ≥ 0
    hard = 0.0
    # controls relative proportions of isotropic and kinematic hardening, 0 ≤ $theta ≤ 1
    theta = 0.0
    # print(f"Soil elastic properites:")
    # print(f"G: {modG/1000:6.1f} MPa, E: {modE/1000:6.1f} MPa, K: {modK/1000:6.1f} MPa")

    # material type and tag for soil
    soil_mattype = "DruckerPrager"
    soil_mattag = 1
    # material prop dictionary
    matprop = {
        "material_type": soil_mattype,
        "material_tag": soil_mattag,
        "bulk_modulus": modK,
        "shear_modulus": modG,
        "sigmay": 0.0,
        "rho": 0.0,
        "rhobar": rhobar,
        "kinf": kinf,
        "ko": ko,
        "delta1": delta1,
        "delta2": delta2,
        "hard": hard,
        "theta": theta,
        "density": soil_density,
    }

    # soil element thickness
    thickness = 1.0
    # analysis type, "PlaneStrain" or "PlaneStress"
    analysis_type = "PlaneStrain"
    # surface pressure on elements
    surface_pressure = 0.0
    # element type, 4 node quadrilateral
    eletype = "quad"
    # element property dictionary
    eleprop = {
        "element_type": eletype,
        "thickness": thickness,
        "analysis_type": analysis_type,
        "material_tag": soil_mattag,
        "bulk_modulus": modK,
        "surface_pressure": surface_pressure,
        "density": 0.0,
        "b1": wgt_x,
        "b2": wgt_y,
    }

    # filename prefix to store pvd data
    fnameprefix = "fs_"
    fss = np.linspace(1, 2.0, 11)
    # print(fss)
    fss = [0.8] + list(fss)
    # fss = [str(fs).replace(".", "").ljust(5, "0") for fs in fss]
    fnames_fs = [
        fnameprefix + str(round(fs, 5)).replace(".", "").ljust(5, "0") for fs in fss
    ]

    # factored parameters
    cs, phis = factored_strength_params(cohesion, friction_angle, np.array(fss))

    # convert to MC, c, phi to DP sigmay and rho
    sigmays, rhos = mc2dp(cs, phis)

    # file to save some iteration parameters
    fname_log = fnameprefix + "log.txt"
    fflog = path_data.joinpath(fname_log)
    fidlog = open(fflog, "w")
    print(
        f"{'FS':6s}, {'C':6s}, {'phi':6s}, {'num_iter':10s}, {'analysis':10s}",
        file=fidlog,
    )
    for fs, fname_fs, sigma_y, rho, c, phi in zip(
        fss, fnames_fs, sigmays, rhos, cs, phis
    ):
        path_fs = path_data / fname_fs
        path_fs.mkdir(parents=True, exist_ok=True)
        matprop["sigmay"] = sigma_y
        matprop["rho"] = rho
        fpath_rec = path_fs
        analysis_result, niter = slope_stability_analysis(
            fid_dict, fpath_rec, matprop, eleprop
        )
        print(
            f"{fs:6.3f}, {c:6.2f}, {phi:6.2f}, {niter:10d}, {analysis_result:10d}",
            file=fidlog,
        )
        if analysis_result < 0:
            break
        # time.sleep(2)
    fidlog.close()


if __name__ == "__main__":
    main()
>>>>>>> 1dcon
