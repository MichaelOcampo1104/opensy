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

**Results:** Ductility ratio mu and behaviour coefficient R = Omega_0 mu of each case, from `output/sensitivity_results.csv` (the source's formulas). Rows are the column rebar diameter, columns the confinement enhancement ratio Kfc.

Ductility mu:

| DIAc (mm) \ Kfc | 1.15 | 1.20 | 1.25 | 1.30 | 1.35 |
|---|---|---|---|---|---|
| 20 | 6.069 | 6.046 | 6.024 | 6.004 | 5.984 |
| 22 | 6.021 | 5.999 | 5.978 | 5.958 | 5.939 |
| 28 | 5.772 | 5.755 | 5.738 | 5.723 | 5.707 |
| 30 | 5.669 | 5.654 | 5.640 | 5.627 | 5.613 |
| 32 | 5.564 | 5.551 | 5.538 | 5.527 | 5.515 |

R:

| DIAc (mm) \ Kfc | 1.15 | 1.20 | 1.25 | 1.30 | 1.35 |
|---|---|---|---|---|---|
| 20 | 7.003 | 6.960 | 6.920 | 6.882 | 6.846 |
| 22 | 7.097 | 7.054 | 7.014 | 6.976 | 6.939 |
| 28 | 7.123 | 7.084 | 7.048 | 7.013 | 6.979 |
| 30 | 7.067 | 7.033 | 6.999 | 6.967 | 6.936 |
| 32 | 6.992 | 6.961 | 6.931 | 6.902 | 6.873 |

Ductility falls along every row and every column: the larger the column rebar and the confinement ratio, the lower the ductility. R peaks at 28 mm column rebar (7.12 at Kfc 1.15) and lies between 6.87 and 7.12 over the grid. The last case (32 mm, Kfc 1.35) has mu = 5.515, Omega_0 = 1.2463 and R = 6.8732. Its bilinear fit yields at X = 125.7 mm and Y = 2.61 MN and ends at X = 693.4 mm and Y = 3.25 MN; its elastic, plastic and tangent stiffnesses are 20,763, 4,692 and 1,133 N/mm (`output/sensitivity_results.txt`). The source's Y-direction formulas, applied to the axial force against the vertical displacement, give mu = 9.07 and R = 1.39 for the same case; they are reported as the source computes them.

**Validation:** `output/validation.txt`, from the final run of this folder:
- **Element check.** In every case the gross force-based column element agrees with the textbook frame element to 1.2 x 10^-15 to 1.9 x 10^-15 (relative).
- **First step.** In every case OpenSees and numpy agree on the first load factor to 6.2 x 10^-5 to 9.3 x 10^-5 (four or five section-state iterations, 10 Lobatto points), the same order as the optimisation sub-model (6.6 x 10^-5).
- **Equilibrium.** At every step the base shear and the axial reaction match the applied loads (2 lambda). In 20 cases the largest departure is below 10^-4 of the largest load. The other five are 28 mm at Kfc 1.20 and 1.25, 30 mm at 1.35, and 32 mm at 1.15 and 1.25; in each, one or two steps lie above 10^-4, and at most 11 steps in any case exceed 10^-6. The largest is 1.4 x 10^-3 (3.4 kN in the axial reaction, at step 8420 of the 28 mm, 1.25 case): steps that the displacement-increment test accepted with a force imbalance, which was not isolated further. Setting the affected steps to equilibrium changes the ductility and the over-strength factor of every case by at most 1 x 10^-8 (relative), so the reported values do not depend on them (LESSON 104).
- **Completed.** 25 of 25 cases, 13,500 steps each, with no non-finite stiffness values.
- **Last case.** Run again in the main process, its base shear agrees with its grid run exactly (relative difference 0).
- **Mesh.** See Note 2.
- **Not validated.** The bilinear fits, Omega_0, mu and R are the source's formulas, ported, and are reported rather than checked against an independent solution.

**Notes:**
1. **Corotational transformation.** As in the other sub-models, the pushovers use the source's corotational transformation.
2. **Fibre mesh.** The source's 40 fibres along the depth of each patch (NUMFIBERS) are kept. Its 5 fibres across the width are reduced to 1. The concrete law is one-dimensional, so the in-plane response does not depend on how the width is divided (LESSON 87). The check for the first case (column 20 mm, Kfc 1.15, all 13,500 steps) gives a ductility of 6.069219674 with 1 fibre and 6.069219665 with 5 fibres (relative difference 1.4 x 10^-9), and R of 7.00271866 and 7.00271864 (relative difference 2.9 x 10^-9). Over the steps, relative to each response's largest value, the differences are 1.5 x 10^-4 for the node-3 vertical displacement, 7.7 x 10^-5 for the axial force, 3.0 x 10^-5 for the shear force, 5.2 x 10^-6 or less for the load factor, 2.9 x 10^-6 or less for the moment and 2.0 x 10^-6 or less for the rotation, and 9 x 10^-8 for the node-3 horizontal displacement. These are larger than rounding: the two meshes take slightly different iterations to meet the solver's displacement tolerance (10^-6), which was not isolated further.
3. **Parallel processes.** The 25 pushovers run three at a time, each in its own process and from its own working folder under `output/.work`. opstool's `set_odb_path` removes the `.opstool.output` folder of the working folder, and that folder is fixed when opstool is imported, so processes that share a folder fail with PermissionError (LESSON 85). Each completed case is saved at once to `output/cases/` (LESSON 88).
4. **Solver.** The source's pushover branch calls no `ops.test`. `ANALYSIS_FUNCTION.py` sets a test and a fallback ladder of algorithms only when a step fails. The conversion sets NormDispIncr in SmartAnalyze from the first step, with the algorithm order 10, 41, 40, 20, 50, 60 (Newton first), as in the optimisation sub-model. The converged values may differ from the source's by the solver tolerance.
5. **Grid and last case.** The source loops over DIAc (20, 22, 28, 30 and 32 mm) outside and Kfc (1.15 to 1.35) inside: 25 cases. Its plots and exports use the variables of its last call, the case of 32 mm and Kfc 1.35. The converted model runs that case again in the main process for its figures, `model_info.json` and the deformed-shape view, and checks that it agrees with the grid run (LESSON 86). Its base shear agrees with its grid run exactly (relative difference 0).
6. **Reinforcement ratios.** The source reports RO_COL = 8 A_bar,col / (Hc Bc) and RO_BE = 6 A_bar,beam / (Hb Bb). Its column section has six bars (three on each face) and its beam eight (three, two and three), so each reported ratio counts the other member's bar number: the column ratio is 8/6 of the six-bar value, and the beam ratio is 6/8 of the eight-bar value (LESSON 100). The table keeps the source's formulas and the sections keep the source's bar layers. At 20 mm column rebar, RO_COL is 0.010053 as reported (0.007540 for six bars) and RO_BE is 0.008042 as reported (0.010723 for eight bars).
7. **Section offsets.** The other sections take Kfc - 0.05 (middle column), Kfc - 0.10 (beam) and Kfc - 0.15 (middle beam), as the source's calls give them. The optimisation sub-model uses Kc - 0.15, - 0.10 and - 0.20 on the same geometry, so its section list was not reused (LESSON 101).
8. **Bar diameters.** The beam bars are 4 mm smaller than the column bars (the source's DIAb = DIAc - 4): 16 to 28 mm for column bars of 20 to 32 mm.
9. **Table columns.** The source's Excel table (its DATA_TOTAL) is written as `output/sensitivity_results.csv`, because openpyxl is not in the environment. Its column AXIAL_RIGIDITY holds the maximum absolute axial force, the same values as AXIAL_FORCE, so the name does not match its content. ROTATIONAL_ST, LATERAL_ST_X and LATERAL_ST_Y are the maxima of KI, KS and KA.
10. **Restart.** Each completed case is saved as `output/cases/<case>.npz` at once, and a run that is interrupted continues with the missing cases after removing the ODB files of the incomplete ones (LESSON 88). Delete `output/cases/` to recompute the grid.
11. **Dynamic branch and records.** The source's `PD_ANALYSIS` also has a transient branch (an HHT integrator, Rayleigh damping from its two lowest modes and a Path ground motion from `Ground_Acceleration_X.txt` and `_Y.txt`), but no statement calls it with `ANA_KIND='DYNAMIC'`. It is not converted (LESSON 84). The two records are kept in `ground_motions/` and are not used.
12. **Source labels and printed values.** The source prints a Y-direction "Ductility Ratio" as YY[2]/YY[1], where YY is the absolute axial force, not the ratio of its Y fit. This model reports the Y fit's ductility mu = X[2]/X[1] and R from the source's Y formulas (`sensitivity_results.txt`). The source's stiffness scatter plots label the x axis as lateral stiffness while they plot rotational stiffness, and its moment axes say kN.mm for values in N.mm. The figures here follow the data (LESSON 102).
13. **Not converted.** `PLOT_2D_FRAME` (in `PLOT_2D.py`) is not run; the deformed shape of the last case is `vis_05_deformed_last_case.html`. `SALAR_MATH.py` is not imported by the source's main. The source's PDF and PowerPoint are not parsed. The source's printed text is written to `output/sensitivity_results.txt`, and its 3D plots to `output/surface_*.png`.
14. **Node 3 is not controlled.** The pushover controls node 4 only. Node 3 lags node 4 during the first 200 mm (by 3.7 to 9.4 mm, depending on the case) and then overtakes it, ending 3.0 to 19.6 mm beyond the control (the optimisation sub-model ends 0.6 mm beyond it). The vertical loads are as large as the horizontal ones, so the beam between the two top nodes carries axial force and shortens or lengthens; that is the difference between the nodes. The beam's axial force is not in the outputs, so this was not isolated further.

**Outputs** (in `output/`, git-ignored): `sensitivity_results.csv` (the source's table over the 25 cases), `sensitivity_results.txt` (the last case's bilinear fits and the ranges of the grid), `cases/*.npz` (each case's summary and step arrays), `pushover_last_case.csv` (13,500 steps of the last case), `validation.txt`, `model_info.json` (the model at the last case), the figures `last_case_curves.png`, `last_case_steps.png`, `last_case_stiffness.png`, `last_case_bilinear.png`, the ten 3D surfaces `surface_*.png` and `correlation_heatmap.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_last_case.html` and `vis_08_pushover_last_case.html`, and the ODBs `RespStepData-*.odb` with their `ModelData-*.zarr` folders for the 25 cases and the last case.

**References:** The source repository (see Source above).

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Sensitivity_Confinement_Enhancement_Ratio_Rebar
PYTHONUTF8=1 python model.py
```
The run took about 27 minutes on this machine (09:28 to 09:55): the 25 pushovers, three at a time, then the last case and the post-processing (about 1.5 minutes). The 5-fibre check of Note 2 ran alongside from 09:38 to 09:48 and slowed the grid during that time, so the timing is not comparable with a run on an idle machine (LESSON 89).
