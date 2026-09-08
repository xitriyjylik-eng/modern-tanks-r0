# R1 BUILD STATUS

Статус: **ACCEPTED / CLOSED**

## R1 scope

`sgdk/src/main.c` содержит R1 core-shell:

- BOOT / TITLE / MAIN_MENU / TEST_BATTLE / GARAGE;
- explicit state enter/leave hooks;
- ResourceBank load/unload API;
- 3-button input abstraction (`held/pressed/released`);
- fixed 60 Hz logical clock with PAL compensation;
- debug/error overlay;
- C → 100-transition soak.

R2 visual art, gameplay, map/tank/AI/SRAM/audio отсутствуют намеренно.

## Финальный FIX2 build

- repository: `xitriyjylik-eng/modern-tanks-r0`;
- source commit: `bc858a619de76a1f5c3112859914ea132e9bf7be`;
- GitHub Actions run: `34178302167`;
- job: `build-r1` — SUCCESS;
- SGDK: 2.11;
- build A/B: PASS;
- byte-for-byte comparison: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `78f73ba4ccabbca43433735538123de82b0097be9cb2dd5f7704838b103552c7`;
- header checksum: `0xAC94`;
- required checksum: `0xAC94`;
- full-ROM XOR-fold: `0x0000`;
- independent verifier: PASS.

## Target acceptance

Владелец проекта проверил FIX2 в MD Emu Games Gen на Android.

PASS подтверждён для:

- ручных переходов MAIN_MENU / TEST_BATTLE / GARAGE;
- `ERR:00`;
- `SOAK: PASS 100/100`;
- финального `STATE: MAIN_MENU`;
- финального `BANK: MENU`;
- продолжения ручной работы после soak до `TRANS:114` без появления ошибок.

Полный итог: `tests/r1/R1_ACCEPTANCE_RESULT.md`.

**R1 ACCEPTED / CLOSED. R2 UNLOCKED / NOT STARTED.**
