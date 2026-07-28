# Dino_RC_Column_3D_Pushover

**Purpose:** Static elastic-plastic pushover analysis of a 3D reinforced concrete column section subject to axial gravity load and lateral displacement control.

**Building System:** 3D Cantilever Reinforced Concrete Column (500x500 mm square cross section) with fiber discretization.

**Model Description:** 3D finite element model (ndm=3, ndf=6) of a 3.0 m tall RC cantilever column discretized into 8 nonlinearBeamColumn elements with 3 Gauss-Lobatto integration points each. The 500x500 mm section uses 64 concrete fibers (Concrete01, f'c=26.8 MPa, epsc0=0.002, f'cu=15 MPa, epscu=0.006) and 16 steel rebar fibers (Steel01, fy=335 MPa, Es=200 GPa). Gravity load of 1.5 MN (1500 kN) is applied incrementally via LoadControl gravity static analysis, followed by lateral displacement control pushover up to 100 mm displacement at the top control node.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC |
| Lateral System | Cantilever Column |
| Lateral Loading | Static pushover (DisplacementControl to 100 mm) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | OpenSeesPy >= 3.0 |
| Units | N, mm, MPa |

**References:**
Static Elastic-Plastic Analysis of Frame Structures (Dino TCL Ref opensees3 reference examples).

**Suggested Citation:**
NA

**Notes:**
Converted from original Tcl reference scripts (`co.tcl` single-element and `co2.tcl` 8-element discretization). Units converted to N, mm, MPa. Gravity analysis uses manual LoadControl loop per AGENT.md §3c exception, followed by displacement-controlled pushover managed by opst.anlys.SmartAnalyze. Visualisations rendered via opstool >= 1.0 (vis_utils).
