"""
Сборка отчета по схеме закрытого реестра контактов.

Отчет описывает, какие поля нужно вести в закрытой Google Таблице
для кураторов, департаментов, городских служб и подрядчиков.

Запуск из корня репозитория:
python scripts/tools/build_private_contact_schema_report.py
"""

from pathlib import Path
import csv
from collections import Counter

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

SOURCE_FILE = ROOT / "data" / "drafts" / "private-contact-registry-schema.csv"
OUTPUT_MD = BUILD_DIR / "private-contact-schema-report.md"
OUTPUT_CSV = BUILD_DIR / "private-contact-schema-report.csv"

FIELDNAMES = [
    "id",
    "contact_group",
    "field_name",
    "required",
    "audience",
    "example",
    "public_allowed",
    "comment",
]


def read_rows():
    if not SOURCE_FILE.exists():
        return []
    with SOURCE_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def normalize_row(row):
    return {
        "id": row.get("ID", "").strip(),
        "contact_group": row.get("Группа контактов", "").strip(),
        "field_name": row.get("Поле закрытой таблицы", "").strip(),
        "required": row.get("Обязательность", "").strip(),
        "audience": row.get("Для кого", "").strip(),
        "example": row.get("Пример значения", "").strip(),
        "public_allowed": row.get("Можно хранить публично", "").strip(),
        "comment": row.get("Комментарий", "").strip(),
    }


def build_rows():
    return [normalize_row(row) for row in read_rows()]


def build_markdown(rows):
    by_group = Counter(row["contact_group"] or "Не указана" for row in rows)
    by_required = Counter(row["required"] or "Не указана" for row in rows)
    private_only = [row for row in rows if row["public_allowed"].lower() == "нет"]

    lines = [
        "# Схема закрытого реестра контактов",
        "",
        "## Назначение",
        "",
        "Отчет описывает поля, которые нужно вести в закрытой Google Таблице для кураторов центрального офиса, городских служб, подрядчиков, нотариусов и кадастровых инженеров.",
        "Публичный репозиторий хранит только схему, а не реальные контакты.",
        "",
        "## Сводка",
        "",
        f"- Всего полей схемы: {len(rows)}",
        f"- Полей только для закрытого контура: {len(private_only)}",
        "",
        "## По группам контактов",
        "",
    ]

    if by_group:
        for group, count in sorted(by_group.items()):
            lines.append(f"- {group}: {count}")
    else:
        lines.append("- Нет данных")

    lines.extend(["", "## По обязательности", ""])
    if by_required:
        for required, count in sorted(by_required.items()):
            lines.append(f"- {required}: {count}")
    else:
        lines.append("- Нет данных")

    lines.extend([
        "",
        "## Поля схемы",
        "",
        "| ID | Группа | Поле | Обязательность | Для кого | Можно публично | Комментарий |",
        "|---|---|---|---|---|---|---|",
    ])

    if not rows:
        lines.append("| - | - | - | - | - | - | - |")
    else:
        for row in rows:
            lines.append(
                f"| {row['id']} | {row['contact_group']} | {row['field_name']} | {row['required']} | {row['audience']} | {row['public_allowed']} | {row['comment']} |"
            )

    lines.extend([
        "",
        "## Правило безопасности",
        "",
        "Если поле содержит ФИО, телефон, почту, мессенджер, внутренний канал, комментарий по человеку или закрытый источник, оно заполняется только в закрытой Google Таблице.",
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
    rows = build_rows()
    OUTPUT_MD.write_text(build_markdown(rows), encoding="utf-8")
    write_csv(rows)
    print(f"Готово: {OUTPUT_MD.relative_to(ROOT)}")
    print(f"Готово: {OUTPUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
