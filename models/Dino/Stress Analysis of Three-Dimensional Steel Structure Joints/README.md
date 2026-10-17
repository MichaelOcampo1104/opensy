# Dino_SteelJoint

**Purpose:** Elasto-plastic displacement-controlled pushover of a 3D steel joint assembly (Dino Exam25). A 580-node, 542-element shell mesh (J2Plasticity steel, 20 mm PlateFiber section) is pushed down 10 mm at node 286 in 10 steps of −1.0 mm. Node-286 load-factor history is validated against `ref/OpenSees/node286.out`; element-366 stresses against `Stress366.out`.

**Building System:** 3D steel joint assembly meshed with **542 `ShellMITC4`** shell elements over 580 nodes. 28 fully-fixed support nodes. **Material:** J2Plasticity steel (K=171666, G=79231 MPa, sig0=200, sigInf=300 MPa) wrapped by a `PlateFiber` matrix into a 20 mm `PlateFiber` shell section. (The commented `ElasticIsotropic 16` line is superseded by the active J2Plasticity line and not defined.) Lumped mass on UX/UY (static pushover — mass is inactive).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). Single Plain pattern (tag 3) applies 5 × −4e5 N UZ reference loads (nodes 272, 273, 286, 293, 300); `DisplacementControl` (node 286, DOF 3/UZ) via `opst.anlys.SmartAnalyze`, one −1.0 mm increment per reference step (`static_split([incr], maxStep=|incr|)`, §12am cadence) for 1:1 alignment with the 10-row reference. No gravity phase, no `loadConst` — the single pattern stays active throughout.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (J2Plasticity + 20 mm PlateFiber shell section) |
| Structural System | Steel joint shell assembly (542 ShellMITC4, 580 nodes) |
| Loading | Displacement-controlled UZ pushover (−1.0 mm × 10 steps = −10 mm) |
| Analysis Type | Static — DisplacementControl via SmartAnalyze |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Stress Analysis of Three-Dimensional Steel Structure Joints/model.py"
```

## Verification

Node 286 history (LF, UX, UY, UZ) at every recorded step, compared against the source reference (`ref/OpenSees/node286.out`, 10 rows: col 0 = load factor, cols 1–3 = node-286 UX/UY/UZ). Element-366 stresses (`Stress366.out`: col 0 = time, cols 1–32 = stresses) spot-checked via in-loop `ops.eleResponse(366, "stresses")`.

| Quantity | Simulation | Reference | Notes |
|----------|-----------|-----------|-------|
| Steps recorded | 10 / 10 | 10 | exact 1:1 |
| LF final (step 10) | 0.56948 | 0.56948 | 0.0001% |
| LF per-point | RMS 0.00000 | — | mean rel error 0.0001% |
| UY final | 1.76745 mm | 1.76745 mm | 0.0001% |
| UZ final | −10.00000 mm | −10.00000 mm | imposed, exact |
| Ele-366 stresses >1 MPa | RMS 0.00108 MPa | — | mean rel error 0.0001% (peaks ~2300 MPa) |

Displacements match to **≤0.0001%**; stresses above 1 MPa match to **0.0001%** (RMS 0.001 MPa). Near-zero shear terms (~1e-10 MPa) agree to 3e-10 MPa absolute — their relative error is meaningless and excluded.

## Output

Written to `output/`:
- `node286_disp_history.csv` — (step, LF, UX, UY, UZ) at each of the 10 recorded steps
- `ele366_stress_history.csv` — ele-366 stresses per step (MPa)
- `pushover_compare.png` — capacity (UZ vs LF) + LF history: simulation (red dashed) vs `node286.out` reference (black solid)
- `vis_01_nodes.html` … `vis_07_animation.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis, V5 final deformed UZ, V6 step-slider, V7 animation)
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal + shell responses)

**References:**

Original source: `ref/OpenSees/EXAM25.tcl` (1430-line Tcl ShellMITC4 joint model) + `ref/OpenSees/EXAM25.s2k` (SAP2000 sibling). Reference results: `ref/OpenSees/node286.out` (10-row node-286 recorder), `node0.out` … `node5.out` (full-field recorders, nodes 1–580 in six ranges), `Stress366.out` (10-row ele-366 stress recorder).

**Notes:** Converted from `EXAM25.tcl`. **Shell recipe** (§12as): `nDMaterial J2Plasticity` (K, G, sig0, sigInf, delta1, delta2 verbatim) → `nDMaterial PlateFiber` → `section PlateFiber` (20 mm); `element ShellMITC4 tag n1 n2 n3 n4 secTag` needs no transform/integration objects. **Element tags are 0-based** (0–541) in the source and preserved verbatim. **No MP constraints:** the source prints a `"rigidDiaphragm"` label but issues no MP commands, so `constraints("Plain")` throughout (§12an does not apply). **`save_shell_resp=True`** in CreateODB (shell stress responses; frame/truss disabled). **Source quirks:** `fix` lines carry trailing `;` (regex tolerates). Source already N-mm-MPa (masses used directly). **Path depth:** standards/ is `parents[3]` (nests under `models/Dino/<analysis-name>/`) with `parents[2]` fallback. Run with: `uv run python "models/Dino/Stress Analysis of Three-Dimensional Steel Structure Joints/model.py"`
