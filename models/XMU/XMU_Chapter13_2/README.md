# XMU_Chapter13_2

**Purpose:** 3D single-wheelset model on rigid track with WheelRail contact elements, rail profiles, and lateral excitation.

**Building System:** Rigid track (200 rail nodes per side, fully fixed) with UIC50 rail profile. Single wheelset with rigid axle and mass/inertia properties, connected via WheelRail contact elements.

**Model Description:** 3D model (ndm=3, ndf=6) in SI units (m, kg, N, Pa). Custom WheelRail elements handle left/right wheel-rail contact with rail irregularity and profile data files. Two-phase analysis: static gravity (20 steps, LoadControl) followed by transient Newmark via SmartAnalyze (6000 steps, dt=0.001 s). Lateral excitation applied as y-direction load with pulse time history.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Elastic steel (rail + wheelset) |
| Lateral System | Rigid track + wheelset |
| Lateral Loading | Lateral pulse excitation (y-direction) |
| Rail Profile | ground_motions/UIC50Fine.txt (1003 lines) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA (requires WheelRail element -- custom OpenSees build) |
| Units | SI (m, kg, N, Pa) |

**Notes:** Converted from main.tcl + rail.tcl + wheelset.tcl (XMU Chapter 13.2 example). SI units retained for WheelRail compatibility. WheelRail is a custom element NOT available in standard OpenSeesPy -- requires custom build. Reference Tcl files preserved in model folder.

**Run:** `conda activate opensy && python model.py`
