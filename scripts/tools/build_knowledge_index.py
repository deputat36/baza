"""
Генератор JSON-индекса базы знаний.

Индекс нужен как нейтральный read-only формат, который в будущем можно будет
подключить к внутреннему порталу, CRM или Навигатору сделок без смешивания
таблиц и без публикации приватных данных.

Запуск из корня репозитория:
python scripts/tools/build_knowledge_index.py
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from workbook_config import ROOT, BUILD_DIR, SHEETS
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"
    SHEETS = []

OUTPUT_FILE = BUILD_DIR / "knowledge-index.json"
SCHEMA_VERSION = "kb-index-v1"

TITLE_COLUMNS = [
    "Название",
    "Ситуация",
    "Вопрос",
    "Организация",
    "Контакт",
    "Роль",
    "Категория",
    "ID",
]

SUMMARY_COLUMNS = [
    "Кратко",
    "Краткое описание",
    "Описание",
    "Что делать",
    "Ответ",
    "Когда нужен",
]

STATUS_COLUMNS = ["Статус", "status"]
PRIORITY_COLUMNS = ["Приоритет", "priority"]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def first_present(row: dict[str, str], columns: list[str]) -> str:
    for column in columns:
        value = (row.get(column) or "").strip()
        if value:
            return value
    return ""


def split_ids(value: str) -> list[str]:
    if not value:
        return []
    normalized = value.replace(",", ";")
    return [part.strip() for part in normalized.split(";") if part.strip()]


def related_fields(row: dict[str, str]) -> dict[str, list[str]]:
    result = {}
    for key, value in row.items():
        if key.startswith("Связанные"):
            ids = split_ids(value or "")
            if ids:
                result[key] = ids
    return result


def compact_row(row: dict[str, str]) -> dict[str, str]:
    return {key: value for key, value in row.items() if (value or "").strip()}


def build_search_text(row: dict[str, str]) -> str:
    values = []
    for value in row.values():
        text = (value or "").strip()
        if text:
            values.append(text)
    return " ".join(values)


def iter_sources():
    seen = set()
    for sheet_name, sources in SHEETS:
        for source in sources:
            if source in seen:
                continue
            seen.add(source)
            yield sheet_name, source, ROOT / source


def build_index():
    records = []
    skipped_sources = []

    for sheet_name, source, path in iter_sources():
        if not path.exists():
            skipped_sources.append({"source": source, "reason": "missing"})
            continue

        for row_number, row in enumerate(read_csv(path), start=2):
            row_id = (row.get("ID") or "").strip()
            if not row_id:
                continue

            record = {
                "id": row_id,
                "sheet": sheet_name,
                "source": source,
                "row_number": row_number,
                "title": first_present(row, TITLE_COLUMNS),
                "summary": first_present(row, SUMMARY_COLUMNS),
                "status": first_present(row, STATUS_COLUMNS),
                "priority": first_present(row, PRIORITY_COLUMNS),
                "related": related_fields(row),
                "search_text": build_search_text(row),
                "raw": compact_row(row),
            }
            records.append(record)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "deputat36/baza CSV drafts and templates",
        "purpose": "Read-only knowledge index for preview, search and future integrations.",
        "records_count": len(records),
        "skipped_sources": skipped_sources,
        "records": records,
    }


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    data = build_index()
    OUTPUT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Готово: {OUTPUT_FILE.relative_to(ROOT)} ({data['records_count']} записей)")


if __name__ == "__main__":
    main()
