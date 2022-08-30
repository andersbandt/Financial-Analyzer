
# TODO: create spending over time graph. To gain insight into something like weekly, daily, monthly spending and how
#  it changes through the semester



# TODO: this function can be written more efficiently...
# strip_non_graphical_transactions: strips certain transactions that are part of categories
#   that don't graph well
def strip_non_graphical_transactions(categories, amounts):
    i = 0
    length = len(categories)
    non_graphical = ["BALANCE", "SHARES", "TRANSFER", "PAYMENT", "VALUE", "INTERNAL"]

    for j in range(0, length):
        if categories[i] in non_graphical:
            print("Removing category: ", categories[i])
            categories.remove(categories[i])
            del amounts[i]
            i -= 1
        '''if categories[i] == "BALANCE":
            print("Removing category: ", categories[i])
            categories.remove(categories[i])
            del amounts[i]
            i -= 1
        elif categories[i] == "SHARES":
            print("Removing category: ", categories[i])
            categories.remove(categories[i])
            del amounts[i]
            i -= 1
        elif categories[i] == "TRANSFER":
            print("Removing category: ", categories[i])
            categories.remove(categories[i])
            del amounts[i]
            i -= 1
        elif categories[i] == "PAYMENT":
            print("Removing category: ", categories[i])
            categories.remove(categories[i])
            del amounts[i]
            i -= 1
        elif categories[i] == "VALUE":
            print("Removing category: ", categories[i])
            categories.remove(categories[i])
            del amounts[i]
            i -= 1
        elif categories[i] == "INTERNAL":
            print("Removing category: ", categories[i])
            categories.remove(categories[i])
            del amounts[i]
            i -= 1'''
        i += 1

    return categories, amounts


# getSpaces: gets the number of spaces needed for pretty printing in straight columns
def get_spaces(length, trim):
    spaces = ""
    for i in range(trim - length):
        spaces += " "
    return spaces


# print_category_amount
def print_category_amount(category, amount):
    string_to_print = ("CATEGORY: " + category + get_spaces(len(category), 16) + " || AMOUNT: " + str(amount))
    print(string_to_print)



