from flask import current_app
from hed.errors import get_printable_issue_string, HedFileError
from hed.schema.schema_compare import compare_differences
from hedweb.web_util import form_has_file, form_has_option, form_has_url, generate_filename, get_schema
from hedweb.constants import base_constants, file_constants

app_config = current_app.config


def format_error(command, issues, display_name):
    issue_str = get_printable_issue_string(issues, f"Schema issues for {display_name}:")
    file_name = generate_filename(display_name, name_suffix='schema_issues', extension='.txt')
    return {'command': command,
            base_constants.COMMAND_TARGET: 'schema',
            'data': issue_str, 'output_display_name': file_name,
            'msg_category': 'warning',
            'msg': 'Schema had issues'
            }


def get_input_from_form(request):
    """ Extract a dictionary of input for processing from the schema form.

    Args:
        request (Request): A Request object containing user data from the schema form.

    Returns:
        dict: A dictionary of schema processing parameters in standard form.

    Raises:
        HedFileError:  If the input arguments were missing or not valid.

    """

    arguments = {
                    base_constants.COMMAND: request.form.get(base_constants.COMMAND_OPTION, ''),
                    base_constants.CHECK_FOR_WARNINGS:
                    form_has_option(request, base_constants.CHECK_FOR_WARNINGS, 'on')
                }
    if form_has_option(request, base_constants.SCHEMA_UPLOAD_OPTIONS, base_constants.SCHEMA_FILE_OPTION) and \
            form_has_file(request, base_constants.SCHEMA_FILE, file_constants.SCHEMA_EXTENSIONS):
        arguments["schema1"] = get_schema(request.files[base_constants.SCHEMA_FILE], input_type='file')
    elif form_has_option(request, base_constants.SCHEMA_UPLOAD_OPTIONS, base_constants.SCHEMA_URL_OPTION) and \
            form_has_url(request, base_constants.SCHEMA_URL, file_constants.SCHEMA_EXTENSIONS):
        arguments["schema1"] = get_schema(request.values[base_constants.SCHEMA_URL], input_type='url')
    else:
        raise HedFileError("SCHEMA_NOT_FOUND", "Must provide a loadable schema", "")

    if form_has_option(request, base_constants.SECOND_SCHEMA_UPLOAD_OPTIONS,
                       base_constants.SECOND_SCHEMA_FILE_OPTION) and \
            form_has_file(request, base_constants.SECOND_SCHEMA_FILE, file_constants.SCHEMA_EXTENSIONS):
        arguments["schema2"] = get_schema(request.files[base_constants.SECOND_SCHEMA_FILE], input_type='file')
    elif form_has_option(request, base_constants.SECOND_SCHEMA_UPLOAD_OPTIONS,
                         base_constants.SECOND_SCHEMA_URL_OPTION) and \
            form_has_url(request, base_constants.SECOND_SCHEMA_URL, file_constants.SCHEMA_EXTENSIONS):
        arguments["schema2"] = get_schema(request.values[base_constants.SECOND_SCHEMA_URL], input_type='url')
    return arguments


def process(arguments):
    """ Perform the requested action for the schema.

    Args:
        arguments (dict): A dictionary with the input arguments extracted from the schema form or service request.

    Returns:
        dict: A dictionary of results in the standard results format.

    Raises:
        HedFileError:  If the command was not found or the input arguments were not valid.

    """

    if base_constants.COMMAND not in arguments or arguments[base_constants.COMMAND] == '':
        raise HedFileError('MissingCommand', 'Command is missing', '')
    schema1_dict = arguments["schema1"]
    if schema1_dict["issues"]:
        return format_error(arguments[base_constants.COMMAND], schema1_dict["issues"],
                            schema1_dict["name"]+"_schema_errors")
    elif arguments[base_constants.COMMAND] == base_constants.COMMAND_VALIDATE:
        results = schema_validate(schema1_dict["schema"], schema1_dict["name"])
    elif arguments[base_constants.COMMAND] == base_constants.COMMAND_COMPARE_SCHEMAS:
        schema2_dict = arguments["schema2"]
        if not schema2_dict or schema2_dict["issues"]:
            return format_error(arguments[base_constants.COMMAND], schema2_dict["issues"],
                                schema2_dict["name"] + "_schema2_errors")
        results = schema_compare(schema1_dict["schema"], schema1_dict["name"],
                                 schema2_dict["schema"], schema2_dict["name"])
    elif arguments[base_constants.COMMAND] == base_constants.COMMAND_CONVERT_SCHEMA:
        results = schema_convert(schema1_dict["schema"], schema1_dict["name"], schema1_dict["type"])
    else:
        raise HedFileError('UnknownProcessingMethod', "Select a schema processing method", "")
    return results


def schema_compare(hed_schema1, display_name1, hed_schema2, display_name2):
    data = compare_differences(hed_schema1, hed_schema2, output='string', sections=None)
    output_name = display_name1 + '_' + display_name2 + '_' + "differences.txt"
    msg_results = ''
    if not data:
        msg_results = ': no differences found'
    return {'command': base_constants.COMMAND_COMPARE_SCHEMAS,
            base_constants.COMMAND_TARGET: 'schema',
            'data': data, 'output_display_name': output_name,
            'schema_version': hed_schema1.get_formatted_version(),
            'msg_category': 'success',
            'msg': 'Schemas were successfully compared' + msg_results}


def schema_convert(hed_schema, display_name, schema_format):
    """ Return a string representation of hed_schema in the desired format as determined by the display name extension.

    Args:
        hed_schema (HedSchema): A HedSchema object containing the schema to be processed.
        display_name (str): The schema display name whose extension determines the conversion format.
        schema_format (str): The format of the incoming HedSchema object

    Returns:
        dict: A dictionary of results in the standard results format.

    """

    if schema_format == file_constants.SCHEMA_XML_EXTENSION:
        data = hed_schema.get_as_mediawiki_string()
        extension = '.mediawiki'
    else:
        data = hed_schema.get_as_xml_string()
        extension = '.xml'
    file_name = display_name + extension

    return {'command': base_constants.COMMAND_CONVERT_SCHEMA,
            base_constants.COMMAND_TARGET: 'schema',
            'data': data, 'output_display_name': file_name,
            'schema_version': hed_schema.get_formatted_version(),
            'msg_category': 'success',
            'msg': 'Schema was successfully converted'}


def schema_validate(hed_schema, display_name):
    """ Run schema compliance for HED-3G.

    Args:
        hed_schema (HedSchema): A HedSchema object containing the schema to be processed.
        display_name (str): The display name associated with this schema object (used in error reports).

    Returns:
        dict: A dictionary of results in the standard results format.

    """

    issues = hed_schema.check_compliance()
    if issues:
        issue_str = get_printable_issue_string(issues, f"Schema issues for {display_name}:")
        file_name = display_name + 'schema_issues.txt'
        return {'command': base_constants.COMMAND_VALIDATE,
                base_constants.COMMAND_TARGET: 'schema',
                'data': issue_str, 'output_display_name': file_name,
                'schema_version': hed_schema.get_formatted_version(),
                'msg_category': 'warning',
                'msg': 'Schema has validation issues'}
    else:
        return {'command': base_constants.COMMAND_VALIDATE,
                base_constants.COMMAND_TARGET: 'schema',
                'data': '', 'output_display_name': display_name,
                'schema_version': hed_schema.get_formatted_version(),
                'msg_category': 'success',
                'msg': 'Schema had no validation issues'}


def get_issue_string(issues, title=None):
    """ Return a string with issues list flatted into single string, one issue per line.

    Parameters:
        issues (list):  A list of strings containing issues to print.
        title (str or None): An optional title that will always show up first if present.

    Returns:
        str: A str containing printable version of the issues or ''.

    """

    issue_str = ''
    if issues:
        issue_list = []
        for issue in issues:
            if isinstance(issue, str):
                issue_list.append(f"ERROR: {issue}.")
            else:
                this_str = f"{issue['message']}"
                if 'code' in issue:
                    this_str = f"{issue['code']}:" + this_str
                if 'line_number' in issue:
                    this_str = this_str + f"\n\tLine number {issue['line_number']}: {issue.get('line', '')} "
                issue_list.append(this_str)
        issue_str += '\n' + '\n'.join(issue_list)
    if title:
        issue_str = title + '\n' + issue_str
    return issue_str
