# Dino_PlasticHinge

**Purpose:** Compare two fibre-section plasticity formulations of the same 3D RC moment frame under a displacement-controlled lateral pushover — concentrated plasticity (`beamWithHinges`) vs distributed plasticity (`nonlinearBeamColumn`) — validating each against the original Tcl reference.

**Building System:** 3D RC moment frame, 2 bays × 2 bays in plan (6 m bays) and 4 stories (3 m story height), 30 nodes. HC500×500 columns (sec 1) and HB300×600 beams (sec 2), each a hand-meshed fibre section of Concrete02 concrete core/cover + Steel01 corner rebar. Six base nodes fully fixed. No gravity — lateral load only.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6), 30 nodes, 52 beam elements. Two element formulations of the *same* frame are built in a single `model.py` and pushed over against the *same* reference curve so the two plasticity models are directly comparable:

- **`beamWithHinges`** (concentrated plasticity) — 500 mm end hinges (columns) / 600 mm (beams) on a fibre section, elastic interior with gross-section `E A Iz Iy G J`.
- **`nonlinearBeamColumn`** (distributed plasticity) — flexibility-based, 3 integration points, full fibre section along the length.

Lateral load is an inverted triangle on UX (4e5/4e5/3e5/3e5/2e5/2e5/1e5/1e5 N at nodes 2,4,1,3,13,14,19,20; ΣP = 2.2 MN). Pushover is DisplacementControl on node 2, DOF 1, 1 mm/step × 100 steps via SmartAnalyze (NormDispIncr, KrylovNewton + 5-algorithm fallback, relaxation=0.5) with per-increment `static_split` cadence for 1:1 alignment with the 100-row reference. Base shear = load factor λ × ΣP. Source Tcl already N-mm-MPa.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC (Concrete02 fc=20 MPa + Steel01 fy=300 MPa, fibre section) |
| Lateral System | Moment frame (52 beams, concentrated vs distributed plasticity) |
| Lateral Loading | Displacement-controlled pushover (100 mm, 100 steps) |
| Earthquake Records | NA (static pushover) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy (opensy conda env, Python 3.12.12, opstool 1.0.26) |
| Units | N, mm, MPa |

**References:**
Original source: `tcl_ref/co.tcl` (308-line Tcl `beamWithHinges` model) and `tcl_ref/co2.tcl` (308-line Tcl `nonlinearBeamColumn` model — identical except the element block). Reference results: `tcl_ref/node2.out` (100-row pushover recorder, col 0 = load factor λ, col 1 = node-2 UX, col 2 = UY, col 3 = UZ). `tcl_ref/result.xlsx` (curated curves).

**Suggested Citation:** NA

**Notes:** Converted from `co.tcl` + `co2.tcl`.

**Why two variants in one file** — the example's whole point is to contrast the two plasticity formulations; the TCL pair share everything (nodes, materials, sections, loads, analysis) except the `element` line, so a single `model.py` with an element-type switch is the faithful standardization.

**3D `beamWithHinges` signature (§12ay):** the Tcl passes *six* elastic-interior values between the right hinge length and the transform tag — `E A Iz Iy G J`. The OpenSeesPy wrapper accepts the same six (the 2D form used by Citiner takes only `E A Iz`). Passing the 5- or 4-property form errors; the full 6-property form is required for ndm=3.

**3D fibre section requires `-GJ` (§12au):** the source Tcl omits `-GJ` from the `section Fiber` and OpenSees only warns; OpenSeesPy *errors*. `-GJ` is added (matching the elastic-interior torsion) so the section is consistent.

**`ops.fix` unpack quirk (§12ay):** this openseespy build errors on the literal form `ops.fix(tag, 1,1,1,1,1,1)` ("invalid # of constraint values") while accepting the unpack form `ops.fix(tag, *[1,1,1,1,1,1])` — a pure arg-counting quirk of the wrapper. The unpack form is used throughout.

**ODB scoping:** `save_frame_resp=False` for both variants — `beamWithHinges` internal sections are accessed by auto-index not user tag (§12v-1), and `nonlinearBeamColumn` internal sections likewise lack user-visible tags (§12ap). Nodal responses still track for the deformed-shape visualisations.

**Dead material:** source `uniaxialMaterial Elastic 3` (E=1.999e5) is never bound to any section/element — omitted per §12ap-6.

**VERIFICATION:**
- `nonlinearBeamColumn`: 100/100 steps, **0.00% diff** on both node-2 UZ and base shear (RMS 0.00000 mm) — this is the TCL that *generated* `node2.out`, so the exact match confirms a faithful conversion.
- `beamWithHinges`: 100/100 steps, 7.70% UZ / 1.05% base-shear diff — the physically-expected gap between concentrated (slightly more flexible, UZ 4.25 vs 3.94 mm) and distributed plasticity.

Outputs: 3 pushover CSVs (ref + hinge + fiber), `pushover_compare.png` (capacity curve + UZ-vs-step), 4 shared model/load HTMLs, 7 per-variant deformed-shape HTMLs (slider + animation + peak).

**Run with:**
```
C:/Users/micha/miniconda3/envs/opensy/python.exe "models/Dino/Elastic-Plastic Analysis of Plastic Hinge Fiber Element/model.py"
```
