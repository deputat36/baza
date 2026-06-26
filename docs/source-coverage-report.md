# Отчёт покрытия CSV-источников

## Назначение

Скрипт `scripts/tools/build_source_coverage_report.py` показывает, какие CSV-файлы входят в XLSX-сборку, а какие остаются вне неё.

Это помогает понять, не забыли ли добавить важный CSV в `scripts/tools/workbook_config.py`.

## Запуск

```bash
python scripts/tools/build_source_coverage_report.py
```

Через Makefile:

```bash
make coverage
```

## Результат

```text
build/source-coverage-report.md
```

## Что показывает отчёт

- CSV-файлы в рабочих папках.
- CSV-источники в XLSX-конфиге.
- CSV, которые включены в XLSX и существуют.
- CSV, которые указаны в XLSX, но отсутствуют.
- CSV, которые есть в репозитории, но не входят в XLSX.
- Дубли в XLSX-конфиге.

## Важно

CSV вне XLSX не всегда являются ошибкой. Это могут быть служебные шаблоны, чек-листы, журналы тестирования или файлы для будущих этапов.
