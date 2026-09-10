# MAP 01 — APPROVED VISUAL REFERENCE STATUS

Date: 2026-09-10
Branch: `r3-map-camera`
Status: **APPROVED MASTER REFERENCE / CONCEPT LOCKED**

The current R3 Region 1 artwork/geography was rejected by the user after emulator testing because it looked like repeated rectangular/stamped blocks and did not match the requested coherent hand-authored world quality.

The proven camera/MAP-streaming/HUD/NTSC-PAL technical foundation may be retained. The old Region 1 geography/art is **NOT accepted** and is not the design source for the rebuild.

Approved full-map overview reference:
`PROJECT_SOURCE/references/MAP_01_VISUAL_REFERENCE_APPROVED.png`

Reference image SHA-256:
`8871a7132c4e2915008e0ee217b8240c6bf26f95a0c4edce0566ea6dcdabf56b`

Authoritative concept specification:
`plan/MAP_01_REGION1_CONCEPT_LOCK.md`

The approved reference defines the large-scale Region 1 composition: coherent winding river from northern source/waterfall to southeast wetlands, 2–3 bridge crossings, central village/road hub, northwest ruins, northeast isolated homestead, eastern fields, southern farms, west/southwest lake and irregular forest masses.

For the new Map 01 art-authoring phase, previous arbitrary graphics-fitting targets are retired as artistic gates. In particular, palette-count/tile-reuse/block-count/%-matching metrics must not dictate the world composition. Technical adaptation must serve the approved art, not reshape it into a block carpet.

Runtime procedural terrain generation and procedural geography authoring remain forbidden. Automation is allowed only for technical support after the art exists: slicing, lossless transport, palette analysis/conversion, collision export, compression, build verification and regression tests.

Next work item after a separate user command: **Stage B — production master map**: create a clean high-resolution manually authored version of this overview, preserving its geography and improving detail/continuity before any SGDK/runtime conversion.
