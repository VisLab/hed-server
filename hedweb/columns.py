import openpyxl
import os
from pandas import DataFrame, read_csv
from hed.errors import HedFileError
from hed.tools.analysis.tabular_summary import TabularSummary
from hedweb.constants import base_constants, file_constants
from hedweb.web_util import form_has_file, form_has_option


def create_column_selections(form_dict):
    """ Return a tag prefix dictionary from a form dictionary.

    Parameters:
        form_dict (dict): The column prefix table returned from a form.

    Returns:
        dict: Keys are column numbers (starting with 1) and values are tag prefixes to prepend.

    """
    columns = []
    columns_selected = []
    columns_categorical = []
    keys = form_dict.keys()
    for key in keys:
        if not key.startswith('column_') or not key.endswith('_name'):
            continue
        pieces = key.split('_')
        col_name = form_dict[key]
        columns.append(col_name)
        if 'column_' + pieces[1] + '_use' in keys:
            columns_selected.append(col_name)
        if 'column_'  +  pieces[1] + '_category' in keys:
            columns_categorical.append(col_name)
    columns_value = list(set(columns_selected).difference(set(columns_categorical)))
    columns_skip = list(set(columns).difference(set(columns_selected)))
    return columns_value, columns_skip


def get_tag_columns(form_dict):
    """ Return the tag column names selected from a form.

    Parameters:
        form_dict (dict): The column names table

    Returns:
        list: List of tag columns

    """
    tag_columns = []
    keys = form_dict.keys()
    for key in keys:
        if not key.startswith('column_') or not key.endswith('_use'):
            continue
        pieces = key.split('_')
        columnNameKey = 'column_' + pieces[1] + '_name'
        if columnNameKey in keys and form_dict[columnNameKey]:
            tag_columns.append(form_dict[columnNameKey])
    return tag_columns

def _create_columns_info(columns_file, has_column_names=True, sheet_name=None):
    """ Create a dictionary of column information from a spreadsheet.

    Parameters:
        columns_file (File-like): File to create the dictionary for.
        has_column_names (bool):  If True, first row is interpreted as the column names.
        sheet_name (str): The name of the worksheet if this is an Excel file.

    Returns:
        dict: Dictionary containing information include column names and number of unique values in each column.

    Raises:
        HedFileError: If the file does not have the either an Excel or text file extension.

    """
    header = None
    if has_column_names:
        header = 0

    sheet_names = None
    filename = columns_file.filename
    file_ext = os.path.splitext(filename.lower())[1]
    if file_ext in file_constants.EXCEL_FILE_EXTENSIONS:
        worksheet, sheet_names = _get_worksheet(columns_file, sheet_name)
        dataframe = dataframe_from_worksheet(worksheet, has_column_names)
        sheet_name = worksheet.title
    elif file_ext in file_constants.TEXT_FILE_EXTENSIONS:
        dataframe = read_csv(columns_file, delimiter='\t', header=header)
    else:
        raise HedFileError('BadFileExtension',
                           f'File {filename} extension does not correspond to an Excel or tsv file', '')
    col_list = list(dataframe.columns)
    col_dict = TabularSummary()
    col_dict.update(dataframe)
    col_counts = col_dict.get_number_unique()
    columns_info = {base_constants.COLUMNS_FILE: filename, base_constants.COLUMN_LIST: col_list,
                    base_constants.COLUMN_COUNTS: col_counts,
                    base_constants.WORKSHEET_SELECTED: sheet_name, base_constants.WORKSHEET_NAMES: sheet_names}
    return columns_info


def dataframe_from_worksheet(worksheet, has_column_names):
    """ Return a pandas data frame from an Excel worksheet.

    Parameters:
        worksheet (Worksheet): A single worksheet of an Excel file.
        has_column_names (bool): If True, interpret the first row as column names.

    Returns:
        DataFrame:  The data represented in the worksheet.

    """
    if not has_column_names:
        data_frame = DataFrame(worksheet.values)
    else:
        data = worksheet.values
        # first row is columns
        cols = next(data)
        data = list(data)
        data_frame = DataFrame(data, columns=cols)
    return data_frame


def get_columns_request(request):
    """ Create a columns info dictionary based on the request.

    Parameters:
        request (Request): The Request object from which to extract the information.

    Returns:
        dict: The dictionary with the column names.

    Raises:
        HedFileError: If the file is missing or has a bad extension.


    """
    if not form_has_file(request, base_constants.COLUMNS_FILE):
        raise HedFileError('MissingFile', 'An uploadable file was not provided', None)
    columns_file = request.files.get(base_constants.COLUMNS_FILE, '')
    has_column_names = form_has_option(request, 'has_column_names', 'on')
    sheet_name = request.form.get(base_constants.WORKSHEET_SELECTED, None)
    return _create_columns_info(columns_file, has_column_names, sheet_name)


def get_column_numbers(form_dict):
    """ Return a tag prefix dictionary from a form dictionary.

    Parameters:
        form_dict (dict): The dictionary returned from a form that contains a column table.

    Returns:
        list: List of selected columns
        
    Note: The form counts columns starting from 1.
    """
    tag_columns = []
    keys = form_dict.keys()
    for key in keys:
        index_check = key.rfind('_check')
        if index_check == -1 or form_dict[key] != 'on':
            continue
        pieces = key.split("_")
        column_number = int(pieces[1])
        tag_columns.append(column_number)
    return tag_columns


def _get_worksheet(excel_file, sheet_name):
    """ Return a Worksheet and a list of sheet names from an Excel file.

    Parameters:
        excel_file (str): Name of the Excel file to use.
        sheet_name (str or None): Name of the worksheet if any, otherwise the first one.

    """
    wb = openpyxl.load_workbook(excel_file, read_only=True)
    sheet_names = wb.sheetnames
    if not sheet_names:
        raise HedFileError('BadExcelFile', 'Excel files must have worksheets', None)
    if sheet_name and sheet_name not in sheet_names:
        raise HedFileError('BadWorksheetName', f'Worksheet {sheet_name} not in Excel file', '')
    if sheet_name:
        worksheet = wb[sheet_name]
    else:
        worksheet = wb.worksheets[0]
    return worksheet, sheet_names
