# Impact from Pipe 300 Pad Stress

**Purpose:** Soil stress increase from a 75 kPa surcharge, carried either on the ground or by a bonded pad foundation of three thicknesses and two stiffnesses, beside a 300 mm pipe at an open cut. It shows how the surcharge disperses with pad thickness and stiffness. All soil, pad and pipe values are placeholders.

**Building System:** NA. A buried pipe beside a shallow open cut, with a 4.9 m wide surcharge on the ground or on a pad.

**Model Description:** The same 2D transverse section, box, pipe, cut, interface and load as [Impact from Pipe 300 Coarse Mesh](../Impact%20from%20Pipe%20300%20Coarse%20Mesh/README.md), with refined zones under and beside the pad. Five cases:

| Case | Pad thickness | Pad E | K |
|------|---------------|-------|---|
| flexible_no_pad | none (load on the ground) | - | 0 |
| pad_t0p3_E30 | 0.3 m | 30 GPa | 0.02 |
| pad_t0p6_E30 | 0.6 m | 30 GPa | 0.16 |
| pad_t1p2_E30 | 1.2 m | 30 GPa | 1.26 |
| pad_t0p6_E3 | 0.6 m | 3 GPa | 0.02 |

K = E_pad t³ / (12(1 − ν²)) / (E_soil B³), with B = 4.91 m, E_soil = 30 MPa and ν_pad = 0.20.

Each case runs gravity first (soil, pad and pipe self-weight), then the 75 kPa surcharge in 20 load steps, on the ground or on the pad top. The pad is bonded to the ground.

Mesh sizes below are gmsh targets. gmsh halves the target when it makes quads, so the element sizes are about half the targets. Soil nodes: 11,014 (no pad) to 12,608 (0.3 m pad).

| Region | Target size | Element size (approx.) |
|--------|-------------|------------------------|
| Pipe | 25 mm | 12.5 mm |
| Open cut | 400 mm | 200 mm |
| Zone under and beside the pad (1.5 m beyond each edge, to 12 m depth) | 500 mm | 250 mm |
| Wider zone (6 m beyond each edge, to 12 m depth) | 1000 mm | 500 mm |
| Pad | thickness / 4 | thickness / 8 (about 8 elements through the thickness) |
| Far field | 4000 mm | 2000 mm |

| Field | Value |
|-------|-------|
| Dimensions | 2D (plane strain, transverse section) |
| Material | Soil: linear elastic, placeholder E = 30 MPa, nu = 0.30, gamma = 18 kN/m³. Pad: linear elastic, placeholder nu = 0.20, gamma = 24 kN/m³, E = 30 GPa or 3 GPa. Pipe: elastic, placeholder E = 3000 MPa, nu = 0.38, wall 12 mm. Interface: placeholder springs, as Impact from Pipe 300 |
| Lateral System | NA |
| Lateral Loading | None. Static vertical surcharge of 75 kPa on the ground or the pad top, in 20 load steps |
| File Format | .py |
| OpenSees Version | openseespy 3.8.0.0, opstool 1.0.26 |
| Units | N, mm, MPa |

**References:** No published source. Geometry from `Impact to 300mm Pipe.dxf` in the folder [Impact from Pipe 300](../Impact%20from%20Pipe%20300/).

**Suggested Citation:** NA

## Results at placeholder values

Stress increase from the surcharge (kPa, compression positive). The depth columns are averages over a 2 m wide band under the pad centre. The pipe column is the mean over the 0.5 m square around the pipe centre, which is 1.4 m deep and about 2.4 m from the nearest pad edge.

| Case | 1 m | 3 m | 5 m | 10 m | Pipe level |
|------|-----|-----|-----|------|------------|
| No pad (flexible) | 72.5 | 54.9 | 40.3 | 22.5 | 1.9 |
| Pad 0.3 m, E 30 GPa | 54.2 | 45.5 | 35.6 | 21.1 | 4.2 |
| Pad 0.6 m, E 30 GPa | 49.4 | 43.7 | 34.7 | 21.1 | 4.1 |
| Pad 1.2 m, E 30 GPa | 48.6 | 43.7 | 35.0 | 21.1 | 4.3 |
| Pad 0.6 m, E 3 GPa | 54.0 | 44.7 | 34.9 | 21.1 | 4.0 |

Closed-form check: a uniform 75 kPa strip 4.91 m wide on an elastic half-space gives 73.1, 56.5, 40.6 and 22.5 kPa at 1, 3, 5 and 10 m.

Contact stress under the pad, in 0.5 m bins across the pad (kPa). The bins carry the full 368.6 N.

| Case | Left edge bin | Middle two bins (mean) | Right edge bin |
|------|---------------|------------|----------------|
| No pad | 75.0 | 75.0 | 75.0 |
| Pad 0.3 m, E 30 GPa | 127.5 | 59.0 | 136.3 |
| Pad 0.6 m, E 30 GPa | 151.0 | 50.9 | 162.7 |
| Pad 1.2 m, E 30 GPa | 153.3 | 49.3 | 153.3 |
| Pad 0.6 m, E 3 GPa | 132.6 | 59.3 | 142.4 |

With a pad, the load moves toward the pad edges. Single nodes at the pad corners reach 466–761 kPa. Those peaks depend on mesh size, so they are not used as results.

Settlement at the pad centre: 29.4 mm with no pad; 26.6–27.2 mm with a pad.

## Checks

- **Equilibrium:** the contact forces from the soil sum to the applied 368.59 N in every case.
- **Flexible case:** the contact is 75.0 kPa at every ground node.
- **Linear scaling:** each animation frame equals the final stress times the load fraction, to within 1e-6 kPa in every case.
- **Flexible depth profile:** within 3% of the closed-form strip at 1, 3, 5 and 10 m.
- **Pad element size:** halving the pad element size (thickness / 4 to thickness / 8) for the 0.3 m case changes the contact bins by under 1% and the depth values by 2% or less.
- **Soil zone:** halving the zone size (500 to 250 mm target) for the 0.3 m case changes the contact bins by under 0.7 kPa and the depth values by under 0.5%.

## Outputs (`output/`)

- `pad_study_summary.json`: results for each case.
- `pad_stress_maps_kPa.png`: stress maps, colour scale capped at 100 kPa.
- `pad_stress_depth_profile_kPa.png`: stress with depth under the pad centre, with the closed-form reference.
- `pad_contact_pressure_kPa.png`: contact stress in 0.5 m bins.
- `animations/stress_<case>.gif`: one per case. The applied surcharge is shown above the stress map, over 21 load steps.
- `animations/stress_all_cases.gif`: all five cases side by side at the same load step.
- `cases/<case>_stress.npz` and `cases/<case>_results.json`: element stresses and per-case results.
- `cases/<case>_frames.npz`: stress at each load step, used by the animations.
- `vis_01` to `vis_05` (HTML), `ModelData-1.zarr` and `RespStepData-1.odb`: opstool checkpoints and response data for the no-pad case. `vis_05_defo_surcharge.html` is at true scale.

## Notes and limitations

- **Placeholders:** all soil, pad, pipe and interface values. Replace them before using any result.
- **Bonded pad:** the pad is bonded to the soil, and its E is 1000 times the soil's. The load moves to the pad edges even for the thinnest pad, where the edge bins are about twice the centre value. A frictionless interface or a plate model could give a different pattern. This has not been checked.
- **Corner peaks:** single nodes at the pad corners depend on mesh size. Use the bin averages, not the peak nodes.
- **Animations:** the model is linear elastic and the ramp is linear, so each frame is the final stress scaled by the load fraction. The animations show the stress building up, not a change in shape. A non-linear soil model would change this.
- **Plane strain:** valid only if the pipe, the cut and the pad are all long and parallel.
- **Box:** the base is fixed 100 m below ground. Stresses at depth depend on that and on the uniform placeholder stiffness.
- **Pipe present from the start:** as in Impact from Pipe 300. Its self-weight is in the gravity state.
- **Solver:** manual gravity and surcharge loops (AGENT.md §3c, §12z).

## Reproduce

Run `model.py` with the project venv. The five cases take about 15 minutes on this machine. `python model.py --animations-only` rebuilds the GIFs from the saved frames without re-solving.
