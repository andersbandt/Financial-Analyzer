"""
@brief this file will be all about pretty printing to the CLI


"""

from prettytable import PrettyTable
from prettytable.colortable import ColorTable, Themes


##############################################################################
####      CONSOLE PRINTING FUNCTIONS     #####################################
##############################################################################

# print_variable_table: prints a variable table
#   @param  variable_names          strings for the top headers
#   @param  values                  a 2D array of the data to print
#   @param  format_finance_col      index of column number to format as financial data
def print_variable_table(variable_names, values, format_finance_col=None):
    # table = PrettyTable()
    table = ColorTable(theme=Themes.OCEAN) # green text with blue outline

    # if we want to format into finance
    if format_finance_col is not None:
        for entry in values:
            formatted_value = "${:,.2f}".format(float(entry[format_finance_col]))
            entry[format_finance_col] = formatted_value

    # populate data
    table.field_names = variable_names
    table.add_rows(values)
    # set alignment and formatting
    table.align = "r"
    table.align["DESC"] = "l"
    table.padding_width = 1
    print(table)


# getSpaces: gets the number of spaces needed for pretty printing in straight columns
def get_spaces(length, trim):
    spaces = ""
    for i in range(trim - length):
        spaces += " "
    return spaces


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
