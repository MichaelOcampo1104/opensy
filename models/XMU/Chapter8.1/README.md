# XMU Chapter 8.1 — Single quadUP Soil Element (u-p Coupled)

## Model Summary

| Property | Value |
|----------|-------|
| Model ID | XMU_Chapter8_1 |
| Type | Coupled u-p soil element — consolidation + cyclic loading |
| Reference | XMU Finite Element Analysis course, Chapter 8.1 |
| Units | kN, m, sec, kPa |
| Source | Converted from `model.tcl` |

## Model Description

Single-element coupled solid-fluid (u-p) analysis:
- **Element**: 1 quadUP element (1×1 m, unit thickness) with pore pressure DOF
- **Material**: PressureDependMultiYield (PDMY) — substituted from source BoundingSurfaceSand (XMU custom)
- **Boundary conditions**: Fixed base (UX,UY), free-draining top (PWP=0), periodic lateral ties
- **Phases**:
  1. Consolidation (VariableTransient): 8 steps at dt=5000s, pore pressure dissipation
  2. Material stage switch (elastic → plastic)
  3. Cyclic dynamic (Transient): 4000 steps at dt=0.01s, ±20 kN horizontal load

### Why kN-m-kPa units?

This is the **first model in the catalogue to retain source units**. Coupled u-p
models have fluid properties (water bulk modulus, permeability, density) that are
physical constants in SI-like units. Converting to N-mm would make densities ~10⁻⁹,
risking numerical conditioning in the u-p formulation and obscuring physical meaning.

## Material Substitution

| Source (BoundingSurfaceSand) | Target (PDMY) |
|-----|-----|
| XMU custom nDMaterial | Standard OpenSeesPy |
| Angles in radians (0.818, 0.5423) | Degrees (47°, 31°) |
| G₀=0.5066 MPa, B₀=200 MPa | G₀=506.6 kPa, B₀=200000 kPa |
| `updateMaterialStage -stage 1000` | `updateMaterialStage -stage 1` |

The PDMY parameter mapping is approximate — it's a different constitutive model
than BoundingSurfaceSand. Key soil behavior (cyclic mobility, liquefaction) is
captured by both.

## File Structure

```
Chapter8.1/
+-- model.py              # Main model (Python, converted from model.tcl)
+-- post_process.py       # ODB-based visualization (standalone)
+-- README.md             # This file
+-- model.tcl             # Original Tcl source (preserved for reference)
+-- output/               # Generated output (created by model.py)
    +-- vis_05_deformed_peak.html   # Peak deformation shape
    +-- vis_06_deformed_slider.html # Step-by-step slider
    +-- stress.out                  # Element stress history
    +-- strain.out                  # Element strain history
```

## Usage

```bash
conda activate opensy
cd models/XMU/Chapter8.1
python model.py

# Post-process ODB data
python post_process.py
```

## Key Parameters

| Parameter | Value | Unit |
|-----------|-------|------|
| Element size | 1.0 × 1.0 | m |
| Soil mass density (ρ) | 1.90 | Mg/m³ |
| Reference G₀ | 506.6 | kPa |
| Reference B₀ | 200,000 | kPa |
| Friction angle (φ) | 47.0 | ° |
| Peak shear strain | 0.05 | — |
| Ref. pressure | 101.325 | kPa |
| Phase transform angle | 31.0 | ° |
| Water bulk modulus | 2.2×10⁶ | kPa |
| Permeability | 5.09×10⁻⁸ | m/s |
| Peak cyclic load | ±20.0 | kN |
| Dynamic time step | 0.01 | s |
| Rayleigh β | 0.02 | — |

## Expected Results

- Pore pressure dissipation during consolidation phase
- Cyclic shear stress-strain hysteresis
- Progressive pore pressure buildup under cyclic loading
- Soil softening and eventual liquefaction behavior

## Notes

- `wipeAnalysis()` preserves domain time — consolidation runs to ~40000s, then
  cyclic loading uses Series times indexed from this clock.
- Rayleigh damping (β=0.02) is applied only in the dynamic phase, not consolidation.
- Body force (-480 kN/m³) is preserved from source — it's a test value, not a
  typical soil unit weight.
- PDMY `numberOfYieldSurf=20` and volumetric limits use OpenSees defaults.
