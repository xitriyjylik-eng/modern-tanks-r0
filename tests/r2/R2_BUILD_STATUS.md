# R2 BUILD STATUS

Дата: **2026-09-08**

Статус: **BUILD/CI PASS / TARGET ACCEPTANCE PENDING**

## Stage

R2 Main Menu Visual Target.

R0 и R1 остаются ACCEPTED / CLOSED. R3 не начинать до отдельного принятия R2 владельцем проекта.

## Реализовано в R2

- accepted R1 core/state machine сохранён;
- нативное меню 320×224 для Mega Drive;
- крупный MODERN TANKS logo;
- battlefield background;
- steel-frame visual language;
- четыре канонических русских пункта: ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ;
- tank-class strip;
- stats preview;
- mini-map preview;
- animated selector;
- subtle scripted moving tank на фоне;
- ИГРАТЬ открывает TEST_BATTLE shell;
- ГАРАЖ открывает GARAGE shell;
- STATISTICS/OPTIONS намеренно остаются visual-only в R2 и будут полноценными meta-state позже;
- menu-bank teardown использует принятую R1 blanked VDP transaction и self-check CRAM/sprites.

## Инварианты

- `design/GAME_DESIGN_FROZEN.md` не менялся;
- locked reference PNG не встраивается в ROM и не изменяется;
- R2 art строится нативно, а не автоуменьшением reference;
- Granada assets/code не используются;
- старый DEV-код не используется;
- R3 gameplay/renderer отсутствует намеренно.

## Воспроизводимый art pipeline

`sgdk/tools/generate_r2_art.py` детерминированно создаёт indexed PNG перед SGDK ResComp. Это исключает зависимость от бинарной передачи PNG через GitHub connector и сохраняет исходный reference нетронутым.

## GitHub Actions — PASS

- repository: `xitriyjylik-eng/modern-tanks-r0`;
- build commit: `49ebfa6087cf8c39c313fa305cd48892509f0948`;
- run: `34180963691`;
- job: `build-r2` — SUCCESS;
- SGDK: 2.11;
- generated-art validation: PASS;
- source/locked-art contract: PASS;
- build A: PASS;
- build B: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM audit: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `dda9c3f62769371f9888b171a1ac2ac6374b886dead551db9fd3de657cbb539f`;
- header checksum: `0x031D`;
- required checksum: `0x031D`;
- full-ROM XOR-fold: `0x0000`;
- artifact: `Modern_Tanks_R2_Main_Menu_Visual`.

## Resource budget

Conservative project-owned menu pattern worst case:

- 444 tiles;
- 14,208 bytes pattern data;
- 30,848 bytes free относительно консервативного 44 KiB project pattern ceiling;
- project VDP sprite payload: 0; scripted tank использует Plane A tiles.

Подробности: `sgdk/res/R2_RESOURCE_BUDGET.md`.

## Gate

CI подтверждает, что ROM корректно и воспроизводимо собирается, но не закрывает visual target gate.

Нужен фактический тест владельцем в MD Emu Games Gen и визуальная проверка относительно `references/MAIN_MENU_REFERENCE.png`.

**R2 НЕ ACCEPTED. R3 BLOCKED.**
