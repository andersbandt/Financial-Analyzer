
# import needed modules
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Style

from ete3 import Tree, TreeStyle, Tree, TextFace, add_face_to_node
import math

# import user defined modules
from src.categories import helper
from src import categories
from db import db_helper
from Finance_GUI import gui_helper


class tabBudgeting:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        # init frames within tab
        self.fr_add_bud = tk.Frame(self.frame, bg="#00bcd4")
        self.fr_add_bud.grid(row=0, column=0, padx=5, pady=5)

        self.fr_view_bud = tk.Frame(self.frame, bg="#00bcd4")
        self.fr_view_bud.grid(row=0, column=1, rowspan=2, padx=5, pady=5)

        self.fr_prompt = tk.Frame(self.frame, bg="gray")
        self.fr_prompt.grid(row=1, column=0, padx=5, pady=5)

        self.load_yes = 0  # yes button to loading statement data
        self.load_no = 0  # no button for loading statement data

        # unsure what these are for
        self.statement = 0
        self.times_analyze_ran = 0

        # set up text box for user communication
        Label(self.fr_prompt, text="Console Output").grid(row=0, column=0, pady=10)
        self.prompt = Text(self.fr_prompt, padx=10, pady=10, height=5, width=50)
        self.prompt.grid(row=1, column=0, padx=10, pady=10)

        # run function to initialize the GUI tab content
        self.initTabContent()


    # initTabContent: initializes the main content of the tab
    def initTabContent(self):
        print("Initializing tab 8 content")

        self.init_fr_add_bud()
        self.init_fr_view_bud()


    def init_fr_add_bud(self):
        # print frame title
        Label(self.fr_add_bud, text="Add Budget Amount", font=("Arial", 16)).grid(row=0, column=0, columnspan=5, padx=3, pady=3)

        # KEYWORD ADDING
        # add drop down for keyword
        budget_category_drop, budget_category_option = gui_helper.generate_all_category_dropdown(self.fr_add_bud)
        budget_category_drop.grid(row=9, column=0, padx=10, pady=5)

        # text input for user to add keyword
        Label(self.fr_add_bud, text="Budget Amount").grid(row=8, column=1, pady=5)

        ### add amount for user to input budget limit
        # validation function for input below
        def MoneyValidation(S):
            if S in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                return True
            self.fr_add_bud.bell()  # .bell() plays that ding sound telling you there was invalid input
            return False

        vcmd = (self.fr_add_bud.register(MoneyValidation), '%S')  # register function

        # add budget amount entry
        b_amount = Entry(self.fr_add_bud, bg='white', validate='key', vcmd=vcmd)
        b_amount.grid(row=9, column=1)

        # set up button to add a budget limit for a Category
        add_b_amount = Button(self.fr_add_bud, text="Add Budget Amount", command=lambda: self.add_budget_gui(budget_category_option.get(), b_amount.get()))
        add_b_amount.grid(row=10, column=3, padx=7, pady=5)  # place 'Start Categorizing' button


    # init_fr_view_bud: inits Frame for viewing budgeting
    def init_fr_view_bud(self):
        # print frame title
        Label(self.fr_view_bud, text="View Budget", font=("Arial", 16)).grid(row=0, column=0, columnspan=5, padx=3, pady=3)

        # set up button to display categories flow chart
        style = Style()
        style.configure('W.TButton', font=('calibri', 10, 'bold', 'underline'), foreground='red')


    ##############################################################################
    ####      ADDING FUNCTIONS        ############################################
    ##############################################################################


    # add_budget_gui: attempts to create a BudgetCategory with input user information
    def add_budget_gui(self, category_name, b_amount):
        # do some more error checking on the BudgetCategory amount
        # if keyword == "":
        #     gui_helper.alert_user("Can't have keyword blank", "Please fill in keyword name", "error")

        # get relevant Category ID
        category_id = helper.category_name_to_id(category_name)
        if category_id == False:
            raise Exception("Error converting from category_name to category_id for creating budget")

        ### create pop up to prompt user to fill out more information
        def popup_bonus():
            win = tk.Toplevel()
            win.wm_title("Window")

            l = tk.Label(win, text="Input")
            l.grid(row=0, column=0)

            b = ttk.Button(win, text="Okay", command=win.destroy)
            b.grid(row=1, column=0)

        popup_bonus()

        cd = 0

        # attempt to set BudgetCategory
        print("add_budget_gui: attempting to insert BudgetCategory of category_id= " + str(category_id))
        res = db_helper.insert_bcat(category_id, b_amount, cd)  # add BudgetCategory date. category_id, lim, and cd
        # if not res:
        #     gui_helper.gui_print(self.frame, self.prompt, "Uh oh, something went wrong adding keyword")
        # else:
        #     gui_helper.gui_print(self.frame, self.prompt, "Set budget amount of : ", keyword, " to category: ", category_name)
        #     keyword_text_obj.delete("1.0", "end")


    ##############################################################################
    ####      HELPER FUNCTIONS          ##########################################
    ##############################################################################


# TODO: generating the category tree eliminates vertical scroll bar
    def show_category_tree_diagram(self, printmode=None):
        if printmode == "debug":
            print("DEBUG: debugging guiTab_3_editCategory.show_category_tree_diagram()")

        # load all Category objects from SQL database
        categories = helper.load_categories()

        ######
        ### trying a new method
        ######

        # set up Canvas
        w = 525
        h = 625
        canvas = Canvas(self.fr_view_cat, width=w, height=h, bg="white")
        #canvas.grid(row=1, column=0, rowspan=3)
        canvas.grid(row=1, column=0, padx=25, pady=25)

        # add a scrollbar
        vsb = tk.Scrollbar(self.fr_view_cat, orient="vertical", command=canvas.yview)
        vsb.grid(row=0, column=1, rowspan=6, sticky='ns')
        canvas.configure(yscrollcommand=vsb.set)

        # generate top Category objects
        top_categories = helper.get_top_level_categories()
        num_top_level = len(top_categories)

        y_pad = 75
        x_child_space = int((w - 20) / 10) + 200  # the denominator should be the length of the tree

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
            #y_top = y_prev + .3*num_top*y_top_space + y_spacer
            y_top = y_prev + y_t_space + y_b_space

            # DEBUG PRINTING
            print("Drawing parent at = ", x_top, ",", y_top) if printmode == "debug" else 0
            print("y_t_space = ", y_t_space) if printmode == "debug" else 0
            print("y_b_space = ", y_b_space) if printmode == "debug" else 0
            # draw top level parent node (all along same leftmost vertical row)
            category.draw_Category_gui_obj(canvas, x_top, y_top, w, h, kind="full", master=self.fr_view_cat)  # draw Category node


            # draw_children: draws the children for a Category 'cat' based on a starting x coordinate 'x_st'
            def draw_children(cat, x_st, y_st, max_angle, fill_color="gray"):
                print("Drawing children for category: ", cat.name)
                # generate angle matrix for drawing parent children
                num_children = len(cat.children_id)
                print("\tlength of children is ", str(num_children))
                angles = gui_helper.generate_tree_angles(num_children, max_angle)

                if angles is None:
                    raise Exception("ERROR: can't create category tree - angle matrix couldn't be generated for parent: ", cat.name)

                for i in range(0, num_children):
                    tmp_Cat = categories.Category(cat.children_id[i])
                    x_cord = x_st + x_child_space
                    y_cord = y_st + int(math.tan(angles[i]) * x_child_space)

                    # draw the child node
                    if printmode == "debug":
                        print("Drawing child at (x, y): " + str(x_cord) + "," + str(y_cord))

                    tmp_Cat.draw_Category_gui_obj(canvas, x_cord, y_cord, w, h, kind="full", fill_color=fill_color, master=self.fr_view_cat)

                    # draw branch linking parent node to child node
                    gui_helper.drawLine(canvas, x_st + w, y_st + h / 2, x_cord, y_cord + h / 2)

                    # recursively call if Category has children
                    l = len(tmp_Cat.children_id)
                    if l > 0:
                        draw_children(tmp_Cat, x_st + x_child_space, y_cord, max_angle, fill_color=fill_color)


            # if top level Category has children, start children drawing algorithm
            if len(category.children_id) > 0:
                # set up next top level category spacing based on children length
                y_t_space = int(3.5 * h * math.sqrt(len(category.children_id)))  # the "top" spacing for the next parent

                # draw children
                max_angle = math.pi * 17 / 180  # max +/- deviation in degrees from parent node
                draw_children(category, x_top, y_top, max_angle, fill_color="#062b19")

            # add bottom level spacing contribution
            if len(categories[num_top+1].children_id) > 0:
                y_b_space = int(3.5 * h * math.sqrt(len(categories[num_top+1].children_id)))  # the "top" spacing for the next parent
            else:
                y_b_space = 0

            # increment our top level counter
            num_top += 1

        # finish sizing scrollbar
        # TODO: calling this may be causing the canvas to resize weird... look into
        canvas.configure(scrollregion=canvas.bbox('all'))


    # renderTree: renders a Tree using built in Tree and Treestyle from ete3 library
    def renderTree(self):
        # load all Category objects from SQL database
        categories = helper.load_categories()

        # create Tree object
        t = helper.create_Tree(categories)
        print("guiTab_3_editCategory.show_category_treediagram: printing tree below")

        # print ASCII of tree using internal print function
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

        t.show(layout=my_layout, tree_style=ts, name='ETE')  # start an interactive session to visualize the current node
        t.render("category_tree.png", w=180, units="mm", tree_style=ts)  # renders the node structure as an image



