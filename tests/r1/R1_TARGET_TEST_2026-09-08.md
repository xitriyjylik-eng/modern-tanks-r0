# Modern Tanks R1 — target tests 2026-09-08

## Emulator

MD Emu Games Gen on Android.

## Functional result

Пользователь дважды подтвердил, что R1 функционально работает:

- TEST_BATTLE открывается и отображается;
- GARAGE открывается и отображается;
- MAIN_MENU ↔ TEST_BATTLE/GARAGE переходы работают;
- возврат B работает;
- видимого crash/VRAM corruption на предоставленных кадрах нет;
- video/debug layer показывает 60 Hz.

То есть state machine, input path и bank switching функционально работают.

## Target test 1 — исходный R1

На screenshots:

- TEST_BATTLE: `TRANS:003 ERR:03`, `LAST ERROR: PALETTE_RESIDUE`;
- GARAGE: `TRANS:005 ERR:05`, `LAST ERROR: PALETTE_RESIDUE`.

R1 не был принят, потому что gate требует отсутствие palette residue и `ERR:00`.

## FIX1

Commit: `16ea3ccad96b51e0514e88076ee6c4f00b752098`.

Изменения:

- all 64 CRAM entries cleared through one `PAL_setColors(0, palette_black, 64, CPU)`;
- `VDP_waitFIFOEmpty()` after clear;
- `VDP_waitFIFOEmpty()` before `PAL_getColors()` readback.

CI run `34177478564`: SUCCESS.

## Target test 2 — FIX1

Пользователь повторно проверил ROM и сообщил, что поведение визуально осталось нормальным, но debug self-check всё ещё рос вместе с переходами:

- TEST_BATTLE: `TRANS:007 ERR:07`, `LAST ERROR: PALETTE_RESIDUE`;
- GARAGE: `TRANS:009 ERR:09`, `LAST ERROR: PALETTE_RESIDUE`.

Следовательно предположение, что достаточно только drain FIFO, было неполным. FIX1 не закрывает defect.

## Уточнённая причина

CRAM cleanup/readback всё ещё выполнялся при включённом active display. Для R1 это ненадёжная диагностическая транзакция: мы пытались доказать состояние CRAM в момент, когда VDP одновременно обслуживает видимый scanout.

SGDK сам использует временное отключение display для безопасных/быстрых операций видеопамяти в `VDP_resetScreen()`.

## FIX2

Commit: `bc858a619de76a1f5c3112859914ea132e9bf7be`.

Теперь каждый state-bank transition выполняется как blanked transaction:

1. `VDP_setEnable(FALSE)`;
2. drain FIFO;
3. state leave + planes/sprites/CRAM cleanup;
4. CRAM readback с interrupts masked вокруг `PAL_getColors()`;
5. загрузка нового bank и draw нового state;
6. drain FIFO;
7. `VDP_setEnable(TRUE)`.

Никакого R2 content, старого DEV-кода или Granada assets/code не добавлено.

### FIX2 CI

GitHub Actions run: `34178302167` — **SUCCESS**.

- source contract: PASS;
- build A: PASS;
- build B: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM audit: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `78f73ba4ccabbca43433735538123de82b0097be9cb2dd5f7704838b103552c7`;
- header checksum: `0xAC94`;
- required checksum: `0xAC94`;
- SGDK full-ROM XOR-fold: `0x0000`.

## Required target result for FIX2

До soak обычные переходы должны оставлять `ERR:00`.

После C в MAIN_MENU и завершения 100 переходов:

- `SOAK: PASS 100/100`;
- `ERR:00`;
- `STATE: MAIN_MENU`;
- `BANK: MENU`;
- manual input всё ещё работает.

До этого подтверждения **R1 остаётся TARGET RETEST PENDING, R2 BLOCKED**.
