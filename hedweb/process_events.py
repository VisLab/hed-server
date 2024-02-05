import json
from werkzeug.utils import secure_filename
import pandas as pd

from hed import schema as hedschema
from hed.errors import get_printable_issue_string, HedFileError, ErrorHandler
from hed.errors.error_reporter import check_for_any_errors
from hed.models.definition_dict import DefinitionDict
from hed.models.sidecar import Sidecar
from hed.models.tabular_input import TabularInput
from hed.models.df_util import get_assembled, shrink_defs
from hed.tools.util.data_util import separate_values
from hed.tools.remodeling.dispatcher import Dispatcher
from hed.tools.remodeling.remodeler_validator import RemodelerValidator
from hed.tools.analysis import analysis_util
from hed.tools.analysis.tabular_summary import TabularSummary
from hed.tools.analysis.annotation_util import generate_sidecar_entry
from hedweb.constants import base_constants
from hedweb.process_base import ProcessBase
from hedweb.columns import create_column_selections
from hedweb.web_util import form_has_option, generate_filename, get_hed_schema_from_pull_down, get_schema_versions

class ProcessEvents(ProcessBase):

    def __init__(self):
        """ Construct a ProcessEvents object to handle events form requests. 
        
        """
        self.schema = None
        self.events = None
        self.command = None
        self.check_for_warnings = False
        self.expand_defs = False
        self.include_summaries = False
        self.columns_selected = None
        self.columns_included = None
        self.sidecar = None
        self.remodel_operations = None
        self.query = None

    def set_input_from_form(self, request):
        """ Set input for processing from an events form.
    
        parameters:
            request (Request): A Request object containing user data from the form.
    
        """
        self.command = request.form.get(base_constants.COMMAND_OPTION, '')
        self.check_for_warnings = form_has_option(request, base_constants.CHECK_FOR_WARNINGS, 'on')
        self.expand_defs = form_has_option(request, base_constants.EXPAND_DEFS, 'on')
        self.include_summaries = form_has_option(request, base_constants.INCLUDE_SUMMARIES, 'on')
        self.columns_selected = create_column_selections(request.form)
        if self.command == base_constants.COMMAND_ASSEMBLE:
            self.columns_included = ['onset']   # TODO  add user interface option to choose columns.
        if self.command != base_constants.COMMAND_GENERATE_SIDECAR:
            self.schema = get_hed_schema_from_pull_down(request)
        if base_constants.SIDECAR_FILE in request.files:
            f = request.files[base_constants.SIDECAR_FILE]
            self.sidecar = Sidecar(files=f, name=secure_filename(f.filename))
        if self.command == base_constants.COMMAND_REMODEL and \
                base_constants.REMODEL_FILE in request.files:
            f = request.files[base_constants.REMODEL_FILE]
            name = secure_filename(f.filename)
            self.remodel_operations = {'name': name, 'operations': json.load(f)}

        if base_constants.EVENTS_FILE in request.files:
            f = request.files[base_constants.EVENTS_FILE]
            self.events = TabularInput(file=f, sidecar=self.sidecar, name=secure_filename(f.filename))

    def process(self):
        """ Perform the requested action for the events file and its sidecar.
    
        Returns:
            dict: A dictionary of results in the standard results format.
    
        Raises:
            HedFileError:  If the command was not found or the input arguments were not valid.
    
        """
        if not self.command:
            raise HedFileError('MissingCommand', 'Command is missing', '')
        elif self.command == base_constants.COMMAND_GENERATE_SIDECAR or self.command == base_constants.COMMAND_REMODEL:
            pass
        elif not self.schema or not \
                isinstance(self.schema, (hedschema.hed_schema.HedSchema, hedschema.hed_schema_group.HedSchemaGroup)):
            raise HedFileError('BadHedSchema', "Please provide a valid HedSchema for event processing", "")
        
        if not self.events or not isinstance(self.events, TabularInput):
            raise HedFileError('InvalidEventsFile', "An events file was not given or could not be read", "")
        if self.command == base_constants.COMMAND_VALIDATE:
            results = self.validate()
        elif self.command == base_constants.COMMAND_SEARCH:
            results = self.search()
        elif self.command == base_constants.COMMAND_ASSEMBLE:
            results = self.assemble()
        elif self.command == base_constants.COMMAND_GENERATE_SIDECAR:
            results = self.generate_sidecar()
        elif self.command == base_constants.COMMAND_REMODEL:
            results = self.remodel()
        else:
            raise HedFileError('UnknownEventsProcessingMethod', f'Command {self.command} is missing or invalid', '')
        return results 
    
    def assemble(self):
        """ Create a tabular file with the first column, specified additional columns and a HED column.
  
    
        Returns:
            dict: A dictionary of results in standard format including either the assembled events string or errors.
    
        Notes:
            options include columns_included and expand_defs.
        """
    
        self.check_for_warnings = False
        results = self.validate()
        if results['data']:
            return results
        df, _, definitions = self._assemble()
        csv_string = df.to_csv(None, sep='\t', index=False, header=True)
        display_name = self.events.name
        file_name = generate_filename(display_name, name_suffix='_expanded', extension='.tsv', append_datetime=True)
        return {base_constants.COMMAND: base_constants.COMMAND_ASSEMBLE,
                base_constants.COMMAND_TARGET: 'events',
                'data': csv_string, 'output_display_name': file_name,
                'definitions': DefinitionDict.get_as_strings(definitions),
                'schema_version': self.schema.get_formatted_version(),
                'msg_category': 'success', 'msg': 'Events file successfully expanded'}

    def _assemble(self):
        eligible_columns, missing_columns = separate_values(list(self.events.dataframe.columns), self.columns_included)
        if self.expand_defs:
            shrink = False
        else:
            shrink = True
        hed_strings, definitions = get_assembled(self.events, self.sidecar, self.schema, extra_def_dicts=None,
                                                 join_columns=True, shrink_defs=shrink, expand_defs=self.expand_defs)
        if not eligible_columns:
            df = pd.DataFrame({"HED_assembled": [str(hed) for hed in hed_strings]})
        else:
            df = self.events.dataframe[eligible_columns].copy(deep=True)
            df['HED_assembled'] = pd.Series(hed_strings).astype(str)
        return df, hed_strings, definitions
    
    def generate_sidecar(self):
        """ Generate a JSON sidecar template from a BIDS-style events file.
  
        Returns:
            dict: A dictionary of results in standard format including either the generated sidecar string or errors.
    
        Notes: Options are the columns selected. If None, all columns are used.
    
        """
        columns_info = TabularSummary.get_columns_info(self.events.dataframe)
        hed_dict = {}
        for column_name, column_type in self.columns_selected.items():
            if column_name not in columns_info:
                continue
            if column_type:
                column_values = list(columns_info[column_name].keys())
            else:
                column_values = None
            hed_dict[column_name] = generate_sidecar_entry(column_name, column_values=column_values)
        display_name = self.events.name
    
        file_name = generate_filename(display_name, name_suffix='_generated', extension='.json', append_datetime=True)
        return {base_constants.COMMAND: base_constants.COMMAND_GENERATE_SIDECAR,
                base_constants.COMMAND_TARGET: 'events',
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
        remodel_name = self.remodel_operations['name']
        operations = self.remodel_operations['operations']
        validator = RemodelerValidator()
        errors = validator.validate(operations)
        if errors:
            issue_str = "\n".join(errors)
            file_name = generate_filename(remodel_name, name_suffix='_operation_parse_errors',
                                          extension='.txt', append_datetime=True)
            return {base_constants.COMMAND: base_constants.COMMAND_REMODEL,
                    base_constants.COMMAND_TARGET: 'events',
                    'data': issue_str, 'output_display_name': file_name,
                    'msg_category': "warning",
                    'msg': f"Remodeling operation list for {display_name} had validation issues"}
        df = self.events.dataframe
        dispatch = Dispatcher(operations, data_root=None, hed_versions=self.schema)
    
        for operation in dispatch.parsed_ops:
            df = dispatch.prep_data(df)
            df = operation.do_op(dispatch, df, display_name, sidecar=self.sidecar)
            df = dispatch.post_proc_data(df)
        data = df.to_csv(None, sep='\t', index=False, header=True)
        name_suffix = f"_remodeled_by_{remodel_name}"
        file_name = generate_filename(display_name, name_suffix=name_suffix, extension='.tsv', append_datetime=True)
        output_name = file_name
        response = {base_constants.COMMAND: base_constants.COMMAND_REMODEL,
                    base_constants.COMMAND_TARGET: 'events', 'data': '', "output_display_name": output_name,
                    base_constants.SCHEMA_VERSION: get_schema_versions(self.schema),
                    base_constants.MSG_CATEGORY: 'success',
                    base_constants.MSG: f"Command parsing for {display_name} remodeling was successful"}
        if dispatch.summary_dicts and self.include_summaries:
            file_list = dispatch.get_summaries()
            file_list.append({'file_name': output_name, 'file_format': '.tsv', 'file_type': 'tabular', 'content': data})
            response[base_constants.FILE_LIST] = file_list
            response[base_constants.ZIP_NAME] = generate_filename(display_name, name_suffix=name_suffix + '_zip',
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
        
        results = self.validate()
        if results['data']:
            return results
        results = self.validate_query()
        if results['data']:
            return results
        df, hed_strings, definitions = self._assemble()
        if not self.expand_defs:
            shrink_defs(df, self.schema)
        df_factor = analysis_util.search_strings(hed_strings, [self.query], query_names=['query_results'])
        row_numbers = list(self.events.dataframe.index[df_factor.loc[:, 'query_results'] == 1])
        if not row_numbers:
            msg = f"Events file has no events satisfying the query {self.query}."
            csv_string = ""
        else:
            df['query_results'] = df_factor.loc[:, 'query_results']
            df = self.events.dataframe.iloc[row_numbers].reset_index()
            csv_string = df.to_csv(None, sep='\t', index=False, header=True)
            msg = f"Events file query {self.query} satisfied by {len(row_numbers)} out of {len(self.events.dataframe)} events."
    
        display_name = self.events.name
        file_name = generate_filename(display_name, name_suffix='_query', extension='.tsv', append_datetime=True)
        return {base_constants.COMMAND: base_constants.COMMAND_SEARCH,
                base_constants.COMMAND_TARGET: 'events',
                'data': csv_string, 'output_display_name': file_name,
                'schema_version': self.schema.get_formatted_version(),
                base_constants.MSG_CATEGORY: 'success', base_constants.MSG: msg}
    
    
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
    
        return {base_constants.COMMAND: base_constants.COMMAND_VALIDATE, base_constants.COMMAND_TARGET: 'events',
                'data': data, "output_display_name": file_name,
                base_constants.SCHEMA_VERSION: get_schema_versions(self.schema),
                base_constants.MSG_CATEGORY: category, base_constants.MSG: msg}
    
    def validate_query(self):
        """ Validate the query and return the results.
    
        Returns
            dict: A dictionary containing results of validation in standard format.
    
        """
    
        if not self.query:
            data = "Empty query could not be processed."
            category = 'warning'
            msg = f"Empty query could not be processed"
        else:
            data = ''
            category = 'success'
            msg = f"Query had no validation issues"
    
        return {base_constants.COMMAND: base_constants.COMMAND_VALIDATE, base_constants.COMMAND_TARGET: 'query',
                'data': data, base_constants.SCHEMA_VERSION: get_schema_versions(self.schema),
                base_constants.MSG_CATEGORY: category, base_constants.MSG: msg}
