"""
План настройки листов Google Таблицы.

Скрипт строит сводку по листам на основе `workbook_config.py`:
- порядок листов;
- количество CSV-источников;
- строки данных;
- максимальное количество колонок;
- базовые настройки интерфейса.

Результат сохраняется в build/google-sheet-tabs-plan.md и build/google-sheet-tabs-plan.csv.
"""

from pathlib import Path
import csv

from workbook_config import BUILD_DIR, ROOT, SHEETS

MD_OUTPUT = BUILD_DIR / "google-sheet-tabs-plan.md"
CSV_OUTPUT = BUILD_DIR / "google-sheet-tabs-plan.csv"


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.reader(file))


def source_stats(relative_path: str):
    path = ROOT / relative_path
    if not path.exists():
        return {"exists": False, "rows": 0, "columns": 0}

    rows = read_rows(path)
    header = rows[0] if rows else []
    data_rows = [row for row in rows[1:] if row and any(cell.strip() for cell in row)]
    return {"exists": True, "rows": len(data_rows), "columns": len(header)}


def tab_recommendation(sheet_name: str):
    technical_tabs = {"Справочники", "Синонимы", "Предложения"}
    if sheet_name in technical_tabs:
        return "Можно скрыть от рядовых пользователей после настройки выпадающих списков"
    if sheet_name == "Главная":
        return "Оставить первым листом и использовать как навигацию"
    return "Оставить видимым, включить фильтр и закрепить строку заголовков"


def build_rows():
    result = []

    for sheet_order, (sheet_name, files) in enumerate(SHEETS, start=1):
        stats = [source_stats(relative_path) for relative_path in files]
        total_rows = sum(item["rows"] for item in stats)
        max_columns = max((item["columns"] for item in stats), default=0)
        missing_sources = sum(1 for item in stats if not item["exists"])

        result.append({
            "sheet_order": sheet_order,
            "sheet_name": sheet_name,
            "source_count": len(files),
            "data_rows": total_rows,
            "max_columns": max_columns,
            "missing_sources": missing_sources,
            "freeze_rows": 1,
            "enable_filter": "да",
            "recommendation": tab_recommendation(sheet_name),
            "sources": "; ".join(files),
        })

    return result


def write_csv(rows):
    fieldnames = [
        "sheet_order",
        "sheet_name",
        "source_count",
        "data_rows",
        "max_columns",
        "missing_sources",
        "freeze_rows",
        "enable_filter",
        "recommendation",
        "sources",
    ]

    with CSV_OUTPUT.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_markdown(rows):
    lines = [
        "# План листов Google Таблицы",
        "",
        "## Сводка",
        "",
        f"- Листов: {len(rows)}",
        f"- CSV-источников: {sum(row['source_count'] for row in rows)}",
        f"- Строк данных: {sum(row['data_rows'] for row in rows)}",
        "",
        "## Листы",
        "",
        "| № | Лист | CSV | Строк | Макс. колонок | Нет источников | Рекомендация |",
        "|---:|---|---:|---:|---:|---:|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['sheet_order']} | {row['sheet_name']} | {row['source_count']} | {row['data_rows']} | {row['max_columns']} | {row['missing_sources']} | {row['recommendation']} |"
        )

    lines.extend(["", "## Базовые настройки", ""])
    for row in rows:
        lines.append(f"### {row['sheet_order']}. {row['sheet_name']}")
        lines.append(f"- Закрепить строк: {row['freeze_rows']}")
        lines.append(f"- Включить фильтр: {row['enable_filter']}")
        lines.append(f"- CSV-источники: {row['sources']}")
        lines.append("")

    lines.extend([
        "## Правило",
        "",
        "План листов строится по `scripts/tools/workbook_config.py`. Если меняется состав XLSX, план Google Таблицы обновляется автоматически при следующем `make preflight`.",
    ])

    return "\n".join(lines) + "\n"


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    rows = build_rows()
    write_csv(rows)
    markdown = build_markdown(rows)
    MD_OUTPUT.write_text(markdown, encoding="utf-8")
    print(markdown)
    print(f"Готово: {MD_OUTPUT}")
    print(f"Готово: {CSV_OUTPUT}")


if __name__ == "__main__":
    main()
