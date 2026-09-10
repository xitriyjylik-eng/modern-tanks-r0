# Modern Tanks — CURRENT STATUS / READ FIRST

Дата фиксации: 2026-09-10.

Это главный статусный файл текущей рабочей ветки. Если старые документы противоречат ему по текущему состоянию R3/Map 01, приоритет у этого файла, `R3_WORK_CHECKPOINT.md` и `R3_MAP01_PRODUCTION_PIPELINE.md`.

## Принятая база
- R0 / R1 / R2: **ACCEPTED / CLOSED**.
- Платформа: Sega Mega Drive / Genesis.
- SDK: SGDK 2.11.
- Нативный экран: 320×224.
- Принятый R2 baseline commit: `a1faa7d567ceb7f5506005b354da28f5c1ea0cee`.
- Принятый R2 ROM SHA-256: `fb6896471a1bf559e13c55118c3d2beedf8c1567ff6703a114ef05857b744017`.
- `main` не изменять до явной пользовательской приёмки R3.

## R3 — текущий статус
R3: **IN PROGRESS / MAP 01 PRODUCTION / NOT ACCEPTED**.

Старый R3-кандидат 1024×768 технически доказал renderer/HUD/smooth camera/MAP lifecycle и прошёл BlastEm NTSC/PAL + soak, но его художественная карта отклонена. Она остаётся только техническим testbed и не является целевым WORLD_ART.

## Главная цель R3
Довести большую цельную Map 01 по утверждённому визуальному эталону до рабочего игрового состояния: ручной WORLD_ART, TERRAIN/COLLISION, OBJECTS/EVENTS, SPAWN/runtime, потоковая подгрузка, плавная камера и финальная проверка без долгой загрузки.

## Актуальная Map 01
- authoritative WORLD_ART master: 1536×1152;
- масштабирование/regeneration: нет;
- sector grid: 12×9 = 108 секторов 128×128;
- старый план 4096×3072 / 192 сектора отменён;
- procedural geography запрещена;
- визуальное качество нельзя ухудшать ради tile-dedup/ROM norms.

## Прогресс
- Z01: WORLD_ART + TERRAIN/COLLISION + OBJECTS/EVENTS + SPAWN/runtime + отдельный SGDK/BlastEm proof — DONE.
- Z03 WORLD_ART scope 768×512 — DONE.
- Z03 TERRAIN/COLLISION 96×64 — DONE V2, validation PASS.
- Z03 overlap с Z01: 2560 cells/layer inherited cell-for-cell — PASS.
- Следующий этап: **Z03 OBJECTS + EVENTS**.

## Конечный маршрут R3
`эталон/география → structure → WORLD_ART → TERRAIN/COLLISION → OBJECTS/EVENTS → SPAWN/runtime → full integration → camera/streaming/latency → NTSC/PAL + soak → user acceptance`.

CI/fuzzy/screenshot metrics — средства диагностики, не самостоятельные этапы.

Подробнее:
- `R3_WORK_CHECKPOINT.md`;
- `R3_MAP01_PRODUCTION_PIPELINE.md`;
- `map01/MAP_01_IMPLEMENTATION_STATUS.md`.
