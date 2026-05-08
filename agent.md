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
- Generate new scripts from a user description + catalogue metadata
- Keep the catalogue (`opensees_catalogue.py`) in sync with actual files

You operate on the repository rooted at `opensy/`.
You MUST NOT modify files outside this root unless explicitly told to.

---

## 2. Repository Layout (Authoritative)

```
opensy/
│
├── AGENT.md                        ← (this file) agent instructions
├── opensees_catalogue.py           ← master catalogue (single source of truth)
├── README.md                       ← human-readable project overview
│
├── standards/                      ← all reusable building blocks
│   ├── units.py                    ← SI unit constants  (kN, m, MPa …)
│   ├── analysis_utils.py           ← gravity / pushover / IDA helpers
│   ├── plot_utils.py               ← standardised matplotlib helpers
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
├── Opensees_references/                      ← learning examples (no research intent)
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
Model : <Short descriptive name>
UniqueID : <matches catalogue UniqueID>
Author   : <name>
Date     : YYYY-MM-DD
Purpose  : <one sentence>
Ref      : <paper / report DOI or URL>
Units    : kN, m, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import openseespy.opensees as ops
import numpy as np
import sys
from pathlib import Path

# Add standards/ to path if running standalone
sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
from analysis_utils import run_gravity, run_pushover, run_dynamic
from plot_utils import plot_pushover, plot_time_history
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
# Geometry
n_stories   = 3
n_bays      = 3
h_story     = 3.0 * m
l_bay       = 5.0 * m

# Material properties
fc          = 30.0 * MPa   # concrete compressive strength
fy          = 420.0 * MPa  # steel yield strength
Es          = 200.0 * GPa  # steel elastic modulus

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

# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_analysis(output_dir: Path) -> None:
    init_model()
    define_materials()
    define_sections()
    define_nodes()
    define_boundary_conditions()
    define_elements()
    define_recorders(output_dir)
    define_gravity_loads()
    run_gravity()
    define_lateral_loads()
    run_pushover(n_steps=100, d_target=0.10 * m)   # adjust as needed

# ── 13. POST-PROCESSING ──────────────────────────────────────────────────────
def post_process(output_dir: Path) -> None:
    plot_pushover(output_dir / "pushover.txt")

# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    run_analysis(output_dir)
    post_process(output_dir)
```

---

## 4. Coding Conventions (Enforced by Audit)

| Rule | ✅ Required | ❌ Forbidden |
|------|------------|-------------|
| Import style | `import openseespy.opensees as ops` | `from openseespy.opensees import *` |
| Naming | `snake_case` everywhere | `camelCase`, `PascalCase`, `ALLCAPS` vars |
| Tags | Named `UPPERCASE` constants in Tag Registry | Bare integers inline (e.g. `ops.fix(1, …)`) |
| Functions | One function per section (see layout above) | Flat script with no functions |
| Units | Import from `standards/units.py` | Redefined per file |
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
[ ] 0.  Header docstring present with all required fields
[ ] 1.  `import openseespy.opensees as ops` (not wildcard)
[ ] 2.  `standards/` imports used (units, analysis_utils, plot_utils)
[ ] 3.  Tag Registry section present; all tags are named constants
[ ] 4.  Parameters section present; all values carry unit multipliers
[ ] 5.  `init_model()` calls `ops.wipe()` before `ops.model()`
[ ] 6.  Each FEM phase is its own function
[ ] 7.  Section banners follow `# ── N. TITLE ──` pattern
[ ] 8.  No magic numbers outside Tag Registry / Parameters
[ ] 9.  Recorders write to `output/` via `Path`
[ ] 10. `if __name__ == "__main__":` guard present
[ ] 11. UniqueID in header matches an entry in opensees_catalogue.py
[ ] 12. Corresponding folder name == UniqueID
[ ] 13. README.md exists in model folder
[ ] 14. Ground motion files are in `ground_motions/` subfolder
[ ] 15. No absolute file paths in script
```

---

## 6. Catalogue Sync Rules

- The folder name under `models/` MUST equal the `UniqueID` in `opensees_catalogue.py`.
- When you create a new model folder, you MUST also add or update the catalogue entry.
- When you rename a folder, update the catalogue `UniqueID` to match.
- The catalogue fields that MUST be populated (not blank / "NA") for a model to be
  considered **complete**:
  - `UniqueID`, `URL`, `purpose`, `Description of Model`,
    `2D/3D`, `Material`, `Lateral Loading`, `file format`

---

## 7. Agent Workflow — Step-by-Step

### 7a. Auditing an existing file
```
1. Read the script.
2. Run through Audit Checklist (Section 5).
3. Print a table: item | status | note.
4. List all FAIL items with a one-line fix description.
5. Ask user: "Refactor now? (yes / no / show diff only)"
```

### 7b. Refactoring a script
```
1. Run audit first.
2. For each FAIL: apply the fix.
3. Do NOT change model logic (element types, material params, load patterns).
4. Write refactored file to same path.
5. Run audit again to confirm all PASS.
6. Summarise changes made.
```

### 7c. Generating a new model from a catalogue entry
```
1. Retrieve the catalogue entry by UniqueID.
2. Select the closest template from templates/ based on:
   - 2D/3D field  → template_2d_* or template_3d_*
   - Material field → fiber section if RC/Steel, elastic if "Elastic"
   - Lateral Loading → gravity / pushover / dynamic branch
3. Copy template to models/<UniqueID>/model.py.
4. Populate header docstring from catalogue fields.
5. Insert TODO markers for every section that needs user input.
6. Auto-generate README.md from catalogue entry.
7. Create ground_motions/ and output/ (with .gitkeep) subdirectories.
8. Report: "Scaffold created. Open model.py and resolve all TODO items."
```

### 7d. Updating the catalogue
```
1. Parse opensees_catalogue.py.
2. Locate the entry dict by UniqueID.
3. Apply field updates provided by the user.
4. Write back — preserve list order and formatting.
5. Confirm: "Catalogue updated: <field> changed from <old> to <new>."
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

# ❌ Flat script (no functions)
ops.wipe()
ops.model(...)
ops.node(1, 0.0, 0.0)
# ... 300 more lines at module level
```

---

## 11. Versioning & Change Log

| Date | Version | Change |
|------|---------|--------|
| 2025-05-08 | 1.0.0 | Initial AGENT.md created |

---

*This file is the single source of truth for the OpenSeesPy standardisation agent.
Update Section 11 whenever this file changes.*
