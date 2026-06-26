# Отчёт по данным

## Назначение

Скрипт `scripts/tools/build_data_report.py` собирает краткую техническую сводку по CSV-файлам проекта.

Он показывает:

- количество CSV-файлов;
- количество строк данных;
- количество колонок в каждом файле;
- распределение статусов, если в файле есть колонка `Статус` или `status`.

## Запуск

```bash
python scripts/tools/build_data_report.py
```

Через Makefile:

```bash
make report
```

Результат сохраняется здесь:

```text
build/data-report.md
```

## Связанные отчёты

Сводка по всем артефактам и ручному чек-листу:

```bash
make summary
```

Результат:

```text
build/preflight-summary.md
```

План листов закрытой Google Таблицы:

```bash
make tabs-plan
```

Результат:

```text
build/google-sheet-tabs-plan.md
build/google-sheet-tabs-plan.csv
```

План выпадающих списков закрытой Google Таблицы:

```bash
make validation-plan
```

Результат:

```text
build/google-sheet-validation-plan.md
build/google-sheet-validation-plan.csv
```

План переноса CSV в закрытую Google Таблицу:

```bash
make import-plan
```

Результат:

```text
build/import-plan.md
build/import-plan.csv
```

Для проверки того, какие CSV входят в XLSX:

```bash
make coverage
```

Результат:

```text
build/source-coverage-report.md
```

Для проверки ID и возможных дублей:

```bash
make ids
```

Результат:

```text
build/id-registry.md
```

Для проверки заголовков и схем CSV:

```bash
make schemas
```

Результат:

```text
build/schema-report.md
```

## Использование

Отчёты нужны перед переносом данных в закрытую Google Таблицу и после крупных изменений в CSV.

Они помогают быстро увидеть наполненность разделов, порядок листов, выпадающие списки, порядок импорта, полноту XLSX-сборки, возможные проблемы с ID и согласованность заголовков.

## Ограничение

Отчёты технические. Они не подтверждают актуальность контактов, юридическую точность и полноту данных.
