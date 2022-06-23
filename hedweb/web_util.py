import io
import json
import os
from urllib.parse import urlparse
from flask import current_app, Response, make_response
from werkzeug.utils import secure_filename

from hed import schema as hedschema

from hed.errors import HedFileError
from hedweb.constants import base_constants, file_constants

app_config = current_app.config


def file_extension_is_valid(filename, accepted_extensions=None):
    """ Return True if the file extension is an accepted one.

    Args:
        filename (str): The name of the file to be checked.
        accepted_extensions (list): A list of accepted extensions.

    Returns:
        bool: True if the file has an accepted extension.

    """
    return not accepted_extensions or os.path.splitext(filename.lower())[1] in accepted_extensions


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


def generate_download_file_from_text(download_text, display_name=None,
                                     header=None, msg_category='success', msg=''):
    """ Generate a download file from text output.

    Args:
        download_text (str): Text with newlines for iterating.
        display_name (str): Name to be assigned to the file in the response.
        header (str): Optional header for download file blob.
        msg_category (str): Category of the message to be displayed ('Success', 'Error', 'Warning')
        msg (str): Optional message to be displayed in the submit-flash-field.

    Returns:
        Response: A Response object containing the downloaded file.

    """
    if not display_name:
        display_name = 'download.txt'

    if not download_text:
        raise HedFileError('EmptyDownloadText', "No download text given", "")

    def generate():
        if header:
            yield header
        for issue in download_text.splitlines(True):
            yield issue

    return Response(generate(), mimetype='text/plain charset=utf-8',
                    headers={'Content-Disposition': f"attachment filename={display_name}",
                             'Category': msg_category, 'Message': msg})


def generate_download_spreadsheet(results,  msg_category='success', msg=''):
    """ Generate a download Excel file.

    Args:
        results (dict): Dictionary with the results to be downloaded.
        msg_category (str): Category of the message to be displayed ('Success', 'Error', 'Warning')
        msg (str): Optional message to be displayed in the submit-flash-field.

    Returns:
        Response: A Response object containing the downloaded file.

    """
    # return generate_download_test()
    spreadsheet = results[base_constants.SPREADSHEET]
    display_name = results[base_constants.OUTPUT_DISPLAY_NAME]

    if not spreadsheet.loaded_workbook:
        return generate_download_file_from_text(spreadsheet.to_csv(), display_name=display_name,
                                                msg_category=msg_category, msg=msg)
    buffer = io.BytesIO()
    spreadsheet.to_excel(buffer, output_processed_file=True)
    buffer.seek(0)
    response = make_response()
    response.data = buffer.read()
    response.headers['Content-Disposition'] = 'attachment; filename=' + display_name
    response.headers['Category'] = msg_category
    response.headers['Message'] = msg
    response.mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response


def generate_text_response(download_text, msg_category='success', msg=''):
    """ Generate a download response.

    Args:
        download_text (str): Text to be downloaded as part of the response.
        msg_category (str): Category of the message to be displayed ('Success', 'Error', 'Warning')
        msg (str): Optional message to be displayed in the submit-flash-field.

    Returns:
        Response: A Response object containing the downloaded file.


    """
    headers = {'Category': msg_category, 'Message': msg}
    if len(download_text) > 0:
        headers['Content-Length'] = len(download_text)
    return Response(download_text, mimetype='text/plain charset=utf-8', headers=headers)


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

        hed_file_path = hedschema.get_path_from_hed_version(request.form[base_constants.SCHEMA_VERSION])
        hed_schema = hedschema.load_schema(hed_file_path)
    elif request.form[base_constants.SCHEMA_VERSION] == \
            base_constants.OTHER_VERSION_OPTION and base_constants.SCHEMA_PATH in request.files:
        f = request.files[base_constants.SCHEMA_PATH]
        hed_schema = hedschema.from_string(f.read(file_constants.BYTE_LIMIT).decode('ascii'),
                                           file_type=secure_filename(f.filename))
    else:
        raise HedFileError("NoSchemaFile", "Must provide a valid schema for upload if other chosen", "")
    return hed_schema


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
    """ Handle an http error.

    Args:
        ex (Exception): A class that extends python Exception class.

    Returns:
        Response: A response object indicating the field_type of error.

    """
    if hasattr(ex, 'error_type'):
        error_code = ex.error_type
    else:
        error_code = type(ex).__name__
    if hasattr(ex, 'message'):
        message = ex.message
    else:
        message = str(ex)
    error_message = f"{error_code}: [{message}]"
    return generate_text_response('', msg_category='error', msg=error_message)


def package_results(results):
    """Package a results dictionary into a standard form.

    Args:
        results (dict): A dictionary with the results

    """
    msg = results.get('msg', '')
    msg_category = results.get('msg_category', 'success')
    display_name = results.get('output_display_name', '')
    if results['data']:
        return generate_download_file_from_text(results['data'], display_name=display_name,
                                                msg_category=msg_category, msg=msg)
    elif not results.get('spreadsheet', None):
        return generate_text_response("", msg=msg, msg_category=msg_category)
    else:
        return generate_download_spreadsheet(results, msg_category=msg_category, msg=msg)
