# Dino_LifeDeath

**Purpose:** Demonstrate the **element birth/death** (progressive element removal) technique on an elastic flat shell. A 6 m × 3 m ShellMITC4 slab carries a gravity load; after gravity is applied and frozen (`loadConst`), an 8-element rectangular "hole" (a mid-span patch) is removed group-by-group mid-analysis, driving load redistribution under the frozen gravity field. Orphan nodes left dangling by each removal are re-pinned to keep the global stiffness matrix non-singular. The model reproduces a demolition / progressive-collapse sequence.

**Building System:** Elastic flat shell (slab in the x-z plane, y=0) — 6000 mm × 3000 mm, meshed into **100 ShellMITC4** quadrilateral shell elements over a **121-node** refined grid (10 bays × 5 bays, with mid-edge and quarter-point refinement). Five support-line nodes along z=0 are fully fixed; all other nodes are rotation-only fixed (translations free) — the standard flat-shell drilling-restraint pattern. **Material:** ElasticIsotropic (E=2.482e4 MPa, ν=0.2) → PlateFiber nDMaterial → PlateFiber section (300 mm thick, "W300"). The removed patch (x∈[1.8,4.2] m, z∈[1.2,1.8] m) sits in the gravity load path between the loaded top edge and the z=0 supports.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). Two-phase static analysis: (1) **Gravity** — −9 MN total (−1e6 N × 9 top-edge nodes), LoadControl 0.1, 10 steps to λ=1.0, Plain constraints + BandGeneral + EnergyIncr 1e-6 + Newton; then `loadConst("-time", 0.0)`. (2) **Element death** — solver reconfigured to Transformation + RCM + SparseGeneral + NormDispIncr 1e-4 + KrylovNewton + LoadControl 1; then 8 stages of `ops.remove("ele", tag)` + `analyze(4)` each, with 3 orphan nodes (67, 81, 83) re-pinned (translations only) as their last connected element is removed. **ODB with `model_update=True`** (§12ax) — mandatory for mid-analysis element removal; re-queries the live element set each step. Node 88 (x=3.0 m, z=3.0 m, top of slab) is the validation node.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Elastic (ElasticIsotropic E=2.482e4 MPa, ν=0.2) |
| Structural System | Flat shell slab (100 ShellMITC4, PlateFiber section 300 mm) |
| Loading | Gravity (−9 MN) + progressive element removal (8 elements) |
| Analysis Type | Static — gravity (LoadControl) then element death (manual remove loop) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root
.venv/Scripts/python.exe "models/Dino/Application of Element Life and Death in Analysis/model.py"
```

## Verification

Node 88 UZ displacement (vertical) at every recorded step, compared against the source reference (`tcl_ref/node88.out`, 42 rows: col 0 = pseudo-time, col 3 = node-88 UZ).

| Quantity | Simulation | Reference (node88.out) | Notes |
|----------|-----------|----------------------|-------|
| Steps recorded | 42 / 42 | 42 | exact 1:1 (10 gravity + 32 death) |
| Post-gravity UZ (step 10) | −0.63423 mm | −0.63423 mm | 0.000% |
| Final UZ (step 42) | −1.28993 mm | −1.28993 mm | 0.000% |
| Per-point UZ RMS error | 9.6e-6 mm | — | ~1e-5 mm (floating-point noise) |
| Max per-step % diff | 0.0022% | — | at step 26 (e70 removal) |

The simulation reproduces the reference **exactly** to floating-point precision: every one of the 42 steps matches `node88.out` to within 0.002%, with an RMS UZ error of ~1e-5 mm on a curve ranging 0 to −1.29 mm. This near-exact match (expected for an elastic model with verbatim solver — cf. the §12aw softening case's 27.7% post-cracking divergence) confirms the element-death mechanics, the orphan-node re-pinning, and the `model_update=True` ODB capture are all correct. The characteristic "staircase" UZ-vs-step curve (linear gravity ramp, then 8 discrete jumps at each removal stage, with flat plateaus within each 4-step block) is reproduced exactly.

## Output

Written to `output/`:
- `node88_uz_history.csv` — (step, node-88 UZ [mm]) at each of the 42 recorded steps
- `node88_uz_compare.png` — simulation (red dashed) vs `node88.out` reference (black solid), with gravity/death boundary and each removal stage marked
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis, V5 final deformed, V6 step-slider, V7 animation showing the hole growing stage by stage)
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal + shell responses, `model_update=True` so the live element set varies per step)

**References:**

Original source: `tcl_ref/co.tcl` (454-line Tcl OpenSees script). Reference results: `tcl_ref/node88.out` (42-row node-88 displacement recorder), `tcl_ref/node0.out` (300-col, nodes 1–100), `tcl_ref/node1.out` (63-col, nodes 101–121), `tcl_ref/disp.xlsx` (node-88 disp vs time, redundant with node88.out).

**Notes:** Converted from `co.tcl`. **This is the repo's first element-birth/death model** (§12ax). Key conversion points: **(1) `ops.remove("ele", tag)`** — OpenSeesPy uses the abbreviated `'ele'` type string (the docs list `'ele'` as canonical; `'element'` also accepted in current builds but `'ele'` is portable). **(2) `CreateODB(model_update=True)` is mandatory** for mid-analysis element removal — with `False`, removed tags persist and per-step arrays misalign; with `True`, opstool re-queries the live model each step and concatenates with `xr.concat(join="outer")` so removed elements drop out of later steps. Tag filters (`node_tags`/`shell_tags`) must be omitted. **(3) SmartAnalyze has no element-death hooks** — the removal sequence is a manual `ops.analyze()` loop with `ops.remove`/`ops.fix` interleaved. **(4) Orphan-node re-pinning in OpenSeesPy** — the source's `fix 67 1 1 1 1 1 1` silently no-ops the already-fixed rotational DOFs; OpenSeesPy errors on the duplicate SP, so the re-pin is `fix(orphan, 1,1,1, 0,0,0)` (translations only; rotations already constrained). **(5) Initial-BC parse must exclude the death-phase re-pin lines** — the regex bounds `src` at the `"material"` marker or it double-matches `fix 67/81/83`. **(6) `node_tags` filter quirk** — with `model_update=True`, passing `node_tags=[88]` returned node 89; reading all nodes and selecting by coordinate is reliable. **(7) Empty `pattern Plain 2 Linear {}`** — the death phase adds no new load; the frozen gravity (via `loadConst`) drives the re-equilibration, and the empty pattern exists only so LoadControl has a time series to advance (matching the source's pseudo-time 2,3,…,33). **Dead materials/sections** (uniaxial Elastic mat 1 & 3, the 250 mm "SLAB1" section 702) defined in the source but referenced by no element are omitted (§12ap-6). **Path depth:** standards/ is `parents[3]` (deep nesting under `models/Dino/<analysis-name>/`), with a `parents[2]` fallback. Run with: `.venv/Scripts/python.exe "models/Dino/Application of Element Life and Death in Analysis/model.py"`
