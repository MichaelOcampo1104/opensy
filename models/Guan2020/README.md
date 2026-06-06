# Guan2020

**Purpose:** Eigenvalue analysis and static pushover of a 2D single-story single-bay steel special moment frame with leaning column for P-Delta effects. Part of the Guan et al. (2020) database of 621 steel SMF buildings.

**Building System:** Single-story, single-bay steel special moment-resisting frame (SMF) with W14×370 columns and W36×160 beam. A leaning column with gravity loads captures P-Delta effects. Designed in accordance with modern codes and standards (ASCE 7).

**Model Description:** 2D finite element model (ndm=2, ndf=3) using elasticBeamColumn elements for frame members and leaning column. Zero-length spring at leaning column top (stiff UX/UY, soft RZ) creates a pin connection. Rigid truss element transfers lateral displacements from frame to leaning column. Floor diaphragm via equalDOF constraints. Four load patterns: dead (101), live (102), earthquake lateral (103), and combined gravity+EQ (104). Gravity: manual LoadControl loop. Pushover: SmartAnalyze Static with DisplacementControl to 5% drift. Eigenvalue analysis for modal periods. Response collection via opst.post.CreateODB.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Steel |
| Lateral System | Special Moment-Resisting Frame (SMF) |
| Lateral Loading | Static pushover (EQ load pattern) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
Guan, X., Burton, H., Shokrabadi, M. (2020). "A Database of Seismic Designs, Nonlinear Models, and Seismic Responses for Steel Moment Resisting Frame Buildings." DesignSafe-CI, DOI: 10.17603/ds2-8yc7-1285.

**Suggested Citation:**
Guan, X., Burton, H., Shokrabadi, M. (2020). Database of Seismic Designs, Nonlinear Models, and Seismic Responses for Steel Moment Resisting Frame Buildings. DesignSafe-CI.

**Notes:** Converted from original Tcl snippet files (Building 10, DynamicAnalysis). Original unit system: kips, inches, seconds — all values converted to N, mm, MPa. Reference Tcl files preserved in ref/ directory. Missing shared library procedures (SectionProperty, rotLeaningCol) reconstructed from context. Run with: `conda activate opensy && python model.py`.
