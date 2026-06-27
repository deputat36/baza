# Индекс слоя будущей совместимости

## Назначение

Этот набор файлов помогает развивать `baza` так, чтобы в будущем её можно было подключить к карточке сделки как read-only источник подсказок.

Проект Навигатора сделок сейчас не меняется.

## Документы

- `docs/future-navigator-compatibility.md` — принцип будущей связки с Навигатором сделок.
- `docs/knowledge-index.md` — описание JSON-индекса знаний.
- `docs/relationship-report.md` — описание отчёта по связям между ID.
- `docs/deal-signals.md` — описание словаря сигналов сделки.
- `docs/deal-signal-report.md` — описание отчёта по покрытию сигналов.
- `docs/deal-audiences.md` — описание словаря аудиторий подсказок.
- `docs/deal-audience-report.md` — описание отчёта по покрытию аудиторий.
- `docs/deal-hint-rules.md` — описание правил будущих подсказок сделки.
- `docs/deal-hint-preview.md` — описание предпросмотра подсказок на безопасных сценариях.

## Данные

- `data/dictionaries/deal-signals.csv` — словарь допустимых сигналов сделки.
- `data/dictionaries/deal-audiences.csv` — словарь допустимых аудиторий подсказок.
- `data/drafts/deal-hint-rules.csv` — черновик правил, которые связывают признаки сделки с ID базы знаний.
- `data/drafts/deal-hint-scenarios.csv` — безопасные тестовые сценарии без реальных сделок.

## Скрипты

- `scripts/tools/build_knowledge_index.py` — собирает `build/knowledge-index.json`.
- `scripts/tools/validate_knowledge_index.py` — проверяет структуру JSON-индекса.
- `scripts/tools/build_relationship_report.py` — собирает отчёты по связям.
- `scripts/tools/build_deal_hint_rules.py` — собирает JSON и отчёты по правилам подсказок.
- `scripts/tools/build_deal_signal_report.py` — собирает отчёт по покрытию сигналов.
- `scripts/tools/build_deal_hint_preview.py` — применяет правила к безопасным тестовым сценариям.
- `scripts/tools/build_deal_audience_report.py` — проверяет покрытие аудиторий правилами и сценариями.

## Артефакты сборки

- `build/knowledge-index.json`
- `build/relationship-report.md`
- `build/relationship-report.csv`
- `build/deal-hint-rules.json`
- `build/deal-hint-rules-report.md`
- `build/deal-hint-rules-report.csv`
- `build/deal-signal-report.md`
- `build/deal-signal-report.csv`
- `build/deal-hint-preview.json`
- `build/deal-hint-preview.md`
- `build/deal-hint-preview.csv`
- `build/deal-audience-report.md`
- `build/deal-audience-report.csv`

## Команды

```bash
make knowledge-check
make relationships
make deal-hints
make deal-signals
make deal-hint-preview
make deal-audiences
make preflight
```

## Практический смысл

Каждая запись с ID должна быть пригодна для будущего показа в интерфейсе сделки:

- иметь понятный заголовок;
- иметь текст для поиска;
- иметь статус проверки;
- ссылаться на связанные документы, контакты, инструкции и ситуации через стабильные ID;
- попадать в правила подсказок, если она должна появляться при конкретном признаке сделки;
- использовать только сигналы из контролируемого словаря;
- использовать только аудитории из контролируемого словаря;
- проходить проверку на безопасных тестовых сценариях.
