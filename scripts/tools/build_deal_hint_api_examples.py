"""
Генератор примеров payload для будущего интерфейса подсказок сделки.

Скрипт не подключается к Навигатору сделок. Он собирает безопасные примеры
того, какие признаки сделки может передать будущий интерфейс и какой ответ
с подсказками можно получить из базы знаний.

Запуск:
python scripts/tools/build_knowledge_index.py
python scripts/tools/build_deal_hint_rules.py
python scripts/tools/build_deal_hint_api_examples.py
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

SCENARIOS_FILE = ROOT / "data" / "drafts" / "deal-hint-scenarios.csv"
KNOWLEDGE_INDEX_FILE = BUILD_DIR / "knowledge-index.json"
RULES_FILE = BUILD_DIR / "deal-hint-rules.json"
OUTPUT_JSON = BUILD_DIR / "deal-hint-api-examples.json"
OUTPUT_MD = BUILD_DIR / "deal-hint-api-examples.md"
OUTPUT_CSV = BUILD_DIR / "deal-hint-api-examples.csv"
SCHEMA_VERSION = "deal-hint-api-examples-v1"


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def split_list(value: Any) -> list[str]:
    text = clean(value)
    if not text:
        return []
    return [part.strip() for part in text.replace(",", ";").split(";") if part.strip()]


def parse_signals(value: Any) -> dict[str, str]:
    signals = {}
    for part in split_list(value):
        if "=" not in part:
            continue
        key, raw_value = part.split("=", 1)
        signals[clean(key)] = clean(raw_value)
    return signals


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Файл не найден: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Файл не найден: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_knowledge_records() -> dict[str, dict[str, Any]]:
    data = read_json(KNOWLEDGE_INDEX_FILE)
    return {clean(record.get("id")): record for record in data.get("records", []) if clean(record.get("id"))}


def load_rules() -> list[dict[str, Any]]:
    data = read_json(RULES_FILE)
    return data.get("rules", [])


def rule_matches(rule: dict[str, Any], signals: dict[str, str]) -> bool:
    signal = clean(rule.get("signal"))
    value = clean(rule.get("value"))
    return signal in signals and clean(signals.get(signal)) == value


def build_hint(rule: dict[str, Any], knowledge_records: dict[str, dict[str, Any]]):
    linked_records = []
    for knowledge_id in rule.get("knowledge_ids", []):
        record = knowledge_records.get(clean(knowledge_id), {})
        linked_records.append({
            "id": clean(knowledge_id),
            "title": clean(record.get("title")),
            "sheet": clean(record.get("sheet")),
            "status": clean(record.get("status")),
            "source": clean(record.get("source")),
        })

    return {
        "rule_id": clean(rule.get("id")),
        "title": clean(rule.get("title")),
        "priority": clean(rule.get("priority")),
        "audience": rule.get("audience", []),
        "signal": clean(rule.get("signal")),
        "value": clean(rule.get("value")),
        "linked_records": linked_records,
    }


def build_examples():
    knowledge_records = load_knowledge_records()
    rules = load_rules()
    scenarios = read_csv(SCENARIOS_FILE)
    examples = []

    for scenario in scenarios:
        scenario_id = clean(scenario.get("ID"))
        signals = parse_signals(scenario.get("Сигналы"))
        matched_rules = [rule for rule in rules if rule_matches(rule, signals)]
        hints = [build_hint(rule, knowledge_records) for rule in matched_rules]

        examples.append({
            "scenario_id": scenario_id,
            "scenario_title": clean(scenario.get("Название сценария")),
            "request": {
                "deal_context": {
                    "source": "safe_test_scenario",
                    "scenario_id": scenario_id,
                    "signals": signals,
                    "audience": split_list(scenario.get("Кому полезно")),
                }
            },
            "response": {
                "matched_rules": [clean(rule.get("id")) for rule in matched_rules],
                "hints": hints,
            },
        })

    return examples


def write_outputs(examples):
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Safe examples of future deal hint request and response payloads.",
        "sources": {
            "scenarios": SCENARIOS_FILE.relative_to(ROOT).as_posix(),
            "rules": RULES_FILE.relative_to(ROOT).as_posix(),
            "knowledge_index": KNOWLEDGE_INDEX_FILE.relative_to(ROOT).as_posix(),
        },
        "examples_count": len(examples),
        "examples": examples,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Примеры payload подсказок сделки",
        "",
        "## Сводка",
        "",
        f"- Примеров: {len(examples)}",
        f"- JSON: `{OUTPUT_JSON.relative_to(ROOT).as_posix()}`",
        "",
        "## Примеры",
        "",
        "| Сценарий | Сигналы | Правила | Подсказок |",
        "|---|---|---|---|",
    ]
    for example in examples:
        signals = "; ".join(f"{key}={value}" for key, value in example["request"]["deal_context"]["signals"].items())
        rule_ids = "; ".join(example["response"]["matched_rules"])
        lines.append(
            f"| {example['scenario_id']} {example['scenario_title']} | {signals} | {rule_ids or '-'} | {len(example['response']['hints'])} |"
        )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["scenario_id", "scenario_title", "signals", "audience", "matched_rules", "hints_count"])
        for example in examples:
            context = example["request"]["deal_context"]
            signals = "; ".join(f"{key}={value}" for key, value in context["signals"].items())
            writer.writerow([
                example["scenario_id"],
                example["scenario_title"],
                signals,
                "; ".join(context["audience"]),
                "; ".join(example["response"]["matched_rules"]),
                len(example["response"]["hints"]),
            ])


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    examples = build_examples()
    write_outputs(examples)

    print(f"Готово: {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"Готово: {OUTPUT_MD.relative_to(ROOT)}")
    print(f"Готово: {OUTPUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
