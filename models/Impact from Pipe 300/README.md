# Impact from Pipe 300

**Purpose:** Response of the ground and of a 300 mm pipe to a 75 kPa surcharge on a cut section beside the pipe. All soil and pipe values are placeholders.

**Building System:** NA. A buried pipe beside a shallow open cut, with a 4.9 m wide surcharge pad on the ground.

**Model Description:** A 2D transverse section taken from `Impact to 300mm Pipe.dxf`. The DXF header says mm, but the 0.15 m radius only makes sense in metres, so the geometry is read in metres.

- **Soil box:** x from -60 m to 85 m, ground at y = 10 m, base 100 m below ground (y = -90 m). Gmsh quad mesh with 36,942 soil nodes: 12.5 mm at the pipe, 100 mm in the cut, 250 mm under the pad and 2 m in the far field.
- **Open cut:** 1.74 m deep, 45° sides, 7.9 m wide at ground and 4.4 m at the floor, left of the pipe. The soil is already cut, so the cut is the starting geometry. No excavation is simulated.
- **Pipe:** Ø300 mm outer, centre at x = 14.45 m and 1.41 m below ground. An elastic beam ring with a plane-strain modulus, tied to 152 interface nodes on the pipe surface. Compression-only normal springs and elastic-plastic shear springs connect them to the soil.
- **Surcharge:** 75 kPa on the ground from x = 16.83 m to 21.74 m, applied in 20 load steps after the gravity state.

| Field | Value |
|-------|-------|
| Dimensions | 2D (plane strain, transverse section) |
| Material | Soil: linear elastic, placeholder E = 30 MPa, nu = 0.30, gamma = 18 kN/m³. Pipe: elastic, placeholder E = 3000 MPa, nu = 0.38, wall 12 mm, gamma = 14 kN/m³. Interface: placeholder normal stiffness per 25 mm, shear capacity 30 kPa at 2 mm slip |
| Lateral System | NA |
| Lateral Loading | None. Static vertical surcharge of 75 kPa on the ground, in 20 load steps |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | openseespy 3.8.0.0, opstool 1.0.26 |
| Units | N, mm, MPa |

**References:** No published source. Geometry from `Impact to 300mm Pipe.dxf` in this folder.

**Suggested Citation:** NA

## Outputs (`output/`)

- `vis_07_surcharge_animation.html`: interactive animation of the response as the load ramps from 0 to 75 kPa. The left panel shows the section with ground displacement magnified ×50. The top right shows the pipe shape relative to its mean, magnified ×100 and coloured by the moment change. The bottom panels show settlement and pipe diameter change against load.
- `vis_07_surcharge_animation.gif`: the same animation as a GIF.
- `vis_07_surcharge_final.png`: the final frame.
- `vis_05_defo_surcharge.html`: deformed shape at true scale (opstool).
- `vis_01` to `vis_04`: opstool checkpoints (nodes, model, loads, pre-analysis).
- `results.json`: gravity state, the 20 load steps, and the surcharge increments.
- `surcharge_frames.npz`: the frames behind the animation.
- `ModelData-1.zarr` and `RespStepData-1.odb`: opstool response database, final step only.

## Results at placeholder values

Surcharge increments from the gravity state, at 75 kPa:

| Quantity | Value |
|----------|-------|
| Ground settlement under the pad centre | 29.3 mm |
| Pipe settlement, centre | 17.7 mm |
| Pipe vertical diameter change | +0.26 mm |
| Pipe horizontal diameter change | -0.28 mm |
| Pipe moment change: springline 0° / crown 90° / springline 180° / invert 270° | +12.5 / -9.8 / +9.6 / -7.5 N·mm/mm |
| Gravity crown moment, for scale | 234.8 N·mm/mm (0.235 kN·m/m) |

Moments are per mm of pipe length: 1 N·mm/mm equals 0.001 kN·m/m.

## Convergence checks

**Mesh.** Box -30 m to 55 m, base -40 m; surcharge increments.

| Mesh | Pipe mesh | Interface nodes | Crown 90° moment change | Springline 0° | Pad settlement (mm) | Pipe settlement (mm) |
|------|-----------|-----------------|--------------------------|---------------|---------------------|----------------------|
| C0 | 25 mm | 76 | -8.82 | 12.05 | 24.60 | 12.93 |
| C1 | 12.5 mm | 152 | -9.11 | 11.66 | 24.60 | 13.04 |
| C2 | 12.5 mm, cut 100 mm, pad 250 mm | 152 | -9.10 | 11.65 | 24.60 | 12.93 |
| C3 | C2 with far field at 1 m | 152 | -9.10 | 11.65 | 24.63 | 13.05 |

The 25 mm pipe mesh overstates the moment increments by about 3%. At 12.5 mm and finer they agree within 0.2%, so the model uses the C2 settings.

**Box.** Surcharge increments on the C2 mesh. Changes are relative to R0, the original box.

| Box | Crown 90° moment | Springline 0° moment | Pad settlement | Pipe settlement |
|-----|------------------|----------------------|----------------|-----------------|
| R0: x -30 to 55 m, base -40 m (original) | -9.10 | 11.65 | 24.60 | 12.93 |
| R1: x -60 to 85 m, base -40 m | -9.18 (+0.8%) | 11.74 (+0.8%) | 25.27 (+2.7%) | 13.64 (+5.5%) |
| R2: x -30 to 55 m, base -90 m | -9.23 (+1.4%) | 11.80 (+1.3%) | 30.19 (+22.7%) | 18.40 (+42.4%) |
| **R3: x -60 to 85 m, base -90 m (used)** | **-9.81 (+7.8%)** | **12.48 (+7.1%)** | **29.34 (+19.3%)** | **17.66 (+36.7%)** |
| R4: x -90 to 115 m, base -90 m | -9.98 (+9.6%) | 12.66 (+8.7%) | 29.74 (+20.9%) | 18.08 (+39.9%) |
| R5: x -60 to 85 m, base -130 m | -9.84 (+8.1%) | 12.50 (+7.3%) | 31.91 (+29.7%) | 20.21 (+56.4%) |

The moment increments converge in both directions. R3 to R5, a deeper base, changes them by 0.2%. R3 to R4, a wider box, changes them by 1.6%. The original box underpredicts them by about 7%, which is why the model uses R3.

Settlements do not converge with depth. R3 to R5 raises the pad settlement by about 9% and the pipe settlement by about 14%. The placeholder stiffness is uniform with depth, so the real soil profile must set the compressible depth.

## Checks

- **Equilibrium:** the base reaction balances the soil and pipe self-weight to 1e-10 N. The surcharge adds exactly its 368.6 N per 1 mm slice.
- **Gravity settlement at x = 0:** 2224 mm, against the 1-D closed form gamma·H²/(2M) = 2228 mm, with H = 100 m and M = E(1-nu)/((1+nu)(1-2nu)) = 40.4 MPa.
- **Regression:** the full run matches the R3 convergence case exactly. The surcharge increments also agree with the earlier excavation-version run to about 1e-6 mm.

## Notes and limitations

- **Placeholders:** soil stiffness and strength, groundwater, pipe material and wall, the interface, and the pad's shape and load type. Replace them before using any result.
- **Settlement depends on box depth.** Uniform placeholder stiffness makes the 100 m base give a 2.2 m self-weight settlement. The real soil profile must set the compressible depth.
- **Pipe present from the start (wished in place).** Self-weight loads the springs: 91 of 152 interface springs carry compression at gravity, and the largest shear force reaches the shear capacity. A real installation sequence would give a different baseline.
- **Plane strain** is valid only if the pipe, the cut and the pad are all long and parallel. A square pad would be less severe than this section.
- **Solver:** the gravity state and the surcharge ramp run in manual `ops.analyze()` loops, not SmartAnalyze (AGENT.md §3c, §12z). The response database is collected at the final step only, because per-step collection took minutes per step on this mesh (AGENT.md §3d).
- **Next refinements:** nonlinear soil (`define_materials()`), installing the pipe after gravity, and a real soil profile.

## Reproduce

Run `model.py` with the project venv. A full run takes about 45 minutes on this machine, most of it in the opstool checkpoints and the final database write. Set `OPENSEES_HEADLESS=1` to skip the plots and the animation; the results and frames are still written.
