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
