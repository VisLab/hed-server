
/**
 * Hides  option in the form.
 * @param {string} optionName - Name of the option checkbox to be hidden
 */
function hideOption(optionName) {
    const el = document.getElementById(optionName);
    if (el) el.checked = false;
    const optEl = document.getElementById(optionName + "_option");
    if (optEl) optEl.style.display = 'none';
}

/**
 * Show  option in the form.
 * @param {string} optionName - Name of the option checkbox to be shown
 * @param {boolean} checked - Indicates whether checked.
 */
function showOption(optionName, checked=false) {
    const optEl = document.getElementById(optionName + "_option");
    if (optEl) optEl.style.display = '';
    const el = document.getElementById(optionName);
    if (el) el.checked = checked;
}

function showElement(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = '';
}

function hideElement(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
}

