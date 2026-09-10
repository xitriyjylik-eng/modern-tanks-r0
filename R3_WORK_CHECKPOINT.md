# Modern Tanks R3 — рабочая точка продолжения

Дата фиксации: 2026-09-10
Рабочая ветка: `r3-map-camera`
Ветка `main`: **НЕ ИЗМЕНЕНА**, остаётся на принятом R2 до отдельной пользовательской приёмки R3.

## Итог по этапам 1–10

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

### Этап 9 — финальная reproducibility + regression + упаковка: PASS

Финальный GitHub Actions build:
- workflow: `R3 Static Region Smooth Camera SGDK CI`;
- run id: `34434756996`, run #171;
- job id: `102737407791`;
- artifact id: `10135767228`;
- artifact digest: `sha256:bc6d10abb6ea64fbce7502c1261a3e80ed958ff88b0914a8837fc554b2a81ee7`.

Финальный ROM:
- size: `262144 bytes`;
- SHA-256: `94285501cd6cb72e909c31676a52c14da01f8e72b960e34636689768e13ed293`;
- Build A/B byte-for-byte PASS;
- SGDK checksum/audit PASS WITH DOCUMENTED WARNINGS;
- этот же SHA прошёл Stage 8 BlastEm NTSC/PAL camera + HUD tests.

Static map:
- playable: `1024x768`;
- runtime map: `1024x1024` с safety padding;
- battle HUD: `320x224` overlay geometry;
- exact accepted R2 landscape tile occurrences: `12074 / 12288` = `98.258%`;
- runtime procedural generation: `false`.

Stage 9 полный архив:
- `Modern_Tanks_FULL_PROJECT_R3_STAGE9_FINAL_CANDIDATE_2026-09-10.zip`;
- SHA-256: `bd5537bf451e5339a29faf78a5549d597d071cd7e0e9f4508295878b6c4cf23b`;
- ZIP integrity PASS.

### Этап 10 — длительная реальная emulator soak-проверка: ЗАВЕРШЁН / PASS

Инструменты Stage 10:
- `sgdk/tools/run_r3_stage10_soak.sh`;
- `sgdk/tools/analyze_r3_stage10_soak.py`;
- `.github/workflows/r3-stage10-soak.yml`.

Финальный GitHub Actions soak:
- workflow: `R3 Stage 10 Long Emulator Soak`;
- run id: `34435644570`, run #1;
- job id: `102740016693`;
- tested head: `373b40117160db8777ee373c5e56ae2d01b28af1`;
- artifact id: `10136353463`;
- artifact ZIP digest: `sha256:c55126214d69424bb463e9c4c4db44bd51aac96b14c92352f2011af994ad7fb6`;
- artifact files: `191`;
- workflow conclusion: `success`.

Перед soak жёстко проверено, что запущен именно финальный ROM:
- SHA-256 required/actual: `94285501cd6cb72e909c31676a52c14da01f8e72b960e34636689768e13ed293`;
- size: `262144 bytes`;
- ROM audit errors: `[]`.

Реальный BlastEm 0.6.3.4 soak:
- NTSC/U: `633` секунд непрерывного runtime, `48` полных циклов `MENU -> BATTLE -> movement -> MENU`;
- PAL/E: `132` секунды дополнительной регрессии, `10` полных циклов;
- суммарное emulator runtime: `765` секунд = **12 минут 45 секунд**;
- суммарно: **58 полных циклов загрузки/выгрузки battle MAP**;
- сохранено и автоматически проверено `180` battle/moved/menu/initial screenshots;
- все циклы прошли с живым процессом BlastEm, без crash/hang.

Screenshot/runtime analyzer:
- NTSC `battle_reset_diff_max = 0.0`;
- PAL `battle_reset_diff_max = 0.0`;
- NTSC `moved_field_diff_min = 0.901088...`;
- PAL `moved_field_diff_min = 0.901088...`;
- NTSC `menu_return_diff_max = 0.0160017` (допуск учитывает принятую ambient-анимацию меню);
- PAL `menu_return_diff_max = 0.0198242`;
- black/corrupt frame failures: `0`;
- combined failures: `[]`;
- combined status: `PASS`.

Ручная перепроверка последних реальных кадров также выполнена: NTSC cycle 48 battle/moved/menu и PAL cycle 10 moved визуально корректны; карта продолжает двигаться, HUD остаётся цельным, возврат в главное меню нормальный.

Диагностика host RSS BlastEm:
- NTSC: `134296 -> 143180 KiB`, рост `8884 KiB`;
- PAL: `136144 -> 148504 KiB`, рост `12360 KiB`.
Это **не** прямое измерение 64 KiB Mega Drive RAM и поэтому не используется как доказательство/опровержение утечки игрового heap. Практический leak-stress обеспечен 58 повторными MAP create/release + resource reload циклами: истощения игрового heap, отказа входа в battle или повреждения кадров не произошло.

Локально скачанный Stage 10 artifact дополнительно проверен `unzip -t`: PASS, `191` файлов. Встроенный `rom.bin` побайтово имеет тот же SHA-256, что Stage 9 candidate.

**Итог Этапа 10: технические этапы R3 1–10 завершены. Длительный реальный emulator soak PASS. Кандидат технически готов к пользовательской проверке. R3 всё ещё НЕ ACCEPTED/CLOSED, пока пользователь сам не подтвердит внешний вид/ощущение камеры и загрузку.**

## Следующий шаг

Только пользовательская приёмка на его эмуляторе:
1. запустить финальный ROM SHA-256 `94285501...ed293`;
2. визуально оценить карту относительно главного меню;
3. оценить время входа в battle;
4. оценить плавность камеры руками;
5. если есть дефект — исправлять отдельным новым кандидатом;
6. если пользователь явно подтверждает приёмку — только тогда можно пометить R3 `ACCEPTED/CLOSED` и отдельно решать вопрос переноса в `main`.

## Правило

Не менять `main` и не объявлять R3 принятым без явного пользовательского подтверждения.
