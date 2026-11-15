# Dino_Beam_Exam03_Pushdown

**Purpose:** Vertical uniform load of 10 N/mm on a 3 m simply supported beam with a 300x600 mm fiber section, pushed down at midspan (node 5, UZ) by 0.1 mm per step for 100 steps (10 mm).

**Building System:** Simply supported 3 m RC beam, 300x600 mm: 36 concrete fibers (5000 mm^2 each, Concrete01) and 5 longitudinal bars (390 mm^2 on top, 490 mm^2 at the bottom, Steel01). Pinned at x = 0 and a roller at x = 3000 mm.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6) with 7 nodes and six nonlinearBeamColumn elements (3 integration points, one fiber section, Linear transforms with local z along global Z), verbatim from `ref/Exam03.tcl`. The load is a uniform -10 N/mm in local z on every element (eleLoad beamUniform). Midspan displacement control on node 5 (UZ) via opst.anlys.SmartAnalyze, with plain Newton first and EnergyIncr 1e-6 tests.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC (Concrete01 + Steel01) |
| Lateral System | NA (beam) |
| Lateral Loading | Vertical uniform load, midspan pushdown to 10 mm (100 steps) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | OpenSeesPy >= 3.0 |
| Units | N, mm, MPa |

**References:**
Dino Chen's OpenSees tutorial, Example 03 (Elastic-Plastic Analysis of a Simply Supported Beam): [http://www.dinochen.com/article.asp?id=152](http://www.dinochen.com/article.asp?id=152). Source: `ref/Exam03.tcl`.

**Suggested Citation:**
Chen, X. W. Dino Chen's OpenSees tutorial, Example 03. http://www.dinochen.com/article.asp?id=152.

**Verification:**
No usable reference output exists for this source. `ref/node0.out` records zeros only (all 600 displacement entries), and the source's node5.out and element outputs are not present. Verification is therefore analytic:
- Elastic check: the first three steps match cracked-section beam theory (Concrete01 without tension, initial tangents, EI = 6.05e13 N mm^2, deflection per unit load factor 0.1744 mm) to within 0.13% (ratio 0.9996 at step 1).
- The full pushdown has no reference. It reaches 10 mm at a load factor of 22.80 (UDL 228 N/mm), where the sections are in the inelastic range.

**Notes:** Converted from `ref/Exam03.tcl`. The 7 nodes, 6 elements, 41 fibers, restraints, and uniform load match the source. `Exam03.tcl` assigns no torsional stiffness, so `-GJ` is 1e8 N mm (the AGENT.md default); the torsion DOFs are fixed at the supports, so the response is unaffected. The source's DisplacementControl (node 5, DOF 3, -0.1 mm) is replayed as a 100-step pushdown to -10 mm.

**Reference files:** `ref/Exam03.tcl`, `ref/node0.out` (zeros only, kept for completeness).
