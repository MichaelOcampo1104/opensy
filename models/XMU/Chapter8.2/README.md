# XMU Chapter 8.2 — Single quadUP Soil Element (u-p Coupled, Direct PDMY)

## Model Summary

| Property | Value |
|----------|-------|
| Model ID | XMU_Chapter8_2 |
| Type | Coupled u-p soil element — consolidation + cyclic loading |
| Reference | XMU Finite Element Analysis course, Chapter 8.2 |
| Units | kN, m, sec, kPa |
| Source | Converted from `model.tcl` |

## Model Description

Single-element coupled solid-fluid (u-p) analysis:
- **Element**: 1 quadUP element (1×1 m, unit thickness) with pore pressure DOF
- **Material**: PressureDependMultiYield (PDMY) — 16-param minimum set (direct, no substitution needed)
- **Boundary conditions**: Fixed base (UX,UY), free-draining top (PWP=0), periodic lateral ties
- **Phases**:
  1. Consolidation (VariableTransient): 5 elastic + 3 plastic steps at dt=5000s
  2. Material stage switch (elastic → plastic)
  3. Cyclic dynamic (Transient): 4000 steps at dt=0.01s, ±20 kN horizontal load

### Differences from Chapter 8.1

| Property | Ch8.1 (BoundingSurfaceSand→PDMY) | Ch8.2 (Direct PDMY) |
|----------|------|------|
| Material source | Substituted from BoundingSurfaceSand | Standard PDMY (no substitution) |
| PDMY params | 22 (full set including optional) | 16 (minimum set) |
| Ref. shear modulus (Gr) | 506.6 kPa | 60,000 kPa |
| Ref. bulk modulus (Br) | 200,000 kPa | 240,000 kPa |
| Friction angle (φ) | 47° | 31° |
| Peak shear strain | 0.05 | 0.1 |
| Ref. pressure | 101.325 kPa | 80 kPa |
| Pressure depend. coeff. | 1.01537 | 0.5 |
| Phase transform angle | 31° | 26.5° |
| Soil character | Loose liquefiable sand | Dense/stiff sand |

### Why kN-m-kPa units?

Coupled u-p models have fluid properties (water bulk modulus, permeability, density) that are
physical constants in SI-like units. Converting to N-mm would make densities ~10⁻⁹,
risking numerical conditioning in the u-p formulation and obscuring physical meaning.

## File Structure

```
Chapter8.2/
├── model.py              # Main model (Python, converted from model.tcl)
├── post_process.py       # ODB-based visualization (standalone)
├── README.md             # This file
├── model.tcl             # Original Tcl source (preserved for reference)
└── output/               # Generated output (created by model.py)
    ├── vis_05_deformed_peak.html   # Peak deformation shape
    ├── vis_06_deformed_slider.html # Step-by-step slider
    ├── stress.out                  # Element stress history
    └── strain.out                  # Element strain history
```

## Usage

```bash
conda activate opensy
cd models/XMU/Chapter8.2
python model.py

# Post-process ODB data
python post_process.py
```

## Key Parameters

| Parameter | Value | Unit |
|-----------|-------|------|
| Element size | 1.0 × 1.0 | m |
| Soil mass density (ρ) | 2.0 | Mg/m³ |
| Reference Gr | 60,000 | kPa |
| Reference Br | 240,000 | kPa |
| Friction angle (φ) | 31.0 | ° |
| Peak shear strain | 0.1 | — |
| Ref. pressure | 80.0 | kPa |
| Phase transform angle | 26.5 | ° |
| Water bulk modulus | 2.2×10⁶ | kPa |
| Permeability | 5.09×10⁻⁸ | m/s |
| Peak cyclic load | ±20.0 | kN |
| Dynamic time step | 0.01 | s |
| Rayleigh β | 0.02 | — |

## Expected Results

- Pore pressure dissipation during consolidation phase
- Cyclic shear stress-strain hysteresis
- Less pore pressure buildup than Ch8.1 (denser soil, higher Gr)
- Stiffer cyclic response with smaller deformations

## Notes

- This model uses standard PDMY directly — no material substitution was needed.
- The 16-param minimum set omits optional params (numYieldSurf, e, volLimits, cohesion);
  OpenSees uses built-in defaults for these.
- `wipeAnalysis()` preserves domain time — consolidation runs to ~40000s, then
  cyclic loading uses Series times indexed from this clock.
- Rayleigh damping (β=0.02) is applied only in the dynamic phase, not consolidation.
- Body force (-480 kN/m³) is preserved from source — it's a test value, not a
  typical soil unit weight.
