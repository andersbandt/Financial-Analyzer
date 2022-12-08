# import needed packages
import tkinter as tk
from tkinter import *
from tkinter import ttk

# import user defined modules



class tabMainDashboard:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.frame.grid(row=0, column=0)

        self.initTabContent()


    def initTabContent(self):
        print("Initializing tab 1 content")

        # print welcome text
        l1 = ttk.Label(self.frame, text="Welcome to the Finance Manager!", style="BW.TLabel", font=("Arial", 16))
        #l1 = Label(self.frame, text="Welcome to the Financial Analyzer!", font=("Arial", 16))
        l1.grid(column=0, row=0)
