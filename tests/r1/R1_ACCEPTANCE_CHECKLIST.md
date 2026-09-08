# R1 CORE / STATE MACHINE — ACCEPTANCE CHECKLIST

Статус: **BUILD/CI PASS → TARGET PENDING**.

## CI baseline

- GitHub Actions run: `34176727527` — SUCCESS;
- commit: `d348e0518bfe74d47da6db705313e4a26c0fc891`;
- ROM SHA-256: `4fdc8d3d8ef9f723caf228b61f183b1fea927bee93727028f6e0a414cf6a726a`;
- ROM size: `131072` bytes;
- verifier: PASS.

## Scope

R1 должен содержать только:

- BOOT;
- TITLE;
- MAIN_MENU shell;
- TEST_BATTLE shell;
- GARAGE shell;
- переходы между состояниями;
- 3-button input abstraction;
- NTSC/PAL timing;
- error/debug layer;
- clean state enter/leave hooks;
- resource bank load/unload API.

R2 visual target, реальный battle renderer, tank art, world, AI, SRAM и audio не входят в R1.

## Manual path

1. После BOOT автоматически появляется TITLE.
2. START или A: TITLE → MAIN MENU.
3. D-Pad UP/DOWN двигает selector.
4. `PLAY [TEST BATTLE]` + A/START → TEST BATTLE shell.
5. B → MAIN MENU.
6. `GARAGE` + A/START → GARAGE shell.
7. B → MAIN MENU.
8. Input не теряется после многократных переходов.

## 100-transition soak

В MAIN MENU нажать **C**.

ROM должен автоматически выполнить ровно 100 переходов — 25 циклов:

`MENU → TEST_BATTLE → MENU → GARAGE → MENU`

После завершения:

- `SOAK: PASS 100/100`;
- `ERR: 00`;
- current state = MAIN_MENU;
- bank = MENU.

После soak снова проверить UP/DOWN, переход в TEST BATTLE, B назад, переход в GARAGE и B назад.

## Gate R1

Во время и после soak не должно быть:

- [ ] VRAM corruption;
- [ ] leaked sprites;
- [ ] freeze/crash;
- [ ] lost input;
- [ ] palette residue.

Target:

- [ ] MD Emu Games Gen PASS.

**R2 запрещён до прямого подтверждения пользователя R1.**
