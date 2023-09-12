import io
from datetime import datetime
import json
import os
import zipfile
from urllib.parse import urlparse
from flask import current_app, Response, make_response, send_file
from werkzeug.utils import secure_filename

from hed import schema as hedschema
from hed import HedSchema, HedSchemaGroup

from hed.errors import HedFileError, ErrorSeverity, ErrorHandler
from hedweb.constants import base_constants, file_constants

app_config = current_app.config

TIME_FORMAT = '%Y_%m_%d_T_%H_%M_%S_%f'


def convert_hed_versions(hed_info):
    hed_list = []
    for key, key_list in hed_info['schema_version_list'].items():
        if key is None:
            hed_list = hed_list + key_list
        else:
            hed_list = hed_list + [key + '_' + element for element in key_list]
    return {'schema_version_list': hed_list}


def file_extension_is_valid(filename, accepted_extensions=None):
    """ Return True if the file extension is an accepted one.

    Args:
        filename (str): The name of the file to be checked.
        accepted_extensions (list): A list of accepted extensions.

    Returns:
        bool: True if the file has an accepted extension.

    """
    return not accepted_extensions or os.path.splitext(filename.lower())[1] in accepted_extensions


def filter_issues(issues, check_for_warnings):
    """ Filter an issues list by severity level to allow warnings. """
    if not check_for_warnings:
        issues = ErrorHandler.filter_issues_by_severity(issues, ErrorSeverity.ERROR)
    return issues


def form_has_file(request, file_field, valid_extensions=None):
    """ Return True if a file with valid extension is in the request.

    Args:
        request (Request): A Request object containing user data from the form.
        file_field (str): Name of the form field containing the file name.
        valid_extensions (list): A list of valid extensions.

    Returns:
        bool: True if a file is present in a request object.

    """

    if file_field in request.files and file_extension_is_valid(request.files[file_field].filename, valid_extensions):
        return True
    else:
        return False


def form_has_option(request, option_name, target_value):
    """ Return True if given option has a specific value.

    Args:
        request (Request): A Request object produced by the post of a form.
        option_name (str): The name of the radio button group in the hedweb form.
        target_value (str): The name of the selected radio button option.

    Returns:
        bool: True if the target radio button has been set and false otherwise.

    Notes:
        -  This is used for radio buttons and check boxes.

    """

    if option_name in request.form and request.form[option_name] == target_value:
        return True
    return False


def form_has_url(request, url_field, valid_extensions=None):
    """ Return True if the url_field has a valid extension.

    Args:
        request (Request): A Request object containing form data.
        url_field (str): The name of the form field with the URL to be parsed.
        valid_extensions (list): A list of valid extensions.

    Returns:
        bool: True if a URL is present in request object.

    """
    if url_field not in request.form:
        return False
    parsed_url = urlparse(request.form.get(url_field))
    return file_extension_is_valid(parsed_url.path, valid_extensions)


def generate_download_file_from_text(results, file_header=None):
    """ Generate a download file from text output.

    Args:
        results: Text with newlines for iterating.
        file_header (str): Optional header for download file blob.

    Returns:
        Response: A Response object containing the downloaded file.

    """
    display_name = results.get('output_display_name', None)
    if display_name is None:
        display_name = 'download.txt'

    download_text = results.get('data', '')
    if not download_text:
        raise HedFileError('EmptyDownloadText', "No download text given", "")

    def generate():
        if file_header:
            yield file_header
        for issue in download_text.splitlines(True):
            yield issue

    return Response(generate(), mimetype='text/plain charset=utf-8',
                    headers={'Content-Disposition': f"attachment filename={display_name}",
                             'Category': results[base_constants.MSG_CATEGORY],
                             'Message': results[base_constants.MSG]})


def generate_download_spreadsheet(results):
    """ Generate a download Excel file.

    Args:
        results (dict): Dictionary with the results to be downloaded.

    Returns:
        Response: A Response object containing the downloaded file.

    """
    # return generate_download_test()
    spreadsheet = results[base_constants.SPREADSHEET]
    if not spreadsheet.loaded_workbook:
        return generate_download_file_from_text({'data': spreadsheet.to_csv(),
                                                 'output_display_name': results[base_constants.OUTPUT_DISPLAY_NAME],
                                                 base_constants.MSG_CATEGORY: results[base_constants.MSG_CATEGORY],
                                                 base_constants.MSG: results[base_constants.MSG]})
    buffer = io.BytesIO()
    spreadsheet.to_excel(buffer)
    buffer.seek(0)
    response = make_response()
    response.data = buffer.read()
    response.headers['Content-Disposition'] = 'attachment; filename=' + results[base_constants.OUTPUT_DISPLAY_NAME]
    response.headers['Category'] = results[base_constants.MSG_CATEGORY]
    response.headers['Message'] = results[base_constants.MSG]
    response.mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response


def generate_filename(base_name, name_prefix=None, name_suffix=None, extension=None, append_datetime=False):
    """ Generate a filename for the attachment.

    Parameters:
        base_name (str):   Name of the base, usually the name of the file that the issues were generated from.
        name_prefix (str): Prefix prepended to the front of the base name.
        name_suffix (str): Suffix appended to the end of the base name.
        extension (str):   Extension to use.
        append_datetime (bool): If True, append the current date-time to the base output filename.

    Returns:
        str:  Name of the attachment other containing the issues.

    Notes:
        - The form prefix_basename_suffix + extension.

    """

    pieces = []
    if name_prefix:
        pieces = pieces + [name_prefix]
    if base_name:
        pieces.append(os.path.splitext(base_name)[0])
    if name_suffix:
        pieces = pieces + [name_suffix]
    filename = "".join(pieces)
    if append_datetime:
        now = datetime.now()
        filename = filename + '_' + now.strftime(TIME_FORMAT)[:-3]
    if filename and extension:
        filename = filename + extension

    return secure_filename(filename)


def generate_text_response(results):
    """ Generate a download response.

    Args:
        results (dict): Dictionary containing the results of the data.

    Returns:
        Response: A Response object containing the downloaded file.


    """
    headers = {'Category': results[base_constants.MSG_CATEGORY], 'Message': results[base_constants.MSG]}
    download_text = results.get('data', '')
    if len(download_text) > 0:
        headers['Content-Length'] = len(download_text)
    return Response(download_text, mimetype='text/plain charset=utf-8', headers=headers)


def generate_download_zip_file(results):
    """ Generate a download response.

    Args:
        results (dict): Dictionary of results to use in constructing response.

    Returns:
        Response: A Response object containing the downloaded file.


    """

    file_list = results[base_constants.FILE_LIST]
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, mode="a", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in file_list:
            zf.writestr(item['file_name'], str.encode(item['content'], 'utf-8'))
    archive.seek(0)
    zip_name = results.get('zip_name', results['output_display_name'])
    response = send_file(archive, as_attachment=True, download_name=zip_name)
    response.headers['Message'] = results[base_constants.MSG]
    response.headers['Category'] = results[base_constants.MSG_CATEGORY]
    return response


def get_hed_schema_from_pull_down(request):
    """ Create a HedSchema object from form pull-down box.

    Args:
        request (Request): A Request object containing form data.

    Returns:
        HedSchema: The HED schema to use.

    """

    if base_constants.SCHEMA_VERSION not in request.form:
        raise HedFileError("NoSchemaError", "Must provide a valid schema or schema version", "")
    elif request.form[base_constants.SCHEMA_VERSION] != base_constants.OTHER_VERSION_OPTION:
        version = request.form[base_constants.SCHEMA_VERSION].split('_')
        if len(version) == 1:
            hed_file_path = hedschema.get_path_from_hed_version(version[0])
        else:
            hed_file_path = hedschema.get_path_from_hed_version(version[1], library_name=version[0])
        hed_schema = hedschema.load_schema(hed_file_path)
    elif request.form[base_constants.SCHEMA_VERSION] == \
            base_constants.OTHER_VERSION_OPTION and base_constants.SCHEMA_PATH in request.files:
        f = request.files[base_constants.SCHEMA_PATH]
        hed_schema = hedschema.from_string(f.read(file_constants.BYTE_LIMIT).decode('ascii'),
                                           schema_format=secure_filename(f.filename))
    else:
        raise HedFileError("NoSchemaFile", "Must provide a valid schema for upload if other chosen", "")
    return hed_schema


def get_option(options, option_name, default_value):
    option_value = default_value
    if options and option_name in options:
        option_value = options[option_name]
    return option_value


def get_parsed_name(filename, is_url=False):
    if is_url:
        filename = urlparse(filename).path
    display_name, file_type = os.path.splitext(os.path.basename(filename))
    return display_name, file_type


def get_schema(schema_input, input_type="version", schema_format='.xml', display_name=''):
    """ Return a HedSchema object from the given parameters.

    Args:
        schema_input (str, file): A string indicating the schema based on the input_type
        input_type (str): 'filename', 'url', 'version', or 'string' indicating how to interpret schema_input.
        schema_format (str): file extension of the schema format.
        display_name (str): Display name of the schema if known.

    Returns:
        HedSchema: The extracted HedSchema object if successful.
        dict: A dictionary that can be returned as a response if errors.

    """
    hed_schema = None
    file_found = True
    issues_dict = {}
    name = display_name
    extension = schema_format
    try:
        if input_type == 'file':
            name, extension = get_parsed_name(secure_filename(schema_input.filename))
            hed_schema = hedschema.from_string(schema_input.read(file_constants.BYTE_LIMIT).decode('ascii'),
                                               schema_format=extension)
        elif input_type == 'url':
            name, extension = get_parsed_name(schema_input, is_url=True)
            hed_schema = hedschema.load_schema(schema_input)
        elif input_type == 'string':
            hed_schema = hedschema.from_string(schema_input, schema_format=schema_format)
        elif input_type == 'version':
            name = schema_input
            extension = '.xml'
            hed_schema = hedschema.load_schema_version(schema_input)
        else:
            file_found = False
        if not file_found:
            raise HedFileError("SCHEMA_NOT_FOUND", "Must provide a loadable schema", "")
    except HedFileError as e:
        if e.issues:
            issues_dict = e.issues
    except Exception as ex:   # TODO: remove after schema load is updated
        issues_dict = [{"code":"BAD_FILE", "message": ex.args[0]}]
    return {"schema": hed_schema, "name": name, "type": extension, "issues": issues_dict}


def get_schema_versions(hed_schema):
    if isinstance(hed_schema, HedSchema) or isinstance(hed_schema, HedSchemaGroup):
        return hed_schema.get_formatted_version()
    if not hed_schema:
        return ''
    else:
        raise ValueError("InvalidHedSchemaOrHedSchemaGroup", "Expected schema or schema group")


def handle_error(ex, hed_info=None, title=None, return_as_str=True):
    """ Handle an error by returning a dictionary or simple string.

    Args:
        ex (Exception): The exception raised.
        hed_info (dict): A dictionary of information describing the error.
        title (str):  A title to be included with the message.
        return_as_str (bool): If true return as string otherwise as dictionary.

    Returns:
        str or dict: Contains error information.

    """

    if not hed_info:
        hed_info = {}
    if hasattr(ex, 'error_type'):
        error_code = ex.error_type
    else:
        error_code = type(ex).__name__

    if not title:
        title = ''
    if hasattr(ex, 'message'):
        message = ex.message
    else:
        message = str(ex)

    hed_info['message'] = f"{title}[{error_code}: {message}]"
    if return_as_str:
        return json.dumps(hed_info)
    else:
        hed_info['error_type'] = error_code
        return hed_info


def handle_http_error(ex):
    """ Handle a http error.

    Args:
        ex (Exception): A class that extends python Exception class.

    Returns:
        Response: A response object indicating the field_type of error.

    """
    if hasattr(ex, 'error_type'):
        error_code = ex.error_type
    elif hasattr(ex, 'code'):
        error_code = ex.code
    else:
        error_code = type(ex).__name__
    if hasattr(ex, 'message'):
        message = ex.message
    else:
        message = str(ex)
    message = message.replace('\n', ' ')
    if hasattr(ex, 'filename'):
        filename = str(ex.filename)
    else:
        filename = ''
    error_message = f"{error_code}: {filename} [{message}]"
    return generate_text_response({'data': '', base_constants.MSG_CATEGORY: 'error', base_constants.MSG: error_message})


def package_results(results):
    """Package a results dictionary into a standard form.

    Args:
        results (dict): A dictionary with the results

    """

    if results.get(base_constants.FILE_LIST, None):
        return generate_download_zip_file(results)
    elif results.get('data', None) and results.get('command_target', None) != 'spreadsheet':
        return generate_download_file_from_text(results)
    elif results.get('data', None) or not results.get('spreadsheet', None):
        return generate_text_response(results)
    else:
        return generate_download_spreadsheet(results)
