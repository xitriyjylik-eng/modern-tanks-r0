# Modern Tanks — current source of truth

Updated: 2026-09-11

## Status
- R0–R2: ACCEPTED / CLOSED. Keep only as baseline/history in `main`; do not use old R3 candidate documents as instructions.
- R3 / Map 01: IN PROGRESS / NOT ACCEPTED.
- Working branch: `r3-live-map01-rom-v1`.
- Map 01 master: 1536×1152, 12×9 sectors of 128×128.
- Z01: full technical pipeline DONE.
- Z03: full technical pipeline DONE; Z01↔Z03 integration PASS.
- Z02 WORLD_ART: DONE V1.
- Z02 TERRAIN + COLLISION: DONE V1 / QA REVIEWED.
- Next content task: manual Z02 OBJECTS + EVENTS, then SPAWN/runtime and integration check.

## Rules
- Build the world primarily by hand. Scripts/generators are for deterministic slicing, conversion, validation and already-authored coordinates, not procedural world design.
- `main` remains the accepted R0–R2 baseline until explicit owner acceptance of R3.
- Old 1024×768 R3 candidate, old Stage 9/10 status, and stale handoff/next-scope documents are obsolete and must not be treated as instructions.
- Current runtime/toolchain additions on this branch are infrastructure only; they do not change the Map 01 content checkpoint.

## Transitional runtime dependency
`sgdk/src/main.c` and the `r3_region1_*` resources still contain the old 1024×768 renderer path. They are retained only because the current build still depends on them while Map 01 runtime integration is incomplete. They are not a design/art source and must be replaced by the Map 01 runtime path, not extended.

## Current checkpoint
Base content checkpoint: `12f9d9675ac45e062c68a5097d59a52e46c03e57` — Z02 terrain/collision complete.
