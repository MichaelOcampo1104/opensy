# Guan2020_Building_1002

**Purpose:** 9-story 3-bay 2D steel special moment frame (SMF) with Steel01 plastic hinges, rigid panel zone joints, and leaning column for P-Delta effects. Part of the Guan et al. (2020) database of 621 steel SMF buildings (Building 1002).

**Building System:** 9-story, 3-bay steel special moment-resisting frame with W14 columns (W14×145–W14×730) and W21–W36 beams (W21×93–W36×262). Column splices at multiple levels with varying section sizes. A leaning column with gravity loads captures P-Delta effects.

**Model Description:** 2D finite element model (ndm=2, ndf=3) with 210 nodes using elasticBeamColumn elements for all frame members and leaning column. Rigid joints enforced via equalDOF master-slave constraints (simpler than the original 8-element panel zone rectangles). Steel01 bilinear hinges at all beam and column ends calibrated from IMK Lignos-Krawinkler (2011) regression equations with stiffness modification factor n=10. Floor diaphragm via equalDOF constraints at each level. Three analysis variants provided:

| Variant | File | Analysis type |
|---------|------|---------------|
| Pushover | `model_pushover.py` | Gravity + displacement-controlled static pushover (SmartAnalyze) |
| Dynamic | `model_dynamic.py` | Gravity + eigenvalue + transient time-history (SmartAnalyze, Newmark) |
| Eigenvalue | `model_eigen.py` | Gravity + eigenvalue (modal periods + eigen visualisation) |

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Steel |
| Lateral System | Special Moment-Resisting Frame (SMF) |
| Lateral Loading | Pushover + Dynamic (ground motion) |
| Earthquake Records | NA (synthetic Ricker wavelet for testing) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
Guan, X., Burton, H., Shokrabadi, M. (2020). "A Database of Seismic Designs, Nonlinear Models, and Seismic Responses for Steel Moment Resisting Frame Buildings." DesignSafe-CI, DOI: 10.17603/ds2-8yc7-1285.

**Suggested Citation:**
Guan, X., Burton, H., Shokrabadi, M. (2020). Database of Seismic Designs, Nonlinear Models, and Seismic Responses for Steel Moment Resisting Frame Buildings. DesignSafe-CI.

**Notes:** Converted from original Tcl files (Building 1002). Original unit system: kips, inches, seconds — all values converted to N, mm, MPa. IMKBilin material replaced with Steel01 due to 2D zeroLength element compatibility issue. Panel zone replaced with equalDOF rigid joints for numerical robustness. Eigenvalue analysis shows spurious stiff modes from Transformation constraint handler — run eigenvalue before gravity with Plain constraints for accurate structural periods. Reference Tcl files preserved in ref/ directory organized by analysis type. Run with: `conda activate opensy && python model_pushover.py` (or `model_dynamic.py` / `model_eigen.py`).
