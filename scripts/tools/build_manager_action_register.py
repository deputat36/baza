"""
Сборка реестра управленческих действий.

Реестр превращает отчеты и еженедельный дайджест в список действий,
которые менеджер может назначить ответственным.

Запуск из корня репозитория:
python scripts/tools/build_manager_action_register.py
"""

from pathlib import Path
import csv

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

OUTPUT_MD = BUILD_DIR / "manager-action-register.md"
OUTPUT_CSV = BUILD_DIR / "manager-action-register.csv"

SOURCES = {
    "digest": BUILD_DIR / "weekly-manager-digest.csv",
    "adoption": BUILD_DIR / "adoption-improvement-plan.csv",
    "requests": BUILD_DIR / "change-request-report.csv",
    "freshness": BUILD_DIR / "data-freshness-report.csv",
    "go_no_go": BUILD_DIR / "go-no-go-report.csv",
}

DONE_STATUSES = {"OK", "READY", "DONE", "CLOSED", "RESOLVED", "COMPLETE", "COMPLETED"}
ACTION_STATUSES = {"WARN", "CHECK", "PENDING", "DRAFT", "NEW", "OPEN", "IN_PROGRESS", "BLOCKER", "EXPIRED"}
HIGH_VALUES = {"HIGH", "Высокая", "ВЫСОКАЯ", "BLOCKER", "Блокер"}

STATUS_FIELDS = [
    "status",
    "metric_status",
    "decision_status",
    "action_status",
    "request_status",
    "freshness_status",
    "status_current",
    "Статус",
]

PRIORITY_FIELDS = ["priority", "criticality", "Критичность", "Приоритет", "decision_impact", "impact"]
TITLE_FIELDS = ["action", "metric", "title", "name", "Задача", "Проблема", "Описание", "section", "area"]
OWNER_FIELDS = ["owner", "responsible", "Ответственный", "Роль", "role"]
SOURCE_ID_FIELDS = ["id", "ID", "source_id", "metric_id", "request_id"]


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def first_existing(row, fields, default=""):
    for field in fields:
        if field in row and str(row[field]).strip():
            return str(row[field]).strip()
    return default


def normalized(value):
    return str(value or "").strip().upper()


def needs_action(row):
    status = normalized(first_existing(row, STATUS_FIELDS))
    priority = first_existing(row, PRIORITY_FIELDS)
    if status and status not in DONE_STATUSES and status in ACTION_STATUSES:
        return True
    return priority in HIGH_VALUES


def status_or_default(row):
    return first_existing(row, STATUS_FIELDS, "CHECK")


def priority_or_default(row):
    priority = first_existing(row, PRIORITY_FIELDS)
    if priority:
        return priority
    status = normalized(status_or_default(row))
    if status == "BLOCKER":
        return "Высокая"
    if status in {"WARN", "EXPIRED"}:
        return "Высокая"
    return "Средняя"


def add_action(actions, source_name, row, default_action):
    source_id = first_existing(row, SOURCE_ID_FIELDS, f"{source_name}-{len(actions) + 1:03d}")
    title = first_existing(row, TITLE_FIELDS, default_action)
    owner = first_existing(row, OWNER_FIELDS, "менеджер")
    status = status_or_default(row)
    priority = priority_or_default(row)

    actions.append({
        "action_id": f"MGR-{len(actions) + 1:04d}",
        "source": source_name,
        "source_id": source_id,
        "title": title,
        "owner": owner,
        "priority": priority,
        "status": "OPEN" if normalized(status) not in DONE_STATUSES else "DONE",
        "next_step": default_action,
    })


def build_actions():
    actions = []

    digest_rows = read_csv(SOURCES["digest"])
    for row in digest_rows:
        if needs_action(row):
            add_action(actions, SOURCES["digest"].name, row, "Разобрать строку еженедельного дайджеста")

    adoption_rows = read_csv(SOURCES["adoption"])
    for row in adoption_rows:
        if needs_action(row):
            add_action(actions, SOURCES["adoption"].name, row, "Назначить ответственного и срок по плану улучшений")

    request_rows = read_csv(SOURCES["requests"])
    for row in request_rows:
        if needs_action(row):
            add_action(actions, SOURCES["requests"].name, row, "Принять решение по предложению сотрудника")

    freshness_rows = read_csv(SOURCES["freshness"])
    for row in freshness_rows:
        if needs_action(row):
            add_action(actions, SOURCES["freshness"].name, row, "Проверить актуальность раздела или контакта")

    go_no_go_rows = read_csv(SOURCES["go_no_go"])
    for row in go_no_go_rows:
        if needs_action(row):
            add_action(actions, SOURCES["go_no_go"].name, row, "Снять блокер запуска или зафиксировать решение")

    missing_sources = [path.name for path in SOURCES.values() if not path.exists()]
    for source in missing_sources:
        actions.append({
            "action_id": f"MGR-{len(actions) + 1:04d}",
            "source": source,
            "source_id": source,
            "title": f"Не найден источник {source}",
            "owner": "администратор базы",
            "priority": "Средняя",
            "status": "OPEN",
            "next_step": "Запустить `make preflight` и повторить сборку реестра",
        })

    return actions


def build_markdown(actions):
    open_actions = [action for action in actions if action["status"] == "OPEN"]
    high_actions = [action for action in open_actions if action["priority"] in HIGH_VALUES or normalized(action["priority"]) == "HIGH"]

    lines = [
        "# Реестр управленческих действий",
        "",
        "## Назначение",
        "",
        "Реестр собирает действия менеджера из еженедельного дайджеста, плана улучшений, очереди предложений, актуальности данных и GO/NO-GO отчета.",
        "",
        "## Сводка",
        "",
        f"- Всего действий: {len(actions)}",
        f"- Открытых действий: {len(open_actions)}",
        f"- Высокий приоритет: {len(high_actions)}",
        "",
        "## Действия",
        "",
        "| ID | Источник | Исходная запись | Действие | Ответственный | Приоритет | Статус | Следующий шаг |",
        "|---|---|---|---|---|---|---|---|",
    ]

    if not actions:
        lines.append("| - | - | - | Нет действий | - | - | - | Продолжать регулярную проверку |")
    else:
        for action in actions:
            lines.append(
                f"| {action['action_id']} | `{action['source']}` | {action['source_id']} | {action['title']} | {action['owner']} | {action['priority']} | {action['status']} | {action['next_step']} |"
            )

    lines.extend([
        "",
        "## Правило работы",
        "",
        "Открытые действия нужно переносить в закрытую рабочую таблицу или задавать ответственным в принятом офисном канале.",
        "Публичный репозиторий не должен содержать реальные внутренние телефоны, клиентские данные и закрытые комментарии по сделкам.",
        "",
    ])

    return "\n".join(lines)


def write_csv(actions):
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = ["action_id", "source", "source_id", "title", "owner", "priority", "status", "next_step"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(actions)


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    actions = build_actions()
    OUTPUT_MD.write_text(build_markdown(actions), encoding="utf-8")
    write_csv(actions)
    print(f"Готово: {OUTPUT_MD.relative_to(ROOT)}")
    print(f"Готово: {OUTPUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
