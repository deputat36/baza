"""
Сборка единого пакета запуска базы знаний.

Пакет не заменяет детальные отчеты. Он дает менеджеру один файл,
из которого понятно, что открыть перед запуском и в каком порядке.

Запуск из корня репозитория:
python scripts/tools/build_office_launch_packet.py
"""

from pathlib import Path
import csv

try:
    from workbook_config import ROOT, BUILD_DIR, OUTPUT_FILE
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"
    OUTPUT_FILE = BUILD_DIR / "baza-knowledge-mvp.xlsx"

OUTPUT_MD = BUILD_DIR / "office-launch-packet.md"
OUTPUT_CSV = BUILD_DIR / "office-launch-packet.csv"

PACKET_ITEMS = [
    ("01", "Старт", "index.html", "Открыть стартовую страницу артефактов"),
    ("02", "Структура", OUTPUT_FILE.name, "Проверить XLSX-книгу и состав листов"),
    ("03", "Интерфейс", "html-preview/index.html", "Проверить HTML-превью для просмотра в браузере"),
    ("04", "Решение", "go-no-go-report.md", "Проверить итог GO/NO-GO и список блокеров"),
    ("05", "Фиксация", "launch-decision-log.md", "Проверить зафиксированное решение запуска"),
    ("06", "Управление", "manager-dashboard.md", "Разобрать WARN и ближайшие действия"),
    ("07", "Готовность", "launch-readiness-report.md", "Проверить READY/CHECK/DRAFT по разделам"),
    ("08", "Ответственность", "section-ownership-report.md", "Проверить владельцев критичных разделов"),
    ("09", "Приемка", "office-acceptance-test-report.md", "Пройти блокирующие сценарии по ролям"),
    ("10", "Обучение", "role-training-report.md", "Проверить блокирующие блоки обучения"),
    ("11", "Запуск", "office-launch-checklist-report.md", "Закрыть задачи, блокирующие запуск"),
    ("12", "Эксплуатация", "operating-rhythm-report.md", "Проверить регулярные задачи после запуска"),
    ("13", "Использование", "usage-metrics-report.md", "Проверить первые метрики использования после запуска"),
    ("14", "Улучшения", "adoption-improvement-plan.md", "Проверить план доработок по метрикам и обратной связи"),
    ("15", "Дайджест", "weekly-manager-digest.md", "Проверить еженедельную сводку менеджера"),
    ("16", "Действия", "manager-action-register.md", "Назначить ответственных по открытому реестру действий"),
    ("17", "Доверие", "source-trust-report.md", "Проверить уровни доверия источников и ограничения использования"),
    ("18", "Жизненный цикл", "record-lifecycle-report.md", "Проверить статусы записей и правило READY"),
    ("19", "Департаменты", "department-routing-report.md", "Проверить маршруты к кураторам центрального офиса"),
    ("20", "Закрытые контакты", "private-contact-schema-report.md", "Проверить поля приватного реестра контактов"),
    ("21", "Проверка контактов", "contact-verification-report.md", "Проверить регламент актуализации закрытых контактов"),
    ("22", "Актуальность", "data-freshness-report.md", "Проверить просроченные и непроверенные разделы"),
    ("23", "Предложения", "change-request-report.md", "Разобрать открытые предложения сотрудников"),
    ("24", "Импорт", "import-plan.md", "Проверить порядок переноса в закрытую Google Таблицу"),
    ("25", "Листы", "google-sheet-tabs-plan.md", "Проверить структуру будущей Google Таблицы"),
    ("26", "Валидации", "google-sheet-validation-plan.md", "Проверить выпадающие списки и справочники"),
    ("27", "Оформление", "google-sheet-formatting-plan.md", "Проверить правила оформления статусов"),
    ("28", "Безопасность", "integration-access-report.md", "Проверить матрицу доступа к закрытым данным"),
    ("29", "Контракты", "integration-contract-report.md", "Проверить готовность read-only контрактов"),
    ("30", "Совместимость", "knowledge-index.json", "Проверить наличие JSON-индекса знаний"),
]


def artifact_status(file_name: str):
    path = BUILD_DIR / file_name
    if path.exists():
        if path.is_file():
            return "есть", f"{path.stat().st_size} байт"
        return "есть", "каталог"
    return "нет", "-"


def build_rows():
    rows = []
    for order, stage, file_name, action in PACKET_ITEMS:
        status, size = artifact_status(file_name)
        rows.append({
            "order": order,
            "stage": stage,
            "artifact": file_name,
            "status": status,
            "size": size,
            "action": action,
        })
    return rows


def build_markdown(rows):
    missing = [row for row in rows if row["status"] != "есть"]

    lines = [
        "# Пакет запуска базы знаний",
        "",
        "## Назначение",
        "",
        "Этот файл собирает ключевые артефакты, которые менеджер должен открыть перед запуском базы знаний в офисе.",
        "",
        "## Сводка",
        "",
        f"- Всего артефактов в пакете: {len(rows)}",
        f"- Не найдено при сборке: {len(missing)}",
        "",
        "## Порядок проверки",
        "",
        "| Шаг | Этап | Артефакт | Статус | Действие |",
        "|---:|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['order']} | {row['stage']} | `{row['artifact']}` | {row['status']} | {row['action']} |"
        )

    lines.extend(["", "## Если чего-то нет", ""])
    if not missing:
        lines.append("Все артефакты пакета найдены.")
    else:
        for row in missing:
            lines.append(f"- `{row['artifact']}`: запустить соответствующий генератор или `make preflight`.")

    lines.extend([
        "",
        "## Правило использования",
        "",
        "Пакет запуска не подтверждает юридическую точность данных и актуальность реальных контактов. Он нужен для управленческой проверки структуры, запуска, обучения и эксплуатации.",
        "Реальные рабочие данные должны храниться только в закрытой Google Таблице.",
        "",
    ])

    return "\n".join(lines)


def write_csv(rows):
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = ["order", "stage", "artifact", "status", "size", "action"]
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
