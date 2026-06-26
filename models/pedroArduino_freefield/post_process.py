# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : pedroArduino_freefield — standalone post-processing
Purpose  : Read existing ODB data and generate stress/deformation diagnostics.
           No re-run needed — works on output/RespStepData-1.nc.
Ref      : opstool excavation example
           https://opstool.readthedocs.io/en/stable/examples/post/excavation/
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))

import opstool as opst
import numpy as np
import matplotlib.pyplot as plt

# ── 2. CONFIG ────────────────────────────────────────────────────────────────
ODB_TAG = 1
output_dir = Path(__file__).parent / "output"
opst.post.set_odb_path(str(output_dir))   # MUST be set before any ODB read

# ── 3. LOAD ODB DATA ─────────────────────────────────────────────────────────
print("Loading element responses from ODB...")
plane = opst.post.get_element_responses(odb_tag=ODB_TAG, ele_type="Plane")
print(f"  Time steps: {plane.sizes.get('time', 'N/A')}")
print(f"  Data variables: {list(plane.data_vars)}")

nodal = opst.post.get_nodal_responses(odb_tag=ODB_TAG)
print(f"  Nodal data vars: {list(nodal.data_vars)}")

# ── 4. DIAGNOSTIC: peak displacements ────────────────────────────────────────
print("\n=== Peak Nodal Displacements ===")
for dof in ["UX", "UY"]:
    if dof in nodal.data_vars:
        abs_max = float(nodal[dof].max())
        abs_min = float(nodal[dof].min())
        peak = max(abs(abs_max), abs(abs_min))
        print(f"  {dof}: max={abs_max:.4f}, min={abs_min:.4f}, peak_abs={peak:.4f}")

# ── 5. SIGMA22 — Vertical effective stress (should increase with depth) ─────
print("\n=== Plotting: sigma22 (vertical stress) ===")
try:
    fig = opst.vis.plotly.plot_unstruct_responses(
        odb_tag=ODB_TAG,
        slides=True,
        ele_type="Plane",
        resp_type="StressesAtNodes",
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
        resp_type="StressesAtNodes",
        resp_dof="sigma12",
        show_defo=True,
        defo_scale=30,
        unit_symbol="kPa",
    )
    fig.write_html(str(output_dir / "vis_11_sigma12.html"))
    print("  -> vis_11_sigma12.html")
except Exception as e:
    print(f"  FAILED: {e}")

# ── 7. Pore pressure (sigma33 or pore_pressure) ─────────────────────────────
# Note: for coupled u-p, pore pressure may be in nodal 'Vel' (dof 3)
# or in plane element 'StressesAtNodes' sigma33 component
print("\n=== Plotting: pore pressure / sigma33 ===")
try:
    # Try sigma33 in plane stresses
    fig = opst.vis.plotly.plot_unstruct_responses(
        odb_tag=ODB_TAG,
        slides=True,
        ele_type="Plane",
        resp_type="StressesAtNodes",
        resp_dof="sigma33",
        unit_symbol="kPa",
    )
    fig.write_html(str(output_dir / "vis_12_sigma33.html"))
    print("  -> vis_12_sigma33.html")
except Exception as e:
    print(f"  sigma33 plot failed: {e}")

# Try nodal pore pressure (UY for pore pressure nodes? or use nodal responses)
try:
    if "Vel" in nodal.data_vars:
        fig = opst.vis.plotly.plot_nodal_responses(
            odb_tag=ODB_TAG,
            slides=True,
            resp_type="Vel",
            resp_dof="UY",
        )
        fig.write_html(str(output_dir / "vis_13_pwp.html"))
        print("  -> vis_13_pwp.html (nodal Vel UY)")
except Exception as e:
    print(f"  nodal pwp plot failed: {e}")

# ── 8. Deformed shape with explicit scaling ─────────────────────────────────
print("\n=== Plotting: deformed shape (UX, explicit scale) ===")
try:
    fig = opst.vis.plotly.plot_nodal_responses(
        odb_tag=ODB_TAG,
        slides=True,
        defo_scale=50.0,          # explicit scale (was True = auto)
        resp_type="disp",
        resp_dof="UX",
    )
    fig.write_html(str(output_dir / "vis_14_defo_ux_scaled.html"))
    print("  -> vis_14_defo_ux_scaled.html")
except Exception as e:
    print(f"  FAILED: {e}")

# ── 9. Stress-strain at a mid-depth element (element 30 ≈ middle of layer 1) ─
print("\n=== Stress-strain: element 30 (mid-depth, dense sand) ===")
try:
    # Extract Gauss-point stresses/strains for a single element
    sigma12_ele = plane["Stresses"].sel(stressDOFs="sigma12", eleTags=30)
    eps12_ele   = plane["Strains"].sel(strainDOFs="eps12", eleTags=30)

    # Average over Gauss points for a cleaner curve
    sigma12_mean = sigma12_ele.mean(dim="GaussPoints")
    eps12_mean   = eps12_ele.mean(dim="GaussPoints")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.plot(eps12_mean.values, sigma12_mean.values, "b-", linewidth=0.5)
    ax1.set_title("Element 30: τ_xy vs γ_xy (GP average)")
    ax1.set_xlabel("Shear strain γ_xy")
    ax1.set_ylabel("Shear stress τ_xy (kPa)")
    ax1.grid(True, alpha=0.3)

    # Try sigma22 vs eps22 for volumetric behavior
    sigma22_ele = plane["Stresses"].sel(stressDOFs="sigma22", eleTags=30)
    eps22_ele   = plane["Strains"].sel(strainDOFs="eps22", eleTags=30)
    sigma22_mean = sigma22_ele.mean(dim="GaussPoints")
    eps22_mean   = eps22_ele.mean(dim="GaussPoints")

    ax2.plot(-eps22_mean.values, -sigma22_mean.values, "r-", linewidth=0.5)
    ax2.set_title("Element 30: -σ_yy vs -ε_yy (GP average)")
    ax2.set_xlabel("Vertical strain -ε_yy")
    ax2.set_ylabel("Vertical effective stress -σ_yy (kPa)")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(str(output_dir / "vis_15_stress_strain.png"), dpi=150)
    plt.close()
    print("  -> vis_15_stress_strain.png")
except Exception as e:
    print(f"  FAILED: {e}")

# ── 10. Stress profile with depth at peak time ──────────────────────────────
print("\n=== Stress profile at final step ===")
try:
    sigma22_nodes = plane["StressesAtNodes"].sel(stressDOFs="sigma22")
    # Last time step
    sigma22_final = sigma22_nodes.isel(time=-1)

    # Get node coordinates from the ODB model data
    # The node Y coordinates give depth (0 = base, 30 = surface)
    # For a rough depth profile, group by Y coordinate bands
    print(f"  sigma22 at final step: min={float(sigma22_final.min()):.1f}, "
          f"max={float(sigma22_final.max()):.1f} kPa")

    sigma12_nodes = plane["StressesAtNodes"].sel(stressDOFs="sigma12")
    sigma12_final = sigma12_nodes.isel(time=-1)
    print(f"  sigma12 at final step: min={float(sigma12_final.min()):.1f}, "
          f"max={float(sigma12_final.max()):.1f} kPa")

except Exception as e:
    print(f"  FAILED: {e}")

print("\n=== Done ===")
print(f"All outputs in: {output_dir}")
