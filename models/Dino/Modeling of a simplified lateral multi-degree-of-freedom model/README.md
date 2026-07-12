# Dino_MDOF_eigen

**Purpose:** Pure eigen / modal analysis of a simplified lateral multi-degree-of-freedom (MDOF) model — a 12-story uniform lumped-mass shear building. The model runs `eigen 10` and writes the 10 natural periods and mode shapes, validated against the closed-form uniform N-DOF shear-building frequency.

**Building System:** 12-story cantilever shear building, 36 m tall (3 m storeys), 13 nodes along z (node 1 = top at z=36000 mm, node 13 = base at z=0). Lumped mass = 100 (N·s²/mm = 100 tonne) on UX only at each node; UY/UZ/all rotations fixed; base fully fixed → **12 active lateral DOFs**. 12 `ElasticTimoshenkoBeam` elements with E=G=1e5 MPa, A=J=Iy=Iz=1e20 (rigid axial/bending/torsion), Avy=Avz=3000 mm² → **story shear stiffness k = G·Av/L = 1e5 N/mm**. This is the classic OpenSees shear-building idealization: beam elements whose only finite flexibility is shear.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6), 13 nodes, 12 `ElasticTimoshenkoBeam` elements (11-arg 3D form with explicit Avy/Avz), Linear geomTransf vector (1,0,0). Pure eigen analysis: `ops.eigen(10)` (default ARPACK subspace solver — uniform stiffness + full-rank mass, so neither §12h-2 stiffness-contrast nor §12al rank-deficient-mass rules apply). Mode shapes saved to the ODB via `save_eigen_data(mode_tag=m, solver="-genBandArpack")` for m=1..10. No loads, no gravity, no static/transient analysis step. λ values written to `Periods.txt` (source convention).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Elastic (E=G=1e5 MPa; shear-building idealization) |
| Lateral System | Cantilever shear building (12 ElasticTimoshenkoBeam) |
| Mass | 100 N·s²/mm (= 100 tonne) per floor, UX only |
| Analysis | Eigen / modal (10 modes) |
| Earthquake Records | NA (modal analysis) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (opensy conda env, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa, tonne |

## Running the model

```bash
conda activate opensy
python "models/Dino/Modeling of a simplified lateral multi-degree-of-freedom model/model.py"
```

Or directly:

```bash
C:/Users/micha/miniconda3/envs/opensy/python.exe "models/Dino/Modeling of a simplified lateral multi-degree-of-freedom model/model.py"
```

## Verification

No external reference file ships in `tcl_ref/` (no `Periods.txt`, no mode-shape `.out` files), so validation is against the **closed-form uniform N-DOF shear-building frequency**:

  ω_j = 2·√(k/m)·sin((2j−1)·π/(4N+2))   with N=12, k=1e5 N/mm, m=100 N·s²/mm.

| Mode | T_sim (s) | T_theory (s) | diff % |
|------|-----------|--------------|--------|
| 1  | 1.5822 | 1.5822 | 0.0000 |
| 2  | 0.5302 | 0.5302 | 0.0000 |
| 3  | 0.3215 | 0.3215 | 0.0000 |
| 4  | 0.2333 | 0.2333 | 0.0000 |
| 5  | 0.1854 | 0.1854 | 0.0000 |
| 6  | 0.1559 | 0.1559 | 0.0000 |
| 7  | 0.1363 | 0.1363 | 0.0000 |
| 8  | 0.1228 | 0.1228 | 0.0000 |
| 9  | 0.1134 | 0.1134 | 0.0000 |
| 10 | 0.1068 | 0.1068 | 0.0000 |

**Max diff: 0.0000% across all 10 modes.** The simulation reproduces the shear-building theory exactly — confirming the ElasticTimoshenkoBeam idealization (rigid axial/bending via 1e20, finite shear via Avy=Avz=3000) correctly reduces to a 12-DOF discrete shear building with k=1e5 N/mm/story. T1=1.582 s, T10=0.107 s.

## Output

Written to `output/`:
- `Periods.txt` — the 10 eigenvalues λ=ω² (source convention: single line of space-separated values)
- `periods_compare.png` — sim (blue) vs theory (grey) bar chart, 10 modes
- `mode_shapes.png` — first 4 mode shapes (UX amplitude vs height), normalised to top=1
- `vis_01_nodes.html`, `vis_02_model.html` — opstool mesh visualisations
- `vis_05_eigen_table.html` — opstool eigen table (all 10 modes: frequencies, periods, masses)
- `vis_06_eigen_modes.html` — opstool mode-shape subplots (modes 1–4, animated)
- `vis_07_mode1_animation.html` — opstool mode-1 animation
- `EigenData-1.odb/`, `ModelData-1.zarr/` — ODB response database (eigen + model data)

**References:**

Original source: `tcl_ref/co.tcl` (99-line Tcl OpenSees script, pure eigen analysis of a 12-DOF shear building).

**Notes:** Converted from `co.tcl`. **ElasticTimoshenkoBeam 11-arg 3D form** (§12av): OpenSeesPy requires `(tag,i,j,E,G,A,Jx,Iy,Iz,Avy,Avz,transfTag)` with explicit Avy/Avz; the 9-arg form (without shear areas) errors. **Shear-building idealization:** A=J=Iy=Iz=1e20 makes axial/bending/torsion rigid, leaving shear (Avy=Avz=3000) as the only finite flexibility → k_story = G·Av/L = 1e5 N/mm. **Dead materials** (tags 1,2,3 — `uniaxialMaterial Elastic`, never referenced because ElasticTimoshenkoBeam takes E,G as numeric literals, not material tags) omitted (§12ap-6). **Mass unit:** the source's literal `mass 1 1.00E+002` is already in N·s²/mm (= 1 tonne) — do NOT multiply by `tonne` (double-converts, making mass 1000× too large → T 1000× too long); the raw number 100 is used directly (§12al/§12b mass-unit rule). **Layout:** pure-eigen model omits only §11 Loading (it has real nodes/elements/BCs/ODB); §12 hosts `ops.eigen()` + `save_eigen_data` (§12ar precedent, mildest adaptation yet). **No-reference validation:** with no reference file in `tcl_ref/`, validate against the closed-form uniform N-DOF shear-building frequency `ω_j = 2√(k/m)·sin((2j−1)π/(4N+2))`. **Eigen solver:** default subspace (ARPACK) — uniform stiffness + full-rank mass, so neither §12h-2 (stiffness contrast) nor §12al (rank-deficient mass) applies. **Path depth:** standards/ is `parents[3]` (this model nests under `models/Dino/<analysis-name>/`), with a `parents[2]` fallback. Run with: `C:/Users/micha/miniconda3/envs/opensy/python.exe "models/Dino/Modeling of a simplified lateral multi-degree-of-freedom model/model.py"`
