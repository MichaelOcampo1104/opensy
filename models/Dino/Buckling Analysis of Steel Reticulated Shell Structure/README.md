# Dino_ReticulatedShell

**Purpose:** Elastic snap-through buckling of a 3D single-layer steel reticulated shell (Dino Exam09). A 67-node, 72-element `dispBeamColumn` dome (elastic DH200X200X12X12 fiber section in a shear+torsion Aggregator) is pushed down 1000 mm at crown node 7 in 200 steps of −5 mm under a −1000 N reference load. Crown load-factor history is validated against `ref/OPENSEES/node7.out` — exact match at every step.

**Building System:** Single-layer reticulated (lattice) shell — hexagonal plan (~9.6 m span, 0.5 m rise), 6 radial ribs × 5 rings (36 shell members, `Corotational` with per-member vecxz) plus a ground-level perimeter ring beam (36 members, 30 free ring nodes + 6 pinned supports 1–6 fixed UX/UY/UZ). 67 nodes, **72 `dispBeamColumn`** elements (Lobatto, 3 IP). **Material:** Elastic steel (E=2.06e5 MPa) fibers — 24 flange × 200 mm² + 12 web × 176 mm² (A=6912 mm²) — wrapped by a rigid shear+torsion `section Aggregator` (Vy 1.585e8 N, Vz 3.169e8 N, T 2.738e10 N·mm²). Lumped mass on UX/UY (static buckling — mass is inactive).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). Single Plain pattern applies the −1000 N UZ reference load at crown node 7; `DisplacementControl` (node 7, DOF 3/UZ) via `opst.anlys.SmartAnalyze`, one −5 mm increment per reference step (`static_split([incr], maxStep=|incr|)`, §12am cadence) for 1:1 alignment with the 200-row reference. No gravity phase, no `loadConst` — the single pattern stays active throughout.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (Elastic E=2.06e5 MPa, fiber + rigid-shear Aggregator) |
| Structural System | Single-layer steel reticulated shell (72 dispBeamColumn, 1 fiber section) |
| Loading | Displacement-controlled UZ pushdown (−5 mm × 200 steps = −1000 mm) |
| Analysis Type | Static — DisplacementControl via SmartAnalyze (snap-through buckling) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
chcp 65001; $env:PYTHONUTF8="utf-8"; uv run python "models/Dino/Buckling Analysis of Steel Reticulated Shell Structure/model.py"
```

## Verification

Crown node-7 history (LF, UX, UY, UZ) at every recorded step, compared against the source reference (`ref/OPENSEES/node7.out`, 200 rows: col 0 = load factor/time, cols 1–3 = crown UX/UY/UZ). `ref/OPENSEES/result.xlsx` (Sheet1) mirrors the same data plus the displacement-magnitude column.

| Quantity | Simulation | Reference (node7.out) | Notes |
|----------|-----------|----------------------|-------|
| Steps recorded | 200 / 200 | 200 | exact 1:1 |
| LF peak (step 35) | 1966.81 | 1966.81 | snap-through critical load, exact |
| LF post-buckling valley (step 129) | 425.35 | 425.35 | @ UZ −645 mm, exact |
| LF final (step 200) | 4967.45 | 4967.45 | membrane re-stiffening, exact |
| LF per-point | max rel err 0.0000 | — | **bit-exact at all 200 steps** |
| UZ final | −1000.00000 mm | −1000.00000 mm | imposed, exact |

Snap-through signature reproduced exactly: linear rise → peak 1967 @ −175 mm → unloading to valley 425 @ −645 mm → tensile-membrane re-hardening to 4967 @ −1000 mm.

## Output

Written to `output/`:
- `crown_history.npz` — `hist` (4, 200) sim [LF, UX, UY, UZ] + `ref` (4, 200) reference arrays
- `vis_01_nodes.html` … `vis_06_slider.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis, V5 deformed, V6 step-slider)
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal responses)

**References:**

Original source: `ref/OPENSEES/co.tcl` (357-line Tcl dispBeamColumn shell model, converted from ETABS `EXAM09.EDB` via `EXAM09.e2k`/`EXAM09.s2k`). Reference results: `ref/OPENSEES/node7.out` (200-row crown recorder), `ref/OPENSEES/node0.out` (all-node recorder), `ref/OPENSEES/result.xlsx` (Sheet1 = node7.out + magnitude column).

**Notes:** Converted from `co.tcl`. **Verbatim replay:** all 67 nodes + masses, 6 pinned supports, 72 `Corotational` transforms (rib vecxz ≈ (±0.052, ∓0.09, 0.995), ring beams (0,0,1)), 72 `dispBeamColumn` elements and the 36-fiber DH200X200X12X12 section are parsed from the source and re-emitted exactly. **`dispBeamColumn` via shared `beamIntegration("Lobatto", 1001, 1001, 3)`** (§12l). **Dead materials kept:** Elastic mats 2 (2.482e4) and 3 (1.999e5) are defined but referenced by no fiber — tag fidelity (§12ap-6). **`-GJ` = 1.0 (NOT §12au):** the Tcl source omits `-GJ`, so the fiber section carries no torsion and the Aggregator's T (2.738e10) governs alone. The §12au G·Σ(A·r²) recipe gives 5.05e12 N·mm² (184× the Aggregator T) and over-stiffens the post-buckling branch by ~6.5% (valley 453 vs 425, final 5287 vs 4967, peak still 1970 vs 1967); with `-GJ 1.0` the run is bit-exact at all 200 steps. **`save_frame_resp=False`** in CreateODB (§12v). **Source quirks:** `fix` lines carry trailing `;` (regex tolerates); `puts "rigidDiaphragm"` prints a label with no MP-constraint command, so `constraints("Plain")` throughout; test mirrored from source (`EnergyIncr 1e-6`, 200 iter) with algo fallback [40, 10, 20, 30, 50, 60]. Source already N-mm-MPa (masses used directly, no conversion). **Path depth:** standards/ is `parents[3]` (nests under `models/Dino/<analysis-name>/`) with `parents[2]` fallback.
