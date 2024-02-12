from hed.errors import ErrorHandler, get_printable_issue_string, HedFileError
from hed import schema as hedschema
from hed.validator import HedValidator

from hedweb.constants import base_constants as bc
from hedweb.base_operations import BaseOperations


class StringOperations(BaseOperations):

    def __init__(self, arguments=None):
        """ Construct a StringOperations object to handle sidecar operations.

        Parameters:
             arguments (dict): Dictionary with parameters extracted from form or service

        """
        self.command = None
        self.schema = None 
        self.string_list = None
        self.definitions = None
        self.check_for_warnings = False
        if arguments:
            self.set_input_from_dict(arguments)

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
        if self.command == bc.COMMAND_VALIDATE:
            results = self.validate()
        elif self.command == bc.COMMAND_TO_SHORT or self.command == bc.COMMAND_TO_LONG:
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
            if self.command == bc.COMMAND_TO_LONG:
                converted_string = hed_string_obj.get_as_form('long_tag')
            else:
                converted_string = hed_string_obj.get_as_form('short_tag')
            strings.append(converted_string)
    
            return {bc.COMMAND: self.command,
                    bc.COMMAND_TARGET: 'strings', 'data': strings,
                    bc.SCHEMA_VERSION: self.schema.get_formatted_version(),
                    'msg_category': 'success',
                    'msg': 'Strings converted successfully'}   
    
    def validate(self):
        """ Validate a list of strings and returns a dictionary containing the issues or a no issues message.

        Returns:
            dict: The results in standard form.
        """
    
        validation_issues = []
        error_handler = ErrorHandler(check_for_warnings=self.check_for_warnings)
        validator = HedValidator(self.schema, self.definitions)
        for pos, h_string in enumerate(self.string_list, start=1):
            issues = validator.validate(h_string, True, error_handler=error_handler)
            if issues:
                validation_issues.append(get_printable_issue_string(issues, f"Errors for HED string {pos}:"))
        if validation_issues:
            return {bc.COMMAND: bc.COMMAND_VALIDATE,
                    bc.COMMAND_TARGET: 'strings', 'data': validation_issues,
                    bc.SCHEMA_VERSION: self.schema.get_formatted_version(),
                    'msg_category': 'warning',
                    'msg': 'Strings had validation issues'}
        else:
            return {bc.COMMAND: bc.COMMAND_VALIDATE,
                    bc.COMMAND_TARGET: 'strings', 'data': '',
                    bc.SCHEMA_VERSION: self.schema.get_formatted_version(),
                    'msg_category': 'success',
                    'msg': 'Strings validated successfully...'}
