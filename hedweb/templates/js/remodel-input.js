

/**
 * Remodel file handler. Checks if the file uploaded has a JSON extention.
 */
$('#remodel_file').on('change',function () {
    let remodelPath = $('#remodel_file').val();
    clearFlashMessages();
    if (cancelWasPressedInChromeFileUpload(remodelPath)) {
        clearForm();
    }
    else if (fileHasValidExtension(remodelPath, JSON_FILE_EXTENSIONS)) {
        updateFileLabel(remodelPath, '#remodel_file_display_name');
    } else {
        clearForm();
        flashMessageOnScreen('Please upload a JSON remodel file (.json)', 'error', 'remodel_file_flash');
    }
});

/**
 * Clears the remodel file label.
 */
function clearRemodelFileLabel() {
    $('#remodel_file_display_name').text('');
}

/**
 * Resets the flash messages that aren't related to the form submission.
 */
function clearRemodelFlashMessages() {
    flashMessageOnScreen('', 'success', 'remodel_flash');
}

function getRemodelFileLabel() {
    return $('#remodel_file')[0].files[0].name;
}

