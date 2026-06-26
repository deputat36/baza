"""
Генератор статического HTML-превью базы знаний.

Создаёт файл build/html-preview/index.html из CSV-файлов проекта.
Превью нужно для быстрого просмотра структуры без Excel и Google Таблицы.

Запуск из корня репозитория:
python scripts/tools/build_html_preview.py
"""

from pathlib import Path
import csv
import html
from datetime import datetime

try:
    from workbook_config import ROOT, SHEETS
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    SHEETS = []

BUILD_DIR = ROOT / "build" / "html-preview"
OUTPUT_FILE = BUILD_DIR / "index.html"
MAX_ROWS_PER_TABLE = 30

EXTRA_CSV_DIRS = [
    ROOT / "data" / "drafts",
    ROOT / "data" / "dictionaries",
    ROOT / "templates",
]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.reader(file))


def escape(value):
    return html.escape(str(value or ""))


def iter_workbook_sources():
    for sheet in SHEETS:
        if isinstance(sheet, dict):
            title = sheet.get("title") or sheet.get("name") or "Без названия"
            raw_sources = sheet.get("sources") or sheet.get("source") or []
        else:
            title = sheet[0]
            raw_sources = sheet[1]

        if isinstance(raw_sources, (str, Path)):
            raw_sources = [raw_sources]

        for source in raw_sources:
            yield title, ROOT / source


def collect_sources():
    sources = []
    used_paths = set()

    for sheet_title, source_path in iter_workbook_sources():
        if source_path.exists():
            sources.append({
                "title": f"{sheet_title}: {source_path.stem}",
                "path": source_path,
                "group": "XLSX-источники",
            })
            used_paths.add(source_path.resolve())

    for directory in EXTRA_CSV_DIRS:
        if not directory.exists():
            continue

        for path in sorted(directory.glob("*.csv")):
            if path.resolve() in used_paths:
                continue
            sources.append({
                "title": path.stem,
                "path": path,
                "group": "Дополнительные CSV",
            })

    return sources


def render_table(rows):
    if not rows:
        return "<p class=\"muted\">Файл пустой.</p>"

    header = rows[0]
    body = rows[1:MAX_ROWS_PER_TABLE + 1]
    hidden_count = max(len(rows) - 1 - len(body), 0)

    parts = ["<div class=\"table-wrap\"><table>"]
    parts.append("<thead><tr>")
    for cell in header:
        parts.append(f"<th>{escape(cell)}</th>")
    parts.append("</tr></thead>")

    parts.append("<tbody>")
    for row in body:
        parts.append("<tr>")
        for index in range(len(header)):
            value = row[index] if index < len(row) else ""
            parts.append(f"<td>{escape(value)}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table></div>")

    if hidden_count:
        parts.append(f"<p class=\"muted\">Показано {len(body)} строк из {len(rows) - 1}. Ещё строк: {hidden_count}.</p>")

    return "".join(parts)


def render_source_card(source):
    relative = source["path"].relative_to(ROOT).as_posix()
    try:
        rows = read_csv(source["path"])
        row_count = max(len(rows) - 1, 0)
        column_count = len(rows[0]) if rows else 0
        table = render_table(rows)
        status = f"{row_count} строк, {column_count} колонок"
    except Exception as exc:
        table = f"<p class=\"error\">Не удалось прочитать файл: {escape(exc)}</p>"
        status = "ошибка чтения"

    return f"""
    <section class=\"card\">
      <div class=\"card-head\">
        <div>
          <p class=\"eyebrow\">{escape(source['group'])}</p>
          <h2>{escape(source['title'])}</h2>
        </div>
        <span class=\"badge\">{escape(status)}</span>
      </div>
      <p class=\"path\">{escape(relative)}</p>
      {table}
    </section>
    """


def build_html():
    sources = collect_sources()
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    cards = "\n".join(render_source_card(source) for source in sources)

    return f"""<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>База знаний Этажи Борисоглебск — HTML-превью</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --panel: #ffffff;
      --text: #111827;
      --muted: #64748b;
      --border: #e5e7eb;
      --accent: #dc2626;
      --accent-dark: #991b1b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    header {{
      background: #111827;
      color: #ffffff;
      padding: 28px 24px;
    }}
    main {{
      width: min(1280px, calc(100% - 32px));
      margin: 24px auto 48px;
    }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin: 0; font-size: 20px; }}
    .summary {{ color: #cbd5e1; margin: 0; }}
    .grid {{ display: grid; gap: 18px; }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
    }}
    .card-head {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 8px;
    }}
    .eyebrow {{
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .04em;
      margin: 0 0 4px;
      text-transform: uppercase;
    }}
    .badge {{
      background: #fee2e2;
      color: var(--accent-dark);
      border-radius: 999px;
      padding: 4px 10px;
      font-size: 12px;
      white-space: nowrap;
    }}
    .path {{
      color: var(--muted);
      font-family: Consolas, monospace;
      font-size: 13px;
      margin: 0 0 12px;
    }}
    .table-wrap {{ overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; }}
    table {{ border-collapse: collapse; width: 100%; min-width: 760px; }}
    th, td {{
      border-bottom: 1px solid var(--border);
      padding: 8px 10px;
      text-align: left;
      vertical-align: top;
      font-size: 13px;
    }}
    th {{
      background: #f3f4f6;
      font-weight: 700;
      position: sticky;
      top: 0;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    .muted {{ color: var(--muted); font-size: 13px; }}
    .error {{ color: var(--accent-dark); font-weight: 700; }}
    .notice {{
      background: #fff7ed;
      border: 1px solid #fed7aa;
      border-radius: 8px;
      color: #9a3412;
      margin-bottom: 18px;
      padding: 14px 16px;
    }}
  </style>
</head>
<body>
  <header>
    <h1>База знаний Этажи Борисоглебск</h1>
    <p class=\"summary\">HTML-превью CSV-структуры. Сгенерировано: {escape(generated_at)}.</p>
  </header>
  <main>
    <div class=\"notice\">
      Это техническое превью публичной части проекта. Реальные внутренние контакты и клиентские данные должны храниться только в закрытой Google Таблице.
    </div>
    <div class=\"grid\">
      {cards}
    </div>
  </main>
</body>
</html>
"""


def main():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(build_html(), encoding="utf-8")
    print(f"HTML-превью создано: {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
