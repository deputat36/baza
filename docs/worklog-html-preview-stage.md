# Этап HTML-превью

## Добавлено

- Генератор статического HTML-превью CSV-структуры.
- Makefile-команда `html-preview`.
- Шаг GitHub Actions для сборки HTML-превью.
- Учёт HTML-превью в preflight-сводке.
- Документация по HTML-превью.
- Обновление README, стартового документа и индекса проекта.

## Файлы

```text
scripts/tools/build_html_preview.py
docs/html-preview.md
Makefile
.github/workflows/validate-data.yml
scripts/tools/build_preflight_summary.py
README.md
docs/start-here.md
docs/project-index.md
```

## Практический смысл

Теперь структуру базы знаний можно быстро посмотреть в браузере без Excel и без готовой Google Таблицы.

## Команды

```bash
make html-preview
make preflight
```

## Результат

```text
build/html-preview/index.html
```

## GitHub Actions

После успешного workflow HTML-превью будет внутри артефакта:

```text
baza-build-artifacts/html-preview/index.html
```

## Следующий шаг

Собрать HTML-превью, открыть `index.html` и проверить глазами структуру разделов, таблиц и черновиков.
