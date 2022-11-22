
# import needed modules
import tkinter as tk
from tkinter import *

import sqlite3
from ete3 import Tree, TreeStyle, Tree, TextFace, add_face_to_node

# import user defined modules
from categories import category_helper
from db import db_helper
from Finance_GUI import gui_helper

# TODO: add ability to delete category
class tabEditCategory:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.prompt = Text(self.frame, padx=5, pady=5, height=5)

        self.load_yes = 0  # yes button to loading statement data
        self.load_no = 0  # no button for loading statement data

        # unsure what these are for
        self.statement = 0
        self.times_analyze_ran = 0

        # set up text box for user communication
        Label(self.frame, text="Console Output").grid(row=7, column=1)
        self.prompt = Text(self.frame, padx=5, pady=5, height=10, width=50)
        self.prompt.grid(row=8, column=1)

        # run function to initialize the GUI tab content
        self.initTabContent()


    # initTabContent: initializes the main content of the tab
    def initTabContent(self):
        print("Initializing tab 3 content")
        # CATEGORY ADDING
        # dropdown for category parent
        parent_category_drop, parent_category_option = self.generate_all_category_dropdown()

        # checkbox for if the category has a parent category or not
        Label(self.frame, text="Select Parent Category").grid(row=0, column=0)

        var1 = tk.IntVar()
        tk.Checkbutton(self.frame, text="Parent", variable=var1, onvalue=1, offvalue=0,
                       command=lambda: self.toggle_show_parent(var1.get(), parent_category_drop)).grid(row=1, column=0)

        # set up user inputs for category information
        Label(self.frame, text="Category Name").grid(row=0, column=1)
        category_name = Text(self.frame, height=5, width=45)
        category_name.grid(row=1, column=1)

        # set up button add a category
        add_category = Button(self.frame, text="Add Category",
                              command=lambda: self.add_category_gui(category_name, var1.get(), parent_category_option.get()))  # category_name, parent
        add_category.grid(row=1, column=3)  # place 'Start Categorizing' button

        # ACCOUNT ADDING
        # TODO: add selector for 'type' of account
        # set up user inputs for account information
        Label(self.frame, text="Account Name").grid(row=3, column=1)
        account_name = Text(self.frame, height=5, width=45)
        account_name.grid(row=4, column=1)

        # set up button to add an account
        Button(self.frame, text="Add Account", command=lambda: self.add_account_gui(account_name)).grid(row=4, column=3)  # place 'Start Categorizing' button

        # KEYWORD ADDING
        # add drop down for category
        keyword_category_drop, keyword_category_option = self.generate_all_category_dropdown()
        keyword_category_drop.grid(row=6, column=0)

        # text input for user to add keyword
        Label(self.frame, text="Keyword Name").grid(row=5, column=1)
        keyword_name = Text(self.frame, height=5, width=45)
        keyword_name.grid(row=6, column=1)

        # set up button to add a keyword
        add_keyword = Button(self.frame, text="Add Keyword", command=lambda: self.add_keyword_gui(keyword_category_option.get(), keyword_name))
        add_keyword.grid(row=6, column=3)  # place 'Start Categorizing' button

        # set up button to display categories flow chart
        show_categories = Button(self.frame, text="Show Category Chart", command=lambda: self.show_category_tree_diagram())
        show_categories.grid(row=9, column=1)  # place 'Start Categorizing' button


    ##############################################################################
    ####      ADDING FUNCTIONS    ############################################
    ##############################################################################
# TODO: add some error checking to see if the text box is blank on all of the 3 below text boxes

    # add_category_gui: attempts to add a category to the SQL database
    def add_category_gui(self, category_name_obj, parent_status, parent):
        if parent_status == 0:
            parent = 1
        else:
            parent = category_helper.category_name_to_id(parent)

        category_name = category_name_obj.get("1.0", "end")
        category_name = category_name.strip('\n')

        if db_helper.insert_category(parent, category_name):
            gui_helper.gui_print(self.frame, self.prompt, "Added category: ", category_name)
            category_name_obj.delete("1.0", "end")
        else:
            gui_helper.gui_print(self.frame, self.prompt, "Something went wrong adding category")

    # add_account_gui: attempts to add a category to the SQL database
    def add_account_gui(self, account_text_obj):
        account_name = account_text_obj.get("1.0", "end").strip("\n")

        try:
            new_account_id = db_helper.insert_account(account_name)
        except Exception as e:
                print("Uh oh, something went wrong with adding to category table: ", e)
        else:
            gui_helper.gui_print(self.frame, self.prompt, "Added account: ", account_name, " with id: ", new_account_id)
            account_text_obj.delete("1.0", "end")

    # add_keyword_gui: attempts to add a keyword to the SQL database
    def add_keyword_gui(self, category_name, keyword_text_obj):
        keyword = keyword_text_obj.get("1.0", "end")
        keyword = keyword.strip('\n')

        #try:
        #    category_id = category_helper.category_name_to_id(category_name)
        #except Error as e:
        #    gui_helper.gui_print(self.frame, self.prompt, "ERROR: ")

        with self.conn:
            try:
                self.cur.execute('INSERT INTO keywords (category_id, keyword) \
                VALUES(?, ?)', (category_id, keyword))
            except sqlite3.Error as e:
                print("Uh oh, something went wrong with adding to keyword table: ", e)
            else:
                gui_helper.gui_print(self.frame, self.prompt, "Added keyword: ", keyword, " to category: ", category_name)
                keyword_text_obj.delete("1.0", "end")

    ##############################################################################
    ####      HELPER FUNCTIONS          ##########################################
    ##############################################################################

    # generate a drop down menu with all categories in SQL database
    def generate_all_category_dropdown(self):
        categories = db_helper.get_category_names()

        clicked_category = StringVar()  # datatype of menu text
        clicked_category.set(categories[0])  # initial menu text
        drop = OptionMenu(self.frame, clicked_category, *categories)  # create drop down menu of months
        return drop, clicked_category

    # toggle_show_parent
    def toggle_show_parent(self, status, dropdown):
        if status == 1:
            dropdown.grid(row=2, column=0)
        else:
            dropdown.grid_forget()


# TODO: finish this function for drawing Category tree in my style
    def show_category_tree_diagram(self):
        # print ASCII of tree using TreeStyle()?/
        categories = category_helper.load_categories()

        # create Tree object
        t = category_helper.create_Tree(categories)
        print("guiTab_3_editCategory.show_category_treediagram: printing tree below")
        print(t.get_ascii(show_internal=True))

        # set up TreeStyle for our tree object
        ts = TreeStyle()
        ts.show_leaf_name = False

        def my_layout(node):  # this adds the recursive node labeling behavior. (I think)
            # create a text face
            f = TextFace(node.name, tight_text=False)  # create name of node

            # set some attributes
            f.margin_top = 25
            f.margin_right = 25
            f.margin_left = 25
            f.margin_bottom = 25

            f.border.width = 1

            # add the text face to the node
            add_face_to_node(f, node, column=0, position="branch-right")  # add TextFace,

        ts.layout_fn = my_layout  # set layout of TreeStyle() object
        ts.scale = 50  # adjust scale

        # display the final category tree
        #tk.Label(self.frame, text=t.get_ascii(), width=40).grid(row=0, column=4, rowspan=8)

        #t.show(layout=my_layout, tree_style=ts, name='ETE')  # start an interactive session to visualize the current node
        #t.render("category_tree.png", w=180, units="mm", tree_style=ts)  # renders the node structure as an image

        ### trying a new method
        w = 500
        h = 300
        canvas = Canvas(self.frame, width=w, height=h, bg="white")
        canvas.grid(row=0, column=4, rowspan=8)

        #gui_helper.paintBranch(canvas, 5, 100, 200, 40, math.pi / 2)

        x = 1
        y = 1

        top_categories = category_helper.get_top_level_categories()
        num_top_level = len(top_categories)

        y_space = int((h-20)/num_top_level)
        x_space = int((w - 20) / 5)  # the denominator should be the length of the tree

        x_start = 10

        y = 0
        x = 1
        for category in top_categories:
            category_helper.draw_Category_gui_obj(category.category_id, canvas, x_start, 10 + y*y_space)
            for child_category in category.children:
                category_helper.draw_Category_gui_obj(child_category, canvas, x_start + x*x_space)

            y += 1
