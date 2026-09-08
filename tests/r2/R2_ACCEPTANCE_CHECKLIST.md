# R2 ACCEPTANCE CHECKLIST

Stage: **R2 Main Menu Visual Target**

Target emulator: **MD Emu Games Gen / Android**.

## 1. Startup

- ROM запускается без crash/red screen.
- BOOT → TITLE работает.
- A/START с TITLE открывает MAIN MENU.

## 2. Visual target

Сравнить с locked `references/MAIN_MENU_REFERENCE.png` по общей композиции и языку оформления, не требуя буквального копирования пикселей.

На экране должны присутствовать:

- крупный MODERN TANKS logo;
- battlefield background, а не одноцветная заглушка;
- steel/metal frame language;
- четыре крупных русских пункта меню;
- tank-class strip;
- stats preview;
- mini-map preview;
- заполненные панели без пустых placeholder-блоков;
- чистая нативная 16-bit графика без грязного auto-downscale reference.

## 3. Menu semantics

Порядок и смысл:

1. ИГРАТЬ
2. ГАРАЖ
3. СТАТИСТИКА
4. НАСТРОЙКИ

Up/Down должны перемещать selector по всем четырём пунктам.

STATISTICS и OPTIONS в R2 разрешено выбирать визуально, но они намеренно не открывают полноценные meta-state до более поздней стадии.

## 4. Animation

- selector имеет видимую анимацию/pulse;
- на battlefield присутствует subtle scripted moving tank;
- анимация не вызывает flicker/corruption/зависание.

## 5. Resource-bank isolation

- ИГРАТЬ + A/START → TEST_BATTLE shell;
- в shell видно, что menu bank выгружен;
- `ERR:00`;
- B → возврат в полноценное R2 menu без corruption;
- ГАРАЖ + A/START → GARAGE shell;
- `ERR:00`;
- B → возврат в menu без corruption.

Повторить несколько циклов MENU ↔ TEST_BATTLE и MENU ↔ GARAGE.

## 6. PASS

R2 можно закрыть только после прямого подтверждения владельца, что:

- visual target устраивает относительно reference;
- menu читаемо и выглядит как законченный игровой экран;
- navigation/animation работают;
- menu bank корректно unload/reload;
- `ERR:00` сохраняется;
- нет видимого VRAM/palette/sprite corruption.

До этого статус: **BUILD/CI PASS / TARGET ACCEPTANCE PENDING**.

**R3 не начинать до отдельного подтверждения R2.**
