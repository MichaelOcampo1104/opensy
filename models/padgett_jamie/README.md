# padgett_jamie

**Purpose:** Nonlinear 3D seismic response of a simply-supported multi-span RC box girder bridge on elastomeric bearings with soil-pile abutment/foundation springs, deck pounding, and Rayleigh-damped transient analysis.

**Building System:** Multi-span simply supported (MSSS) concrete box girder highway bridge typical of Central/Southeastern US (non-seismic design). Superstructure: 3-span RC box girder deck with 4 girders. Substructure: 2-column RC circular pier bents, with CIDH pile foundations. Abutments: seat-type with elastomeric bearing pads and steel dowels. Deck pounding at expansion joints.

**Model Description:** Full 3D grillage model with fiber-section columns (Concrete04 + Steel02), elastic deck girders and transverse slab, elastomeric bearing pads (Steel01 with gap/dowel parallel/series assemblies), bilinear abutment soil springs (Hysteretic + ElasticPPGap), pile-group foundation springs (ElasticPPGap translational + Elastic rotational), and Hertz-contact impact elements (ElasticPPGap pairs) for deck pounding. Rayleigh damping (5% in first 2 modes). TRBDF2 transient integrator.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC (Concrete04 + Steel02 fiber sections for columns; elastic for deck) |
| Lateral System | Frame (RC pier bents) |
| Lateral Loading | Dynamic (UniformExcitation, X-longitudinal + Z-transverse) |
| Earthquake Records | Synthetic Ricker wavelet (dt=0.01s, 2000 pts) or user-supplied ground motion files |
| Design Year | Typical of non-seismic design era (1950s–1980s Central/Southeastern US) |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy |
| Units | N, mm, MPa |

**References:**
Nielson, B.G. (2005). Analytical fragility curves for highway bridges in moderate seismic zones, PhD thesis, Georgia Tech.
Padgett, J.E. (2007). Seismic vulnerability assessment of retrofitted bridges, PhD thesis, Rice University.

**Suggested Citation:**
Nielson (2005) - original Tcl parametric generator. Padgett (2007) - fragility extension. Converted to OpenSeesPy 2026-06-29.

**Notes:** Converted from Tcl parametric builder in tcl_ref/ (1152 fragility bridges). Single representative bridge with median parameters from row i=1129. Fiber column sections use dispBeamColumn + Lobatto (6 IP). All imperial values (in/kip/ksi) converted to N-mm-MPa per AGENT.md §3a. Gravity via load-controlled manual loop; transient via SmartAnalyze TRBDF2.
