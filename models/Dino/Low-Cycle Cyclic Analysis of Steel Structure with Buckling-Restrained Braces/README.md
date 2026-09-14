# Dino_Steel_BRB

**Purpose:** Low-cycle cyclic lateral displacement analysis of a 3D steel structure with buckling-restrained braces.

**Building System:** 3D multi-story steel frame structure. Steel columns and beams. Buckling-restrained braces (BRBs) are modeled to provide energy dissipation under cyclic lateral loading.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6) containing 80 nodes and 120 elements. Columns and beams modeled as dispBeamColumn elements with Lobatto integration (3 IP). The cross-sections are steel sections (Fiber 1, 2, 3) wrapped in section Aggregators. Gravity is dead load (120 distributed beam loads). Lateral cyclic displacement protocol has 4 segments (total 200 steps) up to +/-400 mm displacement at node 25.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (Steel01 fy=295 MPa, Elastic E=1.999e5 MPa) |
| Lateral System | Steel moment-resisting frame with buckling-restrained braces |
| Lateral Loading | Cyclic displacement-controlled protocol (peaks +/-200 mm, +/-400 mm, 200 steps) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (opensy conda env, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

**References:**
Original source: models/Dino/Low-Cycle Cyclic Analysis of Steel Structure with Buckling-Restrained Braces/tcl_ref/co.tcl. Reference results: tcl_ref/node25.out (200-step cyclic recorder).

**Suggested Citation:**
NA

**Notes:** Converted from co.tcl. Verbatim node coordinates and masses. Steel01 material properties. Integration schemes updated from Tcl 6-arg format to standard OpenSeesPy beamIntegration + dispBeamColumn (using 3 IP Lobatto). 3D fiber sections updated with computed -GJ torsional constants. Gravity is manual LoadControl static loop (10 steps) -> loadConst. Lateral cyclic analysis performed using SmartAnalyze static solver in 4 segments corresponding to the reference DisplacementControl increments. Node 25 UX displacement history matches reference to <=0.00007 mm RMS (0.0000% mean relative error). Visualisation HTMLs generated.
