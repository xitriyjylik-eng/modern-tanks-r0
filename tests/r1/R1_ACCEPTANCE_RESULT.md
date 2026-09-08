# R1 ACCEPTANCE RESULT

Дата: **2026-09-08**

Статус: **ACCEPTED / CLOSED**

## Финальный target ROM

- stage: R1 Core / State Machine FIX2;
- source commit: `bc858a619de76a1f5c3112859914ea132e9bf7be`;
- GitHub Actions run: `34178302167`;
- SGDK: 2.11;
- ROM size: `131072` bytes;
- ROM SHA-256: `78f73ba4ccabbca43433735538123de82b0097be9cb2dd5f7704838b103552c7`;
- header checksum: `0xAC94`;
- independent ROM verifier: PASS;
- two clean CI builds: byte-for-byte identical.

## Target test — MD Emu Games Gen / Android

Владелец проекта повторно проверил FIX2 ROM и предоставил screenshots.

Подтверждено:

- MAIN_MENU работает;
- TEST_BATTLE открывается и возвращается в меню;
- GARAGE открывается и возвращается в меню;
- state/bank switching работает;
- после обычных переходов `ERR:00`;
- 100-transition soak завершён: `SOAK: PASS 100/100`;
- после soak: `STATE: MAIN_MENU`;
- после soak: `BANK: MENU`;
- после soak: `ERR:00`;
- счётчик переходов на финальном screenshot: `TRANS:114`, то есть ручное использование продолжилось после автоматического soak без появления ошибок;
- видимых VRAM/palette/sprite corruption, зависаний или потери input не наблюдалось.

## О строке LAST ERROR

На screenshots присутствует `LAST ERROR: R1_ITEM_NOT_IMPLEMENTED` при `ERR:00`.

Это не runtime error и не увеличивает `errorCount`. Строка выставляется при попытке открыть намеренно заблокированные в R1 пункты `STATISTICS [R1 LOCKED]` или `OPTIONS [R1 LOCKED]`. Это диагностическое информационное сообщение с неудачным названием поля и не нарушает R1 gate.

## Итог gate

Gate R1 требовал 100 переходов между MENU / TEST_BATTLE / GARAGE без VRAM corruption, leaked sprites, зависаний, потерянного input и palette residue.

Финальный FIX2 target-test удовлетворяет этим требованиям.

**R1 CORE / STATE MACHINE = ACCEPTED / CLOSED.**

R2 MAIN MENU VISUAL TARGET теперь разблокирован, но в рамках этого acceptance commit не реализуется и не изменяется.
