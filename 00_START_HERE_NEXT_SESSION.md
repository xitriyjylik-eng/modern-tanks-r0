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
- **R2 Main Menu Visual Target — BUILD/CI PASS / TARGET ACCEPTANCE PENDING.**
- **R3 и далее — BLOCKED до прямого R2 acceptance.**

## Инварианты

- идея Modern Tanks не меняется;
- `design/GAME_DESIGN_FROZEN.md` — game-design truth;
- три PNG reference не изменять/не перекодировать/не заменять;
- Granada — только технический образец Mega Drive;
- старая DEV-линия запрещена;
- build только через clean SGDK 2.11 path.

## R2 — текущий build

R2 реализован поверх accepted R1 core.

- build commit `49ebfa6087cf8c39c313fa305cd48892509f0948`;
- GitHub Actions run `34180963691` — SUCCESS;
- ROM 131072 bytes;
- SHA-256 `dda9c3f62769371f9888b171a1ac2ac6374b886dead551db9fd3de657cbb539f`;
- header checksum `0x031D`;
- verifier PASS;
- build A/B byte-identical.

R2 содержит native-resolution menu art: MODERN TANKS logo, battlefield, steel panel, канонические русские menu items, tank-class strip, stats preview, mini-map, selector animation и subtle moving tank.

Locked `MAIN_MENU_REFERENCE.png` не изменён и не встроен. R2 art детерминированно генерируется `sgdk/tools/generate_r2_art.py` перед SGDK ResComp.

## Следующее действие

Только проверить R2 ROM в MD Emu Games Gen по `tests/r2/R2_ACCEPTANCE_CHECKLIST.md`.

Особенно проверить:

1. visual composition относительно locked reference;
2. Up/Down selector + pulse;
3. moving tank на фоне;
4. ИГРАТЬ → TEST_BATTLE → B → MENU, `ERR:00`;
5. ГАРАЖ → GARAGE → B → MENU, `ERR:00`;
6. несколько unload/reload циклов без corruption.

STATISTICS/OPTIONS в R2 visual-only и не обязаны открывать полноценные meta-state.

**R3 не начинать до прямого подтверждения владельца, что R2 принят.**
