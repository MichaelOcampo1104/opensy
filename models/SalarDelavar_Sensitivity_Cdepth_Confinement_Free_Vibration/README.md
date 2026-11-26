# SalarDelavar_Sensitivity_Cdepth_Confinement_Free_Vibration

**Purpose:** Sensitivity of the pushover and free-vibration responses of a 2D reinforced-concrete portal frame to the column depth, the column rebar diameter and the confinement enhancement ratio, over the source's 18 cases (six column depths x three rebar diameters, at Kfc 1.25). For each case the model gives the displacement ductility ratio, the over-strength factor, the behaviour coefficient R and the stiffnesses of the bilinear fit of the pushover; and the peak responses, the first two periods, the Rayleigh coefficients and the logarithmic-decrement damping of the free vibration. Seventh and last sub-model of the source folder `CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO`.

**Building System:** A single-storey, single-bay portal frame with both bases fixed. The columns are 3 m high and 500 mm wide, with 50 mm cover and six bars (three on each face). Their depth Hc is 350, 400, 450, 500, 550 or 600 mm. The column rebar diameter DIAc is 28, 30 or 32 mm. The beam spans 7 m between the column axes and is 500 mm wide and 300 mm deep, with 50 mm cover and eight bars; its bars are DIAc - 4 mm (24, 26 or 28 mm). The confinement enhancement ratio Kfc is 1.25. The other sections take Kfc - 0.05 (middle column), Kfc - 0.10 (beam) and Kfc - 0.15 (middle beam), as the source's calls give them (Note 7).

**Model Description:** 2D model with three DOFs per node (ndm = 2, ndf = 3) and ten nodes. Nine corotational `nonlinearBeamColumn` elements with 10 integration points. Each section has its own materials, as in the source: Concrete01 for the confined core and for the unconfined cover, and Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa). The fibres form patches of 40 fibres along the depth and 1 fibre across the width (Note 2). The element masses and the nodal masses are the source's values as written (Note 11). Each case has two analyses, as in the source:
1. Pushover: horizontal displacement control of node 4 (DOF 1) from 0 to 675 mm in 0.05 mm steps (13,500 steps), with SmartAnalyze (NormDispIncr, tolerance 1 x 10^-6, 5000 iterations, algorithm order 10, 41, 40, 20, 50, 60; Note 4). The reference load is 1 N horizontal and -1 N vertical at nodes 3 and 4. Recorded at each step: load factor, node-3 displacements and rotation, base reactions (sum over both bases), drift and the stiffness ratios KS, KA and KI.
2. Free vibration of node 3 in X: an initial displacement 0.031 mm, an initial velocity 0.00015 mm/s and an initial acceleration 0.000065 mm/s^2 (committed), with a ramp load of 1 N at nodes 3 and 4 in X (a Linear pattern, so t N at time t, as in the source). Rayleigh damping from the two lowest modes, with ratios 5 % for mode 1 and 3 % (0.6 x 5 %) for mode 2, applied through the source's helper (its beta_K is the committed-stiffness coefficient, as in the other sub-models of this folder). Newmark (0.5, 0.25) with SmartAnalyze (transient, NormDispIncr, tolerance 1 x 10^-6, 5000 iterations, algorithm order 10, 41, 40, 20, 50). The time step is 0.001 s and the duration 20 s, so 20,000 steps. Recorded at each step: the node-3 displacements, rotation, velocities and accelerations, the base reactions, drift and the stiffness ratios.

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Concrete01 (f'c = 25 MPa; core confined by the ratio, cover unconfined); Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa, as written) |
| Lateral System | Portal frame (two fixed-base columns and one beam) with the column depths above |
| Lateral Loading | Monotonic pushover (horizontal displacement control of node 4 to 675 mm) and free vibration of node 3 from initial conditions under a ramp load; 18 cases |
| Earthquake Records | None. The source's free vibration has no ground motion. |
| Design Year | NA |
| File Format | .py (source: `py_ref/SENSITIVITY_CONFINEMENT_ENHANCEMENT_RATIO_&_REBAR_&_Cdepth_FREE_VIBRATION.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 (the project's `.venv`) |
| Units | N, mm, MPa (time in s) |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO/SENSITIVITY_CONFINEMENT_ENHANCEMENT_RATIO_%26_REBAR_%26_Cdepth_FREE_VIBRATION (Salar Delavar Ghashghaei). `py_ref/` holds the source main, its helpers (`CONCRETE_SECTION_FUN_TWO.py`, `ANALYSIS_FUNCTION.py`, `BILINEAR_CURVE.py`, `PLOT_2D.py`, `DAMPING_RATIO_FUN.py`, `RAYLEIGH_DAMPING_FUN.py`) and the figure `COVER.png`. The source's PDF and PowerPoint are not copied or parsed. The source folder's `PARALLEL_COMPUTING` variant (a second main script with a histogram helper) is not converted (Note 13).

**Results:** Pushover ductility mu, over-strength factor Omega_0 and R, and the first period of the free vibration, for each case (Kfc 1.25 throughout). Rows are the column depth Hc, columns the column rebar diameter. The values come from `output/pushover_results.csv`, `output/free_vibration_results.csv` and `output/cases/`.

Ductility mu:

| Hc (mm) \ DIAc (mm) | 28 | 30 | 32 |
|---|---|---|---|
| 350 | 5.138 | 5.056 | 4.962 |
| 400 | 5.248 | 5.161 | 5.068 |
| 450 | 5.460 | 5.366 | 5.268 |
| 500 | 5.738 | 5.640 | 5.538 |
| 550 | 6.060 | 5.956 | 5.850 |
| 600 | 6.422 | 6.312 | 6.201 |

Behaviour coefficient R = Omega_0 mu:

| Hc (mm) \ DIAc (mm) | 28 | 30 | 32 |
|---|---|---|---|
| 350 | 7.750 | 7.731 | 7.657 |
| 400 | 7.224 | 7.193 | 7.131 |
| 450 | 7.040 | 6.995 | 6.926 |
| 500 | 7.048 | 6.999 | 6.931 |
| 550 | 7.157 | 7.102 | 7.031 |
| 600 | 7.358 | 7.298 | 7.223 |

First period of the free vibration, with the masses as written (s):

| Hc (mm) \ DIAc (mm) | 28 | 30 | 32 |
|---|---|---|---|
| 350 | 10.290 | 10.135 | 9.976 |
| 400 | 9.123 | 8.987 | 8.848 |
| 450 | 8.177 | 8.057 | 7.934 |
| 500 | 7.384 | 7.278 | 7.169 |
| 550 | 6.708 | 6.614 | 6.517 |
| 600 | 6.125 | 6.042 | 5.956 |

Ductility rises with the column depth (4.96 to 6.42) and falls with the rebar diameter. The over-strength factor falls with depth, from 1.54 (350 mm, 32 mm) to 1.15 (600 mm, 28 mm), so R varies less than mu: from 6.93 to 7.75, the largest at 350 mm and 28 mm. The first period is 5.96 to 10.29 s with the masses as written (Note 11).

The last pushover (600 mm, 32 mm) has mu = 6.2006, Omega_0 = 1.1649 and R = 7.2228. Its bilinear fit yields at X = 111.9 mm and Y = 3.34 MN, and ends at X = 694.1 mm and Y = 3.89 MN; its elastic, plastic and tangent stiffnesses are 29,805, 5,599 and 945 N/mm (`output/sensitivity_results.txt`). Its free vibration has first and second periods of 5.956 s and 2.148 s.

The source's logarithmic-decrement damping is NaN in all 18 cases: node 3's displacement has 2 to 6 negative local maxima (secondary peaks of the two-mode response), and the helper takes the logarithm of their ratio (Note 10). A check outside the model that uses only the positive peaks gives 1.5 to 7.2 %, but the 20 s record holds only about two to three cycles of the first mode, so those values do not measure the damping. The Rayleigh ratios at the two periods are 5.0000 % and 3.0000 % in every case, as set.

**Validation:** `output/validation.txt`, from the final run of this folder:
- **Element check.** In every case the gross force-based column element agrees with the textbook frame element to 1.2 x 10^-15 to 1.9 x 10^-15 (relative).
- **First step.** In every case OpenSees and numpy agree on the first load factor to 7.7 x 10^-5 to 9.7 x 10^-5 (four or five section-state iterations), the same order as the sixth sub-model.
- **Equilibrium.** At every pushover step the base shear and the axial reaction match the applied loads (2 lambda). In 12 cases the largest departure is below 10^-4 of the largest load. In the other six it is confined to one or two steps above 10^-4, and at most 9 steps in any case exceed 10^-6. The largest, 1.4 x 10^-3 (3.4 kN in the axial reaction at step 8420 of the 500 mm, 28 mm case), is the same case and the same steps as the sixth sub-model's 28 mm, Kfc 1.25 case, whose pushover is identical. Setting the isolated steps to equilibrium changes the ductility and the over-strength factor by at most 4.2 x 10^-8 (relative), so the reported values do not depend on them (LESSON 104).
- **Periods at t = 0.** With the masses as written, OpenSees and numpy agree on both periods to within 1.2 x 10^-5 (relative), and the Rayleigh ratios at those periods are 5.0000 % and 3.0000 %.
- **Time step.** With the masses as written the shortest period of the frame is 0.110 to 0.118 s, so the step of 0.001 s resolves it 110 to 118 times. With the other reading the shortest period is 1.11 to 1.19 ms and the step resolves it only about 1.1 times (Note 11).
- **Completed.** 18 of 18 cases, 13,500 pushover steps and 20,000 free-vibration steps each, with no non-finite stiffness values.
- **Last pushover.** Its base shear agrees with its grid run exactly (relative difference 0).
- **Cross-check.** The case 500 mm, 28 mm, Kfc 1.25 has the same pushover as the sixth sub-model's 28 mm, Kfc 1.25 case (ductility 5.738404 and R 7.0480 in both, with the same residual steps), as expected for the same geometry and sections.
- **Mesh.** See Note 2.
- **Not validated.** The bilinear fits, Omega_0, mu, R and the source's logarithmic decrement are the source's formulas, ported (Note 10).

**Notes:**
1. **Corotational transformation.** As in the other sub-models, the analyses use the source's corotational transformation.
2. **Fibre mesh.** The source's 40 fibres along the depth of each patch are kept. Its 5 fibres across the width are reduced to 1, as in the sixth sub-model of this folder: the concrete law is one-dimensional, so the width division does not change the section response (LESSON 87). The 5-fibre check for this model, on the case 500 mm, 28 mm, Kfc 1.25 over all 13,500 steps, gives a ductility of 5.738404350 with 1 fibre and 5.738404308 with 5 fibres (relative difference 7.3 x 10^-9), and R of 7.047996654 and 7.047996551 (relative difference 1.5 x 10^-8). Over the steps, relative to each response's largest value, the differences are 3.0 x 10^-4 for the axial force, 6.2 x 10^-5 for the shear force, 4.4 x 10^-5 for the moment, 3.7 x 10^-5 for the load factor, and below 10^-5 for the displacements and rotation. As in the sixth sub-model, these are larger than rounding: the two meshes take slightly different iterations to meet the solver's displacement tolerance (10^-6), which was not isolated further.
3. **Parallel processes.** The 18 cases run three at a time, each in its own process and from its own working folder under `output/.work`. opstool's `set_odb_path` removes the `.opstool.output` folder of the working folder, which is fixed when opstool is imported, so processes that share a folder fail (LESSON 85). Each completed case is saved at once to `output/cases/` (LESSON 88).
4. **Solver.** The source's pushover branch calls no `ops.test`, and its free-vibration branch sets NormDispIncr and Newton directly. The conversion manages both in SmartAnalyze (the pushover with the source's fallback order from Newton, and the transient with Newton first, as in the ductility sub-model of this folder). The converged values may differ from the source's by the solver tolerance.
5. **Grid and last case.** The source loops over the column depth Hc (350 to 600 mm) outside, the rebar diameter (28, 30, 32 mm) inside, and Kfc (1.25). Its plots and its last exports use the last pushover, the case of 600 mm and 32 mm. The converted model runs that pushover again in the main process for its figures, `model_info.json` and the deformed-shape view, and checks that it agrees with the grid run exactly (LESSON 86).
6. **Reinforcement ratios.** The source reports RO_COL = 100 x 8 A_bar,col / (Hc Bc) and RO_BE = 100 x 6 A_bar,beam / (Hb Bb), in percent. Its column section has six bars and its beam eight, so each reported ratio counts the other member's bar number (LESSON 100). The table keeps the source's formulas, and the RO_BE values depend on the rebar diameter alone. For 28 mm column rebar and Hc 500 mm, RO_COL is 1.970 % as reported (1.478 % for six bars) and RO_BE is 1.810 % as reported (2.413 % for eight bars).
7. **Section offsets.** The other sections take Kfc - 0.05, Kfc - 0.10 and Kfc - 0.15, as the source's calls give them. The optimisation sub-model uses different offsets on the same geometry, so its section list was not reused (LESSON 101).
8. **Bar diameters.** The beam bars are 4 mm smaller than the column bars, as in the source's DIAb = DIAc - 4.
9. **Table columns.** The source's Excel table (its `DATA_TOTAL`) omits the column depth, so `output/pushover_results.csv` adds `Hc`. Its AXIAL_RIGIDITY column holds the maximum absolute axial force, the same values as AXIAL_FORCE. The free-vibration maxima, periods and damping, which the source plots but does not export, are in `output/free_vibration_results.csv`. The openpyxl package is not in the environment, so no Excel file is written.
10. **Logarithmic decrement.** The source's DAMPING_RATIO_FUN solves its equation with fsolve, and this port uses the closed-form root x = |dbar| / sqrt(dbar^2 + 4 pi^2). The helper has no check of the number or the sign of the peaks, so the port returns NaN for fewer than two peaks or a non-positive peak (as the ductility sub-model does). It is the source's estimate of the damping of the free decay; the Rayleigh ratios at the two periods are checked separately.
11. **Masses (LESSON 71).** The source's `MASS = 12000` is labelled [kg], and its element masses are `Bc*Hc*0.000025` and `Bb*Hb*0.000025`. As in the other sub-models of this folder, the values are used as written: 12000 N.s^2/mm at nodes 3 and 4 in X and Y, and the element masses per unit length as written. The other reading (kg read as 1000 kg per N.s^2/mm, and the density of concrete for the elements) gives the periods in `validation.txt`. The other reading (kg read as N.s^2/mm = 1000 kg, and the density of concrete for the element masses) gives first periods of 0.12 to 0.22 s and shortest periods of 1.1 ms (`validation.txt`). The element masses as written are 10^4 times the density of concrete in N.s^2/mm^4, so the shortest period differs by about 100 between the two readings (the square root of 10^4), and the first period by a factor of 46 to 48. The time step of 0.001 s resolves the highest mode only with the masses as written. The values as written are kept, as in the other sub-models of this folder (LESSON 71); which reading the author intended is not settled by the source.
12. **Dynamic branch.** The source's dynamic branch is called in every case of the grid, so it is converted in full. Its `ops.test` and `ops.algorithm` calls are replaced by SmartAnalyze, and its `ops.analyze` loop by the transient split (AGENT.md §3c). Its ODB is saved every 40 steps (about 500 fetches). The source's `while` loop runs until 20 s; the converted run takes 20,000 steps of 0.001 s in every case (`validation.txt`).
13. **Not converted.** The source folder's `PARALLEL_COMPUTING` variant (`SENSITIVITY_..._Cdepth_FV_PARALLEL_COMPUTING.py`, 44,818 bytes, with `HISTOGRAM_BOXPLOT_FUN.py`) is a second main script and is not converted here. `PLOT_2D_FRAME` is not run; the deformed shape of the last pushover is `vis_05_deformed_last_case.html`. The source's PDF and PowerPoint are not parsed. Its figures are written as PNG files in `output/surfaces/` and `output/*.png`.
14. **Figure labels.** Two of the source's 3D surfaces name the rebar diameter and the confinement ratio on their axes, although their data are the steel ratios; the figures here use the steel-ratio axes for every surface. The source's step-plot moments say kN.mm for values in N.mm, and its stiffness scatter axes are labelled the other way round (LESSON 102).
15. **Node 3 is not controlled in the pushover.** As in the sixth sub-model, node 3 lags node 4 early and overtakes it later, because the beam between the top nodes carries axial force under the vertical loads (Note 14 of the sixth sub-model).

**Outputs** (in `output/`, git-ignored): `pushover_results.csv` (the source's table, with Hc), `free_vibration_results.csv` (the free-vibration maxima, periods and damping), `sensitivity_results.txt` (the last pushover's bilinear fits, the ranges and the free-vibration summary), `pushover_last_case.csv` (13,500 steps), `free_vibration_last_case.csv` (20,000 steps), `cases/*.npz` (each case's summary and step arrays), `validation.txt`, `model_info.json` (the model at the last pushover), the figures `last_case_curves.png`, `last_case_steps.png`, `last_case_stiffness.png`, `last_case_bilinear.png`, `dynamic_last_case.png`, `correlation_heatmap.png`, the 37 3D surfaces `surfaces/surface_00.png` to `surfaces/surface_36.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_last_case.html` and `vis_08_pushover_last_case.html`, and the ODBs `RespStepData-push_*.odb` and `RespStepData-dyn_*.odb` (with their `ModelData-*.zarr` folders) for the 18 cases and the last pushover.

**References:** The source repository (see Source above). The source's header cites no paper; its PDF was not parsed.

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Sensitivity_Cdepth_Confinement_Free_Vibration
PYTHONUTF8=1 python model.py
```
The run took about 21 minutes on this machine (10:29 to 10:50), with three cases at a time, followed by the last pushover and the post-processing. Other python processes were running on the machine when the run was checked, so the timing is indicative only (LESSON 89).
