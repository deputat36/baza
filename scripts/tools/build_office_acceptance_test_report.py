"""
Сборка отчета по приемочным сценариям офиса.

Запуск из корня репозитория:
python scripts/tools/build_office_acceptance_test_report.py
"""

from pathlib import Path
import csv
import sys
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
SOURCE_FILE = ROOT / "data" / "drafts" / "office-acceptance-tests.csv"
BUILD_DIR = ROOT / "build"
OUTPUT_MD = BUILD_DIR / "office-acceptance-test-report.md"
OUTPUT_CSV = BUILD_DIR / "office-acceptance-test-report.csv"

REQUIRED_COLUMNS = [
    "ID",
    "Роль",
    "Сценарий",
    "Входные данные",
    "Ожидаемый результат",
    "Артефакт",
    "Критичность",
    "Статус",
    "Блокирует запуск",
]

VALID_CRITICALITY = {"Высокая", "Средняя", "Низкая"}
VALID_STATUS = {"DRAFT", "CHECK", "READY", "DONE", "FAILED", "SKIP"}
VALID_BLOCKER = {"yes", "no"}
FINAL_STATUSES = {"READY", "DONE", "SKIP"}


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def validate_rows(rows):
    problems = []
    if not rows:
        return ["Список приемочных сценариев пустой"]

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in rows[0]]
    if missing_columns:
        return [f"Нет обязательных колонок: {', '.join(missing_columns)}"]

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

        status = row.get("Статус", "").strip().upper()
        if status and status not in VALID_STATUS:
            problems.append(f"Строка {row_number}: неизвестный статус {status}")

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


def is_blocker(row) -> bool:
    return row.get("Блокирует запуск", "").strip().lower() == "yes"


def is_open(row) -> bool:
    return row.get("Статус", "").strip().upper() not in FINAL_STATUSES


def build_report(rows):
    role_counts = Counter(row["Роль"] for row in rows)
    criticality_counts = Counter(row["Критичность"] for row in rows)
    status_counts = Counter(row["Статус"] for row in rows)
    blockers = [row for row in rows if is_blocker(row)]
    open_blockers = [row for row in blockers if is_open(row)]

    by_role = defaultdict(list)
    for row in rows:
        by_role[row["Роль"]].append(row)

    lines = [
        "# Приемочные сценарии офиса",
        "",
        "## Сводка",
        "",
        f"- Всего сценариев: {len(rows)}",
        f"- Блокируют запуск: {len(blockers)}",
        f"- Открытых блокирующих сценариев: {len(open_blockers)}",
        "",
        "## По ролям",
        "",
    ]

    for role, count in role_counts.items():
        lines.append(f"- {role}: {count}")

    lines.extend(["", "## По критичности", ""])
    for criticality, count in criticality_counts.items():
        lines.append(f"- {criticality}: {count}")

    lines.extend(["", "## По статусам", ""])
    for status, count in status_counts.items():
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Открытые блокирующие сценарии", ""])
    if not open_blockers:
        lines.append("Открытых блокирующих сценариев нет.")
    else:
        for row in open_blockers:
            lines.append(
                f"- {row['ID']} | {row['Роль']} | {row['Сценарий']} | "
                f"ожидаемый результат: {row['Ожидаемый результат']}"
            )

    lines.extend(["", "## Детально по ролям", ""])
    for role, role_rows in by_role.items():
        lines.append(f"### {role}")
        lines.append("")
        for row in role_rows:
            lines.append(
                f"- {row['ID']} | {row['Сценарий']} | вход: {row['Входные данные']} | "
                f"результат: {row['Ожидаемый результат']} | {row['Статус']} | "
                f"артефакт: {row['Артефакт']} ({artifact_state(row['Артефакт'])})"
            )
        lines.append("")

    lines.extend([
        "## Правило приемки",
        "",
        "Офисный запуск нельзя считать готовым, пока все сценарии с `Блокирует запуск = yes` не пройдены вручную и не переведены в `READY` или `DONE` в закрытой рабочей таблице.",
        "",
    ])

    return "\n".join(lines)


def write_csv(rows):
    fieldnames = [
        "ID",
        "Роль",
        "Сценарий",
        "Входные данные",
        "Ожидаемый результат",
        "Артефакт",
        "Артефакт статус",
        "Критичность",
        "Статус",
        "Блокирует запуск",
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
    problems = validate_rows(rows)

    if problems:
        print("Приемочные сценарии содержат ошибки.\n")
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
