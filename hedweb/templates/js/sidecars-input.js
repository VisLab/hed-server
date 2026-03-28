

/**
 * Sidecar event handler function. Checks if the file uploaded has a valid sidecar extension.
 */
document.getElementById('sidecar_file').addEventListener('change', function () {
    let sidecarPath = document.getElementById('sidecar_file').value;
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
    document.getElementById('sidecar_display_name').textContent = '';
}
