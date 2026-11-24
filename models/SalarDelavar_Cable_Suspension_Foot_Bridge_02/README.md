# SalarDelavar_Cable_Suspension_Foot_Bridge_02

**Purpose:** Vertical pushover, free vibration and the response to two ground motions (X and Y) of a 2D cable suspension footbridge, sub-model 02 of the source folder `CABLE_SUSPENSION_FOOT_BRIDGE`. The deck is hung from the cable and given bending stiffness (Note 1).

**Building System:** A cable suspension footbridge over a 50 m span. One top cable with 51 nodes, 12 m above the base at the towers and with a 1 m sag, carries 51 vertical hangers, each 2 m long, to a 51-node deck that hangs 2 m below the cable and follows its sag. Source values: top cable diameter 18 mm, hangers 10 mm, deck 25 mm. The source uses these "Cable_Dia" values as diameters.

**Model Description:** 2D model with three DOFs per node (ndm = 2, ndf = 3). The top cable and the hangers are `corotTruss` elements with E = 2.1e7 N/mm^2 as written. The deck is a `corotational` `elasticBeamColumn` with the source's area (491 mm^2) and an added bending inertia I = pi d^4 / 64 = 1.92e4 mm^4 (EI = 4.03e11 N.mm^2). Because the deck follows the sloped cable, its segments are not horizontal. The top-cable ends are fully fixed and the deck ends are pinned. The rotation of every interior top-cable node is fixed, because a cable has no bending stiffness. Each deck node carries a lumped mass of 500000 / 51 = 9804 N.s^2/mm in x and y. The control node is node 76 (deck node 25, x = 24 m, y = 9.0 m). It is the source's `mid_node = int(1.5 × 51)`, which is not at midspan (x = 25 m). Analyses:
1. Pushover: 50,000 displacement-control steps of 0.01 mm downward, to -500 mm, through SmartAnalyze with EnergyIncr 1e-10 and ModifiedNewton, as in the source.
2. Free vibration: a static upward deck displacement of 2 mm, release, and Newmark (0.5, 0.25) for 50 s at dt = 0.01 s. Undamped, and damped with the source's assumed Rayleigh coefficients (ratio 5 %, reference stiffness 1 N/mm).
3. Seismic: ground motions X (OPENSEES_SPRING_SEISMIC_01) and Y (OPENSEES_SPRING_SEISMIC_02) applied together, with HHT called with alpha = 0.9 as a single argument, for 50 s at dt = 0.01 s. Undamped, and damped with the assumed Rayleigh coefficients (reference stiffness 1000 N/mm).

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Elastic cables, hangers and deck (E = 2.1e7 N/mm^2, as written) |
| Lateral System | Cable suspension footbridge: top cable, hangers and a sloped deck |
| Lateral Loading | Pushover (displacement control); free vibration; ground motions X and Y |
| Earthquake Records | OPENSEES_SPRING_SEISMIC_01.txt (X) and _02.txt (Y), 999 points at 0.01 s (9.98 s), factor 1 (records used as mm/s^2, GMfact = 1 in the source) |
| Design Year | NA |
| File Format | .py (source: `py_ref/OPENSEES_CABLE_SUSPENSION_BRIDGE_02.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 |
| Units | N, mm, MPa (time in s) |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CABLE_SUSPENSION_FOOT_BRIDGE/CABLE_STRUCTURE_02 (Salar Delavar Ghashghaei). The source script, the folder README (`py_ref/README_FOOT_BRIDGE.md`), the reference figure and the two records are in `py_ref/` and `ground_motions/`. The records are identical to those of sub-model 01.

**Why bending stiffness was added:** The source models the cables, the deck and the hangers all as truss elements: 151 members for 196 free DOFs. The undeformed stiffness is therefore singular, as for the cable model and sub-model 01 (LESSON 48). The conversion adds bending stiffness to the deck. The first period is finite in both OpenSees and numpy, so the stiffness is positive definite on the free DOFs, and the OpenSees run converges every step. The inertia is an assumption, for the same reason as in the cable model (Note 1).

**Validation:** Each run writes `output/validation.txt`. The numbers below come from the run of this folder, checked against a numpy assembly that includes the sloped deck segments (LESSON 57).
- **Periods.** OpenSees and the numpy assembly agree to six digits: T = 1968.56, 874.22, 491.65 and 314.63 s.
- **First pushover step.** The load factor differs from a linear numpy solve by 1.04e-4 (relative). The linear solve omits the geometric stiffness of the cables (LESSON 56).
- **Pushover equilibrium** (all 50,000 steps). The maximum difference between the sum of the vertical reactions and the load factor is 1.92e-13 of the maximum load factor. The sum of the horizontal reactions is 3.22e-12 of the same.
- **Free vibration** (5000 steps, 50 s). Against a linear numpy Newmark run, the maximum difference is 2.72e-3 mm undamped and 1.97e-3 mm damped, on the initial 2 mm (0.14 % and 0.10 %). The difference comes from the initial state, because the linear replica takes the 2 mm shape from a linear static solve, and from the geometric stiffness (LESSON 56).
- **Damping ratio.** The log-decrement estimates are 0.0 for both runs. The response has fewer than two oscillation peaks in 50 s (the first period is 1968 s), so there is no decrement to measure (Note 3).
- **Seismic.** Not checked against a numpy run: the replica uses Newmark, while the source's HHT with alpha = 0.9 is a different scheme (Note 6).

**Notes:**
1. **Added deck inertia (a deviation from the source).** I = pi * 25^4 / 64 = 1.92e4 mm^4, the solid circle with the deck's source diameter. This is the same rule as sub-model 01 and the cable model (LESSON 50).
2. **Mass unit.** TOTAL_MASS = 500000 is labelled kg in the source, but it is used as N.s^2/mm (1 N.s^2/mm = 1000 kg), which is 5e8 kg as written. As written, the first period is 1968.56 s. Read as kg, the mass would be 1000 times smaller and the first period about 62 s. The value is kept as written, and the choice belongs to the author or the user (LESSON 55).
3. **Rayleigh damping (source).** The coefficients come from an assumed frequency, not from the modes: omega1 = sqrt(K_ref / M) and omega2 = 2 omega1, with K_ref = 1 N/mm in the free run and 1000 N/mm in the dynamic run (the source's KE). The free run has alpha = 9.4e-5 1/s and beta = 23.6 s. The dynamic run has alpha = 2.98e-3 1/s and beta = 0.745 s. The source's eigenvalue-based Rayleigh blocks are inside string literals, so only the assumed-frequency block runs. The stiffness term acts on the deck beams only (LESSON 49). The 5 % ratio is therefore not the structure's damping (LESSON 54).
4. **Pushover and free vibration.** At -500 mm the control node has moved -2.61 mm in x, because the sloped geometry couples vertical and horizontal motion. In the free run the deck moves from 2 mm to 1.67 mm (undamped) and to 1.73 mm (damped) at 50 s.
5. **Seismic response.** The largest vertical displacement is 0.0261 mm (undamped) and 0.0231 mm (damped), both reached at the end of the run (50 s). The largest horizontal displacement is 0.00243 mm (undamped, at 38.55 s) and 0.00055 mm (damped, at 10.4 s). The largest support reactions are 5.9 kN horizontal and 0.67 kN vertical (undamped), and 0.84 kN and 0.66 kN (damped). The records end at 9.98 s. After that, the vertical response is a long-period drift that is still growing at 50 s, because the first period is 1968 s (Note 2). The seismic values therefore do not describe a settled response (LESSON 55).
6. **HHT.** The source calls `ops.integrator('HHT', 0.9)` with one argument, and the conversion keeps that call. The numpy replica does not cover it, so the seismic results are not checked independently.
7. **Young's modulus.** E = 2.1e7 N/mm^2 is 100 times structural steel. It is kept as written, as in the other models.
8. **Load direction.** The source comment on the load line says "horizontal", but the load is vertical: -1 N in y, at the control node.
9. **Solver tolerances.** EnergyIncr 1e-10 for the pushover and 1e-14 for the free and seismic runs, as written. All 50,000 pushover steps and all 5000 steps of each transient run completed, and the run log has no failure messages.
10. **Not carried over.** The source's histogram and boxplot helpers (`HISROGRAM_BOXPLOT` and the plotly function). Its eigenvalue blocks, which are inside string literals or run only when `periodTF` is True (it is False in both dynamic runs). Its per-node recorder files: the conversion keeps the control node's history and the support reactions in CSV, and the full model in the ODB. The output folder `C:\OPENSEESPY_SALAR`, replaced by `output/`.
11. **Reference figure.** `py_ref/OPENSEES_CABLE_SUSPENSION_BRIDGE_02.png` was not compared with the converted results.
12. **Run time.** About 15 minutes on this machine, from the first output (14:14) to the last log entry (14:29).

**Outputs** (in `output/`, git-ignored): `pushover_history.csv` (50,000 steps), `free_undamped_history.csv` and `free_damped_history.csv`, `dynamic_undamped_history.csv` and `dynamic_damped_history.csv` (5000 steps each), `initial_periods.txt`, `validation.txt`, `pushover_curve.png`, `free_vibration.png`, `dynamic.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_pushover.html`, `vis_08_pushover.html` and `vis_09_dynamic.html`, the ODBs and `ModelData-*.zarr` folders for the five analyses, and `run.log`.

**References:** The source repository and its folder README (`py_ref/README_FOOT_BRIDGE.md`). The source script cites a paper (a Semantic Scholar link, line 62 of the script), which was not opened.

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Cable_Suspension_Foot_Bridge_02
PYTHONIOENCODING=utf-8 python model.py
```
