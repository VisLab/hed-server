
function clearColumnInfoFlashMessages() {
    if (document.getElementById('column_info_flash')) {
        flashMessageOnScreen('', 'success', 'column_info_flash')
    }
}

/**
 * Hides  columns section in the form.
 * @param {string} table - One of show_columns, show_indices, or show_events
 */
function hideColumnInfo(table) {
    const el = document.getElementById(table + '_section');
    if (el) el.style.display = 'none';
}

/**
 * Clears tag column text boxes.
 * @param {string} table - One of show_columns, show_indices, or show_events
 */
function removeColumnInfo(table) {
    const el = document.getElementById(table + '_table');
    if (el) {
        el.replaceChildren();
    }
}

function createFormData(columnsFile, hasColumnNames, worksheetName) {
    const formData = new FormData();
    formData.append('csrf_token', "{{ csrf_token() }}");
    formData.append('columns_file', columnsFile);
    if (hasColumnNames) {
        formData.append('has_column_names', 'on');
    }
    if (worksheetName !== undefined) {
        formData.append('worksheet_selected', worksheetName);
    }
    return formData;
}

async function getColumnsInfo(columnsFile, flashMessageLocation, worksheetName = undefined, hasColumnNames = true) {
    if (columnsFile == null) {
        return null;
    }

    try {
        const info = await getColumnsInfoHelper(columnsFile, flashMessageLocation, worksheetName, hasColumnNames);
        return info; // Return resolved information
    } catch (error) {
        return null; // Return null on error
    }
}

async function getColumnsInfoHelper(columnsFile, flashMessageLocation, worksheetName = undefined, hasColumnNames = true) {
    const formData = createFormData(columnsFile, hasColumnNames, worksheetName);
    try {
        const fetchUrl = "{{ url_for('route_blueprint.columns_info_results') }}";
        const response = await fetch(fetchUrl, {
            method: 'POST',
            body: formData,
            headers: {
               'X-CSRFToken': "{{ csrf_token() }}"
            },
            credentials: 'same-origin'
        });

        if (!response.ok) {
            throw new Error(`Network response was not ok. Status: ${response.status}`);
        }

        const info = await response.json();
        if (info['message']) {
            flashMessageOnScreen(info['message'], 'error', flashMessageLocation);
            return null;
        }
        return info; // Successfully resolved information
    } catch (error) {
        flashMessageOnScreen(`File could not be processed: ${error.message}`, 'error', flashMessageLocation);
        return null;
    }
}

/**
 * Displays a vertical list of column names with counts and checkboxes for creating sidecar templates.
 * @param {Array} columnList - An array containing the spreadsheet column names.
 * @param {Object} columnCounts - A dictionary of the count of unique values in each column.
 */
function showEvents(columnList, columnCounts) {
    document.getElementById('show_events_section').style.display = '';
    const columnEventsTable = document.getElementById('show_events_table');
    let contents = '<thead><tr><th scope="col">Include?</th>' +
                   '<th scope="col">Column name (unique entries)</th>' + 
                    '<th scope="col">Categorical?</th></tr></thead>'
    columnEventsTable.replaceChildren();
    if (columnList) {
        for (let i = 0; i < columnList.length; i++) {
            let columnName = columnList[i]
            let column = "column_" + i;
            let useName = column + "_use";
            let categoryName = column + "_category";
            let columnNameField = column + "_name";
            let categoryBoxes = '<td><input type="checkbox" class="form-check-input form-check" ' +
                'name="' + categoryName + '" id="' + categoryName + '">' +
                '<input type="text" hidden id="' + columnNameField + '" name="' + columnNameField +
                '" value="' + columnName + '"></td>';

            let row = '<tr class="table-active"><td><input type="checkbox" ' +
                'class="form-check-input form-check" name="' + useName + '" id="' + useName + '"></td>' +
                '<td>' + columnName + ' (' + columnCounts[columnName] + ')</td>' + categoryBoxes + '</tr>';
            contents = contents + row;
        }
    }
    columnEventsTable.insertAdjacentHTML('beforeend', contents + '</table>')
}

/**
 * Sets the components related to the spreadsheet columns when they are not empty.
 * @param {Array} columnList - An dictionary with column names
 * 
 */
function showIndices(columnList) {
    document.getElementById('show_indices_section').style.display = '';
    const indicesTable = document.getElementById('show_indices_table');
    let contents = '<thead><tr><th scope="col">Include?</th><th scope="col">Column names</th>';
    contents += '</tr></thead>';
    indicesTable.replaceChildren();
    if (columnList) {
        for (let i = 0; i < columnList.length; i++) {
            let columnName = columnList[i]
            let column = "column_" + i;
            let useName = column + "_use";
            let columnNameField = column + "_name";
            let row = '<tr class="table-active"><td><input type="checkbox" ' +
                'class="form-check-input form-check" name="' + useName + '" id="' + useName +
                '"><input type="text" hidden id="' + columnNameField + '" name="' + columnNameField +
                '" value="' + columnName + '"></td>' + '<td>' + columnName + '</td>';
            contents = contents + row + '</tr>';
        }
    }
    indicesTable.insertAdjacentHTML('beforeend', contents + '</table>')
}
