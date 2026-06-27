"""
Отчёт по матрице доступа будущей интеграции.

Проверяет, что роли есть в словаре аудиторий, а области данных описаны
в карте видимости данных. Это подготовка к будущему приватному интерфейсу,
не подключение к Навигатору сделок.

Запуск:
python scripts/tools/build_integration_access_report.py
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

ACCESS_FILE = ROOT / "data" / "drafts" / "integration-access-matrix.csv"
AUDIENCES_FILE = ROOT / "data" / "dictionaries" / "deal-audiences.csv"
VISIBILITY_FILE = ROOT / "data" / "dictionaries" / "integration-data-visibility.csv"
REPORT_MD = BUILD_DIR / "integration-access-report.md"
REPORT_CSV = BUILD_DIR / "integration-access-report.csv"

REQUIRED_COLUMNS = [
    "ID",
    "Аудитория",
    "Область данных",
    "Доступ на чтение",
    "Доступ на изменение",
    "Где хранить",
    "Причина",
    "Статус",
]

ACCESS_VALUES = {"yes", "no", "limited"}


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Файл не найден: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def read_access_rows() -> list[dict[str, str]]:
    if not ACCESS_FILE.exists():
        raise SystemExit(f"Файл матрицы доступа не найден: {ACCESS_FILE.relative_to(ROOT)}")
    with ACCESS_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"В integration-access-matrix.csv нет колонок: {', '.join(missing)}")
        return list(reader)


def load_audiences() -> set[str]:
    return {clean(row.get("Аудитория")) for row in read_csv(AUDIENCES_FILE) if clean(row.get("Аудитория"))}


def load_visibility() -> dict[str, dict[str, str]]:
    visibility = {}
    for row in read_csv(VISIBILITY_FILE):
        area = clean(row.get("Область"))
        if area:
            visibility[area] = {key: clean(value) for key, value in row.items() if key}
    return visibility


def build_rows(access_rows, audiences, visibility):
    rows = []
    problems = []
    seen_ids = set()

    for row_number, row in enumerate(access_rows, start=2):
        item_id = clean(row.get("ID"))
        audience = clean(row.get("Аудитория"))
        area = clean(row.get("Область данных"))
        read_access = clean(row.get("Доступ на чтение")).lower()
        write_access = clean(row.get("Доступ на изменение")).lower()
        storage = clean(row.get("Где хранить"))
        reason = clean(row.get("Причина"))
        status = clean(row.get("Статус"))

        if not item_id:
            problems.append(f"строка {row_number}: пустой ID")
        elif item_id in seen_ids:
            problems.append(f"{item_id}: дубль ID")
        seen_ids.add(item_id)

        if audience not in audiences:
            problems.append(f"{item_id}: аудитория не найдена в deal-audiences.csv: {audience}")

        visibility_row = visibility.get(area)
        if not visibility_row:
            problems.append(f"{item_id}: область данных не найдена в integration-data-visibility.csv: {area}")
        else:
            expected_storage = clean(visibility_row.get("Где хранить"))
            public_safe = clean(visibility_row.get("Публично безопасно")).lower()
            if storage != expected_storage:
                problems.append(f"{item_id}: место хранения не совпадает с картой видимости: {storage} != {expected_storage}")
            if public_safe == "no" and read_access == "yes" and storage == "Публичный репозиторий":
                problems.append(f"{item_id}: приватная область не должна иметь полный публичный доступ")

        for field_name, value in [
            ("Аудитория", audience),
            ("Область данных", area),
            ("Где хранить", storage),
            ("Причина", reason),
            ("Статус", status),
        ]:
            if not value:
                problems.append(f"{item_id}: пустое поле {field_name}")

        if read_access not in ACCESS_VALUES:
            problems.append(f"{item_id}: Доступ на чтение должен быть yes/no/limited")
        if write_access not in ACCESS_VALUES:
            problems.append(f"{item_id}: Доступ на изменение должен быть yes/no/limited")
        if read_access == "no" and write_access in {"yes", "limited"}:
            problems.append(f"{item_id}: нельзя менять данные без доступа на чтение")

        rows.append({
            "id": item_id,
            "audience": audience,
            "area": area,
            "read_access": read_access,
            "write_access": write_access,
            "storage": storage,
            "reason": reason,
            "status": status,
            "comment": clean(row.get("Комментарий")),
        })

    return rows, problems


def write_outputs(rows, problems):
    lines = [
        "# Отчёт по матрице доступа",
        "",
        "## Сводка",
        "",
        f"- Правил доступа: {len(rows)}",
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
        "## Матрица",
        "",
        "| Аудитория | Область | Чтение | Изменение | Хранение |",
        "|---|---|---|---|---|",
    ])
    for row in rows:
        lines.append(
            f"| {row['audience']} | {row['area']} | {row['read_access']} | {row['write_access']} | {row['storage']} |"
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = ["id", "audience", "area", "read_access", "write_access", "storage", "reason", "status", "comment"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    rows, problems = build_rows(read_access_rows(), load_audiences(), load_visibility())
    write_outputs(rows, problems)

    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")

    if problems:
        print("\nНайдены ошибки матрицы доступа:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
