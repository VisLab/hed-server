$(function () {
    prepareForm();
});

/**
 * Set the options according to the action specified.
 */
$('#process_actions').change(function(){
    setOptions();
    clearFlashMessages();
});

$('#sidecar_file').change(function() {
    clearFlashMessages();
})


/**
 * Submit the form if schema and json file specified.
 */
document.getElementById('sidecar_submit').addEventListener('click', function () {
    if (!schemaSpecifiedWhenOtherIsSelected()) {
        return;
    }

    const processActions = document.getElementById('process_actions');
    if (processActions.value === "merge_spreadsheet" ||
        fileIsSpecified('sidecar_file', 'sidecar_flash', 'Sidecar file is not specified.')) {
        submitForm();
    }
});

/**
 * Clear the sidecar form.
 */
document.getElementById('sidecar_clear').addEventListener('click', function () {
    clearForm();
});


/**
 * Clear the fields in the form.
 */
function clearForm() {
    clearFlashMessages();
    setOptions();
    $('#sidecar_file').val('');
    clearSpreadsheet();
    hideOtherSchemaVersionFileUpload()
}

/**
 * Clear the flash messages that aren't related to the form submission.
 */
function clearFlashMessages() {
    clearSchemaSelectFlashMessages();
    flashMessageOnScreen('', 'success', 'sidecar_flash');
}

/**
 * Prepare the validation form after the page is ready. The form will be reset to handle page refresh and
 * components will be hidden and populated.
 */
function prepareForm() {
    clearForm();
    $('#sidecar_form')[0].reset();
    $('#process_actions').val('validate');
    getSchemaVersions()
    hideOtherSchemaVersionFileUpload();
}

/**
 * Set the options for the events depending on the action
 */
function setOptions() {
    let selectedElement = document.getElementById("process_actions");
    if (selectedElement.value === "validate") {
        hideOption("expand_defs");
        showOption("check_for_warnings");
        hideOption("include_description_tags");
        $("#sidecar_input_section").show();
        $("#spreadsheet_input_section").hide();
        $("#schema_pulldown_section").show();
        $("#options_section").show();
    } else if (selectedElement.value === "to_long") {
        hideOption("check_for_warnings");
        showOption("expand_defs");
        hideOption("include_description_tags");
        $("#sidecar_input_section").show();
        $("#spreadsheet_input_section").hide();
        $("#schema_pulldown_section").show();
        $("#options_section").show();
    } else if (selectedElement.value === "to_short") {
        hideOption("check_for_warnings");
        showOption("expand_defs");
        hideOption("include_description_tags");
        $("#sidecar_input_section").show();
        $("#spreadsheet_input_section").hide();
        $("#schema_pulldown_section").show();
        $("#options_section").show();
    } else if (selectedElement.value === "extract_spreadsheet") {
        hideOption("check_for_warnings");
        hideOption("expand_defs");
        hideOption("include_description_tags");
        $("#sidecar_input_section").show();
        $("#spreadsheet_input_section").hide();
        $("#schema_pulldown_section").hide();
        $("#options_section").hide();
    } else if (selectedElement.value === "merge_spreadsheet") {
        hideOption("expand_defs");
        hideOption("check_for_warnings");
        showOption("include_description_tags");
        $("#sidecar_input_section").show();
        $("#spreadsheet_input_section").show();
        $("#schema_pulldown_section").hide();
        $("#options_section").show();
    }
}

// /**
//  * Prepare the data needed for the sidecar submit form.
//  * @returns {[FormData, String]} - Filled in form data and a default name for downloads.
//  */
// function prepareSubmitForm() {
//     const sidecarForm = document.getElementById("sidecar_form");
//     const formData = new FormData(sidecarForm);
//     const selectedElement = document.getElementById("process_actions");
//     formData.append("command_option", selectedElement.value)
//     const sidecarFile = $("#sidecar_file")[0];
//     formData.append('sidecar', sidecarFile.files[0])
//     const spreadsheetFile = $("#spreadsheet_file")[0];
//     formData.append('spreadsheet', spreadsheetFile.files[0])
//     const displayName = convertToResultsName(sidecarFile.files[0].name, '_processed')
//     return [formData, displayName]
// }


async function submitForm() {
    const [formData, defaultName] = prepareSubmitForm("sidecar");
    console.log(formData.entries);
    clearFlashMessages();
    flashMessageOnScreen('Sidecar is being processed ...', 'success', 'sidecar_flash')

    try {
        const response = await fetch("{{url_for('route_blueprint.sidecars_results')}}", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json()
            const error = new Error(errorData.message || `A response error occurred`);
            error.response = response;
            throw error;
        }
        const download = await response.text();
        handleResponse(response, download, defaultName, 'sidecar_flash')
    } catch (error) {
       if (error.response) {
            handleResponseFailure(error.response, message, error, displayName, 'sidecar_flash');
        } else {
            // Network or unexpected error
            const info = `Unexpected error occurred [Source: ${displayName}][Error: ${error.message}]`;
            flashMessageOnScreen(info, 'error', 'sidecar_flash');
        }
    }
}
