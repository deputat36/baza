# Сущности будущего CRM-модуля

Этот файл описывает возможную структуру данных, если база знаний будет перенесена из Google Таблицы в CRM или отдельный внутренний портал.

## knowledge_items

Основная таблица объектов знаний.

| Поле | Тип | Назначение |
|---|---|---|
| id | int | Внутренний ID |
| code | varchar | Код записи: ORG-0301, DOC-0001 |
| type | varchar | Тип объекта |
| category_id | int | Категория |
| title | varchar | Название |
| short_description | text | Краткое описание |
| content | text | Основное содержание |
| priority | tinyint | Приоритет 1–5 |
| status | varchar | Статус |
| source | varchar | Источник |
| checked_at | date | Дата проверки |
| checked_by | int | Кто проверил |
| created_at | datetime | Дата создания |
| updated_at | datetime | Дата обновления |

## contacts

Контакты организаций и людей.

| Поле | Тип | Назначение |
|---|---|---|
| id | int | ID |
| item_id | int | Связь с knowledge_items |
| organization | varchar | Организация |
| person_name | varchar | Контактное лицо |
| position | varchar | Должность |
| phone | varchar | Телефон |
| phone_extra | varchar | Дополнительный телефон |
| email | varchar | Email |
| address | varchar | Адрес |
| website | varchar | Сайт |
| work_hours | varchar | График |

## knowledge_relations

Связи между объектами.

| Поле | Тип | Назначение |
|---|---|---|
| id | int | ID |
| from_item_id | int | Исходный объект |
| to_item_id | int | Связанный объект |
| relation_type | varchar | Тип связи |
| comment | text | Комментарий |

## practice_notes

Практические заметки сотрудников.

| Поле | Тип | Назначение |
|---|---|---|
| id | int | ID |
| item_id | int | К какой записи относится |
| author_id | int | Автор |
| note | text | Текст заметки |
| usefulness | tinyint | Полезность 1–5 |
| status | varchar | На проверке, принято, отклонено |
| created_at | datetime | Дата добавления |

## change_requests

Предложения изменений.

| Поле | Тип | Назначение |
|---|---|---|
| id | int | ID |
| item_id | int | Какая запись меняется |
| author_id | int | Кто предложил |
| what_change | text | Что изменить |
| old_value | text | Что было |
| new_value | text | Что стало |
| reason | text | Почему важно |
| status | varchar | На проверке, принято, отклонено |
| created_at | datetime | Дата предложения |
| reviewed_at | datetime | Дата проверки |
| reviewed_by | int | Кто проверил |
