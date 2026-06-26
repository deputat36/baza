# Этап поиска и навигации в HTML-превью

## Добавлено

- Поиск по HTML-превью.
- Быстрые ссылки на CSV-разделы.
- Сводные счётчики по CSV-файлам, строкам и колонкам.
- Счётчик видимых карточек после фильтрации.
- Кнопка сброса поиска.
- Обновление smoke-проверки HTML-превью.
- Обновление документации по HTML-превью.

## Файлы

```text
scripts/tools/build_html_preview.py
scripts/tools/validate_html_preview.py
docs/html-preview.md
```

## Практический смысл

HTML-превью стало пригоднее для реального просмотра: можно быстро найти нужный CSV-раздел, перейти к нему по ссылке и отфильтровать длинный список карточек.

## Проверка

```bash
make html-check
```

или:

```bash
python scripts/tools/build_html_preview.py
python scripts/tools/validate_html_preview.py
```

## Следующий шаг

Перезапустить workflow `Publish HTML preview` и проверить страницу GitHub Pages после публикации.
