


# import user defined modules
import db.helpers as dbh
from categories import categories_helper as cath


class Account:
    def __init__(self, category_id):
        self.id = int(category_id)

        # grab sql data
        cat_sql_data = dbh.category.get_category_info(category_id)
        self.name = cat_sql_data[0][2]
        self.parent = cat_sql_data[0][1]

        # populate children category_id
        self.children_id = cath.get_category_children(category_id, printmode=None)

        # what is this description used for?
        self.description = None

        # populate keywords
        self.keyword = []
        keywords = dbh.keywords.get_keyword_for_category_id(self.id)
        for keyword in keywords:
            self.keyword.append(
                keyword[2]
            )  # keyword string is third column of sql data structure

        # GUI stuff
        self.master = 0
        self.frame = 0

        # drawing rectangle GUI stuff
        self.canvas = 0
        self.x = 0  # x and y coordinates
        self.y = 0
        self.w = 0  # width
        self.h = 0  # height
        self.option_drop = 0

    # print_category: prints a categories name to the console
    def print_category(self):
        # print("Category parent: " + self.parent)
        print("Category name: ", self.name)
        print("\t\tparent: ", str(self.parent))
        print("\t\tkeywords: ")
        print(self.keyword)


    # getName: gets the name of a category
    def getName(self):
        return self.name


    def rename_account(self):
        print("Executing rename_category")


    def add_child(self):
        print("Executing add_child")


    def delete_category(self):
        print("Executing delete_category")
