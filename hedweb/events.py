from flask import current_app
import json
from werkzeug.utils import secure_filename
import pandas as pd

from hed import schema as hedschema
from hed.errors import get_printable_issue_string, HedFileError, ErrorHandler
from hed.errors.error_reporter import check_for_any_errors
from hed.models import DefinitionDict, Sidecar, TabularInput
from hed.models.df_util import get_assembled, shrink_defs
from hed.tools.util.io_util import generate_filename
from hed.tools.util.data_util import separate_values
from hed.tools.remodeling.dispatcher import Dispatcher
from hed.tools.analysis import analysis_util
from hed.tools.analysis.tabular_summary import TabularSummary
from hed.tools.analysis.annotation_util import generate_sidecar_entry
from hedweb.constants import base_constants
from hedweb.columns import create_column_selections, create_columns_included
from hedweb.web_util import form_has_option, get_hed_schema_from_pull_down, get_option

app_config = current_app.config


def get_events_form_input(request):
    """ Extract a dictionary of input for processing from the events form.

    Args:
        request (Request): A Request object containing user data from the validation form.

    Returns:
        dict: A dictionary of events processing parameters in standard form.

    """

    arguments = {base_constants.SCHEMA: None,
                 base_constants.EVENTS: None,
                 base_constants.COMMAND: request.form.get(base_constants.COMMAND_OPTION, ''),
                 base_constants.CHECK_FOR_WARNINGS: form_has_option(request, base_constants.CHECK_FOR_WARNINGS, 'on'),
                 base_constants.EXPAND_DEFS: form_has_option(request, base_constants.EXPAND_DEFS, 'on'),
                 base_constants.INCLUDE_SUMMARIES: form_has_option(request, base_constants.INCLUDE_SUMMARIES, 'on'),
                 base_constants.COLUMNS_SELECTED: create_column_selections(request.form),
                 base_constants.COLUMNS_INCLUDED: create_columns_included(request.form)
                 }
    if arguments[base_constants.COMMAND] == base_constants.COMMAND_ASSEMBLE:
        arguments[base_constants.COLUMNS_INCLUDED] = ['onset']   # TODO  add user interface option to choose columns.
    if arguments[base_constants.COMMAND] != base_constants.COMMAND_GENERATE_SIDECAR:
        arguments[base_constants.SCHEMA] = get_hed_schema_from_pull_down(request)
    sidecar = None
    if base_constants.SIDECAR_FILE in request.files:
        f = request.files[base_constants.SIDECAR_FILE]
        sidecar = Sidecar(files=f, name=secure_filename(f.filename))
    arguments[base_constants.SIDECAR] = sidecar
    remodel_operations = None
    if arguments[base_constants.COMMAND] == base_constants.COMMAND_REMODEL and \
            base_constants.REMODEL_FILE in request.files:
        f = request.files[base_constants.REMODEL_FILE]
        name = secure_filename(f.filename)
        remodel_operations = {'name': name, 'operations': json.load(f)}
    arguments[base_constants.REMODEL_OPERATIONS] = remodel_operations
    if base_constants.EVENTS_FILE in request.files:
        f = request.files[base_constants.EVENTS_FILE]
        arguments[base_constants.EVENTS] = \
            TabularInput(file=f, sidecar=arguments.get(base_constants.SIDECAR, None),
                         name=secure_filename(f.filename))
    return arguments


def process(arguments):
    """ Perform the requested action for the events file and its sidecar.

    Args:
        arguments (dict): A dictionary with the input arguments from the event form or service request.

    Returns:
        dict: A dictionary of results in the standard results format.

    Raises:
        HedFileError:  If the command was not found or the input arguments were not valid.

    """
    hed_schema = arguments.get('schema', None)
    command = arguments.get(base_constants.COMMAND, None)
    if command == base_constants.COMMAND_GENERATE_SIDECAR:
        pass
    elif not hed_schema or not \
            isinstance(hed_schema, (hedschema.hed_schema.HedSchema, hedschema.hed_schema_group.HedSchemaGroup)):
        raise HedFileError('BadHedSchema', "Please provide a valid HedSchema for event processing", "")
    events = arguments.get(base_constants.EVENTS, None)
    sidecar = arguments.get(base_constants.SIDECAR, None)
    remodel_operations = arguments.get(base_constants.REMODEL_OPERATIONS, None)
    query = arguments.get(base_constants.QUERY, None)
    if not events or not isinstance(events, TabularInput):
        raise HedFileError('InvalidEventsFile', "An events file was given but could not be processed", "")
    if command == base_constants.COMMAND_VALIDATE:
        results = validate(hed_schema, events, sidecar, arguments)
    elif command == base_constants.COMMAND_SEARCH:
        results = search(hed_schema, events, sidecar, query, arguments)
    elif command == base_constants.COMMAND_ASSEMBLE:
        results = assemble(hed_schema, events, sidecar, arguments)
    elif command == base_constants.COMMAND_GENERATE_SIDECAR:
        results = generate_sidecar(events, arguments)
    elif command == base_constants.COMMAND_REMODEL:
        results = remodel(hed_schema, events, sidecar, remodel_operations, arguments)
    else:
        raise HedFileError('UnknownEventsProcessingMethod', f'Command {command} is missing or invalid', '')
    return results


def assemble(hed_schema, events, sidecar, options=None):
    """ Create a tabular file with the first column, specified additional columns and a HED column.

    Args:
        hed_schema (HedSchema or HedSchemaGroup): A HED schema or HED schema group.
        events (TabularInput):  An tabular input object.
        sidecar (Sidecar): An associated sidecar.
        options (dict): Dictionary of options

    Returns:
        dict: A dictionary of results in standard format including either the assembled events string or errors.

    Notes:
        options include columns_included and expand_defs.
    """

    options[base_constants.CHECK_FOR_WARNINGS] = False
    results = validate(hed_schema, events, sidecar=sidecar, options=options)
    if results['data']:
        return results
    columns_included = get_option(options, base_constants.COLUMNS_INCLUDED, [])
    expand_defs = get_option(options, base_constants.EXPAND_DEFS, False)
    df, _, definitions = _assemble(hed_schema, events, sidecar, columns_included=columns_included,
                                   expand_defs=expand_defs)
    csv_string = df.to_csv(None, sep='\t', index=False, header=True)
    display_name = events.name
    file_name = generate_filename(display_name, name_suffix='_expanded', extension='.tsv', append_datetime=True)
    return {base_constants.COMMAND: base_constants.COMMAND_ASSEMBLE,
            base_constants.COMMAND_TARGET: 'events',
            'data': csv_string, 'output_display_name': file_name,
            'definitions': DefinitionDict.get_as_strings(definitions),
            'schema_version': hed_schema.get_formatted_version(as_string=True),
            'msg_category': 'success', 'msg': 'Events file successfully expanded'}


def _assemble(hed_schema, events, sidecar, columns_included=[], expand_defs=True):
    eligible_columns, missing_columns = separate_values(list(events.dataframe.columns), columns_included)
    if expand_defs:
        shrink_defs = False
    else:
        shrink_defs = True
    hed_strings, definitions = get_assembled(events, sidecar, hed_schema, extra_def_dicts=None,
                                             join_columns=True, shrink_defs=shrink_defs, expand_defs=expand_defs)
    if not eligible_columns:
        df = pd.DataFrame({"HED_assembled": [str(hed) for hed in hed_strings]})
    else:
        df = events.dataframe[eligible_columns].copy(deep=True)
        df['HED_assembled'] = pd.Series(hed_strings).astype(str)
    return df, hed_strings, definitions


def generate_sidecar(events, options=None):
    """ Generate a JSON sidecar template from a BIDS-style events file.

    Args:
        events (EventInput):      An events input object to generate sidecars from.
        options (dict):  A dictionary of options.

    Returns:
        dict: A dictionary of results in standard format including either the generated sidecar string or errors.

    Notes: Options are the columns selected. If None, all columns are used.

    """
    columns_selected = get_option(options, base_constants.COLUMNS_SELECTED, None)
    columns_info = TabularSummary.get_columns_info(events.dataframe)
    hed_dict = {}
    for column_name, column_type in columns_selected.items():
        if column_name not in columns_info:
            continue
        if column_type:
            column_values = list(columns_info[column_name].keys())
        else:
            column_values = None
        hed_dict[column_name] = generate_sidecar_entry(column_name, column_values=column_values)
    display_name = events.name

    file_name = generate_filename(display_name, name_suffix='_generated', extension='.json', append_datetime=True)
    return {base_constants.COMMAND: base_constants.COMMAND_GENERATE_SIDECAR,
            base_constants.COMMAND_TARGET: 'events',
            'data': json.dumps(hed_dict, indent=4),
            'output_display_name': file_name, 'msg_category': 'success',
            'msg': 'JSON sidecar generation from event file complete'}


def remodel(hed_schema, events, sidecar, remodel_operations, options=None):
    """ Remodel a given events file.

    Args:
        hed_schema (HedSchema, HedSchemaGroup or None): A HED schema or HED schema group.
        events (EventsInput):      An events input object.
        sidecar (Sidecar or None): A sidecar object.
        remodel_operations (dict): A dictionary with the name and list of operations in the remodeling file.
        options (dict): A dictionary of options.

    Returns:
        dict: A dictionary pointing to results or errors.

    Notes: The options for this are
        - include_summaries (bool):  If true and summaries exist, package event file and summaries in a zip file.

    """

    include_summaries = get_option(options, base_constants.INCLUDE_SUMMARIES, True)
    display_name = events.name
    remodel_name = remodel_operations['name']
    operations = remodel_operations['operations']
    operations_list, errors = Dispatcher.parse_operations(operations)
    if errors:
        issue_str = Dispatcher.errors_to_str(errors)
        file_name = generate_filename(remodel_name, name_suffix='_operation_parse_errors',
                                      extension='.txt', append_datetime=True)
        return {base_constants.COMMAND: base_constants.COMMAND_REMODEL,
                base_constants.COMMAND_TARGET: 'events',
                'data': issue_str, 'output_display_name': file_name,
                'msg_category': "warning",
                'msg': f"Remodeling operation list for {display_name} had validation errors"}
    df = events.dataframe
    dispatch = Dispatcher(operations, data_root=None, hed_versions=hed_schema)

    for operation in dispatch.parsed_ops:
        df = dispatch.prep_data(df)
        df = operation.do_op(dispatch, df, display_name, sidecar=sidecar)
        df = dispatch.post_proc_data(df)
    data = df.to_csv(None, sep='\t', index=False, header=True)
    name_suffix = f"_remodeled_by_{remodel_name}"
    file_name = generate_filename(display_name, name_suffix=name_suffix, extension='.tsv', append_datetime=True)
    output_name = file_name
    response = {base_constants.COMMAND: base_constants.COMMAND_REMODEL,
                base_constants.COMMAND_TARGET: 'events', 'data': '', "output_display_name": output_name,
                base_constants.SCHEMA_VERSION: hedschema.get_schema_versions(hed_schema, as_string=True),
                base_constants.MSG_CATEGORY: 'success',
                base_constants.MSG: f"Command parsing for {display_name} remodeling was successful"}
    if dispatch.context_dict and include_summaries:
        file_list = dispatch.get_summaries()
        file_list.append({'file_name': output_name, 'file_format': '.tsv', 'file_type': 'tabular', 'content': data})
        response[base_constants.FILE_LIST] = file_list
        response[base_constants.ZIP_NAME] = generate_filename(display_name, name_suffix=name_suffix + '_zip',
                                                              extension='.zip', append_datetime=True)
    else:
        response['data'] = data
    return response


def search(hed_schema, events, sidecar, query, options=None):
    """ Create a three-column tsv file with event number, matched string, and assembled strings for matched events.

    Args:
        hed_schema (HedSchema or HedSchemaGroup): A HED schema or HED schema group.
        events (TabularInput):     An events input object.
        sidecar (Sidecar):   A Sidecar object with HED annotations.
        query (str):              A string containing the query.
        options (dict):  A dictionary of options

    Returns:
        dict: A dictionary pointing to results or errors.

    Notes:  The options for this are
        columns_included (list):  A list of column names of columns to include.
        expand_defs (bool): If True, expand the definitions in the assembled HED. Otherwise shrink definitions.

    """
    columns_included = get_option(options, base_constants.COLUMNS_INCLUDED, None)
    expand_defs = get_option(options, base_constants.EXPAND_DEFS, True)
    results = validate(hed_schema, events)
    if results['data']:
        return results
    results = validate_query(hed_schema, query)
    if results['data']:
        return results
    df, hed_strings, definitions = _assemble(hed_schema, events, sidecar, columns_included=columns_included,
                                             expand_defs=True)
    if not expand_defs:
        shrink_defs(df, hed_schema)
    df_factor = analysis_util.search_strings(hed_strings, [query], query_names=['query_results'])
    row_numbers = list(events.dataframe.index[df_factor.loc[:, 'query_results'] == 1])
    if not row_numbers:
        msg = f"Events file has no events satisfying the query {query}."
        csv_string = ""
    else:
        df['query_results'] = df_factor.loc[:, 'query_results']
        df = events.dataframe.iloc[row_numbers].reset_index()
        csv_string = df.to_csv(None, sep='\t', index=False, header=True)
        msg = f"Events file query {query} satisfied by {len(row_numbers)} out of {len(events.dataframe)} events."

    display_name = events.name
    file_name = generate_filename(display_name, name_suffix='_query', extension='.tsv', append_datetime=True)
    return {base_constants.COMMAND: base_constants.COMMAND_SEARCH,
            base_constants.COMMAND_TARGET: 'events',
            'data': csv_string, 'output_display_name': file_name,
            'schema_version': hed_schema.get_formatted_version(as_string=True),
            base_constants.MSG_CATEGORY: 'success', base_constants.MSG: msg}


def validate(hed_schema, events, sidecar=None, options=None):
    """ Validate a tabular input object and return the results.

    Args:
        hed_schema (HedSchema or HedSchemaGroup): Schema or schemas used for validation.
        events (TabularInput): Tabular input object representing a file to be validated.
        sidecar (Sidecar or None): The Sidecar associated with this tabular data file.
        options (dict): Dictionary of options

    Returns:
        dict: A dictionary containing results of validation in standard format.

    Notes: The dictionary of options includes the following.
        - check_for_warnings (bool): If true, validation should include warnings. (default False)


    """
    check_for_warnings = get_option(options, base_constants.CHECK_FOR_WARNINGS, False)
    display_name = events.name
    error_handler = ErrorHandler(check_for_warnings=check_for_warnings)
    issues = []
    if sidecar:
        issues = sidecar.validate(hed_schema, name=sidecar.name, error_handler=error_handler)
    if not check_for_any_errors(issues):
        issues += events.validate(hed_schema, name=events.name, error_handler=error_handler)
    if issues:
        data = get_printable_issue_string(issues, title="Event file errors:")
        file_name = generate_filename(display_name, name_suffix='_validation_errors',
                                      extension='.txt', append_datetime=True)
        category = 'warning'
        msg = f"Events file {display_name} had validation errors"
    else:
        data = ''
        file_name = display_name
        category = 'success'
        msg = f"Events file {display_name} did not have validation errors"

    return {base_constants.COMMAND: base_constants.COMMAND_VALIDATE, base_constants.COMMAND_TARGET: 'events',
            'data': data, "output_display_name": file_name,
            base_constants.SCHEMA_VERSION: hedschema.get_schema_versions(hed_schema, as_string=True),
            base_constants.MSG_CATEGORY: category, base_constants.MSG: msg}


def validate_query(hed_schema, query):
    """ Validate the query and return the results.

    Args:
        hed_schema (HedSchema, or HedSchemaGroup): Schema or schemas used to validate the query.
        query (str):  A str representing the query.

    Returns
        dict: A dictionary containing results of validation in standard format.

    """

    if not query:
        data = "Empty query could not be processed."
        category = 'warning'
        msg = f"Empty query could not be processed"
    else:
        data = ''
        category = 'success'
        msg = f"Query had no validation errors"

    return {base_constants.COMMAND: base_constants.COMMAND_VALIDATE, base_constants.COMMAND_TARGET: 'query',
            'data': data, base_constants.SCHEMA_VERSION: hedschema.get_schema_versions(hed_schema, as_string=True),
            base_constants.MSG_CATEGORY: category, base_constants.MSG: msg}
