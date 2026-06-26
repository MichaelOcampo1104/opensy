#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
from pathlib import Path
import meshio
from itertools import count, zip_longest, islice, takewhile
from collections import defaultdict, namedtuple


class Mesh:
    """Get pertinent information, nodes, elements and physical tags, from Gmsh mesh .msh file"""

    def __init__(self, fpath):
        self.fpath = fpath
        # use meshio to read the Gmsh .msh file
        self.mesh = meshio.read(self.fpath)
        # the node data is {"id": int, "xy": (xc, yc)}
        # get the nodes from the mesh file
        self.nodes = self.get_nodes()
        # the tags data is {"node_id": int, "element_type": string, "tags": [string1, string2, ... ]}
        self.physical_tags = self.get_physical_tags()

        # any entity, node, line, cells (elements in finite elements lingo), surfaces, volumes
        # are elements in Gmsh
        # [{element id: int, element_type: string, physical_tag: [string1, string2,...], nodes: [int, int, ..]}]
        # current physical_tag is not a list because the current version of meshio only
        # returns the first physical tag for one element, this has been addressed in the
        # master branch but not yet released. This has to be fixed in future.
        self.elements_data = self.assemble_elements_data()
        # collect physical tags for all nodes
        self.nodes_tags = self.assemble_nodes_tags()
        self.tags_nodes = self.assemble_tags_nodes()

    def get_nodes(self):
        """Get the nodes from the Gmsh file
        Return a dictionary {node_id: (xc, yc),....  }"""
        Point = namedtuple("Point", ("x", "y", "z"))
        nodes = {}
        for idx, node in enumerate(self.mesh.points):
            nodes.update(
                {
                    idx
                    + 1: Point(round(node[0], 3), round(node[1], 3), round(node[2], 3))
                }
            )
        return nodes

    def get_physical_tags(self):
        """Get the physical tags of various entities, such as node, line"""
        physical_tags = {}
        for key, value in self.mesh.field_data.items():
            physical_tags.update({value[0]: key})
        return physical_tags

    def assemble_elements_data(self):
        """Assoicate entities with nodes and tags,
        these entities were defined during model creation time in Gmsh
        with Physical entity tags. 
        list of dictionaries
        [{element_id: int, element_type: string, physical_tags: string, nodes: [int,...]}]"""

        cntel = count(start=1)
        elements_data = []
        for (k0, v0), (k1, v1) in zip(
            self.mesh.cells_dict.items(),
            self.mesh.cell_data_dict["gmsh:physical"].items(),
        ):
            for a1, a2 in zip(v0, v1):
                elements_data.append(
                    {
                        "element_id": next(cntel),
                        "element_type": k0,
                        "physical_tags": self.physical_tags[a2],
                        "nodes": list(np.array(a1) + 1),
                    }
                )
        return elements_data

    def assemble_nodes_tags(self):
        """Create a dictionary with node numbers as the key and the list of physical tags as the value
        ref: https://docs.python.org/3.3/library/collections.html#collections.defaultdict
        the refernce on using the defaultdict as it is intended to use here.
        elements_data is a list of dictionarys of element data
        {"elenum": int, "element_type": string, "physical_tags": physical_tags[string], "nodes": list[int]}
        """
        d = defaultdict(list)
        for el_data in self.elements_data:
            ls = zip_longest(
                el_data["nodes"],
                [el_data["physical_tags"]],
                fillvalue=el_data["physical_tags"],
            )
            # collect all tags for a node
            for k, v in ls:
                if v not in d[k]:
                    d[k].append(v)
        return d

    def assemble_tags_nodes(self):
        """Return the nodes associated with physical tags to a file
        fid of the output file,
        physical_tags a list of physical tags used in Gmsh
        """
        d = defaultdict(list)
        for nd, tags in self.nodes_tags.items():
            ls = zip_longest(tags, [nd], fillvalue=nd)
            # collect all nodes for a tag
            for k, v in ls:
                d[k].append(v)
        return d

    def show_nodes(self):
        """Write the list of nodes to the console"""
        for k, p in self.nodes.items():
            print(f"Node: {k}, x: {p.x}, y: {p.y}, z: {p.z}")

    def show_physical_tags(self):
        """Write the physical tags for various entities such as nodes, lines, quads
        to the console"""
        for key, value in self.physical_tags.items():
            print(f"Tag id: {key}, Physical tag: {value}")

    def show_elements_data(self):
        for eld in self.elements_data:
            print(
                f"Element id: {eld['element_id']}, Element type: {eld['element_type']}, Physical tag: {eld['physical_tags']}, Nodes: {eld['nodes']}"
            )

    def show_nodes_physical_tags(self):
        for k, v in self.nodes_tags.items():
            # if "lower_boundary" in v:
            print(f"Node: {k}, Tags: {v}")

    def show_tags_nodes(self):
        for k, v in self.tags_nodes.items():
            # if "lower_boundary" in v:
            print(f"Tag: {k}, Nodes: {v}")

    def add_node_rule(self, condition, action):
        """Add not rule"""
        self.node_rules.append((condition, action))

    def write_nodes(self, fid):
        with open(fid, "w") as f:
            print(f"Nodes:", file=f)
            print(f"{'ID'}, {'X'}, {'Y'}, {'Z'}", file=f)
            for k, p in self.nodes.items():
                print(f"{k}, {p.x:.3f}, {p.y:.3f}, {p.z:.3f}", file=f)

    def write_elements(self, fid):
        """Write the elements, tags and node connectivities with element type"""
        # gmsh element tags
        gmsh_eletags = ["quad", "quad8", "quad9"]
        # temporary list
        ele2write = []
        for eld in self.elements_data:
            #     print(
            #         f"Element id: {eld['element_id']}, Element type: {eld['element_type']}, Physical tag: {eld['physical_tags']}, Nodes: {eld['nodes']}"
            #     )
            # check = [el in a for el in gmsh_eletags]
            # if any(check):
            if eld["element_type"] in gmsh_eletags:
                ele2write.append(
                    [
                        eld["element_id"],
                        eld["nodes"],
                        eld["element_type"],
                        eld["physical_tags"],
                    ]
                )
        with open(fid, "w") as f:
            print(f"Elements:", file=f)
            print(
                f"{'ID'}, {', '.join('Node' + str(i + 1) for i in range(len(ele2write[0][1])))}, Type, Physicaltag",
                file=f,
            )
            for el in ele2write:
                print(
                    f"{el[0]}, {', '.join(str(nd) for nd in el[1])}, {el[2]}, {el[3]}",
                    file=f,
                )

    def write_tags(self, fid, tags):
        """Write tags and associated nodes
        fid: file id
        tags: list of tags and the associated nodes to be written to file"""

        def slice_iterable(iterable, chunk):
            """Slice an iterable into chunks of chunk
            ref: https://stackoverflow.com/questions/38272662/python-how-to-limit-number-of-integers-printed-in-a-line"""
            _it = iter(iterable)
            return takewhile(bool, (tuple(islice(_it, chunk)) for _ in count(0)))

        # write at most 10 numbers per line
        nchunk = 10
        with open(fid, "w") as f:
            print(f"Nodes associated with physical tags in Gmsh:", file=f)
            for tag in tags:
                print(f"Start_tag:{tag}", file=f)
                for chunk in slice_iterable(self.tags_nodes[tag], nchunk):
                    print(", ".join(str(num).strip() for num in chunk), file=f)

                # if tag == "EqualDOF_cnodes":
                #     print(
                #         f"{', '.join(str(nd).strip() for nd in self.tags_nodes[tag][::-1])}",
                #         file=f,
                #     )
                # else:
                #     print(
                #         f"{', '.join(str(nd).strip() for nd in self.tags_nodes[tag])}",
                #         file=f,
                #     )
                print(f"End_tag:{tag}\n", file=f)


def filter_listofdict(list_of_dicts, key, val_list):
    return [d for d in list_of_dicts if d[key] in val_list]


def main():

    path_root = Path(r"../")
    path_msh = path_root / "gmsh"

    fname_msh = "2d_dynamicslopeanalysis_ex1_gmsh.msh"
    fin = path_msh.joinpath(fname_msh)
    # gmesh = meshio.read(fin)

    # create three seperate output files for writing the nodes, elements and fixities
    fname_nodes = fname_msh.replace(".msh", "_nodes.txt")
    fname_elements = fname_msh.replace(".msh", "_elements.txt")
    fname_tags = fname_msh.replace(".msh", "_tags.txt")

    fnodes = path_msh.joinpath(fname_nodes)
    felements = path_msh.joinpath(fname_elements)
    ftags = path_msh.joinpath(fname_tags)

    mesh = Mesh(fin)
    # mesh.show_nodes()
    mesh.write_nodes(fnodes)
    # mesh.show_physical_tags()
    # mesh.show_elements_data()
    mesh.write_elements(felements)
    # mesh.show_nodes_physical_tags()
    # mesh.assemble_tags_nodes()
    # mesh.show_tags_nodes()
    mesh.write_tags(
        ftags,
        [
            "EQ_motion",
            "Fix_010",
            "left_outer_slope_boundary",
            "left_inner_slope_boundary",
            "left_outer_foundation_boundary",
            "left_inner_foundation_boundary",
            "right_outer_foundation_boundary",
            "right_inner_foundation_boundary",
        ],
    )


if __name__ == "__main__":
    main()
