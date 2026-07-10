# VividConcrete_RCconc_full_subassembly

Rectangular RC column subassembly — nonlinear static **cyclic** test, standardised
to OpenSeesPy following the repo convention (`models/VividConcrete/model.py`).

## Source
`VividConcrete_RCconc_full_subassembly/tcl_ref/` (Kuanshi Zhong, Stanford column
cyclic-test framework):

| Tcl file | Role | Standardised into `model.py` |
|---|---|---|
| `ColumnCyclicTestVR.tcl` | main driver: model, gravity, cyclic | `run_analysis` / `run_gravity` / `run_cyclic` |
| `DesignVariableVR.tcl` | section & material scalars | §3 parameters |
| `CreateConcreteMaterial.tcl` | `Concrete02` confined/unconfined | `_unconfined_concrete02` / `_confined_concrete02` |
| `CreateRCColumnSection.tcl` | rectangular fiber + shear section | `create_column_section` |
| `GetGaussLobattoIP.tcl` | Gauss-Lobatto IPs (N=6) | `_GAUSS_LOBATTO_6` |
| `LoadingAlgorithmVR.tcl` | `RunStaticLoading` stepping w/ fallbacks | `run_cyclic` |
| `LoadingParameterVR.tcl` | `Lcol, numIntgrPts, P`, and the 22 455-pt `LoadHistory` | scalars in §3; `load_history.txt` |

`SetupBarSlip.tcl` is a **T-wall** bar-slip variant that is **not** `source`d by
`ColumnCyclicTestVR.tcl`; it is out of scope for this column model and left as-is
in `tcl_ref/`.

## What the model represents
A square (18×18 in) RC column, 108 in tall, along global Z:
- 6 Gauss-Lobatto integration points, each with its **own** fiber section
  (confined core + unconfined cover `Concrete02`, `ReinforcingSteel` wrapped by
  `DuctileFracture` longitudinal steel, `Hysteretic` shear aggregated on Vy/Vz).
- Two `zeroLengthSection` **bar-slip** end springs (`Bond_SP01`) at the
  column↔foundation and column↔beam interfaces.
- Axial gravity load `P = −232 kip` applied to the top control node, then
  displacement-controlled **cyclic** lateral loading in Y using the extracted
  experimental protocol.

## Units
Source is imperial (in, kip, ksi). Converted to **N, mm, MPa** via
`standards/units.py` (`inch, kip, ksi`). Material stresses → ×`ksi`; shear forces
→ ×`kip`; lengths/slips → ×`inch`.

## Cyclic protocol
`LoadingParameterVR.tcl`'s 22 455-point `LoadHistory` (inches) is extracted 1:1
into `load_history.txt` (one float per line) and read at run time
(`_read_load_history`), preserving the exact experimental displacement targets
(max ≈ 5.94 in ≈ 151 mm).

## Outputs
- `output/CyclicOutput/disp.out` — top lateral drift (node 2, DOF2)
- `output/CyclicOutput/force.out` — base shear (node 10001, DOF2 reaction)
  → use these two for the hysteresis loop.
- `output/vis_*.html` — opstool deformed-shape plots.
- `output/` ODB (`ModelData` / `RespStepData`).

## Run
Run with a Python that has `openseespy` + `opstool`. In this repo that is the
`opensy` conda env (Python 3.12.12):
```
C:/Users/micha/miniconda3/envs/opensy/python.exe model.py
```

## Compatibility notes
- `DuctileFracture` + `ReinforcingSteel -MPCurveParams` mirror the source Tcl
  flag-for-flag; they run under the `opensy` env's OpenSeesPy build.
- `BandGeneral` is used (source uses `BandGeneral`; `SparseGEN` is not compiled
  in this build).
- **Cyclic stepping:** the source's manual Newton→ModifiedNewton→Broyden→
  NewtonLineSearch fallback chain (a fixed-increment, per-step retry) stalls
  mid-protocol on hard unloading steps where the full increment cannot converge
  in one shot. `run_cyclic` therefore uses `opst.anlys.SmartAnalyze`
  (`relaxation=0.5`, `minStep=1e-3`, alternate algorithms + added test
  iterations), the repo convention (`elkady2019`, `padgett_jamie`). Each target
  increment is handed to SmartAnalyze via `static_split`, so the recorders still
  align 1:1 with the 22 455-pt experimental protocol while gaining adaptive
  sub-stepping on the hard steps.
- `openseespywin` (the pure-Python `openseespy` Windows backend) hard-requires
  Python 3.8; the `opensy` conda env (3.12.12) is used instead so the model
  executes end-to-end.
