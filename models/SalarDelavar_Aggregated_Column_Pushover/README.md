# SalarDelavar_Aggregated_Column_Pushover

**Purpose:** 2D cantilever column with a section Aggregator (elastic axial plus Hysteretic moment-curvature). Gravity is applied by LoadControl, then the top node is pushed sideways in 5 mm steps to 1750 mm.

**Building System:** NA. One steel column, 5 m high, with an eight-rectangle section (flanges, webs and side plates): A = 74,800 mm^2, Ix = 3.653e9 mm^4, centroid at (250, 250) mm.

**Model Description:** One `nonlinearBeamColumn` with 5 integration points and a Linear geometric transformation. The base is fixed in x, y and rotation. The top node carries a lumped mass of 20.4 N.s^2/mm (200 kN weight). The section Aggregator takes the axial force from an elastic material (EA = 1.571e10 N) and the moment from a Hysteretic moment-curvature law (MY = 1.131e9 N.mm, MU = 1.538e9 N.mm, with the script's FI_Y = 1.474e-6 1/mm). Gravity is 200 kN on the top node, applied in 10 LoadControl steps, then frozen with loadConst. The pushover is displacement control in x, 5 mm per step, to 1750 mm (350 steps), solved by SmartAnalyze with EnergyIncr 1e-6 and 1000 iterations, Newton first. The source's reference pattern (1 N lateral and -1 N vertical per unit load factor) is kept. Its vertical part adds to the axial force as the lateral load grows.

| Field | Value |
|-------|-------|
| Dimensions | 2D (ndm=2, ndf=3) |
| Material | Steel (Hysteretic moment-curvature, elastic axial) |
| Lateral System | Single cantilever column |
| Lateral Loading | Gravity + static displacement-controlled pushover |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py (source: `py_ref/COLUMN_PUSHOVER_P-M_INTERACTION.py`) |
| OpenSees Version | openseespy 3.8.0, opstool 1.0.26 |
| Units | N, mm, MPa |

**Source:** https://github.com/salardelavar/OPENSEES_SALAR/tree/main/AGGREGATED_AXIAL%E2%80%93FLEXURAL_SECTION/2D_COLUMN_PUSHOVER (Salar Delavar Ghashghaei). OpenSees example 3600: https://opensees.berkeley.edu/OpenSees/manuals/ExamplesManual/HTML/3600.htm. The source files and the reference figure are in `py_ref/`.

**Validation:** The source has no numeric reference output. The only reference is the figure `py_ref/RESULTS_COLUMN_PUSHOVER_P-M_INTERACTION.png`.
- Initial lateral stiffness is 18,413 N/mm, equal to 3EI/L^3 from the section properties. This is exact.
- Gravity gives a base axial force of 200,000 N.
- The figure does not match the script's yield moment. Its first yield kink is about 0.91e9 N.mm, the peak moment about 1.24e9 N.mm, and the end shear about 247 kN. The script gives 1.131e9, 1.538e9 and 308 kN.
- A diagnostic copy outside the repo, with FI_Y = 1.18e-6 1/mm, reproduces the figure's values: MY 9.05e8, peak moment 1.232e9, end shear 246.4 kN, and end axial force 446.4 kN at -0.1421 mm. The initial stiffness is the same. This suggests the figure comes from a different yield curvature than the current script. The deliverable keeps the script's 1.474e-6, as decided by the user. The 1.18e-6 case is recorded here only as a diagnostic.
- The figure's last point (55 kN at 1750 mm) and its rotation axis, which runs to 4.1 rad, are not reproduced. The model's top rotation ends at 0.396 rad, and its last step converges.

**Notes:**
- Source comments disagree with the code. `Weight` is labelled [kg] but is used as a load in N (200 kN). `ops.fix(1, 1, 1, 1)` is commented "free theta", but it fixes all three DOFs. The code is kept as written.
- The source's hand-written fall-back ladder names the algorithm `RaphsonNewton`, which OpenSees does not define. SmartAnalyze's own ladder replaces it.
- The reference-list entry gives Material "RC". The section is steel.

**Outputs** (in `output/`, git-ignored): `pushover_history.csv` (lateral, axial displacement, rotation, axial force, shear, moment per step), `pushover_curves.png`, and the V1 to V5 HTML views.

**Run:**
```bash
cd models/SalarDelavar_Aggregated_Column_Pushover
PYTHONIOENCODING=utf-8 python model.py
```
