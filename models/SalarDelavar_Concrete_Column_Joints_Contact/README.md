# SalarDelavar_Concrete_Column_Joints_Contact

**Purpose:** Horizontal pushover of the top node (displacement control to 520 mm) and the response to two ground motions (X and Y) of a 3 m reinforced concrete column with axial, lateral and rotational springs at both ends, which model the beam-column joints (sub-model of the source folder `CONCRETE_COLUMN_JOINTS_CONTACT`).

**Building System:** A single 3 m reinforced concrete column with a 600 x 600 mm section, 50 mm cover and 16 longitudinal bars of 25 mm (5 bars on the top and bottom faces, 2 bars on each intermediate layer). At the base and at the top, the column is connected to ground through joint springs (lateral, axial and rotational) that represent the beam-column joints. The column is modelled by three fibre nonlinear beam-column elements of 1 m each.

**Model Description:** 2D model with three DOFs per node (ndm = 2, ndf = 3). The column nodes are at 0, 1, 2 and 3 m height. Each column element is a corotational `nonlinearBeamColumn` with 5 integration points. The bottom and top elements use fibre section 1 (confined core with Concrete02, cover with Concrete02, reinforcement with Hysteretic; 120 x 3 fibres per patch). The middle element uses fibre section 2, with the same geometry and a lower confinement factor for the core. The joint springs are `zeroLength` elements: lateral (dir 1) and axial (dir 2) springs use `Steel02` material 100, and rotational springs (dir 6) use `Steel02` material 200. The base node's vertical DOF is fixed, as in the source, and the spring ground nodes are fixed. The top node carries the masses 2.0 x 10^6 N.s^2/mm in x and y and a rotational mass of 1 x 10^-9, as written. Analyses:
1. Pushover: horizontal displacement control of the top node to +520 mm in 0.01 mm steps (52,000 steps). The reference load is 100 N, and the load factor scales it. SmartAnalyze with EnergyIncr 1e-10 and 5000 iterations, ModifiedNewton first, as in the source.
2. Seismic: ground motions X and Y applied together, with the Newmark scheme (gamma = 0.5, beta = 0.25), dt = 0.01 s, for 10 s (1000 steps). The records are scaled by GMfact = 9810 mm/s^2 and SSF = 0.01, so each record unit gives 98.1 mm/s^2. The initial velocity is 5 x 10^-5 mm/s. Modal Rayleigh damping of 5 % is taken from the first two eigenvalues, as in the source. SmartAnalyze uses Newton iterations (the source's RaphsonNewton) with RelativeNormUnbalance, tolerance 1e-10 and 10,000 iterations.

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Concrete02 (f'c = 25 MPa; core and cover), Hysteretic reinforcement (E_s = 2.1e6 N/mm^2 and f_y = 4000 N/mm^2, as written), Steel02 joint springs |
| Lateral System | 3 m reinforced concrete column with lateral, axial and rotational joint springs at the base and the top |
| Lateral Loading | Pushover (horizontal displacement control); ground motions X and Y |
| Earthquake Records | Ground_Acceleration_X.txt (X) and Ground_Acceleration_Y.txt (Y), 999 points at 0.01 s (9.98 s), scaled by 98.1 mm/s^2 per unit. The records are identical to the foot-bridge records. |
| Design Year | NA |
| File Format | .py (source: `py_ref/CONCRETE_COLUMN_JOINTS_CONTACT.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 |
| Units | N, mm, MPa (time in s) |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_COLUMN_JOINTS_CONTACT (Salar Delavar Ghashghaei). The source script, its README (`py_ref/README_SOURCE.md`), the plotting helper (`py_ref/PLOT_2D.py`, not run) and the reference figure (`py_ref/OPENSEES_COLUMN_JOINT_SPRINGS_CONCRETE.jpg`) are in `py_ref/`. The source also ships a PDF and a PowerPoint. These were not copied or parsed. The records are in `ground_motions/`.

**Why no structural change was needed:** The source's configuration is stable. The two lowest periods are finite, and the OpenSees run converges at every step of both analyses.

**Validation:** Each run writes `output/validation.txt`. The numbers below come from the run of this folder.
- **Section stiffness.** Summed over the fibre geometry, independently of OpenSees: EA = 2.457 x 10^10 N and EI = 9.429 x 10^14 N.mm^2.
- **Periods.** OpenSees and the numpy assembly agree to six digits: T = 0.250321 s and 0.249519 s.
- **First pushover step.** The load factor is 1.260073 x 10^5 in both, a relative difference of 4.8 x 10^-11.
- **Pushover equilibrium** (all 52,000 steps). The maximum residual between the support reactions and the applied load is 5.7 x 10^-13 of the maximum load.
- **Seismic response.** A linear numpy Newmark run, started from zero acceleration and the initial velocity iv0 as OpenSees does, agrees with the OpenSees response to 2.9 x 10^-10 mm in x and 6.9 x 10^-8 mm in y. That is 3.7 x 10^-6 of the largest response (LESSON 61).
- **Modal damping.** As written, the numpy modes give 2.50 % and 2.51 % for the two lowest modes, because the springs carry no stiffness-proportional damping (Note 6). If the springs carried it, the ratios would be 5.00 %.
- **Damping ratio from the logarithmic decrement.** -1.07 %. The record is forced, so this value is not a damping estimate (Note 7).
- **Nonlinear response.** Checked only through the first step and the equilibrium check. The pushover is not compared with an independent solution beyond the first step.

**Notes:**
1. **The top spring carries the load.** The top lateral spring has 1.26 x 10^9 N/mm, which is more than 10^3 times the stiffness of a cantilever of the same bending stiffness (3EI/L^3 is about 10^5 N/mm). The table below shows that the spring carries essentially the whole applied load, and the column's base shear is only its share. The source's pushover plots the base shear, so its curve shows the column's share and not the total load (LESSON 63). Kept as written.

   | Top displacement (mm) | Load factor | Column base shear (N) | Top spring force (N) |
   |---|---|---|---|
   | 5 | 6.30 x 10^7 | 3.64 x 10^5 | 6.30 x 10^9 |
   | 12 | 1.46 x 10^8 | 8.73 x 10^5 | 1.46 x 10^10 |
   | 20 | 1.60 x 10^8 | 1.46 x 10^6 | 1.60 x 10^10 |
   | 50 | 1.91 x 10^8 | 3.62 x 10^6 | 1.91 x 10^10 |
   | 100 | 2.44 x 10^8 | 4.52 x 10^6 | 2.44 x 10^10 |
   | 200 | 3.50 x 10^8 | 1.28 x 10^6 | 3.50 x 10^10 |
   | 300 | 4.56 x 10^8 | 1.19 x 10^6 | 4.56 x 10^10 |
   | 400 | 5.62 x 10^8 | 1.14 x 10^6 | 5.62 x 10^10 |
   | 520 | 6.89 x 10^8 | 1.45 x 10^6 | 6.89 x 10^10 |

   The column base shear peaks at about 4.7 MN, at a top displacement of 118 mm, and then falls to about 1.1 to 1.5 MN. The top spring force is the load factor times the 100 N reference load.
2. **Masses labelled [N].** MASS_X = MASS_Y = 2.0 x 10^6 are labelled "[N]" in the source, but the code uses them as N.s^2/mm (2 x 10^9 kg). Read as a weight, the mass would be 2.0 x 10^6 N / 9810 mm/s^2 = 204 N.s^2/mm, and the two lowest periods would be 0.00253 s and 0.00252 s. A time step of 0.01 s does not resolve those periods. As written, the periods are 0.250 s, which is 25 steps per period. The value is kept as written (LESSON 64).
3. **Reinforcement.** E_s = 2.1 x 10^6 N/mm^2 is ten times the usual structural-steel value, and f_y = 4000 N/mm^2 is far above typical reinforcement. Both are kept as written. Because of the modulus, the bars give about 68 % of the section's bending stiffness (6.4 x 10^14 of 9.4 x 10^14 N.mm^2).
4. **Spring strengths.** The source's formulas with B x H = 600 x 600 mm^2 give P_Y = 42000 B H = 1.51 x 10^10 N (axial, yield displacement 12 mm) and M_Y = 57530 B H = 2.07 x 10^10 N.mm (rotational, yield rotation 0.0523 rad). Kept as written.
5. **Base vertical spring.** The base node's vertical DOF is fixed, as in the source (`fix(1, 0, 1, 0)`). The base axial spring (element 5) therefore carries no force, as in the source.
6. **Damping of the joint springs.** The `zeroLength` springs have no `-doRayleigh` flag, so they carry no stiffness-proportional damping (LESSON 49). The two lowest modes are governed by the springs, so they carry about half of the nominal 5 %: 2.50 % and 2.51 %. Kept as written.
7. **Log-decrement check.** The source estimates the damping from the peaks of the displacement over the whole 10 s forced record. The run ends 0.02 s after the record, so the peaks are not free decay. The converted value of -1.07 % is reported but not used (LESSON 62).
8. **Gravity step.** The source's gravity LoadControl step applies no loads, because its load lines are commented out. The transient therefore starts from rest. The source's pushover gravity block is also commented out.
9. **Base force sign.** The source's pushover reports the base shear, axial force and moment as minus the element-1 end forces (global F_x, F_y and M). Its dynamic run reports them without the minus sign. Both are kept as written, so the dynamic base shear is negative for a positive displacement.
10. **Period labels.** The source prints "Structure First Period" from the larger of the two frequencies, so that label refers to the second period. The Rayleigh coefficients use both frequencies correctly. `initial_periods.txt` lists both periods.
11. **Initial conditions.** OpenSees starts the transient with zero acceleration and the initial velocity iv0 = 5 x 10^-5 mm/s on the translational DOFs (`UniformExcitation -vel0`). The numpy replica uses the same start. With the physical initial acceleration instead, the replica differed from OpenSees by 1.6 x 10^-4 mm in the first 2 s (LESSON 61).
12. **Seismic results.** The largest top-node displacements are 0.0184 mm horizontally, at 9.86 s, and 0.0188 mm vertically, at 4.90 s. The largest column base shear is 1.33 kN, at 9.86 s. The largest top-spring reaction is 2.31 x 10^7 N, at 9.86 s. The ground-acceleration peak is 3.35 mm/s^2 (the record peak of 0.0342 times 98.1).
13. **Not converted.** The contact spring (`CONTACT = False` in the source) and the vertical and rotational pushover options (`KIND` 2 and 3). `KIND = 1` is used. The source's `ANALYSIS` retry function (SmartAnalyze replaces it), the plotting helpers (`PLOT_2D`, `PLOT_TIME_HISORY`, `PLOT_IMAGE`, the `PLOT_2D_FRAME` call), the recorder files (`DTH_PUSH.txt` and similar), and the folder `C:\OPENSEESPY_SALAR`, which is replaced by `output/`.
14. **Solver.** SmartAnalyze converged all 52,000 pushover steps, to 520 mm, and all 1000 steps of the seismic run. The run log has no failure messages.
15. **Reference figure and documents.** The reference figure in `py_ref/` was not compared with the converted results. The PDF and the PowerPoint were not parsed.
16. **Run time.** About 3 minutes on this machine (13:25 to 13:29).

**Outputs** (in `output/`, git-ignored): `pushover_history.csv` (52,000 steps), `dynamic_history.csv` (1000 steps), `initial_periods.txt`, `validation.txt`, `pushover_curve.png`, `dynamic.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_pushover.html`, `vis_08_pushover.html` and `vis_09_dynamic.html`, the ODBs `RespStepData-pushover.odb` and `RespStepData-dynamic.odb` with their `ModelData-*.zarr` folders, and `run.log`.

**References:** The source repository and its README (`py_ref/README_SOURCE.md`).

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Concrete_Column_Joints_Contact
PYTHONIOENCODING=utf-8 python model.py
```
