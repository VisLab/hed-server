
/**
 * Adjust the column names if the has_column_names check box changes state.
 */
document.getElementById('has_column_names')?.addEventListener('change', function() {
    let spreadsheetFile = document.getElementById('spreadsheet_file').files[0];
    let worksheetName = document.getElementById('worksheet_name').options[document.getElementById('worksheet_name').selectedIndex].text;
    let hasColumnNames = document.getElementById('has_column_names').checked;
    setColumnsInfo(spreadsheetFile, 'spreadsheet_flash', worksheetName, hasColumnNames, "show_indices")
})

/**
 * Spreadsheet event handler function. Checks if the file uploaded has a valid spreadsheet extension.
 */
document.getElementById('spreadsheet_file')?.addEventListener('change', function () {
    clearFlashMessages();
    setColumnTable();
})


/**
 * Gets the information associated with the Excel sheet_name that was newly selected. This information contains
 * the names of the columns and column indices that contain HED tags.
 */
document.getElementById('worksheet_name')?.addEventListener('change', function () {
    clearFlashMessages();
    clearWorksheetFlashMessages();
    if (document.getElementById('show_indices_section') !== null) {
        setIndicesTable();
    }
});

function clearSpreadsheet() {
    document.getElementById('spreadsheet_file').value = '';
    document.getElementById('worksheet_name').replaceChildren();
    document.getElementById('worksheet_select').style.display = 'none';
    hideColumnInfo("show_indices");
    removeColumnInfo("show_indices")
}

function clearWorksheetFlashMessages() {
    flashMessageOnScreen('', 'success', 'spreadsheet_input_flash');
}

function getSpreadsheetFileName() {
    return document.getElementById('spreadsheet_file').files[0].name;
}

function getWorksheetName() {
    const selectElement = document.getElementById('worksheet_name');
    if (!selectElement || selectElement.options.length === 0 || selectElement.selectedIndex < 0) {
        return undefined;
    }
    return selectElement.options[selectElement.selectedIndex].text;
}

/**
 * Populate the Excel sheet_name select box.
 * @param {Array} worksheetNames - An array containing the Excel sheet_name names.
 */
function populateWorksheetDropdown(worksheetNames) {
    if (Array.isArray(worksheetNames) && worksheetNames.length > 0) {
        document.getElementById('worksheet_select').style.display = '';
        document.getElementById('worksheet_name').replaceChildren();
        for (let i = 0; i < worksheetNames.length; i++) {
            document.getElementById('worksheet_name').append(new Option(worksheetNames[i], worksheetNames[i]));
        }
    }
}

async function setIndicesTable() {
    clearColumnInfoFlashMessages();
    removeColumnInfo("show_indices_table")
    let spreadsheet = document.getElementById('spreadsheet_file');
    let worksheet = undefined
    if (document.getElementById('worksheet_name') !== null) {
        const wn = document.getElementById('worksheet_name');
        worksheet = wn.options[wn.selectedIndex].text;
    }
    let spreadsheetFile = spreadsheet.files[0];
    if (spreadsheetFile != null) {
        let info = await getColumnsInfo(spreadsheetFile, 'spreadsheet_flash', worksheet, true)
        let cols = info['column_list']
        let selectedElement = document.getElementById("process_actions");
        showIndices(cols)
    }
}

async function setColumnTable() {
    let spreadsheet = document.getElementById('spreadsheet_file');
    let spreadsheetPath = spreadsheet.value;
    let spreadsheetFile = spreadsheet.files[0];

    let info = await getColumnsInfo(spreadsheetFile, 'spreadsheet_input_flash', undefined, true);
    if (fileHasValidExtension(spreadsheetPath, EXCEL_FILE_EXTENSIONS)) {
        await populateWorksheetDropdown(info["worksheet_names"]);
    } else if (fileHasValidExtension(spreadsheetPath, TEXT_FILE_EXTENSIONS)) {
        document.getElementById('worksheet_name').replaceChildren();
        document.getElementById('worksheet_select').style.display = 'none';
    }

    if (document.getElementById('show_indices_section') !== null) {
        let selectedElement = document.getElementById("process_actions");
        setIndicesTable(selectedElement.value === "validate");
    }
}