# XMU_Chapter2

**Purpose:** Textbook-example dynamic time-history analysis of a 2D elastic three-bar truss under static preload followed by El Centro ground motion.

**Building System:** 2D three-bar elastic truss with pinned base supports. Left diagonal (A=10 in²), middle vertical (A=5 in²), and right diagonal (A=5 in²) truss elements connect to a common apex node. Elastic material with E=3000 ksi.

**Model Description:** 2D finite element model (ndm=2, ndf=2) with 4 nodes and 3 Truss elements. Single elastic material. Static point load (100 kip X, -50 kip Y) applied at apex node then frozen with loadConst. El Centro NS ground motion (factor 3.0, dt=0.01s, 20 s) applied via UniformExcitation in X-direction. Dynamic analysis uses SmartAnalyze Transient with Newmark integration (γ=0.5, β=0.25). ODB response collection via opst.post.CreateODB. EDPs: peak apex displacements and base reactions.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Elastic |
| Lateral System | Truss (pinned supports) |
| Lateral Loading | Dynamic earthquake (time-history) |
| Earthquake Records | El Centro 1940 NS component (dt=0.01 s, factor 3.0) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
XMU Finite Element Analysis course, Chapter 2.

**Suggested Citation:**
NA

**Notes:**
Converted from tcl_ref/model.tcl (XMU Chapter 2 example). All imperial units (kips, inches, ksi) converted to N, mm, MPa. Ground motion file (El Centro NS) stored in ground_motions/. Ground motion defined AFTER gravity per AGENT.md §12i (loadConst freezes all loads including UniformExcitation). Run with: conda activate opensy && python model.py
