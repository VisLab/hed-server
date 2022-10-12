

/**
 * Sidecar event handler function. Checks if the file uploaded has a valid sidecar extension.
 */
$('#sidecar_file').on('change',function () {
    let sidecarPath = $('#sidecar_file').val();
    clearFlashMessages();
    if (cancelWasPressedInChromeFileUpload(sidecarPath)) {
        clearForm();
    }
    else if (fileHasValidExtension(sidecarPath, JSON_FILE_EXTENSIONS)) {
        updateFileLabel(sidecarPath, '#sidecar_display_name');
    } else {
        clearForm();
        flashMessageOnScreen('Please upload a JSON sidecar (.json)', 'error', 'sidecar_flash');
    }
});

/**
 * Clears the sidecar file label.
 */
function clearSidecarFileLabel() {
    $('#sidecar_display_name').text('');
}

/**
 * Resets the flash messages that aren't related to the form submission.
 */
function clearSidecarInputFlashMessages() {
    flashMessageOnScreen('', 'success', 'sidecar_flash');
}

function getSidecarFileLabel() {
    return $('#sidecar_file')[0].files[0].name;
}

