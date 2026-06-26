# Этап реестра ID

## Добавлено

- Скрипт `scripts/tools/build_id_registry_report.py`.
- Документация `docs/id-registry.md`.
- Команда `make ids`.
- Реестр ID в `make preflight`.
- Реестр ID в GitHub Actions.
- `id-registry.md` в артефактах `baza-build-artifacts`.
- Обновлены preflight, GitHub Actions docs, artifacts docs, data report docs, exit codes и индекс проекта.

## Практический смысл

Теперь можно быстро увидеть все ID проекта, префиксы, возможные дубли и строки без распознанного ID.

## Следующий шаг

После запуска workflow открыть `id-registry.md` и проверить раздел `Возможные дубли` перед импортом в закрытую Google Таблицу.
