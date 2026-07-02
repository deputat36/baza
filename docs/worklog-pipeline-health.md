# Worklog: pipeline-health

## Дата

2026-07-02

## Задача

Добавить технический слой контроля согласованности сборочного контура проекта `deputat36/baza`.

## Причина

В проекте уже много генераторов, отчетов и артефактов. При дальнейшем развитии есть риск, что новый скрипт будет добавлен только в одно место: например, в Makefile, но не в GitHub Actions, или в workflow, но не в индекс артефактов.

`pipeline-health` нужен, чтобы быстрее находить такие рассинхронизации.

## Что сделано

Добавлены и обновлены файлы:

- `scripts/tools/build_pipeline_health_report.py` — генератор отчета;
- `Makefile` — добавлена цель `pipeline-health`, она включена в `preflight`;
- `.github/workflows/validate-data.yml` — добавлен запуск отчета в GitHub Actions;
- `docs/pipeline-health.md` — документация по проверке;
- `scripts/tools/build_preflight_summary.py` — новый отчет добавлен в preflight-сводку;
- `scripts/tools/build_artifact_index.py` — новый отчет добавлен на стартовую страницу артефактов;
- `README.md` — добавлены команда, документ и артефакты;
- `docs/project-index.md` — обновлена карта проекта;
- `docs/artifact-index.md` — добавлено описание нового отчета.

## Что создает генератор

- `build/pipeline-health-report.md`
- `build/pipeline-health-report.csv`

## Что проверяет

- обязательные управляющие файлы;
- ключевые цели Makefile;
- наличие скриптов, на которые ссылаются Makefile и workflow;
- расхождения между Makefile и GitHub Actions;
- маркеры README;
- наличие ключевых артефактов в preflight-сводке;
- наличие ключевых артефактов в индексе сборки;
- наличие `summary`, `artifact-index`, `pipeline-health` и `inventory` в цепочке `preflight`.

## Ограничения

Проверка не заменяет полный запуск `make preflight` и не проверяет смысловую актуальность базы знаний.

Она отвечает только за техническую согласованность сборочного контура.

## Следующий шаг

Запустить GitHub Actions или локально выполнить:

```bash
make pipeline-health
make preflight
```

После первого запуска проверить, нет ли WARN по расхождениям Makefile и workflow.
