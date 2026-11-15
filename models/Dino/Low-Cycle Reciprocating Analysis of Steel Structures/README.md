# Dino_LowCycleSteel

**Purpose:** Gravity + 4-phase low-cycle UX reciprocation of a 2-storey steel frame (Dino Exam08). A 112-node, 128-element `dispBeamColumn` frame (Steel01 DH300X400X25X25 columns + DH200X200X20X12 beams/braces in shear+torsion Aggregators) carries −4e5 N gravity, then crown node 4 is cycled +100 / −200 / +225 / −250 mm (4000 steps) under a 250 N reference load. Node-4 load-factor history is validated against `ref/OPENSEES/result.xls` right block — exact at all 4010 steps.

**Building System:** 2-storey 3 m × 3 m steel frame (4 m + 4 m storeys), fixed base (nodes 9–12 fully fixed). Columns DH300X400X25X25 (section 1001), beams + diagonal braces DH200X200X20X12 (section 1002). 112 nodes, **128 `dispBeamColumn`** elements (Lobatto, 3 IP; `Linear` transforms — columns/beams (1,0,0)/(0,0,1), braces (±0.8,0,0.6)). **Material:** Steel01 (fy=295 MPa, E=2.06e5, b=0.001) in all 72 fibres, wrapped by rigid shear+torsion `section Aggregator`s. Lumped mass on UX/UY (static — mass is inactive).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). DEAD pattern: −1e5 N UZ at top nodes 2/4/6/8, `LoadControl` 0.5 × 10 steps (manual loop, AGENT §3c exception) → LF 5.0, then `loadConst`. PUSH pattern: +250 N UX at nodes 2/4/6/8; `DisplacementControl` (node 4, DOF 1/UX) via `opst.anlys.SmartAnalyze` in 4 phases (+0.1×1000 / −0.2×1000 / +0.225×1000 / −0.250×1000), one increment per reference step (`static_split([incr], maxStep=|incr|)`, §12am cadence) for 1:1 alignment with the 4010-row reference.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (Steel01 fy=295 MPa, E=2.06e5, b=0.001, fiber + rigid-shear Aggregator) |
| Structural System | 2-storey steel frame + braces (128 dispBeamColumn, 2 fiber sections) |
| Loading | Gravity (−4e5 N → LF 5.0) + cyclic UX (+100/−200/+225/−250 mm, 4000 steps) |
| Analysis Type | Static — LoadControl gravity, DisplacementControl cyclic via SmartAnalyze |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26, xlrd 2.0.2) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
chcp 65001; $env:PYTHONUTF8="utf-8"; uv run python "models/Dino/Low-Cycle Reciprocating Analysis of Steel Structures/model.py"
```

## Verification

Node-4 history (LF, UX, UY, UZ) at every recorded step, compared against `ref/OPENSEES/result.xls` Sheet1 (4010 rows; cols A–D = left block, cols F–I = right block; col 0/5 = load factor, cols 1–3/6–8 = node-4 UX/UY/UZ). **Anchor is the right block.**

| Quantity | Simulation | Reference (right block) | Notes |
|----------|-----------|------------------------|-------|
| Steps recorded | 4010 / 4010 | 4010 | exact 1:1, zero solver failures |
| Gravity LF (step 10) | 5.0 | 5.0 | exact |
| LF peak ph.1 (UX +99.98) | 6706.9 | 6706.9 | exact |
| LF peak ph.2 (UX −100.02) | −6727.2 | −6727.2 | exact |
| LF peak ph.3 (UX +124.98) | 6755.4 | 6755.4 | exact |
| LF peak ph.4 (UX −125.02) | −6779.0 | −6779.0 | exact |
| LF per-point | max rel err 0.00016 | — | mean 1e-6, all 4010 steps |
| UX final | −125.018 mm | −125.018 mm | imposed, exact |

Stable kinematic-hardening loops at all amplitudes — no degradation, as expected for Steel01.

## Output

Written to `output/`:
- `cyclic_history.npz` — `hist` (4, 4010) sim [LF, UX, UY, UZ] + `refA`/`refB` (4, 4010) xls blocks
- `vis_01_nodes.html` … `vis_06_slider.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis, V5 deformed, V6 step-slider; ODB throttled to every 20th cyclic step)
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal responses)

**References:**

Original source: `ref/OPENSEES/Exam08.tcl` (562-line Tcl dispBeamColumn frame). Reference results: `ref/OPENSEES/result.xls` (Sheet1 only; Sheet2/3 empty). ETABS source model: `ref/ETABS/EXAM08.EDB` (+ `.e2k`/`.s2k` text exports, including `ref/OPENSEES/EXAM08.s2k`).

**Notes:** Converted from `Exam08.tcl`. **Verbatim replay:** all 112 nodes + masses (nodes 1–12/29–44/61–76), 4 fixed supports, 128 `Linear` transforms, 128 elements, both 36-fibre sections (all-Steel01) + Aggregators 1001/1002 via shared Lobatto rules (§12l). **Dead materials kept:** Elastic mats 2/3 defined, unreferenced (§12ap-6); the commented `Elastic 1` line is NOT defined. **`-GJ` = 1.0 on both sections** (LESSONS item 11: source omits `-GJ`, Aggregator T governs; polar G·Σ(A·r²) would be 144×/83× T). **Two deliberate solver deviations:** (1) `algoTypes=[10]` = plain Newton — the opensy default first-flag 40 is KrylovNewton, which explodes where Newton passes; (2) `testTol 1e-6` instead of the source 0.1 — see below. `system UmfPack` + `numberer RCM` mirror the source PUSH settings (UmfPack roundoff passes the phase-1 capacity point where BandGeneral breaks Newton). **Which xls block?** The LEFT block is a loose-tolerance (0.1) Newton artifact path: it matches the virgin curve (phase-1 peak 6636.8 vs true 6706.9) then spuriously softens (6253 end of phase 1, decaying to 5900 by phase 4) — impossible for hardening Steel01 under Linear geometry, and unreproducible under current OpenSeesPy (Newton/Krylov die at its reversal kinks; algo-switching and bisection branch-jump or stall). The RIGHT block is the true-equilibrium curve (tight-tol OpenSees rerun by the author): hardening Steel01 loops, matched here to mean rel err 1e-6. **Path-depth:** standards/ is `parents[3]` with `parents[2]` fallback. Run with: `uv run python "models/Dino/Low-Cycle Reciprocating Analysis of Steel Structures/model.py"`
