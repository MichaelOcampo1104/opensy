# Dino_Truss_Bridge_Ex01

**Purpose:** Linear-elastic static analysis of a 3D truss bridge (24 m span, two chords 3 m apart) under four 100 kN vertical loads on the top chord, applied in 100 load steps.

**Building System:** Truss bridge with a 24 m span and two chords 3 m apart in Y. The bottom chord is at z = 0 and the top chord at z = 4.5 m. The chord members (along X, top and bottom) have A = 21,200 mm^2, and all other members (verticals, diagonals, transverse and lateral bracing) have A = 13,050 mm^2. The bottom-chord end nodes 1, 2, 9 and 10 are fixed in all three translations.

**Model Description:** 3D OpenSeesPy model (ndm = 3, ndf = 3) with 18 nodes and 46 truss elements (`truss`, uniaxial Elastic steel, E = 199,900 MPa), verbatim from `ref/Exam01.tcl`. Four vertical loads of 100 kN (-Z) act on nodes 13 to 16. The analysis follows the source: Linear time series, LoadControl with increment 0.01 (100 steps), Newton, EnergyIncr 1e-6 tests and BandGeneral. It runs as a manual loop under the AGENT.md §3c LoadControl exception, because SmartAnalyze would replace LoadControl with DisplacementControl. Node displacements and axial forces are recorded at every step, mirroring the source recorders `node0.out`, `node5.out` and `ele0.out`.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Elastic steel (E = 199,900 MPa) |
| Lateral System | Top and bottom lateral bracing (truss members) |
| Lateral Loading | Vertical: 4 x 100 kN on the top chord (LoadControl, 100 steps) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | OpenSeesPy >= 3.0 |
| Units | N, mm, MPa |

**References:**
Dino Chen's OpenSees tutorial, Example 01 (Static Analysis of a Truss Bridge Structure): [http://www.dinochen.com/article.asp?id=150](http://www.dinochen.com/article.asp?id=150). Source: `ref/Exam01.tcl`, with the ETABS model in `ref/EXAM01.s2k`, `ref/EXAM01.EDB` and `ref/EXAM01.ebk`.

**Suggested Citation:**
Chen, X. W. Dino Chen's OpenSees tutorial, Example 01. http://www.dinochen.com/article.asp?id=150.

**Verification:**
- node5.out (node 5, UX UY UZ, 100 steps): max error 0.000302% of max |value| (max |value| 1.65 mm).
- ele0.out (axial forces, elements 1-46): max error 0.000246% of max |value|.
- node0.out (nodes 1-18): max error 5.8841% of max |value| as recorded. Almost all of it is one common UY translation of the top-chord nodes 11-18. At the final step the offset is +0.097292 mm (model minus source), and the eight nodes agree with that offset to within 6e-7 mm at every step. With the translation removed, the max error is 0.000302% of max |value|.

**Notes:**
Converted from `ref/Exam01.tcl`. Node coordinates, members, areas, supports and loads match the source. Materials 2 and 3 are defined in the source, but no element uses them, so they are omitted.

**Known discrepancy: the top-chord UY is free up to a common translation (not a model error).** The free stiffness matrix is singular to round-off: its smallest eigenvalue is -1.7e-10 N/mm, against 3.5e6 N/mm for the largest. The null vector is UY = 1/sqrt(8) at each of nodes 11-18 and zero elsewhere. Only members 1-4 and 27-29 carry Y motion between top-chord nodes, and together they link the eight nodes into a single tree, so a common UY translation of the top chord strains no member. Every member that joins the top chord to the bottom chord lies in the plane y = 0 or y = 3 m, so none links the top chord to the rest of the structure in Y. The vertical loads do no work on this translation, so equilibrium does not fix it. The solver's value along this direction is set by round-off, and the source (OpenSees Tcl) and this model settle on different values: at step 100, node 11 has UY 0.00656 mm in the source and 0.10385 mm here. Both solutions satisfy equilibrium. The source's displacements reproduce its element forces to 0.00067%, and this model's reproduce its forces to 2.9e-11 N.

The model keeps the source's supports and loads, so the translation is not fixed in the model. Fixing UY at one top-chord node would give a unique solution, but it would change the source model, so it is not done here.

**Reference files:** `ref/Exam01.tcl`, `ref/node0.out`, `ref/node5.out`, `ref/ele0.out`, `ref/EXAM01.s2k`, `ref/EXAM01.EDB`, `ref/EXAM01.ebk`, `ref/EXAM01.U`.
