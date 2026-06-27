"""
Отчёт по словарю сигналов сделки.

Показывает, какие сигналы уже используются в правилах подсказок, а какие
только заведены в словаре и ещё не покрыты правилами.

Запуск:
python scripts/tools/build_deal_signal_report.py
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

SIGNALS_FILE = ROOT / "data" / "dictionaries" / "deal-signals.csv"
RULES_FILE = ROOT / "data" / "drafts" / "deal-hint-rules.csv"
REPORT_MD = BUILD_DIR / "deal-signal-report.md"
REPORT_CSV = BUILD_DIR / "deal-signal-report.csv"


def clean(value):
    return str(value or "").strip()


def read_csv(path: Path):
    if not path.exists():
        raise SystemExit(f"Файл не найден: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    signals = read_csv(SIGNALS_FILE)
    rules = read_csv(RULES_FILE)

    rules_by_signal = defaultdict(list)
    for rule in rules:
        signal = clean(rule.get("Сигнал сделки"))
        if signal:
            rules_by_signal[signal].append(rule)

    signal_names = {clean(row.get("Сигнал")) for row in signals if clean(row.get("Сигнал"))}
    rule_signals = set(rules_by_signal)
    unknown_signals = sorted(rule_signals - signal_names)
    unused_signals = sorted(signal_names - rule_signals)

    lines = [
        "# Отчёт по сигналам сделки",
        "",
        "## Сводка",
        "",
        f"- Сигналов в словаре: {len(signal_names)}",
        f"- Сигналов с правилами: {len(rule_signals & signal_names)}",
        f"- Сигналов без правил: {len(unused_signals)}",
        f"- Неизвестных сигналов в правилах: {len(unknown_signals)}",
        "",
        "## Сигналы без правил",
        "",
    ]

    if unused_signals:
        lines.extend(f"- {signal}" for signal in unused_signals)
    else:
        lines.append("Все сигналы словаря покрыты правилами.")

    lines.extend(["", "## Неизвестные сигналы в правилах", ""])
    if unknown_signals:
        lines.extend(f"- {signal}" for signal in unknown_signals)
    else:
        lines.append("Неизвестных сигналов не найдено.")

    lines.extend(["", "## Покрытие", "", "| Сигнал | Тип | Правил | Статус |", "|---|---|---:|---|"])
    for signal in signals:
        name = clean(signal.get("Сигнал"))
        if not name:
            continue
        lines.append(
            f"| {name} | {clean(signal.get('Тип значения'))} | {len(rules_by_signal.get(name, []))} | {clean(signal.get('Статус'))} |"
        )

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["signal", "value_type", "rules_count", "status", "description"])
        for signal in signals:
            name = clean(signal.get("Сигнал"))
            if not name:
                continue
            writer.writerow([
                name,
                clean(signal.get("Тип значения")),
                len(rules_by_signal.get(name, [])),
                clean(signal.get("Статус")),
                clean(signal.get("Описание")),
            ])

    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")

    if unknown_signals:
        raise SystemExit("В правилах найдены сигналы, которых нет в словаре.")


if __name__ == "__main__":
    main()
