# Генерируемый план листов Google Таблицы

## Назначение

Скрипт `scripts/tools/build_google_sheet_tabs_plan.py` создаёт план настройки листов закрытой Google Таблицы на основе `scripts/tools/workbook_config.py`.

Он формирует два файла:

```text
build/google-sheet-tabs-plan.md
build/google-sheet-tabs-plan.csv
```

## Что входит в план

- порядок листов;
- количество CSV-источников;
- количество строк данных;
- максимальное количество колонок;
- количество отсутствующих источников;
- базовые настройки: фильтр и закрепление строки;
- рекомендация по видимости листа.

## Запуск

```bash
python scripts/tools/build_google_sheet_tabs_plan.py
```

Через Makefile:

```bash
make tabs-plan
```

## Как использовать

1. Запустить `make preflight`.
2. Открыть `build/preflight-summary.md`.
3. Открыть `build/google-sheet-tabs-plan.md`.
4. Создать листы в закрытой Google Таблице в указанном порядке.
5. Настроить фильтры и закрепление строк.
6. Затем переносить CSV по `build/import-plan.md`.

## Важно

План строится по XLSX-конфигу. Если меняется `scripts/tools/workbook_config.py`, план листов обновится при следующей сборке.
