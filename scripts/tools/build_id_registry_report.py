"""
Реестр ID по CSV-файлам проекта.

Скрипт собирает значения из первого столбца CSV-файлов, группирует их по
префиксам и показывает возможные дубли. Отчёт сохраняется в build/id-registry.md.
"""

from pathlib import Path
import csv
from collections import Counter, defaultdict

from workbook_config import BUILD_DIR, ROOT

OUTPUT_FILE = BUILD_DIR / "id-registry.md"
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


def looks_like_id(value: str) -> bool:
    value = value.strip()
    return "-" in value and len(value) >= 6


def id_prefix(value: str) -> str:
    return value.split("-", 1)[0].strip() or "UNKNOWN"


def collect_ids():
    records = []
    skipped = []

    for path in collect_csv_files():
        relative_path = path.relative_to(ROOT).as_posix()
        try:
            rows = read_rows(path)
        except Exception as exc:
            skipped.append((relative_path, f"не удалось прочитать: {exc}"))
            continue

        for row_number, row in enumerate(rows[1:], start=2):
            if not row or all(not cell.strip() for cell in row):
                continue

            value = row[0].strip() if row else ""
            if not looks_like_id(value):
                skipped.append((relative_path, f"строка {row_number}: нет ID"))
                continue

            records.append({
                "id": value,
                "prefix": id_prefix(value),
                "file": relative_path,
                "row": row_number,
            })

    return records, skipped


def build_report():
    records, skipped = collect_ids()
    ids = [record["id"] for record in records]
    id_counts = Counter(ids)
    prefix_counts = Counter(record["prefix"] for record in records)
    duplicates = sorted(value for value, count in id_counts.items() if count > 1)

    locations_by_id = defaultdict(list)
    for record in records:
        locations_by_id[record["id"]].append(record)

    lines = [
        "# Реестр ID",
        "",
        "## Сводка",
        "",
        f"- ID найдено: {len(records)}",
        f"- Уникальных ID: {len(id_counts)}",
        f"- Префиксов ID: {len(prefix_counts)}",
        f"- Возможных дублей ID: {len(duplicates)}",
        f"- Пропущенных строк: {len(skipped)}",
        "",
        "## Префиксы",
        "",
        "| Префикс | Количество |",
        "|---|---:|",
    ]

    for prefix, count in sorted(prefix_counts.items()):
        lines.append(f"| `{prefix}` | {count} |")

    lines.extend(["", "## Возможные дубли", ""])
    if duplicates:
        for duplicate_id in duplicates:
            lines.append(f"### `{duplicate_id}`")
            for record in locations_by_id[duplicate_id]:
                lines.append(f"- `{record['file']}` строка {record['row']}")
            lines.append("")
    else:
        lines.append("- нет")

    lines.extend(["", "## Все ID", "", "| ID | Файл | Строка |", "|---|---|---:|"])
    for record in sorted(records, key=lambda item: (item["id"], item["file"], item["row"])):
        lines.append(f"| `{record['id']}` | `{record['file']}` | {record['row']} |")

    lines.extend(["", "## Пропущенные строки", ""])
    if skipped:
        for file_path, reason in skipped:
            lines.append(f"- `{file_path}`: {reason}")
    else:
        lines.append("- нет")

    lines.extend([
        "",
        "## Примечание",
        "",
        "Отчёт диагностический. Дубль ID нужно проверить вручную: иногда это ошибка, иногда строка-шаблон или служебная запись.",
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
