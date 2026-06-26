# Публикация HTML-превью через GitHub Pages

## Назначение

Workflow `.github/workflows/pages-preview.yml` публикует HTML-превью базы знаний через GitHub Pages.

Это нужно, чтобы структуру CSV можно было открыть в браузере без скачивания XLSX и без сборки закрытой Google Таблицы.

## Что публикуется

Публикуется только результат генератора:

```text
build/html-preview/index.html
```

Генератор:

```text
scripts/tools/build_html_preview.py
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

HTML-превью всё равно можно скачать из артефактов основного workflow:

```text
Actions -> Validate data files -> Artifacts -> baza-build-artifacts
```

И открыть локально:

```text
html-preview/index.html
```
