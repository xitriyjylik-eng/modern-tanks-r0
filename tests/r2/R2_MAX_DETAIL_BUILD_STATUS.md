# R2 MAX DETAIL BUILD STATUS

Дата: **2026-09-08**

Статус: **BUILD/CI PASS / TARGET ACCEPTANCE PENDING**

## Причина rework

Предыдущие R2 candidates были визуально отклонены владельцем проекта как слишком упрощённые относительно locked `references/MAIN_MENU_REFERENCE.png`. MAX DETAIL — полный художественный rework, а не очередная малая правка.

## Target

- настоящий Mega Drive/Genesis ROM на SGDK 2.11;
- SG800 используется как MD/Mega Drive emulator host;
- тот же ROM предназначен для MD/Genesis эмуляторов на ПК;
- HDMI/4K не меняет внутренние Mega Drive VDP limits.

## Art direction

MAX DETAIL намеренно использует значительно большую часть доступного menu pattern budget. Экран рисуется в native 320×224 и включает:

- custom hand-defined pixel font вместо TTF downscale;
- крупный layered metallic MODERN TANKS logo;
- organic battlefield вместо заметного клетчатого ковра;
- winding river + shoreline;
- roads, bridges, brick/steel fortifications;
- clustered vegetation;
- craters/rubble;
- multiple distinct battlefield tanks;
- shells, muzzle flashes, explosions/smoke;
- steel central menu;
- canonical `ИГРАТЬ / ГАРАЖ / СТАТИСТИКА / НАСТРОЙКИ`;
- detailed T-1…T-4 cards;
- segmented stats;
- detailed minimap;
- selector animation и moving tank overlay.

Locked reference PNG не встроен, не downscale'ится и не изменяется. Granada assets/code не используются.

## Build evidence

- source commit: `53ef4dba355abbad5ad052ef1ee35345e17006bf`;
- GitHub Actions run: `34184514661`;
- job `build-r2`: SUCCESS;
- generated art validation: PASS;
- source/locked-art contract: PASS;
- SGDK build A: PASS;
- SGDK build B: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM verifier: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `52b0395fb023ebdaa08ca7e03152fa6b2040ed5c9a6b997509c618c4a9e95eba`;
- header checksum: `0xE671`;
- required checksum: `0xE671`;
- full-ROM XOR-fold: `0x0000`.

Generated resources were verified in CI by SHA-256. `r2_menu_bg.png` exactly matches project source SHA-256 `927534f927eaf17cd939a4977f20adbd8a705ca405f4c1a37511bd2a593376d0`.

## Pattern estimate

Conservative flip-canonical unique-tile estimate from project source:

- background: 857 tiles;
- largest selector: 22 tiles;
- moving overlay: 4 tiles;
- worst simultaneous project patterns: about **883 tiles / 28,256 bytes**;
- remaining versus conservative 44 KiB project-pattern ceiling: about **16,800 bytes**.

Это сознательно намного плотнее ранних R2 builds, но остаётся в разумном Mega Drive menu budget.

## Gate

CI не закрывает visual gate. Нужен прямой target-test владельца. Если экран всё ещё не устраивает относительно reference, продолжать R2. **R3 BLOCKED.**
