# SalarDelavar_Cable_Suspension_Foot_Bridge_01

**Purpose:** Vertical pushover, free vibration and the response to two ground motions (X and Y) of a 2D cable suspension footbridge, sub-model 01 of the source folder `CABLE_SUSPENSION_FOOT_BRIDGE`. The deck is given bending stiffness (Note 1).

**Building System:** A cable suspension footbridge idealization over a 50 m span. One top cable with 51 nodes, 3.5 m above the deck at the towers and with a 1 m sag, carries 51 vertical hangers to a 51-node deck at ground level (y = 0). Source values: top cable diameter 18 mm, hangers 10 mm, deck 25 mm. The source uses these "Cable_Dia" values as diameters.

**Model Description:** 2D model with three DOFs per node (ndm = 2, ndf = 3). The top cable and the hangers are `corotTruss` elements with E = 2.1e7 N/mm^2 as written. The deck is a `corotational` `elasticBeamColumn` with the source's area (491 mm^2) and an added bending inertia I = pi d^4 / 64 = 1.92e4 mm^4 (EI = 4.03e11 N.mm^2). The top-cable ends are fully fixed and the deck ends are pinned. The rotation of every interior top-cable node is fixed, because a cable has no bending stiffness. Each deck node carries a lumped mass of 500000 / 51 = 9804 N.s^2/mm in x and y. The control node is node 76 (deck node 25, x = 24 m). Analyses:
1. Pushover: 50,000 displacement-control steps of 0.01 mm downward, to -500 mm, through SmartAnalyze with EnergyIncr 1e-10 and ModifiedNewton, as in the source.
2. Free vibration: a static upward deck displacement of 2 mm, release, and Newmark (0.5, 0.25) for 50 s at dt = 0.01 s. Undamped, and damped with the source's assumed Rayleigh coefficients (ratio 5 %, reference stiffness 1 N/mm).
3. Seismic: ground motions X (OPENSEES_SPRING_SEISMIC_01) and Y (OPENSEES_SPRING_SEISMIC_02) applied together, factor 1 as written, with HHT called with alpha = 0.9 as a single argument, for 50 s at dt = 0.01 s. Undamped, and damped with the assumed Rayleigh coefficients (reference stiffness 1000 N/mm).

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Elastic cables, hangers and deck (E = 2.1e7 N/mm^2, as written) |
| Lateral System | Cable suspension footbridge: top cable, hangers and deck |
| Lateral Loading | Pushover (displacement control); free vibration; ground motions X and Y |
| Earthquake Records | OPENSEES_SPRING_SEISMIC_01.txt (X) and _02.txt (Y), 999 points each, factor 1 |
| Design Year | NA |
| File Format | .py (source: `py_ref/OPENSEES_CABLE_SUSPENSION_BRIDGE_01.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 |
| Units | N, mm, MPa (time in s) |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CABLE_SUSPENSION_FOOT_BRIDGE/CABLE_STRUCTURE_01 (Salar Delavar Ghashghaei). The source script, the folder README (`py_ref/README_FOOT_BRIDGE.md`), the reference figure and the two records are in `py_ref/` and `ground_motions/`.

**Why bending stiffness was added:** The source models the cables, the deck and the hangers all as truss elements: 151 members for 196 free DOFs. The undeformed stiffness is therefore singular, as for the cable model (LESSON 48). The conversion adds bending stiffness to the deck. The first period is finite in both OpenSees and numpy, so the stiffness is positive definite on the free DOFs, and the OpenSees run converges every step. The inertia is an assumption, for the same reason as in the cable model (Note 1).

**Validation:** Each run writes `output/validation.txt`. The numbers below come from the run of this folder.
- **Periods.** OpenSees and the numpy assembly agree to six digits: T = 1963.29, 872.58, 490.82 and 314.13 s.
- **First pushover step.** The load factor differs from a linear numpy solve by 1.0e-4 (relative). The linear solve omits the geometric stiffness of the cables (LESSON 56).
- **Pushover equilibrium** (all 50,000 steps). The vertical reactions sum to the load factor within 2.7e-13 of the maximum load factor, and the horizontal reactions sum to zero within 8.1e-12.
- **Free vibration** (5000 steps, 50 s). Against a linear numpy Newmark run, the undamped maximum difference is 1.5e-3 mm on the initial 2 mm (0.08 %). The damped difference is 1.4e-3 mm. The difference is set by the initial state, which the linear replica takes from a linear static solve.
- **Damping ratio.** The log-decrement estimates are 0.0 for both runs, because the response has no oscillation peaks in 50 s (Note 3).
- **Seismic.** Not checked against a numpy run: the replica uses Newmark, while the source's HHT with alpha = 0.9 is not that scheme (Note 6).

**Notes:**
1. **Added deck inertia (a deviation from the source).** I = pi * 25^4 / 64 = 1.92e4 mm^4, the solid circle with the deck's source diameter. This follows the same rule as the cable model (LESSON 50).
2. **Mass unit.** TOTAL_MASS = 500000 is labelled kg in the source, but it is used as N.s^2/mm (1 N.s^2/mm = 1000 kg), which is 5e8 kg as written. As written, the first period is 1963 s, and the ground-motion responses are small: the largest vertical displacement is 0.015 mm, reached at 30 s, after the 10 s records end. Read as kg, the mass would be 1000 times smaller and the first period about 62 s. The value is kept as written, and the choice belongs to the author or the user (LESSON 55).
3. **Rayleigh damping (source).** The coefficients come from an assumed frequency, not from the modes: omega1 = sqrt(K_ref / M) and omega2 = 2 omega1, with K_ref = 1 N/mm in the free run and 1000 N/mm in the dynamic run (the source's KE). The free run has alpha = 9.4e-5 1/s and beta = 23.6 s. The dynamic run has alpha = 2.98e-3 1/s and beta = 0.745 s. The stiffness term acts on the deck beams only (LESSON 49). The 5 % ratio is therefore not the structure's damping (LESSON 54).
4. **Free vibration.** The deck moves slowly: from 2 mm to 1.63 mm (undamped) and to 1.69 mm (damped) in 50 s.
5. **Young's modulus.** E = 2.1e7 N/mm^2 is 100 times structural steel. It is kept as written, as in the cable model.
6. **HHT.** The source calls `ops.integrator('HHT', 0.9)` with one argument, and the conversion keeps that call. The numpy replica does not cover it, so the seismic results are not checked independently.
7. **Control node.** The source's `mid_node = int(num_nodes + 0.5 * num_nodes)` is node 76, which is deck node 25 at x = 24 m. The midspan is at x = 25 m.
8. **Load direction.** The source comment says "horizontal", but the load is vertical: -1 N in y.
9. **Solver tolerances.** EnergyIncr 1e-10 for the pushover and 1e-14 for the free and seismic runs, as written. SmartAnalyze converged every step, so no fallback was needed.
10. **Not carried over.** The histogram and boxplot helpers (`HISROGRAM_BOXPLOT` and the plotly function). The eigenvalue blocks, which the source keeps inside string literals, and its modal call, which runs only when `periodTF` is True (it is False in both dynamic runs). The per-node recorder files: the conversion keeps the control node's history and the support reactions in CSV, and the full model in the ODB. The output folder `C:\OPENSEESPY_SALAR`, replaced by `output/`.
11. **Reference figure.** `py_ref/OPENSEES_CABLE_SUSPENSION_BRIDGE_01.png` was not compared with the converted results.
12. **Run time.** About 25 minutes on this machine (13:45 to 14:10), from the first output to the last log entry.

**Outputs** (in `output/`, git-ignored): `pushover_history.csv` (50,000 steps), `free_undamped_history.csv` and `free_damped_history.csv`, `dynamic_undamped_history.csv` and `dynamic_damped_history.csv` (5000 steps each), `initial_periods.txt`, `validation.txt`, `pushover_curve.png`, `free_vibration.png`, `dynamic.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_pushover.html`, `vis_08_pushover.html` and `vis_09_dynamic.html`, the ODBs and `ModelData-*.zarr` folders for the five analyses, and `run.log`.

**References:** The source repository and its folder README (`py_ref/README_FOOT_BRIDGE.md`). The source script cites a paper (an IJSDR link, line 67 of the script), which was not opened.

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Cable_Suspension_Foot_Bridge_01
PYTHONIOENCODING=utf-8 python model.py
```
