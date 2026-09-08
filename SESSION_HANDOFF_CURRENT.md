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

R0 закрыт 2026-09-08 прямым решением владельца проекта после фактического target-теста.

### CI

- GitHub Actions run: `34175976629`;
- commit: `10bd881926743a88c8a211919b176505cc95054c`;
- ROM size: `131072` bytes;
- SHA-256: `1b5de098a33a0ac54256c8680acc0440bdec76ae5c74fa2551bff7050b24ef11`;
- header checksum: `0x5411`;
- SGDK full-ROM XOR-fold: `0x0000`;
- independent verifier: PASS;
- two clean builds: byte-for-byte identical.

### Target test — MD Emu Games Gen / Android

Пользователь лично подтвердил:

- ROM запускается стабильно;
- изображение правильное;
- R0A PASS;
- R0B PASS;
- D-Pad PASS;
- A/B/C/START PASS.

X/Y/Z не считаются ошибкой: R0 принудительно использует `JOY_SUPPORT_3BTN`, а 6-button input не входит в scope R0.

Итог: **R0 полностью ACCEPTED и больше не блокирует R1**.

## 3. Текущий milestone — R1 Core / State Machine — FUNCTIONAL TARGET PASS / CLEANUP RETEST PENDING

R1 реализуется строго по `plan/REBUILD_MASTER_PLAN.md`.

### Scope

- BOOT;
- TITLE;
- MAIN_MENU shell;
- TEST_BATTLE shell;
- GARAGE shell;
- state transitions;
- 3-button input abstraction;
- NTSC/PAL timing;
- debug/error layer;
- clean state enter/leave hooks;
- resource bank load/unload API.

### Реализация

`sgdk/src/main.c` — clean SGDK R1 core-shell без старого DEV-кода и без Granada assets/code.

В нём:

- явный `GameState`;
- явный `ResourceBank`;
- `InputState { held, pressed, released }`;
- `JOY_SUPPORT_3BTN`;
- 60 Hz logical clock с PAL compensation;
- state enter/leave hooks;
- bank unload очищает BG_A/B, WINDOW, scroll, CRAM и VDP sprites;
- palette/sprite self-checks;
- debug overlay;
- встроенный 100-transition soak по кнопке C.

## 4. Первый target-тест R1

Пользователь запустил первый R1 ROM в MD Emu Games Gen и сообщил: **«Отлично работает»**. На предоставленных screenshots TEST_BATTLE и GARAGE визуально работают и переключение state/bank происходит корректно.

Однако debug overlay выявил формальный gate defect:

- TEST_BATTLE: `TRANS:003 ERR:03`, `LAST ERROR: PALETTE_RESIDUE`;
- GARAGE: `TRANS:005 ERR:05`, `LAST ERROR: PALETTE_RESIDUE`.

То есть функциональная часть R1 прошла, но R1 нельзя было закрыть: gate требует `ERR:00` и отсутствие palette residue.

Подробная фиксация: `tests/r1/R1_TARGET_TEST_2026-09-08.md`.

## 5. R1 CRAM cleanup fix

Причина: после CPU-записи CRAM код немедленно переключал VDP на CRAM readback без явного ожидания опустошения FIFO. На target emulator это давало ложный `PALETTE_RESIDUE` на каждом state unload.

Исправлено:

- единая очистка всех 64 CRAM entries через `PAL_setColors(0, palette_black, 64, CPU)`;
- `VDP_waitFIFOEmpty()` после записи;
- дополнительный `VDP_waitFIFOEmpty()` перед `PAL_getColors()`.

Fix commit: `16ea3ccad96b51e0514e88076ee6c4f00b752098`.

### CI fix build

GitHub Actions run: `34177478564` — **SUCCESS**.

- build A/B: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM audit: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `0798b55ea287dc991a896ae67c94d1afa8640a50f85366ab765809ff316cc713`;
- header checksum: `0x8B8E`;
- required checksum: `0x8B8E`;
- SGDK full-ROM XOR-fold: `0x0000`;
- artifact: `Modern_Tanks_R1_Core_Menu`.

## 6. Soak gate / следующий target-test

Кнопка C в MAIN_MENU запускает 100 переходов — 25 циклов:

`MENU → TEST_BATTLE → MENU → GARAGE → MENU`

Обязательный итог нового ROM:

- `SOAK: PASS 100/100`;
- `ERR:00`;
- `STATE: MAIN_MENU`;
- `BANK: MENU`;
- ручной input продолжает работать после soak.

До подтверждения этого результата R1 остаётся **TARGET RETEST PENDING**.

## 7. Что намеренно НЕ входит в R1

- финальная графика меню из `MAIN_MENU_REFERENCE.png`;
- battlefield renderer/HUD;
- tank art;
- region/world tiles;
- gameplay/AI/projectiles;
- SRAM;
- audio.

Это последующие стадии. Scope R1 не расширять.

## 8. Visual references — LOCKED

Исходные SHA-256:

- `COMBAT_REFERENCE.png`: `57985349c3c0eec4c1118ce35988a52181ba6357f24a61a44b6b46721db4d9b5`
- `MAIN_MENU_REFERENCE.png`: `af049be579c56dde8b9239cb1fff11a705167957e17315528fe44d2965592360`
- `TANKS_DETAILED_REFERENCE.png`: `5956e18e6b5d994ec730a37109e8fabd7aec158dd0f71c811a75735947ab07d7`

Они не изменялись.

## 9. Granada

`external_reference/Granada (JU) (REV01) [T+Rus Pirate].zip` используется только как технический ориентир: startup discipline, state/resource paging, VRAM discipline, top-down readability. Никакие Granada assets/code/game rules в Modern Tanks не переносятся.

## 10. Текущий запрет

**R2 НЕ НАЧИНАТЬ.**

Сначала пользователь должен повторно проверить fix ROM в MD Emu Games Gen и подтвердить `ERR:00` + `SOAK: PASS 100/100`. Только после прямого target PASS R1 может быть ACCEPTED/CLOSED.
