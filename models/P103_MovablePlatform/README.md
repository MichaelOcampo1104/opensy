# P103_MovablePlatform

**Purpose:** Independent OpenSeesPy counter-check of the STAAD 3D movable-platform model. Two load cases are covered:

| Case | Combination | Scope | Verdict (2026-09-13) |
|------|-------------|-------|----------------------|
| COMB 301 | 1.0 DL + cantilever LL | reactions + no-uplift | **PASS** (reactions 0.001%) |
| COMB 202 | 1.4 DL + 1.6 LL | reactions + no-uplift | **PASS** (reactions 0.000%) |
| COMB 202 | (as above) | member end forces | **FAIL** — 3% tolerance not met, cause open (see Findings) |

**Building System:** Movable steel platform on wheels/casters: two transverse frames (Frame A Z=0, Frame B Z=0.7 m) of SHS 100x100x12.0 tied by Z-runners, with a 0.65 m cantilever platform (Z=0.7-1.35 m) on rails plus diagonal braces; 100x50x18.7 RHS outrigger (members 7/17). Pinned wheel supports at 6 joints.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6), 16 nodes (STAAD joint numbers), 23 elasticBeamColumn members (STAAD member numbers) with per-orientation Linear transformations.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (elastic, E=200000 MPa) |
| Lateral System | NA (gravity-only static checks) |
| Lateral Loading | NA |
| Earthquake Records | NA |
| Design Year | 2026 (temporary works platform) |
| File Format | .py |
| OpenSees Version | openseespy (venv) + opstool 1.0.26 |
| Units | N, mm, MPa |

## Files

| File | Role |
|------|------|
| `model.py` | COMB 301 counter-check. **Unchanged and byte-identical** — the existing verified artifact. |
| `model_comb202.py` | COMB 202 counter-check (reactions + member end forces). Imports geometry/sections/BCs from `model.py`; adds no geometry of its own. |
| `model_sens.py` | Section sensitivity / stability-constrained design sweep over standard BS EN 10219 hollow sections + counterweight. Reports FoS, reactions, deflection and mass per set. |
| `member_force_report.py` | Closed-form internal force diagrams (axial/shear/torsion/moment) + tabulation, as interactive HTML and CSV. |
| `staad_comb202_reactions.csv` | STAAD COMB 202 support reactions, converted to N / N·mm. |
| `staad_comb202_member_forces.csv` | STAAD COMB 202 global member end forces, 23 members x 2 ends x 6 components, N / N·mm. |
| `staad_comb301_*.csv` | The same reference sets for COMB 301 (used as a regression self-test). |

Run: `python model_comb202.py 202` (default) or `python model_comb202.py 301`.
Outputs go to `output/comb202/` and `output/comb301/` respectively, so neither clashes with `model.py`'s `output/`.

## Section sensitivity (2026-09-13)

`model_sens.py` sweeps standard BS EN 10219 section sets + a rear counterweight.
Section properties were read from the STAAD British catalogue database
(`ProgramData/Bentley/catalogdata/…/Sections.db3`, `BS-SHS` / `BS-RHS`).

| Set | SHS / RHS | Ballast | Mass | FoS |
|---|---|---|---|---|
| baseline (as modelled) | 100×100×12.0 / 100×50×18.7 | — | 678 kg | 1.723 |
| std_max | 100×100×10 / 100×50×8 | 17 kg | 526 kg | 1.500 |
| mid | 100×100×6.3 / 100×50×6.3 | 49 kg | 399 kg | 1.500 |
| light | 80×80×4 / 100×50×4 | 84 kg | **274 kg** | 1.500 |

**The members are stability-governed, not strength-governed.** Strength
utilisation peaks at 6.2%; what binds is the overturning FoS, because the
members do ballast duty on the restoring side. A strength-only optimisation
(STAAD `SELECT`) drives every member to a 20×20×2 tube and the platform tips
(FoS 0.321). Counterweight at the best lever is far more weight-efficient than
member thickness, so light members + ballast win — **60% mass saving**.

The as-modelled sections are **non-standard** (SHS 100×100×12 exceeds the
catalogue max of 10.0; RHS 100×50×18.7 is ~2× the 8.0 max), and STAAD refuses to
design them at all — `PRIS` properties return *"DESIGN NOT PERFORMED WITH
PRISMATIC PROPERTIES"*.

## Findings (2026-09-13)

### STAAD OpenSTAAD output units are misreported — **force is kip, moment is kip-in**

The live model is `UNIT METER KN`, and `GetOutputUnitForForce()` returns `"kN"` / `GetOutputUnitForMoment()` returns `"kN-m"`. **Those strings are wrong for this build.** The values actually returned are kip and kip-in (displacement is correctly reported as inches). Proven two ways:

1. A hand-computed LOAD 1 total from the `.std` (self-weight + member UDLs) is 7.2603 kN; STAAD's summed reactions are 1.6321 → ratio **4.4484** = kN per kip, exact. Same ratio for LOAD 2 and LOAD 3.
2. Member 1 (vertical, L = 34.6063 in) end-B MZ = 1.0613184 and V_A x L = 0.0306684 kip x 34.6063 in = 1.06132 kip-in. Exact.

Conversion used throughout: `1 kip = 4448.2216152605 N`, `1 kip-in = 112984.8290276168 N.mm`, `1 in = 25.4 mm`.

### STAAD member end forces: sign convention

`GetMemberEndForces(m, end, lc, localOrGlobal=1)` returns, in GLOBAL components, the force **applied to the member** at that end. At a support node it equals the joint reaction exactly (checked on members 1 and 7, all six components). OpenSees `eleForce()` uses the same sign here (detected at run time and asserted at all six support nodes, not assumed).

### Shear deformation — STAAD includes it, this model does not

The OpenSees model uses `elasticBeamColumn` (Euler-Bernoulli), which ignores shear deformation. STAAD.Pro includes it. Consequence: nodal UY/UZ are 5–7% stiffer here than STAAD. Switching to `ElasticTimoshenkoBeam` moves them to within ~2% of STAAD, sweeping through zero at a physical shear-area factor `A_s ~ 0.6–1.0 A`.

This is a modelling-convention difference, not an error. It is the likely reason the **member-force** check does not meet the 3% tolerance. Note the claim is deliberately narrow: matching the shear physics *closes the displacement gap* but makes member forces agree **less** well, so shear alone does **not** explain the force residual. Ruled out as a cause: Iy/Iz assignment on the RHS outriggers (swapping makes agreement worse).

### Member-force residual is open

The residual concentrates in **secondary out-of-plane actions** (MY/MZ) while primary actions and all reactions hold. Both models satisfy global equilibrium to machine precision, and the applied UDL recovered from each model's own end forces matches STAAD **exactly for all 23 members** (ratio 1.0000), so neither model is in equilibrium error. Treat the member-force check as an **open item**; do not read the reactions PASS as validating member forces.

## References

- STAAD source: `mm/raw/python-scripts/_verification/staad/P103_Movable_Platform/3D/3D_Movable_bcad-model.std`
- mm report: `StructChecks/Framig-overturning-check/outputs/Overturning_Stability_Check.docx` (FoS 1.72 PASS)
- COMB 301 verdict file: `output/reaction_summary.json`

**Suggested Citation:** NA

**Notes:** Lessons applied: 12c (tags/properties diffed vs .std), 12j (no Pa/kg), 12r (explicit Linear TS), 12n (ODB ingredients), 3c (manual LoadControl loop). Findings banked: `beamUniform` is element-LOCAL (probe-verified); `ops.reactions()` mandatory before `nodeReaction`; **STAAD OpenSTAAD force/moment output units are kip/kip-in on this build despite reporting kN/kN-m**; STAAD PRIS analysis includes shear deformation; `ElasticTimoshenkoBeam` (not `...Beam3d`) is the OpenSeesPy element name, and its argument order is `E G A J Iz Iy Avy Avz` (**Iz before Iy**).
