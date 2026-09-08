# R1 BUILD STATUS

Статус: **BUILD/CI PASS / TARGET ACCEPTANCE PENDING**

## Реализация

`sgdk/src/main.c` содержит только R1 core-shell:

- BOOT / TITLE / MAIN_MENU / TEST_BATTLE / GARAGE;
- explicit enter/leave hooks;
- state-owned resource bank API;
- unload очищает BG_A, BG_B, WINDOW, scroll, CRAM и VDP sprite allocation;
- внутренние palette residue / VDP sprite leak checks;
- 3-button input abstraction (`held/pressed/released`);
- fixed 60 Hz logical clock с PAL compensation;
- debug/error overlay;
- встроенный C → 100-transition soak.

## GitHub Actions CI — PASS

- repository: `xitriyjylik-eng/modern-tanks-r0`;
- source commit: `d348e0518bfe74d47da6db705313e4a26c0fc891`;
- run: `34176727527`;
- job: `build-r1` — SUCCESS;
- SGDK: 2.11;
- container digest: `sha256:327ab838fbdf6bc741c6a7a11ee3c937cf1aaf1dc07a475995e89b741b6a830d`;
- exact image ID: `sha256:e66837c905b7878e02ecfce1e3b906856dad5d751789c29b97555798f6b66972`;
- build A: PASS;
- build B: PASS;
- A/B byte comparison: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `4fdc8d3d8ef9f723caf228b61f183b1fea927bee93727028f6e0a414cf6a726a`;
- header checksum: `0xF22B`;
- required header checksum: `0xF22B`;
- SGDK full-ROM XOR-fold: `0x0000`;
- independent ROM verifier: PASS;
- artifact: `Modern_Tanks_R1_Core_Menu`.

## Budget / isolation facts for R1

- project-owned rescomp tile payload: 0 bytes;
- project-owned VDP sprite payload: 0 bytes;
- final R2 menu art: not loaded;
- no gameplay/map/tank/AI/SRAM/audio implementation;
- no per-frame gameplay DMA workload;
- cleanup occurs only on state transitions.

## Gate

CI доказал воспроизводимую сборку и корректный ROM header/checksum, но не может заменить target runtime test.

**R1 НЕ ACCEPTED до проверки владельцем в MD Emu Games Gen. R2 BLOCKED.**
