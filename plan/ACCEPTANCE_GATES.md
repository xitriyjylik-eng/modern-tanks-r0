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

## R2 — FINAL VISUAL CANDIDATE / CI PASS / TARGET ACCEPTANCE PENDING

Stage: Main Menu Visual Target.

### История visual rejection

Предыдущие R2 builds технически собирались, но были отклонены владельцем из-за слабого соответствия образцам: процедурный клетчатый battlefield, упрощённые танки, лишний нижний HUD, декоративный moving tank и недостаточная visual density.

Эти варианты больше не являются visual candidate.

### Новый visual target владельца

Старый визуальный подход заменён двумя новыми образцами из текущей сессии:

- battlefield gameplay reference: top-down река/мост/лес/дороги/постройки/укрепления/кратеры/огонь/дым, насыщенный 16-bit pixel-art;
- tank mini-sprite reference: T-1/T-2/T-3/T-4, 16x16 gameplay size, 8 направлений, один основной ствол, чёткие корпус/башня/гусеницы и разные silhouettes.

Главное меню должно выглядеть частью того же мира, а не отдельным техническим mockup.

### Current final candidate build evidence

- build commit `d087d03275c658e4799afa53e395251083308669`;
- GitHub Actions run `34201271457` — **SUCCESS**;
- exact prepared background asset `320x224`, indexed-P, SHA-256 `5ec08a6cb60201367bc45becdf116f3efe71597762f5f25d7aa28b62ff6426ea`;
- selector `144x16`, SHA-256 `36deb4395d061cc75f9972e0427b2c9b1ccf45ca2eb95992feac49a0737170fd`;
- PAL0..PAL3 per-8x8-tile validation PASS; tile distribution `576 / 56 / 150 / 338`;
- background unique indexed tiles `921`, selector `6` before ResComp duplicate/flip optimization;
- artificial project graphics ceiling removed; only actual SGDK/VDP limits remain and runtime checks `TILE_USER_MAX_INDEX`;
- two clean SGDK 2.11 builds PASS and byte-for-byte identical;
- independent ROM audit PASS;
- ROM size `131072` bytes;
- ROM SHA-256 `e0b3a90b3a33c8e06bde7ec9749ef7f105ff38558ed3d6eb6b1c0dda5909773c`;
- header checksum `0x49B6` equals required checksum `0x49B6`;
- full-ROM XOR-fold `0x0000`.

### Required R2 composition

- full 320x224 battlefield-style background;
- large `MODERN TANKS` logo;
- steel/navy central panel;
- `ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ`;
- selector/navigation;
- **no** lower `T-1..T-4 / stats / minimap` strip;
- **no** detached decorative moving tank;
- tank/class selection belongs to `ГАРАЖ`;
- map/mission context belongs to mission/gameplay screens.

### Gate R2

PASS только после прямого решения владельца по фактическому ROM в MD Emu Games Gen:

- визуально меню принадлежит тому же миру, что новый gameplay reference;
- фон имеет насыщенную читаемую реку/мост/лес/дороги/постройки/следы боя, без прежнего placeholder/cell look;
- logo и steel/navy panel хорошо читаются;
- четыре канонических русских пункта меню читаются;
- Up/Down selector работает;
- `ИГРАТЬ → TEST_BATTLE → B → MENU` работает;
- `ГАРАЖ → GARAGE → B → MENU` работает;
- menu bank unload/reload не вызывает VRAM/palette/sprite corruption;
- после нескольких переходов нет ERR/corruption;
- нижний HUD и декоративный moving tank отсутствуют.

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
