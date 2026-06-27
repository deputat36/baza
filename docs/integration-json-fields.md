# Поля JSON-контрактов

## Назначение

`data/dictionaries/integration-json-fields.csv` фиксирует минимальные обязательные верхнеуровневые поля JSON-артефактов будущей интеграции.

Это нужно, чтобы будущий интерфейс не зависел от случайной структуры файла.

## Проверка

```bash
make integration-json-fields
```

Полная проверка:

```bash
make preflight
```

## Артефакты

- `build/integration-json-fields-report.md`
- `build/integration-json-fields-report.csv`

## Ограничение

Проверка не заменяет полноценную JSON Schema. Сейчас она фиксирует только минимальный контракт: файл существует, читается как JSON и содержит обязательные верхнеуровневые поля.
