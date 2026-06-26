#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
from pathlib import Path
from itertools import count, chain, repeat
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


def draw_cornernodes(
    ox, oy, lx, ly, nx, ny, start_node_number, xycoords, inkscape, dwg
):
    """Draw the corner nodes and write the node numbers and x and y coordinates in a file
    (ox, oy) : coordinates of the origin
    lx: the spacing of the nodes in the x-direction, horizontal direction
    ly: the spacing of the nodes in the y-direction, vertical direction
    nx: number of elements in the x-direction
    ny: number of elements in the y-direction
    start_node_number: the starting node number, the node number will start from the value of the
                        start_node_number each time this function is called
    xycoords: a dictionary to collect all the nodes (number and xy location) created {node_number: (xcoord, ycoord)}
    inkscape: inkscape extension object in svgwrite
    dwg: drawing object of svgwrite
    """

    layer_crnodes = inkscape.layer(label="Corner nodes", locked=False)
    layer_crndtxt = inkscape.layer(label="Corner node numbers", locked=False)
    dwg.add(layer_crnodes)
    dwg.add(layer_crndtxt)
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
            layer_crndtxt.add(txtnds)
            node_number += 1
    return dwg, xycoords


def draw_hlines(xycoords, nx, ny, dwg):
    """Draw the horizontal lines between neighbouring nodes
    xycoords: a dictionary to collect all the nodes (number and xy location) {node_number: (xcoord, ycoord)}
    nx: number of elements in the x-direction
    ny: number of elements in the y-direction
    dwg: drawing object of svgwrite
    """
    g = dwg.g(id="hlines", stroke="#636363")
    hlines = dwg.add(g)
    cr_last_node_number = (nx + 1) * (ny + 1)
    td_last_node_number = cr_last_node_number + nx * (ny + 1)
    # print(f"Corner nodes: 1 - {cr_last_node_number}")

    # print(f"xycoords: {xycoords}")
    crnodes_dict = slicedict(xycoords, 1, cr_last_node_number + 1)
    # print(f"Corner nodes: {crnodes_dict}")
    crnodes_list = list(crnodes_dict.values())

    # arrange the nodes horizontally
    hor_crnodes = chunks(crnodes_list, nx + 1)

    for hor_crnode in hor_crnodes:
        crlist = [1] + [2] * (nx - 1) + [1]
        # print(crlist, tdlist)
        hor_crnode = repeatlist(hor_crnode, crlist)
        # print(f"Corner nodes: {hor_crnode}")
        # print(f"Top down nodes: {hor_tdnode}")
        for (x1, y1), (x2, y2) in zip(hor_crnode[0:-1], hor_crnode[1:]):
            # print(len(hor_crnode), len(hor_tdnode))
            # print(f"x1: {x1}, y1:{y1}, x2:{x2}, y2:{y2}")
            hlines.add(
                dwg.line(
                    start=(x1 + 3, flip_ycoord(y1, dwg["height"])),
                    end=(x2 - 3, flip_ycoord(y2, dwg["height"])),
                )
            )

    return dwg


def draw_vlines(xycoords, nx, ny, dwg):
    """Draw the vertical lines between neighbouring nodes
    xycoords: a dictionary of all the nodes (node number and xy location) {node_number: (xcoord, ycoord)}
    nx: number of elements in the x-direction
    ny: number of elements in the y-direction
    dwg: drawing object of svgwrite
    """
    g = dwg.g(id="vlines", stroke="#636363")
    vlines = dwg.add(g)
    cr_last_node_number = (nx + 1) * (ny + 1)
    # print(f"Corner nodes: 1 - {cr_last_node_number}")

    # print(f"xycoords: {xycoords}")
    crnodes_dict = slicedict(xycoords, 1, cr_last_node_number + 1)
    # print(f"Corner nodes: {crnodes_dict}")
    crnodes_list = list(crnodes_dict.values())

    # arrange the nodes horizontally
    hor_crnodes = chunks(crnodes_list, nx + 1)

    # print(f"Horizontal left right nodes: {list(hor_lrnodes)}")

    # vertically aligned nodes
    ver_crnodes = zip(*hor_crnodes)

    for ver_crnode in ver_crnodes:
        crlist = [1] + [2] * (ny - 1) + [1]
        # print(crlist, lrlist)
        ver_crnode = repeatlist(ver_crnode, crlist)

        # print(f"Vertical corner nodes: {ver_crnode}")
        # print(f"Vertical top down nodes: {ver_lrnode}")
        for (x1, y1), (x2, y2) in zip(ver_crnode[0:-1], ver_crnode[1:]):
            # print(len(ver_crnode), len(ver_lrnode))
            # print(f"x1: {x1}, y1:{y1}, x2:{x2}, y2:{y2}")
            vlines.add(
                dwg.line(
                    start=(x1, flip_ycoord(y1, dwg["height"]) - 3),
                    end=(x2, flip_ycoord(y2, dwg["height"]) + 3),
                )
            )

    return dwg


def draw_elenumbers(ox, oy, lx, ly, nx, ny, start_node_number, xycoords, dwg):
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
            # print(coord_grid[:, x, y])
            g.add(dwg.circle(center=(xc, yc), r=15, stroke_width=1, fill="none"))
            g.add(dwg.text(node_number, insert=(xc - 5, yc + 5)))
            node_number += 1
    return dwg


def fournode_quadelement(xycoords, elements, nx, ny):
    # corner nodes arranged in horizontally
    hr_crnodes = list(chunks(list(xycoords.keys()), nx + 1))
    cr_last_node_number = (nx + 1) * (ny + 1)
    # print(f"Corner nodes: 1 - {cr_last_node_number}")

    crnodes_dict = slicedict(xycoords, 1, cr_last_node_number + 1)
    # print(f"Corner nodes: {crnodes_dict}")
    crnodes_list = list(crnodes_dict.values())

    # arrange the nodes horizontally
    hor_crnodes = list(chunks(crnodes_list, nx + 1))
    gen_element_numbers = count(1)

    # for (x1, y1), (x2, y2)
    rlist = [1] + [2] * (nx - 1) + [1]
    for bcrns, tcrns in zip(hr_crnodes[0:-1], hr_crnodes[1:]):
        bcrns = list(chunks(repeatlist(bcrns, rlist), 2))
        tcrns = list(chunks(repeatlist(tcrns, rlist), 2))

        for bcrn, tcrn in zip(bcrns, tcrns):
            elen = next(gen_element_numbers)
            print(f"Element: {elen}, Nodei: {bcrn[0]}, Nodej: {bcrn[1]}, Nodek: {tcrn[1]}, Nodel: {tcrn[0]}")
            elnodes = [bcrn[0], bcrn[1], tcrn[1], tcrn[0]]
            elements.update({elen: elnodes})

def roundup(num):
    """Check if a float is a whole number if not round up"""
    return int(num) if num.is_integer() else int(np.ceil(num))


def main():
    # file path and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"
    path_plt = path_root / "plt"
    fname_svg = "sitereponse_soillayers.svg"
    fname_model = "sitereponse_model.csv"

    svgfile = path_plt.joinpath(fname_svg)
    mdfile = path_data.joinpath(fname_model)

    # thickness of soil layer [m]
    h_soillayer = 40
    # soil shear wave velocity [m/s]
    soil_vs = 250.0

    # wavelength parameters
    # highest frequency desired to be well resolved [Hz]
    fmax = 100.0
    # wavelength of the highest resolved frequency
    lamdamin = soil_vs / fmax
    # number of elements per one wavelength
    nele_wave = 10

    # center offset from the bottom left of the page (origin of the page, origin transformed)
    ox = 0.0
    oy = 0.0
    
    # offsets in x and y direction of the nodes
    lx = 50.0
    ly = 50.0
    
    # number of element in x and y direction
    nx = 1
    # trial for vertical element size
    # initial element size
    h_trial = lamdamin/nele_wave
    # if the number of elements is not an integer round up
    ny = roundup(h_soillayer/h_trial)
    print(f"Number of elements: nx = {nx}, ny = {ny}")

    # dictionary for node numbers and corresponding coordinates
    # {node_number: (x, y)}
    xycoords = {}

    # dictionary for element numbers and the corresponding nodes
    # {element_number: (nodei, nodej, nodek, nodel)}
    soil_elements = {}

    # start node number
    start_node_number = 1
    # svg size (2-tuple): (width, height)
    sz = (ox + (nx + 1) * lx, oy + (ny + 1) * ly)
    vbox = "0 0 " + str(int(sz[0])) + " " + str(int(sz[1]))

    dwg = svw.Drawing(
        filename=svgfile, profile="full", size=sz, viewBox=vbox
    )
    inkscape = Inkscape(dwg)
    # the corner coordinates are in increasing order of the nodes
    # with node number and (x, y) coordinates with origin at the bottom left
    # {1: (x1, y1), 2: (x2, y2), .....}
    dwg, corner_xyxycoords = draw_cornernodes(
        ox, oy, lx, ly, nx, ny, start_node_number, xycoords, inkscape, dwg
    )
    dwg = draw_elenumbers(ox, oy, lx, ly, nx, ny, start_node_number, xycoords, dwg)

    # dwg = draw_vlines(corner_xycoords, dwg)
    cr_last_node_number = (nx + 1) * (ny + 1)

    print(f"Corner nodes: 1 - {cr_last_node_number}")

    for key, values in xycoords.items():
        print(f"Node: {key}, (x, y): {values}")

    dwg = draw_hlines(xycoords, nx, ny, dwg)
    dwg = draw_vlines(xycoords, nx, ny, dwg)
    dwg = draw_elenumbers(ox, oy, lx, ly, nx, ny, start_node_number, xycoords, dwg)
    fournode_quadelement(xycoords, soil_elements, nx, ny)
    dwg.save()


if __name__ == "__main__":

    # basic_shapes("basic_shapes.svg")
    main()

