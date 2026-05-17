# ST31_L1

**Purpose:** 2D soil-structure interaction analysis of a cut-and-cover underground box-with_leg-frame structure with diaphragm walls and base/top slabs on Winkler spring supports.

**Building System:** Underground Box-with_leg-frame cut-and-cover structure with reinforced concrete diaphragm walls, a top slab, and a base slab, supported on compression-only Winkler springs representing surrounding soil.

**Model Description:** 2D finite element model using dispBeamColumn elements for diaphragm walls (32 elements each), top slab (9 elements), and base slab (9 elements), with ENT (Elastic No Tension) uniaxial materials for horizontal and vertical Winkler springs across 5 soil layers. Two load cases: uniform earth pressure (15 kPa) and hydrostatic water pressure (triangular distribution). Static analysis with gravity freeze then lateral load application using opst.anlys.SmartAnalyze.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | RC |
| Lateral System | Underground cut-and-cover frame |
| Lateral Loading | Static (earth pressure + hydrostatic water pressure) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
NA

**Suggested Citation:**
NA

**Notes:** ST31 (L1) underground box-with_leg-frame model with two selectable lateral load cases: case 1 = uniform earth pressure (15 kPa), case 2 = hydrostatic water pressure (triangular). Model uses --case argument to switch.