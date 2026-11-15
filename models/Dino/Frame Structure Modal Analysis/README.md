# Dino_Frame_Modal_Ex05

**Purpose:** Modal analysis of the Example 04 four-storey 3D frame (two bays in X, one bay in Y) with elastic sections: 12 eigenvalues, periods, and mode shapes.

**Building System:** Four-storey 3D frame, plan 9.0 m x 5.0 m (bays 4.5 m in X and 5.0 m in Y). Floors at 4.5, 7.5, 10.5, and 13.5 m, with the base fixed at z = 0.

**Model Description:** 3D OpenSeesPy model (ndm=3, ndf=6) with 28 nodes and 47 elasticBeamColumn elements in four property sets (A, E, G, J, Iy, Iz verbatim from `ref/co.tcl`). Lumped translational masses (8.604 and 4.302, in N s^2/mm) sit on 22 nodes. The model runs `eigen 12`, saves each mode shape to the ODB, and writes the eigenvalues to `Periods.txt`. There are no load patterns, because the analysis is a pure modal analysis.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Elastic (E = 26,800 MPa, G = 11,170 MPa in the elements) |
| Lateral System | Moment frame |
| Lateral Loading | None (modal analysis) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | OpenSeesPy >= 3.0 |
| Units | N, mm, MPa, tonne (N s^2/mm) |

**References:**
Dino Chen's OpenSees tutorial, Example 05 (Frame Structure Modal Analysis): [http://www.dinochen.com/article.asp?id=156](http://www.dinochen.com/article.asp?id=156). Source: `ref/co.tcl`, with the ETABS model in `ref/EXAM05.s2k` and `ref/EXAM05.EDB`.

**Suggested Citation:**
Chen, X. W. Dino Chen's OpenSees tutorial, Example 05. http://www.dinochen.com/article.asp?id=156.

**Verification:**
The 12 eigenvalues (lambda = omega^2) match the source's `Periods.txt` to within 0.000033% (maximum). The periods run from T1 = 0.4278 s to T12 = 0.0720 s. The source's eigen recorders (`eigen1` to `eigen12` node outputs) are not in the archive, so the eigenvalues are the only reference.

**Notes:** Converted from `ref/co.tcl`. The 28 nodes, 22 masses, 47 elements, and 47 transform vectors match the source. The masses are used as given: in this N-mm system their unit is already N s^2/mm (AGENT.md §12al). The source's three `uniaxialMaterial Elastic` lines are never referenced by an element, so they are omitted (AGENT.md §12ap-6). `output/Periods.txt` is written in the source's eigenvalue format.

**Reference files:** `ref/co.tcl`, `ref/Periods.txt`, `ref/EXAM05.s2k`, `ref/EXAM05.EDB`.
