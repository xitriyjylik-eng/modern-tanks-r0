# Z03 — TERRAIN + COLLISION

Дата: 2026-09-10  
Статус: **IMPLEMENTED V2 / QA REVIEWED**.

## Участок
Северный водопад, верхняя река, острова, северный мост и стык с Z01. WORLD_ART не изменялся.

## Реализовано
- логическая сетка 96×64 ячейки по 8×8 px = 6144 ячеек на слой;
- TERRAIN и COLLISION подготовлены как полный grid;
- 24 sector-пары terrain/collision подготовлены;
- overlap с Z01: 2560 ячеек каждого слоя унаследованы буквально cell-for-cell;
- вода блокирует движение;
- мост из overlap Z01 остаётся проезжим;
- крупные скальные берега/выходы породы блокируют движение;
- фрагмент северо-западных руин имеет CONDITIONAL collision;
- верхняя физическая граница карты имеет MAP_BORDER.

## Автоматизация
Автоматизация не создаёт географию и не меняет WORLD_ART. Она используется только как технический перенос уже существующей авторской карты на 8px logic grid, для уточнения контуров, sector slicing, hash и validation.

## Проверка
- validation: PASS;
- overlap TERRAIN с Z01: PASS;
- overlap COLLISION с Z01: PASS;
- sector layer files: 48;
- TERRAIN SHA-256: `48de0e7a6a187fd48827dfe8dc23f9dc8c980b7536e9506fff77b2cc76862c8e`;
- COLLISION SHA-256: `74763706715a20fa8c808793f60a1126c964c9d64f1749ea6af449b1233a8e7c`.

Следующий этап: **Z03 OBJECTS + EVENTS**.
