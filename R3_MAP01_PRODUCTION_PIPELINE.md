# R3 — MAP 01 PRODUCTION PIPELINE

Дата: 2026-09-10  
Статус R3: **IN PROGRESS / MAP 01 PRODUCTION / NOT ACCEPTED**.

## Постоянные правила R3 для Map 01
- главный художественный источник: утверждённый `MAP01_WORLD_ART_MASTER_SOURCE.png`, 1536×1152;
- WORLD_ART не масштабировать и не регенерировать;
- мир не строить процедурно и не превращать в повторяющийся tile carpet;
- техническая сетка: 12×9 = 108 секторов 128×128;
- автоматизация допустима только как технический перенос, нарезка, конвертация и проверка уже существующей авторской карты и вручную заданных логических решений;
- автоматическая генерация географии/дорог/объектов и image auto-classification запрещены;
- визуальное качество важнее экономии tileset/ROM;
- `main` не изменять до явной пользовательской приёмки R3.

## Конвейер каждой зоны
`WORLD_ART scope → TERRAIN/COLLISION → OBJECTS/EVENTS → SPAWN/runtime → integration check → next zone`.

## Текущий прогресс зон
### Z01 — Центральная деревня
Полный технический конвейер DONE; финальная пользовательская приёмка PENDING.

### Z03 — Северный водопад
Полный конвейер DONE; Z01↔Z03 integration check PASS.

### Z02 — Северо-западные руины
- WORLD_ART scope: DONE V1;
- exact master crop: `[0,0,640,512]`, 640×512;
- 20 секторов;
- TERRAIN/COLLISION: **DONE V1 / QA REVIEWED**;
- 80×64 = 5120 логических ячеек на слой;
- западная новая часть размечена вручную;
- восточный overlap с Z03: 2048 ячеек/слой, cell-for-cell PASS;
- terrain SHA-256: `4761366821ab36c526dc0a039e2d2742a2595b6c0b0c4e2bda7d7f0920d594d8`;
- collision SHA-256: `96293ae3d14f36b0e9ff271675b77ec49cc070e8118affb781a1075656c04769`;
- next: **OBJECTS + EVENTS AUTHORING**.

### Остальные зоны
Z04, Z05, Z06, Z07, Z08, Z09, Z10, Z11 — PENDING.
