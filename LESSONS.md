# Lessons Learnt — Dino conversion sessions

Running record of non-obvious findings from converting Dino Tcl references to
the opensy standard. Each entry states the evidence so it can be re-checked.

## 2026-10-07 — HingedLinks / ElasticShell / SeamConnection / SinglePressure

### 1. Tcl recorder `localForce` vs Py `eleResponse("localForce")`: shear sign flips
- Evidence: `Dino_HingedLinks` (EXAM12) — axial/torsion/moments ratio +1.000,
  Vy/Vz ratio −1.000 across all 36 `dispBeamColumn`s; displacements exact.
- Rule: assert signs per component against the reference; flip sim shears
  (idx 1,2,7,8) before diffing and document it. Never assume sign conventions.

### 2. `dispBeamColumn` needs explicit `beamIntegration` in Py
- Tcl `element dispBeamColumn tag i j nIP secTag transfTag` becomes
  `beamIntegration("Lobatto", integTag, secTag, nIP)` +
  `element("dispBeamColumn", tag, i, j, transfTag, integTag)`.
  Passing nIP inline raises `BeamIntegrationRule - none found`.
- Rule: one Lobatto object per section; transfTag == eleTag preserved.

### 3. 3D `section Fiber` requires `-GJ` in Py (Tcl defaulted it)
- Evidence: `ops.section("Fiber", 1)` alone raises `torsion not specified`.
- Rule: supply open-section `GJ = G·Σ(bt³)/3`; exact value is immaterial when
  torsion is inactive — note the estimate in the README.

### 4. Source recorder files can be corrupt — check before trusting
- Evidence: SeamConnection `ele33axialForce.out` is byte-identical to the
  pseudo-time column (stray control byte in the Tcl recorder line);
  `ele33deformation.out` is 0 bytes.
- Rule: diff every ref file against siblings (time columns!) before choosing
  anchors. Corrupt → nodes authoritative, sim-only reporting + README note.

### 5. Bare `loadConst 0` is version-specific bookkeeping, not physics
- Evidence: SinglePressure `co.tcl` line `loadConst 0` (missing `-time`).
  Standard `loadConst("-time", 0.0)` reproduces every displacement (24×3×200)
  and every hanger force (11×200) to ≤0.0001%, but phase-2 pseudo-time
  diverges. No-op and bare-`loadConst()` variants reproduce at most the first
  phase-2 step.
- Rule: keep the standard call; validate physics, report time split-by-phase,
  document the `loadConst 0` root cause. Time is bookkeeping.

### 6. `ENT` (compression-only) works in Py with Tcl-identical args
- Evidence: `uniaxialMaterial("ENT", 1, E)` parents hanger trusses;
  SinglePressure hangers start ≈ −800 N and go slack (0 N) in the lateral tail.
- Rule: query truss force via `eleResponse(tag, "axialForce")[0]` — note [0].

### 7. `float()` on a 1-list throws — index `eleResponse` results
- Evidence: `float(ops.eleResponse(33, "axialForce"))` → TypeError → silent NaN
  fallback hid it; `float(...[0])` fixed it (SeamConnection, SinglePressure).
- Rule: always index/single-unpack element responses; treat unexpected NaN as
  a query bug, not a model result.

### 8. Count assertions catch transcription errors immediately
- Evidence: `N_FIX = 11` failed — source has 12 fix lines (node 3 + 11 bases).
- Rule: keep `assert n == N_*` after every regex-replay loop.

### 9. Catalogue dumps must preserve `\uXXXX` escaping
- Evidence: `json.dump(..., ensure_ascii=False)` rewrote ~120 lines of
  `opensees_catalogue.json`; default `ensure_ascii=True` keeps the diff a pure
  append (+21/−0).
- Rule: dump with `indent=2` and default ascii; verify diff is additions-only.

### 10. Ramp single-step linear cases for the slider without changing results
- Evidence: ElasticShell `analyze 1` → 100× `LoadControl 0.01`; final state
  identical (linear), `vis_06_slider.html` now shows the deflection evolving.
- Rule: free visualisation win for linear statics; note the ramp in README.

## 2026-10-08 — ReticulatedShell (Exam09 snap-through buckling)

### 11. Tcl-omitted `-GJ` + Aggregator T ⇒ fiber `-GJ 1.0`, NOT G·Σ(A·r²)
- Evidence: `Dino_ReticulatedShell` — Tcl `section Fiber 1 {...}` omits `-GJ`,
  torsion governed solely by Aggregator T (2.738e10 N·mm²). Py `-GJ 1.0`
  reproduces `node7.out` bit-exactly at all 200 steps (peak 1966.81, valley
  425.35, final 4967.45). The §12au-style polar recipe G·Σ(A·r²) = 5.05e12
  (184× the Aggregator T) over-stiffened the post-buckling branch by ~6.5%
  (valley 453 vs 425, final 5287 vs 4967) while the pre-buckling peak still
  matched (1970 vs 1967) — torsion only bites after snap-through.
- Rule: when the source omits `-GJ` and an Aggregator supplies `T`, pass a
  negligible `-GJ` (1.0) so the Aggregator governs alone. Reserve computed GJ
  for bare fiber sections with genuinely active torsion. Refines item 3.

### 12. Snap-through valleys are post-peak minima, not global minima
- Evidence: Exam09 load factor starts at 105.9 (step 1), peaks at 1966.8,
  unloads to 425.4 — `argmin` over the full history returns step 1.
- Rule: locate the valley as `argmin` over `ref[peak:]`; report peak / valley
  / final checkpoints for buckling runs.

### 13. Tolerance mirroring is not always the discrepancy driver
- Evidence: switching SmartAnalyze `NormDispIncr 1e-8` → source-mirrored
  `EnergyIncr 1e-6 / 200 iter` changed Exam09 results not at all (identical
  LF to 2 dp) — the 6.5% gap was entirely the GJ formulation (item 11).
- Rule: when a gap survives tolerance mirroring, suspect formulation
  (section/transformation defaults), not convergence.

## 2026-10-08 — LowCycleSteel (Exam08 4000-step reciprocation)

### 14. SmartAnalyze flag 40 is KrylovNewton, NOT Newton (10 = plain Newton)
- Evidence: Exam08 `.SmartAnalyze-OpenSees.log` shows
  `AcceleratedNewton::solveCurrentStep()` with default `algoTypes=[40, …]`;
  `_setAlgorithm` map: 10 = `("Newton",)`, 40 = `("KrylovNewton",)`.
  KrylovNewton exploded at steps 532/1015 (Norm 1e4 vs tol 0.1) where plain
  Newton (flag 10) passes — all prior Dino models ran KrylovNewton
  unknowingly (harmless there: elastic or mild plasticity).
- Rule: when the source says `algorithm Newton`, pass `algoTypes=[10]`.
  Read the flag map, never assume 40 == Newton.

### 15. Loose test tolerance fabricates softening — tighten to find the truth
- Evidence: `Dino_LowCycleSteel` (Steel01+b=0.001, Linear geometry — no
  softening mechanism exists): source-mirrored `NormDispIncr 0.1` produced a
  virgin peak 6637 @ UX~50 then spurious softening to 6253 (xls block A,
  "degrading" to 5900 by phase 4). Tight `1e-6` recovered the TRUE hardening
  curve = xls block B, bit-exact at all 4010 steps (mean rel err 1e-6;
  peaks 6706.9/-6727.2/6755.4/-6779.0). Block A is a loose-tol artifact.
- Rule: when a hardening-material + Linear-geometry model softens, suspect
  the TEST first, not the physics. Run tight; if tight == a reference block
  and loose == another, the loose block is the artifact — anchor the tight
  one and document the deviation from the source tolerance.

### 16. Solver-switch rescues branch-jump — validate per-step, don't assume
- Evidence: Exam08 reversal deaths retried with ModifiedNewton/KrylovNewton/
  BFGS then Newton restored: run "completed" but UX err 0.13 mm, LF err up
  to 861x — rescued steps jumped equilibrium branches and poisoned the rest
  of the path. Unrecorded bisection (down to seg/16) stalled identically.
- Rule: a rescue that changes the solver (or step) invalidates the whole
  downstream path. Any rescue experiment must be followed by full-length
  per-step validation; on mismatch, discard the rescue, don't keep it.

### 17. Linear-solver roundoff decides knife-edge Newton convergence
- Evidence: Exam08 step 532 (virgin capacity, UX~53) failed Newton with
  `BandGeneral`, passed with source-mirrored `UmfPack` — all else equal.
- Rule: mirror the source `system` (UmfPack/RCM here) before blaming the
  model; roundoff-level differences are decisive at limit points.

### 18. Legacy `.xls` references need xlrd (installed to `.venv`, env-only)
- Evidence: Exam08 `result.xls` (BIFF8, 4010×9: cols A–D vs F–I two-run
  comparison) unreadable by openpyxl; `uv pip install --python .venv/... xlrd`
  (pure-python, git-ignored env) reads it. Dual-block sheets: validate
  against EACH block separately and anchor explicitly (here: right block).
- Rule: never assume which block/sheet is authoritative — let the
  verification decide, and name the anchor (cols F–I) in README + header.

## 2026-10-08 — FrameTH (Exam07 GM transient)

### 19. `nonlinearBeamColumn` IS `forceBeamColumn` (prove it, don't assume it)
- Evidence: `Dino_FrameTH` — Tcl `nonlinearBeamColumn` replayed as
  `forceBeamColumn` matches node59 to ~1% pre-yield; a `dispBeamColumn`
  trial was 8x worse (mean 28% vs 1.3%, UXmax 27 vs 40 mm — disp locks).
- Rule: legacy name = force-based element. Run the disp-counterfactual
  once when the mapping is uncertain; keep the result in the README.

### 20. Recorder/eleResponse shear signs are ORIENTATION-dependent (refines 1)
- Evidence: Exam07 base columns (vertical, vecxz 0,0,1): Py `eleResponse`
  Vz (idx 2,8) is the negative of the Tcl `localForce` recorder, Vy/M/N
  agree — flips [2,8], NOT item-1's [1,2,7,8]. Totals prove it:
  ΣVz raw = −ref (554k vs 554k mirrored); flipped ΣVz peak +2.2%.
- Rule: resolve the flip set empirically per orientation from a static row
  (gravity/first-step), then apply globally. Never port a flip set across
  orientations. In-plane N/Vz/My then matched to ~1% (means).

### 21. `wipeAnalysis()` after `loadConst` so Newmark sets cleanly
- Evidence: without it, `ops.integrator("Newmark")` while the gravity
  Static analysis exists warns "can't set transient integrator in static
  analysis" and falls back to the default integrator (here identical
  Newmark 0.5/0.25 by luck — same parameters, same results).
- Rule: `ops.wipeAnalysis()` right after gravity `loadConst`; then eigen →
  rayleigh → GM pattern → transient setup (source order).

### 22. Multi-level xlsx: derive factors from elastic ratios, verify each
- Evidence: Exam07 `result_all.xlsx` (小/中/大 shear+disp, no factors
  stated): elastic-shear ratio 455:910:2002 with 大=0.6072 (committed Tcl)
  gives 小/中 = 0.13803/0.27606 (≈50/100/220 gal); both level-runs match
  to ~1–2% (peaks +0.07%/+0.4%), confirming factors AND model jointly.
  大 sheet col B ≡ node59.out row-for-row.
- Rule: cross-check sheets against .out files first (identity → same run),
  derive missing scales from linear-regime ratios, validate every level.
  Env-only level driver (sets GM_FACTOR, custom outdir) keeps model.py
  canonical — never commit variant outputs.

### 23. Deep-plastic transient drift is version-level, not settings-level
- Evidence: Exam07 大震 matches (UX, N/Vz/My ~1%) through first deep yield
  (~t=4 s), then branch-diverges (sim +29.9 vs ref −0.9 at t≈4.03 s) and
  Newton dies at t=8.7 s. Exhausted: Newton/Krylov/BFGS/ModifiedNewton,
  tol 0.1/1e-6 (identical paths — item 15 n/a here), BandGeneral/UmfPack,
  bisection to seg/16, algo-switch rescues (branch-jump, item 16).
  Mild regimes stay version-robust (elastic shell bit-exact; 小/中 ~1%).
- Rule: for GM transients, validate per-regime (gravity/small/moderate/deep)
  and report the breakdown honestly with the boundary (here: first deep
  yield). Death-after-divergence is a consequence, not a second problem —
  fix the divergence or document it, don't chase the death.

## 2026-11-14 — Dino_FramePushover (Exam04 3D RC Frame Pushover)

### 24. Provenance cross-check catches misnamed folders
- Evidence: Folder named `Elastic Time History Analysis of Frame Structure`, but
  `ref/EXAM04.s2k` header reads `实例4_框架结构推覆分析` and `co.tcl` implements
  gravity + 100-step displacement-controlled pushover (`node8.out`).
- Rule: always verify header comments and load patterns in `.tcl` / `.s2k`
  sources rather than assuming folder names reflect the actual analysis type.

### 25. Lateral reference pattern ordering with `loadConst`
- Evidence: defining lateral pattern before gravity causes `ops.loadConst("-time", 0.0)`
  to freeze the reference lateral vector to λ=0, leading to DisplacementControl failure.
- Rule: strictly define lateral pushover patterns AFTER `run_gravity()` and
  `loadConst("-time", 0.0)`.

### 26. Fast SmartAnalyze convergence on 3D RC fiber frames
- Evidence: `Dino_FramePushover` with 47 `nonlinearBeamColumn` elements and 4 fiber
  aggregators solved 10 gravity steps + 100 pushover steps to 300 mm in 0.48 s.
  Nodal displacement matched `node8.out` within 0.00045 mm (0.00015%).
- Rule: mirroring the source's `EnergyIncr 1e-3` / 1000 iter tolerance under
  SmartAnalyze provides fast convergence and bit-accurate tracking on RC frames.

## 2026-11-15 — Dino_RC_Column_4Elem_3D_Pushover (video 03/04 frame column)

### 27. Early load-factor offset against a Tcl reference: rule out the solver, then document it
- Evidence: `Dino_RC_Column_4Elem_3D_Pushover` (tcl_ref/opensees2/co.tcl). Node 1 UX matches exactly and UZ within 4.8e-6 mm, but the replayed load factor is 13% high at step 1 (16.50 vs 14.60 kN) and 2.6 kN high at step 3, falling to a 0.11% mean error from step 10. A plain-Newton replay matches the SmartAnalyze run to 1.5e-10 kN, and a similar early offset (about 15% at step 1) appears in `Dino_SRC_Column_3D_Pushover`.
- Rule: when displacements match and only the early load factors differ, run a plain-Newton literal replay to rule out the solver, then state the offset in the README and catalogue. Do not tune the model toward the reference.

## 2026-11-15 — Dino_Beam_Exam03_Pushdown (Example 03: reference outputs unusable)

### 28. Check that a reference is non-degenerate before converting; if it is not, validate analytically and say so
- Evidence: `Exam03.tcl` (tcl_ref/opensees) has a `node0.out` whose 600 displacement entries are all zero, and its node5.out and element outputs are missing. The conversion was therefore checked only against elastic beam theory: the first three steps match cracked-section theory to 0.13%. For cracked sections the sign of the load matters: with asymmetric reinforcement (780 mm^2 top, 1470 mm^2 bottom), sagging and hogging stiffnesses differ (6.05e13 vs 3.68e13 N mm^2).
- Rule: before converting, count the nonzero entries in each reference file. If the references are empty or zero, convert anyway if useful, record "analytic only" in the README and catalogue, and state the basis of the check.

## 2026-11-15 — Dino_Truss_Bridge_Ex01 (Example 01: zero-energy mode in the truss)

### 29. A zero-energy mode makes some displacements non-unique: find the null vector before chasing a mismatch
- Evidence: `Dino_Truss_Bridge_Ex01` (ref/Exam01.tcl). Element forces and every displacement match the source to about 0.0003 %, except UY of the eight top-chord nodes, which differ by one common value (+0.0973 mm at step 100, the same for all eight to 6e-7 mm). The free stiffness is singular to round-off (smallest eigenvalue -1.7e-10 N/mm vs 3.5e6 N/mm), and its null vector is uniform UY on nodes 11-18: no member joins the top chord to the bottom chord in Y.
- Rule: when a family of DOFs differs by one common constant, compute the stiffness null vector before tuning anything. If it matches the difference, document it, compare with that mode removed, and state that both solutions satisfy equilibrium.

## 2026-11-16 — opensy_ref.py status notes (Examples 37, 40)

### 30. A reference list's status notes go stale; check the repo before recording an example as "not done"
- Evidence: `opensy_ref.py` said Example 40 was "Not done on opensy" and Example 37 "Check this might done in opensy". The repo already had both: `models/Dino/Sectional Analysis of Pushover curves/model.py` (catalogued as `Dino`, which breaks the `Dino_*` pattern) and `models/Dino/Buckling analysis of Shell element steel column` (`Dino_Buckling`). For Example 02, searches for its dinochen id (151) and title found nothing in the repo except `opensy_ref.py`.
- Rule: before recording an example as "not done", match its title against folder names, README headings and catalogue text. Most catalogue entries carry no dinochen URL and some IDs break the `Dino_*` pattern, so the id alone is not enough.

## 2026-11-16 — Geo_example_1 (OpenSees geotechnical Example 1, SI to N-mm)

### 31. units.py mass constants are 1000x off: `kg` is one tonne, and `tonne` is 1000 tonnes
- Evidence: `standards/units.py` sets `kg = N*sec**2/mm` (one tonne in the N-mm-s system) and `tonne = 1000*kg`. So `DENSITY_STEEL = 7850*kg/m**3` comes out 1000x too heavy. In `Geo_example_1` the source density 2.0 t/m^3 is written as `2.0 * (N*sec**2/mm) / m**3` = 2.0e-9 N.s^2/mm^4, and the displacement and acceleration histories match the source to 1.6e-6 and 1.4e-6 of their peaks. A 1000x density error would change the period by about 32x.
- Rule: for SI masses, write the N.s^2/mm value explicitly (t/m^3 divided by 1e9). Do not use `kg` or `tonne` from units.py for mass until they are fixed. The AGENT.md §3a copy of units.py also differs from the file: its `Pa` is 1e-6 N/mm^2, but the file's `Pa` is 1 MPa.

### 32. The current PressureIndependMultiYield takes 11 values; older Tcl lines that omit the last four fail
- Evidence: openseespy 3.8.0 rejects the source line `nDMaterial PressureIndependMultiYield 2 2 $massDen $G $B $cohesion $peakShearStrain` with "invalid PressureIndependMultiYield double inputs", then "invalid PressureIndependMultiYield numberOfYieldSurf". The accepted order is `(tag, nd, rho, G, B, cohesion, peakShearStrain, frictionAng, refPress, pressDependCoe, numberOfYieldSurf)`. The recommended values 0, 100 kPa, 0 and 20 were used. The element stays elastic (peak in-plane shear 10.4 kPa against 30 kPa cohesion), so they do not change the result. `updateMaterialStage -stage 0` prints "no effect" for this material.
- Rule: when porting an older multi-yield material line, supply the recommended values, then check that the response never reaches yield before relying on the elastic result.

### 33. A Tcl `recorder Element ... material N` takes a Gauss-point index, not a material tag
- Evidence: `example_1.tcl` records `material 1` and `material 3` on element 1. The file defines only material tags 1 (FluidSolidPorous, never used by the element) and 2 (PIMY). The ODB Gauss points 1 and 3 match the source stress and strain recorders to 4.7e-6 and 1.6e-6 of the reference peaks.
- Rule: when a recorder's `material` index matches no defined tag, read it as a Gauss-point number, then confirm against the source values.

### 34. Stress columns come in a different order in the source recorder and in opstool; match them by name
- Evidence: the source `stress*.out` columns are (sigma11, sigma22, sigma33, sigma12, para). opstool's `Stresses` stores (sigma11, sigma22, sigma12, sigma33, para#1). Matching by position puts sigma12 against sigma33 and is off by about 3 kPa at Gauss point 1. Matching by name gives 4.7e-6.
- Rule: map each recorder column to its ODB component by name (see `compare_with_reference()` in `models/Geo_example_1/model.py`). Never assume the two orders agree.

### 35. SmartAnalyze's success line crashes a Windows console; `printPer=0` does not stop it
- Evidence: with `printPer=0` and `testPrintFlag=0`, the analysis finished, and then opstool's `_print_status` raised `UnicodeEncodeError` (cp1252) on the final emoji line. `PYTHONIOENCODING=utf-8` fixed it. This refines AGENT.md §12az-3, which treats `printPer=0` as enough.
- Rule: on Windows, run SmartAnalyze models with `PYTHONIOENCODING=utf-8`, and say so in the README.

## 2026-11-16 — Geo_example_1 source link (opensy_ref.py)

### 36. Look up the source link in the reference list before converting; a file's own credit line does not give the link
- Evidence: `example_1.tcl` credits Zhaohui Yang (UCSD) but gives no URL. I converted it first and set the catalogue URL to `NA`. Afterwards `opensy_ref.py` line 5643 ("Jinchi Lu and Zhaohui Yang") linked to the OpenSees wiki page PressureDependMultiYield02-Example_1, and the "Arduino, Pedro" entry (line 829) linked to DesignSafe PRJ-1901. The WebFetch tool was unavailable (model error), and the search summaries disagree on whether the non-02 wiki Example 1 page uses PIMY or PDMY. The file-level match is therefore unverified.
- Rule: before converting, search the reference list for the author name and the material name. Put the link in the catalogue, and mark a file-level match as unverified when the source page could not be opened.
