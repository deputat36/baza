# Этап покрытия CSV-источников

## Добавлено

- Скрипт `scripts/tools/build_source_coverage_report.py`.
- Документация `docs/source-coverage-report.md`.
- Команда `make coverage`.
- Отчёт покрытия в `make preflight`.
- Отчёт покрытия в GitHub Actions.
- `source-coverage-report.md` в артефактах `baza-build-artifacts`.
- Обновлены preflight, GitHub Actions docs, artifacts docs, data report docs и индекс проекта.

## Практический смысл

Теперь можно видеть, какие CSV входят в XLSX-сборку, какие отсутствуют, какие не включены в рабочую книгу и есть ли дубли в конфиге.

## Следующий шаг

После запуска workflow открыть `source-coverage-report.md` и решить, какие CSV нужно добавить в XLSX, а какие оставить служебными.
