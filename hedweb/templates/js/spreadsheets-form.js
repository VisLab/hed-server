$(function () {
    prepareForm();
});


$('#definition_file').change(function() {
    clearFlashMessages();
})

/**
 * Set the options according to the action specified.
 */
$('#process_actions').change(function(){
    setOptions();
    clearSpreadsheet();
    clearFlashMessages();
});


/**
 * Submits the form if a file is given and the schema is selected.
 */
document.getElementById('spreadsheet_submit').addEventListener('click', function ()  {
    if (fileIsSpecified('spreadsheet_file', 'spreadsheet_flash', 'Spreadsheet is not specified.') &&
        schemaSpecifiedWhenOtherIsSelected()) {
        submitForm();
    }
});


/**
 * Clear the spreadsheet form.
 */
document.getElementById('spreadsheet_clear').addEventListener('click', function () {
    clearForm();
});


/**
 * Clear the fields in the form.
 */
function clearForm() {
    clearFlashMessages();
    clearSpreadsheet()
    $('#definition_file').val('');
    $("#validate").prop('checked', true);
    setOptions();
    hideOtherSchemaVersionFileUpload()
}

/**
 * Clear the flash messages that aren't related to the form submission.
 */
function clearFlashMessages() {
    clearColumnInfoFlashMessages();
    clearSchemaSelectFlashMessages();
    clearWorksheetFlashMessages();
    flashMessageOnScreen('', 'success', 'spreadsheet_flash');
}


/**
 * Prepare the spreadsheet form after the page is ready. The form will be reset to handle page refresh and
 * components will be hidden and populated.
 */
function prepareForm() {
    $('#spreadsheet_form')[0].reset();
    clearForm();
    getSchemaVersions()
}



/**
 * Set the options for the events depending on the action
 */
function setOptions() {
    let selectedElement = document.getElementById("process_actions");
    if (selectedElement.value === "validate") {
        showOption("check_for_warnings");
        hideOption("expand_defs");
    } else if (selectedElement.value === "to_long") {
        hideOption("check_for_warnings");
        showOption("expand_defs");
    } else if (selectedElement.value === "to_short") {
        hideOption("check_for_warnings");
        showOption("expand_defs");
    }
}

/**
 * Submit the form and return the results. If there are issues then they are returned in an attachment
 * file.
 */
async function submitForm() {
    const [formData, defaultName] = prepareSubmitForm("spreadsheet");
    const worksheetName = getWorksheetName();
    formData.append('worksheet_selected', worksheetName)
    const spreadsheetFile = getSpreadsheetFileName();
    const isExcel = fileHasValidExtension(spreadsheetFile, EXCEL_FILE_EXTENSIONS) &&
        !$("#validate").prop("checked");
    clearFlashMessages();
    flashMessageOnScreen('Spreadsheet is being processed ...', 'success',
        'spreadsheet_flash')

    try {
        const response = await fetch("{{url_for('route_blueprint.spreadsheets_results')}}", {
            method: "POST",
            body: formData,
        });
        if (!response.ok) {
            const errorData = await response.json()
            const error = new Error(errorData.message || `A response error occurred`);
            error.response = response;
            throw error;
        }
        console.log(response);
        let download;
        if (isExcel) {
            download = await response.blob();
        } else {
            download = await response.text();
        }
        handleResponse(response, download, defaultName, 'spreadsheet_flash');

    } catch (error) {
        if (error.response) {
            handleResponseFailure(error.response, message, error, defaultName, 'spreadsheet_flash');
        } else {
            // Network or unexpected error
            const info = `Unexpected error occurred [Source: ${defaultName}][Error: ${error.message}]`;
            flashMessageOnScreen(info, 'error', 'spreadsheet_flash');
        }
    }
}
