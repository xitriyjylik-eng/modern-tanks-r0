# R2 BUILD STATUS

Дата: **2026-09-08**

Статус: **FOCUSED MENU / TANK REFERENCE REWORK — BUILD/CI PASS / TARGET ACCEPTANCE PENDING**

R0 и R1 остаются ACCEPTED / CLOSED. R3 не начинать до отдельного принятия R2 владельцем проекта.

## Решение владельца по компоновке

После target-проверки предыдущего R2 владелец отдельно уточнил:

- нижний блок `T-1..T-4 / параметры / карта` из главного меню убрать;
- он не выполнял игровой функции и перегружал экран;
- выбор и характеристики танка относятся к `ГАРАЖ`;
- карта/миссионная информация относятся к игровым/миссионным экранам;
- декоративный движущийся танк в главном меню убрать полностью.

## Танки

`references/TANKS_DETAILED_REFERENCE.png` остаётся обязательным художественным эталоном.

Текущий R2 использует вручную нарисованные native-pixel модели вместо простых иконок:

- строгий вид сверху;
- отдельные гусеницы и сегменты траков;
- сформированный бронекорпус;
- башня и башенное кольцо;
- маска орудия + длинный ствол;
- люк/командирская башенка;
- моторная палуба/бортовые модули;
- различимые силуэты T-1 разведчик, T-2 рейнджер, T-3 крепость, T-4 штурмовик.

Locked reference PNG не изменён и не встроен в ROM.

## Текущий экран

- native 320×224;
- металлический `MODERN TANKS`;
- `ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ`;
- поле боя продолжается до нижнего края экрана;
- река, дороги, лес, укрепления, кратеры, выстрелы/дым;
- вручную прорисованные статичные танки на поле;
- единственная текущая декоративная анимация UI — pulse активной строки selector.

## CI PASS

- GitHub Actions run: `34186426856`;
- tested commit: `831cd8348997cdb13e82cfc8422c6748f3e0e0b1`;
- SGDK 2.11 build A/B: PASS, byte-identical;
- independent ROM audit: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `d4baf97f7884ae0e91be0bc599d11046959fae88407c2db7235dd37726dc47f4`;
- header checksum: `0x6DF1`;
- XOR-fold: `0x0000`.

## Resource budget

- background: 950 unique 8×8 tiles before ResComp optimization;
- selector worst case: 24 unique tiles;
- conservative simultaneous upper bound: 974 tiles / 31,168 bytes;
- free against project 44 KiB pattern ceiling: 13,888 bytes;
- moving tank resource: removed;
- menu VDP sprite payload: 0.

## Gate

R2 остаётся **TARGET PENDING** до фактической проверки владельцем.

**R3 BLOCKED.**
