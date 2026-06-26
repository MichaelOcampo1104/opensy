#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Description: create depth spectrum of accelerations, velocities
# and displacements

# Font settings
plt.rc("font", **{"family": "sans-serif", "sans-serif": ["DejaVu Sans"]})
# plt.rc('font', **{'family': 'serif', 'serif': ['Times New Roman']})
params = {
    "axes.labelsize": 12,
    "font.size": 12,
    "legend.fontsize": 12,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    # use Tex to render all fonts
    "text.usetex": True,
    "axes.unicode_minus": True,
}
plt.rcParams.update(params)

# Close all open figures
plt.close("all")


def get_nodes_timestep_values(fpath, ndofs, nodetags, dof, tidxs):
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
    nodetag = np.max(nodetags)
    print(f"The top most node: {nodetag}")

    # ndata = data[nodetag, dof]
    # print(f"Shape of the node data {data.shape}")
    # # # indices of the maximum value in the data
    # # # ref: np.unravel_index(np.argmax(a, axis=None), a.shape)
    # # fridx, nridx, ncidx = np.unravel_index(np.argmax(np.abs(data), axis=None), (nodetag, dof, nc))
    # ncidx = np.argmax(ndata)
    # maxval = np.max(ndata)
    # print(f"Maximum value timestep index: {ncidx}, maximum value: {maxval}")

    # # 0 array indexing, therefore where nodetag is n then index is n - 1
    # # 3D data [frames, row, column]
    # # frames = nodes
    # # and due to Transpose
    # # row = dofs 0: dof = 1, and 1: dof = 2
    # # column: timesteps
    # # the "-1" is for zero node indexing
    return data[nodetags - 1, dof, :][:, tidxs]
    # print(f"Shape of data: {data.shape}")


def main():
    # paths and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"
    path_plt = path_root / "plt"

    # filenames and paths
    fname_acc = "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_accel.out"
    fname_vel = "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_vel.out"
    fname_disp = "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_disp.out"
    fnames = [fname_acc, fname_vel, fname_disp]

    fname_fig = "ex_g_02_sitereponse_multilayer_pressureindependent_totalstress_depthspectrum.png"
    ffig = path_plt.joinpath(fname_fig)

    # time step of data [s]
    dt = 0.005

    # accelaration due to gravity [m/s2]
    accg = 9.81

    # element size in y direction
    ly = 0.20
    # degrees of freedom in the analysis ndof
    ndofs = 2
    number_of_nodes = 302
    # node for output, left corner nodes, [1, 3, 5, ...]
    # number of elements = nx and there are nx + 1 nodes in a row
    nx = 1
    nodetags = np.arange(1, number_of_nodes, nx + 1)
    # dof of interest, 0: x-direction, 1: y-direction
    dof = 0
    # indices of timesteps in the spectrum
    tstart = 0
    tend = 12
    ntsteps = int((tend - tstart) / dt)
    # tidxs = np.linspace(tstart, tend, ntsteps + 1)
    tidxs = np.arange(0, ntsteps + 1)

    # element size in y-direction is ly and there are nnodes-1 elements
    # y: depths, x: timesteps
    zs = np.cumsum(np.full_like(nodetags[1:], ly, dtype=np.double))
    y = np.insert(zs, 0, 0)[::-1]
    x = np.linspace(0, tend, ntsteps + 1)

    # figure
    figscale = 1.0
    figw = 3.847 * 3
    figh = 3.847
    figsz = (figscale * figw, figscale * figh)
    fig, axs = plt.subplots(1, 3, figsize=figsz, sharey=True)
    axs = axs.ravel()

    xlbls = [
        r"$\left| \ddot{u}\right|$ [g]",
        r"$\left| \dot{u} \right|$ [m/s]",
        r"$\left| u \right|$ [m]",
    ]
    for idx, (ax, fname) in enumerate(zip(axs, fnames)):
        print(f"Filename: {fname}")
        fin = path_data.joinpath(fname)
        data = get_nodes_timestep_values(fin, ndofs, nodetags, dof, tidxs)
        # the dt for maximum value, the values for maxmum acceleration, velocity,
        # and displacement may not be the same
        mc = np.argmax(data[-1, :])
        tmax = mc * dt
        print(f"Max column {mc}, time: {tmax}, value: {data[-1, mc]}")
        # use absolute values
        z = np.abs(data)
        if "accel" in fname:
            z = z / accg

        zmin, zmax = 0, np.abs(z).max()
        c = ax.pcolormesh(x, y, z, cmap="Oranges", vmin=zmin, vmax=zmax)
        ax.axis([x.min(), x.max(), y.min(), y.max()])
        ax.invert_yaxis()
        ax.plot(
            [tmax, tmax], [y.min() + 0.8 * y.max(), 0.90 * y.max()], ls="-", color="k"
        )
        ax.set_xlabel(r"$\Delta t$ [s]")
        ax.grid(b=True, which="major", axis="both", ls=":", color="green", alpha=0.4)
        fig.colorbar(c, label=xlbls[idx], ax=ax, pad=0.020)

    axs[0].set_ylabel(r"Depth $z$ [m]")

    fig.savefig(ffig, ext="png", dpi=150, bbox_inches="tight")


if __name__ == "__main__":
    main()
    # cProfile.run('main()')
