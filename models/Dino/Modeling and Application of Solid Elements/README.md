# Dino_SolidBrick

**Purpose:** Static gravity analysis of a 3D solid-element assembly (Dino Exam24). A 480-node, 248-element `stdBrick` mesh (ElasticIsotropic steel) carries three −1e5 N UZ loads ramped 0.01 × 100 steps (LoadControl). The node-102 history is validated against `ref/node102.out` and the full 480-node field against `node0.out` … `node4.out`.

**Building System:** 3D solid assembly meshed with **248 `stdBrick`** 8-node bricks over 480 nodes (ndm=3, ndf=3). 27 fully-fixed support nodes. **Material:** ElasticIsotropic steel (E=206000 MPa, nu=0.3) assigned directly to the bricks (no sections). No masses (static).

**Model Description:** 3D OpenSeesPy solid model (ndm=3, ndf=3). Single Plain pattern applies 3 × −1e5 N UZ loads (nodes 100, 101, 102); the source's single `LoadControl(1.0)` step is run as a 100 × 0.01 manual-loop ramp (the §3c permitted exception — SmartAnalyze forces DisplacementControl), which additionally validates 1:1 against the 100-row `node102.out` ramp reference shipped in `ref/`.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (ElasticIsotropic, E=206000 MPa) |
| Structural System | Solid brick assembly (248 stdBrick, 480 nodes) |
| Loading | Static gravity (3 × −100 kN UZ, 0.01 × 100 LoadControl ramp) |
| Analysis Type | Static — LoadControl manual loop |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for progress output)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Modeling and Application of Solid Elements/model.py"
```

## Verification

Node-102 history (LF, UX, UY, UZ) at every ramp step vs `ref/node102.out` (100 rows: col 0 = load factor, cols 1–3 = UX/UY/UZ); final state vs `ref/snode102.out` (1 row); full 480-node field vs `ref/node0.out` … `node4.out` (each one long row: time + UX/UY/UZ triplets per node).

| Quantity | Simulation | Reference | Notes |
|----------|-----------|-----------|-------|
| Steps recorded | 100 / 100 | 100 | exact 1:1 |
| Ramp LF/UX/UY/UZ per-point | RMS 0.000000 | — | mean rel error ≤0.0001% |
| Final (λ=1) | UX −0.041303, UY 0.005644, UZ −0.276373 | snode102.out identical | exact |
| Full field (480 nodes) | RMS 0.000000 mm | node0-4.out | mean rel error 0.1353% (near-zero DOFs) |

## Output

Written to `output/`:
- `node102_disp_history.csv` — (step, LF, UX, UY, UZ) at each of the 100 ramp steps
- `loadramp_compare.png` — capacity (UZ vs LF) + LF history: simulation (red dashed) vs `node102.out` reference (black solid)
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis, V5 final deformed UZ, V6 step-slider, V7 animation)
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal responses)

**References:**

Original source: `ref/exam24.tcl` (792-line Tcl stdBrick model), `ref/co.tcl.bak` (near-identical backup), `ref/model1.s2k` / `model2.s2k` (SAP2000 siblings). Reference results: `ref/node102.out` (100-row ramp), `ref/snode102.out` (1-row final state), `ref/node0.out` … `node4.out` (full-field final state).

**Notes:** Converted from `exam24.tcl`. **Brick recipe:** `nDMaterial ElasticIsotropic` (E, nu verbatim) feeds `element stdBrick tag n1..n8 matTag` directly — no transform/section/integration objects. **ndf=3 arity trap:** `fix` lines carry six values (`fix 1 1 1 1 1 1 1;`) on an ndf=3 model — only the leading triple is applied (all ones, fully fixed either way); likewise `ops.load` must take exactly 3 values — a 6-value call is *silently* rejected (`Node::addunbalLoad - load to add of incorrect size 6 should be 3`, warning only, zero load applied, run "converges" with all-zero displacements). **No MP constraints:** `puts "rigidDiaphragm"` / `"Equal DOF"` labels with no MP commands → `constraints("Plain")`. **Reference layout:** node0-4.out hold one long row each (time + triplets), not one row per node. **ODB:** nodal responses only (`save_brick_resp=False` — no stress reference). **Path depth:** standards/ is `parents[3]` (nests under `models/Dino/<analysis-name>/`) with `parents[2]` fallback. Run with: `uv run python "models/Dino/Modeling and Application of Solid Elements/model.py"`
