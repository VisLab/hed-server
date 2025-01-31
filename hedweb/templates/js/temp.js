/**
 * Gets information a file with columns. This information the names of the columns in the specified
 * sheet_name and indices that contain HED tags.
 * @param {File} columnsFile - File object with columns.
 * @param {string} flashMessageLocation - ID name of the flash message element in which to display errors.
 * @param {string} worksheetName - Name of sheet_name or undefined.
 * @param {boolean} hasColumnNames - If true has column names
 * @returns {Array} - Array of worksheet names
 */
async function getColumnsInfoAsyncTemp(columnsFile, flashMessageLocation, worksheetName = undefined, hasColumnNames = true) {
    if (columnsFile == null) {
        return null;
    }
    console.log(columnsFile)
    let formData = new FormData();
    formData.append('columns_file', columnsFile);
    if (hasColumnNames) {
        formData.append('has_column_names', 'on')
    }
    if (worksheetName !== undefined) {
        formData.append('worksheet_selected', worksheetName)
    }
    try {
        console.log("Sending formData:", Array.from(formData.entries()));
        const response = await fetch("{{url_for('route_blueprint.columns_info_results')}}",
            {method: "POST", body: formData,
            headers: {'Accept': 'application/json'},});
        console.log(response);
        if (!response.ok) {
            throw new Error('Network response was not okay.');
        }

        const info = await response.json();
        console.log("Received info:", info);
        if (info['message']) {
            flashMessageOnScreen(info['message'], 'error', flashMessageLocation);
            return null;
        }
        return info;
    } catch (error) {
        console.error("Error", error);
        flashMessageOnScreen('File could not be processed.', 'error', flashMessageLocation);
        return null;
    }
}

// function getColumnsInfo(columnsFile, flashMessageLocation, worksheetName = undefined, hasColumnNames = true) {
//     if (columnsFile == null)
//         return null
//     let formData = new FormData();
//     console.log(columnsFile)
//     formData.append('columns_file', columnsFile);
//     if (hasColumnNames) {
//         formData.append('has_column_names', 'on')
//     }
//     if (worksheetName !== undefined) {
//         formData.append('worksheet_selected', worksheetName)
//     }
//     let return_info = null;
//     console.log("Sending formData:", Array.from(formData.entries()));
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
//                 return_info = info;
//             }
//         },
//         error: function () {
//             flashMessageOnScreen('File could not be processed.', 'error', flashMessageLocation);
//         }
//     });
//     return return_info;
// }

async function getColumnsInfoTemp(columnsFile, flashMessageLocation, worksheetName = undefined, hasColumnNames = true) {
    if (columnsFile == null) {
        return null;
    }

    try {
        const info = await getColumnsInfoHelper(columnsFile, flashMessageLocation, worksheetName, hasColumnNames);
        return info; // Return the resolved information
    } catch (error) {
        console.error('Error:', error);
        return null; // Return null if there’s an error
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
function getColumnsInfoTemp(columnsFile, flashMessageLocation, worksheetName=undefined, hasColumnNames=true) {
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

async function getColumnsInfoHelperTemp(columnsFile, flashMessageLocation, worksheetName = undefined, hasColumnNames = true) {
    const formData = createFormData(columnsFile, hasColumnNames, worksheetName);

    return new Promise((resolve, reject) => {
        $.ajax({
            type: 'POST',
            url: "{{url_for('route_blueprint.columns_info_results')}}",
            data: formData,
            contentType: false,
            processData: false,
            dataType: 'json',
            success: function (info) {
                if (info['message']) {
                    flashMessageOnScreen(info['message'], 'error', flashMessageLocation);
                    resolve(null);
                } else {
                    resolve(info);
                }
            },
            error: function () {
                flashMessageOnScreen('File could not be processed.', 'error', flashMessageLocation);
                reject(new Error('AJAX request failed.'));
            }
        });
    });
}
