
function clearColumnInfoFlashMessages() {
    if ($('#column_info_flash').length) {
        flashMessageOnScreen('', 'success', 'column_info_flash')
    }
}

/**
 * Hides  columns section in the form.
 * @param {string} table - One of show_columns, show_indices, or show_events
 */
function hideColumnInfo(table) {
    let table_section = '#' + table + '_section';
    $(table_section).hide();
}

/**
 * Clears tag column text boxes.
 * @param {string} table - One of show_columns, show_indices, or show_events
 */
function removeColumnInfo(table) {
    let table_tag = '#' + table + '_table';
    if ($(table_tag).length) {
        $(table_tag).children().remove();
    }
}

/**
 * Gets information a file with columns. This information the names of the columns in the specified
 * sheet_name and indices that contain HED tags.
 * @param {File} columnsFile - File object with columns.
 * @param {string} flashMessageLocation - ID name of the flash message element in which to display errors.
 * @param {string} worksheetName - Name of sheet_name or undefined.
 * @param {boolean} hasColumnNames - If true has column names
 * @returns {Array} - Array of worksheet names
 */
function getColumnsInfo(columnsFile, flashMessageLocation, worksheetName=undefined, hasColumnNames=true) {
    if (columnsFile == null)
        return null
    let formData = new FormData();
    formData.append('columns_file', columnsFile);
    if (hasColumnNames) {
        formData.append('has_column_names', 'on')
    }
    if (worksheetName !== undefined) {
        formData.append('worksheet_selected', worksheetName)
    }
    let return_info = null;
    $.ajax({
        type: 'POST',
        url: "{{url_for('route_blueprint.columns_info_results')}}",
        data: formData,
        contentType: false,
        processData: false,
        dataType: 'json',
        async: false,
        success: function (info) {
            if (info['message']) {
                flashMessageOnScreen(info['message'], 'error', flashMessageLocation);
            } else {
                return_info = info;
            }
        },
        error: function () {
            flashMessageOnScreen('File could not be processed.', 'error', flashMessageLocation);
        }
    });
    return return_info;
}


/**
 * Displays a vertical list of column names with counts and checkboxes for creating sidecar templates.
 * @param {Array} columnList - An array containing the spreadsheet column names.
 * @param {Object} columnCounts - A dictionary of the count of unique values in each column.
 */
function showEvents(columnList, columnCounts) {
    $('#show_events_section').show();
    let columnEventsTable = $('#show_events_table');
    let contents = '<thead><tr><th scope="col">Include?</th>' +
                   '<th scope="col">Column name (unique entries)</th>' + 
                    '<th scope="col">Categorical?</th></tr></thead>'
    columnEventsTable.empty();

    for (let i = 0; i < columnList.length; i++) {
        let columnName = columnList[i]
        let column = "column_" + i;
        let useName = column + "_use";
        let categoryName = column + "_category";
        let columnField = column + "_name";
        let categoryBoxes = '<td><input type="checkbox" class="form-check-input form-check" ' +
                            'name="' + categoryName + '" id="' + categoryName + '">' +
                            '<input type="text" hidden id="' + columnField + '" name="' + columnField +
                            '" value="' + columnName + '"</td>';

        let row = '<tr class="table-active"><td><input type="checkbox" ' + 
                  'class="form-check-input form-check" name="' + useName + '" id="' + useName + '"></td>' +
            '<td>' + columnName  + ' (' + columnCounts[columnName] + ')</td>' + categoryBoxes + '</tr>';
        contents = contents + row;
    }
    columnEventsTable.append(contents + '</table>')
}

/**
 * Sets the components related to the spreadsheet columns when they are not empty.
 * @param {Array} columnList - An dictionary with column names
 * @param {boolean} hasPrefixes - if true then the prefix inputs are displayed.
 * 
 */
function showIndices(columnList, hasPrefixes=false) {
    $('#show_indices_section').show();
    let indicesTable = $('#show_indices_table');
    let contents = '<thead><tr><th scope="col">Include?</th><th scope="col">Column names</th>';
    if (hasPrefixes) {
        contents += '<th scope="col">Use tag prefix:</th>';
    }
    contents += '</tr></thead>';
    indicesTable.empty();
    for (let i = 0; i < columnList.length; i++) {
        let columnName = columnList[i]
        let checkName = "column_" + i + "_check";
        let checkInput = "column_" + i + "_input";
        let row = '<tr class="table-active"><td><input type="checkbox" ' + 
                  'class="form-check-input form-check" name="' + checkName + '" id="' + checkName + '"></td>' +
                  '<td>' + columnName + '</td>'; 
        if (hasPrefixes) {
            row += '<td><input class="wide_text"' + ' type="text" name="' + checkInput +
                '" id="' + checkInput + '" size="50"></td>';
        }
        contents = contents + row + '</tr>';
    }
    indicesTable.append(contents + '</table>')
}
