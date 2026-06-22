# XMU_Chapter12_3

**Purpose:** 3D peridynamic bond-based concrete damage simulation under static DisplacementControl pushdown.

**Building System:** 150×300×150 mm concrete block discretised as 11×21×11 peridynamic particles (2541 nodes) connected by ~60K truss bonds with Concrete02 material. Top surface loaded vertically with -2.0e6 N per node; base fully fixed.

**Model Description:** 3D peridynamic model (ndm=3, ndf=3) with grid-based node generation and bond search within a horizon of 30.225 mm (3-cell search radius). Bonds in the inner zone (dist ≤ horizon - radij) receive full Concrete02 strength; bonds in the transition zone (horizon - radij < dist < horizon + radij) receive linearly scaled strength. Static analysis with DisplacementControl integrator (400 steps, -0.005 mm/step at centre top node). ODB used for nodal response collection via fetch_response_step after each step. Recorders used for targeted base reaction and control-node displacement output.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Concrete02 (per-bond unique material) |
| Lateral System | Peridynamic bonds (truss elements) |
| Lateral Loading | Static (DisplacementControl pushdown) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
XMU Finite Element Analysis course, Chapter 12.3.

**Suggested Citation:**
NA

**Notes:** Converted from model.tcl + elements.tcl (XMU Chapter 12.3 example). Original units: N, m, Pa — converted to N, mm, MPa. Key differences: (1) Each truss bond gets its own Concrete02 material (tag = bond number); (2) Transition-zone bonds have scaled strength via `fac = (horizon + radij - dist) / (2 * radij)`; (3) Manual `ops.analyze(1)` loop with `fetch_response_step` — 400 steps makes ODB collection feasible; (4) Truss response saving disabled in ODB to keep file size manageable (~60K truss elements). Run with: conda activate opensy && python model.py
