# Прохорова Select — сайт

Прототип сайта личного брокера Елены Прохоровой (бизнес- и премиум-сегмент Москвы).
Публикуется на GitHub Pages из корня: `index.html`.

## Сборка

```
python3 build_ps.py        # → index.html (сайт) и prokhorova-select.html (версия для артефакта claude.ai)
python3 logo_type.py cormorant-light   # логотип набором в шрифте (fontTools) → logo-svg/type-cormorant-light/ — основной способ
python3 logo_vector.py ps-slash   # запасной: трассировка растрового макета (нужен potrace)
```

Логотип на сайте — `logo-svg/type-cormorant-light/`: буквы взяты из шрифтов (Cormorant Garamond Light для P/S, «ПРОХОРОВА», SELECT;
Manrope для подписи), расставлены по пропорциям макета `logo2.png`. Кривые шрифтовые, без потерь.
Варианты: `type-cormorant` (400), `type-cormorant-medium` (500), `type-prata`, `type-oranienbaum`. Шрифты лежат в `fonts/`.

Исходники страницы: `site_src.html` (разметка и стили), `karta_section.html` (раздел карты),
`karta_script.js` (объекты, таблица, карта). Картинки вшиваются в HTML как data-URI.

- `nota/` — геометрия карты Москвы и 42 дома с фото из базы NOTA (`pick.csv`)
- `gen/` — демо-визуализации интерьеров (Higgsfield)
- `logo-svg/ps-slash/` — трассировка макета P/S, `ps-mono/` — первый вариант с монограммой (тоже трассировка)

Квартиры, цены и кейсы — демонстрационные. Заглушки помечены на страницах бронзовым текстом:
телефон, ИНН, Telegram, почта.
