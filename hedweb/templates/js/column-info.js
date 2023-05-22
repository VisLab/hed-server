
function clearColumnInfoFlashMessages() {
    if ($('#column_info_flash').length) {
        flashMessageOnScreen('', 'success', 'column_info_flash')
    }
}

/**
 * Hides  columns section in the form.
 * @param {string} table_tag - One of show_columns, show_indices, or show_events
 */
function hideColumnInfo(table_tag) {
    if ($(table_tag).length) {
        $(table_tag).hide()
    }
}

/**
 * Clears tag column text boxes.
 * @param {string} table_tag - One of show_columns, show_indices, or show_events
 */
function removeColumnInfo(table_tag) {
    if ($(table_tag).length) {
        $(table_tag).children().remove();
    }
}
//
// /**
//  * Gets information a file with columns. This information the names of the columns in the specified
//  * sheet_name and indices that contain HED tags.
//  * @param {File} columnsFile - File object with columns.
//  * @param {string} flashMessageLocation - ID name of the flash message element in which to display errors.
//  * @param {string} worksheetName - Name of sheet_name or undefined.
//  * @param {boolean} hasColumnNames - If true has column names
//  * @param {string} displayType - Show boxes with indices.
//  * @returns {Array} - Array of worksheet names
//  */
// function setColumnsInfo(columnsFile, flashMessageLocation, worksheetName=undefined, hasColumnNames=true,
//                         displayType="show_columns") {
//     if (columnsFile == null)
//         return null
//     let formData = new FormData();
//     formData.append('columns_file', columnsFile);
//     if (hasColumnNames) {
//         formData.append('has_column_names', 'on')
//     }
//     if (worksheetName !== undefined) {
//         formData.append('worksheet_selected', worksheetName)
//     }
//     let worksheet_names = null;
//     $.ajax({
//         type: 'POST',
//         url: "{{url_for('route_blueprint.columns_info_results')}}",
//         data: formData,
//         contentType: false,
//         processData: false,
//         dataType: 'json',
//         async: false,
//         success: function (info) {
//             if (info['message']) {
//                 flashMessageOnScreen(info['message'], 'error', flashMessageLocation);
//             } else {
//                 showColumnInfo(info['column_list'], info['column_counts'], hasColumnNames, displayType);
//                 worksheet_names = info['worksheet_names'];
//             }
//         },
//         error: function () {
//             flashMessageOnScreen('File could not be processed.', 'error', flashMessageLocation);
//         }
//     });
//     return worksheet_names;
// }

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
 * Shows the column names of the columns dictionary.
 * @param {Array} columnList - An array containing the file column names.
 */
function showColumns(columnList) {
    $('#show_columns').show();
    let columnNamesRow = $('<tr/>');

    for(const key of columnList) {
        columnNamesRow.append('<td>' + key + '&nbsp;</td>');
    }
    let columnTable = $('#show_columns_table');
    columnTable.empty();
    columnTable.append(columnNamesRow);
}


/**
 * Sets the components related to the spreadsheet columns when they are not empty.
 * @param {Array} columnList - An array containing the spreadsheet column names.
 * @param {Object} columnCounts - A dictionary containing the unique values in each column.
 * @param {boolean} hasColumnNames - boolean indicating whether array has column names.
 * @param {string} displayType - string indicating type of display.
 */
function showColumnInfo(columnList, countCounts, hasColumnNames= true, displayType="show_columns") {
    if (hasColumnNames && displayType === "show_columns") {
        showColumns(columnList);
    } else if (displayType === "show_indices") {
        showIndices(columnList, hasColumnNames);
    } else if (hasColumnNames && displayType === "show_events") {
        showEvents(columnList, countCounts);
    }
}

/**
 * Displays a vertical list of column names with counts and checkboxes for creating sidecar templates.
 * @param {Array} columnList - An array containing the spreadsheet column names.
 * @param {Object} columnCounts - A dictionary of the count of unique values in each column.
 * @param {boolean} hasColumnNames - A boolean indicating whether the first row represents column names
 * @param {boolean} show_categorical - A boolean indicating whether to show categorical checkboxes
 */
function showEvents(columnList, countCounts) {
    $('#show_events').show();
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
        let categoryBoxes = '<td><input type="checkbox" + class="form-check-input form-check" ' +
                'name="' + categoryName + '" id="' + categoryName + '">' +
                '<input type="text" hidden id="' + columnField + '" name="' + columnField +
                '" value="' + columnName + '"</td>';

        let row = '<tr class="table-active"><td><input type="checkbox" ' + 
                  'class="form-check-input form-check" name="' + useName + '" id="' + useName + '"></td>' +
            '<td>' + columnName  + ' (' + countCounts[columnName] + ')</td>' + categoryBoxes + '</tr>';
        contents = contents + row;
    }
    columnEventsTable.append(contents + '</table>')
}

/**
 * Sets the components related to the spreadsheet columns when they are not empty.
 * @param {Array} columnList - An dictionary with column names
 */
function showIndices(columnList) {
    $('#show_indices').show();
    let indicesTable = $('#show_indices_table');
    let contents = '<thead><tr><th scope="col">Tags?</th>' +
                   '<th scope="col">Column names</th>' + 
                    '<th scope="col">Tag prefix to use (prefixes end in /)</th></tr></thead>'
    indicesTable.empty();
    for (let i = 0; i < columnList.length; i++) {
        let columnName = columnList[i]
        let checkName = "column_" + i + "_check";
        let checkInput = "column_" + i + "_input";
        console.log(checkName)
        console.log(checkInput)
        let row = '<tr class="table-active"><td><input type="checkbox" ' + 
                  'class="form-check-input form-check" name="' + checkName + '" id="' + checkName + '"></td>' +
                  '<td>' + columnName + '</td>' +
                  '<td><input class="wide_text"' + ' type="text" name="' + checkInput +
                  '" id="' + checkInput + '" size="50"></td></tr>';
        console.log(row)
        contents = contents + row;
    }
    indicesTable.append(contents + '</table>')
}


/**
 * Sets the components related to the spreadsheet columns when they are not empty.
 * @param {Array} columnList - An dictionary with column names
 * @param {boolean} hasColumnNames - A boolean indicating whether the first row represents column names
 */
function showIndicesOld(columnList, hasColumnNames= true) {
    $('#show_indices').show();
    let contents = '<tr><th>Tags?</th><th>Column names</th><th>Tag prefix to use (prefixes end in /)</th></tr>'
    let i = 0;
    for(const key of columnList) {
        let column = "column_" + i;
        let columnName = key;
        if (!hasColumnNames) {
            columnName = "column_" + i;
        }
        let checkName = column + "_check";
        let checkInput = column + "_input";
        let row = '<tr><td><input type="checkbox" name="' + checkName + '" id="' + checkName + '" checked></td>' +
            '<td>' + columnName + '</td>' +
            '<td><input class="wide_text"' + ' type="text" name="' + checkInput +
            '" id="' + checkInput + '" size="50"></td></tr>';
        contents = contents + row;
        i = i + 1;
    }
    let columnTable = $('#show_indices_table');
    columnTable.empty();
    columnTable.append(contents)
}
