# R2 resource budget — Visual Rework 1

The runtime artwork is original project-owned pixel art generated directly at **320×224**. The locked `MAIN_MENU_REFERENCE.png` is a visual/composition target only: it is not embedded, resized, modified, or used as a ROM asset. Granada assets/code are not used.

The six generated indexed PNG resources use a four-palette Mega Drive plan. Each 8×8 tile is normalized to one 16-color palette before SGDK ResComp processes it.

## Conservative project-owned pattern payload

Raw unique-tile analysis before ResComp duplicate/flip optimization:

- `r2_menu_bg.png`: **628 unique 8×8 tiles** maximum = 20,096 bytes.
- selected-row overlays: 22 / 20 / 26 / 26 raw unique tiles; only one selector is resident at a time, conservative worst = **26 tiles = 832 bytes**.
- `r2_anim_tank.png`: **4 tiles = 128 bytes**.
- conservative simultaneous upper bound: **658 tiles = 21,056 bytes**.
- against a conservative 44 KiB project pattern ceiling (45,056 bytes): **at least 24,000 bytes remain free** before ResComp duplicate/flip savings.

This is deliberately conservative. SGDK ResComp may reduce the actual tile payload through duplicate and flip optimization; the acceptance decision does not depend on optimistic compression.

Plane tables, SGDK font/system reservations, and other VDP structures are separate from this project-owned pattern estimate.

## Sprites / recurring transfer

- Project VDP sprite-engine payload in the R2 menu: **0 sprites**. The scripted background tank is a 2×2 Plane A overlay.
- Moving overlay update: 4 tiles / 128 bytes plus a 2×2 tilemap update every 8 logic ticks.
- Selector overlay: 104×16 = 13×2 tile cells; it is redrawn only on navigation.
- Full 320×224 menu image is loaded only on `MAIN_MENU` entry, never every frame.

## Visual density added in Visual Rework 1

The increased budget is intentional and funds the features missing in the first R2 candidate: winding river/shoreline, forest clusters, bridges, brick/steel fortifications, craters/debris, multiple battlefield tanks, shell traces, explosions/smoke, dimensional logo frame, narrower reference-like menu composition, detailed T-1..T-4 silhouettes, segmented parameter bars, and a more informative minimap.

R3 assets remain excluded. R2 stays a standalone menu bank and must still unload cleanly when entering TEST_BATTLE or GARAGE.
