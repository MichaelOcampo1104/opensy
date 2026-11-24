# SalarDelavar_Composite_Section_FRP_or_Plate

**Purpose:** Horizontal pushover of a 2D reinforced-concrete portal frame with fibre sections, without and with a 10 mm steel-plate jacket, with a bilinear fit, the over-strength factor, the displacement ductility and the behaviour coefficient R (sub-model of the source folder `CONCRETE_FRAME_EXAMPLES/COMPOSITE_SECTION (FRP or PLATE)`).

**Building System:** A single-storey, single-bay portal frame with both bases fixed. The columns are 3 m high and 500 x 500 mm, with 50 mm cover and six 25 mm bars (three on each face in the plane of the frame). The beam spans 7 m between the column axes and is 500 x 300 mm, with eight 18 mm bars (three top, two middle, three bottom). The confined core and the cover are modelled with Concrete01. The plate run adds a 10 mm steel plate to all four faces of each column and to one face of the beam (Note 3).

**Model Description:** 2D model with three DOFs per node (ndm = 2, ndf = 3) and four nodes. Three corotational `nonlinearBeamColumn` elements with five integration points, each with a fibre section of 20 x 5 fibres per patch. Reference load: 1 N horizontal and -1 N vertical at each top node; the load factor is the output. Horizontal displacement control of node 4 (DOF 1) from 0 to 175 mm in 0.05 mm steps (3500 steps), with SmartAnalyze (NormDispIncr, tolerance 1e-6, 5000 iterations, algorithm ladder 41, 10, 40, 20, 50, 60; KrylovNewton with the initial stiffness first, as in the source). Recorded at each step: the load factor, the displacements of node 3, the base reactions (sum over both bases) and the stiffness ratios KS, KA and KI. Post-processing: the equal-area bilinear fit of the base shear against the node-3 displacement (the source's formulas), the over-strength factor Omega_0, the displacement ductility mu, and R = Omega_0 mu.

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Concrete01 (core: f'c = 27.6 MPa, eps0 = -0.0045; cover: f'c = 18 MPa, eps0 = -0.0025); Hysteretic reinforcement (f_y = 4000 MPa, E_s = 2 x 10^5 MPa, as written); Hysteretic steel plate (f_y = 240 MPa, as written) |
| Lateral System | Portal frame (two fixed-base columns and one beam) |
| Lateral Loading | Monotonic pushover, horizontal displacement control of node 4 to 175 mm |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py (source: `py_ref/COMPOSITE_SECTION_FRAME_PUSHOVER.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 |
| Units | N, mm, MPa |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/COMPOSITE_SECTION%20(FRP%20or%20PLATE) (Salar Delavar Ghashghaei). The source script and its helpers are in `py_ref/`: `COMPOSITE_SECTION_FRAME_PUSHOVER.py` (main), `CONFINED_CONCRETE_WITH_PLATE_SECTION_FUN.py` (section), `BILINEAR_CURVE.py` (fit, ported), `ANALYSIS_FUNCTION.py` and `CONCRETE_SECTION_FUN.py` (not used by the conversion), `PLOT_2D.py` (not run), and the reference figure `COMPOSITE_SECTION_FRAME_PUSHOVER.png` (not compared). The source's Excel export is written here as CSV.

**Validation:** `output/validation.txt`, from the run of this folder:
- **Element assembly.** The force-based element with uncracked sections reproduces the textbook frame element to 3.7 x 10^-16.
- **Section properties (uncracked, initial tangents).** Column EA = 3.848 x 10^9 N and EI = 9.391 x 10^13 N.mm^2; beam EA = 2.396 x 10^9 N and EI = 1.867 x 10^13 N.mm^2. With the plate, the column EI is 1.045 x 10^14 N.mm^2 (+11 %) and the beam EI is 1.900 x 10^13 N.mm^2 (+1.8 %).
- **First pushover step, cracked.** The numpy frame takes the section state of each integration point at the first step (LESSON 66) and uses the same five Lobatto points as the element. Without the plate: OpenSees 270.5123 and numpy 270.5248, relative difference 4.7 x 10^-5. With the plate: OpenSees 349.2403 and numpy 349.2369, relative difference 9.6 x 10^-6. Node-3 displacement at the first step: relative differences 1.7 x 10^-5 (without the plate) and 4.5 x 10^-5 (with it).
- **Reference only.** The uncracked frame gives 698.9 and 762.7, which is 2.6 times the OpenSees first step without the plate (LESSON 65). The same numpy check with a 5-point Gauss-Legendre rule gives 270.6 and 349.1 (relative differences 4.6 x 10^-4 and 4.1 x 10^-4), so the match depends on the integration rule (LESSON 66).
- **Pushover equilibrium** (3500 steps). The largest residual between the base reactions and the applied load is 5.5 x 10^-8 of the largest horizontal load and 1.1 x 10^-9 of the largest vertical load without the plate; with the plate it is 3.6 x 10^-8 and 1.1 x 10^-7.
- **Post-processing.** The bilinear fit, Omega_0, mu and R are the source's formulas, ported, and are reported rather than checked against an independent solution.

**Notes:**
1. **Cracked from the first step.** Concrete01 has no tensile strength, so the tension fibres carry no stiffness and the sections are cracked from the start. The first-step stiffness is therefore well below the gross stiffness (LESSON 65).
2. **Axial load in the columns.** The vertical loads give each column an axial force of about -237 N at the first step (-0.88 N per unit load factor). A cracked section at zero axial force gives a first-step load factor of 266.0, 1.7 % below OpenSees (scratch check, Note 10). The axial force changes the neutral axis and the axial-bending coupling of the cracked section, so the check uses the state of each integration point (LESSON 66).
3. **Beam plate position.** The source's beam plate is the patch `(-(y1 + T), -z1 - T, y1 + T, -z1)`. It spans the full depth on the -z (width) face. Its comment says "Bottom plate", but its coordinates place it on a side face, so in the 2D model it acts like a web. It is kept as written (LESSON 67). The column plate covers all four faces.
4. **Plate values.** The source takes the plate's yield strain (f_y / E_s = 0.02), ultimate stress (1.1818 f_y = 4727.2 MPa) and ultimate strain (75.2 x 0.02 = 1.504) from the rebar values, and uses f_y = 240 MPa as the plate's yield stress. The plate's initial tangent is therefore 240 / 0.02 = 12000 MPa. Kept as written.
5. **Reinforcement.** f_y = 4000 MPa and E_s = 2 x 10^5 MPa (yield strain 0.02) are far from typical reinforcement. Kept as written.
6. **Control node and recorded node.** The source's pushover sets displacement control with two integrators (node 3, then node 4). The second overrides the first, so the model controls node 4 only. The source records node 3. At the last step the node-3 displacement is 167.04 mm without the plate and 167.48 mm with it, for the 175 mm control of node 4. The bilinear fit, mu and R use the node-3 displacement, as in the source (LESSON 68).
7. **Steel01 branch.** The source defines a Steel01 option (`STEEL_KIND = 1`), but its main function uses `STEEL_KIND = 2` (Hysteretic). Only the Hysteretic option is converted.
8. **Results as written** (`output/pushover_results.txt`):

   | Result | Without plate | With plate |
   |---|---|---|
   | Bilinear fit, first point (mm; N) | 47.48; 554905 | 45.00; 677627 |
   | Bilinear fit, second point (mm; N) | 167.04; 1321752 | 167.48; 1743499 |
   | Elastic stiffness (N/mm) | 11687 | 15059 |
   | Over-strength Omega_0 | 2.3819 | 2.5729 |
   | Ductility mu | 3.5181 | 3.7218 |
   | R = Omega_0 mu | 8.3800 | 9.5761 |

   The largest base shear is 1.321752 x 10^6 N without the plate and 1.743499 x 10^6 N with it.
9. **Solver tolerance.** The remaining difference of 2 x 10^-5 to 5 x 10^-5 (relative) at the first step is of the order of the displacement tolerance (NormDispIncr 1e-6, against a first-step displacement of 0.046 mm). It was not reduced further.
10. **Scratch probes (not in this folder).** A cantilever probe in OpenSees with the same sections gave EI_eff = 3.703936 x 10^13 N.mm^2 for the column and 6.2305 x 10^12 N.mm^2 for the beam. These match the zero-force cracked sections and were used to check the fibre geometry before the frame check.
11. **Run time and console.** Each SmartAnalyze run takes about 3 s (3500 steps). Run with `PYTHONUTF8=1`: opstool's progress bar prints a rocket emoji, which stops a run with cp1252 console output when the output is redirected (LESSON 35).
12. **Not converted.** The plotting helper `PLOT_2D.py` (not run) and the Steel01 branch (Note 7).

**Outputs** (in `output/`, git-ignored): `pushover_without_plate.csv` and `pushover_with_plate.csv` (3500 steps, with the source's column names), `pushover_results.txt`, `validation.txt`, `pushover_curve.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_pushover_with_plate.html` and `vis_08_pushover.html`, and the ODBs `RespStepData-*.odb` with their `ModelData-*.zarr` folders.

**References:** The source repository (see Source above).

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Composite_Section_FRP_or_Plate
PYTHONUTF8=1 python model.py
```
