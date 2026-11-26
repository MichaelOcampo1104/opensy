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

## 2026-11-23 — SalarDelavar_Cable_Suspension_Foot_Bridge_01 (truss-only footbridge; beam stiffness added to the deck)

### 54. A Rayleigh damping from an assumed frequency is not the structure's damping; check where the coefficients come from
- Evidence: the source's free-vibration and seismic functions set omega1 = sqrt(K_ref / M), with K_ref = 1 N/mm in the free run and 1000 N/mm in the dynamic run (the source's KE), and omega2 = 2 omega1. The Rayleigh coefficients for a 5 % ratio are then computed from these assumed frequencies, not from the modes. The result is alpha = 9.4e-5 1/s and beta = 23.6 s for the free run, which makes the stiffness term large against the deck.
- Rule: when a source computes Rayleigh coefficients, check whether the frequencies come from the modes (eigen) or are assumed. If they are assumed, report the damping the run actually has, from the modal ratios of the matrices, and not the nominal ratio.

### 55. A mass labelled kg but used as N.s^2/mm can push the first period into thousands of seconds; the ground-motion responses then become small
- Evidence: the foot-bridge source's TOTAL_MASS = 500000 is labelled kg but used as N.s^2/mm, which is 5e8 kg. The first period is 1963 s. The largest vertical response to 10 s of ground motion is 0.015 mm, and it occurs at 30 s, after the record ends. Read as kg, the mass would be 1000 times smaller and the first period about 62 s. This extends LESSON 41.
- Rule: before reading any dynamic result, compare the first period with the length and frequency content of the record. If the period is far longer than the record, the response is not informative. Keep the source's value, record both readings, and leave the choice to the author or the user.

### 56. A linear numpy replica of a corotational model differs by the geometric stiffness; soft structures show differences of 1e-4 to 1e-3
- Evidence: in the foot bridge 01 run, the first pushover step differs from a linear solve by 1.0e-4 (relative), and the free-vibration history differs by 1.5e-3 mm, which is 0.08 % of the 2 mm initial displacement. The cable model, whose deck is stiff, differed by 4e-13 at the same step. The linear replica takes its initial state from a linear static solve and omits the geometric stiffness of the cables. That stiffness is likely significant when the structure's stiffness is low (about 10 N/mm here).
- Rule: when a corotational model is checked against a linear replica, measure the difference at the first step and report it. A difference of this size is geometric, not a model error, and the replica should not be used to validate beyond it.

### 57. A hand-built stiffness matrix for a sloped beam must include the element orientation; a horizontal shortcut gave a 0.2 % period error
- Evidence: in the sub-model 02 deck, which follows the sloped cable, the segments are not horizontal. The first numpy check built each beam segment as if it were horizontal, and its periods were about 0.2 % from the OpenSees values. After each segment matrix is rotated into the global frame (T' k T), the periods agree to six digits (OpenSees 1968.561662 s, numpy 1968.561661 s, and the same for the other three). The OpenSees model did not change; only the check did. Sub-model 01 has a horizontal deck, so its periods were not affected.
- Rule: when a validation builds element matrices by hand, rotate each element into the global frame, or confirm that every element is horizontal before using the shortcut.

### 58. A truss chain with fewer members than free DOFs can report success at its first steps while equilibrium fails
- Evidence: sub-model 03 as written has 50 truss members and 98 free translational DOFs, so its tangent stiffness has rank 50. In a scratch run, OpenSees returned a zero error flag at steps 1 and 2, but the sum of the support reactions differed from the load factor by about 1e-5 N, where the load factor was about 1e-13. Step 4 then failed to converge (NaN after 50,000 iterations, error flag -3).
- Rule: before running a source whose stiffness may be singular, compare its member count with its free DOFs and check the rank. Then check the reaction sum against the load factor at every step. A zero error flag is not evidence of equilibrium. This extends LESSON 48.

### 59. Converting truss members to beams changes what the same Rayleigh coefficients damp
- Evidence: the source damps through corotTruss members, which ignore the stiffness term (LESSON 49), so its coefficients damp only the mass. After sub-model 03 is converted to beams, the same coefficients also damp the stiffness term. The first-mode ratio becomes 284.6 % in the free run and 9.62 % in the dynamic run, against 0.0195 % and 0.617 % for mass-only damping. The free damped run is overdamped and decays without oscillating.
- Rule: when a conversion changes the element type, compute the modal ratios that the coefficients give in the source model and in the converted model. Report both, and leave the choice to the user.
- Outcome: on 2026-11-24 the user chose to keep the source's coefficients as written. The model therefore carries the stiffness-proportional damping, and the mass-only case was not run.

### 60. A time step can be longer than the shortest period of a chain; check the short periods as well as the first
- Evidence: sub-model 03 has 34 of its 98 translational modes with periods shorter than dt = 0.01 s; the shortest is 0.00455 s. The source's truss chain has the same shortest period and the same count, because they come from its axial stiffness EA/L and nodal mass as written, so the beam conversion did not create them. The undamped seismic run has a peak horizontal support reaction of 11.0 kN, more than six times the rigid-body inertia of the record (about 1.7 kN).
- Rule: list the shortest periods before reading a dynamic result. If any is shorter than dt, state which outputs it can affect, and do not read the reactions as physical until the time step has been checked.

### 61. A replica of a transient run must start from the solver's initial state: zero acceleration and the source's initial velocity
- Evidence: in the concrete column joint model, a linear Newmark replica that computed the initial acceleration from the ground force at t = 0 differed from the OpenSees seismic run by 1.6e-4 mm in the first 2 s (0.85 % of the largest response; about 2.8 times too large at the first step). OpenSees starts from zero acceleration with the initial velocity iv0 (5e-5 mm/s, the source's -vel0). With that start the replica agrees to 3e-10 mm (x) and 7e-8 mm (y). A one-step shift of the force made the difference about ten times larger, so the time alignment was already correct.
- Rule: before judging a replica of a dynamic run, match its initial acceleration and velocity to the solver's convention, and test a one-step shift to confirm the time alignment.

### 62. A log-decrement estimate of a forced response is not a damping ratio; use the modal ratio from the matrices
- Evidence: the source estimates damping from the displacement peaks of the whole 10 s ground-motion record. The record is forced, and the run ends 0.02 s after it, so the peaks are not free decay. The conversion gives -1.07 %. The numpy modal ratios of the two lowest modes are 2.50 % and 2.51 % as written, and 5.00 % when the springs also carry the stiffness term.
- Rule: report the modal ratios computed from the matrices, and do not use a log-decrement of a forced response as a damping estimate. This extends LESSON 54.

### 63. A joint spring much stiffer than the column carries almost all of the lateral load; the column's base shear then does not show the total load
- Evidence: in the concrete column joint model the top lateral spring has 1.26e9 N/mm. A cantilever of the same bending stiffness (3EI/L^3 with EI = 9.4e14 N.mm^2) would have about 1e5 N/mm, so the spring is more than 10^3 times stiffer. At 5 mm top displacement the spring carries 6.3 GN and the column base shear is 0.36 MN (0.006 % of the load). At 520 mm the spring carries 68.9 GN and the base shear is 1.45 MN (0.002 %). The source's pushover plots the base shear, so its curve shows the column's share, not the total load.
- Rule: before interpreting a pushover base shear, compare each support spring force with the applied load, and report which path carries the load.

### 64. A mass labelled as a weight moves the period by a factor of 100 and can fall below the time step; check the label against its use
- Evidence: the source labels its top-node masses "[N]" (2.0e6) and uses them as N.s^2/mm (2e9 kg). Read as a weight, the mass is 2.0e6 N / 9810 mm/s^2 = 204 N.s^2/mm, and the two lowest periods become 0.00253 s and 0.00252 s, which the time step of 0.01 s does not resolve. As written, the periods are 0.2503 s and 0.2495 s (25 steps per period). This extends LESSON 55.
- Rule: check each mass label against the way the code uses it, and compare the resulting period with the time step before reading any dynamic result.

## 2026-11-24 — SalarDelavar_Composite_Section_FRP_or_Plate (2D fibre portal frame, Concrete01 and a steel-plate jacket)

### 65. A Concrete01 frame is cracked from its first step: a gross-section check is 2.6 times too stiff
- Evidence: the first pushover step of the source's frame has load factor 270.5 in OpenSees. A linear numpy frame with the uncracked sections gives 698.9 (762.7 with the plate), 2.6 times the OpenSees value. Concrete01 has no tensile strength, so its tension fibres carry no stiffness, and every section is cracked under any bending moment. The first version of the model's check used the gross section and failed for this reason.
- Rule: before choosing a reference for a first step, check each material's tension behaviour. A model whose concrete has no tension needs a cracked-section reference.

### 66. A zero-axial-force cracked section misses 1.7 % of the first step; the check must use the section state at each integration point
- Evidence: with a cracked section at zero axial force, the numpy frame gives 266.0 at the first step, 1.7 % below OpenSees (270.5). The vertical loads put about -237 N of axial force in each column at the first step, and the cracked section's axial-bending coupling depends on that force. A force-based element whose section flexibility follows the state at each of its five Lobatto points, iterated to convergence, gives 270.5248 without the plate (relative difference 4.7e-5) and 349.2369 with it (9.6e-6). A 5-point Gauss-Legendre rule gives 4.6e-4 and 4.1e-4 instead, so the integration rule must match the OpenSees element. The remaining 5e-5 is of the order of the displacement tolerance.
- Rule: for a frame with cracked fibre sections, check the first step with the state-dependent force-based element and the solver's integration rule. Show the Gauss-Legendre variant to expose the sensitivity, and do not use a cracked section taken at zero force.

### 67. A patch described by a comment can sit elsewhere: the source's "bottom" plate of the beam is on a width face
- Evidence: the source's beam plate is `patch('rect', ..., -(y1 + T), -z1 - T, y1 + T, -z1)`, with the comment "Bottom plate". Its depth range covers the full height plus the plate thickness, and its width range lies outside the -z face. The plate is therefore a 10 mm strip on one width face spanning the depth, and in the 2D frame it stiffens the beam like a web (uncracked EI +1.8 %). The column patches, by contrast, cover the four faces as intended.
- Rule: check each source patch against its coordinates, not its comment. Keep the geometry as written, and state in the README where the plate actually is.

### 68. A pushover that controls one node and records another reports a smaller displacement than its target; the ductility then refers to the recorded node
- Evidence: the source controls node 4 to 175 mm and records node 3. At the last step the node-3 displacement is 167.0 mm without the plate and 167.5 mm with it. The source's bilinear fit, ductility and R are computed from the node-3 displacement, so mu = 3.52 and 3.72 refer to node 3, not to the 175 mm control.
- Rule: state in the README which node gives the ductility, and do not read the last control value as the recorded displacement.

## 2026-11-24 — SalarDelavar_Confinement_Nonconstant_Elastic_Or_Inelastic_Frame (2D fibre frame, elastic and inelastic pushover and time history)

### 69. OpenSees lumps the element mass for `-mass`: m·L/2 at each end, with no rotational inertia
- Evidence: a single elastic cantilever element (L = 1000 mm, m = 6.25 N·s²/mm², EI = 10^14 N·mm², EA = 10^9 N) has eigenvalues 96 and 320 rad²/s². These equal 6EI/(mL^4) and EA/(mL/2), the lumped values. The consistent mass of the same element gives 199.7. For the ten-node frame, the six lowest finite eigenvalues of the lumped numpy model, with the massless rotational DOFs condensed out, agree with OpenSees to six decimal places, and the inelastic element starts with the same eigenvalues as the elastic one.
- Rule: check the element mass convention on one element before comparing periods. Build the numpy eigenproblem with the lumped mass, condense the massless DOFs, and state the convention in the README.

### 70. The ground excitation applies the full element mass at each free end, not the lumped half
- Evidence: a single mass on a spring matches the textbook Newmark step exactly (unit test: −2.000 x 10^-5, −8.400 x 10^-5, −1.608 x 10^-4), so the integrator is standard. For the frame, the first step of the node-3 displacement is 1.298 times the textbook value M·r·a. For one cantilever element, the free-end displacement is 2.01 times the textbook value without a nodal mass and 1.208 times with a 12,000 nodal mass; both match the rule that the free end receives the full element mass m·L. The replica with the force Σ(nodal mass) + Σ(m·L at each free end) reproduces the first four steps to seven digits and the linear-geometry OpenSees run over 5000 steps to 3.6 x 10^-11. The textbook force M·r differs by 41 % over 1000 steps. The eigenvalues and the effective mass keep the lumped mass (LESSON 69).
- Rule: do not assume the excitation force uses the same mass as the eigen analysis. Match the force to the solver's first steps (one DOF first, then the model), and state the rule that is found.

### 71. Source masses labelled [kg] are used in N·s²/mm, and the element masses do not match the density of concrete (extends LESSON 55 and 64)
- Evidence: the source's nodal mass 12000 is labelled [kg], and its element masses come from the factors 0.000025·B·H (6.25 for the column, 3.75 for the beam). In the N-mm-s system the total mass is 87,750 N·s²/mm and the four lowest periods are 7.58, 2.44, 1.83 and 1.03 s. Read as kg, each mass is 1000 times smaller and each period 0.0316 times these, down to 0.033 s, which is 3.3 steps of dt = 0.01 s. In N-mm-s, the element mass per unit length is about 10^4 times that of a 500 x 500 mm concrete column at 2500 kg/m³.
- Rule: check each mass label against the unit system the code uses and against the density of the material, and check the shortest period against the time step before reading any transient. Keep the source's value and report both readings.

### 72. A replica of a corotational transient agrees only while the displacement is small; a linear-geometry run of the same model attributes the rest (extends LESSON 56)
- Evidence: the elastic run (corotational) agrees with the linear replica to 1.3 x 10^-8 while |u| <= 1 mm and to 2.1 x 10^-4 while |u| <= 10 mm. Over the full record the difference is 2.5 %, and the peak displacement is 328.7 mm against 325.5 mm with a linear transformation. The same model with a linear transformation agrees with the replica to 3.6 x 10^-11 over 5000 steps, so the residual is geometric.
- Rule: compare a replica only over the window where the displacement is small, report the whole-record difference separately, and attribute it to the geometry only after a linear-geometry run of the same model confirms it.

### 73. A Linear time series grows with time in a transient analysis, so a static load in a dynamic pattern is a ramp
- Evidence: in a transient analysis, a unit horizontal load in a `Linear` pattern gives tip displacements 8.64 x 10^-5, 1.728 x 10^-4 and 2.592 x 10^-4 mm at t = 1, 2 and 3 s, so the load is t N. The source adds such a load to the time-history run, where it reaches 50 N at 50 s.
- Rule: when a static load is placed in a `Linear` pattern that is used in a transient analysis, the load is a ramp in time. Check the time dependence of every load in a dynamic pattern.

## 2026-11-25 — SalarDelavar_Confinement_Nonconstant_Elastic_Inelastic_Impact (2D fibre frame under a harmonic nodal load)

### 74. A time series built on one time axis and applied at another spacing runs at a different frequency: the source's harmonic load runs at 0.1 times its intended frequency
- Evidence: the source computes 5000 values of 1 MN sin(0.65 ω_n t) on load_time = linspace(0, 5 s, 5000), a spacing of 0.0010002 s, and applies them as a Path series with -dt 0.01 s. The applied frequency is 0.32971 rad/s (period 19.06 s), not 3.29648 rad/s (period 1.906 s). The first zero crossing comes at 9.53 s, not 0.953 s, and the values last 49.99 s. The elastic run follows the applied series: the replica agrees with it to 8.0 x 10^-7 over the first 83 steps (|u| <= 1 mm).
- Rule: when a time series is computed on one time axis and applied at a fixed dt, compare the two spacings, and the period of the applied series with the stated frequency, before reading any response. Keep the source's values and state the mismatch in the README.

### 75. A Path series of nodal forces is not scaled by mass, unlike UniformExcitation: the replica applies only the load values
- Evidence: the source applies the values as nodal loads of 1.0 in X at nodes 3 and 4 in a Plain pattern, with no ground motion. A replica that applies F(t) at those DOFs, with the gross stiffness, the lumped mass with the nodal masses and the Rayleigh damping, agrees with OpenSees to 8.0 x 10^-7 over the first 83 steps (|u| <= 1 mm), 3.1 x 10^-4 over 189 steps (|u| <= 10 mm) and 3.3 x 10^-3 over the whole 100 s. The same model with a linear transformation agrees to 1.5 x 10^-11 over all 10,000 steps, so the rest is the corotational geometry (LESSON 72).
- Rule: the force a pattern applies depends on its type. UniformExcitation applies the element and nodal masses to the free DOFs, while a nodal load applies only its value. Build the replica from the pattern the solver uses, then run the same model with a linear transformation before attributing the residual to geometry.

### 76. A Path series is zero after its last value
- Evidence: the source's values end at 49.99 s with -0.699 MN, and the run lasts 100 s. OpenSees agrees with a replica that applies zero force after the last value: the largest |u| after 50 s is 38.24 mm (OpenSees) and 38.34 mm (replica), a difference of 2.7 x 10^-3 of the maximum. A replica that holds the last value settles near -31 mm and differs from OpenSees by 1.59 times the maximum.
- Rule: check how the solver evaluates a time series beyond its last value before reading the response after the data end, and test the replica with the other convention.

### 77. A natural frequency typed into a source script need not be the frame's first frequency
- Evidence: the source sets omega_n = 5.0715 rad/s (period 1.2389 s) as a constant, and its script has no eigen analysis. This frame's first two periods are 7.584 s and 2.441 s (lumped masses in N·s²/mm, LESSON 71), so 5.0715 rad/s matches neither. The source's target 0.65 omega_n (3.30 rad/s) is about four times this frame's first frequency (0.83 rad/s).
- Rule: compare a hard-coded frequency with the model's own eigenvalues before using it to set a load frequency, and report the difference.

### 78. On Windows a path longer than 259 characters fails in the ODB writer, so a long model folder name can stop a run after both analyses have finished
- Evidence: a run under a 75-character UniqueID stopped in `odb.save_response()` with FileNotFoundError on a zarr partial file of the pushover ODB. The path was 265 characters (`models\<UniqueID>\output\RespStepData-pushover_elastic.odb\part_1.zarr\ModelInfo\FixedNodalData\FixedNodalData\.zarray.<hash>.partial`). The 63-character UniqueID of the first sub-model has a deepest final output file of 216 characters. With a 61-character UniqueID, the same model ran to exit code 0 and wrote all its CSV, text and figure files.
- Rule: keep the UniqueID, which is also the folder name, at 61 characters or fewer for this stack, and check the longest output path (including the temporary zarr files) before the first long run. Rename the folder before running if the name is longer.

## 2026-11-25 — SalarDelavar_Ductility_Damage_Index_Confinement_Enhancement (2D fibre frame, ductility damage index)

### 79. A sub-model of the same source series can change a scale factor, so each sub-model's parameters are read from its own script
- Evidence: the first sub-model's main sets `SSF_X = 10.0`, and the ductility sub-model's main sets `SSF_X = 0.01` for the same record (the two X records are identical files, byte for byte). The ductility sub-model also has no elastic branch in its `PD_ANALYSIS`. Its inelastic time history peaks at 0.35 mm, where the first sub-model's peaks at 445.9 mm.
- Rule: read the scale factors, the element branches and the durations from each sub-model's own script. Do not reuse a previous sub-model's parameter set, even when the record files are identical.

### 80. A helper with the same name can change between sub-models: port each version and check its guards against the record
- Evidence: `DAMPING_RATIO_FUN.py` differs between the first sub-model and the ductility sub-model. The first returns 0 when there are fewer than two peaks or a non-positive peak. The second has no such check and returns NaN. On the ductility time history, 7 of the 24 local maxima of the node-3 displacement are zero or negative, so the log-decrement ratio is undefined there: the second version returns NaN, and the first would return 0.
- Rule: diff each helper file against the version already ported before reusing a port, and state in the README what the helper returns for a record it cannot evaluate. Two versions can disagree on the same input.

### 81. A period helper that takes the minimum over four eigenvalues returns NaN when one eigenvalue is negative, and a finite-value summary hides it
- Evidence: in the inelastic time history of the impact-load sub-model, 4 of 10,000 steps have a negative tangent-stiffness eigenvalue, the first at 15.67 s, so the source helper's `np.min` and `np.max` return NaN at those steps. The first report took `np.min` over the whole run, and the range printed as NaN for the whole run. Over the finite steps the range is 1.39 s to 102.5 s.
- Rule: count the NaN results before summarising a range, use NaN-aware reductions, and report the count and the time of the first NaN step.

## 2026-11-25 — SalarDelavar_Ductility_Damage_Index_Confinement_Rigid_Roof (2D fibre frame with a rigid roof)

### 82. A "rigid roof" in a source can be a rotation restraint at the roof nodes, not a rigid diaphragm: read the flags of each fix()
- Evidence: the source's `ops.fix(3, 0, 0, 1)`, `ops.fix(4, 0, 0, 1)`, `ops.fix(9, 0, 0, 1)` and `ops.fix(10, 0, 0, 1)` restrain the third flag, the rotation, and leave the translations free. With the restraints, the two top nodes move together in X: node 3 reaches 675.000 mm, the same as the control node 4. The first pushover load factor rises from 299.8 to 1041.3, about 3.5 times. A numpy model with the same restraints reproduces the first step (relative difference 1.6 x 10^-4), the Rayleigh coefficients (to six digits) and the periods of the two targeted modes (4.480435 s and 1.247120 s).
- Rule: name a restraint by the DOFs it removes, not by the word in the source's comment. Re-derive the numpy free-DOF set from the restraint flags before comparing with OpenSees.

### 83. A bilinear fit of a softening pushover gives a negative post-yield tangent and an over-strength factor below 1, and a damage index below 0
- Evidence: in this sub-model the base shear peaks at 3.33 MN and falls to 3.04 MN at 675 mm, so the post-yield tangent of the fit is -133.4 N/mm and Omega_0 = 0.9743. The damage indices are -0.0848 in X and -0.1605 in Y, because the peak displacements (24.1 mm and 3.4 mm) lie below the yield displacements of the fits (75.0 mm and 8.8 mm). The source's formula is not clipped.
- Rule: check the sign of the post-yield stiffness before reading Omega_0 and the damage index, and report a negative index as computed, with its reason, instead of clipping it.

## 2026-11-26 — SalarDelavar_Optimization_Confinement_Enhancement_Ratio (2D fibre frame, confinement ratio search)

### 84. A branch that the source's main script never calls is not part of the analysis: list the calls before converting
- Evidence: the source's `PD_ANALYSIS` has a DYNAMIC branch (an HHT integrator, Rayleigh damping from its two lowest modes, and a Path ground motion), but the main script calls `PD_ANALYSIS` only with `ANA_KIND='PUSHOVER'`, in the three search calls. The branch is not converted, and the README says so.
- Rule: before converting a source file, list every call of each function and each branch. A branch with no call is documented as not converted, not converted silently.

### 85. Analyses run in separate processes must not share a working folder: opstool's set_odb_path removes the results folder of that folder
- Evidence: three worker processes started from the model folder failed in `opstool.post.set_odb_path` with PermissionError (WinError 5) in `shutil.rmtree`. opstool fixes its results folder when it is imported (`RESULTS_DIR = Path(os.getcwd()) / ".opstool.output"`), so each worker removed the folder that the others were using. With each worker started from its own folder under `output/.work`, the three pushovers of each iteration completed, and the final run wrote 16 ODB sets.
- Rule: start each parallel analysis process from its own working folder before it imports opstool, and call `set_odb_path` only inside that process.

### 86. A source's exported results come from its last call in a loop, not from its optimum: run the optimum itself
- Evidence: the source's Excel export and plots use the variables of the last `PD_ANALYSIS` call in its loop, which is at X + ESP in the last iteration. The conversion adds one pushover at the optimum X* = 2.147387. Its ductility is 5.500000 (a difference of 3 x 10^-13 from the target), and its own results are written.
- Rule: when the source reports 'the optimum', check which call produced its outputs, and run the optimum explicitly.

### 87. A fibre mesh across the width of a patch does not change an in-plane response with a one-dimensional concrete law
- Evidence: at X = 1.25 the ductility is 5.751466871648777 with one fibre across the width and 5.751466871638407 with five (a difference of 1 x 10^-11). The first pushover step and the equilibrium agree to rounding. With one fibre across, each pushover took 48 to 90 s.
- Rule: refine or coarsen a mesh only in the directions that enter the constitutive law, and test one analysis before and after a mesh change. A change along the depth of a section does change the result, so it is a separate decision.

### 88. A long search must save each completed iteration and resume from it
- Evidence: a search run stopped during its fifth iteration when the session ended. Its first four iterations existed only in memory, so their values and the final pushover were lost, and the run had to start again from the beginning.
- Rule: write each completed iteration to disk at once, and let a restarted run continue from the last saved iteration, after removing the partial output of the iteration it was in.

### 89. Run times measured while another model run shares the machine are not comparable: record the load with each timing
- Evidence: the same pushover (Kc = 1.25, whose results agree with the first sub-model's CSV to the last digit) took 625.6 s in the identity check. That check ran while another session's `model.py` was using the machine, and the first sub-model's own pushover took 3 min 28 s (its README).
- Rule: take a timing only when no other run is active, or record the other load next to it, and compare times only between runs made under the same load.

### 90. opstool writes an empty `.opstool.output` folder into the working folder, and the repository's .gitignore does not cover it
- Evidence: empty `.opstool.output` folders appeared inside model folders during several runs (the first sub-model's, and the optimisation search's). The .gitignore covers only `Opensees_references/**/.opstool.output/`, so the folder shows as untracked and would be committed with its model if it were staged.
- Rule: before staging a model folder, check for `.opstool.output` and remove it. A `.gitignore` rule for `models/**/.opstool.output/` would prevent this; that rule is not added here.

## 2026-11-26 — Impact from Pipe 300 Pad Stress (2D stress under a pad foundation; quad elements, gmsh size fields)

### 91. A gmsh Box size field returns its outside value everywhere beyond its transition, so a Min over fields caps the whole mesh
- Evidence: the first pad field was a Box with the pad size inside and 250 mm outside. Min over the fields took that 250 mm everywhere, so the 0.3 m pad case meshed to 939,350 quads instead of about 12,300. A Box with a very large outside value, plus a Threshold band with `StopAtDistMax = 1`, gave 12,314 quads.
- Rule: when a Box or Threshold value goes into a Min, check its value outside its own region: a finite outside value becomes a cap on the whole mesh. Use a very large outside value, or a Threshold with `StopAtDistMax`, and count the quads after meshing. A count far above the estimate means a field is capping the mesh.

### 92. OpenSees returns too few values from `resistingForce` for a 4-node quad, so nodal forces from quads have to come from the element stiffness
- Evidence: `ops.eleResponse(tag, "resistingForce")` returned fewer values than the four nodes need, and the run stopped with IndexError right after the gravity step (converged in 2.4 s). The `stress` response works for quads. The 8 x 8 stiffness from the 2 x 2 Gauss rule, times the change in nodal displacement, reproduces the closed-form nodal forces of a unit rectangle to 1e-12.
- Rule: for quad nodal forces, use K times the change in displacement, and test the routine on a rectangle with a known uniform strain before using it on a model.

### 93. Nodal contact forces from element-average stress missed a uniform load by 5 to 20 %; K times the change in displacement gives the applied load exactly
- Evidence: in the flexible case the exact contact is 75 kPa at every ground node. Element-average stress gave 71.3 to 90.3 kPa at those nodes and 364.2 N in total against 368.6 N applied. K times the change in displacement gives 75.000 kPa at every node, and 368.591 N in all five cases.
- Rule: test a contact routine on a uniform surface load first. Every nodal value must equal the applied pressure and the total must equal the applied force, before the routine is used under a pad.

### 94. With all-quad subdivision gmsh makes elements about half the size target, so count the elements before the run
- Evidence: the 25 mm pipe target gave 76 nodes on the 942 mm outer circumference, about 12.4 mm each. The fine model's 12.5 mm target gave 152 nodes, about 6.2 mm. A 75 mm target in the 0.3 m pad gave 8 rows through its thickness (1,056 quads).
- Rule: with `SubdivisionAlgorithm = 1`, expect elements about half the target. Check the node count on a short edge, here the pipe circumference, or the quad count in one region against the count wanted, and set the target from that.

### 95. Bin averages at a corner are mesh-dependent too: a finer pad held within 1%, but coarser zones moved the edge bins by up to 25%, so only the middle bins and the depths are robust
- Evidence: for the 0.3 m pad, halving the pad element size moved the largest corner-node contact from 757 to 980 kPa, and the 0.5 m edge bins by under 1% (127.5 to 127.8 kPa and 136.3 to 137.0 kPa). Halving the zone size (500 to 250 mm target) moved the bins by under 0.7 kPa. Coarser zones (pad target 1000 mm, wider zone 2000 mm, pad thickness / 2) moved the edge bins by 6 to 7% for three pads and by 25% for the 1.2 m pad, where the coarse run was lopsided (141 kPa on the left, 191 kPa on the right). The middle bins moved by at most 2.6% and the depths by at most 4.2%. The current study has a 7 to 8% right-to-left edge difference in three of four pads. The 0.3 m pipe-level stress moved by 34% under the coarse zones.
- Rule: test edge bins at two mesh sizes, including one coarser than the study, before trusting them. Use the left-to-right difference under a symmetric load as the noise floor. Report the middle bins and the depths as the main results; treat the single-node peaks, the edge bins and the pipe-level values as indicative.

### 96. A depth profile is only as good as the elements at that depth: refine to at least twice the depth of interest before reading it
- Evidence: the first refinement stopped 2 m below ground, so the 4 m far-field elements governed from about 5 m down. The flexible load then read 33 kPa at 10 m, against 22.5 kPa from the closed-form strip solution. Refining to 12 m, with 250 mm and 500 mm elements, gave 22.5 kPa at 10 m (closed form 22.53 kPa). The flexible profile is then within 3 % at 1, 3, 5 and 10 m.
- Rule: before reading a stress at depth, refine the mesh to at least twice that depth, and check the flexible or uniform case against a closed form.

### 97. A linear elastic model with a linear load ramp has frames equal to the final stress times the load fraction, so its animation shows build-up, not a change of shape
- Evidence: in all five cases each frame matched the final stress times its load fraction to within 1e-6 kPa (deviations 6e-9 to 1e-6 kPa). The animation therefore shows the same pattern at a smaller scale at each step.
- Rule: check the frames against the load fraction before describing an animation of a linear run, and say in its caption that the shape does not change. A shape change needs a non-linear material or staged construction.

### 98. A cell-based stress map drawn with edgecolors='none' shows white seams between cells; edgecolors='face' with a thin linewidth removes them
- Evidence: the maps and animation frames drawn with `edgecolors="none"` showed thin white lines along every cell edge. With `edgecolors="face"` and `linewidths=0.15` the same figures show no seams.
- Rule: draw cell-based stress maps with `edgecolors="face"` and a thin linewidth, and check the figure at full size before reporting it.

### 99. A bonded pad with a modulus 1000 times the soil's concentrated the contact at its edges even when thin, which the plate stiffness index does not predict; the interface has not been varied
- Evidence: the 0.3 m pad (K = 0.02) carried 127.5 and 136.3 kPa in its two edge half-metre bins and 59.0 kPa in the middle. The 0.6 m pad at E 3 GPa (also K = 0.02) gave 132.6 and 142.4 kPa at the edges and 59.3 kPa in the middle. A flexible-plate expectation is near-uniform contact at small K. The frictionless case has not been run, so the cause is open.
- Rule: do not read a plate stiffness index as the contact shape of a bonded pad. Run the frictionless interface, or report the edge pattern as unconfirmed.

## 2026-11-26 — SalarDelavar_Sensitivity_Confinement_Enhancement_Ratio_Rebar (2D fibre frame, rebar and confinement grid)

### 100. A ratio the source derives from its geometry must be checked against the bars its own section places
- Evidence: the source's RO_COL = 8 As / (Hc Bc) and RO_BE = 6 As / (Hb Bb). Its CONFINED_CONCRETE_SECTION places six bars in a column (three on each face) and eight in a beam (three, two and three). At 20 mm column rebar the stated ratios are 0.010053 (column) and 0.008042 (beam); the bars the sections have give 0.007540 and 0.010723. So the stated column ratio is 8/6 of the six-bar value, and the stated beam ratio is 6/8 of the eight-bar value.
- Rule: when a source derives a quantity (ratio, area, mass) from a section, count the bars in that section's own calls and compare. Where they differ, convert the source's formula as written and report both values, naming the count the section uses.

### 101. A sub-model that looks like an earlier one can use other section offsets: read each source's section calls
- Evidence: on the same 500 x 500 mm column and 500 x 300 mm beam, the sensitivity source sets the middle column, the beam and the middle beam at Kfc - 0.05, - 0.10 and - 0.15; the optimisation source sets them at Kc - 0.15, - 0.10 and - 0.20. Reusing the optimisation's section list would have changed every section's confinement ratio silently.
- Rule: before reusing a section list, parameter set or helper from an earlier conversion, compare the calls of the new source with the earlier model line by line.

### 102. A source's label or printed value can name a different quantity than the array it uses: check each one
- Evidence: the source prints a Y-direction 'Ductility Ratio' as YY[2]/YY[1], where YY is the absolute axial force, not the ratio X[2]/X[1] of its Y fit. Its stiffness scatter plots label the x axis as lateral stiffness while plotting rotational stiffness there, and its step plots label moments in kN.mm for values in N.mm. The table column AXIAL_RIGIDITY holds the maximum absolute axial force, the same values as AXIAL_FORCE.
- Rule: check every printed value and axis label against the array it is applied to. The converted model computes each quantity from the array its name describes, and the README records each difference from the source.

### 103. opstool's SmartAnalyze log is written to the working folder, so the main process should run from output/
- Evidence: the scratch smoke test ran from its own output folder, and `.SmartAnalyze-OpenSees.log` appeared there next to the ODB files. The repository's .gitignore covers models/**/output/** only, so a log written to the model folder would be untracked.
- Rule: change into output/ before the first analysis of a model run whose analyses write logs to the working folder. The converted sensitivity model does this in its main block.

### 104. A single-case equilibrium check can miss isolated bad steps: check the base reactions against the load at every step, in every case
- Evidence: the optimisation sub-model's one-case check agreed at every step (1.5 x 10^-11 and 5.9 x 10^-11). The sensitivity grid's 25 pushovers show isolated steps in five cases where the base reactions depart from the applied load by up to 1.4 x 10^-3 of the largest load: 3.4 kN in the axial reaction at one step of the 28 mm, 1.25 case, and 64 N in the shear at a few neighbouring steps. The displacement-increment test (tolerance 10^-6) was met at those steps. Setting them to equilibrium changes the ductility and the over-strength factor by at most 1 x 10^-8, so the fits are not affected here.
- Rule: in each pushover's validation, compare the base reactions with the applied load at every step, report the largest departure and its step, and repeat the check for every case of a grid rather than for one. A convergence test on displacement increments does not bound the force error of a step.

## 2026-11-26 — SalarDelavar_Sensitivity_Cdepth_Confinement_Free_Vibration (2D fibre frame, pushover and free vibration grid)

### 105. A logarithmic decrement from every local maximum is undefined when a two-mode free decay has negative secondary peaks: report the count, and do not quote a value from a short record
- Evidence: the source's damping helper takes the log of the ratios of consecutive local maxima of node 3's displacement. In the free vibration of the 18 cases the maxima include 2 to 6 negative values (secondary peaks of the two-mode response), so the log of a negative ratio is undefined, and the port returns NaN in all 18 cases. Using only the positive peaks gives 1.5 to 7.2 %, over a 20 s record that holds two to three cycles of the first mode, so those values depend on the record length. The Rayleigh ratios as set (5 % and 3 %) are exact.
- Rule: before quoting a logarithmic decrement, count the peaks and their signs, and check that the record covers several cycles of the mode of interest. Report the NaN as it is, and check the damping against the Rayleigh coefficients.

### 106. A mass that is off by a factor 10^4 moves the shortest period by its square root (100), so the time step has to be checked under each reading
- Evidence: the source's element masses are 10^4 times the density of concrete per unit area. The shortest period of the lumped-mass frame is 0.110 to 0.118 s with them as written and 1.11 to 1.19 ms with the density of concrete, a ratio of about 100, while the first period differs by a factor of 46 to 48 because the nodal mass also differs (12000 against 12). The time step of 0.001 s resolves the shortest period 110 times as written, but only about once with the density reading.
- Rule: when a mass reading is uncertain, compute the shortest period under each reading before choosing the time step. This extends LESSON 71.

### 107. A case that two sub-models share is a cross-check of the shared conversion, and it must reproduce the same results
- Evidence: the case 500 mm, 28 mm, Kfc 1.25 of the seventh sub-model has the same frame and sections as the 28 mm, Kfc 1.25 case of the sixth. Both give a ductility of 5.738404, R 7.0480 and the same residual steps (8420 and 10746 to 10750), so the section code and the solver path agree across the two conversions.
- Rule: where two sub-models of one source share a case, compare that case between them before reporting either, and record the agreement.

## 2026-11-26 — SalarDelavar_Sensitivity_Cdepth_Free_Vibration_Parallel (parallel computing version of the seventh sub-model)

### 108. A source folder can list a script that imports a module the folder does not contain: check every import against the folder listing before converting
- Evidence: the source's `PARALLEL_COMPUTING` script imports `PLOT_2D` and calls `PLOT_2D_FRAME`, but its folder has no `PLOT_2D.py`, so the script cannot run from the folder as published. The conversion takes `PLOT_2D.py` from the seventh sub-model's `py_ref/`. The six helper files the folder shares with that sub-model are byte-identical to it, which supports the copy, and the README records which copy is used.
- Rule: before converting a script, list each `import` and check it against the folder listing. Where a module is missing, take it from the nearest sibling folder, record the copy used, and compare the files the two folders share.

### 109. A parallel version's main process holds no model, so its post-processing writes empty outputs that a conversion must not take as results
- Evidence: the source's parallel script calls `ops.printModel` and `PLOT_2D_FRAME` in its main process, after the jobs have run. In a fresh main process the model has no nodes and no elements, and `printModel` writes a 391-byte file with no model in it (checked with openseespy 3.8.0). The conversion does not reproduce those outputs, and its README says so.
- Rule: in a parallel or multi-process version, check which calls run in the main process and what model they see. A call on an empty model produces an empty output, which is not a result.

## 2026-11-26 — SalarDelavar_CQC_Response_Spectrum_Analysis (response spectrum analysis with CQC combination, 2D frame)

### 110. A source label can name another unit than the numbers beside it, and an unconverted mass can put the period outside the given spectrum: check both before choosing a reading
- Evidence: the source's spectrum plot labels Sa in g, but its values are in m/s2: the plateau 4.903 is 0.5 x 9.806, and 1.9612 and 3.72628 are 0.2 and 0.38 x 9.806. Its mass is labelled [kg] and used as written, which is 500000 N.s^2/mm per node; the first period is then 38.3 s, beyond the 6 s end of the spectrum. Reading the mass in kg (divided by 1000) and the spectrum in m/s2 (times 1000) gives a first period of 1.21 s, inside the range. The as-written run is kept as a check.
- Rule: check each label against its numbers (a plateau that is a round multiple of g in m/s2 shows the unit), and check that the implied period falls inside the given data before adopting a reading. State the adopted reading as a judgement for the user, and keep the literal result.

### 111. A variable reused for an output file name makes a source read the wrong quantity: trace which file each printed result comes from
- Evidence: the source assigns `filename` to three recorder files in turn, so when its TEST 00 and TEST 01 read the file, it is the beam's file (element 3), not the column's, while its docstring and its TEST 02 report the column base moment. Its TEST 01 prints the same values as TEST 00, because the list it reads is built from a file that still holds the TEST 00 rows first.
- Rule: when a source reuses a variable for output paths, find the file each read uses, and check each printed value against the quantity its label names. A repeated printed value is a finding to trace, not a confirmation.

### 112. A response-spectrum call over all modes stores no element response: read each mode with its own call
- Evidence: after `responseSpectrumAnalysis` without `-mode`, `eleResponse` returns -5.6 x 10^-7 N.mm for the column moment, in both the Path and the list forms, while the mode-by-mode calls return the mode responses (-1.5447 x 10^9 N.mm for mode 1 with the converted inputs). The source's all-modes values exist only in its recorder, which AGENT.md §4 forbids.
- Rule: after a combined analysis call, read the element response once to see what it stores. When the source relies on a recorder for per-mode values, convert to a per-mode loop with one ODB step per mode.

### 113. A combination coefficient built on an eigenvalue ratio: check its argument against the formula, and check whether the affected modes take part
- Evidence: the source's CQC function passes b = lambda_i / lambda_j, a ratio of eigenvalues (omega^2), where the standard coefficient takes the frequency ratio omega_j / omega_i. The converted model keeps the source's function and checks the standard form. Both give 1.5446530596 x 10^9 N.mm here, because the second mode has no X participation (Gamma_2 = 0), so the error does not change this result.
- Rule: check a correlation or combination coefficient's argument against its published formula. Where the argument is wrong, check which modes take part: if none of the affected pairs do, the error has no effect on the result, and the README should say so.

### 114. A linear modal calculation runs no solver iteration, so the source's solver setup need not be carried over: state the exception to the SmartAnalyze rule
- Evidence: the source sets constraints, numberer, system, test, algorithm, integrator and analysis("Static") before its modal and spectrum calls. A probe with the analysis object set and without it gave the same column moment to 1 x 10^-15 (relative). AGENT.md §10 lists one exception, for LoadControl gravity, and none for this calculation, so the conversion calls no ops.analyze, takes one ODB step per mode, and records the choice in the README for the user to confirm.
- Rule: before carrying over a source's solver setup, check whether the command iterates at all. Where it does not, leave the setup out, and state in the README that SmartAnalyze does not apply.

## 2026-11-26 — SalarDelavar_Creep_And_Shrinkage_Analysis (creep and shrinkage of a 2D RC frame under a time-scaled load)

### 115. A Linear load series advanced by a LoadControl time step scales the load with the analysis time: check the load factor against the stated loads before reading the response
- Evidence: the source's loads sit on a Linear time series, and its analysis advances the time with LoadControl steps of 25 days, so the load factor is the analysis time, 28 + 25n. At every step the base shear and axial force equal 2 N and 20 kN times that factor, so the stated 10 kN per node has grown to 1853 times its value at 5 years, and the concrete passes its compressive strain limit from day 203.
- Rule: for a time-dependent analysis, check the load factor against the stated loads at each step before reading the response. A load that scales with the analysis time is a modelling choice to state and check, not a default.

### 116. A helper that receives an argument and overrides it: reproduce the source's printed values to find which value it used
- Evidence: the source's section function takes Kfc as an argument, but its first lines set Kfc = 1.2, so the beam's call (1.1) has no effect. The source's printed values are reproduced exactly only with 1.2 for the beam, which confirms what the function does. The conversion uses the named value and keeps a check run at 1.2 that reproduces the source to 1 x 10^-9.
- Rule: check that each argument a helper receives is used. Where a call's value and the helper's computed value differ, reproduce the source to see which one it used, then state the value adopted and its effect.

### 117. A first analysis whose return code is not tested can carry an unconverged state forward: give every analysis the same convergence check
- Evidence: the source does not test its first analysis, at the creep age (load factor 28). With the beam at Kfc 1.1 that analysis returns -3 on OpenSees' default test, and the steps that follow start from it. The conversion gives it the source's fallback ladder, which converges on the first attempt. The check run (Kfc 1.2) converges on the default test and matches the source exactly, so the added check changes nothing where the source converges.
- Rule: test the return code of every analysis, including the first, and record the attempts. Keep a check run that follows the source's path, to show that the added check changes nothing where the source converges.

### 118. A corotational analysis applies loads at deformed positions: a moment check about the origin must use the displaced positions of the loaded nodes
- Evidence: with the loads at their undeformed positions, the moment balance about the origin has a relative residual of 5.8 x 10^-5 in every run. With the loaded nodes at their displaced positions (node 3 at (u_3x, 3000 + u_3y) and node 4 at (7000 + u_4x, 3000 + u_4y)) the residual is 5 x 10^-13. The difference is the moment of each vertical load through its node's sideways displacement.
- Rule: for a large-displacement analysis (corotational or P-delta), check moment equilibrium with the displacements of the loaded nodes. Report the undeformed residual as a displacement effect, not as an error.
