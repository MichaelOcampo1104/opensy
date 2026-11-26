# SalarDelavar_Optimization_Confinement_Enhancement_Ratio

**Purpose:** Finds the column confinement enhancement ratio of the 2D reinforced-concrete frame of the first sub-model at which its structural ductility ratio is 5.5 (the source's `TARGET_DUCT`), by the source's Newton iteration on the pushover ductility. The pushover at that ratio then gives its over-strength factor and behaviour coefficients. Fifth sub-model of the source folder `CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO`, which holds seven sub-models.

**Building System:** The frame of the first sub-model: a single-storey, single-bay portal frame with both bases fixed. The columns are 3 m high and 500 x 500 mm, with 50 mm cover and six 25 mm bars. The beam spans 7 m between the column axes and is 500 mm wide and 300 mm deep, with 50 mm cover and eight 18 mm bars. The column confinement enhancement ratio is the search variable X (the source's Kc). The other sections keep the source's offsets: the middle column X - 0.15, the beam X - 0.1 and the middle beam X - 0.2. At the optimum X* = 2.147387 these are 2.147387, 1.997387, 2.047387 and 1.947387.

**Model Description:** 2D model with three DOFs per node (ndm = 2, ndf = 3) and ten nodes. Nine corotational `nonlinearBeamColumn` elements with 10 integration points. Each section has its own materials, as in the source: Concrete01 for the core and the cover, and Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa). The fibres form patches of 40 fibres along the depth and 1 fibre across the width (Note 2). Analyses, all pushovers:
1. Search: the source's Newton iteration on F(X) = mu(X) - 5.5, where mu is the ductility ratio of the bilinear fit of the pushover (slope node 10, as the source). The derivative is the central difference at X - ESP and X + ESP (ESP = 1 x 10^-5). Each iteration runs three pushovers, at X, X - ESP and X + ESP, in separate processes (Note 3). The search starts at X = 1.40 and stops when the Newton step |DX| is below 1 x 10^-6. It took five iterations (Note 6).
2. Optimum pushover: horizontal displacement control of node 4 (DOF 1) from 0 to 675 mm in 0.05 mm steps (13,500 steps) at X*, with SmartAnalyze (NormDispIncr, tolerance 1 x 10^-6, 5000 iterations, algorithm ladder 10, 41, 40, 20, 50, 60). The reference load is 1 N horizontal and -1 N vertical at nodes 3 and 4. Recorded at each step: load factor, node-3 displacements and rotation, base reactions (sum over both bases) and the stiffness ratios KS, KA and KI.

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Concrete01 (f'c = 25 MPa; core confined by the ratio, cover unconfined); Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa, as written) |
| Lateral System | Portal frame (two fixed-base columns and one beam) with the confinement ratios above |
| Lateral Loading | Monotonic pushover (horizontal displacement control of node 4 to 675 mm), repeated in each step of the search |
| Earthquake Records | None. The source's time history is defined but never called (Note 12). |
| Design Year | NA |
| File Format | .py (source: `py_ref/CONCRETE_FRAME_OPTIMIZATION_CONFINEMENT_ENHANCEMENT_RATIO.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 (the project's `.venv`) |
| Units | N, mm, MPa (time in s) |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO/OPTIMIZATION_CONFINEMENT_ENHANCEMENT_RATIO (Salar Delavar Ghashghaei). `py_ref/` holds the source main, its helpers (`CONCRETE_SECTION_FUN_TWO.py`, `ANALYSIS_FUNCTION.py`, `BILINEAR_CURVE.py`, `PLOT_2D.py`, `SALAR_MATH.py`) and the reference figure `COVER.png`. The source folder has no records and no damping or eigen helpers. The source's PDF and PowerPoint are not copied or parsed.

**Validation:** `output/validation.txt`, from the final run of this folder:
- **Element assembly.** The force-based element of the column section at X* reproduces the textbook frame element to 1.3 x 10^-15.
- **Section properties at X* (gross, initial tangents).** Column EA = 7.938 x 10^9 N and EI = 1.706 x 10^14 N.mm^2; beam EA = 4.620 x 10^9 N and EI = 3.344 x 10^13 N.mm^2.
- **First pushover step at X*.** OpenSees 303.0758 and numpy 303.0958 (relative difference 6.6 x 10^-5, with 4 iterations of the section states and 10 Lobatto points). The node-3 displacement is 0.04496392 mm (OpenSees) and 0.04496345 mm (numpy).
- **Equilibrium** over all 13,500 steps at X*: 1.5 x 10^-11 (horizontal) and 5.9 x 10^-11 (vertical).
- **Search.** Five iterations; the last Newton step is |DX| = 3.1 x 10^-8, and the ductility at X* is 5.5000000 (the difference from 5.5 is 2.6 x 10^-13).
- **Not validated:** the bilinear fit, the over-strength factor, the ductility and R are the source's formulas, ported, and are reported rather than checked against an independent solution.

**Notes:**
1. **Corotational transformation.** As in the other sub-models, the pushovers use the source's corotational transformation.
2. **Fibre mesh.** The source's 40 fibres along the depth of each patch (NUMFIBERS) are kept. Its 5 fibres across the width are reduced to 1. The concrete law is one-dimensional, so the in-plane response does not depend on how the width is divided. At X = 1.25 the ductility is 5.751466871648777 with 1 fibre across and 5.751466871638407 with 5 (a difference of 1 x 10^-11). The coarser mesh has about five times fewer fibres. Its pushovers took 48 to 90 s each (LESSON 87). The depth mesh was not coarsened, because that changes the results.
3. **Parallel processes.** The three pushovers of each search iteration run in separate processes, each from its own working folder under `output/.work`. opstool's `set_odb_path` removes a `.opstool.output` folder in the current folder, and the folder is fixed when opstool is imported, so processes that share a folder fail with PermissionError (LESSON 85). Each process returns the same values as a run on its own.
4. **Search algorithm.** The source's update is kept: F = mu - 5.5; DF = (F(X + ESP) - F(X - ESP)) / (2 ESP); DX = F / DF; X = X - DX; the residual is |DX|. The solver is SmartAnalyze, not the source's fallback ladder, so the converged value may differ from the source's by its solver tolerance. The source's own optimum is not written to its files, so it is not compared here.
5. **Trend.** The ductility falls as the confinement ratio rises. DF is negative in every iteration (-0.33 at X = 1.40, about -0.22 near the optimum), so the search raises X from 1.40 to 2.147 to reach 5.5. The first sub-model's Kc = 1.25 gives mu = 5.7515, which agrees with this trend.
6. **Iterations.** `search_history.csv` holds one row per iteration. The rows are:

| iteration | X | mu | F = mu - 5.5 | DF | DX | residual | X_new |
|---|---|---|---|---|---|---|---|
| 1 | 1.400000 | 5.6969465 | 1.969e-01 | -0.33328 | -5.909e-01 | 5.909e-01 | 1.990935 |
| 2 | 1.990935 | 5.5338287 | 3.383e-02 | -0.22855 | -1.480e-01 | 1.480e-01 | 2.138947 |
| 3 | 2.138947 | 5.5018387 | 1.839e-03 | -0.21812 | -8.430e-03 | 8.430e-03 | 2.147377 |
| 4 | 2.147377 | 5.5000022 | 2.235e-06 | -0.22018 | -1.015e-05 | 1.015e-05 | 2.147387 |
| 5 | 2.147387 | 5.5000000 | 6.813e-09 | -0.21954 | -3.103e-08 | 3.103e-08 | 2.147387 |

7. **Exported results.** The source's Excel export and its plots use the variables of the last pushover of its loop, which is at X + ESP in the last iteration, not the optimum. This conversion writes the pushover at the optimum instead (LESSON 86).
8. **Results at the optimum X* = 2.147387.** The ductility is 5.500000 and the over-strength factor Omega_0 = 1.1256, so R = Omega_0 mu = 6.1909. The bilinear fit gives X = 122.84 mm and 675.63 mm, and Y = 1.6548 MN and 1.8626 MN. Its elastic stiffness is 13,470.5 N/mm, its plastic stiffness 2,756.9 N/mm, and its post-yield tangent 376.0 N/mm (positive, so no softening).
9. **Node 3 and node 4.** The pushover controls node 4. At the end of the optimum pushover, node 3 is at 675.63 mm, 0.63 mm beyond the control.
10. **Restart.** Each completed iteration is written to `search_history.csv` at once. A run that is interrupted continues from the last completed iteration, and the ODB files of the incomplete iteration are removed first (LESSON 88).
11. **Dynamic branch.** The source's `PD_ANALYSIS` also defines a transient branch (an HHT integrator, Rayleigh damping from the two lowest modes and a Path ground motion), but no statement calls it. It is not converted (LESSON 84).
12. **Not converted.** The records and the Y-direction branches (the source folder has no records), `PLOT_2D.py` (not run), `SALAR_MATH.py` (not imported by the source's main), and the source's PDF and PowerPoint (not parsed). The source's printed text is written to `optimisation_results.txt`.
13. **Run time.** Each of the 16 pushovers (15 in the search and the optimum) took 48 to 90 s with SmartAnalyze. The whole run took about 10 minutes on this machine.

**Outputs** (in `output/`, git-ignored): `search_history.csv` (the Newton iterations), `optimisation_results.txt`, `pushover_optimum.csv` (13,500 steps, with the first sub-model's pushover column names), `validation.txt`, `model_info.json` (the OpenSees model at the optimum), the figures `pushover_curve.png` and `search_residual.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_optimum.html` and `vis_08_pushover.html`, and the ODBs `RespStepData-*.odb` with their `ModelData-*.zarr` folders for the fifteen search pushovers (`opt01_x` to `opt05_max`) and the optimum (`optimum_pushover`), about 45 MB in all.

**References:** The source repository (see Source above).

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Optimization_Confinement_Enhancement_Ratio
PYTHONUTF8=1 python model.py
```
