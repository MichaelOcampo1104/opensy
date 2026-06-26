#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
from scipy import integrate
from pathlib import Path


# Convert PEER Ground motion database record from acceleration to velocity
# Each file contains one time series (single component as you noticed).
# The data is to be read horizontally, line by line, and is organized in 5 columns.
# ref: https://scec.usc.edu/scecpedia/PEER_Data_Format


def read_peer_acc(filepath):
    """Read the PEER database groundmotion file and return as a 1D array"""

    data = np.loadtxt(filepath)
    return data.ravel()


def main():
    # paths and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"

    # peer groundmotion filename, acc in gs
    fname_acc = "GilroyNo1EW.out"
    fname_vel = "velocityhistory.out"
    facc = path_data.joinpath(fname_acc)
    fvel = path_data.joinpath(fname_vel)

    # time step of data [s]
    dt = 0.005

    # accelaration due to gravity [m/s2]
    accg = 9.81

    # convert acceleration to m/s2
    acc = read_peer_acc(facc) * accg
    print(f"Shape of acceleration vector: {acc.shape}")

    # integrate to velocity
    vel = integrate.cumtrapz(acc, dx=dt, initial=0)

    # check the shape of the velocity vector
    print(f"Shape of the velocity vector: {vel.shape}")

    # save it to a txt file
    np.savetxt(fvel, vel)


if __name__ == "__main__":
    main()

