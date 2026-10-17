# Dino_SeamConnection

**Purpose:** Displacement-controlled UX pushover (3 mm × 100 steps = 300 mm at node 1) of a main-tower + podium assembly linked by 4 `ElasticPPGap` trusses across a 200 mm seismic seam (Dino Exam10). Node-1 history is validated against `ref/OPENSEES/node1.out`, the final full-field state against `node0.out` (nodes 1–32); `node12.out`/`node13.out` cover the seam neighbour nodes.

**Building System:** 4-storey main tower (3 × 3 m plan, 12 m high) + 2-storey podium (3 × 3 m bays from X = 3200 to 6200 mm, 6 m high) separated by a 200 mm seismic seam (X = 3000 → 3200 mm). **Elements:** 48 `elasticBeamColumn` (beams A = 1e5 mm² / columns A = 4e4 mm², E = 24820 MPa) + 4 `truss` seam links (A = 4265 mm², `ElasticPPGap` E = 200000 MPa). 8 partial base fixities (UX/UY/UZ fixed, rotations free); lumped UX/UY mass (pushover — mass is inactive).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6) replaying `EXAM10.tcl` verbatim via regex (nodes/mass/fix/transforms/beams/trusses). Single Plain pattern (tag 1) applies 8 × 1 kN UX reference loads (nodes 1, 2, 5, 6, 9, 10, 17, 18); `DisplacementControl` (node 1, DOF 1/UX) via `opst.anlys.SmartAnalyze`, one 3 mm increment per reference step (`static_split([incr], maxStep=|incr|)`) for 1:1 alignment with the 100-row reference. No gravity phase, no `loadConst` — the single pattern stays active throughout.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Concrete frame (E = 24820 MPa) + ElasticPPGap seam trusses |
| Structural System | Tower + podium with trussed seismic seam (48 beams, 4 trusses, 32 nodes) |
| Loading | Displacement-controlled UX pushover (3 mm × 100 steps = 300 mm) |
| Analysis Type | Static — DisplacementControl via SmartAnalyze |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Application of Seam Connection Unit/model.py"
```

## Verification

100-step pushover (`ok` throughout, 100/100 recorded) against the source recorders (col 0 = pseudo-time/load factor, cols 1–3 = UX/UY/UZ).

| Quantity | Simulation | Reference | Notes |
|----------|-----------|-----------|-------|
| Steps recorded | 100 / 100 | 100 | exact 1:1 |
| Node-1 time final | 41.44085 | 41.44080 | 0.0001% |
| Node-1 UX final | 300.00000 mm | 300.00000 mm | imposed, exact |
| Node-1 UZ final | 1.94694 mm | 1.94694 mm | 0.0001% |
| Node-1 per-point | RMS ≤ 3e-05 | — | mean rel error ≤ 0.0001% (all 4 cols) |
| Final full-field (32×3) | RMS 9.79e-05 mm | — | mean rel 0.0001% |
| Ele-33 axialForce final | −24631.34 N | — | sim only (see Notes) |

Nodal histories match to **≤0.0001%**; the imposed UX is exact.

## Output

Written to `output/`:
- `node1_ux_history.csv` — (time, UX, UY, UZ) at node 1 for each of the 100 steps
- `ele33_axial_history.csv` — ele-33 axialForce per step (N, compression negative)
- `pushover_compare.png` — capacity (UX vs time) sim vs `node1.out` + seam-truss force history
- `vis_01_nodes.html` … `vis_04_pre_analysis.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis)
- `vis_05_deformed.html`, `vis_06_slider.html` — UX deformed + 100-step slider
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal + frame + truss)

**References:**

Original source: `ref/OPENSEES/EXAM10.tcl` (214-line Tcl tower + podium model) + `ref/OPENSEES/EXAM10.s2k` (SAP2000 sibling) + `ref/ETABS/` (ETABS 9.x sibling). Reference results: `ref/OPENSEES/node0.out` (100-row full-field, nodes 1–32), `node1.out`/`node12.out`/`node13.out` (100-row single-node histories), `ele33axialForce.out`, `ele33deformation.out`.

**Notes:** Converted from `EXAM10.tcl`. **Seam recipe:** `element truss tag i j 4265 MAT_GAP` with `uniaxialMaterial ElasticPPGap 1 200000 -2e10 -1` for the 4 cross-seam diagonals (11↔14, 12↔13 at z = 6000; 19↔22, 20↔21 at z = 3000). **Dead tags 2/3** (uniaxial Elastic) kept for fidelity — `elasticBeamColumn` takes E/G as numeric literals. **Corrupted element recorders:** `ele33axialForce.out` is byte-identical to the pseudo-time column (the Tcl line carries a stray control byte between `-ele` and `33`, so OpenSees recorded time instead of force) and `ele33deformation.out` is empty (0 bytes); nodal recorders are therefore the authoritative anchor and ele-33 is reported sim-only. **`save_truss_resp=True`** in CreateODB (truss axial responses; link disabled). **Source quirks:** `fix` lines carry trailing `;` (regex tolerates); `puts "rigidDiaphragm"` label with no MP commands → `constraints("Plain")`; source already N-mm-MPa (masses used directly). **Path depth:** standards/ is `parents[3]` (nests under `models/Dino/<analysis-name>/`) with `parents[2]` fallback. Run with: `uv run python "models/Dino/Application of Seam Connection Unit/model.py"`
