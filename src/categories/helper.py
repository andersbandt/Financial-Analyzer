import sqlite3
from ete3 import Tree

from src import categories
from db import db_helper


##############################################################################
####      CATEGORY ARRAY FUNCTIONS    ########################################
##############################################################################

# load_categories: returns an array containing all the category objects
def load_categories():
    all_category_id = db_helper.get_all_category_id()
    categories = []
    for category_id in all_category_id:
        categories.append(categories.Category(category_id[0]))  # have to grab 0 index because category_id is a tuple
    return categories


# check_categories: checks to see if a Category has no keywords
def check_categories(categories_array):
    for category in categories_array:
        if category.keyword is None:
            print("Uh oh, category: " + category.name + " has no keywords associated with it")


# print_categories: prints all the categories in an array of Category
def print_categories(categories_array):
    for category in categories_array:
        category.print()


##############################################################################
####      CATEGORY FUNCTIONS     #############################################
##############################################################################

def get_category_children(category_id, printmode=None):
    # debug print statements
    if printmode == "debug":
        print("DEBUG: category_helper.get_category_children()")
        print("\nExamining category: ", category_id_to_name(category_id))

    # init array to return and ledger data
    category_children = []
    cat_ledge_data = db_helper.get_category_ledger_data()

    # iterate through sql data and grab categories where parent is category
    for cat_sql in cat_ledge_data:
        if cat_sql[1] == category_id:
            category_children.append(cat_sql[0])

    if printmode == "debug":
        print("Got the following for children category")
        for child_id in category_children:
            print(category_id_to_name(child_id))

    return category_children


# category_name_to_id: converts a category name to the ID
def category_name_to_id(category_name):
    return db_helper.get_category_id_from_name(category_name)


# category_id_to_name
def category_id_to_name(category_id):
    return db_helper.get_category_name_from_id(category_id)


##############################################################################
####      GETTER FUNCTIONS     ###############################################
##############################################################################

# get_category_strings: returns an array containing strings of all the category names
def get_category_strings(categories_array):
    category_names = []
    for category in categories_array:
        category_names.append(category.getName())

    category_names = sorted(category_names)

    return category_names


def get_top_level_categories():
    top = []
    for category in load_categories():
        if category.parent == 1:
            top.append(category)
    return top


def get_top_level_category_names(categories):
    top = []
    for category in categories:
        if category.parent == 1:
            top.append(category.name)
    return top


##############################################################################
####      CATEGORY TREE FUNCTIONS     ########################################
##############################################################################

# create_Tree: creates a Tree object of the categories
def create_Tree(categories):
    print("category_helper.create_Tree: Generating Tree object of categories")
    t = Tree()
    root = t.add_child(name="root")  # create root node

    # first add all top level categories
    for category in categories:
        if category.parent == 1:  # if it is a top level category
            root.add_child(name=category.name)

    # then populate children
    for category in categories:
        if category.parent != 1:
            nodes = t.search_nodes(name=category_id_to_name(category.parent))
            for node in nodes:
                node.add_child(name=category.name)

    print("    length of created tree: ", len("root"))

    return t





