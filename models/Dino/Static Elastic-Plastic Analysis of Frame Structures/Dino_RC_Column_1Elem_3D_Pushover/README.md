# Dino_RC_Column_1Elem_3D_Pushover

**Purpose:** Gravity (4500 kN) followed by a 100 mm displacement-controlled pushover of a 3D reinforced-concrete column modelled with one `nonlinearBeamColumn` element and a fiber section.

**Building System:** 3 m tall RC column with a 500x500 mm section: 25 concrete fibers (100x100 mm, Concrete01) and 18 longitudinal bars of 490.6 mm^2 (Steel01), fixed at the base. Lumped masses (0.9375 in UX and UY) are included as in the source; they do not affect the static analysis.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6) with two nodes and one nonlinearBeamColumn element (3 integration points, one fiber section, Linear transform), verbatim from `ref/co.tcl`. Gravity: 4500 kN at the top node, LoadControl 0.01 x 100 steps, then loadConst. Pushover: 1 kN reference load at the top node and displacement control on the top node (DOF 1), 1 mm per step for 100 steps, via opst.anlys.SmartAnalyze with plain Newton first and EnergyIncr 1e-6 tests.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC (Concrete01 + Steel01) |
| Lateral System | Column |
| Lateral Loading | Displacement-controlled pushover (to 100 mm, 100 steps) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | OpenSeesPy >= 3.0 |
| Units | N, mm, MPa |

**References:**
Dino Chen's OpenSees tutorial, video 03/04: [http://www.dinochen.com/article.asp?id=296](http://www.dinochen.com/article.asp?id=296). Source: `ref/co.tcl`, copied from `tcl_ref/opensees` in the parent folder.

**Suggested Citation:**
Chen, X. W. Dino Chen's OpenSees tutorial, video 03/04. http://www.dinochen.com/article.asp?id=296.

**Verification:**
Node-1 history (time, UX, UY, UZ) over the 100 pushover steps, against `ref/node1.out`.
- Displacements: UX is imposed exactly, and UZ differs by at most 5.0e-6 mm.
- Load factor (kN): mean relative error 0.53% over 100 steps. Steps 1-9 account for most of it: the model is up to 2.9 kN higher there (about 7% at step 1). Steps 10-100 average 0.19%, and the peak (step 22) is within 0.05%.
- The early offset is not caused by the solver. A plain-Newton replay (EnergyIncr 1e-6, 200 iterations, one `analyze(1)` per step) matches this model to 1.5e-8 kN. A similar early offset appears in `Dino_RC_Column_4Elem_3D_Pushover` and `Dino_SRC_Column_3D_Pushover`, so it lies between the reference and the literal replay (LESSONS 27).
- `ref/excel.xlsx`, sheet `curve2`: the left block equals `node1.out` exactly. The right block is a different curve that co.tcl does not reproduce (up to 77 kN and 7 mm away from this model at later steps). It is kept for reference only and is not used for validation (LESSONS 18).

**Notes:** Converted from `ref/co.tcl`. The 43 fibers, the nodes, the element, and the lumped masses match the source. `co.tcl` assigns no torsional stiffness, so `-GJ` is 1e8 N mm (the AGENT.md default); torsion is fixed at both ends, so the response is unaffected.

**Reference files:** `ref/co.tcl`, `ref/node1.out`, `ref/excel.xlsx`.
