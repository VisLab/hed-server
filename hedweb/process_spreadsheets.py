import os
from flask import current_app
from werkzeug.utils import secure_filename
from hed import schema as hedschema
from hed.errors import get_printable_issue_string, HedFileError, ErrorHandler
from hed.models.spreadsheet_input import SpreadsheetInput
from hedweb.web_util import get_schema_versions
from hedweb.constants import base_constants, file_constants
from hedweb.process_base import ProcessBase
from hedweb.columns import get_column_names
from hedweb.web_util import filter_issues, form_has_option, generate_filename, get_hed_schema_from_pull_down


class ProcessSpreadsheets(ProcessBase):

    def __init__(self):
        """ Construct a ProcessSpreadsheets object to handle spreadsheet form requests. 

        """
        self.command = None
        self.schema = None
        self.spreadsheet = None
        self.worksheet = None
        self.spreadsheet_type = file_constants.TSV_EXTENSION
        self.prefix_dict = {}
        self.tag_columns = []
        self.has_column_names = True
        self.check_for_warnings = False
        self.expand_defs = False

    def set_input_from_form(self, request):
        """ Set input for processing from a spreadsheets form.

        parameters:
            request (Request): A Request object containing user data from the form.

        """
        self.schema = get_hed_schema_from_pull_down(request)
        self.worksheet = request.form.get(base_constants.WORKSHEET_NAME, None)
        self.command = request.form.get(base_constants.COMMAND_OPTION, '')
        self.check_for_warnings = form_has_option(request, base_constants.CHECK_FOR_WARNINGS, 'on')
        self.tag_columns = get_column_names(request.form)
        filename = request.files[base_constants.SPREADSHEET_FILE].filename
        file_ext = os.path.splitext(filename)[1]
        if file_ext in file_constants.EXCEL_FILE_EXTENSIONS:
            self.spreadsheet_type = file_constants.EXCEL_EXTENSION
        self.spreadsheet = SpreadsheetInput(file=request.files[base_constants.SPREADSHEET_FILE],
                                            file_type=self.spreadsheet_type,
                                            worksheet_name=self.worksheet,
                                            tag_columns=self.tag_columns,
                                            name=filename)

    def process(self):
        """ Perform the requested action for the spreadsheet.
 
        Returns:
            dict: A dictionary of results from spreadsheet processing in standard form.
    
        """
    
        if not self.schema or not isinstance(self.schema, hedschema.hed_schema.HedSchema):
            raise HedFileError('BadHedSchema', "Please provide a valid HedSchema", "")
        if not self.spreadsheet or not isinstance(self.spreadsheet, SpreadsheetInput):
            raise HedFileError('InvalidSpreadsheet', "A spreadsheet was given but could not be processed", "")
        if self.command == base_constants.COMMAND_VALIDATE:
            results = self.spreadsheet_validate()
        elif self.command == base_constants.COMMAND_TO_SHORT or self.command == base_constants.COMMAND_TO_LONG:
            results = self.spreadsheet_convert()
        else:
            raise HedFileError('UnknownSpreadsheetProcessingMethod', f"Command {self.command} is missing or invalid", "")
        return results
    
    def spreadsheet_convert(self):
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
        if self.command == base_constants.COMMAND_TO_LONG:
            suffix = '_to_long'
            self.spreadsheet.convert_to_long(self.schema)
        else:
            suffix = '_to_short'
            self.spreadsheet.convert_to_short(self.schema)
    
        file_name = generate_filename(display_name, name_suffix=suffix, extension=display_ext, append_datetime=True)
        return {base_constants.COMMAND: self.command,
                base_constants.COMMAND_TARGET: 'spreadsheet', 'data': '',
                base_constants.SPREADSHEET: self.spreadsheet, 'output_display_name': file_name,
                base_constants.SCHEMA_VERSION: get_schema_versions(self.schema),
                base_constants.MSG_CATEGORY: 'success',
                base_constants.MSG: f'Spreadsheet {display_name} converted_successfully'} 
    
    def spreadsheet_validate(self):
        """ Validates the spreadsheet.
 
        Returns:
            dict: A dictionary containing results of validation in standard format.
    
        Notes: The allowed options are
            check_for_warnings (bool): Indicates whether validation should check for warnings as well as errors.
    
        """
        
        error_handler = ErrorHandler(check_for_warnings=self.check_for_warnings)
        display_name = self.spreadsheet.name
        issues = self.spreadsheet.validate(self.schema, error_handler=error_handler, name=display_name)
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
    
        return {base_constants.COMMAND: base_constants.COMMAND_VALIDATE,
                base_constants.COMMAND_TARGET: 'spreadsheet', 'data': data,
                base_constants.SPREADSHEET: '',
                base_constants.SCHEMA_VERSION: get_schema_versions(self.schema),
                "output_display_name": file_name,
                base_constants.MSG_CATEGORY: category, base_constants.MSG: msg}
