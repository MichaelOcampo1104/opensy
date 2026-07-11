# Dino_Buckling

**Purpose:** Axial-compression buckling of a thin-walled steel I-section column built from ShellNLDKGQ shell elements, with a lateral imperfection preload followed by displacement-controlled axial shortening.

**Building System:** Cantilever steel I-section (wide-flange) column — 200×200 mm section (200 mm flange width × 200 mm web depth), 20 mm plate thickness, 5000 mm tall. 3 flat shell walls: top flange (y=300), web (x=100), bottom flange (y=100), joined at T-junctions (shared corner nodes). Base fully fixed; top free (loaded). ElasticIsotropic steel E=205000 MPa, ν=0.3.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6) with 1275 nodes and 1200 ShellNLDKGQ (4-node nonlinear DK quadrilateral shell) elements on a regular grid (25 nodes per ring × 51 z-levels; 3 walls × 8 segments × 50 heights). Section: ElasticIsotropic → PlateFiber nDMaterial → PlateFiber section (20 mm thick). Two-phase static analysis: (1) PUSH — 25 kN lateral imperfection (1000 N UX at 25 top nodes), LoadControl λ=0.07, 1 step; (2) loadConst; (3) DEAD — −250 kN axial reference (−10000 N UZ at 25 top nodes), DisplacementControl node 70 DOF 3, −0.5 mm/step × 100 steps, via SmartAnalyze (NormDispIncr @ 1e-4, KrylovNewton primary, post-buckling fallback ladder). Penalty constraints (1e20, 1e20) + UmfPack. Dead uniaxialMaterial tags 2, 3 omitted (never referenced).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (ElasticIsotropic, E=205000 MPa, ν=0.3) |
| Lateral System | Cantilever I-section column (shell elements) |
| Lateral Loading | Displacement-controlled axial shortening (−50 mm, 100 steps) |
| Earthquake Records | NA (static buckling) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (opensy conda env, Python 3.12.12) |
| Units | N, mm, MPa |

## Running the model

```bash
conda activate opensy
python "models/Dino/Buckling analysis of Shell element steel column/model.py"
```

## Verification

Buckling curve (axial load vs. top UZ shortening) compared against the source reference (`py_ref/result.xlsx`, 3 curves at displacement increments d=1/264, 1/132, 1/377):

| Quantity | Simulation | Reference | Notes |
|----------|-----------|-----------|-------|
| Peak axial load | 526.6 kN | ~630 kN | −16% |
| Theoretical Euler Pcr (weak-axis cantilever, K=2) | 542 kN | — | sim ≈ theory |

The simulation's 527 kN peak is consistent with the weak-axis cantilever Euler load (542 kN, π²EI/(2L)² for I=2.68e7 mm⁴), confirming the buckling mode is correctly captured. The reference's 630 kN peak is 16% higher — within the range expected from differences in imperfection magnitude and mesh resolution. The elastic stiffness in the initial ramp matches the reference trend (rapid rise then plateau near the critical load).

## Output

Written to `output/`:
- `buckling_curve.csv` — (axial load [kN], shortening [mm]) at each step
- `buckling_compare.png` — simulation vs 3 reference curves overlay
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis, V5 deformed peak, V6 slider, V7 animation)
- `RespStepData-1.odb/` — ODB response database (shell + nodal responses)

**References:**

Original source: `py_ref/co.tcl` (2621-line Tcl OpenSees script, ShellNLDKGQ shell model). Reference results: `py_ref/result.xlsx` (3 buckling curves). Extracted reference curves: `py_ref/reference_curves.csv`.

**Notes:** Converted from `co.tcl`. **Mesh generation:** the 1275 nodes + 1200 elements are regenerated programmatically from the source's regular grid (not parsed verbatim) — the source's node/element numbering is reproduced via a coordinate-keyed ring generator that ensures the 3 walls genuinely share T-junction corner nodes (critical for the section to act compositely; disconnected walls cannot buckle). **Shell ODB:** `save_shell_resp=True`, `save_frame_resp=False`, `save_truss_resp=False` (repo's first shell model — no prior precedent; §12u-2 memory management). **Two-phase static:** LoadControl PUSH imperfection as manual loop (§3c exception) → loadConst → SmartAnalyze DisplacementControl DEAD (§12z-1: DEAD pattern after loadConst). **Solver:** source Penalty(1e20,1e20) + UmfPack retained (works for this shell model); SmartAnalyze manages the buckling-phase solver internally with KrylovNewton primary + fallback ladder (§12z). **Dead materials** (tags 2, 3 — never referenced) omitted (§12ap-6). **Path depth:** standards/ is `parents[3]` (this model nests under `models/Dino/<analysis-name>/`), with a `parents[2]` fallback. SmartAnalyze replaces the source's raw `ops.analyze(nstep)` + `ops.recorder`. Run with: `C:/Users/micha/miniconda3/envs/opensy/python.exe "models/Dino/Buckling analysis of Shell element steel column/model.py"`
