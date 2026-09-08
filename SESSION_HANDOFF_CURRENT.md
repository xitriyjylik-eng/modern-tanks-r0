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

Успешный SGDK build:

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

## 3. Текущий milestone — R1 Core / State Machine — BUILD/CI PASS / TARGET PENDING

R1 реализуется строго по `plan/REBUILD_MASTER_PLAN.md`.

### Требуемый scope

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

### Реализация текущего source

`sgdk/src/main.c` переписан с R0 probe на R1 core-shell без использования старого DEV-кода.

В нём:

- явный `GameState`;
- явный `ResourceBank`;
- `InputState { held, pressed, released }`;
- `JOY_SUPPORT_3BTN`;
- 60 Hz logical clock; на PAL 50 Hz логика компенсируется до той же реальной скорости;
- state enter/leave hooks;
- bank unload очищает BG_A/B, WINDOW, scroll, CRAM и VDP sprites;
- внутренние проверки palette residue и sprite leak;
- debug overlay с state/bank/videoHz/transition/error counters;
- встроенный автоматический soak по кнопке C в MAIN MENU.

### Soak gate

Кнопка C запускает 100 переходов — 25 циклов:

`MENU → TEST_BATTLE → MENU → GARAGE → MENU`

Ожидаемый итог:

- `SOAK: PASS 100/100`;
- `ERR: 00`;
- `STATE: MAIN_MENU`;
- `BANK: MENU`.

## 4. Что намеренно НЕ входит в R1

- финальная графика меню из `MAIN_MENU_REFERENCE.png`;
- battlefield renderer/HUD;
- tank art;
- region/world tiles;
- gameplay/AI/projectiles;
- SRAM;
- audio.

Это последующие стадии. Не расширять scope R1 только потому, что ROM компилируется.

## 5. Visual references — LOCKED

Исходные SHA-256:

- `COMBAT_REFERENCE.png`: `57985349c3c0eec4c1118ce35988a52181ba6357f24a61a44b6b46721db4d9b5`
- `MAIN_MENU_REFERENCE.png`: `af049be579c56dde8b9239cb1fff11a705167957e17315528fe44d2965592360`
- `TANKS_DETAILED_REFERENCE.png`: `5956e18e6b5d994ec730a37109e8fabd7aec158dd0f71c811a75735947ab07d7`

Они не изменялись при переходе R0 → R1.

## 6. Granada

`external_reference/Granada (JU) (REV01) [T+Rus Pirate].zip` содержит один 524288-byte ROM с SHA-256 `bebebce4f157c3c46d9fe1a85f336cb218aad8ae5dc29c1d454aab9c0f460889`.

Он изучается только как технический ориентир: startup discipline, state/resource paging, VRAM discipline, top-down readability. Никакие его assets/code/game rules в Modern Tanks не переносятся.

## 7. GitHub / R1 CI

Repository: `xitriyjylik-eng/modern-tanks-r0`.

Write/admin access подтверждён. R1 source зафиксирован и реально собран через GitHub Actions.

- R1 source commit: `d348e0518bfe74d47da6db705313e4a26c0fc891`;
- R1 GitHub Actions run: `34176727527`;
- job `build-r1`: SUCCESS;
- две независимые clean SGDK 2.11 сборки совпали byte-for-byte;
- ROM size: `131072` bytes;
- ROM SHA-256: `4fdc8d3d8ef9f723caf228b61f183b1fea927bee93727028f6e0a414cf6a726a`;
- header checksum: `0xF22B`;
- required checksum: `0xF22B`;
- SGDK full-ROM XOR-fold: `0x0000`;
- independent ROM audit: PASS;
- CI artifact: `Modern_Tanks_R1_Core_Menu`;
- exact Docker image digest: `sha256:327ab838fbdf6bc741c6a7a11ee3c937cf1aaf1dc07a475995e89b741b6a830d`;
- exact image ID: `sha256:e66837c905b7878e02ecfce1e3b906856dad5d751789c29b97555798f6b66972`.

Компиляция не закрывает gate: target-test R1 ещё нужен.

## 8. Gate после R1 build

CI часть R1 пройдена. ROM передан пользователю для MD Emu Games Gen.

Ожидаемый target-result после C-soak: `SOAK: PASS 100/100`, `ERR: 00`, `STATE: MAIN_MENU`, `BANK: MENU`, после чего ручной input должен продолжать работать.

**R1 пока НЕ ACCEPTED. Не переходить к R2 до прямого подтверждения пользователя, что R1 принят.**
