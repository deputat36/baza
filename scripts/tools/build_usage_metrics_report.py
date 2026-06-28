"""
Сборка отчета по использованию базы после запуска.

Отчет показывает, пользуются ли сотрудники базой, где есть запросы без
результата и какие метрики требуют внимания менеджера.

Запуск из корня репозитория:
python scripts/tools/build_usage_metrics_report.py
"""

from pathlib import Path
import csv
from collections import defaultdict

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

SOURCE_FILE = ROOT / "data" / "drafts" / "usage-metrics-log.csv"
OUTPUT_MD = BUILD_DIR / "usage-metrics-report.md"
OUTPUT_CSV = BUILD_DIR / "usage-metrics-report.csv"


def clean(value):
    return str(value or "").strip()


def to_number(value):
    try:
        return float(clean(value).replace(",", "."))
    except ValueError:
        return 0.0


def read_rows():
    if not SOURCE_FILE.exists():
        return []
    with SOURCE_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def classify_metric(row):
    value = to_number(row.get("Значение"))
    target = to_number(row.get("Цель"))
    metric = clean(row.get("Показатель")).lower()

    if not target:
        return "CHECK"

    if "без результата" in metric:
        if value <= target:
            return "OK"
        return "WARN"

    if value >= target:
        return "OK"
    if value > 0:
        return "CHECK"
    return "WARN"


def build_rows():
    rows = []
    for row in read_rows():
        value = to_number(row.get("Значение"))
        target = to_number(row.get("Цель"))
        gap = value - target
        rows.append({
            "id": clean(row.get("ID")),
            "period": clean(row.get("Период")),
            "role": clean(row.get("Роль")),
            "metric": clean(row.get("Показатель")),
            "value": clean(row.get("Значение")),
            "target": clean(row.get("Цель")),
            "gap": f"{gap:g}",
            "source": clean(row.get("Источник")),
            "status": clean(row.get("Статус")),
            "metric_status": classify_metric(row),
            "comment": clean(row.get("Комментарий")),
        })
    return rows


def summarize_by_role(rows):
    summary = defaultdict(lambda: {"total": 0, "ok": 0, "check": 0, "warn": 0})
    for row in rows:
        item = summary[row["role"]]
        item["total"] += 1
        item[row["metric_status"].lower()] += 1
    return summary


def build_markdown(rows):
    warn_rows = [row for row in rows if row["metric_status"] == "WARN"]
    check_rows = [row for row in rows if row["metric_status"] == "CHECK"]
    ok_rows = [row for row in rows if row["metric_status"] == "OK"]
    role_summary = summarize_by_role(rows)

    lines = [
        "# Отчет по использованию базы",
        "",
        "## Назначение",
        "",
        "Этот отчет показывает, используется ли база знаний после запуска и какие показатели требуют внимания.",
        "",
        "## Сводка",
        "",
        f"- Всего метрик: {len(rows)}",
        f"- OK: {len(ok_rows)}",
        f"- CHECK: {len(check_rows)}",
        f"- WARN: {len(warn_rows)}",
        "",
        "## По ролям",
        "",
        "| Роль | Всего | OK | CHECK | WARN |",
        "|---|---:|---:|---:|---:|",
    ]

    for role, data in sorted(role_summary.items()):
        lines.append(f"| {role} | {data['total']} | {data['ok']} | {data['check']} | {data['warn']} |")

    lines.extend(["", "## Метрики с вниманием", ""])
    attention = warn_rows + check_rows
    if not attention:
        lines.append("Метрик, требующих внимания, нет.")
    else:
        lines.extend([
            "| ID | Период | Роль | Показатель | Значение | Цель | Статус | Источник |",
            "|---|---|---|---|---:|---:|---|---|",
        ])
        for row in attention:
            lines.append(
                f"| {row['id']} | {row['period']} | {row['role']} | {row['metric']} | {row['value']} | {row['target']} | {row['metric_status']} | {row['source']} |"
            )

    lines.extend([
        "",
        "## Как использовать",
        "",
        "Если `Запросы без результата` растут, нужно добавить синонимы, новые ситуации или недостающие контакты.",
        "Если активных пользователей мало, нужно повторить обучение и упростить стартовую навигацию.",
        "",
        "## Ограничение",
        "",
        "Публичный репозиторий хранит только шаблон метрик. Реальные значения должны переноситься из закрытой Google Таблицы или внутреннего инструмента без клиентских данных.",
        "",
    ])
    return "\n".join(lines)


def write_csv(rows):
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "id",
            "period",
            "role",
            "metric",
            "value",
            "target",
            "gap",
            "source",
            "status",
            "metric_status",
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
