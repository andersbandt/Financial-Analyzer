"""
@brief this file will be all about pretty printing to the CLI


"""


# import needed modules
from pprint import pprint
from prettytable.colortable import ColorTable, Theme


# import logger
from loguru import logger
from utils import logfn


my_custom_theme = Theme(default_color="91", # bright red
                        vertical_color="34",  # bright BLUE
                        horizontal_color="95",  # bright MAGENTA
                        junction_color="94",  # bright BLUE
                        vertical_char="||",
                        horizontal_char='-', # DEFAULT is '-'
                        junction_char='+' # DEFAULT is '+'
                        )


##############################################################################
####      CONSOLE PRINTING FUNCTIONS     #####################################
##############################################################################

#   @param  variable_names          strings for the top headers
#   @param  values                  a 2D array of the data to print
#   @param  format_finance_col      index of column number to format as financial data (starts at 0)
#   @param  max_width_column        the max width of ANY column in the table
# TODO: add a title to this
# @logfn
def print_variable_table(variable_names, values, min_width=15, max_width=40, format_finance_col=None,
                         max_width_column=None, add_row_numbers=True):
    # table = ColorTable(theme=Themes.OCEAN) # green text with blue outline
    # table = CustomColorTable()
    table = ColorTable(theme=my_custom_theme)  # green text with blue outline

    # if we want to set a width limit
    if max_width_column is not None:
        table._max_width = {max_width_column: 90}

    # set MIN column width for EVERY column
    table._max_table_width = 200
    table._min_width = {col: min_width for col in variable_names}
    table._max_width = {col: max_width for col in variable_names}

    # if we want to format into finance
    if format_finance_col is not None:
        for entry in values:
            formatted_value = "${:,.2f}".format(float(entry[format_finance_col]))
            entry[format_finance_col] = formatted_value

    # if we want to add row numbers
    if add_row_numbers:
        pass
        # TODO: this isn't working for example when I load data with a04_load_data
        # values = [[i + 1] + row for i, row in enumerate(values)]
        # variable_names = ["Row"] + variable_names

    # populate data
    # logger.debug(f"Final modified NAMES are looking like: {variable_names}")
    # logger.debug(f"Final modified VALUES are looking like: {values}")
    table.field_names = variable_names
    table.add_rows(values)
    # set alignment and formatting
    table.align = "l"
    table.padding_width = 1
    print(table)


# getSpaces: gets the number of spaces needed for pretty printing in straight columns
def get_spaces(length, trim):
    spaces = ""
    for i in range(trim - length):
        spaces += " "
    return spaces


def print_dict(inp_dict):
    pprint(inp_dict)


# print_category_amount
def print_category_amount(category, amount):
    string_to_print = (
            "CATEGORY: "
            + category.name
            + get_spaces(len(category.name), 16)
            + " || AMOUNT: "
            + str(amount)
    )
    print(string_to_print)
