# Modern Tanks R1 — target test 2026-09-08

## Emulator

MD Emu Games Gen on Android.

## User-observed functional result

User reported that R1 works correctly and supplied screenshots of TEST_BATTLE and GARAGE shells.

Confirmed visually from the screenshots:

- TEST_BATTLE state is entered and rendered;
- GARAGE state is entered and rendered;
- state/bank switching is functioning;
- return-to-menu path is available;
- video reports 60 Hz;
- no visible crash/corruption in the supplied frames.

## Gate defect found in screenshots

The debug layer showed:

- TEST_BATTLE: `TRANS:003 ERR:03`, `LAST ERROR: PALETTE_RESIDUE`;
- GARAGE: `TRANS:005 ERR:05`, `LAST ERROR: PALETTE_RESIDUE`.

Therefore R1 was **not accepted** despite the positive functional result. The R1 gate requires zero palette residue and `ERR:00`.

## Root cause / correction

The original R1 cleanup wrote CRAM through CPU transfers and immediately performed CRAM readback. The VDP FIFO was not explicitly drained before switching the VDP command port to CRAM-read mode. This produced a false `PALETTE_RESIDUE` result on the target emulator.

Fix commit: `16ea3ccad96b51e0514e88076ee6c4f00b752098`.

Correction:

- clear all 64 CRAM entries in one `PAL_setColors(0, palette_black, 64, CPU)` operation;
- call `VDP_waitFIFOEmpty()` after the write;
- call `VDP_waitFIFOEmpty()` again immediately before CRAM readback.

No R2 content, old DEV code or Granada assets/code were introduced.

## CI after fix

GitHub Actions run: `34177478564`.

Result: **SUCCESS**.

- two clean SGDK 2.11 builds: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM audit: PASS;
- artifact publication: PASS.

Target emulator re-test is still required.

## Required target result

After boot and normal transitions, debug layer must remain `ERR:00`.

After pressing C in MAIN_MENU and completing the 100-transition soak:

- `SOAK: PASS 100/100`;
- `ERR:00`;
- `STATE: MAIN_MENU`;
- `BANK: MENU`;
- manual input still works.

Until that is confirmed, **R1 remains TARGET PENDING and R2 remains blocked**.
