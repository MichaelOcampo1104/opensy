# SalarDelavar_Cable_Suspension_Foot_Bridge_03

**Purpose:** Vertical pushover, free vibration and the response to two ground motions (X and Y) of the single cable chain of the source folder `CABLE_SUSPENSION_FOOT_BRIDGE` (sub-model 03). The source's truss chain is given bending stiffness so that it is stable (Note 1).

**Building System:** A single cable chain over an 18 m span. Its 51 nodes lie on an arc: the ends are 0.5 m high and the midspan node is at ground level (y = 0). They are joined by 50 members, each with the source's element area of ten 32 mm cables (8042.5 mm^2). There is no deck and no hanger. The source's "Cable_Dia_01" = 32 mm is the diameter of one cable.

**Model Description:** 2D model with three DOFs per node (ndm = 2, ndf = 3). Each member is a corotational `elasticBeamColumn` with E = 2.1e7 N/mm^2 as written, the source's element area (8042.5 mm^2) and an added bending inertia I = 5.147e6 mm^4 (Note 1). Both ends are pinned: translations fixed, end rotations free (Note 2). Each node carries a lumped mass of 50000 / 51 = 980.4 N.s^2/mm in x and y, with no rotational mass, as in the source. The control node is node 26, the midspan node (x = 9 m, y = 0), which is the source's `mid_node = num_nodes // 2 + 1`. The load is -1 N in y at the control node. Analyses:
1. Pushover: 5000 displacement-control steps of 0.01 mm downward, to -50 mm, through SmartAnalyze with EnergyIncr 1e-10 and ModifiedNewton, as in the source.
2. Free vibration: a static upward midspan displacement of 0.1 mm, release, and Newmark (0.5, 0.25) for 50 s at dt = 0.01 s. Undamped, and damped with the source's assumed Rayleigh coefficients (ratio 5 %, reference stiffness 1 N/mm). Tolerance 1e-10, as in the source.
3. Seismic: ground motions X (OPENSEES_SPRING_SEISMIC_01) and Y (OPENSEES_SPRING_SEISMIC_02) applied together, with HHT called with alpha = 0.9 as a single argument, for 50 s at dt = 0.01 s. Undamped, and damped with the assumed Rayleigh coefficients (reference stiffness 1000 N/mm). Tolerance 1e-6, as in the source's dynamic run.

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Elastic (E = 2.1e7 N/mm^2, as written) |
| Lateral System | Single cable chain of corotational beams (bending stiffness added) |
| Lateral Loading | Pushover (displacement control); free vibration; ground motions X and Y |
| Earthquake Records | OPENSEES_SPRING_SEISMIC_01.txt (X) and _02.txt (Y), 999 points at 0.01 s (9.98 s), factor 1 (records used as mm/s^2, GMfact = 1 in the source) |
| Design Year | NA |
| File Format | .py (source: `py_ref/OPENSEES_CABLE_SUSPENSION_BRIDGE_03.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 |
| Units | N, mm, MPa (time in s) |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CABLE_SUSPENSION_FOOT_BRIDGE/CABLE_STRUCTURE_03 (Salar Delavar Ghashghaei). The source script, the folder README (`py_ref/README_FOOT_BRIDGE.md`) and the source's plotting helper (`py_ref/PLOT_2D_TRUSS.py`, not run) are in `py_ref/`. The two records are identical to those of sub-model 01 (checksums compared). The source's reference figure is a .jpg in the GitHub folder, which was not downloaded.

**Why bending stiffness was added:** The source models the chain as 50 truss members on 98 free translational DOFs (both ends pinned). The tangent stiffness has rank 50, so the undeformed chain is singular (LESSON 48). As written, OpenSees reported success at the first steps, but the support reactions did not match the load factor (a difference of about 1e-5 N with a load factor of about 1e-13), and step 4 did not converge (LESSON 58). The conversion adds bending stiffness to every member, using the solid circle with the same area as the source's element (the rule used for the cable model). With that change the stiffness matrix is positive definite on all 149 free DOFs, and the OpenSees run converges at every step.

**Validation:** Each run writes `output/validation.txt`. The numbers below come from the run of this folder.
- **Periods.** OpenSees and the numpy assembly agree to six digits: T = 8.227351, 3.650971, 2.344716 and 2.052903 s.
- **First pushover step.** The load factor differs from a linear numpy solve by 1.12e-4 (relative). The linear solve omits the geometric stiffness (LESSON 56).
- **Pushover equilibrium** (all 5000 steps). The vertical reaction sum differs from the load factor by 1.94e-12 of the maximum load factor, and the horizontal reaction sum is 2.00e-11 of the same.
- **Free vibration** (5000 steps, 50 s). Against a linear numpy Newmark run with the same time step, the maximum difference is 1.11e-4 mm undamped (0.11 % of the 0.1 mm initial displacement) and 2.80e-5 mm damped. The replica uses the same time step, so this tests the implementation, not the time-step error (Note 6).
- **Modal damping.** The assumed coefficients give first-mode ratios of 284.6 % (free run) and 9.62 % (dynamic run) in this model. If only the mass term acted, as in the source's truss model, the ratios would be 0.0195 % and 0.617 % (Note 3).
- **Damping ratio** from log decrement: 0.0 for both free runs. The undamped run does not decay, and the damped run has no oscillation peaks.
- **Seismic.** Not checked against numpy: the replica uses Newmark, while the source's HHT with alpha = 0.9 is a different scheme (Note 5).

**Notes:**
1. **Added bending stiffness (approved for this sub-model, as for the cable model).** Each member has I = pi * D^4 / 64 with D = 101.19 mm, the diameter of the solid circle with the same area as the source's element (8042.5 mm^2). I = 5.147e6 mm^4 and EI = 1.081e14 N.mm^2. The bending inertia is an assumption. The first period (8.23 s) is compared with the record length (9.98 s) and with the time step (about 820 steps per period) (LESSON 50).
2. **Pinned ends.** The source's ends are pins: ux and uy are fixed, and the source truss has no rotation to fix. The conversion keeps the end rotations free. A scratch test with the end rotations clamped gives a stiffer chain (first period 5.27 s). That test is not used.
3. **Rayleigh damping (source coefficients, as written).** The free run has alpha = 2.98e-4 1/s and beta = 7.45 s (K_ref = 1 N/mm). The dynamic run has alpha = 9.43e-3 1/s and beta = 0.236 s (K_ref = 1000 N/mm). The source's truss model ignores the stiffness term (LESSON 49), so the source damps only the mass term. This model applies both terms, and the modal ratios for modes 1 to 4 are:
   - all members carry the stiffness term: free run 284.6, 641.4, 998.7 and 1140.6 %; dynamic run 9.62, 20.56, 31.76 and 36.22 %;
   - mass term only, as in the source: free run 0.0195, 0.0087, 0.0056 and 0.0049 %; dynamic run 0.617, 0.274, 0.176 and 0.154 %.

   The free damped run is overdamped in mode 1. Its midspan displacement decays without oscillating: 0.1 mm at the start, 0.026 mm at 10 s, and 0.00012 mm at 50 s. The coefficients are kept as written, by the user's choice on 2026-11-24 (LESSON 54 and LESSON 59).
4. **Mass unit.** TOTAL_MASS = 50000 is labelled kg in the source, but it is used as N.s^2/mm (1 N.s^2/mm = 1000 kg), which is 5e7 kg as written. Read as kg, the mass would be 1000 times smaller and the first period 0.260 s. The value is kept as written (LESSON 55). On this reading the first period is close to the record length, so the seismic response is informative.
5. **Time step and short-period modes.** Of the 98 translational modes, 34 have periods shorter than dt = 0.01 s. The shortest is 0.00455 s. The source's truss chain has the same short periods and the same count, because they come from its axial stiffness EA/L and nodal mass as written. The beam conversion did not create them. The source's time step is kept, so these modes are not resolved. HHT with alpha = 0.9 (as written) adds high-frequency damping, but its effect on these modes was not measured. The reactions include the inertia of these modes: the undamped seismic run has a peak horizontal reaction of 11.0 kN at 8.2 s, more than six times the rigid-body inertia of the record (5e4 N.s^2/mm x 0.034 mm/s^2, about 1.7 kN). The free undamped run has a peak vertical reaction of 10.7 kN at 3.4 s, against 4.55 kN for the static load of the 0.1 mm displacement. The reactions are therefore not rigid-body values, and they should not be read as physical until the time step is checked (LESSON 60).
6. **Numpy checks.** The replica uses the same time step and the Newmark scheme, so it confirms the implementation but not the accuracy of the time step (Note 5). It does not check the HHT runs.
7. **Tolerances.** The source uses 1e-10 for the pushover and the free run, and 1e-6 for the dynamic run. The 02 source used 1e-14 for both transient runs. Each value is kept as written.
8. **Control node.** Node 26 is the midspan node. Sub-models 01 and 02 use node 76, the source's `int(1.5 * 51)`, which is not at midspan.
9. **Load direction.** The source applies a vertical load (-1 N in y) at the midspan node, and its comment says "vertical", so there is no mismatch here.
10. **Solver.** SmartAnalyze converged all 5000 pushover steps (to -50 mm) and all 5000 steps of each transient run. The run log has no failure messages.
11. **Not carried over.** The source's `ANALYSIS` retry function (SmartAnalyze replaces it), the histogram and boxplot helpers, the per-node recorder files (DTH_PUSH.txt and similar), the output folder `C:\OPENSEESPY_SALAR`, and the eigenvalue blocks. The source keeps the eigenvalue blocks in string literals, or runs them only when `periodTF` is True, and it is False in both dynamic runs.
12. **Reference figure.** The source folder has no figure (Source above).
13. **Run time.** About 14 minutes on this machine, from the first output (08:32) to the last log entry (08:46).

**Outputs** (in `output/`, git-ignored): `pushover_history.csv` (5000 steps), `free_undamped_history.csv` and `free_damped_history.csv`, `dynamic_undamped_history.csv` and `dynamic_damped_history.csv` (5000 steps each), `initial_periods.txt`, `validation.txt`, `pushover_curve.png`, `free_vibration.png`, `dynamic.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_pushover.html`, `vis_08_pushover.html` and `vis_09_dynamic.html`, the ODBs and `ModelData-*.zarr` folders for the five analyses, and `run.log`.

**References:** The source repository and its folder README (`py_ref/README_FOOT_BRIDGE.md`). The source script's header lists reference links (lines 76 to 98), including a Semantic Scholar record of a cable-suspended pedestrian bridge (line 96) and a PCI Journal article (line 78). None of them was opened.

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Cable_Suspension_Foot_Bridge_03
PYTHONIOENCODING=utf-8 python model.py
```
