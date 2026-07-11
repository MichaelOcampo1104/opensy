# ZhongKuanshi

**Purpose:** Calibrate HystereticSM shear hinges against 7 cyclic RC beam-column joint tests (Naish 2015) using the Zhong (2016) calibration framework — parametric 7-case sweep.

**Building System:** 7 RC beam-column joint specimens from the Naish (2015) test series: CB24F (baseline), CB24D, CB24F-RC (rectangular column), CB24F-PT (post-tensioned), CB24F-12-PT (1/2 PT), CB33F and CB33D (deeper beams, L=60 in). Section b=12 in, h=15–18 in, clear span L=36–60 in, fc=6.85–7.31 ksi. Each specimen modelled as two elastic beam-column elements (Ec from ACI 57000√fc') with a zeroLength HystereticSM shear hinge at mid-span, tied by equalDOF on UX+RZ.

**Model Description:** 2D OpenSeesPy model (ndm=2, ndf=3) with 4 nodes, 3 elements (2 elasticBeamColumn + 1 zeroLength HystereticSM hinge). Each case driven by a displacement-controlled cyclic protocol (~962–1880 steps) parsed from the source LoadingParameter tcl files. The HystereticSM backbone is defined in force-deformation space: y_i = V_i × rpp (kip), x_i = θ_i × L (in), with negative envelope scaled by rnp. Manual `ops.analyze(1)` loop with DisplacementControl + 6-algorithm fallback ladder mirroring the source RunStaticLoading.tcl.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | RC (elastic beam-column + HystereticSM concentrated shear hinge) |
| Lateral System | Beam-column joint subassembly (shear hinge) |
| Lateral Loading | Quasi-static cyclic (displacement-controlled, chord-rotation protocol) |
| Earthquake Records | NA (static cyclic) |
| Design Year | 2015 (Naish tests), 2016 (Zhong framework) |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (opensy conda env, Python 3.12.12) |
| Units | N, mm, MPa |

## Running the model

```bash
# Activate the target environment
conda activate opensy

# Run a single case (default: naish_cb24d)
python models/ZhongKuanshi/model.py naish_cb24d

# Run all 7 cases
python models/ZhongKuanshi/model.py all
```

Available cases: `naish_cb24f`, `naish_cb24d`, `naish_cb24f-rc`, `naish_cb24f-pt`, `naish_cb24f-12-pt`, `naish_cb33f`, `naish_cb33d`.

## Cases

| Case ID | b (in) | h (in) | L (in) | fc (ksi) | V_peak (kip) | Steps |
|---------|--------|--------|--------|----------|--------------|-------|
| naish_cb24f | 12 | 15 | 36 | 6.85 | 170.0 | 1108 |
| naish_cb24d | 12 | 15 | 36 | 6.85 | 159.2 | 1078 |
| naish_cb24f-rc | 12 | 15 | 36 | 7.31 | 191.2 | 1050 |
| naish_cb24f-pt | 12 | 15 | 36 | 7.24 | 210.9 | 1074 |
| naish_cb24f-12-pt | 12 | 15 | 36 | 6.99 | 188.4 | 962 |
| naish_cb33f | 12 | 18 | 60 | 6.85 | 123.6 | 965 |
| naish_cb33d | 12 | 18 | 60 | 6.85 | 118.2 | 1880 |

## Verification

All 7 cases verified against the source Tcl reference (`tcl_ref/SimuOutput/*/disp.out`):
- **Step counts**: exact match (1078/1078, 1108/1108, etc.)
- **Peak shear**: within 1% across all cases
- **Hysteretic energy**: within 0.6–5.3%

## Output

Per case, written to `output/<case_id>/`:
- `hysteresis_curve.csv` — (shear [N], disp [mm]) at each converged step
- `hysteresis_compare.png` — simulation vs test data overlay
- `vis_01_nodes.html` … `vis_05_deformed.html` — opstool visualisations
- `RespStepData-1.odb/` — ODB response database

**References:**

Zhong, K. (2016). ShearHingeCalibration.m MATLAB framework, Stanford University. Source Tcl/MATLAB: `tcl_ref/` (run_simulation.tcl, load_algorithm.tcl, model_id.tcl, hinge_calibration_examples.csv, ModelingParameters/*.tcl, LoadingHistory/*.tcl, TestData/*.txt, SimuOutput/*/).

Naish, D. (2015). RC beam-column joint test series.

**Suggested Citation:**

Zhong, K. (2016). ShearHingeCalibration framework. Stanford University. Naish, D. (2015). RC beam-column joint test series.

**Notes:** Converted from Tcl/MATLAB framework. CRITICAL UNIT FIX: source Tol=1e-4 is in kip·in energy units; in N-mm it must be scaled by `kip*inch` (=112985) → TOL=11.3 N-mm, otherwise the analysis stalls at ~30% of the protocol (EnergyIncr 100000× too tight). SHEAR READING: base shear must be read from the zeroLength element force (`eleResponse` hinge forces, DOF 2), NOT `nodeReaction` at the fixed node — under `equalDOF`+`Plain` constraints the retained-node reaction includes the MP-constraint force, giving values 2–3× the backbone capacity past first yield. Source uses HystereticSM (Mazzoni 2023), available in standard OpenSeesPy.
