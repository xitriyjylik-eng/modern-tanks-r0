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

Владелец проекта явно объявил R0 полностью ACCEPTED. R0 закрыт и больше не блокирует R1.

## R1 — BUILD/CI PASS / TARGET NOT YET ACCEPTED

CI status: GitHub Actions run `34176727527` — SUCCESS; две clean SGDK 2.11 сборки идентичны; ROM audit PASS; SHA-256 `4fdc8d3d8ef9f723caf228b61f183b1fea927bee93727028f6e0a414cf6a726a`.

Build/CI PASS не равен acceptance. Target-test остаётся обязательным.

Gate: 100 последовательных переходов

`MENU → TEST_BATTLE → MENU → GARAGE → MENU`

повторённых 25 раз, без:

- VRAM corruption;
- leaked sprites;
- зависаний;
- потерянного input;
- palette residue.

R1 должен быть проверен пользователем в MD Emu Games Gen. До прямого подтверждения пользователя **R2 BLOCKED**.

## R2
Menu visual conformance.

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
