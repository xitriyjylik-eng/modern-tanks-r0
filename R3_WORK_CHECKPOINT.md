# Modern Tanks R3 — рабочая точка продолжения

Дата фиксации: 2026-09-10
Рабочая ветка: `r3-map-camera`
Принятая ветка `main` не изменяется до успешной сборки и отдельной приёмки R3.

## Пройденные этапы

### Этап 1 — CI-проверка ресурсов: ЗАВЕРШЁН / PASS
Проверенный проектный commit: `062428b98996809397dcbad314799cd6a0f0a6d0`.
GitHub Actions run: `34427893276` / run #157.
- все 6 transport-chunks статического мира проверены;
- R3 overlay восстановлен;
- `R3 verification PASS`;
- точное совпадение тайлов с принятым R2-ландшафтом: `98.258%`.

### Этап 2 — запуск SGDK-сборки: ЗАВЕРШЁН / PASS
Фактически использованный toolchain:
- image tag: `registry.gitlab.com/doragasu/docker-sgdk:v2.11`;
- registry pull digest: `sha256:327ab838fbdf6bc741c6a7a11ee3c937cf1aaf1dc07a475995e89b741b6a830d`;
- local Docker image id: `sha256:e66837c905b7878e02ecfce1e3b906856dad5d751789c29b97555798f6b66972`;
- ResComp: `3.95`;
- compiler: `m68k-elf-gcc` for `-m68000`.
R3 `main.c` и `resources.res` реально восстановлены из hash-verified static payload и вошли в сборку.

### Этап 3 — компиляция/линковка R3: ЗАВЕРШЁН / PASS
- `src/main.c` компилируется с `-Wall -Wextra -O3` без ошибок и предупреждений игрового кода;
- ResComp 3.95 принимает R3 `TILESET/MAP/IMAGE`;
- `r3_region1_tileset`: `21000 bytes` raw;
- `r3_region1_map`: `17992 bytes`, `1469 metatiles`, `48 blocks`;
- `r3_battle_hud`: `2948 bytes` raw;
- общий ресурсный блок: `88442 bytes (86 KB)`;
- линкер, objcopy и sizebnd завершаются успешно.
Инфраструктурные предупреждения Pillow/Node не относятся к исполняемому коду игры.

### Этап 4 — воспроизводимость ROM: ЗАВЕРШЁН / PASS
Проверка выполнена не только внутри одного CI-запуска, но и повторным независимым job.

Исходный job:
- job id: `102716919501`;
- build commit: `062428b98996809397dcbad314799cd6a0f0a6d0`;
- внутри job созданы независимые копии `/tmp/sgdk-r3-a` и `/tmp/sgdk-r3-b`;
- обе отдельно собраны одним зафиксированным SGDK image;
- `cmp /tmp/sgdk-r3-a/out/rom.bin /tmp/sgdk-r3-b/out/rom.bin` завершился успешно;
- итоговый ROM SHA-256: `8af0e68d9e6afda7e751b086d0abcdbec79de325f4ce92ee3254de9660e7f516`.

Повторный независимый GitHub Actions job:
- job id: `102718485468`;
- повторно checkout именно build commit `062428b98996809397dcbad314799cd6a0f0a6d0`;
- Build A: PASS;
- Build B: PASS;
- внутренний `cmp` A/B: PASS;
- полученный ROM SHA-256 снова `8af0e68d9e6afda7e751b086d0abcdbec79de325f4ce92ee3254de9660e7f516`.

Дополнительная локальная сверка двух скачанных CI artifacts:
- ROM из исходного job и ROM из повторного job побайтово идентичны;
- `R3_SHA256.txt` идентичны;
- все 8 внутренних файлов artifact побайтово идентичны: `rom.bin`, `R3_BUILD_REPORT.md`, `R3_RESOURCE_SHA256.txt`, `R3_ROM_AUDIT.json`, `R3_SHA256.txt`, `R3_STATIC_MAP_REPORT.json`, `R3_TOOLCHAIN_IMAGE_DIGEST.txt`, `R3_TOOLCHAIN_IMAGE_ID.txt`.

GitHub ZIP-container digest различается (`2f3f...` против `1908...`) из-за метаданных/упаковки самого ZIP; это не различие результата сборки. Содержимое artifacts и ROM идентичны.

**Итог Этапа 4: PASS. R3 ROM детерминирован и воспроизводится побайтово.**

## Следующий шаг при команде «Продолжай»

Начать только **Этап 5 — техническая проверка ROM**:
1. проверить Mega Drive header и reset vectors;
2. проверить размер ROM и диапазоны заголовка;
3. проверить header checksum и SGDK full-ROM checksum/fold;
4. перепроверить SHA-256 и отсутствие очевидного повреждения структуры;
5. зафиксировать PASS/дефекты и остановиться, не переходя к Этапу 6.

## Правило работы по этапам и времени

На один запрос выполнять только один согласованный этап. На запрос использовать примерно до 20 минут активной работы. Если этап не завершён, перед ответом обновить этот checkpoint точной точкой продолжения.
