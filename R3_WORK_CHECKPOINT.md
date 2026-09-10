# Modern Tanks R3 — рабочая точка продолжения

Дата фиксации: 2026-09-10
Рабочая ветка: `r3-map-camera`
Ветка `main`: **НЕ ИЗМЕНЕНА**, остаётся на принятом R2 до отдельной пользовательской приёмки R3.

## Итог по этапам 1–9

### Этапы 1–3 — ресурсы, SGDK, компиляция: PASS
- статическая Region 1 и transport chunks проверены;
- SGDK image: `registry.gitlab.com/doragasu/docker-sgdk:v2.11`;
- image digest: `sha256:327ab838fbdf6bc741c6a7a11ee3c937cf1aaf1dc07a475995e89b741b6a830d`;
- ResComp 3.95;
- `m68k-elf-gcc -m68000`;
- `main.c`, resources, linker, objcopy и sizebnd проходят успешно.

### Этап 4 — первоначальная reproducibility: PASS
Первоначальный R3 ROM до HUD-fix собирался byte-for-byte одинаково. После HUD-fix окончательная reproducibility повторена на Этапе 9.

### Этап 5 — ROM audit: PASS WITH DOCUMENTED SGDK WARNINGS
- reset PC и stack ABI корректны;
- SEGA header присутствует;
- SGDK checksum проверяется независимо;
- остаются только два стандартных предупреждения SGDK 2.11: его XOR-fold checksum не равен classic additive checksum; default header ROM end = 1 MiB при физическом ROM 256 KiB.

### Этап 6 — runtime smoke: PASS
BlastEm подтвердил TITLE -> MENU -> BATTLE, движение карты и возврат BATTLE -> MENU. На этом этапе был найден HUD bleed через прозрачный системный font background.

### Этап 7 — глубокая камера NTSC/PAL: PASS
- LEFT/RIGHT/UP/DOWN;
- диагонали;
- acceleration/friction;
- отсутствие залипания;
- отсутствие wrap;
- scroll bounds: `X=0..800`, `Y=0..576`;
- camera failures: `[]`.

### Этап 8 — HUD/графический regression fix: PASS
HUD bleed устранён непрозрачными glyph cells с формой default font SGDK 2.11.
Проверенный игровой source/payload commit: `65893b6f9a760748147c8f59eba335593c69fc1a`.

Финальный Stage 8 emulator run:
- run: `34432690670`, run #7;
- job: `102731314266`;
- artifact: `10135106474`;
- 40 кадров NTSC + 40 кадров PAL;
- `max_bottom_changed_pixels = 0`;
- `max_right_static_changed_pixels = 0`;
- `coordinate_foreign_pixels_total = 0`;
- `static_text_foreign_pixels_total = 0`;
- HUD failures: `[]`.

Камера после HUD-fix повторно PASS:
- NTSC steady RIGHT ≈ `88.2353 px/s`, coast `13 px`;
- PAL steady RIGHT ≈ `92.0502 px/s`, coast `15 px`;
- PAL/NTSC ratio ≈ `1.04324`;
- bounds `X=0..800`, `Y=0..576`.

### Этап 9 — финальная reproducibility + regression + упаковка: ЗАВЕРШЁН / PASS

Служебный CI-trigger commit: `eeabef1e1074a12b5d7f0f59f61a9a37218b7fea`. Файл-trigger не входит в SGDK source/resources и не влияет на ROM.

Финальный GitHub Actions build:
- workflow: `R3 Static Region Smooth Camera SGDK CI`;
- run id: `34434756996`, run #171;
- job id: `102737407791`;
- artifact id: `10135767228`;
- artifact digest: `sha256:bc6d10abb6ea64fbce7502c1261a3e80ed958ff88b0914a8837fc554b2a81ee7`.

Финальная reproducibility:
- Build A: PASS;
- Build B: PASS;
- `cmp /tmp/sgdk-r3-a/out/rom.bin /tmp/sgdk-r3-b/out/rom.bin`: PASS;
- оба ROM byte-for-byte идентичны.

Финальный ROM:
- size: `262144 bytes`;
- SHA-256: `94285501cd6cb72e909c31676a52c14da01f8e72b960e34636689768e13ed293`;
- initial SSP: `0xE1000000`;
- reset PC: `0x00000200`;
- console: `SEGA MEGA DRIVE`;
- region: `JUE`;
- SGDK header checksum: `0x9001`;
- independently required SGDK checksum: `0x9001`;
- full-ROM SGDK XOR-fold: `0x0000`;
- errors: `[]`;
- audit: `PASS_WITH_WARNINGS` только из-за двух уже документированных SGDK default metadata/checksum warnings.

Ключевая regression-гарантия: **Stage 9 финальный A/B ROM имеет тот же SHA-256 `94285501...ed293`, что и ROM, реально прошедший Stage 8 BlastEm NTSC/PAL camera + HUD test.** Локально выполнен также прямой `cmp`: Stage 9 `rom.bin` == Stage 8 emulator-tested candidate byte-for-byte.

Static map повторно PASS:
- playable: `1024x768`;
- runtime map: `1024x1024` с safety padding;
- battle HUD: `320x224` overlay geometry;
- exact accepted R2 landscape tile occurrences: `12074 / 12288` = `98.258%`;
- runtime procedural generation: `false`.

Полный локальный R3 Stage 9 archive собран и проверен:
- имя: `Modern_Tanks_FULL_PROJECT_R3_STAGE9_FINAL_CANDIDATE_2026-09-10.zip`;
- ZIP SHA-256: `bd5537bf451e5339a29faf78a5549d597d071cd7e0e9f4508295878b6c4cf23b`;
- size: `5936285 bytes`;
- members: `285`;
- `unzip -t`: PASS;
- встроенный `verify_r3_static_map.py`: PASS;
- встроенный `verify_rom.py` на финальном ROM: PASS_WITH_WARNINGS, errors `[]`.

**Итог Этапа 9: финальный R3-кандидат технически готов к пользовательской приёмке. R3 пока НЕ ACCEPTED/CLOSED.**

## Этап 10 — финальная soak-приёмка: В ПРОЦЕССЕ

Созданы отдельные инструменты долгого реального эмуляторного теста:
- `sgdk/tools/run_r3_stage10_soak.sh`, commit `36f2daf0d7c5403a6bd4a50b98b6be4ee88af0e8`;
- `sgdk/tools/analyze_r3_stage10_soak.py`, commit `90f6cc0fd5dc44c3e7c71f234c4afb9239678bac`;
- workflow `.github/workflows/r3-stage10-soak.yml`, commit `373b40117160db8777ee373c5e56ae2d01b28af1`.

Текущий GitHub Actions run:
- workflow: `R3 Stage 10 Long Emulator Soak`;
- run id: `34435644570`, run #1;
- job id: `102740016693`;
- tested head: `373b40117160db8777ee373c5e56ae2d01b28af1`;
- перед soak уже PASS: static overlay restore, static-map verify, SGDK build и жёсткая проверка SHA финального ROM `94285501cd6cb72e909c31676a52c14da01f8e72b960e34636689768e13ed293`;
- на момент checkpoint выполняется шаг `Run 10+ minute real-emulator soak`.

Сценарий:
- NTSC: минимум `630` секунд непрерывного BlastEm runtime и минимум `40` циклов MENU -> BATTLE -> движение -> MENU;
- PAL: дополнительная повторная регрессия минимум `120` секунд и минимум `8` циклов;
- каждый цикл проверяет, что BlastEm жив, делает battle/moved/menu screenshots и логирует elapsed/RSS;
- analyzer требует корректный возврат в меню, стабильный reset battle state, видимое движение карты и отсутствие чёрных/повреждённых кадров;
- host BlastEm RSS записывается только как диагностический показатель и не выдаётся за прямое измерение Mega Drive heap.

## Следующая точка

Дождаться завершения run `34435644570`. Если soak/analyzer PASS — скачать artifact, зафиксировать точные длительности/число циклов/метрики и закрыть технический Этап 10. Если FAIL — разобрать только первый реальный дефект либо дефект harness, исправить и повторить Stage 10.

## Правило

Не менять `main` и не объявлять R3 принятым без явного пользовательского подтверждения.
