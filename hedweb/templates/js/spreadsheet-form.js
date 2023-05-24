
$(function () {
    prepareForm();
});


/**
 * Set the options according to the action specified.
 */
$('#process_actions').change(function(){
    setOptions();
    clearSpreadsheet();
});


/**
 * Submits the form if a file is given and the schema is selected.
 */
$('#spreadsheet_submit').on('click', function () {
    if (fileIsSpecified('#spreadsheet_file', 'spreadsheet_flash', 'Spreadsheet is not specified.') &&
        schemaSpecifiedWhenOtherIsSelected()) {
        submitForm();
    }
});

/**
 * Clears the form.
 */
$('#spreadsheet_clear').on('click', function () {
    clearForm();
});


/**
 * Clear the fields in the form.
 */
function clearForm() {
    clearFlashMessages();
    $('#spreadsheet_form')[0].reset();
    clearSpreadsheet()
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
    } else if (selectedElement.value === "to_long") {
        hideOption("check_for_warnings");
    } else if (selectedElement.value === "to_short") {
        hideOption("check_for_warnings");
    }
}

/**
 * Submit the form and return the results. If there are issues then they are returned in an attachment
 * file.
 */
function submitForm() {
    let spreadsheetForm = document.getElementById("spreadsheet_form");
    let formData = new FormData(spreadsheetForm);
    let worksheetName = getWorksheetName();
    formData.append('worksheet_selected', worksheetName)
    let selectedElement = document.getElementById("process_actions");
    formData.append("command_option", selectedElement.value)
    let prefix = 'issues';
    if(worksheetName) {
        prefix = prefix + '_worksheet_' + worksheetName;
    }
    let spreadsheetFile = getSpreadsheetFileName();
    let display_name = convertToResultsName(spreadsheetFile, prefix)
    clearFlashMessages();
    flashMessageOnScreen('Spreadsheet is being processed ...', 'success',
        'spreadsheet_flash')
    let isExcel = fileHasValidExtension(spreadsheetFile, EXCEL_FILE_EXTENSIONS) &&
            !$("#validate").prop("checked");
    $.ajax({
        type: 'POST',
        url: "{{url_for('route_blueprint.spreadsheet_results')}}",
        data: formData,
        contentType: false,
        processData: false,
        xhr: function () {
            let xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 2) {
                    if (xhr.status === 200 && isExcel) {
                        xhr.responseType = "blob";
                    } else {
                        xhr.responseType = "text";
                    }
                }
            };
            return xhr;
        },
        success: function (data, status, xqXHR) {
            getResponseSuccess(data, xqXHR, display_name, 'spreadsheet_flash')
        },
        error: function (xhr, status, errorThrown) {
            getResponseFailure(xhr, status, errorThrown, display_name, 'spreadsheet_flash')
        }
    })
}
