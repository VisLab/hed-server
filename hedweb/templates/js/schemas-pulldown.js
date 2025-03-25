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
$('#schema_version').on('change',function () {
    if ($(this).val() === OTHER_VERSION_OPTION) {
        $('#schema_other_version').show();
    } else {
        hideOtherSchemaVersionFileUpload()
    }
    flashMessageOnScreen('', 'success', 'schema_select_flash');
});

/**
 * Checks if the HED file uploaded has a valid extension.
 */
$('#schema_path').on('change', function () {
    let hedSchema = $('#schema_path');
    let hedPath = hedSchema.val();
    let hedFile = hedSchema[0].files[0];
    if (fileHasValidExtension(hedPath, XML_FILE_EXTENSIONS)) {
        getVersionFromSchemaFile(hedFile);
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
 * Gets the version from the HED file that the user uploaded.
 * @param {Object} hedXMLFile - A HED XML file.
 */
async function getVersionFromSchemaFile(hedXMLFile) {
    let formData = new FormData();
    formData.append('schema_path', hedXMLFile);
    formData.append('csrf_token', "{{ csrf_token() }}");
    try {
        const submitUrl = "{{ url_for('route_blueprint.schema_version_results', _external=True)}}";
        const response = await fetch(submitUrl, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const hedInfo = await response.json();  // Parse JSON response

        if (hedInfo['schema_version']) {
            flashMessageOnScreen('Using HED version ' + hedInfo['schema_version'], 'success', 'schema_select_flash');
        } else if (hedInfo['message']) {
            flashMessageOnScreen(hedInfo['message'], 'error', 'schema_select_flash');
        } else {
            flashMessageOnScreen('Server could not retrieve HED versions. Please provide your own.',
                'error', 'schema_select_flash');
        }

    } catch (error) {
        flashMessageOnScreen('Could not get version number from HED XML file.', 'error', 'schema_select_flash');
        console.error('Fetch error:', error);
    }
}


/**
 * Checks to see if a HED XML file is specified when the HED drop-down is set to "Other".
 */
function schemaSpecifiedWhenOtherIsSelected() {
    let hedFile = $('#schema_path');
    let hedFileIsEmpty = hedFile[0].files.length === 0;
    if ($('#schema_version').val() === OTHER_VERSION_OPTION && hedFileIsEmpty) {
        flashMessageOnScreen('Schema version is not specified.', 'error', 'schema_select_flash');
        return false;
    }
    return true;
}

/**
 * Hides the HED XML file upload.
 */
function hideOtherSchemaVersionFileUpload() {
    $('#schema_display_name').text('');
    $('#schema_other_version').hide();
}


/**
 * Populates the HED version drop-down menu.
 * @param {Array} hedVersions - An array containing the HED versions.
 */
function populateSchemaVersionsDropdown(hedVersions) {
    let hedVersionDropdown = $('#schema_version');
    $('#schema_version').empty()
    if (hedVersions.length > 0) {
        hedVersionDropdown.append('<option value=' + hedVersions[0] + '>' + hedVersions[0] + ' (Latest)</option>');
        for (let i = 1; i < hedVersions.length; i++) {
            hedVersionDropdown.append('<option value=' + hedVersions[i].trim().split(' ')[0] + '>' + hedVersions[i] + '</option>');
        }
    }
    hedVersionDropdown.append('<option value=' + OTHER_VERSION_OPTION + '>' + OTHER_VERSION_OPTION +
        '</option>');
}
