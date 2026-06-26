"""
Отчёт покрытия CSV-файлов XLSX-сборкой.

Скрипт показывает:
- какие CSV указаны в `workbook_config.py`;
- какие CSV фактически есть в рабочих папках;
- какие CSV не включены в XLSX-сборку;
- есть ли дубли в карте источников.

Отчёт сохраняется в build/source-coverage-report.md.
"""

from pathlib import Path
from collections import Counter, defaultdict

from workbook_config import BUILD_DIR, ROOT, SHEETS

OUTPUT_FILE = BUILD_DIR / "source-coverage-report.md"
CSV_DIRS = [ROOT / "templates", ROOT / "data" / "dictionaries", ROOT / "data" / "drafts"]


def collect_csv_files():
    files = []
    for directory in CSV_DIRS:
        if directory.exists():
            files.extend(path.relative_to(ROOT).as_posix() for path in sorted(directory.rglob("*.csv")))
    return files


def collect_configured_sources():
    sources = []
    source_to_sheets = defaultdict(list)

    for sheet_name, files in SHEETS:
        for relative_path in files:
            sources.append(relative_path)
            source_to_sheets[relative_path].append(sheet_name)

    return sources, source_to_sheets


def build_report():
    actual_files = set(collect_csv_files())
    configured_sources, source_to_sheets = collect_configured_sources()
    configured_set = set(configured_sources)
    source_counts = Counter(configured_sources)

    included_existing = sorted(configured_set & actual_files)
    configured_missing = sorted(configured_set - actual_files)
    not_in_workbook = sorted(actual_files - configured_set)
    duplicate_sources = sorted(path for path, count in source_counts.items() if count > 1)

    lines = [
        "# Отчёт покрытия CSV-источников",
        "",
        "## Сводка",
        "",
        f"- CSV-файлов в рабочих папках: {len(actual_files)}",
        f"- CSV-источников в XLSX-конфиге: {len(configured_set)}",
        f"- Включены в XLSX и существуют: {len(included_existing)}",
        f"- Указаны в XLSX, но отсутствуют: {len(configured_missing)}",
        f"- Есть в репозитории, но не входят в XLSX: {len(not_in_workbook)}",
        f"- Дубли в XLSX-конфиге: {len(duplicate_sources)}",
        "",
        "## CSV в XLSX",
        "",
        "| CSV | Листы |",
        "|---|---|",
    ]

    for path in included_existing:
        sheets = ", ".join(source_to_sheets[path])
        lines.append(f"| `{path}` | {sheets} |")

    lines.extend(["", "## Указаны в XLSX, но отсутствуют", ""])
    if configured_missing:
        lines.extend(f"- `{path}`" for path in configured_missing)
    else:
        lines.append("- нет")

    lines.extend(["", "## Есть в репозитории, но не входят в XLSX", ""])
    if not_in_workbook:
        lines.extend(f"- `{path}`" for path in not_in_workbook)
    else:
        lines.append("- нет")

    lines.extend(["", "## Дубли в XLSX-конфиге", ""])
    if duplicate_sources:
        for path in duplicate_sources:
            sheets = ", ".join(source_to_sheets[path])
            lines.append(f"- `{path}`: {source_counts[path]} раза; листы: {sheets}")
    else:
        lines.append("- нет")

    lines.extend([
        "",
        "## Примечание",
        "",
        "CSV вне XLSX не всегда являются ошибкой. Это могут быть служебные шаблоны, чек-листы или журналы тестирования.",
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
