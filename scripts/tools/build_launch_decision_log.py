"""
Сборка журнала решения запуска.

GO/NO-GO отчет рассчитывает блокеры. Этот журнал фиксирует управленческое
решение: кто его принял, на каком основании и с какими условиями.

Запуск из корня репозитория:
python scripts/tools/build_launch_decision_log.py
"""

from pathlib import Path
import csv

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

SOURCE_FILE = ROOT / "data" / "drafts" / "launch-decision-log.csv"
GO_NO_GO_CSV = BUILD_DIR / "go-no-go-report.csv"
OUTPUT_MD = BUILD_DIR / "launch-decision-log.md"
OUTPUT_CSV = BUILD_DIR / "launch-decision-log.csv"

FINAL_DECISIONS = {"GO", "NO-GO", "POSTPONED"}


def clean(value):
    return str(value or "").strip()


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def count_go_no_go_blockers():
    rows = read_csv(GO_NO_GO_CSV)
    return sum(1 for row in rows if clean(row.get("decision_impact")) == "BLOCKER")


def decision_status(row):
    decision = clean(row.get("Решение")).upper()
    status = clean(row.get("Статус")).upper()
    if decision in FINAL_DECISIONS and status in {"READY", "DONE", "APPROVED", "CLOSED"}:
        return "FINAL"
    if decision == "PENDING" or status in {"DRAFT", "CHECK", ""}:
        return "PENDING"
    return "CHECK"


def build_rows():
    rows = []
    blockers = count_go_no_go_blockers()
    for row in read_csv(SOURCE_FILE):
        item = {
            "id": clean(row.get("ID")),
            "date": clean(row.get("Дата")),
            "version": clean(row.get("Версия")),
            "decision": clean(row.get("Решение")),
            "decider": clean(row.get("Кто принял")),
            "basis": clean(row.get("Основание")),
            "report": clean(row.get("Связанный отчет")),
            "conditions": clean(row.get("Условия запуска")),
            "open_blockers": clean(row.get("Открытые блокеры")) or str(blockers),
            "next_review": clean(row.get("Следующая проверка")),
            "status": clean(row.get("Статус")),
            "decision_status": decision_status(row),
            "comment": clean(row.get("Комментарий")),
        }
        rows.append(item)
    return rows


def build_markdown(rows):
    final_rows = [row for row in rows if row["decision_status"] == "FINAL"]
    pending_rows = [row for row in rows if row["decision_status"] != "FINAL"]
    latest = rows[-1] if rows else None

    lines = [
        "# Журнал решения запуска",
        "",
        "## Назначение",
        "",
        "Этот файл фиксирует управленческое решение по запуску базы знаний после проверки GO/NO-GO.",
        "",
        "## Сводка",
        "",
        f"- Всего записей: {len(rows)}",
        f"- Финальных решений: {len(final_rows)}",
        f"- Требуют проверки: {len(pending_rows)}",
        "",
    ]

    if latest:
        lines.extend([
            "## Последняя запись",
            "",
            f"- ID: `{latest['id']}`",
            f"- Версия: `{latest['version']}`",
            f"- Решение: `{latest['decision']}`",
            f"- Кто принял: {latest['decider']}",
            f"- Статус решения: {latest['decision_status']}",
            f"- Открытые блокеры по GO/NO-GO: {latest['open_blockers']}",
            "",
        ])

    lines.extend([
        "## Все записи",
        "",
        "| ID | Дата | Версия | Решение | Кто принял | Статус | Блокеры | Следующая проверка |",
        "|---|---|---|---|---|---|---:|---|",
    ])

    for row in rows:
        lines.append(
            f"| {row['id']} | {row['date']} | {row['version']} | {row['decision']} | {row['decider']} | {row['decision_status']} | {row['open_blockers']} | {row['next_review']} |"
        )

    lines.extend([
        "",
        "## Правило фиксации",
        "",
        "Решение считается финальным только если поле `Решение` равно `GO`, `NO-GO` или `POSTPONED`, а статус записи закрыт как готовый или утвержденный.",
        "",
        "## Ограничение",
        "",
        "Журнал фиксирует управленческое решение. Он не заменяет юридическую проверку, проверку реальных контактов и ручную приемку закрытой Google Таблицы.",
        "",
    ])
    return "\n".join(lines)


def write_csv(rows):
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "id",
            "date",
            "version",
            "decision",
            "decider",
            "basis",
            "report",
            "conditions",
            "open_blockers",
            "next_review",
            "status",
            "decision_status",
            "comment",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    rows = build_rows()
    OUTPUT_MD.write_text(build_markdown(rows), encoding="utf-8")
    write_csv(rows)
    print(f"Готово: {OUTPUT_MD.relative_to(ROOT)}")
    print(f"Готово: {OUTPUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
