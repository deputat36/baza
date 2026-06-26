# Этап smoke-проверки HTML-превью

## Добавлено

- Скрипт `scripts/tools/validate_html_preview.py`.
- Makefile-команда `html-check`.
- Подключение smoke-проверки в `make preflight`.
- Проверка HTML-превью в workflow `Validate data files`.
- Проверка HTML-превью перед публикацией в workflow `Publish HTML preview`.
- Обновление документации по HTML-превью и preflight.
- Обновление индекса проекта.

## Практический смысл

CI теперь проверяет не только то, что генератор HTML не упал, но и то, что итоговый `index.html` действительно создан и содержит ключевые блоки.

## Команды

```bash
make html-check
make preflight
```

Или напрямую:

```bash
python scripts/tools/build_html_preview.py
python scripts/tools/validate_html_preview.py
```

## Следующий шаг

Перезапустить workflow:

```text
Actions -> Publish HTML preview -> Run workflow
```

или:

```text
Actions -> Validate data files -> Run workflow
```
