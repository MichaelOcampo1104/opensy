# Dino_SRC_Column_3D_Pushover

**Purpose:** Static elastic-plastic pushover analysis of a 3D steel reinforced concrete (SRC) column under constant axial compression and lateral displacement loading.

**Building System:** Steel reinforced concrete (SRC) composite column (800x800 mm square cross section) with fiber discretization.

**Model Description:** 3D finite element model (ndm=3, ndf=6) of a 3.0 m tall SRC cantilever column using a single nonlinearBeamColumn element. Section: 800x800 mm composite fiber section (Concrete01 for core/cover, Steel01 for rebars and steel shape). Gravity analysis under 10000 kN axial force (LoadControl gravity static analysis) -> displacement-controlled pushover up to 40 mm displacement (DisplacementControl via opst.anlys.SmartAnalyze).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | SRC |
| Lateral System | Column |
| Lateral Loading | Displacement-controlled lateral pushover (to 40 mm, 100 steps) |
| Earthquake Records | NA |
| Design Year | 2018 |
| File Format | .py |
| OpenSees Version | OpenSeesPy >= 3.0 |
| Units | N, mm, MPa |

**References:**
Dino Chen's Blog Example 27: [http://dinochen.com/article.asp?id=267](http://dinochen.com/article.asp?id=267).

**Suggested Citation:**
Chen, X. W. (2018). Static elasto-plastic analysis of steel reinforced concrete column. Dino Chen's Blog, http://dinochen.com/article.asp?id=267.

**Notes:**
Converted from original Tcl reference script `co.tcl`. Units are in N, mm, MPa. Gravity analysis uses manual LoadControl loop per AGENT.md §3c exception, followed by displacement-controlled pushover managed by opst.anlys.SmartAnalyze. Visualisations rendered via opstool >= 1.0 (vis_utils).
