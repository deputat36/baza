"""
Генератор правил подсказок для будущей карточки сделки.

Правила не подключают базу к Навигатору сделок. Они создают read-only
контракт, по которому будущий интерфейс сможет понять, какие записи базы
знаний показывать при определённых признаках сделки.

Запуск:
python scripts/tools/build_knowledge_index.py
python scripts/tools/build_deal_hint_rules.py
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

RULES_FILE = ROOT / "data" / "drafts" / "deal-hint-rules.csv"
KNOWLEDGE_INDEX_FILE = BUILD_DIR / "knowledge-index.json"
OUTPUT_JSON = BUILD_DIR / "deal-hint-rules.json"
REPORT_MD = BUILD_DIR / "deal-hint-rules-report.md"
REPORT_CSV = BUILD_DIR / "deal-hint-rules-report.csv"
SCHEMA_VERSION = "deal-hint-rules-v1"

REQUIRED_COLUMNS = [
    "ID",
    "Сигнал сделки",
    "Значение",
    "Условие",
    "Связанные ID",
    "Заголовок подсказки",
    "Кому показывать",
    "Приоритет",
    "Статус",
]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def split_list(value: Any) -> list[str]:
    text = clean(value)
    if not text:
        return []
    return [part.strip() for part in text.replace(",", ";").split(";") if part.strip()]


def load_knowledge_ids() -> set[str]:
    if not KNOWLEDGE_INDEX_FILE.exists():
        raise SystemExit(f"Сначала соберите {KNOWLEDGE_INDEX_FILE.relative_to(ROOT)}")
    data = json.loads(KNOWLEDGE_INDEX_FILE.read_text(encoding="utf-8"))
    return {clean(record.get("id")) for record in data.get("records", []) if clean(record.get("id"))}


def read_rules():
    if not RULES_FILE.exists():
        raise SystemExit(f"Файл правил не найден: {RULES_FILE.relative_to(ROOT)}")
    with RULES_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"В deal-hint-rules.csv нет колонок: {', '.join(missing)}")
        return list(reader)


def normalize_rule(row: dict[str, str], row_number: int):
    return {
        "id": clean(row.get("ID")),
        "signal": clean(row.get("Сигнал сделки")),
        "value": clean(row.get("Значение")),
        "condition": clean(row.get("Условие")),
        "knowledge_ids": split_list(row.get("Связанные ID")),
        "title": clean(row.get("Заголовок подсказки")),
        "audience": split_list(row.get("Кому показывать")),
        "priority": clean(row.get("Приоритет")),
        "status": clean(row.get("Статус")),
        "comment": clean(row.get("Комментарий")),
        "source": RULES_FILE.relative_to(ROOT).as_posix(),
        "row_number": row_number,
    }


def validate_rules(rules, knowledge_ids):
    problems = []
    seen = set()
    for rule in rules:
        rule_id = rule["id"]
        if not rule_id:
            problems.append(f"строка {rule['row_number']}: пустой ID")
            continue
        if rule_id in seen:
            problems.append(f"{rule_id}: дубль ID правила")
        seen.add(rule_id)

        for field in ["signal", "value", "condition", "title", "priority", "status"]:
            if not rule.get(field):
                problems.append(f"{rule_id}: пустое поле {field}")

        if not rule.get("knowledge_ids"):
            problems.append(f"{rule_id}: нет связанных ID")

        for target_id in rule.get("knowledge_ids", []):
            if target_id not in knowledge_ids:
                problems.append(f"{rule_id}: связанный ID не найден в knowledge-index.json: {target_id}")
    return problems


def write_outputs(rules, problems):
    data = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": RULES_FILE.relative_to(ROOT).as_posix(),
        "purpose": "Read-only draft rules for future deal-card knowledge hints.",
        "rules_count": len(rules),
        "problems_count": len(problems),
        "rules": rules,
    }
    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Отчёт по правилам подсказок сделки",
        "",
        "## Сводка",
        "",
        f"- Правил: {len(rules)}",
        f"- Ошибок: {len(problems)}",
        "",
        "## Ошибки",
        "",
    ]
    if problems:
        lines.extend(f"- {problem}" for problem in problems)
    else:
        lines.append("Ошибок не найдено.")

    lines.extend(["", "## Правила", "", "| ID | Сигнал | Значение | Связанные ID | Статус |", "|---|---|---|---|---|"])
    for rule in rules:
        lines.append(
            f"| {rule['id']} | {rule['signal']} | {rule['value']} | {'; '.join(rule['knowledge_ids'])} | {rule['status']} |"
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "signal", "value", "title", "knowledge_ids", "priority", "status", "row_number"])
        for rule in rules:
            writer.writerow([
                rule["id"],
                rule["signal"],
                rule["value"],
                rule["title"],
                "; ".join(rule["knowledge_ids"]),
                rule["priority"],
                rule["status"],
                rule["row_number"],
            ])


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    knowledge_ids = load_knowledge_ids()
    rules = [normalize_rule(row, row_number) for row_number, row in enumerate(read_rules(), start=2)]
    problems = validate_rules(rules, knowledge_ids)
    write_outputs(rules, problems)

    print(f"Готово: {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")

    if problems:
        print("\nНайдены ошибки правил:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
