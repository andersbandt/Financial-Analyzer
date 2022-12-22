# import needed modules
import tkinter as tk
from tkinter import *
from tkinter.ttk import *

# import user defined packages
from categories import categories_helper
from db import db_helper


class Category:
    def __init__(self, category_id):
        self.id = int(category_id)

        # grab sql data
        cat_sql_data = db_helper.get_category_info(category_id)
        self.name = cat_sql_data[0][2]
        self.parent = cat_sql_data[0][1]

        # populate children category_id
        self.children_id = categories_helper.get_category_children(category_id, printmode=None)

        # what is this description used for?
        self.description = None

        # populate keywords
        self.keyword = []
        keywords = db_helper.get_keyword_for_category_id(self.id)
        for keyword in keywords:
            self.keyword.append(keyword[2])  # keyword string is third column of sql data structure

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

    # draws a GUI representation of the Category on a certain 'canvas'
    #   other parameters include location, size, and color
    def draw_Category_gui_obj(self, canvas, x0, y0, w, h, kind="other", fill_color='gray', master=None):
        # # init Category GUI params
        self.x = x0
        self.y = y0
        self.w = w
        self.h = h
        self.canvas = canvas
        self.master = master

        # draw rectangle
        x1 = x0 + w
        y1 = y0 + h
        rec = self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color)

        # add text
        text = canvas.create_text(x0 + w/2, y0 + h/2, text=self.name, fill="white", font=('Helvetica 8 bold'))

        # add click binding to category GUI object
        # good article about binding types --> https://www.hashbangcode.com/article/using-events-tkinter-canvas-elements-python

        if kind == "full":
            self.canvas.tag_bind(rec, '<Button-1>', self.inter_gui)
        elif kind == "other":
            self.canvas.tag_bind(rec, '<Button-1>', print("test"))
        #self.canvas.tag_bind(rec, '<Enter>', self.change_fill_color("red"))
        #self.canvas.tag_bind(rec, '<Leave>', self.change_fill_color("green"))


    # change_fill_color: changes the fill color of the rectangle of the GUI object
    def change_fill_color(self, fill_color):
        ### raw rectangle method
        x1 = self.x + self.w
        y1 = self.y + self.h
        self.canvas.create_rectangle(self.x, self.y, x1, y1, fill=fill_color)

        # add text
        self.canvas.create_text(self.x + self.w/2, self.y + self.h/2, text=self.name, fill="white", font=('Helvetica 8 bold'))


    def rename_category(self):
        print("Executing rename_category")

    def add_child(self):
        print("Executing add_child")

    def delete_category(self):
        print("Executing delete_category")

    # inter_gui: 'Interactive' function that displays a summary of Category info and options for editing, deleting, etc.
    # TODO: figure out how to be able to delete the frame
    def inter_gui(self, event):
        print('\nClick recorded at ', event.x, event.y)
        print("Executing interactive category function for " + self.name)

        self.frame = tk.Frame(self.master)
        self.frame.grid(row=3, column=0)

        # place category info
        gui_text = "Category: " + self.name
        Label(self.frame, text=gui_text).grid(row=0, column=0, pady=3)
        gui_text = "ID: " + str(self.id)
        Label(self.frame, text=gui_text).grid(row=1, column=0, pady=3)
        gui_text = "Keywords: "
        for keyword in self.keyword:
            gui_text = gui_text + keyword + ", "
        Label(self.frame, text=gui_text).grid(row=2, column=0, pady=3)

        # rename button
        tk.Button(self.frame, text="Rename", command=lambda: self.rename_category()).grid(row=0, column=1)
        # add child button
        tk.Button(self.frame, text="Add Child", command=lambda: self.add_child()).grid(row=1, column=1)
        # delete button
        tk.Button(self.frame, text="Delete", command=lambda: self.delete_category()).grid(row=2, column=1)


