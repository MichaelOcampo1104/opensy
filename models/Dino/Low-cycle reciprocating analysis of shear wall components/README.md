# Dino_ShearWallCyclic

**Purpose:** Low-cycle reciprocating (cyclic) displacement analysis of a 3D shear-wall component (Dino). A 31-node model (12 `dispBeamColumn` fiber elements + 24 `elasticBeamColumn`) runs gravity then 9 `DisplacementControl` UY segments (±0.2–±1.4 mm × 100 steps) at node 26. The load-factor history validates against `OPENSEES/node26.out` (glitch-aware — see below).

**Building System:** 3D shear-wall component — 31 nodes, 3 fully-fixed base nodes (8, 9, 10). 12 `dispBeamColumn` fiber elements (Steel01 fy=395 MPa + Concrete01 fpc=−30 MPa sections wrapped by rigid shear+torsion `section Aggregator`s, Lobatto 3 IP) + 24 `elasticBeamColumn` with inline properties. No masses (static cyclic).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). **Gravity:** Plain pattern 1 (3 × −2.433e5 N UZ at nodes 29–31); LoadControl × 1 manual loop (§3c exception); `loadConst` (source-verbatim). **Cyclic:** Plain pattern 2 (defined after `loadConst`, §12z-1; 1 kN UY reference at node 26); 9 segments `[(+0.2,100), (−0.4,100), (+0.6,100), (−0.8,100), (+1.0,100), (−1.2,100), (+1.4,100), (−1.4,100), (+1.2,100)]` parsed verbatim from the source's integrator/analyze pairs, each fed as one SmartAnalyze target (`static_split`, §12am cadence) with full fallback (relaxation + minStep) for fiber softening at reversals.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC (Steel01 + Concrete01 fiber, rigid-shear Aggregator) |
| Structural System | Shear-wall component (12 dispBeamColumn + 24 elasticBeamColumn) |
| Loading | Gravity then cyclic UY (9 segments, ±0.2–±1.4 mm × 100 steps) |
| Analysis Type | Static — LoadControl gravity + DisplacementControl cyclic |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Low-cycle reciprocating analysis of shear wall components/model.py"
```

## Verification

Node-26 history (LF + UX/UY/UZ) vs `OPENSEES/node26.out`. **Reference-file forensics first:** the file holds 917 valid 4-col rows (plus one 5-column glitch row) vs 901 clean steps (1 + 900) — around step ~857 the run diverged (UY teleported −18 mm for 2 rows) then continued 60 rows past it (restart overlap). `node0.out` (903 rows) and `ele0.out` (902) disagree with each other too. So index alignment is exact only over rows 0–800; segment 9 and the final state are compared by peak/value.

| Quantity | Simulation | Reference | Notes |
|----------|-----------|-----------|-------|
| Steps converged | 901 / 901, no glitch | 917 rows incl. divergence + overlap | sim sails through (SmartAnalyze sub-stepping) |
| Segment peaks \|LF\| (9) | — | — | sim +5.0–7.2% throughout, mean 5.9% |
| Clean prefix RMS (801 rows) | 12.63 | peak scale 373 | 3.4% of peak |
| LF / UY final | 172.90 / 60.66 mm | 174.04 / 60.50 mm | 0.7% / 0.3% |

Hysteresis loops overlay (pinching captured); the systematic ~6% peak excess is solver-path/element-formulation class (§12aw — accepted for softening RC cyclic; cf. §12e 10–15%). The reference's mid-protocol divergence is a failed-step artifact the SmartAnalyze run correctly avoids.

## Output

Written to `output/`:
- `node26_disp_history.csv` — (idx, LF, UX, UY, UZ) per converged sub-step
- `cyclic_compare.png` — hysteresis (UY vs LF) + LF history: simulation (red dashed) vs `node26.out` (black solid)
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal responses)

**References:**

Original source: `OPENSEES/co1.tcl` (321-line Tcl cyclic wall model), `ETABS/` (commercial provenance). Reference results: `OPENSEES/node26.out` (917 valid rows + 1 glitch row), `node0.out` (903 rows full field), `ele0.out` (902 rows element forces).

**Notes:** Converted from `OPENSEES/co1.tcl`. **Verbatim fiber replay** (§12aq) via `ops.fiber(y, z, area, matTag)` (§12ay area-is-THIRD); Aggregators 1001–1002 (rigid Vy/Vz/T). **`dispBeamColumn` via shared `beamIntegration("Lobatto", ...)`** (§12l); **`elasticBeamColumn` native 3D**. **`-GJ` = 1.0 negligible** (Aggregator-wrapped → §12ba parallel-add rule). **`save_frame_resp=False`** (§12v). **Gravity → `loadConst` → cyclic pattern** (§12z-1; source has `loadConst 0.0`, no `wipeAnalysis` — wipe added, harmless). **Source quirks:** `fix` trailing `;` tolerated; `puts "rigidDiaphragm"` label with no MP commands → `constraints("Plain")`; GBK Chinese comment bytes (read tolerantly). Source already N-mm-MPa. **Path depth:** standards/ is `parents[3]` with `parents[2]` fallback. Run with: `uv run python "models/Dino/Low-cycle reciprocating analysis of shear wall components/model.py"`
