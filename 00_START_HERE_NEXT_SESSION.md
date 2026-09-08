# MODERN TANKS — START HERE NEXT SESSION

## Сначала

Прочитать:

1. `SESSION_HANDOFF_CURRENT.md`
2. `plan/REBUILD_MASTER_PLAN.md`
3. `plan/ACCEPTANCE_GATES.md`
4. `tests/r0/R0_ACCEPTANCE_RESULT.md`
5. `tests/r1/R1_BUILD_STATUS.md`
6. `tests/r1/R1_ACCEPTANCE_CHECKLIST.md`

## Текущая точка

- **R0 Hardware Probe — ACCEPTED / CLOSED (2026-09-08).**
- **R1 Core / State Machine — BUILD/CI PASS / TARGET ACCEPTANCE PENDING.**
- **R2 — BLOCKED до прямого пользовательского PASS R1.**

## Неизменяемые требования

- идея Modern Tanks сохраняется без изменений;
- `design/GAME_DESIGN_FROZEN.md` остаётся источником истины;
- три PNG reference нельзя изменять, перекодировать или заменять;
- Granada — только технический ориентир, не donor-ROM;
- старая DEV-линия, DEV ROM/builders/master-plan запрещены;
- ROM собирается штатным SGDK 2.11 toolchain.

## R0 — закрыт

Пользователь лично проверил R0 в MD Emu Games Gen на Android: стабильный запуск и изображение, R0A PASS, R0B PASS, D-Pad и A/B/C/START PASS. X/Y/Z не являются требованием, потому что R0 использует 3-button controller path.

## R1 — собран

Scope R1 ограничен core-shell: BOOT, TITLE, MAIN_MENU, TEST_BATTLE, GARAGE, 3-button input abstraction, PAL/NTSC timing, debug/error layer, enter/leave hooks, resource bank API и 100-transition soak.

CI:

- run `34176727527` — SUCCESS;
- commit `d348e0518bfe74d47da6db705313e4a26c0fc891`;
- ROM 131072 bytes;
- SHA-256 `4fdc8d3d8ef9f723caf228b61f183b1fea927bee93727028f6e0a414cf6a726a`;
- verifier PASS;
- две clean SGDK builds идентичны byte-for-byte.

## Следующее действие

Только проверить R1 ROM в MD Emu Games Gen по `tests/r1/R1_ACCEPTANCE_CHECKLIST.md`. В MAIN MENU нажать C и дождаться `SOAK: PASS 100/100`, `ERR: 00`, `STATE: MAIN_MENU`, `BANK: MENU`, затем снова проверить ручной input.

**Не начинать R2 до прямого подтверждения пользователя, что R1 принят.**
