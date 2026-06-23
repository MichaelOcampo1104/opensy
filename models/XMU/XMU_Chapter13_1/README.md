# XMU_Chapter13_1

**Purpose:** 2D train-bridge interaction with WheelRail contact elements and suspension system.

**Building System:** Rail-bridge-deck system with 80 rail beam elements and 50 bridge beam elements connected via spring-damper pairs. Train model (4 wheelsets, 2 bogies, 1 car body) with primary/secondary suspension.

**Model Description:** 2D model (ndm=2, ndf=3) in SI units (m, kg, N, Pa). Custom WheelRail elements handle wheel-rail contact with rail irregularities. Two-phase analysis: static gravity (10 steps) followed by transient Newmark via SmartAnalyze (3000 steps, dt=0.001 s).

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Elastic (concrete Ec=2.943 GPa, steel E=206 GPa) |
| Lateral System | Rail-bridge-deck + train suspension |
| Lateral Loading | Gravity + transient (WheelRail moving contact) |
| Rail Irregularity | ground_motions/rail_Irreg.txt (4098 lines) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA (requires WheelRail element) |
| Units | SI (m, kg, N, Pa) |

**Notes:** Converted from main.tcl + bridge.tcl + train.tcl. Requires custom OpenSees build with WheelRail element. SI units retained (not converted to N-mm-MPa). Uses SmartAnalyze for transient phase with SP-based wheel motion constraints.

**Run:** `conda activate opensy && python model.py`
