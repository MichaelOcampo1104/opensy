#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
from pathlib import Path
import meshio
import pygmsh


def main():
    # paths and filenames
    path_root = Path(r"../")
    path_gmsh = path_root / "gmsh"
    fname_geo = "2d_slopestability_ex1_pygmsh.geo"

    fgeo = str(path_gmsh.joinpath(fname_geo))

    # height of the slope
    sheight = 10.0
    # depth of the foundation
    fdepth = -2.0 * sheight
    gridsize = 1.0

    geom = pygmsh.built_in.Geometry()

    # coordinates left periodic boundary, slope region
    coords_lpb_slope = [
        [0, 0, 0],
        [1.5 * sheight, 0, 0],
        [1.5 * sheight, sheight, 0],
        [0, sheight, 0],
    ]

    # coordinates of left periodic boundary, foundation region
    coords_lpb_found = [[0, fdepth, 0], [1.5 * sheight, fdepth, 0]]

    # coordinates of the slope region
    coords_slope = [
        [(1.5 + 1 + 4.2) * sheight, 0, 0],
        [(1.5 + 1 + 1.2) * sheight, sheight, 0],
    ]

    # foundation below the slope
    coords_found_slope = [[(1.5 + 1 + 4.2) * sheight, fdepth, 0]]

    # foundation beyond the slope
    coords_found_beyondslope = [
        [(1.5 + 1 + 4.2 + 3) * sheight, 0, 0],
        [(1.5 + 1 + 4.2 + 3) * sheight, fdepth, 0],
    ]

    # right periodic boundary condition, foundation
    coords_rpb_found = [
        [(1.5 + 1 + 4.2 + 3 + 1.5) * sheight, 0, 0],
        [(1.5 + 1 + 4.2 + 3 + 1.5) * sheight, fdepth, 0],
    ]

    # assemble all the coordinates and create labels
    coords = (
        coords_lpb_slope
        + coords_lpb_found
        + coords_slope
        + coords_found_slope
        + coords_found_beyondslope
        + coords_rpb_found
    )
    plabels = ["p" + str(idx) for idx in range(1, len(coords) + 1)]

    # create points and store them in a dictionary
    points = {}
    for plabel, coord in zip(plabels, coords):
        points.update({plabel: geom.add_point(coord, lcar=gridsize)})

    # for key, value in points.items():
    #     print(key, value.id, value.x)

    # create lines, each tuple creates a line, here they are grouped by lists
    # only to group for reviewers, the list does not signify anything else
    # left periodic boundary slope region
    lineps = [("p1", "p2"), ("p2", "p3"), ("p3", "p4"), ("p4", "p1")]
    # left periodic boundary foundation region
    lineps += [("p1", "p5"), ("p5", "p6"), ("p6", "p2")]
    # slope region
    lineps += [("p2", "p7"), ("p7", "p8"), ("p8", "p3")]
    # foundation below the slope
    lineps += [("p6", "p9"), ("p9", "p7")]
    # foundation beyond the slope
    lineps += [("p9", "p11"), ("p11", "p10"), ("p10", "p7")]
    # right boundary foundation region
    lineps += [("p11", "p13"), ("p13", "p12"), ("p12", "p10")]
    lines = {}
    llabels = ["l" + str(idx) for idx in range(1, len(lineps) + 1)]
    for llabel, linep in zip(llabels, lineps):
        lines.update({llabel: geom.add_line(points[linep[0]], points[linep[1]])})
    for k, v in lines.items():
        print(k, v.id, v.points[0].id, v.points[1].id)

    # lineloops, each list consists of a single line loopq
    # left periodic boundary slope region
    looplines = [["l1", "l2", "l3", "l4"]]
    # # left periodic boundary foundation region
    looplines += [["l6", "l7", "-l1", "l5"]]
    # slope region
    looplines += [["l8", "l9", "l10", "-l2"]]
    # foundation below the slope
    looplines += [["l11", "l12", "-l8", "-l7"]]
    # foundation beyond the slope
    looplines += [["l13", "l14", "l15", "-l12"]]
    # right boundary foundation region
    looplines += [["l16", "l17", "l18", "-l14"]]
    lineloops = {}
    looplabels = ["ll" + str(idx) for idx in range(1, len(looplines) + 1)]
    for looplabel, loopline in zip(looplabels, looplines):
        loop = []
        for line in loopline:
            if line[0] == "-":
                loop.append(-lines[line[1:]])
            else:
                loop.append(lines[line])
        lineloops.update({looplabel: geom.add_line_loop(loop)})

    # for k, v in lineloops.items():
    #     print(k, v.id, [l.id for l in v.lines])

    # plane surface
    pslabels = ["ps" + str(idx) for idx in range(1, len(lineloops) + 1)]
    print(pslabels)
    planesurfaces = {}
    for pslabel, (llabel, lineloop) in zip(pslabels, lineloops.items()):
        planesurfaces.update({pslabel: geom.add_plane_surface(lineloop)})

    for k, v in planesurfaces.items():
        print(k, v)

    # transfinite surfaces
    ts_sizes = [[11, 11], [11, 11], [21, 11], [21, 11], [11, 11], [11, 11]]
    for pslabel, ts_size in zip(planesurfaces.keys(), ts_sizes):
        geom.set_transfinite_surface(planesurfaces[pslabel], size=ts_size)

    # recombine for structures quad mesh
    for pslabel in planesurfaces.keys():
        geom.set_recombined_surfaces([planesurfaces[pslabel]])

    # mesh = pygmsh.generate_mesh(
    #     geom,
    #     geo_filename=fgeo,
    #     gmsh_path="C:\DownloadedPrograms\gmsh-4.5.4-Windows64\gmsh.exe",
    # )

    with open(fgeo, "w") as fout:
        fout.write(geom.get_code())
        fout.write("\n")
    # meshio.write("slope.vtk", mesh)


if __name__ == "__main__":
    main()
