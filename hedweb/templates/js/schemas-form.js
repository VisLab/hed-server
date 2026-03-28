document.addEventListener('DOMContentLoaded', function() {
    prepareForm();
});


/**
 * Set the options according to the action specified.
 */
document.getElementById('process_actions').addEventListener('change', function() {
    clearFlashMessages();
    setOptions();
});

/**
 * Checks if the HED file uploaded has a valid extension.
 */
document.getElementById('schema_file').addEventListener('change', function () {
    updateFileLabel(document.getElementById('schema_file').value, '#schema_file_display_name');
    document.getElementById('schema_file_option').checked = true;
    updateFlash("schema");
});

document.getElementById('second_schema_file').addEventListener('change', function () {
    updateFileLabel(document.getElementById('second_schema_file').value, '#second_schema_file_display_name');
    document.getElementById('second_schema_file_option').checked = true;
    updateFlash("second_schema");
});

document.getElementById('schema_url').addEventListener('change', function () {
    updateFileLabel(document.getElementById('schema_url').value, '#schema_url_display_name');
    document.getElementById('schema_url_option').checked = true;
    updateFlash("schema");
});

document.getElementById('second_schema_url').addEventListener('change', function () {
    updateFileLabel(document.getElementById('second_schema_url').value, '#second_schema_url_display_name');
    document.getElementById('second_schema_url_option').checked = true;
    updateFlash("second_schema");
});

document.getElementById('schema_folder').addEventListener('change', function () {
    const files = this.files;
    const label = document.getElementById('schema_folder_label');

    if (files.length > 0) {
        const folderName = files[0].webkitRelativePath.split('/')[0];
        label.textContent = `Schema folder: ${folderName}`;
    } else {
        label.textContent = UPLOAD_FILE_LABEL;
    }
});

document.getElementById('second_schema_folder').addEventListener('change', function () {
    const files = this.files;
    const label = document.getElementById('second_schema_folder_label');

    if (files.length > 0) {
        const folderName = files[0].webkitRelativePath.split('/')[0];
        label.textContent = `Schema folder: ${folderName}`;
    } else {
        label.textContent = UPLOAD_FILE_LABEL;
    }
});

/**
 * Submit the form if a schema is specified.
 */
document.getElementById('schema_submit').addEventListener('click', function () {
    if (getSchemaFilename("schema") === "") {
        flashMessageOnScreen('No valid source input file.  See above.', 'error', 'schema_flash')
    } else {
        submitSchemaForm();
    }
});

/**
 * Clear the form.
 */
document.getElementById('schema_clear').addEventListener('click', function () {
    clearForm();
});


/**
 * Clear the fields in the form.
 */
function clearForm() {
    clearFlashMessages();
    document.getElementById('schema_url_option').checked = false;
    document.getElementById('schema_file_option').checked = false;
    document.getElementById('schema_folder_option').checked = false;
    document.getElementById('schema_url').value = DEFAULT_XML_URL;
    document.getElementById('schema_folder_label').textContent = UPLOAD_FILE_LABEL;
    document.getElementById('second_schema_url').value = DEFAULT_XML_URL;
    document.getElementById('schema_file').value = '';
    document.getElementById('second_schema_file').value = '';
    setOptions();
}

/**
 * Resets the flash message that aren't related to the form submission.
 */
function clearFlashMessages() {
    flashMessageOnScreen('', 'success', 'schema_flash');
}

/**
 * Return the file name extracted from the schema selector.
 * 
 * @param {string} type - prefix on the html selectors (either "schema" or "second_schema")
 * 
 * @returns {string} file name extracted from the selector
 */
function getSchemaFilename(type) {
    let options_name = type + "_upload_options"
    let checkRadio = document.querySelector('input[name="' + options_name+ '"]:checked');
    if (checkRadio == null) {
        flashMessageOnScreen('Required ' + type + ' source not specified.', 'error', 'schema_flash');
        return "";
    }
    let checkRadioVal = checkRadio.id
    
    if (checkRadioVal === type + "_file_option") {
        const schemaFile = document.getElementById(type + '_file');
        let schemaFileIsEmpty = schemaFile.files.length === 0;
        if (schemaFileIsEmpty) {
            flashMessageOnScreen('Schema file not specified.', 'error', 'schema_flash');
            return '';
        }

        return schemaFile.files[0].name;
    }

    if (checkRadioVal === type + "_url_option") {
        let schemaUrl = document.getElementById(type + '_url').value;
        let schemaUrlIsEmpty = schemaUrl === "";
        if (schemaUrlIsEmpty) {
            flashMessageOnScreen('URL not specified.', 'error', 'schema_flash');
            return '';
        }
        return urlFileBasename(schemaUrl);
    }

    if (checkRadioVal === type + "_folder_option") {
        const schemaFolder = document.getElementById(type + '_folder');
        let files = schemaFolder.files;

        if (!files || files.length === 0) {
            flashMessageOnScreen('Schema folder not selected.', 'error', 'schema_flash');
            return '';
        }

        // Option: Return a list of filenames or the name of the root folder
        // For now, return the name of the first file in the folder:
        return files[0].webkitRelativePath.split('/')[0];  // Root folder name
    }
    return '';
}

/**
 * Prepare the validation form after the page is ready. The form will be reset to handle page refresh and
 * components will be hidden and populated.
 */
function prepareForm() {
    clearForm();
    document.getElementById('schema_form').reset();
    document.getElementById('process_actions').value = 'validate';
    document.getElementById('schema_url').value = DEFAULT_XML_URL;
    document.getElementById('second_schema_url').value = DEFAULT_XML_URL;
}


/**
 * Set the options for the events depending on the action
 */
function setOptions() {
    let selectedElement = document.getElementById("process_actions");
    if (selectedElement.value === "validate") {
        showOption("check_for_warnings");
        hideOption("save_merged");
        showElement("options_section");
        hideElement("second_schema_section");
    } else if (selectedElement.value === "compare_schemas") {
        hideOption("check_for_warnings");
        hideOption("save_merged");
        hideElement("options_section");
        showElement("second_schema_section");
    } else {
        hideOption("check_for_warnings");
        showOption("save_merged");
        showElement("options_section");
        hideElement("second_schema_section");
    }
}

/**
 * Submit the form and return the conversion results as an attachment
 */
async function submitSchemaForm() {
    const [formData, defaultName] = prepareSubmitForm("schema");
    const files = document.getElementById('schema_folder').files;
    for (const file of files) {
        // Preserve relative paths using the webkitRelativePath
        formData.append('files[]', file, file.webkitRelativePath);
    }
    const data = Object.fromEntries(formData.entries());
    console.log(data);
    clearFlashMessages();
    flashMessageOnScreen('Schema is being processed...', 'success','schema_flash')
    try {
        const fetchUrl = "{{url_for('route_blueprint.schemas_results')}}";
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
        console.log(download);
        handleResponse1(response, download, defaultName, 'schema_flash');
      } catch (error) {
       if (error.response) {
            handleResponseFailure(error.response, message, error, defaultName, 'schema_flash');
        } else {
            // Network or unexpected error
            const info = `Unexpected error occurred [Source: ${defaultName}][Error: ${error.message}]`;
            flashMessageOnScreen(info, 'error', 'schema_flash');
        }
    }
}


function updateFlash(type) {
     clearFlashMessages();
     let filename = getSchemaFilename(type);
     if (!filename) {
         return
     }
     let hasValidExtension = fileHasValidExtension(filename, SCHEMA_EXTENSIONS);
     if (!hasValidExtension) {
         flashMessageOnScreen('Please choose a valid schema file or url (.xml, .mediawiki, .json)', 'error',
        'schema_flash');
     }
}


function urlFileBasename(url) {
    let urlObj = null
    try {
        urlObj = new URL(url)
    } catch (err) {
       flashMessageOnScreen(err.message, 'error', 'schema_flash');
       return;
    }
    let pathname = urlObj.pathname;
    let index = pathname.lastIndexOf('/');
    return (-1 !== index) ? pathname.substring(index + 1) : pathname;
}
