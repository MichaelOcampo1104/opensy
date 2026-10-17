# Dino_FrameWall

**Purpose:** Eigenvalue (39 modes) + gravity + displacement-controlled pushback analysis of a 3D frame shear-wall structure (Dino). A 956-node model (936 `dispBeamColumn` fiber elements + 364 `elasticBeamColumn`) is pushed 900 mm in UX at node 40 in 900 steps of 1 mm. Eigenvalues validate against `ref/Periods.txt`, the mode-1 shape against `eigen1_node.out`, and the node-40 history against `node40.out`.

**Building System:** 3D frame shear-wall structure — 956 nodes, 20 fully-fixed base nodes. **Members:** 936 `dispBeamColumn` fiber elements (4 sections: Steel01 fy=400 MPa + Concrete01 fpc=−23.4 MPa in fiber sections wrapped by rigid shear+torsion `section Aggregator`s, Lobatto 3 IP) + 364 `elasticBeamColumn` with inline A/E/G/J/Iy/Iz properties. Lumped mass on UX/UY at 436 nodes (eigen + nothing else — static pushback).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). **(1) Eigen** — 39 modes on the unloaded structure (source order: `set lambda [eigen 39]` right after model definition, before any loads). **(2) Gravity** — Plain pattern 1: 2912 `eleLoad -beamUniform` lines replayed verbatim including duplicates (additive); LoadControl 0.1 × 10 manual loop (§3c exception). **(3) Pushback** — Plain pattern 2 (defined after gravity): 52 UX nodal reference loads in a triangular-ish distribution (1.17e5 at the monitored floor → 4.17e3 at roof); `DisplacementControl` (node 40, DOF 1/UX) via `opst.anlys.SmartAnalyze`, one 1 mm increment per reference step (§12am cadence). **No `loadConst` exists in the source** — the gravity pattern stays live and scales with λ during the pushback (visible as the UZ snap-back at pushback step 1); replayed faithfully.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC + Steel (Steel01 + Concrete01 fiber, rigid-shear Aggregator; elastic members) |
| Structural System | Frame shear-wall (936 dispBeamColumn + 364 elasticBeamColumn, 956 nodes) |
| Loading | Gravity (beam UDLs) then UX pushback (1 mm × 900 steps = 900 mm) |
| Analysis Type | Eigen (39 modes) + Static gravity (LoadControl) + pushback (DisplacementControl) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
# NOTE: the 900-step pushback takes ~1.5 h (fiber state determination, ~5 s/step)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Push-back Analysis of a Frame Shear Wall Structure/model.py"
```

## Verification

Node-40 history (LF, UX, UY, UZ) at every recorded step vs `ref/node40.out` (911 rows: initial zero row + 10 gravity + 900 pushback; col 0 = load factor). Eigenvalues vs `ref/Periods.txt` (39 eigenvalues ω²); mode-1 UX shape (956 values) vs `ref/eigen1_node.out` (one long row: time + 956 values, sign-aligned before comparing).

| Quantity | Simulation | Reference | Notes |
|----------|-----------|-----------|-------|
| Steps recorded | 911 / 911 | 911 | exact 1:1 (1 + 10 + 900) |
| LF final | 1.72480 | 1.72480 | 0.0002% |
| UX final | 899.93463 mm | 899.935 mm | 0.0001% (imposed 1 mm/step) |
| UY / UZ final | −0.04224 / 7.18155 mm | identical | ≤0.0012% |
| Eigenvalues (39) | RMS 0.00016 | Periods.txt | mean rel error 0.0000% |
| Mode-1 shape (956) | RMS 0.000000 | eigen1_node.out | rel 0.0002% |

## Output

Written to `output/`:
- `node40_disp_history.csv` — (idx, LF, UX, UY, UZ) at each of the 911 recorded steps
- `pushback_compare.png` — capacity (UX vs LF) + LF history: simulation (red dashed) vs `node40.out` reference (black solid)
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis, V5 final deformed UX, V6 step-slider, V7 animation)
- `RespStepData-1.odb/`, `ModelData-1.zarr/`, `EigenData-1.zarr/` — ODB response + eigen database

**References:**

Original source: `ref/co.tcl` (7239-line Tcl frame-wall model), `ref/model.s2k` (SAP2000 sibling). Reference results: `ref/node40.out` (911-row node-40 recorder), `ref/Periods.txt` (39 eigenvalues), `ref/eigen1_node.out` (mode-1 shape, 956 values).

**Notes:** Converted from `co.tcl`. **Verbatim fiber replay** (§12aq): four fiber sections re-emitted via `ops.fiber(y, z, area, mat)` (§12ay area-is-THIRD), each wrapped by a `section Aggregator` (1001–1004). **`dispBeamColumn` via shared `beamIntegration("Lobatto", ...)`** per section (§12l); **`elasticBeamColumn` keeps its native 3D form** `(tag, i, j, A, E, G, J, Iy, Iz, transf)`. **`-GJ` = 1.0 (negligible) by design:** the Aggregator's rigid T material already supplies torsion and *adds* the fiber GJ in parallel — a physical G·Σ(A·r²) stiffened torsion-sensitive modes by up to 31% (mode 2: +31%); GJ=1.0 matches all 39 eigenvalues to 0.0000% (Tcl's missing torsion behaves as ~zero). **No `loadConst`:** gravity stays live into the pushback (faithful — UZ snap-back at step 11 proves it); pushback pattern defined after gravity. **ODB:** nodal-only + throttled (`ODB_EVERY_N=10`, ~100 fetches; in-loop `nodeDisp` every step for the exact history). **Solver:** manual LoadControl loop for gravity (§3c exception); SmartAnalyze (NormDispIncr 1e-5, KrylovNewton primary) for the pushback — one hard step (~401) cost ~15 min of fallback retries, total runtime ~1.5 h. **Eigen solver:** default (rank-deficient mass tolerated here; −fullGenLapack fallback coded per §12al). **Source quirks:** `fix` lines carry trailing `;` (regex tolerates); `puts "rigidDiaphragm"` label with no MP commands → `constraints("Plain")`. Source already N-mm-MPa. **Path depth:** standards/ is `parents[3]` with `parents[2]` fallback. Run with: `uv run python "models/Dino/Push-back Analysis of a Frame Shear Wall Structure/model.py"`
