#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Description: plot vertical effective stress with depth
# 1D consolidation double drainage
# Units: kN, m, sec

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


def main():
    # file path and filenames
    path_root = Path(r"../")
    path_data = path_root / "data"
    path_plt = path_root / "plt"

    fname_in = "1dcon_stress_doubledrainage.txt"
    fname_fig = "1dcon_stress_doubledrainage.png"
    fin = path_data.joinpath(fname_in)
    ffig = path_plt.joinpath(fname_fig)

    # center offset from the bottom left of the page (origin of the page, origin transformed)
    ox = 0.0
    oy = 0.0

    # size of elements in x and y direction of the nodes
    lx = 1.0
    ly = 1.0

    # number of element in x and y direction
    nx = 1
    ny = 10

    # number of stress output for each element
    nstress = 5

    # For 2D problems, the stress output follows this order: σxx, σyy, σzz, σxy, ηr, where ηr
    # is the ratio between the shear (deviatoric) stress and peak shear strength at the current
    # confinement (0<=ηr<=1.0). The strain output follows this order: εxx, εyy, γxy.
    # output file: stress components for integration point 9 in every element for each time step
    df = pd.read_csv(fin, delimiter=" ")
    nrows, ncols = df.shape
    print(f"Number of rows and columns in OpenSees output file: {nrows}, {ncols}")
    # nstress = number of stress components reported per integration point
    # nele = number of elements
    nele = int(ncols / nstress)
    print(f"Number of elements: {nele}")
    # remove the dt columns and convert into numpy array (ntimesteps, nstress * nele)
    #
    data = df.iloc[:, 1:].values

    # reshape data
    data = np.reshape(data, (nrows, nele, nstress))
    # print(f"Data: {data}")
    ns, nr, nc = data.shape
    print(
        f"Reshaped data: Number of time steps: {ns}, Number of depth rows: {nr}, Number of stress columns: {nc}"
    )

    vstress = data[:, :, 1]
    # hstress = data[:, :, 0]
    print(f"Vertical stress: {vstress.shape}")
    # create for depth
    soil_depth = ny * ly
    depths = np.linspace(soil_depth - ly / 2, 0 + ly / 2, ny)
    print(f"Depth check: {depths}")

    # plot every 5th time step
    rowidxs = (
        [num for num in range(0, 11, 2)]
        + [num for num in range(10, 201, 5)]
        + [num for num in range(200 + 10, 301, 10)]
        + [num for num in range(300 + 50, nrows, 50)]
        + [nrows - 1]
    )
    nrowidx = len(rowidxs)
    print(f"Number of timesteps to plot: {nrowidx}")
    clrs = ["C0"] + ["C1"] * 5 + ["C2"] * (nrowidx - 2 - 5) + ["k"]
    print(f"Number of colors: {len(clrs)}")

    figscale = 1.5
    figw = 3.847
    figh = figw / 1.618
    figsz = (figscale * figw, figscale * figh)
    fig, ax = plt.subplots(figsize=figsz)
    for rowidx, clr in zip(rowidxs, clrs):
        # print(f"rowidx: {rowidx}")
        ax.plot(-vstress[rowidx, :], depths, marker="o", mfc="white", color=clr)
    ax.invert_yaxis()
    ax.grid(b=True, which="major", axis="both", ls=":", alpha=0.5)
    ax.set_xlabel("Vertical effective stress, $\sigma^{'}_\\textrm{v}$ [kPa]")
    ax.set_ylabel("Depth, $z$ [m]")
    fig.savefig(ffig, ext="png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":

    # basic_shapes("basic_shapes.svg")
    main()

