# Dino_FramePushover

**Purpose:** Static elastoplastic pushover analysis of a 4-story, 2-bay x 1-bay 3D RC frame with fiber sections under gravity dead loads and inverted triangular lateral loading to 300 mm roof displacement.

**Building System:** 4-story, 2-bay (4.5 m) by 1-bay (5.0 m) 3D reinforced concrete moment frame structure with 4.5 m ground story and 3.0 m upper stories. Fixed at column bases.

**Model Description:** 3D finite element frame model with 28 nodes and 47 nonlinearBeamColumn fiber elements (NC400X400 and NC400X600 columns, NB300X600 and NB300X500 beams) using Concrete01 and Steel01 fibers with Aggregator shear and torsional stiffness. Gravity applied incrementally with 10 LoadControl steps; lateral inverted-triangular pushover applied via SmartAnalyze DisplacementControl to 300 mm (100 steps x 3 mm) at roof node 8. Validated against Dino Example 04 ref/node8.out.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC |
| Lateral System | Moment-Resisting Frame (MRF) |
| Lateral Loading | Static pushover (inverted triangular displacement control) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
http://dinochen.com

**Suggested Citation:**
Dino Chen, OpenSees Tutorial Example 04: Frame Structure Pushover Analysis (实例4_框架结构推覆分析), http://dinochen.com

**Notes:** Dino Example 04 pushover analysis. Model folder contains ETABS (EXAM04.s2k) and OpenSees reference files. Solved with SmartAnalyze, 100/100 pushover steps match ref/node8.out within 0.00045 mm (0.00015%).
