# ACCEPTANCE GATES — CURRENT

Updated: 2026-09-11

## General rule
A stage is not accepted merely because it compiles. Acceptance requires the checks appropriate to the stage and, for owner-facing visual/gameplay milestones, explicit owner approval.

## Current R3 / Map 01 gates
For each zone:
1. WORLD_ART scope is authored and locked.
2. TERRAIN/COLLISION is validated.
3. OBJECTS/EVENTS is authored and validated.
4. SPAWN/runtime data is validated.
5. Integration with neighboring completed zones passes.
6. Regressions are checked without reopening already accepted art unnecessarily.

## Build/runtime gate
Before R3 acceptance:
- SGDK 2.11 build passes;
- ROM audit/checksum passes;
- runtime uses the current Map 01 data path;
- camera movement is smooth and does not hang;
- map loading/streaming does not introduce long blocking loads;
- no visible technical sector seams;
- final visual/gameplay result is checked by the owner.

## Current milestone
Z01 DONE; Z03 DONE and integrated; Z02 WORLD_ART + TERRAIN/COLLISION DONE.
Next gate: Z02 OBJECTS + EVENTS.

`main` remains the accepted R0–R2 baseline until explicit R3 acceptance.
