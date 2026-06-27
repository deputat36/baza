"""
Конфигурация XLSX-сборки.

Модуль не должен зависеть от openpyxl или других внешних пакетов.
Его используют генератор XLSX и лёгкие проверки источников.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = ROOT / "build"
OUTPUT_FILE = BUILD_DIR / "baza-knowledge-mvp.xlsx"

SHEETS = [
    ("Справочники", [
        "data/dictionaries/object-types.csv",
        "data/dictionaries/statuses.csv",
        "data/dictionaries/priorities.csv",
        "data/dictionaries/categories-core.csv",
    ]),
    ("Контакты", [
        "templates/contacts-template.csv",
        "data/drafts/government-borisoglebsk.csv",
        "data/drafts/banks-mortgage.csv",
        "data/drafts/notaries-structure.csv",
        "data/drafts/cadastral-engineers.csv",
        "data/drafts/evaluators.csv",
        "data/drafts/jkh-borisoglebsk.csv",
        "data/drafts/management-companies.csv",
        "data/drafts/emergency-services.csv",
    ]),
    ("Ситуации", [
        "templates/situations-template.csv",
        "data/drafts/situations-real-estate.csv",
    ]),
    ("База знаний", [
        "templates/knowledge-template.csv",
        "data/drafts/documents-real-estate.csv",
        "data/drafts/document-templates.csv",
    ]),
    ("FAQ", [
        "data/drafts/faq-real-estate.csv",
    ]),
    ("Практика", [
        "templates/practice-note-template.csv",
        "data/drafts/common-mistakes.csv",
    ]),
    ("Предложения", [
        "templates/change-request-template.csv",
        "data/drafts/feedback-log-template.csv",
    ]),
    ("Синонимы", [
        "data/dictionaries/search-synonyms.csv",
        "data/drafts/search-test-cases.csv",
    ]),
    ("Новостройки", [
        "data/drafts/new-buildings.csv",
    ]),
    ("Подрядчики", [
        "data/drafts/contractors.csv",
    ]),
    ("Обучение", [
        "data/drafts/training-checklists.csv",
        "data/drafts/user-scenarios.csv",
    ]),
    ("Интеграция", [
        "data/dictionaries/deal-signals.csv",
        "data/dictionaries/deal-audiences.csv",
        "data/drafts/deal-hint-rules.csv",
        "data/drafts/deal-hint-scenarios.csv",
    ]),
]
