"""
Performs operations on tabular data files using metadata from relevant sidecars if available.
"""

import json
from io import StringIO

import pandas as pd
from hed import schema as hedschema
from hed.errors import ErrorHandler, HedFileError, get_printable_issue_string
from hed.errors.error_reporter import check_for_any_errors
from hed.models.definition_dict import DefinitionDict
from hed.models.query_service import get_query_handlers, search_hed_objs
from hed.models.tabular_input import TabularInput
from hed.tools.analysis.event_checker import EventsChecker
from hed.tools.analysis.event_manager import EventManager
from hed.tools.analysis.hed_tag_manager import HedTagManager
from hed.tools.analysis.tabular_summary import TabularSummary
from remodeler.dispatcher import Dispatcher
from remodeler.remodeler_validator import RemodelerValidator

from hedweb.base_operations import BaseOperations
from hedweb.constants import base_constants as bc
from hedweb.web_util import generate_filename, get_schema_versions


class EventOperations(BaseOperations):
    """Class to perform operations on events files."""

    def __init__(self, arguments=None):
        """Construct a ProcessEvents object to handle events form requests.

        Parameters:
             arguments (dict): Dictionary with parameters extracted from form or service

        """
        self.schema = None
        self.events = None
        self.command = None
        self.append_assembled = False
        self.check_for_warnings = False
        self.columns_skip = []
        self.columns_value = []
        self.expand_defs = False
        self.include_context = False
        self.include_summaries = False
        self.limit_errors = False
        self.queries = None
        self.query_names = None
        self.remodel_operations = None
        self.remove_types = False
        self.replace_defs = False
        self.sidecar = None
        self.show_details = False
        if arguments:
            self.set_input_from_dict(arguments)

    def process(self) -> dict:
        """Perform the requested action for the events file and its sidecar.

        Returns:
            dict: A dictionary of results in the standard results format.

        Raises:
            HedFileError: If the schema was not valid.
            HedFileError:  If the command was not found or the input arguments were not valid.

        """
        if not self.command:
            raise HedFileError("MissingCommand", "Command is missing", "")
        elif (
            self.command == bc.COMMAND_GENERATE_SIDECAR
            or self.command == bc.COMMAND_REMODEL
        ):
            pass
        elif not self.schema or not isinstance(
            self.schema,
            (hedschema.hed_schema.HedSchema, hedschema.hed_schema_group.HedSchemaGroup),
        ):
            raise HedFileError(
                "BadHedSchema",
                "Please provide a valid HedSchema for event processing",
                "",
            )

        if not self.events or not isinstance(self.events, TabularInput):
            raise HedFileError(
                "InvalidEventsFile",
                "An events file was not given or could not be read",
                "",
            )
        if self.command == bc.COMMAND_VALIDATE:
            results = self.validate()
        elif self.command == bc.COMMAND_CHECK_QUALITY:
            results = self.check_quality()
        elif self.command == bc.COMMAND_SEARCH:
            results = self.search()
        elif self.command == bc.COMMAND_ASSEMBLE:
            results = self.assemble()
        elif self.command == bc.COMMAND_GENERATE_SIDECAR:
            results = self.generate_sidecar()
        elif self.command == bc.COMMAND_REMODEL:
            results = self.remodel()
        else:
            raise HedFileError(
                "UnknownEventsProcessingMethod",
                f"Command {self.command} is missing or invalid",
                "",
            )
        return results

    def assemble(self) -> dict:
        """Create a tabular file with the original positions in first column and a HED column.


        Returns:
            dict: A dictionary of results in standard format including either the assembled events string or errors.

        Notes:
            options include columns_included and expand_defs.
        """

        self.check_for_warnings = False
        results = self.validate()
        if results["data"]:
            results["data"] = results["data"]
            return results
        hed_objs, definitions = self.get_hed_objs()
        data = [str(obj) if obj is not None else "" for obj in hed_objs]
        if self.append_assembled:
            df = self.events.dataframe
            df["HedAssembled"] = data
            with StringIO() as output:
                df.to_csv(output, sep="\t", index=False, header=True)
                data = output.getvalue()  # Retrieve the written string
        display_name = self.events.name
        file_name = generate_filename(
            display_name,
            name_suffix="_expanded",
            extension=".tsv",
            append_datetime=True,
        )
        return {
            bc.COMMAND: bc.COMMAND_ASSEMBLE,
            bc.COMMAND_TARGET: "events",
            "data": data,
            "output_display_name": file_name,
            "definitions": DefinitionDict.get_as_strings(definitions),
            "schema_version": self.schema.get_formatted_version(),
            "msg_category": "success",
            "msg": "Events file successfully expanded",
        }

    def check_quality(self) -> dict:
        """Check the quality of the HED annotations for an events file.

        Returns:
            dict: A dictionary of results in standard format including either the assembled events string or errors.

        Notes: The options for this are
            - limit_errors (bool):  If True, report at most 2 errors of each type
            - show_details (bool): If True, a detailed breakdown of the event annotation is displayed with error.

        """
        # Make sure that the events file is actually valid before checking quality
        self.check_for_warnings = False
        display_name = self.events.name
        results = self.validate()
        if results["data"]:
            results["data"] = (
                "Events file had validation issues, so quality check not performed...\n"
                + results["data"]
            )
            return results

        checker = EventsChecker(self.schema, self.events, display_name)
        issues = checker.validate_event_tags()
        file_name = generate_filename(
            display_name, name_suffix="_quality", extension=".txt", append_datetime=True
        )
        if issues:
            num_issues = str(len(issues))
            title = "Annotation quality errors: Total issues: " + num_issues
            if self.limit_errors:
                issues, counts = ErrorHandler.filter_issues_by_count(issues, 2)
                count_str = [f"{code}: {count}" for code, count in counts.items()]
                title = (
                    title
                    + " (Only 2 errors of each type displayed)\n"
                    + "\n".join(count_str)
                )
            if self.show_details:
                checker.insert_issue_details(issues)
            data = get_printable_issue_string(
                issues, title=title, show_details=self.show_details
            )
            msg_category = "warning"
            msg = f"File {display_name} had annotation {num_issues} quality issues"
        else:
            data = ""
            file_name = display_name
            msg_category = "success"
            msg = f"File {display_name} did not have HED annotation quality issues"

        return {
            bc.COMMAND: bc.COMMAND_CHECK_QUALITY,
            bc.COMMAND_TARGET: "events",
            "data": data,
            "output_display_name": file_name,
            "msg_category": msg_category,
            "msg": msg,
        }

    def generate_sidecar(self) -> dict:
        """Generate a JSON sidecar template from a BIDS-style events file.

        Returns:
            dict: A dictionary of results in standard format including either the generated sidecar string or errors.

        Notes: Options are the columns selected. If None, all columns are used.

        """
        display_name = self.events.name
        if self.columns_skip and self.columns_value:
            overlap = set(self.columns_skip).intersection(set(self.columns_value))
            if overlap:
                return {
                    bc.COMMAND: bc.COMMAND_GENERATE_SIDECAR,
                    bc.COMMAND_TARGET: "events",
                    "data": f"Skipped and value column names have these names in common: {str(overlap)}",
                    "output_display_name": generate_filename(
                        display_name,
                        name_suffix="sidecar_generation_issues",
                        extension=".txt",
                        append_datetime=True,
                    ),
                    bc.MSG_CATEGORY: "warning",
                    bc.MSG: "Cannot generate sidecar because skipped and value column names overlap.",
                }
        tab_sum = TabularSummary(
            value_cols=self.columns_value, skip_cols=self.columns_skip
        )
        tab_sum.update(self.events.dataframe)
        hed_dict = tab_sum.extract_sidecar_template()
        file_name = generate_filename(
            display_name,
            name_suffix="_generated",
            extension=".json",
            append_datetime=True,
        )
        return {
            bc.COMMAND: bc.COMMAND_GENERATE_SIDECAR,
            bc.COMMAND_TARGET: "events",
            "data": json.dumps(hed_dict, indent=4),
            "output_display_name": file_name,
            "msg_category": "success",
            "msg": "JSON sidecar generation from event file complete",
        }

    def get_hed_objs(self) -> tuple[list, DefinitionDict]:
        """Return the assembled objects and applicable definitions.

        Returns:
          tuple[list, DefinitionDict]: A tuple containing a list of HED objects and a DefinitionDict of definitions.
        """
        definitions = self.events.get_def_dict(self.schema)
        event_manager = EventManager(self.events, self.schema)
        if self.remove_types:
            types = ["Condition-variable", "Task"]
        else:
            types = []
        tag_manager = HedTagManager(event_manager, types)
        hed_objs = tag_manager.get_hed_objs(self.include_context, self.replace_defs)
        return hed_objs, definitions

    def remodel(self) -> dict:
        """Remodel a given events file.

        Returns:
            dict: A dictionary pointing to results or errors.

        Raises:
            HedFileError: If the remodeling operations were not valid.

        Notes: The options for this are
            - include_summaries (bool):  If true and summaries exist, package event file and summaries in a zip file.

        """

        display_name = self.events.name
        if not self.remodel_operations:
            raise HedFileError(
                "RemodelingOperationsMissing",
                "Must supply remodeling operations for remodeling",
                "",
            )
        remodel_name = self.remodel_operations["name"]
        operations = self.remodel_operations["operations"]
        validator = RemodelerValidator()
        errors = validator.validate(operations)
        if errors:
            issue_str = "\n".join(errors)
            file_name = generate_filename(
                remodel_name,
                name_suffix="_operation_parse_errors",
                extension=".txt",
                append_datetime=True,
            )
            return {
                bc.COMMAND: bc.COMMAND_REMODEL,
                bc.COMMAND_TARGET: "events",
                "data": issue_str,
                "output_display_name": file_name,
                "msg_category": "warning",
                "msg": f"Remodeling operation list for {display_name} had validation issues",
            }
        df = self.events.dataframe
        dispatch = Dispatcher(operations, data_root=None, hed_versions=self.schema)

        for operation in dispatch.parsed_ops:
            df = dispatch.prep_data(df)
            df = operation.do_op(dispatch, df, display_name, sidecar=self.sidecar)
            df = dispatch.post_proc_data(df)
        data = df.to_csv(None, sep="\t", index=False, header=True, lineterminator="\n")
        name_suffix = f"_remodeled_by_{remodel_name}"
        file_name = generate_filename(
            display_name,
            name_suffix=name_suffix,
            extension=".tsv",
            append_datetime=True,
        )
        output_name = file_name
        response = {
            bc.COMMAND: bc.COMMAND_REMODEL,
            bc.COMMAND_TARGET: "events",
            "data": "",
            "output_display_name": output_name,
            bc.SCHEMA_VERSION: get_schema_versions(self.schema),
            bc.MSG_CATEGORY: "success",
            bc.MSG: f"Command parsing for {display_name} remodeling was successful",
        }
        if dispatch.summary_dicts and self.include_summaries:
            file_list = dispatch.get_summaries()
            file_list.append(
                {
                    "file_name": output_name,
                    "file_format": ".tsv",
                    "file_type": "tabular",
                    "content": data,
                }
            )
            response[bc.FILE_LIST] = file_list
            response[bc.ZIP_NAME] = generate_filename(
                display_name,
                name_suffix=name_suffix + "_zip",
                extension=".zip",
                append_datetime=True,
            )
        else:
            response["data"] = data
        return response

    def search(self) -> dict:
        """Create a three-column tsv file with event number, matched string, and assembled strings for matched events.

        Returns:
            dict: A dictionary pointing to results or errors.

        Notes:  The options for this are
            columns_included (list):  A list of column names of columns to include.
            expand_defs (bool): If True, expand the definitions in the assembled HED. Otherwise, shrink definitions.

        """
        # TODO:  This needs to handle expand_defs, versus replace_defs.
        display_name = self.events.name
        queries, query_names, issues = get_query_handlers(
            self.queries, self.query_names
        )
        if issues:
            return {
                bc.COMMAND: bc.COMMAND_SEARCH,
                bc.COMMAND_TARGET: "events",
                "data": "Query errors:\n" + "\n".join(issues),
                "output_display_name": generate_filename(
                    display_name,
                    name_suffix="query_validation_issues",
                    extension=".txt",
                    append_datetime=True,
                ),
                bc.SCHEMA_VERSION: get_schema_versions(self.schema),
                bc.MSG_CATEGORY: "warning",
                bc.MSG: "Queries had validation issues",
            }
        self.check_for_warnings = False
        results = self.validate()
        if results["data"]:
            return results
        hed_objs, definitions = self.get_hed_objs()
        df_factors = search_hed_objs(hed_objs, queries, query_names=query_names)
        if self.append_assembled:
            df = pd.concat([self.events.dataframe, df_factors], axis=1)
            df = df.loc[:, ~df.columns.duplicated(keep="last")]
            data = df.to_csv(
                None, sep="\t", index=False, header=True, lineterminator="\n"
            )
        else:
            data = df_factors.to_csv(
                None, sep="\t", index=False, header=True, lineterminator="\n"
            )
        file_name = generate_filename(
            display_name, name_suffix="_queries", extension=".tsv", append_datetime=True
        )
        return {
            bc.COMMAND: bc.COMMAND_SEARCH,
            bc.COMMAND_TARGET: "events",
            "data": data,
            "definitions": DefinitionDict.get_as_strings(definitions),
            "output_display_name": file_name,
            "schema_version": self.schema.get_formatted_version(),
            bc.MSG_CATEGORY: "success",
            bc.MSG: f"Successfully made {len(self.queries)} queries for {display_name}",
        }

    def validate(self) -> dict:
        """Validate the events tabular input object and return the results.

        Returns:
            dict: A dictionary containing results of validation in standard format.

        Notes: The dictionary of options includes the following.
            - check_for_warnings (bool): If true, validation should include warnings. (default False)

        """
        display_name = self.events.name
        if self.events.dataframe.empty:
            return {
                bc.COMMAND: bc.COMMAND_CHECK_QUALITY,
                bc.COMMAND_TARGET: "events",
                "data": "No tsv data to process",
                "output_display_name": display_name,
                "msg_category": "warning",
                "msg": f"File {display_name} had no data to process",
            }
        error_handler = ErrorHandler(check_for_warnings=self.check_for_warnings)
        issues = []
        if self.sidecar:
            issues = self.sidecar.validate(
                self.schema, name=self.sidecar.name, error_handler=error_handler
            )
        if not check_for_any_errors(issues):
            issues += self.events.validate(
                self.schema, name=self.events.name, error_handler=error_handler
            )
        if issues:
            num_errors = len(issues)
            title = f"File errors for {display_name}: {num_errors} Total errors"
            if self.limit_errors:
                issues, counts = ErrorHandler.filter_issues_by_count(issues, 2)
                count_str = [f"{code}: {count}" for code, count in counts.items()]
                title = (
                    title
                    + " (Only 2 errors of each type displayed)\n"
                    + "\n".join(count_str)
                )
            data = get_printable_issue_string(issues, title=title)
            file_name = generate_filename(
                display_name,
                name_suffix="_validation_issues",
                extension=".txt",
                append_datetime=True,
            )
            category = "warning"
            msg = f"File {display_name} had  {num_errors} validation issues"
        else:
            data = ""
            file_name = display_name
            category = "success"
            msg = f"File {display_name} did not have validation issues"

        return {
            bc.COMMAND: bc.COMMAND_VALIDATE,
            bc.COMMAND_TARGET: "events",
            "data": data,
            "output_display_name": file_name,
            bc.SCHEMA_VERSION: get_schema_versions(self.schema),
            bc.MSG_CATEGORY: category,
            bc.MSG: msg,
        }
