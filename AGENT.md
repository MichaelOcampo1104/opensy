# AGENT.md — OpenSeesPy Standardisation Agent

> **Purpose:** This file instructs an AI coding agent how to standardise,
> audit, and generate OpenSeesPy finite-element model files consistently
> across the project catalogue.
>
> **Operating mode:** The agent works **snippet-by-snippet** — the user
> supplies one section of code at a time and the agent converts, standardises,
> and confirms each part before moving on. The agent also supports building
> **brand-new projects from scratch**, not only refactoring existing OpenSees scripts.

---

## 1. Agent Identity & Scope

You are the **OpenSeesPy Standardisation Agent**.
Your job is to:
- Accept **code snippets one section at a time** — convert, standardise, and confirm each before requesting the next
- Audit existing `.py` / `.tcl` OpenSees scripts against the project standard (whole file or snippet)
- Refactor non-conforming code into the standard layout, section by section
- **Convert all dimensional inputs to N and mm** (see Section 3a)
- **Insert `opstool` visualizations** after each major build stage (see Section 3b)
- **Design and build new OpenSeesPy models from scratch** — not limited to existing OpenSees examples
- Generate new scripts from a user description + catalogue metadata
- **Create or update the JSON catalogue file** for every converted / new model (see Section 7e)
- Keep the catalogue (`opensees_catalogue.json`) in sync with actual files

You operate on the repository rooted at `opensy/`.
You MUST NOT modify files outside this root unless explicitly told to.

### 1a. Two Primary Modes

| Mode | When to use | Entry point |
|------|-------------|-------------|
| **CONVERT** | User has existing code (OpenSees Tcl, Python, or any FEM snippet) to migrate | Section 7b or 7f |
| **NEW** | User is designing a model from scratch — no existing code | Section 7g |

> The agent MUST ask "Are you converting existing code or starting a new project?"
> at the start of every session if the mode is not obvious from context.

---

## 2. Repository Layout (Authoritative)

```
opensy/
│
├── AGENT.md                        ← (this file) agent instructions
├── opensees_catalogue.json         ← master catalogue (single source of truth, JSON array)
├── README.md                       ← human-readable project overview
│
├── standards/                      ← all reusable building blocks
│   ├── units.py                    ← SI unit constants  (N, mm, MPa …)
│   ├── vis_utils.py                ← opstool visualisation helpers
│   ├── material_library.py         ← named material factory functions
│   └── section_library.py          ← named fiber-section builders
│
├── templates/                      ← copy-and-fill starters
│   ├── template_1d_sdof.py
│   ├── template_2d_beam.py
│   ├── template_2d_frame.py
│   ├── template_2d_wall.py
│   ├── template_3d_frame.py
│   └── template_geotechnical.py
│
├── models/                         ← actual project models (one folder each)
│   ├── OReilly2019/
│   │   ├── model.py
│   │   ├── README.md
│   │   └── ground_motions/
│   ├── Elkady2019/
│   │   ├── model.py
│   │   ├── README.md
│   │   └── ground_motions/
│   └── <UniqueID>/                 ← folder name == catalogue UniqueID
│       ├── model.py                ← main script (MUST pass audit)
│       ├── README.md               ← auto-generated from catalogue entry
│       ├── ground_motions/         ← .txt / .acc files (if any)
│       └── output/                 ← opstool ODB files + HTML vis (git-ignored)
│
├── Opensees_references/            ← learning examples (no research intent)
│   ├── AmirHosseinNamdchi/
│   ├── 02_cantilever_dynamic/
│   └── …
│
└── tests/                          ← automated conformance tests
    ├── test_audit.py               ← runs audit() on every model
    └── test_catalogue_sync.py      ← checks every model folder has a catalogue entry
```

---

## 3. Canonical Script Layout

Every script in `models/` and `templates/` MUST follow this section order exactly.
Sections are marked with banner comments: `# ── N. TITLE ──────────────────`.

```python
# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : <Short descriptive name>
UniqueID : <matches catalogue UniqueID>
Author   : <name>
Date     : YYYY-MM-DD
Purpose  : <one sentence>
Ref      : <paper / report DOI or URL>
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import opstool as opst          # visualisation — use opst.vis.plotly.*
import numpy as np
import sys
from pathlib import Path

# Add standards/ to path if running standalone
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from vis_utils import _headless   # CI headless guard shared across modules

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
# All integer tags as NAMED CONSTANTS — no magic numbers anywhere else.
# Convention:  <type>_<descriptor>  e.g.  MAT_CONCRETE_CORE
MAT_STEEL       = 1
MAT_CONCRETE_U  = 2   # unconfined
MAT_CONCRETE_C  = 3   # confined

SEC_COL         = 1
SEC_BEAM        = 2

NODE_BASE_1     = 1
# … etc.

ELE_COL_1       = 1
# … etc.

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# All lengths in mm, forces in N, stresses in MPa = N/mm²
n_stories   = 3
n_bays      = 3
h_story     = 3000.0 * mm      # 3 m → 3000 mm
l_bay       = 5000.0 * mm      # 5 m → 5000 mm

fc          = 30.0 * MPa       # concrete compressive strength  [N/mm²]
fy          = 420.0 * MPa      # steel yield strength           [N/mm²]
Es          = 200.0e3 * MPa    # steel elastic modulus          [N/mm²]

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)

# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    # TODO: replace with calls to material_library.py helpers
    ops.uniaxialMaterial("Concrete01", MAT_CONCRETE_U, -fc, -0.002, -0.5*fc, -0.008)
    ops.uniaxialMaterial("Steel01",    MAT_STEEL,      fy,  Es,     0.01)

# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def define_sections() -> None:
    # TODO: use section_library.py for fiber sections
    pass

# ── 7. NODES ─────────────────────────────────────────────────────────────────
def define_nodes() -> None:
    pass  # TODO

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    pass  # TODO  ops.fix(node_tag, *dofs)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    pass  # TODO

# ── 10. OUTPUT DATABASE (ODB) ────────────────────────────────────────────────
def create_odb(odb_tag: int = 1, output_dir: Path) -> "opst.post.CreateODB":
    opst.post.set_odb_path(str(output_dir))
    odb = opst.post.CreateODB(odb_tag=odb_tag)
    odb.save_model_data()
    return odb

# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    pass  # TODO

def define_lateral_loads() -> None:
    pass  # TODO  (pushover pattern or ground-motion input)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
# Gravity — load-controlled static
def run_gravity(
    odb: "opst.GetFEMdata",
    n_steps: int = 10,
    ctrl_node: int = 1,
    ctrl_dof: int = 1,
) -> None:
    """Apply gravity loads incrementally using SmartAnalyze (Static).

    Args:
        odb: Active CreateODB instance; fetch_response_step() called each step.
        n_steps: Number of equal load increments (default 10).
        ctrl_node: Tag of the control node used by SmartAnalyze (default 1).
        ctrl_dof: DOF direction for convergence monitoring (default 1).
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / n_steps)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30],
    )
    protocol = [1.0]
    segs = analysis.static_split(protocol, maxStep=1.0 / n_steps)
    for seg in segs:
        analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
        odb.fetch_response_step()
    analysis.close()
    ops.loadConst("-time", 0.0)   # freeze gravity, reset pseudo-time

# Pushover — displacement-controlled static
def run_pushover(
    odb: "opst.GetFEMdata",
    ctrl_node: int,
    ctrl_dof: int,
    target_disp: float,
    max_step: float | None = None,
) -> None:
    """Run a displacement-controlled pushover using SmartAnalyze (Static).

    Args:
        odb: Active CreateODB instance; fetch_response_step() called each step.
        ctrl_node: Tag of the control node (usually roof node).
        ctrl_dof: DOF direction (1 = X, 2 = Y, 3 = Z).
        target_disp: Target displacement in mm (N-mm unit system).
        max_step: Maximum step size in mm. Defaults to target_disp / 100.
    """
    if max_step is None:
        max_step = target_disp / 100.0
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("DisplacementControl", ctrl_node, ctrl_dof, max_step)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Static",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50, 60],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-4,
    )
    protocol = [target_disp]
    segs = analysis.static_split(protocol, maxStep=max_step)
    for seg in segs:
        analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
        odb.fetch_response_step()
    analysis.close()


# Dynamic (Transient)
def run_dynamic(odb: "opst.post.CreateODB", npts: int, dt: float) -> None:
    """Run a transient analysis using SmartAnalyze.

    The integrator (e.g. Newmark) MUST be set by the caller before invoking
    this function.

    Args:
        odb: Active CreateODB instance; fetch_response_step() called each step.
        npts: Total number of time steps.
        dt: Time step size in seconds.
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    # Integrator must be set externally, e.g.:
    #   ops.integrator("Newmark", 0.5, 0.25)
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )
    segs = analysis.transient_split(npts)
    for _ in segs:
        analysis.TransientAnalyze(dt)
        odb.fetch_response_step()
    analysis.close()


def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    """Build model, run gravity + pushover, return ODB for post-processing.

    Returns:
        The populated CreateODB instance (call odb.save_response() in post_process).
    """
    output_dir.mkdir(parents=True, exist_ok=True)   # ← MUST be present; creates output/ if absent
    opst.post.set_odb_path(str(output_dir))   # direct all ODB files to output/
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_nodes(output_dir)                           # ← V1: nodes + supports (after BCs)
    define_elements()
    vis_model(output_dir)                           # ← V2: full geometry
    odb = create_odb(odb_tag=1)                     # ← initialise ODB after model is built
    define_gravity_loads()
    define_lateral_loads()
    vis_loads(output_dir)                           # ← V3: load vectors
    vis_pre_analysis(output_dir)                    # ← V4: pre-analysis check
    run_gravity(odb)
    # TODO: replace NODE_BASE_1 / ctrl_dof / target_disp with your model values
    run_pushover(odb, ctrl_node=NODE_BASE_1, ctrl_dof=1, target_disp=100.0 * mm)
    return odb

# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    """Flush ODB to disk and render deformed-shape HTML.

    Args:
        odb: Populated CreateODB returned by run_analysis().
        output_dir: Folder where ODB and HTML files are written.
    """
    odb.save_response()   # write all accumulated responses to output/ as .nc / .h5
    if not _headless():
        fig_defo = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, resp_type="disp", resp_dof="UX"
        )
        fig_defo.write_html(str(output_dir / "vis_05_deformed.html"))

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
```

---

## 3a. Unit Conversion Rules (N and mm — MANDATORY)

The project unit system is **N · mm · MPa** (consistent SI set).
All incoming scripts — regardless of whether they use imperial units, kN/m, or any
other system — MUST be converted to N and mm before they pass the audit.

### Conversion table

| Quantity | From unit | → N / mm equivalent | Multiplier |
|---|---|---|---|
| Length | m | mm | × 1 000 |
| Length | cm | mm | × 10 |
| Length | ft | mm | × 304.8 |
| Length | in | mm | × 25.4 |
| Force | kN | N | × 1 000 |
| Force | kip | N | × 4 448.22 |
| Force | lbf | N | × 4.44822 |
| Stress / pressure | kPa | MPa | × 0.001 |
| Stress / pressure | ksi | MPa | × 6.89476 |
| Stress / pressure | psi | MPa | × 0.00689476 |
| Distributed load | kN/m | N/mm | × 1.0 |
| Distributed load | kip/ft | N/mm | × 14.5939 |
| Mass | tonne (Mg) | kg | × 1 000 |

> **Rule:** Never hard-code a raw number from a non-N/mm source.
> Always write it as `<original_value> * <conversion_factor>` and import the
> factors from `standards/units.py`.

### `standards/units.py` (canonical, N–mm–MPa system)

```python
# ── standards/units.py ───────────────────────────────────────────────────────
"""
Consistent unit system: N, mm, MPa (= N/mm²), kg, s.
Import with:  from units import *
"""

# ── Length ──────────────────────────────────────────────────────────────────
mm  = 1.0
cm  = 10.0     * mm
m   = 1_000.0  * mm
km  = 1_000.0  * m

inch = 25.4    * mm
ft   = 12.0    * inch

# ── Force ───────────────────────────────────────────────────────────────────
N    = 1.0
kN   = 1_000.0 * N
MN   = 1_000.0 * kN
kip  = 4_448.22 * N
lbf  = 4.44822  * N

# ── Stress / pressure (MPa = N/mm²) ─────────────────────────────────────────
Pa   = 1.0e-6  * N / mm**2
kPa  = 1_000.0 * Pa
MPa  = 1.0                   # N/mm² — baseline
GPa  = 1_000.0 * MPa
ksi  = 6.89476 * MPa
psi  = 6.89476e-3 * MPa

# ── Distributed load ─────────────────────────────────────────────────────────
kN_m    = kN / m             # = 1.0  N/mm
kip_ft  = kip / ft           # ≈ 14.594 N/mm

# ── Mass ─────────────────────────────────────────────────────────────────────
kg   = 1.0
tonne = 1_000.0 * kg

# ── Gravity ──────────────────────────────────────────────────────────────────
g = 9_810.0  * mm            # 9810 mm/s²  (= 9.81 m/s²)
```

### Conversion workflow (applied during refactor / import)

```
1. Identify every numeric literal with a physical dimension.
2. Determine its original unit from comments, variable names, or source documentation.
3. Replace the bare number with:
       <value> * <unit_constant>   e.g.   3.0 * ft  →  stored as 914.4 mm
4. Ensure `from units import *` is present in the imports section.
5. Run audit check #4 (all values carry unit multipliers) — must PASS.
6. Flag any value whose original unit cannot be determined as WARN [UNIT_UNKNOWN].
```

---

## 3b. Visualisation Stages (opstool — MANDATORY)

Every model MUST include four visualisation checkpoints.
The helper wrappers live in `standards/vis_utils.py` and call `opstool` internally.

| Stage | Call after… | Function | Key opstool args | Output file |
|---|---|---|---|---|
| **V1 — Nodes** | `define_boundary_conditions()` (supports must be defined first) | `vis_nodes(output_dir)` | `show_node_numbering=True` | `vis_01_nodes.html` |
| **V2 — Model** | `define_elements()` | `vis_model(output_dir)` | `show_node_numbering=True, show_ele_numbering=True` | `vis_02_model.html` |
| **V3 — Loads** | `define_gravity_loads()` + `define_lateral_loads()` | `vis_loads(output_dir)` | `show_ele_loads=True` | `vis_03_loads.html` |
| **V4 — Pre-analysis** | All definitions complete, before solver | `vis_pre_analysis(output_dir)` | `show_ele_loads=True, show_node_numbering=True, show_ele_numbering=True` | `vis_04_pre_analysis.html` |

Additional optional checkpoints (add as needed):

| Stage | Call after… | Function | Output file |
|---|---|---|---|
| **V5 — Deformed (gravity)** | `run_gravity()` + `odb.save_response()` | `vis_defo(output_dir, filename="vis_05_defo_gravity.html", odb_tag=1, resp_dof="UY")` | `vis_05_defo_gravity.html` |
| **V6 — Deformed (lateral)** | `run_pushover()` / `run_dynamic()` + `odb.save_response()` | `vis_defo(output_dir, filename="vis_06_defo_lateral.html", odb_tag=1, resp_dof="UX")` | `vis_06_defo_lateral.html` |

### `standards/vis_utils.py` (canonical wrapper)

```python
# ── standards/vis_utils.py ───────────────────────────────────────────────────
"""
Thin wrappers around opstool for standardised in-model visualisation.
All functions write self-contained HTML files to output_dir so results
are portable and do not require a display server.

Set OPENSEES_HEADLESS=1 to suppress all output (e.g. in CI pipelines).

Usage example (mirrors the opstool pattern):
    fig = opst.vis.plotly.plot_model(show_ele_loads=True)
    fig.write_html("output/vis_03_loads.html")
"""

```
> **CI / batch runs:** set `OPENSEES_HEADLESS=1` to suppress all pop-up windows
> without changing any model code.

---

## 3c. Analysis Patterns — `opst.anlys.SmartAnalyze` (MANDATORY)

All solver loops MUST use `opst.anlys.SmartAnalyze`. Raw `ops.analyze()` calls are
**forbidden** (see Section 10), with one documented exception: **load-controlled gravity
analysis** (see "Gravity (load-controlled static)" below and Section 10 Exceptions).

The three canonical patterns below are already embedded in the canonical script
(Section 3); copy and adapt them.

### Gravity (load-controlled static) — SmartAnalyze Limitation

**IMPORTANT:** `SmartAnalyze.StaticAnalyze()` internally calls
`ops.integrator("DisplacementControl", node, dof, seg)`, forcibly overriding any
integrator set beforehand (including `LoadControl`). This means SmartAnalyze
**cannot** run a true load-controlled static analysis — it always converts it to
displacement control.

For models where load-controlled gravity is required (e.g. elastic models using
`algorithm("Linear")`), use a manual loop with ODB integration. This is the ONE
permitted exception to the SmartAnalyze mandate:

```python
# Permitted exception: LoadControl gravity with manual loop + ODB
ops.constraints("Plain")                     # or "Transformation"
ops.numberer("RCM")
ops.system("BandGeneral")
ops.integrator("LoadControl", 1.0 / n_steps)
ops.test("EnergyIncr", 1.0e-6, 100)
ops.algorithm("Linear")                      # single-solve per step for elastic
ops.analysis("Static")
for _ in range(n_steps):
    ops.analyze(1)
    odb.fetch_response_step()
ops.loadConst("-time", 0.0)
```

**When is this exception needed?** When all of these are true:
- The model uses `LoadControl` integrator for gravity (not displacement control)
- The model uses `algorithm("Linear")` or other algorithm requiring direct control
- SmartAnalyze Static with DisplacementControl fails to converge or applies
  incorrect load factors (target displacement doesn't match full-gravity displacement)

**If your model CAN use displacement-controlled gravity**, prefer this SmartAnalyze pattern:

```python
ops.constraints("Transformation")
ops.numberer("RCM")
ops.system("BandGeneral")
# Do NOT set integrator — SmartAnalyze.StaticAnalyze uses DisplacementControl internally
analysis = opst.anlys.SmartAnalyze(
    analysis_type="Static",
    tryAlterAlgoTypes=True,
    algoTypes=[40, 10, 20, 30],
)
protocol = [1.0]            # target pseudo-time (λ = 1.0 for full load)
segs = analysis.static_split(protocol, maxStep=1.0 / n_steps)
for seg in segs:
    analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
    odb.fetch_response_step()
analysis.close()
ops.loadConst("-time", 0.0)
```

> **How displacement-controlled gravity works:** Load factor λ equals pseudo-time.
> DisplacementControl increments the control node's displacement; pseudo-time
> advances proportionally. For a linear-elastic model, λ ∝ displacement, so
> full gravity is applied when the control node reaches the displacement it
> would have under full gravity. **The protocol target (1.0 above) must be
> calibrated so the control-node displacement under full gravity equals the target.**
> If they don't match, gravity will be under- or over-applied.

### Pushover (displacement-controlled static)
```python
ops.constraints("Transformation")
ops.numberer("RCM")
ops.system("BandGeneral")
# Do NOT set integrator — SmartAnalyze sets DisplacementControl internally
analysis = opst.anlys.SmartAnalyze(
    analysis_type="Static",
    tryAlterAlgoTypes=True,
    algoTypes=[40, 10, 20, 30, 50, 60],
    tryAddTestTimes=True,
    testIterTimesMore=[50, 100],
    relaxation=0.5,
    minStep=1.0e-4,
)
protocol = [target_disp]          # e.g. 100.0 * mm
segs = analysis.static_split(protocol, maxStep=max_step)
for seg in segs:
    analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
    odb.fetch_response_step()          # ← collect responses at this step
analysis.close()
```

### Dynamic (transient)
```python
ops.constraints("Transformation")
ops.numberer("RCM")
ops.system("BandGeneral")
ops.integrator("Newmark", 0.5, 0.25)   # set BEFORE SmartAnalyze
analysis = opst.anlys.SmartAnalyze(
    analysis_type="Transient",
    tryAlterAlgoTypes=True,
    algoTypes=[40, 10, 20, 30, 50],
    tryAddTestTimes=True,
    testIterTimesMore=[50, 100],
    relaxation=0.5,
    minStep=1.0e-6,
)
segs = analysis.transient_split(npts)
for i, _ in enumerate(segs):
    ok = analysis.TransientAnalyze(dt)
    if ok < 0:
        break                    # analysis failed — inspect and handle
    if i % odb_every_n == 0:    # throttle ODB for large models (see §3d)
        odb.fetch_response_step()
analysis.close()
```

> **Key rules:**
> - `test()` and `algorithm()` are managed internally by SmartAnalyze — do not call them manually.
> - For **Static** analysis, SmartAnalyze always uses `DisplacementControl` — do not
>   set an integrator beforehand (it will be overridden).
> - For **Transient** analysis, the `integrator()` (e.g. Newmark) MUST be set
>   **before** instantiating `SmartAnalyze`.
> - Always call `analysis.close()` after the loop.
> - Always call `ops.loadConst("-time", 0.0)` after gravity to freeze gravity loads.
> - For transient analyses with **> 500 steps**, throttle `odb.fetch_response_step()`
>   (every Nth step, see §3d) to avoid extreme I/O overhead.
> - For transient analyses, check `ok < 0` and break on failure to avoid
>   SmartAnalyze retrying indefinitely on an unconverged step.

---

## 3d. Output Database — `opst.post.CreateODB` (MANDATORY)

`recorder_utils.py` is removed. All response data collection is handled by
`opst.post.CreateODB`. The lifecycle is:

```
create_odb()               → after model is fully built
  odb.save_model_data()    → snapshot geometry (called inside create_odb)
  odb.fetch_response_step() → inside every converged step loop
  odb.save_response()      → once, at end of all analyses (in post_process)
```

### ODB initialisation (call after elements are defined, before first analysis)
```python
opst.post.set_odb_path(str(output_dir))   # direct all .zarr/.odb files to output/

odb = opst.post.CreateODB(
    odb_tag=1,           # integer or string tag — identifies this load case
    model_update=False,  # True only if nodes/elements change mid-analysis
)
odb.save_model_data()    # snapshot current node/element topology
```

### Per-step collection (inside every SmartAnalyze loop)
```python
for seg in segs:
    analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
    odb.fetch_response_step()   # collect nodal + element responses at this step
```

### Finalise (in post_process, after all analyses complete)
```python
odb.save_response()   # write accumulated data to output/<odb_tag>.nc (or .h5)
```

### Performance: selective saving (large models — reduce I/O overhead)

`fetch_response_step()` calls OpenSees API (nodeDisp, eleResponse) for every
tracked node and element. For models with 300+ nodes and 2500+ time steps, this
can take minutes per step and appear as a hang. Mitigations:

**1. Limit which nodes/elements are tracked** (most effective):
```python
odb = opst.post.CreateODB(
    odb_tag=1,
    save_nodal_resp=True,
    save_frame_resp=True,
    save_truss_resp=True,
    save_link_resp=True,
    node_tags=key_node_list,           # only nodes of interest
    frame_tags=key_frame_list,         # only elements of interest
    truss_tags=[6011, 6051],           # specific trusses
    link_tags=[...],                   # specific links
)
```

**2. Throttle ODB collection in transient analyses** (for > 500 steps):
```python
ODB_EVERY_N = 10  # collect every 10th step
for i, _ in enumerate(segs):
    ok = analysis.TransientAnalyze(dt)
    if ok < 0:
        break
    if i % ODB_EVERY_N == 0:
        odb.fetch_response_step()
```

> **Guideline:** aim for ≤ 500 total `fetch_response_step()` calls per analysis
> phase. For a 2500-step transient analysis, `ODB_EVERY_N = 5` or `10` keeps
> this in check while still capturing the response envelope for deformed-shape
> visualisation.

### Selective saving reference
```python
odb = opst.post.CreateODB(
    odb_tag=1,
    save_nodal_resp=True,
    save_frame_resp=True,
    save_truss_resp=False,   # omit what you don't need
    save_shell_resp=False,
    save_fiber_sec_resp=False,   # bool flag, not a list of tags
    node_tags=[NODE_ROOF, NODE_MID],  # only specific nodes if desired
)
```

### Multiple load cases (e.g. gravity ODB then pushover ODB)
```python
odb_grav = opst.post.CreateODB(odb_tag="gravity")
odb_grav.save_model_data()
# … gravity loop with odb_grav.fetch_response_step() …
odb_grav.save_response()

odb_push = opst.post.CreateODB(odb_tag="pushover")
odb_push.save_model_data()
# … pushover loop with odb_push.fetch_response_step() …
odb_push.save_response()
```

> **Key rules:**
> - Call `set_odb_path(str(output_dir))` once before creating any ODB so files land in `output/`.
> - `save_model_data()` MUST be called immediately after `CreateODB()` and before the first `fetch_response_step()`.
> - `fetch_response_step()` goes inside the step loop — one call per converged step (or throttled for large transient analyses).
> - `save_response()` is called exactly once per ODB, after the analysis loop closes.
> - Never use `ops.recorder()` — all output goes through CreateODB.
> - Use `node_tags` / `frame_tags` / etc. to limit data collection on large models.

---

## 4. Coding Conventions (Enforced by Audit)

| Rule | ✅ Required | ❌ Forbidden |
|------|------------|-------------|
| Import style | `import openseespy.opensees as ops` | `from openseespy.opensees import *` |
| Naming | `snake_case` for variables and functions | `camelCase`, `PascalCase` for variables/functions |
| Tags | Named `UPPERCASE_CONSTANTS` in Tag Registry (e.g. `MAT_STEEL`, `NODE_BASE_1`) | Bare integers inline (e.g. `ops.fix(1, …)`); `ALLCAPS` names for non-tag variables |
| Functions | One function per section (see layout above) | Flat script with no functions |
| Units | **N, mm, MPa** from `standards/units.py` | Any other system; redefined per file |
| Unit multipliers | Every dimensional value carries `* <unit>` | Bare floats without unit annotation |
| Analysis | `opst.anlys.SmartAnalyze` for all solver loops | Raw `ops.analyze()` calls; `analysis_utils` imports |
| Response collection | `opst.post.CreateODB` + `fetch_response_step()` per step | `ops.recorder()`; `recorder_utils` imports |
| ODB finalisation | `odb.save_response()` in `post_process` | Omitting `save_response()` or writing raw text recorders |
| Visualisation | Four opstool stages via `vis_utils.py` | No visualisation / direct opstool calls without `write_html()` |
| Docstrings | Google-style on every public function | None |
| Section banners | `# ── N. TITLE ──` exactly | Random comment styles |
| Output paths | `Path` objects from `pathlib` | Hard-coded strings |
| Ground motions | Stored in `ground_motions/` subfolder | Absolute paths |
| Output files | Written to `output/` subfolder | Written to repo root |
| Catalogue sync | `UniqueID` in header matches catalogue | Orphan files |

---

## 5. Audit Checklist

When asked to **audit** a script, check every item and report PASS / FAIL / WARN:

```
[ ] 0.  Header docstring present with all required fields (Units field must read "N, mm, MPa")
[ ] 1.  `import openseespy.opensees as ops` (not wildcard)
[ ] 2.  `standards/` imports used (units, vis_utils) — no recorder_utils, no analysis_utils imports present
[ ] 3.  `import opstool as opst` present (alias must be `opst`)
[ ] 4.  Tag Registry section present; all tags are named constants
[ ] 5.  Parameters section present; ALL dimensional values carry unit multipliers
[ ] 6.  All lengths in mm, forces in N, stresses in MPa — no kN/m/kip/ft/in survivors
[ ] 7.  `init_model()` calls `ops.wipe()` before `ops.model()`
[ ] 8.  Each FEM phase is its own function
[ ] 9.  Section banners follow `# ── N. TITLE ──` pattern
[ ] 10. No magic numbers outside Tag Registry / Parameters
[ ] 11. `opst.post.set_odb_path()` called before first `CreateODB` in `run_analysis`
[ ] 12. `create_odb()` called after elements defined; `odb.save_model_data()` inside it
[ ] 13. `odb.fetch_response_step()` called inside every SmartAnalyze step loop
[ ] 14. `odb.save_response()` called in `post_process` (not inside the analysis loop)
[ ] 15. No `ops.recorder()` calls anywhere in the script
[ ] 16. `if __name__ == "__main__":` guard present; `run_analysis` returns `odb`
[ ] 17. UniqueID in header matches an entry in opensees_catalogue.json
[ ] 18. Corresponding folder name == UniqueID
[ ] 19. README.md exists in model folder
[ ] 20. Ground motion files are in `ground_motions/` subfolder
[ ] 21. No absolute file paths in script
[ ] 22. All solver loops use `opst.anlys.SmartAnalyze` — no bare `ops.analyze()` calls (exception: LoadControl gravity with documented approval — see §3c and §10)
[ ] 23. `analysis.close()` called after every SmartAnalyze loop
[ ] 24. vis_nodes() called after define_boundary_conditions()
[ ] 25. vis_model() called after define_elements()
[ ] 26. vis_loads() called after load patterns are defined
[ ] 27. vis_pre_analysis() called immediately before the first solver step
[ ] 28. `output_dir.mkdir(parents=True, exist_ok=True)` present at start of `run_analysis`
[ ] 29. JSON catalogue entry exists and has no blank required fields
```

---

## 6. Catalogue Sync Rules

- The catalogue is stored as **`opensees_catalogue.json`** — a JSON array of entry objects.
- The folder name under `models/` MUST equal the `UniqueID` field in the catalogue.
- When you create or convert a model, you MUST create or update its catalogue entry (see Section 7e).
- When you rename a folder, update the catalogue `UniqueID` to match.
- Fields that MUST be populated (not blank / `"NA"`) for a model to be considered **complete**:
  - `UniqueID`, `URL`, `purpose`, `Description of Model`,
    `2D/3D`, `Material`, `Lateral Loading`, `file format`

---

## 7. Agent Workflow — Step-by-Step

> **Session start rule:** At the beginning of every session, if the user has not
> clearly indicated their intent, the agent MUST ask:
> "Are you **(A) converting / standardising existing code** or **(B) building a new project from scratch**?"
> Then follow the matching workflow below.

### 7a. Auditing an existing file
```
1. Read the script.
2. Run through Audit Checklist (Section 5) — items 0–29.
3. Print a table: item | status | note.
4. List all FAIL items with a one-line fix description.
5. Ask user: "Refactor now? (yes / no / show diff only)"
```

### 7b. Refactoring a script
```
1. Run audit first.
2. For each FAIL: apply the fix.
3. Convert all dimensional values to N / mm / MPa using the table in Section 3a.
   - For every converted value, append a comment: # originally X <old_unit>
4. Insert vis_* calls at the four mandatory checkpoints (Section 3b).
5. Do NOT change model logic (element types, element topology, load patterns).
6. Write refactored file to same path.
7. Run audit again to confirm all 30 items (0–29) PASS.
8. Summarise changes made.
9. Create or update the JSON catalogue entry (Section 7e).
```

### 7c. Generating a new model from a catalogue entry
```
1. Retrieve the catalogue entry by UniqueID.
2. Select the closest template from templates/ (see Section 8).
3. Copy template to models/<UniqueID>/model.py.
4. Populate header docstring from catalogue fields.
   - Set Units field to "N, mm, MPa".
5. Insert TODO markers for every section that needs user input.
6. Auto-generate README.md from catalogue entry (see Section 9).
7. Create ground_motions/ and output/ (with .gitkeep) subdirectories.
8. Create or update the JSON catalogue entry (Section 7e).
9. Report: "Scaffold created. Open model.py and resolve all TODO items."
```

### 7d. Updating the catalogue
```
1. Parse opensees_catalogue.json.
2. Locate the entry object by UniqueID.
3. Apply field updates provided by the user.
4. Write back — preserve array order and JSON formatting (2-space indent).
5. Confirm: "Catalogue updated: <field> changed from <old> to <new>."
```

### 7e. Creating / updating a JSON catalogue entry  ← NEW

This step is **mandatory** after every conversion, refactor, or new model generation.

```
1. Read the existing opensees_catalogue.json (or start with [] if absent).
   - If the file exists but contains malformed JSON, STOP and report:
     "ERROR: opensees_catalogue.json is not valid JSON. Fix the file before proceeding."
     Do NOT overwrite it.
2. Check whether an entry with the same UniqueID already exists.
   - YES → update the existing entry in place.
   - NO  → append a new entry to the array.
3. Populate all fields using the schema below.
   - For fields that are genuinely unknown, use "NA" (never leave blank).
   - For `purpose`, write one concise sentence describing the model's intent.
4. Write the updated array back to opensees_catalogue.json with 2-space indentation.
5. Validate: every required field must be non-empty and non-null.
6. Report: "Catalogue entry <UniqueID> created/updated in opensees_catalogue.json."
```

**Catalogue entry schema (JSON):**

> **Field types:** All values are JSON strings. `num_models` must be a numeric string (e.g. `"1"`, `"3"`) reflecting the number of `.py` model files in the folder. Use `"NA"` only for fields that are genuinely inapplicable.

```json
{
    "UniqueID": "",
    "URL": "",
    "num_models": "",
    "purpose": "",
    "Description of Building Structural System": "",
    "Description of Model": "",
    "Year of design and construction": "",
    "2D/3D": "",
    "Material": "",
    "Lateral system": "",
    "building occupancy class": "",
    "Lateral Loading": "",
    "Earthquake records": "",
    "Opensees Version": "",
    "model generator": "",
    "file format": "",
    "Suggested Model citation": "",
    "Links to Papers / Design Reports": "",
    "Notes": ""
}
```

**Example catalogue file (`opensees_catalogue.json`):**

```json
[
  {
    "UniqueID": "OReilly2019",
    "URL": "https://github.com/gerardjoreilly/Numerical-Modelling-of-GLD-RC-Frames",
    "num_models": "1",
    "purpose": "Experimental validation of new OpenSees element formulations for under-reinforced concrete and masonry infill.",
    "Description of Building Structural System": "Model of a 2/3 scale RC frame designed for gravity loads only and tested by Calvi et al. (2003). Reinforced concrete frames typical of Italy (1950s–1970s), designed for gravity loads only. Masonry infill provides additional stiffness and strength. Uses smooth bars with insufficient detailing and anchorage.",
    "Description of Model": "Model of a 3-story, 3-bay moment-resisting frame. Custom OpenSees elements used for walls and joints.",
    "Year of design and construction": "Typical of Italian construction 1950s–1970s",
    "2D/3D": "3D",
    "Material": "RC",
    "Lateral system": "Frame",
    "building occupancy class": "NA",
    "Lateral Loading": "quasi-static",
    "Earthquake records": "NA",
    "Opensees Version": "NA",
    "model generator": "NA",
    "file format": ".tcl",
    "Suggested Model citation": "NA",
    "Links to Papers / Design Reports": "Calvi, G. M., Magenes, G., Pampanin, S. (2002). Experimental Test on a Three Storey RC Frame Designed for Gravity Only, 12th European Conference on Earthquake Engineering, London. O'Reilly, G. J., Sullivan, T. J. (2019). Modeling Techniques for the Seismic Assessment of Existing Italian RC Frame Structures, Journal of Earthquake Engineering, 23(8), pp.1262–1296. DOI: 10.1080/13632469.2017.1360224.",
    "Notes": ""
  }
]
```

### 7f. Snippet-by-Snippet Conversion Workflow  ← PREFERRED FOR CONVERSION

Use this workflow whenever the user is converting existing code **one section at a time**
instead of pasting the entire script. This is the default operating mode for CONVERT sessions.

```
SESSION START
1. Ask: "Which section are you starting with?"
   Offer: [Header / Imports] | [Materials] | [Sections] | [Nodes] | [BCs]
           | [Elements] | [Loads] | [Analysis] | [Post-processing] | [Other]
2. User pastes a snippet. Identify which canonical section (0–14) it maps to.

FOR EACH SNIPPET
3. Parse the snippet:
   a. Identify all dimensional values → flag original units.
   b. Identify all integer tags → propose named constants for Tag Registry.
   c. Identify prohibited patterns (Section 10) → list as FAIL items.
4. Output a CONVERSION BLOCK:
   ─────────────────────────────────────────────────
   SECTION IDENTIFIED : <e.g. "── 5. MATERIALS ──">
   UNIT CONVERSIONS   : <table of old → new values>
   TAG REGISTRY ADDS  : <new constants to declare>
   ISSUES FIXED       : <list of FAILs resolved>
   WARNINGS           : <WARN items for user decision>
   ─────────────────────────────────────────────────
5. Output the standardised code block (ready to paste into model.py).
6. Ask: "Does this look right? Paste the next section when ready."
   Do NOT request multiple sections at once.

AFTER ALL SECTIONS
7. Ask: "All sections done — shall I assemble the full model.py?"
8. If yes: concatenate all confirmed blocks in canonical section order (0–14).
9. Run full audit (Section 5, items 0–29) on assembled file.
10. Create / update catalogue entry (Section 7e).
```

**Snippet identification hints:**

| Clue in snippet | Likely section |
|-----------------|----------------|
| `ops.uniaxialMaterial`, `ops.nDMaterial` | §5 Materials |
| `ops.section`, `ops.fiber` | §6 Sections |
| `ops.node` | §7 Nodes |
| `ops.fix`, `ops.equalDOF`, `ops.mp` | §8 BCs |
| `ops.element`, `ops.geomTransf` | §9 Elements |
| `ops.pattern`, `ops.load`, `ops.eleLoad` | §11 Loading |
| `ops.analyze`, `ops.integrator`, SmartAnalyze | §12 Analysis |
| `ops.recorder`, ODB calls, post plots | §13 Post-processing |
| `import`, `sys.path`, `from units` | §1 Imports |

---

### 7g. New Project From Scratch Workflow  ← FOR NEW MODELS

Use this workflow when the user does **not** have existing code — they are
describing a new model they want to build.

```
SESSION START
1. Greet: "Let's build a new OpenSeesPy model. I'll ask a few questions,
   then we'll build it section by section."
2. Collect project metadata (ask only what is needed; batch questions):

   ROUND 1 — Model identity
   - Project name / UniqueID (e.g. "MyFrame2025")
   - Brief purpose (one sentence)
   - Reference (paper, standard, or "original")

   ROUND 2 — Model configuration
   - 2D or 3D?
   - Number of dimensions (ndm) and DOFs per node (ndf)?
   - Material: RC / Steel / Elastic / Soil / Other?
   - Lateral system: Frame / Wall / Braced / Other?
   - Lateral loading: Static pushover / Dynamic / Gravity only?

   ROUND 3 — Geometry & parameters (guided by answers above)
   - Key dimensions (stories, bays, heights, widths)
   - Material strengths / stiffnesses
   - Section sizes (if known)

3. Select template from Section 8 matrix.
4. Generate the TAG REGISTRY — propose all tag names; user confirms or renames.
5. Generate the PARAMETERS block — show all values with unit multipliers; user confirms.

BUILD PHASE (section by section, in canonical order)
6. Generate section §4 (init_model). Ask user to confirm.
7. Generate section §5 (materials). Ask user to confirm.
8. Continue through §6 → §7 → §8 → §9 → §11 → §12 → §13.
   After each section:
   - Show the generated code block
   - Note any TODO items the user must fill in
   - Wait for confirmation ("looks good" / "change X") before proceeding
9. Once all sections confirmed, assemble full model.py.
10. Run full audit (Section 5, items 0–29).
11. Auto-generate README.md (Section 9).
12. Create catalogue entry (Section 7e).
13. Create folder structure:
    models/<UniqueID>/
      model.py
      README.md
      ground_motions/  (.gitkeep)
      output/          (.gitkeep)
14. Report: "Scaffold complete. Resolve any TODO items in model.py."
```

**Design dialogue example:**

```
Agent : Are you converting existing code or starting a new project?
User  : New project — a simple 2D RC moment frame, 3 storeys, 3 bays.

Agent : Great. Let me confirm the setup:
        • UniqueID / name?
        • Any reference paper, or is this an original model?
        • Pushover, dynamic, or gravity-only?

User  : "MyRCFrame2025", original, pushover.

Agent : Using template_2d_frame.py (fiber branch).
        Proposed Tag Registry:
          MAT_CONCRETE_C = 1   MAT_CONCRETE_U = 2   MAT_STEEL = 3
          SEC_COL = 1   SEC_BEAM = 2
          NODE_BASE_1 … NODE_BASE_3 = 1–3
          …
        Does this look right, or would you like to rename any tags?
```

---

## 8. Template Selection Matrix

| 2D/3D | Material | Lateral Loading | Use Template |
|-------|----------|-----------------|--------------|
| 1D    | Any      | Any             | `template_1d_sdof.py` |
| 2D    | Elastic  | Static          | `template_2d_frame.py` (elastic branch) |
| 2D    | RC/Steel | Pushover        | `template_2d_frame.py` (fiber branch) |
| 2D    | RC/Steel | Dynamic         | `template_2d_frame.py` (dynamic branch) |
| 2D    | RC       | Wall/Shear      | `template_2d_wall.py` |
| 2D    | Soil/Sand| Any             | `template_geotechnical.py` |
| 3D    | Any      | Any             | `template_3d_frame.py` |
| 2D    | Beam+SSI | Spring support  | `template_2d_beam.py` |

---

## 9. README.md Auto-Generation Template

When creating `models/<UniqueID>/README.md`, use:

```markdown
# <UniqueID>

**Purpose:** <purpose field>

**Building System:** <Description of Building Structural System>

**Model Description:** <Description of Model>

| Field | Value |
|-------|-------|
| Dimensions | <2D/3D> |
| Material | <Material> |
| Lateral System | <Lateral system> |
| Lateral Loading | <Lateral Loading> |
| Earthquake Records | <Earthquake records> |
| Design Year | <Year of design and construction> |
| File Format | <file format> |
| OpenSees Version | <Opensees Version> |
| Units | N, mm, MPa |

**References:**
<Links to Papers / Design Reports>

**Suggested Citation:**
<Suggested Model citation>

**Notes:** <Notes>
```

---

## 10. Prohibited Patterns (Auto-Flagged)

The agent will flag any of the following as FAIL during audit:

```python
# ❌ Wildcard import
from openseespy.opensees import *

# ❌ Magic number tag
ops.uniaxialMaterial("Steel01", 1, 250e3, 200e6, 0.02)

# ❌ Hard-coded path
ops.recorder("Node", "-file", "C:/Users/john/results/disp.txt", ...)

# ❌ Redefined units
kN = 1.0   # should come from standards/units.py

# ❌ Non-N/mm unit system (after conversion)
h_story = 3.0 * m    # must be: h_story = 3000.0 * mm  (or 3.0 * m where m = 1000 mm)

# ❌ Imperial bare number without conversion
h_story = 10.0   # ft?  in?  — WARN [UNIT_UNKNOWN]
Es = 29000.0     # ksi — must become:  Es = 29000.0 * ksi  (= 200 GPa)

# ❌ Raw OpenSees recorder — replaced by CreateODB
ops.recorder("Node", "-file", str(output_dir / "disp.txt"), ...)   # use CreateODB

# ❌ Importing the removed recorder_utils module
from recorder_utils import add_node_recorders, add_element_recorders   # module deleted

# ❌ Missing fetch_response_step inside the step loop
for seg in segs:
    analysis.StaticAnalyze(node=ctrl_node, dof=ctrl_dof, seg=seg)
    # odb.fetch_response_step() missing — FAIL [ODB_FETCH]

# ❌ save_response() called inside the loop instead of after it
for seg in segs:
    analysis.StaticAnalyze(...)
    odb.fetch_response_step()
    odb.save_response()   # must be outside the loop, in post_process

# ❌ Raw OpenSees solver call — bypasses SmartAnalyze convergence management
ops.analyze(100, 0.01)           # must use opst.anlys.SmartAnalyze

# ❌ Importing the removed analysis_utils module
from analysis_utils import run_gravity, run_pushover, run_dynamic   # module deleted

# ❌ Manual test/algorithm calls alongside SmartAnalyze
ops.test("NormDispIncr", 1.0e-6, 10)   # SmartAnalyze manages these internally
ops.algorithm("Newton")                 # SmartAnalyze manages these internally

# ❌ Wrong opstool alias or calling plot directly instead of via vis_utils
import opstool as opsv           # must be: import opstool as opst
opst.plot_model(...)             # must be: opst.vis.plotly.plot_model(...)

# ❌ Not saving to HTML — showing interactive pop-up instead
opst.vis.plotly.plot_model()     # return value discarded; must call .write_html()

# ❌ Flat script (no functions)
ops.wipe()
ops.model(...)
ops.node(1, 0.0, 0.0)
# ... 300 more lines at module level

# ❌ Missing visualisation stage
def run_analysis(output_dir):
    ...
    define_elements()
    # vis_model() missing — FAIL [VIS_MODEL]
    define_gravity_loads()

# ❌ ODB with ALL nodes/elements on large transient models — may hang
#    For models with 200+ nodes and 1000+ time steps, always use
#    targeted node_tags / frame_tags / truss_tags (see §3d).
```

### Permitted exceptions to SmartAnalyze mandate

**Load-controlled gravity analysis** — `SmartAnalyze.StaticAnalyze()` forcibly
overrides any integrator to `DisplacementControl`, making load-controlled gravity
impossible with SmartAnalyze. When LoadControl is required (e.g. elastic models
using `algorithm("Linear")`), a manual `ops.analyze()` loop with `odb.fetch_response_step()`
is permitted. See §3c "Gravity (load-controlled static)" for the approved pattern.

```python
# ✅ PERMITTED — LoadControl gravity with manual loop
ops.integrator("LoadControl", 1.0 / n_steps)
ops.test("EnergyIncr", 1.0e-6, 100)
ops.algorithm("Linear")
ops.analysis("Static")
for _ in range(n_steps):
    ops.analyze(1)
    odb.fetch_response_step()
ops.loadConst("-time", 0.0)
```

This is the **only** exception to the "no raw `ops.analyze()`" rule.

---

## 11. Environment & opstool Version Compatibility

### Conda environment

The project uses a dedicated conda environment that pins a compatible Python + opstool combination:

```bash
conda activate opensy     # Python 3.11, opstool >= 1.0
```

The `opensy` environment is the **target runtime** for all models in this repository.
Prefer `conda activate opensy` before running any model.

### opstool API versions (BREAKING change at 1.0)

opstool 1.0 removed the legacy `GetFEMdata` / `OpsVisPlotly` HDF5-based API and
replaced it with `post.CreateODB` / `vis.plotly.plot_model` (Zarr/ODB backend).
Models written for 0.8.7 will NOT run on 1.0 without changes.

| Feature | opstool 0.8.7 (legacy) | opstool >= 1.0 (target) |
|---------|----------------------|-------------------------|
| Model snapshot | `opst.GetFEMdata(path).get_model_data()` | `opst.post.CreateODB(odb_tag=1).save_model_data()` |
| Per-step collection | `.get_resp_step()` | `odb.fetch_response_step()` |
| Finalise responses | `.save_resp_all()` | `odb.save_response()` |
| Eigen output | `.get_eigen_data(mode_tag, solver)` | `odb.save_eigen_data(mode_tag, solver)` |
| Plot model (vis_utils) | `OpsVisPlotly(results_dir).model_vis(save_html=...)` | `opst.vis.plotly.plot_model(...).write_html(...)` |
| Deformed shape (vis_utils) | `OpsVisPlotly(results_dir).deform_vis(...)` | `opst.vis.plotly.plot_nodal_responses(...).write_html(...)` |
| Output format | `.hdf5` files | `.zarr` / `.odb` files |
| NumPy compat patch | `np.NAN = np.nan; np.NaN = np.nan` REQUIRED | NOT needed |

**Key rules:**
- Use `conda activate opensy` — it has Python 3.11 + opstool 1.0.26 (the target stack)
- `standards/vis_utils.py` MUST be compatible with the target opstool version (currently 1.0 API)
- When running models outside `opensy` env, check `opstool.__version__` first — if < 1.0, the model and vis_utils will fail with `AttributeError: module 'opstool' has no attribute 'GetFEMdata'` (or similar)
- The numpy `np.NAN`/`np.NaN` workaround is ONLY needed for opstool 0.8.7 on NumPy >= 2.0 — do NOT include it in new models

---

## 12. Tcl-to-Python Conversion Guide (Lessons Learned)

> **Source:** Compiled from the shegay2019 NZ.tcl (37K-line, 800 material groups) → model.py (~650 lines) conversion.

### 12a. Tag Scheme Extraction

Tcl models often use **multi-range tag schemes** where the prefix digit position shifts
depending on how many digits the group number has, avoiding collisions with reserved ranges.

**Pattern:** Extract as a helper function rather than reverse-engineering flat formulas.

```python
def _tag3(prefix: int, idx: int, group_offset: int = 0) -> int:
    """Tcl 3-range tag: prefix + (group_offset+idx)*10000 + 1, with digit shift
    when the group number crosses 9 or 99 to keep tags non-colliding."""
    group = group_offset + idx
    if group < 10:
        return prefix * 100_000 + group * 10_000 + 1
    elif group < 100:
        return prefix * 1_000_000 + group * 10_000 + 1
    else:
        return prefix * 10_000_000 + group * 10_000 + 1
```

**Why:** The tag formula appears simple (e.g., `prefix + group*10000 + 1`) but silently
collides at group boundaries (9→10, 99→100). A helper function encodes the digit-shift
logic once and is testable in isolation.

### 12b. Mass Placement — Verify Source

**Always verify which nodes get massed in the source model.** Some Tcl models mass only
one side (e.g., left master nodes); the other side receives mass implicitly through
rigid diaphragm constraints.

**Symptom:** Massing both sides **doubles the translational mass**, producing
`T_python ≈ 1.4 × T_tcl` (since T ∝ √m).

**Fix:** Grep the source for `mass` commands and match the node list exactly. In shegay2019,
only 8 `mass` commands existed (left master nodes 110001–180001); the right side was
connected via rigid truss diaphragm elements.

### 12c. Parameter Cross-Verification

Multi-parameter element commands are **prone to value swapping**. Verify every parameter
against the source line-by-line.

**Real example (shegay2019 elasticBeamColumn):**

| Parameter | Tcl value | Initial Python (WRONG) | Correct Python |
|-----------|-----------|------------------------|----------------|
| A | 806400 in² | `806400 * inch**2` ✓ | `806400 * inch**2` ✓ |
| E | 1732.55 ksi | `E_STEEL` (29000 ksi) ✗ | `1732.55 * ksi` |
| I | 0.27648 in⁴ | `1732.55 * inch**4` ✗ | `0.27648 * inch**4` |

The E and I values were swapped — E got steel's modulus and I got the E value. This
made the PDelta column 16.7× stiffer than intended. The fix had negligible effect on
global periods (the leaning column carries gravity, not lateral stiffness), but
illustrates the risk.

**Rule:** After conversion, diff every numeric parameter in element/material/section
definitions against the original source. A one-line grep of the Tcl for each value
catches most swaps.

### 12d. ODB Performance for Large Transient Analyses

`fetch_response_step()` calls the OpenSees API for **every tracked node and element**
on every call. For a model with 330+ nodes and 8000 steps, this means ~2.6 million
API calls — potentially hours of I/O overhead.

**Mitigations (in priority order):**

1. **Throttle collection** (most effective, always safe):
   ```python
   ODB_EVERY_N = 10  # for analyses with >500 steps
   for i, _ in enumerate(segs):
       ok = analysis.TransientAnalyze(dt)
       if i % ODB_EVERY_N == 0:
           odb.fetch_response_step()
   ```
   Reduces 8000 collections → 800. Aim for ≤500 total `fetch_response_step()` calls.

2. **Selective node tracking** (use with caution):
   ```python
   odb = opst.post.CreateODB(odb_tag=1, node_tags=[...])
   ```
   **WARNING:** Filtering `node_tags` prevents opstool from rendering the full model
   mesh in deformation plots (`plot_nodal_responses`, `plot_nodal_responses_animation`).
   Only use for data-extraction scripts, NOT for visualization models.

**Symptom of no throttling:** Dynamic analysis progresses at 17+ steps/sec for the first
~300 steps, then slows to ~2 steps/sec as ODB data accumulates. Appears as a hang.

### 12e. OpenSeesPy beamIntegration Limitation

**Tcl** supports per-IP sections via inline `-sections`:
```tcl
element dispBeamColumn $tag $i $j $nIP -sections $s1 $s2 ... $sN $transf -integration Lobatto
```

**OpenSeesPy** uses `beamIntegration("Lobatto", integ_tag, section_tag, N)` where
**all IPs share one section**. Per-IP material state tracking is lost.

**Impact:** For fiber-section models, this causes **~10–15% stiffness difference**
in fundamental period compared to the Tcl reference (800 material groups → 160).
This is a fundamental OpenSeesPy limitation — not a bug in the conversion.

**Rule:** Document the discrepancy in the model header and catalogue Notes field.
Accept it as a known approximation; do not chase convergence by distorting material
properties.

### 12f. Standalone Post-Processing Script

A `post_process.py` that reads existing ODB data is **valuable infrastructure** —
it allows re-generating visualizations without re-running the (potentially hour-long)
solver.

```python
"""Standalone post-processing — reads existing ODB data, generates visualizations."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
import opstool as opst

ODB_TAG = 1
output_dir = Path(__file__).parent / "output"
opst.post.set_odb_path(str(output_dir))  # MUST be called before any vis function

# Slider view: step-by-step with draggable slider
opst.vis.plotly.plot_nodal_responses(
    odb_tag=ODB_TAG, slides=True, defo_scale=True,
    resp_type="disp", resp_dof="UX",
).write_html(str(output_dir / "vis_05_slider.html"))

# Peak deformation snapshot
opst.vis.plotly.plot_nodal_responses(
    odb_tag=ODB_TAG, step="absMax", defo_scale=True,
    resp_type="disp", resp_dof="UX",
).write_html(str(output_dir / "vis_06_peak.html"))
```

**Key visualizations available from ODB data (no re-run needed):**
| Function | Key param | Output |
|----------|-----------|--------|
| `plot_nodal_responses()` | `slides=True` | Step-by-step slider view |
| `plot_nodal_responses()` | `step="absMax"` | Peak deformation snapshot |
| `plot_nodal_responses_animation()` | `framerate=N` | Auto-play animation |

### 12g. Imperial → N-mm Conversion Checklist

| Quantity | Tcl unit | Python expression | Gotcha |
|----------|----------|-------------------|--------|
| Length | in | `value * inch` | inch = 25.4 mm |
| Force | kip | `value * kip` | kip = 4448.22 N |
| Stress | ksi | `value * ksi` | ksi = 6.89476 MPa |
| Mass | kip·s²/in | `value * kip / inch` | Numerically correct since sec=1 |
| Rotational stiffness | kip·in/rad | `value * kip * inch` | NOT `kip/inch` — that's force/length |
| Ground motion accel | in/s² | `-factor inch` in timeSeries | Converts to mm/s² |
| Section dimension | in | `value * inch` | Used inside `ops.patch()` / `ops.layer()` |
| Area | in² | `value * inch**2` | |
| Inertia | in⁴ | `value * inch**4` | |
| Soft elastic stub | E=0.01 (ksi) | `0.01` (MPa) | Technically 0.01 ksi = 0.069 MPa, but negligible in Parallel materials |

### 12h. MDOF Shear Building — SimCenter EE-UQ Conversion Pattern

Source: Zhong2022 MDOF_BuildingModel Tcl → Python conversion.

#### 12h-1. TwoNodeLink + Steel01 Architecture

For stick/shear-building models, use `twoNodeLink` elements with:
- **Steel01** bilinear materials for horizontal shear DOFs (X and Y)
- **Elastic** rigid materials (1e12–1e15) for vertical axial and rotational DOFs
- **`-orient 1 0 0 0 1 0`** flag to orient local-x = global-X (horizontal), local-y = global-Y (vertical)

The benign warning `"ignoring nodes and using specified local x vector"` confirms the -orient flag is working correctly — it suppresses node-based auto-orientation. This is expected for vertical links.

#### 12h-2. Eigen Solver: Avoid fullGenLapack with Stiffness Contrasts

**Problem:** `fullGenLapack` eigen solver fails when the stiffness matrix has multi-order-of-magnitude contrasts (e.g., rigid springs at ~1e12 vs shear springs at ~1e5). Produces complex eigenvalues (e.g., `T1 = 0.0000-0.3678j s`) and aborts with OpenSeesError.

**Fix:** Use the default subspace iteration solver — `ops.eigen(mode_j)` without specifying `-fullGenLapack`. The default solver handles ill-conditioned matrices robustly.

#### 12h-3. `ops.wipeAnalysis()` Between Analysis Types

**Problem:** SmartAnalyze warns `"can't set transient integrator in static analysis"` when the gravity (static) analysis object is not cleaned up before dynamic (transient).

**Fix:** Call `ops.wipeAnalysis()` after `ops.loadConst("-time", 0.0)` in the gravity function to clear the static analysis object before the transient solver starts.

#### 12h-4. EDP Tracking During Analysis

For EDPs that cannot be derived from ODB alone (e.g., peak values across all time steps), track them in-memory during the dynamic loop:
- `ops.nodeDisp()` / `ops.nodeAccel()` at each converged step
- Update running maximums in a dict keyed by `"story-dof"`
- Assemble into SimCenter-compatible EDP.json format (`1-PID-X-Y`, `1-PFA-X-Y`) during post-processing

#### 12h-5. SimCenter Parameter Mapping

SimCenter EE-UQ JSON parameter keys map directly to model constants:
- `"W"` → floor weight, `"k"` → story stiffness, `"Fy"` → yield strength, `"HR"` → hardening ratio
- Units in the JSON are imperial (kip, in, s); convert to N, mm using `standards/units.py` constants
- PEER .AT2 ground motion files: parse header line for npts/dt, then space-delimited acceleration values in g

#### 12h-6. Output Artifact Hygiene

Add `.gitignore` patterns to exclude generated output:
```gitignore
models/*/output/*
!models/*/output/.gitkeep
```
Use `.gitkeep` to preserve the empty output directory in version control so other modelers can run the model without creating the directory manually.

### 12i. Ground Motion Ordering: `ops.loadConst()` Freezes All Loads

**Critical rule:** `define_ground_motion()` (UniformExcitation with Path timeSeries) MUST be called AFTER `run_gravity()` completes. Calling it before gravity causes `ops.loadConst("-time", 0.0)` to freeze the UniformExcitation at its t≈0 value, permanently disabling the ground motion.

#### Root Cause

`ops.loadConst("-time", 0.0)` applies to **all** load patterns in the domain — not just gravity. It sets each pattern's load factor to the value at the specified pseudo-time. For a UniformExcitation driven by a Path timeSeries, the load factor at pseudo-time 0 is the first data point (≈0 acceleration). After `loadConst`, the timeSeries no longer advances — the ground motion is held constant at near-zero for the entire dynamic analysis.

#### Symptom

EDPs (drifts, accelerations) are near-zero (~1e-15) despite a valid ground motion input. The structure appears to not respond to the earthquake. Fundamental periods are correct (T1 matches expectation), confirming the model stiffness is correct — the ground motion simply isn't being applied.

#### Fix

Always order the analysis sequence as:

```python
# CORRECT — GM after gravity
define_gravity_loads()
run_gravity(odb)
# loadConst freezes gravity only (GM not yet defined)
define_ground_motion()    # ← AFTER gravity
run_dynamic(odb, dt, npts)
```

```python
# BROKEN — GM before gravity
define_gravity_loads()
define_ground_motion()    # ← defined too early
run_gravity(odb)
# loadConst freezes BOTH gravity AND ground motion to t≈0
run_dynamic(odb, dt, npts)  # no ground motion applied
```

#### Debugging Protocol

If EDPs are suspiciously near-zero after what appears to be a successful run:

1. Check max roof displacement during dynamic loop — if constant at ≈gravity deflection, GM is frozen
2. Create a minimal SDOF test with the same pattern ordering to isolate
3. Binary test: run with GM-before-gravity vs GM-after-gravity — compare EDPs
4. If EDP ratio (correct/wrong) > 1e6, `loadConst` freezing is the cause

#### Detection in Existing Models

Flag any model where `define_ground_motion()` (or equivalent UniformExcitation setup) appears before the `ops.loadConst("-time", 0.0)` call in `run_gravity()`. This is a FAIL item in audit.

**Why:** This bug was discovered during the NEES2014 conversion and cost several hours of debugging. The model appeared to run successfully (no errors, SmartAnalyze reported success) but produced physically meaningless EDPs. The fix is a one-line reorder, but the symptom is silent — no warnings, no convergence failures, just near-zero results.

### 12j. SI → N-mm Conversion (Meters to Millimeters)

Source: XMU Chapter4.1 (SI: N, m, kg, Pa) → N-mm-MPa conversion.

#### Critical: `Pa` in units.py Is NOT the SI Pascal

`units.py` defines `Pa = N / mm**2 = 1.0`. Since N=1 and mm=1, this evaluates to 1.0, which is numerically **1 MPa** (= 1 N/mm²), NOT 1 SI-Pascal (1 Pa = 1 N/m² = 1e-6 N/mm²).

**Symptom of misuse:** `E = 3.0e10 * Pa` (intended 30 GPa) gives 3e10 in N-mm units (= 30,000,000 GPa). The structure becomes 1,000,000× too stiff — T1 drops from ~0.4s to ~0.0004s.

**Fix:** Convert SI stress values manually — divide by 1e6:
```python
# BROKEN — Pa = 1.0 (N/mm²), NOT 1e-6 (SI-Pa)
E = 3.0e10 * Pa    # → 3e10 MPa (absurd)

# CORRECT — manual conversion from SI-Pa to N/mm²
E = 30000.0 * MPa  # 3e10 Pa ÷ 1e6 → 30000 N/mm² = 30 GPa
```

#### SI → N-mm conversion table

| Quantity | SI value | SI unit | → N-mm expression | Numerical | Notes |
|----------|----------|---------|-------------------|-----------|-------|
| Length | `val` | m | `val * m` | val × 1000 | uses `m` constant ✓ |
| Area | `val` | m² | `val * m**2` or `val * m2` | val × 10⁶ | uses `m2` helper ✓ |
| Inertia | `val` | m⁴ | `val * m**4` or `val * m4` | val × 10¹² | uses `m4` helper ✓ |
| Force | `val` | N | `val * N` | val × 1 | N = 1.0, unchanged ✓ |
| Stress | `val` | Pa | `val / 1e6` or `(val/1e6) * MPa` | val ÷ 10⁶ | **NEVER use `Pa`** |
| Mass | `val` | kg | `val / 1000.0` | val ÷ 10³ | **NEVER use `kg`** (=1.0); 1 N·s²/mm = 1000 kg |
| Acceleration | — | m/s² | `g_accel` | 9806.65 | g in mm/s² ✓ |

#### Mass conversion detail

In the N-mm-s system, the consistent mass unit is N·s²/mm (= 1000 kg = 1 tonne). `units.py` defines `kg = N * sec**2 / mm = 1.0`, which does NOT represent 1 kilogram — it represents 1 N·s²/mm (= 1000 kg). Using `10000 * kg` would give mass=10000 N·s²/mm (= 10,000 tonnes) instead of the correct 10 N·s²/mm (= 10 tonnes = 10000 kg).

```python
# BROKEN — kg = 1.0 (N·s²/mm), NOT 1 kg
mass = 10000.0 * kg   # → 10000 N·s²/mm = 10,000 tonnes (10× too heavy)

# CORRECT
mass = 10.0            # 10000 kg ÷ 1000 = 10 N·s²/mm (10 tonnes)
```

#### Detection in Existing Models

Flag any SI-sourced model where:
- `* Pa` appears in stress/modulus definitions → likely 1e6× too stiff
- `* kg` appears in mass definitions → likely 1000× too heavy
- T1 is implausibly small (< 0.001s for building-scale structures) → check E value

**Why:** Most conversions in this project are imperial→N-mm (where kip, inch, ksi constants work correctly). SI→N-mm is rarer but the `Pa` and `kg` constants in units.py are misleading — they don't represent their SI namesakes.

### 12k. Aggregator Section — kN-m→N-mm Conversion

Source: XMU Chapter4.2 (portal frame with Aggregator column sections, kN-m-kPa→N-mm-MPa conversion).

#### Critical: Aggregator Materials Are Force-Deformation, NOT Stress-Strain

An `ops.section("Aggregator", tag, mat_P, "P", mat_Mz, "Mz")` defines section-level force-deformation response. The material assigned to the `"P"` dof has units of **force per unit strain** (N for axial), and the material assigned to `"Mz"` has units of **moment per unit curvature** (N·mm for flexure). They are NOT stress-strain materials.

This means the standard stress conversion (kPa → MPa: ÷1000) gives values that are too small by factors of 1e6 (P) and 1e9 (Mz), because it doesn't account for the missing area and section-modulus factors that a fiber section would implicitly provide.

#### Conversion Factors

| Aggregator DOF | Original unit | → N-mm factor | Why |
|----------------|--------------|---------------|-----|
| `P` (axial force) | kN | × 1000 | Force: kN → N |
| `Mz` (moment) | kN·m | × 1e9 | Moment: kN→N (×1000) + curvature 1/m→1/mm (×1e6) = ×1e9 |

#### Worked Example (XMU Chapter4.2)

```python
# Original Tcl values (kN, m, kPa):
#   E_ax = 4.62e7 kPa   (axial stiffness for Aggregator P)
#   E_fx = 5.74e6 kPa   (flexural stiffness for Aggregator Mz)
#   Fy   = 1.47e4 kPa   (yield stress for Steel01 in Aggregator Mz)

# CORRECT — Aggregator force-deformation conversion
E_col_ax = 4.62e7 * 1000.0     # P: kN→N → 4.62e10 N per unit strain
E_col_fx = 5.74e6 * 1.0e9      # Mz: kN·m→N·mm + curvature → 5.74e15 N·mm per unit curvature
Fy_col   = 1.47e4 * 1.0e9      # My: kN·m→N·mm → 1.47e13 N·mm yield moment

# CONTRAST — Regular elastic beam section (stress-strain based)
E_beam = 2.49e7 / 1000.0        # kPa→MPa → 24900 MPa
A_beam = 3.72 * m**2            # m²→mm² → 3.72e6 mm²
I_beam = 1.8413 * m**4          # m⁴→mm⁴ → 1.8413e12 mm⁴
```

#### Symptom of Wrong Conversion

- **T1 too large** (e.g., 247,188s instead of ~0.26s) — model is impossibly soft because Aggregator stiffness values are 1e6–1e9× too small
- The fix is counterintuitive: **multiply** Aggregator stiffnesses (not divide like regular stress conversion)

#### Detection in Existing Models

Flag any kN-m-sourced model where:
- `section("Aggregator", ...)` is used with materials that were converted via standard stress conversion (÷1000)
- T1 is implausibly large (> 100s for a building-scale structure)
- Aggregator material values look "small" (e.g., 4.62e4 for what should be ~4.62e10)

**Why:** This is the first model in the project using Aggregator sections with a non-N-mm source. The standard kN→N-mm stress conversion (÷1000) silently produces values 1e6–1e9× too small because Aggregator materials bypass the cross-section geometry that would normally convert stress to force/moment.

### 12l. dispBeamColumn Requires beamIntegration in OpenSeesPy

Source: XMU Chapter4.3 (RC portal frame with fiber-section columns, dispBeamColumn elements).

#### Critical: Different Argument Signature from nonlinearBeamColumn

`ops.element("dispBeamColumn", ...)` in OpenSeesPy requires a separate `beamIntegration` object. The element signature is:

```python
# dispBeamColumn (OpenSeesPy)
ops.element("dispBeamColumn", eleTag, iNode, jNode, transfTag, integTag)
```

This differs from `nonlinearBeamColumn` which takes section tag + nIP directly:

```python
# nonlinearBeamColumn (reference)
ops.element("nonlinearBeamColumn", eleTag, iNode, jNode, nIP, secTag, transfTag)
```

#### Correct Usage

```python
ops.beamIntegration("Legendre", INTEG_COL, SEC_COL, n_ip)  # or "Lobatto"
ops.element("dispBeamColumn", ELE_COL, NODE_I, NODE_J, TRANS_COL, INTEG_COL)
```

#### Symptom of Wrong Argument Order

- Passing `(eleTag, iNode, jNode, nIP, secTag, transfTag)` — the nonlinearBeamColumn order — causes:
  - `CrdTransf *getCrdTransf(int tag) - none found with tag: 5` when nIP=5 ends up in the transfTag position
  - `BeamIntegrationRule - none found with tag: 1` when secTag ends up in the integTag position

#### Detection in Existing Models

Flag any model where:
- `dispBeamColumn` is called with 6+ positional args after the element name (instead of 5)
- The 4th arg is a small integer (likely nIP being misinterpreted as transfTag)
- CrdTransf-not-found errors reference suspicious tag numbers matching nIP values

**Why:** This was discovered during the XMU Chapter4.3 conversion where the Tcl uses `element dispBeamColumn 1 1 3 5 1 1` (eleTag, iNode, jNode, nIP, secTag, transfTag). The natural Python translation using the same arg order fails because OpenSeesPy wraps dispBeamColumn to always use beamIntegration.

### §12m — Soil-Structure Interaction with Sequential Model Building (v1.14.0)

#### All Standard Materials for 2D SSI

`MultiYieldSurfaceClay`, `quadWithSensitivity`, and `Hardening` are all available in standard OpenSeesPy from PyPI. A 2D soil-structure interaction model (RC frame on layered soil deposit) does NOT require a custom build — unlike shear wall models relying on `SmearedConcrete`/`SmearedCompositePlaneStress`.

**MultiYieldSurfaceClay** signature: `(tag, nd, rho, Gr, Br, cohesion, peakShearStrain, frictionAngle, refPress, pressDependCoeff, numberOfYieldSurf)`. Set `rho=0` when the soil provides only stiffness and damping (frame nodes carry all lumped mass for inertial effects).

**quadWithSensitivity** signature: `(tag, iNode, jNode, kNode, lNode, thickness, "PlaneStrain", matTag, pressure, density, bodyForceX, bodyForceY)`. The body force handles soil self-weight; the `density` param provides element-level dynamic mass (often set to 0 when using lumped masses on frame nodes).

**Hardening** for rebar: `(tag, E, sigmaY, H_iso, H_kin)`. For kinematic-only hardening, set `H_iso=0`. The equivalent stiffness ratio is `b = H_kin / (E + H_kin)`. Standard OpenSeesPy — no custom build needed.

#### Sequential Model Building (ndf=3 → ndf=2 → equalDOF)

When a model has a frame superstructure (ndf=3: UX, UY, RZ) sitting on a 2D soil continuum (ndf=2: UX, UY), build in three phases:

1. **Frame** — `ops.model("basic", "-ndm", 2, "-ndf", 3)` → nodes, elements, boundary conditions
2. **Soil** — `ops.model("basic", "-ndm", 2, "-ndf", 2)` → nodes, quad elements, body forces, base fixity
3. **Ties** — `ops.equalDOF(soil_node, frame_node, 1, 2)` (UX and UY only; no rotational coupling)

Each `ops.model()` call resets the default ndf for newly created nodes. Soil nodes created after the second call automatically get ndf=2.

#### Soil Body Force Conversion (kN/m³ → N/mm³)

Soil self-weight expressed as ρg in kN/m³ (e.g., γ = 19.6 kN/m³) converts to N/mm³ by dividing by 10⁶:

```
bodyForceY = -19.6e-6  # kN/m³ → N/mm³
```

This value (~10⁻⁵) is tiny but correct — the quad element multiplies by element volume internally, so the net force matches the physical soil weight.

#### Ground Motion Conversion (m/s² → mm/s²)

When the ground motion file contains values in m/s² (peak ~1–3 m/s²), convert to mm/s² by multiplying by 1000. Apply this scaling via the timeseries factor:

```python
gm_scale = factor * 1000.0  # factor=3.0 → 3000 total
ops.timeSeries("Path", tag, "-dt", dt, "-values", *accel, "-factor", gm_scale)
```

Do NOT use `g_accel` (9810 mm/s²) — that converts g-units to mm/s², not m/s² to mm/s².

#### Non-Standard Newmark Parameters

If the source Tcl uses non-standard Newmark parameters (e.g., γ=0.55, β=0.275625, equivalent to HHT α=-0.05), preserve them exactly in the Python translation. These introduce slight negative numerical damping and were chosen intentionally.

#### No Rayleigh Damping

If the source Tcl has no Rayleigh damping definitions, do NOT add any. The soil constitutive model and the implicit Newmark integration provide enough dissipation. Adding unrequested damping changes the response.

**Why:** Chapter6 uses all four of these patterns together. The MultiYieldSurfaceClay + quadWithSensitivity combo was confirmed working in standard OpenSeesPy via an isolated agent smoke test before writing the full model. The sequential model building pattern avoids ndf mismatches (frame nodes with ndf=2 missing RZ, or soil nodes with ndf=3 having ghost RZ). The body force and ground motion conversions are both ÷10⁶ / ×10³ issues that would produce wildly wrong results if mishandled.

---
## 13. Versioning & Change Log

| Date | Version | Change |
|------|---------|--------|
| 2025-05-08 | 1.0.0 | Initial AGENT.md created |
| 2025-05-09 | 1.1.0 | Unit system → N/mm/MPa; opstool stages added; JSON catalogue workflow added |
| 2025-05-09 | 1.1.1 | opstool API corrected to `opst.vis.plotly.plot_model(...).write_html()`; HTML output to `output/`; `_headless()` in `vis_utils.py` |
| 2025-05-09 | 1.2.0 | `analysis_utils.py` removed; all solver loops replaced with `opst.anlys.SmartAnalyze`; Section 3c added; audit checklist extended to 28 items (0–27) |
| 2025-05-09 | 1.3.0 | `recorder_utils.py` removed; all response collection replaced with `opst.post.CreateODB`; Section 3d added; `run_analysis` now returns `odb`; `post_process` calls `odb.save_response()`; `ops.recorder()` added to prohibited patterns |
| 2025-05-09 | 1.4.0 | Consistency fixes: `vis_stage_*` renamed to `vis_*` to match `vis_utils.py` exports; `run_gravity` gains `ctrl_node`/`ctrl_dof` params; V1 stage trigger clarified to after `define_boundary_conditions()`; audit checklist extended to 30 items (0–29) adding `analysis.close()` and `output_dir.mkdir()` checks; `analysis_utils` added to item 2; ALLCAPS naming rule clarified; `num_models` type documented; `vis_defo` updated to use `plot_nodal_responses` (ODB-based); malformed-JSON error handling added to Section 7e |
| 2025-05-11 | 1.5.0 | **Snippet-by-snippet mode** (§7f) added as default CONVERT workflow — agent processes one code section at a time, confirms each before requesting the next; **New project from scratch mode** (§7g) added — supports designing original OpenSeesPy models via guided Q&A, not limited to existing OpenSees examples; Section 1 updated with mode table (CONVERT / NEW); Section 7 updated with mandatory session-start mode question; snippet identification hint table added to §7f |
| 2025-05-11 | 1.5.1 | **opstool API corrections:** (1) `plot_model` kwargs renamed throughout — `show_node_label` → `show_node_numbering`, `show_ele_label` → `show_ele_numbering` (correct v1.x API); (2) `CreateODB` `save_every` param removed — does not exist in the real API; (3) `fiber_ele_tags="all"` in selective-saving example replaced with correct `save_fiber_sec_resp=False` bool param; (4) `vis_model()` wrapper signature updated to match corrected kwarg names |
| 2025-05-11 | 1.5.2 | **API corrections:** (1) `resp_dof` values corrected to uppercase throughout (`"ux"` → `"UX"`, `"uy"` → `"UY"`) — opstool requires uppercase DOF labels in `plot_nodal_responses`; (2) `vis_defo` now forwards `scale` param to `plot_nodal_responses`; (3) `vis_model` stub in canonical script corrected to `show_node_numbering=True` to match `vis_utils.py` defaults and Section 3b table; (4) §7a audit reference corrected from items 0–27 to 0–29 |
| 2026-05-31 | 1.6.0 | **SmartAnalyze Static limitation & ODB performance:** (1) §3c gravity pattern corrected — SmartAnalyze.StaticAnalyze forcibly overrides the integrator to DisplacementControl; LoadControl gravity with manual ops.analyze() loop permitted exception documented in §3c and §10; (2) §3d expanded with ODB performance guidance (targeted tags, throttled fetch for transient); (3) §10 added permitted exceptions subsection |
| 2026-06-01 | 1.7.0 | **opstool version compatibility & conda environment:** (1) §11 added documenting the breaking API change between opstool 0.8.7 (GetFEMdata/OpsVisPlotly/HDF5) and 1.0 (CreateODB/vis.plotly/Zarr); (2) `opensy` conda environment documented as target runtime (Python 3.11, opstool 1.0.26); (3) numpy NAN/NaN compatibility patch documented as 0.8.7-only; (4) vis_utils.py rewritten for opstool 1.0 API (plot_model/plot_nodal_responses returning Figure objects); (5) nafeh2022 model ported from 0.8.7 to 1.0 API as worked example of the conversion |
| 2026-06-14 | 1.8.0 | **Tcl-to-Python conversion guide (§12):** (1) §12a — Tag scheme extraction with `_tag3()` helper pattern for multi-range digit-shift schemes; (2) §12b — Mass placement verification (one-side vs both-side massing doubles translational mass); (3) §12c — Parameter cross-verification against source (E/I swap example from elasticBeamColumn); (4) §12d — ODB throttling for large transient analyses (ODB_EVERY_N, node_tags breaks mesh rendering); (5) §12e — OpenSeesPy beamIntegration limitation (all IPs share one section vs Tcl's per-IP, ~10-15% stiffness difference); (6) §12f — Standalone post_process.py pattern for re-visualization without re-running solver; (7) §12g — Imperial→N-mm conversion checklist with common gotchas. Source: shegay2019 NZ.tcl (37K lines) → model.py (~650 lines) conversion. |
| 2026-06-15 | 1.9.0 | **MDOF shear building conversion (§12h):** Zhong2022 SimCenter EE-UQ MDOF_BuildingModel Tcl→Python conversion. (1) TwoNodeLink + Steel01 stick architecture with -orient flag; (2) fullGenLapack eigen solver failure with stiffness contrasts → default subspace iteration; (3) ops.wipeAnalysis() required between static gravity and transient dynamic; (4) in-memory EDP tracking via ops.nodeDisp()/ops.nodeAccel() at ODB sample points; (5) SimCenter JSON parameter → model constant mapping; (6) output artifact .gitignore hygiene with .gitkeep preservation. |
| 2026-06-15 | 1.10.0 | **Ground motion ordering (§12i):** Documented the critical `ops.loadConst()` bug — freezes ALL loads (including UniformExcitation) to t=0 values, permanently disabling ground motion if defined before gravity. GM MUST be defined after `run_gravity()`. Source: NEES2014 conversion (3-story steel MRF). |
| 2026-06-15 | 1.11.0 | **SI→N-mm conversion (§12j):** Documented the `Pa`/`kg` gotcha in units.py. `Pa = N/mm² = 1.0` (actually 1 MPa, not 1 SI-Pascal). `kg = N·s²/mm = 1.0` (actually 1000 kg = 1 tonne, not 1 kg). SI-sourced models must manually convert: stress ÷1e6, mass ÷1000. Never use `* Pa` or `* kg` from units.py for SI conversions. Source: XMU Chapter4.1 conversion (SI cantilever column). |
| 2026-06-15 | 1.12.0 | **Aggregator section kN-m→N-mm conversion (§12k):** Documented that Aggregator section materials act as force-deformation (not stress-strain). P stiffness ×1000 (kN→N), Mz stiffness ×1e9 (kN·m→N·mm with curvature 1/m→1/mm). Standard stress conversion (÷1000) gives values 1e6–1e9× too small. Source: XMU Chapter4.2 conversion (portal frame with Aggregator columns). |
| 2026-06-15 | 1.13.0 | **dispBeamColumn beamIntegration requirement (§12l):** Documented that OpenSeesPy `dispBeamColumn` uses `beamIntegration` — signature is `(eleTag, iNode, jNode, transfTag, integTag)`, NOT `(eleTag, iNode, jNode, nIP, secTag, transfTag)` like `nonlinearBeamColumn`. Source: XMU Chapter4.3 conversion (RC portal frame with fiber-section columns). |
| 2026-06-16 | 1.14.0 | **Soil-Structure Interaction with Sequential Model Building (§12m):** Documented 2D SSI conversion patterns — MultiYieldSurfaceClay/quadWithSensitivity/Hardening all in standard OpenSeesPy; sequential ndf=3→ndf=2→equalDOF model building; soil body force kN/m³→N/mm³ (÷10⁶); ground motion m/s²→mm/s² (×1000 via timeseries factor, not g_accel); non-standard Newmark parameter preservation; no-Rayleigh-damping convention. Source: XMU Chapter6 conversion (2D RC frame + 5-layer soil deposit under El Centro). |

---
*This file is the single source of truth for the OpenSeesPy standardisation agent.
