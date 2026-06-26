"""
Smoke-проверка HTML-превью базы знаний.

Проверяет, что build/html-preview/index.html существует и содержит ключевые блоки.

Запуск из корня репозитория:
python scripts/tools/validate_html_preview.py
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HTML_FILE = ROOT / "build" / "html-preview" / "index.html"

REQUIRED_MARKERS = [
    "<!doctype html>",
    "База знаний Этажи Борисоглебск",
    "HTML-превью CSV-структуры",
    "XLSX-источники",
    "table-wrap",
    "previewSearch",
    "quick-nav",
    "visibleCount",
]

MIN_SIZE_BYTES = 5000


def main():
    if not HTML_FILE.exists():
        print(f"HTML-превью не найдено: {HTML_FILE.relative_to(ROOT)}")
        return 1

    size = HTML_FILE.stat().st_size
    if size < MIN_SIZE_BYTES:
        print(f"HTML-превью слишком маленькое: {size} байт")
        return 1

    text = HTML_FILE.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]

    if missing:
        print("HTML-превью не прошло smoke-проверку.")
        for marker in missing:
            print(f"- Не найден маркер: {marker}")
        return 1

    print(f"HTML-превью прошло smoke-проверку: {HTML_FILE.relative_to(ROOT)} ({size} байт)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
