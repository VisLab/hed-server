"""
Handles the routes for the HED web application.
"""

import json

from flask import Blueprint, Response, current_app, jsonify, render_template, request
from hed import schema as hedschema
from werkzeug.utils import secure_filename

from hedweb.columns import get_columns_request
from hedweb.constants import base_constants as bc
from hedweb.constants import file_constants, page_constants, route_constants
from hedweb.event_operations import EventOperations
from hedweb.process_form import ProcessForm
from hedweb.process_service import ProcessServices
from hedweb.schema_operations import SchemaOperations
from hedweb.sidecar_operations import SidecarOperations
from hedweb.spreadsheet_operations import SpreadsheetOperations
from hedweb.string_operations import StringOperations
from hedweb.web_util import (
    convert_hed_versions,
    get_exception_message,
    get_parsed_name,
    handle_error,
    handle_http_error,
    package_results,
)

app_config = current_app.config
route_blueprint = Blueprint(route_constants.ROUTE_BLUEPRINT, __name__)


@route_blueprint.route("/columns_info_results", strict_slashes=False, methods=["POST"])
def columns_info_results() -> str:
    """Process columns info request and return results as a JSON string.
    Returns:
        str: A serialized JSON string containing the columns information.
    """
    try:
        if request.method == "POST":
            columns_info = get_columns_request(request)
            return jsonify(columns_info)
        return jsonify({"message": "Method not allowed."}), 405
    except Exception as ex:
        return get_exception_message(ex)


@route_blueprint.route(
    route_constants.EVENTS_SUBMIT_ROUTE, strict_slashes=False, methods=["POST"]
)
def events_results() -> "Response":
    """Process events form submission and return results.

    Returns:
        Response: The response appropriate to the request.

    Notes:
        The response depends on the request:
        - validation: text file with validation errors
        - assemble:  an assembled events file containing assembled events.
        - generate:  a JSON sidecar generated from the events file.

    """

    try:
        parameters = ProcessForm.get_input_from_form(request)
        proc_events = EventOperations(parameters)
        a = proc_events.process()
        return package_results(a)
    except Exception as ex:
        return handle_http_error(ex)


@route_blueprint.route(
    route_constants.SCHEMAS_SUBMIT_ROUTE, strict_slashes=False, methods=["POST"]
)
def schemas_results() -> "Response":
    """Process schema form submission and return results.

    Returns:
        Response: The response appropriate to the request.

    Notes:
        The response depends on the request:
        - validation: text file with validation errors
        - convert:  text file with converted schema.

    """
    parameters = {}
    try:
        parameters = ProcessForm.get_input_from_form(request)
        proc_schemas = SchemaOperations(parameters)
        a = proc_schemas.process()
        return jsonify(a)
    except Exception as ex:
        return jsonify(get_exception_message(ex))


@route_blueprint.route(route_constants.SCHEMA_VERSION_ROUTE, methods=["POST"])
def schema_version_results() -> str:
    """Return the version of the schema as a JSON string.

    Returns:
        str: A serialized JSON string containing the version of the schema.

    """

    try:
        hed_info = {}
        if bc.SCHEMA_PATH in request.files:
            f = request.files[bc.SCHEMA_PATH]
            name, extension = get_parsed_name(secure_filename(f.filename))
            hed_schema = hedschema.from_string(
                f.stream.read(file_constants.BYTE_LIMIT).decode("utf-8"),
                schema_format=extension,
            )
            hed_info[bc.SCHEMA_VERSION] = hed_schema.get_formatted_version()
        return json.dumps(hed_info)
    except Exception as ex:
        return handle_error(ex)


@route_blueprint.route(route_constants.SCHEMA_VERSIONS_ROUTE, methods=["GET"])
def schema_versions_results() -> str:
    """Return serialized JSON string with HED versions.

    Returns:
        str: A serialized JSON string containing a list of the HED versions.

    """

    try:
        hedschema.cache_xml_versions()
        hed_base = convert_hed_versions(
            hedschema.get_hed_versions(library_name="all", check_prerelease=False)
        )
        include_prereleases = (
            request.args.get("include_prereleases", "false").lower() == "true"
        )
        if include_prereleases:
            hed_pre = convert_hed_versions(
                hedschema.get_hed_versions(library_name="all", check_prerelease=True)
            )
            prereleases = [
                version + " (prerelease)"
                for version in hed_pre
                if version not in hed_base
            ]
            hed_base.extend(prereleases)
        return jsonify({bc.SCHEMA_VERSION_LIST: hed_base})
    except Exception as ex:
        return handle_error(ex)


@route_blueprint.route(
    route_constants.SERVICES_SUBMIT_ROUTE, strict_slashes=False, methods=["POST"]
)
def services_results() -> str:
    """Perform the requested web service and return the results in JSON.

    Returns:
        str: A serialized JSON string containing processed information.

    """

    try:
        arguments = ProcessServices.set_input_from_request(request)
        response = ProcessServices.process(arguments)
        return json.dumps(response)
    except Exception as ex:
        errors = handle_error(ex, return_as_str=False)
        response = {
            "error_type": errors.get("error_type", "Unknown error type"),
            "error_msg": errors.get("message", "Unknown failure"),
        }
        return json.dumps(response)


@route_blueprint.route(
    route_constants.SIDECARS_SUBMIT_ROUTE, strict_slashes=False, methods=["POST"]
)
def sidecars_results() -> "Response":
    """Process sidecar form submission and return results.

    Returns:
        Response: The response appropriate to the request.

    Notes:
        The response depends on the request:
        - validation: text file with validation errors
        - convert:  converted sidecar.
        - extract:  4-column spreadsheets.
        - merge:  a merged sidecar.

    """

    try:
        parameters = ProcessForm.get_input_from_form(request)
        proc_sidecars = SidecarOperations(parameters)
        a = proc_sidecars.process()
        b = package_results(a)
        return b
        # return package_results(a)
    except Exception as ex:
        return handle_http_error(ex)


@route_blueprint.route(
    route_constants.SPREADSHEETS_SUBMIT_ROUTE, strict_slashes=False, methods=["POST"]
)
def spreadsheets_results() -> "Response":
    """Process the spreadsheets in the form and return results.

    Returns:
        Response: The response appropriate to the request.

    Notes:
        The response depends on the request:
        - validation: text file with validation errors
        - convert:  converted spreadsheets.

    """
    try:
        parameters = ProcessForm.get_input_from_form(request)
        proc_spreadsheets = SpreadsheetOperations(parameters)
        a = proc_spreadsheets.process()
        response = package_results(a)
        return response
    except Exception as ex:
        return handle_http_error(ex)


@route_blueprint.route(
    route_constants.STRINGS_SUBMIT_ROUTE, strict_slashes=False, methods=["GET", "POST"]
)
def strings_results() -> str:
    """Process string entered in a form text box.

    Returns:
        Response: The response appropriate to the request.

    Notes:
        The response depends on the request, but appears in text box.
        - validation: validation errors
        - convert:  converted string.

    """
    try:
        parameters = ProcessForm.get_input_from_form(request)
        proc_strings = StringOperations(parameters)
        a = proc_strings.process()
        return json.dumps(a)
    except Exception as ex:
        return handle_error(ex)


@route_blueprint.route(
    route_constants.EVENTS_ROUTE, strict_slashes=False, methods=["GET"]
)
def render_events_form() -> str:
    """Form for BIDS event file (with JSON sidecar) processing.

    Returns:
       str: A rendered template for the events form.

    """
    ver = app_config["VERSIONS"]
    return render_template(
        page_constants.EVENTS_PAGE,
        tool_ver=ver["tool_ver"],
        tool_date=ver["tool_date"],
        web_ver=ver["web_ver"],
        web_date=ver["web_date"],
    )


@route_blueprint.route(
    route_constants.HED_TOOLS_HOME_ROUTE, strict_slashes=False, methods=["GET"]
)
def render_home_page() -> str:
    """The home page.

    Returns:
        str: A rendered template for the home page.

    """
    ver = app_config["VERSIONS"]
    return render_template(
        page_constants.HED_TOOLS_HOME_PAGE,
        tool_ver=ver["tool_ver"],
        tool_date=ver["tool_date"],
        web_ver=ver["web_ver"],
        web_date=ver["web_date"],
    )


@route_blueprint.route(
    route_constants.SCHEMAS_ROUTE, strict_slashes=False, methods=["GET"]
)
def render_schemas_form() -> str:
    """The schema processing form.

    Returns:
        str: A rendered template for the schema processing form.

    """
    ver = app_config["VERSIONS"]
    return render_template(
        page_constants.SCHEMAS_PAGE,
        tool_ver=ver["tool_ver"],
        tool_date=ver["tool_date"],
        web_ver=ver["web_ver"],
        web_date=ver["web_date"],
    )


@route_blueprint.route(
    route_constants.SERVICES_ROUTE, strict_slashes=False, methods=["GET"]
)
def render_services_form() -> str:
    """Landing page for HED hedweb services.

    Returns:
        str: A dummy rendered template so that the service can get a csrf token.

    """
    ver = app_config["VERSIONS"]
    return render_template(
        page_constants.SERVICES_PAGE,
        tool_ver=ver["tool_ver"],
        tool_date=ver["tool_date"],
        web_ver=ver["web_ver"],
        web_date=ver["web_date"],
    )


@route_blueprint.route(
    route_constants.SIDECARS_ROUTE, strict_slashes=False, methods=["GET"]
)
def render_sidecars_form() -> str:
    """The sidecar form.

    Returns:
        str: A rendered template for the sidecar form.

    """
    ver = app_config["VERSIONS"]
    return render_template(
        page_constants.SIDECARS_PAGE,
        tool_ver=ver["tool_ver"],
        tool_date=ver["tool_date"],
        web_ver=ver["web_ver"],
        web_date=ver["web_date"],
    )


@route_blueprint.route(
    route_constants.SPREADSHEETS_ROUTE, strict_slashes=False, methods=["GET"]
)
def render_spreadsheets_form() -> str:
    """The spreadsheets form.

    Returns:
        str: A rendered template for the spreadsheets form.

    """
    ver = app_config["VERSIONS"]
    return render_template(
        page_constants.SPREADSHEETS_PAGE,
        tool_ver=ver["tool_ver"],
        tool_date=ver["tool_date"],
        web_ver=ver["web_ver"],
        web_date=ver["web_date"],
    )


@route_blueprint.route(
    route_constants.STRINGS_ROUTE, strict_slashes=False, methods=["GET"]
)
def render_strings_form() -> str:
    """The HED string form.

    Returns:
        str: A rendered template for the HED string form.

    """
    ver = app_config["VERSIONS"]
    return render_template(
        page_constants.STRINGS_PAGE,
        tool_ver=ver["tool_ver"],
        tool_date=ver["tool_date"],
        web_ver=ver["web_ver"],
        web_date=ver["web_date"],
    )
