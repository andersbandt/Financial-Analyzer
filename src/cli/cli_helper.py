"""
@file cli_helper.py
@brief used for assisting CLI functions

"""


# import needed modules
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from datetime import datetime
from loguru import logger

# helper modules for CLI interface
from tools import date_helper
from categories import categories_helper as cath
from categories import Category
import db.helpers as dbh


# get_statement_folder: returns formatted folder of where the statement is. year and month are ints
def get_statement_folder(base_filepath, year, month):
    if month not in range(0, 12):
        month = date_helper.month2Int(month)

    if month == 1:
        month_string = "01-January/"
    elif month == 2:
        month_string = "02-February/"
    elif month == 3:
        month_string = "03-March/"
    elif month == 4:
        month_string = "04-April/"
    elif month == 5:
        month_string = "05-May/"
    elif month == 6:
        month_string = "06-June/"
    elif month == 7:
        month_string = "07-July/"
    elif month == 8:
        month_string = "08-August/"
    elif month == 9:
        month_string = "09-September/"
    elif month == 10:
        month_string = "10-October/"
    elif month == 11:
        month_string = "11-November/"
    elif month == 12:
        month_string = "12-December/"
    else:
        print("Bad month int stored in statement: " + str(month))
        return

    statement_folder = (
        base_filepath + "/" + str(year) + "/monthly_statements/" + month_string # tag:HARDCODE
    )
    return statement_folder



##############################################################################
####      GENERAL INPUT FUNCTIONS        #####################################
##############################################################################

# spinput: really general input function to help with flow control

# type (int)  === will return any POSITIVE VALUE (will return -1 on bad input)
def spinput(prompt, type="text"):
    inp = input(prompt)

    # handle user prompts to either quit command or terminate program
    if inp == 'q':
        return False
    elif inp == "exit":
        return -1

    # TYPE: (int)
    if type == "int":
        try:
            inp = int(inp)
        except ValueError as e:
            print("was that really an int?")
            print(e)
            return -1

    # TYPE: (text)
    if type == "text":
        return inp

    # TYPE: (float)
    if type == "float":
        return float(inp)

    # TYPE: (yes or no)
    # if type == 'yn':


    return inp



# promptYesNo: function for prompting user for a YES or NO input
def promptYesNo(prompt):
    res = input(prompt + "\n\t(y or n):")
    if 'y' in res:
        return True
    else:
        return False


# prompt date function below in another section

##############################################################################
####      prompt_toolkit FUNCTIONS        ####################################
##############################################################################

# autocomplete: helper function I think???
def autocomplete(input_text, word_list):
    completer = WordCompleter(word_list)
    return prompt(input_text, completer=completer)



# inp_auto: user input with autocomplete function on a provided array of strings
# TODO: make this function case INSENSITIVE --> actually less sure if that is a priority
# @param prompt        gets printed
# @param stat          not sure what this is doing
# @param disp_options  toggles all the possible array getting printed or not
def inp_auto(prompt, strings_arr, echo=False, disp_options=True, exact_match=False):
    # IF USER SELECTED DISPLAY OPTIONS
    if disp_options:
        for string in strings_arr:
            print("-" + string)

    user_input = autocomplete(prompt + " ", strings_arr)

    if exact_match:
        if user_input not in strings_arr:
            print(user_input + " is not in inp_auto list!")
            return -1 # can't return -1 here because category NA has ID=0

    if echo:
        print("Selected: " + user_input)
    return user_input


##############################################################################
####      SPECIALIZED INPUT FUNCTIONS    #####################################
##############################################################################

def get_year_input():
    year = input("Enter year input: ")
    return int(year)

def get_month_input():
    month = input("Enter month input (0-12): ")
    return int(month)


def get_date_input(prompt):
    print(prompt)
    while True:
        date_str = input("Enter the date (YYYY-MM-DD): ")

        try:
            # Convert the input string to a datetime object
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.date()  # Return only the date part, not the time
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")


# returns -1 if bad prompt response
def category_prompt_all(prompt_str, display):
    print(prompt_str)
    # get list of all Category objects
    categories = cath.load_categories()
    cat_inp = inp_auto("What is the category?: ",
                       [cat.name for cat in categories],
                       echo=True,
                       disp_options=display,
                       exact_match=True)

    if cat_inp == -1:
        print("category_prompt_all received bad response.")
        return -1
    else:
        return cath.category_name_to_id(cat_inp)


def account_prompt_all(prompt):
    print(prompt)
    # get a list of all the accounts
    accounts = dbh.account.get_account_names()

    # check for empty accounts
    if len(accounts) == 0:
        logger.exception("Uh oh, no accounts found!")
        return

    ac_inp = inp_auto("What is the account?", accounts, echo=True, stat=prompt)
    ac_inp_id = dbh.account.get_account_id_from_name(ac_inp)
    return ac_inp_id



# category_prompt: walks the user through selecting a Category from given array input
# TODO: this function can be broken into at least one other function FOR SURE
# TODO: this function also is incapable of returning a value because of the recursive calls
def category_tree_prompt():
    category_arr = cath.load_top_level_categories()

    # helper function to match cat_inp Category.name string to the right Category object
    def find_category(category_array, cat_name):
        cat_obj = None
        for cat in category_array:
            if cat.name == cat_name:
                cat_obj = cat
        return cat_obj

    status = True
    first_run = True
    cur_cat_obj = None
    while status:
        if not first_run:
            print("Type 'y' to finalize category")
            print("Type 'x' to go one level up")
        first_run = False

        # call inp_auto() to walk user through an autocomplete input experience
        cat_inp = inp_auto("What is the category?: ",
                           [cat.name for cat in category_arr],
                           echo=True,
                           exact_match=False)
        prev_cat_obj = cur_cat_obj
        cur_cat_obj = find_category(category_arr, cat_inp)

        # if cur_cat_obj is None:
        #     res = promptYesNo("Uh oh, input may have been wrong. Try again?")
        #     if res:
        #         return False
        #     else:
        #         return False

        # handle user input
        if cat_inp == 'y':
            print("Returning FINAL Category: " + prev_cat_obj.name)
            return prev_cat_obj.id
        elif cat_inp == 'x':
            print("Backing up Category tree... ")
            print("\tattempting to create Category with id: ", cur_cat_obj.parent)
            if (cur_cat_obj.parent == 1):
                new_arr = cath.load_top_level_categories()
            else:
                new_arr = cath.get_category_children_obj(Category.Category(cur_cat_obj.parent))
            return new_arr
        elif cat_inp == 'q':
            return -1
        elif cat_inp is None:
            print("Ruh oh, bad category input")
        else:
            print("\nGoing deeper into Category tree... ")
            print("Forming new array based on: " + cur_cat_obj.name)
            # form new arrays of Category based on current selected Category
            category_arr = cath.get_category_children_obj(cur_cat_obj)
            if len(category_arr) == 0:
                return cur_cat_obj.id

    return False




    category_arr2 = []
    category_arr2.extend([Category.Category(child_id) for child_id in cur_cat_obj.children_id])
    status = True
    while status:
        # print(prompt)
        print("Type 'y' to finalize category")
        print("Type 'x' to go one level up")
        cat_inp2 = inp_auto("Or select a category from list: ", [cat.name for cat in category_arr2], echo=True, exact_match=False)




# TODO: I think I should refactor this to be outside cli_helper
# get_category_input: this function should display a transaction to the user and prompt them through categorization
#   with the end result being returning the associated category_id with the transaction in question
def get_category_input(transaction, mode=2):
    # create initial category tree
    # categories = cath.load_categories()
    # tree = cath.create_Tree(categories)
    # print(tree)
    # tree_ascii = tree.get_ascii()
    # print(tree_ascii)

    # print transaction and prompt
    print("\n\n")
    trans_prompt = transaction.printTransaction()

    # MODE1: descend into tree
    if mode == 1:
        # set up autocomplete information
        #   by calling category_prompt(on top level of categories)
        cat = category_prompt(cath.load_top_level_categories(), trans_prompt) # TODO: can I eliminate the load here?
    # MODE2: list all prompts in DB
    elif mode == 2:
        cat = category_prompt_all(trans_prompt, False) # second param controls if I print all the categories each transaction or not
    else:
        print("Uh oh, invalid category selection mode!")
        return None

    # do some error handling on category
    if cat == -1:
        print("category input (-1) return reached.")
        return -1 # can't return 0 here because the category NA has an ID of 0 !!!

    # set new Category to Transaction and print for lolz
    # print("Adding category " + cat.getName())
    transaction.setCategory(cat)
    print("\nCategorized transaction below")
    transaction.printTransaction()

    # return newly associated Category ID so upper layer can properly change Transaction data
    return cat

