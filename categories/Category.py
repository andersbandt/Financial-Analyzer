# import needed packages
# import gobject
import os
import xml.dom.minidom
from xml.sax.saxutils import escape

"""
Categories represents the possible financial categories set in categories.xml and sub_categories.xml
categories.xml contains all the master categories
sub_categories.xml contains all the children categories
"""


class Category:
    def __init__(self, category_id, name, parent, keywords):
        self.category_id = int(category_id)
        self.name = name
        self.parent = parent

        self.keyword = []
        self.description = None

        for keyword in keywords:
            if self.category_id == keyword[1]:
                self.keyword.append(keyword[2])

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
