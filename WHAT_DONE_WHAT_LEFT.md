# WHAT DONE / WHAT LEFT

Актуально на 2026-09-09.

## Выполнено и принято

### R0 Hardware Probe — CLOSED

Результат: подтверждена рабочая SGDK/Mega Drive линия и базовый запуск на целевом эмуляторе. Приняты 320×224 и 3-button controller как обязательная базовая конфигурация.

### R1 Core / State Machine — CLOSED

Результат:
- BOOT;
- TITLE;
- MAIN_MENU;
- TEST_BATTLE shell;
- GARAGE shell;
- контролируемые transitions;
- D-pad / A / B / START path;
- 50/60 Hz logic compensation;
- resource banks;
- state enter/leave;
- plane/sprite/palette cleanup;
- error/debug counters.

### R2 Main Menu Visual / Ambient — CLOSED

Владелец проверил финальный ROM и подтвердил приёмку.

Зафиксирован результат:
- качественный нативный 320×224 battlefield background;
- утверждённая русская типографика;
- утверждённая центральная панель меню;
- правильная цветовая гамма ландшафта;
- правая мини-карта удалена;
- river: 12 кадров, течение по руслу, анимация не попадает на берег/дом/мост;
- right flag: 12 кадров, плавное колыхание на существующем флагштоке;
- left flag: отсутствует;
- upper fire: 8 кадров; статичный нарисованный огонь под анимацией удалён;
- lower fire: 8 кадров, отдельная фаза; статичный огонь удалён;
- trees: 12 кадров, минимальное движение листьев/краёв крон;
- анимации не получают отдельную более яркую цветовую гамму;
- независимые timers;
- сохранён R1 core;
- VRAM guard остаётся обязательным;
- два SGDK 2.11 builds совпадают byte-for-byte;
- ROM audit PASS.

Контрольная точка R2:
- commit: `a1faa7d567ceb7f5506005b354da28f5c1ea0cee`;
- CI: `34255626880` SUCCESS;
- ROM size: 131072 bytes;
- ROM SHA-256: `fb6896471a1bf559e13c55118c3d2beedf8c1567ff6703a114ef05857b744017`.

## Что осталось

### R3 Battle Renderer / HUD — NEXT

Сделать настоящее поле боя с камерой и интерфейсом: Plane B world base, Plane A upper world, Window HUD/log layout, camera/scroll, map-edge streaming, HUD/minimap framework, event log framework, clipping игровых спрайтов от HUD. Подробно: `plan/NEXT_R3_SCOPE.md`.

### R4 Tank Art / Player Classes

T-1…T-8, боевые 32×32 sprites, 4 направления, читаемые силуэты/роли, корректный sprite budget и bank lifecycle.

### R5 Region 1 / World Foundation

«Зелёный рубеж»: реальные terrain families, metatiles/world streaming, collision/destruction foundation, крупная test map.

### R6 Combat / Enemies / Mission Vertical Slice

Движение, стрельба, projectile pool, броня/направления, damage, AI, objectives, base/reserves/bonuses; полный первый vertical slice от меню до результата.

### R7 Regions 2–5

Отдельные visual/resource banks и полноценные регионы без разрушения renderer/resource discipline.

### R8 Bosses / Effects / Weather

Goliath, Thunder, Iron Serpent, Tempest, Leviathan; эффекты и погодные состояния.

### R9 Meta Systems

Campaign map, briefing, garage, tank select, upgrades, statistics, options, results, difficulty, ranks, secrets/unlocks, post-campaign modes.

### R10 SRAM

3 profiles, A/B copies, MAGIC/VERSION/SEQUENCE/DATA/CHECKSUM, recovery/corruption tests.

### R11 Audio

XGM2/YM2612 music + PSG/PCM SFX, Z80/audio stress safety.

### R12 QA / Release Candidate

MD Emu Games Gen, BlastEm, Genesis Plus GX, PicoDrive и по возможности hardware; NTSC/PAL, controls, all states/regions/bosses, SRAM, audio, reset, checksum, long-run tests.

## Общее правило продолжения

Не улучшать закрытые этапы «заодно». Каждый новый этап расширяет игру, сохраняя принятые результаты R0–R2, пока владелец явно не попросит их изменить.
