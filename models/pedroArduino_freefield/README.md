# pedroArduino_freefield

**Purpose:** 1D effective-stress site response analysis of a layered soil profile on a 2% slope using coupled u-p (SSPquadUP) elements with PressureDependMultiYield02 material and Lysmer dashpot base.

**Building System:** 30m soil column (3 layers: 2m loose sand, 8m medium sand, 20m dense sand) on an elastic half-space (Vs=700 m/s). Water table at 2m depth. 2% slope with periodic lateral boundaries.

**Model Description:** 2D finite element model with 60 SSPquadUP elements (9-node quadrilateral, coupled solid-fluid) in a single-column mesh. Three PressureDependMultiYield02 materials with calibrated liquefaction parameters. Lysmer dashpot at base (Viscous material, C=875 kN·s/m). Rayleigh damping 2% on modes at 0.2 and 20 Hz. Three-phase analysis: (1) elastic gravity (100 steps, dt=500s), (2) plastic gravity (100 steps, dt=1s), (3) dynamic analysis with SmartAnalyze Transient (7990 steps, dt=0.005s, Newmark 0.5/0.25). Synthetic Ricker wavelet base excitation (peak 0.15 m/s at 1.5 Hz). Post-shake consolidation with 20% damping.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | PressureDependMultiYield02 (3 layers) |
| Lateral System | 1D soil column with periodic boundaries |
| Lateral Loading | Dynamic base excitation (velocity input via dashpot) |
| Earthquake Records | Synthetic Ricker wavelet (dt=0.005s, 7990 pts, peak=0.15 m/s) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy |
| Units | kN, m, kPa, sec (coupled u-p — retained per XMU_Ch8 precedent) |

**References:**
McGann, C., Shin, H., Arduino, P., Mackenzie-Helnwein, P. — University of Washington. freeFieldEffective.tcl.

**Notes:**
Converted from tcl_ref/freeFieldEffective.tcl. Retains source units (kN, m, kPa, sec) as is standard for coupled u-p models — converting to N-mm would make fluid properties (density, permeability) extremely small and risk numerical conditioning (see XMU_Chapter8_1 catalogue entry). Key OpenSeesPy syntax differences: setParameter uses `-val` flag (not `-value`). updateMaterialStage uses `-material` and `-stage` bare keywords. SSPquadUP body forces are in m/s² (element scales internally by density). Gravity uses transient Newmark integration (not LoadControl) for consolidation. SmartAnalyze Transient handles the 7990-step dynamic analysis. Synthetic velocity file created at ground_motions/velocityHistory.in. Run with: conda activate opensy && python model.py
