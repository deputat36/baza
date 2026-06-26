# Preflight-проверка перед публикацией

## Назначение

Preflight — это быстрая проверка перед тем, как считать изменения готовыми.

## Команды

```bash
make install
make preflight
```

Если `make` недоступен, команды можно запустить отдельно:

```bash
pip install -r requirements.txt
python scripts/tools/validate_csv_structure.py
python scripts/tools/validate_workbook_sources.py
python scripts/tools/privacy_scan.py
python scripts/tools/build_workbook_from_csv.py
python scripts/tools/build_html_preview.py
python scripts/tools/validate_html_preview.py
python scripts/tools/build_data_report.py
python scripts/tools/build_source_coverage_report.py
python scripts/tools/build_id_registry_report.py
python scripts/tools/build_schema_report.py
python scripts/tools/build_import_plan.py
python scripts/tools/build_google_sheet_tabs_plan.py
python scripts/tools/build_google_sheet_validation_plan.py
python scripts/tools/build_google_sheet_formatting_plan.py
python scripts/tools/build_preflight_summary.py
python scripts/tools/list_project_files.py
```

## Строгая privacy-проверка

Перед публичной публикацией можно дополнительно запустить:

```bash
make privacy-strict
```

или:

```bash
python scripts/tools/privacy_scan.py --strict
```

## Что проверяется

- CSV-структура.
- Наличие обязательных источников XLSX.
- Потенциально рискованные данные.
- Сборка XLSX.
- Сборка HTML-превью.
- Smoke-проверка HTML-превью.
- Технический отчёт по данным.
- Отчёт покрытия CSV-источников XLSX-сборкой.
- Реестр ID и возможные дубли.
- Отчёт по схемам CSV.
- План импорта в Google Таблицу.
- План листов Google Таблицы.
- План выпадающих списков Google Таблицы.
- План оформления и условного форматирования Google Таблицы.
- Preflight-сводка.
- Инвентаризация файлов.

## Что блокирует проверку

`validate_csv_structure.py` завершится с ошибкой, если найдёт структурные проблемы в CSV.

`validate_workbook_sources.py` завершится с ошибкой, если обязательный CSV-источник для XLSX отсутствует, пустой или не читается.

`validate_html_preview.py` завершится с ошибкой, если HTML-превью не создано, слишком маленькое или не содержит ключевые блоки.

`privacy_scan.py` по умолчанию печатает предупреждения и не блокирует процесс. В строгом режиме `--strict` он завершится с ошибкой при найденных рисках.

`build_source_coverage_report.py`, `build_id_registry_report.py`, `build_schema_report.py`, `build_import_plan.py`, `build_google_sheet_tabs_plan.py`, `build_google_sheet_validation_plan.py`, `build_google_sheet_formatting_plan.py` и `build_preflight_summary.py` формируют диагностические отчёты для ручной проверки.

## Что проверить вручную

- Сначала открыть `build/preflight-summary.md`.
- Проверить `build/html-preview/index.html` в браузере.
- Проверить `build/google-sheet-tabs-plan.md` перед созданием листов.
- Проверить `build/google-sheet-validation-plan.md` перед настройкой выпадающих списков.
- Проверить `build/google-sheet-formatting-plan.md` перед настройкой цветов, фильтров и закрепления строк.
- Проверить `build/import-plan.md` перед переносом CSV.
- Нет ли реальных рабочих контактов.
- Нет ли данных клиентов.
- Нет ли закрытых условий.
- Все непроверенные записи имеют статус `CHECK` или `DRAFT`.
- CSV вне XLSX действительно не нужны в рабочей книге.
- Возможные дубли ID не являются ошибочными повторами.
- Заголовки однотипных CSV согласованы.
- Новые файлы описаны в рабочем журнале или документации.
