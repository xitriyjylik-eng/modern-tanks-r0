# MODERN TANKS — START HERE NEXT SESSION

## Сначала прочитать

1. `SESSION_HANDOFF_CURRENT.md`
2. `plan/REBUILD_MASTER_PLAN.md`
3. `plan/ACCEPTANCE_GATES.md`
4. `tests/r0/R0_ACCEPTANCE_RESULT.md`
5. `tests/r1/R1_ACCEPTANCE_RESULT.md`
6. `tests/r2/R2_BUILD_STATUS.md`
7. `tests/r2/R2_ACCEPTANCE_CHECKLIST.md`
8. `design/GAME_DESIGN_FROZEN.md`

## Текущая точка

- **R0 Hardware Probe — ACCEPTED / CLOSED.**
- **R1 Core / State Machine — ACCEPTED / CLOSED.**
- **R2 Main Menu Visual Target — VISUAL REWORK 1 BUILD/CI PASS / TARGET ACCEPTANCE PENDING.**
- **R3 и далее — BLOCKED до прямого R2 acceptance.**

## Критически важная история R2

Первый R2 candidate технически работал, но владелец проекта визуально отклонил его после запуска в MD Emu Games Gen: он был слишком упрощён относительно locked `references/MAIN_MENU_REFERENCE.png`.

Не возвращаться к первому R2 art. Текущий acceptance candidate — **Visual Rework 1**.

## Инварианты

- идея Modern Tanks не меняется;
- `design/GAME_DESIGN_FROZEN.md` — game-design truth;
- три PNG reference не изменять/не перекодировать/не заменять;
- Granada — только технический образец Mega Drive;
- старая DEV-линия запрещена;
- build только через clean SGDK 2.11 path.

## R2 Visual Rework 1 — текущий build

- build commit `0442a22167097d4b9dc5964301e93fbf2f894234`;
- GitHub Actions run `34182713358` — SUCCESS;
- ROM 131072 bytes;
- SHA-256 `5b6a711bc38255793950c0259b2e297d57fa0bc5978a1210fed4e4911619fe98`;
- header checksum `0x3D61`;
- verifier PASS;
- build A/B byte-identical.

Visual Rework 1 добавляет значительно более плотный native 320×224 pixel-art: winding river, shoreline, forests, bridges, fortifications, craters, multiple tanks, shell/explosion/smoke scene, dimensional metallic logo, narrower central panel, detailed T-1…T-4 strip, segmented stats и improved minimap.

Канонические main-menu semantics остаются frozen: `ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ`. Прокачка остаётся внутри ГАРАЖА, миссии — внутри ИГРАТЬ.

Locked `MAIN_MENU_REFERENCE.png` не изменён и не встроен. Runtime R2 art детерминированно генерируется `sgdk/tools/generate_r2_art.py` перед SGDK ResComp.

## Следующее действие

Только проверить **Visual Rework 1 ROM** в MD Emu Games Gen по `tests/r2/R2_ACCEPTANCE_CHECKLIST.md`.

Особенно проверить:

1. visual composition/density относительно locked reference;
2. Up/Down selector + pulse;
3. moving tank на фоне;
4. ИГРАТЬ → TEST_BATTLE → B → MENU, `ERR:00`;
5. ГАРАЖ → GARAGE → B → MENU, `ERR:00`;
6. несколько unload/reload циклов без corruption.

**R3 не начинать до прямого подтверждения владельца, что R2 принят.**
