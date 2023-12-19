"""
@brief this file will be all about pretty printing to the CLI


"""


# getSpaces: gets the number of spaces needed for pretty printing in straight columns
# def getSpaces(self, length, trim):
#     spaces = ""
#     for i in range(trim - length):
#         spaces += " "
#     return spaces
#
#
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


# this function will generally print an array of data
def print_tagged_array_data(labels, values):
    if len(labels) != len(values):
            print("Can't print desired array! Mismatched lengths in program!")
            quit()


    for label in labels:
        print("f")

    pass