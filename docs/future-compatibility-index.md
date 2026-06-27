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
- `docs/deal-hint-ui-map.md` — описание карты размещения подсказок в будущем интерфейсе.
- `docs/deal-hint-api-examples.md` — описание безопасных примеров request/response для будущего интерфейса.
- `docs/integration-json-fields.md` — описание обязательных верхнеуровневых полей JSON-контрактов.
- `docs/integration-contracts.md` — описание read-only контрактов будущей интеграции.
- `docs/integration-contract-report.md` — описание отчёта по готовности контрактов.
- `docs/deal-hint-rules.md` — описание правил будущих подсказок сделки.
- `docs/deal-hint-preview.md` — описание предпросмотра подсказок на безопасных сценариях.

## Данные

- `data/dictionaries/deal-signals.csv` — словарь допустимых сигналов сделки.
- `data/dictionaries/deal-audiences.csv` — словарь допустимых аудиторий подсказок.
- `data/dictionaries/deal-hint-ui-zones.csv` — словарь допустимых зон будущего интерфейса подсказок.
- `data/dictionaries/integration-contracts.csv` — реестр read-only контрактов будущей интеграции.
- `data/dictionaries/integration-json-fields.csv` — минимальные обязательные поля JSON-контрактов.
- `data/drafts/deal-hint-rules.csv` — черновик правил, которые связывают признаки сделки с ID базы знаний.
- `data/drafts/deal-hint-scenarios.csv` — безопасные тестовые сценарии без реальных сделок.
- `data/drafts/deal-hint-ui-map.csv` — карта размещения правил подсказок по зонам будущего интерфейса.

## Скрипты

- `scripts/tools/build_knowledge_index.py` — собирает `build/knowledge-index.json`.
- `scripts/tools/validate_knowledge_index.py` — проверяет структуру JSON-индекса.
- `scripts/tools/build_relationship_report.py` — собирает отчёты по связям.
- `scripts/tools/build_deal_hint_rules.py` — собирает JSON и отчёты по правилам подсказок.
- `scripts/tools/build_deal_signal_report.py` — собирает отчёт по покрытию сигналов.
- `scripts/tools/build_deal_hint_preview.py` — применяет правила к безопасным тестовым сценариям.
- `scripts/tools/build_deal_audience_report.py` — проверяет покрытие аудиторий правилами и сценариями.
- `scripts/tools/build_deal_hint_ui_map.py` — проверяет карту размещения подсказок в будущем интерфейсе.
- `scripts/tools/build_deal_hint_api_examples.py` — собирает безопасные примеры request/response для будущего интерфейса.
- `scripts/tools/validate_integration_json_fields.py` — проверяет обязательные поля JSON-контрактов.
- `scripts/tools/build_integration_contract_report.py` — проверяет готовность контрактов будущей интеграции.

## Артефакты сборки

- `build/knowledge-index.json`
- `build/relationship-report.md`
- `build/relationship-report.csv`
- `build/deal-hint-rules.json`
- `build/deal-hint-rules-report.md`
- `build/deal-hint-rules-report.csv`
- `build/deal-hint-ui-map.json`
- `build/deal-hint-ui-map-report.md`
- `build/deal-hint-ui-map-report.csv`
- `build/deal-signal-report.md`
- `build/deal-signal-report.csv`
- `build/deal-hint-preview.json`
- `build/deal-hint-preview.md`
- `build/deal-hint-preview.csv`
- `build/deal-audience-report.md`
- `build/deal-audience-report.csv`
- `build/deal-hint-api-examples.json`
- `build/deal-hint-api-examples.md`
- `build/deal-hint-api-examples.csv`
- `build/integration-json-fields-report.md`
- `build/integration-json-fields-report.csv`
- `build/integration-contract-report.md`
- `build/integration-contract-report.csv`

## Команды

```bash
make knowledge-check
make relationships
make deal-hints
make deal-signals
make deal-hint-preview
make deal-audiences
make deal-hint-ui-map
make deal-hint-api-examples
make integration-json-fields
make integration-contracts
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
- иметь определённую зону показа в будущем интерфейсе;
- иметь безопасный пример request/response, если она участвует в будущих подсказках;
- сохранять минимальную стабильную структуру JSON-контрактов;
- входить в явно описанные контракты интеграции, если она нужна будущему интерфейсу;
- проходить проверку на безопасных тестовых сценариях.
