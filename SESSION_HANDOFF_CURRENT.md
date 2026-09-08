# MODERN TANKS — CURRENT SESSION HANDOFF

Дата состояния: **2026-09-08**.

## 1. Жёсткие инварианты

1. Идею, механику и идентичность Modern Tanks не менять.
2. `design/GAME_DESIGN_FROZEN.md` — источник истины по игре.
3. Три PNG в `references/` не изменять, не перекодировать и не заменять.
4. Granada использовать только как технический образец Mega Drive; не копировать её графику, код, карты, музыку или игровые правила.
5. Старую DEV-линию, DEV ROM, Python opcode-emitter и старый DEV master-plan не возвращать.
6. Техническая линия только R0–R12 clean rebuild на SGDK 2.11.

## 2. Закрытые этапы

- **R0 Hardware Probe — ACCEPTED / CLOSED.** Target MD Emu Games Gen PASS.
- **R1 Core / State Machine — ACCEPTED / CLOSED.** FIX2: `ERR:00`, `SOAK: PASS 100/100`, target PASS. Accepted source commit `bc858a619de76a1f5c3112859914ea132e9bf7be`, run `34178302167`.

## 3. Текущий milestone — R2 MAIN MENU VISUAL TARGET

Статус: **TANK REFERENCE FIX — BUILD/CI PASS / TARGET ACCEPTANCE PENDING**.

R3 не начат и остаётся запрещён до прямого принятия R2 владельцем.

### История R2

- Первый R2 candidate был визуально отклонён как слишком упрощённый относительно `references/MAIN_MENU_REFERENCE.png`.
- Visual Rework / MAX DETAIL повысил общую плотность меню, но владелец указал на критический дефект: танки оставались условными пиктограммами и не соответствовали `references/TANKS_DETAILED_REFERENCE.png`.
- Эти варианты больше не считать финальными acceptance candidate.

Текущий candidate — **R2 TANK REFERENCE FIX**.

## 4. Целевая платформа

Modern Tanks остаётся настоящим Mega Drive/Genesis ROM.

- SG800 рассматривается как MD/Mega Drive emulator host для пользовательских ROM;
- HDMI/4K — вывод/upscaling, а не внутреннее разрешение игры;
- основной render target — H40 320×224 Mega Drive;
- тот же `.bin` должен работать на SG800 и в MD/Genesis эмуляторах ПК;
- обязательный control path — 3-button D-Pad + A/B/C/START.

## 5. Официальный tank art direction

Перед последним исправлением непосредственно перечитан locked `references/TANKS_DETAILED_REFERENCE.png`.

Обязательные признаки:

- вид сверху;
- отдельные гусеницы;
- сформированный бронекорпус;
- башня/погон;
- маска орудия + полноценный ствол;
- люки/болты/двигательный отсек/боковые модули в доступном разрешении;
- каждый класс отличается силуэтом и массой;
- T-1 зелёный узкий разведчик;
- T-2 синий универсальный;
- T-3 широкий тяжёлый «крепость»;
- T-4 красный угловатый штурмовик.

Эти признаки теперь перенесены в:

- четыре карточки T-1…T-4 нижнего HUD;
- battlefield tanks на фоне меню;
- moving 16×16 tank overlay.

Reference PNG не изменялся, не перекодировался и не встраивался как готовая текстура. Графика перерисована вручную в Mega Drive-oriented pixel-art коде.

## 6. Текущий R2 CI — PASS

- source/build commit: `acba3abbf58fd3d1666617d51431c2b5f31eab43`;
- GitHub Actions run: `34185523022`;
- job `build-r2`: SUCCESS;
- generated-art validation: PASS;
- source/locked-art contract: PASS;
- SGDK 2.11 build A: PASS;
- SGDK 2.11 build B: PASS;
- byte-for-byte reproducibility: PASS;
- independent ROM audit: PASS;
- ROM size: `131072` bytes;
- ROM SHA-256: `5b73a0e9a1d7c8efb28541631cf09580790c0496d7b60634db41543b3ad586d9`;
- header checksum: `0x647E`;
- required checksum: `0x647E`;
- full-ROM XOR-fold: `0x0000`.

Подробности: `tests/r2/R2_TANK_REFERENCE_FIX.md` и `tests/r2/R2_BUILD_STATUS.md`.

## 7. Следующий обязательный шаг

Только target-проверка текущего **R2 TANK REFERENCE FIX ROM**:

- сравнить меню с `references/MAIN_MENU_REFERENCE.png`;
- отдельно сравнить T-1…T-4 и фоновые танки с `references/TANKS_DETAILED_REFERENCE.png`;
- проверить selector Up/Down;
- ИГРАТЬ → TEST_BATTLE → B → MENU;
- ГАРАЖ → GARAGE → B → MENU;
- после переходов `ERR:00`;
- отсутствие VRAM/palette/sprite corruption.

Если внешний вид всё ещё не устраивает — продолжать R2, а не переходить к R3.

## 8. Строгий запрет

**R2 пока НЕ ACCEPTED. R3 НЕ НАЧИНАТЬ.**
