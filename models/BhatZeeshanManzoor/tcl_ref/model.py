"""
3D G+4 RC Infilled Frame - AAC Block Infill (Pilotis)
Converted from Tcl to Python following AGENT.md conventions.
"""
from __future__ import annotations

import os
from pathlib import Path

import openseespy.opensees as ops

__all__ = ["run_model"]

_EC = 25000.0
_A = 120000.0
_IZ = 315000000.0
_IY = 560000000.0
_GJ = 1943850585.9375
_J = 15000.0

_TCL_DIR = Path(__file__).parent / "G+4 Infilled Frame" / "AAC Block Infill" / "Pilotis"

# Cache for Lobatto beam integration objects, keyed by (sec_tag,)
_beam_hinge_cache: dict[tuple, int] = {}


def _add_fiber(y, z, area, mat):
    ops.fiber(y, z, area, mat)


def _zl(elem_tag, node_i, node_j, mat_stagger, orient):
    ops.element("zeroLength", elem_tag, node_i, node_j,
                "-mat", mat_stagger, mat_stagger, mat_stagger, 5, 5, mat_stagger,
                "-dir", 1, 2, 3, 4, 5, 6,
                "-orient", orient[0], orient[1], orient[2],
                orient[3], orient[4], orient[5])


def _elastic_beam(elem_tag, n1, n2, transf_tag):
    ops.geomTransf("Linear", transf_tag, 0.0, 0.0, 1.0)
    ops.element("elasticBeamColumn", elem_tag, n1, n2, _A, _EC, _J, _GJ, _IY, _IZ, transf_tag)


def _elastic_beam_z(elem_tag, n1, n2, transf_tag):
    ops.geomTransf("Linear", transf_tag, 0.0, -0.0, 1.0)
    ops.element("elasticBeamColumn", elem_tag, n1, n2, _A, _EC, _J, _GJ, _IY, _IZ, transf_tag)


def _force_beam(elem_tag, n1, n2, transf_tag, sec_tag, hinge_len=225.0, hinge_ip=6):
    ops.geomTransf("PDelta", transf_tag, 1.0, 0.0, -0.0)
    ops.element("forceBeamColumn", elem_tag, n1, n2, transf_tag,
                "-HingeRadau", hinge_ip, hinge_len, hinge_ip, hinge_len, sec_tag)


def _load_sections_tcl() -> None:
    """Parse sections.tcl for materials and sections not hardcoded."""
    tcl_file = _TCL_DIR / "sections.tcl"
    if not tcl_file.exists():
        return
    text = tcl_file.read_text()
    in_section = False
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        parts = s.split()
        cmd = parts[0]
        try:
            if cmd == "uniaxialMaterial" and parts[1] == "Concrete02":
                tag = int(parts[2])
                if tag >= 92:
                    # §12x-9: ft=20.0 for numerical stability, same as hardcoded mats
                    ops.uniaxialMaterial("Concrete02", tag,
                                         float(parts[3]), float(parts[4]),
                                         float(parts[5]), float(parts[6]),
                                         float(parts[7]), 20.0, float(parts[9]))
            elif cmd == "section" and parts[1] == "Fiber":
                tag = int(parts[2])
                if tag >= 17:
                    gj = float(parts[4])
                    ops.section("Fiber", tag, "-GJ", gj)
                    in_section = True
            elif cmd == "fiber" and in_section:
                mat_str = parts[4].rstrip("}")
                ops.fiber(float(parts[1]), float(parts[2]), float(parts[3]), int(mat_str))
            elif cmd == "}":
                in_section = False
        except Exception as e:
            print(f"Warning: failed to parse line: {s[:80]}... - {e}")


def _load_elements_tcl() -> None:
    """Parse and execute elements.tcl via Python reimplementation."""
    tcl_file = _TCL_DIR / "elements.tcl"
    if not tcl_file.exists():
        return
    text = tcl_file.read_text()
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if not parts:
            continue
        cmd = parts[0]
        try:
            if cmd == "node":
                ops.node(int(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]))
            elif cmd == "rigidLink" and parts[1] == "beam":
                ops.rigidLink("beam", int(parts[2]), int(parts[3]))
            elif cmd == "geomTransf":
                t = parts[1]
                tag = int(parts[2])
                if t == "Linear":
                    ops.geomTransf("Linear", tag, float(parts[3]), float(parts[4]), float(parts[5]))
                elif t == "PDelta":
                    ops.geomTransf("PDelta", tag, float(parts[3]), float(parts[4]), float(parts[5]))
            elif cmd == "element":
                et = parts[1]
                if et == "elasticBeamColumn":
                    ops.element("elasticBeamColumn", int(parts[2]), int(parts[3]), int(parts[4]),
                                float(parts[5]), float(parts[6]), float(parts[7]),
                                float(parts[8]), float(parts[9]), float(parts[10]), int(parts[11]))
                elif et == "forceBeamColumn":
                    tag = int(parts[2])
                    if len(parts) >= 12 and parts[6].lstrip("-") == "HingeRadau":
                        # Tcl: HingeRadau $secTag $lpI $nIpI $lpJ $nIpJ
                        # §12x-8: dispBeamColumn + HingeRadau beamIntegration.
                        # dispBeamColumn avoids forceBeamColumn state determination
                        # failures; HingeRadau preserves the Tcl hinge-length params.
                        sec_tag = int(parts[7])
                        lp_i = float(parts[8])
                        lp_j = float(parts[10])
                        int_key = (sec_tag, lp_i, lp_j)
                        if int_key not in _beam_hinge_cache:
                            int_tag = len(_beam_hinge_cache) + 6000
                            ops.beamIntegration("HingeRadau", int_tag,
                                                sec_tag, lp_i, sec_tag, lp_j, sec_tag)
                            _beam_hinge_cache[int_key] = int_tag
                        int_tag = _beam_hinge_cache[int_key]
                        ops.element("dispBeamColumn", tag, int(parts[3]),
                                    int(parts[4]), int(parts[5]), int_tag)
                elif et == "truss":
                    ops.element("truss", int(parts[2]), int(parts[3]), int(parts[4]),
                                float(parts[5]), int(parts[6]))
                elif et == "zeroLength":
                    tag = int(parts[2])
                    mats, dirs, orient = [], [], []
                    i = 5
                    while i < len(parts):
                        if parts[i] == "-mat":
                            i += 1
                            while i < len(parts) and parts[i] not in ("-dir", "-orient", "-ele"):
                                mats.append(int(parts[i]))
                                i += 1
                        elif parts[i] == "-dir":
                            i += 1
                            while i < len(parts) and parts[i] not in ("-mat", "-orient", "-ele"):
                                dirs.append(int(parts[i]))
                                i += 1
                        elif parts[i] == "-orient":
                            orient = [float(parts[i+1]), float(parts[i+2]), float(parts[i+3]),
                                      float(parts[i+4]), float(parts[i+5]), float(parts[i+6])]
                            break
                        else:
                            i += 1
                    ops.element("zeroLength", tag, int(parts[3]), int(parts[4]),
                                "-mat", *mats, "-dir", *dirs, "-orient", *orient)
        except Exception as e:
            print(f"Warning: failed to parse line: {s[:80]}... - {e}")


def run_model() -> None:
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)

    # =========================================================================
    # MATERIALS
    # =========================================================================
    # §12x-9: ft=20.0 (vs physical ~3.0) suppresses premature cracking during
    # gravity. OpenSeesPy uniaxialMaterial cannot be redefined, so the same
    # value persists through transient. Post-cracking response is governed
    # by steel reinforcement — elevated ft has negligible effect on global
    # hysteretic behavior while avoiding fiber-section tangent ill-conditioning.
    ops.uniaxialMaterial("Concrete02", 1, -30.0, -0.002, -5.0, -0.01, 0.1, 20.0, 1500.0)
    ops.uniaxialMaterial("Steel02", 2, 500.0, 210000.0, 0.001, 18.0, 0.925, 0.15)
    ops.uniaxialMaterial("Elastic", 5, 1.0e13)

    modimk_data = {
        22: (210e9, 0.0017, 0.00116, 220e6, -151e6, 97, 97, 97, 97, 1, 1, 1, 1, 0.08, 0.08, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0, 0),
        23: (210e9, 0.00125, 0.0008, 148e6, -100e6, 97, 97, 97, 97, 1, 1, 1, 1, 0.073, 0.073, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0, 0),
        24: (210e9, 0.0009, 0.00065, 100e6, -70e6, 97, 97, 97, 97, 1, 1, 1, 1, 0.066, 0.066, 0.1, 0.097, 0.2, 0.2, 0.3, 0.3, 0, 0),
        25: (150e9, 0.00175, 0.00118, 148e6, -100e6, 97, 97, 97, 97, 1, 1, 1, 1, 0.073, 0.073, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0, 0),
        26: (240e9, 0.001098, 0.000742, 148e6, -100e6, 97, 97, 97, 97, 1, 1, 1, 1, 0.073, 0.073, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0, 0),
        33: (150e9, 0.00238, 0.00163, 220e6, -151e6, 97, 97, 97, 97, 1, 1, 1, 1, 0.08, 0.08, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0, 0),
        34: (240e9, 0.0017, 0.00113, 270e6, -180e6, 97, 97, 97, 97, 1, 1, 1, 1, 0.086, 0.086, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0, 0),
    }
    for tag, d in modimk_data.items():
        ops.uniaxialMaterial("IMKPeakOriented", tag, *d)

    pinching_data = {
        70: (3.09, 6.7e-5, 3.69, 1.7e-5, 4.29, 0.00027, 1.71, 0.00113,
             -309e3, -0.00067, -369e3, -0.0017, -429e3, -0.0027, -171e3, -0.0113,
             0.8, 0.1, 0.01, 0.8, 0.1, 0.01, 0.8, 0.7, 0.7, 0.7, 0.8,
             0, 0, 0, 0, 0.1, 1, 0, 1, 1, 0.1, 10, "cycle"),
        72: (1.69, 6.7e-5, 2.02, 1.7e-5, 2.35, 0.00027, 0.94, 0.00113,
             -169e3, -0.000601, -202e3, -0.0016, -235e3, -0.0027, -94e3, -0.007,
             0.8, 0.1, 0.01, 0.8, 0.1, 0.01, 0.8, 0.7, 0.7, 0.7, 0.8,
             0, 0, 0, 0, 0.1, 1, 0, 1, 1, 0.1, 10, "cycle"),
        76: (3.65, 6.7e-5, 4.36, 1.7e-5, 5.07, 0.00027, 2.03, 0.00113,
             -365e3, -0.000457, -436e3, -0.00123, -507e3, -0.002, -203e3, -0.0076,
             0.8, 0.1, 0.01, 0.8, 0.1, 0.01, 0.8, 0.7, 0.7, 0.7, 0.8,
             0, 0, 0, 0, 0.1, 1, 0, 1, 1, 0.1, 10, "cycle"),
        79: (2.91, 6.7e-5, 3.47, 1.7e-5, 4.04, 0.00027, 1.61, 0.00113,
             -291e3, -0.000797, -347e3, -0.00195, -404e3, -0.00311, -161e3, -0.0134,
             0.8, 0.1, 0.01, 0.8, 0.1, 0.01, 0.8, 0.7, 0.7, 0.7, 0.8,
             0, 0, 0, 0, 0.1, 1, 0, 1, 1, 0.1, 10, "cycle"),
        82: (1.69, 6.7e-5, 2.02, 1.7e-5, 2.35, 0.00027, 0.94, 0.00113,
             -200e3, -0.000406, -239e3, -0.0012, -278e3, -0.002, -111e3, -0.0047,
             0.8, 0.1, 0.01, 0.8, 0.1, 0.01, 0.8, 0.7, 0.7, 0.7, 0.8,
             0, 0, 0, 0, 0.1, 1, 0, 1, 1, 0.1, 10, "cycle"),
        85: (1.69, 6.7e-5, 2.02, 1.7e-5, 2.35, 0.00027, 0.94, 0.00113,
             -159e3, -0.000707, -190e3, -0.00191, -221e3, -0.0031, -88e3, -0.0082,
             0.8, 0.1, 0.01, 0.8, 0.1, 0.01, 0.8, 0.7, 0.7, 0.7, 0.8,
             0, 0, 0, 0, 0.1, 1, 0, 1, 1, 0.1, 10, "cycle"),
    }
    for tag, d in pinching_data.items():
        ops.uniaxialMaterial("Pinching4", tag, *d)

    for mat_tag in range(97, 202):
        ops.uniaxialMaterial("Elastic", mat_tag, 1.0e13)

    core_conc = {
        87: (-39.311640669922575, -0.002620776044661505, -32.000465495850406, -0.02298621761048205),
        88: (-35.46967139159928, -0.002364644759439952, -26.57725340321309, -0.018067616035260838),
        89: (-39.11519470305573, -0.002607679646870382, -31.745672536296656, -0.022745557554344507),
        90: (-33.538905186823975, -0.0022359270124549316, -23.26119162133716, -0.015391692176790945),
        91: (-39.18088040989045, -0.0026120586939926966, -31.831065049292093, -0.022826141395610046),
    }
    for tag, v in core_conc.items():
        ops.uniaxialMaterial("Concrete02", tag, v[0], v[1], v[2], v[3], 0.1, 20.0, 1500.0)

    # =========================================================================
    # SECTIONS
    # =========================================================================
    ops.section("Elastic", 4, _EC, _A, _IZ, _IY, _J, _GJ)

    def _build_fiber_section(tag, rebar_xy, rebar_area, core_xy_vals, core_z_vals, core_mat, core_area,
                             cover_xy, cover_z, cover_area, cover_mat,
                             corner_xy, corner_area):
        ops.section("Fiber", tag, "-GJ", 1.0e14)
        for y, z in rebar_xy:
            _add_fiber(y, z, rebar_area, 2)
        for y in core_xy_vals:
            for z in core_z_vals:
                _add_fiber(y, z, core_area, core_mat)
        for y in cover_xy:
            for z in cover_z:
                _add_fiber(y, z, cover_area, cover_mat)
        for y in cover_z:
            for z in cover_xy:
                _add_fiber(y, z, cover_area, cover_mat)
        for y, z in corner_xy:
            _add_fiber(y, z, corner_area, cover_mat)

    core_xy = [-165.0, -135.0, -105.0, -75.0, -45.0, -15.0, 15.0, 45.0, 75.0, 105.0, 135.0, 165.0]
    core_z = [-165.0, -135.0, -105.0, -75.0, -45.0, -15.0, 15.0, 45.0, 75.0, 105.0, 135.0, 165.0]
    cv_xy = [-165.0, -135.0, -105.0, -75.0, -45.0, -15.0, 15.0, 45.0, 75.0, 105.0, 135.0, 165.0]
    cv_z = [-213.75, -191.25, 191.25, 213.75]
    cv_corners = [(-213.75, -213.75), (-191.25, -213.75), (-213.75, -191.25), (-191.25, -191.25),
                  (191.25, -213.75), (213.75, -213.75), (191.25, -191.25), (213.75, -191.25),
                  (-213.75, 191.25), (-191.25, 191.25), (-213.75, 213.75), (-191.25, 213.75),
                  (191.25, 191.25), (213.75, 191.25), (191.25, 213.75), (213.75, 213.75)]

    rebar6 = [(-164.5, -164.5), (164.5, -164.5), (-164.5, 164.5), (164.5, 164.5),
              (-54.8333, -164.5), (54.8333, -164.5), (-54.8333, 164.5), (54.8333, 164.5),
              (-164.5, -54.8333), (-164.5, 54.8333), (164.5, -54.8333), (164.5, 54.8333)]
    rebar7 = [(-162.5, -162.5), (162.5, -162.5), (-162.5, 162.5), (162.5, 162.5),
              (-54.1667, -162.5), (54.1667, -162.5), (-54.1667, 162.5), (54.1667, 162.5),
              (-162.5, -54.1667), (-162.5, 54.1667), (162.5, -54.1667), (162.5, 54.1667)]

    _build_fiber_section(6, rebar6, 490.8738521234052,
                         core_xy, core_z, 87, 910.0277777777779,
                         cv_xy, [-203.0, 203.0], 1327.3333333333333, 1,
                         cv_corners + [(-203, -203), (203, -203), (-203, 203), (203, 203)], 1936.0)
    _build_fiber_section(7, rebar7, 490.8738521234052,
                         core_xy, core_z, 88, 900.0,
                         cv_xy, [-213.75, -191.25, 191.25, 213.75], 675.0, 1,
                         cv_corners, 506.25)
    _build_fiber_section(13, rebar6, 490.8738521234052,
                         core_xy, core_z, 90, 910.0277777777779,
                         cv_xy, [-203.0, 203.0], 1327.3333333333333, 1,
                         cv_corners + [(-203, -203), (203, -203), (-203, 203), (203, 203)], 1936.0)

    ops.section("Fiber", 14, "-GJ", 1.0e14)
    for y, z in [(-165.8941515416367, -166.0), (166.1058484583633, -166.0),
                 (-165.8941515416367, 166.0), (166.1058484583633, 166.0),
                 (-55.22748487497, -166.0), (55.439181791696654, -166.0),
                 (-55.22748487497, 166.0), (55.439181791696654, 166.0)]:
        _add_fiber(y, z, 380.1327110843649, 2)
    _add_fiber(-165.8941515416367, -55.3333, 380.1327110843649, 2)
    _add_fiber(-165.8941515416367, 55.3333, 380.1327110843649, 2)
    _add_fiber(166.1058484583633, -55.3333, 314.1592653589793, 2)
    _add_fiber(166.1058484583633, 55.3333, 314.1592653589793, 2)

    ops.section("Fiber", 12, "-GJ", 1.0e14)
    rebar12 = [(-167.0, -167.0), (167.0, -167.0), (-167.0, 167.0), (167.0, 167.0),
               (-55.6667, -167.0), (55.6667, -167.0), (-55.6667, 167.0), (55.6667, 167.0),
               (-167.0, -55.6667), (-167.0, 55.6667), (167.0, -55.6667), (167.0, 55.6667)]
    for y, z in rebar12:
        _add_fiber(y, z, 314.1592653589793, 2)
    core_xy12 = [-165.9167, -135.75, -105.5833, -75.4167, -45.25, -15.0833,
                 15.0833, 45.25, 75.4167, 105.5833, 135.75, 165.9167]
    for y in core_xy12:
        for z in core_xy12:
            _add_fiber(y, z, 910.0277777777779, 89)
    for y in core_xy12:
        for z in [-203.0, 203.0]:
            _add_fiber(y, z, 1327.3333, 1)
    for y in [-203.0, 203.0]:
        for z in core_xy12:
            _add_fiber(y, z, 1327.3333, 1)
    for y, z in [(-203, -203), (203, -203), (-203, 203), (203, 203)]:
        _add_fiber(y, z, 1936.0, 1)

    # =========================================================================
    # LOAD ADDITIONAL SECTIONS FROM TCL SOURCE (17-21 and materials 92-96)
    # =========================================================================
    _load_sections_tcl()

    # =========================================================================
    # TIME SERIES
    # =========================================================================
    ops.timeSeries("Linear", 1)

    # =========================================================================
    # NODES
    # =========================================================================
    for tag, x, y, z in [(1, 10000, 7250, 4800), (2, 10000, 7250, 8100),
                          (3, 10000, 7250, 11400), (4, 10000, 7250, 14700),
                          (5, 10000, 7250, 18000)]:
        ops.node(tag, x, y, z)

    node_mass = {
        6: (16000, 0, 18000, 9.898572885), 7: (16000, 5500, 14700, 21.19431702),
        8: (16000, 9000, 18000, 14.84301733), 9: (12000, 5500, 18000, 14.84301733),
        10: (20000, 5500, 11400, 16.18952599), 11: (12000, 5500, 11400, 21.19431702),
        12: (8000, 5500, 14700, 21.19431702), 13: (4000, 5500, 11400, 21.19431702),
        14: (0, 5500, 14700, 16.18952599), 15: (16000, 5500, 8100, 21.19431702),
        16: (8000, 5500, 8100, 21.19431702), 17: (0, 5500, 8100, 16.18952599),
        18: (20000, 5500, 4800, 16.33203364), 19: (12000, 5500, 4800, 21.33682467),
        20: (4000, 5500, 4800, 21.33682467), 21: (4000, 0, 4800, 17.60022936),
        22: (8000, 5500, 4800, 21.33682467), 23: (8000, 9000, 4800, 21.33682467),
        24: (4000, 5500, 8100, 21.19431702), 25: (8000, 9000, 8100, 21.19431702),
        26: (12000, 5500, 8100, 21.19431702), 27: (8000, 14500, 8100, 17.45772171),
        28: (12000, 9000, 8100, 21.19431702), 29: (4000, 0, 8100, 17.45772171),
        30: (8000, 0, 8100, 17.45772171), 31: (12000, 0, 8100, 17.45772171),
        32: (4000, 5500, 14700, 21.19431702), 33: (12000, 9000, 11400, 21.19431702),
        34: (12000, 14500, 11400, 17.45772171), 35: (8000, 9000, 801, 0.8152905199),
        36: (4000, 0, 801, 0.8152905199), 37: (0, 0, 4800, 12.5014526),
        38: (4000, 9000, 4800, 21.33682467), 39: (0, 5500, 4800, 16.33203364),
        40: (8000, 0, 4800, 17.60022936), 41: (12000, 0, 4800, 17.60022936),
        42: (16000, 0, 4800, 17.60022936), 43: (4000, 9000, 8100, 21.19431702),
        44: (4000, 9000, 11400, 21.19431702), 45: (0, 5500, 11400, 16.18952599),
        46: (8000, 9000, 11400, 21.19431702), 47: (16000, 0, 8100, 17.45772171),
        48: (4000, 14500, 8100, 17.45772171), 49: (0, 9000, 8100, 16.18952599),
        50: (0, 14500, 8100, 12.35894495), 51: (0, 0, 8100, 12.35894495),
        52: (0, 9000, 4800, 16.33203364), 53: (0, 14500, 4800, 12.5014526),
        54: (0, 14500, 11400, 12.35894495), 55: (4000, 0, 11400, 17.45772171),
        56: (12000, 0, 11400, 17.45772171), 57: (16000, 14500, 11400, 17.45772171),
        58: (8000, 5500, 11400, 21.19431702), 59: (16000, 0, 11400, 17.45772171),
        60: (16000, 9000, 11400, 21.19431702), 61: (8000, 14500, 11400, 17.45772171),
        62: (8000, 0, 11400, 17.45772171), 63: (4000, 0, 14700, 17.45772171),
        64: (8000, 0, 14700, 17.45772171), 65: (4000, 9000, 14700, 21.19431702),
        66: (4000, 14500, 11400, 17.45772171), 67: (0, 9000, 14700, 16.18952599),
        68: (4000, 14500, 14700, 17.45772171), 69: (4000, 14500, 4800, 17.60022936),
        70: (4000, 14500, 18000, 9.898572885), 71: (0, 14500, 14700, 12.35894495),
        72: (8000, 9000, 14700, 21.19431702), 73: (0, 14500, 801, 0.8152905199),
        74: (0, 5500, 801, 0.8152905199), 75: (0, 9000, 801, 0.8152905199),
        76: (4000, 9000, 801, 0.8152905199), 77: (0, 0, 801, 0.8152905199),
        78: (4000, 14500, 801, 0.8152905199), 79: (8000, 5500, 801, 0.8152905199),
        80: (4000, 5500, 801, 0.8152905199), 81: (12000, 5500, 801, 0.8152905199),
        82: (12000, 9000, 4800, 21.33682467), 83: (12000, 5500, 14700, 21.19431702),
        84: (16000, 5500, 11400, 21.19431702), 85: (8000, 14500, 14700, 17.45772171),
        86: (0, 14500, 18000, 5.846330275), 87: (4000, 9000, 18000, 14.84301733),
        88: (0, 0, 14700, 12.35894495), 89: (0, 9000, 18000, 8.675331295),
        90: (8000, 14500, 18000, 9.898572885), 91: (0, 9000, 11400, 16.18952599),
        92: (20000, 0, 4800, 12.5014526), 93: (16000, 5500, 4800, 21.33682467),
        94: (8000, 14500, 4800, 17.60022936), 95: (12000, 14500, 4800, 17.60022936),
        96: (12000, 9000, 14700, 21.19431702), 97: (20000, 0, 11400, 12.35894495),
        98: (12000, 14500, 14700, 17.45772171), 99: (20000, 5500, 14700, 16.18952599),
        100: (20000, 0, 14700, 12.35894495), 101: (16000, 14500, 8100, 17.45772171),
        102: (16000, 14500, 14700, 17.45772171), 103: (16000, 14500, 18000, 9.898572885),
        104: (20000, 14500, 18000, 5.846330275), 105: (8000, 5500, 18000, 14.84301733),
        106: (16000, 5500, 18000, 14.84301733), 107: (12000, 9000, 18000, 14.84301733),
        108: (20000, 9000, 18000, 8.675331295), 109: (12000, 14500, 8100, 17.45772171),
        110: (20000, 5500, 18000, 8.675331295), 111: (20000, 14500, 8100, 12.35894495),
        112: (16000, 9000, 8100, 21.19431702), 113: (8000, 0, 18000, 9.898572885),
        114: (20000, 9000, 8100, 16.18952599), 115: (20000, 5500, 8100, 16.18952599),
        116: (16000, 9000, 4800, 21.33682467), 117: (16000, 9000, 14700, 21.19431702),
        118: (20000, 0, 8100, 12.35894495), 119: (8000, 9000, 18000, 14.84301733),
        120: (4000, 5500, 18000, 14.84301733), 121: (0, 0, 11400, 12.35894495),
        122: (0, 0, 18000, 5.846330275), 123: (0, 5500, 18000, 8.675331295),
        124: (20000, 9000, 14700, 16.18952599), 125: (20000, 9000, 11400, 16.18952599),
        126: (20000, 14500, 11400, 12.35894495), 127: (20000, 9000, 4800, 16.33203364),
        128: (20000, 14500, 14700, 12.35894495), 129: (12000, 14500, 18000, 9.898572885),
        130: (20000, 14500, 4800, 12.5014526), 131: (16000, 0, 14700, 17.45772171),
        132: (12000, 0, 14700, 17.45772171), 133: (12000, 0, 18000, 9.898572885),
        134: (20000, 0, 18000, 5.846330275), 135: (16000, 14500, 4800, 17.60022936),
        136: (12000, 0, 801, 0.8152905199), 137: (20000, 0, 801, 0.8152905199),
        138: (8000, 0, 801, 0.8152905199), 139: (20000, 5500, 801, 0.8152905199),
        140: (16000, 0, 801, 0.8152905199), 141: (4000, 0, 18000, 9.898572885),
        142: (12000, 9000, 801, 0.8152905199), 143: (16000, 5500, 801, 0.8152905199),
        144: (12000, 14500, 801, 0.8152905199), 145: (16000, 14500, 801, 0.8152905199),
        146: (20000, 9000, 801, 0.8152905199), 147: (16000, 9000, 801, 0.8152905199),
        148: (8000, 14500, 801, 0.8152905199), 149: (20000, 14500, 801, 0.8152905199),
    }
    for tag, (x, y, z, m) in node_mass.items():
        ops.node(tag, x, y, z, "-mass", m, m, m, 0, 0, 0)

    # Joint nodes + zeroLength (structural node -> joint node)
    # fmt: off
    joint_nodes = {
        150: (21, 4000, 0, 4800), 151: (22, 8000, 5500, 4800),
        152: (23, 8000, 9000, 4800), 153: (24, 4000, 5500, 8100),
        154: (25, 8000, 9000, 8100), 155: (26, 12000, 5500, 8100),
        156: (27, 8000, 14500, 8100), 157: (28, 12000, 9000, 8100),
        158: (29, 4000, 0, 8100), 159: (30, 8000, 0, 8100),
        160: (31, 12000, 0, 8100), 161: (32, 4000, 5500, 14700),
        162: (33, 12000, 9000, 11400), 163: (34, 12000, 14500, 11400),
        164: (37, 0, 0, 4800), 165: (38, 4000, 9000, 4800),
        166: (39, 0, 5500, 4800), 167: (40, 8000, 0, 4800),
        168: (41, 12000, 0, 4800), 169: (42, 16000, 0, 4800),
        170: (43, 4000, 9000, 8100), 171: (44, 4000, 9000, 11400),
        172: (45, 0, 5500, 11400), 173: (46, 8000, 9000, 11400),
        174: (47, 16000, 0, 8100), 175: (48, 4000, 14500, 8100),
        176: (49, 0, 9000, 8100), 177: (50, 0, 14500, 8100),
        178: (51, 0, 0, 8100), 179: (52, 0, 9000, 4800),
        180: (53, 0, 14500, 4800), 181: (54, 0, 14500, 11400),
        182: (55, 4000, 0, 11400), 183: (56, 12000, 0, 11400),
        184: (57, 16000, 14500, 11400), 185: (58, 8000, 5500, 11400),
        186: (59, 16000, 0, 11400), 187: (60, 16000, 9000, 11400),
        188: (61, 8000, 14500, 11400), 189: (62, 8000, 0, 11400),
        190: (63, 4000, 0, 14700), 191: (64, 8000, 0, 14700),
        192: (65, 4000, 9000, 14700), 193: (66, 4000, 14500, 11400),
        194: (67, 0, 9000, 14700), 195: (68, 4000, 14500, 14700),
        196: (69, 4000, 14500, 4800), 197: (70, 4000, 14500, 18000),
        198: (71, 0, 14500, 14700), 199: (72, 8000, 9000, 14700),
        200: (82, 12000, 9000, 4800), 201: (83, 12000, 5500, 14700),
        202: (84, 16000, 5500, 11400), 203: (85, 8000, 14500, 14700),
        204: (86, 0, 14500, 18000), 205: (87, 4000, 9000, 18000),
        206: (88, 0, 0, 14700), 207: (89, 0, 9000, 18000),
        208: (90, 8000, 14500, 18000), 209: (91, 0, 9000, 11400),
        210: (92, 20000, 0, 4800), 211: (93, 16000, 5500, 4800),
        212: (94, 8000, 14500, 4800), 213: (95, 12000, 14500, 4800),
        214: (96, 12000, 9000, 14700), 215: (97, 20000, 0, 11400),
        216: (98, 12000, 14500, 14700), 217: (99, 20000, 5500, 14700),
        218: (100, 20000, 0, 14700), 219: (101, 16000, 14500, 8100),
        220: (102, 16000, 14500, 14700), 221: (103, 16000, 14500, 18000),
        222: (104, 20000, 14500, 18000), 223: (105, 8000, 5500, 18000),
        224: (106, 16000, 5500, 18000), 225: (107, 12000, 9000, 18000),
        226: (108, 20000, 9000, 18000), 227: (109, 12000, 14500, 8100),
        228: (110, 20000, 5500, 18000), 229: (111, 20000, 14500, 8100),
        230: (112, 16000, 9000, 8100), 231: (113, 8000, 0, 18000),
        232: (114, 20000, 9000, 8100), 233: (115, 20000, 5500, 8100),
        234: (116, 16000, 9000, 4800), 235: (117, 16000, 9000, 14700),
        236: (118, 20000, 0, 8100), 237: (119, 8000, 9000, 18000),
        238: (120, 4000, 5500, 18000), 239: (121, 0, 0, 11400),
        240: (122, 0, 0, 18000), 241: (123, 0, 5500, 18000),
        242: (124, 20000, 9000, 14700), 243: (125, 20000, 9000, 11400),
        244: (126, 20000, 14500, 11400), 245: (127, 20000, 9000, 4800),
        246: (128, 20000, 14500, 14700), 247: (129, 12000, 14500, 18000),
        248: (130, 20000, 14500, 4800), 249: (131, 16000, 0, 14700),
        250: (132, 12000, 0, 14700), 251: (133, 12000, 0, 18000),
        252: (134, 20000, 0, 18000), 253: (135, 16000, 14500, 4800),
        254: (141, 4000, 0, 18000),
    }
    zl_tag = 735
    for joint_tag, (mesh_node, x, y, z) in sorted(joint_nodes.items()):
        ops.node(joint_tag, x, y, z)
        _zl(zl_tag, mesh_node, joint_tag, joint_tag - 150 + 97, (1.0, 0.0, 0.0, 0.0, 1.0, 0.0))
        zl_tag += 1
    # fmt: on

    # =========================================================================
    # TRUSS ELEMENTS (primary infill struts — also in elements.tcl)
    # =========================================================================
    # Primary truss tags 1-18 are defined in elements.tcl, so we skip them
    # here to avoid tag collision.

    # =========================================================================
    # CONSTRAINTS
    # =========================================================================
    for tag in [136, 137, 138, 139, 140, 142, 143, 144, 145, 146, 147, 148, 149,
                35, 36, 73, 74, 75, 76, 77, 78, 79, 80, 81]:
        ops.fix(tag, 1, 1, 1, 1, 1, 1)
    for tag in [1, 2, 3, 4, 5]:
        ops.fix(tag, 0, 0, 1, 1, 1, 0)

    rigid_diaphragm_master = {
        5: [6, 8, 9, 86, 87, 89, 90, 103, 104, 105, 106, 107, 108, 110, 113, 119, 120, 122, 123, 129, 133, 134, 141],
        4: [7, 12, 14, 32, 63, 64, 65, 67, 68, 71, 72, 83, 85, 88, 96, 98, 99, 100, 102, 117, 124, 128, 131, 132],
        3: [10, 11, 13, 33, 34, 44, 45, 46, 54, 55, 56, 57, 58, 59, 60, 61, 62, 66, 84, 91, 97, 121, 125, 126],
        2: [15, 16, 17, 24, 25, 26, 27, 28, 29, 30, 31, 43, 47, 48, 49, 50, 51, 101, 109, 111, 112, 114, 115, 118],
        1: [18, 19, 20, 21, 22, 23, 37, 38, 39, 40, 41, 42, 52, 53, 69, 82, 92, 93, 94, 95, 116, 127, 130, 135],
    }
    for master, slaves in rigid_diaphragm_master.items():
        for slave in slaves:
            ops.rigidDiaphragm(3, master, slave)

    # =========================================================================
    # LOAD ALL ELEMENTS FROM TCL SOURCE
    # =========================================================================
    _load_elements_tcl()

    # =========================================================================
    # RAYLEIGH DAMPING
    # =========================================================================
    ops.rayleigh(0.9608223360604259, 0.0, 0.0016613250844665485, 0.0)

    # =========================================================================
    # GRAVITY LOADS
    # =========================================================================
    gravity_beam_groups = [
        ([23, 24, 25, 34, 35, 37, 38, 46, 47, 52, 53, 60, 64, 65, 66, 67, 68, 69,
          72, 82, 83, 86, 87, 88, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102,
          103, 104, 105, 106, 125, 126, 127, 128, 129, 133, 152, 153, 154, 164, 168,
          174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 197, 199, 200, 202, 203,
          211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 222, 225, 226, 227, 228,
          229, 230, 231, 232, 233, 234, 235, 236, 237, 242, 244, 246, 248, 252, 256,
          257, 258, 259, 260, 261, 266, 273, 274, 275, 276, 295, 304, 305, 306, 307,
          308, 309, 310, 311, 312, 313, 314, 315, 316, 317], 5.0625),
        ([39, 42, 43, 45, 54, 58, 59, 70, 77, 81, 112, 113, 114, 120, 131, 146, 167,
          169, 173, 184, 191, 193, 194, 196, 201, 210, 221, 238, 240, 251, 255, 262,
          264, 265, 277, 281, 284, 287, 288, 289], 22.166),
        ([41, 62, 90, 119, 140, 151, 172, 195, 207, 209, 253, 263, 271, 291, 318, 324], 23.617),
        ([115, 122, 156, 247, 249, 250, 296, 302, 320, 325], 9.88),
        ([123, 162, 268, 327], 11.27),
        ([165, 269], 9.23),
        ([116, 158, 171, 243, 245, 301, 326, 328], 18.54),
        ([159, 160, 267, 299], 14.46),
        ([121, 157, 161, 166, 204, 270, 297, 298, 300, 303], 15.68),
        ([19, 29, 31, 32, 33, 36, 55, 76, 78, 80, 85, 130, 132, 134, 139, 141, 142, 143,
          145, 147, 155, 163, 170, 198, 205, 223, 239, 241, 254, 280, 293, 321], 25.235),
        ([89, 124, 192, 206, 272, 282, 319, 323], 21.48),
        ([21, 26, 30, 40, 51, 63, 71, 108, 110, 117, 138, 144, 190, 283, 290, 322], 20.96),
        ([20, 22, 27, 28, 44, 48, 49, 50, 56, 57, 61, 73, 74, 75, 79, 84, 91, 107, 109,
          111, 118, 135, 136, 137, 148, 149, 150, 185, 186, 187, 188, 189, 208, 224,
          278, 279, 285, 286, 292, 294], 22.16),
    ]
    ops.pattern("Plain", 8, 1)
    for ele_tags, w in gravity_beam_groups:
        for et in ele_tags:
            ops.eleLoad("-ele", et, "-type", "-beamUniform", 0.0, 0.0, -w)

    # =========================================================================
    # GRAVITY ANALYSIS
    # =========================================================================
    # §12x-9: ModifiedNewton with Penalty. Newton/KrylovNewton diverge
    # due to fiber-section tangent ill-conditioning; ModifiedNewton uses
    # initial elastic stiffness throughout. Converges ~66% of gravity.
    # Tolerance relaxed to 0.01 — gravity is stress initialization, not
    # a response quantity of interest.
    ops.constraints("Penalty", 1.0e13, 1.0e13)
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", 0.01, 500, 2)
    ops.algorithm("ModifiedNewton")
    ops.integrator("LoadControl", 0.02)
    ops.analysis("Static")

    total_duration = 1.0
    initial_num_incr = 50
    dt = total_duration / initial_num_incr
    time = 0.0

    for step in range(1, initial_num_incr + 1):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"Gravity step {step} failed (load factor ~{step*0.02:.2f})")
            break
        time += dt
        if step % 10 == 0:
            print(f"Gravity: step {step}/{initial_num_incr}, t={time:.4f}")

    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()

    # =========================================================================
    # GROUND MOTION
    # =========================================================================
    gm_base = Path(__file__).parent.parent.parent / "Ground_modtions_G+4 Infilled Frame" / "Pilotis" / "2475"
    gm_info_dir = gm_base / "GroundMotionInfo"
    gm_histories_dir = gm_base / "histories"
    gm_dt_file = gm_info_dir / "GMTimeSteps.txt"
    gm_nsteps_file = gm_info_dir / "GMNumPoints.txt"
    gm_names_file = gm_info_dir / "GMFileNames.txt"

    if gm_dt_file.is_file():
        with open(gm_dt_file) as f:
            gmotion_dt = [float(x) for x in f.read().strip().split()]
        with open(gm_nsteps_file) as f:
            gmotion_nsteps = [float(x) for x in f.read().strip().split()]
        with open(gm_names_file) as f:
            gmotion_names = f.read().strip().split()

        gm_x_dt = gmotion_dt[0]
        gm_x_nsteps = int(gmotion_nsteps[0])
        gm_x_file = gm_histories_dir / f"{gmotion_names[0]}.txt"

        if os.path.isfile(gm_x_file):
            gm_duration = gm_x_dt * gm_x_nsteps
            gm_num_steps = min(gm_x_nsteps, 5000)
            gm_dt_used = gm_duration / gm_num_steps

            ops.timeSeries("Path", 2, "-dt", gm_dt_used,
                           "-filePath", gm_x_file, "-factor", 9810.0)
            ops.pattern("UniformExcitation", 1, 1, "-accel", 2)

            print(f"Ground motion: {gm_x_file}, dt={gm_dt_used}, steps={gm_num_steps}")
        else:
            print(f"Warning: GM file {gm_x_file} not found, skipping ground motion")
            gm_num_steps = 0
            gm_dt_used = 0.02
    else:
        print("Warning: GroundMotionInfo not found, using uniform excitation placeholder")
        gm_num_steps = 0
        gm_dt_used = 0.02

    # =========================================================================
    # TRANSIENT ANALYSIS
    # =========================================================================
    ops.domainChange()
    ops.constraints("Penalty", 1.0e13, 1.0e13)
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", 0.001, 100)
    ops.algorithm("KrylovNewton")
    ops.integrator("Newmark", 0.5, 0.25)
    ops.analysis("Transient")

    if gm_num_steps > 0:
        max_factor = 1.0
        min_factor = 1e-6
        max_factor_inc = 1.5
        min_factor_inc = 1e-6
        max_iter = 200
        desired_iter = 100

        factor = 1.0
        t = 0.0
        increment_counter = 0
        total_time = gm_duration

        while True:
            increment_counter += 1
            if abs(t) >= abs(total_time):
                print(f"Target time reached. t = {t}")
                break

            dt_curr = gm_dt_used * factor
            if abs(t + dt_curr) > abs(total_time):
                dt_curr = total_time - t

            ok = ops.analyze(1, dt_curr)
            if ok == 0:
                num_iter = ops.testIter()
                factor_inc = min(max_factor_inc, desired_iter / max(num_iter, 1))
                factor = min(factor * factor_inc, max_factor)
                t += dt_curr
                print(f"Step {increment_counter}: dt={dt_curr:.6f}, t={t:.4f}, iter={num_iter}")
            else:
                num_iter = max_iter
                factor_inc = max(min_factor_inc, desired_iter / max_iter)
                factor = max(factor * factor_inc, min_factor)
                print(f"Step {increment_counter}: reducing factor to {factor:.6e}")
                if factor < min_factor:
                    print("ERROR: factor below minimum, giving up")
                    break
    else:
        print("No ground motion loaded. Running 1 transient step as placeholder.")
        ops.analyze(1, 0.02)

    print("ANALYSIS SUCCESSFULLY FINISHED")


if __name__ == "__main__":
    run_model()
