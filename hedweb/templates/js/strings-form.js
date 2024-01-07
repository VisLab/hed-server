
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
    } else if (selectedElement.value === "to_long") {
        hideOption("check_for_warnings");
        $("#options_section").hide();
    } else if (selectedElement.value === "to_short") {
        hideOption("check_for_warnings");
        $("#options_section").hide();
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
function submitStringForm() {
    let stringForm = document.getElementById("string_form");
    let formData = new FormData(stringForm);
    let selectedElement = document.getElementById("process_actions");
    formData.append("command_option", selectedElement.value)
    clearFlashMessages();
    flashMessageOnScreen('HED string is being processed ...', 'success', 'string_flash')
    $.ajax({
            type: 'POST',
            url: "{{url_for('route_blueprint.strings_results')}}",
            data: formData,
            contentType: false,
            processData: false,
            dataType: 'json',
            success: function (hedInfo) {
                clearFlashMessages();
                if (hedInfo['data']) {
                    $('#string_result').val(hedInfo['data'])
                } else {
                    $('#string_result').val('')
                }
                flashMessageOnScreen(hedInfo['msg'], hedInfo['msg_category'], 'string_flash')
            },
            error: function (jqXHR) {
                flashMessageOnScreen(jqXHR.responseJSON.message, 'error', 'string_flash')
            }
        }
    )
}