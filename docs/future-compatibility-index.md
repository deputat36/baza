# Индекс слоя будущей совместимости

## Назначение

Этот набор файлов помогает развивать `baza` так, чтобы в будущем её можно было подключить к карточке сделки как read-only источник подсказок.

Проект Навигатора сделок сейчас не меняется.

## Документы

- `docs/future-navigator-compatibility.md` — принцип будущей связки с Навигатором сделок.
- `docs/manager-dashboard.md` — описание управленческой сводки.
- `docs/role-navigation.md` — описание навигации по ролям сотрудников.
- `docs/section-ownership.md` — описание ответственности за разделы базы.
- `docs/office-acceptance-tests.md` — описание приемочных сценариев офиса.
- `docs/role-training.md` — описание обучения сотрудников по ролям.
- `docs/office-launch-packet.md` — описание единого пакета проверки перед запуском.
- `docs/office-launch-checklist.md` — описание чек-листа запуска базы в офисе.
- `docs/operating-rhythm.md` — описание регулярной эксплуатации после запуска.
- `docs/data-freshness.md` — описание контроля актуальности данных.
- `docs/change-request-queue.md` — описание очереди предложений и исправлений.
- `docs/knowledge-index.md` — описание JSON-индекса знаний.
- `docs/relationship-report.md` — описание отчёта по связям между ID.
- `docs/deal-signals.md` — описание словаря сигналов сделки.
- `docs/deal-signal-report.md` — описание отчёта по покрытию сигналов.
- `docs/deal-audiences.md` — описание словаря аудиторий подсказок.
- `docs/deal-audience-report.md` — описание отчёта по покрытию аудиторий.
- `docs/deal-hint-ui-map.md` — описание карты размещения подсказок в будущем интерфейсе.
- `docs/deal-hint-api-examples.md` — описание безопасных примеров request/response для будущего интерфейса.
- `docs/integration-data-visibility.md` — описание публичных и закрытых данных будущей интеграции.
- `docs/integration-access-matrix.md` — описание матрицы доступа ролей к областям данных.
- `docs/integration-json-fields.md` — описание обязательных верхнеуровневых полей JSON-контрактов.
- `docs/integration-contracts.md` — описание read-only контрактов будущей интеграции.
- `docs/integration-contract-report.md` — описание отчёта по готовности контрактов.
- `docs/deal-hint-rules.md` — описание правил будущих подсказок сделки.
- `docs/deal-hint-preview.md` — описание предпросмотра подсказок на безопасных сценариях.

## Данные

- `data/dictionaries/freshness-policies.csv` — политики актуальности данных.
- `data/dictionaries/change-request-statuses.csv` — статусы заявок на изменение.
- `data/dictionaries/deal-signals.csv` — словарь допустимых сигналов сделки.
- `data/dictionaries/deal-audiences.csv` — словарь допустимых аудиторий подсказок.
- `data/dictionaries/deal-hint-ui-zones.csv` — словарь допустимых зон будущего интерфейса подсказок.
- `data/dictionaries/integration-contracts.csv` — реестр read-only контрактов будущей интеграции.
- `data/dictionaries/integration-json-fields.csv` — минимальные обязательные поля JSON-контрактов.
- `data/dictionaries/integration-data-visibility.csv` — карта публичных и закрытых данных.
- `data/drafts/data-freshness-register.csv` — реестр контроля актуальности разделов.
- `data/drafts/change-request-queue.csv` — очередь предложений и исправлений.
- `data/drafts/role-navigation-map.csv` — навигация по ролям сотрудников.
- `data/drafts/section-ownership-matrix.csv` — матрица владельцев разделов базы.
- `data/drafts/office-acceptance-tests.csv` — приемочные сценарии офиса.
- `data/drafts/role-training-plan.csv` — план обучения сотрудников по ролям.
- `data/drafts/office-launch-checklist.csv` — чек-лист запуска базы в офисе.
- `data/drafts/operating-rhythm.csv` — регламент регулярной эксплуатации базы.
- `data/drafts/deal-hint-rules.csv` — черновик правил, которые связывают признаки сделки с ID базы знаний.
- `data/drafts/deal-hint-scenarios.csv` — безопасные тестовые сценарии без реальных сделок.
- `data/drafts/deal-hint-ui-map.csv` — карта размещения правил подсказок по зонам будущего интерфейса.
- `data/drafts/integration-access-matrix.csv` — матрица доступа ролей к публичным и закрытым данным.

## Скрипты

- `scripts/tools/build_manager_dashboard.py` — собирает короткую управленческую сводку из детальных отчётов.
- `scripts/tools/build_role_navigation_report.py` — собирает отчёт по навигации для ролей.
- `scripts/tools/build_section_ownership_report.py` — собирает отчёт по владельцам разделов базы.
- `scripts/tools/build_office_acceptance_test_report.py` — собирает отчёт по приемочным сценариям офиса.
- `scripts/tools/build_role_training_report.py` — собирает отчёт по обучению сотрудников.
- `scripts/tools/build_office_launch_packet.py` — собирает единый пакет проверки перед запуском.
- `scripts/tools/build_office_launch_checklist_report.py` — собирает отчёт по чек-листу запуска базы в офисе.
- `scripts/tools/build_operating_rhythm_report.py` — собирает отчёт по регулярной эксплуатации базы.
- `scripts/tools/build_data_freshness_report.py` — собирает отчёт актуальности данных.
- `scripts/tools/build_change_request_report.py` — собирает отчёт по очереди предложений и исправлений.
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
- `scripts/tools/build_integration_data_visibility_report.py` — проверяет карту публичных и закрытых данных.
- `scripts/tools/build_integration_access_report.py` — проверяет матрицу доступа ролей.
- `scripts/tools/build_integration_contract_report.py` — проверяет готовность контрактов будущей интеграции.

## Артефакты сборки

- `build/manager-dashboard.md`
- `build/manager-dashboard.csv`
- `build/role-navigation-report.md`
- `build/role-navigation-report.csv`
- `build/section-ownership-report.md`
- `build/section-ownership-report.csv`
- `build/office-acceptance-test-report.md`
- `build/office-acceptance-test-report.csv`
- `build/role-training-report.md`
- `build/role-training-report.csv`
- `build/office-launch-packet.md`
- `build/office-launch-packet.csv`
- `build/office-launch-checklist-report.md`
- `build/office-launch-checklist-report.csv`
- `build/operating-rhythm-report.md`
- `build/operating-rhythm-report.csv`
- `build/data-freshness-report.md`
- `build/data-freshness-report.csv`
- `build/change-request-report.md`
- `build/change-request-report.csv`
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
- `build/integration-data-visibility-report.md`
- `build/integration-data-visibility-report.csv`
- `build/integration-access-report.md`
- `build/integration-access-report.csv`
- `build/integration-json-fields-report.md`
- `build/integration-json-fields-report.csv`
- `build/integration-contract-report.md`
- `build/integration-contract-report.csv`

## Команды

```bash
make manager-dashboard
make role-navigation
make ownership
make acceptance-tests
make role-training
make launch-packet
make operating-rhythm
make office-launch
make freshness
make change-requests
make knowledge-check
make relationships
make deal-hints
make deal-signals
make deal-hint-preview
make deal-audiences
make deal-hint-ui-map
make deal-hint-api-examples
make integration-json-fields
make integration-visibility
make integration-access
make integration-contracts
make preflight
```

## Практический смысл

Каждая запись с ID должна быть пригодна для будущего показа в интерфейсе сделки:

- иметь понятный заголовок;
- иметь текст для поиска;
- иметь статус проверки;
- иметь понятный срок повторной проверки;
- иметь управленческую сводку рисков и ближайших действий;
- иметь понятный маршрут просмотра для разных ролей сотрудников;
- иметь владельца и замещающего для эксплуатации после запуска;
- проходить ручную приемку по роли сотрудника перед запуском;
- быть включенной в обучение сотрудников, если она влияет на рабочий процесс;
- входить в единый пакет проверки перед запуском;
- входить в регулярный цикл эксплуатации после запуска;
- входить в понятный чек-лист запуска в офисе, если она влияет на готовность базы;
- иметь контролируемый процесс предложений и исправлений;
- ссылаться на связанные документы, контакты, инструкции и ситуации через стабильные ID;
- попадать в правила подсказок, если она должна появляться при конкретном признаке сделки;
- использовать только сигналы из контролируемого словаря;
- использовать только аудитории из контролируемого словаря;
- иметь определённую зону показа в будущем интерфейсе;
- иметь безопасный пример request/response, если она участвует в будущих подсказках;
- сохранять минимальную стабильную структуру JSON-контрактов;
- иметь понятный уровень видимости: публичный или закрытый контур;
- иметь понятную матрицу доступа ролей к публичным и закрытым данным;
- входить в явно описанные контракты интеграции, если она нужна будущему интерфейсу;
- проходить проверку на безопасных тестовых сценариях.
