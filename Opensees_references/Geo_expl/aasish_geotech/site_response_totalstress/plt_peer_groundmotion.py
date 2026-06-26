#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Description: Plot PEER ground motion

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


def acceleration_plot(ax, fpath, dt):
    """Plot the acceleration data"""
    data = np.loadtxt(fpath)
    data = data.ravel()
    data_length = data.shape[0]
    print(f"Shape of the data: {data.shape}")
    x = np.linspace(0, dt * data_length, data_length + 1)[:-1]
    print(f"Shape of x: {x.shape}")
    ax.plot(x, data)
    ax.set_xlabel(r"Time, $\Delta t$ [s]")
    ax.set_ylabel(r"Accelration, $a$ [g]")
    ax.grid(b=True, which="major", axis="both", ls=":", alpha=0.4)
    return ax


def velocity_plot(ax, fpath, dt, clr):
    """Plot the velocity data"""
    data = np.loadtxt(fpath)
    print(f"Shape of the data: {data.shape}")
    data_length = data.shape[0]
    x = np.linspace(0, dt * data_length, data_length + 1)[:-1]
    print(f"Shape of x: {x.shape}")
    ax.plot(x, data, color=clr)
    ax.set_xlabel(r"Time, $\Delta t$ [s]")
    ax.set_ylabel(r"Velocity, $v$ [m/s]")
    ax.grid(b=True, which="major", axis="both", ls=":", alpha=0.4)
    return ax


def main():
    # file path and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"
    path_plt = path_root / "plt"
    path_orisoln = path_root / "original_solution"

    # name of the figure file
    fname_fig = "gilroyno1ew_vel.png"
    ffig = path_plt.joinpath(fname_fig)

    # name of the input file
    fname_gm = "velocityHistory.out"
    fgm1 = path_data.joinpath(fname_gm)
    fgm2 = path_orisoln.joinpath(fname_gm)
    # fname_gm = "GilroyNo1EW.out"
    # fgm = path_data.joinpath(fname_gm)
    fgms = [fgm1, fgm2]
    clrs = ["C0", "C1"]

    # time step of the data [s] and length create time for data
    dt = 0.005

    # figure
    figscale = 1.5
    figw = 3.487
    figh = figw / 1.618
    figsz = (figscale * figw, figscale * figh)
    fig, ax = plt.subplots(figsize=figsz)
    # ax = acceleration_plot(ax, fgm, dt)
    for fgm, clr in zip(fgms, clrs):
        ax = velocity_plot(ax, fgm, dt, clr)

    fig.savefig(ffig, ext="png", dpi=150, bbox_inches="tight")


if __name__ == "__main__":

    main()

