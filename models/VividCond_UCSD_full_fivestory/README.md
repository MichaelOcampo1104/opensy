# VividCond_UCSD_full_fivestory

5-story RC **frame-wall building** — nonlinear seismic time-history, standardised
to OpenSeesPy following the repo convention.

## Source
`VividCond_UCSD_full_fivestory/tcl_ref/` (Kuanshi Zhong, Stanford/UCSD
frame-wall building framework):

| Tcl file | Role | Standardised into `model.py` |
|---|---|---|
| `UCSDFrameWall.tcl` | main driver: geometry, materials, sections, elements, gravity, eigen, damping | `run_analysis` + build functions |
| `CreateConcreteMaterial.tcl` | regularized confined/unconfined `Concrete02` (Pugh 2015; rectangular `ke1·ke2·ke3` confinement) | `_unconfined_concrete02` / `_confined_concrete02` |
| `BuildRCrectSection3D.tcl` | rectangular beam/column/slab fiber section + shear aggregator | `_build_rc_rect_section` |
| `CreateRCWallSection.tcl` | `CreatePlanarWallSection` (boundary elements + web + shear) | `_create_planar_wall_section` |
| `GetGaussLobattoIP.tcl` | Gauss-Lobatto IPs (N=6) | `_GAUSS_LOBATTO_6` |
| `RunTests.tcl` | 13-motion driver + recorders | `run_dynamic` (X-only NR94) + recorders |
| `SolverNewmark.tcl` | Newmark + adaptive dt/tol/algorithm recovery | `opst.anlys.SmartAnalyze` (Transient) |
| `RecorderAnalysis.tcl` | alternate recorder/collapse variant | folded into recorders |

## What the model represents
A 5-story RC building (3D, ndm=3 ndf=6) with dual lateral systems:
- **Two 2-bay perimeter moment frames** (south y=0, north y=120 ft) — 3 columns
  + 2 beams per frame per story, `forceBeamColumn` with rectangular fiber
  sections (confined core + unconfined cover `Concrete02`, `Steel02`+`
  DuctileFracture` steel, `Hysteretic` shear aggregator).
- **2 planar RC shear walls** (`CreatePlanarWallSection` fiber sections with
  boundary elements + web).
- **`corotTruss` diagonal braces** (`ElasticPPGap`) between south/north frame
  corners.
- **Rigid floor diaphragms** (`rigidDiaphragm 3`) tying each floor's frame/wall
  nodes to a master diaphragm node carrying the story translational mass.
- Gravity (Constant pattern, per-node tributary point loads) → Rayleigh damping
  (ζ=0.02 on modes 1 & 3) → seismic time-history under a horizontal GM.

~54 nodes, ~72 elements (62 forceBeamColumn + 10 corotTruss), per-IP sections
(5 stories × 6 IPs × 4 section types).

## Units
Source is imperial (in, kip, ksi). Converted to **N, mm, MPa** via
`standards/units.py` (`inch, ft, kip, ksi`). Material stresses → ×`ksi`; forces
→ ×`kip`; lengths → ×`inch`/`ft`; story mass = `W[kip]·kip / (g[mm/s²])` per §12al.

## Ground motion
The source runs 13 triaxial base motions (`base_motions/`, not in the repo).
For end-to-end validation the Northridge-1994 record **NR94cnp.txt**
(dt=0.01 s, ~2495 pts, g-units, reused from VividConcrete/elkady2019) is loaded
as a single `UniformExcitation` in direction 1 (X). `run_dynamic()` is generic —
real triaxial records drop in via `GM_FILE`/`GM_DT`/`GM_NPTS`/`GM_DIR`.

## Outputs
- `output/DynamicOutput/story_disp.out` — X-displacement of the 5 diaphragm
  master nodes (roof drift).
- `output/vis_*.html` — opstool node/model/load/pre-analysis/peak-deformed plots.
- `output/` ODB (`ModelData` / `RespStepData`).

## Run
Run with a Python that has `openseespy` + `opstool`. In this repo that is the
`opensy` conda env (Python 3.12.12):
```
C:/Users/micha/miniconda3/envs/opensy/python.exe model.py
```

## Compatibility notes
- `DuctileFracture` + `Steel02` mirror the source Tcl flag-for-flag; they run
  under the `opensy` env's OpenSeesPy build. Set `FRAC_TAG = 0` to use plain
  `Steel02` (faster, no fracture tracking).
- **Confined concrete:** the source's rectangular confinement factor
  `ke = ke1·ke2·ke3/(1−rou_cc)` (different from the simpler
  `(nl−2)/nl·(1−s/b)` used in the VividConcrete column models) is ported
  faithfully from `CreateConcreteMaterial.tcl`.
- **Constraints:** `Transformation` is used throughout (for the `rigidDiaphragm`
  multi-point constraints). Source dynamic uses `SparseGEN`, not compiled in
  this OpenSeesPy build → `BandGeneral` (per §12af).
- **Solver:** `opst.anlys.SmartAnalyze` (Transient) replaces the source's manual
  adaptive-dt/tol/algorithm recovery loop, with the repo-convention retry
  settings (`relaxation=0.5`, `minStep=1e-6`, `algoTypes=[40,10,20,30,50]`).
- **ODB:** `save_frame_resp=False` — `forceBeamColumn` fiber sections +
  `corotTruss` braces are not collected frame-by-frame (§12ai: corotTruss in
  `frame_tags` crashes opstool's basic-force extractor).
- `openseespywin` gates on Python 3.8; the runnable interpreter is the conda
  `opensy` env (3.12.12).
