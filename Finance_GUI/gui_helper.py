# import needed modules
from tkinter import *
from tkinter import messagebox

import math


#TODO: make general console output that lives on the bottom of the application


# get_statement_folder: returns formatted folder of where the statement is. year and month are ints
def get_statement_folder(base_filepath, year, month):
    if month not in range(0, 12):
        month = month2Int(month)

    if month == 1:
        month_string = "01-January/"
    elif month == 2:
        month_string = "02-February/"
    elif month == 3:
        month_string = "03-March/"
    elif month == 4:
        month_string = "04-April/"
    elif month == 5:
        month_string = "05-May/"
    elif month == 6:
        month_string = "06-June/"
    elif month == 7:
        month_string = "07-July/"
    elif month == 8:
        month_string = "08-August/"
    elif month == 9:
        month_string = "09-September/"
    elif month == 10:
        month_string = "10-October/"
    elif month == 11:
        month_string = "11-November/"
    elif month == 12:
        month_string = "12-December/"
    else:
        print("Bad month int stored in statement: " + str(month))
        return

    statement_folder = base_filepath + "/" + str(year) + "/Monthly Statements/" + month_string
    return statement_folder


# generateYearDropDown: generate a year drop down menu
def generateYearDropDown(frame):
    years = [
        "2020",
        "2021",
        "2022"]

    clicked_year = StringVar()  # datatype of menu text
    clicked_year.set("2022")  # initial menu text
    drop = OptionMenu(frame, clicked_year, *years)  # create drop down menu of years
    return drop, clicked_year


# generate a drop down menu with all 12 months
def generateMonthDropDown(frame):
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    clicked_month = StringVar()  # datatype of menu text
    clicked_month.set(months[0])  # initial menu text
    drop = OptionMenu(frame, clicked_month, *months)  # create drop down menu of months
    return drop, clicked_month


# promptYesNo: prompts the user for a yes or no response with a certain 'message' prompt
def promptYesNo(message):
    response = messagebox.askquestion('ALERT', message)

    if response == "yes":
        return True
    else:
        return False


# gui_print: prints a message both on the Python terminal and a Tkinter frame
def gui_print(master, prompt, message, *args):
    for arg in args:
        message += str(arg)

    message = ">>>" + message
    print(message)
    if master != 0:
        prompt.insert(INSERT, (message+"\n"))

    prompt.see("end")
    return True


# alert_user:
def alert_user(title, message, kind):
    if kind not in ('error', 'warning', 'info'):
        raise ValueError('Unsupported alert kind.')

    show_method = getattr(messagebox, 'show{}'.format(kind))
    show_method(title, message)


# initialize an empty string
def convertTuple(tup):
    string = ''
    for item in tup:
        string = string + item
    return string



##############################################################################
####      TREE FUNCTIONS    #######################################
##############################################################################


def drawLine(canvas, x1, y1, x2, y2):
    print("Drawing a line")
    canvas.create_line(x1, y1, x2, y2, tags="line")


def paintBranch(canvas, depth, x1, y1, length, angle):
    if depth >= 0:
        x2 = x1 + int(math.cos(angle) * length)
        y2 = y1 + int(math.sin(angle) * length)

        # Draw the line
        drawLine(canvas, x1, y1, x2, y2)

        angleFactor = math.pi/5
        sizeFactor = 0.58

        # Draw the left branch
        paintBranch(canvas, depth - 1, x2, y2, length * sizeFactor, angle + angleFactor)
        # Draw the right branch
        paintBranch(canvas, depth - 1, x2, y2, length * sizeFactor, angle - angleFactor)
