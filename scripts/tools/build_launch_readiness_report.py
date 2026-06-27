"""
Отчёт готовности разделов к запуску.

Скрипт анализирует CSV-источники из workbook_config.py и показывает,
какие листы можно переносить в закрытую Google Таблицу, а какие требуют проверки.

Запуск из корня репозитория:
python scripts/tools/build_launch_readiness_report.py
"""

from pathlib import Path
import csv

try:
    from workbook_config import ROOT, BUILD_DIR, SHEETS
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"
    SHEETS = []

REPORT_MD = BUILD_DIR / "launch-readiness-report.md"
REPORT_CSV = BUILD_DIR / "launch-readiness-report.csv"

ID_HEADERS = {"ID", "id"}
STATUS_HEADERS = {"Статус", "status"}
PRIORITY_HEADERS = {"Приоритет", "priority"}


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.reader(file))


def is_empty(value):
    return not str(value or "").strip()


def find_header_index(headers, candidates):
    for index, header in enumerate(headers):
        if str(header or "").strip() in candidates:
            return index
    return None


def iter_sheet_sources():
    for sheet in SHEETS:
        if isinstance(sheet, dict):
            title = sheet.get("title") or sheet.get("name") or "Без названия"
            raw_sources = sheet.get("sources") or sheet.get("source") or []
        else:
            title = sheet[0]
            raw_sources = sheet[1]

        if isinstance(raw_sources, (str, Path)):
            raw_sources = [raw_sources]

        yield title, [ROOT / source for source in raw_sources]


def analyze_source(path: Path):
    result = {
        "path": path.relative_to(ROOT).as_posix(),
        "exists": path.exists(),
        "rows": 0,
        "empty_id": 0,
        "empty_status": 0,
        "empty_priority": 0,
        "notes": [],
    }

    if not path.exists():
        result["notes"].append("файл отсутствует")
        return result

    rows = read_rows(path)
    if not rows:
        result["notes"].append("пустой файл")
        return result

    headers = [str(value or "").strip() for value in rows[0]]
    data_rows = rows[1:]
    result["rows"] = len([row for row in data_rows if not all(is_empty(cell) for cell in row)])

    id_index = find_header_index(headers, ID_HEADERS)
    status_index = find_header_index(headers, STATUS_HEADERS)
    priority_index = find_header_index(headers, PRIORITY_HEADERS)

    if id_index is None:
        result["notes"].append("нет ID")
    if status_index is None:
        result["notes"].append("нет статуса")
    if priority_index is None:
        result["notes"].append("нет приоритета")

    for row in data_rows:
        if all(is_empty(cell) for cell in row):
            continue

        if id_index is not None and (id_index >= len(row) or is_empty(row[id_index])):
            result["empty_id"] += 1
        if status_index is not None and (status_index >= len(row) or is_empty(row[status_index])):
            result["empty_status"] += 1
        if priority_index is not None and (priority_index >= len(row) or is_empty(row[priority_index])):
            result["empty_priority"] += 1

    return result


def status_for_sheet(source_results):
    missing_files = [item for item in source_results if not item["exists"]]
    total_rows = sum(item["rows"] for item in source_results)
    empty_id = sum(item["empty_id"] for item in source_results)
    empty_status = sum(item["empty_status"] for item in source_results)
    empty_priority = sum(item["empty_priority"] for item in source_results)

    if missing_files or total_rows == 0:
        return "DRAFT"
    if empty_id or empty_status or empty_priority:
        return "CHECK"
    return "READY"


def recommendation_for_status(status):
    if status == "READY":
        return "Можно переносить структуру, затем вручную проверить смысл данных."
    if status == "CHECK":
        return "Перед переносом проверить пустые ID, статусы и приоритеты."
    return "Сначала заполнить или подключить источники раздела."


def build_results():
    results = []
    for sheet_title, sources in iter_sheet_sources():
        source_results = [analyze_source(path) for path in sources]
        status = status_for_sheet(source_results)
        results.append({
            "sheet": sheet_title,
            "status": status,
            "sources": len(source_results),
            "rows": sum(item["rows"] for item in source_results),
            "empty_id": sum(item["empty_id"] for item in source_results),
            "empty_status": sum(item["empty_status"] for item in source_results),
            "empty_priority": sum(item["empty_priority"] for item in source_results),
            "missing_files": sum(1 for item in source_results if not item["exists"]),
            "recommendation": recommendation_for_status(status),
            "source_details": source_results,
        })
    return results


def build_markdown(results):
    ready = sum(1 for item in results if item["status"] == "READY")
    check = sum(1 for item in results if item["status"] == "CHECK")
    draft = sum(1 for item in results if item["status"] == "DRAFT")

    lines = [
        "# Отчёт готовности к запуску",
        "",
        "## Назначение",
        "",
        "Отчёт показывает техническую готовность листов будущей закрытой Google Таблицы.",
        "",
        "## Сводка",
        "",
        f"- READY: {ready}",
        f"- CHECK: {check}",
        f"- DRAFT: {draft}",
        "",
        "## Разделы",
        "",
        "| Лист | Статус | Источников | Строк | Пустой ID | Пустой статус | Пустой приоритет | Нет файлов | Рекомендация |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]

    for item in results:
        lines.append(
            f"| {item['sheet']} | {item['status']} | {item['sources']} | {item['rows']} | "
            f"{item['empty_id']} | {item['empty_status']} | {item['empty_priority']} | "
            f"{item['missing_files']} | {item['recommendation']} |"
        )

    lines.extend(["", "## Детализация источников", ""])
    for item in results:
        lines.extend([f"### {item['sheet']}", ""])
        lines.append("| Файл | Есть | Строк | Пустой ID | Пустой статус | Пустой приоритет | Примечания |")
        lines.append("|---|---|---:|---:|---:|---:|---|")
        for source in item["source_details"]:
            exists = "да" if source["exists"] else "нет"
            notes = "; ".join(source["notes"])
            lines.append(
                f"| `{source['path']}` | {exists} | {source['rows']} | {source['empty_id']} | "
                f"{source['empty_status']} | {source['empty_priority']} | {notes} |"
            )
        lines.append("")

    lines.extend([
        "## Как читать статусы",
        "",
        "- READY — источники есть, строки есть, пустых ID/статусов/приоритетов не найдено.",
        "- CHECK — раздел технически есть, но перед переносом нужна ручная проверка обязательных полей.",
        "- DRAFT — нет строк данных или отсутствует источник.",
        "",
        "## Ограничение",
        "",
        "Отчёт оценивает только техническую готовность. Он не подтверждает актуальность контактов и юридическую точность данных.",
    ])

    return "\n".join(lines) + "\n"


def write_csv(results):
    with REPORT_CSV.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Лист",
            "Статус",
            "Источников",
            "Строк",
            "Пустой ID",
            "Пустой статус",
            "Пустой приоритет",
            "Нет файлов",
            "Рекомендация",
        ])
        for item in results:
            writer.writerow([
                item["sheet"],
                item["status"],
                item["sources"],
                item["rows"],
                item["empty_id"],
                item["empty_status"],
                item["empty_priority"],
                item["missing_files"],
                item["recommendation"],
            ])


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    results = build_results()
    REPORT_MD.write_text(build_markdown(results), encoding="utf-8")
    write_csv(results)
    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
