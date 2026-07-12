# Dino_LowCycle

**Purpose:** Low-cycle reciprocating (cyclic) lateral analysis of a 3 m cantilever RC column whose section is an **irregular (re-entrant) arbitrary polygon** meshed with 894 concrete + 17 rebar fibres. A gravity axial load is applied first, then a 10-cycle DisplacementControl protocol drives the top-node UX to ±5, ±10, … ±25 mm, producing the base-shear-vs-drift hysteresis loop.

**Building System:** Cantilever reinforced-concrete column — 3000 mm tall, 5 `dispBeamColumn` elements (600 mm each), fixed at the base (node 1), free at the top (node 100, UY-only fixed). The cross-section is an irregular polygon (~1388 × 1320 mm bounding box) with re-entrant corners, a top-left appendage, and a mid-height notch — genuinely "arbitrary" (the source's `##DB500X500` comment notwithstanding; the mesh is far larger than 500×500). Concrete01 (fc=−26.8 MPa) core/cover + Steel01 (fy=400 MPa) rebar (17 Ø25 bars). Section Aggregator adds rigid shear (Vy, Vz) and torsion (T) DOFs to the fibre flexure.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6), 6 nodes, 5 `dispBeamColumn` elements with Lobatto beamIntegration (3 IP, aggregator section 1001). Section built by **verbatim replay** of the source's 911 fibres (`section_fiber.tcl`) — parsed at runtime and emitted via `ops.fiber(y, z, A, matTag)`. Two-phase static analysis: (1) **Gravity** — −19 125 kN axial (LoadControl, 10 steps to λ=1.0, manual loop per §3c exception), then `loadConst`; (2) **Lateral pattern defined after loadConst** (§12z-1) — unit reference 100 kN at node 100 UX; (3) **Cyclic** — 10 cycles × 100 steps, fixed DisplacementControl increments (±0.05, ±0.10, … ±0.50 mm/step → peaks ±5, ±5, ±10, ±10 … ±25, ±25 mm), driven by `opst.anlys.SmartAnalyze` (Static, NormDispIncr 1e-5, KrylovNewton + fallback ladder [40,10,20,30], relaxation=0.5, minStep=1e-3) with `static_split([cycle_delta], maxStep=|incr|)` for 1:1 step alignment with the 1000-row reference (§12am). Transformation constraints + BandGeneral + RCM. Base shear = lateral load-factor λ × 100 kN reference (source recorder convention).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC (Concrete01 fc=−26.8 MPa + Steel01 fy=400 MPa) |
| Lateral System | Cantilever column (5 dispBeamColumn, fibre section) |
| Section | Irregular polygon (894 concrete + 17 Ø25 rebar fibres) |
| Lateral Loading | 10-cycle DisplacementControl (±5 … ±25 mm, 1000 steps) |
| Earthquake Records | NA (quasi-static cyclic) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (opensy conda env, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
conda activate opensy
python "models/Dino/Low-cycle reciprocating analysis of members with arbitrary cross-sections/model.py"
```

Or directly:

```bash
C:/Users/micha/miniconda3/envs/opensy/python.exe "models/Dino/Low-cycle reciprocating analysis of members with arbitrary cross-sections/model.py"
```

## Verification

Cyclic hysteresis (base shear vs top UX displacement) compared against the source reference (`tcl_ref/node2.out`, 1000 rows: col 0 = lateral load-factor λ, col 1 = node-100 UX displacement). Because displacement is *imposed* (DisplacementControl), the match criterion is the base-shear (λ) column at the 1000 forced displacement points.

| Quantity | Simulation | Reference (node2.out) | Notes |
|----------|-----------|----------------------|-------|
| Steps converged | 1000 / 1000 | 1000 | exact 1:1 |
| Peak +shear | +1684.9 kN | +1684.9 kN | 0.0% |
| Peak −shear | −2026.4 kN | −2026.4 kN | 0.0% |
| Peak drift | ±25.01 mm | ±25.01 mm | matches protocol |
| Per-point shear RMS error | 2.44 kN | — | 0.12% of peak |
| Median per-point relative error | 0.000% | — | essentially exact |

The simulation reproduces the reference hysteresis essentially exactly: identical displacement range (−25.011..24.989 mm both), peak shears matching to 0.0%, and a per-point RMS shear error of 2.44 kN on a ±2026 kN curve (~0.12%). The 46 points with >1% relative error all lie near the zero-crossings where shear ≈ 0 (large relative error, tiny absolute error). This near-exact match confirms the verbatim-fibre-replay + fixed-increment SmartAnalyze approach is correct.

A secondary **P-M interaction surface** (`pmm_surface.png`) is rendered from the xlsx "PMM" sheet (62-point surface, P −3336..32941 kN, M ±4861 kN·m) for section-capacity context, with the gravity demand point (−19 125 kN) marked.

## Output

Written to `output/`:
- `hysteresis_curve.csv` — (base shear [kN], top UX [mm]) at each of the 1000 converged steps
- `hysteresis_compare.png` — simulation (red dashed) vs `node2.out` reference (black solid)
- `pmm_surface.png` — section P-M interaction surface from `section_analysis.xlsx` + gravity demand point
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis, V5 deformed peak, V6 slider, V7 animation)
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal responses)

**References:**

Original source: `tcl_ref/co.tcl` (103-line Tcl OpenSees main script) + `tcl_ref/section_fiber.tcl` (911-fibre section definition). Reference results: `tcl_ref/node2.out` (1000-row cyclic hysteresis recorder), `tcl_ref/section_analysis.xlsx` (sheets "Result" — 3 hysteresis datasets, the 3rd byte-identical to node2.out; "PMM" — 62-point P-M surface).

**Notes:** Converted from `co.tcl` + `section_fiber.tcl`. **Verbatim fibre replay:** the irregular (re-entrant) section is reconstructed by parsing the source's 911 fibres and emitting each via `ops.fiber()` — re-meshing risks both A/I drift (§12aq) and getting the re-entrant corners wrong. **3D Fibre section requires `-GJ`:** the source Tcl omits it (Tcl only warns); OpenSeesPy *errors* without it, so a principled GJ is computed from the concrete modulus and fibre polar inertia (the Aggregator's mat-401 torsion dominates regardless) — §12au. **dispBeamColumn via beamIntegration** (§12l): OpenSeesPy takes `(tag, i, j, transfTag, integTag)`, not the Tcl-style 6-arg `(tag, i, j, nIP, secTag, transfTag)`. **SmartAnalyze cyclic with 1:1 cadence** (§12am): `static_split([cycle_delta], maxStep=|incr|)` feeds each cycle's displacement *change* (not cumulative position) as one target, yielding exactly 100 segments/cycle = 1000 total while allowing adaptive sub-stepping. **loadConst ordering** (§12z-1): gravity pattern before `loadConst`, lateral pattern after. **Base shear = λ × P_LATERAL_REF** — the source `recorder Node -time` col 0 is the lateral pattern load-factor (not force), so base shear = λ × 100 kN (cross-ref §12ap-5). **xlsx read via stdlib** — `openpyxl`/`pandas.read_excel` unavailable in the env; the PMM sheet is read with `zipfile` + `ElementTree`. **Dead materials** (tag 2, `1.999e5` — defined but never referenced) kept for 1:1 source fidelity (harmless). **Path depth:** standards/ is `parents[3]` (this model nests under `models/Dino/<analysis-name>/`), with a `parents[2]` fallback. SmartAnalyze replaces the source's raw `ops.analyze(nstep)` + `ops.recorder`. Run with: `C:/Users/micha/miniconda3/envs/opensy/python.exe "models/Dino/Low-cycle reciprocating analysis of members with arbitrary cross-sections/model.py"`
