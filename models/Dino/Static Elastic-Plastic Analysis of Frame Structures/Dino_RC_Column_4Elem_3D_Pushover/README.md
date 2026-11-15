# Dino_RC_Column_4Elem_3D_Pushover

**Purpose:** Gravity followed by a 100 mm displacement-controlled pushover of a 3D reinforced-concrete column modelled with four `nonlinearBeamColumn` elements and one fiber section.

**Building System:** 3 m tall RC column with a 500x500 mm section: 25 concrete fibers (100x100 mm, Concrete01) and 20 longitudinal bars of 200 mm^2 (Steel01), fixed at the base.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6) with 5 nodes and four nonlinearBeamColumn elements (3 integration points each, one fiber section, Linear transforms), verbatim from `ref/co.tcl`. Gravity: 1500 kN at the top node, LoadControl 0.01 x 100 steps, then loadConst. Pushover: 1 kN reference load at the top node and displacement control on the top node (DOF 1), 1 mm per step for 100 steps, via opst.anlys.SmartAnalyze with plain Newton first and EnergyIncr 1e-6 tests.

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
Dino Chen's OpenSees tutorial, video 03/04: [http://www.dinochen.com/article.asp?id=296](http://www.dinochen.com/article.asp?id=296). Source: `ref/co.tcl`, copied from `tcl_ref/opensees2` in the parent folder.

**Suggested Citation:**
Chen, X. W. Dino Chen's OpenSees tutorial, video 03/04. http://www.dinochen.com/article.asp?id=296.

**Verification:**
Node histories (time, UX, UY, UZ) over the 100 pushover steps, against `ref/node0.out` (nodes 1-5) and `ref/node1.out` (node 1).
- Displacements: node 1 UX is imposed exactly, and its UZ differs by at most 4.8e-6 mm. Nodes 2-5 agree to 5e-5 mm.
- Load factor (kN): mean relative error 0.49% over 100 steps. Nearly all of it is in steps 1-9, where the model is up to 2.6 kN higher (about 13% at step 1). Steps 10-100 average 0.11%, and the peak (step 24) is within 0.04%.
- The early offset does not come from the solver. A plain-Newton replay (EnergyIncr 1e-6, 200 iterations, one `analyze(1)` per step) matches this model to 1.5e-10 kN. A similar early offset (about 15% at step 1) appears in `Dino_SRC_Column_3D_Pushover`, so the offset lies between the reference and the literal replay, not in the solver.

**Notes:** Converted from `ref/co.tcl`. The 45 fibers, nodes, and elements match the source. `co.tcl` assigns no torsional stiffness, so `-GJ` is 1e8 N mm (the AGENT.md default); torsion is fixed at both ends, so the response is unaffected. Elastic material 3 is defined as in the source but used by no fiber. `ref/model1.s2k` is the ETABS text export of the source model.

**Reference files:** `ref/co.tcl`, `ref/node0.out`, `ref/node1.out`, `ref/model1.s2k`.
