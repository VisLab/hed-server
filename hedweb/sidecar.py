import io
import json
from flask import current_app
from werkzeug.utils import secure_filename

from hed import schema as hedschema
from hed.validator import HedValidator
from hed.errors import HedFileError, get_printable_issue_string

from hed.models import HedInput, Sidecar
from hed.tools import df_to_hed, hed_to_df, merge_hed_dict
from hed.util import generate_filename, get_file_extension
from hedweb.constants import base_constants, file_constants
from hedweb.web_util import form_has_option, get_hed_schema_from_pull_down

app_config = current_app.config


def get_input_from_form(request):
    """ Gets the sidecar processing input arguments from a request object.

    Args:
        request (Request): A Request object containing user data from the sidecar processing form.

    Returns:
        dict: A dictionary containing input arguments for calling the underlying sidecar processing functions.

    """

    arguments = {base_constants.SCHEMA: get_hed_schema_from_pull_down(request), base_constants.JSON_SIDECAR: None,
                 base_constants.COMMAND: request.form.get(base_constants.COMMAND_OPTION, None),
                 base_constants.CHECK_FOR_WARNINGS:
                     form_has_option(request, base_constants.CHECK_FOR_WARNINGS, 'on'),
                 base_constants.EXPAND_DEFS:
                     form_has_option(request, base_constants.EXPAND_DEFS, 'on'),
                 base_constants.INCLUDE_DESCRIPTION_TAGS:
                     form_has_option(request, base_constants.INCLUDE_DESCRIPTION_TAGS, 'on'),
                 base_constants.SPREADSHEET_TYPE: file_constants.TSV_EXTENSION,
                 }
    if base_constants.JSON_FILE in request.files:
        f = request.files[base_constants.JSON_FILE]
        fb = io.StringIO(f.read(file_constants.BYTE_LIMIT).decode('ascii'))
        arguments[base_constants.JSON_SIDECARS] = [Sidecar(file=fb, name=secure_filename(f.filename))]
    if base_constants.SPREADSHEET_FILE in request.files and \
            request.files[base_constants.SPREADSHEET_FILE].filename:
        filename = request.files[base_constants.SPREADSHEET_FILE].filename
        file_ext = get_file_extension(filename)
        if file_ext in file_constants.EXCEL_FILE_EXTENSIONS:
            arguments[base_constants.SPREADSHEET_TYPE] = file_constants.EXCEL_EXTENSION
        spreadsheet = HedInput(file=request.files[base_constants.SPREADSHEET_FILE],
                               file_type=arguments[base_constants.SPREADSHEET_TYPE],
                               worksheet_name=arguments.get(base_constants.WORKSHEET_NAME, None),
                               tag_columns=['HED'], has_column_names=True, name=filename)
        arguments[base_constants.SPREADSHEET] = spreadsheet
    return arguments


def process(arguments):
    """Perform the requested action for the sidecar.

    Parameters
    ----------
    arguments: dict
        A dictionary with the input arguments from the sidecar form

    Returns
    -------
      dict
        A dictionary of results.
    """
    hed_schema = arguments.get(base_constants.SCHEMA, None)
    command = arguments.get(base_constants.COMMAND, None)
    if command == base_constants.COMMAND_EXTRACT_SPREADSHEET or command == base_constants.COMMAND_MERGE_SPREADSHEET:
        pass
    elif not hed_schema or not isinstance(hed_schema, hedschema.hed_schema.HedSchema):
        raise HedFileError('BadHedSchema', "Please provide a valid HedSchema", "")
    json_sidecars = arguments.get(base_constants.JSON_SIDECARS, [])
    spreadsheet = arguments.get(base_constants.SPREADSHEET, 'None')
    if not json_sidecars:
        raise HedFileError('MissingJSONFile', "Please give at least 1 valid JSON file to process", "")
    for index, sidecar in enumerate(json_sidecars):
        if not isinstance(sidecar, Sidecar):
            raise HedFileError('InvalidJSONFile', f"Sidecar number {index+1} is invalid", "")
    check_for_warnings = arguments.get(base_constants.CHECK_FOR_WARNINGS, False)
    expand_defs = arguments.get(base_constants.EXPAND_DEFS, False)
    include_description_tags = arguments.get(base_constants.INCLUDE_DESCRIPTION_TAGS, False)
    if command == base_constants.COMMAND_VALIDATE:
        results = sidecar_validate(hed_schema, json_sidecars, check_for_warnings=check_for_warnings)
    elif command == base_constants.COMMAND_TO_SHORT or command == base_constants.COMMAND_TO_LONG:
        results = sidecar_convert(hed_schema, json_sidecars[0], command=command, expand_defs=expand_defs)
    elif command == base_constants.COMMAND_EXTRACT_SPREADSHEET:
        results = sidecar_extract(json_sidecars[0])
    elif command == base_constants.COMMAND_MERGE_SPREADSHEET:
        results = sidecar_merge(json_sidecars[0], spreadsheet, include_description_tags)
    else:
        raise HedFileError('UnknownProcessingMethod', f'Command {command} is missing or invalid', '')
    return results


def sidecar_convert(hed_schema, json_sidecar, command=base_constants.COMMAND_TO_SHORT, expand_defs=False):
    """ Convert a sidecar from long to short form or short to long form.

    Args:
        hed_schema (HedSchema):  HedSchema object used in the conversion.
        json_sidecar (Sidecar):  Sidecar object to be converted in place.
        command (str):           Either 'to short' or 'to long' indicating type of conversion.
        expand_defs (bool):      If True, expand definitions when converting, otherwise do no expansion.

    Returns:
        dict:  A downloadable response dictionary

    """

    schema_version = hed_schema.header_attributes.get('version', 'Unknown version')
    results = sidecar_validate(hed_schema, [json_sidecar], check_for_warnings=False)
    if results['data']:
        return results
    if command == base_constants.COMMAND_TO_LONG:
        tag_form = 'long_tag'
    else:
        tag_form = 'short_tag'
    issues = []
    for hed_string_obj, position_info, issue_items in json_sidecar.hed_string_iter(hed_ops=hed_schema,
                                                                                   expand_defs=expand_defs,
                                                                                   remove_definitions=False):

        converted_string = hed_string_obj.get_as_form(tag_form)
        issues = issues + issue_items
        json_sidecar.set_hed_string(converted_string, position_info)

    # issues = ErrorHandler.filter_issues_by_severity(issues, ErrorSeverity.ERROR)
    display_name = json_sidecar.name
    if issues:
        issue_str = get_printable_issue_string(issues, f"JSON conversion for {display_name} was unsuccessful")
        file_name = generate_filename(display_name, name_suffix=f"_{tag_form}_conversion_errors", extension='.txt')
        return {base_constants.COMMAND: command,
                base_constants.COMMAND_TARGET: 'sidecar',
                'data': issue_str, 'output_display_name': file_name,
                base_constants.SCHEMA_VERSION: schema_version, 'msg_category': 'warning',
                'msg': f'JSON file {display_name} had validation errors'}
    else:
        file_name = generate_filename(display_name, name_suffix=f"_{tag_form}", extension='.json')
        data = json_sidecar.get_as_json_string()
        return {base_constants.COMMAND: command,
                base_constants.COMMAND_TARGET: 'sidecar',
                'data': data, 'output_display_name': file_name,
                base_constants.SCHEMA_VERSION: schema_version, 'msg_category': 'success',
                'msg': f'JSON sidecar {display_name} was successfully converted'}


def sidecar_extract(json_sidecar):
    """ Create a four-column spreadsheet with the HED portion of the JSON sidecar.

    Args:
        json_sidecar (Sidecar): The Sidecar from which to generate_sidecar the HED spreadsheet

    Returns:
        dict
        A downloadable dictionary file or a file containing warnings

    """

    json_string = json_sidecar.get_as_json_string()
    sidecar = json.loads(json_string)
    df = hed_to_df(sidecar)
    data = df.to_csv(None, sep='\t', index=False, header=True)
    display_name = json_sidecar.name
    file_name = generate_filename(display_name, name_suffix='_extracted', extension='.tsv')
    return {base_constants.COMMAND: base_constants.COMMAND_EXTRACT_SPREADSHEET,
            base_constants.COMMAND_TARGET: 'sidecar',
            'data': data, 'output_display_name': file_name,
            'msg_category': 'success', 'msg': f'JSON sidecar {display_name} was successfully extracted'}


def sidecar_merge(json_sidecar, spreadsheet, include_description_tags=False):
    """ Merge an edited 4-column spreadsheet with JSON sidecar.

    Args:
        json_sidecar (Sidecar): The Sidecar from which to generate_sidecar the HED spreadsheet
        spreadsheet (HedInput): The Sidecar from which to generate_sidecar the HED spreadsheet
        include_description_tags (bool): If True, a Description tag is generated from Levels and included.

    Returns:
        dict
        A downloadable dictionary file or a file containing warnings

    """

    if not spreadsheet:
        raise HedFileError('MissingSpreadsheet', f'Cannot merge spreadsheet with sidecar', '')
    df = spreadsheet.dataframe
    hed_dict = df_to_hed(df, description_tag=include_description_tags)
    json_string = json_sidecar.get_as_json_string()
    sidecar_dict = json.loads(json_string)
    merge_hed_dict(sidecar_dict, hed_dict)
    display_name = json_sidecar.name
    data = json.dumps(sidecar_dict, indent=4)
    file_name = generate_filename(display_name, name_suffix='_extracted_merged', extension='.json')
    return {base_constants.COMMAND: base_constants.COMMAND_EXTRACT_SPREADSHEET,
            base_constants.COMMAND_TARGET: 'sidecar',
            'data': data, 'output_display_name': file_name,
            'msg_category': 'success', 'msg': f'JSON sidecar {display_name} was successfully merged'}


def sidecar_validate(hed_schema, json_sidecars, check_for_warnings=False):
    """ Validate the sidecars and return the errors and/or a message in a dictionary

    Args:
        hed_schema (HedSchema or HedSchemaGroup): The hed schemas to be used.
    json_sidecars (list): A list of Sidecar
        Dictionary object
    check_for_warnings: bool
        Indicates whether validation should check for warnings as well as errors

    Returns
    -------
    dict
        dictionary of response values.
    """

    schema_version = hed_schema.header_attributes.get('version', 'Unknown version')
    display_name = json_sidecars[0].name
    if len(json_sidecars) > 1:
        display_name = f"List_of_{len(json_sidecars)}_starting_with_{display_name}"
    validator = HedValidator(hed_schema)
    issue_str = ''
    for sidecar in json_sidecars:
        issues = sidecar.validate_entries(validator, check_for_warnings=check_for_warnings)
        if issues:
            issue_str = issue_str + \
                        get_printable_issue_string(issues, f"JSON dictionary {sidecar.name} validation errors")

    if issue_str:
        file_name = generate_filename(display_name, name_suffix='validation_errors', extension='.txt')
        return {base_constants.COMMAND: base_constants.COMMAND_VALIDATE,
                base_constants.COMMAND_TARGET: 'sidecar',
                'data': issue_str, 'output_display_name': file_name,
                base_constants.SCHEMA_VERSION: schema_version, 'msg_category': 'warning',
                'msg': f'JSON sidecar {display_name} had validation errors'}
    else:
        return {base_constants.COMMAND: base_constants.COMMAND_VALIDATE,
                base_constants.COMMAND_TARGET: 'sidecar', 'data': '',
                base_constants.SCHEMA_VERSION: schema_version, 'msg_category': 'success',
                'msg': f'JSON file {display_name} had no validation errors'}
