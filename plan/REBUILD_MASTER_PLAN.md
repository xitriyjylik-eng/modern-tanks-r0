# MODERN TANKS — REBUILD MASTER PLAN

## 0. Назначение

Это единственный актуальный технический master-plan clean rebuild.

Старая DEV-линия, DEV ROM, Python opcode-emitter и старый DEV master-plan запрещены.

Проект разделён на две истины:

1. **Что представляет собой игра** — `design/GAME_DESIGN_FROZEN.md`.
2. **Как она реализуется на Mega Drive** — этот rebuild-plan и `technical/`.

Granada используется только как технический ориентир. Три PNG в `references/` остаются locked visual references и не изменяются.

---

# 1. Общая стратегия

Проект развивается вертикальными, реально запускаемыми стадиями R0–R12.

Каждая стадия имеет:

- конкретный ROM scope;
- аппаратный/resource budget;
- acceptance gate;
- обязательный target-test в MD Emu Games Gen пользователя;
- desktop-emulator test, когда он доступен в текущем цикле;
- запрет перехода к следующей стадии до PASS текущей.

## Текущий статус — 2026-09-08

- **R0 HARDWARE PROBE — ACCEPTED / CLOSED.**
- **R1 CORE / STATE MACHINE — ACCEPTED / CLOSED.** Финальный FIX2 прошёл CI и target gate: manual transitions PASS, `ERR:00`, `SOAK: PASS 100/100`, пользователь продолжил до `TRANS:114` без ошибок.
- **R2 MAIN MENU VISUAL TARGET — BUILD/CI PASS / TARGET ACCEPTANCE PENDING.** R2 реализован и воспроизводимо собран; ROM передаётся владельцу для visual/target проверки.
- **R3 и далее — BLOCKED** до прямого R2 acceptance.

Идея Modern Tanks не меняется. Granada не является donor-ROM.

---

# 2. R0 — HARDWARE PROBE

**Статус: ACCEPTED / CLOSED — 2026-09-08.**

## Цель

Доказать, что clean SGDK toolchain создаёт ROM, стабильно работающий на целевом Android emulator.

## Scope

- стандартный SGDK startup;
- H40 320×224;
- диагностический фон/text;
- D-Pad;
- A/B/C/START;
- frame counter;
- никакой игровой логики;
- никакого старого DEV-кода;
- никакого SRAM/audio/map streaming.

## Gate R0

PASS при стабильном изображении/запуске, рабочем 3-button input и отсутствии crash screen. X/Y/Z не являются требованием R0.

Полный результат: `tests/r0/R0_ACCEPTANCE_RESULT.md`.

---

# 3. R1 — CORE / STATE MACHINE

**Статус: ACCEPTED / CLOSED — 2026-09-08.**

## Реализовано

- BOOT;
- TITLE;
- MAIN_MENU shell;
- TEST_BATTLE shell;
- GARAGE shell;
- state transitions;
- 3-button input abstraction;
- PAL/NTSC timing;
- error/debug layer;
- state enter/leave hooks;
- ResourceBank load/unload API;
- deterministic plane/sprite/CRAM cleanup;
- blanked VDP transition transaction;
- 100-transition soak.

## Финальный accepted build

- source commit `bc858a619de76a1f5c3112859914ea132e9bf7be`;
- Actions run `34178302167`;
- ROM size `131072` bytes;
- SHA-256 `78f73ba4ccabbca43433735538123de82b0097be9cb2dd5f7704838b103552c7`;
- checksum `0xAC94`;
- audit PASS;
- target PASS.

## Gate R1

100 переходов `MENU → TEST_BATTLE → MENU → GARAGE → MENU` без VRAM corruption, leaked sprites, зависаний, потерянного input и palette residue.

Фактический target-result: `SOAK: PASS 100/100`, `ERR:00`, final `STATE: MAIN_MENU`, `BANK: MENU`; ручная работа продолжена до `TRANS:114` при `ERR:00`.

Полный результат: `tests/r1/R1_ACCEPTANCE_RESULT.md`.

---

# 4. R2 — MAIN MENU VISUAL TARGET

**Статус: BUILD/CI PASS / TARGET ACCEPTANCE PENDING.**

## Источник истины

`references/MAIN_MENU_REFERENCE.png` — locked visual target.

Reference нельзя изменять, перекодировать, встраивать в ROM или автоматически уменьшать как готовый экран.

`design/GAME_DESIGN_FROZEN.md` остаётся источником истины по navigation/game semantics.

## Реализовано в текущем R2

- native-resolution 320×224 menu art;
- крупный MODERN TANKS logo;
- battlefield background;
- steel-frame visual language;
- четыре канонических русских пункта:
  1. ИГРАТЬ
  2. ГАРАЖ
  3. СТАТИСТИКА
  4. НАСТРОЙКИ
- tank-class strip;
- stats preview;
- mini-map preview;
- selector animation/pulse;
- subtle scripted moving tank на фоне;
- accepted R1 state/resource-bank core сохранён;
- ИГРАТЬ → TEST_BATTLE shell;
- ГАРАЖ → GARAGE shell;
- B → возврат в menu;
- menu bank teardown/reload наследует accepted R1 cleanup self-check.

STATISTICS/OPTIONS в R2 являются визуальными пунктами без полноценного meta-state. Полная meta-логика относится к R9.

## Art pipeline

R2 art создаётся детерминированно `sgdk/tools/generate_r2_art.py` непосредственно в native Mega Drive resolution и затем компилируется SGDK ResComp.

Это не копия Granada и не downscale locked reference.

## R2 CI build

- build commit `49ebfa6087cf8c39c313fa305cd48892509f0948`;
- GitHub Actions run `34180963691` — SUCCESS;
- SGDK 2.11;
- native art generation/validation PASS;
- locked-art/source contract PASS;
- build A/B PASS;
- A/B byte-for-byte identical;
- independent ROM audit PASS;
- ROM size `131072` bytes;
- SHA-256 `dda9c3f62769371f9888b171a1ac2ac6374b886dead551db9fd3de657cbb539f`;
- header checksum `0x031D`;
- full-ROM XOR-fold `0x0000`.

## Resource budget

- conservative project-owned menu pattern worst case: 444 tiles / 14,208 bytes;
- 30,848 bytes free относительно conservative 44 KiB project pattern ceiling;
- project VDP sprite payload: 0; scripted tank uses Plane A tiles.

Подробности: `sgdk/res/R2_RESOURCE_BUDGET.md`.

## Gate R2

PASS только после target test владельцем:

- visual comparison с `MAIN_MENU_REFERENCE.png` по композиции и visual language;
- нет пустых placeholder-панелей;
- нет dirty auto-downscale graphics;
- selector/navigation/animation работают;
- menu bank полностью выгружается при переходе в TEST_BATTLE/GARAGE shell;
- после повторных unload/reload циклов `ERR:00`;
- нет VRAM/palette/sprite corruption;
- visual result прямо принят владельцем.

Checklist: `tests/r2/R2_ACCEPTANCE_CHECKLIST.md`.

**R3 не начинать до R2 acceptance.**

---

# 5. R3 — BATTLE RENDERER / HUD

**Статус: BLOCKED.**

## Источник истины

`references/COMBAT_REFERENCE.png`

## Геометрия

- battlefield 224×192;
- right HUD 96×192;
- event log 320×32;
- camera center 112×96.

## Реализовать после R2 PASS

- Plane B base world;
- Plane A upper world;
- Window L-shape для HUD + bottom log;
- camera scrolling;
- map edge streaming;
- minimap framework;
- HUD panels/bars/icons;
- event log framework;
- clipping world sprites to battlefield presentation zone.

## Gate R3

- camera не использует центр 160px;
- HUD никогда не скроллится;
- world sprites не рисуются поверх HUD;
- 10 минут scrolling без tile corruption;
- все четыре направления scrolling PASS.

---

# 6. R4 — TANK ART / PLAYER CLASSES

## Источник истины

`references/TANKS_DETAILED_REFERENCE.png`

## Реализовать T-1…T-8

Каждый tank:

- отдельный 32×32 combat sprite language;
- 4 направления;
- разные корпус/башня/пушка/гусеницы;
- light/shadow/material ramps;
- читаемая роль по силуэту;
- 2-frame track animation где budget допускает;
- combat hitbox логический и не равен визуальной рамке.

## Запрещено

- брать большой reference crop и просто уменьшать до 32×32;
- различать классы только цветом;
- держать все анимации всех восьми tank в VRAM одновременно.

## Gate R4

- 8 классов различимы в grayscale/silhouette test;
- selected tank load/unload без corruption;
- tank не перекрывает HUD;
- sprite/scanline budgets PASS.

---

# 7. R5 — REGION 1 / WORLD FOUNDATION

## Реализовать

Region 1 «Зелёный рубеж»:

- grass families;
- soil;
- roads;
- water + shoreline;
- forest clusters;
- brick;
- steel/concrete;
- bridge;
- ruins;
- craters/debris;
- logical metatile properties;
- destructible stages;
- base/object layer;
- upper/cover layer.

## Map architecture

Большой map остаётся 16×16 logical-metatile based. VDP хранит только текущую 64×32 tile viewport/ring.

## Gate R5

- 1024×1024 test map полностью проходится;
- нет повторяющегося ковра из одного тайла;
- shoreline/road edges связны;
- collision не зависит от декоративного варианта;
- разрушение меняет graphics + logical state корректно.

---

# 8. R6 — COMBAT / ENEMIES / MISSION VERTICAL SLICE

## Перенести из frozen design

- movement;
- shooting;
- projectile pool;
- armor direction;
- damage;
- enemy archetypes;
- AI state machine;
- objectives;
- base/reserves;
- bonuses;
- first mission slice.

Только enemy classes текущей миссии загружаются в VRAM.

## Vertical slice

`MENU → CAMPAIGN/BRIEFING → TANK SELECT → MISSION → RESULTS → SAVE STUB → MENU`

## Gate R6

- mission можно пройти и проиграть;
- нет новых механик вне frozen design;
- AI не телепортируется и не знает игрока без detection;
- pools имеют безопасное переполнение;
- 30 минут stress test без crash.

---

# 9. R7 — REGIONS 2–5

По очереди:

1. Desert Line;
2. Iron Belt;
3. Northern Front;
4. Central Fortress.

Каждый регион получает отдельный настоящий tileset/palette bank, а не перекрашенную копию Region 1.

## Gate R7

Для каждого региона:

- собственный visual identity;
- отдельные edges/corners/transitions;
- VRAM report;
- scrolling test;
- mission object test;
- no palette residue при смене региона.

---

# 10. R8 — BOSSES / EFFECTS / WEATHER

## Bosses

- Goliath;
- Thunder;
- Iron Serpent;
- Tempest;
- Leviathan.

Boss graphics грузятся отдельным BOSS BANK.

## Effects

- projectile types;
- muzzle flash;
- ricochet;
- 32×32+ explosions;
- smoke;
- debris;
- scorch/crater decals;
- rain/dust/snow/ash/sparks.

## Gate R8

- boss weak points работают по frozen design;
- крупный boss не превышает scanline sprite limits;
- effects не ломают читаемость HUD;
- weather не съедает gameplay sprite budget.

---

# 11. R9 — META SYSTEMS

Перенести:

- campaign map;
- briefing;
- garage;
- tank select;
- upgrades;
- statistics;
- options;
- results;
- difficulty;
- ranks;
- secrets/unlocks;
- post-campaign modes из frozen design.

## Gate R9

Полный цикл без сохранения:

`BOOT → MENU → GARAGE → CAMPAIGN → MISSION → RESULTS → GARAGE/MENU`

100 циклов переходов без VRAM/state leakage.

---

# 12. R10 — SRAM

Реализовать frozen schema:

- 3 profiles;
- A/B copies;
- MAGIC;
- VERSION;
- SEQUENCE;
- DATA;
- CHECKSUM;
- recovery from one damaged copy;
- explicit empty/corrupt handling.

## Gate R10

Автоматические тесты:

- normal save/load;
- A corrupted;
- B corrupted;
- both corrupted;
- interrupted save simulation;
- version migration scaffold.

---

# 13. R11 — AUDIO

Только после стабильного renderer/gameplay.

- XGM2/YM2612 music;
- PSG/PCM SFX по необходимости;
- menu/garage/5 regions/boss/final/victory/defeat themes;
- weapon differentiation;
- engine loop;
- priority rules so critical SFX remain audible.

## Gate R11

- нет зависших нот;
- нет Z80 bus corruption;
- SFX не ломают музыку;
- audio stress test + rapid state transitions PASS.

---

# 14. R12 — QA / RELEASE CANDIDATE

## Emulator matrix

Минимум:

- MD Emu Games Gen пользователя;
- BlastEm;
- Genesis Plus GX;
- PicoDrive.

По возможности real hardware / flash cart.

## Проверки

- NTSC/PAL timing;
- 3-button mandatory controls;
- 6-button compatibility;
- all states;
- all regions;
- bosses;
- save/load;
- long-session test;
- sprite limits;
- DMA budget;
- SRAM corruption recovery;
- audio;
- reset/soft reset;
- checksum/header.

Только после этого кандидат может называться release candidate.

---

# 15. Правило каждого нового build

Новый ROM разрешено отдавать пользователю только если вместе с ним существует автоматический отчёт:

- toolchain/version;
- ROM SHA-256;
- header/checksum;
- current stage;
- features intentionally included;
- features intentionally absent;
- VRAM budget;
- sprite budget;
- DMA worst case;
- tested emulator list;
- PASS/FAIL gate.

Checksum сам по себе не является доказательством работоспособности.

---

# 16. Текущий следующий практический шаг

R0 и R1 закрыты как **ACCEPTED / CLOSED**.

R2 уже реализован и имеет **BUILD/CI PASS**, но ещё не принят на target.

Следующий шаг — только запустить R2 ROM в MD Emu Games Gen и пройти `tests/r2/R2_ACCEPTANCE_CHECKLIST.md`.

Если visual target или runtime gate R2 не устраивает, исправлять только R2.

Идею Modern Tanks не менять, три PNG не изменять, Granada использовать только как технический образец, старый DEV не возвращать.

**R3 остаётся запрещён до прямого подтверждения владельца, что R2 принят.**
