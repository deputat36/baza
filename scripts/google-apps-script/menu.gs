/**
 * Пользовательское меню закрытой Google Таблицы базы знаний.
 *
 * Этот файл добавляет меню `База знаний` в интерфейс таблицы.
 * Для полной работы в Apps Script должны быть добавлены файлы:
 * - setup-baza.gs
 * - setup_baza_sheet.gs
 * - validate-baza-sheet.gs
 *
 * Скрипт не отправляет данные наружу и работает только с активной таблицей.
 */

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('База знаний')
    .addItem('1. Создать базовые листы', 'runBazaSetupFromMenu')
    .addItem('2. Применить оформление', 'runBazaFormattingFromMenu')
    .addItem('3. Проверить данные', 'runBazaValidationFromMenu')
    .addSeparator()
    .addItem('Полная подготовка таблицы', 'runFullBazaPreparationFromMenu')
    .addToUi();
}

function runBazaSetupFromMenu() {
  setupBazaKnowledgeSheet();
  showBazaMenuMessage_('Базовая структура таблицы подготовлена.');
}

function runBazaFormattingFromMenu() {
  applyBazaSheetFormattingPlan();
  showBazaMenuMessage_('Оформление, фильтры и выпадающие списки применены.');
}

function runBazaValidationFromMenu() {
  validateBazaKnowledgeSheet();
  showBazaMenuMessage_('Проверка завершена. Откройте лист `Проверка данных`.');
}

function runFullBazaPreparationFromMenu() {
  setupBazaKnowledgeSheet();
  applyBazaSheetFormattingPlan();
  validateBazaKnowledgeSheet();
  showBazaMenuMessage_('Полная подготовка завершена. Проверьте лист `Проверка данных`.');
}

function showBazaMenuMessage_(message) {
  SpreadsheetApp.getActiveSpreadsheet().toast(message, 'База знаний', 6);
}
