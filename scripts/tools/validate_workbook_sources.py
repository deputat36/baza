"""
Проверка источников XLSX-сборки.

Скрипт проверяет, что все CSV-файлы, указанные в `workbook_config.py`,
существуют и читаются.

Запуск:
python scripts/tools/validate_workbook_sources.py
"""

import csv
import sys
from pathlib import Path

from workbook_config import ROOT, SHEETS


def read_csv_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.reader(file))


def validate_source(relative_path: str):
    path = ROOT / relative_path
    problems = []

    if not path.exists():
        return ["файл не найден"]

    if not path.is_file():
        return ["путь не является файлом"]

    try:
        rows = read_csv_rows(path)
    except Exception as exc:
        return [f"не удалось прочитать CSV: {exc}"]

    if not rows:
        problems.append("файл пустой")
    elif not rows[0] or not any(cell.strip() for cell in rows[0]):
        problems.append("нет заголовка")

    return problems


def main():
    all_problems = {}
    total_sources = 0

    for sheet_name, files in SHEETS:
        for relative_path in files:
            total_sources += 1
            problems = validate_source(relative_path)
            if problems:
                key = f"{sheet_name}: {relative_path}"
                all_problems[key] = problems

    if not all_problems:
        print(f"Проверка источников XLSX завершена: {total_sources} файлов готовы.")
        return 0

    print("Проверка источников XLSX завершена: найдены проблемы.\n")
    for source, problems in all_problems.items():
        print(source)
        for problem in problems:
            print(f"  - {problem}")
        print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
