# Homorzabad2021_K291

**Purpose:** Nonlinear dynamic time-history analysis of a 6-story 5-bay steel concentrically-braced frame with rocking, PT strands, and fuse assemblies for seismic collapse assessment.

**Building System:** 6-story, 5-bay by 5-bay steel concentrically-braced frame with rocking connections consisting of pinned column bases, PT (post-tensioning) strands, and replaceable fuse assemblies. The rocking mechanism allows controlled uplift under seismic loading, with self-centering capability provided by PT strands and energy dissipation through steel fuse elements.

**Model Description:** 3D finite element model using elasticBeamColumn elements for beams, columns, and braces with 12 section definitions. Rocking connections modeled with ENT base springs and twoNodeLink elements. PT strands as truss elements with ElasticPP material. Fuse assemblies use SelfCentering (gap) and Steel01 uniaxial materials in zeroLength elements. Rayleigh damping applied to modes 1 and 3. Gravity via SmartAnalyze (load-controlled static); dynamic via SmartAnalyze (transient, Newmark integration) with UniformExcitation ground motion input. ODB response collection via opst.post.CreateODB.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel |
| Lateral System | Concentrically-Braced Frame (CBF) with rocking, PT strands, and fuses |
| Lateral Loading | Dynamic earthquake (time-history) |
| Earthquake Records | Kobe (kobe.txt), dt=0.02s, 2500 points |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
Homorzabad, S. (2021). CRSBF-NDAP.py — optimization framework for concentrically-braced frames with rocking.

**Suggested Citation:**
NA

**Notes:** Converted from original CRSBF-NDAP.py script by S. Homorzabad. All units converted to N-mm-MPa. Ground motion file stored in ground_motions/ subfolder.
