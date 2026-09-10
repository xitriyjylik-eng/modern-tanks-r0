# Modern Tanks R3 — рабочая точка продолжения

Дата фиксации: 2026-09-10  
Рабочая ветка: `map01-implementation-v1`  
`main`: **НЕ ИЗМЕНЯТЬ** до явной пользовательской приёмки R3.

## Текущий статус R3
R3: **IN PROGRESS / MAP 01 PRODUCTION / NOT ACCEPTED**.

Старый R3-кандидат 1024×768 технически доказал battle renderer, HUD, плавную камеру, MAP lifecycle и устойчивость в BlastEm, но его художественная карта отклонена пользователем. Поэтому он остаётся только технической базой и не является финальной картой R3.

Техническая база, которую сохраняем:
- battlefield 224×192, right HUD 96×192, bottom log 320×32;
- fixed-point acceleration/friction камеры;
- PAL/NTSC compensation;
- `MAP_scrollTo()` / MAP streaming foundation;
- корректный MAP create/release lifecycle;
- HUD opacity fix;
- SGDK 2.11 build foundation;
- реальный BlastEm NTSC/PAL deep test и 12m45s soak старой технической базы — PASS.

Старые художественные показатели вроде процента совпадения тайлов с R2 больше не используются как критерий качества.

## Что теперь входит в R3
R3 ведёт весь конечный производственный маршрут Map 01:
1. эталон и география;
2. production structure;
3. WORLD_ART по зонам;
4. TERRAIN + COLLISION;
5. OBJECTS + EVENTS;
6. SPAWN + runtime data;
7. интеграция всей карты в streaming renderer;
8. плавность камеры, соседние sector loads, seams и latency;
9. финальный NTSC/PAL regression + soak;
10. пользовательская визуальная/игровая приёмка.

Подробный трекер: `R3_MAP01_PRODUCTION_PIPELINE.md`.

## Актуальная художественная и техническая база Map 01
- authoritative WORLD_ART: 1536×1152;
- без масштабирования и регенерации;
- техническая сетка: 12×9 = 108 секторов 128×128;
- старый план 4096×3072 / 192 сектора отменён;
- процедурная генерация мира запрещена;
- если единый SGDK MAP ухудшает качество или задерживает вход, применять sector/page streaming, а не упрощать графику.

## Прогресс зон
### Z01 — Центральная деревня
WORLD_ART → TERRAIN/COLLISION → OBJECTS/EVENTS → SPAWN/runtime → отдельный SGDK/BlastEm proof: **DONE**.

### Z03 — Северный водопад / верхняя река / северный мост
- WORLD_ART scope 768×512: **DONE**;
- TERRAIN/COLLISION 96×64 cells: **DONE V2**;
- overlap с Z01: 2560 cells/layer inherited cell-for-cell — **PASS**;
- 24 sector-пары terrain/collision подготовлены;
- validation: **PASS**;
- следующий шаг: **OBJECTS + EVENTS**.

Остальные зоны идут последовательно после интеграционной проверки текущей зоны.

## Правило против зацикливания
Каждая зона проходит только конечный конвейер:
`WORLD_ART scope → TERRAIN/COLLISION → OBJECTS/EVENTS → SPAWN/runtime → integration check → next zone`.

CI, fuzzy similarity и вспомогательные screenshot-метрики — только инструменты диагностики. Они не являются отдельным этапом и не должны задерживать создание карты без реальной регрессии.

## Acceptance gate
R3 становится `ACCEPTED/CLOSED` только когда целевая Map 01 полностью работает на финальном runtime, камера и загрузка приемлемы, финальный NTSC/PAL regression/soak пройден и пользователь явно подтвердил внешний вид и ощущения.
