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
python scripts/tools/build_data_report.py
python scripts/tools/build_source_coverage_report.py
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
- Технический отчёт по данным.
- Отчёт покрытия CSV-источников XLSX-сборкой.
- Инвентаризация файлов.

## Что блокирует проверку

`validate_csv_structure.py` завершится с ошибкой, если найдёт структурные проблемы в CSV.

`validate_workbook_sources.py` завершится с ошибкой, если обязательный CSV-источник для XLSX отсутствует, пустой или не читается.

`privacy_scan.py` по умолчанию печатает предупреждения и не блокирует процесс. В строгом режиме `--strict` он завершится с ошибкой при найденных рисках.

`build_source_coverage_report.py` формирует диагностический отчёт и нужен для ручной проверки полноты XLSX-сборки.

## Что проверить вручную

- Нет ли реальных рабочих контактов.
- Нет ли данных клиентов.
- Нет ли закрытых условий.
- Все непроверенные записи имеют статус `CHECK` или `DRAFT`.
- CSV вне XLSX действительно не нужны в рабочей книге.
- Новые файлы описаны в рабочем журнале или документации.
