"""
Отчёт по видимости данных будущей интеграции.

Показывает, какие источники можно держать в публичном репозитории,
а какие должны оставаться только в закрытой Google Таблице или приватной БД.

Запуск:
python scripts/tools/build_integration_data_visibility_report.py
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

VISIBILITY_FILE = ROOT / "data" / "dictionaries" / "integration-data-visibility.csv"
REPORT_MD = BUILD_DIR / "integration-data-visibility-report.md"
REPORT_CSV = BUILD_DIR / "integration-data-visibility-report.csv"

REQUIRED_COLUMNS = [
    "ID",
    "Область",
    "Путь",
    "Тип данных",
    "Где хранить",
    "Публично безопасно",
    "Причина",
    "Статус",
]

PUBLIC_STORAGE = "Публичный репозиторий"
PRIVATE_SAFE_VALUES = {"no", "нет", "false", "0"}
PUBLIC_SAFE_VALUES = {"yes", "да", "true", "1"}


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def read_rows() -> list[dict[str, str]]:
    if not VISIBILITY_FILE.exists():
        raise SystemExit(f"Файл видимости данных не найден: {VISIBILITY_FILE.relative_to(ROOT)}")

    with VISIBILITY_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"В integration-data-visibility.csv нет колонок: {', '.join(missing)}")
        return list(reader)


def normalize_public_flag(value: str) -> str:
    normalized = clean(value).lower()
    if normalized in PUBLIC_SAFE_VALUES:
        return "yes"
    if normalized in PRIVATE_SAFE_VALUES:
        return "no"
    return "unknown"


def build_report_rows(source_rows: list[dict[str, str]]):
    rows = []
    problems = []
    seen_ids = set()

    for row_number, row in enumerate(source_rows, start=2):
        item_id = clean(row.get("ID"))
        area = clean(row.get("Область"))
        path = clean(row.get("Путь"))
        data_type = clean(row.get("Тип данных"))
        storage = clean(row.get("Где хранить"))
        public_safe = normalize_public_flag(row.get("Публично безопасно", ""))
        reason = clean(row.get("Причина"))
        status = clean(row.get("Статус"))

        if not item_id:
            problems.append(f"строка {row_number}: пустой ID")
        elif item_id in seen_ids:
            problems.append(f"{item_id}: дубль ID")
        seen_ids.add(item_id)

        for field_name, value in [
            ("Область", area),
            ("Путь", path),
            ("Тип данных", data_type),
            ("Где хранить", storage),
            ("Причина", reason),
            ("Статус", status),
        ]:
            if not value:
                problems.append(f"{item_id}: пустое поле {field_name}")

        if public_safe == "unknown":
            problems.append(f"{item_id}: поле `Публично безопасно` должно быть yes/no")

        if storage == PUBLIC_STORAGE and public_safe == "no":
            problems.append(f"{item_id}: приватные данные нельзя хранить в публичном репозитории")

        if public_safe == "yes" and storage != PUBLIC_STORAGE:
            problems.append(f"{item_id}: публично безопасные данные указаны вне публичного репозитория, проверьте назначение")

        rows.append({
            "id": item_id,
            "area": area,
            "path": path,
            "data_type": data_type,
            "storage": storage,
            "public_safe": public_safe,
            "reason": reason,
            "status": status,
            "comment": clean(row.get("Комментарий")),
        })

    return rows, problems


def write_outputs(rows, problems):
    public_rows = [row for row in rows if row["public_safe"] == "yes"]
    private_rows = [row for row in rows if row["public_safe"] == "no"]

    lines = [
        "# Отчёт по видимости данных",
        "",
        "## Сводка",
        "",
        f"- Записей: {len(rows)}",
        f"- Публично безопасных: {len(public_rows)}",
        f"- Только закрытый контур: {len(private_rows)}",
        f"- Ошибок: {len(problems)}",
        "",
        "## Ошибки",
        "",
    ]
    if problems:
        lines.extend(f"- {problem}" for problem in problems)
    else:
        lines.append("Ошибок не найдено.")

    lines.extend([
        "",
        "## Карта видимости",
        "",
        "| ID | Область | Где хранить | Публично безопасно | Причина |",
        "|---|---|---|---|---|",
    ])
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['area']} | {row['storage']} | {row['public_safe']} | {row['reason']} |"
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = ["id", "area", "path", "data_type", "storage", "public_safe", "reason", "status", "comment"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    rows, problems = build_report_rows(read_rows())
    write_outputs(rows, problems)

    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")

    if problems:
        print("\nНайдены ошибки видимости данных:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
