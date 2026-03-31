import io
import os
import unittest

from werkzeug.test import create_environ
from werkzeug.wrappers import Request, Response

from hedweb.constants import base_constants as bc
from hedweb.constants import file_constants
from tests.test_web_base import TestWebBase


class Test(TestWebBase):
    def test_convert_hed_versions(self):
        from hedweb.web_util import convert_hed_versions

        no_none = {"score": ["1.0.0", "2.0.0"]}
        no_none_list = convert_hed_versions(no_none)
        self.assertTrue(no_none_list == ["score_1.0.0", "score_2.0.0"])
        just_none = {None: ["8.0.0", "8.1.0"]}
        just_none_list = convert_hed_versions(just_none)
        self.assertTrue(just_none_list == ["8.0.0", "8.1.0"])
        just_blank = {"": ["9.0.0", "9.1.0"]}
        just_blank_list = convert_hed_versions(just_blank)
        self.assertTrue(just_blank_list == ["_9.0.0", "_9.1.0"])
        test_all = {"score": ["1.0.0", "2.0.0"], None: ["8.0.0", "8.1.0"]}
        test_all_list = convert_hed_versions(test_all)
        self.assertTrue(test_all_list == ["8.0.0", "8.1.0", "score_1.0.0", "score_2.0.0"])

    def test_form_has_file(self):
        from hedweb.web_util import form_has_file

        with self.app.test as _:
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/bids_events.json")
            with open(sidecar_path, "rb") as fp:
                environ = create_environ(data={"sidecar_file": fp})

            request = Request(environ)
            self.assertTrue(
                form_has_file(request.files, "sidecar_file"),
                "Form has file when no extension requirements",
            )
            self.assertFalse(
                form_has_file(request.files, "temp"),
                "Form does not have file when form name is wrong",
            )
            self.assertFalse(
                form_has_file(request.files, "sidecar_file", file_constants.SPREADSHEET_EXTENSIONS),
                "Form does not have file when extension is wrong",
            )
            self.assertTrue(
                form_has_file(request.files, "sidecar_file", [".json"]),
                "Form has file when extensions and form field match",
            )

    def test_form_has_option(self):
        from hedweb.web_util import form_has_option

        with self.app.test as _:
            environ = create_environ(data={bc.CHECK_FOR_WARNINGS: "on"})
            request = Request(environ)
            self.assertTrue(
                form_has_option(request.form, bc.CHECK_FOR_WARNINGS, "on"),
                "Form has the required option when set",
            )
            self.assertFalse(
                form_has_option(request.form, bc.CHECK_FOR_WARNINGS, "off"),
                "Form does not have required option when target value is wrong one",
            )
            self.assertFalse(
                form_has_option(request.form, "blank", "on"),
                "Form does not have required option when option is not in the form",
            )

    def test_form_has_url(self):
        from hedweb.web_util import form_has_url

        with self.app.test as _:
            environ = create_environ(data={bc.SCHEMA_URL: "https://www.google.com/my.json"})
            request = Request(environ)
            self.assertTrue(
                form_has_url(request.form, bc.SCHEMA_URL),
                "Form has a URL that is specified",
            )
            self.assertFalse(
                form_has_url(request.form, "temp"),
                "Form does not have a field that is not specified",
            )
            self.assertFalse(
                form_has_url(request.form, bc.SCHEMA_URL, file_constants.SPREADSHEET_EXTENSIONS),
                "Form does not URL with the wrong extension",
            )

    def test_generate_download_file_from_text(self):
        from hedweb.web_util import generate_download_file_from_text

        with self.app.test_request_context():
            the_text = "The quick brown fox\nIs too slow"
            response = generate_download_file_from_text(
                {"data": the_text, "msg_category": "success", "msg": "Successful"}
            )
            self.assertIsInstance(
                response,
                Response,
                "Generate_response_download_file_from_text returns a response for string",
            )
            self.assertEqual(
                200,
                response.status_code,
                "Generate_response_download_file_from_text has status code 200 for string",
            )
            header_content = dict(response.headers)
            self.assertEqual("success", header_content["Category"], "The msg_category is success")
            self.assertEqual(
                'attachment; filename="download.txt"',
                header_content["Content-Disposition"],
                "generate_download_file has the correct attachment file name",
            )

    def test_generate_download_spreadsheet_excel(self):
        with self.app.test_request_context():
            from hed.models import SpreadsheetInput

            from hedweb.web_util import generate_download_spreadsheet

            spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/ExcelOneSheet.xlsx")

            spreadsheet = SpreadsheetInput(
                file=spreadsheet_path,
                file_type=".xlsx",
                tag_columns=[4],
                has_column_names=True,
                column_prefix_dictionary={
                    1: "Attribute/Informational/Label/",
                    3: "Attribute/Informational/Description/",
                },
                name="ExcelOneSheet.xlsx",
            )
            results = {
                bc.SPREADSHEET: spreadsheet,
                bc.OUTPUT_DISPLAY_NAME: "ExcelOneSheetA.xlsx",
                bc.MSG: "Successful download",
                bc.MSG_CATEGORY: "success",
            }
            response = generate_download_spreadsheet(results)
            self.assertIsInstance(
                response,
                Response,
                "generate_download_spreadsheet returns a response for xlsx files",
            )
            headers_dict = dict(response.headers)
            self.assertEqual(
                200,
                response.status_code,
                "generate_download_spreadsheet should return status code 200",
            )
            self.assertEqual(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                response.mimetype,
                "generate_download_spreadsheet should return spreadsheetml for excel files",
            )
            self.assertTrue(
                headers_dict["Content-Disposition"].startswith("attachment; filename="),
                "generate_download_spreadsheet excel should be downloaded as an attachment",
            )

    def test_generate_download_spreadsheet_excel_code(self):
        with self.app.test_request_context():
            from hed.models import SpreadsheetInput

            from hedweb.web_util import generate_download_spreadsheet

            spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/ExcelOneSheet.xlsx")

            spreadsheet = SpreadsheetInput(
                file=spreadsheet_path,
                file_type=".xlsx",
                tag_columns=[4],
                has_column_names=True,
                column_prefix_dictionary={1: "Label/", 3: "Description/"},
                name="ExcelOneSheet.xlsx",
            )
            results = {
                bc.SPREADSHEET: spreadsheet,
                bc.OUTPUT_DISPLAY_NAME: "ExcelOneSheetA.xlsx",
                bc.MSG: "Successful download",
                bc.MSG_CATEGORY: "success",
            }
            response = generate_download_spreadsheet(results)
            self.assertIsInstance(
                response,
                Response,
                "generate_download_spreadsheet returns a response for tsv files",
            )
            headers_dict = dict(response.headers)
            self.assertEqual(
                200,
                response.status_code,
                "generate_download_spreadsheet should return status code 200",
            )
            self.assertEqual(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                response.mimetype,
                "generate_download_spreadsheet should return spreadsheetml for excel files",
            )
            self.assertTrue(
                headers_dict["Content-Disposition"].startswith("attachment; filename="),
                "generate_download_spreadsheet excel should be downloaded as an attachment",
            )

    def test_generate_download_spreadsheet_tsv(self):
        with self.app.test_request_context():
            from hed.models import SpreadsheetInput

            from hedweb.web_util import generate_download_spreadsheet

            spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/LKTEventCodesHED3.tsv")

            spreadsheet = SpreadsheetInput(
                file=spreadsheet_path,
                file_type=".tsv",
                tag_columns=[5],
                has_column_names=True,
                column_prefix_dictionary={
                    2: "Attribute/Informational/Label/",
                    4: "Attribute/Informational/Description/",
                },
                name="LKTEventCodesHED3.tsv",
            )
            results = {
                bc.SPREADSHEET: spreadsheet,
                bc.OUTPUT_DISPLAY_NAME: "LKTEventCodesHED3.tsv",
                bc.MSG: "Successful download",
                bc.MSG_CATEGORY: "success",
            }
            response = generate_download_spreadsheet(results)
            self.assertIsInstance(
                response,
                Response,
                "generate_download_spreadsheet returns a response for tsv files",
            )
            headers_dict = dict(response.headers)
            self.assertEqual(
                200,
                response.status_code,
                "generate_download_spreadsheet should return status code 200",
            )
            self.assertEqual(
                "text/plain charset=utf-8",
                response.mimetype,
                "generate_download_spreadsheet should return text for tsv files",
            )
            self.assertTrue(
                headers_dict["Content-Disposition"].startswith('attachment; filename="'),
                "generate_download_spreadsheet tsv should be downloaded as an attachment",
            )

    def test_generate_file_name(self):
        from hedweb.web_util import generate_filename

        file1 = generate_filename("mybase")
        self.assertEqual(
            file1,
            "mybase",
            "generate_file_name should return the base when other arguments not set",
        )
        file2 = generate_filename("mybase", name_prefix="prefix")
        self.assertEqual(
            file2,
            "prefixmybase",
            "generate_file_name should return correct name when prefix set",
        )
        file3 = generate_filename("mybase", name_prefix="prefix", extension=".json")
        self.assertEqual(
            file3,
            "prefixmybase.json",
            "generate_file_name should return correct name for extension",
        )
        file4 = generate_filename("mybase", name_suffix="suffix")
        self.assertEqual(
            file4,
            "mybasesuffix",
            "generate_file_name should return correct name when suffix set",
        )
        file5 = generate_filename("mybase", name_suffix="suffix", extension=".json")
        self.assertEqual(
            file5,
            "mybasesuffix.json",
            "generate_file_name should return correct name for extension",
        )
        file6 = generate_filename("mybase", name_prefix="prefix", name_suffix="suffix", extension=".json")
        self.assertEqual(
            file6,
            "prefixmybasesuffix.json",
            "generate_file_name should return correct name for all set",
        )
        filename = generate_filename(None, name_prefix=None, name_suffix=None, extension=None)
        self.assertEqual("", filename, "Return empty when all arguments are none")
        filename = generate_filename(None, name_prefix=None, name_suffix=None, extension=".txt")
        self.assertEqual(
            "",
            filename,
            "Return empty when base_name, prefix, and suffix are None, but extension is not",
        )
        filename = generate_filename("c:/temp.json", name_prefix=None, name_suffix=None, extension=".txt")
        self.assertEqual(
            "c_temp.txt",
            filename,
            "Returns stripped base_name + extension when prefix, and suffix are None",
        )
        filename = generate_filename("temp.json", name_prefix="prefix_", name_suffix="_suffix", extension=".txt")
        self.assertEqual(
            "prefix_temp_suffix.txt",
            filename,
            "Return stripped base_name + extension when prefix, and suffix are None",
        )
        filename = generate_filename(None, name_prefix="prefix_", name_suffix="suffix", extension=".txt")
        self.assertEqual("prefix_suffix.txt", filename, "Returns correct string when no base_name")
        filename = generate_filename(
            "event-strategy-v3_task-matchingpennies_events.json",
            name_suffix="_blech",
            extension=".txt",
        )
        self.assertEqual(
            "event-strategy-v3_task-matchingpennies_events_blech.txt",
            filename,
            "Returns correct string when base_name with hyphens",
        )
        filename = generate_filename("HED7.2.0.xml", name_suffix="_blech", extension=".txt")
        self.assertEqual(
            "HED7.2.0_blech.txt",
            filename,
            "Returns correct string when base_name has periods",
        )

    def test_generate_file_name_with_date(self):
        from hedweb.web_util import generate_filename

        file1 = generate_filename("mybase")
        file1t = generate_filename("mybase", append_datetime=True)
        self.assertGreater(
            len(file1t),
            len(file1),
            "generate_file_name generates a longer file when datetime is used.",
        )
        # TODO convert more of these tests.
        # self.assertEqual(file1, "mybase", "generate_file_name should return the base when other arguments not set")
        # file2 = generate_filename('mybase', name_prefix="prefix")
        # self.assertEqual(file2, "prefixmybase", "generate_file_name should return correct name when prefix set")
        # file3 = generate_filename('mybase', name_prefix="prefix", extension=".json")
        # self.assertEqual(file3, "prefixmybase.json", "generate_file_name should return correct name for extension")
        # file4 = generate_filename('mybase', name_suffix="suffix")
        # self.assertEqual(file4, "mybasesuffix", "generate_file_name should return correct name when suffix set")
        # file5 = generate_filename('mybase', name_suffix="suffix", extension=".json")
        # self.assertEqual(file5, "mybasesuffix.json", "generate_file_name should return correct name for extension")
        # file6 = generate_filename('mybase', name_prefix="prefix", name_suffix="suffix", extension=".json")
        # self.assertEqual(file6, "prefixmybasesuffix.json",
        #                  "generate_file_name should return correct name for all set")
        # filename = generate_filename(None, name_prefix=None, name_suffix=None, extension=None)
        # self.assertEqual('', filename, "Return empty when all arguments are none")
        # filename = generate_filename(None, name_prefix=None, name_suffix=None, extension='.txt')
        # self.assertEqual('', filename,
        #                  "Return empty when base_name, prefix, and suffix are None, but extension is not")
        # filename = generate_filename('c:/temp.json', name_prefix=None, name_suffix=None, extension='.txt')
        # self.assertEqual('c_temp.txt', filename,
        #                  "Returns stripped base_name + extension when prefix, and suffix are None")
        # filename = generate_filename('temp.json', name_prefix='prefix_', name_suffix='_suffix', extension='.txt')
        # self.assertEqual('prefix_temp_suffix.txt', filename,
        #                  "Return stripped base_name + extension when prefix, and suffix are None")
        # filename = generate_filename(None, name_prefix='prefix_', name_suffix='suffix', extension='.txt')
        # self.assertEqual('prefix_suffix.txt', filename,
        #                  "Returns correct string when no base_name")
        # filename = generate_filename('event-strategy-v3_task-matchingpennies_events.json',
        #                              name_suffix='_blech', extension='.txt')
        # self.assertEqual('event-strategy-v3_task-matchingpennies_events_blech.txt', filename,
        #                  "Returns correct string when base_name with hyphens")
        # filename = generate_filename('HED7.2.0.xml', name_suffix='_blech', extension='.txt')
        # self.assertEqual('HED7.2.0_blech.txt', filename, "Returns correct string when base_name has periods")

    def test_generate_text_response(self):
        with self.app.test_request_context():
            from hedweb.web_util import generate_text_response

            results = {"data": "testme", bc.MSG: "testing", bc.MSG_CATEGORY: "success"}
            response = generate_text_response(results)
            self.assertIsInstance(response, Response, "generate_download_text_response returns a response")
            headers_dict = dict(response.headers)
            self.assertEqual(
                200,
                response.status_code,
                "generate_download_text_response should return status code 200",
            )
            self.assertEqual(
                "text/plain charset=utf-8",
                response.mimetype,
                "generate_download_download_text_response should return text",
            )
            self.assertEqual(
                results[bc.MSG],
                headers_dict["Message"],
                "generate_download_text_response have the correct message in the response",
            )
            self.assertEqual(
                results["data"],
                response.data.decode("utf-8"),
                "generate_download_text_response have the download text as response data",
            )

    def test_get_hed_schema_from_pull_down_empty(self):
        from hed.errors.exceptions import HedFileError

        from hedweb.web_util import get_hed_schema_from_pull_down

        with self.app.test:
            environ = create_environ(data={})
            request = Request(environ)
            try:
                get_hed_schema_from_pull_down(request)
            except HedFileError:
                pass
            except Exception:
                self.fail("get_hed_schema_from_pull_down threw the wrong exception when data was empty")
            else:
                self.fail("get_hed_schema_from_pull_down should throw a HedFileError exception when data was empty")

    def test_get_hed_schema_from_pull_down_version(self):
        from hed.schema import HedSchema

        from hedweb.web_util import get_hed_schema_from_pull_down

        with self.app.test:
            environ = create_environ(data={bc.SCHEMA_VERSION: "8.0.0"})
            request = Request(environ)
            hed_schema = get_hed_schema_from_pull_down(request)
            self.assertIsInstance(
                hed_schema,
                HedSchema,
                "get_hed_schema_from_pull_down should return a HedSchema object",
            )

    def test_get_hed_schema_from_pull_down_other(self):
        from hed.schema import HedSchema

        from hedweb.web_util import get_hed_schema_from_pull_down

        with self.app.test:
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/HED8.0.0.xml")
            with open(schema_path, "rb") as fp:
                environ = create_environ(
                    data={
                        bc.SCHEMA_VERSION: bc.OTHER_VERSION_OPTION,
                        bc.SCHEMA_PATH: fp,
                    }
                )
            request = Request(environ)
            hed_schema = get_hed_schema_from_pull_down(request)
            self.assertIsInstance(
                hed_schema,
                HedSchema,
                "get_hed_schema_from_pull_down should return a HedSchema object",
            )

    def test_handle_error(self):
        from hed.errors.exceptions import HedExceptions, HedFileError

        from hedweb.web_util import handle_error

        ex = HedFileError(HedExceptions.BAD_PARAMETERS, "This had bad parameters", "my.file")
        output = handle_error(ex)
        self.assertIsInstance(output, str, "handle_error should return a string if return_as_str")
        output1 = handle_error(ex, return_as_str=False)
        self.assertIsInstance(output1, dict, "handle_error should return a dict if not return_as_str")
        self.assertTrue("message" in output1, "handle_error dict should have a message")
        output2 = handle_error(ex, {"mykey": "blech"}, return_as_str=False)
        self.assertTrue("mykey" in output2, "handle_error dict should include passed dictionary")

    def test_handle_http_error(self):
        from hed.errors.exceptions import HedExceptions, HedFileError

        from hedweb.web_util import handle_http_error

        with self.app.test_request_context():
            ex = HedFileError(HedExceptions.BAD_PARAMETERS, "This had bad parameters", "my.file")
            response = handle_http_error(ex)
            headers = dict(response.headers)
            self.assertEqual(
                "error",
                headers["Category"],
                "handle_http_error should have category error",
            )
            self.assertTrue(headers["Message"].startswith(str(HedExceptions.BAD_PARAMETERS)))
            self.assertFalse(response.data, "handle_http_error should have empty data")
            ex = Exception()
            response = handle_http_error(ex)
            headers = dict(response.headers)
            self.assertEqual(
                "error",
                headers["Category"],
                "handle_http_error should have category error",
            )
            self.assertTrue(
                headers["Message"].startswith("Exception"),
                "handle_http_error error message starts with the error_type",
            )
            self.assertFalse(response.data, "handle_http_error should have empty data")

    def test_file_extension_is_valid(self):
        from hedweb.web_util import file_extension_is_valid

        self.assertTrue(
            file_extension_is_valid("my_file.json"), "any extension is valid when accepted_extensions is None"
        )
        self.assertTrue(file_extension_is_valid("my_file.JSON", [".json"]), "comparison should be case-insensitive")
        self.assertTrue(file_extension_is_valid("my_file.tsv", [".tsv", ".txt"]), "tsv should be accepted")
        self.assertFalse(
            file_extension_is_valid("my_file.xlsx", [".tsv", ".txt"]), "xlsx should be rejected for text-only list"
        )
        self.assertFalse(
            file_extension_is_valid("no_extension", [".json"]), "file without extension should be rejected"
        )
        self.assertTrue(file_extension_is_valid("no_extension", [""]), "empty extension accepted when listed")

    def test_filter_issues(self):
        from hed.errors import ErrorSeverity

        from hedweb.web_util import filter_issues

        error_issue = {"code": "TAG_INVALID", "severity": ErrorSeverity.ERROR}
        warning_issue = {"code": "TAG_WARNING", "severity": ErrorSeverity.WARNING}
        issues = [error_issue, warning_issue]

        filtered_errors = filter_issues(issues, check_for_warnings=False)
        self.assertNotIn(warning_issue, filtered_errors, "warning should be filtered when check_for_warnings is False")
        self.assertIn(error_issue, filtered_errors, "error should remain when check_for_warnings is False")

        filtered_all = filter_issues(issues, check_for_warnings=True)
        self.assertEqual(filtered_all, issues, "all issues should be kept when check_for_warnings is True")

        self.assertEqual(filter_issues([], check_for_warnings=False), [], "empty list should stay empty")

    def test_get_parsed_name(self):
        from hedweb.web_util import get_parsed_name

        name, ext = get_parsed_name("my_schema.xml")
        self.assertEqual(name, "my_schema")
        self.assertEqual(ext, ".xml")

        name, ext = get_parsed_name("/some/path/HED8.2.0.xml")
        self.assertEqual(name, "HED8.2.0")
        self.assertEqual(ext, ".xml")

        name, ext = get_parsed_name(
            "https://raw.githubusercontent.com/hed-standard/hed-schemas/main/standard_schema/hedxml/HED8.2.0.xml",
            is_url=True,
        )
        self.assertEqual(name, "HED8.2.0")
        self.assertEqual(ext, ".xml")

        name, ext = get_parsed_name("noextension")
        self.assertEqual(name, "noextension")
        self.assertEqual(ext, "")

    def test_get_schema_versions(self):
        from hed.schema import load_schema_version

        from hedweb.web_util import get_schema_versions

        self.assertEqual(get_schema_versions(None), "", "None schema should return empty string")

        single = load_schema_version("8.2.0")
        self.assertIsInstance(get_schema_versions(single), str)
        self.assertTrue(len(get_schema_versions(single)) > 0)

        group = load_schema_version(["8.2.0", "sc:score_1.0.0"])
        result = get_schema_versions(group)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

        with self.assertRaises(ValueError):
            get_schema_versions("not_a_schema")

    def test_get_option(self):
        from hedweb.web_util import get_option

        options = {"key1": "value1", "key2": "value2"}
        self.assertEqual(get_option(options, "key1", "default"), "value1")
        self.assertEqual(get_option(options, "missing", "default"), "default")
        self.assertEqual(get_option(None, "key1", "fallback"), "fallback")
        self.assertEqual(get_option({}, "key1", "fallback"), "fallback")

    def test_generate_download_zip_file(self):
        import zipfile

        with self.app.test_request_context():
            from hedweb.web_util import generate_download_zip_file

            file_list = [
                {"file_name": "a.txt", "content": "hello from a"},
                {"file_name": "b.txt", "content": "hello from b"},
            ]
            results = {
                bc.FILE_LIST: file_list,
                "output_display_name": "test_archive.zip",
                bc.MSG: "Success",
                bc.MSG_CATEGORY: "success",
            }
            response = generate_download_zip_file(results)
            response.direct_passthrough = False
            self.assertEqual(200, response.status_code)
            headers = dict(response.headers)
            self.assertEqual("Success", headers["Message"])
            self.assertEqual("success", headers["Category"])
            zip_bytes = response.get_data()
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                names = zf.namelist()
            self.assertIn("a.txt", names)
            self.assertIn("b.txt", names)

    def test_package_results_zip(self):
        import zipfile

        with self.app.test_request_context():
            from hedweb.web_util import package_results

            file_list = [{"file_name": "z.txt", "content": "zip content"}]
            results = {
                bc.FILE_LIST: file_list,
                "output_display_name": "out.zip",
                bc.MSG: "ok",
                bc.MSG_CATEGORY: "success",
            }
            response = package_results(results)
            response.direct_passthrough = False
            self.assertEqual(200, response.status_code)
            zip_bytes = response.get_data()
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                self.assertIn("z.txt", zf.namelist())

    def test_package_results_download_text(self):
        with self.app.test_request_context():
            from hedweb.web_util import package_results

            results = {
                "data": "some text content\n",
                "output_display_name": "out.txt",
                "command_target": "events",
                bc.MSG: "ok",
                bc.MSG_CATEGORY: "success",
            }
            response = package_results(results)
            self.assertEqual(200, response.status_code)
            headers = dict(response.headers)
            self.assertIn("attachment", headers.get("Content-Disposition", ""))

    def test_package_results_inline_text(self):
        with self.app.test_request_context():
            from hedweb.web_util import package_results

            results = {
                "data": "",
                "output_display_name": "out.txt",
                bc.MSG: "ok",
                bc.MSG_CATEGORY: "success",
            }
            response = package_results(results)
            self.assertEqual(200, response.status_code)
            self.assertNotIn("attachment", response.headers.get("Content-Disposition", ""))

    def test_package_results_spreadsheet(self):
        with self.app.test_request_context():
            from hed.models import SpreadsheetInput

            from hedweb.web_util import package_results

            spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/ExcelOneSheet.xlsx")
            spreadsheet = SpreadsheetInput(
                file=spreadsheet_path,
                file_type=".xlsx",
                tag_columns=[4],
                has_column_names=True,
                name="ExcelOneSheet.xlsx",
            )
            results = {
                "data": None,
                bc.SPREADSHEET: spreadsheet,
                bc.OUTPUT_DISPLAY_NAME: "out.xlsx",
                bc.MSG: "ok",
                bc.MSG_CATEGORY: "success",
            }
            response = package_results(results)
            self.assertEqual(200, response.status_code)

    def test_package_results_list_data_joined(self):
        with self.app.test_request_context():
            from hedweb.web_util import package_results

            results = {
                "data": ["line one", "line two"],
                "output_display_name": "out.txt",
                "command_target": "events",
                bc.MSG: "ok",
                bc.MSG_CATEGORY: "success",
            }
            response = package_results(results)
            self.assertEqual(200, response.status_code)
            parts = [r.decode("utf-8") if isinstance(r, bytes) else r for r in response.response]
            content = "".join(parts)
            self.assertIn("line one", content)
            self.assertIn("line two", content)

    def test_generate_download_file_from_text_empty_raises(self):
        with self.app.test_request_context():
            from hed.errors import HedFileError

            from hedweb.web_util import generate_download_file_from_text

            with self.assertRaises(HedFileError):
                generate_download_file_from_text({"data": "", bc.MSG: "ok", bc.MSG_CATEGORY: "success"})

    def test_get_exception_message_safe_filename(self):
        from hed.errors.exceptions import HedExceptions, HedFileError

        from hedweb.constants import base_constants as bc
        from hedweb.web_util import get_exception_message

        # A schema identifier like "HED7.2.0" should be included in the message
        ex = HedFileError(HedExceptions.INVALID_HED_FORMAT, "Outdated schema", "HED7.2.0")
        result = get_exception_message(ex)
        self.assertIn("HED7.2.0", result[bc.MSG], "Safe schema identifier should appear in error message")
        self.assertIn("INVALID_HED_FORMAT", result[bc.MSG], "Error code should appear in error message")

    def test_get_exception_message_path_filename_suppressed(self):
        from hed.errors.exceptions import HedExceptions, HedFileError

        from hedweb.constants import base_constants as bc
        from hedweb.web_util import get_exception_message

        # A filesystem path should NOT be included in the user-facing message
        for path_filename in ["/etc/passwd", "C:\\Windows\\system32\\file.txt", "../../secret"]:
            ex = HedFileError(HedExceptions.BAD_PARAMETERS, "Some error", path_filename)
            result = get_exception_message(ex)
            self.assertNotIn(path_filename, result[bc.MSG], f"Path '{path_filename}' must not appear in error message")

    def test_get_exception_message_control_chars_stripped(self):
        from hed.errors.exceptions import HedExceptions, HedFileError

        from hedweb.constants import base_constants as bc
        from hedweb.web_util import get_exception_message

        # A filename containing CR/LF (header injection attempt) must have those chars removed
        ex = HedFileError(HedExceptions.BAD_PARAMETERS, "Injected", "HED8\r\nX-Injected: evil")
        result = get_exception_message(ex)
        self.assertNotIn("\r", result[bc.MSG], "CR must be stripped from error message")
        self.assertNotIn("\n", result[bc.MSG], "LF must be stripped from error message")


if __name__ == "__main__":
    unittest.main()
