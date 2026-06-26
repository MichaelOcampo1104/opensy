# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : misty_effective stress site resp — standalone post-processing
Purpose  : Read existing ODB data and generate stress/deformation diagnostics.
           No re-run needed — works on output/RespStepData-1.odb.
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import sys
from pathlib import Path

import opstool as opst
import numpy as np
import matplotlib.pyplot as plt

# ── 2. CONFIG ────────────────────────────────────────────────────────────────
ODB_TAG = 1
output_dir = Path(__file__).parent / "output"
opst.post.set_odb_path(str(output_dir))   # MUST be set before any ODB read

if not (output_dir / "RespStepData-1.odb").exists():
    print(f"Output not found: {output_dir / 'RespStepData-1.odb'}")
    print("Run model.py first to generate ODB data.")
    sys.exit(1)

# ── 3. LOAD ODB DATA ─────────────────────────────────────────────────────────
print("Loading element responses from ODB...")
plane = opst.post.get_element_responses(odb_tag=ODB_TAG, ele_type="Plane")
print(f"  Time steps: {plane.sizes.get('time', 'N/A')}")
print(f"  Data variables: {list(plane.data_vars)}")

nodal = opst.post.get_nodal_responses(odb_tag=ODB_TAG)
print(f"  Nodal data vars: {list(nodal.data_vars)}")

# ── 4. DIAGNOSTIC: peak displacements ────────────────────────────────────────
# Nodal disp is stored as (time, nodeTags, DOFs) with DOFs=[UX,UY,UZ,RX,RY,RZ].
# (opstool pads every node to 6 DOFs; UZ/RZ are zero for these 2D u-p nodes.)
print("\n=== Peak Nodal Displacements ===")
disp = np.asarray(nodal["disp"].values)        # (time, nodes, 6)
for i, label in enumerate(["UX", "UY"]):
    arr = disp[:, :, i]
    nz = np.count_nonzero(arr)
    print(f"  {label}: max={arr.max():.5f}, min={arr.min():.5f}, "
          f"peak_abs={np.abs(arr).max():.5f}, nonzero={nz}/{arr.size}")

# ── 5. SIGMA22 — Vertical effective stress (should increase with depth) ─────
# NOTE: use "Stresses" (Gauss-point, averaged per element), NOT "StressesAtNodes".
# 9_4_QuadUP has 4 Gauss points; opstool's contour plot averages them per element.
# Pore pressure is read separately from nodal "pressure" (valid).
print("\n=== Plotting: sigma22 (vertical stress) ===")
try:
    fig = opst.vis.plotly.plot_unstruct_responses(
        odb_tag=ODB_TAG,
        slides=True,
        ele_type="Plane",
        resp_type="Stresses",
        resp_dof="sigma22",
        unit_symbol="kPa",
    )
    fig.write_html(str(output_dir / "vis_10_sigma22.html"))
    print("  -> vis_10_sigma22.html")
except Exception as e:
    print(f"  FAILED: {e}")

# ── 6. SIGMA12 — Shear stress (should show dynamic shear waves) ─────────────
print("\n=== Plotting: sigma12 (shear stress) ===")
try:
    fig = opst.vis.plotly.plot_unstruct_responses(
        odb_tag=ODB_TAG,
        slides=True,
        ele_type="Plane",
        resp_type="Stresses",
        resp_dof="sigma12",
        show_defo=True,
        defo_scale=30,
        unit_symbol="kPa",
    )
    fig.write_html(str(output_dir / "vis_11_sigma12.html"))
    print("  -> vis_11_sigma12.html")
except Exception as e:
    print(f"  FAILED: {e}")

# ── 7. Pore pressure (nodal pressure) ───────────────────────────────────────
# For coupled u-p: nodal "pressure" holds pore water pressure (valid).
# sigma33 in Stresses is the out-of-plane total stress component, not pwp.
#
# NOTE: opstool's ODB does NOT capture the 9_4_QuadUP pore-pressure DOF (dof 3)
# into the "pressure" field — it reads all-zeros here (the PWP DOF is mapped to
# the UZ slot, which opstool leaves zero for 2D nodes). This is a known opstool
# gap shared with the sibling pedroArduino_freefield model. The excess-PWP time
# history is available via ops.recorder('Node',...,'-dof',3,'vel') if needed;
# the effective-stress physics is verified through the sigma22 contour instead.
print("\n=== Plotting: pore pressure (nodal pressure) ===")
try:
    fig = opst.vis.plotly.plot_nodal_responses(
        odb_tag=ODB_TAG,
        slides=True,
        resp_type="pressure",
    )
    fig.write_html(str(output_dir / "vis_12_porepressure.html"))
    print("  -> vis_12_porepressure.html  (note: all-zeros — see opstool PWP gap above)")
except Exception as e:
    print(f"  nodal pore pressure plot failed: {e}")

# ── 8. Deformed shape with explicit scaling ─────────────────────────────────
print("\n=== Plotting: deformed shape (UX, explicit scale) ===")
try:
    fig = opst.vis.plotly.plot_nodal_responses(
        odb_tag=ODB_TAG,
        slides=True,
        defo_scale=50.0,
        resp_type="disp",
        resp_dof="UX",
    )
    fig.write_html(str(output_dir / "vis_14_defo_ux_scaled.html"))
    print("  -> vis_14_defo_ux_scaled.html")
except Exception as e:
    print(f"  FAILED: {e}")

# ── 9. Stress-strain at a mid-depth element ─────────────────────────────────
# Element 30 ≈ middle of layer 1 (dense sand). 9_4_QuadUP has 4 Gauss points;
# average over them for a cleaner hysteresis curve.
print("\n=== Stress-strain: element 30 (mid-depth, dense sand) ===")
try:
    sigma12_ele = plane["Stresses"].sel(stressDOFs="sigma12", eleTags=30)
    eps12_ele = plane["Strains"].sel(strainDOFs="eps12", eleTags=30)
    sigma12_mean = sigma12_ele.mean(dim="GaussPoints")
    eps12_mean = eps12_ele.mean(dim="GaussPoints")

    sigma11_ele = plane["Stresses"].sel(stressDOFs="sigma11", eleTags=30)
    eps22_ele = plane["Strains"].sel(strainDOFs="eps22", eleTags=30)
    sigma11_mean = sigma11_ele.mean(dim="GaussPoints")
    eps22_mean = eps22_ele.mean(dim="GaussPoints")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.plot(eps12_mean.values, sigma12_mean.values, "b-", linewidth=0.5)
    ax1.set_title("Element 30: τ_xy vs γ_xy (GP average)")
    ax1.set_xlabel("Shear strain γ_xy")
    ax1.set_ylabel("Shear stress τ_xy (kPa)")
    ax1.grid(True, alpha=0.3)
    ax2.plot(-eps22_mean.values, -sigma11_mean.values, "r-", linewidth=0.5)
    ax2.set_title("Element 30: confinement vs axial (GP average)")
    ax2.set_xlabel("-ε_yy")
    ax2.set_ylabel("Confinement -σ_11 (kPa)")
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(str(output_dir / "vis_15_stress_strain.png"), dpi=150)
    plt.close()
    print("  -> vis_15_stress_strain.png")
except Exception as e:
    print(f"  FAILED: {e}")

# ── 10. Stress profile at final step ────────────────────────────────────────
# Read Gauss-point Stresses directly (collapse GP axis with mean).
print("\n=== Stress profile at final step ===")
try:
    sigma22_gp = plane["Stresses"].sel(stressDOFs="sigma22").isel(time=-1)
    sigma22_final = sigma22_gp.mean(dim="GaussPoints")
    print(f"  sigma22 at final step: min={float(sigma22_final.min()):.1f}, "
          f"max={float(sigma22_final.max()):.1f} kPa")

    sigma12_gp = plane["Stresses"].sel(stressDOFs="sigma12").isel(time=-1)
    sigma12_final = sigma12_gp.mean(dim="GaussPoints")
    print(f"  sigma12 at final step: min={float(sigma12_final.min()):.1f}, "
          f"max={float(sigma12_final.max()):.1f} kPa")
except Exception as e:
    print(f"  FAILED: {e}")

print("\n=== Done ===")
print(f"All outputs in: {output_dir}")
