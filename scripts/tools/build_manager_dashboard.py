"""
Управленческая сводка по базе знаний.

Скрипт собирает короткий dashboard из уже созданных отчётов build/*.csv.
Он должен запускаться после отчётов готовности, актуальности, очереди изменений,
ответственности за разделы и интеграционных проверок.

Результаты:
- build/manager-dashboard.md
- build/manager-dashboard.csv
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

REPORT_MD = BUILD_DIR / "manager-dashboard.md"
REPORT_CSV = BUILD_DIR / "manager-dashboard.csv"

INPUTS = {
    "readiness": BUILD_DIR / "launch-readiness-report.csv",
    "freshness": BUILD_DIR / "data-freshness-report.csv",
    "change_requests": BUILD_DIR / "change-request-report.csv",
    "missing": BUILD_DIR / "missing-values-report.csv",
    "integration_access": BUILD_DIR / "integration-access-report.csv",
    "integration_contracts": BUILD_DIR / "integration-contract-report.csv",
    "ownership": BUILD_DIR / "section-ownership-report.csv",
}


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def count_by(rows: list[dict[str, str]], column: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = clean(row.get(column)) or "EMPTY"
        counts[value] = counts.get(value, 0) + 1
    return counts


def int_value(value: Any) -> int:
    try:
        return int(float(clean(value).replace(",", ".")))
    except ValueError:
        return 0


def metric(metrics: list[dict[str, str]], section: str, name: str, value: Any, level: str, comment: str):
    metrics.append({
        "section": section,
        "metric": name,
        "value": str(value),
        "level": level,
        "comment": comment,
    })


def build_metrics():
    metrics: list[dict[str, str]] = []
    actions: list[str] = []
    missing_inputs = [name for name, path in INPUTS.items() if not path.exists()]

    if missing_inputs:
        metric(
            metrics,
            "Сборка",
            "Недостающие входные отчёты",
            len(missing_inputs),
            "WARN",
            ", ".join(missing_inputs),
        )
        actions.append("Проверить порядок запуска preflight: dashboard должен строиться после детальных отчётов.")

    readiness_rows = read_csv(INPUTS["readiness"])
    readiness_counts = count_by(readiness_rows, "Статус")
    ready = readiness_counts.get("READY", 0)
    check = readiness_counts.get("CHECK", 0)
    draft = readiness_counts.get("DRAFT", 0)
    metric(metrics, "Готовность", "READY разделов", ready, "OK" if ready else "WARN", "Технически готовые листы")
    metric(metrics, "Готовность", "CHECK разделов", check, "WARN" if check else "OK", "Нужна ручная проверка")
    metric(metrics, "Готовность", "DRAFT разделов", draft, "WARN" if draft else "OK", "Черновые или пустые разделы")
    if check or draft:
        actions.append("Разобрать `launch-readiness-report.md`: закрыть CHECK и DRAFT по ключевым разделам.")

    freshness_rows = read_csv(INPUTS["freshness"])
    freshness_counts = count_by(freshness_rows, "freshness_state")
    never_checked = freshness_counts.get("NEVER_CHECKED", 0)
    overdue = freshness_counts.get("OVERDUE", 0)
    due_soon = freshness_counts.get("DUE_SOON", 0)
    metric(metrics, "Актуальность", "Не проверялись", never_checked, "WARN" if never_checked else "OK", "Нет даты последней проверки")
    metric(metrics, "Актуальность", "Просрочены", overdue, "WARN" if overdue else "OK", "Срок повторной проверки прошёл")
    metric(metrics, "Актуальность", "Скоро проверить", due_soon, "WARN" if due_soon else "OK", "Срок проверки приближается")
    if never_checked or overdue or due_soon:
        actions.append("Назначить проверку разделов из `data-freshness-report.md`, начиная с контактов и юридических инструкций.")

    ownership_rows = read_csv(INPUTS["ownership"])
    ownership_counts = count_by(ownership_rows, "Статус")
    ownership_ready = ownership_counts.get("READY", 0)
    ownership_check = ownership_counts.get("CHECK", 0)
    high_ownership_not_ready = [
        row for row in ownership_rows
        if clean(row.get("Критичность")) == "Высокая" and clean(row.get("Статус")).upper() != "READY"
    ]
    metric(metrics, "Ответственность", "READY зон", ownership_ready, "OK" if ownership_ready else "WARN", "Разделы с подтвержденным владельцем")
    metric(metrics, "Ответственность", "CHECK зон", ownership_check, "WARN" if ownership_check else "OK", "Нужно подтвердить владельца и замещающего")
    metric(metrics, "Ответственность", "Высокая критичность не READY", len(high_ownership_not_ready), "WARN" if high_ownership_not_ready else "OK", "Критичные зоны без подтверждения")
    if high_ownership_not_ready:
        actions.append("Назначить владельцев и замещающих по `section-ownership-report.md`, начиная с высокой критичности.")

    change_rows = read_csv(INPUTS["change_requests"])
    open_changes = [row for row in change_rows if clean(row.get("action_state")) == "OPEN"]
    high_priority_open = [row for row in open_changes if int_value(row.get("priority")) >= 4]
    metric(metrics, "Предложения", "Открытые заявки", len(open_changes), "WARN" if open_changes else "OK", "Заявки не в финальном статусе")
    metric(metrics, "Предложения", "Открытые с приоритетом 4-5", len(high_priority_open), "WARN" if high_priority_open else "OK", "Нужны первыми в разбор")
    if high_priority_open:
        actions.append("Разобрать высокоприоритетные заявки из `change-request-report.md`.")

    missing_rows = read_csv(INPUTS["missing"])
    empty_id = sum(int_value(row.get("Пустой ID")) for row in missing_rows)
    empty_status = sum(int_value(row.get("Пустой статус")) for row in missing_rows)
    empty_priority = sum(int_value(row.get("Пустой приоритет")) for row in missing_rows)
    metric(metrics, "Качество CSV", "Пустые ID", empty_id, "WARN" if empty_id else "OK", "Строки без стабильного идентификатора")
    metric(metrics, "Качество CSV", "Пустые статусы", empty_status, "WARN" if empty_status else "OK", "Строки без статуса")
    metric(metrics, "Качество CSV", "Пустые приоритеты", empty_priority, "WARN" if empty_priority else "OK", "Строки без приоритета")
    if empty_id or empty_status or empty_priority:
        actions.append("Исправить обязательные поля из `missing-values-report.md` перед переносом в рабочую таблицу.")

    access_rows = read_csv(INPUTS["integration_access"])
    contract_rows = read_csv(INPUTS["integration_contracts"])
    full_private_access = [
        row for row in access_rows
        if clean(row.get("storage")) != "Публичный репозиторий" and clean(row.get("read_access")) == "yes"
    ]
    broken_contracts = [
        row for row in contract_rows
        if any(clean(row.get(column)).lower() in {"false", "no", "нет"} for column in ["source_exists", "artifact_exists", "doc_exists", "generator_exists"])
    ]
    metric(metrics, "Интеграция", "Правил доступа", len(access_rows), "OK", "Матрица будущих доступов")
    metric(metrics, "Интеграция", "Полный доступ к закрытым данным", len(full_private_access), "WARN" if full_private_access else "OK", "Требует ручной проверки роли")
    metric(metrics, "Интеграция", "Проблемные контракты", len(broken_contracts), "WARN" if broken_contracts else "OK", "Не найден источник, артефакт, документация или генератор")
    if full_private_access or broken_contracts:
        actions.append("Проверить интеграционные отчёты: доступы к закрытым данным и готовность контрактов.")

    if not actions:
        actions.append("Критичных управленческих действий по dashboard не найдено. Перейти к ручной проверке смысла данных.")

    return metrics, actions


def build_markdown(metrics: list[dict[str, str]], actions: list[str]) -> str:
    warn_count = sum(1 for row in metrics if row["level"] == "WARN")
    ok_count = sum(1 for row in metrics if row["level"] == "OK")

    lines = [
        "# Управленческая сводка",
        "",
        "## Сводка",
        "",
        f"- OK: {ok_count}",
        f"- WARN: {warn_count}",
        "",
        "## Метрики",
        "",
        "| Раздел | Метрика | Значение | Уровень | Комментарий |",
        "|---|---|---:|---|---|",
    ]
    for row in metrics:
        lines.append(f"| {row['section']} | {row['metric']} | {row['value']} | {row['level']} | {row['comment']} |")

    lines.extend(["", "## Ближайшие действия", ""])
    for index, action in enumerate(actions, start=1):
        lines.append(f"{index}. {action}")

    lines.extend([
        "",
        "## Ограничение",
        "",
        "Dashboard показывает управленческие сигналы по техническим отчётам. Он не подтверждает юридическую корректность данных и актуальность реальных контактов.",
    ])
    return "\n".join(lines) + "\n"


def write_csv(metrics: list[dict[str, str]]):
    with REPORT_CSV.open("w", encoding="utf-8-sig", newline="") as file:
        fieldnames = ["section", "metric", "value", "level", "comment"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics)


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    metrics, actions = build_metrics()
    REPORT_MD.write_text(build_markdown(metrics, actions), encoding="utf-8")
    write_csv(metrics)
    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
