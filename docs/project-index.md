# Индекс проекта

## Назначение

Этот файл помогает быстро понять, где что находится в репозитории.

Репозиторий содержит безопасную публичную часть базы знаний: структуру, шаблоны, черновики и регламенты.

Реальные телефоны, ФИО, внутренние контакты и закрытые условия должны храниться только в закрытой Google Таблице.

## Главные документы

- `README.md` — общее описание проекта.
- `docs/concept.md` — концепция базы знаний.
- `docs/structure.md` — сущности, категории и логика ID.
- `docs/google-sheets-mvp.md` — MVP в Google Таблице.
- `docs/google-sheet-layout.md` — макет листов.
- `docs/private-google-sheet-setup.md` — настройка закрытой таблицы.
- `docs/mvp-release-plan.md` — план первого запуска.
- `docs/repository-review.md` — обзор текущего состояния.

## Запуск, проверка и тестирование

- `docs/import-to-google-sheets.md` — порядок импорта CSV.
- `docs/import-manifest.md` — ручной манифест импорта.
- `docs/generated-import-plan.md` — генерируемый план импорта.
- `docs/generated-google-sheet-tabs-plan.md` — генерируемый план листов Google Таблицы.
- `docs/generated-google-sheet-validation-plan.md` — генерируемый план выпадающих списков.
- `docs/generated-google-sheet-formatting-plan.md` — генерируемый план оформления Google Таблицы.
- `docs/google-sheet-launch-checklist.md` — чек-лист запуска таблицы.
- `docs/first-user-test.md` — сценарий первого теста.
- `docs/office-demo-script.md` — сценарий демонстрации на планёрке.
- `docs/weekly-maintenance-regulation.md` — еженедельное обслуживание базы.
- `docs/data-normalization-plan.md` — нормализация данных перед импортом.
- `docs/csv-validation.md` — проверка структуры CSV.
- `docs/workbook-config.md` — конфигурация XLSX-сборки.
- `docs/workbook-sources-validation.md` — проверка источников XLSX.
- `docs/source-coverage-report.md` — покрытие CSV-файлов XLSX-сборкой.
- `docs/id-registry.md` — реестр ID и возможные дубли.
- `docs/schema-report.md` — отчёт по схемам CSV.
- `docs/preflight-summary.md` — сводка preflight-артефактов.
- `docs/privacy-scan.md` — проверка публичной безопасности.
- `docs/preflight-check.md` — единая проверка перед публикацией.
- `docs/ci-exit-codes.md` — коды завершения проверок.
- `docs/github-actions-validation.md` — автоматическая проверка в GitHub Actions.
- `docs/github-actions-artifacts.md` — артефакты GitHub Actions.
- `docs/data-report.md` — технический отчёт по CSV-файлам.

## Правила и безопасность

- `docs/filling-rules.md` — правила заполнения.
- `docs/data-quality-checklist.md` — чек-лист качества данных.
- `docs/security-and-privacy.md` — безопасность и приватность.
- `docs/google-forms-for-employees.md` — формы для предложений сотрудников.
- `.gitignore` — защита от случайной публикации приватных файлов.

## Шаблоны

- `templates/contacts-template.csv` — контакты.
- `templates/knowledge-template.csv` — база знаний.
- `templates/situations-template.csv` — ситуации.
- `templates/change-request-template.csv` — предложения изменений.
- `templates/practice-note-template.csv` — практические заметки.

## Черновики данных

- `data/drafts/government-borisoglebsk.csv` — государственные органы.
- `data/drafts/documents-real-estate.csv` — документы.
- `data/drafts/situations-real-estate.csv` — типовые ситуации.
- `data/drafts/banks-mortgage.csv` — банки и ипотека.
- `data/drafts/notaries-structure.csv` — нотариусы.
- `data/drafts/cadastral-engineers.csv` — кадастровые инженеры.
- `data/drafts/evaluators.csv` — оценщики.
- `data/drafts/jkh-borisoglebsk.csv` — ЖКХ.
- `data/drafts/management-companies.csv` — управляющие компании.
- `data/drafts/online-services.csv` — онлайн-сервисы.
- `data/drafts/contractors.csv` — подрядчики.
- `data/drafts/emergency-services.csv` — экстренные службы.
- `data/drafts/document-templates.csv` — шаблоны документов.
- `data/drafts/faq-real-estate.csv` — FAQ.
- `data/drafts/new-buildings.csv` — новостройки.
- `data/drafts/internal-office-roles-template.csv` — внутренние роли.
- `data/drafts/training-checklists.csv` — обучение.
- `data/drafts/common-mistakes.csv` — частые ошибки.
- `data/drafts/user-scenarios.csv` — пользовательские сценарии.

## Справочники

- `data/dictionaries/object-types.csv` — типы объектов.
- `data/dictionaries/statuses.csv` — статусы.
- `data/dictionaries/priorities.csv` — приоритеты.
- `data/dictionaries/categories-core.csv` — категории.
- `data/dictionaries/search-synonyms.csv` — поисковые синонимы.

## Инструменты

- `scripts/tools/workbook_config.py` — конфигурация XLSX-сборки.
- `scripts/tools/build_workbook_from_csv.py` — сборка XLSX.
- `scripts/tools/validate_workbook_sources.py` — проверка источников XLSX.
- `scripts/tools/build_data_report.py` — отчёт по CSV-файлам.
- `scripts/tools/build_source_coverage_report.py` — отчёт покрытия CSV-источников.
- `scripts/tools/build_id_registry_report.py` — реестр ID.
- `scripts/tools/build_schema_report.py` — отчёт по схемам CSV.
- `scripts/tools/build_import_plan.py` — план импорта в Google Таблицу.
- `scripts/tools/build_google_sheet_tabs_plan.py` — план листов Google Таблицы.
- `scripts/tools/build_google_sheet_validation_plan.py` — план выпадающих списков Google Таблицы.
- `scripts/tools/build_google_sheet_formatting_plan.py` — план оформления Google Таблицы.
- `scripts/tools/build_preflight_summary.py` — preflight-сводка.
- `scripts/tools/validate_csv_structure.py` — проверка CSV.
- `scripts/tools/privacy_scan.py` — проверка публичной безопасности.
- `scripts/tools/list_project_files.py` — инвентаризация файлов.

## Будущее развитие

- `crm-design/entities.md` — черновик сущностей будущего CRM-модуля.

## Рекомендуемый порядок просмотра

1. `README.md`
2. `docs/intermediate-preview.md`
3. `docs/project-index.md`
4. `docs/google-sheets-mvp.md`
5. `docs/private-google-sheet-setup.md`
6. `docs/google-sheet-launch-checklist.md`
7. `data/drafts/`
