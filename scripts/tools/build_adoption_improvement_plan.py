"""
Сборка плана улучшений после запуска базы.

План объединяет ручные задачи из adoption-improvement-plan.csv и
автоматические сигналы из usage-metrics-report.csv.

Запуск из корня репозитория:
python scripts/tools/build_adoption_improvement_plan.py
"""

from pathlib import Path
import csv

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

SOURCE_FILE = ROOT / "data" / "drafts" / "adoption-improvement-plan.csv"
USAGE_METRICS_CSV = BUILD_DIR / "usage-metrics-report.csv"
OUTPUT_MD = BUILD_DIR / "adoption-improvement-plan.md"
OUTPUT_CSV = BUILD_DIR / "adoption-improvement-plan.csv"

PRIORITY_ORDER = {"Высокий": 1, "Средний": 2, "Низкий": 3}
OPEN_STATUSES = {"DRAFT", "CHECK", "NEW", "OPEN", ""}


def clean(value):
    return str(value or "").strip()


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def normalize_manual(row):
    return {
        "id": clean(row.get("ID")),
        "source": clean(row.get("Источник")),
        "signal": clean(row.get("Сигнал")),
        "action": clean(row.get("Что улучшить")),
        "owner": clean(row.get("Ответственный")),
        "priority": clean(row.get("Приоритет")) or "Средний",
        "status": clean(row.get("Статус")) or "DRAFT",
        "artifact": clean(row.get("Артефакт")),
        "origin": "manual",
        "comment": clean(row.get("Комментарий")),
    }


def action_from_metric(row, index):
    metric = clean(row.get("metric"))
    role = clean(row.get("role"))
    status = clean(row.get("metric_status"))

    if status not in {"WARN", "CHECK"}:
        return None

    lower_metric = metric.lower()
    if "без результата" in lower_metric:
        action = "Добавить недостающие материалы и поисковые синонимы"
        owner = "администратор базы"
        priority = "Высокий"
        artifact = "data/dictionaries/search-synonyms.csv"
    elif "активные пользователи" in lower_metric:
        action = "Повторить обучение и проверить стартовую навигацию"
        owner = "менеджер"
        priority = "Высокий"
        artifact = "build/role-training-report.md"
    elif "предложения" in lower_metric:
        action = "Разобрать предложения сотрудников и назначить ответственных"
        owner = "менеджер"
        priority = "Средний"
        artifact = "build/change-request-report.md"
    else:
        action = "Проверить показатель и определить корректирующее действие"
        owner = "менеджер"
        priority = "Средний"
        artifact = "build/usage-metrics-report.md"

    return {
        "id": f"AUTO-{index:04d}",
        "source": "usage-metrics-report",
        "signal": f"{role}: {metric} = {clean(row.get('value'))} при цели {clean(row.get('target'))}",
        "action": action,
        "owner": owner,
        "priority": priority,
        "status": "CHECK",
        "artifact": artifact,
        "origin": "auto",
        "comment": "Автоматически из метрик использования",
    }


def build_rows():
    rows = [normalize_manual(row) for row in read_csv(SOURCE_FILE)]
    auto_index = 1
    for metric_row in read_csv(USAGE_METRICS_CSV):
        action = action_from_metric(metric_row, auto_index)
        if action:
            rows.append(action)
            auto_index += 1
    return sorted(rows, key=lambda row: (PRIORITY_ORDER.get(row["priority"], 9), row["id"]))


def build_markdown(rows):
    open_rows = [row for row in rows if row["status"].upper() in OPEN_STATUSES]
    high_rows = [row for row in rows if row["priority"] == "Высокий" and row["status"].upper() in OPEN_STATUSES]
    auto_rows = [row for row in rows if row["origin"] == "auto"]

    lines = [
        "# План улучшений после запуска",
        "",
        "## Назначение",
        "",
        "Этот файл превращает метрики использования и обратную связь сотрудников в конкретные действия.",
        "",
        "## Сводка",
        "",
        f"- Всего действий: {len(rows)}",
        f"- Открытых действий: {len(open_rows)}",
        f"- Высокий приоритет: {len(high_rows)}",
        f"- Автоматически из метрик: {len(auto_rows)}",
        "",
        "## Действия",
        "",
        "| ID | Приоритет | Источник | Сигнал | Что улучшить | Ответственный | Статус | Артефакт |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['id']} | {row['priority']} | {row['source']} | {row['signal']} | {row['action']} | {row['owner']} | {row['status']} | `{row['artifact']}` |"
        )

    lines.extend([
        "",
        "## Правило работы",
        "",
        "Высокоприоритетные действия разбираются менеджером первыми. Автоматические действия нужно подтвердить вручную перед переносом в рабочую закрытую таблицу.",
        "",
        "## Ограничение",
        "",
        "Публичный репозиторий хранит только шаблон и безопасные сигналы. Реальные данные использования и комментарии сотрудников должны храниться в закрытом контуре.",
        "",
    ])
    return "\n".join(lines)


def write_csv(rows):
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "id",
            "source",
            "signal",
            "action",
            "owner",
            "priority",
            "status",
            "artifact",
            "origin",
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
