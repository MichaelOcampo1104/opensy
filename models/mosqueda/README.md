# mosqueda

**Purpose:** Transient dynamic analysis of a 3D SDOF building with a Tuned Mass Damper (TMD) using a TripleFrictionPendulum isolator under multi-support sine excitation.

**Building System:** 3D single-degree-of-freedom building (SDOF) with elastic X/Y/Z springs representing lateral and vertical stiffness. A TMD attached via a TripleFrictionPendulum (FPSB) bearing provides vibration control through friction pendulum mechanics. Based on the NEEShybrid/mosqueda specimen by Andreas Schellenberg.

**Model Description:** 3D finite element model (ndm=3, ndf=6) with 3 nodes: fixed base, building mass (SDOF), and TMD mass. Building modeled via twoNodeLink element with elastic stiffness (kx=114 kN/mm, ky=178 kN/mm, kz=863 kN/mm). TMD isolator uses TripleFrictionPendulum element with 3 Coulomb friction models (mu=0.055, 0.13, 0.13) and pendulum radii L1=55mm, L2=L3=436mm. Rayleigh damping 5% applied to initial stiffness. Gravity: building (2002 kN) + TMD (249 kN). Multi-support sine excitation (0.5 Hz, 38 mm amplitude, 30s duration). Eigenvalue analysis (fullGenLapack). Transient: SmartAnalyze Transient with Newmark integration, 8192 steps at dt=0.00488s.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Elastic (building) + TripleFrictionPendulum (TMD) |
| Lateral System | SDOF with TMD isolation |
| Lateral Loading | Dynamic multi-support sine excitation (X-direction) |
| Earthquake Records | Sine wave (0.5 Hz, synthetic) |
| Design Year | NA (laboratory specimen) |
| File Format | .py |
| OpenSees Version | Standard OpenSeesPy |
| Units | N, mm, MPa |

**References:**
Schellenberg, A. — NEEShybrid / mosqueda specimen. Building1DOFwithTMD.tcl from the OpenFresco hybrid simulation framework.

**Notes:**
Converted from tcl_ref/Building1DOFwithTMD.tcl (Andreas Schellenberg). All imperial units (kip, in) converted to N, mm, MPa. OpenFresco experimental elements (expElement generic, expControl, expSetup, expSite) removed because expElmFact=0 — pure numerical mode. Multi-support sine excitation replaces the original Loma Prieta .acc/.vel/.dsp files (not present in repository). Gravity defined before loadConst; ground motion defined after per AGENT.md §12z-1. SmartAnalyze Transient with Newmark (0.5,0.25) replaces AlphaOSGeneralized + Linear algorithm. ODB response collection throttled every 5th step. Fundamental period with TMD: T1=0.269s (3.71 Hz).
