# Dino_IsolatedFrame

**Purpose:** Nonlinear dynamic time-history of a 3D frame on rubber isolation bearings (Dino). A 126-node model (252 `elasticBeamColumn` + 9 `zeroLength` Steel02 isolators, 5% Rayleigh damping on modes 1–2) runs 20 s of ground motion (1000 steps × 0.02 s). Node and isolator/frame histories validate against `ref/opensees/node2.out`, `node118.out`, `ele244.out`, `ele245.out`, `ele244d.out`.

**Building System:** 3D frame on 9 rubber bearings — 126 nodes, 252 `elasticBeamColumn` frame members with inline A/E/G/J/Iy/Iz, 9 `zeroLength` isolators (Steel02 bilinear: Fy=100000 N, E=2000 MPa, b=0.15, DOFs 1–2) linking base nodes 109–117 to deck nodes 118–126, with `equalDOF` tying DOFs 3–6 across each bearing. 9 fixed base nodes. Lumped mass on 117 nodes. T1=2.176 s, T2=2.106 s (closely spaced isolated modes).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). Eigen (2 modes) → Rayleigh 5% (`rayleigh alphaM betaKcurr 0 0`, computed from ω1/ω2 exactly as the source) → `UniformExcitation` (UX, `Path` series from `ground_motions/gm1x.txt`: 1501 points, dt=0.02 s, factor 10; first 20 s consumed) → transient Newmark(0.5, 0.25) via `opst.anlys.SmartAnalyze` (`transient_split` + per-step `TransientAnalyze`, `ok<0` break). No gravity phase in the source — direct transient from the zero state. `Transformation` constraints (MP `equalDOF`s, as in the source), `UmfPack` system (source solver).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (Steel02 isolators + Elastic frame) |
| Structural System | Frame on 9 rubber bearings (252 elasticBeamColumn + 9 zeroLength) |
| Loading | Dynamic earthquake (UniformExcitation UX, 20 s) |
| Analysis Type | Transient — Newmark via SmartAnalyze |
| Earthquake Records | gm1x.txt (1501 pts, dt=0.02 s, factor 10) in `ground_motions/` |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Dynamic Analysis of a Frame with Vibration Isolation/model.py"
```

## Verification

Per-step histories (1000 rows) vs `ref/opensees/`: node-2/node-118 disp (`node2.out`, `node118.out`: time + UX/UY/UZ), ele-244 `localForce`/`deformation` (`ele244.out`, `ele244d.out`), ele-245 `localForce` (`ele245.out`). Reference layout is time + values (col 0 = time).

| Quantity | Simulation | Reference | Notes |
|----------|-----------|-----------|-------|
| Steps recorded | 1000 / 1000 | 1000 | exact 1:1 |
| Node-2 / 118 UX | RMS ≤0.00012 | — | mean rel error 0.0001% |
| Ele-244 force / deformation | peak 119114.64 / 113.8956 | 119115.00 / 113.8960 | 0.0001% |
| Ele-245 force magnitudes | peak 303967152.55 | 303967000.00 | magnitude rel error 0.0002% |

Ele-245 matches to **0.0002% in magnitude**; the Vz shear pair (2 of 12 components) carries the opposite sign vs the Tcl recorder — a local-axis sign-convention difference (same class as the STAAD mappings), magnitudes exact to 5 digits.

## Output

Written to `output/`:
- `node2_disp_history.csv`, `node118_disp_history.csv` — (t, UX, UY, UZ) per step
- `dynamic_compare.png` — node-2/node-118 UX histories: simulation (red dashed) vs reference (black solid)
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal, throttled every 2nd step)

**References:**

Original source: `ref/opensees/co.tcl` (836-line Tcl model) + `co.tcl.bak` (near-identical; differs only in comment banners and equalDOF/material comment lines — element 245 and all numerics identical). Sibling variants not converted: `ref/openseesWithoutRubberIsolator/` (fixed-base: deck at z=1750, no isolators), `ref/{sap2000,sap2000WithoutRubberIsolator,ETABS}/` (commercial-model provenance). Ground motion: `ground_motions/gm1x.txt` (copied from `ref/opensees/gm1x.txt` per catalogue convention).

**Notes:** Converted from `ref/opensees/co.tcl`. **`elasticBeamColumn` keeps its native 3D form** `(tag, i, j, A, E, G, J, Iy, Iz, transf)`; **`zeroLength` isolators** `(tag, n1, n2, -mat m1 m2, -dir d1 d2)` parsed generally. **No MP-constraint issue:** `equalDOF` on DOFs 3–6 + `constraints("Transformation")` exactly as the source (§12an-consistent). **Transient pattern:** `ops.integrator("Newmark", 0.5, 0.25)` set *before* `SmartAnalyze`; `transient_split(1000)` + `TransientAnalyze(dt)` with `ok<0` break; `odb.fetch_response_step()` every 2nd step (§3d: 500 fetches), in-loop `nodeDisp`/`eleResponse` every step for 1:1 validation. **No gravity/loadConst** in the source — direct transient (§12i N/A). **GM handling:** `Path` series with `-factor 10` applied in-series (verbatim); first 1000 of 1501 points consumed. **Ele-245 Vz sign convention** (above) — magnitudes authoritative. Source already N-mm-MPa. **Path depth:** standards/ is `parents[3]` with `parents[2]` fallback. Run with: `uv run python "models/Dino/Dynamic Analysis of a Frame with Vibration Isolation/model.py"`
