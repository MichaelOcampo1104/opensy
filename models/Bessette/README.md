# Bessette

**Purpose:** 3D monotonic displacement-controlled pushover of the RC1 structure (a 4 m-tall, 2-column braced-frame-like stick) on a fixed base, with elasticBeamColumn members and concentrated IMKPeakOriented rotational hinges at the column bases and floor levels via zeroLength springs.

**Building System:** RC1 structure from the JP3 Parametric Study (Phase 1, Structure Fixed-Base Analyses). A 4.0 m-tall 2-column frame: two column lines at x = ±2.5 m, each built from 4 elasticBeamColumn segments (PDelta) running vertically along Z, tied at the top (z = 4 m) by 5 elasticBeamColumn beam segments (Linear) along X. Concentrated plasticity via 4 zeroLength springs carrying an IMKPeakOriented rotational hinge (RZ) — 2 at the column bases, 2 at the roof beam-column joints. Lumped mass (3.446 tonne each) at 4 roof nodes.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6) with 18 nodes, 13 elasticBeamColumn elements, 4 zeroLength IMK springs, and 2 materials (stiff Elastic + IMKPeakOriented, My = 27.1 kN·m). The zeroLength springs use 6 materials on 6 DOFs: stiff elastic on DOFs 1-5 (rigid), the IMK hinge on DOF 6 (RZ); equalDOF couples the coincident node pairs on UX/UY/UZ so the spring carries rotation only. Analysis: gravity (10 LoadControl steps, KrylovNewton + Penalty) then monotonic DisplacementControl pushover to 10% roof drift (400 steps of 1 mm) via `opst.anlys.SmartAnalyze` with the §12z fiber-hinge recipe (NormDispIncr @ 1e-5, KrylovNewton-primary algoTypes). Lateral pattern defined after loadConst (§12z-1).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (elastic beams) + IMK rotational hinges |
| Lateral System | Concentrated-plasticity braced frame (RC1) |
| Lateral Loading | Static monotonic pushover (gravity + lateral) |
| Earthquake Records | NA (pushover-only; full SSI dynamic model out of scope) |
| Design Year | 2024 |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy |
| Units | N, mm, MPa |

**References:**
Bessette, C. (2024). JP3 Parametric Study — Phase 1, Structure Fixed-Base Analyses, Static Pushover. University of Colorado Boulder. Source Tcl: `tcl_ref/idCf=48_mainStructPushover.tcl`.

**Suggested Citation:**
Bessette, C. (2024). JP3 Parametric Study — S3D Models. University of Colorado Boulder.

**Notes:**
Converted from the fixed-base structure pushover Tcl (`idCf=48_mainStructPushover.tcl`), a self-contained 266-line file from the larger JP3 SSI study. Source is SI (m-tonne-kN-Pa); converted to N-mm-MPa per AGENT.md §12j/§12k (Pa ÷ 1e6 → MPa; lengths ×1000; moments/stiffness ×1e6; masses ×1000).

**SSI EXCLUSION:** The source distribution also contains the full 3D soil-structure-interaction model (`idCf=48_idgm=225_MP_mainNM.tcl` / `..._mainDGC.tcl`) — 2080 `20_8_BrickUP` coupled u-p soil elements, 20 PressureDependMultiYield02 liquefiable-sand materials, a foundation, and a 4-stage analysis (elastic/plastic gravity with `updateMaterialStage`, seismic dynamic with adaptive timestep, post-shake diffusion with permeability update), driven under OpenSeesMP across 3 processors with the Mumps solver. That model is NOT converted here — `20_8_BrickUP` OpenSeesPy signature, OpenSeesMP partition merging, and Mumps substitution are unverified and the compute is hours-long. Only the fixed-base structure pushover is converted.

**Validation (v1.34.0):** Gravity reaches lf=1.00; pushover converges all 400 steps to 10% roof drift with a physically correct yield→peak→softening curve (base shear peaks ~29 kN at ~6% drift, degrades to ~17 kN at 10% drift as the IMK hinges soften). All 6 vis HTMLs render; `pushover_curve.csv` has 400 points.

Run with: `conda activate opensy && python models/Bessette/model.py`
