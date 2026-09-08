# R2 resource budget

Generated art is original R2 project art derived from the composition goals of `MAIN_MENU_REFERENCE.png`; the locked reference PNG itself is not embedded, resized, altered or copied into the ROM.

The six R2 indexed PNG resources share one 4×16-color Mega Drive palette plan. `rescomp` uses tile-level palette selection and `ALL` duplicate/flip optimisation.

## Project-owned tile payload

- `r2_menu_bg.png`: 412 unique tiles = 13,184 bytes.
- selected row resources: 19 / 20 / 28 / 26 tiles; only one is resident at a time, worst = 28 tiles = 896 bytes.
- `r2_anim_tank.png`: 4 tiles = 128 bytes.
- worst simultaneous R2 menu art: **444 tiles = 14,208 bytes** of project-owned pattern data.
- conservative 44 KiB pattern-budget comparison: **30,848 bytes free**.

Plane tables, SGDK system/font reservations and other VDP tables are separate from this project-owned pattern figure. R2 intentionally stays far below the conservative 44 KiB project pattern ceiling so later stages are not forced to inherit an overpacked menu bank.

## Sprites / DMA

- SGDK sprite engine payload in R2 menu: 0 project sprites; the scripted tank is a 2×2-tile Plane A overlay.
- worst moving overlay update: 4 tiles / 128 bytes plus a 2×2 tilemap update every 8 logic ticks.
- selected row redraw: at most 28 unique tiles / 896 bytes plus 17×2 tilemap cells, only on menu navigation.
- full menu image is loaded only on `MAIN_MENU` entry, never every frame.

CI trigger note: this file is part of the R2 `sgdk/**` source contract and its normal contents update intentionally triggers the R2 GitHub Actions build after the atomic R2 tree commit.
