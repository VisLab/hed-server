
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
    const section = document.getElementById('show_events_section');
    if (section) section.style.display = '';
    const columnEventsTable = document.getElementById('show_events_table');
    if (!columnEventsTable) return;
    columnEventsTable.replaceChildren();

    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['Include?', 'Column name (unique entries)', 'Categorical?'].forEach(text => {
        const th = document.createElement('th');
        th.scope = 'col';
        th.textContent = text;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    columnEventsTable.appendChild(thead);

    const tbody = document.createElement('tbody');
    if (columnList) {
        for (let i = 0; i < columnList.length; i++) {
            const columnName = columnList[i];
            const column = 'column_' + i;

            const row = document.createElement('tr');
            row.className = 'table-active';

            const tdUse = document.createElement('td');
            const useCheckbox = document.createElement('input');
            useCheckbox.type = 'checkbox';
            useCheckbox.className = 'form-check-input form-check';
            useCheckbox.name = column + '_use';
            useCheckbox.id = column + '_use';
            tdUse.appendChild(useCheckbox);
            row.appendChild(tdUse);

            const tdName = document.createElement('td');
            tdName.textContent = columnName + ' (' + columnCounts[columnName] + ')';
            row.appendChild(tdName);

            const tdCategory = document.createElement('td');
            const categoryCheckbox = document.createElement('input');
            categoryCheckbox.type = 'checkbox';
            categoryCheckbox.className = 'form-check-input form-check';
            categoryCheckbox.name = column + '_category';
            categoryCheckbox.id = column + '_category';
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'text';
            hiddenInput.hidden = true;
            hiddenInput.id = column + '_name';
            hiddenInput.name = column + '_name';
            hiddenInput.value = columnName;
            tdCategory.appendChild(categoryCheckbox);
            tdCategory.appendChild(hiddenInput);
            row.appendChild(tdCategory);

            tbody.appendChild(row);
        }
    }
    columnEventsTable.appendChild(tbody);
}

/**
 * Sets the components related to the spreadsheet columns when they are not empty.
 * @param {Array} columnList - An dictionary with column names
 * 
 */
function showIndices(columnList) {
    const section = document.getElementById('show_indices_section');
    if (section) section.style.display = '';
    const indicesTable = document.getElementById('show_indices_table');
    if (!indicesTable) return;
    indicesTable.replaceChildren();

    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['Include?', 'Column names'].forEach(text => {
        const th = document.createElement('th');
        th.scope = 'col';
        th.textContent = text;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    indicesTable.appendChild(thead);

    const tbody = document.createElement('tbody');
    if (columnList) {
        for (let i = 0; i < columnList.length; i++) {
            const columnName = columnList[i];
            const column = 'column_' + i;

            const row = document.createElement('tr');
            row.className = 'table-active';

            const tdUse = document.createElement('td');
            const useCheckbox = document.createElement('input');
            useCheckbox.type = 'checkbox';
            useCheckbox.className = 'form-check-input form-check';
            useCheckbox.name = column + '_use';
            useCheckbox.id = column + '_use';
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'text';
            hiddenInput.hidden = true;
            hiddenInput.id = column + '_name';
            hiddenInput.name = column + '_name';
            hiddenInput.value = columnName;
            tdUse.appendChild(useCheckbox);
            tdUse.appendChild(hiddenInput);
            row.appendChild(tdUse);

            const tdName = document.createElement('td');
            tdName.textContent = columnName;
            row.appendChild(tdName);

            tbody.appendChild(row);
        }
    }
    indicesTable.appendChild(tbody);
}
