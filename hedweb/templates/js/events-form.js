

$(function () {
    prepareForm();
})

$('#process_actions').change(function(){
    clearFlashMessages();
    setOptions();
    setEventsTable()
});

$('#sidecar_file').change(function() {
    clearFlashMessages();
})

$('#remodel_file').change(function() {
    clearFlashMessages();
})


/**
 * Events file handler function. Checks if the file uploaded has a valid spreadsheet extension.
 */
$('#events_file').on('change', function () {
    clearFlashMessages();
    setEventsTable('#events_file')
});

/**
 * Submit the form if there is an events file and an available hed schema
 */
$('#events_submit').on('click', function () {
    if (fileIsSpecified('#events_file', 'events_flash', 'Events file is not specified.')
        && schemaSpecifiedWhenOtherIsSelected()) {
        submitForm();
    }
});

/**
 * Clear the form.
 */
$('#events_clear').click(function() {
    clearForm();
});


/**
 * Clear the fields in the form.
 */
function clearForm() {
    clearFlashMessages();
    $('#sidecar_file').val('');
    $('#events_file').val('');
    $('#remodel_file').val('');
    setOptions();
    hideOtherSchemaVersionFileUpload();
    setEventsTable();
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
    $('#events_form')[0].reset();
    $('#process_actions').val('validate');
    getSchemaVersions()
    hideOtherSchemaVersionFileUpload();
}

/**
 * Sets the column table for this event file
 */
function setEventsTable() {
    clearColumnInfoFlashMessages();
    removeColumnInfo("show_events")
    let action = $('#process_actions').val()
    let events = $('#events_file');
    let eventsFile = events[0].files[0];
    if (action === 'generate_sidecar' && eventsFile != null) {
        let info = getColumnsInfo(eventsFile, 'events_flash', undefined, true)
        let cols = info['column_list']
        let counts = info['column_counts']
        showEvents(cols, counts)
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
        $("#options_section").show();
        $("#schema_pulldown_section").show();
        $("#remodel_input_section").hide();
        $("#sidecar_input_section").show();
        $("#show_events_section").hide();
    } else if (selectedElement.value === "assemble") {
        hideOption("check_for_warnings");
        hideOption("include_summaries")
        hideOption("use_hed");
        showOption("expand_defs");
        $("#options_section").show();
        $("#schema_pulldown_section").show();
        $("#remodel_input_section").hide();
        $("#sidecar_input_section").show();
        $("#show_events_section").hide();
    } else if (selectedElement.value === "generate_sidecar") {
        hideOption("check_for_warnings");
        hideOption("expand_defs");
        hideOption("include_summaries")
        hideOption("use_hed");
        $("#options_section").hide();
        $("#schema_pulldown_section").hide();
        $("#remodel_input_section").hide();
        $("#sidecar_input_section").hide();
        $("#show_events_section").show();
    } else if (selectedElement.value === "remodel") {
        hideOption("check_for_warnings");
        hideOption("expand_defs");
        hideOption("use_hed");
        showOption("include_summaries")
        $("#options_section").show();
        $("#schema_pulldown_section").show();
        $("#remodel_input_section").show();
        $("#sidecar_input_section").show();
        $("#show_events_section").hide();
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
