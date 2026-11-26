# SalarDelavar_Ductility_Damage_Index_Confinement_Rigid_Roof

**Purpose:** Structural ductility damage index of the 2D reinforced-concrete frame of the first sub-model with a rigid roof: the rotations of the roof nodes are restrained, so the beam-column joints at the roof do not turn. The sub-model runs a monotonic pushover to 675 mm (bilinear fit, over-strength factor, displacement ductility and R) and a 50 s time history under the X record at full scale, and computes the damage index DI = (Dd - Dy) / (Du - Dy), where Dd is the peak node-3 displacement of the time history. Fourth sub-model of the source folder `CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO`, which holds seven sub-models.

**Building System:** The same frame as the first sub-model: a single-storey, single-bay portal frame with both bases fixed. The columns are 3 m high and 500 x 500 mm, with 50 mm cover and six 25 mm bars (three on each face in the plane of the frame). The beam spans 7 m between the column axes and is 500 mm wide and 300 mm deep, with 50 mm cover and eight 18 mm bars (three top, two middle, three bottom). The confinement enhancement ratio is 1.25 for elements 1, 3, 4 and 6, 1.10 for elements 2 and 5, 1.15 for elements 7 and 9 and 1.05 for element 8, as in the source. The roof rotations are restrained at nodes 3, 4, 9 and 10 (Note 3).

**Model Description:** 2D model with three DOFs per node (ndm = 2, ndf = 3) and ten nodes. Nine corotational `nonlinearBeamColumn` elements with 10 integration points. The source runs the inelastic element only (Note 2 of the first sub-model applies: the frame is cracked from the first step). Each section has its own materials, as in the source: Concrete01 for the core (strength 25 MPa times the ratio) and for the cover (25 MPa), and Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa). The fibres form 40 x 5 patches. Analyses:
1. Pushover: horizontal displacement control of node 4 (DOF 1) from 0 to 675 mm in 0.05 mm steps (13,500 steps) with SmartAnalyze (NormDispIncr, tolerance 1 x 10^-6, 5000 iterations, algorithm ladder 10, 41, 40, 20, 50, 60). The reference load is 1 N horizontal and -1 N vertical at nodes 3 and 4. Recorded at each step: load factor, node-3 displacements and rotation, base reactions (sum over both bases) and the stiffness ratios KS, KA and KI.
2. Time history: the source's ramp load (1 N at nodes 3 and 4 in X, in a Linear pattern, so t N at time t; Note 6) and the X record through a UniformExcitation pattern, with the record scaled by GMfact (9810 mm/s^2) and SSF_X = 1.00 (Note 4) and the initial velocity 0.0005 mm/s. Newmark (0.5, 0.25), dt = 0.01 s, 50 s (5,000 steps), SmartAnalyze (ladder 10, 41, 40, 20, 50). Modal Rayleigh damping from the first two modes (5 % and 3 %) through the source's helper. Recorded at each step: displacements, velocity and acceleration of node 3, base reactions and the stiffness ratios. The source records no periods during the transient (Note 9).

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Concrete01 (f'c = 25 MPa; core confined by the ratio, cover unconfined); Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa, as written) |
| Lateral System | Portal frame with a rigid roof (roof rotations restrained at nodes 3, 4, 9 and 10) and the confinement ratios above |
| Lateral Loading | Monotonic pushover (horizontal displacement control of node 4 to 675 mm); X ground motion at full scale with a ramp load (time history) |
| Earthquake Records | `Ground_Acceleration_X.txt` (X): 999 values at 0.01 s, in g, scaled by 9810 mm/s^2 x 1.00. `Ground_Acceleration_Y.txt` is copied but not used (the run is X only). |
| Design Year | NA |
| File Format | .py (source: `py_ref/CONCRETE_FRAME_DUCTILITY_DAMAGE_INDEX_CONFINEMENT_ENHANCEMENT_RATIO_RIGID_ROOF.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 (the project's `.venv`) |
| Units | N, mm, MPa (time in s) |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO/DUCTILITY_DAMAGE_INDEX_CONFINEMENT_ENHANCEMENT_RATIO_RIGID_ROOF (Salar Delavar Ghashghaei). `py_ref/` holds the source main, its helpers (`CONCRETE_SECTION_FUN_TWO.py`, `DAMPING_RATIO_FUN.py`, `ANALYSIS_FUNCTION.py`, `BILINEAR_CURVE.py`, `RAYLEIGH_DAMPING_FUN.py`, `PLOT_2D.py`, `SALAR_MATH.py`) and the reference figure `COVER.png`. The source folder has no `EIGENVALUE_ANALYSIS_FUN.py`, because its main does not compute periods during the transient. The source's PDF and PowerPoint are not copied or parsed.

**Validation:** `output/validation.txt`, from the final run of this folder:
- **Element assembly.** The force-based element with gross sections reproduces the textbook frame element to 1.7 x 10^-15.
- **Section properties (gross, initial tangents).** Column EA = 5.851 x 10^9 N and EI = 1.427 x 10^14 N.mm^2; beam EA = 3.576 x 10^9 N and EI = 2.996 x 10^13 N.mm^2.
- **First pushover step, inelastic run.** OpenSees 1041.339 and numpy 1041.509 (relative difference 1.6 x 10^-4, with 3 iterations of the section states and 10 Lobatto points). The node-3 displacement is 0.05 mm in both. The uncracked frame with the roof restraints gives 3168.159, for reference only.
- **Equilibrium** over all 13,500 steps of the pushover: 5.6 x 10^-12 (horizontal) and 2.7 x 10^-11 (vertical).
- **Periods and Rayleigh coefficients.** The four lowest periods of the gross frame with the roof restraints and the lumped mass (LESSON 69) are 4.480435, 1.247120, 1.235778 and 1.029058 s. The numpy coefficients alpha_M = 1.266261 x 10^-1 1/s and beta_K = 6.920505 x 10^-3 s match the OpenSees values of the inelastic run, and the two targeted periods (4.480435 s and 1.247120 s) match too. The coefficients give modal ratios of 5.0000 % and 3.0000 % for modes 1 and 2.
- **Time history:** not replicated. The frame is cracked, so its response is nonlinear, and no elastic replica is run here.
- **Not validated:** the bilinear fit, the over-strength factor, the ductility, R and the damage indices are the source's formulas, ported, and are reported rather than checked against an independent solution.

**Notes:**
1. **Corotational transformation.** As in the other sub-models, both analyses use the source's corotational transformation.
2. **Cracked from the first step.** Concrete01 has no tensile strength, so the frame is cracked from the first pushover step. Its first load factor is 1041.3, against 3168.2 for the uncracked frame with the same roof restraints (ratio 0.33).
3. **Rigid roof.** The source restrains the rotation of the roof nodes with `ops.fix(3, 0, 0, 1)`, `ops.fix(4, 0, 0, 1)`, `ops.fix(9, 0, 0, 1)` and `ops.fix(10, 0, 0, 1)`: the third flag is the rotation, and the translations stay free. The roof is therefore a rotation restraint, not a rigid diaphragm (LESSON 82). The validation uses the same restraints. The frame is stiffer than the first sub-model's: its first pushover load factor is 1041.3, against 299.8, and its bilinear fit has an elastic stiffness of 41,585 N/mm, against 13,308 N/mm.
4. **Scale factor 1.00.** The source sets `SSF_X = 1.00`, so the record is applied at its full scale (9.81 m/s^2 per g of record). The first sub-model uses 10 and the ductility sub-model 0.01. The source also sets `SSF_Y = 1.00` and `iv0_Y`, which are not used because `SEI = 'X'`.
5. **Masses.** As in the first sub-model, the source's `MASS = 12000` (labelled [kg]) is used as N.s^2/mm, and the element masses from `Bc*Hc*0.000025` and `Bb*Hb*0.000025` are used as written (LESSON 71).
6. **Ramp load.** The source adds 1 N at nodes 3 and 4 in a `Linear` pattern to the time history. The series grows with time, so the load is t N, or 50 N at 50 s (LESSON 73). Kept as written.
7. **Rayleigh damping.** As in the first sub-model, the source's helper passes beta_K as the committed-stiffness coefficient (Note 7 of the first sub-model).
8. **Excitation force.** The ground motion is applied through the element masses, as in the first sub-model (LESSON 70). The time history is inelastic and not replicated, so this rule is not tested here.
9. **No periods during the transient.** The source's transient records no periods: its `EIGENVALUE_ANALYSIS` helper is not in this source folder. The only periods are those of the two targeted Rayleigh modes, 4.480435 s and 1.247120 s (Validation), so the period history of the earlier sub-models is not produced.
10. **Logarithmic decrement.** The source's damping helper returns 0 when there are fewer than two local maxima or a non-positive one. Here 10 of the 28 local maxima of the node-3 displacement X are zero or negative, so the estimate is 0 %. That is the source's guarded result, and it is not a damping ratio (LESSON 62). The modal ratios of the coefficients are in Validation.
11. **Node 3 and node 4.** With the roof rotations restrained, the two top nodes move together in X. At the end of the pushover, node 3 is at 675.000 mm, the same as the control node 4. The 683.6 mm overshoot of node 3 in the other sub-models does not occur here.
12. **Bilinear fit and damage index.** The equal-area fit (slope node 10, as the source) gives Omega_0 = 0.9743, mu = 8.9976 and R = 8.7667. The base shear peaks at 3.33 MN and falls to 3.04 MN at 675 mm, so the post-yield tangent of the fit is negative (-133.4 N/mm), and Omega_0 is below 1 (LESSON 83). The source's damage index DI = (Dd - Dy) / (Du - Dy) is -0.0848 in X (Dd = 24.13 mm, Dy = 75.02 mm, Du = 675.00 mm) and -0.1605 in Y (Dd = 3.37 mm, Dy = 8.84 mm, Du = 42.88 mm). Both are negative because the peak displacements lie below the yield displacements of the fits. The source's formula is not clipped, so the negative values are reported as computed. The axial fit gives Omega_0 = 0.8363 and mu = 4.8532.
13. **Solver.** The pushover completed all 13,500 steps to the 675 mm control, and the time history all 5,000 steps with SmartAnalyze. No step failed, and no period is computed, so no NaN can arise in this sub-model.
14. **Output files.** The source's Excel export has 12 columns with `*_WO` names and no time column. They are written as `dynamic_inelastic.csv` with the same names, plus TIME. The source does not export its pushover, so `pushover_inelastic.csv` uses the first sub-model's column names.
15. **Not converted.** The Y record and the `SEI = 'Y'` and `'XY'` branches, so `SSF_Y` and `iv0_Y` are not used. `PLOT_2D.py` (not run) and `SALAR_MATH.py` (not imported by the source's main) are kept as copies only. The source's PDF and PowerPoint are not parsed.
16. **Base shear and the transient.** The time history is not replicated (Validation), so its base shear is not validated either.
17. **Run time.** Measured on this machine with no other run active: the inelastic pushover took 3 min 16 s (13,500 steps), and the inelastic time history 6 min 45 s (5,000 steps). The whole script took about 10 minutes.

**Outputs** (in `output/`, git-ignored): `pushover_inelastic.csv` (13,500 steps, with the first sub-model's pushover column names), `dynamic_inelastic.csv` (5,000 steps, with the source's `*_WO` column names plus TIME), `pushover_results.txt` and `dynamic_results.txt` (the bilinear fit, the behaviour coefficients, the damage indices and the transient results), `validation.txt`, `model_info.json` (the OpenSees model of the last analysis), the figures `pushover_curve.png` and `dynamic_response.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_inelastic_pushover.html`, `vis_08_pushover.html` and `vis_09_dynamic.html`, and the ODBs `RespStepData-*.odb` with their `ModelData-*.zarr` folders for the two analyses.

**References:** The source repository (see Source above). The source's header cites three papers, which were not opened: "Seismic damage prediction by deterministic methods: Concepts and procedures" (doi 10.1002/eqe.4290160507), "A strain-consistent approach for determination of bounds of ductility damage index for different performance levels for seismic design of RC frame members" (ScienceDirect S0141029611005086) and "Energy Index Method: Technique for Identification of Structural Damages" (doi 10.1061/(ASCE)0733-9445(2008)134:6(1061)).

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Ductility_Damage_Index_Confinement_Rigid_Roof
PYTHONUTF8=1 python model.py
```
