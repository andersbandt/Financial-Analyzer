# import needed modules

# import needed modules
from tkinter import *
from tkinter import messagebox

import math

# import user defined modules
from tools import date_helper
from db import db_helper


#TODO: make general console output that lives on the bottom of the application


# get_statement_folder: returns formatted folder of where the statement is. year and month are ints
def get_statement_folder(base_filepath, year, month):
    if month not in range(0, 12):
        month = date_helper.month2Int(month)

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


##############################################################################
####      GUI OBJECT GENERATION FUNCTIONS           ##########################
##############################################################################

# TODO: refactor to code to use this function

# generate a drop down menu with all categories in SQL database
# outputs:
#   drop - tkinter GUI object that will need to be placed on the Frame with .grid()
#   clicked_category - variable representing the chosen Category
def generate_all_category_dropdown(frame):
    categories = db_helper.get_category_names()

    clicked_category = StringVar(frame)  # datatype of menu text
    clicked_category.set(categories[0])  # initial menu text
    drop = OptionMenu(frame, clicked_category, *categories)  # create drop down menu of months
    return drop, clicked_category


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


##############################################################################
####      PROMPT/ALERT FUNCTIONS           ###################################
##############################################################################

# promptYesNo: prompts the user for a yes or no response with a certain 'message' prompt
def promptYesNo(message):
    response = messagebox.askquestion('ALERT', message)

    if response == "yes":
        return True
    else:
        return False


# alert_user: alerts the user with a prompt that flashes on the screen
#   kind can be of type {"error", "warning", and "info"}
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
####      TREE FUNCTIONS           ###########################################
##############################################################################

# TODO: get this angle matrix generation function working properly
#   has to be some component of odd/even in the for loop...
# generate_tree_angles: generates an array of the different angles to plot children node from a parent
def generate_tree_angles(num_children, max_angle):
    if num_children == 0:
        return [0]

    if num_children == 1:
        return [0]

    if num_children == 2:
        return [max_angle/2, -max_angle/2]

    if num_children == 3:
        return [max_angle, 0, -max_angle]

    if num_children == 4:
        return [max_angle, max_angle * 1/2, -max_angle * 1/2, -max_angle]

    if num_children == 5:
        return [max_angle, max_angle * 3/5, 0, -max_angle * 3/5, -max_angle]

    if num_children == 6:
        return [max_angle, max_angle * 4/5, max_angle * 2/5, -max_angle * 2/5, -max_angle * 4/5, -max_angle]

    print("Uh oh, this statement shouldn't be reached! No angle matrix was found!")
    print("ERROR: can't generate angle matrix for number of children: " + str(num_children))


# drawLine: draws a line between coordinates (x1, y1) and (x2, y2) on 'canvas'
def drawLine(canvas, x1, y1, x2, y2):
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
