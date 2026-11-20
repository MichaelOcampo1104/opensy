# SalarDelavar_Cable_Suspension_Bridge_04

**Purpose:** Vertical pushover, free vibration and seismic response (ground motion Y) of a 2D cable suspension bridge idealization. The cables and hangers are corotational truss elements. The deck is a corotational elastic beam, with bending stiffness added (Note 1).

**Building System:** A suspension bridge in the style of the Puente Presidente Ibáñez (Aysén, Chile), idealized in 2D. One equivalent top cable with 22 nodes carries 22 vertical hangers to a deck with 22 nodes. Source values: main span 210 m, top cable 25 m high at the towers with a 20 m sag, top cable equivalent diameter 300 mm, hanger equivalent diameter 50 mm, and an equivalent deck area from the source's 145.6 m diameter.

**Model Description:** 2D model with three DOFs per node (ndm = 2, ndf = 3). The top cable and the hangers are `corotTruss` elements with E = 2.1e7 N/mm² as written in the source. The deck is an `elasticBeamColumn` with a `Corotational` transformation, the source's deck area of 1.67e10 mm², and a bending inertia I = pi D^4 / 64 with D = 145.6 m. The inertia is added; the source has none (Note 1). The deck supports are pinned at both ends, with rotation free. The top cable supports are pinned, and the rotation of every top-cable node is fixed because a cable has no bending stiffness. Each deck node carries a lumped mass of 5e7 / 22 in x and y. The control node is node 33 (deck node 10, x = 100 m). Analyses:
1. Pushover: 250,000 displacement-control steps of 0.01 mm downward at the control node, as a raw `ops.analyze` loop with the source's EnergyIncr 1e-6 test and ModifiedNewton algorithm. This loop is the one exception to AGENT.md §3c for this model, approved by the user on 2026-11-20 (Note 14). It reaches -2500 mm.
2. Free vibration: a static upward deck displacement of 20 mm, then release and Newmark (0.5, 0.25) for 50 s at dt = 0.01 s, undamped and Rayleigh-damped (damping ratio 1 % in mode 1 and 0.6 % in mode 2).
3. Seismic: vertical ground acceleration Ground_Acceleration_Y (factor 9810 mm/s²), HHT with alpha = 1, 50 s at dt = 0.01 s.

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Elastic cables, hangers and deck (E = 2.1e7 N/mm², as written) |
| Lateral System | Suspension bridge: top cable, hangers and deck (cable-stayed idealization not used) |
| Lateral Loading | Pushover (displacement control); free vibration; ground motion Y |
| Earthquake Records | Ground_Acceleration_Y.txt (999 points, dt = 0.01 s); Ground_Acceleration_X.txt is kept but not run |
| Design Year | NA |
| File Format | .py (source: `py_ref/OPENSEES_CABLE_SUSPENSION_BRIDGE_04.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 |
| Units | N, mm, MPa (time in s) |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CABLE_SUSPENSION_BRIDGE/OPENSEES_CABLE_SUSPENSION_BRIDGE_04 (Salar Delavar Ghashghaei). The source script and its helpers, its README, the reference figure and the ground motions are in `py_ref/` and `ground_motions/`. The source's PDF documentation was downloaded but not copied here.

**Why bending stiffness was added:** The source models the cables, the deck and the hangers all as truss elements: 64 members for 80 free DOFs. The undeformed stiffness is therefore singular, and the source's first pushover step fails with its first algorithm (LESSON 48). The conversion adds bending stiffness to the deck, which makes the model stable. The numerical check of the stiffness found no zero eigenvalues. The inertia value is an assumption, because the source gives only an equivalent diameter. Note 1 explains the consequences.

**Validation:** Each run writes `output/validation.txt`. The numbers below come from the run of this folder. (See the section below, filled in after the run.)

- **Periods.** OpenSees and the numpy assembly agree to six digits: T = 0.019664, 0.010718, 0.005374 and 0.004916 s.
- **Initial stiffness.** The first pushover step gives the same load factor as a linear numpy solve (relative difference 4e-13), so the response is linear at the start.
- **Pushover equilibrium** (250,000 steps, all the way to -2500 mm). The vertical reactions sum to the load factor within 2.7e-13 of the maximum load factor, and the horizontal reactions sum to zero within 4.3e-14.
- **Free vibration** (5000 steps, 50 s). Against a linear numpy Newmark run, the undamped maximum difference is 8.1e-5 mm on an initial 20 mm. The damped run (Rayleigh, stiffness term on the deck beams only) differs by 3.5e-7 mm.
- **Seismic** (ground motion Y, 5000 steps). Against the same linear numpy run, the maximum difference is 2.1e-6 mm on a peak of 1.30e-2 mm.
- **Damping ratio.** The log-decrement estimate for the undamped vertical response is -0.0017 %. It is negative, so it does not measure damping; the response is aliased (Note 1).

**Notes:**
1. **Added deck inertia (a deviation from the source).** I = pi D^4 / 64 = 2.21e19 mm^4, so EI = 4.63e26 N.mm^2, using the source's deck diameter. The first period is then 0.0197 s, a deck flexure mode. With dt = 0.01 s, the time step is only about half a period, so the dynamic results are aliased and should not be relied on. The pushover is linear, with a stiffness of about 2.4e12 N/mm. For the deck mode, T scales with I^(-1/2), so a smaller inertia gives longer periods. The inertia should be replaced by the real deck section when it is known (LESSON 50).
2. **Rayleigh damping.** `corotTruss` ignores the Rayleigh stiffness term (LESSON 49), so the stiffness term acts only on the deck beams in the damped runs. The mass term acts on all nodes. The validation shows that the damped run matches a numpy run built the same way.
3. **Units of two source values.** TOTAL_MASS = 5e7 is labelled kg, but it is used as N.s^2/mm, which is 1000 kg per unit. As written, the total mass is 5e10 kg. Read as kg, the mass would be 1000 times smaller. E = 210e5 N/mm^2 is 100 times structural steel. Both values are kept as written, and both need the author's check.
4. **Control node.** The source's `mid_node = int(num_nodes + 0.5 * num_nodes)` is node 33, which is deck node 10 at x = 100 m. It is not the midspan at 105 m, because the node count is even.
5. **Load direction.** The source comment says "horizontal", but the load is vertical: -1 N in y.
6. **Two dynamic runs.** The source runs the seismic analysis twice. The Rayleigh call is inside `if periodTF:`, and both runs set `periodTF = False`, so the two runs are identical. The conversion runs the seismic analysis once (LESSON 52).
7. **Period solver.** The source computes the period at every seismic step with `fullGenLapack`, which OpenSees reports as very slow. The conversion uses the default solver. The validation shows that both give the same initial periods.
8. **Linear solvers and loops.** BandGeneral for the pushover, whose loop is the raw `ops.analyze` loop approved in Note 14. The free-vibration and seismic runs use SmartAnalyze with UmfPack, as in the source.
9. **Retry logic.** The source's retry ladder (ANALYSIS_FUNCTION.py) is replaced by SmartAnalyze's own fall-back (`tryAlterAlgoTypes`). With the added inertia, the first pushover step converges with ModifiedNewton.
10. **Not carried over.** The bilinear fit: BILINEAR_CURVE.py is imported in the source but never called. The histogram and boxplot figures (SALAR_MATH.py): their statistics are not written. The Hysteretic cable option (LINEAR = False) is not run. The X and XY ground-motion options are not run; only Y is. The per-step nodal histories are not kept, only the control node and the reactions. The output folder C:\OPENSEESPY_SALAR is replaced by `output/`.
11. **Reference figure.** `py_ref/OPENSEES_CABLE_SUSPENSION_BRIDGE_04.png` uses 51 nodes per cable (its labels 1 to 204 are DOF numbers). The script uses 22 nodes. The 51-node truss has the same mechanism count: 151 members for 196 free DOFs.
12. **Equivalent area.** The figure says the deck area is equivalent to the deck "area", but the script takes Cable_Dia_01 as a diameter and computes its area as pi D^2 / 4. The conversion keeps the script's use.
13. **Run time.** About 20 minutes on this machine (an estimate: the pushover loop alone is about 6 minutes, from the timing of 2,500 steps; the other runs and the post-processing take the rest).
14. **Pushover loop (resolved).** SmartAnalyze stopped the pushover at step 16,881 (control node at -168.8 mm, load factor 4.07e14 N), and the cause was not identified (LESSON 53). On 2026-11-20 the user approved a raw `ops.analyze` loop for this pushover, as an exception to AGENT.md §3c. The loop keeps the source's EnergyIncr 1e-6 test, ModifiedNewton algorithm and 0.01 mm increment. It runs all 250,000 steps to -2500 mm without failure. The source's fall-back ladder (ANALYSIS_FUNCTION.py) was not triggered and is not reproduced. The free-vibration and seismic runs still use SmartAnalyze.

**Outputs** (in `output/`, git-ignored): `pushover_history.csv` (load factor, control-node displacements and support reactions, every step), `free_undamped_history.csv` and `free_damped_history.csv` (5000 steps), `dynamic_history.csv` (5000 steps, with the first two periods per step), `initial_periods.txt`, `validation.txt`, `pushover_curve.png`, `free_vibration.png`, `dynamic.png`, the views `vis_01_nodes.html` to `vis_04_pre_analysis.html`, `vis_05_deformed_pushover.html`, `vis_08_pushover.html` and `vis_09_dynamic.html`, and the ODBs (`pushover`, `free_undamped`, `free_damped`, `dynamic`).

**References:** The source gives no paper. Its PDF documentation (PDF_OPENSEES_CABLE_SUSPENSION_BRIDGE_04.pdf) was downloaded for reference but not parsed here. Wikipedia (Spanish): Puente Presidente Ibáñez.

**Suggested Citation:** NA (source repository).

**Run:**
```bash
cd models/SalarDelavar_Cable_Suspension_Bridge_04
PYTHONIOENCODING=utf-8 python model.py
```
