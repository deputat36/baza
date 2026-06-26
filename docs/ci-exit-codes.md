# Коды завершения проверок

## Назначение

Этот файл фиксирует, какие проверки должны блокировать workflow, а какие должны работать как отчёт.

## Блокирующие проверки

`python scripts/tools/validate_csv_structure.py`

Возвращает `1`, если найдены структурные проблемы CSV.

`python scripts/tools/validate_workbook_sources.py`

Возвращает `1`, если обязательный источник XLSX отсутствует, пустой или не читается.

`python scripts/tools/build_workbook_from_csv.py`

Должен завершаться успешно, если из текущих CSV можно собрать XLSX.

`python scripts/tools/build_data_report.py`

Должен завершаться успешно, если можно собрать технический отчёт по CSV.

`python scripts/tools/build_source_coverage_report.py`

Должен завершаться успешно, если можно собрать отчёт покрытия CSV-источников.

`python scripts/tools/build_id_registry_report.py`

Должен завершаться успешно, если можно собрать реестр ID.

`python scripts/tools/build_schema_report.py`

Должен завершаться успешно, если можно собрать отчёт по схемам CSV.

`python scripts/tools/build_import_plan.py`

Должен завершаться успешно, если можно собрать план импорта.

`python scripts/tools/build_google_sheet_tabs_plan.py`

Должен завершаться успешно, если можно собрать план листов Google Таблицы.

`python scripts/tools/build_preflight_summary.py`

Должен завершаться успешно, если можно собрать сводку preflight-артефактов.

## Предупреждающие проверки

`python scripts/tools/privacy_scan.py`

По умолчанию возвращает `0`, даже если нашёл потенциальные риски. Это нужно, чтобы GitHub Actions показывал отчёт, но не блокировал техническую сборку.

## Диагностические отчёты

`build/preflight-summary.md`

Показывает список артефактов и ручной чек-лист.

`build/google-sheet-tabs-plan.md` и `build/google-sheet-tabs-plan.csv`

Показывают порядок листов и базовые настройки закрытой Google Таблицы.

`build/import-plan.md` и `build/import-plan.csv`

Показывают порядок переноса CSV в закрытую Google Таблицу.

`build/source-coverage-report.md`

Показывает CSV вне XLSX и дубли в конфиге источников.

`build/id-registry.md`

Показывает префиксы ID, возможные дубли и строки без распознанного ID.

`build/schema-report.md`

Показывает заголовки CSV, группы одинаковых схем и замечания по пустым или повторяющимся колонкам.

## Строгий режим

`python scripts/tools/privacy_scan.py --strict`

Возвращает `1`, если найдены потенциальные риски.

Использовать перед публичной публикацией или ручным аудитом.

## Неблокирующий CSV-отчёт

`python scripts/tools/validate_csv_structure.py --warn-only`

Печатает замечания по CSV, но возвращает `0`.
