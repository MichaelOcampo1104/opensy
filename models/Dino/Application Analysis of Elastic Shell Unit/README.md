# Dino_ElasticShell

**Purpose:** Linear-static lateral (PUSH) check of an L-shaped 100 mm elastic concrete shell wall assembly (Dino Exam13). Six 100 kN UX loads at the top edge are applied in a single Linear step; nodal displacements validate against `ref/OpenSEES/node0.out` (nodes 1–100) and `node1.out` (nodes 101–121).

**Building System:** L-shaped wall assembly meshed with **100 `ShellMITC4`** shell elements over 121 nodes: X-leg (500 × 3000 mm, 5 × 10 panels of 100 × 300 mm at Y = 0) + Y-leg (700 × 3000 mm, 5 × 10 panels of 140 × 300 mm at X = 0). **Material:** C45 concrete `ElasticIsotropic` (E = 32500 MPa, nu = 0.2) wrapped by a `PlateFiber` matrix into a 100 mm `PlateFiber` shell section. 11 fully-fixed base nodes; lumped UX/UY mass (static PUSH — mass is inactive).

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6) replaying `EXAM13.tcl` verbatim via regex (nodes/mass/fix/shells). Single Plain pattern (tag 1) applies 6 × 100 kN UX reference loads (nodes 4, 6, 79, 90, 101, 112); Linear-static `LoadControl` in one step (documented AGENT.md §3c exception — SmartAnalyze forces DisplacementControl and cannot reproduce single-step load-controlled cases) with ODB fetch, then `loadConst`.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Concrete (ElasticIsotropic C45 + 100 mm PlateFiber shell section) |
| Structural System | L-shaped shell wall assembly (100 ShellMITC4, 121 nodes) |
| Loading | Lateral PUSH, 6 × 100 kN UX at top edge, 1 step |
| Analysis Type | Static linear — LoadControl via permitted `ops.analyze()` exception |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (.venv, opstool CreateODB) |
| Units | N, mm, MPa |

## Running the model

```bash
# from repo root (UTF-8 console required on Windows for SmartAnalyze progress bars)
$env:PYTHONIOENCODING="utf-8"; uv run python "models/Dino/Application Analysis of Elastic Shell Unit/model.py"
```

## Verification

Single static step (`ok=0`) against the source recorders (first column = pseudo-time 1.0, dropped before compare; `node0.out` = nodes 1–100, `node1.out` = nodes 101–121).

| Quantity | Simulation | Reference | Notes |
|----------|-----------|-----------|-------|
| Steps recorded | 100 / 100 | 1 | `ok=0`; source applies full load in 1 step, we ramp over 100 (linear — final identical) |
| Node disp (121×3) | RMS 4.19e-05 mm | — | \|ref\|>1e-9 mm mean rel 0.0001% |
| UX range | [0.0, 159.79076] mm | [0.0, 159.79100] mm | UX RMS 7.0e-05 mm |
| Node 6 UX | 159.79076 mm | 159.79100 mm | dedicated `node6.out` recorder (file not shipped; covered via node0 range) |
| Node 112 UX (top loaded) | 144.17521 mm | 144.17500 mm | — |

Displacements match to **0.0001%** (absolute RMS ~4e-05 mm on peaks ~160 mm).

## Output

Written to `output/`:
- `node_disp_sim.csv` — (ux,uy,uz) mm for nodes 1..121
- `vis_01_nodes.html` … `vis_04_pre_analysis.html` — opstool visualisations (V1 nodes, V2 model, V3 loads, V4 pre-analysis)
- `vis_05_deformed.html`, `vis_06_slider.html` — UX deformed + step slider
- `RespStepData-1.odb/`, `ModelData-1.zarr/` — ODB response database (nodal + shell)

**References:**

Original source: `ref/OpenSEES/EXAM13.tcl` (296-line Tcl ShellMITC4 wall model) + `ref/OpenSEES/EXAM13.s2k` (SAP2000 sibling) + `ref/ETABS/EXAM13.EDB`. Reference results: `ref/OpenSEES/node0.out` (nodes 1–100), `node1.out` (nodes 101–121).

**Notes:** Converted from `EXAM13.tcl`. **Shell recipe:** `nDMaterial ElasticIsotropic` (E, nu verbatim) → `nDMaterial PlateFiber` → `section PlateFiber` (100 mm); `element ShellMITC4 tag n1 n2 n3 n4 secTag` needs no transform/integration objects. **Dead tags 1/3** (uniaxial Elastic) kept for fidelity, never referenced. **No MP constraints:** the source prints a `"rigidDiaphragm"` label but issues no MP commands, so `constraints("Plain")` throughout. **`save_shell_resp=True`** in CreateODB (shell responses; frame/truss disabled). Source already N-mm-MPa (masses used directly). **Path depth:** standards/ is `parents[3]` (nests under `models/Dino/<analysis-name>/`) with `parents[2]` fallback. Run with: `uv run python "models/Dino/Application Analysis of Elastic Shell Unit/model.py"`
