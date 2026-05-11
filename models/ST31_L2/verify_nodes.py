#!/usr/bin/env python3
"""Temporary verification: node geometry only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))

import openseespy.opensees as ops
import opstool as opst
import numpy as np
# Workaround: older opstool uses np.NAN (removed in newer numpy)
if not hasattr(np, 'NAN'):
    np.NAN = np.nan
from units import *

# ── Parameters ──
h_dwall        = 30000.0 * mm
t_dwall        = 1000.0  * mm
t_slab         = 800.0   * mm
l_clear        = 8000.0  * mm
l_center       = 9000.0  * mm
depth_slab     = 10000.0 * mm
elem_size      = 1000.0  * mm

n_ele_wall     = 30
n_ele_slab     = 9               # 9000mm ctc / 1000mm
n_node_wall    = n_ele_wall + 1

# ── Sections (elastic) ──
b_strip  = 1000.0 * mm
A_dwall  = b_strip * t_dwall
I_dwall  = b_strip * t_dwall**3 / 12.0
A_slab   = b_strip * t_slab
I_slab   = b_strip * t_slab**3 / 12.0

fc = 40.0 * MPa
Ec = 4700.0 * (fc / MPa)**0.5 * MPa

SEC_DWALL = 1
SEC_SLAB  = 2
INT_DWALL = 1
INT_SLAB  = 2
TRANSF_DWALL = 1
TRANSF_SLAB  = 2

NODE_LWALL_TOP  = 1
NODE_LWALL_SLAB = NODE_LWALL_TOP + 10  # = 11 (y=-10000)
NODE_LWALL_BASE = 31
NODE_RWALL_TOP  = 32
NODE_RWALL_SLAB = NODE_RWALL_TOP + 10  # = 42 (y=-10000)
NODE_RWALL_BASE = 62
NODE_SLAB_START = 63
NODE_SLAB_END   = 70

# ── Build model ──
ops.wipe()
ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)

# Nodes
nid = 1
for i in range(n_node_wall):
    ops.node(nid, 0.0, -i * elem_size)
    nid += 1

for i in range(n_node_wall):
    ops.node(nid, l_center, -i * elem_size)
    nid += 1

for i in range(1, n_ele_slab):
    ops.node(nid, i * elem_size, -depth_slab)
    nid += 1

# Sections
ops.section("Elastic", SEC_DWALL, Ec, A_dwall, I_dwall)
ops.section("Elastic", SEC_SLAB,  Ec, A_slab,  I_slab)

# Beam integrations (Gauss-Lobatto, 5 integration points)
ops.beamIntegration("Lobatto", INT_DWALL, SEC_DWALL, 5)
ops.beamIntegration("Lobatto", INT_SLAB,  SEC_SLAB,  5)

# Geometric transformations
ops.geomTransf("PDelta", TRANSF_DWALL)
ops.geomTransf("Linear", TRANSF_SLAB)

# Elements — left wall
for i in range(n_ele_wall):
    n1 = NODE_LWALL_TOP + i
    n2 = n1 + 1
    ops.element("dispBeamColumn", i + 1, n1, n2, TRANSF_DWALL, INT_DWALL)

# Elements — right wall
for i in range(n_ele_wall):
    n1 = NODE_RWALL_TOP + i
    n2 = n1 + 1
    ops.element("dispBeamColumn", n_ele_wall + i + 1, n1, n2, TRANSF_DWALL, INT_DWALL)

# Elements — slab (left wall x=0 → right wall x=9000 at y=-10000)
slab_nodes = [
    NODE_LWALL_SLAB,  # = 11  (left wall at y=-10000)
    *range(NODE_SLAB_START, NODE_SLAB_END + 1),  # 63→70
    NODE_RWALL_SLAB,  # = 42  (right wall at y=-10000)
]
for i in range(n_ele_slab):
    n1 = slab_nodes[i]
    n2 = slab_nodes[i + 1]
    ops.element("dispBeamColumn", 2 * n_ele_wall + i + 1, n1, n2, TRANSF_SLAB, INT_SLAB)

# ── Visualise ──
output_dir = Path(__file__).parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)
fig = opst.vis.plotly.plot_model(show_node_numbering = True)

fig.write_html("opstool_output/model.html")
ops.wipe()
