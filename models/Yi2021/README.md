# Yi2021

**Purpose:** Static pushover analysis of a single-bay single-story 3D steel moment-resisting frame with Modified Ibarra-Krawinkler (Bilin) concentrated plastic hinges for collapse assessment.

**Building System:** Single-bay, single-story steel moment-resisting frame with W10X33 beams and box-section columns (b=8.02 in, t=0.35 in). The frame is a simplified test case from the WoodFrameBuildingTool suite developed by Xiaolei Xiong (Tongji University) based on the original modelling framework by Henry Burton (Stanford University).

**Model Description:** 3D finite element model (ndm=3, ndf=6) using elasticBeamColumn elements for beams and columns with zero-length concentrated rotational springs at all member ends. Plastic hinges use the Bilin uniaxial material (Modified Ibarra-Krawinkler deterioration model) with parameters calibrated from Lignos & Krawinkler (2011) empirical regression equations for steel W-sections. Rigid diaphragm constraint at roof level via equalDOF. Gravity: manual LoadControl loop. Pushover: SmartAnalyze Static with DisplacementControl to 10% drift. Response collection via opst.post.CreateODB.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel |
| Lateral System | Moment-Resisting Frame |
| Lateral Loading | Static pushover (X-direction) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
- Ibarra, L. F., and Krawinkler, H. (2005). Global collapse of frame structures under seismic excitations. Technical Report 152, Stanford.
- Lignos, D. G., and Krawinkler, H. (2011). Deterioration Modeling of Steel Components in Support of Collapse Prediction of Steel Moment Frames under Earthquake Loading. ASCE Journal of Structural Engineering, 137(11), pp. 1291-1302.

**Suggested Citation:**
Xiong, X., and Burton, H. (2017). WoodFrameBuildingTool — A parametric OpenSees modelling framework for wood and steel moment-resisting frames. Tongji University / Stanford University.

**Notes:** Converted from original Tcl scripts in Xiaolei MomentFrame/ directory. Single-bay single-story simplified test case (NStory=0, NBase=1, XBay=1, ZBay=1). Original unit system: kips, inches, seconds — all values converted to N, mm, MPa. Reference Tcl files preserved in ref/ directory. Run with: `conda activate opensy && python model.py`.
