# R3 — MAP 01 PRODUCTION PIPELINE

Дата: 2026-09-10  
Статус R3: **IN PROGRESS / MAP 01 PRODUCTION / NOT ACCEPTED**.

## Для чего теперь ведётся R3
R3 должен довести уже проверенную техническую основу battle renderer / HUD / smooth camera до полноценной большой Map 01 с утверждённой графикой, логическими слоями и потоковой работой без долгой загрузки.

Старый кандидат R3 1024×768 сохраняется только как техническое доказательство камеры, MAP lifecycle, HUD и BlastEm soak. Его художественная карта отклонена и не является целевым WORLD_ART.

## Постоянные правила R3 для Map 01
- главный художественный источник: утверждённый `MAP01_WORLD_ART_MASTER_SOURCE.png`, 1536×1152;
- WORLD_ART не масштабировать и не регенерировать;
- мир не строить процедурно и не превращать в повторяющийся tile carpet;
- техническая сетка: 12×9 = 108 секторов 128×128; границы игрок не должен видеть;
- автоматизация допустима только как технический перенос, нарезка, конвертация и проверка уже существующей авторской карты;
- визуальное качество важнее экономии tileset/ROM;
- если один SGDK MAP не сохраняет качество и скорость, использовать sector/page streaming, а не упрощать карту;
- `main` не изменять до явной пользовательской приёмки R3.

## Общий конечный маршрут R3
1. Эталон и география Map 01 — **DONE**.
2. Production-структура Map 01 и sector/layer contract — **DONE**.
3. WORLD_ART по зонам — **IN PROGRESS**.
4. TERRAIN + COLLISION по зонам — **IN PROGRESS**.
5. OBJECTS + EVENTS по зонам — **IN PROGRESS**.
6. SPAWN + runtime data по зонам — **IN PROGRESS**.
7. Интеграция всей Map 01 в battle renderer/streaming — **PENDING**.
8. Камера, соседние sector loads, seams, latency, NTSC/PAL — **PENDING FINAL MAP**.
9. Полный emulator regression + soak всей карты — **PENDING FINAL MAP**.
10. Пользовательская визуальная/игровая приёмка — **PENDING**.

## Конвейер каждой зоны
`WORLD_ART scope → TERRAIN/COLLISION → OBJECTS/EVENTS → SPAWN/runtime → integration check → next zone`.

CI и диагностические метрики не являются самостоятельной целью. Они не должны останавливать создание карты, если проверяемая функция уже доказана и нет реальной регрессии.

## Текущий прогресс зон
### Z01 — Центральная деревня
- WORLD_ART: DONE;
- TERRAIN/COLLISION: DONE;
- OBJECTS/EVENTS: DONE;
- SPAWN/runtime: DONE;
- отдельная SGDK/BlastEm technical proof: DONE;
- финальная пользовательская приёмка как части всей карты: PENDING.

### Z03 — Северный водопад / верхняя река / северный мост
- WORLD_ART scope: DONE, exact crop 768×512;
- TERRAIN/COLLISION: DONE V2;
- overlap с Z01: 2560 cells/layer inherited cell-for-cell — PASS;
- OBJECTS/EVENTS: DONE V1 — 10 objects, 8 events, 24 sector indices, validation PASS;
- переходы: Z03→Z01, Z03→Z02, Z03→Z04, северный reserved REGION_2;
- SPAWN/runtime: NEXT;
- integration check: PENDING.

### Остальные зоны
Z02, Z04, Z05, Z06, Z07, Z08, Z09, Z10, Z11 — PENDING в порядке связности с уже готовыми зонами.

## Acceptance gate R3
R3 нельзя считать `ACCEPTED/CLOSED`, пока одновременно не выполнены:
- вся целевая Map 01 использует утверждённый WORLD_ART, а не старый R3 placeholder;
- все нужные зоны имеют production logic layers;
- переходы между соседними секторами визуально и логически непрерывны;
- вход в карту не имеет неприемлемой задержки;
- камера остаётся плавной на реальной полной карте;
- NTSC/PAL regression и soak пройдены на финальной карте;
- владелец явно подтвердил внешний вид и ощущения.
