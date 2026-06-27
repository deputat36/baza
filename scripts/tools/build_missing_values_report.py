"""
Отчёт по незаполненным значениям в CSV-файлах.

Скрипт помогает перед переносом в закрытую Google Таблицу увидеть,
где много пустых ячеек, пустые ID, статусы и приоритеты.

Запуск из корня репозитория:
python scripts/tools/build_missing_values_report.py
"""

from pathlib import Path
import csv

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

REPORT_MD = BUILD_DIR / "missing-values-report.md"
REPORT_CSV = BUILD_DIR / "missing-values-report.csv"
CSV_DIRS = [
    ROOT / "templates",
    ROOT / "data" / "dictionaries",
    ROOT / "data" / "drafts",
]

STATUS_HEADERS = {"Статус", "status"}
PRIORITY_HEADERS = {"Приоритет", "priority"}
ID_HEADERS = {"ID", "id"}


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.reader(file))


def find_header_index(headers, candidates):
    for index, header in enumerate(headers):
        if header.strip() in candidates:
            return index
    return None


def is_empty(value):
    return not str(value or "").strip()


def cell_at(row, index):
    if index is None or index >= len(row):
        return ""
    return row[index]


def analyze_file(path: Path):
    rows = read_rows(path)
    if not rows:
        return {
            "path": path.relative_to(ROOT).as_posix(),
            "rows": 0,
            "columns": 0,
            "empty_cells": 0,
            "empty_percent": 0,
            "empty_id_rows": 0,
            "empty_status_rows": 0,
            "empty_priority_rows": 0,
            "notes": "Пустой файл",
        }

    headers = [str(value or "").strip() for value in rows[0]]
    data_rows = rows[1:]
    column_count = len(headers)
    cell_count = max(len(data_rows) * column_count, 1)

    id_index = find_header_index(headers, ID_HEADERS)
    status_index = find_header_index(headers, STATUS_HEADERS)
    priority_index = find_header_index(headers, PRIORITY_HEADERS)

    empty_cells = 0
    empty_id_rows = 0
    empty_status_rows = 0
    empty_priority_rows = 0

    for row in data_rows:
        for index in range(column_count):
            if is_empty(cell_at(row, index)):
                empty_cells += 1

        if id_index is not None and not all(is_empty(cell) for cell in row):
            if is_empty(cell_at(row, id_index)):
                empty_id_rows += 1

        if status_index is not None and not all(is_empty(cell) for cell in row):
            if is_empty(cell_at(row, status_index)):
                empty_status_rows += 1

        if priority_index is not None and not all(is_empty(cell) for cell in row):
            if is_empty(cell_at(row, priority_index)):
                empty_priority_rows += 1

    notes = []
    if id_index is None:
        notes.append("нет колонки ID")
    if status_index is None:
        notes.append("нет колонки Статус")
    if priority_index is None:
        notes.append("нет колонки Приоритет")

    return {
        "path": path.relative_to(ROOT).as_posix(),
        "rows": len(data_rows),
        "columns": column_count,
        "empty_cells": empty_cells,
        "empty_percent": round(empty_cells * 100 / cell_count, 1),
        "empty_id_rows": empty_id_rows,
        "empty_status_rows": empty_status_rows,
        "empty_priority_rows": empty_priority_rows,
        "notes": "; ".join(notes),
    }


def collect_csv_files():
    files = []
    for directory in CSV_DIRS:
        if directory.exists():
            files.extend(sorted(directory.glob("*.csv")))
    return files


def build_markdown(results):
    lines = [
        "# Отчёт по незаполненным данным",
        "",
        "## Назначение",
        "",
        "Отчёт показывает, где в CSV-файлах много пустых ячеек, пустые ID, статусы и приоритеты.",
        "",
        "## Сводка",
        "",
        "| Файл | Строк | Колонок | Пустых ячеек | Пустых, % | Пустой ID | Пустой статус | Пустой приоритет | Примечания |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]

    for item in results:
        lines.append(
            f"| `{item['path']}` | {item['rows']} | {item['columns']} | {item['empty_cells']} | "
            f"{item['empty_percent']} | {item['empty_id_rows']} | {item['empty_status_rows']} | "
            f"{item['empty_priority_rows']} | {item['notes']} |"
        )

    lines.extend([
        "",
        "## Как использовать",
        "",
        "1. Сначала смотреть файлы с пустыми ID.",
        "2. Затем смотреть пустые статусы и приоритеты.",
        "3. Потом разбирать файлы с высоким процентом пустых ячеек.",
        "4. Реальные рабочие контакты и внутренние данные заполнять только в закрытой Google Таблице.",
        "",
        "## Ограничение",
        "",
        "Отчёт не говорит, что пустая ячейка всегда ошибка. Некоторые поля могут быть необязательными.",
    ])

    return "\n".join(lines) + "\n"


def write_csv(results):
    headers = [
        "Файл",
        "Строк",
        "Колонок",
        "Пустых ячеек",
        "Пустых %",
        "Пустой ID",
        "Пустой статус",
        "Пустой приоритет",
        "Примечания",
    ]

    with REPORT_CSV.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for item in results:
            writer.writerow([
                item["path"],
                item["rows"],
                item["columns"],
                item["empty_cells"],
                item["empty_percent"],
                item["empty_id_rows"],
                item["empty_status_rows"],
                item["empty_priority_rows"],
                item["notes"],
            ])


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    results = [analyze_file(path) for path in collect_csv_files()]
    REPORT_MD.write_text(build_markdown(results), encoding="utf-8")
    write_csv(results)
    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
