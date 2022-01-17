# import needed packages
import tkinter as tk
from tkinter import *
from tkinter import ttk

# import user defined modules



class tabMainDashboard:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.initTabContent()



    def initTabContent(self):
        l1 = ttk.Label(text="Welcome to the Finance Manager!", style="BW.TLabel")

        l1.grid(column=0, row=0)
