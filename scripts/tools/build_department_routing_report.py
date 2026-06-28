"""
Сборка отчета по маршрутизации в департаменты центрального офиса.

Отчет использует публично безопасный черновик без реальных ФИО,
телефонов и внутренних каналов связи.

Запуск из корня репозитория:
python scripts/tools/build_department_routing_report.py
"""

from pathlib import Path
import csv
from collections import Counter

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

SOURCE_FILE = ROOT / "data" / "drafts" / "central-office-routing.csv"
OUTPUT_MD = BUILD_DIR / "department-routing-report.md"
OUTPUT_CSV = BUILD_DIR / "department-routing-report.csv"

FIELDNAMES = [
    "id",
    "direction",
    "when_to_use",
    "recipient_role",
    "what_to_prepare",
    "private_storage",
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
        "direction": row.get("Направление", "").strip(),
        "when_to_use": row.get("Когда обращаться", "").strip(),
        "recipient_role": row.get("Роль получателя", "").strip(),
        "what_to_prepare": row.get("Что подготовить", "").strip(),
        "private_storage": row.get("Где хранить реальные контакты", "").strip(),
        "priority": row.get("Критичность", "").strip(),
        "status": row.get("Статус", "").strip(),
        "comment": row.get("Комментарий", "").strip(),
    }


def build_rows():
    return [normalize_row(row) for row in read_rows()]


def build_markdown(rows):
    priorities = Counter(row["priority"] or "Не указана" for row in rows)
    statuses = Counter(row["status"] or "Не указан" for row in rows)
    need_private_fill = [row for row in rows if row["status"] != "READY"]

    lines = [
        "# Маршрутизация в департаменты центрального офиса",
        "",
        "## Назначение",
        "",
        "Отчет показывает, в какой департамент или к какому типу куратора направлять вопросы менеджеру офиса Борисоглебска.",
        "Реальные ФИО, телефоны, почты и внутренние каналы связи должны храниться только в закрытой Google Таблице.",
        "",
        "## Сводка",
        "",
        f"- Всего направлений: {len(rows)}",
        f"- Требуют заполнения в закрытой таблице: {len(need_private_fill)}",
        "",
        "## По критичности",
        "",
    ]

    if priorities:
        for priority, count in sorted(priorities.items()):
            lines.append(f"- {priority}: {count}")
    else:
        lines.append("- Нет данных")

    lines.extend(["", "## По статусам", ""])
    if statuses:
        for status, count in sorted(statuses.items()):
            lines.append(f"- {status}: {count}")
    else:
        lines.append("- Нет данных")

    lines.extend([
        "",
        "## Маршруты",
        "",
        "| ID | Направление | Когда обращаться | Роль получателя | Что подготовить | Где хранить реальные контакты | Критичность | Статус |",
        "|---|---|---|---|---|---|---|---|",
    ])

    if not rows:
        lines.append("| - | - | - | - | - | - | - | - |")
    else:
        for row in rows:
            lines.append(
                f"| {row['id']} | {row['direction']} | {row['when_to_use']} | {row['recipient_role']} | {row['what_to_prepare']} | {row['private_storage']} | {row['priority']} | {row['status']} |"
            )

    lines.extend([
        "",
        "## Что заполнить в закрытой таблице",
        "",
        "- ФИО куратора или представителя департамента.",
        "- Рабочий канал связи.",
        "- Правила эскалации.",
        "- Замещающий контакт.",
        "- Ограничения по передаче документов и персональных данных.",
        "",
        "## Ограничение",
        "",
        "Этот отчет является структурой маршрутизации. Он не содержит и не должен содержать реальные внутренние контакты в публичном репозитории.",
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
