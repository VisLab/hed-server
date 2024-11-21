import os
import json
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from hed.schema import load_schema_version, from_string
from hed import HedSchema

from hed import schema as hedschema
from hed.errors import HedFileError
from hed.models.hed_string import HedString
from hed.models.sidecar import Sidecar
from hed.models.spreadsheet_input import SpreadsheetInput
from hed.models.tabular_input import TabularInput
from hedweb.constants import base_constants as bc
from hedweb.constants import file_constants as fc
from hedweb.columns import create_column_selections, get_tag_columns
from hedweb.web_util import form_has_file, form_has_option, form_has_url, get_parsed_name


class ProcessForm:
    @staticmethod
    def get_input_from_form(request):
        """ Get a dictionary of input from a service request.

        Parameters:
            request (Request): A Request object containing user data for the service request.

        Returns:
            dict: A dictionary containing input arguments for calling the service request.
        """

        arguments = {
            bc.REQUEST_TYPE: bc.FROM_FORM,
            bc.COMMAND: request.form.get(bc.COMMAND_OPTION, ''),
            bc.APPEND_ASSEMBLED: form_has_option(request.form, bc.APPEND_ASSEMBLED, 'on'),
            bc.CHECK_FOR_WARNINGS: form_has_option(request.form, bc.CHECK_FOR_WARNINGS, 'on'),
            bc.EXPAND_DEFS: form_has_option(request.form, bc.EXPAND_DEFS, 'on'),
            bc.INCLUDE_CONTEXT: form_has_option(request.form, bc.INCLUDE_CONTEXT, 'on'),
            bc.INCLUDE_DESCRIPTION_TAGS: form_has_option(request.form, bc.INCLUDE_DESCRIPTION_TAGS, 'on'),
            bc.INCLUDE_SUMMARIES: form_has_option(request.form, bc.INCLUDE_SUMMARIES, 'on'),
            bc.REMOVE_TYPES_ON: form_has_option(request.form, bc.REMOVE_TYPES_ON, 'on'),
            bc.REPLACE_DEFS: form_has_option(request.form, bc.REPLACE_DEFS, 'on'),
            bc.SPREADSHEET_TYPE: fc.TSV_EXTENSION
        }
        value, skip = create_column_selections(request.form)
        arguments[bc.COLUMNS_SKIP] = skip
        arguments[bc.COLUMNS_VALUE] = value
        arguments[bc.TAG_COLUMNS] = get_tag_columns(request.form)
        ProcessForm.set_schema_from_request(arguments, request)
        ProcessForm.set_json_files(arguments, request)
        ProcessForm.set_queries(arguments, request)
        ProcessForm.set_input_objects(arguments, request)
        return arguments

    @staticmethod
    def set_input_objects(arguments, request):
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
                                                             worksheet_name=arguments[bc.WORKSHEET],
                                                             tag_columns=arguments[bc.TAG_COLUMNS],
                                                             has_column_names=True, name=filename)

    @staticmethod
    def set_json_files(arguments, request):
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

    @staticmethod
    def set_queries(arguments, request):
        """ Update arguments with lists of string queries
        
        Parameters:
            arguments (dict):  A dictionary with the extracted parameters that are to be processed.
            request (Request): A Request object containing form data.
        """
        arguments[bc.QUERY_NAMES] = None
        if bc.QUERY_INPUT in request.form and request.form[bc.QUERY_INPUT]:
            arguments[bc.QUERIES] = [request.form[bc.QUERY_INPUT]]
        else:
            arguments[bc.QUERIES] = None

    @staticmethod
    def set_schema_from_request(arguments, request):
        """ Create a HedSchema object from form pull-down box.

        Parameters:
            arguments (dict):   Dictionary of parameters to which the schema will be added.
            request (Request): A Request object containing form data.

        Returns:
            HedSchema: The HED schema to use.
        """

        if form_has_option(request.form, bc.SCHEMA_VERSION) and \
                request.form[bc.SCHEMA_VERSION] != bc.OTHER_VERSION_OPTION:
            arguments[bc.SCHEMA] = load_schema_version(request.form[bc.SCHEMA_VERSION])
        elif form_has_option(request.form, bc.SCHEMA_VERSION) and form_has_file(request.files, bc.SCHEMA_PATH):
            f = request.files[bc.SCHEMA_PATH]
            arguments[bc.SCHEMA] = \
                from_string(f.read(fc.BYTE_LIMIT).decode('utf-8'), schema_format=secure_filename(f.filename))
        if form_has_option(request.form, bc.SCHEMA_UPLOAD_OPTIONS, bc.SCHEMA_FILE_OPTION) and \
                form_has_file(request.files, bc.SCHEMA_FILE, fc.SCHEMA_EXTENSIONS):
            arguments[bc.SCHEMA] = ProcessForm.get_schema(request.files[bc.SCHEMA_FILE])
        elif form_has_option(request.form, bc.SCHEMA_UPLOAD_OPTIONS, bc.SCHEMA_URL_OPTION) and \
                form_has_url(request.form, bc.SCHEMA_URL, fc.SCHEMA_EXTENSIONS):
            arguments[bc.SCHEMA] = ProcessForm.get_schema(request.values[bc.SCHEMA_URL])
        if form_has_option(request.form, bc.SECOND_SCHEMA_UPLOAD_OPTIONS, bc.SECOND_SCHEMA_FILE_OPTION) and \
                form_has_file(request.files, bc.SECOND_SCHEMA_FILE, fc.SCHEMA_EXTENSIONS):
            arguments[bc.SCHEMA2] = ProcessForm.get_schema(request.files[bc.SECOND_SCHEMA_FILE])
        elif form_has_option(request.form, bc.SECOND_SCHEMA_UPLOAD_OPTIONS, bc.SECOND_SCHEMA_URL_OPTION) and \
                form_has_url(request.form, bc.SECOND_SCHEMA_URL, fc.SCHEMA_EXTENSIONS):
            arguments[bc.SCHEMA2] = ProcessForm.get_schema(request.values[bc.SECOND_SCHEMA_URL])

    @staticmethod
    def get_schema(schema_input=None, version=None, as_xml_string=None):
        """ Return a HedSchema object from the given parameters.

        Parameters:
            schema_input (str or FileStorage or None): Input url or file.
            version (str or None): A schema version string to load, e.g. "8.2.0" or "score_1.1.0".
            as_xml_string (str or None): A schema in xml string format.

        Returns:
            HedSchema: Schema

        :raises HedFileError:
            - The schema can't be loaded for some reason.
        """
        if isinstance(schema_input, FileStorage):
            name, extension = get_parsed_name(secure_filename(schema_input.filename))
            hed_schema = hedschema.from_string(schema_input.read(fc.BYTE_LIMIT).decode('utf-8'),
                                               schema_format=extension,
                                               name=name)
        elif isinstance(schema_input, str):
            name, extension = get_parsed_name(schema_input, is_url=True)
            hed_schema = hedschema.load_schema(schema_input, name=name)
        elif isinstance(version, str):
            return hedschema.load_schema_version(version)
        elif isinstance(as_xml_string, str):
            return hedschema.from_string(as_xml_string, schema_format=".xml")
        else:
            raise HedFileError("SCHEMA_NOT_FOUND", "Must provide a loadable schema", "")

        return hed_schema
