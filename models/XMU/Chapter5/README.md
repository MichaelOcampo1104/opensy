# XMU Chapter 5 -- 2D RC Shear Wall RW2-2 (Cyclic Pushover)

## Model Summary

| Property | Value |
|----------|-------|
| Model ID | XMU_Chapter5 |
| Type | 2D RC shear wall -- cyclic pushover |
| Reference | Thomsen & Wallace (2004) -- RW2-2 specimen |
| Units | N, mm, MPa |
| Source | Converted from `RW2_2.tcl` + `GeneratePeaks.tcl` |

## Model Description

2D reinforced concrete slender structural wall (1032 x 3660 x 102 mm) with:
- **Boundary columns**: 153 x 102 mm fiber sections (Concrete02 confined core +
  cover, Steel02 rebar, 4 x #3 bars per layer, 19 mm cover)
- **Elastic spider-beam**: Rigid elastic links connecting the control node
  (above wall top) to all top nodes, distributing load
- **Quad wall panel**: 6 x 10 mesh of quad elements with
  `SmearedCompositePlaneStress` nDMaterial -- smeared reinforcement (Steel02,
  rho = 0.0024 both directions) + smeared concrete (4 zones with fc = 42.8-45.7 MPa)
- **Sequential model building**: Frame (ndf=3) -> wall (ndf=2) -> equalDOF ties

### Loading Protocol

- **Gravity**: 378 kN axial load at control node (LoadControl, 10 steps, KrylovNewton)
- **Cyclic pushover**: Displacement-controlled, Full cycle (0 -> +peak -> 0 -> -peak -> 0)
- **Peak amplitudes**: 3.79, 9.99, 16.41, 24.22, 38.91, 54.52, 71.05, 71.28 mm
- **Increment**: 0.02 mm
- **Algorithm fallback**: 5-tier (Newton -> Newton-initial -> Broyden -> NewtonLineSearch -> KrylovNewton)

## Custom OpenSeesPy Build Required

This model uses two research-fork materials **NOT available in standard OpenSeesPy**:

| Material | Type | Description |
|----------|------|-------------|
| `SmearedConcrete` | uniaxialMaterial | Simplified concrete for smeared wall model (fc, epsc0) |
| `SmearedCompositePlaneStress` | nDMaterial | Smeared composite plane-stress (18 params) |

These are from the Thomsen & Wallace (2004) RC wall modeling framework.
**Use the same custom OpenSees build that runs the original `RW2_2.tcl`.**

## File Structure

```
Chapter5/
+-- model.py              # Main model (Python, converted from RW2_2.tcl)
+-- post_process.py       # ODB-based visualization (standalone)
+-- README.md             # This file
+-- RW2_2.tcl             # Original Tcl source (preserved for reference)
+-- GeneratePeaks.tcl     # Original peak generator (logic ported to Python)
+-- DisplayModel2D.tcl    # Original display utility (not used in Python)
+-- DisplayPlane.tcl      # Original view plane utility (not used in Python)
+-- test.txt              # Displacement history data (preserved as-is)
+-- output/               # Generated output (created by model.py)
    +-- vis_01_fiber_section.png    # Column fiber section mesh
    +-- vis_02_model.html           # Undeformed model
    +-- vis_05_deformed_peak.html   # Peak deformation (opstool)
    +-- vis_06_deformed_slider.html # Step-by-step slider (opstool)
    +-- vis_07_force_disp.png       # Force-displacement hysteresis
    +-- EDP.json                    # Engineering demand parameters
    +-- disp.out                    # Control node displacement history
    +-- force.out                   # Base reaction history
    +-- *.out                       # Element fiber/strain recorders
```

## Usage

```bash
# Run model (requires custom OpenSeesPy build)
conda activate opensy
cd models/XMU/Chapter5
python model.py

# Post-process ODB data
python post_process.py
```

## Key Parameters

| Parameter | Value | Unit |
|-----------|-------|------|
| Wall width (L) | 1032 | mm |
| Wall height (H) | 3660 | mm |
| Wall thickness (t) | 102 | mm |
| Column section | 153 x 102 | mm |
| Cover thickness | 19 | mm |
| Rebar per layer | 4 x #3 (As=71.2) | mm^2 |
| Core fc (Concrete02) | -47.6 | MPa |
| Cover fc (Concrete02) | -42.8 | MPa |
| Rebar Fy (Steel02) | 395.2 | MPa |
| Wall concrete fc | 42.8, 45.7, 40.8, 41.3 | MPa |
| Smeared steel Fy | 336 | MPa |
| Reinforcement ratio (rho) | 0.0024 | -- |
| Axial load | 378 | kN |
| Peak drift | ~1.9% | -- |

## Expected Results

- Force-displacement hysteresis with pinching (RC wall behavior)
- Peak base shear and drift ratio at each amplitude
- Fiber strain profiles along boundary columns
- Quad element strain distributions in wall panel

## Notes

- dispBeamColumn requires `beamIntegration` in OpenSeesPy (applied automatically)
- Sequential `ops.model()` calls change default ndf for new nodes (officially supported)
- equalDOF ties only constrain translational DOFs (1,2) between frame and quad nodes
- Fiber section visualization uses opstool's decorated wrappers (not raw ops.*)
- The original Tcl code comments out zoned wall materials (112-114) -- all quads use material 111
- `test.txt` contains displacement history data (possibly experimental), preserved as-is
