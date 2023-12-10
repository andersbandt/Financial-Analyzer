"""
@file categories_helper.py
@brief provides functions for dealing with the Category object and Category SQL data (ID and name mainly)
"""

# import needed modules
from ete3 import Tree

# import user created modules
import db.helpers as dbh
from categories import Category


##############################################################################
####      CATEGORY ARRAY FUNCTIONS    ########################################
##############################################################################

# load_categories: returns an array containing all the category objects
def load_categories():
    print("load_categories: loading category ID's")
    all_category_id = dbh.category.get_all_category_id()
    print("load_categories: done getting all categories")
    categories = []
    for category_id in all_category_id:
        categories.append(
            Category.Category(category_id[0])
        )  # have to grab 0 index because category_id is a tuple
    print("ACTUALLY RETURNING CATEGORIERs")
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
    return dbh.category.get_category_name_from_id(category_id)


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

# get_category_children: takes in a Category object and returns an array of all the children
def get_category_children_obj(category):
    cat_child = []
    for child_id in category.children_id:
        cat_child.append(Category.Category(child_id))
    return cat_child



# create_Tree: creates a Tree object of the categories
def create_Tree(categories):
    print("category_helper.create_Tree: Generating Tree object of categories")
    t = Tree()
    root = t.add_child(name="root")  # create root node

    # first add all top level categories
    print("create_Tree: adding top level categories")
    for category in categories:
        if category.parent == 1:  # if it is a top level category
            root.add_child(name=category.name)

    # then populate children
    print("create_Tree: populating children node Categories")
    for category in categories:
        if category.parent != 1:
            nodes = t.search_nodes(name=category_id_to_name(category.parent))
            for node in nodes:
                node.add_child(name=category.name)

    print("\tlength of created tree: ", len("root"))

    return t
