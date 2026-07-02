# Стартовая страница артефактов сборки

## Назначение

Файл `build/index.html` — единая стартовая страница для просмотра результатов сборки.

Он содержит ссылки на:

- HTML-превью;
- XLSX-книгу;
- preflight-сводку;
- pipeline-health отчет;
- отчёт готовности к запуску;
- отчёт по незаполненным данным;
- планы Google Таблицы;
- отчёты по ID, схемам и покрытию CSV;
- управленческие отчеты и интеграционные артефакты.

## Генератор

```text
scripts/tools/build_artifact_index.py
```

## Запуск

Через Makefile:

```bash
make artifact-index
```

В составе полной проверки:

```bash
make preflight
```

## Результат

```text
build/index.html
```

## Как использовать

1. Собрать `make preflight`.
2. Открыть `build/index.html`.
3. Проверить `pipeline-health-report.md`, если недавно менялись Makefile, workflow или генераторы.
4. Перейти к нужному отчёту или превью.
5. Сначала смотреть `launch-readiness-report.md`.
6. Затем смотреть `missing-values-report.md`.
7. После этого переходить к планам Google Таблицы.

## GitHub Pages

Workflow `Publish HTML preview` публикует весь каталог `build/`.

Поэтому главная страница Pages должна открывать именно `build/index.html`.

Ожидаемый адрес:

```text
https://deputat36.github.io/baza/
```

Точный адрес нужно смотреть в настройках GitHub Pages или в результате workflow.
