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

Итог: **R1 ACCEPTED / CLOSED. R2 UNLOCKED.**

## R2 — UNLOCKED / NOT STARTED

Menu visual conformance.

Gate R2:

- screen comparison с `references/MAIN_MENU_REFERENCE.png`;
- нет пустых placeholder-панелей;
- нет автоматически уменьшенной грязной графики;
- menu bank полностью выгружается при переходе в battle;
- free VRAM зафиксирована в отчёте.

R3 не начинать до отдельного R2 acceptance.

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
