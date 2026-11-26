# Impact from Pipe 300 Coarse Mesh

**Purpose:** Coarse-mesh variant of the Impact from Pipe 300 model, for quick runs and for checking changes before the full model is run. Same geometry, box, interface and placeholder data; only the mesh is coarser. All soil and pipe values are placeholders.

**Building System:** NA. A buried pipe beside a shallow open cut, with a 4.9 m wide surcharge pad on the ground.

**Model Description:** The same 2D transverse section, box, interface and load as [Impact from Pipe 300](../Impact%20from%20Pipe%20300/README.md). The full description, the convergence study and the limitations are in that README. The open cut is the starting geometry, and the surcharge runs in 20 load steps.

| Mesh | Fine (Impact from Pipe 300) | Coarse (this model) |
|------|-----------------------------|---------------------|
| Pipe | 12.5 mm (152 interface nodes) | 25 mm (76 interface nodes) |
| Open cut | 100 mm | 400 mm |
| Under the pad | 250 mm | 1000 mm |
| Far field | 2000 mm | 4000 mm |
| Soil nodes | 36,942 | 9,122 |
| Quads | 36,468 | 8,908 |

| Field | Value |
|-------|-------|
| Dimensions | 2D (plane strain, transverse section) |
| Material | Soil: linear elastic, placeholder E = 30 MPa, nu = 0.30, gamma = 18 kN/m³. Pipe: elastic, placeholder E = 3000 MPa, nu = 0.38, wall 12 mm. Interface: placeholder springs |
| Lateral System | NA |
| Lateral Loading | None. Static vertical surcharge of 75 kPa on the ground, in 20 load steps |
| File Format | .py |
| OpenSees Version | openseespy 3.8.0.0, opstool 1.0.26 |
| Units | N, mm, MPa |

**References:** No published source. Geometry from `Impact to 300mm Pipe.dxf` in the folder [Impact from Pipe 300](../Impact%20from%20Pipe%20300/).

**Suggested Citation:** NA

## Accuracy against the fine model

Surcharge increments at 75 kPa, same box. The differences are coarse relative to fine.

| Quantity | Fine | Coarse | Difference |
|----------|------|--------|------------|
| Ground settlement under the pad centre | 29.34 mm | 29.27 mm | -0.3% |
| Pipe settlement, centre | 17.66 mm | 17.84 mm | +1.0% |
| Pipe moment change, springline 0° | 12.48 N·mm/mm | 13.00 N·mm/mm | +4.2% |
| Pipe moment change, crown 90° | -9.81 N·mm/mm | -9.54 N·mm/mm | +2.8% |
| Pipe moment change, springline 180° | 9.59 N·mm/mm | 9.84 N·mm/mm | +2.6% |
| Pipe moment change, invert 270° | -7.54 N·mm/mm | -7.62 N·mm/mm | -1.0% |
| Pipe vertical diameter change | +0.259 mm | +0.258 mm | -0.6% |
| Pipe horizontal diameter change | -0.278 mm | -0.278 mm | 0.0% |

The moment increments carry the largest errors, up to 4%. Use the fine model for any result you report. Use this model for quick checks and parametric runs, and compare it with the fine model before relying on a change.

## Results at placeholder values

Gravity crown moment: 235.0 N·mm/mm. Interface springs carrying compression at gravity: 45 of 76. The fine model has 91 of 152, the same share.

Surcharge increments at 75 kPa: ground settlement under the pad centre 29.3 mm, pipe settlement 17.8 mm, pipe vertical diameter change +0.26 mm, horizontal -0.28 mm. Moment changes at 0°, 90°, 180° and 270°: +13.0, -9.5, +9.8 and -7.6 N·mm/mm.

## Outputs (`output/`)

The same set as the fine model: `vis_07_surcharge_animation.html`, `vis_07_surcharge_animation.gif`, `vis_07_surcharge_final.png`, `vis_05_defo_surcharge.html` (true scale), `vis_01` to `vis_04` (opstool checkpoints), `results.json`, `surcharge_frames.npz`, and the opstool response database (final step only).

## Checks

- **Equilibrium:** the base reaction balances the soil and pipe self-weight to 1e-10 N, and the surcharge adds exactly its 368.6 N per 1 mm slice.
- **Regression:** the run matches the mesh-study candidate exactly.
- **Gravity settlement at x = 0:** 2224 mm, the same as the fine model and the 1-D closed form of 2228 mm.

## Notes and limitations

- **Placeholders:** the same as the fine model. Replace the soil, groundwater, pipe, interface and load data before using any result.
- **Settlement depends on box depth,** because the placeholder stiffness is uniform. The real soil profile must set the depth, as in the fine model.
- **Pipe present from the start (wished in place).** Self-weight loads the springs. A real installation sequence would give a different baseline.
- **Plane strain** is valid only if the pipe, the cut and the pad are all long and parallel.
- **Solver:** the gravity state and the surcharge ramp run in manual `ops.analyze()` loops, not SmartAnalyze (AGENT.md §3c, §12z). The response database is collected at the final step only (AGENT.md §3d).

## Reproduce

Run `model.py` with the project venv. A full run takes about 3 minutes on this machine, against about 45 minutes for the fine model. Set `OPENSEES_HEADLESS=1` to skip the plots and the animation; the results and frames are still written.
