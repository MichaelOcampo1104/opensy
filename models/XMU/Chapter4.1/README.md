# XMU_Chapter4_1

**Purpose:** Textbook-example dynamic time-history analysis of a 2D elastic cantilever column (2-DOF system) under Tabas earthquake with Rayleigh damping (2% on mode 1).

**Building System:** 2D cantilever column (0.5m × 0.5m square section, 6m total height) with lumped masses at mid-height and top (10,000 kg each). Elastic material with E=30 GPa. Two elasticBeamColumn elements with Linear geometric transformation.

**Model Description:** 2D finite element model (ndm=2, ndf=3) with 3 nodes and 2 elasticBeamColumn elements. Fixed base with lumped masses at nodes 2 and 3. Static vertical preload (100 kN at each floor) applied then frozen with loadConst. Tabas earthquake (dt=0.02s, 20s, factor=g) via UniformExcitation in X-direction. Rayleigh damping 2% on mode 1 (stiffness-proportional only, a0=0). Dynamic analysis uses SmartAnalyze Transient with Newmark integration. ODB response collection via opst.post.CreateODB. EDPs: inter-story drifts, peak top displacement, peak base shear.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Elastic (concrete, E=30 GPa) |
| Lateral System | Cantilever column |
| Lateral Loading | Dynamic earthquake (time-history) |
| Earthquake Records | Tabas 1978 Iran (dt=0.02s, 2501 pts, first 1000 pts used) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
XMU Finite Element Analysis course, Chapter 4.1.

**Suggested Citation:**
NA

**Notes:**
Converted from model.tcl (XMU Chapter 4.1 example). Original units: N, m, kg, Pa (SI) — converted to N, mm, MPa. SI→N-mm conversion: lengths ×1000, mass ÷1000 (kg→tonne), stress /1e6 (Pa→MPa). Ground motion defined AFTER gravity per AGENT.md §12i. Run with: conda activate opensy && python model.py
