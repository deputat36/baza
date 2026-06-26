"""
Отчёт по схемам CSV-файлов.

Скрипт собирает заголовки CSV, группирует одинаковые схемы и показывает
потенциальные проблемы: пустые заголовки, повторяющиеся колонки и файлы без строк.

Результат сохраняется в build/schema-report.md.
"""

from pathlib import Path
import csv
from collections import Counter, defaultdict

from workbook_config import BUILD_DIR, ROOT

OUTPUT_FILE = BUILD_DIR / "schema-report.md"
CSV_DIRS = [ROOT / "templates", ROOT / "data" / "dictionaries", ROOT / "data" / "drafts"]


def collect_csv_files():
    files = []
    for directory in CSV_DIRS:
        if directory.exists():
            files.extend(sorted(directory.rglob("*.csv")))
    return files


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.reader(file))


def normalize_header(header):
    return tuple(cell.strip() for cell in header)


def analyze_file(path: Path):
    relative_path = path.relative_to(ROOT).as_posix()

    try:
        rows = read_rows(path)
    except Exception as exc:
        return {
            "file": relative_path,
            "header": tuple(),
            "rows": 0,
            "problems": [f"не удалось прочитать CSV: {exc}"],
        }

    if not rows:
        return {
            "file": relative_path,
            "header": tuple(),
            "rows": 0,
            "problems": ["файл пустой"],
        }

    header = normalize_header(rows[0])
    data_rows = [row for row in rows[1:] if row and any(cell.strip() for cell in row)]
    problems = []

    if not header or not any(header):
        problems.append("нет заголовка")

    empty_columns = [idx + 1 for idx, value in enumerate(header) if not value]
    if empty_columns:
        problems.append(f"пустые названия колонок: {empty_columns}")

    header_counts = Counter(value for value in header if value)
    duplicate_columns = sorted(value for value, count in header_counts.items() if count > 1)
    if duplicate_columns:
        problems.append("повторяющиеся колонки: " + ", ".join(duplicate_columns))

    return {
        "file": relative_path,
        "header": header,
        "rows": len(data_rows),
        "problems": problems,
    }


def build_report():
    analyses = [analyze_file(path) for path in collect_csv_files()]
    schema_groups = defaultdict(list)

    for item in analyses:
        schema_groups[item["header"]].append(item)

    problem_files = [item for item in analyses if item["problems"]]

    lines = [
        "# Отчёт по схемам CSV",
        "",
        "## Сводка",
        "",
        f"- CSV-файлов: {len(analyses)}",
        f"- Уникальных схем заголовков: {len(schema_groups)}",
        f"- Файлов с замечаниями по схеме: {len(problem_files)}",
        "",
        "## Файлы и заголовки",
        "",
        "| Файл | Строк данных | Колонок | Заголовки |",
        "|---|---:|---:|---|",
    ]

    for item in sorted(analyses, key=lambda value: value["file"]):
        header_text = ", ".join(item["header"]) if item["header"] else "-"
        lines.append(f"| `{item['file']}` | {item['rows']} | {len(item['header'])} | {header_text} |")

    lines.extend(["", "## Группы одинаковых схем", ""])
    for index, (header, items) in enumerate(sorted(schema_groups.items(), key=lambda pair: (-len(pair[1]), pair[0])), start=1):
        header_text = ", ".join(header) if header else "-"
        lines.append(f"### Схема {index}: {len(items)} файл(ов)")
        lines.append("")
        lines.append(f"Колонки: {header_text}")
        lines.append("")
        for item in sorted(items, key=lambda value: value["file"]):
            lines.append(f"- `{item['file']}`")
        lines.append("")

    lines.extend(["## Замечания", ""])
    if problem_files:
        for item in sorted(problem_files, key=lambda value: value["file"]):
            lines.append(f"### `{item['file']}`")
            for problem in item["problems"]:
                lines.append(f"- {problem}")
            lines.append("")
    else:
        lines.append("- нет")

    lines.extend([
        "",
        "## Примечание",
        "",
        "Отчёт диагностический. Разные схемы CSV допустимы, если они соответствуют назначению разделов.",
    ])

    return "\n".join(lines) + "\n"


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    report = build_report()
    OUTPUT_FILE.write_text(report, encoding="utf-8")
    print(report)
    print(f"Готово: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
