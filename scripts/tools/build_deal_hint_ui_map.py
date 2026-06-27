"""
Отчёт по карте размещения будущих подсказок в интерфейсе сделки.

Скрипт проверяет, что каждое правило подсказки связано с допустимой зоной
будущего UI. Навигатор сделок не меняется.

Запуск:
python scripts/tools/build_knowledge_index.py
python scripts/tools/build_deal_hint_rules.py
python scripts/tools/build_deal_hint_ui_map.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

ZONES_FILE = ROOT / "data" / "dictionaries" / "deal-hint-ui-zones.csv"
MAP_FILE = ROOT / "data" / "drafts" / "deal-hint-ui-map.csv"
RULES_JSON = BUILD_DIR / "deal-hint-rules.json"
REPORT_MD = BUILD_DIR / "deal-hint-ui-map-report.md"
REPORT_CSV = BUILD_DIR / "deal-hint-ui-map-report.csv"
OUTPUT_JSON = BUILD_DIR / "deal-hint-ui-map.json"

REQUIRED_MAP_COLUMNS = [
    "ID",
    "Правило подсказки",
    "Зона интерфейса",
    "Порядок",
    "Обязательность",
    "Заголовок в интерфейсе",
    "Статус",
]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Файл не найден: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def read_map_rows() -> list[dict[str, str]]:
    if not MAP_FILE.exists():
        raise SystemExit(f"Файл карты UI не найден: {MAP_FILE.relative_to(ROOT)}")
    with MAP_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = [column for column in REQUIRED_MAP_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"В deal-hint-ui-map.csv нет колонок: {', '.join(missing)}")
        return list(reader)


def load_rules() -> dict[str, dict[str, Any]]:
    if not RULES_JSON.exists():
        raise SystemExit(f"Сначала соберите {RULES_JSON.relative_to(ROOT)}")
    data = json.loads(RULES_JSON.read_text(encoding="utf-8"))
    return {clean(rule.get("id")): rule for rule in data.get("rules", []) if clean(rule.get("id"))}


def load_zones() -> dict[str, dict[str, str]]:
    zones = {}
    for row in read_csv(ZONES_FILE):
        zone = clean(row.get("Зона интерфейса"))
        if zone:
            zones[zone] = {key: clean(value) for key, value in row.items() if key}
    return zones


def build_rows(map_rows, rules, zones):
    rows = []
    problems = []
    seen_ids = set()
    mapped_rules = set()

    for row_number, row in enumerate(map_rows, start=2):
        item_id = clean(row.get("ID"))
        rule_id = clean(row.get("Правило подсказки"))
        zone = clean(row.get("Зона интерфейса"))
        order = clean(row.get("Порядок"))
        required = clean(row.get("Обязательность"))
        title = clean(row.get("Заголовок в интерфейсе"))
        status = clean(row.get("Статус"))

        if not item_id:
            problems.append(f"строка {row_number}: пустой ID")
        elif item_id in seen_ids:
            problems.append(f"{item_id}: дубль ID")
        seen_ids.add(item_id)

        if not rule_id:
            problems.append(f"{item_id}: не указано правило подсказки")
        elif rule_id not in rules:
            problems.append(f"{item_id}: правило не найдено в deal-hint-rules.json: {rule_id}")
        mapped_rules.add(rule_id)

        if not zone:
            problems.append(f"{item_id}: не указана зона интерфейса")
        elif zone not in zones:
            problems.append(f"{item_id}: зона не найдена в deal-hint-ui-zones.csv: {zone}")

        for field_name, value in [("Порядок", order), ("Обязательность", required), ("Заголовок в интерфейсе", title), ("Статус", status)]:
            if not value:
                problems.append(f"{item_id}: пустое поле {field_name}")

        rows.append({
            "id": item_id,
            "rule_id": rule_id,
            "rule_title": clean(rules.get(rule_id, {}).get("title")),
            "signal": clean(rules.get(rule_id, {}).get("signal")),
            "value": clean(rules.get(rule_id, {}).get("value")),
            "zone": zone,
            "zone_title": clean(zones.get(zone, {}).get("Название")),
            "order": order,
            "required": required,
            "ui_title": title,
            "status": status,
            "comment": clean(row.get("Комментарий")),
        })

    missing_rule_ids = sorted(set(rules) - mapped_rules)
    for rule_id in missing_rule_ids:
        problems.append(f"{rule_id}: нет зоны интерфейса в deal-hint-ui-map.csv")

    return rows, problems, missing_rule_ids


def write_outputs(rows, problems, missing_rule_ids, zones):
    data = {
        "schema_version": "deal-hint-ui-map-v1",
        "source": MAP_FILE.relative_to(ROOT).as_posix(),
        "zones_source": ZONES_FILE.relative_to(ROOT).as_posix(),
        "rules_source": RULES_JSON.relative_to(ROOT).as_posix(),
        "purpose": "Draft mapping of future deal hints to UI zones.",
        "items_count": len(rows),
        "zones_count": len(zones),
        "missing_rules_count": len(missing_rule_ids),
        "problems_count": len(problems),
        "items": rows,
    }
    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Отчёт по UI-карте подсказок сделки",
        "",
        "## Сводка",
        "",
        f"- Записей карты: {len(rows)}",
        f"- Зон интерфейса: {len(zones)}",
        f"- Правил без зоны: {len(missing_rule_ids)}",
        f"- Ошибок: {len(problems)}",
        "",
        "## Ошибки",
        "",
    ]
    if problems:
        lines.extend(f"- {problem}" for problem in problems)
    else:
        lines.append("Ошибок не найдено.")

    lines.extend([
        "",
        "## Карта",
        "",
        "| Правило | Сигнал | Зона | Обязательность | Заголовок |",
        "|---|---|---|---|---|",
    ])
    for row in rows:
        lines.append(
            f"| {row['rule_id']} | {row['signal']}={row['value']} | {row['zone']} | {row['required']} | {row['ui_title']} |"
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "id",
            "rule_id",
            "rule_title",
            "signal",
            "value",
            "zone",
            "zone_title",
            "order",
            "required",
            "ui_title",
            "status",
            "comment",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    rules = load_rules()
    zones = load_zones()
    rows, problems, missing_rule_ids = build_rows(read_map_rows(), rules, zones)
    write_outputs(rows, problems, missing_rule_ids, zones)

    print(f"Готово: {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")

    if problems:
        print("\nНайдены ошибки UI-карты подсказок:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
