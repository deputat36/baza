"""
Сборка отчета по уровням доверия источников.

Отчет помогает отделять рабочие проверенные данные от черновиков,
закрытых контактов и записей которые требуют проверки.

Запуск из корня репозитория:
python scripts/tools/build_source_trust_report.py
"""

from pathlib import Path
import csv

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

SOURCE_FILE = ROOT / "data" / "drafts" / "source-trust-levels.csv"
OUTPUT_MD = BUILD_DIR / "source-trust-report.md"
OUTPUT_CSV = BUILD_DIR / "source-trust-report.csv"

FIELDNAMES = [
    "ID",
    "Уровень",
    "Где применяется",
    "Что означает",
    "Можно использовать без проверки",
    "Куда вносить реальные данные",
    "Период проверки",
    "Кто проверяет",
    "Статус",
    "Комментарий",
]


def read_rows():
    with SOURCE_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def grouped_counts(rows, key):
    counts = {}
    for row in rows:
        value = row.get(key, "").strip() or "не указано"
        counts[value] = counts.get(value, 0) + 1
    return counts


def build_markdown(rows):
    status_counts = grouped_counts(rows, "Статус")
    usable_counts = grouped_counts(rows, "Можно использовать без проверки")
    private_rows = [row for row in rows if row.get("Уровень") == "PRIVATE_ONLY"]
    check_rows = [row for row in rows if row.get("Можно использовать без проверки") == "no"]

    lines = [
        "# Отчет по уровням доверия источников",
        "",
        "## Назначение",
        "",
        "Отчет задает правила использования данных в базе знаний: что можно применять в работе сразу, что требует проверки и что должно храниться только в закрытой Google Таблице.",
        "",
        "## Сводка",
        "",
        f"- Всего уровней: {len(rows)}",
        f"- Требуют проверки или закрытого контура: {len(check_rows)}",
        f"- Только закрытый контур: {len(private_rows)}",
        "",
        "## По статусам",
        "",
    ]

    for status, count in sorted(status_counts.items()):
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Использование без проверки", ""])
    for value, count in sorted(usable_counts.items()):
        lines.append(f"- {value}: {count}")

    lines.extend([
        "",
        "## Правила",
        "",
        "| ID | Уровень | Где применяется | Использовать без проверки | Куда вносить реальные данные | Период проверки | Ответственный |",
        "|---|---|---|---|---|---|---|",
    ])

    for row in rows:
        lines.append(
            "| {id} | {level} | {area} | {usable} | {target} | {period} | {owner} |".format(
                id=row.get("ID", ""),
                level=row.get("Уровень", ""),
                area=row.get("Где применяется", ""),
                usable=row.get("Можно использовать без проверки", ""),
                target=row.get("Куда вносить реальные данные", ""),
                period=row.get("Период проверки", ""),
                owner=row.get("Кто проверяет", ""),
            )
        )

    lines.extend([
        "",
        "## Рабочее правило",
        "",
        "Если у записи уровень `CHECK_REQUIRED`, `DRAFT`, `PRIVATE_ONLY` или `ARCHIVE`, сотрудник не должен использовать ее как подтвержденную рабочую информацию без дополнительной проверки.",
        "Реальные телефоны, ФИО сотрудников, внутренние условия и клиентские данные фиксируются только в закрытой Google Таблице.",
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
