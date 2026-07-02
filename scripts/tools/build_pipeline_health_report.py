"""
Отчет согласованности сборочного контура проекта.

Проверяет, что ключевые файлы проекта, Makefile, GitHub Actions,
генераторы отчетов, preflight-сводка и индекс артефактов не разъехались
между собой.

Результаты сохраняются в:
- build/pipeline-health-report.md
- build/pipeline-health-report.csv
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

REPORT_MD = BUILD_DIR / "pipeline-health-report.md"
REPORT_CSV = BUILD_DIR / "pipeline-health-report.csv"

REQUIRED_FILES = [
    "README.md",
    "Makefile",
    ".github/workflows/validate-data.yml",
    "scripts/tools/build_preflight_summary.py",
    "scripts/tools/build_artifact_index.py",
    "docs/project-status.md",
    "docs/project-index.md",
]

REQUIRED_MAKE_TARGETS = [
    "validate",
    "sources",
    "privacy",
    "xlsx",
    "html-preview",
    "html-check",
    "report",
    "missing",
    "readiness",
    "coverage",
    "ids",
    "schemas",
    "freshness",
    "change-requests",
    "source-trust",
    "record-lifecycle",
    "private-contact-schema",
    "contact-verification",
    "department-routing",
    "role-navigation",
    "ownership",
    "acceptance-tests",
    "role-training",
    "go-no-go",
    "launch-decision",
    "usage-metrics",
    "adoption-plan",
    "weekly-digest",
    "manager-actions",
    "operating-rhythm",
    "import-plan",
    "tabs-plan",
    "validation-plan",
    "formatting-plan",
    "knowledge-index",
    "knowledge-check",
    "relationships",
    "deal-hints",
    "deal-signals",
    "deal-hint-preview",
    "deal-audiences",
    "deal-hint-ui-map",
    "deal-hint-api-examples",
    "integration-json-fields",
    "integration-visibility",
    "integration-access",
    "integration-contracts",
    "manager-dashboard",
    "office-launch",
    "launch-packet",
    "summary",
    "artifact-index",
    "pipeline-health",
    "inventory",
    "preflight",
]

README_REQUIRED_MARKERS = [
    "make preflight",
    "baza-build-artifacts",
    "docs/project-status.md",
    "docs/project-index.md",
]

PREFLIGHT_REQUIRED_MARKERS = [
    "preflight-summary.md",
    "pipeline-health-report.md",
    "manager-dashboard.md",
    "go-no-go-report.md",
    "office-launch-packet.md",
]

ARTIFACT_INDEX_REQUIRED_MARKERS = [
    "preflight-summary.md",
    "pipeline-health-report.md",
    "manager-dashboard.md",
    "go-no-go-report.md",
    "knowledge-index.json",
]

SCRIPT_PATTERN = re.compile(r"scripts/tools/([A-Za-z0-9_]+\.py)")
TARGET_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+):", re.MULTILINE)


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def add_check(rows: list[dict[str, str]], check_id: str, status: str, area: str, message: str, action: str = "") -> None:
    rows.append({
        "check_id": check_id,
        "status": status,
        "area": area,
        "message": message,
        "action": action,
    })


def scripts_from_text(text: str) -> set[str]:
    return set(SCRIPT_PATTERN.findall(text))


def make_targets(makefile_text: str) -> set[str]:
    return set(TARGET_PATTERN.findall(makefile_text))


def status_rank(status: str) -> int:
    return {"OK": 0, "WARN": 1, "FAIL": 2}.get(status, 1)


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    makefile_text = read_text("Makefile")
    workflow_text = read_text(".github/workflows/validate-data.yml")
    readme_text = read_text("README.md")
    preflight_text = read_text("scripts/tools/build_preflight_summary.py")
    artifact_index_text = read_text("scripts/tools/build_artifact_index.py")

    for relative_path in REQUIRED_FILES:
        status = "OK" if (ROOT / relative_path).exists() else "FAIL"
        add_check(
            rows,
            f"file:{relative_path}",
            status,
            "required-files",
            f"Файл `{relative_path}` {'найден' if status == 'OK' else 'не найден'}.",
            "Вернуть файл или обновить список обязательных элементов." if status == "FAIL" else "",
        )

    targets = make_targets(makefile_text)
    for target in REQUIRED_MAKE_TARGETS:
        status = "OK" if target in targets else "FAIL"
        add_check(
            rows,
            f"make-target:{target}",
            status,
            "makefile",
            f"Цель Makefile `{target}` {'найдена' if status == 'OK' else 'не найдена'}.",
            "Добавить цель в Makefile или убрать ее из обязательного списка." if status == "FAIL" else "",
        )

    make_scripts = scripts_from_text(makefile_text)
    workflow_scripts = scripts_from_text(workflow_text)

    for script_name in sorted(make_scripts | workflow_scripts):
        script_path = ROOT / "scripts" / "tools" / script_name
        status = "OK" if script_path.exists() else "FAIL"
        add_check(
            rows,
            f"script-exists:{script_name}",
            status,
            "scripts",
            f"Скрипт `{script_name}` {'существует' if status == 'OK' else 'не найден'}.",
            "Создать скрипт или убрать ссылку из Makefile/workflow." if status == "FAIL" else "",
        )

    only_in_makefile = sorted(make_scripts - workflow_scripts)
    only_in_workflow = sorted(workflow_scripts - make_scripts)

    if only_in_makefile:
        add_check(
            rows,
            "scripts:only-in-makefile",
            "WARN",
            "workflow-sync",
            "В Makefile есть скрипты, которых нет в validate-data.yml: " + ", ".join(only_in_makefile),
            "Проверить, должны ли эти шаги выполняться в GitHub Actions.",
        )
    else:
        add_check(rows, "scripts:only-in-makefile", "OK", "workflow-sync", "Все скрипты Makefile отражены в workflow.")

    if only_in_workflow:
        add_check(
            rows,
            "scripts:only-in-workflow",
            "WARN",
            "workflow-sync",
            "В validate-data.yml есть скрипты, которых нет в Makefile: " + ", ".join(only_in_workflow),
            "Проверить, нужна ли отдельная цель Makefile.",
        )
    else:
        add_check(rows, "scripts:only-in-workflow", "OK", "workflow-sync", "Все скрипты workflow отражены в Makefile.")

    for marker in README_REQUIRED_MARKERS:
        status = "OK" if marker in readme_text else "WARN"
        add_check(
            rows,
            f"readme-marker:{marker}",
            status,
            "readme",
            f"Маркер `{marker}` {'найден' if status == 'OK' else 'не найден'} в README.md.",
            "Обновить README, чтобы входная документация совпадала со сборкой." if status == "WARN" else "",
        )

    for marker in PREFLIGHT_REQUIRED_MARKERS:
        status = "OK" if marker in preflight_text else "WARN"
        add_check(
            rows,
            f"preflight-marker:{marker}",
            status,
            "preflight",
            f"Маркер `{marker}` {'найден' if status == 'OK' else 'не найден'} в build_preflight_summary.py.",
            "Добавить артефакт в EXPECTED_ARTIFACTS или ручной чек-лист preflight." if status == "WARN" else "",
        )

    for marker in ARTIFACT_INDEX_REQUIRED_MARKERS:
        status = "OK" if marker in artifact_index_text else "WARN"
        add_check(
            rows,
            f"artifact-index-marker:{marker}",
            status,
            "artifact-index",
            f"Маркер `{marker}` {'найден' if status == 'OK' else 'не найден'} в build_artifact_index.py.",
            "Добавить ссылку в индекс артефактов." if status == "WARN" else "",
        )

    preflight_line = next((line for line in makefile_text.splitlines() if line.startswith("preflight:")), "")
    for target in ["summary", "artifact-index", "pipeline-health", "inventory"]:
        status = "OK" if target in preflight_line else "WARN"
        add_check(
            rows,
            f"preflight-target:{target}",
            status,
            "makefile-preflight",
            f"Цель `{target}` {'есть' if status == 'OK' else 'не найдена'} в цепочке preflight.",
            "Добавить цель в зависимость preflight, если она должна выполняться при общей проверке." if status == "WARN" else "",
        )

    return rows


def build_markdown(rows: list[dict[str, str]]) -> str:
    statuses = {"OK": 0, "WARN": 0, "FAIL": 0}
    for row in rows:
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1

    overall = max((row["status"] for row in rows), key=status_rank, default="OK")
    overall_text = {
        "OK": "OK — критичных рассинхронизаций не найдено.",
        "WARN": "WARN — есть элементы, которые стоит проверить вручную.",
        "FAIL": "FAIL — есть ошибки, которые могут ломать сборку или доверие к артефактам.",
    }[overall]

    lines = [
        "# Pipeline health report",
        "",
        "## Назначение",
        "",
        "Отчет проверяет согласованность сборочного контура проекта: Makefile, GitHub Actions, генераторы, README, preflight-сводку и индекс артефактов.",
        "",
        "## Итог",
        "",
        f"Статус: **{overall_text}**",
        "",
        f"- OK: {statuses.get('OK', 0)}",
        f"- WARN: {statuses.get('WARN', 0)}",
        f"- FAIL: {statuses.get('FAIL', 0)}",
        "",
        "## Проверки",
        "",
        "| ID | Статус | Зона | Сообщение | Что сделать |",
        "|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| `{row['check_id']}` | {row['status']} | {row['area']} | {row['message']} | {row['action']} |"
        )

    lines.extend([
        "",
        "## Как использовать",
        "",
        "1. После изменения Makefile, workflow или генераторов запустить `make pipeline-health` или полный `make preflight`.",
        "2. Если появились WARN, проверить, не забыли ли добавить новый скрипт в Makefile, GitHub Actions, preflight или индекс артефактов.",
        "3. Если появились FAIL, исправить отсутствующие файлы, цели или ссылки до передачи артефактов сотрудникам.",
        "",
        "## Ограничения",
        "",
        "Отчет не заменяет ручной запуск всей сборки. Он помогает быстро увидеть рассинхронизации между управляющими файлами проекта.",
    ])
    return "\n".join(lines) + "\n"


def write_csv(rows: list[dict[str, str]]) -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    with REPORT_CSV.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["check_id", "status", "area", "message", "action"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    REPORT_MD.write_text(build_markdown(rows), encoding="utf-8")
    write_csv(rows)
    print(f"Pipeline health report written: {REPORT_MD}")
    print(f"Pipeline health CSV written: {REPORT_CSV}")


if __name__ == "__main__":
    main()
