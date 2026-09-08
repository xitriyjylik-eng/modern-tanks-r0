# MODERN TANKS — START HERE NEXT SESSION

## Сначала прочитать

1. `SESSION_HANDOFF_CURRENT.md`
2. `plan/REBUILD_MASTER_PLAN.md`
3. `plan/ACCEPTANCE_GATES.md`
4. `tests/r0/R0_ACCEPTANCE_RESULT.md`
5. `tests/r1/R1_ACCEPTANCE_RESULT.md`
6. `tests/r2/R2_MAX_DETAIL_BUILD_STATUS.md`
7. `tests/r2/R2_ACCEPTANCE_CHECKLIST.md`
8. `design/GAME_DESIGN_FROZEN.md`

## Текущая точка

- **R0 Hardware Probe — ACCEPTED / CLOSED.**
- **R1 Core / State Machine — ACCEPTED / CLOSED.**
- **R2 Main Menu Visual Target — MAX DETAIL BUILD/CI PASS / TARGET ACCEPTANCE PENDING.**
- **R3 и далее — BLOCKED до прямого R2 acceptance.**

## История R2

Первый R2 candidate и Visual Rework 1 были технически рабочими, но владелец проекта визуально отклонил их как слишком упрощённые относительно locked `references/MAIN_MENU_REFERENCE.png`. Не возвращаться к этим вариантам.

Текущий candidate — **R2 MAX DETAIL**.

## Целевая платформа

Игра остаётся настоящим SGDK/Mega Drive ROM. SG800 рассматривается как MD/Mega Drive emulator host; HDMI/4K относится к выводу/масштабированию, а не к 4K framebuffer игры. Тот же `.bin` должен запускаться на SG800 и MD/Genesis-эмуляторах ПК.

## Инварианты

- идея Modern Tanks не меняется;
- `design/GAME_DESIGN_FROZEN.md` — game-design truth;
- три PNG reference не изменять/не перекодировать/не заменять;
- Granada — только технический образец Mega Drive;
- старая DEV-линия запрещена;
- build только через clean SGDK 2.11 path.

## R2 MAX DETAIL — текущий build

- source commit `53ef4dba355abbad5ad052ef1ee35345e17006bf`;
- GitHub Actions run `34184514661` — SUCCESS;
- ROM 131072 bytes;
- SHA-256 `52b0395fb023ebdaa08ca7e03152fa6b2040ed5c9a6b997509c618c4a9e95eba`;
- header checksum `0xE671`;
- independent verifier PASS;
- build A/B byte-identical;
- exact generated-art SHA checks PASS.

MAX DETAIL использует существенно более плотный нативный 320×224 pixel-art: custom pixel font, крупный многослойный logo, organic battlefield, winding river/shoreline, forests, roads, bridges, fortifications, craters, multiple tanks, shells/flashes/smoke, detailed T-1…T-4 cards, segmented stats и minimap.

Канонические main-menu semantics остаются frozen: `ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ`. Прокачка остаётся внутри ГАРАЖА, миссии — внутри ИГРАТЬ.

Locked `MAIN_MENU_REFERENCE.png` не изменён и не встроен.

## Следующее действие

Только проверить **R2 MAX DETAIL ROM** на целевой платформе и в MD Emu Games Gen по `tests/r2/R2_ACCEPTANCE_CHECKLIST.md`.

Если визуально не устраивает — продолжать R2, не начинать R3.

**R3 не начинать до прямого подтверждения владельца, что R2 принят.**
