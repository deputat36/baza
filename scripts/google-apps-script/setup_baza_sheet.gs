/*
 * Помощник оформления закрытой Google Таблицы базы знаний.
 *
 * Использование:
 * 1. Сначала запустить базовый скрипт scripts/google-apps-script/setup-baza.gs.
 * 2. Затем вставить этот файл в Apps Script.
 * 3. Запустить applyBazaSheetFormattingPlan().
 *
 * В публичный репозиторий не добавлять реальные рабочие контакты и приватные данные.
 */

const BAZA_FORMATTING_SHEETS = [
  { name: 'Главная', color: '#111827', frozenRows: 1, filter: false },
  { name: 'Контакты', color: '#2563eb', frozenRows: 1, filter: true },
  { name: 'Ситуации', color: '#16a34a', frozenRows: 1, filter: true },
  { name: 'База знаний', color: '#7c3aed', frozenRows: 1, filter: true },
  { name: 'FAQ', color: '#0891b2', frozenRows: 1, filter: true },
  { name: 'Практика', color: '#ea580c', frozenRows: 1, filter: true },
  { name: 'Предложения изменений', color: '#dc2626', frozenRows: 1, filter: true },
  { name: 'Справочники', color: '#64748b', frozenRows: 1, filter: true },
  { name: 'Синонимы', color: '#475569', frozenRows: 1, filter: true },
  { name: 'Новостройки', color: '#9333ea', frozenRows: 1, filter: true },
  { name: 'Подрядчики', color: '#0f766e', frozenRows: 1, filter: true },
  { name: 'Обучение', color: '#be123c', frozenRows: 1, filter: true },
  { name: 'Метрики', color: '#334155', frozenRows: 1, filter: true },
];

const BAZA_STATUS_VALUES = ['DRAFT', 'CHECK', 'READY', 'VERIFIED', 'OUTDATED', 'PRIVATE', 'ARCHIVE'];
const BAZA_PRIORITY_VALUES = ['Высокая', 'Средняя', 'Низкая'];
const BAZA_DATA_ROWS_LIMIT = 1000;

const BAZA_STATUS_COLORS = {
  DRAFT: '#fef3c7',
  CHECK: '#dbeafe',
  READY: '#dcfce7',
  VERIFIED: '#dcfce7',
  OUTDATED: '#fee2e2',
  PRIVATE: '#ede9fe',
  ARCHIVE: '#f3f4f6',
};

const BAZA_PRIORITY_COLORS = {
  'Высокая': '#fee2e2',
  'Средняя': '#fef3c7',
  'Низкая': '#dcfce7',
};

function applyBazaSheetFormattingPlan() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();

  BAZA_FORMATTING_SHEETS.forEach((config) => {
    const sheet = spreadsheet.getSheetByName(config.name);
    if (!sheet) {
      return;
    }

    applyBazaBaseFormat_(sheet, config);
    applyBazaKnownDropdowns_(sheet);
    applyBazaKnownConditionalFormatting_(sheet);
  });
}

function applyBazaBaseFormat_(sheet, config) {
  sheet.setTabColor(config.color);
  sheet.setFrozenRows(config.frozenRows);

  const lastColumn = Math.max(sheet.getLastColumn(), 1);
  const headerRange = sheet.getRange(1, 1, 1, lastColumn);

  headerRange
    .setFontWeight('bold')
    .setBackground('#111827')
    .setFontColor('#ffffff')
    .setVerticalAlignment('middle')
    .setWrap(true);

  sheet.setRowHeight(1, 42);

  if (config.filter && sheet.getLastRow() > 1 && !sheet.getFilter()) {
    sheet.getDataRange().createFilter();
  }
}

function applyBazaKnownDropdowns_(sheet) {
  const statusColumn = findBazaHeaderColumn_(sheet, ['Статус', 'status']);
  const priorityColumn = findBazaHeaderColumn_(sheet, ['Приоритет', 'priority']);

  if (statusColumn) {
    setBazaDropdown_(sheet, statusColumn, BAZA_STATUS_VALUES);
  }

  if (priorityColumn) {
    setBazaDropdown_(sheet, priorityColumn, BAZA_PRIORITY_VALUES);
  }
}

function applyBazaKnownConditionalFormatting_(sheet) {
  const rules = [];
  const statusColumn = findBazaHeaderColumn_(sheet, ['Статус', 'status']);
  const priorityColumn = findBazaHeaderColumn_(sheet, ['Приоритет', 'priority']);

  if (statusColumn) {
    Object.keys(BAZA_STATUS_COLORS).forEach((value) => {
      rules.push(buildBazaTextRule_(sheet, statusColumn, value, BAZA_STATUS_COLORS[value]));
    });
  }

  if (priorityColumn) {
    Object.keys(BAZA_PRIORITY_COLORS).forEach((value) => {
      rules.push(buildBazaTextRule_(sheet, priorityColumn, value, BAZA_PRIORITY_COLORS[value]));
    });
  }

  if (rules.length) {
    sheet.setConditionalFormatRules(rules);
  }
}

function setBazaDropdown_(sheet, column, values) {
  const rule = SpreadsheetApp.newDataValidation()
    .requireValueInList(values, true)
    .setAllowInvalid(false)
    .build();

  sheet.getRange(2, column, BAZA_DATA_ROWS_LIMIT, 1).setDataValidation(rule);
}

function buildBazaTextRule_(sheet, column, value, color) {
  return SpreadsheetApp.newConditionalFormatRule()
    .whenTextEqualTo(value)
    .setBackground(color)
    .setRanges([sheet.getRange(2, column, BAZA_DATA_ROWS_LIMIT, 1)])
    .build();
}

function findBazaHeaderColumn_(sheet, names) {
  const lastColumn = sheet.getLastColumn();
  if (!lastColumn) {
    return null;
  }

  const headers = sheet.getRange(1, 1, 1, lastColumn).getValues()[0];
  for (let index = 0; index < headers.length; index += 1) {
    const current = String(headers[index]).trim();
    if (names.indexOf(current) !== -1) {
      return index + 1;
    }
  }

  return null;
}
