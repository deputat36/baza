# Примеры payload подсказок сделки

## Назначение

`build/deal-hint-api-examples.json` показывает безопасные примеры будущего обмена данными между карточкой сделки и базой знаний.

Проект Навигатора сделок сейчас не меняется.

## Что показывает файл

- какие признаки сделки можно передать в запросе;
- какие правила подсказок сработают;
- какие записи базы знаний вернутся как подсказки;
- для какой аудитории подсказка полезна.

## Источники

- `data/drafts/deal-hint-scenarios.csv`
- `build/deal-hint-rules.json`
- `build/knowledge-index.json`

## Команда

```bash
make deal-hint-api-examples
```

Полная проверка:

```bash
make preflight
```

## Артефакты

- `build/deal-hint-api-examples.json`
- `build/deal-hint-api-examples.md`
- `build/deal-hint-api-examples.csv`

## Ограничение

Это не рабочий API и не подключение к CRM. Это безопасный контрактный пример для будущей разработки интерфейса.
