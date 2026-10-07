# Dino_SinglePressure

**Purpose:** Two-phase DisplacementControl pushover of a beam-on-hangers assembly with compression-only (`ENT`) truss links (Dino Exam10): phase 1 pushes the mast top down 1 mm (UZ −0.01 × 100), phase 2 pushes it +X 50 mm (UX 0.5 × 100). Node-24 history is validated against `ref/OPENSEES/node24.out` (200 rows), the final full-field state against `node0.out`, hanger axial histories against `ele23.out`.

**Building System:** Beam line (nodes 1–11 at z = 500 mm, 2000 mm span) hung by 11 vertical `truss` links (A = 250 mm², `ENT` compression-only, E = 199900 MPa) from fixed base nodes, plus a central mast (nodes 2–18–24, `elasticBeamColumn` A = 2.4e5 mm²) rising to z = 2500 mm. **Frame:** 12 `elasticBeamColumn` (beams A = 3e5 mm² / mast A = 2.4e5 mm², E = 24820 MPa). Node 3 slides (UX held); 10 base nodes fully fixed. Lumped UX/UY mass (pushover — mass is inactive).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6) replaying `co.tcl` verbatim via regex (nodes/mass/fix/transforms/beams/trusses). Phase 1: Plain pattern 1 (+1000 N UZ at node 24), `DisplacementControl` (node 24, DOF 3/UZ) via `opst.anlys.SmartAnalyze`, one −0.01 mm increment per reference step, then `loadConst`; phase 2: Plain pattern 2 (1 N UX at node 24), `DisplacementControl` (node 24, DOF 1/UX), one +0.5 mm increment per step. Per-increment `static_split([incr], maxStep=|incr|)` cadence keeps the recorder 1:1 with the 200 reference rows.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Concrete frame (E = 24820 MPa) + ENT compression-only hangers |
| Structural System | Beam on 11 hanger trusses + mast (12 beams, 11 trusses, 24 nodes) |
| Loading | Two-phase DisplacementControl: UZ −1 mm then UX +50 mm (200 steps) |
| Analysis Type | Static — DisplacementControl via SmartAnalyze |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Application of a Single-Pressure Connection Unit/model.py"
```

## Verification

200-step run (`ok` throughout, 200/200 recorded) against the source recorders (col 0 = pseudo-time, cols 1–3 = UX/UY/UZ; `ele23.out` = time + 11 hanger axials).

| Quantity | Simulation | Reference | Notes |
|----------|-----------|-----------|-------|
| Steps recorded | 200 / 200 | 200 | exact 1:1 (100 down + 100 push) |
| Node-24 UX final | 50.00000 mm | 50.00000 mm | imposed, exact; per-point RMS 0 |
| Node-24 UZ final | 14.50153 mm | 14.50150 mm | per-point RMS 1e-05, 0.0000% |
| Node-24 UY | 0 throughout | 0 throughout | exact |
| Hanger axial (11 × 200) | RMS 0.094 N | — | \|ref\|>1 N mean rel 0.0001% (slack tail excluded) |
| Final full-field (24×3) | RMS 1.18e-05 mm | — | mean rel 0.0001% |
| Pseudo-time phase 1 | RMS 2.6e-04 | — | exact; bookkeeping only |
| Pseudo-time phase 2 | diverges | — | documented deviation, see Notes |

All physical quantities match to **≤0.0001%**; imposed UX is exact; hangers go slack (0 N) in the lateral tail as expected for compression-only links.

## Output

Written to `output/`:
- `node24_history.csv` — (time, UX, UY, UZ) at node 24 for each of the 200 steps
- `hanger_axial_history.csv` — 11 hanger axialForces per step (N, eles 13–23)
- `pushover_compare.png` — trajectory (UX vs UZ) sim vs `node24.out` + hanger force histories
- `vis_01_nodes.html` … `vis_04_pre_analysis.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis)
- `vis_05_deformed.html`, `vis_06_slider.html` — UX deformed + 200-step slider
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal + frame + truss)

**References:**

Original source: `ref/OPENSEES/co.tcl` (139-line Tcl beam + mast model) + `ref/OPENSEES/EXAM10.tcl` (same phases) + `ref/OPENSEES/EXAM10.s2k` (SAP2000 sibling) + `ref/ETABS/` (ETABS 9.x sibling). Reference results: `ref/OPENSEES/node0.out` (200-row full-field, nodes 1–24), `node24.out` (200-row mast-top history), `ele23.out` (200-row hanger axial histories), `ele0.out` (200-row all-element dump, no Tcl recorder line — secondary).

**Notes:** Converted from `co.tcl`. **Single-pressure recipe:** `element truss tag i j 250 MAT_ENT` with `uniaxialMaterial ENT 1 199900` — tensionless hangers that go slack (0 N) once the mast leans. **Dead tags 2/3** (uniaxial Elastic) kept for fidelity — `elasticBeamColumn` takes E/G as numeric literals. **Pseudo-time deviation:** phase-1 time matches to 2.6e-04, but phase-2 time diverges by construction — the source issues a bare `loadConst 0` (missing `-time` flag; behaviour is Tcl-version-specific: lock-without-reset vs reset), while the conversion uses the standard `loadConst("-time", 0.0)` per AGENT.md §3c. Tested variants (no-op, bare `loadConst()`) reproduce at most the first phase-2 step; every displacement (24×3×200) and every hanger force (11×200) matches regardless, so time is reported split-by-phase and excluded from pass/fail. **`save_truss_resp=True`** in CreateODB (hanger axials). **Source quirks:** `fix` lines carry trailing `;` (regex tolerates); `puts "rigidDiaphragm"` label with no MP commands → `constraints("Plain")`; source already N-mm-MPa (masses used directly). **Path depth:** standards/ is `parents[3]` (nests under `models/Dino/<analysis-name>/`) with `parents[2]` fallback. Run with: `uv run python "models/Dino/Application of a Single-Pressure Connection Unit/model.py"`
