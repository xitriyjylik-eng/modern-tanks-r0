# MODERN TANKS — CURRENT SESSION HANDOFF

Дата состояния: **2026-09-08**.

## 1. Жёсткие инварианты

1. Идею, механику и идентичность Modern Tanks не менять.
2. `design/GAME_DESIGN_FROZEN.md` — источник истины по игре.
3. Три PNG в `references/` не изменять, не перекодировать и не заменять.
4. Granada использовать только как технический образец Mega Drive; не копировать её графику, код, карты, музыку или игровые правила.
5. Старую DEV-линию, DEV ROM, Python opcode-emitter и старый DEV master-plan не возвращать.
6. Техническая линия только R0–R12 clean rebuild на SGDK 2.11.

## 2. R0 Hardware Probe — ACCEPTED / CLOSED

R0 закрыт владельцем проекта после фактической проверки в MD Emu Games Gen на Android.

Подтверждено: стабильный запуск, правильное изображение, R0A PASS, R0B PASS, D-Pad и A/B/C/START PASS. X/Y/Z не входят в scope обязательного 3-button path.

CI R0:

- run `34175976629`;
- commit `10bd881926743a88c8a211919b176505cc95054c`;
- ROM 131072 bytes;
- SHA-256 `1b5de098a33a0ac54256c8680acc0440bdec76ae5c74fa2551bff7050b24ef11`;
- verifier PASS.

## 3. R1 Core / State Machine — ACCEPTED / CLOSED

Финальный accepted source: FIX2.

- source commit: `bc858a619de76a1f5c3112859914ea132e9bf7be`;
- GitHub Actions run: `34178302167` — SUCCESS;
- ROM: 131072 bytes;
- SHA-256: `78f73ba4ccabbca43433735538123de82b0097be9cb2dd5f7704838b103552c7`;
- header checksum: `0xAC94`;
- two clean SGDK 2.11 builds: byte-identical;
- independent ROM verifier: PASS.

### R1 scope, который теперь считается доказанным

- BOOT;
- TITLE;
- MAIN_MENU shell;
- TEST_BATTLE shell;
- GARAGE shell;
- state transitions;
- 3-button input abstraction;
- NTSC/PAL timing;
- debug/error layer;
- state enter/leave hooks;
- ResourceBank load/unload API;
- cleanup BG_A/B, WINDOW, scroll, sprites и CRAM;
- 100-transition soak.

### История palette self-check

Исходный R1 и FIX1 функционально работали, но target screenshots показывали ложный `PALETTE_RESIDUE` при state teardown. FIX2 перевёл teardown/setup в короткую blanked VDP transaction, после чего defect исчез.

### Финальный target-test FIX2

Владелец проекта проверил FIX2 в MD Emu Games Gen на Android и предоставил screenshots.

Подтверждено:

- ручные переходы MENU / TEST_BATTLE / GARAGE работают;
- `ERR:00` после ручных переходов;
- `SOAK: PASS 100/100`;
- после soak `STATE: MAIN_MENU`;
- после soak `BANK: MENU`;
- после soak `ERR:00`;
- финальный screenshot показывает `TRANS:114`, то есть после автоматических 100 переходов ручная работа продолжалась без накопления ошибок.

`LAST ERROR: R1_ITEM_NOT_IMPLEMENTED` при `ERR:00` не является runtime error: это информационная строка после нажатия на намеренно заблокированный R1-пункт `STATISTICS` или `OPTIONS`; `errorCount` она не увеличивает.

Полный результат: `tests/r1/R1_ACCEPTANCE_RESULT.md`.

## 4. Текущий milestone — R2 MAIN MENU VISUAL TARGET

Статус: **UNLOCKED / NOT STARTED**.

R2 разрешён только потому, что R1 теперь ACCEPTED/CLOSED. В acceptance commit R2 код/графика не добавлялись.

Перед началом R2 обязательно перечитать:

- `plan/REBUILD_MASTER_PLAN.md`, раздел R2;
- `plan/ACCEPTANCE_GATES.md`;
- `design/GAME_DESIGN_FROZEN.md`;
- `references/MAIN_MENU_REFERENCE.png` как locked visual target;
- technical документы по Mega Drive/VRAM/Granada.

R2 должен делать визуальное меню Modern Tanks максимально близким по композиции к `MAIN_MENU_REFERENCE.png`, но не менять game-design/navigation semantics. Granada остаётся только техническим образцом.

## 5. Что не трогать

- три PNG reference — LOCKED;
- `design/GAME_DESIGN_FROZEN.md` — не менять смысл игры;
- Granada — только technical reference;
- старый DEV — запрещён.

Следующая работа должна начинаться строго с анализа требований R2, без перехода к R3 до отдельного acceptance R2.
