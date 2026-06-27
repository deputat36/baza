# Индекс слоя будущей совместимости

## Назначение

Этот набор файлов помогает развивать `baza` так, чтобы в будущем её можно было подключить к карточке сделки как read-only источник подсказок.

Проект Навигатора сделок сейчас не меняется.

## Документы

- `docs/future-navigator-compatibility.md` — принцип будущей связки с Навигатором сделок.
- `docs/knowledge-index.md` — описание JSON-индекса знаний.
- `docs/relationship-report.md` — описание отчёта по связям между ID.

## Скрипты

- `scripts/tools/build_knowledge_index.py` — собирает `build/knowledge-index.json`.
- `scripts/tools/validate_knowledge_index.py` — проверяет структуру JSON-индекса.
- `scripts/tools/build_relationship_report.py` — собирает отчёты по связям.

## Артефакты сборки

- `build/knowledge-index.json`
- `build/relationship-report.md`
- `build/relationship-report.csv`

## Команды

```bash
make knowledge-check
make relationships
make preflight
```

## Практический смысл

Каждая запись с ID должна быть пригодна для будущего показа в интерфейсе сделки:

- иметь понятный заголовок;
- иметь текст для поиска;
- иметь статус проверки;
- ссылаться на связанные документы, контакты, инструкции и ситуации через стабильные ID.
