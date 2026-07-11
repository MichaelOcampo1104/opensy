# OPST_mc_section

**Purpose:** Moment-curvature analysis of a 2×2 m hollow RC box section via opstool's `FiberSecMesh` + `MomentCurvature` — the repo's first pure section-level analysis (no structural mesh).

**Building System:** Square hollow RC box section, 2000×2000 mm outer, 50 mm cover, 1000×1000 mm central core hole. Cover concrete fc=32.4 MPa (Concrete04), confined core fc=40.6 MPa (Concrete04, ecu=−0.0144), Steel01 rebar fy=300 MPa, 20 mm dia @ 100 mm around the perimeter. Constant axial compression −20 MN.

**Model Description:** Section-level analysis (no nodes/elements/gravity/pushover/ODB). The fiber section is built with opstool's `opst.pre.section.FiberSecMesh` (polygon patches with holes, triangulated via `sectionproperties`) and registered to OpenSees via `to_opspy_cmds`. `opst.anlys.MomentCurvature` imposes monotonic curvature about the local-y axis (internal zeroLength element) under constant axial force. Limit states: yield = steel reaches 2e-3 strain; ultimate = core concrete crushing at ecu=−0.0144. Bilinearised via equal-energy (`bilinearize`).

| Field | Value |
|-------|-------|
| Dimensions | NA (section analysis — no structural mesh) |
| Material | RC (fiber-section: Concrete04 cover+core + Steel01 rebar) |
| Lateral System | NA (section analysis) |
| Lateral Loading | Monotonic moment-curvature (curvature-imposed) |
| Earthquake Records | NA (static section analysis) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (opensy conda env, Python 3.12.12) |
| Units | N, mm, MPa |

## Running the model

```bash
conda activate opensy
python models/OPST_mc_section/model.py
```

## Verification

Moment-curvature limit states compared against the opstool docs reference (`https://opstool.readthedocs.io/en/stable/src/analysis/mc_analysis.html`):

| Point | Simulation | Reference | Difference |
|-------|-----------|-----------|------------|
| φy (yield curvature) | 1.620e-3 /m | 1.600e-3 /m | +1.24% |
| My (yield moment) | 20560 kN·m | 20553 kN·m | +0.04% |
| φu (ultimate curvature) | 4.375e-2 /m | 4.340e-2 /m | +0.81% |
| Mu (ultimate moment) | 23708 kN·m | 23750 kN·m | −0.17% |

All four limit-state points agree within 1.3%. The small residual differences come from triangle-mesh stochasticity (the `sectionproperties` triangulator is not seed-fixed), not from the unit conversion — the conversion kN-m→N-mm-MPa is an exact rescaling.

## Output

Written to `output/`:
- `mphi_curve.png` — M-φ curve with yield & ultimate points, bilinearised backbone, and reference markers overlaid
- `fiber_stress_strain.png` — fiber stress-strain responses by material (opstool `plot_fiber_responses`)

**References:**

Original source: opstool docs — [Moment Curvature Analysis of Section](https://opstool.readthedocs.io/en/stable/src/analysis/mc_analysis.html). Verbatim source preserved at `py_ref/mc_analysis_source.py` (kN-m units).

**Notes:** Converted from the opstool docs example. **Unit conversion (kN-m → N-mm-MPa):** stresses ×`kPa` (1 kN/m² = 1 kPa = 1e-3 MPa), geometry ×`m` (1 m = 1000 mm), moments via `kN*m` (1 kN·m = 1e6 N·mm), axial force ×`kN`. **Curvature-unit trap (§12ar):** `MomentCurvature.analyze(max_phi, incr_phi)` takes curvature in the model's length unit — source `incr_phi=1e-5` [1/m] becomes `1e-8` [1/mm] in N-mm (×1e-3); `max_phi` default 0.5 [1/m] → 5e-4 [1/mm]. A 1000× error here stops the analysis at step 0 or gives moments 1000× off. Strains (dimensionless) are unchanged. **Section-level layout adaptation:** §7 Nodes / §8 BCs / §9 Elements / §10 ODB / §11 Loading are omitted (MomentCurvature builds its own internal zeroLength element; no nodal ODB responses) — precedent §12p/§12q. **`FiberSecMesh` vs `ops.patch("rect")`:** the source uses opstool's polygon-patch mesher (supports the cover outline + central hole), not the raw `ops.patch("rect")` of §12ap/§12e (rectangles without holes). **`offset` sign:** `opst.pre.section.offset(d>0)` shrinks inward (docstring is reversed). **Visualisation:** the standard V1–V7 HTML stages don't apply (no mesh/nodal responses); custom matplotlib plots follow `standards/plot_utils.py` style.
