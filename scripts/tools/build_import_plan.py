"""
План импорта CSV в Google Таблицу.

Скрипт строит импортный план на основе `workbook_config.py` и сохраняет:
- build/import-plan.csv
- build/import-plan.md
"""

from pathlib import Path
import csv

from workbook_config import BUILD_DIR, ROOT, SHEETS

CSV_OUTPUT = BUILD_DIR / "import-plan.csv"
MD_OUTPUT = BUILD_DIR / "import-plan.md"


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.reader(file))


def source_stats(relative_path: str):
    path = ROOT / relative_path
    if not path.exists():
        return {
            "exists": "нет",
            "rows": 0,
            "columns": 0,
            "header": "",
        }

    rows = read_rows(path)
    header = rows[0] if rows else []
    data_rows = [row for row in rows[1:] if row and any(cell.strip() for cell in row)]

    return {
        "exists": "да",
        "rows": len(data_rows),
        "columns": len(header),
        "header": ", ".join(cell.strip() for cell in header),
    }


def build_rows():
    rows = []
    order = 1

    for sheet_order, (sheet_name, files) in enumerate(SHEETS, start=1):
        for source_order, relative_path in enumerate(files, start=1):
            stats = source_stats(relative_path)
            rows.append({
                "order": order,
                "sheet_order": sheet_order,
                "sheet_name": sheet_name,
                "source_order": source_order,
                "source_csv": relative_path,
                "exists": stats["exists"],
                "data_rows": stats["rows"],
                "columns": stats["columns"],
                "header": stats["header"],
                "import_note": "Импортировать в указанный лист после проверки preflight-отчётов",
            })
            order += 1

    return rows


def write_csv(rows):
    fieldnames = [
        "order",
        "sheet_order",
        "sheet_name",
        "source_order",
        "source_csv",
        "exists",
        "data_rows",
        "columns",
        "header",
        "import_note",
    ]

    with CSV_OUTPUT.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_markdown(rows):
    total_rows = sum(row["data_rows"] for row in rows)
    missing = [row for row in rows if row["exists"] != "да"]

    lines = [
        "# План импорта в Google Таблицу",
        "",
        "## Сводка",
        "",
        f"- CSV-источников: {len(rows)}",
        f"- Строк данных: {total_rows}",
        f"- Отсутствующих источников: {len(missing)}",
        "",
        "## Порядок импорта",
        "",
        "| № | Лист | CSV | Строк | Колонок | Статус |",
        "|---:|---|---|---:|---:|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['order']} | {row['sheet_name']} | `{row['source_csv']}` | {row['data_rows']} | {row['columns']} | {row['exists']} |"
        )

    lines.extend(["", "## Отсутствующие источники", ""])
    if missing:
        lines.extend(f"- `{row['source_csv']}` для листа `{row['sheet_name']}`" for row in missing)
    else:
        lines.append("- нет")

    lines.extend([
        "",
        "## Правило импорта",
        "",
        "Перед переносом открыть `preflight-summary.md`, проверить диагностические отчёты и только после этого переносить данные в закрытую Google Таблицу.",
        "",
        "Реальные внутренние контакты и приватные данные не добавлять в публичные CSV.",
    ])

    return "\n".join(lines) + "\n"


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    rows = build_rows()
    write_csv(rows)
    markdown = build_markdown(rows)
    MD_OUTPUT.write_text(markdown, encoding="utf-8")
    print(markdown)
    print(f"Готово: {CSV_OUTPUT}")
    print(f"Готово: {MD_OUTPUT}")


if __name__ == "__main__":
    main()
