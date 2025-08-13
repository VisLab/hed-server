"""
Performs operations on HED schemas, such as validation, comparison, and conversion.
"""
import os
import io
import tempfile
import zipfile
import base64
from hedweb.web_util import get_exception_message
from hed.scripts.script_util import validate_schema_object


from hed.errors import get_printable_issue_string, HedFileError
from hed.schema.schema_comparer import SchemaComparer
from hed import schema as hedschema
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from hedweb.web_util import generate_filename, get_parsed_name
from hedweb.constants import base_constants as bc
from hedweb.constants import file_constants as fc
from hedweb.base_operations import BaseOperations


class SchemaOperations(BaseOperations):
    """ Class to perform operations on HED schemas."""

    def __init__(self, arguments=None):
        """ Construct a SchemaOperations object to handle sidecar operations.

        Parameters:
             arguments (dict): Dictionary with parameters extracted from form or service

        """
        super().__init__()
        self.schema = None
        self.schema2 = None
        self.command = None
        self.check_for_warnings = False
        if arguments:
            self.set_input_from_dict(arguments)

    def process(self) -> dict:
        """ Perform the requested action for the schema.
    
        Returns:
            dict: A dictionary of results in the standard results format.
    
        Raises:
            HedFileError:  If the command was not found or the input arguments were not valid.
            HedFileError: If the schema is not found or cannot be loaded.
    
        """
        if not self.command:
            raise HedFileError('MissingCommand', 'Command is missing', '')
        if not self.schema:
            raise HedFileError("SCHEMA_NOT_FOUND", "Must provide a source schema", "")
        if self.command == bc.COMMAND_VALIDATE:
            results = self.validate()
        elif self.command == bc.COMMAND_COMPARE_SCHEMAS:
            if not self.schema2:
                raise HedFileError("SCHEMA_NOT_FOUND", "Must provide a compare schema", "")
            results = self.compare()
        elif self.command == bc.COMMAND_CONVERT_SCHEMA:
            results = self.convert()
        else:
            raise HedFileError('UnknownProcessingMethod', "Select a schema processing method", "")
        return results

    def compare(self):
        """ Compare two schemas and return the differences.
        Returns:
            dict: A dictionary of results in the standard results format.
        """

        comp = SchemaComparer(self.schema, self.schema2)
        data = comp.compare_differences()
        output_name = self.schema.name + '_' + self.schema2.name + '_' + "differences.txt"
        msg_results = ''
        if not data:
            msg_results = ': no differences found'
        return {'command': bc.COMMAND_COMPARE_SCHEMAS,
                bc.COMMAND_TARGET: 'schema',
                'data': data,
                'output_display_name': output_name,
                'schema_version': self.schema.get_formatted_version(),
                'schema2_version': self.schema2.get_formatted_version(),
                'msg_category': 'success',
                'msg': 'Schemas were successfully compared' + msg_results}

    def convert(self) -> dict:
        """Convert schema to multiple formats, save to temp dir, zip, and return as base64-encoded data.

        Returns:
            dict: A dictionary of results in the standard results format.
        """

        schema_name = self.schema.name
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = os.path.join(tmpdir, f"{schema_name}_converted")
            os.makedirs(base_dir, exist_ok=True)
            # Write all the formats to the temp directory.
            self.schema.save_as_xml(os.path.join(base_dir, schema_name + '.xml'))
            self.schema.save_as_mediawiki(os.path.join(base_dir, schema_name + '.mediawiki'))
            self.schema.save_as_dataframes(os.path.join(base_dir, 'hedtsv', schema_name,  schema_name + '.tsv'))

            # Create zip archive in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(base_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, os.path.dirname(base_dir))
                        zipf.write(full_path, arcname)

            zip_buffer.seek(0)
            zip_bytes = zip_buffer.read()
            encoded_zip = base64.b64encode(zip_bytes).decode('utf-8')
            zip_file_name = f"{schema_name}_converted.zip"

            return {
                'command': 'convert_schema',
                'command_target': 'schema',
                'data': encoded_zip,
                'output_display_name': zip_file_name,
                'schema_version': schema_name,
                'msg_category': 'success',
                'msg': 'Schema was successfully converted'
            }

    def validate(self) -> dict:
        """ Run schema compliance for HED-3G.
        
        Returns:
            dict: A dictionary of results in the standard results format.
    
        """

        issues = validate_schema_object(self.schema, self.schema.name)
        if issues:
            issue_str = get_printable_issue_string(issues, f"Schema issues for {self.schema.name}:")
            file_name = self.schema.name + '_schema_issues.txt'
            return {'command': bc.COMMAND_VALIDATE,
                    bc.COMMAND_TARGET: 'schema',
                    'data': issue_str,
                    'output_display_name': file_name,
                    'schema_version': self.schema.get_formatted_version(),
                    'msg_category': 'warning',
                    'msg': 'Schema has validation issues'}
        else:
            return {'command': bc.COMMAND_VALIDATE,
                    bc.COMMAND_TARGET: 'schema',
                    'data': '',
                    'output_display_name': self.schema.name,
                    'schema_version': self.schema.get_formatted_version(),
                    'msg_category': 'success',
                    'msg': 'Schema had no validation issues'}

    @staticmethod
    def format_error(command, exception) -> dict:
        """ Format an error for a schema command.

        Parameters:
            command (str): The command that caused the error.
            exception (HedFileError): The exception that was raised.

        Returns:
            dict: A dictionary of results in the standard results format.
        """
        if isinstance(exception, HedFileError) and len(exception.issues) >= 1:
            issue_str = get_printable_issue_string(exception.issues, f"Schema issues for {exception.filename}:")
            file_name = generate_filename(exception.filename, name_suffix='_issues', extension='.txt')
        else:
            issue_str = get_exception_message(exception)
            file_name = 'unknown'
        return {'command': command,
                bc.COMMAND_TARGET: 'schema',
                'data': issue_str,
                'output_display_name': file_name,
                'msg_category': 'warning',
                'msg': 'Schema had issues'
                }


def get_schema(schema_input=None, version=None, as_xml_string=None) -> hedschema.HedSchema:
    """ Return a HedSchema object from the given parameters.

    Parameters:
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
