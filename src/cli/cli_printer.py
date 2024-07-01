"""
@brief this file will be all about pretty printing to the CLI


"""

from prettytable import PrettyTable
from prettytable.colortable import ColorTable, Themes


##############################################################################
####      CONSOLE PRINTING FUNCTIONS     #####################################
##############################################################################

# print_variable_table: prints a variable table
#   @param  variable_names      strings for the top headers
#   @param  values              a 2D array of the data to print
def print_variable_table(variable_names, values, theme=Themes.OCEAN):
    # table = PrettyTable()
    table = ColorTable()
    # populate data
    table.field_names = variable_names
    table.add_rows(values)
    # set alignment and formatting
    table.align = "r"
    table.align["DESC"] = "l"
    table.padding_width = 1
    print(table)


# this function will print some tabular financial data (commonly account names and balances)
def print_balances(names, values, title):
    print(f"\n\n========= {title} =========")
    # check for length mismatch
    if len(names) != len(values):
        print("Can't print desired array! Mismatched lengths in program")
        return False

    table_values = []
    for i in range(0, len(names)):
        formatted_value = "${:,.2f}".format(values[i])
        # print(f"\t{names[i].ljust(25)}: {formatted_value}")
        table_values.append([names[i], values[i]])
    print_variable_table(
        ["ACCOUNT", "AMOUNT"],
        table_values
    )


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
