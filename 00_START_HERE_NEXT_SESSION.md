# MODERN TANKS — START HERE NEXT SESSION

## Сначала прочитать

1. `SESSION_HANDOFF_CURRENT.md`
2. `plan/REBUILD_MASTER_PLAN.md`
3. `plan/ACCEPTANCE_GATES.md`
4. `tests/r0/R0_ACCEPTANCE_RESULT.md`
5. `tests/r1/R1_ACCEPTANCE_RESULT.md`
6. `tests/r2/R2_BUILD_STATUS.md`
7. `tests/r2/R2_ACCEPTANCE_CHECKLIST.md`

## Текущая точка

- **R0 — ACCEPTED / CLOSED.**
- **R1 — ACCEPTED / CLOSED.**
- **R2 — FOCUSED MENU / TANK REFERENCE REWORK BUILD/CI PASS / TARGET PENDING.**
- **R3+ — BLOCKED до прямого R2 acceptance.**

## Последнее решение владельца

Не возвращать нижний `T-1..T-4 / параметры / карта` HUD в главное меню. Он удалён как нефункциональный и перегружающий экран.

Не возвращать декоративный движущийся танк. Он удалён из runtime и из resources.

Главное меню теперь использует всё нижнее пространство как продолжение battlefield art. Tank/class selection относится к GARAGE; map/mission context — к соответствующим игровым экранам.

## Tank art direction

`TANKS_DETAILED_REFERENCE.png` остаётся обязательным образцом. Не использовать простые прямоугольные tank icons.

Текущий R2 содержит вручную нарисованный top-down renderer: отдельные tracks, shaped hull, turret/ring, mantlet + long gun, hatch/details и разные пропорции T-1/T-2/T-3/T-4.

Locked PNG не изменять и не встраивать как готовую текстуру.

## Текущий tested build

- GitHub Actions run `34186426856` — SUCCESS;
- tested commit `831cd8348997cdb13e82cfc8422c6748f3e0e0b1`;
- ROM 131072 bytes;
- SHA-256 `d4baf97f7884ae0e91be0bc599d11046959fae88407c2db7235dd37726dc47f4`;
- header checksum `0x6DF1`;
- verifier PASS;
- build A/B byte-identical;
- conservative patterns 31,168 bytes, 13,888 bytes free vs project 44 KiB ceiling.

## Следующее действие

Только проверить текущий R2 ROM визуально и функционально. Если не устраивает — продолжать R2.

**R3 НЕ НАЧИНАТЬ.**
