"""
Предпросмотр будущих подсказок сделки.

Скрипт применяет deal-hint-rules.json к безопасным тестовым сценариям и
показывает, какие правила сработали. Он не подключается к Навигатору сделок
и не использует реальные сделки.

Запуск:
python scripts/tools/build_knowledge_index.py
python scripts/tools/build_deal_hint_rules.py
python scripts/tools/build_deal_hint_preview.py
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

SCENARIOS_FILE = ROOT / "data" / "drafts" / "deal-hint-scenarios.csv"
RULES_JSON = BUILD_DIR / "deal-hint-rules.json"
OUTPUT_JSON = BUILD_DIR / "deal-hint-preview.json"
REPORT_MD = BUILD_DIR / "deal-hint-preview.md"
REPORT_CSV = BUILD_DIR / "deal-hint-preview.csv"


def clean(value: Any) -> str:
    return str(value or "").strip()


def split_list(value: Any) -> list[str]:
    text = clean(value)
    if not text:
        return []
    return [part.strip() for part in text.replace(",", ";").split(";") if part.strip()]


def parse_pairs(value: Any) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for item in split_list(value):
        if "=" not in item:
            continue
        key, raw_value = item.split("=", 1)
        signal = clean(key)
        signal_value = clean(raw_value)
        if signal and signal_value:
            result.setdefault(signal, set()).add(signal_value)
    return result


def read_csv(path: Path):
    if not path.exists():
        raise SystemExit(f"Файл не найден: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def load_rules():
    if not RULES_JSON.exists():
        raise SystemExit(f"Сначала соберите {RULES_JSON.relative_to(ROOT)}")
    data = json.loads(RULES_JSON.read_text(encoding="utf-8"))
    return data.get("rules", [])


def rule_matches(rule: dict, signals: dict[str, set[str]]) -> bool:
    signal = clean(rule.get("signal"))
    value = clean(rule.get("value"))
    return bool(signal and value and value in signals.get(signal, set()))


def build_preview():
    rules = load_rules()
    rules_by_id = {clean(rule.get("id")): rule for rule in rules if clean(rule.get("id"))}
    scenarios = []
    problems = []

    for row_number, row in enumerate(read_csv(SCENARIOS_FILE), start=2):
        scenario_id = clean(row.get("ID"))
        signals = parse_pairs(row.get("Сигналы"))
        expected = split_list(row.get("Ожидаемые правила"))
        matched_rules = [rule for rule in rules if rule_matches(rule, signals)]
        matched_ids = [clean(rule.get("id")) for rule in matched_rules]

        missing_expected = [rule_id for rule_id in expected if rule_id not in matched_ids]
        unexpected = [rule_id for rule_id in matched_ids if rule_id not in expected]
        unknown_expected = [rule_id for rule_id in expected if rule_id not in rules_by_id]

        for rule_id in missing_expected:
            problems.append(f"{scenario_id}: ожидалось правило {rule_id}, но оно не сработало")
        for rule_id in unexpected:
            problems.append(f"{scenario_id}: сработало неожиданное правило {rule_id}")
        for rule_id in unknown_expected:
            problems.append(f"{scenario_id}: ожидаемое правило не найдено: {rule_id}")

        scenarios.append({
            "id": scenario_id,
            "title": clean(row.get("Название сценария")),
            "signals": {key: sorted(values) for key, values in signals.items()},
            "expected_rule_ids": expected,
            "matched_rule_ids": matched_ids,
            "matched_hints": [
                {
                    "rule_id": clean(rule.get("id")),
                    "title": clean(rule.get("title")),
                    "knowledge_ids": rule.get("knowledge_ids", []),
                    "priority": clean(rule.get("priority")),
                    "audience": rule.get("audience", []),
                }
                for rule in matched_rules
            ],
            "audience": split_list(row.get("Кому полезно")),
            "comment": clean(row.get("Комментарий")),
            "row_number": row_number,
        })

    return scenarios, problems


def write_outputs(scenarios, problems):
    data = {
        "schema_version": "deal-hint-preview-v1",
        "source": SCENARIOS_FILE.relative_to(ROOT).as_posix(),
        "rules_source": RULES_JSON.relative_to(ROOT).as_posix(),
        "purpose": "Safe preview of future deal hint matching. No real deal data.",
        "scenarios_count": len(scenarios),
        "problems_count": len(problems),
        "scenarios": scenarios,
    }
    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Предпросмотр подсказок сделки",
        "",
        "## Сводка",
        "",
        f"- Сценариев: {len(scenarios)}",
        f"- Ошибок ожиданий: {len(problems)}",
        "",
        "## Ошибки",
        "",
    ]
    if problems:
        lines.extend(f"- {problem}" for problem in problems)
    else:
        lines.append("Ошибок ожиданий не найдено.")

    lines.extend(["", "## Сценарии", "", "| ID | Сценарий | Сигналы | Сработали правила |", "|---|---|---|---|"])
    for scenario in scenarios:
        signals_text = "; ".join(
            f"{key}={', '.join(values)}" for key, values in scenario["signals"].items()
        )
        lines.append(
            f"| {scenario['id']} | {scenario['title']} | {signals_text} | {'; '.join(scenario['matched_rule_ids'])} |"
        )

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["scenario_id", "scenario_title", "signals", "expected_rule_ids", "matched_rule_ids", "problems"])
        for scenario in scenarios:
            scenario_problems = [problem for problem in problems if problem.startswith(f"{scenario['id']}:")]
            signals_text = "; ".join(
                f"{key}={', '.join(values)}" for key, values in scenario["signals"].items()
            )
            writer.writerow([
                scenario["id"],
                scenario["title"],
                signals_text,
                "; ".join(scenario["expected_rule_ids"]),
                "; ".join(scenario["matched_rule_ids"]),
                " | ".join(scenario_problems),
            ])


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    scenarios, problems = build_preview()
    write_outputs(scenarios, problems)

    print(f"Готово: {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")

    if problems:
        raise SystemExit("В предпросмотре подсказок найдены ошибки ожиданий.")


if __name__ == "__main__":
    main()
