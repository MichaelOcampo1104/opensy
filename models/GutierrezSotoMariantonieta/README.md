# GutierrezSotoMariantonieta

**Purpose:** 3D non-linear dynamic analysis of a 6-story self-centering
post-tensioned steel braced frame with controlled-rocking bays and
replaceable fuse assemblies, subjected to scaled Kobe ground motion.

**Building System:** 6-story steel special braced frame, 5 bays × 4 column
lines in plan (bay widths 6 m × 6 m, story height 4 m). Two of the column
lines are rocking bays: post-tensioned (PT) strands anchor the frame to the
foundation and a SelfCentering gap + Steel01 fuse provide energy dissipation
and re-centering. The remaining bays are a conventional steel braced frame.
Floor nodal mass 24,000 kg.

**Model Description:** 3D (ndm=3, ndf=6) OpenSeesPy model with 282 nodes and
650 elements: 610 `elasticBeamColumn` (columns, beams, braces, struts),
8 `truss` (PT strands), 16 `twoNodeLink` (base vertical-reaction springs),
16 `zeroLength` (fuse pin connections). Two `PDelta` geometric transforms.
Materials: `ElasticPP` + `Parallel` PT strands (201–203), `ENT` base
connection (301), `SelfCentering` + `Steel01` fuses (401, 414). Nodal mass
24 tonne/floor-node, translational only. 5% Rayleigh damping on modes 1 & 3
(current-K beta). Single-step elastic gravity (LoadControl + Linear),
then 2500-step Newmark transient (dt=0.01) under scaled Kobe Y-direction
UniformExcitation (factor 0.69·g, dt=0.02).

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (elastic beam-column + PT strands + SelfCentering fuses) |
| Lateral System | Self-centering steel braced frame with controlled rocking |
| Lateral Loading | Dynamic — Kobe ground motion (UniformExcitation, Y-dir) |
| Earthquake Records | kobe.txt — 1250 pts @ dt=0.02 s, scaled ×0.69·g |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy |
| Units | N, mm, MPa (converted from source SI per AGENT.md §12j) |

**Running:**

```bash
conda activate opensy
python model.py
```

Outputs land in `output/`.

**⚠️ Assumed parameters (replace with source data):**

The source (`tcl_ref/01..13-*.py`) is the body of an STKO parameter-sweep
script; the driver file that defined several parameters was not provided.
The following values are **representative AISC placeholders**, clearly marked
in `model.py §3 ASSUMED PARAMETERS`. They produce a runnable model but its
stiffness/strength will not match the original paper exactly:

| Parameter | Placeholder | Basis |
|-----------|-------------|-------|
| `Section_Mat` VS1–VS6 (columns) | W14×120 base, W14×80 upper | AISC SMF column sizing |
| `Section_Mat` VS7–VS9 (X-beams) | W24×55 | AISC SMF beam |
| `Section_Mat` VS10–VS12 (Y-braces) | W12×40 | AISC brace |
| `Strand_Area` | 2000 mm² (~12 #15 strands) | Typical controlled-rocking PT |
| `Fuse_Yield` | 250 kN | Mid-range replaceable fuse |

To use the source's exact values, edit the `SECTION` dict and the
`STRAND_AREA` / `FUSE_YIELD` constants in `model.py §3` and re-run
`_extract.py` (or just edit `model_data.json` directly).

**References:**
Gutierrez-Soto, M. et al. — DREAM Structures Lab
([sotostructures.com/research/publications](https://sotostructures.com/research/publications/)).
Related work on controlled-rocking steel braced frames in the 17WCEE
proceedings (e.g. "Seismic Design Optimization of Controlled Rocking Steel
Braced Frames based on Neural Dynamic Model").

**Notes:**
Converted from `tcl_ref/01..13-*.py` (a 13-file STKO build sequence). The
mesh (282 nodes, 650 elements), all fixities, masses, and gravity loads are
extracted from the source into `model_data.json` (a throwaway parser was used
to guarantee 1:1 transcription; that parser is not committed). Units
converted SI → N-mm-MPa per AGENT.md §12j (stress ÷1e6, mass ÷1000; never
using `* Pa` or `* kg` which are misnamed in `units.py`). All text recorders
migrated to `opst.post.CreateODB` (§3d); key nodes/elements tracked per the
original recorder list (roof 604, fuses 2011/2051, strands 6011/6051,
columns, beams). Per AGENT.md §12i, the UniformExcitation is defined AFTER
gravity so `loadConst` doesn't freeze it. The source's outer sweep counters
(`n`, `ni`, `Analysis_number`) are dropped — only one config runs.
