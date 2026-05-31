# OpenSeesPy Standardisation Framework

An engineering-focused OpenSeesPy repository for standardized finite-element modelling, automated auditing, visualization, validation, and AI-assisted model generation.

---

# Overview

This repository provides a structured framework for developing, auditing, validating, and maintaining OpenSeesPy finite-element models using deterministic engineering standards.

The project introduces:

* standardized OpenSeesPy project architecture,
* enforced unit consistency (`N-mm-MPa`),
* automated audit workflows,
* engineering validation utilities,
* integrated `opstool` visualization pipelines,
* standardized nonlinear analysis procedures,
* structured model cataloguing,
* AI-agent-compatible modelling workflows.

The framework is designed for:

* structural engineering research,
* nonlinear finite-element modelling,
* geotechnical and underground structures,
* soil-structure interaction (SSI),
* reinforced concrete and steel systems,
* reproducible simulation workflows,
* AI-assisted OpenSeesPy generation and refactoring.

---

# Core Objectives

## 1. Standardized OpenSeesPy Modelling

All models follow a deterministic architecture with:

* mandatory section ordering,
* standardized naming conventions,
* explicit tag allocation rules,
* centralized unit handling,
* reproducible analysis workflows.

---

## 2. Engineering Validation

The framework separates:

* code correctness,
* engineering correctness.

Validation utilities are intended to detect:

* floating nodes,
* disconnected domains,
* rigid body mechanisms,
* unsupported DOFs,
* duplicate nodes,
* invalid meshes,
* unstable numerical configurations.

---

## 3. AI-Assisted OpenSeesPy Development

This repository is designed to work with AI coding agents through the included:

```text
AGENT.md
```

The agent specification enables:

* automated script auditing,
* OpenSeesPy refactoring,
* template-driven model generation,
* unit-system conversion,
* visualization insertion,
* catalogue synchronization,
* nonlinear analysis standardization.

---

## 4. Geotechnical & Underground Modelling

The framework explicitly supports:

* diaphragm walls,
* excavation staging,
* tunnel analysis,
* effective stress analysis,
* soil-structure interaction,
* groundwater conditions,
* staged construction simulation.

---

# Repository Structure

```text
opensy/
│
├── AGENT.md
├── README.md
├── opensees_catalogue.json
│
├── standards/
│   ├── units.py
│   ├── vis_utils.py
│   ├── validation_utils.py
│   ├── mesh_utils.py
│   ├── gmsh_import.py
│   ├── tagging.py
│   ├── load_utils.py
│   ├── soil_profile.py
│   ├── material_library.py
│   └── section_library.py
│
├── templates/
├── models/
├── Opensees_references/
└── tests/
```

---

# Key Features

## Standardized Unit System

The repository uses:

```text
N · mm · MPa · kg · s
```

All dimensional quantities require explicit unit multipliers.

Example:

```python
wall_thickness = 800.0 * mm
fy = 500.0 * MPa
```

---

## Standardized Nonlinear Analysis

All nonlinear analysis workflows use:

```python
opst.anlys.SmartAnalyze
```

The framework standardizes:

* convergence recovery,
* adaptive step subdivision,
* algorithm switching,
* nonlinear solver management.

---

## Integrated Visualization Pipeline

Visualization is standardized using:

```text
opstool → plotly → HTML
```

Mandatory visualization checkpoints include:

* node geometry,
* model geometry,
* loading visualization,
* pre-analysis verification,
* deformed shapes,
* response contours.

---

## Output Database Standardization

Response collection uses:

```python
opst.post.CreateODB
```

instead of legacy OpenSees recorders.

This provides:

* structured result storage,
* consistent post-processing,
* scalable output handling,
* improved AI interoperability.

---

# Supported Model Classes

The framework supports:

| Model Class     | Description                |
| --------------- | -------------------------- |
| FRAME_2D        | 2D frame systems           |
| FRAME_3D        | 3D frame systems           |
| WALL_2D         | Structural wall systems    |
| GEOTECH_2D      | 2D geotechnical analysis   |
| GEOTECH_3D      | 3D geotechnical analysis   |
| SSI_2D          | Soil-structure interaction |
| SSI_3D          | 3D SSI                     |
| FIBER_NONLINEAR | Fiber nonlinear systems    |
| SHELL           | Shell / plate structures   |
| TUNNEL          | Underground structures     |
| BRIDGE          | Bridge systems             |

---

# Intended Applications

This framework is intended for:

* nonlinear structural analysis,
* earthquake engineering,
* underground excavation analysis,
* diaphragm wall design verification,
* research reproducibility,
* OpenSeesPy standardization,
* AI-assisted FEM generation,
* engineering education,
* parametric studies,
* benchmarking and validation.

---

# Design Philosophy

The repository follows several guiding principles:

## Deterministic Structure

All models should be:

* readable,
* auditable,
* reproducible,
* modular,
* scalable.

---

## Engineering-First AI

AI generation should follow engineering rules rather than free-form code generation.

The framework prioritizes:

* engineering consistency,
* numerical stability,
* maintainability,
* reproducibility.

---

## Separation of Concerns

The framework separates:

| Responsibility | Purpose                      |
| -------------- | ---------------------------- |
| Build          | Geometry/material definition |
| Validate       | Engineering checks           |
| Analyze        | Numerical execution          |
| Post-process   | Results and visualization    |

---

# Planned Future Development

Planned future capabilities include:

* Gmsh integration pipelines,
* MPI / parallel OpenSees workflows,
* automated pushover reporting,
* rebar demand extraction,
* diaphragm wall reinforcement verification,
* AI calibration workflows,
* BIM interoperability,
* cloud-based batch analysis,
* automated model benchmarking.

---

# Dependencies

Recommended environment:

```text
Python 3.x
OpenSeesPy
opstool
numpy
scipy
pandas
plotly
gmsh
pyvista
```

---

# Status

This repository is an actively evolving engineering framework. As of 2026-05-31.

## Model Inventory

| UniqueID | Type | Material | Loading | SmartAnalyze | ODB | Status |
|----------|------|----------|---------|-------------|-----|--------|
| [ST31_L2](models/ST31_L2/) | 2D underground | RC | Static | Static (DispControl) | Full | ✅ Working |
| [ST31_L1](models/ST31_L1/) | 2D underground | RC | Static | Static (DispControl) | Full | ✅ Working |
| [OReilly2019](models/OReilly2019/) | 3D frame | RC | Cyclic pushover | Static (DispControl) | Full | ✅ Working |
| [elkady2019](models/elkady2019/) | 2D frame | Steel | Dynamic + pushover | Transient + Static | Full | ✅ Working |
| [Homorzabad2021_K291](models/Homorzabad2021_K291/) | 3D braced frame | Steel | Dynamic earthquake | Transient only¹ | Selective + throttled² | ✅ Working |
| [nafeh2022](models/nafeh2022/) | 3D frame | RC + masonry infill | Gravity + eigen | Manual LoadControl³ | Full | ✅ Working |

> ¹ **SmartAnalyze Static exception:** Gravity uses manual LoadControl loop — SmartAnalyze forces DisplacementControl which is incompatible with load-controlled gravity for this model ([AGENT.md §3c](AGENT.md)).
>
> ² **ODB throttling:** Dynamic fetch_response_step every 10th step; frame/truss/link tags limited to key elements ([AGENT.md §3d](AGENT.md)).
>
> ³ **Manual LoadControl gravity:** SmartAnalyze Static incompatible with load-controlled gravity ([AGENT.md §3c](AGENT.md)).

## Lessons Learned (by model)

### Homorzabad2021_K291 (2026-05-31)

1. **SmartAnalyze Static forces DisplacementControl.** `StaticAnalyze()` calls `ops.integrator("DisplacementControl", ...)` internally, overriding any preset integrator. Load-controlled gravity (LoadControl + Linear algorithm) cannot work through SmartAnalyze Static. The approved workaround is a manual `ops.analyze()` loop with `odb.fetch_response_step()`. This is the **only** permitted exception to the SmartAnalyze mandate. Pushover and other displacement-controlled analyses are unaffected.

2. **ODB fetch_response_step() scales with tracked element count.** On a 300-node, 500-element 3D model at 2500 time steps, calling `fetch_response_step()` for every node/element at every step means ~2M+ OpenSees API calls — enough to appear as a hang. Mitigation: (a) pass `node_tags`/`frame_tags`/`truss_tags`/`link_tags` kwargs to `CreateODB` to only track what's needed for post-processing; (b) throttle collection to every Nth step for transient analyses (`if i % 10 == 0: odb.fetch_response_step()`). Aim for ≤500 total fetch calls per analysis phase.

### nafeh2022 (2026-06-01)

5. **opstool has a breaking API change at 1.0.** Models written for 0.8.7 (`GetFEMdata`/`OpsVisPlotly`/HDF5) will fail with `AttributeError` on 1.0. The `opensy` conda environment (Python 3.11, opstool 1.0.26) is the target runtime. See [AGENT.md §11](AGENT.md) for the full API migration table.

6. **vis_utils.py and model.py must match the opstool version.** When switching between opstool versions, both files need coordinated updates — the function signatures and import patterns differ completely. The numpy `np.NAN`/`np.NaN` compatibility hack is only needed for opstool 0.8.7 on NumPy >= 2.0.

### OReilly2019 (2025-05)

7. **Fiber-section ODB collection is expensive but manageable for pushover.** For a 3D RC frame with fiber sections under cyclic pushover (~200 steps), full ODB collection is acceptable. No throttling needed below 500 steps.

8. **Joint2D elements need explicit link_tags in CreateODB.** Zero-length rotational springs (Pinching4) won't appear in `frame_tags` — they must be listed separately in `link_tags` for force-deformation data in the ODB.

---

# License

MIT
---

# Acknowledgements

This framework builds upon:

* OpenSees / OpenSeesPy
* opstool
* the earthquake engineering research community
* nonlinear finite-element modelling practices
* geotechnical and structural engineering workflows
