# Генератор XLSX

## Назначение

Скрипт собирает промежуточную Excel-книгу из CSV-файлов репозитория.

Файл нужен для быстрой проверки структуры перед переносом в закрытую Google Таблицу.

## Скрипт

`scripts/tools/build_workbook_from_csv.py`

## Запуск

```bash
pip install openpyxl
python scripts/tools/build_workbook_from_csv.py
```

## Результат

`build/baza-knowledge-mvp.xlsx`

## Ограничение

XLSX-сборка не должна содержать реальные внутренние контакты, данные клиентов и закрытые условия.

Реальные рабочие данные заполняются только в закрытой Google Таблице.
