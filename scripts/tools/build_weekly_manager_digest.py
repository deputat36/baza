"""
Сборка еженедельного дайджеста менеджера.

Дайджест собирает управленческую картину из уже созданных отчетов:
GO/NO-GO, решение запуска, метрики использования, план улучшений,
очередь предложений и актуальность данных.

Запуск из корня репозитория:
python scripts/tools/build_weekly_manager_digest.py
"""

from pathlib import Path
import csv

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

OUTPUT_MD = BUILD_DIR / "weekly-manager-digest.md"
OUTPUT_CSV = BUILD_DIR / "weekly-manager-digest.csv"

SOURCES = {
    "go_no_go": BUILD_DIR / "go-no-go-report.csv",
    "launch_decision": BUILD_DIR / "launch-decision-log.csv",
    "usage_metrics": BUILD_DIR / "usage-metrics-report.csv",
    "adoption_plan": BUILD_DIR / "adoption-improvement-plan.csv",
    "change_requests": BUILD_DIR / "change-request-report.csv",
    "freshness": BUILD_DIR / "data-freshness-report.csv",
}

OPEN_STATUSES = {"NEW", "OPEN", "CHECK", "DRAFT", "PENDING", "IN_PROGRESS", "WARN"}
DONE_STATUSES = {"DONE", "CLOSED", "READY", "OK", "RESOLVED", "COMPLETE", "COMPLETED"}
RISK_STATUSES = {"BLOCKER", "WARN", "CHECK", "DRAFT", "PENDING", "EXPIRED", "HIGH"}


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def first_existing(row, names):
    for name in names:
        if name in row and str(row[name]).strip():
            return str(row[name]).strip()
    return ""


def normalized(value):
    return str(value or "").strip().upper()


def count_by_status(rows, fields, statuses):
    count = 0
    for row in rows:
        value = normalized(first_existing(row, fields))
        if value in statuses:
            count += 1
    return count


def count_open(rows):
    count = 0
    for row in rows:
        value = normalized(first_existing(row, ["status", "metric_status", "decision_status", "Статус", "status_current"]))
        if not value:
            continue
        if value in OPEN_STATUSES and value not in DONE_STATUSES:
            count += 1
    return count


def latest_value(rows, fields, default="нет данных"):
    if not rows:
        return default
    value = first_existing(rows[-1], fields)
    return value or default


def add_row(rows, area, metric, value, status, action, source):
    rows.append({
        "area": area,
        "metric": metric,
        "value": str(value),
        "status": status,
        "action": action,
        "source": source,
    })


def build_rows():
    go_no_go = read_csv(SOURCES["go_no_go"])
    launch_decision = read_csv(SOURCES["launch_decision"])
    usage_metrics = read_csv(SOURCES["usage_metrics"])
    adoption_plan = read_csv(SOURCES["adoption_plan"])
    change_requests = read_csv(SOURCES["change_requests"])
    freshness = read_csv(SOURCES["freshness"])

    rows = []

    blockers = count_by_status(go_no_go, ["decision_impact", "impact", "status"], {"BLOCKER"})
    add_row(
        rows,
        "Запуск",
        "Блокеры GO/NO-GO",
        blockers,
        "WARN" if blockers else "OK",
        "Разобрать блокеры до расширения использования" if blockers else "Контролировать новые блокеры",
        SOURCES["go_no_go"].name,
    )

    decision = latest_value(launch_decision, ["decision", "Решение"])
    decision_status = latest_value(launch_decision, ["decision_status", "status", "Статус"], "PENDING")
    add_row(
        rows,
        "Решение",
        "Последнее решение запуска",
        decision,
        normalized(decision_status) or "PENDING",
        "Проверить дату следующего решения и условия запуска",
        SOURCES["launch_decision"].name,
    )

    usage_warn = count_by_status(usage_metrics, ["metric_status", "status", "Статус"], {"WARN", "CHECK"})
    add_row(
        rows,
        "Использование",
        "Метрики со статусом WARN/CHECK",
        usage_warn,
        "WARN" if usage_warn else "OK",
        "Назначить действия по слабым метрикам" if usage_warn else "Продолжить сбор метрик",
        SOURCES["usage_metrics"].name,
    )

    adoption_open = count_open(adoption_plan)
    add_row(
        rows,
        "Улучшения",
        "Открытые действия плана улучшений",
        adoption_open,
        "CHECK" if adoption_open else "OK",
        "Назначить ответственных и сроки по открытым действиям" if adoption_open else "Добавлять новые действия по обратной связи",
        SOURCES["adoption_plan"].name,
    )

    requests_open = count_open(change_requests)
    add_row(
        rows,
        "Предложения",
        "Открытые предложения сотрудников",
        requests_open,
        "CHECK" if requests_open else "OK",
        "Разобрать очередь предложений на еженедельной проверке" if requests_open else "Продолжить принимать предложения",
        SOURCES["change_requests"].name,
    )

    freshness_risk = count_by_status(
        freshness,
        ["freshness_status", "status", "Статус", "check_status"],
        RISK_STATUSES,
    )
    add_row(
        rows,
        "Актуальность",
        "Разделы, требующие проверки актуальности",
        freshness_risk,
        "WARN" if freshness_risk else "OK",
        "Проверить контакты, инструкции и правила с риск-статусом" if freshness_risk else "Сохранить текущий ритм проверки",
        SOURCES["freshness"].name,
    )

    missing_sources = [path.name for path in SOURCES.values() if not path.exists()]
    add_row(
        rows,
        "Сборка",
        "Не найденные источники дайджеста",
        len(missing_sources),
        "CHECK" if missing_sources else "OK",
        "Перед дайджестом запустить `make preflight`" if missing_sources else "Все источники дайджеста найдены",
        ", ".join(missing_sources) if missing_sources else "build/",
    )

    return rows


def build_markdown(rows):
    risky = [row for row in rows if normalized(row["status"]) not in {"OK", "READY", "DONE"}]

    lines = [
        "# Еженедельный дайджест менеджера",
        "",
        "## Назначение",
        "",
        "Дайджест собирает в один файл состояние запуска, использования базы, плана улучшений, предложений сотрудников и актуальности данных.",
        "",
        "## Сводка",
        "",
        "| Блок | Метрика | Значение | Статус | Действие | Источник |",
        "|---|---|---:|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['area']} | {row['metric']} | {row['value']} | {row['status']} | {row['action']} | `{row['source']}` |"
        )

    lines.extend(["", "## Приоритеты недели", ""])
    if not risky:
        lines.append("Критичных отклонений по дайджесту нет. Нужно продолжать регулярный сбор метрик и предложений.")
    else:
        for row in risky:
            lines.append(f"- {row['area']}: {row['action']}.")

    lines.extend([
        "",
        "## Рекомендуемый порядок проверки",
        "",
        "1. Открыть `go-no-go-report.md` и проверить блокеры.",
        "2. Открыть `launch-decision-log.md` и сверить решение запуска.",
        "3. Открыть `usage-metrics-report.md` и посмотреть слабые метрики.",
        "4. Открыть `adoption-improvement-plan.md` и назначить ответственных.",
        "5. Открыть `change-request-report.md` и разобрать предложения сотрудников.",
        "6. Открыть `data-freshness-report.md` и проверить рискованные разделы.",
        "",
        "## Ограничение",
        "",
        "Дайджест не подтверждает юридическую точность данных и актуальность реальных контактов. Он нужен для регулярного управленческого контроля.",
        "Реальные рабочие данные должны храниться только в закрытой Google Таблице.",
        "",
    ])

    return "\n".join(lines)


def write_csv(rows):
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = ["area", "metric", "value", "status", "action", "source"]
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
