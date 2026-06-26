"""
Базовая проверка публичной безопасности репозитория.

Скрипт ищет потенциально рискованные слова и шаблоны в текстовых файлах.
По умолчанию он работает как предупреждение. Для строгого режима используйте --strict.

Запуск:
python scripts/tools/privacy_scan.py
python scripts/tools/privacy_scan.py --strict
"""

from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parents[2]

TEXT_EXTENSIONS = {
    ".md", ".csv", ".txt", ".py", ".gs", ".yml", ".yaml", ".json"
}

SKIP_DIRS = {".git", "build", "__pycache__", ".pytest_cache"}

RISK_WORDS = [
    "паспорт",
    "снилс",
    "токен",
    "token",
    "password",
    "пароль",
    "secret",
    "ключ доступа",
    "client_secret",
]

PHONE_PATTERN = re.compile(r"(?:\+7|8)\D{0,3}\d{3}\D{0,3}\d{3}\D{0,3}\d{2}\D{0,3}\d{2}")
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

ALLOW_FILES = {
    "CONTRIBUTING.md",
    "docs/private-google-sheet-setup.md",
    "docs/security-and-privacy.md",
    "scripts/tools/privacy_scan.py",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Проверка публичной безопасности проекта")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Завершаться с кодом 1, если найдены потенциальные риски",
    )
    return parser.parse_args()


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def scan_file(path: Path):
    relative = path.relative_to(ROOT).as_posix()
    if relative in ALLOW_FILES:
        return []

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    findings = []
    lower_text = text.lower()

    for word in RISK_WORDS:
        if word.lower() in lower_text:
            findings.append(f"риск-слово: {word}")

    if PHONE_PATTERN.search(text):
        findings.append("похоже на телефон")

    if EMAIL_PATTERN.search(text):
        findings.append("похоже на email")

    return findings


def main():
    args = parse_args()
    problems = {}

    for path in ROOT.rglob("*"):
        if not path.is_file() or should_skip(path) or not is_text_file(path):
            continue

        findings = scan_file(path)
        if findings:
            problems[path.relative_to(ROOT).as_posix()] = findings

    if not problems:
        print("Проверка публичной безопасности завершена: явных замечаний нет.")
        return 0

    print("Найдены потенциально рискованные места. Проверьте вручную.\n")
    for file_path, findings in problems.items():
        print(file_path)
        for finding in findings:
            print(f"  - {finding}")
        print()

    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
