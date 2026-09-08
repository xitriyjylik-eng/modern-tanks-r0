# R2 TANK REFERENCE FIX

Дата: 2026-09-08

Статус: **BUILD/CI PASS / TARGET ACCEPTANCE PENDING**.

Причина коррекции: владелец проекта указал, что танки R2 не соответствовали официальному `references/TANKS_DETAILED_REFERENCE.png` и выглядели как условные пиктограммы.

## Источник истины

`references/TANKS_DETAILED_REFERENCE.png` перечитан непосредственно перед исправлением.

Обязательные признаки, перенесённые в R2:

- вид строго сверху;
- отдельные гусеницы;
- сформированный бронекорпус, а не прямоугольник;
- башня/погон;
- маска орудия и длинный ствол;
- люк/болты/двигательный отсек/боковые модули в пределах доступного разрешения;
- различимый силуэт каждого класса;
- T-1 — узкий зелёный разведчик;
- T-2 — более широкий синий универсальный танк;
- T-3 — самый широкий тяжёлый танк/«крепость» с толстым орудием;
- T-4 — красный угловатый штурмовик.

Исправлены не только четыре карточки T-1…T-4 в нижнем HUD, но и фоновые танки battlefield и 16×16 moving tank overlay.

Reference PNG не изменён, не перекодирован и не встроен как готовая текстура. Графика перерисована вручную в Mega Drive-oriented pixel-art коде.

## CI

- commit: `acba3abbf58fd3d1666617d51431c2b5f31eab43`;
- GitHub Actions run: `34185523022`;
- SGDK 2.11 build A: PASS;
- SGDK 2.11 build B: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM audit: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `5b73a0e9a1d7c8efb28541631cf09580790c0496d7b60634db41543b3ad586d9`;
- header checksum: `0x647E`;
- required checksum: `0x647E`;
- full-ROM XOR-fold: `0x0000`.

R2 остаётся незакрытым до фактической проверки владельцем в MD Emu Games Gen. R3 остаётся BLOCKED.
