# Modern Tanks R3 — рабочая точка продолжения

Дата фиксации: 2026-09-10
Рабочая ветка: `r3-map-camera`
Принятая ветка `main` не изменяется до успешной сборки и отдельной приёмки R3.

## Пройденные этапы

### Этап 1 — CI-проверка ресурсов: ЗАВЕРШЁН
Проверенный проектный commit: `062428b98996809397dcbad314799cd6a0f0a6d0`.
GitHub Actions run: `34427893276` / run #157.
- все 6 transport-chunks статического мира проверены;
- R3 overlay восстановлен;
- `R3 verification PASS`;
- точное совпадение тайлов с принятым R2-ландшафтом: `98.258%`.

### Этап 2 — запуск SGDK-сборки: ЗАВЕРШЁН
Проверено по фактическому логу run #157, а не только по YAML.

Фактически использованный toolchain:
- image tag: `registry.gitlab.com/doragasu/docker-sgdk:v2.11`;
- registry pull digest: `sha256:327ab838fbdf6bc741c6a7a11ee3c937cf1aaf1dc07a475995e89b741b6a830d`;
- local Docker image id: `sha256:e66837c905b7878e02ecfce1e3b906856dad5d751789c29b97555798f6b66972`;
- ResComp: `3.95`;
- compiler: `m68k-elf-gcc` for `-m68000`.

Проверена структура SGDK-проекта: `src/`, `res/`, `r3ci/`, `tools/` и build scripts присутствуют.

Особенность хранения R3:
- repository `sgdk/src/main.c` и `sgdk/res/resources.res` остаются базовыми R2-файлами;
- `sgdk/tools/r3_ci_overlay_small.py restore` до сборки декодирует hash-verified статический R3 payload из `sgdk/r3ci` и заменяет ими `src/main.c` и `res/resources.res`;
- это lossless transport, не процедурная генерация карты.

Подтверждение фактического участия R3 в сборке:
- restore завершился сообщением `R3 CI overlay restored from static authored payload`;
- ResComp обработал `TILESET r3_region1_tileset`, `MAP r3_region1_map`, `IMAGE r3_battle_hud`;
- resource summary: `88442 bytes (86 KB)`;
- затем `m68k-elf-gcc` реально скомпилировал `src/main.c` в `out/src/main.o`;
- линкер включил `out/res/resources.o` и `out/src/main.o` в ROM.

**Итог Этапа 2: PASS. SGDK-сборка действительно запускается и получает восстановленные R3-код и ресурсы.**

## Следующий шаг при команде «Продолжай»

Начать **Этап 3 — проверить компиляцию R3 и наличие/отсутствие ошибок компилятора**:
1. отдельно разобрать вывод `m68k-elf-gcc`, linker и ResComp на warnings/errors;
2. проверить, нет ли скрытых проблем API SGDK, типов, MAP, палитр и VRAM на compile/link уровне;
3. если ошибки есть — исправить и пересобрать; если ошибок нет — зафиксировать PASS;
4. остановиться после Этапа 3, не переходя к проверке воспроизводимости Этапа 4.

## Правило работы по этапам и времени

На один запрос выполнять только один согласованный этап. На запрос использовать примерно до 20 минут активной работы. Если этап не завершён, перед ответом обновить этот checkpoint точной точкой продолжения.
