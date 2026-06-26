# Генератор XLSX

## Назначение

Скрипт собирает промежуточную Excel-книгу из CSV-файлов репозитория.

Файл нужен для быстрой проверки структуры перед переносом в закрытую Google Таблицу.

## Скрипты

- `scripts/tools/workbook_config.py` — список листов, источников и путь результата.
- `scripts/tools/validate_workbook_sources.py` — проверка обязательных CSV-источников.
- `scripts/tools/build_workbook_from_csv.py` — сборка XLSX.

## Проверка источников

Перед сборкой нужно проверить, что все обязательные CSV-источники существуют и читаются:

```bash
python scripts/tools/validate_workbook_sources.py
```

Через Makefile:

```bash
make sources
```

## Запуск

```bash
pip install -r requirements.txt
make xlsx
```

Если Makefile недоступен:

```bash
python scripts/tools/validate_workbook_sources.py
python scripts/tools/build_workbook_from_csv.py
```

## Результат

`build/baza-knowledge-mvp.xlsx`

## Изменение состава листов

Состав листов и CSV-источников меняется в `scripts/tools/workbook_config.py`.

После изменения нужно запустить:

```bash
make sources
make xlsx
```

## Ограничение

XLSX-сборка не должна содержать реальные внутренние контакты, данные клиентов и закрытые условия.

Реальные рабочие данные заполняются только в закрытой Google Таблице.
