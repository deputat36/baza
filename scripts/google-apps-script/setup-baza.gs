/**
 * База знаний специалиста по недвижимости | стартовая настройка Google Таблицы
 *
 * Скрипт создаёт базовые листы, закрепляет первую строку,
 * включает фильтр и добавляет служебные подсказки.
 *
 * Реальные контакты, ФИО и внутренние данные в этот файл не добавлять.
 */

function setupBazaKnowledgeSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const sheets = [
    'Главная',
    'Контакты',
    'Ситуации',
    'База знаний',
    'FAQ',
    'Практика',
    'Предложения изменений',
    'Справочники',
    'Синонимы',
    'Новостройки',
    'Подрядчики',
    'Обучение',
    'Метрики'
  ];

  sheets.forEach(function(name) {
    let sheet = ss.getSheetByName(name);
    if (!sheet) {
      sheet = ss.insertSheet(name);
    }

    sheet.setFrozenRows(1);

    if (sheet.getLastColumn() > 0 && sheet.getLastRow() > 0) {
      const range = sheet.getDataRange();
      if (!sheet.getFilter()) {
        range.createFilter();
      }
    }
  });

  setupMainSheet_(ss);
  setupStatusDictionary_(ss);
}

function setupMainSheet_(ss) {
  const sheet = ss.getSheetByName('Главная');
  sheet.clear();

  const rows = [
    ['База знаний специалиста по недвижимости', ''],
    ['Статус', 'Архитектурный MVP / подготовка рабочей версии'],
    ['Главное правило', 'Реальные контакты и внутренние данные хранить только в закрытой таблице'],
    ['', ''],
    ['Быстрые разделы', 'Назначение'],
    ['Контакты', 'Организации, службы, партнёры, роли'],
    ['Ситуации', 'Что делать в типовых рабочих случаях'],
    ['База знаний', 'Документы, инструкции, шаблоны'],
    ['FAQ', 'Короткие ответы на частые вопросы'],
    ['Практика', 'Проверенные полезные заметки сотрудников'],
    ['Предложения изменений', 'Ошибки, идеи и правки'],
    ['Справочники', 'Статусы, категории, приоритеты'],
    ['Метрики', 'Польза базы и результаты тестов']
  ];

  sheet.getRange(1, 1, rows.length, 2).setValues(rows);
  sheet.setFrozenRows(1);
  sheet.autoResizeColumns(1, 2);
}

function setupStatusDictionary_(ss) {
  const sheet = ss.getSheetByName('Справочники');

  const rows = [
    ['Статус', 'Описание'],
    ['DRAFT', 'Черновик'],
    ['CHECK', 'Нужно проверить'],
    ['VERIFIED', 'Проверено'],
    ['OUTDATED', 'Устарело'],
    ['PRIVATE', 'Только закрытая версия']
  ];

  sheet.getRange(1, 1, rows.length, 2).setValues(rows);
  sheet.setFrozenRows(1);
  sheet.autoResizeColumns(1, 2);
}
