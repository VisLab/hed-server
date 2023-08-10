

/**
 * Sidecar event handler function. Checks if the file uploaded has a valid sidecar extension.
 */
$('#sidecar_file').on('change',function () {
    let sidecarPath = $('#sidecar_file').val();
    clearFlashMessages();
    if (fileHasValidExtension(sidecarPath, JSON_FILE_EXTENSIONS)) {
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
