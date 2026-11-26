# SalarDelavar_Sensitivity_Confinement_Enhancement_Ratio_Rebar

**Purpose:** Sensitivity of the pushover response of a 2D reinforced-concrete portal frame to the column rebar diameter and the confinement enhancement ratio, over the source's 5 x 5 grid. For each of the 25 cases the model gives the displacement ductility ratio, the over-strength factor, the behaviour coefficient R and the stiffnesses of the bilinear fit of the base shear. Sixth of the seven sub-models of the source folder `CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO`.

**Building System:** A single-storey, single-bay portal frame with both bases fixed, with the geometry of the optimisation sub-model. The columns are 3 m high and 500 x 500 mm, with 50 mm cover and six bars. The beam spans 7 m between the column axes and is 500 mm wide and 300 mm deep, with 50 mm cover and eight bars. The column rebar diameter DIAc is 20, 22, 28, 30 or 32 mm; the beam bars are DIAc - 4 mm. The confinement enhancement ratio Kfc is 1.15, 1.20, 1.25, 1.30 or 1.35 for the column section. The other sections take Kfc - 0.05 (middle column), Kfc - 0.10 (beam) and Kfc - 0.15 (middle beam), as the source's calls give them (Note 7).

**Model Description:** 2D model with three DOFs per node (ndm = 2, ndf = 3) and ten nodes. Nine corotational `nonlinearBeamColumn` elements with 10 integration points. Each section has its own materials, as in the source: Concrete01 for the confined core and for the unconfined cover, and Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa). The fibres form patches of 40 fibres along the depth and 1 fibre across the width (Note 2). Each case is one pushover: horizontal displacement control of node 4 (DOF 1) from 0 to 675 mm in 0.05 mm steps (13,500 steps), with SmartAnalyze (NormDispIncr, tolerance 1 x 10^-6, 5000 iterations, algorithm order 10, 41, 40, 20, 50, 60; Note 4). The reference load is 1 N horizontal and -1 N vertical at nodes 3 and 4. Recorded at each step: load factor, node-3 displacements and rotation, base reactions (sum over both bases) and the stiffness ratios KS, KA and KI.

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Concrete01 (f'c = 25 MPa; core confined by the ratio, cover unconfined); Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa, as written) |
| Lateral System | Portal frame (two fixed-base columns and one beam) with the confinement ratios above |
| Lateral Loading | Monotonic pushover (horizontal displacement control of node 4 to 675 mm), 25 cases of the grid |
| Earthquake Records | None used. The source's records are in `ground_motions/`, but its dynamic branch is never called (Note 11). |
| Design Year | NA |
| File Format | .py (source: `py_ref/SENSITIVITY_CONFINEMENT_ENHANCEMENT_RATIO_&_REBAR.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 (the project's `.venv`) |
| Units | N, mm, MPa (time in s) |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO/SENSITIVITY_CONFINEMENT_ENHANCEMENT_RATIO_%26_REBAR (Salar Delavar Ghashghaei). `py_ref/` holds the source main, its helpers (`CONCRETE_SECTION_FUN_TWO.py`, `ANALYSIS_FUNCTION.py`, `BILINEAR_CURVE.py`, `PLOT_2D.py`, `SALAR_MATH.py`) and the reference figure `COVER.png`. The source's PDF and PowerPoint are not copied or parsed.

**Validation:** `output/validation.txt`, from the final run of this folder:
TBD_VALIDATION

**Notes:**
1. **Corotational transformation.** As in the other sub-models, the pushovers use the source's corotational transformation.
2. **Fibre mesh.** The source's 40 fibres along the depth of each patch (NUMFIBERS) are kept. Its 5 fibres across the width are reduced to 1. The concrete law is one-dimensional, so the in-plane response does not depend on how the width is divided (LESSON 87). TBD_MESH
3. **Parallel processes.** The 25 pushovers run three at a time, each in its own process and from its own working folder under `output/.work`. opstool's `set_odb_path` removes the `.opstool.output` folder of the working folder, and that folder is fixed when opstool is imported, so processes that share a folder fail with PermissionError (LESSON 85). Each completed case is saved at once to `output/cases/` (LESSON 88).
4. **Solver.** The source's pushover branch calls no `ops.test`. `ANALYSIS_FUNCTION.py` sets a test and a fallback ladder of algorithms only when a step fails. The conversion sets NormDispIncr in SmartAnalyze from the first step, with the algorithm order 10, 41, 40, 20, 50, 60 (Newton first), as in the optimisation sub-model. The converged values may differ from the source's by the solver tolerance.
5. **Grid and last case.** The source loops over DIAc (20, 22, 28, 30 and 32 mm) outside and Kfc (1.15 to 1.35) inside: 25 cases. Its plots and exports use the variables of its last call, the case of 32 mm and Kfc 1.35. The converted model runs that case again in the main process for its figures, `model_info.json` and the deformed-shape view, and checks that it agrees with the grid run (LESSON 86). TBD_LAST
6. **Reinforcement ratios.** The source reports RO_COL = 8 A_bar,col / (Hc Bc) and RO_BE = 6 A_bar,beam / (Hb Bb). Its column section has six bars (three on each face) and its beam eight (three, two and three), so each reported ratio counts the other member's bar number: the column ratio is 8/6 of the six-bar value, and the beam ratio is 6/8 of the eight-bar value (LESSON 91). The table keeps the source's formulas and the sections keep the source's bar layers. At 20 mm column rebar, RO_COL is 0.010053 as reported (0.007540 for six bars) and RO_BE is 0.008042 as reported (0.010723 for eight bars).
7. **Section offsets.** The sections of the other two fibre sections take Kfc - 0.05 (middle column), Kfc - 0.10 (beam) and Kfc - 0.15 (middle beam). The optimisation sub-model uses Kc - 0.15, - 0.10 and - 0.20 on the same geometry, so its section list was not reused (LESSON 92).
8. **Bar diameters.** The beam bars are 4 mm smaller than the column bars (the source's DIAb = DIAc - 4): 16 to 28 mm for column bars of 20 to 32 mm.
9. **Table columns.** The source's Excel table (its DATA_TOTAL) is written as `output/sensitivity_results.csv`, because openpyxl is not in the environment. Its column AXIAL_RIGIDITY holds the maximum absolute axial force, the same values as AXIAL_FORCE, so the name does not match its content. ROTATIONAL_ST, LATERAL_ST_X and LATERAL_ST_Y are the maxima of KI, KS and KA.
10. **Restart.** Each completed case is saved as `output/cases/<case>.npz` at once, and a run that is interrupted continues with the missing cases after removing the ODB files of the incomplete ones (LESSON 88). Delete `output/cases/` to recompute the grid.
11. **Dynamic branch and records.** The source's `PD_ANALYSIS` also has a transient branch (an HHT integrator, Rayleigh damping from its two lowest modes and a Path ground motion from `Ground_Acceleration_X.txt` and `_Y.txt`), but no statement calls it with `ANA_KIND='DYNAMIC'`. It is not converted (LESSON 84). The two records are kept in `ground_motions/` and are not used.
12. **Source labels and printed values.** The source prints a Y-direction "Ductility Ratio" as YY[2]/YY[1], where YY is the absolute axial force, not the ratio of its Y fit. This model reports the Y fit's ductility mu = X[2]/X[1] and R from the source's Y formulas (`sensitivity_results.txt`). The source's stiffness scatter plots label the x axis as lateral stiffness while they plot rotational stiffness, and its moment axes say kN.mm for values in N.mm. The figures here follow the data (LESSON 93).
13. **Not converted.** `PLOT_2D_FRAME` (in `PLOT_2D.py`) is not run; the deformed shape of the last case is `vis_05_deformed_last_case.html`. `SALAR_MATH.py` is not imported by the source's main. The source's PDF and PowerPoint are not parsed. The source's printed text is written to `output/sensitivity_results.txt`, and its 3D plots to `output/surface_*.png`.

**Outputs** (in `output/`, git-ignored): `sensitivity_results.csv` (the source's table over the 25 cases), `sensitivity_results.txt` (the last case's bilinear fits and the ranges of the grid), `cases/*.npz` (each case's summary and step arrays), `pushover_last_case.csv` (13,500 steps of the last case), `validation.txt`, `model_info.json` (the model at the last case), the figures `last_case_curves.png`, `last_case_steps.png`, `last_case_stiffness.png`, `last_case_bilinear.png`, the ten 3D surfaces `surface_*.png` and `correlation_heatmap.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_last_case.html` and `vis_08_pushover_last_case.html`, and the ODBs `RespStepData-*.odb` with their `ModelData-*.zarr` folders for the 25 cases and the last case.

**References:** The source repository (see Source above).

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Sensitivity_Confinement_Enhancement_Ratio_Rebar
PYTHONUTF8=1 python model.py
```
TBD_RUNTIME
