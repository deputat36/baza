# Генерируемый план оформления Google Таблицы

## Назначение

Скрипт `scripts/tools/build_google_sheet_formatting_plan.py` формирует план оформления и условного форматирования закрытой Google Таблицы.

Он создаёт два файла:

```text
build/google-sheet-formatting-plan.md
build/google-sheet-formatting-plan.csv
```

## Что входит в план

- цвета для статусов;
- цвета для приоритетов;
- базовые правила оформления листов;
- рекомендации по закреплению строки заголовков, фильтрам и переносу текста.

## Запуск

```bash
python scripts/tools/build_google_sheet_formatting_plan.py
```

Через Makefile:

```bash
make formatting-plan
```

## Как использовать

1. Запустить `make preflight`.
2. Открыть `build/google-sheet-formatting-plan.md`.
3. Настроить условное форматирование в закрытой Google Таблице.
4. Проверить визуально статусы и приоритеты после импорта.

## Важно

План не применяет форматирование автоматически. Он нужен как инструкция для ручной настройки таблицы.
