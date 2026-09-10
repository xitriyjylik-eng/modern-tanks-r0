# Z02 — TERRAIN + COLLISION

Дата: 2026-09-10  
Статус: **IMPLEMENTED V1 / QA REVIEWED**

- сетка 80×64 по 8×8 px = 5120 ячеек/слой;
- 20 sector-пар;
- новая западная часть размечена вручную по утверждённому WORLD_ART;
- восточный overlap Z02↔Z03: 256×512 px = 2048 ячеек/слой, literal cell-for-cell inheritance — PASS;
- руины: CONDITIONAL; скалы: CLIFF_BLOCK; верхняя и левая границы: MAP_BORDER;
- image auto-classification: NO; procedural geography: NO;
- TERRAIN SHA-256: `4761366821ab36c526dc0a039e2d2742a2595b6c0b0c4e2bda7d7f0920d594d8`;
- COLLISION SHA-256: `96293ae3d14f36b0e9ff271675b77ec49cc070e8118affb781a1075656c04769`;
- validation: PASS.

Полный воспроизводимый payload находится в `map01z02layersci_exact/`. Следующий этап: **OBJECTS + EVENTS Z02**.
