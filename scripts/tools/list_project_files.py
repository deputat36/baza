"""
Инвентаризация файлов проекта.

Скрипт выводит список основных файлов репозитория по разделам.

Запуск:
python scripts/tools/list_project_files.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SECTIONS = {
    "Документация": ["docs"],
    "Шаблоны": ["templates"],
    "Справочники": ["data/dictionaries"],
    "Черновики": ["data/drafts"],
    "Скрипты": ["scripts"],
    "CRM-дизайн": ["crm-design"],
}

SKIP_PARTS = {".git", "build", "__pycache__"}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def collect_files(relative_dir: str):
    directory = ROOT / relative_dir
    if not directory.exists():
        return []

    files = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and not should_skip(path):
            files.append(path.relative_to(ROOT))
    return files


def main():
    for section, directories in SECTIONS.items():
        print(f"\n## {section}")
        found = []
        for directory in directories:
            found.extend(collect_files(directory))

        if not found:
            print("- нет файлов")
            continue

        for path in found:
            print(f"- {path.as_posix()}")


if __name__ == "__main__":
    main()
