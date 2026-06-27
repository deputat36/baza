"""
Проверка обязательных верхнеуровневых полей JSON-контрактов.

Скрипт не проверяет всю бизнес-логику. Он фиксирует минимальный контракт,
который будущий интерфейс сможет читать стабильно.

Запуск:
python scripts/tools/validate_integration_json_fields.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

try:
    from workbook_config import ROOT, BUILD_DIR
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"

EXPECTATIONS_FILE = ROOT / "data" / "dictionaries" / "integration-json-fields.csv"
REPORT_MD = BUILD_DIR / "integration-json-fields-report.md"
REPORT_CSV = BUILD_DIR / "integration-json-fields-report.csv"

REQUIRED_COLUMNS = ["ID", "Контракт", "Артефакт", "Обязательные поля", "Статус"]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def split_list(value: Any) -> list[str]:
    text = clean(value)
    if not text:
        return []
    return [part.strip() for part in text.replace(",", ";").split(";") if part.strip()]


def read_expectations() -> list[dict[str, str]]:
    if not EXPECTATIONS_FILE.exists():
        raise SystemExit(f"Файл ожиданий не найден: {EXPECTATIONS_FILE.relative_to(ROOT)}")

    with EXPECTATIONS_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"В integration-json-fields.csv нет колонок: {', '.join(missing)}")
        return list(reader)


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(relative_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{relative_path}: верхний уровень JSON должен быть объектом")
    return data


def build_report_rows(expectations: list[dict[str, str]]):
    rows = []
    problems = []
    seen_ids = set()
    seen_contracts = set()

    for row_number, item in enumerate(expectations, start=2):
        item_id = clean(item.get("ID"))
        contract = clean(item.get("Контракт"))
        artifact = clean(item.get("Артефакт"))
        required_fields = split_list(item.get("Обязательные поля"))
        status = clean(item.get("Статус"))

        if not item_id:
            problems.append(f"строка {row_number}: пустой ID")
        elif item_id in seen_ids:
            problems.append(f"{item_id}: дубль ID")
        seen_ids.add(item_id)

        if not contract:
            problems.append(f"{item_id}: пустое имя контракта")
        elif contract in seen_contracts:
            problems.append(f"{item_id}: дубль контракта {contract}")
        seen_contracts.add(contract)

        if not artifact:
            problems.append(f"{item_id}: не указан артефакт")
        if not required_fields:
            problems.append(f"{item_id}: не указаны обязательные поля")
        if not status:
            problems.append(f"{item_id}: пустой статус")

        existing_fields = []
        missing_fields = []
        artifact_exists = False
        json_valid = False

        if artifact:
            try:
                data = load_json(artifact)
                artifact_exists = True
                json_valid = True
                for field in required_fields:
                    if field in data:
                        existing_fields.append(field)
                    else:
                        missing_fields.append(field)
            except FileNotFoundError:
                problems.append(f"{item_id}: JSON-артефакт не найден: {artifact}")
            except json.JSONDecodeError as exc:
                problems.append(f"{item_id}: JSON не читается: {artifact}: {exc}")
            except ValueError as exc:
                problems.append(f"{item_id}: {exc}")

        for field in missing_fields:
            problems.append(f"{item_id}: нет обязательного поля `{field}` в {artifact}")

        rows.append({
            "id": item_id,
            "contract": contract,
            "artifact": artifact,
            "required_fields": "; ".join(required_fields),
            "existing_fields": "; ".join(existing_fields),
            "missing_fields": "; ".join(missing_fields),
            "artifact_exists": artifact_exists,
            "json_valid": json_valid,
            "status": status,
        })

    return rows, problems


def yes_no(value: bool) -> str:
    return "да" if value else "нет"


def write_outputs(rows, problems):
    lines = [
        "# Отчёт по полям JSON-контрактов",
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
        "## Проверка",
        "",
        "| ID | Контракт | JSON | Поля найдены | Поля отсутствуют |",
        "|---|---|---|---|---|",
    ])
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['contract']} | {yes_no(row['json_valid'])} | {row['existing_fields'] or '-'} | {row['missing_fields'] or '-'} |"
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "id",
            "contract",
            "artifact",
            "required_fields",
            "existing_fields",
            "missing_fields",
            "artifact_exists",
            "json_valid",
            "status",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    rows, problems = build_report_rows(read_expectations())
    write_outputs(rows, problems)

    print(f"Готово: {REPORT_MD.relative_to(ROOT)}")
    print(f"Готово: {REPORT_CSV.relative_to(ROOT)}")

    if problems:
        print("\nНайдены ошибки полей JSON-контрактов:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
