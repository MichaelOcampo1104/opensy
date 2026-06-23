# Citiner — Cantilever RC Column Pushover (AdaBoost PHL)

Monotonic or cyclic displacement-controlled pushover of a single RC cantilever
column with a fiber-section `beamWithHinges` element. Column geometry,
reinforcement, material strengths, and plastic-hinge length (`PHL`) are
parameterised so they can be set from an external ML model (e.g. the companion
AdaBoost notebook in `ref/`).

## Source

Tcl templates by the Citiner group:
- `ref/monotonicTemplate.tcl` — Concrete01, Linear geomTransf, single push to 72 mm
- `ref/cyclicTemplate.tcl` — Concrete02, PDelta geomTransf, 23-segment alternating protocol

Converted to N-mm-MPa per AGENT.md §3a.

## Usage

```bash
conda activate opensy
python models/Citiner/model.py
```

Set the module-level constant `CYCLIC = True` (cyclic, default) or
`CYCLIC = False` (monotonic) to select the loading protocol.

## Parameters

Column properties in Section 3 of `model.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `B`       | 150 mm  | Section width |
| `H`       | 140 mm  | Section height |
| `L`       | 1500 mm | Column length |
| `db`      | 10 mm   | Longitudinal bar diameter |
| `nb`      | 6       | Number of longitudinal bars |
| `dbv`     | 6 mm    | Stirrup diameter |
| `fy`      | 557 MPa | Steel yield strength |
| `Es`      | 200 GPa | Steel elastic modulus |
| `fpc_c`   | -52 MPa | Confined concrete strength |
| `PHL`     | 99.82 mm| Plastic hinge length (AdaBoost) |
| `axial_ratio` | 0.10 | P / (Ag · fpc) |

## Output

HTML visualisations are written to `output/`:
- `vis_01_nodes.html` — node positions + boundary conditions
- `vis_02_model.html` — undeformed geometry with numbering
- `vis_03_loads.html` — load vectors
- `vis_04_pre_analysis.html` — final geometry check
- `vis_05_deformed_UX.html` — deformed shape (deformation slider)
