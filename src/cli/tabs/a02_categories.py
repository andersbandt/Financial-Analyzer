"""
@file a04_load_data.py
@brief sub menu for loading in raw financial data and storing in database

"""

# import user defined modules
import db.helpers as dbh
from categories import categories_helper as cath
import cli.cli_helper as clih
import cli.cli_printer as clip
from cli.cli_class import SubMenu
from cli.cli_class import Action


class TabCategory(SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None

        # initialize information about sub menu options
        action_arr = [Action("Add category", self.a01_add_category),
                      Action("Print categories", self.a02_print_category),
                      Action("Add keyword", self.a03_manage_keywords),
                      Action("Print keywords", self.a04_print_keywords),
                      Action("Delete category", self.a05_delete_category),
                      Action("Update parent of category", self.a06_move_parent),
                      Action("Delete a keyword", self.a07_delete_keyword)
                      ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

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
        category_name = clih.spinput("\nWhat is this new category name?: ", inp_type="text")

        # insert_category: inserts a category into the SQL database
        dbh.category.insert_category(category_name, parent_id)
        return True

    def a02_print_category(self):
        print("... printing categories ...")

        # print out ASCII tree of categories
        tree = cath.create_Tree(cath.load_categories(), cat_type="name")
        tree_ascii = tree.get_ascii(compact=False, show_internal=True)
        tree.get_ascii()
        print(tree_ascii)

        # print out raw SQl table
        categories = dbh.category.get_category_ledger_data()
        clip.print_variable_table(["Category ID", "Parent ID", "NAme"],
                                  categories)
        return True

    # TODO (low-priority): some category check improvements
        # perform some verification on database integrity
        #   - no double names
        #   - no disconnected categories (all in tree structure)

    def a03_manage_keywords(self):
        print("... managing keywords ...")
        category_id = clih.category_prompt_all("Please enter the associated category of this keyword", True)
        if category_id is False:
            print("Ok, quitting add keyword")
            return False

        keyword_string = clih.spinput("What is the string for this keyword?  "
                                      "*note that it will be converted to all uppercase\n\tkeyword :",
                                      inp_type="text")
        keyword_string = keyword_string.upper()

        # check if keyword string already exists
        cat_id_for_keyword = dbh.keywords.get_category_id_for_keyword(keyword_string)
        if len(cat_id_for_keyword) != 0:
            print("Keyword string already exists for category ID: ", cat_id_for_keyword)
            print("ERROR: can't add keyword if string already exists!")
            return False

        dbh.keywords.insert_keyword(keyword_string, category_id)

        print("Ok, added keyword: ", keyword_string)
        print("\tfor category", cath.category_id_to_name(category_id))

    def a04_print_keywords(self):
        print("... printing keywords ...")

        # get input on what type of keyword print to do
        print_options = ["ALL", "PER CATEGORY"]
        print_type = clih.prompt_num_options("What type of print do you want to perform?: ",
                                             print_options)

        if print_type == 1:
            keyword_lg = dbh.keywords.get_keyword_ledger_data()
        elif print_type == 2:
            category_id = clih.category_prompt_all("What category to print keywords for?", False)
            keyword_lg = dbh.keywords.get_keyword_for_category_id(category_id)
        else:
            print("INVALID KEYWORD PRINTING!!!")
            return False

        table_values = []
        for keyword in keyword_lg:
            cat_name = cath.category_id_to_name(keyword[1])
            table_values.append([cat_name, keyword[2]])
        clip.print_variable_table(
            ["Category", "Keyword String"],
            table_values
        )

    def a05_delete_category(self):
        # print out all categories
        self.a02_print_category()

        print("Infinite loop started to delete categories. Enter 'q' or 'quit' at anytime to exit")
        status = True
        while status:
            category_id = clih.spinput("What is the category ID you want to DROP?", inp_type="int")
            if category_id is False:
                return None
            dbh.category.delete_category(category_id)
            print("Ok deleted category with ID: " + str(category_id))

    def a06_move_parent(self):
        print("... moving parent category for ID ...")
        category_id = clih.category_prompt_all("What category do you want to change the parent for?",
                                               False)  # setting display=False

        new_parent_id = clih.category_prompt_all("What is the new parent for this category?", False)

        # do some checking on the parent move?
        confirm = clih.spinput("Move category " + \
                               cath.category_id_to_name(category_id) + \
                               " to parent " + \
                               cath.category_id_to_name(new_parent_id) + \
                               " ? (y) or (n): ",
                               inp_type="text")

        if confirm != 'y':
            print("Ok, aborting category parent move")
            return

        # make database change
        dbh.category.update_parent(category_id, new_parent_id)

        print(
            f"Updated {cath.category_id_to_name(category_id)} to parent {cath.category_id_to_name(new_parent_id)} !!! Ok!")

    # a07_delete_keyword: prompts user to delete keywords. Modeleed after a05_delete_category
    def a07_delete_keyword(self):
        # print out keywords
        self.a04_print_keywords()

        print("Infinite loop started to delete keyword. Enter 'q' or 'quit' at anytime to exit")
        status = True
        while status:
            keyword_id = clih.spinput("What is the keyword ID you want to DROP?", inp_type="int")
            if keyword_id is False:
                return None
            dbh.keywords.delete_keyword(keyword_id)
            print("Ok deleted keyword with SQL ID: " + str(keyword_id))

    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################
