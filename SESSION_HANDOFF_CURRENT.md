# MODERN TANKS — CURRENT SESSION HANDOFF

Дата состояния: **2026-09-08**.

## 1. Инварианты

- Идею Modern Tanks не менять.
- R0 и R1 не откатывать.
- Granada — только технический образец Mega Drive; её графика/код в Modern Tanks не встраиваются.
- Старая DEV-линия запрещена.
- Clean SGDK 2.11 rebuild only.
- Нативная цель Mega Drive: `320x224`, стандартный 3-button controller.

## 2. Актуальный визуальный источник истины

Владелец заменил старую визуальную цель двумя новыми утверждёнными образцами из текущей сессии:

1. **Gameplay visual reference** — top-down поле боя с рекой, мостом, лесом, зданиями, укреплениями, дорогами, кратерами, огнём/дымом и насыщенной 16-bit детализацией.
2. **Tank mini-sprite reference** — T-1/T-2/T-3/T-4, вид сверху, 16x16 в игре, 8 направлений, один основной ствол, отчётливые корпус/башня/гусеницы и разные силуэты классов.

Старые упрощённые карта/танки больше не являются visual target. Файлы legacy references можно хранить как историю проекта, но новые реализации не должны ориентироваться на их старую упрощённую интерпретацию.

Подробные параметры зафиксированы в `plan/VISUAL_STYLE_TARGET.md`.

## 3. Закрытые этапы

- **R0 — ACCEPTED / CLOSED.**
- **R1 — ACCEPTED / CLOSED.** FIX2 target: `ERR:00`, `SOAK: PASS 100/100`.

## 4. R2 — FINAL VISUAL CANDIDATE / CI PASS / TARGET PENDING

R2 остаётся главным меню. R3 не начинать до прямого принятия R2 владельцем.

Обязательная компоновка R2:

- логотип `MODERN TANKS`;
- полноценный battlefield background в новом утверждённом стиле;
- центральная steel/navy menu panel;
- четыре пункта `ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ`;
- selector/navigation;
- **нет** нижнего HUD `T-1..T-4 / параметры / карта`;
- **нет** отдельного декоративного движущегося танка.

Выбор/характеристики танка относятся к `ГАРАЖ`; карта/миссионные данные — к игровым/миссионным экранам.

## 5. Графическая реализация текущего R2

Текущий candidate больше не использует прежний процедурный клетчатый art-layer.

- Background — exact deterministic indexed asset `320x224`, подготовленный из утверждённого battlefield visual language.
- Используется 8bpp indexed PNG с выбором PAL0..PAL3 на каждом 8x8 tile.
- SHA background asset: `5ec08a6cb60201367bc45becdf116f3efe71597762f5f25d7aa28b62ff6426ea`.
- Selector asset: `144x16`, SHA `36deb4395d061cc75f9972e0427b2c9b1ccf45ca2eb95992feac49a0737170fd`.
- Palette-tile distribution: `PAL0=576`, `PAL1=56`, `PAL2=150`, `PAL3=338`.
- Unique indexed tiles before ResComp optimization: background `921`, selector `6`.
- Искусственный старый project ceiling удалён; остаются только реальные ограничения VDP/SGDK, runtime проверяет `TILE_USER_MAX_INDEX`.
- Background не использует PAL0 index 15; он зарезервирован selector pulse.

## 6. Финальный CI candidate

- tested commit: `d087d03275c658e4799afa53e395251083308669`;
- GitHub Actions run: `34201271457` — **SUCCESS**;
- SGDK 2.11 build A/B: **PASS, byte-identical**;
- independent ROM audit: **PASS**;
- ROM size: `131072` bytes;
- ROM SHA-256: `e0b3a90b3a33c8e06bde7ec9749ef7f105ff38558ed3d6eb6b1c0dda5909773c`;
- header checksum: `0x49B6`;
- required checksum: `0x49B6`;
- XOR-fold: `0x0000`;
- console header: `SEGA MEGA DRIVE`.

Artifact: `Modern_Tanks_R2_Final_Visual_Candidate`.

## 7. Что проверить владельцу в MD Emu Games Gen

- общий вид меню соответствует новой утверждённой 16-bit battlefield стилистике;
- река/мост/лес/постройки/земля/следы боя выглядят как единый мир с будущим gameplay;
- логотип и steel/navy panel читаются хорошо;
- Up/Down selector работает;
- `ИГРАТЬ → TEST_BATTLE → B → MENU`;
- `ГАРАЖ → GARAGE → B → MENU`;
- нижнего HUD нет;
- декоративного ездящего танка нет;
- нет corruption/ERR после нескольких переходов.

**R2 пока НЕ ACCEPTED. R3 BLOCKED до прямого target PASS владельца.**
