# bradley2021

**Purpose:** Cyclic tension force-deformation analysis of 19 bolted-bolted steel angles using a zeroLengthSection fiber model with experimentally calibrated SteelMPF materials.

**Building System:** Single bolted-bolted steel angle connection — the vertical leg is assumed connected to a rigid member, and tension is applied to the outstanding leg. Tested angle sizes range from L4×4×5/16 to L8×6×3/4.

**Model Description:** 2D zeroLengthSection model with two coincident nodes. A single fiber at the origin captures the axial force-deformation behavior using a Parallel composite material that combines a soft elastic (numerical stability), ENT (bolt bearing), and a MinMax→Fatigue→SteelMPF chain calibrated from Beland et al. (2019) experiments. 19 test cases (TC1–TC19) each represent a different angle size. Cyclic loading follows FEMA 350 protocol (half cycles) with displacement-controlled analysis using SmartAnalyze.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Steel |
| Lateral System | NA (component-level test) |
| Lateral Loading | Cyclic displacement-controlled (FEMA 350 half cycles) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
Beland, T., Bradley, C., Tremblay, R., Rogers, C.A. (2019). Experimental calibration of bolted angle connection behavior for seismic applications.

**Suggested Citation:**
NA

**Notes:** Converted from original Tcl model (A-MainScript.tcl and associated procedures). Original imperial units (ksi, inches, kips) converted to N-mm-MPa. The model runs 19 test cases sequentially; use --tc N to run a single case. Reference Tcl files preserved in ref/ directory.
