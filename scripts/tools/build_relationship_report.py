"""
Отчёт по связям между записями базы знаний.

Использует build/knowledge-index.json и показывает:
- сколько связей найдено;
- какие связанные ID отсутствуют в индексе;
- какие записи не имеют входящих связей;
- какие записи ссылаются на другие записи.

Запуск:
python scripts/tools/build_knowledge_index.py
python scripts/tools/build_relationship_report.py
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

INDEX_FILE = BUILD_DIR / "knowledge-index.json"
REPORT_MD = BUILD_DIR / "relationship-report.md"
REPORT_CSV = BUILD_DIR / "relationship-report.csv"


def load_index():
    if not INDEX_FILE.exists():
        raise SystemExit(f"Сначала соберите {INDEX_FILE.relative_to(ROOT)}")
    return json.loads(INDEX_FILE.read_text(encoding="utf-8"))


def collect_edges(records):
    edges = []
    for record in records:
        source_id = record.get("id")
        for field, targets in (record.get("related") or {}).items():
            for target_id in targets:
                edges.append({
                    "source_id": source_id,
                    "source_title": record.get("title", ""),
                    "field": field,
                    "target_id": target_id,
                })
    return edges


def build_report(data):
    records = data.get("records", [])
    by_id = {record.get("id"): record for record in records if record.get("id")}
    edges = collect_edges(records)

    incoming = defaultdict(list)
    outgoing = defaultdict(list)
    missing = []

    for edge in edges:
        outgoing[edge["source_id"]].append(edge)
        if edge["target_id"] in by_id:
            incoming[edge["target_id"]].append(edge)
        else:
            missing.append(edge)

    isolated = [
        record for record in records
        if not incoming.get(record.get("id")) and not outgoing.get(record.get("id"))
    ]

    lines = [
        "# Отчёт по связям базы знаний",
        "",
        "## Сводка",
        "",
        f"- Записей в индексе: {len(records)}",
        f"- Связей между ID: {len(edges)}",
        f"- Отсутствующих связанных ID: {len(missing)}",
        f"- Записей без входящих и исходящих связей: {len(isolated)}",
        "",
        "## Отсутствующие связанные ID",
        "",
    ]

    if missing:
        lines.append("| Источник | Поле | Не найден ID |")
        lines.append("|---|---|---|")
        for edge in missing:
            lines.append(f"| {edge['source_id']} | {edge['field']} | {edge['target_id']} |")
    else:
        lines.append("Отсутствующих связанных ID не найдено.")

    lines.extend(["", "## Записи без связей", ""])
    if isolated:
        lines.append("| ID | Раздел | Название |")
        lines.append("|---|---|---|")
        for record in isolated[:100]:
            lines.append(f"| {record.get('id')} | {record.get('sheet')} | {record.get('title')} |")
        if len(isolated) > 100:
            lines.append(f"\nПоказаны первые 100 из {len(isolated)} записей.")
    else:
        lines.append("Записей без связей не найдено.")

    return "\n".join(lines) + "\n", edges, missing, isolated


def write_csv(edges, missing):
    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["source_id", "source_title", "field", "target_id", "target_exists"])
        missing_keys = {(edge["source_id"], edge["field"], edge["target_id"]) for edge in missing}
        for edge in edges:
            key = (edge["source_id"], edge["field"], edge["target_id"])
            writer.writerow([
                edge["source_id"],
                edge["source_title"],
                edge["field"],
                edge["target_id"],
                "no" if key in missing_keys else "yes",
            ])


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    data = load_index()
    markdown, edges, missing, _isolated = build_report(data)
    REPORT_MD.write_text(markdown, encoding="utf-8")
    write_csv(edges, missing)
    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
