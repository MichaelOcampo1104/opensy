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
- `animations/opstool/stress_slider_<case>.html`: one opstool slider per case, with Play, Pause and a surcharge slider from 0 to 75 kPa. The colours are the same element stresses as the maps. About 18 to 19 MB each. A static preview at 75 kPa is saved beside each one as `stress_slider_<case>_final.png`.
- `animations/odb/<case>/`: opstool response databases for the sliders (full run, gravity state first, plane stresses at every step).
- `interface/interface_summary.json` and `interface/pad_interface_comparison.png`: the bonded, frictionless and friction results side by side.
- `interface/frictionless/cases/` and `interface/friction/cases/`: per-case results for the interface models.
- `coarse_zone/`: the five cases with coarser zones, with `coarse_vs_fine.json` and `coarse_vs_fine_contact.png` comparing them with the current study.
- `cases/<case>_stress.npz` and `cases/<case>_results.json`: element stresses and per-case results.
- `cases/<case>_frames.npz`: stress at each load step, used by the animations.
- `vis_01` to `vis_05` (HTML), `ModelData-1.zarr` and `RespStepData-1.odb`: opstool checkpoints and response data for the no-pad case. `vis_05_defo_surcharge.html` is at true scale.

## Pad-soil interface: bonded, frictionless and friction

The main results tie the pad to the soil: the pad's base nodes are shared with the soil, so there is no slip. Two interface models test that assumption. Each pad base node is split from the soil node below it and joined to it by a zero-length spring.

- **Normal spring:** compression only, stiffness E_soil / 1 mm per area (PLACEHOLDER). It adds under 0.01 mm of settlement under the surcharge.
- **Frictionless model:** no shear spring.
- **Friction model:** an elastic-plastic shear spring that yields at mu N, with mu = 0.4 (PLACEHOLDER). N is the pad base normal force from the previous pass; the first pass uses the pad weight plus the surcharge per node. Three passes were run, and the friction limit changed by at most 2.5% between the last two.
- One pad base node is pinned horizontally. No horizontal load is applied, so this only removes the rigid-body mode.

| Case | Model | 1 m | 3 m | 5 m | 10 m | Edge bins | Middle bin | Pad settlement (mm) |
|------|-------|-----|-----|-----|------|-----------|------------|---------------------|
| Pad 0.3 m, E 30 GPa | bonded | 54.2 | 45.5 | 35.6 | 21.1 | 127.5 / 136.3 | 59.0 | 27.23 |
| | frictionless | 58.8 | 50.6 | 38.6 | 22.1 | 131.3 / 141.1 | 58.6 | 27.92 |
| | friction, mu 0.4 | 54.3 | 45.9 | 35.9 | 21.2 | 125.9 / 134.4 | 59.4 | 27.31 |
| Pad 0.6 m, E 30 GPa | bonded | 49.4 | 43.7 | 34.7 | 21.1 | 151.0 / 162.7 | 51.0 | 26.69 |
| | frictionless | 52.3 | 48.0 | 37.3 | 22.1 | 157.3 / 171.1 | 49.5 | 27.23 |
| | friction, mu 0.4 | 49.6 | 44.1 | 34.9 | 21.2 | 148.5 / 160.1 | 51.4 | 26.77 |
| Pad 1.2 m, E 30 GPa | bonded | 48.6 | 43.7 | 35.0 | 21.1 | 153.3 / 153.3 | 49.3 | 26.59 |
| | frictionless | 51.3 | 47.8 | 37.6 | 22.0 | 160.8 / 160.8 | 47.6 | 27.08 |
| | friction, mu 0.4 | 48.8 | 44.1 | 35.3 | 21.2 | 150.9 / 151.2 | 49.7 | 26.67 |
| Pad 0.6 m, E 3 GPa | bonded | 54.0 | 44.7 | 34.9 | 21.1 | 132.6 / 142.4 | 59.3 | 27.19 |
| | frictionless | 60.0 | 50.4 | 38.2 | 22.2 | 131.5 / 142.1 | 60.5 | 28.05 |
| | friction, mu 0.4 | 54.2 | 45.3 | 35.3 | 21.3 | 130.3 / 139.7 | 59.7 | 27.30 |

Stresses are kPa. The middle bin is the sixth of ten 0.5 m bins.

- **Friction model:** within 0.6 kPa of the bonded result at every depth and every pad, so the bonded base is a close approximation at mu = 0.4.
- **Frictionless model:** the stress at 1 m is 2.7 to 6.0 kPa higher (6 to 11%). The pad settles 0.5 to 0.9 mm more, and the pipe-level stress for the 0.3 m pad falls from 4.2 to 2.7 kPa.
- **Edge concentration:** present in all three models, so it is not caused by shear transfer through a bonded base.
- **Checks:** contact totals are 368.59 N in every model. After the friction limit iteration, the shear is within 2.5% of mu times the actual normal force, and 13 to 26% of the pad base nodes are at the limit.
- **Linearity:** the frictionless runs stay linear (deviations of 1e-6 kPa or less). The friction runs do not: once the base slips, the stress is not proportional to the load (deviations of 10 to 78 kPa across the passes). The stress animations in the Outputs section are only a scaling of the final state for the bonded model; a friction animation would need the full nonlinear history.

## Coarser zones (mesh sensitivity)

The same five cases were run with coarser zones: a pad target of 1000 mm (the coarse pad target of the Impact from Pipe 300 Coarse Mesh model), a 2000 mm wider zone and pad elements of thickness / 2. The pipe, cut and far-field sizes are unchanged. `python model.py --coarse` writes `output/coarse_zone/`, with `coarse_vs_fine.json` and `coarse_vs_fine_contact.png` comparing the two.

| Case | Soil nodes (current to coarse) | Depth change (max) | Middle bins change | Edge bins change (max) | Pipe level (kPa, current to coarse) | Settlement change |
|------|------------------------------|--------------------|--------------------|------------------------|-------------------------------------|-------------------|
| No pad | 11,014 to 9,482 | 2.0% | none (75 kPa) | none (75 kPa) | 1.93 to 2.00 | 0.02 mm |
| Pad 0.3 m, E 30 GPa | 12,608 to 5,742 | 2.9% | 0.3% | 6.3% | 4.17 to 5.59 | 0.06 mm |
| Pad 0.6 m, E 30 GPa | 11,644 to 9,732 | 1.2% | 1.0% | 7.0% | 4.05 to 4.09 | 0.05 mm |
| Pad 1.2 m, E 30 GPa | 11,498 to 9,634 | 4.2% | 2.6% | 24.8% | 4.28 to 4.26 | 0.18 mm |
| Pad 0.6 m, E 3 GPa | 11,644 to 9,732 | 1.2% | 0.3% | 6.9% | 3.98 to 4.03 | 0.04 mm |

- **Depth values** move by 4.2% at most, and the settlement by 0.2 mm at most. The depth and middle-bin results are reasonably robust.
- **Edge bins** move by up to 25% for the 1.2 m pad, and the coarse run is asymmetric (141 kPa on the left, 191 kPa on the right). The current study is also not perfectly symmetric: the right edge is 7 to 8% above the left in three of the four pad cases. So the edge bins are uncertain at roughly ±8%.
- **Pipe-level stress** for the 0.3 m pad moves by 34%, so that value is not converged and should not be used as a result.
- The current study remains the reference.

## Notes and limitations

- **Placeholders:** all soil, pad, pipe and interface values. Replace them before using any result.
- **Bonded pad:** the main results assume a bonded pad, whose E is 1000 times the soil's. The friction model at mu = 0.4 and the frictionless model are in the section above. The edge concentration is present in all three, so the bonded base does not cause it. The interface stiffness and mu are placeholders, and the friction limit is an iteration over passes rather than a contact solver.
- **Corner peaks and edge bins:** single nodes at the pad corners depend on mesh size. The edge bins are uncertain at about ±8% and change by up to 25% with coarser zones (see the section above). Use the middle bins and the depth values as the main results, and treat the edge bins as indicative.
- **Animations:** the model is linear elastic and the ramp is linear, so each frame is the final stress scaled by the load fraction. The animations show the stress building up, not a change in shape. A non-linear soil model would change this.
- **Plane strain:** valid only if the pipe, the cut and the pad are all long and parallel.
- **Box:** the base is fixed 100 m below ground. Stresses at depth depend on that and on the uniform placeholder stiffness.
- **Pipe present from the start:** as in Impact from Pipe 300. Its self-weight is in the gravity state.
- **Solver:** manual gravity and surcharge loops (AGENT.md §3c, §12z).
- **Slider values:** the sliders use the same element stresses as the maps. opstool's own values are Gauss-point means. They differ from the maps by a median of 0.06 kPa, and by up to about 12 kPa at re-entrant corners of the cut, the pipe and the pad.

## Reproduce

Run `model.py` with the project venv. The five cases take about 15 minutes on this machine. `python model.py --animations-only` rebuilds the GIFs from the saved frames without re-solving. `python model.py --sliders` writes the five response databases (about 25 minutes) and the opstool sliders. `python model.py --sliders-only` rebuilds only the sliders from the existing databases (about 2 minutes). `python model.py --interface` runs the frictionless and friction interface models for the four pad cases and writes the comparison (about 4 minutes). `python model.py --coarse` runs the five cases with coarser zones and writes the comparison (about 5 minutes).
