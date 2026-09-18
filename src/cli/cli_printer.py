"""
@brief this file will be all about pretty printing to the CLI


"""


# import needed modules
import shutil
from pprint import pprint
from prettytable.colortable import ColorTable, Theme


# import logger
from loguru import logger


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
#   @param  values                  a 2D array of the data to print. NOTE: can't be a NUMPY array
#   @param  format_finance_col      index of column number to format as financial data (starts at 0)
#   @param  max_width_column        the max width of ANY column in the table
#   @param  title                   optional title to display above the table
def print_variable_table(variable_names, values, min_width=15, max_width=40, format_finance_col=None,
                         max_width_column=None, add_row_numbers=True, title=None):
    # DEBUG PRINTOUT BELOW
    logger.debug(variable_names)
    logger.debug(values)
    # END OF DEBUG PRINTOUT

    # table = ColorTable(theme=Themes.OCEAN) # green text with blue outline
    # table = CustomColorTable()
    table = ColorTable(theme=my_custom_theme)  # green text with blue outline

    # Size to the ACTUAL terminal, not a fixed guess. A budget wider than the real terminal
    # doesn't just overflow cleanly -- PrettyTable pads columns out to fill it, so the rendered
    # table ends up wider than the terminal and gets soft-wrapped mid-cell by the terminal
    # itself, breaking the box-drawing into the "||" fragments strewn across separate lines.
    # Piping to a file/non-tty has no real width, so fall back to something generous.
    #
    # The theme's vertical_char is "||" (2 chars), but PrettyTable's width budgeting assumes a
    # 1-char separator -- with N columns there are N+1 separators, so the actual rendered width
    # comes out N+1 chars OVER whatever budget we give it. Subtract that back out, or a table
    # sized "exactly" to the terminal still overflows it by a handful of columns every time.
    term_width = shutil.get_terminal_size(fallback=(200, 24)).columns
    table._max_table_width = max(term_width - (len(variable_names) + 1), 20)

    # set MIN/MAX column width for EVERY column
    table._min_width = {col: min_width for col in variable_names}
    table._max_width = {col: max_width for col in variable_names}

    # Give one column extra room (e.g. a long Description/Note column) -- must happen AFTER
    # the uniform per-column pass above, which otherwise immediately clobbers this.
    if max_width_column is not None:
        table._max_width[max_width_column] = 90

    # if we want to format into finance
    if format_finance_col is not None:
        for entry in values:
            formatted_value = "${:,.2f}".format(float(entry[format_finance_col]))
            entry[format_finance_col] = formatted_value


    # populate data
    table.field_names = variable_names
    table.add_rows(values)
    # set alignment and formatting
    table.align = "l"
    table.padding_width = 1

    # print title if provided
    if title is not None:
        print(f"\n{title}")
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
