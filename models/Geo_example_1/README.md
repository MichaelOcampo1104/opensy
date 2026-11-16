# Geo_example_1

**Purpose:** Elastic plane-strain site-response test of one quad with a PressureIndependMultiYield material under a 1 Hz sinusoidal base acceleration (OpenSees geotechnical Example 1, Zhaohui Yang, UCSD).

**Building System:** NA. Single-element material test, no structure.

**Model Description:** One 1 m x 1 m plane-strain quad, 1 m thick. The base nodes are fixed in x and y, and the top nodes are tied in x and y after gravity. Gravity enters as the element body force (buoyant unit weight). The base acceleration is a `UniformExcitation` pattern (Sine, 1 Hz, 9.81 m/s^2 amplitude). The source's `VariableTransient` is replaced by a fixed 0.01 s SmartAnalyze step over 2000 steps. The material stays in its elastic stage.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | Soil, PressureIndependMultiYield (elastic stage) |
| Lateral System | NA |
| Lateral Loading | Dynamic, sinusoidal base acceleration |
| Earthquake Records | NA (synthetic sine, 1 Hz, 9.81 m/s^2) |
| Design Year | NA |
| File Format | .py (source: `tcl_ref/example_1.tcl`) |
| OpenSees Version | Converted for openseespy 3.8.0 and opstool 1.0.26 |
| Units | N, mm, MPa, s |

**Validation** (`output/validation.txt`, written by `model.py`): displacement, acceleration, and stress and strain at Gauss points 1 and 3 match the six source outputs. The largest error is 4.7e-6 of each reference peak (pass threshold 1e-3). `output/response_compare.png` overlays the responses.

**References:**
Source script and outputs: `tcl_ref/example_1.tcl`, `tcl_ref/disp.out`, `tcl_ref/acce.out`, `tcl_ref/stress1.out`, `tcl_ref/strain1.out`, `tcl_ref/stress3.out`, `tcl_ref/strain3.out`.

**Suggested Citation:** NA

**Notes:**
- Source units are SI (m, kN, t, s), converted to N-mm-MPa-s. The density 2.0 t/m^3 is 2.0e-9 N.s^2/mm^4, because 1 t = 1 N.s^2/mm. `units.py` `kg` and `tonne` are not used for mass (see LESSONS.md, entry 31).
- The current PressureIndependMultiYield needs `frictionAng`, `refPress`, `pressDependCoe` and `numberOfYieldSurf`. The source omits them, so the model uses 0, 100 kPa, 0 and 20. These values do not change the elastic response.
- `updateMaterialStage -stage 0` reports "no effect" for this material in the current build. The response is still elastic: the peak in-plane shear is 10.4 kPa against 30 kPa cohesion.
- The `recorder ... material 1` and `material 3` lines select Gauss points 1 and 3, not material tags. The source's `FluidSolidPorous` (tag 1) is never used by the element, so it is omitted.
- On Windows, run with `PYTHONIOENCODING=utf-8`. SmartAnalyze's success line (with an emoji) crashes the default cp1252 console even with `printPer=0`.

**Run:**
```bash
cd models/Geo_example_1
PYTHONIOENCODING=utf-8 python model.py
```
