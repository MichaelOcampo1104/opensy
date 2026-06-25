# elwoodkenneth_C10

**Purpose:** Cyclic displacement-controlled pushover of a single RC column (C10 specimen) with fiber-section forceBeamColumn elements, graded confinement layers, and Aggregator shear spring (Vy).

**Building System:** Single RC column (wall-like section, 1454 mm wide × 200 mm deep, 3260 mm tall) with concentrated longitudinal reinforcement and confined core concrete. C10 specimen from Ken Elwood's RC column test database — shear-critical response.

**Model Description:** 2D finite element model (ndm=2, ndf=3) with 2 forceBeamColumn elements (10 Lobatto integration points each) using fiber-discretised RC sections with Aggregator shear spring (Vy). 36 Concrete02 materials (4 concrete groups) and 18 Steel02 + 18 MinMax wrappers capture graded confinement from column ends to mid-height. C10 variant has fc=-4.743 MPa for variant-2 concrete (constant epsU=-0.008) and slightly different confinement strains from the base elwoodKenneth model. Gravity axial load (1452 kN) followed by 15-cycle displacement-controlled pushover (peak amplitudes from ±3 mm to ±103 mm).

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | RC (fiber-section forceBeamColumn) |
| Lateral System | Cantilever column |
| Lateral Loading | Static cyclic displacement-controlled pushover |
| Earthquake Records | NA |
| Design Year | NA (laboratory test specimen) |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy |
| Units | N, mm, MPa |

**References:**
Elwood, K. J. — UBC / UC Berkeley RC column test database.

**Notes:**
Converted from Tcl reference files (modelMaterial9.tcl + modelGeometry9.tcl + wallDriver.tcl) in tcl_ref/. C10 variant differs from elwoodKenneth in column height (3260 mm vs 3300 mm), concrete confinement parameters (group 101-109 uses fc=-4.743 MPa with constant epsU=-0.008), and cyclic protocol (15 cycles vs 16). Per-IP graded confinement uses a single representative section (SEC_AGG_5) due to OpenSeesPy beamIntegration limitation (AGENT.md §12e). Lateral pattern defined after loadConst per §12z-1. Manual solver loop per §12z-3.
