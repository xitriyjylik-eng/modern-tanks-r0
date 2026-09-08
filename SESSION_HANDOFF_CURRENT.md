# MODERN TANKS — CURRENT SESSION HANDOFF

Дата состояния: **2026-09-08**.

## 1. Инварианты

- Идею Modern Tanks не менять.
- Три locked PNG reference не изменять/не перекодировать/не заменять.
- `MAIN_MENU_REFERENCE.png` — обязательный визуальный target главного меню.
- `TANKS_DETAILED_REFERENCE.png` — обязательный art-direction/геометрический target танков.
- Granada — только технический образец Mega Drive.
- Старая DEV-линия запрещена.
- Clean SGDK 2.11 rebuild only.

## 2. Закрытые этапы

- **R0 — ACCEPTED / CLOSED.**
- **R1 — ACCEPTED / CLOSED.** FIX2 target: `ERR:00`, `SOAK: PASS 100/100`.

## 3. R2 MAIN MENU VISUAL TARGET

Статус: **REFERENCE-FAITHFUL REWORK — BUILD/CI PASS / TARGET ACCEPTANCE PENDING**.

R3 не начинать до прямого принятия R2 владельцем.

## 4. Обязательное решение владельца по компоновке

- убрать из главного меню нижний HUD `T-1..T-4 / параметры / карта`;
- выбор/характеристики танка относятся к `ГАРАЖ`;
- карта и миссионная информация относятся к миссионным/игровым экранам;
- полностью убрать отдельный декоративный движущийся танк;
- сохранить четыре канонических пункта: `ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ`.

Текущий R2 это решение реализует. Единственная текущая UI-анимация — pulse/навигация активного пункта меню.

## 5. Новое правило визуальной реализации R2

Предыдущая ручная стилизация танков и поля признана недостаточно похожей на утверждённые примеры и больше не является target.

Текущий R2 строится как reference-faithful Mega Drive adaptation:

- композиция, battlefield/metal/logo visual language берутся непосредственно из утверждённого `MAIN_MENU_REFERENCE.png`;
- формы и внешний язык T-1/T-2/T-3/T-4 берутся непосредственно из `TANKS_DETAILED_REFERENCE.png`;
- runtime asset адаптируется к native Mega Drive `320x224` и допустимой палитре/тайлам;
- исходные locked reference PNG не изменяются и не заменяются;
- запрещено подменять работу отдельной AI-generated картинкой;
- R2 должен оцениваться по визуальной близости к утверждённым reference, а не по принципу «стало немного лучше».

## 6. Текущий CI candidate

- GitHub Actions run: `34189204407` — **SUCCESS**;
- tested commit: `6ebd952febbc29dec71f0278f7b00f2a1f8c804c`;
- SGDK 2.11 build A/B: **PASS, byte-identical**;
- ROM audit: **PASS**;
- ROM size: `131072` bytes;
- SHA-256: `f73f2e80107ce25a5622f0e9d5f6dc84c3d0f1b7375178b3355132e58305c082`;
- header checksum: `0x4215`;
- required checksum: `0x4215`;
- XOR-fold: `0x0000`;
- console header: `SEGA MEGA DRIVE`;
- input contract: standard 3-button controller.

CI дополнительно проверяет SHA исходного подготовленного R2 background asset перед SGDK-сборкой, чтобы повреждённая/обрезанная передача графики не могла тихо попасть в ROM.

## 7. Что проверить владельцу

Только target-проверка текущего R2 ROM в MD Emu Games Gen:

- общий визуальный язык и композицию против `MAIN_MENU_REFERENCE.png`;
- формы/детализацию танков против `TANKS_DETAILED_REFERENCE.png`;
- отсутствие нижнего HUD `танки / параметры / карта`;
- отсутствие отдельного ездящего декоративного танка;
- Up/Down selector;
- ИГРАТЬ → TEST_BATTLE → B → MENU;
- ГАРАЖ → GARAGE → B → MENU;
- отсутствие corruption/ERR при переходах.

**R2 пока НЕ ACCEPTED. R3 BLOCKED.**
