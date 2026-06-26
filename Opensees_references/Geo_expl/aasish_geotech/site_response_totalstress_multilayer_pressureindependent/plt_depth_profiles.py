#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


# Description: Plot acceleration, velocity and displacement depth profiles

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
    # paths and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"
    path_plt = path_root / "plt"

    fname_dp = "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_depthprofiles.csv"
    f_dp = path_data.joinpath(fname_dp)

    # plot all three figures in the same plot, filename
    fname_fig = "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_depthprofiles.png"
    ffig = path_plt.joinpath(fname_fig)

    # acceleration due to gravity [m/s2]
    accg = 9.81

    # figure
    figscale = 1.5
    figw = 3.847 * 2
    figh = figw / 1.618
    figsz = (figscale * figw, figscale * figh)
    fig, axs = plt.subplots(1, 3, figsize=figsz, sharey=True)
    axs = axs.ravel()

    xlbls = [r"$\ddot{u}$ [g]", r"$\dot{u}$ [m/s]", r"$u$ [m]"]
    data = np.loadtxt(f_dp, delimiter=",", skiprows=1, unpack=True)
    data[1] = data[1] / accg
    for idx, ax in enumerate(axs):
        print(f"idx: {idx}, {idx + 1}")
        ax.plot(data[idx + 1], data[0])
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position("top")
        ax.set_xlabel(xlbls[idx], labelpad=10)
        ax.grid(b=True, which="major", axis="both", ls=":", color="k", alpha=0.4)
        ax.set_ylim(ax.get_ylim()[::-1])

    # yaxis label
    axs[0].set_ylabel(r"Depth, $z$ [m]")

    # save figure
    fig.savefig(ffig, ext="png", dip=150, bbox_inches="tight")


if __name__ == "__main__":
    main()

