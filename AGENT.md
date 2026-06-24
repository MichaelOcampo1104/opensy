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

---

## 13. Versioning & Change Log

| Date | Version | Change |
|------|---------|--------|
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
| 2026-06-23 | 1.20.0 | **beamWithHinges ODB incompatibility & SmartAnalyze convergence tuning (§12v):** (1) beamWithHinges internal sections lack user-visible tags → `save_frame_resp=False` required in CreateODB (fixes "sectionForceDeformation(tag=0) none found" error). (2) Manual `ops.test()`/`ops.algorithm()` before SmartAnalyze is prohibited — SmartAnalyze manages these internally. (3) RC pushover needs full algorithm fallback list + `relaxation=0.5` + `tryAddTestTimes=True` for convergence at moderate drifts. (4) `constraints("Transformation")` preferred over `"Plain"` for SmartAnalyze pushover. (5) Cyclic pushover with negative increments should use a manual `StaticAnalyze` loop, not `static_split`. Source: Citiner conversion (RC cantilever column, fiber-section beamWithHinges, 23-segment cyclic pushover). |
| 2026-06-24 | 1.22.0 | **Tcl forceBeamColumn HingeRadau conversion + gravity convergence (§12x):** (1) Tcl format `HingeRadau $secTag $lpI $nIpI $lpJ $nIpJ` was mis-parsed — secTag swapped with nIpJ. (2) dispBeamColumn+HingeRadau preserves hinge lengths (200-225mm); forceBeamColumn state determination is unreliable in OpenSeesPy. (3) Newton/KrylovNewton diverge on gravity step 2 — 3D dispBeamColumn fiber-section tangent becomes singular due to stiffness contrasts (zeroLength 1e13 vs fiber beam 1e6). (4) ModifiedNewton+Penalty(1e13) is the stable combination — reaches ~66% gravity with relaxed tolerance (0.01). (5) `ops.uniaxialMaterial` cannot redefine existing tags; `ops.remove("uniaxialMaterial")` not supported — Concrete02 ft must be elevated (20 MPa) from initial definition. (6) Penalty springs regularise the matrix better than Transformation elimination for models with rigidDiaphragm + stiff zeroLength joints. Source: BhatZeeshanManzoor G+4 RC infilled frame, STKO/SimCenter Tcl -> Python. |

---
*This file is the single source of truth for the OpenSeesPy standardisation agent.
