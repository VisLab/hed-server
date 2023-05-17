

$(function () {
    prepareForm();
})


$('#process_actions').change(function(){
    setOptions();
    setEventsTable('#events_file')
});


/**
 * Events file handler function. Checks if the file uploaded has a valid spreadsheet extension.
 */
$('#events_file').on('change', function () {
    let eventsPath = $('#events_file').val();
    if (cancelWasPressedInChromeFileUpload(eventsPath) || !fileHasValidExtension(eventsPath, TEXT_FILE_EXTENSIONS)) {
        clearForm();
        flashMessageOnScreen('Please upload a tsv file (.tsv, .txt)', 'error', 'events_flash');
        return;
    }
    setEventsTable('#events_file')
    updateFileLabel(eventsPath, '#events_display_name');
});

/**
 * Submits the form if there is an events file and an available hed schema
 */
$('#events_submit').on('click', function () {
    if (fileIsSpecified('#events_file', 'events_flash', 'Events file is not specified.')
        && schemaSpecifiedWhenOtherIsSelected()) {
        submitForm();
    }
});


/**
 * Clears the fields in the form.
 */
function clearForm() {
    $('#events_form')[0].reset();
    $('#sidecar_file').val('');
    $('#events_file').val('');
    $('#remodel_file').val('');
    $('#process_actions').val('validate');
    setOptions();
    clearFlashMessages();
    hideColumnInfo("show_columns");
    hideColumnInfo("show_events");
    hideOtherSchemaVersionFileUpload();
}

/**
 * Clear the flash messages that aren't related to the form submission.
 */
function clearFlashMessages() {
    clearColumnInfoFlashMessages();
    clearSchemaSelectFlashMessages();
    flashMessageOnScreen('', 'success', 'events_flash');
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
 * Sets the column table for this event file
 * @param {string} event_tag  - jquery tag pointing to the event file.
 */
function setEventsTable(event_tag) {
    clearFlashMessages();
    removeColumnInfo("show_columns");
    removeColumnInfo("show_events")
    let events = $(event_tag);
    let eventsFile = events[0].files[0];
    if ($("#generate_sidecar").is(":checked")) {
        setColumnsInfo(eventsFile, 'events_flash', undefined, true,  "show_events")
    } else if (!$("#remodel").is(":checked")){
        setColumnsInfo(eventsFile, 'events_flash', undefined, true,  "show_columns")
    }
}

/**
 * Set the options for the events depending on the action
 */
function setOptions() {
    let selectedElement = document.getElementById("process_actions");
    if (selectedElement.value === "validate") {
        hideOption("expand_defs");
        hideOption("include_summaries")
        hideOption("use_hed");
        showOption("check_for_warnings");
        $("#remodel_input_section").hide();
        $("#sidecar_input_section").show();
        $("#schema_pulldown_section").show();
        $("#options_section").show();
    } else if (selectedElement.value === "assemble") {
        hideOption("check_for_warnings");
        hideOption("include_summaries")
        hideOption("use_hed");
        showOption("expand_defs");
        $("#remodel_input_section").hide();
        $("#sidecar_input_section").show();
        $("#schema_pulldown_section").show();
        $("#options_section").show();
    } else if (selectedElement.value === "generate_sidecar") {
        hideOption("check_for_warnings");
        hideOption("expand_defs");
        hideOption("include_summaries")
        hideOption("use_hed");
        $("#remodel_input_section").hide();
        $("#sidecar_input_section").hide();
        $("#schema_pulldown_section").hide();
        $("#options_section").hide();
    } else if (selectedElement.value === "remodel") {
        hideOption("check_for_warnings");
        hideOption("expand_defs");
        hideOption("use_hed");
        showOption("include_summaries")
        $("#options_section").show();
        $("#sidecar_input_section").show();
        $("#remodel_input_section").show();
        $("#schema_pulldown_section").show();
    }
}

/**
 * Submit the form and return the validation results. If there are issues then they are returned in an attachment
 * file.
 */
function submitForm() {
    let eventsForm = document.getElementById("events_form");
    let formData = new FormData(eventsForm);
    let selectedElement = document.getElementById("process_actions");
    formData.append("command_option", selectedElement.value)
    let prefix = 'issues';
    let eventsFile = $('#events_file')[0].files[0].name;
    let includeSummaries = $('#include_summaries').is(':checked')
    let display_name = convertToResultsName(eventsFile, prefix)
    clearFlashMessages();
    flashMessageOnScreen('Event file is being processed ...', 'success', 'events_flash')
    let postType = {
        type: 'POST',
        url: "{{url_for('route_blueprint.events_results')}}",
        data: formData,
        contentType: false,
        processData: false,

        success: function (download, status, xhr) {
            getResponseSuccess(download, xhr, display_name, 'events_flash')
        },
        error: function (xhr, status, errorThrown) {
            getResponseFailure(xhr, status, errorThrown, display_name, 'events_flash')
        }
    }
    if (includeSummaries){
        postType["xhrFields"] = {
            responseType: 'blob'
        }
    }
    $.ajax(postType)
}
