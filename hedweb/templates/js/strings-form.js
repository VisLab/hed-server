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

$('#definition_file').change(function() {
    clearFlashMessages();
})
/**
 * Submit the form if a string has been entered.
 */
$('#string_submit').on('click', function () {
   if (!stringIsSpecified()) {
        flashMessageOnScreen('Must give a non-empty string.  See above.', 'error', 'string_flash')
    } else {
        submitStringForm();
    }
});

/**
 * Clears the form.
 */
$('#string_clear').on('click', function () {
    clearForm();
});

/**
 * Resets the fields in the form.
 */
function clearForm() {
    clearFlashMessages();
    setOptions();
    hideOtherSchemaVersionFileUpload();
    $('#definition_file').val('');
    $('#string_result').val('');
    $('#string_input').val('');
}

/**
 * Clear the flash messages that aren't related to the form submission.
 */
function clearFlashMessages() {
    clearSchemaSelectFlashMessages();
    flashMessageOnScreen('', 'success', 'string_flash');
}

/**
 * Prepare the validation form after the page is ready. The form will be reset to handle page refresh and
 * components will be hidden and populated.
 */
function prepareForm() {
    clearForm();
    $('#string_form')[0].reset();
    $('#process_actions').val('validate');
    getSchemaVersions()
    hideOtherSchemaVersionFileUpload()
}

/**
 * Set the options for the events depending on the action
 */
function setOptions() {
    // let action_value = $("#process_actions").val;
    let selectedElement = document.getElementById("process_actions");
    if (selectedElement.value === "validate") {
        showOption("check_for_warnings");
        $("#options_section").show();
        $("#definition_section").show();
        $("#query_input_section").hide();
    } else if (selectedElement.value === "to_long") {
        hideOption("check_for_warnings");
         $("#options_section").hide();
         $("#definition_section").hide();
         $("#query_input_section").hide();
    } else if (selectedElement.value === "to_short") {
        hideOption("check_for_warnings");
        $("#options_section").hide();
        $("#definition_section").hide();
        $("#query_input_section").hide();
    } else if (selectedElement.value === "search") {
        hideOption("check_for_warnings");
        $("#options_section").hide();
        $("#definition_section").hide();
        $("#query_input_section").show();
    }
}

/**
 * Checks to see if a hedstring has been specified.
 */
function stringIsSpecified() {
    return true;
}


/**
 * Submit the form and return the validation results. If there are issues then they are returned in an attachment
 * file.
 */
async function submitStringForm() {
    const [formData, defaultName] = prepareSubmitForm("string");
    clearFlashMessages();
    flashMessageOnScreen('HED string is being processed ...', 'success', 'string_flash');
    try {
        const response = await fetch("{{url_for('route_blueprint.strings_results')}}", {
            method: "POST",
            body: formData,
            headers: {
               'X-CSRFToken': "{{ csrf_token() }}"
            },
            credentials: 'same-origin'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `A response error occurred`);
        }

        const hedInfo = await response.json();
        clearFlashMessages();
        if (hedInfo['data']) {
            document.getElementById('string_result').value = hedInfo['data'];
        } else {
            document.getElementById('string_result').value = '';
        }
        flashMessageOnScreen(hedInfo['msg'], hedInfo['msg_category'], 'string_flash')
    } catch (error) {
        flashMessageOnScreen(error.message, 'error', 'string_flash')
    }
}
