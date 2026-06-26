# misty_effective stress site resp

**Purpose:** 1D effective-stress site response analysis of a layered soil profile on a 2% slope using 9-node coupled u-p (`9_4_QuadUP`) elements with `PressureDependMultiYield02` and a Lysmer dashpot base.

**Building System:** 30 m soil column (3 layers: 20 m dense sand, 8 m medium sand, 2 m loose sand) on an elastic half-space (Vs = 700 m/s). Water table at 2 m depth. 2% slope with periodic lateral boundaries.

**Model Description:** 2D finite-element model with 60 `9_4_QuadUP` (NineFourNodeQuadUP) elements in a single-column mesh. Each element has 9 nodes: 4 corners (ndf=3: UX, UY, pore-pressure) + 4 edge-mids + 1 center (ndf=2: UX, UY). Three `PressureDependMultiYield02` materials with calibrated liquefaction parameters. Lysmer dashpot at the base (Viscous material, C = 1750 kN·s/m). Rayleigh damping 2% on modes at 0.2 and 20 Hz. Three-phase analysis: (1) elastic gravity (10 steps, dt=500 s), (2) plastic gravity (40 steps, dt=500 s), (3) dynamic analysis with SmartAnalyze Transient (7990 steps, dt=0.005 s, Newmark 0.5/0.25). Synthetic Ricker wavelet base excitation (peak 0.15 m/s at 1.5 Hz). Post-shake consolidation with 20% damping and `PostShake=1` activated.

| Field | Value |
|-------|-------|
| Dimensions | 2D |
| Material | PressureDependMultiYield02 (3 layers) |
| Lateral System | 1D soil column with periodic boundaries |
| Lateral Loading | Dynamic base excitation (velocity input via Lysmer dashpot) |
| Earthquake Records | Synthetic Ricker wavelet (dt=0.005s, 7990 pts, peak=0.15 m/s) |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy |
| Units | kN, m, kPa, sec (coupled u-p — retained per XMU_Ch8 precedent) |

**References:**
Mistry, H. — *Effective Stress Site Response_rev.ipynb*, University of Manchester. After McGann, C., Shin, H., Arduino, P., Mackenzie-Helnwein, P. — University of Washington.

**Suggested Citation:**
McGann, C., Shin, H., Arduino, P., Mackenzie-Helnwein, P. — University of Washington.

**Notes:**
Converted from `ref/Effective Stress Site Response_rev.ipynb`. This is the **9-node `9_4_QuadUP`** variant of the free-field effective-stress site response model — distinct from the sibling `pedroArduino_freefield` (4-node `quadUP`/`SSPquadUP`). Key differences from pedroArduino: 9-node element topology (4 corner pore-pressure nodes + 5 bubble nodes), 2.0 m horizontal element size (vs 0.5 m), permeability 1.0e-4 m/s (vs 1.0e-8), 2% slope (vs 1%), and CFL vsMax = 250 m/s (vs 500).

Retains source units (kN, m, kPa, sec) as is standard for coupled u-p models — converting to N-mm would make fluid properties (density, permeability) extremely small and risk numerical conditioning (see XMU_Chapter8.1 catalogue entry). The mesh was rewritten using a clean coordinate-grid layout (corner nodes ndf=3, edge-mid/center nodes ndf=2) faithful to the notebook's intent rather than its exact interleaved node-tag arithmetic. Stress diagnostics read Gauss-point `Stresses` (not `StressesAtNodes` — see §12ad). Run with: `conda activate opensy && python model.py`, then `python post_process.py` for stress contours.

**Verified-working analysis (3 phases):** gravity (elastic 100×500s + plastic 100×1s), dynamic (7990 steps @ dt=0.005s), and a bounded post-shake consolidation. Two OpenSeesPy-specific fixes were required beyond the notebook (see AGENT.md §12ae): (1) the base **edge-mid (bubble) nodes** must share the base UY fixity (`fix(n_bot, 0, 1)`) — the notebook's `ops.fix(2, 0, 1)` — or the 9-node edge bows downward and the elastic→plastic PDMY02 transition diverges (Norm R ~6.6e5); (2) plastic gravity needs **KrylovNewton + dt=1.0** (Newton cycles at Norm~0.005 near the yield surface). Post-shake (PostShake=1) **diverges at dt≥0.01** (Norm R → ~1e11 → NaN) and only dt=0.005 is stable, so a full 100 s consolidation is ~16000 steps; the model therefore runs a bounded post-shake (6 batches × 50 steps) and saves the dynamic response to the ODB *before* post-shake so the verified dynamic results survive regardless of post-shake outcome.

**Known limitation (shared with pedroArduino_freefield):** opstool's ODB does not capture the `9_4_QuadUP` pore-pressure DOF into the nodal `pressure` field (reads all-zeros) — the effective-stress physics is instead verified through the σ₂₂ contour (−429 kPa at base → −4.5 kPa at surface, correct vertical effective-stress gradient) and the σ₁₂ shear-stress contour. Excess PWP time histories are available via `ops.recorder('Node', ..., '-dof', 3, 'vel')` if needed.
