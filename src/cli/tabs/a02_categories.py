"""
@file a04_load_data.py
@brief sub menu for loading in raw financial data and storing in database

"""

# import user defined modules
from categories import categories_helper as cath
import cli.cli_helper as clih
from cli.tabs import SubMenu

import db.helpers as dbh


class TabCategory(SubMenu.SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None

        # initialize information about sub menu options
        action_strings = ["Add category",
                          "Print categories",
                          "Add keyword",
                          "Print keywords",
                          "Delete category",
                          "Update parent of category",
                          "Delete a keyword"]

        action_funcs = [self.a01_add_category,
                        self.a02_check_category,
                        self.a03_manage_keywords,
                        self.a04_print_keywords,
                        self.a05_delete_category,
                        self.a06_move_parent,
                        self.a07_delete_keyword]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)


    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_add_category(self):
        print("... adding a category ...")

        # determine if this is top level
        top_res = clih.promptYesNo("Is this a top level category?")

        # find parent category to populate
        if not top_res:
            # determine parent category
            parent_id = clih.category_tree_prompt()
        else:
            parent_id = 1

        # prompt for name
        category_name = clih.spinput("What is this new category name?: ")

        # insert_category: inserts a category into the SQL database
        dbh.category.insert_category(category_name, parent_id)
        return True


    def a02_check_category(self):
        print("... checking categories ...")

        # print out ASCII tree of categories
        tree = cath.create_Tree(cath.load_categories(), cat_type="name")

        # METHOD 1: using get_ascii function
        tree_ascii = tree.get_ascii(compact=False, show_internal=True)
        tree.get_ascii()
        print(tree_ascii)

        # perform some verification on database integrity
        #   - no double names
        #   - no disconnected categories (all in tree structure)



    def a03_manage_keywords(self):
        print("... managing keywords ...")
        category_id = clih.category_prompt_all("Please enter the associated category of this keyword", True)

        keyword_string = clih.spinput("What is the string for this keyword?  "
                                      "*note that it will be converted to all uppercase\n\tkeyword :",
                                      type="text")
        keyword_string = keyword_string.upper()

        # check if keyword string already exists
        cat_id_for_keyword = dbh.keywords.get_category_id_for_keyword(keyword_string)
        if len(cat_id_for_keyword) != 0:
            print("Keyword string already exists for category ID: ", cat_id_for_keyword)
            print("ERROR: can't add keyword if string already exists!")
            return

        dbh.keywords.insert_keyword(keyword_string, category_id)

        print("Ok, added keyword: ", keyword_string)
        print("\tfor category", cath.category_id_to_name(category_id))


    def a04_print_keywords(self):
        print("... printing keywords ...")
        keyword_lg = dbh.keywords.get_keyword_ledger_data()

        for keyword in keyword_lg:
            cat_name = cath.category_id_to_name(keyword[1])
            print(cat_name + ": " + str(keyword[2]))


    def a05_delete_category(self):
        categories = dbh.category.get_category_ledger_data()

        for item in categories:
            print(item)

        category_id = clih.spinput("What is the category ID you want to DROP?", type="int")
        dbh.category.delete_category(category_id)
        print("Ok deleted category with ID: " + str(category_id))


    def a06_move_parent(self):
        print("... moving parent category for ID ...")
        category_id = clih.category_prompt_all("What category do you want to change the parent for?", False) # setting display=False

        new_parent_id = clih.category_prompt_all("What is the new parent for this category?", False)

        # do some checking on the parent move?
        confirm = clih.spinput("Move category "  + \
                               cath.category_id_to_name(category_id)  + \
                               " to parent " + \
                               cath.category_id_to_name(new_parent_id) + \
                               " ? (y) or (n): ",
                               inp_type="text")

        if confirm != 'y':
            print("Ok, aborting category parent move")
            return

        # make database change
        dbh.category.update_parent(category_id, new_parent_id)

        print(f"Updated {cath.category_id_to_name(category_id)} to parent {cath.category_id_to_name(new_parent_id)} !!! Ok!")


    # TODO: finish this function to delete a keyword
    def a07_delete_keyword(self):
        print("... deleting keyword ...")

        res = clih.promptYesNo("Do you want to delete keyword (y or n)?: ")
        if not res:
            print("Ok not deleting keyword")
            return

    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################




