"""
Reads elements.tcl and RCJointModel3D.tcl from the Tcl reference directory
and generates the corresponding ops commands.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import ops as ops

_TCL_DIR = Path(__file__).parent / "G+4 Infilled Frame" / "AAC Block Infill" / "Pilotis"


def _parse_float(s: str) -> float:
    return float(s.replace("e", "e"))


def _parse_orient(tokens: list[str], idx: int) -> list[float]:
    """Parse -orient arguments starting at idx, return 6 floats."""
    return [_parse_float(tokens[idx]), _parse_float(tokens[idx + 1]),
            _parse_float(tokens[idx + 2]), _parse_float(tokens[idx + 3]),
            _parse_float(tokens[idx + 4]), _parse_float(tokens[idx + 5])]


def load_joint_nodes() -> None:
    """Load RCJointModel3D.tcl - joint nodes and their zeroLength elements."""
    tcl_file = _TCL_DIR / "RCJointModel3D.tcl"
    if not tcl_file.exists():
        print(f"Warning: {tcl_file} not found, skipping joint nodes")
        return

    lines = tcl_file.read_text().splitlines()
    node_lines = [l for l in lines if l.startswith("node ")]
    zl_lines = [l for l in lines if l.startswith("element zeroLength")]

    for line in node_lines:
        parts = line.split()
        tag = int(parts[1])
        x = _parse_float(parts[2])
        y = _parse_float(parts[3])
        z = _parse_float(parts[4])
        ops.node(tag, x, y, z)

    for line in zl_lines:
        parts = line.split()
        tag = int(parts[2])
        n1 = int(parts[3])
        n2 = int(parts[4])
        mats = []
        dirs = []
        orient: list[float] = []
        i = 5
        while i < len(parts):
            if parts[i] == "-mat":
                i += 1
                while i < len(parts) and parts[i] != "-dir":
                    mats.append(int(parts[i]))
                    i += 1
            elif parts[i] == "-dir":
                i += 1
                while i < len(parts) and parts[i] != "-orient":
                    dirs.append(int(parts[i]))
                    i += 1
            elif parts[i] == "-orient":
                orient = _parse_orient(parts, i + 1)
                break
            else:
                i += 1
        ops.element("zeroLength", tag, n1, n2,
                    "-mat", *mats,
                    "-dir", *dirs,
                    "-orient", *orient)


def load_elements() -> None:
    """Load elements.tcl - all structural elements, auxiliary nodes, rigidLinks, etc."""
    tcl_file = _TCL_DIR / "elements.tcl"
    if not tcl_file.exists():
        print(f"Warning: {tcl_file} not found, skipping elements")
        return

    lines = tcl_file.read_text().splitlines()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split()
        if not parts:
            continue

        cmd = parts[0]

        if cmd == "node":
            tag = int(parts[1])
            x = _parse_float(parts[2])
            y = _parse_float(parts[3])
            z = _parse_float(parts[4])
            ops.node(tag, x, y, z)

        elif cmd == "rigidLink" and parts[1] == "beam":
            master = int(parts[2])
            slave = int(parts[3])
            ops.rigidLink("beam", master, slave)

        elif cmd == "geomTransf":
            transf_type = parts[1]
            tag = int(parts[2])
            if transf_type == "Linear":
                vec_x = _parse_float(parts[3])
                vec_y = _parse_float(parts[4])
                vec_z = _parse_float(parts[5])
                ops.geomTransf("Linear", tag, vec_x, vec_y, vec_z)
            elif transf_type == "PDelta":
                vec_x = _parse_float(parts[3])
                vec_y = _parse_float(parts[4])
                vec_z = _parse_float(parts[5])
                ops.geomTransf("PDelta", tag, vec_x, vec_y, vec_z)

        elif cmd == "element":
            elem_type = parts[1]

            if elem_type == "elasticBeamColumn":
                tag = int(parts[2])
                n1 = int(parts[3])
                n2 = int(parts[4])
                a = _parse_float(parts[5])
                e = _parse_float(parts[6])
                gj = _parse_float(parts[7])
                j_calc = _parse_float(parts[8])
                iy = _parse_float(parts[9])
                iz = _parse_float(parts[10])
                transf = int(parts[11])
                ops.element("elasticBeamColumn", tag, n1, n2, a, e, gj, j_calc, iy, iz, transf)

            elif elem_type == "forceBeamColumn":
                tag = int(parts[2])
                n1 = int(parts[3])
                n2 = int(parts[4])
                transf = int(parts[5])
                # Parse: element forceBeamColumn tag n1 n2 transf HingeRadau ...
                if len(parts) >= 10 and parts[6] == "HingeRadau":
                    hinge_n1 = int(parts[7])
                    hinge_len1 = _parse_float(parts[8])
                    hinge_n2 = int(parts[9])
                    hinge_len2 = _parse_float(parts[10])
                    sec_tag = int(parts[11])
                    ops.element("forceBeamColumn", tag, n1, n2, transf,
                                "HingeRadau", hinge_n1, hinge_len1,
                                hinge_n2, hinge_len2, sec_tag)

            elif elem_type == "truss":
                tag = int(parts[2])
                n1 = int(parts[3])
                n2 = int(parts[4])
                area = _parse_float(parts[5])
                mat = int(parts[6])
                ops.element("truss", tag, n1, n2, area, mat)

            elif elem_type == "zeroLength":
                tag = int(parts[2])
                n1 = int(parts[3])
                n2 = int(parts[4])
                mats: list[int] = []
                dirs: list[int] = []
                orient: list[float] = []
                i = 5
                while i < len(parts):
                    if parts[i] == "-mat":
                        i += 1
                        while i < len(parts) and parts[i] not in ("-dir", "-orient"):
                            mats.append(int(parts[i]))
                            i += 1
                    elif parts[i] == "-dir":
                        i += 1
                        while i < len(parts) and parts[i] not in ("-mat", "-orient"):
                            dirs.append(int(parts[i]))
                            i += 1
                    elif parts[i] == "-orient":
                        orient = _parse_orient(parts, i + 1)
                        break
                    else:
                        i += 1
                ops.element("zeroLength", tag, n1, n2,
                            "-mat", *mats,
                            "-dir", *dirs,
                            "-orient", *orient)


def run() -> None:
    """Load both joint nodes and elements from Tcl files."""
    print("Loading joint nodes from RCJointModel3D.tcl...")
    load_joint_nodes()
    print("Loading elements from elements.tcl...")
    load_elements()
    print("Done loading from Tcl files.")


if __name__ == "__main__":
    run()
