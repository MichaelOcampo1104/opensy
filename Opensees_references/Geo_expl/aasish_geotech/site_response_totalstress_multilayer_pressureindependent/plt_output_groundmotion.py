#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
from scipy import integrate
from pathlib import Path
import matplotlib.pyplot as plt


# Description: Plot the acceleration, velocity and displacement time histories from the
# output file. In this file the surface accelerations, velocities and displacements from the analysis
# performed with .py file is also compared with those from the example .tcl file downloaded from the
# opensees example section
# ref: https://opensees.berkeley.edu/wiki/index.php/Site_Response_Analysis_of_a_Layered_Soil_Column_(Total_Stress_Analysis)
# Example: freeFieldSingle.tcl

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


def get_data(fpath, ndof, nodetag):
    """Get the data from output file for the given node
    fpath: full path including the filename of the output file
    ndof: number of variables or dofs reported at each node
    nodetag: the node number at which data is desired
    return 1d arrays of timestep and the requested variable
    """

    # read outdata
    # How is the data arranged? the first column is dt
    # Then the following columns are accelrations for
    # node1_dof1, node1_dof2, node2_dof1, node2_dof2 and so on
    # for the number of nodes
    data = np.loadtxt(fpath)

    # first create the timestep column from the data
    dts = data[:, 0]
    data = data[:, 1:]
    data = data.T
    # Check if it is really the timestep column,
    # comment this line if not needed
    # print(
    #     # f"Shape of the time steps: {dts.shape}, Average dt: {np.mean(np.diff(dts))} s"
    # )

    # number of rows (number of timesteps) and columns (number of nodes x ndf)
    nr, nc = data.shape
    print(f"Shape of data: {nr} {nc}")

    # todo: write a better explanation of reshaping the data, a separate document with easily to understand explanations
    # reshape 2D array data into 3D array data, where the depth frames are the different nodes
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
    # each row contains values for different time shape for ndf
    # due to transpose the values are row wise instead of column wise
    # so instead of [[0, 1], [4, 5], [8, 9]] in the first frame for node1 we get
    # [[0, 4, 8], [1, 5, 9]] due to transpose.
    # after removing the time step column the first column,
    # the number of columns = number of nodes * ndofs (or the number variables reported per node)
    nnodes = int(nr / ndof)
    print(f"Number of nodes: {nnodes}")
    data = np.reshape(data, (nnodes, ndof, nc))
    fr, nr, nc = data.shape
    print(
        f"Reshaped of data: Frame (nodes): {fr}, Rows (dofs): {nr}, Columns (timesteps): {nc}"
    )

    # 0 array indexing, therefore when nodetag is n, then index is n - 1
    adata = data[nodetag - 1, 0, :]

    return dts, adata


def main():
    # paths and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"
    path_plt = path_root / "plt"
    path_orisol = path_root / "original_solution"

    # filenames for [acceleration, velocity, displacement] from the python Openseespy file I created
    fnames = [
        "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_accel.out",
        "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_vel.out",
        "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_disp.out",
    ]
    # these are output from the Opensees example totalstress site reponse analysis
    # ref: https://opensees.berkeley.edu/wiki/index.php/Site_Response_Analysis_of_a_Layered_Soil_Column_(Total_Stress_Analysis)
    # Tcl file: freeFieldSingle.tcl
    fnames_ori = ["acceleration.out", "velocity.out", "displacement.out"]

    # plot all three figures in the same plot, filename
    fname_fig = "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_surface_groundmotion.png"

    ffig = path_plt.joinpath(fname_fig)

    # accelaration due to gravity [m/s2]
    accg = 9.81

    # number of dof or number of variables per node
    ndof = 2

    # output node for ground surface acceleration: the right ground surface node
    nodetag = 301

    # figure
    figscale = 1.5
    figw = 3.847
    figh = 2 * figw / 1.618
    figsz = (figscale * figw, figscale * figh)
    fig, axs = plt.subplots(3, 1, figsize=figsz, sharex=True)
    axs = axs.ravel()

    for ax, fname, fname_ori in zip(axs, fnames, fnames_ori):
        print(f"Filename: {fname}")
        fpth_ori = path_orisol.joinpath(fname_ori)
        fpth = path_data.joinpath(fname)
        dts, data = get_data(fpth, ndof, nodetag)
        dts_ori, data_ori = get_data(fpth_ori, ndof, nodetag)
        print(dts.shape, data.shape)
        if "accel" in fname:
            print(f"Change to gs")
            data = data / accg
            data_ori = data_ori / accg
        ax.plot(
            dts,
            data,
            ls="-",
            alpha=0.5,
            # label=r".py, KrylovNewton, dt=0.005s, Tol=1e-6",
            label="OpenSeesPy"
        )
        ax.plot(
            dts_ori,
            data_ori,
            ls="-",
            alpha=0.5,
            # label=r".tcl, Newton, dt=0.005s, Tol=1e-3",
            label="OpenSees"
        )

    # xaxis label
    axs[-1].set_xlabel(r"$\Delta t$ [s]")

    # legends
    axs[0].legend(frameon=False, loc="upper right")

    # yaxis labels
    yaxis_labels = [r"$\ddot{u}$ [g]", r"$v$ [m/s]", r"$u$ [m]"]

    for ax, ylbl in zip(axs, yaxis_labels):
        ax.set_ylabel(ylbl)
        ax.grid(b=True, which="major", axis="both", ls=":", color="k", alpha=0.4)

    fig.savefig(ffig, ext="png", dip=150, bbox_inches="tight")


if __name__ == "__main__":
    main()

