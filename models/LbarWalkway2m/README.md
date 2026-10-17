# LbarWalkway2m

**Purpose:** Equivalent OpenSeesPy model of the STAAD 2 m L-bar walkway, run at ULS 1.35 DL + 1.5 LL.

**Building System:** 2 m walkway framing in equal angles EA 75x75x6 (S275) — two 1 m spans cantilevering from a fixed support with a diagonal brace to a pinned support 0.6 m below.

**Model Description:** 3D elastic model (ndm=3, ndf=6) with 4 nodes and 3 elasticBeamColumn members (tags = STAAD joint/member numbers). Joint 1 fixed, joint 4 pinned. Single ULS pattern combining factored selfweight (1.35) and 2.25 kN/m live UDL on the two span members (1.5). Load-controlled static via the AGENT.md §3c manual LoadControl/Linear loop. ODB response collection via opst.post.CreateODB.

| Field | Value |
|-------|-------|
| Dimensions | 3D |
| Material | Steel (S275, elastic) |
| Lateral System | Braced cantilever walkway |
| Lateral Loading | Gravity-only static (ULS) |
| Earthquake Records | NA |
| Design Year | NA |
| File Format | .py |
| OpenSees Version | NA |
| Units | N, mm, MPa |

**References:**
models/2m L bars Walk way/Lbar walkway.std

**Suggested Citation:**
NA

**Notes:** Two deliberate deviations from the .std (user-confirmed 2026-09-23): member 3 carries the same EA 75x75x6 (no property assigned in .std); joint 4 pinned (no support in .std, which leaves a mechanism). Section values nominal EA 75x75x6: A = 873 mm², Iy = Iz = 455 000 mm⁴, J = 10 368 mm⁴. Counter-check vs STAAD .anl output pending — run STAAD ANALYSE and compare reactions/member forces (≤3%).
