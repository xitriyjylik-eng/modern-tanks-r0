# MODERN TANKS — START HERE NEXT SESSION

## Сначала прочитать

1. `SESSION_HANDOFF_CURRENT.md`
2. `plan/REBUILD_MASTER_PLAN.md`
3. `plan/ACCEPTANCE_GATES.md`
4. `tests/r0/R0_ACCEPTANCE_RESULT.md`
5. `tests/r1/R1_BUILD_STATUS.md`
6. `tests/r1/R1_ACCEPTANCE_CHECKLIST.md`
7. `tests/r1/R1_TARGET_TEST_2026-09-08.md`

## Текущая точка

- **R0 Hardware Probe — ACCEPTED / CLOSED.**
- **R1 Core / State Machine — FUNCTIONAL TARGET PASS / FIX2 CI PASS / TARGET RETEST PENDING.**
- **R2 — BLOCKED до clean R1 target PASS.**

## Инварианты

- идея Modern Tanks не меняется;
- `design/GAME_DESIGN_FROZEN.md` — game-design truth;
- три PNG reference не изменять/не перекодировать/не заменять;
- Granada — только технический образец Mega Drive;
- старая DEV-линия запрещена;
- build только через clean SGDK 2.11 path.

## Почему R1 ещё не закрыт

Пользователь уже подтвердил, что меню, TEST_BATTLE, GARAGE, возвраты и rendering работают. Но debug self-check дважды показал `PALETTE_RESIDUE`.

FIX1 с одним FIFO drain не помог: screenshots показали `ERR:07` и `ERR:09`.

## Текущий FIX2

Commit: `bc858a619de76a1f5c3112859914ea132e9bf7be`.

GitHub Actions run `34178302167` — SUCCESS.

- ROM: 131072 bytes;
- SHA-256: `78f73ba4ccabbca43433735538123de82b0097be9cb2dd5f7704838b103552c7`;
- header checksum: `0xAC94`;
- verifier PASS;
- build A/B byte-identical.

FIX2 переводит весь state teardown/setup в короткую blanked VDP transaction: display OFF → cleanup/readback → next bank/draw → display ON.

## Следующее действие

Проверить только FIX2 ROM в MD Emu Games Gen.

1. Несколько раз пройти `MENU → TEST_BATTLE → MENU → GARAGE → MENU` — `ERR` должен оставаться `00`.
2. В MAIN_MENU нажать C.
3. Дождаться `SOAK: PASS 100/100`, `ERR:00`, `STATE: MAIN_MENU`, `BANK: MENU`.
4. После soak снова проверить manual input.

**R2 не начинать до прямого подтверждения пользователя этого clean PASS.**
