# Modern Tanks — Clean Rebuild

Чистая rebuild-линия **Modern Tanks** для Sega Mega Drive / Genesis на SGDK 2.11.

## Текущий статус

- **R0 Hardware Probe — ACCEPTED / CLOSED** после фактической проверки владельцем в MD Emu Games Gen.
- **R1 Core / State Machine — ACCEPTED / CLOSED**.
- **R2 Main Menu Visual — BUILD / CI PASS, TARGET ACCEPTANCE PENDING**.
- **R3 gameplay — BLOCKED** до прямого пользовательского подтверждения R2.

Текущий R2 animated candidate собран GitHub Actions run `34231083602`. Две независимые SGDK 2.11 сборки совпали byte-for-byte; ROM audit PASS. ROM SHA-256: `571360f8ba7c0a348a76983bf60c213dd564888206d46ef07d3e3dad83f3e824`.

## Жёсткие правила

- идею Modern Tanks не менять;
- `design/GAME_DESIGN_FROZEN.md` — источник истины по игре;
- старую DEV-линию, DEV ROM и Python opcode-emitter не использовать;
- три PNG reference не изменять и не перекодировать;
- Granada используется **только как технический образец** Mega Drive/VDP/resource discipline; её code/assets/maps/music/game rules не переносятся;
- обязательный базовый input path — 3-button controller.

## R1 core

Сохраняются:

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
- resource bank load/unload API.

## R2 animated menu candidate

Текущая сборка сохраняет русскую типографику главного меню, убирает правую мини-карту и добавляет четырёхкадровые циклы движения реки вниз, двух флагов на ветру и огня. Поле работает в нативном разрешении 320×224 с прямыми индексированными PNG-ресурсами; восстановление PNG через Base64/Base85 в CI не используется.

R2 закрывается только после визуального подтверждения владельцем на целевом эмуляторе.

## GitHub Actions

Workflow: `.github/workflows/r0-build.yml` — историческое имя файла сохранено.

CI проверяет прямые PNG-ресурсы, собирает проект дважды из одного SGDK 2.11 Docker image, сравнивает ROM byte-for-byte, проверяет ROM header/checksum, SHA-256 и публикует artifact.

## Точки входа

- `SESSION_HANDOFF_CURRENT.md`
- `plan/REBUILD_MASTER_PLAN.md`
- `plan/ACCEPTANCE_GATES.md`
- `tests/r0/R0_ACCEPTANCE_RESULT.md`
- `tests/r1/R1_BUILD_STATUS.md`
- `tests/r1/R1_ACCEPTANCE_CHECKLIST.md`
