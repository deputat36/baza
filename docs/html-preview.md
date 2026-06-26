# HTML-превью базы знаний

## Назначение

HTML-превью нужно, чтобы быстро посмотреть структуру CSV-файлов в браузере без Excel и без готовой Google Таблицы.

Генератор:

```text
scripts/tools/build_html_preview.py
```

Smoke-проверка:

```text
scripts/tools/validate_html_preview.py
```

Результат:

```text
build/html-preview/index.html
```

## Запуск

Через Makefile:

```bash
make html-preview
```

Проверить, что HTML-превью создано корректно:

```bash
make html-check
```

Или напрямую:

```bash
python scripts/tools/build_html_preview.py
python scripts/tools/validate_html_preview.py
```

В составе полной проверки:

```bash
make preflight
```

## Что есть в HTML-превью

- Сводные счётчики по CSV-файлам, строкам и колонкам.
- Поиск по названию раздела, пути файла и первым строкам CSV.
- Быстрые ссылки на каждый CSV-раздел.
- Карточки CSV-файлов с первыми строками таблиц.
- Горизонтальная прокрутка широких таблиц.

## Что проверяет smoke-проверка

- Файл `build/html-preview/index.html` существует.
- Файл не выглядит пустым.
- В HTML есть ключевой заголовок.
- В HTML есть блоки таблиц.
- В HTML есть маркер XLSX-источников.
- В HTML есть поиск и блок быстрых ссылок.

## Что попадает в превью

- CSV-файлы, входящие в XLSX-сборку.
- Дополнительные CSV из `data/drafts/`.
- Справочники из `data/dictionaries/`.
- Шаблоны из `templates/`.

Для каждого файла показывается:

- название;
- путь;
- количество строк и колонок;
- первые строки таблицы.

## Ограничение

Превью показывает только публичную безопасную часть проекта.

Реальные рабочие контакты, ФИО, внутренние условия и клиентские данные должны храниться только в закрытой Google Таблице.

## Где смотреть в GitHub Actions

После успешного workflow файл будет внутри артефакта:

```text
baza-build-artifacts/html-preview/index.html
```

Путь в интерфейсе GitHub:

```text
Actions -> Validate data files -> Artifacts -> baza-build-artifacts
```

## Где смотреть через GitHub Pages

Для публикации HTML-превью добавлен workflow:

```text
.github/workflows/pages-preview.yml
```

Инструкция:

```text
docs/github-pages-preview.md
```

Если GitHub Pages включён с источником `GitHub Actions`, страницу можно опубликовать через:

```text
Actions -> Publish HTML preview -> Run workflow
```
