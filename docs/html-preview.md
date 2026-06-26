# HTML-превью базы знаний

## Назначение

HTML-превью нужно, чтобы быстро посмотреть структуру CSV-файлов в браузере без Excel и без готовой Google Таблицы.

Генератор:

```text
scripts/tools/build_html_preview.py
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

Или напрямую:

```bash
python scripts/tools/build_html_preview.py
```

В составе полной проверки:

```bash
make preflight
```

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
