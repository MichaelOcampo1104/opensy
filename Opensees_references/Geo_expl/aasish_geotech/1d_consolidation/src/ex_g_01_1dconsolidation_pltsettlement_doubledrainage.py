#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Description: plot time settlement curve for double drainage
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


def time_settlement_curve(ax, infile):
    df = pd.read_csv(infile, delimiter=" ")
    nrows, ncols = df.shape
    print(f"Number of rows and columns in OpenSees output file: {nrows}, {ncols}")
    # downward displacement positive as in geotechnical convention
    vdisp = -df.iloc[:, 2].values
    dt = df.iloc[:, 0].values
    ax.plot(dt, vdisp)
    return ax


def main():
    # file path and filenames
    path_root = Path(r"../")
    path_data = path_root / "data"
    path_plt = path_root / "plt"

    fnames_data = ["1dcon_disp_doubledrainage.txt", "1dcon_disp_singledrainage.txt"]
    fname_fig = "1dcon_loadsettlement_curve.png"

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

    # number of strain output for each element
    nstrain = 3

    # figure
    figscale = 1.5
    figw = 3.847
    figh = figw / 1.618
    figsz = (figscale * figw, figscale * figh)
    fig, ax = plt.subplots(figsize=figsz)

    # For 2D problems, the stress output follows this order: σxx, σyy, σzz, σxy, ηr, where ηr
    # is the ratio between the shear (deviatoric) stress and peak shear strength at the current
    # confinement (0<=ηr<=1.0). The strain output follows this order: εxx, εyy, γxy.
    # output file: stress components for integration point 9 in every element for each time step
    for fname_data in fnames_data:
        infile = path_data.joinpath(fname_data)
        ax = time_settlement_curve(ax, infile)

    ax.invert_yaxis()
    ax.grid(b=True, which="major", axis="both", ls=":", alpha=0.5)
    ax.set_xlabel("Time elasped, $\Delta t$ [s]")
    ax.set_ylabel("Surface settlement, $\Delta z$ [m]")
    ax.legend(labels=["Double drainage", "Single drainage"], frameon=False)
    fig.savefig(ffig, ext="png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":

    # basic_shapes("basic_shapes.svg")
    main()

