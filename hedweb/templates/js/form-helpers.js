

/**
 * Converts a path and suffix to a text results name
 * @param {String} filename - Pathname of the original file
 * @param {String} suffix - Suffix to be appended to the file name of original file
 * @returns {String} - File name of the
 */
function convertToResultsName(filename, suffix) {
    let parts = getFilenameAndExtension(filename);
    return parts[0] + suffix + ".txt"
}


/**
 * Compares the file extension of the file at the specified path to an Array of accepted file extensions.
 * @param {String} filePath - A path to a file.
 * @param {Array} acceptedFileExtensions - An array of accepted file extensions.
 * @returns {boolean} - True if the file has an accepted file extension.
 */
function fileHasValidExtension(filePath, acceptedFileExtensions) {
    let fileExtension = filePath.split('.').pop();
    return $.inArray(fileExtension.toLowerCase(), acceptedFileExtensions) !== -1
}


/**
 * Checks to see if a file has been specified.
 * @param {string} nameID - id of the element holding the name (no #).
 * @param {string} flashID - id of the flash element to display error message.
 * @param {string} errorMsg - error message to be displayed if file isn't in form.
 * @returns {boolean} - returns true if file is specified.
 */
function fileIsSpecified(nameID, flashID, errorMsg) {
    let theFile = $(nameID);
    if (theFile[0].files.length === 0) {
        flashMessageOnScreen(errorMsg, 'error', flashID);
        return false;
    }
    return true;
}


/**
 * Flash a message on the screen.
 * @param {String} message - The message that will be flashed on the screen.
 * @param {String} category - The msg_category of the message. The categories are 'error', 'success', and 'other'.
 * @param {String} flashMessageElementId - ID of the flash element
 */
function flashMessageOnScreen(message, category, flashMessageElementId) {
    let flashMessage = document.getElementById(flashMessageElementId);
    flashMessage.innerHTML = message;
    setFlashMessageCategory(flashMessage, category);
}


function getFilenameAndExtension(pathname){

  let clean = pathname.toString().replace(/^.*[\\\/]/, '');
  if (!clean) {
      return ['', '']
  }

  let filename = clean.substring(0, clean.lastIndexOf('.'));
  let ext = clean.split('.').pop();
  return [filename, ext];
}


/**
 * Gets the file download name from a Response header
 * @param {Object} headers - Dictionary containing Response header information
 * @param {String} defaultName - The default name to use
 * @returns {String} - Name of the save file
 */
function getFilenameFromResponseHeader(headers, defaultName) {
    const disposition = headers.get('Content-disposition')
    let filename = "";
    if (disposition && disposition.indexOf('attachment') !== -1) {
        let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        let matches = filenameRegex.exec(disposition);
        if (matches != null && matches[1]) {
            filename = matches[1].replace(/['"]/g, '');
        }
    }
    if (!filename) {
        filename = defaultName;
    }
    return filename
}

// function prepareSubmitForm() {
//     const eventsForm = document.getElementById("events_form");
//     const formData = new FormData(eventsForm);
//     const selectedElement = document.getElementById("process_actions");
//     formData.append("command_option", selectedElement.value);
//     const eventsFile =  $("#events_file")[0];
//     formData.append('events', eventsFile.files[0])
//     const displayName = convertToResultsName(eventsFile.files[0].name, '_processed');
//     return [formData, displayName]
// }

/**
 * Create the form data and default display name for the submit form.
 * @param {string} type - The ID of the form to construct the data from.
 * @returns {[FormData, string]} - The form data and a default display name.
 */
function prepareSubmitForm(type) {
    const form = document.getElementById(`${type}_form`);
    const formData = new FormData(form);
    const selectedElement = document.getElementById("process_actions");
    formData.append("command_option", selectedElement.value);
    const fileDesignator=  $(`#${type}_file`)[0];
    let defaultName = "default_processed"
    if (fileDesignator && fileDesignator.files && fileDesignator.files.length > 0) {
        defaultName = convertToResultsName(fileDesignator.files[0].name, '_processed');
    }
    return [formData, defaultName]
}



/**
 * Gets standard failure response for download
 * @param {Object} xhr - Dictionary containing Response header information
 * @param {String} status - a status text message
 * @param {String} errorThrown - name of the error thrown
 * @param {String} display_name - Name used for the downloaded blob file
 * @param {String} flashLocation - ID of the flash location element for displaying response Message
 */
function getResponseFailure( xhr, status, errorThrown, display_name, flashLocation) {
    let info = xhr.getResponseHeader('Message');
    let category =  xhr.getResponseHeader('Category');
    if (!info) {
        info = 'Unknown processing error occurred';
    }
    info = info + '[Source: ' + display_name + ']' + '[Status:' + status + ']' + '[Error:' + errorThrown + ']';
    flashMessageOnScreen(info, category, flashLocation);
}

/**
 * Downloads a response as a file if there is data.
 * @param {String} download - The downloaded data to be turned into a file.
 * @param {Object} xhr - http response header
 * @param {String} display_name - Download filename to use if not included in the downloaded response.
 * @param {String} flashLocation - Name of the field in which to write messages if available.
 */
function getResponseSuccess(download, xhr, display_name, flashLocation) {
    let info = xhr.getResponseHeader('Message');
    let category =  xhr.getResponseHeader('Category');
    let contentType = xhr.getResponseHeader('Content-type');
    if (download && download.size !== 0) {
        let filename = getFilenameFromResponseHeader(xhr, display_name)
        triggerDownloadBlob(download, filename, contentType);
    }
    if (info) {
        flashMessageOnScreen(info, category, flashLocation);
    } else {
        flashMessageOnScreen('', 'success', flashLocation);
    }
}

/**
 * Downloads a response as a file if there is data.
 * @param {String} download - The downloaded data to be turned into a file.
 * @param {String} defaultName - Download filename to use if not included in the downloaded response.
 * @param {String} flashLocation - Name of the field in which to write messages if available.
 */
function handleResponse(response, download, defaultName, flashLocation) {
    const info = response.headers.get('Message');
    const category =  response.headers.get('Category');
    let contentType = response.headers.get('Content-type');
    if (download) {
        let filename = getFilenameFromResponseHeader(response.headers, defaultName)
        triggerDownloadBlob(download, filename, contentType);
    }
    if (info) {
        flashMessageOnScreen(info, category, flashLocation);
    } else {
        flashMessageOnScreen('', 'success', flashLocation);
    }
}

function handleResponseFailure(response, message, error, displayName, flashLocation) {
    const category =  response.headers.has('Category') ? response.headers.get('Category') : 'error';
    const flashMsg = `${message}[Source: ${displayName}][Status: ${response.status}][Error: ${error.message}]`;
    flashMessageOnScreen(flashMsg, category, flashLocation);
}



/**
 * Flash a message on the screen.
 * @param {Object} flashMessage - The li element containing the flash message.
 * @param {String} category - The msg_category of the message. The categories are 'error', 'success', and 'other'.
 */
function setFlashMessageCategory(flashMessage, category) {
    if ("error" === category) {
        flashMessage.style.backgroundColor = 'lightcoral';
    } else if ("success" === category) {
        flashMessage.style.backgroundColor = 'palegreen';
    } else if ("warning" === category) {
        flashMessage.style.backgroundColor = 'orange';
    } else {
        flashMessage.style.backgroundColor = '#f0f0f5';
    }
}

/**
 * Returns the extension of a file.
 * @param {string} filename - The filename of the file whose extension should be split off.
 * @returns string - The file extension or an empty string if there is no extension.
 *
 */
function splitExt(filename) {
    const index = filename.lastIndexOf('.');
    return (-1 !== index) ? [filename.substring(0, index), filename.substring(index + 1)] : [filename, ''];
}


/**
 * Trigger the "save as" dialog for a text blob to save as a file with display name.
 * @param {Blob|Array|String} download - Bytes or blob to put in the file
 * @param {String} displayName - File name to use if none provided in the downloaded content
 * @param {String} contentType - Type of file to create
 */
function triggerDownloadBlob(download, displayName, contentType) {
    let url;
    if ((download instanceof Blob) && (download.size > 0)) {
        url = URL.createObjectURL(download, {type: contentType});
    }  else if ((download instanceof Array) && (download.length > 0)) {
        url = URL.createObjectURL(new Blob(download, {type: contentType}));
    } else if (download.length > 0) {
        url = URL.createObjectURL(new Blob([download], {type: contentType}));
    }
    if (url) {
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', displayName);
        //document.body.appendChild(link);
        link.click();
        URL.revokeObjectURL(url); // Clean up the URL
    }
}

/**
 * Updates a file label.
 * @param {String} filePath - The path to the dictionary.
 * @param {String} displayName - The ID of the label field to set
 */
function updateFileLabel(filePath, displayName) {
    let filename = filePath.split('\\').pop();
    $(displayName).text(filename);
}
