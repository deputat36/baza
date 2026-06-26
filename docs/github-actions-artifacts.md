# Артефакты GitHub Actions

## Что сохраняется

Workflow `.github/workflows/validate-data.yml` собирает и сохраняет артефакты из каталога `build/`.

Ожидаемые файлы:

- `preflight-summary.md` — сводка проверки и ручной чек-лист;
- `baza-knowledge-mvp.xlsx` — промежуточная Excel-книга;
- `google-sheet-tabs-plan.md` — план листов закрытой Google Таблицы;
- `google-sheet-tabs-plan.csv` — табличная версия плана листов;
- `google-sheet-validation-plan.md` — план выпадающих списков и справочников;
- `google-sheet-validation-plan.csv` — табличная версия плана выпадающих списков;
- `google-sheet-formatting-plan.md` — план оформления и условного форматирования;
- `google-sheet-formatting-plan.csv` — табличная версия плана оформления;
- `import-plan.md` — порядок импорта CSV в Google Таблицу;
- `import-plan.csv` — табличная версия плана импорта;
- `data-report.md` — техническая сводка по CSV-файлам;
- `source-coverage-report.md` — покрытие CSV-файлов XLSX-сборкой;
- `id-registry.md` — реестр ID по CSV-файлам;
- `schema-report.md` — отчёт по схемам CSV.

## Как использовать

1. Открыть последний запуск GitHub Actions.
2. Проверить, что workflow завершился без ошибки.
3. Скачать артефакт `baza-build-artifacts`.
4. Сначала открыть `preflight-summary.md`.
5. Открыть `google-sheet-tabs-plan.md` и сверить порядок листов.
6. Открыть `google-sheet-validation-plan.md` и сверить выпадающие списки.
7. Открыть `google-sheet-formatting-plan.md` и сверить цвета статусов и приоритетов.
8. Открыть XLSX и проверить структуру листов.
9. Открыть `import-plan.md` и сверить порядок переноса.
10. Открыть `data-report.md` и оценить наполненность разделов.
11. Открыть `source-coverage-report.md` и проверить CSV, которые не входят в XLSX.
12. Открыть `id-registry.md` и проверить возможные дубли ID.
13. Открыть `schema-report.md` и проверить заголовки CSV.

## Важно

Артефакты не должны содержать приватные рабочие данные.

Реальные контакты и внутренние материалы хранятся только в закрытой Google Таблице.
