"""
@brief this file will be all about pretty printing to the CLI


"""
from prettytable import PrettyTable



# # printTransaction: pretty prints a single transaction
# def printTransaction(self, print_mode=True):
#     stringToPrint = (
#             "DATE: "
#             + "".join(self.date)
#             + " || AMOUNT: "
#             + "".join(str(self.amount))
#             + self.getSpaces(len(str(self.amount)), 8)
#             + " || DESC: "
#             + "".join(self.description[0:70])
#             + self.getSpaces(len(self.description), 70)
#     )
#     if self.category_id is not None:
#         category_name = dbh.category.get_category_name_from_id(self.category_id)
#         stringToPrint = stringToPrint + " || CATEGORY: " + str(category_name) + self.getSpaces(len(str(category_name)),
#                                                                                                30)
#
#     stringToPrint = stringToPrint + " || ACCOUNT: " + "".join(
#         dbh.account.get_account_name_from_id(self.account_id)) + self.getSpaces(len(str(self.account_id)), 30)
#
#     if self.note is not None:
#         stringToPrint = stringToPrint + " || NOTE: " + self.note
#
#     if print_mode:
#         print(stringToPrint)
#     return stringToPrint


# TODO: complete this function. Will be used to "pretty print" transactions and other things in tabular format
# print_variable_table: prints a variable table
#   @param  variable_names      strings for the top headers
#   @param  values              a 2D array of the data to print
def print_variable_table(variable_names, values):
    table = PrettyTable()
    # do checking on same length input arrays
    table.field_names = variable_names
    table.add_rows(values)
    print(table)



# this function will print some tabular financial data (commonly account names and balances)
def print_balances(names, values, title):
    print(f"\n\n========= {title} =========")

    # check for length mismatch
    if len(names) != len(values):
        print("Can't print desired array! Mismatched lengths in program")
        return False

    for i in range(0, len(names)):
        formatted_value = "${:,.2f}".format(values[i])
        print(f"\t{names[i].ljust(25)}: {formatted_value}")



# this function will generally print an array of data
# TODO: complete this printing function - will be useful for printing transactions, categories, etc.
def print_tagged_array_data(labels, values):
    if len(labels) != len(values):
        print("YIKES: can't print with different length inputs")
        raise InterruptedError("Won't print variable table")
    pass



##############################################################################
####      CONSOLE PRINTING FUNCTIONS     #####################################
##############################################################################

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
