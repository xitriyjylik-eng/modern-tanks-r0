# MODERN TANKS — START HERE NEXT SESSION

## Сначала прочитать

1. `SESSION_HANDOFF_CURRENT.md`
2. `plan/REBUILD_MASTER_PLAN.md`
3. `plan/ACCEPTANCE_GATES.md`
4. `tests/r0/R0_ACCEPTANCE_RESULT.md`
5. `tests/r1/R1_ACCEPTANCE_RESULT.md`
6. `design/GAME_DESIGN_FROZEN.md`

## Текущая точка

- **R0 Hardware Probe — ACCEPTED / CLOSED.**
- **R1 Core / State Machine — ACCEPTED / CLOSED.**
- **R2 Main Menu Visual Target — UNLOCKED / NOT STARTED.**
- **R3 и далее — не начинать до отдельного R2 acceptance.**

## Инварианты

- идея Modern Tanks не меняется;
- `design/GAME_DESIGN_FROZEN.md` — game-design truth;
- три PNG reference не изменять/не перекодировать/не заменять;
- Granada — только технический образец Mega Drive;
- старая DEV-линия запрещена;
- build только через clean SGDK 2.11 path.

## R1 — финальный результат

Accepted ROM: FIX2.

- source commit `bc858a619de76a1f5c3112859914ea132e9bf7be`;
- GitHub Actions run `34178302167` — SUCCESS;
- ROM 131072 bytes;
- SHA-256 `78f73ba4ccabbca43433735538123de82b0097be9cb2dd5f7704838b103552c7`;
- verifier PASS;
- build A/B byte-identical;
- target MD Emu Games Gen: manual state transitions PASS;
- `ERR:00` PASS;
- `SOAK: PASS 100/100` PASS;
- final `STATE: MAIN_MENU`, `BANK: MENU` PASS;
- final screenshot reached `TRANS:114` with `ERR:00`.

`LAST ERROR: R1_ITEM_NOT_IMPLEMENTED` при `ERR:00` — информационная строка после выбора intentionally locked R1 menu item, а не runtime error.

## Следующее действие

Следующая стадия — **R2 MAIN MENU VISUAL TARGET**. Перед кодом сначала подробно сверить требования R2 с `REBUILD_MASTER_PLAN`, `ACCEPTANCE_GATES`, frozen game design и locked `MAIN_MENU_REFERENCE.png`.

R2 должен изменять только то, что входит в его scope. Не переносить gameplay/R3+, не использовать старый DEV и не копировать Granada assets/code.
