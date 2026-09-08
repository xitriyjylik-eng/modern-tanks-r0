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

- стадия остаётся FAIL;
- следующая функциональность не добавляется;
- сначала локализуется причина на текущем минимальном scope.

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

## R2 — BUILD/CI PASS / TARGET ACCEPTANCE PENDING

Stage: Main Menu Visual Target.

Build evidence:

- build commit `49ebfa6087cf8c39c313fa305cd48892509f0948`;
- GitHub Actions run `34180963691` — SUCCESS;
- native-resolution R2 art generation PASS;
- locked-art/source contract PASS;
- two clean SGDK 2.11 builds PASS и byte-for-byte identical;
- independent ROM audit PASS;
- ROM size `131072` bytes;
- ROM SHA-256 `dda9c3f62769371f9888b171a1ac2ac6374b886dead551db9fd3de657cbb539f`;
- header checksum `0x031D`;
- full-ROM XOR-fold `0x0000`.

Gate R2:

- screen comparison с `references/MAIN_MENU_REFERENCE.png` по композиции/visual language;
- крупный MODERN TANKS logo;
- battlefield background;
- steel frame language;
- четыре канонических русских пункта меню;
- tank-class strip;
- stats preview;
- mini-map preview;
- selector animation + subtle scripted background action;
- нет пустых placeholder-панелей;
- нет автоматически уменьшенной грязной графики;
- menu bank полностью выгружается при переходе в TEST_BATTLE/GARAGE shell;
- после нескольких unload/reload циклов сохраняется `ERR:00`;
- free VRAM/project pattern budget зафиксирован в `sgdk/res/R2_RESOURCE_BUDGET.md`.

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
