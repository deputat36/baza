# Этап стартовой страницы артефактов

## Добавлено

- Генератор `build/index.html`.
- Стартовая страница артефактов сборки.
- Makefile-команда `artifact-index`.
- Сборка индекса в основном workflow.
- Публикация всего каталога `build/` через GitHub Pages.
- Документация по стартовой странице артефактов.
- Обновление GitHub Pages инструкции, preflight-инструкции, preflight-сводки и индекса проекта.

## Файлы

```text
scripts/tools/build_artifact_index.py
docs/artifact-index.md
Makefile
.github/workflows/validate-data.yml
.github/workflows/pages-preview.yml
scripts/tools/build_preflight_summary.py
docs/github-pages-preview.md
docs/preflight-check.md
docs/project-index.md
```

## Результат сборки

```text
build/index.html
```

## Практический смысл

После сборки теперь не нужно искать отдельные отчёты вручную. Достаточно открыть `build/index.html` и перейти к нужному артефакту.

На GitHub Pages главной страницей также должен стать общий индекс артефактов.

## Команды

```bash
make artifact-index
make preflight
```

## Следующий шаг

Перезапустить `Validate data files` и `Publish HTML preview`, затем открыть опубликованную Pages-страницу или скачать артефакт `baza-build-artifacts` и открыть `index.html`.
