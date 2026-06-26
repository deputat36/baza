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

## Предупреждающие проверки

`python scripts/tools/privacy_scan.py`

По умолчанию возвращает `0`, даже если нашёл потенциальные риски. Это нужно, чтобы GitHub Actions показывал отчёт, но не блокировал техническую сборку.

## Строгий режим

`python scripts/tools/privacy_scan.py --strict`

Возвращает `1`, если найдены потенциальные риски.

Использовать перед публичной публикацией или ручным аудитом.

## Неблокирующий CSV-отчёт

`python scripts/tools/validate_csv_structure.py --warn-only`

Печатает замечания по CSV, но возвращает `0`.
