# Zhong2022

**Purpose:** Nonlinear dynamic time-history analysis of a 12-story MDOF shear-building model with bilinear hysteretic story springs for seismic uncertainty quantification studies via SimCenter EE-UQ.

**Building System:** 12-story MDOF stick/shear-building model representing a multi-story structure with concentrated story stiffness, strength, and mass. Each story has bilinear hysteretic behavior in both horizontal directions with 2% Rayleigh damping on modes 1 and 3.

**Model Description:** 2D finite element model (ndm=2, ndf=3) with 13 nodes (base + 12 floors) connected by twoNodeLink elements. Each link contains Steel01 bilinear springs for X and Y shear, plus rigid elastic springs for vertical and rotational DOFs. Lumped mass at each floor. Ground motion input via UniformExcitation in both directions. Dynamic analysis uses SmartAnalyze Transient with Newmark integration (γ=0.5, β=0.25). Output EDPs: Peak Inter-story Drift ratio (PID) and Peak Floor Acceleration (PFA) for all 12 stories in both directions.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Steel (bilinear hysteretic) |
| Lateral System | MDOF shear building (stick model) |
| Lateral Loading | Dynamic earthquake (time-history) |
| Earthquake Records | PEER NGA-West2 (RSN6–RSN97); synthetic Ricker wavelet for testing |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
Zhong, K. (2022). SimCenter EE-UQ MDOF building model for seismic uncertainty quantification.

**Suggested Citation:**
Zhong, K. (2022). MDOF building model for seismic UQ. Stanford University / SimCenter.

**Notes:**
Converted from SimCenter EE-UQ MDOF_BuildingModel Tcl reference files (tcl_ref/newmark_solver.tcl, MyRecorder.tcl, MyPostprocess.tcl). Original units: kips, inches, seconds — all values converted to N, mm, MPa. Ground motion records (.AT2 files) from PEER NGA-West2 must be placed in ground_motions/ and configured via gm_file_x / gm_file_y in model.py. A synthetic Ricker wavelet is used by default for testing. Random variables (w, kx, ky, Fyx, Fyy, HRx, HRy) are configurable via module-level constants in the Parameters section.
