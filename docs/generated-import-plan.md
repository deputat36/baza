# Генерируемый план импорта

## Назначение

Скрипт `scripts/tools/build_import_plan.py` строит план переноса CSV в закрытую Google Таблицу на основе `scripts/tools/workbook_config.py`.

Он формирует два файла:

```text
build/import-plan.csv
build/import-plan.md
```

## Что входит в план

- порядок импорта;
- название листа;
- путь к CSV;
- количество строк данных;
- количество колонок;
- заголовки CSV;
- статус наличия источника.

## Запуск

```bash
python scripts/tools/build_import_plan.py
```

Через Makefile:

```bash
make import-plan
```

## Как использовать

1. Запустить `make preflight`.
2. Открыть `build/preflight-summary.md`.
3. Открыть `build/import-plan.md`.
4. Переносить CSV в закрытую Google Таблицу в указанном порядке.
5. После импорта проверить фильтры, статусы и выпадающие списки.

## Важно

План строится по XLSX-конфигу. Если CSV нужно добавить в рабочую книгу и импорт, его нужно добавить в `scripts/tools/workbook_config.py`.
