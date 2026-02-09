"""
Handles processing of service requests in a standardized way.
"""

import io
import json
import os

from flask import current_app
from hed import schema as hedschema
from hed.errors import HedFileError
from hed.models.hed_string import HedString
from hed.models.sidecar import Sidecar
from hed.models.spreadsheet_input import SpreadsheetInput
from hed.models.tabular_input import TabularInput
from hed.tools.analysis.annotation_util import strs_to_sidecar

from hedweb.base_operations import BaseOperations
from hedweb.constants import base_constants as bc
from hedweb.event_operations import EventOperations
from hedweb.schema_operations import SchemaOperations
from hedweb.sidecar_operations import SidecarOperations
from hedweb.spreadsheet_operations import SpreadsheetOperations
from hedweb.string_operations import StringOperations


def normalize_boolean(value, default=False):
    """Convert various representations of boolean values to actual booleans.

    Parameters:
        value: The value to normalize (can be bool, str, int, etc.)
        default: The default value if value is None or cannot be converted

    Returns:
        bool: The normalized boolean value
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "on", "1", "yes")
    if isinstance(value, int):
        return bool(value)
    return default


class ProcessServices:
    """A class to process service requests and return results in a standard format."""

    def __init__(self):
        pass

    @staticmethod
    def set_input_from_request(request) -> dict:
        """Get a dictionary of input from a service request.

        Parameters:
            request (Request): A Request object containing user data for the service request.

        Returns:
            dict: A dictionary containing input arguments for calling the service request.
        """
        form_data = request.data
        form_string = form_data.decode()
        service_request = json.loads(form_string)
        arguments = ProcessServices.get_service_info(service_request)
        arguments[bc.SCHEMA] = ProcessServices.get_input_schema(service_request)
        ProcessServices.set_parameters(arguments, service_request)
        ProcessServices.set_remodel_parameters(arguments, service_request)
        ProcessServices.set_definitions(arguments, service_request)
        ProcessServices.set_sidecar(arguments, service_request)
        ProcessServices.set_input_objects(arguments, service_request)
        ProcessServices.set_queries(arguments, service_request)
        return arguments

    @staticmethod
    def set_parameters(arguments, params):
        """Update arguments with the columns that requested for the service.

        Parameters:
            arguments (dict):  A dictionary with the extracted parameters that are to be processed.
            params (dict): The service request dictionary extracted from the Request object.
        """
        # Column parameters
        arguments[bc.REQUEST_TYPE] = bc.FROM_SERVICE
        arguments[bc.COLUMNS_CATEGORICAL] = ProcessServices.get_list(
            bc.COLUMNS_CATEGORICAL, params
        )
        arguments[bc.COLUMNS_VALUE] = ProcessServices.get_list(bc.COLUMNS_VALUE, params)
        arguments[bc.COLUMNS_SKIP] = ProcessServices.get_list(bc.COLUMNS_SKIP, params)
        arguments[bc.TAG_COLUMNS] = ProcessServices.get_list(bc.TAG_COLUMNS, params)
        arguments[bc.HAS_COLUMN_NAMES] = True

        # Assemble and search parameters
        arguments[bc.INCLUDE_CONTEXT] = params.get(bc.INCLUDE_CONTEXT, False)
        arguments[bc.REMOVE_TYPES_ON] = params.get(bc.REMOVE_TYPES_ON, False)
        arguments[bc.REPLACE_DEFS] = params.get(bc.REPLACE_DEFS, False)
        arguments[bc.EXPAND_DEFS] = params.get(bc.EXPAND_DEFS, False)
        arguments[bc.INCLUDE_DESCRIPTION_TAGS] = params.get(
            bc.INCLUDE_DESCRIPTION_TAGS, False
        )
        arguments[bc.INCLUDE_SUMMARIES] = params.get(bc.INCLUDE_SUMMARIES, False)

    @staticmethod
    def get_list(name, params) -> list:
        """Return value in params associated with name as a list.

        Parameters:
            name (str): The name of the parameter to extract from the params dictionary.
            params (dict): A dictionary of the service request values.

        Returns:
            list: A list of values associated with the name in the params dictionary.
        """
        if name not in params or not params[name]:
            return []
        elif isinstance(params[name], str):
            return [params[name]]
        else:
            return params[name]

    @staticmethod
    def set_queries(arguments, params):
        """Update arguments with lists of string queries and query names.

        Parameters:
            arguments (dict):  A dictionary with the extracted parameters that are to be processed.
            params (dict): The service request dictionary extracted from the Request object.
        """
        if bc.QUERIES in params and params[bc.QUERIES]:
            arguments[bc.QUERIES] = params.get(bc.QUERIES, None)
            arguments[bc.QUERY_NAMES] = params.get(bc.QUERY_NAMES, None)

    @staticmethod
    def set_sidecar(arguments, params):
        """Update arguments with the sidecars if there are any.

        Parameters:
            arguments (dict):  A dictionary with the extracted parameters that are to be processed.
            params (dict): The service request dictionary extracted from the Request object.
        """
        sidecar_list = params.get(bc.SIDECAR_STRING, [])
        arguments[bc.SIDECAR] = strs_to_sidecar(sidecar_list)

    @staticmethod
    def set_definitions(arguments, params):
        """Update arguments with the definitions if there are any.

        Parameters:
            arguments (dict):  A dictionary with the extracted parameters that are to be processed.
            params (dict): The service request dictionary extracted from the Request object.
        """
        definition_string = params.get(bc.DEFINITION_STRING, "")
        def_file = None
        if definition_string:
            def_file = io.StringIO(definition_string)

        arguments[bc.DEFINITIONS] = Sidecar(files=def_file).get_def_dict(
            arguments[bc.SCHEMA]
        )

    @staticmethod
    def set_input_objects(arguments, params):
        """Update arguments with the information in the params dictionary.

        Parameters:
            arguments (dict):  A dictionary with the extracted parameters that are to be processed.
            params (dict): A dictionary of the service request values.

        Updates the arguments dictionary with the input objects including events, spreadsheets, schemas or strings.

        """

        schema = arguments.get("schema", None)
        if bc.EVENTS_STRING in params and params[bc.EVENTS_STRING]:
            arguments[bc.EVENTS] = TabularInput(
                file=io.StringIO(params[bc.EVENTS_STRING]),
                sidecar=arguments.get(bc.SIDECAR, None),
                name="Events",
            )
        if bc.SPREADSHEET_STRING in params and params[bc.SPREADSHEET_STRING]:
            arguments[bc.SPREADSHEET] = SpreadsheetInput(
                file=io.StringIO(params[bc.SPREADSHEET_STRING]),
                file_type=".tsv",
                tag_columns=arguments[bc.TAG_COLUMNS],
                has_column_names=True,
                column_prefix_dictionary=None,
                name="spreadsheets.tsv",
            )
        if bc.STRING_LIST in params and params[bc.STRING_LIST]:
            working_list = params[bc.STRING_LIST]
            if isinstance(working_list, str):
                working_list = [working_list]
            s_list = []
            for s in working_list:
                s_list.append(HedString(s, hed_schema=schema))
            arguments[bc.STRING_LIST] = s_list

    @staticmethod
    def set_remodel_parameters(arguments, params):
        """Update arguments with the remodeler information if any.

        Parameters:
            arguments (dict):  A dictionary with the extracted parameters that are to be processed.
            params (dict): The service request dictionary extracted from the Request object.

        Updates the arguments dictionary with the sidecars.

        """

        if bc.REMODEL_STRING in params and params[bc.REMODEL_STRING]:
            arguments[bc.REMODEL_OPERATIONS] = {
                "name": "remodel_commands.json",
                "operations": json.loads(params[bc.REMODEL_STRING]),
            }

    @staticmethod
    def get_service_info(params) -> dict:
        """Get a dictionary with the service request command information filled in.

        Parameters:
            params (dict): A dictionary of the service request values.

        Returns:
            dict: A dictionary with the command, command target and options resolved from the service request.

        """
        service = params.get(bc.SERVICE, "")
        command = service
        command_target = ""
        pieces = service.split("_", 1)
        if command != "get_services" and len(pieces) == 2:
            command = pieces[1]
            command_target = pieces[0]
        has_column_names = True
        expand_defs = params.get(bc.EXPAND_DEFS, False)
        check_for_warnings = params.get(bc.CHECK_FOR_WARNINGS, True)
        include_description_tags = params.get(bc.INCLUDE_DESCRIPTION_TAGS, True)
        include_prereleases = normalize_boolean(
            params.get(bc.INCLUDE_PRERELEASES, False)
        )

        return {
            bc.SERVICE: service,
            bc.COMMAND: command,
            bc.COMMAND_TARGET: command_target,
            bc.HAS_COLUMN_NAMES: has_column_names,
            bc.CHECK_FOR_WARNINGS: check_for_warnings,
            bc.EXPAND_DEFS: expand_defs,
            bc.INCLUDE_DESCRIPTION_TAGS: include_description_tags,
            bc.INCLUDE_PRERELEASES: include_prereleases,
            bc.REQUEST_TYPE: bc.FROM_SERVICE,
        }

    @staticmethod
    def get_input_schema(parameters):
        """Get a HedSchema or HedSchemaGroup object from the parameters.

        Parameters:
            parameters (dict): A dictionary of parameters extracted from the service request.

        """

        the_schema = None
        if bc.SCHEMA_STRING in parameters and parameters[bc.SCHEMA_STRING]:
            the_schema = hedschema.from_string(parameters[bc.SCHEMA_STRING])
        elif bc.SCHEMA_URL in parameters and parameters[bc.SCHEMA_URL]:
            the_schema = hedschema.load_schema(parameters[bc.SCHEMA_URL])
        elif bc.SCHEMA_VERSION in parameters and parameters[bc.SCHEMA_VERSION]:
            # Check if include_prereleases parameter is present and normalize to boolean
            include_prereleases = normalize_boolean(
                parameters.get(bc.INCLUDE_PRERELEASES, False)
            )
            the_schema = hedschema.load_schema_version(
                parameters[bc.SCHEMA_VERSION], check_prerelease=include_prereleases
            )
        return the_schema

    @staticmethod
    def process(arguments) -> dict:
        """Call the desired service processing function and return the results in a standard format.

        Parameters:
            arguments (dict): A dictionary of arguments for the processing resolved from the request.

        Returns:
            dict: A dictionary of results in standard response format to be JSONified.

        """

        response = {
            bc.SERVICE: arguments.get(bc.SERVICE, ""),
            "results": {},
            "error_type": "",
            "error_msg": "",
        }
        if arguments.get(bc.COMMAND, "") == "get_services":
            response["results"] = ProcessServices.get_services_list()
        else:
            proc_obj = ProcessServices.get_process(arguments.get(bc.COMMAND_TARGET, ""))
            if not proc_obj:
                response["error_type"] = "HEDServiceInvalid"
                response["error_msg"] = "Must specify a valid service"
                return response

            proc_obj.set_input_from_dict(arguments)
            response["results"] = proc_obj.process()
        results = response.get("results", {})
        results["software_version"] = current_app.config["VERSIONS"]
        results = ProcessServices.package_spreadsheet(results)
        response["results"] = results
        return response

    @staticmethod
    def get_process(target) -> "BaseOperations":
        """Return the BaseProcess object specific to the target string.

        Parameters:
            target (str): Indicates what type of BaseProcess is needed.

        Returns:
            BaseOperations:  A processing object of a subclass of BaseOperations.

        """
        if target == "events":
            proc_obj = EventOperations()
        elif target == "sidecar":
            proc_obj = SidecarOperations()
        elif target == "spreadsheet":
            proc_obj = SpreadsheetOperations()
        elif target == "strings":
            proc_obj = StringOperations()
        elif target == "schemas":
            proc_obj = SchemaOperations()
        else:
            raise HedFileError(
                "InvalidTargetForProcessing",
                f'Target "{target}" is missing or invalid',
                "",
            )
        return proc_obj

    @staticmethod
    def package_spreadsheet(results) -> dict:
        """Get the transformed results dictionary where spreadsheets are converted to strings.

        Parameters:
            results (dict): The dictionary of results in standardized form returned from processing.

        Returns:
            dict: The results transformed so that all entries are strings.


        """
        if results["msg_category"] == "success" and results.get(bc.SPREADSHEET, ""):
            results[bc.SPREADSHEET] = results[bc.SPREADSHEET].to_csv(file=None)
        elif bc.SPREADSHEET in results:
            del results[bc.SPREADSHEET]
        return results

    @staticmethod
    def get_services_list() -> dict:
        """Get a formatted string describing services using the resources/services.json file

        Returns:
           dict: dictionary in standard form with data as formatted string of services.

        """
        dir_path = os.path.dirname(os.path.realpath(__file__))
        the_path = os.path.join(dir_path, "static/resources/services.json")
        with open(the_path) as f:
            service_info = json.load(f)
        services = service_info["services"]
        meanings = service_info["parameter_meanings"]
        returns = service_info["returns"]
        results = service_info["results"]

        ver = current_app.config["VERSIONS"]
        commit_info = f" Commit: {ver['tool_commit']}" if ver.get("tool_commit") else ""
        date_info = f" Date: {ver['web_date']}" if ver.get("web_date") else ""
        services_string = (
            f"\nServices:\n\tHEDTools version: {ver['tool_ver']}{commit_info}\n"
            f"\tHEDServices version: {ver['web_ver']}{date_info}"
        )
        for service, info in services.items():
            description = info["Description"]
            parameters = ProcessServices.get_parameter_string(info["Parameters"])

            return_string = info["Returns"]
            next_string = f"\n{service}:\n\tDescription: {description}\n{parameters}\n\tReturns: {return_string}\n"
            services_string += next_string

        meanings_string = "\nParameter meanings:\n"
        for string, meaning in meanings.items():
            meanings_string += f"\t{string}: {meaning}\n"

        returns_string = "\nReturn values:\n"
        for return_val, meaning in returns.items():
            returns_string += f"\t{return_val}: {meaning}\n"

        results_string = "\nResults field meanings:\n"
        for result_val, meaning in results.items():
            results_string += f"\t{result_val}: {meaning}\n"
        data = services_string + meanings_string + returns_string + results_string
        return {
            bc.COMMAND: "get_services",
            bc.COMMAND_TARGET: "",
            "data": data,
            "output_display_name": "",
            bc.SCHEMA_VERSION: "",
            "msg_category": "success",
            "msg": "List of available services and their meanings",
        }

    @staticmethod
    def get_parameter_string(params) -> str:
        """Get a formatted string describing the parameters for a service.
        Parameters:
            params (list): A list of parameters for the service.
        Returns:
            str: A formatted string describing the parameters.
        """
        if not params:
            return "\tParameters: []"
        param_list = []
        for p in params:
            if isinstance(p, list):
                param_list.append(" or ".join(p))
            else:
                param_list.append(p)

        return "\tParameters:\n\t\t" + "\n\t\t".join(param_list)
