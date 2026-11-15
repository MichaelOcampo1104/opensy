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

**Verification:**
Node-2 history (time, UX, UY, UZ over the 100 pushover steps) against `ref/node2.out`, which holds the same data as Sheet1 of the source `result.xlsx`.
- Fibers: all 188 match `ref/co.tcl` (coordinates, areas, material tags).
- Load factor: mean relative error 1.25% over 100 steps. Steps 1-9 account for most of it: there the model is up to 23.5 kN above the reference (about 15% at step 1). Steps 10-100 average 0.33%, the peak (step 36) is within 0.07%, and the final step within 0.03%.
- UZ: maximum error 5e-6 mm. UX is imposed exactly.
- The early-step difference is not explained by the Tcl as written. A Tcl-literal replay (plain Newton, EnergyIncr 1e-6, 200 iterations) and runs with -GJ = 1e12 give the same numbers, so these settings do not cause it.

**References:**
Dino Chen's Blog Example 27: [http://dinochen.com/article.asp?id=267](http://dinochen.com/article.asp?id=267).

**Suggested Citation:**
Chen, X. W. (2018). Static elasto-plastic analysis of steel reinforced concrete column. Dino Chen's Blog, http://dinochen.com/article.asp?id=267.

**Notes:**
Converted from original Tcl reference script `co.tcl`. Units are in N, mm, MPa. Gravity analysis uses manual LoadControl loop per AGENT.md §3c exception, followed by displacement-controlled pushover managed by opst.anlys.SmartAnalyze. Visualisations rendered via opstool >= 1.0 (vis_utils).
