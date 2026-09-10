# Modern Tanks R3 — рабочая точка продолжения

Дата фиксации: 2026-09-10
Рабочая ветка: `r3-map-camera`
Принятая ветка `main` не изменяется до успешной финальной проверки и отдельной пользовательской приёмки R3.

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
- compiler: `m68k-elf-gcc -m68000`.
R3 `main.c` и `resources.res` реально восстанавливаются из hash-verified static payload и входят в сборку. Payload — только lossless transport, не процедурная генерация карты.

### Этап 3 — компиляция/линковка R3: ЗАВЕРШЁН / PASS
- `src/main.c` компилируется с `-Wall -Wextra -O3`;
- ResComp принимает R3 TILESET/MAP/IMAGE;
- карта: `1469 metatiles`, `48 blocks`;
- linker, objcopy и sizebnd проходят успешно.

### Этап 4 — воспроизводимость исходного R3 ROM: ЗАВЕРШЁН / PASS
До графического исправления HUD два независимых Build A/B совпали byte-for-byte.
SHA-256 той версии: `8af0e68d9e6afda7e751b086d0abcdbec79de325f4ce92ee3254de9660e7f516`.
После Этапа 8 ROM закономерно изменился из-за нового непрозрачного HUD-шрифта; окончательную повторную reproducibility-проверку новой версии выполнить на Этапе 9.

### Этап 5 — технический аудит ROM: ЗАВЕРШЁН / PASS WITH WARNINGS
Для исходной R3-версии:
- размер: `262144 bytes`;
- initial SSP: `0xE1000000`;
- reset PC: `0x00000200`;
- `SEGA MEGA DRIVE`, region `JUE`;
- SGDK checksum проверялся независимо;
- известные неблокирующие предупреждения: classic additive checksum отличается от SGDK `sizebnd -checksum`; SGDK default header объявляет ROM end `0x000FFFFF` при физическом `0x0003FFFF`.
Эти же два предупреждения, без новых ошибок, повторно подтверждены для ROM Этапа 8.

### Этап 6 — реальный runtime/emulator smoke-test: ЗАВЕРШЁН / PASS WITH VISUAL WARNING
BlastEm 0.6.3.4 подтвердил TITLE -> MENU -> BATTLE, движение RIGHT/DOWN и BATTLE -> MENU без зависания. Финальный run: `34429982468`, job `102723241048`, artifact `10134120126`.
Именно здесь обнаружено просвечивание движущейся BG_B через прозрачный background системного SGDK-шрифта в battle HUD/log. Дефект вынесен на Этап 8.

### Этап 7 — углублённая проверка камеры: ЗАВЕРШЁН / PASS
Финальный run:
- workflow: `R3 Deep Camera NTSC PAL`;
- run id: `34431740584`, run #6;
- job id: `102728497596`;
- проверенный commit: `b64ce44691733967094286b5b7150503a4a18db7`;
- artifact id: `10134786196`;
- artifact ZIP digest: `sha256:dff77cc0b093850960717964672d147927311d889cf816307eb1fea0b7d0c3d0`.

Подтверждено реальным BlastEm в NTSC и PAL:
- LEFT / RIGHT / UP / DOWN;
- диагонали;
- ускорение/торможение;
- отсутствие залипания;
- все четыре границы без wrap;
- точные scroll bounds `X=0..800`, `Y=0..576`;
- `failures: []`.

### Этап 8 — графический/HUD-аудит: ЗАВЕРШЁН / PASS

#### Найденный подтверждённый дефект
До исправления системный шрифт SGDK использовал прозрачный color 0, поэтому при записи текста на BG_A фон его 8x8 ячеек становился прозрачным и через него был виден движущийся BG_B.
На старых реальных кадрах специализированный анализатор фиксировал, в частности:
- до `1868` меняющихся пикселей нижнего HUD;
- до `1415` меняющихся пикселей статической части правого HUD;
- десятки тысяч foreign/world pixels внутри текстовых ячеек.

#### Исправление
Battle HUD переведён с прозрачного системного вывода текста на отдельный непрозрачный набор из `96` ASCII-тайлов:
- форма символов взята точно из default font SGDK 2.11;
- пиксели символов остаются PAL0 index 15 (жёлтый);
- фон каждой текстовой ячейки — PAL0 index 7 (тёмный непрозрачный HUD);
- меню/заглавный экран и их шрифт не изменены;
- карта, география и camera logic не изменены;
- новый SHA-256 восстановленного R3 `main.c`: `0eb6593357d6b42c002ad9d0c457a156b3b5908048db118b1c227543fb641bcc`.

Изменения записаны в static CI payload и verifier. Добавлен `sgdk/tools/analyze_r3_hud_visual.py`, который проверяет реальные кадры, а не только исходный PNG.

#### Финальная реальная проверка Этапа 8
Workflow: `R3 Deep Camera NTSC PAL`
- run id: `34432690670`, run #7;
- job id: `102731314266`;
- tested head: `65893b6f9a760748147c8f59eba335593c69fc1a`;
- artifact id: `10135106474` (`Modern_Tanks_R3_Deep_Camera_Evidence`);
- artifact ZIP digest: `sha256:6109c5e8bcb1e573dd070af498be8bfe736aaa02cf6c50468379b873a8f1a8aa`;
- artifact содержит `180` файлов доказательств.

Новый ROM:
- size: `262144 bytes`;
- SHA-256: `94285501cd6cb72e909c31676a52c14da01f8e72b960e34636689768e13ed293`;
- header checksum = independently required SGDK checksum = `0x9001`;
- ROM audit: `PASS_WITH_WARNINGS`, только два уже известных SGDK metadata/checksum warning, ошибок нет.

HUD analyzer, реальные BlastEm frames:
- NTSC: `40` кадров;
- PAL: `40` кадров;
- `max_bottom_changed_pixels = 0` в обоих режимах;
- `max_right_static_changed_pixels = 0`;
- `coordinate_foreign_pixels_total = 0`;
- `static_text_foreign_pixels_total = 0`;
- `failure_count = 0`.

Регрессия камеры после изменения HUD также PASS:
- NTSC steady RIGHT `88.2353 px/s`, coast `13 px`;
- PAL steady RIGHT `92.0502 px/s`, coast `15 px`;
- PAL/NTSC ratio `1.04324`;
- bounds остались `X=0..800`, `Y=0..576`;
- camera failures `[]`.

Ручная перепроверка реальных активных кадров выполнена минимум в четырёх случаях: начальная и сильно смещённая позиция NTSC, начальная и нижняя граничная позиция PAL. Правый HUD и нижний лог визуально цельные; лес/вода/грунт через фон букв больше не просвечивают. Геометрия сохранена: battlefield `224x192`, right HUD `96x192`, bottom log `320x32`.

**Итог Этапа 8: подтверждённый HUD bleed устранён и доказан нулевыми изменениями/foreign pixels на 80 реальных кадрах NTSC+PAL. Технический PASS.**

## Следующий шаг при команде «Продолжай»

Начать только **Этап 9 — финальная регрессия и упаковка R3-кандидата для пользовательской приёмки**:
1. повторить reproducibility Build A/B уже для нового HUD-fixed ROM и потребовать byte-for-byte совпадение;
2. повторить итоговый ROM audit и зафиксировать окончательный SHA-256;
3. убедиться, что static-map verifier, runtime smoke, deep camera и HUD checks относятся к одной и той же финальной версии;
4. собрать единый полный архив исходников/статических ресурсов/checkpoint/отчётов плюс отдельно готовый `rom.bin`;
5. проверить ZIP integrity и hashes;
6. выдать пользователю финальный R3 candidate для проверки в его эмуляторе;
7. **не** менять `main` и не объявлять R3 принятым без отдельного пользовательского подтверждения.

## Правило работы по этапам и времени

На один запрос выполнять только один согласованный этап. На запрос использовать примерно до 20 минут активной работы. Если этап не завершён, перед ответом обновить этот checkpoint точной точкой продолжения.
