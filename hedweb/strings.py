from flask import current_app

from hed.errors import ErrorHandler, get_printable_issue_string, HedFileError
from hed.models.hed_string import HedString
from hed import schema as hedschema

from hedweb.constants import base_constants
from hedweb.web_util import form_has_option, get_hed_schema_from_pull_down

app_config = current_app.config


def get_input_from_form(request):
    """ Get input arguments from a request object associated with the string form.

    Args:
        request (Request): A Request object containing user data from the string form.

    Returns:
        dict: Contains input arguments for calling the underlying string processing functions.

    """
    hed_schema = get_hed_schema_from_pull_down(request)
    hed_string = request.form.get(base_constants.STRING_INPUT, None)
    if hed_string:
        string_list = [HedString(hed_string, hed_schema)]
    else:
        raise HedFileError('EmptyHedString', 'Must enter a HED string', '')
    arguments = {base_constants.COMMAND: request.form.get(base_constants.COMMAND_OPTION, ''),
                 base_constants.SCHEMA: hed_schema,
                 base_constants.STRING_LIST: string_list,
                 base_constants.CHECK_FOR_WARNINGS:
                     form_has_option(request, base_constants.CHECK_FOR_WARNINGS, 'on')}
    return arguments


def process(arguments):
    """ Perform the requested string processing action.

    Args:
        arguments (dict): A dictionary with the input arguments from the string form or string service request.

    Returns:
        dict: The results in standard format.

    """
    hed_schema = arguments.get('schema', None)
    if not hed_schema or not isinstance(hed_schema, hedschema.hed_schema.HedSchema):
        raise HedFileError('BadHedSchema', "Please provide a valid HedSchema", "")
    string_list = arguments.get(base_constants.STRING_LIST, None)
    command = arguments.get(base_constants.COMMAND, None)
    check_for_warnings = arguments.get(base_constants.CHECK_FOR_WARNINGS, False)
    if not string_list:
        raise HedFileError('EmptyHedStringList', "Please provide a list of HED strings to be processed", "")
    if command == base_constants.COMMAND_VALIDATE:
        results = validate(hed_schema, string_list, check_for_warnings=check_for_warnings)
    elif command == base_constants.COMMAND_TO_SHORT:
        results = convert(hed_schema, string_list, command, check_for_warnings=check_for_warnings)
    elif command == base_constants.COMMAND_TO_LONG:
        results = convert(hed_schema, string_list, command, check_for_warnings=check_for_warnings)
    else:
        raise HedFileError('UnknownProcessingMethod', f'Command {command} is missing or invalid', '')
    return results


def convert(hed_schema, string_list, command=base_constants.COMMAND_TO_SHORT, check_for_warnings=False):
    """ Convert a list of strings from long to short or long to short then converts to short.

    Args:
        hed_schema (HedSchema or HedSchemas): The HED schema to be used in processing.
        string_list (list): A list of HedString to be processed.
        command (str): Name of the command to execute (default to short if unrecognized)
        check_for_warnings (bool): Indicates whether validation should check for warnings as well as errors.

    Returns:
        dict: The results of string processing in standard format.

    """

    results = validate(hed_schema, string_list, check_for_warnings=check_for_warnings)
    if results['data']:
        return results
    strings = []
    conversion_errors = []
    for pos, hed_string_obj in enumerate(string_list, start=1):
        if command == base_constants.COMMAND_TO_LONG:
            converted_string = hed_string_obj.get_as_form('long_tag')
        else:
            converted_string = hed_string_obj.get_as_form('short_tag')
        strings.append(converted_string)

        return {base_constants.COMMAND: command,
                base_constants.COMMAND_TARGET: 'strings', 'data': strings,
                base_constants.SCHEMA_VERSION: hed_schema.get_formatted_version(),
                'msg_category': 'success',
                'msg': 'Strings converted successfully'}


def validate(hed_schema, string_list, check_for_warnings=False):
    """ Validate a list of strings and returns a dictionary containing the issues or a no issues message.

    Args:
        hed_schema (HedSchema or HedSchemas): The HED schema to be used in processing.
        string_list (list): A list of strings to be processed.
        check_for_warnings (bool): If True, check for warnings as well as errors

    Returns:
        dict: The results in standard form.
    """

    validation_issues = []
    error_handler = ErrorHandler(check_for_warnings=check_for_warnings)
    for pos, h_string in enumerate(string_list, start=1):
        issues = h_string.validate(hed_schema, error_handler=error_handler)
        if issues:
            validation_issues.append(get_printable_issue_string(issues, f"Errors for HED string {pos}:"))
    if validation_issues:
        return {base_constants.COMMAND: base_constants.COMMAND_VALIDATE,
                base_constants.COMMAND_TARGET: 'strings', 'data': validation_issues,
                base_constants.SCHEMA_VERSION: hed_schema.get_formatted_version(),
                'msg_category': 'warning',
                'msg': 'Strings had validation issues'}
    else:
        return {base_constants.COMMAND: base_constants.COMMAND_VALIDATE,
                base_constants.COMMAND_TARGET: 'strings', 'data': '',
                base_constants.SCHEMA_VERSION: hed_schema.get_formatted_version(),
                'msg_category': 'success',
                'msg': 'Strings validated successfully...'}
