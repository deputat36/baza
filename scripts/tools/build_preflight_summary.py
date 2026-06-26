"""
Сводка preflight-проверки.

Скрипт собирает короткий markdown-файл со списком созданных артефактов и
ручным чек-листом перед переносом данных в закрытую Google Таблицу.

Результат сохраняется в build/preflight-summary.md.
"""

from pathlib import Path

from workbook_config import BUILD_DIR, OUTPUT_FILE

SUMMARY_FILE = BUILD_DIR / "preflight-summary.md"

EXPECTED_ARTIFACTS = [
    (OUTPUT_FILE.name, "Промежуточная Excel-книга для просмотра структуры"),
    ("import-plan.md", "Порядок импорта CSV в Google Таблицу"),
    ("import-plan.csv", "Табличная версия плана импорта"),
    ("data-report.md", "Техническая сводка по CSV-файлам"),
    ("source-coverage-report.md", "Покрытие CSV-файлов XLSX-сборкой"),
    ("id-registry.md", "Реестр ID и возможные дубли"),
    ("schema-report.md", "Отчёт по схемам и заголовкам CSV"),
]

MANUAL_CHECKS = [
    "Открыть XLSX и проверить список листов.",
    "Проверить `import-plan.md`: порядок переноса CSV в Google Таблицу понятен.",
    "Проверить `data-report.md`: нет ли неожиданно пустых разделов.",
    "Проверить `source-coverage-report.md`: CSV вне XLSX действительно служебные или будущие.",
    "Проверить `id-registry.md`: возможные дубли ID не являются ошибками.",
    "Проверить `schema-report.md`: однотипные CSV имеют ожидаемые заголовки.",
    "Проверить privacy scan в логах: нет ли реальных рабочих контактов или приватных данных.",
    "Перед импортом убедиться, что реальные внутренние данные остаются только в закрытой Google Таблице.",
]


def artifact_status(file_name: str):
    path = BUILD_DIR / file_name
    if not path.exists():
        return "нет", "-"
    if path.is_file():
        return "есть", f"{path.stat().st_size} байт"
    return "есть", "каталог"


def build_summary():
    lines = [
        "# Preflight-сводка",
        "",
        "## Назначение",
        "",
        "Этот файл собирает в одном месте результаты технической проверки перед переносом данных в закрытую Google Таблицу.",
        "",
        "## Артефакты",
        "",
        "| Файл | Статус | Размер | Назначение |",
        "|---|---|---:|---|",
    ]

    for file_name, description in EXPECTED_ARTIFACTS:
        status, size = artifact_status(file_name)
        lines.append(f"| `{file_name}` | {status} | {size} | {description} |")

    lines.extend(["", "## Ручной чек-лист", ""])
    for index, item in enumerate(MANUAL_CHECKS, start=1):
        lines.append(f"{index}. {item}")

    lines.extend([
        "",
        "## Что считать готовностью",
        "",
        "Данные можно переносить в закрытую Google Таблицу, если блокирующие проверки прошли, XLSX открывается, план импорта понятен, а замечания из диагностических отчётов проверены вручную.",
        "",
        "## Ограничение",
        "",
        "Сводка не подтверждает актуальность контактов и юридическую точность данных. Она фиксирует только техническую готовность структуры.",
    ])

    return "\n".join(lines) + "\n"


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    summary = build_summary()
    SUMMARY_FILE.write_text(summary, encoding="utf-8")
    print(summary)
    print(f"Готово: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
