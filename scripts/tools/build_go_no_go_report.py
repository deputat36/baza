"""
Сборка управленческого отчета GO/NO-GO перед запуском базы.

Отчет собирает блокеры из чек-листа запуска, приемочных сценариев,
плана обучения и матрицы владельцев разделов.

Запуск из корня репозитория:
python scripts/tools/build_go_no_go_report.py
"""

from pathlib import Path
import csv

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

OUTPUT_MD = BUILD_DIR / "go-no-go-report.md"
OUTPUT_CSV = BUILD_DIR / "go-no-go-report.csv"

DONE_STATUSES = {"READY", "DONE", "OK", "CLOSED", "ГОТОВО", "ВЫПОЛНЕНО", "ЗАКРЫТО"}

SOURCES = [
    {
        "name": "Чек-лист запуска",
        "path": ROOT / "data" / "drafts" / "office-launch-checklist.csv",
        "item_field": "Задача",
        "owner_field": "Ответственный",
        "block_field": "Блокирует запуск",
    },
    {
        "name": "Приемочные сценарии",
        "path": ROOT / "data" / "drafts" / "office-acceptance-tests.csv",
        "item_field": "Сценарий",
        "owner_field": "Роль",
        "block_field": "Блокирует запуск",
    },
    {
        "name": "Обучение по ролям",
        "path": ROOT / "data" / "drafts" / "role-training-plan.csv",
        "item_field": "Блок обучения",
        "owner_field": "Роль",
        "block_field": "Блокирует запуск",
    },
    {
        "name": "Ответственные за разделы",
        "path": ROOT / "data" / "drafts" / "section-ownership-matrix.csv",
        "item_field": "Раздел",
        "owner_field": "Владелец роли",
        "block_field": None,
    },
]


def read_rows(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def clean(value):
    return str(value or "").strip()


def is_done(status):
    return clean(status).upper() in DONE_STATUSES


def blocks_launch(row, source):
    if source["block_field"]:
        return clean(row.get(source["block_field"])).lower() == "yes"
    return clean(row.get("Критичность")) == "Высокая"


def blocker_reason(row, source):
    if source["block_field"]:
        return "Блокирует запуск и не закрыто"
    return "Высокая критичность без статуса готовности"


def collect_items():
    items = []
    for source in SOURCES:
        for row in read_rows(source["path"]):
            status = clean(row.get("Статус"))
            should_block = blocks_launch(row, source)
            done = is_done(status)
            items.append({
                "source": source["name"],
                "id": clean(row.get("ID")),
                "item": clean(row.get(source["item_field"])),
                "owner": clean(row.get(source["owner_field"])),
                "artifact": clean(row.get("Артефакт") or row.get("Источник отчета")),
                "criticality": clean(row.get("Критичность")),
                "status": status,
                "blocks_launch": "yes" if should_block else "no",
                "decision_impact": "BLOCKER" if should_block and not done else "OK",
                "reason": blocker_reason(row, source) if should_block and not done else "",
            })
    return items


def build_markdown(items):
    blockers = [item for item in items if item["decision_impact"] == "BLOCKER"]
    decision = "GO" if not blockers else "NO-GO"

    lines = [
        "# GO/NO-GO отчет запуска",
        "",
        "## Решение",
        "",
        f"**{decision}**",
        "",
        "## Сводка",
        "",
        f"- Всего проверяемых пунктов: {len(items)}",
        f"- Блокеров запуска: {len(blockers)}",
        "",
        "## Блокеры",
        "",
    ]

    if not blockers:
        lines.append("Блокеров запуска не найдено.")
    else:
        lines.extend([
            "| Источник | ID | Пункт | Ответственный | Статус | Артефакт | Причина |",
            "|---|---|---|---|---|---|---|",
        ])
        for item in blockers:
            lines.append(
                f"| {item['source']} | {item['id']} | {item['item']} | {item['owner']} | {item['status']} | `{item['artifact']}` | {item['reason']} |"
            )

    lines.extend([
        "",
        "## Правило решения",
        "",
        "`GO` возможен только когда нет открытых пунктов, которые блокируют запуск, и нет высококритичных зон ответственности без статуса готовности.",
        "",
        "## Ограничение",
        "",
        "Отчет проверяет управленческую готовность по CSV-статусам. Он не подтверждает юридическую точность данных и актуальность реальных контактов.",
        "",
    ])
    return "\n".join(lines)


def write_csv(items):
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "source",
            "id",
            "item",
            "owner",
            "artifact",
            "criticality",
            "status",
            "blocks_launch",
            "decision_impact",
            "reason",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    items = collect_items()
    OUTPUT_MD.write_text(build_markdown(items), encoding="utf-8")
    write_csv(items)
    print(f"Готово: {OUTPUT_MD.relative_to(ROOT)}")
    print(f"Готово: {OUTPUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
