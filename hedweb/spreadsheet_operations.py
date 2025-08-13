"""
Performs operations on spreadsheets, such as validation, conversion, and extraction.
"""
import os
from werkzeug.utils import secure_filename
from hed import schema as hedschema
from hed.errors import get_printable_issue_string, HedFileError, ErrorHandler
from hed.models.spreadsheet_input import SpreadsheetInput
from hedweb.web_util import get_schema_versions
from hedweb.constants import base_constants as bc
from hedweb.constants import file_constants as fc
from hedweb.base_operations import BaseOperations
from hedweb.web_util import filter_issues, generate_filename


class SpreadsheetOperations(BaseOperations):
    """ Class to perform operations on spreadsheets."""

    def __init__(self, arguments=None):
        """ Construct a ProcessSpreadsheet object to handle spreadsheet operations.

        Parameters:
             arguments (dict): Dictionary with parameters extracted from form or service

        """
        self.command = None
        self.schema = None
        self.definitions = None
        self.spreadsheet = None
        self.worksheet = None
        self.spreadsheet_type = fc.TSV_EXTENSION
        self.tag_columns = []
        self.has_column_names = True
        self.check_for_warnings = False
        self.expand_defs = False
        if arguments:
            self.set_input_from_dict(arguments)

    def process(self) -> dict:
        """ Perform the requested action for the spreadsheet.
 
        Returns:
            dict: A dictionary of results from spreadsheet processing in standard form.

        Raises:
            HedFileError: If the command was not found or the input arguments were not valid.
            HedFileError: If the schema is not found or cannot be loaded.
            HedFileError: If the spreadsheet is not found or cannot be loaded.
        """
    
        if not self.schema or not isinstance(self.schema, hedschema.hed_schema.HedSchema):
            raise HedFileError('BadHedSchema', "Please provide a valid HedSchema", "")
        if not self.spreadsheet or not isinstance(self.spreadsheet, SpreadsheetInput):
            raise HedFileError('InvalidSpreadsheet', "A spreadsheet was given but could not be processed", "")
        if self.command == bc.COMMAND_VALIDATE:
            results = self.spreadsheet_validate()
        elif self.command == bc.COMMAND_TO_SHORT or self.command == bc.COMMAND_TO_LONG:
            results = self.spreadsheet_convert()
        else:
            raise HedFileError('UnknownSpreadsheetProcessingMethod',
                               f"Command {self.command} is missing or invalid", "")
        return results
    
    def spreadsheet_convert(self) -> dict:
        """ Convert a spreadsheet long to short unless the command is not COMMAND_TO_LONG then converts to short
    
        Returns:
            dict: A downloadable dictionary in standard format.
    
        Notes: the allowed options are
            command (str): Name of the command to execute.
            check_for_warnings (bool): If True, check for warnings.
    
        """
    
        self.check_for_warnings = False
        results = self.spreadsheet_validate()
        if results['data']:
            return results
        display_name = self.spreadsheet.name
        display_ext = os.path.splitext(secure_filename(display_name))[1]
        if self.command == bc.COMMAND_TO_LONG:
            suffix = '_to_long'
            self.spreadsheet.convert_to_long(self.schema)
        else:
            suffix = '_to_short'
            self.spreadsheet.convert_to_short(self.schema)
    
        file_name = generate_filename(display_name, name_suffix=suffix, extension=display_ext, append_datetime=True)
        return {bc.COMMAND: self.command,
                bc.COMMAND_TARGET: 'spreadsheet', 'data': '',
                bc.SPREADSHEET: self.spreadsheet, 'output_display_name': file_name,
                bc.SCHEMA_VERSION: get_schema_versions(self.schema),
                bc.MSG_CATEGORY: 'success',
                bc.MSG: f'Spreadsheet {display_name} converted successfully'}
    
    def spreadsheet_validate(self) -> dict:
        """ Validates the spreadsheet.
 
        Returns:
            dict: A dictionary containing results of validation in standard format.
    
        Notes: The allowed options are
            check_for_warnings (bool): Indicates whether validation should check for warnings as well as errors.
    
        """
        
        error_handler = ErrorHandler(check_for_warnings=self.check_for_warnings)
        display_name = self.spreadsheet.name
        issues = self.spreadsheet.validate(self.schema, extra_def_dicts=self.definitions,
                                           error_handler=error_handler, name=display_name)
        issues = filter_issues(issues, self.check_for_warnings)
        if issues:
            data = get_printable_issue_string(issues, f"Spreadsheet {display_name} validation issues")
            file_name = generate_filename(display_name, name_suffix='_validation_issues',
                                          extension='.txt', append_datetime=True)
            category = "warning"
            msg = f"Spreadsheet {file_name} had validation issues"
        else:
            data = ''
            file_name = display_name
            category = 'success'
            msg = f'Spreadsheet {display_name} had no validation issues'
    
        return {bc.COMMAND: bc.COMMAND_VALIDATE,
                bc.COMMAND_TARGET: 'spreadsheet', 'data': data,
                bc.SPREADSHEET: '',
                bc.SCHEMA_VERSION: get_schema_versions(self.schema),
                "output_display_name": file_name,
                bc.MSG_CATEGORY: category, bc.MSG: msg}
