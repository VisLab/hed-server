document.addEventListener('DOMContentLoaded', () => {
    const checkbox = document.getElementById('include_prereleases');
    if (checkbox) {
        checkbox.addEventListener('change', getSchemaVersions);
    }
});
/**
 *
 * Event handler function when the HED version drop-down menu changes. If Other is selected the file browser
 * underneath it will appear. If another option is selected then it will disappear.
 */
document.getElementById('schema_version').addEventListener('change', function () {
    if (this.value === OTHER_VERSION_OPTION) {
        document.getElementById('schema_other_version').style.display = '';
    } else {
        hideOtherSchemaVersionFileUpload()
    }
    flashMessageOnScreen('', 'success', 'schema_select_flash');
});

/**
 * Checks if the HED file uploaded has a valid extension.
 */
document.getElementById('schema_path').addEventListener('change', function () {
    let hedPath = document.getElementById('schema_path').value;
    if (fileHasValidExtension(hedPath, XML_FILE_EXTENSIONS)) {
        clearSchemaSelectFlashMessages();
        updateFileLabel(hedPath, '#schema_display_name');
    } else {
        flashMessageOnScreen('Please upload a valid schema file (.xml)', 'error',
            'schema_select_flash')
    }
})

/**
 * Resets the flash messages that aren't related to the form submission.
 */
function clearSchemaSelectFlashMessages() {
    flashMessageOnScreen('', 'success', 'schema_select_flash');
}

/**
 * Gets the HED versions that are in the HED version drop-down menu.
 */

async function getSchemaVersions() {
    const checkbox = document.getElementById('include_prereleases');
    const isChecked = checkbox && checkbox.checked ? 'true' : 'false';
    try {
        const fetchUrl = `{{url_for("route_blueprint.schema_versions_results")}}?include_prereleases=${isChecked}`;
        const response = await fetch(fetchUrl, {
            method: 'GET',
            headers: {
               'X-CSRFToken': "{{ csrf_token() }}"
            },
            credentials: 'same-origin'
        });

        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.status}`);
        }

        const schemaInfo = await response.json();  // Parse JSON response
        if (schemaInfo['schema_version_list']) {
            populateSchemaVersionsDropdown(schemaInfo['schema_version_list']);
        } else if (schemaInfo['message']) {
            flashMessageOnScreen(schemaInfo['message'], 'error', 'schema_select_flash');
        } else {
            flashMessageOnScreen('Server could not retrieve HED versions. Please provide your own.',
                'error', 'schema_select_flash');
        }
    } catch (error) {
        flashMessageOnScreen('Server could not retrieve HED schema versions. Please provide your own.',
            'error', 'schema_select_flash');
        console.error('Fetch error:', error);
    }
}

/**
 * Checks to see if a HED XML file is specified when the HED drop-down is set to "Other".
 */
function schemaSpecifiedWhenOtherIsSelected() {
    const hedFile = document.getElementById('schema_path');
    let hedFileIsEmpty = hedFile.files.length === 0;
    if (document.getElementById('schema_version').value === OTHER_VERSION_OPTION && hedFileIsEmpty) {
        flashMessageOnScreen('Schema version is not specified.', 'error', 'schema_select_flash');
        return false;
    }
    return true;
}

/**
 * Hides the HED XML file upload.
 */
function hideOtherSchemaVersionFileUpload() {
    const displayEl = document.getElementById('schema_display_name');
    if (displayEl) displayEl.textContent = '';
    const otherEl = document.getElementById('schema_other_version');
    if (otherEl) otherEl.style.display = 'none';
}


/**
 * Populates the HED version drop-down menu.
 * @param {Array} hedVersions - An array containing the HED versions.
 */
function populateSchemaVersionsDropdown(hedVersions) {
    const hedVersionDropdown = document.getElementById('schema_version');
    hedVersionDropdown.replaceChildren();
    if (hedVersions.length > 0) {
        for (let i = 0; i < hedVersions.length; i++) {
            hedVersionDropdown.insertAdjacentHTML('beforeend', '<option value=' + hedVersions[i].trim().split(' ')[0] + '>' + hedVersions[i] + '</option>');
        }
    }
    hedVersionDropdown.insertAdjacentHTML('beforeend', '<option value=' + OTHER_VERSION_OPTION + '>' + OTHER_VERSION_OPTION + '</option>');
}
