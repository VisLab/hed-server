$(function () {
    prepareForm();
})

document.getElementById('process_actions').addEventListener('change', function(){
   try {
       clearFlashMessages();
       setOptions();
       setEventsTable()
   }catch (error) {
       console.error('Error in setting events table', error);
   }
});


document.getElementById('sidecar_file').addEventListener('change', function() {
    clearFlashMessages();
});


document.getElementById('remodel_file').addEventListener('change', function() {
    clearFlashMessages();
});

/**
 * Events file handler function. Checks if the file uploaded has a valid spreadsheet extension.
 */
document.getElementById('events_file').addEventListener('change', function () {
    clearFlashMessages();
    setEventsTable()
});


/**
 * Submit the form if there is an events file and an available HED schema
 */
$('#events_submit').on('click', function () {
    if (fileIsSpecified('events_file', 'events_flash', 'Events file is not specified.')
        && schemaSpecifiedWhenOtherIsSelected()) {
        submitForm();
    }
});


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
    clearEventsTable();
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
    document.getElementById('process_actions').value = 'validate';
    getSchemaVersions()
    hideOtherSchemaVersionFileUpload();
}

function clearEventsTable() {
    clearFlashMessages();
    hideColumnInfo("show_events");
    removeColumnInfo("show_events");
}


/**
 * Sets the column table for this event file
 */
async function setEventsTable() {
    clearEventsTable();
    if (document.getElementById('process_actions').value !== 'generate_sidecar') {
        return;
    }

    let eventsFile = document.querySelector('#events_file').files[0];
    if (!eventsFile) {
        return null
    } else if (!(eventsFile instanceof File)) {
        flashMessageOnScreen('An event file must be provided ...', 'warning', 'events_flash');
        return null;
    }
    const info = await getColumnsInfo(eventsFile, 'events_flash', undefined, true);
    if (info) {
        let cols = info['column_list'];
        let counts = info['column_counts'];
        showEvents(cols, counts);
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
        showElement("options_section")
        //$("#options_section").show();
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
          const submitUrl = "{{ url_for('route_blueprint.events_results') }}";
          const response = await fetch(submitUrl, {
              method: "POST",
              body: formData,
              headers: {
               'X-CSRFToken': "{{ csrf_token() }}"
              },
              credentials: 'same-origin'
          });

          if (!response.ok) {
            const errorData = await response.json()
            const error = new Error(errorData.message || `A response error occurred Status: ${response.status}`);
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
