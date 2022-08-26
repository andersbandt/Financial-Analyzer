# import needed packages
import tkinter as tk
from tkinter import *
from tkinter import ttk

import lambdas
import sqlite3

# import user defined modules
from Statement_Classes import Statement
from categories import category_helper
from categories import Category

from ete3 import Tree, TreeStyle, Tree, TextFace, add_face_to_node

from Finance_GUI import gui_helper


class tabEditCategory:
    def __init__(self, master, conn):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.prompt = Text(self.frame, padx=5, pady=5, height=5)

        self.load_yes = 0  # yes button to loading statement data
        self.load_no = 0  # no button for loading statement data

        # unsure what these are for
        self.statement = 0
        self.times_analyze_ran = 0

        # set up text box for user communication
        label = Label(self.frame, text="Console Output")
        label.grid(row=7, column=1)
        self.prompt = Text(self.frame, padx=5, pady=5, height=10, width = 25)
        self.prompt.grid(row=8, column=1)

        # establish SQL database properties
        self.conn = conn
        self.cur = self.conn.cursor()

        # run function to initialize the GUI tab content
        self.initTabContent()



    # initTabContent: initializes the main content of the tab
    def initTabContent(self):
        print("Initializing tab 3 content")
        # CATEGORY ADDING
        # dropdown for category parent
        parent_category_drop, parent_category_option = self.generate_all_category_dropdown()

        # checkbox for if the category has a parent category or not
        label = Label(self.frame, text="Select Parent Category")
        label.grid(row=0, column=0)

        var1 = tk.IntVar()
        c1 = tk.Checkbutton(self.frame, text="Parent", variable=var1, onvalue=1, offvalue=0,
                            command=lambda: self.toggle_show_parent(var1.get(), parent_category_drop))
        c1.grid(row=1, column=0)

        # set up user inputs for category information
        label = Label(self.frame, text="Category Name")
        label.grid(row=0, column=1)
        category_name = Text(self.frame, height=6, width=20)
        category_name.grid(row=1, column=1)

        # set up button add a category
        add_category = Button(self.frame, text="Add Category",
                              command=lambda: self.add_category(category_name, var1.get(), parent_category_option.get()))  # category_name, parent
        add_category.grid(row=1, column=3)  # place 'Start Categorizing' button

        # ACCOUNT ADDING
        # set up user inputs for account information
        label = Label(self.frame, text="Account Name")
        label.grid(row=3, column=1)
        account_name = Text(self.frame, height=6, width=20)
        account_name.grid(row=4, column=1)

        # set up button to add an account
        add_account = Button(self.frame, text="Add Account",
                             command=lambda: self.add_account(account_name.get(1.0, "end")))
        add_account.grid(row=4, column=3)  # place 'Start Categorizing' button

        # KEYWORD ADDING
        # add drop down for category
        keyword_category_drop, keyword_category_option = self.generate_all_category_dropdown()
        keyword_category_drop.grid(row=6, column=0)

        # text input for user to add keyword
        label = Label(self.frame, text="Keyword Name")
        label.grid(row=5, column=1)
        keyword_name = Text(self.frame, height=6, width=20)
        keyword_name.grid(row=6, column=1)

        # set up button to add a keyword
        add_keyword = Button(self.frame, text="Add Keyword",
                             command=lambda: self.add_keyword(keyword_category_option.get(), keyword_name))
        add_keyword.grid(row=6, column=3)  # place 'Start Categorizing' button


        # set up button to display categories flow chart
        show_categories = Button(self.frame, text="Show Category Chart", command=lambda: self.show_category_tree_diagram())
        show_categories.grid(row=9, column=1)  # place 'Start Categorizing' button


    ##############################################################################
    ####      SQL ADDING FUNCTIONS    ############################################
    ##############################################################################

    # add_category: attempts to add a category to the SQL database
    def add_category(self, category_name_obj, parent_status, parent):
        if parent_status == 0:
            parent = 1
        else:
            parent = category_helper.category_name_to_id(self.conn, parent)

        category_name = category_name_obj.get("1.0", "end")
        category_name = category_name.strip('\n')

        with self.conn:
            self.cur.execute('SELECT category_id FROM category')
            category_id = self.cur.fetchall()[-1][0] + 1  # grab latest addition (should be highest value) and add 1
            try:
                self.cur.execute('INSERT INTO category (category_id, parent, name) \
                VALUES(?, ?, ?)', (category_id, parent, category_name))
            except sqlite3.Error as e:
                print("Uh oh, something went wrong with adding to category table: ", e)
            else:
                gui_helper.gui_print(self.frame, self.prompt, "Added category: ", category_name, " with id: ", category_id)
                category_name_obj.delete("1.0", "end")

    # add_account: attempts to add a category to the SQL database
    def add_account(self, account_name):
        with self.conn:
            self.cur.execute('SELECT account_id FROM account')
            new_account_id = self.cur.fetchall()[-1][0] + 1  # grab latest addition (should be highest value) and add 1
            try:
                self.cur.execute('INSERT INTO account (account_id, name) \
                VALUES(?, ?)', (new_account_id, account_name))
            except sqlite3.Error as e:
                print("Uh oh, something went wrong with adding to category table: ", e)
            else:
                print("Added account: ", account_name, " with id: ", new_account_id)

# TODO: get text box content to be erased upon completion of this function
    # add_keyword: attempts to add a keyword to the SQL database
    def add_keyword(self, category_name, keyword_text_obj):
        keyword = keyword_text_obj.get("1.0", "end")
        keyword = keyword.strip('\n')
        category_id = category_helper.category_name_to_id(self.conn, category_name)

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
        with self.conn:
            self.cur.execute('SELECT name FROM category')
            categories = self.cur.fetchall()

        i = 0
        for category in categories:
            categories[i] = gui_helper.convertTuple(category)
            i += 1

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


    def show_category_tree_diagram(self):
        # print ASCII of tree using TreeStyle()?/
        categories = category_helper.load_categories(self.conn)

        # create Tree object
        t = category_helper.create_Tree(self.conn, categories)

        # set up TreeStyle for our tree object
        ts = TreeStyle()
        ts.show_leaf_name = False
        def my_layout(node): # this adds the recursive node labeling behavior. (I think)
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
        ts.scale = 90  # adjust scale

        # display the final category tree
        #t.show(layout=my_layout, tree_style=ts, name='ETE')  # start an interative session to visualize the current node
        #self.master.geometry('1300x1000')
        t.render("category_tree.png", w=183, units="mm", tree_style=ts)  # renders the node structure as an image

