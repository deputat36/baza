"""
Сборка отчета по проверке актуальности контактов.

Отчет описывает, какие группы контактов нужно регулярно проверять,
кто отвечает за проверку и где фиксировать результат.

Запуск из корня репозитория:
python scripts/tools/build_contact_verification_report.py
"""

from pathlib import Path
import csv
from collections import Counter

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

SOURCE_FILE = ROOT / "data" / "drafts" / "contact-verification-workflow.csv"
OUTPUT_MD = BUILD_DIR / "contact-verification-report.md"
OUTPUT_CSV = BUILD_DIR / "contact-verification-report.csv"

FIELDNAMES = [
    "id",
    "contact_group",
    "what_to_check",
    "how_to_check",
    "cadence",
    "role",
    "result_artifact",
    "priority",
    "status",
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
        "what_to_check": row.get("Что проверять", "").strip(),
        "how_to_check": row.get("Как проверять", "").strip(),
        "cadence": row.get("Периодичность", "").strip(),
        "role": row.get("Роль", "").strip(),
        "result_artifact": row.get("Артефакт результата", "").strip(),
        "priority": row.get("Критичность", "").strip(),
        "status": row.get("Статус", "").strip(),
        "comment": row.get("Комментарий", "").strip(),
    }


def build_rows():
    return [normalize_row(row) for row in read_rows()]


def build_markdown(rows):
    by_cadence = Counter(row["cadence"] or "Не указана" for row in rows)
    by_role = Counter(row["role"] or "Не указана" for row in rows)
    high_priority = [row for row in rows if row["priority"] == "Высокая"]

    lines = [
        "# Проверка актуальности контактов",
        "",
        "## Назначение",
        "",
        "Отчет задает регулярный порядок проверки контактов для закрытой Google Таблицы: кураторы центрального офиса, городские службы, управляющие компании, нотариусы, кадастровые инженеры, оценщики, банки и подрядчики.",
        "Публичный репозиторий хранит только процесс проверки, а не реальные контакты.",
        "",
        "## Сводка",
        "",
        f"- Всего групп проверки: {len(rows)}",
        f"- Высокая критичность: {len(high_priority)}",
        "",
        "## По периодичности",
        "",
    ]

    if by_cadence:
        for cadence, count in sorted(by_cadence.items()):
            lines.append(f"- {cadence}: {count}")
    else:
        lines.append("- Нет данных")

    lines.extend(["", "## По ролям", ""])
    if by_role:
        for role, count in sorted(by_role.items()):
            lines.append(f"- {role}: {count}")
    else:
        lines.append("- Нет данных")

    lines.extend([
        "",
        "## Регламент проверки",
        "",
        "| ID | Группа | Что проверять | Как проверять | Периодичность | Роль | Где фиксировать | Критичность | Статус |",
        "|---|---|---|---|---|---|---|---|---|",
    ])

    if not rows:
        lines.append("| - | - | - | - | - | - | - | - | - |")
    else:
        for row in rows:
            lines.append(
                f"| {row['id']} | {row['contact_group']} | {row['what_to_check']} | {row['how_to_check']} | {row['cadence']} | {row['role']} | {row['result_artifact']} | {row['priority']} | {row['status']} |"
            )

    lines.extend([
        "",
        "## Правило фиксации",
        "",
        "Результат проверки фиксируется в закрытой Google Таблице: дата проверки, кто проверил, источник, следующий срок проверки и статус контакта.",
        "ФИО, телефоны, почты, мессенджеры, внутренние каналы, клиентские данные и комментарии по людям не публикуются в репозитории.",
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
