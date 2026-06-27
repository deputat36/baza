# Индекс слоя будущей совместимости

## Назначение

Этот набор файлов помогает развивать `baza` так, чтобы в будущем её можно было подключить к карточке сделки как read-only источник подсказок.

Проект Навигатора сделок сейчас не меняется.

## Документы

- `docs/future-navigator-compatibility.md` — принцип будущей связки с Навигатором сделок.
- `docs/knowledge-index.md` — описание JSON-индекса знаний.
- `docs/relationship-report.md` — описание отчёта по связям между ID.
- `docs/deal-hint-rules.md` — описание правил будущих подсказок сделки.

## Данные

- `data/drafts/deal-hint-rules.csv` — черновик правил, которые связывают признаки сделки с ID базы знаний.

## Скрипты

- `scripts/tools/build_knowledge_index.py` — собирает `build/knowledge-index.json`.
- `scripts/tools/validate_knowledge_index.py` — проверяет структуру JSON-индекса.
- `scripts/tools/build_relationship_report.py` — собирает отчёты по связям.
- `scripts/tools/build_deal_hint_rules.py` — собирает JSON и отчёты по правилам подсказок.

## Артефакты сборки

- `build/knowledge-index.json`
- `build/relationship-report.md`
- `build/relationship-report.csv`
- `build/deal-hint-rules.json`
- `build/deal-hint-rules-report.md`
- `build/deal-hint-rules-report.csv`

## Команды

```bash
make knowledge-check
make relationships
make deal-hints
make preflight
```

## Практический смысл

Каждая запись с ID должна быть пригодна для будущего показа в интерфейсе сделки:

- иметь понятный заголовок;
- иметь текст для поиска;
- иметь статус проверки;
- ссылаться на связанные документы, контакты, инструкции и ситуации через стабильные ID;
- попадать в правила подсказок, если она должна появляться при конкретном признаке сделки.
