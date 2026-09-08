# R2 BUILD STATUS

Дата: **2026-09-08**

Статус: **TANK REFERENCE FIX — BUILD/CI PASS / TARGET ACCEPTANCE PENDING**

## Stage

R2 Main Menu Visual Target.

R0 и R1 остаются ACCEPTED / CLOSED. R3 не начинать до отдельного принятия R2 владельцем проекта.

## История R2

Первый R2 candidate был визуально отклонён как слишком упрощённый относительно `references/MAIN_MENU_REFERENCE.png`.

Visual Rework / Max Detail существенно повысил плотность меню, но владелец повторно указал на критический дефект: танки оставались условными пиктограммами и не соответствовали официальному `references/TANKS_DETAILED_REFERENCE.png`.

Поэтому предыдущий ROM также не считать финальным acceptance candidate.

## Текущий кандидат — Tank Reference Fix

Перед исправлением непосредственно перечитан `references/TANKS_DETAILED_REFERENCE.png`.

В R2 теперь перенесён его визуальный язык в реальном Mega Drive-разрешении:

- танки строго сверху;
- отдельные гусеницы с сегментацией;
- бронекорпус с формой/скосами;
- башня и погон;
- маска орудия и полноценный ствол;
- люк, болты, engine deck и боковые модули там, где позволяет размер;
- T-1 зелёный узкий разведчик;
- T-2 синий универсальный;
- T-3 самый широкий тяжёлый «крепость» с толстым орудием;
- T-4 красный угловатый штурмовик;
- фоновые battlefield tanks также переработаны;
- moving 16×16 menu tank также переработан.

Reference PNG не изменялся, не перекодировался и не встраивался как готовая текстура. Granada assets/code не использованы. Старая DEV-линия не используется.

## GitHub Actions — PASS

- repository: `xitriyjylik-eng/modern-tanks-r0`;
- build commit: `acba3abbf58fd3d1666617d51431c2b5f31eab43`;
- GitHub Actions run: `34185523022`;
- job: `build-r2` — SUCCESS;
- SGDK: 2.11;
- generated-art validation: PASS;
- source/locked-art contract: PASS;
- build A: PASS;
- build B: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM audit: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `5b73a0e9a1d7c8efb28541631cf09580790c0496d7b60634db41543b3ad586d9`;
- header checksum: `0x647E`;
- required checksum: `0x647E`;
- full-ROM XOR-fold: `0x0000`.

Подробный отчёт по коррекции: `tests/r2/R2_TANK_REFERENCE_FIX.md`.

## Gate

Нужен фактический запуск текущего ROM владельцем в MD Emu Games Gen и визуальное сравнение с обоими locked references:

- `references/MAIN_MENU_REFERENCE.png` — композиция меню;
- `references/TANKS_DETAILED_REFERENCE.png` — дизайн и читаемость танков.

Проверить также ИГРАТЬ/ГАРАЖ, возврат B и отсутствие corruption/ERR.

**R2 НЕ ACCEPTED. R3 BLOCKED.**
