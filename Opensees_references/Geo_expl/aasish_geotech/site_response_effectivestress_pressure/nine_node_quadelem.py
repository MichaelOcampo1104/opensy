#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import openseespy.opensees as ops
from pathlib import Path
from itertools import count, chain, repeat

# Example problem:
# Description: 1D consolidation
# Original solution by: Christopher McGann and Pedro Arduino, University of Washington
# ref: https://opensees.berkeley.edu/wiki/index.php/One-dimensional_Consolidation
# Units: kN, m, sec


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


def create_nodes(cxs, cys, start_node_number, xycoords):
    # print(f"Cxs: {cxs}")
    # print(f"Cys: {cys}")
    # create a itertools generator count
    gen_node_number = count(start_node_number)
    xv, yv = np.meshgrid(cxs, cys, indexing="ij")
    coord_grid = np.array([xv, yv])
    gshape = coord_grid.shape

    for y in range(gshape[2]):
        for x in range(gshape[1]):
            xc, yc = coord_grid[:, x, y]
            node_number = next(gen_node_number)
            print(f"Node number: {node_number}, xc: {xc}, yc: {yc}")
            ops.node(node_number, xc, yc)
            xycoords.update({node_number: (xc, yc)})
    return xycoords


def create_elements(
    soil_elements, hr_crnodes, hr_tbnodes, hr_lrnodes, hr_cnnodes, eprop
):
    thick = eprop["thickness"]
    mattag = eprop["material_tag"]
    modK = eprop["bulk_modulus"]
    waterdensity = eprop["water_density"]
    k_hor = eprop["horizontal_permeability"]
    k_ver = eprop["vertical_permeability"]
    accg_x = eprop["g_xdir"]
    accg_y = eprop["g_ydir"]
    nx = len(hr_cnnodes[0])
    gen_element_numbers = count(1)

    rlist = [1] + [2] * (nx - 1) + [1]
    for bcrns, tcrns, btbns, ttbns, lrns, cnns in zip(
        hr_crnodes[0:-1],
        hr_crnodes[1:],
        hr_tbnodes[0:-1],
        hr_tbnodes[1:],
        hr_lrnodes,
        hr_cnnodes,
    ):
        bcrns = list(chunks(repeatlist(bcrns, rlist), 2))
        tcrns = list(chunks(repeatlist(tcrns, rlist), 2))
        lrns = list(chunks(repeatlist(lrns, rlist), 2))

        for bcrn, tcrn, btbn, ttbn, lrn, cnn in zip(
            bcrns, tcrns, btbns, ttbns, lrns, cnns
        ):
            elen = next(gen_element_numbers)
            # print(bcrn, tcrn, btbn, ttbn, lrn, cnn)
            elnodes = [
                bcrn[0],
                bcrn[1],
                tcrn[1],
                tcrn[0],
                btbn,
                lrn[1],
                ttbn,
                lrn[0],
                cnn,
            ]
            soil_elements.update({elen: elnodes})

            ops.element(
                "9_4_QuadUP",
                elen,
                *elnodes,
                thick,
                mattag,
                modK,
                waterdensity,
                k_hor,
                k_ver,
                accg_x,
                accg_y,
            )

    return soil_elements


class Node:
    """
    Defines the node numbers (nn) and the nodal coordinates (xn, yn)
    """

    def __init__(self, nn=1, xc=0, yc=0):
        self.nn = nn
        self.coords = (xc, yc)

    def set_node_number(self, nn):
        self.nn = nn
        return self.nn

    def set_node_coords(self, coords):
        if isinstance(coords, tuple) and len(coords) == 2:
            self.coords = coords
        else:
            raise ValueError("Coordinates must be tuple (xc, yc)")
        return self.coords

    def get_node_number(self):
        return self.nn

    def get_node_coords(self):
        return self.coords

    @property
    def node_info(self):
        return (self.nn, self.coords)


class Element_Nine_Four_Node_QuadUP:
    """
    """

    def __init__(self, nele=1, nn=1, xc=0.0, yc=0.0, dx=1.0, dy=1.0):
        """
        xc: x-coordinate of the origin
        yc: y-coordinate of the origin
        dx: length of element in x-direction
        dy: length of element in y-direction
        """
        self.xc = xc
        self.yc = yc
        self.dx = dx
        self.dy = dy
        self.nele = nele
        node = Node()
        #
        pass

    def set_origin(self, xc, yc):
        self.xc = xc
        self.yc = yc
        return (self.xc, self.yc)

    def set_element_size(self, dx, dy):
        self.dx = dx
        self.dy = dy
        return (self.dx, self.dy)

    def get_origin(self):
        # print(f"(xc, yc): {self.xc, self.yc}")
        return (self.xc, self.yc)

    def get_element_size(self):
        # print(f"Element size (dx, dy): {self.dx, self.dy}")
        return (self.dx, self.dy)

    def make_nodes(self):
        x0 = self.xc
        y0 = self.yc
        dx = self.dx
        dy = self.dy
        nn = self.nn
        nele = self.nele
        nodes = []
        for 
        # nodes = [
        #     Node(nele, x0, y0),
        #     Node(nele + 1, x0 + dx, y0),
        #     Node(nele + 2, x0 + dx, y0 + dx),
        #     Node(nele + 3, x0, y0 + dx),
        #     Node(nele + 4, x0 + dx / 2, y0),
        #     Node(nele + 5, x0 + dx, y0 + dx / 2),
        #     Node(nele + 6, x0 + dx / 2, y0 + dy),
        #     Node(nele + 7, x0, y0 + dy / 2),
        #     Node(nele + 8, x0 + dx / 2, y0 + dy / 2),
        # ]


def main():
    # file path and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"

    # center offset from the bottom left of the page (origin of the page, origin transformed)
    ox = 0.0
    oy = 0.0

    # size of elements in x and y direction of the nodes
    lx = 1.0
    ly = 1.0

    # number of element in x and y direction
    nx = 1
    ny = 10

    # start node number
    start_node_number = 1

    node = Node()
    print(f"None number: {node.nn}, xc: {node.coords[0]}, yc: {node.coords[1]}")
    nn = node.set_node_number(2)
    ncord = node.set_node_coords((2, 2))
    print(f"Node info: {node.node_info}")
    # ninenode = nine_node_quad_element(xc=2)
    # origin = ninenode.get_origin()
    # elesz = ninenode.get_element_size()
    # print(elesz)

    # ninenode.set_origin(1, 1)
    # ninenode.set_element_size(0.5, 0.5)

    # norgin = ninenode.get_origin()
    # nelesz = ninenode.get_element_size()

    # print(norgin)
    # print(nelesz)


if __name__ == "__main__":

    # basic_shapes("basic_shapes.svg")
    main()

