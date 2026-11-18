# SalarDelavar_Bridge_Viscous_Damper_SDOF

**Purpose:** Free vibration of a bridge substructure with a deck on bearings and viscous dampers. The deck is displaced 0.3 mm by a static step and released. The decay is integrated for 10 s with dt = 0.01 s.

**Building System:** Bridge substructure, given only as lumped parameters. A substructure (pier) mass Ms sits on a spring ks and a damper Cs to ground. A deck mass Mb sits on a bearing (spring kb, damper Cb) and a viscous damper Cd between Ms and Mb. The source gives no section or geometry.

**Model Description:** Two lumped masses in a 2D model (ndm = 2, ndf = 2). The y DOF is restrained at every node, so the motion is along x. Five zeroLength elements: ks and Cs from ground to Ms, and kb, Cb and Cd from Ms to Mb. The dampers are linear (alpha = 1). A static DisplacementControl step moves Mb to 0.3 mm (Ms to 0.1 mm), and the load pattern is then removed. The free vibration runs with Newmark average acceleration (gamma 0.5, beta 0.25) through SmartAnalyze, 1000 steps of 0.01 s. The source's Rayleigh coefficients are set as written, but only the mass term acts (Notes 3).

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=2); motion along x, y restrained |
| Material | Linear springs and linear viscous dampers (lumped; no structural material) |
| Lateral System | Bridge substructure with deck bearing and viscous damper |
| Lateral Loading | Free vibration after a 0.3 mm static deck displacement (no ground motion) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py (source: `py_ref/BRIDGE_VISCOUS_DAMPER_SDOF.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 |
| Units | N, mm, MPa (time in s) |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/BRIDGE_VISCOUS_DAMPER_SDOF (Salar Delavar Ghashghaei). The source script, its `ANALYSIS_FUNCTION.py`, its README and the reference figure are in `py_ref/`.

**Validation:** Each run writes `output/validation.txt`. The results below are from the run of this folder.
- Frequency: omega_1 = 22.3607 rad/s, equal to the closed-form value. T_1 = 0.2810 s. The source's PERIOD = pi/omega_1 = 0.1405 s is half of T_1.
- Static state: u_ms = 0.1000 mm and u_mb = 0.3000 mm, both exact.
- Newmark replica: the same average-acceleration scheme, written in numpy, agrees with OpenSees to 3e-17 mm in displacement, 9e-16 mm/s in velocity and 9e-14 mm/s^2 in acceleration.
- Exact solution: the continuous solution, from the eigen-decomposition of the first-order system, differs from OpenSees by up to 0.0215 mm (7 % of u0) at t = 0.07 s. The cause is the zero start acceleration (Notes 5). With a consistent start, the Newmark error alone is 0.0020 mm.
- Forces: the base reaction equals +Cs * v_ms, and the spring force equals +ks * u_ms. Both agree exactly.
- Damping in the run (dashpots plus the mass term): modal xi = 0.1901 in mode 1 (omega 23.58 rad/s) and 0.7204 in mode 2 (omega 42.41 rad/s). The source's DR = 0.02 is not in the run (Notes 3).
- Figure: not matched. The model's peaks (u0 = 0.3 mm) are 0.2958 mm, 4.152 mm/s, 166.1 mm/s^2 and 21,811 N. The figure's peaks are 0.09862 mm, 1.3855 mm/s, 55.39 mm/s^2 and 7281 N. The same equations with u0 = 0.1 mm give 0.098616 mm (2e-6 relative), 1.3841 mm/s (0.1 %), 55.376 mm/s^2 (0.02 %) and 7270 N (0.15 %). The figure therefore looks like a run with u0 = 0.1 mm, while the script says 0.3 mm. The deliverable keeps 0.3 mm, and nothing is tuned (Notes 6).

**Notes:**
1. **Mass units.** The source labels Ms = 1000 and Mb = 500 in kg, but the values are used as N.s^2/mm, and 1 N.s^2/mm = 1000 kg. Read as kg, the masses would be 1.0 and 0.5 N.s^2/mm. The period would then be 9 ms, shorter than the 10 ms step, and the dashpots would overdamp the motion so that nothing oscillates. The figure's peaks follow the values as written, so they are kept (LESSONS 41).
2. **Stiffness unit.** The source comment gives kb in N/m, but the value 5e5 is used as N/mm. Kept as written.
3. **Damping.** `ops.rayleigh(a0, a1, 0, 0)` applies the stiffness term (a1 = 1.79e-3 s) to zeroLength elements only with `-doRayleigh`, and the source does not pass it. So a1 has no effect in the source's run either. The mass term a0 = 0.04 acts, but gives only 0.09 % damping in mode 1. The damping that remains is the dashpots: modal 19 % in mode 1 and 72 % in mode 2. The source's a0 = (2 * Omega * DR) / Omega simplifies to 2 * DR = 0.04, which has no 1/s; kept as written. Setting `link_rayleigh = True` adds `-doRayleigh` to the two springs, so the stiffness term acts, and the validation then matches the replica with a1 * K (LESSONS 43).
4. **Period.** The source's PERIOD = pi / Omega_1 is half the period. T_1 = 2 pi / Omega_1 = 0.281 s is used here (LESSONS 42).
5. **Start state.** The static step leaves the nodal accelerations at zero. The transient therefore starts without the equilibrium acceleration of Mb (-200 mm/s^2). OpenSees behaves like the zero-start replica, and this is kept (LESSONS 46).
6. **Figure.** Not matched; see Validation. The figure's peak at 0.0986 mm suggests it was made with u0 = 0.1 mm (LESSONS 47).
7. **Dimension.** The model is ndm = 2 with the y DOF restrained, not ndm = 1, because opstool cannot draw one-component nodal loads (LESSONS 44). The equations are those of the 1D chain.
8. **Display positions.** The source puts all three nodes at x = 0. Here they are at 0, 1000 and 2000 mm so that the plots show the chain. OpenSees prints one ZeroLength warning per element (five in total). The response is identical with coincident nodes (LESSONS 45).
9. **Not carried over.** The HystereticSM column relation and its KP/KN plot (the material is commented out in the source). The STIFF secant array (unused, and it divides by the displacement). The SALAR_MATH plotting module (not in this repository; `standards/vis_utils.py` replaces it). The retry ladder in `ANALYSIS_FUNCTION.py` (SmartAnalyze replaces it). The commented-out recorders (`CreateODB` replaces them).
10. **Name.** The source title says SDOF, but the model has two DOFs (Ms and Mb). The name follows the source's repository folder.
11. **Source comments.** The labels "weld", "brce" and "Structure acceleration" in the source comments are leftovers. The variable names are kept.

**Outputs** (in `output/`, git-ignored): `time_history.csv` (1000 steps: time, u_ms, v_ms, u_mb, v_mb, a_mb, spring force, base reaction), `time_history.png` (four panels, as in the source figure), `hysteresis.png` (base reaction against displacement), `validation.txt`, `vis_01_nodes.html` to `vis_04_pre_analysis.html` (V1 to V4), `vis_08_time_history.html` (interactive time histories), `vis_09_hysteresis.html` (interactive spiral), and the ODB (`ModelData-1.zarr`, `RespStepData-1.odb`, responses every 10th step).

**References:** The source gives no paper. Its comments mention viscous dampers in the seismic retrofit of bridges, with no DOI. Source repository: see Source above.

**Suggested Citation:** NA (source repository, no paper).

**Run:**
```bash
cd models/SalarDelavar_Bridge_Viscous_Damper_SDOF
PYTHONIOENCODING=utf-8 python model.py
```
