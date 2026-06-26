# Этап отчёта по схемам CSV

## Добавлено

- Скрипт `scripts/tools/build_schema_report.py`.
- Документация `docs/schema-report.md`.
- Команда `make schemas`.
- Отчёт по схемам в `make preflight`.
- Отчёт по схемам в GitHub Actions.
- `schema-report.md` в артефактах `baza-build-artifacts`.
- Обновлены preflight, GitHub Actions docs, artifacts docs, data report docs, exit codes и индекс проекта.

## Практический смысл

Теперь можно быстро увидеть заголовки всех CSV, группы одинаковых схем, пустые заголовки и повторяющиеся колонки.

## Следующий шаг

После запуска workflow открыть `schema-report.md` и проверить, что однотипные CSV имеют ожидаемые заголовки перед импортом в закрытую Google Таблицу.
