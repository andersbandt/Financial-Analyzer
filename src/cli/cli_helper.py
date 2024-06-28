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
from categories import categories_helper as cath
from categories import Category
import db.helpers as dbh


##############################################################################
####      GENERAL INPUT FUNCTIONS        #####################################
##############################################################################

# esc_cmd: helper function to handle valid command / input escape strings
def esc_cmd(inp):
    if inp == 'q':
        return False
    elif inp == 'quit':
        return False
    elif inp == "exit":
        return False


# parse_inp_type: performs parsing of user input based on type
#       @param[in]      inp         string input string from python input()
#       @param[in]      inp_type
#                           text     string return of input
#                           int      will return any POSITIVE VALUE (will return -1 on bad input) # TODO: verify this actually can't handle "-" minus sign
#                           float    will return any float value (maybe POSITIVE ONLY?)
#
def parse_inp_type(inp, inp_type):
    # TYPE: (text)
    if inp_type == "text":
        return inp

    # TYPE: (int) or (float)
    elif inp_type == "int" or "float":
        inp = inp.replace(',', '')  # get rid of commas
        # TODO: perform check for correctly positioned commands here
        try:
            if inp_type == "int":
                inp = int(inp)
            elif inp_type == "float":
                inp = float(inp)
        except ValueError as e:
            print("was that really a float/int?")
            return False
        return inp

    # UNKNOWN TYPE!
    else:
        raise BaseException("Unknown clih.spinput type!")


# spinput: really general input function to help with flow control
def spinput(prompt_str, inp_type):
    while True:
        inp = input(prompt_str)
        p_inp = parse_inp_type(inp, inp_type)
        if p_inp is not False:
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
# @param exact_match     requires input to be in strings_arr   # TODO: shouldn't it always be exact_match...? What's the point of this?
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
    m = get_month_input()
    return [y, m]


# TODO: ask ChatGPT to make version that automatically adds a dash "-" after the first four YYYY is entered
#   and then another one after the next MM is entered
def get_date_input(prompt_str):
    print(prompt_str)
    while True:
        date_str = input("Enter the date (YYYY-MM-DD): ")

        # handle QUIT commands
        if (date_str == "q") or (date_str == "quit"):
            return False

        # try to convert into datetime object
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.date()  # Return only the date part, not the time
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")


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
        return -1
    else:
        return cath.category_name_to_id(cat_inp)


# category_prompt: walks the user through selecting a Category from given array input
# TODO: 1) reduce size      2) figure out how to return value with recursive calls
# I also rarely use this function in practice ....
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
        cat_inp2 = inp_auto("Or select a category from list: ", [cat.name for cat in category_arr2], echo=True,
                            exact_match=False)



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
    ac_inp_id = dbh.account.get_account_id_from_name(ac_inp)
    return ac_inp_id


def account_prompt_all(prompt_str):
    # get a list of all the accounts
    accounts = dbh.account.get_account_names()

    # check for empty accounts
    if len(accounts) == 0:
        logger.exception("Uh oh, no accounts found!")
        return

    ac_inp = inp_auto(prompt_str, accounts, echo=True)
    ac_inp_id = dbh.account.get_account_id_from_name(ac_inp)
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
