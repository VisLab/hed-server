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
 * Submit the form if there is an events file and an available HED schema
 */
$('#events_submit').on('click', function () {
    if (fileIsSpecified('#events_file', 'events_flash', 'Events file is not specified.')
        && schemaSpecifiedWhenOtherIsSelected()) {
        submitForm();
    }
});
// document.getElementById('events_submit').addEventListener('click', function () {
//     if (!schemaSpecifiedWhenOtherIsSelected() ||
//         !fileIsSpecified('events_file', 'events_flash', 'Events file is not specified.')) {
//         return;
//     }
//     try {
//      await submitForm();
//     } catch (error) {
//             console.error("Form could not be submitted:", error)
//     }
// });


/**
 * Clear the events form.
 */
document.getElementById('events_clear').addEventListener('click', function () {
    clearForm();
});


/**
 * Clear the fields in the form.
 */
function clearForm() {
    clearFlashMessages();
    document.getElementById('sidecar_file').value = '';
    document.getElementById('events_file').value = '';
    document.getElementById('remodel_file').value = '';
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
    document.getElementById('process_actions').value = 'validate';
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
        hideOption("append_assembled");
        showOption("check_for_warnings");
        hideOption("expand_defs");
        hideOption("include_context");
        hideOption("include_summaries");
        hideOption("remove_types_on");
        hideOption("replace_defs");
        hideOption("use_hed");
        $("#options_section").show();
        $("#query_input_section").hide();
        $("#schema_pulldown_section").show();
        $("#remodel_input_section").hide();
        $("#sidecar_input_section").show();
        $("#show_events_section").show();
    } else if (selectedElement.value === "assemble") {
        showOption("append_assembled", true);
        hideOption("check_for_warnings");
        hideOption("expand_defs");
        showOption("include_context", true);
        hideOption("include_summaries");
        showOption("remove_types_on", true);
        showOption("replace_defs", true);
        hideOption("use_hed");
        $("#options_section").show();
        $("#query_input_section").hide();
        $("#schema_pulldown_section").show();
        $("#remodel_input_section").hide();
        $("#sidecar_input_section").show();
        $("#show_events_section").show();
    } else if (selectedElement.value === "generate_sidecar") {
        hideOption("append_assembled");
        hideOption("check_for_warnings");
        hideOption("expand_defs");
        hideOption("include_context");
        hideOption("include_summaries");
        hideOption("remove_types_on");
        hideOption("replace_defs");
        hideOption("use_hed");
        $("#options_section").hide();
        $("#query_input_section").hide();
        $("#schema_pulldown_section").hide();
        $("#remodel_input_section").hide();
        $("#sidecar_input_section").hide();
        $("#show_events_section").show();
    } else if (selectedElement.value === "remodel") {
        hideOption("append_assembled");
        hideOption("check_for_warnings");
        hideOption("expand_defs");
        hideOption("include_context");
        showOption("include_summaries")
        hideOption("remove_types_on")
        hideOption("replace_defs");
        hideOption("use_hed");
        $("#options_section").show();
        $("#query_input_section").hide();
        $("#schema_pulldown_section").show();
        $("#remodel_input_section").show();
        $("#sidecar_input_section").show();
        $("#show_events_section").show();
    }  else if (selectedElement.value === "search") {
        showOption("append_assembled", true);
        hideOption("check_for_warnings");
        hideOption("expand_defs");
        showOption("include_context", true);
        hideOption("include_summaries");
        showOption("remove_types_on", true);
        showOption("replace_defs", true);
        hideOption("use_hed");
        $("#options_section").show();
        $("#query_input_section").show();
        $("#schema_pulldown_section").show();
        $("#remodel_input_section").hide();
        $("#sidecar_input_section").show();
        $("#show_events_section").show();
    }
}

/**
 * Submit the form and return the validation results. If there are issues then they are returned in an attachment
 * file.
 */
async function submitForm() {
    const [formData, defaultName] = prepareSubmitForm("events");
    const includeSummaries = $('#include_summaries').is(':checked')
    clearFlashMessages();
    flashMessageOnScreen('Event file is being processed ...', 'success', 'events_flash')

     try {
        const response = await fetch("{{url_for('route_blueprint.events_results')}}", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json()
            const error = new Error(errorData.message || `A response error occurred`);
            error.response = response;
            throw error;
        }

        let download;
        if (includeSummaries){
            download = await response.blob();
        } else {
            download = await response.text();
        }
        handleResponse(response, download, defaultName, 'events_flash');
      } catch (error) {
       if (error.response) {
            handleResponseFailure(error.response, message, error, defaultName, 'events_flash');
        } else {
            // Network or unexpected error
            const info = `Unexpected error occurred [Source: ${defaultName}][Error: ${error.message}]`;
            flashMessageOnScreen(info, 'error', 'events_flash');
        }
    }
}
