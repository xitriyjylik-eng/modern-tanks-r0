# Modern Tanks — CURRENT STATUS / READ FIRST

Дата фиксации: 2026-09-09

Это главный статусный файл проекта. Если старые документы противоречат этому файлу по состоянию этапов, приоритет у этого файла и `plan/PROJECT_PROGRESS_ACCEPTED_R2.md`.

## Принятая контрольная точка

- Платформа: Sega Mega Drive / Genesis.
- SDK: SGDK 2.11.
- Нативный экран: 320×224.
- Основной путь управления: 3-button controller.
- Репозиторий: `xitriyjylik-eng/modern-tanks-r0`.
- Принятый игровой baseline R2: commit `a1faa7d567ceb7f5506005b354da28f5c1ea0cee`.
- Финальный проверочный CI run R2: `34255626880` — SUCCESS.
- Принятый ROM SHA-256: `fb6896471a1bf559e13c55118c3d2beedf8c1567ff6703a114ef05857b744017`.
- Размер ROM: 131072 bytes.
- ROM audit: PASS.
- Владелец проекта проверил финальный R2 в целевом эмуляторе и явно подтвердил: «Супер, засчитываю».

## Состояние этапов

| Этап | Статус | Результат |
|---|---|---|
| R0 Hardware Probe | ACCEPTED / CLOSED | Базовый Mega Drive/SGDK runtime и фактическая проверка на целевом эмуляторе |
| R1 Core / State Machine | ACCEPTED / CLOSED | BOOT, TITLE, MAIN_MENU, TEST_BATTLE shell, GARAGE shell, переходы, input, NTSC/PAL timing, bank lifecycle, error layer |
| R2 Main Menu Visual / Ambient | ACCEPTED / CLOSED | Финальное главное меню, принятый фон, палитра и окружающие анимации |
| R3 Battle Renderer / HUD | NEXT / UNBLOCKED / NOT STARTED | Следующий этап реализации |
| R4 Tank Art / Player Classes | PENDING | После R3 |
| R5 Region 1 / World Foundation | PENDING | После R4 |
| R6 Combat / Enemies / Mission Vertical Slice | PENDING | После R5 |
| R7 Regions 2–5 | PENDING | После vertical slice |
| R8 Bosses / Effects / Weather | PENDING | Далее по master plan |
| R9 Meta Systems | PENDING | Кампания, гараж, апгрейды, статистика, options/results |
| R10 SRAM | PENDING | 3 профиля, A/B copies, checksum/recovery |
| R11 Audio | PENDING | XGM2/YM2612 + PSG/PCM |
| R12 QA / Release Candidate | PENDING | Emulator matrix, NTSC/PAL, reset/save/audio/checksum |

## Что именно принято в R2

Главное меню, его шрифт, компоновка, рамки, селектор, общий ландшафт и цветовая гамма считаются зафиксированными. Правая мини-карта удалена. Общая детализация и качество фона приняты и не должны ухудшаться при последующих этапах.

Окружающая анимация финального R2:

- река — 12 кадров, медленное течение по локальному направлению русла;
- берег, дома и мост исключены из маски воды;
- правый флаг — 12 плавных кадров на существующем флагштоке;
- левого флага нет;
- верхний огонь — 8 кадров, статичный дубликат пламени убран из фона;
- нижний огонь — независимые 8 кадров, статичный дубликат также убран;
- деревья — лёгкое 12-кадровое движение периферии крон;
- вода, огонь, флаг и листва используют существующие цветовые категории сцены и не должны визуально выбиваться яркостью;
- отдельные анимации имеют собственные таймеры;
- R1 core сохранён.

## CI и воспроизводимость

Финальный R2 проходит генерацию/проверку ресурсов, VRAM budget guard, две независимые сборки SGDK 2.11, byte-for-byte сравнение ROM и ROM audit. Принятый baseline не следует менять при подготовке R3, кроме осознанных изменений, относящихся к новому этапу.

## Что делать дальше

Начинать R3. Не возвращаться к редизайну принятого R2 без прямого запроса владельца.

R3 должен использовать `references/COMBAT_REFERENCE.png` как визуальный ориентир боя, при этом три locked reference PNG нельзя изменять, перекодировать или заменять. Granada остаётся только техническим ориентиром Mega Drive/VDP/resource discipline и не является донором кода, ассетов, карт, музыки или правил игры.

Подробный R3 scope: `plan/NEXT_R3_SCOPE.md`.
Подробная фиксация прогресса: `plan/PROJECT_PROGRESS_ACCEPTED_R2.md`.
Финальная приёмка R2: `R2_ACCEPTANCE_FINAL.md`.
