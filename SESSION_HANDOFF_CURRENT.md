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

Target acceptance:

- manual MENU / TEST_BATTLE / GARAGE transitions PASS;
- `ERR:00`;
- `SOAK: PASS 100/100`;
- final `STATE: MAIN_MENU`, `BANK: MENU`;
- user continued to `TRANS:114` with `ERR:00`.

Полный результат: `tests/r1/R1_ACCEPTANCE_RESULT.md`.

## 4. Текущий milestone — R2 MAIN MENU VISUAL TARGET

Статус: **BUILD/CI PASS / TARGET ACCEPTANCE PENDING**.

R2 реализован поверх принятого R1 core. R3 не начат.

### R2 visual scope

В текущем ROM есть:

- native-resolution 320×224 menu art;
- крупный MODERN TANKS logo;
- battlefield background;
- steel-frame visual language;
- канонические пункты `ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ`;
- tank-class strip;
- stats preview;
- mini-map preview;
- animated/pulsing selector;
- subtle scripted moving tank на battlefield;
- переход ИГРАТЬ → TEST_BATTLE shell;
- переход ГАРАЖ → GARAGE shell;
- возврат B;
- меню unload/reload использует принятую R1 blanked VDP transaction и CRAM/sprite self-check.

STATISTICS и OPTIONS в R2 остаются visual-only: полноценные meta-state относятся к более поздней стадии. Это не меняет frozen design.

## 5. R2 art pipeline

Locked `references/MAIN_MENU_REFERENCE.png` не изменён, не перекодирован и не встроен в ROM.

Проектный R2 art создаётся детерминированно скриптом:

`sgdk/tools/generate_r2_art.py`

Скрипт рисует меню непосредственно в native Mega Drive resolution и создаёт indexed PNG для SGDK ResComp. Это также исключает ненадёжную бинарную передачу PNG через connector.

Granada assets/code в R2 отсутствуют. Старая DEV-линия отсутствует.

## 6. R2 CI — PASS

Финальный build:

- build commit: `49ebfa6087cf8c39c313fa305cd48892509f0948`;
- GitHub Actions run: `34180963691`;
- job `build-r2`: SUCCESS;
- generated-art validation: PASS;
- source/locked-art contract: PASS;
- SGDK 2.11 build A: PASS;
- SGDK 2.11 build B: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM audit: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `dda9c3f62769371f9888b171a1ac2ac6374b886dead551db9fd3de657cbb539f`;
- header checksum: `0x031D`;
- required checksum: `0x031D`;
- SGDK full-ROM XOR-fold: `0x0000`.

Resource budget:

- conservative project-owned menu pattern worst case: 444 tiles / 14,208 bytes;
- conservative 44 KiB project pattern ceiling free: 30,848 bytes;
- project VDP sprite payload: 0; moving tank uses Plane A tiles.

Подробности: `tests/r2/R2_BUILD_STATUS.md` и `sgdk/res/R2_RESOURCE_BUDGET.md`.

## 7. Следующий обязательный шаг

Только target-проверка R2 ROM в MD Emu Games Gen по `tests/r2/R2_ACCEPTANCE_CHECKLIST.md`.

Проверить:

- visual composition относительно `references/MAIN_MENU_REFERENCE.png`;
- selector Up/Down;
- selector pulse и moving background tank;
- ИГРАТЬ → TEST_BATTLE → B → MENU;
- ГАРАЖ → GARAGE → B → MENU;
- после нескольких переходов `ERR:00`;
- отсутствие VRAM/palette/sprite corruption.

## 8. Строгий запрет

**R2 пока НЕ ACCEPTED. R3 НЕ НАЧИНАТЬ.**

R3 разрешается только после прямого подтверждения владельцем, что R2 принят.
