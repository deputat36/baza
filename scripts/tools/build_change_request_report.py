"""
Отчёт по очереди предложений и исправлений.

Скрипт проверяет рабочую очередь заявок на изменение и создаёт:
- build/change-request-report.md
- build/change-request-report.csv
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

QUEUE_FILE = ROOT / "data" / "drafts" / "change-request-queue.csv"
STATUSES_FILE = ROOT / "data" / "dictionaries" / "change-request-statuses.csv"
AUDIENCES_FILE = ROOT / "data" / "dictionaries" / "deal-audiences.csv"
REPORT_MD = BUILD_DIR / "change-request-report.md"
REPORT_CSV = BUILD_DIR / "change-request-report.csv"

REQUIRED_QUEUE_COLUMNS = [
    "ID", "Дата", "Автор", "Роль", "Тип изменения", "Раздел", "Что изменить",
    "Почему важно", "Приоритет", "Статус", "Ответственный"
]
REQUIRED_STATUS_COLUMNS = ["ID", "Статус", "Смысл", "Финальное состояние"]
VALID_PRIORITIES = {"1", "2", "3", "4", "5"}


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def read_csv(path: Path, required_columns: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Файл не найден: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = [column for column in required_columns if column not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"В {path.relative_to(ROOT)} нет колонок: {', '.join(missing)}")
        return list(reader)


def load_statuses():
    statuses = {}
    problems = []
    for row_number, row in enumerate(read_csv(STATUSES_FILE, REQUIRED_STATUS_COLUMNS), start=2):
        status = clean(row.get("Статус"))
        if not status:
            problems.append(f"change-request-statuses строка {row_number}: пустой статус")
            continue
        if status in statuses:
            problems.append(f"change-request-statuses строка {row_number}: дубль статуса {status}")
        statuses[status] = {
            "meaning": clean(row.get("Смысл")),
            "final": clean(row.get("Финальное состояние")).lower(),
        }
    return statuses, problems


def load_roles():
    roles = {""}
    if not AUDIENCES_FILE.exists():
        return roles
    for row in read_csv(AUDIENCES_FILE, ["Аудитория"]):
        roles.add(clean(row.get("Аудитория")))
    return roles


def build_rows(statuses, roles):
    rows = []
    problems = []
    seen_ids = set()

    for row_number, row in enumerate(read_csv(QUEUE_FILE, REQUIRED_QUEUE_COLUMNS), start=2):
        item_id = clean(row.get("ID"))
        role = clean(row.get("Роль"))
        change_type = clean(row.get("Тип изменения"))
        section = clean(row.get("Раздел"))
        description = clean(row.get("Что изменить"))
        reason = clean(row.get("Почему важно"))
        priority = clean(row.get("Приоритет"))
        status = clean(row.get("Статус"))
        owner = clean(row.get("Ответственный"))

        if not item_id:
            problems.append(f"строка {row_number}: пустой ID")
        elif item_id in seen_ids:
            problems.append(f"{item_id}: дубль ID")
        seen_ids.add(item_id)

        for field_name, value in [
            ("Тип изменения", change_type),
            ("Раздел", section),
            ("Что изменить", description),
            ("Почему важно", reason),
            ("Приоритет", priority),
            ("Статус", status),
            ("Ответственный", owner),
        ]:
            if not value:
                problems.append(f"{item_id}: пустое поле {field_name}")

        if role not in roles:
            problems.append(f"{item_id}: роль не найдена в deal-audiences.csv: {role}")
        if priority not in VALID_PRIORITIES:
            problems.append(f"{item_id}: приоритет должен быть от 1 до 5")
        if status not in statuses:
            problems.append(f"{item_id}: неизвестный статус {status}")

        final_state = statuses.get(status, {}).get("final", "")
        action_state = "CLOSED" if final_state == "yes" else "OPEN"

        rows.append({
            "id": item_id,
            "date": clean(row.get("Дата")),
            "author": clean(row.get("Автор")),
            "role": role,
            "change_type": change_type,
            "section": section,
            "related_id": clean(row.get("Связанная запись")),
            "description": description,
            "reason": reason,
            "source": clean(row.get("Источник")),
            "priority": priority,
            "status": status,
            "action_state": action_state,
            "owner": owner,
            "decision_date": clean(row.get("Дата решения")),
            "comment": clean(row.get("Комментарий")),
        })

    return rows, problems


def write_outputs(rows, problems):
    status_counts = {}
    owner_counts = {}
    open_rows = []
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
        owner_counts[row["owner"]] = owner_counts.get(row["owner"], 0) + 1
        if row["action_state"] == "OPEN":
            open_rows.append(row)

    open_rows.sort(key=lambda item: (-(int(item["priority"]) if item["priority"].isdigit() else 0), item["id"]))

    lines = [
        "# Отчёт по очереди предложений и исправлений",
        "",
        "## Сводка",
        "",
        f"- Всего заявок: {len(rows)}",
        f"- Открытых заявок: {len(open_rows)}",
        f"- Технических ошибок: {len(problems)}",
        "",
        "## По статусам",
        "",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## По ответственным", ""])
    for owner, count in sorted(owner_counts.items()):
        lines.append(f"- {owner}: {count}")

    lines.extend(["", "## Технические ошибки", ""])
    if problems:
        lines.extend(f"- {problem}" for problem in problems)
    else:
        lines.append("Ошибок структуры не найдено.")

    lines.extend([
        "",
        "## Открытые заявки",
        "",
        "| ID | Приоритет | Статус | Ответственный | Раздел | Что изменить |",
        "|---|---:|---|---|---|---|",
    ])
    for row in open_rows:
        lines.append(
            f"| {row['id']} | {row['priority']} | {row['status']} | {row['owner']} | {row['section']} | {row['description']} |"
        )

    BUILD_DIR.mkdir(exist_ok=True)
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "id", "date", "author", "role", "change_type", "section", "related_id",
            "description", "reason", "source", "priority", "status", "action_state",
            "owner", "decision_date", "comment"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    statuses, status_problems = load_statuses()
    rows, queue_problems = build_rows(statuses, load_roles())
    problems = status_problems + queue_problems
    write_outputs(rows, problems)

    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")

    if problems:
        print("\nНайдены технические ошибки очереди изменений:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
