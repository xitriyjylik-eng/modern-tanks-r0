# Modern Tanks — R0

Этот репозиторий содержит чистую перезапуск-сборку проекта **Modern Tanks** для Sega Mega Drive / Genesis на SGDK 2.11.

Текущий этап: **R0 HARDWARE PROBE — SOURCE V3 READY**.

## Что проверяет R0

R0 намеренно не является игрой. Это минимальный аппаратный/SDK-пробник перед переносом игровых механик:

1. **R0A** — стандартный SGDK startup, VDP и raw `VDP_waitVSync()` без системного VBlank pipeline.
2. **R0B** — переход на штатный `SYS_doVBlankProcess()`.
3. **R0C** — включение `JOY_SUPPORT_3BTN`, чтение D-Pad/A/B/C/START и визуальная реакция.

## Почему так

Предыдущий DEV-подход с самодельным bootstrap/opcode-emitter удалён. Новая реализация строится от проверенной базы **Granada** и штатной архитектуры SGDK.

Пока R0 ROM не пройдёт аппаратный/эмуляторный acceptance gate, перенос карты, танков, AI, оружия, SRAM и прочих игровых систем запрещён.

## Сборка

### Docker

```sh
cd sgdk
./build_r0_docker.sh
```

### GitHub Actions

Workflow: `.github/workflows/r0-build.yml`

Он выполняет две независимые сборки SGDK 2.11 из одного exact Docker image ID, сравнивает ROM побайтно, проверяет заголовок/чексум и публикует артефакт.

## Документы

- `00_START_HERE_NEXT_SESSION.md` — точка входа для новой сессии.
- `SESSION_HANDOFF_CURRENT.md` — текущее состояние и следующий шаг.
- `design/GAME_DESIGN_FROZEN.md` — замороженная идея игры.
- `plan/REBUILD_MASTER_PLAN.md` — новый rebuild-план.
- `tests/r0/R0_ACCEPTANCE_CHECKLIST.md` — обязательные критерии R0.
