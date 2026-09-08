# Modern Tanks — Clean Rebuild

Чистая rebuild-линия **Modern Tanks** для Sega Mega Drive / Genesis на SGDK 2.11.

## Текущий статус

- **R0 Hardware Probe — ACCEPTED / CLOSED** 2026-09-08 после фактической проверки владельцем в MD Emu Games Gen.
- **R1 Core / State Machine — BUILD/CI PASS / TARGET ACCEPTANCE PENDING**.
- **R2 и далее — BLOCKED** до прямого пользовательского PASS R1.

R1 GitHub Actions run `34176727527` завершён SUCCESS. Две clean SGDK 2.11 сборки совпали byte-for-byte; ROM audit PASS. R1 ROM SHA-256: `4fdc8d3d8ef9f723caf228b61f183b1fea927bee93727028f6e0a414cf6a726a`.

## Жёсткие правила

- идею Modern Tanks не менять;
- `design/GAME_DESIGN_FROZEN.md` — источник истины по игре;
- старую DEV-линию, DEV ROM и Python opcode-emitter не использовать;
- три PNG reference не изменять и не перекодировать;
- Granada используется **только как технический образец** Mega Drive/VDP/resource discipline; её code/assets/maps/music/game rules не переносятся;
- обязательный базовый input path — 3-button controller.

## R1 scope

Только:

- BOOT;
- TITLE;
- MAIN_MENU shell;
- TEST_BATTLE shell;
- GARAGE shell;
- state transitions;
- 3-button input abstraction;
- NTSC/PAL timing;
- debug/error layer;
- clean state enter/leave hooks;
- resource bank load/unload API;
- встроенный 100-transition soak test.

Финальная графика меню, battle renderer, tank art, world, AI, SRAM и audio относятся к последующим стадиям.

## R1 target test

В MAIN MENU кнопка **C** запускает 100 переходов — 25 циклов:

`MENU → TEST_BATTLE → MENU → GARAGE → MENU`

Ожидаемый итог: `SOAK: PASS 100/100`, `ERR: 00`, `STATE: MAIN_MENU`, `BANK: MENU`, после чего ручной input должен продолжать работать.

## GitHub Actions

Workflow: `.github/workflows/r0-build.yml` — историческое имя файла сохранено, но workflow сейчас собирает R1.

CI выполняет две независимые clean builds из одного exact SGDK 2.11 Docker image ID, byte comparison, ROM header/checksum audit, SHA-256 и artifact publication.

## Точки входа

- `SESSION_HANDOFF_CURRENT.md`
- `plan/REBUILD_MASTER_PLAN.md`
- `plan/ACCEPTANCE_GATES.md`
- `tests/r0/R0_ACCEPTANCE_RESULT.md`
- `tests/r1/R1_BUILD_STATUS.md`
- `tests/r1/R1_ACCEPTANCE_CHECKLIST.md`
