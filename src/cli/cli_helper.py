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
from account import account_helper as acch
from categories import categories_helper as cath
from categories import Category
from tools import date_helper as dateh
import db.helpers as dbh


##############################################################################
####      GENERAL INPUT FUNCTIONS        #####################################
##############################################################################

# esc_cmd: helper function to handle valid command / input escape strings
def esc_cmd(inp):
    if inp == 'q':
        return True
    elif inp == 'quit':
        return True
    elif inp == "exit":
        return True
    else:
        return False


# parse_inp_type: performs parsing of user input based on type
#       @param[in]      inp         string input string from python input()
#       @param[in]      inp_type
#                           text     string return of input
#                           int      will return any POSITIVE VALUE (will return -1 on bad input) # TODO: verify this actually can't handle "-" minus sign
#                           float    will return any float value (maybe POSITIVE ONLY?)
def parse_inp_type(inp, inp_type):
    # TYPE: (int)
    if inp_type == "int":
        inp = inp.replace(',', '')  # get rid of commas
        try:
            inp = int(inp)
        except ValueError as e:
            print("was that really an int?")
            print(e)
            return -1
        return inp
    # TYPE: (text)
    if inp_type == "text":
        return inp

    # TYPE: (int) or (float)
    elif inp_type == "int" or "float":
        try:
            # TODO: perform check for correctly positioned commands here
            inp = inp.replace(',', '')  # get rid of commas
        except AttributeError:
            pass
        try:
            if inp_type == "int":
                inp = int(inp)
            elif inp_type == "float":
                inp = float(inp)
        except ValueError as e:
            print("was that really a float/int?")
            return False
        return inp

    # TYPE: (float)
    elif inp_type == "float":
        inp = inp.replace(',', '')  # get rid of commas
        return float(inp)

    # TYPE: (yes or no)
    # if type == 'yn':

    # UNKNOWN TYPE!
    else:
        raise BaseException("Unknown clih.spinput type!")


# spinput: really general input function to help with flow control
#   @param[in]        inp_type   (see the variable description in function inp_type)
def spinput(prompt_str, inp_type):
    while True:
        inp = input(prompt_str)
        if esc_cmd(inp):
            return False

        p_inp = parse_inp_type(inp, inp_type)
        return p_inp


# promptYesNo: function for prompting user for a YES or NO input
def promptYesNo(prompt_str):
    res = input(prompt_str + "\n\t(y or n): ")
    if 'y' in res:
        return True
    else:
        return False


# prompt_num_options: prompts an array of string options with a corresponding int response
def prompt_num_options(prompt_str, prompt_string_arr):
    i = 1
    for pro in prompt_string_arr:
        print(f"{i} - {pro}")
        i += 1
    res = input(prompt_str)
    if res == 'q' or res == 'quit':
        return False
    try:
        if int(res) > len(prompt_string_arr):
            print("Uh oh I think your choice was out of bounds!")
            return False
        return int(res)
    except ValueError:
        return False

def prompt_for_int_array(prompt_str):
    int_arr = []
    while True:
        new_int = input("Enter int to add: ")
        if esc_cmd(new_int):
            return int_arr
        int_arr.append(new_int)

##############################################################################
####      prompt_toolkit FUNCTIONS        ####################################
##############################################################################

# autocomplete: helper function I think???
def autocomplete(input_text, word_list):
    completer = WordCompleter(word_list)
    return prompt(input_text, completer=completer)


# inp_auto: user input with autocomplete function on a provided array of strings
# @param prompt_str      gets printed
# @param string_arr      array of options for user to have autocomplete run on
# @param echo            echo confirmation of selection?
# @param disp_options    toggles all the possible array getting printed or not
# @param exact_match     requires input to be in strings_arr
def inp_auto(prompt_str, strings_arr, echo=False, disp_options=True, exact_match=False):
    print("\n")
    # IF USER SELECTED DISPLAY OPTIONS
    if disp_options:
        for string in strings_arr:
            print("-" + string)

    user_input = autocomplete(prompt_str + " ", strings_arr)

    if exact_match:
        if user_input not in strings_arr:
            print(user_input + " is not in inp_auto list!")
            return -1  # can't return -1 here because category NA has ID=0

    if echo:
        print("Selected: " + user_input + "\n")
    return user_input


##############################################################################
####      SPECIALIZED INPUT FUNCTIONS    #####################################
##############################################################################

def get_year_input():
    year = input("Enter year input: ")
    try:
        return int(year)
    except ValueError:
        return False


def get_month_input():
    month = input("Enter month input (0-12): ")
    try:
        return int(month)
    except ValueError:
        return False


def prompt_year_month():
    print("\n... prompting user to find file for Statement")
    # get date information to determine which folder to look in
    y = get_year_input()
    if y is False:
        return False
    m = get_month_input()
    if m is False:
        return False
    return [y, m]


# TODO: ask ChatGPT to make version that automatically adds a dash "-" after the first four YYYY is entered
#   and then another one after the next MM is entered
def get_date_input(prompt_str):
    print(prompt_str)
    print("\tpssst -- can enter 'today' for current date")
    while True:
        date_str = input("Enter the date (YYYY-MM-DD): ")
        if date_str == "today":
            return dateh.get_cur_str_date()

        # handle QUIT commands
        if (date_str == "q") or (date_str == "quit"):
            return False

        # try to convert into datetime object
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            # return date_obj.date()  # Return only the date part, not the time # TODO: do I want to return this instead for some extra insurance?
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
        else:
            return date_str

##############################################################################
####      CATEGORY INPUT FUNCTIONS    ########################################
##############################################################################


# param         prompt_str    string to print to user
# @param        display       print out all the categories or NOT
# @returns      -1 if bad prompt response, category_id otherwise
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
        return False
    else:
        return cath.category_name_to_id(cat_inp)


# category_prompt: walks the user through selecting a Category from given array input
# TODO: reduce size. Separate parsing or make recursive. Or both.
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
    cur_cat_obj = Category.Category(0)
    cur_cat_obj.set_parent(1)
    prev_cat_obj = cur_cat_obj
    while status:
        print("Type 'y' to finalize category")
        print("Type 'x' to go one level up")

        # call inp_auto() to walk user through an autocomplete input experience
        cat_inp = inp_auto("What is the category?: ",
                           [cat.name for cat in category_arr],
                           echo=True,
                           exact_match=False)
        # HANDLE USER STRING COMMANDS
        if cat_inp == 'y':
            print("Returning for parent category: " + prev_cat_obj.name)
            return prev_cat_obj.id
        elif cat_inp == 'x':
            print("Backing up Category tree... ")
            print("\tattempting to create Category with id: ", cur_cat_obj.parent)
            if cur_cat_obj.parent == 1:
                new_arr = cath.load_top_level_categories()
            else:
                new_arr = cath.get_category_children_obj(Category.Category(cur_cat_obj.parent))
            return new_arr
        elif cat_inp == 'q':
            return -1
        elif cat_inp is None:
            print("Ruh oh, bad category input")

        # PARSE INPUT CATEGORY FOR TREE SEARCH
        cur_cat_obj = find_category(category_arr, cat_inp)
        prev_cat_obj = cur_cat_obj
        if cur_cat_obj is not None:
            print("\nGoing deeper into Category tree... ")
            print("Forming new array based on: " + cur_cat_obj.name)
            category_arr = cath.get_category_children_obj(cur_cat_obj)
            if len(category_arr) == 0:
                print("No children for selected category. Returning automatically")
                return cur_cat_obj.id

    return False


    category_arr2 = []
    category_arr2.extend([Category.Category(child_id) for child_id in cur_cat_obj.children_id])
    status = True
    while status:
        # print(prompt)
        print("Type 'y' to finalize category")
        print("Type 'x' to go one level up")
        cat_inp2 = inp_auto("Or select a category from list: ", [cat.name for cat in category_arr2], echo=True,
                            exact_match=False)

    # category_arr2 = []
    # category_arr2.extend([Category.Category(child_id) for child_id in cur_cat_obj.children_id])
    # status = True
    # while status:
    #     # print(prompt)
    #     print("Type 'y' to finalize category")
    #     print("Type 'x' to go one level up")
    #     cat_inp2 = inp_auto("Or select a category from list: ", [cat.name for cat in category_arr2], echo=True,
    #                         exact_match=False)


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
        cat = category_tree_prompt(cath.load_top_level_categories(), trans_prompt)
    # MODE2: list all prompts in DB
    elif mode == 2:
        cat = category_prompt_all(trans_prompt,
                                  False)  # second param controls if I print all the categories each transaction or not
    else:
        print("Uh oh, invalid category selection mode!")
        return None

    # do some error handling on category
    if cat == -1:
        print("category input (-1) return reached.")
        return -1  # can't return 0 here because the category NA has an ID of 0 !!!

    # set new Category to Transaction and print for lolz
    # print("Adding category " + cat.getName())
    transaction.setCategory(cat)
    print("\nCategorized transaction below")
    transaction.printTransaction()

    # return newly associated Category ID so upper layer can properly change Transaction data
    return cat


##############################################################################
####      ACCOUNT INPUT FUNCTIONS    #########################################
##############################################################################

def account_prompt_type(prompt_str, acc_type):
    # get a list of all the accounts
    accounts = dbh.account.get_account_names_by_type(acc_type)

    # check for empty accounts
    if len(accounts) == 0:
        logger.exception("Uh oh, no accounts found!")
        return

    ac_inp = inp_auto(prompt_str, accounts, echo=True, exact_match=True)
    if ac_inp is False:
        return False
    ac_inp_id = acch.account_name_to_id(ac_inp)
    return ac_inp_id


def account_prompt_all(prompt_str):
    # get a list of all the accounts
    accounts = dbh.account.get_account_names()

    # check for empty accounts
    if len(accounts) == 0:
        logger.exception("Uh oh, no accounts found!")
        return

    ac_inp = inp_auto(prompt_str, accounts, echo=True)
    ac_inp_id = acch.account_name_to_id(ac_inp)
    return ac_inp_id


def get_account_id_manual():
    accounts = dbh.account.get_account_ledger_data()
    i = 1
    for account in accounts:
        print(str(i) + ": " + account[1])
        i += 1

    acc_num = int(input("\t\tPlease enter what account you want: "))
    acc = accounts[acc_num - 1][0]
    return acc
