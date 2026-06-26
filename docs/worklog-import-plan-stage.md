# Этап генерируемого плана импорта

## Добавлено

- Скрипт `scripts/tools/build_import_plan.py`.
- Документация `docs/generated-import-plan.md`.
- Команда `make import-plan`.
- `build/import-plan.md` и `build/import-plan.csv` в `make preflight`.
- План импорта в GitHub Actions.
- План импорта в артефактах `baza-build-artifacts`.
- Обновлены preflight summary, import manifest, artifacts docs, preflight docs, data report docs, exit codes и индекс проекта.

## Практический смысл

Теперь порядок переноса CSV в закрытую Google Таблицу строится автоматически из XLSX-конфига и попадает в артефакты сборки.

## Следующий шаг

После запуска workflow открыть `preflight-summary.md`, затем `import-plan.md` и переносить CSV в закрытую Google Таблицу по указанному порядку.
