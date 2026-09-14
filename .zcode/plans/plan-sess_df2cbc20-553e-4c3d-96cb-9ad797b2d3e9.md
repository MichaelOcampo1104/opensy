## Convert `models/Dino/Analysis of a Pseudo-Collapse Test on a Frame Structure` → standardized OpenSeesPy

This is **CONVERT mode** (AGENT.md §7b): translate the Tcl source `tcl_ref/co.tcl` into a standard-conforming `model.py`, generate `README.md`, sync the catalogue, and **verify by running**.

### Files to create / change
1. **`model.py`** (new) — the standardized OpenSeesPy model.
2. **`README.md`** (new) — auto-generated from the catalogue entry (§9).
3. **`output/.gitkeep`** (new) — keep the git-ignored output dir.
4. **`opensees_catalogue.json`** (edit, root) — append one entry, `Dino_PseudoCollapse`.

### model.py — conversion decisions (all matching the source `co.tcl` and repo §-conventions)

**Canonical layout** (§3): 0 Header → 1 Imports → 2 Tag Registry → 3 Parameters → 4 init → 5 Materials → 6 Sections → 7 Nodes → 8 BCs → 9 Elements → 10 ODB → 11 Loading → 12 Analysis → 13 Post-process → 14 Main.

**Verbatim parsing (not hardcoding)** — like the LifeDeath model: the large node/mass/fixity/element/geomTransf/fiber tables are parsed from `tcl_ref/co.tcl` via regex at runtime, so the model is an exact 1:1 replay rather than a transcription that could drift. The 44 nodes, 44 masses, 8 fixities, 83 geomTransf, 83 elements, and all eleLoad lines are parsed.

**Units (§3a)** — source is already N-mm-MPa (coords in mm, E in MPa, forces in N); values imported via `from units import *` and tagged with `*mm`, `*MPa`, `*N`.

**Path depth** — `standards/` is `parents[3]` (this model nests under `models/Dino/<analysis-name>/`), with `parents[2]` fallback — same as LifeDeath/LayeredShell (§12as-5).

**Materials** — keep the live ones verbatim:
- `Steel01 1` (fy=300, E=206000, b=0.01) and `Concrete02 2` (7-arg: fpc=−20, epsc0=−0.002, fpcu=−5, epsU=−0.0033, lambda=0.1, ft=2.2, Ets=1100).
- The 6 `Elastic` shear/torsion materials for the Aggregator (201/301/401, 202/302/402) — kept.
- `Elastic 3` (1.999e5) is referenced by **no** fiber/element → **dead, omitted** (§12ap-6).

**Sections — verbatim fiber replay** (like LowCycle, §12aq): both Fiber sections (1 = NC500×500: 25 concrete fibers @ 1e4 + 16 steel @ 314; 2 = NB300×600: 25 concrete @ 7200 + 6 steel @ 314) are parsed from the source `fiber` commands and re-emitted via `ops.fiber()`, preserving exact areas/centroids. Then rebuild the two `section Aggregator` (1001, 1002) wrapping them with rigid shear+torsion. `nonlinearBeamColumn` uses the Aggregator tags (1001/1002), exactly as the source.

**Elements** — `nonlinearBeamColumn` retains its native signature `(tag, i, j, nIP=3, secTag, transfTag)` — **NOT** converted to dispBeamColumn (§12l).

**ODB (§3d, §12v)** — `CreateODB(save_nodal_resp=True, save_frame_resp=False, model_update=False)`. Frame-response saving is off because `nonlinearBeamColumn` internal sections have no user-visible tags (§12v) — consistent with every other Dino frame model.

**Loading** — two phases mirroring the source:
- Phase 1 (pattern 1, before `loadConst`): node-35 `+3e5` UZ point load + the 66 `eleLoad -beamUniform 0 -6.375 0` lines (duplicates preserved verbatim so results match).
- Phase 2 (pattern 2, **after** `loadConst`, §12z-1): node-35 `−3e5` UZ.

**Analysis** — **both phases are `LoadControl`**, so per the §3c permitted exception (SmartAnalyze forces DisplacementControl) each phase is a **manual `ops.analyze()` loop** with the source's exact solver (Plain constraints/numberer, BandGeneral, EnergyIncr 1e-6/200, Newton; LoadControl 0.1 then 0.01) — this is how LifeDeath matched its reference to 0.000%. `fetch_response_step()` inside both loops; 110 total recorded steps.

**Visualisation (§3b)** — `vis_nodes`, `vis_model`, `vis_loads`, `vis_pre_analysis`, then `vis_defo`/`vis_slider`/`vis_anim` (UZ, since the pushdown is vertical) in post-process = 7 HTMLs.

**Post-process / validation** — flush ODB; read node-35 history (UX,UY,UZ) back from the ODB; load `tcl_ref/node35.out` (110 rows, cols = time/UX/UY/UZ); plot sim-vs-reference (matplotlib, `pushdown_compare.png`) and dump `node35_disp_history.csv`; print per-dof peak + RMS diff.

### Catalogue entry (`Dino_PseudoCollapse`)
19 fields, matching the exact schema/formatting of the existing `Dino` entries (string values, `num_models`="1", `NA` sentinels, verification results + §-citations embedded in `Notes`). Run-command will use the working `uv run python "models/Dino/Analysis of a Pseudo-Collapse Test on a Frame Structure/model.py"`.

### Verification (will run)
Execute the model with `uv run python "models/Dino/Analysis of a Pseudo-Collapse Test on a Frame Structure/model.py"`. Success criteria: 110/110 steps converge; node-35 UX/UY/UZ history matches `node35.out` closely (for a verbatim-fiber + verbatim-solver force-controlled model, expect near-exact match like LifeDeath's 0.000%). The actual numbers go into the catalogue `Notes`. If convergence differs materially I'll report it honestly rather than claim success.

### Out of scope / notes
- `EXAM29.tcl` is byte-identical to `co.tcl` — left as-is (reference).
- The auto-created `.venv/` is gitignored; no source files outside this model folder + the root catalogue will be touched (per AGENT.md §1).
- I will not commit/push (you haven't asked).