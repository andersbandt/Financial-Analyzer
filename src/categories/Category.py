# import needed modules


# import user defined modules
import db.helpers as dbh
from categories import categories_helper as cath


class Category:
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
                # TODO: phase this .upper() out? Maybe by making SURE that loaded keywords into SQL are already uppercase?
                keyword[2].upper()
            )  # keyword string is third column of sql data structure


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


    def rename_category(self):
        print("Executing rename_category")


    def add_child(self):
        print("Executing add_child")


    def delete_category(self):
        print("Executing delete_category")
