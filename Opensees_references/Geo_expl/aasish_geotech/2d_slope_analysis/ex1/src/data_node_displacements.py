#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import pandas as pd
from pathlib import Path


# Description: Plot displacements time-history of the given nodes


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


def get_timesteps(fpath):
    """Get the data from output file for the given node, return the desired data for 
    fpath: full path including the filename of the output file
    return 1d arrays of timesteps
    """
    # read acceleration data
    # How is the data arranged? the first column is dt
    # Then the following columns are accelrations for
    # node1_dof1, node1_dof2, node2_dof1, node2_dof2 and so on
    # for the number of nodes
    data = np.loadtxt(fpath)

    # first create the timestep column from the data
    return data[:, 0]


def get_nodalvalues(fpath, ndofs, nodetag, data_dof):
    """Get the data from output file for the given node, return the desired data for 
    fpath: full path including the filename of the output file
    ndofs: number of variables or dofs reported at each node
    nodetag: the node number at which data is desired
    data_dof: the dof of the desired data data_dof = 1 is x-dir data, data_dof = 2 is y-dir data and so on
    only one dof per call
    return 1d array and the requested variable
    """

    # read acceleration data
    # How is the data arranged? the first column is dt
    # Then the following columns are accelrations for
    # node1_dof1, node1_dof2, node2_dof1, node2_dof2 and so on
    # for the number of nodes
    data = np.loadtxt(fpath)

    # first create the timestep column from the data
    # dts = data[:, 0]
    # all the columns except the first timestep column
    data = data[:, 1:]

    # transposing makes it easy to manipulate data
    data = data.T
    # Check if it is really the timestep column,
    # comment this line if not needed
    # print(
    # f"Shape of the time steps: {dts.shape}, Average dt: {np.mean(np.diff(dts))} s"
    # )

    # number of rows (number of timesteps) and columns (number of nodes x ndf)
    nr, nc = data.shape
    print(f"Shape of data without the timestep: {nr} {nc}")

    # reshape 2D array data into 3D array data, where the depth frames are the different nodes
    # two nodes and two dofs per node (4 columns) and three time steps (number of rows)
    # e.g if a = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]
    # for easier grouping using transpose b = a.T => [[ 0  4  8], [ 1  5  9], [ 2  6 10], [ 3  7 11]]
    # reshape d = np.reshape(b, (2, 2, 3)) where (nf, nc, nr) nf = number of frames
    # nc = number of columns, nr is the number of rows =>
    # [[[ 0  4  8]
    #    [ 1  5  9]]
    #
    # [[ 2  6 10]
    #    [ 3  7 11]]]
    # so in the above, assume the data for two nodes with ndf=2 and three timesteps so we want
    # to group [[0, 1], [4, 5], [8, 9]] in the first frame for node1
    # and [[2, 3], [6, 7], [10, 11]] in the second frame for node2
    # each row contains values for different time step for ndf
    # due to transpose the values are rowwise instead of column wise
    # so instead of [[0, 1], [4, 5], [8, 9]] in the first frame for node1 we get
    # [[0, 4, 8], [1, 5, 9]] due to transpose.
    # after removing the time step column the first column,
    # the number of columns = number of nodes * ndofs (or the number variables reported per node)
    nnodes = int(nr / ndofs)
    print(f"Number of nodes: {nnodes}")
    data = np.reshape(data, (nnodes, ndofs, nc))
    fr, nr, nc = data.shape
    print(
        f"Shape of acceleration vector: Frame (nodes): {fr}, Rows (dofs): {nr}, Columns (timesteps): {nc}"
    )

    # 0 array indexing, therefore where nodetag is n then index is n - 1
    # 3D data [frames, row, column]
    # frames = nodes
    # and due to Transpose
    # row = dofs 0: dof = 1, and 1: dof = 2
    # column: timesteps
    return data[nodetag - 1, data_dof, :]


def main():

    path_root = Path(r"../")
    path_data = path_root / "data"
    path_plt = path_root / "plt"

    fname_disp = "2ddex1_disp.out"
    fname_out = "2ddex1_nodedisp_out.csv"

    fdisp = path_data.joinpath(fname_disp)
    fout = path_data.joinpath(fname_out)

    # number of dofs in the nodal data
    ndofs = 2
    # node number
    # nodetags = [264, 449, 909]
    nodetags = [5, 80, 6, 108]
    # horizontal
    data_dof = 0

    data_dict = {}
    data_dict.update({"dts": list(get_timesteps(fdisp))})
    for nodetag in nodetags:
        print(f"Getting data for node: {nodetag}")
        data_dict.update(
            {
                "Node_"
                + str(nodetag): list(get_nodalvalues(fdisp, ndofs, nodetag, data_dof))
            }
        )

    df = pd.DataFrame(data_dict)
    df.to_csv(fout, index=False)


if __name__ == "__main__":
    main()
