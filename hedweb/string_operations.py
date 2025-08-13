"""
Performs operations on strings, such as validation and conversion between long and short forms.
"""

from hed.errors import ErrorHandler, get_printable_issue_string, HedFileError
from hed import schema as hedschema
from hed import get_query_handlers, search_hed_objs
from hed.validator import HedValidator
from hedweb.constants import base_constants as bc
from hedweb.base_operations import BaseOperations


class StringOperations(BaseOperations):
    """ Class to perform operations on spreadsheets."""

    def __init__(self, arguments=None):
        """ Construct a StringOperations object to handle sidecar operations.

        Parameters:
             arguments (dict): Dictionary with parameters extracted from form or service

        """
        self.command = None
        self.schema = None 
        self.string_list = None
        self.queries = None
        self.query_names = None
        self.definitions = None
        self.check_for_warnings = False
        self.request_type = None
        if arguments:
            self.set_input_from_dict(arguments)

    def process(self) -> dict:
        """ Perform the requested string processing action.
 
        Returns:
            dict: The results in standard format.

        Raises:
            HedFileError: If the command was not found or the input arguments were not valid.
            HedFileError: If the schema is not found or cannot be loaded.
            HedFileError: If the string list is empty or not provided.
    
        """
        if not self.command:
            raise HedFileError('MissingCommand', 'Command is missing', '')
        elif not self.schema or not isinstance(self.schema, hedschema.hed_schema.HedSchema):
            raise HedFileError('BadHedSchema', "Please provide a valid HedSchema", "")
        elif not self.string_list:
            raise HedFileError('EmptyHedStringList', "Please provide HED strings to be processed", "")
        if self.command == bc.COMMAND_VALIDATE:
            results = self.validate()
        elif self.command == bc.COMMAND_SEARCH:
            results = self.search()
        elif self.command == bc.COMMAND_TO_SHORT or self.command == bc.COMMAND_TO_LONG:
            results = self.convert()
        else:
            raise HedFileError('UnknownProcessingMethod', f'Command {self.command} is missing or invalid', '')
        return results

    def convert(self) -> dict:
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

    def search(self) -> dict:
        """ Return a list or a boolean

        Returns:
            dict: A dictionary pointing to results or errors.

        Notes:  The options for this are
            columns_included (list):  A list of column names of columns to include.
            expand_defs (bool): If True, expand the definitions in the assembled HED. Otherwise, shrink definitions.

        """
        if not self.queries:
            raise HedFileError('EmptyQueries', 'Please provide a query to search', '')
        queries, query_names, issues = get_query_handlers(self.queries, self.query_names)
        if issues:
            return {bc.COMMAND: bc.COMMAND_VALIDATE,
                    bc.COMMAND_TARGET: 'strings', 
                    'data': get_printable_issue_string(issues, f"Query errors"),
                    bc.SCHEMA_VERSION: self.schema.get_formatted_version(),
                    'msg_category': 'warning',
                    'msg': 'Strings had validation issues'}
        self.check_for_warnings = False
        results = self.validate()
        if results['data']:
            return results
        df_factors = search_hed_objs(self.string_list, queries, query_names=query_names)
        
        if self.request_type == "from_form" and df_factors.iat[0, 0]:
            data = "String satisfies the query"
        elif self.request_type == "from_form":
            data = "String does not satisfy query"
        else:
            numpy_array = df_factors.to_numpy()
            data = numpy_array.tolist()
        return {bc.COMMAND: bc.COMMAND_SEARCH,
                bc.COMMAND_TARGET: 'events',
                'data': data,
                'schema_version': self.schema.get_formatted_version(),
                'query_names': self.query_names,
                'queries': self.queries,
                'string_list': [str(hed) for hed in self.string_list],
                bc.MSG_CATEGORY: 'success',
                bc.MSG: f"Successfully made queries"}

    def validate(self) -> dict:
        """ Validate a list of strings and returns a dictionary containing the issues or a no issues message.

        Returns:
            dict: The results in standard form.
        """
    
        validation_issues = []
        error_handler = ErrorHandler(check_for_warnings=self.check_for_warnings)
        validator = HedValidator(self.schema, self.definitions)
        for pos, h_string in enumerate(self.string_list):
            issues = validator.validate(h_string, True, error_handler=error_handler)
            if issues:
                validation_issues.append(get_printable_issue_string(issues, f"Errors for HED string {pos}:"))
        if validation_issues:
            return {bc.COMMAND: bc.COMMAND_VALIDATE,
                    bc.COMMAND_TARGET: 'strings', 'data': '\n'.join(validation_issues),
                    bc.SCHEMA_VERSION: self.schema.get_formatted_version(),
                    'msg_category': 'warning',
                    'msg': 'Strings had validation issues'}
        else:
            return {bc.COMMAND: bc.COMMAND_VALIDATE,
                    bc.COMMAND_TARGET: 'strings', 'data': '',
                    bc.SCHEMA_VERSION: self.schema.get_formatted_version(),
                    'msg_category': 'success',
                    'msg': 'Strings validated successfully...'}
