# VividConcrete

**Purpose:** 3D nonlinear seismic time-history analysis of a circular RC bridge column modelled with a fiber-section `forceBeamColumn` (6 Gauss-Lobatto integration points, each with its own confined/unconfined concrete + rebar section) and a `zeroLengthSection` bar-slip end spring (Bond_SP01).

**Building System:** Single circular RC bridge column (column C1 design), 3D. Height 288 in (7.32 m), diameter 48 in (1.22 m). Longitudinal reinforcement: 18 #11 bars (Asl = 1.56 in², fyl = 75.2 ksi). Transverse reinforcement: #5 ties at 6 in (Ast = 0.62 in², fyt = 54.8 ksi). Concrete: fc = 6.1 ksi (42 MPa), Ec = 3320 ksi. Axial gravity load P = 522 kip (2321 kN). Based on the Kuanshi Zhong (Stanford, 2017) fiber + bar-slip modeling framework.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6) with 3 nodes, 1 `forceBeamColumn` (nodes 2→3) using `UserDefined` Gauss-Lobatto integration (6 IPs, per-IP Aggregator-wrapped fiber sections: cover Concrete02 + Mander-confined core Concrete02 + 18 ReinforcingSteel rebar fibers + Hysteretic shear Vy/Vz), and 1 `zeroLengthSection` bar-slip spring (nodes 1→2, Bond_SP01 + confined/unconfined Concrete02 + shear). ~26 materials total. Analysis: gravity (10 LoadControl steps) → Rayleigh damping (ζ=0.03 on modes 1 & 3) → seismic time-history under a horizontal UniformExcitation. Mander-confined concrete properties (fcc, ecc, flp, ke, rouS) and the Hysteretic shear backbone derived via the source's exact expression chain. Ground motion applied AFTER loadConst (§12i). Dynamic phase via `opst.anlys.SmartAnalyze` (Transient) with the §12z fiber-softening recipe.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | RC (fiber-section: Concrete02 + ReinforcingSteel + Bond_SP01) |
| Lateral System | Cantilever column with bar-slip base spring |
| Lateral Loading | Seismic time-history (ground motion) |
| Earthquake Records | Northridge 1994 (NR94cnp.txt, validation substitute) |
| Design Year | 2017 |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy |
| Units | N, mm, MPa |

**References:**
Zhong, K. (2017). Fiber-section + bar-slip column modeling framework. Stanford University. Source Tcl: `tcl_ref/` (CreateModel, DesignPropertyC1, GetGaussLobattoIP, SolverNewmark, SquenceTestNew).

**Suggested Citation:**
Zhong, K. (2017). VividConcrete — fiber-section + bar-slip RC column dynamic analysis. Stanford University.

**Notes:**
Converted from 5 Tcl files (570 lines total). Source is imperial (in, kip, ksi); converted to N-mm-MPa via standards/units.py.

**GM SUBSTITUTION:** The source runs 6 sequential ground motions (Loma Prieta ×5 + Kobe, `./TableInput/EQ1GM.txt` … `EQ6GM.txt`) which are NOT in the repo. For end-to-end validation the Northridge-1994 record `NR94cnp.txt` (dt=0.01s, ~2490 pts, g-units, reused from models/elkady2019) is used. `run_dynamic()` is generic — the real GMs drop in by changing `GM_FILE` / `GM_DT` / `GM_NPTS`.

**SOLVER NOTE:** Source uses SparseGEN (not compiled into this OpenSeesPy build); BandGeneral substituted (§12af). Source eigen uses `-fullGenLapack`; retained here because the column's mass matrix is rank-2 (only node-3 UX + RY carry mass), which defeats the ARPACK subspace solver ("Could not build an Arnoldi factorization").

**Validation (v1.35.0):** Gravity reaches lf=1.00; T1=0.849s (physically sound for a 7.3 m RC column under 522 kip axial); dynamic analysis converges all 2490 steps (24.9s of Northridge) with realistic roof-displacement oscillation (−31 to +15 mm). All 6 vis HTMLs render.

Run with: `conda activate opensy && python models/VividConcrete/model.py`
