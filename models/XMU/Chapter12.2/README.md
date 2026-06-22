# XMU_Chapter12_2

**Purpose:** Textbook-example 2D peridynamic bond-based fracture simulation under transient base excitation with explicit CentralDifference integration.

**Building System:** 40x40 grid of peridynamic bonds (truss elements) with elastic material (E=200 GPa). A pre-existing crack is seeded by omitting bonds between two columns near mid-span.

**Model Description:** 2D peridynamic model (ndm=2, ndf=2) with 1600 nodes and ~8000 truss bond elements connecting nodes within a horizon distance of 1.5 m (1500 mm). Left edge fixed, right edge excited by Ricker wavelet displacement pulse via MultipleSupport pattern. Rayleigh stiffness-proportional damping (2% on mode 1). Explicit CentralDifference integration with bond-breaking damage model (bonds removed when stretched beyond horizon distance). Recorders used for nodal displacement output (4000 steps x 1600 nodes impractical for ODB collection).

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Elastic (steel, E=200 GPa) |
| Lateral System | Peridynamic bonds (truss elements) |
| Lateral Loading | Transient (MultipleSupport base excitation) |
| Earthquake Records | Ricker wavelet displacement pulse (dt=1e-5, 2000 pts, peak 1 mm) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
XMU Finite Element Analysis course, Chapter 12.2.

**Suggested Citation:**
NA

**Notes:** Converted from main.tcl + nodebuild.tcl + elementbuild.tcl + remove.tcl (XMU Chapter 12.2 example). Original units: N, m, kg, Pa — converted to N, mm, MPa. Key differences from canonical layout: (1) CentralDifference explicit dynamics incompatible with SmartAnalyze — manual ops.analyze() loop required. (2) ODB not practical for 1600-node x 4000-step output — recorders used instead (documented exception). (3) Bond-breaking element removal used during analysis. (4) Ground motion time series was missing (timeSeries.tcl absent) — replaced with synthetic Ricker wavelet placeholder (gm_disp.txt). Run with: conda activate opensy && python model.py
