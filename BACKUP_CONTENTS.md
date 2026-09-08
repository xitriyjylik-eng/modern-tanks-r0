# FULL BACKUP CONTENTS

Этот проектный backup предназначен для сохранения и переноса разработки Modern Tanks в новую сессию/машину без потери контекста.

## Что должно находиться в полном архиве

### `PROJECT_SOURCE/`

Полный snapshot репозитория после фиксации приёмки R2. Он содержит:
- source code;
- SGDK resource declarations;
- deterministic R2 asset generator;
- GitHub Actions workflows;
- design/plan/technical/tests документы;
- locked visual references;
- исторические recovery/служебные материалы, которые уже присутствуют в репозитории.

`PROJECT_SOURCE/` является исходной рабочей копией. Финальные R2 assets генерируются из неё штатным generator/CI и поэтому source snapshot сохраняется **до** запуска генератора.

### `ACCEPTED_R2_GENERATED_RESOURCES/`

Снимок реально сгенерированных финальных R2 ресурсов:
- final static `r2_menu_bg.png` после удаления статичных дублей анимируемых объектов;
- river 0..11;
- right flag 0..11;
- upper fire 0..7;
- lower fire 0..7;
- trees 0..11;
- selector и top-right patch;
- generator diagnostics.

### `ACCEPTED_R2_BUILD/`

- `Modern_Tanks_R2_ACCEPTED.bin`;
- ROM SHA-256;
- ROM audit JSON;
- reproducibility marker;
- SGDK image id/digest;
- resource SHA manifest;
- resource budget;
- build report.

### `STATUS/`

Копии главных handoff-файлов:
- `00_CURRENT_STATUS_READ_FIRST.md`;
- `README_RU.md`;
- `SESSION_HANDOFF_CURRENT.md`;
- `WHAT_DONE_WHAT_LEFT.md`;
- `R2_ACCEPTANCE_FINAL.md`;
- `PROJECT_PROGRESS_ACCEPTED_R2.md`;
- `NEXT_R3_SCOPE.md`.

### Корневой manifest

`FILE_MANIFEST_SHA256.txt` содержит SHA-256 всех файлов внутри backup package, кроме самого manifest на момент вычисления.

## Контрольная точка

Принятый игровой R2 baseline: `a1faa7d567ceb7f5506005b354da28f5c1ea0cee`.
Документационный backup commit может быть новее, но gameplay/SGDK source относительно принятого baseline обязан оставаться неизменным; backup workflow проверяет это через `git diff` для `sgdk/`.

## Следующая разработка

После распаковки сначала читать `STATUS/00_CURRENT_STATUS_READ_FIRST.md`. Затем `STATUS/NEXT_R3_SCOPE.md`. Первый незавершённый этап — R3.
