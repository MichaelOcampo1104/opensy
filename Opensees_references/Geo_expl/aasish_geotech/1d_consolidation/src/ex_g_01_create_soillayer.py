#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
from pathlib import Path
from itertools import chain, repeat
import svgwrite as svw
from svgwrite.extensions import Inkscape

# Draw the nodes and demarcate elements for the 9 node soil element in opensees for consolidation problem.


def chunks(L, n):
    """Yield successive n-sized chunks from L.
    chunks("abcdefghi", 3) -> ['abc', 'def', 'ghi']
    chunks([1,2,3,4,5,6,7,8,9], 3) -> [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    for list output: list(chunks(L, n))
    ref: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    author: Ned Batchelder
    """

    for i in range(0, len(L), n):
        yield L[i : i + n]


def flip_ycoord(y, height):
    """Flip the y-coordinate so that the origin is bottom left rather than top left"""
    return height - y


def slicedict(dict, start, stop):
    """Slice dictionary from start to stop
    ref: https://stackoverflow.com/questions/29216889/slicing-a-dictionary
    author: kindall
    """
    if start > stop:
        raise ValueError("stop > start")
    keys = range(start, stop)
    return {k: dict[k] for k in keys}


def repeatlist(a, b):
    """Repeat each item in list a, number of times specified in another list b
    ref: https://stackoverflow.com/questions/33382474/repeat-each-item-in-a-list-a-number-of-times-specified-in-another-list
    authors: thefourtheye and ShadowRanger
    example: a = [2, 3, 4], b = [1, 2, 3]
    repeatlist(a, b) -> [2, 3, 3, 4, 4, 4]"""
    return list(chain.from_iterable(map(repeat, a, b)))


def draw_outernodes(ox, oy, lx, ly, nx, ny, start_node_number, dwg):
    g = dwg.g(id="outernodes", stroke="#2c7bb6", font_family="DejaVu Sans")
    dwg.add(g)
    cxs = np.linspace(0, nx * lx, num=nx + 1) + ox
    cys = np.linspace(0, ny * ly, num=ny + 1) + oy
    # print(f"Cxs: {cxs}")
    # print(f"Cys: {cys}")
    height = dwg["height"]
    cys = flip_ycoord(cys, height)
    node_number = start_node_number
    xycoords = []
    for cy in cys:
        xycoord = []
        for cx in cxs:
            # print(f"(cx, cy): {cx, cy}")
            g.add(dwg.circle(center=(cx, cy), r=4, stroke_width=1, fill="none"))
            g.add(dwg.text(node_number, insert=(cx - 10, cy + 20)))
            node_number += 1
            xycoord.append([cx, flip_coord(cy, height)])
        xycoords.append(xycoord)
    return dwg, xycoords


def draw_cornernodes(
    ox, oy, lx, ly, nx, ny, start_node_number, xycoords, inkscape, dwg
):
    layer_crnodes = inkscape.layer(label="Corner nodes", locked=False)
    dwg.add(layer_crnodes)
    g = dwg.g(id="outernodes", stroke="#2c7bb6", font_family="DejaVu Sans")
    dwg.add(g)
    cxs = np.linspace(0, nx * lx, num=nx + 1) + ox
    cys = np.linspace(0, ny * ly, num=ny + 1) + oy
    # print(f"Cxs: {cxs}")
    # print(f"Cys: {cys}")

    node_number = start_node_number
    xv, yv = np.meshgrid(cxs, cys, indexing="ij")
    yv = flip_ycoord(yv, dwg["height"])
    coord_grid = np.array([xv, yv])
    gshape = coord_grid.shape

    for y in range(gshape[2]):
        for x in range(gshape[1]):
            xc, yc = coord_grid[:, x, y]
            # print(f"Node number: {node_number}, xc: {xc}, yc: {yc}")
            xycoords.update({node_number: (xc, flip_ycoord(yc, dwg["height"]))})
            nds = g.add(dwg.circle(center=(xc, yc), r=4, stroke_width=1, fill="none"))
            layer_crnodes.add(nds)
            txtnds = g.add(dwg.text(node_number, insert=(xc - 10, yc + 20)))
            layer_crnodes.add(txtnds)
            node_number += 1
    return dwg, xycoords


def draw_tdnodes(ox, oy, lx, ly, nx, ny, start_node_number, xycoords, dwg):
    g = dwg.g(id="tdnodes", stroke="#d7191c", font_family="DejaVu Sans")
    dwg.add(g)
    cxs = np.cumsum([lx / 2] + [lx] * (nx - 1)) + ox
    cys = np.cumsum([0] + [ly] * ny) + oy

    # print(f"Top down nodes:")
    # print(f"Cxs: {cxs}, Cyx: {cys}")
    xv, yv = np.meshgrid(cxs, cys, indexing="ij")
    yv = flip_ycoord(yv, dwg["height"])
    coord_grid = np.array([xv, yv])
    gshape = coord_grid.shape

    node_number = start_node_number
    for y in range(gshape[2]):
        for x in range(gshape[1]):
            xc, yc = coord_grid[:, x, y]
            xycoords.update({node_number: (xc, flip_ycoord(yc, dwg["height"]))})
            # print(coord_grid[:, x, y])
            g.add(dwg.circle(center=(xc, yc), r=4, stroke_width=1, fill="none"))
            g.add(dwg.text(node_number, insert=(xc - 10, yc + 20)))
            node_number += 1
    return dwg


def draw_lrnodes(ox, oy, lx, ly, nx, ny, start_node_number, xycoords, dwg):
    g = dwg.g(id="lrnodes", stroke="#fdae61", font_family="DejaVu Sans")
    dwg.add(g)

    cxs = np.cumsum([0] + [lx] * nx) + ox
    cys = np.cumsum([ly / 2] + [ly] * (ny - 1)) + oy
    cys = flip_ycoord(cys, dwg["height"])

    # print(f"Top down nodes:")
    # print(f"Cxs: {cxs}, Cyx: {cys}")
    xv, yv = np.meshgrid(cxs, cys, indexing="ij")
    coord_grid = np.array([xv, yv])
    gshape = coord_grid.shape
    # xs = coord_grid[:, :, 0]

    node_number = start_node_number
    for y in range(gshape[2]):
        for x in range(gshape[1]):
            xc, yc = coord_grid[:, x, y]
            xycoords.update({node_number: (xc, flip_ycoord(yc, dwg["height"]))})
            # print(coord_grid[:, x, y])
            g.add(dwg.circle(center=(xc, yc), r=4, stroke_width=1, fill="none"))
            g.add(dwg.text(node_number, insert=(xc - 10, yc + 20)))
            node_number += 1
    return dwg


def draw_centernodes(ox, oy, lx, ly, nx, ny, start_node_number, xycoords, dwg):
    g = dwg.g(id="lrnodes", stroke="#abd9e9")
    dwg.add(g)

    cxs = np.cumsum([lx / 2] + [lx] * (nx - 1)) + ox
    cys = np.cumsum([ly / 2] + [ly] * (ny - 1)) + oy

    # print(f"Top down nodes:")
    # print(f"Cxs: {cxs}, Cyx: {cys}")
    xv, yv = np.meshgrid(cxs, cys, indexing="ij")
    yv = flip_ycoord(yv, dwg["height"])
    coord_grid = np.array([xv, yv])
    gshape = coord_grid.shape

    node_number = start_node_number
    for y in range(gshape[2]):
        for x in range(gshape[1]):
            xc, yc = coord_grid[:, x, y]
            xycoords.update({node_number: (xc, flip_ycoord(yc, dwg["height"]))})
            # print(coord_grid[:, x, y])
            g.add(dwg.circle(center=(xc, yc), r=4, stroke_width=1, fill="none"))
            g.add(dwg.text(node_number, insert=(xc - 10, yc + 20)))
            node_number += 1
    return dwg


def draw_hlines(xycoords, nx, ny, dwg):
    g = dwg.g(id="hlines", stroke="#636363")
    hlines = dwg.add(g)
    cr_last_node_number = (nx + 1) * (ny + 1)
    td_last_node_number = cr_last_node_number + nx * (ny + 1)
    print(f"Corner nodes: 1 - {cr_last_node_number}")
    print(f"Top down nodes: {cr_last_node_number + 1} - {td_last_node_number}")

    # print(f"xycoords: {xycoords}")
    crnodes_dict = slicedict(xycoords, 1, cr_last_node_number + 1)
    # print(f"Corner nodes: {crnodes_dict}")
    crnodes_list = list(crnodes_dict.values())
    tdnodes_dict = slicedict(xycoords, cr_last_node_number + 1, td_last_node_number + 1)
    # print(f"Top down nodes: {tdnodes_dict}")
    tdnodes_list = list(tdnodes_dict.values())

    # arrange the nodes horizontally
    hor_crnodes = chunks(crnodes_list, nx + 1)
    hor_tdnodes = chunks(tdnodes_list, nx)

    for hor_crnode, hor_tdnode in zip(hor_crnodes, hor_tdnodes):
        crlist = [1] + [2] * (nx - 1) + [1]
        tdlist = [2] * nx
        # print(crlist, tdlist)
        hor_crnode = repeatlist(hor_crnode, crlist)
        hor_tdnode = repeatlist(hor_tdnode, tdlist)
        # print(f"Corner nodes: {hor_crnode}")
        # print(f"Top down nodes: {hor_tdnode}")
        for i in range(0, 2 * nx, 2):
            # print(len(hor_crnode), len(hor_tdnode))
            x1 = hor_crnode[i][0]
            y1 = hor_crnode[i][1]
            x2 = hor_tdnode[i][0]
            y2 = hor_tdnode[i][1]
            print(f"x1: {x1}, y1:{y1}, x2:{x2}, y2:{y2}")
            hlines.add(
                dwg.line(
                    start=(x1 + 3, flip_ycoord(y1, dwg["height"])),
                    end=(x2 - 3, flip_ycoord(y2, dwg["height"])),
                )
            )
        for i in range(1, 2 * nx, 2):
            # print(len(hor_crnode), len(hor_tdnode))
            x1 = hor_tdnode[i][0]
            y1 = hor_tdnode[i][1]
            x2 = hor_crnode[i][0]
            y2 = hor_crnode[i][1]
            print(f"x1: {x1}, y1:{y1}, x2:{x2}, y2:{y2}")
            hlines.add(
                dwg.line(
                    start=(x1 + 3, flip_ycoord(y1, dwg["height"])),
                    end=(x2 - 3, flip_ycoord(y2, dwg["height"])),
                )
            )

    return dwg


# def draw_hlines_2(xycoords, dwg):
#     g = dwg.g(id="hlines", stroke="#636363")
#     hlines = dwg.add(g)
#     for xycoord in xycoords:
#         for (x1, y1), (x2, y2) in zip(xycoord[:-1], xycoord[1:]):
#             print(f"x1: {x1}, y1:{y1}, x2:{x2}, y2:{y2}")
#             hlines.add(dwg.line(start=(x1 + 3, y1), end=(x2 - 3, y2)))

#     return dwg


def draw_vlines(xycoords, nx, ny, dwg):
    g = dwg.g(id="vlines", stroke="#636363")
    vlines = dwg.add(g)
    cr_last_node_number = (nx + 1) * (ny + 1)
    td_last_node_number = cr_last_node_number + nx * (ny + 1)
    lr_last_node_number = td_last_node_number + (nx + 1) * ny
    print(f"Corner nodes: 1 - {cr_last_node_number}")
    print(f"Left right nodes: {td_last_node_number + 1} - {lr_last_node_number}")

    # print(f"xycoords: {xycoords}")
    crnodes_dict = slicedict(xycoords, 1, cr_last_node_number + 1)
    # print(f"Corner nodes: {crnodes_dict}")
    crnodes_list = list(crnodes_dict.values())
    lrnodes_dict = slicedict(xycoords, td_last_node_number + 1, lr_last_node_number + 1)
    # print(f"Left right nodes: {lrnodes_dict}")
    lrnodes_list = list(lrnodes_dict.values())
    # print(f"Left right nodes: {lrnodes_list}")

    # arrange the nodes horizontally
    hor_crnodes = chunks(crnodes_list, nx + 1)
    hor_lrnodes = chunks(lrnodes_list, nx + 1)
    # print(f"Horizontal left right nodes: {list(hor_lrnodes)}")

    # vertically aligned nodes
    ver_crnodes = zip(*hor_crnodes)
    ver_lrnodes = zip(*hor_lrnodes)

    for ver_crnode, ver_lrnode in zip(ver_crnodes, ver_lrnodes):
        crlist = [1] + [2] * (ny - 1) + [1]
        lrlist = [2] * ny
        # print(crlist, lrlist)
        ver_crnode = repeatlist(ver_crnode, crlist)
        ver_lrnode = repeatlist(ver_lrnode, lrlist)

        # print(f"Vertical corner nodes: {ver_crnode}")
        # print(f"Vertical top down nodes: {ver_lrnode}")
        for i in range(0, 2 * ny, 2):
            # print(len(ver_crnode), len(ver_lrnode))
            x1 = ver_crnode[i][0]
            y1 = ver_crnode[i][1]
            x2 = ver_lrnode[i][0]
            y2 = ver_lrnode[i][1]
            print(f"x1: {x1}, y1:{y1}, x2:{x2}, y2:{y2}")
            vlines.add(
                dwg.line(
                    start=(x1, flip_ycoord(y1, dwg["height"]) - 3),
                    end=(x2, flip_ycoord(y2, dwg["height"]) + 3),
                )
            )
        for i in range(1, 2 * ny, 2):
            # print(len(ver_crnode), len(ver_lrnode))
            x1 = ver_lrnode[i][0]
            y1 = ver_lrnode[i][1]
            x2 = ver_crnode[i][0]
            y2 = ver_crnode[i][1]
            print(f"x1: {x1}, y1:{y1}, x2:{x2}, y2:{y2}")
            vlines.add(
                dwg.line(
                    start=(x1, flip_ycoord(y1, dwg["height"]) - 3),
                    end=(x2, flip_ycoord(y2, dwg["height"]) + 3),
                )
            )

    return dwg


# def draw_vlines_2(xycoords, dwg):
#     g = dwg.g(id="vlines", stroke="#636363")
#     vlines = dwg.add(g)
#     xycoords = list(zip(*xycoords))
#     for xycoord in xycoords:
#         for (x1, y1), (x2, y2) in zip(xycoord[:-1], xycoord[1:]):
#             print(f"x1: {x1}, y1:{y1}, x2:{x2}, y2:{y2}")
#             vlines.add(dwg.line(start=(x1, y1 - 3), end=(x2, y2 + 3)))

#     return dwg


def main():
    # file path and filenames
    path_root = Path(r"../")
    path_plt = path_root / "plt"
    fname_svg = "1dconsolidation_r1c10.svg"

    svgfile = path_plt.joinpath(fname_svg)
    # center offset from the bottom left of the page (origin of the page, origin transformed)
    ox = 50.0
    oy = 50.0
    # offsets in x and y direction of the nodes
    lx = 100.0
    ly = 100.0
    # number of element in x and y direction
    nx = 1
    ny = 10
    # dictionary for node numbers and corresponding coordinates
    # {node_number: (x, y)}
    xycoords = {}
    # svg size (2-tuple): (width, height)
    dwg = svw.Drawing(
        filename=svgfile, profile="full", size=(800, 1200), viewBox=("0 0 800 1200")
    )
    inkscape = Inkscape(dwg)
    top_layer = inkscape.layer(label="Default layer", locked=True)
    dwg.add(top_layer)
    # the corner coordinates are in increasing order of the nodes
    # with node number and (x, y) coordinates with origin at the bottom left
    # {1: (x1, y1), 2: (x2, y2), .....}
    dwg, corner_xyxycoords = draw_cornernodes(
        ox, oy, lx, ly, nx, ny, 1, xycoords, inkscape, dwg
    )

    # flat_list = [item for xycoord in xycoords for item in xycoord]
    # col_nodes = list(zip(*xycoords))

    # dwg = draw_vlines(corner_xycoords, dwg)
    last_node_number = (nx + 1) * (ny + 1)
    # # dwg = draw_corner_nodes(ox, oy, lx, ly, nx, ny, 0, dwg)
    dwg = draw_tdnodes(ox, oy, lx, ly, nx, ny, last_node_number + 1, xycoords, dwg)
    last_node_number += nx * (ny + 1)
    dwg = draw_lrnodes(ox, oy, lx, ly, nx, ny, last_node_number + 1, xycoords, dwg)
    last_node_number += (nx + 1) * ny
    dwg = draw_centernodes(ox, oy, lx, ly, nx, ny, last_node_number + 1, xycoords, dwg)
    cr_last_node_number = (nx + 1) * (ny + 1)
    td_last_node_number = cr_last_node_number + nx * (ny + 1)
    lr_last_node_number = td_last_node_number + (nx + 1) * ny
    cn_last_node_number = lr_last_node_number + nx * ny
    print(f"Corner nodes: 1 - {cr_last_node_number}")
    print(f"Top down nodes: {cr_last_node_number + 1} - {td_last_node_number}")
    print(f"Left right nodes: {td_last_node_number + 1} - {lr_last_node_number}")
    print(f"Center nodes: {lr_last_node_number + 1} - {cn_last_node_number}")

    # for key, values in xycoords.items():
    #     print(f"Node: {key}, (x, y): {values}")

    dwg = draw_hlines(xycoords, nx, ny, dwg)
    dwg = draw_vlines(xycoords, nx, ny, dwg)
    dwg.save()


if __name__ == "__main__":

    # basic_shapes("basic_shapes.svg")
    main()

