/**
 * Проверка закрытой Google Таблицы базы знаний.
 *
 * Скрипт не отправляет данные наружу. Он проверяет активную таблицу
 * и создаёт служебный лист `Проверка данных` с найденными замечаниями.
 *
 * Реальные контакты, ФИО и внутренние данные в публичный репозиторий не добавлять.
 */

const BAZA_VALIDATION_REPORT_SHEET = 'Проверка данных';
const BAZA_VALIDATION_SKIP_SHEETS = ['Главная', 'Справочники', BAZA_VALIDATION_REPORT_SHEET];
const BAZA_VALIDATION_STATUSES = ['DRAFT', 'CHECK', 'READY', 'VERIFIED', 'OUTDATED', 'PRIVATE', 'ARCHIVE'];
const BAZA_VALIDATION_PRIORITIES = ['Высокая', 'Средняя', 'Низкая'];

function validateBazaKnowledgeSheet() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const issues = [];

  spreadsheet.getSheets().forEach((sheet) => {
    const sheetName = sheet.getName();
    if (BAZA_VALIDATION_SKIP_SHEETS.indexOf(sheetName) !== -1) {
      return;
    }

    validateBazaSheet_(sheet, issues);
  });

  writeBazaValidationReport_(spreadsheet, issues);
}

function validateBazaSheet_(sheet, issues) {
  const lastRow = sheet.getLastRow();
  const lastColumn = sheet.getLastColumn();

  if (lastRow === 0 || lastColumn === 0) {
    issues.push(buildBazaIssue_(sheet.getName(), 0, '', 'Пустой лист', 'Лист не содержит данных'));
    return;
  }

  const headers = sheet.getRange(1, 1, 1, lastColumn).getValues()[0].map((value) => String(value).trim());
  validateBazaHeaders_(sheet.getName(), headers, issues);

  if (lastRow < 2) {
    issues.push(buildBazaIssue_(sheet.getName(), 1, '', 'Нет строк данных', 'Есть заголовок, но нет записей'));
    return;
  }

  const values = sheet.getRange(2, 1, lastRow - 1, lastColumn).getValues();
  const idColumn = findBazaColumnIndex_(headers, ['ID', 'id']);
  const statusColumn = findBazaColumnIndex_(headers, ['Статус', 'status']);
  const priorityColumn = findBazaColumnIndex_(headers, ['Приоритет', 'priority']);

  values.forEach((row, rowIndex) => {
    const rowNumber = rowIndex + 2;
    if (isBazaEmptyRow_(row)) {
      return;
    }

    if (idColumn !== -1 && !String(row[idColumn]).trim()) {
      issues.push(buildBazaIssue_(sheet.getName(), rowNumber, headers[idColumn], 'Пустой ID', 'У строки не заполнен ID'));
    }

    if (statusColumn !== -1) {
      validateBazaAllowedValue_(sheet, row, rowNumber, statusColumn, headers[statusColumn], BAZA_VALIDATION_STATUSES, issues);
    }

    if (priorityColumn !== -1) {
      validateBazaAllowedValue_(sheet, row, rowNumber, priorityColumn, headers[priorityColumn], BAZA_VALIDATION_PRIORITIES, issues);
    }
  });
}

function validateBazaHeaders_(sheetName, headers, issues) {
  const seen = {};

  headers.forEach((header, index) => {
    const columnName = columnToLetter_(index + 1);
    if (!header) {
      issues.push(buildBazaIssue_(sheetName, 1, columnName, 'Пустой заголовок', 'В первой строке есть пустой заголовок'));
      return;
    }

    if (seen[header]) {
      issues.push(buildBazaIssue_(sheetName, 1, header, 'Дубль заголовка', 'Заголовок повторяется'));
    }

    seen[header] = true;
  });
}

function validateBazaAllowedValue_(sheet, row, rowNumber, columnIndex, header, allowedValues, issues) {
  const value = String(row[columnIndex]).trim();
  if (!value) {
    return;
  }

  if (allowedValues.indexOf(value) === -1) {
    issues.push(buildBazaIssue_(sheet.getName(), rowNumber, header, 'Недопустимое значение', value));
  }
}

function writeBazaValidationReport_(spreadsheet, issues) {
  let reportSheet = spreadsheet.getSheetByName(BAZA_VALIDATION_REPORT_SHEET);
  if (!reportSheet) {
    reportSheet = spreadsheet.insertSheet(BAZA_VALIDATION_REPORT_SHEET);
  }

  reportSheet.clear();

  const rows = [
    ['Дата проверки', 'Лист', 'Строка', 'Колонка', 'Проблема', 'Значение или комментарий'],
  ];

  const checkedAt = new Date();
  if (issues.length === 0) {
    rows.push([checkedAt, '', '', '', 'Замечаний не найдено', '']);
  } else {
    issues.forEach((issue) => {
      rows.push([checkedAt, issue.sheet, issue.row, issue.column, issue.problem, issue.value]);
    });
  }

  reportSheet.getRange(1, 1, rows.length, rows[0].length).setValues(rows);
  reportSheet.setFrozenRows(1);
  reportSheet.autoResizeColumns(1, rows[0].length);
  reportSheet.getRange(1, 1, 1, rows[0].length)
    .setFontWeight('bold')
    .setBackground('#111827')
    .setFontColor('#ffffff');
}

function buildBazaIssue_(sheet, row, column, problem, value) {
  return {
    sheet: sheet,
    row: row,
    column: column,
    problem: problem,
    value: value,
  };
}

function findBazaColumnIndex_(headers, names) {
  for (let index = 0; index < headers.length; index += 1) {
    if (names.indexOf(headers[index]) !== -1) {
      return index;
    }
  }
  return -1;
}

function isBazaEmptyRow_(row) {
  return row.every((value) => !String(value).trim());
}

function columnToLetter_(column) {
  let temp = column;
  let letter = '';

  while (temp > 0) {
    const modulo = (temp - 1) % 26;
    letter = String.fromCharCode(65 + modulo) + letter;
    temp = Math.floor((temp - modulo) / 26);
  }

  return letter;
}
