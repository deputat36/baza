"""
Сборка отчета по чек-листу запуска базы в офисе.

Запуск из корня репозитория:
python scripts/tools/build_office_launch_checklist_report.py
"""

from pathlib import Path
import csv
import sys
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
SOURCE_FILE = ROOT / "data" / "drafts" / "office-launch-checklist.csv"
BUILD_DIR = ROOT / "build"
OUTPUT_MD = BUILD_DIR / "office-launch-checklist-report.md"
OUTPUT_CSV = BUILD_DIR / "office-launch-checklist-report.csv"

REQUIRED_COLUMNS = [
    "ID",
    "Этап",
    "Задача",
    "Ответственный",
    "Артефакт",
    "Критичность",
    "Статус",
    "Блокирует запуск",
]

VALID_CRITICALITY = {"Высокая", "Средняя", "Низкая"}
VALID_BLOCKER = {"yes", "no"}
FINAL_STATUSES = {"DONE", "READY", "APPLIED", "SKIP"}


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def check_columns(rows):
    if not rows:
        return ["Чек-лист запуска пустой"]

    missing = [column for column in REQUIRED_COLUMNS if column not in rows[0]]
    if missing:
        return [f"Нет обязательных колонок: {', '.join(missing)}"]

    return []


def validate_rows(rows):
    problems = []
    seen_ids = set()

    for row_number, row in enumerate(rows, start=2):
        item_id = row.get("ID", "").strip()
        if not item_id:
            problems.append(f"Строка {row_number}: нет ID")
        elif item_id in seen_ids:
            problems.append(f"Строка {row_number}: дубль ID {item_id}")
        else:
            seen_ids.add(item_id)

        for column in REQUIRED_COLUMNS:
            if not row.get(column, "").strip():
                problems.append(f"Строка {row_number}: не заполнено поле {column}")

        criticality = row.get("Критичность", "").strip()
        if criticality and criticality not in VALID_CRITICALITY:
            problems.append(f"Строка {row_number}: неизвестная критичность {criticality}")

        blocker = row.get("Блокирует запуск", "").strip().lower()
        if blocker and blocker not in VALID_BLOCKER:
            problems.append(f"Строка {row_number}: Блокирует запуск должно быть yes или no")

    return problems


def artifact_state(path_text: str) -> str:
    path_text = path_text.strip()
    if not path_text:
        return "не указан"

    path = ROOT / path_text
    if path.exists():
        return "есть"

    if path_text.startswith("build/"):
        return "будет собран"

    return "не найден"


def normalize_status(status: str) -> str:
    return status.strip().upper()


def is_open(row) -> bool:
    return normalize_status(row.get("Статус", "")) not in FINAL_STATUSES


def is_blocker(row) -> bool:
    return row.get("Блокирует запуск", "").strip().lower() == "yes"


def build_report(rows):
    stage_counts = Counter(row["Этап"] for row in rows)
    owner_counts = Counter(row["Ответственный"] for row in rows)
    criticality_counts = Counter(row["Критичность"] for row in rows)
    blockers = [row for row in rows if is_blocker(row)]
    open_blockers = [row for row in blockers if is_open(row)]

    by_stage = defaultdict(list)
    for row in rows:
        by_stage[row["Этап"]].append(row)

    lines = [
        "# Чек-лист запуска базы в офисе",
        "",
        "## Сводка",
        "",
        f"- Всего задач: {len(rows)}",
        f"- Блокируют запуск: {len(blockers)}",
        f"- Открытых блокирующих задач: {len(open_blockers)}",
        "",
        "## По этапам",
        "",
    ]

    for stage, count in stage_counts.items():
        lines.append(f"- {stage}: {count}")

    lines.extend(["", "## По ответственным", ""])
    for owner, count in owner_counts.items():
        lines.append(f"- {owner}: {count}")

    lines.extend(["", "## По критичности", ""])
    for criticality, count in criticality_counts.items():
        lines.append(f"- {criticality}: {count}")

    lines.extend(["", "## Открытые блокирующие задачи", ""])
    if not open_blockers:
        lines.append("Открытых блокирующих задач нет.")
    else:
        for row in open_blockers:
            lines.append(
                f"- {row['ID']} | {row['Этап']} | {row['Задача']} | "
                f"ответственный: {row['Ответственный']} | артефакт: {row['Артефакт']}"
            )

    lines.extend(["", "## Детальный список", ""])
    for stage, stage_rows in by_stage.items():
        lines.append(f"### {stage}")
        lines.append("")
        for row in stage_rows:
            lines.append(
                f"- {row['ID']} | {row['Задача']} | {row['Критичность']} | "
                f"{row['Статус']} | артефакт: {row['Артефакт']} ({artifact_state(row['Артефакт'])})"
            )
        lines.append("")

    lines.extend([
        "## Правило использования",
        "",
        "Запускать офисную версию можно только после ручного закрытия всех задач, где `Блокирует запуск = yes`.",
        "Реальные внутренние контакты и рабочие комментарии нужно вносить только в закрытую Google Таблицу.",
        "",
    ])

    return "\n".join(lines)


def write_csv(rows):
    fieldnames = [
        "ID",
        "Этап",
        "Задача",
        "Ответственный",
        "Артефакт",
        "Критичность",
        "Статус",
        "Блокирует запуск",
        "Артефакт статус",
        "Комментарий",
    ]

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            output_row = {field: row.get(field, "") for field in fieldnames}
            output_row["Артефакт статус"] = artifact_state(row.get("Артефакт", ""))
            writer.writerow(output_row)


def main():
    rows = read_rows(SOURCE_FILE)
    problems = check_columns(rows) + validate_rows(rows)

    if problems:
        print("Чек-лист запуска содержит ошибки.\n")
        for problem in problems:
            print(f"- {problem}")
        sys.exit(1)

    BUILD_DIR.mkdir(exist_ok=True)
    OUTPUT_MD.write_text(build_report(rows), encoding="utf-8")
    write_csv(rows)

    print(f"Готово: {OUTPUT_MD.relative_to(ROOT)}")
    print(f"Готово: {OUTPUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
