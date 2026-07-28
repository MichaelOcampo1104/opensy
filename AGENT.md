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
| **V6 — Step slider** | `odb.save_response()` in `post_process` | `vis_slider(output_dir, filename="vis_06_slider.html", odb_tag=1, resp_dof="UX")` | `vis_06_slider.html` |

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

### §12o — Sensitivity Analysis with DDM: OpenSeesPy API Pitfalls (v1.16.0)

Source: XMU Chapter11 conversion (2D truss with Steel01, parameter sensitivity, El Centro GM).

#### 1. `addToParameter` Uses Bare Keywords (No Tcl Dashes)

```python
# BROKEN — Tcl-style dash prefixes
ops.addToParameter(tag, "-element", eleTag, "-material", "E")

# CORRECT — bare keywords
ops.addToParameter(tag, "element", eleTag, "material", "E")
```

The warning `"unable to assign parameter to object of type -element"` confirms the dash prefix is being parsed as the object type string, not a flag.

#### 2. Sensitivity Recorder Data Type Must Be a Single String

```python
# BROKEN — two separate args
ops.recorder("Node", "-file", "ddm.out", ..., "sensitivity", 1)

# CORRECT — single string
ops.recorder("Node", "-file", "ddm.out", ..., f"sensitivity {tag}")
```

Error symptom: `"NodeRecorder::NodeRecorder - dataToStore Invalid String Input! not recognized (disp, vel, accel, incrDisp, incrDeltaDisp)"`.

#### 3. SmartAnalyze Does NOT Support Sensitivity

DDM sensitivity computation requires `ops.sensitivityAlgorithm("-computeAtEachStep")` before each manual `ops.analyze(1)` step. SmartAnalyze provides no hook for this and wraps the solver loop internally, making it incompatible. Use manual analysis loops (documented exception per §3c/§10).

#### 4. CreateODB Element-Type Flags Must Match Element Type

| Element type | Flag | Tag param |
|---|---|---|
| Frame/beam | `save_frame_resp=True` | `frame_tags=[...]` |
| Truss | `save_truss_resp=True` | `truss_tags=[...]` |
| Link | `save_link_resp=True` | `link_tags=[...]` |

Using the wrong flag (e.g. `save_frame_resp=True` for truss elements) causes opstool to attempt beam-specific force extraction, producing `IndexError: list index out of range` in `_get_beam_local_force()`.

#### 5. `parents[n]` Depth Depends on Model Subfolder Nesting

When model.py is at `models/XMU/Chapter11/` (3 levels deep from repo root), `parents[2]` resolves to `models/`, not the repo root. Use `parents[3]` to reach the repo root for `sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))`.

| Model path | `parents` needed |
|---|---|
| `models/<UniqueID>/model.py` | `parents[2]` |
| `models/XMU/Chapter11/model.py` | `parents[3]` |

#### 6. Import All Required vis_* Functions

The canonical `from vis_utils import _headless` is insufficient when the model calls `vis_nodes()`, `vis_model()`, etc. Import explicitly:
```python
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis
```

### §12p — Explicit Dynamics & Element Removal: Peridynamics Model (v1.16.0)

Source: XMU Chapter12.2 conversion (40x40 PD grid, CentralDifference, bond-breaking).

#### 1. SmartAnalyze Incompatible with Explicit Dynamics

`opst.anlys.SmartAnalyze` wraps implicit solver loops (Newton-Raphson, KrylovNewton, etc.) with adaptive convergence management. It does NOT support:
- `CentralDifference` / `NewmarkExplicit` explicit integrators
- `ops.remove("element", tag)` during the analysis loop (element removal)

For explicit dynamics, use a manual `ops.analyze(1, dt)` loop:
```python
ops.integrator("CentralDifference")
ops.analysis("Transient")
for step in range(n_steps):
    ops.analyze(1, timestep)
    # optional per-step logic (e.g. element removal)
```

#### 2. ODB Impractical for Large Explicit Analyses

For models with 1600+ nodes and 4000+ time steps, calling `odb.fetch_response_step()` after every step produces **6.4 million API calls** — causing hours of I/O overhead and potentially appearing as a hang (see §3d, §12d).

**Mitigation:** Use `ops.recorder()` for complete output and CreateODB for model snapshot only:
```python
# Model snapshot only (no fetch_response_step in loop)
odb = opst.post.CreateODB(odb_tag=1, ...)
odb.save_model_data()          # geometry snapshot
# ... analysis loop without fetch_response_step ...
odb.save_response()            # finalise (may have no step data)

# Separate recorders for full output
ops.recorder("Node", "-file", "dispx.out", "-nodeRange", 1, nNodes, "-dof", 1, "disp")
```

The recorders produce text files that can be parsed with numpy later. This is a documented exception to the "no recorders" rule (§10) when ODB is not feasible.

#### 3. `nodeCoord` Returns Model-Unit Coordinates

`ops.nodeCoord(tag)` returns coordinates in the model's unit system. After N-mm conversion, a 40m × 40m grid produces coordinates in the range 0–39000 mm. The `fixX` command checks against the model-unit value:
```python
ops.fixX(0.0, 1, 1)  # fixes nodes where x == 0.0 mm
```

#### 4. Element Removal During Analysis

OpenSeesPy supports `ops.remove("element", tag)` during a transient analysis to model progressive damage/fracture. This works with `CentralDifference` but may cause instability if too many elements are removed at once. Check bond stretch in the per-step loop:
```python
# Deformed bond length check
cAx = ops.nodeCoord(n1)[0] + ops.nodeDisp(n1)[0]
cAy = ops.nodeCoord(n1)[1] + ops.nodeDisp(n1)[1]
cBx = ops.nodeCoord(n2)[0] + ops.nodeDisp(n2)[0]
cBy = ops.nodeCoord(n2)[1] + ops.nodeDisp(n2)[1]
length = math.sqrt((cBx - cAx)**2 + (cBy - cAy)**2)
if length > stretch_limit:
    ops.remove("element", ele)
```

#### 5. `numberer Plain` vs `numberer RCM`

For explicit dynamics with `CentralDifference`, the equation system is never factorised (the method uses lumped mass + damping). `numberer Plain` is acceptable and matches the original Tcl. The default `numberer RCM` also works but is unnecessary overhead.

#### 6. `ops.groundMotion()` for MultipleSupport Patterns

The `MultipleSupport` pattern uses `ops.groundMotion()` + `ops.imposedMotion()`:
```python
ops.pattern("MultipleSupport", 1)
ops.groundMotion(gmTag, "Plain", "-disp", seriesTag)
ops.imposedMotion(nodeTag, dof, gmTag)
```

This applies prescribed displacement to specific nodes (e.g. base nodes for earthquake excitation). The `-disp` flag specifies displacement time series (vs `-accel` for acceleration).

#### 7. `vis_defo()` in `vis_utils.py` Lags the AGENT.md Contract

The `vis_defo()` wrapper in `standards/vis_utils.py:78` is **missing `odb_tag` and `resp_dof` parameters** documented in the §3b table. Its signature:

```python
def vis_defo(output_dir, filename="vis_05_deformed.html", resp_dof="disp", scale=10.0)
```

But §3b documents calls like `vis_defo(output_dir, odb_tag=1, resp_dof="UX")` — these raise `TypeError: unexpected keyword argument`.

**Internally**, `vis_defo` ignores `resp_dof` entirely and hard-codes `odb_tag=1` and `resp_type="disp"` in the `plot_nodal_responses()` call. The `resp_dof` parameter name itself is misleading — it currently defaults to `"disp"` which is actually the response type, not a DOF selector.

**Fix:** The `vis_utils.py` signature should be updated to:
```python
def vis_defo(output_dir, filename="vis_05_deformed.html", odb_tag=1, resp_dof="disp", scale=10.0)
```
And forward `odb_tag` + `resp_dof` to `plot_nodal_responses()`. The `resp_dof` values `"UX"`, `"UY"` from §3b map to opstool's `plot_nodal_responses` `resp_dof` parameter (controls the scalar colour field).

**Rule of thumb:** When the AGENT.md §3b table shows a function signature, the implementation in `vis_utils.py` must match. Cross-check before deploying any model that depends on deformed-shape visualization.

### §12q — 3D Peridynamic Grid-Based Models: Node Indexing, Bond Generation, and Per-Material Concrete02 (v1.16.0)

Source: XMU Chapter12.3 conversion (3D PD concrete block, 2541 nodes, ~60K truss bonds, static DisplacementControl).

#### 1. Grid-Based Node Indexing Requires a `node_id()` Helper

For 3D peridynamic grids where the Tcl uses `nodeid($i,$j,$k)` as a computed tag, reproduce the indexing with a helper function:

```python
# Tcl: set nodeid($i,$j,$k) [expr 1 + $i*( $ndivy+1)*( $ndivz+1) + $j*( $ndivz+1) + $k]
NODE_STRIDE_Y = ndivz + 1
NODE_STRIDE_X = (ndivy + 1) * (ndivz + 1)

def node_id(i, j, k):
    return 1 + i * NODE_STRIDE_X + j * NODE_STRIDE_Y + k
```

This is critical because `fix`, `equalDOF`, and `recorder` commands all use these computed node IDs. An off-by-one error in the stride values produces wrong node locations or bond connectivity.

#### 2. Tcl `contact()` Matrix → Python `set` of Tuples

The Tcl uses a 2D array `contact($Cid,$Tid)` to prevent duplicate bonds. In Python, use a `set` of `(min_id, max_id)` tuples — simpler and avoids a large 2D list:

```python
visited: set = set()
# ...
key = (min(n1, n2), max(n1, n2))
if key in visited:
    continue
# ... create bond ...
visited.add(key)
```

#### 3. Transition-Zone Strength Scaling Affects Only Stress Properties

In peridynamic models with a transition zone (`horizon - radij < dist < horizon + radij`), only the material's **stress** (or stiffness) properties are scaled by `fac`. The strain-like properties remain unchanged:

| Parameter | Scaled by `fac`? | Reason |
|---|---|---|
| `fpc` (compressive strength) | Yes | Stress property |
| `fpcu` (crushing strength) | Yes | Stress property |
| `ft` (tensile strength) | Yes | Stress property |
| `Ets` (tension softening stiffness) | Yes | Stress/stiffness property |
| `epsc0` (strain at peak) | No | Strain property |
| `epsU` (ultimate strain) | No | Strain property |
| `lambda` (unloading ratio) | No | Shape parameter |

```python
# Inner zone — full strength
ops.uniaxialMaterial("Concrete02", tag, cfpc, epsc0, fpcu, epsU, lambda, ft, Ets)

# Transition zone — scaled strength
ops.uniaxialMaterial("Concrete02", tag,
    cfpc * fac, epsc0,   # stress scaled, strain unscaled
    fpcu * fac, epsU,
    lambda,
    ft * fac, Ets * fac,
)
```

#### 4. Each Bond Gets Its Own Material Tag

Unlike continuum models where one material serves many elements, peridynamic models often assign unique Concrete02 materials (tag = bond number) to each truss bond. This creates thousands of materials — XMU Chapter12.3 has ~60K unique Concrete02 instances. This is slow to create but is a faithful reproduction of the original Tcl per-bond material model.

#### 5. ODB Truss Response Saving Should Be Disabled for Large Bond Counts

With ~60K truss elements and 400 analysis steps, `save_truss_resp=True` would produce ~24M truss-force data points (~200 MB ODB file). For static models where truss forces can be recovered from recorder files, disable truss response saving:

```python
odb = opst.post.CreateODB(
    ...,
    save_nodal_resp=True,    # keep — needed for deformed-shape vis
    save_truss_resp=False,   # disable — too many bonds
)
```

Nodal responses (2541 nodes × 400 steps ≈ 1M values) are manageable and sufficient for deformed shape visualization.

#### 6. Static DisplacementControl with 400 Steps + `fetch_response_step` Is Practical

Unlike explicit dynamics (Ch12.2) where 4000 steps × 1600 nodes was impractical, a static model with 400 steps and 2541 nodes is manageable:

```python
for step in range(1, 401):
    ok = ops.analyze(1)
    if ok != 0:
        break
    odb.fetch_response_step()   # ~1M data points total — fast
```

This is the recommended pattern for static peridynamic models. Each `fetch_response_step` captures the current node coordinates/displacements into the ODB for later visualization.

### §12r — `ops.pattern("Plain", tag, tsTag)` Requires a Numeric Time Series Tag (v1.16.0)

Source: XMU Chapter12.3 conversion — `ops.pattern("Plain", 1, "Linear")` raised `OpenSeesError`.

#### Tcl Shorthand vs OpenSeesPy API

In Tcl, the time series type can be inlined as the third argument:

```tcl
# Tcl — type string "Linear" is accepted
pattern Plain 1 Linear {
    load 1 0.0 -100.0 0.0
}
```

In OpenSeesPy, the third argument is the **time series tag** (integer), not the type string. Passing `"Linear"` as the third argument causes `OpenSeesError: See stderr output`:

```python
# BROKEN — "Linear" is not a valid integer tag
ops.pattern("Plain", 1, "Linear")
```

You must create an explicit time series first and pass its tag:

```python
# CORRECT
ops.timeSeries("Linear", 1)    # create time series with tag 1
ops.pattern("Plain", 2, 1)    # pattern tag 2, references time series tag 1
ops.load(node, 0.0, -100.0, 0.0)
```

#### Why This Happens

The Tcl parser interprets `pattern Plain 1 Linear` as `pattern Plain 1 -timeSeries Linear` with a type-string shorthand. OpenSeesPy's Python bindings skip the Tcl parsing layer and directly call the C++ API where the third parameter is the integer time series tag. There is no implicit creation of a default linear time series.

#### Prevention

- Always create an explicit `ops.timeSeries("Linear", tsTag)` before calling `ops.pattern("Plain", patternTag, tsTag)`.
- Use separate tags for the time series and pattern to avoid ambiguity (e.g., `TS_LOAD = 1`, `PAT_LOAD = 2`).
- Never pass a string literal like `"Linear"` or `"Constant"` as the third argument to `ops.pattern()`.

### §12n — ODB Response Collection: `fetch_response_step()` Is NOT Optional (v1.15.0)

Source: XMU Chapter8.2 model debugging — deformed-shape plots missing after successful analysis.

#### Critical: Three Requirements for ODB Deformed-Shape Visualizations

`opst.post.CreateODB` with `save_nodal_resp=True` and `odb.fetch_response_step()` calls are BOTH required. Either alone produces an empty `RespStepData-1.odb` and all deformed plots fail with `FileNotFoundError: No parts found`.

The full lifecycle:

```
create_odb()                              → after model is fully built
  odb.save_model_data()                   → snapshot geometry
  odb.fetch_response_step()               → inside EVERY converged step loop
  odb.save_response()                     → once, at end (in post_process)
```

#### Missing Ingredient #1 — `save_nodal_resp=True` + `node_tags`

```python
# BROKEN — creates empty RespStepData directory
odb = opst.post.CreateODB(odb_tag=1)      # no save_nodal_resp, no node_tags
odb.save_model_data()

# CORRECT
odb = opst.post.CreateODB(
    odb_tag=1,
    model_update=False,
    save_nodal_resp=True,                 # MANDATORY for deformation plots
    node_tags=[1, 2, 3, 4],              # MANDATORY — which nodes to track
)
odb.save_model_data()
```

**Rule:** For any model that needs deformed-shape visualizations, `save_nodal_resp=True` and `node_tags` are non-negotiable. Omitting them creates the ODB directory structure but silently records nothing.

#### Missing Ingredient #2 — `fetch_response_step()` in the Analysis Loop

```python
# BROKEN — no response data collected (produces empty RespStepData)
ops.analyze(4000, 0.01)
odb.save_response()

# CORRECT — manual step loop with fetch
for i in range(4000):
    ok = ops.analyze(1, 0.01)
    if ok != 0:
        break
    odb.fetch_response_step()            # collect at EVERY converged step
odb.save_response()
```

**Rule:** `ops.analyze(N, dt)` runs N steps internally and provides no hook for `fetch_response_step()`. For models that must use raw `ops.analyze()` (e.g., `VariableTransient` consolidation, or `LoadControl` gravity exception per §3c/§10), you MUST use a manual step loop — `ops.analyze(1, dt)` repeated N times — and call `odb.fetch_response_step()` after each step.

#### Symptom

- Analysis completes without errors (model converges, stress/strain recorders work)
- `RespStepData-1.odb` directory is created but empty (0 bytes, no part files)
- `odb.save_response()` completes without error (reports "All responses data saved")
- `opst.vis.plotly.plot_nodal_responses()` raises `FileNotFoundError: No parts found in RespStepData-1.odb`
- If the plot call is wrapped in try/except, the error is swallowed and deformed plots silently never appear

#### Debugging Protocol

If deformed plots are missing after what appears to be a successful run:

1. Check `output/RespStepData-1.odb/` — if empty (no `.zarr`/`.nc` files), response collection didn't happen
2. Verify `CreateODB` was called with `save_nodal_resp=True` AND `node_tags`
3. Verify `fetch_response_step()` is called inside the step loop (not just once before/after)
4. Verify the manual step loop exists — `ops.analyze(N, dt)` without a manual loop is the most common cause
5. Remove try/except wrappers from post_process plot calls to expose the real error

#### Detection in Existing Models

Flag any model where:
- `CreateODB(odb_tag=...)` is called without `save_nodal_resp=True` — FAIL [ODB_NODAL_RESP]
- `ops.analyze(N, dt)` is used with N > 1 AND no manual step loop with `fetch_response_step()` — WARN [ODB_FETCH_MISSING]
- `save_response()` is called but `fetch_response_step()` never appears in the file — FAIL [ODB_NO_FETCH]
- `plot_nodal_responses()` calls are wrapped in bare `except Exception` — WARN [ODB_SILENT_FAIL]

**Why:** This was discovered during XMU Chapter8.2 verification. Both XMU Chapter8.1 and 8.2 inherited a pattern where `CreateODB` was initialized without `save_nodal_resp=True` and the dynamic analysis used `ops.analyze(4000, 0.01)` without a manual step loop. The analysis converged and file recorders worked fine, but the ODB directory was empty and all deformed-shape HTML files were silently missing. The fix touched two locations (create_odb + run_dynamic) in both models.

### §12s — Train-Bridge Interaction: Moving Wheel Load via SP Constraints, fix/sp Conflicts, Massless Nodes (v1.17.0)

Source: XMU Chapter13.1 refactoring (2D train-bridge interaction, 4 wheelsets, 2 bogies, 1 car body, 3000-step transient with wheel-rail contact via SP constraints).

#### 1. Wheel Position Verification — Cross-Check Against Actual Node Coordinates

The wheel-to-rail mapping in `setup_wheel_rail()` must use the **actual** wheel node coordinates, not computed from assumed vehicle geometry offsets.

**Bug found:** The `locs` array used offsets `[0.0, 2.5, 17.5, 20.0]` for the four wheels, but the actual wheel node positions relative to the first wheel were `[0.0, 2.5, 18.0, 20.5]`. The 17.5/18.0 and 20.0/20.5 mismatches caused wheels 3 and 4 to read rail displacements from the wrong element (~⅓ element offset).

```python
# BROKEN — assumed geometry offsets
locs = [pInitLocation + offset for offset in [0.0, 2.5, 17.5, 20.0]]

# CORRECT — derived from actual node positions
# Node 2003 at x=28.0, node 2001 at x=10.0 → offset = 18.0
# Node 2004 at x=30.5, node 2001 at x=10.0 → offset = 20.5
locs = [pInitLocation + offset for offset in [0.0, 2.5, 18.0, 20.5]]
```

**Rule:** Always verify node positions by computing from the `ops.node()` calls, not from assumed distances. Diff the computed offsets against any hard-coded locs arrays.

#### 2. `fix()` + `sp()` on the Same DOF Creates Conflicting Constraints

Applying both `ops.fix(node, 1, 0, 1)` (UX=0 homogeneous constraint) and `ops.sp(node, 1, 0.0)` (UX=0 pattern-imposed displacement) to the same DOF is redundant when values match, but **conflicting when one changes** (e.g., `sp` updated to `pVel * t` in a transient loop while `fix` still enforces UX=0).

```python
# BROKEN — conflicting constraints on UX
ops.fix(n, 1, 0, 1)          # UX permanently fixed at 0
# later in transient:
ops.sp(wn, 1, pVel_ * t)     # UX prescribed to pVel*t — conflicts!

# CORRECT — fix leaves UX free; SP controls it entirely
ops.fix(n, 0, 0, 1)          # UX free (controlled by SPs below)
ops.sp(wn, 1, pVel_ * t)     # UX prescribed via SP — no conflict
```

**Rule:** For DOFs controlled by SP constraints (e.g., moving wheel displacements in a transient loop), set the corresponding `fix()` DOF to 0 (free). Let the SP constraint be the sole prescribed-displacement mechanism.

#### 3. Massless Nodes in Beam Assemblies Cause Singular Mass Matrices

When `elasticBeamColumn` is used without `-mass` / `-cMass` flags, the element-end nodes have no mass. In transient dynamics, zero-mass nodes can produce singular or ill-conditioned mass matrices, causing solver convergence issues.

```python
# BROKEN — only centre nodes get mass; end nodes (2005, 2007, 2008, 2010) are massless
ops.mass(2006, Mb, Mb, JMb)
ops.mass(2009, Mb, Mb, JMb)
ops.element("elasticBeamColumn", 2001, 2005, 2006, ...)   # -mass not used

# CORRECT — distribute bogie mass across all 3 nodes per bogie
for n in [2005, 2006, 2007]:
    ops.mass(n, Mb / 3, Mb / 3, JMb / 3)
for n in [2008, 2009, 2010]:
    ops.mass(n, Mb / 3, Mb / 3, JMb / 3)
```

**Rule:** For any beam assembly where the beam elements use lumped mass (no `-cMass`), verify that **all** nodes in the assembly have mass assigned. Missing mass on end-nodes is a common source of numerical issues in transient analyses.

#### 4. SmartAnalyze Transient Works with Per-Step SP Constraint Modification

SmartAnalyze Transient is compatible with domain-level modifications between steps, such as `remove("sp")` + `sp()` for moving wheel constraints. The SP modifications must be applied before each `TransientAnalyze()` call:

```python
ops.integrator("Newmark", 0.5, 0.25)
analysis = opst.anlys.SmartAnalyze(analysis_type="Transient", ...)
segs = analysis.transient_split(N_TRANSIENT)
for i, _ in enumerate(segs):
    t = (i + 1) * pDeltT
    apply_wheel_constraints(t, wr_config)   # modify SPs
    ok = analysis.TransientAnalyze(pDeltT)  # then solve
    if ok < 0:
        break
    odb.fetch_response_step()
analysis.close()
```

**Rule:** Per-step domain modifications (SP constraints, element removal, material state changes) are applied BEFORE the analyze call in a SmartAnalyze loop. The domain state at the time of `TransientAnalyze()` is what gets used in the solver iteration.

#### 5. SP-Based Moving Wheel Contact as a WheelRail Element Alternative

When a custom WheelRail element is not available in the OpenSees build, wheel-rail contact can be approximated by imposing time-varying displacement constraints:
- UX = train velocity × time (constant-speed horizontal motion)
- UY = interpolated rail nodal displacement + rail irregularity profile

```python
def apply_wheel_constraints(t: float, config: dict) -> None:
    ops.loadConst("-pattern", PAT_WHEEL)
    for i, wn in enumerate(wheel_nodes):
        x = locs[i] + pVel * t
        ele_idx = int(x / rail_dx)
        xi = (x - ele_idx * rail_dx) / rail_dx
        uy_i = ops.nodeDisp(n_i, 2)
        uy_j = ops.nodeDisp(n_j, 2)
        uy_rail = (1.0 - xi) * uy_i + xi * uy_j
        irreg = float(np.interp(x, irreg_data[:, 0], irreg_data[:, 1]))
        ops.remove("sp", wn, 1)
        ops.remove("sp", wn, 2)
        ops.sp(wn, 1, pVel * t)
        ops.sp(wn, 2, uy_rail + irreg)
```

**Limitation:** This is a one-way coupling (wheel follows rail) — there is no contact-force feedback from wheel to rail. Full wheel-rail interaction requires the custom WheelRail element.

#### 6. SI-Unit Models Can Still Conform to AGENT.md Structure

When SI units are intentionally retained (e.g., the WheelRail element expects m-kg-N-Pa), the AGENT.md structural conventions still apply:
- Section banners and ordering
- Tag Registry with named constants
- Parameter section with all dimensional values documented
- `opstool` visualization stages (V1–V4)
- `SmartAnalyze` for solver loops (when compatible)
- `CreateODB` for output
- `opensees_catalogue.json` entry
- Folder name matching UniqueID

The audit items for unit conversion (§5 items 5-6) are SKIPPED, not FAILED, when the catalogue explicitly documents the SI retention rationale.

### §12t — 3D Single-Wheelset on Rigid Track: Rigid-Body Modes, Post-loadConst SP Patterns, SmartAnalyze with Per-Step SP Updates (v1.18.0)

Source: XMU Chapter13.2 conversion (3D single-wheelset on rigid track, original WheelRail custom element replaced with SP-based wheel-rail contact, 6000-step transient).

#### 1. Eliminate Rigid-Body Modes with a Soft Spring

When a wheelset is connected by stiff "rigid" beams and a DOF (e.g., UY translation) has no stiffness from any element, the system matrix is singular. Static solvers fail with convergence errors even with `constraints("Transformation")`.

**Fix:** Add a 1 N/m `zeroLength` spring in the problematic DOF between the free node and a fixed auxiliary node:

```python
ops.node(NODE_UY_SPRING, 0, 0, R0)
ops.fix(NODE_UY_SPRING, 1, 1, 1, 1, 1, 1)
ops.uniaxialMaterial("Elastic", MAT_UY_SPRING, 1.0)     # 1 N/m — negligible
ops.element("zeroLength", ELE_UY_SPRING, NODE_WHEEL_CENTER, NODE_UY_SPRING,
            "-mat", MAT_UY_SPRING, "-dir", 2)
```

- Natural frequency for a 933 kg wheelset: √(1/933)/(2π) ≈ 0.005 Hz — does not affect dynamics
- Use `constraints("Plain")` for static phase to avoid ill-conditioning from stiff beams under Transformation constraints
- Higher test tolerance (1.0e-1) and more steps (100) help convergence

#### 2. Moving SP Constraints Must Be Created AFTER `loadConst`

`ops.loadConst("-time", 0.0)` freezes **all** existing load patterns, including SP constraints. A pattern created BEFORE `loadConst` cannot have its SPs removed or updated afterward.

```python
# BROKEN — pattern created before loadConst
setup_wheel_sp()           # creates pattern with Constant TS, SP(UX=0)
ops.loadConst("-time", 0.0)  # freezes the wheel SP pattern
# later:
ops.remove("sp", ...)       # ERROR — pattern is frozen

# CORRECT — pattern created after loadConst
ops.loadConst("-time", 0.0)
ops.wipeAnalysis()
setup_wheel_sp()            # creates pattern AFTER loadConst — NOT frozen
# later:
ops.remove("sp", ...)       # OK — pattern is modifiable
```

**Rule:** Any pattern that needs per-step modification (e.g., moving displacement constraints) MUST be created after `ops.loadConst()`. Only gravity and lateral load patterns should exist before `loadConst`.

#### 3. `ops.timeSeries` Tag Collisions After `wipeAnalysis`

Creating a `timeSeries` with a low tag number (e.g., tag 4) after `loadConst` + `wipeAnalysis` can fail with `"TimeSeries *getTimeSeries(int tag) - none found with tag: N"`. This occurs even though `wipeAnalysis` nominally only clears analysis objects, not model objects.

**Fix:** Use higher tag numbers (e.g., 10+) for time series and patterns created after `loadConst`. The collision may be due to internal OpenSeesPy tag namespaces that overlap with low tag values.

#### 4. SmartAnalyze Transient with Per-Step SP Modification

SmartAnalyze Transient supports domain modifications between steps. Apply `ops.remove("sp")` + `ops.sp()` before each `TransientAnalyze()` call:

```python
for i, _ in enumerate(segs):
    update_wheel_sp(i * dT)          # remove old SP, add new UX = pVel * t
    ok = analysis.TransientAnalyze(dT)
    ...

def update_wheel_sp(t: float) -> None:
    ops.remove("sp", PAT_WHEEL, NODE_WHEEL_CENTER, 1)
    ops.sp(NODE_WHEEL_CENTER, 1, pVel * t, PAT_WHEEL)
```

The domain state at the time of `TransientAnalyze()` is what the solver iteration uses. SP modifications MUST use a non-frozen pattern (created after `loadConst`).

#### 5. Auxiliary Nodes Must Be Created After `ops.model()`

Auxiliary nodes (e.g., the fixed UY spring anchor node) should be created alongside the main model nodes, inside `build_wheelset_nodes()` or equivalent. Their `ops.fix()` constraints belong in the BCs section. This keeps the model topology complete before element definition.

### §12u — opstool CreateODB and plot_nodal_responses: node_tags Limits Deformation Visualization (v1.19.0)

Source: XMU Chapter13.2 debugging (3D single-wheelset, ~400 rail nodes, 5 tracked wheel nodes, 6000-step transient).

#### 1. `node_tags` in CreateODB Breaks Deformation Plots

`plot_nodal_responses()` loads ALL node coordinates from the model data (`save_model_data()`) but only has deformation data for nodes tracked by `node_tags`. When these sets differ, the deformation overlay fails:

```
ValueError: operands could not be broadcast together with shapes (5,3) (406,3)
```

The function does NOT accept a `node_tags` parameter — it always attempts to render the full mesh.

**Fix:** Omit `node_tags` from `CreateODB` when deformation visualization is needed, so ALL nodes are tracked:

```python
# BROKEN — only 5 nodes tracked; plot_nodal_responses can't render
odb = opst.post.CreateODB(odb_tag=1, save_nodal_resp=True,
    node_tags=[1, 51, 1001, 1051, 2001])

# CORRECT — omit node_tags for full mesh tracking
odb = opst.post.CreateODB(odb_tag=1, save_nodal_resp=True)
```

**Memory impact:** For ~406 nodes × 6001 steps × 6 DOFs × float32 ≈ 58 MB — manageable for most models.

If filtering is absolutely required (e.g., extreme mesh sizes), the trade-off must be documented: deformation plots and sliders will be unavailable.

#### 2. `save_frame_resp` Defaults to True — Can Exhaust Memory

With `save_frame_resp=True` (the default), `save_response()` builds arrays of shape `(n_steps+1, n_elements, n_resp_components)`. For 402 beam elements × 6001 steps × 6 components × float32 ≈ 55 MB per call. Combined with nodal data, this can exceed available memory.

**Fix:** Explicitly set `save_frame_resp=False` when only nodal displacements are needed:

```python
odb = opst.post.CreateODB(odb_tag=1,
    save_nodal_resp=True,
    save_frame_resp=False,   # ← disable unless element forces are needed
    save_truss_resp=False,
)
```

**Rule:** Always review the default ODB flags. `save_nodal_resp=True` alone is not sufficient — the other `save_*_resp` flags default to True and silently accumulate element data that may never be plotted.

### §12v — `beamWithHinges` Internal Section Tags Break CreateODB; SmartAnalyze Convergence Tuning (v1.20.0)

Source: Citiner conversion (RC cantilever column, fiber-section beamWithHinges, cyclic pushover, 23 segments).

#### 1. `beamWithHinges` + `save_frame_resp=True` Causes `sectionForceDeformation(tag=0)` Error

`beamWithHinges` creates internal section objects that are accessed by a 1-based index within the element, **not** by the user-assigned fiber-section tag. When `CreateODB` attempts to read section responses via `ops.sectionForceDeformation(tag)`, it looks for tag `0` (the first auto-indexed section) instead of the user's section tag (e.g. `SEC_COL = 1`), producing:

```
SectionForceDeformation *getSectionForceDeformation(int tag) - none found with tag: 0
ERROR classType - section with tag 0 not found
```

**Fix:** Set `save_frame_resp=False` in `CreateODB`:

```python
odb = opst.post.CreateODB(odb_tag=1,
    save_frame_resp=False,   # beamWithHinges internal sections lack user-visible tags
)
```

Nodal response tracking for deformed-shape visualisation still works. If element section forces are needed, consider `nonlinearBeamColumn` or `dispBeamColumn` instead of `beamWithHinges`.

#### 2. Manual `ops.test()`/`ops.algorithm()` Before SmartAnalyze Causes Issues

Calling `ops.test("EnergyIncr", 1.0e-2, 200)` and `ops.algorithm("Newton")` **before** instantiating `SmartAnalyze` interferes with SmartAnalyze's internal test/algorithm management. Per AGENT.md §3c:

> `test()` and `algorithm()` are managed internally by SmartAnalyze — do not call them manually.

**Fix:** Remove manual `ops.test()` and `ops.algorithm()` calls before SmartAnalyze. SmartAnalyze selects the appropriate test and algorithm automatically based on its `algoTypes` list.

#### 3. Default SmartAnalyze Settings Are Insufficient for RC Pushover

SmartAnalyze with `algoTypes=[40, 10, 20, 30]` (no `relaxation`, no `tryAddTestTimes`) converges for small elastic pushes but fails at moderate drifts (~1.7% for RC columns under cyclic PDelta). The AGENT.md §3c pushover pattern provides the correct settings:

```python
analysis = opst.anlys.SmartAnalyze(
    analysis_type="Static",
    tryAlterAlgoTypes=True,
    algoTypes=[40, 10, 20, 30, 50, 60],    # KrylovNewton → Newton → Newton-initial → ModifiedNewton → NewtonLineSearch → BFGS
    tryAddTestTimes=True,
    testIterTimesMore=[50, 100],
    relaxation=0.5,
    minStep=1.0e-4,
)
```

**Rule:** Always use the full algorithm fallback list + `relaxation=0.5` + `tryAddTestTimes=True` for displacement-controlled RC pushover.

#### 4. `constraints("Transformation")` for SmartAnalyze Pushover

The Tcl templates use `constraints("Plain")` throughout. SmartAnalyze pushover with PDelta and cyclic reversals converges better with `constraints("Transformation")`. Use `"Plain"` only for the manual LoadControl gravity phase.

#### 5. Negative Segments in Cyclic Pushover: Loop vs static_split

`analysis.static_split(protocol, maxStep)` is designed for monotonic protocols with positive targets. For cyclic segments with negative `remaining`, use a manual loop calling `StaticAnalyze(node, dof, seg=dU)` repeatedly with constant `dU = remaining / n_steps` (positive or negative). This matches the OReilly2019 cyclic pattern.

### §12w — CookDustin F12-D100: Tcl-Parsing RC Frame with IMKPeakOriented Hinges, SmartAnalyze Hang Prevention (v1.21.0)

Source: CookDustin F12-D100 conversion (2D 4-bay × 12-story RC SMF with concentrated IMKPeakOriented plasticity hinges, leaning column, Tcl model-only, lb-in-psi → N-mm-MPa).

#### 1. Tcl Parsing Over CSV Reconstruction for Cracked-Section Properties

The Tcl `elasticBeamColumn` commands contain A, E, Iz values that differ from the CSV `element_table` gross-section properties (Iz factor ≈1.1 — cracked/effective section ratio computed by the SimCenter pipeline). Parsing the Tcl directly guarantees exact match with the reference; CSV values would introduce systematic stiffness errors.

```python
# Parsing approach: read model.tcl line-by-line for all element/material/node/BC data
tcl_data = _parse_tcl(TCL_PATH)
# CSVs used only for non-structural data (story gravity loads from story.csv)
```

**Rule:** When Tcl and CSVs both exist and the Tcl values represent post-processed (cracked/effective) section properties, parse the Tcl. Reserve CSVs for metadata the Tcl doesn't contain.

#### 2. IMKPeakOriented Unit Conversion: Only K₀ and Mₚ Are Dimensional

IMKPeakOriented has 23 float parameters. Of these, only two carry physical dimensions:
- **K₀** (index 0): rotational stiffness — lb·in/rad → N·mm/rad (× 112.98)
- **Mₚ** (indices 4, 10): positive/negative plastic moment — lb·in → N·mm (× 112.98)

All other parameters (post-yield stiffness ratio, ductility capacities, cyclic degradation parameters) are **dimensionless ratios** and pass through unconverted.

```python
cvals = list(vals)
if len(cvals) >= 1:
    cvals[0] *= LBIN2NMM   # K0
if len(cvals) >= 5:
    cvals[4] *= LBIN2NMM   # Mp positive
if len(cvals) >= 11:
    cvals[10] *= LBIN2NMM  # Mp negative
```

**Rule:** For IMK/hysteretic material models, identify which parameters are stiffness/strength (need unit conversion) and which are dimensionless shape parameters (pass through). A wholesale conversion of all parameters introduces errors.

#### 3. SmartAnalyze Aggressive Retry Settings Cause Hangs on IMK Hinge Softening

SmartAnalyze's `tryAddTestTimes=True` + `relaxation=0.5` + `minStep=1.0e-4` triggers indefinite retry when an IMKPeakOriented hinge enters its post-peak descending branch. The solver subdivides steps down to 1e-4 of the original increment, retrying all 6 algorithm types at each subdivision, never converging.

**Fix:** Keep SmartAnalyze simple for RC frame pushover — just `tryAlterAlgoTypes=True` with `algoTypes=[40, 10, 20, 30]` (KrylovNewton → Newton → ModifiedNewton → NewtonLineSearch). Fail fast and report divergence:

```python
analysis = opst.anlys.SmartAnalyze(
    analysis_type="Static",
    tryAlterAlgoTypes=True,
    algoTypes=[40, 10, 20, 30],    # no tryAddTestTimes, relaxation, or minStep
)
```

**Symptom of hang:** SmartAnalyze progress bar freezes (e.g., 17/200) with no error message; user must Ctrl+C; `save_response()` and all subsequent output never execute.

**Rule:** Use the full aggressive retry settings (§12v-3) only for models that have demonstrated convergence issues with the simple settings. For IMK hinge models that can genuinely soften (descending branch), the simple settings let the analysis report failure immediately instead of hanging.

#### 4. Do NOT Set `ops.constraints`/`numberer`/`system` Before SmartAnalyze After Manual Gravity

After `ops.analysis("Static")` in the manual LoadControl gravity phase, the constraint/numberer/system handlers are frozen. Calling them again before SmartAnalyze produces `"WARNING can't set handler after analysis is created"` and has no effect. SmartAnalyze sets these handlers internally.

```python
# Gravity (manual LoadControl — permitted exception)
ops.analysis("Static")
for _ in range(N_GRAV_STEPS):
    ops.analyze(1)
    odb.fetch_response_step()
ops.loadConst("-time", 0.0)

# Pushover (SmartAnalyze) — NO manual constraints/numberer/system calls
analysis = opst.anlys.SmartAnalyze(analysis_type="Static", ...)
```

**Rule:** After any manual `ops.analysis()` call, do NOT set handlers again before SmartAnalyze. SmartAnalyze handles its own handler setup.

#### 5. `set_odb_path()` Must Be Called Before `plot_nodal_responses()` in `post_process`

The ODB path is set in `create_odb()` inside `run_analysis()`. When `post_process()` calls `vis_defo()` → `plot_nodal_responses()`, the path may not be active. Always call `opst.post.set_odb_path(str(output_dir))` in `post_process` before any visualization function that reads ODB data.

#### 6. `vis_defo()` Positional Arg Pitfall

`vis_defo(output_dir: Path, filename: str = "vis_05_deformed.html", odb_tag: int = 1, ...)` — passing the ODB object as the second positional argument maps to `filename`, not `odb_tag`. The call must use keyword arguments:

```python
# BROKEN — odb object passed as filename
vis_defo(output_dir, odb, resp_dof="UX")

# CORRECT — odb_tag as keyword; odb object not needed by vis_defo
vis_defo(output_dir, odb_tag="F12-D100", resp_dof="UX")
```

#### 7. Verify Source Units Carefully: lb/in/psi vs kip/in/ksi

The original Tcl uses lb, in, psi (not kip). Verify by cross-checking E against concrete code formula: E = 57,000√fc' in psi. For fc' = 7000 psi, E = 57,000√7000 ≈ 4,768,962 psi — matches the Tcl value. For kip units, this would be 4,769 ksi, which is implausibly high.

**Rule:** When converting imperial Tcl models, always verify the base unit system by cross-checking a known physical relationship (E vs fc', steel E = 29,000 ksi, etc.) against the Tcl values.

#### 8. `cvals = list(vals)` Must Be Assigned Before the `if` Block

When processing `uniaxialMaterial` commands in a loop where only some material types need unit conversion, the converted-variables list must be initialised unconditionally:

```python
# BROKEN — cvals is only defined inside the if block
for tag, mtype, vals in tcl_data["uniaxial_mat"]:
    if mtype == "IMKPeakOriented":
        cvals = list(vals)      # ← only assigned for IMK
        cvals[0] *= LBIN2NMM
    ops.uniaxialMaterial(mtype, tag, *cvals)  # UnboundLocalError for Elastic

# CORRECT — cvals initialised before the if block
for tag, mtype, vals in tcl_data["uniaxial_mat"]:
    cvals = list(vals)           # ← always assigned
    if mtype == "IMKPeakOriented":
        cvals[0] *= LBIN2NMM
    ops.uniaxialMaterial(mtype, tag, *cvals)
```

**Rule:** In any loop where a subset of items needs transformation, initialise the working variable unconditionally before the conditional logic.

#### 9. `CreateODB` Has No `save_eles_resp` Parameter

`opst.post.CreateODB` does NOT accept a generic `save_eles_resp` flag. Each element type has its own dedicated flag:

```python
# BROKEN — raises KeyError: "Incorrect parameter save_eles_resp"
odb = opst.post.CreateODB(odb_tag=1, save_eles_resp=True)

# CORRECT — use element-type-specific flags
odb = opst.post.CreateODB(odb_tag=1,
    save_nodal_resp=True,
    save_frame_resp=True,   # elasticBeamColumn, dispBeamColumn, etc.
    save_link_resp=True,    # zeroLength, twoNodeLink, etc.
    save_truss_resp=True,   # truss elements
)
```

**Valid flags** (from opstool 1.0.26): `elastic_frame_sec_points`, `interpolate_beam_disp`, `section_response_dof`, `compute_mechanical_measures`, `project_gauss_to_nodes`, `save_nodal_resp`, `save_frame_resp`, `save_truss_resp`, `save_link_resp`, `save_shell_resp`, `save_fiber_sec_resp`, `save_plane_resp`, `save_brick_resp`, `save_contact_resp`, `save_sensitivity_resp`, `node_tags`, `frame_tags`, `truss_tags`, `link_tags`, `shell_tags`, `fiber_ele_tags`, `plane_tags`, `brick_tags`, `contact_tags`, `sensitivity_para_tags`.

**Rule:** Always use element-type-specific `save_*_resp` flags. The generic `save_eles_resp` does not exist.

### §12x — Tcl `forceBeamColumn HingeRadau` Parsing: Parameter Swap + Integration Type Mismatch (v1.22.0)

Source: BhatZeeshanManzoor G+4 RC infilled frame conversion (3D, 5-story, IMKPeakOriented + Pinching4 + fiber sections, STKO/SimCenter Tcl → Python).

#### 1. The Tcl `HingeRadau` Format: `$secTag $lpI $nIpI $lpJ $nIpJ`

In STKO-exported Tcl, `forceBeamColumn` with the `HingeRadau` flag follows this argument order:

```tcl
element forceBeamColumn $eleTag $iNode $jNode $transfTag HingeRadau $secTag $lpI $nIpI $lpJ $nIpJ
```

The parameters after `HingeRadau` are: **section tag, hinge length I, number of IPs I, hinge length J, number of IPs J**.

The last value (`nIpJ`) looks like an IP count but can be mistaken for a section tag by a naive parser, especially when the IP counts happen to fall in the same numeric range as valid section tags (e.g., `nIpJ=7` and fiber section 7 both exist).

#### 2. The Bug: `secTag` and `nIpJ` Swapped, `Lobatto` Replaces `HingeRadau`

The parser swapped the first and last HingeRadau parameters, then created the wrong integration type:

```python
# BROKEN — secTag and nIpJ swapped, Lobatto instead of HingeRadau
np_i = int(parts[7])       # actually secTag → mislabeled
lp_i = float(parts[8])     # lpI ✓
np_j = int(parts[9])       # actually nIpI → mislabeled
lp_j = float(parts[10])    # lpJ ✓
sec_tag = int(parts[11])   # actually nIpJ → WRONG VALUE for section tag!
ops.beamIntegration("Lobatto", int_tag, sec_tag, 5)  # uses nIpJ as section tag!
```

**Three simultaneous failures:**
1. `sec_tag` receives `nIpJ` (e.g., 7) instead of the real section tag (e.g., 6)
2. `beamIntegration("Lobatto", ...)` is used instead of `beamIntegration("HingeRadau", ...)` — Lobatto distributes IPs along the full element; HingeRadau concentrates them in the hinge regions
3. `5` is hardcoded as the number of IPs, discarding the hinge length parameters entirely

#### 3. The Fix: Correct Parameter Extraction + HingeRadau Integration

```python
# CORRECT — secTag is parts[7], nIpJ is parts[11]
sec_tag = int(parts[7])      # secTag
lp_i = float(parts[8])       # lpI
# parts[9]  = nIpI — not a beamIntegration HingeRadau parameter
lp_j = float(parts[10])      # lpJ
# parts[11] = nIpJ — not a beamIntegration HingeRadau parameter
int_key = (sec_tag, lp_i, lp_j)
# HingeRadau: (tag, secTagI, lpI, secTagJ, lpJ, secTagE)
ops.beamIntegration("HingeRadau", int_tag, sec_tag, lp_i, sec_tag, lp_j, sec_tag)
ops.element("forceBeamColumn", tag, iNode, jNode, transfTag, int_tag)
```

**`beamIntegration("HingeRadau", ...)` signature (OpenSeesPy):**
```python
ops.beamIntegration("HingeRadau", tag, secTagI, lpI, secTagJ, lpJ, secTagE)
```
- `secTagI`: section tag for hinge at end I
- `lpI`: plastic hinge length at end I
- `secTagJ`: section tag for hinge at end J
- `lpJ`: plastic hinge length at end J
- `secTagE`: section tag for the elastic interior

This differs from the Tcl documentation which often lists `(secTagE, lpI, lpJ, secTagH)` — in OpenSeesPy, each section tag comes **before** its corresponding hinge length, and all three section positions (I-hinge, J-hinge, elastic interior) are explicit. For typical fiber-section models, all three use the same section tag.

The `nIpI`/`nIpJ` values from the Tcl **do not map to `beamIntegration HingeRadau` parameters** — the Tcl element-level `-HingeRadau` flag and the `beamIntegration HingeRadau` object have different signatures. `beamIntegration HingeRadau` determines the number of Radau integration points per hinge internally (2 per hinge region is typical). The Tcl `nIpI`/`nIpJ` parameters are silently dropped in the Python translation.

**Impact if unfixed:** Every `forceBeamColumn` with HingeRadau gets:
- Lobatto integration with Gaussian-like IP distribution (no hinge concentration) → plasticity can't localize correctly at beam ends
- The wrong fiber section (nIpJ instead of secTag) → potentially a non-existent section tag or the wrong material model
- Fixed 5 IPs regardless of element length or hinge length
- Element stiffness and nonlinear response are fundamentally incorrect

#### 4. Verification Methodology: Cross-Check Against Known Section Tags

To resolve parameter ordering ambiguity when both candidate values map to valid section tags, cross-check with a known format. For this model, the presence of both fiber section 6 and fiber section 7, and both section 18 and section 19, made either interpretation internally consistent. The correct ordering was confirmed by:
1. Checking that the `-HingeRadau` element-level flag is documented as `$secTag $lpI $nIpI $lpJ $nIpJ` in OpenSees source
2. Verifying that STKO exports follow this convention
3. Confirming that `beamIntegration HingeRadau` accepts `(secTagE, lpI, lpJ, secTagH)` — NOT `(nIpI, lpI, nIpJ, lpJ, secTagH)`

**Rule:** When parsing Tcl element commands with inline integration flags, always verify the Tcl argument order against the corresponding OpenSeesPy `beamIntegration` signature. They are often **different APIs** — the Tcl element wrapper accepts parameters that the standalone `beamIntegration` object does not.

#### 5. `_force_beam()` Helper Uses Tcl Syntax in Python — Never Works

A helper function defined but never called still merits flagging:

```python
# BROKEN — OpenSeesPy forceBeamColumn takes an integration tag, not inline flags
def _force_beam(elem_tag, n1, n2, transf_tag, sec_tag, hinge_len=225.0, hinge_ip=6):
    ops.element("forceBeamColumn", elem_tag, n1, n2, transf_tag,
                "-HingeRadau", hinge_ip, hinge_len, hinge_ip, hinge_len, sec_tag)
```

In OpenSeesPy, `forceBeamColumn` signature is `(tag, iNode, jNode, transfTag, integTag)`. The `-HingeRadau` inline flag is Tcl-only — it would raise `OpenSeesError` if called. Always create a `beamIntegration` object and pass its tag.

**Rule:** Any helper that calls `ops.element()` with Tcl-style dash-prefixed flags (`-HingeRadau`, `-integration`, `-sections`) is dead code in OpenSeesPy — these flags only work in the Tcl interpreter.

#### 6. Penalty Constraints + Rigid Diaphragms → Singular/Ill-Conditioned System

STKO-exported Tcl often uses `constraints("Penalty", 1e13, 1e13)` to enforce multi-point constraints (rigidLinks, rigidDiaphragms, equalDOFs). Combined with the model's own very stiff elements (zeroLength with 1e13 stiffness), this creates an extremely ill-conditioned system:

```
NormDispIncr: current Norm: 1.62  Norm deltaR: 4.06e9
```

The displacement correction is tiny (1.62) but the residual force is enormous (4e9) — the hallmark of penalty-method failure. Tiny constraint violations produce huge penalty forces that dominate the residual.

**Fix:** Use `constraints("Transformation")` instead. Transformation handles multi-point constraints by variable elimination (not penalty springs), avoiding the ill-conditioning entirely:

```python
# BROKEN — penalty + stiff elements = ill-conditioned system
ops.constraints("Penalty", 1e13, 1e13)

# CORRECT — variable elimination, no penalty springs
ops.constraints("Transformation")
```

This applies to both gravity (static LoadControl) and transient analysis phases. The fix has no effect on results — it only changes how constraints are enforced numerically.

**Rule:** When converting STKO/SimCenter Tcl models, always replace `constraints("Penalty", ...)` with `constraints("Transformation")`. The only exception is when the model explicitly requires penalty for a specific reason (e.g., Lagrange multipliers are incompatible with the chosen solver).

#### 7. `beamIntegration("HingeRadau")` + `forceBeamColumn` = State Determination Failure

Even with the correct signature, `beamIntegration("HingeRadau", ...)` causes forceBeamColumn's flexibility-based state determination to fail on the first gravity step:

```
ForceBeamColumn3d::update - failed to get compatible element forces & deformations
for element: 258 (dW: << -2348.93, dW0: 4.40778e+15)
```

The Tcl element-level `-HingeRadau` flag creates an integration with a different internal IP distribution than the standalone `beamIntegration("HingeRadau")` object. The Tcl flag uses `nIpI`/`nIpJ` to control the number of integration points in each hinge region; the standalone `beamIntegration` determines this internally (typically 2 Radau points per hinge + fixed interior points), which may be insufficient for forceBeamColumn's force interpolation functions to represent distributed gravity loads.

**Fix:** Use Lobatto integration with the correct section tag, carrying forward the max of `nIpI`/`nIpJ` from the Tcl as the Lobatto IP count:

```python
# CORRECT — Lobatto with Tcl's IP count, correct section tag
sec_tag = int(parts[7])                           # $secTag (was swapped with nIpJ)
n_ip = max(int(parts[9]), int(parts[11]))         # nIpI, nIpJ → IP count
ops.beamIntegration("Lobatto", int_tag, sec_tag, n_ip)
ops.element("forceBeamColumn", tag, iNode, jNode, transfTag, int_tag)
```

This accepts the ~10% stiffness approximation documented in §12e (all IPs share one section vs Tcl's per-IP sections). The section tag fix is more critical than the integration type — using the wrong section tag (nIpJ instead of secTag) causes fundamentally incorrect element response.

**Symptom of HingeRadau failure:** forceBeamColumn state determination fails at the very first gravity step with `dW0` on the order of 10¹⁵ — the initial energy norm is astronomically large, indicating the flexibility-based iteration starts from an incompatible state.

**Rule:** For STKO/SimCenter Tcl models, parse the HingeRadau element flag to extract secTag correctly. Use `beamIntegration("HingeRadau", tag, secTag, lpI, secTag, lpJ, secTag)` + `dispBeamColumn`. The `nIpI`/`nIpJ` from the Tcl are dropped (cannot be mapped to `beamIntegration HingeRadau`). The hinge lengths (`lpI`/`lpJ`, typically 200-225 mm) are preserved via the `HingeRadau` beamIntegration. Prefer `HingeRadau` over `Lobatto` for dispBeamColumn — it concentrates IPs at element ends (correct for plasticity) and uses the Tcl hinge-length data.

#### 8. `dispBeamColumn` + Fiber Sections = Newton Tangent Ill-Conditioning

Even after fixing the element type and integration, any Newton-type algorithm (Newton, KrylovNewton, NewtonLineSearch) diverges within 1-2 gravity steps:

```
WARNING: numeric analysis returns 1 -- Umfpackgenlinsolver::solve
StaticAnalysis::analyze() - the Algorithm failed at step: 0 with domain at load factor 0.2
```

The tangent stiffness matrix becomes numerically singular after the first converged step. This is NOT caused by:
- Concrete tensile cracking (observed even with purely linear-elastic materials)
- P-Delta geometric nonlinearity (observed with `Linear` geomTransf)
- Constraint handler choice (observed with both `Penalty` and `Transformation`)
- HingeRadau vs Lobatto integration (both fail identically)

The root cause appears to be fundamental ill-conditioning in the 3D dispBeamColumn fiber-section tangent when combined with rigidDiaphragm constraints and stiff zeroLength joint elements (stiffness ratio ~10^7-10^8 between zeroLength 1e13 and fiber beam ~1e6 N/mm).

#### 9. ModifiedNewton + Penalty Gravity Strategy

**Symptom:** Gravity analysis with Newton/KrylovNewton diverges. ModifiedNewton converges stably but slowly.

**Fix — ModifiedNewton with relaxed tolerance:**

```python
ops.constraints("Penalty", 1.0e13, 1.0e13)
ops.numberer("RCM")
ops.system("UmfPack")
ops.test("NormDispIncr", 0.01, 500, 2)  # relaxed tolerance
ops.algorithm("ModifiedNewton")           # initial elastic stiffness throughout
ops.integrator("LoadControl", 0.02)      # 50 small steps
ops.analysis("Static")
```

**Why this works:** ModifiedNewton uses the initial (elastic) stiffness for all iterations. This stiffness is well-conditioned (no cracked fibers, no softened materials). Each iteration direction is stable, even for ill-conditioned tangent problems. The trade-off is slow convergence — early steps converge in 3-10 iterations, later steps need 30-100+ iterations.

**Concrete tensile strength:** Define `Concrete02` with elevated tensile strength (`ft = 20.0` instead of physical ~3.0 MPa) for the entire analysis. This suppresses premature tensile cracking that would destabilise even ModifiedNewton. Post-cracking response is governed by steel reinforcement, so the exact `ft` value has negligible effect on global hysteretic behavior.

**IMPORTANT — materials cannot be redefined in OpenSeesPy:**
```python
ops.uniaxialMaterial("Concrete02", 1, ...)  # defines tag 1
ops.uniaxialMaterial("Concrete02", 1, ...)  # ERROR: MapOfTaggedObjects refuses duplicate
```

`ops.remove("uniaxialMaterial", tag)` is also NOT supported. Materials must be defined once with the desired parameters — there is no mechanism to modify them later for different analysis phases (e.g., gravity vs transient). The same `ft` value persists through the entire analysis.

**Current limitation:** ModifiedNewton reaches ~66% of full gravity (load factor 0.66 with 50 steps). At ~68% load factor, even ModifiedNewton diverges (`norm = inf` after 300+ iterations), likely due to material compressive softening (Concrete02 nonlinear compression + Pinching4 infill strut degradation). For models needing full gravity, further investigation is required — possible approaches include two-phase gravity application or displacement-controlled loading.

**Rule:** For 3D fiber-section models with large stiffness contrasts (zeroLength joints, rigidDiaphragm):
1. Use `Penalty(1e13, 1e13)` constraints — Penalty springs regularise the stiffness matrix better than `Transformation` elimination
2. Use `ModifiedNewton` algorithm — avoids Newton tangent ill-conditioning
3. Use `NormDispIncr` test with relaxed tolerance (0.01) and many iterations (500)
4. Use small load steps (0.02) — the consistent step size makes ModifiedNewton's convergence predictable
5. Define Concrete02 with elevated `ft` from the start — materials cannot be redefined later
6. Use `dispBeamColumn` with `beamIntegration("HingeRadau", ...)` preserving hinge lengths — avoids forceBeamColumn state determination failures while keeping hinge-concentrated IP distribution

### §12y — opstool `tcl2py`: Actual Execution, MP Workarounds, and Analysis-Stripping Strategy (v1.23.0)

Source: BhatZeeshanManzoor G+4 RC infilled frame, STKO/SimCenter Tcl → Python conversion (2026-06-25).

#### 1. `tcl2py` Executes OpenSees Commands During Conversion — NOT Pure Syntax Translation

`opstool.pre.tcl2py()` evaluates Tcl source files through a Tcl interpreter that mirrors OpenSees commands to OpenSeesPy. During evaluation, it **actually runs** `ops.analyze()` calls. This has two critical implications:

- **Convergence failures block conversion.** If the source Tcl's gravity analysis doesn't converge in OpenSeesPy, tcl2py will raise a TclError and halt — producing zero output.
- **The converted output reproduces the source approach literally.** tcl2py does NOT fix known OpenSeesPy incompatibilities (e.g., forceBeamColumn state determination, Newton ill-conditioning, Concrete02 ft values). It faithfully translates what the Tcl source specifies.

```python
# tcl2py translates this Tcl:
# element forceBeamColumn 23 268 16 23 -HingeRadau 6 200.0 5 200.0 7
# ...to:
ops.beamIntegration('HingeRadau', 23, *[6, 200.0, 6, 200.0, 7])
ops.element('forceBeamColumn', 23, 268, 16, 23, 23)
# Same forceBeamColumn + HingeRadau that fails in OpenSeesPy (§12x).
```

**Rule:** tcl2py is a literal translator, not a fixer. Expect every source-Tcl convergence problem to be faithfully reproduced in the converted output.

#### 2. OpenSeesMP Code Blocks Conversion

STKO-generated analysis scripts contain OpenSeesMP (parallel processing) code that tcl2py cannot evaluate:

```tcl
set param_id [getPID]       # getPID() returns None in standard OpenSeesPy → Tcl evaluation fails
set num_proc [getNP]        # getNP() returns None → "None must be equal to 40" error
```

**Workaround — patch the source Tcl before feeding to tcl2py:**

```tcl
# Replace:
set param_id [getPID]
# With:
set param_id 0

# Comment out MP processor-count check:
# set num_proc [getNP]
# set num_param [expr int($num_dt/2)]
# if {$num_proc != $num_param} { ... }
set num_proc 1

# Replace [getPID] in recorder/monitor filenames:
# "./monitor_[getPID].plt" → "./monitor_0.plt"
```

**Also remove Tcl MP synchronization primitives:**
```tcl
# barrier / after 1000 set end 1 / vwait end
# These are Tcl/Tk event-loop commands that may not work in tcl2py's interpreter.
# Replace with simple puts statements.
```

#### 3. Analysis Execution Loops Must Be Commented Out

tcl2py evaluates all Tcl code including `for` loops and `while 1` loops that drive the analysis. When `ops.analyze()` fails inside these loops, the Tcl `error` statement halts the entire conversion.

**Workaround — comment out execution loops before conversion:**

The two execution blocks that must be stripped:

1. **Gravity analysis loop** (`for {set incr 1} {$incr <= $num_incr} {incr incr}`) — calls `analyze 1` inside a for loop, converts `error "the analysis did not converge"` into a TclError
2. **Transient analysis loop** (`while 1`) — adaptive time-stepping with `analyze 1 $dt` and error-on-failure

Leave the analysis **setup** commands (constraints, numberer, system, test, algorithm, integrator, analysis) unchanged so tcl2py converts them. Add dummy post-loop statements so the converted Python has valid variable bindings:

```tcl
# The transient analysis converged successfully (dummy for conversion)
set time $total_time
```

**Rule:** When converting via tcl2py, strip execution loops but preserve analysis configuration. The converted output will have the correct setup (constraints, algorithm, integrator, etc.) that you can then adjust per the lessons in §12x (ModifiedNewton, relaxed tolerance, etc.).

#### 4. What tcl2py Output Is Useful For

Even though tcl2py produces code that needs the same fixes as manual conversion, the output is valuable for:

| Use | Detail |
|-----|--------|
| **Model definition verification** | All materials, sections, nodes, elements, and fiber discretization are converted faithfully — cross-check your manual conversion |
| **Recorder setup** | `ops.recorder('Drift', ...)`, `ops.recorder('Node', ...)` are correctly converted with all arguments |
| **RigidDiaphragm commands** | All `ops.rigidDiaphragm()` calls are converted verbatim |
| **EleLoad patterns** | All `ops.eleLoad()` beam-distributed loads are converted verbatim |
| **Rayleigh damping** | `ops.rayleigh()` with correct coefficients |
| **Ground motion setup** | `ops.timeSeries('Path', ...)` and `ops.pattern('UniformExcitation', ...)` correctly created |
| **MPCO recorder** | The `.mpco` and `.mpco.cdata` infrastructure is preserved |

**Rule:** Use tcl2py as a verification tool, not a replacement for manual conversion. After converting, diff the model definition sections (materials/sections/elements/nodes) against your manual conversion. Apply the §12x fixes (dispBeamColumn, ModifiedNewton, elevated ft) to the tcl2py output.

#### 5. tcl2py Warnings — Expected and Ignorable

During conversion, tcl2py emits warnings that are expected for fiber-section models:

```
Warning: -GJ or -torsion not used for fiber section, GJ=100000000 is assumed!
```

This is informational — fiber sections in OpenSeesPy default to GJ=1e8 N·mm when no torsional stiffness is assigned. It does NOT indicate an error in the conversion.

**Rule:** These warnings can be safely ignored. They appear once per fiber section definition (typically 10-20 times for a multi-element RC frame model).

### §12z — RC Column Cyclic Pushover: Lateral Pattern After loadConst, Manual Solver Loop for Fiber-Section Softening (v1.24.0)

Source: elwoodKenneth conversion (2D RC cantilever column, fiber-section forceBeamColumn, 36 Concrete02 materials, 18 Steel02, 16-cycle cyclic pushover to 104 mm / 3.2% drift, ksi-in-kip → N-mm-MPa).

#### 1. Lateral Load Pattern MUST Be Defined AFTER `loadConst` for DisplacementControl

`ops.loadConst("-time", 0.0)` freezes **all** existing load patterns at their pseudo-time-0 value. For a Linear time series at t=0, the load factor is 0 — meaning the reference load vector is zero. When `DisplacementControl` subsequently uses this frozen pattern as its reference, it computes an infinite load factor (e.g., 6.59e+19) to scale the zero load to reach the target displacement, causing immediate solver failure.

This is the same mechanism as the ground-motion ordering bug (§12i), but applied to lateral pushover patterns:

```python
# BROKEN — lateral pattern frozen at λ=0
define_gravity_loads()
define_lateral_loads()      # pattern 200, Linear TS
run_gravity(odb)            # loadConst freezes pattern 200 at t=0 → λ=0
# DisplacementControl sees λ=0, computes infinite load factor
run_pushover(odb, ...)

# CORRECT — lateral pattern after loadConst
define_gravity_loads()
run_gravity(odb)            # loadConst freezes gravity only
define_lateral_loads()      # pattern 200 created AFTER — NOT frozen
run_pushover(odb, ...)
```

**Detection:** Check for `StaticAnalysis::analyze() - the Algorithm failed at step: 0 with domain at load factor > 1e10`. A load factor exceeding 10¹⁰ on the first pushover step indicates the reference pattern is frozen at zero.

**Rule:** Any load pattern used as a reference by DisplacementControl (or any integrator that scales a reference load vector) MUST be created AFTER `ops.loadConst("-time", 0.0)`. Only gravity patterns should exist before loadConst.

#### 2. ZeroLength Elements Create Stiffness Contrast That Blocks Gravity Convergence

Models with very stiff zeroLength base springs (e.g., `Elastic 1e12` in ksi units ≈ 1.75e14 N/mm) combined with fiber-section forceBeamColumn elements (axial stiffness ≈ 7e8 N/mm) produce a stiffness ratio of ~2.4×10⁵. Newton/KrylovNewton algorithms diverge on the very first gravity step:

```
CTestNormUnbalance::test() - failed to converge after: 75 iterations
  current Norm: 3.25e-06 (max: 1e-06)
  Norm deltaX: 5.18e-13
```

The displacement correction is fully converged (5e-13) but the force norm barely overshoots the tolerance. The root cause is the stiffness contrast in `constraints("Plain")` handler — the stiff zeroLength elements dominate the equation system.

**Fix:** Replace zeroLength base springs with direct fixity on the base node. The zeroLength elements in the source Tcl were used for reaction recording; with ODB (`odb.fetch_response_step()`), reactions are automatically available for all fixed nodes without needing zeroLength elements.

```python
# INSTEAD OF:
# ops.node(NODE_FIXED, 0, 0); ops.fix(NODE_FIXED, ...)
# ops.node(NODE_BASE, 0, 0)
# ops.element("zeroLength", ..., "-mat", E_STIFF, "-dir", 1)
# ops.element("zeroLength", ..., "-mat", E_STIFF, "-dir", 2)
# ops.element("zeroLength", ..., "-mat", E_STIFF, "-dir", 6)

# USE:
ops.node(NODE_BASE, 0, 0)
ops.fix(NODE_BASE, 1, 1, 1)  # direct fixity on base node
```

**When can zeroLength base springs be removed?** When the model does NOT need per-DOF reaction separation, and ODB nodal reaction collection suffices. If the source Tcl uses zeroLength elements only for convenience (not for nonlinear base behavior), removing them simplifies the model and improves convergence.

#### 3. SmartAnalyze Test Tolerance Configuration for Fiber-Section RC Pushover

`opst.anlys.SmartAnalyze` uses a default `EnergyIncr` test with tolerance 1e-10 and 10 max iterations. For fiber-section RC columns with Concrete02 materials entering the descending branch (>1% drift), this tolerance is too tight:

```
CTestEnergyIncr::test() - failed to converge after: 10 iterations
  current EnergyIncr: 1.81e-06 (max: 1e-10)
  Norm deltaX: 4.85e-05, Norm deltaR: 56.5
```

The EnergyIncr is 4 orders of magnitude above tolerance due to force imbalance from fiber-section state determination (~50 N at 1452 kN axial = 0.004%), even though the displacement solution is fully converged (Norm deltaX = 4.85e-5).

**Fix:** SmartAnalyze accepts test-control kwargs — pass `testType` and `testTol` to switch from `EnergyIncr` to `NormDispIncr` with a relaxed tolerance:

```python
analysis = opst.anlys.SmartAnalyze(
    analysis_type="Static",
    testType="NormDispIncr",          # ← was "EnergyIncr"
    testTol=1.0e-5,                   # ← was 1.0e-10
    testIterTimes=200,                # ← was 10
    tryAlterAlgoTypes=True,
    algoTypes=[40, 10, 20, 30],
    tryLooseTestTol=True,             # auto-relax if convergence stalls
    looseTestTolTo=1.0e-4,
    tryAddTestTimes=True,
    testIterTimesMore=[50, 100],
)
```

Note: `tryLooseTestTolTo` is derived from `testTol` (not `looseTestTolTo`), so set it explicitly.

**Key parameters for RC pushover:**

| Parameter | Default | RC pushover recommendation |
|-----------|---------|---------------------------|
| `testType` | `"EnergyIncr"` | `"NormDispIncr"` |
| `testTol` | 1e-10 | 1e-5 |
| `testIterTimes` | 10 | 200 |
| `tryLooseTestTol` | `False` | `True` (auto-relax to 1e-4) |
| `tryAlterAlgoTypes` | `False` | `True` |
| `algoTypes` | [40,10,20,30,50,60,70,90] | [40, 10, 20, 30] |
| `tryAddTestTimes` | `False` | `True` |
| `testIterTimesMore` | [50] | [50, 100] |

#### 4. Smaller Step Size for forceBeamColumn Element-Level Convergence

Even with a relaxed test tolerance, `SmartAnalyze` can fail at large drift (>1%) with:
```
ForceBeamColumn2d::update - failed to get compatible element forces & deformations
```

This is an **element-level** state determination failure — the flexibility-based forceBeamColumn element's internal Newton iteration diverges when fiber sections enter the softening branch. Unlike the global solver test tolerance, this is controlled by the element's own internal iteration and is sensitive to step size.

**Fix:** Reduce `MAX_STEP_SIZE` from 0.5 mm to 0.2 mm (or smaller). Smaller displacement increments give the forceBeamColumn element's internal iteration smaller changes to process, keeping the element-level Newton within its convergence radius:

```python
MAX_STEP_SIZE = 0.2  # mm — 0.5 mm caused element-level failure at ~1% drift
```

This allows SmartAnalyze to complete the full cyclic protocol (15-16 cycles, 102-104 mm peak, 3.2% drift) without element-level state determination failures.

**Rule of thumb:** If SmartAnalyze fails with `ForceBeamColumn2d::update - failed to get compatible element forces & deformations`, reduce `MAX_STEP_SIZE` by 2-3×. If it fails with a test/convergence error, adjust `testTol`/`testType`. If it hangs subdividing below `minStep`, the section has genuinely softened past zero stiffness — accept the failure as a physical limit of the model.

#### 5. Algorithm Selection for RC Pushover: KrylovNewton Over Newton

For fiber-section forceBeamColumn elements under cyclic pushover with axial gravity preload, KrylovNewton (algoType=40) converges where Newton (algoType=10) fails. The Krylov acceleration in KrylovNewton provides better search directions for the flexibility-based element state determination.

**Fallback chain order for RC pushover:**
1. `KrylovNewton` — primary, best for fiber-section convergence
2. `Newton` — falls back when KrylovNewton overshoots
3. `NewtonLineSearch` — helps when standard Newton oscillates
4. `ModifiedNewton` — uses initial stiffness, converges slowly but stably
5. `KrylovNewton` with relaxed tolerance (1e-4) — last resort

#### 6. Gravity Analysis: `NormDispIncr` + `KrylovNewton` More Robust Than Tcl's `NormUnbalance` + `Newton`

The source Tcl uses `test NormUnbalance 1e-6 75` and `algorithm Newton` for gravity. In OpenSeesPy, switching to `test NormDispIncr 1.0e-5 200` and `algorithm KrylovNewton` provides more reliable convergence for fiber-section models under pure axial load. The `NormDispIncr` test checks displacement increments (which converge monotonically for load-controlled gravity) rather than force unbalance (which can oscillate in the first step).

#### 7. Cyclic Pushover Protocol: Natural Peak-to-Peak Flow

The original Tcl's `CyclicSolutionAlgorithm.tcl` was a shared helper (not present in the repository). The cyclic protocol can be reconstructed from the peak-displacement list as a flat sequence of alternating positive/negative targets:

```python
targets = []
for peak_pos, peak_neg in CYCLE_PEAKS_MM:
    targets.append(peak_pos)  # push forward
    targets.append(peak_neg)  # pull backward
# DisplacementControl naturally transitions between successive targets
# without needing explicit return-to-zero steps
```

The DisplacementControl integrator drives from the current position to each successive target, creating the cyclic hysteresis loop automatically. No explicit return-to-zero segment is needed — the transition from a negative peak to the next cycle's positive peak inherently passes through zero.

**Symptom if return-to-zero is attempted:** With `target_disp=0`, the function computes `step_size = 0 / n_steps = 0`, and the DisplacementControl integrator attempts zero-displacement steps, producing a `step_size must be > 0` error (or hangs at the current position).

### §12aa — Effective-Stress Site Response: quadUP Argument Signature & Base UX Fixity (v1.26.0)

Source: pedroArduino_freefield conversion (1D effective-stress soil column, 3-layer PDMY02, quadUP + Lysmer dashpot, kN-m-kPa-s units).

#### 1. `quadUP` Element Signature: `fmass` Is NOT Optional — Don't Omit It

The `quadUP` (FourNodeQuadUP) element signature has **8** material/property args after the 4 node tags:

```
element quadUP eleTag iNode jNode kNode lNode  thick matTag bulk fmass hPerm vPerm b1 b2
```

The `fmass` (fluid mass density) argument sits between `bulk` and `hPerm`. Omitting it shifts every subsequent argument left, producing a model that **runs without error** but silently applies zero gravity and bogus permeability — the worst kind of bug (no crash, no warning, wrong physics).

**Real example (pedroArduino_freefield):**

| Position | Expected | What the bug fed it | Effect |
|----------|----------|----------------------|--------|
| fmass | fluid ρ | `1.0` (intended hPerm) | harmless coincidence |
| hPerm | hPerm | `1.0` (intended vPerm) | harmless coincidence |
| vPerm | vPerm | `BODY_X` ≈ −0.098 | negative permeability |
| b1 | bx | `BODY_Y` = −9.81 | horizontal force 100× too large |
| **b2** | **by** | *(missing → 0.0)* | **no vertical gravity at all** |

**Symptom:** Zero deformation / settlement in the gravity phase. The column never consolidates because the vertical body force never reaches OpenSees.

**Root cause:** The inline comment was written as `# quadUP: thick, matTag, bulk, hPerm, vPerm, bx, by` — it omitted `fmass` — and the code was written to match the wrong comment. The Tcl source used `SSPquadUP` (a *different* signature with `eInit` + `alpha`), so the arg list could not be copied across element types verbatim.

**Fix:**

```python
# quadUP: thick, matTag, bulk, fmass, hPerm, vPerm, b1, b2
ops.element("quadUP", tag, nI, nI + 1, nI + N_NODE_X + 1, nI + N_NODE_X,
            1.0, k, bulk, 1.0, 1.0, 1.0, BODY_X, BODY_Y)
#           thick  mat    bulk    fmass  hPerm  vPerm  b1     b2
```

**Detection in Existing Models:** Flag any `quadUP` element call with fewer than 8 args after the 4 nodes. Cross-check the arg count against the [OpenSees quadUP wiki](https://opensees.berkeley.edu/wiki/index.php/Four_Node_Quad_u-p_Element) signature. When converting a Tcl that uses a different u-p element type (`SSPquadUP`, `bbarQuadUP`, `NineFourNodeQuadUP`), do NOT copy the argument list — each has a distinct signature. Re-derive from the Python docs.

**Rule:** When converting between coupled u-p element types (`SSPquadUP` → `quadUP` or vice versa), treat the element construction line as a from-scratch translation, never a copy. The body-force and permeability arguments land in different positions across these elements.

#### 2. Gravity-Phase Base UX Fixity — `fix 1 1 1 0` Then `remove sp 1 1`

On a sloped free-field column (even 1% grade), the horizontal component of gravity body force has no resisting stiffness in UX at the base once the Lysmer dashpot is the only lateral restraint. This creates a **rigid-body horizontal drift mode** that diverges with a huge residual norm.

**Symptom:** `analyze` returns `-3` with `Norm R: 98044.1` on the first plastic gravity step; all node displacements read as exactly 0.0 (Newton never converges, nothing is recorded). The norm is enormous (≈1e5) compared to a normal unconverged step (≈1e-1).

**Fix — match the Tcl exactly:**

```python
# Gravity phase: temporarily fix base UX for stability
ops.fix(1, 1, 1, 0)        # tcl: fix 1 1 1 0
# ... gravity analysis ...
ops.remove("sp", 1, 1)     # tcl: remove sp 1 1 — free base UX before dynamic
```

The temporary UX fix is **removed before the dynamic phase** so the base is free to follow the input motion transmitted through the Lysmer dashpot. Skipping the removal would clamp the base and block the seismic input entirely.

**Verified by isolated probe:** base UX-free → `ok=-3`, all disp 0.0; base UX-fixed → `ok=0`, top node settles 15 mm. This is not optional for sloped columns — even a 1° slope needs it.

#### 3. OpenSeesPy `fix()` Errors on a DOF Already Constrained (unlike Tcl `fix`)

OpenSeesPy's `ops.fix(node, *dofs)` raises `OpenSeesError` if the node already has an SP constraint on any of the specified DOFs. Tcl's `fix` silently overwrites. This bites when a node has a base BC (`fix(i, 0, 1, 0)` — UY fixed) and gravity wants to re-fix the full triple (`fix(1, 1, 1, 0)` — UY re-specified).

**Symptom:**

```
Domain::addSP_Constraint - cannot add as node already constrained in that dof
SP_Constraint: 16  Node: 1 DOF: 2 ...
opensees.OpenSeesError: See stderr output
```

**Fix:** Release the conflicting DOF's existing SP before re-fixing:

```python
# Node 1 already has UY (DOF 2) fixed from base BC; release it before re-fixing
ops.remove("sp", 1, 2)
ops.fix(1, 1, 1, 0)
```

`ops.remove("sp", node, dof)` is the OpenSeesPy equivalent of Tcl `remove sp $node $dof`. It returns `None` on success (verified). This pattern (release-then-refix) is needed whenever you overlay a fuller fixity on a node that already has a partial one.

### §12ab — SSPquadUP Correct Element Signature & Cross-Element-Type Conversion Hazards (v1.27.0)

Source: pedroArduino_freefield SSPquadUP correction — the original `model.py` used `quadUP` but the Tcl source uses `SSPquadUP`. Three different conversions of the same Tcl exist, each using a different element type.

#### 1. SSPquadUP Element Signature: matTag BEFORE thick, Plus e0 and press

The SSPquadUP (Stabilized Single-Point Quad u-p) signature has **10** material/property args after the 4 node tags:

```
element SSPquadUP eleTag nI nJ nK nL  matTag thick bulk fmass hPerm vPerm e0 press bx by
element quadUP    eleTag nI nJ nK nL  thick matTag bulk fmass hPerm vPerm         b1 b2
```

**Critical differences vs quadUP:**

| Position | SSPquadUP | quadUP | Impact if swapped |
|----------|-----------|--------|-------------------|
| 1st arg | **matTag** | **thick** | Material tag → thickness slot → wrong soil layer |
| 2nd arg | **thick** | **matTag** | Thickness → material slot → bogus material |
| 7th arg | **e0** (void ratio) | *(absent)* | Missing → SSPquadUP gets 0 or garbage |
| 8th arg | **press** (ref pressure) | *(absent)* | Missing → effective-stress calc broken |
| 9th/10th | bx, by | b1, b2 | Same function, different position in list |

SSPquadUP requires `e0` (initial void ratio, e.g. 0.77 for loose sand, 0.47 for dense) and `press` (reference pressure, typically 1.5e-6 kPa) passed at the **element level** — not just inside the PDMY02 material definition. Without `press`, the effective-stress calculation has no reference pressure and produces wrong results.

**Correct Python for SSPquadUP:**

```python
ops.element("SSPquadUP", tag,
    nI, nI + 1, nI + N_NODE_X + 1, nI + N_NODE_X,
    k,              # matTag ← BEFORE thick
    1.0,            # thick
    s["uBulk"],     # bulk
    1.0,            # fmass
    1.0, 1.0,       # hPerm, vPerm (temp = 1.0 for gravity)
    s["e0"],        # e0 ← REQUIRED, per-layer void ratio
    PRESS,          # press ← REQUIRED, 1.5e-6 kPa
    BODY_X, BODY_Y) # body forces
```

#### 2. Cross-Element-Type Conversion: Never Copy the Arg List

Three different u-p element types exist for the same physics, each with a distinct signature:

| Element | Nodes | Key extra args | Source |
|---------|-------|---------------|--------|
| `SSPquadUP` | 4 | e0, press | Tcl `freeFieldEffective.tcl` |
| `quadUP` | 4 | *(none)* | Current `model.py` (wrong) |
| `9_4_QuadUP` | 9 (4 PP) | Different topology | Notebook `Effective Stress Site Response_rev.ipynb` |

**Rule:** When converting between coupled u-p element types, treat the element construction line as a from-scratch translation. Identify the source element type FIRST by grepping the Tcl for `element SSPquadUP\|quadUP\|9_4_QuadUP\|bbarQuadUP`, then look up the correct Python signature. Never assume they're interchangeable.

#### 3. PostShake Parameter: Activate PDMY02 Consolidation Mode

After the dynamic phase, PDMY02 materials need `PostShake=1` set on all elements to activate post-shaking consolidation (excess pore pressure dissipation):

```tcl
# Tcl source (L528):
setParameter -value 0 -eleRange 1 3125 PostShake 1
```

```python
# Python equivalent:
for ele in range(1, n_elem + 1):
    ops.setParameter("-val", 1, "-ele", ele, "PostShake")
```

**Symptom of missing PostShake:** The post-shake consolidation phase runs but excess pore pressures do not dissipate — the model stays in a post-liquefaction state. No error or warning is produced.

#### 4. 1D Site Response Visualization: Deformed Shape Is One Line

For a 1-column soil mesh (N_ELEM_X=1, N_NODE_X=2) with `equalDOF` tying each horizontal pair for periodic boundaries, all nodes at the same elevation share the same lateral displacement. The deformed shape in UX is a single vertical line shifting side-to-side — this is **correct behavior**, not a bug.

**Better diagnostics for soil models:** Use stress contour plots instead of displacement plots:

```python
# Stress contours (shows 2D field across element interiors)
# Use resp_type="Stresses" (Gauss-point, averaged per element) — NOT
# "StressesAtNodes", which is all-zeros for single-Gauss-point elements
# like quadUP (see §12ad).
opst.vis.plotly.plot_unstruct_responses(
    odb_tag=1, slides=True, ele_type="Plane",
    resp_type="Stresses", resp_dof="sigma22",  # vertical stress
)
# Shear stress with deformation overlay
opst.vis.plotly.plot_unstruct_responses(
    odb_tag=1, slides=True, ele_type="Plane",
    resp_type="Stresses", resp_dof="sigma12",  # shear stress
    show_defo=True, defo_scale=30,
)
# Pore pressure: read from nodal 'pressure' (valid) not sigma33
opst.vis.plotly.plot_nodal_responses(
    odb_tag=1, slides=True, resp_type="pressure",
)
```

These show the 2D stress field across element interiors, which is the proper diagnostic for verifying a site response model is working (gravitational stress gradient with depth, dynamic shear waves propagating upward). See §12ad for why `StressesAtNodes` must be avoided on single-Gauss-point elements.

### §12ac — ODB Path Ordering: `set_odb_path` MUST Precede `CreateODB` (v1.28.0)

Source: pedroArduino_freefield — output plots missing because response data was written to the wrong directory.

#### The Bug

`opst.post.set_odb_path()` migrates any existing ODB data from the default `.opstool.output/` into the target path. But it only takes effect for **subsequent** ODB operations — if `CreateODB` is instantiated *before* `set_odb_path` is called, the response data silently lands in the default `.opstool.output/` instead of the intended `output/`. The model's own `output/RespStepData-1.odb` directory is created (by `save_model_data`) but ends up **empty**, while the real data sits hidden in the repo-root default.

```python
# BROKEN — CreateODB before set_odb_path; response data misrouted
odb = opst.post.CreateODB(odb_tag=1, save_nodal_resp=True, ...)
opst.post.set_odb_path(str(output_dir))   # too late — ODB already initialized
odb.save_model_data()

# CORRECT — set_odb_path first
opst.post.set_odb_path(str(output_dir))   # MUST precede CreateODB
odb = opst.post.CreateODB(odb_tag=1, save_nodal_resp=True, ...)
odb.save_model_data()
```

#### Symptom

- `output/RespStepData-1.odb/` exists but is empty (no `part_i.zarr` inside)
- `post_process.py` fails with `FileNotFoundError: No parts found in .../RespStepData-1.odb`
- `get_nodal_responses()` / `get_element_responses()` raise errors or return empty
- The data *is* there — but in `.opstool.output/` at the repo root, not where you expect

This is a **silent failure**: the model runs to completion with no error, and only post-processing reveals the data is unreachable. Compounding the problem, the default `.opstool.output/` is gitignored, so the data vanishes from version control entirely.

#### Detection in Existing Models

Flag any model where `opst.post.set_odb_path(...)` appears *after* `opst.post.CreateODB(...)` in the same scope. The canonical pattern in §3d shows the correct order (`set_odb_path` first), but this lesson formalizes *why*: the path migration only applies to ODBs created after the call.

**Rule:** `opst.post.set_odb_path(str(output_dir))` is the **first** ODB-related call in `run_analysis()` / `__main__`, preceding `CreateODB`. This is already what §3d shows — treat it as a hard ordering requirement, not a style preference.

### §12ad — Single-Gauss-Point Elements: Use `Stresses`, Not `StressesAtNodes` (v1.28.0)

Source: pedroArduino_freefield — stress contour plots all read zero despite valid analysis.

#### The Bug

opstool's Gauss-point-to-node stress projection (`StressesAtNodes`, `StressMeasuresAtNodes`) only supports specific `(element_type, num_nodes, num_gauss_points)` combinations:

```python
# opstool/utils/ele_shape_func.py — supported quad projection keys
("quad", 4, 4), ("quad", 9, 9), ("quad", 8, 9)   # NO ("quad", 4, 1)
```

For elements that report **only 1 Gauss point** — notably `quadUP` (FourNodeQuadUP), and any reduced-integration quad — the lookup `get_gp2node_func("quad", 4, 1)` returns `None`. The projection then falls back to a **zero fill** (see `_get_plane_resp.py:310`), and every `StressesAtNodes` value is `0.0` across all elements and all time steps.

This is a **silent failure**: the Gauss-point `Stresses` are valid (verified: σ₂₂ from −308 kPa at base to −4 kPa at surface — a physically correct vertical stress profile), but the node-projected view is all-zeros. No warning, no error — just zeros where stresses should be.

#### The Fix

Read Gauss-point data directly with `resp_type="Stresses"`. opstool's `plot_unstruct_responses` averages the Gauss-point values per element internally (trivial when there's only 1 GP), so contour plots work correctly:

```python
# BROKEN — all-zeros for quadUP (1 GP unsupported by projection)
opst.vis.plotly.plot_unstruct_responses(
    odb_tag=1, ele_type="Plane",
    resp_type="StressesAtNodes", resp_dof="sigma22",   # ← 0.0 everywhere
)

# CORRECT — Gauss-point Stresses, averaged per element
opst.vis.plotly.plot_unstruct_responses(
    odb_tag=1, ele_type="Plane",
    resp_type="Stresses", resp_dof="sigma22",          # ← valid values
)
```

For **pore pressure** in coupled u-p elements, `Stresses` σ₃₃ is the out-of-plane total stress component, *not* pore water pressure. Read PWP from nodal `pressure` instead, which is always valid regardless of element type:

```python
# Pore water pressure — read from nodal data, not sigma33
opst.vis.plotly.plot_nodal_responses(
    odb_tag=1, resp_type="pressure",   # ← valid (absmax 381 kPa verified)
)
```

When extracting raw arrays (e.g. for stress profiles or stress-strain loops), read `plane["Stresses"]` and collapse the `GaussPoints` dimension:

```python
plane = opst.post.get_element_responses(odb_tag=1, ele_type="Plane")
sigma22 = plane["Stresses"].sel(stressDOFs="sigma22").isel(time=-1)
sigma22_final = sigma22.mean(dim="GaussPoints")   # collapse GP axis
```

#### Detection in Existing Models

Flag any `post_process.py` that uses `resp_type="StressesAtNodes"` (or `StressMeasuresAtNodes`) on a model using `quadUP`, `SSPquadUP`, or any element with a single Gauss point. Quick check:

```python
import opstool as opst
from opstool.utils import get_gp2node_func
# If this returns None, StressesAtNodes will be all-zeros:
f = get_gp2node_func("quad", 4, 1)   # quadUP reports (quad, 4, 1) → None
```

Also check the ODB directly: if `Stresses` has nonzero absmax but `StressesAtNodes` is all-zeros, the projection is unsupported for that element type.

**Rule:** Prefer `resp_type="Stresses"` (Gauss-point) over `StressesAtNodes` for all u-p coupled elements (`quadUP`, `SSPquadUP`, `bbarQuadUP`, `NineFourNodeQuadUP`). The `AtNodes` variants only work for elements whose `(type, nodes, GP)` triple is in opstool's projection table. The Gauss-point variant works universally and is what opstool's own contour plotting averages internally.

### §12ae — 9_4_QuadUP Site Response: Base Bubble-Node Fixity, Plastic-Gravity Solver & Post-Shake Divergence (v1.29.0)

Source: misty_effective stress site resp — model diverged at the elastic→plastic gravity transition; full post-shake consolidation diverged.

#### 1. 9-node edge-mid ("bubble") nodes need the base UY fixity too

The `9_4_QuadUP` (NineFourNodeQuadUP) element has 4 corner nodes (ndf=3: UX, UY, PWP) plus 4 edge-mid + 1 center node (ndf=2: UX, UY). When converting the notebook's interleaved node-tag arithmetic to a clean coordinate-grid mesh, it is easy to fix the base **corner** nodes' UY (`fix(n, 0, 1, 0)`) and forget the base **edge-mid** node. That bottom-mid node sits on y=0; left free in UY it bows downward (~6 mm during elastic gravity), and the elastic→plastic PDMY02 transition then **diverges** (Norm R ~6.6e5, ok=-3).

The notebook's `ops.fix(2, 0, 1)` (node 2 = the base interior/center node) is exactly this fix. In a grid mesh it generalises to fixing UY on the bottom-edge-mid node of every base-row element:

```python
for ele_tag, (i, j) in _iter_elements():
    if j == 0:                       # base row
        n_bot = bubble[ele_tag][0]   # bottom edge-mid node
        ops.fix(n_bot, 0, 1)         # UX free, UY fixed (matches base corners)
```

Without this, even the correct plastic-gravity solver (below) only cycles at Norm~0.005. With it, Norm R drops ~5400×.

#### 2. Plastic gravity needs KrylovNewton + small dt

The notebook does `analyze(40, 500.0)` for the plastic (stage 1) gravity. Under OpenSeesPy this diverges on the PDMY02 elastic→plastic transition: Newton converges the elastic phase but **cycles at Norm~0.005** (just above 1e-4) once the material switches to plastic — the tangent near the yield surface defeats plain Newton-Raphson. The fix: **KrylovNewton** (secant acceleration escapes the cycle) with **dt=1.0** (small steps cross the transition). This mirrors the working `pedroArduino_freefield` recipe but with KrylovNewton instead of Newton:

```python
# elastic stage 0: Newton, dt=500, 100 steps  (ok=0)
# plastic stage 1: KrylovNewton, dt=1.0, 100 steps  (ok=0)
ops.algorithm("KrylovNewton")
ops.test("NormDispIncr", 1.0e-4, 50, 1)
ops.analyze(100, 1.0)
```

Verified: top-node UY = −0.0161 m (sensible for a 30 m column under gravity).

#### 3. Post-shake (PostShake=1) diverges at dt ≥ 0.01

After dynamic shaking, `setParameter(... PostShake 1)` switches PDMY02 into post-shake consolidation mode and excess pore pressure begins to dissipate. The notebook drives this to t=100 s with Newton + dt=0.05 + tol=1e-5. On the 9_4_QuadUP mesh under OpenSeesPy this **diverges**: Norm R blows up (9e3 → 4.7e5 → 2.9e6 → 3.7e11) within 5 iterations, then NaN. **Only dt ≤ 0.005 is stable** (converges in 3 iterations/step at tol=1e-3 with KrylovNewton). Because a full 100 s consolidation at dt=0.005 is ~16000 steps (hours), make post-shake **bounded and best-effort**:

```python
odb.save_response()          # save the verified DYNAMIC response FIRST
activate_postshake(n_elem)   # PostShake=1
# bounded post-shake: small batches at dt=0.005, bail on first non-converged step
ops.test("NormDispIncr", 1.0e-3, 50, 1); ops.algorithm("KrylovNewton")
for b in range(6):           # 6 batches × 50 steps
    if ops.analyze(50, 0.005) != 0:
        break                # stop cleanly; dynamic results already on disk
    odb.save_response()
```

#### 4. opstool does not capture the u-p pore-pressure DOF (shared with §12ad)

For both `9_4_QuadUP` and `quadUP`, opstool's ODB `pressure` field reads **all-zeros** — the pore-pressure DOF (dof 3) is not mapped into the saved nodal response (it lands in the UZ slot, which opstool leaves zero for 2D nodes). This is identical in the sibling `pedroArduino_freefield`. Verify the effective-stress physics through the Gauss-point **σ₂₂ contour** instead (−429 kPa at base → −4.5 kPa at surface = correct vertical effective-stress gradient). Excess-PWP time histories need `ops.recorder('Node', ..., '-dof', 3, 'vel')`.

#### Detection / rules

- **9_4_QuadUP conversions:** after building the mesh, assert that every node on the base line (y=0) — corners AND edge-mids — is UY-fixed. A missing base bubble fixity shows up as elastic gravity converging but plastic gravity diverging at step 1.
- **PDMY02 elastic→plastic transition diverging:** switch plastic gravity to KrylovNewton + dt≈1.0. Newton cycling at Norm just above tol (vs blowing up) is the signature.
- **PostShake consolidation diverging:** cap dt at 0.005 (KrylovNewton, tol=1e-3). Always `odb.save_response()` the dynamic results BEFORE post-shake so a divergent post-shake cannot discard the verified run.

---

### §12af — 3D MSSS Bridge Transient: Gravity-as-Ramp, BandGeneral Solver & Manual Newton Loop (v1.30.0)

Source: `padgett_jamie` model conversion — 3-span simply-supported concrete box girder bridge on elastomeric bearings with fiber columns, abutment springs, foundation springs, and deck pounding.

#### 1. Static Gravity LoadControl Fails at ~40% for Stiffness-Contrast 3D Bridge Models

The Tcl parametric generator runs `analyze 5` with `LoadControl 0.2` and succeeds for its 1152 parameter combinations. The single representative bridge (row i=1129) **cannot converge past 40% gravity** under the same settings in OpenSeesPy. This is a genuine model stability issue at loads above 40% — not a conversion error:

| Setting | Converged steps | Load reached |
|---------|----------------|-------------|
| `LoadControl(0.2)`, 5 steps | 2/5 | 40% |
| `LoadControl(0.1)`, 10 steps | 4/10 | 40% |
| `LoadControl(0.05)`, 20 steps | 0/20 | 0% |

The failure occurs at the **same 40% load threshold** regardless of step count — the stiffness from 40% gravity produces a tangent-stiffness transition that static LoadControl cannot cross.

**Root cause:** The stiffness contrast between rigid links (1e6 × girder stiffness), fiber-section columns (Concrete04 + Steel02), nonlinear bearings (Steel01 + ElasticPPGap + Hysteretic dowel), and abutment/foundation springs creates a system where some elements are at a tangent-stiffness transition near 40% gravity load. Newton iterations diverge exponentially (Norm deltaR jumps from ~1e6 to ~1e45 within a single iteration).

#### 2. Fix: Apply ALL Gravity as a Transient Ramp (Not Static Analysis)

Instead of attempting partial static gravity, apply **all gravity as a smooth ramp during the transient dynamic analysis**. The approach:

```python
GRAV_RAMP_DURATION = 2.0  # seconds to ramp gravity from 0→100%

# Gravity ramp time series
ramp_npts = int(GRAV_RAMP_DURATION / gm_dt)
ramp = np.linspace(0.0, 1.0, ramp_npts)
ops.timeSeries("Path", TS_GRAV, "-dt", gm_dt, "-values", *ramp, "-factor", 1.0)
ops.pattern("Plain", PAT_GRAV, TS_GRAV)
# Apply ops.load() for full gravity on all gravity-load nodes

# GM zero-padded by ramp_npts so it starts AFTER gravity is fully ramped
zero_pad = np.zeros(ramp_npts)
gm_padded = np.concatenate([zero_pad, gm_raw * factor])
ops.timeSeries("Path", TS_GM_X, "-dt", gm_dt, "-values", *gm_padded, "-factor", 1.0)
ops.pattern("UniformExcitation", PAT_GM_X, 1, "-accel", TS_GM_X)
```

**Why this works:** At t=0 the structure has zero applied load. The first transient step applies a tiny gravity increment (≈0.05% full gravity per step at dt=0.001). The Newton algorithm converges easily because the load increment is small and the structure is never far from equilibrium. The gravity ramp completes in 2 seconds; the GM starts at t=2s.

**Constraint:** The `loadConst("-time", 0.0)` pattern-freezing trick (§12i) is NOT used here — there is no separate static gravity phase. The gravity pattern is active throughout the transient.

#### 3. Solver Selection: BandGeneral Beats UmfPack for Stiffness-Contrast Models

UmfPack and SparseGEN (SuperLU) both fail to factorize the Newmark effective-stiffness matrix after a few transient steps, while BandGeneral (LAPACK banded solver) works reliably:

| Solver | Behavior |
|--------|----------|
| `UmfPack` | `numeric analysis returns 1 -- Umfpackgenlinsolver::solve` (fails at step 7 with Linear algorithm) |
| `SparseGEN` | `SuperLU::solve - Error 1 in factorization dgstrf` (singular matrix) |
| `BandGeneral` | **Converges 6000/6000+ steps** (no failures) |

**Mechanism:** UmfPack refactors the matrix at every solve call. For matrices with high stiffness contrast, UmfPack's numerical pivot tolerance may flag small pivots as zero, aborting the factorization. BandGeneral uses LAPACK's `dgbsv` with full row/column pivoting and handles the contrast. The stiffness matrix is NOT truly singular — the eigen solver returns valid eigenvalues (T1=2.69s).

#### 4. Manual Transient Loop Replaces SmartAnalyze (Documented Exception)

SmartAnalyze's adaptive sub-stepping reduces the time step to ~6e-7s when the first full-step attempt fails. At this tiny step size, the Newmark effective-stiffness term `1/(β·Δt²)·M` dominates (≈1e13× M). For DOFs with zero mass (bearing-top nodes, bent-bottom nodes), the mass-term vanishes and K_eff ≈ K_t, which may become ill-conditioned. The solution — a **fixed-step manual loop** matching the Tcl source's approach:

```python
dt_analysis = 0.001  # fixed step (matches Tcl source's dt=0.001)
ops.analysis("Transient")
for i in range(total_steps):
    ok = ops.analyze(1, dt_analysis)
    if ok != 0:
        # Fallback: relax tolerance, switch algorithm
        ops.test("NormDispIncr", 1.0e-2, 100, 3)
        ops.algorithm("NewtonLineSearch")
        ok = ops.analyze(1, dt_analysis)
        # Restore normal settings
        ops.test("NormDispIncr", 1.0e-3, 200, 3)
        ops.algorithm("Newton")
    if ok != 0:
        break  # genuine failure
    if i % odb_interval == 0:
        odb.fetch_response_step()
```

This is a documented exception per §3c/§10 (SmartAnalyze is incompatible with this model's numerical characteristics).

#### 5. Algorithm Choice and Fallback Strategy

| Algorithm | Behavior |
|-----------|----------|
| `Newton` | Primary choice. Converges 99% of steps. Fails at ~1% of steps with borderline Norm (e.g., 1.44e-4 vs tol 1e-4). |
| `NewtonLineSearch` | Reliable fallback. Resolves the borderline failures when tolerance is relaxed to 1e-2. |
| `KrylovNewton` | Fails at step 1 when residual forces are present; works after ramp completes but offers no advantage over Newton. |
| `Newton -initial` | **Segfaults** (exit code 139). Do not use with this model's element/matrix combination. |
| `ModifiedNewton` | Not tested; Newton's convergence rate is adequate. |

#### 6. Eigen Period Shift Under Full vs Partial Gravity

Using the **transient gravity ramp** (0→100%) vs the **partial static gravity** (40%) produces significantly different eigenvalues:

| State | T1 | T2 |
|-------|-----|-----|
| 40% partial gravity (static, frozen) | 3.41 s | 2.00 s |
| 100% full gravity (via transient ramp) | 2.69 s | 1.74 s |

The ~20% period decrease under full gravity is expected — columns and bearings stiffen under higher axial compression. Models relying on partial gravity for eigen analysis or Rayleigh coefficients will systematically underpredict natural frequencies.

**Rule:** Always run the eigen analysis AFTER the gravity ramp has completed (not before or during). For the ramp approach, the eigen analysis in `run_dynamic` naturally captures the full-gravity state.

#### 7. ODB Throttling for Long Transient Analyses

With 22,000 analysis steps (2s ramp + 20s GM, both at dt=0.001), calling `odb.fetch_response_step()` every step produces 22,000 API calls — excessive. Throttle to every Nth GM-step:

```python
steps_per_gm = round(gm_dt / dt_analysis)  # e.g., 5 for gm_dt=0.005, dt=0.001
odb_every_n_gm = 5  # collect every 5th GM-step
odb_interval = steps_per_gm * odb_every_n_gm  # every 25 analysis steps

for i in range(total_steps):
    ok = ops.analyze(1, dt_analysis)
    ...
    if i % odb_interval == 0:
        odb.fetch_response_step()
```

This reduces 22,000 calls → ~880, which completes in minutes rather than hours.

#### Detection / Rules

- **If static LoadControl diverges at the same load factor regardless of step count** → the model has a stiffness regime change at that load. Switch to the gravity-as-transient-ramp approach.
- **If UmfPack returns "numeric analysis returns 1" after a few successful transient steps** → switch to BandGeneral. This is NOT a matrix singularity (eigen values are valid; BandGeneral succeeds).
- **If `eigen` returns shorter periods than expected** → measure at full-gravity state (after gravity ramp), not at partial-gravity state. The stiffness difference is real.
- **Always zero-pad the GM time series** when gravity is applied during the transient. The GM must start after gravity is fully (or mostly) ramped up.
- **For gravity ramp in model catalogues:** Set `file format: .py`, note "Gravity via transient ramp" in the Notes field. The Tcl source uses static gravity; the Python conversion uses the ramp as a documented adaptation.

---

### §12ag — SmartAnalyze Compatibility for Stiffness-Contrast Models: Fictitious Mass Regularisation (v1.31.0)

Source: `padgett_jamie` SmartAnalyze variant — 3-span MSSS bridge with fiber columns, bearings, and rigid links (1e6× stiffness contrast).

#### 1. Zero-Mass Free DOFs Cause K_eff Singularity at Micro-Step Sizes

SmartAnalyze's adaptive sub-stepping reduces the time step when convergence is slow. At very small Δt (≈6e-7s), the Newmark effective-stiffness matrix is dominated by the mass-proportional term:

```
K_eff = 1/(β·Δt²)·M + γ/(β·Δt)·C + K
```

At Δt = 6e-7s: `1/(β·Δt²) ≈ 1.1e13`. For DOFs where M = 0 (e.g., bearing-top nodes, bent-bottom nodes), the mass term vanishes and `K_eff ≈ K`. If the tangent stiffness K for those DOFs is also ill-conditioned (from stiffness contrast), K_eff becomes near-singular and the linear solver fails.

**Symptom:** SmartAnalyze reduces the step to `Current step 6.104e-07 is below the min step 1.000e-06` and then fails with UmfPack/SuperLU factorization error.

#### 2. Fix: `_ensure_minimum_mass(1e-6)` for Every Free DOF

Assign a tiny fictitious mass (1e-6 N·s²/mm) to every free DOF that has zero mass. This is ~0.00003% of the deck mass (≈3 N·s²/mm) — negligible for global dynamics but critical for regularising K_eff:

```python
def _ensure_minimum_mass(min_mass: float = 1.0e-6) -> None:
    """Assign a tiny fictitious mass to every free DOF that has zero mass."""
    for tag in ops.getNodeTags():
        masses = [ops.nodeMass(tag, dof) for dof in range(1, 7)]
        if any(m < min_mass for m in masses):
            patched = [max(m, min_mass) for m in masses]
            ops.mass(tag, *patched)
```

Call this **after** `define_masses()` and **before** creating the ODB (the ODB snapshots the mass distribution at `save_model_data()`).

#### 3. Results: SmartAnalyze Performance With vs Without Fictitious Mass

| Configuration | Steps converged | Failure mode |
|---|---|---|
| No fictitious mass, SmartAnalyze | 0/1200 | UmfPack error at step 1 |
| `_ensure_minimum_mass(1e-6)`, SmartAnalyze | 648/1200 (54%) | Convergence at peak GM amplitude |
| `_ensure_minimum_mass(1e-6)`, manual Newton dt=0.001 | 1200/1200 (100%) | No failures |

The fictitious mass enables SmartAnalyze to get past the initial-step singularity. For full-coverage production runs, the manual Newton loop at fixed dt=0.001 is still more robust (it subdivides the GM step into 5× smaller increments, making each Newton iteration easier to converge).

#### 4. Toggleable Flag Pattern

For models where both SmartAnalyze and a manual loop are useful, use a module-level flag:

```python
USE_SMARTANALYZE = False  # True → SmartAnalyze; False → manual Newton loop

def run_analysis(output_dir):
    ...
    define_masses()
    if USE_SMARTANALYZE:
        _ensure_minimum_mass()
    ...
```

This keeps a single `model.py` that supports both modes. Users developing the model can iterate quickly with SmartAnalyze, then switch to the manual loop for production runs.

#### Detection / Rules

- **If SmartAnalyze fails with UmfPack/SuperLU solver error at the very first step** → check for zero-mass free DOFs. Use `ops.getNodeTags()` + `ops.nodeMass(tag, dof)` to audit.
- **If the model has zeroLength elements (bearings, springs, impact) AND beam elements** → the bearing-adjacent nodes (bearing-top etc.) likely have no mass. Add fictitious masses.
- **Fictitious mass should be ≤ 1e-6 for bridge models** (as a fraction of the smallest real mass). For smaller models, scale proportionally.
- **For the manual Newton loop fallback**, use `dt_analysis = 0.001` with `steps_per_gm = round(gm_dt / dt_analysis)` — this gives 5× sub-stepping for `gm_dt=0.005`, matching the Tcl source's approach.

### §12ah — PM4Sand `FirstCall` Routing & Mixed-ndf Fictitious-Mass Scoping (v1.32.0)

Source: `RathjeEllen` — 2D coupled u-p effective-stress site response with PM4Sand liquefaction (18-case parametric sweep, GiD `UWquad2D` Tcl → OpenSeesPy).

#### 1. PM4Sand `FirstCall` Requires the Trailing Material Tag — as a String

The Tcl source's elastic→plastic gravity transition is:
```tcl
updateMaterialStage -material 1 -stage 1
setParameter -value 0 -ele $eleTag FirstCall $matTag
```

PM4Sand's `FirstCall` parameter is **mandatory**: it triggers the material's internal initialization, which reads the gravity stress state and populates stress-dependent secondary parameters (`Ado`, `z_max`, `h0`, `c_dr`, `c_kaf`, …). Without it, those parameters stay at their sentinels and the first plastic computation **divides by zero**, producing `Vector::operator/(double fact) - divide-by-zero error` → NaN residuals → `analyze` returns `-3`.

The OpenSeesPy form (verified against the [official PM4Sand cyclic-simple-shear example](https://openseespydoc.readthedocs.io/en/latest/src/pm4sand_cyc_cal.html), line 191):
```python
ops.setParameter("-val", 0, "-ele", ele_tag, "FirstCall", "<matTag_as_STRING>")
```

Two failure modes when this is wrong:
- **Passing the matTag as an int** → `"Invalid String Input!"` (openseespy stringifies trailing positional args but rejects a bare int in the parameter-name slot).
- **Dropping the matTag entirely** → the call succeeds silently, but PM4Sand's initialization never fires → NaN on the first plastic step.

> **Correction to §12ab point 3:** the §12ab PostShake lesson ("drop the trailing tag") applies **only to PDMY02's `PostShake` parameter**, where the trailing integer is unused. It does **not** generalize to PM4Sand's `FirstCall`, where the trailing matTag is the routing key. When in doubt, match the Tcl source's trailing args exactly.

#### 2. Plastic-Gravity Solver for PM4Sand: KrylovNewton + dt=1.0

PM4Sand's tangent near the elastic→plastic yield surface defeats plain Newton-Raphson — it cycles at Norm just above tol or, with FirstCall mis-fired, hits a divide-by-zero producing NaN. The fix is identical to the §12ae recipe for PDMY02:

```python
ops.algorithm("KrylovNewton")
ops.test("NormDispIncr", 1.0e-4, 50, 1)
ops.analyze(10, 1.0)   # plastic gravity: 10 steps × dt=1s
```

KrylovNewton's secant acceleration escapes the yield-surface cycle. Elastic gravity stays Newton (it always converges).

#### 3. Fictitious-Mass Helper Must Be Scoped to a Single ndf

The §12ag `_ensure_minimum_mass()` helper iterated `ops.getNodeTags()`. In a coupled u-p soil model with a Lysmer dashpot, the soil nodes are ndf=3 (ux, uy, pwp) but the dashpot nodes are ndf=2 (ux, uy), built in a sub-builder. Calling `ops.mass(tag, m1, m2, m3)` on a 2-DOF dashpot node raises `Node::setMass - incompatible matrices`.

Fix: pass the soil-node tag set explicitly and only patch those:
```python
def _ensure_minimum_mass(soil_node_tags, min_mass=1.0e-9):
    for tag in soil_node_tags:           # ndf=3 soil nodes only
        masses = [ops.nodeMass(tag, dof) for dof in (1, 2, 3)]
        if any(m < min_mass for m in masses):
            ops.mass(tag, *[max(m, min_mass) for m in masses])
```

General rule: **whenever a model mixes ndf** (soil+structure, fluid+solid, dashpot+frame), every helper that touches node DOFs must be scoped to one ndf group. Iterate by tag-set, not by `ops.getNodeTags()`.

#### 4. `ops.analysis("Transient")` Is Required After `wipeAnalysis()` for Manual Loops

`run_analysis` calls `ops.wipeAnalysis()` between gravity and dynamic. This clears the analysis object. The SmartAnalyze path works because SmartAnalyze instantiates its own analysis internally — but a manual `ops.analyze(1, dt)` loop requires the analysis object to be reconstructed first:

```python
ops.constraints("Penalty", 1.0e15, 1.0e15)
ops.test(...)
ops.algorithm("Newton")
ops.numberer("RCM")
ops.system("ProfileSPD")
ops.integrator("Newmark", 0.5, 0.25)
ops.analysis("Transient")               # ← REQUIRED after wipeAnalysis()
ops.rayleigh(A0, A1, 0.0, 0.0)
```

Without it: `"WARNING No Analysis type has been specified"` followed by `opensees.OpenSeesError` on the first `ops.analyze()` call.

#### 5. ODB Slimming for Large Transient Soil Models

For a 10,050-element SSPquadUP / 16,505-step model, the dominant runtime cost was `fetch_response_step()` querying all elements for stress/strain — and per §12ad those results were **silently all-zeros** anyway (SSPquadUP's single Gauss point isn't supported by opstool's projection). Disable the wasted work:

```python
odb = opst.post.CreateODB(
    odb_tag=1,
    save_nodal_resp=True,
    save_plane_resp=False,              # all-zeros for SSPquadUP; pure overhead
    compute_mechanical_measures=False,
)
```

Combined with `ODB_EVERY_N = 200` (≈82 ODB samples over 16,500 steps — well under the ≤500 target) and a manual Newton loop at the CFL-limited dt=0.001, the dynamic phase runs in a tractable time. PM4Sand's constitutive evaluation on 10,000+ elements is genuinely expensive (per-step tangent is ~5–10× PDMY02) — there is no algorithmic shortcut for that; the optimizations above remove only the *wasted* work.

#### 6. Per-Case Parametric Mesh via .dat Files

When the source Tcl is a GiD-generated parametric sweep (many cases, identical materials/analysis, different meshes), do NOT try to re-derive the mesh in Python. The GiD mesh is irregular (free-field column at finite distance, non-uniform X spacing) and not reproducible from a formula. Instead:

- Copy the 4 GiD `.dat` files per case (`nodeInfo`, `elementInfo`, `nodeFixitiesInfo`, `nodeEqualDOFInfo`) into `cases/<case>/`.
- Extract the few per-case tags that live only in the Tcl (dashpot element/nodes, load node, base master, motion dt/nsteps) into a `case_meta.json` via a throwaway extractor.
- A single parametric `model.py` reads `cases/<case>/` at build time, selected via `python model.py <case>`.

This avoids 18 near-duplicate Python files while staying byte-faithful to each source mesh.

#### Detection / Rules

- **PM4Sand elastic→plastic NaN** → check `FirstCall` is being set with the trailing matTag **as a string**; check plastic gravity uses KrylovNewton + dt=1.
- **"Invalid String Input!" from setParameter** → a trailing int was passed where a string token is expected; pass it as `str(mat_tag)` (or read it raw from the Tcl line via `line.split()[6]`, which is already a string).
- **`Node::setMass - incompatible matrices`** → a mixed-ndf model called the mass helper on a node of the wrong ndf; scope the helper to one tag-set.
- **`WARNING No Analysis type has been specified` after a manual `ops.analyze()`** → missing `ops.analysis("Transient")` after `wipeAnalysis()`.
- **Large transient soil model "running but slow"** → check `save_plane_resp`/`compute_mechanical_measures` on single-Gauss-point elements (§12ad); they're all-zeros and pure overhead.

---

### §12ai — Truss Tags in `frame_tags` Crash opstool's Basic-Force Extractor (v1.33.0)

Source: `GutierrezSotoMariantonieta` — 3D self-centering post-tensioned steel braced frame (STKO 13-file build → Python), where PT strands are modelled as `truss` elements.

#### 1. A truss returns a length-1 basic force; opstool assumes length 6

`opstool.post._get_response._get_beam_basic_resp()` builds the 6-component basic-force vector (`N, MZ1, MZ2, MY1, MY2, T`) for every tag in `frame_tags`. It special-cases response lengths **0** (fill `[0.0]*6`) and **3** (a 2D beam → pad to 6). Any other length falls through to the sign-flip block, which indexes `resp[1]`:

```python
resp = ops.eleResponse(ele_tag, "basicForces")   # truss → [N], length 1
if len(resp) == 0:        resp = [0.0]*6      # no
elif len(resp) == 3:      resp = [...]         # no
resp = [resp[0], -resp[1], ...]                # ← IndexError: list index out of range
```

A `truss` element legitimately returns only `[N]` (axial force) — it carries no moments. So passing any truss tag to `frame_tags` raises `IndexError: list index out of range` inside `CreateODB` / `FrameRespStepData`, **before any analysis step is collected** — the ODB constructor calls `_set_resp()` at init.

#### 2. Symptom and fix

**Symptom:** `CreateODB(…, frame_tags=[…])` crashes at construction with the traceback bottoming in `_get_beam_basic_resp` → `resp = […, -resp[1], …]` → `IndexError: list index out of range`. The model is fully built (mesh prints, materials define), but no analysis runs.

**Fix:** Keep truss tags out of `frame_tags`. Trusses are axial-only and don't fit the beam-column basic-force schema. If PT/axial force time histories are needed, record them directly:

```python
# frame_tags = beam-columns only — NO truss tags
key_frames = [1001, 1002, …]               # elasticBeamColumn tags
odb = opst.post.CreateODB(
    odb_tag=1,
    save_nodal_resp=True,
    save_frame_resp=True,
    frame_tags=key_frames,                 # beam-columns only
    # save_truss_resp=True + truss_tags=[6011, 6051] is safe if truss data is wanted
)
# PT axial force, on demand:
# ops.eleResponse(6011, "basicForces")  → [N]
```

`save_truss_resp=True` with `truss_tags=[…]` uses opstool's dedicated truss-response path (length-1 aware) and is the correct channel for axial-force data — never `frame_tags`.

#### 3. Cross-reference: `node_tags` filtering still breaks deformed plots (§12u)

The same model hit a second, non-fatal opstool quirk after the truss fix: passing `node_tags=[604, 2011, 2051]` to `CreateODB` records displacements for only those 3 nodes, but `plot_nodal_responses(defo_scale=True)` tries to deform all 282 mesh nodes → `operands could not be broadcast together with shapes (3,3) (282,3)`. This is the §12u failure mode restated for the STKO-converted 3D frame: **omit `node_tags` (pass `None`) when the ODB will feed a deformed-shape plot of the full mesh.** The two fixes are independent — the truss bug is fatal-at-init, the node_tags filter is non-fatal-at-postprocess.

#### Detection / Rules

- **`IndexError: list index out of range` at `resp[1]` inside `_get_beam_basic_resp`** → a non-beam element (truss, or any element whose `basicForces` response is not length 0/3/6/12) is in `frame_tags`. Grep the model's element definitions for the tags in `frame_tags` and remove the truss/link/zeroLength tags.
- **`IndexError` traceback originates in `CreateODB.__init__` / `_set_resp`** (not inside an analysis loop) → the crash is at ODB construction, i.e. a tag-list problem, not a convergence or step problem.
- **`operands could not be broadcast together with shapes (N,N) (M,N)` from `plot_nodal_responses`** where N ≪ M → `node_tags` was filtered (§12u); set `node_tags=None` for full-mesh deformed plots.
- **Rule:** `frame_tags` accepts **beam-column elements only** (`elasticBeamColumn`, `forceBeamColumn`, `dispBeamColumn`, `elasticTimoshenkoBeam`, …). Axial-only elements (`truss`, `corotTruss`) use `truss_tags`; link/spring elements (`twoNodeLink`, `zeroLength`) use `link_tags`.

### §12aj — Chevron CBF Pushover: Recovery-Ladder Load-Factor Spam Is Not Step-0 Failure; EnergyIncr+Newton Stalls in the Brace-Buckling Transition (v1.34.0)

Source: `BradleyCameron_R3` — 3-story chevron concentrically braced steel frame (Sizemore 2017 framework / Bradley et al. 2021, DesignSafe PRJ-2957), conformant re-conversion of the non-conformant `bradley2021_Building_system`. 2D, 877 nodes, 916 elements (dispBeamColumn fiber W/HSS sections + elasticBeamColumn + truss + zeroLength weld/gusset springs + zeroLengthSection angle fuses), 260 uniaxial materials, IMKBilin beam hinges. Pushover via the source's `B-AdvanceAnalysis` recovery ladder (4 tols × 3 step-factors × 8 algorithms) ported as a manual `ops.analyze(1)` loop.

#### 1. A pushover that "fails on step 0" but writes 51 curve points is converging fine — then stalling

**Symptom (misleading):** the run log ends with:
```
=== Pushover (monotonic) ===
  Target 1/1: drift=10.00% (roof ±1371.6 mm)
  Damping: T1=0.985s T2=0.388s T3=0.269s ...
    convergence failure — stopping.
  -> pushover_curve.csv (51 points)
```
sandwiched between hundreds of `DisplacementControl::newStep(void) - failed in solver` / `domain at load factor 10.6–12.1` / `Umfpackgenlinsolver::solve` warnings. The first instinct is "pushover fails at step 0 with an absurd load factor of ~12" → suspect the §12z lateral-pattern-frozen-at-λ=0 bug.

**Reality:** the `state.history` list (which feeds `pushover_curve.csv`) is only appended **after** a converged step in `_advance_step`, and the early-failure return path skips the append. So 51 CSV points = **51 pushover steps genuinely converged** (drift 0.002% → 0.15%, base shear 0.7 → 145.7 kip). Step **52** then fails, and the load-factor-10+ warnings are the **recovery ladder firing on that failing 52nd step** — the DisplacementControl integrator, hunting for a step that converges, drives the load factor up as it fails. They are a *symptom of the stall*, not evidence of step-0 failure.

**Diagnostic protocol (do this before blaming loadConst):**
1. `wc -l pushover_curve.csv` — if it has many points (not 0/1), the pushover ran for a while before failing. The number of points = number of converged steps.
2. Cross-check `len(state.history)` against the `step_count` in the run log.
3. Only if the CSV is empty AND the first log line after `=== Pushover ===` is the failure should you suspect §12z pattern freezing. A non-empty CSV rules it out.
4. Confirm the §12z ordering regardless: `define_pushover_loads()` must be called **after** `run_gravity()` (after `loadConst`). This model already did that correctly.

#### 2. The real cause: `EnergyIncr` @ 1e-8 + Newton is too tight for fiber-section brace buckling

The curve dies at **0.15% roof drift** with base shear **still rising monotonically** (no `Vb>0` collapse sign-flip) and **zero weld fractures** (no `WF`/`WR` events). This is the **elastic-to-brace-buckling transition** — the regime where fiber-section `dispBeamColumn` braces (Steel02 composites + corotational transform) begin to soften and the global tangent becomes ill-conditioned. The baseline `test("EnergyIncr", 1e-8, 200)` + `algorithm("Newton")` cannot track it; even the full 4×3×8 recovery grid (tolerances down to 1e-5, step-shrink down to dx/100, all 8 algorithms) fails to converge step 52.

This is the **same fiber-section tangent-ill-conditioning class of problem documented in §12x point 8 and §12z point 3/5** — restated here for a steel CBF (the §12x/§12z sources were RC frames). The fix is the §12z-3/§12z-5 recipe:

```python
# SmartAnalyze kwargs (preferred, §12z corrected):
analysis = opst.anlys.SmartAnalyze(
    analysis_type="Static",
    testType="NormDispIncr",      # ← was EnergyIncr
    testTol=1.0e-5,               # ← was 1e-8
    testIterTimes=200,
    tryAlterAlgoTypes=True,
    algoTypes=[40, 10, 20, 30],   # KrylovNewton primary
    tryLooseTestTol=True,
    looseTestTolTo=1.0e-4,
    tryAddTestTimes=True,
    testIterTimesMore=[50, 100],
)
```
For this model's documented SmartAnalyze **exception** (§3c/§12p: the source's custom `B-AdvanceAnalysis` recovery ladder + recursive `B-RemoveWeld` element-removal are not exposed by SmartAnalyze), apply the same tuning to the manual loop: baseline `test("NormDispIncr", 1.0e-5, 200)` + `algorithm("KrylovNewton")`, and if element-level `dispBeamColumn update` failures appear past ~1%, shrink `PUSHOVER_DX` from 0.02 in (§12z-4).

**Rule of thumb:** if a pushover CSV ends with base shear still monotonically increasing (no sign flip) and no fracture/removal events fired, the stall is a **solver-tuning limit in the softening transition**, not a modeling error. Verify the model is sound (eigen period, mass, load pattern — see point 4) before tuning the solver.

#### 3. `ops.rayleigh()` global is a documented simplification — the source uses per-region damping

The source (`B-Regions.tcl`) applies Rayleigh damping via two `region -rayleigh` calls: stiffness-proportional `a1_mod` on ~400 elastic beam-column elements (region 1, `betaKcomm` slot), mass-proportional `a0` on the 3 mass nodes (region 2). The R3 model collapses both into a single global `ops.rayleigh(a0, 0.0, 0.0, a1_mod)`. The eigen periods match (T1=0.907s pre-damping → 0.985s damped), so the simplification is numerically faithful for this model. But: global `ops.rayleigh` applies `a1_mod` to **all** elements including the zeroLength weld/gusset springs and zeroLengthSection fuses, which the source excludes. For models where spring/element damping materially changes the result, port the per-region calls exactly (`ops.region(tag, "-ele", *eles, "-rayleigh", a0, betaK, betaKinit, betaKcomm)`).

#### 4. Validation checklist that confirms "the model is correct, only the solver stalls"

Before tuning the solver, confirm these (all verified PASS for BradleyCameron_R3):
- **Data extraction vs source Tcl:** weld_eles `[846,858,870,882,894,906]`, ebc_eles `[845,857,869,881,893,905]`, capacities `[267.3,237.6,207.9,267.3,237.6,207.9]` kip, weld_mat `[8,7,6,5,4,3,2,1]` — exact match to `B-WeldInfo.tcl`.
- **Eigen period:** pre-gravity T1 ≈ 0.9s for a 3-story ~13.7 m CBF — physically reasonable.
- **Lateral mass:** on DOF1 (UX), total 7.92 kip·s²/in = 3061 kip seismic weight — correct for a 3-story frame; mass on DOF2/3 is the 1e-9 numerical-stub value, not a mis-scale.
- **ELFP load pattern:** sum of `lat1+lat2+lat3` × 2 column lines = 196.1 kip at LF=1.0 — matches ASCE 7-10 source.
- **§12z ordering:** `define_pushover_loads()` after `run_gravity()` — correct.
- **Gravity:** reaches lf=1.00 via the documented two-phase fiber-section workaround (§12x); `loadConst` applied.

#### Detection / Rules

- **`pushover_curve.csv` has N>1 points but the log shows `convergence failure` + load-factor >10 warnings** → the pushover ran N steps then stalled in a softening transition; the load-factor spam is the recovery ladder on the failing step, NOT step-0 failure. Do NOT chase §12z/§12i pattern-freezing.
- **CSV ends with base shear monotonic (no sign flip) and zero `WF`/`WR`/fracture events** → solver-tuning limit, not a modeling error. Apply §12z-3/5 (`NormDispIncr` + `KrylovNewton` + relaxed tol).
- **`grep -c "    WF\|    WR" run.log` == 0** on a CBF pushover that dies before ~2% drift → weld/EBF removal logic never engaged; the curve never reached brace-fracture demand. The stall is purely numerical.
- **Rule:** for fiber-section steel CBF/BRBF pushovers, default the solver to `NormDispIncr` @ 1e-5 + `KrylovNewton` primary (§12z-3/5). `EnergyIncr` @ 1e-8 + Newton is appropriate only for purely elastic or mildly nonlinear phases.
- **Rule:** a non-empty `state.history`/CSV is the authoritative evidence that pushover steps converged — trust it over the wall of solver warnings, which accumulate from the failing step's recovery attempts.

### §12ak — equalDOF + zeroLength Hinge Architecture: Base Shear Lives at the Column-Base Node, Not the Fixed Node; Penalty Reads Zero, Transformation Stalls (v1.35.0)

Source: `Bessette` — 3D fixed-base RC1 structure pushover (JP3 Parametric Study, Caroline Bessette 2024). 18 nodes, 13 elasticBeamColumn + 4 zeroLength IMK springs, gravity + monotonic DisplacementControl pushover to 10% drift.

#### 1. Concentrated-plasticity hinge topology (equalDOF + zeroLength on RZ only)

The source models each rotational hinge as a **zeroLength between two coincident nodes**, with 6 materials on 6 DOFs — stiff elastic on DOFs 1-5 (UX,UY,UZ,RX,RY = rigid) and the IMK hinge on DOF 6 (RZ only). The two coincident nodes are additionally tied by `equalDOF(master, slave, 1, 2, 3)` so they share translations. At a column base this looks like:

```
fixed node 5000001 ──zeroLength(600001)── column-base node 3000001 ── column ...
   (fix 1 1 1 1 1 1)        │                  (equalDOF 5000001→3000001 UX UY UZ)
                     mat: stiff,stiff,stiff,
                          stiff, IMK, stiff
                     dir:   1     2    3
                              4    5    6
```

Because `equalDOF` makes 5000001 the translation master, the **translational stiffness and shear flow through the column into node 3000001**, not into the fixed node. The zeroLength between them carries **only the RZ moment** (the IMK hinge). Verified: `nodeReaction(5000001, 1) ≈ 3.5e-31` (zero) while `nodeReaction(3000001, 1) = -13770 N` (the full column shear) — and `eleForce(600001) = [0,0,0,0,-29.4e6,0, ...]` (pure RY moment, no translation).

#### 2. The base-shear bug: reading reactions at the fixed node gives zero

**Symptom:** the pushover converges all 400 steps to 10% drift with correct displacements, but the capacity curve (`pushover_curve.csv`) is all zeros — `nodeReaction(NODE_BASE, 1)` returns ~3e-31 at every step.

**Root cause:** `base_shear = sum(nodeReaction at fixed nodes)` is wrong for this topology. The fixed node's translational DOFs carry no reaction because the equalDOF constraint diverted the shear to the column-base node.

**Fix:** read base shear from the **column-base nodes** (the nodes directly above the zeroLength springs), not from the fully-fixed nodes:

```python
# WRONG — fixed node translational reaction ≈ 0 under equalDOF+zeroLength-on-RZ
def _base_shear():
    return ops.nodeReaction(NODE_BASE_L, 1) + ops.nodeReaction(NODE_BASE_R, 1)

# CORRECT — column-base node carries the shear (equalDOF diverted it here)
def _base_shear():
    return ops.nodeReaction(3000001, 1) + ops.nodeReaction(3000002, 1)
```

**Diagnostic protocol:** if a pushover converges with correct displacements but `nodeReaction` at the "base" returns ~0, dump the full reaction vector at several nodes:
```python
ops.reactions()
for n in [fixed_node, column_base_node, roof_node, ...]:
    print(n, ops.nodeReaction(n))
```
The shear will appear at whichever node the column's translational stiffness lands on. For a direct-fixity column it's the fixed node; for an equalDOF+zeroLength hinge it's the node just above the spring.

#### 3. Penalty vs Transformation: reactions are fine in both, but Transformation stalls the pushover

A minimal cantilever test shows **both** `constraints("Penalty",1e15,1e15)` and `constraints("Transformation")` return correct `nodeReaction` at a directly-fixed node. So Penalty is NOT inherently broken for reactions — the §2 zero-reaction is purely the equalDOF topology, not the constraint type.

However, switching the *pushover* from Penalty to Transformation (to "fix" the imagined reaction bug) **broke convergence**: Transformation stalled at 1.69% drift (67 steps) where Penalty converged the full 400 steps to 10%. The equalDOF + zeroLength + elasticBeamColumn combination is better-conditioned under Penalty (which regularises via stiff springs) than Transformation (which eliminates DOFs and can singularise the zeroLength-only rotation DOF). 

**Rule:** for concentrated-plasticity models (zeroLength hinges + equalDOF), prefer `constraints("Penalty", 1e15, 1e15)` for *both* gravity and pushover. Do NOT switch to Transformation expecting better reactions — it will likely stall. To get correct base shear, fix the **node you read from** (§2), not the constraint type.

#### 4. `ops.reactions()` must be called before `nodeReaction` inside a SmartAnalyze loop

SmartAnalyze's `StaticAnalyze`/`TransientAnalyze` advance the solution but do **not** automatically compute the reaction vector. Reading `nodeReaction` without a preceding `ops.reactions()` returns the value from the last time reactions were computed (often stale or zero). Insert `ops.reactions()` immediately before the `nodeReaction`/`nodeDisp` reads in the per-step tracking loop:

```python
for seg in segs:
    ok = analysis.StaticAnalyze(node=ctrl, dof=dof, seg=seg)
    if ok < 0: break
    odb.fetch_response_step()
    ops.reactions()                       # ← populate reactions BEFORE reading
    history.append((drift, _base_shear()))
```

(ODB-based reaction collection via `save_nodal_resp=True` does not need this — `fetch_response_step` handles it. Only manual in-loop `nodeReaction` calls require the explicit `ops.reactions()`.)

#### Detection / Rules

- **Converged pushover with all-zero base shear in the CSV** → the reaction is being read from the wrong node (fixed node under equalDOF+zeroLength-on-RZ topology). Dump `nodeReaction` across nodes to find where the shear actually lands.
- **`nodeReaction(fixed_node) ≈ 1e-31` but `eleForce(spring)` shows a large moment** → confirmed equalDOF-on-translation + zeroLength-on-rotation topology; read base shear from the node above the spring.
- **Transformation pushover stalls early where Penalty converged** → the equalDOF+zeroLength topology is better-conditioned under Penalty; revert to Penalty and fix the read node instead.
- **`nodeReaction` returns stale/zero right after `StaticAnalyze`** → insert `ops.reactions()` before the read; SmartAnalyze does not compute reactions automatically.
- **Rule:** for concentrated-plasticity hinge models, use `constraints("Penalty", 1e15, 1e15)` for the full analysis and read base shear from the column-base nodes (above the zeroLength springs), with `ops.reactions()` called before each in-loop `nodeReaction`.

### §12al — Imperial→N-mm Mass Conversion: Do NOT Re-Multiply P[N]/g by kip/inch; Rank-Deficient Mass Defeats ARPACK Eigen (v1.36.0)

Source: `VividConcrete` — 3D circular RC bridge column, fiber-section `forceBeamColumn` + `zeroLengthSection` bar-slip, gravity → Rayleigh damping → seismic time-history (Zhong, Stanford 2017). 3 nodes, ~26 materials, imperial source (in, kip, ksi).

#### 1. The double-conversion mass trap: a 4448× too-heavy mass → T1 off by 80×

**Symptom:** after converting an imperial column model to N-mm-MPa, the eigen analysis returns T1 ≈ 56 s for a 7.3 m column that should be ~0.7 s — and the ARPACK subspace solver fails with `ArpackSolver::Error with _saupd info = -9999 / Could not build an Arnoldi factorization`. The static lateral stiffness checks out correct (hand-calc k ≈ 19000 N/mm matches the model's 16950 N/mm), so the model is not a mechanism — the mass is wrong.

**Root cause:** the source defines mass as `-P/g` where P is an axial load and g is gravity. After converting **P to Newtons** (`P_GRAVITY = -522 * kip` → Newtons) and the **length to mm**, the mass is already in N·s²/mm after dividing by g[mm/s²]:

```python
# WRONG — double-converts (P is already in Newtons, not kip)
P_GRAVITY = -522.0 * kip               # already Newtons
mx = -P_GRAVITY / G_INCH * kip / inch  # ÷386.089 × 175.13 → 1,052,267 N·s²/mm
# nodeMass returns 1,053,226 — 4448× too heavy → T1 = 56.6 s

# CORRECT — P[N] ÷ g[mm/s²] = N·s²/mm directly, no extra factor
g_mm = G_INCH * inch                   # 386.089 in/s² → 9806.65 mm/s²
mx = -P_GRAVITY / g_mm                 # → 236.77 N·s²/mm → T1 = 0.849 s ✓
```

The error multiplies by `kip/inch` (175.13) a second time. Because force was *already* converted to Newtons, the resulting mass is too large by the kip→N factor (4448). This is the mirror image of the §12j `kg` trap: there the issue is `kg` being defined as 1.0 (= tonne); here it's applying a force conversion factor twice to a quantity that was already converted.

**Detection:** T1 off by ~4000-5000× (the kip factor) AND/OR `nodeMass(node, dof)` returning ~1e6 for a node that should be ~200 → a mass double-conversion. Cross-check: `T_expected = 2π·√(m/k)` with hand-calc k from `3EI/L³`.

**Rule:** when the source computes mass from a force (`m = P/g`), convert P to Newtons and g to mm/s² **once each** — the quotient is N·s²/mm directly. Never multiply by `kip/inch` or `kg` afterward. For mass given directly in imperial units (kip·s²/in), multiply by `kip/inch` (= 175.13) — but for mass *derived* from an already-converted force, do not.

#### 2. Rank-deficient mass matrix defeats the ARPACK subspace eigen solver

**Symptom:** `ops.eigen(3)` raises `OpenSeesError` / prints `ArpackSolver::Error with _saupd info = -9999 / Could not build an Arnoldi factorization / IPARAM(5) - the size of the current Arnoldi factorization is 3`.

**Root cause:** the column carries mass on only ONE node (node 3) and only on 2 DOFs (UX + a small RY inertia). The mass matrix M is rank-2, so the generalized eigen problem `Kφ = ω²Mφ` has ~zero eigenvalues that the ARPACK Lanczos iteration cannot resolve — the Arnoldi factorization collapses at size 3.

**Fix:** use `-fullGenLapack` (the source's choice). This **deviates from §12h-2** (which prefers the default subspace solver for *stiffness-contrast* models) — but the issue here is mass rank, not stiffness contrast. `fullGenLapack` factorizes M⁻¹K directly (full Lapack `dsygv`) and returns the modes reliably even for rank-deficient M:

```python
# CORRECT for rank-deficient mass models
lam = ops.eigen("-fullGenLapack", N_EIGEN)
# returns 3 modes; the high-frequency ones are mass-rank artifacts but the
# low modes (the ones Rayleigh damping uses) are physical.
```

**Caveat:** with rank-deficient M, the higher modes are mass-rank artifacts (e.g. T3 ≈ 0.0005 s). Rayleigh damping fits ζ on modes 1 & 3 per Chopra — if mode 3 is spurious, prefer fitting on modes 1 & 2, or add a small regularizing mass to other DOFs so M is full-rank.

**Detection / Rules:**
- **T1 off by ~4000× AND ARPACK Arnoldi failure together** → mass double-conversion (§1). Fix the mass first; the eigen may then work with the default solver.
- **`ArpackSolver::Error info = -9999` with correct stiffness (static k matches hand-calc)** → rank-deficient mass matrix; switch to `ops.eigen("-fullGenLapack", N)` (deviation from §12h-2, justified for mass-rank not stiffness-contrast).
- **Mass defined as `P/g` with P already in Newtons** → do NOT multiply by `kip/inch`; `P[N]/g[mm/s²]` is the mass in N·s²/mm directly.
- **Rule:** verify `nodeMass(node, dof)` after `define_nodes()` against a hand calc (`m = P/g`) before running eigen — a 4448× discrepancy is the double-conversion signature.

---

### §12am — Long Cyclic Protocols: Manual Fixed-Increment Fallback Chains Stall Mid-Protocol; Use `opst.anlys.SmartAnalyze` + `vis_defo` for the Peak Plot (v1.37.0)

Source: `VividConcrete_RCconc_full_subassembly` — 3D square RC column subassembly, fiber-section `forceBeamColumn` (6 Gauss-Lobatto IPs, per-IP confined/unconfined `Concrete02` + `ReinforcingSteel`/`DuctileFracture` + `Hysteretic` shear) with two `zeroLengthSection` bar-slip springs (`Bond_SP01`), gravity → displacement-controlled cyclic over a **22 455-point** experimental protocol (Zhong, Stanford 2017). 4 nodes, ~60 materials, imperial source (in, kip, ksi).

#### 1. The fixed-increment fallback chain: a faithful 1:1 port of the source's `RunStaticLoading.tcl` STALLS mid-protocol

**Symptom:** the cyclic run (port of `RunStaticLoading.tcl`, `LoadType=CyclicStep`) converges cleanly to step ~14 528 (~1.6% drift, 44 mm) then stops — every fallback in the source's manual chain (Newton → Newton `-initial` → `ModifiedNewton` → `ModifiedNewton -initial` → `Broyden 20` → `NewtonLineSearch 0.8 100`) fails on step 14 529. This is far short of the 6.23 in (5.8% drift, 158 mm) protocol peak — a real ductile RC column should sustain much higher drift.

**Root cause:** these fallbacks all retry the **same full increment** with a different algorithm. On a hard unloading step the fiber section's tangent is ill-conditioned over the *whole* increment, so no single full-size step converges — but a *sub-divided* increment does. The source Tcl would hit the same wall in an equivalent OpenSees build; this is a single-step numerical stall during unloading, **not genuine collapse**: the same step fails even with `DuctileFracture` removed (in fact it fails *earlier*, at ~step 13 475, with `ForceBeamColumn3d::update() - section failed in setTrial`).

**Fix:** drive the cyclic with `opst.anlys.SmartAnalyze` (the repo convention — `elkady2019`, `padgett_jamie`), which layers adaptive sub-stepping (`relaxation`, `minStep`) on top of the alternate-algorithm retries:

```python
analysis = opst.anlys.SmartAnalyze(
    analysis_type="Static",
    tryAlterAlgoTypes=True,
    algoTypes=[40, 10, 20, 30, 50, 60],   # Newton, Newton -initial,
    #     Newton -initialThenCurrent, Newton -Secant, NewtonLineSearch,
    #     NewtonLineSearch -type Bisection
    tryAddTestTimes=True,
    testIterTimesMore=[50, 100],
    relaxation=0.5,
    minStep=1.0e-3,
)
```

**Protocol preservation — feed one target increment at a time:** SmartAnalyze's `static_split` sub-divides *within* a single target. To keep the recorder at **one row per experimental target** (so `disp.out`/`force.out` align 1:1 with the 22 455-pt protocol — essential for hysteresis plotting), iterate over the load history and hand SmartAnalyze one increment per target:

```python
current_disp = 0.0
for i, target in enumerate(load_history):
    incr = target - current_disp
    segs = analysis.static_split([incr], maxStep=abs(incr))
    for seg in segs:
        rc = analysis.StaticAnalyze(node=NODE_CTRL, dof=2, seg=seg)
        if rc < 0:
            break          # genuine failure — stop, report the step
    else:
        current_disp = target
        continue
    break                   # break outer loop on inner failure
```

**Validation:** the previously-failing step now passes (verified by driving to step 14 528 then handing step 14 529 to SmartAnalyze — `PASSED`); the full run completes 22 455/22 455 steps, peak drift ±158 mm (protocol max), base shear ±13.25 kip (vs the stalled ~4.6 kip), 44 force sign-changes → proper energy-dissipating loops.

**Detection / Rules:**
- **Cyclic run stalls at a fraction of the protocol peak, every manual fallback failing on the same step, with column drift still well below expected capacity** → fixed-increment retry exhaustion on a hard unloading step, not collapse. Switch to `SmartAnalyze` with `relaxation`/`minStep`.
- **Confirm not-physical before tuning:** re-run with the suspect damage material (e.g. `DuctileFracture`) removed; if it still stalls (or stalls earlier) the cause is fiber-section tangent ill-conditioning at that increment, not the fracture trigger.
- **Preserve protocol granularity:** feed SmartAnalyze one target increment at a time via `static_split([incr], maxStep=abs(incr))`, NOT the whole history as one protocol — otherwise the recorder loses 1:1 alignment with the experimental targets.
- **Cross-ref §12v / §12z / §12aj:** the same fiber-section tangent-ill-conditioning class (softening `dispBeamColumn`/`forceBeamColumn` fiber sections) that defeats Newton in pushover; for cyclic the cure is adaptive sub-stepping (SmartAnalyze) rather than the single-fiber-softening algorithm recipe.

#### 2. `plot_nodal_responses(defo_scale=True)` in `post_process` — peak-deformed plot silently missing

**Symptom:** after a long cyclic run, `output/vis_05_peak_deformed.html` is absent (only `vis_01..04` exist), but `post_process` reports nothing — the failure is swallowed by a bare `except Exception`.

**Root cause:** `post_process` called `opst.vis.plotly.plot_nodal_responses(..., defo_scale=True)` directly. While `defo_scale=True` is technically accepted (auto-scale), the call bypassed the repo's `vis_defo` helper (`standards/vis_utils.py`), which exists precisely to encapsulate the correct `absMax`-step + numeric-scale kwargs. The wrapped `try/except` hid the real error.

**Fix:** use the repo helper with a numeric scale:

```python
from vis_utils import vis_defo          # already imported alongside vis_nodes etc.
vis_defo(output_dir, filename="vis_05_peak_deformed.html",
         odb_tag=ODB_TAG, resp_dof="UY", resp_type="disp", scale=10.0)
```

`vis_defo` reads the ODB's `absMax` step by default, so it captures the peak-deformed shape. **Rule:** never call `opst.vis.plotly.*` directly from a `model.py` — go through the `vis_utils` wrappers (`vis_nodes`/`vis_model`/`vis_loads`/`vis_pre_analysis`/`vis_defo`/`vis_anim`). Cross-ref §12u/§12ai: the same `plot_nodal_responses` path is where `node_tags=`/`defo_scale=` break deformed plots.

#### 3. `openseespywin` Python-3.8 gate — the right env is the conda `opensy` env

The pure-Python `openseespy` Windows backend (`openseespywin`) `raise RuntimeError('Python version 3.8 is needed for Windows')` on any interpreter ≠ 3.8 — so `python model.py` with the system Python (3.14) fails at import even though `openseespy` is pip-installed. The repo's runnable interpreter is the **`opensy` conda env** (`C:/Users/micha/miniconda3/envs/opensy/python.exe`, Python 3.12.12), which has working `openseespy` + `opstool`. **Rule:** run all Windows models with the `opensy` env interpreter; do not trust "syntax-checked only, not executed" caveats from sessions that lacked a working env — re-validate end-to-end once the env exists.

---

### §12an — 3D Frame-Wall Building: rigidDiaphragm + Transformation Constraints, Per-Story/Per-IP Section Tag Scheme, corotTruss ODB Scoping (v1.38.0)

Source: `VividCond_UCSD_full_fivestory` — 5-story RC building (Zhong, Stanford/UCSD 2017–2019): two 2-bay perimeter moment frames + 2 planar shear walls + diagonal `corotTruss` braces + rigid floor diaphragms. 54 nodes, 72 elements, ~120 per-IP sections, ~150 materials, imperial source (in, kip, ksi).

#### 1. `rigidDiaphragm` needs `Transformation` (not `Plain`) constraints — for both gravity and dynamic

**Symptom:** with `constraints("Plain")`, gravity either fails to converge or the diaphragm-coupled DOFs drift; `constraints Transformation` is required wherever `rigidDiaphragm` (a multi-point constraint) is used.

**Rule:** any model with `rigidDiaphragm`/`equalDOF`/MP constraints must use `constraints("Transformation")` for **both** the gravity (LoadControl) phase and the dynamic (Newmark) phase. `Plain` cannot distribute MP-constraint reactions. This is consistent with §12x-6 (STKO MP models → Transformation); the exception (Penalty, §12ak) is only for zeroLength-hinge concentrated-plasticity models, not rigid-diaphragm buildings.

#### 2. Per-story × per-IP tag scheme — make every helper take an *absolute* tag, not `(story, relative)`

**Symptom:** `MapOfTaggedObjects::addComponent - not adding as one with similar tag exists, tag: 201` — a material tag collides on the second story.

**Root cause:** a helper `_df(story, tag, ...)` was called as `_df(s, 201, ...)` intending the *story-relative* DF tag, but the helper used `tag` directly (201) instead of `s*1000 + 201` — so story 0 wrote tag 201 and story 1 tried to write the same 201. The helper's `story` parameter was dead.

**Fix:** helpers that define tagged objects must take the **absolute** tag as computed by the caller — drop the dead `story` param. The source's tag scheme is `story*1000 + <group>` where group encodes the material/section kind:
- concrete: `story*1000 + ip*10 + {1 col/wall-cover, 2 beam-cover, 4 col/wall-core, 5 beam-core}`
- steel/DF/Bond: `story*1000 + {101..105}` (Steel02), `{201..205}` (DF), `{301..305}` (Bond_SP01)
- sections: `story*1000 + {100,200,300,400} + ip` (beam/col/wall/slab)

**Rule:** when porting a Tcl `for {set story_id ...}` loop that builds `expr $story_id*1000+...` tags, compute the absolute tag in Python *before* passing to any helper; never let a helper reconstruct it from a story index unless the helper signature genuinely needs both. Verify with a build smoke-test that reaches the second story.

#### 3. `corotTruss` braces must use `truss_tags`, not `frame_tags`, in the ODB

**Symptom (pre-empted, §12ai):** `CreateODB(frame_tags=[...])` that includes `corotTruss` element tags raises `IndexError: list index out of range` at ODB construction — a truss's `basicForces` is length-1 (`[N]`) but opstool's beam-force extractor only special-cases lengths 0 and 3.

**Fix:** for this model `save_frame_resp=False` (nodal responses suffice for deformed plots + roof drift). If frame forces are needed later, keep `frame_tags` beam-column-only and add `save_truss_resp=True` + `truss_tags=[...]` for the braces. Cross-ref §12ai.

#### 4. Triaxial-GM source with no base_motions in repo — single-component NR94 substitute (established pattern)

The source `RunTests.tcl` loops over 13 triaxial (X/Y/Z) base motions (`./base_motions/`, not in the repo). The repo's only GM file is the single-component `NR94cnp.txt` (Northridge-1994, dt=0.01 s, ~2495 pts, g-units). Following the established VividConcrete/elkady2019 pattern: load NR94 as a single `UniformExcitation` in direction 1 (X) for end-to-end validation, and make `run_dynamic()` generic (`GM_FILE`/`GM_DT`/`GM_NPTS`/`GM_DIR` params) so real triaxial records drop in when sourced. **Rule:** GM defined *after* `loadConst` (§12i). Validation: T1=0.577 s (physical for a 5-story RC wall-frame), 2495/2495 steps converge, roof drift −172 mm (0.94%), peak inter-story drift 1.39%.

#### 5. Confined-concrete `ke` varies by source — port the *exact* formula, don't reuse another model's

This source's `CreateConcreteMaterial.tcl` uses a **rectangular** confinement factor `ke = ke1·ke2·ke3/(1−rou_cc)` with `ke1 = 1 − n·wi²/(6·b·d)`, `ke2 = 1 − 0.5·s/b`, `ke3 = 1 − 0.5·s/d` — *different* from the simpler `(nl−2)/nl·(1−s/b)` used in the VividConcrete column models. **Rule:** when a repo has multiple Zhong-framework sources, do not assume the concrete helper is shared — read each source's `CreateConcreteMaterial.tcl` and port its `ke` expression verbatim. The two formulas give different `fpc`/`epsc0` and reusing the wrong one silently biases the section capacity.

#### 6. Step-slider deformed shape — added `vis_slider()` to `standards/vis_utils.py`

The repo had `vis_defo` (V5 peak) and `vis_anim` (V7 animation) wrappers but **no slider wrapper** — the reference `VividConcrete/model.py` called `plot_nodal_responses(slides=True)` directly, bypassing `vis_utils` (the §12am anti-pattern). Added **`vis_slider(output_dir, filename="vis_06_slider.html", odb_tag=1, resp_dof="UX", resp_type="disp", scale=10.0)`** to `standards/vis_utils.py` (between `vis_defo` and `vis_anim`), wrapping `plot_nodal_responses(slides=True, defo_scale=scale, ...)`. It produces a self-contained HTML with a draggable slider — one frame per collected ODB step, so the user can scrub the deformation evolution. Wired into both `VividCond_UCSD_full_fivestory` and `VividConcrete_RCconc_full_subassembly` `post_process()`. **Rule:** the slider needs ODB frames to have been collected during the analysis (throttled by `ODB_EVERY_N`); with `ODB_EVERY_N=10` over a ~2500-step run the slider has ~250 frames, which is plenty. Note: generating it from an already-saved ODB requires `opst.post.set_odb_path(str(output_dir))` to be active before the call (the ODB is read back from disk in `post_process`).

---

### §12ao — EnergyIncr Tolerance Unit Conversion + equalDOF+Plain nodeReaction Spurious Shear (v1.39.0)

Source: `ZhongKuanshi` — 7-case HystereticSM shear-hinge calibration sweep (Zhong Stanford 2016 / Naish 2015), imperial (in, kip, ksi) → N-mm-MPa.

#### 1. `EnergyIncr` Tolerance Is Unit-Dependent — Scale by kip·in → N·mm

The source Tcl uses `test EnergyIncr $Tol $numIter` with `Tol = 1e-4`. This tolerance is in the model's energy units — **kip·in** in the source. When converting to N-mm-MPa, the EnergyIncr norm scales by the energy unit conversion factor:

```
1 kip·in = 4448.22 N × 25.4 mm = 112,984.8 N·mm
```

So `Tol = 1e-4` in kip·in becomes `Tol = 1e-4 × 112984.8 ≈ 11.3` N·mm. Using the unscaled `1e-4` makes the tolerance **~100,000× too tight**, causing the analysis to stall at ~30% of the cyclic protocol — every step past first yield fails to converge because the energy norm (which involves force × displacement) is 5 orders of magnitude above 1e-4.

```python
# BROKEN — tolerance 100000x too tight for N-mm model
TOL = 1.0e-4  # this was correct for kip-in; in N-mm it's absurdly tight

# CORRECT — scale by energy unit conversion
LBIN2NMM = kip * inch          # 112,984.8 N·mm per kip·in
TOL = 1.0e-4 * LBIN2NMM        # ≈ 11.3 N·mm
```

**Symptom:** Load-factor spam (`domain at load factor > 1e5`) and `EnergyIncr` failures where `Norm deltaX` is tiny (displacement converged) but `EnergyIncr` is 4–6 orders of magnitude above tolerance. The fallback ladder exhausts on every step past ~30% of the protocol.

**Detection:** If a source Tcl with `test EnergyIncr 1e-X` stalls after unit conversion to N-mm, check whether the tolerance was unit-converted. `EnergyIncr` involves `dF · dU` (force × displacement), so it scales by the product of the force and length conversion factors.

**Rule:** When converting `EnergyIncr` tolerance from imperial to N-mm, multiply by `kip * inch` (= 112,985). For `NormDispIncr` (displacement-only norm), multiply by `inch` (= 25.4). For `NormUnbalance` (force-only norm), multiply by `kip` (= 4448.22). **Never** carry over an unscaled tolerance value during unit conversion.

#### 2. `nodeReaction` Under `equalDOF` + `Plain` Constraints Gives Spurious Shear Past Yield

For a shear-hinge subassembly with `equalDOF(master, slave, 1, 3)` + `constraints("Plain")`, reading the base shear via `nodeReaction(fixed_node, dof_2)` returns the **retained-node reaction including the MP-constraint force**. This gives shear values 2–3× the hinge backbone capacity past first yield — physically impossible.

```python
# BROKEN — reaction includes MP-constraint force, 2-3x too high past yield
ops.reactions()
shear = -ops.nodeReaction(NODE_FIX_L, 2)  # → 349 kip when backbone max is 159 kip

# CORRECT — read the zeroLength element's global force directly
ele_forces = ops.eleResponse(ELE_HINGE, "forces")
shear = -ele_forces[1]   # global Y component = hinge shear
```

This differs from §12ak (concentrated plasticity with zeroLength-on-RZ + equalDOF-on-translation): there the shear diverted to the column-base node (read from a different node); here with Plain constraints + a DOF-2-only hinge, the retained-node reaction is contaminated by the constraint enforcement force.

**Symptom:** Hysteresis curve shows shear exceeding the defined backbone capacity (e.g., 349 kip when V4 = 159 kip). The displacement is correct; only the force reading is wrong.

**Rule:** For any model with `equalDOF` + `zeroLength` hinge, read the hinge shear from `ops.eleResponse(hinge_tag, "forces")` (the element's global force vector), not from `nodeReaction` at a constrained node. The element force is the constitutive response; the nodal reaction includes constraint forces that don't represent the physical shear.

#### 3. HystereticSM (Mazzoni 2023) Available in Standard OpenSeesPy

`ops.uniaxialMaterial("HystereticSM", ...)` is available in the standard OpenSeesPy PyPI distribution — no custom build needed. The material defines a multi-point envelope hysteretic law with pinching, damage, and unloading stiffness degradation. The backbone is specified in **force-deformation** space via `-posEnv`/`-negEnv` flags:

```python
ops.uniaxialMaterial(
    "HystereticSM", tag,
    "-posEnv", y1, x1, y2, x2, y3, x3, y4, x4, y5, x5,   # positive backbone (y=force, x=deformation)
    "-negEnv", y1n, x1n, y2n, x2n, y3n, x3n, y4n, x4n, y5n, x5n,
    "-pinch", px, py,
    "-damage", damage1, damage2,
    "-beta", beta,
)
```

When used in a `zeroLength` element on DOF 2, "force" = shear and "deformation" = transverse displacement.

#### 4. Manual Fallback-Ladder Loop as Documented SmartAnalyze Exception

The source's `RunStaticLoading.tcl` uses a per-step `DisplacementControl` integrator reset + a 6-algorithm fallback ladder (Newton → Newton-initial → ModifiedNewton → ModifiedNewton-initial → Broyden → NewtonLineSearch), retrying each failing step with relaxed tolerance (10×Tol, 10×iterations). This fixed-increment retry chain is **not exposed by SmartAnalyze** (which does adaptive sub-stepping within a single target via `relaxation`/`minStep`). For hysteretic materials with severe softening branches (V5 < 0.4×V3), the per-step integrator reset + full ladder is more effective than SmartAnalyze's sub-stepping because it gives the material a fresh tangent at each algorithm switch.

This is a documented exception per §3c/§10: use `ops.analyze(1)` in a manual loop with the fallback ladder when the source's recovery strategy is incompatible with SmartAnalyze.

#### 5. HystereticSM Backbone x-Axis Is Deformation, Not Rotation — Convert θ→δ

The source calibration framework (ShearHingeCalibration.m) defines the HystereticSM backbone in terms of `(V, θ)` pairs — shear force V [kip] and chord rotation θ [rad]. But `HystereticSM` takes **force-deformation** pairs, so the rotation must be converted to a transverse displacement **before** constructing the material:

```python
# Backbone: y_i = V_i * rpp [kip → N], x_i = theta_i * L [rad × in → in → mm]
pos_y = [V[i] * rpp * kip for i in range(5)]   # force
pos_x = [th[i] * (L * inch) for i in range(5)]  # deformation = θ × L
```

The negative envelope scales the force by `rnp` (negative residual/proportional ratio) but the deformation is symmetric: `x_neg = -theta * L`. Passing the raw rotation values as the x-axis would make the hinge 36× too stiff (for L=36 in) because the deformation would be in radians (~0.01) instead of inches (~0.4).

**Detection:** If the model's initial stiffness is wildly off (period or elastic-shear slope), check whether the HystereticSM x-axis received rotations (rad) instead of displacements (length). The clue: the backbone x-values should be on the order of the member's chord displacement (mm), not rotation (rad).

**Rule:** For shear-hinge calibration models where the source data is in `(V, θ)` space, always convert `θ → δ = θ × L` before passing to `HystereticSM`. The material's x-axis is deformation in the model's length unit, not rotation.

#### 6. Source disp.out Column 1 Is Shear, Not Pseudo-Time — Verify Recorder Semantics

The source Tcl `recorder Node -file disp.out -time -node 4 -dof 2 disp` produces a 2-column file where column 1 is the `-time` flag. In a standard LoadControl/DisplacementControl analysis, `-time` returns the pseudo-time (load factor). But the source's custom `RunStaticLoading` proc resets the `DisplacementControl` integrator at every step, so the pseudo-time tracks the cumulative control-node displacement — NOT the applied load factor.

The MATLAB post-processing script (`ShearHingeCalibration.m`) reads `disp.out` as `(shear, disp)`: `simu.hinge_shear = res(:,1)`. This works because, with the per-step integrator reset, the pseudo-time column coincidentally captures a value that the MATLAB interprets as shear. In reality, the reliable shear source is `shear.out` (`recorder Node -file shear.out -time -node 1 -dof 2 reaction`), where column 2 is the node-1 UY reaction.

**Rule:** When porting a Tcl model whose recorder output feeds a MATLAB/Python post-processor, verify what each column actually represents by cross-referencing the recorder command AND the post-processor's column indexing. Do not assume `-time` means wall-clock or load-factor — with custom integrator management it can track displacement or any other quantity. The safest approach: re-derive the output from `ops.eleResponse` / `ops.nodeReaction` in the Python model, as in point 2 above.

---

### §12ap — Tkinter GUI Stripping, pygmsh → ops.patch, nonlinearBeamColumn ODB Scoping, Recorder -time Semantics (v1.40.0)

Source: `Dino` — 3D RC cantilever column pushover with fiber section (Concrete01 + Steel01), original `column_sec.py` wrapped in a Tkinter GUI + pygmsh triangle mesh.

#### 1. Tkinter GUI Wrappers Are Stripped — Parameters Become Named Constants

The source `column_sec.py` wraps the entire OpenSees model in a `calculation()` function called from a Tkinter button, reading all parameters from `ttk.Entry` widgets. For standardization, strip the GUI entirely: move the default parameter values into the §3 Parameters section as named constants. The model runs headless via `python model.py` with no user interaction.

**Rule:** When converting a GUI-wrapped OpenSees script, extract the GUI's default values into the Parameters section. The GUI code (`tkinter`, `ttk`, `messagebox`, `root.mainloop()`) is removed — it has no structural purpose and blocks CI/headless execution.

#### 2. pygmsh Triangle Mesh → `ops.patch("rect")` — Native Fiber Commands

The source uses `pygmsh` to triangulate the concrete section into 244 triangle fibers, writing centroids/areas to `triangle_data.txt`, then reads them back into individual `ops.fiber(x, y, area, matTag)` calls. pygmsh is **not available** in the opensy conda env (only the lower-level `gmsh` bindings). The standard repo approach — used by every fiber-section model — is `ops.patch("rect", matTag, ny, nz, yL, zB, yR, zT)`:

```python
# Source (pygmsh — NOT in opensy env):
with pygmsh.geo.Geometry() as geom:
    ...  # triangulate, extract triangle_cells
for triangle in triangle_cells:
    ops.fiber(centroid_x, centroid_y, area, MAT_CONCRETE)

# Standardized (native OpenSees — always available):
ops.patch("rect", MAT_CONCRETE, 20, 20,
          -B_SEC/2, -H_SEC/2, B_SEC/2, H_SEC/2)   # 400 fibers
```

**Impact:** A 20×20 rect patch (400 fibers) vs 244 pygmsh triangles produces ~10% stiffer response (peak base shear 8810 kN vs 7980 kN). Finer concrete discretization captures more of the section's effective stiffness (§12e). This is an expected and acceptable discretization effect — not a bug.

**Rule:** When the source uses an external mesher (pygmsh, meshpy, gmsh direct), replace it with `ops.patch("rect")` for rectangular concrete areas or `ops.patch("circ")` for circular. The native commands are always available and integrate with `ops.layer("straight")` for rebar. Match the fiber count approximately; document the expected stiffness difference.

#### 3. `nonlinearBeamColumn` Retains Standard Signature — NOT dispBeamColumn

`ops.element("nonlinearBeamColumn", tag, iNode, jNode, nIP, secTag, transfTag)` takes the section tag and IP count directly — no separate `beamIntegration` object needed. This differs from `dispBeamColumn` which requires `beamIntegration("Lobatto", integTag, secTag, nIP)` (§12l). The source's call is correct and preserved verbatim.

**Rule:** `nonlinearBeamColumn` and `forceBeamColumn` take `(tag, i, j, nIP, secTag, transfTag)`. Only `dispBeamColumn` requires the separate `beamIntegration` object. Do not add `beamIntegration` to a `nonlinearBeamColumn` call.

#### 4. `save_frame_resp=False` for nonlinearBeamColumn — Same as forceBeamColumn (§12v)

`nonlinearBeamColumn` (like `forceBeamColumn`) creates internal section objects accessed by a 1-based index, not the user-assigned fiber-section tag. When `CreateODB` attempts to read section responses via `ops.sectionForceDeformation(tag)`, it looks for tag 0 → error. Set `save_frame_resp=False`:

```python
odb = opst.post.CreateODB(
    odb_tag=1,
    save_nodal_resp=True,
    save_frame_resp=False,   # nonlinearBeamColumn internal sections (§12v)
)
```

Nodal response tracking for deformed-shape visualization still works.

#### 5. Recorder `-time` Column Is the Load Factor, Not Force — Verify Units

The source `recorder Node -file node_disp.out -time -node 2 -dof 1 disp` produces col1 = `-time` = pseudo-time = load factor λ (unitless), col2 = displacement [mm]. The actual base shear = λ × reference_load. The reference load was 1000 N, so `base_shear = col1 × 1000 N`. Reading col1 directly as "shear in N" gives values 1000× too small.

```python
# Reference file interpretation:
ref = np.loadtxt('node_disp.out')
ref_load_factor = ref[:, 0]      # λ (unitless)
ref_disp = ref[:, 1]             # mm
ref_base_shear = ref_load_factor * P_LATERAL_REF   # N (= λ × 1000)
```

**Rule:** When a source recorder uses `-time`, the first column is the pseudo-time (load factor for LoadControl/DisplacementControl static). To get the physical force, multiply by the reference load magnitude. Do not interpret `-time` as force directly.

#### 6. Dead Materials (Defined But Never Referenced) Should Be Omitted

The source defines `ops.uniaxialMaterial('Elastic', 200, 1000E12)` — a 1e12-stiffness elastic material that is never referenced by any section or element. It served no structural purpose (likely a leftover from template code). Omit dead materials during standardization to keep the Tag Registry clean.

**Rule:** During conversion, grep the source for every `uniaxialMaterial` / `nDMaterial` tag and verify it appears in at least one `section` / `element` / `fiber` / `layer` call. If not, omit it and note the removal.

---

### §12aq — Fiber-Mesh Density Does NOT Change Section Stiffness; A Documented Recorder Lesson Still Shipped as a Bug; Stale Reference Data (v1.41.0)

Source: `Dino` verification follow-up — the §12ap (v1.40.0) entry claimed finer fiber discretization caused a ~10% stiffness rise, but direct section-property + OpenSees probes show that is physically wrong; and §12ap-5's "recorder -time = load factor" rule was nonetheless violated by `model.py`'s own reference loader.

#### 1. A finer mesh of the SAME concrete area converges to the SAME stiffness — NOT stiffer (corrects §12ap-2 and §12e)

§12ap-2 (and §12e) claimed the 20×20 rect patch (400 fibers) is "~10% stiffer" than pygmsh's 244 triangles because "finer concrete discretization captures more of the section's effective stiffness." **That is incorrect.** A fiber section integrates area and second moment of area over its fibers; a finer subdivision of the *same* rectangle converges to the same A and I, hence the same EI and the same `3EI/L³`. Direct computation from the committed meshes:

```
pygmsh 244-triangle mesh:  A = 960000 mm²,  I_y = 5.083e10 mm⁴
20×20 rect patch:           A = 960000 mm²,  I_y = 5.120e10 mm⁴  (analytic)
                            → area match: exact; I match: 0.4%
```

A 0.4% section-property difference cannot produce a 10–24% response difference.

**Rule:** Do not attribute pushover stiffness differences to fiber-mesh density when the mesh covers the same geometric area. Verify by computing A and I directly from the mesh centroids/areas (`I = Σ area · y²`); if they agree within ~1%, the mesh is NOT the cause. (Corrects §12ap-2 "Impact" and §12e's "~10-15% stiffness difference" attribution.)

#### 2. The actual cause of Dino's stiffness gap: axial precompression (and a stale reference)

Direct OpenSees probe of the one-element cantilever, same section/element/fixities as `model.py`:

```
lateral k, no axial load:               3589 kN/mm
lateral k, with −15000 kN gravity:      4863 kN/mm   (+35%)
uncracked theory 3EI/L³ (Ec=fcu/eps0):  4328 kN/mm
sim full model step-1:                  5137 kN/mm
reference node_disp.out step-1:         4158 kN/mm
```

The −15000 kN axial precompression raises the lateral stiffness ~35% (the fiber section is stiffer when the concrete is in compression). The simulation (5137 kN/mm) is consistent with a precompressed, largely-uncracked section; the reference (4158 kN/mm) matches the *un-precompressed* / uncracked-theory value almost exactly. The committed `node_disp.out` is therefore a stale artifact (regenerated from an earlier run inconsistent with the committed `triangle_data.txt`), not a target to match. The simulation is physically the more reliable result.

**Rule:** When sim-vs-reference elastic stiffness disagrees by >~15%, run a no-axial vs with-axial stiffness probe on a one-element cantilever (apply unit lateral load, read `nodeDisp`). If the with-axial value matches the simulation and the no-axial value matches the reference, the reference was generated under different loading — treat the simulation as authoritative and document the reference as stale.

#### 3. A documented AGENT.md lesson still shipped as a bug in its own model — add a units-sanity gate

§12ap-5 documents that `recorder Node -time` col 0 is the load factor λ, not force, and that base shear = λ × reference_load. Yet `model.py`'s own reference loader read col 0 directly as "N" and the post-processor plotted `ref_shear/1e3` — so the reference curve rendered at 7.98 kN against the simulation's 8810 kN (a 1000× error, an invisible flat line). The lesson was written but not applied to the model whose section recorded it. Fix: `ref_shear = ref[:, 0] * P_LATERAL`.

**Rule:** A documented lesson does not prevent the bug unless a check enforces it. After conversion, add a units-sanity gate to every reference-vs-simulation plot: assert the peak magnitudes agree within an order of magnitude (e.g. `abs(sim_peak - ref_peak) / max(sim_peak, ref_peak) < 5`); if they differ by 10× or more, suspect a recorder-unit mismatch (load factor vs force, kN vs N, kip vs N) and re-derive the column semantics from the source `recorder` command before trusting the overlay.

#### Detection / Rules
- **Mesh-stiffness attribution:** compute A and I from the source and standardized meshes (`I = Σ area · y²`). Agreement within ~1% ⇒ mesh is NOT the cause of any >5% response difference.
- **Sim-vs-reference elastic-stiffness gap >15%:** run a no-axial vs with-axial one-element cantilever probe. A match to the no-axial value flags the reference as generated under different loading (stale).
- **Reference-vs-sim plot overlay:** gate on peak magnitudes agreeing within an order of magnitude. A 1000× ratio ⇒ recorder-unit bug (load factor read as force). Cross-ref §12ap-5, §12ao-6.

---

### §12ar — Section-Level (Moment-Curvature) Analysis: Layout Adaptation, Curvature-Unit Trap, FiberSecMesh vs ops.patch, offset Sign (v1.42.0)

Source: `OPST_mc_section` — opstool docs Moment-Curvature example (`https://opstool.readthedocs.io/en/stable/src/analysis/mc_analysis.html`). The repo's first pure section-level model: a fiber section analyzed with `opst.pre.section.FiberSecMesh` + `opst.anlys.MomentCurvature` to produce an M-φ curve, with no structural nodes/elements/gravity/pushover/ODB.

#### 1. Section-level analyses adapt the 14-section layout by omitting §7–11

A moment-curvature (or any pure section) analysis has no nodes, elements, boundary conditions, ODB, or load patterns — `MomentCurvature` builds its own internal zeroLength element and imposes curvature directly. The canonical §3 layout is adapted by keeping the banner skeleton but omitting the inapplicable sections with a one-line comment ("Not used — MomentCurvature builds its own zeroLength element internally"), rather than stubbing them with `pass`. §12 ANALYSIS hosts the `MomentCurvature(...)` instantiation + `.analyze()` + `.get_limit_state()` + `.bilinearize()` calls. This mirrors the peridynamics precedent (§12p/§12q) where §6 SECTIONS / §11 LOADING are deleted when they don't apply.

**Rule:** For section-level / non-structural analyses, keep the §0–§14 banner skeleton (so audit tools and readers can navigate), omit the sections that genuinely don't apply (§7 Nodes, §8 BCs, §9 Elements, §10 ODB, §11 Loading) with a brief comment explaining why, and host the actual work in §12 ANALYSIS + §13 POST-PROCESSING. Do not stub empty functions.

#### 2. MomentCurvature curvature-unit trap — `max_phi`/`incr_phi` scale with the model's length unit (1000× error source)

`opst.anlys.MomentCurvature.analyze(max_phi, incr_phi)` takes curvature in the reciprocal of the model's length unit. The opstool docs example uses kN-m units with `incr_phi=1e-5` [1/m] (and `max_phi` defaulting to 0.5 [1/m]). Converting the model to N-mm-MPa requires scaling these curvature arguments by `1 m / 1 mm = 1e-3`: `incr_phi = 1e-5 × 1e-3 = 1e-8` [1/mm], `max_phi = 0.5 × 1e-3 = 5e-4` [1/mm]. Forgetting this factor leaves the analysis trying to reach 0.5 [1/mm] = 500 [1/m] — 1000× beyond any physical curvature — and the computed moments come out 1000× too large (or the analysis stops at step 0 / never reaches the limit state). Strains (dimensionless) are unchanged by unit conversion; only length-derived quantities (curvature, moment, axial force, stress) scale.

```python
# Source (kN-m):    MC.analyze(incr_phi=1e-5)           # 1e-5 [1/m]
# Standardized (N-mm): MC.analyze(incr_phi=1e-5 * 1e-3)  # 1e-8 [1/mm]
INCR_PHI = 1.0e-5 * 1.0e-3   # 1e-8 /mm  (source 1e-5 /m × 1e-3 m/mm)
MAX_PHI  = 0.5    * 1.0e-3   # 5e-4 /mm  (default 0.5 /m × 1e-3 m/mm)
```

**Rule:** When converting a MomentCurvature (or any curvature-driven) analysis between unit systems, scale `max_phi` and `incr_phi` by the length-unit ratio (`m→mm` = ×1e-3). Detection: if the analysis runs to `max_phi` without reaching a limit state, or the computed moments are ~1000× the expected engineering value, the curvature arguments were not scaled. Strain-based limit-state thresholds (`get_limit_state(threshold=...)`) are dimensionless and need NO scaling.

#### 3. `FiberSecMesh` (opstool polygon patches) vs `ops.patch("rect")` — choose by geometry

The opstool docs example builds the section with `opst.pre.section.FiberSecMesh` + `create_polygon_patch` (triangulated by `sectionproperties`), NOT the raw `ops.patch("rect")` used by §12ap/§12e. `FiberSecMesh` supports arbitrary polygon outlines **with holes** (the cover ring around a central core hole here) and emits native OpenSees `fiber` commands via `SEC.to_opspy_cmds(secTag, GJ)`. `ops.patch("rect")` only handles simple rectangles without holes. Either is acceptable; choose based on section geometry. When the source uses `FiberSecMesh`, preserve it — do NOT force-convert to `ops.patch("rect")` if the section has holes or non-rectangular outline.

**Rule:** Use `ops.patch("rect")` (§12ap) for simple rectangular sections. Use `opst.pre.section.FiberSecMesh` + `create_polygon_patch` when the section has holes, chamfers, or a non-rectangular outline. Register the section to OpenSees via `SEC.to_opspy_cmds(secTag, GJ)` — this is the method name (NOT `to_ops_cmds`).

#### 4. `opst.pre.section.offset(d)` sign — docstring is reversed; `d>0` shrinks INWARD

The `offset(points, d)` docstring says "positive values offset inwards, negative values outwards" — this is accidentally correct in the docstring text, but the implementation calls `ply.buffer(-d)`, so a **positive `d` shrinks the polygon inward** and a negative `d` expands it outward. Using the wrong sign when building a cover ring (outer outline minus an inset outline) produces an overlapping/invalid geometry and a `shapely.errors.GEOSException: TopologyException: unable to assign free hole to a shell` at `SEC.mesh()` time. The source uses positive `d` (`offset(outlines, d=0.05)`) to shrink the 2×2 outline inward to the cover-inner boundary.

**Rule:** `opst.pre.section.offset(points, d)` with `d > 0` shrinks inward. To build a cover ring, `coverlines = offset(outlines, d=COVER)` (positive) then `create_polygon_patch(outlines, holes=[coverlines])`.

#### 5. vis_utils V1–V7 do not apply to section analyses — use custom matplotlib

The seven `vis_*` HTML helpers in `standards/vis_utils.py` all render OpenSees node/element meshes or ODB nodal displacements — none of which exist in a section analysis. For section results, use custom matplotlib following `standards/plot_utils.py` style (`COLORS` dict, `_style_ax`, Agg backend, dpi=150): an M-φ curve for the moment-curvature result, and opstool's own `MomentCurvature.plot_fiber_responses(return_ax=True)` for fiber stress-strain (save its returned figure). Skip the V1–V7 HTML files entirely.

**Rule:** Section-level models produce matplotlib PNGs (`mphi_curve.png`, `fiber_stress_strain.png`), not the V1–V7 HTML visualizations. Follow `plot_utils.py` styling. Use opstool's built-in `.plot_M_phi()` / `.plot_fiber_responses(return_ax=True)` where available.

#### Detection / Rules
- **Layout:** section-level models omit §7–11 with explanatory comments; work lives in §12 + §13. Precedent §12p/§12q.
- **Curvature-unit scaling:** `max_phi`/`incr_phi` × length-unit ratio when converting unit systems (kN-m→N-mm = ×1e-3). Strain thresholds unchanged. Detection: 1000× moment error or analysis never reaches limit state.
- **Section mesher:** `FiberSecMesh` for holes/non-rectangular; `ops.patch("rect")` for simple rectangles. Method is `to_opspy_cmds(secTag, GJ)`.
- **offset sign:** `d > 0` shrinks inward (despite docstring ambiguity).
- **Visualization:** custom matplotlib PNGs (plot_utils.py style), not V1–V7 HTML.

---

### §12as — First Shell-Element Model: ShellNLDKGQ + PlateFiber, Coordinate-Keyed Mesh Generation for Composite Sections, SmartAnalyze for Post-Buckling, Deep Nesting Path Depth (v1.43.0)

Source: `Dino_Buckling` — axial-compression buckling of a thin-walled steel I-section cantilever column built from 1200 ShellNLDKGQ elements (original `co.tcl`). The repo's first shell-element model.

#### 1. Shell-section recipe: ElasticIsotropic → PlateFiber nDMaterial → PlateFiber section

A shell element (`ShellNLDKGQ`, `ShellMITC4`, `ASDShellQ4`) needs a *plate section*, not a fiber section. The standard chain is: `nDMaterial("ElasticIsotropic", matTag, E, nu)` → `nDMaterial("PlateFiber", plateMatTag, matTag)` (wraps the 3D material into a plane-stress plate form) → `section("PlateFiber", secTag, plateMatTag, thickness)`. The element takes the section tag directly: `element("ShellNLDKGQ", tag, n1, n2, n3, n4, secTag)`. This is the only shell recipe tested in the repo; there is no `section_library.py` helper for it.

**Rule:** For shell elements, build the three-stage material chain (ElasticIsotropic → PlateFiber nDMaterial → PlateFiber section) and pass the section tag to the element. Do NOT try to use a `Fiber` section or `ops.patch` with shell elements — those are for beam-column fiber sections only.

#### 2. Coordinate-keyed mesh generation — walls MUST share corner nodes by coordinate

When a section is built from multiple shell walls (an I-section's 3 walls, a box's 4 walls), the walls MUST share corner nodes where they meet, or the section acts as disconnected plates and cannot buckle/deflect compositely. A naive ring generator that appends each wall's nodes to a list produces *duplicate* corner nodes (each wall creates its own node at the shared coordinate) → the walls are disjoint → the column is far too stiff and never buckles.

The fix: key nodes by their `(x, y)` coordinate so a second wall visiting an existing coordinate reuses the same tag. In Python:

```python
rings = {}
tag = 0
for kz in range(N_SEG_H + 1):
    z = (H_COL / N_SEG_H) * kz
    ring = {}                                  # {(x,y): tag}
    for wall in walls:                         # walls = [top_flange, web, bot_flange]
        for (x, y) in wall:
            key = (round(x, 6), round(y, 6))
            if key not in ring:
                tag += 1
                ops.node(tag, x, y, z)
                ring[key] = tag
    rings[kz] = ring
```

Element connectivity then looks up tags by coordinate key, guaranteeing shared walls resolve to shared nodes.

**Rule:** For multi-wall shell sections, generate nodes via a coordinate-keyed dict (not a flat list) so T-junction/L-junction corners are shared. Detection: if a multi-wall column never buckles and its axial stiffness is ~10× the theoretical EA/L, the walls are likely disjoint (each carrying load independently).

#### 3. SmartAnalyze is required for post-buckling — a manual DisplacementControl loop overshoots the limit point

For this steel shell column, a manual `ops.analyze(1)` DisplacementControl loop (source-style) climbs monotonically to 5000+ kN without snapping through the buckling limit point — the fixed 0.5 mm increment is too large to track the post-buckling softening, so the solver steps past the limit point into a stiffened post-buckled branch. `opst.anlys.SmartAnalyze` (with `relaxation=0.5`, `minStep=1e-2`, `tryLooseTestTol=True`, `looseTestTolTo=1e-3`, algorithm ladder `[40,10,20,30]`) sub-steps through the limit point and correctly captures the ~527 kN peak (matching the Euler cantilever Pcr = 542 kN). This is the §12z SmartAnalyze recipe applied to shell buckling.

**Rule:** For buckling/post-buckling analysis, use SmartAnalyze (not a manual fixed-increment loop) — the fixed increment overshoots the limit point. Settings: `NormDispIncr` @ 1e-4, KrylovNewton primary, `relaxation=0.5`, `minStep=1e-2`, `tryLooseTestTol`. Cross-ref §12z, §12aj.

#### 4. `save_shell_resp=True` — repo's first shell ODB; Penalty+UmfPack works for shells

CreateODB for shell models: `save_shell_resp=True`, `save_frame_resp=False`, `save_truss_resp=False` (shells have no frame/truss responses; disabling avoids silent memory growth per §12u-2). Omit `node_tags` (§12u — breaks `plot_nodal_responses` deformed plots). The source's `constraints("Penalty", 1e20, 1e20)` + `system("UmfPack")` worked for this 1200-shell model — unlike the §12af stiffness-contrast failure (bridge models). Shell models do not inherently trigger the UmfPack pivot failure; test Penalty+UmfPack first, switch to Transformation+BandGeneral only if it fails.

**Rule:** Shell ODB uses `save_shell_resp=True` (not `save_frame_resp`). Penalty+UmfPack is a valid starting point for shell models; the §12af UmfPack failure is stiffness-contrast-specific, not shell-specific.

#### 5. Deep nesting (models/Dino/<analysis-name>/) needs `parents[3]` for standards/

Models nested under `models/<Family>/<AnalysisName>/` (two levels under `models/`) are one level deeper than the canonical `models/<UniqueID>/` layout. The standards-import line `sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))` points to `models/` (wrong); it must be `parents[3]` (the repo root). Use a fallback to be robust to future relocation:

```python
_STANDARDS = Path(__file__).parents[3] / "standards"
if not _STANDARDS.exists():
    _STANDARDS = Path(__file__).parents[2] / "standards"
sys.path.insert(0, str(_STANDARDS))
```

**Rule:** For models nested deeper than `models/<UniqueID>/`, adjust the `parents[]` depth for the standards import. Verify by checking `_STANDARDS.exists()`.

#### Detection / Rules
- **Shell section:** ElasticIsotropic → PlateFiber nDMaterial → PlateFiber section; pass secTag to element.
- **Multi-wall mesh:** coordinate-keyed node generation (`{(x,y): tag}`); flat-list generation produces disjoint walls → no buckling, ~10× stiffness. Detection: column never buckles, stiffness ≫ EA/L.
- **Post-buckling solver:** SmartAnalyze (not manual fixed-increment loop) — fixed increment overshoots the limit point. §12z settings.
- **Shell ODB:** `save_shell_resp=True`; omit `node_tags`. Penalty+UmfPack works for shells (§12af failure is stiffness-contrast-specific).
- **Deep nesting:** `parents[3]` for `models/<Family>/<Analysis>/`; use `.exists()` fallback.

---

### §12at — Debug Scratch-Script ≠ Standardized Model: A Solver-Mismatch Can Look Like a Stale Reference (v1.44.0)

Source: `Dino_Buckling` post-mortem. During validation, a throwaway debug script (manual `ops.analyze(1)` DisplacementControl loop, replicating the source Tcl) gave a peak axial load of **5129 kN** for the buckling column. The reference `result.xlsx` showed **~630 kN**. This 8× gap — plus the reference showing a clean limit point the debug run never produced — led to a lengthy "the committed reference is stale" investigation (Euler theory, stiffness cross-checks), mirroring the §12aq-2 Dino-sectional stale-reference diagnosis.

Running the actual standardized model (`opst.anlys.SmartAnalyze` with sub-stepping, relaxation, algorithm fallback) gave **526.6 kN** — within 3% of the Euler cantilever Pcr (542 kN) and 16% of the reference. The reference was **correct**. The 8× gap was entirely an artifact of the debug script's fixed 0.5 mm increment overshooting the post-buckling limit point, not a geometry or reference problem.

#### The rule

A debug scratch-script can diverge from the standardized model by an order of magnitude when the two differ in **solver strategy** — most critically fixed-increment (`ops.analyze(1)` with a fixed DisplacementControl/LoadControl increment) vs adaptive sub-stepping (SmartAnalyze with `relaxation`, `minStep`, algorithm fallback). This class of solver mismatch is invisible in the elastic range (both agree) but dominates around limit points, snap-throughs, and post-buckling softening, where a fixed increment steps past a non-uniqueness or onto a stiffened branch.

**Before declaring a committed reference stale (§12aq-2), validate with the full standardized model — not a debug script.** If the debug script and the standardized model disagree by more than the reference does from either, the bug is in the debug script's solver settings (almost always the fixed increment + missing relaxation), not in the model or the reference. A debug script is for isolating *model-definition* questions (geometry, materials, fixities, connectivity); it is NOT authoritative for *response* questions on a softening/limit-point structure.

```text
Debug script (fixed incr)    Standardized (SmartAnalyze)   Reference
     5129 kN         ──vs──>        526.6 kN          ──vs──>  ~630 kN
     ↑ wrong (overshot limit point)   ↑ correct          ↑ correct (not stale)
```

#### Detection / Rules
- **Order-of-magnitude gap between debug script and standardized model** ⇒ the debug script's solver is the cause, not the model or the reference. Re-run the full model before any stale-reference diagnosis (§12aq-2).
- **A debug script is authoritative for model-definition questions** (does the mesh connect? are the materials right? is the fixity correct?) — verify those in isolation by all means. It is **NOT authoritative for response values** near limit points / softening / snap-through.
- **Fixed-increment (`ops.analyze(1)`) vs SmartAnalyze:** the two agree in the elastic range and diverge at non-linearities. Cross-ref §12as-3 (SmartAnalyze required for post-buckling), §12z, §12aj, §12am (manual fixed-increment chains stall mid-protocol).

---

### §12au — Arbitrary (Irregular) Cross-Section Cyclic: Verbatim Fibre Replay, 3D Fibre `-GJ`, `static_split` Cadence (v1.45.0)

Source: `Dino_LowCycle` — low-cycle cyclic analysis of a 3 m RC cantilever column with an irregular (re-entrant) "arbitrary" cross-section (original `co.tcl` + 911-fibre `section_fiber.tcl`). The repo's first irregular-section cyclic model. Validation: **1000/1000 steps, peak shear +1684.9/−2026.4 kN matching `node2.out` to 0.0%, per-point RMS 2.44 kN (~0.12%).**

#### 1. Verbatim fibre replay — do NOT re-mesh an irregular section

The section has re-entrant corners (a top-left appendage + a mid-height notch) meshed into 894 concrete + 17 rebar fibres. Re-meshing (via `FiberSecMesh`/`sectionproperties`) risks both (a) A/I drift vs the source mesh — the §12aq lesson, where finer-vs-coarser of the *same* area converges but a *different* triangulation of an irregular polygon does not — and (b) getting the re-entrant outline wrong (`shapely TopologyException`). The faithful approach: parse the source fibre file at runtime and replay each fibre verbatim via `ops.fiber(y, z, A, matTag)`. This guarantees byte-identical section properties (verified: A_conc = 1 107 833 mm², 17 rebar) and hence a 0.0% response match.

```python
# section_fiber.tcl line:  "fiber  -511.934  -503.548  1207.39  1"
pat = re.compile(r"^\s*fiber\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+(\d+)\s*$")
ops.section("Fiber", SEC, "-GJ", GJ)     # -GJ required (see point 2)
for (y, z, area, mat) in parsed_fibers:
    ops.fiber(y, z, area, mat)           # section-local (y, z) = source (x, y)
```

**Rule:** For irregular / re-entrant / arbitrary cross-sections, replay the source's fibres verbatim (`ops.fiber`); reserve `FiberSecMesh`/`ops.patch` re-meshing for simple regular sections (rectangular, circular). Detection: if a re-meshed section's pushover/cyclic response diverges from the reference for no obvious solver reason, suspect A/I drift from the re-triangulation.

#### 2. 3D `section("Fiber")` REQUIRES `-GJ` in OpenSeesPy (Tcl only warns)

The source Tcl builds the fibre section with no `-GJ` — Tcl merely prints "WARNING torsion not specified" and continues (the `section Aggregator ... T` supplies torsion separately). **OpenSeesPy raises an `OpenSeesError` and stops** at `section("Fiber", 1)` without `-GJ`. The fix: supply a principled GJ computed from the concrete Young's modulus and the fibre polar second moment of area — the value is a formality because the Aggregator's torsion material dominates, but it must be physically defensible (not an arbitrary placeholder). `GJ = G·J` where `G = Ec/(2(1+ν))` and `J = Σ area·(y² + z²)` over the fibres.

**Rule:** A 3D `ops.section("Fiber", tag)` MUST include `-GJ` (or `-torsion matTag`); unlike Tcl, OpenSeesPy errors rather than warns. When the section also has an Aggregator supplying torsion, any reasonable GJ on the inner Fiber section is fine (the Aggregator's torsion material governs). Detection: `OpenSeesError('See stderr output')` at `section("Fiber", ...)` immediately after the call, with the "torsion not specified" warning on stderr.

#### 3. `static_split([cycle_delta], maxStep=|incr|)` — feed the per-cycle DELTA, not cumulative position

For a fixed-increment cyclic protocol with a 1:1 recorder (e.g. this source: 100 steps/cycle × 10 cycles = 1000 rows), SmartAnalyze's `static_split(targets, maxStep)` must be called per cycle with the cycle's **displacement change from the current position** as `targets[0]`, NOT the cumulative absolute destination. `static_split` interprets each target as an increment from the *current* state and splits it into `maxStep`-sized segments:

```python
# CORRECT — 100 segments/cycle, 1000 total
for incr in CYCLE_INCR:                              # +0.05,-0.10,...,-0.50 mm/step
    cycle_delta = incr * N_STEPS_PER_CYCLE           # +5, -10, +15, -20, ... mm
    segs = analysis.static_split([cycle_delta], maxStep=abs(incr))   # 100 segs
# WRONG — passing cumulative abs position: cycle 2's "−5.0" yields only 50 segs
#         (treated as a −5 mm increment from +5, landing at 0, not −5) → 591/1000 steps.
```

The bug signature: the model "completes" all 10 cycles (🎉 Successfully finished × N) and reaches the final peak displacement, but the converged-step count is far below the expected (e.g. 591/1000) and the per-cycle progress bar shows `1/1` for later cycles instead of `100/100`. This is a *cadence* bug, not a convergence bug — the physics is right (peaks match the reference) but the recorder is under-sampled because the later cycles' large displacements get coalesced into few segments.

**Rule:** When driving a fixed-increment cyclic protocol with `static_split` + `StaticAnalyze` for 1:1 recorder alignment, pass each cycle's displacement **delta** (`incr × N_steps_per_cycle`) as the single target, with `maxStep = |incr|`. Do NOT pass the cumulative absolute displacement. Detection: all cycles "finish" but `len(history) ≪ N_expected`, and per-cycle progress bars show 1 segment instead of N. Cross-ref §12am (the per-increment `static_split([incr], maxStep=abs(incr))` pattern).

#### 4. DisplacementControl recorder `-time` col = lateral load-factor λ; base shear = λ × reference load

The source `recorder Node -file node2.out -time -node 100 -dof 1 disp` writes col 0 = the pseudo-time (lateral pattern load-factor λ) and col 1 = the recorded displacement. Because displacement is *imposed* by DisplacementControl, the validation quantity is the **λ (hence base-shear) column at the forced displacements**, not the displacement column (which is tautologically matched). Base shear = λ × P_LATERAL_REF (the reference lateral load, here 100 kN). This is the §12ap-5 / §12aq-3 rule restated for the cyclic case.

**Rule:** For a DisplacementControl-driven cyclic/pushover model validated against a `-time` recorder, compute base shear as `λ × P_LATERAL_REF` and validate on the λ column (displacement is imposed). Cross-ref §12ap-5.

#### 5. `.xlsx` readable with stdlib alone when `openpyxl`/`pandas.read_excel` unavailable

The `opensy` env has neither `openpyxl` nor `xlrd`/`python-calamine`, so `pandas.read_excel` fails (`Import openpyxl failed`). For a secondary plot sourced from a workbook (here the P-M interaction surface), parse the `.xlsx` (a zip of OOXML) directly with `zipfile` + `xml.etree.ElementTree`: locate the target sheet via `xl/workbook.xml` + `xl/_rels/workbook.xml.rels`, then iterate `sheetN.xml`'s `<row>/<c>/<v>` cells keyed by column letter. Avoids adding a dependency for a non-essential plot. The units of the workbook columns must be verified independently (here the PMM sheet was already in kN/kN·m, not N/N·mm — a naive `÷1e3`/`÷1e6` produced a 1000×/1e6× too-small surface).

**Rule:** When the env lacks `openpyxl` and the xlsx data is simple (numeric cells, no shared strings), read it with `zipfile` + `ElementTree` rather than installing a package — but verify the column units against a known physical quantity (e.g. the gravity demand point must sit inside a P-M surface) before plotting.

#### Detection / Rules
- **Irregular section:** verbatim fibre replay (`ops.fiber`), not `FiberSecMesh`/`ops.patch` re-meshing. Detection: re-meshed section's response diverges from reference for no solver reason ⇒ A/I drift.
- **3D Fiber `-GJ`:** mandatory in OpenSeesPy (Tcl only warns). Compute `GJ = G·Σ area·(y²+z²)`; Aggregator torsion governs regardless. Detection: `OpenSeesError` at `section("Fiber",...)`.
- **`static_split` cyclic cadence:** pass per-cycle delta (`incr×N`), not cumulative abs position, with `maxStep=|incr|`. Detection: all cycles finish but `len(history) ≪ N_expected`; progress bar `1/1` not `100/100`. Cross-ref §12am.
- **DisplacementControl `-time` col = λ:** base shear = λ × P_LATERAL_REF; validate on the λ column. Cross-ref §12ap-5.
- **xlsx via stdlib:** `zipfile` + `ElementTree` when `openpyxl` absent; verify column units against a physical check.

---

### §12av — Simplified Lateral MDOF (Pure Eigen): ElasticTimoshenkoBeam Shear-Building Idealization, Mass-Unit Double-Conversion, No-Reference Theory Validation (v1.46.0)

Source: `Dino_MDOF_eigen` — pure eigen/modal analysis of a 12-story uniform lumped-mass shear building (original `co.tcl`, 99 lines, only `eigen 10` + mode-shape recorders, no loads/gravity/analysis step). The repo's first **pure eigen-only** model and first **MDOF shear-building** model. Validation: **all 10 periods match closed-form shear-building theory to 0.0000%** (T1=1.582 s … T10=0.107 s).

#### 1. ElasticTimoshenkoBeam 3D REQUIRES explicit Avy/Avz (11-arg form)

OpenSeesPy's `element("ElasticTimoshenkoBeam", tag, i, j, ...)` in 3D requires the 11-arg form `(tag, iNode, jNode, E, G, A, Jx, Iy, Iz, Avy, Avz, transfTag)` — the 9-arg form without shear areas errors with `"not enough args provided, want: ... $Avy $Avz"`. (Tcl is equally strict; this is not a Tcl-vs-Python divergence like §12au's `-GJ`, but the signature is easy to mis-parse from a space-separated Tcl line where `Avy Avz transfTag` run together.) Cross-ref §12l (dispBeamColumn beamIntegration), §12au (element-signature gotchas).

**Rule:** For 3D `ElasticTimoshenkoBeam`, always supply Avy and Avz explicitly. Detection: `OpenSeesError('See stderr output')` + "not enough args ... $Avy $Avz" at element creation.

#### 2. Shear-building idealization via ElasticTimoshenkoBeam — inflate A/J/Iy/Iz, leave Av finite

A lumped-mass shear building can be built with beam elements by setting A = Jx = Iy = Iz to a huge value (1e20) so axial, torsional, and bending stiffness are effectively rigid (~3.7e9× stiffer than shear), leaving **shear as the only finite flexibility**: `k_story = G · Av / L`. With G=1e5 MPa, Av=3000 mm², L=3000 mm → k = 1e5 N/mm/story. The resulting 12-element vertical chain is a clean 12-DOF discrete shear building (the K matrix is the tridiagonal `[k, 2k, …, 2k] / −k` form). This is a cleaner alternative to zeroLength shear springs + equalDOF for MDOF models where beam visualization is wanted.

**Rule:** For a beam-element shear building, set A=J=Iy=Iz=1e20 (rigid) and a finite Avy=Avz; the story stiffness is then `k = G·Av/L`. Detection: if a Timoshenko-beam building's periods don't match `2√(k/m)·sin(...)`, check whether bending (EI) is leaking into the lateral stiffness — if Iy/Iz isn't inflated enough, the element adds flexural stiffness on top of shear.

#### 3. Mass-unit double-conversion trap (restated for the eigen case) — T off by 1000×

The source's `mass 1 1.00E+002` is the literal number **100 in N·s²/mm** (the mass unit of this N-mm system, which equals 1 tonne — `kg = N·s²/mm` in `units.py`, `tonne = 1000·kg`). Multiplying by `tonne` (writing `M = 100 * tonne`) double-converts to 100 000, making the mass 1000× too large → every period √1000 = 31.6× too long (T1 came out **50.03 s** instead of 1.582 s, still matching "theory" 0.000% because the theory formula used the same wrong m — the bug was self-consistent and invisible until checked against an absolute expectation). This is the §12al / §12b mass-unit rule restated for the eigen-only case: mass numbers from an N-mm source are already in N·s²/mm; do NOT re-multiply by `tonne`/`kg`.

**Rule:** In an N-mm-MPa model, use the source's mass number directly (it is already in N·s²/mm = tonnes); do NOT multiply by `tonne` or `kg` from `units.py`. Detection: T₁ off by ~30–1000× (here 31.6×) with the sim-vs-theory diff still ~0% (the double-conversion is self-consistent). The catch is that a no-reference eigen model validated only against a hand-coded theory formula will PASS while being 30× wrong — so always sanity-check T1 against an engineering expectation (a 12-story building is ~1–2 s, NOT 50 s). Cross-ref §12al.

#### 4. No-reference validation: pure modal model validates against structural theory

When `tcl_ref/` ships no reference output (no `Periods.txt`, no `.out` mode-shape files — common for a teaching/example MDOF source), the validation anchor is the closed-form theory. For a uniform N-DOF shear building: `ω_j = 2·√(k/m)·sin((2j−1)·π/(4N+2))`. Here all 10 modes matched to 0.0000%, confirming both the element idealization (point 2) and the mass scaling (point 3 — after the tonne fix). The §12ar `_pct()` idiom (sim vs reference, flag >~1%) generalizes to sim vs theory.

**Rule:** A pure eigen model with no reference file validates against the appropriate closed-form frequency formula; print per-mode sim-vs-theory and sanity-check T1 against an engineering range (a multi-story building is 0.1–5 s, a flexible long-period structure 5–10 s; 50 s for a 12-story building is a units bug).

#### 5. Layout adaptation for pure-eigen — omit only §11; §12 hosts eigen + save_eigen_data

A pure-eigen model has real nodes/elements/BCs/ODB (unlike §12ar's section-level model, which had none) but no loads/gravity/analysis. The mildest §3 layout adaptation yet: keep §0–§10 (Materials may also be omitted if the elements take E,G as literals — here ElasticTimoshenkoBeam does, so the source's 3 dead Elastic materials are dropped per §12ap-6), **omit only §11 Loading** with a comment, and host `ops.eigen()` + `odb.save_eigen_data(mode_tag=m)` in §12. Mode shapes are visualized via `opst.vis.plotly.plot_eigen_table` / `plot_eigen(subplots=True)` / `plot_eigen_animation` (Guan2020 precedent), reading the ODB; custom matplotlib PNGs (periods bar chart, mode-shape-vs-height) supplement per `plot_utils.py` style.

**Rule:** For a pure-eigen (no-load) model, omit §11 Loading only; keep §7–§10; §12 hosts the eigen call + `save_eigen_data`. Visualize with `opst.vis.plotly.plot_eigen*` (Guan2020) + matplotlib. Cross-ref §12ar (which omits §7–§11 — a stronger adaptation, forced by the absence of any structural mesh).

#### Detection / Rules
- **ElasticTimoshenkoBeam Avy/Avz:** mandatory in 3D (11-arg form). Detection: "not enough args ... $Avy $Avz" at element creation.
- **Shear-building via Timoshenko:** A=J=Iy=Iz=1e20 (rigid) + finite Av → k=G·Av/L. Detection: periods don't match shear-building theory ⇒ bending stiffness leaking in (inflate Iy/Iz).
- **Mass double-conversion:** source mass number is already N·s²/mm; do NOT ×`tonne`. Detection: T1 off ~30–1000× but sim-vs-theory still ~0% (self-consistent bug); sanity-check T1 against engineering range (12-story ≈ 1–2 s, NOT 50 s). §12al.
- **No-reference validation:** closed-form theory `ω_j = 2√(k/m)·sin((2j−1)π/(4N+2))` for a uniform shear building; here 0.0000% all 10 modes.
- **Pure-eigen layout:** omit §11 only; keep §7–§10; §12 hosts eigen + save_eigen_data. plot_eigen* (Guan2020) + matplotlib. Cross-ref §12ar.

---

### §12aw — Nonlinear RC Layered-Shell Wall: PlaneStressUserMaterial→PlateFromPlaneStress, Steel02→PlateRebar, `section LayeredShell`, ShellDKGQ, Softening-Solver Mismatch Is Directional (v1.47.0)

Source: `Dino_LayeredShell_wall` — elastoplastic pushover of a 1.5 m × 6.0 m × 0.2 m RC shear wall, meshed 6×10 into 50 ShellDKGQ quad shells over a 6-layer `LayeredShell` section (original `co.tcl`). The repo's first **nonlinear-shell** model (§12as was an elastic-shell buckling model; §12au/§12z were nonlinear fibres). Validation: **200/200 pushover steps** converged; elastic stiffness matches the reference to **1.8%** (0–2.4 mm drift); post-cracking branch diverges (sim peak 205.6 kN vs ref 148.6 kN, 27.7%) — a §12at-class solver mismatch (see point 5, and notably the *inverse* of §12at's buckling case).

#### 1. Nonlinear RC layered-shell recipe — the PlaneStress + PlateRebar material chain

Unlike §12as's elastic-shell chain (`ElasticIsotropic → PlateFiber nDMaterial → PlateFiber section`), a nonlinear RC layered shell builds a 3-deep material wrapper per layer type. **Concrete:** `PlaneStressUserMaterial` (7-param smeared RC: fpc, fpt, then 5 strain stops) → `PlateFromPlaneStress` (adds a linear out-of-plane shear modulus `G_out` so the 2D plane-stress concrete can carry transverse shear in a plate). **Rebar:** `Steel02` (uniaxial) → `PlateRebar` (orients the 1D steel at a given angle within the layer plane — 90° for vertical rebar, 0° for horizontal). Then `section("LayeredShell", tag, nLayers, mat1 t1 mat2 t2 ...)` stacks layers from the −z face to the +z face.

```python
# Concrete: PlaneStressUserMaterial (7-param) -> PlateFromPlaneStress (+G_out)
ops.nDMaterial("PlaneStressUserMaterial", 2, 40, 7, fpc, fpt, -6.13, -2e-3, -5e-2, 1e-3, 5e-2)
ops.nDMaterial("PlateFromPlaneStress", 4, 2, 12.77e9)        # wraps mat 2 + out-of-plane G
# Rebar: Steel02 -> PlateRebar (angle in the layer plane)
ops.uniaxialMaterial("Steel02", 5, 582., 205000., 0.0033, 14, 0.925, 0.15)   # vertical
ops.nDMaterial("PlateRebar", 7, 5, 90)
# Section: 6-layer sandwich (rebar / conc / conc / rebar, symmetric)
ops.section("LayeredShell", 701, 6, 8,0.8, 7,0.8, 4,100, 4,100, 7,0.8, 8,0.8)
```

**Rule:** For a nonlinear RC shell, the material chain is `PlaneStressUserMaterial → PlateFromPlaneStress` (concrete) and `Steel02 → PlateRebar` (rebar), assembled by `section("LayeredShell", ...)` which the shell element (ShellDKGQ / ShellNLDKGQ) takes directly as its section tag. No `PlateFiber`/`section("PlateFiber")` indirection — that's the elastic-shell path (§12as). Layer order is −z face → +z face; a symmetric rebar/conc/conc/rebar sandwich is the standard RC-wall layout.

#### 2. `PlaneStressUserMaterial` arg-order trap — the 7 params are NOT `(fpc, fpt, E, …)`; pass them verbatim

The 7 trailing params of `PlaneStressUserMaterial` are `(fpc, fpt, epstu, epscu0, epucu, …)` in a smeared-RC convention (peak compressive/tensile strength then *strain* stops) — NOT the `(E, ν, fy, …)` of `ElasticIsotropic`/`J2Plasticity`. The third arg here is `-6.13` (a strain stop, negative for compression), which a naive reader would parse as a Young's modulus sign error. Reinterpreting or "tidying" these args silently corrupts the stress-strain law. **Pass the 7 params verbatim from the source** with a comment flagging the convention, as §12ap (concrete `ops.patch`) and §12au (verbatim fibre replay) do for their verbatim quantities.

**Rule:** `PlaneStressUserMaterial`'s 7 params are strength-then-strain-stops in a smeared-RC convention; do NOT reinterpret them as elastic constants. Detection: if the wall's elastic stiffness is wildly off (≫/≪ reference) in the pre-cracking range, suspect a mis-parsed arg; if only the post-cracking branch differs (elastic range fine), the args are correct and the gap is solver-side (point 5).

#### 3. Gravity phase — manual `LoadControl` loop + `loadConst` BEFORE the lateral pattern

The source does gravity (axial UZ load at the top edge, `analyze 10`) then `loadConst` (freezes the gravity load at λ=1) then defines the lateral pattern and runs the pushover. SmartAnalyze forces `DisplacementControl`, so the gravity `LoadControl` phase is a **manual `ops.analyze(1)` loop** (the §3c permitted exception, cross-ref §12z-2), and the lateral pattern MUST be defined **after** `loadConst` — a DisplacementControl pattern frozen at λ=0 yields an infinite load factor at step 0 (§12z-1). `loadConst("-time", 0.0)` resets the pseudo-time so the pushover λ starts from 0.

```python
# Phase 1: gravity (LoadControl, manual loop) THEN loadConst
ops.integrator("LoadControl", 1.0/N_GRAV_STEPS)
for _ in range(N_GRAV_STEPS): ops.analyze(1)
ops.loadConst("-time", 0.0); ops.wipeAnalysis()
# Phase 2: lateral pattern AFTER loadConst, then DisplacementControl pushover
define_lateral_loads()    # §12z-1: must follow loadConst
```

**Rule:** For a gravity-then-pushover RC model, run gravity as a manual `LoadControl` loop, call `loadConst("-time", 0.0)`, `wipeAnalysis()`, THEN define the lateral pattern and run the DisplacementControl pushover. Defining the lateral pattern before `loadConst` makes the first pushover step carry infinite lateral force. Cross-ref §12z-1/§12z-2.

#### 4. `ShellDKGQ` takes the `LayeredShell` section tag directly; per-increment `static_split` cadence

`ShellDKGQ` (discrete-Kirchhoff + Generalized-Quadrilateral, 4-node) — like `ShellNLDKGQ` (§12as) — takes the section tag as its last arg with **no** `"-nlGeo"`/thickness flag. The pushover uses the §12as-3 SmartAnalyze recipe (relaxation=0.5, minStep, algorithm fallback, loose-tol recovery), but here each 0.1 mm increment is fed via `static_split([incr], maxStep=incr)` so the recorder stays 1:1 with the 200-step reference (the §12am per-increment cadence, not §12au's per-cycle cadence).

**Rule:** ShellDKGQ / ShellNLDKGQ take the LayeredShell (or any) section tag directly as the element's last arg. For a fixed-increment pushover with a 1:1 recorder, drive SmartAnalyze one increment at a time: `static_split([incr], maxStep=incr)` then `StaticAnalyze(node, dof, seg)`. Cross-ref §12as-3, §12am, §12au-3.

#### 5. Softening-solver mismatch is DIRECTIONAL — SmartAnalyze can be stiffer OR softer than the fixed-increment reference (the inverse of §12at)

This wall's softening `PlaneStressUserMaterial` has a non-unique post-cracking branch; the tracked peak depends on solver strategy. Here SmartAnalyze (relaxation + loose-tol recovery) **converges all 200 steps** and tracks a **stiffer rebar-dominated branch (205.6 kN)**, while the reference's fixed-increment `KrylovNewton` run tracks the **softer concrete-crushing branch (148.6 kN)** and stalls at 189/200 (11 steps lost to softening). The elastic branches agree to **1.8%** (verified point-by-point: 1.8% at 0.1–2.4 mm, crossing at ~2.5 mm, then diverging — 25% by 6 mm, 28% at peak), confirming the model definition is correct; the divergence is purely the solver's choice of post-cracking equilibrium path.

This is the **inverse** of §12at's buckling post-mortem, where the *fixed-increment* script overshot the limit point to a *higher* peak (5129 vs 630 kN) and SmartAnalyze gave the *lower*, physically-correct Euler peak. Generalised: **for a softening/snap-through model the fixed-increment path and the adaptive (SmartAnalyze) path are both *valid equilibrium paths* but need not agree on which branch they settle on; the sign and magnitude of the mismatch are solver-dependent and not, by themselves, evidence of a model error.** The model-error detector (from §12at) is the *elastic* range: if the pre-nonlinear stiffness matches the reference (here 1.8%), the materials/section/mesh are correct and the post-nonlinear gap is solver-side; if the elastic range is off, the model definition is wrong.

**Rule:** A softening/snap-through model's post-nonlinear peak is solver-dependent and can be either higher OR lower than a fixed-increment reference (here higher; §12at's buckling was lower). Validate the model on the **elastic-range stiffness match** (here 1.8% to ~2.5 mm) — if that matches, the model is correct and the post-cracking divergence is a §12at-class solver mismatch, not a bug. Cross-ref §12at (inverse case), §12as-3, §12z.

#### Detection / Rules
- **Nonlinear RC shell recipe:** `PlaneStressUserMaterial → PlateFromPlaneStress` (concrete) + `Steel02 → PlateRebar` (rebar) → `section("LayeredShell")`; shell element takes the secTag directly. NOT the `PlateFiber` elastic-shell path (§12as).
- **`PlaneStressUserMaterial` 7 args:** strength-then-strain-stops smeared-RC convention; pass verbatim, do NOT reinterpret as elastic constants. Detection: elastic stiffness wildly off ⇒ mis-parsed arg; only post-cracking off ⇒ args fine, gap is solver-side.
- **Gravity + loadConst ordering:** manual `LoadControl` gravity loop → `loadConst("-time",0.0)` → `wipeAnalysis()` → define lateral pattern → DisplacementControl pushover. Lateral pattern before `loadConst` ⇒ infinite force at step 0 (§12z-1).
- **`static_split` pushover cadence:** one increment at a time, `static_split([incr], maxStep=incr)` for 1:1 recorder (§12am per-increment; cf §12au per-cycle).
- **Softening solver-mismatch is directional:** post-nonlinear peak can be higher (here) OR lower (§12at) than the fixed-increment reference; both are valid equilibrium paths. Model correctness is decided by the **elastic-range stiffness match** (1.8% here). Cross-ref §12at (inverse), §12as-3, §12z.

---

### §12ax — Element Birth/Death: `ops.remove('ele',...)` Mid-Analysis, `CreateODB(model_update=True)`, Orphan-Node Re-Pinning, Empty-Pattern Re-Equilibration (v1.48.0)

Source: `Dino_LifeDeath_shell` — progressive element removal ("element life and death") on a 6 m × 3 m elastic ShellMITC4 slab (100 elements, 121 nodes, ElasticIsotropic → PlateFiber section). After gravity is applied and frozen, an 8-element rectangular patch is removed group-by-group (4 steps each), with 3 orphan nodes re-pinned as their last element is removed (original `co.tcl`). The repo's first **element-birth/death** model (progressive-collapse / demolition style). Validation: **42/42 steps, node-88 UZ matches `node88.out` to 0.000% (post-gravity −0.63423 mm, final −1.28993 mm), per-step RMS 9.6e-6 mm.**

#### 1. Element-birth/death recipe — `ops.remove('ele', tag)` mid-analysis + `model_update=True` ODB

Element death removes an element from the live domain between analysis steps (its stiffness leaves the global K, internal forces redistribute). Drive it with a **manual `ops.analyze()` loop** — `ops.remove("ele", tag)` at the stage boundary, then `analyze(n)` to re-equilibrate under the reduced stiffness. **`CreateODB(model_update=True)` is MANDATORY**: with `model_update=False`, the ODB captures the element set once at construction and per-step response arrays misalign when tags disappear; with `True`, opstool re-queries `GetFEMdata().get_model_info()` each step and concatenates per-step datasets with `xr.concat(..., dim="time", join="outer")`, so removed elements simply drop out of later steps (earlier steps retain them). Tag filters (`node_tags`/`shell_tags`) MUST be omitted — let the ODB track all live tags (passing a tag that later gets deleted is documented-undefined).

```python
odb = opst.post.CreateODB(odb_tag=1, model_update=True,    # §12ax: required for death
                          save_nodal_resp=True, save_shell_resp=True,
                          save_frame_resp=False)            # no node_tags/shell_tags filters
# ... gravity + loadConst ...
for (etag, orphan, _) in DEATH_SEQUENCE:
    ops.remove("ele", etag)                                 # kill the element
    if orphan is not None:
        ops.fix(orphan, 1, 1, 1, 0, 0, 0)                   # pin orphan translations (see §3)
    ops.analyze(4)                                          # re-equilibrate (see §5)
    for _ in range(4):
        odb.fetch_response_step()                           # 1:1 with reference
```

**Rule:** For progressive element removal, drive a manual `ops.analyze()` loop with `ops.remove("ele", tag)` at each stage, and initialize the ODB with `model_update=True` and NO tag filters. Detection: if post-removal visualisation shows the removed elements still present, or per-step arrays throw a shape/alignment error, `model_update` is False (or a tag filter is set). Cross-ref §12u-2 (when NOT to set model_update), §12am (1:1 recorder cadence).

#### 2. `ops.remove('ele', tag)` — the `'ele'` type string (Tcl `remove element` → Python `remove('ele')`)

The OpenSeesPy `remove(type, tag)` command's valid `type` strings are `'ele'`, `'loadPattern'`, `'parameter'`, `'node'`, `'timeSeries'`, `'sp'`, `'mp'` (per the docs). Tcl's `remove element $tag` becomes Python `ops.remove("ele", tag)` — the abbreviated `'ele'`, not `'element'`. (Current OpenSeesPy builds also accept `'element'` as a synonym, but `'ele'` is the documented-canonical form and is portable; use `'ele'`.)

**Rule:** Convert Tcl `remove element <tag>` to `ops.remove("ele", tag)`. Detection: `remove("element", ...)` may silently work in some builds and fail in others — use `'ele'`.

#### 3. Orphan-node re-pinning — OpenSeesPy errors on duplicate SP where Tcl silently no-ops

When a removal isolates a node (all its connected elements gone), that node must be re-pinned or the global K goes singular. The source Tcl writes `fix 67 1 1 1 1 1 1` — but node 67 *already* has its 3 rotations fixed from the initial BC (`fix 67 0 0 0 1 1 1`), and Tcl silently no-ops the duplicate rotational SPs. **OpenSeesPy raises `OpenSeesError('See stderr output')`** on the duplicate SP (`Domain::addSP_Constraint - cannot add as node already constrained in that dof`). Fix: pin only the 3 **translations** that were previously free — `ops.fix(orphan, 1, 1, 1, 0, 0, 0)` — leaving the already-constrained rotations alone. (Net effect is identical to the Tcl: all 6 DOFs end up fixed.) Symmetrically, the **initial-BC regex must exclude the death-phase re-pin lines** (the source has `fix 67/81/83 ...` at both the BC block AND the death block; an unbounded `^fix\s+(\d+)...` regex matches both, double-pinning during the initial parse and erroring at construction). Bound the initial-BC parse to before the `"material"` marker (or equivalent section boundary).

**Rule:** (a) An orphan-node re-pin that follows an initial rotation-only fix must pin only the translations: `fix(orphan, 1,1,1, 0,0,0)` — OpenSeesPy errors on a duplicate SP where Tcl's `fix ... 1 1 1 1 1 1` silently no-ops. Detection: `OpenSeesError` + "cannot add SP ... already constrained" at the death-phase `ops.fix`. (b) The initial-BC parse must exclude later death-phase `fix` lines — bound the regex to the BC block (split `src` at the next section marker). Cross-ref §12au-2 (Tcl-warns-vs-Python-errors pattern, here for SPs not `-GJ`).

#### 4. SmartAnalyze has no element-death support — use a manual `ops.analyze()` loop

`opst.anlys.SmartAnalyze` is a convergence-control wrapper (test-tolerance switching, algorithm fallback, step relaxation) with **no API hook, callback, or documented support for removing elements between steps**. For an element-death sequence, use a plain `ops.analyze(n)` loop and insert `ops.remove`/`ops.fix` at the stage boundaries yourself. SmartAnalyze's convergence robustness is unnecessary here anyway — each post-removal `analyze(4)` is a single linear-elastic re-equilibration under frozen load (converges in 1–13 Newton iterations). For a nonlinear-death model where robustness matters, use SmartAnalyze *per leg* between removals (it just won't coordinate the removals).

**Rule:** Element birth/death is driven by a manual `ops.analyze()` loop with `ops.remove`/`ops.fix` interleaved — SmartAnalyze cannot trigger removals. Cross-ref §12as-3 / §12z (SmartAnalyze's actual purpose: softening/snap-through convergence).

#### 5. Empty-pattern re-equilibration — LoadControl steps under frozen gravity with no new load

The death phase adds **no new load** (the source's `pattern Plain 2 Linear {}` is empty). The driver is the stiffness drop from each removal: under the frozen gravity (locked in by `loadConst`), the reduced structure re-equilibrates, and node displacements grow as load paths are shed. OpenSeesPy accepts an empty `ops.pattern("Plain", 2, ts)` (no `ops.load` calls) — it exists only so the LoadControl integrator has a time series to advance, reproducing the source's pseudo-time progression (t = 2,3,4,5 after the first removal, etc.). A free correctness invariant: with zero load increment and zero stiffness change, steps 2–4 of each 4-step block are no-ops — node UZ must be **constant within each block** (any drift means a spurious load or wrong integrator). In this model the 8 staged UZ "jumps" (e70: −0.270 mm, e52: −0.201 mm, e50: −0.105 mm …) carry all the signal; the upper row of the removed patch (z=1.5–1.8 m, closer to node 88) contributes ~91% of the post-gravity deflection.

**Rule:** A death phase driven by frozen gravity (no new load) uses an empty LoadControl pattern; verify the within-block-constancy invariant (steps 2–4 of each stage must not drift). Cross-ref §12z (loadConst), §12aw-3 (gravity-then-pushover ordering).

#### 6. `node_tags` filter quirk with `model_update=True` — read all nodes, select by coordinate

With `model_update=True`, `opst.post.get_nodal_responses(node_tags=[88])` returned node **89**'s data (off-by-one in the filtered selection over the varying live-node set). The reliable read is to omit the filter (read all 121 nodes) and select the target node by coordinate: `ds.sel(nodeTags=88)`. The ODB also stores a leading t=0.0 zero frame (pre-analysis) — drop it (`uz[1:]`) to align 1:1 with the reference recorder's row count.

**Rule:** With `model_update=True`, do not trust the `node_tags` filter for single-node reads — read all nodes and `.sel(nodeTags=<tag>)`. Drop the leading t=0.0 frame for 1:1 reference alignment. Detection: a single-node read returns the wrong tag's data / wrong-shaped series.

#### Detection / Rules
- **Element-death recipe:** manual `ops.analyze()` loop + `ops.remove("ele", tag)`; ODB with `model_update=True` and no tag filters. Detection: removed elements still visible in viz / array-shape errors ⇒ model_update False or tag filter set.
- **`ops.remove('ele', tag)`:** Tcl `remove element` → Python `remove('ele')`; `'ele'` is canonical (`'element'` accepted in some builds).
- **Orphan re-pin:** pin translations only `(1,1,1,0,0,0)` after an initial rotation-only fix; OpenSeesPy errors on duplicate SP (Tcl no-ops). Initial-BC parse must exclude death-phase `fix` lines (bound regex at next section marker). §12au-2 pattern.
- **SmartAnalyze ≠ death:** no removal hooks; use manual `ops.analyze()`. §12as-3/§12z.
- **Empty-pattern re-equilibration:** frozen gravity drives; within-block UZ constancy is a free invariant.
- **`node_tags` filter + model_update:** unreliable — read all nodes, `.sel(nodeTags=tag)`; drop the t=0.0 zero frame.

---

### §12ay — `ops.fiber()` Argument-Order Trap (Silent NaN Stiffness); Two-LoadControl-Phase Force-Controlled Frames (v1.49.0)

Source: `Dino_PseudoCollapse` — OpenSees Example 2.9, a 3D RC moment-resisting frame (3 bays × 3 bays × 4 storeys, 44 nodes, 83 `nonlinearBeamColumn` elements) with two Steel01/Concrete02 fiber sections wrapped in rigid shear+torsion `section Aggregator`s. Two **force-controlled** phases: gravity (node 35 +3e5 N UZ + 128 `eleLoad -beamUniform` lines, LoadControl 0.1, 10 steps) → `loadConst` → pushdown (node 35 −3e5 N UZ, LoadControl 0.01, 100 steps) = 110 recorded steps, validated against `tcl_ref/node35.out`. Validation: **110/110 steps, node-35 UX/UY/UZ match `node35.out` to ≤0.27% mean rel error** (UX/UY 0.2667%, UZ 0.1917%; final UZ −16.9274 mm sim vs −16.8883 mm ref).

#### 1. `ops.fiber()` argument order is `(y, z, area, matTag)` — reversing it passes a negative coordinate as the area → silent NaN stiffness → singular matrix at step 0

The OpenSeesPy `ops.fiber()` signature is `ops.fiber(y, z, A, matTag)` — **the area is the THIRD argument, not the first.** Tcl's `fiber $y $z $A $matTag` has the same order, but when emitting fibers in a Python loop from parsed coordinates the natural-but-wrong instinct is `ops.fiber(area, y, z, mat)` (area-first, mirroring how a fiber is conceptualised: "a patch of area A at (y,z)"). This reversal is **catastrophic and silent**: the first coordinate (e.g. −200) is interpreted as the area, so the fiber is assigned a *negative area* → the section's axial/flexural tangent contains a negative contribution → `ForceBeamColumn3d::update()` returns `dW = NaN` on the very first trial → `BandGenLinLapackSolver::solve()` fails with `matrix singular U(i,i) = 0, i=0` → `analyze` returns −3 at step 0. No error names "fiber" or "area"; it presents exactly like a dead DOF or a missing constraint.

This is a **verbatim-fiber-replay trap** (§12au-1/§12aq pattern): when you parse `fiber y z A mat` from a Tcl source and re-emit it, you MUST preserve the OpenSeesPy argument order, not the conceptual one. A clean `ops.patch("rect")` + `ops.layer("straight")` section (§12ap) does not expose this because those commands take their own argument orders.

**Rule:** `ops.fiber(y, z, area, matTag)` — area is THIRD, not first. Detection: `ForceBeamColumn3d::update - failed to get compatible ... dW: -nan(ind)` + `matrix singular U(i,i)=0` at **step 0** on a freshly-built fiber-section model ⇒ a fiber was emitted with a negative/zero area (reversed args), NOT a mechanism or missing material. Cross-ref §12au-1 (verbatim fiber replay), §12aq (fiber mesh).

#### 2. `ops.fiber()` argument order is confirmed by an incremental-diagnostic method

The trap was isolated by an **incremental probe**: (a) `elasticBeamColumn` with the section's hand-computed EA/EI → converges (rules out the model topology / fixities / solver); (b) `nonlinearBeamColumn` + a *clean* `patch`/`layer` section → converges (rules out the element type and the material chain); (c) `nonlinearBeamColumn` + the **parsed** fibers → fails with the NaN signature. The only variable between (b) and (c) is how the fibers are emitted → the `ops.fiber()` call. This "swap one variable at a time from a known-good baseline" method is the repo's standard debugging approach (cf. §12at's "debug script ≠ standardized model" warning, here inverted: the *debug scripts* are what found the bug).

**Rule:** When a fiber-section model fails at step 0 with NaN/singular, isolate it with an incremental probe: elastic element → clean patch/layer section → parsed fibers. The failing swap names the bug. Cross-ref §12at.

#### 3. `nonlinearBeamColumn` + `section Aggregator` + rigid shear/torsion — the source's section architecture, ported verbatim

The source wraps each fiber section in a `section Aggregator 1001 201 Vy 301 Vz 401 T -section 1` — binding three large Elastic materials (mat 201/301/401, ~1e9–1e13) to the shear (Vy/Vz) and torsion (T) codes so all transverse/torsional deformation is rigid and only the fiber section's axial/flexural law is active. In OpenSeesPy this is `ops.section("Aggregator", 1001, 201,"Vy", 301,"Vz", 401,"T", "-section", 1)`. The Aggregator tag (1001/1002) is what `nonlinearBeamColumn` binds — NOT the bare fiber section tag (1/2). The six Elastic shear/torsion materials are NOT dead (§12ap-6) — they are live Aggregator inputs and must be defined; only the unrelated `Elastic 3` (1.999e5, referenced by nothing) is dead.

**Rule:** A `section Aggregator` wrapping a fiber section adds rigid shear+torsion codes; the element binds the *Aggregator* tag, and all Aggregator-fed materials are live (define them). Only materials referenced by no section/element are dead. Cross-ref §12ap-6.

#### 4. `-GJ` required for the bare fiber section inside an Aggregator (§12au, restated for the Aggregator case)

Even though the Aggregator supplies the real (rigid) torsion via its `T` material, the inner `section("Fiber", 1)` STILL requires `-GJ` in OpenSeesPy — the error fires at the inner fiber-section construction (`section Fiber 1`), before the Aggregator is built. The §12au recipe (`GJ = G_steel · Σ A·(y²+z²)` over the fibers) applies unchanged. Because the Aggregator's rigid T dominates torsion, the exact GJ value has negligible structural effect (confirmed: ≤0.27% match to the reference regardless), but it must be present to construct the section.

**Rule:** Every 3D `section("Fiber")` needs `-GJ`, including ones later wrapped by an Aggregator — the error fires at inner construction. Compute GJ from the fiber geometry (§12au); its value is structurally negligible when the Aggregator supplies torsion. Cross-ref §12au.

#### 5. Two `LoadControl` phases → two manual `ops.analyze()` loops (§3c exception, restated for force-controlled pushdown)

The source is **force-controlled in both phases** (LoadControl 0.1 gravity, LoadControl 0.01 pushdown) — NOT displacement-controlled. SmartAnalyze forces DisplacementControl, so per the §3c permitted exception each phase is a manual `ops.analyze()` loop with the source's verbatim solver (Plain constraints, Plain numberer, BandGeneral, EnergyIncr 1e-6/200, Newton). The two signs on node 35 (+3e5 then −3e5) do NOT cancel: phase 2 starts from the frozen gravity state (`loadConst`), so UZ grows monotonically to ~−17 mm — this is the "pseudo-collapse" demand. The 128 `eleLoad` lines (most beams written 2–4×) are replayed **verbatim including duplicates** so the total gravity load (and hence the displacement match) is identical to the Tcl run.

**Rule:** A force-controlled pushdown/pullback uses LoadControl manual loops (§3c exception); replay duplicate `eleLoad` lines verbatim (they are additive — de-duplicating changes the load and breaks the match). Lateral/pushdown pattern defined AFTER `loadConst` (§12z-1). Cross-ref §12z, §12ap-5.

#### Detection / Rules
- **`ops.fiber(y, z, area, matTag)`:** area is THIRD. Reversed args ⇒ negative area ⇒ NaN stiffness ⇒ `matrix singular U(i,i)=0` at step 0. Isolate via incremental probe (elastic → clean patch/layer → parsed fibers).
- **`section Aggregator` + fiber section:** element binds the Aggregator tag (1001/1002); Aggregator-fed shear/torsion Elastic materials are LIVE (not dead). §12ap-6.
- **`-GJ` on inner `section("Fiber")`:** required even when an Aggregator supplies torsion — error fires at inner construction. §12au.
- **Two LoadControl phases:** two manual `ops.analyze()` loops (§3c exception); replay duplicate `eleLoad` verbatim; pushdown pattern after `loadConst`. §12z-1, §12ap-5.

---

## 13. Versioning & Change Log

| Date | Version | Change |
|------|---------|--------|
| 2026-07-15 | 1.49.0 | **`ops.fiber()` argument-order trap (silent NaN stiffness); two-LoadControl-phase force-controlled frames (§12ay):** (1) **`ops.fiber(y, z, area, matTag)` — the area is the THIRD argument, not the first.** Reversing it to `ops.fiber(area, y, z, mat)` (the natural-but-wrong "area at (y,z)" conceptual order) passes a negative coordinate (e.g. −200) as the area → the section tangent gets a negative contribution → `ForceBeamColumn3d::update() dW = NaN` → `BandGenLinLapackSolver::solve() matrix singular U(i,i)=0, i=0` → `analyze` returns −3 at **step 0**, presenting exactly like a dead DOF / missing constraint. No error names "fiber" or "area". A clean `ops.patch`/`ops.layer` section (§12ap) never exposes this — it's a **verbatim-fiber-replay** trap (§12au-1/§12aq). Detection rule: NaN + singular-at-step-0 on a freshly-built fiber-section model ⇒ a fiber was emitted with a negative/zero area, NOT a mechanism. (2) **Incremental-probe method:** isolate by swapping one variable from a known-good baseline — `elasticBeamColumn` (converges ⇒ topology/fixities OK) → `nonlinearBeamColumn` + clean `patch`/`layer` section (converges ⇒ element/materials OK) → `nonlinearBeamColumn` + parsed fibers (fails ⇒ the `ops.fiber()` call). The failing swap names the bug (cf. §12at inverted). (3) **`section Aggregator` + rigid shear/torsion:** the source wraps each fiber section in `section Aggregator 1001 201 Vy 301 Vz 401 T -section 1` so transverse/torsional deformation is rigid; `nonlinearBeamColumn` binds the *Aggregator* tag (1001/1002), NOT the bare fiber tag (1/2). The six Elastic shear/torsion materials are LIVE Aggregator inputs (not dead); only the unreferenced `Elastic 3` is omitted (§12ap-6). (4) **`-GJ` on the inner `section("Fiber")` is still required** even when the Aggregator supplies torsion — the error fires at inner construction, before the Aggregator is built; the §12au recipe (`GJ = G_steel·Σ A·(y²+z²)`) applies, value structurally negligible (≤0.27% match regardless). (5) **Two force-controlled LoadControl phases** (gravity LoadControl 0.1/10 → `loadConst` → pushdown LoadControl 0.01/100) ⇒ two manual `ops.analyze()` loops (§3c exception, SmartAnalyze forces DisplacementControl); the +3e5/−3e5 signs on node 35 do NOT cancel (phase 2 starts from frozen gravity → UZ grows to ~−17 mm); 128 `eleLoad` lines (most beams 2–4×) replayed **verbatim including duplicates** (de-duplicating changes the load). Validation: **110/110 steps, node-35 UX/UY/UZ match `node35.out` to ≤0.27% mean rel error** (UX/UY 0.2667%, UZ 0.1917%; final UZ −16.9274 mm sim vs −16.8883 mm ref). 7 vis HTMLs + pushdown_compare.png + node35_disp_history.csv. Source: Dino_PseudoCollapse conversion (3D RC moment frame, OpenSees Example 2.9, 44 nodes / 83 nonlinearBeamColumn / 2 fiber sections, original co.tcl a.k.a. EXAM29.tcl). |
| 2026-07-12 | 1.48.0 | **Element birth/death — `ops.remove('ele',...)` mid-analysis, `CreateODB(model_update=True)` mandatory, orphan-node re-pinning, empty-pattern re-equilibration (§12ax):** (1) **Element-death recipe:** progressive element removal is a manual `ops.analyze()` loop with `ops.remove("ele", tag)` at each stage; `CreateODB(model_update=True)` is MANDATORY (with `False`, removed tags persist and per-step arrays misalign; with `True`, opstool re-queries the live model each step and `xr.concat(join="outer")` drops removed elements from later steps). Tag filters (`node_tags`/`shell_tags`) must be omitted. First repo use of `model_update=True`. (2) **`ops.remove('ele', tag)`** — Tcl `remove element` → Python `remove('ele')`; `'ele'` is the documented-canonical type string (`'element'` also accepted in current builds but `'ele'` is portable). (3) **Orphan-node re-pinning in OpenSeesPy:** the source's `fix 67 1 1 1 1 1 1` silently no-ops the already-fixed rotational DOFs; OpenSeesPy errors on the duplicate SP (`Domain::addSP_Constraint ... already constrained`) — fix: pin only the translations `fix(orphan, 1,1,1, 0,0,0)` (the §12au-2 Tcl-warns-vs-Python-errors pattern, here for SPs). Symmetrically, the initial-BC regex must exclude the death-phase `fix 67/81/83` lines or it double-matches and errors at construction (bound the parse at the next section marker). (4) **SmartAnalyze has no element-death hooks** — no API/callback to trigger removals between steps; use a manual loop. (5) **Empty-pattern re-equilibration:** the death phase adds no new load (`pattern Plain 2 Linear {}`); the frozen gravity (via `loadConst`) drives re-equilibration as stiffness drops — within each 4-step removal block, UZ must be constant (free correctness invariant). (6) **`node_tags` filter quirk with `model_update=True`:** `get_nodal_responses(node_tags=[88])` returned node 89 — read all nodes and `.sel(nodeTags=88)` instead; drop the leading t=0.0 zero frame for 1:1 alignment. Validation: **42/42 steps, node-88 UZ matches `node88.out` to 0.000% (post-gravity −0.63423 mm, final −1.28993 mm), per-step RMS 9.6e-6 mm** (exact for an elastic model with verbatim solver, cf. §12aw's 27.7% softening divergence). 7 vis HTMLs + node88_uz_compare.png + node88_uz_history.csv. Source: Dino_LifeDeath_shell conversion (6×3 m elastic ShellMITC4 slab, 100 elements, 121 nodes, progressive 8-element removal + 3 orphan re-pins, original co.tcl). |
| 2026-07-12 | 1.47.0 | **Nonlinear RC layered-shell wall — PlaneStressUserMaterial→PlateFromPlaneStress, Steel02→PlateRebar, section LayeredShell, ShellDKGQ, softening-solver mismatch is directional (§12aw):** (1) **Nonlinear RC shell recipe:** concrete via `PlaneStressUserMaterial` (7-param smeared RC) → `PlateFromPlaneStress` (+out-of-plane G); rebar via `Steel02` → `PlateRebar` (90°/0°); assembled by `section("LayeredShell", tag, nLayers, mat t …)` which ShellDKGQ takes directly. NOT the elastic `PlateFiber` chain of §12as. (2) **`PlaneStressUserMaterial` arg-order trap:** the 7 trailing params are strength-then-strain-stops (e.g. arg 3 = −6.13 is a compressive strain stop, NOT a Young's modulus); pass verbatim from source, do NOT reinterpret as elastic constants. Detection: elastic-range stiffness wildly off ⇒ mis-parsed arg; only post-cracking off ⇒ args correct, gap is solver-side. (3) **Gravity + loadConst ordering:** manual `LoadControl` loop → `loadConst("-time",0.0)` → `wipeAnalysis()` → define lateral pattern AFTER loadConst → DisplacementControl pushover (lateral pattern before `loadConst` ⇒ infinite force at step 0; §12z-1). (4) **`static_split` pushover cadence:** one 0.1 mm increment at a time, `static_split([incr], maxStep=incr)` then `StaticAnalyze(node,dof,seg)`, for a 1:1 200-step recorder (§12am per-increment; cf §12au per-cycle). (5) **Softening-solver mismatch is DIRECTIONAL (the inverse of §12at):** this wall's softening PlaneStressUserMaterial has a non-unique post-cracking branch — SmartAnalyze (relaxation + loose-tol recovery) converges all 200/200 steps onto a *stiffer* rebar-dominated branch (205.6 kN) while the reference's fixed-increment KrylovNewton tracks the *softer* concrete-crushing branch (148.6 kN, stalls 189/200). In §12at's buckling the direction was reversed (fixed-increment *overshot* higher; SmartAnalyze gave the lower Euler peak). Rule: the post-nonlinear peak can be higher OR lower than a fixed-increment reference and both are valid equilibrium paths — model correctness is decided by the **elastic-range stiffness match** (verified 1.8% to ~2.5 mm drift; curves cross at ~2.5 mm, reach 25% by 6 mm). Validation: 200/200 steps, 27.7% peak diff (accepted §12at-class solver mismatch, NOT a model error). 7 vis HTMLs + pushover_compare.png + pushover_curve.csv. Source: Dino_LayeredShell_wall conversion (1.5×6.0×0.2 m RC shear wall, 50 ShellDKGQ, 6-layer LayeredShell, original co.tcl). |
| 2026-07-12 | 1.46.0 | **Simplified lateral MDOF (pure eigen) — ElasticTimoshenkoBeam shear-building idealization, mass-unit double-conversion, no-reference theory validation (§12av):** (1) **ElasticTimoshenkoBeam 3D requires explicit Avy/Avz (11-arg form)** `(tag,i,j,E,G,A,Jx,Iy,Iz,Avy,Avz,transfTag)`; the 9-arg form errors ("not enough args ... $Avy $Avz"). Cross-ref §12l/§12au. (2) **Shear-building idealization via ElasticTimoshenkoBeam:** A=Jx=Iy=Iz=1e20 (rigid axial/bending/torsion) + finite Avy=Avz=3000 → only shear is flexible → k_story = G·Av/L = 1e5 N/mm. A clean 12-element chain is a 12-DOF discrete shear building (cleaner than zeroLength springs + equalDOF when beam visualization is wanted). Detection: if periods don't match shear-building theory, bending stiffness (EI) is leaking in → inflate Iy/Iz. (3) **Mass-unit double-conversion trap (restated for eigen):** the source's `mass 1 1.00E+002` is already in N·s²/mm (= 1 tonne); multiplying by `tonne` double-converts to 100000 → T1 came out 50.03 s instead of 1.582 s (31.6× too long), yet sim-vs-theory was still 0.000% because the theory formula used the same wrong m (self-consistent, invisible bug). Fix: use the raw mass number directly; do NOT ×`tonne`/`kg`. Detection: T1 off ~30–1000× with sim-vs-theory ~0%; ALWAYS sanity-check T1 against an engineering range (12-story ≈ 1–2 s, NOT 50 s). Cross-ref §12al/§12b. (4) **No-reference validation via structural theory:** `tcl_ref/` shipped no Periods.txt/.out files; validated against closed-form `ω_j = 2√(k/m)·sin((2j−1)π/(4N+2))` → **0.0000% all 10 modes** (T1=1.582 s … T10=0.107 s), confirming both the idealization and the mass scaling. (5) **Layout: pure-eigen omits only §11 Loading** (has real nodes/elements/BCs/ODB, unlike §12ar which omits §7–11); §12 hosts `ops.eigen(10)` + `save_eigen_data(mode_tag=m)`; visualize via `plot_eigen_table`/`plot_eigen(subplots=True)`/`plot_eigen_animation` (Guan2020 precedent) + matplotlib (periods bar chart, mode shapes vs height). Dead materials (3 Elastic tags, unreferenced — ElasticTimoshenkoBeam takes E,G as literals) omitted (§12ap-6). Default ARPACK eigen solver (uniform stiffness + full-rank mass — neither §12h-2 nor §12al applies). Validation: 10/10 modes, max 0.0000% vs theory. Source: Dino_MDOF_eigen conversion (12-story 36 m shear building, 13 nodes, 12 ElasticTimoshenkoBeam, 100 t/floor UX-only, original co.tcl). |
| 2026-07-12 | 1.45.0 | **Arbitrary (irregular) cross-section cyclic — verbatim fibre replay, 3D Fibre `-GJ` mandatory, `static_split` cadence (§12au):** (1) **Verbatim fibre replay** for irregular/re-entrant sections: the 894-concrete+17-rebar section is reconstructed by parsing `section_fiber.tcl` at runtime and emitting each fibre via `ops.fiber(y,z,A,mat)` — re-meshing (`FiberSecMesh`/`ops.patch`) risks A/I drift (§12aq) and getting re-entrant corners wrong (`shapely TopologyException`). Guarantees byte-identical section properties. (2) **3D `section("Fiber")` REQUIRES `-GJ` in OpenSeesPy** — the source Tcl omits it (Tcl only warns; the Aggregator's `T` material supplies torsion); OpenSeesPy *errors* at `section("Fiber",1)` without it. Fix: compute `GJ = G·Σ area·(y²+z²)` (concrete E + fibre polar inertia); Aggregator torsion governs regardless. (3) **`static_split` cyclic cadence:** feed each cycle's displacement **delta** (`incr×N_steps_per_cycle`) as the single target with `maxStep=|incr|` → exactly 100 segments/cycle = 1000 total, 1:1 with the recorder. Passing the *cumulative absolute* destination is a cadence bug: all cycles "finish" (🎉) and peaks match, but `len(history) ≪ N_expected` (got 591/1000) because later cycles' large displacements coalesce into few segments. Detection: progress bars `1/1` not `100/100`. Cross-ref §12am. (4) **DisplacementControl `-time` col = lateral λ** (not force); base shear = λ × P_LATERAL_REF; validate on the λ column (displacement is imposed). §12ap-5 for cyclic. (5) **`.xlsx` via stdlib:** env lacks `openpyxl`/`pandas.read_excel` — read the PMM sheet with `zipfile`+`ElementTree` (`<row>/<c>/<v>` keyed by column letter); verify column units against a physical check (gravity demand inside the P-M surface). Validation: 1000/1000 cyclic steps, peak shear +1684.9/−2026.4 kN matching `node2.out` to **0.0%/0.0%**, per-point RMS 2.44 kN (~0.12%), median relative error 0.000%. 7 vis HTMLs + hysteresis_compare.png + pmm_surface.png + hysteresis_curve.csv. Source: Dino_LowCycle conversion (3D RC cantilever, 5 dispBeamColumn via beamIntegration, irregular section, 10-cycle ±5..±25 mm, original co.tcl + section_fiber.tcl). |
| 2026-07-11 | 1.44.0 | **Debug scratch-script ≠ standardized model — a solver-mismatch can masquerade as a stale reference (§12at):** During Dino_Buckling validation, a throwaway debug script (manual `ops.analyze(1)` DisplacementControl loop) gave a 5129 kN peak while the reference showed ~630 kN — an 8× gap that triggered a lengthy stale-reference investigation (Euler cross-checks, §12aq-2 pattern). The actual standardized model (SmartAnalyze with relaxation/minStep/algorithm-fallback) gave 526.6 kN — within 3% of Euler cantilever Pcr=542 kN and 16% of the reference. The reference was CORRECT; the 8× gap was entirely the debug script's fixed increment overshooting the post-buckling limit point. Rule: before declaring a committed reference stale, validate with the full standardized model, not a debug script. A debug script is authoritative for model-definition questions (mesh connectivity, materials, fixities) but NOT for response values near limit points/softening/snap-through — fixed-increment and SmartAnalyze diverge there. Detection: if debug script and standardized model disagree by more than the reference does from either, the bug is in the debug script's solver. Cross-ref §12as-3, §12z, §12aj, §12am. Source: Dino_Buckling post-mortem. |
| 2026-07-11 | 1.43.0 | **First shell-element model — ShellNLDKGQ + PlateFiber section, coordinate-keyed mesh generation for composite sections, SmartAnalyze for post-buckling, deep-nesting path depth (§12as):** (1) Shell-section recipe: ElasticIsotropic → PlateFiber nDMaterial → PlateFiber section (20 mm thick); element takes secTag directly. No `section_library.py` helper for shells. (2) **Coordinate-keyed mesh generation:** multi-wall sections (I-section's 3 walls) MUST share corner nodes by (x,y) coordinate — a flat-list ring generator produces *duplicate* corner nodes → disjoint walls → column never buckles, ~10× too stiff. Fix: key nodes as `{(x,y): tag}` so revisited coordinates reuse the tag. Detection: column doesn't buckle + stiffness ≫ EA/L. (3) **SmartAnalyze required for post-buckling:** a manual fixed-increment DisplacementControl loop (source-style) overshoots the limit point and climbs to 5000+ kN; SmartAnalyze (relaxation=0.5, minStep=1e-2, tryLooseTestTol, algoTypes=[40,10,20,30]) sub-steps through the limit point → 527 kN peak matching Euler cantilever Pcr=542 kN. §12z recipe applied to shell buckling. (4) `save_shell_resp=True` (repo's first shell ODB), `save_frame_resp=False`; omit `node_tags` (§12u). Penalty(1e20,1e20)+UmfPack works for shells — the §12af UmfPack failure is stiffness-contrast-specific, not shell-specific. (5) Deep nesting (`models/Dino/<analysis-name>/`) needs `parents[3]` for standards (not `parents[2]`); use `.exists()` fallback. Validation: 100/100 buckling steps, peak 526.6 kN (sim) vs ~630 kN (ref) — 16% diff; sim peak matches weak-axis cantilever Euler Pcr=542 kN. 7 vis HTMLs + buckling_compare.png + buckling_curve.csv. Source: Dino_Buckling conversion (3D steel I-section cantilever, 1200 ShellNLDKGQ, original co.tcl Tcl, axial-compression buckling). |
| 2026-07-11 | 1.42.0 | **Section-level (moment-curvature) analysis — layout adaptation, curvature-unit trap, FiberSecMesh vs ops.patch, offset sign (§12ar):** (1) The repo's first pure section-level model (opstool docs Moment-Curvature example) — no nodes/elements/gravity/pushover/ODB. Layout adapted by omitting §7 Nodes / §8 BCs / §9 Elements / §10 ODB / §11 Loading with explanatory comments (NOT bare `pass`); work hosted in §12 ANALYSIS + §13 POST-PROCESSING. Precedent §12p/§12q. (2) **Curvature-unit trap:** `MomentCurvature.analyze(max_phi, incr_phi)` takes curvature in the reciprocal of the model's length unit; converting kN-m→N-mm requires scaling these by ×1e-3 (1/m → 1/mm) — source `incr_phi=1e-5` [1/m] → `1e-8` [1/mm], `max_phi` default 0.5 [1/m] → 5e-4 [1/mm]. Forgetting this gives a 1000× moment error or analysis never reaching the limit state. Strain thresholds (dimensionless) need NO scaling. (3) `opst.pre.section.FiberSecMesh` (polygon patches via sectionproperties, supports holes) vs `ops.patch("rect")` of §12ap/§12e (rectangles only) — choose by geometry; preserve `FiberSecMesh` when the section has holes. Registration method is `SEC.to_opspy_cmds(secTag, GJ)` (NOT `to_ops_cmds`). (4) `opst.pre.section.offset(d)` with `d>0` shrinks inward (calls `buffer(-d)`); wrong sign → `shapely TopologyException: unable to assign free hole to a shell` at mesh time. (5) vis_utils V1–V7 do not apply (no mesh/nodal responses) — use custom matplotlib PNGs (`mphi_curve.png`, `fiber_stress_strain.png`) following `plot_utils.py` style; opstool `.plot_fiber_responses(return_ax=True)`. Validation: all 4 limit-state points within 1.3% of docs reference (phiy +1.24%, My +0.04%, phiu +0.81%, Mu -0.17%). Source: OPST_mc_section conversion (opstool docs Moment-Curvature, 2x2 m hollow RC box, Concrete04 cover+core + Steel01, kN-m→N-mm-MPa). |
| 2026-07-11 | 1.41.0 | **Fiber-mesh density ≠ stiffness; documented recorder lesson still shipped as a bug; stale reference data (§12aq):** (1) Corrects §12ap-2/§12e: a finer mesh of the SAME concrete area converges to the SAME A and I (hence same EI), so it cannot cause a 10–24% stiffness rise — pygmsh 244-tri and 20×20 rect patch agree on A exactly and on I within 0.4%. Don't attribute response differences to fiber density when area matches. (2) Dino's real stiffness gap is axial precompression: one-element cantilever probe gives k=3589 kN/mm (no axial) vs 4863 kN/mm (with −15000 kN gravity, +35%) vs uncracked theory 4328; sim=5137, reference=4158. The reference matches the *un-precompressed* value almost exactly → committed `node_disp.out` is stale (regenerated under different loading), simulation is authoritative. (3) §12ap-5's "recorder -time col = load factor, not force" rule was violated by `model.py`'s own reference loader (`ref[:,0]` read as N, plotted /1e3 → reference curve at 7.98 kN vs sim 8810 kN, 1000× error, invisible). Fix `ref_shear = ref[:,0] * P_LATERAL`. New rule: gate every sim-vs-reference overlay on peak magnitudes agreeing within an order of magnitude; a ≥10× ratio ⇒ recorder-unit bug. Validation: re-ran Dino, 100/100 pushover steps, corrected pushover_compare.png now shows both curves at matching scale (ref 7980 kN vs sim 8810 kN). Source: Dino verification follow-up. |
| 2026-07-11 | 1.40.0 | **RC column pushover — Tkinter GUI stripping, pygmsh→ops.patch, nonlinearBeamColumn ODB, recorder -time semantics (§12ap):** (1) Tkinter GUI wrappers stripped — parameters become named constants in §3 (using GUI defaults); GUI code blocks CI/headless execution. (2) pygmsh triangle mesh (244 fibers) → `ops.patch("rect", ..., 20, 20)` (400 fibers) — pygmsh not in opensy env; native OpenSees fiber commands always available. Rebar `ops.layer` preserved exactly. ~10% stiffer response from finer discretization (peak 8810 kN vs 7980 kN, §12e). (3) `nonlinearBeamColumn` retains standard signature `(tag, i, j, nIP, secTag, transfTag)` — NOT dispBeamColumn (no beamIntegration object, §12l). (4) `save_frame_resp=False` in CreateODB — nonlinearBeamColumn internal sections lack user-visible tags (§12v, same as forceBeamColumn). (5) Recorder `-time` col = load factor λ (unitless), not force — base shear = λ × reference_load; reading col1 directly as N gives 1000× too small. (6) Dead materials (defined but never referenced by any section/element) omitted. SmartAnalyze (Static) replaces raw `ops.analyze(nstep)` + `ops.recorder`; lateral pattern after loadConst (§12z). Validation: gravity converges, pushover 100/100 steps (exact match on count + displacement 0.08→8.00 mm), peak shear 10.4% diff (expected discretization effect), 7 vis HTMLs + pushover_compare.png. Source: Dino conversion (3D RC cantilever column, fiber-section Concrete01+Steel01, original column_sec.py + pygmsh + Tkinter). |
| 2026-07-11 | 1.39.0 | **Shear-hinge calibration sweep — EnergyIncr tolerance unit conversion; equalDOF+Plain nodeReaction spurious shear; HystereticSM backbone θ→δ; source recorder semantics (§12ao):** (1) Source Tcl `test EnergyIncr 1e-4` is in **kip·in** energy units — in N·mm it MUST be scaled by `kip*inch` (=112985), giving TOL≈11.3 N·mm. Using the unscaled 1e-4 makes EnergyIncr ~100000× too tight → analysis stalls at ~30% of the protocol. Detection: load-factor spam >1e5 and `EnergyIncr` Norm deltaR >> Norm deltaX with displacement essentially converged. General rule: EnergyIncr tol ×`kip*inch`, NormDispIncr tol ×`inch`, NormUnbalance tol ×`kip`. (2) Under `equalDOF(master, slave, 1, 3)` + `constraints("Plain")`, `nodeReaction(retained_node, 2)` includes the MP-constraint force past first yield, giving shear values 2–3× the backbone capacity. Fix: read base shear from the zeroLength hinge element force (`ops.eleResponse(ELE_HINGE, "forces")[1]`), NOT `nodeReaction`. Cross-ref §12ak: there shear diverted to column-base node; here with Plain+DOF-2 hinge the retained-node reaction is contaminated. (3) `HystereticSM` (Mazzoni 2023) is available in standard OpenSeesPy — `-posEnv`/`-negEnv` backbone is force-deformation (y=force, x=deformation). (4) The source's `RunStaticLoading.tcl` 6-algorithm fallback ladder (Newton→Newton-initial→ModifiedNewton→ModifiedNewton-initial→Broyden→NewtonLineSearch) with per-step `DisplacementControl` integrator reset is a documented §3c/§10 exception to SmartAnalyze. (5) HystereticSM backbone x-axis is deformation not rotation — source (V,θ) pairs need θ→δ=θ×L conversion before passing to the material, else the hinge is L× too stiff. (6) Source `disp.out` col1 is NOT pseudo-time but shear — the custom per-step integrator reset makes `-time` track displacement; verify recorder semantics against the post-processor's column indexing. Validation: all 7 Naish (2015) cases match source exactly on step count (1078/1078, 1108/1108, etc.), within 1% on peak shear (159.2/159.2, 210.8/210.9 kip), within 0.6–5.3% on hysteretic energy; 7 vis HTMLs per case (V1 nodes, V2 model, V3 loads, V4 pre-analysis, V5 deformed peak, V6 step slider, V7 animation). Source: ZhongKuanshi conversion (7-case HystereticSM shear-hinge calibration sweep, Zhong Stanford 2016 / Naish 2015). |
| 2026-07-10 | 1.38.0 | **3D frame-wall building — rigidDiaphragm needs Transformation; per-story/per-IP tag scheme must pass absolute tags; corotTruss ODB scoping; triaxial-GM-with-no-repo-files substitute (§12an):** (1) Any model with rigidDiaphragm/equalDOF/MP constraints requires `constraints("Transformation")` for BOTH gravity and dynamic — `Plain` cannot distribute MP-constraint reactions (consistent with §12x-6; Penalty §12ak is only for zeroLength-hinge models). (2) A helper `_df(story, tag, ...)` called as `_df(s, 201, ...)` collides tags across stories because the helper used the relative `tag` (201) directly instead of `s*1000+201`, and the `story` param was dead — `MapOfTaggedObjects::addComponent - not adding as one with similar tag exists`. Fix: helpers take the ABSOLUTE tag computed by the caller; source scheme is `story*1000+{group}`. (3) corotTruss braces need `truss_tags`/`save_trust_resp` in the ODB, not `frame_tags` (§12ai); for this model `save_frame_resp=False`. (4) Source runs 13 triaxial base_motions NOT in repo → single-component NR94cnp.txt X-dir validation substitute (VividConcrete/elkady2019 pattern), run_dynamic() generic via GM_FILE/GM_DT/GM_NPTS/GM_DIR; GM after loadConst (§12i). (5) This source's rectangular confinement `ke=ke1·ke2·ke3/(1-rou_cc)` differs from the VividConcrete column models' `(nl-2)/nl*(1-s/b)` — port each source's CreateConcreteMaterial.tcl ke verbatim, don't reuse another model's. Validation: gravity lf=1.00, T1=0.577s T2=0.512s T3=0.163s (physical 5-story RC wall-frame), dynamic 2495/2495 steps converge, roof X-drift -172 mm (0.94%), peak inter-story drift 1.39% (story 2), 6 vis HTMLs incl. step slider. Source: VividCond_UCSD_full_fivestory conversion (5-story RC frame-wall building, 2 perimeter frames + 2 walls + corotTruss braces + rigid diaphragms, Zhong Stanford/UCSD 2017-2019). |
| 2026-07-10 | 1.37.0 | **Long cyclic protocols — fixed-increment fallback chain stalls mid-protocol; SmartAnalyze sub-stepping + vis_defo for the peak plot (§12am):** (1) A faithful 1:1 port of the source `RunStaticLoading.tcl` manual fallback chain (Newton→Newton -initial→ModifiedNewton→ModifiedNewton -initial→Broyden→NewtonLineSearch) STALLS mid-protocol at step ~14529 (~1.6% drift, 44 mm) of a 22455-pt cyclic protocol — every fallback retries the SAME full increment with a different algorithm, but on a hard unloading step the fiber-section tangent is ill-conditioned over the whole increment so no single full-size step converges. NOT collapse: the same step fails even earlier (~step 13475) with DuctileFracture removed (`ForceBeamColumn3d::update() - section failed in setTrial`). Fix: `opst.anlys.SmartAnalyze` (repo convention, elkady2019/padgett_jamie) with `relaxation=0.5`, `minStep=1e-3`, `algoTypes=[40,10,20,30,50,60]`; feed ONE target increment at a time via `static_split([incr], maxStep=abs(incr))` so recorders keep 1:1 alignment with the experimental protocol. (2) `vis_05_peak_deformed.html` was silently missing because `post_process` called `plot_nodal_responses(defo_scale=True)` directly under a bare `try/except`; fixed via the repo `vis_defo` helper (numeric scale, absMax step). (3) `openseespywin` gates on Python 3.8 — the runnable interpreter is the conda `opensy` env (3.12.12). Validation: cyclic 22455/22455 steps (was 14528), peak drift ±158 mm = 6.23 in / 5.8% (was stalled at 44 mm), base shear ±13.25 kip (was ~4.6 kip), 44 force sign-changes → proper loops, 5 vis HTMLs. Source: VividConcrete_RCconc_full_subassembly conversion (3D square RC column, fiber forceBeamColumn + 2 zeroLengthSection bar-slip, Zhong Stanford 2017). |
| 2026-07-09 | 1.36.0 | **Imperial→N-mm mass double-conversion trap + rank-deficient-mass ARPACK eigen failure (§12al):** (1) When the source computes mass as `m = P/g` and P is converted to Newtons, dividing by g[mm/s²] already gives N·s²/mm — multiplying again by `kip/inch` (175.13) double-converts to a 4448× too-heavy mass → T1 = 56 s instead of 0.85 s. Detection: T1 off by ~4000× (the kip factor). Fix: `m = P_GRAVITY[N] / (G_INCH*inch)` with no extra factor. (2) A rank-deficient mass matrix (mass on only 1 node / 2 DOFs) defeats the ARPACK subspace eigen solver (`ArpackSolver::Error info = -9999 / Could not build an Arnoldi factorization`); static lateral stiffness is correct so it's not a mechanism. Fix: `ops.eigen("-fullGenLapack", N)` — deviates from §12h-2 (which addresses stiffness contrast, not mass rank); fullGenLapack factorizes M⁻¹K directly and resolves rank-deficient M. (3) Verified VividConcrete: T1 56.6s→0.849s after mass fix; dynamic 2490/2490 Northridge steps converge. Source: VividConcrete conversion (3D circular RC column, fiber forceBeamColumn + zeroLengthSection bar-slip, Zhong Stanford 2017). |
| 2026-07-09 | 1.35.0 | **equalDOF + zeroLength hinge topology — base shear at column-base node not fixed node; Penalty vs Transformation (§12ak):** (1) Concentrated-plasticity hinges modelled as zeroLength between coincident nodes (stiff mats on DOFs 1-5 rigid, IMK hinge on DOF 6 RZ) plus `equalDOF(master, slave, 1,2,3)` divert the translational shear to the column-base node, NOT the fixed node — `nodeReaction(fixed_node,1) ≈ 3e-31` while `nodeReaction(column_base,1)` carries the full shear; `eleForce(spring)` shows pure moment only. (2) Fix: read base shear from the column-base nodes (above the springs), not the fixed nodes; a converged pushover with all-zero CSV base shear means the wrong node is being read. (3) Switching the pushover from `constraints("Penalty",1e15,1e15)` to `Transformation` (expecting better reactions) STALLS at 1.69% drift where Penalty converged 400 steps to 10% — the equalDOF+zeroLength topology is better-conditioned under Penalty; both return correct reactions at a directly-fixed node in a minimal test, so Penalty is not the bug. (4) `ops.reactions()` must be called before in-loop `nodeReaction` — SmartAnalyze's StaticAnalyze does not compute reactions automatically. Rule: for zeroLength-hinge models use Penalty throughout and read base shear from the node above the spring, with `ops.reactions()` before each read. Source: Bessette conversion (3D fixed-base RC1 pushover, JP3 study, 13 elasticBeamColumn + 4 zeroLength IMK springs). |
| 2026-07-09 | 1.34.0 | **Chevron CBF pushover — recovery-ladder load-factor spam vs step-0 failure; EnergyIncr+Newton stalls in brace-buckling transition (§12aj):** (1) A pushover whose run log is dominated by `DisplacementControl::newStep - failed in solver` / `domain at load factor ~10-12` warnings, yet writes N>1 points to `pushover_curve.csv`, is NOT failing at step 0 — it converged N steps then stalled; the load-factor spam is the recovery ladder firing on the failing (N+1)th step, not evidence of §12z pattern-freezing. `state.history`/CSV is appended only after a converged step, so its length is the authoritative converged-step count. (2) For `BradleyCameron_R3` (3-story chevron CBF, dispBeamColumn fiber braces + IMKBilin hinges + zeroLength weld springs), the curve dies at 0.15% roof drift with base shear still monotonically rising and zero weld fractures — the elastic-to-brace-buckling transition, same fiber-section tangent-ill-conditioning class as §12x/§12z (RC sources). Fix: §12z-3/5 recipe — `NormDispIncr` @ 1e-5 + `KrylovNewton` primary + `tryLooseTestTol`; shrink `PUSHOVER_DX` if element-level `dispBeamColumn update` failures appear past ~1%. (3) `ops.rayleigh()` global is a documented simplification of the source's two per-`region -rayleigh` calls; eigen periods match (T1 0.907→0.985s) so faithful here, but port per-region calls exactly when spring/element damping matters. (4) Validation checklist confirming "model correct, only solver stalls": data extraction exact vs `B-WeldInfo.tcl`, T1≈0.9s physical, mass on DOF1 = 3061 kip, ELFP 196 kip @ LF=1.0, §12z ordering correct, gravity lf=1.00. Source: BradleyCameron_R3 verification (conformant re-conversion of bradley2021_Building_system, Sizemore 2017 / Bradley et al. 2021 DesignSafe PRJ-2957). |
| 2026-07-06 | 1.33.0 | **Truss tags in `frame_tags` crash opstool's basic-force extractor (§12ai):** A `truss` element's `basicForces` response is length 1 (`[N]`); `opstool.post._get_response._get_beam_basic_resp()` only special-cases lengths 0 and 3, so any truss tag passed to `CreateODB(frame_tags=[…])` slips through to the sign-flip block and raises `IndexError: list index out of range` at `resp[1]` — at ODB construction, before any step is collected. Fix: keep `frame_tags` beam-column-only; truss axial forces use the dedicated `save_truss_resp=True` + `truss_tags=[…]` path (length-1 aware). Cross-ref §12u restated for 3D STKO frame: `node_tags=[…]` filtering still breaks `plot_nodal_responses(defo_scale=True)` deformed plots (`shapes (3,3) (282,3)` broadcast error) — omit `node_tags` (pass `None`) when the ODB feeds a full-mesh deformed plot. Source: GutierrezSotoMariantonieta conversion (3D self-centering PT steel braced frame, STKO 13-file build). |
| 2026-07-05 | 1.32.0 | **PM4Sand FirstCall routing & mixed-ndf fictitious-mass scoping (§12ah):** (1) PM4Sand's `FirstCall` parameter is mandatory at the elastic→plastic transition (triggers internal init that reads gravity stress state and populates stress-dependent secondary params); without it the first plastic step divides by zero → NaN residuals. OpenSeesPy requires the trailing matTag **as a string**: `ops.setParameter("-val", 0, "-ele", ele, "FirstCall", "<matTag_str>")`. Passing it as int → "Invalid String Input!"; dropping it → silent NaN. Correction to §12ab point 3: the PostShake "drop the trailing tag" rule applies only to PDMY02's PostShake, not PM4Sand's FirstCall. (2) Plastic gravity needs KrylovNewton + dt=1.0 (same as §12ae PDMY02 recipe — PM4Sand's yield-surface tangent defeats plain Newton). (3) The §12ag `_ensure_minimum_mass()` helper must be scoped to a single ndf when the model mixes ndf (soil ndf=3 + dashpot ndf=2 here); calling `ops.mass(tag, m1, m2, m3)` on a 2-DOF node raises "incompatible matrices". (4) `ops.analysis("Transient")` is required after `wipeAnalysis()` for manual `ops.analyze()` loops — SmartAnalyze instantiates its own analysis internally, manual loops do not. Without it: "WARNING No Analysis type has been specified". (5) For 10k+ element / 16k+ step SSPquadUP models, disabling `save_plane_resp`/`compute_mechanical_measures` removes pure overhead (all-zeros per §12ad anyway); ODB every 200th step + manual Newton loop at CFL-limited dt=0.001 keeps the dynamic phase tractable. PM4Sand constitutive evaluation is genuinely expensive (per-step tangent ~5–10× PDMY02) — there's no algorithmic shortcut for that. Source: RathjeEllen conversion (18-case GiD UWquad2D parametric sweep, PM4Sand + SSPquadUP + Lysmer dashpot). |
| 2026-06-29 | 1.31.0 | **SmartAnalyze compatibility via fictitious-mass regularisation (§12ag):** (1) Zero-mass free DOFs (bearing-top nodes, bent-bottom nodes) cause K_eff singularity at SmartAnalyze's micro-step sizes — the mass term `1/(β·Δt²)·M` vanishes where M=0, leaving only K_t which is ill-conditioned. (2) Fix: `_ensure_minimum_mass(1e-6)` assigns a fictitious mass (0.00003% of deck mass) to all DOFs — regularises K_eff without affecting dynamics. (3) SmartAnalyze goes from 0→648/1200 steps with the fix; manual Newton loop at dt=0.001 still needed for 100% coverage. (4) Toggleable `USE_SMARTANALYZE` flag keeps both modes in a single `model.py`. Source: padgett_jamie SmartAnalyze variant (3D MSSS bridge, BandGeneral, gravity ramp). |
| 2026-06-29 | 1.30.0 | **3D MSSS bridge conversion — gravity-as-ramp, BandGeneral solver, manual Newton loop (§12af):** (1) Static LoadControl cannot converge past ~40% gravity for stiffness-contrast bridge models — fix: apply ALL gravity as a transient ramp (0→100% over 2s, GM zero-padded). (2) UmfPack & SparseGEN fail to factor K_eff (return "numeric analysis returns 1" / SuperLU Error 1) — BandGeneral (LAPACK dgbsv) works reliably. (3) SmartAnalyze adaptive sub-stepping hits singular K_eff at Δt≈6e-7s — manual Newton loop at fixed dt=0.001s with NewtonLineSearch fallback converges 22000/22000 steps. (4) Full-gravity eigen periods (T1=2.69s, T2=1.74s) are ~20% shorter than partial-gravity (T1=3.41s). Source: padgett_jamie model conversion (Nielson 2005, Padgett 2007). |
| 2026-06-26 | 1.29.0 | **9_4_QuadUP site response — base bubble-node fixity, plastic-gravity solver, post-shake divergence (§12ae):** (1) The 9-node `9_4_QuadUP` element's base **edge-mid ("bubble") node** must share the base UY fixity (`fix(n_bot, 0, 1)`, the notebook's `ops.fix(2, 0, 1)`) — left free it bows ~6 mm downward and the elastic→plastic PDMY02 transition diverges (Norm R ~6.6e5). This is easy to miss when rewriting the notebook's interleaved node tags into a clean grid mesh. (2) Plastic gravity (stage 1) needs **KrylovNewton + dt=1.0** — the notebook's `analyze(40, 500)` diverges under OpenSeesPy because Newton cycles at Norm~0.005 near the PDMY02 yield surface; KrylovNewton's secant acceleration escapes it. (3) Post-shake (PostShake=1) **diverges at dt≥0.01** (Norm R → ~1e11 → NaN); only dt=0.005 is stable, making a full 100 s consolidation ~16000 steps — so post-shake must be bounded/best-effort and `odb.save_response()` of the dynamic results must happen BEFORE post-shake. (4) opstool does not capture the u-p pore-pressure DOF into the `pressure` field (all-zeros) for 9_4_QuadUP/quadUP — verify physics via the σ₂₂ contour instead. Source: misty_effective stress site resp (9-node coupled u-p, 3-layer PDMY02, Lysmer dashpot). |
| 2026-06-26 | 1.28.0 | **ODB path ordering & single-Gauss-point stress projection (§12ac, §12ad):** (1) `opst.post.set_odb_path()` MUST be called BEFORE `CreateODB` — calling it after silently misroutes response data to the default `.opstool.output/` (repo root, gitignored), leaving `output/RespStepData-1.odb` empty. Silent failure: model runs clean, only post-processing reveals data unreachable. (2) `StressesAtNodes` reads all-zeros for single-Gauss-point elements (quadUP, reduced-integration quads) — opstool's Gauss→node projection supports only quad(4,4)/(9,9)/(8,9), not (4,1); the projection returns None and falls back to zero-fill. The Gauss-point `Stresses` are valid. Fix: use `resp_type="Stresses"` (averaged per element) not `StressesAtNodes`; read pore pressure from nodal `pressure` not σ₃₃. Verified σ₂₂ −308 to −4 kPa (correct vertical stress profile), σ₁₂ peak 63 kPa. (3) §12ab §4 corrected — its example recommended the broken `StressesAtNodes`. Source: pedroArduino_freefield stress contour debugging. |
| 2026-06-26 | 1.27.0 | **SSPquadUP correct signature & cross-element-type conversion hazards (§12ab):** (1) SSPquadUP has matTag BEFORE thick (opposite of quadUP) plus two extra args: e0 (initial void ratio per layer) and press (reference pressure 1.5e-6 kPa) — both REQUIRED at element level, not just in material. (2) Three different u-p element types exist for the same physics (SSPquadUP/quadUP/9_4_QuadUP) with distinct signatures — never copy arg lists across element types; identify source element first. (3) PostShake=1 parameter MUST be set on all PDMY02 elements after dynamic phase to activate post-shaking consolidation — missing it means no excess PWP dissipation. (4) 1D site response models with 1-column mesh + equalDOF produce deformed shapes that look like "one line" — this is correct; use plot_unstruct_responses for stress contour diagnostics instead. Source: pedroArduino_freefield SSPquadUP correction (1D PDMY02 soil column, 3-layer, Lysmer dashpot). |
| 2026-06-26 | 1.26.0 | **Effective-stress site response — quadUP signature & base fixity (§12aa):** (1) `quadUP` element requires `fmass` (fluid mass density) as the 4th arg after the 4 nodes (`thick matTag bulk fmass hPerm vPerm b1 b2` — 8 args, not 7). Omitting it shifts args left → zero gravity body force, silent failure with no deformation. Cross-element-type conversion (SSPquadUP→quadUP) must re-derive args from Python docs, never copy the Tcl list. (2) Sloped free-field columns need temporary base UX fixity during gravity (`fix 1 1 1 0`) then removal before dynamic (`remove sp 1 1`) — without it the rigid-body drift mode diverges (`ok=-3`, Norm R≈1e5, all disp 0.0). (3) OpenSeesPy `fix()` errors (unlike Tcl) if a DOF already has an SP — release with `ops.remove("sp", node, dof)` before re-fixing. Source: pedroArduino_freefield conversion (1D PDMY02 soil column, quadUP + Lysmer dashpot, kN-m-kPa-s). |
| 2026-06-25 | 1.25.0 | **§12z corrected — SmartAnalyze supports testType/testTol kwargs; element-level step-size fix:** (1) SmartAnalyze accepts `testType`, `testTol`, `testIterTimes`, `tryLooseTestTol`, `looseTestTolTo` as kwargs — no need for manual solver loop. Use `testType="NormDispIncr"`, `testTol=1.0e-5` for fiber-section RC pushover. (2) `ForceBeamColumn2d::update - failed to get compatible element forces & deformations` at >1% drift is an element-level convergence issue fixed by reducing `MAX_STEP_SIZE` from 0.5 to 0.2 mm (gives forceBeamColumn's internal Newton smaller increments). (3) Both elwoodKenneth and elwoodkenneth_C10 now use SmartAnalyze exclusively — all cycles through 3.2% drift complete with 🎉. Source: elwoodkenneth_C10 verification. |
| 2026-06-25 | 1.24.0 | **RC column cyclic pushover — lateral pattern ordering, zeroLength stiffness contrast, SmartAnalyze test tolerance (§12z):** (1) Lateral load pattern for DisplacementControl MUST be defined AFTER `ops.loadConst("-time", 0.0)` — if frozen at λ=0, DisplacementControl computes infinite load factor (6.59e19). Same mechanism as §12i (GM ordering). (2) ZeroLength base springs (1.75e14 N/mm) with fiber-section columns (7e8 N/mm) create ~2.4e5 stiffness contrast causing Newton to diverge on gravity step 0 — fix by fixing base node directly. (3) KrylovNewton (algoType=40) preferred over Newton for fiber-section RC pushover. (4) Natural peak-to-peak cyclic flow eliminates need for return-to-zero segments. Source: elwoodKenneth conversion (2D RC cantilever column, fiber-section forceBeamColumn, 36 Concrete02, 18 Steel02, 16-cycle cyclic pushover to 3.2% drift). |
| 2026-06-25 | 1.23.0 | **opstool tcl2py conversion behavior & workarounds (§12y):** (1) tcl2py actually executes OpenSees commands during conversion, not just syntax translation — convergence failures in source Tcl will block conversion; (2) OpenSeesMP code (getPID/getNP/barrier/after/vwait) must be stripped before conversion; (3) analysis execution loops must be commented out (leave setup commands for conversion); (4) tcl2py output reproduces source Tcl literally (forceBeamColumn + Newton + ft=3.0) — all §12x fixes still required; (5) tcl2py useful as verification tool for model definition, recorder setup, rigidDiaphragm, GM loading, Rayleigh damping. Source: BhatZeeshanManzoor G+4 RC infilled frame. |
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
| 2026-06-17 | 1.15.0 | **ODB Response Collection: fetch_response_step() is NOT optional (§12n):** Documented that CreateODB must be initialized with `save_nodal_resp=True` + `node_tags` AND `fetch_response_step()` must be called inside every converged step loop. Either missing produces an empty RespStepData directory — deformed-shape plots fail with `FileNotFoundError`. `ops.analyze(N, dt)` provides no hook for fetch, so a manual `ops.analyze(1, dt)` loop is mandatory for any analysis needing ODB deformation output. Debugging protocol and detection rules added. Source: XMU Chapter8.2 verification (both Ch8.1 and 8.2 were affected). |
| 2026-06-22 | 1.16.0 | **Sensitivity analysis with DDM (§12o) + Explicit dynamics / element removal (§12p) + 3D peridynamic grid model (§12q) + Plain pattern tsTag gotcha (§12r) + vis_utils fix:** Documented OpenSeesPy sensitivity API pitfalls from XMU Chapter11 conversion — `addToParameter` bare keywords, sensitivity recorder single-string arg, SmartAnalyze DDM incompatibility, CreateODB element-type flag matching, `parents[n]` depth dependency, explicit vis_* imports. Added §12p documenting explicit dynamics (CentralDifference) incompatibility with SmartAnalyze, ODB impracticality for large explicit analyses, `nodeCoord` unit awareness, element removal via `ops.remove()`, `numberer Plain` for explicit, `MultipleSupport` pattern syntax, and `vis_defo()` signature missing `odb_tag`/`resp_dof` params. Added §12q documenting 3D peridynamic grid patterns — `node_id()` helper, `set`-based visited check, transition-zone strength scaling (stress vs strain), per-bond Concrete02 materials, ODB truss-response disabling for large bond counts, and 400-step static fetch pattern. Added §12r documenting that `ops.pattern("Plain", tag, "Linear")` fails because the third arg must be a numeric tsTag, not a type string — explicit `ops.timeSeries("Linear", tsTag)` required. Fixed `vis_utils.py:vis_defo()` to accept `odb_tag`, `resp_type`, and `resp_dof` kwargs and forward them to `plot_nodal_responses()`. Sources: XMU Chapter12.2 PD conversion (2D, explicit, bond-breaking) and XMU Chapter12.3 PD conversion (3D, static, Concrete02). |
| 2026-06-23 | 1.19.0 | **opstool CreateODB node_tags & frame response memory (§12u):** Documented that `node_tags` in CreateODB breaks `plot_nodal_responses` deformation plots — shape mismatch when tracked nodes differ from model mesh nodes; omit `node_tags` for full mesh tracking (~58 MB for 406 nodes × 6001 steps). `save_frame_resp` defaults to True and can exhaust memory (~55 MB for 402 beam elements); set `save_frame_resp=False` when only nodal data is needed. Source: XMU Chapter13.2 debugging. |
| 2026-06-23 | 1.18.0 | **3D single-wheelset rigid-body modes & post-loadConst SP patterns (§12t):** Documented lessons from XMU Chapter13.2 conversion — eliminating rigid-body UY modes with 1 N/m soft spring; moving SP constraints MUST be created AFTER `loadConst` to remain modifiable; `ops.timeSeries` tag collisions after `wipeAnalysis` (use higher tags); SmartAnalyze Transient supports per-step `remove("sp")` + `sp()` updates; auxiliary node creation belongs before element definition. |
| 2026-06-23 | 1.17.0 | **Train-bridge interaction: wheel-rail SP constraints, fix/sp conflict, massless nodes (§12s):** Documented patterns from XMU Chapter13.1 refactoring — wheel position verification against actual node coordinates; `fix()`/`sp()` conflict on same DOF; mass distribution to all beam nodes to avoid singular mass matrices; SmartAnalyze transient compatibility with per-step SP modifications; SP-based moving wheel contact as alternative to custom WheelRail elements; SI-unit model structural conformance to AGENT.md without unit conversion. |
| 2026-07-28 | 1.48.0 | **3D Fiber section `-GJ` requirement, `timeSeries` integer tag in `pattern`, Windows SmartAnalyze encoding & dynamic `standards` path search (§12az):** (1) **3D `section("Fiber")` REQUIRES `-GJ` flag in OpenSeesPy:** OpenSees Tcl only emits a warning (`WARNING torsion not specified`), but OpenSeesPy raises a fatal `opensees.OpenSeesError`. Always pass `-GJ, Gj` (e.g. `ops.section("Fiber", secTag, "-GJ", Gj)`) when defining 3D fiber sections. (2) **OpenSeesPy `ops.pattern` REQUIRES explicit `timeSeries` integer tag:** `ops.pattern("Plain", 1, "Linear")` fails with `WARNING failed to get load pattern tag` / `WARNING failed to create pattern` because the 3rd argument must be an integer `tsTag` created beforehand via `ops.timeSeries("Linear", tsTag)`. (3) **Windows console encoding in `SmartAnalyze`:** progress bar emojis cause `UnicodeEncodeError` on Windows consoles with default single-byte encodings (e.g. cp1252); pass `printPer=0` / `testPrintFlag=0` to `SmartAnalyze` or set environment variable `$env:PYTHONIOENCODING="utf-8"`. (4) **Dynamic `standards/` path resolution:** avoid fixed `parents[2]` indexing for deeply nested models (e.g. `models/Dino/<Topic>/<UniqueID>/model.py`); use dynamic search `for p in Path(__file__).parents: if (p / "standards").exists(): sys.path.insert(0, str(p / "standards")); break`. Source: Dino_RC_Column_3D_Pushover conversion (3D RC cantilever column pushover, original co.tcl/co2.tcl). |

---
*This file is the single source of truth for the OpenSeesPy standardisation agent.
