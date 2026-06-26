# Этап плана выпадающих списков Google Таблицы

## Добавлено

- Скрипт `scripts/tools/build_google_sheet_validation_plan.py`.
- Документация `docs/generated-google-sheet-validation-plan.md`.
- Команда `make validation-plan`.
- `build/google-sheet-validation-plan.md` и `build/google-sheet-validation-plan.csv` в `make preflight`.
- План выпадающих списков в GitHub Actions.
- План выпадающих списков в артефактах `baza-build-artifacts`.
- Обновлены preflight summary, artifacts docs, preflight docs, data report docs, exit codes, google sheet layout и индекс проекта.

## Практический смысл

Теперь перед настройкой закрытой Google Таблицы есть отдельный план выпадающих списков по справочникам: статусы, приоритеты, категории и типы объектов.

## Следующий шаг

После запуска workflow открыть `preflight-summary.md`, затем `google-sheet-validation-plan.md` и настроить проверку данных в рабочих листах Google Таблицы.
