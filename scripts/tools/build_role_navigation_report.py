"""
Отчёт по навигации для ролей.

Скрипт проверяет карту навигации сотрудников и создаёт:
- build/role-navigation-report.md
- build/role-navigation-report.csv

Отсутствующие артефакты фиксируются как предупреждения в отчёте, но не ломают CI:
часть build-файлов появляется только после полной сборки.
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

NAVIGATION_FILE = ROOT / "data" / "drafts" / "role-navigation-map.csv"
AUDIENCES_FILE = ROOT / "data" / "dictionaries" / "deal-audiences.csv"
REPORT_MD = BUILD_DIR / "role-navigation-report.md"
REPORT_CSV = BUILD_DIR / "role-navigation-report.csv"

REQUIRED_COLUMNS = [
    "ID",
    "Аудитория",
    "Сценарий",
    "С чего начать",
    "Основные разделы",
    "Артефакты",
    "Следующее действие",
    "Приоритет",
    "Статус",
]
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


def load_audiences() -> set[str]:
    return {clean(row.get("Аудитория")) for row in read_csv(AUDIENCES_FILE, ["Аудитория"]) if clean(row.get("Аудитория"))}


def split_values(value: str) -> list[str]:
    return [part.strip() for part in clean(value).split(";") if part.strip()]


def artifact_state(path_value: str) -> str:
    states = []
    for item in split_values(path_value):
        path = ROOT / item
        states.append("yes" if path.exists() else "no")
    if not states:
        return "no_artifacts"
    if all(state == "yes" for state in states):
        return "all_exist"
    if any(state == "yes" for state in states):
        return "partial"
    return "missing_now"


def build_rows():
    audiences = load_audiences()
    rows = []
    problems = []
    seen_ids = set()

    for row_number, row in enumerate(read_csv(NAVIGATION_FILE, REQUIRED_COLUMNS), start=2):
        item_id = clean(row.get("ID"))
        audience = clean(row.get("Аудитория"))
        scenario = clean(row.get("Сценарий"))
        start_from = clean(row.get("С чего начать"))
        sections = clean(row.get("Основные разделы"))
        artifacts = clean(row.get("Артефакты"))
        next_action = clean(row.get("Следующее действие"))
        priority = clean(row.get("Приоритет"))
        status = clean(row.get("Статус"))
        comment = clean(row.get("Комментарий"))

        if not item_id:
            problems.append(f"строка {row_number}: пустой ID")
        elif item_id in seen_ids:
            problems.append(f"{item_id}: дубль ID")
        seen_ids.add(item_id)

        if audience not in audiences:
            problems.append(f"{item_id}: аудитория не найдена в deal-audiences.csv: {audience}")
        if priority not in VALID_PRIORITIES:
            problems.append(f"{item_id}: приоритет должен быть от 1 до 5")

        for field_name, value in [
            ("Сценарий", scenario),
            ("С чего начать", start_from),
            ("Основные разделы", sections),
            ("Артефакты", artifacts),
            ("Следующее действие", next_action),
            ("Статус", status),
        ]:
            if not value:
                problems.append(f"{item_id}: пустое поле {field_name}")

        rows.append({
            "id": item_id,
            "audience": audience,
            "scenario": scenario,
            "start_from": start_from,
            "sections": sections,
            "artifacts": artifacts,
            "artifact_state": artifact_state(artifacts),
            "next_action": next_action,
            "priority": priority,
            "status": status,
            "comment": comment,
        })

    return rows, problems


def write_outputs(rows: list[dict[str, str]], problems: list[str]):
    by_role: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_role.setdefault(row["audience"], []).append(row)

    lines = [
        "# Отчёт по навигации для ролей",
        "",
        "## Сводка",
        "",
        f"- Сценариев: {len(rows)}",
        f"- Ролей: {len(by_role)}",
        f"- Технических ошибок: {len(problems)}",
        "",
        "## Технические ошибки",
        "",
    ]
    if problems:
        lines.extend(f"- {problem}" for problem in problems)
    else:
        lines.append("Ошибок структуры не найдено.")

    lines.extend(["", "## По ролям", ""])
    for audience in sorted(by_role):
        lines.extend([f"### {audience}", ""])
        lines.append("| Приоритет | Сценарий | С чего начать | Следующее действие | Артефакты |")
        lines.append("|---:|---|---|---|---|")
        for row in sorted(by_role[audience], key=lambda item: (-int(item["priority"]), item["id"])):
            lines.append(
                f"| {row['priority']} | {row['scenario']} | {row['start_from']} | {row['next_action']} | {row['artifact_state']} |"
            )
        lines.append("")

    BUILD_DIR.mkdir(exist_ok=True)
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8-sig", newline="") as file:
        fieldnames = [
            "id", "audience", "scenario", "start_from", "sections", "artifacts",
            "artifact_state", "next_action", "priority", "status", "comment"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows, problems = build_rows()
    write_outputs(rows, problems)
    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")

    if problems:
        print("\nНайдены технические ошибки навигации по ролям:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
