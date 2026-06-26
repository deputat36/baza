# Preflight-проверка перед публикацией

## Назначение

Preflight — это быстрая проверка перед тем, как считать изменения готовыми.

## Команды

```bash
make install
make preflight
```

Если `make` недоступен, команды можно запустить отдельно:

```bash
pip install -r requirements.txt
python scripts/tools/validate_csv_structure.py
python scripts/tools/privacy_scan.py
python scripts/tools/build_workbook_from_csv.py
python scripts/tools/list_project_files.py
```

## Что проверяется

- CSV-структура.
- Потенциально рискованные данные.
- Сборка XLSX.
- Инвентаризация файлов.

## Что проверить вручную

- Нет ли реальных рабочих контактов.
- Нет ли данных клиентов.
- Нет ли закрытых условий.
- Все непроверенные записи имеют статус `CHECK` или `DRAFT`.
- Новые файлы описаны в рабочем журнале или документации.
