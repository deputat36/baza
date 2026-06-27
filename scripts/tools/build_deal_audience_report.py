"""
Отчёт по аудиториям будущих подсказок сделки.

Проверяет, что роли из правил подсказок и безопасных сценариев есть
в контролируемом словаре data/dictionaries/deal-audiences.csv.

Запуск:
python scripts/tools/build_deal_audience_report.py
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

AUDIENCES_FILE = ROOT / "data" / "dictionaries" / "deal-audiences.csv"
RULES_FILE = ROOT / "data" / "drafts" / "deal-hint-rules.csv"
SCENARIOS_FILE = ROOT / "data" / "drafts" / "deal-hint-scenarios.csv"
REPORT_MD = BUILD_DIR / "deal-audience-report.md"
REPORT_CSV = BUILD_DIR / "deal-audience-report.csv"


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def split_list(value: Any) -> list[str]:
    text = clean(value)
    if not text:
        return []
    return [part.strip() for part in text.replace(",", ";").split(";") if part.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Файл не найден: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def load_audiences() -> dict[str, dict[str, str]]:
    rows = read_csv(AUDIENCES_FILE)
    audiences = {}
    for row in rows:
        audience = clean(row.get("Аудитория"))
        if audience:
            audiences[audience] = {key: clean(value) for key, value in row.items() if key}
    return audiences


def collect_usage(rows: list[dict[str, str]], id_column: str, audience_column: str):
    usage = defaultdict(list)
    for row_number, row in enumerate(rows, start=2):
        row_id = clean(row.get(id_column)) or f"строка {row_number}"
        for audience in split_list(row.get(audience_column)):
            usage[audience].append(row_id)
    return usage


def write_outputs(audiences, rule_usage, scenario_usage, problems):
    all_used = set(rule_usage) | set(scenario_usage)
    unused = sorted(set(audiences) - all_used)

    lines = [
        "# Отчёт по аудиториям подсказок",
        "",
        "## Сводка",
        "",
        f"- Аудиторий в словаре: {len(audiences)}",
        f"- Используются в правилах: {len(rule_usage)}",
        f"- Используются в сценариях: {len(scenario_usage)}",
        f"- Неиспользуемых аудиторий: {len(unused)}",
        f"- Ошибок: {len(problems)}",
        "",
        "## Ошибки",
        "",
    ]
    if problems:
        lines.extend(f"- {problem}" for problem in problems)
    else:
        lines.append("Ошибок не найдено.")

    lines.extend(["", "## Покрытие", "", "| Аудитория | В правилах | В сценариях | Статус |", "|---|---|---|---|"])
    for audience in sorted(audiences):
        lines.append(
            f"| {audience} | {'; '.join(rule_usage.get(audience, [])) or '-'} | {'; '.join(scenario_usage.get(audience, [])) or '-'} | {audiences[audience].get('Статус', '')} |"
        )

    if unused:
        lines.extend(["", "## Неиспользуемые аудитории", ""])
        lines.extend(f"- {audience}" for audience in unused)

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["audience", "rule_ids", "scenario_ids", "status", "role_name"])
        for audience in sorted(audiences):
            writer.writerow([
                audience,
                "; ".join(rule_usage.get(audience, [])),
                "; ".join(scenario_usage.get(audience, [])),
                audiences[audience].get("Статус", ""),
                audiences[audience].get("Название роли", ""),
            ])


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    audiences = load_audiences()
    rules = read_csv(RULES_FILE)
    scenarios = read_csv(SCENARIOS_FILE)

    rule_usage = collect_usage(rules, "ID", "Кому показывать")
    scenario_usage = collect_usage(scenarios, "ID", "Кому полезно")

    known = set(audiences)
    problems = []
    for audience in sorted(set(rule_usage) - known):
        problems.append(f"Неизвестная аудитория в правилах: {audience}")
    for audience in sorted(set(scenario_usage) - known):
        problems.append(f"Неизвестная аудитория в сценариях: {audience}")

    write_outputs(audiences, rule_usage, scenario_usage, problems)

    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")

    if problems:
        print("\nНайдены ошибки аудиторий:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
