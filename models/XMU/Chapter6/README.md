# XMU Chapter 6 -- 2D Soil-Structure Interaction (RC Frame + Soil Deposit)

## Model Summary

| Property | Value |
|----------|-------|
| Model ID | XMU_Chapter6 |
| Type | 2D soil-structure interaction -- dynamic time-history |
| Reference | XMU Finite Element Analysis course, Chapter 6 |
| Units | N, mm, MPa |
| Source | Converted from `model.tcl` |

## Model Description

2D soil-structure interaction model with:
- **Superstructure**: 2-story 3-bay RC frame (ndf=3) with fiber-section columns
  and beams. Concrete01 (cover + confined core) with Hardening rebar.
  16 dispBeamColumn elements (4 Legendre integration points).
- **Soil foundation**: 5-layer soil deposit (ndf=2) modeled with 72
  quadWithSensitivity elements (PlaneStrain, 600 mm thickness).
  MultiYieldSurfaceClay nDMaterial for 4 soil layers (stiffness increasing
  with depth) + structural concrete surrogate under frame columns.
- **Sequential model building**: frame (ndf=3) -> soil (ndf=2) ->
  equalDOF ties (5 lateral periodicity + 9 frame-to-soil).
- **Soil mesh**: 19 x 5 grid (95 nodes), x=-9.2 to 23.2 m, y=-7.2 to 0 m.

### Analysis Protocol

- **Gravity**: 10-step static LoadControl (frame self-weight + soil body forces)
- **Dynamic**: Newmark (gamma=0.55, beta=0.275625), 2400 steps at dt=0.005 s
- **Ground motion**: El Centro NS (factor 3, dt=0.01, 12 s duration)
- **No Rayleigh damping** (matching original Tcl)

## All Materials Available in Standard OpenSeesPy

Unlike Chapter5 (which requires custom SmearedConcrete/SmearedCompositePlaneStress),
this model uses only standard OpenSeesPy materials:
- `Concrete01` (cover + core)
- `Hardening` (rebar, kinematic hardening)
- `MultiYieldSurfaceClay` (soil)

All confirmed working with standard OpenSeesPy from PyPI.

## File Structure

```
Chapter6/
+-- model.py              # Main model (Python, converted from model.tcl)
+-- post_process.py       # ODB-based visualization (standalone)
+-- README.md             # This file
+-- model.tcl             # Original Tcl source (preserved for reference)
+-- stress_strain.m       # Original MATLAB post-processing (reference)
+-- elcentro.txt          # Original ground motion file (preserved)
+-- ground_motions/       # Ground motion directory
    +-- elcentro.txt      # El Centro NS component
+-- output/               # Generated output (created by model.py)
    +-- vis_05_deformed_peak.html   # Peak deformation shape
    +-- vis_06_deformed_slider.html # Step-by-step slider
    +-- EDdisplacementP.json        # Engineering demand parameters
    +-- disp4/5/6.out              # Node displacement history
    +-- node*.out                  # Soil surface node displacements
    +-- Force*.out                 # Section force history
    +-- Deformation*.out           # Section deformation history
    +-- steelstress/strain*.out    # Fiber stress/strain
    +-- concrete*.out              # Concrete fiber stress/strain
    +-- stress*.out                # Soil element stress/strain
```

## Usage

```bash
conda activate opensy
cd models/XMU/Chapter6
python model.py

# Post-process ODB data
python post_process.py
```

## Key Parameters

| Parameter | Value | Unit |
|-----------|-------|------|
| Frame bays | 3 x 7.0 m | mm |
| Story height | 3.6 m x 2 | mm |
| Column section (center) | 600 x 500 | mm |
| Column section (side) | 500 x 500 | mm |
| Beam section | 500 x 400 | mm |
| Cover fc (Concrete01) | -27.6 | MPa |
| Core fc (Concrete01) | -34.5 | MPa |
| Rebar Fy (Hardening) | 248.2 | MPa |
| Rebar E | 200,000 | MPa |
| Soil G (layer 1, top) | 54.5 | MPa |
| Soil G (layer 4, bottom) | 96.8 | MPa |
| Soil mesh size | 19 x 5 | nodes |
| Soil domain | 32.4 x 7.2 | m |
| Side column mass | 15.0 | tonne |
| Center column mass | 30.0 | tonne |
| Ground motion scaling | 3.0 | factor |

## Expected Results

- Peak roof displacement and inter-story drift
- Soil-structure interaction period elongation vs fixed-base
- Soil stress/strain distribution under earthquake loading
- Fiber stress/strain in beam elements
- Section force-deformation hysteresis

## Notes

- Original units: m, ton, sec, kN, kPa -- converted to N, mm, MPa
- dispBeamColumn requires `beamIntegration` in OpenSeesPy
- Sequential `ops.model()` calls change default ndf for new nodes
- Soil body force: -19.6 kN/m^3 -> -1.96e-5 N/mm^3 (/10^6)
- Hardening rebar: b=H_kin/(E+H_kin)=0.008 (kinematic only, H_iso=0)
- Newmark gamma=0.55, beta=0.275625 (equivalent to HHT alpha=-0.05)
- MultiYieldSurfaceClay rho=0 (no soil dynamic mass)
- Material 100 (structural concrete) uses MultiYieldSurfaceClay with
  very stiff parameters under frame columns
