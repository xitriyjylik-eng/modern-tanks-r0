# NEXT R3 SCOPE — Battle Renderer / HUD

Статус: **NEXT / UNBLOCKED / NOT STARTED**.

R3 начинается только после принятого R2. R2 визуально и технически закрыт; этот этап не является поводом переделывать главное меню.

## Цель R3

Заменить TEST_BATTLE shell на настоящий renderer/HUD foundation, пригодный для дальнейшего игрового vertical slice, но не пытаться преждевременно реализовать весь combat R6.

Визуальный ориентир: `references/COMBAT_REFERENCE.png`.

## Целевая геометрия экрана

- полный экран: 320×224;
- battlefield: 224×192;
- right HUD: 96×192;
- bottom event log: 320×32;
- camera center battlefield: примерно 112×96, а не центр всего 320px экрана.

## Реализовать

1. Plane B — базовый слой мира: земля, дороги, вода и нижний terrain.
2. Plane A — верхний world layer: декор/объекты, которые логически находятся над базовым terrain.
3. Window/HUD layout — фиксированная правая панель и нижний event log, не зависящие от camera scroll.
4. Camera — перемещение по миру с центром относительно battlefield viewport.
5. Map-edge streaming / tilemap update foundation для карты больше одного экрана.
6. HUD framework: панели, полосы/значения, места под иконки и состояние танка.
7. Minimap framework внутри HUD, без возврата удалённой мини-карты из главного меню.
8. Event log framework в нижней полосе.
9. World sprite clipping/presentation discipline: игровые sprites не должны визуально залезать на HUD/log.
10. VRAM ownership/banks для battle renderer с чистой загрузкой и выгрузкой через уже принятый R1 lifecycle.

## Не входит в R3

- полный набор T-1…T-8 art — R4;
- полноценная Region 1 content/map — R5;
- полный combat/AI/objectives — R6;
- bosses, SRAM, audio и meta systems — более поздние этапы.

## Acceptance gate R3

R3 нельзя закрыть, пока не выполнено всё ниже:

- camera центрируется относительно 224px battlefield, а не 320px общего экрана;
- HUD и bottom log не прокручиваются вместе с миром;
- world sprites не рисуются поверх HUD;
- движение/scroll проверены во всех 4 направлениях;
- минимум 10 минут непрерывного scroll test без tile corruption/VRAM artifacts;
- переход MAIN_MENU → TEST_BATTLE → MAIN_MENU не оставляет palette/sprite/tile residue;
- NTSC и PAL timing не ломают renderer/update loop;
- CI собирает две идентичные SGDK 2.11 ROM и проходит ROM audit;
- после технического gate владелец получает ROM для фактической проверки.

## Качество

Не снижать принятую визуальную планку R2 ради упрощения. Оптимизация должна идти через корректное Mega Drive resource planning, metatiles, banking, streaming и palette discipline, а не через искусственное обеднение графики.
