
# import needed modules
from tkinter import *

# import user defined packages
from categories import category_helper


# TODO: refactor 'category_id' to 'id'. Might be tedious
class Category:
    def __init__(self, category_id, name, parent, keywords):
        self.category_id = int(category_id)
        self.name = name
        self.parent = parent

        self.children = category_helper.get_category_children(category_id)  # uncomment when function is finished

        self.keyword = []
        self.description = None

        # populate keywords
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


    def draw_Category_gui_obj(self, canvas, x, y):
        # This will create style object
        style = Style()

        # This will be adding style, and
        # naming that style variable as
        # W.Tbutton (TButton is used for ttk.Button).
        style.configure('W.TButton', font=('calibri', 10, 'bold', 'underline'), foreground='red')

        btn1 = Button(canvas, text=self.name, style='W.TButton', command=self.inter_gui)
        btn1.grid(row=y, column=x, padx=10)


    def inter_gui(self):
        print("Executing interactive category function")