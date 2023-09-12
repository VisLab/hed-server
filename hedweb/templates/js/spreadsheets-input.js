
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
    clearFlashMessages();
    let spreadsheet = $('#spreadsheet_file');
    let spreadsheetPath = spreadsheet.val();
    let spreadsheetFile = spreadsheet[0].files[0];

    let info = getColumnsInfo(spreadsheetFile, 'spreadsheet_input_flash', undefined,true);
    if (fileHasValidExtension(spreadsheetPath, EXCEL_FILE_EXTENSIONS)) {
        populateWorksheetDropdown(info["worksheet_names"]);
    } else if (fileHasValidExtension(spreadsheetPath, TEXT_FILE_EXTENSIONS)) {
        $('#worksheet_name').empty();
        $('#worksheet_select').hide();
    }
    
    if ($('#show_indices_section') != null) {
        let selectedElement = document.getElementById("process_actions");
        setIndicesTable(selectedElement.value === "validate");
    }
})


/**
 * Gets the information associated with the Excel sheet_name that was newly selected. This information contains
 * the names of the columns and column indices that contain HED tags.
 */
$('#worksheet_name').on('change', function () {
    clearFlashMessages();
    clearWorksheetFlashMessages()
    if ($('#show_indices_section') != null) {
        setIndicesTable();
    }
});

function clearSpreadsheet() {
    $('#spreadsheet_file').val('');
    $('#worksheet_name').empty();
    $('#worksheet_select').hide();
    hideColumnInfo("show_indices");
    removeColumnInfo("show_indices")
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

function setIndicesTable() {
    clearColumnInfoFlashMessages();
    removeColumnInfo("show_indices_table")
    let spreadsheet = $('#spreadsheet_file')[0];
    let worksheet = undefined
    if ($('#worksheet_name') != null){
        worksheet = $('#worksheet_name option:selected').text();
    }
    let spreadsheetFile = spreadsheet.files[0];
    if (spreadsheetFile != null) {
        let info = getColumnsInfo(spreadsheetFile, 'spreadsheet_flash', worksheet, true)
        let cols = info['column_list']
        let selectedElement = document.getElementById("process_actions");
        showIndices(cols, selectedElement.value === "validate")
    }
}
