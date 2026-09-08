# R2 FINAL ACCEPTANCE

Дата: 2026-09-09

Статус: **ACCEPTED / CLOSED**.

Владелец проекта фактически проверил финальный ROM на целевом эмуляторе и подтвердил результат сообщением: «Супер, засчитываю.»

## Принятый baseline

- commit: `a1faa7d567ceb7f5506005b354da28f5c1ea0cee`;
- CI run: `34255626880` — SUCCESS;
- ROM SHA-256: `fb6896471a1bf559e13c55118c3d2beedf8c1567ff6703a114ef05857b744017`;
- ROM size: 131072 bytes;
- ROM audit: PASS;
- SGDK: 2.11;
- reproducibility: две независимые сборки совпали byte-for-byte.

## Что именно принято визуально

- главное меню и русская типографика;
- центральная панель и селектор;
- общая детализация battlefield background;
- цветовая гамма ландшафта;
- отсутствие правой мини-карты;
- река с движением по руслу;
- плавный правый флаг;
- два независимых огня;
- лёгкое движение деревьев;
- отсутствие левого флага;
- анимации не выбиваются из общей палитры и яркости сцены.

## Что именно принято технически

- 12 river frames;
- 12 right-flag frames;
- 8 upper-fire frames;
- 8 lower-fire frames;
- 12 tree frames;
- mask guards для river/bridge/shore;
- статичные дубли огня/полотна удаляются из фонового слоя;
- independent animation timers;
- сохранён R1 state/resource lifecycle;
- VRAM budget guard;
- direct SGDK resource pipeline;
- CI reproducibility and ROM audit.

## Правило после приёмки

R2 считается закрытым. Любое изменение принятого меню, фона, палитры или ambient-анимаций требует отдельного явного запроса владельца. Обычная дальнейшая разработка должна идти в R3 и последующие этапы.
