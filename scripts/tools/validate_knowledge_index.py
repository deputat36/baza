"""
Проверка JSON-индекса базы знаний.

Запуск из корня репозитория:
python scripts/tools/build_knowledge_index.py
python scripts/tools/validate_knowledge_index.py
"""

from __future__ import annotations

import json
from pathlib import Path

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

INDEX_FILE = BUILD_DIR / "knowledge-index.json"
EXPECTED_SCHEMA = "kb-index-v1"
REQUIRED_RECORD_FIELDS = [
    "id",
    "sheet",
    "source",
    "row_number",
    "title",
    "summary",
    "status",
    "priority",
    "related",
    "search_text",
    "raw",
]


def fail(message: str):
    print(f"Ошибка: {message}")
    raise SystemExit(1)


def load_index():
    if not INDEX_FILE.exists():
        fail(f"файл не найден: {INDEX_FILE.relative_to(ROOT)}")
    try:
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"некорректный JSON: {exc}")


def validate_record(record: dict, position: int, seen_ids: set[str], problems: list[str]):
    for field in REQUIRED_RECORD_FIELDS:
        if field not in record:
            problems.append(f"запись {position}: нет поля {field}")

    record_id = str(record.get("id") or "").strip()
    if not record_id:
        problems.append(f"запись {position}: пустой id")
    elif record_id in seen_ids:
        problems.append(f"запись {position}: дубль id {record_id}")
    else:
        seen_ids.add(record_id)

    if not str(record.get("title") or "").strip():
        problems.append(f"{record_id or position}: пустой title")

    if not str(record.get("search_text") or "").strip():
        problems.append(f"{record_id or position}: пустой search_text")

    if not isinstance(record.get("related"), dict):
        problems.append(f"{record_id or position}: related должен быть объектом")

    if not isinstance(record.get("raw"), dict):
        problems.append(f"{record_id or position}: raw должен быть объектом")


def main():
    data = load_index()
    problems = []

    if data.get("schema_version") != EXPECTED_SCHEMA:
        problems.append(f"schema_version должен быть {EXPECTED_SCHEMA}")

    records = data.get("records")
    if not isinstance(records, list):
        fail("records должен быть списком")

    seen_ids = set()
    for position, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            problems.append(f"запись {position}: должна быть объектом")
            continue
        validate_record(record, position, seen_ids, problems)

    declared_count = data.get("records_count")
    if declared_count != len(records):
        problems.append(f"records_count={declared_count}, фактически {len(records)}")

    if problems:
        print("Проверка knowledge-index.json: найдены ошибки.\n")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)

    print(f"Проверка knowledge-index.json завершена: {len(records)} записей, ошибок нет.")


if __name__ == "__main__":
    main()
