from hed.errors import get_printable_issue_string, HedFileError
from hed.schema.schema_compare import compare_differences
from hedweb.web_util import form_has_file, form_has_option, form_has_url, generate_filename, get_schema
from hedweb.constants import base_constants, file_constants
from hedweb.process_base import ProcessBase

class ProcessSchemas(ProcessBase):

    def __init__(self):
        """ Construct a ProcessEvents object to handle events form requests. 

        """
        self.schema = None
        self.schema2 = None
        self.command = None
        self.check_for_warnings = False

    def set_input_from_dict(self, input_dict):
        """ Extract a dictionary of input for processing from a JSON service request.

        parameters:
            input_dict (dict): A dict object containing user data from a JSON service request.

        Returns:
            dict: A dictionary of schema processing parameters in standard form.

        """
        self.schema = input_dict.get(base_constants.SCHEMA, None)
        self.schema2 = input_dict.get(base_constants.SCHEMA2, None)
        self.command = input_dict.get(base_constants.COMMAND, '')
        self.check_for_warnings = input_dict.get(base_constants.CHECK_FOR_WARNINGS, False)

    def set_input_from_form(self, request):
        """ Extract a dictionary of input for processing from the schemas form.

        parameters:
            request (Request): A Request object containing user data from the form.
    
        """

        self.command = request.form.get(base_constants.COMMAND_OPTION, None)
        self.check_for_warnings = form_has_option(request, base_constants.CHECK_FOR_WARNINGS, 'on')
        if form_has_option(request, base_constants.SCHEMA_UPLOAD_OPTIONS, base_constants.SCHEMA_FILE_OPTION) and \
                form_has_file(request, base_constants.SCHEMA_FILE, file_constants.SCHEMA_EXTENSIONS):
            self.schema = get_schema(request.files[base_constants.SCHEMA_FILE], input_type='file')
        elif form_has_option(request, base_constants.SCHEMA_UPLOAD_OPTIONS, base_constants.SCHEMA_URL_OPTION) and \
                form_has_url(request, base_constants.SCHEMA_URL, file_constants.SCHEMA_EXTENSIONS):
            self.schema = get_schema(request.values[base_constants.SCHEMA_URL], input_type='url')
        if form_has_option(request, base_constants.SECOND_SCHEMA_UPLOAD_OPTIONS,
                           base_constants.SECOND_SCHEMA_FILE_OPTION) and \
                form_has_file(request, base_constants.SECOND_SCHEMA_FILE, file_constants.SCHEMA_EXTENSIONS):
            self.schema2 = get_schema(request.files[base_constants.SECOND_SCHEMA_FILE], input_type='file')
        elif form_has_option(request, base_constants.SECOND_SCHEMA_UPLOAD_OPTIONS,
                             base_constants.SECOND_SCHEMA_URL_OPTION) and \
                form_has_url(request, base_constants.SECOND_SCHEMA_URL, file_constants.SCHEMA_EXTENSIONS):
            self.schema2 = get_schema(request.values[base_constants.SECOND_SCHEMA_URL], input_type='url')


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
        elif self.schema["issues"]:
            return self.format_error(self.command, self.schema["issues"], self.schema["name"] + "_schema_errors")
        if self.command == base_constants.COMMAND_VALIDATE:
            results = self.validate()
        elif self.command == base_constants.COMMAND_COMPARE_SCHEMAS:
            if not self.schema2:
                raise HedFileError("SCHEMA_NOT_FOUND", "Must provide a compare schema", "")
            if self.schema2["issues"]:
                return self.format_error(self.command, self.schema2["issues"], self.schema2["name"] + "_schema2_errors")
            results = self.compare()
        elif self.command == base_constants.COMMAND_CONVERT_SCHEMA:
            results = self.convert()
        else:
            raise HedFileError('UnknownProcessingMethod', "Select a schema processing method", "")
        return results

    def compare(self):
        data = compare_differences(self.schema["schema"], self.schema2["schema"], output='string', sections=None)
        output_name = self.schema["name"] + '_' + self.schema2["name"] + '_' + "differences.txt"
        msg_results = ''
        if not data:
            msg_results = ': no differences found'
        return {'command': base_constants.COMMAND_COMPARE_SCHEMAS,
                base_constants.COMMAND_TARGET: 'schema',
                'data': data, 'output_display_name': output_name,
                'schema_version': self.schema["schema"].get_formatted_version(),
                'schema2_version': self.schema2["schema"].get_formatted_version(),
                'msg_category': 'success',
                'msg': 'Schemas were successfully compared' + msg_results}

    def convert(self):
        """ Return a string representation of hed_schema in the desired format as determined by the display name extension.
      
        Returns:
            dict: A dictionary of results in the standard results format.
    
        """

        if self.schema["type"] == file_constants.SCHEMA_XML_EXTENSION:
            data = self.schema["schema"].get_as_mediawiki_string()
            extension = '.mediawiki'
        else:
            data = self.schema["schema"].get_as_xml_string()
            extension = '.xml'
        file_name = self.schema["name"] + extension

        return {'command': base_constants.COMMAND_CONVERT_SCHEMA,
                base_constants.COMMAND_TARGET: 'schema',
                'data': data, 'output_display_name': file_name,
                'schema_version': self.schema["schema"].get_formatted_version(),
                'msg_category': 'success',
                'msg': 'Schema was successfully converted'}

    def validate(self):
        """ Run schema compliance for HED-3G.
        
        Returns:
            dict: A dictionary of results in the standard results format.
    
        """

        issues = self.schema["schema"].check_compliance()
        if issues:
            issue_str = get_printable_issue_string(issues, f"Schema issues for {self.schema['name']}:")
            file_name = self.schema["name"] + 'schema_issues.txt'
            return {'command': base_constants.COMMAND_VALIDATE,
                    base_constants.COMMAND_TARGET: 'schema',
                    'data': issue_str, 'output_display_name': file_name,
                    'schema_version': self.schema["schema"].get_formatted_version(),
                    'msg_category': 'warning',
                    'msg': 'Schema has validation issues'}
        else:
            return {'command': base_constants.COMMAND_VALIDATE,
                    base_constants.COMMAND_TARGET: 'schema',
                    'data': '', 'output_display_name': self.schema["name"],
                    'schema_version': self.schema["schema"].get_formatted_version(),
                    'msg_category': 'success',
                    'msg': 'Schema had no validation issues'}

    @staticmethod
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

    @staticmethod
    def format_error(command, issues, display_name):
        issue_str = get_printable_issue_string(issues, f"Schema issues for {display_name}:")
        file_name = generate_filename(display_name, name_suffix='schema_issues', extension='.txt')
        return {'command': command,
                base_constants.COMMAND_TARGET: 'schema',
                'data': issue_str, 'output_display_name': file_name,
                'msg_category': 'warning',
                'msg': 'Schema had issues'
                }
