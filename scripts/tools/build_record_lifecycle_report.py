"""
Сборка отчета по жизненному циклу записей базы знаний.

Отчет задает правила перехода записей между статусами: DRAFT, CHECK,
READY, STALE, PRIVATE_ONLY, BLOCKED и ARCHIVE.

Запуск из корня репозитория:
python scripts/tools/build_record_lifecycle_report.py
"""

from pathlib import Path
import csv

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

SOURCE_FILE = ROOT / "data" / "drafts" / "record-lifecycle.csv"
OUTPUT_MD = BUILD_DIR / "record-lifecycle-report.md"
OUTPUT_CSV = BUILD_DIR / "record-lifecycle-report.csv"

FIELDNAMES = [
    "ID",
    "Статус",
    "Когда ставится",
    "Кто может поставить",
    "Что нужно для перехода дальше",
    "Можно показывать сотрудникам",
    "Можно использовать в работе",
    "Следующий статус",
    "Комментарий",
]


def read_rows():
    with SOURCE_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def count_by(rows, field):
    counts = {}
    for row in rows:
        value = row.get(field, "").strip() or "не указано"
        counts[value] = counts.get(value, 0) + 1
    return counts


def build_markdown(rows):
    usable = count_by(rows, "Можно использовать в работе")
    visible = count_by(rows, "Можно показывать сотрудникам")
    blocked = [row for row in rows if row.get("Можно использовать в работе") != "yes"]

    lines = [
        "# Отчет по жизненному циклу записей",
        "",
        "## Назначение",
        "",
        "Отчет задает правила, по которым запись переходит от черновика к проверенной рабочей информации, закрытому контуру или архиву.",
        "",
        "## Сводка",
        "",
        f"- Всего статусов: {len(rows)}",
        f"- Нельзя использовать в работе без изменения статуса: {len(blocked)}",
        "",
        "## Использование в работе",
        "",
    ]

    for value, count in sorted(usable.items()):
        lines.append(f"- {value}: {count}")

    lines.extend(["", "## Видимость сотрудникам", ""])
    for value, count in sorted(visible.items()):
        lines.append(f"- {value}: {count}")

    lines.extend([
        "",
        "## Статусы",
        "",
        "| ID | Статус | Когда ставится | Кто ставит | Условие перехода | Видно сотрудникам | Использовать в работе | Следующий статус |",
        "|---|---|---|---|---|---|---|---|",
    ])

    for row in rows:
        lines.append(
            "| {id} | {status} | {when} | {owner} | {condition} | {visible} | {usable} | {next_status} |".format(
                id=row.get("ID", ""),
                status=row.get("Статус", ""),
                when=row.get("Когда ставится", ""),
                owner=row.get("Кто может поставить", ""),
                condition=row.get("Что нужно для перехода дальше", ""),
                visible=row.get("Можно показывать сотрудникам", ""),
                usable=row.get("Можно использовать в работе", ""),
                next_status=row.get("Следующий статус", ""),
            )
        )

    lines.extend([
        "",
        "## Рабочее правило",
        "",
        "Рабочей считается только запись в статусе `READY` и с непросроченной датой следующей проверки.",
        "Записи `DRAFT`, `CHECK`, `STALE`, `BLOCKED`, `PRIVATE_ONLY` и `ARCHIVE` не должны использоваться как подтвержденная рабочая информация.",
        "",
    ])

    return "\n".join(lines)


def write_csv(rows):
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    rows = read_rows()
    OUTPUT_MD.write_text(build_markdown(rows), encoding="utf-8")
    write_csv(rows)
    print(f"Готово: {OUTPUT_MD.relative_to(ROOT)}")
    print(f"Готово: {OUTPUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
