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

## 2026-11-16 — SalarDelavar_Aggregated_Column_Pushover (GitHub 2D column pushover)

### 37. A reference figure can come from different parameters than its script; check the yield moment before accepting the model
- Evidence: the script sets FI_Y = 1.474e-6 1/mm, so MY = 1.131e9 N.mm. The figure's first yield kink is about 0.91e9 N.mm, its peak moment about 1.24e9 and its end shear about 247 kN. A diagnostic copy outside the repo with FI_Y = 1.18e-6 1/mm gives MY 9.05e8, peak moment 1.232e9, end shear 246.4 kN and end axial 446.4 kN at -0.1421 mm, which match the figure. The initial stiffness (18,413 N/mm) is the same in both runs, so only the post-yield curvature differs.
- Rule: compare the first yield moment and the peak with the figure before accepting a model. If they differ, run a diagnostic copy outside the repo, report the value, and keep the script's value in the deliverable.

### 38. A pushover reference pattern with a vertical part adds axial load as the lateral load grows
- Evidence: the source pattern is (1 N lateral, -1 N vertical) per unit load factor, so the axial force rises from 200 kN to about 447 kN at 1750 mm. The figure's end axial force of about 450 kN and axial shortening of -0.142 mm agree with this.
- Rule: read the axial force plot first. If it rises with the lateral load, the reference pattern has a vertical part, and that part must be kept.

### 39. Source comments can contradict the code; convert the code and record the mismatch
- Evidence: `Weight = 200000.0  # [kg]` is used as a load in N (200 kN). `ops.fix(1, 1, 1, 1)` is commented "free theta" but fixes all three DOFs. The fall-back ladder names 'RaphsonNewton', which OpenSees does not define. The reference-list entry gives Material "RC" for a steel section.
- Rule: convert the code, not the comments. Record each mismatch in the README, and check every algorithm and material name in the source against OpenSees.

### 40. After wipeAnalysis, SmartAnalyze warns and falls back to default handlers; re-set the source's handlers first
- Evidence: the first run of `SalarDelavar_Aggregated_Column_Pushover` printed "no ConstraintHandler / Numberer / LinearSOE specified" warnings at every SmartAnalyze step, because `wipeAnalysis` had cleared the handlers. After `ops.constraints("Plain")`, `ops.numberer("Plain")` and `ops.system("BandGeneral")` were set between `wipeAnalysis` and `SmartAnalyze`, the log had no warnings, and the end state matched to roundoff (top shear 307,733 N, base moment 1.5387e9 N.mm).
- Rule: after `wipeAnalysis`, set the source's constraints, numberer and system again before `SmartAnalyze`, and grep the log for "no ... specified". This refines AGENT.md §12w, item 4, which covers the case with no `wipeAnalysis`.

## 2026-11-18 — SalarDelavar_Bridge_Viscous_Damper_SDOF (GitHub bridge viscous damper)

### 41. A "kg" label on a mass can hide a 1000x unit difference; check the period against the time step and the figure
- Evidence: `Ms = 1000  # [kg]` and `Mb = 500  # [kg]` are used in OpenSees as N.s^2/mm, and 1 N.s^2/mm = 1000 kg. Read as kg, the masses would be 1.0 and 0.5 N.s^2/mm. The undamped period would then be 9 ms, shorter than the 10 ms step, and the dashpots alone would overdamp the chain (all four eigenvalues are real). With the values as written, u0 = 0.1 mm reproduces the figure's displacement peak to 2e-6 (LESSON 47), so the values are kept.
- Rule: before converting a mass labelled kg, compute the period and the damped eigenvalues under each reading. Keep the values the figure supports, and record the reading in the README.

### 42. Rayleigh coefficients in the source: a0 = 2*DR has no 1/s, and PERIOD = pi/Omega is half the period
- Evidence: `a0 = (2 * Omega01 * DR) / Omega01` cancels Omega, so a0 = 0.04 with no unit. The mass term would need 2*DR*Omega = 0.89 1/s to give 2 % in mode 1; as written it gives 0.09 %. `PERIOD = np.pi / Omega01` is T1/2 = 0.1405 s, while T1 = 2*pi/Omega1 = 0.2810 s.
- Rule: check the units of each Rayleigh coefficient and of each period formula. Keep the source's values, and report the modal damping the run actually has.

### 43. OpenSees ignores the Rayleigh stiffness term on zeroLength elements unless -doRayleigh is given
- Evidence: a single spring-mass test with a zeroLength spring and `ops.rayleigh(0, betaK, 0, 0)` gave the undamped response (end displacement 0.0939 mm), while a numpy Newmark with C = betaK*K gave 0.0067 mm. Adding `-doRayleigh` to the same element gave 0.006726 mm, which matches numpy. The mass term (alphaM) is applied at the domain level and acts without the flag. In the bridge model the stiffness term (a1 = 1.79e-3 s) is therefore inactive, and the damping is the dashpots alone: modal xi = 19 % and 72 %. The model keeps the source's behaviour (`link_rayleigh = False`). With `link_rayleigh = True`, the two-mass run matches the numpy replica with a1*K to 1e-16 mm.
- Rule: when a source uses Rayleigh damping with zeroLength elements, test whether the stiffness term acts, and report the modal damping of the run rather than the nominal DR.

### 44. opstool cannot draw one-component nodal loads; ndm = 1 fails at the V3 and V4 stages
- Evidence: `opst.vis.plotly.plot_model(show_nodal_loads=True)` on a 1D model raises `IndexError` at `data[1]` in `opstool/post/_get_model_data_base.py` (`_make_nodal_load`), so V3 and V4 cannot run. The model was rebuilt as ndm = 2, ndf = 2 with the y DOF restrained at every node. The equations are unchanged, and all four stages then run.
- Rule: model 1D motion as ndm = 2, ndf = 2 with the y DOF fixed, so that the mandatory V3 and V4 stages work.

### 45. zeroLength elements with spread display coordinates warn once per element but give the same response
- Evidence: spreading the nodes to x = 0, 1000 and 2000 mm for the plots gives `ZeroLength::setDomain(): Element ... has L= 1000, which is greater than the tolerance` for each element. The displacement histories with coincident and spread nodes agree to the printed precision, and the spread run agrees with the numpy replica to 3e-17 mm.
- Rule: keep the source's coincident nodes unless the plots need separation. If you separate them, expect the warnings, and confirm the response against coincident nodes.

### 46. A displacement-controlled static step leaves the nodal accelerations at zero, so the first Newmark steps start unbalanced
- Evidence: after the 0.3 mm deck step, the equilibrium acceleration of Mb at t = 0 is -200 mm/s^2 (from M a = -K u), but OpenSees starts the transient from zero acceleration. The run matches a Newmark replica that also starts from zero, to 3e-17 mm. Against the exact continuous solution the error is 0.0215 mm (7 % of u0) at t = 0.07 s. With the consistent start, a0 = -inv(M) K u0, the error falls to 0.0020 mm, which is the Newmark error.
- Rule: after a static step that is followed by a transient, compare the start acceleration with the equilibrium value. Keep the source's behaviour, and report the difference in validation.txt.

### 47. A figure can match the script's equations with a different initial displacement; test the peaks before accepting a parameter
- Evidence: the figure's displacement peak, 0.098615 mm, is its first sample, so the deck starts near 0.1 mm, while the script has u0 = 0.3 mm. The same equations with u0 = 0.1 mm give 0.0986156 mm (2e-6 relative), 1.3841 mm/s (0.1 % low), 55.376 mm/s^2 (0.02 % low) and 7270 N (0.15 % low). The model keeps 0.3 mm, and validation.txt reports the 0.1 mm replica.
- Rule: when a figure's peaks match only under another parameter, run a diagnostic outside the deliverable, report the result, and keep the script's value. This extends LESSON 37.

## 2026-11-20 — SalarDelavar_Cable_Suspension_Bridge_04 (truss-only mechanism; converted with added deck beam stiffness, LESSONS 49-53)

### 48. A truss-only model has a singular initial stiffness; the source's fallback runs it, but equilibrium fails
- Evidence: the source builds the cables, deck and hangers only as `corotTruss` elements. With 22 nodes per cable there are 21 top + 21 deck + 22 hanger members = 64 members, and the four end nodes are fixed, which leaves 80 free DOFs. Each member adds one rank-1 term to K, so rank(K) is at most 64 < 80 and the undeformed stiffness is singular. The source's first pushover algorithm (ModifiedNewton with EnergyIncr) fails at step 1 (load factor -nan). The source's retry ladder (KrylovNewton with NormDispIncr) recovers step 1, and steps 2 to 10 then converge with the first algorithm. The load factor grows roughly as the cube of the displacement, which suggests the stiffness comes from cable tension (not verified). But the support reactions are not in equilibrium: the horizontal reactions sum to +63.6 N, -63.6 N and +63.6 N at steps 2, 5 and 8, where the applied load is vertical only. The cause is not confirmed. The reference figure's 51-node version has the same count: 151 members for 196 free DOFs.
- Rule: before converting a truss-only source, count members against free DOFs. Then run the source's own loop and check global equilibrium at each step before trusting any output. Convert the code as written and record the mismatch. Do not add elements without the author's intent.

## 2026-11-20 — SalarDelavar_Cable_Suspension_Bridge_04 (conversion with added deck beam stiffness)

### 49. OpenSees ignores the Rayleigh stiffness term on corotTruss elements; elasticBeamColumn does apply it
- Evidence: a single spring-mass test with a corotTruss element and `ops.rayleigh(0, 0, 0, betaK)` gave the same end displacement as the undamped run (-0.098926 mm). The same test with an elasticBeamColumn matched a numpy Newmark run with C = betaK*K to 1e-16 mm (end 0.006726 mm, undamped 0.093907 mm). A zeroLength element needs `-doRayleigh` for the same term (LESSON 43).
- Rule: in a truss-only model, Rayleigh damping gives mass-proportional damping only. Check each element type with a one-element test before reporting a damped response, and state which elements carry the stiffness term.

### 50. A stabilizing beam stiffness can set the response; check the first period against the time step
- Evidence: the source gives the deck only an area and an equivalent diameter (145.6 m). Adding bending stiffness from the same solid circle (I = pi*D^4/64 = 2.2e19 mm^4, EI = 4.6e26 N.mm^2) makes deck flexure the first mode, with T1 = 0.0197 s. OpenSees and numpy agree on this period. With dt = 0.01 s the response is aliased (T1/dt is about 2). The pushover becomes linear, with a stiffness of about 2.4e12 N/mm. For the deck mode, T scales with I^(-1/2).
- Rule: when a stabilizing assumption is needed, state its basis, compute the first period, and compare it with the time step before trusting any dynamic result. Do not choose the value to fit a figure.

### 51. SmartAnalyze costs about 5.8 ms per static step, against 0.5 ms for raw ops.analyze; plan the run time
- Evidence: 1000 static displacement-control steps took 5.8 s in SmartAnalyze and 0.5 s with raw `ops.analyze`, on the same model and settings. Reading the reactions every step added nothing measurable. The source's 250,000-step pushover therefore takes about 25 minutes, and the ODB fetches were limited to 100 calls.
- Rule: time one step inside SmartAnalyze before writing a long protocol. Limit ODB fetches for long analyses, and state the run time in the README.

### 52. A source's "damped" run can equal the undamped run when the damping call sits behind an unset flag
- Evidence: in the source's dynamic function, the Rayleigh call is inside `if periodTF:`, and both dynamic runs set `periodTF = False`. The `damping` argument is never used, so the two runs are identical by construction. The conversion runs the dynamic analysis once.
- Rule: check that each damping option reaches the solver, and compare the damped and undamped outputs before reporting any effect of damping.

### 53. SmartAnalyze can stop a long displacement-control pushover early; a raw loop with the same test can run to the target
- Evidence: in the converted cable model, SmartAnalyze reports a failed step at step 16,881 (control node -168.8 mm, load factor 4.07e14 N). The same step with raw `ops.analyze`, with EnergyIncr 1e-6 and a persistent ModifiedNewton, converges for 250,000 steps. Calling `support_reactions()` after each step does not change the failure. Re-creating the integrator or the analysis object at each step, as SmartAnalyze does, fails at step 6 in the raw replay, although SmartAnalyze itself reaches step 16,880. The exact mechanism is not identified.
- Rule: after each SmartAnalyze run, compare the last step with the protocol's target. If the run stops early, replay the window with raw OpenSees to see whether the state is solvable. Report the mechanism as unidentified when it is not found, and do not change the solver settings without a decision.
- Outcome: the user approved a raw `ops.analyze` loop for this pushover on 2026-11-20, as an exception to AGENT.md §3c. The loop keeps the source's EnergyIncr 1e-6 test, ModifiedNewton algorithm and 0.01 mm increment, and reaches the 2500 mm target.
