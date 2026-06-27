"""
Сборка отчета по владельцам разделов базы знаний.

Запуск из корня репозитория:
python scripts/tools/build_section_ownership_report.py
"""

from pathlib import Path
import csv
import sys
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
SOURCE_FILE = ROOT / "data" / "drafts" / "section-ownership-matrix.csv"
BUILD_DIR = ROOT / "build"
OUTPUT_MD = BUILD_DIR / "section-ownership-report.md"
OUTPUT_CSV = BUILD_DIR / "section-ownership-report.csv"

REQUIRED_COLUMNS = [
    "ID",
    "Раздел",
    "Владелец роли",
    "Замещающий",
    "Что контролирует",
    "Периодичность",
    "Источник отчета",
    "Критичность",
    "Статус",
]

VALID_CRITICALITY = {"Высокая", "Средняя", "Низкая"}
VALID_STATUS = {"DRAFT", "CHECK", "READY", "DONE"}


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def validate_rows(rows):
    problems = []
    if not rows:
        return ["Матрица ответственности пустая"]

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


def build_report(rows):
    owner_counts = Counter(row["Владелец роли"] for row in rows)
    backup_counts = Counter(row["Замещающий"] for row in rows)
    criticality_counts = Counter(row["Критичность"] for row in rows)
    status_counts = Counter(row["Статус"] for row in rows)

    by_owner = defaultdict(list)
    for row in rows:
        by_owner[row["Владелец роли"]].append(row)

    high_risk = [row for row in rows if row["Критичность"] == "Высокая" and row["Статус"].upper() != "READY"]

    lines = [
        "# Ответственные за разделы базы",
        "",
        "## Сводка",
        "",
        f"- Всего зон ответственности: {len(rows)}",
        f"- Высокая критичность не READY: {len(high_risk)}",
        "",
        "## По владельцам",
        "",
    ]

    for owner, count in owner_counts.items():
        lines.append(f"- {owner}: {count}")

    lines.extend(["", "## По замещающим", ""])
    for backup, count in backup_counts.items():
        lines.append(f"- {backup}: {count}")

    lines.extend(["", "## По критичности", ""])
    for criticality, count in criticality_counts.items():
        lines.append(f"- {criticality}: {count}")

    lines.extend(["", "## По статусам", ""])
    for status, count in status_counts.items():
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Зоны высокого риска", ""])
    if not high_risk:
        lines.append("Зон высокого риска без READY нет.")
    else:
        for row in high_risk:
            lines.append(
                f"- {row['ID']} | {row['Раздел']} | владелец: {row['Владелец роли']} | "
                f"периодичность: {row['Периодичность']} | источник: {row['Источник отчета']}"
            )

    lines.extend(["", "## Детально по владельцам", ""])
    for owner, owner_rows in by_owner.items():
        lines.append(f"### {owner}")
        lines.append("")
        for row in owner_rows:
            lines.append(
                f"- {row['ID']} | {row['Раздел']} | {row['Что контролирует']} | "
                f"{row['Периодичность']} | {row['Статус']} | источник: {row['Источник отчета']} ({artifact_state(row['Источник отчета'])})"
            )
        lines.append("")

    lines.extend([
        "## Правило эксплуатации",
        "",
        "У каждого критичного раздела должен быть владелец и замещающий. Если владелец не назначен в закрытой рабочей таблице, раздел нельзя считать готовым к офисному запуску.",
        "",
    ])

    return "\n".join(lines)


def write_csv(rows):
    fieldnames = [
        "ID",
        "Раздел",
        "Владелец роли",
        "Замещающий",
        "Что контролирует",
        "Периодичность",
        "Источник отчета",
        "Источник статус",
        "Критичность",
        "Статус",
        "Комментарий",
    ]

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            output_row = {field: row.get(field, "") for field in fieldnames}
            output_row["Источник статус"] = artifact_state(row.get("Источник отчета", ""))
            writer.writerow(output_row)


def main():
    rows = read_rows(SOURCE_FILE)
    problems = validate_rows(rows)

    if problems:
        print("Матрица ответственности содержит ошибки.\n")
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
