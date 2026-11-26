# SalarDelavar_Sensitivity_Cdepth_Free_Vibration_Parallel

**Purpose:** The sensitivity study of the seventh sub-model of the source folder `CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO`, in the source's parallel computing version. For each of the 18 cases (six column depths x three rebar diameters, at Kfc 1.25) it gives the pushover ductility, over-strength factor, R and the bilinear stiffnesses, and the free-vibration maxima, periods, Rayleigh coefficients and logarithmic-decrement damping. The analyses are those of the seventh sub-model; this conversion checks that the parallel version gives the same result for every case (Note 4).

**Building System:** The same frame as the seventh sub-model: a single-storey, single-bay portal frame with both bases fixed. The columns are 3 m high and 500 mm wide, with 50 mm cover and six bars. Their depth Hc is 350, 400, 450, 500, 550 or 600 mm. The column rebar diameter DIAc is 28, 30 or 32 mm. The beam spans 7 m between the column axes and is 500 mm wide and 300 mm deep, with 50 mm cover and eight bars; its bars are DIAc - 4 mm. The confinement enhancement ratio Kfc is 1.25. The other sections take Kfc - 0.05 (middle column), Kfc - 0.10 (beam) and Kfc - 0.15 (middle beam) (Note 7).

**Model Description:** 2D model with three DOFs per node (ndm = 2, ndf = 3) and ten nodes. Nine corotational `nonlinearBeamColumn` elements with 10 integration points, with Concrete01 for the confined core and the unconfined cover, and Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa). The fibres form patches of 40 fibres along the depth and 1 fibre across the width (Note 2). The masses are the source's values as written (Note 11). Each case has two analyses, as in the source:
1. Pushover: horizontal displacement control of node 4 (DOF 1) from 0 to 675 mm in 0.05 mm steps (13,500 steps), with SmartAnalyze (NormDispIncr, tolerance 1 x 10^-6, 5000 iterations, algorithm order 10, 41, 40, 20, 50, 60; Note 5).
2. Free vibration of node 3 in X: an initial displacement 0.031 mm, an initial velocity 0.00015 mm/s and an initial acceleration 0.000065 mm/s^2, with a ramp load of 1 N at nodes 3 and 4 in X. Rayleigh damping from the two lowest modes, with ratios 5 % and 3 %. Newmark (0.5, 0.25) with SmartAnalyze (transient, NormDispIncr, tolerance 1 x 10^-6). The time step is 0.001 s and the duration 20 s, so 20,000 steps.

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Concrete01 (f'c = 25 MPa; core confined by the ratio, cover unconfined); Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa, as written) |
| Lateral System | Portal frame (two fixed-base columns and one beam) with the column depths above |
| Lateral Loading | Monotonic pushover (horizontal displacement control of node 4 to 675 mm) and free vibration of node 3 from initial conditions under a ramp load; 18 cases |
| Earthquake Records | None. The free vibration has no ground motion. |
| Design Year | NA |
| File Format | .py (source: `py_ref/SENSITIVITY_CONFINEMENT_ENHANCEMENT_RATIO_&_REBAR_&_Cdepth_FV_PARALLEL_COMPUTING.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 (the project's `.venv`) |
| Units | N, mm, MPa (time in s) |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO/SENSITIVITY_CONFINEMENT_ENHANCEMENT_RATIO_%26_REBAR_%26_Cdepth_FREE_VIBRATION/PARALLEL_COMPUTING (Salar Delavar Ghashghaei). `py_ref/` holds the source script, the helper files of the folder (`ANALYSIS_FUNCTION.py`, `BILINEAR_CURVE.py`, `CONCRETE_SECTION_FUN_TWO.py`, `DAMPING_RATIO_FUN.py`, `RAYLEIGH_DAMPING_FUN.py`, `HISTOGRAM_BOXPLOT_FUN.py`), the figure `COVER.png` and `PLOT_2D.py` (Note 13). The source's PDF and PowerPoint are not copied or parsed.

**Results:** Every result is the same as the seventh sub-model's (see the cross-check below), so the tables are the same. Pushover ductility mu, behaviour coefficient R = Omega_0 mu and the first free-vibration period, with the column depth Hc in rows and the column rebar diameter in columns (Kfc 1.25; from `output/pushover_results.csv`, `output/free_vibration_results.csv` and `output/cases/`).

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

The grid ranges from mu 4.96 to 6.42 and R 6.93 to 7.75. The last pushover (600 mm, 32 mm) has mu = 6.2006, Omega_0 = 1.1649 and R = 7.2228 (`output/sensitivity_results.txt`). The source's logarithmic-decrement damping is NaN in every case (Note 10).

**Cross-check against the seventh sub-model:** every case agrees with the seventh sub-model's saved result bit for bit. The comparison covers 8,316,720 values (the summary of each of the 18 cases and all of its step arrays), with no difference and the NaN positions matching. Both versions run the same code, so this checks the parallel runner and the repeatability of the analyses, not the physics, which the seventh sub-model's validation covers (LESSON 107). The comparison was a scratch check outside the repository.

**Validation:** `output/validation.txt`, from the final run of this folder:
- **Element check.** In every case the gross force-based column element agrees with the textbook frame element to 1.2 x 10^-15 to 1.9 x 10^-15 (relative).
- **First step.** In every case OpenSees and numpy agree on the first load factor to 7.7 x 10^-5 to 9.7 x 10^-5 (four or five section-state iterations), the same order as the sixth and seventh sub-models.
- **Equilibrium.** At every pushover step the base shear and the axial reaction match the applied loads (2 lambda). In 12 cases the largest departure is below 10^-4 of the largest load. In the other six it is confined to one or two steps above 10^-4, and at most 9 steps in any case exceed 10^-6. The largest, 1.4 x 10^-3 (3.4 kN in the axial reaction at step 8420 of the 500 mm, 28 mm case), is the same case and steps as in the seventh sub-model (LESSON 104).
- **Periods at t = 0.** With the masses as written, OpenSees and numpy agree on both periods to within 1.2 x 10^-5 (relative), and the Rayleigh ratios at those periods are 5.0000 % and 3.0000 %.
- **Time step.** With the masses as written the shortest period of the frame is 0.110 to 0.118 s, so the step of 0.001 s resolves it 110 to 118 times (LESSON 106).
- **Completed.** 18 of 18 cases, 13,500 pushover steps and 20,000 free-vibration steps each, with no non-finite stiffness values.
- **Last pushover.** Its base shear agrees with its grid run exactly (relative difference 0).
- **Cross-check.** Identical to the seventh sub-model in every case (see above and Note 4).
- **Mesh.** See Note 2.
- **Not validated.** The bilinear fits, Omega_0, mu, R and the source's logarithmic decrement are the source's formulas, ported (Note 10).

**Notes:**
1. **Corotational transformation.** As in the other sub-models, the analyses use the source's corotational transformation.
2. **Fibre mesh.** The source's 40 fibres along the depth of each patch are kept. Its 5 fibres across the width are reduced to 1, as in the seventh sub-model (LESSON 87). The seventh sub-model's 5-fibre check of the case 500 mm, 28 mm, Kfc 1.25 (ductility agreement to 7.3 x 10^-9, relative) applies to this conversion unchanged, since it has the same case and code (Note 4).
3. **Parallel processes.** The source runs the 18 cases with joblib (`Parallel(n_jobs=-1)`), so each case runs as a separate job. Here the cases run three at a time, each in its own process from its own working folder under `output/.work`, because opstool's `set_odb_path` removes the `.opstool.output` folder of the working folder, which is fixed when opstool is imported, so processes that share a folder fail (LESSON 85). The source does not use opstool, so its jobs do not share this problem. Each completed case is saved at once to `output/cases/` (LESSON 88).
4. **Cross-check.** Every case of this conversion is compared with the same case of the seventh sub-model: every summary value and every step array (`cases/*.npz`). Both use the same code path, so this checks the parallel runner and the determinism of the analyses, not the physics (LESSON 107). The comparison covers 8,316,720 values over the 18 cases; all agree exactly (largest relative difference 0). The check confirms that the parallel runner gives the same results as the sequential one, which is what the source's parallel version claims.
5. **Solver.** The source's pushover branch calls no `ops.test`, and its free-vibration branch sets NormDispIncr and Newton directly. The conversion manages both in SmartAnalyze, as in the seventh sub-model. The converged values may differ from the source's by the solver tolerance.
6. **Grid and last pushover.** The source's loop runs over the column depth (350 to 600 mm) outside, the rebar diameter (28, 30, 32 mm) inside, and Kfc (1.25). The sequential sub-model's plots use its last pushover (600 mm, 32 mm); the parallel version draws none of them (Note 14). This conversion runs that pushover again in the main process for its figures, `model_info.json` and the deformed-shape view, and checks that it agrees with the grid run exactly (LESSON 86).
7. **Reinforcement ratios.** The source reports RO_COL = 100 x 8 A_bar,col / (Hc Bc) and RO_BE = 100 x 6 A_bar,beam / (Hb Bb), in percent. Its column section has six bars and its beam eight, so each reported ratio counts the other member's bar number (LESSON 100). The table keeps the source's formulas (as in the seventh sub-model).
8. **Section offsets and bar diameters.** As in the seventh sub-model: the other sections take Kfc - 0.05, Kfc - 0.10 and Kfc - 0.15 (LESSON 101), and the beam bars are DIAc - 4 mm.
9. **Table columns.** The source's Excel table omits the column depth, so `output/pushover_results.csv` adds `Hc`. Its AXIAL_RIGIDITY column is the maximum absolute axial force, the same values as AXIAL_FORCE. The free-vibration maxima, periods and damping are in `output/free_vibration_results.csv`. openpyxl is not in the environment, so no Excel file is written.
10. **Logarithmic decrement.** As in the seventh sub-model, the source's DAMPING_RATIO_FUN is ported in closed form, and returns NaN when a peak is non-positive (LESSON 105). Here it is NaN in every case.
11. **Masses (LESSON 71).** As in the seventh sub-model, the source's `MASS = 12000` (labelled [kg]) and its element masses are used as written, and the other reading is in `validation.txt` The other reading gives first periods of 0.12 to 0.22 s and shortest periods of 1.1 ms, as in the seventh sub-model (its Note 11).
12. **Dynamic branch.** The source's dynamic branch is called in every case, so it is converted in full (as in the seventh sub-model).
13. **Files of the folder not in the conversion.** `PLOT_2D.py` is not in the source's `PARALLEL_COMPUTING` folder, although the script imports it, so the copy from the seventh sub-model's `py_ref/` is used (identical in the folder's other files). `PLOT_2D_FRAME` is not run; the deformed shape of the last pushover is `vis_05_deformed_last_case.html`. The source's PDF and PowerPoint are not parsed. The one-byte file `a` (a newline) is not copied.
14. **Parallel version outputs not reproduced.** In the source, the main process runs no OpenSees analysis, so its `PLOT_2D_FRAME` figure and its `printModel` output are empty. `HISTOGRAM_BOXPLOT_FUN.py` (the histogram and boxplot of a result) is defined but never called by the script, so it is not run. The source defines `PLOT_LINE` and `PLOT_SCATTER` but calls neither in this version. This conversion keeps the last-pushover figures of the seventh sub-model, so the two conversions can be compared output by output.

**Outputs** (in `output/`, git-ignored): `pushover_results.csv` (the source's table, with Hc), `free_vibration_results.csv`, `sensitivity_results.txt`, `pushover_last_case.csv`, `free_vibration_last_case.csv`, `cases/*.npz` (each case's summary and step arrays), `validation.txt`, `model_info.json`, the figures `last_case_curves.png`, `last_case_steps.png`, `last_case_stiffness.png`, `last_case_bilinear.png`, `dynamic_last_case.png`, `correlation_heatmap.png`, the 37 3D surfaces `surfaces/surface_00.png` to `surfaces/surface_36.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_last_case.html` and `vis_08_pushover_last_case.html`, and the ODBs `RespStepData-push_*.odb` and `RespStepData-dyn_*.odb` (with their `ModelData-*.zarr` folders).

**References:** The source repository (see Source above).

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Sensitivity_Cdepth_Free_Vibration_Parallel
PYTHONUTF8=1 python model.py
```
The run took about 29 minutes on this machine (15:37 to 16:06), with three cases at a time, followed by the last pushover and the post-processing. Other python processes were running on the machine during the run, so the timing is indicative only (LESSON 89). The source's joblib version would use all cores; the timing here is not a measure of that speed-up.
