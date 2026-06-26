/*
 * Шаблон настройки закрытой Google Таблицы базы знаний.
 *
 * Использование:
 * 1. Открыть закрытую Google Таблицу.
 * 2. Расширения -> Apps Script.
 * 3. Вставить этот файл.
 * 4. Запустить setupBazaKnowledgeSheet().
 *
 * В публичный репозиторий не добавлять реальные рабочие контакты и приватные данные.
 */

const BAZA_SHEETS = [
  { name: 'Главная', color: '#111827', frozenRows: 1, filter: false },
  { name: 'Контакты', color: '#2563eb', frozenRows: 1, filter: true },
  { name: 'Ситуации', color: '#16a34a', frozenRows: 1, filter: true },
  { name: 'База знаний', color: '#7c3aed', frozenRows: 1, filter: true },
  { name: 'Практика', color: '#ea580c', frozenRows: 1, filter: true },
  { name: 'Предложения изменений', color: '#dc2626', frozenRows: 1, filter: true },
  { name: 'Справочники', color: '#64748b', frozenRows: 1, filter: true },
];

const STATUS_VALUES = ['DRAFT', 'CHECK', 'READY', 'ARCHIVE'];
const PRIORITY_VALUES = ['Высокая', 'Средняя', 'Низкая'];
const DATA_ROWS_LIMIT = 1000;

const STATUS_COLORS = {
  DRAFT: '#fef3c7',
  CHECK: '#dbeafe',
  READY: '#dcfce7',
  ARCHIVE: '#f3f4f6',
};

const PRIORITY_COLORS = {
  'Высокая': '#fee2e2',
  'Средняя': '#fef3c7',
  'Низкая': '#dcfce7',
};

function setupBazaKnowledgeSheet() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();

  BAZA_SHEETS.forEach((config) => {
    const sheet = getOrCreateSheet_(spreadsheet, config.name);
    applySheetBaseFormat_(sheet, config);
    applyKnownDropdowns_(sheet);
    applyKnownConditionalFormatting_(sheet);
  });
}

function getOrCreateSheet_(spreadsheet, name) {
  const existing = spreadsheet.getSheetByName(name);
  if (existing) {
    return existing;
  }
  return spreadsheet.insertSheet(name);
}

function applySheetBaseFormat_(sheet, config) {
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

function applyKnownDropdowns_(sheet) {
  const statusColumn = findHeaderColumn_(sheet, ['Статус', 'status']);
  const priorityColumn = findHeaderColumn_(sheet, ['Приоритет', 'priority']);

  if (statusColumn) {
    setDropdown_(sheet, statusColumn, STATUS_VALUES);
  }

  if (priorityColumn) {
    setDropdown_(sheet, priorityColumn, PRIORITY_VALUES);
  }
}

function applyKnownConditionalFormatting_(sheet) {
  const rules = [];
  const statusColumn = findHeaderColumn_(sheet, ['Статус', 'status']);
  const priorityColumn = findHeaderColumn_(sheet, ['Приоритет', 'priority']);

  if (statusColumn) {
    Object.keys(STATUS_COLORS).forEach((value) => {
      rules.push(buildTextRule_(sheet, statusColumn, value, STATUS_COLORS[value]));
    });
  }

  if (priorityColumn) {
    Object.keys(PRIORITY_COLORS).forEach((value) => {
      rules.push(buildTextRule_(sheet, priorityColumn, value, PRIORITY_COLORS[value]));
    });
  }

  sheet.setConditionalFormatRules(rules);
}

function setDropdown_(sheet, column, values) {
  const rule = SpreadsheetApp.newDataValidation()
    .requireValueInList(values, true)
    .setAllowInvalid(false)
    .build();

  sheet.getRange(2, column, DATA_ROWS_LIMIT, 1).setDataValidation(rule);
}

function buildTextRule_(sheet, column, value, color) {
  return SpreadsheetApp.newConditionalFormatRule()
    .whenTextEqualTo(value)
    .setBackground(color)
    .setRanges([sheet.getRange(2, column, DATA_ROWS_LIMIT, 1)])
    .build();
}

function findHeaderColumn_(sheet, names) {
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
