"""
Генератор стартовой страницы артефактов сборки.

Создаёт build/index.html со ссылками на HTML-превью, XLSX и отчёты.

Запуск из корня репозитория:
python scripts/tools/build_artifact_index.py
"""

from pathlib import Path
import html
from datetime import datetime

try:
    from workbook_config import ROOT, BUILD_DIR, OUTPUT_FILE
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    BUILD_DIR = ROOT / "build"
    OUTPUT_FILE = BUILD_DIR / "baza-knowledge-mvp.xlsx"

INDEX_FILE = BUILD_DIR / "index.html"

ARTIFACTS = [
    ("Главное", [
        ("HTML-превью", "html-preview/index.html", "Просмотр CSV-структуры в браузере"),
        ("XLSX-книга", OUTPUT_FILE.name, "Промежуточная Excel-книга"),
        ("GO/NO-GO отчет", "go-no-go-report.md", "Итоговое управленческое решение перед запуском"),
        ("GO/NO-GO CSV", "go-no-go-report.csv", "Табличная версия блокеров запуска"),
        ("Журнал решения запуска", "launch-decision-log.md", "Фиксация решения, условий и следующей проверки"),
        ("Журнал решения CSV", "launch-decision-log.csv", "Табличная версия решения запуска"),
        ("Метрики использования", "usage-metrics-report.md", "Использование базы после запуска и запросы без результата"),
        ("Метрики использования CSV", "usage-metrics-report.csv", "Табличная версия метрик использования"),
        ("План улучшений", "adoption-improvement-plan.md", "Действия по метрикам и обратной связи сотрудников"),
        ("План улучшений CSV", "adoption-improvement-plan.csv", "Табличная версия плана улучшений"),
        ("Еженедельный дайджест", "weekly-manager-digest.md", "Ключевые действия менеджера на неделю"),
        ("Еженедельный дайджест CSV", "weekly-manager-digest.csv", "Табличная версия недельной сводки"),
        ("Реестр действий", "manager-action-register.md", "Открытые управленческие действия по отчетам"),
        ("Реестр действий CSV", "manager-action-register.csv", "Табличная версия управленческих действий"),
        ("Маршрутизация департаментов", "department-routing-report.md", "Куда направлять вопросы центральному офису"),
        ("Маршрутизация департаментов CSV", "department-routing-report.csv", "Табличная версия маршрутов к департаментам"),
        ("Схема закрытых контактов", "private-contact-schema-report.md", "Поля приватного реестра контактов"),
        ("Схема закрытых контактов CSV", "private-contact-schema-report.csv", "Табличная версия схемы закрытых контактов"),
        ("Управленческая сводка", "manager-dashboard.md", "Короткий dashboard для менеджера"),
        ("Управленческая сводка CSV", "manager-dashboard.csv", "Табличная версия dashboard"),
        ("Навигация по ролям", "role-navigation-report.md", "С чего начинать СПН, менеджеру, юристу, брокеру и администратору"),
        ("Навигация по ролям CSV", "role-navigation-report.csv", "Табличная версия ролевых маршрутов"),
        ("Ответственные за разделы", "section-ownership-report.md", "Кто отвечает за актуальность и качество разделов"),
        ("Ответственные за разделы CSV", "section-ownership-report.csv", "Табличная версия ответственности"),
        ("Приемочные сценарии", "office-acceptance-test-report.md", "Ручная проверка рабочих действий сотрудников"),
        ("Приемочные сценарии CSV", "office-acceptance-test-report.csv", "Табличная версия приемочных сценариев"),
        ("Обучение по ролям", "role-training-report.md", "Что должны уметь сотрудники перед запуском"),
        ("Обучение по ролям CSV", "role-training-report.csv", "Табличная версия плана обучения"),
        ("Пакет запуска", "office-launch-packet.md", "Единый порядок проверки перед запуском базы"),
        ("Пакет запуска CSV", "office-launch-packet.csv", "Табличная версия пакета запуска"),
        ("Чек-лист запуска", "office-launch-checklist-report.md", "Что закрыть перед запуском базы в офисе"),
        ("Чек-лист запуска CSV", "office-launch-checklist-report.csv", "Табличная версия чек-листа запуска"),
        ("Регламент эксплуатации", "operating-rhythm-report.md", "Что проверять регулярно после запуска"),
        ("Регламент эксплуатации CSV", "operating-rhythm-report.csv", "Табличная версия регулярных задач"),
        ("JSON-индекс знаний", "knowledge-index.json", "Read-only индекс для поиска и будущих интеграций"),
        ("Preflight-сводка", "preflight-summary.md", "Список артефактов и ручной чек-лист"),
    ]),
    ("Готовность и качество данных", [
        ("Готовность к запуску", "launch-readiness-report.md", "Статусы READY/CHECK/DRAFT по листам"),
        ("Готовность к запуску CSV", "launch-readiness-report.csv", "Табличная версия отчёта готовности"),
        ("Актуальность данных", "data-freshness-report.md", "Сроки проверки контактов, инструкций и правил"),
        ("Актуальность данных CSV", "data-freshness-report.csv", "Табличная версия отчёта актуальности"),
        ("Очередь изменений", "change-request-report.md", "Открытые предложения, исправления, ответственные и приоритеты"),
        ("Очередь изменений CSV", "change-request-report.csv", "Табличная версия очереди предложений"),
        ("Незаполненные данные", "missing-values-report.md", "Пустые ID, статусы, приоритеты и ячейки"),
        ("Незаполненные данные CSV", "missing-values-report.csv", "Табличная версия отчёта по пустым значениям"),
        ("Отчёт по данным", "data-report.md", "Техническая сводка по CSV"),
        ("Реестр ID", "id-registry.md", "ID, префиксы и возможные дубли"),
        ("Схемы CSV", "schema-report.md", "Заголовки и схемы CSV"),
    ]),
    ("Связи и будущая интеграция", [
        ("Отчёт по связям", "relationship-report.md", "Проверка связей между SIT, DOC, ORG, INS и другими ID"),
        ("Отчёт по связям CSV", "relationship-report.csv", "Табличная версия связей и отсутствующих ID"),
        ("Правила подсказок", "deal-hint-rules.json", "JSON-контракт будущих подсказок карточки сделки"),
        ("Отчёт правил подсказок", "deal-hint-rules-report.md", "Проверка правил и связанных ID"),
        ("Отчёт правил CSV", "deal-hint-rules-report.csv", "Табличная версия правил подсказок"),
        ("Отчёт сигналов", "deal-signal-report.md", "Покрытие словаря сигналов правилами"),
        ("Отчёт сигналов CSV", "deal-signal-report.csv", "Табличная версия покрытия сигналов"),
        ("Предпросмотр подсказок", "deal-hint-preview.md", "Проверка срабатывания правил на безопасных сценариях"),
        ("Предпросмотр подсказок JSON", "deal-hint-preview.json", "Машиночитаемый предпросмотр будущих подсказок"),
        ("Предпросмотр подсказок CSV", "deal-hint-preview.csv", "Табличная версия предпросмотра"),
        ("UI-карта подсказок", "deal-hint-ui-map-report.md", "Проверка размещения подсказок по зонам интерфейса"),
        ("UI-карта подсказок JSON", "deal-hint-ui-map.json", "Машиночитаемая карта размещения подсказок"),
        ("UI-карта подсказок CSV", "deal-hint-ui-map-report.csv", "Табличная версия UI-карты"),
        ("Примеры payload", "deal-hint-api-examples.md", "Примеры request и response для будущих подсказок"),
        ("Примеры payload JSON", "deal-hint-api-examples.json", "Машиночитаемые примеры будущего обмена данными"),
        ("Примеры payload CSV", "deal-hint-api-examples.csv", "Табличная версия примеров payload"),
        ("Отчёт аудиторий", "deal-audience-report.md", "Покрытие аудиторий правилами и сценариями"),
        ("Отчёт аудиторий CSV", "deal-audience-report.csv", "Табличная версия покрытия аудиторий"),
        ("Отчёт видимости данных", "integration-data-visibility-report.md", "Что можно хранить публично, а что только в закрытом контуре"),
        ("Отчёт видимости CSV", "integration-data-visibility-report.csv", "Табличная версия видимости данных"),
        ("Отчёт доступа", "integration-access-report.md", "Матрица доступа ролей к публичным и закрытым данным"),
        ("Отчёт доступа CSV", "integration-access-report.csv", "Табличная версия матрицы доступа"),
        ("Отчёт полей JSON", "integration-json-fields-report.md", "Проверка обязательных полей JSON-контрактов"),
        ("Отчёт полей JSON CSV", "integration-json-fields-report.csv", "Табличная версия проверки JSON-полей"),
        ("Отчёт контрактов интеграции", "integration-contract-report.md", "Проверка read-only контрактов будущей интеграции"),
        ("Отчёт контрактов CSV", "integration-contract-report.csv", "Табличная версия контрактов интеграции"),
        ("JSON-индекс знаний", "knowledge-index.json", "Контракт чтения для будущих интерфейсов"),
    ]),
    ("Google Таблица", [
        ("План листов", "google-sheet-tabs-plan.md", "Порядок листов закрытой Google Таблицы"),
        ("План листов CSV", "google-sheet-tabs-plan.csv", "Табличная версия плана листов"),
        ("План выпадающих списков", "google-sheet-validation-plan.md", "Справочники для валидаций"),
        ("План выпадающих списков CSV", "google-sheet-validation-plan.csv", "Табличная версия плана валидаций"),
        ("План оформления", "google-sheet-formatting-plan.md", "Цвета, фильтры и условное форматирование"),
        ("План оформления CSV", "google-sheet-formatting-plan.csv", "Табличная версия плана оформления"),
        ("План импорта", "import-plan.md", "Порядок переноса CSV"),
        ("План импорта CSV", "import-plan.csv", "Табличная версия плана импорта"),
    ]),
    ("Покрытие", [
        ("Покрытие источников", "source-coverage-report.md", "Какие CSV входят в XLSX"),
    ]),
]


def escape(value):
    return html.escape(str(value or ""))


def artifact_status(path: str):
    artifact_path = BUILD_DIR / path
    if artifact_path.exists():
        if artifact_path.is_file():
            return "есть", f"{artifact_path.stat().st_size} байт"
        return "есть", "каталог"
    return "нет", "-"


def render_cards():
    sections = []
    for group, artifacts in ARTIFACTS:
        cards = []
        for title, path, description in artifacts:
            status, size = artifact_status(path)
            status_class = "ok" if status == "есть" else "missing"
            cards.append(f"""
            <article class=\"card\">
              <div class=\"card-top\">
                <h3>{escape(title)}</h3>
                <span class=\"status {status_class}\">{escape(status)}</span>
              </div>
              <p>{escape(description)}</p>
              <p class=\"meta\">{escape(path)} · {escape(size)}</p>
              <a href=\"{escape(path)}\">Открыть</a>
            </article>
            """)
        sections.append(f"""
        <section>
          <h2>{escape(group)}</h2>
          <div class=\"grid\">{''.join(cards)}</div>
        </section>
        """)
    return "\n".join(sections)


def build_html():
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Артефакты сборки базы знаний</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --panel: #ffffff;
      --text: #111827;
      --muted: #64748b;
      --border: #e5e7eb;
      --accent: #dc2626;
      --ok: #15803d;
      --bad: #b91c1c;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }}
    header {{ background: #111827; color: #fff; padding: 28px 24px; }}
    main {{ width: min(1180px, calc(100% - 32px)); margin: 24px auto 48px; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin: 24px 0 12px; font-size: 20px; }}
    h3 {{ margin: 0; font-size: 16px; }}
    .summary {{ color: #cbd5e1; margin: 0; }}
    .notice {{ background: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px; color: #9a3412; padding: 14px 16px; }}
    .grid {{ display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }}
    .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }}
    .card-top {{ align-items: flex-start; display: flex; gap: 12px; justify-content: space-between; }}
    .card p {{ color: var(--muted); margin: 10px 0; }}
    .card .meta {{ font-family: Consolas, monospace; font-size: 12px; }}
    .card a {{ color: var(--accent); font-weight: 700; text-decoration: none; }}
    .status {{ border-radius: 999px; font-size: 12px; padding: 3px 8px; white-space: nowrap; }}
    .status.ok {{ background: #dcfce7; color: var(--ok); }}
    .status.missing {{ background: #fee2e2; color: var(--bad); }}
  </style>
</head>
<body>
  <header>
    <h1>Артефакты сборки базы знаний</h1>
    <p class=\"summary\">Сгенерировано: {escape(generated_at)}.</p>
  </header>
  <main>
    <div class=\"notice\">Это навигационная страница по артефактам сборки. Реальные рабочие данные должны храниться только в закрытой Google Таблице.</div>
    {render_cards()}
  </main>
</body>
</html>
"""


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    INDEX_FILE.write_text(build_html(), encoding="utf-8")
    print(f"Готово: {INDEX_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
