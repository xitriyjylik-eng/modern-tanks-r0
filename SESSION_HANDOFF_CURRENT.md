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

Статус: **VISUAL REWORK 1 — BUILD/CI PASS / TARGET ACCEPTANCE PENDING**.

R2 реализуется поверх принятого R1 core. R3 не начат и остаётся запрещён до отдельного принятия R2.

### Первый R2 candidate — REJECTED VISUALLY

Первый R2 ROM прошёл SGDK CI и функционально работал, но владелец проекта после запуска в MD Emu Games Gen **не принял его визуально**.

Причина: композиция была слишком упрощённой относительно locked `references/MAIN_MENU_REFERENCE.png`: плоский logo, клетчатый/simple battlefield, слишком широкая центральная panel, условные tank icons и упрощённый bottom HUD.

Этот первый R2 build больше не считать acceptance candidate.

## 5. R2 Visual Rework 1

Новый вариант перерисован в native 320×224 непосредственно для Mega Drive.

В нём есть:

- более узкая reference-like central menu composition;
- dimensional metallic MODERN TANKS logo + steel side wings;
- winding river + shoreline;
- forest clusters;
- grass/dirt variation;
- bridges;
- brick/steel fortifications;
- craters/debris;
- multiple distinct battlefield tanks;
- muzzle flashes, shell traces, explosions, smoke;
- edge signs;
- канонические пункты `ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ`;
- animated selector;
- detailed T-1…T-4 strip;
- segmented stats bars;
- improved minimap;
- subtle scripted moving background tank;
- accepted R1 menu-bank unload/reload and CRAM/sprite cleanup path.

Пункты главного меню не меняются ради буквального копирования reference: по frozen design `ПРОКАЧКА` находится внутри ГАРАЖА, а выбор миссий — внутри ИГРАТЬ.

## 6. R2 art pipeline

Locked `references/MAIN_MENU_REFERENCE.png` не изменён, не перекодирован и не встроен в ROM.

Runtime art детерминированно генерируется скриптом:

`sgdk/tools/generate_r2_art.py`

Скрипт создаёт indexed 320×224 PNG и selector assets непосредственно в Mega Drive-oriented palette layout перед SGDK ResComp. Granada assets/code отсутствуют. Старая DEV-линия отсутствует.

## 7. Visual Rework 1 CI — PASS

Финальный build candidate:

- build commit: `0442a22167097d4b9dc5964301e93fbf2f894234`;
- GitHub Actions run: `34182713358`;
- job `build-r2`: SUCCESS;
- generated-art validation: PASS;
- source/locked-art contract: PASS;
- SGDK 2.11 build A: PASS;
- SGDK 2.11 build B: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM audit: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `5b6a711bc38255793950c0259b2e297d57fa0bc5978a1210fed4e4911619fe98`;
- header checksum: `0x3D61`;
- required checksum: `0x3D61`;
- SGDK full-ROM XOR-fold: `0x0000`.

Resource budget (conservative pre-ResComp upper bound):

- 658 unique tiles;
- 21,056 bytes pattern data;
- at least 24,000 bytes free относительно 44 KiB project pattern ceiling;
- project VDP sprite payload: 0.

Подробности: `tests/r2/R2_BUILD_STATUS.md` и `sgdk/res/R2_RESOURCE_BUDGET.md`.

## 8. Следующий обязательный шаг

Только target-проверка **Visual Rework 1** в MD Emu Games Gen:

- compare screen с `references/MAIN_MENU_REFERENCE.png`;
- проверить visual density/composition/logo/background/bottom strip;
- selector Up/Down;
- selector pulse + moving background tank;
- ИГРАТЬ → TEST_BATTLE → B → MENU;
- ГАРАЖ → GARAGE → B → MENU;
- после переходов `ERR:00`;
- отсутствие VRAM/palette/sprite corruption.

## 9. Строгий запрет

**R2 пока НЕ ACCEPTED. R3 НЕ НАЧИНАТЬ.**

R3 разрешается только после прямого подтверждения владельцем, что R2 принят.
