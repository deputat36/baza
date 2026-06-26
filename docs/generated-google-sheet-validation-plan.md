# Генерируемый план выпадающих списков

## Назначение

Скрипт `scripts/tools/build_google_sheet_validation_plan.py` формирует план проверки данных для закрытой Google Таблицы.

Он создаёт два файла:

```text
build/google-sheet-validation-plan.md
build/google-sheet-validation-plan.csv
```

## Что входит в план

- справочник;
- CSV-источник;
- значение для выпадающего списка;
- подпись значения;
- рекомендуемые колонки применения;
- назначение справочника.

## Запуск

```bash
python scripts/tools/build_google_sheet_validation_plan.py
```

Через Makefile:

```bash
make validation-plan
```

## Как использовать

1. Запустить `make preflight`.
2. Открыть `build/google-sheet-validation-plan.md`.
3. Проверить справочники.
4. Настроить проверку данных в закрытой Google Таблице.
5. Для сотрудников показывать понятные подписи, а коды использовать как стабильные значения.

## Важно

План не настраивает Google Таблицу автоматически. Он нужен как инструкция для ручной настройки выпадающих списков.
