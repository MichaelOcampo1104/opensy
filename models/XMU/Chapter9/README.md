# XMU Chapter 9 — Steel01 Parameter Optimization

Textbook example from XMU Finite Element Analysis course, Chapter 9.
Demonstrates material parameter optimization using `scipy.optimize.minimize`
(L-BFGS-B) in place of the original SNOPT solver.

## Model

- **ndf=2** truss model: 4 nodes, 3 truss elements
- 2 `Steel01` bilinear materials with 6 design variables:
  E1, fy1, b1, E2, fy2, b2
- Tabas earthquake ground motion (UniformExcitation, factor=g)
- SmartAnalyze Transient with Newmark integration (γ=0.55, β=0.275625)
- 2000 steps at dt=0.01 s
- Full ODB lifecycle + opstool visualization stages (AGENT.md v1.15.0)
- Units: **N, mm, MPa, s** (converted from SI)

## Architecture

Two-path design to keep the optimization loop lean while producing full
AGENT.md-compliant ODB + HTML outputs on the final run:

| Path | Function | When | ODB | Vis |
|------|----------|------|-----|-----|
| Optimization | `run_obj_fem()` | 50× inside scipy loop | No | No |
| Visualization | `run_analysis()` | Once after convergence | Yes | V1–V6 |

## Optimization

- **Objective**: sum of squared errors between experimental and FEM
  node-4 UX displacement
- **Solver**: `scipy.optimize.minimize(method="L-BFGS-B")`, max 50 iterations
- **Replaces**: original SNOPT (`runSNOPTAnalysis`)

| Variable | Start (MPa) | Lower bound (MPa) |
|----------|-------------|-------------------|
| E1       | 180         | 100               |
| fy1      | 0.27        | 0.1               |
| b1       | 0.016       | 0.0               |
| E2       | 180         | 100               |
| fy2      | 0.27        | 0.1               |
| b2       | 0.016       | 0.0               |

## File Structure

```
Chapter9/
├── model.py                # Main script: FE model + scipy optimization
├── post_process.py         # ODB deformed HTML + matplotlib comparison plots
├── README.md               # This file
├── ground_motions/
│   ├── tabas.txt           # Tabas ground motion (g units, dt=0.02)
│   └── .gitkeep
├── node4_exp.txt           # Experimental node-4 displacement history
├── sntoya.spc              # Original SNOPT parameters (archival)
├── main.tcl                # Original SNOPT driver (archival)
├── tclFileToRun.tcl        # Original FE model (archival)
├── F.tcl                   # Original objective function (archival)
└── output/                 # Generated results (git-ignored)
    ├── opt_results.json           # Optimised parameters
    ├── node4_optimised.out        # Full-resolution FEM displacement
    ├── vis_01_nodes.html          # V1 — nodes + supports
    ├── vis_02_model.html          # V2 — full undeformed geometry
    ├── vis_03_loads.html          # V3 — load vectors
    ├── vis_04_pre_analysis.html   # V4 — pre-analysis check
    ├── vis_05_deformed_peak.html  # V5 — peak deformation
    ├── vis_06_deformed_slider.html # V6 — step-by-step slider
    └── figures/
        ├── vis_comparison.png
        └── vis_error.png
```

## Usage

```bash
conda activate opensy
python model.py            # Run optimization + final vis run
python post_process.py     # Regenerate comparison plots + ODB HTML
```

## Conversion Notes

- SNOPT replaced with `scipy.optimize.minimize` (L-BFGS-B, supports bounds)
- SI units (N, m, kg, Pa) converted to N-mm-MPa
- Mass: ÷1000 (kg → N·s²/mm), Stress: ÷1e6 (Pa → MPa)
- Ground motion factor: ×1000 (m/s² → mm/s²)
- Optimization path uses SmartAnalyze with in-memory nodeDisp tracking
  (no ODB/file I/O overhead per iteration)
- Final visualization path uses full ODB lifecycle with throttled
  fetch_response_step (every 5th step) + all 4 vis stages + deformed HTML
