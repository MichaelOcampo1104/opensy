# Dino_HingedLinks

**Purpose:** Linear-static gravity check of a 3D one-storey steel frame (Dino Exam12) validating the ETABS rigid-link + moment-release detail against the OpenSees `zeroLength` + `equalDOF` hinge method. Ten −10 kN roof loads are applied in a single Linear step; nodal displacements validate against `ref/OPENSEES/node0.out`, element local forces against `ele0.out`.

**Building System:** One storey, 4 m X-bay × 4 × 4 m Y-bays, 3 m high. Ten DH200X200 columns (fiber SEC_COL, E = 206000 MPa) each split by a `zeroLength` rotational hinge (k = 1.0 N-mm/rad on dirs 4/5/6, translations carried by paired `equalDOF 1 2 3`) at both ends -- the OpenSees analogue of the ETABS `RIGID`-segment + `RELEASE M2/M3` detail (`EXAM12.e2k` C*-1/C*-9 lines). Roof/ground beams are DH200X500 (SEC_BEAM); transverse X-beams DH200X200. Four corner bases fixed; 10 roof masses (1.02 N-s²/mm on UX/UY).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6). 40 nodes, 36 `dispBeamColumn` fiber elements (Lobatto-3 per section, transfTag == eleTag: columns vecxz (1,0,0), beams (0,0,1)) + 20 `zeroLength` hinges. Single Plain pattern (tag 1) applies 10 × −10000 N UZ at nodes 1/3/5/8/10/21/23/25/28/30. Linear-static LoadControl in one step (`algorithm Linear`, documented AGENT.md §3c exception -- SmartAnalyze forces DisplacementControl and cannot reproduce single-step load-controlled gravity), ODB fetch, then `loadConst`.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (Elastic E = 206000 MPa fibers; hinge k = 1.0) |
| Structural System | 1-storey steel frame (36 dispBeamColumn + 20 zeroLength hinges, 40 nodes) |
| Loading | Gravity static, 10 × −10 kN UZ roof loads, 1 step |
| Analysis Type | Static linear -- LoadControl via permitted `ops.analyze()` exception |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, opstool CreateODB) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Methods for Handling Hinged Links/model.py"
```

## Verification

Single static step (`ok=0`) against the source recorders (first column = pseudo-time 1.0, dropped before compare).

| Quantity | Simulation | Reference | Notes |
|----------|-----------|-----------|-------|
| Steps recorded | 1 / 1 | 1 | `ok=0` |
| Node disp (40×3) | RMS 1.27e-06 mm | -- | \|ref\|>1e-9 mm mean rel 0.0001% (UX/UY ~1e-14 noise excluded) |
| UZ range | [−2.48838, 0.0] mm | [−2.48838, 0.0] mm | UZ RMS 2.2e-06 mm |
| Node 8 UZ | −2.48838 mm | −2.48838 mm | dedicated `node8.out` recorder |
| Ele localForce (56) | RMS 3.24 | -- | shear sign-adjusted, \|ref\|>1 mean rel 0.0001% (80/492 terms) |
| Max \|localForce\| | 43.68M N / N-mm | ~43.68M | ground-beam end moment |

Displacements match to **0.0001%**; element forces match to **0.0001%** after the documented shear sign adjustment (axial/torsion/moments +1.000, shears −1.000 between Tcl recorder and OpenSeesPy `eleResponse`).

## Output

Written to `output/`:
- `node_disp_sim.csv` -- (ux,uy,uz) mm for nodes 1..40
- `vis_01_nodes.html` … `vis_04_pre_analysis.html` -- opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis)
- `vis_05_deformed.html`, `vis_06_slider.html` -- UZ deformed + step slider
- `RespStepData-1.odb/`, `ModelData-1.zarr/` -- ODB response database (nodal + frame + link)

**References:**

Original source: `ref/OPENSEES/exam12.tcl` (247-line Tcl frame + `ele0.out`/`node0.out`/`node8.out` recorders) + `ref/ETABS/EXAM12.e2k` (ETABS 9.7.4 rigid-link + release sibling).

**Notes:** Converted from `exam12.tcl`. **Hinge recipe:** `element zeroLength tag i j -mat 1 1 1 -dir 4 5 6` (k=1.0 rotational) + `equalDOF r c 1 2 3` (translations) per column end -- ETABS `RIGID` + `RELEASE M2I/M3I/M2J/M3J` analogue. **Fiber + Py deltas:** 3D `section Fiber` needs `-GJ` (open-section J: beam 2.293e6 / col 3.318e5 mm4); `dispBeamColumn` takes `(tag,i,j,transfTag,integTag)` via shared Lobatto-3 `beamIntegration` per section (not Tcl inline numIntPts). **Shear sign:** Tcl recorder vs Py `eleResponse` differ by −1 on Vy/Vz (asserted per-element, adjusted in verification). **LoadControl exception** (§3c/§10): linear gravity uses manual `ops.analyze(1)` + ODB fetch + `loadConst`. **MAT 2** (25500 MPa) is dead code in the source, kept for fidelity. **Path depth:** standards/ is `parents[3]` (nests under `models/Dino/<analysis-name>/`) with `parents[2]` fallback. Run with: `uv run python "models/Dino/Methods for Handling Hinged Links/model.py"`
