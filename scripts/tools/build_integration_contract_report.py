"""
Отчёт по контрактам будущей интеграции.

Контракт здесь — это стабильный источник или артефакт сборки, который
может использовать будущий интерфейс как read-only входные данные.

Запуск:
python scripts/tools/build_integration_contract_report.py
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

CONTRACTS_FILE = ROOT / "data" / "dictionaries" / "integration-contracts.csv"
REPORT_MD = BUILD_DIR / "integration-contract-report.md"
REPORT_CSV = BUILD_DIR / "integration-contract-report.csv"

REQUIRED_COLUMNS = [
    "ID",
    "Контракт",
    "Версия",
    "Назначение",
    "Источник",
    "Артефакт",
    "Документация",
    "Генератор",
    "Статус",
]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def read_contracts() -> list[dict[str, str]]:
    if not CONTRACTS_FILE.exists():
        raise SystemExit(f"Файл контрактов не найден: {CONTRACTS_FILE.relative_to(ROOT)}")

    with CONTRACTS_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"В integration-contracts.csv нет колонок: {', '.join(missing)}")
        return list(reader)


def path_exists(relative_path: str) -> bool:
    path = ROOT / relative_path
    return path.exists()


def build_rows(contracts: list[dict[str, str]]):
    rows = []
    problems = []
    seen_ids = set()
    seen_names = set()

    for row_number, contract in enumerate(contracts, start=2):
        contract_id = clean(contract.get("ID"))
        name = clean(contract.get("Контракт"))
        version = clean(contract.get("Версия"))
        source = clean(contract.get("Источник"))
        artifact = clean(contract.get("Артефакт"))
        doc = clean(contract.get("Документация"))
        generator = clean(contract.get("Генератор"))
        status = clean(contract.get("Статус"))

        checks = {
            "source_exists": path_exists(source) if source else False,
            "artifact_exists": path_exists(artifact) if artifact else False,
            "doc_exists": path_exists(doc) if doc else False,
            "generator_exists": path_exists(generator) if generator else False,
        }

        if not contract_id:
            problems.append(f"строка {row_number}: пустой ID")
        elif contract_id in seen_ids:
            problems.append(f"{contract_id}: дубль ID")
        seen_ids.add(contract_id)

        if not name:
            problems.append(f"{contract_id}: пустое имя контракта")
        elif name in seen_names:
            problems.append(f"{contract_id}: дубль имени контракта {name}")
        seen_names.add(name)

        if not version:
            problems.append(f"{contract_id}: пустая версия")
        if not status:
            problems.append(f"{contract_id}: пустой статус")

        for check_name, passed in checks.items():
            if not passed:
                problems.append(f"{contract_id}: не найдено {check_name}")

        rows.append({
            "id": contract_id,
            "contract": name,
            "version": version,
            "purpose": clean(contract.get("Назначение")),
            "source": source,
            "artifact": artifact,
            "documentation": doc,
            "generator": generator,
            "status": status,
            **checks,
        })

    return rows, problems


def yes_no(value: bool) -> str:
    return "да" if value else "нет"


def write_outputs(rows, problems):
    lines = [
        "# Отчёт по контрактам интеграции",
        "",
        "## Сводка",
        "",
        f"- Контрактов: {len(rows)}",
        f"- Ошибок: {len(problems)}",
        "",
        "## Ошибки",
        "",
    ]
    if problems:
        lines.extend(f"- {problem}" for problem in problems)
    else:
        lines.append("Ошибок не найдено.")

    lines.extend([
        "",
        "## Контракты",
        "",
        "| ID | Контракт | Версия | Источник | Артефакт | Документация | Генератор |",
        "|---|---|---|---|---|---|---|",
    ])
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['contract']} | {row['version']} | {yes_no(row['source_exists'])} | {yes_no(row['artifact_exists'])} | {yes_no(row['doc_exists'])} | {yes_no(row['generator_exists'])} |"
        )

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "id",
            "contract",
            "version",
            "purpose",
            "source",
            "artifact",
            "documentation",
            "generator",
            "status",
            "source_exists",
            "artifact_exists",
            "doc_exists",
            "generator_exists",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    rows, problems = build_rows(read_contracts())
    write_outputs(rows, problems)

    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")

    if problems:
        print("\nНайдены ошибки контрактов интеграции:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
