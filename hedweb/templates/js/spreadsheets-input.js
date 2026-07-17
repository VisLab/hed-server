
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
    setColumnTable('spreadsheet_file', 'spreadsheet_input_flash');
})

/**
 * 4-column spreadsheet event handler (sidecar merge). Handles file upload and worksheet population.
 */
document.getElementById('spreadsheet_4col')?.addEventListener('change', function () {
    clearFlashMessages();
    setColumnTable('spreadsheet_4col', 'spreadsheet_input_flash');
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
    // Clear regular spreadsheet file (spreadsheets page)
    const spreadsheetFile = document.getElementById('spreadsheet_file');
    if (spreadsheetFile) {
        spreadsheetFile.value = '';
    }
    
    // Clear 4-column spreadsheet file (sidecars page)
    const spreadsheet4col = document.getElementById('spreadsheet_4col');
    if (spreadsheet4col) {
        spreadsheet4col.value = '';
    }
    
    // Clear worksheet-related elements (shared)
    const worksheetName = document.getElementById('worksheet_name');
    if (worksheetName) {
        worksheetName.replaceChildren();
    }
    
    const worksheetSelect = document.getElementById('worksheet_select');
    if (worksheetSelect) {
        worksheetSelect.style.display = 'none';
    }
    
    // Column info handling (spreadsheets page)
    if (typeof hideColumnInfo === 'function') {
        hideColumnInfo("show_indices");
    }
    if (typeof removeColumnInfo === 'function') {
        removeColumnInfo("show_indices");
    }
}

function clearWorksheetFlashMessages() {
    flashMessageOnScreen('', 'success', 'spreadsheet_input_flash');
}

function getSpreadsheetFileName() {
    // Try to get from spreadsheet_file first (spreadsheets page)
    const spreadsheetFile = document.getElementById('spreadsheet_file');
    if (spreadsheetFile && spreadsheetFile.files.length > 0) {
        return spreadsheetFile.files[0].name;
    }
    
    // Fall back to spreadsheet_4col (sidecars page)
    const spreadsheet4col = document.getElementById('spreadsheet_4col');
    if (spreadsheet4col && spreadsheet4col.files.length > 0) {
        return spreadsheet4col.files[0].name;
    }
    
    return undefined;
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
    
    // Try to get from spreadsheet_file first, then fall back to spreadsheet_4col
    let spreadsheet = document.getElementById('spreadsheet_file');
    if (!spreadsheet || spreadsheet.files.length === 0) {
        spreadsheet = document.getElementById('spreadsheet_4col');
    }
    if (!spreadsheet || spreadsheet.files.length === 0) {
        return;
    }
    
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

async function setColumnTable(spreadsheetElementId = 'spreadsheet_file', flashMessageId = 'spreadsheet_input_flash') {
    let spreadsheet = document.getElementById(spreadsheetElementId);
    if (!spreadsheet) {
        return;
    }
    
    let spreadsheetPath = spreadsheet.value;
    let spreadsheetFile = spreadsheet.files[0];

    let info = await getColumnsInfo(spreadsheetFile, flashMessageId, undefined, true);
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