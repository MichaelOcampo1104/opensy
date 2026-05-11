#!/usr/bin/env python3
"""Manual 2D plot of model geometry using matplotlib."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))

import openseespy.opensees as ops
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from standards.units import *

# ── Parameters ──
h_dwall        = 30000.0 * mm
t_dwall        = 1000.0  * mm
t_slab         = 800.0   * mm
l_center       = 9000.0  * mm
depth_slab     = 10000.0 * mm
elem_size      = 1000.0  * mm
n_ele_wall     = 30
n_ele_slab     = 9
n_node_wall    = n_ele_wall + 1

# Section & integration
b_strip  = 1000.0 * mm
A_dwall  = b_strip * t_dwall
I_dwall  = b_strip * t_dwall**3 / 12.0
A_slab   = b_strip * t_slab
I_slab   = b_strip * t_slab**3 / 12.0
fc = 40.0 * MPa
Ec = 4700.0 * (fc / MPa)**0.5 * MPa
SEC_DWALL = 1; SEC_SLAB = 2
INT_DWALL = 1; INT_SLAB = 2
TRANSF_DWALL = 1; TRANSF_SLAB = 2

NODE_LWALL_TOP  = 1
NODE_LWALL_SLAB = NODE_LWALL_TOP + 10
NODE_LWALL_BASE = 31
NODE_RWALL_TOP  = 32
NODE_RWALL_SLAB = NODE_RWALL_TOP + 10
NODE_RWALL_BASE = 62
NODE_SLAB_START = 63
NODE_SLAB_END   = 70

output_dir = Path(__file__).parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)

# ── Build model ──
ops.wipe()
ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)

nid = 1
for i in range(n_node_wall):
    ops.node(nid, 0.0, -i * elem_size); nid += 1
for i in range(n_node_wall):
    ops.node(nid, l_center, -i * elem_size); nid += 1
for i in range(1, n_ele_slab):
    ops.node(nid, i * elem_size, -depth_slab); nid += 1

ops.section("Elastic", SEC_DWALL, Ec, A_dwall, I_dwall)
ops.section("Elastic", SEC_SLAB,  Ec, A_slab,  I_slab)
ops.beamIntegration("Lobatto", INT_DWALL, SEC_DWALL, 5)
ops.beamIntegration("Lobatto", INT_SLAB,  SEC_SLAB,  5)
ops.geomTransf("PDelta", TRANSF_DWALL)
ops.geomTransf("Linear", TRANSF_SLAB)

for i in range(n_ele_wall):
    ops.element("dispBeamColumn", i+1, NODE_LWALL_TOP+i, NODE_LWALL_TOP+i+1, TRANSF_DWALL, INT_DWALL)
for i in range(n_ele_wall):
    ops.element("dispBeamColumn", n_ele_wall+i+1, NODE_RWALL_TOP+i, NODE_RWALL_TOP+i+1, TRANSF_DWALL, INT_DWALL)

slab_nodes = [NODE_LWALL_SLAB] + list(range(NODE_SLAB_START, NODE_SLAB_END+1)) + [NODE_RWALL_SLAB]
for i in range(n_ele_slab):
    ops.element("dispBeamColumn", 2*n_ele_wall+i+1, slab_nodes[i], slab_nodes[i+1], TRANSF_SLAB, INT_SLAB)

# ── Extract coordinates ──
node_xy = {}
for tag in ops.getNodeTags():
    node_xy[tag] = ops.nodeCoord(tag)

elems = []
for tag in ops.getEleTags():
    nodes = ops.eleNodes(tag)
    elems.append((tag, nodes))

ops.wipe()

# ── Plot ──
fig, ax = plt.subplots(figsize=(12, 16))

# Draw elements as thick lines
for tag, (n1, n2) in elems:
    x = [node_xy[n1][0], node_xy[n2][0]]
    y = [node_xy[n1][1], node_xy[n2][1]]
    # Colour: walls = blue, slab = red
    color = "red" if tag > 2 * n_ele_wall else "royalblue"
    lw = 4 if tag > 2 * n_ele_wall else 3
    ax.plot(x, y, color=color, lw=lw, zorder=2)

# Draw nodes
xs = [xy[0] for xy in node_xy.values()]
ys = [xy[1] for xy in node_xy.values()]
ax.scatter(xs, ys, color="black", s=20, zorder=3)

# Annotate key nodes
key_annotations = {
    1: "L-Wall Top",
    11: "L-Wall @ Slab",
    31: "L-Wall Base (fixed)",
    32: "R-Wall Top",
    42: "R-Wall @ Slab",
    62: "R-Wall Base (fixed)",
    67: "Slab Midspan",
}

for tag, label in key_annotations.items():
    x, y = node_xy[tag]
    ax.annotate(label, (x, y), xytext=(10, -10),
                textcoords="offset points", fontsize=8,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8),
                zorder=4)

# Formatting
ax.set_xlabel("X (mm)")
ax.set_ylabel("Y (mm)")
ax.set_title("ST31_L2 — H-Frame Underground Structure (1m strip)")
ax.grid(True, alpha=0.3)
ax.set_aspect("equal")

# Legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color="royalblue", lw=3, label="D-Wall (dispBeamColumn)"),
    Line2D([0], [0], color="red", lw=4, label="Base Slab (dispBeamColumn)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="black", markersize=6, label="Nodes"),
]
ax.legend(handles=legend_elements, loc="lower right")

fig.tight_layout()
fig.savefig(str(output_dir / "vis_geometry.png"), dpi=150)
print(f"✓ Geometry plot saved to {output_dir / 'vis_geometry.png'}")

# Also plot as simple line schematic
fig2, ax2 = plt.subplots(figsize=(6, 10))
for tag, (n1, n2) in elems:
    x = [node_xy[n1][0], node_xy[n2][0]]
    y = [node_xy[n1][1], node_xy[n2][1]]
    color = "red" if tag > 2 * n_ele_wall else "royalblue"
    ax2.plot(x, y, color=color, lw=3, zorder=2)

# Annotate key dimensions
ax2.annotate("", xy=(0, 0), xytext=(0, -30000),
             arrowprops=dict(arrowstyle="<->", color="gray"), zorder=1)
ax2.text(-1500, -15000, "30,000 mm\n(30 m)", ha="center", fontsize=9, color="gray")

ax2.annotate("", xy=(0, -10000), xytext=(9000, -10000),
             arrowprops=dict(arrowstyle="<->", color="gray"), zorder=1)
ax2.text(4500, -9000, "9,000 mm\n(9 m ctc)", ha="center", fontsize=9, color="gray")

ax2.annotate("", xy=(0, -10000), xytext=(0, -30000),
             arrowprops=dict(arrowstyle="<->", color="lightblue"), zorder=1)
ax2.text(500, -20000, "20,000 mm\n(wall embedment)", ha="left", fontsize=8, color="lightblue")

ax2.set_xlabel("X (mm)")
ax2.set_ylabel("Y (mm)")
ax2.set_title("ST31_L2 — Schematic\nH-Frame with D-Walls")
ax2.grid(True, alpha=0.3)
ax2.set_aspect("equal")
ax2.invert_yaxis()
xmin, xmax = ax2.get_xlim()
ax2.set_xlim(xmin - 2000, xmax + 2000)
fig2.tight_layout()
fig2.savefig(str(output_dir / "vis_schematic.png"), dpi=150)
print(f"✓ Schematic saved to {output_dir / 'vis_schematic.png'}")
