# Этап отчёта готовности к запуску

## Добавлено

- Генератор отчёта готовности разделов к запуску.
- Markdown- и CSV-версии отчёта.
- Makefile-команда `readiness`.
- Сборка отчёта в GitHub Actions.
- Учёт отчёта в preflight-сводке.
- Документация по отчёту.
- Обновление preflight-инструкции и индекса проекта.

## Файлы

```text
scripts/tools/build_launch_readiness_report.py
docs/launch-readiness-report.md
Makefile
.github/workflows/validate-data.yml
scripts/tools/build_preflight_summary.py
docs/preflight-check.md
docs/project-index.md
```

## Результаты сборки

```text
build/launch-readiness-report.md
build/launch-readiness-report.csv
```

## Практический смысл

После сборки можно быстро увидеть, какие листы будущей закрытой Google Таблицы имеют статус `READY`, `CHECK` или `DRAFT`.

## Команды

```bash
make readiness
make preflight
```

## Следующий шаг

Перезапустить workflow `Validate data files` и открыть `launch-readiness-report.md` в артефактах сборки.
