import os
import json
from werkzeug.utils import secure_filename
import pandas as pd

from hed import schema as hedschema
from hed.errors import get_printable_issue_string, HedFileError, ErrorHandler
from hed.errors.error_reporter import check_for_any_errors
from hed.models.definition_dict import DefinitionDict
from hed.models.hed_string import HedString
from hed.models.sidecar import Sidecar
from hed.models.spreadsheet_input import SpreadsheetInput
from hed.models.tabular_input import TabularInput
from hedweb.constants import base_constants as bc
from hedweb.constants import file_constants as fc
from hedweb.columns import create_column_selections, get_tag_columns
from hedweb.web_util import form_has_option, get_hed_schema_from_pull_down


def get_input_from_form(request):
    """ Get a dictionary of input from a service request.

    Parameters:
        request (Request): A Request object containing user data for the service request.

    Returns:
        dict: A dictionary containing input arguments for calling the service request.
    """

    arguments = {
        bc.COMMAND: request.form.get(bc.COMMAND_OPTION, ''),
        bc.CHECK_FOR_WARNINGS: form_has_option(request, bc.CHECK_FOR_WARNINGS, 'on'),
        bc.EXPAND_DEFS: form_has_option(request, bc.EXPAND_DEFS, 'on'),
        bc.INCLUDE_DESCRIPTION_TAGS: form_has_option(request, bc.INCLUDE_DESCRIPTION_TAGS, 'on'),
        bc.INCLUDE_SUMMARIES: form_has_option(request, bc.INCLUDE_SUMMARIES, 'on'),
        bc.SPREADSHEET_TYPE: fc.TSV_EXTENSION
    }
    value, skip = create_column_selections(request.form)
    arguments[bc.COLUMNS_SKIP] = skip
    arguments[bc.COLUMNS_VALUE] = value
    arguments[bc.TAG_COLUMNS] = get_tag_columns(request.form)
    arguments[bc.SCHEMA] = get_hed_schema_from_pull_down(request)
    if bc.SIDECAR_FILE in request.files and request.files[bc.SIDECAR_FILE]:
        f = request.files[bc.SIDECAR_FILE]
        arguments[bc.SIDECAR] = Sidecar(files=f, name=secure_filename(f.filename))
    if bc.REMODEL_FILE in request.files and request.files[bc.REMODEL_FILE]:
        f = request.files[bc.REMODEL_FILE]
        name = secure_filename(f.filename)
        arguments[bc.REMODEL_OPERATIONS] = {'name': name, 'operations': json.load(f)}
    if bc.DEFINITION_FILE in request.files and request.files[bc.DEFINITION_FILE]:
        f = request.files[bc.DEFINITION_FILE]
        sidecar = Sidecar(files=f, name=secure_filename(f.filename))
        arguments[bc.DEFINITIONS] = sidecar.get_def_dict(arguments[bc.SCHEMA], extra_def_dicts=None)
    if bc.EVENTS_FILE in request.files and request.files[bc.EVENTS_FILE]:
        f = request.files[bc.EVENTS_FILE]
        arguments[bc.EVENTS] = TabularInput(file=f, sidecar=arguments.get(bc.SIDECAR, None),
                                            name=secure_filename(f.filename))
    if bc.STRING_INPUT in request.form and request.form[bc.STRING_INPUT]:
        arguments[bc.STRING_LIST] = [HedString(request.form[bc.STRING_INPUT], arguments[bc.SCHEMA])]
    if bc.SPREADSHEET_FILE in request.files and request.files[bc.SPREADSHEET_FILE].filename:
        arguments[bc.WORKSHEET] = request.form.get(bc.WORKSHEET_NAME, None)
        filename = request.files[bc.SPREADSHEET_FILE].filename
        file_ext = os.path.splitext(filename)[1]
        if file_ext in fc.EXCEL_FILE_EXTENSIONS:
            arguments[bc.SPREADSHEET_TYPE] = fc.EXCEL_EXTENSION
            arguments[bc.SPREADSHEET] = SpreadsheetInput(file=request.files[bc.SPREADSHEET_FILE],
                                                         file_type=fc.EXCEL_EXTENSION,
                                                         worksheet_name=None,
                                                         tag_columns=['HED'],
                                                         has_column_names=True, name=filename)
    return arguments


# form_data = request.data
# form_string = form_data.decode()
# service_request = json.loads(form_string)
# arguments = ProcessServices.get_service_info(service_request)
# arguments[bc.SCHEMA] = ProcessServices.set_input_schema(service_request)
# ProcessServices.set_column_parameters(arguments, service_request)
# ProcessServices.set_remodel_parameters(arguments, service_request)
# ProcessServices.set_definitions(arguments, service_request)
# ProcessServices.set_sidecar(arguments, service_request)
# ProcessServices.set_input_objects(arguments, service_request)
# ProcessServices.set_queries(arguments, service_request)
# return arguments
