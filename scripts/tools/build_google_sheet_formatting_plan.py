"""
План оформления и условного форматирования Google Таблицы.

Скрипт формирует правила оформления для статусов, приоритетов и базовых
настроек листов. Результат сохраняется в:
- build/google-sheet-formatting-plan.md
- build/google-sheet-formatting-plan.csv
"""

from pathlib import Path
import csv

from workbook_config import BUILD_DIR

MD_OUTPUT = BUILD_DIR / "google-sheet-formatting-plan.md"
CSV_OUTPUT = BUILD_DIR / "google-sheet-formatting-plan.csv"

STATUS_RULES = [
    ("VERIFIED", "Проверено", "#D9EAD3", "#274E13", "Можно использовать"),
    ("CHECK", "Нужно проверить", "#FFF2CC", "#7F6000", "Требует ручной проверки"),
    ("REVIEW", "На проверке", "#D9EAF7", "#0B5394", "Ожидает проверки ответственным"),
    ("DRAFT", "Черновик", "#EADCF8", "#351C75", "Не использовать как финальную запись"),
    ("OUTDATED", "Устарело", "#F4CCCC", "#990000", "Не использовать без обновления"),
    ("BROKEN", "Не работает", "#FCE5CD", "#783F04", "Контакт, ссылка или процесс не работает"),
    ("NOT_RECOMMENDED", "Не рекомендовать", "#E6B8AF", "#660000", "Не использовать в работе"),
    ("PRIVATE", "Внутреннее", "#D9D2E9", "#20124D", "Доступ ограничить"),
]

PRIORITY_RULES = [
    ("5", "Критически важно", "#CC0000", "#FFFFFF", "Показывать вверху и проверять регулярно"),
    ("4", "Важно", "#E69138", "#FFFFFF", "Высокий рабочий приоритет"),
    ("3", "Полезно", "#F1C232", "#000000", "Средний приоритет"),
    ("2", "Редко", "#D9EAD3", "#000000", "Низкая частота использования"),
    ("1", "Справочно", "#EEEEEE", "#666666", "Справочная информация"),
]

BASE_RULES = [
    ("Все рабочие листы", "Первая строка", "Закрепить строку заголовков", "Закрепить 1 строку"),
    ("Все рабочие листы", "Заголовки", "Выделить заголовки", "Жирный текст, светлый фон"),
    ("Все рабочие листы", "Данные", "Включить фильтр", "Фильтр по всем заполненным колонкам"),
    ("Все рабочие листы", "Текст", "Включить перенос", "Перенос текста для длинных описаний"),
    ("Справочники", "Лист", "Можно скрыть", "После настройки выпадающих списков"),
]


def build_rows():
    rows = []

    for value, label, bg, fg, note in STATUS_RULES:
        rows.append({
            "group": "Статусы",
            "target": "Столбец Статус / status",
            "condition": value,
            "label": label,
            "background": bg,
            "text_color": fg,
            "action": "Условное форматирование по точному совпадению",
            "note": note,
        })

    for value, label, bg, fg, note in PRIORITY_RULES:
        rows.append({
            "group": "Приоритеты",
            "target": "Столбец Приоритет / priority",
            "condition": value,
            "label": label,
            "background": bg,
            "text_color": fg,
            "action": "Условное форматирование по точному совпадению",
            "note": note,
        })

    for sheet, target, action, note in BASE_RULES:
        rows.append({
            "group": "Базовое оформление",
            "target": f"{sheet}: {target}",
            "condition": "",
            "label": "",
            "background": "",
            "text_color": "",
            "action": action,
            "note": note,
        })

    return rows


def write_csv(rows):
    fieldnames = ["group", "target", "condition", "label", "background", "text_color", "action", "note"]
    with CSV_OUTPUT.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_markdown(rows):
    lines = [
        "# План оформления Google Таблицы",
        "",
        "## Сводка",
        "",
        f"- Правил: {len(rows)}",
        "- Формат: ручная настройка в закрытой Google Таблице",
        "",
        "## Условное форматирование статусов",
        "",
        "| Значение | Подпись | Фон | Текст | Назначение |",
        "|---|---|---|---|---|",
    ]

    for value, label, bg, fg, note in STATUS_RULES:
        lines.append(f"| `{value}` | {label} | `{bg}` | `{fg}` | {note} |")

    lines.extend(["", "## Условное форматирование приоритетов", "", "| Значение | Подпись | Фон | Текст | Назначение |", "|---|---|---|---|---|"])
    for value, label, bg, fg, note in PRIORITY_RULES:
        lines.append(f"| `{value}` | {label} | `{bg}` | `{fg}` | {note} |")

    lines.extend(["", "## Базовое оформление", "", "| Область | Действие | Примечание |", "|---|---|---|"])
    for sheet, target, action, note in BASE_RULES:
        lines.append(f"| {sheet}: {target} | {action} | {note} |")

    lines.extend([
        "",
        "## Как применять",
        "",
        "1. Настроить листы по `google-sheet-tabs-plan.md`.",
        "2. Настроить выпадающие списки по `google-sheet-validation-plan.md`.",
        "3. Добавить условное форматирование для колонок `Статус` и `Приоритет`.",
        "4. Проверить, что технические листы не мешают сотрудникам.",
        "",
        "## Ограничение",
        "",
        "План не применяет форматирование автоматически. Он фиксирует правила для ручной настройки закрытой Google Таблицы.",
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
