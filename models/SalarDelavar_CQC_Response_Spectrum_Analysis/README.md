# SalarDelavar_CQC_Response_Spectrum_Analysis

**Purpose:** Response spectrum analysis of a one-bay, one-storey reinforced-concrete frame, with the periods and participation of the first two modes, the column base moment of each mode, and their CQC combination. It converts the source's `CQC_RESPONSE_SPECTRUM_ANALYSIS/EXAMPLE_01`, the next folder after `CONFINEMENT_ENHANCEMENT_RATIO` in `CONCRETE_FRAME_EXAMPLES`.

**Building System:** A single-storey, single-bay reinforced-concrete portal frame with both bases fixed. The columns are 3 m high and 400 x 400 mm. The beam spans 5 m between the column axes and is 300 mm wide and 400 mm deep. The members are elastic, with gross sections and Ec = 4700 sqrt(fc) = 25,743 MPa for fc = 30 MPa.

**Model Description:** 2D model with three DOFs per node, four nodes and three `forceBeamColumn` elements (two columns and the beam), with five Lobatto integration points and elastic sections. Lumped masses of 500 N.s^2/mm at nodes 3 and 4 in X and Y, with no rotational inertia (Note 1). The seismic input is the source's given response spectrum: 103 points from T = 0 to 6 s, in the X direction, with 5 % modal damping and CQC combination. The analysis is a response spectrum analysis run one mode at a time, for the first two modes (Note 7). The source's Sa values are in m/s² and are converted to mm/s² (Note 2).

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Elastic, Ec = 4700 sqrt(fc) = 25,743 MPa (fc = 30 MPa); gross sections |
| Lateral System | Portal frame with fixed bases (columns 400 x 400 mm, 3 m; beam 300 x 400 mm, 5 m) |
| Lateral Loading | Response spectrum analysis in X from the given spectrum (Sa against T, 0 to 6 s), 5 % damping, CQC |
| Earthquake Records | None. The spectrum is given; the source has no ground-motion record. |
| Design Year | NA |
| File Format | .py (source: `py_ref/RESPONSE_SPECTRUM_ANALYSIS.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 (the project's `.venv`) |
| Units | N, mm, MPa (time in s) |

**References:** Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CQC_RESPONSE_SPECTRUM_ANALYSIS/EXAMPLE_01 (Salar Delavar Ghashghaei). OpenSees command: https://openseespydoc.readthedocs.io/en/latest/src/responseSpectrumAnalysis.html. The source's two video links: https://www.youtube.com/watch?v=I7aG25MasNM and https://www.youtube.com/watch?v=48DNGzmznZ0. `py_ref/` holds the source script, its plot helper `PLOT_2D.py` (imported by the source but not called here, Note 8) and the figure `COVER.png`.

**Suggested Citation:** NA

**Results:** The converted model, with the mass in N.s^2/mm and the spectrum in mm/s² (Notes 1 and 2). Mode 1 carries all the X response. Mode 2 is antisymmetric in X and takes no part.

| Mode | T (s) | lambda (rad^2/s^2) | Participation Gamma | Sa(T) (mm/s²) | Column 1 base moment (N.mm) | Column 1 axial force (N) | Base shear, both columns (N) |
|---|---|---|---|---|---|---|---|
| 1 | 1.211283 | 26.907183 | -31.622481 | 1619.9076 | -1.544653e+09 | 3.575689e+05 | -1.619877e+06 |
| 2 | 0.125909 | 2490.2529 | 0 | 4903.0000 | -7.4e-07 | 5.6e-11 | ~0 |

- The CQC combination of the column 1 base moment is 1.5446530596 x 10^9 N.mm (1544.65 kN.m), the same as the magnitude of mode 1, because mode 2 takes no part. The OpenSees sign convention gives the moment as negative.
- The effective modal mass is Gamma^2 = 999.98 N.s^2/mm, which is 99.998 % of the 1000 N.s^2/mm total. The base shear equals Gamma^2 x Sa(T1) = 999.98 x 1619.9 mm/s² (1.62 MN).
- **The source's own numbers, as written.** With the mass as written and the spectrum read as numbers in mm/s², the first period is 38.3041 s, beyond the spectrum's 6 s end. The model is run on those numbers as a check: it reproduces the source's eigenvalues (0.0269072 and 2.49025), its TEST 02 column base moment (-1.5615254750 x 10^8 N.mm) and its TEST 00 beam moment from the recorder (5.8580476250 x 10^7 N.mm). See Note 1.

**Validation:** `output/validation.txt`, from the final run of this folder. 15 checks pass, and the run log has no warnings or errors.
- **Eigenvalues.** An independent numpy calculation (the four translational DOFs of nodes 3 and 4, with the rotations condensed out) agrees with OpenSees for both modes to 1.4 x 10^-14 (relative).
- **Mode 1 response.** The column base moment and the base shear agree with an independent modal static solution (the modal forces M phi Gamma Sa solved on the full frame, then the element end forces) to 5 x 10^-14 (relative).
- **Equilibrium.** The base shear equals Gamma^2 Sa(T1) to 8 x 10^-15 (relative).
- **Mode 2.** Its participation in X is zero, and its column moment is 7 x 10^-7 N.mm (zero).
- **CQC.** The source's coefficient and the standard frequency-ratio form agree exactly, and both equal the mode 1 moment (Note 5).
- **Path route.** The spectrum as a Path time series, mode by mode, gives the list route's moments to 1.2 x 10^-15 (column) and 4.1 x 10^-16 (beam).
- **As written.** The source's own values reproduce its printed and recorded results to 1.3 x 10^-14 (relative): the two eigenvalues, the TEST 02 column moment and the TEST 00 beam moment. The numpy calculation agrees with OpenSees to 5.3 x 10^-14.
- **All-modes calls.** After one all-modes call (no `-mode`), the column moment read from the element is -5.6 x 10^-7 N.mm, in both the Path and the list forms. Those calls store no element response (Note 4).

**Notes:**
1. **Mass units (AGENT.md §12j).** The source writes `mass = 500000.0` labelled [kg] and uses it as written. In the N-mm-s system that is 500,000 N.s^2/mm per node (5 x 10^8 kg). The first period is then 38.3041 s, beyond the spectrum's 6 s end, so OpenSees holds the spectrum at its last value, 0.1637602 (the base shear of 163,757 N equals 999,981 x 0.1637602). The model reads the label instead: 500000 kg / 1000 = 500 N.s^2/mm per node (1 N.s^2/mm = 1000 kg, so `standards/units.py` `kg` is not 1 kg). That gives T1 = 1.2113 s, inside the spectrum. **This reading is a judgement for the user to confirm**, because all the converted results depend on it. The as-written run is kept as the reproduction check.
2. **Spectrum units.** The source's Sa values are in m/s². The plateau 4.903 is 0.5 x 9.806 m/s², and 1.9612 and 3.72628 are 0.2 and 0.38 times 9.806. The source's plot labels the axis [g], which is wrong. The model multiplies by 1000 (1 m/s² = 1000 mm/s², `units.py`: `m / sec**2`). Read as numbers in mm/s², the spectrum and the base shear would both be 1000 times too small.
3. **Recorders replaced.** The source writes its per-mode responses with three `ops.recorder` calls, which AGENT.md §4 forbids. The model reads the element responses with `ops.eleResponse` after each mode's call and stores each mode as one `CreateODB` step. The recorder files are not reproduced. The source reassigns its `filename` variable with each recorder, so the file that TEST 00 and TEST 01 read is the beam's (`SALAR_ele_3_sec_1.txt`), not the column's.
4. **The source's TEST 00 and TEST 01.** TEST 00 (all modes in one call, Tn and Sa lists) and TEST 01 (all modes in one call, Path time series) cannot be converted as all-modes calls: after such a call the element response is zero (Validation). Their per-mode values exist only in the recorder. TEST 01's own rows in the recorder file (rows 3 and 4) are zero, and its printed values are the first two rows of the file, which are TEST 00's. So the source's TEST 01 repeats TEST 00 and checks nothing. TEST 02 (mode by mode, column base moment) is the converted model's main route, and the Path route is checked mode by mode.
5. **CQC coefficient.** The source's CQC function takes b_ij = lambda_i / lambda_j, a ratio of eigenvalues (omega^2). The correlation coefficient of the standard CQC formula (Der Kiureghian, 1981) takes the frequency ratio omega_j / omega_i. The model keeps the source's function (`cqc_source`) and checks the standard form (`cqc_frequency_ratio`). Both agree here because mode 2 has no X participation, so the coefficient does not change these results. It would matter for two modes that both take part and have close periods.
6. **Beam moment location.** The beam moment is read at integration point 2 of the beam: the second of five Lobatto points, 0.17 L from node 3, not at the beam end. The source's docstring names the column base moments as its outputs; the beam value is the source's TEST 00 quantity and is kept for the reproduction check.
7. **Solver.** The response spectrum command runs no iteration: it takes the modal eigenvectors and the spectrum and computes each mode's static response to the modal forces. SmartAnalyze has no convergence to manage here, and the model calls no `ops.analyze`. AGENT.md §10 lists no exception for this calculation, so each mode is one ODB step (`fetch_response_step` after each). The source's `constraints`, `numberer`, `system`, `test`, `algorithm`, `integrator` and `analysis` calls are not needed, and a probe with an analysis object set gave the same moment to 10^-15 (relative). **Please confirm whether this should be recorded as an AGENT.md exception.**
8. **Visualisation.** The source's `PLOT_2D_FRAME` and its spectrum plot use `plt.show()`. They are replaced by HTML files from `vis_utils`: V1 to V4 (`vis_nodes`, `vis_model`, `vis_loads`, `vis_pre_analysis`), the deformed shape from ODB tag 1 (`vis_05_deformed_rsa.html`), and the spectrum (`vis_07_response_spectrum.html`, values in m/s² as the source has them). V3 has no load vectors to draw, because the spectrum is not a load. `PLOT_2D.py` is kept in `py_ref/` and is not imported.
9. **Outputs.** The source prints nodes 1 to 4 and elements 1 to 3 with `printModel` to the console; the model writes the same model to `output/RESPONSE_SPECTRUM_ANALYSIS.json`. The source's modal report (`ops.modalProperties`) is `output/SALAR_ModalReport.txt`. The ODB files are tag 1 (the main run), tag 2 (the Path route) and tag 3 (the as-written check). `output/` is git-ignored.
