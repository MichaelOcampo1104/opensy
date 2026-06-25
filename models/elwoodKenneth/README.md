# elwoodKenneth

**Purpose:** Cyclic displacement-controlled pushover of a single RC column with fiber-section forceBeamColumn elements, graded confinement layers, and Aggregator shear spring (Vy).

**Building System:** Single RC column (wall-like section, 1454 mm wide × 200 mm deep, 3300 mm tall) with concentrated longitudinal reinforcement and confined core concrete. Column designed for shear-critical behavior — part of Ken Elwood's RC column test database.

**Model Description:** 2D finite element model (ndm=2, ndf=3) with 2 forceBeamColumn elements (10 Lobatto integration points each) using fiber-discretised RC sections with Aggregator shear spring (Vy). Four concrete groups (36 Concrete02 materials) and two steel groups (18 Steel02 materials + 18 MinMax wrappers) capture graded confinement from column ends to mid-height. Gravity axial load (1452 kN) followed by 16-cycle displacement-controlled pushover (peak amplitudes from ±3 mm to ±104 mm).

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

**Suggested Citation:**
NA

**Notes:**
Converted from Tcl reference files (modelMaterial9.tcl + modelGeometry9.tcl + wallDriver.tcl) in tcl_refs/staticFiles/. Original units: ksi, in, kip — all converted to N, mm, MPa.

Key conversion notes:
1. **Per-IP sections**: Source Tcl uses `forceBeamColumn -sections` for per-IP graded confinement (10 IPs with 9 Aggregator section variants). OpenSeesPy's beamIntegration supports only one section per element. A single representative section (SEC_AGG_5, mid-height medium confinement) is used for all IPs — ~10-15% stiffness difference expected per AGENT.md §12e.
2. **Aggregator Vy**: Shear spring (Steel01) in Aggregator uses force-deformation interpretation. The Aggregator maps material stress→section force and strain→section deformation. Conversion: fy ×4448.22 (kip→N), E ×(4448.22/25.4) (ksi→N/mm).
3. **Gravity**: Manual LoadControl loop per AGENT.md §3c exception (SmartAnalyze StaticAnalyze forces DisplacementControl).
4. **Pushover**: 16-cycle symmetric protocol (+peak → -peak → 0) using SmartAnalyze per segment with KrylovNewton→Newton→ModifiedNewton→NewtonLineSearch→BFGS algorithm fallback.
5. **No ground motions**: Static pushover only (ground_motions/ dir empty kept for consistency).
6. Reference Tcl files preserved in tcl_refs/ subdirectory.
