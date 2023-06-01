

/**
 * Remodel file handler. Checks if the file uploaded has a JSON extension.
 */
$('#remodel_file').on('change',function () {
    let remodelPath = $('#remodel_file').val();
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
    $('#remodel_file_display_name').text('');
}
