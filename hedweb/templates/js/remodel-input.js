

/**
 * Remodel file handler. Checks if the file uploaded has a JSON extension.
 */
document.getElementById('remodel_file').addEventListener('change', function () {
    let remodelPath = document.getElementById('remodel_file').value;
    clearFlashMessages();
    if (fileHasValidExtension(remodelPath, JSON_FILE_EXTENSIONS)) {
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
    document.getElementById('remodel_file_display_name').textContent = '';
}
