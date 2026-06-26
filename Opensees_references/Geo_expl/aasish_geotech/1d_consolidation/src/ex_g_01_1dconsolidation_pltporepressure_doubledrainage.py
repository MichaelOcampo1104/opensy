#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Description: plot pore pressure
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

    fname_pp = "1dcon_porepressure_doubledrainage.txt"
    fname_fig = "1dcon_porepressure_doubledrainage.png"
    fin = path_data.joinpath(fname_pp)
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

    # corner left edges
    ledgcr_start = 1
    ledgcr_end = 21

    # initial pore pressure increase [kPa]
    p0 = 1000.0

    number_corner_nodes = (nx + 1) * (ny + 1)
    number_topbottomedges_nodes = number_corner_nodes + nx * (ny + 1)
    number_leftrightedges_nodes = number_topbottomedges_nodes + (nx + 1) * ny
    number_total_nodes = number_leftrightedges_nodes + nx * ny
    print(f"Total number of nodes: {number_total_nodes}")

    df = pd.read_csv(fin, delimiter=" ")
    nrows, ncols = df.shape
    print(f"Number of rows and columns: {nrows}, {ncols}")

    # create node numbers, the first column is dt
    colnames = [num for num in range(1, ncols)]
    colnames = ["dt"] + colnames
    df.columns = colnames

    # porepressure from left edge node numbers
    ledgnum = [num for num in range(ledgcr_start, ledgcr_end + 1, nx + 1)]
    # only use columns for the interested nodes
    df = df.loc[:, ledgnum]
    # print(f"Dataframe with only needed nodes: {df}")

    # create for depth
    soil_depth = ny * ly
    depths = np.linspace(soil_depth, 0, ny + 1)
    # print(f"Depth check: {depths}")

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
        ax.plot(
            df.iloc[rowidx].values / p0,
            depths / soil_depth,
            marker="o",
            mfc="white",
            color=clr,
        )
    ax.invert_yaxis()
    ax.grid(b=True, which="major", axis="both", ls=":", alpha=0.5)
    ax.set_xlabel("Excess pore pressure, $\Delta u$ [kPa]")
    ax.set_ylabel("Depth, $z$ [m]")
    fig.savefig(ffig, ext="png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":

    # basic_shapes("basic_shapes.svg")
    main()

