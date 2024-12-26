$(function () {
    prepareForm();
});


/**
 * Set the options according to the action specified.
 */
$('#process_actions').change(function(){
    clearFlashMessages();
    setOptions();
});

/**
 * Checks if the HED file uploaded has a valid extension.
 */
$('#schema_file').on('change', function () {
    updateFileLabel($('#schema_file').val(), '#schema_file_display_name');
    $('#schema_file_option').prop('checked', true);
    updateFlash("schema");
});

$('#second_schema_file').on('change', function () {
    updateFileLabel($('#second_schema_file').val(), '#second_schema_file_display_name');
    $('#second_schema_file_option').prop('checked', true);
    updateFlash("second_schema");
});

$('#schema_url').on('change', function () {
    updateFileLabel($('#schema_url').val(), '#schema_url_display_name');
    $('#schema_url_option').prop('checked', true);
    updateFlash("schema");
});

$('#second_schema_url').on('change', function () {
    updateFileLabel($('#second_schema_url').val(), '#second_schema_url_display_name');
    $('#second_schema_url_option').prop('checked', true);
    updateFlash("second_schema");
});

/**
 * Submit the form if a schema is specified.
 */
$('#schema_submit').on('click', function () {
    if (getSchemaFilename("schema") === "") {
        flashMessageOnScreen('No valid source input file.  See above.', 'error', 'schema_flash')
    } else {
        submitSchemaForm();
    }
});

/**
 * Clear the form.
 */
$('#schema_clear').on('click', function () {
    clearForm();
});

//
//
// $('#schema_file_option').on('change', function () {
//     updateForm();
// });
//
// $('#schema_url_option').on('change',function () {
//     updateForm();
// });
//
// $('#second_schema_file_option').on('change', function () {
//     updateForm();
// });
//
// $('#second_schema_url_option').on('change',function () {
//     updateForm();
// });

/**
 * Clear the fields in the form.
 */
function clearForm() {
    clearFlashMessages();
    $('#schema_url_option').prop('checked', false);
    $('#schema_file_option').prop('checked', false);
    $('#schema_url').val(DEFAULT_XML_URL);
    $('#second_schema_url').val(DEFAULT_XML_URL);
    $('#schema_file').val('');
    $('#second_schema_file').val('');
    setOptions();
}

/**
 * Resets the flash message that aren't related to the form submission.
 */
function clearFlashMessages() {
    flashMessageOnScreen('', 'success', 'schema_flash');
}

function convertToOutputName(original_filename) {
    let file_parts = splitExt(original_filename);
    let basename = file_parts[0]
    let extension = file_parts[1]
    let new_extension = 'bad'
    if (extension === SCHEMA_XML_EXTENSION) {
        new_extension = SCHEMA_MEDIAWIKI_EXTENSION
    } else if (extension === SCHEMA_MEDIAWIKI_EXTENSION) {
        new_extension = SCHEMA_XML_EXTENSION
    }

    return basename + "." + new_extension
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
        let schemaFile = $('#' + type + '_file');
        let schemaFileIsEmpty = schemaFile[0].files.length === 0;
        if (schemaFileIsEmpty) {
            flashMessageOnScreen('Schema file not specified.', 'error', 'schema_flash');
            return '';
        }

        return schemaFile[0].files[0].name;
    }

 
    if (checkRadioVal === type + "_url_option") {
        let schemaUrl = $('#' + type + '_url').val();
        let schemaUrlIsEmpty = schemaUrl === "";
        if (schemaUrlIsEmpty) {
            flashMessageOnScreen('URL not specified.', 'error', 'schema_flash');
            return '';
        }
        return urlFileBasename(schemaUrl);
    }
    return '';
}

/**
 * Prepare the validation form after the page is ready. The form will be reset to handle page refresh and
 * components will be hidden and populated.
 */
function prepareForm() {
    clearForm();
    $('#schema_form')[0].reset();
    $('#process_actions').val('validate');
    $('#schema_url').val(DEFAULT_XML_URL);
    $('#second_schema_url').val(DEFAULT_XML_URL);
}


/**
 * Set the options for the events depending on the action
 */
function setOptions() {
    let selectedElement = document.getElementById("process_actions");
    if (selectedElement.value === "validate") {
        showOption("check_for_warnings");
        $("#options_section").show();
        $("#second_schema_section").hide()
    } else if (selectedElement.value === "compare_schemas") {
        hideOption("check_for_warnings");
        $("#options_section").hide();
        $("#second_schema_section").show()
    } else {
        hideOption("check_for_warnings");
        $("#options_section").hide();
        $("#second_schema_section").hide()
    }
}

/**
 * Submit the form and return the conversion results as an attachment
 */
async function submitSchemaForm() {
    const [formData, defaultName] = prepareSubmitForm("schema");
    let schemaURL = document.getElementById("schema_url")
    formData.append("schema_url", schemaURL.value)
    clearFlashMessages();
    flashMessageOnScreen('Schema is being processed...', 'success','schema_flash')
    try {
        const response = await fetch("{{url_for('route_blueprint.schemas_results')}}", {
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
        handleResponse(response, download, defaultName, 'schema_flash');
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


/*function updateForm() {
     clearFlashMessages();
     let filename = getSchemaFilename("schema");
     let isXMLFilename = fileHasValidExtension(filename, [SCHEMA_XML_EXTENSION]);
     let isMediawikiFilename = fileHasValidExtension(filename, [SCHEMA_MEDIAWIKI_EXTENSION]);

     let hasValidFilename = false;
     if (isXMLFilename) {
       // $('#schema-conversion-submit').html("Convert to mediawiki")
        hasValidFilename = true;
     } else if (isMediawikiFilename) {
        //$('#schema-conversion-submit').html("Convert to XML");
        hasValidFilename = true;
     } else {
        // $('#schema-conversion-submit').html("Convert Format");
     }

     let urlChecked = document.getElementById("schema_url_option").checked;
     if (!urlChecked || hasValidFilename) {
        flashMessageOnScreen("", 'success', 'schema_flash')
     }
     let uploadChecked = document.getElementById("schema_file_option").checked;
     if (!uploadChecked || hasValidFilename) {
        flashMessageOnScreen("", 'success', 'schema_flash')
     }

     if (filename && urlChecked && !hasValidFilename) {
        flashMessageOnScreen('Please choose a valid schema url (.xml, .mediawiki)', 'error',
        'schema_flash');
     }

     if (filename && uploadChecked && !hasValidFilename) {
         flashMessageOnScreen('Please upload a valid schema file (.xml, .mediawiki)', 'error',
        'schema_flash');
     }

     if (!uploadChecked && !urlChecked) {
        flashMessageOnScreen('No source file specified.', 'error', 'schema_flash');
     }

     flashMessageOnScreen('', 'success', 'schema_flash')
}*/


function updateFlash(type) {
     clearFlashMessages();
     let filename = getSchemaFilename(type);
     if (!filename) {
         return
     }
     let hasValidExtension = fileHasValidExtension(filename, SCHEMA_EXTENSIONS);
     if (!hasValidExtension) {
         flashMessageOnScreen('Please choose a valid schema file or url (.xml, .mediawiki)', 'error',
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
