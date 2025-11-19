
/**
 * Hides  option in the form.
 * @param {string} optionName - Name of the option checkbox to be hidden
 */
function hideOption(optionName) {
    $("#" + optionName).prop('checked', false)
    $("#" + optionName + "_option").hide()
}

/**
 * Show  option in the form.
 * @param {string} optionName - Name of the option checkbox to be shown
 * @param {boolean} checked - Indicates whether checked.
 */
function showOption(optionName, checked=false) {
    $("#" + optionName + "_option").show();
    $("#" + optionName).prop('checked', checked)
}

function showElement(id) {
    document.getElementById(id).style.display = '';
}

function hideElement(id) {
    document.getElementById(id).style.display = 'none';
}

