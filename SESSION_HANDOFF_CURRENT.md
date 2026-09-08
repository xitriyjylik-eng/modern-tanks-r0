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

## 3. Текущий milestone — R1 Core / State Machine

Статус: **FUNCTIONAL TARGET PASS / FIX2 CI PASS / TARGET RETEST PENDING**.

R1 scope:

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
- 100-transition soak.

R2 art/gameplay не входят в R1.

## 4. Что пользователь уже подтвердил по R1

В MD Emu Games Gen функционально работают:

- MAIN_MENU navigation;
- вход в TEST_BATTLE;
- возврат B;
- вход в GARAGE;
- возврат B;
- state/bank switching;
- rendering без видимого crash/corruption.

Но два target test выявили внутренний `PALETTE_RESIDUE` self-check.

### Исходный R1

- TEST_BATTLE: `TRANS:003 ERR:03`;
- GARAGE: `TRANS:005 ERR:05`.

### FIX1

После FIFO-drain исправления defect сохранился:

- TEST_BATTLE: `TRANS:007 ERR:07`;
- GARAGE: `TRANS:009 ERR:09`.

Значит проблема была не в пользовательском управлении и не в видимой картинке. Ненадёжной была сама CRAM cleanup/readback транзакция при active display.

Полная история: `tests/r1/R1_TARGET_TEST_2026-09-08.md`.

## 5. FIX2

Source commit: `bc858a619de76a1f5c3112859914ea132e9bf7be`.

State transition теперь выполняется как blanked video transaction:

1. `VDP_setEnable(FALSE)`;
2. FIFO drain;
3. state leave;
4. BG_A/B/WINDOW + scroll + VDP sprites teardown;
5. all 64 CRAM entries → black;
6. CRAM readback with interrupts masked;
7. next bank load + state draw;
8. FIFO drain;
9. `VDP_setEnable(TRUE)`.

Это соответствует SGDK-подходу к безопасным крупным video-memory reset operations: не пытаться проверять CRAM во время active visible scanout.

### FIX2 CI

GitHub Actions run `34178302167` — **SUCCESS**.

- source contract: PASS;
- build A/B: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM verifier: PASS;
- ROM size: `131072` bytes;
- SHA-256: `78f73ba4ccabbca43433735538123de82b0097be9cb2dd5f7704838b103552c7`;
- header checksum: `0xAC94`;
- required checksum: `0xAC94`;
- full-ROM XOR-fold: `0x0000`.

## 6. Следующий обязательный target test

Проверить только FIX2 ROM.

Сначала несколько ручных переходов:

`MAIN_MENU → TEST_BATTLE → MAIN_MENU → GARAGE → MAIN_MENU`.

`ERR` должен оставаться `00`.

Затем C в MAIN_MENU запускает 100-transition soak. Обязательный финал:

- `SOAK: PASS 100/100`;
- `ERR:00`;
- `STATE: MAIN_MENU`;
- `BANK: MENU`;
- manual input продолжает работать.

До этого R1 **НЕ ACCEPTED**.

## 7. Что не трогать

- три PNG reference — LOCKED;
- `design/GAME_DESIGN_FROZEN.md` — не менять смысл игры;
- Granada — только technical reference;
- старый DEV — запрещён;
- R2 — не начинать до clean R1 target PASS.
