#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
from pathlib import Path
import meshio


def read_nodes4vtk(fpath):
    """Read nodes tags and coordinates from file
    fpath: path to the nodes file
    Return: a dictionary {node_id: [x, y, x]} datatypes {int: [float, float, float]}"""
    datatypes = [int, float, float, float]
    data = []
    with open(fpath, "r") as f:
        lines = f.readlines()
    lines = lines[2:]
    for line in lines:
        vals = line.strip(",\n").split(",")
        pvals = [datatype(val.strip()) for val, datatype in zip(vals, datatypes)]
        data.append(pvals[1:4])
    return np.array(data)


def read_quadelements4vtk(fpath):
    """Read nodes tags and coordinates from file, 4 node Quad elements
    fpath: path to the nodes file
    Return: a dictionary {node_id: [x, y, x]} datatypes {int: [float, float, float]}"""
    datatypes = [int, float, float, float, float, str, str]
    data = []
    with open(fpath, "r") as f:
        lines = f.readlines()
    lines = lines[2:]
    for line in lines:
        vals = line.strip(",\n").split(",")
        pvals = [datatype(val.strip()) for val, datatype in zip(vals, datatypes)]
        data.append(pvals[1:5])
    return {"quad": (np.array(data) - 1).astype(int)}


def reshape_recorder_data(data, ndofs):
    """Reshape 2D numpy ndarray (recorder data) into 3D numpy ndarray with 
    time step as the frames, nodes as rows and node values as columns,
    data[timestep, nodes, ndofs].
    data[0] gives the first time step data, and data[1] gives the second timestep,
    data[0, :, 0] gives dof = 1 values at all the nodes for the first timestep"""

    # first create the timestep column from the data
    # dts = data[:, 0]
    # all the columns except the first timestep column
    data = data[:, 1:]

    # number of rows (number of timesteps) and columns (number of nodes x ndf)
    nr, nc = data.shape
    print(
        f"Shape of time steps (nrows): {nr}, node data (number of nodes x ndof per node): {nc}"
    )

    return np.reshape(data, (nr, int(nc / ndofs), ndofs))


def recorder_data(fpath, ndofs):
    """Read the output file written by the OpenSees recorders
    Seems like all recorders follow the same format
    fpath: complete path to the input file
    ndofs: number of degrees of freedom per node, how many variables are written per node"""
    # How is the recorder data arranged?
    # if there are two dofs (dof = *[1, 2]) per node and there are three nodes and 2 timesteps
    # 0 n1dof1 n1dof2 n2dof1 n2dof2 n3dof1 n3dof2
    # 1 n1dof1 n1dof2 n2dof1 n2dof2 n3dof1 n3dof2
    # the first column is the timestep and rest are the values for the dof for the variable choosen
    # e.g. displacements, then n1dof1 and n1dof2 are 1-direction (x), 2-direction (y) displacements
    # at node 1
    data = np.loadtxt(fpath)

    return reshape_recorder_data(data, ndofs)


def average_element_data(fpaths):
    """Read output file for each of the Gauss points and return averaged strain at the centroid
    fpaths a list of path objects of the files that need to be read
    Return: ndarray of the average of the values in the file
    """
    number_of_files = len(fpaths)
    data = np.loadtxt(fpaths[0])
    dshape = data.shape
    if number_of_files > 1:
        for fpath in fpaths[1:]:
            ndata = np.loadtxt(fpath)
            if ndata.shape == dshape:
                data += ndata
            else:
                raise ValueError(f"The shapes of {fname} is different:")

    return data / number_of_files


def displacementxy_dict(fpath, timestep, ndofs):
    """Read node displacements and return a dictionary for meshio point data for vector
    fpath: path to the displacement file
    timestep: timestep for which the data is required
    ndofs: number of dofs per each node in the output file
    Return: a dictionary {"Displacement": np.c_[disp1, disp2]} where disp1 and disp2 are 1d array
    of displacement for a particular dof (e.g. disp1 is for dof=1) for all the nodes and likewise
    for disp2
    """
    fpath = list(fpath.glob("*disp.out"))
    # read the node displacement output file from OpenSees
    node_data = recorder_data(fpath[0], ndofs)
    # dof = 1 (index 0) displacement is first column, dof = 2 (index 1) is the second column
    # for vector data pass in a 2D array with 3 columns for X, Y, Z,
    # if two column 2D array is passed meshio adds the third column of zeros
    return {"Displacement": np.c_[node_data[timestep, :, 0], node_data[timestep, :, 1]]}


def element_data(fpath, vartype, timestep, ndofs):
    """Read element data and return a dictionary for meshio cell data
    fpath: path of the data folder
    vartype: type of variable to read and return, this string is used to create the pattern used
             to search for files containing this data type 
    timestep: timestep for which the data is required
    ndofs: number of dofs per each node in the output file
    Return: a 2d array with data for the requested variable (vartype) for the given timestep
    e.g. if ndofs = 2, the returned array is a 2D array with columnar variables
    """
    # create search pattern
    search_pattern = "*" + vartype + "?.out"
    fpaths = list(fpath.glob(search_pattern))
    # assemble Gauss points strain files, and average the Gauss points stresses
    # to computed one stress value per element centroid
    data = average_element_data(fpaths)
    data = reshape_recorder_data(data, ndofs)
    # point_data["strain"] = strain[1]
    return data[timestep]


def main():

    path_root = Path(r"../")
    path_msh = path_root / "gmsh"
    path_data = path_root / "data"

    fname_nodes = "griffiths_and_lane_1999_example_1_nodes.txt"
    fname_elements = "griffiths_and_lane_1999_example_1_elements.txt"
    fname_out = "griffiths_and_lane_1999_example_1.vtk"
    fname_disp = "fs_08000disp.out"
    fname_strain1 = "fs_08000_strain1.out"
    # fnames_in= path_data.glob("*strain?.out")

    fnodes = path_msh.joinpath(fname_nodes)
    felements = path_msh.joinpath(fname_elements)
    fdisp = path_data.joinpath(fname_disp)
    fstrain1 = path_data.joinpath(fname_strain1)
    fout = path_msh.joinpath(fname_out)

    points = read_nodes4vtk(fnodes)
    number_of_nodes = len(points)
    print(f"Number of nodes: {number_of_nodes}")
    cells = read_quadelements4vtk(felements)
    number_of_elements = len(cells["quad"])
    print(f"Number of elements: {number_of_elements}")

    # get all the factor of safety data directories, igore the last one which failed to converge
    fsdirs = [fsdir for fsdir in path_data.glob("*/") if fsdir.is_dir()][:-1]

    # number of dofs in the nodal data
    nndofs = 2
    # number of time steps for this problem 2, 0 and 1
    # we are interested in time step 1 which is the end of load application
    timestep = 1
    # Average stress per element by average four integartion point stresses,
    # for 2D quad elements the element recorder for stress returns sigma1, sigma2, sigma12?, there ndofs=3
    # only consider data at the end of loading for each FS, therefore timestep = 1
    vartypes = ["stress", "strain"]
    endofs = 3

    for fsdir in fsdirs:
        print(fsdir.stem)
        # create vtk filename
        fout = path_data.joinpath(fsdir.stem + ".vtk")
        cell_data = {}
        point_data = displacementxy_dict(fsdir, timestep, nndofs)

        for vartype in vartypes:
            edata = element_data(fsdir, vartype, timestep, endofs)
            cell_data.update({vartype.title(): edata})

        meshio.write_points_cells(
            fout,
            points,
            cells,
            # Optionally provide extra data on points, cells, etc.
            point_data=point_data,
            cell_data=cell_data,
            # field_data=field_data
        )


if __name__ == "__main__":
    main()
