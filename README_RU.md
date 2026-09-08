# Modern Tanks — Clean Rebuild

Чистая rebuild-линия **Modern Tanks** для Sega Mega Drive / Genesis на SGDK 2.11.

## Текущий принятый статус

- **R0 Hardware Probe — ACCEPTED / CLOSED**.
- **R1 Core / State Machine — ACCEPTED / CLOSED**.
- **R2 Main Menu Visual / Ambient — ACCEPTED / CLOSED** после фактической проверки владельцем в эмуляторе.
- **R3 Battle Renderer / HUD — NEXT / UNBLOCKED / NOT STARTED**.

Принятый baseline R2: commit `a1faa7d567ceb7f5506005b354da28f5c1ea0cee`.
Финальный R2 CI run: `34255626880` — SUCCESS.
Принятый ROM SHA-256: `fb6896471a1bf559e13c55118c3d2beedf8c1567ff6703a114ef05857b744017`.
ROM size: 131072 bytes. ROM audit: PASS.

## Жёсткие правила

- идею Modern Tanks не менять;
- `design/GAME_DESIGN_FROZEN.md` — источник истины по игре;
- старую DEV-линию, DEV ROM и Python opcode-emitter не использовать;
- три PNG в `references/` являются locked references: не изменять, не перекодировать и не заменять;
- Granada используется **только как технический образец** Mega Drive/VDP/resource discipline; её код, ассеты, карты, музыка и игровые правила не переносятся;
- обязательный базовый input path — 3-button controller;
- принятый R2 не редизайнить без прямого запроса владельца.

## R1 core — принято

Сохраняются:

- BOOT;
- TITLE;
- MAIN_MENU;
- TEST_BATTLE shell;
- GARAGE shell;
- state transitions;
- 3-button input abstraction;
- NTSC/PAL timing;
- debug/error layer;
- clean state enter/leave hooks;
- resource bank load/unload API.

## R2 main menu / ambient — принято

Финальный R2 работает в 320×224 и сохраняет утверждённую русскую типографику, центральное меню и цветовую гамму ландшафта. Правая мини-карта удалена.

Принятые окружающие эффекты:

- 12-кадровая река с течением по руслу, без воды на берегу/мосту/зданиях;
- 12-кадровый правый флаг на существующем флагштоке;
- левый флаг отсутствует;
- два независимых 8-кадровых огня без статичных дубликатов пламени на фоне;
- лёгкая 12-кадровая анимация листвы;
- анимации используют существующие палитровые категории сцены и не должны выделяться повышенной яркостью;
- каждая группа анимации имеет независимый таймер.

Ресурсы для финального R2 детерминированно строятся `sgdk/tools/build_refined_animation_assets.py`; `sgdk/res/resources.res` описывает итоговый набор кадров. CI проверяет маски, палитры и VRAM budget.

## Следующий этап — R3

R3 создаёт реальный battle renderer / HUD shell и является первым не начатым этапом после принятого меню. Подробное ТЗ: `plan/NEXT_R3_SCOPE.md`.

После R3 по плану: R4 танки → R5 Region 1/world foundation → R6 combat vertical slice → R7 regions 2–5 → R8 bosses/effects/weather → R9 meta systems → R10 SRAM → R11 audio → R12 QA/release candidate.

## GitHub Actions

Основная R2 проверка: `.github/workflows/r0-build.yml` — историческое имя файла сохранено.

Отдельная архивная сборка: `.github/workflows/r2-full-backup.yml`. Она формирует полный сохраняемый пакет с исходниками, финальными сгенерированными ресурсами, свежесобранным ROM, аудитом и SHA-256 manifest.

## Начинать чтение проекта отсюда

1. `00_CURRENT_STATUS_READ_FIRST.md`
2. `SESSION_HANDOFF_CURRENT.md`
3. `WHAT_DONE_WHAT_LEFT.md`
4. `plan/PROJECT_PROGRESS_ACCEPTED_R2.md`
5. `plan/NEXT_R3_SCOPE.md`
6. `design/GAME_DESIGN_FROZEN.md`
7. `plan/REBUILD_MASTER_PLAN.md`
