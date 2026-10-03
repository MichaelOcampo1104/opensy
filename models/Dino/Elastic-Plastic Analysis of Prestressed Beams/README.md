# Dino_PrestressedBeam

**Purpose:** Displacement-controlled UZ pushdown of a 3D prestressed beam (Dino). A 24-node model (23 `dispBeamColumn` fiber elements + 12 rigid `elasticBeamColumn` links, Steel01/Concrete02 sections with a 1600 MPa strand ring) runs a zero-load gravity step then 360 pushdown steps of −1.0 mm at node 19. The load-factor history validates against `ref/OpenSEES/node19.out`.

**Building System:** 3D prestressed beam — 24 nodes (node 1 near-fixed; nodes 2–24 guided rollers holding UY/RY/RZ). **Sections:** concrete grid (Concrete02 fpc=−26.8 MPa) + prestressing strand ring (Steel01 fy=1600 MPa, E=206000, 20 fibers on r=50 mm) + mild steel (fy=200 MPa); 12 rigid links (E ~ 2e8 MPa scale) tie the tendon line to the girder. No masses (static).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). **Phase 1:** Plain pattern 1 (a single *zero* load at node 3 — structurally a no-op, replayed verbatim); LoadControl × 1 manual loop (§3c exception). **Phase 2:** Plain pattern 2 (−1e3 N UZ at node 19, defined after phase 1; no `loadConst` in the source, moot since phase 1 is load-free); `DisplacementControl` (node 19, DOF 3/UZ) via `opst.anlys.SmartAnalyze`, one −1.0 mm increment per reference step (§12am cadence) for 1:1 alignment with the 361-row reference (1 gravity + 360 pushdown; the Tcl recorder writes one row per analyze step, no initial row).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Prestressed (Steel01 strand fy=1600 MPa + Concrete02) |
| Structural System | Prestressed beam (23 dispBeamColumn + 12 rigid links) |
| Loading | Zero-load gravity then UZ pushdown (−1.0 mm × 360 = −360 mm) |
| Analysis Type | Static — LoadControl then DisplacementControl |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Elastic-Plastic Analysis of Prestressed Beams/model.py"
```

## Verification

Node-19 history (LF, UX, UY, UZ) at every recorded step vs `ref/OpenSEES/node19.out` (361 rows: col 0 = load factor, cols 1–3 = UX/UY/UZ). Full field (`node0.out`) shares the layout.

| Quantity | Simulation | Reference | Notes |
|----------|-----------|-----------|-------|
| Steps recorded | 361 / 361 | 361 | exact 1:1 (1 + 360) |
| LF final | 999.35985 | 999.217 | 0.014% |
| LF per-point | RMS 2.39676 | — | mean rel error 0.4986% (post-yield path) |
| UZ final | −360.00000 mm | −360.00000 mm | imposed, exact |

LF matches to **0.5%**; the residual is post-yield solver-path divergence (SmartAnalyze `NormDispIncr`/KrylovNewton vs Tcl Newton — §12aw directional-mismatch class, negligible here), not a modeling error: the elastic range and all imposed quantities are exact.

## Output

Written to `output/`:
- `node19_disp_history.csv` — (idx, LF, UX, UY, UZ) at each of the 361 recorded steps
- `pushdown_compare.png` — capacity (UZ vs LF) + LF history: simulation (red dashed) vs `node19.out` reference (black solid)
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal responses)

**References:**

Original source: `ref/OpenSEES/co.tcl` (229-line Tcl model) + `co.tcl.bak` (identical), `ref/OpenSEES/Model.s2k` (SAP2000 sibling), `ref/ETABS/` (commercial provenance). Reference results: `ref/OpenSEES/node19.out` (361-row node-19 recorder), `node0.out` (full field), `result.xlsx`.

**Notes:** Converted from `ref/OpenSEES/co.tcl`. **Verbatim fiber replay** (§12aq) via `ops.fiber(y, z, area, matTag)` (§12ay area-is-THIRD). **`dispBeamColumn` via shared `beamIntegration("Lobatto", ...)`** per section (§12l); **`elasticBeamColumn` native 3D** (rigid-scale A/E/G/J/Iy/Iz verbatim). **`-GJ` physical** (G·Σ(A·r²)): no Aggregators wrap these sections, so fiber GJ is the true torsion (no §12ba parallel-add issue). **`save_frame_resp=False`** (§12v convention). **Source quirks:** `fix` lines carry trailing `;` (regex tolerates); `puts "rigidDiaphragm"` label with no MP commands → `constraints("Plain")`; source file carries GBK Chinese comment bytes (read tolerantly — only ASCII numerics are parsed). Source already N-mm-MPa. **Path depth:** standards/ is `parents[3]` with `parents[2]` fallback. Run with: `uv run python "models/Dino/Elastic-Plastic Analysis of Prestressed Beams/model.py"`
