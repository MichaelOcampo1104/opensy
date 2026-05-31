# nafeh2022 — 5-Storey Infilled RC Frame (Archetype 1, GLD)

**UniqueID:** nafeh2022
**Source:** Port of `arch_1_5st.tcl` from [Infilled-RC-Building-Database](https://github.com/gerardjoreilly/Infilled-RC-Building-Database)
**Author:** Al Mouayed Bellah Nafeh (IUSS Pavia, 2020)
**Units:** N · mm · MPa · tonne · s

## Description

3D nonlinear model of a 5-storey, 8×4-bay RC moment-resisting frame designed for gravity loads only (GLD), representative of Italian pre-1970s construction. Masonry infill walls are modelled as equivalent diagonal struts with Pinching4 material. Joint shear behaviour captured via zero-length rotational springs.

## Model Components

| Component | Description |
|-----------|-------------|
| **Columns** | 300×300mm (stories 1–2), 200×200mm (stories 3–5) |
| **Beams** | 500×300mm throughout |
| **Joints** | Zero-length rotational springs (Hysteretic material) |
| **Infill** | Single diagonal struts (Pinching4), weak/medium sets |
| **Diaphragm** | Rigid per floor (column 4/row 3 master) |

## Analysis

- **Gravity:** Manual LoadControl loop (100 steps)
- **Eigen:** 5 modes (fullGenLapack via ops.eigen)

## Files

| File | Purpose |
|------|---------|
| `model.py` | Main model script (§0–15 canonical layout) |
| `infill.py` | Masonry infill strut model (port of Tcl `infill` procedure) |
| `joint_model.py` | Beam-column joint model (port of Tcl `jointModel`) |
| `rc_bc_non_duct.py` | Force-based beam-column with lumped plasticity hinges |
| `tcl_reference/` | Original Tcl source files for reference |
| `output/` | HDF5 data and HTML visualisations |

## Usage

```bash
cd models/nafeh2022
python model.py
```

## References

- Nafeh, A. M. B. (2020). Infilled-RC-Building-Database. IUSS Pavia.
- O'Reilly, G. J., Sullivan, T. J. (2019) *J. Earthquake Eng.*, 23(8), 1262–1296.
- Hak et al. (2012).
- Sassun et al. (2015).
- Stafford-Smith, B., Carter, C. (1969). *Proc. ICE*, 43(1), 31–45.
