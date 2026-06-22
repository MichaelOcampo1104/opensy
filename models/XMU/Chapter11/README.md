# XMU_Chapter11

**Purpose:** Textbook-example sensitivity analysis of a 2D truss under static lateral load followed by El Centro ground motion using DDM.

**Building System:** 2D three-bar truss with pinned supports at node 1 and roller supports at nodes 2 and 3. Steel truss bars with bilinear Steel01 material (Fy=248.2 MPa, E=200 GPa).

**Model Description:** 2D finite element model (ndm=2, ndf=2) with 3 nodes and 2 Truss elements. Static load (20 kN at node 3) followed by UniformExcitation ground motion (el.txt, factor=300, dt=0.01s). DDM sensitivity computed for material stiffness parameter (E) on both elements. Manual LoadControl loop (no SmartAnalyze — sensitivity incompatible). ODB response collection via opst.post.CreateODB.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Steel (bilinear Steel01) |
| Lateral System | Truss (pinned supports) |
| Lateral Loading | Static + Dynamic earthquake (time-history) |
| Earthquake Records | El Centro 1940 NS component (el.txt, dt=0.01s, 3218 pts, factor=300, first 100 pts used) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
XMU Finite Element Analysis course, Chapter 11.

**Suggested Citation:**
NA

**Notes:** Converted from model.tcl (XMU Chapter 11 example). Original units: m, N, kPa — converted to N, mm, MPa. Sensitivity analysis uses ops.parameter() + ops.addToParameter() + ops.sensitivityAlgorithm(). Manual analysis loops required (SmartAnalyze does not support sensitivity — documented exception per AGENT.md §3c/§10). Sensitivity recorder kept as exception (opstool CreateODB does not support sensitivity collection). Ground motion file (el.txt) in ground_motions/. Run with: conda activate opensy && python model.py
