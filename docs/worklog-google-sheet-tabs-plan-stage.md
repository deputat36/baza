# Этап плана листов Google Таблицы

## Добавлено

- Скрипт `scripts/tools/build_google_sheet_tabs_plan.py`.
- Документация `docs/generated-google-sheet-tabs-plan.md`.
- Команда `make tabs-plan`.
- `build/google-sheet-tabs-plan.md` и `build/google-sheet-tabs-plan.csv` в `make preflight`.
- План листов в GitHub Actions.
- План листов в артефактах `baza-build-artifacts`.
- Обновлены preflight summary, artifacts docs, preflight docs, data report docs, exit codes, google sheet layout и индекс проекта.

## Практический смысл

Теперь перед созданием закрытой Google Таблицы есть автоматически собираемый план листов: порядок, количество CSV-источников, строки, колонки и базовые рекомендации по настройке.

## Следующий шаг

После запуска workflow открыть `preflight-summary.md`, затем `google-sheet-tabs-plan.md`, создать листы и потом переносить CSV по `import-plan.md`.
