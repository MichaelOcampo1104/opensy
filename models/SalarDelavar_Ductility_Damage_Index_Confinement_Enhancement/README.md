# SalarDelavar_Ductility_Damage_Index_Confinement_Enhancement

**Purpose:** Structural ductility damage index of the 2D reinforced-concrete frame of the first sub-model: the monotonic pushover to 675 mm (base-shear bilinear fit, over-strength factor, displacement ductility and R) and the damage index DI = (Dd - Dy) / (Du - Dy), where Dd is the peak node-3 displacement of an inelastic time history under the X record scaled by 0.01 g. Third sub-model of the source folder `CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO`, which holds seven sub-models.

**Building System:** The same frame as the first sub-model: a single-storey, single-bay portal frame with both bases fixed. The columns are 3 m high and 500 x 500 mm, with 50 mm cover and six 25 mm bars (three on each face in the plane of the frame). The beam spans 7 m between the column axes and is 500 mm wide and 300 mm deep, with 50 mm cover and eight 18 mm bars (three top, two middle, three bottom). The confinement enhancement ratio is 1.25 for elements 1, 3, 4 and 6, 1.10 for elements 2 and 5, 1.15 for elements 7 and 9 and 1.05 for element 8, as in the source.

**Model Description:** 2D model with three DOFs per node (ndm = 2, ndf = 3) and ten nodes. Nine corotational `nonlinearBeamColumn` elements with 10 integration points. The source runs the inelastic element only, so this sub-model has no elastic run (Note 3). Each section has its own materials, as in the source: Concrete01 for the core (strength 25 MPa times the ratio) and for the cover (25 MPa), and Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa). The fibres form 40 x 5 patches. Analyses:
1. Pushover: horizontal displacement control of node 4 (DOF 1) from 0 to 675 mm in 0.05 mm steps (13,500 steps) with SmartAnalyze (NormDispIncr, tolerance 1 x 10^-6, 5000 iterations, algorithm ladder 10, 41, 40, 20, 50, 60). The reference load is 1 N horizontal and -1 N vertical at nodes 3 and 4. Recorded at each step: load factor, node-3 displacements and rotation, base reactions (sum over both bases) and the stiffness ratios KS, KA and KI.
2. Time history: the source's ramp load (1 N at nodes 3 and 4 in X, in a Linear pattern, so t N at time t; Note 6) and the X record through a UniformExcitation pattern, with the record scaled by GMfact (9810 mm/s^2) and SSF_X = 0.01 (Note 4) and the initial velocity 0.0005 mm/s. Newmark (0.5, 0.25), dt = 0.01 s, 50 s (5000 steps), SmartAnalyze (ladder 10, 41, 40, 20, 50). Modal Rayleigh damping from the first two modes (5 % and 3 %) through the source's helper. Recorded at each step: displacements, velocity and acceleration of node 3, base reactions, the stiffness ratios and the shortest and longest of the first four periods.

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Concrete01 (f'c = 25 MPa; core confined by the ratio, cover unconfined); Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa, as written) |
| Lateral System | Portal frame (two fixed-base columns and one beam) with the confinement ratios above |
| Lateral Loading | Monotonic pushover (horizontal displacement control of node 4 to 675 mm); X ground motion with a ramp load (time history) |
| Earthquake Records | `Ground_Acceleration_X.txt` (X): 999 values at 0.01 s, in g, scaled by 9810 mm/s^2 x 0.01. `Ground_Acceleration_Y.txt` is copied but not used (the run is X only). |
| Design Year | NA |
| File Format | .py (source: `py_ref/CONCRETE_FRAME_DUCTILITY_DAMAGE_INDEX_CONFINEMENT_ENHANCEMENT_RATIO.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 (the project's `.venv`) |
| Units | N, mm, MPa (time in s) |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CONFINEMENT_ENHANCEMENT_RATIO/DUCTILITY_DAMAGE_INDEX_CONFINEMENT_ENHANCEMENT_RATIO (Salar Delavar Ghashghaei). `py_ref/` holds the source main, its helpers (`CONCRETE_SECTION_FUN_TWO.py`, `DAMPING_RATIO_FUN.py`, `ANALYSIS_FUNCTION.py`, `BILINEAR_CURVE.py`, `RAYLEIGH_DAMPING_FUN.py`, `EIGENVALUE_ANALYSIS_FUN.py`, `PLOT_2D.py`, `SALAR_MATH.py`) and the reference figure `COVER.png`. The helpers `CONCRETE_SECTION_FUN_TWO.py` (whitespace only) and `DAMPING_RATIO_FUN.py` (a different version from the first sub-model's) are this sub-model's copies. The source's PDF and PowerPoint are not copied or parsed. The source's Excel export is written here as CSV.

**Validation:** `output/validation.txt`, from the final run of this folder:
- **Element assembly.** The force-based element with gross sections reproduces the textbook frame element to 1.7 x 10^-15.
- **Section properties (gross, initial tangents).** Column EA = 5.851 x 10^9 N and EI = 1.427 x 10^14 N.mm^2; beam EA = 3.576 x 10^9 N and EI = 2.996 x 10^13 N.mm^2.
- **First pushover step, inelastic run.** OpenSees 299.8451 and numpy 299.8672 (7.4 x 10^-5), with the section states of the first step and 10 Lobatto points. The node-3 displacement is 0.04502298 mm (OpenSees) and 0.04502249 mm (numpy). The uncracked frame gives 1068.849, for reference only.
- **Equilibrium** over all 13,500 steps of the pushover: 3.8 x 10^-12 (horizontal) and 1.9 x 10^-11 (vertical).
- **Periods and Rayleigh coefficients.** The four lowest periods of the gross frame with the lumped mass (LESSON 69) are 7.584309, 2.440709, 1.832704 and 1.030376 s. The numpy coefficients alpha_M = 7.457112 x 10^-2 1/s and beta_K = 1.205471 x 10^-2 s match those of the inelastic run in OpenSees, and they give modal ratios of 5.0000 % and 3.0000 % for modes 1 and 2. At the first step of the time history, OpenSees gives the shortest and longest of the first four periods as 1.459937 s and 12.243107 s (the cracked state).
- **Time history:** not replicated. The frame is cracked, so its response is nonlinear, and only its start is checked (the first periods above).
- **Not validated:** the bilinear fit, the over-strength factor, the ductility, R and the damage indices are the source's formulas, ported, and are reported rather than checked against an independent solution.

**Notes:**
1. **Corotational transformation.** As in the first sub-model, both analyses use the source's corotational transformation. The pushover is the same model with the same load: `pushover_inelastic.csv` is byte-identical to the first sub-model's.
2. **Cracked from the first step.** Concrete01 has no tensile strength, so the frame is cracked from the first pushover step: its first load factor is 299.8, against 1068.8 for the gross frame (ratio 0.28), as in the first sub-model.
3. **No elastic run.** The source's `PD_ANALYSIS` has no elastic branch (it takes no element-kind argument), so this sub-model runs the inelastic element only, for the pushover and the time history. The elastic results of the first sub-model are not repeated here.
4. **Scale factor 0.01.** The source sets `SSF_X = 0.01`, where the first sub-model uses 10. The two X records are identical. The ground acceleration is therefore 0.01 standard gravities (98.1 mm/s^2 per g of record), and the peak node-3 displacement of the time history is 0.35 mm. The source also sets `SSF_Y = 0.01` and `iv0_Y`, which are not used because `SEI = 'X'`.
5. **Masses.** As in the first sub-model, the source's `MASS = 12000` (labelled [kg]) is used as N.s^2/mm, and the element masses from `Bc*Hc*0.000025` and `Bb*Hb*0.000025` are used as written (LESSON 71).
6. **Ramp load.** The source adds 1 N at nodes 3 and 4 in a `Linear` pattern to the time history. That series grows with time, so the load is t N, or 50 N at 50 s (LESSON 73). Kept as written.
7. **Rayleigh damping.** As in the first sub-model, the source's helper passes beta_K as the committed-stiffness coefficient (Note 7 of the first sub-model).
8. **Excitation force.** The ground motion is applied through the element masses, as in the first sub-model (LESSON 70). The time history is inelastic and not replicated, so this rule is not tested here.
9. **Source text that does not apply here.** The source's header describes an HHT-alpha integrator, but the HHT line is commented out and the run uses Newmark (0.5, 0.25). The source's `GMfact` enters the ground-motion factor. Its plots are written as PNG files, and its printed results go to the results files.
10. **Logarithmic decrement.** This sub-model's source helper (`DAMPING_RATIO_FUN.py`) has no guard for the number or the sign of the peaks. Here it returns NaN. Of the 24 local maxima of the node-3 displacement X, 7 are zero or negative, so the ratio of consecutive peaks is negative in places and its logarithm is undefined. The first sub-model's helper returns 0 for such a record, so the two helpers disagree on the same kind of input (LESSON 80). The estimate is not a modal damping ratio (LESSON 62); the modal ratios of the coefficients are in Validation.
11. **Node 3 and node 4.** The pushover controls node 4 and records node 3, as in the first sub-model. The node-3 displacement at the end is 683.6 mm, which is larger than the 675 mm control.
12. **Bilinear fit and damage index.** The equal-area fit (slope node 10, as the source) gives Omega_0 = 1.1615, mu = 5.7515 and R = 6.6802, as in the first sub-model. The source's damage index DI = (Dd - Dy) / (Du - Dy), with Dd the peak node-3 displacement of the time history, is -0.2098 in X (Dd = 0.3473 mm, Dy = 118.86 mm, Du = 683.64 mm) and -0.1750 in Y (Dd = 0.0284 mm, Dy = 8.13 mm, Du = 54.45 mm). Both are negative because the peak displacements lie below the yield displacements of the fits. The source's formula is not clipped, so the negative values are reported as computed; the source describes DI close to 0 for an elastic response.
13. **Solver and period helper.** The pushover completed all 13,500 steps to the 675 mm control, and the time history all 5,000 steps with SmartAnalyze. The source's period helper takes the minimum and maximum of four eigenvalues. This run has no step with a NaN period (0 of 5,000). Where a tangent eigenvalue is negative, the helper returns NaN; the report then uses the finite values and counts the NaN steps, as the impact-load sub-model does.
14. **Output files.** The source's Excel export has 12 columns with `*_WO` names and no time column. They are written as `dynamic_inelastic.csv` with the same names, plus TIME, PERIOD_MIN and PERIOD_MAX. The source does not export its pushover, so `pushover_inelastic.csv` uses the first sub-model's column names.
15. **Not converted.** The Y record and the `SEI = 'Y'` and `'XY'` branches, so `SSF_Y` and `iv0_Y` are not used. `PLOT_2D.py` (not run) and `SALAR_MATH.py` (not imported by the source's main) are kept as copies only. The source's PDF and PowerPoint are not parsed.
16. **Base shear and the transient.** The inelastic time history is not replicated (Validation), so its base shear is not validated either.
17. **Run time.** Measured on this machine while another model run shared the processor: the inelastic pushover took 8 min 4 s (13,500 steps), and the inelastic time history took 2 min 22 s (5,000 steps). The whole script took about 11 minutes.

**Outputs** (in `output/`, git-ignored): `pushover_inelastic.csv` (13,500 steps, with the first sub-model's pushover column names), `dynamic_inelastic.csv` (5,000 steps, with the source's `*_WO` column names plus TIME, PERIOD_MIN and PERIOD_MAX), `pushover_results.txt` and `dynamic_results.txt` (the bilinear fit, the behaviour coefficients, the damage indices and the transient results), `validation.txt`, `model_info.json` (the OpenSees model of the last analysis), the figures `pushover_curve.png` and `dynamic_response.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_inelastic_pushover.html`, `vis_08_pushover.html` and `vis_09_dynamic.html`, and the ODBs `RespStepData-*.odb` with their `ModelData-*.zarr` folders for the two analyses.

**References:** The source repository (see Source above). The source's header cites three papers, which were not opened: "Seismic damage prediction by deterministic methods: Concepts and procedures" (doi 10.1002/eqe.4290160507), "A strain-consistent approach for determination of bounds of ductility damage index for different performance levels for seismic design of RC frame members" (ScienceDirect S0141029611005086) and "Energy Index Method: Technique for Identification of Structural Damages" (doi 10.1061/(ASCE)0733-9445(2008)134:6(1061)).

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Ductility_Damage_Index_Confinement_Enhancement
PYTHONUTF8=1 python model.py
```
