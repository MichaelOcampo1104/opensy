# XMU_Chapter4_3

**Purpose:** Textbook-example dynamic time-history analysis of a single-story single-bay RC portal frame with fiber-section columns (Concrete01 cover + confined core, Steel01 rebar) and elastic beam under Tabas earthquake (Rayleigh damping 2% on mode 1).

**Building System:** Single-story single-bay RC portal frame (6.0m wide × 3.0m tall). Columns are 500×500 mm RC with 440×440 mm confined core, 30 mm cover, and 6×Φ25 longitudinal rebar (3 top + 3 bottom). Beam is elastic (E=30 GPa, A=0.15 m², I=4.5e-3 m⁴).

**Model Description:** 2D finite element model (ndm=2, ndf=3) with 4 nodes and 3 dispBeamColumn elements (5 integration points each). Fixed column bases with lumped masses at top nodes (20 tonnes each, X-direction only). Column sections: fiber-discretised RC with Concrete01 (cover + confined core) and Steel01 rebar. Beam: elastic section. Uniform downward load on beam (-65.33 N/mm) applied via static analysis then frozen with loadConst. Tabas earthquake (dt=0.02s, 20s) via UniformExcitation in X. Rayleigh damping 2% on mode 1 (stiffness-proportional only). Dynamic analysis with SmartAnalyze Transient + Newmark integration. ODB response collection via opst.post.CreateODB.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | RC (fiber columns) + Elastic beam |
| Lateral System | Portal frame (moment-resisting) |
| Lateral Loading | Dynamic earthquake (time-history) |
| Earthquake Records | Tabas 1978 Iran (dt=0.02s, first 1000 pts) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
XMU Finite Element Analysis course, Chapter 4.3.

**Suggested Citation:**
NA

**Notes:**
Converted from model.tcl (XMU Chapter 4.3 example). Original units: kN, m, kPa — converted to N, mm, MPa. Fiber-section RC columns with Concrete01 (cover + confined core) and Steel01 rebar. dispBeamColumn elements preserved from source (not nonlinearBeamColumn). Ground motion defined AFTER gravity per AGENT.md §12i. Run with: conda activate opensy && python model.py
