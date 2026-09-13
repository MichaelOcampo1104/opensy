# P103_MovablePlatform

**Purpose:** Independent OpenSeesPy counter-check of the STAAD 3D movable-platform model under COMB 301 (1.0 DL + cantilever LL): verify support reactions and the no-uplift verdict.

**Building System:** Movable steel platform on wheels/casters: two transverse frames (Frame A Z=0, Frame B Z=0.7 m) of SHS 100x100x12.0 tied by Z-runners, with a 0.65 m cantilever platform (Z=0.7-1.35 m) on rails plus diagonal braces; 100x50x18.7 RHS outrigger (members 7/17). Pinned wheel supports at 6 joints.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6), 16 nodes (STAAD joint numbers), 23 elasticBeamColumn members (STAAD member numbers) with per-orientation Linear transformations. COMB 301 UDLs (self-weight from AX x density, grating 0.15, angle 0.03, cantilever LL 0.81 N/mm) applied via beamUniform after explicit global-to-local transformation. Load-controlled gravity (AGENT.md 3c exception). Result: line A 1203 N, line B 7515 N vs STAAD 1210/7510 N and Python beam 1203/7515 N; equilibrium residuals 0; no uplift - PASS.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (elastic, E=200000 MPa) |
| Lateral System | NA (gravity-only stability check) |
| Lateral Loading | NA (static gravity COMB 301 only) |
| Earthquake Records | NA |
| Design Year | 2026 (temporary works platform) |
| File Format | .py |
| OpenSees Version | openseespy (venv) + opstool 1.0.26 |
| Units | N, mm, MPa |

**References:**
mm report: StructChecks/Framig-overturning-check/outputs/Overturning_Stability_Check.docx (FoS 1.72 PASS); STAAD 3D_Movable_bcad-model.std (FINAL 12:41 run)

**Suggested Citation:**
NA

**Notes:** Lessons applied: 12c (tags/properties diffed vs .std), 12j (no Pa/kg), 12r (explicit Linear TS), 12n (ODB ingredients), 3c (manual LoadControl loop). New findings: beamUniform is element-LOCAL (probe-verified); ops.reactions() mandatory before nodeReaction.
