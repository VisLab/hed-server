import json
import pandas as pd

from hed import schema as hedschema
from hed.errors import get_printable_issue_string, HedFileError, ErrorHandler
from hed.errors.error_reporter import check_for_any_errors
from hed.models.definition_dict import DefinitionDict
from hed.models.tabular_input import TabularInput
from hed.models.df_util import get_assembled
from hed.models.query_service import get_query_handlers, search_strings
from hed.tools.remodeling.dispatcher import Dispatcher
from hed.tools.remodeling.remodeler_validator import RemodelerValidator
from hed.tools.analysis.hed_tag_manager import HedTagManager
from hed.tools.analysis.event_manager import EventManager
from hed.tools.analysis.tabular_summary import TabularSummary
from hed.tools.analysis.annotation_util import generate_sidecar_entry
from hedweb.constants import base_constants as bc
from hedweb.base_operations import BaseOperations
from hedweb.web_util import generate_filename, get_schema_versions


class EventOperations(BaseOperations):

    def __init__(self, arguments=None):
        """ Construct a ProcessEvents object to handle events form requests. 

        Parameters:
             arguments (dict): Dictionary with parameters extracted from form or service

        """
        self.schema = None
        self.events = None
        self.command = None
        self.check_for_warnings = False
        self.expand_defs = False
        self.include_summaries = False
        self.columns_skip = []
        self.columns_value = []
        self.sidecar = None
        self.remodel_operations = None
        self.queries = None
        self.query_names = None
        self.remove_types = []
        self.replace_defs = False
        self.expand_context = True
        if arguments:
            self.set_input_from_dict(arguments)

    def process(self):
        """ Perform the requested action for the events file and its sidecar.
    
        Returns:
            dict: A dictionary of results in the standard results format.
    
        Raises:
            HedFileError:  If the command was not found or the input arguments were not valid.
    
        """
        if not self.command:
            raise HedFileError('MissingCommand', 'Command is missing', '')
        elif self.command == bc.COMMAND_GENERATE_SIDECAR or self.command == bc.COMMAND_REMODEL:
            pass
        elif not self.schema or not \
                isinstance(self.schema, (hedschema.hed_schema.HedSchema, hedschema.hed_schema_group.HedSchemaGroup)):
            raise HedFileError('BadHedSchema', "Please provide a valid HedSchema for event processing", "")
        
        if not self.events or not isinstance(self.events, TabularInput):
            raise HedFileError('InvalidEventsFile', "An events file was not given or could not be read", "")
        if self.command == bc.COMMAND_VALIDATE:
            results = self.validate()
        elif self.command == bc.COMMAND_SEARCH:
            results = self.search()
        elif self.command == bc.COMMAND_ASSEMBLE:
            results = self.assemble()
        elif self.command == bc.COMMAND_GENERATE_SIDECAR:
            results = self.generate_sidecar()
        elif self.command == bc.COMMAND_REMODEL:
            results = self.remodel()
        else:
            raise HedFileError('UnknownEventsProcessingMethod', f'Command {self.command} is missing or invalid', '')
        return results 
    
    def assemble(self):
        """ Create a tabular file with the original positions in first column and a HED column.
  
    
        Returns:
            dict: A dictionary of results in standard format including either the assembled events string or errors.
    
        Notes:
            options include columns_included and expand_defs.
        """
    
        self.check_for_warnings = False
        results = self.validate()
        if results['data']:
            return results
        hed_strings, definitions = get_assembled(self.events, self.schema, defs_expanded=self.expand_defs)
        df = pd.DataFrame({"HED_assembled": [str(hed) for hed in hed_strings]})
        csv_string = df.to_csv(None, sep='\t', index=False, header=True)
        display_name = self.events.name
        file_name = generate_filename(display_name, name_suffix='_expanded', extension='.tsv', append_datetime=True)
        return {bc.COMMAND: bc.COMMAND_ASSEMBLE,
                bc.COMMAND_TARGET: 'events',
                'data': csv_string, 'output_display_name': file_name,
                'definitions': DefinitionDict.get_as_strings(definitions),
                'schema_version': self.schema.get_formatted_version(),
                'msg_category': 'success', 'msg': 'Events file successfully expanded'}

    def generate_sidecar(self):
        """ Generate a JSON sidecar template from a BIDS-style events file.
  
        Returns:
            dict: A dictionary of results in standard format including either the generated sidecar string or errors.
    
        Notes: Options are the columns selected. If None, all columns are used.
    
        """
        display_name = self.events.name
        if self.columns_skip and self.columns_value:
            overlap = set(self.columns_skip).intersection(set(self.columns_value))
            if overlap:
                return {bc.COMMAND: bc.COMMAND_GENERATE_SIDECAR, bc.COMMAND_TARGET: 'events',
                        'data': f"Skipped and value column names have these names in common: {str(overlap)}",
                        "output_display_name": generate_filename(display_name, name_suffix='sidecar_generation_issues',
                                                                 extension='.txt', append_datetime=True),
                        bc.MSG_CATEGORY: 'warning',
                        bc.MSG: f"Cannot generate sidecar because skipped and value column names overlap."}

        columns_info = TabularSummary.get_columns_info(self.events.dataframe)
        hed_dict = {}
        for column_name in columns_info:
            if column_name in self.columns_skip:
                continue
            elif column_name in self.columns_value:
                hed_dict[column_name] = generate_sidecar_entry(column_name)
            else:
                hed_dict[column_name] = generate_sidecar_entry(column_name,
                                                               column_values=list(columns_info[column_name].keys()))
        file_name = generate_filename(display_name, name_suffix='_generated', extension='.json', append_datetime=True)
        return {bc.COMMAND: bc.COMMAND_GENERATE_SIDECAR,
                bc.COMMAND_TARGET: 'events',
                'data': json.dumps(hed_dict, indent=4),
                'output_display_name': file_name, 'msg_category': 'success',
                'msg': 'JSON sidecar generation from event file complete'}

    def remodel(self):
        """ Remodel a given events file.
    
        Returns:
            dict: A dictionary pointing to results or errors.
    
        Notes: The options for this are
            - include_summaries (bool):  If true and summaries exist, package event file and summaries in a zip file.
    
        """
    
        display_name = self.events.name
        if not self.remodel_operations:
            raise HedFileError("RemodelingOperationsMissing", "Must supply remodeling operations for remodeling", "")
        remodel_name = self.remodel_operations['name']
        operations = self.remodel_operations['operations']
        validator = RemodelerValidator()
        errors = validator.validate(operations)
        if errors:
            issue_str = "\n".join(errors)
            file_name = generate_filename(remodel_name, name_suffix='_operation_parse_errors',
                                          extension='.txt', append_datetime=True)
            return {bc.COMMAND: bc.COMMAND_REMODEL,
                    bc.COMMAND_TARGET: 'events',
                    'data': issue_str, 'output_display_name': file_name,
                    'msg_category': "warning",
                    'msg': f"Remodeling operation list for {display_name} had validation issues"}
        df = self.events.dataframe
        dispatch = Dispatcher(operations, data_root=None, hed_versions=self.schema)
    
        for operation in dispatch.parsed_ops:
            df = dispatch.prep_data(df)
            df = operation.do_op(dispatch, df, display_name, sidecar=self.sidecar)
            df = dispatch.post_proc_data(df)
        data = df.to_csv(None, sep='\t', index=False, header=True, lineterminator='\n')
        name_suffix = f"_remodeled_by_{remodel_name}"
        file_name = generate_filename(display_name, name_suffix=name_suffix, extension='.tsv', append_datetime=True)
        output_name = file_name
        response = {bc.COMMAND: bc.COMMAND_REMODEL,
                    bc.COMMAND_TARGET: 'events', 'data': '', "output_display_name": output_name,
                    bc.SCHEMA_VERSION: get_schema_versions(self.schema),
                    bc.MSG_CATEGORY: 'success',
                    bc.MSG: f"Command parsing for {display_name} remodeling was successful"}
        if dispatch.summary_dicts and self.include_summaries:
            file_list = dispatch.get_summaries()
            file_list.append({'file_name': output_name, 'file_format': '.tsv', 'file_type': 'tabular', 'content': data})
            response[bc.FILE_LIST] = file_list
            response[bc.ZIP_NAME] = generate_filename(display_name, name_suffix=name_suffix + '_zip',
                                                      extension='.zip', append_datetime=True)
        else:
            response['data'] = data
        return response
    
    def search(self):
        """ Create a three-column tsv file with event number, matched string, and assembled strings for matched events.
    
        Returns:
            dict: A dictionary pointing to results or errors.
    
        Notes:  The options for this are
            columns_included (list):  A list of column names of columns to include.
            expand_defs (bool): If True, expand the definitions in the assembled HED. Otherwise, shrink definitions.
    
        """

        display_name = self.events.name
        queries, query_names, issues = get_query_handlers(self.queries, self.query_names)
        if issues:
            return {bc.COMMAND: bc.COMMAND_SEARCH, bc.COMMAND_TARGET: 'events',
                    'data': "Query errors:\n" + "\n".join(issues),
                    "output_display_name": generate_filename(display_name, name_suffix='query_validation_issues',
                                                             extension='.txt', append_datetime=True),
                    bc.SCHEMA_VERSION: get_schema_versions(self.schema),
                    bc.MSG_CATEGORY: 'warning',
                    bc.MSG: f"Queries had validation issues"}
        results = self.validate()
        if results['data']:
            return results
        tag_man = HedTagManager(EventManager(self.events, self.schema), remove_types=self.remove_types)
        hed_objs = tag_man.get_hed_objs(include_context=self.expand_context, replace_defs=self.replace_defs)
        df_factors = search_strings(hed_objs, queries, query_names=query_names)
        file_name = generate_filename(display_name, name_suffix='_queries', extension='.tsv', append_datetime=True)
        return {bc.COMMAND: bc.COMMAND_SEARCH,
                bc.COMMAND_TARGET: 'events',
                'data': df_factors.to_csv(None, sep='\t', index=False, header=True, lineterminator='\n'),
                'output_display_name': file_name, 'schema_version': self.schema.get_formatted_version(),
                bc.MSG_CATEGORY: 'success',
                bc.MSG: f"Successfully made {len(self.queries)} queries for {display_name}"}

    def validate(self):
        """ Validate the events tabular input object and return the results.
    
        Returns:
            dict: A dictionary containing results of validation in standard format.
    
        Notes: The dictionary of options includes the following.
            - check_for_warnings (bool): If true, validation should include warnings. (default False)
    
        """
        display_name = self.events.name
        error_handler = ErrorHandler(check_for_warnings=self.check_for_warnings)
        issues = []
        if self.sidecar:
            issues = self.sidecar.validate(self.schema, name=self.sidecar.name, error_handler=error_handler)
        if not check_for_any_errors(issues):
            issues += self.events.validate(self.schema, name=self.events.name, error_handler=error_handler)
        if issues:
            data = get_printable_issue_string(issues, title="Event file errors:")
            file_name = generate_filename(display_name, name_suffix='_validation_issues',
                                          extension='.txt', append_datetime=True)
            category = 'warning'
            msg = f"Events file {display_name} had validation issues"
        else:
            data = ''
            file_name = display_name
            category = 'success'
            msg = f"Events file {display_name} did not have validation issues"
    
        return {bc.COMMAND: bc.COMMAND_VALIDATE, bc.COMMAND_TARGET: 'events',
                'data': data, "output_display_name": file_name,
                bc.SCHEMA_VERSION: get_schema_versions(self.schema),
                bc.MSG_CATEGORY: category, bc.MSG: msg}
