# XMU_Chapter4_2

**Purpose:** Textbook-example dynamic time-history analysis of a single-story single-bay portal frame with Steel01 bilinear columns and elastic beam under Tabas earthquake (Rayleigh damping 2% on mode 1).

**Building System:** Single-story single-bay portal frame (12.80m wide × 10.97m tall). Columns use an Aggregator section: Steel01 (Fy=14.7 MPa, E=5.74 GPa) for flexure and Elastic (E=46.2 GPa) for axial response. Beam uses an elastic section (E=24.9 GPa, A=3.72 m², I=1.8413 m⁴).

**Model Description:** 2D finite element model (ndm=2, ndf=3) with 4 nodes and 3 nonlinearBeamColumn elements (5 integration points each). Fixed column bases with lumped masses at top nodes (80 tonnes each, X-direction only). Uniform downward load on beam (-122.5 N/mm) applied via static analysis then frozen with loadConst. Tabas earthquake (dt=0.02s, 20s) via UniformExcitation in X. Rayleigh damping 2% on mode 1 (stiffness-proportional only). Dynamic analysis with SmartAnalyze Transient + Newmark integration. ODB response collection via opst.post.CreateODB.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Steel (bilinear columns) + Elastic beam |
| Lateral System | Portal frame (moment-resisting) |
| Lateral Loading | Dynamic earthquake (time-history) |
| Earthquake Records | Tabas 1978 Iran (dt=0.02s, first 1000 pts) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
XMU Finite Element Analysis course, Chapter 4.2.

**Suggested Citation:**
NA

**Notes:**
Converted from model.tcl (XMU Chapter 4.2 example). Original units: kN, m, kPa — converted to N, mm, MPa. kN→N (×1000), m→mm (×1000), kPa→MPa (÷1000), mass same numerical value (kN·s²/m ≡ N·s²/mm). Ground motion defined AFTER gravity per AGENT.md §12i. Run with: conda activate opensy && python model.py
