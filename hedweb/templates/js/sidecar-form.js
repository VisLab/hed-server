
$(function () {
    prepareForm();
});

/**
 * Set the options according to the action specified.
 */
$('#process_actions').change(function(){
    setOptions();
});

$('#sidecar_file').change(function() {
    clearFlashMessages();
})

/**
 * Submit the form on click if schema and json file specified.
 */
$('#sidecar_submit').on('click', function () {
    if (fileIsSpecified('#sidecar_file', 'sidecar_flash', 'Sidecar file is not specified.' ) &&
        schemaSpecifiedWhenOtherIsSelected()) {
        submitForm();
    }
});

/**
 * Clear the fields in the form.
 */
function clearForm() {
    $('#sidecar_form')[0].reset();
    $('#process_actions').val('validate');
    clearWorksheet()
    setOptions();
    clearFlashMessages()
    $('#sidecar_file').val('');
    $('#spreadsheet_file').val('');
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

/**
 * Submit the form and return the validation results. If there are issues then they are returned in an attachment
 * file.
 */
function submitForm() {
    let sidecarForm = document.getElementById("sidecar_form");
    let formData = new FormData(sidecarForm);
    let selectedElement = document.getElementById("process_actions");
    formData.append("command_option", selectedElement.value)
    let sidecarFile = $("#sidecar_file")[0];
    formData.append('sidecar', sidecarFile.files[0])
    let display_name = convertToResultsName(sidecarFile, 'issues')
    let spreadsheetFile = $("#spreadsheet_file")[0];
    formData.append('spreadsheet', spreadsheetFile.files[0])
    clearFlashMessages();
    flashMessageOnScreen('Sidecar is being processed ...', 'success', 'sidecar_flash')
    $.ajax({
            type: 'POST',
            url: "{{url_for('route_blueprint.sidecar_results')}}",
            data: formData,
            contentType: false,
            processData: false,
            dataType: 'text',
            success: function (download, status, xhr) {
                getResponseSuccess(download, xhr, display_name, 'sidecar_flash')
            },
            error: function (xhr, status, errorThrown) {
                getResponseFailure(xhr, status, errorThrown, display_name, 'sidecar_flash')
            }
        }
    )
}
