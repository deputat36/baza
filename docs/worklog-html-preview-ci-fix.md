# Исправление HTML-превью в CI

## Проблема

Workflow падал на шаге:

```text
python scripts/tools/build_html_preview.py
```

Ошибка:

```text
TypeError: tuple indices must be integers or slices, not str
```

## Причина

Генератор HTML-превью ожидал, что `SHEETS` из `scripts/tools/workbook_config.py` содержит словари с ключами `title` и `source`.

Фактический формат `SHEETS`:

```text
("Название листа", ["source1.csv", "source2.csv"])
```

## Исправление

`scripts/tools/build_html_preview.py` обновлён:

- добавлен `iter_workbook_sources()`;
- поддержан текущий tuple-формат `SHEETS`;
- сохранена совместимость со словарным форматом на будущее;
- HTML-превью теперь собирает все CSV-источники каждого XLSX-листа.

## Следующий шаг

Повторно запустить workflow:

```text
Actions -> Publish HTML preview -> Run workflow
```

или основной workflow:

```text
Actions -> Validate data files -> Run workflow
```
