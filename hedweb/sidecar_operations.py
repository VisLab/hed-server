"""
Performs operations on JSON sidecars, such as validation, conversion, extraction, and merging with spreadsheets.
"""
import json
from hed.errors import ErrorHandler
from hed import schema as hedschema
from hed.errors import HedFileError, get_printable_issue_string
from hed.models import df_util
from hed.tools.analysis.annotation_util import df_to_hed, hed_to_df, merge_hed_dict
from hedweb.constants import file_constants as fc
from hedweb.constants import base_constants as bc
from hedweb.base_operations import BaseOperations
from hedweb.web_util import generate_filename, get_schema_versions


class SidecarOperations(BaseOperations):
    """ Class to perform operations on sidecars."""

    def __init__(self, arguments=None):
        """ Construct a SidecarOperations object to handle sidecar operations.

        Parameters:
             arguments (dict or None): Dictionary with parameters extracted from form or service

        """
        self.schema = None
        self.command = None
        self.sidecar = None
        self.spreadsheet = None
        self.check_for_warnings = False
        self.expand_defs = False
        self.include_description_tags = False
        self.spreadsheet_type = fc.TSV_EXTENSION
        if arguments:
            self.set_input_from_dict(arguments)

    def process(self) -> dict:
        """ Perform the requested action for the sidecar.
        
        Returns:
            dict: A dictionary of results in standard form.

        Raises:
            HedFileError: If the command was not found or the input arguments were not valid.
            HedFileError: If the schema is not found or cannot be loaded.
            HedFileError: If the sidecar is not found or cannot be loaded.
            HedFileError: If a required spreadsheet is not found or cannot be loaded.
    
        """
        if not self.command:
            raise HedFileError('MissingCommand', 'Command is missing', '')
        elif not self.sidecar and not bc.COMMAND_MERGE_SPREADSHEET:
            raise HedFileError('MissingSidecarFile', "Please give a valid JSON sidecar file to process", "")
        elif (self.command == bc.COMMAND_EXTRACT_SPREADSHEET or
              self.command == bc.COMMAND_MERGE_SPREADSHEET):
            pass
        elif not self.schema or not isinstance(self.schema, hedschema.hed_schema.HedSchema):
            raise HedFileError('BadHedSchema', "Please provide a valid HedSchema", "")

        if self.command == bc.COMMAND_VALIDATE:
            results = self.sidecar_validate()
        elif self.command == bc.COMMAND_TO_SHORT or self.command == bc.COMMAND_TO_LONG:
            results = self.sidecar_convert()
        elif self.command == bc.COMMAND_EXTRACT_SPREADSHEET:
            results = self.sidecar_extract()
        elif self.command == bc.COMMAND_MERGE_SPREADSHEET:
            results = self.sidecar_merge()
        else:
            raise HedFileError('UnknownProcessingMethod', f'Command {self.command} is missing or invalid', '')
        return results
       
    def sidecar_convert(self) -> dict:
        """ Convert a sidecar from long to short form or short to long form.
    
        Returns:
            dict:  A downloadable response dictionary
    
        Notes:
            command (str):           Either 'to short' or 'to long' indicating type of conversion.
            expand_defs (bool):      If True, expand definitions when converting, otherwise do no expansion
    
        """
        self.check_for_warnings = False
        results = self.sidecar_validate()
        if results[bc.MSG_CATEGORY] == 'warning':
            return results
        display_name = self.sidecar.name
        if self.expand_defs:
            def_dicts = self.sidecar.extract_definitions(hed_schema=self.schema)
        else:
            def_dicts = None
        if self.command == bc.COMMAND_TO_LONG:
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
        return {bc.COMMAND: self.command, bc.COMMAND_TARGET: 'sidecar',
                'data': data, 'output_display_name': file_name,
                bc.SCHEMA_VERSION: get_schema_versions(self.schema),
                'msg_category': category, 'msg': msg}
    
    def sidecar_extract(self ) -> dict:
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
        return {bc.COMMAND: bc.COMMAND_EXTRACT_SPREADSHEET,
                bc.COMMAND_TARGET: 'sidecar',
                'data': data, 'output_display_name': file_name,
                'msg_category': 'success', 'msg': f'JSON sidecar {display_name} was successfully extracted'}
    
    def sidecar_merge(self) -> dict:
        """ Merge an edited 4-column spreadsheet with JSON sidecar.

        Returns:
            dict: A downloadable dictionary file or a file containing warnings

        Raises:
            HedFileError: If the spreadsheet is not provided or cannot be loaded.

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
        return {bc.COMMAND: self.command,
                bc.COMMAND_TARGET: 'sidecar',
                'data': data, 'output_display_name': file_name,
                'msg_category': 'success', 'msg': f'JSON sidecar {display_name} was successfully merged'}
    
    def sidecar_validate(self) -> dict:
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
    
        return {bc.COMMAND: self.command, bc.COMMAND_TARGET: 'sidecar',
                'data': data, 'output_display_name': file_name,
                bc.SCHEMA_VERSION: get_schema_versions(self.schema),
                bc.MSG_CATEGORY: category, bc.MSG: msg}
