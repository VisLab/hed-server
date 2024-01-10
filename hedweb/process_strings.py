from werkzeug.utils import secure_filename
from hed.errors import ErrorHandler, get_printable_issue_string, HedFileError
from hed.models.sidecar import Sidecar
from hed.models.hed_string import HedString
from hed import schema as hedschema
from hedweb.constants import base_constants
from hedweb.web_util import form_has_option, get_hed_schema_from_pull_down
from hedweb.process_base import ProcessBase


class ProcessStrings(ProcessBase):

    def __init__(self):
        """ Construct a ProcessStrings object to handle strings form requests. 

        """
        self.command = None
        self.schema = None 
        self.string_list = None
        self.definitions = None
        self.check_for_warnings = False

    def set_input_from_dict(self, input_dict):
        """ Extract a dictionary of input for processing from the schema form.

        Args:
            input_dict (dict): A dict object containing user data from a JSON service request.

        Returns:
            dict: A dictionary of schema processing parameters in standard form.

        """
        self.command = input_dict.get(base_constants.COMMAND, '')
        self.schema = input_dict.get(base_constants.SCHEMA, None)
        self.string_list = input_dict.get(base_constants.STRING_LIST, '')
        self.definitions = input_dict.get(base_constants.DEFINITIONS, None)
        self.check_for_warnings = input_dict.get(base_constants.CHECK_FOR_WARNINGS, False)
        
    def set_input_from_form(self, request):
        """ Extract a dictionary of input for processing from the events form.

        parameters:
            request (Request): A Request object containing user data from the form.

        """
        self.command = request.form.get(base_constants.COMMAND_OPTION, None)
        self.schema = get_hed_schema_from_pull_down(request)
        hed_string = request.form.get(base_constants.STRING_INPUT, None)
        if hed_string:
            self.string_list = [HedString(hed_string, self.schema)]
        if base_constants.DEFINITION_FILE in request.files:
            f = request.files[base_constants.DEFINITION_FILE]
            sidecar = Sidecar(files=f, name=secure_filename(f.filename))
            self.definitions = sidecar.get_def_dict(self.schema, extra_def_dicts=None)
        self.check_for_warnings = form_has_option(request, base_constants.CHECK_FOR_WARNINGS, 'on')
      
    def process(self):
        """ Perform the requested string processing action.
 
        Returns:
            dict: The results in standard format.
    
        """
        if not self.command:
            raise HedFileError('MissingCommand', 'Command is missing', '')
        elif not self.schema or not isinstance(self.schema, hedschema.hed_schema.HedSchema):
            raise HedFileError('BadHedSchema', "Please provide a valid HedSchema", "")
        elif not self.string_list:
            raise HedFileError('EmptyHedStringList', "Please provide HED strings to be processed", "")
        if self.command == base_constants.COMMAND_VALIDATE:
            results = self.validate()
        elif self.command == base_constants.COMMAND_TO_SHORT or self.command == base_constants.COMMAND_TO_LONG:
            results = self.convert()
        else:
            raise HedFileError('UnknownProcessingMethod', f'Command {self.command} is missing or invalid', '')
        return results
    
    def convert(self):
        """ Convert a list of strings from long to short or  from short to long.
    
        Returns:
            dict: The results of string processing in standard format.
    
        """
    
        results = self.validate()
        if results['data']:
            return results
        strings = []
        for pos, hed_string_obj in enumerate(self.string_list, start=1):
            if self.command == base_constants.COMMAND_TO_LONG:
                converted_string = hed_string_obj.get_as_form('long_tag')
            else:
                converted_string = hed_string_obj.get_as_form('short_tag')
            strings.append(converted_string)
    
            return {base_constants.COMMAND: self.command,
                    base_constants.COMMAND_TARGET: 'strings', 'data': strings,
                    base_constants.SCHEMA_VERSION: self.schema.get_formatted_version(),
                    'msg_category': 'success',
                    'msg': 'Strings converted successfully'}   
    
    def validate(self):
        """ Validate a list of strings and returns a dictionary containing the issues or a no issues message.

        Returns:
            dict: The results in standard form.
        """
    
        validation_issues = []
        error_handler = ErrorHandler(check_for_warnings=self.check_for_warnings)
        for pos, h_string in enumerate(self.string_list, start=1):
            issues = h_string.validate(self.schema, error_handler=error_handler)
            if issues:
                validation_issues.append(get_printable_issue_string(issues, f"Errors for HED string {pos}:"))
        if validation_issues:
            return {base_constants.COMMAND: base_constants.COMMAND_VALIDATE,
                    base_constants.COMMAND_TARGET: 'strings', 'data': validation_issues,
                    base_constants.SCHEMA_VERSION: self.schema.get_formatted_version(),
                    'msg_category': 'warning',
                    'msg': 'Strings had validation issues'}
        else:
            return {base_constants.COMMAND: base_constants.COMMAND_VALIDATE,
                    base_constants.COMMAND_TARGET: 'strings', 'data': '',
                    base_constants.SCHEMA_VERSION: self.schema.get_formatted_version(),
                    'msg_category': 'success',
                    'msg': 'Strings validated successfully...'}
