document.addEventListener('DOMContentLoaded', function() {
    prepareForm();
});

/**
 * Set the options according to the action specified.
 */
document.getElementById('process_actions').addEventListener('change', function() {
    setOptions();
    clearFlashMessages();
});

document.getElementById('sidecar_file').addEventListener('change', function() {
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
    document.getElementById('sidecar_file').value = '';
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
    document.getElementById('sidecar_form').reset();
    document.getElementById('process_actions').value = 'validate';
    getSchemaVersions()
    hideOtherSchemaVersionFileUpload();
}

/**
 * Set the options for the events depending on the action
 */
function setOptions() {
    let selectedElement = document.getElementById("process_actions");
    if (selectedElement.value === "validate") {
        showOption("check_for_warnings");
        hideOption("include_description_tags");
        showElement("sidecar_input_section");
        hideElement("spreadsheet_input_section");
        showElement("schema_pulldown_section");
        showElement("options_section");
    } else if (selectedElement.value === "to_long") {
        hideOption("check_for_warnings");
        hideOption("include_description_tags");
        showElement("sidecar_input_section");
        hideElement("spreadsheet_input_section");
        showElement("schema_pulldown_section");
        showElement("options_section");
    } else if (selectedElement.value === "to_short") {
        hideOption("check_for_warnings");
        hideOption("include_description_tags");
        showElement("sidecar_input_section");
        hideElement("spreadsheet_input_section");
        showElement("schema_pulldown_section");
        showElement("options_section");
    } else if (selectedElement.value === "extract_spreadsheet") {
        hideOption("check_for_warnings");
        hideOption("include_description_tags");
        showElement("sidecar_input_section");
        hideElement("spreadsheet_input_section");
        hideElement("schema_pulldown_section");
        hideElement("options_section");
    } else if (selectedElement.value === "merge_spreadsheet") {
        hideOption("check_for_warnings");
        showOption("include_description_tags");
        showElement("sidecar_input_section");
        showElement("spreadsheet_input_section");
        hideElement("schema_pulldown_section");
        showElement("options_section");
    }
}


async function submitForm() {
    const [formData, defaultName] = prepareSubmitForm("sidecar");
    // const data = Object.fromEntries(formData.entries());
    // console.log(data);
    clearFlashMessages();
    flashMessageOnScreen('Sidecar is being processed ...', 'success', 'sidecar_flash')

    try {
        const fetchUrl = "{{url_for('route_blueprint.sidecars_results')}}";
        const response = await fetch(fetchUrl, {
            method: "POST",
            body: formData,
            headers: {
               'X-CSRFToken': "{{ csrf_token() }}"
            },
            credentials: 'same-origin'
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
