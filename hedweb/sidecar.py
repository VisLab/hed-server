import os
import io
import json
from flask import current_app
from werkzeug.utils import secure_filename

from hed.errors import ErrorHandler
from hed import schema as hedschema
from hed.errors import HedFileError, get_printable_issue_string

from hed.models.spreadsheet_input import SpreadsheetInput
from hed.models.sidecar import Sidecar
from hed.models import df_util
from hed.tools.analysis.annotation_util import df_to_hed, hed_to_df, merge_hed_dict

from hedweb.constants import base_constants, file_constants
from hedweb.web_util import form_has_option, generate_filename, get_hed_schema_from_pull_down, get_option

app_config = current_app.config


def get_input_from_form(request):
    """ Gets the sidecar processing input arguments from a request object.

    Args:
        request (Request): A Request object containing user data from the sidecar processing form.

    Returns:
        dict: A dictionary containing input arguments for calling the underlying sidecar processing functions.

    """

    arguments = {base_constants.SCHEMA: get_hed_schema_from_pull_down(request), base_constants.SIDECAR: None,
                 base_constants.COMMAND: request.form.get(base_constants.COMMAND_OPTION, None),
                 base_constants.CHECK_FOR_WARNINGS:
                     form_has_option(request, base_constants.CHECK_FOR_WARNINGS, 'on'),
                 base_constants.EXPAND_DEFS:
                     form_has_option(request, base_constants.EXPAND_DEFS, 'on'),
                 base_constants.INCLUDE_DESCRIPTION_TAGS:
                     form_has_option(request, base_constants.INCLUDE_DESCRIPTION_TAGS, 'on'),
                 base_constants.SPREADSHEET_TYPE: file_constants.TSV_EXTENSION,
                 }
    if base_constants.SIDECAR_FILE in request.files:
        f = request.files[base_constants.SIDECAR_FILE]
        fb = io.StringIO(f.read(file_constants.BYTE_LIMIT).decode('ascii'))
        arguments[base_constants.SIDECAR] = Sidecar(files=fb, name=secure_filename(f.filename))
    if base_constants.SPREADSHEET_FILE in request.files and \
            request.files[base_constants.SPREADSHEET_FILE].filename:
        filename = request.files[base_constants.SPREADSHEET_FILE].filename
        file_ext = os.path.splitext(filename)[1]
        if file_ext in file_constants.EXCEL_FILE_EXTENSIONS:
            arguments[base_constants.SPREADSHEET_TYPE] = file_constants.EXCEL_EXTENSION
        spreadsheet = SpreadsheetInput(file=request.files[base_constants.SPREADSHEET_FILE],
                                       file_type=arguments[base_constants.SPREADSHEET_TYPE],
                                       worksheet_name=arguments.get(base_constants.WORKSHEET_NAME, None),
                                       tag_columns=['HED'], has_column_names=True, name=filename)
        arguments[base_constants.SPREADSHEET] = spreadsheet
    return arguments


def process(arguments):
    """Perform the requested action for the sidecar.

    Args:
        arguments (dict): A dictionary with the input arguments from the sidecar form.

    Returns:
        dict: A dictionary of results in standard form.

    """
    hed_schema = arguments.get(base_constants.SCHEMA, None)
    command = arguments.get(base_constants.COMMAND, None)
    if command == base_constants.COMMAND_EXTRACT_SPREADSHEET or command == base_constants.COMMAND_MERGE_SPREADSHEET:
        pass
    elif not hed_schema or not isinstance(hed_schema, hedschema.hed_schema.HedSchema):
        raise HedFileError('BadHedSchema', "Please provide a valid HedSchema", "")
    sidecar = arguments.get(base_constants.SIDECAR, None)
    spreadsheet = arguments.get(base_constants.SPREADSHEET, 'None')
    if not sidecar:
        raise HedFileError('MissingSidecarFile', "Please give a valid JSON sidecar file to process", "")

    if command == base_constants.COMMAND_VALIDATE:
        results = sidecar_validate(hed_schema, sidecar, arguments)
    elif command == base_constants.COMMAND_TO_SHORT or command == base_constants.COMMAND_TO_LONG:
        results = sidecar_convert(hed_schema, sidecar, arguments)
    elif command == base_constants.COMMAND_EXTRACT_SPREADSHEET:
        results = sidecar_extract(sidecar)
    elif command == base_constants.COMMAND_MERGE_SPREADSHEET:
        results = sidecar_merge(sidecar, spreadsheet, arguments)
    else:
        raise HedFileError('UnknownProcessingMethod', f'Command {command} is missing or invalid', '')
    return results


def sidecar_convert(hed_schema, sidecar, options=None):
    """ Convert a sidecar from long to short form or short to long form.

    Args:
        hed_schema (HedSchema):  HedSchema object used in the conversion.
        sidecar (Sidecar):  Sidecar object to be converted in place.
        options (dict or None):  Options for this operation.

    Returns:
        dict:  A downloadable response dictionary

    Notes:
        command (str):           Either 'to short' or 'to long' indicating type of conversion.
        expand_defs (bool):      If True, expand definitions when converting, otherwise do no expansion

    """
    options[base_constants.CHECK_FOR_WARNINGS] = False
    results = sidecar_validate(hed_schema, sidecar, options)
    if results[base_constants.MSG_CATEGORY] == 'warning':
        return results
    display_name = sidecar.name
    command = get_option(options, base_constants.COMMAND, None)
    if command == base_constants.COMMAND_TO_LONG:
        tag_form = 'long_tag'
    else:
        tag_form = 'short_tag'
    error_handler = ErrorHandler(check_for_warnings=False)
    for column_data in sidecar:
        hed_strings = column_data.get_hed_strings()
        hed_strings = df_util.convert_to_form(hed_strings, hed_schema, "long_tag")
        column_data.set_hed_strings(hed_strings)

    file_name = generate_filename(display_name, name_suffix=f"_{tag_form}", extension='.json', append_datetime=True)
    data = sidecar.get_as_json_string()
    category = 'success'
    msg = f'Sidecar file {display_name} was successfully converted'
    return {base_constants.COMMAND: command, base_constants.COMMAND_TARGET: 'sidecar',
            'data': data, 'output_display_name': file_name,
            base_constants.SCHEMA_VERSION: hedschema.get_schema_versions(hed_schema, as_string=True),
            'msg_category': category, 'msg': msg}


def sidecar_extract(sidecar):
    """ Create a four-column spreadsheet with the HED portion of the JSON sidecar.

    Args:
        sidecar (Sidecar): The Sidecar from which to generate_sidecar the HED spreadsheet.

    Returns:
        dict: A downloadable dictionary file or a file containing warnings

    """

    json_string = sidecar.get_as_json_string()
    str_sidecar = json.loads(json_string)
    df = hed_to_df(str_sidecar)
    data = df.to_csv(None, sep='\t', index=False, header=True)
    display_name = sidecar.name
    file_name = generate_filename(display_name, name_suffix='_extracted', extension='.tsv', append_datetime=True)
    return {base_constants.COMMAND: base_constants.COMMAND_EXTRACT_SPREADSHEET,
            base_constants.COMMAND_TARGET: 'sidecar',
            'data': data, 'output_display_name': file_name,
            'msg_category': 'success', 'msg': f'JSON sidecar {display_name} was successfully extracted'}


def sidecar_merge(sidecar, spreadsheet, options=None):
    """ Merge an edited 4-column spreadsheet with JSON sidecar.

    Args:
        sidecar (Sidecar): The Sidecar from which to generate_sidecar the HED spreadsheet
        spreadsheet (HedInput): The Sidecar from which to generate_sidecar the HED spreadsheet
        options (dict or None): The options allowed for this operation.

    Returns:
        dict
        A downloadable dictionary file or a file containing warnings

    Notes: The allowed option for merge is:
        include_description_tags (bool): If True, a Description tag is generated from Levels and included.

    """

    include_description_tags = get_option(options, base_constants.INCLUDE_DESCRIPTION_TAGS, False)
    if not spreadsheet:
        raise HedFileError('MissingSpreadsheet', 'Cannot merge spreadsheet with sidecar', '')
    df = spreadsheet.dataframe
    hed_dict = df_to_hed(df, description_tag=include_description_tags)
    json_string = sidecar.get_as_json_string()
    sidecar_dict = json.loads(json_string)
    merge_hed_dict(sidecar_dict, hed_dict)
    display_name = sidecar.name
    data = json.dumps(sidecar_dict, indent=4)
    file_name = generate_filename(display_name, name_suffix='_extracted_merged',
                                  extension='.json', append_datetime=True)
    return {base_constants.COMMAND: base_constants.COMMAND_EXTRACT_SPREADSHEET,
            base_constants.COMMAND_TARGET: 'sidecar',
            'data': data, 'output_display_name': file_name,
            'msg_category': 'success', 'msg': f'JSON sidecar {display_name} was successfully merged'}


def sidecar_validate(hed_schema, sidecar, options=None):
    """ Validate the sidecars and return the errors and/or a message in a dictionary.

    Args:
        hed_schema (HedSchema or HedSchemaGroup): The hed schemas to be used.
        sidecar (Sidecar): A Sidecar object to validate.
        options (dict or None): A dictionary of options.

    Returns:
        dict: A dictionary of response values in standard form.

    Notes:  The allowed option for validate is:
        check_for_warnings (bool): If True, check for warnings as well as errors.

    """

    check_for_warnings = get_option(options, base_constants.CHECK_FOR_WARNINGS, True)
    command = get_option(options, base_constants.COMMAND, None)
    display_name = sidecar.name
    error_handler = ErrorHandler(check_for_warnings=check_for_warnings)
    issues = sidecar.validate(hed_schema, name=sidecar.name, error_handler=error_handler)
    if issues:
        data = get_printable_issue_string(issues, f"JSON dictionary {sidecar.name} validation errors")
        file_name = generate_filename(display_name, name_suffix='validation_errors',
                                      extension='.txt', append_datetime=True)
        category = 'warning'
        msg = f'JSON sidecar {display_name} had validation errors'
    else:
        data = ''
        file_name = display_name
        category = 'success'
        msg = f'JSON file {display_name} had no validation errors'

    return {base_constants.COMMAND: command, base_constants.COMMAND_TARGET: 'sidecar',
            'data': data, 'output_display_name': file_name,
            base_constants.SCHEMA_VERSION: hedschema.get_schema_versions(hed_schema, as_string=True),
            base_constants.MSG_CATEGORY: category, base_constants.MSG: msg}
