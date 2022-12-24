# import needed modules
import math
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Style

import PyQt5  # necessary for 'ete3.TreeStyle' to be imported
from ete3 import TextFace, Tree, TreeStyle, add_face_to_node

import db.helpers as dbh
# import user defined modules
from categories import categories_helper
from gui import gui_helper


# TODO: add ability to delete category
class tabEditCategory:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        # init frames within tab
        self.fr_add_data = tk.Frame(self.frame, bg="#00bcd4")
        self.fr_add_data.grid(row=0, column=0, padx=5, pady=5)

        self.fr_view_cat = tk.Frame(self.frame, bg="#00bcd4")
        self.fr_view_cat.grid(row=0, column=1, rowspan=2, padx=5, pady=5)

        self.fr_prompt = tk.Frame(self.frame, bg="gray")
        self.fr_prompt.grid(row=1, column=0, padx=5, pady=5)

        self.load_yes = 0  # yes button to loading statement data
        self.load_no = 0  # no button for loading statement data

        # unsure what these are for
        self.statement = 0
        self.times_analyze_ran = 0

        # set up text box for user communication
        tk.Label(self.fr_prompt, text="Console Output").grid(row=0, column=0, pady=10)
        self.prompt = tk.Text(self.fr_prompt, padx=10, pady=10, height=5, width=50)
        self.prompt.grid(row=1, column=0, padx=10, pady=10)

        # run function to initialize the GUI tab content
        self.initTabContent()

    # initTabContent: initializes the main content of the tab
    def initTabContent(self):
        print("Initializing tab 3 content")

        self.init_fr_add_data()
        self.init_fr_view_cat()

    def init_fr_add_data(self):
        # print frame title
        tk.Label(self.fr_add_data, text="Add Category Data", font=("Arial", 16)).grid(
            row=0, column=0, columnspan=5, padx=3, pady=3
        )

        # params for text box inputs
        h = 2
        w = 20

        # CATEGORY ADDING
        # dropdown for category parent
        (
            parent_category_drop,
            parent_category_option,
        ) = gui_helper.generate_all_category_dropdown(self.fr_add_data)

        # checkbox for if the category has a parent category or not
        tk.Label(self.fr_add_data, text="Select Parent Category").grid(row=1, column=0)
        var1 = tk.IntVar()
        tk.Checkbutton(
            self.fr_add_data,
            text="Parent",
            variable=var1,
            onvalue=1,
            offvalue=0,
            command=lambda: self.toggle_show_parent(var1.get(), parent_category_drop),
        ).grid(row=2, column=0)

        # set up user inputs for category information
        tk.Label(self.fr_add_data, text="Category Name").grid(row=1, column=1, pady=5)
        category_name = tk.Text(self.fr_add_data, height=h, width=w)
        category_name.grid(row=2, column=1, columnspan=2)

        # set up button add a category
        add_category = tk.Button(
            self.fr_add_data,
            text="Add Category",
            command=lambda: self.add_category_gui(
                category_name, var1.get(), parent_category_option.get()
            ),
        )  # category_name, parent
        add_category.grid(row=4, column=3)  # place 'Add Category' button

        # ACCOUNT ADDING
        # TODO: add selector for 'type' of account
        # set up user inputs for account information
        tk.Label(self.fr_add_data, text="Account Name").grid(row=5, column=1, pady=5)
        account_name = tk.Text(self.fr_add_data, height=h, width=w)
        account_name.grid(row=6, column=1)

        # set up button to add an account
        tk.Button(
            self.fr_add_data,
            text="Add Account",
            command=lambda: self.add_account_gui(account_name),
        ).grid(
            row=7, column=3
        )  # place 'Start Categorizing' button

        # KEYWORD ADDING
        # add drop down for keyword
        (
            keyword_category_drop,
            keyword_category_option,
        ) = gui_helper.generate_all_category_dropdown(self.fr_add_data)
        keyword_category_drop.grid(row=9, column=0)

        # text input for user to add keyword
        tk.Label(self.fr_add_data, text="Keyword Name").grid(row=8, column=1, pady=5)
        keyword_name = tk.Text(self.fr_add_data, height=h, width=w)
        keyword_name.grid(row=9, column=1)

        # set up button to add a keyword
        add_keyword = tk.Button(
            self.fr_add_data,
            text="Add Keyword",
            command=lambda: self.add_keyword_gui(
                keyword_category_option.get(), keyword_name
            ),
        )
        add_keyword.grid(row=10, column=3)  # place 'Start Categorizing' button

    # init_fr_view_cat: inits Frame for viewing category tree
    def init_fr_view_cat(self):
        # print frame title
        tk.Label(self.fr_view_cat, text="View Categories", font=("Arial", 16)).grid(
            row=0, column=0, columnspan=5, padx=3, pady=3
        )

        # set up button to display categories flow chart
        style = Style()
        style.configure(
            "W.TButton", font=("calibri", 10, "bold", "underline"), foreground="red"
        )

        # show_categories = ttk.Button(self.fr_view_cat,
        #                              text="Show Category Chart",
        #                              style='W.TButton',
        #                              command=lambda: self.show_category_tree_diagram(printmode="debug"))  # PRINTMODE
        # show_categories.grid(row=0, column=1)  # place 'Start Categorizing' button

        # print out ASCII tree
        self.renderTree()
        self.show_category_tree_diagram(printmode="debug")

    ##############################################################################
    ####      ADDING FUNCTIONS        ############################################
    ##############################################################################

    # add_category_gui: attempts to add a category to the SQL database
    def add_category_gui(self, category_name_obj, parent_status, parent):
        # set new category parent status
        if parent_status == 0:  # if we are creating a top level category
            parent = 1  # set parent as 1
        else:
            stripped_parent = parent[2 : len(parent) - 3]
            print("Got this for parent: ", stripped_parent)
            parent = categories_helper.category_name_to_id(
                stripped_parent
            )  # otherwise set parent to category_id of chosen parent

        category_name = category_name_obj.get("1.0", "end").strip(
            "\n"
        )  # I THINK THIS CATEGORY NAME IS GETTING STRIPPED WRONG
        if category_name == "":
            gui_helper.alert_user(
                "Can't have category blank", "Please fill in category name", "error"
            )

        res = dbh.insert_category(parent, category_name)
        if res:
            gui_helper.gui_print(
                self.frame, self.prompt, "Added category: ", category_name
            )
            category_name_obj.delete("1.0", "end")
            self.show_category_tree_diagram()
        else:
            gui_helper.gui_print(
                self.frame, self.prompt, "Something went wrong adding category"
            )

    # add_account_gui: attempts to add a category to the SQL database
    # TODO: refactor to add account 'type' support
    def add_account_gui(self, account_text_obj):
        account_name = account_text_obj.get("1.0", "end").strip("\n")
        if account_name == "":
            gui_helper.alert_user(
                "Can't have account name blank", "Please fill in account name", "error"
            )

        try:
            new_account_id = dbh.account.insert_account(account_name)
        except Exception as e:
            print("Uh oh, something went wrong with adding to category table: ", e)
        else:
            gui_helper.gui_print(
                self.frame,
                self.prompt,
                "Added account: ",
                account_name,
                " with id: ",
                new_account_id,
            )
            account_text_obj.delete("1.0", "end")
        # TODO: make it update drawn category tree if enabled

    # add_keyword_gui: attempts to add a keyword to the SQL database
    def add_keyword_gui(self, category_name, keyword_text_obj):
        keyword = keyword_text_obj.get("1.0", "end").strip("\n")
        keyword = keyword.strip("\n")
        if keyword == "":
            gui_helper.alert_user(
                "Can't have keyword blank", "Please fill in keyword name", "error"
            )

        category_name = category_name[2 : len(category_name) - 3]
        category_id = categories_helper.category_name_to_id(category_name)

        res = dbh.keywords.insert_keyword(keyword, category_id)
        if not res:
            gui_helper.gui_print(
                self.frame, self.prompt, "Uh oh, something went wrong adding keyword"
            )
        else:
            gui_helper.gui_print(
                self.frame,
                self.prompt,
                "Added keyword: ",
                keyword,
                " to category: ",
                category_name,
            )
            keyword_text_obj.delete("1.0", "end")

    ##############################################################################
    ####      HELPER FUNCTIONS          ##########################################
    ##############################################################################

    # generate a drop down menu with all categories in SQL database
    def generate_all_category_dropdown(self, frame):
        categories = dbh.category.get_category_names()

        clicked_category = tk.StringVar()  # datatype of menu text
        clicked_category.set(categories[0])  # initial menu text
        drop = tk.OptionMenu(
            frame, clicked_category, *categories
        )  # create drop down menu of months
        return drop, clicked_category

    # toggle_show_parent
    def toggle_show_parent(self, status, dropdown):
        if status == 1:
            dropdown.grid(row=3, column=0)
        else:
            dropdown.grid_forget()

    # TODO: generating the category tree eliminates vertical scroll bar
    def show_category_tree_diagram(self, printmode=None):
        from categories import Category

        if printmode == "debug":
            print("DEBUG: debugging guiTab_3_editCategory.show_category_tree_diagram()")

        # load all Category objects from SQL database
        categories = categories_helper.load_categories()

        ######
        ### trying a new method
        ######

        # set up Canvas
        w = 525
        h = 625
        canvas = tk.Canvas(self.fr_view_cat, width=w, height=h, bg="white")
        # canvas.grid(row=1, column=0, rowspan=3)
        canvas.grid(row=1, column=0, padx=25, pady=25)

        # add a scrollbar
        vsb = tk.Scrollbar(self.fr_view_cat, orient="vertical", command=canvas.yview)
        vsb.grid(row=0, column=1, rowspan=6, sticky="ns")
        canvas.configure(yscrollcommand=vsb.set)

        # generate top Category objects
        top_categories = categories_helper.get_top_level_categories()
        num_top_level = len(top_categories)

        y_pad = 75
        x_child_space = (
            int((w - 20) / 10) + 200
        )  # the denominator should be the length of the tree

        # set parameters for starting node location
        x_top = 150
        y_top = y_pad

        # set up category GUI object dimensions
        w = 100
        h = 30

        num_top = 0  # start at the lowest top level category and move our way up
        y_t_space = 125
        y_b_space = 0
        for category in top_categories:
            y_prev = y_top
            # y_top = y_prev + .3*num_top*y_top_space + y_spacer
            y_top = y_prev + y_t_space + y_b_space

            # DEBUG PRINTING
            print(
                "Drawing parent at = ", x_top, ",", y_top
            ) if printmode == "debug" else 0
            print("y_t_space = ", y_t_space) if printmode == "debug" else 0
            print("y_b_space = ", y_b_space) if printmode == "debug" else 0
            # draw top level parent node (all along same leftmost vertical row)
            category.draw_Category_gui_obj(
                canvas, x_top, y_top, w, h, kind="full", master=self.fr_view_cat
            )  # draw Category node

            # draw_children: draws the children for a Category 'cat' based on a starting x coordinate 'x_st'
            def draw_children(cat, x_st, y_st, max_angle, fill_color="gray"):
                print("Drawing children for category: ", cat.name)
                # generate angle matrix for drawing parent children
                num_children = len(cat.children_id)
                print("\tlength of children is ", str(num_children))
                angles = gui_helper.generate_tree_angles(num_children, max_angle)

                if angles is None:
                    raise Exception(
                        "ERROR: can't create category tree - angle matrix couldn't be generated for parent: ",
                        cat.name,
                    )

                for i in range(0, num_children):
                    tmp_Cat = Category(cat.children_id[i])
                    x_cord = x_st + x_child_space
                    y_cord = y_st + int(math.tan(angles[i]) * x_child_space)

                    # draw the child node
                    if printmode == "debug":
                        print(
                            "Drawing child at (x, y): "
                            + str(x_cord)
                            + ","
                            + str(y_cord)
                        )

                    tmp_Cat.draw_Category_gui_obj(
                        canvas,
                        x_cord,
                        y_cord,
                        w,
                        h,
                        kind="full",
                        fill_color=fill_color,
                        master=self.fr_view_cat,
                    )

                    # draw branch linking parent node to child node
                    gui_helper.drawLine(
                        canvas, x_st + w, y_st + h / 2, x_cord, y_cord + h / 2
                    )

                    # recursively call if Category has children
                    l = len(tmp_Cat.children_id)
                    if l > 0:
                        draw_children(
                            tmp_Cat,
                            x_st + x_child_space,
                            y_cord,
                            max_angle,
                            fill_color=fill_color,
                        )

            # if top level Category has children, start children drawing algorithm
            if len(category.children_id) > 0:
                # set up next top level category spacing based on children length
                y_t_space = int(
                    3.5 * h * math.sqrt(len(category.children_id))
                )  # the "top" spacing for the next parent

                # draw children
                max_angle = (
                    math.pi * 17 / 180
                )  # max +/- deviation in degrees from parent node
                draw_children(category, x_top, y_top, max_angle, fill_color="#062b19")

            # add bottom level spacing contribution
            if len(categories[num_top + 1].children_id) > 0:
                y_b_space = int(
                    3.5 * h * math.sqrt(len(categories[num_top + 1].children_id))
                )  # the "top" spacing for the next parent
            else:
                y_b_space = 0

            # increment our top level counter
            num_top += 1

        # finish sizing scrollbar
        # TODO: calling this may be causing the canvas to resize weird... look into
        canvas.configure(scrollregion=canvas.bbox("all"))

    # renderTree: renders a Tree using built in Tree and Treestyle from ete3 library
    def renderTree(self):
        # load all Category objects from SQL database
        categories = categories_helper.load_categories()

        # create Tree object
        t = categories_helper.create_Tree(categories)
        print("guiTab_3_editCategory.show_category_treediagram: printing tree below")

        # print ASCII of tree using internal print function
        print(t.get_ascii(show_internal=True))

        # set up TreeStyle for our tree object
        ts = TreeStyle()
        ts.show_leaf_name = False

        def my_layout(
            node,
        ):  # this adds the recursive node labeling behavior. (I think)
            # create a text face
            f = TextFace(node.name, tight_text=False)  # create name of node

            # set some attributes
            f.margin_top = 25
            f.margin_right = 25
            f.margin_left = 25
            f.margin_bottom = 25

            f.border.width = 1

            # add the text face to the node
            add_face_to_node(
                f, node, column=0, position="branch-right"
            )  # add TextFace,

        ts.layout_fn = my_layout  # set layout of TreeStyle() object
        ts.scale = 50  # adjust scale

        # display the final category tree
        # tk.Label(self.frame, text=t.get_ascii(), width=40).grid(row=0, column=4, rowspan=8)

        t.show(
            layout=my_layout, tree_style=ts, name="ETE"
        )  # start an interactive session to visualize the current node
        # t.render("category_tree.png", w=180, units="mm", tree_style=ts)  # renders the node structure as an image
