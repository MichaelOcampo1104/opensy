# XMU_Chapter4_4

**Purpose:** Textbook-example dynamic time-history analysis of a 3-story 1-bay 3D RC frame with fiber-section columns (Concrete01 confined core + unconfined cover, Steel01 rebar, Aggregator torsion), elastic beams, rigid diaphragms, and bi-directional Tabas earthquake (FN + FP).

**Building System:** 3-story 1-bay 3D RC frame (6.096m × 6.096m bay, 3.6576m story height). Columns are 457.2×457.2 mm RC with 377.2×377.2 mm confined core, 40 mm cover, and 3 bars per side (Φ25.5, area=510 mm²). Beams are elastic (E≈24.86 GPa, A=0.279 m², Iz=4.32e-3 m⁴, Iy=2.43e-3 m⁴). Rigid diaphragms at each floor constrain slave Rz to master node.

**Model Description:** 3D finite element model (ndm=3, ndf=6) with 19 nodes and 24 dispBeamColumn elements (12 columns, 12 beams). Fixed column bases. Lumped masses at floor master nodes (30 tonnes each, X+Y translation + Rz rotation). Column sections: fiber-discretised RC with Concrete01 (core + cover) and Steel01 rebar, aggregated with elastic torsion material (GJ). Beam sections: elastic 3D (E, A, Iz, Iy, G=GJ, J=1.0). Gravity loads (74 kN per column node downward) applied via static analysis then frozen with loadConst. Tabas earthquake (dt=0.02s, 50s) via UniformExcitation in X (FN) and Y (FP). Rayleigh damping 2% on mode 1 (stiffness-proportional only). Dynamic analysis with SmartAnalyze Transient + Newmark integration (γ=0.55, β=0.275625). ODB response collection via opst.post.CreateODB.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC (fiber columns + Aggregator torsion) + Elastic beams |
| Lateral System | 3D moment frame (4 columns × 3 stories) |
| Lateral Loading | Dynamic earthquake (time-history, bi-directional) |
| Earthquake Records | Tabas 1978 Iran — FN + FP (dt=0.02s, 2500 pts, 50s) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
XMU Finite Element Analysis course, Chapter 4.4.

**Suggested Citation:**
NA

**Notes:**
Converted from model.tcl + RCsection.tcl (XMU Chapter 4.4 example). Original units: kN, m, kPa — converted to N, mm, MPa. Fiber-section RC columns with Concrete01 (core + cover) and Steel01 rebar, aggregated with elastic torsion material. Beams use G=GJ, J=1.0 elastic section trick from source. dispBeamColumn elements preserved from source (not nonlinearBeamColumn). Ground motion defined AFTER gravity per AGENT.md §12i. Run with: conda activate opensy && python model.py
