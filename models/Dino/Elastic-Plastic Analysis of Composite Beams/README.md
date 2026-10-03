# Dino_CompositeBeam

**Purpose:** Elasto-plastic displacement-controlled pushover of a 3D composite-beam frame (Dino Exam21). A 28-node, 39-element frame with three fiber sections (steel beam, deep concrete/steel composite girder, circular tube) is pushed down 150 mm at node 8 in 100 steps of −1.5 mm. Node-8 load-factor history is validated against `tcl_ref/node8.out`.

**Building System:** 3D composite frame — lower chord (nodes 3–13, section 1001/DB400×600), deep girder (nodes 14–24, section 1002/DB2000×200), circular-tube uprights (section 1003/DB120×10) plus side spans. 28 nodes, **39 `dispBeamColumn`** elements (Lobatto, 3 IP). Base: node 1 (0 0 1 0 0 0), node 2 fully fixed in translation. **Material:** Steel01 (fy=450 MPa, E=2.05e5, b=0.0001) + Elastic (E=2.482e4 concrete-ish, E=2.05e6 rigid tube) in fiber sections wrapped by rigid shear+torsion `section Aggregator`s. Lumped mass on UX/UY (static pushover — mass is inactive).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). Single Plain pattern applies the −1e5 N UZ reference load at node 8; `DisplacementControl` (node 8, DOF 3/UZ) via `opst.anlys.SmartAnalyze`, one −1.5 mm increment per reference step (`static_split([incr], maxStep=|incr|)`, §12am cadence) for 1:1 alignment with the 100-row reference. No gravity phase, no `loadConst` — the single pattern stays active throughout.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel + Elastic composite (Steel01 fy=450 MPa + Elastic, rigid-shear Aggregator) |
| Structural System | 3D composite-beam frame (39 dispBeamColumn, 3 fiber sections) |
| Loading | Displacement-controlled UZ pushover (−1.5 mm × 100 steps = −150 mm) |
| Analysis Type | Static — DisplacementControl via SmartAnalyze |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Elastic-Plastic Analysis of Composite Beams/model.py"
```

## Verification

Node 8 history (LF, UX, UY, UZ) at every recorded step, compared against the source reference (`tcl_ref/node8.out`, 100 rows: col 0 = load factor, cols 1–3 = node-8 UX/UY/UZ). `result.xlsx` (Fig1/Fig2 sheets) mirrors the same data.

| Quantity | Simulation | Reference (node8.out) | Notes |
|----------|-----------|----------------------|-------|
| Steps recorded | 100 / 100 | 100 | exact 1:1 |
| LF final (step 100) | 25.26251 | 25.26110 | 0.006% |
| LF per-point | RMS 0.00513 | — | mean rel error 0.0099% |
| UY final | 8.34840 mm | 8.34791 mm | 0.006% |
| UY per-point | RMS 0.00050 mm | — | mean rel error 0.0062% |
| UZ final | −150.00000 mm | −150.00000 mm | imposed, exact |

All DOFs match to **≤0.01% mean relative error**.

## Output

Written to `output/`:
- `node8_disp_history.csv` — (step, LF, UX, UY, UZ) at each of the 100 recorded steps
- `pushover_compare.png` — capacity (UZ vs LF) + LF history: simulation (red dashed) vs `node8.out` reference (black solid)
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis, V5 final deformed UZ, V6 step-slider, V7 animation)
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal responses)

**References:**

Original source: `tcl_ref/exam21.tcl` (285-line Tcl dispBeamColumn frame model). Reference results: `tcl_ref/node8.out` (100-row node-8 recorder: time/LF, UX, UY, UZ), `tcl_ref/result.xlsx` (same data, Fig1/Fig2 sheets).

**Notes:** Converted from `exam21.tcl`. **Verbatim fiber replay** (§12aq): the three fiber sections are parsed from the source `fiber` commands and re-emitted via `ops.fiber(y, z, area, mat)`, including the ten zero-area fibers of section 2 (harmless, preserved for fidelity). Each is wrapped by a `section Aggregator` (1001/1002/1003) adding rigid Vy/Vz/T codes. **`dispBeamColumn` via shared `beamIntegration("Lobatto", ...)`** — one rule per section (nIP=3), reused across elements (§12l). **`-GJ` required** (§12au): computed per-section as G·Σ(A·r²), dominated by the Aggregator's rigid torsion regardless. **`save_frame_resp=False`** in CreateODB (§12v). **Which Steel01?** The committed `exam21.tcl` is all-Elastic (Steel01 lines commented), but `node8.out` yields past ~step 30 — so the reference is the elasto-plastic run. Tested three variants 2026-10-03: all-Elastic matches steps 1–30 exactly then overshoots (LF 46.9 vs 25.3); Steel01 mats 1+4 (fy4=1000) undershoots (LF 20.4, UY 3.1 vs 8.3); **Steel01 mat 1 only (fy=450, E=2.05e5, b=0.0001), mat 4 Elastic** matches to 0.01% — adopted as `PLASTIC = True, PLASTIC_MAT4 = False` (set `PLASTIC = False` to reproduce the committed elastic Tcl). **Source quirks:** `fix` lines carry trailing `;` (regex tolerates); `puts "rigidDiaphragm"` / `"Equal DOF"` print labels with no MP-constraint commands, so `constraints("Plain")` throughout. Source already N-mm-MPa (masses used directly, no conversion). **Path depth:** standards/ is `parents[3]` (nests under `models/Dino/<analysis-name>/`) with `parents[2]` fallback. Run with: `uv run python "models/Dino/Elastic-Plastic Analysis of Composite Beams/model.py"`
