# PROJECT PROGRESS — ACCEPTED R2

Этот файл фиксирует фактический прогресс проекта после пользовательской приёмки R2 и имеет приоритет над устаревшими статусными строками в старых handoff/build-документах.

## Пройденная линия

### R0 — Hardware Probe
Статус: **ACCEPTED / CLOSED**.

Цель этапа выполнена: базовая SGDK/Mega Drive линия запускается и проверена владельцем на целевом эмуляторе. Нативное разрешение 320×224 и базовый 3-button input зафиксированы.

### R1 — Core / State Machine
Статус: **ACCEPTED / CLOSED**.

Реализованы и сохранены:
- state enum BOOT/TITLE/MAIN_MENU/TEST_BATTLE/GARAGE;
- валидируемые transitions;
- input held/pressed/released;
- 3-button controller;
- NTSC/PAL timing compensation;
- resource bank ownership;
- enter/leave lifecycle;
- очистка planes/sprites/palettes;
- error/debug tracking;
- shell-переходы в TEST_BATTLE и GARAGE и возврат B.

### R2 — Main Menu Visual / Ambient
Статус: **ACCEPTED / CLOSED**.

Пользовательская приёмка выполнена после проверки финального ROM в эмуляторе.

Фиксируется как принятый визуальный baseline:
- центральное меню, его шрифт, рамки, селектор и позиции;
- ландшафт, его детализация и цветовой баланс;
- отсутствие правой мини-карты;
- 12-frame river flow по руслу с точной маской;
- 12-frame right flag;
- отсутствие left flag;
- 8-frame upper fire и 8-frame lower fire без статичных дублей огня;
- 12-frame subtle tree foliage motion;
- независимые animation timers;
- использование текущих palette banks без искусственного повышения яркости анимаций;
- сохранён R1 resource/state core.

Техническая фиксация:
- accepted baseline commit: `a1faa7d567ceb7f5506005b354da28f5c1ea0cee`;
- final CI run: `34255626880` SUCCESS;
- accepted ROM SHA-256: `fb6896471a1bf559e13c55118c3d2beedf8c1567ff6703a114ef05857b744017`;
- accepted ROM size: 131072 bytes;
- reproducibility: two SGDK 2.11 builds byte-for-byte equal;
- ROM audit: PASS.

## Непройденная линия

### R3 — Battle Renderer / HUD
Статус: **NEXT / UNBLOCKED / NOT STARTED**.

Это первая новая разработка. Детали в `plan/NEXT_R3_SCOPE.md`.

### R4 — Tank Art / Player Classes
Статус: PENDING.

### R5 — Region 1 / World Foundation
Статус: PENDING.

### R6 — Combat / Enemies / Mission Vertical Slice
Статус: PENDING.

### R7 — Regions 2–5
Статус: PENDING.

### R8 — Bosses / Effects / Weather
Статус: PENDING.

### R9 — Meta Systems
Статус: PENDING.

### R10 — SRAM
Статус: PENDING.

### R11 — Audio
Статус: PENDING.

### R12 — QA / Release Candidate
Статус: PENDING.

## Инварианты продолжения

1. R0–R2 не открывать повторно без явного запроса владельца.
2. `design/GAME_DESIGN_FROZEN.md` не переписывать под удобство реализации.
3. Locked references в `references/` не изменять.
4. R3 строить на уже принятом R1 lifecycle/resource discipline.
5. VRAM/sprite/scanline/palette ограничения проверять автоматически, а не только визуально.
6. Каждый новый gate закрывается только после сборки, технической проверки и, когда требуется, пользовательской проверки в эмуляторе.
