"""
Сводный отчёт по CSV-файлам проекта.

Скрипт считает файлы, строки данных и базовые поля. Результат сохраняется
в build/data-report.md и печатается в консоль.

Запуск:
python scripts/tools/build_data_report.py
"""

from pathlib import Path
import csv
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = ROOT / "build"
OUTPUT_FILE = BUILD_DIR / "data-report.md"
CSV_DIRS = [ROOT / "templates", ROOT / "data" / "dictionaries", ROOT / "data" / "drafts"]


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.reader(file))


def collect_csv_files():
    files = []
    for directory in CSV_DIRS:
        if directory.exists():
            files.extend(sorted(directory.rglob("*.csv")))
    return files


def normalize_header(value: str) -> str:
    return value.strip().lower()


def file_stats(path: Path):
    rows = read_rows(path)
    header = rows[0] if rows else []
    data_rows = [row for row in rows[1:] if row and any(cell.strip() for cell in row)]

    status_counter = Counter()
    normalized_header = [normalize_header(cell) for cell in header]
    status_index = None

    for candidate in ("статус", "status"):
        if candidate in normalized_header:
            status_index = normalized_header.index(candidate)
            break

    if status_index is not None:
        for row in data_rows:
            if len(row) > status_index and row[status_index].strip():
                status_counter[row[status_index].strip()] += 1

    return {
        "path": path.relative_to(ROOT).as_posix(),
        "columns": len(header),
        "rows": len(data_rows),
        "statuses": status_counter,
    }


def build_report(stats):
    total_files = len(stats)
    total_rows = sum(item["rows"] for item in stats)

    lines = [
        "# Отчёт по данным",
        "",
        "## Сводка",
        "",
        f"- CSV-файлов: {total_files}",
        f"- Строк данных: {total_rows}",
        "",
        "## Файлы",
        "",
        "| Файл | Строк данных | Колонок | Статусы |",
        "|---|---:|---:|---|",
    ]

    for item in stats:
        statuses = ", ".join(
            f"{status}: {count}" for status, count in sorted(item["statuses"].items())
        ) or "-"
        lines.append(
            f"| `{item['path']}` | {item['rows']} | {item['columns']} | {statuses} |"
        )

    lines.extend([
        "",
        "## Примечание",
        "",
        "Отчёт показывает только техническую сводку. Он не подтверждает актуальность контактов, юридическую точность и полноту данных.",
    ])

    return "\n".join(lines) + "\n"


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    stats = [file_stats(path) for path in collect_csv_files()]
    report = build_report(stats)
    OUTPUT_FILE.write_text(report, encoding="utf-8")
    print(report)
    print(f"Готово: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
