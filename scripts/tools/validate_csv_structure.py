"""
Проверка CSV-файлов базы знаний.

Скрипт ищет базовые проблемы:
- пустые файлы;
- строки без ID;
- дубли ID;
- слишком короткие строки;
- файлы без заголовка.

Запуск из корня репозитория:
python scripts/tools/validate_csv_structure.py
"""

from pathlib import Path
import csv
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
CSV_DIRS = [ROOT / "templates", ROOT / "data" / "dictionaries", ROOT / "data" / "drafts"]


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.reader(file))


def looks_like_id(value: str) -> bool:
    if not value:
        return False
    return "-" in value and len(value.strip()) >= 6


def validate_file(path: Path):
    problems = []

    try:
        rows = read_rows(path)
    except Exception as exc:
        return [f"Не удалось прочитать файл: {exc}"]

    if not rows:
        return ["Пустой файл"]

    header = rows[0]
    if not header or not header[0].strip():
        problems.append("Нет корректного заголовка")

    ids = []
    for row_number, row in enumerate(rows[1:], start=2):
        if not row or all(not cell.strip() for cell in row):
            continue

        first_value = row[0].strip() if row else ""
        if not looks_like_id(first_value):
            problems.append(f"Строка {row_number}: первый столбец не похож на ID")
        else:
            ids.append((first_value, row_number))

        if len(row) < 3:
            problems.append(f"Строка {row_number}: слишком мало столбцов")

    seen = defaultdict(list)
    for value, row_number in ids:
        seen[value].append(row_number)

    for value, row_numbers in seen.items():
        if len(row_numbers) > 1:
            problems.append(f"Дубль ID {value}: строки {row_numbers}")

    return problems


def main():
    all_problems = {}

    for directory in CSV_DIRS:
        if not directory.exists():
            continue

        for path in sorted(directory.glob("*.csv")):
            problems = validate_file(path)
            if problems:
                all_problems[str(path.relative_to(ROOT))] = problems

    if not all_problems:
        print("CSV-проверка завершена: проблем не найдено.")
        return

    print("CSV-проверка завершена: найдены замечания.\n")
    for file_path, problems in all_problems.items():
        print(file_path)
        for problem in problems:
            print(f"  - {problem}")
        print()


if __name__ == "__main__":
    main()
