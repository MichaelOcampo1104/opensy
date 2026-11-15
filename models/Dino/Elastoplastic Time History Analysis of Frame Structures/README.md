# Dino_FrameTH

**Purpose:** Gravity + X-direction seismic transient of a 6-storey RC frame (Dino Exam07). A 63-node, 126-element `forceBeamColumn` frame (Steel01 + Concrete02 column/beam fibre sections in shear+torsion Aggregators) carries beam-UDL gravity, then runs a 5%-damped Newmark transient (3000 × 0.005 s = 15 s) under GM1X × 0.6072. Validated at three shaking levels from `ref/OPENSEES/result_all.xlsx` (factors 0.13803 / 0.27606 / 0.6072): full-history match at small/moderate levels; large-level match through first deep yield, then version drift (see Verification).

**Building System:** 6-storey 3-bay × 2-bay RC moment frame (9 m × 7 m plan, 3–3.5 m storeys, 18.5 m roof), fixed base (nodes 37–45). Columns NC400X400 (section 1001: all-Steel01 fibres in the source — the 25 "concrete" grid fibres carry mat tag 1, replayed verbatim), beams NB200X500 (section 1002: Concrete02 + Steel01 rebar). 63 nodes, **126 `forceBeamColumn`** elements (Lobatto, 3 IP; `Linear` transforms). **Material:** Steel01 rebar (fy=400 MPa, E=2.06e5, b=0.01) + Concrete02 (−26.8/−0.0015/−10/−0.0033/0.1/2.2/1100) in rigid shear+torsion `section Aggregator`s. 3-component lumped mass (active in transient), 5% Rayleigh damping on modes 1–2 (T1 = 0.538 s).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). DEAD pattern: 456 beamUniform eleLoad lines replayed verbatim (duplicates accumulate as in Tcl); `LoadControl` 0.1 × 10 (manual loop, AGENT §3c exception) → LF 1.0, then `loadConst` + `wipeAnalysis`. UniformExcitation dir-1 from `ground_motions/GM1X.txt` (byte-identical copy of the ref, 2048 pts @ 0.02 s); Newmark 0.5/0.25 transient via `opst.anlys.SmartAnalyze` (plain Newton, flag 10). In-loop per-step history (time, node-59 UX) + base-column localForce (eles 106–114); ODB fetch every 6th step (~500 fetches).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC (Steel01 fy=400 MPa + Concrete02, fiber + rigid-shear Aggregator) |
| Structural System | 6-storey RC frame (126 forceBeamColumn, 2 fiber sections) |
| Loading | Beam-UDL gravity + X GM transient (3000 × 0.005 s), 3 levels |
| Analysis Type | Static LoadControl gravity + Transient Newmark via SmartAnalyze |
| Earthquake Records | GM1X.txt (×0.13803 / ×0.27606 / ×0.6072) in `ground_motions/` |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26, xlrd 2.0.2) |
| Units | N, mm, MPa (time in seconds) |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
chcp 65001; $env:PYTHONUTF8="utf-8"; uv run python "models/Dino/Elastoplastic Time History Analysis of Frame Structures/model.py"
# other shaking levels via the env-only driver (not part of the repo):
# python run_levels.py <gm_factor> <outdir> [testTol]
```

## Verification

Node-59 UX history (time + UX, 3010 rows incl. 10 gravity rows) against `ref/OPENSEES/node59.out` (= 大震 sheet, row-identical) and `result_all.xlsx` 小震/中震 sheets; base shear (Σ column Vz, flips [2,8]) and N/My against `shear.out`.

| Level | Steps | UX match | Base-force match | Notes |
|-------|-------|----------|-----------------|-------|
| Gravity | 10 / 10 | LF 5.0→1.0 exact; UX −0.01693 vs −0.01687 | N exact; Vy/Vz/My ≈ static | eleLoad accumulation correct |
| 小震 (×0.13803) | 3010 / 3010 | mean 1.15%, abs < 0.12 mm; peak 16.71 vs 16.72 | — | factor from elastic-shear ratio |
| 中震 (×0.27606) | 3010 / 3010 | mean 1.7%; peak 48.37 vs 48.19 (+0.4%) | — | zero solver failures |
| 大震 (×0.6072) | 1752 / 3010 | in-plane N/Vz/My ~1% through t≈4 s (800 steps) | ΣVz peak +2.2% | diverges ~t=4 s, Newton dies t=8.7 s |

小震/中震 validate the full chain (mass, stiffness, damping, GM input, UDL state) to ~1–2% / sub-mm. 大震 matches through first deep yield (UX err <3% to step 800, in-plane base forces ~1%), then the path diverges and Newton cannot proceed under current OpenSeesPy despite exhausting solver (Newton/Krylov/BFGS/ModifiedNewton), test (0.1/1e-6 identical paths), system (BandGeneral/UmfPack) and substepping variants. Residual 小震/中震 drift (~1%) and the 大震 break are attributed to formulation drift in deep-plastic forceBeamColumn/Concrete02 response since 2012 (mild regimes are version-robust; the elastic ReticulatedShell matched bit-exactly). Out-of-plane residue (Vy/Mz/T, ~1% of in-plane) differs by version as expected for near-zero quantities.

## Output

Written to `output/` (canonical 大震 run; level runs to `output_xiao*/output_zhong`, git-ignored):
- `transient_history.npz` — `hist` (2, N) [time, node59-UX], `ref` node59.out, `shear_t`/`shear_f` (M,9,12) base-column localForce, `ref_shear` shear.out
- `vis_01_nodes.html` … `vis_06_slider.html` — opstool visualisations
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database

**References:**

Original source: `ref/OPENSEES/EXAM7.tcl` (1004-line Tcl force-element frame). Reference results: `ref/OPENSEES/node59.out` (3010-row roof recorder), `node0.out` (all-node), `shear.out` (base columns 106–114), `result_all.xlsx` (小/中/大 base-shear + displacement sheets + 汇总； 大震 col B ≡ node59.out), `etabs_top_disp.txt` (ETABS elastic 小震 check, ~10× smaller than 大震 — not comparable). ETABS source model: `ref/ETABS/EXAM7.EDB` (+ `.e2k`).

**Notes:** Converted from `EXAM7.tcl`. **Verbatim replay:** 63 nodes + 3-comp masses, 9 fixed supports, 126 `Linear` transforms, 456 eleLoad lines, both fibre sections (mix asserted: sec1 all-Steel01! sec2 25×Concrete02 + 10×Steel01) + Aggregators via shared Lobatto rules (§12l). **`nonlinearBeamColumn` = `forceBeamColumn`** (legacy force-based name; a dispBeamColumn trial was 8× worse). Dead Elastic mat 3 kept (§12ap-6). **`-GJ` = 1.0 both sections** (LESSONS 11). **Solver:** `algoTypes=[10]` plain Newton (LESSONS 14), `system UmfPack` + `numberer RCM` mirror source, `testTol` = source 0.1 (tight 1e-6 gives the identical path here at 30× cost — LESSONS 15 n/a to this transient). `wipeAnalysis()` after `loadConst` so Newmark sets without warnings. **Shear sign rule is orientation-dependent** (refines LESSONS 1): these vertical columns need flips [2,8] (Vz), not [1,2,7,8] — resolved from the quasi-static first row. **Path depth:** standards/ is `parents[3]` with fallback. GM factors 小/中 derived from elastic-shear ratios (455:910:2002 → 0.13803/0.27606/0.6072 ≈ 50/100/220 gal).
