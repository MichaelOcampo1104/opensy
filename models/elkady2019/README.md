# elkady2019

**Purpose:** Nonlinear dynamic (EQ) and pushover (PO) analysis of a 4-story 3-bay steel special moment frame (SMF) with panel zones, IMK springs, and an elastic gravity frame, used to study seismic collapse capacity of steel MRFs.

**Building System:** 4-story, 3-bay steel special moment-resisting frame (SMF) per AISC 341 seismic provisions. The lateral system comprises W14 wide-flange columns and W21 wide-flange beams with Reduced Beam Section (RBS) connections. An elastic gravity frame (EGF) modelled as a leaning column captures P-Δ effects from tributary gravity loads. Column splices are located at mid-height of every other story.

**Model Description:** 2D finite element model with 16 panel zones modelled as rectangular parallelograms (ConstructPanel_Rectangle). Panel zone nonlinearity is captured via Skiadopoulos–Elkady–Lignos Hysteretic springs (Spring_PZ). Beam-to-column and column-to-panel-zone connections use IMKBilin rotational springs (Spring_IMK) calibrated with Lignos–Krawinkler (2011) and Lignos et al. (2019) regression equations. Column elements use ModElasticBeam2d with stiffness-modifier n=10. Gravity analysis uses opst.anlys.SmartAnalyze (static, load-controlled); dynamic analysis uses DynamicAnalysisCollapseSolverX with Newmark integration and SmartAnalyze convergence management. ODB-based response collection via opst.post.CreateODB.

| Field               | Value                                                              |
|---------------------|--------------------------------------------------------------------|
| Dimensions          | 2D                                                                 |
| Material            | Steel                                                              |
| Lateral System      | Special Moment-Resisting Frame (SMF) with RBS connections          |
| Lateral Loading     | Dynamic (earthquake) + static pushover                             |
| Earthquake Records  | 1994 Northridge – Canoga Park (NR94cnp.txt), dt=0.01s, 2495 pts   |
| Design Year         | NA (research model calibrated to AISC 341 SMF)                    |
| File Format         | .py                                                                |
| OpenSees Version    | NA                                                                 |
| Units               | N, mm, MPa                                                         |

## File Structure

```
elkady2019/
├── SMF4B.py                    ← main model script (this file)
├── README.md                   ← this file
├── constructpanel_rectangle.py ← panel zone geometry helper
├── dynamicanalysiscollapsesolverx.py ← transient collapse solver
├── lognrmrand.py               ← log-normal random variable generator
├── sdrlimittester.py           ← story-drift collapse check
├── spring_imk.py               ← IMK beam/column spring helper
├── spring_panel.py             ← panel spring helper
├── spring_pinching.py          ← pinching spring helper
├── spring_pz.py                ← panel zone spring helper
├── spring_rigid.py             ← rigid spring helper
├── spring_zero.py              ← zero-stiffness spring helper
├── ground_motions/
│   └── NR94cnp.txt             ← 1994 Northridge Canoga Park record
├── output/                     ← ODB + HTML visualisations (git-ignored)
└── tcl_ref/                    ← original Tcl reference files
    └── SMF4B.tcl
```

## Running the Model

```bash
# Dynamic earthquake analysis (default: RUN_EQ=1, RUN_PO=0)
python SMF4B.py

# Headless mode (suppresses HTML visualisation output)
OPENSEES_HEADLESS=1 python SMF4B.py
```

To run pushover instead, set `RUN_PO = 1` and `RUN_EQ = 0` at the top of [SMF4B.py](SMF4B.py).

## References

**References:**
- Elkady, A. and Lignos, D.G. (2014). Modeling of the Composite Action in Fully Restrained Beam-to-Column Connections: Implications in the Seismic Design and Collapse Capacity of Steel Special Moment Frames. *Earthquake Engineering & Structural Dynamics* 43(13).
- Lignos, D.G. and Krawinkler, H. (2011). Deterioration Modeling of Steel Components in Support of Collapse Prediction of Steel Moment Frames under Earthquake Loading. *Journal of Structural Engineering* 137(11).
- Lignos, D.G. et al. (2019). Proposed Updates to the ASCE 41 Nonlinear Modeling Parameters for Wide-Flange Steel Columns in Support of Performance-based Seismic Engineering. *Journal of Structural Engineering* 145(9).
- Skiadopoulos, A., Elkady, A. and Lignos, D.G. (2020). Proposed Panel Zone Model for Seismic Design of Steel Moment-Resisting Frames. *ASCE Journal of Structural Engineering*.

**Suggested Citation:**
Elkady, A. and Lignos, D.G. (2014). Modeling of the Composite Action in Fully Restrained Beam-to-Column Connections. *Earthquake Engineering & Structural Dynamics* 43(13).

**Notes:** Converted from original Tcl script (SMF4B.tcl) by Dr. Ahmed Elkady. All units converted from imperial (ksi, inches, kips) to N–mm–MPa consistent unit system. Rayleigh damping ζ=2% applied to modes 1 and 3.
