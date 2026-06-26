# Этап preflight-сводки

## Добавлено

- Скрипт `scripts/tools/build_preflight_summary.py`.
- Документация `docs/preflight-summary.md`.
- Команда `make summary`.
- Preflight-сводка в `make preflight`.
- Preflight-сводка в GitHub Actions.
- `preflight-summary.md` в артефактах `baza-build-artifacts`.
- Обновлены artifacts docs, preflight docs, GitHub Actions docs, data report docs, exit codes и индекс проекта.

## Практический смысл

Теперь после сборки есть один стартовый файл `preflight-summary.md`, с которого удобно начинать ручную проверку перед импортом данных в закрытую Google Таблицу.

## Следующий шаг

После запуска workflow скачать `baza-build-artifacts` и открыть `preflight-summary.md` первым.
