# R2 ACCEPTANCE CHECKLIST

Stage: **R2 Main Menu Visual Target — Visual Rework 1**

Target emulator: **MD Emu Games Gen / Android**.

Первый R2 candidate уже был визуально отклонён владельцем. Не считать технический CI PASS достаточным: текущий Visual Rework 1 должен реально приблизиться к locked `references/MAIN_MENU_REFERENCE.png` по композиции и плотности.

## 1. Startup

- ROM запускается без crash/red screen.
- BOOT → TITLE работает.
- A/START с TITLE открывает MAIN MENU.

## 2. Visual target

Сравнить с locked `references/MAIN_MENU_REFERENCE.png` по общей композиции, visual density и 16-bit language, не требуя буквального совпадения каждого пикселя.

На экране должны быть заметно выражены:

- крупный dimensional metallic MODERN TANKS logo;
- насыщенный battlefield background;
- winding water/shoreline;
- forest/terrain clusters;
- bridges/fortifications/obstacles;
- несколько battlefield tanks и battle-effect details;
- steel/metal frame language;
- четыре крупных русских пункта меню;
- более узкая central panel, близкая по пропорциям к reference;
- tank-class strip с различимыми T-1…T-4 silhouettes;
- segmented stats preview;
- mini-map preview;
- заполненные панели без пустых placeholder-блоков;
- чистая нативная 16-bit графика без грязного auto-downscale reference.

Если экран снова выглядит как упрощённая схема reference, а не как законченный 16-bit menu screen, R2 остаётся FAIL/PENDING.

## 3. Menu semantics

Порядок и смысл frozen design:

1. ИГРАТЬ
2. ГАРАЖ
3. СТАТИСТИКА
4. НАСТРОЙКИ

Up/Down должны перемещать selector по всем четырём пунктам.

`ПРОКАЧКА` остаётся внутри ГАРАЖА, выбор миссий — внутри ИГРАТЬ. Эти две ветви не добавлять как top-level только ради буквального копирования reference.

STATISTICS и OPTIONS в R2 разрешено выбирать визуально, но они намеренно не открывают полноценные meta-state до более поздней стадии.

## 4. Animation

- selector имеет видимую animation/pulse;
- на battlefield присутствует subtle scripted moving tank;
- анимация не вызывает flicker/corruption/зависание.

## 5. Resource-bank isolation

- ИГРАТЬ + A/START → TEST_BATTLE shell;
- в shell menu bank выгружен;
- `ERR:00`;
- B → возврат в полноценное R2 menu без corruption;
- ГАРАЖ + A/START → GARAGE shell;
- `ERR:00`;
- B → возврат в menu без corruption.

Повторить несколько циклов MENU ↔ TEST_BATTLE и MENU ↔ GARAGE.

## 6. PASS

R2 можно закрыть только после прямого подтверждения владельца, что:

- Visual Rework 1 визуально устраивает относительно reference;
- menu читаемо и выглядит как законченный игровой экран;
- navigation/animation работают;
- menu bank корректно unload/reload;
- `ERR:00` сохраняется;
- нет видимого VRAM/palette/sprite corruption.

До этого статус: **BUILD/CI PASS / TARGET ACCEPTANCE PENDING**.

**R3 не начинать до отдельного подтверждения R2.**
