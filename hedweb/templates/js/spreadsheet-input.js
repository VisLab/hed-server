
/**
 * Adjust the column names if the has_column_names check box changes state.
 */
$('#has_column_names').on('change', function() {
    let spreadsheetFile = $('#spreadsheet_file')[0].files[0];
    let worksheetName = $('#worksheet_name option:selected').text();
    let hasColumnNames = $("#has_column_names").is(':checked')
    setColumnsInfo(spreadsheetFile, 'spreadsheet_flash', worksheetName, hasColumnNames, "show_indices")
})

/**
 * Spreadsheet event handler function. Checks if the file uploaded has a valid spreadsheet extension.
 */
$('#spreadsheet_file').on('change', function () {
    let spreadsheet = $('#spreadsheet_file');
    let spreadsheetPath = spreadsheet.val();
    let spreadsheetFile = spreadsheet[0].files[0];

    let hasColumnNames = $("#has_column_names").is(':checked');
    let worksheetNames = setColumnsInfo(spreadsheetFile, 'spreadsheet_input_flash',
        undefined, hasColumnNames, "show_indices");
    if (fileHasValidExtension(spreadsheetPath, EXCEL_FILE_EXTENSIONS)) {
        populateWorksheetDropdown(worksheetNames);
    } else if (fileHasValidExtension(spreadsheetPath, TEXT_FILE_EXTENSIONS)) {
        $('#worksheet_name').empty();
        $('#worksheet_select').hide();
    }
})


/**
 * Gets the information associated with the Excel sheet_name that was newly selected. This information contains
 * the names of the columns and column indices that contain HED tags.
 */
$('#worksheet_name').on('change', function () {
    let spreadsheetFile = $('#spreadsheet_file')[0].files[0];
    let worksheetName = $('#worksheet_name option:selected').text();
    let hasColumnNames = $("#has_column_names").is(':checked')
    clearFlashMessages();
    setColumnsInfo(spreadsheetFile, 'spreadsheet_flash', worksheetName, hasColumnNames, "show_indices");
});

function clearWorksheet() {
    $('#spreadsheet_display_name').text('');
    $('#worksheet_name').empty();
    $('#worksheet_select').hide();
    hideColumnInfo("show_indices");
}

function clearWorksheetFlashMessages() {
    flashMessageOnScreen('', 'success', 'spreadsheet_input_flash');
}

function getSpreadsheetFileName() {
    return $('#spreadsheet_file')[0].files[0].name;
}

function getWorksheetName() {
    return $('#worksheet_select option:selected').text();
}

/**
 * Populate the Excel sheet_name select box.
 * @param {Array} worksheetNames - An array containing the Excel sheet_name names.
 */
function populateWorksheetDropdown(worksheetNames) {
    if (Array.isArray(worksheetNames) && worksheetNames.length > 0) {
        $('#worksheet_select').show();
        $('#worksheet_name').empty();
        for (let i = 0; i < worksheetNames.length; i++) {
            $('#worksheet_name').append(new Option(worksheetNames[i], worksheetNames[i]) );
        }
    }
}
