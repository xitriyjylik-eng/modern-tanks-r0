# MODERN TANKS — CURRENT SESSION HANDOFF

Дата состояния: **2026-09-08**.

## 1. Инварианты

- Идею Modern Tanks не менять.
- Три locked PNG reference не изменять/не перекодировать/не заменять.
- `TANKS_DETAILED_REFERENCE.png` — обязательный art-direction танков.
- Granada — только технический образец Mega Drive.
- Старая DEV-линия запрещена.
- Clean SGDK 2.11 rebuild only.

## 2. Закрытые этапы

- **R0 — ACCEPTED / CLOSED.**
- **R1 — ACCEPTED / CLOSED.** FIX2 target: `ERR:00`, `SOAK: PASS 100/100`.

## 3. R2 MAIN MENU VISUAL TARGET

Статус: **FOCUSED MENU / TANK REFERENCE REWORK — BUILD/CI PASS / TARGET ACCEPTANCE PENDING**.

R3 не начинать до прямого принятия R2 владельцем.

## 4. Последнее обязательное решение владельца

После проверки предыдущего R2 владелец уточнил компоновку:

- убрать из главного меню нижний HUD `T-1..T-4 / параметры / карта`;
- эта панель не несла функции в MAIN MENU и перегружала экран;
- выбор/характеристики танка относятся к `ГАРАЖ`;
- карта и миссионная информация относятся к миссионным/игровым экранам;
- полностью убрать декоративный движущийся танк наверху/на фоне меню.

Текущий R2 это решение реализует: поле боя продолжается до нижнего края 320×224, а единственная текущая UI-анимация — pulse активного пункта меню.

## 5. Танки

Танки больше не строятся как простые прямоугольные пиктограммы.

Вручную нарисован reference-driven native pixel renderer с признаками:

- строгий top-down;
- отдельные гусеницы и tread-сегменты;
- бронекорпус со скосами;
- башня/погон;
- маска орудия и длинный ствол;
- люк/командирская башенка, болты, моторная палуба/бортовые модули;
- разные пропорции T-1 разведчика, T-2 рейнджера, T-3 крепости и T-4 штурмовика.

В R2 эти машины используются только как статичная часть battlefield art. Финальный gameplay sprite-set относится к последующим этапам и не должен начинаться раньше плана.

## 6. Текущий CI

- GitHub Actions run: `34186426856` — SUCCESS;
- tested commit: `831cd8348997cdb13e82cfc8422c6748f3e0e0b1`;
- SGDK 2.11 build A/B: PASS, byte-identical;
- ROM audit: PASS;
- ROM size: `131072` bytes;
- SHA-256: `d4baf97f7884ae0e91be0bc599d11046959fae88407c2db7235dd37726dc47f4`;
- header checksum: `0x6DF1`;
- XOR-fold: `0x0000`.

Resource budget from CI:

- 950 unique background tiles;
- worst selector 24 tiles;
- conservative simultaneous project patterns: 974 tiles / 31,168 bytes;
- 13,888 bytes free vs project 44 KiB ceiling;
- menu VDP sprite payload: 0;
- moving tank resource removed.

После tested commit также удалён старый неиспользуемый `sgdk/art/r2_anim_tank.png.b64`; это неиспользуемый source artifact и на собранный ROM не влияет.

## 7. Следующий шаг

Только target-проверка текущего R2 ROM владельцем:

- визуально оценить новое более чистое меню;
- сравнить статичные танки с `TANKS_DETAILED_REFERENCE.png`;
- проверить Up/Down selector;
- ИГРАТЬ → TEST_BATTLE → B → MENU;
- ГАРАЖ → GARAGE → B → MENU;
- убедиться, что переходы не дают corruption/ERR.

**R2 пока НЕ ACCEPTED. R3 BLOCKED.**
