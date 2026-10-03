# Dino_ViscousDamper

**Purpose:** Dynamic time-history of a 3D frame with viscous dampers (Dino). A 54-node model (105 `elasticBeamColumn` + 5 `nonlinearBeamColumn` damper columns whose fiber sections carry Maxwell dashpot fibers, 2% Rayleigh damping on modes 1–2) runs 20 s of ground motion (1000 steps × 0.02 s). Frame response validates against `ref/opensees/disp14.out`, `disp45.out`, `vel45.out` (see the damper note below for `ele110.out`).

**Building System:** 3D frame with viscous dampers — 54 nodes, 9 fixed base nodes. 105 `elasticBeamColumn` frame members (inline A/E/G/J/Iy/Iz) + 5 `nonlinearBeamColumn` damper columns (fiber section: 4 Maxwell fibers 0.01×0.01 area 1250, wrapped by a rigid-shear `section Aggregator`). Damper material: Maxwell (K=100000, C=3000, a=1, L=1 — stock OpenSeesPy, no custom build). Lumped mass on all 54 nodes. T1=0.312 s, T2=0.257 s.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). Eigen (2 modes) → Rayleigh 2% (`rayleigh alphaM betaKcurr 0 0`, computed from ω1/ω2 exactly as the source) → `UniformExcitation` (UX, `Path` series from `ground_motions/gm1x.txt`: 1501 points, dt=0.02 s, factor 5; first 20 s consumed) → transient Newmark(0.5, 0.25) via `opst.anlys.SmartAnalyze` (`transient_split` + per-step `TransientAnalyze`, `ok<0` break). No gravity phase in the source — direct transient from the zero state. `Transformation` constraints, `UmfPack` system, `EnergyIncr 1e-4/200` test tolerance (source-verbatim; SmartAnalyze defaults stall at step 1).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel + Maxwell dashpots (frame Elastic, damper Maxwell fibers) |
| Structural System | Frame with viscous dampers (105 elasticBeamColumn + 5 Maxwell-fiber columns) |
| Loading | Dynamic earthquake (UniformExcitation UX, 20 s) |
| Analysis Type | Transient — Newmark via SmartAnalyze |
| Earthquake Records | gm1x.txt (1501 pts, dt=0.02 s, factor 5) in `ground_motions/` |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Dynamic Analysis of a Frame with Viscous Dampers/model.py"
```

## Verification

Per-step histories (1000 rows) vs `ref/opensees/`: `disp14.out`/`disp45.out` (time + UX disp), `vel45.out` (time + UX vel). Reference layout is time + values (col 0 = time).

| Variant | Quantity | Result | Notes |
|---------|----------|--------|-------|
| `DAMPER_ACTIVE=False` (limp-damper diagnostic) | disp45 / vel45 / disp14 | 0.23% / 0.31% / 1.50% mean rel error | frame validated |
| `DAMPER_ACTIVE=True` (verbatim, default) | disp45 | strongly overdamped vs ref | see damper note |

## Damper note (open formulation question)

The verbatim Maxwell dampers engage ~81 kN axial (implied k ≈ 77 kN/mm, consistent with hand calc K·A/L) while the reference `ele110.out` shows ±3 N / ±1 N·m — effectively idle dampers. Evidence: (1) analytic Maxwell ODE at 3 Hz predicts ~50–80 kN for the observed ~1 mm damper stretch — the simulation is the physically consistent one for the committed constants; (2) a damper-free probe reproduces the reference peak to 6 digits (2.571949 vs 2.57) and its full history to 0.2–1.5%; (3) softening the dashpot (C 3000→30) changes nothing — the K-spring floor (~33 kN) always engages, so no (K, C) variant of the committed constants can reproduce an idle damper. Most plausible: **the reference outputs predate the damper activation** (a without-dampers comparison run filed alongside, mirroring the isolated-frame folder's `openseesWithoutRubberIsolator/` sibling pattern) — i.e. a §12aq-class reference-side variant, not a conversion error: the frame (stiffness/mass/damping/GM) is proven exact by the damper-free match. `DAMPER_ACTIVE = False` (near-zero-stiffness stand-in) reproduces the reference frame response for isolation purposes; default `True` stays source-faithful.

## Output

Written to `output/` (default verbatim run):
- `disp14_disp_history.csv`, `node45_history.csv` — per-step (t, UX[, vel])
- `dynamic_compare.png` — node-45 disp/vel: simulation (red dashed) vs reference (black solid)
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal, throttled every 2nd step)

**References:**

Original source: `ref/opensees/co.tcl` (410-line Tcl model), `ref/ETABS/` (commercial provenance). Reference results: `disp14.out`, `disp45.out`, `vel45.out` (1000-row UX histories), `ele110.out` (damper force — see note). Ground motion: `ground_motions/gm1x.txt` (copied from `ref/opensees/gm1x.txt`).

**Notes:** Converted from `ref/opensees/co.tcl`. **Damper architecture:** the 5 "columns" are pure-damper elements — fiber section holds *only* 4 Maxwell fibers, wrapped by `section Aggregator 1003` (rigid Vy/Vz/T); `nonlinearBeamColumn` keeps its native `(tag, i, j, nIP, secTag, transfTag)` form (§12l); `-GJ 1.0` negligible per §12ba (Aggregator-wrapped). **Maxwell 4-arg** `(K, C, a, L)` verified in stock OpenSeesPy. **Transient pattern:** Newmark set *before* SmartAnalyze; `transient_split(1000)` + `TransientAnalyze(dt)`, `ok<0` break; ODB every 2nd step (§3d); in-loop `nodeDisp` + `nodeVel` (velocity validation) + `eleResponse` every step. **Source test tolerance** (`EnergyIncr 1e-4/200`) passed explicitly — defaults stall at step 1 (§12z-3 class). **No gravity/loadConst** (§12i N/A). Source already N-mm-MPa. **Path depth:** standards/ is `parents[3]` with `parents[2]` fallback. Run with: `uv run python "models/Dino/Dynamic Analysis of a Frame with Viscous Dampers/model.py"`
