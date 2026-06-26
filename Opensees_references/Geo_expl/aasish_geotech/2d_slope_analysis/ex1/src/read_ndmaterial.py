#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
from pathlib import Path
import meshio
from itertools import count, zip_longest, chain, repeat, dropwhile, takewhile, islice

from collections import defaultdict, namedtuple


def read_blocks(fpath, start_string, end_string):
    """Return blocks of lines between start_string and end_string in a file as list
    ref:https://stackoverflow.com/questions/18865058/extract-values-between-two-strings-in-a-text-file-using-python
    ref:https://stackoverflow.com/questions/27805919/how-to-only-read-lines-in-a-text-file-after-a-certain-string
    """
    with open(fpath) as f:
        while True:
            # it = dropwhile(lambda line: line.strip() != start_string, f)
            # it = takewhile(lambda line: line.strip() != end_string, it)
            it = dropwhile(lambda line: start_string not in line.strip(), f)
            it = takewhile(lambda line: end_string not in line.strip(), it)
            return list(it)[1:]


def read_nyieldsurf(fpath, nyldsurf, start_nsurftag, end_nsurftag):
    """Read Shear strain  and shear stress values from the material input file"""
    nyieldsurflines = read_blocks(fpath, start_nsurftag, end_nsurftag)
    # drop the first line of header
    nyieldsurflines = nyieldsurflines[1:]
    nyldsurf_data = []
    for line in nyieldsurflines:
        line = line.strip(",\n").split(",")
        line = [float(val) for val in line]
        nyldsurf_data += [line[0], line[1]]
        # check if correct number of lines were read
    if len(nyldsurf_data) != (2 * abs(nyldsurf)):
        print(
            "WARNING: The number of yield surface points returned is less than that specified"
        )
    return nyldsurf_data


def read_ndmaterial_pressureindependent(fpath, start_matprop, end_matprop):
    """ """
    datatypes = [
        str,
        str,
        int,
        int,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        int,
    ]
    dkeys = [
        "mattype",
        "mattag",
        "nd",
        "rho",
        "refshear",
        "refbulk",
        "cohesion",
        "peak_shear_strain",
        "friction_angle",
        "refpressure",
        "pressure_coeff",
        "nyieldsurf",
        "yieldsurf",
    ]
    # discard the first header line
    lines = read_blocks(fpath, start_matprop, end_matprop)[1:]
    # parse values with correct datatype
    matprop_dict = {}
    mattag_dict = {}
    nsurf_dict = {}
    for line in lines:
        vals = line.strip(",\n").split(",")
        pvals = [datatype(val) for val, datatype in zip(vals, datatypes)]
        physical_tag = pvals[0]
        mattag = pvals[1]
        mattag_dict.update({physical_tag: mattag})
        dkv = dict(zip(dkeys, pvals[1:]))
        matprop_dict.update({physical_tag: dkv})
        nyldsurf = pvals[-1]
        customsurf = []
        if nyldsurf < 0:
            start_nyldsurftag = "start_nyldsurf:" + physical_tag
            end_nyldsurftag = "end_nyldsurf:" + physical_tag
            nyldsurf_data = read_nyieldsurf(
                fpath, nyldsurf, start_nyldsurftag, end_nyldsurftag
            )
            nsurf_dict.update({physical_tag: nyldsurf_data})
        else:
            nsurf_dict.update({"AutoGen": [0, 0]})
    return mattag_dict, matprop_dict, nsurf_dict


def main():
    path_root = Path(r"../")
    path_gmsh = path_root / "gmsh"
    path_data = path_root / "data"

    fname_matfile = "ndmat_multiyield_pressureindependent.csv"
    fmatfile = path_data.joinpath(fname_matfile)

    # drop the first line as it is header row
    mattag_dict, matprop_dict, nsurf_dict = read_ndmaterial_pressureindependent(
        fmatfile, "start_ndmaterial:", "end_ndmaterial:"
    )
    print(mattag_dict, matprop_dict, nsurf_dict)
    # matprop_dict, mattag_dict = read_ndmaterial_pressureindependent(fmatfile)
    # ptag = "Soil"
    # print(matprop_dict[ptag])


if __name__ == "__main__":
    main()
