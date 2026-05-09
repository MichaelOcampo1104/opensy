# AGENT.md — OpenSeesPy Standardisation Agent

> **Purpose:** This file instructs an AI coding agent how to standardise,
> audit, and generate OpenSeesPy finite-element model files consistently
> across the project catalogue.

---

## 1. Agent Identity & Scope

You are the **OpenSeesPy Standardisation Agent**.
Your job is to:
- Audit existing `.py` / `.tcl` OpenSees scripts against the project standard
- Refactor non-conforming scripts into the standard layout
- **Convert all dimensional inputs to N and mm** (see Section 3a)
- **Insert `opstool` visualizations** after each major build stage (see Section 3b)
- Generate new scripts from a user description + catalogue metadata
- **Create or update the JSON catalogue file** for every converted / new model (see Section 7e)
- Keep the catalogue (`opensees_catalogue.json`) in sync with actual files

You operate on the repository rooted at `opensy/`.
You MUST NOT modify files outside this root unless explicitly told to.

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
│   ├── analysis_utils.py           ← gravity / pushover / IDA helpers
│   ├── vis_utils.py                ← opstool visualisation helpers  ← NEW
│   ├── material_library.py         ← named material factory functions
│   ├── section_library.py          ← named fiber-section builders
│   └── recorder_utils.py           ← recorder factory functions
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
│       └── output/                 ← recorder output (git-ignored)
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
import opstool as opst          # visualisation  — use opst.vis.plotly.*
import numpy as np
import sys
from pathlib import Path

# Add standards/ to path if running standalone
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from analysis_utils import run_gravity, run_pushover, run_dynamic
from vis_utils import _headless   # CI headless guard shared across modules
from recorder_utils import add_node_recorders, add_element_recorders

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

# ── 7V. VISUALISE — NODES ────────────────────────────────────────────────────
def vis_stage_nodes(output_dir: Path) -> None:
    """Render node positions and boundary conditions; saves HTML to output_dir."""
    if _headless():
        return
    fig = opst.vis.plotly.plot_model(show_node_label=True, show_ele_label=False)
    fig.write_html(str(output_dir / "vis_01_nodes.html"))

# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    pass  # TODO  ops.fix(node_tag, *dofs)

# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    pass  # TODO

# ── 9V. VISUALISE — MODEL (NODES + MEMBERS) ──────────────────────────────────
def vis_stage_model(output_dir: Path) -> None:
    """Render full undeformed model geometry; saves HTML to output_dir."""
    if _headless():
        return
    fig = opst.vis.plotly.plot_model(show_node_label=True, show_ele_label=True)
    fig.write_html(str(output_dir / "vis_02_model.html"))

# ── 10. RECORDERS ────────────────────────────────────────────────────────────
def define_recorders(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    add_node_recorders(output_dir)
    add_element_recorders(output_dir)

# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity_loads() -> None:
    pass  # TODO

def define_lateral_loads() -> None:
    pass  # TODO  (pushover pattern or ground-motion input)

# ── 11V. VISUALISE — LOADS ───────────────────────────────────────────────────
def vis_stage_loads(output_dir: Path) -> None:
    """Render applied load vectors; saves HTML to output_dir."""
    if _headless():
        return
    fig = opst.vis.plotly.plot_model(show_ele_loads=True, show_node_label=False)
    fig.write_html(str(output_dir / "vis_03_loads.html"))

# ── 11C. PRE-ANALYSIS CHECK ──────────────────────────────────────────────────
def vis_stage_pre_analysis(output_dir: Path) -> None:
    """Full model + loads — final sanity check before solver; saves HTML."""
    if _headless():
        return
    fig = opst.vis.plotly.plot_model(
        show_ele_loads=True,
        show_node_label=True,
        show_ele_label=True,
    )
    fig.write_html(str(output_dir / "vis_04_pre_analysis.html"))

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_analysis(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    vis_stage_nodes(output_dir)                    # ← V1: nodes + supports
    define_elements()
    vis_stage_model(output_dir)                    # ← V2: full geometry
    define_recorders(output_dir)
    define_gravity_loads()
    define_lateral_loads()
    vis_stage_loads(output_dir)                    # ← V3: load vectors
    vis_stage_pre_analysis(output_dir)             # ← V4: pre-analysis check
    run_gravity()
    run_pushover(n_steps=100, d_target=100.0 * mm) # 100 mm target displacement

# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(output_dir: Path) -> None:
    from plot_utils import plot_pushover
    plot_pushover(output_dir / "pushover.txt")
    if not _headless():
        fig_defo = opst.vis.plotly.plot_defo(scale=10.0)
        fig_defo.write_html(str(output_dir / "vis_05_deformed.html"))

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    run_analysis(output_dir)
    post_process(output_dir)
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
| **V1 — Nodes** | `define_nodes()` + `define_boundary_conditions()` | `vis_nodes(output_dir)` | `show_node_label=True` | `vis_01_nodes.html` |
| **V2 — Model** | `define_elements()` | `vis_model(output_dir)` | `show_node_label=True, show_ele_label=True` | `vis_02_model.html` |
| **V3 — Loads** | `define_gravity_loads()` + `define_lateral_loads()` | `vis_loads(output_dir)` | `show_ele_loads=True` | `vis_03_loads.html` |
| **V4 — Pre-analysis** | All definitions complete, before solver | `vis_pre_analysis(output_dir)` | `show_ele_loads=True, show_node_label=True, show_ele_label=True` | `vis_04_pre_analysis.html` |

Additional optional checkpoints (add as needed):

| Stage | Call after… | Function | Output file |
|---|---|---|---|
| **V5 — Deformed (gravity)** | `run_gravity()` | `vis_defo(output_dir, filename="vis_05_defo_gravity.html", scale=10.0)` | `vis_05_defo_gravity.html` |
| **V6 — Deformed (lateral)** | `run_pushover()` / `run_dynamic()` | `vis_defo(output_dir, filename="vis_06_defo_lateral.html", scale=10.0)` | `vis_06_defo_lateral.html` |

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

import os
from pathlib import Path
import opstool as opst


def _headless() -> bool:
    """Return True when running in a headless / CI environment."""
    return os.getenv("OPENSEES_HEADLESS", "0") == "1"


def vis_nodes(output_dir: Path, filename: str = "vis_01_nodes.html") -> None:
    """V1 — Render node positions and boundary conditions.

    Args:
        output_dir: Folder where the HTML file is written.
        filename: Output filename (default: vis_01_nodes.html).
    """
    if _headless():
        return
    fig = opst.vis.plotly.plot_model(
        show_node_label=True,
        show_ele_label=False,
    )
    fig.write_html(str(output_dir / filename))


def vis_model(
    output_dir: Path,
    filename: str = "vis_02_model.html",
    show_node_label: bool = True,
    show_ele_label: bool = True,
) -> None:
    """V2 — Render full undeformed model geometry (nodes + members).

    Args:
        output_dir: Folder where the HTML file is written.
        filename: Output filename (default: vis_02_model.html).
        show_node_label: Annotate node tags on the figure.
        show_ele_label: Annotate element tags on the figure.
    """
    if _headless():
        return
    fig = opst.vis.plotly.plot_model(
        show_node_label=show_node_label,
        show_ele_label=show_ele_label,
    )
    fig.write_html(str(output_dir / filename))


def vis_loads(output_dir: Path, filename: str = "vis_03_loads.html") -> None:
    """V3 — Render applied load vectors superimposed on the geometry.

    Args:
        output_dir: Folder where the HTML file is written.
        filename: Output filename (default: vis_03_loads.html).
    """
    if _headless():
        return
    fig = opst.vis.plotly.plot_model(
        show_ele_loads=True,
        show_node_label=False,
        show_ele_label=False,
    )
    fig.write_html(str(output_dir / filename))


def vis_pre_analysis(
    output_dir: Path,
    filename: str = "vis_04_pre_analysis.html",
) -> None:
    """V4 — Full model + loads, final sanity check before solver runs.

    Args:
        output_dir: Folder where the HTML file is written.
        filename: Output filename (default: vis_04_pre_analysis.html).
    """
    if _headless():
        return
    fig = opst.vis.plotly.plot_model(
        show_ele_loads=True,
        show_node_label=True,
        show_ele_label=True,
    )
    fig.write_html(str(output_dir / filename))


def vis_defo(
    output_dir: Path,
    filename: str = "vis_05_deformed.html",
    scale: float = 10.0,
) -> None:
    """V5 — Deformed shape at current solver state.

    Args:
        output_dir: Folder where the HTML file is written.
        filename: Output filename (default: vis_05_deformed.html).
        scale: Displacement amplification factor for visualisation.
    """
    if _headless():
        return
    fig = opst.vis.plotly.plot_defo(scale=scale)
    fig.write_html(str(output_dir / filename))
```

> **CI / batch runs:** set `OPENSEES_HEADLESS=1` to suppress all pop-up windows
> without changing any model code.

---

## 4. Coding Conventions (Enforced by Audit)

| Rule | ✅ Required | ❌ Forbidden |
|------|------------|-------------|
| Import style | `import openseespy.opensees as ops` | `from openseespy.opensees import *` |
| Naming | `snake_case` everywhere | `camelCase`, `PascalCase`, `ALLCAPS` vars |
| Tags | Named `UPPERCASE` constants in Tag Registry | Bare integers inline (e.g. `ops.fix(1, …)`) |
| Functions | One function per section (see layout above) | Flat script with no functions |
| Units | **N, mm, MPa** from `standards/units.py` | Any other system; redefined per file |
| Unit multipliers | Every dimensional value carries `* <unit>` | Bare floats without unit annotation |
| Visualisation | Four opstool stages via `vis_utils.py` | No visualisation / direct opstool calls |
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
[ ] 2.  `standards/` imports used (units, analysis_utils, vis_utils, recorder_utils)
[ ] 3.  `import opstool as opst` present (alias must be `opst`, not `opsv`)
[ ] 4.  Tag Registry section present; all tags are named constants
[ ] 5.  Parameters section present; ALL dimensional values carry unit multipliers
[ ] 6.  All lengths in mm, forces in N, stresses in MPa — no kN/m/kip/ft/in survivors
[ ] 7.  `init_model()` calls `ops.wipe()` before `ops.model()`
[ ] 8.  Each FEM phase is its own function
[ ] 9.  Section banners follow `# ── N. TITLE ──` pattern
[ ] 10. No magic numbers outside Tag Registry / Parameters
[ ] 11. Recorders write to `output/` via `Path`
[ ] 12. `if __name__ == "__main__":` guard present
[ ] 13. UniqueID in header matches an entry in opensees_catalogue.json
[ ] 14. Corresponding folder name == UniqueID
[ ] 15. README.md exists in model folder
[ ] 16. Ground motion files are in `ground_motions/` subfolder
[ ] 17. No absolute file paths in script
[ ] 18. vis_stage_nodes() called after define_boundary_conditions()
[ ] 19. vis_stage_model() called after define_elements()
[ ] 20. vis_stage_loads() called after load patterns are defined
[ ] 21. vis_stage_pre_analysis() called immediately before the first solver step
[ ] 22. JSON catalogue entry exists and has no blank required fields
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

### 7a. Auditing an existing file
```
1. Read the script.
2. Run through Audit Checklist (Section 5) — items 0–22.
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
4. Insert vis_stage_* calls at the four mandatory checkpoints (Section 3b).
5. Do NOT change model logic (element types, element topology, load patterns).
6. Write refactored file to same path.
7. Run audit again to confirm all 22 items PASS.
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
    # vis_stage_model() missing — FAIL [VIS_MODEL]
    define_gravity_loads()
```

---

## 11. Versioning & Change Log

| Date | Version | Change |
|------|---------|--------|
| 2025-05-08 | 1.0.0 | Initial AGENT.md created |
| 2025-05-09 | 1.1.0 | Unit system → N/mm/MPa; opstool stages added; JSON catalogue workflow added |
| 2025-05-09 | 1.1.1 | opstool API corrected to `opst.vis.plotly.plot_model(...).write_html()`; all vis helpers now write HTML files to `output/`; `_headless()` guard moved to `vis_utils.py`; stage table updated with output filenames |

---

*This file is the single source of truth for the OpenSeesPy standardisation agent.
Update Section 11 whenever this file changes.*
