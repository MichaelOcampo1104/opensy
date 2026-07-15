# Dino_PseudoCollapse

**Purpose:** Gravity + force-controlled **pushdown** of a 3D RC moment frame (OpenSees Example 2.9 — "pseudo-collapse" test). A 3-bay × 3-bay × 4-storey RC frame (44 nodes, 83 `nonlinearBeamColumn` elements, two Steel01/Concrete02 fiber sections) is first loaded under gravity (node 35 pulled up 300 kN + beam UDLs), then node 35 is pushed down 300 kN. Because phase 2 starts from the frozen gravity state, the two load signs do not cancel: UZ grows monotonically to ~−17 mm — the pseudo-collapse displacement demand. Node-35 displacement history is validated against `tcl_ref/node35.out`.

**Building System:** Three-dimensional RC moment-resisting frame — 3 bays × 3 bays in plan (6 m bays) × 4 storeys (3 m storey height). 44 nodes, **83 `nonlinearBeamColumn`** elements: 21 columns (NC500×500, section 1001) + 62 beams (NB300×600, section 1002). Base nodes 37–44 pinned (translations fixed, rotations free). **Material:** Steel01 (fy=300, E=206000, b=0.01) rebar + Concrete02 (fpc=−20, epsc0=−0.002, fpcu=−5, epsU=−0.0033, λ=0.1, ft=2.2, Ets=1100) concrete, in fiber sections wrapped by rigid shear+torsion `section Aggregator`s. Lumped mass on UX/UY at the upper nodes.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). Two-phase force-controlled static analysis: **(1) Gravity** — Plain pattern 1 applies +3e5 N UZ at node 35 plus 128 `eleLoad -beamUniform 0 -6.375 0` lines (replayed verbatim, including duplicates); LoadControl 0.1, 10 steps to λ=1.0 (Plain constraints + Plain numberer + BandGeneral + EnergyIncr 1e-6/200 + Newton); then `loadConst("-time", 0.0)`. **(2) Pushdown** — Plain pattern 2 (defined *after* `loadConst`, §12z-1) applies −3e5 N UZ at node 35; LoadControl 0.01, 100 steps to λ=1.0. Both phases are manual `ops.analyze()` loops (§3c permitted exception — SmartAnalyze forces DisplacementControl). Node 35 (coords (0,0,3000) mm, a ground corner) is the validation node.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC (fiber-section: Steel01 + Concrete02, rigid-shear Aggregator) |
| Structural System | 3D moment frame (83 nonlinearBeamColumn, 2 fiber sections) |
| Loading | Gravity (+300 kN uplift + beam UDLs) then pushdown (−300 kN) |
| Analysis Type | Static — gravity (LoadControl) then pushdown (LoadControl) |
| Earthquake Records | NA (static pushdown) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root
uv run python "models/Dino/Analysis of a Pseudo-Collapse Test on a Frame Structure/model.py"
```

## Verification

Node 35 displacement (UX, UY, UZ) at every recorded step, compared against the source reference (`tcl_ref/node35.out`, 110 rows: col 0 = pseudo-time, cols 1–3 = node-35 UX/UY/UZ).

| Quantity | Simulation | Reference (node35.out) | Notes |
|----------|-----------|----------------------|-------|
| Steps recorded | 110 / 110 | 110 | exact 1:1 (10 gravity + 100 pushdown) |
| UX post-gravity (step 10) | −0.18570 mm | −0.18577 mm | 0.038% |
| UX final (step 110) | −0.82677 mm | −0.82907 mm | 0.278% |
| UY post-gravity (step 10) | −0.18570 mm | −0.18577 mm | 0.038% |
| UY final (step 110) | −0.82677 mm | −0.82907 mm | 0.278% |
| UZ post-gravity (step 10) | −0.23656 mm | −0.23601 mm | 0.233% |
| UZ final (step 110) | −16.92740 mm | −16.88830 mm | 0.232% |
| UX per-point mean rel error | — | — | 0.2667% |
| UY per-point mean rel error | — | — | 0.2667% |
| UZ per-point mean rel error | — | — | 0.1917% |

All three DOFs match the reference to **≤0.27% mean relative error** across the full 110-step history — an excellent agreement for a nonlinear fiber-section frame, confirming the verbatim fiber replay, the rigid-shear Aggregator, the `loadConst` two-phase split, and the verbatim force-controlled solver are all correct. The slight residual (~0.2%) comes from the OpenSeesPy-only `-GJ` term added to the bare fiber sections (the Tcl source omits it — §12au); it is dominated by the Aggregator's rigid torsion code and has negligible structural effect.

## Output

Written to `output/`:
- `node35_disp_history.csv` — (step, UX, UY, UZ [mm]) at each of the 110 recorded steps
- `pushdown_compare.png` — node-35 UZ: simulation (red dashed) vs `node35.out` reference (black solid), with the gravity/pushdown boundary marked
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis, V5 final deformed UZ, V6 step-slider, V7 animation)
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal responses)

**References:**

Original source: `tcl_ref/co.tcl` (532-line Tcl OpenSees script; `tcl_ref/EXAM29.tcl` is a byte-identical copy — OpenSees Example 2.9). Reference results: `tcl_ref/node35.out` (110-row node-35 displacement recorder: time, UX, UY, UZ), `tcl_ref/node0.out` (110-row × 120-col recorder of all nodes, full-field).

**Notes:** Converted from `co.tcl`. **Verbatim fiber replay** (§12aq): the two fiber sections (NC500×500: 25 concrete @ 1e4 + 16 steel @ 314; NB300×600: 25 concrete @ 7200 + 6 steel @ 314) are parsed from the source `fiber` commands and re-emitted via `ops.fiber(y, z, area, mat)`, preserving exact centroids/areas (re-meshing risks A/I drift and breaks the displacement match). Each is wrapped by a `section Aggregator` (1001/1002) adding rigid Vy/Vz/T codes. **`nonlinearBeamColumn` retains its native signature** `(tag, i, j, nIP=3, secTag, transfTag)` — NOT converted to dispBeamColumn (§12l). **`-GJ` required** (§12au): OpenSeesPy 3D `section Fiber` errors without it (Tcl only warns); computed per-section as G_steel·Σ(A·r²), dominated by the Aggregator's rigid torsion regardless. **`save_frame_resp=False`** in CreateODB — nonlinearBeamColumn internal sections lack user-visible tags (§12v). **Dead material** (uniaxial Elastic mat 3, never referenced) omitted (§12ap-6). **Two LoadControl phases** → manual `ops.analyze()` loops (§3c exception); lateral/pushdown pattern defined after `loadConst` (§12z-1). The 128 `eleLoad` lines (most beams written 2–4×) are replayed verbatim so the total load matches. **Path depth:** standards/ is `parents[3]` (nests under `models/Dino/<analysis-name>/`) with `parents[2]` fallback. Run with: `uv run python "models/Dino/Analysis of a Pseudo-Collapse Test on a Frame Structure/model.py"`
