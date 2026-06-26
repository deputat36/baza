# Артефакты GitHub Actions

## Что сохраняется

Workflow `.github/workflows/validate-data.yml` собирает и сохраняет артефакты из каталога `build/`.

Ожидаемые файлы:

- `preflight-summary.md` — сводка проверки и ручной чек-лист;
- `baza-knowledge-mvp.xlsx` — промежуточная Excel-книга;
- `data-report.md` — техническая сводка по CSV-файлам;
- `source-coverage-report.md` — покрытие CSV-файлов XLSX-сборкой;
- `id-registry.md` — реестр ID по CSV-файлам;
- `schema-report.md` — отчёт по схемам CSV.

## Как использовать

1. Открыть последний запуск GitHub Actions.
2. Проверить, что workflow завершился без ошибки.
3. Скачать артефакт `baza-build-artifacts`.
4. Сначала открыть `preflight-summary.md`.
5. Открыть XLSX и проверить структуру листов.
6. Открыть `data-report.md` и оценить наполненность разделов.
7. Открыть `source-coverage-report.md` и проверить CSV, которые не входят в XLSX.
8. Открыть `id-registry.md` и проверить возможные дубли ID.
9. Открыть `schema-report.md` и проверить заголовки CSV.

## Важно

Артефакты не должны содержать приватные рабочие данные.

Реальные контакты и внутренние материалы хранятся только в закрытой Google Таблице.
