import os
import json
from werkzeug.utils import secure_filename

from hed.errors import ErrorHandler
from hed import schema as hedschema
from hed.errors import HedFileError, get_printable_issue_string

from hed.models.spreadsheet_input import SpreadsheetInput
from hed.models.sidecar import Sidecar
from hed.models import df_util
from hed.tools.analysis.annotation_util import df_to_hed, hed_to_df, merge_hed_dict
from hedweb.constants import base_constants as bc
from hedweb.constants import file_constants as fc
from hedweb.constants import base_constants, file_constants
from hedweb.base_operations import BaseOperations
from hedweb.web_util import form_has_option, generate_filename, get_hed_schema_from_pull_down, get_schema_versions


class SidecarOperations(BaseOperations):

    def __init__(self):
        """ Construct a ProcessSidecars object to handle sidecar form requests. 

        """
        self.schema = None
        self.command = None
        self.sidecar = None
        self.spreadsheet = None
        self.check_for_warnings = False
        self.expand_defs = False
        self.include_description_tags = False
        self.spreadsheet_type = fc.TSV_EXTENSION

    def set_input_from_form(self, request):
        """ Set a dictionary of input for processing from a sidecars form.

         parameters:
             request (Request): A Request object containing user data from the form.

         """
    
        self.schema = get_hed_schema_from_pull_down(request)
        self.command = request.form.get(base_constants.COMMAND_OPTION, None)
        self.check_for_warnings = form_has_option(request, base_constants.CHECK_FOR_WARNINGS, 'on')
        self.expand_defs = form_has_option(request, base_constants.EXPAND_DEFS, 'on')
        self.include_description_tags = form_has_option(request, base_constants.INCLUDE_DESCRIPTION_TAGS, 'on')
        self.spreadsheet_type = file_constants.TSV_EXTENSION
        if base_constants.SIDECAR_FILE in request.files:
            f = request.files[base_constants.SIDECAR_FILE]
            if f.filename:
                self.sidecar = Sidecar(files=f, name=secure_filename(f.filename))
        if bc.SPREADSHEET_FILE in request.files and request.files[bc.SPREADSHEET_FILE].filename:
            filename = request.files[bc.SPREADSHEET_FILE].filename
            file_ext = os.path.splitext(filename)[1]
            if file_ext in file_constants.EXCEL_FILE_EXTENSIONS:
                self.spreadsheet_type = file_constants.EXCEL_EXTENSION
            self.spreadsheet = SpreadsheetInput(file=request.files[bc.SPREADSHEET_FILE],
                                                file_type=self.spreadsheet_type,
                                                worksheet_name=None,
                                                tag_columns=['HED'], has_column_names=True, name=filename)

    def process(self):
        """ Perform the requested action for the sidecar.
        
        Returns:
            dict: A dictionary of results in standard form.
    
        """
        if not self.command:
            raise HedFileError('MissingCommand', 'Command is missing', '')
        elif not self.sidecar and not base_constants.COMMAND_MERGE_SPREADSHEET:
            raise HedFileError('MissingSidecarFile', "Please give a valid JSON sidecar file to process", "")
        elif (self.command == base_constants.COMMAND_EXTRACT_SPREADSHEET or
              self.command == base_constants.COMMAND_MERGE_SPREADSHEET):
            pass
        elif not self.schema or not isinstance(self.schema, hedschema.hed_schema.HedSchema):
            raise HedFileError('BadHedSchema', "Please provide a valid HedSchema", "")

        if self.command == base_constants.COMMAND_VALIDATE:
            results = self.sidecar_validate()
        elif self.command == base_constants.COMMAND_TO_SHORT or self.command == base_constants.COMMAND_TO_LONG:
            results = self.sidecar_convert()
        elif self.command == base_constants.COMMAND_EXTRACT_SPREADSHEET:
            results = self.sidecar_extract()
        elif self.command == base_constants.COMMAND_MERGE_SPREADSHEET:
            results = self.sidecar_merge()
        else:
            raise HedFileError('UnknownProcessingMethod', f'Command {self.command} is missing or invalid', '')
        return results
       
    def sidecar_convert(self):
        """ Convert a sidecar from long to short form or short to long form.
    
        Returns:
            dict:  A downloadable response dictionary
    
        Notes:
            command (str):           Either 'to short' or 'to long' indicating type of conversion.
            expand_defs (bool):      If True, expand definitions when converting, otherwise do no expansion
    
        """
        self.check_for_warnings = False
        results = self.sidecar_validate()
        if results[base_constants.MSG_CATEGORY] == 'warning':
            return results
        display_name = self.sidecar.name
        if self.expand_defs:
            def_dicts = self.sidecar.extract_definitions(hed_schema=self.schema)
        else:
            def_dicts = None
        if self.command == base_constants.COMMAND_TO_LONG:
            tag_form = 'long_tag'
        else:
            tag_form = 'short_tag'
        for column_data in self.sidecar:
            hed_strings = column_data.get_hed_strings()
            if hed_strings.empty:
                continue
            if self.expand_defs:
                df_util.expand_defs(hed_strings, self.schema, def_dicts, columns=None)
            else:
                df_util.shrink_defs(hed_strings, self.schema)
            df_util.convert_to_form(hed_strings, self.schema, tag_form)
            column_data.set_hed_strings(hed_strings)
    
        file_name = generate_filename(display_name, name_suffix=f"_{tag_form}", extension='.json', append_datetime=True)
        data = self.sidecar.get_as_json_string()
        category = 'success'
        msg = f'Sidecar file {display_name} was successfully converted'
        return {base_constants.COMMAND: self.command, base_constants.COMMAND_TARGET: 'sidecar',
                'data': data, 'output_display_name': file_name,
                base_constants.SCHEMA_VERSION: get_schema_versions(self.schema),
                'msg_category': category, 'msg': msg}
    
    def sidecar_extract(self):
        """ Create a four-column spreadsheet with the HED portion of the JSON sidecar.
 
        Returns:
            dict: A downloadable dictionary file or a file containing warnings
    
        """
        json_string = self.sidecar.get_as_json_string()
        str_sidecar = json.loads(json_string)
        df = hed_to_df(str_sidecar)
        data = df.to_csv(None, sep='\t', index=False, header=True)
        display_name = self.sidecar.name
        file_name = generate_filename(display_name, name_suffix='_extracted', extension='.tsv', append_datetime=True)
        return {base_constants.COMMAND: base_constants.COMMAND_EXTRACT_SPREADSHEET,
                base_constants.COMMAND_TARGET: 'sidecar',
                'data': data, 'output_display_name': file_name,
                'msg_category': 'success', 'msg': f'JSON sidecar {display_name} was successfully extracted'}
    
    def sidecar_merge(self):
        """ Merge an edited 4-column spreadsheet with JSON sidecar.

        Returns:
            dict
            A downloadable dictionary file or a file containing warnings
    
        Notes: The allowed option for merge is:
            include_description_tags (bool): If True, a Description tag is generated from Levels and included.
    
        """
    
        if not self.spreadsheet:
            raise HedFileError('MissingSpreadsheet', 'Cannot merge spreadsheet with sidecar', '')
        df = self.spreadsheet.dataframe
        hed_dict = df_to_hed(df, description_tag=self.include_description_tags)
        if self.sidecar:
            sidecar_dict = json.loads(self.sidecar.get_as_json_string())
            display_name = self.sidecar.name
        else:
            sidecar_dict = {}
            display_name = "empty_sidecar"
        merge_hed_dict(sidecar_dict, hed_dict)

        data = json.dumps(sidecar_dict, indent=4)
        file_name = generate_filename(display_name, name_suffix='_merged_with_spreadsheet',
                                      extension='.json', append_datetime=True)
        return {base_constants.COMMAND: self.command,
                base_constants.COMMAND_TARGET: 'sidecar',
                'data': data, 'output_display_name': file_name,
                'msg_category': 'success', 'msg': f'JSON sidecar {display_name} was successfully merged'}
    
    def sidecar_validate(self):
        """ Validate the sidecars and return the errors and/or a message in a dictionary.
 
        Returns:
            dict: A dictionary of response values in standard form.
    
        Notes:  The allowed option for validate is:
            check_for_warnings (bool): If True, check for warnings as well as errors.
    
        """
    
        error_handler = ErrorHandler(check_for_warnings=self.check_for_warnings)
        issues = self.sidecar.validate(self.schema, name=self.sidecar.name, error_handler=error_handler)
        if issues:
            data = get_printable_issue_string(issues, f"JSON dictionary {self.sidecar.name} validation issues")
            file_name = generate_filename(self.sidecar.name, name_suffix='validation_issues',
                                          extension='.txt', append_datetime=True)
            category = 'warning'
            msg = f'JSON sidecar {self.sidecar.name} had validation issues'
        else:
            data = ''
            file_name = self.sidecar.name
            category = 'success'
            msg = f'JSON file {self.sidecar.name} had no validation issues'
    
        return {base_constants.COMMAND: self.command, base_constants.COMMAND_TARGET: 'sidecar',
                'data': data, 'output_display_name': file_name,
                base_constants.SCHEMA_VERSION: get_schema_versions(self.schema),
                base_constants.MSG_CATEGORY: category, base_constants.MSG: msg}
