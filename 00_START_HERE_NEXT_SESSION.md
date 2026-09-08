# MODERN TANKS — START HERE NEXT SESSION

## Сначала прочитать

1. `SESSION_HANDOFF_CURRENT.md`
2. `plan/REBUILD_MASTER_PLAN.md`
3. `plan/ACCEPTANCE_GATES.md`
4. `tests/r0/R0_ACCEPTANCE_RESULT.md`
5. `tests/r1/R1_ACCEPTANCE_RESULT.md`
6. `tests/r2/R2_BUILD_STATUS.md`
7. `tests/r2/R2_TANK_REFERENCE_FIX.md`
8. `tests/r2/R2_ACCEPTANCE_CHECKLIST.md`
9. `design/GAME_DESIGN_FROZEN.md`

## Текущая точка

- **R0 Hardware Probe — ACCEPTED / CLOSED.**
- **R1 Core / State Machine — ACCEPTED / CLOSED.**
- **R2 Main Menu Visual Target — TANK REFERENCE FIX BUILD/CI PASS / TARGET ACCEPTANCE PENDING.**
- **R3 и далее — BLOCKED до прямого R2 acceptance.**

## Критическая история R2

Первый R2 был отклонён как слишком простой. MAX DETAIL повысил плотность экрана, но владелец отдельно указал, что танки не соответствовали locked `references/TANKS_DETAILED_REFERENCE.png`.

Не возвращаться к упрощённым tank icons.

Текущий candidate — **R2 TANK REFERENCE FIX**.

## Инварианты

- идея Modern Tanks не меняется;
- `design/GAME_DESIGN_FROZEN.md` — game-design truth;
- три PNG reference не изменять/не перекодировать/не заменять;
- `MAIN_MENU_REFERENCE.png` — визуальная цель меню;
- `TANKS_DETAILED_REFERENCE.png` — обязательная цель дизайна танков;
- Granada — только технический образец Mega Drive;
- старая DEV-линия запрещена;
- build только через clean SGDK 2.11 path.

## Текущий R2 build

- build commit `acba3abbf58fd3d1666617d51431c2b5f31eab43`;
- GitHub Actions run `34185523022` — SUCCESS;
- ROM 131072 bytes;
- SHA-256 `5b73a0e9a1d7c8efb28541631cf09580790c0496d7b60634db41543b3ad586d9`;
- header checksum `0x647E`;
- verifier PASS;
- build A/B byte-identical.

В последней коррекции перерисованы T-1…T-4 cards, battlefield tanks и moving 16×16 tank. Требуемый язык: top-down, отдельные tracks, shaped hull, turret, mantlet/barrel, hatch/details и разные class silhouettes.

## Следующее действие

Только проверить текущий R2 ROM в MD Emu Games Gen / на целевой MD-совместимой платформе.

Если танки или общее меню всё ещё не устраивают — продолжать R2. **R3 не начинать.**
