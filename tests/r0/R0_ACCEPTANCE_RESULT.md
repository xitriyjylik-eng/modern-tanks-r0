# R0 HARDWARE PROBE — ACCEPTANCE RESULT

Дата закрытия: **2026-09-08**  
Статус: **ACCEPTED / CLOSED**

## Build / CI

- SGDK 2.11 Docker CI: PASS.
- Две независимые сборки ROM: byte-for-byte identical.
- Независимый SGDK header/checksum audit: PASS.
- R0 ROM SHA-256: `1b5de098a33a0ac54256c8680acc0440bdec76ae5c74fa2551bff7050b24ef11`.
- Успешный GitHub Actions run: `34175976629`.
- Успешный commit: `10bd881926743a88c8a211919b176505cc95054c`.

## Target test — MD Emu Games Gen / Android

Пользователь лично подтвердил:

- ROM запускается стабильно;
- изображение отображается правильно;
- R0A PASS;
- R0B PASS;
- D-Pad работает;
- A/B/C/START работают.

X/Y/Z не считаются ошибкой: R0 намеренно использует `JOY_SUPPORT_3BTN`, а 6-button input не входит в scope R0.

## Решение владельца проекта

Пользователь явно указал: **«Считай R0 Hardware Probe полностью ACCEPTED и закрывай этап R0.»**

Следующая разрешённая стадия: **R1 Core / State Machine**.
R2 запрещён до отдельного подтверждения R1 пользователем.
