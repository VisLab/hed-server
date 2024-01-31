from hed.errors import get_printable_issue_string, HedFileError
from hed.schema.schema_compare import compare_differences
from hed import schema as hedschema
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


from hedweb.web_util import form_has_file, form_has_option, form_has_url, generate_filename, get_parsed_name
from hedweb.constants import base_constants, file_constants
from hedweb.process_base import ProcessBase
class ProcessSchemas(ProcessBase):

    def __init__(self):
        """ Construct a ProcessEvents object to handle events form requests. 

        """
        super().__init__()
        self.schema = None
        self.schema2 = None
        self.command = None
        self.check_for_warnings = False

    def set_input_from_form(self, request):
        """ Extract a dictionary of input for processing from the schemas form.

        parameters:
            request (Request): A Request object containing user data from the form.
    
        """
        self.command = request.form.get(base_constants.COMMAND_OPTION, None)
        self.check_for_warnings = form_has_option(request, base_constants.CHECK_FOR_WARNINGS, 'on')
        if form_has_option(request, base_constants.SCHEMA_UPLOAD_OPTIONS, base_constants.SCHEMA_FILE_OPTION) and \
                form_has_file(request, base_constants.SCHEMA_FILE, file_constants.SCHEMA_EXTENSIONS):
            self.schema = get_schema(request.files[base_constants.SCHEMA_FILE])
        elif form_has_option(request, base_constants.SCHEMA_UPLOAD_OPTIONS, base_constants.SCHEMA_URL_OPTION) and \
                form_has_url(request, base_constants.SCHEMA_URL, file_constants.SCHEMA_EXTENSIONS):
            self.schema = get_schema(request.values[base_constants.SCHEMA_URL])
        if form_has_option(request, base_constants.SECOND_SCHEMA_UPLOAD_OPTIONS,
                           base_constants.SECOND_SCHEMA_FILE_OPTION) and \
                form_has_file(request, base_constants.SECOND_SCHEMA_FILE, file_constants.SCHEMA_EXTENSIONS):
            self.schema2 = get_schema(request.files[base_constants.SECOND_SCHEMA_FILE])
        elif form_has_option(request, base_constants.SECOND_SCHEMA_UPLOAD_OPTIONS,
                             base_constants.SECOND_SCHEMA_URL_OPTION) and \
                form_has_url(request, base_constants.SECOND_SCHEMA_URL, file_constants.SCHEMA_EXTENSIONS):
            self.schema2 = get_schema(request.values[base_constants.SECOND_SCHEMA_URL])

    def process(self):
        """ Perform the requested action for the schema.
    
        Returns:
            dict: A dictionary of results in the standard results format.
    
        Raises:
            HedFileError:  If the command was not found or the input arguments were not valid.
    
        """
        if not self.command:
            raise HedFileError('MissingCommand', 'Command is missing', '')
        if not self.schema:
            raise HedFileError("SCHEMA_NOT_FOUND", "Must provide a source schema", "")
        if self.command == base_constants.COMMAND_VALIDATE:
            results = self.validate()
        elif self.command == base_constants.COMMAND_COMPARE_SCHEMAS:
            if not self.schema2:
                raise HedFileError("SCHEMA_NOT_FOUND", "Must provide a compare schema", "")
            results = self.compare()
        elif self.command == base_constants.COMMAND_CONVERT_SCHEMA:
            results = self.convert()
        else:
            raise HedFileError('UnknownProcessingMethod', "Select a schema processing method", "")
        return results

    def compare(self):
        data = compare_differences(self.schema, self.schema2, output='string', sections=None)
        output_name = self.schema.name + '_' + self.schema2.name + '_' + "differences.txt"
        msg_results = ''
        if not data:
            msg_results = ': no differences found'
        return {'command': base_constants.COMMAND_COMPARE_SCHEMAS,
                base_constants.COMMAND_TARGET: 'schema',
                'data': data,
                'output_display_name': output_name,
                'schema_version': self.schema.get_formatted_version(),
                'schema2_version': self.schema2.get_formatted_version(),
                'msg_category': 'success',
                'msg': 'Schemas were successfully compared' + msg_results}

    def convert(self):
        """ Return a string representation of hed_schema in the desired format as determined by the display name extension.
      
        Returns:
            dict: A dictionary of results in the standard results format.
    
        """

        if self.schema.source_format == file_constants.SCHEMA_XML_EXTENSION:
            data = self.schema.get_as_mediawiki_string()
            extension = '.mediawiki'
        else:
            data = self.schema.get_as_xml_string()
            extension = '.xml'
        file_name = self.schema.name + extension

        return {'command': base_constants.COMMAND_CONVERT_SCHEMA,
                base_constants.COMMAND_TARGET: 'schema',
                'data': data,
                'output_display_name': file_name,
                'schema_version': self.schema.get_formatted_version(),
                'msg_category': 'success',
                'msg': 'Schema was successfully converted'}

    def validate(self):
        """ Run schema compliance for HED-3G.
        
        Returns:
            dict: A dictionary of results in the standard results format.
    
        """

        issues = self.schema.check_compliance()
        if issues:
            issue_str = get_printable_issue_string(issues, f"Schema issues for {self.schema.name}:")
            file_name = self.schema.name + 'schema_issues.txt'
            return {'command': base_constants.COMMAND_VALIDATE,
                    base_constants.COMMAND_TARGET: 'schema',
                    'data': issue_str,
                    'output_display_name': file_name,
                    'schema_version': self.schema.get_formatted_version(),
                    'msg_category': 'warning',
                    'msg': 'Schema has validation issues'}
        else:
            return {'command': base_constants.COMMAND_VALIDATE,
                    base_constants.COMMAND_TARGET: 'schema',
                    'data': '',
                    'output_display_name': self.schema.name,
                    'schema_version': self.schema.get_formatted_version(),
                    'msg_category': 'success',
                    'msg': 'Schema had no validation issues'}

    @staticmethod
    def format_error(command, exception):
        issue_str = get_printable_issue_string(exception.issues, f"Schema issues for {exception.filename}:")
        file_name = generate_filename(exception.filename, name_suffix='_issues', extension='.txt')
        return {'command': command,
                base_constants.COMMAND_TARGET: 'schema',
                'data': issue_str,
                'output_display_name': file_name,
                'msg_category': 'warning',
                'msg': 'Schema had issues'
                }


def get_schema(schema_input=None, version=None, as_xml_string=None):
    """ Return a HedSchema object from the given parameters.

    Args:
        schema_input (str or FileStorage or None): Input url or file
        version (str or None): A schema version string to load, e.g. "8.2.0" or "score_1.1.0"
        as_xml_string (str or None): A schema in xml string format
    Returns:
        HedSchema: Schema

    :raises HedFileError:
        - The schema can't be loaded for some reason
    """
    if isinstance(schema_input, FileStorage):
        name, extension = get_parsed_name(secure_filename(schema_input.filename))
        hed_schema = hedschema.from_string(schema_input.read(file_constants.BYTE_LIMIT).decode('ascii'),
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
