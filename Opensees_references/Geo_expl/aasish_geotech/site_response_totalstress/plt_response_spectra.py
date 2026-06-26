#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
from scipy import integrate
from pathlib import Path
import matplotlib.pyplot as plt
import eqsig.single as eq
from matplotlib.lines import Line2D



# Description: Plot the acceleration, velocity and displacement spectra
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


def main():
    # paths and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"
    path_plt = path_root / "plt"

    # filenames for [acceleration, velocity, displacement] from the python Openseespy file I created
    fnames = [
        "ex_g_02_reponse_spectra_eqsig_damp0p05.csv",
        "ex_g_02_reponse_spectra_freq_damp0p05.csv" 
    ]
    # these are output from the Opensees example totalstress site reponse analysis
    # ref: https://opensees.berkeley.edu/wiki/index.php/Site_Response_Analysis_of_a_Layered_Soil_Column_(Total_Stress_Analysis)
    # Tcl file: freeFieldSingle.tcl
    # fname_matlab = "response_spectra_matlab.csv"

    # this is the response spectra computed using the EQSIG package
    # fname_eqsig = "ex_g_02_reponse_spectra_eqsig_damp0p05.csv"

    # plot all three figures in the same plot, filename
    fname_fig = "ex_g_02_response_spectra.png"
    ffig = path_plt.joinpath(fname_fig)
   
    # acceleration due to gravity [m/s2]
    accg = 9.81

    # customization
    clrs = ["C0", "C1"]
    lbls = ["EQSIG", "Frequency domain"]

    # figure
    figscale = 1.5
    figw = 3.847
    figh = 2 * figw / 1.618
    figsz = (figscale * figw, figscale * figh)
    fig, axs = plt.subplots(3, 1, figsize=figsz, sharex=True)
    axs = axs.ravel()

    for fname, clr in zip(fnames, clrs):
        print(f"Filename: {fname}")
        fpath_in = path_data.joinpath(fname)
        periods, umaxs, vmaxs, amaxs = np.loadtxt(fpath_in, skiprows=1, delimiter=',', unpack=True)
        axs[0].plot(periods, umaxs, color=clr, alpha=0.5)
        axs[1].plot(periods, vmaxs, color=clr, alpha=0.5)
        axs[2].plot(periods, amaxs, color=clr, alpha=0.5)


    # # add the spectra from the matlab output
    # print(f"Filename: {fname_matlab}")
    # fpath_matlab = path_data.joinpath(fname_matlab)
    # periods, umaxs, vmaxs, amaxs = np.loadtxt(fpath_matlab, skiprows=1, delimiter=',', unpack=True)
    # axs[0].plot(periods, umaxs, color='C2', alpha=0.5)
    # axs[1].plot(periods, vmaxs, color='C2', alpha=0.5)
    # axs[2].plot(periods, amaxs, color='C2', alpha=0.5)
    
    # plot data computed using the eqsig package
    # print(f"Filename: {fname_eqsig}")
    # fpath_eqsig= path_data.joinpath(fname_eqsig)
    # periods, umaxs, vmaxs, amaxs = np.loadtxt(fpath_eqsig, skiprows=1, delimiter=',', unpack=True)
    # axs[0].plot(periods, umaxs, alpha=0.5, color="C3")
    # axs[1].plot(periods, vmaxs, alpha=0.5, color="C3")
    # axs[2].plot(periods, amaxs, alpha=0.5, color="C3")
    
    # add line labels
    custom_lines = []
    for lbl,clr in zip(lbls, clrs):
        custom_lines.append(Line2D([0], [0], ls="-", color=clr, label=lbl))

    # legend
    axs[0].legend(handles=custom_lines, labels=lbls, frameon=False, loc=2)

    # xaxis label
    axs[-1].set_xlabel(r"Time period, $T$ [s]")
    axs[-1].set_xscale('log')
    
    # yaxis labels
    yaxis_labels = [r"$S_\textrm{d}$ [m]", r"$S_\textrm{v}$ [m/s]", r"$S_\textrm{a}$ [g]"]

    for ax, ylbl in zip(axs, yaxis_labels):
        ax.set_ylabel(ylbl)
        ax.grid(b=True, which="major", axis="both", ls=":", color="k", alpha=0.4)

    
    fig.savefig(ffig, ext="png", dip=150, bbox_inches="tight")


if __name__ == "__main__":
    main()

