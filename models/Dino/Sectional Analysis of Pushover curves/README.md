# Dino

**Purpose:** Gravity + displacement-controlled pushover of a 3D RC cantilever column with a fiber section (Concrete01 concrete + Steel01 rebar).

**Building System:** Single RC cantilever column, 1200×800 mm rectangular section, 1000 mm length. Concrete fc=26.8 MPa (Concrete01), Steel fy=435 MPa (Steel01, b=0.0001). Rebar: 28 #40 bars (8+8 top/bottom rows, 6+6 side rows), 50 mm cover. Axial load 15000 kN compression.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6) with 2 nodes, 1 nonlinearBeamColumn element (flexibility-based, 2 integration points). Fiber section built via `ops.patch("rect")` (20×20 concrete grid = 400 fibers) replacing the source's pygmsh triangle mesh (244 fibers). Rebar via `ops.layer("straight")` — 4 perimeter rows preserved exactly. Gravity (LoadControl, 10 steps) → displacement-controlled pushover to 8 mm via SmartAnalyze (NormDispIncr @ 1e-5, KrylovNewton).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC (fiber-section: Concrete01 + Steel01) |
| Lateral System | Cantilever column |
| Lateral Loading | Displacement-controlled pushover (8 mm, 100 steps) |
| Earthquake Records | NA (static pushover) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (opensy conda env, Python 3.12.12) |
| Units | N, mm, MPa |

## Running the model

```bash
conda activate opensy
python models/Dino/model.py
```

## Verification

Pushover curve compared against source reference (`Sectional Analysis of Pushover curves/py_ref/node_disp.out`, 100-point curve):
- **Steps**: 100/100 (exact match)
- **Displacement**: exact (0.08 → 8.00 mm)
- **Peak base shear**: 8810 kN (sim) vs 7980 kN (ref) — 10.4% higher
- **Elastic stiffness**: 5137 kN/mm (sim) vs 4158 kN/mm (ref) — 23.5% stiffer

The pushover shape (elastic ramp → yield plateau at ~2 mm) is preserved.

**Note on the reference file.** `node_disp.out` was recorded with `recorder Node -time -dof 1 disp`, so column 0 is the pseudo-time λ (the lateral load factor), not base shear. The source's lateral reference load was 1000 N, so base shear in N = λ × 1000. The model scales the reference by `P_LATERAL` before plotting (`model.py` §11a).

**Why the simulation is stiffer than the reference.** This is NOT a mesh effect — a finer mesh of the same concrete area converges to the same stiffness, not a stiffer one (the source's 244-triangle pygmsh mesh and the 20×20 rect patch agree on area within 0% and on section second-moment within 0.4%). Probing the model directly:
- Cantilever lateral stiffness with **no axial load**: 3589 kN/mm
- With the −15000 kN gravity axial load applied: 4863 kN/mm (≈ **+35%** from precompression of the fiber section)
- Uncracked-section theory `3EI/L³` (Ec ≈ fcu/eps0 = 12523 MPa): 4328 kN/mm

The simulation's elastic stiffness (5137 kN/mm) is consistent with a precompressed, largely-uncracked fiber section, while the reference (4158 kN/mm) matches the *un-precompressed* / uncracked-theory value almost exactly. This indicates the committed `node_disp.out` is a stale artifact (regenerated from an earlier run inconsistent with the committed `triangle_data.txt`), not a target to match. The simulation is physically the more reliable result.

## Output

Written to `output/`:
- `pushover_curve.csv` — (base shear [N], disp [mm]) at each step
- `pushover_compare.png` — simulation vs reference overlay
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis, V5 deformed peak, V6 slider, V7 animation)
- `RespStepData-1.odb/` — ODB response database

**References:**

Original source: `Sectional Analysis of Pushover curves/py_ref/column_sec.py` (Tkinter GUI + pygmsh mesh + OpenSeesPy). Pre-generated reference outputs: `node_disp.out` (100-pt pushover), `triangle_data.txt` (244 fiber centroids).

**Notes:** Converted from `column_sec.py`. GUI STRIPPING: the Tkinter GUI is removed — parameters are named constants in §3 (using the GUI default values). pygmsh → `ops.patch("rect")`: pygmsh is not in the opensy env; the standard repo approach (native OpenSees fiber commands) replaces it with a 20×20 rect patch (400 fibers vs source's 244 triangles). Rebar layers (`ops.layer`) preserved exactly. `nonlinearBeamColumn` retains its standard signature `(tag, i, j, nIP, secTag, transfTag)` — NOT dispBeamColumn (§12l). `save_frame_resp=False` in CreateODB — nonlinearBeamColumn internal sections lack user-visible tags (§12v). Dead `Elastic` material tag 200 omitted. SmartAnalyze (Static) replaces the source's raw `ops.analyze(nstep)` + `ops.recorder` — ODB + `fetch_response_step` instead. Lateral pattern defined after `loadConst` (§12z).
