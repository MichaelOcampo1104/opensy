# elkady2020

**Purpose:** Nonlinear dynamic earthquake analysis of a 3-story 1-bay steel special concentrically-braced frame (SCBF) to study seismic collapse capacity of CBF systems.

**Building System:** 3-story, 1-bay steel special concentrically-braced frame (SCBF) with wide-flange columns (W12x106), wide-flange beams, and circular HSS brace sections. Moment frame (MF) resists lateral loads with fiber-section columns and ModElasticBeam2d beams with IMK rotational springs at beam ends and panel zones. An elastic gravity frame (EGF) leaning column captures P-Delta effects from tributary gravity loads.

**Model Description:** 2D finite element model with corner and mid-span gusset plate connections, fiber-section CHS braces with fatigue-wrapped Steel02 materials, and gusset plate rotational springs (Spring_Gusset). Panel zones use the Skiadopoulos-Elkady-Lignos hysteretic spring model (Spring_PZ). Columns modeled with fiber WF sections (Voce-Chaboche UVCuniaxial material). Gravity uses SmartAnalyze (load-controlled static); dynamic uses DynamicAnalysisCollapseSolverX with Newmark integration. ODB response collection via opst.post.CreateODB.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Steel |
| Lateral System | Special Concentrically-Braced Frame (SCBF) with gusset plates |
| Lateral Loading | Dynamic earthquake |
| Earthquake Records | 1994 Northridge - Canoga Park (NR94cnp.txt), dt=0.01s, 2495 points |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
Elkady, A. and Lignos, D.G. (2014). Modeling of the Composite Action in Fully Restrained Beam-to-Column Connections. Earthquake Engineering & Structural Dynamics 43(13).

**Suggested Citation:**
Elkady, A. and Lignos, D.G. (2014). Modeling of the Composite Action in Fully Restrained Beam-to-Column Connections. Earthquake Engineering & Structural Dynamics 43(13).

**Notes:** Converted from original Tcl script (SCBF3B.tcl) by Dr. Ahmed Elkady (github.com/amaelkady/OpenSEES_Models_CBF). All units converted from imperial (ksi, inches, kips) to N-mm-MPa. Model uses fiber-section columns, fiber CHS braces with fatigue, and gusset plate models.
