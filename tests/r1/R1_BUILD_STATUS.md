# R1 BUILD STATUS

Статус: **FUNCTIONAL TARGET PASS / FIX2 CI PASS / TARGET RETEST PENDING**

## R1 scope

`sgdk/src/main.c` содержит только R1 core-shell:

- BOOT / TITLE / MAIN_MENU / TEST_BATTLE / GARAGE;
- explicit state enter/leave hooks;
- ResourceBank load/unload API;
- 3-button input abstraction (`held/pressed/released`);
- fixed 60 Hz logical clock with PAL compensation;
- debug/error overlay;
- C → 100-transition soak.

R2 visual art, gameplay, map/tank/AI/SRAM/audio отсутствуют намеренно.

## Target history

Первый R1 и FIX1 функционально работали в MD Emu Games Gen, но debug layer показывал `PALETTE_RESIDUE` на каждом state transition. FIX1 (FIFO drain) оказался недостаточен.

Подробности: `tests/r1/R1_TARGET_TEST_2026-09-08.md`.

## FIX2 cleanup model

State transition теперь выполняется при временно выключенном VDP display:

- display OFF;
- plane/sprite/CRAM teardown;
- all 64 CRAM colors cleared;
- FIFO drained;
- CRAM readback with interrupts masked;
- next bank loaded and state drawn;
- display ON.

Это делает R1 palette-cleanup self-check детерминированным вместо CRAM readback во время active scanout.

## GitHub Actions FIX2 — PASS

- repository: `xitriyjylik-eng/modern-tanks-r0`;
- source commit: `bc858a619de76a1f5c3112859914ea132e9bf7be`;
- run: `34178302167`;
- job: `build-r1` — SUCCESS;
- SGDK: 2.11;
- build A/B: PASS;
- byte-for-byte comparison: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `78f73ba4ccabbca43433735538123de82b0097be9cb2dd5f7704838b103552c7`;
- header checksum: `0xAC94`;
- required checksum: `0xAC94`;
- full-ROM XOR-fold: `0x0000`;
- independent verifier: PASS;
- artifact: `Modern_Tanks_R1_Core_Menu`.

## Gate

Новый FIX2 ROM должен быть проверен владельцем в MD Emu Games Gen.

PASS только при:

- обычные переходы не увеличивают `ERR`;
- после C-soak: `SOAK: PASS 100/100`;
- `ERR:00`;
- `STATE: MAIN_MENU`;
- `BANK: MENU`;
- input работает после soak.

**R1 НЕ ACCEPTED до этого target result. R2 BLOCKED.**
