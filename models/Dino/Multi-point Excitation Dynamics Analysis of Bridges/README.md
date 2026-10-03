# Dino_MultiBridge

**Purpose:** Dynamic time-history of a 3D bridge under multi-support displacement excitation (Dino). A 241-node model (367 `elasticBeamColumn` + 72 `ShellMITC4` deck shells, 5% Rayleigh damping on modes 1–2) runs 20 s of support displacement (1000 steps × 0.02 s) through two `MultipleSupport` patterns. Histories validate against `ref/OPENSEES/node203_mul.out` (0.0001%).

**Building System:** 3D bridge — 241 nodes on 4 imposed-motion supports (nodes 1–4, fully fixed), 367 `elasticBeamColumn` frame members with inline A/E/G/J/Iy/Iz, 72 `ShellMITC4` deck shells (260 mm `PlateFiber`: ElasticIsotropic 26000/0.2). Lumped mass on all 241 nodes. T1=0.957 s, T2=0.856 s.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). Eigen (2 modes) → Rayleigh 5% (`rayleigh alphaM betaKcurr 0 0`, computed from ω1/ω2 exactly as the source) → two `MultipleSupport` patterns (§12p form): pattern 1 drives supports 1/3 (UX) from record 1, pattern 2 drives supports 2/4 from record 2 (`groundMotion` + `imposedMotion`, `Path` series from `ground_motions/dm{1,2}x.txt`: 1501 points, dt=0.02 s, factor 1; first 20 s consumed) → transient Newmark(0.5, 0.25) via `opst.anlys.SmartAnalyze` (`transient_split` + per-step `TransientAnalyze`, `ok<0` break). No gravity phase in the source — direct transient from the zero state. `Transformation` constraints, `SparseSPD` system, `EnergyIncr 1e-4/200` test tolerance (all source-verbatim; SmartAnalyze defaults are far too tight here and stall at step 1).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Elastic (frame + 260 mm PlateFiber deck) |
| Structural System | Bridge, multi-support excitation (367 elasticBeamColumn + 72 ShellMITC4) |
| Loading | Dynamic multi-support displacement (2 records, 20 s) |
| Analysis Type | Transient — Newmark via SmartAnalyze |
| Earthquake Records | dm1x.txt, dm2x.txt (1501 pts, dt=0.02 s, factor 1) in `ground_motions/` |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Multi-point Excitation Dynamics Analysis of Bridges/model.py"
```

## Verification

Per-step histories (1000 rows) vs `ref/OPENSEES/node203_mul.out` (time + UX/UY/UZ at node 203 — **this** is the record reproduced by the committed `co.tcl`, proven below). Reference layout is time + values (col 0 = time).

| Quantity | Simulation | Reference | Notes |
|----------|-----------|-----------|-------|
| Steps recorded | 1000 / 1000 | 1000 | exact 1:1 |
| Node-203 UX | RMS 0.00014 | — | mean rel error 0.0001% (peaks ±161 mm) |
| Node-203 UY / UZ | RMS ≤0.00008 | — | mean rel error 0.0001% |

**Which reference? (§12aq forensics):** `ref/` ships two overlapping sets — `node203.out`/`ele330.out`/`node0-2.out` (self-consistent) and the lone `node203_mul.out`. The committed `co.tcl` assigns **DM1X to both** support groups, and the simulation reproduces `_mul` to 0.0001% on all DOFs — while `node203.out` row 1 is exactly 2× `_mul` row 1 yet finals differ 18× (not a uniform scale: genuinely different excitation). So `_mul` is the multi-support-pattern run matching the committed source; the other set belongs to an unidentified variant and is reported only as variant evidence (max diff 115 mm, expected). `ele330.out` pairs with that variant set (no `_mul` counterpart exists), hence no element-force validation claim.

## Output

Written to `output/`:
- `node203_disp_history.csv` — (t, UX, UY, UZ) per step
- `dynamic_compare.png` — node-203 UX history: simulation (red dashed) vs `node203_mul.out` (black solid)
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal, throttled every 2nd step)

**References:**

Original source: `ref/OPENSEES/co.tcl` (1362-line Tcl multi-support bridge model), `ref/OPENSEES/Model.s2k` (SAP2000 sibling), `ref/SAP2000/Model_V14.sdb` (commercial provenance). Reference results: `node203_mul.out` (primary — matches committed source), `node203.out` / `ele330.out` / `node0-2.out` (variant set), `result.xlsx`. Records: `ground_motions/dm1x.txt`, `dm2x.txt` (copied from `ref/OPENSEES/` per catalogue convention).

**Notes:** Converted from `ref/OPENSEES/co.tcl`. **`elasticBeamColumn` native 3D** `(A, E, G, J, Iy, Iz)`; **ShellMITC4 deck** `(tag, n1–n4, secTag)` on the `PlateFiber` section (§12as). **MultiSupport pattern** (§12p): `pattern("MultipleSupport")` → `groundMotion(tag, "Plain", "-disp", tsTag)` → `imposedMotion(node, dof, gmTag)`; numeric series tags throughout (§12r). **Committed source assigns DM1X to both groups** (factor 1) — replayed verbatim even though DM2X ships alongside. **Solver fidelity matters:** source `EnergyIncr 1e-4/200` passed to SmartAnalyze via `testType/testTol/testIterTimes` — defaults stall at step 1 (§12z-3 class). **No gravity/loadConst** (§12i N/A). **No MP constraints** beyond imposed supports (`puts "rigidDiaphragm"` label only) — `Transformation` as sourced. Source already N-mm-MPa (masses used directly; 6-value mass lines need no arity fix on ndf=6, cf. §12ba). **Path depth:** standards/ is `parents[3]` with `parents[2]` fallback. Run with: `uv run python "models/Dino/Multi-point Excitation Dynamics Analysis of Bridges/model.py"`
