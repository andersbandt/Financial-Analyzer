import sqlite3
from ete3 import Tree

from categories import Category
from databases import database_helper


##############################################################################
####      VARIOUS FUNCTIONS    ###############################################
##############################################################################

# load_categories: returns an array containing all the category objects
def load_categories():
    categories_sql = database_helper.get_category_ledger_data()
    keywords = database_helper.get_keyword_ledger_data()

    categories = []
    for category_sql in categories_sql:
        categories.append(Category.Category(category_sql[0], category_sql[2], category_sql[1], keywords))

    return categories


def check_categories(categories_array):
    for category in categories_array:
        if category.keyword is None:
            print("Uh oh, category: " + category.name + " has no keywords associated with it")


def print_categories(categories_array):
    for category in categories_array:
        category.print()


# get_category_strings: returns an array containing strings of all the category names
def get_category_strings(categories_array):
    category_names = []
    for category in categories_array:
        category_names.append(category.getName())

    return category_names


# category_name_to_id: converts a category name to the ID
def category_name_to_id(category_name):
    return database_helper.get_category_id_from_name(category_name)

# category_id_to_name
def category_id_to_name(category_id):
    return database_helper.get_category_name_from_id(category_id)


def create_Tree(categories):
    t = Tree()
    root = t.add_child(name="root")

    for category in categories:
        print("Examining category", category.name)
        if category.parent == 1:  # if it is a top level category
            root.add_child(name=category.name)
        else:
            nodes = t.search_nodes(name=category_id_to_name(category.parent))
            for node in nodes:
                node.add_child(name=category.name)

    #print(t)
    print(t.get_ascii(show_internal=True))
    return t

