"""
Отчёт актуальности данных.

Скрипт проверяет реестр актуальности и собирает отчёты:
- build/data-freshness-report.md
- build/data-freshness-report.csv

Просроченная дата проверки фиксируется в отчёте, но не ломает CI.
CI падает только при технических ошибках структуры.
"""

from __future__ import annotations

import csv
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

POLICIES_FILE = ROOT / "data" / "dictionaries" / "freshness-policies.csv"
REGISTER_FILE = ROOT / "data" / "drafts" / "data-freshness-register.csv"
REPORT_MD = BUILD_DIR / "data-freshness-report.md"
REPORT_CSV = BUILD_DIR / "data-freshness-report.csv"

REQUIRED_POLICY_COLUMNS = ["ID", "Политика", "Интервал дней", "Критичность", "Что проверять", "Статус"]
REQUIRED_REGISTER_COLUMNS = ["ID", "Объект", "Тип", "Путь", "Политика", "Последняя проверка", "Ответственный", "Статус"]


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


def parse_date(value: str):
    value = clean(value)
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return "INVALID"


def load_policies():
    policies = {}
    problems = []
    seen_ids = set()
    seen_names = set()

    for row_number, row in enumerate(read_csv(POLICIES_FILE, REQUIRED_POLICY_COLUMNS), start=2):
        policy_id = clean(row.get("ID"))
        name = clean(row.get("Политика"))
        interval_raw = clean(row.get("Интервал дней"))

        if not policy_id:
            problems.append(f"freshness-policies строка {row_number}: пустой ID")
        elif policy_id in seen_ids:
            problems.append(f"freshness-policies строка {row_number}: дубль ID {policy_id}")
        seen_ids.add(policy_id)

        if not name:
            problems.append(f"{policy_id}: пустая политика")
        elif name in seen_names:
            problems.append(f"{policy_id}: дубль политики {name}")
        seen_names.add(name)

        try:
            interval_days = int(interval_raw)
        except ValueError:
            interval_days = 0
            problems.append(f"{policy_id}: интервал должен быть числом")

        if interval_days <= 0:
            problems.append(f"{policy_id}: интервал должен быть больше нуля")

        policies[name] = {
            "id": policy_id,
            "name": name,
            "interval_days": interval_days,
            "criticality": clean(row.get("Критичность")),
            "check_scope": clean(row.get("Что проверять")),
            "status": clean(row.get("Статус")),
        }

    return policies, problems


def build_rows(policies):
    today = date.today()
    rows = []
    problems = []
    seen_ids = set()

    for row_number, row in enumerate(read_csv(REGISTER_FILE, REQUIRED_REGISTER_COLUMNS), start=2):
        item_id = clean(row.get("ID"))
        object_name = clean(row.get("Объект"))
        item_type = clean(row.get("Тип"))
        source_path = clean(row.get("Путь"))
        policy_name = clean(row.get("Политика"))
        last_checked_raw = clean(row.get("Последняя проверка"))
        owner = clean(row.get("Ответственный"))
        status = clean(row.get("Статус"))
        comment = clean(row.get("Комментарий"))

        if not item_id:
            problems.append(f"строка {row_number}: пустой ID")
        elif item_id in seen_ids:
            problems.append(f"{item_id}: дубль ID")
        seen_ids.add(item_id)

        for field_name, value in [
            ("Объект", object_name),
            ("Тип", item_type),
            ("Путь", source_path),
            ("Политика", policy_name),
            ("Ответственный", owner),
            ("Статус", status),
        ]:
            if not value:
                problems.append(f"{item_id}: пустое поле {field_name}")

        source_exists = "yes" if source_path and (ROOT / source_path).exists() else "no"
        if source_path and source_exists == "no":
            problems.append(f"{item_id}: путь не найден: {source_path}")

        policy = policies.get(policy_name)
        if not policy:
            problems.append(f"{item_id}: политика не найдена: {policy_name}")
            interval_days = 0
            criticality = ""
            check_scope = ""
        else:
            interval_days = policy["interval_days"]
            criticality = policy["criticality"]
            check_scope = policy["check_scope"]

        last_checked = parse_date(last_checked_raw)
        if last_checked == "INVALID":
            problems.append(f"{item_id}: дата должна быть в формате YYYY-MM-DD")
            last_checked_value = ""
            next_check = ""
            days_left = ""
            freshness_state = "INVALID_DATE"
        elif last_checked is None:
            last_checked_value = ""
            next_check = ""
            days_left = ""
            freshness_state = "NEVER_CHECKED"
        else:
            due_date = last_checked + timedelta(days=interval_days)
            days_delta = (due_date - today).days
            last_checked_value = last_checked.isoformat()
            next_check = due_date.isoformat()
            days_left = str(days_delta)
            if days_delta < 0:
                freshness_state = "OVERDUE"
            elif days_delta <= 14:
                freshness_state = "DUE_SOON"
            else:
                freshness_state = "OK"

        rows.append({
            "id": item_id,
            "object": object_name,
            "type": item_type,
            "path": source_path,
            "source_exists": source_exists,
            "policy": policy_name,
            "interval_days": str(interval_days or ""),
            "criticality": criticality,
            "check_scope": check_scope,
            "last_checked": last_checked_value,
            "next_check": next_check,
            "days_left": days_left,
            "freshness_state": freshness_state,
            "owner": owner,
            "status": status,
            "comment": comment,
        })

    return rows, problems


def write_outputs(rows, problems):
    state_counts = {}
    for row in rows:
        state_counts[row["freshness_state"]] = state_counts.get(row["freshness_state"], 0) + 1

    lines = [
        "# Отчёт актуальности данных",
        "",
        "## Сводка",
        "",
        f"- Объектов контроля: {len(rows)}",
        f"- Технических ошибок: {len(problems)}",
        "",
        "## Состояния",
        "",
    ]

    for state in ["OK", "DUE_SOON", "OVERDUE", "NEVER_CHECKED", "INVALID_DATE"]:
        lines.append(f"- {state}: {state_counts.get(state, 0)}")

    lines.extend(["", "## Технические ошибки", ""])
    if problems:
        lines.extend(f"- {problem}" for problem in problems)
    else:
        lines.append("Ошибок структуры не найдено.")

    lines.extend([
        "",
        "## Реестр",
        "",
        "| Объект | Политика | Последняя проверка | Следующая проверка | Состояние | Ответственный |",
        "|---|---|---|---|---|---|",
    ])
    for row in rows:
        lines.append(
            f"| {row['object']} | {row['policy']} | {row['last_checked'] or '-'} | {row['next_check'] or '-'} | {row['freshness_state']} | {row['owner']} |"
        )

    BUILD_DIR.mkdir(exist_ok=True)
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "id", "object", "type", "path", "source_exists", "policy", "interval_days",
            "criticality", "check_scope", "last_checked", "next_check", "days_left",
            "freshness_state", "owner", "status", "comment"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    policies, policy_problems = load_policies()
    rows, register_problems = build_rows(policies)
    problems = policy_problems + register_problems
    write_outputs(rows, problems)

    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")

    if problems:
        print("\nНайдены технические ошибки реестра актуальности:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
