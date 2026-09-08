# ACCEPTANCE GATES

## Общее правило

Ни одна стадия не считается завершённой по факту успешной компиляции.

Обычная схема проверки:

1. **Build** — компиляция, header, checksum, resource checks.
2. **Emulator** — минимум один точный desktop emulator, когда он доступен в текущем цикле проверки.
3. **Target** — фактический запуск пользователем в MD Emu Games Gen.

Прямое решение владельца проекта может закрыть конкретный gate после фактической проверки целевого ROM; такое решение должно быть явно записано в handoff и тестовом отчёте.

## Красный флаг

Если target-screen отличается от ожидаемого:

- стадия остаётся FAIL/PENDING;
- следующая функциональность не добавляется;
- сначала локализуется причина на текущем минимальном scope;
- успешный CI не отменяет visual rejection владельца.

## R0 — ACCEPTED / CLOSED — 2026-09-08

Фактический тест пользователем в MD Emu Games Gen:

- стабильный запуск — PASS;
- изображение — PASS;
- R0A — PASS;
- R0B — PASS;
- D-Pad — PASS;
- A/B/C/START — PASS;
- X/Y/Z не являются требованием R0, так как probe принудительно использует `JOY_SUPPORT_3BTN`.

R0 закрыт и больше не блокирует следующие стадии.

## R1 — ACCEPTED / CLOSED — 2026-09-08

Финальный accepted ROM: FIX2.

CI:

- source commit `bc858a619de76a1f5c3112859914ea132e9bf7be`;
- GitHub Actions run `34178302167` — SUCCESS;
- две clean SGDK 2.11 сборки идентичны byte-for-byte;
- ROM audit PASS;
- ROM SHA-256 `78f73ba4ccabbca43433735538123de82b0097be9cb2dd5f7704838b103552c7`.

Target gate требовал 100 последовательных переходов

`MENU → TEST_BATTLE → MENU → GARAGE → MENU`

повторённых 25 раз, без VRAM corruption, leaked sprites, зависаний, потерянного input и palette residue.

Фактический target-result в MD Emu Games Gen:

- обычные переходы работают;
- `ERR:00` после ручных переходов;
- `SOAK: PASS 100/100`;
- финал `STATE: MAIN_MENU`;
- финал `BANK: MENU`;
- финал `ERR:00`;
- после soak пользователь продолжил ручные переходы; финальный screenshot показывает `TRANS:114`, `ERR:00`.

`LAST ERROR: R1_ITEM_NOT_IMPLEMENTED` при `ERR:00` не считается gate defect: это информационная строка при выборе intentionally locked R1 item и она не увеличивает `errorCount`.

Итог: **R1 ACCEPTED / CLOSED.**

## R2 — VISUAL REWORK 1 / BUILD/CI PASS / TARGET ACCEPTANCE PENDING

Stage: Main Menu Visual Target.

### Target history

Первый R2 candidate технически прошёл CI, но был **визуально отклонён владельцем** после запуска в MD Emu Games Gen и прямого сравнения с `references/MAIN_MENU_REFERENCE.png`.

Этот build не является accepted R2 и больше не используется как visual candidate.

Основные причины rejection: недостаточная visual density, плоский logo, простой клетчатый battlefield, слишком широкая central panel, условные tank silhouettes и упрощённый bottom HUD.

### Visual Rework 1 build evidence

- build commit `0442a22167097d4b9dc5964301e93fbf2f894234`;
- GitHub Actions run `34182713358` — SUCCESS;
- native-resolution R2 art generation PASS;
- locked-art/source contract PASS;
- two clean SGDK 2.11 builds PASS и byte-for-byte identical;
- independent ROM audit PASS;
- ROM size `131072` bytes;
- ROM SHA-256 `5b6a711bc38255793950c0259b2e297d57fa0bc5978a1210fed4e4911619fe98`;
- header checksum `0x3D61`;
- full-ROM XOR-fold `0x0000`.

Visual Rework 1 содержит native 320×224 artwork с winding river/shoreline, forest clusters, bridges, brick/steel fortifications, craters, multiple tanks, shell/explosion/smoke scene, dimensional metallic logo, narrower reference-like menu panel, detailed T-1…T-4 strip, segmented stats и improved minimap.

### Gate R2

PASS только если владелец прямо принимает новый target screen после проверки в MD Emu Games Gen:

- screen comparison с `references/MAIN_MENU_REFERENCE.png` по композиции, visual density и 16-bit visual language;
- крупный dimensional MODERN TANKS logo;
- насыщенный battlefield background, а не tile-placeholder поле;
- steel frame language;
- четыре канонических русских пункта меню;
- tank-class strip с различимыми T-1…T-4 silhouettes;
- stats preview;
- mini-map preview;
- selector animation + subtle scripted background action;
- нет пустых placeholder-панелей;
- нет automatically downscaled dirty reference graphics;
- menu bank полностью выгружается при переходе в TEST_BATTLE/GARAGE shell;
- после нескольких unload/reload циклов сохраняется `ERR:00`;
- нет VRAM/palette/sprite corruption;
- free project pattern budget зафиксирован в `sgdk/res/R2_RESOURCE_BUDGET.md`.

Полный target checklist: `tests/r2/R2_ACCEPTANCE_CHECKLIST.md`.

**R2 пока НЕ ACCEPTED. R3 BLOCKED до прямого target PASS владельца.**

## R3
Scrolling/HUD/window stability.

## R4
Player sprites/banks/scanline budget.

## R5
World streaming/metatile/collision consistency.

## R6
One complete mission gameplay slice.

## R7
All region banks.

## R8
Boss/effects/weather budget.

## R9
Full meta-state cycle.

## R10
SRAM recovery tests.

## R11
Audio/Z80 stress tests.

## R12
Multi-emulator/release QA.
