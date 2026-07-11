# ─────────────────────────────────────────────────────────────────────────────
# VERBATIM SOURCE — opstool Moment-Curvature section analysis example
# Retrieved 2026-07-11 from:
#   https://opstool.readthedocs.io/en/stable/src/analysis/mc_analysis.html
# Units: kN-m (NOT N-mm). Preserved here for provenance / reference only.
# The standardized N-mm-MPa version lives in ../model.py.
# ─────────────────────────────────────────────────────────────────────────────

import opstool as opst
import openseespy.opensees as ops
import matplotlib.pyplot as plt


# ── Create Section ────────────────────────────────────────────────────────────
ops.wipe()
ops.model("basic", "-ndm", 3, "-ndf", 6)

matTagC, matTagCCore, matTagS = 1, 2, 3

Ec, fc, ec, ecu = 3.55e7, -32.4e3, -2000.0e-6, 2.1 * (-2000.0e-6)
ft, et = 2.64e3, 107e-6
fccore, eccore, ecucore = -40.6e3, -4079e-6, -0.0144
Fys, Es, bs = 300.0e3, 2.0e8, 0.01

ops.uniaxialMaterial("Concrete04", matTagC, fc, ec, ecu, Ec, ft, et)
ops.uniaxialMaterial("Concrete04", matTagCCore, fccore, eccore, ecucore, Ec, ft, et)
ops.uniaxialMaterial("Steel01", matTagS, Fys, Es, bs)

outlines = [[0, 0], [2, 0], [2, 2], [0, 2]]
coverlines = opst.pre.section.offset(outlines, d=0.05)
cover = opst.pre.section.create_polygon_patch(outlines, holes=[coverlines])
holelines = [[0.5, 0.5], [1.5, 0.5], [1.5, 1.5], [0.5, 1.5]]
core = opst.pre.section.create_polygon_patch(coverlines, holes=[holelines])

SEC = opst.pre.section.FiberSecMesh()
SEC.add_patch_group(dict(cover=cover, core=core))
SEC.set_mesh_size(dict(cover=0.1, core=0.1))
SEC.set_mesh_color(dict(cover="gray", core="green"))
SEC.set_ops_mat_tag(dict(cover=matTagC, core=matTagCCore))
SEC.mesh()
rebar_lines = opst.pre.section.offset(outlines, d=(0.05 + 0.032 / 2))
SEC.add_rebar_line(points=rebar_lines, dia=0.02, gap=0.1, color="red",
                   ops_mat_tag=matTagS)
SEC.get_frame_props(display_results=False)
SEC.centring()
SEC.to_opspy_cmds(secTag=1, GJ=100000)

SEC.view()

# ── Moment Curvature ──────────────────────────────────────────────────────────
MC = opst.anlys.MomentCurvature(sec_tag=1, axial_force=-20000)
MC.analyze(axis="y", incr_phi=1e-5, smart_analyze=True)
# Note: max_phi defaults to 0.5 [1/m] — NOT shown in the docs snippet above;
# it is the MomentCurvature.analyze default.
fig, ax = MC.plot_M_phi()

# ── Limit State ───────────────────────────────────────────────────────────────
phiy, My = MC.get_limit_state(matTag=matTagS, threshold=2e-3)
phiu, Mu = MC.get_limit_state(matTag=matTagCCore, threshold=-0.0144, peak_drop=False)
print(f"phiy = {phiy:.3e}, My = {My:.2f}")
print(f"phiu = {phiu:.3e}, Mu = {Mu:.2f}")

# ── Bilinearization ───────────────────────────────────────────────────────────
phi_eq, M_eq = MC.bilinearize(phiy, My, phiu)
print(f"phi_eq = {phi_eq:.3e}, M_eq = {M_eq:.2f}")

MC.plot_fiber_responses()
