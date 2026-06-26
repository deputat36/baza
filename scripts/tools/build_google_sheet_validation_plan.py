"""
План выпадающих списков для Google Таблицы.

Скрипт собирает значения из справочников `data/dictionaries` и формирует:
- build/google-sheet-validation-plan.md
- build/google-sheet-validation-plan.csv
"""

from pathlib import Path
import csv

from workbook_config import BUILD_DIR, ROOT

MD_OUTPUT = BUILD_DIR / "google-sheet-validation-plan.md"
CSV_OUTPUT = BUILD_DIR / "google-sheet-validation-plan.csv"

DICTIONARIES = [
    {
        "name": "Статусы",
        "source": "data/dictionaries/statuses.csv",
        "value_column": "code",
        "label_column": "name",
        "target_columns": "Статус, status",
        "usage": "Использовать для статуса записи и проверки актуальности",
    },
    {
        "name": "Приоритеты",
        "source": "data/dictionaries/priorities.csv",
        "value_column": "priority",
        "label_column": "name",
        "target_columns": "Приоритет, priority",
        "usage": "Использовать для сортировки важных записей и частоты применения",
    },
    {
        "name": "Категории",
        "source": "data/dictionaries/categories-core.csv",
        "value_column": "code",
        "label_column": "name",
        "target_columns": "Категория, category",
        "usage": "Использовать для группировки контактов, ситуаций и материалов",
    },
    {
        "name": "Типы объектов",
        "source": "data/dictionaries/object-types.csv",
        "value_column": "code",
        "label_column": "name",
        "target_columns": "Тип, type",
        "usage": "Использовать для типа сущности: контакт, документ, инструкция, ситуация",
    },
]


def read_dict_rows(relative_path: str):
    path = ROOT / relative_path
    if not path.exists():
        return [], [f"файл не найден: {relative_path}"]

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        if not reader.fieldnames:
            return [], [f"нет заголовков: {relative_path}"]
        return rows, []


def build_rows():
    result = []

    for dictionary in DICTIONARIES:
        rows, problems = read_dict_rows(dictionary["source"])
        if problems:
            result.append({
                "dictionary": dictionary["name"],
                "source_csv": dictionary["source"],
                "value": "",
                "label": "",
                "target_columns": dictionary["target_columns"],
                "usage": dictionary["usage"],
                "status": "; ".join(problems),
            })
            continue

        for row in rows:
            value = row.get(dictionary["value_column"], "").strip()
            label = row.get(dictionary["label_column"], "").strip()
            if not value:
                continue

            result.append({
                "dictionary": dictionary["name"],
                "source_csv": dictionary["source"],
                "value": value,
                "label": label,
                "target_columns": dictionary["target_columns"],
                "usage": dictionary["usage"],
                "status": "OK",
            })

    return result


def write_csv(rows):
    fieldnames = ["dictionary", "source_csv", "value", "label", "target_columns", "usage", "status"]
    with CSV_OUTPUT.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_markdown(rows):
    groups = {}
    for row in rows:
        groups.setdefault(row["dictionary"], []).append(row)

    lines = [
        "# План выпадающих списков Google Таблицы",
        "",
        "## Сводка",
        "",
        f"- Справочников: {len(groups)}",
        f"- Значений: {sum(1 for row in rows if row['status'] == 'OK')}",
        f"- Замечаний: {sum(1 for row in rows if row['status'] != 'OK')}",
        "",
        "## Справочники",
        "",
    ]

    for dictionary_name, items in groups.items():
        first = items[0]
        lines.append(f"### {dictionary_name}")
        lines.append(f"- Источник: `{first['source_csv']}`")
        lines.append(f"- Колонки для применения: {first['target_columns']}")
        lines.append(f"- Назначение: {first['usage']}")
        lines.append("")
        lines.append("| Значение | Подпись | Статус |")
        lines.append("|---|---|---|")
        for item in items:
            lines.append(f"| `{item['value']}` | {item['label']} | {item['status']} |")
        lines.append("")

    lines.extend([
        "## Как применять",
        "",
        "1. Создать или проверить лист `Справочники`.",
        "2. Перенести значения из CSV-справочников.",
        "3. Настроить проверку данных в рабочих листах по указанным колонкам.",
        "4. Для сотрудников показывать понятные подписи, а коды использовать как стабильные значения.",
        "",
        "## Ограничение",
        "",
        "План не настраивает Google Таблицу автоматически. Он фиксирует, какие справочники использовать при ручной настройке выпадающих списков.",
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
