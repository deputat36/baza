# Этап отчёта по незаполненным данным

## Добавлено

- Генератор отчёта по незаполненным значениям в CSV.
- Markdown- и CSV-версии отчёта.
- Makefile-команда `missing`.
- Сборка отчёта в GitHub Actions.
- Учёт отчёта в preflight-сводке.
- Документация по отчёту.
- Обновление preflight-инструкции.

## Файлы

```text
scripts/tools/build_missing_values_report.py
docs/missing-values-report.md
Makefile
.github/workflows/validate-data.yml
scripts/tools/build_preflight_summary.py
docs/preflight-check.md
```

## Результаты сборки

```text
build/missing-values-report.md
build/missing-values-report.csv
```

## Практический смысл

Перед переносом в закрытую Google Таблицу можно быстро увидеть, где пустые ID, статусы, приоритеты и слишком много пустых ячеек.

## Команды

```bash
make missing
make preflight
```
