# Этап публикации HTML-превью через GitHub Pages

## Добавлено

- Workflow `Publish HTML preview`.
- Инструкция по включению GitHub Pages.
- Ссылки на Pages-просмотр в README, стартовом документе и HTML-preview инструкции.
- Обновление индекса проекта.

## Файлы

```text
.github/workflows/pages-preview.yml
docs/github-pages-preview.md
README.md
docs/start-here.md
docs/html-preview.md
docs/project-index.md
```

## Практический смысл

HTML-превью можно публиковать как обычную страницу GitHub Pages.

Это даёт простой способ посмотреть структуру базы знаний в браузере без скачивания артефактов, Excel и закрытой Google Таблицы.

## Что нужно включить в GitHub

```text
Settings -> Pages -> Build and deployment -> Source: GitHub Actions
```

## Как запустить

```text
Actions -> Publish HTML preview -> Run workflow
```

## Ожидаемый адрес

```text
https://deputat36.github.io/baza/
```

Точный адрес нужно смотреть в настройках GitHub Pages или в результате workflow.

## Ограничение

Публиковать можно только безопасную публичную часть проекта.

Реальные контакты, ФИО, внутренние условия и клиентские данные должны оставаться только в закрытой Google Таблице.
