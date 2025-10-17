"""
@file categories_helper.py
@brief provides functions for dealing with the Category object and Category SQL data (ID and name mainly)
"""

# import needed modules
from ete3 import Tree

# import user created modules
import db.helpers as dbh
from categories import Category

# import logger
from loguru import logger
from utils import logfn


##############################################################################
####      CATEGORY ARRAY FUNCTIONS    ########################################
##############################################################################

# load_categories: returns an array containing all the category objects
def load_categories():
    # logger.debug("cath.load_categories: loading category ID's")
    all_category_id = dbh.category.get_all_category_id()
    categories = []
    for category_id in all_category_id:
        categories.append(
            Category.Category(category_id[0])
        )  # have to grab 0 index because category_id is a tuple
    return categories


def load_top_level_categories():
    all_category = dbh.category.get_category_ledger_data()
    categories = []
    for category in all_category:
        if category[1] == 1:
            categories.append(
                Category.Category(category[0])
            )  # have to grab 0 index because category_id is a tuple
    return categories


# check_categories: checks to see if a Category has no keywords
def check_categories(categories_array):
    for category in categories_array:
        if category.keyword is None:
            print(
                "Uh oh, category: "
                + category.name
                + " has no keywords associated with it"
            )


# print_categories: prints all the categories in an array of Category
def print_categories(categories_array):
    for category in categories_array:
        category.print()


##############################################################################
####      CATEGORY FUNCTIONS     #############################################
##############################################################################

# category_name_to_id: converts a category name to the ID
def category_name_to_id(category_name):
    try:
        category_id = dbh.category.get_category_id_from_name(category_name)
    except Exception as e:
        print("Something went wrong getting category ID from name: " + str(category_name))
        return -1
    return category_id


# category_id_to_name
def category_id_to_name(category_id):
    if category_id is None:
        return "NA" #tag:hardcode?
    return dbh.category.get_category_name_from_id(category_id)


##############################################################################
####      GETTER FUNCTIONS     ###############################################
##############################################################################

def get_category_children(category_id, printmode=None):
    # debug print statements
    if printmode == "debug":
        print("DEBUG: category_helper.get_category_children()")
        print("\nExamining category: ", category_id_to_name(category_id))

    # init array to return and ledger data
    category_children = []
    cat_ledge_data = dbh.category.get_category_ledger_data()

    # iterate through sql data and grab categories where parent is category
    for cat_sql in cat_ledge_data:
        if cat_sql[1] == category_id:
            category_children.append(cat_sql[0])

    if printmode == "debug":
        print("Got the following for children category")
        for child_id in category_children:
            print(category_id_to_name(child_id))

    return category_children


def get_category_parent(category_id, printmode=None):
    # debug print statement
    if printmode:
        print(f"... finding parent for category: {category_id}")

    # find parent_id for category
    old_parent_id = category_id
    while True:
        parent_id = dbh.category.get_category_parent_id(old_parent_id)

        if parent_id is None or parent_id == 0:
            return 0
        if parent_id == 1:
            return old_parent_id

        old_parent_id = parent_id

    return old_parent_id


# get_category_strings: returns an array containing strings of all the category names
def get_category_strings(categories_array):
    category_names = []
    for category in categories_array:
        category_names.append(category.getName())

    category_names = sorted(category_names)

    return category_names


def get_top_level_categories(cat_type="class"):
    top = []
    for category in load_categories():
        if category.parent == 1:
            if cat_type == "class":
                top.append(category)
            elif cat_type == "id":
                top.append(category.id)
            elif cat_type == "name":
                top.append(category.name)
    return top


##############################################################################
####      CATEGORY TREE FUNCTIONS     ########################################
##############################################################################

# get_category_children: takes in a Category object and returns an array of all the children
def get_category_children_obj(category):
    cat_child = []
    for child_id in category.children_id:
        cat_child.append(Category.Category(child_id))
    return cat_child


# create_Tree: creates a Tree object of the categories
# @logfn
def create_Tree(categories, cat_type="id"):
    # logger.debug("category_helper.create_Tree: Generating Tree object of categories")
    t = Tree()
    root = t.add_child(name="root")  # create root node

    # first add all top level categories
    for category in get_top_level_categories():
        if category.parent == 1:  # if it is a top level category
            if cat_type == "id":
                root.add_child(name=category.id)
            elif cat_type == "name":
                root.add_child(name=category.name)
            else:
                logger.exception("Bad type supplied for category Tree creation")

    # then populate children
    for category in categories:
        if category.parent != 1:
            if cat_type == "id":
                nodes = t.search_nodes(name=category.parent)
            elif cat_type == "name":
                nodes = t.search_nodes(name=category_id_to_name(category.parent))
            for node in nodes:
                if cat_type == "id":
                    node.add_child(name=category.id)
                elif cat_type == "name":
                    node.add_child(name=category.name)

    return t
