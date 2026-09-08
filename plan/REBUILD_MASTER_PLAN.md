# MODERN TANKS — REBUILD MASTER PLAN

## 0. Назначение

Это новый единственный технический master-plan проекта.

Старая DEV-линия, старые ROM и старый master-plan удалены из нового проекта.

Проект теперь разделён на две независимые истины:

1. **Что представляет собой игра** — `design/GAME_DESIGN_FROZEN.md`.
2. **Как она реализуется на Mega Drive** — этот rebuild-plan и `technical/`.

Granada используется как технический ориентир. Три PNG в `references/` остаются художественным ориентиром и не меняются.

---

# 1. Общая стратегия

Нельзя снова строить сразу «полную игру» и проверять только checksum.

Новый проект развивается вертикальными, реально запускаемыми слоями.

Каждая стадия имеет:

- конкретный ROM scope;
- аппаратный budget;
- acceptance gate;
- обязательный тест на целевом Android emulator пользователя;
- тест минимум на одном точном desktop emulator;
- только после PASS разрешается следующая стадия.

Старая DEV-нумерация запрещена. Используется R0–R12.

## Текущий статус стадий — 2026-09-08

- **R0 HARDWARE PROBE — ACCEPTED / CLOSED.** SGDK CI PASS; пользователь лично проверил ROM в MD Emu Games Gen: стабильный запуск, корректное изображение, R0A PASS, R0B PASS, D-Pad и A/B/C/START PASS. X/Y/Z не входят в R0, потому что R0 использует обязательный 3-button path.
- **R1 CORE / STATE MACHINE — ACCEPTED / CLOSED.** Финальный FIX2 прошёл SGDK CI и target gate: ручные переходы PASS, `ERR:00`, `SOAK: PASS 100/100`, финал `STATE: MAIN_MENU`, `BANK: MENU`; после soak пользователь продолжил работу до `TRANS:114` без ошибок.
- **R2 MAIN MENU VISUAL TARGET — UNLOCKED / NOT STARTED.** Это следующая стадия.
- **R3 и далее — BLOCKED** до отдельного acceptance R2.

Старая DEV-линия по-прежнему запрещена. Granada остаётся только техническим образцом.

---

# 2. R0 — HARDWARE PROBE

**Статус: ACCEPTED / CLOSED — 2026-09-08.**

Закрыт прямым решением владельца проекта после фактического теста целевого ROM в MD Emu Games Gen. Исторические детали и результаты сохранены в `tests/r0/`.

## Цель

Доказать, что новый SGDK toolchain формирует ROM, который стабильно запускается в MD Emu Games Gen.

## Содержимое ROM

Только:

- стандартный SGDK startup;
- H40 320×224;
- один фон;
- текст `MODERN TANKS / R0`;
- D-Pad меняет позицию маленького marker;
- A/B/C меняют диагностический индикатор;
- frame counter;
- никакой игровой логики;
- никакого старого кода;
- никакого SRAM/audio/map streaming.

## Gate R0

PASS только если:

- нет красного/одноцветного crash screen;
- изображение стабильно 5+ минут;
- D-Pad/A/B/C/START работают;
- reset/reload работает;
- ROM одинаково запускается в MD Emu Games Gen и минимум одном из BlastEm/Genesis Plus GX/PicoDrive.

При FAIL следующая стадия запрещена.

---

# 3. R1 — CORE / STATE MACHINE

**Статус: ACCEPTED / CLOSED — 2026-09-08.**

## Реализовать

- BOOT;
- TITLE;
- MAIN_MENU shell;
- TEST_BATTLE shell;
- GARAGE shell;
- переходы между состояниями;
- input abstraction 3-button first;
- frame timing NTSC/PAL;
- error/debug layer;
- clean state enter/leave hooks;
- resource bank load/unload API.

### Финальный accepted R1 build

- source commit: `bc858a619de76a1f5c3112859914ea132e9bf7be`;
- GitHub Actions run: `34178302167`;
- build A/B: PASS и byte-for-byte identical;
- ROM audit: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `78f73ba4ccabbca43433735538123de82b0097be9cb2dd5f7704838b103552c7`;
- header checksum: `0xAC94`;
- target acceptance: PASS.

## Gate R1

100 последовательных переходов:

`MENU ↔ TEST_BATTLE ↔ MENU ↔ GARAGE ↔ MENU`

без:

- VRAM corruption;
- leaked sprites;
- зависаний;
- потерянного input;
- palette residue.

Фактический target-result FIX2:

- ручные переходы PASS;
- `ERR:00`;
- `SOAK: PASS 100/100`;
- финал `STATE: MAIN_MENU`;
- финал `BANK: MENU`;
- после soak пользователь продолжил переходы до `TRANS:114` при `ERR:00`.

Полный отчёт: `tests/r1/R1_ACCEPTANCE_RESULT.md`.

---

# 4. R2 — MAIN MENU VISUAL TARGET

**Статус: UNLOCKED / NOT STARTED.**

## Источник истины

`references/MAIN_MENU_REFERENCE.png`

## Реализовать

- крупный MODERN TANKS logo;
- живой battlefield background;
- steel frame language;
- крупные русские пункты меню;
- tank-class strip;
- stats preview;
- mini-map preview;
- subtle scripted background action;
- selector animation.

## Важно

Не менять game-design/navigation semantics из `GAME_DESIGN_FROZEN.md` ради буквального копирования подписей с картинки. Визуальная композиция должна быть максимально близкой, логика игры остаётся Modern Tanks.

## Gate R2

- screen comparison с reference;
- нет пустых placeholder-панелей;
- нет автоматически уменьшенной грязной графики;
- menu bank полностью выгружается при переходе в battle;
- free VRAM зафиксирована в отчёте.

---

# 5. R3 — BATTLE RENDERER / HUD

## Источник истины

`references/COMBAT_REFERENCE.png`

## Геометрия

- battlefield 224×192;
- right HUD 96×192;
- event log 320×32;
- camera center 112×96.

## Реализовать

- Plane B base world;
- Plane A upper world;
- Window L-shape для HUD + bottom log;
- camera scrolling;
- map edge streaming;
- minimap framework;
- HUD panels/bars/icons;
- event log framework;
- clipping sprites to battlefield presentation zone.

## Gate R3

- камера не использует центр 160px;
- HUD никогда не скроллится;
- world sprites не визуализируются поверх HUD;
- 10 минут непрерывного scrolling без tile corruption;
- все четыре направления scrolling проверены.

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
- combat hitbox остаётся логическим и не равен визуальной рамке.

## Запрещено

- брать большой reference crop и просто уменьшать до 32×32;
- различать классы только цветом;
- держать все анимации всех восьми tank в VRAM в battle.

## Gate R4

- все 8 классов различимы в grayscale/silhouette test;
- выбранный tank загружается/выгружается без corruption;
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

Большой map остаётся 16×16 logical metatile based.

VDP хранит только текущую 64×32 tile viewport/ring.

## Gate R5

- 1024×1024 test map полностью проходится;
- нет повторяющегося «ковра» из одного тайла;
- shoreline/road edges выглядят связно;
- collision никогда не зависит от декоративного варианта тайла;
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

## Enemy graphics

Только enemy classes текущей миссии загружаются в VRAM.

## Vertical slice

Mission 1 должна быть полностью проходима:

`MENU → CAMPAIGN/BRIEFING → TANK SELECT → MISSION → RESULTS → SAVE STUB → MENU`

## Gate R6

- миссию можно пройти и проиграть;
- нет новых механик;
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

Каждый регион получает настоящий отдельный tileset/palette bank, а не перекрашенную копию Region 1.

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
- explosion/effects не ломают читаемость HUD;
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
- post-campaign modes, уже описанные в frozen design.

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

По возможности реальное железо / flash cart.

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

Checksum сам по себе никогда больше не считается доказательством работоспособности.

---

# 16. Текущий следующий практический шаг

R0 и R1 закрыты как **ACCEPTED / CLOSED**.

Следующая стадия — **R2 MAIN MENU VISUAL TARGET**.

Перед реализацией R2 сначала подробно сверить его требования с:

- `references/MAIN_MENU_REFERENCE.png`;
- `design/GAME_DESIGN_FROZEN.md`;
- `plan/ACCEPTANCE_GATES.md`;
- техническими документами Mega Drive/VRAM/Granada.

Идею Modern Tanks не менять, три PNG не изменять, Granada использовать только как технический образец, старый DEV не возвращать.

**R3 остаётся запрещён до отдельного подтверждения R2.**
