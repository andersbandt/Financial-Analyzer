# import needed packages
import sqlite3
from categories import Category

from ete3 import Tree

##############################################################################
####      VARIOUS FUNCTIONS    ###############################################
##############################################################################

# load_categories: returns an array containing all the category objects
def load_categories(conn):
    cur = conn.cursor()
    with conn:
        try:
            cur.execute('SELECT * FROM category')
            categories_sql = cur.fetchall()
            cur.execute('SELECT * FROM keywords')
            keywords = cur.fetchall()
        except sqlite3.Error as e:
            print("Uh oh, something went wrong requesting categories")

    categories = []
    for category_sql in categories_sql:
        categories.append(Category.Category(category_sql[0], category_sql[2], category_sql[1], keywords))

    return categories


def check_categories(categories_array):
    for category in categories_array:
        if category.keyword == None:
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
def category_name_to_id(conn, category_name):
    cur = conn.cursor()
    with conn:
        try:
            #conn.set_trace_callback(print)
            cur.execute('SELECT category_id FROM category WHERE name=?', [category_name])
            #conn.set_trace_callback(None)
        except sqlite3.Error as e:
            print("Uh oh, something went wrong finding category ID from name: ", e)
            return False

        try:
            return cur.fetchall()[0][0] # have to get the first tuple element in array of results
        except IndexError as e:
            print("ERROR (probably no results found for SQL query): ", e)


# category_id_to_name
def category_id_to_name(conn, category_id):
    cur = conn.cursor()
    #print("category_id_to_name got this for category_id", category_id)
    with conn:
        try:
            cur.execute('SELECT name FROM category WHERE category_id=?', [category_id])
        except sqlite3.Error as e:
            print("Uh oh, something went wrong with finding category name from ID: ", e)
            return False

        return cur.fetchall()[0][0]


def create_Tree(conn, categories):
    t = Tree()
    root = t.add_child(name="root")

    for category in categories:
        print("Examining category", category.name)
        if category.parent == 1:
            root.add_child(name=category.name)
        else:
            nodes = t.search_nodes(name=category_id_to_name(conn, category.parent))
            for node in nodes:
                node.add_child(name=category.name)

    #print(t)
    print(t.get_ascii(show_internal=True))
    return t

