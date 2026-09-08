# MODERN TANKS — CURRENT SESSION HANDOFF

Дата состояния: **2026-09-08**.

## 1. Жёсткие инварианты

1. Идею, механику и идентичность Modern Tanks не менять.
2. `design/GAME_DESIGN_FROZEN.md` — источник истины по игре.
3. Три PNG в `references/` не изменять, не перекодировать и не заменять.
4. Granada использовать только как технический образец Mega Drive; не копировать её графику, код, карты, музыку или игровые правила.
5. Старую DEV-линию, DEV ROM, Python opcode-emitter и старый DEV master-plan не возвращать.
6. Техническая линия только R0–R12 clean rebuild на SGDK 2.11.

## 2. Закрытые этапы

- **R0 Hardware Probe — ACCEPTED / CLOSED.** Target MD Emu Games Gen PASS.
- **R1 Core / State Machine — ACCEPTED / CLOSED.** FIX2: `ERR:00`, `SOAK: PASS 100/100`, target PASS. Accepted source commit `bc858a619de76a1f5c3112859914ea132e9bf7be`, run `34178302167`.

## 3. Текущий milestone — R2 MAIN MENU VISUAL TARGET

Статус: **MAX DETAIL BUILD/CI PASS / TARGET ACCEPTANCE PENDING**.

R3 не начат и остаётся запрещён до прямого принятия R2 владельцем.

### История отклонений

Первый R2 candidate и Visual Rework 1 технически собирались и работали, но владелец проекта отклонил их визуально как слишком упрощённые относительно locked `references/MAIN_MENU_REFERENCE.png`.

Не возвращаться к ним. Текущий candidate — **R2 MAX DETAIL**.

## 4. Целевая платформа

Modern Tanks остаётся настоящим Mega Drive/Genesis ROM.

- SG800 рассматривается как MD/Mega Drive emulator host для пользовательских ROM;
- HDMI/4K — вывод/upscaling, а не внутреннее разрешение игры;
- основной render target остаётся H40 320×224 Mega Drive;
- тот же `.bin` должен работать на SG800 и в MD/Genesis эмуляторах ПК;
- обязательный control path — 3-button D-Pad + A/B/C/START; 6-button pads совместимы, X/Y/Z не требуются базовой игре.

## 5. R2 MAX DETAIL art direction

Вместо малого процедурного улучшения сделан полный художественный rework с существенно более плотным использованием Mega Drive pattern budget:

- native 320×224 indexed pixel art;
- собственный hand-defined pixel font вместо TTF/downscale;
- крупный layered metallic `MODERN TANKS` logo с steel wings/rivets/bevels;
- organic battlefield вместо заметной 8×8 сетки;
- winding river + shoreline;
- grass/dirt variation, roads;
- bridges;
- brick/steel fortifications;
- clustered trees;
- craters/rubble;
- multiple distinct top-down tanks;
- shells, muzzle flashes, explosions, smoke;
- steel central menu;
- canonical `ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ`;
- detailed T-1…T-4 cards;
- segmented stats bars;
- detailed minimap;
- selector pulse/navigation;
- moving tank overlay;
- accepted R1 bank unload/reload + CRAM/sprite cleanup сохранены.

`ПРОКАЧКА` остаётся внутри ГАРАЖА, выбор миссий — внутри ИГРАТЬ согласно frozen design.

Locked reference PNG не встроен, не изменён и не downscale'ится. Granada assets/code отсутствуют.

## 6. R2 MAX DETAIL CI — PASS

- source commit: `53ef4dba355abbad5ad052ef1ee35345e17006bf`;
- GitHub Actions run: `34184514661`;
- job `build-r2`: SUCCESS;
- generated-art validation: PASS;
- generated resource SHA checks: PASS;
- source/locked-art contract: PASS;
- SGDK 2.11 build A: PASS;
- SGDK 2.11 build B: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM audit: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `52b0395fb023ebdaa08ca7e03152fa6b2040ed5c9a6b997509c618c4a9e95eba`;
- header checksum: `0xE671`;
- full-ROM XOR-fold: `0x0000`;
- exact `r2_menu_bg.png` SHA-256: `927534f927eaf17cd939a4977f20adbd8a705ca405f4c1a37511bd2a593376d0`.

Conservative project-pattern estimate: about **883 tiles / 28,256 bytes**, leaving about **16,800 bytes** against the 44 KiB project-pattern ceiling. Это сознательно заметно плотнее ранних R2 builds.

Полный статус: `tests/r2/R2_MAX_DETAIL_BUILD_STATUS.md`.

## 7. Следующий обязательный шаг

Только target-проверка **R2 MAX DETAIL ROM**:

- визуальное сравнение с locked main-menu reference;
- selector Up/Down + pulse;
- moving battlefield tank;
- ИГРАТЬ → TEST_BATTLE → B → MENU;
- ГАРАЖ → GARAGE → B → MENU;
- после переходов `ERR:00`;
- отсутствие VRAM/palette/sprite corruption.

Если внешний вид всё ещё не устраивает — продолжать R2, а не переходить к R3.

## 8. Строгий запрет

**R2 пока НЕ ACCEPTED. R3 НЕ НАЧИНАТЬ.**
