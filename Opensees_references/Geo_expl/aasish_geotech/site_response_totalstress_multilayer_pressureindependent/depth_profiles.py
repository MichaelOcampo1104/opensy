#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import pandas as pd
from pathlib import Path


# Description: create depth profiles of accelerations, velocities
# and displacements. These profiles are created at the timestep when
# these quantities are maximum and the timesteps in the three may not be
# the same.


def get_nodes_timestep_values(fpath, ndofs, nodetags, dof, timestep):
    """Get the data for the list of nodes for ndof and at specified timestep
    fpath: full path including the filename of the output file
    ndofs: number of variables or dofs reported at each node 
    nodetags: a list of nodetags at which data is desired
    dof: the dof of the variable required in the depth profile 
    timestep: timestep at which the values for the nodes are required
    return arrays of requested data
    """

    # read acceleration data
    # How is the data arranged? the first column is dt
    # Then the following columns are accelrations for
    # node1_dof1, node1_dof2, node2_dof1, node2_dof2 and so on
    # for the number of nodes
    data = np.loadtxt(fpath)
    # number of rows (number of timesteps) and columns (number of nodes x ndf)
    # nr, nc = data.shape
    # print(f"Shape of data: {nr} {nc}")

    # first create the timestep column from the data
    # dts = data[:, 0]
    # all the columns except the first timestep column
    data = data[:, 1:]
    # number of rows (number of timesteps) and columns (number of nodes x ndf)
    # nr, nc = data.shape
    # print(f"Shape of data: {nr} {nc}")

    # transposing makes it easy to manipulate data
    data = data.T
    # Check if it is really the timestep column,
    # comment this line if not needed
    # print(
    # f"Shape of the time steps: {dts.shape}, Average dt: {np.mean(np.diff(dts))} s"
    # )

    # number of rows (number of timesteps) and columns (number of nodes x ndf)
    nr, nc = data.shape
    # print(f"Shape of data: {nr} {nc}")

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
    # print(f"Number of nodes: {nnodes}")
    data = np.reshape(data, (nnodes, ndofs, nc))
    fr, nr, nc = data.shape
    print(
        f"Shape of data: Frame (nodes): {fr}, Rows (dofs): {nr}, Columns (timesteps): {nc}"
    )

    # indices of the maximum value on the ground surface
    nodetag = max(nodetags)
    print(f"The top most node: {nodetag}")

    ndata = data[nodetag, dof]
    print(f"Shape of the node data {data.shape}")
    # # indices of the maximum value in the data
    # # ref: np.unravel_index(np.argmax(a, axis=None), a.shape)
    # fridx, nridx, ncidx = np.unravel_index(np.argmax(np.abs(data), axis=None), (nodetag, dof, nc))
    ncidx = np.argmax(ndata)
    print(f"Maximum value timestep index: {ncidx}")

    # # 0 array indexing, therefore where nodetag is n then index is n - 1
    # # 3D data [frames, row, column]
    # # frames = nodes
    # # and due to Transpose
    # # row = dofs 0: dof = 1, and 1: dof = 2
    # # column: timesteps
    # # the "-1" is for zero node indexing
    return data[nodetags - 1, dof, ncidx]


def main():
    # paths and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"

    # filenames and paths
    fname_acc = "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_accel.out"
    fname_vel = "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_vel.out"
    fname_disp = "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_disp.out"
    fnames = [fname_acc, fname_vel, fname_disp]

    fname_dp = "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_depthprofiles.csv"
    f_dp = path_data.joinpath(fname_dp)

    # time step of data [s]
    dt = 0.005

    # accelaration due to gravity [m/s2]
    accg = 9.81

    # degrees of freedom in the analysis ndof
    ndofs = 2
    number_of_nodes = 302
    # node for output, left corner nodes, [1, 3, 5, ...]
    # number of elements = nx and there are nx + 1 nodes in a row
    nx = 1
    nodetags = np.arange(1, number_of_nodes, nx + 1)
    # dof of interest, 0: x-direction, 1: y-direction
    dof = 0
    # depth profile at the end of simulation
    timestep = -1
    # element size in the y direction
    ly = 0.2
    data = []
    for fname in fnames:
        print(f"Filename: {fname}")
        fin = path_data.joinpath(fname)
        dp = get_nodes_timestep_values(fin, ndofs, nodetags, dof, timestep)
        data.append(dp)

    # element size in y-direction is ly and there are nnodes-1 elements
    zs = np.cumsum(np.full_like(nodetags[1:], 0.2, dtype=np.double))
    zs = np.insert(zs, 0, 0)[::-1]

    # create a pandas dataframe and then write the value to files
    df = pd.DataFrame()
    df["z [m]"] = zs
    df["acc [g]"] = data[0]
    df["vel [m/s]"] = data[1]
    df["disp [m]"] = data[2]
    df.to_csv(f_dp, index=False)


if __name__ == "__main__":
    main()
    # cProfile.run('main()')
