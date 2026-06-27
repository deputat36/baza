# Публикация артефактов через GitHub Pages

## Назначение

Workflow `.github/workflows/pages-preview.yml` публикует артефакты сборки через GitHub Pages.

Это нужно, чтобы структуру базы знаний, HTML-превью и диагностические отчёты можно было открыть в браузере без скачивания XLSX и без сборки закрытой Google Таблицы.

## Что публикуется

Публикуется каталог:

```text
build/
```

Главная страница:

```text
build/index.html
```

Она содержит ссылки на:

- HTML-превью;
- XLSX-книгу;
- preflight-сводку;
- отчёт готовности к запуску;
- отчёт по незаполненным данным;
- планы Google Таблицы;
- отчёты по ID, схемам и покрытию CSV.

## Основные генераторы

```text
scripts/tools/build_html_preview.py
scripts/tools/build_artifact_index.py
```

## Как включить

В репозитории GitHub нужно открыть:

```text
Settings -> Pages
```

В разделе `Build and deployment` выбрать:

```text
Source: GitHub Actions
```

После этого workflow `Publish HTML preview` сможет публиковать страницу.

## Как запустить вручную

```text
Actions -> Publish HTML preview -> Run workflow
```

## Где смотреть результат

После успешного запуска GitHub покажет ссылку на Pages в блоке deployment.

Обычно адрес будет похож на:

```text
https://deputat36.github.io/baza/
```

Точный адрес нужно смотреть в настройках GitHub Pages или в результате workflow.

## Важно

Публиковать можно только безопасную публичную часть проекта.

Реальные телефоны, ФИО, внутренние контакты, клиентские данные и закрытые условия не должны попадать в CSV публичного репозитория.

## Если Pages не включён

Артефакты всё равно можно скачать из основного workflow:

```text
Actions -> Validate data files -> Artifacts -> baza-build-artifacts
```

И открыть локально:

```text
index.html
```
