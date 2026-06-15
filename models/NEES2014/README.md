# NEES2014

**Purpose:** Nonlinear dynamic time-history analysis of a 3-story, 4-bay steel moment-resisting frame (pre-Northridge SAC/FEMA Phase II) with fiber-section beam-column elements for seismic collapse assessment.

**Building System:** 3-story, 4-bay steel moment-resisting frame designed per pre-Northridge Los Angeles SAC/FEMA Phase II specifications. W14 columns (W14x257 exterior, W14x311 interior) and W24–W33 beams (W33x118, W30x116, W24x68). Beam yield strength 36 ksi, column yield strength 54 ksi. Elastic perfectly-plastic panel zones with rigid floor diaphragms.

**Model Description:** 2D finite element model (ndm=2, ndf=3) with 16 nodes (4 base + 12 floor nodes) and 21 nonlinearBeamColumn elements (12 columns + 9 beams). Fiber-discretised W-sections using patch quad with 28 fibers per section (6 web-depth, 2 web-thickness, 4 flange-width, 2 flange-thickness). Steel02 material with 0.3% strain hardening for both beams and columns. PDelta geometric transformation throughout. Rayleigh damping 5% on modes 1 and 3. UniformExcitation in X-direction only. Collapse detection at 80% inter-story drift ratio. Gravity analysis via manual LoadControl loop; dynamic analysis via SmartAnalyze Transient with Newmark integration. EDPs: PID (peak inter-story drift ratio), PFA (peak floor acceleration), PFB (peak base shear), PRD (peak roof displacement), collapse status.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Steel |
| Lateral System | Moment-Resisting Frame (pre-Northridge) |
| Lateral Loading | Dynamic earthquake (time-history) |
| Earthquake Records | FEMA/SAC LA 10-in-50 (44 record pairs); synthetic Ricker wavelet for testing |
| Design Year | pre-1994 (pre-Northridge) |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
FEMA-355-C (2000). State of the Art Report on Systems Performance of Steel Moment Frames Subject to Earthquake Ground Shaking. SAC Joint Venture.
FEMA-440 (2005). Improvement of Nonlinear Static Seismic Analysis Procedures. Appendix F.

**Suggested Citation:**
Khajehhesameddin, P. (2014). 3-Story 4-Bay Steel Moment-Resisting Frame Model for Seismic Collapse Assessment. NEES Project Model-93, Purdue University.

**Notes:**
Converted from original NEES Model-93 Tcl reference files (ModelComponent-6/Model.tcl, Analysis_Dynamic.tcl). All imperial units (kips, inches, ksi) converted to N, mm, MPa using standards/units.py. Ground motion records from FEMA/SAC Phase II (44 LA records, 10% in 50 years). Original Tcl files preserved in Model-93_Tcl/ for reference. Set gm_file_x in model.py to use a specific ground motion from ground_motions/; defaults to synthetic Ricker wavelet. Ground motion MUST be defined after run_gravity() because ops.loadConst() freezes all loads including UniformExcitation to their t=0 values — see AGENT.md §12i.
