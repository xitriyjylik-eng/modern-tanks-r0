# R2 resource budget — Focused Menu / Tank Reference Rework

R2 remains a native **320×224 Mega Drive** menu bank. Locked reference PNGs are visual targets only: they are not embedded, resized, modified, or used as ROM textures. Granada assets/code are not used.

## Current visual structure

- full-screen static battlefield background;
- metallic `MODERN TANKS` logo;
- four canonical menu rows: `ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ`;
- hand-drawn top-down tank silhouettes based on the locked `TANKS_DETAILED_REFERENCE.png` art direction;
- selector overlay/pulse.

Removed by owner direction:

- the lower T-1..T-4 class-card strip;
- parameter bars;
- lower minimap;
- decorative moving menu tank.

Those elements had no R2 gameplay role. Tank/class selection belongs to GARAGE; map/mission context belongs outside the main menu.

## Runtime transfer policy

- full 320×224 menu image loads only on MAIN_MENU entry;
- project VDP sprite-engine payload in R2 menu: **0 sprites**;
- no moving battlefield overlay remains;
- recurring visual work is limited to selector navigation/pulse;
- accepted R1 menu-bank teardown/CRAM/sprite cleanup remains unchanged.

## Budget validation

GitHub Actions computes the exact current unique 8×8 tile count from the generated indexed PNGs on every R2 build. CI fails if the conservative project-pattern estimate exceeds the project **44 KiB** ceiling. The generated `R2_RESOURCE_BUDGET.md` inside each CI artifact is therefore authoritative for the exact candidate build.
