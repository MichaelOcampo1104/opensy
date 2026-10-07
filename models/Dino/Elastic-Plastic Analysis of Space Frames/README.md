# DinoSpaceFrame

**Purpose:** 3-direction nonlinear transient of a 179-node / 720-member steel space truss with elastic-plastic trussSection members (TP300x20).

**Building System:** Double-layer steel space grid (top chord at z=3000, bottom chord at z=0), 25.6 m x 32 m footprint, supported on 4 bottom-chord pins. All 720 members are circular pipe TP300x20 (D=300, t=20) with Steel01 elastic-plastic material (fy=250 MPa).

**Model Description:** 3D truss finite element model (ndm=3, ndf=3) with 179 nodes and 720 trussSection fiber elements (20-fiber circular ring per section). Lumped translational masses at all nodes. Rayleigh damping 2% on modes 1–2. Simultaneous 3-direction UniformExcitation (GM1X/Y/Z x5, dt=0.02 s); 2000-step transient at dt=0.01 s (20 s) via opst.anlys.SmartAnalyze with Newmark integration. ODB-based response collection via opst.post.CreateODB (every 4th step, 500 fetches).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel |
| Lateral System | Space truss / grid |
| Lateral Loading | Dynamic earthquake (3-dir time-history) |
| Earthquake Records | GM1X/Y/Z.txt (2048 pts each, dt=0.02 s, factor 5.0) |
| Design Year | 2013 (ETABS EXAM14.EDB saved 4/14/13) |
| File Format | .py |
| OpenSees Version | openseespy 3.8.0.0 / opstool 1.0.26 |
| Units | N, mm, MPa |

**References:**
EXAM14.s2k (SAP2000/ETABS export of EXAM14.EDB); original Tcl driver ref/co.tcl

**Suggested Citation:**
NA

**Notes:** Converted from ref/co.tcl (Tcl, OpenSees) with zero logic change. Known deviations recorded in model.py: W1 Steel01 fy=250 MPa vs s2k Q345/FY=345 (kept 250); W2 analysis covers first ~20 s of 40.96 s GM record (kept verbatim); W3 folder name contains spaces (nested Dino path kept per user choice); W4 Elastic mats 1–3 unused (kept); W5 top chord free, only 4 bottom pins; W7 solver trio RCM/BandGeneral (was Plain/UmfPack); W8 ODB throttled every 4th step. Run with: python model.py (set OPENSEES_HEADLESS=1 in CI).
