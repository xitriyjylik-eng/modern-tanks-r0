# MODERN TANKS — START HERE NEXT SESSION

## Сначала

Прочитать:

1. `SESSION_HANDOFF_CURRENT.md`
2. `plan/REBUILD_MASTER_PLAN.md`
3. `plan/ACCEPTANCE_GATES.md`
4. `tests/r0/R0_ACCEPTANCE_RESULT.md`
5. `tests/r1/R1_BUILD_STATUS.md`
6. `tests/r1/R1_ACCEPTANCE_CHECKLIST.md`
7. `tests/r1/R1_TARGET_TEST_2026-09-08.md`

## Текущая точка

- **R0 Hardware Probe — ACCEPTED / CLOSED (2026-09-08).**
- **R1 Core / State Machine — FUNCTIONAL TARGET PASS / CLEANUP RETEST PENDING.**
- **R2 — BLOCKED до чистого пользовательского PASS R1.**

## Неизменяемые требования

- идея Modern Tanks сохраняется без изменений;
- `design/GAME_DESIGN_FROZEN.md` остаётся источником истины;
- три PNG reference нельзя изменять, перекодировать или заменять;
- Granada — только технический ориентир, не donor-ROM;
- старая DEV-линия, DEV ROM/builders/master-plan запрещены;
- ROM собирается штатным SGDK 2.11 toolchain.

## R0 — закрыт

Пользователь лично проверил R0 в MD Emu Games Gen на Android: стабильный запуск и изображение, R0A PASS, R0B PASS, D-Pad и A/B/C/START PASS. X/Y/Z не являются требованием, потому что R0 использует 3-button controller path.

## R1 — первый target-test

Пользователь подтвердил, что R1 визуально и по переходам работает. Но screenshots показали `LAST ERROR: PALETTE_RESIDUE` и рост ERR вместе с TRANS, поэтому формальный gate не закрыт.

Исправлен порядок CRAM cleanup/readback:

- fix commit `16ea3ccad96b51e0514e88076ee6c4f00b752098`;
- GitHub Actions run `34177478564` — SUCCESS;
- ROM 131072 bytes;
- SHA-256 `0798b55ea287dc991a896ae67c94d1afa8640a50f85366ab765809ff316cc713`;
- header checksum `0x8B8E`;
- verifier PASS;
- две clean SGDK builds идентичны byte-for-byte.

## Следующее действие

Только повторно проверить FIX1 ROM в MD Emu Games Gen. До запуска soak обычные переходы не должны увеличивать ERR. Затем в MAIN MENU нажать C и дождаться:

- `SOAK: PASS 100/100`;
- `ERR:00`;
- `STATE: MAIN_MENU`;
- `BANK: MENU`.

После soak снова проверить D-Pad/A/B/C/START.

**Не начинать R2 до прямого подтверждения чистого R1 PASS.**
