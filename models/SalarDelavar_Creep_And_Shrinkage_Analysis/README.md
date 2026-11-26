# SalarDelavar_Creep_And_Shrinkage_Analysis

**Purpose:** Creep and shrinkage of a reinforced-concrete frame over 5 years of analysis time, with two reinforcement models (Steel01 and Hysteretic). For each model, at each of 73 steps, the model gives the base reactions, the displacements and rotation of the top nodes and the midspan, and the three stiffnesses. It also fits a bilinear curve to the Steel01 run (ductility, over-strength factor and R). This is the first of the three sub-models in the source folder `CONCRETE_FRAME_EXAMPLES/CREEP_AND_SHRINKAGE`. The other two are not converted yet (Note 11).

**Building System:** A single-storey, single-bay reinforced-concrete portal frame with both bases fixed, and a 7 m beam with a midspan node. The columns are 3 m high and 500 x 500 mm, with 50 mm cover and six 25 mm bars (three on each face). The beam is 500 mm wide and 300 mm deep, with 50 mm cover and eight 18 mm bars (three at the top, two in the middle and three at the bottom). The concrete has a strength of 25 MPa, with a confined core (confinement ratio 1.2 in the column and 1.1 in the beam, Note 2) and an unconfined cover.

**Model Description:** 2D model with three DOFs per node, five nodes and four corotational `nonlinearBeamColumn` elements (the two columns, and the beam in two halves). Each section is a fibre section with patches of 20 fibres along the depth and 5 across the width. The core and cover concrete are TDConcrete, which models creep and shrinkage (ACI 209R-92 with the source's constants). The reinforcement is Steel01 (run 1) or Hysteretic (run 2), with f_y = 4000 MPa and E_s = 200,000 MPa. Each top node carries 1 N horizontally, 10 kN downward and a moment of 2.5 x 10^5 N.mm, with opposite signs at the two nodes. The loads are on a Linear time series, so the load factor equals the analysis time (Note 1). The analysis applies the loads at day 28, switches creep on, and runs 73 load steps of 25 days to day 1853. Each step is one `ops.analyze` call with the source's fallback ladder (Note 3), and one ODB step.

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | TDConcrete (f'c = 25 MPa, creep and shrinkage by ACI 209R-92); Steel01 or Hysteretic reinforcement (f_y = 4000 MPa, E_s = 200,000 MPa) |
| Lateral System | Portal frame with fixed bases (columns 500 x 500 mm, 3 m; beam 500 x 300 mm, 7 m) |
| Lateral Loading | Top-node loads on a Linear time series (load factor = analysis time, from day 28 to day 1853; Note 1) |
| Earthquake Records | None |
| Design Year | NA |
| File Format | .py (source: `py_ref/CONCRETE_FRAME_CREEP_AND_SHRINKAGE.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 (the project's `.venv`) |
| Units | N, mm, MPa (time in days) |

**References:** Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CREEP_AND_SHRINKAGE/CREEP_AND_SHRINKAGE_ANALYSIS (Salar Delavar Ghashghaei). The source's header cites: Creep and Shrinkage, Their Effect on the Behavior of Concrete Structures (https://link.springer.com/book/10.1007/978-1-4612-5424-9); https://en.wikipedia.org/wiki/Creep_and_shrinkage_of_concrete; https://www.sciencedirect.com/science/article/abs/pii/S0950061817313028; and https://www.sciencedirect.com/science/article/abs/pii/S0029549300003046. TDConcrete: https://openseespydoc.readthedocs.io/en/latest/src/TDConcrete.html. `py_ref/` holds the source main script, its helpers and the figure `COVER.png`. The source's PDF and PowerPoint are not copied or parsed.

**Suggested Citation:** NA

**Results:** The Steel01 run, with the beam at Kfc 1.1 (Note 2). The base shear and base axial force are fixed by equilibrium with the loads (Note 1), so the displacements, rotation and moment carry the structural response.

| Day | Load factor | Node 3, X (mm) | Node 5, Y (mm) | Rotation, node 3 (rad) | Base shear (N) | Base axial (N) | Base moment (N.mm) |
|---|---|---|---|---|---|---|---|
| 53 | 53 | 0.478719 | -1.279537 | -3.142 x 10^-4 | -106 | 1.06 x 10^6 | 2.680 x 10^5 |
| 203 | 203 | 0.854917 | -4.070810 | -8.756 x 10^-4 | -406 | 4.06 x 10^6 | 1.083 x 10^6 |
| 853 | 853 | 1.253549 | -14.696010 | -2.817 x 10^-3 | -1706 | 1.706 x 10^7 | 5.878 x 10^6 |
| 1853 | 1853 | 1.845051 | -30.499352 | -5.743 x 10^-3 | -3706 | 3.706 x 10^7 | 2.187 x 10^7 |

At day 1853 the lateral stiffness in X is 2009 N/mm, the stiffness in Y (axial) is 1.215 x 10^6 N/mm, and the rotational stiffness is 3.808 x 10^9 N.mm/rad.

Bilinear fits of the Steel01 run, as the source plots them:
- X (base shear against the node-3 displacement): elastic 640.5 N/mm, plastic 2008.6 N/mm, tangent 3753.0 N/mm; ductility 1.784, over-strength factor 5.595, R 9.984.
- Y (base axial force against the node-5 displacement): elastic 1.0537 x 10^6 N/mm, plastic 1.2151 x 10^6 N/mm, tangent 1.2721 x 10^6 N/mm; ductility 3.833, over-strength factor 4.420, R 16.94.

The check run at Kfc 1.2, which reproduces the source, gives X: ductility 1.773, over-strength 5.595, R 9.919; and Y: ductility 3.868, over-strength 4.467, R 17.28 (the source's printed values).

**Validation:** `output/validation.txt`, from the final run of this folder. All 31 checks pass, and the run log has no Python errors.
- **Time.** The 73 steps run from day 53 to day 1853 in 25-day steps, exactly 28 + 25n.
- **Equilibrium, every step, every run.** The base shear equals 2 N x t and the base axial force equals 20 kN x t. The moments about the origin balance to a relative residual of 5.5 x 10^-13 or less (the force residuals are at most 5.5 x 10^-11).
- **Moments at the deformed positions (LESSON 118).** With the undeformed node positions the moment residual is 5.8 x 10^-5, and that is not an error. The corotational analysis moves the loaded nodes, and each vertical load's moment changes with its node's sideways displacement. The balance is checked with the displaced positions.
- **Reproduction of the source.** The check run (beam at 1.2, the source's effective value) matches the source's printed displacements, base shear and base axial force at steps 1, 2 and 73 to 10^-9 (relative), and its bilinear fits to 6 x 10^-6 (relative, at the printed four decimals).
- **Fallback ladder.** The check run needs it only at step 7 (day 203, load factor 203), as the source does. The main runs need it only for the analysis at the creep age, which converges on its first attempt (Note 3).
- **Steel01 and Hysteretic.** At day 1853 their displacements agree to 1 x 10^-8 and their base moments to 2 x 10^-8 (relative).
- **Beam confinement (Note 2).** At day 1853 the converted beam (1.1) differs from the source's effective 1.2 by 0.18 % at node 3, 0.018 % at node 5 and 0.058 % in rotation.

**Notes:**
1. **The load grows with time (not changed).** The source applies its loads on a Linear time series and advances the analysis with LoadControl steps of 25 days. The load factor of a Linear series is the analysis time, so the load factor is 28 + 25n: 53 at the first step and 1853 at the last. The applied loads therefore grow with time. At day 203 they are 203 times the stated values, and at day 1853 they are 1853 times: 37.06 MN of vertical load, 3.7 kN of horizontal load, and couples of -4.63 x 10^8 N.mm at node 3 and +4.63 x 10^8 N.mm at node 4. The base shear and axial force follow this exactly (Validation). A creep analysis usually holds the load constant after the creep age, so this may not be what the author intended. The source's results are reproduced here as written. From day 203 the concrete is past its compressive strain limit in many fibres (Note 9), and the solver continues from that state, as the source does. Changing the load protocol changes every result, so it is the user's decision.
2. **Beam confinement ratio.** The source's main script calls the section function with Kfc = 1.1 for the beam, but the function sets `Kfc = 1.2` in its first lines and ignores the argument. The source's results therefore use 1.2 for both sections. The converted model uses the value the call names, 1.1 for the beam (LESSON 102). The check run keeps 1.2 and reproduces the source exactly. At day 1853 the effect is small (Validation). The fitted Steel01 ductility is 1.784 with 1.1 and 1.773 with 1.2.
3. **Solver: an exception to the SmartAnalyze rule, for approval.** Each step is one `ops.analyze(1)` call, followed by the source's fallback ladder (`ANALYSIS_FUNCTION.py`, ported as `analyze_step`): five convergence tests and seven algorithms, tried in turn until one converges. SmartAnalyze cannot run this analysis, because its static mode always uses displacement control, whatever integrator is set (AGENT.md §3c). The analysis is load-controlled, so it falls under the LoadControl exception in §3c and §10, which the audit (item 22) allows only with documented approval. **Please confirm the exception.** The source does not test its first analysis, at the creep age (load factor 28). With the beam at 1.1 that analysis does not converge on OpenSees' default test (return code -3), and the steps that follow would start from an unchecked state. The converted model therefore applies the same ladder to it. The check run converges on the default test and follows the source's path exactly.
4. **Units and time.** Lengths are in mm, forces in N, stresses in MPa, and time in days, because TDConcrete's creep and shrinkage functions are written in days. The source's values are kept: ultimate shrinkage 400 micro-strain (entered negative, as the material requires), ultimate creep coefficient 3.0, creep age 28 days, drying from day 14, casting at day 2, and the ACI 209R-92 fitting parameters. Tension strength is 0.55 times the compressive strength.
5. **Reinforcement model.** Steel01 and Hysteretic give the same response here, so the steel model does not change the result: the concrete governs. As in the source, only the Steel01 run is fitted.
6. **Source header.** The source's docstring describes pushover analysis, cyclic degradation, pinching and element rotation histories. It does not describe this code, which runs a creep and shrinkage analysis with two steel models. The converted header describes what the code runs.
7. **Time column.** The source's `TIME` list counts 25-day steps from zero (25 to 1825 days). The analysis time is 28 + 25n (53 to 1853 days). The converted CSV uses the analysis time (`TIME_DAY`), which the source does not export.
8. **Outputs.** The source writes an Excel file, which needs openpyxl, and the project environment does not have it. The same table is written as `output/CONCRETE_FRAME_CREEP_AND_SHRINKAGE_RESULTS.csv`, with the time column added. The source's twelve matplotlib figures are HTML files: `vis_08_curves_*` (P-M, shear-displacement, axial-displacement and moment-rotation curves) and `vis_09_history_*` (six histories), one set per run. The logarithmic axes of its two stiffness plots are not reproduced. Its `PLOT_2D_FRAME` is not called, and the deformed shape comes from `vis_defo` (`vis_05_deformed_steel01.html`). `printModel` writes `CONCRETE_FRAME_CREEP_AND_SHRINKAGE.json` for the model of the Hysteretic run, as the source does at the end of its main script.
9. **Solver messages.** TDConcrete prints `Strain Compression Limit Exceeded` for each fibre beyond its compressive limit, from day 203 on. The source's two runs printed 568,030 such lines, and the converted script prints 852,085 lines over its three runs. The console output is about 35 MB for the two source runs, which is why the validation reads the arrays, not the log.
10. **Not carried over.** The commented uniform load (`dl`, whose `eleLoad` is commented out), the commented recorder block and the stress-strain files it would write, the `TDConcreteEXP` settings (its material is commented out), the strain and stress values that no material call uses (`eps1C`, `fc2C`, `EtC`, `Bs`, `Esh`), and the Excel file name. They are listed so that nothing in the source is lost silently. `py_ref/` keeps all the source's Python files, including `CONCRETE_SECTION_FUN.py`, which the main script does not import.
11. **Other sub-models.** The folder's other two sub-models, `CREEP_AND_SHRINKAGE_ANALYSIS_PERIOD` (eigenvalue periods) and `CREEP_AND_SHRINKAGE_SENSITIVITY_ANALYSIS_REBAR_Cdepth`, are not converted here.
