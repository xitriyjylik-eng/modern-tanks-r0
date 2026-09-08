# R2 BUILD STATUS

Дата: **2026-09-08**

Статус: **VISUAL REWORK 1 — BUILD/CI PASS / TARGET ACCEPTANCE PENDING**

## Stage

R2 Main Menu Visual Target.

R0 и R1 остаются ACCEPTED / CLOSED. R3 не начинать до отдельного принятия R2 владельцем проекта.

## История target-проверки R2

Первый R2 candidate технически работал и прошёл CI, но владелец проекта **визуально отклонил** его после сравнения с `references/MAIN_MENU_REFERENCE.png`.

Причина отказа: он передавал только общую схему референса, но был существенно беднее по визуальной плотности — плоский логотип, слишком простое поле, слишком широкая центральная панель, условные танки и упрощённый нижний HUD.

Этот build больше не считать кандидатом на acceptance.

## Visual Rework 1

R2 полностью перерисован в native 320×224 без масштабирования locked reference.

Добавлено/переделано:

- более узкая центральная композиция, близкая к reference;
- объёмный металлический MODERN TANKS logo с боковыми steel wings;
- извилистая река и береговые полосы вместо прямых клетчатых каналов;
- forest clusters;
- dirt/grass variation;
- мосты;
- brick/steel fortifications;
- кратеры и debris;
- несколько различимых battlefield tanks;
- muzzle flashes, shell traces, explosions и smoke;
- edge sign panels;
- четыре канонических пункта `ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ`;
- selector уменьшен до 104×16 и соответствует новой геометрии меню;
- более детальные T-1…T-4 silhouettes;
- segmented stats bars;
- улучшенная minimap;
- accepted R1 transitions/cleanup сохранены.

## Инварианты

- `design/GAME_DESIGN_FROZEN.md` не менялся;
- locked reference PNG не изменён, не перекодирован и не встроен в ROM;
- runtime art строится нативно, а не автоуменьшением reference;
- Granada assets/code не используются;
- старый DEV-код не используется;
- R3 gameplay/renderer отсутствует намеренно.

## GitHub Actions — PASS

Visual Rework 1 final build:

- repository: `xitriyjylik-eng/modern-tanks-r0`;
- build commit: `0442a22167097d4b9dc5964301e93fbf2f894234`;
- GitHub Actions run: `34182713358`;
- job: `build-r2` — SUCCESS;
- SGDK: 2.11;
- generated-art validation: PASS;
- source/locked-art contract: PASS;
- build A: PASS;
- build B: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM audit: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `5b6a711bc38255793950c0259b2e297d57fa0bc5978a1210fed4e4911619fe98`;
- header checksum: `0x3D61`;
- required checksum: `0x3D61`;
- full-ROM XOR-fold: `0x0000`;
- artifact: `Modern_Tanks_R2_Main_Menu_Visual_Rework_1`.

## Resource budget

Conservative pre-ResComp project-owned upper bound:

- 658 unique 8×8 tiles;
- 21,056 bytes pattern data;
- at least 24,000 bytes free относительно консервативного 44 KiB project pattern ceiling;
- project VDP sprite payload: 0; scripted tank uses Plane A tiles.

Подробности: `sgdk/res/R2_RESOURCE_BUDGET.md`.

## Gate

CI подтверждает корректную и воспроизводимую сборку, но R2 visual target закрывается только target-тестом владельца в MD Emu Games Gen.

Проверить Visual Rework 1 относительно locked `MAIN_MENU_REFERENCE.png`, затем переходы ИГРАТЬ/ГАРАЖ и отсутствие corruption/ERR.

**R2 НЕ ACCEPTED. R3 BLOCKED.**
